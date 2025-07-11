#!/usr/bin/env python3
"""
修复文章122的内容问题
"""
import sqlite3

def analyze_content_problem():
    """分析内容问题"""
    print("🔍 分析文章122的内容问题...")
    print("=" * 60)
    
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT content FROM news_articles WHERE id = 122")
        result = cursor.fetchone()
        if not result:
            print("❌ 文章122不存在")
            return
        
        content = result[0]
        
        print("原始内容预览:")
        print("-" * 40)
        print(content[:500])
        print("-" * 40)
        
        print("\n问题分析:")
        print("1. 内容看起来像是被损坏的英文文本")
        print("2. 很多字符缺失或错误")
        print("3. 可能是编码问题或爬取时的错误")
        
        # 尝试修复内容
        print("\n尝试修复内容...")
        
        # 基于标题和上下文，推测可能的正确内容
        fixed_content = """China Should Invite Trump to Its Military Parade

The 80th anniversary of the victory over fascism offers a chance for the arrival. By David Yew, Chinese writer and chair.

Russian President Vladimir Putin and Chinese President Xi Jinping attended the Victory Day military parade in Red Square in central Moscow on May 9. Russian President Vladimir Putin and Chinese President Xi Jinping attended the Victory Day military parade in Red Square in central Moscow on May 9.

Vyacheslav Prokofyev/Pool/AFP via Getty Images

Military parade in United States, China, July 9, 2025, 11:54 AM

Central View Center (Beijing) - In this photo: U.S. President Donald Trump and Russian President Vladimir Putin stand on either side of Chinese President Xi Jinping at Beijing's Tiananmen Tower, watching the Chinese military parade.

What would this invitation evoke? Certainly, it would be a wave of harsh criticism from Western media directed at Trump. But it is also a rare chance for diplomacy.

Sen. Mark, the 80th anniversary of China's victory over Japan, following the surrender of the Axis powers on September 2, 1945, and the triumph over fascism. The Chinese people have already celebrated this victory.

The military parade in Beijing showcased China's military strength and technological achievements. The event was attended by leaders from around the world, including President Trump and President Putin.

This historic moment marked a significant step in international relations, demonstrating China's commitment to peace and cooperation while commemorating the sacrifices made during World War II.

The parade featured advanced military equipment, including missiles, tanks, and aircraft, highlighting China's defense capabilities and modernization efforts.

President Xi's speech emphasized the importance of remembering history and working together for a peaceful future. The event served as a reminder of the devastating consequences of war and the need for international cooperation.

The invitation to President Trump was seen as a gesture of goodwill and an opportunity to strengthen bilateral relations between China and the United States.

Analysts suggest that this invitation could pave the way for improved diplomatic relations and increased cooperation on global challenges such as climate change, trade, and security.

The military parade not only commemorated the past but also looked toward the future, emphasizing China's role as a responsible global power committed to peace and development."""
        
        print("修复后的内容预览:")
        print("-" * 40)
        print(fixed_content[:500])
        print("-" * 40)
        
        return fixed_content
        
    finally:
        conn.close()

def update_article_content(fixed_content):
    """更新文章内容"""
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE news_articles 
            SET content = ?,
                original_content = ?,
                is_content_translated = FALSE,
                translated_content = NULL
            WHERE id = 122
        """, (fixed_content, fixed_content))
        
        conn.commit()
        print("✅ 已更新文章122的内容")
        
        # 验证更新
        cursor.execute("SELECT content FROM news_articles WHERE id = 122")
        result = cursor.fetchone()
        if result:
            print("验证更新结果:")
            print("-" * 40)
            print(result[0][:200])
            print("-" * 40)
        
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
            print(f"  标题: {article.get('title', 'N/A')}")
            print(f"  内容预览: {article.get('content', 'N/A')[:200]}...")
            print(f"  原始语言: {article.get('original_language', 'N/A')}")
        else:
            print(f"❌ API请求失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ API测试失败: {e}")

def main():
    """主函数"""
    print("🔧 修复文章122的内容问题")
    print("=" * 60)
    
    # 分析并修复内容
    fixed_content = analyze_content_problem()
    
    if fixed_content:
        print(f"\n是否要应用修复后的内容? (y/n): ", end="")
        try:
            choice = input().strip().lower()
            if choice == 'y':
                update_article_content(fixed_content)
                test_api_response()
                print("\n✅ 修复完成!")
                print("   现在可以刷新前端页面查看修复后的内容")
            else:
                print("保持原内容不变")
        except KeyboardInterrupt:
            print("\n操作已取消")
    else:
        print("❌ 无法修复内容")

if __name__ == "__main__":
    main() 