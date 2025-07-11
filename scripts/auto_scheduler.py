#!/usr/bin/env python3
"""
NewsMind 自动新闻采集调度器
"""
import time
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def run_news_crawl():
    """运行新闻采集"""
    try:
        print(f"🔄 开始新闻采集 - {datetime.now()}")
        
        # 运行新闻采集脚本
        result = subprocess.run([
            sys.executable, 
            "scripts/simple_news_crawler.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ 新闻采集成功 - {datetime.now()}")
            print(result.stdout)
        else:
            print(f"❌ 新闻采集失败 - {datetime.now()}")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ 运行新闻采集时出错: {e}")

def main():
    """主函数"""
    print("🚀 NewsMind 自动新闻采集调度器")
    print("=" * 50)
    print("📅 执行频率: 每6小时")
    print("⏹️  按 Ctrl+C 停止")
    print("-" * 50)
    
    try:
        while True:
            # 运行新闻采集
            run_news_crawl()
            
            # 等待6小时
            print(f"⏰ 等待6小时后再次执行...")
            time.sleep(6 * 60 * 60)  # 6小时
            
    except KeyboardInterrupt:
        print("\n⏹️  调度器已停止")

if __name__ == "__main__":
    main()
