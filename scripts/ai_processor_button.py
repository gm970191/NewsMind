#!/usr/bin/env python3
"""
AI处理按钮功能
检测并处理缺失的翻译和总结
"""
import asyncio
import sqlite3
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.services.ai_processor import AIProcessor
from backend.app.services.news_service import NewsRepository
from backend.app.core.database import get_db_session


class AIProcessorButton:
    """AI处理按钮功能"""
    
    def __init__(self):
        self.repo = NewsRepository()
        self.ai_processor = AIProcessor(self.repo)
    
    async def process_article_by_id(self, article_id: int) -> Dict[str, any]:
        """处理指定文章ID"""
        try:
            print(f"🔍 检查文章 {article_id} 的处理状态...")
            
            # 检查文章是否存在
            article = self.repo.get_article_by_id(article_id)
            if not article:
                return {"success": False, "message": "文章不存在"}
            
            # 检查当前处理状态
            status = self._check_processing_status(article_id)
            print(f"📊 当前状态: {status}")
            
            # 根据缺失内容进行处理
            if status['needs_summary'] or status['needs_translation']:
                print("🚀 开始AI处理...")
                success = await self.ai_processor.process_single_article(article)
                
                if success:
                    # 重新检查状态
                    new_status = self._check_processing_status(article_id)
                    return {
                        "success": True,
                        "message": "AI处理完成",
                        "old_status": status,
                        "new_status": new_status
                    }
                else:
                    return {"success": False, "message": "AI处理失败"}
            else:
                return {"success": True, "message": "文章已完全处理", "status": status}
                
        except Exception as e:
            print(f"❌ 处理失败: {e}")
            return {"success": False, "message": f"处理失败: {str(e)}"}
    
    def _check_processing_status(self, article_id: int) -> Dict[str, any]:
        """检查文章的处理状态"""
        try:
            conn = sqlite3.connect('backend/newsmind.db')
            cursor = conn.cursor()
            
            # 获取文章信息
            cursor.execute("""
                SELECT title, content, language, is_processed 
                FROM news_articles 
                WHERE id = ?
            """, (article_id,))
            article = cursor.fetchone()
            
            if not article:
                return {"error": "文章不存在"}
            
            title, content, language, is_processed = article
            
            # 获取AI处理结果
            cursor.execute("""
                SELECT summary_zh, summary_en, translation_zh 
                FROM processed_content 
                WHERE article_id = ?
            """, (article_id,))
            processed = cursor.fetchone()
            
            conn.close()
            
            # 分析状态
            has_summary_zh = processed and processed[0] and len(processed[0].strip()) > 0
            has_summary_en = processed and processed[1] and len(processed[1].strip()) > 0
            has_translation = processed and processed[2] and len(processed[2].strip()) > 0
            
            needs_summary = not has_summary_zh or not has_summary_en
            needs_translation = language != 'zh' and not has_translation
            
            return {
                "article_id": article_id,
                "title": title,
                "language": language,
                "is_processed": is_processed,
                "has_summary_zh": has_summary_zh,
                "has_summary_en": has_summary_en,
                "has_translation": has_translation,
                "needs_summary": needs_summary,
                "needs_translation": needs_translation,
                "needs_processing": needs_summary or needs_translation
            }
            
        except Exception as e:
            return {"error": f"检查状态失败: {str(e)}"}
    
    async def batch_process_unprocessed(self, limit: int = 10) -> Dict[str, any]:
        """批量处理未处理的文章"""
        try:
            print(f"🔍 查找未处理的文章（限制 {limit} 篇）...")
            
            # 获取未处理的文章
            conn = sqlite3.connect('backend/newsmind.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, title, language 
                FROM news_articles 
                WHERE is_processed = 0 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            
            unprocessed_articles = cursor.fetchall()
            conn.close()
            
            if not unprocessed_articles:
                return {"success": True, "message": "没有未处理的文章", "processed": 0}
            
            print(f"📝 找到 {len(unprocessed_articles)} 篇未处理文章")
            
            # 批量处理
            results = await self.ai_processor.process_articles(limit)
            
            return {
                "success": True,
                "message": f"批量处理完成",
                "total": results['total_articles'],
                "success_count": results['success_count'],
                "error_count": results['error_count'],
                "api_calls": results['api_calls']
            }
            
        except Exception as e:
            print(f"❌ 批量处理失败: {e}")
            return {"success": False, "message": f"批量处理失败: {str(e)}"}
    
    def get_processing_stats(self) -> Dict[str, any]:
        """获取处理统计信息"""
        try:
            conn = sqlite3.connect('backend/newsmind.db')
            cursor = conn.cursor()
            
            # 总文章数
            cursor.execute("SELECT COUNT(*) FROM news_articles")
            total_articles = cursor.fetchone()[0]
            
            # 已处理文章数
            cursor.execute("SELECT COUNT(*) FROM news_articles WHERE is_processed = 1")
            processed_articles = cursor.fetchone()[0]
            
            # 未处理文章数
            cursor.execute("SELECT COUNT(*) FROM news_articles WHERE is_processed = 0")
            unprocessed_articles = cursor.fetchone()[0]
            
            # 有AI处理记录的文章数
            cursor.execute("SELECT COUNT(*) FROM processed_content")
            ai_processed = cursor.fetchone()[0]
            
            # 语言分布
            cursor.execute("""
                SELECT language, COUNT(*) 
                FROM news_articles 
                GROUP BY language
            """)
            language_dist = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                "total_articles": total_articles,
                "processed_articles": processed_articles,
                "unprocessed_articles": unprocessed_articles,
                "ai_processed": ai_processed,
                "processing_rate": round(processed_articles / total_articles * 100, 2) if total_articles > 0 else 0,
                "language_distribution": language_dist
            }
            
        except Exception as e:
            return {"error": f"获取统计失败: {str(e)}"}


async def main():
    """主函数 - 用于测试"""
    processor = AIProcessorButton()
    
    print("🤖 AI处理按钮功能测试")
    print("=" * 50)
    
    # 获取统计信息
    stats = processor.get_processing_stats()
    print("📊 处理统计:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 50)
    
    # 测试处理单篇文章（如果有未处理的文章）
    if stats.get('unprocessed_articles', 0) > 0:
        print("🔍 测试处理单篇文章...")
        # 获取第一个未处理的文章
        conn = sqlite3.connect('backend/newsmind.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM news_articles WHERE is_processed = 0 LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        
        if result:
            article_id = result[0]
            result = await processor.process_article_by_id(article_id)
            print(f"处理结果: {result}")
    
    print("\n✅ 测试完成")


if __name__ == "__main__":
    asyncio.run(main()) 