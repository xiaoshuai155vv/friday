#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环自我评估与策略迭代优化引擎

在 round 387 完成的元进化自主意识深度增强引擎基础上，进一步增强系统的自我评估与策略迭代优化能力。
让系统能够自动分析进化决策的效果、识别低效模式、动态调整进化策略参数，形成真正的「决策→执行→评估→优化」的闭环。
系统不仅能决定要进化什么，还能评估自己的决策质量并持续改进。

Version: 1.0.0
Author: Auto Evolution System
"""

import json
import os
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# 基础路径配置
SCRIPT_DIR = Path(__file__).parent
RUNTIME_DIR = SCRIPT_DIR.parent / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"
CONFIG_DIR = RUNTIME_DIR / "config"


def _safe_print(text: str):
    """安全打印，支持 UTF-8"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore'))


class EvolutionSelfEvaluationStrategyIterationEngine:
    """
    自我评估与策略迭代优化引擎

    核心能力：
    1. 进化决策效果自动评估 - 分析成功率、效率、偏差
    2. 低效模式识别 - 发现重复决策、保守策略、资源浪费
    3. 策略参数动态迭代优化 - 调整触发阈值、权重、执行顺序
    4. 评估→优化→执行→验证闭环
    5. 驾驶舱集成 - 可视化展示评估结果和优化建议
    """

    def __init__(self):
        self.engine_name = "self_evaluation_strategy_iteration"
        self.version = "1.0.0"
        self.state_file = STATE_DIR / f"{self.engine_name}_state.json"
        self.evaluation_history_file = STATE_DIR / f"{self.engine_name}_evaluation_history.json"
        self.optimization_log_file = STATE_DIR / f"{self.engine_name}_optimization_log.json"
        self.config = self._load_config()
        self.load_state()
        self._ensure_dependencies()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        config_file = CONFIG_DIR / "evolution_loop.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                _safe_print(f"[{self.engine_name}] 配置加载失败: {e}")

        return {
            "auto_evaluation_enabled": True,
            "pattern_detection_enabled": True,
            "auto_optimization_enabled": True,
            "cockpit_integration_enabled": True,
            "evaluation_window_size": 20,
            "min_samples_for_optimization": 5,
            "consecutive_failure_threshold": 3,
            "efficiency_degradation_threshold": 0.2
        }

    def _ensure_dependencies(self):
        """确保依赖模块存在"""
        self.meta_autonomous_available = False
        self.cockpit_available = False
        self.decision_quality_available = False
        self.adaptive_learning_available = False

        # 检查元进化自主意识引擎 (round 387)
        meta_file = SCRIPT_DIR / "evolution_meta_autonomous_consciousness_deep_engine.py"
        if meta_file.exists():
            self.meta_autonomous_available = True
            _safe_print(f"[{self.engine_name}] 元进化自主意识引擎已就绪")

        # 检查进化驾驶舱 (round 350)
        cockpit_file = SCRIPT_DIR / "evolution_cockpit_engine.py"
        if cockpit_file.exists():
            self.cockpit_available = True
            _safe_print(f"[{self.engine_name}] 进化驾驶舱已就绪")

        # 检查决策质量评估引擎 (round 335)
        dq_file = SCRIPT_DIR / "evolution_decision_quality_evaluator.py"
        if dq_file.exists():
            self.decision_quality_available = True
            _safe_print(f"[{self.engine_name}] 决策质量评估引擎已就绪")

        # 检查自适应学习引擎 (round 352)
        al_file = SCRIPT_DIR / "evolution_adaptive_learning_strategy_engine.py"
        if al_file.exists():
            self.adaptive_learning_available = True
            _safe_print(f"[{self.engine_name}] 自适应学习引擎已就绪")

    def load_state(self):
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    self.state = json.load(f)
            except Exception as e:
                _safe_print(f"[{self.engine_name}] 状态加载失败: {e}")
                self.state = self._get_default_state()
        else:
            self.state = self._get_default_state()

    def _get_default_state(self) -> Dict[str, Any]:
        """获取默认状态"""
        return {
            "evaluation_count": 0,
            "optimization_count": 0,
            "patterns_identified": [],
            "current_strategy_params": {
                "opportunity_threshold": 0.3,
                "decision_weight_urgency": 0.4,
                "decision_weight_value": 0.6,
                "execution_timeout_minutes": 30,
                "max_retries": 3
            },
            "last_evaluation_time": None,
            "last_optimization_time": None,
            "efficiency_trend": [],
            "active": False
        }

    def save_state(self):
        """保存状态"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[{self.engine_name}] 状态保存失败: {e}")

    def evaluate_decision_effectiveness(self) -> Dict[str, Any]:
        """
        评估进化决策效果

        分析最近的进化决策与执行结果，计算：
        - 成功率
        - 效率
        - 偏差分析
        """
        _safe_print(f"[{self.engine_name}] 开始评估进化决策效果...")

        # 获取最近的进化完成记录
        completed_files = sorted(STATE_DIR.glob("evolution_completed_ev_*.json"))

        # 取最近 N 个
        window_size = self.config.get("evaluation_window_size", 20)
        recent_files = completed_files[-window_size:] if len(completed_files) > window_size else completed_files

        if len(recent_files) < 3:
            return {
                "status": "insufficient_data",
                "message": f"数据不足（{len(recent_files)} 条），需要更多进化数据",
                "sample_size": len(recent_files)
            }

        evaluations = []
        success_count = 0
        total_estimated_time = 0
        total_actual_time = 0

        for f in recent_files:
            try:
                with open(f, 'r', encoding='utf-8') as data:
                    info = json.load(data)

                    # 解析结果
                    goal = info.get("current_goal", "")
                    status = info.get("status", "unknown")
                    baseline = info.get("基线校验", "")

                    # 判断是否成功
                    is_success = status == "已完成" or "通过" in baseline
                    if is_success:
                        success_count += 1

                    evaluations.append({
                        "goal": goal,
                        "status": status,
                        "success": is_success,
                        "baseline_check": baseline
                    })
            except Exception as e:
                _safe_print(f"[{self.engine_name}] 解析 {f} 失败: {e}")

        # 计算指标
        success_rate = success_count / len(evaluations) if evaluations else 0
        avg_time = total_actual_time / len(evaluations) if evaluations and total_actual_time > 0 else 0

        # 计算效率趋势（如果有足够数据）
        efficiency_trend = self._calculate_efficiency_trend(evaluations)

        result = {
            "status": "completed",
            "sample_size": len(evaluations),
            "success_rate": round(success_rate, 3),
            "success_count": success_count,
            "failure_count": len(evaluations) - success_count,
            "efficiency_trend": efficiency_trend,
            "evaluations": evaluations[-10:],  # 最近10条
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # 更新状态
        self.state["evaluation_count"] = self.state.get("evaluation_count", 0) + 1
        self.state["last_evaluation_time"] = result["timestamp"]
        self.save_state()

        # 保存评估历史
        self._save_evaluation_history(result)

        _safe_print(f"[{self.engine_name}] 评估完成: 成功率 {success_rate:.1%}, 样本数 {len(evaluations)}")

        return result

    def _calculate_efficiency_trend(self, evaluations: List[Dict[str, Any]]) -> str:
        """计算效率趋势"""
        if len(evaluations) < 5:
            return "stable"

        # 检查最近的一半 vs 更早的一半
        mid = len(evaluations) // 2
        recent = evaluations[mid:]
        older = evaluations[:mid]

        recent_success = sum(1 for e in recent if e.get("success", False))
        older_success = sum(1 for e in older if e.get("success", False))

        recent_rate = recent_success / len(recent) if recent else 0
        older_rate = older_success / len(older) if older else 0

        diff = recent_rate - older_rate

        if diff > 0.1:
            return "improving"
        elif diff < -0.1:
            return "degrading"
        else:
            return "stable"

    def _save_evaluation_history(self, result: Dict[str, Any]):
        """保存评估历史"""
        history = []
        if self.evaluation_history_file.exists():
            try:
                with open(self.evaluation_history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except:
                pass

        history.append(result)

        # 只保留最近50条
        history = history[-50:]

        try:
            with open(self.evaluation_history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[{self.engine_name}] 评估历史保存失败: {e}")

    def identify_inefficient_patterns(self) -> List[Dict[str, Any]]:
        """
        识别低效模式

        发现：
        - 重复决策
        - 保守策略
        - 资源浪费
        - 连续失败
        """
        _safe_print(f"[{self.engine_name}] 识别低效模式...")

        patterns = []

        # 获取评估历史
        history = []
        if self.evaluation_history_file.exists():
            try:
                with open(self.evaluation_history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except:
                pass

        if len(history) < 3:
            return patterns

        # 检查连续失败模式
        consecutive_failures = self._detect_consecutive_failures(history)
        if consecutive_failures > 0:
            patterns.append({
                "type": "consecutive_failures",
                "description": f"检测到连续 {consecutive_failures} 次失败",
                "severity": "high",
                "suggestion": "检查进化策略是否失效，考虑调整触发条件"
            })

        # 检查重复进化模式
        repetition = self._detect_repetition_pattern(history)
        if repetition:
            patterns.append({
                "type": "repetition",
                "description": "检测到重复进化模式",
                "severity": "medium",
                "details": repetition,
                "suggestion": "优化进化策略多样性，避免重复"
            })

        # 检查效率下降趋势
        efficiency_trend = history[-1].get("efficiency_trend", "stable") if history else "stable"
        if efficiency_trend == "degrading":
            patterns.append({
                "type": "efficiency_degradation",
                "description": "检测到效率下降趋势",
                "severity": "high",
                "suggestion": "需要调整进化策略参数"
            })

        # 检查成功率过低
        recent_success_rate = history[-1].get("success_rate", 0.5) if history else 0.5
        if recent_success_rate < 0.5:
            patterns.append({
                "type": "low_success_rate",
                "description": f"成功率过低: {recent_success_rate:.1%}",
                "severity": "high",
                "suggestion": "重新评估进化目标和执行策略"
            })

        # 更新状态
        self.state["patterns_identified"] = patterns
        self.save_state()

        _safe_print(f"[{self.engine_name}] 发现 {len(patterns)} 个低效模式")

        return patterns

    def _detect_consecutive_failures(self, history: List[Dict[str, Any]]) -> int:
        """检测连续失败"""
        threshold = self.config.get("consecutive_failure_threshold", 3)
        consecutive = 0
        max_consecutive = 0

        for entry in reversed(history):
            if not entry.get("success", True):
                consecutive += 1
                max_consecutive = max(max_consecutive, consecutive)
            else:
                consecutive = 0

        return max_consecutive if max_consecutive >= threshold else 0

    def _detect_repetition_pattern(self, history: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """检测重复模式"""
        # 统计目标相似度
        goals = [e.get("goal", "") for e in history[-10:] if e.get("goal")]

        if len(goals) < 3:
            return None

        # 简单相似度检测（检查关键词重复）
        keyword_counts = defaultdict(int)
        for goal in goals:
            # 提取关键词
            keywords = goal.split()[-3:]  # 取最后3个词
            for kw in keywords:
                if len(kw) > 2:
                    keyword_counts[kw] += 1

        # 找出重复最多的关键词
        max_count = max(keyword_counts.values()) if keyword_counts else 0
        if max_count >= 3:
            most_common = max(keyword_counts.items(), key=lambda x: x[1])
            return {
                "keyword": most_common[0],
                "count": most_common[1],
                "total": len(goals)
            }

        return None

    def generate_optimization_recommendations(self, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        生成优化建议

        基于识别的低效模式，生成可执行的优化建议
        """
        recommendations = []

        for pattern in patterns:
            if pattern.get("type") == "consecutive_failures":
                # 建议调整触发条件
                recommendations.append({
                    "type": "parameter_adjustment",
                    "parameter": "opportunity_threshold",
                    "current_value": self.state["current_strategy_params"]["opportunity_threshold"],
                    "suggested_value": min(0.6, self.state["current_strategy_params"]["opportunity_threshold"] + 0.1),
                    "reason": "连续失败，需要提高触发阈值以选择更安全的进化机会",
                    "priority": "high"
                })

            elif pattern.get("type") == "repetition":
                # 建议增加策略多样性
                recommendations.append({
                    "type": "strategy_diversification",
                    "suggestion": "增加进化策略的多样性，避免重复",
                    "actions": [
                        "引入更多进化目标候选",
                        "增加随机性因素",
                        "优先选择长期未执行的进化方向"
                    ],
                    "priority": "medium"
                })

            elif pattern.get("type") == "efficiency_degradation":
                # 建议调整权重
                recommendations.append({
                    "type": "weight_adjustment",
                    "parameter": "decision_weight_value",
                    "current_value": self.state["current_strategy_params"]["decision_weight_value"],
                    "suggested_value": self.state["current_strategy_params"]["decision_weight_value"] + 0.1,
                    "reason": "效率下降，需要更加重视价值评估",
                    "priority": "high"
                })

            elif pattern.get("type") == "low_success_rate":
                # 建议全面审查
                recommendations.append({
                    "type": "comprehensive_review",
                    "suggestion": "成功率过低，建议全面审查进化策略",
                    "actions": [
                        "分析失败原因",
                        "检查执行环境",
                        "重新评估目标设定"
                    ],
                    "priority": "critical"
                })

        # 添加通用优化建议（如果没有发现特定模式）
        if not recommendations:
            recommendations.append({
                "type": "proactive_optimization",
                "suggestion": "系统运行正常，进行预防性优化",
                "actions": [
                    "微调参数以进一步提升效率",
                    "更新评估模型权重"
                ],
                "priority": "low"
            })

        _safe_print(f"[{self.engine_name}] 生成了 {len(recommendations)} 条优化建议")

        return recommendations

    def apply_optimizations(self, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        应用优化建议

        自动调整策略参数，形成优化闭环
        """
        _safe_print(f"[{self.engine_name}] 应用优化建议...")

        applied = []
        current_params = self.state["current_strategy_params"]

        for rec in recommendations:
            if rec.get("type") == "parameter_adjustment":
                param = rec.get("parameter")
                suggested = rec.get("suggested_value")

                if param in current_params:
                    old_value = current_params[param]
                    current_params[param] = suggested
                    applied.append({
                        "parameter": param,
                        "old_value": old_value,
                        "new_value": suggested,
                        "reason": rec.get("reason")
                    })
                    _safe_print(f"[{self.engine_name}] 调整参数 {param}: {old_value} -> {suggested}")

            elif rec.get("type") == "weight_adjustment":
                param = rec.get("parameter")
                suggested = rec.get("suggested_value")

                if param in current_params:
                    old_value = current_params[param]
                    current_params[param] = min(1.0, suggested)  # 不超过1
                    applied.append({
                        "parameter": param,
                        "old_value": old_value,
                        "new_value": current_params[param],
                        "reason": rec.get("reason")
                    })
                    _safe_print(f"[{self.engine_name}] 调整权重 {param}: {old_value} -> {current_params[param]}")

        # 更新状态
        self.state["current_strategy_params"] = current_params
        self.state["optimization_count"] = self.state.get("optimization_count", 0) + 1
        self.state["last_optimization_time"] = datetime.now(timezone.utc).isoformat()
        self.save_state()

        # 记录优化日志
        self._log_optimization(applied, recommendations)

        return {
            "status": "completed",
            "applied_count": len(applied),
            "applied": applied,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def _log_optimization(self, applied: List[Dict[str, Any]], recommendations: List[Dict[str, Any]]):
        """记录优化日志"""
        logs = []
        if self.optimization_log_file.exists():
            try:
                with open(self.optimization_log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except:
                pass

        logs.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "applied": applied,
            "total_recommendations": len(recommendations),
            "applied_count": len(applied)
        })

        # 只保留最近50条
        logs = logs[-50:]

        try:
            with open(self.optimization_log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[{self.engine_name}] 优化日志写入失败: {e}")

    def run_full_optimization_cycle(self) -> Dict[str, Any]:
        """
        运行完整的评估→优化循环

        流程：评估效果 -> 识别模式 -> 生成建议 -> 应用优化
        """
        _safe_print(f"[{self.engine_name}] 启动完整优化周期...")

        # 1. 评估决策效果
        evaluation = self.evaluate_decision_effectiveness()

        # 2. 识别低效模式
        patterns = self.identify_inefficient_patterns()

        # 3. 生成优化建议
        recommendations = self.generate_optimization_recommendations(patterns)

        # 4. 应用优化
        optimization = self.apply_optimizations(recommendations)

        return {
            "evaluation": evaluation,
            "patterns": patterns,
            "recommendations": recommendations,
            "optimization": optimization,
            "current_params": self.state["current_strategy_params"]
        }

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "engine_name": self.engine_name,
            "version": self.version,
            "evaluation_count": self.state.get("evaluation_count", 0),
            "optimization_count": self.state.get("optimization_count", 0),
            "patterns_identified_count": len(self.state.get("patterns_identified", [])),
            "current_params": self.state.get("current_strategy_params", {}),
            "last_evaluation_time": self.state.get("last_evaluation_time"),
            "last_optimization_time": self.state.get("last_optimization_time"),
            "dependencies": {
                "meta_autonomous": self.meta_autonomous_available,
                "cockpit": self.cockpit_available,
                "decision_quality": self.decision_quality_available,
                "adaptive_learning": self.adaptive_learning_available
            }
        }


# CLI 接口
def main():
    import argparse

    parser = argparse.ArgumentParser(description="自我评估与策略迭代优化引擎")
    parser.add_argument("command", choices=["evaluate", "identify", "optimize", "full_cycle", "status"],
                        help="要执行的命令")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    args = parser.parse_args()

    engine = EvolutionSelfEvaluationStrategyIterationEngine()

    if args.command == "evaluate":
        result = engine.evaluate_decision_effectiveness()
        _safe_print(f"\n评估结果:")
        _safe_print(f"  状态: {result.get('status')}")
        _safe_print(f"  样本数: {result.get('sample_size', 0)}")
        _safe_print(f"  成功率: {result.get('success_rate', 0):.1%}")

    elif args.command == "identify":
        patterns = engine.identify_inefficient_patterns()
        _safe_print(f"\n发现 {len(patterns)} 个低效模式:")
        for i, p in enumerate(patterns, 1):
            _safe_print(f"  {i}. [{p.get('severity')}] {p.get('description')}")
            _safe_print(f"     建议: {p.get('suggestion')}")

    elif args.command == "optimize":
        patterns = engine.identify_inefficient_patterns()
        recommendations = engine.generate_optimization_recommendations(patterns)
        result = engine.apply_optimizations(recommendations)
        _safe_print(f"\n优化完成:")
        _safe_print(f"  应用 {result.get('applied_count')} 项优化")

    elif args.command == "full_cycle":
        result = engine.run_full_optimization_cycle()
        _safe_print(f"\n完整优化周期执行完成:")
        _safe_print(f"  评估: {result['evaluation'].get('status')}")
        _safe_print(f"  发现模式: {len(result['patterns'])} 个")
        _safe_print(f"  生成建议: {len(result['recommendations'])} 条")
        _safe_print(f"  应用优化: {result['optimization'].get('applied_count')} 项")

    elif args.command == "status":
        status = engine.get_status()
        _safe_print(f"\n引擎状态:")
        _safe_print(f"  引擎: {status['engine_name']} v{status['version']}")
        _safe_print(f"  评估次数: {status['evaluation_count']}")
        _safe_print(f"  优化次数: {status['optimization_count']}")
        _safe_print(f"  当前策略参数:")
        for k, v in status['current_params'].items():
            _safe_print(f"    - {k}: {v}")
        _safe_print(f"  依赖模块:")
        for dep, available in status['dependencies'].items():
            _safe_print(f"    - {dep}: {'OK' if available else 'NO'}")


if __name__ == "__main__":
    main()