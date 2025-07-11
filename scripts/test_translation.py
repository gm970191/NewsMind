#!/usr/bin/env python3
"""
测试AI翻译功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from ai_translator import detect_language, translate_text

def test_translation():
    """测试翻译功能"""
    print("🧪 测试AI翻译功能...")
    print("=" * 60)
    
    test_texts = [
        "Trump pledges 50% tariffs against Brazil",
        "AI technology breakthrough in China",
        "ニュース速報：日本経済の最新動向",
        "L'actualité en France aujourd'hui",
        "Deutsche Wirtschaft im Aufschwung"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📝 测试 {i}:")
        print(f"原文: {text}")
        
        # 检测语言
        lang = detect_language(text)
        print(f"检测语言: {lang}")
        
        # 翻译
        translated = translate_text(text)
        print(f"翻译结果: {translated}")
        print("-" * 40)

if __name__ == '__main__':
    test_translation() 