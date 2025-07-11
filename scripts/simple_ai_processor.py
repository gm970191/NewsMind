#!/usr/bin/env python3
"""
简化的AI处理脚本
直接使用DeepSeek API进行翻译和总结
"""
import asyncio
import sqlite3
import sys
import os
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv('backend/.env')

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"


class SimpleAIProcessor:
    """简化的AI处理器"""
    
    def __init__(self):
        if not DEEPSEEK_API_KEY:
            raise ValueError("DEEPSEEK_API_KEY not found in environment variables")
    
    async def translate_to_chinese(self, text: str) -> Optional[str]:
        """翻译为中文"""
        try:
            headers = {
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的翻译助手。请将以下内容翻译成中文，保持原文的意思和风格。直接返回翻译结果，不要添加任何解释。"
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 4000
            }
            
            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content'].strip()
            
            return None
            
        except Exception as e:
            print(f"翻译失败: {e}")
            return None
    
    async def generate_summary_zh(self, text: str) -> Optional[str]:
        """生成中文摘要"""
        try:
            headers = {
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": """你是一个专业的新闻编辑，请为以下新闻内容生成一个详细、准确的中文摘要。

要求：
1. 摘要长度控制在200-300字之间
2. 突出新闻的核心信息、关键事实和重要细节
3. 使用客观、准确的语言
4. 保持新闻的时效性和重要性
5. 包含新闻的背景信息、主要人物、时间地点等关键要素
6. 避免主观评价和推测
7. 确保摘要内容完整，能够帮助读者快速了解新闻全貌

请直接返回摘要内容，不要添加任何额外的说明或格式。"""
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 4000
            }
            
            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content'].strip()
            
            return None
            
        except Exception as e:
            print(f"生成摘要失败: {e}")
            return None
    
    async def generate_summary_en(self, text: str) -> Optional[str]:
        """生成英文摘要"""
        try:
            headers = {
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": """You are a professional news editor. Please generate a detailed and accurate English summary for the following news content.

Requirements:
1. Summary length should be between 200-300 words
2. Highlight the core information, key facts, and important details of the news
3. Use objective and accurate language
4. Maintain the timeliness and importance of the news
5. Include background information, key figures, time and location, and other essential elements
6. Avoid subjective evaluations and speculations
7. Ensure the summary is comprehensive and helps readers quickly understand the full picture of the news

Please return the summary content directly, without any additional explanations or formatting."""
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 4000
            }
            
            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content'].strip()
            
            return None
            
        except Exception as e:
            print(f"生成英文摘要失败: {e}")
            return None


class AIProcessorButton:
    """AI处理按钮功能"""
    
    def __init__(self):
        self.ai_processor = SimpleAIProcessor()
    
    def check_processing_status(self, article_id: int) -> Dict[str, any]:
        """检查文章的处理状态"""
        try:
            conn = sqlite3.connect('backend/newsmind.db')
            cursor = conn.cursor()
            
            # 获取文章信息
            cursor.execute("""
                SELECT title, content, language, is_processed 
                FROM news_articles 
                WHERE id = ?
            """, (article_id,))
            article = cursor.fetchone()
            
            if not article:
                return {"error": "文章不存在"}
            
            title, content, language, is_processed = article
            
            # 获取AI处理结果
            cursor.execute("""
                SELECT summary_zh, summary_en, translation_zh 
                FROM processed_content 
                WHERE article_id = ?
            """, (article_id,))
            processed = cursor.fetchone()
            
            conn.close()
            
            # 分析状态
            has_summary_zh = processed and processed[0] and len(processed[0].strip()) > 0
            has_summary_en = processed and processed[1] and len(processed[1].strip()) > 0
            has_translation = processed and processed[2] and len(processed[2].strip()) > 0
            
            needs_summary = not has_summary_zh or not has_summary_en
            needs_translation = language != 'zh' and not has_translation
            
            return {
                "article_id": article_id,
                "title": title,
                "language": language,
                "is_processed": is_processed,
                "has_summary_zh": has_summary_zh,
                "has_summary_en": has_summary_en,
                "has_translation": has_translation,
                "needs_summary": needs_summary,
                "needs_translation": needs_translation,
                "needs_processing": needs_summary or needs_translation
            }
            
        except Exception as e:
            return {"error": f"检查状态失败: {str(e)}"}
    
    async def process_article_by_id(self, article_id: int) -> Dict[str, any]:
        """处理指定文章ID"""
        try:
            print(f"🔍 检查文章 {article_id} 的处理状态...")
            
            # 检查文章是否存在
            conn = sqlite3.connect('backend/newsmind.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT title, content, language, is_processed 
                FROM news_articles 
                WHERE id = ?
            """, (article_id,))
            article = cursor.fetchone()
            
            if not article:
                return {"success": False, "message": "文章不存在"}
            
            title, content, language, is_processed = article
            
            # 检查当前处理状态
            status = self.check_processing_status(article_id)
            print(f"📊 当前状态: {status}")
            
            # 根据缺失内容进行处理
            if status['needs_summary'] or status['needs_translation']:
                print("🚀 开始AI处理...")
                
                start_time = time.time()
                
                # 生成摘要
                summary_zh = None
                summary_en = None
                if status['needs_summary']:
                    print("📝 生成中文摘要...")
                    summary_zh = await self.ai_processor.generate_summary_zh(content)
                    
                    print("📝 生成英文摘要...")
                    summary_en = await self.ai_processor.generate_summary_en(content)
                
                # 翻译
                translation_zh = None
                if status['needs_translation']:
                    print("🌐 翻译为中文...")
                    translation_zh = await self.ai_processor.translate_to_chinese(content)
                
                processing_time = time.time() - start_time
                
                # 保存处理结果
                if summary_zh or summary_en or translation_zh:
                    # 检查是否已有处理记录
                    cursor.execute("SELECT id FROM processed_content WHERE article_id = ?", (article_id,))
                    existing = cursor.fetchone()
                    
                    if existing:
                        # 更新现有记录
                        cursor.execute("""
                            UPDATE processed_content 
                            SET summary_zh = COALESCE(?, summary_zh),
                                summary_en = COALESCE(?, summary_en),
                                translation_zh = COALESCE(?, translation_zh),
                                processing_time = ?,
                                updated_at = ?
                            WHERE article_id = ?
                        """, (summary_zh, summary_en, translation_zh, processing_time, datetime.now().isoformat(), article_id))
                    else:
                        # 创建新记录
                        cursor.execute("""
                            INSERT INTO processed_content (
                                article_id, summary_zh, summary_en, translation_zh, 
                                processing_time, created_at, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (article_id, summary_zh, summary_en, translation_zh, processing_time, 
                              datetime.now().isoformat(), datetime.now().isoformat()))
                    
                    # 更新文章状态
                    cursor.execute("""
                        UPDATE news_articles 
                        SET is_processed = 1, updated_at = ? 
                        WHERE id = ?
                    """, (datetime.now().isoformat(), article_id))
                    
                    conn.commit()
                    conn.close()
                    
                    # 重新检查状态
                    new_status = self.check_processing_status(article_id)
                    return {
                        "success": True,
                        "message": "AI处理完成",
                        "old_status": status,
                        "new_status": new_status,
                        "processing_time": processing_time
                    }
                else:
                    conn.close()
                    return {"success": False, "message": "AI处理失败，未生成任何内容"}
            else:
                conn.close()
                return {"success": True, "message": "文章已完全处理", "status": status}
                
        except Exception as e:
            print(f"❌ 处理失败: {e}")
            return {"success": False, "message": f"处理失败: {str(e)}"}
    
    def get_processing_stats(self) -> Dict[str, any]:
        """获取处理统计信息"""
        try:
            conn = sqlite3.connect('backend/newsmind.db')
            cursor = conn.cursor()
            
            # 总文章数
            cursor.execute("SELECT COUNT(*) FROM news_articles")
            total_articles = cursor.fetchone()[0]
            
            # 已处理文章数
            cursor.execute("SELECT COUNT(*) FROM news_articles WHERE is_processed = 1")
            processed_articles = cursor.fetchone()[0]
            
            # 未处理文章数
            cursor.execute("SELECT COUNT(*) FROM news_articles WHERE is_processed = 0")
            unprocessed_articles = cursor.fetchone()[0]
            
            # 有AI处理记录的文章数
            cursor.execute("SELECT COUNT(*) FROM processed_content")
            ai_processed = cursor.fetchone()[0]
            
            # 语言分布
            cursor.execute("""
                SELECT language, COUNT(*) 
                FROM news_articles 
                GROUP BY language
            """)
            language_dist = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                "total_articles": total_articles,
                "processed_articles": processed_articles,
                "unprocessed_articles": unprocessed_articles,
                "ai_processed": ai_processed,
                "processing_rate": round(processed_articles / total_articles * 100, 2) if total_articles > 0 else 0,
                "language_distribution": language_dist
            }
            
        except Exception as e:
            return {"error": f"获取统计失败: {str(e)}"}


async def main():
    """主函数 - 用于测试"""
    try:
        processor = AIProcessorButton()
        
        print("🤖 AI处理按钮功能测试")
        print("=" * 50)
        
        # 获取统计信息
        stats = processor.get_processing_stats()
        print("📊 处理统计:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print("\n" + "=" * 50)
        
        # 测试处理单篇文章（如果有未处理的文章）
        if stats.get('unprocessed_articles', 0) > 0:
            print("🔍 测试处理单篇文章...")
            # 获取第一个未处理的文章
            conn = sqlite3.connect('backend/newsmind.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM news_articles WHERE is_processed = 0 LIMIT 1")
            result = cursor.fetchone()
            conn.close()
            
            if result:
                article_id = result[0]
                result = await processor.process_article_by_id(article_id)
                print(f"处理结果: {result}")
        
        print("\n✅ 测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 