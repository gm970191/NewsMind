#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def recreate_article_122():
    """重新创建文章122"""
    
    # 连接数据库
    conn = sqlite3.connect('backend/newsmind.db')
    cursor = conn.cursor()
    
    try:
        # 检查是否已存在文章122
        cursor.execute("SELECT id FROM news_articles WHERE id = 122")
        if cursor.fetchone():
            print("文章122已存在")
            return
        
        # 重新创建文章122
        article_data = {
            'id': 122,
            'original_title': 'China Should Invite Trump to Its Military Parade',
            'translated_title': '中国应该邀请特朗普参加军事阅兵',
            'original_content': 'The 80th anniversary of the global victory over fascism offers a chance to change narratives. Imagine this: U.S. President Donald Trump and Russian President Vladimir Putin stand on either side of Chinese President Xi Jinping atop Beijing\'s Tiananmen Tower, watching a Chinese military parade. What would that image evoke? Certainly a political storm and a wave of harsh criticism from Western media directed at Trump. But it might also be a rare chance for diplomacy.',
            'translated_content': '80周年全球反法西斯胜利的机会提供了改变叙事的契机。想象一下：美国总统唐纳德·特朗普和俄罗斯总统弗拉基米尔·普京站在位于北京天安门广场的中国总理习近平一侧，观看一场中国军队表演。那幅画面会引发什么？当然是一场政治风暴和西方媒体对特朗普的一阵猛烈批评。但这种罕见的机会也可能是一种外交机会。',
            'source_url': 'https://foreignpolicy.com/2025/07/09/trump-china-world-war-2-putin-military-parade/',
            'source_id': 18,
            'source_name': 'Foreign Policy',
            'original_language': 'en',
            'is_title_translated': True,
            'is_content_translated': True,
            'is_processed': True,
            'category': '政治',
            'quality_score': 0.9,
            'translation_quality_score': 0.9
        }
        
        # 插入文章
        cursor.execute("""
            INSERT INTO news_articles (
                id, original_title, translated_title, original_content, translated_content,
                source_url, source_id, source_name, original_language, is_title_translated,
                is_content_translated, is_processed, category, quality_score, translation_quality_score,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (
            article_data['id'], article_data['original_title'], article_data['translated_title'],
            article_data['original_content'], article_data['translated_content'], article_data['source_url'],
            article_data['source_id'], article_data['source_name'], article_data['original_language'],
            article_data['is_title_translated'], article_data['is_content_translated'], article_data['is_processed'],
            article_data['category'], article_data['quality_score'], article_data['translation_quality_score']
        ))
        
        conn.commit()
        
        print("文章122重新创建成功！")
        print(f"标题: {article_data['translated_title']}")
        print(f"原文内容长度: {len(article_data['original_content'])} 字符")
        print(f"翻译内容长度: {len(article_data['translated_content'])} 字符")
        
        # 验证创建结果
        cursor.execute("SELECT id, translated_title FROM news_articles WHERE id = 122")
        result = cursor.fetchone()
        if result:
            print(f"验证成功: ID {result[0]}, 标题: {result[1]}")
        
    except Exception as e:
        print(f"创建失败: {e}")
        conn.rollback()
        
    finally:
        conn.close()

if __name__ == "__main__":
    recreate_article_122() 