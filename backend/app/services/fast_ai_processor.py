"""
快速AI处理器 - 专门用于高效的翻译和总结
"""
import asyncio
import time
import logging
from typing import Optional, Dict, Any

from langchain_deepseek import ChatDeepSeek
from langchain.schema import SystemMessage, HumanMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.core.config import settings
from app.models.news import NewsRepository, NewsArticle

logger = logging.getLogger(__name__)

class FastAIProcessor:
    """快速AI内容处理器 - 专门用于翻译和总结"""
    
    def __init__(self, repo: NewsRepository):
        self.repo = repo
        # 使用最小配置，最大化速度
        self.llm = ChatDeepSeek(
            api_key=settings.deepseek_api_key,
            model="deepseek-chat",
            temperature=0.0,  # 最低温度，最稳定
            max_tokens=500    # 最小token数，最快速度
        )
        # 更小的文本分割
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # 更小的chunk
            chunk_overlap=50,  # 更小的重叠
            length_function=len,
        )
    
    async def process_articles_fast(self, limit: int = 10) -> Dict[str, int]:
        """快速批量处理文章"""
        unprocessed_articles = self.repo.get_unprocessed_articles(limit)
        
        results = {
            'total_articles': len(unprocessed_articles),
            'success_count': 0,
            'error_count': 0,
            'total_time': 0
        }
        
        for article in unprocessed_articles:
            try:
                start_time = time.time()
                logger.info(f"快速处理文章: {article.title[:30]}...")
                
                success = await self.process_single_article_fast(article)
                
                processing_time = time.time() - start_time
                results['total_time'] += processing_time
                
                if success:
                    results['success_count'] += 1
                    logger.info(f"✅ 快速处理成功: {processing_time:.1f}s")
                else:
                    results['error_count'] += 1
                    logger.error(f"❌ 快速处理失败: {processing_time:.1f}s")
                
                # 最小延迟
                await asyncio.sleep(0.2)
                
            except Exception as e:
                logger.error(f"快速处理文章 {article.id} 出错: {e}")
                results['error_count'] += 1
        
        avg_time = results['total_time'] / results['success_count'] if results['success_count'] > 0 else 0
        logger.info(f"快速处理完成: 成功{results['success_count']}篇，平均{avg_time:.1f}s/篇")
        
        return results
    
    async def process_single_article_fast(self, article: NewsArticle) -> bool:
        """快速处理单篇文章"""
        try:
            start_time = time.time()
            # 1. 快速生成中文摘要
            summary_zh = await self._generate_summary_fast(article.content, "zh")
            if not summary_zh:
                return False
            # 2. 快速生成详细摘要（可选，或与summary_zh一致）
            detailed_summary_zh = summary_zh
            # 3. 快速翻译（仅英文）
            translation_zh = None
            if article.language == 'en':
                translation_zh = await self._translate_fast(article.content)
            # 4. 保存到news_articles表
            update_data = {
                'summary_zh': summary_zh,
                'detailed_summary_zh': detailed_summary_zh,
                'translated_content': translation_zh,
                'quality_score': 7.0,
                'is_processed': True
            }
            self.repo.update_article(article.id, update_data)
            return True
        except Exception as e:
            logger.error(f"快速处理文章 {article.id} 出错: {e}")
            return False
    
    async def _generate_summary_fast(self, content: str, language: str) -> Optional[str]:
        """快速生成摘要"""
        try:
            # 限制内容长度
            if len(content) > 1000:
                content = content[:1000]
            
            if language == "zh":
                prompt = "为以下新闻生成100字以内的中文摘要，突出核心信息："
            else:
                prompt = "Generate a 100-word English summary of the following news, focus on key facts:"
            
            messages = [
                SystemMessage(content=prompt),
                HumanMessage(content=content)
            ]
            
            response = await self.llm.ainvoke(messages)
            summary = response.content.strip()
            
            return summary if len(summary) > 10 else None
            
        except Exception as e:
            logger.error(f"快速生成{language}摘要出错: {e}")
            return None
    
    async def _translate_fast(self, content: str) -> Optional[str]:
        """快速翻译"""
        try:
            # 限制内容长度
            if len(content) > 1000:
                content = content[:1000]
            
            prompt = "将以下英文翻译成中文，保持简洁："
            
            messages = [
                SystemMessage(content=prompt),
                HumanMessage(content=content)
            ]
            
            response = await self.llm.ainvoke(messages)
            translation = response.content.strip()
            
            return translation if len(translation) > 20 else None
            
        except Exception as e:
            logger.error(f"快速翻译出错: {e}")
            return None 