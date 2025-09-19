# 🛒 沃尔玛AI Agent平台 - API文档
# Walmart AI Agent Platform - API Documentation

## 概述

沃尔玛AI Agent平台提供了一套完整的RESTful API和WebSocket接口，支持智能对话、Agent管理、文档处理、数据分析等功能。

## 基础信息

- **基础URL**: `http://localhost:8080/api/v1`
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON
- **字符编码**: UTF-8

## 认证

所有API请求（除了登录和健康检查）都需要在请求头中包含JWT token：

```http
Authorization: Bearer <your_jwt_token>
```

### 获取Token

```http
POST /auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**响应**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "user_id",
    "username": "username",
    "email": "email@example.com",
    "full_name": "Full Name"
  }
}
```

## API端点

### 1. 健康检查

#### GET /health
检查系统健康状态

**响应**:
```json
{
  "status": "healthy",
  "timestamp": 1640995200,
  "version": "1.0.0",
  "components": {
    "database": "healthy",
    "redis": "healthy",
    "vector_db": "healthy"
  }
}
```

### 2. 聊天API

#### POST /chat/message
发送聊天消息

**请求体**:
```json
{
  "message": "请分析Q4销售数据",
  "conversation_id": "optional_conversation_id",
  "preferred_agent_id": "optional_agent_id",
  "stream": false
}
```

**响应**:
```json
{
  "id": "message_id",
  "message": "根据Q4销售数据分析...",
  "agent_id": "retail_analysis_agent_id",
  "agent_name": "零售分析助手",
  "conversation_id": "conversation_id",
  "timestamp": "2024-01-01T00:00:00Z",
  "metadata": {
    "query_type": "sales_analysis",
    "data_sources": 5,
    "confidence": 0.92
  }
}
```

#### POST /chat/stream
流式聊天消息

**请求体**: 同上，但会返回Server-Sent Events流

**响应**: 
```
data: {"content": "根据", "agent_id": "agent_id"}
data: {"content": "Q4销售", "agent_id": "agent_id"}
data: {"content": "数据分析", "agent_id": "agent_id"}
data: [DONE]
```

#### GET /chat/conversations
获取对话历史

**查询参数**:
- `limit`: 返回数量限制 (默认: 20)
- `offset`: 偏移量 (默认: 0)

**响应**:
```json
[
  {
    "conversation_id": "conv_123",
    "messages": [
      {
        "id": "msg_1",
        "role": "user",
        "content": "用户消息",
        "timestamp": "2024-01-01T00:00:00Z"
      },
      {
        "id": "msg_2",
        "role": "assistant",
        "content": "AI回复",
        "timestamp": "2024-01-01T00:01:00Z",
        "agent_id": "agent_id",
        "agent_name": "Agent名称"
      }
    ],
    "total_messages": 2,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:01:00Z"
  }
]
```

### 3. Agent管理API

#### GET /agents
获取Agent列表

**响应**:
```json
[
  {
    "id": "agent_id",
    "name": "零售分析助手",
    "description": "专门分析零售业务数据",
    "agent_type": "retail_analysis",
    "capabilities": ["data_analysis", "natural_language"],
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "stats": {
      "total_messages": 150,
      "success_rate": 0.95,
      "average_response_time": 2.3
    }
  }
]
```

#### POST /agents
创建新Agent

**请求体**:
```json
{
  "agent_type": "retail_analysis",
  "name": "自定义零售分析助手",
  "description": "专门处理零售数据分析",
  "capabilities": ["data_analysis", "natural_language", "reasoning"],
  "config": {
    "temperature": 0.7,
    "max_tokens": 2000
  }
}
```

**响应**:
```json
{
  "agent_id": "new_agent_id",
  "message": "Agent创建成功"
}
```

#### GET /agents/{agent_id}
获取Agent详情

**响应**:
```json
{
  "id": "agent_id",
  "name": "零售分析助手",
  "description": "专门分析零售业务数据",
  "agent_type": "retail_analysis",
  "capabilities": ["data_analysis", "natural_language"],
  "is_active": true,
  "config": {
    "temperature": 0.7,
    "max_tokens": 2000
  },
  "stats": {
    "total_messages": 150,
    "success_rate": 0.95,
    "average_response_time": 2.3,
    "last_active": "2024-01-01T00:00:00Z"
  }
}
```

