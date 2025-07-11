"""
Web crawler service for news collection
"""
import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse

# 检查是否禁用playwright
if os.environ.get('DISABLE_PLAYWRIGHT') != '1':
    try:
        from playwright.async_api import async_playwright, Browser, Page
        PLAYWRIGHT_AVAILABLE = True
    except ImportError:
        PLAYWRIGHT_AVAILABLE = False
else:
    PLAYWRIGHT_AVAILABLE = False

from bs4 import BeautifulSoup
import requests
from feedparser import parse as feedparse

from app.core.config import settings
from app.services.news_service import NewsRepository
from app.models.news import NewsSource, NewsArticle

logger = logging.getLogger(__name__)


class WebCrawler:
    """网页抓取器"""
    
    def __init__(self, repo: NewsRepository):
        self.repo = repo
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.start_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close_browser()
    
    async def start_browser(self):
        """启动浏览器"""
        if not PLAYWRIGHT_AVAILABLE:
            logger.warning("Playwright not available, using requests-based crawling")
            return
            
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu'
                ]
            )
            self.page = await self.browser.new_page()
            
            # 设置用户代理
            await self.page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            PLAYWRIGHT_AVAILABLE = False
    
    async def close_browser(self):
        """关闭浏览器"""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    async def crawl_news_sources(self) -> Dict[str, int]:
        """抓取所有新闻源"""
        sources = self.repo.get_active_sources()
        results = {
            'total_sources': len(sources),
            'success_count': 0,
            'error_count': 0,
            'new_articles': 0
        }
        
        for source in sources:
            try:
                logger.info(f"Crawling source: {source.name} ({source.url})")
                
                if source.type == 'web':
                    articles = await self.crawl_web_source(source)
                elif source.type == 'rss':
                    articles = await self.crawl_rss_source(source)
                else:
                    logger.warning(f"Unknown source type: {source.type}")
                    continue
                
                # 保存文章
                for article_data in articles:
                    try:
                        # 检查是否已存在
                        existing = self.repo.get_article_by_url(article_data['source_url'])
                        if not existing:
                            self.repo.create_article(article_data)
                            results['new_articles'] += 1
                            logger.info(f"Saved new article: {article_data['title'][:50]}...")
                    except Exception as e:
                        logger.error(f"Error saving article: {e}")
                
                results['success_count'] += 1
                
            except Exception as e:
                logger.error(f"Error crawling source {source.name}: {e}")
                results['error_count'] += 1
        
        return results
    
    async def crawl_web_source(self, source: NewsSource) -> List[Dict[str, Any]]:
        """抓取网页新闻源"""
        try:
            if not PLAYWRIGHT_AVAILABLE or not self.page:
                # 使用requests作为备选方案
                logger.info(f"Using requests for web crawling: {source.url}")
                response = requests.get(source.url, timeout=30)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
            else:
                # 使用playwright
                await self.page.goto(source.url, wait_until='networkidle', timeout=30000)
                content = await self.page.content()
                soup = BeautifulSoup(content, 'html.parser')
            
            # 根据不同的新闻源使用不同的解析策略
            articles = []
            
            if 'cnn.com' in source.url:
                articles = self._parse_cnn(soup, source)
            elif 'bbc.com' in source.url:
                articles = self._parse_bbc(soup, source)
            elif 'reuters.com' in source.url:
                articles = self._parse_reuters(soup, source)
            elif 'techcrunch.com' in source.url:
                articles = self._parse_techcrunch(soup, source)
            elif 'bloomberg.com' in source.url:
                articles = self._parse_bloomberg(soup, source)
            else:
                # 通用解析策略
                articles = self._parse_generic(soup, source)
            
            # 为每个文章获取完整内容
            for article in articles:
                if article.get('source_url') and not article.get('content'):
                    try:
                        full_content = await self._get_full_content(article['source_url'])
                        if full_content:
                            article['content'] = full_content
                        else:
                            # 如果获取失败，使用标题作为内容
                            article['content'] = article['title']
                    except Exception as e:
                        logger.warning(f"Failed to get full content for {article['source_url']}: {e}")
                        article['content'] = article['title']
            
            return articles[:settings.max_articles_per_source]
            
        except Exception as e:
            logger.error(f"Error crawling web source {source.url}: {e}")
            return []
    
    async def crawl_rss_source(self, source: NewsSource) -> List[Dict[str, Any]]:
        """抓取RSS新闻源"""
        try:
            # 解析RSS
            feed = feedparse(source.url)
            articles = []
            
            for entry in feed.entries[:settings.max_articles_per_source]:
                try:
                    article_data = {
                        'title': entry.get('title', ''),
                        'content': entry.get('summary', ''),
                        'source_url': entry.get('link', ''),
                        'source_id': source.id,
                        'source_name': source.name,
                        'publish_time': self._parse_rss_date(entry.get('published')),
                        'category': source.category,
                        'language': 'en'  # 默认英文
                    }
                    
                    # 如果内容为空，尝试获取完整内容
                    if not article_data['content'] and entry.get('link'):
                        try:
                            full_content = await self._get_full_content(entry.get('link'))
                            if full_content:
                                article_data['content'] = full_content
                        except Exception as e:
                            logger.warning(f"Failed to get full content for {entry.get('link')}: {e}")
                    
                    articles.append(article_data)
                    
                except Exception as e:
                    logger.error(f"Error parsing RSS entry: {e}")
                    continue
            
            return articles
            
        except Exception as e:
            logger.error(f"Error crawling RSS source {source.url}: {e}")
            return []
    
    async def _get_full_content(self, url: str) -> Optional[str]:
        """获取完整内容"""
        try:
            await self.page.goto(url, wait_until='networkidle', timeout=15000)
            content = await self.page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # 移除脚本、样式、导航、页脚等无关内容
            for element in soup(["script", "style", "nav", "header", "footer", "aside", "menu"]):
                element.decompose()
            
            # 尝试找到主要内容 - 更全面的选择器
            content_selectors = [
                'article',
                '.article-content',
                '.post-content',
                '.entry-content',
                '.content',
                'main',
                '.main-content',
                '.story-content',
                '.article-body',
                '.post-body',
                '.entry-body',
                '.content-body',
                '.text-content',
                '.article-text',
                '.story-text',
                '[role="main"]',
                '.article',
                '.story'
            ]
            
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text(strip=True)
                    if len(text) > 100:  # 确保内容足够长
                        return text
            
            # 尝试找到包含最多文本的段落
            paragraphs = soup.find_all('p')
            if paragraphs:
                # 按文本长度排序，取最长的几个段落
                paragraphs.sort(key=lambda p: len(p.get_text()), reverse=True)
                content_parts = []
                total_length = 0
                
                for p in paragraphs[:10]:  # 最多取10个段落
                    text = p.get_text(strip=True)
                    if len(text) > 20:  # 只取有意义的段落
                        content_parts.append(text)
                        total_length += len(text)
                        if total_length > 500:  # 如果总长度超过500字符就停止
                            break
                
                if content_parts:
                    return ' '.join(content_parts)
            
            # 如果没有找到特定内容区域，返回body文本
            body = soup.find('body')
            if body:
                text = body.get_text(strip=True)
                if len(text) > 100:
                    return text
            
            return None
            
        except Exception as e:
            logger.warning(f"Error getting full content from {url}: {e}")
            return None
    
    def _parse_cnn(self, soup: BeautifulSoup, source: NewsSource) -> List[Dict[str, Any]]:
        """解析CNN页面"""
        articles = []
        
        # CNN文章链接选择器
        article_links = soup.select('a[href*="/2024/"], a[href*="/2025/"]')
        
        for link in article_links[:settings.max_articles_per_source]:
            try:
                href = link.get('href')
                if not href or not href.startswith('http'):
                    href = urljoin(source.url, href)
                
                title = link.get_text(strip=True)
                if not title or len(title) < 10:
                    continue
                
                article_data = {
                    'title': title,
                    'content': '',  # 稍后获取完整内容
                    'source_url': href,
                    'source_id': source.id,
                    'source_name': source.name,
                    'category': source.category,
                    'language': 'en'
                }
                
                articles.append(article_data)
                
            except Exception as e:
                logger.error(f"Error parsing CNN article: {e}")
                continue
        
        return articles
    
    def _parse_bbc(self, soup: BeautifulSoup, source: NewsSource) -> List[Dict[str, Any]]:
        """解析BBC页面"""
        articles = []
        
        # BBC文章链接选择器
        article_links = soup.select('a[href*="/news/"]')
        
        for link in article_links[:settings.max_articles_per_source]:
            try:
                href = link.get('href')
                if not href or not href.startswith('http'):
                    href = urljoin(source.url, href)
                
                title = link.get_text(strip=True)
                if not title or len(title) < 10:
                    continue
                
                article_data = {
                    'title': title,
                    'content': '',
                    'source_url': href,
                    'source_id': source.id,
                    'source_name': source.name,
                    'category': source.category,
                    'language': 'en'
                }
                
                articles.append(article_data)
                
            except Exception as e:
                logger.error(f"Error parsing BBC article: {e}")
                continue
        
        return articles
    
    def _parse_reuters(self, soup: BeautifulSoup, source: NewsSource) -> List[Dict[str, Any]]:
        """解析Reuters页面"""
        articles = []
        
        # Reuters文章链接选择器
        article_links = soup.select('a[href*="/article/"]')
        
        for link in article_links[:settings.max_articles_per_source]:
            try:
                href = link.get('href')
                if not href or not href.startswith('http'):
                    href = urljoin(source.url, href)
                
                title = link.get_text(strip=True)
                if not title or len(title) < 10:
                    continue
                
                article_data = {
                    'title': title,
                    'content': '',
                    'source_url': href,
                    'source_id': source.id,
                    'source_name': source.name,
                    'category': source.category,
                    'language': 'en'
                }
                
                articles.append(article_data)
                
            except Exception as e:
                logger.error(f"Error parsing Reuters article: {e}")
                continue
        
        return articles
    
    def _parse_techcrunch(self, soup: BeautifulSoup, source: NewsSource) -> List[Dict[str, Any]]:
        """解析TechCrunch页面"""
        articles = []
        
        # TechCrunch文章链接选择器
        article_links = soup.select('a[href*="/2024/"], a[href*="/2025/"]')
        
        for link in article_links[:settings.max_articles_per_source]:
            try:
                href = link.get('href')
                if not href or not href.startswith('http'):
                    href = urljoin(source.url, href)
                
                title = link.get_text(strip=True)
                if not title or len(title) < 10:
                    continue
                
                article_data = {
                    'title': title,
                    'content': '',
                    'source_url': href,
                    'source_id': source.id,
                    'source_name': source.name,
                    'category': source.category,
                    'language': 'en'
                }
                
                articles.append(article_data)
                
            except Exception as e:
                logger.error(f"Error parsing TechCrunch article: {e}")
                continue
        
        return articles
    
    def _parse_bloomberg(self, soup: BeautifulSoup, source: NewsSource) -> List[Dict[str, Any]]:
        """解析Bloomberg页面"""
        articles = []
        
        # Bloomberg文章链接选择器
        article_links = soup.select('a[href*="/news/"]')
        
        for link in article_links[:settings.max_articles_per_source]:
            try:
                href = link.get('href')
                if not href or not href.startswith('http'):
                    href = urljoin(source.url, href)
                
                title = link.get_text(strip=True)
                if not title or len(title) < 10:
                    continue
                
                article_data = {
                    'title': title,
                    'content': '',
                    'source_url': href,
                    'source_id': source.id,
                    'source_name': source.name,
                    'category': source.category,
                    'language': 'en'
                }
                
                articles.append(article_data)
                
            except Exception as e:
                logger.error(f"Error parsing Bloomberg article: {e}")
                continue
        
        return articles
    
    def _parse_generic(self, soup: BeautifulSoup, source: NewsSource) -> List[Dict[str, Any]]:
        """通用解析策略"""
        articles = []
        
        # 通用文章链接选择器
        article_links = soup.select('a[href*="article"], a[href*="news"], a[href*="story"]')
        
        for link in article_links[:settings.max_articles_per_source]:
            try:
                href = link.get('href')
                if not href or not href.startswith('http'):
                    href = urljoin(source.url, href)
                
                title = link.get_text(strip=True)
                if not title or len(title) < 10:
                    continue
                
                article_data = {
                    'title': title,
                    'content': '',
                    'source_url': href,
                    'source_id': source.id,
                    'source_name': source.name,
                    'category': source.category,
                    'language': 'en'
                }
                
                articles.append(article_data)
                
            except Exception as e:
                logger.error(f"Error parsing generic article: {e}")
                continue
        
        return articles
    
    def _parse_rss_date(self, date_str: str) -> Optional[datetime]:
        """解析RSS日期"""
        if not date_str:
            return None
        
        try:
            # 尝试解析常见的RSS日期格式
            import email.utils
            parsed_date = email.utils.parsedate_to_datetime(date_str)
            return parsed_date
        except Exception:
            try:
                # 尝试其他格式
                from dateutil import parser
                return parser.parse(date_str)
            except Exception:
                logger.warning(f"Could not parse date: {date_str}")
                return None 