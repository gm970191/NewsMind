# -*- coding: utf-8 -*-
"""
新闻过滤与自动分类工具 - 宽松版
只要是有意义的新闻就保留
"""
import sys
import os
import re
import html
sys.path.insert(0, os.path.dirname(__file__))
from filter_config import FILTER_CONFIG

def clean_html_tags(text):
    """
    彻底清除HTML标签和特殊字符
    """
    if not text:
        return ""
    
    # 解码HTML实体
    text = html.unescape(text)
    
    # 移除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    
    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    
    # 移除特殊符号和无效字符
    text = re.sub(r'[&nbsp;|&amp;|&lt;|&gt;|&quot;|&#39;]', '', text)
    
    # 移除控制字符
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    return text.strip()

def is_valid_content(text, min_length=30, min_chinese_ratio=0.0):
    """
    判断内容是否有效 - 更宽松的条件
    - min_length: 最小字符长度（降为30）
    - min_chinese_ratio: 中文字符最小比例（允许为0，支持英文新闻）
    """
    if not text or len(text) < min_length:
        return False
    
    # 允许英文新闻，去除中文比例限制
    meaningful_chars = len(re.findall(r'[\u4e00-\u9fff\w]', text))
    total_chars = len(text)
    meaningful_ratio = meaningful_chars / total_chars if total_chars > 0 else 0
    
    # 更宽松的比例要求
    return meaningful_ratio >= 0.2

def match_keywords(text, keywords):
    """关键词匹配"""
    for kw in keywords:
        if kw.lower() in text.lower():
            return True
    return False

def filter_article(title, content):
    """
    宽松的新闻过滤逻辑。
    只要内容有效就保留，尝试分类，如果无法分类则归为"其他"。
    返回：(是否保留, 分类名或"其他", 清洗后的内容)
    """
    # 清洗HTML标签
    clean_title = clean_html_tags(title)
    clean_content = clean_html_tags(content)
    
    # 检查内容有效性 - 只要标题或内容有一个有效就保留
    if not is_valid_content(clean_title, min_length=5) and not is_valid_content(clean_content, min_length=30):
        return False, None, ""
    
    # 屏蔽明显无意义的内容
    text = f'{clean_title} {clean_content}'
    if match_keywords(text, FILTER_CONFIG['blocked_keywords']):
        return False, None, ""
    
    # 尝试分类，如果无法分类则归为"其他"
    for cat, info in FILTER_CONFIG['categories'].items():
        if match_keywords(text, info['keywords']):
            return True, cat, clean_content
    
    # 如果无法分类但有意义，归为"其他"
    return True, "其他", clean_content

def validate_article_data(title, content, url=None):
    """
    验证文章数据的完整性 - 更宽松的条件
    """
    if not title or not content:
        return False, "标题或内容为空"
    
    clean_title = clean_html_tags(title)
    clean_content = clean_html_tags(content)
    
    if not is_valid_content(clean_title, min_length=3):
        return False, "标题无效"
    
    if not is_valid_content(clean_content, min_length=50):
        return False, "内容无效"
    
    return True, "数据有效"

if __name__ == '__main__':
    # 测试HTML清洗
    test_html = '<p style="text-align: left;"><span style="font-family: Oxygen;">&nbsp;</span>这是一段测试内容</p>'
    cleaned = clean_html_tags(test_html)
    print(f'HTML清洗测试: {cleaned}')
    
    # 测试内容有效性
    valid = is_valid_content(cleaned)
    print(f'内容有效性: {valid}')
    
    # 测试过滤
    test_title = '中国AI芯片产业迎来新突破'
    test_content = '近日，华为发布了新一代AI芯片，推动中国科技进步。'
    keep, cat, clean_content = filter_article(test_title, test_content)
    print(f'保留: {keep}, 分类: {cat}, 清洗后内容: {clean_content[:50]}...')
    
    test_title2 = '八卦明星恋情曝光'
    keep2, cat2, clean_content2 = filter_article(test_title2, '')
    print(f'保留: {keep2}, 分类: {cat2}') 