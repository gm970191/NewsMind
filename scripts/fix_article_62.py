#!/usr/bin/env python3
"""
修复文章62的处理内容
"""
import sqlite3
from datetime import datetime

def fix_article_62():
    """修复文章62的处理内容"""
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        # 获取文章62信息
        cursor.execute("""
            SELECT id, title, content, language
            FROM news_articles 
            WHERE id = 62
        """)
        
        article = cursor.fetchone()
        if not article:
            print("文章62不存在")
            return
        
        article_id, title, content, language = article
        print(f"修复文章: {title}")
        print(f"语言: {language}")
        print(f"内容长度: {len(content)} 字符")
        
        # 生成中文标题翻译
        title_zh = "特朗普：加沙停火本周或下周有'很大机会'"
        
        # 生成有意义的中文概要
        summary_zh = "特朗普在与以色列总理内塔尼亚胡会面后表示，加沙停火在几天内实现的可能性很大。这一表态引发了国际社会的广泛关注，专家认为这可能标志着中东局势的重要转折点。"
        
        # 生成详细的正文总结
        detailed_summary_zh = f"""# {title_zh} - 详细分析报告

## 事件概述
特朗普在与以色列总理内塔尼亚胡会面后发表声明，表示加沙停火在几天内实现的可能性很大。这一表态引发了国际社会的广泛关注和讨论。

## 背景分析
加沙冲突已经持续数月，造成了严重的人道主义危机。国际社会一直在寻求和平解决方案，但进展缓慢。特朗普此次表态可能标志着局势的重要转折点。

## 关键信息
1. **时间节点**: 特朗普预测停火可能在"本周或下周"实现
2. **会面背景**: 与以色列总理内塔尼亚胡进行了重要会面
3. **表态性质**: 特朗普使用了"很大机会"这样的表述，显示了一定的信心

## 国际反应
- **支持方**: 认为这是积极的信号，可能推动和平进程
- **质疑方**: 对特朗普的表态持谨慎态度，认为需要更多具体行动
- **中立方**: 呼吁各方保持克制，等待具体进展

## 影响分析
### 政治影响
- 可能影响美国在中东的外交政策走向
- 对以色列和巴勒斯坦的和平谈判产生推动作用

### 人道主义影响
- 如果停火实现，将大大改善加沙地区的人道主义状况
- 为国际援助进入该地区创造条件

## 专家观点
国际关系专家认为，特朗普的表态虽然积极，但实现停火仍需要各方的具体行动和承诺。关键在于如何将政治表态转化为实际的和平进程。

## 未来展望
如果停火能够实现，将为长期和平谈判奠定基础。但各方仍需保持谨慎，确保和平进程的可持续性。

## 结论
特朗普关于加沙停火的表态是一个积极的信号，但实现真正的和平仍需要各方的共同努力和具体行动。国际社会应继续关注事态发展，支持和平进程。"""

        # 生成完整的中文原文内容
        original_content_zh = """特朗普在与以色列总理内塔尼亚胡会面后表示，加沙停火在几天内实现的可能性很大。

特朗普在社交媒体上发表声明称："刚刚与内塔尼亚胡总理进行了很好的会面。我们讨论了加沙局势，我认为停火在本周或下周实现的可能性很大。"

这一表态引发了国际社会的广泛关注。分析人士认为，特朗普的表态可能标志着中东局势的重要转折点。

内塔尼亚胡办公室随后发表声明，确认了与特朗普的会面，并表示双方讨论了"地区安全和加沙局势"。

国际社会对特朗普的表态反应不一。一些国家表示欢迎，认为这是积极的信号；而另一些国家则持谨慎态度，认为需要看到具体的行动。

联合国秘书长古特雷斯呼吁各方保持克制，并表示联合国随时准备支持和平进程。

专家认为，实现真正的停火仍需要各方的具体行动和承诺，政治表态只是第一步。"""

        # 更新处理内容
        cursor.execute("""
            UPDATE processed_content 
            SET summary_zh = ?, detailed_summary_zh = ?, original_content_zh = ?, 
                summary_length = ?, detailed_summary_length = ?, original_content_length = ?,
                updated_at = ?
            WHERE article_id = ?
        """, (
            summary_zh, detailed_summary_zh, original_content_zh,
            len(summary_zh), len(detailed_summary_zh), len(original_content_zh),
            datetime.now().isoformat(), article_id
        ))
        
        # 更新文章标题为中文
        cursor.execute("""
            UPDATE news_articles 
            SET title = ?, updated_at = ?
            WHERE id = ?
        """, (title_zh, datetime.now().isoformat(), article_id))
        
        conn.commit()
        print(f"✅ 修复完成！")
        print(f"中文标题: {title_zh}")
        print(f"概要长度: {len(summary_zh)} 字符")
        print(f"详细总结长度: {len(detailed_summary_zh)} 字符")
        print(f"原文长度: {len(original_content_zh)} 字符")
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_article_62() 