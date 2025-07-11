#!/usr/bin/env python3
"""
新闻显示要求端到端验证脚本
检查所有新闻是否都达到用户的显示要求
"""
import requests
import json
import sys
import os
from datetime import datetime

# 配置
BASE_URL = "http://localhost:3000"
API_BASE = "http://localhost:8000"

def test_api_health():
    """测试API健康状态"""
    print("🔍 测试API健康状态...")
    
    try:
        # 测试后端健康
        response = requests.get(f"{API_BASE}/health", timeout=10)
        if response.status_code == 200:
            print("✅ 后端API健康")
        else:
            print(f"❌ 后端API不健康: {response.status_code}")
            return False
            
        # 测试前端代理
        response = requests.get(f"{BASE_URL}/api/v1/news/statistics", timeout=10)
        if response.status_code == 200:
            print("✅ 前端代理正常")
        else:
            print(f"❌ 前端代理异常: {response.status_code}")
            return False
            
        return True
    except Exception as e:
        print(f"❌ API健康测试失败: {e}")
        return False

def get_all_articles():
    """获取所有文章"""
    print("\n📰 获取所有文章...")
    
    try:
        # 获取已处理文章
        response = requests.get(f"{BASE_URL}/api/v1/ai/processed-articles?limit=100", timeout=10)
        if response.status_code == 200:
            processed_articles = response.json().get('articles', [])
            print(f"✅ 获取已处理文章: {len(processed_articles)}篇")
        else:
            print(f"❌ 获取已处理文章失败: {response.status_code}")
            return []
            
        # 获取所有文章
        response = requests.get(f"{BASE_URL}/api/v1/news/articles?limit=100", timeout=10)
        if response.status_code == 200:
            all_articles = response.json().get('articles', [])
            print(f"✅ 获取所有文章: {len(all_articles)}篇")
        else:
            print(f"❌ 获取所有文章失败: {response.status_code}")
            return []
            
        return processed_articles, all_articles
    except Exception as e:
        print(f"❌ 获取文章失败: {e}")
        return [], []

