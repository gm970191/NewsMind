"""
News crawler service - 简化版
"""
import asyncio
import logging
import requests
import feedparser
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

from app.services.news_service import NewsRepository
from app.models.news import NewsSource

logger = logging.getLogger(__name__)


class NewsCrawler:
    """新闻爬虫 - 简化版"""
    
    def __init__(self, repo: NewsRepository):
        self.repo = repo
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    async def crawl_today_news(self) -> int:
        """抓取当天新闻"""
        sources = self.repo.get_active_sources()
        total_new_articles = 0
        
        for source in sources:
            try:
                logger.info(f"正在抓取: {source.name}")
                
                if source.type == 'rss':
                    articles = await self._crawl_rss(source)
                else:
                    articles = await self._crawl_web(source)
                
                # 保存文章
                for article_data in articles:
                    saved_article = self.repo.save_article(article_data)
                    if saved_article:
                        total_new_articles += 1
                
                logger.info(f"{source.name}: 保存了 {len(articles)} 篇新文章")
                
            except Exception as e:
                logger.error(f"抓取 {source.name} 失败: {e}")
        
        return total_new_articles
    
    async def _crawl_rss(self, source: NewsSource) -> List[Dict[str, Any]]:
        """抓取RSS源"""
        try:
            response = self.session.get(source.url, timeout=10)
            response.raise_for_status()
            
            feed = feedparser.parse(response.text)
            articles = []
            
            for entry in feed.entries[:10]:  # 只取前10篇
                # 提取标题和概要
                title = entry.get('title', '').strip()
                summary = entry.get('summary', '').strip()
                
                # 如果没有summary，尝试其他字段
                if not summary:
                    summary = entry.get('description', '')
                
                # 清理HTML标签
                summary = self._clean_html(summary)
                
                # 确保有内容
                if title and summary and len(summary) > 10:
                    article_data = {
                        'original_title': title,
                        'original_summary': summary,
                        'source_url': entry.get('link', ''),
                        'source_id': source.id,
                        'source_name': source.name,
                        'category': source.category,
                        'is_translated': False
                    }
                    articles.append(article_data)
            
            return articles
            
        except Exception as e:
            logger.error(f"RSS抓取失败 {source.url}: {e}")
            return []
    
    async def _crawl_web(self, source: NewsSource) -> List[Dict[str, Any]]:
        """抓取网页新闻"""
        try:
            response = self.session.get(source.url, timeout=10)
            response.raise_for_status()
            
            # 简单的网页解析（这里可以根据具体网站定制）
            # 目前返回空列表，因为网页抓取需要针对具体网站定制
            logger.warning(f"网页抓取暂未实现: {source.url}")
            return []
            
        except Exception as e:
            logger.error(f"网页抓取失败 {source.url}: {e}")
            return []
    
    def _clean_html(self, text: str) -> str:
        """清理HTML标签"""
        if not text:
            return ""
        
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close() 