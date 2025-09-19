# 🛒 沃尔玛AI Agent平台 - 主应用入口
# Walmart AI Agent Platform - Main Application Entry

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app

from app.api.routes import api_router
from app.core.config import get_settings
from app.core.database import init_db
from app.utils.logger import setup_logging

# 初始化设置
settings = get_settings()
setup_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理"""
    logger.info("🚀 启动沃尔玛AI Agent平台...")
    
    # 初始化数据库
    await init_db()
    logger.info("✅ 数据库初始化完成")
    
    # 初始化向量数据库
    from app.services.vector_service import VectorService
    vector_service = VectorService()
    await vector_service.initialize()
    logger.info("✅ 向量数据库初始化完成")
    
    # 启动后台任务
    logger.info("✅ 平台启动完成，准备接收请求")
    
    yield
    
    logger.info("🛑 正在关闭沃尔玛AI Agent平台...")
    # 清理资源
    logger.info("✅ 平台已安全关闭")


# 创建FastAPI应用
app = FastAPI(
    title="沃尔玛AI Agent平台",
    description="企业级AI Agent解决方案，专为零售巨头设计的智能分析平台",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    lifespan=lifespan,
)

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# 添加Prometheus监控端点
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "内部服务器错误",
            "error_type": type(exc).__name__,
            "path": str(request.url),
        },
    )


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "walmart-ai-agent",
        "version": "1.0.0",
        "timestamp": asyncio.get_event_loop().time(),
    }


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "🛒 欢迎使用沃尔玛AI Agent平台",
        "description": "企业级AI Agent解决方案",
        "docs": "/api/v1/docs",
        "version": "1.0.0",
    }


# 注册API路由
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8080,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else 4,
        log_level=settings.LOG_LEVEL.lower(),
    )
