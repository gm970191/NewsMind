#!/usr/bin/env python3
"""
修复不完整文章脚本
为缺少详细总结和原始内容的文章补充完整内容
"""
import requests
import json
import sys
import time
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

def process_article_with_ai(article_id):
    """使用AI处理文章"""
    try:
        response = requests.post(f"{BASE_URL}/api/v1/ai/process/{article_id}", timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ AI处理文章{article_id}失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ AI处理文章{article_id}异常: {e}")
        return None

def check_article_completeness(article):
    """检查文章完整性"""
    if not article or not article.get('processed_content'):
        return False
    
    pc = article['processed_content']
    required_fields = ['detailed_summary_zh', 'original_content_zh', 'original_content_en']
    
    for field in required_fields:
        if not pc.get(field) or len(pc.get(field, '')) < 100:
            return False
    
    return True

def fix_article_content(article_id):
    """修复单篇文章内容"""
    print(f"\n🔧 修复文章 {article_id}...")
    
    # 获取文章详情
    article = get_article_detail(article_id)
    if not article:
        print(f"❌ 无法获取文章{article_id}详情")
        return False
    
    # 检查是否已完整
    if check_article_completeness(article):
        print(f"✅ 文章{article_id}内容已完整")
        return True
    
    # 使用AI重新处理
    print(f"🤖 使用AI重新处理文章{article_id}...")
    result = process_article_with_ai(article_id)
    
    if result:
        print(f"✅ 文章{article_id}AI处理成功")
        
        # 验证处理结果
        time.sleep(2)  # 等待数据库更新
        updated_article = get_article_detail(article_id)
        if updated_article and check_article_completeness(updated_article):
            print(f"✅ 文章{article_id}内容修复完成")
            return True
        else:
            print(f"⚠️  文章{article_id}内容仍不完整")
            return False
    else:
        print(f"❌ 文章{article_id}AI处理失败")
        return False

def get_incomplete_articles():
    """获取不完整的文章列表"""
    print("🔍 获取不完整文章列表...")
    
    try:
        # 获取已处理文章
        response = requests.get(f"{BASE_URL}/api/v1/ai/processed-articles?limit=100", timeout=10)
        if response.status_code == 200:
            articles = response.json().get('articles', [])
            print(f"✅ 获取已处理文章: {len(articles)}篇")
        else:
            print(f"❌ 获取已处理文章失败: {response.status_code}")
            return []
        
        # 检查哪些文章不完整
        incomplete_articles = []
        for article in articles:
            article_id = article.get('id')
            if article_id:
                article_detail = get_article_detail(article_id)
                if article_detail and not check_article_completeness(article_detail):
                    incomplete_articles.append(article_id)
        
        print(f"📊 发现 {len(incomplete_articles)} 篇不完整文章")
        return incomplete_articles
        
    except Exception as e:
        print(f"❌ 获取不完整文章失败: {e}")
        return []

def main():
    """主函数"""
    print("🚀 开始修复不完整文章...")
    print(f"📅 修复时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 获取不完整文章列表
    incomplete_articles = get_incomplete_articles()
    
    if not incomplete_articles:
        print("✅ 没有发现不完整的文章")
        return
    
    # 修复每篇文章
    success_count = 0
    fail_count = 0
    
    for article_id in incomplete_articles:
        if fix_article_content(article_id):
            success_count += 1
        else:
            fail_count += 1
        
        # 避免请求过于频繁
        time.sleep(1)
    
    # 统计结果
    print(f"\n📊 修复结果统计:")
    print(f"   总文章数: {len(incomplete_articles)}")
    print(f"   修复成功: {success_count}")
    print(f"   修复失败: {fail_count}")
    
    if success_count > 0:
        print(f"\n🎉 成功修复 {success_count} 篇文章")
    if fail_count > 0:
        print(f"⚠️  有 {fail_count} 篇文章修复失败，需要手动检查")

if __name__ == "__main__":
    main() 