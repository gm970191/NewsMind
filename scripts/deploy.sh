#!/bin/bash

# NewsMind 部署脚本
set -e

echo "🚀 开始部署 NewsMind 系统..."

# 检查环境变量
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "❌ 错误: 未设置 DEEPSEEK_API_KEY 环境变量"
    exit 1
fi

# 创建必要的目录
echo "📁 创建必要目录..."
mkdir -p backend/logs
mkdir -p nginx/ssl

# 停止现有服务
echo "🛑 停止现有服务..."
docker-compose -f docker-compose.prod.yml down || true

# 构建镜像
echo "🔨 构建Docker镜像..."
docker-compose -f docker-compose.prod.yml build

# 启动服务
echo "▶️ 启动服务..."
docker-compose -f docker-compose.prod.yml up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 健康检查
echo "🏥 执行健康检查..."
for i in {1..10}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ 后端服务健康检查通过"
        break
    fi
    echo "⏳ 等待后端服务启动... ($i/10)"
    sleep 5
done

if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ 前端服务健康检查通过"
else
    echo "❌ 前端服务健康检查失败"
fi

# 显示服务状态
echo "📊 服务状态:"
docker-compose -f docker-compose.prod.yml ps

echo "🎉 部署完成!"
echo "📱 访问地址:"
echo "   - 前端: http://localhost:3000"
echo "   - API文档: http://localhost:8000/docs"
echo "   - 健康检查: http://localhost:8000/health"

# 显示日志
echo "📋 查看日志:"
echo "   docker-compose -f docker-compose.prod.yml logs -f" 