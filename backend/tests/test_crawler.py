"""
News crawler tests
"""
import pytest
import asyncio
from unittest.mock import Mock, patch

from app.core.database import SessionLocal, create_tables, drop_tables
from app.services.news_service import NewsRepository
from app.services.crawler import WebCrawler
from app.models.news import NewsSource


@pytest.fixture
def db():
    """数据库会话fixture"""
    drop_tables()
    create_tables()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def repo(db):
    """Repository fixture"""
    return NewsRepository(db)


@pytest.fixture
def test_source(repo):
    """测试新闻源"""
    source_data = {
        "name": "Test News",
        "url": "https://test-news.com",
        "type": "web",
        "category": "测试"
    }
    return repo.create_source(source_data)


@pytest.mark.asyncio
async def test_crawler_initialization(repo):
    """测试爬虫初始化"""
    async with WebCrawler(repo) as crawler:
        assert crawler.browser is not None
        assert crawler.page is not None


@pytest.mark.asyncio
async def test_crawl_empty_sources(repo):
    """测试空新闻源的情况"""
    async with WebCrawler(repo) as crawler:
        results = await crawler.crawl_news_sources()
        
        assert results['total_sources'] == 0
        assert results['success_count'] == 0
        assert results['error_count'] == 0
        assert results['new_articles'] == 0


@pytest.mark.asyncio
async def test_crawl_web_source_mock(repo, test_source):
    """测试网页抓取（使用Mock）"""
    with patch('playwright.async_api.async_playwright') as mock_playwright:
        # Mock Playwright
        mock_browser = Mock()
        mock_page = Mock()
        mock_playwright.return_value.__aenter__.return_value.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        
        # Mock页面内容
        mock_page.content.return_value = """
        <html>
            <body>
                <a href="/article1">Test Article 1</a>
                <a href="/article2">Test Article 2</a>
            </body>
        </html>
        """
        
        async with WebCrawler(repo) as crawler:
            articles = await crawler.crawl_web_source(test_source)
            
            # 验证抓取结果
            assert len(articles) > 0
            assert all('title' in article for article in articles)
            assert all('source_url' in article for article in articles)


@pytest.mark.asyncio
async def test_crawl_rss_source_mock(repo):
    """测试RSS抓取（使用Mock）"""
    # 创建RSS新闻源
    source_data = {
        "name": "Test RSS",
        "url": "https://test-rss.com/feed.xml",
        "type": "rss",
        "category": "测试"
    }
    rss_source = repo.create_source(source_data)
    
    with patch('feedparser.parse') as mock_feedparse:
        # Mock RSS feed
        mock_feed = Mock()
        mock_feed.entries = [
            Mock(
                title="RSS Test Article",
                link="https://test-rss.com/article1",
                summary="This is a test RSS article",
                published="2024-01-01T00:00:00Z"
            )
        ]
        mock_feedparse.return_value = mock_feed
        
        async with WebCrawler(repo) as crawler:
            articles = await crawler.crawl_rss_source(rss_source)
            
            # 验证RSS解析结果
            assert len(articles) == 1
            assert articles[0]['title'] == "RSS Test Article"
            assert articles[0]['source_url'] == "https://test-rss.com/article1"


@pytest.mark.asyncio
async def test_parse_cnn_mock(repo, test_source):
    """测试CNN解析"""
    from bs4 import BeautifulSoup
    
    # Mock CNN页面内容
    html_content = """
    <html>
        <body>
            <a href="/2024/01/test-article">CNN Test Article</a>
            <a href="/2025/01/another-article">Another CNN Article</a>
        </body>
    </html>
    """
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    async with WebCrawler(repo) as crawler:
        articles = crawler._parse_cnn(soup, test_source)
        
        assert len(articles) > 0
        assert all('CNN' in article['title'] or 'Test' in article['title'] for article in articles)


@pytest.mark.asyncio
async def test_parse_bbc_mock(repo, test_source):
    """测试BBC解析"""
    from bs4 import BeautifulSoup
    
    # Mock BBC页面内容
    html_content = """
    <html>
        <body>
            <a href="/news/test-article">BBC Test Article</a>
            <a href="/news/another-article">Another BBC Article</a>
        </body>
    </html>
    """
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    async with WebCrawler(repo) as crawler:
        articles = crawler._parse_bbc(soup, test_source)
        
        assert len(articles) > 0
        assert all('BBC' in article['title'] or 'Test' in article['title'] for article in articles)


def test_parse_rss_date():
    """测试RSS日期解析"""
    from app.services.crawler import WebCrawler
    
    crawler = WebCrawler(Mock())
    
    # 测试标准RSS日期格式
    date_str = "Mon, 01 Jan 2024 00:00:00 GMT"
    parsed_date = crawler._parse_rss_date(date_str)
    assert parsed_date is not None
    assert parsed_date.year == 2024
    assert parsed_date.month == 1
    assert parsed_date.day == 1
    
    # 测试无效日期
    invalid_date = "invalid-date"
    parsed_date = crawler._parse_rss_date(invalid_date)
    assert parsed_date is None


@pytest.mark.asyncio
async def test_get_full_content_mock(repo):
    """测试获取完整内容"""
    with patch('playwright.async_api.async_playwright') as mock_playwright:
        mock_browser = Mock()
        mock_page = Mock()
        mock_playwright.return_value.__aenter__.return_value.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        
        # Mock页面内容
        mock_page.content.return_value = """
        <html>
            <body>
                <article>
                    <h1>Test Article</h1>
                    <p>This is the full content of the article.</p>
                </article>
            </body>
        </html>
        """
        
        async with WebCrawler(repo) as crawler:
            content = await crawler._get_full_content("https://test.com/article")
            
            assert content is not None
            assert "Test Article" in content
            assert "full content" in content 