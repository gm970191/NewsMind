#!/usr/bin/env python3
"""
清理数据库中的无效新闻文章
删除内容为空、仅有HTML标签、无实际内容的记录
"""
import sqlite3
import re
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from news_filter import clean_html_tags, is_valid_content

def check_article_validity(title, content):
    """检查文章是否有效"""
    if not title or not content:
        return False, "标题或内容为空"
    
    # 清洗HTML标签
    clean_title = clean_html_tags(title)
    clean_content = clean_html_tags(content)
    
    # 检查标题有效性
    if not is_valid_content(clean_title, min_length=5):
        return False, "标题无效"
    
    # 检查内容有效性
    if not is_valid_content(clean_content, min_length=100):
        return False, "内容无效"
    
    return True, "有效"

def cleanup_invalid_articles():
    """清理无效文章"""
    print("🧹 开始清理数据库中的无效新闻...")
    print("=" * 60)
    
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        # 获取所有文章
        cursor.execute("SELECT id, title, content FROM news_articles")
        articles = cursor.fetchall()
        
        print(f"📊 总文章数: {len(articles)}")
        
        invalid_count = 0
        valid_count = 0
        
        for article_id, title, content in articles:
            is_valid, reason = check_article_validity(title, content)
            
            if not is_valid:
                print(f"   🗑️  删除无效文章 ID:{article_id} - {reason}")
                print(f"      标题: {title[:50]}...")
                print(f"      内容长度: {len(content) if content else 0}")
                
                # 删除无效文章
                cursor.execute("DELETE FROM news_articles WHERE id = ?", (article_id,))
                
                # 同时删除相关的processed_content记录
                cursor.execute("DELETE FROM processed_content WHERE article_id = ?", (article_id,))
                
                invalid_count += 1
            else:
                valid_count += 1
        
        # 提交更改
        conn.commit()
        
        print(f"\n📈 清理结果:")
        print(f"   ✅ 保留有效文章: {valid_count}")
        print(f"   🗑️  删除无效文章: {invalid_count}")
        print(f"   📊 清理比例: {invalid_count/(valid_count+invalid_count)*100:.1f}%")
        
        # 显示清理后的统计
        cursor.execute("SELECT COUNT(*) FROM news_articles")
        remaining_count = cursor.fetchone()[0]
        print(f"   📋 剩余文章总数: {remaining_count}")
        
    except Exception as e:
        print(f"❌ 清理过程中出错: {e}")
        conn.rollback()
    finally:
        conn.close()

def show_sample_articles():
    """显示样本文章内容"""
    print("\n📋 显示当前数据库中的样本文章:")
    print("=" * 60)
    
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, title, content FROM news_articles LIMIT 5")
        articles = cursor.fetchall()
        
        for article_id, title, content in articles:
            print(f"\n📰 文章 ID: {article_id}")
            print(f"   标题: {title}")
            print(f"   内容长度: {len(content) if content else 0}")
            if content:
                clean_content = clean_html_tags(content)
                print(f"   清洗后内容: {clean_content[:100]}...")
                is_valid, reason = check_article_validity(title, content)
                print(f"   有效性: {'✅' if is_valid else '❌'} {reason}")
            print("-" * 40)
    
    finally:
        conn.close()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--show':
        show_sample_articles()
    else:
        cleanup_invalid_articles() 