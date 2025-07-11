#!/usr/bin/env python3
import sqlite3

def check_article_59():
    """检查文章59"""
    try:
        conn = sqlite3.connect('backend/newsmind.db')
        cursor = conn.cursor()
        
        # 检查文章59
        cursor.execute('SELECT title, content, language FROM news_articles WHERE id = 59')
        result = cursor.fetchone()
        
        if result:
            title, content, language = result
            print("📰 文章59:")
            print(f"标题: {title}")
            print(f"语言: {language}")
            print(f"内容长度: {len(content)}")
            print(f"内容前200字: {content[:200]}...")
            
            # 检查AI处理结果
            cursor.execute('SELECT summary_zh, summary_en, translation_zh FROM processed_content WHERE article_id = 59')
            processed = cursor.fetchone()
            
            if processed:
                summary_zh, summary_en, translation_zh = processed
                print(f"\n🤖 AI处理结果:")
                print(f"中文摘要: {'有' if summary_zh else '无'}")
                print(f"英文摘要: {'有' if summary_en else '无'}")
                print(f"中文翻译: {'有' if translation_zh else '无'}")
            else:
                print("\n❌ 无AI处理记录")
        else:
            print("❌ 文章59不存在")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")

if __name__ == "__main__":
    check_article_59() 