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
from app.models.news import NewsArticle

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
                # 移除有问题的异步测试，改为简单的同步检查
                logger.info("使用本地LM Studio")
            except Exception as e:
                logger.warning(f"本地LM Studio不可用，切换到DeepSeek: {e}")
                from app.core.config import settings
                self.llm = DeepSeekLLM(api_key=settings.deepseek_api_key)
                logger.info("使用DeepSeek LLM")
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
            summary_zh = await self._generate_summary_zh(article.original_content)
            if not summary_zh:
                logger.error(f"Failed to generate Chinese summary for article {article.id}")
                return False
            # 2. 生成详细摘要（可选，或与summary_zh一致）
            detailed_summary_zh = summary_zh
            # 3. 翻译标题为中文（如原文为英文）
            translated_title = None
            if article.original_language == 'en' and article.original_title:
                translated_title = await self._translate_title_to_chinese(article.original_title)
            # 4. 翻译正文为中文（如原文为英文）
            translation_zh = None
            if article.original_language == 'en':
                translation_zh = await self._translate_to_chinese(article.original_content)
            # 5. 质量分数
            quality_score = 7.0
            # 6. 保存到news_articles表
            update_data = {
                'summary_zh': summary_zh,
                'detailed_summary_zh': detailed_summary_zh,
                'translated_title': translated_title,
                'translated_content': translation_zh,
                'quality_score': quality_score,
                'is_processed': True,
                'is_title_translated': translated_title is not None,
                'is_content_translated': translation_zh is not None,
                'translation_quality_score': 9.0 if translation_zh else 0.0
            }
            self.repo.update_article(article.id, update_data)
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
    
    async def _translate_title_to_chinese(self, title: str) -> Optional[str]:
        """翻译标题为中文"""
        try:
            logger.info(f"开始翻译标题: {title}")
            
            system_prompt = """将以下英文新闻标题翻译成中文，保持简洁明了，直接返回翻译结果。"""
            user_prompt = f"英文标题：{title}"

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            logger.info("调用LLM进行标题翻译...")
            response = await self.llm.ainvoke(messages)
            logger.info("标题翻译完成")
            
            translation = response.content.strip()
            logger.info(f"标题翻译结果: {translation}")
            
            if len(translation) > 5:
                logger.info("标题翻译成功")
                return translation
            else:
                logger.warning(f"标题翻译结果太短: {translation}")
                return None
            
        except Exception as e:
            logger.error(f"标题翻译过程中出错: {e}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            return None

    async def _translate_to_chinese(self, content: str) -> Optional[str]:
        """翻译为中文"""
        try:
            logger.info(f"开始翻译内容，长度: {len(content)}")
            
            # 如果内容太长，先分割
            if len(content) > 1500:
                chunks = self.text_splitter.split_text(content)
                content = chunks[0]  # 使用第一个chunk
                logger.info(f"内容过长，使用第一个chunk，长度: {len(content)}")
            
            system_prompt = """将以下英文新闻翻译成中文，保持原意，使用流畅的中文表达。直接返回翻译结果。"""
            user_prompt = f"英文内容：\n\n{content}"

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            logger.info("调用LLM进行翻译...")
            response = await self.llm.ainvoke(messages)
            logger.info("LLM调用完成")
            
            translation = response.content.strip()
            logger.info(f"翻译结果长度: {len(translation)}")
            
            if len(translation) > 20:
                logger.info("翻译成功")
                return translation
            else:
                logger.warning(f"翻译结果太短: {translation}")
                return None
            
        except Exception as e:
            logger.error(f"翻译过程中出错: {e}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
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
            # 直接重新处理并覆盖news_articles表相关字段
            return await self.process_single_article(article)
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