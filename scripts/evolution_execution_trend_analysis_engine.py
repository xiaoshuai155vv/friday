#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环执行效果跨轮对比分析与趋势预测增强引擎

在 round 424 完成的知识驱动自动触发与自优化引擎基础上，进一步增强进化效果的
跨轮对比分析与趋势预测能力。让系统能够自动收集历史进化执行数据、实现跨轮效果
对比分析、生成进化趋势预测报告、基于趋势提供优化建议，形成「数据收集→对比分析→
趋势预测→优化建议→执行优化」的完整闭环。

功能：
1. 历史进化执行数据自动收集与分析
2. 跨轮效果对比（成功率/效率/价值实现）
3. 进化趋势预测（基于历史模式的未来走向）
4. 优化建议生成（基于趋势分析的改进方向）
5. 与进化驾驶舱深度集成（可视化趋势和预测）

集成到 do.py 支持：
- 趋势分析、进化趋势、跨轮对比、趋势预测
- 效果对比、执行对比、轮次对比
- 优化建议、趋势建议、预测建议
"""

import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import statistics

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
STATE_DIR = PROJECT_ROOT / "runtime" / "state"
LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"


class EvolutionExecutionTrendAnalysisEngine:
    """进化环执行效果跨轮对比分析与趋势预测增强引擎"""

    def __init__(self):
        self.state_dir = STATE_DIR
        self.logs_dir = LOGS_DIR
        self.capabilities_file = PROJECT_ROOT / "references" / "capabilities.md"
        self.version = "1.0.0"

    def load_evolution_history(self) -> List[Dict]:
        """加载历史进化数据用于趋势分析"""
        history = []

        # 读取所有完成的进化记录
        for f in self.state_dir.glob("evolution_completed_*.json"):
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    if isinstance(data, dict) and 'loop_round' in data:
                        history.append(data)
            except Exception as e:
                print(f"Warning: Failed to load {f}: {e}")

        # 按轮次排序（从旧到新）
        history.sort(key=lambda x: x.get('loop_round', 0))
        return history

    def load_recent_logs(self) -> List[Dict]:
        """加载最近的日志数据"""
        recent_logs_file = self.state_dir / "recent_logs.json"
        if recent_logs_file.exists():
            try:
                with open(recent_logs_file, 'r', encoding='utf-8') as fp:
                    return json.load(fp)
            except Exception as e:
                print(f"Warning: Failed to load recent_logs: {e}")
        return []

    def analyze_cross_round_comparison(self, history: List[Dict]) -> Dict[str, Any]:
        """跨轮效果对比分析"""
        if len(history) < 2:
            return {
                "status": "insufficient_data",
                "message": "需要至少2轮进化数据才能进行跨轮对比",
                "comparisons": []
            }

        comparisons = []
        total_rounds = len(history)

        # 对相邻轮次进行对比
        for i in range(1, min(total_rounds, 50)):  # 最多对比最近50轮
            prev_round = history[i - 1]
            curr_round = history[i]

            prev_goal = prev_round.get('current_goal', 'Unknown')
            curr_goal = curr_round.get('current_goal', 'Unknown')
            prev_status = prev_round.get('status', 'unknown')
            curr_status = curr_round.get('status', 'unknown')

            comparison = {
                "round_comparison": f"round {prev_round.get('loop_round')} vs round {curr_round.get('loop_round')}",
                "prev_goal": prev_goal,
                "curr_goal": curr_goal,
                "prev_status": prev_status,
                "curr_status": curr_status,
                "status_change": "improved" if (curr_status == "completed" and prev_status == "failed") else
                                 "declined" if (curr_status == "failed" and prev_status == "completed") else
                                 "stable"
            }
            comparisons.append(comparison)

        # 统计分析
        status_changes = [c['status_change'] for c in comparisons]
        improved_count = status_changes.count('improved')
        declined_count = status_changes.count('declined')
        stable_count = status_changes.count('stable')

        # 计算连续成功/失败
        consecutive_success = 0
        consecutive_failure = 0
        max_consecutive_success = 0
        max_consecutive_failure = 0

        for round_data in history:
            status = round_data.get('status', 'unknown')
            if status == 'completed':
                consecutive_success += 1
                consecutive_failure = 0
                max_consecutive_success = max(max_consecutive_success, consecutive_success)
            elif status == 'failed':
                consecutive_failure += 1
                consecutive_success = 0
                max_consecutive_failure = max(max_consecutive_failure, consecutive_failure)
            else:
                consecutive_success = 0
                consecutive_failure = 0

        return {
            "status": "success",
            "total_rounds_analyzed": total_rounds,
            "total_comparisons": len(comparisons),
            "improved_count": improved_count,
            "declined_count": declined_count,
            "stable_count": stable_count,
            "max_consecutive_success": max_consecutive_success,
            "max_consecutive_failure": max_consecutive_failure,
            "trend_direction": "improving" if improved_count > declined_count else
                               "declining" if declined_count > improved_count else "stable",
            "comparisons": comparisons[-10:]  # 最近10次对比
        }

    def analyze_efficiency_trend(self, history: List[Dict]) -> Dict[str, Any]:
        """分析执行效率趋势"""
        if not history:
            return {"status": "no_data", "efficiency_trend": "unknown"}

        # 简化的效率分析 - 基于完成率
        # 将历史分成多个时间段进行对比
        periods = []
        period_size = 10
        for i in range(0, len(history), period_size):
            period_data = history[i:i + period_size]
            completed = sum(1 for r in period_data if r.get('status') == 'completed')
            period = {
                "rounds": f"{period_data[0].get('loop_round', '?')}-{period_data[-1].get('loop_round', '?')}",
                "total": len(period_data),
                "completed": completed,
                "completion_rate": completed / len(period_data) if period_data else 0
            }
            periods.append(period)

        # 计算整体趋势
        if len(periods) >= 2:
            recent_rate = periods[-1].get('completion_rate', 0)
            earlier_rate = periods[0].get('completion_rate', 0)

            if recent_rate > earlier_rate + 0.1:
                efficiency_trend = "improving"
            elif recent_rate < earlier_rate - 0.1:
                efficiency_trend = "declining"
            else:
                efficiency_trend = "stable"
        else:
            efficiency_trend = "stable"
            if history:
                completed = sum(1 for r in history if r.get('status') == 'completed')
                efficiency_trend = "improving" if completed / len(history) > 0.7 else "stable"

        return {
            "status": "success",
            "efficiency_trend": efficiency_trend,
            "periods": periods,
            "average_completion_rate": sum(p['completion_rate'] for p in periods) / len(periods) if periods else 0
        }

    def analyze_value_realization_trend(self, history: List[Dict]) -> Dict[str, Any]:
        """分析价值实现趋势"""
        if not history:
            return {"status": "no_data", "value_trend": "unknown"}

        # 分析每轮是否有价值实现相关的记录
        value_realized_rounds = []
        for round_data in history:
            goal = round_data.get('current_goal', '')
            if '价值' in goal or 'value' in goal.lower():
                value_realized_rounds.append(round_data.get('loop_round', 0))

        # 计算价值实现频率
        value_frequency = len(value_realized_rounds) / len(history) if history else 0

        # 趋势分析
        if len(value_realized_rounds) >= 2:
            # 检查价值实现是否越来越频繁
            recent_value_rounds = [r for r in value_realized_rounds if r >= history[-5].get('loop_round', 0)]
            earlier_value_rounds = [r for r in value_realized_rounds if r < history[5].get('loop_round', 0)] if len(history) > 10 else []

            if len(recent_value_rounds) > len(earlier_value_rounds):
                value_trend = "increasing"
            elif len(recent_value_rounds) < len(earlier_value_rounds):
                value_trend = "decreasing"
            else:
                value_trend = "stable"
        else:
            value_trend = "stable" if value_frequency > 0 else "no_value_rounds"

        return {
            "status": "success",
            "value_trend": value_trend,
            "value_realization_rounds": value_realized_rounds[-10:] if value_realized_rounds else [],
            "value_frequency": value_frequency,
            "total_value_rounds": len(value_realized_rounds)
        }

    def predict_future_trend(self, history: List[Dict]) -> Dict[str, Any]:
        """预测未来进化趋势"""
        if len(history) < 5:
            return {
                "prediction": "insufficient_data",
                "confidence": 0,
                "message": "数据不足，无法进行趋势预测"
            }

        # 分析最近的趋势
        recent_history = history[-10:] if len(history) >= 10 else history
        recent_completed = sum(1 for r in recent_history if r.get('status') == 'completed')
        recent_success_rate = recent_completed / len(recent_history) if recent_history else 0

        # 计算趋势斜率（简化的线性趋势）
        success_rates = []
        period_size = 5
        for i in range(0, len(history), period_size):
            period = history[i:i + period_size]
            completed = sum(1 for r in period if r.get('status') == 'completed')
            success_rates.append(completed / len(period) if period else 0)

        # 简化的斜率计算
        if len(success_rates) >= 2:
            trend_slope = (success_rates[-1] - success_rates[0]) / len(success_rates)
        else:
            trend_slope = 0

        # 基于斜率预测
        if trend_slope > 0.05:
            prediction = "strongly_improving"
            confidence = 0.8
        elif trend_slope > 0:
            prediction = "slightly_improving"
            confidence = 0.6
        elif trend_slope < -0.05:
            prediction = "strongly_declining"
            confidence = 0.8
        elif trend_slope < 0:
            prediction = "slightly_declining"
            confidence = 0.6
        else:
            prediction = "stable"
            confidence = 0.7

        return {
            "prediction": prediction,
            "confidence": confidence,
            "trend_slope": trend_slope,
            "recent_success_rate": recent_success_rate,
            "message": f"基于{len(history)}轮历史数据分析，预测未来趋势为{prediction}"
        }

    def generate_optimization_suggestions(self, history: List[Dict]) -> List[Dict]:
        """基于趋势分析生成优化建议"""
        suggestions = []

        # 1. 分析连续失败
        max_consecutive_failure = 0
        current_consecutive_failure = 0
        failure_rounds = []

        for round_data in history:
            status = round_data.get('status', 'unknown')
            if status == 'failed':
                current_consecutive_failure += 1
                max_consecutive_failure = max(max_consecutive_failure, current_consecutive_failure)
                failure_rounds.append(round_data.get('loop_round', 0))
            else:
                current_consecutive_failure = 0

        if max_consecutive_failure >= 3:
            suggestions.append({
                "type": "failure_pattern",
                "priority": "high",
                "issue": f"发现{max_consecutive_failure}轮连续失败",
                "suggestion": "建议暂停自动进化，执行系统健康检查，诊断失败原因后再继续",
                "action": "run_health_check"
            })

        # 2. 分析效率趋势
        efficiency = self.analyze_efficiency_trend(history)
        if efficiency.get('efficiency_trend') == 'declining':
            suggestions.append({
                "type": "efficiency_decline",
                "priority": "medium",
                "issue": "进化效率呈下降趋势",
                "suggestion": "建议分析效率下降原因，可能需要优化执行策略或减少并发任务",
                "action": "optimize_strategy"
            })

        # 3. 分析重复进化
        module_counts = defaultdict(int)
        for round_data in history:
            goal = round_data.get('current_goal', '')
            # 提取模块名（简化）
            module_name = goal.split('：')[0] if '：' in goal else goal.split(':')[0] if ':' in goal else goal[:20]
            module_counts[module_name] += 1

        repeated = {k: v for k, v in module_counts.items() if v >= 2}
        if repeated:
            suggestions.append({
                "type": "repeated_evolution",
                "priority": "low",
                "issue": f"发现重复进化模式: {len(repeated)}个模块被多次进化",
                "suggestion": "建议合并相似进化任务，避免重复开发",
                "action": "merge_tasks"
            })

        # 4. 如果状态良好，生成增强建议
        if not suggestions:
            suggestions.append({
                "type": "positive_status",
                "priority": "low",
                "issue": "系统状态良好",
                "suggestion": "可继续探索新的进化方向，增强系统能力",
                "action": "explore_new_directions"
            })

        return suggestions

    def analyze_and_predict(self) -> Dict[str, Any]:
        """完整的跨轮对比分析和趋势预测"""
        # 1. 加载历史数据
        history = self.load_evolution_history()

        # 2. 执行各项分析
        cross_round = self.analyze_cross_round_comparison(history)
        efficiency = self.analyze_efficiency_trend(history)
        value_trend = self.analyze_value_realization_trend(history)
        prediction = self.predict_future_trend(history)
        suggestions = self.generate_optimization_suggestions(history)

        # 3. 综合分析
        overall_health = "good"
        if cross_round.get('max_consecutive_failure', 0) >= 3:
            overall_health = "needs_attention"
        elif efficiency.get('efficiency_trend') == 'declining':
            overall_health = "warning"

        return {
            "status": "success",
            "version": self.version,
            "overall_health": overall_health,
            "total_history_rounds": len(history),
            "cross_round_analysis": cross_round,
            "efficiency_trend": efficiency,
            "value_trend": value_trend,
            "prediction": prediction,
            "suggestions": suggestions,
            "timestamp": datetime.now().isoformat()
        }

    def compare_specific_rounds(self, round1: int, round2: int) -> Dict[str, Any]:
        """对比指定的两轮进化"""
        history = self.load_evolution_history()

        round1_data = None
        round2_data = None

        for h in history:
            if h.get('loop_round') == round1:
                round1_data = h
            if h.get('loop_round') == round2:
                round2_data = h

        if not round1_data or not round2_data:
            return {
                "status": "error",
                "message": f"未找到 round {round1} 或 round {round2} 的数据"
            }

        comparison = {
            "round1": round1_data.get('loop_round'),
            "round2": round2_data.get('loop_round'),
            "round1_goal": round1_data.get('current_goal'),
            "round2_goal": round2_data.get('current_goal'),
            "round1_status": round1_data.get('status'),
            "round2_status": round2_data.get('status'),
            "round1_action": round1_data.get('做了什么', 'N/A'),
            "round2_action": round2_data.get('做了什么', 'N/A'),
            "status_comparison": "improved" if (round2_data.get('status') == 'completed' and round1_data.get('status') == 'failed') else
                                 "declined" if (round2_data.get('status') == 'failed' and round1_data.get('status') == 'completed') else
                                 "similar"
        }

        return {
            "status": "success",
            "comparison": comparison
        }

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取用于进化驾驶舱展示的数据"""
        analysis = self.analyze_and_predict()

        # 提取关键指标用于可视化
        return {
            "status": "success",
            "version": self.version,
            "overall_health": analysis.get('overall_health', 'unknown'),
            "total_rounds": analysis.get('total_history_rounds', 0),
            "efficiency_trend": analysis.get('efficiency_trend', {}).get('efficiency_trend', 'unknown'),
            "value_trend": analysis.get('value_trend', {}).get('value_trend', 'unknown'),
            "prediction": analysis.get('prediction', {}).get('prediction', 'unknown'),
            "confidence": analysis.get('prediction', {}).get('confidence', 0),
            "top_suggestions": analysis.get('suggestions', [])[:3],
            "timestamp": analysis.get('timestamp')
        }

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        history = self.load_evolution_history()
        analysis = self.analyze_and_predict()

        return {
            "name": "进化环执行效果跨轮对比分析与趋势预测增强引擎",
            "version": self.version,
            "status": "active",
            "total_history_rounds": len(history),
            "overall_health": analysis.get('overall_health', 'unknown'),
            "capabilities": [
                "跨轮效果对比分析",
                "执行效率趋势分析",
                "价值实现趋势分析",
                "未来趋势预测",
                "优化建议生成",
                "进化驾驶舱数据提供"
            ]
        }


