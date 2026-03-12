#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
场景执行后的智能后续建议系统
当场景计划执行完成后，自动生成后续行动建议，让系统更像有意识的助手
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# 添加项目根目录到Python路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)


# 场景后续关系图谱：定义场景完成后的可能后续场景
SCENARIO_FOLLOWUP_GRAPH = {
    # iHaier 场景 -> 休息或娱乐
    "ihaier": ["play_music", "watch_movie", "browse_zhihu", "focus_reminder"],
    "ihaier_performance_declaration": ["focus_reminder", "play_music"],
    "ihaier_contact_latest_message": ["focus_reminder", "play_music"],

    # 看电影 -> 听音乐或浏览
    "watch_movie": ["play_music", "browse_zhihu", "read_news"],
    "movie": ["play_music", "browse_zhihu", "read_news"],

    # 听音乐 -> 看电影或浏览
    "play_music": ["watch_movie", "browse_zhihu", "read_news"],
    "listen_to_music": ["watch_movie", "browse_zhihu", "read_news"],
    "music": ["watch_movie", "browse_zhihu", "read_news"],

    # 刷知乎 -> 看新闻或听音乐
    "browse_zhihu": ["read_news", "play_music", "watch_movie"],
    "zhihu": ["read_news", "play_music", "watch_movie"],

    # 看新闻 -> 刷知乎或休息
    "read_news": ["browse_zhihu", "play_music", "focus_reminder"],
    "news": ["browse_zhihu", "play_music", "focus_reminder"],

    # 视频会议 -> 休息或看新闻
    "video_conference": ["focus_reminder", "read_news", "play_music"],

    # 批量文件操作 -> 休息
    "batch_file_operation": ["focus_reminder", "play_music"],

    # 通用场景 -> 建议休息
    "default": ["focus_reminder", "play_music"]
}


def get_current_time_period() -> str:
    """获取当前时间段"""
    hour = datetime.now().hour
    if 6 <= hour < 9:
        return "morning"
    elif 9 <= hour < 12:
        return "forenoon"
    elif 12 <= hour < 14:
        return "noon"
    elif 14 <= hour < 18:
        return "afternoon"
    elif 18 <= hour < 22:
        return "evening"
    else:
        return "night"


def get_focus_status() -> Dict[str, bool]:
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
        'focus_mode_active': False
    }


