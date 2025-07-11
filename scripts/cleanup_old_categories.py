#!/usr/bin/env python3
"""
清理旧分类 - 将旧的分类归类到"其他"
"""
import sqlite3

def cleanup_old_categories():
    """清理旧分类"""
    print("🧹 清理旧分类...")
    
    conn = sqlite3.connect("newsmind.db")
    cursor = conn.cursor()
    
    # 旧分类列表
    old_categories = ['健康', '教育', '文化', '体育']
    
    try:
        updated_count = 0
        
        # 更新文章分类
        for old_category in old_categories:
            cursor.execute("""
                UPDATE news_articles 
                SET category = '其他' 
                WHERE category = ?
            """, (old_category,))
            updated = cursor.rowcount
            if updated > 0:
                print(f"  📰 {old_category}: 更新 {updated} 篇文章分类为 '其他'")
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
        
        print("\n📊 更新后文章分类统计:")
        for category, count in categories:
            print(f"  {category}: {count} 篇文章")
        
    except Exception as e:
        print(f"❌ 清理失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    cleanup_old_categories() 