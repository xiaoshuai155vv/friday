#!/usr/bin/env python3
"""
智能系统自省与元认知引擎
让系统具备自我审视、自我分析能力，主动发现进化策略中的问题和优化机会，实现真正的元进化（对进化的进化）。

功能：
1. 系统整体健康状态分析（引擎活跃度、能力覆盖、执行效率）
2. 进化瓶颈识别（发现哪些进化方向被忽视、哪些能力重复建设）
3. 进化策略有效性评估（分析历史进化决策的效果）
4. 生成自我优化建议报告
"""

import os
import json
import glob
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict

# 项目根目录
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"


def get_recent_logs(days: int = 7) -> List[Dict]:
    """获取最近的行为日志"""
    logs = []
    cutoff = datetime.now() - timedelta(days=days)

    log_files = glob.glob(str(LOGS_DIR / "behavior_*.log"))
    for log_file in log_files:
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        # 尝试解析 JSON 行
                        entry = json.loads(line)
                        if isinstance(entry, dict) and 'time' in entry:
                            entry_time = datetime.fromisoformat(entry['time'].replace('+00:00', ''))
                            if entry_time >= cutoff:
                                logs.append(entry)
                    except json.JSONDecodeError:
                        continue
        except Exception:
            continue

    return sorted(logs, key=lambda x: x.get('time', ''), reverse=True)


def get_evolution_history() -> List[Dict]:
    """获取进化历史"""
    history = []

    # 读取 evolution_completed_*.json 文件
    completed_files = glob.glob(str(STATE_DIR / "evolution_completed_*.json"))
    for file_path in completed_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                history.append(data)
        except Exception:
            continue

    return sorted(history, key=lambda x: x.get('loop_round', 0), reverse=True)


def get_engine_count() -> int:
    """统计引擎数量（scripts 目录下的 py 文件）"""
    scripts_dir = PROJECT_ROOT / "scripts"
    engine_files = []

    # 查找各种引擎文件
    patterns = ['*_engine.py', '*_orchestrator.py', '*_manager.py', '*_tool.py',
                '*_analyzer.py', '*_generator.py', '*_learner.py', '*_optimizer.py']
    for pattern in patterns:
        engine_files.extend(glob.glob(str(scripts_dir / pattern)))

    return len(set(engine_files))


