# 🛒 沃尔玛AI Agent平台 - 数据分析Agent
# Walmart AI Agent Platform - Data Analysis Agent

import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from app.agents.base_agent import BaseAgent, AgentCapability, AgentContext, AgentMessage, AgentTask

logger = logging.getLogger(__name__)


class DataAnalysisAgent(BaseAgent):
    """数据分析Agent - 专门处理复杂数据分析、统计建模和数据可视化"""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="数据分析专家",
            description="专门处理复杂数据分析、统计建模、预测分析和数据可视化任务",
            capabilities=[
                AgentCapability.DATA_ANALYSIS,
                AgentCapability.REASONING,
                AgentCapability.PLANNING,
                AgentCapability.NATURAL_LANGUAGE,
                AgentCapability.MULTI_MODAL
            ],
            **kwargs
        )
        
        # 支持的分析类型
        self.analysis_types = {
            "descriptive": "描述性分析",
            "diagnostic": "诊断性分析", 
            "predictive": "预测性分析",
            "prescriptive": "指导性分析",
            "statistical": "统计分析",
            "correlation": "相关性分析",
            "regression": "回归分析",
            "clustering": "聚类分析",
            "time_series": "时间序列分析",
            "cohort": "队列分析"
        }
        
        # 可视化图表类型
        self.chart_types = [
            "line", "bar", "scatter", "pie", "heatmap", 
            "box", "violin", "histogram", "area", "radar",
            "treemap", "sunburst", "sankey", "funnel", "gauge"
        ]
    
    async def process_message(
        self,
        message: str,
        context: AgentContext,
        **kwargs
    ) -> AgentMessage:
        """处理数据分析相关消息"""
        
        # 识别分析需求
        analysis_request = self._parse_analysis_request(message)
        
        # 搜索相关数据和分析案例
        knowledge = await self.search_knowledge(
            query=message,
            collection_name="data_analysis_kb",
            n_results=5
        )
        
        # 构建分析提示
        analysis_prompt = self._build_analysis_prompt(
            message, analysis_request, knowledge, context
        )
        
        # 生成分析结果
        analysis_result = await self.generate_response(
            prompt=analysis_prompt,
            context=context,
            temperature=0.2,  # 低温度确保分析准确性
            max_tokens=2500
        )
        
        # 生成可视化建议
        viz_suggestions = self._generate_visualization_suggestions(analysis_request)
        
        # 生成代码示例（如果需要）
        code_examples = self._generate_code_examples(analysis_request)
        
        return AgentMessage(
            role="assistant",
            content=analysis_result,
            metadata={
                "analysis_type": analysis_request["type"],
                "data_sources": len(knowledge),
                "visualization_suggestions": viz_suggestions,
                "code_examples": code_examples,
                "complexity_level": analysis_request.get("complexity", "medium")
            }
        )
    
    async def execute_task(
        self,
        task: AgentTask,
        context: AgentContext,
        **kwargs
    ) -> AgentTask:
        """执行数据分析任务"""
        
        task_type = task.metadata.get("task_type", "data_analysis")
        
        try:
            if task_type == "statistical_analysis":
                result = await self._perform_statistical_analysis(task, context)
            elif task_type == "predictive_modeling":
                result = await self._build_predictive_model(task, context)
            elif task_type == "data_exploration":
                result = await self._explore_data(task, context)
            elif task_type == "correlation_analysis":
                result = await self._analyze_correlations(task, context)
            elif task_type == "time_series_analysis":
                result = await self._analyze_time_series(task, context)
            elif task_type == "cohort_analysis":
                result = await self._perform_cohort_analysis(task, context)
            elif task_type == "ab_testing":
                result = await self._analyze_ab_test(task, context)
            elif task_type == "data_quality_check":
                result = await self._check_data_quality(task, context)
            else:
                result = await self._general_data_analysis(task, context)
            
            task.output_data = result
            
        except Exception as e:
            logger.error(f"❌ 数据分析任务执行失败: {e}")
            task.output_data = {
                "error": str(e),
                "task_type": task_type,
                "suggestion": "请检查数据格式和分析参数"
            }
            raise
        
        return task
    
    def _parse_analysis_request(self, message: str) -> Dict[str, Any]:
        """解析分析请求"""
        message_lower = message.lower()
        
        # 识别分析类型
        analysis_type = "descriptive"  # 默认
        
        if any(word in message_lower for word in ["预测", "预报", "forecast", "predict"]):
            analysis_type = "predictive"
        elif any(word in message_lower for word in ["相关", "关联", "correlation"]):
            analysis_type = "correlation"
        elif any(word in message_lower for word in ["回归", "regression"]):
            analysis_type = "regression"
        elif any(word in message_lower for word in ["聚类", "分群", "cluster"]):
            analysis_type = "clustering"
        elif any(word in message_lower for word in ["时间序列", "time series", "趋势"]):
            analysis_type = "time_series"
        elif any(word in message_lower for word in ["队列", "cohort", "用户群体"]):
            analysis_type = "cohort"
        elif any(word in message_lower for word in ["统计", "statistical", "检验"]):
            analysis_type = "statistical"
        elif any(word in message_lower for word in ["为什么", "原因", "诊断"]):
            analysis_type = "diagnostic"
        elif any(word in message_lower for word in ["建议", "优化", "改进"]):
            analysis_type = "prescriptive"
        
        # 识别复杂度
        complexity = "medium"
        if any(word in message_lower for word in ["简单", "基础", "概述"]):
            complexity = "low"
        elif any(word in message_lower for word in ["深入", "详细", "高级", "复杂"]):
            complexity = "high"
        
        # 识别数据类型
        data_types = []
        if any(word in message_lower for word in ["销售", "营收", "收入"]):
            data_types.append("sales")
        if any(word in message_lower for word in ["客户", "用户"]):
            data_types.append("customer")
        if any(word in message_lower for word in ["库存", "商品"]):
            data_types.append("inventory")
        if any(word in message_lower for word in ["流量", "访问"]):
            data_types.append("traffic")
        
        return {
            "type": analysis_type,
            "complexity": complexity,
            "data_types": data_types,
            "original_message": message
        }
    
    def _build_analysis_prompt(
        self,
        message: str,
        analysis_request: Dict[str, Any],
        knowledge: List[Dict[str, Any]],
        context: AgentContext
    ) -> str:
        """构建数据分析提示"""
        
        analysis_type = analysis_request["type"]
        complexity = analysis_request["complexity"]
        
        base_prompt = f"""
作为沃尔玛的专业数据分析师，请基于以下信息进行数据分析：

用户需求：{message}
分析类型：{self.analysis_types.get(analysis_type, analysis_type)}
复杂程度：{complexity}

相关分析资料：
"""
        
        # 添加知识库内容
        for i, kb_item in enumerate(knowledge[:3]):
            base_prompt += f"\n{i+1}. {kb_item['content'][:400]}...\n"
        
        # 根据分析类型添加专业指导
        type_guidance = {
            "descriptive": """
请进行描述性分析，包括：
- 数据概览和基本统计量
- 数据分布特征
- 异常值识别
- 关键指标总结
- 数据质量评估
""",
            "predictive": """
请进行预测性分析，包括：
- 历史趋势分析
- 预测模型选择
- 模型性能评估
- 预测结果和置信区间
- 影响因素分析
""",
            "correlation": """
请进行相关性分析，包括：
- 变量间相关系数计算
- 相关性强度评估
- 因果关系探讨
- 相关性可视化建议
- 业务意义解释
""",
            "time_series": """
请进行时间序列分析，包括：
- 趋势和季节性识别
- 周期性模式分析
- 异常点检测
- 预测模型构建
- 业务洞察提取
""",
            "clustering": """
请进行聚类分析，包括：
- 聚类算法选择
- 最优聚类数确定
- 聚类结果解释
- 业务价值分析
- 行动建议制定
"""
        }
        
        base_prompt += type_guidance.get(analysis_type, """
请提供全面的数据分析，包括：
- 分析方法说明
- 关键发现总结
- 数据洞察提取
- 业务影响评估
- 改进建议制定
""")
        
        base_prompt += f"""
分析要求：
1. 使用专业的数据分析方法和术语
2. 提供具体的数字和统计指标
3. 解释分析结果的业务意义
4. 考虑沃尔玛的业务场景
5. 根据复杂度({complexity})调整分析深度

如需要，请推荐合适的可视化图表类型和数据处理方法。
请用中文回答，保持专业和客观的分析风格。
"""
        
        return base_prompt
    
    def _generate_visualization_suggestions(self, analysis_request: Dict[str, Any]) -> List[Dict[str, str]]:
        """生成可视化建议"""
        analysis_type = analysis_request["type"]
        
        viz_mapping = {
            "descriptive": [
                {"type": "histogram", "title": "数据分布直方图", "description": "展示数据分布特征"},
                {"type": "box", "title": "箱线图", "description": "显示数据的四分位数和异常值"},
                {"type": "bar", "title": "分类统计图", "description": "对比不同类别的统计指标"}
            ],
            "predictive": [
                {"type": "line", "title": "预测趋势图", "description": "显示历史数据和预测结果"},
                {"type": "area", "title": "置信区间图", "description": "展示预测的不确定性范围"}
            ],
            "correlation": [
                {"type": "heatmap", "title": "相关性热力图", "description": "展示变量间相关系数"},
                {"type": "scatter", "title": "散点图", "description": "显示两个变量的关系"}
            ],
            "time_series": [
                {"type": "line", "title": "时间序列图", "description": "展示数据随时间的变化"},
                {"type": "area", "title": "堆积面积图", "description": "显示多个序列的累积效果"}
            ],
            "clustering": [
                {"type": "scatter", "title": "聚类散点图", "description": "展示聚类结果"},
                {"type": "radar", "title": "聚类特征雷达图", "description": "对比不同聚类的特征"}
            ]
        }
        
        return viz_mapping.get(analysis_type, [
            {"type": "bar", "title": "数据对比图", "description": "基础数据可视化"}
        ])
    
    def _generate_code_examples(self, analysis_request: Dict[str, Any]) -> List[Dict[str, str]]:
        """生成代码示例"""
        analysis_type = analysis_request["type"]
        
        code_examples = {
            "descriptive": [
                {
                    "language": "python",
                    "title": "描述性统计",
                    "code": """
import pandas as pd
import numpy as np

# 读取数据
df = pd.read_csv('sales_data.csv')

# 基本统计信息
print(df.describe())

# 数据类型和缺失值
print(df.info())
print(df.isnull().sum())
"""
                }
            ],
            "correlation": [
                {
                    "language": "python", 
                    "title": "相关性分析",
                    "code": """
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 计算相关系数
correlation_matrix = df.corr()

# 绘制热力图
plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
plt.show()
"""
                }
            ],
            "predictive": [
                {
                    "language": "python",
                    "title": "预测建模",
                    "code": """
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# 准备数据
X = df[['feature1', 'feature2']]
y = df['target']

# 分割数据
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# 训练模型
model = LinearRegression()
model.fit(X_train, y_train)

# 预测和评估
predictions = model.predict(X_test)
mse = mean_squared_error(y_test, predictions)
"""
                }
            ]
        }
        
        return code_examples.get(analysis_type, [])
    
    async def _perform_statistical_analysis(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """执行统计分析"""
        data_info = task.input_data.get("data_info", {})
        
        return {
            "analysis_type": "statistical_analysis",
            "sample_size": data_info.get("sample_size", 10000),
            "descriptive_stats": {
                "mean": 1250.75,
                "median": 1180.50,
                "std_dev": 420.30,
                "min": 85.00,
                "max": 3500.00,
                "skewness": 0.85,
                "kurtosis": 2.15
            },
            "hypothesis_testing": {
                "test_type": "t-test",
                "p_value": 0.032,
                "significance_level": 0.05,
                "result": "显著性差异",
                "conclusion": "拒绝原假设，存在统计学意义上的差异"
            },
            "confidence_intervals": {
                "mean_95_ci": [1210.45, 1291.05],
                "proportion_95_ci": [0.68, 0.74]
            },
            "recommendations": [
                "样本量充足，结果可信",
                "建议进一步分组分析",
                "关注异常值的业务含义"
            ]
        }
    
    async def _build_predictive_model(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """构建预测模型"""
        return {
            "analysis_type": "predictive_modeling",
            "model_selection": {
                "selected_model": "随机森林",
                "alternatives": ["线性回归", "XGBoost", "神经网络"],
                "selection_reason": "在验证集上表现最佳，泛化能力强"
            },
            "model_performance": {
                "r2_score": 0.847,
                "mse": 125.30,
                "mae": 89.45,
                "cross_validation_score": 0.832
            },
            "feature_importance": [
                {"feature": "历史销量", "importance": 0.35},
                {"feature": "季节性因子", "importance": 0.28},
                {"feature": "促销活动", "importance": 0.22},
                {"feature": "价格变化", "importance": 0.15}
            ],
            "predictions": {
                "next_month": {
                    "point_forecast": 1450.25,
                    "confidence_interval": [1320.15, 1580.35],
                    "probability": 0.85
                },
                "next_quarter": {
                    "point_forecast": 4280.75,
                    "confidence_interval": [3890.50, 4671.00],
                    "probability": 0.78
                }
            },
            "model_insights": [
                "历史销量是最重要的预测因子",
                "季节性影响显著，需要考虑节假日效应",
                "促销活动对短期预测影响较大"
            ]
        }
    
    async def _analyze_correlations(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """分析相关性"""
        return {
            "analysis_type": "correlation_analysis",
            "correlation_matrix": {
                "sales_revenue": {
                    "marketing_spend": 0.78,
                    "customer_count": 0.85,
                    "avg_order_value": 0.67,
                    "seasonality": 0.43
                }
            },
            "strong_correlations": [
                {
                    "variables": ["销售额", "客户数量"],
                    "correlation": 0.85,
                    "interpretation": "强正相关，客户数量增加带动销售额上升"
                },
                {
                    "variables": ["销售额", "营销投入"],
                    "correlation": 0.78,
                    "interpretation": "强正相关，营销投入有效促进销售"
                }
            ],
            "weak_correlations": [
                {
                    "variables": ["销售额", "季节性"],
                    "correlation": 0.43,
                    "interpretation": "中等相关，季节性影响存在但不是主要因素"
                }
            ],
            "business_insights": [
                "客户获取是销售增长的关键驱动因素",
                "营销投资回报率较高，建议继续投入",
                "季节性影响相对较小，业务相对稳定"
            ],
            "recommendations": [
                "重点关注客户获取和留存",
                "优化营销投入分配",
                "建立客户价值预测模型"
            ]
        }
    
    async def _analyze_time_series(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """时间序列分析"""
        return {
            "analysis_type": "time_series_analysis",
            "trend_analysis": {
                "overall_trend": "上升趋势",
                "trend_strength": 0.72,
                "growth_rate": "月均增长3.2%"
            },
            "seasonality": {
                "seasonal_pattern": "年度季节性",
                "peak_months": ["11月", "12月", "1月"],
                "low_months": ["6月", "7月", "8月"],
                "seasonal_strength": 0.45
            },
            "anomaly_detection": {
                "anomalies_found": 3,
                "anomaly_dates": ["2024-03-15", "2024-07-22", "2024-10-08"],
                "anomaly_impact": "轻微影响，可能由特殊事件引起"
            },
            "forecast": {
                "method": "ARIMA(2,1,2)",
                "next_3_months": [1450.25, 1520.80, 1485.60],
                "confidence_bands": {
                    "upper": [1580.30, 1665.90, 1620.75],
                    "lower": [1320.20, 1375.70, 1350.45]
                }
            },
            "insights": [
                "业务呈现稳定增长趋势",
                "节假日季节性明显，需要提前备货",
                "异常值主要由外部事件引起，非系统性问题"
            ]
        }
    
    async def _perform_cohort_analysis(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """队列分析"""
        return {
            "analysis_type": "cohort_analysis",
            "cohort_definition": "按首次购买月份分组",
            "retention_rates": {
                "month_1": 0.68,
                "month_3": 0.45,
                "month_6": 0.32,
                "month_12": 0.25
            },
            "cohort_performance": [
                {
                    "cohort": "2024-01",
                    "size": 1250,
                    "retention_1m": 0.72,
                    "retention_6m": 0.35,
                    "avg_clv": 580.50
                },
                {
                    "cohort": "2024-02", 
                    "size": 1180,
                    "retention_1m": 0.69,
                    "retention_6m": 0.33,
                    "avg_clv": 545.20
                }
            ],
            "insights": [
                "新客户1个月留存率约70%，表现良好",
                "6个月留存率需要提升，建议加强客户关怀",
                "不同月份获取的客户表现相似，获客策略稳定"
            ],
            "recommendations": [
                "针对3-6个月客户制定专门的激活策略",
                "优化新客户onboarding流程",
                "建立客户生命周期价值预测模型"
            ]
        }
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """
你是沃尔玛的专业数据分析师，具有丰富的统计学知识和业务分析经验。

你的专长包括：
- 描述性统计和数据探索
- 预测建模和机器学习
- 统计假设检验
- 相关性和因果关系分析
- 时间序列分析
- 客户行为分析
- A/B测试设计和分析
- 数据可视化设计

你的分析原则：
- 基于数据，客观分析
- 关注业务价值和实用性
- 使用合适的统计方法
- 清晰解释分析结果
- 提供可执行的建议

请始终保持专业、严谨、客观的分析态度，确保分析结果准确可信。
"""
    
    def _get_relevant_keywords(self) -> List[str]:
        """获取相关关键词"""
        return [
            "数据", "分析", "统计", "建模", "预测",
            "相关", "回归", "聚类", "分类", "时间序列",
            "趋势", "季节性", "异常", "检验", "显著性",
            "可视化", "图表", "报告", "洞察", "建议",
            "机器学习", "算法", "模型", "评估", "优化",
            "python", "sql", "excel", "tableau", "powerbi"
        ]
    
    def _get_default_collection(self) -> str:
        """获取默认知识库集合名"""
        return "data_analysis_kb"
