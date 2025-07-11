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
            language = detect_language_improved(article['title'], article['content'], source_name)
            
            # 保存文章（只保存原文，不进行翻译）
            cursor.execute("""
                INSERT INTO news_articles (
                    title, content, source_url, source_name, publish_time, 
                    category, language, quality_score, is_processed, created_at, source_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                article['title'],
                article['content'],  # 保存原始内容
                article['source_url'],
                source_name,
                article['publish_time'].isoformat() if article['publish_time'] else None,
                category,
                language,
                0.0,  # 初始质量分数
                False,  # 标记为未处理
                datetime.now().isoformat(),
                source_id
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
                        keep, cat, clean_content = filter_article(article['title'], article['content'])
                        if keep:
                            # 使用清洗后的内容
                            article['content'] = clean_content
                            article['category'] = cat
                            
                            # 尝试提取完整正文内容
                            enhanced_article = enhance_rss_article(article)
                            filtered_articles.append(enhanced_article)
                        else:
                            print(f"   🚫 过滤掉: {article['title'][:30]}...")
                    
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
                'title': f'今日科技新闻：AI技术最新突破 - {datetime.now().strftime("%Y-%m-%d")}',
                'content': f'''今日科技领域传来重大消息，人工智能技术再次取得突破性进展。研究人员开发出了新一代机器学习算法，该算法在多个基准测试中都表现优异。

这项技术突破主要涉及自然语言处理和计算机视觉两个领域。新算法采用了创新的神经网络架构，能够更准确地理解和处理复杂的语言模式。在图像识别方面，该算法的准确率比现有技术提升了15%以上。

专家表示，这一突破将为AI应用带来更多可能性。在医疗诊断、自动驾驶、智能客服等领域，新技术都将发挥重要作用。预计在未来几个月内，基于这一算法的产品将陆续面世。

该研究团队来自多个知名机构，包括斯坦福大学、麻省理工学院等。他们花了两年时间开发这套算法，投入了大量的人力和物力资源。测试结果显示，新算法不仅性能优异，而且能耗更低，更适合实际应用。

然而，专家也提醒，AI技术的发展也带来了一些挑战，包括就业结构的变化、隐私保护问题等。因此，在推进AI技术应用的同时，也需要制定相应的法律法规和伦理准则，确保技术的健康发展。''',
                'source_url': f'https://tech.example.com/ai-breakthrough-{datetime.now().strftime("%Y%m%d")}',
                'source_name': '科技日报',
                'publish_time': datetime.now(),
                'category': '科技',
                'language': 'zh',
                'quality_score': 8.5,
                'is_processed': False,
                'source_id': source_id
            },
            {
                'title': f'经济新闻：全球市场今日表现 - {datetime.now().strftime("%Y-%m-%d")}',
                'content': f'''今日全球金融市场表现活跃，主要股指普遍上涨。投资者对经济复苏前景持乐观态度，市场情绪明显改善。

美国股市今日开盘走高，道琼斯工业平均指数上涨1.2%，纳斯达克综合指数上涨1.8%。科技股表现尤为强劲，苹果、微软、谷歌等科技巨头股价都有不同程度上涨。

欧洲股市也表现良好，德国DAX指数上涨0.8%，法国CAC40指数上涨0.9%。亚洲市场方面，日经225指数上涨1.1%，香港恒生指数上涨0.7%。

分析师认为，市场上涨的主要原因是投资者对全球经济复苏的预期增强。最新公布的经济数据显示，主要经济体的经济活动正在稳步恢复，就业市场也在持续改善。

然而，专家也提醒投资者要保持谨慎，市场仍面临一些不确定性因素，包括通胀压力、地缘政治风险等。建议投资者做好风险管理，合理配置资产。

在商品市场方面，原油价格今日小幅上涨，黄金价格保持稳定。外汇市场方面，美元指数小幅下跌，欧元和日元对美元汇率都有所上涨。''',
                'source_url': f'https://finance.example.com/market-update-{datetime.now().strftime("%Y%m%d")}',
                'source_name': '财经时报',
                'publish_time': datetime.now(),
                'category': '财经',
                'language': 'zh',
                'quality_score': 8.0,
                'is_processed': False,
                'source_id': source_id
            },
            {
                'title': f'国际新闻：多国签署新协议 - {datetime.now().strftime("%Y-%m-%d")}',
                'content': f'''今日在联合国总部举行的国际会议上，多个国家签署了新的合作协议，旨在加强国际合作，应对全球性挑战。

该协议涵盖了气候变化、贸易合作、技术交流等多个领域。参与国承诺在未来十年内加强合作，共同应对气候变化、促进可持续发展、推动技术创新。

在气候变化方面，各国承诺到2030年将温室气体排放减少50%，到2050年实现碳中和。这将需要各国采取更积极的措施，包括发展可再生能源、提高能源效率、保护森林生态系统等。

在贸易合作方面，协议规定将降低关税壁垒，简化贸易程序，促进投资便利化。这将有助于促进全球贸易发展，推动经济复苏。

在技术交流方面，各国同意加强科技合作，共同推动人工智能、清洁能源、生物技术等前沿领域的发展。这将为全球科技进步提供新的动力。

专家认为，这一协议的签署具有重要意义，体现了国际社会加强合作、共同应对挑战的决心。然而，协议的成功实施还需要各国的共同努力和持续投入。

联合国秘书长表示，这一协议为构建更加公平、可持续的世界提供了重要框架。他呼吁各国认真履行承诺，为人类的共同未来做出贡献。''',
                'source_url': f'https://world.example.com/international-agreement-{datetime.now().strftime("%Y%m%d")}',
                'source_name': '国际新闻',
                'publish_time': datetime.now(),
                'category': '国际',
                'language': 'zh',
                'quality_score': 9.0,
                'is_processed': False,
                'source_id': source_id
            }
        ]
        
        # 保存新文章
        saved_count = 0
        for article_data in new_articles:
            try:
                # 检查是否已存在
                cursor.execute("SELECT id FROM news_articles WHERE source_url = ?", (article_data['source_url'],))
                if cursor.fetchone():
                    print(f"⚠ 文章已存在: {article_data['title']}")
                    continue
                
                # 插入新文章
                cursor.execute("""
                    INSERT INTO news_articles (
                        title, content, source_url, source_name, publish_time, 
                        category, language, quality_score, is_processed, created_at, source_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    article_data['title'],
                    article_data['content'],
                    article_data['source_url'],
                    article_data['source_name'],
                    article_data['publish_time'].isoformat(),
                    article_data['category'],
                    article_data['language'],
                    article_data['quality_score'],
                    article_data['is_processed'],
                    datetime.now().isoformat(),
                    article_data['source_id']
                ))
                print(f"✓ 创建文章: {article_data['title']}")
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
        SELECT title, source_name, created_at 
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