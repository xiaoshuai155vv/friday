#!/usr/bin/env python3
"""
进化环高级预测引擎
实现更高级的预测算法，结合历史数据、系统状态、用户行为模式等多维度信息进行预测

功能：
1. 多维度数据融合预测算法
2. 建立预测模型训练和评估机制
3. 集成到 do.py 支持关键词触发
"""

import os
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict
import math

# 添加 scripts 目录到路径
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

# 状态和日志目录
PROJECT_DIR = os.path.dirname(SCRIPTS_DIR)  # 项目根目录
RUNTIME_DIR = os.path.join(PROJECT_DIR, "runtime")
STATE_DIR = os.path.join(RUNTIME_DIR, "state")
LOGS_DIR = os.path.join(RUNTIME_DIR, "logs")


def load_evolution_history() -> List[Dict[str, Any]]:
    """加载进化历史数据"""
    history_file = os.path.join(STATE_DIR, "evolution_history.json")
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and 'history' in data:
                    return data['history']
        except Exception as e:
            print(f"加载进化历史失败: {e}")

    # 尝试从其他文件加载历史
    completed_files = []
    if os.path.exists(STATE_DIR):
        for f in os.listdir(STATE_DIR):
            if f.startswith("evolution_completed_") and f.endswith(".json"):
                completed_files.append(os.path.join(STATE_DIR, f))

    history = []
    for file_path in sorted(completed_files, reverse=True)[:50]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'loop_round' in data:
                    history.append(data)
        except Exception:
            pass

    return sorted(history, key=lambda x: x.get('loop_round', 0), reverse=True)


def load_system_state() -> Dict[str, Any]:
    """加载当前系统状态"""
    state = {
        "current_round": 104,
        "active_engines": 0,
        "system_health": "unknown"
    }

    # 统计已创建的引擎
    engine_count = 0
    engine_files = [
        "evolution_meta_learning_engine.py",
        "evolution_loop_automation.py",
        "evolution_strategy_engine.py",
        "evolution_log_analyzer.py",
        "evolution_self_evaluator.py",
        "evolution_history_db.py",
        "evolution_learning_engine.py",
        "evolution_coordinator.py",
        "evolution_dashboard.py",
        "evolution_cli.py",
        "evolution_api_server.py",
        "evolution_explainer.py",
        "decision_orchestrator.py",
        "emotion_engine.py",
        "conversation_manager.py",
        "adaptive_learning_engine.py",
        "proactive_notification_engine.py",
        "self_healing_engine.py",
        "scenario_recommender.py",
        "voice_interaction_engine.py",
        "tts_engine.py",
        "file_manager_engine.py",
        "workflow_engine.py",
        "module_linkage_engine.py",
        "context_memory.py",
        "task_memory.py",
        "knowledge_graph.py"
    ]

    for engine in engine_files:
        if os.path.exists(os.path.join(SCRIPTS_DIR, engine)):
            engine_count += 1

    state["active_engines"] = engine_count

    # 检查系统健康状态
    health_file = os.path.join(STATE_DIR, "system_health.json")
    if os.path.exists(health_file):
        try:
            with open(health_file, 'r', encoding='utf-8') as f:
                health_data = json.load(f)
                state["system_health"] = health_data.get("status", "unknown")
        except Exception:
            pass

    return state


