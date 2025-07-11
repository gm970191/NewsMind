#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import re

def is_real_chinese_translation(text):
    """检查是否为真正的中文翻译（不包含日语、韩语等其他语言）"""
    if not text:
        return False
    
    # 检查是否以语言标记开头
    language_patterns = [
        r'^\[EN\]', r'^\[DE\]', r'^\[FR\]', r'^\[IT\]', r'^\[ES\]', 
        r'^\[PT\]', r'^\[RU\]', r'^\[JA\]', r'^\[KO\]', r'^\[ZH\]',
        r'^\[日语\]', r'^\[韩语\]', r'^\[俄语\]', r'^\[法语\]', r'^\[德语\]'
    ]
    
    for pattern in language_patterns:
        if re.match(pattern, text.strip()):
            return False
    
    # 检查是否包含中文字符
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    
    # 检查是否包含日语假名
    japanese_chars = re.findall(r'[\u3040-\u309f\u30a0-\u30ff]', text)
    
    # 检查是否包含韩语字符
    korean_chars = re.findall(r'[\uac00-\ud7af]', text)
    
    # 检查是否包含俄语字符
    russian_chars = re.findall(r'[\u0400-\u04ff]', text)
    
    # 必须是中文且不包含其他语言字符
    return len(chinese_chars) > 0 and len(japanese_chars) == 0 and len(korean_chars) == 0 and len(russian_chars) == 0

def final_cleanup_chinese_only():
    """最终清理，只保留真正的中文翻译文章"""
    
    # 连接数据库
    conn = sqlite3.connect('backend/newsmind.db')
    cursor = conn.cursor()
    
    try:
        print("=== 最终清理：只保留中文翻译文章 ===")
        
        # 统计信息
        cursor.execute("SELECT COUNT(*) FROM news_articles")
        total_articles = cursor.fetchone()[0]
        print(f"当前总文章数: {total_articles}")
        
        # 检查所有文章
        cursor.execute("""
            SELECT id, original_title, translated_title, translated_content 
            FROM news_articles 
            ORDER BY id
        """)
        
        all_articles = cursor.fetchall()
        
        chinese_articles = []
        non_chinese_articles = []
        
        for article in all_articles:
            article_id, original_title, translated_title, translated_content = article
            
            # 检查标题是否为真正的中文翻译
            if is_real_chinese_translation(translated_title):
                chinese_articles.append(article_id)
                print(f"✓ 中文文章 ID: {article_id}, 标题: {translated_title[:50]}...")
            else:
                non_chinese_articles.append(article_id)
                print(f"✗ 非中文文章 ID: {article_id}, 标题: {translated_title[:50]}...")
        
        print(f"\n=== 统计结果 ===")
        print(f"真正的中文翻译文章数: {len(chinese_articles)}")
        print(f"非中文文章数: {len(non_chinese_articles)}")
        
        if not non_chinese_articles:
            print("所有文章都是中文翻译，无需清理")
            return
        
        # 自动删除非中文文章
        print(f"\n=== 开始删除操作 ===")
        print(f"正在删除 {len(non_chinese_articles)} 篇非中文文章...")
        
        # 先删除相关的processed_content记录
        cursor.execute("""
            DELETE FROM processed_content 
            WHERE article_id IN ({})
        """.format(','.join(map(str, non_chinese_articles))))
        processed_deleted = cursor.rowcount
        print(f"删除了 {processed_deleted} 条相关的processed_content记录")
        
        # 删除非中文文章
        cursor.execute("""
            DELETE FROM news_articles 
            WHERE id IN ({})
        """.format(','.join(map(str, non_chinese_articles))))
        articles_deleted = cursor.rowcount
        
        conn.commit()
        
        print(f"成功删除了 {articles_deleted} 篇非中文文章")
        
        # 显示删除后的统计
        cursor.execute("SELECT COUNT(*) FROM news_articles")
        remaining_articles = cursor.fetchone()[0]
        print(f"删除后剩余文章数: {remaining_articles}")
        
        # 显示剩余文章
        print(f"\n=== 剩余中文文章 ===")
        cursor.execute("""
            SELECT id, translated_title 
            FROM news_articles 
            ORDER BY id
        """)
        
        remaining_articles = cursor.fetchall()
        
        for article in remaining_articles:
            article_id, translated_title = article
            print(f"ID: {article_id}, 中文标题: {translated_title}")
        
        print("\n=== 清理完成 ===")
        
    except Exception as e:
        print(f"操作失败: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        
    finally:
        conn.close()

if __name__ == "__main__":
    final_cleanup_chinese_only() 