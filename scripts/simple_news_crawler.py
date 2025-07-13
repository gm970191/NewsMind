#!/usr/bin/env python3
"""
简化新闻爬虫 - 只抓取标题和概要
"""
import asyncio
import sys
import os
import logging
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.database import SessionLocal
from backend.app.services.news_service import NewsRepository
from backend.app.services.crawler import NewsCrawler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """主函数"""
    logger.info("开始抓取新闻...")
    
    # 创建数据库会话
    db = SessionLocal()
    repo = NewsRepository(db)
    
    try:
        # 创建爬虫实例
        crawler = NewsCrawler(repo)
        
        # 抓取新闻
        new_articles = await crawler.crawl_today_news()
        
        logger.info(f"抓取完成！新增 {new_articles} 篇文章")
        
        # 显示统计信息
        stats = repo.get_statistics()
        logger.info(f"数据库统计:")
        logger.info(f"  总文章数: {stats.get('total_articles', 0)}")
        logger.info(f"  已翻译: {stats.get('translated_articles', 0)}")
        logger.info(f"  待翻译: {stats.get('untranslated_articles', 0)}")
        logger.info(f"  新闻源: {stats.get('total_sources', 0)}")
        
    except Exception as e:
        logger.error(f"抓取失败: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main()) 