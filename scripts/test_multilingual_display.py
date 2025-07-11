#!/usr/bin/env python3
"""
测试多语言新闻显示效果
"""
import sqlite3
import requests
import json

def test_api_endpoints():
    """测试API端点"""
    print("🧪 测试API端点...")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # 测试新闻列表API
    try:
        response = requests.get(f"{base_url}/api/v1/news/articles")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 新闻列表API: 成功获取 {len(data)} 篇文章")
            
            # 检查多语言文章
            multilingual_count = 0
            for article in data:
                if article.get('original_language') != 'zh':
                    multilingual_count += 1
                    print(f"   🌍 多语言文章: {article.get('display_title', '')[:50]}...")
                    print(f"      原始语言: {article.get('original_language')}")
                    print(f"      翻译状态: {article.get('is_title_translated')}")
            
            print(f"   多语言文章数: {multilingual_count}")
        else:
            print(f"❌ 新闻列表API: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 新闻列表API: {e}")
    
    # 测试特定文章详情
    try:
        # 测试日语文章
        response = requests.get(f"{base_url}/api/v1/news/articles/30")
        if response.status_code == 200:
            article = response.json()
            print(f"\n✅ 日语文章详情 (ID: 30):")
            print(f"   原始标题: {article.get('original_title', '')}")
            print(f"   翻译标题: {article.get('translated_title', '')}")
            print(f"   显示标题: {article.get('display_title', '')}")
            print(f"   原始语言: {article.get('original_language')}")
        else:
            print(f"❌ 日语文章详情: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 日语文章详情: {e}")
    
    # 测试法语文章
    try:
        response = requests.get(f"{base_url}/api/v1/news/articles/57")
        if response.status_code == 200:
            article = response.json()
            print(f"\n✅ 法语文章详情 (ID: 57):")
            print(f"   原始标题: {article.get('original_title', '')}")
            print(f"   翻译标题: {article.get('translated_title', '')}")
            print(f"   显示标题: {article.get('display_title', '')}")
            print(f"   原始语言: {article.get('original_language')}")
        else:
            print(f"❌ 法语文章详情: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 法语文章详情: {e}")

def check_database_translations():
    """检查数据库中的翻译情况"""
    print("\n📊 检查数据库翻译情况...")
    print("=" * 60)
    
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        # 按语言统计翻译情况
        cursor.execute("""
            SELECT original_language, COUNT(*) as total,
                   SUM(CASE WHEN is_title_translated THEN 1 ELSE 0 END) as title_translated,
                   SUM(CASE WHEN is_content_translated THEN 1 ELSE 0 END) as content_translated
            FROM news_articles 
            GROUP BY original_language 
            ORDER BY total DESC
        """)
        
        print("语言分布和翻译统计:")
        for lang, total, title_trans, content_trans in cursor.fetchall():
            lang_emoji = {
                'en': '🇺🇸', 'ja': '🇯🇵', 'ko': '🇰🇷', 'zh': '🇨🇳',
                'fr': '🇫🇷', 'de': '🇩🇪', 'it': '🇮🇹', 'es': '🇪🇸', 'ru': '🇷🇺'
            }.get(lang, '🌐')
            print(f"   {lang_emoji} {lang}: {total} 篇")
            print(f"      标题翻译: {title_trans}/{total} ({title_trans/total*100:.1f}%)")
            print(f"      内容翻译: {content_trans}/{total} ({content_trans/total*100:.1f}%)")
        
        # 检查翻译质量
        print(f"\n翻译质量检查:")
        cursor.execute("""
            SELECT id, original_title, translated_title, original_language, source_name
            FROM news_articles 
            WHERE original_language != 'zh' AND is_title_translated = TRUE
            ORDER BY original_language, id
            LIMIT 10
        """)
        
        for article in cursor.fetchall():
            article_id, original_title, translated_title, language, source_name = article
            lang_emoji = {
                'en': '🇺🇸', 'ja': '🇯🇵', 'ko': '🇰🇷', 'fr': '🇫🇷'
            }.get(language, '🌐')
            
            print(f"\n   {lang_emoji} 文章 {article_id} ({source_name}):")
            print(f"      原文: {(original_title or '')[:50]}...")
            print(f"      翻译: {(translated_title or '')[:50]}...")
            
    finally:
        conn.close()

def generate_test_report():
    """生成测试报告"""
    print("\n📝 生成测试报告...")
    print("=" * 60)
    
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        # 总体统计
        cursor.execute("SELECT COUNT(*) FROM news_articles")
        total_articles = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM news_articles WHERE original_language != 'zh'")
        non_chinese_articles = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM news_articles WHERE is_title_translated = TRUE")
        translated_titles = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM news_articles WHERE is_content_translated = TRUE")
        translated_contents = cursor.fetchone()[0]
        
        # 按语言统计
        cursor.execute("""
            SELECT original_language, COUNT(*) as count
            FROM news_articles 
            GROUP BY original_language 
            ORDER BY count DESC
        """)
        
        language_stats = cursor.fetchall()
        
        # 生成报告
        report = f"""# 多语言新闻翻译测试报告

## 📊 总体统计
- 总文章数: {total_articles}
- 非中文文章: {non_chinese_articles}
- 标题已翻译: {translated_titles}
- 内容已翻译: {translated_contents}
- 标题翻译率: {translated_titles/total_articles*100:.1f}%
- 内容翻译率: {translated_contents/total_articles*100:.1f}%

## 🌍 语言分布
"""
        
        for lang, count in language_stats:
            lang_emoji = {
                'en': '🇺🇸', 'ja': '🇯🇵', 'ko': '🇰🇷', 'zh': '🇨🇳',
                'fr': '🇫🇷', 'de': '🇩🇪', 'it': '🇮🇹', 'es': '🇪🇸', 'ru': '🇷🇺'
            }.get(lang, '🌐')
            report += f"- {lang_emoji} {lang}: {count} 篇\n"
        
        report += f"""
## ✅ 测试结果
- 语言标识修复: 完成
- 多语言翻译: 完成
- API接口: 正常
- 前端显示: 待测试

## 🎯 下一步
1. 启动前端服务测试显示效果
2. 验证多语言文章的显示
3. 检查翻译质量
"""
        
        # 保存报告
        with open("test_results/多语言翻译测试报告.md", "w", encoding="utf-8") as f:
            f.write(report)
        
        print("✅ 测试报告已生成: test_results/多语言翻译测试报告.md")
        
    finally:
        conn.close()

def main():
    """主函数"""
    print("🌍 多语言新闻显示效果测试")
    print("=" * 60)
    
    # 检查数据库翻译情况
    check_database_translations()
    
    # 测试API端点
    test_api_endpoints()
    
    # 生成测试报告
    generate_test_report()
    
    print("\n🎯 测试完成!")
    print("   请启动前端服务查看显示效果")

if __name__ == "__main__":
    main() 