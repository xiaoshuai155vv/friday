#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户偏好学习器：记录用户选择并应用到后续任务
用法:
  python user_preference_learner.py record <类型> <值>   # 记录用户选择
  python user_preference_learner.py get                       # 获取用户偏好
  python user_preference_learner.py clear                    # 清除学习记录
"""

import os
import sys
import json
from datetime import datetime, timezone

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPTS)
PREF_FILE = os.path.join(PROJECT, "memory", "user_preferences.json")


def load_preferences():
    """加载用户偏好文件"""
    if not os.path.isfile(PREF_FILE):
        return {
            "version": "1.0",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "preferences": {},
            "usage_history": {
                "frequent_apps": [],
                "frequent_contacts": [],
                "frequent_operations": []
            },
            "learned_patterns": {}
        }

    try:
        with open(PREF_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading preferences: {e}", file=sys.stderr)
        return {}


def save_preferences(prefs):
    """保存用户偏好文件"""
    try:
        os.makedirs(os.path.dirname(PREF_FILE), exist_ok=True)
        prefs["last_updated"] = datetime.now(timezone.utc).isoformat()
        with open(PREF_FILE, "w", encoding="utf-8") as f:
            json.dump(prefs, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving preferences: {e}", file=sys.stderr)
        return False


def record_preference(pref_type, value):
    """记录用户偏好"""
    prefs = load_preferences()

    # 记录到 usage_history
    if pref_type == "app":
        if "frequent_apps" not in prefs.get("usage_history", {}):
            prefs.setdefault("usage_history", {}).setdefault("frequent_apps", [])

        apps = prefs["usage_history"]["frequent_apps"]
        if value not in apps:
            apps.append(value)
            # 只保留最近10个
            prefs["usage_history"]["frequent_apps"] = apps[-10:]

    elif pref_type == "contact":
        if "frequent_contacts" not in prefs.get("usage_history", {}):
            prefs.setdefault("usage_history", {}).setdefault("frequent_contacts", [])

        contacts = prefs["usage_history"]["frequent_contacts"]
        if value not in contacts:
            contacts.append(value)
            prefs["usage_history"]["frequent_contacts"] = contacts[-10:]

    elif pref_type == "operation":
        if "frequent_operations" not in prefs.get("usage_history", {}):
            prefs.setdefault("usage_history", {}).setdefault("frequent_operations", [])

        ops = prefs["usage_history"]["frequent_operations"]
        if value not in ops:
            ops.append(value)
            prefs["usage_history"]["frequent_operations"] = ops[-10:]

    # 记录到 learned_patterns
    if pref_type == "app":
        patterns = prefs.setdefault("learned_patterns", {})
        apps = prefs.get("usage_history", {}).get("frequent_apps", [])
        if len(apps) >= 3:
            # 最频繁使用的应用
            from collections import Counter
            most_common = Counter(apps).most_common(1)
            if most_common:
                patterns["most_frequent_app"] = most_common[0][0]
                prefs["preferences"]["preferred_app"] = most_common[0][0]

    if save_preferences(prefs):
        print(f"Recorded: {pref_type} = {value}", file=sys.stderr)
        return True
    return False


def get_preferences():
    """获取用户偏好"""
    prefs = load_preferences()
    print(json.dumps(prefs, ensure_ascii=False, indent=2))
    return prefs


def clear_learning():
    """清除学习记录"""
    prefs = load_preferences()
    prefs["usage_history"] = {
        "frequent_apps": [],
        "frequent_contacts": [],
        "frequent_operations": []
    }
    prefs["learned_patterns"] = {}
    if save_preferences(prefs):
        print("Cleared learning records", file=sys.stderr)
        return True
    return False


def main():
    if len(sys.argv) < 2:
        print("用法: python user_preference_learner.py record <类型> <值>")
        print("      python user_preference_learner.py get")
        print("      python user_preference_learner.py clear")
        print("类型: app, contact, operation")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "record":
        if len(sys.argv) < 4:
            print("用法: python user_preference_learner.py record <类型> <值>", file=sys.stderr)
            sys.exit(1)
        pref_type = sys.argv[2]
        value = sys.argv[3]
        success = record_preference(pref_type, value)
        sys.exit(0 if success else 1)

    elif cmd == "get":
        get_preferences()
        sys.exit(0)

    elif cmd == "clear":
        success = clear_learning()
        sys.exit(0 if success else 1)

    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()