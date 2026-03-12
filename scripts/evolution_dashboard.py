#!/usr/bin/env python3
"""
进化环可视化监控面板
实时展示进化状态、各模块健康度、历史趋势
让进化环的运行更加透明可控
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

# 添加 scripts 目录到路径
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

# 项目根目录
PROJECT = os.path.dirname(SCRIPTS_DIR)

# 定义路径常量
RUNTIME_DIR = os.path.join(PROJECT, "runtime")
STATE_DIR = os.path.join(RUNTIME_DIR, "state")
LOGS_DIR = os.path.join(RUNTIME_DIR, "logs")

# 进化环相关文件路径
EVOLUTION_STATE_FILE = os.path.join(STATE_DIR, "current_mission.json")
EVOLUTION_AUTO_LAST = os.path.join(PROJECT, "references/evolution_auto_last.md")
SELF_VERIFY_RESULT = os.path.join(STATE_DIR, "self_verify_result.json")
EVOLUTION_HISTORY_DB = os.path.join(STATE_DIR, "evolution_history.db")

# 各模块状态文件
MODULE_STATE_FILES = {
    "strategy_engine": os.path.join(STATE_DIR, "evolution_strategy_output.json"),
    "log_analyzer": os.path.join(STATE_DIR, "evolution_analysis.json"),
    "self_evaluator": os.path.join(STATE_DIR, "evolution_self_evaluation.json"),
    "loop_automation": os.path.join(STATE_DIR, "evolution_automation_status.json"),
    "history_db": EVOLUTION_HISTORY_DB,
    "learning_engine": os.path.join(STATE_DIR, "evolution_learning_output.json"),
    "coordinator": os.path.join(STATE_DIR, "evolution_coordinator_status.json"),
    "scheduler": os.path.join(STATE_DIR, "evolution_scheduler_state.json"),
}


def get_current_mission() -> Dict[str, Any]:
    """获取当前任务状态"""
    if os.path.exists(EVOLUTION_STATE_FILE):
        try:
            with open(EVOLUTION_STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {"phase": "unknown", "loop_round": 0, "current_goal": "unknown"}


def get_module_status(module_name: str) -> Dict[str, Any]:
    """获取单个模块的状态"""
    state_file = MODULE_STATE_FILES.get(module_name)
    if state_file and os.path.exists(state_file):
        try:
            if state_file.endswith('.db'):
                # SQLite 数据库需要特殊处理
                return {"exists": True, "type": "database"}
            with open(state_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if content.strip():
                    data = json.loads(content)
                    return {"exists": True, "status": "ok", "data": data}
                else:
                    return {"exists": True, "status": "empty"}
        except Exception as e:
            return {"exists": True, "status": "error", "message": str(e)}
    return {"exists": False, "status": "not_found"}


def get_all_modules_health() -> Dict[str, Any]:
    """获取所有模块的健康状态"""
    modules = {
        "策略引擎": "strategy_engine",
        "日志分析": "log_analyzer",
        "自我评估": "self_evaluator",
        "闭环自动化": "loop_automation",
        "历史数据库": "history_db",
        "学习引擎": "learning_engine",
        "协调器": "coordinator",
        "调度器": "scheduler",
    }

    health_status = {}
    healthy_count = 0
    total_count = len(modules)

    for display_name, module_key in modules.items():
        status = get_module_status(module_key)
        if status.get("exists") and status.get("status") in ["ok", "empty"]:
            health_status[display_name] = "[OK] 健康"
            healthy_count += 1
        elif status.get("exists"):
            health_status[display_name] = "[WARN] 异常"
            healthy_count += 1
        else:
            health_status[display_name] = "[X] 未找到"

    return {
        "modules": health_status,
        "healthy_count": healthy_count,
        "total_count": total_count,
        "health_score": round(healthy_count / total_count * 100, 1) if total_count > 0 else 0
    }


def get_recent_evolution_rounds(count: int = 10) -> List[Dict[str, Any]]:
    """获取最近的进化轮次"""
    rounds = []

    # 读取 evolution_auto_last.md 获取历史
    if os.path.exists(EVOLUTION_AUTO_LAST):
        try:
            with open(EVOLUTION_AUTO_LAST, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                current_round = {}

                for line in lines:
                    if line.startswith('## 2026-03-12 round '):
                        if current_round:
                            rounds.append(current_round)
                        round_num = line.replace('## 2026-03-12 round ', '').strip()
                        current_round = {"round": round_num, "goal": "", "status": ""}
                    elif line.startswith('- **current_goal**：') and current_round:
                        current_round["goal"] = line.replace('- **current_goal**：', '').strip()
                    elif line.startswith('- **是否完成**：') and current_round:
                        current_round["status"] = line.replace('- **是否完成**：', '').strip()

                if current_round:
                    rounds.append(current_round)
        except Exception:
            pass

    return rounds[-count:] if rounds else []


def get_evolution_statistics() -> Dict[str, Any]:
    """获取进化统计数据"""
    stats = {
        "total_rounds": 0,
        "completed_rounds": 0,
        "success_rate": 0,
        "recent_trend": "stable"
    }

    rounds = get_recent_evolution_rounds(20)
    stats["total_rounds"] = len(rounds)

    completed = sum(1 for r in rounds if r.get("status") == "已完成")
    stats["completed_rounds"] = completed

    if rounds:
        stats["success_rate"] = round(completed / len(rounds) * 100, 1)

    # 计算近期趋势
    if len(rounds) >= 5:
        recent_completed = sum(1 for r in rounds[-5:] if r.get("status") == "已完成")
        if recent_completed >= 4:
            stats["recent_trend"] = "improving"
        elif recent_completed <= 2:
            stats["recent_trend"] = "declining"
        else:
            stats["recent_trend"] = "stable"

    return stats


def get_self_verify_result() -> Optional[Dict[str, Any]]:
    """获取基线校验结果"""
    if os.path.exists(SELF_VERIFY_RESULT):
        try:
            with open(SELF_VERIFY_RESULT, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return None


def generate_dashboard_json() -> Dict[str, Any]:
    """生成完整的仪表板数据"""
    mission = get_current_mission()
    modules_health = get_all_modules_health()
    recent_rounds = get_recent_evolution_rounds()
    stats = get_evolution_statistics()
    verify_result = get_self_verify_result()

    dashboard = {
        "generated_at": datetime.now().isoformat(),
        "current_mission": {
            "round": mission.get("loop_round", 0),
            "phase": mission.get("phase", "unknown"),
            "goal": mission.get("current_goal", "待定"),
            "next_action": mission.get("next_action", "")
        },
        "modules_health": modules_health,
        "statistics": stats,
        "recent_rounds": recent_rounds,
        "baseline_verify": {
            "status": verify_result.get("overall_status", "unknown") if verify_result else "unknown",
            "passed": verify_result.get("passed_count", 0) if verify_result else 0,
            "total": verify_result.get("total_count", 0) if verify_result else 0
        }
    }

    return dashboard


def print_dashboard(dashboard: Dict[str, Any]):
    """打印仪表板到控制台"""
    print("\n" + "=" * 60)
    print("           进化环可视化监控面板")
    print("=" * 60)

    # 当前任务
    mission = dashboard.get("current_mission", {})
    print(f"\n[当前状态] (Round {mission.get('round', 0)})")
    print(f"   阶段: {mission.get('phase', 'unknown')}")
    print(f"   目标: {mission.get('goal', 'N/A')[:50]}...")

    # 模块健康度
    health = dashboard.get("modules_health", {})
    print(f"\n[模块健康度] (健康得分: {health.get('health_score', 0)}%)")
    print(f"   健康: {health.get('healthy_count', 0)}/{health.get('total_count', 0)}")

    modules = health.get("modules", {})
    for name, status in modules.items():
        print(f"   {name}: {status}")

    # 统计
    stats = dashboard.get("statistics", {})
    print(f"\n[进化统计]")
    print(f"   总轮次: {stats.get('total_rounds', 0)}")
    print(f"   已完成: {stats.get('completed_rounds', 0)}")
    print(f"   成功率: {stats.get('success_rate', 0)}%")
    print(f"   近期趋势: {stats.get('recent_trend', 'unknown')}")

    # 最近轮次
    recent = dashboard.get("recent_rounds", [])
    if recent:
        print(f"\n[最近进化轮次]")
        for r in recent[-5:]:
            status_icon = "OK" if r.get("status") == "已完成" else "?"
            goal = r.get("goal", "N/A")[:30]
            print(f"   Round {r.get('round', '?')}: {status_icon} {goal}...")

    # 基线校验
    verify = dashboard.get("baseline_verify", {})
    print(f"\n[基线校验]")
    print(f"   状态: {verify.get('status', 'unknown')}")
    print(f"   通过: {verify.get('passed', 0)}/{verify.get('total', 0)}")

    print("\n" + "=" * 60)
    print(f"数据生成时间: {dashboard.get('generated_at', '')}")
    print("=" * 60 + "\n")


def export_dashboard_json(output_file: Optional[str] = None):
    """导出仪表板数据到 JSON 文件"""
    if output_file is None:
        output_file = os.path.join(STATE_DIR, "evolution_dashboard.json")

    dashboard = generate_dashboard_json()

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dashboard, f, ensure_ascii=False, indent=2)

    return output_file


def export_dashboard_markdown(output_file: Optional[str] = None):
    """导出仪表板数据到 Markdown 文件"""
    if output_file is None:
        output_file = os.path.join(STATE_DIR, "evolution_dashboard.md")

    dashboard = generate_dashboard_json()

    md_content = "# 进化环监控面板\n\n"
    md_content += f"**生成时间**: {dashboard.get('generated_at', '')}\n\n"

    # 当前任务
    mission = dashboard.get("current_mission", {})
    md_content += f"## 当前状态 (Round {mission.get('round', 0)})\n\n"
    md_content += f"- **阶段**: {mission.get('phase', 'unknown')}\n"
    md_content += f"- **目标**: {mission.get('goal', 'N/A')}\n"
    md_content += f"- **下一步**: {mission.get('next_action', 'N/A')}\n\n"

    # 模块健康度
    health = dashboard.get("modules_health", {})
    md_content += f"## 模块健康度 (得分: {health.get('health_score', 0)}%)\n\n"
    md_content += f"健康模块: {health.get('healthy_count', 0)}/{health.get('total_count', 0)}\n\n"

    modules = health.get("modules", {})
    for name, status in modules.items():
        md_content += f"- {name}: {status}\n"
    md_content += "\n"

    # 统计
    stats = dashboard.get("statistics", {})
    md_content += "## 进化统计\n\n"
    md_content += f"- 总轮次: {stats.get('total_rounds', 0)}\n"
    md_content += f"- 已完成: {stats.get('completed_rounds', 0)}\n"
    md_content += f"- 成功率: {stats.get('success_rate', 0)}%\n"
    md_content += f"- 近期趋势: {stats.get('recent_trend', 'unknown')}\n\n"

    # 最近轮次
    recent = dashboard.get("recent_rounds", [])
    if recent:
        md_content += "## 最近进化轮次\n\n"
        for r in recent[-10:]:
            status_icon = "✓" if r.get("status") == "已完成" else "○"
            md_content += f"- Round {r.get('round', '?')}: {status_icon} {r.get('goal', 'N/A')}\n"
        md_content += "\n"

    # 基线校验
    verify = dashboard.get("baseline_verify", {})
    md_content += "## 基线校验\n\n"
    md_content += f"- 状态: {verify.get('status', 'unknown')}\n"
    md_content += f"- 通过: {verify.get('passed', 0)}/{verify.get('total', 0)}\n\n"

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)

    return output_file


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="进化环可视化监控面板")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    parser.add_argument("--markdown", action="store_true", help="输出 Markdown 格式")
    parser.add_argument("--export-json", nargs="?", const="default", help="导出 JSON 文件 (可选指定路径)")
    parser.add_argument("--export-markdown", nargs="?", const="default", help="导出 Markdown 文件 (可选指定路径)")
    parser.add_argument("--auto", action="store_true", help="自动模式：持续更新显示")

    args = parser.parse_args()

    dashboard = generate_dashboard_json()

    if args.export_json is not None:
        if args.export_json == "default":
            output_file = os.path.join(STATE_DIR, "evolution_dashboard.json")
        else:
            output_file = args.export_json
        export_dashboard_json(output_file)
        print(f"JSON 已导出到: {output_file}")

    if args.export_markdown is not None:
        if args.export_markdown == "default":
            output_file = os.path.join(STATE_DIR, "evolution_dashboard.md")
        else:
            output_file = args.export_markdown
        export_dashboard_markdown(output_file)
        print(f"Markdown 已导出到: {output_file}")

    if args.json:
        print(json.dumps(dashboard, ensure_ascii=False, indent=2))
    elif args.markdown:
        print(export_dashboard_markdown())
    else:
        print_dashboard(dashboard)

        if args.auto:
            print("自动模式：每 30 秒更新一次 (Ctrl+C 退出)")
            try:
                while True:
                    time.sleep(30)
                    dashboard = generate_dashboard_json()
                    print("\033[2J\033[H")  # 清屏
                    print_dashboard(dashboard)
            except KeyboardInterrupt:
                print("\n退出自动模式")


if __name__ == "__main__":
    main()