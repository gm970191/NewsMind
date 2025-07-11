#!/usr/bin/env python3
"""
NewsMind 后端服务启动脚本
支持开发环境和生产环境
"""
import os
import sys
import argparse
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def setup_environment():
    """设置环境变量"""
    # 禁用playwright（如果环境不支持）
    if os.environ.get('DISABLE_PLAYWRIGHT'):
        print("⚠️  Playwright已禁用，使用简化模式")
    
    # 设置日志级别
    os.environ.setdefault('LOG_LEVEL', 'INFO')

def start_development_server():
    """启动开发服务器"""
    try:
        from app.main import app
        import uvicorn
        
        print("🚀 启动NewsMind开发服务器")
        print("📍 访问地址: http://localhost:8000")
        print("📚 API文档: http://localhost:8000/docs")
        print("⏹️  按 Ctrl+C 停止服务")
        print("-" * 50)
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("💡 请确保已安装所需依赖:")
        print("   pip install fastapi uvicorn sqlalchemy")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

def start_production_server():
    """启动生产服务器"""
    try:
        from app.main import app
        import uvicorn
        
        print("🚀 启动NewsMind生产服务器")
        print("📍 访问地址: http://localhost:8000")
        print("📚 API文档: http://localhost:8000/docs")
        print("⏹️  按 Ctrl+C 停止服务")
        print("-" * 50)
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="warning"
        )
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("💡 请确保已安装所需依赖:")
        print("   pip install fastapi uvicorn sqlalchemy")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

def start_simple_server():
    """启动简化服务器（用于测试）"""
    try:
        from flask import Flask, jsonify
        
        app = Flask(__name__)
        DB_PATH = "backend/newsmind.db"
        
        @app.route('/health')
        def health():
            return jsonify({
                "status": "healthy",
                "version": "1.0.0",
                "database": "connected" if os.path.exists(DB_PATH) else "not_found",
                "message": "简化服务器运行中，请使用主FastAPI服务器获取完整功能"
            })
        
        print("🚀 启动NewsMind简化测试服务器")
        print("📍 访问地址: http://localhost:8000")
        print("📚 健康检查: http://localhost:8000/health")
        print("⚠️  简化服务器仅用于健康检查，完整API请使用主服务器")
        print("⏹️  按 Ctrl+C 停止服务")
        print("-" * 50)
        
        app.run(host='0.0.0.0', port=8000, debug=False)
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("💡 请安装Flask:")
        print("   pip install flask")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='NewsMind 后端服务启动脚本')
    parser.add_argument('--mode', choices=['dev', 'prod', 'simple'], 
                       default='dev', help='启动模式 (默认: dev)')
    parser.add_argument('--disable-playwright', action='store_true',
                       help='禁用playwright')
    
    args = parser.parse_args()
    
    # 设置环境
    if args.disable_playwright:
        os.environ['DISABLE_PLAYWRIGHT'] = '1'
    
    setup_environment()
    
    # 根据模式启动服务
    if args.mode == 'dev':
        start_development_server()
    elif args.mode == 'prod':
        start_production_server()
    elif args.mode == 'simple':
        start_simple_server()

if __name__ == '__main__':
    main() 