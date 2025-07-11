#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_api_correct():
    """测试正确的API路径"""
    try:
        url = "http://localhost:8000/api/v1/news/articles/122"
        print(f"测试API: {url}")
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        print("=== API返回数据 ===")
        print(f"文章ID: {data.get('id')}")
        print(f"翻译标题: {data.get('translated_title')}")
        
        processed_content = data.get('processed_content', {})
        print(f"\n=== processed_content 字段 ===")
        print(f"processed_content: {processed_content}")
        
        if processed_content:
            print(f"\n=== 详细内容 ===")
            print(f"summary_zh: {processed_content.get('summary_zh', 'N/A')}")
            print(f"detailed_summary_zh: {processed_content.get('detailed_summary_zh', 'N/A')}")
        else:
            print("processed_content为空")
        
        return data
        
    except Exception as e:
        print(f"测试失败: {e}")
        return None

if __name__ == "__main__":
    test_api_correct() 