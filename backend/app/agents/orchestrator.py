# 🛒 沃尔玛AI Agent平台 - Agent编排器
# Walmart AI Agent Platform - Agent Orchestrator

import asyncio
import logging
from typing import Any, Dict, List, Optional, Type
from datetime import datetime
from uuid import uuid4

from app.agents.base_agent import BaseAgent, AgentContext, AgentMessage, AgentTask, AgentCapability
from app.services.llm_service import LLMService
from app.services.vector_service import VectorService
from app.services.data_service import DataService

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Agent编排器 - 管理和协调多个Agent"""
    
    def __init__(
        self,
        llm_service: LLMService,
        vector_service: VectorService,
        data_service: DataService
    ):
        self.llm_service = llm_service
        self.vector_service = vector_service
        self.data_service = data_service
        
        # Agent管理
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_types: Dict[str, Type[BaseAgent]] = {}
        
        # 任务队列
        self.task_queue: List[AgentTask] = []
        self.active_contexts: Dict[str, AgentContext] = {}
        
        # 路由规则
        self.routing_rules: List[Dict[str, Any]] = []
        
        # 统计信息
        self.total_messages = 0
        self.total_tasks = 0
        self.successful_routes = 0
        
        logger.info("✅ Agent编排器初始化完成")
    
    def register_agent_type(self, agent_class: Type[BaseAgent], agent_type_name: str):
        """注册Agent类型"""
        self.agent_types[agent_type_name] = agent_class
        logger.info(f"✅ 注册Agent类型: {agent_type_name}")
    
    async def create_agent(
        self,
        agent_type: str,
        name: str,
        description: str,
        capabilities: List[AgentCapability],
        **kwargs
    ) -> str:
        """创建Agent实例"""
        if agent_type not in self.agent_types:
            raise ValueError(f"未知的Agent类型: {agent_type}")
        
        agent_class = self.agent_types[agent_type]
        agent = agent_class(
            name=name,
            description=description,
            capabilities=capabilities,
            llm_service=self.llm_service,
            vector_service=self.vector_service,
            data_service=self.data_service,
            **kwargs
        )
        
        self.agents[agent.id] = agent
        logger.info(f"✅ 创建Agent: {name} ({agent.id})")
        
        return agent.id
    
    def remove_agent(self, agent_id: str) -> bool:
        """移除Agent"""
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        asyncio.create_task(agent.cleanup())
        del self.agents[agent_id]
        
        logger.info(f"✅ 移除Agent: {agent.name} ({agent_id})")
        return True
    
    async def route_message(
        self,
        message: str,
        user_id: str,
        conversation_id: Optional[str] = None,
        preferred_agent_id: Optional[str] = None,
        **kwargs
    ) -> AgentMessage:
        """路由消息到合适的Agent"""
        self.total_messages += 1
        
        # 获取或创建上下文
        conversation_id = conversation_id or str(uuid4())
        context = self._get_or_create_context(conversation_id, user_id)
        
        try:
            # 选择Agent
            selected_agent = await self._select_agent(
                message, context, preferred_agent_id, **kwargs
            )
            
            if not selected_agent:
                return AgentMessage(
                    role="assistant",
                    content="抱歉，当前没有可用的Agent来处理您的请求。",
                    conversation_id=conversation_id,
                    metadata={"error": "no_suitable_agent"}
                )
            
            # 处理消息
            response = await selected_agent.handle_message(message, context, **kwargs)
            
            # 更新对话历史
            user_message = AgentMessage(
                role="user",
                content=message,
                conversation_id=conversation_id,
                metadata={"user_id": user_id}
            )
            
            context.conversation_history.extend([user_message, response])
            
            # 限制历史记录长度
            if len(context.conversation_history) > 50:
                context.conversation_history = context.conversation_history[-50:]
            
            self.successful_routes += 1
            logger.info(f"✅ 消息路由成功: {selected_agent.name}")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ 消息路由失败: {e}")
            return AgentMessage(
                role="assistant",
                content=f"处理消息时发生错误: {str(e)}",
                conversation_id=conversation_id,
                metadata={"error": str(e)}
            )
    
    async def execute_task(
        self,
        task: AgentTask,
        user_id: str,
        conversation_id: Optional[str] = None,
        preferred_agent_id: Optional[str] = None,
        **kwargs
    ) -> AgentTask:
        """执行任务"""
        self.total_tasks += 1
        
        # 获取或创建上下文
        conversation_id = conversation_id or str(uuid4())
        context = self._get_or_create_context(conversation_id, user_id)
        context.current_task = task
        
        try:
            # 选择Agent
            selected_agent = await self._select_agent_for_task(
                task, context, preferred_agent_id, **kwargs
            )
            
            if not selected_agent:
                task.status = "failed"
                task.error_message = "没有合适的Agent来执行此任务"
                task.completed_at = datetime.now()
                return task
            
            # 执行任务
            completed_task = await selected_agent.start_task(task, context)
            
            logger.info(f"✅ 任务执行完成: {task.name} by {selected_agent.name}")
            return completed_task
            
        except Exception as e:
            logger.error(f"❌ 任务执行失败: {e}")
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = datetime.now()
            return task
    
    async def _select_agent(
        self,
        message: str,
        context: AgentContext,
        preferred_agent_id: Optional[str] = None,
        **kwargs
    ) -> Optional[BaseAgent]:
        """选择合适的Agent处理消息"""
        
        # 如果指定了首选Agent，先尝试使用
        if preferred_agent_id and preferred_agent_id in self.agents:
            agent = self.agents[preferred_agent_id]
            if agent.is_active and await agent.can_handle_message(message, context, **kwargs):
                return agent
        
        # 评估所有可用的Agent
        candidate_agents = []
        
        for agent in self.agents.values():
            if not agent.is_active:
                continue
            
            # 检查Agent是否能处理该消息
            can_handle = await agent.can_handle_message(message, context, **kwargs)
            if can_handle:
                # 计算Agent适合度分数
                score = await self._calculate_agent_score(agent, message, context)
                candidate_agents.append((agent, score))
        
        if not candidate_agents:
            return None
        
        # 选择得分最高的Agent
        candidate_agents.sort(key=lambda x: x[1], reverse=True)
        return candidate_agents[0][0]
    
    async def _select_agent_for_task(
        self,
        task: AgentTask,
        context: AgentContext,
        preferred_agent_id: Optional[str] = None,
        **kwargs
    ) -> Optional[BaseAgent]:
        """为任务选择合适的Agent"""
        
        # 如果指定了首选Agent，先尝试使用
        if preferred_agent_id and preferred_agent_id in self.agents:
            agent = self.agents[preferred_agent_id]
            if agent.is_active and await agent.can_execute_task(task, context, **kwargs):
                return agent
        
        # 评估所有可用的Agent
        candidate_agents = []
        
        for agent in self.agents.values():
            if not agent.is_active:
                continue
            
            # 检查Agent是否能执行该任务
            can_execute = await agent.can_execute_task(task, context, **kwargs)
            if can_execute:
                # 计算Agent适合度分数
                score = await self._calculate_task_agent_score(agent, task, context)
                candidate_agents.append((agent, score))
        
        if not candidate_agents:
            return None
        
        # 选择得分最高的Agent
        candidate_agents.sort(key=lambda x: x[1], reverse=True)
        return candidate_agents[0][0]
    
    async def _calculate_agent_score(
        self,
        agent: BaseAgent,
        message: str,
        context: AgentContext
    ) -> float:
        """计算Agent处理消息的适合度分数"""
        score = 0.0
        
        # 基础分数：成功率
        if agent.total_requests > 0:
            success_rate = agent.successful_requests / agent.total_requests
            score += success_rate * 40  # 最高40分
        else:
            score += 30  # 新Agent给予中等分数
        
        # 响应时间分数（响应越快分数越高）
        if agent.average_response_time > 0:
            time_score = max(0, 20 - agent.average_response_time)  # 最高20分
            score += time_score
        else:
            score += 15
        
        # 当前负载分数（负载越低分数越高）
        load_score = max(0, 20 - len(agent.current_tasks) * 2)  # 最高20分
        score += load_score
        
        # 错误率惩罚
        if agent.total_requests > 0:
            error_rate = agent.error_count / agent.total_requests
            score -= error_rate * 20  # 最多扣20分
        
        # 能力匹配分数
        required_capabilities = self._extract_required_capabilities(message)
        matching_capabilities = set(agent.capabilities) & set(required_capabilities)
        capability_score = len(matching_capabilities) * 5  # 每个匹配能力5分
        score += capability_score
        
        return max(0, score)  # 确保分数不为负
    
    async def _calculate_task_agent_score(
        self,
        agent: BaseAgent,
        task: AgentTask,
        context: AgentContext
    ) -> float:
        """计算Agent执行任务的适合度分数"""
        score = 0.0
        
        # 基础分数：成功率
        if agent.total_requests > 0:
            success_rate = agent.successful_requests / agent.total_requests
            score += success_rate * 50  # 最高50分
        else:
            score += 35
        
        # 任务优先级分数
        score += task.priority * 5  # 优先级1-10，每级5分
        
        # 能力匹配分数
        required_capabilities = task.metadata.get("required_capabilities", [])
        matching_capabilities = set(agent.capabilities) & set(required_capabilities)
        if required_capabilities:
            capability_match_rate = len(matching_capabilities) / len(required_capabilities)
            score += capability_match_rate * 30  # 最高30分
        
        # 当前负载惩罚
        score -= len(agent.current_tasks) * 3
        
        return max(0, score)
    
    def _extract_required_capabilities(self, message: str) -> List[AgentCapability]:
        """从消息中提取所需的能力"""
        message_lower = message.lower()
        required_capabilities = []
        
        # 简单的关键词匹配（实际项目中可以使用更复杂的NLP方法）
        capability_keywords = {
            AgentCapability.DATA_ANALYSIS: ["分析", "统计", "数据", "报表", "图表"],
            AgentCapability.DOCUMENT_SEARCH: ["搜索", "查找", "文档", "资料"],
            AgentCapability.NATURAL_LANGUAGE: ["聊天", "对话", "解释", "回答"],
            AgentCapability.WORKFLOW_EXECUTION: ["执行", "运行", "流程", "工作流"],
            AgentCapability.REAL_TIME_PROCESSING: ["实时", "即时", "监控"],
            AgentCapability.REASONING: ["推理", "分析", "判断", "决策"],
            AgentCapability.PLANNING: ["计划", "规划", "安排", "策略"]
        }
        
        for capability, keywords in capability_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                required_capabilities.append(capability)
        
        return required_capabilities
    
    def _get_or_create_context(self, conversation_id: str, user_id: str) -> AgentContext:
        """获取或创建上下文"""
        if conversation_id not in self.active_contexts:
            self.active_contexts[conversation_id] = AgentContext(
                conversation_id=conversation_id,
                user_id=user_id
            )
        
        return self.active_contexts[conversation_id]
    
    def add_routing_rule(
        self,
        pattern: str,
        agent_id: str,
        priority: int = 1,
        conditions: Optional[Dict[str, Any]] = None
    ):
        """添加路由规则"""
        rule = {
            "pattern": pattern,
            "agent_id": agent_id,
            "priority": priority,
            "conditions": conditions or {}
        }
        
        self.routing_rules.append(rule)
        self.routing_rules.sort(key=lambda x: x["priority"], reverse=True)
        
        logger.info(f"✅ 添加路由规则: {pattern} -> {agent_id}")
    
    def remove_routing_rule(self, pattern: str) -> bool:
        """移除路由规则"""
        original_count = len(self.routing_rules)
        self.routing_rules = [rule for rule in self.routing_rules if rule["pattern"] != pattern]
        
        removed = len(self.routing_rules) < original_count
        if removed:
            logger.info(f"✅ 移除路由规则: {pattern}")
        
        return removed
    
    def get_agent_status(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """获取Agent状态"""
        if agent_id:
            if agent_id in self.agents:
                return self.agents[agent_id].get_status()
            else:
                return {"error": "Agent not found"}
        
        # 返回所有Agent状态
        return {
            "total_agents": len(self.agents),
            "active_agents": sum(1 for agent in self.agents.values() if agent.is_active),
            "agents": {
                agent_id: agent.get_status() 
                for agent_id, agent in self.agents.items()
            }
        }
    
    def get_orchestrator_stats(self) -> Dict[str, Any]:
        """获取编排器统计信息"""
        return {
            "total_messages": self.total_messages,
            "total_tasks": self.total_tasks,
            "successful_routes": self.successful_routes,
            "success_rate": self.successful_routes / self.total_messages if self.total_messages > 0 else 0,
            "active_contexts": len(self.active_contexts),
            "routing_rules": len(self.routing_rules),
            "registered_agent_types": list(self.agent_types.keys()),
            "active_agents": len([a for a in self.agents.values() if a.is_active])
        }
    
    async def cleanup(self):
        """清理资源"""
        # 清理所有Agent
        cleanup_tasks = [agent.cleanup() for agent in self.agents.values()]
        await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        
        # 清空状态
        self.agents.clear()
        self.active_contexts.clear()
        self.task_queue.clear()
        
        logger.info("🧹 Agent编排器清理完成")
