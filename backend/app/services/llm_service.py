# 🛒 沃尔玛AI Agent平台 - 大语言模型服务
# Walmart AI Agent Platform - Large Language Model Service

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, AsyncGenerator
from enum import Enum

import httpx
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class ModelProvider(str, Enum):
    """模型提供商枚举"""
    OPENAI = "openai"
    CHATGLM = "chatglm"
    DEEPSEEK = "deepseek"
    ANTHROPIC = "anthropic"


class LLMResponse:
    """LLM响应包装类"""
    
    def __init__(
        self,
        content: str,
        model: str,
        provider: ModelProvider,
        tokens_used: Optional[int] = None,
        cost: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.content = content
        self.model = model
        self.provider = provider
        self.tokens_used = tokens_used
        self.cost = cost
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "model": self.model,
            "provider": self.provider,
            "tokens_used": self.tokens_used,
            "cost": self.cost,
            "metadata": self.metadata
        }


class BaseLLMProvider(ABC):
    """LLM提供商基类"""
    
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.client = None
    
    @abstractmethod
    async def initialize(self):
        """初始化客户端"""
        pass
    
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> LLMResponse:
        """聊天完成"""
        pass
    
    @abstractmethod
    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式聊天完成"""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI模型提供商"""
    
    def __init__(self):
        super().__init__(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            model=settings.OPENAI_MODEL
        )
    
    async def initialize(self):
        """初始化OpenAI客户端"""
        if not self.api_key:
            raise ValueError("OpenAI API密钥未设置")
        
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        logger.info("✅ OpenAI客户端初始化完成")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> LLMResponse:
        """OpenAI聊天完成"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                **kwargs
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None
            
            return LLMResponse(
                content=content,
                model=self.model,
                provider=ModelProvider.OPENAI,
                tokens_used=tokens_used,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "response_id": response.id
                }
            )
            
        except Exception as e:
            logger.error(f"❌ OpenAI聊天完成失败: {e}")
            raise
    
    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """OpenAI流式聊天完成"""
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"❌ OpenAI流式聊天失败: {e}")
            raise


class ChatGLMProvider(BaseLLMProvider):
    """ChatGLM模型提供商"""
    
    def __init__(self):
        super().__init__(
            api_key=settings.CHATGLM_API_KEY,
            base_url=settings.CHATGLM_BASE_URL,
            model=settings.CHATGLM_MODEL
        )
    
    async def initialize(self):
        """初始化ChatGLM客户端"""
        if not self.api_key:
            raise ValueError("ChatGLM API密钥未设置")
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=60.0
        )
        logger.info("✅ ChatGLM客户端初始化完成")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> LLMResponse:
        """ChatGLM聊天完成"""
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "stream": stream,
                **kwargs
            }
            
            if max_tokens:
                payload["max_tokens"] = max_tokens
            
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            tokens_used = data.get("usage", {}).get("total_tokens")
            
            return LLMResponse(
                content=content,
                model=self.model,
                provider=ModelProvider.CHATGLM,
                tokens_used=tokens_used,
                metadata={
                    "finish_reason": data["choices"][0].get("finish_reason"),
                    "response_id": data.get("id")
                }
            )
            
        except Exception as e:
            logger.error(f"❌ ChatGLM聊天完成失败: {e}")
            raise
    
    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """ChatGLM流式聊天完成"""
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "stream": True,
                **kwargs
            }
            
            if max_tokens:
                payload["max_tokens"] = max_tokens
            
            async with self.client.stream("POST", "/chat/completions", json=payload) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]  # 去掉 "data: " 前缀
                        
                        if data_str.strip() == "[DONE]":
                            break
                        
                        try:
                            data = json.loads(data_str)
                            content = data["choices"][0]["delta"].get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            logger.error(f"❌ ChatGLM流式聊天失败: {e}")
            raise


class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek模型提供商"""
    
    def __init__(self):
        super().__init__(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
            model=settings.DEEPSEEK_MODEL
        )
    
    async def initialize(self):
        """初始化DeepSeek客户端"""
        if not self.api_key:
            raise ValueError("DeepSeek API密钥未设置")
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=60.0
        )
        logger.info("✅ DeepSeek客户端初始化完成")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> LLMResponse:
        """DeepSeek聊天完成"""
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "stream": stream,
                **kwargs
            }
            
            if max_tokens:
                payload["max_tokens"] = max_tokens
            
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            tokens_used = data.get("usage", {}).get("total_tokens")
            
            return LLMResponse(
                content=content,
                model=self.model,
                provider=ModelProvider.DEEPSEEK,
                tokens_used=tokens_used,
                metadata={
                    "finish_reason": data["choices"][0].get("finish_reason"),
                    "response_id": data.get("id")
                }
            )
            
        except Exception as e:
            logger.error(f"❌ DeepSeek聊天完成失败: {e}")
            raise
    
    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """DeepSeek流式聊天完成"""
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "stream": True,
                **kwargs
            }
            
            if max_tokens:
                payload["max_tokens"] = max_tokens
            
            async with self.client.stream("POST", "/chat/completions", json=payload) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        
                        if data_str.strip() == "[DONE]":
                            break
                        
                        try:
                            data = json.loads(data_str)
                            content = data["choices"][0]["delta"].get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            logger.error(f"❌ DeepSeek流式聊天失败: {e}")
            raise


