"""
Task scheduler for news collection
"""
import logging
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import settings
from app.services.crawler import WebCrawler
from app.services.news_service import NewsRepository
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)


class NewsScheduler:
    """新闻采集定时任务调度器"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
    
    def start(self):
        """启动调度器"""
        if not self.is_running:
            # 添加定时采集任务
            self.scheduler.add_job(
                func=self._crawl_job,
                trigger=CronTrigger(hour='*/6'),  # 每6小时执行一次
                id='news_crawl',
                name='News Collection Job',
                replace_existing=True
            )
            
            # 添加数据清理任务
            self.scheduler.add_job(
                func=self._cleanup_job,
                trigger=CronTrigger(hour=2, minute=0),  # 每天凌晨2点执行
                id='data_cleanup',
                name='Data Cleanup Job',
                replace_existing=True
            )
            
            # 启动调度器
            self.scheduler.start()
            self.is_running = True
            logger.info("News scheduler started")
    
    def stop(self):
        """停止调度器"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("News scheduler stopped")
    
    async def _crawl_job(self):
        """新闻采集任务"""
        logger.info("Starting news collection job")
        
        try:
            db = SessionLocal()
            repo = NewsRepository(db)
            
            async with WebCrawler(repo) as crawler:
                results = await crawler.crawl_news_sources()
                
                logger.info(f"News collection completed: {results}")
                
                # 记录任务执行结果
                self._log_job_result('crawl', results)
                
        except Exception as e:
            logger.error(f"Error in news collection job: {e}")
            self._log_job_result('crawl', {'error': str(e)})
        finally:
            if 'db' in locals():
                db.close()
    
    async def _cleanup_job(self):
        """数据清理任务"""
        logger.info("Starting data cleanup job")
        
        try:
            db = SessionLocal()
            repo = NewsRepository(db)
            
            # 删除旧文章
            deleted_count = repo.delete_old_articles()
            
            logger.info(f"Data cleanup completed: deleted {deleted_count} old articles")
            
            # 记录任务执行结果
            self._log_job_result('cleanup', {'deleted_count': deleted_count})
            
        except Exception as e:
            logger.error(f"Error in data cleanup job: {e}")
            self._log_job_result('cleanup', {'error': str(e)})
        finally:
            if 'db' in locals():
                db.close()
    
    def _log_job_result(self, job_type: str, result: dict):
        """记录任务执行结果"""
        timestamp = datetime.utcnow().isoformat()
        logger.info(f"Job {job_type} completed at {timestamp}: {result}")
    
    def get_jobs(self):
        """获取所有任务"""
        return self.scheduler.get_jobs()
    
    def add_manual_job(self, job_func, **kwargs):
        """添加手动任务"""
        job_id = f"manual_{datetime.utcnow().timestamp()}"
        self.scheduler.add_job(
            func=job_func,
            id=job_id,
            **kwargs
        )
        return job_id
    
    def remove_job(self, job_id: str):
        """移除任务"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Job {job_id} removed")
            return True
        except Exception as e:
            logger.error(f"Error removing job {job_id}: {e}")
            return False


# 全局调度器实例
news_scheduler = NewsScheduler() 