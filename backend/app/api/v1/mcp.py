# 🛒 沃尔玛AI Agent平台 - MCP协议API
# Walmart AI Agent Platform - MCP Protocol API

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field

from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.mcp_service import MCPService, MCPServer, MCPTool, MCPResource

router = APIRouter()
logger = logging.getLogger(__name__)

# 全局MCP服务实例
_mcp_service: Optional[MCPService] = None


async def get_mcp_service() -> MCPService:
    """获取MCP服务实例"""
    global _mcp_service
    if _mcp_service is None:
        _mcp_service = MCPService()
        await _mcp_service.initialize()
    return _mcp_service


class MCPServerRequest(BaseModel):
    """MCP服务器注册请求"""
    name: str = Field(..., description="服务器名称")
    endpoint: str = Field(..., description="服务器端点")
    auth_token: Optional[str] = Field(None, description="认证令牌")
    capabilities: List[str] = Field(default_factory=list, description="服务器能力")


class MCPToolCallRequest(BaseModel):
    """MCP工具调用请求"""
    server_name: str = Field(..., description="服务器名称")
    tool_name: str = Field(..., description="工具名称")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="工具参数")
    session_id: Optional[str] = Field(None, description="会话ID")


class MCPPromptRequest(BaseModel):
    """MCP提示词模板请求"""
    server_name: str = Field(..., description="服务器名称")
    template_name: str = Field(..., description="模板名称")
    template: str = Field(..., description="模板内容")
    variables: List[str] = Field(default_factory=list, description="变量列表")


@router.get("/servers", response_model=List[Dict[str, Any]])
async def list_mcp_servers(
    mcp_service: MCPService = Depends(get_mcp_service),
    current_user: User = Depends(get_current_user)
):
    """获取已注册的MCP服务器列表"""
    try:
        servers = []
        for name, server in mcp_service.servers.items():
            servers.append({
                "name": server.name,
                "endpoint": server.endpoint,
                "capabilities": server.capabilities,
                "tools_count": len(server.tools),
                "resources_count": len(server.resources),
                "status": "connected"  # 简化状态
            })
        
        return servers
        
    except Exception as e:
        logger.error(f"❌ 获取MCP服务器列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取服务器列表失败: {str(e)}")


@router.post("/servers/register")
async def register_mcp_server(
    request: MCPServerRequest,
    mcp_service: MCPService = Depends(get_mcp_service),
    current_user: User = Depends(get_current_user)
):
    """注册MCP服务器"""
    try:
        server = MCPServer(
            name=request.name,
            endpoint=request.endpoint,
            auth_token=request.auth_token,
            capabilities=request.capabilities
        )
        
        success = await mcp_service.register_server(server)
        
        if success:
            return {
                "message": f"MCP服务器 {request.name} 注册成功",
                "server_name": request.name,
                "status": "registered"
            }
        else:
            raise HTTPException(status_code=400, detail="服务器注册失败")
            
    except Exception as e:
        logger.error(f"❌ MCP服务器注册失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务器注册失败: {str(e)}")


@router.get("/resources", response_model=List[MCPResource])
async def list_mcp_resources(
    server_name: Optional[str] = None,
    mcp_service: MCPService = Depends(get_mcp_service),
    current_user: User = Depends(get_current_user)
):
    """列出MCP资源"""
    try:
        resources = await mcp_service.list_resources(server_name)
        return resources
        
    except Exception as e:
        logger.error(f"❌ 获取MCP资源失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取资源失败: {str(e)}")


@router.get("/resources/{server_name}/{resource_uri:path}")
async def get_mcp_resource(
    server_name: str,
    resource_uri: str,
    mcp_service: MCPService = Depends(get_mcp_service),
    current_user: User = Depends(get_current_user)
):
    """获取特定MCP资源"""
    try:
        resource_content = await mcp_service.get_resource(server_name, resource_uri)
        
        if resource_content is None:
            raise HTTPException(status_code=404, detail="资源不存在")
        
        return resource_content
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取MCP资源失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取资源失败: {str(e)}")


@router.get("/tools", response_model=List[MCPTool])
async def list_mcp_tools(
    server_name: Optional[str] = None,
    mcp_service: MCPService = Depends(get_mcp_service),
    current_user: User = Depends(get_current_user)
):
    """列出MCP工具"""
    try:
        tools = await mcp_service.list_tools(server_name)
        return tools
        
    except Exception as e:
        logger.error(f"❌ 获取MCP工具失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取工具失败: {str(e)}")


