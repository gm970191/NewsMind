#!/usr/bin/env python3
"""
向 news_articles 表添加缺失的 AI 处理字段
"""

import sqlite3
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_ai_fields_to_news_articles():
    """向 news_articles 表添加 AI 处理字段"""
    
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        logger.info("开始向 news_articles 表添加 AI 处理字段...")
        
        # 需要添加的字段列表
        fields_to_add = [
            ('summary_zh', 'TEXT'),
            ('detailed_summary_zh', 'TEXT')
        ]
        
        # 获取当前表结构
        cursor.execute("PRAGMA table_info(news_articles)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        logger.info(f"当前字段: {existing_columns}")
        
        # 添加缺失的字段
        for field_name, field_type in fields_to_add:
            if field_name not in existing_columns:
                logger.info(f"添加字段: {field_name}")
                try:
                    cursor.execute(f"ALTER TABLE news_articles ADD COLUMN {field_name} {field_type}")
                    logger.info(f"✅ 成功添加字段: {field_name}")
                except Exception as e:
                    logger.warning(f"添加字段 {field_name} 失败: {e}")
            else:
                logger.info(f"字段 {field_name} 已存在，跳过")
        
        # 验证字段添加结果
        cursor.execute("PRAGMA table_info(news_articles)")
        final_columns = [row[1] for row in cursor.fetchall()]
        logger.info(f"最终字段: {final_columns}")
        
        # 检查是否所有必需字段都存在
        required_fields = ['summary_zh', 'detailed_summary_zh']
        missing_fields = [field for field in required_fields if field not in final_columns]
        
        if missing_fields:
            logger.error(f"❌ 仍有缺失字段: {missing_fields}")
            return False
        else:
            logger.info("✅ 所有必需字段已添加")
        
        # 提交事务
        conn.commit()
        logger.info("✅ 字段添加完成！")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 添加字段失败: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def verify_ai_fields():
    """验证 AI 字段是否正确添加"""
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        logger.info("\n🔍 验证 AI 字段...")
        
        # 检查字段是否存在
        cursor.execute("PRAGMA table_info(news_articles)")
        columns = [row[1] for row in cursor.fetchall()]
        
        required_fields = ['summary_zh', 'detailed_summary_zh']
        for field in required_fields:
            if field in columns:
                logger.info(f"✅ {field} 字段存在")
            else:
                logger.error(f"❌ {field} 字段缺失")
        
        # 检查现有数据
        cursor.execute("SELECT COUNT(*) FROM news_articles")
        total_articles = cursor.fetchone()[0]
        logger.info(f"总文章数: {total_articles}")
        
        cursor.execute("SELECT COUNT(*) FROM news_articles WHERE summary_zh IS NOT NULL")
        articles_with_summary = cursor.fetchone()[0]
        logger.info(f"包含摘要的文章数: {articles_with_summary}")
        
        cursor.execute("SELECT COUNT(*) FROM news_articles WHERE detailed_summary_zh IS NOT NULL")
        articles_with_detailed = cursor.fetchone()[0]
        logger.info(f"包含详细摘要的文章数: {articles_with_detailed}")
        
    except Exception as e:
        logger.error(f"验证失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 开始向 news_articles 表添加 AI 处理字段...")
    success = add_ai_fields_to_news_articles()
    if success:
        verify_ai_fields()
        print("✅ 字段添加完成！")
    else:
        print("❌ 字段添加失败！") 