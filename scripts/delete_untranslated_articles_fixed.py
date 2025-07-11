#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def delete_untranslated_articles():
    """删除没有中文翻译的新闻文章"""
    
    # 连接数据库
    conn = sqlite3.connect('backend/newsmind.db')
    cursor = conn.cursor()
    
    try:
        # 统计信息
        print("=== 新闻翻译状态统计 ===")
        
        # 总文章数
        cursor.execute("SELECT COUNT(*) FROM news_articles")
        total_articles = cursor.fetchone()[0]
        print(f"总文章数: {total_articles}")
        
        # 有翻译标题的文章数
        cursor.execute("SELECT COUNT(*) FROM news_articles WHERE translated_title IS NOT NULL AND translated_title != ''")
        articles_with_title = cursor.fetchone()[0]
        print(f"有翻译标题的文章数: {articles_with_title}")
        
        # 有翻译内容的文章数
        cursor.execute("SELECT COUNT(*) FROM news_articles WHERE translated_content IS NOT NULL AND translated_content != ''")
        articles_with_content = cursor.fetchone()[0]
        print(f"有翻译内容的文章数: {articles_with_content}")
        
        # 完全没有翻译的文章数
        cursor.execute("""
            SELECT COUNT(*) FROM news_articles 
            WHERE (translated_title IS NULL OR translated_title = '') 
            AND (translated_content IS NULL OR translated_content = '')
        """)
        articles_no_translation = cursor.fetchone()[0]
        print(f"完全没有翻译的文章数: {articles_no_translation}")
        
        # 显示没有翻译的文章详情
        print(f"\n=== 没有翻译的文章列表 ===")
        cursor.execute("""
            SELECT id, original_title, source_url, created_at 
            FROM news_articles 
            WHERE (translated_title IS NULL OR translated_title = '') 
            AND (translated_content IS NULL OR translated_content = '')
            ORDER BY created_at DESC
        """)
        
        untranslated_articles = cursor.fetchall()
        
        if untranslated_articles:
            print(f"找到 {len(untranslated_articles)} 篇没有翻译的文章:")
            for article in untranslated_articles:
                article_id, title, url, created_at = article
                # 处理可能为None的字段
                title_display = title[:50] + "..." if title and len(title) > 50 else (title or "无标题")
                created_at_display = created_at or "未知时间"
                print(f"ID: {article_id}, 标题: {title_display}, 创建时间: {created_at_display}")
        else:
            print("没有找到没有翻译的文章")
            return
        
        # 确认是否删除
        print(f"\n=== 删除确认 ===")
        confirm = input(f"确定要删除这 {len(untranslated_articles)} 篇没有翻译的文章吗？(y/N): ")
        
        if confirm.lower() == 'y':
            # 删除没有翻译的文章
            print("正在删除没有翻译的文章...")
            
            # 先删除相关的processed_content记录
            cursor.execute("""
                DELETE FROM processed_content 
                WHERE article_id IN (
                    SELECT id FROM news_articles 
                    WHERE (translated_title IS NULL OR translated_title = '') 
                    AND (translated_content IS NULL OR translated_content = '')
                )
            """)
            processed_deleted = cursor.rowcount
            print(f"删除了 {processed_deleted} 条相关的processed_content记录")
            
            # 删除没有翻译的文章
            cursor.execute("""
                DELETE FROM news_articles 
                WHERE (translated_title IS NULL OR translated_title = '') 
                AND (translated_content IS NULL OR translated_content = '')
            """)
            articles_deleted = cursor.rowcount
            
            conn.commit()
            
            print(f"成功删除了 {articles_deleted} 篇没有翻译的文章")
            
            # 显示删除后的统计
            cursor.execute("SELECT COUNT(*) FROM news_articles")
            remaining_articles = cursor.fetchone()[0]
            print(f"删除后剩余文章数: {remaining_articles}")
            
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
    delete_untranslated_articles() 