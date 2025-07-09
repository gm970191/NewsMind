#!/usr/bin/env python3
"""
修复日语新闻语言标记
"""
import sqlite3

def fix_japanese_language():
    """修复日语新闻的语言标记"""
    print("🔧 修复日语新闻语言标记...")
    
    conn = sqlite3.connect("newsmind.db")
    cursor = conn.cursor()
    
    try:
        # 修复朝日新闻的语言标记
        cursor.execute("""
            UPDATE news_articles 
            SET language = 'ja' 
            WHERE source_name = '朝日新闻' AND language = 'en'
        """)
        updated = cursor.rowcount
        if updated > 0:
            print(f"  ✅ 朝日新闻: 修复 {updated} 篇文章为日语")
        
        # 修复读卖新闻的语言标记
        cursor.execute("""
            UPDATE news_articles 
            SET language = 'ja' 
            WHERE source_name = '读卖新闻' AND language = 'en'
        """)
        updated = cursor.rowcount
        if updated > 0:
            print(f"  ✅ 读卖新闻: 修复 {updated} 篇文章为日语")
        
        # 修复日本经济新闻的语言标记
        cursor.execute("""
            UPDATE news_articles 
            SET language = 'ja' 
            WHERE source_name = '日本经济新闻' AND language = 'en'
        """)
        updated = cursor.rowcount
        if updated > 0:
            print(f"  ✅ 日本经济新闻: 修复 {updated} 篇文章为日语")
        
        conn.commit()
        print("\n✅ 日语新闻语言标记修复完成!")
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        conn.rollback()
    finally:
        conn.close()

def show_japanese_articles():
    """显示日语新闻"""
    print("\n🇯🇵 日语新闻:")
    print("-" * 60)
    
    conn = sqlite3.connect("newsmind.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT title, source_name, language 
            FROM news_articles 
            WHERE language = 'ja'
            ORDER BY created_at DESC
            LIMIT 10
        """)
        
        articles = cursor.fetchall()
        if articles:
            for title, source, lang in articles:
                print(f"🇯🇵 [{source}] {title}")
        else:
            print("暂无日语新闻")
            
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    finally:
        conn.close()

def show_language_stats():
    """显示语言统计"""
    print("\n📊 语言分布统计:")
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
    print("NewsMind 日语新闻语言修复工具")
    print("=" * 60)
    
    # 修复日语新闻语言标记
    fix_japanese_language()
    
    # 显示语言统计
    show_language_stats()
    
    # 显示日语新闻
    show_japanese_articles()

if __name__ == "__main__":
    main() 