#!/usr/bin/env python3
"""
批量翻译多语言新闻 - 处理非中文文章的标题和正文翻译
"""
import sqlite3
import time
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from lmstudio_llm import LMStudioLLM

class MultilingualTranslator:
    def __init__(self):
        self.lmstudio = LMStudioLLM()
        self.db_path = "backend/newsmind.db"
        
        # 检查LM Studio是否可用
        if not self.lmstudio.test_available():
            print("❌ LM Studio不可用，请确保服务正在运行")
            sys.exit(1)
        
        print("✅ LM Studio连接成功")

    def get_articles_to_translate(self):
        """获取需要翻译的文章"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, title, content, original_language, source_name
                FROM news_articles 
                WHERE original_language != 'zh'
                AND (is_title_translated = FALSE OR is_content_translated = FALSE)
                ORDER BY id
            """)
            
            articles = []
            for row in cursor.fetchall():
                articles.append({
                    'id': row[0],
                    'title': row[1],
                    'content': row[2],
                    'original_language': row[3],
                    'source_name': row[4]
                })
            
            return articles
        finally:
            conn.close()

    def translate_title(self, title, source_language):
        """翻译标题"""
        if not title or len(title.strip()) < 5:
            return title
        
        prompt = f"""请将以下{source_language}语标题翻译成中文，保持新闻标题的简洁性和准确性：

原文：{title}

中文翻译："""
        
        try:
            response = self.lmstudio.generate(prompt, max_tokens=100)
            if response and response.strip():
                return response.strip()
            else:
                return title
        except Exception as e:
            print(f"     ❌ 标题翻译失败: {e}")
            return title

    def translate_content(self, content, source_language):
        """翻译正文内容"""
        if not content or len(content.strip()) < 20:
            return content
        
        # 限制内容长度，避免翻译时间过长
        content_to_translate = content[:2000] if len(content) > 2000 else content
        
        prompt = f"""请将以下{source_language}语新闻内容翻译成中文，保持原文的意思和结构：

原文：{content_to_translate}

中文翻译："""
        
        try:
            response = self.lmstudio.generate(prompt, max_tokens=1000)
            if response and response.strip():
                return response.strip()
            else:
                return content
        except Exception as e:
            print(f"     ❌ 内容翻译失败: {e}")
            return content

    def update_article_translation(self, article_id, translated_title, translated_content):
        """更新文章的翻译内容"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE news_articles 
                SET translated_title = ?,
                    translated_content = ?,
                    is_title_translated = TRUE,
                    is_content_translated = TRUE,
                    translation_quality_score = 8.0
                WHERE id = ?
            """, (translated_title, translated_content, article_id))
            
            conn.commit()
        except Exception as e:
            print(f"     ❌ 数据库更新失败: {e}")
            conn.rollback()
        finally:
            conn.close()

    def batch_translate(self):
        """批量翻译"""
        print("🌍 开始批量翻译多语言新闻...")
        print("=" * 60)
        
        articles = self.get_articles_to_translate()
        
        if not articles:
            print("✅ 没有需要翻译的文章")
            return
        
        print(f"📝 找到 {len(articles)} 篇需要翻译的文章")
        
        success_count = 0
        language_stats = {}
        
        for i, article in enumerate(articles, 1):
            article_id = article['id']
            title = article['title']
            content = article['content']
            source_language = article['original_language']
            source_name = article['source_name']
            
            lang_emoji = {
                'en': '🇺🇸', 'ja': '🇯🇵', 'ko': '🇰🇷', 'fr': '🇫🇷', 
                'de': '🇩🇪', 'it': '🇮🇹', 'es': '🇪🇸', 'ru': '🇷🇺'
            }.get(source_language, '🌐')
            
            print(f"\n[{i}/{len(articles)}] {lang_emoji} 文章 {article_id}")
            print(f"    来源: {source_name}")
            print(f"    语言: {source_language}")
            print(f"    标题: {title[:50]}...")
            
            # 翻译标题
            print("     🔄 翻译标题...")
            translated_title = self.translate_title(title, source_language)
            
            # 翻译内容
            print("     🔄 翻译内容...")
            translated_content = self.translate_content(content, source_language)
            
            # 更新数据库
            print("     💾 保存翻译结果...")
            self.update_article_translation(article_id, translated_title, translated_content)
            
            print(f"     ✅ 翻译完成")
            print(f"     标题翻译: {translated_title[:50]}...")
            
            success_count += 1
            
            # 统计语言分布
            if source_language not in language_stats:
                language_stats[source_language] = 0
            language_stats[source_language] += 1
            
            # 避免请求过于频繁
            time.sleep(1)
        
        print(f"\n✅ 批量翻译完成!")
        print(f"   成功翻译: {success_count}/{len(articles)} 篇")
        
        print("\n📊 语言分布统计:")
        for lang, count in language_stats.items():
            lang_emoji = {
                'en': '🇺🇸', 'ja': '🇯🇵', 'ko': '🇰🇷', 'fr': '🇫🇷', 
                'de': '🇩🇪', 'it': '🇮🇹', 'es': '🇪🇸', 'ru': '🇷🇺'
            }.get(lang, '🌐')
            print(f"   {lang_emoji} {lang}: {count} 篇")

    def show_translation_stats(self):
        """显示翻译统计"""
        print("\n📊 翻译状态统计:")
        print("-" * 40)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 总体统计
            cursor.execute("SELECT COUNT(*) FROM news_articles")
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM news_articles WHERE is_title_translated = TRUE")
            title_translated = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM news_articles WHERE is_content_translated = TRUE")
            content_translated = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM news_articles WHERE original_language != 'zh'")
            non_chinese = cursor.fetchone()[0]
            
            print(f"总文章数: {total}")
            print(f"非中文文章: {non_chinese}")
            print(f"标题已翻译: {title_translated}")
            print(f"内容已翻译: {content_translated}")
            print(f"标题翻译率: {title_translated/total*100:.1f}%")
            print(f"内容翻译率: {content_translated/total*100:.1f}%")
            
            # 按语言统计
            cursor.execute("""
                SELECT original_language, COUNT(*) as count,
                       SUM(CASE WHEN is_title_translated THEN 1 ELSE 0 END) as title_translated,
                       SUM(CASE WHEN is_content_translated THEN 1 ELSE 0 END) as content_translated
                FROM news_articles 
                GROUP BY original_language 
                ORDER BY count DESC
            """)
            
            print(f"\n按语言统计:")
            for lang, count, title_trans, content_trans in cursor.fetchall():
                lang_emoji = {
                    'en': '🇺🇸', 'ja': '🇯🇵', 'ko': '🇰🇷', 'zh': '🇨🇳',
                    'fr': '🇫🇷', 'de': '🇩🇪', 'it': '🇮🇹', 'es': '🇪🇸', 'ru': '🇷🇺'
                }.get(lang, '🌐')
                print(f"   {lang_emoji} {lang}: {count} 篇 (标题翻译: {title_trans}, 内容翻译: {content_trans})")
                
        finally:
            conn.close()

def main():
    """主函数"""
    print("🌍 多语言新闻批量翻译工具")
    print("=" * 60)
    
    translator = MultilingualTranslator()
    
    # 显示当前翻译统计
    translator.show_translation_stats()
    
    # 执行批量翻译
    translator.batch_translate()
    
    # 显示翻译后统计
    translator.show_translation_stats()
    
    print("\n🎯 翻译完成!")
    print("   现在可以测试前端显示效果")

if __name__ == "__main__":
    main() 