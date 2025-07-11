"""
AI processing service for news content
"""
import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Protocol
from datetime import datetime

from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter
import requests

from app.core.config import settings
from app.services.news_service import NewsRepository
from app.models.news import NewsArticle, ProcessedContent

logger = logging.getLogger(__name__)


class LLMBackend(Protocol):
    async def ainvoke(self, messages: list) -> Any:
        ...

class LMStudioLLM:
    """本地LM Studio LLM实现"""
    def __init__(self, api_url: str = "http://127.0.0.1:1234/v1/chat/completions"):
        self.api_url = api_url

    async def ainvoke(self, messages: list) -> Any:
        # 转换为OpenAI格式
        payload = {
            "model": "lmstudio",
            "messages": [
                {"role": "system", "content": m.content} if isinstance(m, SystemMessage) else {"role": "user", "content": m.content}
                for m in messages
            ],
            "temperature": 0.1,
            "max_tokens": 800
        }
        try:
            resp = requests.post(self.api_url, json=payload, timeout=30)
            resp.raise_for_status()
            result = resp.json()
            content = result["choices"][0]["message"]["content"]
            class Resp: pass
            r = Resp(); r.content = content
            return r
        except Exception as e:
            raise RuntimeError(f"LM Studio调用失败: {e}")

class DeepSeekLLM:
    """DeepSeek LLM实现（兼容langchain_deepseek）"""
    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        self.llm = ChatDeepSeek(api_key=api_key, model=model, temperature=0.1, max_tokens=800)
    async def ainvoke(self, messages: list) -> Any:
        return await self.llm.ainvoke(messages)


