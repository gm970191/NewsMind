#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def fix_summary_and_detailed():
    """修复文章122的summary_zh为简明概要，detailed_summary_zh为详细总结。"""
    
    # 简明概要（100-300字，突出要点）
    summary_zh = (
        "本文简要分析了中国邀请美国前总统特朗普参加军事阅兵式的可能性及其意义。作者认为，"
        "在纪念二战胜利80周年的重要时刻，邀请特朗普出席阅兵式不仅有助于展示中国的外交开放，"
        "也可能成为改善中美关系的契机。文章指出，这一举措虽有助于提升中国在国际社会中的形象，"
        "但也面临西方舆论批评和国际政治风险。总体来看，作者建议中国可权衡利弊，适时采取灵活外交策略。"
    )

    # 详细总结（1000字左右，结构完整）
    detailed_summary_zh = (
        "本文深入分析了中国邀请美国前总统特朗普参加军事阅兵式的可能性及其深远影响。\n\n"
        "【核心观点】\n作者认为，在纪念二战胜利80周年的重要历史时刻，邀请特朗普参加阅兵式具有重要的战略意义。"
        "这一举措既能展现中国的外交开放姿态，又可借机缓解西方对其人权记录的批评。\n\n"
        "【历史背景】\n文章回顾了二战东方战场的历史，指出中国在反法西斯战争中的巨大贡献长期被西方叙事淡化。"
        "中国军民伤亡超过2000万人，牵制并消灭了约48万日军，其战略价值不亚于欧洲战场。\n\n"
        "【外交意义】\n邀请特朗普参加阅兵式可能成为改善中美关系的契机。三国领导人（中国、美国、俄罗斯）共同观礼，"
        "客观上承认了中国在反法西斯战争中的核心地位，有助于重塑国际社会对二战东方战场的认知。\n\n"
        "【面临的挑战】\n然而，这一提议也面临诸多挑战和争议：\n1. 特朗普的出席可能引发西方媒体的强烈批评\n"
        "2. 可能被视为对某些历史观点的认可\n3. 在当前国际政治环境下存在一定风险\n\n"
        "【战略价值】\n文章认为，尽管存在风险，但邀请特朗普参加阅兵式可能是一个值得考虑的外交举措，"
        "有助于推动国际关系的和解与发展，同时展示中国对历史和解的开放态度。\n\n"
        "【结论】\n作者最终建议，在权衡利弊后，邀请特朗普参加阅兵式可能有助于缓解当前紧张的中美关系，"
        "推动国际关系的和解与发展。"
    )

    # 连接数据库
    conn = sqlite3.connect('backend/newsmind.db')
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE processed_content 
            SET summary_zh = ?, detailed_summary_zh = ?, updated_at = datetime('now')
            WHERE article_id = 122
        """, (summary_zh, detailed_summary_zh))
        conn.commit()
        print("修复完成！\n\n【简明概要】\n" + summary_zh + "\n\n【详细总结】\n" + detailed_summary_zh)
    except Exception as e:
        print(f"修复失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_summary_and_detailed() 