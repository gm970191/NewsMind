#!/usr/bin/env python3
"""
检查AI处理后的文章
"""
import sqlite3

def check_processed_articles():
    """检查AI处理后的文章"""
    print("📊 检查AI处理后的文章...")
    print("=" * 60)
    
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        # 统计处理情况
        cursor.execute("SELECT COUNT(*) FROM news_articles WHERE is_processed = 1")
        processed_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM news_articles WHERE is_processed = 0")
        unprocessed_count = cursor.fetchone()[0]
        
        print(f"📈 处理统计:")
        print(f"   已处理文章: {processed_count} 篇")
        print(f"   未处理文章: {unprocessed_count} 篇")
        print(f"   处理率: {processed_count/(processed_count+unprocessed_count)*100:.1f}%")
        
        # 获取最新的已处理文章
        cursor.execute("""
            SELECT na.id, na.title, na.language, na.source_name, 
                   pc.summary_zh, pc.translation_zh, pc.processing_time
            FROM news_articles na
            JOIN processed_content pc ON na.id = pc.article_id
            ORDER BY na.created_at DESC
            LIMIT 5
        """)
        
        articles = cursor.fetchall()
        
        print(f"\n📰 最新已处理文章:")
        for article in articles:
            article_id, title, language, source_name, summary_zh, translation_zh, processing_time = article
            
            print(f"\n   📝 文章ID: {article_id}")
            print(f"      标题: {title[:50]}...")
            print(f"      语言: {language}")
            print(f"      来源: {source_name}")
            print(f"      处理时间: {processing_time:.1f}秒")
            
            if summary_zh:
                print(f"      中文摘要: {summary_zh[:100]}...")
            else:
                print(f"      中文摘要: 无")
                
            if translation_zh:
                print(f"      中文翻译: {translation_zh[:100]}...")
            else:
                print(f"      中文翻译: 无")
        
        # 按语言统计
        cursor.execute("""
            SELECT na.language, COUNT(*) as count
            FROM news_articles na
            JOIN processed_content pc ON na.id = pc.article_id
            GROUP BY na.language
            ORDER BY count DESC
        """)
        
        language_stats = cursor.fetchall()
        
        print(f"\n🌍 按语言统计:")
        for language, count in language_stats:
            print(f"   {language}: {count} 篇")
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_processed_articles() 