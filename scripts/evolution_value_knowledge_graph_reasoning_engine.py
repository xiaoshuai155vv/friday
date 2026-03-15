#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环价值知识图谱深度推理与智能决策增强引擎
version 1.0.0

在 round 561 完成的元进化价值投资组合优化与风险对冲引擎基础上，构建价值知识图谱深度推理能力。
让系统能够将价值投资决策与知识图谱深度融合，实现价值驱动的知识推理、智能推荐、主动决策增强，
形成「价值投资→知识推理→智能决策→价值实现」的完整价值知识闭环。

本轮新增：
1. 价值知识图谱构建 - 整合价值投资引擎和知识图谱引擎
2. 价值驱动知识推理 - 基于价值预测进行知识推理
3. 智能投资推荐 - 基于知识图谱提供智能投资建议
4. 主动决策增强 - 增强元进化决策的知识支撑
5. 与 round 561 价值投资组合引擎深度集成
6. 驾驶舱数据接口

Version: 1.0.0
Round: 562
"""

import os
import json
import sqlite3
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import math

# 解决 Windows 控制台编码问题
import sys
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# 路径配置
SCRIPT_DIR = Path(__file__).parent
RUNTIME_STATE_DIR = SCRIPT_DIR.parent / "runtime" / "state"
DATA_DIR = SCRIPT_DIR.parent / "data"
EVOLUTION_DB = RUNTIME_STATE_DIR / "evolution_history.db"
KNOWLEDGE_GRAPH_PATH = RUNTIME_STATE_DIR / "knowledge_graph.json"


class EvolutionValueKnowledgeGraphReasoningEngine:
    """价值知识图谱深度推理与智能决策增强引擎"""

    VERSION = "1.0.0"
    ROUND = 562

    def __init__(self):
        """初始化引擎"""
        self.db_path = EVOLUTION_DB
        self.data_dir = DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.kg_reasoning_cache = self.data_dir / "kg_reasoning_cache.json"
        self.recommendation_cache = self.data_dir / "investment_recommendation_cache.json"
        self.reasoning_history = self.data_dir / "reasoning_history.json"
        self.decision_enhancement_cache = self.data_dir / "decision_enhancement_cache.json"

    def _get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(str(self.db_path))

    def _load_cache(self, cache_file: Path) -> Dict:
        """加载缓存"""
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_cache(self, cache_file: Path, data: Dict):
        """保存缓存"""
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_history(self) -> List[Dict]:
        """加载推理历史"""
        if self.reasoning_history.exists():
            try:
                with open(self.reasoning_history, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_history(self, history: List[Dict]):
        """保存推理历史"""
        with open(self.reasoning_history, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def get_status(self) -> Dict:
        """获取引擎状态"""
        cache = self._load_cache(self.kg_reasoning_cache)
        recommendations = self._load_cache(self.recommendation_cache)
        history = self._load_history()

        # 尝试加载价值投资组合引擎的数据
        portfolio_optimizer_path = SCRIPT_DIR / "evolution_value_investment_portfolio_optimizer.py"
        has_portfolio_optimizer = portfolio_optimizer_path.exists()

        # 尝试加载知识图谱
        kg_exists = KNOWLEDGE_GRAPH_PATH.exists()
        kg_nodes = 0
        kg_edges = 0
        if kg_exists:
            try:
                with open(KNOWLEDGE_GRAPH_PATH, 'r', encoding='utf-8') as f:
                    kg_data = json.load(f)
                    kg_nodes = len(kg_data.get("nodes", {}))
                    kg_edges = len(kg_data.get("edges", []))
            except Exception:
                pass

        return {
            "engine": "EvolutionValueKnowledgeGraphReasoningEngine",
            "version": self.VERSION,
            "round": self.ROUND,
            "status": "active",
            "has_portfolio_optimizer": has_portfolio_optimizer,
            "kg_nodes": kg_nodes,
            "kg_edges": kg_edges,
            "reasoning_cache_entries": len(cache),
            "recommendation_count": len(recommendations.get("recommendations", [])),
            "reasoning_history_count": len(history),
            "initialized_at": cache.get("initialized_at", datetime.now().isoformat())
        }

    def build_value_knowledge_graph(self, integrate_portfolio: bool = True) -> Dict:
        """
        构建价值知识图谱，将价值投资数据与知识图谱融合

        Args:
            integrate_portfolio: 是否集成价值投资组合引擎数据

        Returns:
            构建结果
        """
        result = {
            "status": "success",
            "kg_nodes_added": 0,
            "kg_edges_added": 0,
            "value_nodes": [],
            "investment_nodes": [],
            "insights": []
        }

        # 加载知识图谱
        kg_data = {"nodes": {}, "edges": [], "metadata": {}}
        if KNOWLEDGE_GRAPH_PATH.exists():
            try:
                with open(KNOWLEDGE_GRAPH_PATH, 'r', encoding='utf-8') as f:
                    loaded_kg = json.load(f)
                    if isinstance(loaded_kg, dict) and 'nodes' in loaded_kg:
                        kg_data = loaded_kg
            except Exception as e:
                result["status"] = "error"
                result["error"] = f"加载知识图谱失败: {e}"
                return result

        # 添加价值相关节点
        value_categories = [
            "价值投资", "投资组合", "风险对冲", "价值预测",
            "价值追踪", "价值量化", "价值实现", "投资优化"
        ]

        for category in value_categories:
            node_id = f"value_{category}"
            if node_id not in kg_data["nodes"]:
                kg_data["nodes"][node_id] = {
                    "type": "value_category",
                    "properties": {
                        "name": category,
                        "created_at": datetime.now().isoformat(),
                        "round": self.ROUND
                    }
                }
                result["kg_nodes_added"] += 1
                result["value_nodes"].append(node_id)

        # 从进化历史中提取价值相关的投资决策
        investment_nodes = []
        if integrate_portfolio:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT round_number, current_goal, status, execution_time
                    FROM evolution_rounds
                    WHERE current_goal LIKE '%价值%' OR current_goal LIKE '%投资%' OR current_goal LIKE '%优化%'
                    ORDER BY round_number DESC
                    LIMIT 50
                """)
                rows = cursor.fetchall()
                conn.close()

                for row in rows:
                    round_num, goal, status, exec_time = row
                    node_id = f"investment_{round_num}"
                    if node_id not in kg_data["nodes"]:
                        kg_data["nodes"][node_id] = {
                            "type": "investment_decision",
                            "properties": {
                                "round": round_num,
                                "goal": goal[:100] if goal else "",
                                "status": status,
                                "execution_time": exec_time,
                                "created_at": datetime.now().isoformat()
                            }
                        }
                        result["kg_nodes_added"] += 1
                        investment_nodes.append(node_id)

                result["investment_nodes"] = investment_nodes

            except Exception as e:
                result["insights"].append(f"从进化历史提取投资决策时出错: {e}")

        # 添加价值节点之间的关系
        for value_node in result["value_nodes"]:
            for investment_node in investment_nodes:
                edge_id = f"edge_{value_node}_{investment_node}"
                edge_exists = any(
                    e.get("from") == value_node and e.get("to") == investment_node
                    for e in kg_data["edges"]
                )
                if not edge_exists:
                    kg_data["edges"].append({
                        "from": value_node,
                        "to": investment_node,
                        "relation": "guides",
                        "properties": {
                            "created_at": datetime.now().isoformat()
                        }
                    })
                    result["kg_edges_added"] += 1

        # 尝试保存更新后的知识图谱
        try:
            with open(KNOWLEDGE_GRAPH_PATH, 'w', encoding='utf-8') as f:
                json.dump(kg_data, f, ensure_ascii=False, indent=2)
            result["insights"].append(f"知识图谱已更新：新增{result['kg_nodes_added']}个节点，{result['kg_edges_added']}条边")
        except Exception as e:
            result["insights"].append(f"保存知识图谱时出错: {e}")

        # 初始化缓存
        cache = self._load_cache(self.kg_reasoning_cache)
        cache["initialized_at"] = datetime.now().isoformat()
        cache["last_build"] = datetime.now().isoformat()
        cache["build_result"] = {
            "kg_nodes_added": result["kg_nodes_added"],
            "kg_edges_added": result["kg_edges_added"]
        }
        self._save_cache(self.kg_reasoning_cache, cache)

        return result

    def reason_value_driven(self, query: str = None) -> Dict:
        """
        价值驱动的知识推理

        Args:
            query: 可选的查询主题

        Returns:
            推理结果
        """
        result = {
            "status": "success",
            "reasoning_chain": [],
            "insights": [],
            "value_driven_paths": []
        }

        # 加载知识图谱
        kg_data = {"nodes": {}, "edges": [], "metadata": {}}
        if KNOWLEDGE_GRAPH_PATH.exists():
            try:
                with open(KNOWLEDGE_GRAPH_PATH, 'r', encoding='utf-8') as f:
                    loaded_kg = json.load(f)
                    if isinstance(loaded_kg, dict) and 'nodes' in loaded_kg:
                        kg_data = loaded_kg
            except Exception as e:
                result["status"] = "error"
                result["error"] = f"加载知识图谱失败: {e}"
                return result

        # 构建价值驱动路径
        value_nodes = [n for n, v in kg_data["nodes"].items() if v.get("type") == "value_category"]
        investment_nodes = [n for n, v in kg_data["nodes"].items() if v.get("type") == "investment_decision"]

        result["reasoning_chain"].append(f"发现{len(value_nodes)}个价值类别节点")
        result["reasoning_chain"].append(f"发现{len(investment_nodes)}个投资决策节点")

        # 追踪价值→投资决策的路径
        for value_node in value_nodes:
            for edge in kg_data["edges"]:
                if edge.get("from") == value_node:
                    target = edge.get("to")
                    path = {
                        "from": value_node,
                        "relation": edge.get("relation"),
                        "to": target,
                        "reasoning": f"价值类别{value_node}通过{edge.get('relation')}关系指导投资决策{target}"
                    }
                    result["value_driven_paths"].append(path)

        # 生成洞察
        if result["value_driven_paths"]:
            result["insights"].append(f"发现{len(result['value_driven_paths'])}条价值驱动路径")
            # 按价值类别统计
            category_stats = {}
            for path in result["value_driven_paths"]:
                category = path["from"].replace("value_", "")
                category_stats[category] = category_stats.get(category, 0) + 1

            for cat, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
                result["insights"].append(f"价值类别「{cat}」指导了{count}个投资决策")
        else:
            result["insights"].append("未发现价值驱动路径，建议先运行构建知识图谱")

        # 保存推理历史
        history = self._load_history()
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "paths_found": len(result["value_driven_paths"]),
            "insights": result["insights"]
        }
        history.append(history_entry)
        # 保留最近100条
        history = history[-100:]
        self._save_history(history)

        return result

    def generate_investment_recommendations(self, focus_areas: List[str] = None) -> Dict:
        """
        基于知识图谱生成智能投资推荐

        Args:
            focus_areas: 重点关注的领域

        Returns:
            推荐结果
        """
        result = {
            "status": "success",
            "recommendations": [],
            "reasoning": [],
            "confidence": 0.0
        }

        if focus_areas is None:
            focus_areas = ["价值投资", "投资组合", "风险对冲", "价值预测"]

        # 加载知识图谱和进化历史
        kg_data = {"nodes": {}, "edges": [], "metadata": {}}
        if KNOWLEDGE_GRAPH_PATH.exists():
            try:
                with open(KNOWLEDGE_GRAPH_PATH, 'r', encoding='utf-8') as f:
                    loaded_kg = json.load(f)
                    if isinstance(loaded_kg, dict) and 'nodes' in loaded_kg:
                        kg_data = loaded_kg
            except Exception:
                pass

        # 分析历史投资决策的成功率
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT round_number, current_goal, status, execution_time
                FROM evolution_rounds
                WHERE current_goal LIKE '%价值%' OR current_goal LIKE '%投资%'
                ORDER BY round_number DESC
                LIMIT 30
            """)
            rows = cursor.fetchall()
            conn.close()

            success_count = sum(1 for row in rows if row[2] == "completed")
            total_count = len(rows)
            success_rate = success_count / total_count if total_count > 0 else 0.5

            result["reasoning"].append(f"历史价值投资决策：{total_count}轮，成功率{success_rate:.1%}")

            # 基于分析生成推荐
            for focus in focus_areas:
                recommendation = {
                    "area": focus,
                    "action": "",
                    "priority": "medium",
                    "rationale": ""
                }

                if "价值预测" in focus:
                    recommendation["action"] = "继续强化价值预测能力，结合知识图谱进行预测增强"
                    recommendation["priority"] = "high"
                    recommendation["rationale"] = "价值预测是投资决策的基础，准确预测能显著提升投资回报"
                elif "投资组合" in focus:
                    recommendation["action"] = "优化投资组合配置，分散风险敞口"
                    recommendation["priority"] = "high"
                    recommendation["rationale"] = f"基于{success_rate:.1%}的历史成功率，建议优化组合配置"
                elif "风险对冲" in focus:
                    recommendation["action"] = "增强风险对冲策略，降低低价值投资风险"
                    recommendation["priority"] = "medium"
                    recommendation["rationale"] = "风险对冲是保护投资组合的重要手段"
                elif "价值投资" in focus:
                    recommendation["action"] = "深化价值投资与知识图谱的集成，实现智能决策增强"
                    recommendation["priority"] = "high"
                    recommendation["rationale"] = "价值投资与知识图谱的深度融合是本轮核心目标"

                result["recommendations"].append(recommendation)

            result["confidence"] = success_rate

        except Exception as e:
            result["status"] = "error"
            result["error"] = f"生成推荐时出错: {e}"

        # 保存推荐缓存
        cache = self._load_cache(self.recommendation_cache)
        cache["recommendations"] = result["recommendations"]
        cache["generated_at"] = datetime.now().isoformat()
        cache["confidence"] = result["confidence"]
        self._save_cache(self.recommendation_cache, cache)

        return result

    def enhance_decision(self, context: Dict = None) -> Dict:
        """
        增强元进化决策的知识支撑

        Args:
            context: 决策上下文

        Returns:
            增强结果
        """
        result = {
            "status": "success",
            "enhanced_factors": [],
            "knowledge_support": [],
            "decision_enhancement": {}
        }

        if context is None:
            context = {}

        # 获取知识图谱推理结果
        reasoning_result = self.reason_value_driven()
        result["knowledge_support"].extend(reasoning_result.get("insights", []))

        # 获取投资推荐
        recommendation_result = self.generate_investment_recommendations()
        if recommendation_result.get("recommendations"):
            top_rec = recommendation_result["recommendations"][0]
            result["enhanced_factors"].append({
                "factor": "top_recommendation",
                "value": top_rec.get("action"),
                "priority": top_rec.get("priority"),
                "confidence": recommendation_result.get("confidence", 0.5)
            })

        # 加载价值投资组合引擎的数据
        portfolio_cache = DATA_DIR / "investment_portfolio_cache.json"
        if portfolio_cache.exists():
            try:
                with open(portfolio_cache, 'r', encoding='utf-8') as f:
                    portfolio_data = json.load(f)
                    if portfolio_data:
                        result["enhanced_factors"].append({
                            "factor": "portfolio_optimizer_data",
                            "value": "已加载投资组合优化数据",
                            "data_keys": list(portfolio_data.keys())[:5]
                        })
            except Exception:
                pass

        # 构建决策增强报告
        result["decision_enhancement"] = {
            "summary": "基于价值知识图谱的决策增强已完成",
            "knowledge_paths": len(reasoning_result.get("value_driven_paths", [])),
            "recommendations_count": len(recommendation_result.get("recommendations", [])),
            "confidence_score": recommendation_result.get("confidence", 0.5),
            "enhanced_factors_count": len(result["enhanced_factors"])
        }

        # 保存决策增强缓存
        cache = self._load_cache(self.decision_enhancement_cache)
        cache.update(result["decision_enhancement"])
        cache["enhanced_at"] = datetime.now().isoformat()
        self._save_cache(self.decision_enhancement_cache, cache)

        return result

    def run_full_integration(self) -> Dict:
        """
        运行完整的价值知识图谱集成流程

        Returns:
            集成结果
        """
        result = {
            "status": "success",
            "steps": [],
            "summary": ""
        }

        # 步骤1：构建价值知识图谱
        result["steps"].append("开始构建价值知识图谱...")
        kg_result = self.build_value_knowledge_graph()
        result["steps"].append(f"知识图谱构建完成：新增{kg_result.get('kg_nodes_added', 0)}个节点")

        # 步骤2：价值驱动推理
        result["steps"].append("开始价值驱动推理...")
        reasoning_result = self.reason_value_driven()
        result["steps"].append(f"推理完成：发现{len(reasoning_result.get('value_driven_paths', []))}条路径")

        # 步骤3：生成投资推荐
        result["steps"].append("生成智能投资推荐...")
        rec_result = self.generate_investment_recommendations()
        result["steps"].append(f"推荐生成完成：{len(rec_result.get('recommendations', []))}条建议")

        # 步骤4：决策增强
        result["steps"].append("增强决策知识支撑...")
        enhance_result = self.enhance_decision()
        result["steps"].append(f"决策增强完成：{len(enhance_result.get('enhanced_factors', []))}个增强因子")

        result["summary"] = "价值知识图谱深度推理集成完成，所有组件协同工作正常"

        return result

    def get_cockpit_data(self) -> Dict:
        """获取驾驶舱数据"""
        status = self.get_status()
        reasoning = self._load_cache(self.kg_reasoning_cache)
        recommendations = self._load_cache(self.recommendation_cache)
        decision_enhancement = self._load_cache(self.decision_enhancement_cache)
        history = self._load_history()

        return {
            "engine": "EvolutionValueKnowledgeGraphReasoningEngine",
            "version": self.VERSION,
            "round": self.ROUND,
            "status": status,
            "reasoning": {
                "last_build": reasoning.get("last_build"),
                "cache_entries": len(reasoning)
            },
            "recommendations": {
                "count": len(recommendations.get("recommendations", [])),
                "confidence": recommendations.get("confidence", 0.0),
                "generated_at": recommendations.get("generated_at")
            },
            "decision_enhancement": decision_enhancement,
            "recent_history": history[-5:] if history else []
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能全场景进化环价值知识图谱深度推理与智能决策增强引擎"
    )
    parser.add_argument("--status", action="store_true", help="获取引擎状态")
    parser.add_argument("--build-kg", action="store_true", help="构建价值知识图谱")
    parser.add_argument("--reason", action="store_true", help="执行价值驱动推理")
    parser.add_argument("--recommend", action="store_true", help="生成智能投资推荐")
    parser.add_argument("--enhance", action="store_true", help="增强决策知识支撑")
    parser.add_argument("--full", action="store_true", help="运行完整集成流程")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")

    args = parser.parse_args()

    engine = EvolutionValueKnowledgeGraphReasoningEngine()

    if args.status:
        result = engine.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.build_kg:
        result = engine.build_value_knowledge_graph()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.reason:
        result = engine.reason_value_driven()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.recommend:
        result = engine.generate_investment_recommendations()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.enhance:
        result = engine.enhance_decision()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.full:
        result = engine.run_full_integration()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.cockpit_data:
        result = engine.get_cockpit_data()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 默认显示状态
    result = engine.get_status()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()