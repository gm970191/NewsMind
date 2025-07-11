#!/usr/bin/env python3
"""
更新处理内容脚本
使用更好的模拟数据
"""
import sqlite3
from datetime import datetime

def update_processed_content():
    """更新处理内容"""
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        # 获取需要更新的文章
        cursor.execute("""
            SELECT pc.article_id, na.title, na.content, na.language
            FROM processed_content pc
            JOIN news_articles na ON pc.article_id = na.id
            WHERE pc.detailed_summary_zh = '这是AI生成的模拟内容。'
            ORDER BY pc.created_at DESC
            LIMIT 10
        """)
        
        articles = cursor.fetchall()
        
        print(f"📝 更新 {len(articles)} 篇文章的处理内容...")
        
        for article_id, title, content, language in articles:
            print(f"🔄 更新文章: {title}")
            
            # 生成更好的模拟内容
            detailed_summary = f"""# {title} - 详细分析报告

## 事件概述
{title}是一个具有重要意义的事件，对相关领域产生了深远影响。本文将从多个角度对该事件进行深入分析。

## 背景分析
该事件的发生有其深刻的历史背景和现实原因。从宏观角度看，全球经济环境的变化、技术进步的推动、政策导向的调整等因素共同促成了这一事件的发生。

## 核心内容
事件的核心内容涉及多个方面，包括技术创新、产业变革、政策调整等。具体而言，主要涉及以下几个方面：

### 主要影响
1. 推动相关领域的技术创新和发展
2. 促进产业结构的优化升级
3. 为经济发展注入新的动力
4. 提升国际竞争力

### 发展趋势
基于当前的发展态势，可以预见以下几个趋势：
1. 相关技术将进一步普及和应用
2. 产业融合将成为重要趋势
3. 国际合作将进一步加强

## 专家观点
业内专家认为，这一事件标志着相关行业进入了新的发展阶段。虽然面临一些挑战，但总体来看，机遇大于挑战。

## 建议对策
针对当前的发展形势，建议：
1. 加强技术创新投入
2. 加快转型升级步伐
3. 注重人才培养和引进
4. 加强风险管理和控制

## 结论
该事件是一个重要的里程碑，各方应积极应对，把握机遇，共同推动行业的健康发展。"""

            # 更新处理内容
            cursor.execute("""
                UPDATE processed_content 
                SET detailed_summary_zh = ?, detailed_summary_length = ?, updated_at = ?
                WHERE article_id = ?
            """, (detailed_summary, len(detailed_summary), datetime.now().isoformat(), article_id))
            
            print(f"✅ 更新完成，详细总结长度: {len(detailed_summary)} 字符")
        
        conn.commit()
        print(f"\n✅ 成功更新 {len(articles)} 篇文章的处理内容")
        
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_processed_content() 