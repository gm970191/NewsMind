#!/usr/bin/env python3
"""
修复语言标识问题 V2 - 基于新闻源名称的准确语言检测
"""
import sqlite3
import re
from datetime import datetime

def detect_language_by_source(source_name):
    """基于新闻源名称检测语言"""
    # 基于新闻源名称的语言映射
    language_mapping = {
        # 英语新闻源
        'en': [
            'CNN', 'BBC News', 'Reuters', 'TechCrunch', 'Bloomberg', 
            'The Guardian', 'The New York Times', 'NYTimes', 'NPR News', 
            'Ars Technica', 'Wired', 'Google News China', 'VentureBeat AI', 
            'Al Jazeera', 'RT News', 'Sputnik', 'Foreign Policy'
        ],
        
        # 日语新闻源
        'ja': [
            'NHK News', '朝日新闻', '读卖新闻', '日本经济新闻'
        ],
        
        # 韩语新闻源
        'ko': [
            '韩国中央日报', '韩国经济日报'
        ],
        
        # 中文新闻源
        'zh': [
            '新浪新闻', '腾讯新闻', '网易新闻', '凤凰网', '澎湃新闻', 
            '36氪', '虎嗅网', '钛媒体', '新加坡早报', '德国之声中文', 
            '联合国新闻'
        ],
        
        # 法语新闻源
        'fr': [
            'Le Monde', 'France 24'
        ],
        
        # 德语新闻源
        'de': [
            'Deutsche Welle', '德国之声'
        ],
        
        # 意大利语新闻源
        'it': [
            'Corriere della Sera', 'La Repubblica'
        ],
        
        # 西班牙语新闻源
        'es': [
            'El País', 'El Mundo'
        ],
        
        # 俄语新闻源
        'ru': [
            'RT News', 'Sputnik'
        ]
    }
    
    # 查找匹配的语言
    for lang, sources in language_mapping.items():
        if source_name in sources:
            return lang
    
    # 默认英语
    return 'en'

def detect_language_by_content(title, content):
    """基于内容特征检测语言（辅助方法）"""
    if not title:
        return 'en'
    
    text = (title + " " + (content or "")).lower()
    
    # 日语特征检测（平假名、片假名、汉字）
    japanese_chars = re.findall(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf]', text)
    if len(japanese_chars) > len(text) * 0.15:
        return 'ja'
    
    # 韩语特征检测
    korean_chars = re.findall(r'[\uac00-\ud7af]', text)
    if len(korean_chars) > len(text) * 0.15:
        return 'ko'
    
    # 中文特征检测
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    if len(chinese_chars) > len(text) * 0.4:
        return 'zh'
    
    # 俄语特征检测
    russian_chars = re.findall(r'[\u0400-\u04ff]', text)
    if len(russian_chars) > len(text) * 0.15:
        return 'ru'
    
    # 阿拉伯语特征检测
    arabic_chars = re.findall(r'[\u0600-\u06ff]', text)
    if len(arabic_chars) > len(text) * 0.15:
        return 'ar'
    
    # 默认英语
    return 'en'

def fix_language_identification():
    """修复语言标识问题"""
    print("🔧 修复语言标识问题 V2...")
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
            
            # 首先基于新闻源名称检测语言
            source_language = detect_language_by_source(source_name)
            
            # 如果新闻源无法确定，则基于内容检测
            if source_language == 'en':
                content_language = detect_language_by_content(title, content)
                # 只有当内容检测结果不是英语时，才使用内容检测结果
                if content_language != 'en':
                    correct_language = content_language
                else:
                    correct_language = 'en'
            else:
                correct_language = source_language
            
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
    print("🌍 新闻语言标识修复工具 V2")
    print("=" * 60)
    
    fix_language_identification()
    
    print("\n🎯 下一步:")
    print("   1. 运行翻译脚本重新翻译非中文文章")
    print("   2. 验证翻译质量")
    print("   3. 测试前端显示效果")

if __name__ == "__main__":
    main() 