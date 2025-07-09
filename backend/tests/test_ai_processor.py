"""
AI processor tests
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from app.core.database import SessionLocal, create_tables, drop_tables
from app.services.news_service import NewsRepository
from app.services.ai_processor import AIProcessor
from app.models.news import NewsArticle, NewsSource, ProcessedContent


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
def test_article(repo):
    """测试文章"""
    article_data = {
        "title": "Test Article",
        "content": "This is a test article content for AI processing. It contains enough text to generate meaningful summaries and translations.",
        "source_url": "https://test.com/article1",
        "source_id": 1,
        "source_name": "Test Source",
        "category": "测试",
        "language": "en",
        "is_processed": False
    }
    return repo.create_article(article_data)


@pytest.mark.asyncio
async def test_ai_processor_initialization(repo):
    """测试AI处理器初始化"""
    with patch('app.services.ai_processor.ChatDeepSeek'):
        processor = AIProcessor(repo)
        assert processor.repo == repo
        assert processor.text_splitter is not None


@pytest.mark.asyncio
async def test_process_empty_articles(repo):
    """测试空文章列表的处理"""
    with patch('app.services.ai_processor.ChatDeepSeek'):
        processor = AIProcessor(repo)
        results = await processor.process_articles(limit=10)
        
        assert results['total_articles'] == 0
        assert results['success_count'] == 0
        assert results['error_count'] == 0
        assert results['api_calls'] == 0


@pytest.mark.asyncio
async def test_process_single_article_mock(repo, test_article):
    """测试单篇文章处理（使用Mock）"""
    with patch('app.services.ai_processor.ChatDeepSeek') as mock_llm_class:
        # Mock LLM实例
        mock_llm_instance = Mock()
        mock_response = Mock()
        mock_response.content = "This is a test summary"
        mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)
        mock_llm_class.return_value = mock_llm_instance
        
        processor = AIProcessor(repo)
        success = await processor.process_single_article(test_article)
        
        # 验证处理结果
        assert success is True
        
        # 验证文章状态已更新
        updated_article = repo.get_article_by_id(test_article.id)
        assert updated_article.is_processed is True
        
        # 验证处理结果已保存
        processed_content = repo.get_processed_content(test_article.id)
        assert processed_content is not None
        assert processed_content.summary_zh is not None
        assert processed_content.summary_en is not None


@pytest.mark.asyncio
async def test_generate_summary_zh_mock(repo):
    """测试中文摘要生成"""
    with patch('app.services.ai_processor.ChatDeepSeek') as mock_llm_class:
        mock_llm_instance = Mock()
        mock_response = Mock()
        mock_response.content = "这是一篇测试文章的摘要"
        mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)
        mock_llm_class.return_value = mock_llm_instance
        
        processor = AIProcessor(repo)
        content = "This is a test article content for generating Chinese summary."
        summary = await processor._generate_summary_zh(content)
        
        assert summary is not None
        assert len(summary) > 0
        assert "摘要" in summary


@pytest.mark.asyncio
async def test_generate_summary_en_mock(repo):
    """测试英文摘要生成"""
    with patch('app.services.ai_processor.ChatDeepSeek') as mock_llm_class:
        mock_llm_instance = Mock()
        mock_response = Mock()
        mock_response.content = "This is a test summary in English"
        mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)
        mock_llm_class.return_value = mock_llm_instance
        
        processor = AIProcessor(repo)
        content = "This is a test article content for generating English summary."
        summary = await processor._generate_summary_en(content)
        
        assert summary is not None
        assert len(summary) > 0
        assert "test" in summary.lower()


@pytest.mark.asyncio
async def test_translate_to_chinese_mock(repo):
    """测试翻译为中文"""
    with patch('app.services.ai_processor.ChatDeepSeek') as mock_llm_class:
        mock_llm_instance = Mock()
        mock_response = Mock()
        mock_response.content = "这是一篇英文文章的翻译"
        mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)
        mock_llm_class.return_value = mock_llm_instance
        
        processor = AIProcessor(repo)
        content = "This is an English article that needs to be translated to Chinese."
        translation = await processor._translate_to_chinese(content)
        
        assert translation is not None
        assert len(translation) > 0
        assert "翻译" in translation


@pytest.mark.asyncio
async def test_evaluate_quality_mock(repo):
    """测试质量评估"""
    with patch('app.services.ai_processor.ChatDeepSeek') as mock_llm_class:
        mock_llm_instance = Mock()
        mock_response = Mock()
        mock_response.content = "8.5"
        mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)
        mock_llm_class.return_value = mock_llm_instance
        
        processor = AIProcessor(repo)
        content = "This is a high-quality test article with good content and structure."
        score = await processor._evaluate_quality(content)
        
        assert score is not None
        assert isinstance(score, float)
        assert 0.0 <= score <= 10.0


def test_clean_summary():
    """测试摘要清理"""
    # 直接测试清理函数，不创建AIProcessor实例
    from app.services.ai_processor import AIProcessor
    
    # 创建一个简单的Mock对象
    mock_repo = Mock()
    
    with patch('app.services.ai_processor.ChatDeepSeek'):
        processor = AIProcessor(mock_repo)
        
        # 测试移除前缀
        summary_with_prefix = "摘要：这是一篇测试文章"
        cleaned = processor._clean_summary(summary_with_prefix)
        assert cleaned == "这是一篇测试文章"
        
        # 测试移除多余空格
        summary_with_spaces = "  这是  一篇  测试文章  "
        cleaned = processor._clean_summary(summary_with_spaces)
        assert cleaned == "这是 一篇 测试文章"


@pytest.mark.asyncio
async def test_reprocess_article_mock(repo, test_article):
    """测试重新处理文章"""
    with patch('app.services.ai_processor.ChatDeepSeek') as mock_llm_class:
        mock_llm_instance = Mock()
        mock_response = Mock()
        mock_response.content = "Updated test summary"
        mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)
        mock_llm_class.return_value = mock_llm_instance
        
        processor = AIProcessor(repo)
        
        # 先处理一次
        success1 = await processor.process_single_article(test_article)
        assert success1 is True
        
        # 重新处理
        success2 = await processor.reprocess_article(test_article.id)
        assert success2 is True
        
        # 验证处理结果已更新
        processed_content = repo.get_processed_content(test_article.id)
        assert processed_content is not None
        assert "Updated" in processed_content.summary_zh


@pytest.mark.asyncio
async def test_process_single_article_by_id_mock(repo, test_article):
    """测试根据ID处理文章"""
    with patch('app.services.ai_processor.ChatDeepSeek') as mock_llm_class:
        mock_llm_instance = Mock()
        mock_response = Mock()
        mock_response.content = "Test summary"
        mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)
        mock_llm_class.return_value = mock_llm_instance
        
        processor = AIProcessor(repo)
        success = await processor.process_single_article_by_id(test_article.id)
        
        assert success is True
        
        # 验证文章已处理
        updated_article = repo.get_article_by_id(test_article.id)
        assert updated_article.is_processed is True


@pytest.mark.asyncio
async def test_process_nonexistent_article(repo):
    """测试处理不存在的文章"""
    with patch('app.services.ai_processor.ChatDeepSeek'):
        processor = AIProcessor(repo)
        success = await processor.process_single_article_by_id(999)
        
        assert success is False


@pytest.mark.asyncio
async def test_get_processing_stats(repo):
    """测试获取处理统计信息"""
    with patch('app.services.ai_processor.ChatDeepSeek'):
        processor = AIProcessor(repo)
        stats = await processor.get_processing_stats()
        
        assert isinstance(stats, dict)
        assert "total_processed" in stats
        assert "average_quality_score" in stats
        assert "average_processing_time" in stats 