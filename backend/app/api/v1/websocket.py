# 🛒 沃尔玛AI Agent平台 - WebSocket API
# Walmart AI Agent Platform - WebSocket API

import asyncio
import json
import logging
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from pydantic import BaseModel

from app.agents.orchestrator import AgentOrchestrator
from app.core.dependencies import get_agent_orchestrator
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[str, List[str]] = {}  # user_id -> [connection_ids]
        self.connection_users: Dict[str, str] = {}  # connection_id -> user_id
        
    async def connect(self, websocket: WebSocket, connection_id: str, user_id: str):
        """接受WebSocket连接"""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        self.connection_users[connection_id] = user_id
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(connection_id)
        
        logger.info(f"✅ WebSocket连接建立: {connection_id} (用户: {user_id})")
    
    def disconnect(self, connection_id: str):
        """断开WebSocket连接"""
        if connection_id in self.active_connections:
            user_id = self.connection_users.get(connection_id)
            
            del self.active_connections[connection_id]
            del self.connection_users[connection_id]
            
            if user_id and user_id in self.user_connections:
                self.user_connections[user_id].remove(connection_id)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
            
            logger.info(f"❌ WebSocket连接断开: {connection_id} (用户: {user_id})")
    
    async def send_personal_message(self, message: dict, connection_id: str):
        """发送个人消息"""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_text(json.dumps(message, ensure_ascii=False))
            except Exception as e:
                logger.error(f"❌ 发送消息失败: {e}")
                self.disconnect(connection_id)
    
    async def send_user_message(self, message: dict, user_id: str):
        """发送用户消息到所有连接"""
        if user_id in self.user_connections:
            disconnected = []
            for connection_id in self.user_connections[user_id]:
                try:
                    await self.send_personal_message(message, connection_id)
                except Exception:
                    disconnected.append(connection_id)
            
            # 清理断开的连接
            for connection_id in disconnected:
                self.disconnect(connection_id)
    
    async def broadcast(self, message: dict):
        """广播消息到所有连接"""
        disconnected = []
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message, ensure_ascii=False))
            except Exception:
                disconnected.append(connection_id)
        
        # 清理断开的连接
        for connection_id in disconnected:
            self.disconnect(connection_id)
    
    def get_user_connections(self, user_id: str) -> List[str]:
        """获取用户的所有连接"""
        return self.user_connections.get(user_id, [])
    
    def get_active_users(self) -> List[str]:
        """获取所有活跃用户"""
        return list(self.user_connections.keys())
    
    def get_connection_count(self) -> int:
        """获取连接数量"""
        return len(self.active_connections)


# 全局连接管理器
manager = ConnectionManager()


class WSMessage(BaseModel):
    """WebSocket消息模型"""
    type: str  # message, status, notification, error
    data: dict
    timestamp: Optional[str] = None
    user_id: Optional[str] = None
    connection_id: Optional[str] = None


@router.websocket("/chat/{user_id}")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    user_id: str,
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator)
):
    """WebSocket聊天端点"""
    connection_id = str(uuid4())
    
    try:
        await manager.connect(websocket, connection_id, user_id)
        
        # 发送连接确认
        await manager.send_personal_message({
            "type": "connection",
            "data": {
                "status": "connected",
                "connection_id": connection_id,
                "message": "WebSocket连接已建立"
            },
            "timestamp": asyncio.get_event_loop().time()
        }, connection_id)
        
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # 处理不同类型的消息
            await handle_websocket_message(
                message_data, connection_id, user_id, orchestrator
            )
            
    except WebSocketDisconnect:
        manager.disconnect(connection_id)
        logger.info(f"🔌 WebSocket连接正常断开: {connection_id}")
        
    except Exception as e:
        logger.error(f"❌ WebSocket连接异常: {e}")
        manager.disconnect(connection_id)


async def handle_websocket_message(
    message_data: dict,
    connection_id: str,
    user_id: str,
    orchestrator: AgentOrchestrator
):
    """处理WebSocket消息"""
    try:
        message_type = message_data.get("type", "message")
        data = message_data.get("data", {})
        
        if message_type == "chat":
            await handle_chat_message(data, connection_id, user_id, orchestrator)
        elif message_type == "ping":
            await handle_ping_message(connection_id)
        elif message_type == "status":
            await handle_status_request(connection_id, orchestrator)
        elif message_type == "task":
            await handle_task_request(data, connection_id, user_id, orchestrator)
        else:
            await manager.send_personal_message({
                "type": "error",
                "data": {
                    "message": f"未知消息类型: {message_type}"
                }
            }, connection_id)
            
    except Exception as e:
        logger.error(f"❌ 处理WebSocket消息失败: {e}")
        await manager.send_personal_message({
            "type": "error",
            "data": {
                "message": f"消息处理失败: {str(e)}"
            }
        }, connection_id)


