# 🛒 沃尔玛AI Agent平台 - 聊天API
# Walmart AI Agent Platform - Chat API

import logging
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from app.agents.orchestrator import AgentOrchestrator
from app.agents.base_agent import AgentMessage
from app.core.dependencies import get_agent_orchestrator, get_current_user
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str = Field(..., description="用户消息")
    conversation_id: Optional[str] = Field(None, description="对话ID")
    preferred_agent_id: Optional[str] = Field(None, description="首选Agent ID")
    stream: bool = Field(False, description="是否流式返回")
    context: Dict[str, Any] = Field(default_factory=dict, description="额外上下文")


class ChatResponse(BaseModel):
    """聊天响应模型"""
    id: str = Field(..., description="消息ID")
    conversation_id: str = Field(..., description="对话ID")
    message: str = Field(..., description="回复消息")
    agent_id: Optional[str] = Field(None, description="处理的Agent ID")
    agent_name: Optional[str] = Field(None, description="Agent名称")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    timestamp: str = Field(..., description="时间戳")


class ConversationHistory(BaseModel):
    """对话历史模型"""
    conversation_id: str
    messages: List[Dict[str, Any]]
    total_messages: int
    created_at: str
    updated_at: str


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
    current_user: User = Depends(get_current_user)
):
    """发送聊天消息"""
    try:
        # 路由消息到合适的Agent
        response = await orchestrator.route_message(
            message=request.message,
            user_id=str(current_user.id),
            conversation_id=request.conversation_id,
            preferred_agent_id=request.preferred_agent_id,
            **request.context
        )
        
        # 获取Agent信息
        agent_name = None
        if response.agent_id and response.agent_id in orchestrator.agents:
            agent_name = orchestrator.agents[response.agent_id].name
        
        return ChatResponse(
            id=response.id,
            conversation_id=response.conversation_id,
            message=response.content,
            agent_id=response.agent_id,
            agent_name=agent_name,
            metadata=response.metadata,
            timestamp=response.timestamp.isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ 聊天消息处理失败: {e}")
        raise HTTPException(status_code=500, detail=f"消息处理失败: {str(e)}")


@router.post("/stream")
async def stream_message(
    request: ChatRequest,
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
    current_user: User = Depends(get_current_user)
):
    """流式聊天消息"""
    
    async def generate_response():
        try:
            conversation_id = request.conversation_id or str(uuid4())
            
            # 获取上下文
            context = orchestrator._get_or_create_context(
                conversation_id, str(current_user.id)
            )
            
            # 选择Agent
            selected_agent = await orchestrator._select_agent(
                request.message, context, request.preferred_agent_id
            )
            
            if not selected_agent:
                yield f"data: {{'error': '没有可用的Agent处理请求'}}\n\n"
                return
            
            # 流式生成响应
            if hasattr(selected_agent, 'stream_completion') and selected_agent.llm_service:
                messages = selected_agent._build_message_history(request.message, context)
                
                async for chunk in selected_agent.llm_service.stream_completion(
                    messages=messages,
                    provider=selected_agent.preferred_model,
                    temperature=0.7
                ):
                    yield f"data: {{'content': '{chunk}', 'agent_id': '{selected_agent.id}', 'agent_name': '{selected_agent.name}'}}\n\n"
            else:
                # 如果Agent不支持流式，则一次性返回
                response = await selected_agent.handle_message(request.message, context)
                yield f"data: {{'content': '{response.content}', 'agent_id': '{selected_agent.id}', 'agent_name': '{selected_agent.name}', 'final': true}}\n\n"
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            logger.error(f"❌ 流式聊天失败: {e}")
            yield f"data: {{'error': '{str(e)}'}}\n\n"
    
    return EventSourceResponse(generate_response())


@router.get("/conversations", response_model=List[ConversationHistory])
async def get_conversations(
    limit: int = 20,
    offset: int = 0,
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
    current_user: User = Depends(get_current_user)
):
    """获取用户对话历史列表"""
    try:
        user_conversations = []
        
        # 从活跃上下文中筛选用户的对话
        for conv_id, context in orchestrator.active_contexts.items():
            if context.user_id == str(current_user.id):
                conversation = ConversationHistory(
                    conversation_id=conv_id,
                    messages=[msg.dict() for msg in context.conversation_history],
                    total_messages=len(context.conversation_history),
                    created_at=context.conversation_history[0].timestamp.isoformat() if context.conversation_history else "",
                    updated_at=context.conversation_history[-1].timestamp.isoformat() if context.conversation_history else ""
                )
                user_conversations.append(conversation)
        
        # 按更新时间排序
        user_conversations.sort(key=lambda x: x.updated_at, reverse=True)
        
        # 分页
        return user_conversations[offset:offset + limit]
        
    except Exception as e:
        logger.error(f"❌ 获取对话历史失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取对话历史失败: {str(e)}")


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    limit: int = 50,
    offset: int = 0,
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
    current_user: User = Depends(get_current_user)
):
    """获取特定对话的消息历史"""
    try:
        if conversation_id not in orchestrator.active_contexts:
            raise HTTPException(status_code=404, detail="对话不存在")
        
        context = orchestrator.active_contexts[conversation_id]
        
        # 验证用户权限
        if context.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="无权访问此对话")
        
        # 分页获取消息
        messages = context.conversation_history[offset:offset + limit]
        
        return {
            "conversation_id": conversation_id,
            "messages": [msg.dict() for msg in messages],
            "total_messages": len(context.conversation_history),
            "has_more": offset + limit < len(context.conversation_history)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取对话消息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取对话消息失败: {str(e)}")


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
    current_user: User = Depends(get_current_user)
):
    """删除对话"""
    try:
        if conversation_id not in orchestrator.active_contexts:
            raise HTTPException(status_code=404, detail="对话不存在")
        
        context = orchestrator.active_contexts[conversation_id]
        
        # 验证用户权限
        if context.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="无权删除此对话")
        
        # 删除对话上下文
        del orchestrator.active_contexts[conversation_id]
        
        return {"message": "对话已删除", "conversation_id": conversation_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 删除对话失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除对话失败: {str(e)}")


@router.post("/conversations/{conversation_id}/clear")
async def clear_conversation(
    conversation_id: str,
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
    current_user: User = Depends(get_current_user)
):
    """清空对话历史"""
    try:
        if conversation_id not in orchestrator.active_contexts:
            raise HTTPException(status_code=404, detail="对话不存在")
        
        context = orchestrator.active_contexts[conversation_id]
        
        # 验证用户权限
        if context.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="无权修改此对话")
        
        # 清空对话历史
        context.conversation_history.clear()
        
        return {"message": "对话历史已清空", "conversation_id": conversation_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 清空对话失败: {e}")
        raise HTTPException(status_code=500, detail=f"清空对话失败: {str(e)}")


@router.get("/suggestions")
async def get_chat_suggestions(
    query: Optional[str] = None,
    limit: int = 5,
    current_user: User = Depends(get_current_user)
):
    """获取聊天建议"""
    try:
        # 基础建议
        base_suggestions = [
            "分析Q4销售数据趋势",
            "查看库存周转率情况",
            "分析客户购买行为模式",
            "生成月度业绩报告",
            "预测下季度销售趋势",
            "分析商品品类表现",
            "查看门店运营指标",
            "分析竞争对手策略",
            "优化库存补货策略",
            "分析客户满意度数据"
        ]
        
        if query:
            # 基于查询过滤建议
            filtered_suggestions = [
                s for s in base_suggestions 
                if any(word in s for word in query.split())
            ]
            suggestions = filtered_suggestions[:limit] if filtered_suggestions else base_suggestions[:limit]
        else:
            suggestions = base_suggestions[:limit]
        
        return {
            "suggestions": suggestions,
            "total": len(suggestions)
        }
        
    except Exception as e:
        logger.error(f"❌ 获取聊天建议失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取建议失败: {str(e)}")


@router.post("/feedback")
async def submit_feedback(
    feedback_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """提交聊天反馈"""
    try:
        # 验证反馈数据
        required_fields = ["message_id", "rating", "feedback_type"]
        if not all(field in feedback_data for field in required_fields):
            raise HTTPException(status_code=400, detail="缺少必要的反馈字段")
        
        # 异步处理反馈
        background_tasks.add_task(
            process_feedback,
            feedback_data,
            str(current_user.id)
        )
        
        return {"message": "反馈已提交，谢谢您的建议！"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 提交反馈失败: {e}")
        raise HTTPException(status_code=500, detail=f"提交反馈失败: {str(e)}")


async def process_feedback(feedback_data: Dict[str, Any], user_id: str):
    """处理用户反馈（后台任务）"""
    try:
        # 这里可以将反馈存储到数据库、发送通知等
        logger.info(f"📝 收到用户反馈: {user_id} - {feedback_data}")
        
        # 如果是负面反馈，可以触发改进流程
        if feedback_data.get("rating", 5) < 3:
            logger.warning(f"⚠️ 负面反馈需要关注: {feedback_data}")
        
    except Exception as e:
        logger.error(f"❌ 处理反馈失败: {e}")
