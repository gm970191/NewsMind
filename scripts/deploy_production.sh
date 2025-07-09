#!/bin/bash
# NewsMind 生产环境部署脚本
# 适用于阿里云ECS部署

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 配置变量
PROJECT_NAME="newsmind"
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_DIR="/opt/backups"
LOG_DIR="/opt/logs"

# 检查Docker是否安装
check_docker() {
    log_info "检查Docker环境..."
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    log_success "Docker环境检查通过"
}

# 检查环境变量
check_environment() {
    log_info "检查环境变量..."
    
    if [ -z "$DEEPSEEK_API_KEY" ]; then
        log_warning "DEEPSEEK_API_KEY未设置，将使用默认值"
        export DEEPSEEK_API_KEY="demo-key"
    fi
    
    if [ -z "$DOMAIN" ]; then
        log_warning "DOMAIN未设置，将使用localhost"
        export DOMAIN="localhost"
    fi
    
    log_success "环境变量检查完成"
}

# 创建必要目录
create_directories() {
    log_info "创建必要目录..."
    
    mkdir -p $BACKUP_DIR
    mkdir -p $LOG_DIR
    mkdir -p /opt/newsmind/data
    
    log_success "目录创建完成"
}

# 备份现有数据
backup_data() {
    log_info "备份现有数据..."
    
    if [ -d "/opt/newsmind/data" ]; then
        BACKUP_FILE="$BACKUP_DIR/newsmind_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
        tar -czf $BACKUP_FILE -C /opt/newsmind data/
        log_success "数据备份完成: $BACKUP_FILE"
    else
        log_warning "没有找到现有数据，跳过备份"
    fi
}

# 构建Docker镜像
build_images() {
    log_info "构建Docker镜像..."
    
    # 构建后端镜像
    log_info "构建后端镜像..."
    docker build -t newsmind-backend:latest ./backend/
    
    # 构建前端镜像
    log_info "构建前端镜像..."
    docker build -t newsmind-frontend:latest ./frontend/
    
    log_success "Docker镜像构建完成"
}

# 停止现有服务
stop_services() {
    log_info "停止现有服务..."
    
    if docker-compose -f $DOCKER_COMPOSE_FILE ps | grep -q "Up"; then
        docker-compose -f $DOCKER_COMPOSE_FILE down
        log_success "现有服务已停止"
    else
        log_info "没有运行中的服务"
    fi
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 启动服务
    docker-compose -f $DOCKER_COMPOSE_FILE up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
    
    # 检查服务状态
    if docker-compose -f $DOCKER_COMPOSE_FILE ps | grep -q "Up"; then
        log_success "服务启动成功"
    else
        log_error "服务启动失败"
        docker-compose -f $DOCKER_COMPOSE_FILE logs
        exit 1
    fi
}

# 健康检查
health_check() {
    log_info "进行健康检查..."
    
    # 检查后端健康状态
    for i in {1..10}; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            log_success "后端服务健康检查通过"
            break
        else
            log_warning "后端服务健康检查失败，重试 $i/10"
            sleep 5
        fi
        
        if [ $i -eq 10 ]; then
            log_error "后端服务健康检查失败"
            return 1
        fi
    done
    
    # 检查前端服务
    for i in {1..10}; do
        if curl -f http://localhost:80 > /dev/null 2>&1; then
            log_success "前端服务健康检查通过"
            break
        else
            log_warning "前端服务健康检查失败，重试 $i/10"
            sleep 5
        fi
        
        if [ $i -eq 10 ]; then
            log_error "前端服务健康检查失败"
            return 1
        fi
    done
    
    return 0
}

# 配置防火墙
configure_firewall() {
    log_info "配置防火墙..."
    
    # 检查ufw是否可用
    if command -v ufw &> /dev/null; then
        # 允许HTTP和HTTPS端口
        ufw allow 80/tcp
        ufw allow 443/tcp
        ufw allow 8000/tcp  # 后端API端口
        
        log_success "防火墙配置完成"
    else
        log_warning "ufw未安装，请手动配置防火墙"
    fi
}

# 配置SSL证书（如果提供）
configure_ssl() {
    if [ -n "$SSL_CERT_PATH" ] && [ -n "$SSL_KEY_PATH" ]; then
        log_info "配置SSL证书..."
        
        # 复制证书文件
        cp $SSL_CERT_PATH /opt/newsmind/ssl/cert.pem
        cp $SSL_KEY_PATH /opt/newsmind/ssl/key.pem
        
        # 更新nginx配置
        sed -i 's/# ssl_certificate/ssl_certificate/g' /opt/newsmind/nginx.conf
        sed -i 's/# ssl_certificate_key/ssl_certificate_key/g' /opt/newsmind/nginx.conf
        
        log_success "SSL证书配置完成"
    else
        log_info "未提供SSL证书，跳过SSL配置"
    fi
}

# 设置定时任务
setup_cron() {
    log_info "设置定时任务..."
    
    # 创建日志轮转脚本
    cat > /opt/newsmind/rotate_logs.sh << 'EOF'
#!/bin/bash
# 日志轮转脚本
find /opt/logs -name "*.log" -mtime +7 -delete
find /opt/backups -name "*.tar.gz" -mtime +30 -delete
EOF
    
    chmod +x /opt/newsmind/rotate_logs.sh
    
    # 添加到crontab
    (crontab -l 2>/dev/null; echo "0 2 * * * /opt/newsmind/rotate_logs.sh") | crontab -
    
    log_success "定时任务设置完成"
}

# 显示部署信息
show_deployment_info() {
    log_success "部署完成！"
    echo ""
    echo "=== 部署信息 ==="
    echo "项目名称: $PROJECT_NAME"
    echo "前端地址: http://$DOMAIN"
    echo "API文档: http://$DOMAIN:8000/docs"
    echo "健康检查: http://$DOMAIN:8000/health"
    echo ""
    echo "=== 管理命令 ==="
    echo "查看服务状态: docker-compose -f $DOCKER_COMPOSE_FILE ps"
    echo "查看日志: docker-compose -f $DOCKER_COMPOSE_FILE logs"
    echo "重启服务: docker-compose -f $DOCKER_COMPOSE_FILE restart"
    echo "停止服务: docker-compose -f $DOCKER_COMPOSE_FILE down"
    echo ""
    echo "=== 监控信息 ==="
    echo "日志目录: $LOG_DIR"
    echo "备份目录: $BACKUP_DIR"
    echo "数据目录: /opt/newsmind/data"
}

# 主部署流程
main() {
    log_info "开始部署 NewsMind 生产环境..."
    
    # 检查当前目录
    if [ ! -f "docker-compose.prod.yml" ]; then
        log_error "请在项目根目录运行此脚本"
        exit 1
    fi
    
    # 执行部署步骤
    check_docker
    check_environment
    create_directories
    backup_data
    build_images
    stop_services
    start_services
    
    if health_check; then
        configure_firewall
        configure_ssl
        setup_cron
        show_deployment_info
        log_success "NewsMind 部署成功！"
    else
        log_error "健康检查失败，部署中止"
        exit 1
    fi
}

# 清理函数
cleanup() {
    log_info "清理临时文件..."
    docker system prune -f
    log_success "清理完成"
}

# 错误处理
trap cleanup EXIT

# 运行主函数
main "$@" 