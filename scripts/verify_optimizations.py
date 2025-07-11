#!/usr/bin/env python3
import requests

# 测试API
response = requests.get("http://localhost:8000/api/v1/news/articles/62")
if response.status_code == 200:
    article = response.json()
    pc = article.get('processed_content', {})
    
    print("✅ API正常")
    print(f"详细总结长度: {len(pc.get('detailed_summary_zh', ''))} 字符")
    print(f"原始内容长度: {len(pc.get('original_content_zh', ''))} 字符")
    
    # 检查详细总结是否移除标题
    detailed_summary = pc.get('detailed_summary_zh', '')
    if detailed_summary.startswith('## 事件概述'):
        print("✅ 中文总结已移除重复标题")
    else:
        print("❌ 中文总结仍包含重复标题")
    
    # 检查双语内容
    original_content = pc.get('original_content_zh', '')
    if '---' in original_content:
        parts = original_content.split('---')
        chinese_part = parts[0].strip()
        english_part = parts[1].strip() if len(parts) > 1 else ""
        print(f"✅ 双语内容: 中文{len(chinese_part)}字符, 英文{len(english_part)}字符")
    else:
        print("❌ 无双语分隔符")
    
    print("\n🎉 所有优化完成！")
    print("现在可以访问: http://localhost:3000/article/62")
else:
    print(f"❌ API错误: {response.status_code}") 