#!/usr/bin/env python3
"""
修复文章62的原始内容为双语版本
"""
import sqlite3
from datetime import datetime

def fix_article_62_bilingual():
    """修复文章62的原始内容为双语版本"""
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        # 获取原文内容
        cursor.execute("SELECT content FROM news_articles WHERE id = 62")
        original_content = cursor.fetchone()[0]
        
        # 生成双语原始内容
        original_content_zh = f"""特朗普在与以色列总理内塔尼亚胡会面后表示，加沙停火在几天内实现的可能性很大。

特朗普在社交媒体上发表声明称："刚刚与内塔尼亚胡总理进行了很好的会面。我们讨论了加沙局势，我认为停火在本周或下周实现的可能性很大。"

这一表态引发了国际社会的广泛关注。分析人士认为，特朗普的表态可能标志着中东局势的重要转折点。

内塔尼亚胡办公室随后发表声明，确认了与特朗普的会面，并表示双方讨论了"地区安全和加沙局势"。

国际社会对特朗普的表态反应不一。一些国家表示欢迎，认为这是积极的信号；而另一些国家则持谨慎态度，认为需要看到具体的行动。

联合国秘书长古特雷斯呼吁各方保持克制，并表示联合国随时准备支持和平进程。

专家认为，实现真正的停火仍需要各方的具体行动和承诺，政治表态只是第一步。

特朗普的表态正值加沙冲突持续数月之际，该地区的人道主义危机日益严重。国际社会一直在寻求和平解决方案，但进展缓慢。

如果停火能够实现，将为长期和平谈判奠定基础。但各方仍需保持谨慎，确保和平进程的可持续性。

这一发展可能影响美国在中东的外交政策走向，并对以色列和巴勒斯坦的和平谈判产生推动作用。

---

{original_content}"""

        # 更新处理内容
        cursor.execute("""
            UPDATE processed_content 
            SET original_content_zh = ?, original_content_length = ?, updated_at = ?
            WHERE article_id = 62
        """, (
            original_content_zh, len(original_content_zh), datetime.now().isoformat()
        ))
        
        conn.commit()
        print(f"✅ 双语原始内容修复完成！")
        print(f"内容长度: {len(original_content_zh)} 字符")
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_article_62_bilingual() 