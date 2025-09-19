# 🛒 沃尔玛AI Agent平台 - API测试
# Walmart AI Agent Platform - API Tests

import pytest
import json
from fastapi.testclient import TestClient
from tests.conftest import assert_response_ok, assert_response_created, assert_response_error


class TestHealthCheck:
    """健康检查API测试"""
    
    def test_health_check(self, client):
        """测试健康检查端点"""
        response = client.get("/health")
        data = assert_response_ok(response)
        
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data


class TestChatAPI:
    """聊天API测试"""
    
    def test_send_message(self, client, sample_chat_message, auth_headers):
        """测试发送消息"""
        response = client.post(
            "/api/v1/chat/message",
            json=sample_chat_message,
            headers=auth_headers
        )
        
        data = assert_response_ok(response)
        
        assert "message" in data
        assert "agent_id" in data
        assert "conversation_id" in data
        assert "timestamp" in data
    
    def test_send_message_without_auth(self, client, sample_chat_message):
        """测试未认证发送消息"""
        response = client.post(
            "/api/v1/chat/message",
            json=sample_chat_message
        )
        
        assert_response_error(response, 401)
    
    def test_send_empty_message(self, client, auth_headers):
        """测试发送空消息"""
        response = client.post(
            "/api/v1/chat/message",
            json={"message": ""},
            headers=auth_headers
        )
        
        assert_response_error(response, 422)
    
    def test_get_conversations(self, client, auth_headers):
        """测试获取对话历史"""
        response = client.get(
            "/api/v1/chat/conversations",
            headers=auth_headers
        )
        
        data = assert_response_ok(response)
        assert isinstance(data, list)


class TestAgentsAPI:
    """Agent管理API测试"""
    
    def test_list_agents(self, client, auth_headers):
        """测试获取Agent列表"""
        response = client.get(
            "/api/v1/agents",
            headers=auth_headers
        )
        
        data = assert_response_ok(response)
        assert isinstance(data, list)
        assert len(data) > 0
        
        # 检查Agent数据结构
        agent = data[0]
        assert "id" in agent
        assert "name" in agent
        assert "description" in agent
        assert "is_active" in agent
    
    def test_create_agent(self, client, sample_agent_data, auth_headers):
        """测试创建Agent"""
        response = client.post(
            "/api/v1/agents",
            json=sample_agent_data,
            headers=auth_headers
        )
        
        data = assert_response_created(response)
        
        assert "agent_id" in data
        assert data["message"] == "Agent创建成功"
    
    def test_get_agent_details(self, client, auth_headers):
        """测试获取Agent详情"""
        # 首先创建一个Agent
        sample_data = {
            "agent_type": "retail_analysis",
            "name": "测试Agent",
            "description": "测试用Agent",
            "capabilities": ["data_analysis"]
        }
        
        create_response = client.post(
            "/api/v1/agents",
            json=sample_data,
            headers=auth_headers
        )
        create_data = assert_response_created(create_response)
        agent_id = create_data["agent_id"]
        
        # 获取Agent详情
        response = client.get(
            f"/api/v1/agents/{agent_id}",
            headers=auth_headers
        )
        
        data = assert_response_ok(response)
        
        assert data["id"] == agent_id
        assert data["name"] == sample_data["name"]
        assert data["description"] == sample_data["description"]
    
    def test_update_agent(self, client, auth_headers):
        """测试更新Agent"""
        # 首先创建一个Agent
        sample_data = {
            "agent_type": "retail_analysis",
            "name": "测试Agent",
            "description": "测试用Agent",
            "capabilities": ["data_analysis"]
        }
        
        create_response = client.post(
            "/api/v1/agents",
            json=sample_data,
            headers=auth_headers
        )
        create_data = assert_response_created(create_response)
        agent_id = create_data["agent_id"]
        
        # 更新Agent
        update_data = {
            "name": "更新后的Agent",
            "description": "更新后的描述"
        }
        
        response = client.put(
            f"/api/v1/agents/{agent_id}",
            json=update_data,
            headers=auth_headers
        )
        
        data = assert_response_ok(response)
        assert data["message"] == "Agent更新成功"
    
    def test_delete_agent(self, client, auth_headers):
        """测试删除Agent"""
        # 首先创建一个Agent
        sample_data = {
            "agent_type": "retail_analysis",
            "name": "测试Agent",
            "description": "测试用Agent",
            "capabilities": ["data_analysis"]
        }
        
        create_response = client.post(
            "/api/v1/agents",
            json=sample_data,
            headers=auth_headers
        )
        create_data = assert_response_created(create_response)
        agent_id = create_data["agent_id"]
        
        # 删除Agent
        response = client.delete(
            f"/api/v1/agents/{agent_id}",
            headers=auth_headers
        )
        
        data = assert_response_ok(response)
        assert data["message"] == "Agent删除成功"