@router.post("/tools/call")
async def call_mcp_tool(
    request: MCPToolCallRequest,
    background_tasks: BackgroundTasks,
    mcp_service: MCPService = Depends(get_mcp_service),
    current_user: User = Depends(get_current_user)
):
    """调用MCP工具"""
    try:
        result = await mcp_service.call_tool(
            server_name=request.server_name,
            tool_name=request.tool_name,
            arguments=request.arguments,
            session_id=request.session_id
        )
        
        # 记录工具调用日志
        background_tasks.add_task(
            log_tool_usage,
            request.tool_name,
            request.server_name,
            str(current_user.id),
            result.get("status", "unknown")
        )
        
        return result
        
    except Exception as e:
        logger.error(f"❌ MCP工具调用失败: {e}")
        raise HTTPException(status_code=500, detail=f"工具调用失败: {str(e)}")


@router.post("/prompts")
async def create_mcp_prompt_template(
    request: MCPPromptRequest,
    mcp_service: MCPService = Depends(get_mcp_service),
    current_user: User = Depends(get_current_user)
):
    """创建MCP提示词模板"""
    try:
        success = await mcp_service.create_prompt_template(
            server_name=request.server_name,
            template_name=request.template_name,
            template=request.template,
            variables=request.variables
        )
        
        if success:
            return {
                "message": f"提示词模板 {request.template_name} 创建成功",
                "template_name": request.template_name,
                "server_name": request.server_name
            }
        else:
            raise HTTPException(status_code=400, detail="模板创建失败")
            
    except Exception as e:
        logger.error(f"❌ 创建MCP提示词模板失败: {e}")
        raise HTTPException(status_code=500, detail=f"模板创建失败: {str(e)}")


@router.get("/servers/{server_name}/capabilities")
async def get_server_capabilities(
    server_name: str,
    mcp_service: MCPService = Depends(get_mcp_service),
    current_user: User = Depends(get_current_user)
):
    """获取服务器能力"""
    try:
        capabilities = await mcp_service.get_server_capabilities(server_name)
        
        return {
            "server_name": server_name,
            "capabilities": capabilities,
            "total": len(capabilities)
        }
        
    except Exception as e:
        logger.error(f"❌ 获取服务器能力失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取能力失败: {str(e)}")


@router.get("/health")
async def mcp_health_check(
    mcp_service: MCPService = Depends(get_mcp_service),
    current_user: User = Depends(get_current_user)
):
    """MCP服务健康检查"""
    try:
        server_count = len(mcp_service.servers)
        active_sessions = len(mcp_service.active_sessions)
        
        return {
            "status": "healthy",
            "mcp_version": "1.0.0",
            "servers_count": server_count,
            "active_sessions": active_sessions,
            "features": [
                "resource_management",
                "tool_calling",
                "prompt_templates",
                "session_management"
            ]
        }
        
    except Exception as e:
        logger.error(f"❌ MCP健康检查失败: {e}")
        raise HTTPException(status_code=500, detail=f"健康检查失败: {str(e)}")


@router.delete("/servers/{server_name}")
async def unregister_mcp_server(
    server_name: str,
    mcp_service: MCPService = Depends(get_mcp_service),
    current_user: User = Depends(get_current_user)
):
    """注销MCP服务器"""
    try:
        if server_name not in mcp_service.servers:
            raise HTTPException(status_code=404, detail="服务器不存在")
        
        # 关闭客户端连接
        if server_name in mcp_service.clients:
            await mcp_service.clients[server_name].aclose()
            del mcp_service.clients[server_name]
        
        # 删除服务器记录
        del mcp_service.servers[server_name]
        
        # 清理相关会话
        sessions_to_remove = [
            session_id for session_id, srv_name in mcp_service.active_sessions.items()
            if srv_name == server_name
        ]
        for session_id in sessions_to_remove:
            del mcp_service.active_sessions[session_id]
        
        return {
            "message": f"MCP服务器 {server_name} 已注销",
            "server_name": server_name,
            "status": "unregistered"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 注销MCP服务器失败: {e}")
        raise HTTPException(status_code=500, detail=f"注销服务器失败: {str(e)}")


async def log_tool_usage(
    tool_name: str,
    server_name: str,
    user_id: str,
    status: str
):
    """记录工具使用日志（后台任务）"""
    try:
        logger.info(
            f"📊 MCP工具使用记录: "
            f"用户={user_id}, 服务器={server_name}, "
            f"工具={tool_name}, 状态={status}"
        )
        
        # 这里可以将使用记录保存到数据库或监控系统
        
    except Exception as e:
        logger.error(f"❌ 记录工具使用失败: {e}")
