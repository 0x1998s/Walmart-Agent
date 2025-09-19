# 🛒 沃尔玛AI Agent平台 - 销售Agent
# Walmart AI Agent Platform - Sales Agent

import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from app.agents.base_agent import BaseAgent, AgentCapability, AgentContext, AgentMessage, AgentTask

logger = logging.getLogger(__name__)


class SalesAgent(BaseAgent):
    """销售Agent - 专门处理销售相关分析和预测"""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="销售分析助手",
            description="专门处理销售数据分析、预测、报告生成和销售策略优化",
            capabilities=[
                AgentCapability.DATA_ANALYSIS,
                AgentCapability.NATURAL_LANGUAGE,
                AgentCapability.REASONING,
                AgentCapability.PLANNING,
                AgentCapability.REAL_TIME_PROCESSING
            ],
            **kwargs
        )
    
    async def process_message(
        self,
        message: str,
        context: AgentContext,
        **kwargs
    ) -> AgentMessage:
        """处理销售相关消息"""
        
        # 识别销售查询类型
        query_type = self._identify_sales_query(message)
        
        # 搜索相关销售数据
        knowledge = await self.search_knowledge(
            query=message,
            collection_name="sales_reports",
            n_results=5
        )
        
        # 构建销售分析提示
        analysis_prompt = self._build_sales_prompt(
            message, query_type, knowledge, context
        )
        
        # 生成分析结果
        analysis_result = await self.generate_response(
            prompt=analysis_prompt,
            context=context,
            temperature=0.2,  # 较低温度确保数据准确性
            max_tokens=2000
        )
        
        # 生成可视化建议
        chart_suggestions = self._generate_sales_charts(query_type)
        
        return AgentMessage(
            role="assistant",
            content=analysis_result,
            metadata={
                "query_type": query_type,
                "data_sources": len(knowledge),
                "chart_suggestions": chart_suggestions,
                "analysis_confidence": self._calculate_confidence(knowledge)
            }
        )
    
    async def execute_task(
        self,
        task: AgentTask,
        context: AgentContext,
        **kwargs
    ) -> AgentTask:
        """执行销售分析任务"""
        
        task_type = task.metadata.get("task_type", "sales_analysis")
        
        try:
            if task_type == "revenue_analysis":
                result = await self._analyze_revenue(task, context)
            elif task_type == "sales_forecast":
                result = await self._forecast_sales(task, context)
            elif task_type == "performance_report":
                result = await self._generate_performance_report(task, context)
            elif task_type == "conversion_analysis":
                result = await self._analyze_conversion(task, context)
            elif task_type == "regional_analysis":
                result = await self._analyze_regional_performance(task, context)
            else:
                result = await self._general_sales_analysis(task, context)
            
            task.output_data = result
            
        except Exception as e:
            logger.error(f"❌ 销售分析任务执行失败: {e}")
            task.output_data = {
                "error": str(e),
                "task_type": task_type
            }
            raise
        
        return task
    
    def _identify_sales_query(self, message: str) -> str:
        """识别销售查询类型"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["营收", "收入", "revenue"]):
            return "revenue"
        elif any(word in message_lower for word in ["预测", "forecast", "预估"]):
            return "forecast"
        elif any(word in message_lower for word in ["转化", "conversion", "转化率"]):
            return "conversion"
        elif any(word in message_lower for word in ["区域", "地区", "regional"]):
            return "regional"
        elif any(word in message_lower for word in ["绩效", "performance", "表现"]):
            return "performance"
        elif any(word in message_lower for word in ["增长", "growth", "同比"]):
            return "growth"
        elif any(word in message_lower for word in ["漏斗", "funnel", "流程"]):
            return "funnel"
        else:
            return "general"
    
    def _build_sales_prompt(
        self,
        message: str,
        query_type: str,
        knowledge: List[Dict[str, Any]],
        context: AgentContext
    ) -> str:
        """构建销售分析提示"""
        
        base_prompt = f"""
作为沃尔玛的专业销售分析师，请基于以下信息分析销售数据：

用户问题：{message}
分析类型：{query_type}

相关销售数据：
"""
        
        # 添加知识库内容
        for i, kb_item in enumerate(knowledge[:3]):
            base_prompt += f"\n{i+1}. {kb_item['content'][:400]}...\n"
        
        # 根据查询类型添加专业指导
        type_guidance = {
            "revenue": """
请从以下角度分析营收：
- 总营收和增长趋势
- 各产品线营收贡献
- 季节性影响因素
- 营收质量分析
- 提升建议
""",
            "forecast": """
请进行销售预测分析：
- 历史数据趋势分析
- 季节性和周期性模式
- 市场因素影响评估
- 预测模型和置信区间
- 风险因素识别
""",
            "conversion": """
请分析转化率情况：
- 各渠道转化率对比
- 转化漏斗分析
- 影响转化的关键因素
- 优化建议
- 预期效果评估
""",
            "regional": """
请进行区域销售分析：
- 各区域销售表现对比
- 区域特色和差异分析
- 市场渗透率评估
- 区域策略建议
- 资源配置优化
""",
            "performance": """
请分析销售绩效：
- KPI达成情况
- 销售团队表现
- 产品表现排名
- 改进机会识别
- 激励策略建议
"""
        }
        
        base_prompt += type_guidance.get(query_type, """
请提供全面的销售分析，包括：
- 现状概述
- 关键指标分析
- 趋势识别
- 问题诊断
- 改进建议
""")
        
        base_prompt += """
请确保分析结果：
1. 数据驱动，有理有据
2. 结构清晰，重点突出
3. 包含具体的数字和比例
4. 提供可执行的建议
5. 考虑沃尔玛的业务特点

