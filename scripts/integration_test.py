#!/usr/bin/env python3
"""
NewsMind 系统集成测试脚本
"""
import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Any
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegrationTester:
    """系统集成测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.test_results = []
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def test_health_check(self) -> bool:
        """测试健康检查"""
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✓ 健康检查通过: {data}")
                    return True
                else:
                    logger.error(f"✗ 健康检查失败: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"✗ 健康检查异常: {e}")
            return False
    
    async def test_news_articles(self) -> bool:
        """测试新闻文章API"""
        try:
            async with self.session.get(f"{self.base_url}/api/v1/news/articles") as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', [])
                    logger.info(f"✓ 新闻文章API通过: 获取到 {len(articles)} 条文章")
                    return True
                else:
                    logger.error(f"✗ 新闻文章API失败: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"✗ 新闻文章API异常: {e}")
            return False
    
    async def test_article_detail(self, article_id: int = 1) -> bool:
        """测试文章详情API"""
        try:
            async with self.session.get(f"{self.base_url}/api/v1/news/articles/{article_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✓ 文章详情API通过: {data.get('title', 'Unknown')}")
                    return True
                else:
                    logger.error(f"✗ 文章详情API失败: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"✗ 文章详情API异常: {e}")
            return False
    
    async def test_ai_processing(self, article_id: int = 1) -> bool:
        """测试AI处理API"""
        try:
            async with self.session.post(f"{self.base_url}/api/v1/ai/process/{article_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✓ AI处理API通过: {data.get('message', 'Unknown')}")
                    return True
                else:
                    logger.error(f"✗ AI处理API失败: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"✗ AI处理API异常: {e}")
            return False
    
    async def test_statistics(self) -> bool:
        """测试统计信息API"""
        try:
            async with self.session.get(f"{self.base_url}/api/v1/news/statistics") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✓ 统计信息API通过: 总文章数 {data.get('total_articles', 0)}")
                    return True
                else:
                    logger.error(f"✗ 统计信息API失败: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"✗ 统计信息API异常: {e}")
            return False
    
    async def test_search(self) -> bool:
        """测试搜索API"""
        try:
            params = {"keyword": "测试"}
            async with self.session.get(f"{self.base_url}/api/v1/news/search", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✓ 搜索API通过: 找到 {data.get('total', 0)} 条结果")
                    return True
                else:
                    logger.error(f"✗ 搜索API失败: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"✗ 搜索API异常: {e}")
            return False
    
    async def test_frontend_connectivity(self) -> bool:
        """测试前端连接性"""
        try:
            async with self.session.get("http://localhost:3000") as response:
                if response.status == 200:
                    content = await response.text()
                    if "NewsMind" in content:
                        logger.info("✓ 前端连接性测试通过")
                        return True
                    else:
                        logger.error("✗ 前端页面内容异常")
                        return False
                else:
                    logger.error(f"✗ 前端连接失败: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"✗ 前端连接异常: {e}")
            return False
    
    async def run_performance_test(self, endpoint: str, iterations: int = 10) -> Dict[str, Any]:
        """性能测试"""
        logger.info(f"开始性能测试: {endpoint}")
        times = []
        
        for i in range(iterations):
            start_time = time.time()
            try:
                async with self.session.get(f"{self.base_url}{endpoint}") as response:
                    if response.status == 200:
                        await response.json()
                        times.append(time.time() - start_time)
                    else:
                        logger.error(f"性能测试请求失败: {response.status}")
            except Exception as e:
                logger.error(f"性能测试异常: {e}")
        
        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            result = {
                "endpoint": endpoint,
                "iterations": len(times),
                "avg_time": round(avg_time * 1000, 2),  # 毫秒
                "min_time": round(min_time * 1000, 2),
                "max_time": round(max_time * 1000, 2),
                "success_rate": len(times) / iterations * 100
            }
            
            logger.info(f"性能测试结果: 平均 {result['avg_time']}ms, 成功率 {result['success_rate']}%")
            return result
        else:
            return {"error": "No successful requests"}
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        logger.info("开始系统集成测试...")
        
        tests = [
            ("健康检查", self.test_health_check),
            ("新闻文章API", self.test_news_articles),
            ("文章详情API", self.test_article_detail),
            ("AI处理API", self.test_ai_processing),
            ("统计信息API", self.test_statistics),
            ("搜索API", self.test_search),
            ("前端连接性", self.test_frontend_connectivity),
        ]
        
        results = {}
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            logger.info(f"\n--- 测试: {test_name} ---")
            try:
                result = await test_func()
                results[test_name] = result
                if result:
                    passed += 1
            except Exception as e:
                logger.error(f"测试 {test_name} 异常: {e}")
                results[test_name] = False
        
        # 性能测试
        logger.info("\n--- 性能测试 ---")
        performance_results = {}
        performance_endpoints = [
            "/health",
            "/api/v1/news/articles",
            "/api/v1/news/statistics"
        ]
        
        for endpoint in performance_endpoints:
            performance_results[endpoint] = await self.run_performance_test(endpoint)
        
        # 汇总结果
        summary = {
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": total - passed,
            "success_rate": round(passed / total * 100, 2),
            "test_results": results,
            "performance_results": performance_results,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        logger.info(f"\n=== 测试总结 ===")
        logger.info(f"总测试数: {total}")
        logger.info(f"通过测试: {passed}")
        logger.info(f"失败测试: {total - passed}")
        logger.info(f"成功率: {summary['success_rate']}%")
        
        return summary

async def main():
    """主函数"""
    async with IntegrationTester() as tester:
        results = await tester.run_all_tests()
        
        # 保存测试结果
        with open("integration_test_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info("测试结果已保存到 integration_test_results.json")
        
        # 返回测试结果
        return results

if __name__ == "__main__":
    asyncio.run(main()) 