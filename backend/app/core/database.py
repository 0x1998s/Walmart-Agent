# 🛒 沃尔玛AI Agent平台 - 数据库管理
# Walmart AI Agent Platform - Database Management

import asyncio
from typing import AsyncGenerator

from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# 创建异步数据库引擎
async_engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

# 创建同步数据库引擎（用于Alembic迁移）
sync_engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# 创建同步会话工厂
SessionLocal = sessionmaker(
    bind=sync_engine,
    autoflush=False,
    autocommit=False,
)

# 数据库基础模型
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_db():
    """获取同步数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_db():
    """初始化数据库"""
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # 创建所有表
        async with async_engine.begin() as conn:
            # 导入所有模型以确保它们被注册
            from app.models import user, document, agent, task, metrics
            
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ 数据库表创建完成")
            
        # 创建默认数据
        await create_default_data()
        logger.info("✅ 默认数据创建完成")
        
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        raise


async def create_default_data():
    """创建默认数据"""
    from app.models.user import User
    from app.services.auth_service import AuthService
    
    async with AsyncSessionLocal() as session:
        # 检查是否已有管理员用户
        admin_user = await session.get(User, 1)
        if not admin_user:
            # 创建默认管理员用户
            auth_service = AuthService()
            admin_user = User(
                username="admin",
                email="admin@walmart.com",
                full_name="系统管理员",
                hashed_password=auth_service.get_password_hash("walmart_admin_2024"),
                is_active=True,
                is_superuser=True,
            )
            session.add(admin_user)
            await session.commit()


# 数据库连接事件监听器
@event.listens_for(sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """设置数据库连接参数"""
    if "sqlite" in settings.DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# 数据库健康检查
async def check_db_health() -> bool:
    """检查数据库连接健康状态"""
    try:
        async with async_engine.begin() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception:
        return False


# 数据库清理
async def cleanup_db():
    """清理数据库连接"""
    await async_engine.dispose()
