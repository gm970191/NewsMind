#!/usr/bin/env python3
"""
简化版RSS爬虫，不依赖playwright
"""
import sys
import os
import asyncio
import requests
from datetime import datetime
from pathlib import Path
from feedparser import parse as feedparse

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal
from app.services.news_service import NewsRepository
from app.models.news import NewsSource


class SimpleRSSCrawler:
    """简化版RSS爬虫"""
    
    def __init__(self, repo: NewsRepository):
        self.repo = repo
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def crawl_rss_sources(self):
        """抓取所有RSS新闻源"""
        sources = self.repo.get_active_sources()
        results = {
            'total_sources': len(sources),
            'success_count': 0,
            'error_count': 0,
            'new_articles': 0
        }
        
        for source in sources:
            try:
                print(f"正在采集: {source.name} ({source.url})")
                
                if source.type == 'rss':
                    articles = self.crawl_rss_source(source)
                else:
                    print(f"跳过非RSS源: {source.name}")
                    continue
                
                # 保存文章
                for article_data in articles:
                    try:
                        # 检查是否已存在
                        existing = self.repo.get_article_by_url(article_data['source_url'])
                        if not existing:
                            self.repo.create_article(article_data)
                            results['new_articles'] += 1
                            print(f"  ✓ 保存新文章: {article_data['title'][:50]}...")
                    except Exception as e:
                        print(f"  ✗ 保存文章失败: {e}")
                
                results['success_count'] += 1
                
            except Exception as e:
                print(f"  ✗ 采集失败: {e}")
                results['error_count'] += 1
        
        return results
    
    def crawl_rss_source(self, source: NewsSource):
        """抓取单个RSS源"""
        try:
            # 获取RSS内容
            response = self.session.get(source.url, timeout=30)
            response.raise_for_status()
            
            # 解析RSS
            feed = feedparse(response.content)
            articles = []
            
            print(f"  找到 {len(feed.entries)} 篇文章")
            
            for entry in feed.entries[:10]:  # 限制最多10篇
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
                            pass
                    
                    article_data = {
                        'title': title,
                        'content': content,
                        'source_url': link,
                        'source_id': source.id,
                        'source_name': source.name,
                        'publish_time': publish_time,
                        'category': source.category,
                        'language': 'en'  # 默认英文
                    }
                    
                    articles.append(article_data)
                    
                except Exception as e:
                    print(f"    解析文章失败: {e}")
                    continue
            
            return articles
            
        except Exception as e:
            print(f"  抓取RSS失败: {e}")
            return []


def test_rss_crawler():
    """测试RSS爬虫"""
    print("=== 开始测试RSS新闻采集 ===")
    
    # 创建数据库会话
    db = SessionLocal()
    repo = NewsRepository(db)
    
    try:
        # 获取所有活跃的新闻源
        sources = repo.get_active_sources()
        print(f"找到 {len(sources)} 个活跃新闻源:")
        for source in sources:
            print(f"  - {source.name} ({source.type}): {source.url}")
        
        # 开始采集
        print("\n开始采集RSS新闻...")
        crawler = SimpleRSSCrawler(repo)
        results = crawler.crawl_rss_sources()
        
        # 显示结果
        print(f"\n采集结果:")
        print(f"  总新闻源: {results['total_sources']}")
        print(f"  成功采集: {results['success_count']}")
        print(f"  采集失败: {results['error_count']}")
        print(f"  新增文章: {results['new_articles']}")
        
        # 显示最新文章
        if results['new_articles'] > 0:
            print(f"\n最新采集的文章:")
            articles = repo.get_recent_articles(days=1)
            for i, article in enumerate(articles[:5], 1):
                print(f"  {i}. {article.title}")
                print(f"     来源: {article.source_name}")
                print(f"     时间: {article.created_at}")
                print(f"     分类: {article.category}")
                print(f"     链接: {article.source_url}")
                print()
        
        return results
        
    except Exception as e:
        print(f"采集过程中出现错误: {e}")
        return None
    finally:
        db.close()


def main():
    """主函数"""
    print("NewsMind RSS爬虫测试")
    print("=" * 50)
    
    # 运行测试
    results = test_rss_crawler()
    
    if results:
        print("=" * 50)
        print("测试完成!")
        
        if results['new_articles'] > 0:
            print(f"✅ 成功采集到 {results['new_articles']} 篇新文章")
        else:
            print("⚠️  未采集到新文章，可能原因:")
            print("   - 文章已存在（去重机制）")
            print("   - RSS源暂时无更新")
            print("   - 网络连接问题")
    else:
        print("❌ 测试失败")


if __name__ == "__main__":
    main() 