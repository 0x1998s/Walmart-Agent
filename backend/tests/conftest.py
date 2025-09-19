# 🛒 沃尔玛AI Agent平台 - 测试配置
# Walmart AI Agent Platform - Test Configuration

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.core.dependencies import get_agent_orchestrator, get_llm_service, get_vector_service
from app.agents.orchestrator import AgentOrchestrator
from app.services.llm_service import LLMService
from app.services.vector_service import VectorService
from app.services.data_service import DataService


# 测试数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session():
    """创建测试数据库会话"""
    # 创建表
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # 清理表
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def override_get_db(db_session):
    """覆盖数据库依赖"""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass
    return _override_get_db


@pytest.fixture(scope="function")
async def mock_llm_service():
    """模拟LLM服务"""
    class MockLLMService:
        def __init__(self):
            self.providers = {}
            self.default_provider = "mock"
        
        async def initialize(self):
            pass
        
        async def chat_completion(self, messages, **kwargs):
            from app.services.llm_service import LLMResponse, ModelProvider
            return LLMResponse(
                content="这是一个测试响应",
                model="mock-model",
                provider=ModelProvider.OPENAI,
                tokens_used=50,
                metadata={"test": True}
            )
        
        async def stream_completion(self, messages, **kwargs):
            for chunk in ["测试", "流式", "响应"]:
                yield chunk
        
        def get_available_providers(self):
            return ["mock"]
        
        async def health_check(self):
            return {"mock": True}
    
    return MockLLMService()


@pytest.fixture(scope="function")
async def mock_vector_service():
    """模拟向量服务"""
    class MockVectorService:
        def __init__(self):
            self.collections = {}
        
        async def initialize(self):
            pass
        
        async def add_documents(self, collection_name, documents, **kwargs):
            return [f"doc_{i}" for i in range(len(documents))]
        
        async def search_similar_documents(self, collection_name, query, **kwargs):
            return {
                "ids": [["doc_1", "doc_2"]],
                "documents": [["相关文档1", "相关文档2"]],
                "metadatas": [[{"source": "test"}, {"source": "test"}]],
                "distances": [[0.1, 0.2]]
            }
        
        async def get_collection_stats(self, collection_name):
            return {
                "name": collection_name,
                "count": 100,
                "metadata": {}
            }
        
        async def list_collections(self):
            return [
                {"name": "test_collection", "count": 100}
            ]
    
    return MockVectorService()


@pytest.fixture(scope="function")
async def mock_data_service(mock_vector_service):
    """模拟数据服务"""
    class MockDataService:
        def __init__(self):
            self.vector_service = mock_vector_service
        
        async def initialize(self, vector_service):
            self.vector_service = vector_service
        
        async def process_file(self, file_path, **kwargs):
            return {
                "status": "success",
                "file_path": str(file_path),
                "text_chunks": ["测试文本块1", "测试文本块2"],
                "metadata": {"test": True}
            }
        
        async def search_documents(self, query, **kwargs):
            return {
                "ids": [["doc_1"]],
                "documents": [["测试文档"]],
                "metadatas": [[{"source": "test"}]],
                "distances": [[0.1]]
            }
    
    return MockDataService()


@pytest.fixture(scope="function")
async def mock_orchestrator(mock_llm_service, mock_vector_service, mock_data_service):
    """模拟Agent编排器"""
    orchestrator = AgentOrchestrator(
        llm_service=mock_llm_service,
        vector_service=mock_vector_service,
        data_service=mock_data_service
    )
    
    # 注册测试Agent
    from app.agents.retail_agent import RetailAnalysisAgent
    orchestrator.register_agent_type(RetailAnalysisAgent, "retail_analysis")
    
    # 创建测试Agent
    await orchestrator.create_agent(
        agent_type="retail_analysis",
        name="测试零售分析助手",
        description="测试用的零售分析Agent",
        capabilities=["data_analysis", "natural_language"]
    )
    
    return orchestrator


@pytest.fixture(scope="function")
def client(override_get_db, mock_orchestrator, mock_llm_service, mock_vector_service):
    """创建测试客户端"""
    
    # 覆盖依赖
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_agent_orchestrator] = lambda: mock_orchestrator
    app.dependency_overrides[get_llm_service] = lambda: mock_llm_service
    app.dependency_overrides[get_vector_service] = lambda: mock_vector_service
    
    with TestClient(app) as test_client:
        yield test_client
    
    # 清理依赖覆盖
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_headers():
    """认证头"""
    # 这里应该生成真实的JWT token，简化处理
    return {"Authorization": "Bearer test_token"}


@pytest.fixture(scope="function")
def sample_user_data():
    """示例用户数据"""
    return {
        "username": "test_user",
        "email": "test@walmart.com",
        "full_name": "测试用户",
        "password": "test_password_123"
    }


@pytest.fixture(scope="function")
def sample_chat_message():
    """示例聊天消息"""
    return {
        "message": "请分析Q4销售数据",
        "conversation_id": "test_conversation_123"
    }


@pytest.fixture(scope="function")
def sample_agent_data():
    """示例Agent数据"""
    return {
        "agent_type": "retail_analysis",
        "name": "测试Agent",
        "description": "用于测试的Agent",
        "capabilities": ["data_analysis", "natural_language"]
    }


@pytest.fixture(scope="function")
def sample_task_data():
    """示例任务数据"""
    return {
        "name": "测试分析任务",
        "description": "测试用的数据分析任务",
        "input_data": {"query": "分析销售数据"},
        "priority": 5,
        "metadata": {"test": True}
    }


# 测试工具函数
def assert_response_ok(response):
    """断言响应成功"""
    assert response.status_code == 200
    return response.json()


def assert_response_created(response):
    """断言资源创建成功"""
    assert response.status_code == 201
    return response.json()


def assert_response_error(response, status_code=400):
    """断言响应错误"""
    assert response.status_code == status_code
    return response.json()


# 异步测试标记
pytestmark = pytest.mark.asyncio
