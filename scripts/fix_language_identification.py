#!/usr/bin/env python3
"""
修复语言标识问题 - 识别并正确标记多语言文章
"""
import sqlite3
import re
from datetime import datetime

def detect_language_advanced(title, content, source_name):
    """高级语言检测"""
    if not title:
        return 'en'  # 默认英语
    
    text = (title + " " + (content or "")).lower()
    
    # 日语特征检测
    japanese_chars = re.findall(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf]', text)
    if len(japanese_chars) > len(text) * 0.1:
        return 'ja'
    
    # 韩语特征检测
    korean_chars = re.findall(r'[\uac00-\ud7af]', text)
    if len(korean_chars) > len(text) * 0.1:
        return 'ko'
    
    # 中文特征检测
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    if len(chinese_chars) > len(text) * 0.3:
        return 'zh'
    
    # 法语特征检测
    french_words = ['le', 'la', 'les', 'de', 'du', 'des', 'et', 'est', 'sont', 'pour', 'avec', 'sur', 'dans', 'par', 'que', 'qui', 'ce', 'cette', 'ces', 'un', 'une', 'au', 'aux', 'en', 'se', 'ne', 'pas', 'plus', 'moins', 'très', 'bien', 'bon', 'bonne', 'nouveau', 'nouvelle', 'grand', 'grande', 'petit', 'petite']
    french_count = sum(1 for word in french_words if word in text.split())
    if french_count > 3:
        return 'fr'
    
    # 德语特征检测
    german_words = ['der', 'die', 'das', 'und', 'ist', 'sind', 'für', 'mit', 'auf', 'von', 'zu', 'in', 'an', 'bei', 'nach', 'vor', 'über', 'unter', 'zwischen', 'hinter', 'neben', 'seit', 'während', 'wegen', 'trotz', 'ohne', 'gegen', 'um', 'durch', 'entlang', 'gegenüber', 'jenseits', 'diesseits', 'außerhalb', 'innerhalb']
    german_count = sum(1 for word in german_words if word in text.split())
    if german_count > 3:
        return 'de'
    
    # 意大利语特征检测
    italian_words = ['il', 'la', 'lo', 'gli', 'le', 'di', 'da', 'in', 'con', 'su', 'per', 'tra', 'fra', 'e', 'o', 'ma', 'se', 'che', 'chi', 'cui', 'quale', 'quali', 'quanto', 'quanta', 'quanti', 'quante', 'questo', 'questa', 'questi', 'queste', 'quello', 'quella', 'quelli', 'quelle', 'mio', 'mia', 'miei', 'mie', 'tuo', 'tua', 'tuoi', 'tue', 'suo', 'sua', 'suoi', 'sue']
    italian_count = sum(1 for word in italian_words if word in text.split())
    if italian_count > 3:
        return 'it'
    
    # 俄语特征检测
    russian_chars = re.findall(r'[\u0400-\u04ff]', text)
    if len(russian_chars) > len(text) * 0.1:
        return 'ru'
    
    # 阿拉伯语特征检测
    arabic_chars = re.findall(r'[\u0600-\u06ff]', text)
    if len(arabic_chars) > len(text) * 0.1:
        return 'ar'
    
    # 基于新闻源名称的语言映射
    language_mapping = {
        'en': ['CNN', 'BBC News', 'Reuters', 'TechCrunch', 'Bloomberg', 
               'The Guardian', 'The New York Times', 'NYTimes', 'NPR News', 'Ars Technica', 'Wired',
               'Google News China', 'VentureBeat AI', 'Al Jazeera', 'RT News', 'Sputnik'],
        'ja': ['NHK News', '朝日新闻', '读卖新闻', '日本经济新闻'],
        'ko': ['韩国中央日报', '韩国经济日报'],
        'zh': ['新浪新闻', '腾讯新闻', '网易新闻', '凤凰网', '澎湃新闻', '36氪', '虎嗅网', '钛媒体', '新加坡早报', '德国之声中文', '联合国新闻'],
        'fr': ['Le Monde', 'France 24'],
        'de': ['Deutsche Welle', '德国之声'],
        'it': ['Corriere della Sera', 'La Repubblica'],
        'es': ['El País', 'El Mundo'],
        'ru': ['RT News', 'Sputnik']
    }
    
    # 首先基于新闻源名称判断
    for lang, sources in language_mapping.items():
        if source_name in sources:
            return lang
    
    # 默认英语
    return 'en'

def fix_language_identification():
    """修复语言标识问题"""
    print("🔧 修复语言标识问题...")
    print("=" * 60)
    
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        # 获取所有文章
        cursor.execute("""
            SELECT id, title, content, original_language, source_name 
            FROM news_articles 
            ORDER BY id
        """)
        
        articles = cursor.fetchall()
        fixed_count = 0
        language_changes = {}
        
        for article in articles:
            article_id, title, content, current_language, source_name = article
            
            # 检测正确的语言
            correct_language = detect_language_advanced(title, content, source_name)
            
            # 如果语言标识不正确，进行修复
            if current_language != correct_language:
                print(f"  🔄 文章 {article_id}: {current_language} → {correct_language}")
                print(f"      标题: {title[:50]}...")
                print(f"      来源: {source_name}")
                
                # 更新语言标识
                cursor.execute("""
                    UPDATE news_articles 
                    SET original_language = ?, 
                        is_title_translated = FALSE,
                        is_content_translated = FALSE,
                        translated_title = NULL,
                        translated_content = NULL
                    WHERE id = ?
                """, (correct_language, article_id))
                
                fixed_count += 1
                
                # 统计语言变化
                if correct_language not in language_changes:
                    language_changes[correct_language] = 0
                language_changes[correct_language] += 1
        
        conn.commit()
        
        print(f"\n✅ 语言标识修复完成!")
        print(f"   修复文章数: {fixed_count}")
        
        if language_changes:
            print("\n📊 语言变化统计:")
            for lang, count in language_changes.items():
                lang_emoji = {
                    'en': '🇺🇸', 'ja': '🇯🇵', 'ko': '🇰🇷', 'zh': '🇨🇳',
                    'fr': '🇫🇷', 'de': '🇩🇪', 'it': '🇮🇹', 'es': '🇪🇸', 'ru': '🇷🇺'
                }.get(lang, '🌐')
                print(f"   {lang_emoji} {lang}: {count} 篇")
        
        # 显示最终语言分布
        show_final_language_distribution(cursor)
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        conn.rollback()
    finally:
        conn.close()

def show_final_language_distribution(cursor):
    """显示最终语言分布"""
    print("\n📊 最终语言分布:")
    print("-" * 40)
    
    cursor.execute("""
        SELECT original_language, COUNT(*) as count 
        FROM news_articles 
        GROUP BY original_language 
        ORDER BY count DESC
    """)
    
    for lang, count in cursor.fetchall():
        lang_emoji = {
            'en': '🇺🇸', 'ja': '🇯🇵', 'ko': '🇰🇷', 'zh': '🇨🇳',
            'fr': '🇫🇷', 'de': '🇩🇪', 'it': '🇮🇹', 'es': '🇪🇸', 'ru': '🇷🇺'
        }.get(lang, '🌐')
        print(f"{lang_emoji} {lang}: {count} 篇")

def main():
    """主函数"""
    print("🌍 新闻语言标识修复工具")
    print("=" * 60)
    
    fix_language_identification()
    
    print("\n🎯 下一步:")
    print("   1. 运行翻译脚本重新翻译非中文文章")
    print("   2. 验证翻译质量")
    print("   3. 测试前端显示效果")

if __name__ == "__main__":
    main() 