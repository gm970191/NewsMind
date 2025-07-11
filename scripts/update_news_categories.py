#!/usr/bin/env python3
"""
更新新闻分类 - 重新分类为科技、财经、军事、政治、国际、其他
"""
import sqlite3

def update_news_categories():
    """更新新闻分类"""
    print("🔄 重新分类新闻源...")
    
    conn = sqlite3.connect("newsmind.db")
    cursor = conn.cursor()
    
    # 新闻源分类映射
    category_mapping = {
        # 科技类
        '科技': [
            'TechCrunch', '36氪', '虎嗅网', '钛媒体', 'Ars Technica', 'Wired'
        ],
        # 财经类
        '财经': [
            'Bloomberg', '日本经济新闻', '韩国经济日报'
        ],
        # 军事类
        '军事': [
            # 暂时为空，后续可添加军事新闻源
        ],
        # 政治类
        '政治': [
            # 暂时为空，后续可添加政治新闻源
        ],
        # 国际类
        '国际': [
            'CNN', 'BBC News', 'Reuters', 'The Guardian', 'The New York Times', 
            'NPR News', 'Google News', 'BBC World', 'Al Jazeera', 'France 24', 
            'Deutsche Welle', '朝日新闻', '读卖新闻', '韩国中央日报', 
            '新加坡早报', '海峡时报', '曼谷邮报', '印度时报', '马来西亚星报'
        ],
        # 其他类
        '其他': [
            '新浪新闻', '腾讯新闻', '网易新闻', '凤凰网', '澎湃新闻'
        ]
    }
    
    try:
        updated_count = 0
        
        # 更新新闻源分类
        for category, sources in category_mapping.items():
            for source_name in sources:
                cursor.execute("""
                    UPDATE news_sources 
                    SET category = ? 
                    WHERE name = ?
                """, (category, source_name))
                updated = cursor.rowcount
                if updated > 0:
                    print(f"  ✅ {source_name}: 分类更新为 '{category}'")
                    updated_count += 1
        
        # 更新文章分类
        for category, sources in category_mapping.items():
            for source_name in sources:
                cursor.execute("""
                    UPDATE news_articles 
                    SET category = ? 
                    WHERE source_name = ?
                """, (category, source_name))
                updated = cursor.rowcount
                if updated > 0:
                    print(f"  📰 {source_name}: 更新 {updated} 篇文章分类为 '{category}'")
        
        conn.commit()
        print(f"\n✅ 成功更新 {updated_count} 个新闻源的分类!")
        
        # 显示更新后的统计
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM news_sources 
            WHERE is_active = 1 
            GROUP BY category
            ORDER BY count DESC
        """)
        categories = cursor.fetchall()
        
        print("\n📊 新闻源分类统计:")
        for category, count in categories:
            print(f"  {category}: {count} 个新闻源")
        
        # 显示文章分类统计
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM news_articles 
            GROUP BY category
            ORDER BY count DESC
        """)
        article_categories = cursor.fetchall()
        
        print("\n📰 文章分类统计:")
        for category, count in article_categories:
            print(f"  {category}: {count} 篇文章")
        
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_news_categories() 