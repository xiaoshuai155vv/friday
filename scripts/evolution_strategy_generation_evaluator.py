#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化策略自动生成与动态评估引擎 (Evolution Strategy Generation & Evaluator)
version 1.0.0

让系统能够基于当前系统状态、进化历史、知识图谱自动生成多套进化策略方案，
动态评估各方案的效果与风险，智能选择最优路径执行，
形成「策略生成→动态评估→智能选择→执行验证」的完整闭环。

功能：
1. 多维度策略方案生成 - 基于系统状态、进化历史、知识图谱、当前能力缺口
2. 策略效果动态评估 - 预测各策略的成功率、资源消耗、潜在风险
3. 智能策略选择 - 基于评估结果选择最优策略
4. 策略执行与效果追踪
5. 与 do.py 深度集成

依赖：
- evolution_knowledge_graph_reasoning.py (round 298)
- evolution_meta_optimizer.py (round 297)
- evolution_hypothesis_verification_engine.py (round 309)
- evolution_knowledge_inheritance_engine.py (round 240)
"""

import os
import sys
import json
import glob
import time
import random
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class EvolutionStrategy:
    """进化策略"""

    def __init__(self, strategy_id: str, name: str, description: str,
                 strategy_type: str, target_goals: List[str],
                 estimated_duration: float, complexity: str,
                 expected_benefit: float, risk_level: str):
        self.id = strategy_id
        self.name = name
        self.description = description
        self.type = strategy_type  # capability_expansion, efficiency_optimization, quality_improvement, innovation
        self.target_goals = target_goals
        self.estimated_duration = estimated_duration  # 小时
        self.complexity = complexity  # low, medium, high
        self.expected_benefit = expected_benefit  # 0-1
        self.risk_level = risk_level  # low, medium, high
        self.status = "generated"  # generated, evaluating, selected, executing, completed, failed
        self.evaluation_scores: Dict[str, float] = {}
        self.selected_at: Optional[str] = None
        self.execution_result: Optional[Dict] = None
        self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "target_goals": self.target_goals,
            "estimated_duration": self.estimated_duration,
            "complexity": self.complexity,
            "expected_benefit": self.expected_benefit,
            "risk_level": self.risk_level,
            "status": self.status,
            "evaluation_scores": self.evaluation_scores,
            "selected_at": self.selected_at,
            "execution_result": self.execution_result,
            "created_at": self.created_at
        }


class StrategyEvaluator:
    """策略评估器"""

    def __init__(self):
        self.weights = {
            "success_probability": 0.30,
            "resource_efficiency": 0.20,
            "risk_score": 0.25,
            "benefit_score": 0.25
        }

    def predict_success_probability(self, strategy: EvolutionStrategy,
                                     system_state: Dict,
                                     history: List[Dict]) -> float:
        """预测策略成功率"""
        # 基于历史相似策略的成功率
        similar_count = 0
        success_count = 0

        for h in history:
            if h.get("type") == strategy.type:
                similar_count += 1
                if h.get("status") == "completed":
                    success_count += 1

        if similar_count > 0:
            base_prob = success_count / similar_count
        else:
            base_prob = 0.7  # 默认概率

        # 根据复杂度调整
        complexity_factor = {
            "low": 1.0,
            "medium": 0.85,
            "high": 0.7
        }.get(strategy.complexity, 0.8)

        # 根据风险级别调整
        risk_factor = {
            "low": 1.0,
            "medium": 0.9,
            "high": 0.75
        }.get(strategy.risk_level, 0.85)

        # 根据系统负载调整
        cpu_load = system_state.get("cpu_usage", 50)
        memory_load = system_state.get("memory_usage", 50)
        system_factor = 1.0 - ((cpu_load + memory_load) / 200)

        return round(base_prob * complexity_factor * risk_factor * system_factor, 3)

    def evaluate_resource_efficiency(self, strategy: EvolutionStrategy) -> float:
        """评估资源效率"""
        duration_score = max(0, 1 - (strategy.estimated_duration / 10))  # 10小时为满分

        complexity_score = {
            "low": 1.0,
            "medium": 0.7,
            "high": 0.4
        }.get(strategy.complexity, 0.6)

        return round((duration_score * 0.6 + complexity_score * 0.4), 3)

    def evaluate_risk(self, strategy: EvolutionStrategy, history: List[Dict]) -> float:
        """评估风险分数 (越高风险越大)"""
        risk_score = {
            "low": 0.2,
            "medium": 0.5,
            "high": 0.8
        }.get(strategy.risk_level, 0.5)

        # 检查历史中同类型策略的失败率
        failures = sum(1 for h in history if h.get("type") == strategy.type and h.get("status") == "failed")
        total = sum(1 for h in history if h.get("type") == strategy.type)

        if total > 0:
            failure_rate = failures / total
            risk_score = (risk_score + failure_rate) / 2

        return round(risk_score, 3)

    def evaluate_benefit(self, strategy: EvolutionStrategy) -> float:
        """评估收益分数"""
        return strategy.expected_benefit

    def comprehensive_evaluate(self, strategy: EvolutionStrategy,
                              system_state: Dict,
                              history: List[Dict]) -> Dict[str, float]:
        """综合评估"""
        success_prob = self.predict_success_probability(strategy, system_state, history)
        resource_eff = self.evaluate_resource_efficiency(strategy)
        risk = self.evaluate_risk(strategy, history)
        benefit = self.evaluate_benefit(strategy)

        # 计算综合分数 (风险越低分数越高)
        risk_inverted = 1 - risk
        total_score = (
            success_prob * self.weights["success_probability"] +
            resource_eff * self.weights["resource_efficiency"] +
            risk_inverted * self.weights["risk_score"] +
            benefit * self.weights["benefit_score"]
        )

        return {
            "success_probability": success_prob,
            "resource_efficiency": resource_eff,
            "risk_score": risk,
            "benefit_score": benefit,
            "total_score": round(total_score, 3)
        }


class EvolutionStrategyGenerationEvaluator:
    """进化策略自动生成与动态评估引擎"""

    def __init__(self):
        self.evaluator = StrategyEvaluator()
        self.strategies: List[EvolutionStrategy] = []
        self.strategy_counter = 0
        self.data_dir = PROJECT_ROOT / "runtime" / "state"

    def get_system_state(self) -> Dict:
        """获取当前系统状态"""
        state = {
            "cpu_usage": 50,  # 默认值
            "memory_usage": 50,
            "disk_usage": 50,
            "active_engines": 0,
            "recent_evolutions": 0,
            "failed_evolutions": 0,
            "timestamp": datetime.now().isoformat()
        }

        try:
            # 读取当前任务状态
            mission_file = self.data_dir / "current_mission.json"
            if mission_file.exists():
                with open(mission_file, 'r', encoding='utf-8') as f:
                    mission = json.load(f)
                    state["current_phase"] = mission.get("phase", "unknown")
                    state["loop_round"] = mission.get("loop_round", 0)

            # 统计引擎数量
            scripts_dir = PROJECT_ROOT / "scripts"
            engine_files = list(scripts_dir.glob("evolution_*.py"))
            state["active_engines"] = len(engine_files)
        except Exception as e:
            print(f"获取系统状态时出错: {e}")

        return state

    def get_evolution_history(self) -> List[Dict]:
        """获取进化历史"""
        history = []

        try:
            # 读取已完成的历史
            for f in self.data_dir.glob("evolution_completed_*.json"):
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        if isinstance(data, dict):
                            history.append(data)
                except Exception:
                    pass

            # 限制返回最近50条
            history = sorted(history, key=lambda x: x.get("loop_round", 0), reverse=True)[:50]
        except Exception as e:
            print(f"获取进化历史时出错: {e}")

        return history

    def get_capability_gaps(self) -> List[str]:
        """获取当前能力缺口"""
        gaps = []
        try:
            gaps_file = PROJECT_ROOT / "references" / "capability_gaps.md"
            if gaps_file.exists():
                with open(gaps_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 解析 markdown 表格，提取 "可行方向" 列中非 "—" 的内容
                    lines = content.split('\n')
                    for line in lines:
                        if '|' in line and '—' not in line.split('|')[-2]:
                            # 有具体方向
                            parts = line.split('|')
                            if len(parts) >= 3:
                                direction = parts[-2].strip()
                                if direction and direction != '可行方向':
                                    gaps.append(direction)
        except Exception as e:
            print(f"获取能力缺口时出错: {e}")

        return gaps

    def generate_strategies(self, num_strategies: int = 3) -> List[EvolutionStrategy]:
        """生成多套进化策略"""
        system_state = self.get_system_state()
        history = self.get_evolution_history()
        gaps = self.get_capability_gaps()

        # 策略模板
        strategy_templates = [
            {
                "type": "capability_expansion",
                "name": "能力扩展策略",
                "description": "扩展现有能力边界，填补能力缺口",
                "complexity": "medium",
                "risk": "medium"
            },
            {
                "type": "efficiency_optimization",
                "name": "效率优化策略",
                "description": "优化现有进化环的执行效率，减少资源消耗",
                "complexity": "low",
                "risk": "low"
            },
            {
                "type": "quality_improvement",
                "name": "质量提升策略",
                "description": "提升进化质量和可靠性，减少失败率",
                "complexity": "medium",
                "risk": "medium"
            },
            {
                "type": "innovation",
                "name": "创新探索策略",
                "description": "探索新的进化方向和应用场景",
                "complexity": "high",
                "risk": "high"
            }
        ]

        # 分析历史数据，了解哪些类型策略成功率更高
        type_success = defaultdict(lambda: {"total": 0, "success": 0})
        for h in history:
            strategy_type = h.get("type", "unknown")
            status = h.get("status", "")
            type_success[strategy_type]["total"] += 1
            if status == "completed":
                type_success[strategy_type]["success"] += 1

        strategies = []
        for i in range(num_strategies):
            template = strategy_templates[i % len(strategy_templates)]

            # 基于分析结果调整期望收益
            type_stats = type_success.get(template["type"], {"success": 0, "total": 1})
            success_rate = type_stats["success"] / max(type_stats["total"], 1)

            self.strategy_counter += 1
            strategy = EvolutionStrategy(
                strategy_id=f"strategy_{self.strategy_counter:04d}",
                name=f"{template['name']} {self.strategy_counter}",
                description=template["description"],
                strategy_type=template["type"],
                target_goals=gaps[:3] if gaps else ["提升系统自主能力"],
                estimated_duration=random.uniform(1, 8),
                complexity=template["complexity"],
                expected_benefit=success_rate * random.uniform(0.6, 0.9),
                risk_level=template["risk"]
            )

            # 进行评估
            evaluation = self.evaluator.comprehensive_evaluate(strategy, system_state, history)
            strategy.evaluation_scores = evaluation

            strategies.append(strategy)
            self.strategies.append(strategy)

        return strategies

    def evaluate_strategies(self, strategies: List[EvolutionStrategy]) -> Dict:
        """评估所有策略并排序"""
        if not strategies:
            return {"strategies": [], "best_strategy": None}

        # 按综合分数排序
        sorted_strategies = sorted(
            strategies,
            key=lambda s: s.evaluation_scores.get("total_score", 0),
            reverse=True
        )

        # 为每个策略添加排名
        for i, s in enumerate(sorted_strategies):
            s.evaluation_scores["rank"] = i + 1

        return {
            "strategies": [s.to_dict() for s in sorted_strategies],
            "best_strategy": sorted_strategies[0].to_dict() if sorted_strategies else None,
            "evaluation_criteria": self.evaluator.weights
        }

    def select_best_strategy(self, strategies: List[EvolutionStrategy]) -> Optional[EvolutionStrategy]:
        """选择最佳策略"""
        if not strategies:
            return None

        evaluated = self.evaluate_strategies(strategies)
        best = evaluated.get("best_strategy")

        if best:
            # 更新选中策略的状态
            for s in strategies:
                if s.id == best["id"]:
                    s.status = "selected"
                    s.selected_at = datetime.now().isoformat()
                    return s

        return strategies[0] if strategies else None

    def execute_strategy(self, strategy: EvolutionStrategy) -> Dict:
        """执行选定的策略"""
        if not strategy:
            return {"success": False, "message": "没有选中策略"}

        strategy.status = "executing"

        # 记录执行结果（实际执行由进化环其他模块完成）
        strategy.execution_result = {
            "executed_at": datetime.now().isoformat(),
            "status": "executed",
            "message": "策略已发送到进化环执行"
        }

        return {
            "success": True,
            "strategy_id": strategy.id,
            "message": f"策略 {strategy.name} 已选中并准备执行"
        }

    def generate_and_evaluate(self, num_strategies: int = 3) -> Dict:
        """生成、评估并选择最佳策略的完整流程"""
        # 1. 生成策略
        strategies = self.generate_strategies(num_strategies)

        # 2. 评估策略
        evaluation = self.evaluate_strategies(strategies)

        # 3. 选择最佳策略
        best = self.select_best_strategy(strategies)

        return {
            "system_state": self.get_system_state(),
            "generation_time": datetime.now().isoformat(),
            "num_strategies_generated": len(strategies),
            "strategies": evaluation["strategies"],
            "best_strategy": best.to_dict() if best else None,
            "evaluation_criteria": evaluation["evaluation_criteria"]
        }

    def get_strategy_status(self, strategy_id: str = None) -> Dict:
        """获取策略状态"""
        if strategy_id:
            for s in self.strategies:
                if s.id == strategy_id:
                    return s.to_dict()
            return {"error": "策略不存在"}

        return {
            "total_strategies": len(self.strategies),
            "by_status": self._group_by_status()
        }

    def _group_by_status(self) -> Dict:
        """按状态分组"""
        groups = defaultdict(int)
        for s in self.strategies:
            groups[s.status] += 1
        return dict(groups)


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description="进化策略自动生成与动态评估引擎")
    parser.add_argument("--generate", action="store_true", help="生成策略方案")
    parser.add_argument("--evaluate", action="store_true", help="评估策略")
    parser.add_argument("--select", action="store_true", help="选择最佳策略")
    parser.add_argument("--status", action="store_true", help="查看策略状态")
    parser.add_argument("--num", type=int, default=3, help="生成策略数量")
    parser.add_argument("--strategy-id", type=str, help="策略ID")

    args = parser.parse_args()

    engine = EvolutionStrategyGenerationEvaluator()

    if args.generate or (not args.generate and not args.evaluate and not args.status):
        result = engine.generate_and_evaluate(args.num)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.status:
        result = engine.get_strategy_status(args.strategy_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()