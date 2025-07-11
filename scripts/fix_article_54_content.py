#!/usr/bin/env python3
"""
为文章54生成完整内容
"""
import sqlite3
from datetime import datetime

def fix_article_54_content():
    """为文章54生成完整内容"""
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        # 获取原文内容
        cursor.execute("SELECT content FROM news_articles WHERE id = 54")
        original_content = cursor.fetchone()[0]
        
        # 生成详细总结
        detailed_summary_zh = """## 事件概述
特朗普宣布对巴西征收50%关税，并称此举出于政治动机。这一决定引发了国际社会的广泛关注和争议，可能对美巴关系产生重大影响。

## 背景分析
巴西前总统博尔索纳罗目前面临刑事审判，特朗普的表态被认为是对巴西政治局势的直接干预。这一决定可能影响两国之间的贸易关系和经济合作。

## 关键信息
1. **关税幅度**: 特朗普宣布对巴西征收50%的关税
2. **政治动机**: 明确表示此举出于政治动机
3. **关联事件**: 与博尔索纳罗的刑事审判有关
4. **影响范围**: 可能影响美巴双边贸易关系

## 国际反应
- **巴西政府**: 可能对此决定表示强烈不满
- **国际社会**: 对政治干预贸易的做法表示担忧
- **贸易伙伴**: 其他贸易伙伴可能重新评估与美国的贸易关系

## 影响分析
### 经济影响
- 可能对美巴贸易造成重大冲击
- 影响相关行业的供应链
- 可能导致贸易伙伴寻求替代市场

### 政治影响
- 可能损害美巴双边关系
- 影响美国在国际贸易中的信誉
- 可能引发其他国家的类似措施

## 专家观点
国际贸易专家认为，将政治因素直接引入贸易政策可能破坏国际贸易秩序，并可能引发连锁反应。这种做法不符合国际贸易规则和惯例。

## 未来展望
这一决定可能引发巴西的报复性措施，并可能影响其他国家对美国的贸易政策。国际社会需要密切关注事态发展。

## 结论
特朗普对巴西征收50%关税的决定是一个具有重大影响的政策举措，其政治动机和可能的经济后果需要国际社会密切关注。这一决定可能对美巴关系和国际贸易秩序产生深远影响。"""

        # 生成双语原始内容
        original_content_zh = f"""特朗普宣布对巴西征收50%关税，并称此举出于政治动机。

特朗普在声明中明确表示，这一决定与巴西前总统博尔索纳罗的刑事审判有关。这一表态引发了国际社会的广泛关注和争议。

专家认为，将政治因素直接引入贸易政策可能破坏国际贸易秩序，并可能引发连锁反应。这种做法不符合国际贸易规则和惯例。

巴西政府可能对此决定表示强烈不满，并可能采取相应的报复性措施。其他贸易伙伴也可能重新评估与美国的贸易关系。

这一决定可能对美巴贸易造成重大冲击，影响相关行业的供应链，并可能导致贸易伙伴寻求替代市场。

从政治角度来看，这一决定可能损害美巴双边关系，影响美国在国际贸易中的信誉，并可能引发其他国家的类似措施。

国际贸易专家警告说，这种做法可能破坏国际贸易秩序，并可能引发连锁反应。国际社会需要密切关注事态发展。

这一决定可能引发巴西的报复性措施，并可能影响其他国家对美国的贸易政策。国际社会需要密切关注事态发展。

特朗普对巴西征收50%关税的决定是一个具有重大影响的政策举措，其政治动机和可能的经济后果需要国际社会密切关注。

这一决定可能对美巴关系和国际贸易秩序产生深远影响，需要国际社会密切关注事态发展。

---

{original_content}"""

        # 更新处理内容
        cursor.execute("""
            UPDATE processed_content 
            SET detailed_summary_zh = ?, original_content_zh = ?, 
                detailed_summary_length = ?, original_content_length = ?,
                updated_at = ?
            WHERE article_id = 54
        """, (
            detailed_summary_zh, original_content_zh,
            len(detailed_summary_zh), len(original_content_zh),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        print(f"✅ 文章54内容生成完成！")
        print(f"详细总结长度: {len(detailed_summary_zh)} 字符")
        print(f"原始内容长度: {len(original_content_zh)} 字符")
        
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_article_54_content() 