def analyze_completed_scenario(scenario_name: str, execution_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    分析完成的场景，生成后续建议

    Args:
        scenario_name: 场景名称
        execution_result: 执行结果

    Returns:
        后续建议列表
    """
    suggestions = []

    # 识别场景类型
    scenario_type = _identify_scenario_type(scenario_name)

    # 获取可能的后续场景
    followup_scenarios = SCENARIO_FOLLOWUP_GRAPH.get(
        scenario_type,
        SCENARIO_FOLLOWUP_GRAPH["default"]
    )

    # 获取当前状态
    time_period = get_current_time_period()
    focus_status = get_focus_status()

    # 根据时间段和状态生成建议
    for followup in followup_scenarios:
        suggestion = _build_suggestion(followup, time_period, focus_status, scenario_type)
        if suggestion:
            suggestions.append(suggestion)

    # 添加通用建议
    suggestions.extend(_get_general_suggestions(time_period, focus_status))

    return suggestions[:5]  # 限制最多5条建议


def _identify_scenario_type(scenario_name: str) -> str:
    """识别场景类型"""
    scenario_lower = scenario_name.lower()

    for key in SCENARIO_FOLLOWUP_GRAPH:
        if key != "default" and key in scenario_lower:
            return key

    # 根据文件名识别
    if "ihaier" in scenario_lower or "performance" in scenario_lower or "message" in scenario_lower:
        return "ihaier"
    elif "watch" in scenario_lower or "movie" in scenario_lower:
        return "movie"
    elif "music" in scenario_lower or "play" in scenario_lower or "listen" in scenario_lower:
        return "music"
    elif "zhihu" in scenario_lower:
        return "zhihu"
    elif "news" in scenario_lower or "read" in scenario_lower:
        return "news"
    elif "video" in scenario_lower or "conference" in scenario_lower:
        return "video_conference"
    elif "batch" in scenario_lower or "file" in scenario_lower:
        return "batch_file_operation"

    return "default"


def _build_suggestion(followup_type: str, time_period: str, focus_status: Dict[str, bool], completed_scenario: str) -> Optional[Dict[str, Any]]:
    """构建具体建议"""
    suggestion_templates = {
        "focus_reminder": {
            "priority": "medium",
            "type": "followup",
            "title": "休息一下",
            "template": "完成了{scenario}，建议休息一下，恢复精力"
        },
        "play_music": {
            "priority": "low",
            "type": "followup",
            "title": "放松一下",
            "template": "完成了{scenario}，要不要放首歌放松一下？"
        },
        "watch_movie": {
            "priority": "low",
            "type": "followup",
            "title": "看个电影",
            "template": "完成了{scenario}，想看个电影休息一下吗？"
        },
        "browse_zhihu": {
            "priority": "low",
            "type": "followup",
            "title": "刷会儿知乎",
            "template": "完成了{scenario}，刷会儿知乎看看有什么有趣的内容？"
        },
        "read_news": {
            "priority": "low",
            "type": "followup",
            "title": "看看新闻",
            "template": "完成了{scenario}，看看今天有什么新闻？"
        }
    }

    template = suggestion_templates.get(followup_type)
    if not template:
        return None

    scenario_display = _get_scenario_display(completed_scenario)

    return {
        "priority": template["priority"],
        "type": template["type"],
        "title": template["title"],
        "content": template["template"].format(scenario=scenario_display),
        "suggested_action": followup_type,
        "timestamp": datetime.now().isoformat()
    }


def _get_general_suggestions(time_period: str, focus_status: Dict[str, bool]) -> List[Dict[str, Any]]:
    """获取通用建议（与场景无关）"""
    suggestions = []

    # 如果番茄钟未激活，建议开启
    if not focus_status.get('pomodoro_active') and not focus_status.get('focus_mode_active'):
        if time_period in ["forenoon", "afternoon"]:
            suggestions.append({
                "priority": "medium",
                "type": "general",
                "title": "开启专注模式",
                "content": "现在是工作好时段，要开启番茄钟保持专注吗？",
                "suggested_action": "focus_reminder",
                "timestamp": datetime.now().isoformat()
            })

    return suggestions


def _get_scenario_display(scenario_type: str) -> str:
    """获取场景的中文显示名称"""
    display_names = {
        "ihaier": "工作任务",
        "ihaier_performance_declaration": "绩效申报",
        "ihaier_contact_latest_message": "消息查看",
        "watch_movie": "看电影",
        "movie": "观影",
        "play_music": "听音乐",
        "listen_to_music": "听音乐",
        "music": "音乐",
        "browse_zhihu": "刷知乎",
        "zhihu": "刷知乎",
        "read_news": "看新闻",
        "news": "阅读新闻",
        "video_conference": "视频会议",
        "batch_file_operation": "文件操作"
    }
    return display_names.get(scenario_type, "任务")


def save_followup_suggestions(scenario_name: str, suggestions: List[Dict[str, Any]]):
    """保存后续建议到状态文件"""
    output_file = os.path.join(PROJECT_ROOT, 'runtime', 'state', 'scenario_followup_suggestions.json')

    data = {
        "scenario": scenario_name,
        "suggestions": suggestions,
        "generated_at": datetime.now().isoformat()
    }

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"后续建议已保存到: {output_file}", file=sys.stderr)
    except Exception as e:
        print(f"保存建议失败: {e}", file=sys.stderr)


def show_followup_notification(suggestions: List[Dict[str, Any]]):
    """显示后续建议通知"""
    if not suggestions:
        return

    # 获取最高优先级的建议
    priority_order = {"high": 0, "medium": 1, "low": 2}
    sorted_suggestions = sorted(suggestions, key=lambda x: priority_order.get(x.get("priority", "low"), 2))
    top_suggestion = sorted_suggestions[0]

    # 发送通知
    try:
        notification_script = os.path.join(SCRIPT_DIR, 'notification_tool.py')
        if os.path.exists(notification_script):
            import subprocess
            message = f"{top_suggestion.get('title', '建议')}: {top_suggestion.get('content', '')}"
            subprocess.run([sys.executable, notification_script, 'show', message],
                          capture_output=True, timeout=10)
    except Exception as e:
        print(f"发送通知失败: {e}", file=sys.stderr)


def generate_followup(scenario_name: str, execution_result: Optional[Dict[str, Any]] = None, notify: bool = True) -> List[Dict[str, Any]]:
    """
    生成场景后续建议的主函数

    Args:
        scenario_name: 场景名称
        execution_result: 执行结果（可选）
        notify: 是否发送通知

    Returns:
        建议列表
    """
    if execution_result is None:
        execution_result = {}

    # 分析场景并生成建议
    suggestions = analyze_completed_scenario(scenario_name, execution_result)

    # 保存建议
    save_followup_suggestions(scenario_name, suggestions)

    # 发送通知
    if notify:
        show_followup_notification(suggestions)

    return suggestions


def main():
    """命令行入口"""
    import argparse
    parser = argparse.ArgumentParser(description='场景后续建议生成器')
    parser.add_argument('scenario', help='场景名称')
    parser.add_argument('--notify', action='store_true', default=True, help='是否发送通知')
    parser.add_argument('--no-notify', action='store_true', help='不发送通知')
    args = parser.parse_args()

    notify = args.notify and not args.no_notify
    suggestions = generate_followup(args.scenario, notify=notify)

    print(f"为场景 '{args.scenario}' 生成了 {len(suggestions)} 条后续建议:")
    for i, s in enumerate(suggestions, 1):
        print(f"  {i}. [{s.get('priority', 'N/A')}] {s.get('title', '建议')}: {s.get('content', '')}")


if __name__ == '__main__':
    main()