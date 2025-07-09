#!/usr/bin/env python3
"""
检查日语新闻API
"""
import sqlite3
import json

def check_japanese_articles():
    """检查日语新闻"""
    print("🇯🇵 检查日语新闻...")
    
    conn = sqlite3.connect("newsmind.db")
    cursor = conn.cursor()
    
    try:
        # 查询日语新闻
        cursor.execute("""
            SELECT id, title, source_name, language 
            FROM news_articles 
            WHERE language = 'ja'
            ORDER BY created_at DESC
            LIMIT 5
        """)
        
        articles = cursor.fetchall()
        print(f"\n找到 {len(articles)} 篇日语新闻:")
        print("-" * 60)
        
        for article in articles:
            article_id, title, source, lang = article
            print(f"ID: {article_id}")
            print(f"标题: {title}")
            print(f"来源: {source}")
            print(f"语言: {lang}")
            print("-" * 40)
        
        # 模拟API响应
        print(f"\n📡 模拟API响应:")
        print("-" * 60)
        
        api_articles = []
        for article in articles:
            article_id, title, source, lang = article
            api_articles.append({
                "id": article_id,
                "title": title,
                "source_name": source,
                "language": lang,
                "category": "国际"
            })
        
        api_response = {
            "articles": api_articles,
            "total": len(api_articles)
        }
        
        print(json.dumps(api_response, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    finally:
        conn.close()

def check_all_languages():
    """检查所有语言的文章"""
    print("\n📊 所有语言文章统计:")
    print("-" * 40)
    
    conn = sqlite3.connect("newsmind.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT language, COUNT(*) as count 
            FROM news_articles 
            GROUP BY language 
            ORDER BY count DESC
        """)
        
        for lang, count in cursor.fetchall():
            lang_emoji = {
                'en': '🇺🇸',
                'ja': '🇯🇵', 
                'ko': '🇰🇷',
                'zh': '🇨🇳'
            }.get(lang, '🌐')
            print(f"{lang_emoji} {lang}: {count} 篇")
            
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    finally:
        conn.close()

def main():
    """主函数"""
    print("NewsMind 日语新闻API检查工具")
    print("=" * 60)
    
    check_japanese_articles()
    check_all_languages()

if __name__ == "__main__":
    main() 