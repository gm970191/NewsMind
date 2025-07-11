#!/usr/bin/env python3
"""
网页正文提取模块
从新闻原文链接中提取完整正文内容
"""
import requests
from bs4 import BeautifulSoup
import re
import time
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from news_filter import clean_html_tags

def extract_article_content(url, max_retries=2):
    """
    从新闻链接中提取正文内容
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 移除script和style标签
            for script in soup(["script", "style"]):
                script.decompose()
            
            # 尝试多种正文提取策略
            content = extract_content_by_strategy(soup, url)
            
            if content and len(content.strip()) > 100:
                return clean_html_tags(content)
            
            time.sleep(1)  # 避免请求过快
            
        except Exception as e:
            print(f"     ⚠️  提取失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            continue
    
    return None

def extract_content_by_strategy(soup, url):
    """
    使用多种策略提取正文内容
    """
    # 策略1: 查找常见的正文容器
    content_selectors = [
        'article',
        '.article-content',
        '.story-content',
        '.post-content',
        '.entry-content',
        '.content-body',
        '.article-body',
        '.story-body',
        '.post-body',
        '.entry-body',
        '[class*="content"]',
        '[class*="article"]',
        '[class*="story"]',
        '[class*="post"]',
        '[class*="entry"]'
    ]
    
    for selector in content_selectors:
        elements = soup.select(selector)
        for element in elements:
            # 移除导航、广告等无关内容
            for unwanted in element.select('nav, .nav, .navigation, .ad, .advertisement, .sidebar, .comments'):
                unwanted.decompose()
            
            text = element.get_text(separator=' ', strip=True)
            if len(text) > 200:  # 确保内容足够长
                return text
    
    # 策略2: 查找包含最多文本的段落
    paragraphs = soup.find_all('p')
    if paragraphs:
        # 按长度排序，取最长的几个段落
        paragraphs.sort(key=lambda p: len(p.get_text()), reverse=True)
        content_parts = []
        total_length = 0
        
        for p in paragraphs[:10]:  # 最多取10个段落
            text = p.get_text(strip=True)
            if len(text) > 50:  # 段落至少50字符
                content_parts.append(text)
                total_length += len(text)
                if total_length > 500:  # 总长度超过500字符就停止
                    break
        
        if content_parts:
            return ' '.join(content_parts)
    
    # 策略3: 基于URL特征的特殊处理
    if 'bbc.com' in url:
        return extract_bbc_content(soup)
    elif 'cnn.com' in url:
        return extract_cnn_content(soup)
    elif 'reuters.com' in url:
        return extract_reuters_content(soup)
    elif 'nytimes.com' in url:
        return extract_nytimes_content(soup)
    
    return None

def extract_bbc_content(soup):
    """BBC特定提取逻辑"""
    content = soup.find('div', {'data-component': 'text-block'})
    if content:
        return content.get_text(separator=' ', strip=True)
    return None

def extract_cnn_content(soup):
    """CNN特定提取逻辑"""
    content = soup.find('div', class_='l-container')
    if content:
        paragraphs = content.find_all('p', class_='paragraph')
        if paragraphs:
            return ' '.join([p.get_text(strip=True) for p in paragraphs])
    return None

def extract_reuters_content(soup):
    """Reuters特定提取逻辑"""
    content = soup.find('div', class_='article-body')
    if content:
        return content.get_text(separator=' ', strip=True)
    return None

def extract_nytimes_content(soup):
    """NYTimes特定提取逻辑"""
    content = soup.find('section', {'name': 'articleBody'})
    if content:
        return content.get_text(separator=' ', strip=True)
    return None

def enhance_rss_article(article):
    """
    增强RSS文章内容
    如果RSS只提供摘要，尝试从原文链接提取完整内容
    """
    if not article.get('source_url'):
        return article
    
    # 如果内容已经足够长，不需要提取
    if len(article.get('content', '')) > 300:
        return article
    
    print(f"     🔍 尝试提取完整内容: {article['title'][:50]}...")
    
    extracted_content = extract_article_content(article['source_url'])
    if extracted_content:
        article['content'] = extracted_content
        print(f"     ✅ 成功提取，内容长度: {len(extracted_content)}")
    else:
        print(f"     ⚠️  提取失败，保持原内容")
    
    return article

if __name__ == '__main__':
    # 测试提取功能
    test_url = "https://www.bbc.com/news/world-us-canada-123456"
    print("测试网页内容提取...")
    content = extract_article_content(test_url)
    if content:
        print(f"提取成功，内容长度: {len(content)}")
        print(f"内容预览: {content[:200]}...")
    else:
        print("提取失败") 