class TestDocumentsAPI:
    """文档管理API测试"""
    
    def test_upload_document(self, client, auth_headers):
        """测试文档上传"""
        # 创建测试文件
        test_content = "这是一个测试文档内容"
        files = {
            "file": ("test.txt", test_content, "text/plain")
        }
        
        response = client.post(
            "/api/v1/documents/upload",
            files=files,
            headers=auth_headers
        )
        
        data = assert_response_created(response)
        
        assert "document_id" in data
        assert "filename" in data
        assert "message" in data
    
    def test_list_documents(self, client, auth_headers):
        """测试获取文档列表"""
        response = client.get(
            "/api/v1/documents",
            headers=auth_headers
        )
        
        data = assert_response_ok(response)
        assert isinstance(data, list)
    
    def test_search_documents(self, client, auth_headers):
        """测试文档搜索"""
        search_data = {
            "query": "销售数据",
            "limit": 10
        }
        
        response = client.post(
            "/api/v1/documents/search",
            json=search_data,
            headers=auth_headers
        )
        
        data = assert_response_ok(response)
        
        assert "results" in data
        assert "total" in data
        assert isinstance(data["results"], list)


class TestAnalyticsAPI:
    """数据分析API测试"""
    
    def test_dashboard_stats(self, client, auth_headers):
        """测试仪表盘统计"""
        response = client.get(
            "/api/v1/analytics/dashboard-stats",
            headers=auth_headers
        )
        
        data = assert_response_ok(response)
        
        assert "totalAgents" in data
        assert "activeAgents" in data
        assert "totalMessages" in data
        assert "successRate" in data
    
    def test_performance_metrics(self, client, auth_headers):
        """测试性能指标"""
        response = client.get(
            "/api/v1/analytics/performance",
            headers=auth_headers
        )
        
        data = assert_response_ok(response)
        
        assert "responseTime" in data
        assert "successRate" in data
        assert "throughput" in data


class TestMCPAPI:
    """MCP协议API测试"""
    
    def test_list_mcp_servers(self, client, auth_headers):
        """测试获取MCP服务器列表"""
        response = client.get(
            "/api/v1/mcp/servers",
            headers=auth_headers
        )
        
        data = assert_response_ok(response)
        assert isinstance(data, list)
    
    def test_register_mcp_server(self, client, auth_headers):
        """测试注册MCP服务器"""
        server_data = {
            "name": "test_server",
            "endpoint": "http://test-server:8000",
            "capabilities": ["resources", "tools"]
        }
        
        response = client.post(
            "/api/v1/mcp/servers/register",
            json=server_data,
            headers=auth_headers
        )
        
        data = assert_response_ok(response)
        
        assert "message" in data
        assert "server_name" in data
        assert data["server_name"] == "test_server"
    
    def test_list_mcp_tools(self, client, auth_headers):
        """测试获取MCP工具列表"""
        response = client.get(
            "/api/v1/mcp/tools",
            headers=auth_headers
        )
        
        data = assert_response_ok(response)
        assert isinstance(data, list)
    
    def test_call_mcp_tool(self, client, auth_headers):
        """测试调用MCP工具"""
        tool_data = {
            "server_name": "walmart_data_server",
            "tool_name": "analyze_sales_data",
            "arguments": {
                "date_range": "2024-Q4",
                "category": "electronics"
            }
        }
        
        response = client.post(
            "/api/v1/mcp/tools/call",
            json=tool_data,
            headers=auth_headers
        )
        
        data = assert_response_ok(response)
        
        assert "result" in data
        assert "status" in data


class TestWebSocketAPI:
    """WebSocket API测试"""
    
    def test_websocket_connection_stats(self, client, auth_headers):
        """测试WebSocket连接统计"""
        response = client.get(
            "/api/v1/ws/connections/stats",
            headers=auth_headers
        )
        
        data = assert_response_ok(response)
        
        assert "active_connections" in data
        assert "active_users" in data
        assert "users" in data
    
    def test_broadcast_message(self, client, auth_headers):
        """测试广播消息"""
        message_data = {
            "type": "announcement",
            "title": "系统通知",
            "content": "测试广播消息"
        }
        
        response = client.post(
            "/api/v1/ws/broadcast",
            json=message_data,
            headers=auth_headers
        )
        
        data = assert_response_ok(response)
        
        assert "message" in data
        assert "recipients" in data


class TestErrorHandling:
    """错误处理测试"""
    
    def test_404_error(self, client):
        """测试404错误"""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """测试方法不允许错误"""
        response = client.put("/api/v1/health")
        assert response.status_code == 405
    
    def test_validation_error(self, client, auth_headers):
        """测试数据验证错误"""
        invalid_data = {
            "message": ""  # 空消息应该失败
        }
        
        response = client.post(
            "/api/v1/chat/message",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422
