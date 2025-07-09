#!/usr/bin/env python3
"""
真实新闻爬虫 - 支持多种新闻源
"""
import sys
import os
import time
import json
import requests
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urljoin, urlparse
import re

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

try:
    import feedparser
except ImportError:
    print("安装feedparser: pip install feedparser")
    sys.exit(1)

class RealNewsCrawler:
    """真实新闻爬虫"""
    
    def __init__(self):
        self.db_path = "newsmind.db"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.results = {
            'total_sources': 0,
            'success_count': 0,
            'error_count': 0,
            'new_articles': 0,
            'errors': []
        }
    
    def get_news_sources(self):
        """获取所有活跃的新闻源"""
        conn = sqlite3.connect(self.db_path)
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
    
    def crawl_all_sources(self):
        """爬取所有新闻源"""
        sources = self.get_news_sources()
        self.results['total_sources'] = len(sources)
        
        print(f"🚀 开始爬取 {len(sources)} 个新闻源...")
        print("=" * 60)
        
        for source in sources:
            source_id, name, url, source_type, category, is_active = source
            print(f"\n📰 正在爬取: {name} ({source_type})")
            print(f"   URL: {url}")
            
            try:
                if source_type == 'rss':
                    articles = self.crawl_rss_source(source)
                elif source_type == 'api':
                    articles = self.crawl_api_source(source)
                else:
                    print(f"  ⚠️  不支持的源类型: {source_type}")
                    continue
                
                # 保存文章
                saved_count = self.save_articles(articles, source)
                print(f"  ✅ 成功保存 {saved_count} 篇新文章")
                self.results['success_count'] += 1
                
            except Exception as e:
                error_msg = f"爬取 {name} 失败: {str(e)}"
                print(f"  ❌ {error_msg}")
                self.results['error_count'] += 1
                self.results['errors'].append(error_msg)
        
        return self.results
    
    def crawl_rss_source(self, source):
        """爬取RSS源"""
        source_id, name, url, source_type, category, is_active = source
        
        try:
            # 获取RSS内容
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # 解析RSS
            feed = feedparser.parse(response.content)
            articles = []
            
            print(f"   📊 找到 {len(feed.entries)} 篇文章")
            
            for entry in feed.entries[:20]:  # 限制最多20篇
                try:
                    # 提取文章信息
                    title = entry.get('title', '').strip()
                    content = entry.get('summary', '').strip()
                    link = entry.get('link', '')
                    
                    if not title or not link:
                        continue
                    
                    # 解析发布时间
                    publish_time = None
                    if entry.get('published'):
                        try:
                            publish_time = datetime(*entry.published_parsed[:6])
                        except:
                            publish_time = datetime.now()
                    else:
                        publish_time = datetime.now()
                    
                    # 清理内容
                    content = self.clean_content(content)
                    
                    article_data = {
                        'title': title,
                        'content': content,
                        'source_url': link,
                        'source_id': source_id,
                        'source_name': name,
                        'publish_time': publish_time,
                        'category': category,
                        'language': 'zh' if self.is_chinese(title) else 'en'
                    }
                    
                    articles.append(article_data)
                    
                except Exception as e:
                    print(f"     ⚠️  解析文章失败: {e}")
                    continue
            
            return articles
            
        except Exception as e:
            raise Exception(f"RSS解析失败: {e}")
    
    def crawl_api_source(self, source):
        """爬取API源"""
        source_id, name, url, source_type, category, is_active = source
        
        try:
            # 获取API数据
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            # 新浪新闻API格式
            if 'sina' in url.lower():
                if 'result' in data and 'data' in data['result']:
                    items = data['result']['data']
                    print(f"   📊 找到 {len(items)} 篇文章")
                    
                    for item in items[:20]:
                        try:
                            title = item.get('title', '').strip()
                            content = item.get('intro', '').strip()
                            link = item.get('url', '')
                            
                            if not title or not link:
                                continue
                            
                            # 解析发布时间
                            publish_time = datetime.now()
                            if item.get('ctime'):
                                try:
                                    publish_time = datetime.fromtimestamp(int(item['ctime']))
                                except:
                                    pass
                            
                            article_data = {
                                'title': title,
                                'content': content,
                                'source_url': link,
                                'source_id': source_id,
                                'source_name': name,
                                'publish_time': publish_time,
                                'category': category,
                                'language': 'zh'
                            }
                            
                            articles.append(article_data)
                            
                        except Exception as e:
                            print(f"     ⚠️  解析文章失败: {e}")
                            continue
            
            return articles
            
        except Exception as e:
            raise Exception(f"API解析失败: {e}")
    
    def clean_content(self, content):
        """清理内容"""
        if not content:
            return ""
        
        # 移除HTML标签
        content = re.sub(r'<[^>]+>', '', content)
        
        # 移除多余空白
        content = re.sub(r'\s+', ' ', content).strip()
        
        # 限制长度
        if len(content) > 1000:
            content = content[:1000] + "..."
        
        return content
    
    def is_chinese(self, text):
        """判断是否为中文"""
        if not text:
            return False
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        return len(chinese_chars) > len(text) * 0.3
    
    def save_articles(self, articles, source):
        """保存文章到数据库"""
        if not articles:
            return 0
        
        conn = sqlite3.connect(self.db_path)
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
                    article['source_name'],
                    article['source_url'],
                    article['category'],
                    article['language'],
                    article['publish_time'].isoformat(),
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    0,  # 未处理
                    article['source_id']
                ))
                
                saved_count += 1
                self.results['new_articles'] += 1
            
            conn.commit()
            
        except Exception as e:
            print(f"     ❌ 保存文章失败: {e}")
            conn.rollback()
        finally:
            conn.close()
        
        return saved_count
    
    def print_results(self):
        """打印爬取结果"""
        print("\n" + "=" * 60)
        print("📊 爬取结果统计")
        print("=" * 60)
        print(f"总新闻源: {self.results['total_sources']}")
        print(f"成功爬取: {self.results['success_count']}")
        print(f"爬取失败: {self.results['error_count']}")
        print(f"新增文章: {self.results['new_articles']}")
        
        if self.results['errors']:
            print(f"\n❌ 错误详情:")
            for error in self.results['errors']:
                print(f"  - {error}")

def main():
    """主函数"""
    print("NewsMind 真实新闻爬虫")
    print("=" * 60)
    
    crawler = RealNewsCrawler()
    
    # 开始爬取
    start_time = time.time()
    results = crawler.crawl_all_sources()
    end_time = time.time()
    
    # 打印结果
    crawler.print_results()
    
    print(f"\n⏱️  耗时: {end_time - start_time:.2f} 秒")
    
    if results['new_articles'] > 0:
        print(f"\n🎉 成功获取 {results['new_articles']} 篇新文章!")
        print("📍 现在可以访问前端页面查看最新新闻")
    else:
        print(f"\n⚠️  未获取到新文章，可能原因:")
        print("   - 文章已存在（去重机制）")
        print("   - 新闻源暂时无更新")
        print("   - 网络连接问题")

if __name__ == "__main__":
    main() 