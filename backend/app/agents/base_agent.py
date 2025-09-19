# 🛒 沃尔玛AI Agent平台 - 基础Agent类
# Walmart AI Agent Platform - Base Agent Class

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from pydantic import BaseModel, Field

from app.services.llm_service import LLMService, ModelProvider
from app.services.vector_service import VectorService
from app.services.data_service import DataService

logger = logging.getLogger(__name__)


class AgentCapability(str, Enum):
    """Agent能力枚举"""
    DATA_ANALYSIS = "data_analysis"          # 数据分析
    NATURAL_LANGUAGE = "natural_language"   # 自然语言处理
    DOCUMENT_SEARCH = "document_search"      # 文档搜索
    WORKFLOW_EXECUTION = "workflow_execution" # 工作流执行
    REAL_TIME_PROCESSING = "real_time_processing"  # 实时处理
    MULTI_MODAL = "multi_modal"             # 多模态处理
    REASONING = "reasoning"                  # 推理能力
    PLANNING = "planning"                    # 规划能力


class AgentMessage(BaseModel):
    """Agent消息模型"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    role: str  # "user", "assistant", "system", "tool"
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    agent_id: Optional[str] = None
    conversation_id: Optional[str] = None


class AgentTask(BaseModel):
    """Agent任务模型"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Dict[str, Any] = Field(default_factory=dict)
    status: str = "pending"  # pending, running, completed, failed
    priority: int = 1  # 1-10, 10为最高优先级
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    agent_id: Optional[str] = None


