# 🛒 沃尔玛AI Agent平台 - 库存Agent
# Walmart AI Agent Platform - Inventory Agent

import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from app.agents.base_agent import BaseAgent, AgentCapability, AgentContext, AgentMessage, AgentTask

logger = logging.getLogger(__name__)


class InventoryAgent(BaseAgent):
    """库存Agent - 专门处理库存管理、优化和预警"""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="库存管理助手",
            description="专门处理库存数据分析、库存优化、补货预警和供应链管理",
            capabilities=[
                AgentCapability.DATA_ANALYSIS,
                AgentCapability.REAL_TIME_PROCESSING,
                AgentCapability.REASONING,
                AgentCapability.PLANNING,
                AgentCapability.NATURAL_LANGUAGE
            ],
            **kwargs
        )
    
    async def process_message(
        self,
        message: str,
        context: AgentContext,
        **kwargs
    ) -> AgentMessage:
        """处理库存相关消息"""
        
        # 识别库存查询类型
        query_type = self._identify_inventory_query(message)
        
        # 搜索相关库存数据
        knowledge = await self.search_knowledge(
            query=message,
            collection_name="inventory_data",
            n_results=5
        )
        
        # 构建库存分析提示
        analysis_prompt = self._build_inventory_prompt(
            message, query_type, knowledge, context
        )
        
        # 生成分析结果
        analysis_result = await self.generate_response(
            prompt=analysis_prompt,
            context=context,
            temperature=0.1,  # 极低温度确保库存数据准确性
            max_tokens=2000
        )
        
        # 生成库存可视化建议
        chart_suggestions = self._generate_inventory_charts(query_type)
        
        # 检查是否需要紧急预警
        alerts = self._check_inventory_alerts(knowledge)
        
        return AgentMessage(
            role="assistant",
            content=analysis_result,
            metadata={
                "query_type": query_type,
                "data_sources": len(knowledge),
                "chart_suggestions": chart_suggestions,
                "alerts": alerts,
                "urgency_level": self._calculate_urgency(alerts)
            }
        )
    
    async def execute_task(
        self,
        task: AgentTask,
        context: AgentContext,
        **kwargs
    ) -> AgentTask:
        """执行库存管理任务"""
        
        task_type = task.metadata.get("task_type", "inventory_analysis")
        
        try:
            if task_type == "stock_level_check":
                result = await self._check_stock_levels(task, context)
            elif task_type == "reorder_optimization":
                result = await self._optimize_reorder_points(task, context)
            elif task_type == "turnover_analysis":
                result = await self._analyze_inventory_turnover(task, context)
            elif task_type == "demand_forecast":
                result = await self._forecast_demand(task, context)
            elif task_type == "abc_analysis":
                result = await self._perform_abc_analysis(task, context)
            elif task_type == "deadstock_identification":
                result = await self._identify_deadstock(task, context)
            else:
                result = await self._general_inventory_analysis(task, context)
            
            task.output_data = result
            
        except Exception as e:
            logger.error(f"❌ 库存管理任务执行失败: {e}")
            task.output_data = {
                "error": str(e),
                "task_type": task_type
            }
            raise
        
        return task
    
    def _identify_inventory_query(self, message: str) -> str:
        """识别库存查询类型"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["库存", "存货", "stock", "inventory"]):
            if any(word in message_lower for word in ["缺货", "断货", "out of stock"]):
                return "stockout"
            elif any(word in message_lower for word in ["补货", "采购", "reorder"]):
                return "reorder"
            elif any(word in message_lower for word in ["周转", "turnover", "流转"]):
                return "turnover"
            elif any(word in message_lower for word in ["预警", "alert", "warning"]):
                return "alert"
            elif any(word in message_lower for word in ["优化", "optimize", "改善"]):
                return "optimization"
            else:
                return "status"
        elif any(word in message_lower for word in ["需求", "demand", "预测"]):
            return "demand_forecast"
        elif any(word in message_lower for word in ["滞销", "死库存", "deadstock"]):
            return "deadstock"
        elif any(word in message_lower for word in ["abc分析", "abc analysis"]):
            return "abc_analysis"
        else:
            return "general"
    
    def _build_inventory_prompt(
        self,
        message: str,
        query_type: str,
        knowledge: List[Dict[str, Any]],
        context: AgentContext
    ) -> str:
        """构建库存分析提示"""
        
        base_prompt = f"""
