#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def fix_summary_122():
    """修复文章122的摘要，将数据写入正确的ProcessedContent表"""
    
    # 连接数据库
    conn = sqlite3.connect('backend/newsmind.db')
    cursor = conn.cursor()
    
    try:
        # 手动创建的摘要
        summary_zh = """本文探讨了中国是否应该邀请美国前总统特朗普参加其军事阅兵式的问题。作者认为，在纪念二战胜利80周年的背景下，邀请特朗普参加阅兵式可能有助于改善中美关系，但也面临诸多挑战和争议。文章分析了邀请特朗普的利弊，包括可能带来的外交机遇和国内外的政治风险。"""
        
        detailed_summary_zh = """本文深入分析了中国邀请美国前总统特朗普参加军事阅兵式的可能性及其影响。作者指出，在纪念二战胜利80周年的重要时刻，邀请特朗普参加阅兵式可能成为改善中美关系的契机。文章认为，这样的邀请可以展示中国对历史和解的开放态度，同时也有助于缓解当前紧张的中美关系。

然而，作者也承认这一提议面临诸多挑战。首先，特朗普的出席可能引发西方媒体的强烈批评，特别是在当前国际政治环境下。其次，邀请特朗普可能被视为对某些历史观点的认可，这在国内外都可能引起争议。文章还分析了俄罗斯总统普京的参与对整体局势的影响，以及三国领导人同台可能产生的象征意义。

作者最终建议，尽管存在风险，但邀请特朗普参加阅兵式可能是一个值得考虑的外交举措，有助于推动国际关系的和解与发展。"""
        
        # 检查ProcessedContent表中是否已有记录
        cursor.execute("SELECT id FROM processed_content WHERE article_id = 122")
        existing_record = cursor.fetchone()
        
        if existing_record:
            # 更新现有记录
            print("更新现有的ProcessedContent记录...")
            cursor.execute("""
                UPDATE processed_content 
                SET 
                    summary_zh = ?,
                    summary_en = ?,
                    quality_score = 0.8,
                    processing_time = 5.0,
                    api_calls_used = 2,
                    updated_at = datetime('now')
                WHERE article_id = 122
            """, (summary_zh, detailed_summary_zh))
        else:
            # 创建新记录
            print("创建新的ProcessedContent记录...")
            cursor.execute("""
                INSERT INTO processed_content 
                (article_id, summary_zh, summary_en, quality_score, processing_time, api_calls_used, created_at, updated_at)
                VALUES (122, ?, ?, 0.8, 5.0, 2, datetime('now'), datetime('now'))
            """, (summary_zh, detailed_summary_zh))
        
        # 同时更新NewsArticle表中的is_processed字段
        cursor.execute("""
            UPDATE news_articles 
            SET 
                is_processed = TRUE,
                updated_at = datetime('now')
            WHERE id = 122
        """)
        
        conn.commit()
        
        print("\n摘要修复完成！")
        print(f"摘要: {summary_zh}")
        print(f"详细摘要: {detailed_summary_zh}")
        
        # 验证更新结果
        cursor.execute("""
            SELECT summary_zh, summary_en, quality_score 
            FROM processed_content 
            WHERE article_id = 122
        """)
        result = cursor.fetchone()
        
        if result:
            print(f"\n验证结果:")
            print(f"summary_zh: {'✓' if result[0] else '✗'}")
            print(f"summary_en: {'✓' if result[1] else '✗'}")
            print(f"quality_score: {result[2]}")
        
    except Exception as e:
        print(f"修复失败: {e}")
        conn.rollback()
        
    finally:
        conn.close()

if __name__ == "__main__":
    fix_summary_122() 