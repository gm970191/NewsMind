#!/usr/bin/env python3
"""
采集指定新闻源的真实数据
"""
import requests
import sqlite3
from datetime import datetime
import xml.etree.ElementTree as ET
from urllib.parse import urljoin
import time

def crawl_specific_sources():
    """采集指定新闻源"""
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    # 新闻源配置
    sources = [
        {
            "name": "Al Jazeera",
            "description": "中东视角、全球南方国家重要媒体",
            "url": "https://www.aljazeera.com/xml/rss/all.xml",
            "category": "国际"
        },
        {
            "name": "The Washington Post",
            "description": "美国政界报道主力媒体", 
            "url": "https://feeds.washingtonpost.com/rss/world",
            "category": "国际"
        }
    ]
    
    total_articles = 0
    
    try:
        print("🌐 开始采集指定新闻源...")
        print("=" * 60)
        
        for source in sources:
            print(f"\n📰 正在采集: {source['name']}")
            print(f"   描述: {source['description']}")
            print(f"   URL: {source['url']}")
            
            try:
                # 获取RSS内容
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(source['url'], headers=headers, timeout=10)
                response.raise_for_status()
                
                # 解析RSS
                root = ET.fromstring(response.content)
                
                # 查找所有item元素
                items = root.findall('.//item')
                print(f"   找到 {len(items)} 篇文章")
                
                articles_saved = 0
                for i, item in enumerate(items[:10]):  # 限制每源最多10篇
                    try:
                        # 提取文章信息
                        title_elem = item.find('title')
                        link_elem = item.find('link')
                        description_elem = item.find('description')
                        pub_date_elem = item.find('pubDate')
                        
                        if title_elem is None or title_elem.text is None:
                            continue
                            
                        title = title_elem.text.strip()
                        link = link_elem.text.strip() if link_elem is not None and link_elem.text else ""
                        description = description_elem.text.strip() if description_elem is not None and description_elem.text else ""
                        
                        # 处理发布时间
                        pub_date = None
                        if pub_date_elem is not None and pub_date_elem.text:
                            try:
                                pub_date = datetime.strptime(pub_date_elem.text, '%a, %d %b %Y %H:%M:%S %z')
                            except:
                                pub_date = datetime.now()
                        else:
                            pub_date = datetime.now()
                        
                        # 生成唯一URL
                        unique_url = f"{link}_{i}" if link else f"https://{source['name'].lower().replace(' ', '')}.com/article_{i}"
                        
                        # 保存到数据库
                        cursor.execute("""
                            INSERT INTO news_articles 
                            (title, source_name, source_url, source_id, category, language, content, content_length,
                             publish_time, created_at, updated_at, is_processed)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            title,
                            source['name'],
                            unique_url,
                            total_articles + 1,
                            source['category'],
                            'en',  # 这些源都是英文
                            description or title,  # 如果没有描述就用标题
                            len(description or title),
                            pub_date.isoformat(),
                            datetime.now().isoformat(),
                            datetime.now().isoformat(),
                            False
                        ))
                        
                        articles_saved += 1
                        print(f"   ✓ 保存: {title[:50]}...")
                        
                    except Exception as e:
                        print(f"   ❌ 处理文章失败: {e}")
                        continue
                
                print(f"   ✅ 成功保存 {articles_saved} 篇文章")
                total_articles += articles_saved
                
            except Exception as e:
                print(f"   ❌ 采集失败: {e}")
                continue
            
            # 避免请求过快
            time.sleep(2)
        
        conn.commit()
        print(f"\n🎉 采集完成！总共保存 {total_articles} 篇文章")
        
        # 显示最新文章
        cursor.execute("""
            SELECT title, source_name, created_at 
            FROM news_articles 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        latest_articles = cursor.fetchall()
        print(f"\n📰 最新文章:")
        for article in latest_articles:
            title, source, created_at = article
            print(f"   - {title} ({source})")
        
    except Exception as e:
        print(f"❌ 采集过程出错: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    crawl_specific_sources() 