class LLMService:
    """大语言模型服务"""
    
    def __init__(self):
        self.providers: Dict[ModelProvider, BaseLLMProvider] = {}
        self.default_provider = ModelProvider.OPENAI
    
    async def initialize(self):
        """初始化所有可用的LLM提供商"""
        # 初始化OpenAI
        if settings.OPENAI_API_KEY:
            openai_provider = OpenAIProvider()
            await openai_provider.initialize()
            self.providers[ModelProvider.OPENAI] = openai_provider
        
        # 初始化ChatGLM
        if settings.CHATGLM_API_KEY:
            chatglm_provider = ChatGLMProvider()
            await chatglm_provider.initialize()
            self.providers[ModelProvider.CHATGLM] = chatglm_provider
        
        # 初始化DeepSeek
        if settings.DEEPSEEK_API_KEY:
            deepseek_provider = DeepSeekProvider()
            await deepseek_provider.initialize()
            self.providers[ModelProvider.DEEPSEEK] = deepseek_provider
        
        # 设置默认提供商
        if self.providers:
            self.default_provider = next(iter(self.providers.keys()))
        
        logger.info(f"✅ LLM服务初始化完成，可用提供商: {list(self.providers.keys())}")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        provider: Optional[ModelProvider] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> LLMResponse:
        """聊天完成"""
        provider = provider or self.default_provider
        
        if provider not in self.providers:
            raise ValueError(f"提供商 {provider} 不可用")
        
        return await self.providers[provider].chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            **kwargs
        )
    
    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        provider: Optional[ModelProvider] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式聊天完成"""
        provider = provider or self.default_provider
        
        if provider not in self.providers:
            raise ValueError(f"提供商 {provider} 不可用")
        
        async for chunk in self.providers[provider].stream_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        ):
            yield chunk
    
    async def multi_provider_completion(
        self,
        messages: List[Dict[str, str]],
        providers: List[ModelProvider],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> List[LLMResponse]:
        """多提供商并行完成"""
        tasks = []
        
        for provider in providers:
            if provider in self.providers:
                task = self.chat_completion(
                    messages=messages,
                    provider=provider,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
                tasks.append(task)
        
        if not tasks:
            raise ValueError("没有可用的提供商")
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 过滤异常结果
        valid_results = [r for r in results if isinstance(r, LLMResponse)]
        
        return valid_results
    
    async def get_best_response(
        self,
        messages: List[Dict[str, str]],
        providers: Optional[List[ModelProvider]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """获取最佳响应（基于多提供商比较）"""
        providers = providers or list(self.providers.keys())
        
        responses = await self.multi_provider_completion(
            messages=messages,
            providers=providers,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        if not responses:
            raise RuntimeError("所有提供商都失败了")
        
        # 简单的评分机制（可以根据需要扩展）
        def score_response(response: LLMResponse) -> float:
            score = len(response.content)  # 基础分数：内容长度
            
            # 提供商权重
            provider_weights = {
                ModelProvider.OPENAI: 1.2,
                ModelProvider.CHATGLM: 1.1,
                ModelProvider.DEEPSEEK: 1.0,
            }
            score *= provider_weights.get(response.provider, 1.0)
            
            return score
        
        # 选择得分最高的响应
        best_response = max(responses, key=score_response)
        
        return best_response
    
    def get_available_providers(self) -> List[ModelProvider]:
        """获取可用的提供商列表"""
        return list(self.providers.keys())
    
    async def health_check(self) -> Dict[str, bool]:
        """健康检查所有提供商"""
        health_status = {}
        
        test_messages = [{"role": "user", "content": "Hello"}]
        
        for provider, client in self.providers.items():
            try:
                await client.chat_completion(test_messages, max_tokens=10)
                health_status[provider] = True
            except Exception as e:
                logger.warning(f"提供商 {provider} 健康检查失败: {e}")
                health_status[provider] = False
        
        return health_status
