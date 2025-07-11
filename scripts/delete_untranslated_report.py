#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime

def generate_delete_report():
    """生成删除操作的总结报告"""
    
    # 连接数据库
    conn = sqlite3.connect('backend/newsmind.db')
    cursor = conn.cursor()
    
    try:
        print("=" * 60)
        print("新闻翻译清理操作总结报告")
        print("=" * 60)
        print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 当前状态统计
        print("【当前数据库状态】")
        
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
        
        # 翻译完成率
        translation_rate = (articles_with_title / total_articles * 100) if total_articles > 0 else 0
        print(f"翻译完成率: {translation_rate:.1f}%")
        
        print()
        print("【操作结果】")
        if articles_no_translation == 0:
            print("✓ 所有文章都已翻译完成")
            print("✓ 没有需要删除的文章")
        else:
            print(f"⚠ 仍有 {articles_no_translation} 篇文章没有翻译")
        
        # 检查processed_content表
        print()
        print("【AI处理状态】")
        cursor.execute("SELECT COUNT(*) FROM processed_content")
        processed_count = cursor.fetchone()[0]
        print(f"已AI处理的文章数: {processed_count}")
        
        # 有摘要的文章数
        cursor.execute("SELECT COUNT(*) FROM processed_content WHERE summary_zh IS NOT NULL AND summary_zh != ''")
        articles_with_summary = cursor.fetchone()[0]
        print(f"有中文摘要的文章数: {articles_with_summary}")
        
        print()
        print("【建议】")
        if articles_no_translation == 0:
            print("✓ 数据库清理完成，所有文章都有中文翻译")
            print("✓ 可以正常使用新闻系统")
        else:
            print("⚠ 建议继续翻译剩余的文章")
            print("⚠ 或者考虑删除这些未翻译的文章")
        
        print()
        print("=" * 60)
        
    except Exception as e:
        print(f"生成报告失败: {e}")
        
    finally:
        conn.close()

if __name__ == "__main__":
    generate_delete_report() 