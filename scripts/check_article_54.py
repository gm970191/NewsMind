#!/usr/bin/env python3
"""
检查文章54的状态
"""
import requests

def check_article_54():
    """检查文章54的状态"""
    try:
        response = requests.get("http://localhost:8000/api/v1/news/articles/54")
        if response.status_code == 200:
            article = response.json()
            
            print("文章54状态:")
            print(f"标题: {article.get('title')}")
            print(f"语言: {article.get('language')}")
            print(f"是否已处理: {article.get('is_processed')}")
            
            pc = article.get('processed_content', {})
            if pc:
                print(f"概要长度: {len(pc.get('summary_zh', ''))} 字符")
                print(f"详细总结长度: {len(pc.get('detailed_summary_zh', ''))} 字符")
                print(f"原始内容长度: {len(pc.get('original_content_zh', ''))} 字符")
                
                print(f"\n概要预览: {pc.get('summary_zh', '')[:100]}...")
                print(f"详细总结预览: {pc.get('detailed_summary_zh', '')[:100]}...")
                print(f"原始内容预览: {pc.get('original_content_zh', '')[:100]}...")
            else:
                print("无处理内容")
        else:
            print(f"API错误: {response.status_code}")
            
    except Exception as e:
        print(f"检查失败: {e}")

if __name__ == "__main__":
    check_article_54() 