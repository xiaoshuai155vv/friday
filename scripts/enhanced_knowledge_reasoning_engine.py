#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强智能知识推理引擎
让系统能够进行更深入的因果推理、类比推理，并主动从知识图谱中发现隐藏关联，为用户提供主动洞察

功能：
1. 因果推理链分析 - 分析事件之间的因果关系
2. 类比推理和隐喻理解 - 发现不同领域之间的相似性
3. 知识关联发现 - 从知识图谱中主动发现隐藏关联
4. 主动洞察生成 - 基于推理主动向用户推荐有价值的信息

集成到 do.py 支持关键词：
- 知识推理、因果分析、推理、主动洞察、发现关联
"""

import sys
import os
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from scripts.knowledge_graph import KnowledgeGraph
except ImportError:
    # 如果 knowledge_graph 不可用，提供一个简单的替代
    class KnowledgeGraph:
        def __init__(self, storage_path="runtime/state/knowledge_graph.json"):
            self.storage_path = storage_path
            self.graph = {"nodes": {}, "edges": [], "metadata": {}}
            self._load_graph()

        def _load_graph(self):
            if os.path.exists(self.storage_path):
                try:
                    with open(self.storage_path, 'r', encoding='utf-8') as f:
                        self.graph = json.load(f)
                except:
                    pass

        def get_nodes_by_type(self, node_type: str) -> List[Dict]:
            return [{"id": k, "type": v.get("type"), "properties": v.get("properties")}
                    for k, v in self.graph.get("nodes", {}).items() if v.get("type") == node_type]

        def get_related_nodes(self, node_id: str, relation_type: str = None) -> List[Dict]:
            related = []
            for edge in self.graph.get("edges", []):
                if edge.get("from") == node_id:
                    if relation_type is None or edge.get("relation") == relation_type:
                        target = self.graph.get("nodes", {}).get(edge.get("to"))
                        if target:
                            related.append({
                                "node_id": edge.get("to"),
                                "node_type": target.get("type"),
                                "relation": edge.get("relation"),
                                "properties": target.get("properties", {})
                            })
            return related

        def get_graph_statistics(self) -> Dict[str, Any]:
            return {
                "total_nodes": len(self.graph.get("nodes", {})),
                "total_edges": len(self.graph.get("edges", []))
            }

        def get_all_nodes(self) -> Dict:
            return self.graph.get("nodes", {})

        def get_all_edges(self) -> List[Dict]:
            return self.graph.get("edges", [])


@dataclass
class CausalChain:
    """因果链"""
    cause: str
    effect: str
    confidence: float
    chain: List[str] = field(default_factory=list)
    intermediate_nodes: List[str] = field(default_factory=list)


@dataclass
class AnalogyResult:
    """类比结果"""
    source_concept: str
    target_concept: str
    similarity: float
    common_properties: List[str] = field(default_factory=list)
    explanation: str = ""


@dataclass
class Insight:
    """洞察"""
    id: str
    title: str
    description: str
    source_type: str  # causal, analogy, association, pattern
    confidence: float
    related_nodes: List[str] = field(default_factory=list)
    suggested_actions: List[str] = field(default_factory=list)
    timestamp: str = ""


class EnhancedKnowledgeReasoningEngine:
    """增强智能知识推理引擎"""

    def __init__(self, knowledge_graph: KnowledgeGraph = None):
        """
        初始化增强知识推理引擎

        Args:
            knowledge_graph: 知识图谱实例，如果为None则创建新实例
        """
        self.kg = knowledge_graph or KnowledgeGraph()
        self.insights_history: List[Insight] = []
        self.reasoning_cache: Dict[str, Any] = {}

        # 加载历史洞察
        self._load_insights()

    def _load_insights(self):
        """加载历史洞察"""
        insights_path = "runtime/state/insights_history.json"
        if os.path.exists(insights_path):
            try:
                with open(insights_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data.get("insights", []):
                        self.insights_history.append(Insight(**item))
            except Exception as e:
                print(f"加载洞察历史失败: {e}")

    def _save_insights(self):
        """保存洞察到历史"""
        insights_path = "runtime/state/insights_history.json"
        try:
            os.makedirs(os.path.dirname(insights_path), exist_ok=True)
            with open(insights_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "insights": [
                        {
                            "id": i.id,
                            "title": i.title,
                            "description": i.description,
                            "source_type": i.source_type,
                            "confidence": i.confidence,
                            "related_nodes": i.related_nodes,
                            "suggested_actions": i.suggested_actions,
                            "timestamp": i.timestamp
                        }
                        for i in self.insights_history[-50:]  # 保留最近50条
                    ],
                    "updated_at": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存洞察历史失败: {e}")

    def analyze_causal_chain(self, start_node: str, max_depth: int = 3) -> List[CausalChain]:
        """
        分析因果链

        Args:
            start_node: 起始节点
            max_depth: 最大深度

        Returns:
            因果链列表
        """
        causal_chains = []

        # BFS 查找因果链
        visited = set()
        queue = [(start_node, [start_node])]

        while queue:
            current, path = queue.pop(0)

            if len(path) > max_depth:
                continue

            if current in visited:
                continue

            visited.add(current)

            # 查找当前节点的关联
            related = self.kg.get_related_nodes(current)

            for rel in related:
                node_id = rel.get("node_id")
                relation = rel.get("relation", "")

                # 判断是否为因果关系
                if any(keyword in relation.lower() for keyword in ["cause", "effect", "lead_to", "result", "原因", "导致", "结果"]):
                    new_path = path + [node_id]
                    chain = CausalChain(
                        cause=start_node,
                        effect=node_id,
                        confidence=0.7,
                        chain=new_path,
                        intermediate_nodes=new_path[1:-1] if len(new_path) > 2 else []
                    )
                    causal_chains.append(chain)

                # 继续探索
                if len(path) < max_depth and node_id not in visited:
                    queue.append((node_id, path + [node_id]))

        return causal_chains

    def find_analogies(self, concept: str, domain: str = None) -> List[AnalogyResult]:
        """
        查找类比

        Args:
            concept: 概念
            domain: 领域（可选）

        Returns:
            类比结果列表
        """
        analogies = []

        # 获取所有概念节点
        all_nodes = self.kg.get_nodes_by_type("knowledge")

        # 如果指定了领域，筛选
        if domain:
            all_nodes = [n for n in all_nodes if n.get("properties", {}).get("domain") == domain]

        # 查找相似的概念
        for node in all_nodes:
            node_id = node.get("id", "")
            properties = node.get("properties", {})

            # 基于名称相似度（简化版）
            similarity = self._calculate_similarity(concept, node_id)

            if similarity > 0.3:  # 阈值
                analogy = AnalogyResult(
                    source_concept=concept,
                    target_concept=node_id,
                    similarity=similarity,
                    common_properties=self._find_common_properties(concept, node_id),
                    explanation=self._generate_analogy_explanation(concept, node_id, similarity)
                )
                analogies.append(analogy)

        # 按相似度排序
        analogies.sort(key=lambda x: x.similarity, reverse=True)

        return analogies[:5]  # 返回前5个

    def _calculate_similarity(self, concept1: str, concept2: str) -> float:
        """计算两个概念的相似度（简化版）"""
        # 基于字符重叠
        set1 = set(concept1.lower())
        set2 = set(concept2.lower())

        if not set1 or not set2:
            return 0.0

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0

    def _find_common_properties(self, concept1: str, concept2: str) -> List[str]:
        """查找共同属性"""
        common = []

        node1 = self.kg.get_node_details(concept1)
        node2 = self.kg.get_node_details(concept2)

        if node1 and node2:
            props1 = node1.get("properties", {})
            props2 = node2.get("properties", {})

            for key in props1:
                if key in props2 and props1[key] == props2[key]:
                    common.append(f"{key}: {props1[key]}")

        return common

    def _generate_analogy_explanation(self, source: str, target: str, similarity: float) -> str:
        """生成类比解释"""
        return f"'{source}' 和 '{target}' 有 {similarity:.1%} 的相似度，它们可能在某些方面有共同点"

    def discover_hidden_associations(self, node_id: str, depth: int = 2) -> List[Dict]:
        """
        发现隐藏关联

        Args:
            node_id: 节点ID
            depth: 搜索深度

        Returns:
            隐藏关联列表
        """
        hidden_associations = []

        # 使用 BFS 查找间接关联
        visited = {node_id}
        queue = [(node_id, 0, [])]

        while queue:
            current, depth_curr, path = queue.pop(0)

            if depth_curr >= depth:
                continue

            related = self.kg.get_related_nodes(current)

            for rel in related:
                next_node = rel.get("node_id")
                relation = rel.get("relation", "")

                if next_node not in visited:
                    new_path = path + [{"node": current, "relation": relation}]

                    # 找到间接关联
                    if depth_curr > 0:
                        # 构建关联描述
                        association = {
                            "from": node_id,
                            "to": next_node,
                            "path": new_path,
                            "strength": 1.0 / (depth_curr + 1),  # 深度越深，强度越弱
                            "path_description": self._describe_path(new_path + [{"node": next_node, "relation": relation}])
                        }
                        hidden_associations.append(association)

                    visited.add(next_node)
                    queue.append((next_node, depth_curr + 1, new_path))

        return hidden_associations

    def _describe_path(self, path: List[Dict]) -> str:
        """描述路径"""
        if not path:
            return ""

        descriptions = []
        for i, step in enumerate(path):
            node = step.get("node", "")
            relation = step.get("relation", "")
            if node and relation:
                descriptions.append(f"{node} --[{relation}]--> ")

        return "".join(descriptions).rstrip(" -->")

    def generate_proactive_insights(self, context: Dict[str, Any] = None) -> List[Insight]:
        """
        生成主动洞察

        Args:
            context: 上下文信息

        Returns:
            洞察列表
        """
        insights = []

        # 1. 基于知识图谱统计的洞察
        stats = self.kg.get_graph_statistics()
        total_nodes = stats.get("total_nodes", 0)
        total_edges = stats.get("total_edges", 0)

        # 如果知识图谱有足够的数据，生成洞察
        if total_nodes > 5:
            # 洞察1: 知识密度洞察
            density = total_edges / total_nodes if total_nodes > 0 else 0
            if density < 0.5:
                insight = Insight(
                    id=f"insight_density_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    title="知识关联密度较低",
                    description=f"当前知识图谱有 {total_nodes} 个节点和 {total_edges} 条边，关联密度为 {density:.2f}，建议增加更多实体之间的关联",
                    source_type="pattern",
                    confidence=0.8,
                    related_nodes=[],
                    suggested_actions=["添加更多实体间的关系", "丰富现有实体的属性"]
                )
                insights.append(insight)

            # 洞察2: 节点类型分布洞察
            node_dist = stats.get("node_distribution", {})
            for node_type, count in node_dist.items():
                if count == 1:
                    insight = Insight(
                        id=f"insight_singleton_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        title=f"孤立节点: {node_type}类型",
                        description=f"发现 {count} 个 {node_type} 类型的节点没有形成网络，建议与其他节点建立关联",
                        source_type="association",
                        confidence=0.7,
                        related_nodes=[],
                        suggested_actions=[f"为 {node_type} 节点添加关联"]
                    )
                    insights.append(insight)

        # 2. 基于最近交互的洞察
        recent_interactions = self._get_recent_interactions()
        if len(recent_interactions) >= 3:
            patterns = self._detect_interaction_patterns(recent_interactions)
            if patterns:
                insight = Insight(
                    id=f"insight_pattern_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    title="检测到交互模式",
                    description=f"检测到您最近有 {patterns['count']} 次相似的交互: {patterns['description']}",
                    source_type="pattern",
                    confidence=0.75,
                    related_nodes=patterns.get("related_nodes", []),
                    suggested_actions=patterns.get("suggestions", [])
                )
                insights.append(insight)

        # 3. 保存洞察到历史
        for insight in insights:
            insight.timestamp = datetime.now().isoformat()
            self.insights_history.append(insight)

        self._save_insights()

        return insights

    def _get_recent_interactions(self) -> List[Dict]:
        """获取最近交互（简化版）"""
        # 从场景日志或行为日志中获取
        interactions = []

        # 尝试从 scenario_log 读取
        log_path = "runtime/state/scenario_experiences.json"
        if os.path.exists(log_path):
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    interactions = data.get("experiences", [])[-10:]  # 最近10条
            except:
                pass

        return interactions

    def _detect_interaction_patterns(self, interactions: List[Dict]) -> Optional[Dict]:
        """检测交互模式"""
        if not interactions:
            return None

        # 简化版：检测频繁场景
        scene_counts = defaultdict(int)
        for interaction in interactions:
            scene = interaction.get("scene", "")
            if scene:
                scene_counts[scene] += 1

        # 找出最频繁的场景
        if scene_counts:
            max_scene = max(scene_counts, key=scene_counts.get)
            count = scene_counts[max_scene]

            if count >= 3:
                return {
                    "count": count,
                    "description": f"频繁使用场景 '{max_scene}'",
                    "related_nodes": [max_scene],
                    "suggestions": [f"建议为 '{max_scene}' 创建快捷方式或自动化流程"]
                }

        return None

    def reason(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        推理接口

        Args:
            query: 查询
            context: 上下文

        Returns:
            推理结果
        """
        result = {
            "query": query,
            "reasoning_type": "unknown",
            "results": [],
            "insights": [],
            "confidence": 0.0
        }

        # 分析查询类型
        query_lower = query.lower()

        # 因果推理
        if any(keyword in query_lower for keyword in ["原因", "因果", "导致", "cause", "why", "因为"]):
            result["reasoning_type"] = "causal"
            # 尝试从知识图谱中查找因果链
            start_node = context.get("focus_node", "user_default") if context else "user_default"
            chains = self.analyze_causal_chain(start_node)
            result["results"] = [
                {
                    "cause": chain.cause,
                    "effect": chain.effect,
                    "chain": chain.chain,
                    "confidence": chain.confidence
                }
                for chain in chains
            ]
            result["confidence"] = 0.7 if chains else 0.3

        # 类比推理
        elif any(keyword in query_lower for keyword in ["类似", "相似", "像", "analog", "like", "similar"]):
            result["reasoning_type"] = "analogy"
            concept = context.get("concept", query) if context else query
            analogies = self.find_analogies(concept)
            result["results"] = [
                {
                    "source": a.source_concept,
                    "target": a.target_concept,
                    "similarity": a.similarity,
                    "explanation": a.explanation
                }
                for a in analogies
            ]
            result["confidence"] = 0.6 if analogies else 0.3

        # 关联发现
        elif any(keyword in query_lower for keyword in ["关联", "关系", "connection", "relationship", "发现"]):
            result["reasoning_type"] = "association"
            node = context.get("focus_node", "user_default") if context else "user_default"
            associations = self.discover_hidden_associations(node)
            result["results"] = associations
            result["confidence"] = 0.7 if associations else 0.4

        # 主动洞察
        elif any(keyword in query_lower for keyword in ["洞察", "建议", "insight", "suggest", "主动"]):
            result["reasoning_type"] = "insight"
            insights = self.generate_proactive_insights(context)
            result["insights"] = [
                {
                    "id": i.id,
                    "title": i.title,
                    "description": i.description,
                    "confidence": i.confidence,
                    "suggested_actions": i.suggested_actions
                }
                for i in insights
            ]
            result["confidence"] = 0.8 if insights else 0.5

        # 通用推理
        else:
            result["reasoning_type"] = "general"
            # 返回知识图谱统计和推荐
            stats = self.kg.get_graph_statistics()
            result["results"] = [stats]
            result["confidence"] = 0.6

        return result

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "engine": "enhanced_knowledge_reasoning",
            "version": "1.0",
            "knowledge_graph_stats": self.kg.get_graph_statistics(),
            "insights_count": len(self.insights_history),
            "capabilities": [
                "causal_chain_analysis",
                "analogy_finding",
                "hidden_association_discovery",
                "proactive_insight_generation"
            ]
        }


