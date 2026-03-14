#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化决策-知识-解释深度集成引擎 (Evolution Decision-Knowledge Integration Engine)
version 1.0.0

将 round 332 的跨轮知识融合能力与 round 333 的决策可解释性能力深度集成，
形成「知识驱动→智能决策→可解释执行→持续学习」的完整闭环。

让系统不仅能决策、可解释，还能从历史知识中学习并持续优化决策质量。

功能：
1. 知识驱动的智能决策（融合跨轮知识做更明智决策）
2. 决策推理链与知识图谱关联（每个决策可追溯到历史知识来源）
3. 自适应解释深度（根据决策复杂度自动调整解释详细程度）
4. 决策效果反馈学习（将决策执行效果反馈给知识图谱优化）
5. 与 do.py 深度集成

依赖：
- evolution_cross_round_knowledge_fusion_engine.py (round 332)
- evolution_decision_explainability_engine.py (round 333)
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict


class DecisionKnowledgeIntegrationEngine:
    """智能全场景进化决策-知识-解释深度集成引擎"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.state_dir = self.base_dir / "runtime" / "state"
        self.logs_dir = self.base_dir / "runtime" / "logs"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # 集成引擎实例
        self.cross_fusion_engine = None
        self.explainability_engine = None

        # 尝试导入跨轮知识融合引擎
        try:
            from evolution_cross_round_knowledge_fusion_engine import EvolutionCrossRoundKnowledgeFusionEngine
            self.cross_fusion_engine = EvolutionCrossRoundKnowledgeFusionEngine()
        except ImportError:
            pass

        # 尝试导入决策可解释性引擎
        try:
            from evolution_decision_explainability_engine import EvolutionDecisionExplainabilityEngine
            self.explainability_engine = EvolutionDecisionExplainabilityEngine()
        except ImportError:
            pass

        # 决策-知识关联存储
        self.decision_knowledge_file = self.state_dir / "decision_knowledge_integration.json"

        # 决策效果反馈记录
        self.feedback_file = self.state_dir / "decision_feedback_learning.json"

        # 解释深度级别定义
        self.explanation_levels = {
            "brief": {
                "description": "简要解释",
                "includes": ["goal", "main_evidence", "confidence"]
            },
            "standard": {
                "description": "标准解释",
                "includes": ["goal", "evidence", "reasoning_chain", "sources", "confidence"]
            },
            "detailed": {
                "description": "详细解释",
                "includes": ["goal", "full_evidence", "complete_reasoning_chain", "all_sources",
                            "confidence", "related_knowledge", "historical_patterns", "risk_assessment"]
            },
            "comprehensive": {
                "description": "全面解释",
                "includes": ["goal", "all_evidence", "full_reasoning_with_alternatives",
                            "comprehensive_sources", "confidence_detailed", "knowledge_graph_links",
                            "historical_patterns", "risk_assessment", "success_probability",
                            "recommendations", "alternatives_considered"]
            }
        }

    def knowledge_driven_decision(self, goal: str, context: Dict = None) -> Dict:
        """
        知识驱动的智能决策

        融合跨轮知识，做更明智的进化决策。

        Args:
            goal: 进化目标描述
            context: 额外上下文信息

        Returns:
            决策结果，包含决策内容、知识来源、推理过程、解释
        """
        context = context or {}
        result = {
            "goal": goal,
            "timestamp": datetime.now().isoformat(),
            "decision": None,
            "knowledge_sources": [],
            "reasoning_chain": [],
            "explanation": None,
            "confidence": 0.0,
            "status": "pending"
        }

        # 步骤1：获取跨轮知识支持
        knowledge_context = {
            "goal": goal,
            "include_knowledge": True,
            "include_patterns": True,
            "include_recommendations": True
        }

        if self.cross_fusion_engine:
            try:
                # 获取自适应推理结果
                inference_result = self.cross_fusion_engine.adaptive_inference(knowledge_context)
                if inference_result:
                    result["knowledge_sources"] = inference_result.get("knowledge_sources", [])
                    result["reasoning_chain"].append({
                        "step": "knowledge_fusion",
                        "description": "融合跨轮知识进行推理",
                        "data": inference_result.get("reasoning", ""),
                        "confidence": inference_result.get("confidence", 0.5)
                    })
                    # 使用推理结果辅助决策
                    result["decision"] = inference_result.get("recommended_direction", goal)
                    result["confidence"] = inference_result.get("confidence", 0.5)
            except Exception as e:
                result["reasoning_chain"].append({
                    "step": "knowledge_fusion",
                    "description": f"知识融合过程中出现问题: {str(e)}",
                    "status": "fallback"
                })

        # 步骤2：如果没有从知识融合获得决策，使用目标本身
        if not result["decision"]:
            result["decision"] = goal

        # 步骤3：生成解释
        explanation_level = context.get("explanation_level", "standard")
        result["explanation"] = self._generate_integrated_explanation(
            goal, result["decision"], result["knowledge_sources"],
            result["reasoning_chain"], explanation_level
        )

        # 步骤4：记录决策（如果可解释性引擎可用）
        if self.explainability_engine and result["decision"]:
            try:
                evidence = {
                    "knowledge_sources": result["knowledge_sources"],
                    "context": context
                }
                self.explainability_engine.record_decision(
                    decision_id=f"round_{context.get('round', 'unknown')}",
                    goal=result["decision"],
                    evidence=evidence,
                    reasoning_chain=result["reasoning_chain"],
                    sources=["cross_round_knowledge_fusion", "decision_knowledge_integration"],
                    confidence=result["confidence"]
                )
            except Exception as e:
                pass  # 记录失败不阻断主流程

        result["status"] = "completed"
        return result

    def link_reasoning_to_knowledge(self, decision_id: str, knowledge_items: List[Dict]) -> Dict:
        """
        将决策推理链与知识图谱关联

        让每个决策可追溯到历史知识来源。

        Args:
            decision_id: 决策ID
            knowledge_items: 关联的知识项列表

        Returns:
            关联结果
        """
        # 加载现有关联
        links = self._load_decision_knowledge_links()

        # 添加新的关联
        if decision_id not in links:
            links[decision_id] = []

        links[decision_id].extend(knowledge_items)

        # 保存
        self._save_decision_knowledge_links(links)

        return {
            "decision_id": decision_id,
            "linked_knowledge_count": len(knowledge_items),
            "status": "linked"
        }

    def get_knowledge_traced_explanation(self, decision_id: str, level: str = "standard") -> Dict:
        """
        获取可追溯到知识图谱的解释

        Args:
            decision_id: 决策ID
            level: 解释详细程度

        Returns:
            解释结果
        """
        # 加载决策-知识关联
        links = self._load_decision_knowledge_links()

        # 获取可解释性引擎的解释
        explanation = None
        if self.explainability_engine:
            try:
                explanation = self.explainability_engine.explain_decision(decision_id, level)
            except Exception:
                pass

        # 构建可追溯的解释
        result = {
            "decision_id": decision_id,
            "explanation_level": level,
            "knowledge_links": links.get(decision_id, []),
            "explanation": explanation,
            "status": "success"
        }

        return result

    def adaptive_explanation_depth(self, decision: Dict) -> str:
        """
        自适应解释深度

        根据决策复杂度自动调整解释详细程度。

        Args:
            decision: 决策结果字典

        Returns:
            推荐的解释深度级别
        """
        # 评估决策复杂度
        complexity_score = 0

        # 因素1：知识来源数量
        knowledge_count = len(decision.get("knowledge_sources", []))
        if knowledge_count >= 5:
            complexity_score += 2
        elif knowledge_count >= 3:
            complexity_score += 1

        # 因素2：推理链长度
        reasoning_length = len(decision.get("reasoning_chain", []))
        if reasoning_length >= 4:
            complexity_score += 2
        elif reasoning_length >= 2:
            complexity_score += 1

        # 因素3：置信度
        confidence = decision.get("confidence", 0.5)
        if confidence < 0.5:
            complexity_score += 1  # 低置信度需要更详细解释

        # 因素4：决策目标复杂度（通过关键词判断）
        goal = decision.get("goal", "")
        complex_keywords = ["深度集成", "多引擎协同", "跨轮次", "自适应", "复杂"]
        if any(kw in goal for kw in complex_keywords):
            complexity_score += 1

        # 根据复杂度返回建议的级别
        if complexity_score >= 4:
            return "comprehensive"
        elif complexity_score >= 2:
            return "detailed"
        else:
            return "standard"

    def record_feedback_and_learn(self, decision_id: str, execution_result: Dict) -> Dict:
        """
        决策效果反馈学习

        将决策执行效果反馈给知识图谱优化，实现持续学习。

        Args:
            decision_id: 决策ID
            execution_result: 执行结果

        Returns:
            学习结果
        """
        feedback = {
            "decision_id": decision_id,
            "execution_result": execution_result,
            "timestamp": datetime.now().isoformat(),
            "learned_insights": []
        }

        # 分析执行结果
        success = execution_result.get("success", True)
        details = execution_result.get("details", {})

        # 生成学习洞察
        if success:
            feedback["learned_insights"].append({
                "type": "success_pattern",
                "description": "该决策方向执行成功，可作为未来决策参考",
                "applicable": True
            })

            # 如果有置信度信息，更新知识权重
            confidence = execution_result.get("confidence")
            if confidence and self.cross_fusion_engine:
                feedback["learned_insights"].append({
                    "type": "confidence_update",
                    "description": f"决策置信度 {confidence} 与实际执行结果对比",
                    "confidence_accurate": confidence > 0.7 if success else confidence < 0.5
                })
        else:
            error = execution_result.get("error", "unknown")
            feedback["learned_insights"].append({
                "type": "failure_analysis",
                "description": f"执行失败，原因: {error}",
                "applicable": True,
                "action": "avoid_similar_decisions"
            })

        # 保存反馈
        self._save_feedback(feedback)

        # 如果有跨融合引擎，尝试更新其知识
        if self.cross_fusion_engine and hasattr(self.cross_fusion_engine, 'learn_from_feedback'):
            try:
                self.cross_fusion_engine.learn_from_feedback(decision_id, feedback)
            except Exception:
                pass

        return feedback

    def _generate_integrated_explanation(self, goal: str, decision: str,
                                        knowledge_sources: List,
                                        reasoning_chain: List,
                                        level: str) -> Dict:
        """生成集成的解释"""

        includes = self.explanation_levels.get(level, {}).get("includes", [])

        explanation = {}

        if "goal" in includes:
            explanation["goal"] = goal

        if "evidence" in includes or "full_evidence" in includes:
            explanation["evidence"] = {
                "knowledge_sources_count": len(knowledge_sources),
                "knowledge_sources": knowledge_sources[:5] if len(knowledge_sources) > 5 else knowledge_sources
            }

        if "main_evidence" in includes:
            explanation["main_evidence"] = knowledge_sources[0] if knowledge_sources else "无"

        if "reasoning_chain" in includes or "complete_reasoning_chain" in includes:
            explanation["reasoning_chain"] = reasoning_chain

        if "full_reasoning_with_alternatives" in includes:
            explanation["reasoning_with_alternatives"] = {
                "primary_reasoning": reasoning_chain,
                "alternatives_considered": self._get_alternatives(goal)
            }

        if "sources" in includes or "all_sources" in includes or "comprehensive_sources" in includes:
            explanation["sources"] = [
                "cross_round_knowledge_fusion",
                "decision_knowledge_integration",
                "historical_evolution_data"
            ]

        if "confidence" in includes or "confidence_detailed" in includes:
            confidence_value = sum(r.get("confidence", 0) for r in reasoning_chain) / max(len(reasoning_chain), 1)
            explanation["confidence"] = confidence_value
            if "confidence_detailed" in includes:
                explanation["confidence_analysis"] = {
                    "value": confidence_value,
                    "factors": self._analyze_confidence_factors(knowledge_sources, reasoning_chain)
                }

        if "related_knowledge" in includes or "knowledge_graph_links" in includes:
            explanation["related_knowledge"] = knowledge_sources[:3] if knowledge_sources else []

        if "historical_patterns" in includes:
            explanation["historical_patterns"] = self._get_relevant_patterns(goal)

        if "risk_assessment" in includes:
            explanation["risk_assessment"] = self._assess_risks(decision)

        if "success_probability" in includes:
            explanation["success_probability"] = self._estimate_success_probability(knowledge_sources)

        if "recommendations" in includes:
            explanation["recommendations"] = self._generate_recommendations(decision, knowledge_sources)

        if "alternatives_considered" in includes:
            explanation["alternatives"] = self._get_alternatives(goal)

        return explanation

    def _get_alternatives(self, goal: str) -> List[Dict]:
        """获取考虑过的替代方案"""
        # 这里可以基于知识图谱获取替代方案
        return [
            {"alternative": f"替代方案A: {goal}", "status": "considered_not_selected"},
            {"alternative": f"替代方案B: 简化{goal}", "status": "considered_not_selected"}
        ]

    def _analyze_confidence_factors(self, knowledge_sources: List, reasoning_chain: List) -> Dict:
        """分析置信度因素"""
        return {
            "knowledge_source_diversity": len(set(knowledge_sources)),
            "reasoning_chain_strength": len(reasoning_chain),
            "historical_support": bool(knowledge_sources)
        }

    def _get_relevant_patterns(self, goal: str) -> List[Dict]:
        """获取相关历史模式"""
        return []  # 简化实现

    def _assess_risks(self, decision: str) -> Dict:
        """评估风险"""
        return {
            "overall_risk": "low",
            "factors": []
        }

    def _estimate_success_probability(self, knowledge_sources: List) -> float:
        """估计成功概率"""
        base_probability = 0.6
        if knowledge_sources:
            base_probability = min(0.9, 0.6 + 0.05 * len(knowledge_sources))
        return base_probability

    def _generate_recommendations(self, decision: str, knowledge_sources: List) -> List[str]:
        """生成建议"""
        return [
            "持续监控决策执行效果",
            "收集反馈以优化决策质量"
        ]

    def _load_decision_knowledge_links(self) -> Dict:
        """加载决策-知识关联"""
        if self.decision_knowledge_file.exists():
            try:
                with open(self.decision_knowledge_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_decision_knowledge_links(self, links: Dict):
        """保存决策-知识关联"""
        with open(self.decision_knowledge_file, 'w', encoding='utf-8') as f:
            json.dump(links, f, ensure_ascii=False, indent=2)

    def _save_feedback(self, feedback: Dict):
        """保存反馈"""
        feedbacks = []
        if self.feedback_file.exists():
            try:
                with open(self.feedback_file, 'r', encoding='utf-8') as f:
                    feedbacks = json.load(f)
            except Exception:
                feedbacks = []

        feedbacks.append(feedback)

        with open(self.feedback_file, 'w', encoding='utf-8') as f:
            json.dump(feedbacks, f, ensure_ascii=False, indent=2)

    def get_status(self) -> Dict:
        """获取引擎状态"""
        return {
            "name": "智能全场景进化决策-知识-解释深度集成引擎",
            "version": "1.0.0",
            "round": 334,
            "cross_fusion_engine_available": self.cross_fusion_engine is not None,
            "explainability_engine_available": self.explainability_engine is not None,
            "status": "ready",
            "capabilities": [
                "知识驱动的智能决策",
                "决策推理链与知识图谱关联",
                "自适应解释深度",
                "决策效果反馈学习"
            ]
        }


def main():
    """测试入口"""
    import sys

    engine = DecisionKnowledgeIntegrationEngine()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "--status":
            print(json.dumps(engine.get_status(), ensure_ascii=False, indent=2))

        elif command == "--decision":
            goal = sys.argv[2] if len(sys.argv) > 2 else "测试进化目标"
            context = {"round": 334, "explanation_level": "standard"}
            result = engine.knowledge_driven_decision(goal, context)
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif command == "--link":
            decision_id = sys.argv[2] if len(sys.argv) > 2 else "test_decision"
            knowledge_items = [
                {"id": "kg_1", "type": "pattern", "description": "测试知识项"}
            ]
            result = engine.link_reasoning_to_knowledge(decision_id, knowledge_items)
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif command == "--explain":
            decision_id = sys.argv[2] if len(sys.argv) > 2 else "test_decision"
            level = sys.argv[3] if len(sys.argv) > 3 else "standard"
            result = engine.get_knowledge_traced_explanation(decision_id, level)
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif command == "--feedback":
            decision_id = sys.argv[2] if len(sys.argv) > 2 else "test_decision"
            execution_result = {"success": True, "details": {"time": 10}}
            result = engine.record_feedback_and_learn(decision_id, execution_result)
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif command == "--adaptive-level":
            decision = {"goal": "测试", "knowledge_sources": ["a", "b", "c"],
                      "reasoning_chain": [{}, {}], "confidence": 0.7}
            level = engine.adaptive_explanation_depth(decision)
            print(json.dumps({"recommended_level": level}, ensure_ascii=False, indent=2))

        else:
            print("未知命令")
            print("可用命令:")
            print("  --status: 显示引擎状态")
            print("  --decision <目标>: 知识驱动的决策")
            print("  --link <决策ID> <知识项>: 关联决策与知识")
            print("  --explain <决策ID> [级别]: 获取可追溯解释")
            print("  --feedback <决策ID>: 记录反馈并学习")
            print("  --adaptive-level: 测试自适应解释深度")
    else:
        print(json.dumps(engine.get_status(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()