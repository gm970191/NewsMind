#!/usr/bin/env python3
"""
创建更好的测试数据
"""
import sqlite3
from datetime import datetime
import random

def create_better_test_data():
    """创建更好的测试数据"""
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        # 清空现有数据
        cursor.execute("DELETE FROM processed_content")
        cursor.execute("DELETE FROM news_articles")
        
        # 测试文章数据
        test_articles = [
            {
                "title": "人工智能技术突破：GPT-5模型发布，性能大幅提升",
                "source_name": "科技日报",
                "category": "科技",
                "language": "zh",
                "content": "OpenAI今日正式发布了GPT-5模型，这是继GPT-4之后的重要升级。新模型在多个基准测试中表现优异，特别是在推理能力、代码生成和创意写作方面都有显著提升。GPT-5采用了全新的架构设计，训练数据量达到前所未有的规模，预计将为AI应用带来革命性变化。专家表示，这一突破将推动人工智能技术在各个领域的广泛应用。"
            },
            {
                "title": "全球经济复苏：多国GDP增长超预期，市场信心回升",
                "source_name": "财经时报",
                "category": "财经",
                "language": "zh",
                "content": "最新经济数据显示，全球主要经济体GDP增长均超过市场预期。美国、欧盟、中国等主要经济体的复苏势头强劲，失业率持续下降，消费者信心指数创下新高。分析人士认为，这一趋势得益于各国有效的经济刺激政策和疫苗接种的推进。预计未来几个季度，全球经济将继续保持稳定增长态势。"
            },
            {
                "title": "气候变化应对：联合国气候大会达成新协议",
                "source_name": "国际新闻",
                "category": "国际",
                "language": "zh",
                "content": "在刚刚结束的联合国气候变化大会上，各国代表就减排目标达成新的协议。协议要求发达国家在2030年前将温室气体排放减少50%，发展中国家则根据自身情况制定相应的减排计划。此外，会议还设立了1000亿美元的气候基金，用于支持发展中国家的清洁能源项目。环保组织对这一协议表示欢迎，认为这是应对气候变化的重要一步。"
            },
            {
                "title": "SpaceX成功发射载人飞船，开启商业太空旅游新时代",
                "source_name": "科技前沿",
                "category": "科技",
                "language": "zh",
                "content": "SpaceX公司今日成功发射了载有平民乘客的载人飞船，标志着商业太空旅游正式开启。这次飞行任务名为Inspiration4，四名平民乘客将在太空中停留三天，进行科学实验和地球观测。这是人类历史上首次全平民太空飞行，为未来的太空旅游奠定了基础。专家认为，这一里程碑事件将推动太空产业的快速发展。"
            },
            {
                "title": "新能源汽车销量创新高：电动汽车市场迎来爆发期",
                "source_name": "汽车周刊",
                "category": "科技",
                "language": "zh",
                "content": "最新统计数据显示，今年第三季度全球新能源汽车销量达到创纪录的300万辆，同比增长超过60%。其中，纯电动汽车占比达到70%，插电式混合动力汽车占30%。中国、欧洲和美国是主要市场，各国政府推出的补贴政策和充电基础设施的完善推动了销量的快速增长。预计到2025年，新能源汽车将占据全球汽车市场的30%以上。"
            }
        ]
        
        print("📝 创建高质量测试数据...")
        
        for i, article in enumerate(test_articles, 1):
            # 插入文章
            cursor.execute("""
                INSERT INTO news_articles 
                (title, source_name, source_url, source_id, category, language, content, content_length, 
                 publish_time, created_at, updated_at, is_processed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                article["title"],
                article["source_name"],
                "https://example.com/article",
                1,
                article["category"],
                article["language"],
                article["content"],
                len(article["content"]),
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                False
            ))
            
            article_id = cursor.lastrowid
            print(f"✓ 创建文章 {i}: {article['title']}")
        
        conn.commit()
        print(f"\n✅ 成功创建 {len(test_articles)} 篇高质量测试文章")
        
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_better_test_data() 