#!/usr/bin/env python3
"""
测试API修复的脚本
"""
import requests
import json
import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_api():
    """测试API修复"""
    base_url = "http://localhost:8000"
    
    print("🧪 测试API修复...")
    
    # 测试1: 简单API调用
    print("\n1. 测试简单API调用...")
    try:
        response = requests.get(f"{base_url}/api/v1/news/articles?skip=0&limit=5", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 简单API调用成功，返回 {len(data.get('articles', []))} 篇文章")
        else:
            print(f"❌ 简单API调用失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 简单API调用异常: {e}")
        return False
    
    # 测试2: 带分类的API调用
    print("\n2. 测试带分类的API调用...")
    try:
        response = requests.get(
            f"{base_url}/api/v1/news/articles?skip=0&limit=20&category=国际", 
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 带分类API调用成功，返回 {len(data.get('articles', []))} 篇文章")
        else:
            print(f"❌ 带分类API调用失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 带分类API调用异常: {e}")
        return False
    
    # 测试3: 带日期筛选的API调用
    print("\n3. 测试带日期筛选的API调用...")
    try:
        response = requests.get(
            f"{base_url}/api/v1/news/articles?skip=0&limit=20&category=国际&date=today", 
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 带日期筛选API调用成功，返回 {len(data.get('articles', []))} 篇文章")
        else:
            print(f"❌ 带日期筛选API调用失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 带日期筛选API调用异常: {e}")
        return False
    
    # 测试4: 已处理文章API调用
    print("\n4. 测试已处理文章API调用...")
    try:
        response = requests.get(f"{base_url}/api/v1/ai/processed-articles", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 已处理文章API调用成功，返回 {len(data.get('articles', []))} 篇文章")
        else:
            print(f"❌ 已处理文章API调用失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 已处理文章API调用异常: {e}")
        return False
    
    print("\n🎉 所有API测试通过！")
    return True

def test_database_queries():
    """测试数据库查询修复"""
    print("\n🔍 测试数据库查询修复...")
    
    try:
        from app.core.database import get_db
        from app.services.news_service import NewsRepository
        
        db = next(get_db())
        repo = NewsRepository(db)
        
        # 测试1: 基本查询
        print("1. 测试基本查询...")
        articles = repo.get_articles(skip=0, limit=5)
        print(f"✅ 基本查询成功，返回 {len(articles)} 篇文章")
        
        # 测试2: 带分类查询
        print("2. 测试带分类查询...")
        articles = repo.get_articles(skip=0, limit=5, category="国际")
        print(f"✅ 带分类查询成功，返回 {len(articles)} 篇文章")
        
        # 测试3: 带日期筛选查询
        print("3. 测试带日期筛选查询...")
        articles = repo.get_articles(skip=0, limit=5, date="today")
        print(f"✅ 带日期筛选查询成功，返回 {len(articles)} 篇文章")
        
        # 测试4: 已处理文章查询
        print("4. 测试已处理文章查询...")
        articles_with_content = repo.get_processed_articles_with_content(skip=0, limit=5)
        print(f"✅ 已处理文章查询成功，返回 {len(articles_with_content)} 篇文章")
        
        # 测试5: 统计查询
        print("5. 测试统计查询...")
        stats = repo.get_processing_statistics()
        print(f"✅ 统计查询成功，返回 {len(stats)} 个统计项")
        
        db.close()
        print("\n🎉 所有数据库查询测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 数据库查询测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始测试API修复...")
    
    # 测试数据库查询
    db_success = test_database_queries()
    
    # 测试API调用
    api_success = test_api()
    
    if db_success and api_success:
        print("\n🎉 所有测试通过！API修复成功！")
        sys.exit(0)
    else:
        print("\n❌ 部分测试失败，需要进一步检查")
        sys.exit(1) 