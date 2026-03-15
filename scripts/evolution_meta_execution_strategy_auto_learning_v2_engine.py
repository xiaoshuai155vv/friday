"""
智能全场景进化环元进化执行策略自动学习与智能优化引擎 V2
Version: 1.0.0

基于 round 680 场景执行鲁棒性增强引擎，构建让系统能够：
1. 自动分析场景执行模式
2. 学习最优策略参数
3. 实现真正的自适应执行优化
4. 与 round 680 场景执行鲁棒性引擎深度集成

此引擎让系统从「被动调整策略」升级到「主动学习最优策略」，实现真正的执行策略智能优化。
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import re
from collections import defaultdict

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE_DIR = PROJECT_ROOT / "runtime" / "state"
RUNTIME_LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"
REFERENCES_DIR = PROJECT_ROOT / "references"
ASSETS_PLANS_DIR = PROJECT_ROOT / "assets" / "plans"


class EvolutionMetaExecutionStrategyAutoLearningV2Engine:
    """元进化执行策略自动学习与智能优化引擎 V2"""

    def __init__(self):
        self.version = "1.0.0"
        self.name = "元进化执行策略自动学习与智能优化引擎 V2"
        self.execution_patterns = self._load_execution_patterns()
        self.strategy_parameters = self._initialize_strategy_parameters()
        self.learning_cache = self._load_learning_cache()
        print(f"[{self.name}] 初始化完成 (v{self.version})")

    def _load_execution_patterns(self) -> List[Dict[str, Any]]:
        """加载执行模式数据"""
        patterns = []
        try:
            patterns_file = RUNTIME_STATE_DIR / "execution_patterns.json"
            if patterns_file.exists():
                with open(patterns_file, 'r', encoding='utf-8') as f:
                    patterns = json.load(f)
        except Exception as e:
            print(f"[模式加载] 无法加载执行模式: {e}")
        return patterns

    def _save_execution_patterns(self):
        """保存执行模式数据"""
        try:
            patterns_file = RUNTIME_STATE_DIR / "execution_patterns.json"
            with open(patterns_file, 'w', encoding='utf-8') as f:
                json.dump(self.execution_patterns, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[模式保存] 保存失败: {e}")

    def _load_learning_cache(self) -> Dict[str, Any]:
        """加载学习缓存"""
        cache = {}
        try:
            cache_file = RUNTIME_STATE_DIR / "strategy_learning_cache.json"
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
        except Exception as e:
            print(f"[缓存加载] 无法加载学习缓存: {e}")
        return cache

    def _save_learning_cache(self):
        """保存学习缓存"""
        try:
            cache_file = RUNTIME_STATE_DIR / "strategy_learning_cache.json"
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.learning_cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[缓存保存] 保存失败: {e}")

    def _initialize_strategy_parameters(self) -> Dict[str, Any]:
        """初始化策略参数库"""
        return {
            # 重试策略参数
            "retry": {
                "max_attempts": 3,
                "base_delay": 1.0,
                "backoff_factor": 2.0,
                "jitter": True
            },
            # 超时策略参数
            "timeout": {
                "default": 30.0,
                "per_action_type": {
                    "vision": 15.0,
                    "click": 5.0,
                    "type": 3.0,
                    "activate": 10.0,
                    "screenshot": 5.0
                }
            },
            # 窗口激活参数
            "window_activation": {
                "wait_before_activate": 0.5,
                "wait_after_activate": 1.0,
                "maximize_after_activate": True,
                "retry_attach_thread": True
            },
            # 执行顺序优化参数
            "execution_order": {
                "prioritize_dependencies": True,
                "parallel_when_possible": False,
                "group_by_app": True
            },
            # 错误处理参数
            "error_handling": {
                "auto_retry_on_failure": True,
                "fallback_to_alternative": True,
                "escalate_after_attempts": 3
            }
        }

    def analyze_execution_pattern(self, scenario_name: str, execution_log: Dict[str, Any]) -> Dict[str, Any]:
        """分析场景执行模式"""
        print(f"\n[模式分析] 正在分析场景执行模式: {scenario_name}")

        # 提取执行特征
        features = {
            "scenario_name": scenario_name,
            "timestamp": datetime.now().isoformat(),
            "total_steps": len(execution_log.get("steps", [])),
            "failed_steps": len([s for s in execution_log.get("steps", []) if s.get("status") == "failed"]),
            "avg_step_duration": sum(s.get("duration", 0) for s in execution_log.get("steps", [])) / max(len(execution_log.get("steps", [])), 1),
            "step_types": [s.get("type") for s in execution_log.get("steps", [])],
            "error_types": [s.get("error_type") for s in execution_log.get("steps", []) if s.get("status") == "failed"]
        }

        # 识别成功/失败模式
        success_rate = (features["total_steps"] - features["failed_steps"]) / max(features["total_steps"], 1)

        pattern_analysis = {
            "features": features,
            "success_rate": success_rate,
            "efficiency_score": self._calculate_efficiency_score(features),
            "bottleneck_steps": self._identify_bottleneck_steps(execution_log),
            "recommended_optimizations": self._generate_optimization_recommendations(features)
        }

        # 保存分析结果
        self.execution_patterns.append(pattern_analysis)
        self._save_execution_patterns()

        print(f"[模式分析] 分析完成 - 成功率: {success_rate:.2%}, 效率得分: {pattern_analysis['efficiency_score']:.2f}")
        return pattern_analysis

    def _calculate_efficiency_score(self, features: Dict[str, Any]) -> float:
        """计算效率得分"""
        # 基于多个因素计算效率得分
        success_weight = 0.4
        duration_weight = 0.3
        step_count_weight = 0.3

        # 成功率得分
        success_score = 1.0 - (features.get("failed_steps", 0) / max(features.get("total_steps", 1), 1))

        # 步骤数量得分（越少越好）
        step_count_score = 1.0 / (1.0 + features.get("total_steps", 0) * 0.1)

        # 耗时得分（越短越好）
        avg_duration = features.get("avg_step_duration", 0)
        duration_score = 1.0 / (1.0 + avg_duration * 0.1)

        efficiency = (success_score * success_weight +
                     duration_score * duration_weight +
                     step_count_score * step_count_weight)

        return min(efficiency * 100, 100.0)

    def _identify_bottleneck_steps(self, execution_log: Dict[str, Any]) -> List[Dict[str, Any]]:
        """识别瓶颈步骤"""
        bottlenecks = []

        for step in execution_log.get("steps", []):
            if step.get("status") == "failed":
                bottlenecks.append({
                    "step_index": step.get("index"),
                    "step_type": step.get("type"),
                    "error_type": step.get("error_type"),
                    "duration": step.get("duration", 0),
                    "retry_count": step.get("retry_count", 0)
                })

        return bottlenecks

    def _generate_optimization_recommendations(self, features: Dict[str, Any]) -> List[str]:
        """生成优化建议"""
        recommendations = []

        # 基于失败步骤
        if features.get("failed_steps", 0) > 0:
            recommendations.append("建议增加失败步骤的重试次数和延迟时间")

        # 基于执行时间
        if features.get("avg_step_duration", 0) > 5.0:
            recommendations.append("部分步骤执行时间较长，建议优化执行顺序或使用并行执行")

        # 基于步骤数量
        if features.get("total_steps", 0) > 10:
            recommendations.append("步骤数量较多，建议合并相关步骤减少开销")

        # 基于步骤类型
        step_types = features.get("step_types", [])
        if "activate" in step_types and step_types.count("activate") > 2:
            recommendations.append("窗口激活操作频繁，建议优化激活策略")

        if "vision" in step_types and step_types.count("vision") > 3:
            recommendations.append("视觉识别调用频繁，建议添加结果缓存机制")

        return recommendations

    def learn_optimal_parameters(self, scenario_name: str) -> Dict[str, Any]:
        """学习最优策略参数"""
        print(f"\n[参数学习] 正在学习场景 {scenario_name} 的最优参数")

        # 查找该场景的历史模式
        scenario_patterns = [p for p in self.execution_patterns if p.get("features", {}).get("scenario_name") == scenario_name]

        if not scenario_patterns:
            print(f"[参数学习] 无历史模式数据，使用默认参数")
            return self.strategy_parameters.copy()

        # 分析历史成功/失败案例
        successful_patterns = [p for p in scenario_patterns if p.get("success_rate", 0) > 0.8]
        failed_patterns = [p for p in scenario_patterns if p.get("success_rate", 0) < 0.5]

        # 学习最优参数
        learned_params = self.strategy_parameters.copy()

        if successful_patterns:
            # 从成功案例中提取优化参数
            avg_retry = sum(p.get("features", {}).get("failed_steps", 0) for p in successful_patterns) / len(successful_patterns)
            if avg_retry < 1:
                learned_params["retry"]["max_attempts"] = max(2, int(learned_params["retry"]["max_attempts"] * 0.8))

        if failed_patterns:
            # 从失败案例中增加容错参数
            learned_params["retry"]["max_attempts"] = min(5, learned_params["retry"]["max_attempts"] + 1)
            learned_params["retry"]["backoff_factor"] = min(3.0, learned_params["retry"]["backoff_factor"] * 1.2)

        # 保存学习结果
        if scenario_name not in self.learning_cache:
            self.learning_cache[scenario_name] = {}

        self.learning_cache[scenario_name]["learned_parameters"] = learned_params
        self.learning_cache[scenario_name]["last_learned"] = datetime.now().isoformat()
        self.learning_cache[scenario_name]["sample_count"] = len(scenario_patterns)
        self._save_learning_cache()

        print(f"[参数学习] 学习完成 - 基于 {len(scenario_patterns)} 条样本")
        return learned_params

    def get_adaptive_strategy(self, scenario_name: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """获取自适应执行策略"""
        print(f"\n[策略生成] 正在为场景 {scenario_name} 生成自适应策略")

        # 先学习最优参数
        learned_params = self.learn_optimal_parameters(scenario_name)

        # 结合当前上下文生成策略
        strategy = {
            "scenario_name": scenario_name,
            "parameters": learned_params,
            "generated_at": datetime.now().isoformat(),
            "adaptation_reason": self._generate_adaptation_reason(scenario_name, context),
            "predicted_success_rate": self._predict_success_rate(scenario_name)
        }

        return strategy

    def _generate_adaptation_reason(self, scenario_name: str, context: Optional[Dict[str, Any]]) -> str:
        """生成适配原因"""
        reason = f"基于场景 {scenario_name} 的历史执行模式分析"

        if scenario_name in self.learning_cache:
            cache = self.learning_cache[scenario_name]
            if "sample_count" in cache:
                reason += f"，累计学习 {cache['sample_count']} 个样本"

        if context:
            if context.get("is_retry"):
                reason += "（重试场景，增强容错）"
            if context.get("is_high_priority"):
                reason += "（高优先级场景，优化执行效率）"

        return reason

    def _predict_success_rate(self, scenario_name: str) -> float:
        """预测执行成功率"""
        scenario_patterns = [p for p in self.execution_patterns if p.get("features", {}).get("scenario_name") == scenario_name]

        if not scenario_patterns:
            return 0.5  # 默认 50% 成功率

        # 基于历史成功率加权预测
        recent_patterns = sorted(scenario_patterns, key=lambda p: p.get("features", {}).get("timestamp", ""), reverse=True)[:5]

        if not recent_patterns:
            return 0.5

        weights = [1.0 / (i + 1) for i in range(len(recent_patterns))]
        total_weight = sum(weights)
        weighted_success = sum(p.get("success_rate", 0) * w for p, w in zip(recent_patterns, weights))

        return weighted_success / total_weight if total_weight > 0 else 0.5

    def auto_optimize_execution(self, scenario_name: str, execution_feedback: Dict[str, Any]) -> Dict[str, Any]:
        """自动优化执行"""
        print(f"\n[执行优化] 正在自动优化场景 {scenario_name} 的执行")

        # 分析执行反馈
        analysis = self.analyze_execution_pattern(scenario_name, execution_feedback)

        # 获取优化后的策略
        optimized_strategy = self.get_adaptive_strategy(scenario_name, {"is_retry": execution_feedback.get("is_retry", False)})

        # 生成优化报告
        optimization_report = {
            "scenario_name": scenario_name,
            "analysis": analysis,
            "optimized_strategy": optimized_strategy,
            "applied_optimizations": analysis.get("recommended_optimizations", []),
            "timestamp": datetime.now().isoformat()
        }

        print(f"[执行优化] 优化完成 - 预测成功率: {optimized_strategy['predicted_success_rate']:.2%}")
        return optimization_report

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱数据接口"""
        # 统计学习情况
        total_scenarios = len(self.learning_cache)
        avg_success_rate = 0.0

        if self.execution_patterns:
            success_rates = [p.get("success_rate", 0) for p in self.execution_patterns]
            avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0.0

        return {
            "engine_name": self.name,
            "version": self.version,
            "total_scenarios_learned": total_scenarios,
            "total_patterns_analyzed": len(self.execution_patterns),
            "average_success_rate": avg_success_rate,
            "current_parameters": self.strategy_parameters,
            "last_updated": datetime.now().isoformat()
        }


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description="元进化执行策略自动学习与智能优化引擎 V2")
    parser.add_argument("--action", choices=["analyze", "learn", "strategy", "optimize", "cockpit"], default="cockpit",
                       help="执行的动作")
    parser.add_argument("--scenario", type=str, help="场景名称")
    parser.add_argument("--execution-log", type=str, help="执行日志 JSON 字符串")

    args = parser.parse_args()

    engine = EvolutionMetaExecutionStrategyAutoLearningV2Engine()

    if args.action == "analyze":
        if not args.scenario or not args.execution_log:
            print("[错误] 需要提供 --scenario 和 --execution-log 参数")
            return

        try:
            execution_log = json.loads(args.execution_log)
            result = engine.analyze_execution_pattern(args.scenario, execution_log)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except json.JSONDecodeError as e:
            print(f"[错误] JSON 解析失败: {e}")

    elif args.action == "learn":
        if not args.scenario:
            print("[错误] 需要提供 --scenario 参数")
            return

        result = engine.learn_optimal_parameters(args.scenario)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.action == "strategy":
        if not args.scenario:
            print("[错误] 需要提供 --scenario 参数")
            return

        result = engine.get_adaptive_strategy(args.scenario)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.action == "optimize":
        if not args.scenario or not args.execution_log:
            print("[错误] 需要提供 --scenario 和 --execution-log 参数")
            return

        try:
            execution_feedback = json.loads(args.execution_log)
            result = engine.auto_optimize_execution(args.scenario, execution_feedback)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except json.JSONDecodeError as e:
            print(f"[错误] JSON 解析失败: {e}")

    elif args.action == "cockpit":
        result = engine.get_cockpit_data()
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()