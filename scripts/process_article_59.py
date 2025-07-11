#!/usr/bin/env python3
"""
专门处理文章59的脚本
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.simple_ai_processor import AIProcessorButton


async def process_article_59():
    """处理文章59"""
    try:
        processor = AIProcessorButton()
        
        print("🔍 专门处理文章59")
        print("=" * 50)
        
        # 检查文章59的状态
        status = processor.check_processing_status(59)
        print("📊 文章59当前状态:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        print("\n" + "=" * 50)
        
        # 处理文章59
        result = await processor.process_article_by_id(59)
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
        
        print("\n✅ 处理完成")
        
    except Exception as e:
        print(f"❌ 处理失败: {e}")


if __name__ == "__main__":
    asyncio.run(process_article_59()) 