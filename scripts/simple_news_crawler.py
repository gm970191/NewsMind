#!/usr/bin/env python3
"""
简化版新闻爬虫 - 使用系统Python
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

def parse_rss_content(content):
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
                articles.append({
                    'title': title,
                    'content': description,
                    'source_url': link,
                    'publish_time': datetime.now()
                })
        except Exception as e:
            continue
    
    return articles

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
                'zh',
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
                    articles = parse_rss_content(content)
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
    print("NewsMind 简化新闻爬虫")
    print("=" * 60)
    
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