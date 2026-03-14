#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化知识图谱深度推理引擎 (Evolution Knowledge Graph Reasoning Engine)
version 1.0.0

让系统能够跨轮次构建进化知识图谱，实现知识间的深度关联推理，从海量进化历史中主动发现隐藏的优化机会和创新模式。

功能：
1. 进化知识图谱构建 - 将历史进化数据转为知识图谱结构
2. 知识关联分析 - 发现跨领域、跨时间的关联
3. 隐藏机会挖掘 - 通过图推理发现隐藏优化点
4. 创新模式识别 - 识别创新模式和机会
5. 深度推理引擎 - 支持多跳推理和路径分析
6. 与 do.py 深度集成

依赖：
- evolution_knowledge_inheritance_engine.py (round 240)
- evolution_meta_pattern_discovery.py (round 244)
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

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class KnowledgeGraphNode:
    """知识图谱节点"""

    def __init__(self, node_id: str, node_type: str, label: str, properties: Dict = None):
        self.id = node_id
        self.type = node_type
        self.label = label
        self.properties = properties or {}
        self.connections: List[Tuple[str, str]] = []  # (target_id, relation_type)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type,
            "label": self.label,
            "properties": self.properties,
            "connections": self.connections
        }


class KnowledgeGraphEdge:
    """知识图谱边"""

    def __init__(self, source: str, target: str, relation: str, weight: float = 1.0):
        self.source = source
        self.target = target
        self.relation = relation
        self.weight = weight

    def to_dict(self) -> Dict:
        return {
            "source": self.source,
            "target": self.target,
            "relation": self.relation,
            "weight": self.weight
        }


