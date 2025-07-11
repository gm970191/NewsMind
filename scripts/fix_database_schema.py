#!/usr/bin/env python3
"""
数据库结构修复脚本
删除旧的字段，确保表结构与模型一致
"""
import sys
from pathlib import Path

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal
from sqlalchemy import text


def fix_database_schema():
    """修复数据库表结构"""
    print("🔧 开始修复数据库表结构...")
    
    db = SessionLocal()
    
    try:
        # 检查当前表结构
        result = db.execute(text('PRAGMA table_info(news_articles)'))
        columns = [row[1] for row in result.fetchall()]
        print(f"当前字段: {columns}")
        
        # 检查索引
        result = db.execute(text('PRAGMA index_list(news_articles)'))
        indexes = [row[1] for row in result.fetchall()]
        print(f"当前索引: {indexes}")
        
        # 删除依赖title字段的索引
        title_indexes = [idx for idx in indexes if 'title' in idx.lower()]
        for index in title_indexes:
            print(f"删除索引: {index}")
            try:
                db.execute(text(f'DROP INDEX {index}'))
                print(f"✓ 成功删除索引: {index}")
            except Exception as e:
                print(f"✗ 删除索引 {index} 失败: {e}")
        
        # 需要删除的旧字段
        old_columns = ['title', 'content', 'language', 'content_length']
        
        # 删除旧字段
        for column in old_columns:
            if column in columns:
                print(f"删除字段: {column}")
                try:
                    db.execute(text(f'ALTER TABLE news_articles DROP COLUMN {column}'))
                    print(f"✓ 成功删除字段: {column}")
                except Exception as e:
                    print(f"✗ 删除字段 {column} 失败: {e}")
        
        # 提交更改
        db.commit()
        
        # 验证修复结果
        result = db.execute(text('PRAGMA table_info(news_articles)'))
        new_columns = [row[1] for row in result.fetchall()]
        print(f"修复后字段: {new_columns}")
        
        # 检查是否还有旧字段
        remaining_old = [col for col in old_columns if col in new_columns]
        if remaining_old:
            print(f"⚠ 仍有旧字段存在: {remaining_old}")
        else:
            print("✅ 数据库表结构修复完成！")
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    fix_database_schema() 