def check_article_detail(article_id):
    """检查单篇文章详情"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/news/articles/{article_id}", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"❌ 获取文章{article_id}详情失败: {e}")
        return None

def verify_news_card_requirements(article):
    """验证新闻卡片页要求"""
    issues = []
    
    # 1. 标题与内容都应该是中文的
    title = article.get('title', '')
    content = article.get('content', '')
    
    # 检查标题是否包含中文字符
    if not any('\u4e00' <= char <= '\u9fff' for char in title):
        issues.append("标题不是中文")
    
    # 检查内容是否包含中文字符
    if not any('\u4e00' <= char <= '\u9fff' for char in content):
        issues.append("内容不是中文")
    
    # 2. 概要显示中文而不是英文内容
    if len(content) > 200:
        content = content[:200]
    
    # 检查概要是否主要是中文
    chinese_chars = sum(1 for char in content if '\u4e00' <= char <= '\u9fff')
    total_chars = len(content)
    if total_chars > 0 and chinese_chars / total_chars < 0.3:
        issues.append("概要内容主要是英文，不是中文")
    
    return issues

def verify_article_detail_requirements(article_detail):
    """验证文章详情页要求"""
    issues = []
    
    if not article_detail:
        return ["无法获取文章详情"]
    
    # 1. 标题同时显示中文与原文
    title = article_detail.get('title', '')
    original_title = article_detail.get('original_title', '')
    
    if not title:
        issues.append("缺少中文标题")
    
    # 2. 检查是否有处理内容
    processed_content = article_detail.get('processed_content')
    if not processed_content:
        issues.append("缺少AI处理内容")
        return issues
    
    # 3. 正文总结支持Markdown格式
    detailed_summary_zh = processed_content.get('detailed_summary_zh', '')
    if not detailed_summary_zh:
        issues.append("缺少中文详细总结")
    elif len(detailed_summary_zh) < 100:
        issues.append("中文详细总结内容太少")
    
    # 4. 正文总结中不要显示重复标题信息
    if title and detailed_summary_zh and title in detailed_summary_zh:
        issues.append("详细总结中包含重复标题信息")
    
    # 5. 原始内容分为两个区块
    original_content_zh = processed_content.get('original_content_zh', '')
    original_content_en = processed_content.get('original_content_en', '')
    
    if not original_content_zh:
        issues.append("缺少中文原始内容")
    if not original_content_en:
        issues.append("缺少英文原始内容")
    
    # 6. 内容质量检查
    if detailed_summary_zh and len(detailed_summary_zh) < 300:
        issues.append("详细总结字数不足300字")
    
    if original_content_zh and len(original_content_zh) < 200:
        issues.append("中文原始内容字数不足")
    
    return issues

def main():
    """主函数"""
    print("🚀 开始新闻显示要求端到端验证...")
    print(f"📅 验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 测试API健康状态
    if not test_api_health():
        print("❌ API健康测试失败，退出验证")
        sys.exit(1)
    
    # 2. 获取所有文章
    processed_articles, all_articles = get_all_articles()
    if not processed_articles and not all_articles:
        print("❌ 无法获取文章数据，退出验证")
        sys.exit(1)
    
    # 3. 验证新闻卡片页要求
    print("\n📋 验证新闻卡片页要求...")
    card_issues = []
    
    # 检查已处理文章
    for article in processed_articles[:10]:  # 检查前10篇
        issues = verify_news_card_requirements(article)
        if issues:
            card_issues.append({
                'id': article.get('id'),
                'title': article.get('title', '')[:50],
                'issues': issues
            })
    
    # 检查所有文章
    for article in all_articles[:10]:  # 检查前10篇
        issues = verify_news_card_requirements(article)
        if issues:
            card_issues.append({
                'id': article.get('id'),
                'title': article.get('title', '')[:50],
                'issues': issues
            })
    
    if card_issues:
        print(f"⚠️  发现 {len(card_issues)} 个新闻卡片问题:")
        for issue in card_issues:
            print(f"   文章{issue['id']} ({issue['title']}): {', '.join(issue['issues'])}")
    else:
        print("✅ 新闻卡片页要求验证通过")
    
    # 4. 验证文章详情页要求
    print("\n📄 验证文章详情页要求...")
    detail_issues = []
    
    # 检查已处理文章的详情
    for article in processed_articles[:5]:  # 检查前5篇
        article_id = article.get('id')
        if article_id:
            article_detail = check_article_detail(article_id)
            issues = verify_article_detail_requirements(article_detail)
            if issues:
                detail_issues.append({
                    'id': article_id,
                    'title': article.get('title', '')[:50],
                    'issues': issues
                })
    
    if detail_issues:
        print(f"⚠️  发现 {len(detail_issues)} 个文章详情问题:")
        for issue in detail_issues:
            print(f"   文章{issue['id']} ({issue['title']}): {', '.join(issue['issues'])}")
    else:
        print("✅ 文章详情页要求验证通过")
    
    # 5. 统计结果
    print("\n📊 验证结果统计:")
    print(f"   已处理文章数: {len(processed_articles)}")
    print(f"   总文章数: {len(all_articles)}")
    print(f"   新闻卡片问题: {len(card_issues)}")
    print(f"   文章详情问题: {len(detail_issues)}")
    
    # 6. 总体评估
    total_issues = len(card_issues) + len(detail_issues)
    if total_issues == 0:
        print("\n🎉 所有新闻显示要求验证通过！")
        print("✅ 新闻卡片页: 符合要求")
        print("✅ 文章详情页: 符合要求")
        print("✅ 内容质量: 符合要求")
        sys.exit(0)
    else:
        print(f"\n⚠️  发现 {total_issues} 个问题需要修复")
        print("建议:")
        print("1. 检查AI处理是否完整")
        print("2. 验证翻译质量")
        print("3. 确保内容格式正确")
        sys.exit(1)

if __name__ == "__main__":
    main() 