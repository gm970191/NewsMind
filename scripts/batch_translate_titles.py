#!/usr/bin/env python3
"""
批量翻译新闻标题脚本
使用本地LM Studio翻译translated_title为空的记录
"""

import sys
import os
import sqlite3
import requests
import json
import time
from typing import List, Dict, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_lmstudio_connection():
    """测试LM Studio连接"""
    try:
        response = requests.get("http://127.0.0.1:1234/v1/models", timeout=5)
        if response.status_code == 200:
            models = response.json()
            print(f"✅ LM Studio连接成功，可用模型: {[m['id'] for m in models.get('data', [])]}")
            return True
        else:
            print(f"❌ LM Studio连接失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ LM Studio连接失败: {e}")
        return False

def translate_title_with_lmstudio(title: str, language: str) -> Optional[str]:
    """使用LM Studio翻译标题"""
    if language in ['zh', 'zh-CN']:
        return title  # 中文不需要翻译
    
    try:
        # 构建翻译提示
        prompt = f"""请将以下英文新闻标题翻译成中文，只返回翻译结果，不要添加任何解释：

英文标题：{title}

中文翻译："""
        
        payload = {
            "model": "qwen2-0.5b-instruct",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 100
        }
        
        response = requests.post(
            "http://127.0.0.1:1234/v1/chat/completions",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            translated_title = result['choices'][0]['message']['content'].strip()
            # 清理翻译结果
            translated_title = translated_title.replace('中文翻译：', '').strip()
            return translated_title
        else:
            print(f"❌ 翻译请求失败，状态码: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 翻译失败: {e}")
        return None

def get_untranslated_articles(db_path: str, limit: int = 50) -> List[Dict]:
    """获取未翻译的文章"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, title, original_language, original_title
        FROM news_articles 
        WHERE (translated_title IS NULL OR translated_title = '') 
        AND (original_language != 'zh' AND original_language != 'zh-CN')
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    
    articles = []
    for row in cursor.fetchall():
        articles.append({
            'id': row[0],
            'title': row[1],
            'original_language': row[2],
            'original_title': row[3]
        })
    
    conn.close()
    return articles

def update_translated_title(db_path: str, article_id: int, translated_title: str):
    """更新翻译后的标题"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE news_articles 
        SET translated_title = ?, 
            is_title_translated = TRUE,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (translated_title, article_id))
    
    conn.commit()
    conn.close()

def batch_translate_titles(db_path: str = "newsmind.db", batch_size: int = 20):
    """批量翻译标题"""
    print("🚀 开始批量翻译新闻标题...")
    
    # 测试LM Studio连接
    if not test_lmstudio_connection():
        print("❌ LM Studio未启动或连接失败，请确保LM Studio在 http://127.0.0.1:1234 运行")
        return
    
    # 获取需要翻译的文章
    articles = get_untranslated_articles(db_path, batch_size)
    print(f"📝 找到 {len(articles)} 篇文章需要翻译")
    
    if not articles:
        print("✅ 所有文章都已翻译完成")
        return
    
    success_count = 0
    failed_count = 0
    
    for i, article in enumerate(articles, 1):
        print(f"\n📰 处理第 {i}/{len(articles)} 篇文章:")
        print(f"   ID: {article['id']}")
        print(f"   原文: {article['title']}")
        print(f"   语言: {article['original_language']}")
        
        # 翻译标题
        translated_title = translate_title_with_lmstudio(article['title'], article['original_language'])
        
        if translated_title:
            # 更新数据库
            update_translated_title(db_path, article['id'], translated_title)
            print(f"   ✅ 翻译: {translated_title}")
            success_count += 1
        else:
            print(f"   ❌ 翻译失败")
            failed_count += 1
        
        # 添加延迟避免请求过快
        time.sleep(1)
    
    print(f"\n🎉 批量翻译完成!")
    print(f"   ✅ 成功: {success_count}")
    print(f"   ❌ 失败: {failed_count}")
    print(f"   📊 成功率: {success_count/(success_count+failed_count)*100:.1f}%")

def verify_translation_results(db_path: str = "newsmind.db"):
    """验证翻译结果"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 统计翻译情况
    cursor.execute("SELECT COUNT(*) FROM news_articles")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM news_articles WHERE translated_title IS NOT NULL AND translated_title != ''")
    translated = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM news_articles WHERE is_title_translated = TRUE")
    marked_translated = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM news_articles WHERE original_language IN ('zh', 'zh-CN')")
    chinese = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n📊 翻译结果统计:")
    print(f"   总文章数: {total}")
    print(f"   有翻译标题: {translated}")
    print(f"   标记已翻译: {marked_translated}")
    print(f"   中文原文: {chinese}")
    print(f"   翻译覆盖率: {translated/total*100:.1f}%")

if __name__ == "__main__":
    print("🔧 新闻标题批量翻译工具")
    print("=" * 50)
    
    # 执行批量翻译
    batch_translate_titles(batch_size=50)
    
    # 验证结果
    verify_translation_results() 