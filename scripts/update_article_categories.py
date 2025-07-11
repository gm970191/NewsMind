#!/usr/bin/env python3
"""
更新文章分类 - 将现有文章的分类与新闻源分类保持一致
"""
import sqlite3

def update_article_categories():
    """更新文章分类"""
    print("🔄 更新文章分类...")
    
    conn = sqlite3.connect("newsmind.db")
    cursor = conn.cursor()
    
    try:
        # 获取所有新闻源及其分类
        cursor.execute("""
            SELECT name, category 
            FROM news_sources 
            WHERE is_active = 1
        """)
        sources = cursor.fetchall()
        
        source_categories = {name: category for name, category in sources}
        
        print(f"📊 找到 {len(sources)} 个活跃新闻源")
        
        # 更新文章分类
        updated_count = 0
        for source_name, category in sources:
            cursor.execute("""
                UPDATE news_articles 
                SET category = ? 
                WHERE source_name = ? AND category != ?
            """, (category, source_name, category))
            updated = cursor.rowcount
            if updated > 0:
                print(f"  ✅ {source_name}: 更新 {updated} 篇文章分类为 '{category}'")
                updated_count += updated
        
        conn.commit()
        print(f"\n✅ 成功更新 {updated_count} 篇文章的分类!")
        
        # 显示更新后的统计
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM news_articles 
            GROUP BY category
            ORDER BY count DESC
        """)
        categories = cursor.fetchall()
        
        print("\n📰 更新后文章分类统计:")
        for category, count in categories:
            print(f"  {category}: {count} 篇文章")
        
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_article_categories() 