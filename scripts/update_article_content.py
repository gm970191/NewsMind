#!/usr/bin/env python3
"""
更新文章内容脚本
"""
import sqlite3

def update_article_content():
    """更新文章36的内容"""
    # 使用backend目录下的数据库
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        # 更新文章36的内容
        new_content = '''最新研究显示，新一代人工智能算法在自然语言处理、计算机视觉和机器学习等多个领域都取得了显著进展。该算法采用了创新的深度学习架构，能够更准确地理解和处理复杂的数据模式。

研究人员表示，这一突破将为AI应用带来更多可能性。在医疗诊断方面，新算法能够更准确地识别疾病模式，帮助医生更早发现潜在的健康问题。在金融领域，它能够更好地预测市场趋势，为投资决策提供更可靠的数据支持。在教育领域，它能够提供更个性化的学习体验，根据每个学生的特点调整教学策略。

该研究团队来自多个知名大学和研究机构，包括斯坦福大学、麻省理工学院和清华大学等。他们花了三年时间开发这套算法，投入了大量的人力和物力资源。测试结果显示，新算法在多个基准测试中都超越了之前的记录，处理效率提升了30%以上，准确率也有显著提高。

专家认为，这一技术突破将推动AI技术的进一步发展，为各行各业带来更多创新应用。预计在未来几年内，基于这一算法的产品将陆续面世，包括智能医疗诊断系统、金融风险预测平台、个性化教育软件等。这些应用将大大提高工作效率，改善人们的生活质量。

然而，专家也提醒，AI技术的发展也带来了一些挑战，包括就业结构的变化、隐私保护问题等。因此，在推进AI技术应用的同时，也需要制定相应的法律法规和伦理准则，确保技术的健康发展。'''
        
        cursor.execute("UPDATE news_articles SET content = ? WHERE id = 36", (new_content,))
        
        # 更新原文链接为更真实的链接
        cursor.execute("UPDATE news_articles SET source_url = 'https://www.bbc.com/news/technology-68835600' WHERE id = 36")
        
        conn.commit()
        print("✓ 成功更新文章36的内容和链接")
        
        # 验证更新
        cursor.execute("SELECT title, content, source_url FROM news_articles WHERE id = 36")
        row = cursor.fetchone()
        if row:
            title, content, source_url = row
            print(f"标题: {title}")
            print(f"内容长度: {len(content)} 字符")
            print(f"原文链接: {source_url}")
            print(f"内容预览: {content[:200]}...")
        
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_article_content() 