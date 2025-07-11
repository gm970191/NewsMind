#!/usr/bin/env python3
"""
测试配置文件
"""
import os

# 设置测试用的API密钥（请替换为您的实际密钥）
os.environ['DEEPSEEK_API_KEY'] = 'your_deepseek_api_key_here'

print("⚠️  请将 'your_deepseek_api_key_here' 替换为您的实际DeepSeek API密钥")
print("然后运行: python scripts/direct_api_test.py") 