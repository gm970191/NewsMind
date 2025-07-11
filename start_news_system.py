#!/usr/bin/env python3
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
        
        print("\n✅ 所有服务启动完成！")
        print("📍 前端地址: http://localhost:3000")
        print("📍 后端地址: http://localhost:8000")
        print("📅 新闻采集: 每6小时自动执行")
        print("⏹️  按 Ctrl+C 停止所有服务")
        
        # 等待用户中断
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️  正在停止所有服务...")
            
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