#### PUT /agents/{agent_id}
更新Agent

**请求体**:
```json
{
  "name": "更新后的名称",
  "description": "更新后的描述",
  "is_active": true,
  "config": {
    "temperature": 0.8
  }
}
```

#### DELETE /agents/{agent_id}
删除Agent

**响应**:
```json
{
  "message": "Agent删除成功"
}
```

### 4. 文档管理API

#### POST /documents/upload
上传文档

**请求**: multipart/form-data
- `file`: 文件内容
- `collection_name`: 可选，指定集合名称

**响应**:
```json
{
  "document_id": "doc_id",
  "filename": "document.pdf",
  "file_size": 1024000,
  "file_type": "application/pdf",
  "collection_name": "default",
  "chunks_created": 15,
  "message": "文档上传并处理成功"
}
```

#### GET /documents
获取文档列表

**查询参数**:
- `collection_name`: 集合名称过滤
- `limit`: 限制数量
- `offset`: 偏移量

**响应**:
```json
[
  {
    "id": "doc_id",
    "filename": "sales_report.pdf",
    "file_size": 1024000,
    "file_type": "application/pdf",
    "collection_name": "sales_reports",
    "upload_time": "2024-01-01T00:00:00Z",
    "chunks_count": 15,
    "status": "processed"
  }
]
```

#### POST /documents/search
搜索文档

**请求体**:
```json
{
  "query": "销售数据分析",
  "collection_name": "optional_collection",
  "limit": 10,
  "threshold": 0.7
}
```

**响应**:
```json
{
  "results": [
    {
      "document_id": "doc_id",
      "filename": "sales_report.pdf",
      "chunk_text": "相关文本内容...",
      "score": 0.95,
      "metadata": {
        "page": 5,
        "section": "Q4分析"
      }
    }
  ],
  "total": 1,
  "query_time": 0.15
}
```

#### DELETE /documents/{document_id}
删除文档

### 5. 数据分析API

#### GET /analytics/dashboard-stats
获取仪表盘统计数据

**查询参数**:
- `range`: 时间范围 (1h, 24h, 7d, 30d)

**响应**:
```json
{
  "totalAgents": 5,
  "activeAgents": 4,
  "totalMessages": 1250,
  "successRate": 95.5,
  "averageResponseTime": 2300,
  "completedTasks": 89,
  "period": "24h"
}
```

#### GET /analytics/performance
获取性能数据

**响应**:
```json
{
  "responseTime": {
    "labels": ["00:00", "01:00", "02:00"],
    "values": [2100, 2300, 1900]
  },
  "successRate": {
    "labels": ["成功", "失败"],
    "values": [95.5, 4.5]
  },
  "throughput": {
    "requests_per_minute": 45,
    "peak_requests_per_minute": 120
  }
}
```

### 6. MCP协议API

#### GET /mcp/servers
获取MCP服务器列表

**响应**:
```json
[
  {
    "name": "walmart_data_server",
    "endpoint": "http://localhost:8001/mcp",
    "capabilities": ["resources", "tools", "prompts"],
    "tools_count": 3,
    "resources_count": 5,
    "status": "connected"
  }
]
```

#### POST /mcp/servers/register
注册MCP服务器

**请求体**:
```json
{
  "name": "custom_server",
  "endpoint": "http://custom-server:8000/mcp",
  "auth_token": "optional_token",
  "capabilities": ["resources", "tools"]
}
```

#### GET /mcp/tools
获取MCP工具列表

**响应**:
```json
[
  {
    "name": "analyze_sales_data",
    "description": "分析销售数据并生成报告",
    "inputSchema": {
      "type": "object",
      "properties": {
        "date_range": {"type": "string"},
        "category": {"type": "string"}
      },
      "required": ["date_range"]
    }
  }
]
```

#### POST /mcp/tools/call
调用MCP工具

**请求体**:
```json
{
  "server_name": "walmart_data_server",
  "tool_name": "analyze_sales_data",
  "arguments": {
    "date_range": "2024-Q4",
    "category": "electronics"
  },
  "session_id": "optional_session_id"
}
```

