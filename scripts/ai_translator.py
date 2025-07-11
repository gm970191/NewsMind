#!/usr/bin/env python3
"""
AI翻译模块
支持多语种新闻自动翻译为中文
"""
import re
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# 自动加载.env文件
try:
    from dotenv import load_dotenv
    # 尝试多个可能的.env文件路径
    env_paths = [
        os.path.join(os.path.dirname(__file__), '../backend/.env'),
        os.path.join(os.path.dirname(__file__), '../.env'),
        os.path.join(os.path.dirname(__file__), '../../backend/.env'),
        '.env'
    ]
    for env_path in env_paths:
        if os.path.exists(env_path):
            load_dotenv(env_path)
            print(f"     ✅ 已加载环境变量文件: {env_path}")
            break
except ImportError:
    print("     ⚠️  python-dotenv未安装，尝试直接读取环境变量")

from news_filter import clean_html_tags
import requests

def detect_language(text):
    """
    检测文本语言
    返回: 'zh', 'en', 'ja', 'fr', 'de', 'other'
    """
    if not text:
        return 'other'
    
    # 中文字符检测
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    total_chars = len(re.findall(r'[a-zA-Z\u4e00-\u9fff]', text))
    
    if total_chars > 0 and chinese_chars / total_chars > 0.3:
        return 'zh'
    
    # 日文字符检测
    japanese_chars = len(re.findall(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf]', text))
    if japanese_chars > 0:
        return 'ja'
    
    # 韩文字符检测
    korean_chars = len(re.findall(r'[\uac00-\ud7af]', text))
    if korean_chars > 0:
        return 'ko'
    
    # 阿拉伯文字符检测
    arabic_chars = len(re.findall(r'[\u0600-\u06ff]', text))
    if arabic_chars > 0:
        return 'ar'
    
    # 俄文字符检测
    russian_chars = len(re.findall(r'[\u0400-\u04ff]', text))
    if russian_chars > 0:
        return 'ru'
    
    # 英文检测（默认）
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    if english_chars > 0:
        return 'en'
    
    return 'other'

def translate_with_openai(text, target_lang='zh'):
    """
    使用OpenAI API翻译文本
    """
    try:
        import openai
        
        # 检查是否有API密钥
        if not os.getenv('OPENAI_API_KEY'):
            print("     ⚠️  OpenAI API密钥未设置，跳过翻译")
            return None
        
        client = openai.OpenAI()
        
        # 构建翻译提示
        system_prompt = f"你是一个专业的新闻翻译专家。请将以下文本翻译成{target_lang}，保持新闻的准确性和可读性。只返回翻译结果，不要添加任何解释。"
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            max_tokens=2000,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"     ⚠️  OpenAI翻译失败: {e}")
        return None

def translate_with_google_translate(text, target_lang='zh'):
    """
    使用Google Translate API翻译文本
    """
    try:
        from googletrans import Translator
        
        translator = Translator()
        result = translator.translate(text, dest=target_lang)
        return result.text
        
    except Exception as e:
        print(f"     ⚠️  Google翻译失败: {e}")
        return None

def translate_with_deepseek(text, target_lang='zh'):
    """
    使用DeepSeek API翻译文本
    """
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("     ⚠️  DeepSeek API密钥未设置，跳过翻译")
        return None
    url = 'https://api.deepseek.com/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    # DeepSeek支持多轮对话，这里只用单轮
    system_prompt = f"你是一个专业的新闻翻译专家。请将以下文本翻译成{target_lang}，保持新闻的准确性和可读性。只返回翻译结果，不要添加任何解释。"
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        "max_tokens": 2048,
        "temperature": 0.3
    }
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        return result['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"     ⚠️  DeepSeek翻译失败: {e}")
        return None

def translate_text(text, target_lang='zh'):
    """
    翻译文本到目标语言
    优先使用DeepSeek，其次OpenAI，最后Google Translate
    """
    if not text or len(text.strip()) < 10:
        return text
    # 检测源语言
    source_lang = detect_language(text)
    if source_lang == 'zh':
        return text
    print(f"     🌐 检测到{source_lang}语言，开始翻译...")
    # 1. DeepSeek
    translated = translate_with_deepseek(text, target_lang)
    if translated:
        print(f"     ✅ DeepSeek翻译完成")
        return translated
    # 2. OpenAI
    translated = translate_with_openai(text, target_lang)
    if translated:
        print(f"     ✅ OpenAI翻译完成")
        return translated
    # 3. Google Translate
    translated = translate_with_google_translate(text, target_lang)
    if translated:
        print(f"     ✅ Google翻译完成")
        return translated
    print(f"     ⚠️  翻译失败，保持原文")
    return text

def translate_article(article):
    """
    翻译文章内容
    """
    if not article.get('title') or not article.get('content'):
        return article
    
    # 翻译标题
    original_title = article['title']
    translated_title = translate_text(original_title)
    if translated_title and translated_title != original_title:
        article['title'] = translated_title
        article['original_title'] = original_title
    
    # 翻译内容
    original_content = article['content']
    translated_content = translate_text(original_content)
    if translated_content and translated_content != original_content:
        article['content'] = translated_content
        article['original_content'] = original_content
    
    return article

def batch_translate_articles(articles, max_articles=10):
    """
    批量翻译文章（限制数量避免API费用过高）
    """
    if not articles:
        return articles
    
    # 限制翻译数量
    articles_to_translate = articles[:max_articles]
    remaining_articles = articles[max_articles:]
    
    print(f"     🔄 开始批量翻译 {len(articles_to_translate)} 篇文章...")
    
    for i, article in enumerate(articles_to_translate, 1):
        print(f"     📝 翻译进度: {i}/{len(articles_to_translate)}")
        translated_article = translate_article(article)
        articles_to_translate[i-1] = translated_article
    
    # 合并结果
    return articles_to_translate + remaining_articles

if __name__ == '__main__':
    # 测试翻译功能
    test_texts = [
        "Trump pledges 50% tariffs against Brazil",
        "AI technology breakthrough in China",
        "ニュース速報：日本経済の最新動向",
        "L'actualité en France aujourd'hui"
    ]
    
    print("测试AI翻译功能...")
    for text in test_texts:
        lang = detect_language(text)
        print(f"原文 ({lang}): {text}")
        translated = translate_text(text)
        print(f"翻译: {translated}")
        print("-" * 50) 