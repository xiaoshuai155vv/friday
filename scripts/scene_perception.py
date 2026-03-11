#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
场景自动感知与智能推荐。
根据当前前台窗口/应用，自动推荐可能需要的场景计划，提升拟人化交互体验。
用法: scene_perception.py [--output json]
"""

import sys
import os
import json
import glob

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(PROJECT, "scripts")
PLANS_DIR = os.path.join(PROJECT, "assets", "plans")
STATE_DIR = os.path.join(PROJECT, "runtime", "state")

# 前台应用到场景的映射关系
APP_SCENE_MAPPING = {
    # iHaier 相关
    "iHaier": ["ihaier_performance_declaration.json", "example_ihaier_send_message.json", "example_ihaier_check_messages.json", "send_to_zhouxiaoshuai.json"],
    "iHaier2.0": ["ihaier_performance_declaration.json", "example_ihaier_send_message.json", "example_ihaier_check_messages.json", "send_to_zhouxiaoshuai.json"],
    "办公平台": ["ihaier_performance_declaration.json", "example_ihaier_send_message.json", "example_ihaier_check_messages.json", "send_to_zhouxiaoshuai.json"],
    "办公": ["ihaier_performance_declaration.json", "example_ihaier_send_message.json", "example_ihaier_check_messages.json", "send_to_zhouxiaoshuai.json"],

    # 浏览器相关
    "chrome": ["example_visit_website.json"],
    "msedge": ["example_visit_website.json"],
    "firefox": ["example_visit_website.json"],
    "browser": ["example_visit_website.json"],

    # 音乐相关
    "cloudmusic": ["play_music.json", "listen_to_music.json"],
    "网易云音乐": ["play_music.json", "listen_to_music.json"],
    "Music": ["play_music.json", "listen_to_music.json"],

    # 视频/电影相关
    "movie": ["watch_movie.json"],
    "video": ["video_conference.json"],
    "PotPlayer": ["watch_movie.json"],
    "VLC": ["watch_movie.json"],

    # 知乎/新闻相关
    "zhihu": ["browse_zhihu.json"],
    "知乎": ["browse_zhihu.json"],
    "news": ["read_news.json"],
    "新闻": ["read_news.json", "news_reader.json"],
}


def get_foreground_window_info():
    """获取当前前台窗口信息"""
    sys.path.insert(0, SCRIPTS)
    # 动态导入避免循环
    import importlib.util
    spec = importlib.util.spec_from_file_location("get_foreground_window", os.path.join(SCRIPTS, "get_foreground_window.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.get_foreground_window_info()


def get_scene_recommendations(title, process_name):
    """根据前台窗口信息推荐相关场景计划"""
    recommendations = []

    # 将标题和进程名转为小写方便匹配
    title_lower = (title or "").lower()
    process_lower = (process_name or "").lower()

    # 遍历映射关系，查找匹配
    matched_plans = []
    for app_key, plan_files in APP_SCENE_MAPPING.items():
        app_key_lower = app_key.lower()
        if app_key_lower in title_lower or app_key_lower in process_lower:
            matched_plans.extend(plan_files)

    # 去重
    matched_plans = list(set(matched_plans))

    # 读取每个匹配 plan 的信息
    for plan_file in matched_plans:
        plan_path = os.path.join(PLANS_DIR, plan_file)
        if os.path.isfile(plan_path):
            try:
                with open(plan_path, encoding="utf-8") as f:
                    plan_data = json.load(f)
                    # 提取描述（通常是第一个元素的 comment）
                    description = ""
                    for step in plan_data:
                        if isinstance(step, dict) and "comment" in step and "comment" in step.get("do", ""):
                            description = step.get("comment", "")
                            break

                    recommendations.append({
                        "plan": plan_file,
                        "intent": plan_data.get("intent", plan_file.replace(".json", "")),
                        "description": description[:100] if description else f"执行 {plan_file}",
                        "matched_on": app_key if app_key in title_lower or app_key in process_lower else "进程"
                    })
            except Exception:
                pass

    return recommendations


def main():
    import argparse
    parser = argparse.ArgumentParser(description="场景自动感知与智能推荐")
    parser.add_argument("--output", choices=["json", "text"], default="json", help="输出格式")
    parser.add_argument("--save", action="store_true", help="保存建议到 runtime/state/active_suggestions.json")
    args = parser.parse_args()

    # 获取前台窗口信息
    title, process_name = get_foreground_window_info()

    if args.output == "json":
        result = {
            "foreground_window": {
                "title": title,
                "process_name": process_name
            },
            "recommendations": []
        }

        if title or process_name:
            recommendations = get_scene_recommendations(title, process_name)
            result["recommendations"] = recommendations

        print(json.dumps(result, ensure_ascii=False, indent=2))

        if args.save and recommendations:
            try:
                os.makedirs(STATE_DIR, exist_ok=True)
                output_path = os.path.join(STATE_DIR, "active_suggestions.json")
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"\n建议已保存到: {output_path}")
            except Exception as e:
                print(f"保存文件失败: {e}")
        elif args.save:
            print("无推荐内容，不保存文件")
    else:
        # 文本格式输出
        print(f"当前前台窗口: {title} ({process_name})")
        print("推荐场景计划:")

        recommendations = get_scene_recommendations(title, process_name)
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec['intent']}: {rec['description']}")


if __name__ == "__main__":
    main()