"""
元进化优化机会主动发现与智能决策增强引擎
Evolution Meta Optimization Opportunity Discovery and Intelligent Decision Engine

version: 1.0.0
description: 让系统能够主动从进化历史、跨引擎协同、知识图谱中发现优化机会，
生成智能优化建议，并能够自主决策是否执行优化，
形成「机会发现→智能评估→自动决策→执行优化→效果验证」的完整优化闭环。

功能：
1. 进化历史优化机会发现 - 从590+轮进化历史中分析低效模式、重复改进、资源浪费
2. 跨引擎协同优化机会发现 - 分析引擎间协作效率、识别协同瓶颈
3. 知识图谱优化机会发现 - 从知识图谱中识别知识缺口、推理断点
4. 智能优化建议生成 - 将发现的优化机会转化为可执行建议
5. 自主决策能力 - 评估优化建议的价值、风险、成本，自主决定是否执行
6. 与已有进化引擎的深度集成
7. 驾驶舱数据接口
8. do.py 集成支持

依赖：
- round 589: 元进化价值投资智能决策引擎
- round 551: 跨轮次深度学习与自适应策略迭代优化引擎
- round 552: 进化方法论自动优化引擎
- round 553: 元进化策略执行验证与闭环优化引擎
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from collections import defaultdict


class MetaOptimizationOpportunityDiscoveryEngine:
    """元进化优化机会主动发现与智能决策增强引擎"""

    VERSION = "1.0.0"

    def __init__(self, runtime_dir: str = None):
        self.runtime_dir = runtime_dir or os.path.join(os.path.dirname(__file__), "..", "runtime")
        self.state_dir = os.path.join(self.runtime_dir, "state")
        self.logs_dir = os.path.join(self.runtime_dir, "logs")

        # 优化机会缓存
        self.opportunity_cache_file = os.path.join(self.state_dir, "optimization_opportunity_cache.json")
        self.current_opportunities = []
        self.decision_results = {}

    def load_evolution_history(self) -> List[Dict]:
        """加载进化历史数据"""
        history = []
        state_dir = Path(self.state_dir)

        # 加载所有已完成的历史文件
        for file in state_dir.glob("evolution_completed_*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get("round"):
                        history.append(data)
            except Exception as e:
                print(f"[优化机会发现] 加载历史失败 {file}: {e}")

        # 按轮次排序
        history.sort(key=lambda x: x.get("round", 0))
        return history

    def discover_history_optimization_opportunities(self) -> Dict:
        """发现进化历史中的优化机会

        分析590+轮进化历史，识别：
        - 低效模式（重复改进某功能）
        - 资源浪费（多轮做类似的事情）
        - 优化空间（可以合并的改进）
        """
        history = self.load_evolution_history()

        opportunities = {
            "total_rounds": len(history),
            "patterns": [],
            "inefficiencies": [],
            "optimization_suggestions": []
        }

        if not history:
            return opportunities

        # 分析进化主题分布
        theme_counts = defaultdict(int)
        for item in history:
            goal = item.get("current_goal", "")
            # 提取关键主题词
            if "价值" in goal:
                theme_counts["价值投资"] += 1
            if "元进化" in goal or "自" in goal:
                theme_counts["元进化"] += 1
            if "知识" in goal:
                theme_counts["知识"] += 1
            if "决策" in goal:
                theme_counts["决策"] += 1
            if "创新" in goal:
                theme_counts["创新"] += 1
            if "健康" in goal or "自愈" in goal:
                theme_counts["健康"] += 1
            if "协作" in goal or "协同" in goal:
                theme_counts["协作"] += 1

        opportunities["patterns"] = [
            {
                "type": "主题分布",
                "data": dict(theme_counts),
                "insight": "从主题分布可以看出当前进化集中在哪些领域"
            }
        ]

        # 分析连续轮次的相似性
        similar_rounds = []
        for i in range(len(history) - 1):
            goal1 = history[i].get("current_goal", "")[:50]
            goal2 = history[i + 1].get("current_goal", "")[:50]

            # 简单的关键词重叠检测
            keywords1 = set(goal1.split()) & set(goal2.split())
            if len(keywords1) >= 2:
                similar_rounds.append({
                    "round_a": history[i].get("round"),
                    "round_b": history[i + 1].get("round"),
                    "shared_keywords": list(keywords1)
                })

        if similar_rounds:
            opportunities["inefficiencies"].append({
                "type": "连续相似进化",
                "count": len(similar_rounds),
                "details": similar_rounds[:5],
                "suggestion": "连续轮次做相似主题的进化，考虑合并或间隔执行"
            })

        # 检测已完成但未充分验证的轮次
        unverified = [h for h in history if h.get("verify_result", {}).get("status") != "pass"]
        if unverified:
            opportunities["inefficiencies"].append({
                "type": "未验证轮次",
                "count": len(unverified),
                "rounds": [h.get("round") for h in unverified],
                "suggestion": "部分轮次缺少验证通过记录，需要补充验证或分析原因"
            })

        # 生成优化建议
        if theme_counts:
            max_theme = max(theme_counts.items(), key=lambda x: x[1])
            opportunities["optimization_suggestions"].append({
                "area": "进化方向",
                "priority": "高",
                "title": f"关注度不均: {max_theme[0]}",
                "description": f"当前进化主题分布不均，{max_theme[0]}占比过高",
                "actions": [
                    "增加其他领域如创新、健康、协作的进化",
                    "平衡各领域的能力覆盖"
                ]
            })

        if similar_rounds:
            opportunities["optimization_suggestions"].append({
                "area": "进化效率",
                "priority": "中",
                "title": "连续相似进化存在重复",
                "description": "检测到连续轮次做相似主题的进化",
                "actions": [
                    "建立进化主题间隔机制",
                    "合并相似进化为一次性完成"
                ]
            })

        return opportunities

    def discover_cross_engine_optimization_opportunities(self) -> Dict:
        """发现跨引擎协同优化机会

        分析引擎间的协作效率，识别协同瓶颈和优化空间
        """
        opportunities = {
            "engines": [],
            "collaboration_gaps": [],
            "optimization_suggestions": []
        }

        # 扫描所有进化引擎
        scripts_dir = Path(os.path.join(os.path.dirname(__file__), "..", "scripts"))
        engine_files = list(scripts_dir.glob("evolution_*.py"))

        engine_list = []
        for f in engine_files:
            name = f.stem.replace("evolution_", "").replace("_", " ").title()
            engine_list.append({
                "name": name,
                "file": f.name
            })

        opportunities["engines"] = engine_list
        opportunities["total_engines"] = len(engine_list)

        # 基于已知的引擎依赖关系分析协作机会
        # 假设：后面的轮次依赖前面的轮次
        history = self.load_evolution_history()

        # 分析引擎调用链
        engine_dependencies = defaultdict(set)
        for item in history:
            round_num = item.get("round", 0)
            goal = item.get("current_goal", "")

            # 提取依赖轮次（从描述中提取 rXXX 格式）
            import re
            deps = re.findall(r'r(\d+)', goal)
            for dep in deps:
                engine_dependencies[round_num].add(int(dep))

        # 找出潜在协作机会（无直接依赖但可以协作的引擎）
        collaboration_opportunities = []
        for round_a in engine_dependencies:
            deps_a = engine_dependencies[round_a]
            for round_b in engine_dependencies:
                if round_b > round_a and round_b not in deps_a:
                    # 检查是否可以考虑协作
                    if round_b - round_a <= 10:  # 10轮以内
                        collaboration_opportunities.append({
                            "from_round": round_a,
                            "to_round": round_b,
                            "gap": round_b - round_a,
                            "suggestion": f"round {round_a} 和 round {round_b} 可以考虑协同优化"
                        })

        if collaboration_opportunities:
            opportunities["collaboration_gaps"] = collaboration_opportunities[:10]
            opportunities["optimization_suggestions"].append({
                "area": "跨引擎协同",
                "priority": "中",
                "title": "发现跨引擎协作机会",
                "description": f"发现 {len(collaboration_opportunities)} 个潜在的跨引擎协作机会",
                "actions": [
                    "增强引擎间的数据共享",
                    "建立跨引擎触发机制",
                    "优化依赖关系减少冗余"
                ]
            })

        # 默认优化建议
        opportunities["optimization_suggestions"].append({
            "area": "引擎管理",
            "priority": "低",
            "title": "引擎数量与复杂度平衡",
            "description": f"当前共有 {len(engine_list)} 个进化引擎，需要平衡功能丰富性与维护成本",
            "actions": [
                "评估引擎功能重叠",
                "考虑合并小型引擎",
                "建立引擎健康度评估"
            ]
        })

        return opportunities

    def discover_knowledge_optimization_opportunities(self) -> Dict:
        """发现知识图谱优化机会

        从知识图谱角度识别知识缺口和推理断点
        """
        opportunities = {
            "knowledge_coverage": {},
            "reasoning_gaps": [],
            "optimization_suggestions": []
        }

        # 读取能力文档
        capabilities_file = os.path.join(os.path.dirname(__file__), "..", "references", "capabilities.md")
        if os.path.exists(capabilities_file):
            try:
                with open(capabilities_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 统计能力类别
                    categories = ["操作", "感知", "推理", "执行", "学习", "创新", "元能力"]
                    for cat in categories:
                        count = content.count(f"### {cat}")
                        opportunities["knowledge_coverage"][cat] = count
            except Exception as e:
                print(f"[优化机会发现] 读取能力文档失败: {e}")

        # 读取失败记录
        failures_file = os.path.join(os.path.dirname(__file__), "..", "references", "failures.md")
        if os.path.exists(failures_file):
            try:
                with open(failures_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 统计失败类型
                    failure_types = ["执行失败", "集成失败", "配置失败", "依赖失败", "超时"]
                    for ft in failure_types:
                        if ft in content:
                            opportunities["reasoning_gaps"].append({
                                "type": ft,
                                "count": content.count(ft)
                            })
            except Exception as e:
                print(f"[优化机会发现] 读取失败记录失败: {e}")

        # 基于知识覆盖生成优化建议
        if opportunities["knowledge_coverage"]:
            low_coverage = [k for k, v in opportunities["knowledge_coverage"].items() if v == 0]
            if low_coverage:
                opportunities["optimization_suggestions"].append({
                    "area": "知识覆盖",
                    "priority": "高",
                    "title": f"能力缺口: {', '.join(low_coverage)}",
                    "description": f"检测到 {len(low_coverage)} 个能力类别尚未覆盖",
                    "actions": [
                        f"补充 {', '.join(low_coverage)} 能力",
                        "完善能力文档描述"
                    ]
                })

        # 基于失败记录生成优化建议
        if opportunities["reasoning_gaps"]:
            top_gap = max(opportunities["reasoning_gaps"], key=lambda x: x.get("count", 0))
            opportunities["optimization_suggestions"].append({
                "area": "失败预防",
                "priority": "中",
                "title": f"高频失败类型: {top_gap['type']}",
                "description": f"检测到 {top_gap['type']} 类型的失败最为常见",
                "actions": [
                    f"针对 {top_gap['type']} 建立预防机制",
                    "增强错误处理和恢复能力",
                    "完善失败记录和分析"
                ]
            })

        # 默认建议
        if not opportunities["optimization_suggestions"]:
            opportunities["optimization_suggestions"].append({
                "area": "知识管理",
                "priority": "低",
                "title": "知识体系完善",
                "description": "当前知识图谱状态良好，持续维护即可",
                "actions": [
                    "定期更新能力文档",
                    "保持失败记录更新",
                    "关注新能力补充"
                ]
            })

        return opportunities

    def comprehensive_discovery(self) -> Dict:
        """综合发现所有类型的优化机会

        Returns:
            综合分析结果
        """
        history_opps = self.discover_history_optimization_opportunities()
        engine_opps = self.discover_cross_engine_optimization_opportunities()
        knowledge_opps = self.discover_knowledge_optimization_opportunities()

        # 合并所有优化建议
        all_suggestions = []
        all_suggestions.extend(history_opps.get("optimization_suggestions", []))
        all_suggestions.extend(engine_opps.get("optimization_suggestions", []))
        all_suggestions.extend(knowledge_opps.get("optimization_suggestions", []))

        # 按优先级排序
        priority_order = {"高": 0, "中": 1, "低": 2}
        all_suggestions.sort(key=lambda x: priority_order.get(x.get("priority", "低"), 2))

        # 构建综合报告
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_rounds_analyzed": history_opps.get("total_rounds", 0),
            "total_engines": engine_opps.get("total_engines", 0),
            "discovery_results": {
                "history_optimization": history_opps,
                "cross_engine_optimization": engine_opps,
                "knowledge_optimization": knowledge_opps
            },
            "all_suggestions": all_suggestions,
            "summary": {
                "high_priority": len([s for s in all_suggestions if s.get("priority") == "高"]),
                "medium_priority": len([s for s in all_suggestions if s.get("priority") == "中"]),
                "low_priority": len([s for s in all_suggestions if s.get("priority") == "低"])
            }
        }

        # 缓存结果
        self.current_opportunities = all_suggestions
        self._save_opportunity_cache(report)

        return report

    def _save_opportunity_cache(self, report: Dict):
        """保存优化机会缓存"""
        try:
            with open(self.opportunity_cache_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[优化机会发现] 保存缓存失败: {e}")

    def evaluate_and_decide(self, suggestions: List[Dict] = None) -> Dict:
        """智能评估优化建议并自主决策

        Args:
            suggestions: 优化建议列表，默认为缓存中的建议

        Returns:
            决策结果
        """
        if suggestions is None:
            suggestions = self.current_opportunities

        if not suggestions:
            suggestions = self.comprehensive_discovery().get("all_suggestions", [])

        decisions = {
            "timestamp": datetime.now().isoformat(),
            "total_suggestions": len(suggestions),
            "decisions": []
        }

        # 对每个建议进行价值-风险评估
        for suggestion in suggestions:
            priority = suggestion.get("priority", "低")
            area = suggestion.get("area", "未知")
            actions = suggestion.get("actions", [])

            # 简单的价值评估
            value_score = {"高": 3, "中": 2, "低": 1}.get(priority, 1)

            # 风险评估（基于领域）
            risk_factors = {
                "进化方向": 2,  # 较高风险，可能影响系统行为
                "进化效率": 1,  # 中等风险
                "跨引擎协同": 2,  # 较高风险，涉及多引擎
                "引擎管理": 1,  # 较低风险
                "知识覆盖": 3,  # 高价值，但执行复杂
                "失败预防": 2,  # 中等风险
                "知识管理": 1   # 较低风险
            }
            risk_score = risk_factors.get(area, 2)

            # 计算执行成本（基于动作数量）
            cost_score = min(len(actions), 3)

            # 决策：价值 > 风险 + 成本 时建议执行
            decision_value = value_score * 2 - risk_score - cost_score
            should_execute = decision_value > 2

            decision = {
                "suggestion": suggestion,
                "evaluation": {
                    "value_score": value_score,
                    "risk_score": risk_score,
                    "cost_score": cost_score,
                    "decision_value": decision_value
                },
                "decision": "执行" if should_execute else "推迟",
                "reason": self._generate_decision_reason(should_execute, priority, area)
            }
            decisions["decisions"].append(decision)

        # 统计决策结果
        execute_count = len([d for d in decisions["decisions"] if d["decision"] == "执行"])
        postpone_count = len(decisions["decisions"]) - execute_count

        decisions["summary"] = {
            "to_execute": execute_count,
            "to_postpone": postpone_count,
            "execution_rate": execute_count / len(decisions["decisions"]) if decisions["decisions"] else 0
        }

        self.decision_results = decisions
        return decisions

    def _generate_decision_reason(self, should_execute: bool, priority: str, area: str) -> str:
        """生成决策原因"""
        if should_execute:
            return f"该优化建议优先级为{priority}，针对{area}领域，预计价值高于风险，建议执行"
        else:
            return f"该优化建议针对{area}领域，执行成本或风险较高，建议推迟或进一步评估"

    def get_cockpit_data(self) -> Dict:
        """获取驾驶舱数据接口

        Returns:
            驾驶舱展示数据
        """
        # 获取最新分析结果
        if not self.current_opportunities:
            self.comprehensive_discovery()

        return {
            "engine_name": "元进化优化机会主动发现与智能决策增强引擎",
            "version": self.VERSION,
            "round": 590,
            "status": "running",
            "components": {
                "history_analysis": "已完成",
                "cross_engine_analysis": "已完成",
                "knowledge_analysis": "已完成",
                "decision_made": "已完成" if self.decision_results else "待决策"
            },
            "opportunities_found": len(self.current_opportunities),
            "summary": {
                "high_priority": len([s for s in self.current_opportunities if s.get("priority") == "高"]),
                "medium_priority": len([s for s in self.current_opportunities if s.get("priority") == "中"]),
                "low_priority": len([s for s in self.current_opportunities if s.get("priority") == "低"])
            } if self.current_opportunities else {},
            "last_discovery": datetime.now().isoformat()
        }

    def get_optimization_summary(self) -> Dict:
        """获取优化摘要

        Returns:
            优化摘要信息
        """
        if not self.current_opportunities:
            self.comprehensive_discovery()

        if not self.decision_results:
            self.evaluate_and_decide()

        decisions = self.decision_results.get("decisions", [])
        execute_decisions = [d for d in decisions if d["decision"] == "执行"]

        return {
            "total_opportunities": len(self.current_opportunities),
            "to_execute": len(execute_decisions),
            "to_postpone": len(decisions) - len(execute_decisions),
            "execution_suggestions": [
                {
                    "title": d["suggestion"].get("title", ""),
                    "area": d["suggestion"].get("area", ""),
                    "priority": d["suggestion"].get("priority", ""),
                    "reason": d["reason"]
                }
                for d in execute_decisions[:5]
            ]
        }


def main():
    """主函数：支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description="元进化优化机会主动发现与智能决策增强引擎")
    parser.add_argument("--discover", action="store_true", help="执行综合优化机会发现")
    parser.add_argument("--history", action="store_true", help="发现进化历史优化机会")
    parser.add_argument("--cross-engine", action="store_true", help="发现跨引擎协同优化机会")
    parser.add_argument("--knowledge", action="store_true", help="发现知识图谱优化机会")
    parser.add_argument("--decide", action="store_true", help="评估并决策优化建议")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")
    parser.add_argument("--summary", action="store_true", help="获取优化摘要")
    parser.add_argument("--version", action="store_true", help="显示版本信息")
    parser.add_argument("--status", action="store_true", help="显示引擎状态")

    args = parser.parse_args()

    engine = MetaOptimizationOpportunityDiscoveryEngine()

    # 版本信息
    if args.version:
        print(f"元进化优化机会主动发现与智能决策增强引擎 v{engine.VERSION}")
        return

    # 引擎状态
    if args.status:
        data = engine.get_cockpit_data()
        print(f"引擎状态: {data['status']}")
        print(f"发现优化机会数: {data['opportunities_found']}")
        print(f"各组件状态:")
        for component, status in data['components'].items():
            print(f"  - {component}: {status}")
        return

    # 驾驶舱数据
    if args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    # 优化摘要
    if args.summary:
        data = engine.get_optimization_summary()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    # 进化历史优化机会
    if args.history:
        data = engine.discover_history_optimization_opportunities()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    # 跨引擎协同优化机会
    if args.cross_engine:
        data = engine.discover_cross_engine_optimization_opportunities()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    # 知识图谱优化机会
    if args.knowledge:
        data = engine.discover_knowledge_optimization_opportunities()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    # 评估并决策
    if args.decide:
        data = engine.evaluate_and_decide()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    # 综合优化机会发现
    if args.discover:
        data = engine.comprehensive_discovery()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    # 默认显示帮助
    parser.print_help()


if __name__ == "__main__":
    main()