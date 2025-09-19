# 🛒 沃尔玛AI Agent平台 - 部署指南
# Walmart AI Agent Platform - Deployment Guide

## 概述

本指南详细介绍如何在不同环境中部署沃尔玛AI Agent平台，包括开发环境、测试环境和生产环境的部署配置。

## 系统要求

### 硬件要求

**最低配置**:
- CPU: 4核心
- 内存: 8GB RAM
- 存储: 50GB SSD
- 网络: 100Mbps

**推荐配置**:
- CPU: 8核心
- 内存: 16GB RAM
- 存储: 200GB SSD
- 网络: 1Gbps

**生产环境**:
- CPU: 16核心
- 内存: 32GB RAM
- 存储: 500GB SSD (数据库) + 100GB SSD (应用)
- 网络: 10Gbps

### 软件要求

- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / Windows Server 2019+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Python**: 3.11+
- **Node.js**: 18+
- **PostgreSQL**: 15+
- **Redis**: 7+

## 快速部署

### 使用Docker Compose (推荐)

1. **克隆项目**:
```bash
git clone <repository-url>
cd Walmart-Agent
```

2. **配置环境变量**:
```bash
cp env.example .env
# 编辑 .env 文件，填入真实的配置值
```

3. **启动服务**:
```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

4. **访问应用**:
- 前端界面: http://localhost:3000
- API文档: http://localhost:8080/api/v1/docs
- 监控面板: http://localhost:3001 (Grafana)

### 使用启动脚本

**Linux/Mac**:
```bash
./scripts/start.sh
```

**Windows**:
```cmd
scripts\start.bat
```

## 详细部署步骤

### 1. 环境准备

#### 安装Docker和Docker Compose

**Ubuntu/Debian**:
```bash
# 更新包索引
sudo apt update

# 安装必要的包
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# 添加Docker官方GPG密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加Docker仓库
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 启动Docker服务
sudo systemctl enable docker
sudo systemctl start docker

# 添加用户到docker组
sudo usermod -aG docker $USER
```

**CentOS/RHEL**:
```bash
# 安装必要的包
sudo yum install -y yum-utils

# 添加Docker仓库
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 安装Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 启动Docker服务
sudo systemctl enable docker
sudo systemctl start docker
```

### 2. 配置文件设置

#### 环境变量配置

创建 `.env` 文件：
```bash
cp env.example .env
```

编辑 `.env` 文件，重要配置项：

```env
# 基础配置
APP_NAME="沃尔玛AI Agent平台"
ENVIRONMENT=production
DEBUG=false

# 安全配置 (生产环境必须更改)
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 数据库配置
DATABASE_URL=postgresql://walmart_admin:your_secure_password@postgres:5432/walmart_ai_agent
REDIS_URL=redis://:your_redis_password@redis:6379/0

# AI模型API密钥 (必须填入真实密钥)
OPENAI_API_KEY=your_openai_api_key_here
CHATGLM_API_KEY=your_chatglm_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Dify配置
DIFY_API_URL=http://dify:8001
DIFY_API_KEY=your_dify_api_key_here
```

#### SSL证书配置 (生产环境)

1. **生成自签名证书** (测试用):
```bash
mkdir -p configs/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout configs/ssl/key.pem \
  -out configs/ssl/cert.pem \
  -subj "/C=CN/ST=Beijing/L=Beijing/O=Walmart/CN=walmart-ai-agent.local"
```

2. **使用Let's Encrypt** (生产环境):
```bash
# 安装certbot
sudo apt install certbot

# 获取证书
sudo certbot certonly --standalone -d your-domain.com

# 复制证书到项目目录
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem configs/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem configs/ssl/key.pem
```

### 3. 服务部署

#### 使用Docker Compose

1. **构建镜像**:
```bash
docker-compose build
```

2. **启动服务**:
```bash
# 后台启动所有服务
docker-compose up -d

# 或者分步启动
docker-compose up -d postgres redis chromadb
sleep 30  # 等待数据库启动
docker-compose up -d backend
sleep 20  # 等待后端启动
docker-compose up -d frontend nginx
```

3. **验证部署**:
```bash
# 检查服务状态
docker-compose ps

# 查看日志
docker-compose logs backend
docker-compose logs frontend

