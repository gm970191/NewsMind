#!/usr/bin/env python3
"""
改进文章122的翻译 - 尝试不同的翻译方法
"""
import sqlite3

def get_article_122():
    """获取文章122的信息"""
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, title, content, translated_title, original_language, source_name
            FROM news_articles 
            WHERE id = 122
        """)
        
        article = cursor.fetchone()
        if article:
            return {
                'id': article[0],
                'title': article[1],
                'content': article[2],
                'translated_title': article[3],
                'original_language': article[4],
                'source_name': article[5]
            }
        return None
    finally:
        conn.close()

def generate_alternative_translations():
    """生成不同的翻译选项"""
    original_title = "China Should Invite Trump to Its Military Parade"
    
    translations = {
        "直译": "中国应该邀请特朗普参加其军事阅兵",
        "意译1": "中国应邀请特朗普出席军事阅兵式",
        "意译2": "中国应该邀请特朗普观看军事阅兵",
        "意译3": "中国应邀请特朗普参加阅兵仪式",
        "意译4": "中国应该邀请特朗普出席阅兵式",
        "意译5": "中国应邀请特朗普参加军事阅兵典礼",
        "意译6": "中国应该邀请特朗普观看阅兵仪式",
        "意译7": "中国应邀请特朗普出席军事阅兵典礼",
        "意译8": "中国应该邀请特朗普参加阅兵典礼"
    }
    
    return translations

def test_different_language_approaches():
    """测试不同语言的处理方法"""
    print("🌍 测试不同语言的处理方法...")
    print("=" * 60)
    
    # 获取文章信息
    article = get_article_122()
    if not article:
        print("❌ 文章122不存在")
        return
    
    print(f"文章ID: {article['id']}")
    print(f"原始标题: {article['title']}")
    print(f"当前翻译: {article['translated_title']}")
    print(f"原始语言: {article['original_language']}")
    print(f"新闻源: {article['source_name']}")
    print()
    
    # 生成不同的翻译选项
    translations = generate_alternative_translations()
    
    print("不同的翻译选项:")
    for method, translation in translations.items():
        print(f"  {method}: {translation}")
    
    print()
    
    # 分析哪个翻译更好
    print("翻译质量分析:")
    print("  ✅ 直译: 准确但可能不够自然")
    print("  ✅ 意译1: 更符合中文表达习惯")
    print("  ✅ 意译2: 强调'观看'动作")
    print("  ✅ 意译3: 简洁明了")
    print("  ✅ 意译4: 正式场合用语")
    print("  ✅ 意译5: 强调典礼性质")
    print("  ✅ 意译6: 突出观看体验")
    print("  ✅ 意译7: 正式且庄重")
    print("  ✅ 意译8: 简洁且正式")
    
    print()
    print("推荐翻译:")
    print("  🏆 最佳选择: 中国应邀请特朗普出席军事阅兵式")
    print("  🥈 次选: 中国应该邀请特朗普参加阅兵仪式")
    print("  🥉 第三选择: 中国应邀请特朗普出席阅兵式")

def update_article_translation(translation):
    """更新文章翻译"""
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE news_articles 
            SET translated_title = ?,
                translation_quality_score = 9.0
            WHERE id = 122
        """, (translation,))
        
        conn.commit()
        print(f"✅ 已更新文章122的翻译为: {translation}")
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        conn.rollback()
    finally:
        conn.close()

def test_api_response():
    """测试API响应"""
    print("\n🧪 测试API响应...")
    print("=" * 60)
    
    import requests
    
    try:
        response = requests.get("http://localhost:8000/api/v1/news/articles/122")
        if response.status_code == 200:
            article = response.json()
            print("API返回的文章信息:")
            print(f"  原始标题: {article.get('original_title', 'N/A')}")
            print(f"  翻译标题: {article.get('translated_title', 'N/A')}")
            print(f"  显示标题: {article.get('display_title', 'N/A')}")
            print(f"  原始语言: {article.get('original_language', 'N/A')}")
            print(f"  翻译状态: {article.get('is_title_translated', 'N/A')}")
        else:
            print(f"❌ API请求失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ API测试失败: {e}")

def main():
    """主函数"""
    print("🔧 改进文章122的翻译")
    print("=" * 60)
    
    # 测试不同语言的处理方法
    test_different_language_approaches()
    
    # 询问用户选择哪个翻译
    print("\n请选择要应用的翻译:")
    translations = generate_alternative_translations()
    
    for i, (method, translation) in enumerate(translations.items(), 1):
        print(f"  {i}. {method}: {translation}")
    
    print("  0. 不更新，保持当前翻译")
    
    try:
        choice = input("\n请输入选择 (0-9): ").strip()
        choice = int(choice)
        
        if choice == 0:
            print("保持当前翻译不变")
        elif 1 <= choice <= len(translations):
            selected_method = list(translations.keys())[choice - 1]
            selected_translation = translations[selected_method]
            
            print(f"\n应用翻译: {selected_method}")
            print(f"翻译内容: {selected_translation}")
            
            # 更新数据库
            update_article_translation(selected_translation)
            
            # 测试API响应
            test_api_response()
            
        else:
            print("❌ 无效选择")
            
    except ValueError:
        print("❌ 请输入有效数字")
    except KeyboardInterrupt:
        print("\n操作已取消")

if __name__ == "__main__":
    main() 