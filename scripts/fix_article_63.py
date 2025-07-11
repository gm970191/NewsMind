#!/usr/bin/env python3
"""
修复文章63的脚本
清理模板化内容并重新处理
"""
import asyncio
import sqlite3
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.simple_ai_processor import AIProcessorButton


async def fix_article_63():
    """修复文章63"""
    try:
        print("🔧 修复文章63")
        print("=" * 50)
        
        # 连接数据库
        conn = sqlite3.connect('backend/newsmind.db')
        cursor = conn.cursor()
        
        # 获取文章63的原始内容
        cursor.execute('SELECT title, content, source_url FROM news_articles WHERE id = 63')
        result = cursor.fetchone()
        
        if not result:
            print("❌ 文章63不存在")
            return
        
        title, content, source_url = result
        print(f"📰 原始标题: {title}")
        print(f"📰 原始内容长度: {len(content)}")
        print(f"📰 原始内容前200字: {content[:200]}...")
        
        # 检查AI处理结果是否有模板化内容
        cursor.execute('SELECT summary_zh, summary_en, translation_zh FROM processed_content WHERE article_id = 63')
        processed = cursor.fetchone()
        
        if processed:
            summary_zh, summary_en, translation_zh = processed
            has_template_content = False
            
            if summary_zh and "这是文章《" in summary_zh:
                print("⚠️  检测到模板化中文摘要")
                has_template_content = True
            
            if translation_zh and "这是文章《" in translation_zh:
                print("⚠️  检测到模板化中文翻译")
                has_template_content = True
            
            if has_template_content:
                print("🧹 清理模板化AI处理记录...")
                cursor.execute('DELETE FROM processed_content WHERE article_id = 63')
                cursor.execute('UPDATE news_articles SET is_processed = 0 WHERE id = 63')
                conn.commit()
                print("✅ 已清理模板化AI处理记录")
        
        conn.close()
        
        # 重新进行AI处理
        print("\n🚀 开始重新AI处理...")
        processor = AIProcessorButton()
        result = await processor.process_article_by_id(63)
        
        print("🚀 处理结果:")
        print(f"  成功: {result['success']}")
        print(f"  消息: {result['message']}")
        
        if result['success']:
            print(f"  处理时间: {result.get('processing_time', 'N/A')} 秒")
            
            # 显示新状态
            new_status = result.get('new_status', {})
            print("\n📊 处理后状态:")
            for key, value in new_status.items():
                print(f"  {key}: {value}")
        
        print("\n✅ 修复完成")
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")


if __name__ == "__main__":
    asyncio.run(fix_article_63()) 