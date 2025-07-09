#!/usr/bin/env python3
"""
创建测试新闻数据
"""
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

import sqlite3

def create_test_news():
    """创建测试新闻数据"""
    print("📰 创建测试新闻数据...")
    
    # 连接到数据库
    db_path = "newsmind.db"  # 使用根目录的数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取第一个新闻源ID
    cursor.execute("SELECT id FROM news_sources WHERE is_active = 1 LIMIT 1")
    result = cursor.fetchone()
    if not result:
        print("❌ 没有找到活跃的新闻源，请先初始化数据库")
        return False
    
    source_id = result[0]
    print(f"使用新闻源ID: {source_id}")
    
    # 测试新闻数据
    test_articles = [
        {
            'title': '人工智能技术突破：新型算法提升效率30%',
            'content': '最新研究显示，基于深度学习的AI算法在多个领域取得了显著突破。该算法不仅提高了处理效率，还降低了能耗，为未来AI应用开辟了新的可能性。研究人员表示，这项技术将在医疗、金融、教育等领域产生深远影响。',
            'source_name': '科技日报',
            'source_url': 'https://example.com/ai-breakthrough',
            'category': '科技',
            'language': 'zh',
            'publish_time': datetime.now() - timedelta(hours=2)
        },
        {
            'title': '全球气候变化：各国承诺加强环保措施',
            'content': '在最新召开的全球气候峰会上，各国领导人就应对气候变化达成重要共识。与会国家承诺在未来十年内大幅减少碳排放，并投资可再生能源项目。专家认为，这些措施将对全球环境产生积极影响。',
            'source_name': '国际新闻',
            'source_url': 'https://example.com/climate-summit',
            'category': '国际',
            'language': 'zh',
            'publish_time': datetime.now() - timedelta(hours=4)
        },
        {
            'title': '新能源汽车销量创新高：市场前景广阔',
            'content': '据最新统计数据显示，新能源汽车销量在今年第三季度创下历史新高，同比增长超过50%。专家分析认为，这一增长趋势将持续，预计到2025年，新能源汽车将占据汽车市场的30%以上份额。',
            'source_name': '财经日报',
            'source_url': 'https://example.com/ev-sales',
            'category': '财经',
            'language': 'zh',
            'publish_time': datetime.now() - timedelta(hours=6)
        },
        {
            'title': '健康生活：专家建议每日运动30分钟',
            'content': '世界卫生组织最新发布的健康指南建议，成年人每天应进行至少30分钟的中等强度运动。研究表明，规律运动不仅能预防多种疾病，还能提高生活质量。专家建议将运动融入日常生活，如步行上班、爬楼梯等。',
            'source_name': '健康时报',
            'source_url': 'https://example.com/health-exercise',
            'category': '健康',
            'language': 'zh',
            'publish_time': datetime.now() - timedelta(hours=8)
        },
        {
            'title': '教育改革：数字化教学成为新趋势',
            'content': '随着技术的快速发展，数字化教学正在成为教育领域的新趋势。越来越多的学校开始采用在线学习平台、虚拟现实技术等创新教学方法。专家认为，这种转变将为学生提供更加个性化和高效的学习体验。',
            'source_name': '教育周刊',
            'source_url': 'https://example.com/digital-education',
            'category': '教育',
            'language': 'zh',
            'publish_time': datetime.now() - timedelta(hours=10)
        },
        {
            'title': 'SpaceX成功发射新一代卫星：推进太空互联网计划',
            'content': 'SpaceX公司今日成功发射了新一代Starlink卫星，这是其太空互联网计划的重要里程碑。这批卫星将为全球偏远地区提供高速互联网服务。公司表示，计划在未来几年内发射数万颗卫星，构建全球卫星互联网网络。',
            'source_name': '科技前沿',
            'source_url': 'https://example.com/spacex-launch',
            'category': '科技',
            'language': 'zh',
            'publish_time': datetime.now() - timedelta(hours=12)
        },
        {
            'title': '文化艺术：传统与现代的完美融合',
            'content': '在最新举办的文化艺术节上，艺术家们展示了传统艺术与现代技术的完美融合。通过数字技术，古老的绘画、音乐、舞蹈等艺术形式焕发出新的生命力。观众们对这种创新表现出了极大的热情和认可。',
            'source_name': '文化月刊',
            'source_url': 'https://example.com/art-fusion',
            'category': '文化',
            'language': 'zh',
            'publish_time': datetime.now() - timedelta(hours=14)
        },
        {
            'title': '体育赛事：奥运会筹备工作进展顺利',
            'content': '距离下一届奥运会还有不到一年的时间，主办城市的筹备工作正在紧张进行中。场馆建设、交通规划、安全保障等各项工作都在按计划推进。组委会表示，有信心为全世界呈现一届精彩的体育盛会。',
            'source_name': '体育新闻',
            'source_url': 'https://example.com/olympics-prep',
            'category': '体育',
            'language': 'zh',
            'publish_time': datetime.now() - timedelta(hours=16)
        }
    ]
    
    try:
        # 插入测试文章
        for i, article in enumerate(test_articles, 1):
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
                source_id
            ))
            print(f"  ✓ 插入文章 {i}: {article['title'][:30]}...")
        
        # 提交事务
        conn.commit()
        
        # 查询统计信息
        cursor.execute("SELECT COUNT(*) FROM news_articles")
        total_articles = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM news_articles WHERE is_processed = 1")
        processed_articles = cursor.fetchone()[0]
        
        print(f"\n✅ 测试数据创建完成!")
        print(f"📊 数据库统计:")
        print(f"  总文章数: {total_articles}")
        print(f"  已处理文章: {processed_articles}")
        print(f"  新增测试文章: {len(test_articles)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建测试数据失败: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def main():
    """主函数"""
    print("NewsMind 测试数据创建工具")
    print("=" * 50)
    
    # 创建测试数据
    success = create_test_news()
    
    if success:
        print("\n🎉 现在可以访问前端页面查看新闻了!")
        print("📍 前端地址: http://localhost:3000")
        print("📍 后端API: http://localhost:8000/api/v1/news/articles")
    else:
        print("\n❌ 测试数据创建失败，请检查数据库连接")

if __name__ == "__main__":
    main() 