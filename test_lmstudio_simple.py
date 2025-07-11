#!/usr/bin/env python3
"""
简单测试LM Studio API
"""
import requests
import json

def test_lmstudio():
    url = "http://localhost:1234/v1/chat/completions"
    
    data = {
        "model": "qwen2-0.5b-instruct",
        "messages": [
            {"role": "user", "content": "你好"}
        ],
        "max_tokens": 20
    }
    
    try:
        print("🧪 测试LM Studio API...")
        print(f"URL: {url}")
        print(f"数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        response = requests.post(url, json=data, timeout=30)
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                print(f"✅ 成功! 回复: {content}")
                return True
            else:
                print("❌ 响应格式异常")
                return False
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    test_lmstudio() 