#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json

def check_article_122_translation():
    """检查文章122的翻译原文与正文总结"""
    
    # 连接数据库
    conn = sqlite3.connect('backend/newsmind.db')
    cursor = conn.cursor()
    
    try:
        # 查询文章122的详细信息
        cursor.execute("""
            SELECT 
                id,
                original_title,
                translated_title,
                original_content,
                translated_content,
                summary_zh,
                detailed_summary_zh,
                original_language,
                is_title_translated,
                is_content_translated
            FROM news_articles 
            WHERE id = 122
        """)
        
        result = cursor.fetchone()
        
        if result:
            (id, original_title, translated_title, original_content, 
             translated_content, summary_zh, detailed_summary_zh, 
             original_language, is_title_translated, is_content_translated) = result
            
            print("=" * 80)
            print("文章122 - 翻译原文与正文总结检查")
            print("=" * 80)
            
            print(f"\n【基本信息】")
            print(f"文章ID: {id}")
            print(f"原文语言: {original_language}")
            print(f"标题已翻译: {'是' if is_title_translated else '否'}")
            print(f"正文已翻译: {'是' if is_content_translated else '否'}")
            
            print(f"\n【原文标题】")
            print(f"{original_title}")
            
            print(f"\n【翻译标题】")
            print(f"{translated_title}")
            
            print(f"\n【原文内容】")
            print(f"{original_content[:500]}...")
            if len(original_content) > 500:
                print(f"(内容长度: {len(original_content)} 字符)")
            
            print(f"\n【翻译内容】")
            if translated_content:
                print(f"{translated_content[:500]}...")
                if len(translated_content) > 500:
                    print(f"(内容长度: {len(translated_content)} 字符)")
            else:
                print("(未翻译)")
            
            print(f"\n【中文摘要】")
            if summary_zh:
                print(f"{summary_zh}")
            else:
                print("(无摘要)")
            
            print(f"\n【详细摘要】")
            if detailed_summary_zh:
                print(f"{detailed_summary_zh}")
            else:
                print("(无详细摘要)")
            
            print("\n" + "=" * 80)
            
            # 分析翻译质量
            print("\n【翻译质量分析】")
            
            if is_title_translated and translated_title:
                print("✓ 标题已翻译")
            else:
                print("✗ 标题未翻译")
            
            if is_content_translated and translated_content:
                print("✓ 正文已翻译")
            else:
                print("✗ 正文未翻译")
            
            if summary_zh:
                print("✓ 有中文摘要")
            else:
                print("✗ 无中文摘要")
            
            if detailed_summary_zh:
                print("✓ 有详细摘要")
            else:
                print("✗ 无详细摘要")
            
            # 检查内容是否损坏
            if original_content and len(original_content) < 100:
                print("⚠ 原文内容可能损坏或过短")
            
            if translated_content and len(translated_content) < 100:
                print("⚠ 翻译内容可能损坏或过短")
            
        else:
            print("未找到文章122")
            
    except Exception as e:
        print(f"查询出错: {e}")
        
    finally:
        conn.close()

if __name__ == "__main__":
    check_article_122_translation() 