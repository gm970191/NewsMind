#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def update_manual_summary_122():
    """为文章122手动添加摘要"""
    
    # 连接数据库
    conn = sqlite3.connect('backend/newsmind.db')
    cursor = conn.cursor()
    
    try:
        # 手动创建的摘要
        summary_zh = """本文探讨了中国是否应该邀请美国前总统特朗普参加其军事阅兵式的问题。作者认为，在纪念二战胜利80周年的背景下，邀请特朗普参加阅兵式可能有助于改善中美关系，但也面临诸多挑战和争议。文章分析了邀请特朗普的利弊，包括可能带来的外交机遇和国内外的政治风险。"""
        
        detailed_summary_zh = """本文深入分析了中国邀请美国前总统特朗普参加军事阅兵式的可能性及其影响。作者指出，在纪念二战胜利80周年的重要时刻，邀请特朗普参加阅兵式可能成为改善中美关系的契机。文章认为，这样的邀请可以展示中国对历史和解的开放态度，同时也有助于缓解当前紧张的中美关系。

然而，作者也承认这一提议面临诸多挑战。首先，特朗普的出席可能引发西方媒体的强烈批评，特别是在当前国际政治环境下。其次，邀请特朗普可能被视为对某些历史观点的认可，这在国内外都可能引起争议。文章还分析了俄罗斯总统普京的参与对整体局势的影响，以及三国领导人同台可能产生的象征意义。

作者最终建议，尽管存在风险，但邀请特朗普参加阅兵式可能是一个值得考虑的外交举措，有助于推动国际关系的和解与发展。"""
        
        # 更新数据库
        print("正在更新数据库...")
        cursor.execute("""
            UPDATE news_articles 
            SET 
                summary_zh = ?,
                detailed_summary_zh = ?,
                updated_at = datetime('now')
            WHERE id = 122
        """, (summary_zh, detailed_summary_zh))
        
        conn.commit()
        
        print("\n摘要更新完成！")
        print(f"摘要: {summary_zh}")
        print(f"详细摘要: {detailed_summary_zh}")
        
    except Exception as e:
        print(f"更新失败: {e}")
        conn.rollback()
        
    finally:
        conn.close()

if __name__ == "__main__":
    update_manual_summary_122() 