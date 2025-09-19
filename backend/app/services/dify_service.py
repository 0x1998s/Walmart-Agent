# 🛒 沃尔玛AI Agent平台 - Dify集成服务
# Walmart AI Agent Platform - Dify Integration Service

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, AsyncGenerator
from uuid import uuid4

import httpx
from pydantic import BaseModel

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class DifyWorkflow(BaseModel):
    """Dify工作流模型"""
    id: str
    name: str
    description: Optional[str] = None
    status: str = "active"
    created_at: str
    updated_at: str


class DifyApp(BaseModel):
    """Dify应用模型"""
    id: str
    name: str
    mode: str  # "chat", "completion", "agent"
    enable_site: bool
    enable_api: bool
    api_rpm_limit: int
    api_rph_limit: int


class DifyConversation(BaseModel):
    """Dify对话模型"""
    id: str
    name: str
    inputs: Dict[str, Any]
    status: str
    introduction: str
    created_at: str


class DifyService:
    """Dify平台集成服务"""
    
    def __init__(self):
        self.base_url = settings.DIFY_API_URL
        self.api_key = settings.DIFY_API_KEY
        self.app_token = settings.DIFY_APP_TOKEN
        self.client: Optional[httpx.AsyncClient] = None
    
    async def initialize(self):
        """初始化Dify客户端"""
        if not self.api_key:
            logger.warning("⚠️ Dify API密钥未设置，将使用模拟模式")
            return
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=60.0
        )
        
        # 测试连接
        try:
            await self._health_check()
            logger.info("✅ Dify服务初始化完成")
        except Exception as e:
            logger.error(f"❌ Dify服务初始化失败: {e}")
            raise
    
    async def _health_check(self) -> bool:
        """健康检查"""
        if not self.client:
            return False
        
        try:
            response = await self.client.get("/v1/apps")
            return response.status_code == 200
        except Exception:
            return False
    
    async def create_chat_message(
        self,
        query: str,
        inputs: Optional[Dict[str, Any]] = None,
        user: str = "walmart-user",
        conversation_id: Optional[str] = None,
        response_mode: str = "blocking",
        files: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """创建聊天消息"""
        if not self.client:
            return await self._mock_chat_response(query)
        
        try:
            payload = {
                "inputs": inputs or {},
                "query": query,
                "response_mode": response_mode,
                "user": user,
                "files": files or []
            }
            
            if conversation_id:
                payload["conversation_id"] = conversation_id
            
            response = await self.client.post(
                f"/v1/chat-messages",
                json=payload,
                headers={"Authorization": f"Bearer {self.app_token}"}
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Dify聊天消息创建成功: {data.get('id')}")
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Dify聊天消息创建失败: {e}")
            return await self._mock_chat_response(query)
    
    async def stream_chat_message(
        self,
        query: str,
        inputs: Optional[Dict[str, Any]] = None,
        user: str = "walmart-user",
        conversation_id: Optional[str] = None,
        files: Optional[List[Dict[str, Any]]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """流式聊天消息"""
        if not self.client:
            async for chunk in self._mock_stream_response(query):
                yield chunk
            return
        
        try:
            payload = {
                "inputs": inputs or {},
                "query": query,
                "response_mode": "streaming",
                "user": user,
                "files": files or []
            }
            
            if conversation_id:
                payload["conversation_id"] = conversation_id
            
            async with self.client.stream(
                "POST",
                "/v1/chat-messages",
                json=payload,
                headers={"Authorization": f"Bearer {self.app_token}"}
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        
                        if data_str.strip() == "[DONE]":
                            break
                        
                        try:
                            data = json.loads(data_str)
                            yield data
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            logger.error(f"❌ Dify流式聊天失败: {e}")
            async for chunk in self._mock_stream_response(query):
                yield chunk
    
    async def get_conversations(
        self,
        user: str = "walmart-user",
        last_id: Optional[str] = None,
        limit: int = 20
    ) -> List[DifyConversation]:
        """获取对话列表"""
        if not self.client:
            return await self._mock_conversations()
        
        try:
            params = {"user": user, "limit": limit}
            if last_id:
                params["last_id"] = last_id
            
            response = await self.client.get(
                "/v1/conversations",
                params=params,
                headers={"Authorization": f"Bearer {self.app_token}"}
            )
            response.raise_for_status()
            
            data = response.json()
            conversations = [
                DifyConversation(**conv) for conv in data.get("data", [])
            ]
            
            logger.info(f"✅ 获取到 {len(conversations)} 个对话")
            return conversations
            
        except Exception as e:
            logger.error(f"❌ 获取对话列表失败: {e}")
            return await self._mock_conversations()
    
    async def get_conversation_messages(
        self,
        conversation_id: str,
        user: str = "walmart-user",
        first_id: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """获取对话消息"""
        if not self.client:
            return await self._mock_messages()
        
        try:
            params = {"user": user, "limit": limit}
            if first_id:
                params["first_id"] = first_id
            
            response = await self.client.get(
                f"/v1/conversations/{conversation_id}/messages",
                params=params,
                headers={"Authorization": f"Bearer {self.app_token}"}
            )
            response.raise_for_status()
            
            data = response.json()
            messages = data.get("data", [])
            
            logger.info(f"✅ 获取到 {len(messages)} 条消息")
            return messages
            
        except Exception as e:
            logger.error(f"❌ 获取对话消息失败: {e}")
            return await self._mock_messages()
    
    async def rename_conversation(
        self,
        conversation_id: str,
        name: str,
        user: str = "walmart-user"
    ) -> bool:
        """重命名对话"""
        if not self.client:
            return True
        
        try:
            payload = {"name": name, "user": user}
            
            response = await self.client.POST(
                f"/v1/conversations/{conversation_id}/name",
                json=payload,
                headers={"Authorization": f"Bearer {self.app_token}"}
            )
            response.raise_for_status()
            
            logger.info(f"✅ 对话重命名成功: {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 对话重命名失败: {e}")
            return False
    
    async def get_app_info(self) -> Optional[DifyApp]:
        """获取应用信息"""
        if not self.client:
            return await self._mock_app_info()
        
        try:
            response = await self.client.get(
                "/v1/parameters",
                headers={"Authorization": f"Bearer {self.app_token}"}
            )
            response.raise_for_status()
            
            data = response.json()
            app_info = DifyApp(**data)
            
            logger.info(f"✅ 获取应用信息成功: {app_info.name}")
            return app_info
            
        except Exception as e:
            logger.error(f"❌ 获取应用信息失败: {e}")
            return await self._mock_app_info()
    
    async def create_workflow(
        self,
        name: str,
        description: str,
        graph: Dict[str, Any],
        features: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """创建工作流"""
        if not self.client:
            return str(uuid4())
        
        try:
            payload = {
                "name": name,
                "description": description,
                "graph": graph,
                "features": features or {}
            }
            
            response = await self.client.post(
                "/v1/workflows",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            workflow_id = data.get("id")
            
            logger.info(f"✅ 工作流创建成功: {workflow_id}")
            return workflow_id
            
        except Exception as e:
            logger.error(f"❌ 工作流创建失败: {e}")
            return None
    
    async def run_workflow(
        self,
        workflow_id: str,
        inputs: Dict[str, Any],
        user: str = "walmart-user"
    ) -> Dict[str, Any]:
        """运行工作流"""
        if not self.client:
            return await self._mock_workflow_result(inputs)
        
        try:
            payload = {
                "inputs": inputs,
                "user": user,
                "response_mode": "blocking"
            }
            
            response = await self.client.post(
                f"/v1/workflows/{workflow_id}/run",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ 工作流运行完成: {workflow_id}")
            
            return data
            
        except Exception as e:
            logger.error(f"❌ 工作流运行失败: {e}")
            return await self._mock_workflow_result(inputs)
    
    async def get_workflow_logs(
        self,
        workflow_id: str,
        keyword: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """获取工作流日志"""
        if not self.client:
            return []
        
        try:
            params = {"page": page, "limit": limit}
            if keyword:
                params["keyword"] = keyword
            if status:
                params["status"] = status
            
            response = await self.client.get(
                f"/v1/workflows/{workflow_id}/logs",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            logs = data.get("data", [])
            
            logger.info(f"✅ 获取到 {len(logs)} 条工作流日志")
            return logs
            
        except Exception as e:
            logger.error(f"❌ 获取工作流日志失败: {e}")
            return []
    
    # ===== 模拟方法（用于测试和演示） =====
    
    async def _mock_chat_response(self, query: str) -> Dict[str, Any]:
        """模拟聊天响应"""
        await asyncio.sleep(1)  # 模拟延迟
        
        return {
            "id": str(uuid4()),
            "object": "chat.completion",
            "created": 1677652288,
            "answer": f"这是对 '{query}' 的模拟回复。在实际环境中，这将由Dify平台处理。",
            "metadata": {
                "usage": {
                    "prompt_tokens": len(query.split()),
                    "completion_tokens": 20,
                    "total_tokens": len(query.split()) + 20
                }
            },
            "created_at": "2024-01-01T00:00:00Z"
        }
    
    async def _mock_stream_response(self, query: str) -> AsyncGenerator[Dict[str, Any], None]:
        """模拟流式响应"""
        response_text = f"这是对 '{query}' 的模拟流式回复。"
        
        for i, char in enumerate(response_text):
            await asyncio.sleep(0.05)
            yield {
                "event": "message",
                "message_id": str(uuid4()),
                "conversation_id": str(uuid4()),
                "answer": char,
                "created_at": "2024-01-01T00:00:00Z"
            }
        
        yield {
            "event": "message_end",
            "message_id": str(uuid4()),
            "conversation_id": str(uuid4()),
            "metadata": {
                "usage": {
                    "prompt_tokens": len(query.split()),
                    "completion_tokens": len(response_text),
                    "total_tokens": len(query.split()) + len(response_text)
                }
            }
        }
    
    async def _mock_conversations(self) -> List[DifyConversation]:
        """模拟对话列表"""
        return [
            DifyConversation(
                id=str(uuid4()),
                name="沃尔玛销售分析对话",
                inputs={},
                status="normal",
                introduction="分析沃尔玛销售数据",
                created_at="2024-01-01T00:00:00Z"
            ),
            DifyConversation(
                id=str(uuid4()),
                name="库存管理咨询",
                inputs={},
                status="normal", 
                introduction="库存优化建议",
                created_at="2024-01-01T00:00:00Z"
            )
        ]
    
    async def _mock_messages(self) -> List[Dict[str, Any]]:
        """模拟消息列表"""
        return [
            {
                "id": str(uuid4()),
                "conversation_id": str(uuid4()),
                "inputs": {},
                "query": "请分析Q4销售数据",
                "answer": "根据Q4数据分析，销售额同比增长15%...",
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
    
    async def _mock_app_info(self) -> DifyApp:
        """模拟应用信息"""
        return DifyApp(
            id=str(uuid4()),
            name="沃尔玛AI助手",
            mode="chat",
            enable_site=True,
            enable_api=True,
            api_rpm_limit=1000,
            api_rph_limit=60000
        )
    
    async def _mock_workflow_result(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """模拟工作流结果"""
        await asyncio.sleep(2)  # 模拟处理时间
        
        return {
            "id": str(uuid4()),
            "workflow_id": str(uuid4()),
            "status": "succeeded",
            "outputs": {
                "result": f"工作流处理完成，输入参数: {inputs}",
                "processed_at": "2024-01-01T00:00:00Z"
            },
            "created_at": "2024-01-01T00:00:00Z",
            "finished_at": "2024-01-01T00:00:02Z"
        }