请用中文回答，保持专业客观的分析风格。
"""
        
        return base_prompt
    
    def _generate_sales_charts(self, query_type: str) -> List[Dict[str, str]]:
        """生成销售图表建议"""
        chart_mapping = {
            "revenue": [
                {"type": "line", "title": "营收趋势图", "description": "展示营收随时间变化"},
                {"type": "waterfall", "title": "营收构成瀑布图", "description": "分析营收来源构成"},
                {"type": "bar", "title": "产品线营收对比", "description": "各产品线营收表现"}
            ],
            "forecast": [
                {"type": "line", "title": "销售预测图", "description": "历史数据与预测趋势"},
                {"type": "area", "title": "置信区间图", "description": "预测的不确定性范围"}
            ],
            "conversion": [
                {"type": "funnel", "title": "转化漏斗图", "description": "各阶段转化情况"},
                {"type": "bar", "title": "渠道转化率对比", "description": "不同渠道转化效果"}
            ],
            "regional": [
                {"type": "map", "title": "区域销售地图", "description": "地理分布销售热力图"},
                {"type": "radar", "title": "区域表现雷达图", "description": "多维度区域对比"}
            ],
            "performance": [
                {"type": "gauge", "title": "KPI达成仪表盘", "description": "关键指标完成度"},
                {"type": "scatter", "title": "绩效分布图", "description": "销售人员/产品绩效分布"}
            ]
        }
        
        return chart_mapping.get(query_type, [
            {"type": "bar", "title": "销售数据对比图", "description": "基础销售数据可视化"}
        ])
    
    async def _analyze_revenue(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """营收分析"""
        return {
            "analysis_type": "revenue",
            "period": task.input_data.get("period", "Q4_2024"),
            "revenue_metrics": {
                "total_revenue": 2800000000,
                "growth_rate": 0.12,
                "gross_margin": 0.25,
                "net_margin": 0.08
            },
            "revenue_breakdown": {
                "Electronics": {"revenue": 980000000, "growth": 0.18},
                "Groceries": {"revenue": 1200000000, "growth": 0.08},
                "Clothing": {"revenue": 620000000, "growth": 0.15}
            },
            "insights": [
                "电子产品营收增长强劲，达到18%",
                "食品杂货保持稳定增长",
                "服装类目表现超出预期"
            ],
            "recommendations": [
                "加大电子产品营销投入",
                "优化食品杂货供应链",
                "扩展服装品类选择"
            ]
        }
    
    async def _forecast_sales(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """销售预测"""
        return {
            "analysis_type": "forecast",
            "forecast_period": task.input_data.get("forecast_days", 90),
            "predictions": {
                "next_month": {
                    "revenue": 950000000,
                    "confidence": 0.85,
                    "range": {"min": 900000000, "max": 1000000000}
                },
                "next_quarter": {
                    "revenue": 2850000000,
                    "confidence": 0.78,
                    "range": {"min": 2700000000, "max": 3000000000}
                }
            },
            "factors": [
                "季节性需求增长",
                "新产品线推出",
                "市场竞争加剧",
                "经济环境影响"
            ],
            "risks": [
                "供应链中断风险",
                "消费者信心下降",
                "原材料价格上涨"
            ],
            "recommendations": [
                "加强库存管理",
                "多元化供应商",
                "灵活定价策略"
            ]
        }
    
    async def _generate_performance_report(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """生成绩效报告"""
        return {
            "analysis_type": "performance",
            "report_period": task.input_data.get("period", "monthly"),
            "kpi_achievement": {
                "revenue_target": {"achieved": 0.95, "target": 1000000000},
                "growth_target": {"achieved": 1.12, "target": 0.10},
                "margin_target": {"achieved": 0.88, "target": 0.25}
            },
            "top_performers": [
                {"category": "Electronics", "score": 95, "growth": 0.18},
                {"category": "Home & Garden", "score": 88, "growth": 0.14},
                {"category": "Sports", "score": 82, "growth": 0.11}
            ],
            "improvement_areas": [
                {"category": "Automotive", "score": 65, "issues": ["库存不足", "价格竞争"]},
                {"category": "Books", "score": 58, "issues": ["需求下降", "线上竞争"]}
            ],
            "action_items": [
                "优化低绩效品类策略",
                "加强高绩效品类投入",
                "改进库存管理系统"
            ]
        }
    
    def _calculate_confidence(self, knowledge: List[Dict[str, Any]]) -> float:
        """计算分析置信度"""
        if not knowledge:
            return 0.4
        
        avg_score = sum(item.get("score", 0) for item in knowledge) / len(knowledge)
        knowledge_factor = min(len(knowledge) / 5, 1.0)
        
        confidence = (avg_score * 0.6 + knowledge_factor * 0.4)
        return round(confidence, 2)
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """
你是沃尔玛的专业销售分析师，具有丰富的零售销售经验和数据分析能力。

你的专长包括：
- 销售数据深度分析
- 营收预测和建模
- 销售绩效评估
- 转化率优化
- 区域市场分析
- 销售策略制定

请始终基于数据进行客观分析，提供具有商业价值的洞察和建议。
使用专业的销售和零售术语，确保分析结果对业务决策有实际指导意义。
"""
    
    def _get_relevant_keywords(self) -> List[str]:
        """获取相关关键词"""
        return [
            "销售", "营收", "收入", "业绩", "增长",
            "预测", "forecast", "趋势", "同比", "环比",
            "转化", "conversion", "漏斗", "绩效",
            "区域", "渠道", "产品线", "品类",
            "KPI", "目标", "达成", "表现",
            "客单价", "复购", "留存", "获客",
            "毛利", "净利", "利润率", "成本"
        ]
    
    def _get_default_collection(self) -> str:
        """获取默认知识库集合名"""
        return "sales_reports"
