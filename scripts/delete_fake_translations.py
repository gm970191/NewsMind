#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import re

def is_real_chinese_translation(text):
    """检查是否为真正的中文翻译"""
    if not text:
        return False
    
    # 检查是否以语言标记开头
    language_patterns = [
        r'^\[EN\]', r'^\[DE\]', r'^\[FR\]', r'^\[IT\]', r'^\[ES\]', 
        r'^\[PT\]', r'^\[RU\]', r'^\[JA\]', r'^\[KO\]', r'^\[ZH\]'
    ]
    
    for pattern in language_patterns:
        if re.match(pattern, text.strip()):
            return False
    
    # 检查是否包含中文字符
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    return len(chinese_chars) > 0

def delete_fake_translations():
    """删除伪翻译的文章"""
    
    # 连接数据库
    conn = sqlite3.connect('backend/newsmind.db')
    cursor = conn.cursor()
    
    try:
        print("=== 伪翻译文章清理 ===")
        
        # 统计信息
        cursor.execute("SELECT COUNT(*) FROM news_articles")
        total_articles = cursor.fetchone()[0]
        print(f"总文章数: {total_articles}")
        
        # 查找伪翻译的文章
        cursor.execute("""
            SELECT id, original_title, translated_title, translated_content 
            FROM news_articles 
            WHERE translated_title IS NOT NULL AND translated_title != ''
        """)
        
        articles_with_translation = cursor.fetchall()
        
        fake_translations = []
        real_translations = []
        
        for article in articles_with_translation:
            article_id, original_title, translated_title, translated_content = article
            
            # 检查标题是否为真正的中文翻译
            if is_real_chinese_translation(translated_title):
                real_translations.append(article_id)
            else:
                fake_translations.append(article_id)
                print(f"发现伪翻译文章 ID: {article_id}, 标题: {translated_title[:50]}...")
        
        print(f"\n=== 统计结果 ===")
        print(f"真正的中文翻译文章数: {len(real_translations)}")
        print(f"伪翻译文章数: {len(fake_translations)}")
        
        if not fake_translations:
            print("没有找到伪翻译的文章")
            return
        
        # 显示伪翻译文章详情
        print(f"\n=== 伪翻译文章列表 ===")
        cursor.execute("""
            SELECT id, original_title, translated_title, created_at 
            FROM news_articles 
            WHERE id IN ({})
            ORDER BY created_at DESC
        """.format(','.join(map(str, fake_translations))))
        
        fake_articles = cursor.fetchall()
        
        for article in fake_articles:
            article_id, original_title, translated_title, created_at = article
            print(f"ID: {article_id}, 原文标题: {original_title[:50]}..., 伪翻译: {translated_title[:50]}...")
        
        # 确认删除
        print(f"\n=== 删除确认 ===")
        confirm = input(f"确定要删除这 {len(fake_translations)} 篇伪翻译的文章吗？(y/N): ")
        
        if confirm.lower() == 'y':
            # 删除伪翻译的文章
            print("正在删除伪翻译的文章...")
            
            # 先删除相关的processed_content记录
            cursor.execute("""
                DELETE FROM processed_content 
                WHERE article_id IN ({})
            """.format(','.join(map(str, fake_translations))))
            processed_deleted = cursor.rowcount
            print(f"删除了 {processed_deleted} 条相关的processed_content记录")
            
            # 删除伪翻译的文章
            cursor.execute("""
                DELETE FROM news_articles 
                WHERE id IN ({})
            """.format(','.join(map(str, fake_translations))))
            articles_deleted = cursor.rowcount
            
            conn.commit()
            
            print(f"成功删除了 {articles_deleted} 篇伪翻译的文章")
            
            # 显示删除后的统计
            cursor.execute("SELECT COUNT(*) FROM news_articles")
            remaining_articles = cursor.fetchone()[0]
            print(f"删除后剩余文章数: {remaining_articles}")
            
            # 验证剩余文章都是真正的中文翻译
            cursor.execute("""
                SELECT id, translated_title 
                FROM news_articles 
                WHERE translated_title IS NOT NULL AND translated_title != ''
            """)
            
            remaining_translations = cursor.fetchall()
            real_count = 0
            
            for article in remaining_translations:
                article_id, translated_title = article
                if is_real_chinese_translation(translated_title):
                    real_count += 1
                else:
                    print(f"警告：文章 {article_id} 仍为伪翻译: {translated_title[:50]}...")
            
            print(f"剩余文章中真正的中文翻译数: {real_count}")
            
        else:
            print("取消删除操作")
        
    except Exception as e:
        print(f"操作失败: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        
    finally:
        conn.close()

if __name__ == "__main__":
    delete_fake_translations() 