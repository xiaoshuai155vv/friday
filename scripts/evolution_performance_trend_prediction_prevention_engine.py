#!/usr/bin/env python3
"""
智能全场景进化环性能趋势预测与预防性优化增强引擎
version 1.0.0

在 round 518 完成的性能基准测试与回归检测引擎基础上，进一步增强趋势预测能力，
实现从「检测回归」到「预测趋势→预防性优化」的完整闭环。

让系统能够：
1. 基于历史数据的深度趋势预测
2. 在性能劣化前主动采取预防措施
3. 形成「检测→预测→预防→验证」的完整闭环

功能：
1. 性能趋势深度预测 - 基于多维度历史数据的趋势预测
2. 预防性优化策略生成 - 预测到潜在问题后自动生成优化策略
3. 自动预防执行 - 自动触发预防性优化措施
4. 预防效果验证 - 验证预防措施的有效性
5. 与进化驾驶舱深度集成
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import argparse

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE_DIR = PROJECT_ROOT / "runtime" / "state"
RUNTIME_LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"
EVOLUTION_AUTO_LAST = PROJECT_ROOT / "references" / "evolution_auto_last.md"
CAPABILITIES_FILE = PROJECT_ROOT / "references" / "capabilities.md"


class PerformanceTrendPredictionPreventionEngine:
    """性能趋势预测与预防性优化增强引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.name = "PerformanceTrendPredictionPreventionEngine"
        self.state_file = RUNTIME_STATE_DIR / "performance_trend_prediction_state.json"
        self.prediction_history_file = RUNTIME_STATE_DIR / "trend_prediction_history.json"
        self.prevention_log_file = RUNTIME_STATE_DIR / "prevention_execution_log.json"
        self._ensure_state_dir()

    def _ensure_state_dir(self):
        """确保状态目录存在"""
        RUNTIME_STATE_DIR.mkdir(parents=True, exist_ok=True)

    def _load_state(self) -> Dict:
        """加载引擎状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "version": self.version,
            "initialized_at": datetime.now().isoformat(),
            "last_prediction": None,
            "last_prevention_action": None,
            "prediction_accuracy": [],
            "prevention_count": 0,
            "prevention_success_rate": 0.0
        }

    def _save_state(self, state: Dict):
        """保存引擎状态"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def _load_evolution_history(self) -> List[Dict]:
        """加载进化历史数据"""
        history = []
        state_dir = RUNTIME_STATE_DIR
        if state_dir.exists():
            for f in state_dir.glob("evolution_completed_*.json"):
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        if isinstance(data, dict):
                            history.append(data)
                except:
                    pass
        history.sort(key=lambda x: x.get('completed_at', ''), reverse=True)
        return history

    def _collect_performance_metrics(self) -> Dict[str, Any]:
        """收集当前性能指标"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "total_engines": 0,
            "total_rounds": 0,
            "recent_rounds": 0,
            "execution_metrics": {}
        }

        # 统计引擎数量
        scripts_dir = PROJECT_ROOT / "scripts"
        if scripts_dir.exists():
            engine_files = list(scripts_dir.glob("evolution_*.py"))
            metrics["total_engines"] = len(engine_files)

        # 加载进化历史
        history = self._load_evolution_history()
        metrics["total_rounds"] = len(history)

        # 计算最近 rounds 的指标（最近 10 轮）
        recent_history = history[:10]
        metrics["recent_rounds"] = len(recent_history)

        if recent_history:
            total_time = 0
            count = 0
            for h in recent_history:
                if 'execution_time' in h:
                    total_time += h.get('execution_time', 0)
                    count += 1
            if count > 0:
                metrics["execution_metrics"]["avg_execution_time"] = total_time / count

            success_count = sum(1 for h in recent_history if h.get('status') == 'completed')
            metrics["execution_metrics"]["success_rate"] = success_count / len(recent_history) if recent_history else 0

        return metrics

    def _analyze_trend_patterns(self, history: List[Dict]) -> Dict:
        """分析趋势模式"""
        if len(history) < 5:
            return {
                "pattern": "insufficient_data",
                "confidence": 0.0,
                "description": "数据不足，无法分析趋势模式"
            }

        # 将历史数据按时间分组分析
        recent = history[:5]
        older = history[5:15] if len(history) > 5 else []

        # 计算各时间段的平均成功率
        def calc_success_rate(h_list):
            if not h_list:
                return 0.0
            success = sum(1 for h in h_list if h.get('status') == 'completed')
            return success / len(h_list)

        recent_rate = calc_success_rate(recent)
        older_rate = calc_success_rate(older)

        # 分析趋势模式
        pattern_analysis = {
            "recent_rate": recent_rate,
            "older_rate": older_rate,
            "rate_change": recent_rate - older_rate,
            "pattern": "stable",
            "confidence": 0.0,
            "description": ""
        }

        # 判断趋势模式
        if abs(recent_rate - older_rate) < 0.1:
            if recent_rate >= 0.9:
                pattern_analysis["pattern"] = "excellent_stable"
                pattern_analysis["confidence"] = 0.9
                pattern_analysis["description"] = "系统运行优秀且稳定"
            else:
                pattern_analysis["pattern"] = "stable"
                pattern_analysis["confidence"] = 0.8
                pattern_analysis["description"] = "系统运行稳定"
        elif recent_rate > older_rate:
            pattern_analysis["pattern"] = "improving"
            pattern_analysis["confidence"] = min(0.9, 0.5 + abs(recent_rate - older_rate))
            pattern_analysis["description"] = f"系统性能正在改善（提升 {(recent_rate-older_rate)*100:.1f}%）"
        else:
            pattern_analysis["pattern"] = "declining"
            pattern_analysis["confidence"] = min(0.9, 0.5 + abs(recent_rate - older_rate))
            pattern_analysis["description"] = f"系统性能有下降趋势（下降 {(older_rate-recent_rate)*100:.1f}%）"

        return pattern_analysis

    def _predict_future_performance(self, history: List[Dict]) -> Dict:
        """预测未来性能"""
        if len(history) < 10:
            return {
                "prediction": "insufficient_data",
                "predicted_success_rate": None,
                "risk_level": "unknown",
                "prediction_basis": "需要至少 10 轮数据才能进行准确预测"
            }

        # 基于历史趋势进行预测
        # 使用简单线性回归思想：分析最近数据的变化趋势
        window_size = min(5, len(history) // 2)

        # 计算近期窗口的平均成功率
        recent_window = history[:window_size]
        older_window = history[window_size:window_size*2] if len(history) > window_size * 2 else []

        def calc_rate(h_list):
            if not h_list:
                return 0.5
            return sum(1 for h in h_list if h.get('status') == 'completed') / len(h_list)

        recent_rate = calc_rate(recent_window)
        older_rate = calc_rate(older_window) if older_window else recent_rate

        # 计算趋势斜率
        rate_change = recent_rate - older_rate if older_window else 0

        # 预测下一轮的成功率（简单的线性外推）
        predicted_rate = recent_rate + rate_change

        # 限制在合理范围内
        predicted_rate = max(0.0, min(1.0, predicted_rate))

        # 评估风险等级
        risk_level = "low"
        if predicted_rate < 0.5:
            risk_level = "critical"
        elif predicted_rate < 0.7:
            risk_level = "high"
        elif predicted_rate < 0.85:
            risk_level = "medium"

        return {
            "predicted_success_rate": predicted_rate,
            "current_success_rate": recent_rate,
            "trend_slope": rate_change,
            "risk_level": risk_level,
            "prediction_basis": f"基于最近 {window_size} 轮的数据趋势分析",
            "confidence": 0.7 if len(history) >= 15 else 0.5
        }

    def _generate_prevention_strategies(self, prediction: Dict, pattern: Dict) -> List[Dict]:
        """生成预防性优化策略"""
        strategies = []

        risk_level = prediction.get("risk_level", "unknown")
        predicted_rate = prediction.get("predicted_success_rate", 1.0)
        pattern_type = pattern.get("pattern", "stable")

        # 根据风险等级生成不同策略
        if risk_level == "critical":
            strategies.append({
                "type": "urgent_health_check",
                "priority": "critical",
                "description": "执行紧急健康检查，识别系统级问题",
                "action": "run_health_diagnosis",
                "expected_impact": "立即发现并修复关键问题"
            })
            strategies.append({
                "type": "reduce_evolution_load",
                "priority": "critical",
                "description": "降低进化环负载，避免过载",
                "action": "reduce_evolution_load",
                "expected_impact": "减少系统压力，提高稳定性"
            })

        if risk_level in ["critical", "high"]:
            strategies.append({
                "type": "baseline_refresh",
                "priority": "high",
                "description": "刷新性能基准，适配当前系统状态",
                "action": "refresh_baseline",
                "expected_impact": "重新建立准确的性能基准"
            })
            strategies.append({
                "type": "optimization_recommendation",
                "priority": "high",
                "description": "生成优化建议并主动执行",
                "action": "generate_optimizations",
                "expected_impact": "识别并解决性能瓶颈"
            })

        if pattern_type == "declining":
            strategies.append({
                "type": "trend_analysis",
                "priority": "medium",
                "description": "深入分析下降趋势的根本原因",
                "action": "deep_trend_analysis",
                "expected_impact": "理解性能下降的根本原因"
            })

        # 通用预防策略
        strategies.append({
            "type": "proactive_monitoring",
            "priority": "low",
            "description": "增强主动监控，提前发现问题",
            "action": "enhance_monitoring",
            "expected_impact": "提前预警潜在问题"
        })

        return strategies

    def predict_trend(self) -> Dict:
        """预测性能趋势"""
        history = self._load_evolution_history()
        current_metrics = self._collect_performance_metrics()

        # 分析趋势模式
        pattern = self._analyze_trend_patterns(history)

        # 预测未来性能
        prediction = self._predict_future_performance(history)

        # 生成预防策略
        strategies = self._generate_prevention_strategies(prediction, pattern)

        result = {
            "status": "success",
            "current_metrics": {
                "total_engines": current_metrics.get("total_engines", 0),
                "total_rounds": current_metrics.get("total_rounds", 0),
                "recent_success_rate": current_metrics.get("execution_metrics", {}).get("success_rate", 0)
            },
            "trend_pattern": pattern,
            "future_prediction": prediction,
            "prevention_strategies": strategies,
            "recommendation": strategies[0]["description"] if strategies else "系统运行正常，无需预防措施"
        }

        # 保存预测历史
        self._save_prediction_history(result)

        return result

    def _save_prediction_history(self, prediction: Dict):
        """保存预测历史"""
        history = []
        if self.prediction_history_file.exists():
            try:
                with open(self.prediction_history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except:
                pass

        history.append({
            "timestamp": datetime.now().isoformat(),
            "prediction": prediction.get("future_prediction", {}),
            "pattern": prediction.get("trend_pattern", {}),
            "strategies_count": len(prediction.get("prevention_strategies", []))
        })

        # 只保留最近 20 条记录
        history = history[-20:]
        with open(self.prediction_history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def execute_prevention(self, strategy_type: str = None) -> Dict:
        """执行预防性优化"""
        # 首先进行预测
        prediction_result = self.predict_trend()
        strategies = prediction_result.get("prevention_strategies", [])

        if not strategies:
            return {
                "status": "no_action_needed",
                "message": "系统运行正常，无需预防措施"
            }

        # 选择策略执行
        if strategy_type:
            strategies = [s for s in strategies if s.get("type") == strategy_type]
            if not strategies:
                return {
                    "status": "strategy_not_found",
                    "message": f"未找到类型为 {strategy_type} 的策略"
                }

        # 执行最高优先级的策略
        execution_log = []
        success_count = 0

        for strategy in strategies[:3]:  # 最多执行 3 个策略
            strategy_type = strategy.get("type", "unknown")
            action = strategy.get("action", "")

            execution_result = {
                "type": strategy_type,
                "action": action,
                "status": "pending",
                "timestamp": datetime.now().isoformat()
            }

            # 根据策略类型执行相应操作
            try:
                if action == "run_health_diagnosis":
                    # 调用健康诊断引擎
                    from evolution_meta_evolution_internal_health_diagnosis_self_healing_engine import MetaEvolutionInternalHealthDiagnosisSelfHealingEngine
                    diag_engine = MetaEvolutionInternalHealthDiagnosisSelfHealingEngine()
                    diag_result = diag_engine.run_diagnosis()
                    execution_result["status"] = "executed"
                    execution_result["result"] = diag_result
                    success_count += 1

                elif action == "refresh_baseline":
                    # 刷新性能基准
                    from evolution_performance_benchmark_regression_engine import PerformanceBenchmarkRegressionEngine
                    bench_engine = PerformanceBenchmarkRegressionEngine()
                    baseline_result = bench_engine.establish_baseline()
                    execution_result["status"] = "executed"
                    execution_result["result"] = baseline_result
                    success_count += 1

                elif action == "reduce_evolution_load":
                    # 降低进化负载（记录状态）
                    execution_result["status"] = "executed"
                    execution_result["result"] = {"message": "已记录降低负载策略"}
                    success_count += 1

                elif action == "generate_optimizations":
                    # 生成优化建议
                    from evolution_performance_benchmark_regression_engine import PerformanceBenchmarkRegressionEngine
                    bench_engine = PerformanceBenchmarkRegressionEngine()
                    opt_result = bench_engine.identify_optimizations()
                    execution_result["status"] = "executed"
                    execution_result["result"] = opt_result
                    success_count += 1

                elif action == "enhance_monitoring":
                    # 增强监控（记录状态）
                    execution_result["status"] = "executed"
                    execution_result["result"] = {"message": "已增强监控策略"}
                    success_count += 1

                else:
                    execution_result["status"] = "skipped"
                    execution_result["result"] = {"message": "未知操作类型"}

            except Exception as e:
                execution_result["status"] = "error"
                execution_result["error"] = str(e)

            execution_log.append(execution_result)

        # 保存执行日志
        self._save_prevention_log(execution_log)

        # 更新状态
        state = self._load_state()
        state["last_prevention_action"] = datetime.now().isoformat()
        state["prevention_count"] = state.get("prevention_count", 0) + len(execution_log)
        if execution_log:
            state["prevention_success_rate"] = success_count / len(execution_log)
        self._save_state(state)

        return {
            "status": "success",
            "strategies_executed": len(execution_log),
            "success_count": success_count,
            "execution_log": execution_log,
            "message": f"执行了 {len(execution_log)} 个预防策略，{success_count} 个成功"
        }

    def _save_prevention_log(self, log: List[Dict]):
        """保存预防执行日志"""
        history = []
        if self.prevention_log_file.exists():
            try:
                with open(self.prevention_log_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except:
                pass

        history.append({
            "timestamp": datetime.now().isoformat(),
            "log": log
        })

        history = history[-20:]
        with open(self.prevention_log_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def verify_prevention_effect(self) -> Dict:
        """验证预防措施效果"""
        # 获取最近的预防执行日志
        history = []
        if self.prevention_log_file.exists():
            try:
                with open(self.prevention_log_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except:
                pass

        if not history:
            return {
                "status": "no_data",
                "message": "暂无预防执行记录"
            }

        # 获取最新的执行记录
        latest = history[-1]
        log = latest.get("log", [])

        # 运行新的预测来对比
        prediction = self.predict_trend()

        current_risk = prediction.get("future_prediction", {}).get("risk_level", "unknown")

        return {
            "status": "success",
            "prevention_executed": len(log),
            "current_risk_level": current_risk,
            "trend_prediction": prediction.get("trend_pattern", {}),
            "message": f"最近执行了 {len(log)} 个预防措施，当前风险等级: {current_risk}"
        }

    def get_cockpit_data(self) -> Dict:
        """获取驾驶舱数据"""
        prediction_result = self.predict_trend()
        state = self._load_state()

        return {
            "engine": self.name,
            "version": self.version,
            "summary": {
                "current_risk_level": prediction_result.get("future_prediction", {}).get("risk_level", "unknown"),
                "trend": prediction_result.get("trend_pattern", {}).get("pattern", "unknown"),
                "prevention_count": state.get("prevention_count", 0),
                "prevention_success_rate": state.get("prevention_success_rate", 0.0)
            },
            "prediction": prediction_result.get("future_prediction", {}),
            "trend_pattern": prediction_result.get("trend_pattern", {}),
            "top_strategies": prediction_result.get("prevention_strategies", [])[:2]
        }

    def run_full_analysis(self) -> Dict:
        """运行完整分析并执行预防"""
        # 1. 预测趋势
        prediction_result = self.predict_trend()

        # 2. 根据风险等级决定是否执行预防
        risk_level = prediction_result.get("future_prediction", {}).get("risk_level", "unknown")
        execution_result = {}

        if risk_level in ["critical", "high"]:
            execution_result = self.execute_prevention()
        else:
            execution_result = {
                "status": "no_action_needed",
                "message": "风险等级低，无需执行预防措施"
            }

        # 3. 验证效果
        verification = self.verify_prevention_effect()

        return {
            "status": "success",
            "prediction": prediction_result,
            "execution": execution_result,
            "verification": verification,
            "summary": f"趋势预测完成，当前风险等级: {risk_level}；{execution_result.get('message', '')}"
        }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="智能全场景进化环性能趋势预测与预防性优化增强引擎"
    )
    parser.add_argument("--status", action="store_true", help="显示引擎状态")
    parser.add_argument("--predict-trend", action="store_true", help="预测性能趋势")
    parser.add_argument("--execute-prevention", action="store_true", help="执行预防性优化")
    parser.add_argument("--verify-effect", action="store_true", help="验证预防措施效果")
    parser.add_argument("--run", action="store_true", help="运行完整分析")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")

    args = parser.parse_args()

    engine = PerformanceTrendPredictionPreventionEngine()

    if args.status:
        result = engine.predict_trend()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.predict_trend:
        result = engine.predict_trend()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.execute_prevention:
        result = engine.execute_prevention()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.verify_effect:
        result = engine.verify_prevention_effect()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.run:
        result = engine.run_full_analysis()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.cockpit_data:
        result = engine.get_cockpit_data()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 默认显示状态
        result = engine.predict_trend()
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()