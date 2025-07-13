"""
AI processing service - 简化版，使用本地LM Studio
"""
import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Protocol
import requests

from app.services.news_service import NewsRepository
from app.models.news import NewsArticle

logger = logging.getLogger(__name__)


class LMStudioLLM:
    """本地LM Studio LLM实现"""
    def __init__(self, api_url: str = "http://127.0.0.1:1234/v1/chat/completions"):
        self.api_url = api_url

    async def ainvoke(self, messages: list) -> Any:
        # 转换为OpenAI格式
        payload = {
            "model": "qwen2-0.5b-instruct",
            "messages": [
                {"role": "system", "content": m.content} if hasattr(m, 'content') and m.content else {"role": "user", "content": m.content}
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


class AIProcessor:
    """AI内容处理器 - 简化版"""
    
    def __init__(self, repo: NewsRepository):
        self.repo = repo
        self.llm = LMStudioLLM()
    
    async def process_articles(self, limit: int = 10) -> Dict[str, int]:
        """批量处理未翻译的文章"""
        # 获取未翻译的文章
        untranslated_articles = self.repo.get_untranslated_articles(limit)
        
        results = {
            'total_articles': len(untranslated_articles),
            'success_count': 0,
            'error_count': 0
        }
        
        for article in untranslated_articles:
            try:
                logger.info(f"Processing article: {article.original_title[:50]}...")
                
                # 处理单篇文章
                success = await self.process_single_article(article)
                
                if success:
                    results['success_count'] += 1
                else:
                    results['error_count'] += 1
                
                # 减少延迟
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error processing article {article.id}: {e}")
                results['error_count'] += 1
        
        return results
    
    async def process_single_article(self, article: NewsArticle) -> bool:
        """处理单篇文章 - 翻译标题和概要"""
        try:
            # 1. 翻译标题
            translated_title = await self._translate_title(article.original_title)
            if not translated_title:
                logger.error(f"Failed to translate title for article {article.id}")
                return False
            
            # 2. 翻译概要
            translated_summary = await self._translate_summary(article.original_summary)
            if not translated_summary:
                logger.error(f"Failed to translate summary for article {article.id}")
                return False
            
            # 3. 保存翻译结果
            success = self.repo.update_article_translation(
                article.id, translated_title, translated_summary
            )
            
            if success:
                logger.info(f"Successfully processed article {article.id}")
                return True
            else:
                logger.error(f"Failed to save translation for article {article.id}")
                return False
                
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
    
    async def _translate_title(self, title: str) -> Optional[str]:
        """翻译标题为中文"""
        try:
            system_prompt = "将以下英文新闻标题翻译成中文，保持简洁明了，直接返回翻译结果。"
            user_prompt = f"英文标题：{title}"

            messages = [
                type('SystemMessage', (), {'content': system_prompt})(),
                type('HumanMessage', (), {'content': user_prompt})()
            ]
            
            response = await self.llm.ainvoke(messages)
            translation = response.content.strip()
            
            if len(translation) > 5:
                return translation
            else:
                return None
            
        except Exception as e:
            logger.error(f"标题翻译失败: {e}")
            return None

    async def _translate_summary(self, summary: str) -> Optional[str]:
        """翻译概要为中文"""
        try:
            system_prompt = "将以下英文新闻概要翻译成中文，保持原意，使用流畅的中文表达。直接返回翻译结果。"
            user_prompt = f"英文概要：\n\n{summary}"

            messages = [
                type('SystemMessage', (), {'content': system_prompt})(),
                type('HumanMessage', (), {'content': user_prompt})()
            ]
            
            response = await self.llm.ainvoke(messages)
            translation = response.content.strip()
            
            if len(translation) > 20:
                return translation
            else:
                return None
            
        except Exception as e:
            logger.error(f"概要翻译失败: {e}")
            return None 