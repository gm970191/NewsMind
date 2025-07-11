#!/usr/bin/env python3
"""
测试翻译功能
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

async def test_translation():
    """测试翻译功能"""
    print("🧪 开始测试翻译功能...")
    
    db = SessionLocal()
    repo = NewsRepository(db)
    
    try:
        # 创建AI处理器
        print("🔧 创建AI处理器...")
        processor = AIProcessor(repo)
        print(f"✅ AI处理器创建成功，LLM类型: {type(processor.llm).__name__}")
        
        # 测试内容
        test_content = "The Marines will be assigned tasks related to transportation, logistics and administrative functions. They're not authorized to make arrests."
        
        print(f"📝 测试内容: {test_content}")
        print(f"📏 内容长度: {len(test_content)} 字符")
        
        # 测试翻译
        print("\n🔄 开始翻译...")
        try:
            translation = await processor._translate_to_chinese(test_content)
            
            if translation:
                print(f"✅ 翻译成功: {translation}")
                print(f"📏 翻译长度: {len(translation)} 字符")
            else:
                print("❌ 翻译失败: 返回None")
        except Exception as e:
            print(f"❌ 翻译过程中出错: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ 翻译测试出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_translation()) 