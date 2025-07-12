#!/usr/bin/env python3
"""
测试AI处理优化功能
"""
import requests
import json
import time

def test_ai_processing():
    """测试AI处理功能"""
    base_url = "http://localhost:8000/api/v1"
    
    print("🧪 测试AI处理优化功能")
    print("=" * 50)
    
    # 1. 获取未处理的文章
    print("1. 获取未处理的文章...")
    try:
        response = requests.get(f"{base_url}/news/articles?is_processed=false&limit=1")
        if response.status_code == 200:
            articles = response.json().get('articles', [])
            if articles:
                article = articles[0]
                article_id = article['id']
                print(f"   找到未处理文章: ID={article_id}, 标题={article['original_title'][:50]}...")
            else:
                print("   没有找到未处理的文章")
                return
        else:
            print(f"   获取文章失败: {response.status_code}")
            return
    except Exception as e:
        print(f"   请求失败: {e}")
        return
    
    # 2. 测试基础AI处理（简化版）
    print("\n2. 测试基础AI处理（标题翻译+概要生成）...")
    try:
        start_time = time.time()
        response = requests.post(f"{base_url}/ai/process/{article_id}")
        end_time = time.time()
        
        if response.status_code == 200:
            print(f"   ✅ 基础AI处理成功")
            print(f"   耗时: {end_time - start_time:.2f}秒")
            print(f"   响应: {response.json()}")
        else:
            print(f"   ❌ 基础AI处理失败: {response.status_code}")
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   ❌ 基础AI处理异常: {e}")
    
    # 3. 检查处理结果
    print("\n3. 检查基础处理结果...")
    try:
        response = requests.get(f"{base_url}/news/articles/{article_id}")
        if response.status_code == 200:
            article = response.json()
            print(f"   标题翻译: {'✅' if article.get('translated_title') else '❌'}")
            print(f"   中文概要: {'✅' if article.get('summary_zh') else '❌'}")
            print(f"   正文翻译: {'✅' if article.get('translated_content') else '❌'}")
            print(f"   处理状态: {'✅' if article.get('is_processed') else '❌'}")
        else:
            print(f"   获取文章详情失败: {response.status_code}")
    except Exception as e:
        print(f"   检查结果异常: {e}")
    
    # 4. 测试完整AI处理
    print("\n4. 测试完整AI处理（翻译正文+详细总结）...")
    try:
        start_time = time.time()
        response = requests.post(f"{base_url}/ai/process-full/{article_id}")
        end_time = time.time()
        
        if response.status_code == 200:
            print(f"   ✅ 完整AI处理成功")
            print(f"   耗时: {end_time - start_time:.2f}秒")
            print(f"   响应: {response.json()}")
        else:
            print(f"   ❌ 完整AI处理失败: {response.status_code}")
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   ❌ 完整AI处理异常: {e}")
    
    # 5. 检查完整处理结果
    print("\n5. 检查完整处理结果...")
    try:
        response = requests.get(f"{base_url}/news/articles/{article_id}")
        if response.status_code == 200:
            article = response.json()
            print(f"   标题翻译: {'✅' if article.get('translated_title') else '❌'}")
            print(f"   中文概要: {'✅' if article.get('summary_zh') else '❌'}")
            print(f"   详细总结: {'✅' if article.get('detailed_summary_zh') else '❌'}")
            print(f"   正文翻译: {'✅' if article.get('translated_content') else '❌'}")
            print(f"   处理状态: {'✅' if article.get('is_processed') else '❌'}")
            print(f"   内容翻译状态: {'✅' if article.get('is_content_translated') else '❌'}")
        else:
            print(f"   获取文章详情失败: {response.status_code}")
    except Exception as e:
        print(f"   检查结果异常: {e}")
    
    # 6. 测试API接口
    print("\n6. 测试API接口...")
    try:
        # 测试文章状态接口
        response = requests.get(f"{base_url}/ai/article-status/{article_id}")
        if response.status_code == 200:
            status = response.json()
            print(f"   ✅ 文章状态接口正常")
            print(f"   需要处理: {status.get('needs_processing')}")
            print(f"   需要翻译: {status.get('needs_translation')}")
            print(f"   需要摘要: {status.get('needs_summary')}")
        else:
            print(f"   ❌ 文章状态接口失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ API接口测试异常: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 AI处理优化功能测试完成！")

if __name__ == "__main__":
    test_ai_processing() 