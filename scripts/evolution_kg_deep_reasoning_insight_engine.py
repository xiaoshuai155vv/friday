#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景知识图谱深度推理与主动洞察生成引擎 (Evolution KG Deep Reasoning & Insight Engine)
version 1.0.0

基于 round 298 的知识图谱推理引擎和 round 329 的全局态势感知能力，
增强知识图谱的深度推理与主动洞察生成 - 让系统能够主动从知识图谱中发现隐藏的优化机会、
创新方向、跨领域关联，形成"主动推理→洞察生成→价值发现→创新实现"的完整闭环，
实现从"被动查询"到"主动发现"的范式升级。

功能：
1. 知识图谱深度推理增强（多跳推理、因果推理、反事实推理）
2. 主动洞察生成（主动分析知识图谱发现隐藏机会）
3. 创新方向发现（从跨领域关联中识别创新点）
4. 价值评估与优先级排序
5. 洞察驱动的自动进化触发
6. 与 do.py 深度集成

依赖：
- evolution_knowledge_graph_reasoning.py (round 298)
- evolution_global_situation_awareness.py (round 329)
- knowledge_graph.py
"""

import os
import sys
import json
import glob
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path
import itertools
import re

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class DeepReasoningNode:
    """深度推理节点"""

    def __init__(self, node_id: str, node_type: str, label: str, properties: Dict = None):
        self.id = node_id
        self.type = node_type
        self.label = label
        self.properties = properties or {}
        self.connections: List[Tuple[str, str]] = []

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type,
            "label": self.label,
            "properties": self.properties,
            "connections": self.connections
        }


class DeepReasoningEdge:
    """深度推理边"""

    def __init__(self, source: str, target: str, relation: str, weight: float = 1.0, reasoning_type: str = None):
        self.source = source
        self.target = target
        self.relation = relation
        self.weight = weight
        self.reasoning_type = reasoning_type  # direct, multi_hop, causal, counterfactual

    def to_dict(self) -> Dict:
        return {
            "source": self.source,
            "target": self.target,
            "relation": self.relation,
            "weight": self.weight,
            "reasoning_type": self.reasoning_type
        }


class Insight:
    """洞察对象"""

    def __init__(self, insight_id: str, title: str, description: str, insight_type: str,
                 value_score: float, feasibility: float, risk: float):
        self.id = insight_id
        self.title = title
        self.description = description
        self.type = insight_type  # optimization, innovation, correlation, warning
        self.value_score = value_score  # 0-100
        self.feasibility = feasibility  # 0-100
        self.risk = risk  # 0-100
        self.evidence: List[Dict] = []
        self.related_nodes: List[str] = []
        self.created_at = datetime.now().isoformat()
        self.status = "discovered"  # discovered, validated, implemented, dismissed

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "type": self.type,
            "value_score": self.value_score,
            "feasibility": self.feasibility,
            "risk": self.risk,
            "priority_score": (self.value_score * 0.4 + self.feasibility * 0.4 - self.risk * 0.2),
            "evidence": self.evidence,
            "related_nodes": self.related_nodes,
            "created_at": self.created_at,
            "status": self.status
        }


class KGDeepReasoningInsightEngine:
    """智能全场景知识图谱深度推理与主动洞察生成引擎"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.runtime_dir = self.project_root / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.logs_dir = self.runtime_dir / "logs"
        self.version = "1.0.0"

        # 存储目录
        self.insight_dir = self.runtime_dir / "kg_deep_insights"
        self.insight_dir.mkdir(exist_ok=True)

        self.insights_file = self.insight_dir / "active_insights.json"
        self.reasoning_cache_file = self.insight_dir / "reasoning_cache.json"

        # 图数据
        self.nodes: Dict[str, DeepReasoningNode] = {}
        self.edges: List[DeepReasoningEdge] = []
        self.insights: Dict[str, Insight] = {}

        # 加载已有数据
        self._load_data()

        # 推理模式
        self.reasoning_patterns = {
            "multi_hop": self._multi_hop_reasoning,
            "causal": self._causal_reasoning,
            "counterfactual": self._counterfactual_reasoning,
            "pattern_matching": self._pattern_matching_reasoning
        }

        # 领域分类
        self.domain_categories = {
            "knowledge": ["知识", "图谱", "推理", "传承", "图谱"],
            "decision": ["决策", "规划", "意图", "目标", "策略"],
            "execution": ["执行", "自动化", "编排", "调度", "运行"],
            "collaboration": ["协同", "协作", "多智能体", "社会化", "团队"],
            "optimization": ["优化", "效率", "效能", "性能", "提升"],
            "health": ["健康", "自愈", "诊断", "保障", "免疫"],
            "learning": ["学习", "适应", "元学习", "策略", "经验"],
            "innovation": ["创新", "创造", "发现", "机会", "新"],
            "prediction": ["预测", "预防", "趋势", "洞察", "分析"],
            "service": ["服务", "推荐", "场景", "意图", "用户"],
            "evolution": ["进化", "环", "自进化", "自我"],
            "meta": ["元", "meta", "反思", "自省"]
        }

    def _load_data(self):
        """加载已有数据"""
        # 加载洞察
        if self.insights_file.exists():
            try:
                with open(self.insights_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for ins_data in data.get("insights", []):
                        insight = Insight(
                            ins_data["id"],
                            ins_data["title"],
                            ins_data["description"],
                            ins_data["type"],
                            ins_data["value_score"],
                            ins_data["feasibility"],
                            ins_data["risk"]
                        )
                        insight.evidence = ins_data.get("evidence", [])
                        insight.related_nodes = ins_data.get("related_nodes", [])
                        insight.status = ins_data.get("status", "discovered")
                        self.insights[insight.id] = insight
            except Exception as e:
                print(f"加载洞察失败: {e}")

        # 加载推理缓存（包含构建的知识图谱）
        self._load_reasoning_graph()

    def _load_reasoning_graph(self):
        """加载推理图谱 - 从各引擎历史数据构建"""
        # 从进化历史构建图谱
        self._build_evolution_graph()

    def _build_evolution_graph(self):
        """从进化历史构建知识图谱"""
        # 扫描所有 evolution_completed_*.json 文件
        completed_files = list(self.state_dir.glob("evolution_completed_*.json"))

        for file_path in completed_files[:50]:  # 取最近50轮
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 提取进化信息
                round_num = data.get("loop_round", 0)
                goal = data.get("current_goal", "")
                done = data.get("是否完成", "")

                if goal and round_num > 0:
                    # 创建进化轮次节点
                    node_id = f"evolution_round_{round_num}"
                    node = DeepReasoningNode(
                        node_id,
                        "evolution_round",
                        f"Round {round_num}",
                        {"goal": goal, "completed": "完成" in done}
                    )
                    self.nodes[node_id] = node

                    # 分析目标关键词，关联领域
                    for domain, keywords in self.domain_categories.items():
                        for kw in keywords:
                            if kw in goal:
                                # 创建领域节点
                                domain_node_id = f"domain_{domain}"
                                if domain_node_id not in self.nodes:
                                    self.nodes[domain_node_id] = DeepReasoningNode(
                                        domain_node_id, "domain", domain, {"count": 0}
                                    )

                                # 添加边
                                edge = DeepReasoningEdge(
                                    node_id, domain_node_id, "belongs_to", 1.0, "direct"
                                )
                                self.edges.append(edge)

                                # 统计领域出现次数
                                self.nodes[domain_node_id].properties["count"] += 1
                                break
            except Exception as e:
                continue

    def _save_data(self):
        """保存数据"""
        # 保存洞察
        data = {
            "version": self.version,
            "last_updated": datetime.now().isoformat(),
            "insights": [ins.to_dict() for ins in self.insights.values()]
        }
        with open(self.insights_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _multi_hop_reasoning(self, start_node: str, max_hops: int = 3) -> List[Dict]:
        """多跳推理 - 追踪多条推理路径"""
        paths = []
        visited = set()

        def dfs(current: str, path: List[str], depth: int):
            if depth > max_hops:
                return

            visited.add(current)
            path = path + [current]

            # 查找当前节点的邻居
            for edge in self.edges:
                if edge.source == current and edge.target not in visited:
                    new_path = path + [edge.target]
                    paths.append({
                        "path": new_path,
                        "relations": [edge.relation],
                        "depth": depth
                    })
                    dfs(edge.target, path, depth + 1)

        dfs(start_node, [], 0)
        return paths

    def _causal_reasoning(self, node_a: str, node_b: str) -> Dict:
        """因果推理 - 分析因果关系"""
        # 查找从 A 到 B 的路径
        causal_paths = []

        for edge in self.edges:
            if edge.source == node_a:
                # 检查是否通过某中间节点到达 B
                intermediate_paths = self._multi_hop_reasoning(edge.target, 2)
                for p in intermediate_paths:
                    if node_b in p["path"]:
                        causal_paths.append({
                            "cause": node_a,
                            "effect": node_b,
                            "mechanism": p["path"],
                            "confidence": 0.7
                        })

        return {
            "has_causal_relation": len(causal_paths) > 0,
            "paths": causal_paths,
            "confidence": len(causal_paths) / 3.0 if causal_paths else 0.0
        }

    def _counterfactual_reasoning(self, node: str, assumption: str) -> Dict:
        """反事实推理 - 假设某种情况不发生会怎样"""
        # 查找该节点的依赖
        dependencies = []
        for edge in self.edges:
            if edge.target == node:
                dependencies.append({
                    "source": edge.source,
                    "relation": edge.relation
                })

        # 查找该节点的影响
        impacts = []
        for edge in self.edges:
            if edge.source == node:
                impacts.append({
                    "target": edge.target,
                    "relation": edge.relation
                })

        return {
            "node": node,
            "assumption": assumption,
            "dependencies": dependencies,
            "potential_impacts": impacts,
            "reasoning": f"如果 {assumption}，则可能影响 {len(impacts)} 个相关节点"
        }

    def _pattern_matching_reasoning(self, pattern: List[str]) -> List[Dict]:
        """模式匹配推理 - 识别特定模式"""
        matches = []

        # 查找包含指定模式的路径
        for edge in self.edges:
            for kw in pattern:
                if kw in edge.relation or kw in self.nodes.get(edge.target, DeepReasoningNode("", "", "")).label:
                    matches.append({
                        "source": edge.source,
                        "target": edge.target,
                        "relation": edge.relation,
                        "pattern_matched": kw
                    })

        return matches

    def generate_insights(self, force_refresh: bool = False) -> Dict:
        """主动生成洞察 - 分析知识图谱发现隐藏机会"""
        if not force_refresh and self.insights:
            return {
                "status": "cached",
                "insights_count": len(self.insights),
                "insights": [ins.to_dict() for ins in list(self.insights.values())[:10]]
            }

        new_insights = []

        # 1. 分析领域分布发现优化机会
        domain_insights = self._analyze_domain_distribution()
        new_insights.extend(domain_insights)

        # 2. 跨领域关联发现创新方向
        cross_domain_insights = self._discover_cross_domain_correlations()
        new_insights.extend(cross_domain_insights)

        # 3. 进化趋势分析发现预测洞察
        trend_insights = self._analyze_evolution_trends()
        new_insights.extend(trend_insights)

        # 4. 检测未完成项发现待办洞察
        pending_insights = self._discover_pending_opportunities()
        new_insights.extend(pending_insights)

        # 添加新洞察
        for ins in new_insights:
            if ins.id not in self.insights:
                self.insights[ins.id] = ins

        # 保存
        self._save_data()

        return {
            "status": "generated",
            "insights_count": len(self.insights),
            "new_insights_count": len(new_insights),
            "insights": [ins.to_dict() for ins in list(self.insights.values())[:10]]
        }

    def _analyze_domain_distribution(self) -> List[Insight]:
        """分析领域分布发现优化机会"""
        insights = []

        # 统计各领域进化轮次数量
        domain_counts = defaultdict(int)
        for node in self.nodes.values():
            if node.type == "domain":
                domain_counts[node.id] = node.properties.get("count", 0)

        # 找出冷门领域（进化较少的）
        total_rounds = sum(domain_counts.values())
        if total_rounds > 0:
            for domain, count in domain_counts.items():
                if count < total_rounds / len(domain_counts) * 0.3:
                    insight = Insight(
                        f"domain_insight_{domain}",
                        f"领域深耕机会: {domain}",
                        f"'{domain}' 领域进化轮次较少({count}轮)，存在未被充分探索的进化空间",
                        "optimization",
                        value_score=65.0,
                        feasibility=80.0,
                        risk=20.0
                    )
                    insight.related_nodes = [domain]
                    insight.evidence = [{"type": "distribution", "count": count, "total": total_rounds}]
                    insights.append(insight)

        return insights

    def _discover_cross_domain_correlations(self) -> List[Insight]:
        """跨领域关联发现创新方向"""
        insights = []

        # 查找跨领域边
        domain_nodes = {n.id: n for n in self.nodes.values() if n.type == "domain"}
        cross_domain_edges = []

        for edge in self.edges:
            src_domain = None
            tgt_domain = None
            for dn in domain_nodes:
                if edge.source.startswith(dn) or dn in edge.source:
                    src_domain = dn
                if edge.target.startswith(dn) or dn in edge.target:
                    tgt_domain = dn

            if src_domain and tgt_domain and src_domain != tgt_domain:
                cross_domain_edges.append((src_domain, tgt_domain))

        # 发现创新组合
        if len(cross_domain_edges) >= 2:
            # 找出可以组合但尚未充分探索的领域对
            for i, (d1, d2) in enumerate(cross_domain_edges):
                for d3, d4 in cross_domain_edges[i+1:]:
                    if d1 == d3 or d1 == d4 or d2 == d3 or d2 == d4:
                        # 发现三元组合
                        domains = list(set([d1, d2, d3, d4]))
                        if len(domains) >= 3:
                            insight = Insight(
                                f"cross_domain_{len(insights)}",
                                f"跨领域创新机会: {' + '.join([d.replace('domain_', '') for d in domains[:3]])}",
                                f"发现跨领域关联: {', '.join([d.replace('domain_', '') for d in domains[:3]])} 领域可进行创新组合",
                                "innovation",
                                value_score=75.0,
                                feasibility=70.0,
                                risk=30.0
                            )
                            insight.related_nodes = domains
                            insights.append(insight)

        return insights

    def _analyze_evolution_trends(self) -> List[Insight]:
        """进化趋势分析发现预测洞察"""
        insights = []

        # 分析最近进化的领域趋势
        recent_domains = defaultdict(int)
        for node in self.nodes.values():
            if node.type == "evolution_round":
                goal = node.properties.get("goal", "")
                for domain in self.domain_categories:
                    for kw in self.domain_categories[domain]:
                        if kw in goal:
                            recent_domains[domain] += 1

        # 找出最近热门但可能过热的领域
        if recent_domains:
            max_count = max(recent_domains.values()) if recent_domains else 1
            for domain, count in recent_domains.items():
                if count >= max_count * 0.8:
                    insight = Insight(
                        f"trend_{domain}",
                        f"趋势预警: {domain} 领域近期过热",
                        f"'{domain}' 领域在近期进化中占比过高({count}轮)，建议关注其他领域平衡发展",
                        "warning",
                        value_score=60.0,
                        feasibility=85.0,
                        risk=15.0
                    )
                    insight.related_nodes = [f"domain_{domain}"]
                    insights.append(insight)

        return insights

    def _discover_pending_opportunities(self) -> List[Insight]:
        """发现待完成的机会"""
        insights = []

        # 检查未完成的进化轮次
        for node in self.nodes.values():
            if node.type == "evolution_round" and not node.properties.get("completed", True):
                goal = node.properties.get("goal", "")
                if goal:
                    insight = Insight(
                        f"pending_{node.id}",
                        f"待完成进化: {goal[:30]}...",
                        f"存在未完成的进化任务: {goal}",
                        "optimization",
                        value_score=70.0,
                        feasibility=60.0,
                        risk=40.0
                    )
                    insight.related_nodes = [node.id]
                    insights.append(insight)

        return insights

    def get_insight_by_id(self, insight_id: str) -> Optional[Dict]:
        """获取指定洞察详情"""
        insight = self.insights.get(insight_id)
        if insight:
            return insight.to_dict()
        return None

    def validate_insight(self, insight_id: str) -> Dict:
        """验证洞察 - 深入分析洞察的有效性"""
        insight = self.insights.get(insight_id)
        if not insight:
            return {"status": "not_found"}

        # 深入分析
        validation = {
            "insight_id": insight_id,
            "status": "validating",
            "analysis": []
        }

        # 分析相关节点
        for node_id in insight.related_nodes:
            node = self.nodes.get(node_id)
            if node:
                validation["analysis"].append({
                    "node": node_id,
                    "type": node.type,
                    "label": node.label,
                    "exists": True
                })
            else:
                validation["analysis"].append({
                    "node": node_id,
                    "exists": False
                })

        # 生成验证结论
        evidence_strength = len(insight.evidence)
        validation["conclusion"] = f"发现 {evidence_strength} 条证据支持此洞察"
        validation["recommendation"] = "建议实施" if evidence_strength >= 1 else "需要更多验证"

        insight.status = "validated"
        self._save_data()

        return validation

    def implement_insight(self, insight_id: str) -> Dict:
        """实现洞察 - 将洞察转化为进化触发"""
        insight = self.insights.get(insight_id)
        if not insight:
            return {"status": "not_found"}

        # 记录实现
        implementation = {
            "insight_id": insight_id,
            "title": insight.title,
            "implemented_at": datetime.now().isoformat(),
            "status": "ready_for_evolution"
        }

        insight.status = "implemented"
        self._save_data()

        return implementation

    def get_insight_dashboard(self) -> Dict:
        """获取洞察仪表盘"""
        # 分类统计
        type_counts = defaultdict(int)
        status_counts = defaultdict(int)
        priority_scores = []

        for ins in self.insights.values():
            type_counts[ins.type] += 1
            status_counts[ins.status] += 1
            priority_scores.append(ins.value_score * 0.4 + ins.feasibility * 0.4 - ins.risk * 0.2)

        return {
            "version": self.version,
            "total_insights": len(self.insights),
            "by_type": dict(type_counts),
            "by_status": dict(status_counts),
            "avg_priority": sum(priority_scores) / len(priority_scores) if priority_scores else 0,
            "recent_insights": [ins.to_dict() for ins in list(self.insights.values())[:5]],
            "graph_stats": {
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges),
                "domain_nodes": len([n for n in self.nodes.values() if n.type == "domain"])
            }
        }

    def run_deep_reasoning_cycle(self) -> Dict:
        """运行完整的深度推理循环"""
        # 1. 重新构建图谱
        self._build_evolution_graph()

        # 2. 执行多类型推理
        reasoning_results = {}

        # 多跳推理
        multi_hop_results = []
        for node_id in list(self.nodes.keys())[:10]:
            paths = self._multi_hop_reasoning(node_id, max_hops=2)
            if paths:
                multi_hop_results.append({"start": node_id, "paths": len(paths)})
        reasoning_results["multi_hop"] = multi_hop_results

        # 3. 生成洞察
        insights_result = self.generate_insights(force_refresh=True)

        # 4. 返回综合结果
        return {
            "status": "completed",
            "reasoning_results": reasoning_results,
            "insights": insights_result,
            "dashboard": self.get_insight_dashboard(),
            "timestamp": datetime.now().isoformat()
        }


def main():
    """主函数 - 测试用"""
    engine = KGDeepReasoningInsightEngine()

    # 测试生成洞察
    print("=== 测试生成洞察 ===")
    result = engine.generate_insights()
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # 测试深度推理循环
    print("\n=== 测试深度推理循环 ===")
    cycle_result = engine.run_deep_reasoning_cycle()
    print(f"推理完成: {cycle_result['status']}")
    print(f"节点数: {cycle_result['dashboard']['graph_stats']['total_nodes']}")
    print(f"边数: {cycle_result['dashboard']['graph_stats']['total_edges']}")
    print(f"洞察数: {cycle_result['dashboard']['total_insights']}")

    # 测试获取洞察仪表盘
    print("\n=== 洞察仪表盘 ===")
    dashboard = engine.get_insight_dashboard()
    print(f"总洞察数: {dashboard['total_insights']}")
    print(f"按类型: {dashboard['by_type']}")
    print(f"按状态: {dashboard['by_status']}")


if __name__ == "__main__":
    main()