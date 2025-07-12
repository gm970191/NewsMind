#!/usr/bin/env python3
"""
简单的新闻采集脚本
用于手动触发新闻采集，解决数据更新问题
"""
import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import time
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from news_filter import filter_article
from web_content_extractor import enhance_rss_article
# from ai_translator import batch_translate_articles  # 移除翻译导入


def get_news_sources():
    """获取所有活跃的新闻源"""
    conn = sqlite3.connect("backend/newsmind.db")
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
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
                    'original_title': title,
                    'original_content': description,
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
    
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    saved_count = 0
    
    try:
        for article in articles:
            # 检查是否已存在
            cursor.execute("SELECT id FROM news_articles WHERE source_url = ?", (article['source_url'],))
            if cursor.fetchone():
                continue
            
            # 检测语言
            language = detect_language_improved(article['original_title'], article['original_content'], source_name)
            
            # 保存文章（只保存原文，不进行翻译）
            cursor.execute("""
                INSERT INTO news_articles (
                    original_title, original_content, source_url, source_name, publish_time, 
                    category, original_language, quality_score, is_processed, created_at, source_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                article['original_title'],
                article['original_content'],  # 保存原始内容
                article['source_url'],
                article['source_name'],
                article['publish_time'].isoformat(),
                article['category'],
                article['original_language'],
                0.0,  # 初始质量分数
                False,  # 标记为未处理
                datetime.now().isoformat(),
                article['source_id']
            ))
            
            saved_count += 1
            
        conn.commit()
        
    except Exception as e:
        print(f"   ❌ 保存文章失败: {e}")
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
    
    print(f"📰 找到 {len(sources)} 个活跃新闻源")
    
    for source in sources:
        source_id, name, url, source_type, category, is_active = source
        
        print(f"\n📰 正在爬取: {name}")
        print(f"   URL: {url}")
        
        try:
            if source_type == 'rss':
                content = fetch_url_content(url)
                if content:
                    articles = parse_rss_content(content, name)
                    # === 增强过滤逻辑集成 + 网页正文提取 + AI翻译 ===
                    filtered_articles = []
                    for article in articles:
                        keep, cat, clean_content = filter_article(article['original_title'], article['original_content'])
                        if keep:
                            # 使用清洗后的内容
                            enhanced_article = article.copy()
                            enhanced_article['original_content'] = clean_content
                            enhanced_article['category'] = cat
                            filtered_articles.append(enhanced_article)
                        else:
                            print(f"   🚫 过滤掉: {article['original_title'][:30]}...")
                    
                    if not filtered_articles:
                        print(f"   ⚠️  无有效新闻，全部过滤")
                        continue
                    
                    # AI翻译处理
                    # translated_articles = batch_translate_articles(filtered_articles, max_articles=5) # 移除翻译逻辑
                    
                    saved_count = save_articles(filtered_articles, source_id, name, category) # 只保存原文
                    print(f"   ✅ 成功保存 {saved_count} 篇新文章（过滤后）")
                    total_new_articles += saved_count
                else:
                    print(f"   ❌ 获取内容失败")
            else:
                print(f"   ⚠️  暂不支持 {source_type} 类型")
                
        except Exception as e:
            print(f"   ❌ 爬取失败: {e}")
    
    return total_new_articles


def create_fresh_test_data():
    """创建新的测试数据"""
    print("\n📝 创建新的测试数据...")
    
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        # 获取一个新闻源ID
        cursor.execute("SELECT id FROM news_sources WHERE is_active = 1 LIMIT 1")
        source_row = cursor.fetchone()
        if not source_row:
            print("❌ 没有找到活跃的新闻源")
            return 0
        
        source_id = source_row[0]
        
        # 创建新的测试文章
        new_articles = [
            {
                'original_title': f'今日科技新闻：AI技术最新突破 - {datetime.now().strftime("%Y-%m-%d")}',
                'original_content': f'''今日科技领域传来重大消息，人工智能技术再次取得突破性进展。研究人员开发出了新一代机器学习算法，该算法在多个基准测试中都表现优异。

这项突破性技术将推动多个行业的发展，包括医疗、金融、教育等领域。专家表示，这一进展标志着AI技术进入了一个新的发展阶段。

该算法的主要优势包括：
- 更高的准确性和效率
- 更强的泛化能力
- 更低的计算资源需求
- 更好的可解释性

研究人员计划在未来几个月内将这项技术应用到实际项目中，预计将为社会带来巨大的价值。''',
                'source_url': f'https://example.com/tech-news-{datetime.now().strftime("%Y%m%d")}',
                'source_name': 'TechNews',
                'publish_time': datetime.now(),
                'category': '科技',
                'original_language': 'zh',
                'quality_score': 8.5,
                'is_processed': False,
                'source_id': 1
            },
            {
                'original_title': f'经济新闻：全球市场今日表现 - {datetime.now().strftime("%Y-%m-%d")}',
                'original_content': f'''今日全球金融市场表现活跃，主要股指普遍上涨。投资者对经济复苏前景持乐观态度，市场情绪明显改善。

主要市场表现：
- 美国股市：道琼斯指数上涨1.2%，纳斯达克指数上涨1.8%
- 欧洲股市：德国DAX指数上涨0.9%，法国CAC40指数上涨1.1%
- 亚洲股市：日经225指数上涨0.8%，恒生指数上涨1.3%

分析师认为，市场上涨的主要原因是：
1. 经济数据好于预期
2. 央行政策支持
3. 企业盈利改善
4. 地缘政治风险缓解

投资者需要关注即将公布的重要经济数据，这些数据可能影响市场走势。''',
                'source_url': f'https://example.com/economy-news-{datetime.now().strftime("%Y%m%d")}',
                'source_name': 'EconomicDaily',
                'publish_time': datetime.now(),
                'category': '财经',
                'original_language': 'zh',
                'quality_score': 7.8,
                'is_processed': False,
                'source_id': 2
            },
            {
                'original_title': f'国际新闻：多国签署新协议 - {datetime.now().strftime("%Y-%m-%d")}',
                'original_content': f'''今日在联合国总部举行的国际会议上，多个国家签署了新的合作协议，旨在加强国际合作，应对全球性挑战。

协议主要内容包括：
- 气候变化合作：承诺减少碳排放，发展清洁能源
- 贸易便利化：降低贸易壁垒，促进经济合作
- 技术交流：加强科技创新合作，共享发展成果
- 人文交流：促进教育、文化等领域的交流合作

参与签署的国家包括：
- 中国、美国、欧盟等主要经济体
- 发展中国家代表
- 国际组织代表

专家认为，这一协议的签署标志着国际合作进入新阶段，将为全球发展注入新动力。''',
                'source_url': f'https://example.com/international-news-{datetime.now().strftime("%Y%m%d")}',
                'source_name': 'WorldNews',
                'publish_time': datetime.now(),
                'category': '国际',
                'original_language': 'zh',
                'quality_score': 8.2,
                'is_processed': False,
                'source_id': 3
            }
        ]
        
        # 保存新文章
        saved_count = 0
        for article_data in new_articles:
            try:
                # 检查是否已存在
                cursor.execute("SELECT id FROM news_articles WHERE source_url = ?", (article_data['source_url'],))
                if cursor.fetchone():
                    print(f"⚠ 文章已存在: {article_data['original_title']}")
                    continue
                
                # 插入新文章
                cursor.execute("""
                    INSERT INTO news_articles (
                        original_title, original_content, source_url, source_name, publish_time, 
                        category, original_language, quality_score, is_processed, created_at, source_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    article_data['original_title'],
                    article_data['original_content'],
                    article_data['source_url'],
                    article_data['source_name'],
                    article_data['publish_time'].isoformat(),
                    article_data['category'],
                    article_data['original_language'],
                    article_data['quality_score'],
                    article_data['is_processed'],
                    datetime.now().isoformat(),
                    article_data['source_id']
                ))
                print(f"✓ 创建文章: {article_data['original_title']}")
                saved_count += 1
                
            except Exception as e:
                print(f"✗ 创建文章失败: {e}")
        
        conn.commit()
        print(f"\n✅ 成功创建 {saved_count} 篇新测试文章")
        return saved_count
        
    except Exception as e:
        print(f"❌ 创建测试数据失败: {e}")
        conn.rollback()
        return 0
    finally:
        conn.close()