class EvolutionKnowledgeGraphReasoning:
    """智能全场景进化知识图谱深度推理引擎"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.runtime_dir = self.project_root / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.logs_dir = self.runtime_dir / "logs"
        self.version = "1.0.0"

        # 知识图谱存储
        self.graph_dir = self.runtime_dir / "knowledge_graph"
        self.graph_dir.mkdir(exist_ok=True)

        self.graph_file = self.graph_dir / "evolution_kg.json"
        self.opportunities_file = self.graph_dir / "hidden_opportunities.json"
        self.innovation_file = self.graph_dir / "innovation_patterns.json"

        # 图数据
        self.nodes: Dict[str, KnowledgeGraphNode] = {}
        self.edges: List[KnowledgeGraphEdge] = []

        # 加载已有图谱
        self._load_graph()

        # 领域关键词映射
        self.domain_keywords = {
            "知识": ["知识", "图谱", "推理", "传承"],
            "决策": ["决策", "规划", "意图", "目标"],
            "执行": ["执行", "自动化", "编排", "调度"],
            "协同": ["协同", "协作", "多智能体", "社会化"],
            "优化": ["优化", "效率", "效能", "性能"],
            "健康": ["健康", "自愈", "诊断", "保障"],
            "学习": ["学习", "适应", "元学习", "策略"],
            "创新": ["创新", "创造", "发现", "机会"],
            "预测": ["预测", "预防", "趋势", "洞察"],
            "服务": ["服务", "推荐", "场景", "意图"],
        }

    def _load_graph(self):
        """加载已有图谱"""
        if self.graph_file.exists():
            try:
                with open(self.graph_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 加载节点
                    for node_data in data.get("nodes", []):
                        node = KnowledgeGraphNode(
                            node_data["id"],
                            node_data["type"],
                            node_data["label"],
                            node_data.get("properties", {})
                        )
                        node.connections = node_data.get("connections", [])
                        self.nodes[node.id] = node
                    # 加载边
                    for edge_data in data.get("edges", []):
                        edge = KnowledgeGraphEdge(
                            edge_data["source"],
                            edge_data["target"],
                            edge_data["relation"],
                            edge_data.get("weight", 1.0)
                        )
                        self.edges.append(edge)
            except Exception as e:
                print(f"加载图谱失败: {e}")

    def _save_graph(self):
        """保存图谱"""
        data = {
            "version": self.version,
            "last_updated": datetime.now().isoformat(),
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges]
        }
        with open(self.graph_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_evolution_history(self, limit: int = 100) -> List[Dict]:
        """加载进化历史"""
        evolution_files = sorted(
            self.state_dir.glob("evolution_completed_*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )[:limit]

        history = []
        for f in evolution_files:
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    history.append(data)
            except Exception as e:
                print(f"Warning: Failed to load {f}: {e}")

        # 按轮次排序
        history.sort(key=lambda x: x.get('loop_round', 0))
        return history

    def build_knowledge_graph(self, history: List[Dict] = None) -> Dict[str, Any]:
        """
        构建进化知识图谱
        返回：图谱结构
        """
        if history is None:
            history = self.load_evolution_history()

        # 清空现有图谱
        self.nodes.clear()
        self.edges.clear()

        # 创建节点：进化轮次
        round_nodes = {}
        for entry in history:
            round_num = entry.get("loop_round", 0)
            if round_num == 0:
                continue

            node_id = f"round_{round_num}"
            goal = entry.get("current_goal", "")
            status = entry.get("status", "unknown")

            # 提取领域
            domains = self._extract_domains(goal)

            node = KnowledgeGraphNode(
                node_id=node_id,
                node_type="evolution_round",
                label=goal[:100] if goal else f"Round {round_num}",
                properties={
                    "round": round_num,
                    "status": status,
                    "domains": domains,
                    "goal": goal,
                    "done": entry.get("做了什么", []),
                    "timestamp": entry.get("timestamp", "")
                }
            )
            self.nodes[node_id] = node
            round_nodes[round_num] = node_id

        # 创建领域节点
        domain_nodes = {}
        for domain in self.domain_keywords.keys():
            node_id = f"domain_{domain}"
            node = KnowledgeGraphNode(
                node_id=node_id,
                node_type="domain",
                label=f"{domain}领域",
                properties={"domain": domain}
            )
            self.nodes[node_id] = node
            domain_nodes[domain] = node_id

        # 创建边：进化之间的关联
        for i, entry in enumerate(history):
            round_num = entry.get("loop_round", 0)
            if round_num == 0:
                continue

            source_id = f"round_{round_num}"
            if source_id not in self.nodes:
                continue

            source_node = self.nodes[source_id]
            domains = source_node.properties.get("domains", [])

            # 连接领域
            for domain in domains:
                if domain in domain_nodes:
                    self.edges.append(KnowledgeGraphEdge(
                        source_id,
                        domain_nodes[domain],
                        "belongs_to",
                        1.0
                    ))

            # 连接相邻轮次（时间序列）
            if i > 0:
                prev_round = history[i - 1].get("loop_round", 0)
                if prev_round > 0:
                    self.edges.append(KnowledgeGraphEdge(
                        f"round_{prev_round}",
                        source_id,
                        "leads_to",
                        0.8
                    ))

            # 基于内容相似性连接
            for j, other_entry in enumerate(history[i+1:], i+1):
                other_round = other_entry.get("loop_round", 0)
                if other_round == 0:
                    continue

                other_goal = other_entry.get("current_goal", "")
                other_domains = self._extract_domains(other_goal)

                # 计算领域重叠
                overlap = len(set(domains) & set(other_domains))
                if overlap > 0:
                    weight = overlap * 0.5
                    self.edges.append(KnowledgeGraphEdge(
                        source_id,
                        f"round_{other_round}",
                        "related_to",
                        weight
                    ))

        # 保存图谱
        self._save_graph()

        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "domain_nodes": len(domain_nodes),
            "round_nodes": len(round_nodes)
        }

    def _extract_domains(self, goal: str) -> List[str]:
        """从目标中提取领域"""
        domains = []
        goal_lower = goal.lower()

        for domain, keywords in self.domain_keywords.items():
            for kw in keywords:
                if kw.lower() in goal_lower:
                    domains.append(domain)
                    break

        return domains if domains else ["其他"]

    def analyze_relationships(self) -> Dict[str, Any]:
        """
        分析知识关联
        返回：关联分析结果
        """
        analysis = {
            "domain_relationships": defaultdict(list),
            "cross_domain_patterns": [],
            "temporal_patterns": [],
            "influence_chains": []
        }

        # 领域关联分析
        domain_edges = defaultdict(list)
        for edge in self.edges:
            if edge.source.startswith("domain_") or edge.target.startswith("domain_"):
                key = tuple(sorted([edge.source, edge.target]))
                domain_edges[key].append(edge.relation)

        for (d1, d2), relations in domain_edges.items():
            d1_name = d1.replace("domain_", "")
            d2_name = d2.replace("domain_", "")
            analysis["domain_relationships"][f"{d1_name} -> {d2_name}"] = list(set(relations))

        # 跨域模式识别
        domain_nodes = {k: v for k, v in self.nodes.items() if v.type == "domain"}
        domain_list = list(domain_nodes.keys())

        # 找出经常一起出现的领域对
        domain_cooccurrence = defaultdict(int)
        for edge in self.edges:
            if edge.relation == "related_to":
                source_node = self.nodes.get(edge.source)
                target_node = self.nodes.get(edge.target)
                if source_node and target_node:
                    source_domains = source_node.properties.get("domains", [])
                    target_domains = target_node.properties.get("domains", [])
                    for d1 in source_domains:
                        for d2 in target_domains:
                            if d1 != d2:
                                domain_cooccurrence[frozenset([d1, d2])] += 1

        # 找出高共现的跨域模式
        for domains, count in domain_cooccurrence.items():
            if count >= 2:
                analysis["cross_domain_patterns"].append({
                    "domains": list(domains),
                    "cooccurrence_count": count,
                    "pattern_type": "frequent_cooccurrence"
                })

        # 时间序列模式
        rounds = sorted([n for n in self.nodes.keys() if n.startswith("round_")],
                       key=lambda x: int(x.split("_")[1]))

        for i in range(len(rounds) - 1):
            source = self.nodes[rounds[i]]
            target = self.nodes[rounds[i + 1]]

            # 检查是否有关联边
            has_lead = any(e.source == rounds[i] and e.target == rounds[i+1]
                          for e in self.edges if e.relation == "leads_to")

            if has_lead:
                source_domains = source.properties.get("domains", [])
                target_domains = target.properties.get("domains", [])

                if source_domains == target_domains:
                    analysis["temporal_patterns"].append({
                        "from_round": rounds[i],
                        "to_round": rounds[i + 1],
                        "pattern": "sequential_enhancement",
                        "domain": source_domains[0] if source_domains else "unknown"
                    })
                elif source_domains and target_domains:
                    analysis["temporal_patterns"].append({
                        "from_round": rounds[i],
                        "to_round": rounds[i + 1],
                        "pattern": "domain_evolution",
                        "from_domain": source_domains[0],
                        "to_domain": target_domains[0]
                    })

        # 影响链分析
        for start_round in rounds[:10]:  # 分析最近10轮的影响
            chain = self._find_influence_chain(start_round, max_depth=3)
            if len(chain) >= 2:
                analysis["influence_chains"].append(chain)

        return analysis

    def _find_influence_chain(self, start_id: str, max_depth: int = 3) -> List[Dict]:
        """查找影响链"""
        chain = []
        visited = {start_id}
        current = start_id
        depth = 0

        while depth < max_depth:
            next_edge = None
            for edge in self.edges:
                if edge.source == current and edge.target not in visited:
                    if edge.relation in ["leads_to", "related_to"]:
                        next_edge = edge
                        break

            if not next_edge:
                break

            chain.append({
                "from": current,
                "to": next_edge.target,
                "relation": next_edge.relation
            })

            visited.add(next_edge.target)
            current = next_edge.target
            depth += 1

        return chain

    def discover_hidden_opportunities(self, history: List[Dict] = None) -> List[Dict[str, Any]]:
        """
        发现隐藏的优化机会
        通过图推理发现潜在的优化点
        """
        if history is None:
            history = self.load_evolution_history()

        opportunities = []

        # 分析1：重复领域但低效的进化
        domain_rounds = defaultdict(list)
        for entry in history:
            goal = entry.get("current_goal", "")
            round_num = entry.get("loop_round", 0)
            domains = self._extract_domains(goal)
            for domain in domains:
                domain_rounds[domain].append({
                    "round": round_num,
                    "goal": goal,
                    "status": entry.get("status", "unknown")
                })

        for domain, rounds in domain_rounds.items():
            if len(rounds) >= 3:
                # 检查是否每次都是相似的目标
                goals = [r["goal"][:50] for r in rounds]
                if len(set(goals)) < len(goals) * 0.5:
                    opportunities.append({
                        "type": "repeated_similar_evolution",
                        "domain": domain,
                        "count": len(rounds),
                        "description": f"{domain}领域存在多次相似进化，可能存在重复工作",
                        "suggestion": f"建议合并或深入{domain}领域的进化，避免重复",
                        "priority": "high"
                    })

        # 分析2：缺失的领域组合
        covered_combinations = set()
        for entry in history:
            goal = entry.get("current_goal", "")
            domains = self._extract_domains(goal)
            if len(domains) >= 2:
                covered_combinations.add(frozenset(domains))

        # 建议有价值的组合
        potential_combos = []
        all_domains = list(self.domain_keywords.keys())
        for i, d1 in enumerate(all_domains):
            for d2 in all_domains[i+1:]:
                combo = frozenset([d1, d2])
                if combo not in covered_combinations:
                    potential_combos.append(list(combo))

        if potential_combos:
            opportunities.append({
                "type": "missing_domain_combination",
                "domains": potential_combos[:5],
                "description": "发现未探索的领域组合，可能产生创新",
                "suggestion": "尝试跨领域集成，如" + " + ".join(potential_combos[0]),
                "priority": "medium"
            })

        # 分析3：低完成率的进化类型
        status_counts = defaultdict(lambda: {"total": 0, "completed": 0})
        for entry in history:
            goal = entry.get("current_goal", "")
            domains = self._extract_domains(goal)
            status = entry.get("status", "unknown")

            for domain in domains:
                status_counts[domain]["total"] += 1
                if status == "completed":
                    status_counts[domain]["completed"] += 1

        for domain, counts in status_counts.items():
            if counts["total"] >= 2:
                completion_rate = counts["completed"] / counts["total"]
                if completion_rate < 0.5:
                    opportunities.append({
                        "type": "low_completion_domain",
                        "domain": domain,
                        "completion_rate": completion_rate,
                        "description": f"{domain}领域进化完成率较低({completion_rate:.1%})",
                        "suggestion": f"需要改进{domain}领域的进化策略或执行方法",
                        "priority": "medium"
                    })

        # 分析4：长时间未进化的领域
        if history:
            latest_round = max(history, key=lambda x: x.get("loop_round", 0))
            latest_domains = self._extract_domains(latest_round.get("current_goal", ""))

            for domain in all_domains:
                if domain not in latest_domains:
                    # 检查这个领域是否在历史中有记录
                    domain_history = [e for e in history
                                    if domain in self._extract_domains(e.get("current_goal", ""))]
                    if domain_history:
                        last_round = max(domain_history, key=lambda x: x.get("loop_round", 0))
                        gap = latest_round.get("loop_round", 0) - last_round.get("loop_round", 0)
                        if gap > 30:  # 超过30轮未进化
                            opportunities.append({
                                "type": "stagnant_domain",
                                "domain": domain,
                                "last_round": last_round.get("loop_round", 0),
                                "gap": gap,
                                "description": f"{domain}领域已{gap}轮未进化",
                                "suggestion": f"建议重新关注{domain}领域，探索新的进化方向",
                                "priority": "low"
                            })

        # 保存机会
        with open(self.opportunities_file, 'w', encoding='utf-8') as f:
            json.dump(opportunities, f, ensure_ascii=False, indent=2)

        return opportunities

    def identify_innovation_patterns(self, history: List[Dict] = None) -> List[Dict[str, Any]]:
        """
        识别创新模式
        发现有价值的创新进化方向
        """
        if history is None:
            history = self.load_evolution_history()

        patterns = []

        # 分析1：首创性进化（首次出现的领域组合）
        seen_combinations = set()
        first_occurrences = []

        for entry in history:
            goal = entry.get("current_goal", "")
            round_num = entry.get("loop_round", 0)
            domains = self._extract_domains(goal)

            combo = frozenset(domains)
            if combo not in seen_combinations:
                seen_combinations.add(combo)
                first_occurrences.append({
                    "round": round_num,
                    "domains": domains,
                    "goal": goal[:100]
                })

        # 找出真正的创新（多个领域的首次组合）
        for fc in first_occurrences:
            if len(fc["domains"]) >= 2:
                patterns.append({
                    "type": "first_integration",
                    "round": fc["round"],
                    "domains": fc["domains"],
                    "description": f"首次跨领域集成: {'+'.join(fc['domains'])}",
                    "value": "high"
                })

        # 分析2：成功的快速连续进化
        for i in range(len(history) - 1):
            current = history[i]
            next_entry = history[i + 1]

            current_round = current.get("loop_round", 0)
            next_round = next_entry.get("loop_round", 0)

            if next_round - current_round <= 5:  # 5轮内
                if current.get("status") == "completed" and next_entry.get("status") == "completed":
                    current_domains = self._extract_domains(current.get("current_goal", ""))
                    next_domains = self._extract_domains(next_entry.get("current_goal", ""))

                    if current_domains != next_domains:
                        patterns.append({
                            "type": "rapid_succession",
                            "rounds": [current_round, next_round],
                            "domains": list(set(current_domains + next_domains)),
                            "description": "连续两轮不同领域快速完成",
                            "value": "medium"
                        })

        # 分析3：自我增强型进化（同一领域多轮深化）
        domain_rounds = defaultdict(list)
        for entry in history:
            goal = entry.get("current_goal", "")
            round_num = entry.get("loop_round", 0)
            domains = self._extract_domains(goal)
            for domain in domains:
                domain_rounds[domain].append(round_num)

        for domain, rounds in domain_rounds.items():
            rounds_sorted = sorted(rounds)
            consecutive_count = 1
            max_consecutive = 1

            for i in range(1, len(rounds_sorted)):
                if rounds_sorted[i] - rounds_sorted[i-1] <= 3:
                    consecutive_count += 1
                    max_consecutive = max(max_consecutive, consecutive_count)
                else:
                    consecutive_count = 1

            if max_consecutive >= 3:
                patterns.append({
                    "type": "deep_enhancement",
                    "domain": domain,
                    "consecutive_rounds": max_consecutive,
                    "description": f"{domain}领域连续{max_consecutive}轮深化",
                    "value": "high"
                })

        # 保存创新模式
        with open(self.innovation_file, 'w', encoding='utf-8') as f:
            json.dump(patterns, f, ensure_ascii=False, indent=2)

        return patterns

    def reason_opportunities(self, max_depth: int = 3) -> List[Dict[str, Any]]:
        """
        深度推理：基于图谱发现隐藏机会
        使用多跳推理发现潜在优化点
        """
        reasoning_results = []

        # 1. 路径分析：找出关键影响路径
        key_paths = self._analyze_key_paths(max_depth)
        if key_paths:
            reasoning_results.append({
                "type": "key_influence_paths",
                "count": len(key_paths),
                "paths": key_paths[:5],
                "description": "发现关键影响路径，可能揭示进化方向"
            })

        # 2. 中心性分析：找出核心节点
        central_nodes = self._analyze_centrality()
        if central_nodes:
            reasoning_results.append({
                "type": "central_nodes",
                "nodes": central_nodes[:5],
                "description": "核心进化节点，引领领域发展方向"
            })

        # 3. 社区检测：发现领域簇
        communities = self._detect_communities()
        if communities:
            reasoning_results.append({
                "type": "domain_communities",
                "communities": communities,
                "description": "发现领域社区，可能存在协同进化机会"
            })

        return reasoning_results

    def _analyze_key_paths(self, max_depth: int) -> List[List[str]]:
        """分析关键路径"""
        paths = []
        round_nodes = [n for n in self.nodes.keys() if n.startswith("round_")]

        for start in round_nodes[:10]:  # 从最近10轮开始
            path = self._find_influence_chain(start, max_depth)
            if len(path) >= 2:
                full_path = [start]
                for step in path:
                    full_path.append(step["to"])
                paths.append(full_path)

        # 按长度排序
        paths.sort(key=len, reverse=True)
        return paths[:10]

    def _analyze_centrality(self) -> List[Dict]:
        """分析节点中心性"""
        # 统计每个节点的连接数
        connection_count = defaultdict(int)
        for edge in self.edges:
            connection_count[edge.source] += 1
            connection_count[edge.target] += 1

        # 排序
        sorted_nodes = sorted(connection_count.items(), key=lambda x: x[1], reverse=True)

        central = []
        for node_id, count in sorted_nodes[:10]:
            if node_id in self.nodes:
                node = self.nodes[node_id]
                central.append({
                    "id": node_id,
                    "label": node.label[:50],
                    "connections": count,
                    "type": node.type
                })

        return central

    def _detect_communities(self) -> List[List[str]]:
        """简单社区检测"""
        # 基于领域聚类
        domain_nodes = {k: v for k, v in self.nodes.items() if v.type == "domain"}

        communities = []
        visited = set()

        for domain_id, node in domain_nodes.items():
            community = [domain_id]

            # 找与该领域直接相关的进化轮次
            for edge in self.edges:
                if edge.source == domain_id and edge.target not in visited:
                    community.append(edge.target)
                elif edge.target == domain_id and edge.source not in visited:
                    community.append(edge.source)

            if len(community) >= 2:
                communities.append(community)

        return communities[:5]

    def get_status(self) -> Dict[str, Any]:
        """获取图谱状态"""
        return {
            "version": self.version,
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "domain_nodes": len([n for n in self.nodes.values() if n.type == "domain"]),
            "round_nodes": len([n for n in self.nodes.values() if n.type == "evolution_round"]),
            "last_updated": datetime.now().isoformat()
        }

    def run_full_analysis(self) -> Dict[str, Any]:
        """运行完整分析"""
        # 加载历史
        history = self.load_evolution_history()

        # 构建图谱
        build_result = self.build_knowledge_graph(history)

        # 分析关联
        relationships = self.analyze_relationships()

        # 发现隐藏机会
        opportunities = self.discover_hidden_opportunities(history)

        # 识别创新模式
        innovations = self.identify_innovation_patterns(history)

        # 深度推理
        reasoning = self.reason_opportunities()

        return {
            "graph_stats": build_result,
            "relationships": relationships,
            "opportunities": opportunities,
            "innovations": innovations,
            "reasoning": reasoning,
            "status": self.get_status()
        }


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(
        description='智能全场景进化知识图谱深度推理引擎'
    )
    parser.add_argument('command', nargs='?', default='status',
                       choices=['status', 'build', 'analyze', 'opportunities',
                               'innovations', 'reasoning', 'full'],
                       help='要执行的命令')
    parser.add_argument('--goal', '-g', type=str, default='',
                       help='当前进化目标（用于分析相关性）')
    parser.add_argument('--depth', '-d', type=int, default=3,
                       help='推理深度')

    args = parser.parse_args()

    engine = EvolutionKnowledgeGraphReasoning()

    if args.command == 'status':
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.command == 'build':
        result = engine.build_knowledge_graph()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'analyze':
        result = engine.analyze_relationships()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'opportunities':
        result = engine.discover_hidden_opportunities()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'innovations':
        result = engine.identify_innovation_patterns()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'reasoning':
        result = engine.reason_opportunities(args.depth)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'full':
        result = engine.run_full_analysis()
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()