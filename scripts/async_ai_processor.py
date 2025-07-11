#!/usr/bin/env python3
"""
后台异步AI处理脚本
自动翻译和总结新闻内容
"""
import asyncio
import sqlite3
import sys
import os
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional
import logging

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv('backend/.env')
except ImportError:
    print("⚠️  python-dotenv未安装，尝试直接读取环境变量")

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ai_processor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AsyncAIProcessor:
    """异步AI处理器"""
    
    def __init__(self):
        if not DEEPSEEK_API_KEY:
            raise ValueError("DEEPSEEK_API_KEY not found in environment variables")
        self.api_key = DEEPSEEK_API_KEY
        self.api_url = DEEPSEEK_API_URL
        self.db_path = "backend/newsmind.db"
    
    async def process_unprocessed_articles(self, max_articles: int = 20):
        """处理未处理的文章"""
        print("🤖 开始后台AI处理...")
        print("=" * 60)
        
        # 获取未处理的文章
        articles = self.get_unprocessed_articles(max_articles)
        
        if not articles:
            print("✅ 没有需要处理的文章")
            return
        
        print(f"📝 找到 {len(articles)} 篇未处理文章")
        
        # 并发处理文章
        tasks = []
        for article in articles:
            task = asyncio.create_task(self.process_single_article(article))
            tasks.append(task)
        
        # 等待所有任务完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 统计结果
        success_count = sum(1 for r in results if r is True)
        failed_count = len(results) - success_count
        
        print(f"\n📊 AI处理完成:")
        print(f"   ✅ 成功处理: {success_count} 篇")
        print(f"   ❌ 处理失败: {failed_count} 篇")
        print(f"   📈 成功率: {success_count/len(results)*100:.1f}%")
    
    def get_unprocessed_articles(self, limit: int) -> List[Dict]:
        """获取未处理的文章"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, title, content, language, source_name, category
                FROM news_articles 
                WHERE is_processed = 0
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            
            articles = []
            for row in cursor.fetchall():
                articles.append({
                    'id': row[0],
                    'title': row[1],
                    'content': row[2],
                    'language': row[3],
                    'source_name': row[4],
                    'category': row[5]
                })
            
            return articles
            
        finally:
            conn.close()
    
    async def process_single_article(self, article: Dict) -> bool:
        """处理单篇文章"""
        try:
            article_id = article['id']
            print(f"📝 处理文章 ID:{article_id} - {article['title'][:30]}...")
            
            start_time = time.time()
            
            # 1. 翻译标题（如果原文不是中文）
            translated_title = None
            if article['language'] != 'zh':
                translated_title = await self.translate_to_chinese(article['title'])
                if translated_title:
                    print(f"      标题翻译: {article['title'][:30]}... → {translated_title[:30]}...")
                else:
                    print(f"      标题翻译失败: {article['title'][:30]}...")
            
            # 2. 生成中文摘要
            summary_zh = await self.generate_summary_zh(article['content'])
            
            # 3. 生成英文摘要
            summary_en = await self.generate_summary_en(article['content'])
            
            # 4. 生成详细中文总结
            detailed_summary_zh = await self.generate_detailed_summary_zh(article['content'])
            
            # 5. 翻译为中文（如果原文不是中文）
            translation_zh = None
            if article['language'] != 'zh':
                translation_zh = await self.translate_to_chinese(article['content'])
            
            # 6. 保存处理结果
            processing_time = time.time() - start_time
            
            success = self.save_processed_content(
                article_id, summary_zh, summary_en, translation_zh, translated_title, 
                detailed_summary_zh, processing_time
            )
            
            if success:
                # 更新文章状态为已处理
                self.update_article_status(article_id, True)
                print(f"   ✅ 文章 {article_id} 处理完成 ({processing_time:.1f}s)")
                return True
            else:
                print(f"   ❌ 文章 {article_id} 保存失败")
                return False
                
        except Exception as e:
            logger.error(f"处理文章 {article.get('id', 'unknown')} 出错: {e}")
            print(f"   ❌ 文章 {article.get('id', 'unknown')} 处理出错: {e}")
            return False
    
    async def generate_summary_zh(self, content: str) -> Optional[str]:
        """生成中文摘要"""
        try:
            # 限制内容长度
            if len(content) > 2000:
                content = content[:2000]
            
            prompt = """为以下新闻生成简洁的中文摘要，控制在150字以内，突出核心信息。直接返回摘要内容，不要添加任何格式。"""
            
            response = await self.call_deepseek_api(prompt, content)
            if response and len(response) > 20:
                return response
            return None
            
        except Exception as e:
            logger.error(f"生成中文摘要失败: {e}")
            return None
    
    async def generate_summary_en(self, content: str) -> Optional[str]:
        """生成英文摘要"""
        try:
            # 限制内容长度
            if len(content) > 2000:
                content = content[:2000]
            
            prompt = """Generate a concise English summary of the following news, within 150 words, focusing on key facts. Return only the summary content."""
            
            response = await self.call_deepseek_api(prompt, content)
            if response and len(response) > 20:
                return response
            return None
            
        except Exception as e:
            logger.error(f"生成英文摘要失败: {e}")
            return None
    
    async def generate_detailed_summary_zh(self, content: str) -> Optional[str]:
        """生成详细中文总结"""
        try:
            # 限制内容长度
            if len(content) > 2000:
                content = content[:2000]
            
            prompt = """为以下新闻生成详细的中文总结，包含事件背景、发展过程、结果影响等。直接返回总结内容，不要添加任何格式。"""
            
            response = await self.call_deepseek_api(prompt, content)
            if response and len(response) > 20:
                return response
            return None
            
        except Exception as e:
            logger.error(f"生成详细中文总结失败: {e}")
            return None
    
    async def translate_to_chinese(self, content: str) -> Optional[str]:
        """翻译为中文"""
        try:
            # 限制内容长度
            if len(content) > 2000:
                content = content[:2000]
            
            prompt = """将以下内容翻译成中文，保持原意，使用流畅的中文表达。直接返回翻译结果，不要添加任何格式。"""
            
            response = await self.call_deepseek_api(prompt, content)
            if response and len(response) > 50:
                return response
            return None
            
        except Exception as e:
            logger.error(f"翻译失败: {e}")
            return None
    
    async def call_deepseek_api(self, system_prompt: str, user_content: str) -> Optional[str]:
        """调用DeepSeek API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_content
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 1000
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content'].strip()
            
            return None
            
        except Exception as e:
            logger.error(f"DeepSeek API调用失败: {e}")
            return None
    
    def save_processed_content(self, article_id: int, summary_zh: str, summary_en: str, 
                             translation_zh: str, translated_title: str, detailed_summary_zh: str, processing_time: float) -> bool:
        """保存处理结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 检查是否已存在处理结果
            cursor.execute("SELECT id FROM processed_content WHERE article_id = ?", (article_id,))
            existing = cursor.fetchone()
            
            if existing:
                # 更新现有记录
                cursor.execute("""
                    UPDATE processed_content 
                    SET summary_zh = ?, summary_en = ?, translation_zh = ?, 
                        translated_title = ?, detailed_summary_zh = ?, processing_time = ?, updated_at = ?
                    WHERE article_id = ?
                """, (summary_zh, summary_en, translation_zh, translated_title, detailed_summary_zh, processing_time, 
                     datetime.now().isoformat(), article_id))
            else:
                # 插入新记录
                cursor.execute("""
                    INSERT INTO processed_content (
                        article_id, summary_zh, summary_en, translation_zh, 
                        translated_title, detailed_summary_zh, processing_time, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (article_id, summary_zh, summary_en, translation_zh, 
                     translated_title, detailed_summary_zh, processing_time, datetime.now().isoformat(), datetime.now().isoformat()))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"保存处理结果失败: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def update_article_status(self, article_id: int, is_processed: bool):
        """更新文章处理状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE news_articles 
                SET is_processed = ?, updated_at = ?
                WHERE id = ?
            """, (1 if is_processed else 0, datetime.now().isoformat(), article_id))
            conn.commit()
            
        except Exception as e:
            logger.error(f"更新文章状态失败: {e}")
            conn.rollback()
        finally:
            conn.close()


async def main():
    """主函数"""
    try:
        processor = AsyncAIProcessor()
        await processor.process_unprocessed_articles(max_articles=20)
        
    except Exception as e:
        logger.error(f"AI处理主程序出错: {e}")
        print(f"❌ AI处理失败: {e}")


if __name__ == "__main__":
    # 确保logs目录存在
    os.makedirs('logs', exist_ok=True)
    
    # 运行异步处理
    asyncio.run(main()) 