class AgentContext(BaseModel):
    """Agent上下文"""
    conversation_id: str
    user_id: str
    session_data: Dict[str, Any] = Field(default_factory=dict)
    conversation_history: List[AgentMessage] = Field(default_factory=list)
    current_task: Optional[AgentTask] = None
    capabilities_used: List[AgentCapability] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseAgent(ABC):
    """基础Agent类 - 所有Agent的父类"""
    
    def __init__(
        self,
        name: str,
        description: str,
        capabilities: List[AgentCapability],
        llm_service: Optional[LLMService] = None,
        vector_service: Optional[VectorService] = None,
        data_service: Optional[DataService] = None,
        preferred_model: ModelProvider = ModelProvider.OPENAI
    ):
        self.id = str(uuid4())
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.llm_service = llm_service
        self.vector_service = vector_service
        self.data_service = data_service
        self.preferred_model = preferred_model
        
        # Agent状态
        self.is_active = True
        self.current_tasks: Dict[str, AgentTask] = {}
        self.completed_tasks: List[AgentTask] = []
        self.error_count = 0
        self.last_activity = datetime.now()
        
        # 性能统计
        self.total_requests = 0
        self.successful_requests = 0
        self.average_response_time = 0.0
        
        logger.info(f"✅ Agent初始化完成: {self.name} ({self.id})")
    
    @abstractmethod
    async def process_message(
        self,
        message: str,
        context: AgentContext,
        **kwargs
    ) -> AgentMessage:
        """处理消息 - 子类必须实现"""
        pass
    
    @abstractmethod
    async def execute_task(
        self,
        task: AgentTask,
        context: AgentContext,
        **kwargs
    ) -> AgentTask:
        """执行任务 - 子类必须实现"""
        pass
    
    async def can_handle_message(
        self,
        message: str,
        context: AgentContext,
        **kwargs
    ) -> bool:
        """判断是否能处理该消息"""
        # 默认实现：检查关键词匹配
        keywords = self._get_relevant_keywords()
        message_lower = message.lower()
        
        return any(keyword in message_lower for keyword in keywords)
    
    async def can_execute_task(
        self,
        task: AgentTask,
        context: AgentContext,
        **kwargs
    ) -> bool:
        """判断是否能执行该任务"""
        # 检查任务是否需要当前Agent的能力
        required_capabilities = task.metadata.get("required_capabilities", [])
        
        if not required_capabilities:
            return True
        
        return any(cap in self.capabilities for cap in required_capabilities)
    
    async def generate_response(
        self,
        prompt: str,
        context: AgentContext,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """生成LLM响应"""
        if not self.llm_service:
            raise RuntimeError(f"Agent {self.name} 未配置LLM服务")
        
        # 构建消息历史
        messages = self._build_message_history(prompt, context)
        
        try:
            response = await self.llm_service.chat_completion(
                messages=messages,
                provider=self.preferred_model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return response.content
            
        except Exception as e:
            logger.error(f"❌ Agent {self.name} LLM响应生成失败: {e}")
            self.error_count += 1
            raise
    
    async def search_knowledge(
        self,
        query: str,
        collection_name: Optional[str] = None,
        n_results: int = 5,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """搜索知识库"""
        if not self.vector_service:
            logger.warning(f"Agent {self.name} 未配置向量服务")
            return []
        
        try:
            collection_name = collection_name or self._get_default_collection()
            
            results = await self.vector_service.hybrid_search(
                collection_name=collection_name,
                query=query,
                n_results=n_results,
                **kwargs
            )
            
            # 格式化结果
            formatted_results = []
            if results.get("documents") and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    formatted_results.append({
                        "content": doc,
                        "metadata": results.get("metadatas", [[{}]])[0][i],
                        "score": 1 - results.get("distances", [[1]])[0][i],  # 转换为相似度分数
                        "id": results.get("ids", [[""]])[0][i]
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Agent {self.name} 知识搜索失败: {e}")
            return []
    
    async def start_task(
        self,
        task: AgentTask,
        context: AgentContext
    ) -> AgentTask:
        """开始执行任务"""
        task.status = "running"
        task.started_at = datetime.now()
        task.agent_id = self.id
        
        self.current_tasks[task.id] = task
        self.last_activity = datetime.now()
        
        logger.info(f"🚀 Agent {self.name} 开始执行任务: {task.name}")
        
        try:
            # 执行任务
            completed_task = await self.execute_task(task, context)
            
            # 更新任务状态
            completed_task.status = "completed"
            completed_task.completed_at = datetime.now()
            
            # 移动到已完成任务列表
            self.completed_tasks.append(completed_task)
            if task.id in self.current_tasks:
                del self.current_tasks[task.id]
            
            self.successful_requests += 1
            logger.info(f"✅ Agent {self.name} 任务完成: {task.name}")
            
            return completed_task
            
        except Exception as e:
            # 处理任务失败
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = datetime.now()
            
            self.error_count += 1
            logger.error(f"❌ Agent {self.name} 任务失败: {task.name} - {e}")
            
            if task.id in self.current_tasks:
                del self.current_tasks[task.id]
            
            return task
    
    async def handle_message(
        self,
        message: str,
        context: AgentContext,
        **kwargs
    ) -> AgentMessage:
        """处理消息的完整流程"""
        start_time = datetime.now()
        self.total_requests += 1
        self.last_activity = start_time
        
        try:
            # 检查是否能处理该消息
            if not await self.can_handle_message(message, context, **kwargs):
                return AgentMessage(
                    role="assistant",
                    content=f"抱歉，我无法处理这类请求。我是 {self.name}，专门处理 {self.description}。",
                    agent_id=self.id,
                    conversation_id=context.conversation_id,
                    metadata={"error": "unsupported_request"}
                )
            
            # 处理消息
            response = await self.process_message(message, context, **kwargs)
            response.agent_id = self.id
            response.conversation_id = context.conversation_id
            
            # 更新统计信息
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            self._update_performance_stats(response_time)
            
            logger.info(f"✅ Agent {self.name} 消息处理完成，耗时: {response_time:.2f}s")
            
            return response
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"❌ Agent {self.name} 消息处理失败: {e}")
            
            return AgentMessage(
                role="assistant",
                content=f"处理请求时发生错误，请稍后重试。错误信息: {str(e)}",
                agent_id=self.id,
                conversation_id=context.conversation_id,
                metadata={"error": str(e)}
            )
    
    def _build_message_history(
        self,
        current_prompt: str,
        context: AgentContext
    ) -> List[Dict[str, str]]:
        """构建消息历史"""
        messages = [
            {
                "role": "system",
                "content": self._get_system_prompt()
            }
        ]
        
        # 添加历史对话（限制数量避免超出token限制）
        recent_history = context.conversation_history[-10:]  # 最近10条消息
        
        for msg in recent_history:
            if msg.role in ["user", "assistant"]:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # 添加当前消息
        messages.append({
            "role": "user",
            "content": current_prompt
        })
        
        return messages
    
    def _update_performance_stats(self, response_time: float):
        """更新性能统计"""
        if self.successful_requests == 1:
            self.average_response_time = response_time
        else:
            # 计算移动平均
            self.average_response_time = (
                (self.average_response_time * (self.successful_requests - 1) + response_time) 
                / self.successful_requests
            )
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """获取系统提示词 - 子类必须实现"""
        pass
    
    @abstractmethod
    def _get_relevant_keywords(self) -> List[str]:
        """获取相关关键词 - 子类必须实现"""
        pass
    
    @abstractmethod
    def _get_default_collection(self) -> str:
        """获取默认知识库集合名 - 子类必须实现"""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """获取Agent状态"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "is_active": self.is_active,
            "current_tasks_count": len(self.current_tasks),
            "completed_tasks_count": len(self.completed_tasks),
            "error_count": self.error_count,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "success_rate": self.successful_requests / self.total_requests if self.total_requests > 0 else 0,
            "average_response_time": self.average_response_time,
            "last_activity": self.last_activity.isoformat(),
            "preferred_model": self.preferred_model
        }
    
    async def cleanup(self):
        """清理资源"""
        # 取消所有正在进行的任务
        for task in self.current_tasks.values():
            task.status = "cancelled"
            task.completed_at = datetime.now()
            task.error_message = "Agent shutdown"
        
        self.current_tasks.clear()
        self.is_active = False
        
        logger.info(f"🧹 Agent {self.name} 资源清理完成")
