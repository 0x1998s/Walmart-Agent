# 🛒 沃尔玛AI Agent平台
## Walmart AI Agent Platform

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61dafb.svg)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178c6.svg)](https://typescriptlang.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ed.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

**🚀 基于沃尔玛JD需求开发的企业级AI Agent**

**作者：Jemmy Yang | 微信：Joeng_Jimmy**

</div>

---

## 🎯 项目概述

**沃尔玛AI Agent**是基于沃尔玛高级算法工程师JD需求开发的企业级AI Agent,该项目展现了从需求分析到系统实现的完整能力，是一个真正可投入生产使用的AI Agent解决方案。

### 🌟 核心特性

- 🧠 **多Agent协同架构** - 销售、库存、客服、数据分析专业Agent
- 📊 **向量数据库集成** - ChromaDB多源数据整合，支持结构化/非结构化数据  
- 🔗 **MCP协议支持** - 2025前沿Agent通信标准，工具集成和资源管理
- 🚀 **多LLM支持** - OpenAI/ChatGLM/DeepSeek统一接口
- ⚡ **实时WebSocket** - 双向通信，实时数据推送和Agent状态监控
- 📈 **算法Metrics体系** - 完整的性能评估和监控系统

### 🏆 技术亮点

- **企业级架构**: 微服务 + 多Agent + 插件化设计
- **AI原生**: 多LLM支持 + 向量检索 + 图混合检索  
- **生产就绪**: 完整监控 + 日志 + 容器化部署
- **高性能**: 异步处理 + 缓存优化 + 连接池管理

### 🏗️ 系统架构图

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端管理界面   │    │   API网关层     │    │   AI Agent核心   │
│   React + TS    │◄──►│   FastAPI      │◄──►│   LangChain     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   向量数据库     │    │   关系型数据库   │    │   大模型服务     │
│   ChromaDB     │◄──►│   PostgreSQL   │    │   Multi-LLM     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🔧 核心功能模块

#### 1. Dify平台集成模块
- Dify SDK封装
- 工作流自动化
- 模板管理系统

#### 2. 多源数据整合模块
- 结构化数据处理 (SQL/NoSQL)
- 非结构化数据处理 (文档/图片/音视频)
- 数据清洗与标准化
- 实时数据流处理

#### 3. 向量数据库系统
- ChromaDB集群部署
- 多维向量索引
- 相似度搜索优化
- 数据版本管理

#### 4. AI Agent引擎
- 多模型支持 (ChatGLM/GPT/DeepSeek)
- 智能路由与负载均衡
- 上下文记忆管理
- 任务编排与执行

#### 5. Metrics评估体系
- 实时性能监控
- 准确率评估
- 用户满意度追踪
- A/B测试框架

---

## 🏗️ 技术架构

### 🚀 后端技术栈

#### 核心框架
- **FastAPI** - 高性能异步API服务
- **SQLAlchemy** - 异步数据库ORM  
- **Pydantic** - 数据验证和序列化
- **Celery** - 分布式任务队列

#### AI/LLM集成
- **Dify Platform** - 开源LLM应用开发平台
- **OpenAI API** - GPT系列模型
- **ChatGLM API** - 智谱清言模型
- **DeepSeek API** - DeepSeek模型
- **LangChain** - LLM应用开发框架

#### 数据存储
- **PostgreSQL** - 主数据库（生产环境）
- **SQLite** - 轻量级数据库（开发环境）
- **Redis** - 缓存和会话存储
- **ChromaDB** - 向量数据库

#### 通信协议
- **MCP (Model Context Protocol)** - 2025前沿Agent通信标准
- **WebSocket** - 实时双向通信
- **RESTful API** - 标准HTTP接口

### 🎨 前端技术栈
- **React 18** - 现代前端框架
- **TypeScript** - 类型安全
- **Ant Design Pro** - 企业级UI组件库
- **ECharts** - 专业数据可视化
- **Zustand** - 轻量级状态管理
- **Vite** - 高性能构建工具

### 🔧 基础设施
- **Docker** - 容器化部署
- **Docker Compose** - 多容器编排
- **Nginx** - 反向代理和负载均衡
- **Prometheus + Grafana** - 监控告警
- **ELK Stack** - 日志管理

---

## 📁 项目结构

```
Walmart-Agent/
├── backend/                          # 🚀 后端服务
│   ├── app/
│   │   ├── agents/                   # 🤖 多Agent实现
│   │   │   ├── base_agent.py        # Agent基类
│   │   │   ├── retail_agent.py      # 零售分析Agent
│   │   │   ├── sales_agent.py       # 销售Agent
│   │   │   ├── inventory_agent.py   # 库存Agent
│   │   │   ├── customer_service_agent.py # 客服Agent
│   │   │   ├── data_analysis_agent.py    # 数据分析Agent
│   │   │   └── orchestrator.py      # Agent编排器
│   │   ├── api/                     # 🌐 API接口层
│   │   │   └── v1/
│   │   │       ├── chat.py          # 聊天接口
│   │   │       ├── agents.py        # Agent管理接口
│   │   │       ├── mcp.py           # MCP协议接口
│   │   │       └── websocket.py     # WebSocket接口
│   │   ├── core/                    # 🏗️ 核心功能
│   │   │   ├── config.py           # 配置管理
│   │   │   ├── database.py         # 数据库连接
│   │   │   └── dependencies.py     # 依赖注入
│   │   ├── models/                  # 📊 数据模型
│   │   ├── services/                # 🔧 业务服务层
│   │   │   ├── llm_service.py      # LLM服务
│   │   │   ├── vector_service.py   # 向量检索服务
│   │   │   ├── data_service.py     # 数据处理服务
│   │   │   ├── mcp_service.py      # MCP协议服务
│   │   │   └── metrics_service.py  # 指标评估服务
│   │   └── utils/                   # 🛠️ 工具函数
│   ├── tests/                       # 🧪 测试用例
│   ├── Dockerfile                   # 🐳 后端容器配置
│   └── requirements.txt             # 📦 Python依赖
├── frontend/                        # 🎨 前端应用
│   ├── src/
│   │   ├── components/             # React组件
│   │   ├── pages/                  # 页面组件
│   │   │   ├── Dashboard.tsx       # 仪表板
│   │   │   ├── ChatInterface.tsx   # 聊天界面
│   │   │   ├── AgentManagement.tsx # Agent管理
│   │   │   └── Analytics.tsx       # 数据分析
│   │   ├── services/               # API服务
│   │   ├── stores/                 # 状态管理
│   │   └── utils/                  # 工具函数
│   ├── Dockerfile                  # 🐳 前端容器配置
│   └── package.json               # 📦 Node.js依赖
├── configs/                        # ⚙️ 配置文件
│   ├── nginx/                      # Nginx配置
│   ├── prometheus/                 # Prometheus配置
│   └── grafana/                    # Grafana配置
├── docs/                          # 📚 项目文档
├── scripts/                       # 📜 脚本文件
├── docker-compose.yml             # 🐳 容器编排
├── .github/                       # 🔧 GitHub配置
├── .gitignore                     # 📝 Git忽略文件
├── LICENSE                        # 📄 开源许可证
├── CONTRIBUTING.md                # 🤝 贡献指南
├── 简介.md                        # 📖 项目简介
└── README.md                      # 📖 项目说明
```

---

## 🔗 Dify平台集成

### Dify开源AI应用开发平台

本项目深度集成了**Dify平台**，作为企业级AI应用开发的核心基础设施：

#### 🌟 Dify平台优势
- **🔧 低代码开发** - 可视化工作流设计，快速构建AI应用
- **🤖 多模型支持** - 统一接口管理不同LLM模型
- **📚 知识库管理** - 内置RAG系统，支持多格式文档
- **🔄 工作流编排** - 复杂业务逻辑的可视化编排
- **📊 应用监控** - 完整的应用性能和使用统计

#### 🔧 集成功能

##### 1. **Dify SDK集成**
```python
# Dify客户端初始化
dify_client = DifyClient(
    api_key=settings.DIFY_API_KEY,
    base_url=settings.DIFY_API_URL
)

# 聊天对话
response = await dify_client.chat_messages.create(
    inputs={},
    query="分析沃尔玛上季度销售数据",
    user="walmart_user",
    conversation_id=conversation_id
)
```

##### 2. **工作流自动化**
- **业务流程模板** - 预置零售业务分析流程
- **动态参数传递** - 支持复杂业务参数配置
- **条件分支处理** - 智能业务逻辑判断
- **异常处理机制** - 完整的错误处理和重试

##### 3. **知识库管理**
- **文档自动入库** - 支持PDF、Word、Excel等格式
- **向量化处理** - 自动生成文档向量表示
- **智能检索** - 基于语义的文档检索
- **版本管理** - 知识库内容版本控制

##### 4. **应用编排**
```python
# Dify工作流调用
workflow_result = await dify_service.run_workflow(
    workflow_id="retail_analysis_flow",
    inputs={
        "time_period": "Q3_2024",
        "store_locations": ["北京", "上海", "深圳"],
        "analysis_type": "sales_trend"
    }
)
```

#### 🎯 业务场景应用

##### **零售数据分析流程**
1. **数据收集** → Dify工作流自动收集多源数据
2. **数据处理** → 内置数据清洗和标准化流程
3. **AI分析** → 多模型协同分析业务指标
4. **报告生成** → 自动生成可视化分析报告
5. **结果推送** → 多渠道结果分发和通知

##### **客户服务自动化**
- **智能客服** - Dify构建的多轮对话系统
- **问题分类** - 自动识别和分类客户问题
- **解决方案推荐** - 基于知识库的智能推荐
- **人工转接** - 复杂问题无缝转人工处理

#### 📊 Dify集成架构

```
┌─────────────────────────────────────────────────────────┐
│                    Walmart AI Agent                    │
├─────────────────────────────────────────────────────────┤
│                    Dify Platform                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   工作流     │  │   知识库     │  │   模型管理   │    │
│  │  Workflow   │  │ Knowledge   │  │   Models    │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
├─────────────────────────────────────────────────────────┤
│                   LLM Models                           │
│  OpenAI GPT  │  ChatGLM  │  DeepSeek  │  Local Models │
└─────────────────────────────────────────────────────────┘
```

#### ⚙️ Docker配置

```yaml
# docker-compose.yml 中的Dify服务配置
dify:
  image: langgenius/dify-web:latest
  ports:
    - "3001:3000"
  environment:
    - CONSOLE_API_URL=http://dify-api:5001
    - APP_API_URL=http://dify-api:5001
  depends_on:
    - dify-api

dify-api:
  image: langgenius/dify-api:latest
  ports:
    - "5001:5001"
  environment:
    - SECRET_KEY=walmart-dify-secret
    - DB_HOST=postgres
    - REDIS_HOST=redis
```

---

## 🤖 Agent架构设计

### 核心Agent类型

#### 1. 🏪 零售分析Agent (RetailAnalysisAgent)
- **职责**: 综合零售业务分析
- **能力**: 销售趋势、库存分析、客户行为
- **输出**: 业务洞察、预测报告

#### 2. 💰 销售Agent (SalesAgent)  
- **职责**: 销售数据分析和预测
- **能力**: 收入分析、销售预测、绩效报告
- **输出**: 销售报表、预测模型

#### 3. 📦 库存Agent (InventoryAgent)
- **职责**: 库存管理和优化
- **能力**: 库存监控、补货预警、周转分析
- **输出**: 库存报告、补货建议

#### 4. 🎧 客户服务Agent (CustomerServiceAgent)
- **职责**: 客户服务和关系管理
- **能力**: 智能客服、投诉处理、CRM管理
- **输出**: 服务报告、客户画像

#### 5. 📊 数据分析Agent (DataAnalysisAgent)
- **职责**: 高级数据分析和建模
- **能力**: 统计建模、预测分析、数据可视化
- **输出**: 分析报告、预测模型

### Agent协同机制

```python
# Agent编排器示例
orchestrator = AgentOrchestrator()

# 智能路由 - 根据消息内容选择合适的Agent
message = "分析一下上个月的销售趋势"
agent = await orchestrator.route_message(message, user_id)

# 多Agent协同 - 复杂任务分解
task = "生成季度业务报告"
agents = await orchestrator.decompose_task(task)
```

---

## 🔗 MCP协议集成

### Model Context Protocol 支持

作为2025年的前沿Agent通信标准，本项目率先集成了MCP协议：

#### 🛠️ 工具注册
```python
# 注册MCP工具
await mcp_service.register_server(MCPServer(
    name="walmart_tools",
    endpoint="http://localhost:8002",
    capabilities=["tools", "resources", "prompts"]
))
```

#### 📚 资源管理
```python
# 获取MCP资源
resources = await mcp_service.list_resources("walmart_tools")
content = await mcp_service.get_resource("walmart_tools", "sales_data")
```

#### 🔧 工具调用
```python
# 调用MCP工具
result = await mcp_service.call_tool(
    server_name="walmart_tools",
    tool_name="analyze_sales",
    arguments={"period": "last_month"}
)
```

---

## 🚀 快速开始

### 📋 环境要求
- **Python 3.11+** - 后端开发语言
- **Node.js 18+** - 前端开发环境  
- **Docker & Docker Compose** - 容器化部署
- **PostgreSQL 13+** - 主数据库（生产环境）
- **Redis 6+** - 缓存和会话存储

### 🛠️ 安装步骤

#### 方式一：Docker快速部署（推荐）
```bash
# 1. 克隆项目
git clone https://github.com/0x1998s/Walmart-Agent.git
cd Walmart-Agent

# 2. 配置环境变量
cp env.example .env
# 编辑.env文件，设置API密钥和数据库连接

# 3. 一键启动所有服务
docker-compose up -d

# 4. 访问应用
# 前端: http://localhost:3000
# 后端API: http://localhost:8000  
# API文档: http://localhost:8000/docs
```

#### 方式二：本地开发部署
```bash
# 1. 克隆项目
git clone https://github.com/0x1998s/Walmart-Agent.git
cd Walmart-Agent

# 2. 后端设置
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件

# 启动后端服务
uvicorn app.main:app --reload --port 8000

# 3. 前端设置（新终端）
cd frontend  
npm install
npm run dev

# 4. 启动外部服务
# PostgreSQL, Redis, ChromaDB等
```

### 🔧 配置说明

#### 环境变量配置
```bash
# .env文件示例
# 数据库配置
DATABASE_URL=postgresql://walmart_admin:walmart_secure_2024@localhost:5432/walmart_ai_agent
REDIS_URL=redis://:walmart_redis_2024@localhost:6379/0

# AI模型配置
OPENAI_API_KEY=your_openai_api_key
CHATGLM_API_KEY=your_chatglm_api_key  
DEEPSEEK_API_KEY=your_deepseek_api_key

# 向量数据库配置
CHROMA_HOST=localhost
CHROMA_PORT=8001

# 安全配置
SECRET_KEY=walmart-ai-agent-super-secret-key-2024
```

---

## 📖 使用示例

### 💬 聊天对话
```bash
# 健康检查
curl http://localhost:8000/health

# 发送聊天消息
curl -X POST "http://localhost:8000/api/v1/chat/message" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{
       "message": "分析一下上个月的销售数据",
       "preferred_agent_id": "sales_agent"
     }'
```

### 🤖 Agent管理
```bash
# 获取Agent列表
curl -X GET "http://localhost:8000/api/v1/agents" \
     -H "Authorization: Bearer YOUR_TOKEN"

# 创建新Agent
curl -X POST "http://localhost:8000/api/v1/agents" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{
       "agent_type": "custom",
       "name": "自定义Agent",
       "description": "专门处理特定业务逻辑",
       "capabilities": ["data_analysis", "natural_language"]
     }'
```

### 🛠️ MCP工具调用
```bash
# 列出可用工具
curl -X GET "http://localhost:8000/api/v1/mcp/tools" \
     -H "Authorization: Bearer YOUR_TOKEN"

# 调用MCP工具
curl -X POST "http://localhost:8000/api/v1/mcp/tools/call" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{
       "server_name": "walmart_tools",
       "tool_name": "analyze_inventory",
       "arguments": {"store_id": "store_001"}
     }'
```

### 🔄 Dify工作流调用
```bash
# 创建Dify工作流
curl -X POST "http://localhost:8000/api/v1/dify/workflows" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{
       "name": "零售数据分析流程",
       "description": "自动分析零售业务数据",
       "graph": {
         "nodes": [
           {
             "id": "start",
             "type": "start",
             "data": {"title": "开始"}
           },
           {
             "id": "data_collect",
             "type": "code",
             "data": {
               "title": "数据收集",
               "code": "# 收集销售数据"
             }
           }
         ]
       }
     }'

# 运行Dify工作流
curl -X POST "http://localhost:8000/api/v1/dify/workflows/run" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{
       "workflow_id": "retail_analysis_flow",
       "inputs": {
         "time_period": "Q4_2024",
         "store_id": "walmart_001"
       }
     }'
```

### ⚡ WebSocket实时通信
```javascript
// 前端WebSocket连接
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/chat/user123');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('收到消息:', data);
};

// 发送消息
ws.send(JSON.stringify({
    type: 'chat',
    data: {
        message: '实时分析当前库存状态',
        agent_id: 'inventory_agent'
    }
}));
```

---

## 🧪 测试

### 后端测试
```bash
cd backend

# 运行所有测试
pytest tests/ -v

# 运行测试并生成覆盖率报告
pytest tests/ -v --cov=. --cov-report=html

# 运行特定测试
pytest tests/test_agents.py::TestRetailAnalysisAgent -v
```

### 前端测试
```bash
cd frontend

# 运行测试
npm test

# 运行测试并生成覆盖率报告  
npm run test:coverage

# 类型检查
npm run type-check

# 构建测试
npm run build
```

### 集成测试
```bash
# 启动完整服务栈
docker-compose up -d

# 等待服务启动
sleep 30

# 健康检查
curl -f http://localhost:8000/health
curl -f http://localhost:3000

# API集成测试
curl -f http://localhost:8000/api/v1/agents

# 清理环境
docker-compose down
```

---

## 📊 监控和日志

### Prometheus监控指标
- **请求数量**: HTTP请求总数和成功率
- **响应时间**: API响应时间分布  
- **Agent性能**: Agent处理时间和成功率
- **资源使用**: CPU、内存、数据库连接数

### Grafana可视化面板
- **系统概览**: 整体健康状态和关键指标
- **Agent监控**: 各Agent的性能和状态
- **用户活动**: 用户访问和使用情况
- **错误追踪**: 错误率和异常监控

### 日志管理
```python
# 结构化日志示例
logger.info("Agent处理消息", extra={
    "agent_id": agent.id,
    "user_id": context.user_id,
    "message_length": len(message),
    "processing_time": elapsed_time
})
```

---

## 🔒 安全特性

### 身份认证
- **JWT令牌**: 无状态身份验证
- **角色权限**: 基于角色的访问控制
- **会话管理**: Redis会话存储

### 数据安全
- **输入验证**: Pydantic数据验证
- **SQL注入防护**: SQLAlchemy ORM保护
- **敏感信息加密**: 密码哈希和API密钥保护

### API安全
- **速率限制**: 防止API滥用
- **CORS配置**: 跨域请求控制
- **HTTPS支持**: 生产环境TLS加密

---

## 📈 性能优化

### 后端优化
- **异步处理**: 全异步架构，提高并发性能
- **连接池**: 数据库连接池管理
- **缓存策略**: Redis缓存热点数据
- **任务队列**: Celery异步任务处理

### 前端优化  
- **代码分割**: 动态导入减少初始加载
- **组件缓存**: React.memo优化渲染
- **状态管理**: Zustand轻量级状态管理
- **构建优化**: Vite快速构建和热更新

### 数据库优化
- **索引优化**: 关键字段索引
- **查询优化**: N+1查询问题解决
- **分页查询**: 大数据集分页处理
- **连接优化**: 连接池和超时配置

---

## 🚀 部署指南

### 生产环境部署

#### 1. 环境准备
```bash
# 安装Docker和Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. 配置文件
```bash
# 复制生产环境配置
cp env.example .env.production

# 编辑生产环境变量
nano .env.production
```

#### 3. 启动服务
```bash
# 使用生产配置启动
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 检查服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 4. 数据库迁移
```bash
# 运行数据库迁移
docker-compose exec backend alembic upgrade head

# 创建初始数据
docker-compose exec backend python -m app.core.init_data
```

### 扩展部署

#### 水平扩展
```bash
# 扩展后端服务实例
docker-compose up -d --scale backend=3

# 扩展前端服务实例  
docker-compose up -d --scale frontend=2
```

#### 负载均衡
```nginx
# Nginx负载均衡配置
upstream backend {
    server backend_1:8000;
    server backend_2:8000;
    server backend_3:8000;
}

server {
    listen 80;
    location /api/ {
        proxy_pass http://backend;
    }
}
```

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！请查看 [CONTRIBUTING.md](./CONTRIBUTING.md) 了解详细信息。

### 快速贡献步骤
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证。详情请查看 [LICENSE](./LICENSE) 文件。

---

## 📞 联系方式

- **作者**: Jemmy Yang
- **微信**: Joeng_Jimmy  
- **邮箱**: jemmy_yang@yeah.net
- **GitHub**: [@0x1998s](https://github.com/0x1998s)
- **项目地址**: [https://github.com/0x1998s/Walmart-Agent](https://github.com/0x1998s/Walmart-Agent)

---

## 🙏 致谢

感谢以下开源项目的支持：
- [FastAPI](https://fastapi.tiangolo.com/) - 高性能Web框架
- [React](https://reactjs.org/) - 用户界面库
- [ChromaDB](https://www.trychroma.com/) - 向量数据库
- [Ant Design](https://ant.design/) - 企业级UI设计语言
- [Docker](https://www.docker.com/) - 容器化平台

---

## 📊 项目统计

<div align="center">

![GitHub stars](https://img.shields.io/github/stars/0x1998s/Walmart-Agent?style=social)
![GitHub forks](https://img.shields.io/github/forks/0x1998s/Walmart-Agent?style=social)
![GitHub issues](https://img.shields.io/github/issues/0x1998s/Walmart-Agent)
![GitHub pull requests](https://img.shields.io/github/issues-pr/0x1998s/Walmart-Agent)

</div>

---

<div align="center">

**欢迎HR和技术负责人联系我，期待与您深入交流！**

**🚀 沃尔玛AI Agent - 让零售业务更智能**

*最后更新: 2025年9月*

</div>
