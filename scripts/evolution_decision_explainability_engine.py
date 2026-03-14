"""
智能进化决策可解释性深度增强引擎 (Evolution Decision Explainability Engine)

让系统能够详细解释每个进化决策的背后逻辑、证据来源、推理过程，
形成真正的"知其然亦知其所以然"的进化决策闭环。

功能：
1. 决策证据链追踪 - 记录每个进化决策所依据的证据（知识图谱、历史模式、系统状态）
2. 推理过程可视化 - 展示从假设到决策的完整推理链
3. 决策历史可追溯 - 存储和查询历史进化决策及其解释
4. 多维度解释生成 - 从知识融合、模式识别、效能分析等维度提供解释
5. 决策质量评估 - 评估每个决策的质量和可信度

集成 round 332 的跨轮知识融合引擎来增强解释能力。
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class EvolutionDecisionExplainabilityEngine:
    """智能进化决策可解释性深度增强引擎"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.state_dir = self.base_dir / "runtime" / "state"
        self.logs_dir = self.base_dir / "runtime" / "logs"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # 决策证据存储文件
        self.decision_evidence_file = self.state_dir / "evolution_decision_evidence.json"

        # 尝试导入跨轮知识融合引擎
        self.cross_fusion_engine = None
        try:
            from evolution_cross_round_knowledge_fusion_engine import EvolutionCrossRoundKnowledgeFusionEngine
            self.cross_fusion_engine = EvolutionCrossRoundKnowledgeFusionEngine()
        except ImportError:
            pass

        # 决策类型及其解释模板
        self.decision_templates = {
            "capability_gap": "基于能力缺口分析，发现系统缺少{capability}能力",
            "failure_lesson": "从历史失败中吸取教训，避免{lesson}问题再次发生",
            "pattern_discovery": "从进化历史中发现{pattern}模式，决定采取{action}",
            "knowledge_fusion": "融合{count}个跨轮知识，发现{insight}",
            "efficiency_optimization": "分析进化效率，发现可优化点{optimization}",
            "self_proposed": "系统自主提出的创新方向：{proposal}",
            "hybrid": "综合多种证据的混合决策：{factors}"
        }

        # 证据来源权重
        self.evidence_weights = {
            "knowledge_graph": 0.25,
            "historical_patterns": 0.20,
            "failure_analysis": 0.20,
            "capability_gaps": 0.15,
            "efficiency_metrics": 0.10,
            "self_proposed": 0.10
        }

    def record_decision(self, decision_id: str, goal: str, evidence: Dict, reasoning_chain: List[Dict],
                       sources: List[str], confidence: float = 0.8) -> Dict:
        """
        记录一个进化决策及其证据

        Args:
            decision_id: 决策ID（通常是 round 号）
            goal: 进化目标描述
            evidence: 决策所依据的证据字典
            reasoning_chain: 推理链列表
            sources: 证据来源列表
            confidence: 决策置信度

        Returns:
            记录结果
        """
        record = {
            "decision_id": decision_id,
            "goal": goal,
            "evidence": evidence,
            "reasoning_chain": reasoning_chain,
            "sources": sources,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat(),
            "explanation": self._generate_explanation(goal, evidence, reasoning_chain, sources)
        }

        # 加载现有记录
        records = self._load_records()

        # 检查是否已存在同ID记录
        existing_ids = [r.get("decision_id") for r in records]
        if decision_id in existing_ids:
            # 更新现有记录
            for i, r in enumerate(records):
                if r.get("decision_id") == decision_id:
                    records[i] = record
                    break
        else:
            records.append(record)

        # 保存记录
        self._save_records(records)

        return {
            "status": "recorded",
            "decision_id": decision_id,
            "explanation": record["explanation"]
        }

    def _generate_explanation(self, goal: str, evidence: Dict, reasoning_chain: List[Dict],
                             sources: List[str]) -> str:
        """生成决策的自然语言解释"""

        explanations = []
        explanations.append(f"**进化目标**：{goal}\n")

        # 证据来源分析
        explanations.append("**决策依据**：")
        for source in sources:
            source_weight = self.evidence_weights.get(source, 0.1)
            explanations.append(f"- {source}（权重：{source_weight:.0%}）")

            if source in evidence:
                evidence_content = evidence[source]
                if isinstance(evidence_content, dict):
                    for key, value in evidence_content.items():
                        explanations.append(f"  • {key}: {value}")
                elif isinstance(evidence_content, list):
                    for item in evidence_content[:3]:  # 最多显示3条
                        explanations.append(f"  • {item}")
                else:
                    explanations.append(f"  • {evidence_content}")

        # 推理链展示
        if reasoning_chain:
            explanations.append("\n**推理过程**：")
            for i, step in enumerate(reasoning_chain, 1):
                step_type = step.get("type", "unknown")
                content = step.get("content", "")
                conclusion = step.get("conclusion", "")

                explanations.append(f"{i}. [{step_type}] {content}")
                if conclusion:
                    explanations.append(f"   → 结论：{conclusion}")

        # 综合解释
        explanations.append("\n**决策总结**：")
        # 根据证据来源生成总结
        if "knowledge_fusion" in sources and self.cross_fusion_engine:
            explanations.append("系统通过深度融合跨轮知识，分析历史进化模式，结合当前系统状态，")
            explanations.append("做出了符合系统长期发展目标的进化决策。")
        elif "failure_analysis" in sources:
            explanations.append("基于历史失败教训，系统决定采取预防性进化方向，")
            explanations.append("以避免类似问题再次发生。")
        elif "efficiency_optimization" in sources:
            explanations.append("基于进化效率分析，系统决定采取优化措施，")
            explanations.append("以提升整体进化效果。")
        else:
            explanations.append("综合多维度证据，系统做出了该进化决策。")

        return "\n".join(explanations)

    def explain_decision(self, decision_id: str) -> str:
        """
        解释特定决策

        Args:
            decision_id: 决策ID

        Returns:
            决策解释
        """
        records = self._load_records()

        for record in records:
            if record.get("decision_id") == decision_id:
                return record.get("explanation", "未找到该决策的解释")

        return f"未找到决策 {decision_id} 的记录"

    def get_decision_history(self, limit: int = 10) -> List[Dict]:
        """
        获取决策历史

        Args:
            limit: 返回数量限制

        Returns:
            决策历史列表
        """
        records = self._load_records()
        # 按时间倒序
        sorted_records = sorted(records, key=lambda x: x.get("timestamp", ""), reverse=True)
        return sorted_records[:limit]

    def analyze_decision_quality(self, decision_id: str) -> Dict:
        """
        分析决策质量

        Args:
            decision_id: 决策ID

        Returns:
            质量分析结果
        """
        records = self._load_records()

        for record in records:
            if record.get("decision_id") == decision_id:
                evidence = record.get("evidence", {})
                sources = record.get("sources", [])
                confidence = record.get("confidence", 0.5)

                # 计算证据覆盖率
                covered_sources = sum(1 for s in sources if s in evidence)
                coverage = covered_sources / len(sources) if sources else 0

                # 计算推理链完整性
                reasoning_chain = record.get("reasoning_chain", [])
                chain_completeness = min(len(reasoning_chain) / 5, 1.0)  # 假设5步为完整

                # 综合质量评分
                quality_score = (confidence * 0.4 + coverage * 0.3 + chain_completeness * 0.3)

                return {
                    "decision_id": decision_id,
                    "quality_score": quality_score,
                    "confidence": confidence,
                    "evidence_coverage": coverage,
                    "reasoning_chain_completeness": chain_completeness,
                    "quality_level": "高" if quality_score > 0.7 else ("中" if quality_score > 0.4 else "低"),
                    "suggestions": self._generate_quality_suggestions(quality_score, coverage, chain_completeness)
                }

        return {"error": f"未找到决策 {decision_id}"}

    def _generate_quality_suggestions(self, quality: float, coverage: float, chain_complete: float) -> List[str]:
        """生成质量改进建议"""
        suggestions = []

        if quality < 0.7:
            if coverage < 0.5:
                suggestions.append("建议增加更多证据来源以支持决策")
            if chain_complete < 0.5:
                suggestions.append("建议完善推理链，增加更多推理步骤")
            if quality < 0.4:
                suggestions.append("建议重新评估该决策的依据")

        if not suggestions:
            suggestions.append("决策质量良好，无需改进")

        return suggestions

    def get_recent_explanations(self, count: int = 5) -> str:
        """
        获取最近决策的解释摘要

        Args:
            count: 获取数量

        Returns:
            解释摘要
        """
        records = self.get_decision_history(count)

        if not records:
            return "暂无决策记录"

        output = ["**最近进化决策解释摘要**\n"]

        for record in records:
            decision_id = record.get("decision_id", "unknown")
            goal = record.get("goal", "未知目标")[:50]
            timestamp = record.get("timestamp", "")
            confidence = record.get("confidence", 0)

            output.append(f"**{decision_id}** ({timestamp[:10]})")
            output.append(f"- 目标：{goal}...")
            output.append(f"- 置信度：{confidence:.0%}")
            output.append("")

        return "\n".join(output)

    def _load_records(self) -> List[Dict]:
        """加载决策记录"""
        if self.decision_evidence_file.exists():
            try:
                with open(self.decision_evidence_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_records(self, records: List[Dict]):
        """保存决策记录"""
        try:
            with open(self.decision_evidence_file, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存决策记录失败：{e}")

    def get_status(self) -> Dict:
        """获取引擎状态"""
        records = self._load_records()

        # 统计各来源使用情况
        source_stats = {}
        for record in records:
            for source in record.get("sources", []):
                source_stats[source] = source_stats.get(source, 0) + 1

        # 统计决策质量分布
        quality_levels = {"高": 0, "中": 0, "低": 0}
        for record in records:
            confidence = record.get("confidence", 0)
            if confidence > 0.7:
                quality_levels["高"] += 1
            elif confidence > 0.4:
                quality_levels["中"] += 1
            else:
                quality_levels["低"] += 1

        return {
            "engine_name": "智能进化决策可解释性深度增强引擎",
            "version": "1.0.0",
            "total_decisions": len(records),
            "source_statistics": source_stats,
            "quality_distribution": quality_levels,
            "cross_fusion_available": self.cross_fusion_engine is not None,
            "capabilities": [
                "决策证据链追踪 - 记录每个决策的依据",
                "推理过程可视化 - 展示完整推理链",
                "决策历史可追溯 - 查询历史决策",
                "多维度解释生成 - 从多角度解释决策",
                "决策质量评估 - 评估决策质量并提供建议",
                "跨轮知识融合集成 - 增强解释深度"
            ]
        }

    def auto_explain_current_decision(self) -> str:
        """
        自动解释当前轮次的决策（基于最新状态）

        Returns:
            解释内容
        """
        # 读取当前任务状态
        mission_file = self.state_dir / "current_mission.json"
        if mission_file.exists():
            try:
                with open(mission_file, "r", encoding="utf-8") as f:
                    mission = json.load(f)

                current_goal = mission.get("current_goal", "待定")
                loop_round = mission.get("loop_round", 333)

                # 读取上一轮的知识融合状态
                evidence = {}
                sources = []

                if self.cross_fusion_engine:
                    try:
                        fusion_status = self.cross_fusion_engine.get_status()
                        evidence["knowledge_fusion"] = fusion_status
                        sources.append("knowledge_fusion")
                    except Exception:
                        pass

                # 读取能力缺口
                gaps_file = self.base_dir / "references" / "capability_gaps.md"
                if gaps_file.exists():
                    evidence["capability_gaps"] = "见 capability_gaps.md"
                    sources.append("capability_gaps")

                # 读取失败教训
                failures_file = self.base_dir / "references" / "failures.md"
                if failures_file.exists():
                    evidence["failure_analysis"] = "见 failures.md"
                    sources.append("failure_analysis")

                # 构建简单推理链
                reasoning_chain = [
                    {"type": "分析", "content": "分析当前系统状态和能力缺口", "conclusion": "确定进化方向"},
                    {"type": "融合", "content": "融合跨轮进化知识", "conclusion": "获取历史经验"},
                    {"type": "决策", "content": "基于证据做出进化决策", "conclusion": current_goal}
                ]

                # 生成解释
                explanation = self._generate_explanation(
                    current_goal, evidence, reasoning_chain, sources
                )

                return explanation

            except Exception as e:
                return f"自动解释失败：{e}"

        return "无法获取当前决策信息"


def main():
    """CLI 入口"""
    import sys
    import argparse
    import io

    # 设置输出编码为 UTF-8，处理 Windows GBK 环境
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="智能进化决策可解释性深度增强引擎")
    parser.add_argument("action", nargs="?", default="status",
                        choices=["status", "record", "explain", "history", "quality", "recent", "auto_explain"],
                        help="执行的操作")
    parser.add_argument("--decision-id", "-d", help="决策ID")
    parser.add_argument("--goal", "-g", help="进化目标")
    parser.add_argument("--evidence", "-e", type=json.loads, help="证据（JSON格式）")
    parser.add_argument("--sources", "-s", nargs="+", help="证据来源")
    parser.add_argument("--chain", "-c", type=json.loads, help="推理链（JSON格式）")
    parser.add_argument("--confidence", type=float, default=0.8, help="置信度")
    parser.add_argument("--limit", "-l", type=int, default=5, help="返回数量限制")

    args = parser.parse_args()

    engine = EvolutionDecisionExplainabilityEngine()

    if args.action == "status":
        result = engine.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == "record":
        if not args.decision_id or not args.goal:
            print("错误：需要提供 --decision-id 和 --goal 参数")
            return

        result = engine.record_decision(
            args.decision_id,
            args.goal,
            args.evidence or {},
            args.chain or [],
            args.sources or [],
            args.confidence
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == "explain":
        if not args.decision_id:
            print("错误：需要提供 --decision-id 参数")
            return
        print(engine.explain_decision(args.decision_id))

    elif args.action == "history":
        history = engine.get_decision_history(args.limit)
        print(json.dumps(history, ensure_ascii=False, indent=2))

    elif args.action == "quality":
        if not args.decision_id:
            print("错误：需要提供 --decision-id 参数")
            return
        result = engine.analyze_decision_quality(args.decision_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == "recent":
        print(engine.get_recent_explanations(args.limit))

    elif args.action == "auto_explain":
        print(engine.auto_explain_current_decision())


if __name__ == "__main__":
    main()