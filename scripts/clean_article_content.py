#!/usr/bin/env python3
"""
清理文章内容，移除HTML标签并优化内容质量
"""
import sys
import re
from pathlib import Path

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.database import get_db
from app.models.news import NewsArticle
from bs4 import BeautifulSoup

def clean_content(content):
    """清理文章内容"""
    if not content:
        return content
    
    # 使用BeautifulSoup移除HTML标签
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text()
    
    # 清理多余的空白字符
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 移除常见的无用文本
    text = re.sub(r'^(Read more|Continue reading|More info|Learn more)', '', text, flags=re.IGNORECASE)
    
    return text

def optimize_article_content():
    """优化文章内容"""
    print("🧹 开始清理和优化文章内容...")
    
    db = next(get_db())
    
    try:
        # 获取所有文章
        articles = db.query(NewsArticle).all()
        
        cleaned_count = 0
        improved_count = 0
        
        for article in articles:
            original_content = article.original_content
            if not original_content:
                continue
            
            # 清理内容
            cleaned_content = clean_content(original_content)
            
            # 如果清理后的内容更短，说明原来有HTML标签
            if len(cleaned_content) < len(original_content):
                article.original_content = cleaned_content
                cleaned_count += 1
                print(f"✅ 清理文章 {article.id}: {len(original_content)} -> {len(cleaned_content)} 字符")
            
            # 如果内容太短（少于50字符），尝试用标题补充
            if len(cleaned_content) < 50 and article.original_title:
                enhanced_content = f"{article.original_title}. {cleaned_content}"
                if len(enhanced_content) > len(cleaned_content):
                    article.original_content = enhanced_content
                    improved_count += 1
                    print(f"📝 增强文章 {article.id}: {len(cleaned_content)} -> {len(enhanced_content)} 字符")
        
        # 提交更改
        db.commit()
        
        print(f"\n📊 清理结果:")
        print(f"   清理HTML标签: {cleaned_count} 篇")
        print(f"   内容增强: {improved_count} 篇")
        print(f"   总计处理: {cleaned_count + improved_count} 篇")
        
        # 显示清理后的统计
        print(f"\n📈 清理后的内容长度统计:")
        short_count = 0
        medium_count = 0
        long_count = 0
        
        for article in articles:
            content_length = len(article.original_content or "")
            if content_length < 100:
                short_count += 1
            elif content_length < 500:
                medium_count += 1
            else:
                long_count += 1
        
        print(f"   短文章 (<100字符): {short_count} 篇")
        print(f"   中等文章 (100-500字符): {medium_count} 篇")
        print(f"   长文章 (≥500字符): {long_count} 篇")
        print(f"   总计: {len(articles)} 篇")
        
    except Exception as e:
        print(f"❌ 清理失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    optimize_article_content() 