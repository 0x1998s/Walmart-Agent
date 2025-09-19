#!/bin/bash
# 🛒 沃尔玛AI Agent平台 - 启动脚本
# Walmart AI Agent Platform - Startup Script

set -e

echo "🛒 启动沃尔玛AI Agent平台..."

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

# 检查环境
check_environment() {
    log_info "检查环境依赖..."
    
    # 检查Python版本
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if [[ $(echo "$PYTHON_VERSION >= 3.11" | bc -l) -eq 1 ]]; then
            log_success "Python版本: $PYTHON_VERSION ✓"
        else
            log_error "需要Python 3.11+，当前版本: $PYTHON_VERSION"
            exit 1
        fi
    else
        log_error "未找到Python3"
        exit 1
    fi
    
    # 检查Node.js版本
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node -v | sed 's/v//')
        if [[ $(echo "$NODE_VERSION >= 18.0.0" | bc -l) -eq 1 ]]; then
            log_success "Node.js版本: $NODE_VERSION ✓"
        else
            log_error "需要Node.js 18+，当前版本: $NODE_VERSION"
            exit 1
        fi
    else
        log_error "未找到Node.js"
        exit 1
    fi
    
    # 检查Docker
    if command -v docker &> /dev/null; then
        log_success "Docker已安装 ✓"
    else
        log_warning "Docker未安装，将使用本地模式"
    fi
    
    # 检查Docker Compose
    if command -v docker-compose &> /dev/null; then
        log_success "Docker Compose已安装 ✓"
    else
        log_warning "Docker Compose未安装"
    fi
}

# 创建必要目录
create_directories() {
    log_info "创建必要目录..."
    
    mkdir -p data/uploads
    mkdir -p logs
    mkdir -p configs/chromadb
    mkdir -p configs/nginx
    mkdir -p configs/prometheus
    mkdir -p configs/grafana/dashboards
    mkdir -p configs/grafana/datasources
    
    log_success "目录创建完成 ✓"
}

# 生成配置文件
generate_configs() {
    log_info "生成配置文件..."
    
    # 生成环境变量文件
    if [ ! -f .env ]; then
        cat > .env << EOF
# 🛒 沃尔玛AI Agent平台环境配置
# Walmart AI Agent Platform Environment Configuration

# 基础配置
APP_NAME="沃尔玛AI Agent平台"
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=INFO

# 数据库配置
DATABASE_URL=postgresql://walmart_admin:walmart_secure_2024@localhost:5432/walmart_ai_agent
REDIS_URL=redis://:walmart_redis_2024@localhost:6379/0

# 向量数据库配置
CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_AUTH_USER=admin
CHROMA_AUTH_PASSWORD=walmart_chroma_2024

# AI模型配置 (请填入真实的API密钥)
OPENAI_API_KEY=your_openai_api_key_here
CHATGLM_API_KEY=your_chatglm_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Dify配置
DIFY_API_URL=http://localhost:8001
DIFY_API_KEY=your_dify_api_key_here

# 安全配置
SECRET_KEY=walmart-ai-agent-super-secret-key-2024
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Celery配置
CELERY_BROKER_URL=redis://:walmart_redis_2024@localhost:6379/1
CELERY_RESULT_BACKEND=redis://:walmart_redis_2024@localhost:6379/2
EOF
        log_success "生成环境配置文件 .env ✓"
    fi
    
    # 生成ChromaDB认证文件
    if [ ! -f configs/chromadb/server.htpasswd ]; then
        echo "admin:walmart_chroma_2024" > configs/chromadb/server.htpasswd
        log_success "生成ChromaDB认证文件 ✓"
    fi
}

# 安装依赖
install_dependencies() {
    log_info "安装依赖包..."
    
    # 安装后端依赖
    if [ -f backend/requirements.txt ]; then
        log_info "安装Python依赖..."
        cd backend
        python3 -m pip install -r requirements.txt
        cd ..
        log_success "Python依赖安装完成 ✓"
    fi
    
    # 安装前端依赖
    if [ -f frontend/package.json ]; then
        log_info "安装Node.js依赖..."
        cd frontend
        npm install
        cd ..
        log_success "Node.js依赖安装完成 ✓"
    fi
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 检查是否使用Docker
    if command -v docker-compose &> /dev/null && [ "$USE_DOCKER" = "true" ]; then
        log_info "使用Docker Compose启动服务..."
        docker-compose up -d
        log_success "Docker服务启动完成 ✓"
        
        # 等待服务启动
        log_info "等待服务启动..."
        sleep 30
        
        # 检查服务状态
        docker-compose ps
        
    else
        log_info "使用本地模式启动服务..."
        
        # 启动后端服务
        log_info "启动后端API服务..."
        cd backend
        nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080 > ../logs/backend.log 2>&1 &
        BACKEND_PID=$!
        echo $BACKEND_PID > ../logs/backend.pid
        cd ..
        log_success "后端服务启动完成 (PID: $BACKEND_PID) ✓"
        
        # 启动前端服务
        log_info "启动前端开发服务器..."
        cd frontend
        nohup npm run dev > ../logs/frontend.log 2>&1 &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > ../logs/frontend.pid
        cd ..
        log_success "前端服务启动完成 (PID: $FRONTEND_PID) ✓"
    fi
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    # 检查后端API
    if curl -s http://localhost:8080/health > /dev/null; then
        log_success "后端API服务正常 ✓"
    else
        log_warning "后端API服务检查失败"
    fi
    
    # 检查前端服务
    if curl -s http://localhost:3000 > /dev/null; then
        log_success "前端服务正常 ✓"
    else
        log_warning "前端服务检查失败"
    fi
}

# 显示访问信息
show_access_info() {
    echo ""
    echo "🎉 沃尔玛AI Agent平台启动完成！"
    echo ""
    echo "📍 访问地址："
    echo "   前端管理界面: http://localhost:3000"
    echo "   后端API文档: http://localhost:8080/api/v1/docs"
    echo "   系统健康检查: http://localhost:8080/health"
    echo ""
    echo "📊 监控地址："
    echo "   Prometheus: http://localhost:9090"
    echo "   Grafana: http://localhost:3001 (admin/walmart_grafana_2024)"
    echo "   Flower: http://localhost:5555 (admin/walmart_flower_2024)"
    echo ""
    echo "📝 日志文件："
    echo "   后端日志: logs/backend.log"
    echo "   前端日志: logs/frontend.log"
    echo ""
    echo "🛑 停止服务: ./scripts/stop.sh"
    echo ""
}

# 主函数
main() {
    echo "🛒 沃尔玛AI Agent平台启动脚本"
    echo "================================"
    
    # 解析参数
    USE_DOCKER=false
    SKIP_DEPS=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --docker)
                USE_DOCKER=true
                shift
                ;;
            --skip-deps)
                SKIP_DEPS=true
                shift
                ;;
            --help)
                echo "使用方法: $0 [选项]"
                echo "选项:"
                echo "  --docker      使用Docker Compose启动"
                echo "  --skip-deps   跳过依赖安装"
                echo "  --help        显示帮助信息"
                exit 0
                ;;
            *)
                log_error "未知选项: $1"
                exit 1
                ;;
        esac
    done
    
    # 执行启动流程
    check_environment
    create_directories
    generate_configs
    
    if [ "$SKIP_DEPS" != "true" ]; then
        install_dependencies
    fi
    
    start_services
    sleep 10
    health_check
    show_access_info
}

# 错误处理
trap 'log_error "启动过程中发生错误，请检查日志"; exit 1' ERR

# 执行主函数
main "$@"
