#!/usr/bin/env python3
"""
检查文章状态脚本
详细检查每篇文章的处理状态和内容质量
"""
import requests
import json
import sys
from datetime import datetime

# 配置
BASE_URL = "http://localhost:3000"

def get_article_detail(article_id):
    """获取文章详情"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/news/articles/{article_id}", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"❌ 获取文章{article_id}详情失败: {e}")
        return None

def check_article_status(article_id):
    """检查单篇文章状态"""
    article = get_article_detail(article_id)
    if not article:
        return None
    
    print(f"\n📄 文章 {article_id} 状态检查:")
    print(f"   标题: {article.get('title', 'N/A')}")
    print(f"   原文标题: {article.get('original_title', 'N/A')}")
    print(f"   内容长度: {len(article.get('content', ''))}")
    print(f"   处理状态: {'已处理' if article.get('processed_content') else '未处理'}")
    
    if article.get('processed_content'):
        pc = article['processed_content']
        print(f"   中文概要: {len(pc.get('summary_zh', ''))} 字符")
        print(f"   中文详细总结: {len(pc.get('detailed_summary_zh', ''))} 字符")
        print(f"   中文原始内容: {len(pc.get('original_content_zh', ''))} 字符")
        print(f"   英文原始内容: {len(pc.get('original_content_en', ''))} 字符")
        
        # 检查内容质量
        issues = []
        if not pc.get('summary_zh'):
            issues.append("缺少中文概要")
        if not pc.get('detailed_summary_zh'):
            issues.append("缺少中文详细总结")
        if not pc.get('original_content_zh'):
            issues.append("缺少中文原始内容")
        if not pc.get('original_content_en'):
            issues.append("缺少英文原始内容")
        
        if issues:
            print(f"   ⚠️  问题: {', '.join(issues)}")
        else:
            print("   ✅ 内容完整")
    
    return article

def main():
    """主函数"""
    print("🔍 开始检查文章状态...")
    
    # 检查几个关键文章
    article_ids = [62, 56, 54, 52, 49]
    
    for article_id in article_ids:
        check_article_status(article_id)

if __name__ == "__main__":
    main() 