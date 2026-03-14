#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环跨轮次知识深度整合与智能推理引擎

在 round 372 的决策-执行闭环集成基础上，进一步增强跨轮次知识深度整合
与智能推理能力。让系统能够跨 370+ 轮进化历史深度整合知识，构建进化知识
网络图谱，实现跨轮次知识关联分析、进化趋势预测、创新机会发现，让系统不仅
能执行进化，还能从历史进化中学习并发现新的进化方向。

Version: 1.0.0
Author: Auto Evolution System
"""

import json
import os
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import defaultdict

# 基础路径配置
SCRIPT_DIR = Path(__file__).parent
RUNTIME_DIR = SCRIPT_DIR.parent / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"
REFERENCES_DIR = SCRIPT_DIR.parent / "references"


class EvolutionKnowledgeDeepIntegrationEngine:
    """
    跨轮次知识深度整合与智能推理引擎

    核心能力：
    1. 跨轮次进化知识自动收集与结构化（历史进化目标、执行结果、经验教训）
    2. 进化知识网络图谱构建（知识节点、关联关系、权重更新）
    3. 跨轮次知识关联分析与趋势预测
    4. 创新机会智能发现（基于知识组合、模式识别）
    5. 与决策引擎的深度集成（知识驱动的智能决策）
    """

    def __init__(self):
        self.engine_name = "knowledge_deep_integration"
        self.version = "1.0.0"
        self.knowledge_graph_file = STATE_DIR / f"{self.engine_name}_knowledge_graph.json"
        self.analysis_file = STATE_DIR / f"{self.engine_name}_analysis.json"
        self.opportunities_file = STATE_DIR / f"{self.engine_name}_opportunities.json"
        self.load_state()

    def load_state(self):
        """加载引擎状态"""
        # 加载知识图谱
        if self.knowledge_graph_file.exists():
            with open(self.knowledge_graph_file, 'r', encoding='utf-8') as f:
                self.knowledge_graph = json.load(f)
        else:
            self.knowledge_graph = {
                "nodes": {},  # 节点ID -> 节点信息
                "edges": [],  # 边列表
                "last_updated": None,
                "version": self.version
            }

        # 加载分析结果
        if self.analysis_file.exists():
            with open(self.analysis_file, 'r', encoding='utf-8') as f:
                self.analysis = json.load(f)
        else:
            self.analysis = {
                "trends": [],
                "patterns": [],
                "insights": [],
                "last_analysis": None
            }

        # 加载创新机会
        if self.opportunities_file.exists():
            with open(self.opportunities_file, 'r', encoding='utf-8') as f:
                self.opportunities = json.load(f)
        else:
            self.opportunities = {
                "discovered": [],
                "validated": [],
                "implemented": [],
                "last_discovery": None
            }

    def save_state(self):
        """保存引擎状态"""
        # 保存知识图谱
        self.knowledge_graph["last_updated"] = datetime.now().isoformat()
        with open(self.knowledge_graph_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_graph, f, ensure_ascii=False, indent=2)

        # 保存分析结果
        with open(self.analysis_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis, f, ensure_ascii=False, indent=2)

        # 保存创新机会
        with open(self.opportunities_file, 'w', encoding='utf-8') as f:
            json.dump(self.opportunities, f, ensure_ascii=False, indent=2)

    def collect_evolution_knowledge(self) -> Dict[str, Any]:
        """
        跨轮次收集进化知识

        Returns:
            收集结果
        """
        print(f"[{self.engine_name}] 开始收集跨轮次进化知识...")

        collected_count = 0
        new_nodes = {}

        # 1. 从 evolution_completed_*.json 收集进化历史
        state_files = list(STATE_DIR.glob("evolution_completed_*.json"))
        print(f"[{self.engine_name}] 发现 {len(state_files)} 个进化完成记录")

        for file in state_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 提取关键信息
                round_num = data.get("loop_round", 0)
                goal = data.get("current_goal", "")
                status = data.get("status", "unknown")
                timestamp = data.get("completed_at", "")

                if round_num and goal:
                    node_id = f"round_{round_num}"
                    if node_id not in self.knowledge_graph["nodes"]:
                        new_nodes[node_id] = {
                            "id": node_id,
                            "round": round_num,
                            "goal": goal,
                            "status": status,
                            "timestamp": timestamp,
                            "type": "evolution_round",
                            "tags": self._extract_tags(goal),
                            "capabilities_added": data.get("capabilities_added", []),
                            "metrics": data.get("metrics", {})
                        }
                        collected_count += 1
            except Exception as e:
                print(f"[{self.engine_name}] 读取 {file} 失败: {e}")

        # 2. 从 evolution_auto_last.md 获取最新摘要
        auto_last_file = REFERENCES_DIR / "evolution_auto_last.md"
        if auto_last_file.exists():
            try:
                content = auto_last_file.read_text(encoding='utf-8')
                # 提取最新轮次信息
                match = re.search(r'round\s*(\d+)', content)
                if match:
                    latest_round = int(match.group(1))
                    print(f"[{self.engine_name}] 最新进化轮次: {latest_round}")
            except Exception as e:
                print(f"[{self.engine_name}] 读取 evolution_auto_last.md 失败: {e}")

        # 3. 从 failures.md 收集失败教训
        failures_file = REFERENCES_DIR / "failures.md"
        if failures_file.exists():
            try:
                content = failures_file.read_text(encoding='utf-8')
                # 提取失败模式
                failure_nodes = self._extract_failure_patterns(content)
                for node_id, node_data in failure_nodes.items():
                    if node_id not in self.knowledge_graph["nodes"]:
                        new_nodes[node_id] = node_data
                        collected_count += 1
            except Exception as e:
                print(f"[{self.engine_name}] 读取 failures.md 失败: {e}")

        # 添加新节点
        self.knowledge_graph["nodes"].update(new_nodes)

        print(f"[{self.engine_name}] 收集完成，新增 {collected_count} 个知识节点")

        return {
            "success": True,
            "collected": collected_count,
            "total_nodes": len(self.knowledge_graph["nodes"])
        }

    def _extract_tags(self, goal: str) -> List[str]:
        """从目标中提取关键词标签"""
        # 常见关键词
        keywords = [
            "智能", "全场景", "进化环", "引擎", "决策", "执行",
            "知识", "推理", "预测", "优化", "集成", "协同",
            "自适应", "自主", "创新", "意识", "服务"
        ]

        tags = []
        for kw in keywords:
            if kw in goal:
                tags.append(kw)

        # 如果没有匹配，添加默认标签
        if not tags:
            tags = ["进化"]

        return tags[:5]  # 最多5个标签

    def _extract_failure_patterns(self, content: str) -> Dict[str, Any]:
        """从失败记录中提取模式"""
        nodes = {}

        # 匹配日期和失败描述
        pattern = r'- (\d{4}-\d{2}-\d{2})：(.*?)(?:→|$)'
        matches = re.findall(pattern, content)

        for date, description in matches:
            node_id = f"failure_{date.replace('-', '')}"
            if node_id not in nodes:
                nodes[node_id] = {
                    "id": node_id,
                    "type": "failure_lesson",
                    "date": date,
                    "description": description.strip(),
                    "tags": self._extract_tags(description),
                    "extracted_at": datetime.now().isoformat()
                }

        return nodes

    def build_knowledge_graph(self) -> Dict[str, Any]:
        """
        构建进化知识网络图谱

        Returns:
            构建结果
        """
        print(f"[{self.engine_name}] 开始构建知识网络图谱...")

        nodes = self.knowledge_graph["nodes"]
        edges = []

        # 基于标签和类型建立关联
        node_list = list(nodes.values())

        # 1. 基于标签的关联
        tag_groups = defaultdict(list)
        for node in node_list:
            for tag in node.get("tags", []):
                tag_groups[tag].append(node["id"])

        # 为同标签节点建立边
        for tag, node_ids in tag_groups.items():
            if len(node_ids) > 1:
                for i in range(len(node_ids) - 1):
                    edges.append({
                        "source": node_ids[i],
                        "target": node_ids[i + 1],
                        "type": "same_tag",
                        "tag": tag,
                        "weight": 0.8
                    })

        # 2. 基于进化顺序的关联（相邻轮次）
        round_nodes = [n for n in node_list if n.get("type") == "evolution_round"]
        round_nodes.sort(key=lambda x: x.get("round", 0))

        for i in range(len(round_nodes) - 1):
            edges.append({
                "source": round_nodes[i]["id"],
                "target": round_nodes[i + 1]["id"],
                "type": "sequential",
                "weight": 1.0
            })

        # 3. 基于"集成"关键字的关联
        integration_keywords = ["集成", "深度集成", "融合", "协同"]
        for i, node_a in enumerate(node_list):
            for node_b in node_list[i+1:]:
                tags_a = set(node_a.get("tags", []))
                tags_b = set(node_b.get("tags", []))

                common_tags = tags_a & tags_b
                if common_tags:
                    # 计算相似度
                    similarity = len(common_tags) / max(len(tags_a | tags_b), 1)
                    if similarity > 0.3:
                        edges.append({
                            "source": node_a["id"],
                            "target": node_b["id"],
                            "type": "similar",
                            "common_tags": list(common_tags),
                            "weight": similarity
                        })

        self.knowledge_graph["edges"] = edges

        print(f"[{self.engine_name}] 知识网络图谱构建完成：{len(nodes)} 个节点，{len(edges)} 条边")

        return {
            "success": True,
            "nodes": len(nodes),
            "edges": len(edges)
        }

    def analyze_trends_and_patterns(self) -> Dict[str, Any]:
        """
        分析进化趋势和模式

        Returns:
            分析结果
        """
        print(f"[{self.engine_name}] 开始分析进化趋势和模式...")

        trends = []
        patterns = []
        insights = []

        nodes = list(self.knowledge_graph["nodes"].values())
        rounds = [n for n in nodes if n.get("type") == "evolution_round"]
        rounds.sort(key=lambda x: x.get("round", 0))

        # 1. 分析进化方向趋势
        if rounds:
            # 统计标签频率
            tag_counts = defaultdict(int)
            for r in rounds:
                for tag in r.get("tags", []):
                    tag_counts[tag] += 1

            # 最常见的进化方向
            top_tags = sorted(tag_counts.items(), key=lambda x: -x[1])[:10]
            trends.append({
                "type": "top_evolution_directions",
                "data": [{"tag": t, "count": c} for t, c in top_tags],
                "analyzed_at": datetime.now().isoformat()
            })

        # 2. 分析连续性模式
        if len(rounds) >= 3:
            # 检查是否有持续的进化方向
            recent_rounds = rounds[-10:]  # 最近10轮
            recent_tags = set()
            for r in recent_rounds:
                recent_tags.update(r.get("tags", []))

            # 检查是否有新的进化方向
            all_tags = set()
            for r in rounds:
                all_tags.update(r.get("tags", []))

            new_tags = recent_tags - all_tags

            if new_tags:
                patterns.append({
                    "type": "emerging_directions",
                    "tags": list(new_tags),
                    "analyzed_at": datetime.now().isoformat()
                })

        # 3. 生成洞察
        if rounds:
            # 整体进化效率
            completed = sum(1 for r in rounds if r.get("status") == "completed")
            total = len(rounds)
            success_rate = completed / total if total > 0 else 0

            insights.append({
                "type": "evolution_success_rate",
                "value": f"{success_rate*100:.1f}%",
                "completed": completed,
                "total": total,
                "analyzed_at": datetime.now().isoformat()
            })

            # 进化速度（轮/天）- 简化计算
            if rounds:
                first_round = rounds[0].get("round", 1)
                last_round = rounds[-1].get("round", first_round)
                rounds_span = last_round - first_round + 1
                insights.append({
                    "type": "evolution_velocity",
                    "value": f"{rounds_span} 轮",
                    "analyzed_at": datetime.now().isoformat()
                })

        self.analysis = {
            "trends": trends,
            "patterns": patterns,
            "insights": insights,
            "last_analysis": datetime.now().isoformat()
        }

        print(f"[{self.engine_name}] 分析完成：{len(trends)} 个趋势，{len(patterns)} 个模式，{len(insights)} 个洞察")

        return {
            "success": True,
            "trends_count": len(trends),
            "patterns_count": len(patterns),
            "insights_count": len(insights)
        }

    def discover_innovation_opportunities(self) -> Dict[str, Any]:
        """
        发现创新机会

        Returns:
            发现结果
        """
        print(f"[{self.engine_name}] 开始发现创新机会...")

        opportunities = []

        nodes = list(self.knowledge_graph["nodes"].values())
        edges = self.knowledge_graph.get("edges", [])

        # 1. 识别能力组合创新机会
        # 查找具有不同能力但可能有协同效应的节点组合
        capability_tags = set()
        for node in nodes:
            tags = node.get("tags", [])
            for tag in ["决策", "执行", "推理", "预测", "优化", "创新", "集成"]:
                if tag in tags:
                    capability_tags.add(tag)

        # 检查是否有未组合的能力
        required_combinations = [
            ("决策", "推理"),
            ("决策", "优化"),
            ("推理", "创新"),
            ("优化", "执行"),
            ("集成", "协同")
        ]

        node_tag_map = {}
        for node in nodes:
            node_id = node["id"]
            node_tag_map[node_id] = set(node.get("tags", []))

        for source_tag, target_tag in required_combinations:
            # 检查是否有节点同时具备这两个能力
            found = False
            for node_id, tags in node_tag_map.items():
                if source_tag in tags and target_tag in tags:
                    found = True
                    break

            if not found:
                opportunities.append({
                    "type": "capability_combination",
                    "description": f"探索{source_tag}与{target_tag}的深度集成",
                    "potential_benefit": "高",
                    "suggested_action": f"创建结合{source_tag}和{target_tag}的新引擎"
                })

        # 2. 识别进化方向空白
        # 统计现有进化方向
        direction_counts = defaultdict(int)
        for node in nodes:
            for tag in node.get("tags", []):
                direction_counts[tag] += 1

        # 找出较少涉及的进化方向
        rare_directions = ["意识", "情感", "创意", "元认知", "跨维度"]
        for direction in rare_directions:
            if direction_counts.get(direction, 0) < 5:
                opportunities.append({
                    "type": "underexplored_direction",
                    "description": f"深化{direction}相关能力",
                    "potential_benefit": "中",
                    "suggested_action": f"增强{direction}维度的进化"
                })

        # 3. 识别集成优化机会
        integration_nodes = [n for n in nodes if "集成" in n.get("tags", []) or "融合" in n.get("tags", [])]
        if len(integration_nodes) > 10:
            opportunities.append({
                "type": "integration_optimization",
                "description": "已有大量集成引擎，优化协调机制",
                "potential_benefit": "高",
                "suggested_action": "增强跨引擎协同调度和状态同步"
            })

        # 保存发现的机会
        self.opportunities = {
            "discovered": opportunities,
            "validated": self.opportunities.get("validated", []),
            "implemented": self.opportunities.get("implemented", []),
            "last_discovery": datetime.now().isoformat()
        }

        print(f"[{self.engine_name}] 发现 {len(opportunities)} 个创新机会")

        return {
            "success": True,
            "opportunities_found": len(opportunities),
            "opportunities": opportunities
        }

    def integrate_with_decision_engine(self, query: str) -> Dict[str, Any]:
        """
        与决策引擎集成，提供知识驱动的决策支持

        Args:
            query: 决策查询

        Returns:
            决策支持结果
        """
        print(f"[{self.engine_name}] 处理决策查询: {query}")

        # 基于知识图谱提供决策建议
        suggestions = []

        # 1. 查找相关历史
        query_lower = query.lower()
        related_nodes = []

        for node in self.knowledge_graph["nodes"].values():
            node_goal = node.get("goal", "").lower()
            if any(kw in node_goal for kw in query_lower.split()):
                related_nodes.append(node)

        # 2. 基于分析结果提供建议
        for insight in self.analysis.get("insights", []):
            if insight.get("type") == "evolution_success_rate":
                suggestions.append({
                    "type": "efficiency",
                    "message": f"当前进化成功率 {insight['value']}，建议关注成功率提升"
                })

        # 3. 基于创新机会提供建议
        if self.opportunities.get("discovered"):
            top_opportunity = self.opportunities["discovered"][0]
            suggestions.append({
                "type": "innovation",
                "message": f"建议探索: {top_opportunity['description']}"
            })

        return {
            "success": True,
            "query": query,
            "related_rounds": len(related_nodes),
            "suggestions": suggestions,
            "knowledge_nodes": [n["id"] for n in related_nodes[:5]]
        }

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "engine": self.engine_name,
            "version": self.version,
            "knowledge_graph": {
                "nodes": len(self.knowledge_graph.get("nodes", {})),
                "edges": len(self.knowledge_graph.get("edges", [])),
                "last_updated": self.knowledge_graph.get("last_updated")
            },
            "analysis": {
                "trends": len(self.analysis.get("trends", [])),
                "patterns": len(self.analysis.get("patterns", [])),
                "insights": len(self.analysis.get("insights", [])),
                "last_analysis": self.analysis.get("last_analysis")
            },
            "opportunities": {
                "discovered": len(self.opportunities.get("discovered", [])),
                "validated": len(self.opportunities.get("validated", [])),
                "implemented": len(self.opportunities.get("implemented", [])),
                "last_discovery": self.opportunities.get("last_discovery")
            }
        }

    def run_full_cycle(self) -> Dict[str, Any]:
        """
        运行完整知识整合周期

        Returns:
            周期执行结果
        """
        print(f"\n{'='*50}")
        print(f"开始执行知识深度整合引擎完整周期")
        print(f"{'='*50}\n")

        # 1. 收集知识
        result1 = self.collect_evolution_knowledge()
        print(f"收集知识: {result1}\n")

        # 2. 构建图谱
        result2 = self.build_knowledge_graph()
        print(f"构建图谱: {result2}\n")

        # 3. 分析趋势
        result3 = self.analyze_trends_and_patterns()
        print(f"分析趋势: {result3}\n")

        # 4. 发现机会
        result4 = self.discover_innovation_opportunities()
        print(f"发现机会: {result4}\n")

        # 5. 保存状态
        self.save_state()

        # 6. 测试与决策引擎集成
        integration_result = self.integrate_with_decision_engine("进化优化")
        print(f"决策集成测试: {integration_result}\n")

        print(f"{'='*50}")
        print(f"知识深度整合引擎周期执行完成")
        print(f"{'='*50}\n")

        return {
            "success": True,
            "collected": result1.get("collected"),
            "graph_nodes": result2.get("nodes"),
            "graph_edges": result2.get("edges"),
            "trends": result3.get("trends_count"),
            "patterns": result3.get("patterns_count"),
            "insights": result3.get("insights_count"),
            "opportunities": result4.get("opportunities_found")
        }


def main():
    """主入口"""
    import sys

    engine = EvolutionKnowledgeDeepIntegrationEngine()

    if len(sys.argv) < 2:
        print(f"跨轮次知识深度整合与智能推理引擎 v{engine.version}")
        print("\n用法:")
        print("  python evolution_knowledge_deep_integration_engine.py status         - 查看引擎状态")
        print("  python evolution_knowledge_deep_integration_engine.py collect       - 收集进化知识")
        print("  python evolution_knowledge_deep_integration_engine.py build        - 构建知识图谱")
        print("  python evolution_knowledge_deep_integration_engine.py analyze      - 分析趋势模式")
        print("  python evolution_knowledge_deep_integration_engine.py discover    - 发现创新机会")
        print("  python evolution_knowledge_deep_integration_engine.py integrate   - 测试决策集成")
        print("  python evolution_knowledge_deep_integration_engine.py cycle       - 运行完整周期")
        return

    command = sys.argv[1]

    if command == "status":
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif command == "collect":
        result = engine.collect_evolution_knowledge()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        engine.save_state()

    elif command == "build":
        result = engine.build_knowledge_graph()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        engine.save_state()

    elif command == "analyze":
        result = engine.analyze_trends_and_patterns()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        engine.save_state()

    elif command == "discover":
        result = engine.discover_innovation_opportunities()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        engine.save_state()

    elif command == "integrate":
        query = sys.argv[2] if len(sys.argv) > 2 else "进化优化"
        result = engine.integrate_with_decision_engine(query)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "cycle":
        result = engine.run_full_cycle()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "test":
        print("=== 测试知识深度整合引擎 ===")
        result = engine.run_full_cycle()
        print(f"\n测试结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        print("\n=== 测试完成 ===")


if __name__ == "__main__":
    main()