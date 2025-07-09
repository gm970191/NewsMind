#!/usr/bin/env python3
"""
添加国际新闻源 - 支持多语言新闻
"""
import sqlite3
import time
from datetime import datetime

def add_international_sources():
    """添加国际新闻源"""
    print("🌍 添加国际新闻源...")
    
    international_sources = [
        # 英语新闻源
        {
            'name': 'Google News',
            'url': 'https://news.google.com/rss',
            'type': 'rss',
            'category': '国际',
            'is_active': 1
        },
        {
            'name': 'BBC World',
            'url': 'http://feeds.bbci.co.uk/news/world/rss.xml',
            'type': 'rss',
            'category': '国际',
            'is_active': 1
        },
        {
            'name': 'Al Jazeera',
            'url': 'https://www.aljazeera.com/xml/rss/all.xml',
            'type': 'rss',
            'category': '国际',
            'is_active': 1
        },
        {
            'name': 'France 24',
            'url': 'https://www.france24.com/en/rss',
            'type': 'rss',
            'category': '国际',
            'is_active': 1
        },
        {
            'name': 'Deutsche Welle',
            'url': 'https://rss.dw.com/xml/rss-de-all',
            'type': 'rss',
            'category': '国际',
            'is_active': 1
        },
        
        # 日语新闻源
        {
            'name': '朝日新闻',
            'url': 'https://rss.asahi.com/rss/asahi/newsheadlines.rdf',
            'type': 'rss',
            'category': '国际',
            'is_active': 1
        },
        {
            'name': '读卖新闻',
            'url': 'https://www.yomiuri.co.jp/rss/feed/',
            'type': 'rss',
            'category': '国际',
            'is_active': 1
        },
        {
            'name': '日本经济新闻',
            'url': 'https://www.nikkei.com/rss/feed/nikkei/news.xml',
            'type': 'rss',
            'category': '财经',
            'is_active': 1
        },
        
        # 韩语新闻源
        {
            'name': '韩国中央日报',
            'url': 'https://www.joongang.co.kr/rss/rss.xml',
            'type': 'rss',
            'category': '国际',
            'is_active': 1
        },
        {
            'name': '韩国经济日报',
            'url': 'https://www.hankyung.com/rss',
            'type': 'rss',
            'category': '财经',
            'is_active': 1
        },
        
        # 新加坡新闻源
        {
            'name': '新加坡早报',
            'url': 'https://www.zaobao.com.sg/realtime/world',
            'type': 'web',
            'category': '国际',
            'is_active': 1
        },
        {
            'name': '海峡时报',
            'url': 'https://www.straitstimes.com/news/world/rss.xml',
            'type': 'rss',
            'category': '国际',
            'is_active': 1
        },
        
        # 其他亚洲新闻源
        {
            'name': '曼谷邮报',
            'url': 'https://www.bangkokpost.com/rss/data/world.xml',
            'type': 'rss',
            'category': '国际',
            'is_active': 1
        },
        {
            'name': '印度时报',
            'url': 'https://timesofindia.indiatimes.com/rssfeedstopstories.cms',
            'type': 'rss',
            'category': '国际',
            'is_active': 1
        },
        {
            'name': '马来西亚星报',
            'url': 'https://www.thestar.com.my/rss/World/',
            'type': 'rss',
            'category': '国际',
            'is_active': 1
        }
    ]
    
    conn = sqlite3.connect("newsmind.db")
    cursor = conn.cursor()
    
    added_count = 0
    
    try:
        for source in international_sources:
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
            print(f"  ✅ 添加 {source['name']} ({source['type']})")
            added_count += 1
        
        conn.commit()
        print(f"\n✅ 成功添加 {added_count} 个国际新闻源")
        
    except Exception as e:
        print(f"❌ 添加新闻源失败: {e}")
        conn.rollback()
    finally:
        conn.close()
    
    return added_count

def show_language_distribution():
    """显示语言分布"""
    print("\n📊 新闻源语言分布:")
    print("-" * 50)
    
    language_sources = {
        '英语': ['CNN', 'BBC News', 'Reuters', 'TechCrunch', 'Bloomberg', 
                'The Guardian', 'The New York Times', 'NPR News', 'Ars Technica', 'Wired',
                'Google News', 'BBC World', 'Al Jazeera', 'France 24', 'Deutsche Welle',
                '海峡时报', '曼谷邮报', '印度时报', '马来西亚星报'],
        '日语': ['朝日新闻', '读卖新闻', '日本经济新闻'],
        '韩语': ['韩国中央日报', '韩国经济日报'],
        '中文': ['新浪新闻', '腾讯新闻', '网易新闻', '凤凰网', '澎湃新闻', '36氪', '虎嗅网', '钛媒体', '新加坡早报']
    }
    
    for language, sources in language_sources.items():
        print(f"{language}: {len(sources)} 个新闻源")
        for source in sources:
            print(f"  - {source}")

def main():
    """主函数"""
    print("NewsMind 国际新闻源添加工具")
    print("=" * 60)
    
    # 添加国际新闻源
    added_count = add_international_sources()
    
    # 显示语言分布
    show_language_distribution()
    
    print(f"\n🎉 国际新闻源添加完成!")
    print(f"📝 现在可以测试大模型的总结与翻译能力:")
    print(f"   - 英语新闻翻译为中文")
    print(f"   - 日语新闻翻译为中文")
    print(f"   - 韩语新闻翻译为中文")
    print(f"   - 多语言新闻智能总结")

if __name__ == "__main__":
    main() 