class AIProcessor:
    """AI内容处理器"""
    
    def __init__(self, repo: NewsRepository, llm: LLMBackend = None):
        self.repo = repo
        # 优先本地LM Studio，不可用时自动切换DeepSeek
        if llm is not None:
            self.llm = llm
        else:
            try:
                self.llm = LMStudioLLM()
                # 测试本地服务可用性
                import asyncio
                async def test():
                    msg = [SystemMessage(content="你是AI助手。"), HumanMessage(content="你好")]
                    await self.llm.ainvoke(msg)
                asyncio.get_event_loop().run_until_complete(test())
            except Exception as e:
                logger.warning(f"本地LM Studio不可用，切换到DeepSeek: {e}")
                from app.core.config import settings
                self.llm = DeepSeekLLM(api_key=settings.deepseek_api_key)
        # 减少文本长度，提高处理速度
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,  # 减少chunk大小
            chunk_overlap=100,  # 减少重叠
            length_function=len,
        )
    
    async def process_articles(self, limit: int = 10) -> Dict[str, int]:
        """批量处理未处理的文章"""
        # 获取未处理的文章
        unprocessed_articles = self.repo.get_unprocessed_articles(limit)
        
        results = {
            'total_articles': len(unprocessed_articles),
            'success_count': 0,
            'error_count': 0,
            'api_calls': 0
        }
        
        for article in unprocessed_articles:
            try:
                logger.info(f"Processing article: {article.title[:50]}...")
                
                # 处理单篇文章
                success = await self.process_single_article(article)
                
                if success:
                    results['success_count'] += 1
                    results['api_calls'] += 3  # 摘要、翻译、质量评估各一次
                else:
                    results['error_count'] += 1
                
                # 减少延迟，提高处理速度
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error processing article {article.id}: {e}")
                results['error_count'] += 1
        
        return results
    
    async def process_single_article(self, article: NewsArticle) -> bool:
        """处理单篇文章"""
        try:
            start_time = time.time()
            
            # 1. 生成中文摘要
            summary_zh = await self._generate_summary_zh(article.content)
            if not summary_zh:
                logger.error(f"Failed to generate Chinese summary for article {article.id}")
                return False
            
            # 2. 生成英文摘要
            summary_en = await self._generate_summary_en(article.content)
            if not summary_en:
                logger.error(f"Failed to generate English summary for article {article.id}")
                return False
            
            # 3. 翻译为中文（如果原文是英文）
            translation_zh = None
            if article.language == 'en':
                translation_zh = await self._translate_to_chinese(article.content)
            
            # 4. 质量评估（可选，为提高速度可跳过）
            quality_score = 7.0  # 默认中等质量，跳过AI评估以提高速度
            
            # 5. 保存处理结果
            processing_time = time.time() - start_time
            
            processed_data = {
                'article_id': article.id,
                'summary_zh': summary_zh,
                'summary_en': summary_en,
                'translation_zh': translation_zh,
                'quality_score': quality_score,
                'processing_time': processing_time
            }
            
            self.repo.create_processed_content(processed_data)
            
            # 6. 更新文章状态
            self.repo.update_article_processed_status(article.id, True)
            
            logger.info(f"Successfully processed article {article.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing article {article.id}: {e}")
            return False
    
    async def process_single_article_by_id(self, article_id: int) -> bool:
        """根据ID处理单篇文章"""
        try:
            article = self.repo.get_article_by_id(article_id)
            if not article:
                logger.error(f"Article {article_id} not found")
                return False
            
            return await self.process_single_article(article)
            
        except Exception as e:
            logger.error(f"Error processing article {article_id}: {e}")
            return False
    
    async def _generate_summary_zh(self, content: str) -> Optional[str]:
        """生成中文摘要"""
        try:
            # 如果内容太长，先分割
            if len(content) > 1500:
                chunks = self.text_splitter.split_text(content)
                content = chunks[0]  # 使用第一个chunk
            
            system_prompt = """为以下新闻生成简洁的中文摘要，控制在150字以内，突出核心信息。直接返回摘要内容。"""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"新闻内容：\n\n{content}")
            ]
            
            response = await self.llm.ainvoke(messages)
            summary = response.content.strip()
            
            # 清理摘要
            summary = self._clean_summary(summary)
            
            return summary if len(summary) > 20 else None
            
        except Exception as e:
            logger.error(f"Error generating Chinese summary: {e}")
            return None
    
    async def _generate_summary_en(self, content: str) -> Optional[str]:
        """生成英文摘要"""
        try:
            # 如果内容太长，先分割
            if len(content) > 1500:
                chunks = self.text_splitter.split_text(content)
                content = chunks[0]  # 使用第一个chunk
            
            system_prompt = """Generate a concise English summary of the following news in 150 words or less. Focus on key facts. Return summary directly."""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"News content:\n\n{content}")
            ]
            
            response = await self.llm.ainvoke(messages)
            summary = response.content.strip()
            
            # 清理摘要
            summary = self._clean_summary(summary)
            
            return summary if len(summary) > 20 else None
            
        except Exception as e:
            logger.error(f"Error generating English summary: {e}")
            return None
    
    async def _translate_to_chinese(self, content: str) -> Optional[str]:
        """翻译为中文"""
        try:
            # 如果内容太长，先分割
            if len(content) > 1500:
                chunks = self.text_splitter.split_text(content)
                content = chunks[0]  # 使用第一个chunk
            
            system_prompt = """将以下英文新闻翻译成中文，保持原意，使用流畅的中文表达。直接返回翻译结果。"""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"英文内容：\n\n{content}")
            ]
            
            response = await self.llm.ainvoke(messages)
            translation = response.content.strip()
            
            return translation if len(translation) > 50 else None
            
        except Exception as e:
            logger.error(f"Error translating to Chinese: {e}")
            return None
    
    async def _evaluate_quality(self, content: str) -> Optional[float]:
        """评估内容质量"""
        try:
            system_prompt = """你是一个新闻质量评估专家，请对以下新闻内容进行质量评估。

评估维度：
1. 信息完整性（0-10分）
2. 语言表达质量（0-10分）
3. 新闻价值（0-10分）
4. 客观性（0-10分）
5. 时效性（0-10分）

请综合考虑以上维度，给出一个0-10分的总体质量评分，保留一位小数。

请直接返回数字评分，不要添加任何其他内容。"""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"新闻内容：\n\n{content}")
            ]
            
            response = await self.llm.ainvoke(messages)
            score_text = response.content.strip()
            
            # 提取数字
            try:
                score = float(score_text)
                # 确保分数在合理范围内
                score = max(0.0, min(10.0, score))
                return round(score, 1)
            except ValueError:
                logger.warning(f"Invalid quality score: {score_text}")
                return 5.0  # 默认中等质量
            
        except Exception as e:
            logger.error(f"Error evaluating quality: {e}")
            return 5.0  # 默认中等质量
    
    def _clean_summary(self, summary: str) -> str:
        """清理摘要内容"""
        # 移除常见的AI回复前缀
        prefixes_to_remove = [
            "摘要：", "总结：", "概要：", "Summary:", "Abstract:", 
            "以下是摘要：", "Here's the summary:", "The summary is:"
        ]
        
        for prefix in prefixes_to_remove:
            if summary.startswith(prefix):
                summary = summary[len(prefix):].strip()
        
        # 移除多余的换行和空格
        summary = " ".join(summary.split())
        
        return summary
    
    async def reprocess_article(self, article_id: int) -> bool:
        """重新处理指定文章"""
        try:
            article = self.repo.get_article_by_id(article_id)
            if not article:
                logger.error(f"Article {article_id} not found")
                return False
            
            # 删除之前的处理结果
            self.repo.delete_processed_content(article_id)
            
            # 重新处理
            success = await self.process_single_article(article)
            
            return success
            
        except Exception as e:
            logger.error(f"Error reprocessing article {article_id}: {e}")
            return False
    
    async def get_processing_stats(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        try:
            stats = self.repo.get_processing_statistics()
            return stats
        except Exception as e:
            logger.error(f"Error getting processing stats: {e}")
            return {} 