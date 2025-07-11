#!/usr/bin/env python3
"""
继续批量修复文章的脚本
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.batch_fix_articles import BatchArticleFixer


async def continue_batch_fix():
    """继续批量修复"""
    try:
        fixer = BatchArticleFixer()
        
        print("🤖 继续批量文章修复")
        print("=" * 60)
        
        # 继续修复更多文章
        result = await fixer.batch_fix_articles(max_articles=10)  # 这次处理10篇
        
        print("\n" + "=" * 60)
        print("📊 修复结果")
        print("=" * 60)
        print(f"总文章数: {result['total']}")
        print(f"修复成功: {result['fixed']}")
        print(f"修复失败: {result['failed']}")
        print(f"消息: {result['message']}")
        
        if result['results']:
            print(f"\n📝 详细结果:")
            for r in result['results']:
                status = "✅" if r['success'] else "❌"
                print(f"  {status} 文章 {r['article_id']}: {r['message']} ({r['processing_time']:.1f}s)")
        
        print("\n✅ 继续批量修复完成")
        
    except Exception as e:
        print(f"❌ 继续批量修复失败: {e}")


if __name__ == "__main__":
    asyncio.run(continue_batch_fix()) 