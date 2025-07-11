#!/usr/bin/env python3
"""
数据验证脚本
验证新闻数据更新情况
"""
import requests
import json
from datetime import datetime


def check_latest_articles():
    """检查最新文章"""
    try:
        response = requests.get("http://localhost:8000/api/v1/news/articles?limit=10")
        response.raise_for_status()
        data = response.json()
        
        articles = data.get('articles', [])
        print(f"📊 总文章数量: {len(articles)}")
        
        if articles:
            print(f"\n📰 最新5篇文章:")
            for i, article in enumerate(articles[:5]):
                title = article.get('title', '无标题')
                source = article.get('source_name', '未知来源')
                created_at = article.get('created_at', '未知时间')
                print(f"  {i+1}. {title}")
                print(f"     来源: {source}")
                print(f"     时间: {created_at}")
                print()
        
        return len(articles)
        
    except Exception as e:
        print(f"❌ 检查文章失败: {e}")
        return 0


def check_service_health():
    """检查服务健康状态"""
    try:
        response = requests.get("http://localhost:8000/health")
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ 服务状态: {data.get('status', 'unknown')}")
        print(f"📋 版本: {data.get('version', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 服务检查失败: {e}")
        return False


def main():
    """主函数"""
    print("🔍 NewsMind 数据验证")
    print("=" * 50)
    
    # 检查服务状态
    if not check_service_health():
        print("❌ 后端服务未运行")
        return
    
    print()
    
    # 检查最新文章
    article_count = check_latest_articles()
    
    if article_count > 0:
        print("✅ 数据验证成功！")
        print("📍 前端页面应该能正常显示最新新闻")
    else:
        print("⚠️  没有找到文章数据")


if __name__ == "__main__":
    main() 