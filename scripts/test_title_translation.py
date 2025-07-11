#!/usr/bin/env python3
"""
测试标题翻译功能
"""
import sys
from pathlib import Path

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.services.ai_processor import AIProcessor
from app.services.news_service import NewsRepository
from app.core.database import SessionLocal
import asyncio

async def test_title_translation():
    """测试标题翻译功能"""
    print("🧪 开始测试标题翻译功能...")
    
    db = SessionLocal()
    repo = NewsRepository(db)
    
    try:
        # 创建AI处理器
        processor = AIProcessor(repo)
        
        # 测试标题
        test_title = "Israel-Gaza War"
        
        print(f"📝 测试标题: {test_title}")
        
        # 测试标题翻译
        print("\n🔄 开始翻译标题...")
        translation = await processor._translate_title_to_chinese(test_title)
        
        if translation:
            print(f"✅ 标题翻译成功: {translation}")
        else:
            print("❌ 标题翻译失败: 返回None")
            
    except Exception as e:
        print(f"❌ 标题翻译测试出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_title_translation()) 