#!/usr/bin/env python3
"""
更新中国新闻源分类 - 将"综合"分类改为"中国"
"""
import sqlite3

def update_chinese_sources_category():
    """更新中国新闻源的分类"""
    print("🇨🇳 更新中国新闻源分类...")
    
    conn = sqlite3.connect("newsmind.db")
    cursor = conn.cursor()
    
    # 中国新闻源列表
    chinese_sources = [
        '新浪新闻', '腾讯新闻', '网易新闻', '凤凰网', '澎湃新闻'
    ]
    
    try:
        # 更新新闻源分类
        for source_name in chinese_sources:
            cursor.execute("""
                UPDATE news_sources 
                SET category = '中国' 
                WHERE name = ? AND category = '综合'
            """, (source_name,))
            updated = cursor.rowcount
            if updated > 0:
                print(f"  ✅ {source_name}: 分类更新为'中国'")
            else:
                print(f"  ⚠️  {source_name}: 未找到或已更新")
        
        # 更新文章分类
        for source_name in chinese_sources:
            cursor.execute("""
                UPDATE news_articles 
                SET category = '中国' 
                WHERE source_name = ? AND category = '综合'
            """, (source_name,))
            updated = cursor.rowcount
            if updated > 0:
                print(f"  ✅ {source_name}: 更新 {updated} 篇文章分类为'中国'")
        
        conn.commit()
        print("\n✅ 中国新闻源分类更新完成!")
        
        # 显示统计信息
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM news_sources 
            WHERE is_active = 1 
            GROUP BY category
        """)
        categories = cursor.fetchall()
        
        print("\n📊 新闻源分类统计:")
        for category, count in categories:
            print(f"  {category}: {count} 个新闻源")
        
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_chinese_sources_category() 