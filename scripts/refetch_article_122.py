#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import sqlite3
import re
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
import json

def fetch_article_content(url):
    """重新获取文章内容"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"正在获取文章内容: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 针对Foreign Policy网站的内容提取
        # 查找文章标题
        title = None
        title_selectors = [
            'h1.article-title',
            'h1.title',
            '.article-header h1',
            'h1',
            '.headline'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text().strip()
                break
        
        # 查找文章内容
        content = None
        content_selectors = [
            '.article-content',
            '.post-content',
            '.entry-content',
            '.content-body',
            'article .content',
            '.article-body'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # 移除脚本和样式标签
                for script in content_elem(["script", "style"]):
                    script.decompose()
                
                # 获取所有段落文本
                paragraphs = content_elem.find_all(['p', 'h2', 'h3', 'h4'])
                content_parts = []
                
                for p in paragraphs:
                    text = p.get_text().strip()
                    if text and len(text) > 20:  # 过滤太短的段落
                        content_parts.append(text)
                
                content = '\n\n'.join(content_parts)
                break
        
        # 如果没有找到特定内容区域，尝试获取所有段落
        if not content:
            paragraphs = soup.find_all('p')
            content_parts = []
            for p in paragraphs:
                text = p.get_text().strip()
                if text and len(text) > 50:  # 过滤太短的段落
                    content_parts.append(text)
            content = '\n\n'.join(content_parts)
        
        return title, content
        
    except Exception as e:
        print(f"获取文章内容失败: {e}")
        return None, None

def translate_with_lmstudio(text, target_language="中文"):
    """使用LM Studio进行翻译"""
    try:
        url = "http://localhost:1234/v1/chat/completions"
        
        prompt = f"""请将以下英文文本翻译成{target_language}，保持原文的意思和风格：

{text}

请只返回翻译结果，不要添加任何解释或额外内容。"""
        
        payload = {
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 4000,
            "stream": False
        }
        
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        translated_text = result['choices'][0]['message']['content'].strip()
        
        return translated_text
        
    except Exception as e:
        print(f"翻译失败: {e}")
        return None

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
        
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        summary = result['choices'][0]['message']['content'].strip()
        
        return summary
        
    except Exception as e:
        print(f"生成摘要失败: {e}")
        return None

def update_article_122():
    """更新文章122的内容"""
    
    # 连接数据库
    conn = sqlite3.connect('backend/newsmind.db')
    cursor = conn.cursor()
    
    try:
        # 获取文章122的URL
        cursor.execute("SELECT source_url FROM news_articles WHERE id = 122")
        result = cursor.fetchone()
        
        if not result:
            print("未找到文章122")
            return
        
        source_url = result[0]
        print(f"文章122的URL: {source_url}")
        
        # 重新获取文章内容
        title, content = fetch_article_content(source_url)
        
        if not content:
            print("无法获取文章内容")
            return
        
        print(f"\n获取到的标题: {title}")
        print(f"获取到的内容长度: {len(content)} 字符")
        print(f"内容预览: {content[:200]}...")
        
        # 翻译标题
        print("\n正在翻译标题...")
        translated_title = translate_with_lmstudio(title, "中文")
        
        # 翻译内容
        print("正在翻译内容...")
        # 分段翻译，避免内容过长
        content_parts = content.split('\n\n')
        translated_parts = []
        
        for i, part in enumerate(content_parts):
            if len(part.strip()) > 50:  # 只翻译有意义的段落
                print(f"翻译第 {i+1}/{len(content_parts)} 段...")
                translated_part = translate_with_lmstudio(part, "中文")
                if translated_part:
                    translated_parts.append(translated_part)
                time.sleep(1)  # 避免请求过快
        
        translated_content = '\n\n'.join(translated_parts)
        
        # 生成摘要
        print("正在生成摘要...")
        summary_zh = generate_summary_with_lmstudio(content, "中文")
        
        # 生成详细摘要
        print("正在生成详细摘要...")
        detailed_summary_zh = generate_summary_with_lmstudio(content, "中文")
        
        # 更新数据库
        print("正在更新数据库...")
        cursor.execute("""
            UPDATE news_articles 
            SET 
                original_title = ?,
                translated_title = ?,
                original_content = ?,
                translated_content = ?,
                summary_zh = ?,
                detailed_summary_zh = ?,
                is_title_translated = ?,
                is_content_translated = ?,
                updated_at = datetime('now')
            WHERE id = 122
        """, (
            title,
            translated_title,
            content,
            translated_content,
            summary_zh,
            detailed_summary_zh,
            True if translated_title else False,
            True if translated_content else False
        ))
        
        conn.commit()
        
        print("\n更新完成！")
        print(f"原文标题: {title}")
        print(f"翻译标题: {translated_title}")
        print(f"原文内容长度: {len(content)} 字符")
        print(f"翻译内容长度: {len(translated_content)} 字符")
        print(f"摘要: {summary_zh}")
        
    except Exception as e:
        print(f"更新失败: {e}")
        conn.rollback()
        
    finally:
        conn.close()

if __name__ == "__main__":
    update_article_122() 