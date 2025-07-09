#!/usr/bin/env python3
"""
创建测试数据
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal
from app.services.news_service import NewsRepository
from app.models.news import NewsArticle


def create_test_data():
    """创建测试数据"""
    print("创建测试数据...")
    
    db = SessionLocal()
    repo = NewsRepository(db)
    
    try:
        # 获取新闻源
        sources = repo.get_active_sources()
        if not sources:
            print("没有找到新闻源，请先运行 init_db.py")
            return
        
        source = sources[0]  # 使用第一个新闻源
        
        # 创建测试文章
        test_articles = [
            {
                'title': 'AI技术突破：新的语言模型在多个基准测试中表现优异',
                'content': '最新研究显示，新一代人工智能语言模型在自然语言处理任务中取得了显著进展。该模型在阅读理解、文本生成和翻译等多个基准测试中都超越了之前的记录。研究人员表示，这一突破将为AI应用带来更多可能性。',
                'source_url': 'https://example.com/ai-breakthrough-2024',
                'source_id': source.id,
                'source_name': source.name,
                'publish_time': datetime.now() - timedelta(hours=2),
                'category': '科技',
                'language': 'zh',
                'quality_score': 8.5,
                'is_processed': False
            },
            {
                'title': '全球经济复苏：主要经济体增长数据超出预期',
                'content': '根据最新发布的全球经济数据，主要经济体在2024年第一季度表现强劲，增长数据普遍超出市场预期。专家分析认为，这一趋势表明全球经济正在稳步复苏，但仍需关注通胀和地缘政治风险。',
                'source_url': 'https://example.com/global-economy-recovery',
                'source_id': source.id,
                'source_name': source.name,
                'publish_time': datetime.now() - timedelta(hours=4),
                'category': '财经',
                'language': 'zh',
                'quality_score': 9.0,
                'is_processed': True
            },
            {
                'title': '气候变化：联合国发布最新环境报告',
                'content': '联合国环境规划署今日发布最新气候变化报告，指出全球温室气体排放仍在上升，但可再生能源的使用也在快速增长。报告呼吁各国加强合作，采取更积极的措施应对气候变化挑战。',
                'source_url': 'https://example.com/climate-change-report-2024',
                'source_id': source.id,
                'source_name': source.name,
                'publish_time': datetime.now() - timedelta(hours=6),
                'category': '国际',
                'language': 'zh',
                'quality_score': 8.0,
                'is_processed': False
            },
            {
                'title': '科技创新：量子计算机在密码学领域取得重要进展',
                'content': '科学家们宣布在量子计算机研究方面取得重要突破，新的量子算法能够更高效地解决复杂的密码学问题。这一进展对网络安全和加密技术发展具有重要意义。',
                'source_url': 'https://example.com/quantum-computing-advance',
                'source_id': source.id,
                'source_name': source.name,
                'publish_time': datetime.now() - timedelta(hours=8),
                'category': '科技',
                'language': 'zh',
                'quality_score': 9.5,
                'is_processed': True
            },
            {
                'title': '国际关系：多国签署新的贸易协定',
                'content': '在今日举行的国际经济论坛上，多个国家签署了新的贸易协定，旨在促进区域经济合作和贸易自由化。该协定预计将为参与国带来显著的经济效益。',
                'source_url': 'https://example.com/trade-agreement-2024',
                'source_id': source.id,
                'source_name': source.name,
                'publish_time': datetime.now() - timedelta(hours=10),
                'category': '国际',
                'language': 'zh',
                'quality_score': 7.5,
                'is_processed': False
            }
        ]
        
        # 保存测试文章
        for article_data in test_articles:
            try:
                # 检查是否已存在
                existing = repo.get_article_by_url(article_data['source_url'])
                if not existing:
                    repo.create_article(article_data)
                    print(f"✓ 创建测试文章: {article_data['title']}")
                else:
                    print(f"⚠ 文章已存在: {article_data['title']}")
            except Exception as e:
                print(f"✗ 创建文章失败: {e}")
        
        print(f"\n测试数据创建完成！")
        
        # 显示统计信息
        articles = repo.get_articles(limit=100)
        print(f"数据库中共有 {len(articles)} 篇文章")
        
    except Exception as e:
        print(f"创建测试数据时出错: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    create_test_data() 