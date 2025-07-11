#!/usr/bin/env python3
"""
数据库升级脚本 v2 - 重新设计news_articles表结构
将现有的title和content字段迁移到original_title和original_content
添加新的翻译相关字段
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upgrade_database():
    """升级数据库结构"""
    try:
        # 创建数据库连接 - 使用SQLite数据库
        database_url = "sqlite:///./newsmind.db"
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with engine.connect() as connection:
            logger.info("开始数据库升级...")
            
            # 检查当前表结构
            inspector = inspect(engine)
            existing_columns = [col['name'] for col in inspector.get_columns('news_articles')]
            logger.info(f"当前字段: {existing_columns}")
            
            # 需要添加的字段列表
            required_fields = [
                ('original_title', 'VARCHAR(500)'),
                ('original_content', 'TEXT'),
                ('original_language', 'VARCHAR(10)'),
                ('translated_title', 'VARCHAR(500)'),
                ('translated_content', 'TEXT'),
                ('is_title_translated', 'BOOLEAN DEFAULT FALSE'),
                ('is_content_translated', 'BOOLEAN DEFAULT FALSE'),
                ('translation_quality_score', 'FLOAT DEFAULT 0.0'),
                ('quality_score', 'FLOAT DEFAULT 0.0'),
                ('is_processed', 'BOOLEAN DEFAULT FALSE'),
                ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
                ('updated_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP')
            ]
            
            # 添加缺失的字段
            for field_name, field_type in required_fields:
                if field_name not in existing_columns:
                    logger.info(f"添加字段: {field_name}")
                    try:
                        connection.execute(text(f"ALTER TABLE news_articles ADD COLUMN {field_name} {field_type}"))
                    except Exception as e:
                        logger.warning(f"添加字段 {field_name} 失败: {e}")
            
            # 迁移现有数据
            logger.info("迁移现有数据...")
            
            # 将现有的title和content迁移到original字段
            if 'title' in existing_columns and 'original_title' not in existing_columns:
                connection.execute(text("""
                    UPDATE news_articles 
                    SET original_title = title
                    WHERE original_title IS NULL
                """))
            
            if 'content' in existing_columns and 'original_content' not in existing_columns:
                connection.execute(text("""
                    UPDATE news_articles 
                    SET original_content = content
                    WHERE original_content IS NULL
                """))
            
            if 'language' in existing_columns and 'original_language' not in existing_columns:
                connection.execute(text("""
                    UPDATE news_articles 
                    SET original_language = language
                    WHERE original_language IS NULL
                """))
            
            # 处理翻译状态
            logger.info("处理翻译状态...")
            
            # 如果原始语言是中文，标记为已翻译
            connection.execute(text("""
                UPDATE news_articles 
                SET is_title_translated = TRUE, 
                    is_content_translated = TRUE,
                    translated_title = original_title,
                    translated_content = original_content
                WHERE original_language = 'zh' OR original_language = 'zh-CN'
            """))
            
            connection.commit()
            logger.info("数据库升级完成！")
            
            # 验证升级结果
            logger.info("验证升级结果...")
            result = connection.execute(text("SELECT COUNT(*) as count FROM news_articles"))
            total_count = result.fetchone()[0]
            
            result = connection.execute(text("SELECT COUNT(*) as count FROM news_articles WHERE original_title IS NOT NULL"))
            migrated_count = result.fetchone()[0]
            
            result = connection.execute(text("SELECT COUNT(*) as count FROM news_articles WHERE is_title_translated = TRUE"))
            translated_count = result.fetchone()[0]
            
            logger.info(f"总文章数: {total_count}")
            logger.info(f"已迁移文章数: {migrated_count}")
            logger.info(f"已翻译文章数: {translated_count}")
            
    except Exception as e:
        logger.error(f"数据库升级失败: {e}")
        raise

def verify_database_structure():
    """验证数据库结构"""
    try:
        database_url = "sqlite:///./newsmind.db"
        engine = create_engine(database_url)
        inspector = inspect(engine)
        
        # 检查news_articles表结构
        columns = inspector.get_columns('news_articles')
        column_names = [col['name'] for col in columns]
        
        required_columns = [
            'original_title', 'original_content', 'original_language',
            'translated_title', 'translated_content',
            'is_title_translated', 'is_content_translated', 'translation_quality_score',
            'quality_score', 'is_processed', 'created_at', 'updated_at'
        ]
        
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            logger.error(f"缺少必要字段: {missing_columns}")
            return False
        
        logger.info("数据库结构验证通过")
        logger.info(f"所有字段: {column_names}")
        return True
        
    except Exception as e:
        logger.error(f"数据库结构验证失败: {e}")
        return False

if __name__ == "__main__":
    logger.info("开始数据库升级流程...")
    
    # 执行升级
    upgrade_database()
    
    # 验证结果
    if verify_database_structure():
        logger.info("数据库升级成功完成！")
    else:
        logger.error("数据库升级验证失败！")
        sys.exit(1) 