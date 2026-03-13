#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能自适应进化策略动态调优引擎 (Evolution Adaptive Optimizer)
让系统能够根据进化执行过程中的实时反馈数据，动态分析进化策略的有效性，
自动识别低效/失败模式，并在下一轮迭代中智能调整执行策略参数，实现真正的自适应进化。

功能：
1. 进化执行过程数据收集与分析 - 收集执行中的各项指标
2. 策略有效性实时评估 - 实时评估当前策略的有效性
3. 失败/低效模式自动识别 - 自动识别失败和低效的进化模式
4. 动态策略调优 - 动态调整引擎选择、执行顺序、超时设置等参数

集成：支持"进化自适应调优"、"自适应优化"、"策略动态调整"、"进化优化"等关键词触发
"""

import os
import sys
import json
import glob
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPTS)
RUNTIME_STATE = os.path.join(PROJECT, "runtime", "state")
RUNTIME_LOGS = os.path.join(PROJECT, "runtime", "logs")
REFERENCES = os.path.join(PROJECT, "references")


class EvolutionAdaptiveOptimizer:
    """智能自适应进化策略动态调优引擎"""

    def __init__(self):
        self.name = "EvolutionAdaptiveOptimizer"
        self.version = "1.0.0"
        self.config_path = os.path.join(RUNTIME_STATE, "evolution_adaptive_config.json")
        self.metrics_path = os.path.join(RUNTIME_STATE, "evolution_execution_metrics.json")
        self.patterns_path = os.path.join(RUNTIME_STATE, "evolution_failure_patterns.json")

        self.config = self._load_config()
        self.metrics = self._load_metrics()
        self.failure_patterns = self._load_failure_patterns()

    def _load_config(self) -> Dict:
        """加载配置"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        # 默认配置
        return {
            "strategy_params": {
                "engine_selection_weight": 0.3,
                "execution_order_weight": 0.25,
                "timeout_adjustment_rate": 0.15,
                "retry_strategy": 0.2,
                "parallel_execution_threshold": 0.6
            },
            "thresholds": {
                "low_efficiency_threshold": 0.4,
                "high_risk_threshold": 0.7,
                "timeout_warning_threshold": 300,
                "max_retries": 3
            },
            "adjustment_rules": {
                "on_low_efficiency": ["reduce_engine_count", "increase_timeout", "simplify_execution"],
                "on_failure": ["analyze_root_cause", "adjust_strategy", "fallback_to_baseline"],
                "on_timeout": ["increase_timeout", "split_task", "use_faster_engine"]
            },
            "last_optimization_time": None,
            "optimization_count": 0
        }

    def _save_config(self):
        """保存配置"""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def _load_metrics(self) -> Dict:
        """加载执行指标"""
        if os.path.exists(self.metrics_path):
            try:
                with open(self.metrics_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "execution_records": [],
            "performance_history": [],
            "engine_effectiveness": defaultdict(dict),
            "last_updated": None
        }

    def _save_metrics(self):
        """保存执行指标"""
        try:
            self.metrics["last_updated"] = datetime.now().isoformat()
            with open(self.metrics_path, "w", encoding="utf-8") as f:
                json.dump(self.metrics, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存指标失败: {e}")

    def _load_failure_patterns(self) -> Dict:
        """加载失败模式"""
        if os.path.exists(self.patterns_path):
            try:
                with open(self.patterns_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "patterns": [],
            "inefficient_patterns": [],
            "last_updated": None
        }

    def _save_failure_patterns(self):
        """保存失败模式"""
        try:
            self.failure_patterns["last_updated"] = datetime.now().isoformat()
            with open(self.patterns_path, "w", encoding="utf-8") as f:
                json.dump(self.failure_patterns, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存失败模式失败: {e}")

    def collect_execution_data(self, round_data: Dict) -> Dict:
        """收集执行数据"""
        record = {
            "round": round_data.get("loop_round", 0),
            "goal": round_data.get("current_goal", ""),
            "status": round_data.get("status", "unknown"),
            "execution_time": round_data.get("execution_time", 0),
            "engines_used": round_data.get("engines_used", []),
            "success_rate": round_data.get("success_rate", 0.5),
            "errors": round_data.get("errors", []),
            "timestamp": datetime.now().isoformat()
        }

        # 收集性能指标
        perf_record = {
            "round": record["round"],
            "execution_time": record["execution_time"],
            "success_rate": record["success_rate"],
            "timestamp": record["timestamp"]
        }

        self.metrics["execution_records"].append(record)
        self.metrics["performance_history"].append(perf_record)

        # 更新引擎有效性
        for engine in record.get("engines_used", []):
            if engine not in self.metrics["engine_effectiveness"]:
                self.metrics["engine_effectiveness"][engine] = {
                    "total_uses": 0,
                    "successes": 0,
                    "failures": 0,
                    "avg_execution_time": 0
                }

            engine_stats = self.metrics["engine_effectiveness"][engine]
            engine_stats["total_uses"] += 1
            if record["status"] == "completed":
                engine_stats["successes"] += 1
            else:
                engine_stats["failures"] += 1

        # 保持记录数量限制
        if len(self.metrics["execution_records"]) > 100:
            self.metrics["execution_records"] = self.metrics["execution_records"][-50:]
            self.metrics["performance_history"] = self.metrics["performance_history"][-50:]

        self._save_metrics()

        return {
            "status": "collected",
            "record_count": len(self.metrics["execution_records"])
        }

    def evaluate_strategy_effectiveness(self) -> Dict[str, Any]:
        """评估策略有效性"""
        if len(self.metrics["performance_history"]) < 3:
            return {
                "status": "insufficient_data",
                "message": "数据不足，需要至少3条执行记录"
            }

        recent_records = self.metrics["execution_records"][-10:]

        # 计算关键指标
        total_rounds = len(recent_records)
        successful = sum(1 for r in recent_records if r.get("status") == "completed")
        failed = sum(1 for r in recent_records if r.get("status") in ["failed", "error"])

        avg_execution_time = sum(r.get("execution_time", 0) for r in recent_records) / total_rounds if total_rounds > 0 else 0
        avg_success_rate = sum(r.get("success_rate", 0) for r in recent_records) / total_rounds if total_rounds > 0 else 0

        # 评估各策略参数的有效性
        strategy_params = self.config.get("strategy_params", {})
        effectiveness = {
            "overall_success_rate": successful / total_rounds if total_rounds > 0 else 0,
            "average_execution_time": avg_execution_time,
            "average_success_rate": avg_success_rate,
            "failure_rate": failed / total_rounds if total_rounds > 0 else 0,
            "strategy_effectiveness": self._calculate_strategy_effectiveness(recent_records),
            "engine_rankings": self._rank_engines_by_effectiveness()
        }

        return {
            "status": "evaluated",
            "metrics": effectiveness,
            "recommendation": self._generate_effectiveness_recommendation(effectiveness)
        }

    def _calculate_strategy_effectiveness(self, records: List[Dict]) -> Dict[str, float]:
        """计算各策略的有效性"""
        params = self.config.get("strategy_params", {})

        effectiveness = {}
        for param, weight in params.items():
            # 基于历史数据计算该策略参数的有效性
            # 简化计算：成功率与策略参数的相关性
            if param == "engine_selection_weight":
                # 引擎选择权重有效性：使用成功率高的引擎
                high_success_engines = self._get_high_success_engines()
                effectiveness[param] = len(high_success_engines) / max(len(self.metrics["engine_effectiveness"]), 1)
            elif param == "timeout_adjustment_rate":
                # 超时调整有效性：基于执行时间
                avg_time = sum(r.get("execution_time", 0) for r in records) / len(records) if records else 0
                threshold = self.config.get("thresholds", {}).get("timeout_warning_threshold", 300)
                effectiveness[param] = 1.0 if avg_time < threshold else 0.5
            elif param == "retry_strategy":
                # 重试策略有效性：失败后重试成功率
                retry_success = sum(1 for r in records if r.get("status") == "completed" and r.get("retry_count", 0) > 0)
                total_retries = sum(r.get("retry_count", 0) for r in records)
                effectiveness[param] = retry_success / max(total_retries, 1)
            else:
                effectiveness[param] = 0.5  # 默认值

        return effectiveness

    def _get_high_success_engines(self) -> List[str]:
        """获取高成功率引擎"""
        high_success = []
        for engine, stats in self.metrics["engine_effectiveness"].items():
            if stats["total_uses"] >= 2:
                success_rate = stats["successes"] / stats["total_uses"]
                if success_rate >= 0.7:
                    high_success.append(engine)
        return high_success

    def _rank_engines_by_effectiveness(self) -> List[Dict]:
        """按有效性排序引擎"""
        rankings = []
        for engine, stats in self.metrics["engine_effectiveness"].items():
            if stats["total_uses"] >= 1:
                success_rate = stats["successes"] / stats["total_uses"] if stats["total_uses"] > 0 else 0
                avg_time = stats["avg_execution_time"]
                rankings.append({
                    "engine": engine,
                    "success_rate": success_rate,
                    "total_uses": stats["total_uses"],
                    "effectiveness_score": success_rate * 0.7 + (1 / (avg_time + 1)) * 0.3
                })

        return sorted(rankings, key=lambda x: x["effectiveness_score"], reverse=True)[:10]

    def _generate_effectiveness_recommendation(self, effectiveness: Dict) -> str:
        """生成有效性建议"""
        success_rate = effectiveness.get("overall_success_rate", 0)
        avg_time = effectiveness.get("average_execution_time", 0)
        threshold = self.config.get("thresholds", {})

        if success_rate >= 0.8 and avg_time < threshold.get("timeout_warning_threshold", 300):
            return "策略运行良好，保持当前配置"
        elif success_rate < 0.5:
            return "成功率较低，建议调整策略参数或更换引擎"
        elif avg_time > threshold.get("timeout_warning_threshold", 300):
            return "执行时间过长，建议增加超时时间或优化执行流程"
        else:
            return "策略效果一般，有优化空间"

    def detect_failure_patterns(self) -> Dict[str, Any]:
        """检测失败/低效模式"""
        if len(self.metrics["execution_records"]) < 3:
            return {
                "status": "insufficient_data",
                "message": "数据不足"
            }

        recent = self.metrics["execution_records"][-20:]

        # 检测重复失败模式
        failed_records = [r for r in recent if r.get("status") in ["failed", "error"]]

        if not failed_records:
            return {
                "status": "no_failures",
                "message": "近期无失败记录",
                "patterns": []
            }

        # 分析失败特征
        failure_analysis = {
            "common_engines": [],
            "common_errors": [],
            "execution_time_correlation": None,
            "inefficiency_signals": []
        }

        # 统计失败引擎
        engine_failures = defaultdict(int)
        error_types = defaultdict(int)

        for record in failed_records:
            for engine in record.get("engines_used", []):
                engine_failures[engine] += 1

            for error in record.get("errors", []):
                error_types[error] += 1

        # 获取常见失败引擎
        failure_analysis["common_engines"] = [
            {"engine": e, "count": c}
            for e, c in sorted(engine_failures.items(), key=lambda x: x[1], reverse=True)[:5]
        ]

        # 获取常见错误
        failure_analysis["common_errors"] = [
            {"error": e, "count": c}
            for e, c in sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5]
        ]

        # 检测低效信号
        inefficient_signals = []

        # 信号1：连续失败
        if len(failed_records) >= 3:
            last_three = recent[-3:]
            if all(r.get("status") in ["failed", "error"] for r in last_three):
                inefficient_signals.append({
                    "signal": "连续失败",
                    "severity": "high",
                    "description": "最近3轮连续失败，需要立即调整策略"
                })

        # 信号2：成功率下降
        if len(recent) >= 10:
            first_half = recent[:5]
            second_half = recent[-5:]
            first_rate = sum(r.get("success_rate", 0) for r in first_half) / 5
            second_rate = sum(r.get("success_rate", 0) for r in second_half) / 5

            if second_rate < first_rate * 0.7:
                inefficient_signals.append({
                    "signal": "成功率下降",
                    "severity": "medium",
                    "description": f"成功率从 {first_rate:.1%} 下降到 {second_rate:.1%}"
                })

        # 信号3：执行时间过长
        threshold = self.config.get("thresholds", {}).get("timeout_warning_threshold", 300)
        long_running = [r for r in recent if r.get("execution_time", 0) > threshold]
        if long_running:
            inefficient_signals.append({
                "signal": "执行时间过长",
                "severity": "medium",
                "description": f"{len(long_running)} 轮执行时间超过 {threshold} 秒"
            })

        failure_analysis["inefficiency_signals"] = inefficient_signals

        # 保存检测到的失败模式
        if inefficient_signals:
            self.failure_patterns["patterns"].append({
                "detected_at": datetime.now().isoformat(),
                "signals": inefficient_signals,
                "metrics": failure_analysis
            })
            self._save_failure_patterns()

        return {
            "status": "detected",
            "failure_analysis": failure_analysis,
            "pattern_count": len(inefficient_signals)
        }

    def optimize_strategy(self) -> Dict[str, Any]:
        """动态优化策略"""
        # 评估当前策略有效性
        evaluation = self.evaluate_strategy_effectiveness()

        if evaluation.get("status") == "insufficient_data":
            return {
                "status": "insufficient_data",
                "message": "数据不足，无法优化"
            }

        # 检测失败模式
        failure_detection = self.detect_failure_patterns()

        # 基于分析结果生成优化建议
        optimized_params = dict(self.config.get("strategy_params", {}))
        adjustments = []

        # 优化逻辑
        metrics = evaluation.get("metrics", {})
        effectiveness = metrics.get("strategy_effectiveness", {})

        # 根据策略有效性调整权重
        for param, eff in effectiveness.items():
            if eff < 0.4:
                # 有效性低，降低该策略的权重
                original = optimized_params.get(param, 0.2)
                optimized_params[param] = max(0.1, original * 0.8)
                adjustments.append(f"{param}: {original:.2f} -> {optimized_params[param]:.2f} (有效性低)")

        # 根据失败模式调整
        if failure_detection.get("status") == "detected":
            signals = failure_detection.get("failure_analysis", {}).get("inefficiency_signals", [])

            for signal in signals:
                signal_type = signal.get("signal", "")
                severity = signal.get("severity", "low")

                if severity == "high":
                    # 高严重性：大幅调整
                    if "连续失败" in signal_type:
                        optimized_params["retry_strategy"] = min(0.4, optimized_params.get("retry_strategy", 0.2) + 0.15)
                        adjustments.append("retry_strategy: 增加重试策略权重")
                    if "执行时间过长" in signal_type:
                        optimized_params["timeout_adjustment_rate"] = min(0.3, optimized_params.get("timeout_adjustment_rate", 0.15) + 0.1)
                        adjustments.append("timeout_adjustment_rate: 增加超时调整权重")

                elif severity == "medium":
                    # 中等严重性：适度调整
                    if "成功率下降" in signal_type:
                        optimized_params["engine_selection_weight"] = min(0.5, optimized_params.get("engine_selection_weight", 0.3) + 0.1)
                        adjustments.append("engine_selection_weight: 增加引擎选择权重")

        # 确保权重总和合理
        total_weight = sum(optimized_params.values())
        if total_weight > 1.0:
            # 归一化
            for param in optimized_params:
                optimized_params[param] = optimized_params[param] / total_weight

        # 保存优化结果
        self.config["strategy_params"] = optimized_params
        self.config["last_optimization_time"] = datetime.now().isoformat()
        self.config["optimization_count"] = self.config.get("optimization_count", 0) + 1
        self._save_config()

        return {
            "status": "optimized",
            "original_params": self.config.get("strategy_params", {}),
            "optimized_params": optimized_params,
            "adjustments": adjustments,
            "evaluation_summary": evaluation.get("recommendation", ""),
            "failure_detection_summary": failure_detection.get("status", "unknown"),
            "optimization_time": datetime.now().isoformat()
        }

    def get_adaptive_recommendations(self) -> Dict[str, Any]:
        """获取自适应建议（供进化环在决策时调用）"""
        # 快速分析最近数据
        recent_metrics = self.metrics.get("execution_records", [])[-5:]

        if not recent_metrics:
            return {
                "status": "no_data",
                "recommendations": ["暂无执行数据，无法生成建议"]
            }

        recommendations = []

        # 基于最近表现生成建议
        success_count = sum(1 for r in recent_metrics if r.get("status") == "completed")
        success_rate = success_count / len(recent_metrics)

        avg_time = sum(r.get("execution_time", 0) for r in recent_metrics) / len(recent_metrics)

        if success_rate >= 0.8:
            recommendations.append({
                "type": "positive",
                "message": "近期进化表现良好，成功率较高",
                "action": "保持当前策略，可适度尝试创新"
            })
        elif success_rate >= 0.5:
            recommendations.append({
                "type": "caution",
                "message": "近期成功率一般，建议优化策略",
                "action": "可调用 optimize_strategy() 进行策略调优"
            })
        else:
            recommendations.append({
                "type": "warning",
                "message": "近期失败率较高，需要调整",
                "action": "建议先运行 optimize_strategy() 优化策略"
            })

        if avg_time > 300:
            recommendations.append({
                "type": "performance",
                "message": f"平均执行时间较长 ({avg_time:.0f}秒)",
                "action": "考虑增加超时时间或优化执行流程"
            })

        # 引擎建议
        engine_rankings = self._rank_engines_by_effectiveness()
        if engine_rankings:
            top_engine = engine_rankings[0]
            recommendations.append({
                "type": "engine",
                "message": f"当前最有效的引擎: {top_engine['engine']} (成功率 {top_engine['success_rate']:.1%})",
                "action": "在后续进化中优先考虑使用该引擎"
            })

            # 警告低效引擎
            low_engines = [e for e in engine_rankings[-3:] if e['success_rate'] < 0.3]
            if low_engines:
                recommendations.append({
                    "type": "warning",
                    "message": f"低效引擎: {', '.join([e['engine'] for e in low_engines])}",
                    "action": "建议减少使用或优化这些引擎"
                })

        return {
            "status": "ready",
            "recommendations": recommendations,
            "quick_stats": {
                "recent_success_rate": success_rate,
                "average_execution_time": avg_time,
                "total_records": len(self.metrics.get("execution_records", []))
            }
        }

    def get_status(self) -> Dict[str, Any]:
        """获取优化器状态"""
        return {
            "name": self.name,
            "version": self.version,
            "config": {
                "strategy_params": self.config.get("strategy_params", {}),
                "thresholds": self.config.get("thresholds", {}),
                "optimization_count": self.config.get("optimization_count", 0),
                "last_optimization": self.config.get("last_optimization_time")
            },
            "metrics": {
                "total_records": len(self.metrics.get("execution_records", [])),
                "engine_count": len(self.metrics.get("engine_effectiveness", {})),
                "last_updated": self.metrics.get("last_updated")
            },
            "failure_patterns": {
                "pattern_count": len(self.failure_patterns.get("patterns", []))
            }
        }


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="智能自适应进化策略动态调优引擎")
    parser.add_argument("command", nargs="?", default="status",
                       help="命令: status|collect|evaluate|detect|optimize|recommend")
    parser.add_argument("--round", type=int, help="轮次号")
    parser.add_argument("--goal", type=str, help="进化目标")
    parser.add_argument("--status", type=str, help="执行状态")
    parser.add_argument("--time", type=float, help="执行时间(秒)")
    parser.add_argument("--engines", type=str, help="使用的引擎(逗号分隔)")
    parser.add_argument("--rate", type=float, help="成功率")

    args = parser.parse_args()

    optimizer = EvolutionAdaptiveOptimizer()

    if args.command == "status":
        result = optimizer.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "collect":
        if not all([args.round, args.goal, args.status]):
            print("错误: 需要提供 --round, --goal, --status 参数")
            sys.exit(1)

        round_data = {
            "loop_round": args.round,
            "current_goal": args.goal,
            "status": args.status,
            "execution_time": args.time or 0,
            "engines_used": args.engines.split(",") if args.engines else [],
            "success_rate": args.rate or 0.5
        }
        result = optimizer.collect_execution_data(round_data)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "evaluate":
        result = optimizer.evaluate_strategy_effectiveness()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "detect":
        result = optimizer.detect_failure_patterns()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "optimize":
        result = optimizer.optimize_strategy()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "recommend":
        result = optimizer.get_adaptive_recommendations()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {args.command}")
        print("可用命令: status, collect, evaluate, detect, optimize, recommend")
        sys.exit(1)


if __name__ == "__main__":
    main()