**响应**:
```json
{
  "result": {
    "analysis": "销售数据分析完成",
    "insights": ["电子产品销售增长15%"],
    "recommendations": ["加大电子产品库存"]
  },
  "execution_time": 2.5,
  "status": "success"
}
```

### 7. WebSocket API

#### WebSocket /ws/chat/{user_id}
实时聊天WebSocket连接

**连接**: `ws://localhost:8080/api/v1/ws/chat/{user_id}`

**发送消息格式**:
```json
{
  "type": "chat",
  "data": {
    "message": "请分析销售数据",
    "conversation_id": "optional",
    "preferred_agent_id": "optional"
  }
}
```

**接收消息格式**:
```json
{
  "type": "message",
  "data": {
    "message": "分析结果...",
    "agent_id": "agent_id",
    "agent_name": "Agent名称",
    "conversation_id": "conv_id"
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**其他消息类型**:
- `connection`: 连接确认
- `status`: 状态更新
- `error`: 错误消息
- `ping`/`pong`: 心跳检测

## 错误处理

所有API错误都返回以下格式：

```json
{
  "detail": "错误描述",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-01T00:00:00Z",
  "path": "/api/v1/endpoint"
}
```

### 常见错误码

- `400`: 请求参数错误
- `401`: 未认证
- `403`: 权限不足
- `404`: 资源不存在
- `422`: 数据验证失败
- `429`: 请求频率限制
- `500`: 服务器内部错误

## 限流规则

- 一般API: 10 requests/second
- 登录API: 1 request/second
- 文件上传: 5 requests/minute

## SDK使用示例

### Python

```python
import requests
import websocket
import json

class WalmartAIClient:
    def __init__(self, base_url="http://localhost:8080/api/v1"):
        self.base_url = base_url
        self.token = None
    
    def login(self, username, password):
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password}
        )
        data = response.json()
        self.token = data["access_token"]
        return data
    
    def send_message(self, message, conversation_id=None):
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {"message": message}
        if conversation_id:
            data["conversation_id"] = conversation_id
        
        response = requests.post(
            f"{self.base_url}/chat/message",
            json=data,
            headers=headers
        )
        return response.json()
    
    def connect_websocket(self, user_id):
        ws_url = f"ws://localhost:8080/api/v1/ws/chat/{user_id}"
        ws = websocket.WebSocket()
        ws.connect(ws_url)
        return ws

# 使用示例
client = WalmartAIClient()
client.login("admin", "password")
response = client.send_message("分析Q4销售数据")
print(response)
```

### JavaScript

```javascript
class WalmartAIClient {
    constructor(baseUrl = 'http://localhost:8080/api/v1') {
        this.baseUrl = baseUrl;
        this.token = null;
    }
    
    async login(username, password) {
        const response = await fetch(`${this.baseUrl}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await response.json();
        this.token = data.access_token;
        return data;
    }
    
    async sendMessage(message, conversationId) {
        const response = await fetch(`${this.baseUrl}/chat/message`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.token}`
            },
            body: JSON.stringify({
                message,
                conversation_id: conversationId
            })
        });
        return response.json();
    }
    
    connectWebSocket(userId) {
        const ws = new WebSocket(`ws://localhost:8080/api/v1/ws/chat/${userId}`);
        
        ws.onopen = () => console.log('WebSocket连接已建立');
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('收到消息:', data);
        };
        
        return ws;
    }
}

// 使用示例
const client = new WalmartAIClient();
client.login('admin', 'password').then(() => {
    client.sendMessage('分析Q4销售数据').then(response => {
        console.log(response);
    });
});
```

## 最佳实践

1. **认证管理**: 及时刷新token，处理认证失效
2. **错误处理**: 实现完善的错误处理和重试机制
3. **限流处理**: 遵守API限流规则，实现指数退避
4. **WebSocket管理**: 实现心跳检测和自动重连
5. **数据缓存**: 合理缓存不常变化的数据
6. **日志记录**: 记录API调用日志便于调试


---

如有问题，请联系技术支持或查看在线文档：http://localhost:8080/api/v1/docs
