#!/usr/bin/env python3
"""
修复现有文章的标题翻译和详细总结
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
        logging.FileHandler('logs/fix_articles.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LMStudioLLM:
    def __init__(self, api_url="http://127.0.0.1:1234/v1/chat/completions"):
        self.api_url = api_url

    def test_available(self) -> bool:
        try:
            data = {
                "model": "lmstudio",
                "messages": [
                    {"role": "system", "content": "你是AI助手。"},
                    {"role": "user", "content": "你好"}
                ],
                "temperature": 0.1,
                "max_tokens": 10
            }
            resp = requests.post(self.api_url, json=data, timeout=5)
            resp.raise_for_status()
            result = resp.json()
            return 'choices' in result and len(result['choices']) > 0
        except Exception as e:
            logger.warning(f"本地LM Studio不可用: {e}")
            return False

    def call(self, system_prompt: str, user_content: str, max_tokens=1000) -> Optional[str]:
        try:
            data = {
                "model": "lmstudio",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                "temperature": 0.1,
                "max_tokens": max_tokens
            }
            resp = requests.post(self.api_url, json=data, timeout=30)
            resp.raise_for_status()
            result = resp.json()
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content'].strip()
            return None
        except Exception as e:
            logger.warning(f"LM Studio调用失败: {e}")
            return None


class ArticleFixer:
    def __init__(self):
        self.api_key = DEEPSEEK_API_KEY
        self.api_url = DEEPSEEK_API_URL
        self.lmstudio = LMStudioLLM()
        self.db_path = "backend/newsmind.db"
        self.use_lmstudio = self.lmstudio.test_available()
        if not self.api_key and not self.use_lmstudio:
            raise ValueError("DEEPSEEK_API_KEY 环境变量未设置，且本地LM Studio不可用")

    def get_articles_to_fix(self, limit: int = 10) -> List[Dict]:
        """获取需要修复的文章（只要没有中文标题就处理）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT na.id, na.title, na.content, na.language, na.is_processed, pc.translated_title
                FROM news_articles na
                LEFT JOIN processed_content pc ON na.id = pc.article_id
                WHERE na.is_processed = 1
                AND (pc.translated_title IS NULL OR pc.translated_title = '' OR pc.translated_title GLOB '*[a-zA-Z]*')
                AND na.language != 'zh'
                ORDER BY na.created_at DESC
                LIMIT ?
            ''', (limit,))
            articles = []
            for row in cursor.fetchall():
                articles.append({
                    'id': row[0],
                    'title': row[1],
                    'content': row[2],
                    'language': row[3],
                    'is_processed': bool(row[4]),
                    'translated_title': row[5]
                })
            return articles
        finally:
            conn.close()

    async def call_llm(self, system_prompt: str, user_content: str) -> Optional[str]:
        """优先调用本地LM Studio，不可用时fallback到DeepSeek"""
        if self.use_lmstudio:
            result = self.lmstudio.call(system_prompt, user_content)
            if result:
                return result
            else:
                logger.warning("LM Studio调用失败，fallback到DeepSeek")
                self.use_lmstudio = False
        # fallback到DeepSeek
        if self.api_key:
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1000
                }
                resp = requests.post(self.api_url, headers=headers, json=data, timeout=30)
                resp.raise_for_status()
                result = resp.json()
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content'].strip()
                return None
            except Exception as e:
                logger.error(f"DeepSeek API调用失败: {e}")
                return None
        return None

    async def translate_title(self, title: str) -> Optional[str]:
        try:
            prompt = """将以下新闻标题翻译成中文，保持原意，使用流畅的中文表达。直接返回翻译结果，不要添加任何格式。"""
            return await self.call_llm(prompt, title)
        except Exception as e:
            logger.error(f"翻译标题失败: {e}")
            return None

    async def generate_detailed_summary(self, content: str) -> Optional[str]:
        """生成详细中文总结"""
        try:
            if len(content) > 2000:
                content = content[:2000]

            prompt = """为以下新闻生成详细的中文总结，包含事件背景、发展过程、结果影响等。直接返回总结内容，不要添加任何格式。"""
            return await self.call_llm(prompt, content)
        except Exception as e:
            logger.error(f"生成详细总结失败: {e}")
            return None

    def update_article_content(self, article_id: int, translated_title: str, detailed_summary: str) -> bool:
        """更新文章内容"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE processed_content
                SET translated_title = ?, detailed_summary_zh = ?, updated_at = ?
                WHERE article_id = ?
            """, (translated_title, detailed_summary, datetime.now().isoformat(), article_id))

            conn.commit()
            return True

        except Exception as e:
            logger.error(f"更新文章内容失败: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    async def fix_single_article(self, article: Dict) -> bool:
        """修复单篇文章"""
        try:
            article_id = article['id']
            print(f"🔧 修复文章 ID:{article_id} - {article['title'][:30]}...")

            start_time = time.time()

            # 1. 翻译标题
            translated_title = await self.translate_title(article['title'])
            if translated_title:
                print(f"      标题翻译: {article['title'][:30]}... → {translated_title[:30]}...")
            else:
                print(f"      标题翻译失败")
                return False

            # 2. 生成详细总结
            detailed_summary = await self.generate_detailed_summary(article['content'])
            if detailed_summary:
                print(f"      详细总结: {detailed_summary[:50]}...")
            else:
                print(f"      详细总结生成失败")
                return False

            # 3. 保存结果
            success = self.update_article_content(article_id, translated_title, detailed_summary)

            if success:
                processing_time = time.time() - start_time
                print(f"   ✅ 文章 {article_id} 修复完成 ({processing_time:.1f}s)")
                return True
            else:
                print(f"   ❌ 文章 {article_id} 保存失败")
                return False

        except Exception as e:
            logger.error(f"修复文章 {article.get('id', 'unknown')} 出错: {e}")
            print(f"   ❌ 文章 {article.get('id', 'unknown')} 修复出错: {e}")
            return False

    async def fix_articles(self, max_articles: int = 10):
        """修复文章"""
        print("🔧 开始修复文章标题翻译和详细总结...")
        print("=" * 60)

        articles = self.get_articles_to_fix(max_articles)
        print(f"📝 找到 {len(articles)} 篇需要修复的文章")

        if not articles:
            print("✅ 没有需要修复的文章")
            return

        success_count = 0
        error_count = 0

        for article in articles:
            success = await self.fix_single_article(article)
            if success:
                success_count += 1
            else:
                error_count += 1

            # 添加延迟避免API限制
            await asyncio.sleep(2)

        print(f"\n📊 修复完成:")
        print(f"   ✅ 成功修复: {success_count} 篇")
        print(f"   ❌ 修复失败: {error_count} 篇")
        print(f"   📈 成功率: {success_count/(success_count+error_count)*100:.1f}%")


async def main():
    """主函数"""
    try:
        fixer = ArticleFixer()
        await fixer.fix_articles(max_articles=10)

    except Exception as e:
        logger.error(f"修复程序出错: {e}")
        print(f"❌ 修复失败: {e}")


if __name__ == "__main__":
    # 确保logs目录存在
    os.makedirs('logs', exist_ok=True)
    # 测试本地LM Studio可用性
    lmstudio = LMStudioLLM()
    print("[测试] 本地LM Studio可用性:", "可用" if lmstudio.test_available() else "不可用")
    # 运行异步修复
    asyncio.run(main()) 