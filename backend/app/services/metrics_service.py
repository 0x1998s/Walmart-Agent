# 🛒 沃尔玛AI Agent平台 - 指标评估服务
# Walmart AI Agent Platform - Metrics Service

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.metrics import Metrics, MetricType
from app.models.agent import Agent
from app.models.task import Task

logger = logging.getLogger(__name__)


class MetricsService:
    """指标评估服务 - 监控和评估算法应用效果"""
    
    def __init__(self):
        self.metric_collectors = {}
        self.alert_thresholds = {
            MetricType.RESPONSE_TIME: 5.0,  # 5秒
            MetricType.SUCCESS_RATE: 0.8,   # 80%
            MetricType.ERROR_RATE: 0.2,     # 20%
            MetricType.ACCURACY: 0.7,       # 70%
        }
        
    async def record_metric(
        self,
        metric_name: str,
        metric_type: MetricType,
        value: float,
        unit: Optional[str] = None,
        agent_id: Optional[UUID] = None,
        task_id: Optional[UUID] = None,
        timestamp: Optional[datetime] = None
    ) -> bool:
        """记录指标"""
        try:
            async with AsyncSessionLocal() as session:
                metric = Metrics(
                    metric_name=metric_name,
                    metric_type=metric_type,
                    value=value,
                    unit=unit,
                    timestamp=timestamp or datetime.now(),
                    agent_id=agent_id,
                    task_id=task_id
                )
                
                session.add(metric)
                await session.commit()
                
                logger.info(f"✅ 记录指标: {metric_name} = {value} {unit or ''}")
                
                # 检查告警阈值
                await self._check_alert_threshold(metric_name, metric_type, value)
                
                return True
                
        except Exception as e:
            logger.error(f"❌ 记录指标失败: {e}")
            return False
    
    async def get_agent_metrics(
        self,
        agent_id: UUID,
        metric_types: Optional[List[MetricType]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取Agent指标"""
        try:
            async with AsyncSessionLocal() as session:
                query = session.query(Metrics).filter(Metrics.agent_id == agent_id)
                
                if metric_types:
                    query = query.filter(Metrics.metric_type.in_(metric_types))
                
                if start_time:
                    query = query.filter(Metrics.timestamp >= start_time)
                
                if end_time:
                    query = query.filter(Metrics.timestamp <= end_time)
                
                query = query.order_by(Metrics.timestamp.desc()).limit(limit)
                
                result = await session.execute(query)
                metrics = result.scalars().all()
                
                return [
                    {
                        "id": str(metric.id),
                        "metric_name": metric.metric_name,
                        "metric_type": metric.metric_type,
                        "value": metric.value,
                        "unit": metric.unit,
                        "timestamp": metric.timestamp.isoformat(),
                        "agent_id": str(metric.agent_id) if metric.agent_id else None,
                        "task_id": str(metric.task_id) if metric.task_id else None
                    }
                    for metric in metrics
                ]
                
        except Exception as e:
            logger.error(f"❌ 获取Agent指标失败: {e}")
            return []
    
    async def calculate_agent_performance(
        self,
        agent_id: UUID,
        time_period: timedelta = timedelta(days=7)
    ) -> Dict[str, Any]:
        """计算Agent性能指标"""
        try:
            end_time = datetime.now()
            start_time = end_time - time_period
            
            async with AsyncSessionLocal() as session:
                # 响应时间统计
                response_time_query = session.query(
                    func.avg(Metrics.value).label('avg_response_time'),
                    func.min(Metrics.value).label('min_response_time'),
                    func.max(Metrics.value).label('max_response_time'),
                    func.count(Metrics.id).label('count')
                ).filter(
                    and_(
                        Metrics.agent_id == agent_id,
                        Metrics.metric_type == MetricType.RESPONSE_TIME,
                        Metrics.timestamp >= start_time,
                        Metrics.timestamp <= end_time
                    )
                )
                
                response_time_result = await session.execute(response_time_query)
                response_time_stats = response_time_result.first()
                
                # 成功率统计
                success_rate_query = session.query(
                    func.avg(Metrics.value).label('avg_success_rate')
                ).filter(
                    and_(
                        Metrics.agent_id == agent_id,
                        Metrics.metric_type == MetricType.SUCCESS_RATE,
                        Metrics.timestamp >= start_time,
                        Metrics.timestamp <= end_time
                    )
                )
                
                success_rate_result = await session.execute(success_rate_query)
                success_rate_stats = success_rate_result.first()
                
                # 错误率统计
                error_rate_query = session.query(
                    func.avg(Metrics.value).label('avg_error_rate')
                ).filter(
                    and_(
                        Metrics.agent_id == agent_id,
                        Metrics.metric_type == MetricType.ERROR_RATE,
                        Metrics.timestamp >= start_time,
                        Metrics.timestamp <= end_time
                    )
                )
                
                error_rate_result = await session.execute(error_rate_query)
                error_rate_stats = error_rate_result.first()
                
                # 准确率统计
                accuracy_query = session.query(
                    func.avg(Metrics.value).label('avg_accuracy')
                ).filter(
                    and_(
                        Metrics.agent_id == agent_id,
                        Metrics.metric_type == MetricType.ACCURACY,
                        Metrics.timestamp >= start_time,
                        Metrics.timestamp <= end_time
                    )
                )
                
                accuracy_result = await session.execute(accuracy_query)
                accuracy_stats = accuracy_result.first()
                
                return {
                    "agent_id": str(agent_id),
                    "time_period": {
                        "start": start_time.isoformat(),
                        "end": end_time.isoformat(),
                        "days": time_period.days
                    },
                    "response_time": {
                        "avg": float(response_time_stats.avg_response_time or 0),
                        "min": float(response_time_stats.min_response_time or 0),
                        "max": float(response_time_stats.max_response_time or 0),
                        "count": response_time_stats.count or 0,
                        "unit": "seconds"
                    },
                    "success_rate": {
                        "avg": float(success_rate_stats.avg_success_rate or 0),
                        "unit": "percentage"
                    },
                    "error_rate": {
                        "avg": float(error_rate_stats.avg_error_rate or 0),
                        "unit": "percentage"
                    },
                    "accuracy": {
                        "avg": float(accuracy_stats.avg_accuracy or 0),
                        "unit": "percentage"
                    }
                }
                
        except Exception as e:
            logger.error(f"❌ 计算Agent性能指标失败: {e}")
            return {}
    
    async def get_system_metrics(
        self,
        time_period: timedelta = timedelta(hours=24)
    ) -> Dict[str, Any]:
        """获取系统整体指标"""
        try:
            end_time = datetime.now()
            start_time = end_time - time_period
            
            async with AsyncSessionLocal() as session:
                # 总请求数
                total_requests_query = session.query(
                    func.count(Metrics.id).label('total_requests')
                ).filter(
                    and_(
                        Metrics.metric_type == MetricType.THROUGHPUT,
                        Metrics.timestamp >= start_time,
                        Metrics.timestamp <= end_time
                    )
                )
                
                total_requests_result = await session.execute(total_requests_query)
                total_requests = total_requests_result.scalar() or 0
                
                # 平均响应时间
                avg_response_time_query = session.query(
                    func.avg(Metrics.value).label('avg_response_time')
                ).filter(
                    and_(
                        Metrics.metric_type == MetricType.RESPONSE_TIME,
                        Metrics.timestamp >= start_time,
                        Metrics.timestamp <= end_time
                    )
                )
                
                avg_response_time_result = await session.execute(avg_response_time_query)
                avg_response_time = avg_response_time_result.scalar() or 0
                
                # 系统成功率
                system_success_rate_query = session.query(
                    func.avg(Metrics.value).label('avg_success_rate')
                ).filter(
                    and_(
                        Metrics.metric_type == MetricType.SUCCESS_RATE,
                        Metrics.timestamp >= start_time,
                        Metrics.timestamp <= end_time
                    )
                )
                
                system_success_rate_result = await session.execute(system_success_rate_query)
                system_success_rate = system_success_rate_result.scalar() or 0
                
                # 活跃Agent数量
                active_agents_query = session.query(
                    func.count(Agent.id).label('active_agents')
                ).filter(Agent.is_active == True)
                
                active_agents_result = await session.execute(active_agents_query)
                active_agents = active_agents_result.scalar() or 0
                
                # 今日完成任务数
                completed_tasks_query = session.query(
                    func.count(Task.id).label('completed_tasks')
                ).filter(
                    and_(
                        Task.status == 'completed',
                        Task.completed_at >= start_time,
                        Task.completed_at <= end_time
                    )
                )
                
                completed_tasks_result = await session.execute(completed_tasks_query)
                completed_tasks = completed_tasks_result.scalar() or 0
                
                return {
                    "timestamp": end_time.isoformat(),
                    "time_period": {
                        "start": start_time.isoformat(),
                        "end": end_time.isoformat(),
                        "hours": time_period.total_seconds() / 3600
                    },
                    "system_performance": {
                        "total_requests": total_requests,
                        "avg_response_time": float(avg_response_time),
                        "success_rate": float(system_success_rate),
                        "active_agents": active_agents,
                        "completed_tasks": completed_tasks
                    },
                    "health_status": self._calculate_health_status(
                        float(avg_response_time),
                        float(system_success_rate)
                    )
                }
                
        except Exception as e:
            logger.error(f"❌ 获取系统指标失败: {e}")
            return {}
    
    async def generate_performance_report(
        self,
        agent_ids: Optional[List[UUID]] = None,
        time_period: timedelta = timedelta(days=7)
    ) -> Dict[str, Any]:
        """生成性能报告"""
        try:
            report = {
                "report_id": str(datetime.now().timestamp()),
                "generated_at": datetime.now().isoformat(),
                "time_period": {
                    "days": time_period.days,
                    "start": (datetime.now() - time_period).isoformat(),
                    "end": datetime.now().isoformat()
                },
                "system_overview": await self.get_system_metrics(time_period),
                "agent_performance": []
            }
            
            # 如果指定了Agent，只分析指定的Agent
            if agent_ids:
                target_agents = agent_ids
            else:
                # 获取所有活跃Agent
                async with AsyncSessionLocal() as session:
                    agents_query = session.query(Agent.id).filter(Agent.is_active == True)
                    agents_result = await session.execute(agents_query)
                    target_agents = [agent.id for agent in agents_result.scalars().all()]
            
            # 生成每个Agent的性能报告
            for agent_id in target_agents:
                agent_performance = await self.calculate_agent_performance(agent_id, time_period)
                if agent_performance:
                    report["agent_performance"].append(agent_performance)
            
            # 生成洞察和建议
            report["insights"] = await self._generate_insights(report)
            report["recommendations"] = await self._generate_recommendations(report)
            
            return report
            
        except Exception as e:
            logger.error(f"❌ 生成性能报告失败: {e}")
            return {}
    
    async def _check_alert_threshold(
        self,
        metric_name: str,
        metric_type: MetricType,
        value: float
    ):
        """检查告警阈值"""
        try:
            threshold = self.alert_thresholds.get(metric_type)
            if threshold is None:
                return
            
            alert_triggered = False
            alert_message = ""
            
            if metric_type in [MetricType.RESPONSE_TIME, MetricType.ERROR_RATE]:
                # 这些指标值越低越好
                if value > threshold:
                    alert_triggered = True
                    alert_message = f"指标 {metric_name} 超过阈值: {value} > {threshold}"
            
            elif metric_type in [MetricType.SUCCESS_RATE, MetricType.ACCURACY]:
                # 这些指标值越高越好
                if value < threshold:
                    alert_triggered = True
                    alert_message = f"指标 {metric_name} 低于阈值: {value} < {threshold}"
            
            if alert_triggered:
                logger.warning(f"⚠️ 告警触发: {alert_message}")
                # 这里可以发送邮件、短信等告警通知
                await self._send_alert(metric_name, metric_type, value, threshold, alert_message)
                
        except Exception as e:
            logger.error(f"❌ 检查告警阈值失败: {e}")
    
    async def _send_alert(
        self,
        metric_name: str,
        metric_type: MetricType,
        value: float,
        threshold: float,
        message: str
    ):
        """发送告警（可以扩展为邮件、短信等）"""
        # 这里可以集成邮件服务、短信服务、钉钉、企业微信等
        logger.warning(f"📢 告警通知: {message}")
    
    def _calculate_health_status(
        self,
        avg_response_time: float,
        success_rate: float
    ) -> str:
        """计算系统健康状态"""
        if avg_response_time > 10 or success_rate < 0.5:
            return "critical"
        elif avg_response_time > 5 or success_rate < 0.8:
            return "warning"
        else:
            return "healthy"
    
    async def _generate_insights(self, report: Dict[str, Any]) -> List[str]:
        """生成洞察"""
        insights = []
        
        try:
            system_performance = report.get("system_overview", {}).get("system_performance", {})
            avg_response_time = system_performance.get("avg_response_time", 0)
            success_rate = system_performance.get("success_rate", 0)
            
            if avg_response_time > 3:
                insights.append(f"系统平均响应时间为 {avg_response_time:.2f} 秒，建议优化性能")
            
            if success_rate < 0.9:
                insights.append(f"系统成功率为 {success_rate:.1%}，需要关注错误处理")
            
            # 分析Agent性能差异
            agent_performances = report.get("agent_performance", [])
            if len(agent_performances) > 1:
                response_times = [ap.get("response_time", {}).get("avg", 0) for ap in agent_performances]
                max_rt = max(response_times)
                min_rt = min(response_times)
                
                if max_rt > min_rt * 2:
                    insights.append("Agent间性能差异较大，建议优化负载均衡")
            
        except Exception as e:
            logger.error(f"❌ 生成洞察失败: {e}")
        
        return insights
    
    async def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        try:
            system_performance = report.get("system_overview", {}).get("system_performance", {})
            health_status = report.get("system_overview", {}).get("health_status", "unknown")
            
            if health_status == "critical":
                recommendations.extend([
                    "立即检查系统资源使用情况",
                    "考虑扩容或优化关键组件",
                    "启用降级策略保障基本服务"
                ])
            elif health_status == "warning":
                recommendations.extend([
                    "监控系统负载趋势",
                    "优化高频操作的性能",
                    "准备扩容预案"
                ])
            
            # 基于Agent性能给出建议
            agent_performances = report.get("agent_performance", [])
            for ap in agent_performances:
                response_time = ap.get("response_time", {}).get("avg", 0)
                if response_time > 5:
                    recommendations.append(f"Agent {ap.get('agent_id', 'unknown')} 响应时间过长，建议优化")
            
        except Exception as e:
            logger.error(f"❌ 生成建议失败: {e}")
        
        return recommendations
    
    async def set_alert_threshold(
        self,
        metric_type: MetricType,
        threshold: float
    ) -> bool:
        """设置告警阈值"""
        try:
            self.alert_thresholds[metric_type] = threshold
            logger.info(f"✅ 设置告警阈值: {metric_type} = {threshold}")
            return True
        except Exception as e:
            logger.error(f"❌ 设置告警阈值失败: {e}")
            return False
    
    async def get_alert_thresholds(self) -> Dict[str, float]:
        """获取告警阈值"""
        return {metric_type.value: threshold for metric_type, threshold in self.alert_thresholds.items()}
