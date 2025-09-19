# 🛒 沃尔玛AI Agent平台 - 依赖注入
# Walmart AI Agent Platform - Dependencies

import logging
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.orchestrator import AgentOrchestrator
from app.core.database import get_db
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.llm_service import LLMService
from app.services.vector_service import VectorService
from app.services.data_service import DataService

logger = logging.getLogger(__name__)

# 安全方案
security = HTTPBearer()

# 全局服务实例（在应用启动时初始化）
_llm_service: Optional[LLMService] = None
_vector_service: Optional[VectorService] = None
_data_service: Optional[DataService] = None
_agent_orchestrator: Optional[AgentOrchestrator] = None
_auth_service: Optional[AuthService] = None


async def initialize_services():
    """初始化全局服务"""
    global _llm_service, _vector_service, _data_service, _agent_orchestrator, _auth_service
    
    try:
        # 初始化LLM服务
        _llm_service = LLMService()
        await _llm_service.initialize()
        
        # 初始化向量服务
        _vector_service = VectorService()
        await _vector_service.initialize()
        
        # 初始化数据服务
        _data_service = DataService()
        await _data_service.initialize(_vector_service)
        
        # 初始化认证服务
        _auth_service = AuthService()
        
        # 初始化Agent编排器
        _agent_orchestrator = AgentOrchestrator(
            llm_service=_llm_service,
            vector_service=_vector_service,
            data_service=_data_service
        )
        
        # 注册Agent类型
        from app.agents.retail_agent import RetailAnalysisAgent
        from app.agents.sales_agent import SalesAgent
        from app.agents.inventory_agent import InventoryAgent
        from app.agents.customer_service_agent import CustomerServiceAgent
        from app.agents.data_analysis_agent import DataAnalysisAgent
        
        _agent_orchestrator.register_agent_type(RetailAnalysisAgent, "retail_analysis")
        _agent_orchestrator.register_agent_type(SalesAgent, "sales")
        _agent_orchestrator.register_agent_type(InventoryAgent, "inventory")
        _agent_orchestrator.register_agent_type(CustomerServiceAgent, "customer_service")
        _agent_orchestrator.register_agent_type(DataAnalysisAgent, "data_analysis")
        
        # 创建默认Agent
        await _agent_orchestrator.create_agent(
            agent_type="retail_analysis",
            name="沃尔玛零售分析助手",
            description="专业的零售业务分析Agent，帮助分析销售数据、库存情况、客户行为等",
            capabilities=[
                "data_analysis",
                "natural_language", 
                "document_search",
                "reasoning",
                "planning"
            ]
        )
        
        await _agent_orchestrator.create_agent(
            agent_type="sales",
            name="销售分析专家",
            description="专门处理销售数据分析、预测、报告生成和销售策略优化",
            capabilities=[
                "data_analysis",
                "natural_language",
                "reasoning",
                "planning",
                "real_time_processing"
            ]
        )
        
        await _agent_orchestrator.create_agent(
            agent_type="inventory",
            name="库存管理专家",
            description="专门处理库存数据分析、库存优化、补货预警和供应链管理",
            capabilities=[
                "data_analysis",
                "real_time_processing",
                "reasoning",
                "planning",
                "natural_language"
            ]
        )
        
        await _agent_orchestrator.create_agent(
            agent_type="customer_service",
            name="客户服务助手",
            description="专门处理客户咨询、投诉处理、订单问题、退换货服务和客户关系管理",
            capabilities=[
                "natural_language",
                "document_search",
                "reasoning",
                "real_time_processing",
                "workflow_execution"
            ]
        )
        
        await _agent_orchestrator.create_agent(
            agent_type="data_analysis",
            name="数据分析专家",
            description="专门处理复杂数据分析、统计建模、预测分析和数据可视化任务",
            capabilities=[
                "data_analysis",
                "reasoning",
                "planning",
                "natural_language",
                "multi_modal"
            ]
        )
        
        logger.info("✅ 所有服务初始化完成")
        
    except Exception as e:
        logger.error(f"❌ 服务初始化失败: {e}")
        raise


async def cleanup_services():
    """清理服务资源"""
    global _agent_orchestrator, _vector_service, _data_service, _llm_service
    
    try:
        if _agent_orchestrator:
            await _agent_orchestrator.cleanup()
        
        # 其他服务清理...
        logger.info("🧹 服务清理完成")
        
    except Exception as e:
        logger.error(f"❌ 服务清理失败: {e}")


def get_llm_service() -> LLMService:
    """获取LLM服务"""
    if _llm_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM服务未初始化"
        )
    return _llm_service


def get_vector_service() -> VectorService:
    """获取向量服务"""
    if _vector_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="向量服务未初始化"
        )
    return _vector_service


def get_data_service() -> DataService:
    """获取数据服务"""
    if _data_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="数据服务未初始化"
        )
    return _data_service


def get_agent_orchestrator() -> AgentOrchestrator:
    """获取Agent编排器"""
    if _agent_orchestrator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent编排器未初始化"
        )
    return _agent_orchestrator


def get_auth_service() -> AuthService:
    """获取认证服务"""
    if _auth_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="认证服务未初始化"
        )
    return _auth_service


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """获取当前用户"""
    try:
        # 验证JWT token
        payload = auth_service.verify_token(credentials.credentials)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 从数据库获取用户
        user = await db.get(User, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户账户已禁用",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 用户认证失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证失败",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账户已禁用"
        )
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """要求管理员权限"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user


# 可选认证（允许匿名访问）
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
) -> Optional[User]:
    """获取当前用户（可选）"""
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials, db, auth_service)
    except HTTPException:
        return None
