#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自主决策模块 - 让系统在无用户指令时能主动做一些有意义的事情
增强版：添加时间上下文和环境上下文理解能力
"""

import os
import time
import json
import subprocess
from datetime import datetime
from pathlib import Path


# 时间上下文：不同时间段推荐的任务
TIME_CONTEXT_TASKS = {
    "morning": [  # 6:00-12:00
        "查看今日工作计划",
        "检查邮件",
        "打开 iHaier 查看消息",
        "开始一天的工作"
    ],
    "afternoon": [  # 12:00-18:00
        "查看上午工作总结",
        "处理待办事项",
        "查看是否有新消息",
        "整理下午工作内容"
    ],
    "evening": [  # 18:00-22:00
        "查看今日工作总结",
        "查看明日日程安排",
        "处理遗留工作"
    ],
    "night": [  # 22:00-6:00
        "系统运行正常",
        "可进行后台任务"
    ]
}


def get_time_context():
    """获取当前时间上下文"""
    now = datetime.now()
    hour = now.hour

    if 6 <= hour < 12:
        period = "morning"
    elif 12 <= hour < 18:
        period = "afternoon"
    elif 18 <= hour < 22:
        period = "evening"
    else:
        period = "night"

    return {
        "period": period,
        "hour": hour,
        "suggestions": TIME_CONTEXT_TASKS.get(period, [])
    }

# 系统状态目录
STATE_DIR = Path("runtime/state")
ACTIVE_SUGGESTIONS_FILE = STATE_DIR / "active_suggestions.json"
TASK_STATUS_FILE = STATE_DIR / "task_status.json"
HEALTH_REPORT_FILE = STATE_DIR / "health_report.json"
SESSION_CONTEXT_FILE = STATE_DIR / "session_context.json"


def check_system_health():
    """检查系统健康状况"""
    if HEALTH_REPORT_FILE.exists():
        try:
            with open(HEALTH_REPORT_FILE, 'r', encoding='utf-8') as f:
                health_data = json.load(f)
                return health_data.get('all_ok', False)
        except Exception:
            return False
    return False


def get_active_suggestions():
    """获取当前活跃场景建议"""
    if ACTIVE_SUGGESTIONS_FILE.exists():
        try:
            with open(ACTIVE_SUGGESTIONS_FILE, 'r', encoding='utf-8') as f:
                suggestions = json.load(f)
                return suggestions
        except Exception:
            return {}
    return {}


def get_current_task_status():
    """获取当前任务状态"""
    if TASK_STATUS_FILE.exists():
        try:
            with open(TASK_STATUS_FILE, 'r', encoding='utf-8') as f:
                status = json.load(f)
                return status
        except Exception:
            return {}
    return {}


def check_idle_time():
    """检查空闲时间（简化实现）"""
    # 这里可以实现更复杂的空闲时间检测逻辑
    # 现在我们假设如果没有任何任务在运行，则认为是空闲状态
    task_status = get_current_task_status()
    return not bool(task_status.get('current_task'))


def get_session_context():
    """获取会话上下文"""
    if SESSION_CONTEXT_FILE.exists():
        try:
            with open(SESSION_CONTEXT_FILE, 'r', encoding='utf-8') as f:
                context = json.load(f)
                return context
        except Exception:
            return {}
    return {}


def get_environment_context():
    """获取环境上下文（当前前台窗口）"""
    context = {
        "time": get_time_context(),
        "active_window": None
    }

    # 尝试获取当前活动窗口标题
    try:
        # 使用 PowerShell 获取前台窗口
        ps_script = '''
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll", CharSet = CharSet.Auto)]
    public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);
}
"@
$hwnd = [Win32]::GetForegroundWindow()
$sb = New-Object System.Text.StringBuilder 256
[Win32]::GetWindowText($hwnd, $sb, 256) | Out-Null
$sb.ToString()
'''
        result = subprocess.run(
            ['powershell', '-Command', ps_script],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            context["active_window"] = result.stdout.strip()
    except Exception:
        pass

    return context


def make_autonomous_decision():
    """
    做出自主决策（增强版：包含时间上下文和环境上下文）
    返回决策建议或执行的操作
    """
    # 获取环境上下文
    env_context = get_environment_context()
    time_context = env_context["time"]

    # 检查系统健康状况
    if not check_system_health():
        return {
            "decision": "system_health_issue",
            "action": "建议检查系统健康状况",
            "context": time_context
        }

    # 检查是否有活跃建议
    suggestions = get_active_suggestions()
    if suggestions:
        return {
            "decision": "scene_suggestion",
            "suggestions": suggestions,
            "context": time_context
        }

    # 检查是否空闲
    if check_idle_time():
        # 如果空闲，基于时间上下文推荐任务
        time_suggestions = time_context.get("suggestions", [])

        # 检查当前活动窗口
        active_window = env_context.get("active_window")
        if active_window:
            # 如果用户正在使用某个应用，给出相关建议
            return {
                "decision": "time_context_suggestion",
                "active_window": active_window,
                "time_period": time_context["period"],
                "suggestions": time_suggestions[:2] if time_suggestions else ["系统运行正常"],
                "context": time_context
            }
        else:
            # 没有活动窗口时，基于时间推荐
            context = get_session_context()
            recent_apps = context.get('recent_apps', [])

            if recent_apps:
                return {
                    "decision": "idle_suggestion",
                    "action": f"建议打开最近使用的应用：{recent_apps[-1]}",
                    "time_period": time_context["period"],
                    "time_suggestions": time_suggestions,
                    "context": time_context
                }
            else:
                return {
                    "decision": "idle_suggestion",
                    "action": time_suggestions[0] if time_suggestions else "系统空闲，建议查看系统状态",
                    "time_period": time_context["period"],
                    "time_suggestions": time_suggestions,
                    "context": time_context
                }

    # 如果有正在进行的任务
    task_status = get_current_task_status()
    if task_status.get('current_task'):
        return {
            "decision": "task_continue",
            "task": task_status.get('current_task'),
            "progress": task_status.get('progress', '未知'),
            "context": time_context
        }

    # 默认决策
    return {
        "decision": "default",
        "action": "系统运行正常，等待用户指令",
        "context": time_context
    }


def main():
    """主函数 - 执行自主决策并输出结果"""
    print("=== 自主决策模块 ===")

    # 执行自主决策
    decision = make_autonomous_decision()

    # 输出决策结果
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] 自主决策结果:")
    print(json.dumps(decision, ensure_ascii=False, indent=2))

    # 将结果保存到状态文件中供其他模块使用
    autonomous_decision_file = STATE_DIR / "autonomous_decision.json"
    try:
        with open(autonomous_decision_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": timestamp,
                "decision": decision
            }, f, ensure_ascii=False, indent=2)
        print(f"决策结果已保存到 {autonomous_decision_file}")
    except Exception as e:
        print(f"保存决策结果时出错: {e}")


if __name__ == "__main__":
    main()