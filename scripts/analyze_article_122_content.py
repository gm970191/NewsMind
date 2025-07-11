#!/usr/bin/env python3
"""
分析文章122的正文内容问题
"""
import sqlite3
import re

def analyze_content_issues():
    """分析内容问题"""
    print("🔍 分析文章122的正文内容问题...")
    print("=" * 60)
    
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, title, content, original_language, source_name 
            FROM news_articles 
            WHERE id = 122
        """)
        
        article = cursor.fetchone()
        if not article:
            print("❌ 文章122不存在")
            return
        
        article_id, title, content, language, source_name = article
        
        print(f"文章ID: {article_id}")
        print(f"标题: {title}")
        print(f"新闻源: {source_name}")
        print(f"当前语言标记: {language}")
        print(f"内容长度: {len(content)} 字符")
        print()
        
        print("正文内容分析:")
        print("-" * 40)
        print(content)
        print("-" * 40)
        
        # 分析内容特征
        print("\n内容特征分析:")
        
        # 检查是否包含中文字符
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', content)
        print(f"中文字符数: {len(chinese_chars)}")
        if chinese_chars:
            print(f"中文字符示例: {chinese_chars[:10]}")
        
        # 检查是否包含俄文字符
        russian_chars = re.findall(r'[\u0400-\u04ff]', content)
        print(f"俄文字符数: {len(russian_chars)}")
        if russian_chars:
            print(f"俄文字符示例: {russian_chars[:10]}")
        
        # 检查是否包含日文字符
        japanese_chars = re.findall(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf]', content)
        print(f"日文字符数: {len(japanese_chars)}")
        if japanese_chars:
            print(f"日文字符示例: {japanese_chars[:10]}")
        
        # 检查是否包含韩文字符
        korean_chars = re.findall(r'[\uac00-\ud7af]', content)
        print(f"韩文字符数: {len(korean_chars)}")
        if korean_chars:
            print(f"韩文字符示例: {korean_chars[:10]}")
        
        # 检查是否包含阿拉伯文字符
        arabic_chars = re.findall(r'[\u0600-\u06ff]', content)
        print(f"阿拉伯文字符数: {len(arabic_chars)}")
        if arabic_chars:
            print(f"阿拉伯文字符示例: {arabic_chars[:10]}")
        
        # 检查英文字符
        english_chars = re.findall(r'[a-zA-Z]', content)
        print(f"英文字符数: {len(english_chars)}")
        
        # 检查数字
        digits = re.findall(r'\d', content)
        print(f"数字字符数: {len(digits)}")
        
        # 检查特殊字符
        special_chars = re.findall(r'[^\w\s]', content)
        print(f"特殊字符数: {len(special_chars)}")
        if special_chars:
            print(f"特殊字符示例: {special_chars[:20]}")
        
        # 分析可能的语言
        print("\n可能的语言分析:")
        
        if len(chinese_chars) > len(content) * 0.1:
            print("  🇨🇳 可能是中文内容")
        
        if len(russian_chars) > len(content) * 0.1:
            print("  🇷🇺 可能是俄文内容")
        
        if len(japanese_chars) > len(content) * 0.1:
            print("  🇯🇵 可能是日文内容")
        
        if len(korean_chars) > len(content) * 0.1:
            print("  🇰🇷 可能是韩文内容")
        
        if len(arabic_chars) > len(content) * 0.1:
            print("  🇸🇦 可能是阿拉伯文内容")
        
        if len(english_chars) > len(content) * 0.3:
            print("  🇺🇸 可能是英文内容")
        
        # 检查是否是编码问题
        print("\n编码问题分析:")
        if len(special_chars) > len(content) * 0.2:
            print("  ⚠️  可能存在编码问题")
        
        # 尝试识别内容中的关键词
        print("\n内容关键词分析:")
        words = re.findall(r'\b\w+\b', content.lower())
        word_freq = {}
        for word in words:
            if len(word) > 2:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # 显示最常见的词
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        print("最常见词汇:")
        for word, count in sorted_words[:10]:
            print(f"  {word}: {count} 次")
        
    finally:
        conn.close()

def check_other_articles_for_similar_issues():
    """检查其他文章是否有类似问题"""
    print("\n🔍 检查其他文章是否有类似问题...")
    print("=" * 60)
    
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, title, content, original_language, source_name 
            FROM news_articles 
            WHERE LENGTH(content) > 100
            ORDER BY id
            LIMIT 20
        """)
        
        articles = cursor.fetchall()
        
        print("检查文章内容质量:")
        for article in articles:
            article_id, title, content, language, source_name = article
            
            # 检查内容是否包含大量特殊字符
            special_chars = re.findall(r'[^\w\s]', content)
            special_ratio = len(special_chars) / len(content) if content else 0
            
            if special_ratio > 0.3:  # 如果特殊字符超过30%
                print(f"  ⚠️  文章 {article_id} ({source_name}): 特殊字符比例 {special_ratio:.2%}")
                print(f"      标题: {title[:50]}...")
                print(f"      内容预览: {content[:100]}...")
                print()
    
    finally:
        conn.close()

def main():
    """主函数"""
    print("🔍 文章122内容问题分析")
    print("=" * 60)
    
    # 分析文章122的内容
    analyze_content_issues()
    
    # 检查其他文章是否有类似问题
    check_other_articles_for_similar_issues()
    
    print("\n🎯 分析完成!")
    print("   根据分析结果，可以确定内容的具体问题和语言")

if __name__ == "__main__":
    main() 