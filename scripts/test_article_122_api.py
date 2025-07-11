#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_article_122_api():
    """测试文章122的API接口"""
    
    try:
        url = "http://localhost:3000/article/122"
        print(f"正在测试API: {url}")
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        print("\n=== 文章122 API测试结果 ===")
        print(f"状态码: {response.status_code}")
        print(f"标题: {data.get('translated_title', 'N/A')}")
        print(f"摘要: {data.get('summary_zh', 'N/A')[:100]}..." if data.get('summary_zh') else 'N/A')
        print(f"翻译内容长度: {len(data.get('translated_content', ''))}" if data.get('translated_content') else 0)
        print(f"原文内容长度: {len(data.get('original_content', ''))}" if data.get('original_content') else 0)
        
        # 检查关键字段
        print("\n=== 字段检查 ===")
        print(f"translated_title: {'✓' if data.get('translated_title') else '✗'}")
        print(f"summary_zh: {'✓' if data.get('summary_zh') else '✗'}")
        print(f"translated_content: {'✓' if data.get('translated_content') else '✗'}")
        print(f"original_content: {'✓' if data.get('original_content') else '✗'}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"API请求失败: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        return False
    except Exception as e:
        print(f"测试失败: {e}")
        return False

if __name__ == "__main__":
    test_article_122_api() 