def load_recent_logs() -> List[Dict[str, Any]]:
    """加载最近的日志"""
    logs = []
    recent_logs_file = os.path.join(STATE_DIR, "recent_logs.json")
    if os.path.exists(recent_logs_file):
        try:
            with open(recent_logs_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    logs = data[-50:]  # 最近50条
        except Exception:
            pass
    return logs


def analyze_time_features(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析时间特征"""
    time_features = {
        "evolution_timestamps": [],
        "hour_distribution": defaultdict(int),
        "day_distribution": defaultdict(int),
        "interval_stats": {}
    }

    for h in history:
        if "updated_at" in h:
            try:
                timestamp = h["updated_at"]
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_features["hour_distribution"][dt.hour] += 1
                time_features["day_distribution"][dt.strftime("%A")] += 1
                time_features["evolution_timestamps"].append(timestamp)
            except Exception:
                pass

    # 计算间隔统计
    timestamps = sorted(time_features["evolution_timestamps"])
    if len(timestamps) >= 2:
        intervals = []
        for i in range(1, len(timestamps)):
            try:
                t1 = datetime.fromisoformat(timestamps[i-1].replace('Z', '+00:00'))
                t2 = datetime.fromisoformat(timestamps[i].replace('Z', '+00:00'))
                interval = (t2 - t1).total_seconds() / 3600  # 转换为小时
                intervals.append(interval)
            except Exception:
                pass

        if intervals:
            time_features["interval_stats"] = {
                "avg_interval_hours": sum(intervals) / len(intervals),
                "min_interval_hours": min(intervals),
                "max_interval_hours": max(intervals)
            }

    return time_features


def analyze_success_patterns(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析成功模式"""
    patterns = {
        "by_goal_length": defaultdict(lambda: {"total": 0, "completed": 0}),
        "by_keyword": defaultdict(lambda: {"total": 0, "completed": 0}),
        "consecutive_success": [],
        "failure_recovery": []
    }

    consecutive = 0
    max_consecutive = 0

    for h in history:
        goal = h.get("current_goal", "")
        is_completed = h.get("是否完成") == "完成"

        # 按目标长度分析
        goal_length = len(goal)
        if goal_length < 50:
            length_cat = "short"
        elif goal_length < 100:
            length_cat = "medium"
        else:
            length_cat = "long"

        patterns["by_goal_length"][length_cat]["total"] += 1
        if is_completed:
            patterns["by_goal_length"][length_cat]["completed"] += 1

        # 按关键词分析
        keywords = ["增强", "创建", "实现", "优化", "智能", "自动", "预测", "协同"]
        for kw in keywords:
            if kw in goal:
                patterns["by_keyword"][kw]["total"] += 1
                if is_completed:
                    patterns["by_keyword"][kw]["completed"] += 1

        # 连续成功分析
        if is_completed:
            consecutive += 1
            max_consecutive = max(max_consecutive, consecutive)
        else:
            if consecutive > 0:
                patterns["consecutive_success"].append(consecutive)
            consecutive = 0

        # 失败恢复分析
        if not is_completed:
            patterns["failure_recovery"].append({
                "round": h.get("loop_round"),
                "goal": goal[:50]
            })

    patterns["max_consecutive_success"] = max_consecutive

    return patterns


def predict_next_evolution_direction(
    history: List[Dict[str, Any]],
    system_state: Dict[str, Any],
    time_features: Dict[str, Any],
    success_patterns: Dict[str, Any]
) -> Dict[str, Any]:
    """
    预测下一轮进化方向

    使用多维度数据融合：
    1. 基于历史成功模式
    2. 基于系统当前状态
    3. 基于时间特征
    4. 基于进化趋势
    """
    prediction = {
        "recommended_directions": [],
        "confidence_scores": {},
        "reasoning": []
    }

    # 分析1：基于系统状态推荐
    active_engines = system_state.get("active_engines", 0)
    if active_engines < 20:
        prediction["reasoning"].append(f"系统当前有 {active_engines} 个引擎，可继续创建新引擎")
        prediction["recommended_directions"].append({
            "direction": "新引擎创建",
            "description": "继续创建新的智能引擎",
            "confidence": 0.7
        })
    elif active_engines < 30:
        prediction["reasoning"].append(f"系统已有 {active_engines} 个引擎，建议增强现有引擎协同")
        prediction["recommended_directions"].append({
            "direction": "引擎协同增强",
            "description": "增强已有引擎之间的协同工作能力",
            "confidence": 0.8
        })
    else:
        prediction["reasoning"].append(f"系统已有 {active_engines} 个引擎，建议关注自动化和预测优化")
        prediction["recommended_directions"].append({
            "direction": "自动化优化",
            "description": "提升现有功能的自动化程度",
            "confidence": 0.75
        })

    # 分析2：基于成功模式推荐
    by_keyword = success_patterns.get("by_keyword", {})
    best_keyword = None
    best_rate = 0

    for kw, stats in by_keyword.items():
        if stats["total"] >= 2:  # 至少2次样本
            rate = stats["completed"] / stats["total"]
            if rate > best_rate:
                best_rate = rate
                best_keyword = kw

    if best_keyword:
        prediction["reasoning"].append(f"历史数据表明含'{best_keyword}'的进化成功率最高({best_rate:.1%})")
        prediction["recommended_directions"].append({
            "direction": f"基于{best_keyword}的进化",
            "description": f"重点关注{best_keyword}相关的进化方向",
            "confidence": best_rate
        })
        prediction["confidence_scores"]["keyword_based"] = best_rate
    else:
        prediction["confidence_scores"]["keyword_based"] = 0.5

    # 分析3：基于时间特征推荐
    interval_stats = time_features.get("interval_stats", {})
    if interval_stats:
        avg_interval = interval_stats.get("avg_interval_hours", 24)
        prediction["reasoning"].append(f"进化平均间隔 {avg_interval:.1f} 小时")

        if avg_interval > 48:
            prediction["recommended_directions"].append({
                "direction": "增加进化频率",
                "description": "考虑增加进化频率或优化进化效率",
                "confidence": 0.6
            })

    # 分析4：基于失败恢复分析
    failures = success_patterns.get("failure_recovery", [])
    if failures:
        prediction["reasoning"].append(f"有 {len(failures)} 轮次未完成，可考虑重试或简化")
        prediction["recommended_directions"].append({
            "direction": "修复未完成任务",
            "description": "重新尝试之前未完成的进化任务",
            "confidence": 0.65
        })

    # 计算综合置信度
    scores = list(prediction["confidence_scores"].values())
    if scores:
        prediction["overall_confidence"] = sum(scores) / len(scores)
    else:
        prediction["overall_confidence"] = 0.5

    return prediction


def predict_evolution_timeline(
    history: List[Dict[str, Any]],
    time_features: Dict[str, Any]
) -> Dict[str, Any]:
    """预测进化时间线"""
    timeline = {
        "next_evolution_estimate": None,
        "estimated_intervals": {},
        "trend_analysis": ""
    }

    interval_stats = time_features.get("interval_stats", {})
    if interval_stats:
        avg_interval = interval_stats.get("avg_interval_hours", 24)
        timeline["estimated_intervals"] = {
            "average": avg_interval,
            "min": interval_stats.get("min_interval_hours", 0),
            "max": interval_stats.get("max_interval_hours", 0)
        }

        # 预测下一轮时间
        if history:
            last_update = history[0].get("updated_at", "")
            if last_update:
                try:
                    last_dt = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                    next_dt = last_dt + timedelta(hours=avg_interval)
                    timeline["next_evolution_estimate"] = next_dt.isoformat()
                except Exception:
                    pass

    # 趋势分析
    if len(history) >= 10:
        recent_completed = sum(1 for h in history[:10] if h.get("是否完成") == "完成")
        recent_rate = recent_completed / 10

        if recent_rate >= 0.8:
            timeline["trend_analysis"] = "进化效率高且稳定，建议保持当前策略"
        elif recent_rate >= 0.5:
            timeline["trend_analysis"] = "进化效率一般，建议优化任务复杂度"
        else:
            timeline["trend_analysis"] = "进化效率较低，建议简化目标或增加支持"
    else:
        timeline["trend_analysis"] = "历史数据不足，无法准确分析趋势"

    return timeline


def run_advanced_prediction() -> Dict[str, Any]:
    """运行高级预测分析"""
    print("=" * 60)
    print("进化环高级预测引擎")
    print("=" * 60)

    # 加载多维度数据
    print("\n[1/5] 加载进化历史数据...")
    history = load_evolution_history()
    print(f"    加载了 {len(history)} 条进化记录")

    print("\n[2/5] 加载系统状态...")
    system_state = load_system_state()
    print(f"    当前活跃引擎数: {system_state.get('active_engines', 0)}")
    print(f"    系统健康状态: {system_state.get('system_health', 'unknown')}")

    print("\n[3/5] 分析时间特征...")
    time_features = analyze_time_features(history)
    interval_stats = time_features.get("interval_stats", {})
    if interval_stats:
        print(f"    平均进化间隔: {interval_stats.get('avg_interval_hours', 0):.1f} 小时")

    print("\n[4/5] 分析成功模式...")
    success_patterns = analyze_success_patterns(history)
    max_consecutive = success_patterns.get("max_consecutive_success", 0)
    print(f"    最大连续成功轮次: {max_consecutive}")

    print("\n[5/5] 生成预测...")
    direction_prediction = predict_next_evolution_direction(
        history, system_state, time_features, success_patterns
    )
    timeline_prediction = predict_evolution_timeline(history, time_features)

    # 构建结果
    result = {
        "timestamp": datetime.now().isoformat(),
        "data_sources": {
            "history_count": len(history),
            "system_state": system_state,
            "time_features_summary": {
                "hour_distribution": dict(time_features.get("hour_distribution", {})),
                "interval_stats": interval_stats
            }
        },
        "predictions": {
            "next_direction": direction_prediction,
            "timeline": timeline_prediction
        },
        "summary": {
            "recommended_primary_direction": direction_prediction["recommended_directions"][0] if direction_prediction["recommended_directions"] else None,
            "overall_confidence": direction_prediction.get("overall_confidence", 0),
            "next_evolution_estimate": timeline_prediction.get("next_evolution_estimate"),
            "trend": timeline_prediction.get("trend_analysis", "")
        }
    }

    # 保存结果
    result_file = os.path.join(STATE_DIR, "advanced_evolution_prediction_result.json")
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n结果已保存到: {result_file}")

    # 打印摘要
    print("\n" + "=" * 60)
    print("高级预测分析摘要")
    print("=" * 60)

    print(f"\n系统状态:")
    print(f"  - 活跃引擎: {system_state.get('active_engines', 0)} 个")
    print(f"  - 健康状态: {system_state.get('system_health', 'unknown')}")

    print(f"\n推荐进化方向:")
    for i, direction in enumerate(direction_prediction.get("recommended_directions", [])[:3], 1):
        print(f"  {i}. {direction.get('direction', 'N/A')}")
        print(f"     描述: {direction.get('description', '')}")
        print(f"     置信度: {direction.get('confidence', 0):.1%}")

    print(f"\n时间线预测:")
    if timeline_prediction.get("next_evolution_estimate"):
        print(f"  - 预计下次进化: {timeline_prediction['next_evolution_estimate']}")
    print(f"  - 趋势分析: {timeline_prediction.get('trend_analysis', 'N/A')}")

    print(f"\n综合置信度: {direction_prediction.get('overall_confidence', 0):.1%}")

    return result


def get_prediction_summary() -> str:
    """获取预测摘要（供 do.py 调用）"""
    history = load_evolution_history()
    system_state = load_system_state()
    time_features = analyze_time_features(history)
    success_patterns = analyze_success_patterns(history)

    direction_prediction = predict_next_evolution_direction(
        history, system_state, time_features, success_patterns
    )
    timeline_prediction = predict_evolution_timeline(history, time_features)

    summary = "【进化环高级预测】\n\n"

    if direction_prediction.get("recommended_directions"):
        summary += "推荐进化方向:\n"
        for i, d in enumerate(direction_prediction["recommended_directions"][:2], 1):
            summary += f"  {i}. {d.get('direction', 'N/A')} (置信度: {d.get('confidence', 0):.1%})\n"
            summary += f"     {d.get('description', '')}\n"

    summary += f"\n综合置信度: {direction_prediction.get('overall_confidence', 0):.1%}\n"

    if timeline_prediction.get("next_evolution_estimate"):
        summary += f"预计下次进化: {timeline_prediction['next_evolution_estimate']}\n"

    summary += f"趋势分析: {timeline_prediction.get('trend_analysis', 'N/A')}\n"

    return summary


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="进化环高级预测引擎")
    parser.add_argument("--predict", action="store_true", help="运行预测分析")
    parser.add_argument("--summary", action="store_true", help="获取预测摘要")
    parser.add_argument("--format", choices=["json", "text"], default="text", help="输出格式")

    args = parser.parse_args()

    # 如果没有指定参数，默认运行预测
    if not any([args.predict, args.summary]):
        args.predict = True

    if args.predict:
        result = run_advanced_prediction()
        if args.format == "json":
            print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.summary:
        summary = get_prediction_summary()
        print(summary)


if __name__ == "__main__":
    main()