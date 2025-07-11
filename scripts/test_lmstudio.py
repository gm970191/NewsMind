#!/usr/bin/env python3
"""
独立测试本地LM Studio大模型
"""
import requests
import json
import time
from typing import Optional, Dict, Any
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LMStudioLLM:
    """本地LM Studio大模型调用类"""
    
    def __init__(self, api_url: str = "http://127.0.0.1:1234/v1/chat/completions"):
        self.api_url = api_url
        self.timeout = 30
    
    def test_connection(self) -> bool:
        """测试连接可用性"""
        try:
            logger.info(f"🔍 测试连接: {self.api_url}")
            # 直接测试API端点，不使用health端点
            response = requests.get(self.api_url.replace("/v1/chat/completions", ""), timeout=5)
            if response.status_code in [200, 404, 405]:  # 这些状态码表示服务在运行
                logger.info("✅ 连接测试成功")
                return True
            else:
                logger.warning(f"⚠️  连接测试失败，状态码: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ 连接测试异常: {e}")
            return False
    
    def test_available(self) -> bool:
        """测试API可用性"""
        try:
            logger.info("🧪 测试API可用性...")
            data = {
                "model": "lmstudio",
                "messages": [
                    {"role": "system", "content": "你是AI助手。"},
                    {"role": "user", "content": "你好"}
                ],
                "temperature": 0.1,
                "max_tokens": 10
            }
            
            response = requests.post(self.api_url, json=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                logger.info(f"✅ API测试成功，响应: {content}")
                return True
            else:
                logger.warning("⚠️  API响应格式异常")
                return False
                
        except Exception as e:
            logger.error(f"❌ API测试失败: {e}")
            return False
    
    def call(self, system_prompt: str, user_content: str, max_tokens: int = 1000) -> Optional[str]:
        """调用大模型"""
        try:
            data = {
                "model": "lmstudio",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                "temperature": 0.1,
                "max_tokens": max_tokens
            }
            
            logger.info(f"🤖 调用大模型: {user_content[:50]}...")
            start_time = time.time()
            
            response = requests.post(self.api_url, json=data, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content'].strip()
                elapsed = time.time() - start_time
                logger.info(f"✅ 调用成功 ({elapsed:.2f}s): {content[:100]}...")
                return content
            else:
                logger.error("❌ 响应格式异常")
                return None
                
        except Exception as e:
            logger.error(f"❌ 调用失败: {e}")
            return None
    
    def test_translation(self) -> bool:
        """测试翻译功能"""
        logger.info("🌐 测试翻译功能...")
        
        system_prompt = "将以下英文新闻标题翻译成中文，保持原意，使用流畅的中文表达。直接返回翻译结果，不要添加任何格式。"
        user_content = "Chinese researchers unveil Memory Operating System for AI models"
        
        result = self.call(system_prompt, user_content)
        if result:
            logger.info(f"✅ 翻译测试成功: {result}")
            return True
        else:
            logger.error("❌ 翻译测试失败")
            return False
    
    def test_summary(self) -> bool:
        """测试摘要功能"""
        logger.info("📝 测试摘要功能...")
        
        system_prompt = "为以下新闻生成简洁的中文摘要，控制在150字以内，突出核心信息。直接返回摘要内容。"
        user_content = """
        Chinese researchers have developed a new Memory Operating System (MemOS) for AI models. 
        This system enables AI models to maintain long-term memory and context awareness, 
        similar to human memory processes. The technology could revolutionize how AI systems 
        handle complex, multi-step tasks and maintain context over extended periods.
        """
        
        result = self.call(system_prompt, user_content)
        if result:
            logger.info(f"✅ 摘要测试成功: {result}")
            return True
        else:
            logger.error("❌ 摘要测试失败")
            return False
    
    def benchmark(self, num_calls: int = 3) -> Dict[str, Any]:
        """性能基准测试"""
        logger.info(f"⚡ 开始性能基准测试 ({num_calls} 次调用)...")
        
        system_prompt = "你是AI助手，请简单回复。"
        user_content = "你好，请简单介绍一下自己。"
        
        times = []
        success_count = 0
        
        for i in range(num_calls):
            start_time = time.time()
            result = self.call(system_prompt, user_content)
            elapsed = time.time() - start_time
            
            if result:
                times.append(elapsed)
                success_count += 1
                logger.info(f"  调用 {i+1}: {elapsed:.2f}s")
            else:
                logger.warning(f"  调用 {i+1}: 失败")
            
            # 间隔1秒
            if i < num_calls - 1:
                time.sleep(1)
        
        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            benchmark_result = {
                "total_calls": num_calls,
                "success_count": success_count,
                "success_rate": success_count / num_calls * 100,
                "avg_time": avg_time,
                "min_time": min_time,
                "max_time": max_time,
                "times": times
            }
            
            logger.info(f"📊 基准测试结果:")
            logger.info(f"  总调用: {num_calls}")
            logger.info(f"  成功: {success_count}")
            logger.info(f"  成功率: {benchmark_result['success_rate']:.1f}%")
            logger.info(f"  平均时间: {avg_time:.2f}s")
            logger.info(f"  最快: {min_time:.2f}s")
            logger.info(f"  最慢: {max_time:.2f}s")
            
            return benchmark_result
        else:
            logger.error("❌ 基准测试失败，无成功调用")
            return {"error": "No successful calls"}


def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 LM Studio 本地大模型测试")
    print("=" * 60)
    
    # 创建测试实例
    llm = LMStudioLLM()
    
    # 1. API可用性测试（包含连接测试）
    print("\n1️⃣ API可用性测试")
    if not llm.test_available():
        print("❌ API不可用，请检查LM Studio是否启动在 http://127.0.0.1:1234")
        print("💡 提示：请确保LM Studio已启动并配置了正确的模型")
        return
    
    # 2. 功能测试
    print("\n2️⃣ 功能测试")
    translation_ok = llm.test_translation()
    summary_ok = llm.test_summary()
    
    if not translation_ok or not summary_ok:
        print("❌ 功能测试失败")
        return
    
    # 3. 性能基准测试
    print("\n3️⃣ 性能基准测试")
    benchmark_result = llm.benchmark(3)
    
    # 4. 总结
    print("\n" + "=" * 60)
    print("📋 测试总结")
    print("=" * 60)
    print("✅ API可用性: 通过")
    print(f"✅ 翻译功能: {'通过' if translation_ok else '失败'}")
    print(f"✅ 摘要功能: {'通过' if summary_ok else '失败'}")
    print(f"✅ 性能测试: 成功率 {benchmark_result.get('success_rate', 0):.1f}%")
    print("\n🎉 LM Studio 本地大模型测试完成！")


if __name__ == "__main__":
    main() 