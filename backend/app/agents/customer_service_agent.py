# 🛒 沃尔玛AI Agent平台 - 客户服务Agent
# Walmart AI Agent Platform - Customer Service Agent

import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from app.agents.base_agent import BaseAgent, AgentCapability, AgentContext, AgentMessage, AgentTask

logger = logging.getLogger(__name__)


class CustomerServiceAgent(BaseAgent):
    """客户服务Agent - 专门处理客户服务、投诉处理和客户关系管理"""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="客户服务助手",
            description="专门处理客户咨询、投诉处理、订单问题、退换货服务和客户关系管理",
            capabilities=[
                AgentCapability.NATURAL_LANGUAGE,
                AgentCapability.DOCUMENT_SEARCH,
                AgentCapability.REASONING,
                AgentCapability.REAL_TIME_PROCESSING,
                AgentCapability.WORKFLOW_EXECUTION
            ],
            **kwargs
        )
        
        # 客户服务专用配置
        self.service_categories = {
            "order_inquiry": "订单查询",
            "return_refund": "退换货",
            "product_info": "商品咨询",
            "complaint": "投诉建议",
            "account_issue": "账户问题",
            "payment_issue": "支付问题",
            "delivery_issue": "配送问题",
            "technical_support": "技术支持"
        }
        
        # 常见问题库
        self.faq_database = self._init_faq_database()
    
    async def process_message(
        self,
        message: str,
        context: AgentContext,
        **kwargs
    ) -> AgentMessage:
        """处理客户服务相关消息"""
        
        # 识别服务类型
        service_type = self._identify_service_type(message)
        
        # 检查是否为常见问题
        faq_answer = self._check_faq(message)
        if faq_answer:
            return AgentMessage(
                role="assistant",
                content=faq_answer,
                metadata={
                    "service_type": service_type,
                    "response_type": "faq",
                    "confidence": 0.9
                }
            )
        
        # 搜索相关服务知识
        knowledge = await self.search_knowledge(
            query=message,
            collection_name="customer_service_kb",
            n_results=3
        )
        
        # 构建服务响应提示
        service_prompt = self._build_service_prompt(
            message, service_type, knowledge, context
        )
        
        # 生成服务响应
        service_response = await self.generate_response(
            prompt=service_prompt,
            context=context,
            temperature=0.3,  # 较低温度确保回复准确专业
            max_tokens=1500
        )
        
        # 生成后续行动建议
        next_actions = self._generate_next_actions(service_type, message)
        
        return AgentMessage(
            role="assistant",
            content=service_response,
            metadata={
                "service_type": service_type,
                "response_type": "custom",
                "knowledge_sources": len(knowledge),
                "next_actions": next_actions,
                "urgency_level": self._assess_urgency(message, service_type)
            }
        )
    
    async def execute_task(
        self,
        task: AgentTask,
        context: AgentContext,
        **kwargs
    ) -> AgentTask:
        """执行客户服务任务"""
        
        task_type = task.metadata.get("task_type", "customer_inquiry")
        
        try:
            if task_type == "order_tracking":
                result = await self._track_order(task, context)
            elif task_type == "return_processing":
                result = await self._process_return(task, context)
            elif task_type == "complaint_handling":
                result = await self._handle_complaint(task, context)
            elif task_type == "account_verification":
                result = await self._verify_account(task, context)
            elif task_type == "escalation_management":
                result = await self._manage_escalation(task, context)
            elif task_type == "customer_feedback":
                result = await self._process_feedback(task, context)
            else:
                result = await self._general_customer_service(task, context)
            
            task.output_data = result
            
        except Exception as e:
            logger.error(f"❌ 客户服务任务执行失败: {e}")
            task.output_data = {
                "error": str(e),
                "task_type": task_type,
                "fallback_response": "我们已记录您的问题，客服专员将在24小时内联系您。"
            }
            raise
        
        return task
    
    def _identify_service_type(self, message: str) -> str:
        """识别客户服务类型"""
        message_lower = message.lower()
        
        # 订单相关
        if any(word in message_lower for word in ["订单", "order", "购买", "下单"]):
            return "order_inquiry"
        
        # 退换货
        elif any(word in message_lower for word in ["退货", "换货", "退款", "return", "refund"]):
            return "return_refund"
        
        # 商品咨询
        elif any(word in message_lower for word in ["商品", "产品", "价格", "规格", "参数"]):
            return "product_info"
        
        # 投诉建议
        elif any(word in message_lower for word in ["投诉", "建议", "不满", "问题", "complaint"]):
            return "complaint"
        
        # 账户问题
        elif any(word in message_lower for word in ["账户", "登录", "密码", "account", "profile"]):
            return "account_issue"
        
        # 支付问题
        elif any(word in message_lower for word in ["支付", "付款", "payment", "银行卡", "支付宝", "微信"]):
            return "payment_issue"
        
        # 配送问题
        elif any(word in message_lower for word in ["配送", "快递", "物流", "delivery", "shipping"]):
            return "delivery_issue"
        
        # 技术支持
        elif any(word in message_lower for word in ["技术", "bug", "故障", "无法使用", "technical"]):
            return "technical_support"
        
        return "general_inquiry"
    
    def _check_faq(self, message: str) -> Optional[str]:
        """检查是否为常见问题"""
        message_lower = message.lower()
        
        for question, answer in self.faq_database.items():
            # 简单的关键词匹配（实际项目中可以使用语义匹配）
            if any(keyword in message_lower for keyword in question.lower().split()):
                return answer
        
        return None
    
    def _init_faq_database(self) -> Dict[str, str]:
        """初始化常见问题数据库"""
        return {
            "营业时间": """
沃尔玛门店营业时间：
• 大部分门店：早上8:00 - 晚上22:00
• 24小时门店：全天候营业
• 节假日可能调整，请提前查询具体门店信息
• 在线商城：24小时服务

如需查询具体门店营业时间，请访问我们的门店查询页面。
""",
            
            "退换货政策": """
沃尔玛退换货政策：
• 商品购买后30天内可申请退换货
• 商品需保持原包装和标签完整
• 需提供购买凭证（小票或订单号）
• 特殊商品（如生鲜、个人护理用品）可能有不同政策

退换货流程：
1. 携带商品和购买凭证到门店客服中心
2. 或在线申请退换货服务
3. 我们将在3-5个工作日内处理您的申请
""",
            
            "会员权益": """
沃尔玛会员专享权益：
• 会员专属价格和优惠
• 积分累积和兑换
• 生日特惠和节日礼品
• 优先客服支持
• 免费送货服务（满额）

如何成为会员：
• 门店现场办理
• 手机APP在线注册
• 微信小程序快速申请
""",
            
            "配送服务": """
沃尔玛配送服务：
• 标准配送：2-3个工作日
• 快速配送：次日达（部分城市）
• 当日达：下单当天送达（限定区域）
• 门店自提：免费，2小时内可取

配送费用：
• 满99元免配送费
• 未满额订单配送费8元
• 会员享受更多免费配送优惠
""",
            
            "支付方式": """
沃尔玛支持的支付方式：
• 现金
• 银行卡（借记卡/信用卡）
• 微信支付
• 支付宝
• Apple Pay / Google Pay
• 沃尔玛礼品卡

在线支付安全保障：
• SSL加密技术
• 银行级安全标准
• 不存储您的支付信息
"""
        }
    
    def _build_service_prompt(
        self,
        message: str,
        service_type: str,
        knowledge: List[Dict[str, Any]],
        context: AgentContext
    ) -> str:
        """构建客户服务提示"""
        
        base_prompt = f"""
作为沃尔玛的专业客户服务代表，请友好、耐心、专业地回答客户问题：

客户问题：{message}
服务类型：{service_type}

相关服务信息：
"""
        
        # 添加知识库内容
        for i, kb_item in enumerate(knowledge[:2]):
            base_prompt += f"\n{i+1}. {kb_item['content'][:300]}...\n"
        
        # 根据服务类型添加专业指导
        type_guidance = {
            "order_inquiry": """
处理订单查询时请：
- 详细说明订单状态和配送信息
- 提供订单跟踪方法
- 解释可能的延误原因
- 主动提供解决方案
""",
            "return_refund": """
处理退换货时请：
- 详细说明退换货政策和流程
- 确认商品是否符合退换条件
- 提供具体的操作步骤
- 告知处理时间和注意事项
""",
            "complaint": """
处理投诉时请：
- 表示理解和歉意
- 认真倾听客户的具体问题
- 提供具体的解决方案
- 确保问题得到妥善处理
- 必要时提供升级渠道
""",
            "product_info": """
提供商品信息时请：
- 详细介绍商品特性和规格
- 说明价格和优惠信息
- 提供使用建议
- 推荐相关商品
""",
            "technical_support": """
提供技术支持时请：
- 逐步引导客户操作
- 提供清晰的解决步骤
- 确认问题是否解决
- 提供替代方案
"""
        }
        
        base_prompt += type_guidance.get(service_type, """
请提供专业的客户服务，包括：
- 友好的问候和理解
- 清晰的问题解答
- 具体的解决方案
- 贴心的服务建议
""")
        
        base_prompt += """
回复要求：
1. 语气友好、耐心、专业
2. 回答准确、详细、有帮助
3. 主动提供解决方案
4. 体现沃尔玛的优质服务
5. 如有必要，提供联系方式或升级渠道

请用中文回答，体现沃尔玛"省钱省心"的服务理念。
"""
        
        return base_prompt
    
    def _generate_next_actions(self, service_type: str, message: str) -> List[str]:
        """生成后续行动建议"""
        action_mapping = {
            "order_inquiry": [
                "查询订单详细状态",
                "设置配送提醒",
                "联系配送员"
            ],
            "return_refund": [
                "准备退换货材料",
                "预约门店服务",
                "跟踪退款进度"
            ],
            "complaint": [
                "记录投诉详情",
                "安排专员跟进",
                "定期回访客户"
            ],
            "product_info": [
                "查看商品详情页",
                "比较类似商品",
                "添加购物车"
            ],
            "technical_support": [
                "尝试建议的解决方案",
                "联系技术专员",
                "反馈问题状态"
            ]
        }
        
        return action_mapping.get(service_type, [
            "如有其他问题随时联系",
            "关注沃尔玛官方服务号",
            "参与客户满意度调查"
        ])
    
    def _assess_urgency(self, message: str, service_type: str) -> str:
        """评估问题紧急程度"""
        message_lower = message.lower()
        
        # 高紧急度关键词
        high_urgency_keywords = [
            "紧急", "急需", "马上", "立即", "投诉", 
            "退款", "欺诈", "故障", "无法使用"
        ]
        
        # 中等紧急度关键词
        medium_urgency_keywords = [
            "问题", "帮助", "不满", "延误", "错误"
        ]
        
        if any(keyword in message_lower for keyword in high_urgency_keywords):
            return "high"
        elif any(keyword in message_lower for keyword in medium_urgency_keywords):
            return "medium"
        elif service_type in ["complaint", "return_refund", "payment_issue"]:
            return "medium"
        else:
            return "low"
    
    async def _track_order(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """订单跟踪"""
        order_id = task.input_data.get("order_id", "WM202401150001")
        
        return {
            "service_type": "order_tracking",
            "order_id": order_id,
            "order_status": {
                "status": "已发货",
                "tracking_number": "SF1234567890",
                "estimated_delivery": "2024-01-18",
                "current_location": "北京分拣中心"
            },
            "order_details": {
                "items": [
                    {"name": "iPhone 15", "quantity": 1, "price": 5999},
                    {"name": "保护壳", "quantity": 1, "price": 99}
                ],
                "total_amount": 6098,
                "payment_method": "微信支付"
            },
            "next_steps": [
                "您的订单预计明天送达",
                "配送员将在送达前1小时联系您",
                "如有问题请随时联系客服"
            ]
        }
    
    async def _process_return(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """处理退换货"""
        return {
            "service_type": "return_processing",
            "return_eligibility": {
                "eligible": True,
                "reason": "商品在30天退换期内",
                "conditions": ["商品包装完整", "附件齐全", "无人为损坏"]
            },
            "return_process": {
                "step1": "填写退货申请表",
                "step2": "打包商品并贴上退货标签",
                "step3": "选择退货方式（门店或快递）",
                "step4": "等待退款处理（3-5个工作日）"
            },
            "refund_info": {
                "refund_amount": 5999,
                "refund_method": "原支付方式",
                "processing_time": "3-5个工作日"
            },
            "contact_info": {
                "customer_service": "400-826-8826",
                "service_hours": "9:00-21:00"
            }
        }
    
    async def _handle_complaint(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """处理投诉"""
        complaint_type = task.input_data.get("complaint_type", "service_quality")
        
        return {
            "service_type": "complaint_handling",
            "complaint_id": f"CP{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "acknowledgment": "我们已收到您的投诉，深表歉意",
            "investigation": {
                "status": "正在调查",
                "assigned_to": "高级客服专员",
                "expected_resolution": "48小时内"
            },
            "compensation": {
                "type": "根据调查结果确定",
                "options": ["退款", "换货", "优惠券", "积分补偿"]
            },
            "escalation": {
                "available": True,
                "manager_contact": "manager@walmart.cn",
                "escalation_process": "如不满意处理结果，可申请经理介入"
            },
            "follow_up": {
                "schedule": "24小时后电话回访",
                "satisfaction_survey": "处理完成后进行满意度调查"
            }
        }
    
    async def _verify_account(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """账户验证"""
        return {
            "service_type": "account_verification",
            "verification_methods": [
                "手机短信验证",
                "邮箱验证",
                "身份证后四位",
                "安全问题回答"
            ],
            "account_status": "正常",
            "recent_activities": [
                {"date": "2024-01-15", "action": "登录", "location": "北京"},
                {"date": "2024-01-14", "action": "购买", "amount": 299}
            ],
            "security_tips": [
                "定期更换密码",
                "不要在公共设备上保存登录信息",
                "发现异常活动及时联系客服"
            ]
        }
    
    async def _manage_escalation(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """管理升级"""
        return {
            "service_type": "escalation_management",
            "escalation_level": "经理级别",
            "assigned_manager": "张经理",
            "contact_info": {
                "phone": "400-826-8826 转 8001",
                "email": "manager@walmart.cn"
            },
            "escalation_timeline": {
                "acknowledgment": "2小时内",
                "investigation": "24小时内",
                "resolution": "72小时内"
            },
            "priority": "高优先级",
            "tracking_number": f"ESC{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
    
    async def _process_feedback(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """处理客户反馈"""
        return {
            "service_type": "customer_feedback",
            "feedback_id": f"FB{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "feedback_category": task.input_data.get("category", "service_improvement"),
            "acknowledgment": "感谢您的宝贵反馈",
            "processing": {
                "review_team": "客户体验团队",
                "review_timeline": "7个工作日内",
                "implementation": "根据反馈重要性安排改进"
            },
            "reward": {
                "points": 50,
                "coupon": "感谢优惠券 - 50元",
                "description": "感谢您的反馈，已为您发放积分奖励"
            }
        }
    
    async def _general_customer_service(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """通用客户服务"""
        return {
            "service_type": "general_inquiry",
            "response": "我们已收到您的咨询，客服代表将为您提供专业服务",
            "available_services": [
                "商品咨询", "订单查询", "退换货服务",
                "会员服务", "技术支持", "投诉建议"
            ],
            "contact_methods": {
                "hotline": "400-826-8826",
                "online_chat": "官网在线客服",
                "email": "service@walmart.cn",
                "wechat": "沃尔玛官方服务号"
            },
            "service_hours": "9:00-21:00 (周一至周日)"
        }
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """
你是沃尔玛的专业客户服务代表，具有丰富的客户服务经验和问题解决能力。

你的服务理念：
- 客户至上，服务第一
- 耐心倾听，专业解答
- 主动服务，超越期待
- 诚信可靠，值得信赖

你的服务范围：
- 商品咨询和推荐
- 订单查询和跟踪
- 退换货服务
- 投诉处理和问题解决
- 账户和支付问题
- 技术支持

请始终保持友好、耐心、专业的服务态度，为客户提供准确、及时、贴心的服务。
体现沃尔玛"省钱省心"的服务承诺。
"""
    
    def _get_relevant_keywords(self) -> List[str]:
        """获取相关关键词"""
        return [
            "客服", "服务", "帮助", "咨询", "问题",
            "订单", "购买", "支付", "配送", "物流",
            "退货", "换货", "退款", "return", "refund",
            "投诉", "建议", "不满", "complaint",
            "账户", "登录", "密码", "会员",
            "商品", "产品", "价格", "优惠",
            "技术", "故障", "bug", "无法使用",
            "营业时间", "门店", "联系方式"
        ]
    
    def _get_default_collection(self) -> str:
        """获取默认知识库集合名"""
        return "customer_service_kb"
