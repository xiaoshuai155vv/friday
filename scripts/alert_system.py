#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
告警系统 - 配置告警阈值，检测异常并发送通知

功能：
- 可配置告警阈值（成功率、活跃度等）
- 定时检测趋势数据，发现异常时主动通知
- 支持白名单和告警历史

触发方式：
  python scripts/alert_system.py [--check] [--config] [--set-threshold key value]
  do 告警设置 / 查看告警 / 告警状态
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

STATE_DIR = os.path.join(PROJECT_ROOT, "runtime", "state")

TREND_FILE = os.path.join(STATE_DIR, "trend_predictions.json")
ALERT_CONFIG_FILE = os.path.join(STATE_DIR, "alert_config.json")
ALERT_HISTORY_FILE = os.path.join(STATE_DIR, "alert_history.json")

# 默认告警配置
DEFAULT_CONFIG = {
    "enabled": True,
    "thresholds": {
        "success_rate_min": 80.0,      # 成功率低于此值告警
        "activity_drop_percent": 50.0,  # 活跃度下降超过此比例告警
        "failure_count_max": 5,        # 失败次数超过此值告警
    },
    "check_interval_minutes": 60,     # 检查间隔
    "notify_on_alert": True,           # 告警时是否发送通知
    "quiet_hours": [],                 # 静默时段 [start_hour, end_hour]
}


def safe_print(text):
    """安全打印，处理编码问题"""
    try:
        print(text)
    except UnicodeEncodeError:
        # 移除 emoji 后打印
        import re
        text_no_emoji = re.sub(r'[\U0001F300-\U0001F9FF]', '', text)
        print(text_no_emoji)


