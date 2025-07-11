#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import requests
import time

def generate_summary_with_lmstudio(text, language="中文"):
    """使用LM Studio生成摘要"""
    try:
        url = "http://localhost:1234/v1/chat/completions"
        
        prompt = f"""请为以下文本生成一个简洁的{language}摘要，突出主要观点和关键信息：

{text}

请生成一个200-300字的摘要，保持客观和准确。"""
        
        payload = {
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1000,
            "stream": False
        }
        
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        summary = result['choices'][0]['message']['content'].strip()
        
        return summary
        
    except Exception as e:
        print(f"生成摘要失败: {e}")
        return None

def update_summary_122():
    """为文章122生成摘要"""
    
    # 连接数据库
    conn = sqlite3.connect('backend/newsmind.db')
    cursor = conn.cursor()
    
    try:
        # 获取文章122的原文内容
        cursor.execute("SELECT original_content FROM news_articles WHERE id = 122")
        result = cursor.fetchone()
        
        if not result or not result[0]:
            print("未找到文章122的原文内容")
            return
        
        content = result[0]
        print(f"文章122原文内容长度: {len(content)} 字符")
        
        # 生成摘要
        print("正在生成摘要...")
        summary_zh = generate_summary_with_lmstudio(content, "中文")
        
        if summary_zh:
            print("正在生成详细摘要...")
            detailed_summary_zh = generate_summary_with_lmstudio(content, "中文")
            
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
            
            print("\n摘要生成完成！")
            print(f"摘要: {summary_zh}")
            print(f"详细摘要: {detailed_summary_zh}")
        else:
            print("摘要生成失败")
        
    except Exception as e:
        print(f"更新失败: {e}")
        conn.rollback()
        
    finally:
        conn.close()

if __name__ == "__main__":
    update_summary_122() 