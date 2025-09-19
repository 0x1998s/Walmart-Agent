# 🛒 沃尔玛AI Agent平台 - Agent管理API
# Walmart AI Agent Platform - Agent Management API

import logging
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field

from app.agents.orchestrator import AgentOrchestrator
from app.agents.base_agent import AgentCapability, AgentTask
from app.core.dependencies import get_agent_orchestrator, get_current_user, require_admin
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


class AgentCreateRequest(BaseModel):
    """创建Agent请求模型"""
    agent_type: str = Field(..., description="Agent类型")
    name: str = Field(..., description="Agent名称")
    description: str = Field(..., description="Agent描述")
    capabilities: List[AgentCapability] = Field(..., description="Agent能力列表")
    config: Dict[str, Any] = Field(default_factory=dict, description="配置参数")


class AgentResponse(BaseModel):
    """Agent响应模型"""
    id: str
    name: str
    description: str
    capabilities: List[AgentCapability]
    is_active: bool
    current_tasks_count: int
    completed_tasks_count: int
    success_rate: float
    average_response_time: float
    last_activity: str
    preferred_model: str


class TaskCreateRequest(BaseModel):
    """创建任务请求模型"""
    name: str = Field(..., description="任务名称")
    description: str = Field(..., description="任务描述")
    input_data: Dict[str, Any] = Field(default_factory=dict, description="输入数据")
    priority: int = Field(default=1, description="任务优先级(1-10)")
    preferred_agent_id: Optional[str] = Field(None, description="首选Agent ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="任务元数据")


class TaskResponse(BaseModel):
    """任务响应模型"""
    id: str
    name: str
    description: str
    status: str
    priority: int
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    agent_id: Optional[str]
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    error_message: Optional[str]


@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
    current_user: User = Depends(get_current_user)
):
    """获取Agent列表"""
    try:
        agents = []
        for agent_id, agent in orchestrator.agents.items():
            status = agent.get_status()
            agents.append(AgentResponse(
                id=status["id"],
                name=status["name"],
                description=status["description"],
                capabilities=status["capabilities"],
                is_active=status["is_active"],
                current_tasks_count=status["current_tasks_count"],
                completed_tasks_count=status["completed_tasks_count"],
                success_rate=status["success_rate"],
                average_response_time=status["average_response_time"],
                last_activity=status["last_activity"],
                preferred_model=status["preferred_model"]
            ))
        
        return agents
        
    except Exception as e:
        logger.error(f"❌ 获取Agent列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取Agent列表失败: {str(e)}")


