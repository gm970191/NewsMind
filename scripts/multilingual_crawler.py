#!/usr/bin/env python3
"""
多语言新闻爬虫 - 支持英语、日语、韩语、中文等
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

def detect_language_advanced(title, content, source_name):
    """高级语言检测"""
    # 基于新闻源名称的语言映射
    language_mapping = {
        # 英语新闻源
        'en': ['CNN', 'BBC News', 'Reuters', 'TechCrunch', 'Bloomberg', 
               'The Guardian', 'The New York Times', 'NPR News', 'Ars Technica', 'Wired',
               'Google News', 'BBC World', 'Al Jazeera', 'France 24', 'Deutsche Welle',
               '海峡时报', '曼谷邮报', '印度时报', '马来西亚星报'],
        
        # 日语新闻源
        'ja': ['朝日新闻', '读卖新闻', '日本经济新闻'],
        
        # 韩语新闻源
        'ko': ['韩国中央日报', '韩国经济日报'],
        
        # 中文新闻源
        'zh': ['新浪新闻', '腾讯新闻', '网易新闻', '凤凰网', '澎湃新闻', '36氪', '虎嗅网', '钛媒体', '新加坡早报']
    }
    
    # 首先基于新闻源名称判断
    for lang, sources in language_mapping.items():
        if source_name in sources:
            return lang
    
    # 基于内容特征判断
    text = (title + " " + content).lower()
    
    # 日语特征
    japanese_chars = re.findall(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf]', text)
    if len(japanese_chars) > len(text) * 0.1:
        return 'ja'
    
    # 韩语特征
    korean_chars = re.findall(r'[\uac00-\ud7af]', text)
    if len(korean_chars) > len(text) * 0.1:
        return 'ko'
    
    # 中文特征
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    if len(chinese_chars) > len(text) * 0.3:
        return 'zh'
    
    # 默认英语
    return 'en'

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
                # 高级语言检测
                language = detect_language_advanced(title, description, source_name)
                
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

def crawl_multilingual_news():
    """爬取多语言新闻"""
    print("🚀 开始爬取多语言新闻...")
    print("=" * 60)
    
    sources = get_news_sources()
    total_new_articles = 0
    language_stats = {'en': 0, 'ja': 0, 'ko': 0, 'zh': 0}
    
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
                    
                    # 统计语言分布
                    for article in articles:
                        lang = article['language']
                        if lang in language_stats:
                            language_stats[lang] += 1
                    
                    print(f"   ✅ 成功保存 {saved_count} 篇新文章")
                    total_new_articles += saved_count
                else:
                    print(f"   ❌ 获取内容失败")
            else:
                print(f"   ⚠️  暂不支持 {source_type} 类型")
                
        except Exception as e:
            print(f"   ❌ 爬取失败: {e}")
    
    return total_new_articles, language_stats

def main():
    """主函数"""
    print("NewsMind 多语言新闻爬虫")
    print("=" * 60)
    
    # 开始爬取
    start_time = time.time()
    new_articles, language_stats = crawl_multilingual_news()
    end_time = time.time()
    
    print("\n" + "=" * 60)
    print("📊 爬取结果")
    print("=" * 60)
    print(f"新增文章: {new_articles}")
    print(f"耗时: {end_time - start_time:.2f} 秒")
    
    print(f"\n🌍 语言分布:")
    print(f"  英语 (en): {language_stats['en']} 篇")
    print(f"  日语 (ja): {language_stats['ja']} 篇")
    print(f"  韩语 (ko): {language_stats['ko']} 篇")
    print(f"  中文 (zh): {language_stats['zh']} 篇")
    
    if new_articles > 0:
        print(f"\n🎉 成功获取 {new_articles} 篇多语言新闻!")
        print("📍 现在可以测试大模型的总结与翻译能力:")
        print("   - 英语新闻翻译为中文")
        print("   - 日语新闻翻译为中文")
        print("   - 韩语新闻翻译为中文")
        print("   - 多语言新闻智能总结")
    else:
        print(f"\n⚠️  未获取到新文章")

if __name__ == "__main__":
    main() 