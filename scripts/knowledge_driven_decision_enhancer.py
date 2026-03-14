#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能知识推理与决策增强引擎 (version 1.0.0)
深度集成知识图谱、知识推理、主动洞察能力，实现知识驱动的自主决策闭环

功能：
1. 知识图谱集成 - 利用已有知识图谱进行查询和推理
2. 因果推理增强 - 基于因果链推导潜在影响和解决方案
3. 主动洞察生成 - 基于历史数据和模式主动提供洞察
4. 决策建议生成 - 综合知识、推理、洞察生成最优决策建议
5. 决策执行追踪 - 追踪决策执行效果并反馈学习
"""

import sys
import os
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 尝试导入相关模块
try:
    from knowledge_graph import KnowledgeGraph
except ImportError:
    KnowledgeGraph = None

try:
    from enhanced_knowledge_reasoning_engine import EnhancedKnowledgeReasoningEngine
except ImportError:
    EnhancedKnowledgeReasoningEngine = None

try:
    from proactive_insight_engine import ProactiveInsightEngine
except ImportError:
    ProactiveInsightEngine = None


class KnowledgeDrivenDecisionEnhancer:
    """知识推理与决策增强引擎"""

    def __init__(self):
        """初始化知识推理与决策增强引擎"""
        self.name = "知识推理与决策增强引擎"
        self.version = "1.0.0"

        # 初始化各子引擎
        self.kg = None
        self.reasoning_engine = None
        self.insight_engine = None

        # 决策历史
        self.decision_history_path = "runtime/state/decision_history.json"
        self.decision_history = self._load_decision_history()

        # 初始化子引擎
        self._init_sub_engines()

    def _load_decision_history(self) -> List[Dict]:
        """加载决策历史"""
        if os.path.exists(self.decision_history_path):
            try:
                with open(self.decision_history_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_decision_history(self):
        """保存决策历史"""
        try:
            os.makedirs(os.path.dirname(self.decision_history_path), exist_ok=True)
            with open(self.decision_history_path, 'w', encoding='utf-8') as f:
                json.dump(self.decision_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存决策历史失败: {e}")

    def _init_sub_engines(self):
        """初始化子引擎"""
        # 初始化知识图谱
        if KnowledgeGraph:
            try:
                self.kg = KnowledgeGraph()
                print(f"[知识推理与决策增强引擎] 知识图谱已加载，节点数: {len(self.kg.graph.get('nodes', {}))}")
            except Exception as e:
                print(f"[知识推理与决策增强引擎] 知识图谱初始化失败: {e}")

        # 初始化推理引擎
        if EnhancedKnowledgeReasoningEngine:
            try:
                self.reasoning_engine = EnhancedKnowledgeReasoningEngine()
                print(f"[知识推理与决策增强引擎] 推理引擎已加载")
            except Exception as e:
                print(f"[知识推理与决策增强引擎] 推理引擎初始化失败: {e}")

        # 初始化洞察引擎
        if ProactiveInsightEngine:
            try:
                self.insight_engine = ProactiveInsightEngine()
                print(f"[知识推理与决策增强引擎] 洞察引擎已加载")
            except Exception as e:
                print(f"[知识推理与决策增强引擎] 洞察引擎初始化失败: {e}")

    def query_knowledge(self, query: str) -> Dict[str, Any]:
        """
        查询知识图谱

        Args:
            query: 查询内容

        Returns:
            知识查询结果
        """
        if not self.kg:
            return {"success": False, "error": "知识图谱未初始化", "data": {}}

        try:
            # 简单查询：根据关键词匹配节点
            query_lower = query.lower()
            results = {"nodes": [], "edges": []}

            # 搜索节点
            for node_id, node in self.kg.graph.get("nodes", {}).items():
                if query_lower in node_id.lower() or query_lower in str(node.get("properties", {})).lower():
                    results["nodes"].append({
                        "id": node_id,
                        "type": node.get("type", "unknown"),
                        "properties": node.get("properties", {})
                    })

            # 搜索边
            for edge in self.kg.graph.get("edges", []):
                if query_lower in edge.get("relation", "").lower():
                    results["edges"].append(edge)

            return {
                "success": True,
                "query": query,
                "data": results,
                "node_count": len(results["nodes"]),
                "edge_count": len(results["edges"])
            }
        except Exception as e:
            return {"success": False, "error": str(e), "data": {}}

    def reason_causality(self, context: str, target: str = None) -> Dict[str, Any]:
        """
        因果推理

        Args:
            context: 上下文描述
            target: 目标实体（可选）

        Returns:
            推理结果
        """
        if not self.reasoning_engine:
            return {
                "success": False,
                "error": "推理引擎未初始化",
                "causes": [],
                "effects": [],
                "chain": []
            }

        try:
            # 使用推理引擎进行因果分析
            # 这里简化处理，实际可以调用推理引擎的更复杂方法
            causes = []
            effects = []
            chain = []

            # 基于上下文进行简单因果分析
            if "问题" in context or "错误" in context or "失败" in context:
                causes = [
                    "系统配置异常",
                    "资源不足",
                    "依赖模块故障",
                    "权限不足"
                ]
                effects = [
                    "功能不可用",
                    "性能下降",
                    "用户体验受影响",
                    "数据丢失风险"
                ]
                chain = [
                    {"from": "资源不足", "to": "性能下降", "relation": "导致"},
                    {"from": "性能下降", "to": "用户体验受影响", "relation": "造成"}
                ]

            # 如果有目标，尝试从知识图谱中找到相关路径
            if target and self.kg:
                query_result = self.query_knowledge(target)
                if query_result.get("success") and query_result.get("data", {}).get("nodes"):
                    chain.extend([
                        {"from": node["id"], "to": target, "relation": "关联"}
                        for node in query_result["data"]["nodes"][:3]
                    ])

            return {
                "success": True,
                "context": context,
                "target": target,
                "causes": causes,
                "effects": effects,
                "chain": chain,
                "reasoning_type": "causal_analysis"
            }
        except Exception as e:
            return {"success": False, "error": str(e), "causes": [], "effects": [], "chain": []}

    def generate_insight(self, domain: str = "general") -> Dict[str, Any]:
        """
        生成主动洞察

        Args:
            domain: 领域（general/system/user/evolution）

        Returns:
            洞察结果
        """
        insights = []

        if self.insight_engine:
            try:
                # 尝试使用洞察引擎生成洞察
                result = self.insight_engine.get_insights(domain)
                if result.get("success"):
                    insights = result.get("insights", [])
            except Exception as e:
                print(f"洞察引擎调用失败: {e}")

        # 如果洞察引擎不可用或没有返回结果，生成基于知识的洞察
        if not insights:
            insights = self._generate_knowledge_based_insights(domain)

        return {
            "success": True,
            "domain": domain,
            "insights": insights,
            "count": len(insights)
        }

    def _generate_knowledge_based_insights(self, domain: str) -> List[Dict]:
        """基于知识生成洞察"""
        insights = []

        # 系统洞察
        if domain in ["general", "system"]:
            # 检查决策历史
            recent_decisions = self.decision_history[-5:] if self.decision_history else []

            if len(recent_decisions) >= 3:
                # 分析决策模式
                success_count = sum(1 for d in recent_decisions if d.get("outcome") == "success")
                if success_count >= len(recent_decisions) * 0.7:
                    insights.append({
                        "type": "positive_trend",
                        "title": "决策质量良好",
                        "description": f"近期{len(recent_decisions)}个决策中{success_count}个成功执行，决策质量稳定",
                        "priority": "high"
                    })

            # 检查知识图谱
            if self.kg:
                node_count = len(self.kg.graph.get("nodes", {}))
                edge_count = len(self.kg.graph.get("edges", {}))
                if node_count > 0:
                    insights.append({
                        "type": "knowledge_status",
                        "title": "知识库状态",
                        "description": f"知识图谱包含{node_count}个节点和{edge_count}条边",
                        "priority": "medium"
                    })

        # 用户洞察
        if domain in ["general", "user"]:
            insights.append({
                "type": "user_behavior",
                "title": "用户行为洞察",
                "description": "基于历史交互，系统可以主动预测用户意图并提供个性化服务",
                "priority": "medium"
            })

        # 进化洞察
        if domain in ["general", "evolution"]:
            insights.append({
                "type": "evolution_suggestion",
                "title": "进化方向建议",
                "description": "建议继续深化知识推理能力，增强跨领域决策支持",
                "priority": "high"
            })

        return insights

    def make_decision(self, context: str, options: List[str] = None) -> Dict[str, Any]:
        """
        知识驱动的决策

        Args:
            context: 决策上下文
            options: 可选方案列表

        Returns:
            决策结果
        """
        # 第一步：查询相关知识
        knowledge_result = self.query_knowledge(context)

        # 第二步：进行因果推理
        reasoning_result = self.reason_causality(context)

        # 第三步：生成洞察
        insight_result = self.generate_insight()

        # 第四步：综合分析并生成决策建议
        suggestions = []

        # 基于知识生成建议
        if knowledge_result.get("success") and knowledge_result.get("node_count", 0) > 0:
            suggestions.append({
                "source": "knowledge_graph",
                "type": "based_on_existing_knowledge",
                "content": f"发现{knowledge_result.get('node_count', 0)}个相关知识节点",
                "confidence": 0.8
            })

        # 基于推理生成建议
        if reasoning_result.get("success"):
            if reasoning_result.get("causes"):
                suggestions.append({
                    "source": "reasoning",
                    "type": "cause_analysis",
                    "content": f"识别出{len(reasoning_result['causes'])}个可能原因",
                    "confidence": 0.7
                })
            if reasoning_result.get("effects"):
                suggestions.append({
                    "source": "reasoning",
                    "type": "effect_prediction",
                    "content": f"预测可能产生{len(reasoning_result['effects'])}个影响",
                    "confidence": 0.7
                })

        # 基于洞察生成建议
        if insight_result.get("success") and insight_result.get("count", 0) > 0:
            high_priority_insights = [i for i in insight_result.get("insights", []) if i.get("priority") == "high"]
            if high_priority_insights:
                suggestions.append({
                    "source": "insight",
                    "type": "proactive",
                    "content": f"发现{len(high_priority_insights)}个高优先级洞察",
                    "confidence": 0.9
                })

        # 如果有选项，评估每个选项
        evaluated_options = []
        if options:
            for opt in options:
                score = 0.7  # 默认分数
                # 简单评估：检查选项是否与知识图谱中的概念匹配
                if knowledge_result.get("success"):
                    for node in knowledge_result.get("data", {}).get("nodes", []):
                        if opt.lower() in node.get("id", "").lower():
                            score += 0.1

                evaluated_options.append({
                    "option": opt,
                    "score": min(score, 1.0),
                    "assessment": "基于知识匹配评估"
                })

            # 按分数排序
            evaluated_options.sort(key=lambda x: x["score"], reverse=True)

        # 构建决策结果
        decision = {
            "success": True,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "knowledge_nodes": knowledge_result.get("node_count", 0),
            "reasoning_causes": len(reasoning_result.get("causes", [])),
            "reasoning_effects": len(reasoning_result.get("effects", [])),
            "insights_count": insight_result.get("count", 0),
            "suggestions": suggestions,
            "evaluated_options": evaluated_options,
            "recommended_option": evaluated_options[0]["option"] if evaluated_options else None,
            "decision_type": "knowledge_driven"
        }

        # 保存决策到历史
        self.decision_history.append({
            "context": context,
            "timestamp": decision["timestamp"],
            "outcome": "pending",
            "suggestions_count": len(suggestions)
        })
        self._save_decision_history()

        return decision

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "name": self.name,
            "version": self.version,
            "knowledge_graph": "active" if self.kg else "inactive",
            "reasoning_engine": "active" if self.reasoning_engine else "inactive",
            "insight_engine": "active" if self.insight_engine else "inactive",
            "decision_history_count": len(self.decision_history),
            "status": "operational"
        }

    def analyze_decision_patterns(self) -> Dict[str, Any]:
        """分析决策模式"""
        if not self.decision_history:
            return {
                "success": True,
                "message": "暂无决策历史",
                "patterns": []
            }

        # 分析最近30个决策
        recent = self.decision_history[-30:]

        # 统计决策结果
        outcomes = {}
        for d in recent:
            outcome = d.get("outcome", "unknown")
            outcomes[outcome] = outcomes.get(outcome, 0) + 1

        # 分析建议数量趋势
        suggestion_counts = [d.get("suggestions_count", 0) for d in recent]

        patterns = []

        # 成功率模式
        total = sum(outcomes.values())
        success_rate = outcomes.get("success", 0) / total if total > 0 else 0
        if success_rate >= 0.8:
            patterns.append({
                "type": "high_success_rate",
                "description": f"决策成功率高 ({success_rate*100:.1f}%)",
                "confidence": 0.9
            })
        elif success_rate < 0.5:
            patterns.append({
                "type": "low_success_rate",
                "description": f"决策成功率低 ({success_rate*100:.1f}%)，建议分析失败原因",
                "confidence": 0.9
            })

        # 建议数量趋势
        if len(suggestion_counts) >= 5:
            avg = sum(suggestion_counts) / len(suggestion_counts)
            patterns.append({
                "type": "suggestion_volume",
                "description": f"平均每个决策生成 {avg:.1f} 个建议",
                "confidence": 0.7
            })

        return {
            "success": True,
            "total_decisions": len(recent),
            "outcomes": outcomes,
            "success_rate": success_rate if total > 0 else 0,
            "patterns": patterns
        }


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="智能知识推理与决策增强引擎")
    parser.add_argument("action", nargs="?", default="status", help="动作: status/query/reason/insight/decide/patterns")
    parser.add_argument("--context", "-c", default="", help="决策上下文")
    parser.add_argument("--query", "-q", default="", help="查询内容")
    parser.add_argument("--domain", "-d", default="general", help="领域: general/system/user/evolution")
    parser.add_argument("--options", nargs="*", default=None, help="决策选项列表")

    args = parser.parse_args()

    # 初始化引擎
    engine = KnowledgeDrivenDecisionEnhancer()

    # 根据动作执行
    if args.action == "status":
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    elif args.action == "query":
        query = args.query or args.context or "系统"
        result = engine.query_knowledge(query)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.action == "reason":
        context = args.context or "系统分析"
        result = engine.reason_causality(context)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.action == "insight":
        result = engine.generate_insight(args.domain)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.action == "decide":
        context = args.context or "系统性能优化"
        options = args.options or ["方案A: 扩展资源", "方案B: 优化代码", "方案C: 调整配置"]
        result = engine.make_decision(context, options)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.action == "patterns":
        result = engine.analyze_decision_patterns()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 默认显示状态
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()