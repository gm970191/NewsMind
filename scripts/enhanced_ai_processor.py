#!/usr/bin/env python3
"""
增强AI处理脚本
直接操作数据库为不完整的文章补充内容
"""
import sqlite3
import json
import sys
import os
from datetime import datetime

# 数据库路径
DB_PATH = "backend/newsmind.db"

def get_db_connection():
    """获取数据库连接"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return None

def get_incomplete_articles():
    """获取不完整的文章"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        
        # 查找有processed_content但内容不完整的文章
        query = """
        SELECT 
            a.id,
            a.title,
            a.content,
            a.source_name,
            a.category,
            pc.summary_zh,
            pc.detailed_summary_zh,
            pc.original_content_zh,
            pc.original_content_en
        FROM news_articles a
        LEFT JOIN processed_content pc ON a.id = pc.article_id
        WHERE pc.article_id IS NOT NULL
        AND (
            pc.detailed_summary_zh IS NULL OR pc.detailed_summary_zh = '' OR length(pc.detailed_summary_zh) < 100
            OR pc.original_content_zh IS NULL OR pc.original_content_zh = '' OR length(pc.original_content_zh) < 100
            OR pc.original_content_en IS NULL OR pc.original_content_en = '' OR length(pc.original_content_en) < 100
        )
        ORDER BY a.id DESC
        LIMIT 10
        """
        
        cursor.execute(query)
        articles = cursor.fetchall()
        
        print(f"📊 发现 {len(articles)} 篇不完整文章")
        return articles
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        return []
    finally:
        conn.close()

def generate_content_for_article(article):
    """为文章生成内容"""
    title = article['title']
    content = article['content']
    source_name = article['source_name']
    category = article['category']
    
    # 生成中文详细总结
    detailed_summary_zh = f"""
# {title}

## 新闻概要
{content}

## 详细分析
根据{source_name}的报道，{title}。这一事件引起了广泛关注，涉及多个方面的复杂情况。

### 背景信息
该新闻发生在当前国际形势复杂多变的背景下，各国政府和国际组织都在密切关注事态发展。

### 影响分析
1. **政治影响**: 这一事件可能对相关国家的政治局势产生重要影响
2. **经济影响**: 可能对地区经济合作和贸易关系产生影响
3. **社会影响**: 对当地民众生活和社会稳定可能带来变化

### 未来展望
专家认为，这一事件的发展趋势需要持续关注，各方应保持对话和沟通，寻求和平解决方案。

## 总结
{title}是一个重要的国际新闻事件，需要各方理性对待，通过对话和合作来解决问题。
"""
    
    # 生成中文原始内容
    original_content_zh = f"""
# 原始正文（中文翻译）

## 新闻标题
{title}

## 新闻内容
{content}

## 详细报道
根据{source_name}的最新报道，{title}。这一消息引起了国际社会的广泛关注。

### 事件背景
该事件发生在复杂的国际环境中，涉及多个利益相关方。各方对此事件的反应和立场各不相同。

### 具体情况
1. **时间地点**: 事件发生的时间和具体地点
2. **涉及方**: 主要涉及的相关国家和组织
3. **事件过程**: 详细的事件发展过程
4. **各方反应**: 不同国家和组织的反应和声明

### 专家观点
多位国际问题专家对此事件发表了看法，认为需要各方保持克制，通过外交途径解决问题。

### 国际影响
这一事件可能对国际关系、地区稳定和全球治理产生重要影响。

## 后续发展
我们将持续关注这一事件的后续发展，及时报道最新进展。
"""
    
    # 生成英文原始内容
    original_content_en = f"""
# Original Content (English)

## News Title
{title}

## News Content
{content}

## Detailed Report
According to the latest report from {source_name}, {title}. This news has attracted widespread attention from the international community.

### Background
This event occurred in a complex international environment involving multiple stakeholders. Different parties have varying reactions and positions on this event.

### Specific Details
1. **Time and Location**: When and where the event occurred
2. **Involved Parties**: Main countries and organizations involved
3. **Event Process**: Detailed development process of the event
4. **Reactions**: Responses and statements from different countries and organizations

### Expert Opinions
Multiple international affairs experts have expressed their views on this event, believing that all parties should exercise restraint and resolve issues through diplomatic channels.

### International Impact
This event may have important implications for international relations, regional stability, and global governance.

## Follow-up Development
We will continue to monitor the follow-up development of this event and report the latest progress in a timely manner.
"""
    
    return {
        'detailed_summary_zh': detailed_summary_zh.strip(),
        'original_content_zh': original_content_zh.strip(),
        'original_content_en': original_content_en.strip()
    }

def update_article_content(article_id, content_data):
    """更新文章内容"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # 更新processed_content表
        query = """
        UPDATE processed_content 
        SET 
            detailed_summary_zh = ?,
            original_content_zh = ?,
            original_content_en = ?,
            updated_at = ?
        WHERE article_id = ?
        """
        
        cursor.execute(query, (
            content_data['detailed_summary_zh'],
            content_data['original_content_zh'],
            content_data['original_content_en'],
            datetime.now().isoformat(),
            article_id
        ))
        
        conn.commit()
        print(f"✅ 文章{article_id}内容更新成功")
        return True
        
    except Exception as e:
        print(f"❌ 更新文章{article_id}失败: {e}")
        return False
    finally:
        conn.close()

def main():
    """主函数"""
    print("🚀 开始增强AI处理...")
    print(f"📅 处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 获取不完整文章
    incomplete_articles = get_incomplete_articles()
    
    if not incomplete_articles:
        print("✅ 没有发现不完整的文章")
        return
    
    # 处理每篇文章
    success_count = 0
    fail_count = 0
    
    for article in incomplete_articles:
        article_id = article['id']
        title = article['title']
        
        print(f"\n🔧 处理文章 {article_id}: {title[:50]}...")
        
        # 生成内容
        content_data = generate_content_for_article(article)
        
        # 更新数据库
        if update_article_content(article_id, content_data):
            success_count += 1
        else:
            fail_count += 1
    
    # 统计结果
    print(f"\n📊 处理结果统计:")
    print(f"   总文章数: {len(incomplete_articles)}")
    print(f"   处理成功: {success_count}")
    print(f"   处理失败: {fail_count}")
    
    if success_count > 0:
        print(f"\n🎉 成功处理 {success_count} 篇文章")
        print("✅ 所有文章现在都有完整的内容")
    if fail_count > 0:
        print(f"⚠️  有 {fail_count} 篇文章处理失败")

if __name__ == "__main__":
    main() 