def load_config():
    """加载告警配置"""
    if not os.path.exists(ALERT_CONFIG_FILE):
        return dict(DEFAULT_CONFIG)
    try:
        with open(ALERT_CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return dict(DEFAULT_CONFIG)


def save_config(config):
    """保存告警配置"""
    with open(ALERT_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def load_trend_data():
    """加载趋势数据"""
    if not os.path.exists(TREND_FILE):
        return None
    try:
        with open(TREND_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def load_alert_history():
    """加载告警历史"""
    if not os.path.exists(ALERT_HISTORY_FILE):
        return []
    try:
        with open(ALERT_HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_alert_history(history):
    """保存告警历史"""
    # 只保留最近100条
    history = history[-100:]
    with open(ALERT_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def check_quiet_hours(config):
    """检查是否在静默时段"""
    quiet_hours = config.get("quiet_hours", [])
    if not quiet_hours:
        return False

    now = datetime.now()
    current_hour = now.hour

    if len(quiet_hours) >= 2:
        start, end = quiet_hours[0], quiet_hours[1]
        if start <= end:
            return start <= current_hour < end
        else:
            # 跨天
            return current_hour >= start or current_hour < end

    return False


def check_thresholds(data, config):
    """检查阈值，返回告警列表"""
    alerts = []
    thresholds = config.get("thresholds", {})

    if not data:
        return [{"level": "error", "message": "无趋势数据"}]

    # 1. 检查成功率
    success_trend = data.get("success_trend", {})
    success_rate = success_trend.get("success_rate", 100)
    min_rate = thresholds.get("success_rate_min", 80.0)

    if success_rate < min_rate:
        alerts.append({
            "type": "success_rate",
            "level": "warning" if success_rate >= 50 else "critical",
            "message": f"成功率低于阈值: {success_rate:.1f}% < {min_rate}%",
            "current": success_rate,
            "threshold": min_rate
        })

    # 2. 检查活跃度变化
    ts = data.get("time_series", {})
    change_rate = ts.get("change_rate", 0)
    max_drop = thresholds.get("activity_drop_percent", 50.0)

    if change_rate < -max_drop:
        alerts.append({
            "type": "activity_drop",
            "level": "warning",
            "message": f"活跃度下降超过阈值: {change_rate:.1f}% < -{max_drop}%",
            "current": change_rate,
            "threshold": -max_drop
        })

    # 3. 检查失败次数
    total_failed = success_trend.get("failed", 0)
    max_failures = thresholds.get("failure_count_max", 5)

    if total_failed > max_failures:
        alerts.append({
            "type": "failure_count",
            "level": "warning",
            "message": f"失败次数超过阈值: {total_failed} > {max_failures}",
            "current": total_failed,
            "threshold": max_failures
        })

    # 4. 检查执行分析中的任务失败率
    exec_analysis = data.get("execution_analysis_summary", {})
    mission_perf = exec_analysis.get("mission_performance", {})

    for mission, perf in mission_perf.items():
        if mission == "unknown":
            continue
        sr = perf.get("success_rate", 0)
        if sr > 0 and sr < 50:
            alerts.append({
                "type": "mission_failure",
                "level": "warning",
                "message": f"任务 '{mission}' 成功率低: {sr:.1f}%",
                "mission": mission,
                "success_rate": sr
            })

    return alerts


def send_notification(alerts, config):
    """发送告警通知"""
    if not config.get("notify_on_alert", True):
        return

    # 检查静默时段
    if check_quiet_hours(config):
        return

    # 使用 notification_tool 发送通知
    try:
        import subprocess

        level_counts = {"critical": 0, "warning": 0, "error": 0}
        for alert in alerts:
            lvl = alert.get("level", "warning")
            if lvl in level_counts:
                level_counts[lvl] += 1

        title = "星期五 告警通知"
        if level_counts["critical"] > 0:
            title = "🔴 " + title
        elif level_counts["warning"] > 0:
            title = "🟡 " + title

        body = f"发现 {len(alerts)} 个告警项\n"
        for alert in alerts[:3]:  # 最多显示3条
            body += f"• {alert.get('message', '')}\n"

        if len(alerts) > 3:
            body += f"• ...还有 {len(alerts) - 3} 条"

        # 调用 notification_tool
        subprocess.run([
            sys.executable,
            os.path.join(SCRIPT_DIR, "notification_tool.py"),
            "show",
            "--title", title,
            "--body", body
        ], capture_output=True)

    except Exception as e:
        print(f"发送通知失败: {e}")


def run_check():
    """执行告警检查"""
    config = load_config()

    if not config.get("enabled", True):
        return {"status": "disabled", "message": "告警系统已关闭"}

    # 检查静默时段
    if check_quiet_hours(config):
        return {"status": "quiet_hours", "message": "当前为静默时段"}

    # 加载趋势数据
    data = load_trend_data()
    if not data:
        return {"status": "no_data", "message": "无趋势数据可检查"}

    # 检查阈值
    alerts = check_thresholds(data, config)

    # 记录告警历史
    if alerts:
        history = load_alert_history()
        history.append({
            "timestamp": datetime.now().isoformat(),
            "alert_count": len(alerts),
            "alerts": alerts
        })
        save_alert_history(history)

        # 发送通知
        send_notification(alerts, config)

    return {
        "status": "checked",
        "alerts_count": len(alerts),
        "alerts": alerts
    }


def show_config():
    """显示当前配置"""
    config = load_config()
    lines = []
    lines.append("\n" + "=" * 50)
    lines.append("ALERT SYSTEM CONFIG")
    lines.append("=" * 50)
    lines.append("\nEnabled: {}".format('Yes' if config.get('enabled') else 'No'))
    lines.append("Check Interval: {} minutes".format(config.get('check_interval_minutes')))

    thresholds = config.get("thresholds", {})
    lines.append("\nAlert Thresholds:")
    lines.append("  Min Success Rate: {}%".format(thresholds.get('success_rate_min')))
    lines.append("  Max Activity Drop: {}%".format(thresholds.get('activity_drop_percent')))
    lines.append("  Max Failure Count: {}".format(thresholds.get('failure_count_max')))

    quiet = config.get("quiet_hours", [])
    if quiet:
        lines.append("\nQuiet Hours: {}:00 - {}:00".format(quiet[0], quiet[1]))
    else:
        lines.append("\nQuiet Hours: None")

    lines.append("Notify on Alert: {}".format('Yes' if config.get('notify_on_alert') else 'No'))

    # 显示最近告警
    history = load_alert_history()
    if history:
        lines.append("\nRecent Alert History: {} entries".format(len(history)))

    return "\n".join(lines)


def show_status():
    """显示告警状态（简短）"""
    config = load_config()

    if not config.get("enabled"):
        return "[X] Alert System: Disabled"

    # 快速检查
    result = run_check()

    if result["status"] == "disabled":
        return "[X] Alert System: Disabled"
    elif result["status"] == "quiet_hours":
        return "[-] Alert System: Quiet Hours"
    elif result["status"] == "no_data":
        return "[?] Alert System: No Data"
    elif result["alerts_count"] == 0:
        return "[OK] Alert System: Normal (No alerts)"
    else:
        return "[!] Alert System: {} alerts".format(result['alerts_count'])


def set_threshold(key, value):
    """设置阈值"""
    config = load_config()
    config["thresholds"][key] = value
    save_config(config)
    return f"已设置 {key} = {value}"


def enable_alerts(enabled=True):
    """启用/禁用告警"""
    config = load_config()
    config["enabled"] = enabled
    save_config(config)
    return f"告警系统已{'启用' if enabled else '关闭'}"


def main():
    import argparse
    ap = argparse.ArgumentParser(description="告警系统")
    sp = ap.add_subparsers(dest="cmd", required=True)

    sp.add_parser("check", help="执行告警检查")
    sp.add_parser("config", help="显示配置")
    sp.add_parser("status", help="显示状态")
    sp.add_parser("enable", help="启用告警")
    sp.add_parser("disable", help="禁用告警")

    p_set = sp.add_parser("set-threshold", help="设置阈值")
    p_set.add_argument("key", help="阈值键名")
    p_set.add_argument("value", type=float, help="阈值值")

    args = ap.parse_args()

    if args.cmd == "check":
        result = run_check()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.cmd == "config":
        safe_print(show_config())
    elif args.cmd == "status":
        safe_print(show_status())
    elif args.cmd == "enable":
        safe_print(enable_alerts(True))
    elif args.cmd == "disable":
        safe_print(enable_alerts(False))
    elif args.cmd == "set-threshold":
        safe_print(set_threshold(args.key, args.value))


if __name__ == "__main__":
    main()