作为沃尔玛的专业库存管理专家，请基于以下信息分析库存情况：

用户问题：{message}
分析类型：{query_type}

相关库存数据：
"""
        
        # 添加知识库内容
        for i, kb_item in enumerate(knowledge[:3]):
            base_prompt += f"\n{i+1}. {kb_item['content'][:400]}...\n"
        
        # 根据查询类型添加专业指导
        type_guidance = {
            "stockout": """
请重点分析缺货情况：
- 缺货商品清单和影响评估
- 缺货原因分析
- 紧急补货建议
- 预防措施制定
- 损失评估和挽回策略
""",
            "reorder": """
请分析补货策略：
- 当前补货点设置合理性
- 最优订货量计算
- 供应商交货周期分析
- 季节性需求考虑
- 成本效益优化
""",
            "turnover": """
请分析库存周转情况：
- 各品类周转率对比
- 快慢周转商品识别
- 周转率改善建议
- 资金占用优化
- 仓储效率提升
""",
            "alert": """
请提供库存预警分析：
- 当前预警商品清单
- 预警级别和紧急程度
- 预警原因和趋势分析
- 应对措施建议
- 预警系统优化建议
""",
            "optimization": """
请提供库存优化方案：
- 库存结构分析
- 优化机会识别
- 成本节约潜力评估
- 实施路径和时间表
- 风险评估和应对
""",
            "demand_forecast": """
请进行需求预测分析：
- 历史需求模式分析
- 未来需求预测
- 影响因素识别
- 预测准确性评估
- 库存规划建议
"""
        }
        
        base_prompt += type_guidance.get(query_type, """
请提供全面的库存分析，包括：
- 当前库存状态概述
- 关键问题识别
- 风险评估
- 优化建议
- 执行计划
""")
        
        base_prompt += """
请确保分析结果：
1. 数据准确，逻辑清晰
2. 突出紧急和重要事项
3. 提供具体的数量和时间
4. 包含成本效益分析
5. 考虑沃尔玛的规模和特点

