#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能主动建议引擎
根据系统状态、时间、用户习惯等生成主动建议并通知用户
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any
import sys

# 添加项目根目录到Python路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)


def get_system_health_status():
    """获取系统健康状态"""
    health_file = os.path.join(PROJECT_ROOT, 'runtime', 'state', 'health_report.json')
    if os.path.exists(health_file):
        try:
            with open(health_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return None


def get_focus_status():
    """获取番茄钟状态"""
    focus_file = os.path.join(PROJECT_ROOT, 'runtime', 'state', 'focus_reminder_status.json')
    if os.path.exists(focus_file):
        try:
            with open(focus_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {
        'pomodoro_active': False,
        'rest_reminder_active': False,
        'focus_mode_active': False
    }


def get_trend_data():
    """获取趋势数据"""
    trend_file = os.path.join(PROJECT_ROOT, 'runtime', 'state', 'execution_analysis.json')
    if os.path.exists(trend_file):
        try:
            with open(trend_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return None


def show_notification(message):
    """发送通知"""
    try:
        notification_script = os.path.join(SCRIPT_DIR, 'notification_tool.py')
        if os.path.exists(notification_script):
            import subprocess
            subprocess.run([sys.executable, notification_script, 'show', message],
                          capture_output=True, timeout=10)
    except Exception as e:
        print(f"通知失败: {e}")


def generate_active_suggestions() -> List[Dict[str, Any]]:
    """
    生成主动建议

    Returns:
        List of suggestions with priority, type, and content
    """
    suggestions = []

    # 1. 系统健康状态建议
    try:
        health_status = get_system_health_status()
        if health_status:
            # 检查CPU
            cpu_usage = health_status.get('cpu_usage', 0)
            if cpu_usage > 80:
                suggestions.append({
                    'priority': 'high',
                    'type': 'system_health',
                    'title': '系统负载过高',
                    'content': f'CPU使用率较高 ({cpu_usage:.1f}%)，建议适当休息',
                    'timestamp': datetime.now().isoformat()
                })

            # 检查内存
            memory_usage = health_status.get('memory_usage', 0)
            if memory_usage > 85:
                suggestions.append({
                    'priority': 'high',
                    'type': 'system_health',
                    'title': '内存占用过高',
                    'content': f'内存使用率较高 ({memory_usage:.1f}%)，建议关闭不必要的程序',
                    'timestamp': datetime.now().isoformat()
                })
        else:
            # 尝试直接检查系统
            try:
                import subprocess
                # CPU 检查
                result = subprocess.run(['wmic', 'cpu', 'get', 'loadpercentage'],
                                        capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1 and lines[1].strip().isdigit():
                        cpu_usage = int(lines[1].strip())
                        if cpu_usage > 80:
                            suggestions.append({
                                'priority': 'high',
                                'type': 'system_health',
                                'title': '系统负载过高',
                                'content': f'CPU使用率较高 ({cpu_usage}%)，建议适当休息',
                                'timestamp': datetime.now().isoformat()
                            })
            except Exception:
                pass
    except Exception as e:
        print(f"系统健康检查错误: {e}")

    # 2. 番茄钟状态建议
    try:
        focus_status = get_focus_status()
        if focus_status.get('pomodoro_active'):
            start_time = focus_status.get('pomodoro_start_time')
            if start_time:
                try:
                    start_dt = datetime.fromisoformat(start_time)
                    elapsed = datetime.now() - start_dt
                    minutes = int(elapsed.total_seconds() / 60)
                    work_duration = focus_status.get('work_duration', 25)

                    if minutes >= work_duration:
                        suggestions.append({
                            'priority': 'medium',
                            'type': 'focus_timer',
                            'title': '番茄钟工作时间结束',
                            'content': f'您已专注工作 {minutes} 分钟，建议适当休息',
                            'timestamp': datetime.now().isoformat()
                        })
                except Exception:
                    pass
    except Exception as e:
        print(f"番茄钟状态检查错误: {e}")

    # 3. 趋势分析建议
    try:
        trend_data = get_trend_data()
        if trend_data:
            # 如果最近成功率很高，可以给出积极建议
            success_rate = trend_data.get('success_rate', 0)
            if success_rate > 90:
                suggestions.append({
                    'priority': 'low',
                    'type': 'trend_analysis',
                    'title': '工作状态良好',
                    'content': '近期任务执行成功率很高，继续保持！',
                    'timestamp': datetime.now().isoformat()
                })
    except Exception as e:
        print(f"趋势分析错误: {e}")

    # 4. 时间相关建议
    current_hour = datetime.now().hour
    if 22 <= current_hour or current_hour < 7:
        suggestions.append({
            'priority': 'medium',
            'type': 'time_based',
            'title': '夜间提醒',
            'content': '现在是深夜，注意休息，避免过度疲劳',
            'timestamp': datetime.now().isoformat()
        })

    return suggestions


def save_suggestions_to_file(suggestions: List[Dict[str, Any]]):
    """将建议保存到文件"""
    suggestions_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                   'runtime', 'state', 'active_suggestions.json')

    # 确保目录存在
    os.makedirs(os.path.dirname(suggestions_file), exist_ok=True)

    # 读取现有建议
    existing_suggestions = []
    if os.path.exists(suggestions_file):
        try:
            with open(suggestions_file, 'r', encoding='utf-8') as f:
                existing_suggestions = json.load(f)
        except Exception as e:
            print(f"读取现有建议文件错误: {e}")

    # 添加新建议
    existing_suggestions.extend(suggestions)

    # 保留最新的50条建议
    existing_suggestions = existing_suggestions[-50:]

    # 写入文件
    try:
        with open(suggestions_file, 'w', encoding='utf-8') as f:
            json.dump(existing_suggestions, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存建议文件错误: {e}")


def send_suggestions_to_user():
    """向用户发送建议"""
    suggestions = generate_active_suggestions()

    # 保存建议到文件
    save_suggestions_to_file(suggestions)

    # 发送通知给用户
    for suggestion in suggestions:
        # 只发送高优先级建议
        if suggestion['priority'] == 'high':
            try:
                show_notification(f"[主动建议] {suggestion['title']}: {suggestion['content']}")
            except Exception as e:
                print(f"发送通知错误: {e}")

    return suggestions


def main():
    """主函数"""
    print("正在生成主动建议...")
    suggestions = send_suggestions_to_user()

    print(f"生成了 {len(suggestions)} 条建议:")
    for suggestion in suggestions:
        print(f"- {suggestion['title']}: {suggestion['content']} (优先级: {suggestion['priority']})")


if __name__ == "__main__":
    main()