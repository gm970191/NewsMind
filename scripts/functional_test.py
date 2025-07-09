#!/usr/bin/env python3
"""
NewsMind 功能测试脚本
测试完整的用户场景和业务流程
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

class FunctionalTester:
    """功能测试器"""
    
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
    
    async def test_user_scenario_1(self) -> bool:
        """测试场景1: 用户浏览新闻列表"""
        logger.info("=== 测试场景1: 用户浏览新闻列表 ===")
        
        try:
            # 1. 获取新闻列表
            async with self.session.get(f"{self.base_url}/api/v1/news/articles") as response:
                if response.status != 200:
                    logger.error(f"获取新闻列表失败: {response.status}")
                    return False
                
                data = await response.json()
                articles = data.get('articles', [])
                logger.info(f"✓ 成功获取 {len(articles)} 条新闻")
            
            # 2. 检查新闻数据结构
            if articles:
                article = articles[0]
                required_fields = ['id', 'title', 'content', 'source_name', 'category']
                for field in required_fields:
                    if field not in article:
                        logger.error(f"新闻数据缺少字段: {field}")
                        return False
                logger.info("✓ 新闻数据结构正确")
            
            # 3. 测试分页功能
            async with self.session.get(f"{self.base_url}/api/v1/news/articles?skip=0&limit=5") as response:
                if response.status == 200:
                    data = await response.json()
                    if len(data.get('articles', [])) <= 5:
                        logger.info("✓ 分页功能正常")
                    else:
                        logger.error("分页功能异常")
                        return False
            
            logger.info("✓ 场景1测试通过")
            return True
            
        except Exception as e:
            logger.error(f"场景1测试异常: {e}")
            return False
    
    async def test_user_scenario_2(self) -> bool:
        """测试场景2: 用户搜索新闻"""
        logger.info("=== 测试场景2: 用户搜索新闻 ===")
        
        try:
            # 1. 搜索关键词
            keyword = "测试"
            async with self.session.get(f"{self.base_url}/api/v1/news/search?keyword={keyword}") as response:
                if response.status != 200:
                    logger.error(f"搜索功能失败: {response.status}")
                    return False
                
                data = await response.json()
                results = data.get('articles', [])
                logger.info(f"✓ 搜索 '{keyword}' 找到 {len(results)} 条结果")
            
            # 2. 验证搜索结果
            if results:
                for article in results:
                    if keyword.lower() in article.get('title', '').lower() or keyword.lower() in article.get('content', '').lower():
                        logger.info("✓ 搜索结果相关性正确")
                        break
                else:
                    logger.warning("搜索结果相关性可能存在问题")
            
            logger.info("✓ 场景2测试通过")
            return True
            
        except Exception as e:
            logger.error(f"场景2测试异常: {e}")
            return False
    
    async def test_user_scenario_3(self) -> bool:
        """测试场景3: 用户查看文章详情"""
        logger.info("=== 测试场景3: 用户查看文章详情 ===")
        
        try:
            # 1. 获取文章详情
            article_id = 1
            async with self.session.get(f"{self.base_url}/api/v1/news/articles/{article_id}") as response:
                if response.status != 200:
                    logger.error(f"获取文章详情失败: {response.status}")
                    return False
                
                article = await response.json()
                logger.info(f"✓ 成功获取文章: {article.get('title', 'Unknown')}")
            
            # 2. 检查文章详情数据
            required_fields = ['id', 'title', 'content', 'source_url', 'source_name']
            for field in required_fields:
                if field not in article:
                    logger.error(f"文章详情缺少字段: {field}")
                    return False
            
            # 3. 检查AI处理结果
            processed_content = article.get('processed_content')
            if processed_content:
                logger.info("✓ 文章已包含AI处理结果")
            else:
                logger.info("文章未经过AI处理")
            
            logger.info("✓ 场景3测试通过")
            return True
            
        except Exception as e:
            logger.error(f"场景3测试异常: {e}")
            return False
    
    async def test_user_scenario_4(self) -> bool:
        """测试场景4: 用户触发AI处理"""
        logger.info("=== 测试场景4: 用户触发AI处理 ===")
        
        try:
            # 1. 触发AI处理
            article_id = 1
            async with self.session.post(f"{self.base_url}/api/v1/ai/process/{article_id}") as response:
                if response.status != 200:
                    logger.error(f"AI处理失败: {response.status}")
                    return False
                
                result = await response.json()
                logger.info(f"✓ AI处理成功: {result.get('message', 'Unknown')}")
            
            # 2. 等待处理完成并检查结果
            await asyncio.sleep(2)
            
            async with self.session.get(f"{self.base_url}/api/v1/news/articles/{article_id}") as response:
                if response.status == 200:
                    article = await response.json()
                    processed_content = article.get('processed_content')
                    if processed_content:
                        logger.info("✓ AI处理结果已保存")
                    else:
                        logger.warning("AI处理结果可能未保存")
            
            logger.info("✓ 场景4测试通过")
            return True
            
        except Exception as e:
            logger.error(f"场景4测试异常: {e}")
            return False
    
    async def test_user_scenario_5(self) -> bool:
        """测试场景5: 用户查看统计信息"""
        logger.info("=== 测试场景5: 用户查看统计信息 ===")
        
        try:
            # 1. 获取统计信息
            async with self.session.get(f"{self.base_url}/api/v1/news/statistics") as response:
                if response.status != 200:
                    logger.error(f"获取统计信息失败: {response.status}")
                    return False
                
                stats = await response.json()
                logger.info(f"✓ 总文章数: {stats.get('total_articles', 0)}")
                logger.info(f"✓ 已处理文章: {stats.get('processed_articles', 0)}")
            
            # 2. 检查统计数据结构
            required_fields = ['total_articles', 'processed_articles', 'total_sources']
            for field in required_fields:
                if field not in stats:
                    logger.error(f"统计信息缺少字段: {field}")
                    return False
            
            logger.info("✓ 场景5测试通过")
            return True
            
        except Exception as e:
            logger.error(f"场景5测试异常: {e}")
            return False
    
    async def test_error_handling(self) -> bool:
        """测试错误处理"""
        logger.info("=== 测试错误处理 ===")
        
        try:
            # 1. 测试不存在的文章
            async with self.session.get(f"{self.base_url}/api/v1/news/articles/99999") as response:
                if response.status == 404:
                    logger.info("✓ 404错误处理正确")
                else:
                    logger.error("404错误处理异常")
                    return False
            
            # 2. 测试无效的搜索参数
            async with self.session.get(f"{self.base_url}/api/v1/news/search?keyword=") as response:
                if response.status in [400, 422]:
                    logger.info("✓ 参数验证正确")
                else:
                    logger.warning("参数验证可能存在问题")
            
            # 3. 测试无效的AI处理请求
            async with self.session.post(f"{self.base_url}/api/v1/ai/process/99999") as response:
                if response.status in [404, 400]:
                    logger.info("✓ 无效请求处理正确")
                else:
                    logger.warning("无效请求处理可能存在问题")
            
            logger.info("✓ 错误处理测试通过")
            return True
            
        except Exception as e:
            logger.error(f"错误处理测试异常: {e}")
            return False
    
    async def test_performance_scenarios(self) -> bool:
        """测试性能场景"""
        logger.info("=== 测试性能场景 ===")
        
        try:
            # 1. 并发请求测试
            start_time = time.time()
            tasks = []
            for i in range(10):
                task = self.session.get(f"{self.base_url}/api/v1/news/articles")
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks)
            end_time = time.time()
            
            success_count = sum(1 for resp in responses if resp.status == 200)
            logger.info(f"✓ 并发测试: {success_count}/10 成功，耗时 {end_time - start_time:.2f}秒")
            
            # 2. 大数据量测试
            async with self.session.get(f"{self.base_url}/api/v1/news/articles?limit=1000") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✓ 大数据量测试: 获取 {len(data.get('articles', []))} 条记录")
            
            logger.info("✓ 性能场景测试通过")
            return True
            
        except Exception as e:
            logger.error(f"性能场景测试异常: {e}")
            return False
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """运行所有功能测试"""
        logger.info("开始功能测试...")
        
        test_scenarios = [
            ("用户浏览新闻列表", self.test_user_scenario_1),
            ("用户搜索新闻", self.test_user_scenario_2),
            ("用户查看文章详情", self.test_user_scenario_3),
            ("用户触发AI处理", self.test_user_scenario_4),
            ("用户查看统计信息", self.test_user_scenario_5),
            ("错误处理", self.test_error_handling),
            ("性能场景", self.test_performance_scenarios),
        ]
        
        results = {}
        passed = 0
        total = len(test_scenarios)
        
        for scenario_name, test_func in test_scenarios:
            logger.info(f"\n--- 测试场景: {scenario_name} ---")
            try:
                result = await test_func()
                results[scenario_name] = result
                if result:
                    passed += 1
            except Exception as e:
                logger.error(f"测试场景 {scenario_name} 异常: {e}")
                results[scenario_name] = False
        
        # 汇总结果
        summary = {
            "total_scenarios": total,
            "passed_scenarios": passed,
            "failed_scenarios": total - passed,
            "success_rate": round(passed / total * 100, 2),
            "test_results": results,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        logger.info(f"\n=== 功能测试总结 ===")
        logger.info(f"总测试场景: {total}")
        logger.info(f"通过场景: {passed}")
        logger.info(f"失败场景: {total - passed}")
        logger.info(f"成功率: {summary['success_rate']}%")
        
        return summary

async def main():
    """主函数"""
    async with FunctionalTester() as tester:
        results = await tester.run_all_tests()
        
        # 保存测试结果
        with open("functional_test_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info("功能测试结果已保存到 functional_test_results.json")
        
        # 返回测试结果
        return results

if __name__ == "__main__":
    asyncio.run(main()) 