def main():
    """主函数 - 支持命令行调用"""
    import sys

    engine = EvolutionExecutionTrendAnalysisEngine()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command in ["analyze", "分析", "趋势分析"]:
            result = engine.analyze_and_predict()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return

        elif command in ["predict", "预测", "趋势预测"]:
            history = engine.load_evolution_history()
            result = engine.predict_future_trend(history)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return

        elif command in ["compare", "对比", "比较"]:
            if len(sys.argv) >= 4:
                try:
                    r1 = int(sys.argv[2])
                    r2 = int(sys.argv[3])
                    result = engine.compare_specific_rounds(r1, r2)
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                except ValueError:
                    print("Error: 请提供有效的轮次数字")
            else:
                print("Usage: python evolution_execution_trend_analysis_engine.py compare <round1> <round2>")
            return

        elif command in ["cockpit", "驾驶舱", "可视化"]:
            result = engine.get_cockpit_data()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return

        elif command in ["suggestions", "建议", "优化建议"]:
            history = engine.load_evolution_history()
            result = engine.generate_optimization_suggestions(history)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return

        elif command in ["status", "状态"]:
            result = engine.get_status()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return

        elif command in ["help", "帮助"]:
            help_text = """
进化环执行效果跨轮对比分析与趋势预测增强引擎 (v1.0.0)

用法:
  python evolution_execution_trend_analysis_engine.py <command>

命令:
  analyze / 分析 / 趋势分析
    - 执行完整的跨轮对比分析和趋势预测
    - 返回对比分析、效率趋势、价值趋势、预测结果、优化建议

  predict / 预测 / 趋势预测
    - 仅执行趋势预测
    - 返回预测结果和置信度

  compare <round1> <round2> / 对比 <round1> <round2>
    - 对比指定的两轮进化
    - 返回两轮的详细信息和对比结果

  cockpit / 驾驶舱 / 可视化
    - 获取用于进化驾驶舱展示的数据
    - 返回简化的关键指标

  suggestions / 建议 / 优化建议
    - 基于趋势分析生成优化建议
    - 返回可执行的改进建议

  status / 状态
    - 获取引擎当前状态
    - 返回版本、历史轮次、能力列表

  help / 帮助
    - 显示此帮助信息
"""
            print(help_text)
            return

    # 默认返回状态
    result = engine.get_status()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()