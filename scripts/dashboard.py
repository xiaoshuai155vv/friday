#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进化环状态仪表板 - 整合系统状态、趋势分析、告警信息、健康检查等

功能：
- 统一展示系统各模块状态
- 显示进化环进度和当前阶段
- 汇总趋势分析和告警信息
- 提供交互式状态查询

触发方式：
  python scripts/dashboard.py [--full]
  do 状态面板 / 系统状态 / 进化状态 / dashboard
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

STATE_DIR = os.path.join(PROJECT_ROOT, "runtime", "state")
LOGS_DIR = os.path.join(PROJECT_ROOT, "runtime", "logs")


def safe_print(text):
    """安全打印，处理编码问题"""
    try:
        print(text)
    except UnicodeEncodeError:
        import re
        text_no_emoji = re.sub(r'[\U0001F300-\U0001F9FF]', '', text)
        print(text_no_emoji)


def load_json(filepath, default=None):
    """安全加载 JSON 文件"""
    if not os.path.exists(filepath):
        return default
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def format_time(iso_time):
    """格式化 ISO 时间"""
    if not iso_time:
        return "N/A"
    try:
        dt = datetime.fromisoformat(iso_time.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return iso_time


def load_current_mission():
    """加载当前任务状态"""
    return load_json(os.path.join(STATE_DIR, "current_mission.json"), {})


def load_health_report():
    """加载健康报告"""
    return load_json(os.path.join(STATE_DIR, "health_report.json"), {})


def load_trend_predictions():
    """加载趋势预测"""
    return load_json(os.path.join(STATE_DIR, "trend_predictions.json"), {})


def load_alert_config():
    """加载告警配置"""
    return load_json(os.path.join(STATE_DIR, "alert_config.json"), {})


def load_alert_history():
    """加载告警历史"""
    return load_json(os.path.join(STATE_DIR, "alert_history.json"), [])


def load_task_status():
    """加载任务状态"""
    return load_json(os.path.join(STATE_DIR, "task_status.json"), {})


def load_recent_logs():
    """加载最近日志"""
    return load_json(os.path.join(STATE_DIR, "recent_logs.json"), {})


def load_execution_analysis():
    """加载执行分析"""
    return load_json(os.path.join(STATE_DIR, "execution_analysis.json"), {})


def load_failure_predictions():
    """加载失败预测"""
    return load_json(os.path.join(STATE_DIR, "failure_predictions.json"), {})


def build_header():
    """构建仪表板头部"""
    mission = load_current_mission()
    loop_round = mission.get("loop_round", "N/A")
    phase = mission.get("phase", "N/A")
    current_goal = mission.get("current_goal", "N/A")
    updated_at = mission.get("updated_at", "")

    header = f"""
╔══════════════════════════════════════════════════════════════════╗
║               星期五进化环状态仪表板                              ║
╠══════════════════════════════════════════════════════════════════╣
║  循环轮次: Round {loop_round}                                            ║
║  当前阶段: {phase:<47} ║
║  更新时间: {format_time(updated_at):<43} ║
╚══════════════════════════════════════════════════════════════════╝
"""
    return header


def build_health_section():
    """构建健康检查部分"""
    health = load_health_report()
    if not health:
        return "【系统健康】暂无数据，请运行 system_health_check.py"

    status = health.get("status", "unknown")
    check_time = health.get("check_time", "")
    components = health.get("components", [])

    status_icon = "✓" if status == "healthy" else "✗"
    status_text = "健康" if status == "healthy" else "异常"

    section = f"""
【系统健康】{status_icon} {status_text} | 检查时间: {format_time(check_time)}
─────────────────────────────────────────────────────────────────
"""
    for comp in components:
        comp_name = comp.get("component", "Unknown")
        comp_status = comp.get("status", "unknown")
        comp_msg = comp.get("message", "")
        icon = "✓" if comp_status == "healthy" else "✗"
        section += f"  {icon} {comp_name}: {comp_msg}\n"

    return section


def build_evolution_section():
    """构建进化环进度部分"""
    mission = load_current_mission()

    loop_round = mission.get("loop_round", "N/A")
    phase = mission.get("phase", "N/A")
    next_action = mission.get("next_action", "N/A")

    section = f"""
【进化环进度】
─────────────────────────────────────────────────────────────────
  轮次: Round {loop_round}
  阶段: {phase}
  下一步: {next_action}
"""
    return section


def build_trend_section():
    """构建趋势分析部分"""
    trends = load_trend_predictions()
    if not trends:
        return "【趋势分析】暂无数据，请运行 trend_predictor.py"

    predictions = trends.get("predictions", [])
    analysis = trends.get("analysis", {})

    section = "【趋势分析】\n─────────────────────────────────────────────────────────────────\n"

    # 活跃度趋势
    activity_trend = analysis.get("activity_trend", "N/A")
    section += f"  活跃度趋势: {activity_trend}\n"

    # 成功率
    success_rate = analysis.get("success_rate", 0)
    section += f"  任务成功率: {success_rate:.1f}%\n"

    # 预测
    if predictions:
        section += f"  预测 ({len(predictions)}条):\n"
        for pred in predictions[:3]:
            pred_type = pred.get("type", "N/A")
            pred_desc = pred.get("description", "N/A")
            section += f"    - {pred_type}: {pred_desc}\n"

    return section


def build_alert_section():
    """构建告警部分"""
    config = load_alert_config()
    history = load_alert_history()

    if not config:
        return "【告警系统】未配置告警，请运行 alert_system.py --config"

    enabled = config.get("enabled", True)
    thresholds = config.get("thresholds", {})

    section = "【告警系统】\n─────────────────────────────────────────────────────────────────\n"
    section += f"  状态: {'启用' if enabled else '禁用'}\n"

    if thresholds:
        section += f"  阈值配置:\n"
        section += f"    最低成功率: {thresholds.get('success_rate_min', 80)}%\n"
        section += f"    最大活跃度下降: {thresholds.get('activity_drop_percent', 50)}%\n"
        section += f"    最大失败次数: {thresholds.get('failure_count_max', 5)}\n"

    # 最近告警
    if history:
        section += f"  最近告警 ({len(history)}条):\n"
        for alert in history[-3:]:
            alert_time = format_time(alert.get("time", ""))
            alert_type = alert.get("type", "N/A")
            alert_msg = alert.get("message", "N/A")
            section += f"    [{alert_time}] {alert_type}: {alert_msg}\n"

    return section


def build_capability_section():
    """构建能力概览部分"""
    # 统计 scripts 目录下的工具数量
    script_count = 0
    plan_count = 0

    try:
        for f in os.listdir(SCRIPT_DIR):
            if f.endswith(".py") and not f.startswith("_"):
                script_count += 1
    except Exception:
        pass

    plans_dir = os.path.join(PROJECT_ROOT, "assets", "plans")
    if os.path.exists(plans_dir):
        try:
            for f in os.listdir(plans_dir):
                if f.endswith(".json"):
                    plan_count += 1
        except Exception:
            pass

    section = f"""
【能力概览】
─────────────────────────────────────────────────────────────────
  工具脚本: {script_count} 个
  场景计划: {plan_count} 个
"""
    return section


def build_recent_activity_section():
    """构建最近活动部分"""
    logs = load_recent_logs()

    section = "【最近活动】\n─────────────────────────────────────────────────────────────────\n"

    # 获取最近的行为日志
    log_file = os.path.join(LOGS_DIR, "behavior_" + datetime.now().strftime("%Y-%m-%d") + ".log")
    recent_entries = []

    if os.path.exists(log_file):
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                # 取最后 5 行
                for line in lines[-5:]:
                    if line.strip():
                        recent_entries.append(line.strip())
        except Exception:
            pass

    if recent_entries:
        for entry in recent_entries:
            # 截取关键部分
            if len(entry) > 80:
                entry = entry[:77] + "..."
            section += f"  {entry}\n"
    else:
        section += "  暂无活动记录\n"

    return section


def build_dashboard(full=False):
    """构建完整仪表板"""
    parts = [build_header()]

    if full:
        parts.append(build_evolution_section())
        parts.append(build_health_section())
        parts.append(build_capability_section())
        parts.append(build_trend_section())
        parts.append(build_alert_section())
    else:
        # 简短模式只显示核心信息
        parts.append(build_capability_section())
        parts.append(build_evolution_section())
        parts.append(build_trend_section())

    parts.append(build_recent_activity_section())

    return "\n".join(parts)


def main():
    """主函数"""
    # 设置输出编码
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    # 解析参数
    full = "--full" in sys.argv

    # 构建并输出仪表板
    dashboard = build_dashboard(full=full)
    safe_print(dashboard)

    return 0


if __name__ == "__main__":
    sys.exit(main())