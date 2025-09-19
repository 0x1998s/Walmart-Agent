# 🛒 沃尔玛AI Agent平台 - Agent测试
# Walmart AI Agent Platform - Agent Tests

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.agents.base_agent import AgentContext, AgentMessage, AgentTask
from app.agents.retail_agent import RetailAnalysisAgent
from app.agents.sales_agent import SalesAgent
from app.agents.inventory_agent import InventoryAgent


class TestRetailAnalysisAgent:
    """零售分析Agent测试"""
    
    @pytest.fixture
    async def retail_agent(self, mock_llm_service, mock_vector_service, mock_data_service):
        """创建零售分析Agent"""
        agent = RetailAnalysisAgent(
            llm_service=mock_llm_service,
            vector_service=mock_vector_service,
            data_service=mock_data_service
        )
        return agent
    
    async def test_agent_initialization(self, retail_agent):
        """测试Agent初始化"""
        assert retail_agent.name == "零售分析助手"
        assert "data_analysis" in [cap.value for cap in retail_agent.capabilities]
        assert retail_agent.is_active
    
    async def test_process_message(self, retail_agent):
        """测试消息处理"""
        context = AgentContext(
            user_id="test_user",
            conversation_id="test_conversation",
            session_data={}
        )
        
        message = "分析Q4销售数据趋势"
        result = await retail_agent.process_message(message, context)
        
        assert isinstance(result, AgentMessage)
        assert result.role == "assistant"
        assert len(result.content) > 0
        assert result.metadata is not None
    
    async def test_execute_task(self, retail_agent):
        """测试任务执行"""
        context = AgentContext(
            user_id="test_user",
            conversation_id="test_conversation",
            session_data={}
        )
        
        task = AgentTask(
            name="销售数据分析",
            description="分析Q4销售数据",
            input_data={"period": "Q4_2024"},
            metadata={"task_type": "sales_analysis"}
        )
        
        result = await retail_agent.execute_task(task, context)
        
        assert isinstance(result, AgentTask)
        assert result.status in ["completed", "failed"]
        assert result.output_data is not None
    
    async def test_search_knowledge(self, retail_agent):
        """测试知识搜索"""
        results = await retail_agent.search_knowledge(
            query="销售数据",
            collection_name="retail_data",
            n_results=5
        )
        
        assert isinstance(results, list)
        assert len(results) > 0


class TestSalesAgent:
    """销售Agent测试"""
    
    @pytest.fixture
    async def sales_agent(self, mock_llm_service, mock_vector_service, mock_data_service):
        """创建销售Agent"""
        agent = SalesAgent(
            llm_service=mock_llm_service,
            vector_service=mock_vector_service,
            data_service=mock_data_service
        )
        return agent
    
    async def test_sales_query_identification(self, sales_agent):
        """测试销售查询类型识别"""
        # 测试营收查询
        query_type = sales_agent._identify_sales_query("查看本季度营收情况")
        assert query_type == "revenue"
        
        # 测试预测查询
        query_type = sales_agent._identify_sales_query("预测下个月销售额")
        assert query_type == "forecast"
        
        # 测试转化率查询
        query_type = sales_agent._identify_sales_query("分析转化率数据")
        assert query_type == "conversion"
    
    async def test_revenue_analysis(self, sales_agent):
        """测试营收分析"""
        context = AgentContext(
            user_id="test_user",
            conversation_id="test_conversation",
            session_data={}
        )
        
        task = AgentTask(
            name="营收分析",
            description="分析营收数据",
            input_data={"period": "Q4_2024"},
            metadata={"task_type": "revenue_analysis"}
        )
        
        result = await sales_agent._analyze_revenue(task, context)
        
        assert result["analysis_type"] == "revenue"
        assert "revenue_metrics" in result
        assert "revenue_breakdown" in result
        assert "insights" in result
        assert "recommendations" in result
    
    async def test_sales_forecast(self, sales_agent):
        """测试销售预测"""
        context = AgentContext(
            user_id="test_user",
            conversation_id="test_conversation",
            session_data={}
        )
        
        task = AgentTask(
            name="销售预测",
            description="预测销售趋势",
            input_data={"forecast_days": 90},
            metadata={"task_type": "sales_forecast"}
        )
        
        result = await sales_agent._forecast_sales(task, context)
        
        assert result["analysis_type"] == "forecast"
        assert "predictions" in result
        assert "factors" in result
        assert "risks" in result