请用中文回答，保持专业和紧迫感。
"""
        
        return base_prompt
    
    def _generate_inventory_charts(self, query_type: str) -> List[Dict[str, str]]:
        """生成库存图表建议"""
        chart_mapping = {
            "stockout": [
                {"type": "bar", "title": "缺货商品统计", "description": "各品类缺货商品数量"},
                {"type": "timeline", "title": "缺货时间线", "description": "缺货发生时间和持续时长"}
            ],
            "reorder": [
                {"type": "scatter", "title": "补货点优化图", "description": "当前vs建议补货点对比"},
                {"type": "line", "title": "补货周期分析", "description": "历史补货周期趋势"}
            ],
            "turnover": [
                {"type": "bar", "title": "库存周转率对比", "description": "各品类周转率表现"},
                {"type": "heatmap", "title": "周转率热力图", "description": "商品周转情况分布"}
            ],
            "alert": [
                {"type": "gauge", "title": "库存预警仪表盘", "description": "各级别预警数量"},
                {"type": "treemap", "title": "预警商品分布", "description": "按品类显示预警商品"}
            ],
            "optimization": [
                {"type": "sankey", "title": "库存流向图", "description": "库存流转和优化路径"},
                {"type": "waterfall", "title": "成本节约瀑布图", "description": "优化带来的成本变化"}
            ]
        }
        
        return chart_mapping.get(query_type, [
            {"type": "bar", "title": "库存状态图", "description": "基础库存数据可视化"}
        ])
    
    def _check_inventory_alerts(self, knowledge: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """检查库存预警"""
        alerts = []
        
        # 模拟预警检查
        sample_alerts = [
            {
                "type": "low_stock",
                "severity": "high",
                "product": "iPhone 15 Pro",
                "current_stock": 25,
                "reorder_point": 50,
                "message": "iPhone 15 Pro库存严重不足，需要紧急补货"
            },
            {
                "type": "overstock",
                "severity": "medium", 
                "product": "冬季外套",
                "current_stock": 1500,
                "normal_stock": 500,
                "message": "冬季外套库存过多，建议促销清理"
            },
            {
                "type": "slow_moving",
                "severity": "low",
                "product": "DVD播放器",
                "days_no_sale": 45,
                "message": "DVD播放器45天无销售，考虑下架"
            }
        ]
        
        return sample_alerts
    
    def _calculate_urgency(self, alerts: List[Dict[str, Any]]) -> str:
        """计算紧急程度"""
        if not alerts:
            return "normal"
        
        high_severity_count = sum(1 for alert in alerts if alert.get("severity") == "high")
        
        if high_severity_count > 0:
            return "urgent"
        elif len(alerts) > 3:
            return "high"
        else:
            return "medium"
    
    async def _check_stock_levels(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """检查库存水平"""
        return {
            "analysis_type": "stock_level_check",
            "timestamp": datetime.now().isoformat(),
            "overall_status": "需要关注",
            "total_skus": 45000,
            "stock_status": {
                "in_stock": 42500,
                "low_stock": 2000,
                "out_of_stock": 500
            },
            "category_breakdown": {
                "Electronics": {"total": 12000, "low_stock": 800, "out_of_stock": 150},
                "Groceries": {"total": 18000, "low_stock": 600, "out_of_stock": 200},
                "Clothing": {"total": 15000, "low_stock": 600, "out_of_stock": 150}
            },
            "urgent_actions": [
                "立即补货缺货商品500个SKU",
                "优先处理电子产品低库存预警",
                "联系供应商确认交货时间"
            ]
        }
    
    async def _optimize_reorder_points(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """优化补货点"""
        return {
            "analysis_type": "reorder_optimization",
            "optimization_results": {
                "total_skus_analyzed": 45000,
                "optimization_candidates": 8500,
                "potential_savings": 2500000,
                "service_level_improvement": 0.03
            },
            "recommendations": [
                {
                    "category": "Electronics",
                    "current_reorder_point": 100,
                    "optimized_reorder_point": 85,
                    "savings": 450000
                },
                {
                    "category": "Groceries", 
                    "current_reorder_point": 200,
                    "optimized_reorder_point": 180,
                    "savings": 320000
                }
            ],
            "implementation_plan": [
                "阶段1：试点高价值商品优化",
                "阶段2：扩展到所有品类",
                "阶段3：建立动态调整机制"
            ]
        }
    
    async def _analyze_inventory_turnover(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """分析库存周转"""
        return {
            "analysis_type": "turnover_analysis",
            "overall_turnover": 8.2,
            "category_turnover": {
                "Electronics": {"turnover": 12.5, "status": "优秀", "trend": "上升"},
                "Groceries": {"turnover": 15.8, "status": "优秀", "trend": "稳定"},
                "Clothing": {"turnover": 6.2, "status": "一般", "trend": "下降"},
                "Home & Garden": {"turnover": 4.8, "status": "需改善", "trend": "下降"}
            },
            "slow_movers": [
                {"product": "大型家电", "turnover": 2.1, "action": "促销清理"},
                {"product": "季节性商品", "turnover": 1.8, "action": "调整采购策略"}
            ],
            "improvement_opportunities": [
                "优化服装类目采购策略",
                "加强家居园艺营销推广",
                "调整慢周转商品定价"
            ]
        }
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """
你是沃尔玛的专业库存管理专家，具有丰富的供应链和库存优化经验。

你的专长包括：
- 库存水平监控和预警
- 补货策略优化
- 库存周转率分析
- 需求预测和规划
- 死库存识别和处理
- ABC分析和分类管理
- 供应链协调

请始终以数据为准，提供准确的库存分析和实用的优化建议。
注重成本效益和服务水平的平衡，确保库存管理既高效又经济。
"""
    
    def _get_relevant_keywords(self) -> List[str]:
        """获取相关关键词"""
        return [
            "库存", "存货", "stock", "inventory",
            "缺货", "断货", "补货", "采购", "reorder",
            "周转", "turnover", "流转", "轮转",
            "预警", "alert", "warning", "监控",
            "优化", "optimize", "改善", "提升",
            "需求", "demand", "预测", "forecast",
            "滞销", "死库存", "deadstock", "慢周转",
            "安全库存", "最小库存", "最大库存",
            "供应商", "交货", "lead time", "周期"
        ]
    
    def _get_default_collection(self) -> str:
        """获取默认知识库集合名"""
        return "inventory_data"
