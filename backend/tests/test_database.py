"""
Database operation tests
"""
import pytest
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, create_tables, drop_tables
from app.services.news_service import NewsRepository
from app.models.news import NewsArticle, NewsSource


@pytest.fixture
def db():
    """数据库会话fixture"""
    # 每次测试前重新创建表
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


def test_create_source(repo):
    """测试创建新闻源"""
    source_data = {
        "name": "Test Source 1",
        "url": "https://test1.com",
        "type": "web",
        "category": "测试",
        "weight": 1.0
    }
    
    source = repo.create_source(source_data)
    assert source.id is not None
    assert source.name == "Test Source 1"
    assert source.url == "https://test1.com"


def test_get_source_by_url(repo):
    """测试根据URL获取新闻源"""
    # 先创建一个源
    source_data = {
        "name": "Test Source 2",
        "url": "https://test2.com",
        "type": "web",
        "category": "测试"
    }
    created_source = repo.create_source(source_data)
    
    # 根据URL获取
    found_source = repo.get_source_by_url("https://test2.com")
    assert found_source is not None
    assert found_source.id == created_source.id


def test_create_article(repo):
    """测试创建新闻文章"""
    # 先创建新闻源
    source_data = {
        "name": "Test Source 3",
        "url": "https://test3.com",
        "type": "web",
        "category": "测试"
    }
    source = repo.create_source(source_data)
    
    # 创建文章
    article_data = {
        "title": "Test Article",
        "content": "This is a test article content.",
        "source_url": "https://test3.com/article1",
        "source_id": source.id,
        "source_name": source.name,
        "category": "测试"
    }
    
    article = repo.create_article(article_data)
    assert article.id is not None
    assert article.title == "Test Article"
    assert article.source_id == source.id


def test_get_articles(repo):
    """测试获取文章列表"""
    # 创建测试数据
    source_data = {
        "name": "Test Source 4",
        "url": "https://test4.com",
        "type": "web",
        "category": "测试"
    }
    source = repo.create_source(source_data)
    
    # 创建多篇文章
    for i in range(5):
        article_data = {
            "title": f"Test Article {i}",
            "content": f"This is test article {i} content.",
            "source_url": f"https://test4.com/article{i}",
            "source_id": source.id,
            "source_name": source.name,
            "category": "测试"
        }
        repo.create_article(article_data)
    
    # 测试获取文章列表
    articles = repo.get_articles(limit=10)
    assert len(articles) == 5
    
    # 测试分页
    articles = repo.get_articles(skip=2, limit=2)
    assert len(articles) == 2


def test_search_articles(repo):
    """测试搜索文章"""
    # 创建测试数据
    source_data = {
        "name": "Test Source 5",
        "url": "https://test5.com",
        "type": "web",
        "category": "测试"
    }
    source = repo.create_source(source_data)
    
    # 创建包含特定关键词的文章
    article_data = {
        "title": "AI Technology News",
        "content": "This article discusses artificial intelligence technology.",
        "source_url": "https://test5.com/ai-article",
        "source_id": source.id,
        "source_name": source.name,
        "category": "科技"
    }
    repo.create_article(article_data)
    
    # 搜索包含"AI"的文章
    results = repo.search_articles("AI")
    assert len(results) == 1
    assert "AI" in results[0].title


def test_get_statistics(repo):
    """测试获取统计信息"""
    # 创建测试数据
    source_data = {
        "name": "Test Source 6",
        "url": "https://test6.com",
        "type": "web",
        "category": "测试"
    }
    source = repo.create_source(source_data)
    
    # 创建文章
    for i in range(3):
        article_data = {
            "title": f"Test Article {i}",
            "content": f"This is test article {i} content.",
            "source_url": f"https://test6.com/article{i}",
            "source_id": source.id,
            "source_name": source.name,
            "category": "测试",
            "is_processed": i < 2  # 前两篇已处理
        }
        repo.create_article(article_data)
    
    # 获取统计信息
    stats = repo.get_statistics()
    assert stats["total_articles"] == 3
    assert stats["processed_articles"] == 2
    assert stats["unprocessed_articles"] == 1
    assert stats["total_sources"] == 1
    assert stats["processing_rate"] == 66.66666666666666 