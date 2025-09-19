# 🛒 沃尔玛AI Agent平台 - 向量数据库服务
# Walmart AI Agent Platform - Vector Database Service

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any
from uuid import uuid4

import chromadb
import numpy as np
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class VectorService:
    """向量数据库服务 - 支持多源数据整合"""
    
    def __init__(self):
        self.client: Optional[chromadb.Client] = None
        self.embedding_model: Optional[SentenceTransformer] = None
        self.collections: Dict[str, chromadb.Collection] = {}
        
    async def initialize(self):
        """初始化向量数据库连接"""
        try:
            # 初始化ChromaDB客户端
            self.client = chromadb.HttpClient(
                host=settings.CHROMA_HOST,
                port=settings.CHROMA_PORT,
                settings=Settings(
                    chroma_client_auth_provider="chromadb.auth.basic_authn.BasicAuthClientProvider",
                    chroma_client_auth_credentials=f"{settings.CHROMA_AUTH_USER}:{settings.CHROMA_AUTH_PASSWORD}"
                )
            )
            
            # 初始化嵌入模型
            self.embedding_model = SentenceTransformer(settings.DEFAULT_EMBEDDING_MODEL)
            
            # 创建默认集合
            await self._create_default_collections()
            
            logger.info("✅ 向量数据库服务初始化完成")
            
        except Exception as e:
            logger.error(f"❌ 向量数据库初始化失败: {e}")
            raise
    
    async def _create_default_collections(self):
        """创建默认集合"""
        default_collections = [
            "walmart_documents",      # 沃尔玛文档集合
            "product_catalog",        # 商品目录
            "customer_data",          # 客户数据
            "sales_reports",          # 销售报告
            "inventory_data",         # 库存数据
            "market_analysis",        # 市场分析
            "operational_logs",       # 运营日志
        ]
        
        for collection_name in default_collections:
            try:
                collection = self.client.get_or_create_collection(
                    name=collection_name,
                    metadata={
                        "description": f"沃尔玛{collection_name}数据集合",
                        "created_by": "system",
                        "version": "1.0"
                    }
                )
                self.collections[collection_name] = collection
                logger.info(f"✅ 创建集合: {collection_name}")
                
            except Exception as e:
                logger.error(f"❌ 创建集合失败 {collection_name}: {e}")
    
    async def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """添加文档到向量数据库"""
        try:
            if collection_name not in self.collections:
                self.collections[collection_name] = self.client.get_or_create_collection(collection_name)
            
            collection = self.collections[collection_name]
            
            # 生成ID
            if ids is None:
                ids = [str(uuid4()) for _ in documents]
            
            # 生成嵌入向量
            embeddings = await self._generate_embeddings(documents)
            
            # 添加到集合
            collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas or [{} for _ in documents],
                ids=ids
            )
            
            logger.info(f"✅ 成功添加 {len(documents)} 个文档到集合 {collection_name}")
            return ids
            
        except Exception as e:
            logger.error(f"❌ 添加文档失败: {e}")
            raise
    
    async def search_similar_documents(
        self,
        collection_name: str,
        query: str,
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
        include: List[str] = ["documents", "metadatas", "distances"]
    ) -> Dict[str, Any]:
        """搜索相似文档"""
        try:
            if collection_name not in self.collections:
                raise ValueError(f"集合 {collection_name} 不存在")
            
            collection = self.collections[collection_name]
            
            # 生成查询向量
            query_embedding = await self._generate_embeddings([query])
            
            # 执行搜索
            results = collection.query(
                query_embeddings=query_embedding,
                n_results=n_results,
                where=where,
                include=include
            )
            
            logger.info(f"✅ 在集合 {collection_name} 中搜索到 {len(results['ids'][0])} 个相似文档")
            return results
            
        except Exception as e:
            logger.error(f"❌ 搜索文档失败: {e}")
            raise
    
    async def update_documents(
        self,
        collection_name: str,
        ids: List[str],
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """更新文档"""
        try:
            if collection_name not in self.collections:
                raise ValueError(f"集合 {collection_name} 不存在")
            
            collection = self.collections[collection_name]
            
            update_data = {"ids": ids}
            
            if documents:
                embeddings = await self._generate_embeddings(documents)
                update_data["documents"] = documents
                update_data["embeddings"] = embeddings
            
            if metadatas:
                update_data["metadatas"] = metadatas
            
            collection.update(**update_data)
            
            logger.info(f"✅ 成功更新集合 {collection_name} 中的 {len(ids)} 个文档")
            return True
            
        except Exception as e:
            logger.error(f"❌ 更新文档失败: {e}")
            return False
    
    async def delete_documents(
        self,
        collection_name: str,
        ids: List[str]
    ) -> bool:
        """删除文档"""
        try:
            if collection_name not in self.collections:
                raise ValueError(f"集合 {collection_name} 不存在")
            
            collection = self.collections[collection_name]
            collection.delete(ids=ids)
            
            logger.info(f"✅ 成功删除集合 {collection_name} 中的 {len(ids)} 个文档")
            return True
            
        except Exception as e:
            logger.error(f"❌ 删除文档失败: {e}")
            return False
    
    async def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """获取集合统计信息"""
        try:
            if collection_name not in self.collections:
                raise ValueError(f"集合 {collection_name} 不存在")
            
            collection = self.collections[collection_name]
            count = collection.count()
            
            return {
                "name": collection_name,
                "count": count,
                "metadata": collection.metadata,
            }
            
        except Exception as e:
            logger.error(f"❌ 获取集合统计失败: {e}")
            return {}
    
    async def list_collections(self) -> List[Dict[str, Any]]:
        """列出所有集合"""
        try:
            collections = self.client.list_collections()
            return [
                {
                    "name": col.name,
                    "metadata": col.metadata,
                    "count": col.count()
                }
                for col in collections
            ]
            
        except Exception as e:
            logger.error(f"❌ 列出集合失败: {e}")
            return []
    
    async def create_collection(
        self,
        name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """创建新集合"""
        try:
            collection = self.client.create_collection(
                name=name,
                metadata=metadata or {}
            )
            self.collections[name] = collection
            
            logger.info(f"✅ 成功创建集合: {name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 创建集合失败 {name}: {e}")
            return False
    
    async def delete_collection(self, name: str) -> bool:
        """删除集合"""
        try:
            self.client.delete_collection(name=name)
            if name in self.collections:
                del self.collections[name]
            
            logger.info(f"✅ 成功删除集合: {name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 删除集合失败 {name}: {e}")
            return False
    
    async def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """生成文本嵌入向量"""
        if not self.embedding_model:
            raise RuntimeError("嵌入模型未初始化")
        
        # 在线程池中运行嵌入生成（避免阻塞）
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None, 
            self.embedding_model.encode, 
            texts
        )
        
        return embeddings.tolist()
    
    async def hybrid_search(
        self,
        collection_name: str,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        n_results: int = 10,
        alpha: float = 0.7  # 语义搜索权重
    ) -> Dict[str, Any]:
        """混合搜索 - 结合语义搜索和关键词搜索"""
        try:
            # 语义搜索
            semantic_results = await self.search_similar_documents(
                collection_name=collection_name,
                query=query,
                n_results=n_results * 2,  # 获取更多结果用于重排序
                where=filters
            )
            
            # 关键词匹配（简单实现）
            keyword_scores = self._calculate_keyword_scores(
                query, 
                semantic_results.get("documents", [[]])[0]
            )
            
            # 混合评分
            final_results = self._combine_scores(
                semantic_results, 
                keyword_scores, 
                alpha, 
                n_results
            )
            
            return final_results
            
        except Exception as e:
            logger.error(f"❌ 混合搜索失败: {e}")
            raise
    
    def _calculate_keyword_scores(self, query: str, documents: List[str]) -> List[float]:
        """计算关键词匹配分数"""
        query_terms = set(query.lower().split())
        scores = []
        
        for doc in documents:
            doc_terms = set(doc.lower().split())
            intersection = query_terms.intersection(doc_terms)
            score = len(intersection) / len(query_terms) if query_terms else 0
            scores.append(score)
        
        return scores
    
    def _combine_scores(
        self,
        semantic_results: Dict[str, Any],
        keyword_scores: List[float],
        alpha: float,
        n_results: int
    ) -> Dict[str, Any]:
        """组合语义和关键词分数"""
        if not semantic_results.get("distances"):
            return semantic_results
        
        distances = semantic_results["distances"][0]
        
        # 将距离转换为相似度分数（距离越小，相似度越高）
        max_distance = max(distances) if distances else 1
        semantic_scores = [(max_distance - d) / max_distance for d in distances]
        
        # 组合分数
        combined_scores = [
            alpha * sem_score + (1 - alpha) * kw_score
            for sem_score, kw_score in zip(semantic_scores, keyword_scores)
        ]
        
        # 根据组合分数排序
        sorted_indices = sorted(
            range(len(combined_scores)),
            key=lambda i: combined_scores[i],
            reverse=True
        )[:n_results]
        
        # 重新组织结果
        result = {
            "ids": [[semantic_results["ids"][0][i] for i in sorted_indices]],
            "documents": [[semantic_results["documents"][0][i] for i in sorted_indices]],
            "metadatas": [[semantic_results["metadatas"][0][i] for i in sorted_indices]],
            "distances": [[1 - combined_scores[i] for i in sorted_indices]],  # 转回距离
        }
        
        return result
