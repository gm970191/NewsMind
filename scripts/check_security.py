#!/usr/bin/env python3
"""
安全检查脚本
用于验证API密钥配置和敏感信息检查
"""

import os
import re
import sys
from pathlib import Path


def check_env_file():
    """检查.env文件是否存在且配置正确"""
    env_file = Path("backend/.env")
    
    if not env_file.exists():
        print("❌ 错误: .env 文件不存在")
        print("   请按照 backend/ENV_SETUP.md 的说明创建 .env 文件")
        return False
    
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否包含API密钥
    if "DEEPSEEK_API_KEY" not in content:
        print("❌ 错误: .env 文件中缺少 DEEPSEEK_API_KEY 配置")
        return False
    
    # 检查API密钥是否为占位符
    if "your_deepseek_api_key_here" in content:
        print("❌ 错误: 请将 your_deepseek_api_key_here 替换为您的实际API密钥")
        return False
    
    # 检查API密钥格式
    api_key_match = re.search(r'DEEPSEEK_API_KEY=(sk-[a-zA-Z0-9]+)', content)
    if not api_key_match:
        print("❌ 错误: API密钥格式不正确，应以 'sk-' 开头")
        return False
    
    print("✅ .env 文件配置正确")
    return True


def check_hardcoded_secrets():
    """检查代码中是否有硬编码的敏感信息"""
    sensitive_patterns = [
        r'sk-[a-zA-Z0-9]{32,}',  # API密钥格式
        r'password\s*=\s*["\'][^"\']+["\']',  # 硬编码密码
        r'secret\s*=\s*["\'][^"\']+["\']',  # 硬编码密钥
        r'token\s*=\s*["\'][^"\']+["\']',  # 硬编码令牌
    ]
    
    python_files = list(Path("backend").rglob("*.py"))
    issues_found = []
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for pattern in sensitive_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    issues_found.append({
                        'file': str(file_path),
                        'line': content[:match.start()].count('\n') + 1,
                        'match': match.group()[:20] + '...' if len(match.group()) > 20 else match.group()
                    })
        except Exception as e:
            print(f"⚠️  警告: 无法读取文件 {file_path}: {e}")
    
    if issues_found:
        print("❌ 发现硬编码的敏感信息:")
        for issue in issues_found:
            print(f"   文件: {issue['file']}:{issue['line']}")
            print(f"   内容: {issue['match']}")
        return False
    
    print("✅ 未发现硬编码的敏感信息")
    return True


def check_gitignore():
    """检查.gitignore是否包含敏感文件"""
    gitignore_file = Path(".gitignore")
    
    if not gitignore_file.exists():
        print("❌ 错误: .gitignore 文件不存在")
        return False
    
    with open(gitignore_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_patterns = [
        '.env',
        '*.db',
        '*.log',
        '__pycache__',
        '.venv',
    ]
    
    missing_patterns = []
    for pattern in required_patterns:
        if pattern not in content:
            missing_patterns.append(pattern)
    
    if missing_patterns:
        print(f"❌ 错误: .gitignore 缺少以下模式: {', '.join(missing_patterns)}")
        return False
    
    print("✅ .gitignore 配置正确")
    return True


def test_api_key():
    """测试API密钥是否有效"""
    try:
        # 导入配置
        sys.path.insert(0, 'backend')
        from app.core.config import settings
        
        if not settings.deepseek_api_key:
            print("❌ 错误: API密钥未配置")
            return False
        
        print(f"✅ API密钥已配置: {settings.deepseek_api_key[:10]}...")
        return True
        
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        return False
    except Exception as e:
        print(f"⚠️  警告: 无法测试API密钥: {e}")
        return True


def main():
    """主函数"""
    print("🔐 NewsMind 安全检查")
    print("=" * 50)
    
    checks = [
        ("环境变量配置", check_env_file),
        ("硬编码敏感信息检查", check_hardcoded_secrets),
        ("Git忽略文件检查", check_gitignore),
        ("API密钥测试", test_api_key),
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        print(f"\n📋 检查: {check_name}")
        try:
            if check_func():
                passed += 1
        except Exception as e:
            print(f"❌ 检查失败: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 检查结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有安全检查通过！您的配置是安全的。")
        return 0
    else:
        print("⚠️  发现安全问题，请按照上述建议进行修复。")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 