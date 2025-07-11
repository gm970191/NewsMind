#!/usr/bin/env python3
"""
批量翻译新闻标题脚本
"""
import sys
import os
import sqlite3
from datetime import datetime
import logging

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.lmstudio_llm import LMStudioLLM

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/translate_titles.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class NewsTitleTranslator:
    def __init__(self, db_path: str = "backend/newsmind.db"):
        self.db_path = db_path
        self.llm = LMStudioLLM(model="qwen2-0.5b-instruct")
        
        # 检查本地LM Studio是否可用
        if not self.llm.is_available():
            raise RuntimeError("本地LM Studio不可用，请检查服务是否启动")
        
        logger.info("✅ LM Studio服务可用")
    
    def get_untranslated_articles(self, limit: int = 10) -> list:
        """获取没有中文翻译标题的文章"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, title, language, translated_title
                FROM news_articles
                WHERE language != 'zh'
                AND (translated_title IS NULL OR translated_title = '' OR translated_title GLOB '*[a-zA-Z]*')
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            
            articles = []
            for row in cursor.fetchall():
                articles.append({
                    'id': row[0],
                    'title': row[1],
                    'language': row[2],
                    'translated_title': row[3]
                })
            
            return articles
            
        finally:
            conn.close()
    
    def translate_title(self, title: str) -> str:
        """翻译标题为中文"""
        system_prompt = "将以下新闻标题翻译成中文，保持原意，使用流畅的中文表达。直接返回翻译结果，不要添加任何格式。"
        
        result = self.llm.simple_chat(title, system_prompt=system_prompt, max_tokens=100)
        if result:
            # 清理可能的AI回复前缀
            result = result.strip()
            if result.startswith("翻译：") or result.startswith("中文翻译："):
                result = result.split("：", 1)[1].strip()
            return result
        return None
    
    def save_translated_title(self, article_id: int, translated_title: str) -> bool:
        """保存翻译后的标题到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 直接更新news_articles表的translated_title字段
            cursor.execute("""
                UPDATE news_articles 
                SET translated_title = ?, updated_at = ?
                WHERE id = ?
            """, (translated_title, datetime.now().isoformat(), article_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"保存翻译标题失败: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def translate_articles(self, limit: int = 10):
        """批量翻译文章标题"""
        logger.info(f"🔍 查找需要翻译标题的文章...")
        
        articles = self.get_untranslated_articles(limit)
        logger.info(f"📝 找到 {len(articles)} 篇需要翻译的文章")
        
        if not articles:
            logger.info("✅ 没有需要翻译的文章")
            return
        
        success_count = 0
        error_count = 0
        
        for article in articles:
            try:
                article_id = article['id']
                title = article['title']
                
                logger.info(f"🔧 翻译文章 {article_id}: {title[:50]}...")
                
                # 翻译标题
                translated_title = self.translate_title(title)
                
                if translated_title:
                    logger.info(f"   原文: {title}")
                    logger.info(f"   翻译: {translated_title}")
                    
                    # 保存到数据库
                    if self.save_translated_title(article_id, translated_title):
                        success_count += 1
                        logger.info(f"   ✅ 文章 {article_id} 翻译完成")
                    else:
                        error_count += 1
                        logger.error(f"   ❌ 文章 {article_id} 保存失败")
                else:
                    error_count += 1
                    logger.error(f"   ❌ 文章 {article_id} 翻译失败")
                
            except Exception as e:
                error_count += 1
                logger.error(f"   ❌ 文章 {article.get('id', 'unknown')} 处理出错: {e}")
        
        logger.info(f"\n📊 翻译完成:")
        logger.info(f"   ✅ 成功翻译: {success_count} 篇")
        logger.info(f"   ❌ 翻译失败: {error_count} 篇")
        if success_count + error_count > 0:
            logger.info(f"   📈 成功率: {success_count/(success_count+error_count)*100:.1f}%")


def main():
    """主函数"""
    try:
        translator = NewsTitleTranslator()
        translator.translate_articles(limit=20)  # 翻译20篇文章
        
    except Exception as e:
        logger.error(f"翻译程序出错: {e}")
        print(f"❌ 翻译失败: {e}")


if __name__ == "__main__":
    # 确保logs目录存在
    os.makedirs('logs', exist_ok=True)
    
    # 运行翻译
    main() 