async def handle_chat_message(
    data: dict,
    connection_id: str,
    user_id: str,
    orchestrator: AgentOrchestrator
):
    """处理聊天消息"""
    message = data.get("message", "")
    conversation_id = data.get("conversation_id")
    preferred_agent_id = data.get("preferred_agent_id")
    
    if not message:
        await manager.send_personal_message({
            "type": "error",
            "data": {"message": "消息内容不能为空"}
        }, connection_id)
        return
    
    try:
        # 发送处理中状态
        await manager.send_personal_message({
            "type": "status",
            "data": {
                "status": "processing",
                "message": "正在处理您的消息..."
            }
        }, connection_id)
        
        # 路由消息到Agent
        response = await orchestrator.route_message(
            message=message,
            user_id=user_id,
            conversation_id=conversation_id,
            preferred_agent_id=preferred_agent_id
        )
        
        # 发送回复
        await manager.send_personal_message({
            "type": "message",
            "data": {
                "message": response.content,
                "agent_id": response.agent_id,
                "agent_name": orchestrator.agents.get(response.agent_id, {}).name if response.agent_id else None,
                "conversation_id": response.conversation_id,
                "metadata": response.metadata
            },
            "timestamp": response.timestamp.isoformat()
        }, connection_id)
        
    except Exception as e:
        await manager.send_personal_message({
            "type": "error",
            "data": {
                "message": f"处理聊天消息失败: {str(e)}"
            }
        }, connection_id)


async def handle_ping_message(connection_id: str):
    """处理ping消息"""
    await manager.send_personal_message({
        "type": "pong",
        "data": {
            "timestamp": asyncio.get_event_loop().time()
        }
    }, connection_id)


async def handle_status_request(connection_id: str, orchestrator: AgentOrchestrator):
    """处理状态请求"""
    try:
        stats = orchestrator.get_orchestrator_stats()
        await manager.send_personal_message({
            "type": "status",
            "data": {
                "system_status": "healthy",
                "stats": stats,
                "connection_info": {
                    "connection_id": connection_id,
                    "active_connections": manager.get_connection_count(),
                    "active_users": len(manager.get_active_users())
                }
            }
        }, connection_id)
        
    except Exception as e:
        await manager.send_personal_message({
            "type": "error",
            "data": {
                "message": f"获取状态失败: {str(e)}"
            }
        }, connection_id)


async def handle_task_request(
    data: dict,
    connection_id: str,
    user_id: str,
    orchestrator: AgentOrchestrator
):
    """处理任务请求"""
    try:
        from app.agents.base_agent import AgentTask
        
        task = AgentTask(
            name=data.get("name", "WebSocket任务"),
            description=data.get("description", ""),
            input_data=data.get("input_data", {}),
            priority=data.get("priority", 1),
            metadata=data.get("metadata", {})
        )
        
        # 发送任务开始通知
        await manager.send_personal_message({
            "type": "task_started",
            "data": {
                "task_id": task.id,
                "task_name": task.name,
                "status": "started"
            }
        }, connection_id)
        
        # 执行任务
        completed_task = await orchestrator.execute_task(
            task=task,
            user_id=user_id,
            preferred_agent_id=data.get("preferred_agent_id")
        )
        
        # 发送任务完成通知
        await manager.send_personal_message({
            "type": "task_completed",
            "data": {
                "task_id": completed_task.id,
                "task_name": completed_task.name,
                "status": completed_task.status,
                "output_data": completed_task.output_data,
                "error_message": completed_task.error_message
            }
        }, connection_id)
        
    except Exception as e:
        await manager.send_personal_message({
            "type": "task_error",
            "data": {
                "message": f"任务执行失败: {str(e)}"
            }
        }, connection_id)


@router.get("/connections/stats")
async def get_connection_stats():
    """获取连接统计信息"""
    return {
        "active_connections": manager.get_connection_count(),
        "active_users": len(manager.get_active_users()),
        "users": manager.get_active_users()
    }


@router.post("/broadcast")
async def broadcast_message(message: dict):
    """广播消息到所有连接"""
    try:
        await manager.broadcast({
            "type": "broadcast",
            "data": message,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        return {
            "message": "广播消息已发送",
            "recipients": manager.get_connection_count()
        }
        
    except Exception as e:
        logger.error(f"❌ 广播消息失败: {e}")
        raise HTTPException(status_code=500, detail=f"广播失败: {str(e)}")


@router.post("/users/{user_id}/notify")
async def notify_user(user_id: str, message: dict):
    """通知特定用户"""
    try:
        connections = manager.get_user_connections(user_id)
        if not connections:
            raise HTTPException(status_code=404, detail="用户未在线")
        
        await manager.send_user_message({
            "type": "notification",
            "data": message,
            "timestamp": asyncio.get_event_loop().time()
        }, user_id)
        
        return {
            "message": f"通知已发送给用户 {user_id}",
            "connections": len(connections)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 用户通知失败: {e}")
        raise HTTPException(status_code=500, detail=f"通知失败: {str(e)}")
