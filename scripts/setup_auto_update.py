#!/usr/bin/env python3
"""
自动更新设置脚本
用于设置定时新闻采集任务
"""
import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime


def create_batch_file():
    """创建Windows批处理文件"""
    batch_content = '''@echo off
cd /d "%~dp0"
echo 开始新闻采集 - %date% %time%
python scripts/simple_news_crawler.py
echo 采集完成 - %date% %time%
pause
'''
    
    batch_file = Path("scripts/run_news_crawl.bat")
    batch_file.write_text(batch_content, encoding='utf-8')
    print(f"✅ 创建批处理文件: {batch_file}")


def create_scheduled_task():
    """创建Windows计划任务"""
    try:
        # 获取当前目录的绝对路径
        current_dir = Path.cwd().absolute()
        batch_file = current_dir / "scripts" / "run_news_crawl.bat"
        
        # 创建计划任务命令
        task_name = "NewsMind_NewsCrawl"
        schedule = "every 6 hours"  # 每6小时执行一次
        
        cmd = f'''schtasks /create /tn "{task_name}" /tr "{batch_file}" /sc hourly /mo 6 /f'''
        
        print(f"🔄 创建计划任务: {task_name}")
        print(f"   执行文件: {batch_file}")
        print(f"   执行频率: 每6小时")
        
        # 执行命令
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 计划任务创建成功！")
            print("📋 任务信息:")
            print(f"   任务名称: {task_name}")
            print(f"   执行频率: 每6小时")
            print(f"   执行文件: {batch_file}")
        else:
            print("❌ 计划任务创建失败")
            print(f"错误信息: {result.stderr}")
            
    except Exception as e:
        print(f"❌ 创建计划任务时出错: {e}")


def create_python_scheduler():
    """创建Python调度器脚本"""
    scheduler_content = '''#!/usr/bin/env python3
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
        print("\\n⏹️  调度器已停止")

if __name__ == "__main__":
    main()
'''
    
    scheduler_file = Path("scripts/auto_scheduler.py")
    scheduler_file.write_text(scheduler_content, encoding='utf-8')
    print(f"✅ 创建调度器脚本: {scheduler_file}")


def create_startup_script():
    """创建启动脚本"""
    startup_content = '''#!/usr/bin/env python3
"""
NewsMind 启动脚本
自动启动前端、后端和新闻采集
"""
import subprocess
import sys
import time
from pathlib import Path

def start_backend():
    """启动后端服务"""
    print("🚀 启动后端服务...")
    try:
        # 启动后端服务
        backend_process = subprocess.Popen([
            sys.executable, 
            "backend/start_server.py", 
            "--mode", "simple"
        ], cwd=Path.cwd())
        
        print("✅ 后端服务启动成功")
        return backend_process
    except Exception as e:
        print(f"❌ 后端服务启动失败: {e}")
        return None

def start_frontend():
    """启动前端服务"""
    print("🚀 启动前端服务...")
    try:
        # 启动前端服务
        frontend_process = subprocess.Popen([
            "npm", "run", "dev"
        ], cwd=Path.cwd() / "frontend")
        
        print("✅ 前端服务启动成功")
        return frontend_process
    except Exception as e:
        print(f"❌ 前端服务启动失败: {e}")
        return None

def start_scheduler():
    """启动新闻采集调度器"""
    print("🚀 启动新闻采集调度器...")
    try:
        # 启动调度器
        scheduler_process = subprocess.Popen([
            sys.executable, 
            "scripts/auto_scheduler.py"
        ], cwd=Path.cwd())
        
        print("✅ 新闻采集调度器启动成功")
        return scheduler_process
    except Exception as e:
        print(f"❌ 新闻采集调度器启动失败: {e}")
        return None

def main():
    """主函数"""
    print("📰 NewsMind 自动启动脚本")
    print("=" * 50)
    
    processes = []
    
    try:
        # 启动后端
        backend_process = start_backend()
        if backend_process:
            processes.append(backend_process)
        
        # 等待后端启动
        time.sleep(3)
        
        # 启动前端
        frontend_process = start_frontend()
        if frontend_process:
            processes.append(frontend_process)
        
        # 等待前端启动
        time.sleep(5)
        
        # 启动调度器
        scheduler_process = start_scheduler()
        if scheduler_process:
            processes.append(scheduler_process)
        
        print("\\n✅ 所有服务启动完成！")
        print("📍 前端地址: http://localhost:3000")
        print("📍 后端地址: http://localhost:8000")
        print("📅 新闻采集: 每6小时自动执行")
        print("⏹️  按 Ctrl+C 停止所有服务")
        
        # 等待用户中断
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\\n⏹️  正在停止所有服务...")
            
    except Exception as e:
        print(f"❌ 启动过程中出错: {e}")
    
    finally:
        # 停止所有进程
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
        
        print("✅ 所有服务已停止")

if __name__ == "__main__":
    main()
'''
    
    startup_file = Path("start_news_system.py")
    startup_file.write_text(startup_content, encoding='utf-8')
    print(f"✅ 创建启动脚本: {startup_file}")


def create_readme():
    """创建使用说明"""
    readme_content = '''# NewsMind 自动更新设置

## 自动更新方案

### 方案1: 使用启动脚本（推荐）
```bash
python start_news_system.py
```
这个脚本会自动启动：
- 后端服务 (http://localhost:8000)
- 前端服务 (http://localhost:3000)
- 新闻采集调度器（每6小时执行一次）

### 方案2: 手动运行新闻采集
```bash
python scripts/simple_news_crawler.py
```

### 方案3: 使用Windows计划任务
1. 运行 `python scripts/setup_auto_update.py` 创建计划任务
2. 系统会自动每6小时执行一次新闻采集

## 服务地址
- 前端: http://localhost:3000
- 后端: http://localhost:8000
- 健康检查: http://localhost:8000/health

## 新闻采集频率
- 默认: 每6小时执行一次
- 可手动执行: `python scripts/simple_news_crawler.py`

## 故障排除
1. 如果新闻采集失败，系统会自动创建测试数据
2. 检查日志文件了解详细错误信息
3. 确保网络连接正常

## 停止服务
- 按 Ctrl+C 停止所有服务
- 或分别停止各个进程
'''
    
    readme_file = Path("AUTO_UPDATE_README.md")
    readme_file.write_text(readme_content, encoding='utf-8')
    print(f"✅ 创建使用说明: {readme_file}")


def main():
    """主函数"""
    print("🔧 NewsMind 自动更新设置工具")
    print("=" * 50)
    
    # 创建批处理文件
    create_batch_file()
    
    # 创建Python调度器
    create_python_scheduler()
    
    # 创建启动脚本
    create_startup_script()
    
    # 创建使用说明
    create_readme()
    
    # 尝试创建Windows计划任务
    print("\n🔄 尝试创建Windows计划任务...")
    create_scheduled_task()
    
    print("\n✅ 自动更新设置完成！")
    print("\n📋 可用的启动方式:")
    print("1. 完整启动: python start_news_system.py")
    print("2. 手动采集: python scripts/simple_news_crawler.py")
    print("3. 调度器: python scripts/auto_scheduler.py")
    print("\n📖 详细说明请查看: AUTO_UPDATE_README.md")


if __name__ == "__main__":
    main() 