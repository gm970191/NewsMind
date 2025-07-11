#!/usr/bin/env python3
"""
验证文章54的效果
"""
import requests

def verify_article_54():
    """验证文章54的效果"""
    try:
        response = requests.get("http://localhost:8000/api/v1/news/articles/54")
        if response.status_code == 200:
            article = response.json()
            
            print("文章54验证结果:")
            print(f"标题: {article.get('title')}")
            print(f"语言: {article.get('language')}")
            print(f"是否已处理: {article.get('is_processed')}")
            
            pc = article.get('processed_content', {})
            if pc:
                print(f"\n处理内容统计:")
                print(f"概要长度: {len(pc.get('summary_zh', ''))} 字符")
                print(f"详细总结长度: {len(pc.get('detailed_summary_zh', ''))} 字符")
                print(f"原始内容长度: {len(pc.get('original_content_zh', ''))} 字符")
                
                # 检查详细总结是否包含Markdown格式
                detailed_summary = pc.get('detailed_summary_zh', '')
                if '## ' in detailed_summary:
                    print("✅ 详细总结包含Markdown格式")
                else:
                    print("❌ 详细总结不包含Markdown格式")
                
                # 检查原始内容是否为双语
                original_content = pc.get('original_content_zh', '')
                if '---' in original_content:
                    print("✅ 原始内容为双语版本")
                else:
                    print("❌ 原始内容不是双语版本")
                
                print(f"\n📝 现在可以访问: http://localhost:3000/article/54")
                print("预期效果:")
                print("1. ✅ 标题显示中文和原文")
                print("2. ✅ 正文总结支持Markdown格式")
                print("3. ✅ 原始正文显示英文原文")
                print("4. ✅ 中文翻译显示中文翻译内容")
                
            else:
                print("❌ 无处理内容")
        else:
            print(f"❌ API错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 验证失败: {e}")

if __name__ == "__main__":
    verify_article_54() 