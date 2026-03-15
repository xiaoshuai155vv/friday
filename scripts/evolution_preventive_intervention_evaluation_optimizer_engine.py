#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环预防性干预效果评估与持续优化引擎
在 round 526 完成的预防性干预执行基础上，进一步增强干预效果评估与持续优化能力
实现从「执行干预」到「评估效果→持续优化」的范式升级，构建完整的预防性价值管理闭环

Version: 1.0.0
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import statistics


class PreventiveInterventionEvaluationOptimizerEngine:
    """预防性干预效果评估与持续优化引擎"""

    def __init__(self):
        self.runtime_dir = Path(__file__).parent.parent / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.data_dir = self.runtime_dir / "data"
        self.evaluation_data_file = self.data_dir / "intervention_evaluation_data.json"
        self.optimization_log_file = self.data_dir / "intervention_optimization_log.json"
        self.effectiveness_cache_file = self.data_dir / "intervention_effectiveness_cache.json"
        self._ensure_directories()
        self._initialize_data()

    def _ensure_directories(self):
        """确保必要的目录存在"""
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _initialize_data(self):
        """初始化数据文件"""
        if not self.evaluation_data_file.exists():
            with open(self.evaluation_data_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "evaluations": [],
                    "intervention_records": [],
                    "last_updated": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)

        if not self.optimization_log_file.exists():
            with open(self.optimization_log_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "optimizations": [],
                    "last_updated": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)

        if not self.effectiveness_cache_file.exists():
            with open(self.effectiveness_cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "effectiveness_metrics": {},
                    "trend_analysis": {},
                    "last_updated": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)

    def _load_evaluation_data(self) -> Dict:
        """加载评估数据"""
        try:
            with open(self.evaluation_data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"evaluations": [], "intervention_records": []}

    def _save_evaluation_data(self, data: Dict):
        """保存评估数据"""
        data["last_updated"] = datetime.now().isoformat()
        with open(self.evaluation_data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_optimization_log(self) -> Dict:
        """加载优化日志"""
        try:
            with open(self.optimization_log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"optimizations": []}

    def _save_optimization_log(self, data: Dict):
        """保存优化日志"""
        data["last_updated"] = datetime.now().isoformat()
        with open(self.optimization_log_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_effectiveness_cache(self) -> Dict:
        """加载效果缓存"""
        try:
            with open(self.effectiveness_cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"effectiveness_metrics": {}}

    def _save_effectiveness_cache(self, data: Dict):
        """保存效果缓存"""
        data["last_updated"] = datetime.now().isoformat()
        with open(self.effectiveness_cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def evaluate_intervention_effect(self, intervention_id: str, strategy_type: str,
                                     before_metrics: Dict, after_metrics: Dict) -> Dict:
        """
        评估干预效果

        Args:
            intervention_id: 干预ID
            strategy_type: 策略类型
            before_metrics: 干预前指标
            after_metrics: 干预后指标

        Returns:
            评估结果
        """
        evaluation = {
            "intervention_id": intervention_id,
            "strategy_type": strategy_type,
            "timestamp": datetime.now().isoformat(),
            "before_metrics": before_metrics,
            "after_metrics": after_metrics,
            "metrics_change": {},
            "effectiveness_score": 0.0,
            "status": "unknown"
        }

        # 计算指标变化
        for key in before_metrics:
            if key in after_metrics and isinstance(before_metrics[key], (int, float)) and isinstance(after_metrics[key], (int, float)):
                change = after_metrics[key] - before_metrics[key]
                change_pct = (change / before_metrics[key] * 100) if before_metrics[key] != 0 else 0
                evaluation["metrics_change"][key] = {
                    "absolute": change,
                    "percentage": round(change_pct, 2)
                }

        # 计算效果分数
        effectiveness_factors = []
        if "success_rate" in evaluation["metrics_change"]:
            sr_change = evaluation["metrics_change"]["success_rate"].get("percentage", 0)
            effectiveness_factors.append(min(sr_change / 10, 1.0))  # 成功率提升最多10分

        if "efficiency" in evaluation["metrics_change"]:
            eff_change = evaluation["metrics_change"]["efficiency"].get("percentage", 0)
            effectiveness_factors.append(min(eff_change / 10, 1.0))

        if "value_realization" in evaluation["metrics_change"]:
            vr_change = evaluation["metrics_change"]["value_realization"].get("percentage", 0)
            effectiveness_factors.append(min(vr_change / 10, 1.0))

        if effectiveness_factors:
            evaluation["effectiveness_score"] = round(statistics.mean(effectiveness_factors) * 100, 2)

        # 判定状态
        if evaluation["effectiveness_score"] >= 70:
            evaluation["status"] = "highly_effective"
        elif evaluation["effectiveness_score"] >= 40:
            evaluation["status"] = "effective"
        elif evaluation["effectiveness_score"] >= 20:
            evaluation["status"] = "marginally_effective"
        else:
            evaluation["status"] = "ineffective"

        # 保存评估结果
        data = self._load_evaluation_data()
        data["evaluations"].append(evaluation)
        # 只保留最近100条评估
        data["evaluations"] = data["evaluations"][-100:]
        self._save_evaluation_data(data)

        return evaluation

    def analyze_effectiveness_trend(self, time_window_days: int = 30) -> Dict:
        """
        分析效果趋势

        Args:
            time_window_days: 时间窗口（天）

        Returns:
            趋势分析结果
        """
        data = self._load_evaluation_data()
        evaluations = data.get("evaluations", [])

        # 过滤时间窗口内的评估
        cutoff_date = datetime.now() - timedelta(days=time_window_days)
        recent_evaluations = []
        for ev in evaluations:
            try:
                eval_time = datetime.fromisoformat(ev["timestamp"])
                if eval_time >= cutoff_date:
                    recent_evaluations.append(ev)
            except Exception:
                continue

        if not recent_evaluations:
            return {
                "time_window_days": time_window_days,
                "total_evaluations": 0,
                "trend": "no_data",
                "message": "时间窗口内无评估数据"
            }

        # 统计各状态数量
        status_counts = {}
        effectiveness_scores = []
        for ev in recent_evaluations:
            status = ev.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
            effectiveness_scores.append(ev.get("effectiveness_score", 0))

        # 计算平均值和趋势
        avg_effectiveness = statistics.mean(effectiveness_scores) if effectiveness_scores else 0

        # 计算趋势（比较前后半段）
        mid_point = len(recent_evaluations) // 2
        if mid_point > 0:
            first_half_avg = statistics.mean([ev.get("effectiveness_score", 0) for ev in recent_evaluations[:mid_point]])
            second_half_avg = statistics.mean([ev.get("effectiveness_score", 0) for ev in recent_evaluations[mid_point:]])
            if second_half_avg > first_half_avg + 5:
                trend = "improving"
            elif second_half_avg < first_half_avg - 5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"

        return {
            "time_window_days": time_window_days,
            "total_evaluations": len(recent_evaluations),
            "status_counts": status_counts,
            "avg_effectiveness_score": round(avg_effectiveness, 2),
            "trend": trend,
            "highly_effective_count": status_counts.get("highly_effective", 0),
            "effective_count": status_counts.get("effective", 0),
            "ineffective_count": status_counts.get("ineffective", 0),
            "analysis_timestamp": datetime.now().isoformat()
        }

    def generate_optimization_recommendations(self) -> List[Dict]:
        """
        生成优化建议

        Returns:
            优化建议列表
        """
        recommendations = []

        # 分析效果趋势
        trend_analysis = self.analyze_effectiveness_trend(time_window_days=30)

        # 基于趋势生成建议
        if trend_analysis.get("total_evaluations", 0) == 0:
            recommendations.append({
                "type": "data_collection",
                "priority": "high",
                "title": "需要更多干预数据",
                "description": "当前评估数据不足，需要执行更多干预并收集效果数据",
                "action": "执行更多预防性干预并记录效果"
            })
            return recommendations

        # 趋势分析建议
        if trend_analysis.get("trend") == "declining":
            recommendations.append({
                "type": "strategy_adjustment",
                "priority": "high",
                "title": "干预效果下降，需要调整策略",
                "description": f"近30天干预效果呈下降趋势，平均效果分数: {trend_analysis.get('avg_effectiveness_score', 0)}",
                "action": "重新评估现有策略，调整干预参数"
            })

        # 状态分布建议
        status_counts = trend_analysis.get("status_counts", {})
        ineffective_count = status_counts.get("ineffective", 0)
        total = trend_analysis.get("total_evaluations", 1)

        if ineffective_count / total > 0.3:
            recommendations.append({
                "type": "strategy_review",
                "priority": "high",
                "title": "无效干预比例过高",
                "description": f"约 {ineffective_count/total*100:.1f}% 的干预效果不佳",
                "action": "审查无效干预的策略类型，识别问题模式"
            })

        # 高度有效干预识别
        highly_effective = status_counts.get("highly_effective", 0)
        if highly_effective / total > 0.3:
            recommendations.append({
                "type": "best_practice",
                "priority": "medium",
                "title": "发现高效策略",
                "description": f"约 {highly_effective/total*100:.1f}% 的干预效果显著",
                "action": "分析高效干预的特征，推广成功策略"
            })

        # 通用优化建议
        recommendations.append({
            "type": "continuous_optimization",
            "priority": "medium",
            "title": "持续优化机制",
            "description": "基于效果评估结果持续优化干预策略",
            "action": "定期执行效果评估，根据趋势调整策略"
        })

        # 保存优化日志
        optimization_log = self._load_optimization_log()
        optimization_log["optimizations"].append({
            "timestamp": datetime.now().isoformat(),
            "recommendations": recommendations,
            "trend_analysis": trend_analysis
        })
        optimization_log["optimizations"] = optimization_log["optimizations"][-50:]
        self._save_optimization_log(optimization_log)

        return recommendations

    def get_effectiveness_metrics(self) -> Dict:
        """
        获取效果指标

        Returns:
            效果指标
        """
        cache = self._load_effectiveness_cache()
        trend_analysis = self.analyze_effectiveness_trend(time_window_days=30)

        return {
            "current_metrics": cache.get("effectiveness_metrics", {}),
            "trend_analysis": trend_analysis,
            "last_updated": datetime.now().isoformat()
        }

    def record_intervention_execution(self, intervention_id: str, strategy_type: str,
                                      strategy_params: Dict, execution_result: Dict) -> bool:
        """
        记录干预执行

        Args:
            intervention_id: 干预ID
            strategy_type: 策略类型
            strategy_params: 策略参数
            execution_result: 执行结果

        Returns:
            是否成功
        """
        data = self._load_evaluation_data()
        record = {
            "intervention_id": intervention_id,
            "strategy_type": strategy_type,
            "strategy_params": strategy_params,
            "execution_result": execution_result,
            "timestamp": datetime.now().isoformat()
        }
        data["intervention_records"].append(record)
        data["intervention_records"] = data["intervention_records"][-100:]
        self._save_evaluation_data(data)
        return True


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description="预防性干预效果评估与持续优化引擎")
    parser.add_argument("--evaluate", action="store_true", help="评估干预效果")
    parser.add_argument("--intervention-id", type=str, help="干预ID")
    parser.add_argument("--strategy-type", type=str, help="策略类型")
    parser.add_argument("--before-metrics", type=str, help="干预前指标(JSON)")
    parser.add_argument("--after-metrics", type=str, help="干预后指标(JSON)")
    parser.add_argument("--analyze-trend", action="store_true", help="分析效果趋势")
    parser.add_argument("--time-window", type=int, default=30, help="时间窗口(天)")
    parser.add_argument("--recommendations", action="store_true", help="生成优化建议")
    parser.add_argument("--metrics", action="store_true", help="获取效果指标")
    parser.add_argument("--record", action="store_true", help="记录干预执行")
    parser.add_argument("--execution-result", type=str, help="执行结果(JSON)")

    args = parser.parse_args()

    engine = PreventiveInterventionEvaluationOptimizerEngine()

    if args.evaluate:
        if not args.intervention_id or not args.strategy_type:
            print("错误: --intervention-id 和 --strategy-type 是必需参数")
            return

        before_metrics = json.loads(args.before_metrics) if args.before_metrics else {}
        after_metrics = json.loads(args.after_metrics) if args.after_metrics else {}

        result = engine.evaluate_intervention_effect(
            args.intervention_id,
            args.strategy_type,
            before_metrics,
            after_metrics
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.analyze_trend:
        result = engine.analyze_effectiveness_trend(time_window_days=args.time_window)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.recommendations:
        recommendations = engine.generate_optimization_recommendations()
        print(json.dumps(recommendations, ensure_ascii=False, indent=2))

    elif args.metrics:
        metrics = engine.get_effectiveness_metrics()
        print(json.dumps(metrics, ensure_ascii=False, indent=2))

    elif args.record:
        if not args.intervention_id or not args.strategy_type:
            print("错误: --intervention-id 和 --strategy-type 是必需参数")
            return

        result = engine.record_intervention_execution(
            args.intervention_id,
            args.strategy_type,
            {},
            json.loads(args.execution_result) if args.execution_result else {}
        )
        print(f"记录结果: {'成功' if result else '失败'}")

    else:
        # 默认显示效果指标
        metrics = engine.get_effectiveness_metrics()
        print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()