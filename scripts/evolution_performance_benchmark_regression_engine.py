#!/usr/bin/env python3
"""
智能全场景进化环自动化性能基准测试与回归检测引擎
version 1.0.0

让系统能够追踪进化环自身的执行效率变化、自动发现性能回归、预测优化机会，
实现从被动响应性能问题到主动预防的范式升级。

功能：
1. 性能基准自动建立 - 基于历史数据建立性能基准
2. 回归自动检测 - 自动检测性能回归
3. 性能趋势预测 - 预测未来性能趋势
4. 优化机会智能识别 - 识别可优化点
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


class PerformanceBenchmarkRegressionEngine:
    """自动化性能基准测试与回归检测引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.name = "PerformanceBenchmarkRegressionEngine"
        self.state_file = RUNTIME_STATE_DIR / "performance_benchmark_state.json"
        self.benchmark_data_file = RUNTIME_STATE_DIR / "performance_benchmark_data.json"
        self.regression_history_file = RUNTIME_STATE_DIR / "regression_detection_history.json"
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
            "last_baseline_update": None,
            "baseline_metrics": {},
            "regression_count": 0,
            "optimization_opportunities": []
        }

    def _save_state(self, state: Dict):
        """保存引擎状态"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def _load_evolution_history(self) -> List[Dict]:
        """加载进化历史数据"""
        history = []
        # 从 evolution_completed_*.json 文件中收集
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
        # 按时间排序
        history.sort(key=lambda x: x.get('completed_at', ''), reverse=True)
        return history

    def _collect_performance_metrics(self) -> Dict[str, Any]:
        """收集当前性能指标"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "total_engines": 0,
            "total_rounds": 0,
            "recent_rounds": 0,
            "baseline_metrics": {},
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
            # 计算平均执行时间（如果可用）
            total_time = 0
            count = 0
            for h in recent_history:
                if 'execution_time' in h:
                    total_time += h.get('execution_time', 0)
                    count += 1
            if count > 0:
                metrics["execution_metrics"]["avg_execution_time"] = total_time / count

            # 计算成功率
            success_count = sum(1 for h in recent_history if h.get('status') == 'completed')
            metrics["execution_metrics"]["success_rate"] = success_count / len(recent_history) if recent_history else 0

        return metrics

    def _establish_baseline(self, metrics: Dict) -> Dict:
        """建立性能基准"""
        state = self._load_state()

        # 更新基准指标
        state["baseline_metrics"] = {
            "total_engines": metrics.get("total_engines", 0),
            "total_rounds": metrics.get("total_rounds", 0),
            "success_rate": metrics.get("execution_metrics", {}).get("success_rate", 1.0),
            "avg_execution_time": metrics.get("execution_metrics", {}).get("avg_execution_time", 0),
            "established_at": datetime.now().isoformat()
        }
        state["last_baseline_update"] = datetime.now().isoformat()

        return state

    def _detect_regression(self, current_metrics: Dict) -> List[Dict]:
        """检测性能回归"""
        state = self._load_state()
        regressions = []
        baseline = state.get("baseline_metrics", {})

        if not baseline:
            return regressions

        # 检测成功率回归
        current_success_rate = current_metrics.get("execution_metrics", {}).get("success_rate", 1.0)
        baseline_success_rate = baseline.get("success_rate", 1.0)
        if current_success_rate < baseline_success_rate * 0.9:  # 下降超过 10%
            regressions.append({
                "type": "success_rate_degradation",
                "severity": "high" if current_success_rate < baseline_success_rate * 0.8 else "medium",
                "current_value": current_success_rate,
                "baseline_value": baseline_success_rate,
                "degradation_percent": (baseline_success_rate - current_success_rate) / baseline_success_rate * 100,
                "timestamp": datetime.now().isoformat()
            })

        # 检测执行时间回归
        current_avg_time = current_metrics.get("execution_metrics", {}).get("avg_execution_time", 0)
        baseline_avg_time = baseline.get("avg_execution_time", 0)
        if baseline_avg_time > 0 and current_avg_time > baseline_avg_time * 1.2:  # 增加超过 20%
            regressions.append({
                "type": "execution_time_increase",
                "severity": "high" if current_avg_time > baseline_avg_time * 1.5 else "medium",
                "current_value": current_avg_time,
                "baseline_value": baseline_avg_time,
                "increase_percent": (current_avg_time - baseline_avg_time) / baseline_avg_time * 100,
                "timestamp": datetime.now().isoformat()
            })

        # 检测引擎数量变化
        current_engines = current_metrics.get("total_engines", 0)
        baseline_engines = baseline.get("total_engines", 0)
        if current_engines < baseline_engines:
            regressions.append({
                "type": "engine_count_decrease",
                "severity": "medium",
                "current_value": current_engines,
                "baseline_value": baseline_engines,
                "decrease_count": baseline_engines - current_engines,
                "timestamp": datetime.now().isoformat()
            })

        return regressions

    def _predict_trend(self) -> Dict:
        """预测性能趋势"""
        history = self._load_evolution_history()

        if len(history) < 3:
            return {"trend": "insufficient_data", "prediction": "需要更多数据才能进行趋势预测"}

        # 简化趋势分析：基于最近历史的表现
        recent = history[:5]
        older = history[5:10] if len(history) > 5 else []

        trend_analysis = {
            "based_on_rounds": len(recent),
            "recent_success_rate": 0,
            "older_success_rate": 0,
            "trend": "stable",
            "prediction": "系统运行稳定"
        }

        if recent:
            recent_success = sum(1 for h in recent if h.get('status') == 'completed')
            trend_analysis["recent_success_rate"] = recent_success / len(recent)

        if older:
            older_success = sum(1 for h in older if h.get('status') == 'completed')
            trend_analysis["older_success_rate"] = older_success / len(older)

        # 计算趋势
        if trend_analysis["recent_success_rate"] > trend_analysis["older_success_rate"] * 1.1:
            trend_analysis["trend"] = "improving"
            trend_analysis["prediction"] = "系统性能正在改善"
        elif trend_analysis["recent_success_rate"] < trend_analysis["older_success_rate"] * 0.9:
            trend_analysis["trend"] = "declining"
            trend_analysis["prediction"] = "系统性能有下降趋势，建议关注"
        else:
            trend_analysis["trend"] = "stable"
            trend_analysis["prediction"] = "系统运行稳定"

        return trend_analysis

    def _identify_optimization_opportunities(self) -> List[Dict]:
        """识别优化机会"""
        opportunities = []
        state = self._load_state()
        history = self._load_evolution_history()

        # 基于历史数据分析优化机会
        if len(history) >= 5:
            # 检测重复失败
            failed_rounds = [h for h in history if h.get('status') != 'completed']
            if len(failed_rounds) > 3:
                opportunities.append({
                    "type": "high_failure_rate",
                    "description": f"最近 {len(failed_rounds)} 轮存在失败记录，建议分析失败原因",
                    "priority": "high",
                    "suggested_action": "运行诊断引擎分析失败原因"
                })

            # 检测长时间未完成的 rounds
            pending = [h for h in history if h.get('status') == 'pending']
            if len(pending) > 2:
                opportunities.append({
                    "type": "pending_rounds",
                    "description": f"存在 {len(pending)} 个待处理的进化轮次",
                    "priority": "medium",
                    "suggested_action": "检查待处理任务并继续执行"
                })

        # 基于基准检测优化机会
        baseline = state.get("baseline_metrics", {})
        if baseline:
            current_metrics = self._collect_performance_metrics()
            regressions = self._detect_regression(current_metrics)
            if regressions:
                opportunities.append({
                    "type": "performance_regression",
                    "description": f"检测到 {len(regressions)} 个性能回归问题",
                    "priority": "high",
                    "details": regressions,
                    "suggested_action": "运行回归分析并采取纠正措施"
                })

        return opportunities

    def status(self) -> Dict:
        """获取引擎状态"""
        state = self._load_state()
        current_metrics = self._collect_performance_metrics()
        regressions = self._detect_regression(current_metrics)
        opportunities = self._identify_optimization_opportunities()

        return {
            "engine": self.name,
            "version": self.version,
            "state": state,
            "current_metrics": current_metrics,
            "regressions_detected": len(regressions),
            "regressions": regressions[:3],  # 只返回前 3 个
            "optimization_opportunities": len(opportunities),
            "opportunities": opportunities[:3]
        }

    def establish_baseline(self) -> Dict:
        """建立性能基准"""
        metrics = self._collect_performance_metrics()
        state = self._establish_baseline(metrics)
        self._save_state(state)

        return {
            "status": "success",
            "message": "性能基准已建立",
            "baseline": state["baseline_metrics"]
        }

    def detect_regression(self) -> Dict:
        """检测性能回归"""
        current_metrics = self._collect_performance_metrics()
        regressions = self._detect_regression(current_metrics)

        # 记录检测历史
        history = []
        if self.regression_history_file.exists():
            try:
                with open(self.regression_history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except:
                pass

        history.append({
            "timestamp": datetime.now().isoformat(),
            "regressions_count": len(regressions),
            "regressions": regressions
        })

        # 只保留最近 20 条记录
        history = history[-20:]
        with open(self.regression_history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

        # 更新状态
        state = self._load_state()
        state["regression_count"] = len(regressions)
        self._save_state(state)

        return {
            "status": "success",
            "regressions_detected": len(regressions),
            "regressions": regressions,
            "message": f"检测到 {len(regressions)} 个性能回归问题" if regressions else "未检测到性能回归"
        }

    def predict_trend(self) -> Dict:
        """预测性能趋势"""
        trend = self._predict_trend()
        return {
            "status": "success",
            "trend": trend
        }

    def identify_optimizations(self) -> Dict:
        """识别优化机会"""
        opportunities = self._identify_optimization_opportunities()

        # 保存到状态
        state = self._load_state()
        state["optimization_opportunities"] = opportunities
        self._save_state(state)

        return {
            "status": "success",
            "optimization_opportunities": len(opportunities),
            "opportunities": opportunities
        }

    def run_full_analysis(self) -> Dict:
        """运行完整分析"""
        # 1. 建立基准
        baseline_result = self.establish_baseline()

        # 2. 检测回归
        regression_result = self.detect_regression()

        # 3. 预测趋势
        trend_result = self.predict_trend()

        # 4. 识别优化机会
        optimization_result = self.identify_optimizations()

        return {
            "status": "success",
            "baseline": baseline_result,
            "regressions": regression_result,
            "trend": trend_result,
            "optimizations": optimization_result,
            "summary": f"分析了 {regression_result['regressions_detected']} 个回归问题，识别出 {optimization_result['optimization_opportunities']} 个优化机会"
        }

    def get_cockpit_data(self) -> Dict:
        """获取驾驶舱数据"""
        status = self.status()
        trend = self._predict_trend()

        return {
            "engine": self.name,
            "version": self.version,
            "summary": {
                "regressions_detected": status["regressions_detected"],
                "optimization_opportunities": status["optimization_opportunities"],
                "trend": trend.get("trend", "unknown")
            },
            "baseline": status["state"].get("baseline_metrics", {}),
            "current_metrics": status["current_metrics"],
            "recent_regressions": status["regressions"][:2],
            "top_opportunities": status["opportunities"][:2] if status.get("opportunities") else []
        }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="智能全场景进化环自动化性能基准测试与回归检测引擎"
    )
    parser.add_argument("--status", action="store_true", help="显示引擎状态")
    parser.add_argument("--establish-baseline", action="store_true", help="建立性能基准")
    parser.add_argument("--detect-regression", action="store_true", help="检测性能回归")
    parser.add_argument("--predict-trend", action="store_true", help="预测性能趋势")
    parser.add_argument("--identify-optimizations", action="store_true", help="识别优化机会")
    parser.add_argument("--run", action="store_true", help="运行完整分析")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")

    args = parser.parse_args()

    engine = PerformanceBenchmarkRegressionEngine()

    if args.status:
        result = engine.status()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.establish_baseline:
        result = engine.establish_baseline()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.detect_regression:
        result = engine.detect_regression()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.predict_trend:
        result = engine.predict_trend()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.identify_optimizations:
        result = engine.identify_optimizations()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.run:
        result = engine.run_full_analysis()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.cockpit_data:
        result = engine.get_cockpit_data()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 默认显示状态
        result = engine.status()
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()