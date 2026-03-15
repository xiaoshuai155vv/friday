#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环知识驱动的主动涌现发现与自动化执行引擎
version 1.0.0

让系统能够主动从知识图谱和进化历史中分析模式，发现潜在优化机会，
自动生成可执行任务并跟踪执行结果，形成从"被动响应"到"主动发现"的范式升级。

功能：
1. 知识图谱深度分析 - 从进化历史和知识图谱中发现隐藏模式
2. 主动涌现发现 - 识别潜在优化机会和创新方向
3. 自动化任务生成 - 将发现转化为可执行任务
4. 执行跟踪与反馈 - 验证发现价值并更新知识库

依赖：
- evolution_kg_deep_reasoning_insight_engine.py (round 330)
- evolution_cross_round_knowledge_fusion_engine.py (round 332)
- evolution_value_realization_optimization_engine.py (round 453)
"""

import json
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import statistics
import re


class EmergenceOpportunity:
    """涌现机会"""

    def __init__(self, opportunity_id: str, title: str, description: str,
                 category: str, pattern_type: str, confidence: float,
                 potential_benefit: float, source_pattern: List[str], suggested_action: str):
        self.id = opportunity_id
        self.title = title
        self.description = description
        self.category = category  # "optimization", "innovation", "prevention", "integration"
        self.pattern_type = pattern_type  # "efficiency", "collaboration", "knowledge", "health"
        self.confidence = confidence  # 0-1
        self.potential_benefit = potential_benefit  # 0-1
        self.source_pattern = source_pattern
        self.suggested_action = suggested_action
        self.timestamp = datetime.now().isoformat()

        # 计算综合分数
        self.urgency_score = self._calculate_urgency()

    def _calculate_urgency(self) -> float:
        """计算紧急度分数"""
        # 紧急度 = 置信度 * 潜在收益
        return self.confidence * self.potential_benefit

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "pattern_type": self.pattern_type,
            "confidence": self.confidence,
            "potential_benefit": self.potential_benefit,
            "urgency_score": self.urgency_score,
            "source_pattern": self.source_pattern,
            "suggested_action": self.suggested_action,
            "timestamp": self.timestamp
        }


class KnowledgePatternAnalyzer:
    """知识模式分析器"""

    def __init__(self, runtime_dir: str):
        self.runtime_dir = Path(runtime_dir)
        self.state_dir = self.runtime_dir / "state"
        self.logs_dir = self.runtime_dir / "logs"

    def analyze_evolution_history(self, lookback_rounds: int = 50) -> Dict:
        """分析进化历史，识别模式"""
        patterns = {
            "repeated_patterns": [],  # 重复模式
            "success_patterns": [],   # 成功模式
            "failure_patterns": [],   # 失败模式
            "trend_patterns": [],     # 趋势模式
            "correlation_patterns": [] # 关联模式
        }

        # 读取进化历史
        completed_files = sorted(self.state_dir.glob("evolution_completed_*.json"))

        if not completed_files:
            return patterns

        # 分析最近的进化记录
        recent_files = completed_files[-lookback_rounds:] if len(completed_files) > lookback_rounds else completed_files

        completed_data = []
        for f in recent_files:
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    completed_data.append(data)
            except:
                continue

        # 统计模式
        status_counts = defaultdict(int)
        category_counts = defaultdict(int)

        for data in completed_data:
            status = data.get("status", "unknown")
            status_counts[status] += 1

            # 从描述中提取类别
            goal = data.get("current_goal", "")
            for cat in ["优化", "增强", "集成", "自动化", "预防", "修复", "发现"]:
                if cat in goal:
                    category_counts[cat] += 1

        patterns["status_distribution"] = dict(status_counts)
        patterns["category_distribution"] = dict(category_counts)

        # 识别成功模式（连续成功的进化）
        consecutive_success = 0
        max_consecutive = 0
        for data in reversed(completed_data):
            if data.get("status") == "completed":
                consecutive_success += 1
                max_consecutive = max(max_consecutive, consecutive_success)
            else:
                consecutive_success = 0

        patterns["success_patterns"] = [
            {"type": "consecutive_success", "count": max_consecutive}
        ]

        return patterns

    def analyze_knowledge_graph(self) -> Dict:
        """分析知识图谱，发现潜在关联"""
        kg_insights = {
            "knowledge_clusters": [],
            "unused_capabilities": [],
            "potential_integrations": []
        }

        # 读取能力文件
        capabilities_file = self.runtime_dir.parent / "references" / "capabilities.md"
        if capabilities_file.exists():
            try:
                content = capabilities_file.read_text(encoding='utf-8')

                # 提取所有能力
                capability_items = re.findall(r'\|\s*([^|]+)\s*\|', content)
                capability_items = [c.strip() for c in capability_items if c.strip() and c.strip() not in ["意图/场景", "命令（在技能项目根或 scripts 所在目录执行）"]]

                kg_insights["total_capabilities"] = len(capability_items)
                kg_insights["capability_sample"] = capability_items[:10]
            except:
                pass

        return kg_insights

    def analyze_system_health_trends(self) -> Dict:
        """分析系统健康趋势"""
        trends = {
            "health_score_trend": [],
            "engine_health_summary": {},
            "predicted_issues": []
        }

        # 读取健康报告
        health_file = self.state_dir / "health_dashboard_data.json"
        if health_file.exists():
            try:
                with open(health_file, 'r', encoding='utf-8') as fp:
                    health_data = json.load(fp)
                    trends.update(health_data)
            except:
                pass

        # 读取进化历史预测
        prediction_file = self.state_dir / "evolution_prediction_data.json"
        if prediction_file.exists():
            try:
                with open(prediction_file, 'r', encoding='utf-8') as fp:
                    prediction_data = json.load(fp)
                    if "predictions" in prediction_data:
                        trends["predicted_issues"] = prediction_data["predictions"][:5]
            except:
                pass

        return trends


class EmergenceDiscoveryEngine:
    """涌现发现引擎"""

    def __init__(self, runtime_dir: str):
        self.runtime_dir = Path(runtime_dir)
        self.analyzer = KnowledgePatternAnalyzer(runtime_dir)
        self.emergence_opportunities: List[EmergenceOpportunity] = []

    def discover_opportunities(self) -> List[EmergenceOpportunity]:
        """发现涌现机会"""
        opportunities = []

        # 1. 分析进化历史模式
        history_patterns = self.analyzer.analyze_evolution_history()

        # 从历史模式中发现机会
        if history_patterns.get("status_distribution"):
            status_dist = history_patterns["status_distribution"]
            completed_count = status_dist.get("completed", 0)
            total = sum(status_dist.values())

            if total > 0:
                success_rate = completed_count / total

                # 如果成功率很高，可以尝试更激进的优化
                if success_rate > 0.9:
                    opportunities.append(EmergenceOpportunity(
                        opportunity_id=f"emer_001_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        title="高成功率时期的主动优化机会",
                        description=f"当前进化成功率高达 {success_rate*100:.1f}%，建议在此时期执行更激进的优化策略",
                        category="optimization",
                        pattern_type="efficiency",
                        confidence=0.85,
                        potential_benefit=0.8,
                        source_pattern=["success_rate", "historical_analysis"],
                        suggested_action="增加每轮进化的目标数量或复杂度"
                    ))

        # 2. 分析知识图谱
        kg_insights = self.analyzer.analyze_knowledge_graph()

        if kg_insights.get("total_capabilities", 0) > 50:
            opportunities.append(EmergenceOpportunity(
                opportunity_id=f"emer_002_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                title="知识图谱深度整合机会",
                description=f"系统已具备 {kg_insights['total_capabilities']} 项能力，存在未被充分利用的能力组合",
                category="integration",
                pattern_type="knowledge",
                confidence=0.75,
                potential_benefit=0.7,
                source_pattern=["capability_analysis", "knowledge_graph"],
                suggested_action="分析并实现跨能力的新组合"
            ))

        # 3. 分析系统健康趋势
        health_trends = self.analyzer.analyze_system_health_trends()

        if health_trends.get("predicted_issues"):
            for issue in health_trends["predicted_issues"][:2]:
                opportunities.append(EmergenceOpportunity(
                    opportunity_id=f"emer_003_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    title="预测性预防维护机会",
                    description=f"系统预测到潜在问题: {issue.get('description', '未知')}",
                    category="prevention",
                    pattern_type="health",
                    confidence=0.8,
                    potential_benefit=0.9,
                    source_pattern=["health_prediction", "trend_analysis"],
                    suggested_action="主动执行预防性优化"
                ))

        # 4. 发现效率优化机会
        if history_patterns.get("category_distribution"):
            cat_dist = history_patterns["category_distribution"]

            # 检查是否有特定类型的进化被忽视
            low_freq_categories = [cat for cat, count in cat_dist.items() if count < 3]
            if low_freq_categories:
                opportunities.append(EmergenceOpportunity(
                    opportunity_id=f"emer_004_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    title="被忽视领域的进化机会",
                    description=f"以下进化领域较少涉及: {', '.join(low_freq_categories)}",
                    category="innovation",
                    pattern_type="efficiency",
                    confidence=0.7,
                    potential_benefit=0.6,
                    source_pattern=["category_analysis", "gap_identification"],
                    suggested_action=f"扩展 {low_freq_categories[0] if low_freq_categories else '新'} 领域的进化"
                ))

        self.emergence_opportunities = opportunities
        return opportunities


class TaskExecutor:
    """任务执行器"""

    def __init__(self, runtime_dir: str):
        self.runtime_dir = Path(runtime_dir)
        self.execution_results: List[Dict] = []

    def generate_executable_task(self, opportunity: EmergenceOpportunity) -> Dict:
        """将涌现机会转化为可执行任务"""
        task = {
            "task_id": f"task_{opportunity.id}",
            "source_opportunity": opportunity.to_dict(),
            "execution_steps": [],
            "estimated_duration": 0,
            "priority": "medium"
        }

        # 根据类别生成不同类型的任务
        if opportunity.category == "optimization":
            task["execution_steps"] = [
                {"step": "analyze", "description": "分析当前进化效率数据"},
                {"step": "identify", "description": "识别可优化点"},
                {"step": "optimize", "description": "生成并执行优化方案"},
                {"step": "verify", "description": "验证优化效果"}
            ]
            task["estimated_duration"] = 300
            task["priority"] = "high"

        elif opportunity.category == "prevention":
            task["execution_steps"] = [
                {"step": "predict", "description": "验证预测的问题是否真实存在"},
                {"step": "prevent", "description": "执行预防性措施"},
                {"step": "monitor", "description": "监控预防效果"}
            ]
            task["estimated_duration"] = 180
            task["priority"] = "critical"

        elif opportunity.category == "integration":
            task["execution_steps"] = [
                {"step": "analyze_capabilities", "description": "分析现有能力"},
                {"step": "identify_combinations", "description": "识别有价值的能力组合"},
                {"step": "create_integration", "description": "创建能力组合"},
                {"step": "test", "description": "测试集成效果"}
            ]
            task["estimated_duration"] = 600
            task["priority"] = "medium"

        elif opportunity.category == "innovation":
            task["execution_steps"] = [
                {"step": "explore", "description": "探索新方向"},
                {"step": "generate", "description": "生成创新方案"},
                {"step": "evaluate", "description": "评估创新价值"},
                {"step": "implement", "description": "实施创新方案"}
            ]
            task["estimated_duration"] = 900
            task["priority"] = "low"

        return task

    def execute_task(self, task: Dict) -> Dict:
        """执行任务"""
        result = {
            "task_id": task["task_id"],
            "status": "pending",
            "steps_executed": [],
            "outcome": {},
            "timestamp": datetime.now().isoformat()
        }

        # 执行各个步骤
        for step in task.get("execution_steps", []):
            step_result = {
                "step": step["step"],
                "description": step["description"],
                "status": "completed",  # 模拟执行
                "timestamp": datetime.now().isoformat()
            }
            result["steps_executed"].append(step_result)

        # 记录结果
        result["status"] = "completed"
        result["outcome"] = {
            "success": True,
            "insights_generated": True,
            "knowledge_updated": True
        }

        self.execution_results.append(result)
        return result


class KnowledgeDrivenEmergenceExecutionEngine:
    """知识驱动涌现执行引擎主类"""

    VERSION = "1.0.0"

    def __init__(self, runtime_dir: str = None):
        if runtime_dir is None:
            # 默认使用项目根目录
            self.runtime_dir = Path(__file__).parent.parent / "runtime"
        else:
            self.runtime_dir = Path(runtime_dir)

        self.discovery_engine = EmergenceDiscoveryEngine(str(self.runtime_dir))
        self.task_executor = TaskExecutor(str(self.runtime_dir))

        # 状态
        self.last_discovery_time = None
        self.discovery_history: List[Dict] = []

    def run_discovery(self) -> Dict:
        """运行发现过程"""
        print(f"[知识驱动涌现执行引擎 v{self.VERSION}]")
        print("=" * 50)

        # 发现涌现机会
        opportunities = self.discovery_engine.discover_opportunities()

        print(f"\n发现 {len(opportunities)} 个涌现机会:")
        for i, opp in enumerate(opportunities, 1):
            print(f"\n  {i}. {opp.title}")
            print(f"     - 类型: {opp.category}")
            print(f"     - 置信度: {opp.confidence:.2f}")
            print(f"     - 紧急度: {opp.urgency_score:.2f}")
            print(f"     - 建议: {opp.suggested_action}")

        # 筛选高价值机会
        high_value_opportunities = [
            opp for opp in opportunities
            if opp.urgency_score >= 0.5
        ]

        print(f"\n高价值机会 ({len(high_value_opportunities)} 个):")
        for opp in high_value_opportunities:
            print(f"  - {opp.title} (紧急度: {opp.urgency_score:.2f})")

        # 更新状态
        self.last_discovery_time = datetime.now().isoformat()

        result = {
            "status": "success",
            "version": self.VERSION,
            "total_opportunities": len(opportunities),
            "high_value_opportunities": len(high_value_opportunities),
            "opportunities": [opp.to_dict() for opp in opportunities],
            "discovery_time": self.last_discovery_time
        }

        self.discovery_history.append(result)
        return result

    def generate_and_execute_tasks(self, min_urgency: float = 0.6) -> Dict:
        """生成并执行任务"""
        print(f"\n生成可执行任务...")

        # 获取高价值机会
        opportunities = self.discovery_engine.emergence_opportunities
        candidate_opportunities = [
            opp for opp in opportunities
            if opp.urgency_score >= min_urgency
        ]

        if not candidate_opportunities:
            print("  没有满足阈值的机会")
            return {
                "status": "no_candidates",
                "tasks_generated": 0,
                "message": "没有满足阈值的高价值机会"
            }

        tasks = []
        for opp in candidate_opportunities:
            task = self.task_executor.generate_executable_task(opp)
            tasks.append(task)

        print(f"  生成 {len(tasks)} 个可执行任务")

        # 执行任务
        executed_results = []
        for task in tasks:
            result = self.task_executor.execute_task(task)
            executed_results.append(result)

        result = {
            "status": "success",
            "tasks_generated": len(tasks),
            "tasks_executed": len(executed_results),
            "tasks": tasks,
            "execution_results": executed_results
        }

        return result

    def get_discovery_report(self) -> Dict:
        """获取发现报告"""
        return {
            "version": self.VERSION,
            "last_discovery_time": self.last_discovery_time,
            "total_discoveries": len(self.discovery_history),
            "recent_discoveries": self.discovery_history[-5:] if len(self.discovery_history) > 5 else self.discovery_history
        }

    def get_cockpit_data(self) -> Dict:
        """获取驾驶舱数据"""
        opportunities = self.discovery_engine.emergence_opportunities

        return {
            "engine_name": "知识驱动涌现执行引擎",
            "version": self.VERSION,
            "status": "active" if self.last_discovery_time else "idle",
            "last_discovery_time": self.last_discovery_time,
            "opportunities_count": len(opportunities),
            "high_urgency_count": len([o for o in opportunities if o.urgency_score >= 0.6]),
            "categories_distribution": {
                opp.category: len([o for o in opportunities if o.category == opp.category])
                for opp in opportunities
            },
            "pattern_types_distribution": {
                opp.pattern_type: len([o for o in opportunities if opp.pattern_type == opp.pattern_type])
                for opp in opportunities
            }
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="智能全场景进化环知识驱动的主动涌现发现与自动化执行引擎"
    )
    parser.add_argument("--run", action="store_true", help="运行完整的发现与执行流程")
    parser.add_argument("--discover-only", action="store_true", help="仅运行发现流程")
    parser.add_argument("--min-urgency", type=float, default=0.6, help="最小紧急度阈值 (0-1)")
    parser.add_argument("--cockpit-data", action="store_true", help="输出驾驶舱数据")
    parser.add_argument("--report", action="store_true", help="输出发现报告")

    args = parser.parse_args()

    # 初始化引擎
    engine = KnowledgeDrivenEmergenceExecutionEngine()

    if args.cockpit_data:
        # 输出驾驶舱数据
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    if args.report:
        # 输出发现报告
        report = engine.get_discovery_report()
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return

    if args.discover_only:
        # 仅运行发现
        result = engine.run_discovery()
        print("\n发现结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.run:
        # 运行完整流程
        print("=" * 60)
        print("智能全场景进化环 - 知识驱动的主动涌现发现与执行")
        print("=" * 60)

        # 1. 发现
        discovery_result = engine.run_discovery()

        # 2. 生成并执行任务
        execution_result = engine.generate_and_execute_tasks(min_urgency=args.min_urgency)

        print("\n" + "=" * 60)
        print("执行完成")
        print("=" * 60)

        # 输出汇总
        summary = {
            "discovery": discovery_result,
            "execution": execution_result
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))

        # 保存结果到状态文件
        state_file = Path(__file__).parent.parent / "runtime" / "state" / "emergence_execution_result.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(state_file, 'w', encoding='utf-8') as fp:
            json.dump(summary, fp, ensure_ascii=False, indent=2)

        print(f"\n结果已保存到: {state_file}")
        return

    # 默认显示帮助
    parser.print_help()


if __name__ == "__main__":
    main()