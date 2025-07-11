#!/usr/bin/env python3
"""
批量AI处理速度测试
"""
import requests
import json
import time
import os
import asyncio

def test_batch_processing():
    """测试批量处理速度"""
    
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ 未设置DEEPSEEK_API_KEY环境变量")
        return
    
    print("🚀 开始批量AI处理速度测试...")
    
    # API配置
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 测试文章列表
    test_articles = [
        {
            "title": "美国爱国者导弹库存不足",
            "content": "据媒体报道，美国爱国者导弹库存仅为五角大楼需求的25%。这一情况引发了美国军方对防空能力的担忧。"
        },
        {
            "title": "全球经济复苏趋势",
            "content": "最新经济数据显示，全球经济正在逐步复苏。多个主要经济体的GDP增长超出预期，就业市场也在改善。"
        },
        {
            "title": "科技创新推动发展",
            "content": "人工智能、新能源等前沿技术的快速发展正在推动各行业转型升级，为经济发展注入新动力。"
        },
        {
            "title": "环境保护新政策",
            "content": "各国政府正在制定更严格的环境保护政策，以应对气候变化挑战，推动绿色可持续发展。"
        },
        {
            "title": "教育数字化转型",
            "content": "数字化技术正在深刻改变教育行业，在线教育平台快速发展，为学习者提供更多选择。"
        }
    ]
    
    print(f"📝 测试文章数量: {len(test_articles)}")
    
    # 优化配置
    fast_config = {
        "model": "deepseek-chat",
        "temperature": 0.1,
        "max_tokens": 800
    }
    
    total_time = 0
    success_count = 0
    results = []
    
    for i, article in enumerate(test_articles, 1):
        print(f"\n📰 处理文章 {i}: {article['title']}")
        
        # 快速摘要prompt
        fast_prompt = "为以下新闻生成100字以内的中文摘要，突出核心信息："
        
        data = {
            **fast_config,
            "messages": [
                {
                    "role": "system",
                    "content": fast_prompt
                },
                {
                    "role": "user",
                    "content": article['content']
                }
            ]
        }
        
        start_time = time.time()
        try:
            response = requests.post(url, headers=headers, json=data)
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                summary = result['choices'][0]['message']['content'].strip()
                
                total_time += processing_time
                success_count += 1
                
                results.append({
                    "article_id": i,
                    "title": article['title'],
                    "processing_time": processing_time,
                    "summary_length": len(summary),
                    "summary": summary[:50] + "..." if len(summary) > 50 else summary
                })
                
                print(f"✅ 成功: {processing_time:.1f}秒, 摘要长度: {len(summary)}字符")
            else:
                print(f"❌ 失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ 错误: {e}")
        
        # 短暂延迟，避免API限速
        time.sleep(0.5)
    
    # 统计结果
    print("\n" + "="*60)
    print("📊 批量处理结果统计")
    print("="*60)
    
    if success_count > 0:
        avg_time = total_time / success_count
        total_articles = len(test_articles)
        
        print(f"📈 处理统计:")
        print(f"   总文章数: {total_articles}")
        print(f"   成功处理: {success_count}")
        print(f"   失败数量: {total_articles - success_count}")
        print(f"   成功率: {success_count/total_articles*100:.1f}%")
        print(f"   总耗时: {total_time:.1f}秒")
        print(f"   平均耗时: {avg_time:.1f}秒/篇")
        print(f"   处理速度: {60/avg_time:.1f}篇/分钟")
        
        print(f"\n📝 详细结果:")
        for result in results:
            print(f"   文章{result['article_id']}: {result['processing_time']:.1f}s, {result['summary_length']}字符")
            print(f"     摘要: {result['summary']}")
        
        # 性能评估
        print(f"\n🎯 性能评估:")
        if avg_time < 10:
            print("   🚀 优秀: 平均处理时间小于10秒")
        elif avg_time < 20:
            print("   👍 良好: 平均处理时间小于20秒")
        else:
            print("   ⚠️  一般: 平均处理时间超过20秒")
            
        if success_count == total_articles:
            print("   ✅ 完美: 所有文章处理成功")
        elif success_count/total_articles > 0.8:
            print("   👍 良好: 成功率超过80%")
        else:
            print("   ⚠️  一般: 成功率较低")
    else:
        print("❌ 没有成功处理的文章")

if __name__ == "__main__":
    test_batch_processing() 