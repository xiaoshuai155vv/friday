#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查询场景经验：按关键词、标签或最近 N 条列出成功/失败记录，供规划时参考。
用法:
  python query_scenario_experiences.py [条数]                     # 最近 N 条，默认 20
  python query_scenario_experiences.py --keyword 自拍             # 包含「自拍」的场景
  python query_scenario_experiences.py --keyword 摄像头 --limit 10
  python query_scenario_experiences.py --tags ihaier,自拍         # 按标签筛选
  python query_scenario_experiences.py --stats                   # 统计各标签的成功率
输出 JSON 到 stdout。
"""

import argparse
import json
import os
import sys
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EXPERIENCES_FILE = os.path.join(ROOT, "runtime", "state", "scenario_experiences.json")


def extract_tags(scene_desc):
    """从场景描述中提取标签"""
    # 基础标签映射
    tag_map = {
        "ihaier": ["ihaier", "办公平台", "绩效", "消息"],
        "自拍": ["自拍", "摄像头", "拍照"],
        "浏览器": ["浏览器", "访问网站", "网页"],
        "计算器": ["计算器", "计算"],
        "文件": ["文件", "目录", "打开文件"],
        "音乐": ["音乐", "播放", "听歌"],
        "通知": ["通知", "提醒"],
        "截图": ["截图", "视觉"]
    }

    tags = []
    scene_lower = scene_desc.lower()
    for tag, keywords in tag_map.items():
        if any(keyword in scene_lower for keyword in keywords):
            tags.append(tag)

    # 如果没有识别到标签，返回默认标签
    if not tags:
        tags.append("其他")

    return tags


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("limit", nargs="?", type=int, default=20, help="最近 N 条，默认 20")
    ap.add_argument("--keyword", "-k", default="", help="只输出场景描述或命令中包含该关键词的条目")
    ap.add_argument("--tags", default="", help="按标签筛选，多个标签用逗号分隔，如 --tags ihaier,自拍")
    ap.add_argument("--stats", action="store_true", help="统计各标签的成功率")
    args = ap.parse_args()

    if not os.path.isfile(EXPERIENCES_FILE):
        print(json.dumps({"entries": [], "stats": {}}, ensure_ascii=False))
        return
    try:
        with open(EXPERIENCES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(json.dumps({"error": str(e), "entries": [], "stats": {}}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

    entries = data.get("entries") or []

    # 按关键词筛选
    if args.keyword:
        kw = args.keyword.strip().lower()
        entries = [e for e in entries if kw in (e.get("scene") or "").lower() or kw in (e.get("intent_or_cmd") or "").lower()]

    # 按标签筛选
    if args.tags:
        wanted_tags = set(args.tags.split(","))
        entries = [e for e in entries if set(extract_tags(e.get("scene", ""))) & wanted_tags]

    # 只保留最近的 entries
    entries = entries[-args.limit:]

    # 如果需要统计
    if args.stats:
        tag_stats = defaultdict(lambda: {"total": 0, "success": 0})
        for entry in entries:
            scene = entry.get("scene", "")
            tags = extract_tags(scene)
            result = entry.get("result", "").lower()
            for tag in tags:
                tag_stats[tag]["total"] += 1
                if result == "success":
                    tag_stats[tag]["success"] += 1

        # 计算成功率
        stats = {}
        for tag, counts in tag_stats.items():
            success_rate = counts["success"] / counts["total"] if counts["total"] > 0 else 0
            stats[tag] = {
                "total": counts["total"],
                "success": counts["success"],
                "success_rate": round(success_rate, 2)
            }

        print(json.dumps({"entries": entries, "stats": stats}, ensure_ascii=False, indent=0))
    else:
        print(json.dumps({"entries": entries, "stats": {}}, ensure_ascii=False, indent=0))


if __name__ == "__main__":
    main()
