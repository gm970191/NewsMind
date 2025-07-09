#!/usr/bin/env python3
"""
NewsMind 性能测试脚本
测试系统性能指标和负载能力
"""
import asyncio
import aiohttp
import time
import statistics
import json
from typing import Dict, List, Any
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceTester:
    """性能测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.results = {}
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
        self.session = aiohttp.ClientSession(connector=connector)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def measure_response_time(self, url: str, method: str = "GET", **kwargs) -> float:
        """测量单个请求的响应时间"""
        start_time = time.time()
        try:
            if method.upper() == "GET":
                async with self.session.get(url, **kwargs) as response:
                    await response.read()
            elif method.upper() == "POST":
                async with self.session.post(url, **kwargs) as response:
                    await response.read()
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            end_time = time.time()
            return end_time - start_time
        except Exception as e:
            logger.error(f"请求失败 {url}: {e}")
            return -1
    
    async def test_api_endpoints(self) -> Dict[str, Any]:
        """测试API端点性能"""
        logger.info("=== 测试API端点性能 ===")
        
        endpoints = [
            ("/health", "GET"),
            ("/api/v1/news/articles", "GET"),
            ("/api/v1/news/articles/1", "GET"),
            ("/api/v1/news/statistics", "GET"),
            ("/api/v1/news/search?keyword=测试", "GET"),
            ("/api/v1/system/cache/stats", "GET"),
        ]
        
        results = {}
        
        for endpoint, method in endpoints:
            logger.info(f"测试端点: {method} {endpoint}")
            
            # 进行多次测试取平均值
            response_times = []
            for i in range(10):
                response_time = await self.measure_response_time(
                    f"{self.base_url}{endpoint}", 
                    method
                )
                if response_time > 0:
                    response_times.append(response_time)
                await asyncio.sleep(0.1)  # 避免过于频繁的请求
            
            if response_times:
                results[endpoint] = {
                    "method": method,
                    "count": len(response_times),
                    "min": min(response_times),
                    "max": max(response_times),
                    "avg": statistics.mean(response_times),
                    "median": statistics.median(response_times),
                    "std": statistics.stdev(response_times) if len(response_times) > 1 else 0
                }
                logger.info(f"✓ {endpoint}: 平均 {results[endpoint]['avg']:.3f}s")
            else:
                results[endpoint] = {"error": "All requests failed"}
                logger.error(f"✗ {endpoint}: 所有请求失败")
        
        return results
    
    async def test_concurrent_load(self, concurrency: int = 50, duration: int = 30) -> Dict[str, Any]:
        """测试并发负载"""
        logger.info(f"=== 测试并发负载 ({concurrency} 并发, {duration}秒) ===")
        
        start_time = time.time()
        end_time = start_time + duration
        
        # 创建并发任务
        async def worker():
            response_times = []
            errors = 0
            
            while time.time() < end_time:
                try:
                    # 随机选择端点进行测试
                    endpoints = [
                        "/api/v1/news/articles",
                        "/api/v1/news/articles/1",
                        "/api/v1/news/statistics",
                        "/health"
                    ]
                    
                    import random
                    endpoint = random.choice(endpoints)
                    
                    response_time = await self.measure_response_time(
                        f"{self.base_url}{endpoint}"
                    )
                    
                    if response_time > 0:
                        response_times.append(response_time)
                    else:
                        errors += 1
                    
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    errors += 1
                    await asyncio.sleep(0.1)
            
            return response_times, errors
        
        # 启动并发任务
        tasks = [worker() for _ in range(concurrency)]
        results = await asyncio.gather(*tasks)
        
        # 汇总结果
        all_response_times = []
        total_errors = 0
        
        for response_times, errors in results:
            all_response_times.extend(response_times)
            total_errors += errors
        
        actual_duration = time.time() - start_time
        total_requests = len(all_response_times) + total_errors
        
        if all_response_times:
            summary = {
                "concurrency": concurrency,
                "duration": actual_duration,
                "total_requests": total_requests,
                "successful_requests": len(all_response_times),
                "failed_requests": total_errors,
                "requests_per_second": total_requests / actual_duration,
                "success_rate": len(all_response_times) / total_requests * 100,
                "response_times": {
                    "min": min(all_response_times),
                    "max": max(all_response_times),
                    "avg": statistics.mean(all_response_times),
                    "median": statistics.median(all_response_times),
                    "p95": sorted(all_response_times)[int(len(all_response_times) * 0.95)],
                    "p99": sorted(all_response_times)[int(len(all_response_times) * 0.99)]
                }
            }
            
            logger.info(f"✓ 总请求数: {total_requests}")
            logger.info(f"✓ 成功请求: {len(all_response_times)}")
            logger.info(f"✓ 失败请求: {total_errors}")
            logger.info(f"✓ 成功率: {summary['success_rate']:.2f}%")
            logger.info(f"✓ 每秒请求数: {summary['requests_per_second']:.2f}")
            logger.info(f"✓ 平均响应时间: {summary['response_times']['avg']:.3f}s")
            logger.info(f"✓ P95响应时间: {summary['response_times']['p95']:.3f}s")
            
            return summary
        else:
            logger.error("所有并发请求都失败了")
            return {"error": "All concurrent requests failed"}
    
    async def test_memory_usage(self) -> Dict[str, Any]:
        """测试内存使用情况"""
        logger.info("=== 测试内存使用情况 ===")
        
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            
            # 记录初始内存使用
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # 进行一些操作
            for i in range(100):
                await self.measure_response_time(f"{self.base_url}/api/v1/news/articles")
                if i % 10 == 0:
                    await asyncio.sleep(0.1)
            
            # 记录最终内存使用
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            results = {
                "initial_memory_mb": round(initial_memory, 2),
                "final_memory_mb": round(final_memory, 2),
                "memory_increase_mb": round(memory_increase, 2),
                "memory_increase_percent": round(memory_increase / initial_memory * 100, 2)
            }
            
            logger.info(f"✓ 初始内存: {results['initial_memory_mb']} MB")
            logger.info(f"✓ 最终内存: {results['final_memory_mb']} MB")
            logger.info(f"✓ 内存增长: {results['memory_increase_mb']} MB ({results['memory_increase_percent']}%)")
            
            return results
            
        except ImportError:
            logger.warning("psutil 未安装，跳过内存测试")
            return {"error": "psutil not available"}
        except Exception as e:
            logger.error(f"内存测试异常: {e}")
            return {"error": str(e)}
    
    async def test_database_performance(self) -> Dict[str, Any]:
        """测试数据库性能"""
        logger.info("=== 测试数据库性能 ===")
        
        try:
            # 测试不同查询的性能
            queries = [
                ("/api/v1/news/articles", "获取所有文章"),
                ("/api/v1/news/articles?limit=10", "获取10篇文章"),
                ("/api/v1/news/articles?skip=0&limit=5", "分页查询"),
                ("/api/v1/news/search?keyword=测试", "搜索查询"),
                ("/api/v1/news/statistics", "统计查询"),
            ]
            
            results = {}
            
            for endpoint, description in queries:
                logger.info(f"测试查询: {description}")
                
                response_times = []
                for i in range(5):
                    response_time = await self.measure_response_time(
                        f"{self.base_url}{endpoint}"
                    )
                    if response_time > 0:
                        response_times.append(response_time)
                    await asyncio.sleep(0.2)
                
                if response_times:
                    results[description] = {
                        "endpoint": endpoint,
                        "avg_time": statistics.mean(response_times),
                        "min_time": min(response_times),
                        "max_time": max(response_times)
                    }
                    logger.info(f"✓ {description}: 平均 {results[description]['avg_time']:.3f}s")
                else:
                    results[description] = {"error": "All queries failed"}
                    logger.error(f"✗ {description}: 查询失败")
            
            return results
            
        except Exception as e:
            logger.error(f"数据库性能测试异常: {e}")
            return {"error": str(e)}
    
    async def test_cache_performance(self) -> Dict[str, Any]:
        """测试缓存性能"""
        logger.info("=== 测试缓存性能 ===")
        
        try:
            # 测试缓存命中率
            endpoint = "/api/v1/news/articles"
            
            # 第一次请求（缓存未命中）
            first_response_time = await self.measure_response_time(
                f"{self.base_url}{endpoint}"
            )
            
            await asyncio.sleep(0.1)
            
            # 第二次请求（缓存命中）
            second_response_time = await self.measure_response_time(
                f"{self.base_url}{endpoint}"
            )
            
            if first_response_time > 0 and second_response_time > 0:
                cache_improvement = (first_response_time - second_response_time) / first_response_time * 100
                
                results = {
                    "first_request_time": first_response_time,
                    "second_request_time": second_response_time,
                    "cache_improvement_percent": cache_improvement,
                    "cache_effective": cache_improvement > 10  # 如果缓存提升超过10%认为有效
                }
                
                logger.info(f"✓ 首次请求: {first_response_time:.3f}s")
                logger.info(f"✓ 缓存请求: {second_response_time:.3f}s")
                logger.info(f"✓ 缓存提升: {cache_improvement:.2f}%")
                
                if results["cache_effective"]:
                    logger.info("✓ 缓存效果良好")
                else:
                    logger.warning("⚠ 缓存效果不明显")
                
                return results
            else:
                logger.error("缓存测试请求失败")
                return {"error": "Cache test requests failed"}
                
        except Exception as e:
            logger.error(f"缓存性能测试异常: {e}")
            return {"error": str(e)}
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """运行所有性能测试"""
        logger.info("开始性能测试...")
        
        start_time = time.time()
        
        # 运行各项测试
        api_results = await self.test_api_endpoints()
        concurrent_results = await self.test_concurrent_load(concurrency=30, duration=20)
        memory_results = await self.test_memory_usage()
        db_results = await self.test_database_performance()
        cache_results = await self.test_cache_performance()
        
        end_time = time.time()
        
        # 汇总结果
        summary = {
            "test_duration": end_time - start_time,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "api_endpoints": api_results,
            "concurrent_load": concurrent_results,
            "memory_usage": memory_results,
            "database_performance": db_results,
            "cache_performance": cache_results,
            "overall_assessment": self._assess_performance(api_results, concurrent_results, memory_results)
        }
        
        logger.info(f"\n=== 性能测试总结 ===")
        logger.info(f"测试耗时: {summary['test_duration']:.2f}秒")
        logger.info(f"整体评估: {summary['overall_assessment']}")
        
        return summary
    
    def _assess_performance(self, api_results: Dict, concurrent_results: Dict, memory_results: Dict) -> str:
        """评估整体性能"""
        try:
            # 检查API响应时间
            avg_response_times = []
            for endpoint, data in api_results.items():
                if isinstance(data, dict) and 'avg' in data:
                    avg_response_times.append(data['avg'])
            
            if avg_response_times:
                avg_api_time = statistics.mean(avg_response_times)
                if avg_api_time < 0.1:
                    api_score = "优秀"
                elif avg_api_time < 0.5:
                    api_score = "良好"
                elif avg_api_time < 1.0:
                    api_score = "一般"
                else:
                    api_score = "较差"
            else:
                api_score = "未知"
            
            # 检查并发性能
            if isinstance(concurrent_results, dict) and 'success_rate' in concurrent_results:
                success_rate = concurrent_results['success_rate']
                if success_rate > 95:
                    concurrent_score = "优秀"
                elif success_rate > 90:
                    concurrent_score = "良好"
                elif success_rate > 80:
                    concurrent_score = "一般"
                else:
                    concurrent_score = "较差"
            else:
                concurrent_score = "未知"
            
            # 检查内存使用
            if isinstance(memory_results, dict) and 'memory_increase_percent' in memory_results:
                memory_increase = memory_results['memory_increase_percent']
                if memory_increase < 10:
                    memory_score = "优秀"
                elif memory_increase < 30:
                    memory_score = "良好"
                elif memory_increase < 50:
                    memory_score = "一般"
                else:
                    memory_score = "较差"
            else:
                memory_score = "未知"
            
            # 综合评估
            scores = [api_score, concurrent_score, memory_score]
            if all(score == "优秀" for score in scores):
                return "优秀 - 系统性能表现卓越"
            elif scores.count("优秀") >= 2:
                return "良好 - 系统性能表现良好"
            elif scores.count("较差") >= 2:
                return "较差 - 需要性能优化"
            else:
                return "一般 - 性能表现中等"
                
        except Exception as e:
            return f"评估失败: {e}"

async def main():
    """主函数"""
    async with PerformanceTester() as tester:
        results = await tester.run_all_tests()
        
        # 保存测试结果
        with open("performance_test_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info("性能测试结果已保存到 performance_test_results.json")
        
        return results

if __name__ == "__main__":
    asyncio.run(main()) 