#!/usr/bin/env python3
"""
检查新闻源配置
"""
import sqlite3
import json

def check_news_sources():
    """检查新闻源配置"""
    print("📰 检查新闻源配置...")
    
    # 连接到数据库
    conn = sqlite3.connect("newsmind.db")
    cursor = conn.cursor()
    
    try:
        # 查询所有新闻源
        cursor.execute("""
            SELECT id, name, url, type, category, is_active, created_at
            FROM news_sources 
            ORDER BY id
        """)
        
        sources = cursor.fetchall()
        
        print(f"\n📊 找到 {len(sources)} 个新闻源:")
        print("-" * 80)
        
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
        
        # 查询文章统计
        cursor.execute("SELECT COUNT(*) FROM news_articles")
        total_articles = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM news_articles WHERE is_processed = 1")
        processed_articles = cursor.fetchone()[0]
        
        print(f"\n📈 文章统计:")
        print(f"  总文章数: {total_articles}")
        print(f"  已处理文章: {processed_articles}")
        print(f"  未处理文章: {total_articles - processed_articles}")
        
        return sources
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        return []
    finally:
        conn.close()

def add_real_news_sources():
    """添加真实的新闻源"""
    print("\n🔄 添加真实新闻源...")
    
    # 真实新闻源配置
    real_sources = [
        {
            'name': '新浪新闻',
            'url': 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2509&k=&num=50&page=1&r=' + str(int(time.time())),
            'type': 'api',
            'category': '综合',
            'is_active': 1
        },
        {
            'name': '腾讯新闻',
            'url': 'https://rss.qq.com/news.xml',
            'type': 'rss',
            'category': '综合',
            'is_active': 1
        },
        {
            'name': '网易新闻',
            'url': 'https://feed.m.163.com/nc/rss/T1348647853363.xml',
            'type': 'rss',
            'category': '综合',
            'is_active': 1
        },
        {
            'name': '凤凰网',
            'url': 'https://feed.ifeng.com/c/8eJx3.xml',
            'type': 'rss',
            'category': '综合',
            'is_active': 1
        },
        {
            'name': '澎湃新闻',
            'url': 'https://www.thepaper.cn/rss.jsp',
            'type': 'rss',
            'category': '综合',
            'is_active': 1
        },
        {
            'name': '36氪',
            'url': 'https://www.36kr.com/feed',
            'type': 'rss',
            'category': '科技',
            'is_active': 1
        },
        {
            'name': '虎嗅网',
            'url': 'https://www.huxiu.com/rss/0.xml',
            'type': 'rss',
            'category': '科技',
            'is_active': 1
        },
        {
            'name': '钛媒体',
            'url': 'https://www.tmtpost.com/rss.xml',
            'type': 'rss',
            'category': '科技',
            'is_active': 1
        }
    ]
    
    conn = sqlite3.connect("newsmind.db")
    cursor = conn.cursor()
    
    try:
        for source in real_sources:
            # 检查是否已存在
            cursor.execute("SELECT id FROM news_sources WHERE name = ?", (source['name'],))
            if cursor.fetchone():
                print(f"  ⚠️  {source['name']} 已存在，跳过")
                continue
            
            # 插入新新闻源
            cursor.execute("""
                INSERT INTO news_sources (name, url, type, category, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """, (
                source['name'],
                source['url'],
                source['type'],
                source['category'],
                source['is_active']
            ))
            print(f"  ✅ 添加 {source['name']}")
        
        conn.commit()
        print(f"\n✅ 成功添加 {len(real_sources)} 个真实新闻源")
        
    except Exception as e:
        print(f"❌ 添加新闻源失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    import time
    
    print("NewsMind 新闻源管理工具")
    print("=" * 50)
    
    # 检查现有新闻源
    sources = check_news_sources()
    
    # 添加真实新闻源
    add_real_news_sources()
    
    print("\n🎉 新闻源配置完成!") 