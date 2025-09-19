# 🛒 沃尔玛AI Agent平台 - API路由
# Walmart AI Agent Platform - API Routes

from fastapi import APIRouter

from app.api.v1 import agents, chat, documents, analytics, admin, mcp, websocket

# 创建主路由器
api_router = APIRouter()

# 包含各个模块的路由
api_router.include_router(
    agents.router,
    prefix="/agents",
    tags=["agents"]
)

api_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["chat"]
)

api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["documents"]
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["analytics"]
)

api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"]
)

api_router.include_router(
    mcp.router,
    prefix="/mcp",
    tags=["mcp"]
)

api_router.include_router(
    websocket.router,
    prefix="/ws",
    tags=["websocket"]
)