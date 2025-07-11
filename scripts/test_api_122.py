#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_api_122():
    """测试文章122的API接口"""
    try:
        url = "http://localhost:3000/news/articles/122"
        print(f"测试API: {url}")
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        print("=== API返回数据 ===")
        print(f"文章ID: {data.get('id')}")
        print(f"翻译标题: {data.get('translated_title')}")
        print(f"原文内容长度: {len(data.get('original_content', ''))}")
        print(f"翻译内容长度: {len(data.get('translated_content', ''))}")
        
        processed_content = data.get('processed_content', {})
        print(f"\n=== processed_content 字段 ===")
        print(f"processed_content: {processed_content}")
        
        if processed_content:
            print(f"\n=== 详细内容 ===")
            print(f"summary_zh: {processed_content.get('summary_zh', 'N/A')}")
            print(f"detailed_summary_zh: {processed_content.get('detailed_summary_zh', 'N/A')}")
            print(f"summary_en: {processed_content.get('summary_en', 'N/A')}")
            print(f"quality_score: {processed_content.get('quality_score', 'N/A')}")
        else:
            print("processed_content为空")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"API请求失败: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        return None
    except Exception as e:
        print(f"测试失败: {e}")
        return None

if __name__ == "__main__":
    test_api_122() 