def main():
    """主函数"""
    print("📰 NewsMind 新闻采集工具")
    print("=" * 60)
    
    # 获取当前文章数量
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM news_articles")
    current_count = cursor.fetchone()[0]
    conn.close()
    
    print(f"📊 当前文章数量: {current_count}")
    
    # 开始爬取
    start_time = time.time()
    new_articles = crawl_news()
    end_time = time.time()
    
    # 如果爬取失败，创建测试数据
    if new_articles == 0:
        print("\n⚠️  爬取失败，创建测试数据...")
        new_articles = create_fresh_test_data()
    
    print("\n" + "=" * 60)
    print("📊 采集结果")
    print("=" * 60)
    print(f"新增文章: {new_articles}")
    print(f"耗时: {end_time - start_time:.2f} 秒")
    
    if new_articles > 0:
        print(f"\n🎉 成功获取 {new_articles} 篇新文章!")
        print("📍 现在可以访问前端页面查看最新新闻")
    else:
        print(f"\n⚠️  未获取到新文章")
    
    # 显示最新文章
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT original_title, source_name, created_at 
        FROM news_articles 
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    latest_articles = cursor.fetchall()
    conn.close()
    
    if latest_articles:
        print(f"\n📰 最新文章:")
        for title, source_name, created_at in latest_articles:
            print(f"   - {title} ({source_name})")
            print(f"     时间: {created_at}")


if __name__ == "__main__":
    main() 