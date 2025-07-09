#!/usr/bin/env python3
"""
修复文章语言标记
"""
import sqlite3

def fix_language_tags():
    """修复文章语言标记"""
    print("🔧 修复文章语言标记...")
    
    conn = sqlite3.connect("newsmind.db")
    cursor = conn.cursor()
    
    # 国外新闻源列表
    foreign_sources = ['CNN', 'BBC News', 'Reuters', 'TechCrunch', 'Bloomberg', 
                      'The Guardian', 'The New York Times', 'NPR News', 'Ars Technica', 'Wired']
    
    # 中文新闻源列表
    chinese_sources = ['新浪新闻', '腾讯新闻', '网易新闻', '凤凰网', '澎湃新闻', '36氪', '虎嗅网', '钛媒体']
    
    try:
        # 修复国外新闻源的语言标记
        for source in foreign_sources:
            cursor.execute("""
                UPDATE news_articles 
                SET language = 'en' 
                WHERE source_name = ? AND language = 'zh'
            """, (source,))
            updated = cursor.rowcount
            if updated > 0:
                print(f"  ✅ {source}: 修复 {updated} 篇文章为英文")
        
        # 修复中文新闻源的语言标记
        for source in chinese_sources:
            cursor.execute("""
                UPDATE news_articles 
                SET language = 'zh' 
                WHERE source_name = ? AND language = 'en'
            """, (source,))
            updated = cursor.rowcount
            if updated > 0:
                print(f"  ✅ {source}: 修复 {updated} 篇文章为中文")
        
        conn.commit()
        print("\n✅ 语言标记修复完成!")
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        conn.rollback()
    finally:
        conn.close()

def show_foreign_articles():
    """显示国外新闻源文章"""
    print("\n🌍 国外新闻源文章:")
    print("-" * 60)
    
    conn = sqlite3.connect("newsmind.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT title, source_name, language 
            FROM news_articles 
            WHERE source_name IN ('CNN', 'BBC News', 'Reuters', 'TechCrunch', 'Bloomberg', 
                                'The Guardian', 'The New York Times', 'NPR News', 'Ars Technica', 'Wired')
            ORDER BY created_at DESC
            LIMIT 20
        """)
        
        articles = cursor.fetchall()
        if articles:
            for title, source, lang in articles:
                lang_emoji = "🇺🇸" if lang == 'en' else "🇨🇳"
                print(f"{lang_emoji} [{source}] {title}")
        else:
            print("暂无国外新闻源文章")
            
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    finally:
        conn.close()

def main():
    """主函数"""
    print("NewsMind 语言标记修复工具")
    print("=" * 60)
    
    # 修复语言标记
    fix_language_tags()
    
    # 显示国外文章
    show_foreign_articles()

if __name__ == "__main__":
    main() 