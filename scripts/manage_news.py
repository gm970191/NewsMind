#!/usr/bin/env python3
"""
NewsMind 新闻管理工具
"""
import sqlite3
import time
import sys
from datetime import datetime

def show_menu():
    """显示主菜单"""
    print("\n" + "=" * 60)
    print("NewsMind 新闻管理工具")
    print("=" * 60)
    print("1. 查看新闻源")
    print("2. 查看文章统计")
    print("3. 爬取最新新闻")
    print("4. 查看最新文章")
    print("5. 清理旧文章")
    print("6. 退出")
    print("=" * 60)

def show_news_sources():
    """查看新闻源"""
    print("\n📰 新闻源列表")
    print("-" * 60)
    
    conn = sqlite3.connect("newsmind.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, name, url, type, category, is_active, created_at
            FROM news_sources 
            ORDER BY id
        """)
        
        sources = cursor.fetchall()
        
        if not sources:
            print("暂无新闻源")
            return
        
        for source in sources:
            status = "✅ 活跃" if source[5] else "❌ 禁用"
            print(f"ID: {source[0]}")
            print(f"名称: {source[1]}")
            print(f"URL: {source[2]}")
            print(f"类型: {source[3]}")
            print(f"分类: {source[4]}")
            print(f"状态: {status}")
            print(f"创建时间: {source[6]}")
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    finally:
        conn.close()

def show_article_stats():
    """查看文章统计"""
    print("\n📊 文章统计")
    print("-" * 60)
    
    conn = sqlite3.connect("newsmind.db")
    cursor = conn.cursor()
    
    try:
        # 总文章数
        cursor.execute("SELECT COUNT(*) FROM news_articles")
        total_articles = cursor.fetchone()[0]
        
        # 已处理文章
        cursor.execute("SELECT COUNT(*) FROM news_articles WHERE is_processed = 1")
        processed_articles = cursor.fetchone()[0]
        
        # 未处理文章
        cursor.execute("SELECT COUNT(*) FROM news_articles WHERE is_processed = 0")
        unprocessed_articles = cursor.fetchone()[0]
        
        # 按分类统计
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM news_articles 
            GROUP BY category 
            ORDER BY count DESC
        """)
        category_stats = cursor.fetchall()
        
        # 按来源统计
        cursor.execute("""
            SELECT source_name, COUNT(*) as count 
            FROM news_articles 
            GROUP BY source_name 
            ORDER BY count DESC
        """)
        source_stats = cursor.fetchall()
        
        print(f"总文章数: {total_articles}")
        print(f"已处理: {processed_articles}")
        print(f"未处理: {unprocessed_articles}")
        
        print(f"\n📈 按分类统计:")
        for category, count in category_stats:
            print(f"  {category}: {count} 篇")
        
        print(f"\n📰 按来源统计:")
        for source, count in source_stats[:10]:  # 显示前10个
            print(f"  {source}: {count} 篇")
            
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    finally:
        conn.close()

def crawl_latest_news():
    """爬取最新新闻"""
    print("\n🚀 开始爬取最新新闻...")
    
    try:
        # 导入并运行爬虫
        import subprocess
        result = subprocess.run([sys.executable, "scripts/simple_news_crawler.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 爬取完成!")
            print(result.stdout)
        else:
            print("❌ 爬取失败!")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ 执行爬虫失败: {e}")

def show_latest_articles():
    """查看最新文章"""
    print("\n📰 最新文章列表")
    print("-" * 60)
    
    conn = sqlite3.connect("newsmind.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, title, source_name, category, publish_time, is_processed
            FROM news_articles 
            ORDER BY created_at DESC
            LIMIT 20
        """)
        
        articles = cursor.fetchall()
        
        if not articles:
            print("暂无文章")
            return
        
        for article in articles:
            processed = "✅" if article[5] else "⏳"
            print(f"{processed} [{article[0]}] {article[1]}")
            print(f"    来源: {article[2]} | 分类: {article[3]} | 时间: {article[4]}")
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    finally:
        conn.close()

def clean_old_articles():
    """清理旧文章"""
    print("\n🧹 清理旧文章")
    print("-" * 60)
    
    conn = sqlite3.connect("newsmind.db")
    cursor = conn.cursor()
    
    try:
        # 统计旧文章
        cursor.execute("""
            SELECT COUNT(*) FROM news_articles 
            WHERE created_at < datetime('now', '-7 days')
        """)
        old_count = cursor.fetchone()[0]
        
        if old_count == 0:
            print("没有需要清理的旧文章")
            return
        
        print(f"找到 {old_count} 篇7天前的旧文章")
        confirm = input("确认删除? (y/N): ")
        
        if confirm.lower() == 'y':
            cursor.execute("""
                DELETE FROM news_articles 
                WHERE created_at < datetime('now', '-7 days')
            """)
            conn.commit()
            print(f"✅ 成功删除 {old_count} 篇旧文章")
        else:
            print("取消删除")
            
    except Exception as e:
        print(f"❌ 清理失败: {e}")
        conn.rollback()
    finally:
        conn.close()

def main():
    """主函数"""
    while True:
        show_menu()
        
        try:
            choice = input("\n请选择操作 (1-6): ").strip()
            
            if choice == '1':
                show_news_sources()
            elif choice == '2':
                show_article_stats()
            elif choice == '3':
                crawl_latest_news()
            elif choice == '4':
                show_latest_articles()
            elif choice == '5':
                clean_old_articles()
            elif choice == '6':
                print("\n👋 再见!")
                break
            else:
                print("❌ 无效选择，请重新输入")
                
        except KeyboardInterrupt:
            print("\n\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 操作失败: {e}")
        
        input("\n按回车键继续...")

if __name__ == "__main__":
    main() 