def get_capabilities_summary() -> Dict[str, Any]:
    """获取能力摘要"""
    capabilities_file = PROJECT_ROOT / "references" / "capabilities.md"

    if not capabilities_file.exists():
        return {"total": 0, "categories": {}}

    try:
        with open(capabilities_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 简单统计能力数量
        lines = content.split('\n')
        total = 0
        categories = defaultdict(int)

        for line in lines:
            if line.startswith('|') and '--' not in line:
                parts = line.split('|')
                if len(parts) >= 3:
                    total += 1

        return {"total": total, "categories": dict(categories)}
    except Exception:
        return {"total": 0, "categories": {}}


def analyze_system_health() -> Dict[str, Any]:
    """分析系统整体健康状态"""
    health = {
        "timestamp": datetime.now().isoformat(),
        "engine_count": get_engine_count(),
        "evolution_rounds": 0,
        "recent_activity": {"total": 0, "by_phase": defaultdict(int)},
        "capabilities": get_capabilities_summary(),
        "status": "healthy",
        "issues": []
    }

    # 获取进化历史
    history = get_evolution_history()
    health["evolution_rounds"] = len(history)
    health["latest_round"] = history[0] if history else None

    # 分析近期活动
    logs = get_recent_logs(days=7)
    health["recent_activity"]["total"] = len(logs)

    for log in logs:
        phase = log.get('phase', 'unknown')
        health["recent_activity"]["by_phase"][phase] += 1

    # 检查潜在问题
    if health["engine_count"] < 30:
        health["issues"].append("引擎数量较少，可能需要更多能力建设")

    if len(history) < 50:
        health["issues"].append("进化历史较短，进化策略有效性数据不足")

    return health


def identify_evolution_bottlenecks() -> Dict[str, Any]:
    """识别进化瓶颈"""
    bottlenecks = {
        "timestamp": datetime.now().isoformat(),
        "identified": [],
        "suggestions": []
    }

    # 分析进化历史，识别被忽视的方向
    history = get_evolution_history()

    # 统计各 round 的主题
    themes = defaultdict(int)
    for item in history:
        goal = item.get('current_goal', '')
        if goal:
            # 提取关键词
            keywords = ['引擎', '学习', '优化', '推荐', '预测', '协同', '自动化',
                       '知识', '工作流', '自省', '元认知']
            for kw in keywords:
                if kw in goal:
                    themes[kw] += 1

    # 识别可能的瓶颈
    if themes.get('自省', 0) + themes.get('元认知', 0) == 0:
        bottlenecks["identified"].append("缺少系统自我审视和元认知能力")
        bottlenecks["suggestions"].append("创建智能系统自省与元认知引擎，实现自我分析和优化")

    if themes.get('多模态', 0) < 2:
        bottlenecks["identified"].append("多模态感知能力可能不足")
        bottlenecks["suggestions"].append("增强视觉、语音等多模态感知能力")

    # 检查是否有重复建设的迹象
    recent_goals = [h.get('current_goal', '') for h in history[:10]]
    if len(set(recent_goals)) < len(recent_goals) * 0.7:
        bottlenecks["identified"].append("近期进化方向可能有重复")
        bottlenecks["suggestions"].append("审视最近10轮进化，确保方向不重复")

    # 能力覆盖检查
    caps = get_capabilities_summary()
    if caps["total"] < 100:
        bottlenecks["identified"].append("能力覆盖还不够全面")
        bottlenecks["suggestions"].append("继续扩展能力覆盖，特别是用户常用场景")

    return bottlenecks


def evaluate_evolution_strategy() -> Dict[str, Any]:
    """评估进化策略有效性"""
    evaluation = {
        "timestamp": datetime.now().isoformat(),
        "metrics": {},
        "effectiveness": "unknown",
        "insights": []
    }

    history = get_evolution_history()

    if len(history) < 5:
        evaluation["effectiveness"] = "insufficient_data"
        evaluation["insights"].append("进化历史较短，无法充分评估策略有效性")
        return evaluation

    # 分析完成率
    completed = sum(1 for h in history if h.get('status') == 'completed')
    total = len(history)
    completion_rate = completed / total if total > 0 else 0

    evaluation["metrics"]["completion_rate"] = completion_rate
    evaluation["metrics"]["total_rounds"] = total

    # 分析每轮的平均执行时间（如果有记录的话）
    # 这里简化为分析日志条数
    logs = get_recent_logs(days=7)
    phase_counts = defaultdict(int)
    for log in logs:
        phase_counts[log.get('phase', 'unknown')] += 1

    evaluation["metrics"]["recent_activity"] = dict(phase_counts)

    # 给出洞察
    if completion_rate >= 0.8:
        evaluation["effectiveness"] = "high"
        evaluation["insights"].append("进化完成率高，策略执行有效")
    elif completion_rate >= 0.5:
        evaluation["effectiveness"] = "medium"
        evaluation["insights"].append("进化完成率中等，部分策略可能需要调整")
    else:
        evaluation["effectiveness"] = "low"
        evaluation["insights"].append("进化完成率较低，需要审视目标设定和执行策略")

    # 检查进化是否有明确的连续性
    recent_rounds = [h.get('loop_round', 0) for h in history[:10]]
    if all(recent_rounds[i] - recent_rounds[i+1] == 1 for i in range(len(recent_rounds)-1)):
        evaluation["insights"].append("进化轮次连续性好，没有明显中断")
    else:
        evaluation["insights"].append("进化轮次存在中断，可能需要检查定时触发器")

    return evaluation


def generate_self_optimization_report() -> Dict[str, Any]:
    """生成自我优化建议报告"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": "",
        "health": None,
        "bottlenecks": None,
        "strategy": None,
        "recommendations": []
    }

    # 获取各项分析
    health = analyze_system_health()
    bottlenecks = identify_evolution_bottlenecks()
    strategy = evaluate_evolution_strategy()

    report["health"] = health
    report["bottlenecks"] = bottlenecks
    report["strategy"] = strategy

    # 生成综合建议
    recommendations = []

    # 基于健康状态
    for issue in health.get("issues", []):
        recommendations.append(f"健康问题: {issue}")

    # 基于瓶颈识别
    for suggestion in bottlenecks.get("suggestions", []):
        recommendations.append(f"瓶颈建议: {suggestion}")

    # 基于策略评估
    for insight in strategy.get("insights", []):
        recommendations.append(f"策略洞察: {insight}")

    report["recommendations"] = recommendations

    # 生成摘要
    report["summary"] = f"系统当前有 {health['engine_count']} 个引擎，已完成 {health['evolution_rounds']} 轮进化，策略有效性评估为 {strategy['effectiveness']}。建议优先处理瓶颈问题以提升系统能力。"

    return report


def reflect(analysis_type: str = "full") -> str:
    """
    执行系统自省

    Args:
        analysis_type: 分析类型 (full/health/bottlenecks/strategy/recommendations)
    """
    if analysis_type == "health":
        result = analyze_system_health()
    elif analysis_type == "bottlenecks":
        result = identify_evolution_bottlenecks()
    elif analysis_type == "strategy":
        result = evaluate_evolution_strategy()
    elif analysis_type == "recommendations":
        result = generate_self_optimization_report()
    else:  # full
        result = generate_self_optimization_report()

    return json.dumps(result, ensure_ascii=False, indent=2)


def main():
    """CLI 入口"""
    import sys

    if len(sys.argv) < 2:
        print(reflect("full"))
        return

    command = sys.argv[1].lower()

    if command in ["health", "bottlenecks", "strategy", "recommendations", "full"]:
        print(reflect(command))
    elif command == "--help" or command == "-h":
        print(__doc__)
        print("\n用法:")
        print("  python system_self_reflection_engine.py [command]")
        print("\n命令:")
        print("  health           - 系统健康状态分析")
        print("  bottlenecks      - 进化瓶颈识别")
        print("  strategy         - 进化策略有效性评估")
        print("  recommendations  - 生成自我优化建议报告")
        print("  full             - 完整分析（默认）")
    else:
        print(f"未知命令: {command}")
        print("使用 --help 查看帮助")


if __name__ == "__main__":
    main()