# 健康检查
curl http://localhost/health
```

#### 手动部署

如果不使用Docker，可以手动部署各个组件：

1. **数据库部署**:
```bash
# PostgreSQL
sudo apt install postgresql-15
sudo -u postgres createuser walmart_admin
sudo -u postgres createdb walmart_ai_agent
sudo -u postgres psql -c "ALTER USER walmart_admin PASSWORD 'your_password';"

# Redis
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

2. **后端部署**:
```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
alembic upgrade head

# 启动应用
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

3. **前端部署**:
```bash
cd frontend

# 安装依赖
npm install

# 构建生产版本
npm run build

# 使用nginx服务静态文件
sudo cp -r build/* /var/www/html/
```

### 4. 反向代理配置

#### Nginx配置

创建 `/etc/nginx/sites-available/walmart-ai-agent`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # 前端代理
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API代理
    location /api/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket代理
    location /api/v1/ws/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/walmart-ai-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 5. 监控配置

#### Prometheus + Grafana

1. **启动监控服务**:
```bash
docker-compose -f docker-compose.monitoring.yml up -d
```

2. **访问监控面板**:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin)

3. **配置Grafana仪表盘**:
- 导入预定义的仪表盘配置
- 设置告警规则
- 配置通知渠道

## 环境特定配置

### 开发环境

```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    volumes:
      - ./backend:/app
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
    command: uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    volumes:
      - ./frontend:/app
    command: npm run dev
```

### 测试环境

```yaml
# docker-compose.test.yml
version: '3.8'
services:
  backend:
    build: ./backend
    environment:
      - ENVIRONMENT=testing
      - DATABASE_URL=postgresql://test_user:test_pass@postgres:5432/test_db
    command: pytest tests/

  frontend:
    build: ./frontend
    command: npm run test
```

### 生产环境

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  backend:
    build: ./backend
    restart: unless-stopped
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ./frontend
    restart: unless-stopped
```

## 数据备份与恢复

### 数据库备份

```bash
# 创建备份
docker-compose exec postgres pg_dump -U walmart_admin walmart_ai_agent > backup_$(date +%Y%m%d_%H%M%S).sql

# 恢复备份
docker-compose exec -T postgres psql -U walmart_admin walmart_ai_agent < backup_file.sql
```

### 向量数据库备份

```bash
# ChromaDB数据备份
docker-compose exec chromadb tar -czf /tmp/chroma_backup.tar.gz /app/chroma/data
docker cp $(docker-compose ps -q chromadb):/tmp/chroma_backup.tar.gz ./chroma_backup_$(date +%Y%m%d).tar.gz
```

### 自动备份脚本

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/walmart-ai-agent"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 数据库备份
docker-compose exec postgres pg_dump -U walmart_admin walmart_ai_agent > $BACKUP_DIR/db_backup_$DATE.sql

# 向量数据库备份
docker-compose exec chromadb tar -czf /tmp/chroma_backup.tar.gz /app/chroma/data
docker cp $(docker-compose ps -q chromadb):/tmp/chroma_backup.tar.gz $BACKUP_DIR/chroma_backup_$DATE.tar.gz

# 清理旧备份 (保留7天)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "备份完成: $BACKUP_DIR"
```

## 性能优化

### 数据库优化

1. **PostgreSQL配置优化**:
```sql
-- postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
```

2. **索引优化**:
```sql
-- 为常用查询创建索引
CREATE INDEX CONCURRENTLY idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX CONCURRENTLY idx_documents_collection_name ON documents(collection_name);
CREATE INDEX CONCURRENTLY idx_agents_is_active ON agents(is_active);
```

### 应用优化

1. **连接池配置**:
```python
# database.py
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

2. **Redis缓存配置**:
```python
# 缓存配置
CACHE_CONFIG = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_URL"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 50,
                "retry_on_timeout": True
            }
        },
        "TIMEOUT": 300
    }
}
```

## 故障排除

### 常见问题

1. **服务启动失败**:
```bash
# 检查端口占用
netstat -tulpn | grep :8080

# 检查Docker日志
docker-compose logs backend

# 检查磁盘空间
df -h
```

2. **数据库连接失败**:
```bash
# 检查数据库状态
docker-compose exec postgres pg_isready

# 检查连接配置
docker-compose exec backend env | grep DATABASE_URL
```

3. **内存不足**:
```bash
# 检查内存使用
free -h
docker stats

# 调整服务配置
# 在docker-compose.yml中添加内存限制
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
```

### 日志分析

1. **应用日志**:
```bash
# 查看实时日志
docker-compose logs -f backend

# 查看错误日志
docker-compose logs backend | grep ERROR

# 导出日志
docker-compose logs --no-color backend > backend.log
```

2. **系统监控**:
```bash
# 系统资源监控
htop
iotop
nethogs

# Docker监控
docker stats
docker system df
```

## 安全配置

### 网络安全

1. **防火墙配置**:
```bash
# Ubuntu UFW
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 8080/tcp  # 只允许内部访问
```

2. **Docker网络隔离**:
```yaml
# docker-compose.yml
networks:
  internal:
    driver: bridge
    internal: true
  external:
    driver: bridge

services:
  backend:
    networks:
      - internal
      - external
  postgres:
    networks:
      - internal  # 只能内部访问
```

### 应用安全

1. **环境变量加密**:
```bash
# 使用Docker secrets
echo "your_secret_key" | docker secret create jwt_secret -
```

2. **访问控制**:
```yaml
# nginx配置
location /api/admin/ {
    allow 192.168.1.0/24;
    deny all;
    proxy_pass http://backend;
}
```

## 扩展部署

### 水平扩展

1. **负载均衡配置**:
```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  backend:
    build: ./backend
    deploy:
      replicas: 3
  
  nginx:
    image: nginx:alpine
    volumes:
      - ./configs/nginx/upstream.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - backend
```

2. **数据库读写分离**:
```python
# 主从数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'walmart_ai_agent',
        'USER': 'walmart_admin',
        'HOST': 'postgres-master',
        'PORT': '5432',
    },
    'replica': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'walmart_ai_agent',
        'USER': 'readonly_user',
        'HOST': 'postgres-replica',
        'PORT': '5432',
    }
}
```

### Kubernetes部署

1. **Kubernetes配置文件**:
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: walmart-ai-agent-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: walmart-ai-agent-backend
  template:
    metadata:
      labels:
        app: walmart-ai-agent-backend
    spec:
      containers:
      - name: backend
        image: walmart-ai-agent/backend:latest
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: url
```

2. **Helm Chart配置**:
```yaml
# helm/values.yaml
replicaCount: 3

image:
  repository: walmart-ai-agent/backend
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 8080

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: walmart-ai-agent.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: walmart-ai-agent-tls
      hosts:
        - walmart-ai-agent.example.com
```

## 维护指南

### 定期维护任务

1. **系统更新**:
```bash
#!/bin/bash
# maintenance.sh

# 更新系统包
sudo apt update && sudo apt upgrade -y

# 清理Docker
docker system prune -f

# 重启服务
docker-compose restart

# 检查服务状态
docker-compose ps
```

2. **数据库维护**:
```sql
-- 定期执行的维护SQL
VACUUM ANALYZE;
REINDEX DATABASE walmart_ai_agent;

-- 清理过期数据
DELETE FROM messages WHERE created_at < NOW() - INTERVAL '90 days';
DELETE FROM logs WHERE created_at < NOW() - INTERVAL '30 days';
```

### 监控告警

1. **设置告警规则**:
```yaml
# prometheus/alert_rules.yml
groups:
- name: walmart-ai-agent
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 5m
    annotations:
      summary: "High error rate detected"
  
  - alert: DatabaseDown
    expr: up{job="postgres"} == 0
    for: 1m
    annotations:
      summary: "Database is down"
```

2. **通知配置**:
```yaml
# alertmanager.yml
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@walmart-ai-agent.com'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
- name: 'web.hook'
  email_configs:
  - to: 'admin@walmart-ai-agent.com'
    subject: '[Alert] {{ .GroupLabels.alertname }}'
    body: |
      {{ range .Alerts }}
      Alert: {{ .Annotations.summary }}
      {{ end }}
```

---

部署完成后，请访问系统管理界面进行初始配置和用户管理。如有问题，请查看故障排除部分或联系技术支持。
