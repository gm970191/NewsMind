#!/usr/bin/env python3
"""
改进版新闻爬虫 - 修复语言检测和添加更多国外新闻源
"""
import sqlite3
import time
import json
from datetime import datetime
import urllib.request
import urllib.parse
import re

def get_news_sources():
    """获取所有活跃的新闻源"""
    conn = sqlite3.connect("newsmind.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, name, url, type, category, is_active
            FROM news_sources 
            WHERE is_active = 1
            ORDER BY id
        """)
        sources = cursor.fetchall()
        return sources
    finally:
        conn.close()

def add_more_foreign_sources():
    """添加更多国外新闻源"""
    print("🔄 添加更多国外新闻源...")
    
    new_sources = [
        {
            'name': 'The Guardian',
            'url': 'https://www.theguardian.com/world/rss',
            'type': 'rss',
            'category': '国际',
            'is_active': 1
        },
        {
            'name': 'The New York Times',
            'url': 'https://rss.nytimes.com/services/xml/rss/nyt/World.xml',
            'type': 'rss',
            'category': '国际',
            'is_active': 1
        },
        {
            'name': 'NPR News',
            'url': 'https://feeds.npr.org/1001/rss.xml',
            'type': 'rss',
            'category': '国际',
            'is_active': 1
        },
        {
            'name': 'Ars Technica',
            'url': 'https://feeds.arstechnica.com/arstechnica/index',
            'type': 'rss',
            'category': '科技',
            'is_active': 1
        },
        {
            'name': 'Wired',
            'url': 'https://www.wired.com/feed/rss',
            'type': 'rss',
            'category': '科技',
            'is_active': 1
        }
    ]
    
    conn = sqlite3.connect("newsmind.db")
    cursor = conn.cursor()
    
    try:
        for source in new_sources:
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
        print(f"\n✅ 成功添加 {len(new_sources)} 个国外新闻源")
        
    except Exception as e:
        print(f"❌ 添加新闻源失败: {e}")
        conn.rollback()
    finally:
        conn.close()

def fetch_url_content(url):
    """获取URL内容"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"     ❌ 获取内容失败: {e}")
        return None

def parse_rss_content(content, source_name):
    """解析RSS内容"""
    articles = []
    
    # 简单的RSS解析
    title_pattern = r'<title>(.*?)</title>'
    link_pattern = r'<link>(.*?)</link>'
    description_pattern = r'<description>(.*?)</description>'
    
    titles = re.findall(title_pattern, content, re.DOTALL)
    links = re.findall(link_pattern, content, re.DOTALL)
    descriptions = re.findall(description_pattern, content, re.DOTALL)
    
    # 过滤掉RSS feed本身的标题
    if titles and 'rss' in titles[0].lower():
        titles = titles[1:]
    
    for i in range(min(len(titles), len(links), 10)):  # 最多10篇
        try:
            title = re.sub(r'<[^>]+>', '', titles[i]).strip()
            link = links[i].strip()
            description = re.sub(r'<[^>]+>', '', descriptions[i]).strip() if i < len(descriptions) else ""
            
            if title and link and not title.startswith('http'):
                # 改进的语言检测
                language = detect_language_improved(title, description, source_name)
                
                articles.append({
                    'title': title,
                    'content': description,
                    'source_url': link,
                    'publish_time': datetime.now(),
                    'language': language
                })
        except Exception as e:
            continue
    
    return articles

def detect_language_improved(title, content, source_name):
    """改进的语言检测"""
    # 国外新闻源默认英文
    foreign_sources = ['CNN', 'BBC News', 'Reuters', 'TechCrunch', 'Bloomberg', 
                      'The Guardian', 'The New York Times', 'NPR News', 'Ars Technica', 'Wired']
    
    if source_name in foreign_sources:
        return 'en'
    
    # 中文新闻源默认中文
    chinese_sources = ['新浪新闻', '腾讯新闻', '网易新闻', '凤凰网', '澎湃新闻', '36氪', '虎嗅网', '钛媒体']
    if source_name in chinese_sources:
        return 'zh'
    
    # 基于内容检测
    text = (title + " " + content).lower()
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    english_chars = re.findall(r'[a-zA-Z]', text)
    
    if len(chinese_chars) > len(english_chars):
        return 'zh'
    else:
        return 'en'

def save_articles(articles, source_id, source_name, category):
    """保存文章到数据库"""
    if not articles:
        return 0
    
    conn = sqlite3.connect("newsmind.db")
    cursor = conn.cursor()
    
    saved_count = 0
    
    try:
        for article in articles:
            # 检查是否已存在（基于URL去重）
            cursor.execute("SELECT id FROM news_articles WHERE source_url = ?", (article['source_url'],))
            if cursor.fetchone():
                continue
            
            # 插入新文章
            cursor.execute("""
                INSERT INTO news_articles (
                    title, content, source_name, source_url, category, language,
                    publish_time, created_at, updated_at, is_processed, source_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                article['title'],
                article['content'],
                source_name,
                article['source_url'],
                category,
                article['language'],
                article['publish_time'].isoformat(),
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                0,  # 未处理
                source_id
            ))
            
            saved_count += 1
        
        conn.commit()
        
    except Exception as e:
        print(f"     ❌ 保存文章失败: {e}")
        conn.rollback()
    finally:
        conn.close()
    
    return saved_count

def crawl_news():
    """爬取新闻"""
    print("🚀 开始爬取真实新闻...")
    print("=" * 60)
    
    sources = get_news_sources()
    total_new_articles = 0
    
    for source in sources:
        source_id, name, url, source_type, category, is_active = source
        
        print(f"\n📰 正在爬取: {name}")
        print(f"   URL: {url}")
        
        try:
            if source_type == 'rss':
                content = fetch_url_content(url)
                if content:
                    articles = parse_rss_content(content, name)
                    saved_count = save_articles(articles, source_id, name, category)
                    print(f"   ✅ 成功保存 {saved_count} 篇新文章")
                    total_new_articles += saved_count
                else:
                    print(f"   ❌ 获取内容失败")
            else:
                print(f"   ⚠️  暂不支持 {source_type} 类型")
                
        except Exception as e:
            print(f"   ❌ 爬取失败: {e}")
    
    return total_new_articles

def main():
    """主函数"""
    print("NewsMind 改进版新闻爬虫")
    print("=" * 60)
    
    # 添加更多国外新闻源
    add_more_foreign_sources()
    
    # 开始爬取
    start_time = time.time()
    new_articles = crawl_news()
    end_time = time.time()
    
    print("\n" + "=" * 60)
    print("📊 爬取结果")
    print("=" * 60)
    print(f"新增文章: {new_articles}")
    print(f"耗时: {end_time - start_time:.2f} 秒")
    
    if new_articles > 0:
        print(f"\n🎉 成功获取 {new_articles} 篇新文章!")
        print("📍 现在可以访问前端页面查看最新新闻")
    else:
        print(f"\n⚠️  未获取到新文章")

if __name__ == "__main__":
    main() 