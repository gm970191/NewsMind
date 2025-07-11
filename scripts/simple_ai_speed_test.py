#!/usr/bin/env python3
"""
简化的AI处理速度测试
直接测试DeepSeek API，不依赖后端框架
"""
import asyncio
import time
import os
from typing import Optional

# 尝试导入DeepSeek
try:
    from langchain_deepseek import ChatDeepSeek
    from langchain.schema import SystemMessage, HumanMessage
    print("✅ 成功导入DeepSeek")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("请先解决依赖冲突问题")
    exit(1)

async def test_deepseek_speed():
    """测试DeepSeek API速度"""
    
    # 检查API密钥
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ 未设置DEEPSEEK_API_KEY环境变量")
        print("请在.env文件中设置您的API密钥")
        return
    
    print("🚀 开始测试DeepSeek API速度...")
    
    # 测试内容
    test_content = """
    据媒体报道，美国爱国者导弹库存仅为五角大楼需求的25%。这一情况引发了美国军方对防空能力的担忧。
    专家表示，爱国者导弹系统是美军重要的防空武器，库存不足可能影响其应对潜在威胁的能力。
    五角大楼正在评估这一情况，并考虑增加采购计划。
    """
    
    print(f"📝 测试内容长度: {len(test_content)} 字符")
    
    # 创建标准配置的LLM
    print("\n" + "="*50)
    print("🔧 测试标准配置")
    print("="*50)
    
    llm_standard = ChatDeepSeek(
        api_key=api_key,
        model="deepseek-chat",
        temperature=0.3,
        max_tokens=4000
    )
    
    # 标准prompt
    standard_prompt = """你是一个专业的新闻编辑，请为以下新闻内容生成一个详细、准确的中文摘要。

要求：
1. 摘要长度控制在200-300字之间
2. 突出新闻的核心信息、关键事实和重要细节
3. 使用客观、准确的语言
4. 保持新闻的时效性和重要性
5. 包含新闻的背景信息、主要人物、时间地点等关键要素
6. 避免主观评价和推测
7. 确保摘要内容完整，能够帮助读者快速了解新闻全貌

请直接返回摘要内容，不要添加任何额外的说明或格式。"""
    
    messages_standard = [
        SystemMessage(content=standard_prompt),
        HumanMessage(content=f"新闻内容：\n\n{test_content}")
    ]
    
    start_time = time.time()
    try:
        response_standard = await llm_standard.ainvoke(messages_standard)
        time_standard = time.time() - start_time
        summary_standard = response_standard.content.strip()
        print(f"✅ 标准配置成功: {time_standard:.1f}秒")
        print(f"📝 摘要长度: {len(summary_standard)} 字符")
        print(f"📝 摘要内容: {summary_standard[:100]}...")
    except Exception as e:
        print(f"❌ 标准配置失败: {e}")
        time_standard = 0
    
    # 创建优化配置的LLM
    print("\n" + "="*50)
    print("⚡ 测试优化配置")
    print("="*50)
    
    llm_fast = ChatDeepSeek(
        api_key=api_key,
        model="deepseek-chat",
        temperature=0.1,
        max_tokens=800
    )
    
    # 简化prompt
    fast_prompt = "为以下新闻生成100字以内的中文摘要，突出核心信息："
    
    messages_fast = [
        SystemMessage(content=fast_prompt),
        HumanMessage(content=test_content)
    ]
    
    start_time = time.time()
    try:
        response_fast = await llm_fast.ainvoke(messages_fast)
        time_fast = time.time() - start_time
        summary_fast = response_fast.content.strip()
        print(f"✅ 优化配置成功: {time_fast:.1f}秒")
        print(f"📝 摘要长度: {len(summary_fast)} 字符")
        print(f"📝 摘要内容: {summary_fast[:100]}...")
    except Exception as e:
        print(f"❌ 优化配置失败: {e}")
        time_fast = 0
    
    # 比较结果
    print("\n" + "="*50)
    print("📊 速度对比结果")
    print("="*50)
    
    if time_standard > 0 and time_fast > 0:
        speedup = time_standard / time_fast
        print(f"⏱️  标准配置: {time_standard:.1f}秒")
        print(f"⚡ 优化配置: {time_fast:.1f}秒")
        print(f"🚀 速度提升: {speedup:.1f}倍")
        
        if speedup > 1.5:
            print("🎉 优化配置显著提升了处理速度！")
        elif speedup > 1.1:
            print("👍 优化配置有一定速度提升")
        else:
            print("⚠️  速度提升不明显")
    else:
        print("❌ 无法进行速度对比，因为处理失败")
    
    # 测试翻译速度
    print("\n" + "="*50)
    print("🌐 测试翻译速度")
    print("="*50)
    
    english_content = """
    According to media reports, the US Patriot missile inventory is only 25% of the Pentagon's requirements. 
    This situation has raised concerns about the US military's air defense capabilities.
    Experts say the Patriot missile system is an important air defense weapon for the US military, 
    and insufficient inventory may affect its ability to respond to potential threats.
    The Pentagon is assessing this situation and considering increasing procurement plans.
    """
    
    print(f"📝 英文内容长度: {len(english_content)} 字符")
    
    # 标准翻译prompt
    standard_translate_prompt = """你是一个专业的翻译专家，请将以下英文新闻内容翻译成中文。

要求：
1. 保持原文的意思和语气
2. 使用准确、流畅的中文表达
3. 保持新闻的专业性和可读性
4. 适当调整语序以符合中文表达习惯
5. 保留重要的专有名词和数字

请直接返回翻译结果，不要添加任何额外的说明或格式。"""
    
    messages_translate_standard = [
        SystemMessage(content=standard_translate_prompt),
        HumanMessage(content=f"英文内容：\n\n{english_content}")
    ]
    
    start_time = time.time()
    try:
        response_translate = await llm_standard.ainvoke(messages_translate_standard)
        time_translate = time.time() - start_time
        translation = response_translate.content.strip()
        print(f"✅ 翻译成功: {time_translate:.1f}秒")
        print(f"📝 翻译长度: {len(translation)} 字符")
        print(f"📝 翻译内容: {translation[:100]}...")
    except Exception as e:
        print(f"❌ 翻译失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_deepseek_speed()) 