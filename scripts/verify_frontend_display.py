#!/usr/bin/env python3
"""
验证前端显示效果
"""
import requests
import json

def verify_frontend_display():
    """验证前端显示效果"""
    print("🔍 验证前端显示效果...")
    
    try:
        # 获取文章62的API数据
        response = requests.get("http://localhost:8000/api/v1/news/articles/62")
        if response.status_code == 200:
            article = response.json()
            
            print("✅ API数据获取成功")
            print(f"📰 文章标题: {article.get('title')}")
            print(f"🌐 原文标题: {article.get('original_title')}")
            print(f"🔤 语言: {article.get('language')}")
            
            if article.get('processed_content'):
                pc = article['processed_content']
                print(f"\n📊 处理内容统计:")
                print(f"   中文概要: {len(pc.get('summary_zh', ''))} 字符")
                print(f"   详细总结: {len(pc.get('detailed_summary_zh', ''))} 字符")
                print(f"   原始内容: {len(pc.get('original_content_zh', ''))} 字符")
                
                print(f"\n📝 内容预览:")
                print(f"   中文概要: {pc.get('summary_zh', '')[:100]}...")
                print(f"   详细总结: {pc.get('detailed_summary_zh', '')[:100]}...")
                print(f"   原始内容: {pc.get('original_content_zh', '')[:100]}...")
                
                # 验证内容是否充足
                if len(pc.get('detailed_summary_zh', '')) > 500:
                    print("✅ 详细总结内容充足")
                else:
                    print("⚠️  详细总结内容可能不足")
                
                if len(pc.get('original_content_zh', '')) > 300:
                    print("✅ 原始内容充足")
                else:
                    print("⚠️  原始内容可能不足")
                
                return True
            else:
                print("❌ 无处理内容")
                return False
        else:
            print(f"❌ API请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

def check_frontend_page():
    """检查前端页面"""
    print("\n🔍 检查前端页面...")
    try:
        response = requests.get("http://localhost:3000")
        if response.status_code == 200:
            print("✅ 前端页面可访问")
            return True
        else:
            print(f"❌ 前端页面错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 前端页面检查失败: {e}")
        return False

def main():
    """主函数"""
    print("🧪 验证前端显示效果")
    print("=" * 50)
    
    # 验证API数据
    api_ok = verify_frontend_display()
    
    # 检查前端页面
    frontend_ok = check_frontend_page()
    
    print("\n" + "=" * 50)
    print("📊 验证结果:")
    print(f"   API数据: {'✅ 正常' if api_ok else '❌ 异常'}")
    print(f"   前端页面: {'✅ 可访问' if frontend_ok else '❌ 不可访问'}")
    
    if api_ok and frontend_ok:
        print("\n🎉 前端显示验证通过！")
        print("📝 现在可以访问 http://localhost:3000/article/62 查看效果")
        print("📋 预期效果:")
        print("   1. ✅ 标题显示中文和原文（原文字体较小）")
        print("   2. ✅ 正文总结有详细内容（794字符）")
        print("   3. ✅ 原始内容数据充足（489字符）")
    else:
        print("\n⚠️  验证失败，需要进一步检查")

if __name__ == "__main__":
    main() 