class TestInventoryAgent:
    """库存Agent测试"""
    
    @pytest.fixture
    async def inventory_agent(self, mock_llm_service, mock_vector_service, mock_data_service):
        """创建库存Agent"""
        agent = InventoryAgent(
            llm_service=mock_llm_service,
            vector_service=mock_vector_service,
            data_service=mock_data_service
        )
        return agent
    
    async def test_inventory_query_identification(self, inventory_agent):
        """测试库存查询类型识别"""
        # 测试缺货查询
        query_type = inventory_agent._identify_inventory_query("哪些商品缺货了")
        assert query_type == "stockout"
        
        # 测试补货查询
        query_type = inventory_agent._identify_inventory_query("需要补货的商品")
        assert query_type == "reorder"
        
        # 测试周转查询
        query_type = inventory_agent._identify_inventory_query("库存周转率分析")
        assert query_type == "turnover"
    
    async def test_stock_level_check(self, inventory_agent):
        """测试库存水平检查"""
        context = AgentContext(
            user_id="test_user",
            conversation_id="test_conversation",
            session_data={}
        )
        
        task = AgentTask(
            name="库存检查",
            description="检查当前库存水平",
            input_data={},
            metadata={"task_type": "stock_level_check"}
        )
        
        result = await inventory_agent._check_stock_levels(task, context)
        
        assert result["analysis_type"] == "stock_level_check"
        assert "overall_status" in result
        assert "stock_status" in result
        assert "category_breakdown" in result
        assert "urgent_actions" in result
    
    async def test_inventory_alerts(self, inventory_agent):
        """测试库存预警"""
        knowledge = [
            {"content": "iPhone库存不足", "score": 0.9},
            {"content": "冬季外套库存过多", "score": 0.8}
        ]
        
        alerts = inventory_agent._check_inventory_alerts(knowledge)
        
        assert isinstance(alerts, list)
        assert len(alerts) > 0
        
        # 检查预警类型
        alert_types = [alert["type"] for alert in alerts]
        assert "low_stock" in alert_types or "overstock" in alert_types
    
    async def test_urgency_calculation(self, inventory_agent):
        """测试紧急程度计算"""
        high_alerts = [
            {"type": "low_stock", "severity": "high"},
            {"type": "stockout", "severity": "high"}
        ]
        
        urgency = inventory_agent._calculate_urgency(high_alerts)
        assert urgency == "urgent"
        
        medium_alerts = [
            {"type": "overstock", "severity": "medium"}
        ]
        
        urgency = inventory_agent._calculate_urgency(medium_alerts)
        assert urgency == "medium"
        
        no_alerts = []
        urgency = inventory_agent._calculate_urgency(no_alerts)
        assert urgency == "normal"


class TestAgentOrchestrator:
    """Agent编排器测试"""
    
    async def test_agent_registration(self, mock_orchestrator):
        """测试Agent注册"""
        agent_count = len(mock_orchestrator.agent_types)
        assert agent_count > 0
        
        # 检查是否包含零售分析Agent
        assert "retail_analysis" in mock_orchestrator.agent_types
    
    async def test_agent_creation(self, mock_orchestrator):
        """测试Agent创建"""
        agent_id = await mock_orchestrator.create_agent(
            agent_type="retail_analysis",
            name="测试Agent",
            description="测试用Agent",
            capabilities=["data_analysis"]
        )
        
        assert agent_id is not None
        assert agent_id in mock_orchestrator.agents
    
    async def test_message_routing(self, mock_orchestrator):
        """测试消息路由"""
        response = await mock_orchestrator.route_message(
            message="分析销售数据",
            user_id="test_user",
            conversation_id="test_conversation"
        )
        
        assert response is not None
        assert hasattr(response, 'content')
        assert hasattr(response, 'agent_id')
    
    async def test_orchestrator_stats(self, mock_orchestrator):
        """测试编排器统计"""
        stats = mock_orchestrator.get_orchestrator_stats()
        
        assert "total_agents" in stats
        assert "active_agents" in stats
        assert "total_conversations" in stats
        assert "total_messages" in stats