@router.post("/", response_model=Dict[str, str])
async def create_agent(
    request: AgentCreateRequest,
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
    current_user: User = Depends(require_admin)
):
    """创建新Agent"""
    try:
        agent_id = await orchestrator.create_agent(
            agent_type=request.agent_type,
            name=request.name,
            description=request.description,
            capabilities=request.capabilities,
            **request.config
        )
        
        return {
            "message": f"Agent创建成功: {request.name}",
            "agent_id": agent_id
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ 创建Agent失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建Agent失败: {str(e)}")


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
    current_user: User = Depends(get_current_user)
):
    """获取特定Agent信息"""
    try:
        if agent_id not in orchestrator.agents:
            raise HTTPException(status_code=404, detail="Agent不存在")
        
        agent = orchestrator.agents[agent_id]
        status = agent.get_status()
        
        return AgentResponse(
            id=status["id"],
            name=status["name"],
            description=status["description"],
            capabilities=status["capabilities"],
            is_active=status["is_active"],
            current_tasks_count=status["current_tasks_count"],
            completed_tasks_count=status["completed_tasks_count"],
            success_rate=status["success_rate"],
            average_response_time=status["average_response_time"],
            last_activity=status["last_activity"],
            preferred_model=status["preferred_model"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取Agent信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取Agent信息失败: {str(e)}")


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str,
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
    current_user: User = Depends(require_admin)
):
    """删除Agent"""
    try:
        if not orchestrator.remove_agent(agent_id):
            raise HTTPException(status_code=404, detail="Agent不存在")
        
        return {"message": f"Agent已删除: {agent_id}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 删除Agent失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除Agent失败: {str(e)}")


@router.post("/{agent_id}/activate")
async def activate_agent(
    agent_id: str,
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
    current_user: User = Depends(require_admin)
):
    """激活Agent"""
    try:
        if agent_id not in orchestrator.agents:
            raise HTTPException(status_code=404, detail="Agent不存在")
        
        agent = orchestrator.agents[agent_id]
        agent.is_active = True
        
        return {"message": f"Agent已激活: {agent.name}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 激活Agent失败: {e}")
        raise HTTPException(status_code=500, detail=f"激活Agent失败: {str(e)}")


@router.post("/{agent_id}/deactivate")
async def deactivate_agent(
    agent_id: str,
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
    current_user: User = Depends(require_admin)
):
    """停用Agent"""
    try:
        if agent_id not in orchestrator.agents:
            raise HTTPException(status_code=404, detail="Agent不存在")
        
        agent = orchestrator.agents[agent_id]
        agent.is_active = False
        
        return {"message": f"Agent已停用: {agent.name}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 停用Agent失败: {e}")
        raise HTTPException(status_code=500, detail=f"停用Agent失败: {str(e)}")


@router.get("/{agent_id}/tasks", response_model=List[TaskResponse])
async def get_agent_tasks(
    agent_id: str,
    status_filter: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
    current_user: User = Depends(get_current_user)
):
    """获取Agent的任务列表"""
    try:
        if agent_id not in orchestrator.agents:
            raise HTTPException(status_code=404, detail="Agent不存在")
        
        agent = orchestrator.agents[agent_id]
        
        # 合并当前任务和已完成任务
        all_tasks = list(agent.current_tasks.values()) + agent.completed_tasks
        
        # 状态过滤
        if status_filter:
            all_tasks = [task for task in all_tasks if task.status == status_filter]
        
        # 按创建时间排序
        all_tasks.sort(key=lambda x: x.created_at, reverse=True)
        
        # 分页
        tasks = all_tasks[offset:offset + limit]
        
        return [
            TaskResponse(
                id=task.id,
                name=task.name,
                description=task.description,
                status=task.status,
                priority=task.priority,
                input_data=task.input_data,
                output_data=task.output_data,
                agent_id=task.agent_id,
                created_at=task.created_at.isoformat(),
                started_at=task.started_at.isoformat() if task.started_at else None,
                completed_at=task.completed_at.isoformat() if task.completed_at else None,
                error_message=task.error_message
            )
            for task in tasks
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取Agent任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取Agent任务失败: {str(e)}")


@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    request: TaskCreateRequest,
    background_tasks: BackgroundTasks,
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
    current_user: User = Depends(get_current_user)
):
    """创建新任务"""
    try:
        # 创建任务对象
        task = AgentTask(
            name=request.name,
            description=request.description,
            input_data=request.input_data,
            priority=request.priority,
            metadata=request.metadata
        )
        
        # 异步执行任务
        background_tasks.add_task(
            execute_task_async,
            task,
            str(current_user.id),
            orchestrator,
            request.preferred_agent_id
        )
        
        return TaskResponse(
            id=task.id,
            name=task.name,
            description=task.description,
            status=task.status,
            priority=task.priority,
            input_data=task.input_data,
            output_data=task.output_data,
            agent_id=task.agent_id,
            created_at=task.created_at.isoformat(),
            started_at=task.started_at.isoformat() if task.started_at else None,
            completed_at=task.completed_at.isoformat() if task.completed_at else None,
            error_message=task.error_message
        )
        
    except Exception as e:
        logger.error(f"❌ 创建任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
    current_user: User = Depends(get_current_user)
):
    """获取特定任务信息"""
    try:
        # 在所有Agent中查找任务
        task = None
        for agent in orchestrator.agents.values():
            # 检查当前任务
            if task_id in agent.current_tasks:
                task = agent.current_tasks[task_id]
                break
            
            # 检查已完成任务
            for completed_task in agent.completed_tasks:
                if completed_task.id == task_id:
                    task = completed_task
                    break
            
            if task:
                break
        
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        return TaskResponse(
            id=task.id,
            name=task.name,
            description=task.description,
            status=task.status,
            priority=task.priority,
            input_data=task.input_data,
            output_data=task.output_data,
            agent_id=task.agent_id,
            created_at=task.created_at.isoformat(),
            started_at=task.started_at.isoformat() if task.started_at else None,
            completed_at=task.completed_at.isoformat() if task.completed_at else None,
            error_message=task.error_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取任务信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取任务信息失败: {str(e)}")


@router.get("/types")
async def get_agent_types(
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
    current_user: User = Depends(get_current_user)
):
    """获取可用的Agent类型"""
    try:
        agent_types = list(orchestrator.agent_types.keys())
        
        # 添加类型描述
        type_descriptions = {
            "retail_analysis": "零售分析Agent - 专门处理销售数据分析、趋势预测等",
            "sales_agent": "销售Agent - 处理销售相关查询和分析",
            "inventory_agent": "库存Agent - 管理库存分析和优化",
            "customer_service": "客服Agent - 处理客户咨询和服务",
            "data_analysis": "数据分析Agent - 通用数据分析和报告生成"
        }
        
        return {
            "agent_types": [
                {
                    "type": agent_type,
                    "description": type_descriptions.get(agent_type, f"{agent_type} Agent")
                }
                for agent_type in agent_types
            ],
            "total": len(agent_types)
        }
        
    except Exception as e:
        logger.error(f"❌ 获取Agent类型失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取Agent类型失败: {str(e)}")


@router.get("/capabilities")
async def get_agent_capabilities(
    current_user: User = Depends(get_current_user)
):
    """获取Agent能力列表"""
    try:
        capabilities = [
            {
                "name": capability.value,
                "description": get_capability_description(capability)
            }
            for capability in AgentCapability
        ]
        
        return {
            "capabilities": capabilities,
            "total": len(capabilities)
        }
        
    except Exception as e:
        logger.error(f"❌ 获取Agent能力失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取Agent能力失败: {str(e)}")


@router.get("/stats")
async def get_agent_stats(
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
    current_user: User = Depends(get_current_user)
):
    """获取Agent统计信息"""
    try:
        stats = orchestrator.get_orchestrator_stats()
        
        # 添加详细统计
        agent_stats = []
        for agent_id, agent in orchestrator.agents.items():
            agent_status = agent.get_status()
            agent_stats.append({
                "id": agent_id,
                "name": agent_status["name"],
                "success_rate": agent_status["success_rate"],
                "total_requests": agent_status["total_requests"],
                "average_response_time": agent_status["average_response_time"],
                "current_tasks": agent_status["current_tasks_count"]
            })
        
        return {
            **stats,
            "agent_details": agent_stats
        }
        
    except Exception as e:
        logger.error(f"❌ 获取Agent统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取Agent统计失败: {str(e)}")


async def execute_task_async(
    task: AgentTask,
    user_id: str,
    orchestrator: AgentOrchestrator,
    preferred_agent_id: Optional[str] = None
):
    """异步执行任务"""
    try:
        await orchestrator.execute_task(
            task=task,
            user_id=user_id,
            preferred_agent_id=preferred_agent_id
        )
        logger.info(f"✅ 后台任务执行完成: {task.name}")
        
    except Exception as e:
        logger.error(f"❌ 后台任务执行失败: {e}")


def get_capability_description(capability: AgentCapability) -> str:
    """获取能力描述"""
    descriptions = {
        AgentCapability.DATA_ANALYSIS: "数据分析和统计处理能力",
        AgentCapability.NATURAL_LANGUAGE: "自然语言理解和生成能力",
        AgentCapability.DOCUMENT_SEARCH: "文档搜索和知识检索能力",
        AgentCapability.WORKFLOW_EXECUTION: "工作流程执行和自动化能力",
        AgentCapability.REAL_TIME_PROCESSING: "实时数据处理能力",
        AgentCapability.MULTI_MODAL: "多模态数据处理能力",
        AgentCapability.REASONING: "逻辑推理和决策能力",
        AgentCapability.PLANNING: "规划和策略制定能力"
    }
    
    return descriptions.get(capability, "未知能力")