# ==================== CLI 接口 ====================

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="增强智能知识推理引擎")
    parser.add_argument("command", choices=["reason", "causal", "analogy", "association", "insight", "status"],
                        help="命令")
    parser.add_argument("--query", "-q", help="查询内容")
    parser.add_argument("--context", "-c", help="上下文 JSON")
    parser.add_argument("--node", "-n", help="节点 ID")
    parser.add_argument("--concept", help="概念")
    parser.add_argument("--depth", "-d", type=int, default=2, help="深度")

    args = parser.parse_args()

    # 创建引擎实例
    engine = EnhancedKnowledgeReasoningEngine()

    if args.command == "reason":
        context = json.loads(args.context) if args.context else None
        result = engine.reason(args.query or "通用推理", context)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "causal":
        chains = engine.analyze_causal_chain(args.node or "user_default", args.depth)
        print(json.dumps([{
            "cause": c.cause,
            "effect": c.effect,
            "chain": c.chain,
            "confidence": c.confidence
        } for c in chains], ensure_ascii=False, indent=2))

    elif args.command == "analogy":
        analogies = engine.find_analogies(args.concept or "test")
        print(json.dumps([{
            "source": a.source_concept,
            "target": a.target_concept,
            "similarity": a.similarity,
            "explanation": a.explanation
        } for a in analogies], ensure_ascii=False, indent=2))

    elif args.command == "association":
        associations = engine.discover_hidden_associations(args.node or "user_default", args.depth)
        print(json.dumps(associations, ensure_ascii=False, indent=2))

    elif args.command == "insight":
        insights = engine.generate_proactive_insights()
        print(json.dumps([{
            "id": i.id,
            "title": i.title,
            "description": i.description,
            "confidence": i.confidence,
            "suggested_actions": i.suggested_actions
        } for i in insights], ensure_ascii=False, indent=2))

    elif args.command == "status":
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()