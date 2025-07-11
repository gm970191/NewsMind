#!/usr/bin/env python3
"""
直接调用DeepSeek API测试
绕过langchain依赖问题
"""
import requests
import json
import time
import os

def test_deepseek_api():
    """直接测试DeepSeek API"""
    
    # 检查API密钥
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ 未设置DEEPSEEK_API_KEY环境变量")
        print("请在.env文件中设置您的API密钥")
        return
    
    print("🚀 开始直接测试DeepSeek API...")
    
    # API配置
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 测试内容
    test_content = "据媒体报道，美国爱国者导弹库存仅为五角大楼需求的25%。这一情况引发了美国军方对防空能力的担忧。"
    
    print(f"📝 测试内容长度: {len(test_content)} 字符")
    
    # 测试标准配置
    print("\n" + "="*50)
    print("🔧 测试标准配置")
    print("="*50)
    
    standard_data = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": "你是一个专业的新闻编辑，请为以下新闻内容生成一个详细、准确的中文摘要。要求：1. 摘要长度控制在200-300字之间 2. 突出新闻的核心信息、关键事实和重要细节 3. 使用客观、准确的语言 4. 保持新闻的时效性和重要性 5. 包含新闻的背景信息、主要人物、时间地点等关键要素 6. 避免主观评价和推测 7. 确保摘要内容完整，能够帮助读者快速了解新闻全貌。请直接返回摘要内容，不要添加任何额外的说明或格式。"
            },
            {
                "role": "user",
                "content": f"新闻内容：\n\n{test_content}"
            }
        ],
        "temperature": 0.3,
        "max_tokens": 4000
    }
    
    start_time = time.time()
    try:
        response = requests.post(url, headers=headers, json=standard_data)
        time_standard = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            summary = result['choices'][0]['message']['content'].strip()
            print(f"✅ 标准配置成功: {time_standard:.1f}秒")
            print(f"📝 摘要长度: {len(summary)} 字符")
            print(f"📝 摘要内容: {summary[:100]}...")
        else:
            print(f"❌ 标准配置失败: {response.status_code} - {response.text}")
            time_standard = 0
    except Exception as e:
        print(f"❌ 标准配置失败: {e}")
        time_standard = 0
    
    # 测试优化配置
    print("\n" + "="*50)
    print("⚡ 测试优化配置")
    print("="*50)
    
    fast_data = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": "为以下新闻生成100字以内的中文摘要，突出核心信息："
            },
            {
                "role": "user",
                "content": test_content
            }
        ],
        "temperature": 0.1,
        "max_tokens": 800
    }
    
    start_time = time.time()
    try:
        response = requests.post(url, headers=headers, json=fast_data)
        time_fast = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            summary = result['choices'][0]['message']['content'].strip()
            print(f"✅ 优化配置成功: {time_fast:.1f}秒")
            print(f"📝 摘要长度: {len(summary)} 字符")
            print(f"📝 摘要内容: {summary[:100]}...")
        else:
            print(f"❌ 优化配置失败: {response.status_code} - {response.text}")
            time_fast = 0
    except Exception as e:
        print(f"❌ 优化配置失败: {e}")
        time_fast = 0
    
    # 比较结果
    print("\n" + "="*50)
    print("📊 速度对比结果")
    print("="*50)
    
    if time_standard > 0 and time_fast > 0:
        speedup = time_standard / time_fast
        print(f"⏱️  标准配置: {time_standard:.1f}秒")
        print(f"⚡ 优化配置: {time_fast:.1f}秒")
        print(f"🚀 速度提升: {speedup:.1f}倍")
        
        if speedup > 1.5:
            print("🎉 优化配置显著提升了处理速度！")
        elif speedup > 1.1:
            print("👍 优化配置有一定速度提升")
        else:
            print("⚠️  速度提升不明显")
    else:
        print("❌ 无法进行速度对比，因为处理失败")
    
    # 测试翻译
    print("\n" + "="*50)
    print("🌐 测试翻译速度")
    print("="*50)
    
    english_content = "According to media reports, the US Patriot missile inventory is only 25% of the Pentagon's requirements. This situation has raised concerns about the US military's air defense capabilities."
    
    translate_data = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": "将以下英文新闻翻译成中文，保持原意，使用流畅的中文表达。直接返回翻译结果。"
            },
            {
                "role": "user",
                "content": english_content
            }
        ],
        "temperature": 0.1,
        "max_tokens": 800
    }
    
    start_time = time.time()
    try:
        response = requests.post(url, headers=headers, json=translate_data)
        time_translate = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            translation = result['choices'][0]['message']['content'].strip()
            print(f"✅ 翻译成功: {time_translate:.1f}秒")
            print(f"📝 翻译长度: {len(translation)} 字符")
            print(f"📝 翻译内容: {translation[:100]}...")
        else:
            print(f"❌ 翻译失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 翻译失败: {e}")

if __name__ == "__main__":
    test_deepseek_api() 