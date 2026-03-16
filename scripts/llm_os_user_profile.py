#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-OS 用户画像与偏好管理模块 - 提供用户画像和个性化设置管理能力

本模块提供类似用户配置文件管理器的能力：
- 用户画像管理（存储用户个人信息和配置）
- 偏好设置管理（语言、主题、通知等个性化设置）
- 用户行为历史记录
- 快速偏好切换

版本: 1.0.0
依赖: json, os, datetime
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# 脚本目录和状态目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "runtime", "state")
USER_PROFILE_DIR = os.path.join(STATE_DIR, "llm_os_user_profiles")
PROFILE_FILE = os.path.join(USER_PROFILE_DIR, "default_profile.json")
PREFERENCES_FILE = os.path.join(USER_PROFILE_DIR, "preferences.json")
BEHAVIOR_HISTORY_FILE = os.path.join(USER_PROFILE_DIR, "behavior_history.json")


def ensure_dir():
    """确保目录存在"""
    os.makedirs(USER_PROFILE_DIR, exist_ok=True)


def get_version():
    """获取模块版本"""
    return "1.0.0"


def init_default_profile():
    """初始化默认用户画像"""
    default_profile = {
        "profile_id": "default",
        "name": "默认用户",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "personal_info": {
            "display_name": "用户",
            "language": "zh-CN",
            "timezone": "Asia/Shanghai"
        },
        "appearance": {
            "theme": "dark",
            "accent_color": "#0078D4",
            "font_size": "medium",
            "density": "comfortable"
        },
        "notifications": {
            "enabled": True,
            "sound": True,
            "desktop_banner": True,
            "focus_assist": False
        },
        "privacy": {
            "location_enabled": False,
            "telemetry_enabled": False,
            "diagnostics_enabled": True
        },
        "shortcuts": {
            "custom": {}
        },
        "workspace": {
            "default_view": "grid",
            "show_hidden_files": False,
            "confirm_delete": True,
            "auto_save": True
        }
    }
    return default_profile


def load_profile(profile_id="default"):
    """加载用户画像"""
    ensure_dir()
    if profile_id == "default":
        profile_path = PROFILE_FILE
    else:
        profile_path = os.path.join(USER_PROFILE_DIR, f"{profile_id}.json")

    if os.path.exists(profile_path):
        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return init_default_profile()
    return init_default_profile()


def save_profile(profile):
    """保存用户画像"""
    ensure_dir()
    profile_id = profile.get("profile_id", "default")
    if profile_id == "default":
        profile_path = PROFILE_FILE
    else:
        profile_path = os.path.join(USER_PROFILE_DIR, f"{profile_id}.json")

    profile["updated_at"] = datetime.now().isoformat()
    try:
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
        return True
    except IOError:
        return False


def get_preferences():
    """获取偏好设置"""
    ensure_dir()
    if os.path.exists(PREFERENCES_FILE):
        try:
            with open(PREFERENCES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_preferences(preferences):
    """保存偏好设置"""
    ensure_dir()
    try:
        with open(PREFERENCES_FILE, 'w', encoding='utf-8') as f:
            json.dump(preferences, f, ensure_ascii=False, indent=2)
        return True
    except IOError:
        return False


def update_preference(key, value):
    """更新单个偏好设置"""
    preferences = get_preferences()
    preferences[key] = value
    return save_preferences(preferences)


def get_preference(key, default=None):
    """获取单个偏好设置"""
    preferences = get_preferences()
    return preferences.get(key, default)


def load_behavior_history():
    """加载行为历史"""
    ensure_dir()
    if os.path.exists(BEHAVIOR_HISTORY_FILE):
        try:
            with open(BEHAVIOR_HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_behavior_history(history):
    """保存行为历史"""
    ensure_dir()
    try:
        with open(BEHAVIOR_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        return True
    except IOError:
        return False


def add_behavior_record(action, details=None):
    """添加行为记录"""
    history = load_behavior_history()
    record = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details or {}
    }
    history.append(record)
    # 只保留最近1000条记录
    if len(history) > 1000:
        history = history[-1000:]
    return save_behavior_history(history)


def get_behavior_history(limit=50):
    """获取行为历史"""
    history = load_behavior_history()
    return history[-limit:] if len(history) > limit else history


def list_profiles():
    """列出所有用户画像"""
    ensure_dir()
    profiles = []
    for f in os.listdir(USER_PROFILE_DIR):
        if f.endswith('.json') and f != 'preferences.json' and f != 'behavior_history.json':
            profile_path = os.path.join(USER_PROFILE_DIR, f)
            try:
                with open(profile_path, 'r', encoding='utf-8') as pf:
                    profile_data = json.load(pf)
                    profiles.append({
                        "id": profile_data.get("profile_id", f.replace('.json', "")),
                        "name": profile_data.get("name", "未知"),
                        "updated_at": profile_data.get("updated_at", "")
                    })
            except (json.JSONDecodeError, IOError):
                pass
    return profiles


def create_profile(profile_id, name, template="default"):
    """创建新用户画像"""
    if template == "default":
        profile = init_default_profile()
    else:
        profile = load_profile(template)

    profile["profile_id"] = profile_id
    profile["name"] = name
    profile["created_at"] = datetime.now().isoformat()
    profile["updated_at"] = datetime.now().isoformat()

    return save_profile(profile)


def delete_profile(profile_id):
    """删除用户画像"""
    if profile_id == "default":
        return False  # 不能删除默认画像

    profile_path = os.path.join(USER_PROFILE_DIR, f"{profile_id}.json")
    if os.path.exists(profile_path):
        try:
            os.remove(profile_path)
            return True
        except OSError:
            return False
    return False


def set_theme(theme):
    """设置主题"""
    profile = load_profile()
    profile["appearance"]["theme"] = theme
    add_behavior_record("theme_change", {"theme": theme})
    return save_profile(profile)


def set_language(language):
    """设置语言"""
    profile = load_profile()
    profile["personal_info"]["language"] = language
    add_behavior_record("language_change", {"language": language})
    return save_profile(profile)


def set_notification_enabled(enabled):
    """设置通知启用状态"""
    profile = load_profile()
    profile["notifications"]["enabled"] = enabled
    add_behavior_record("notification_change", {"enabled": enabled})
    return save_profile(profile)


def export_profile(profile_id="default"):
    """导出用户画像"""
    profile = load_profile(profile_id)
    export_path = os.path.join(USER_PROFILE_DIR, f"{profile_id}_export.json")
    try:
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
        return export_path
    except IOError:
        return None


def import_profile(import_path):
    """导入用户画像"""
    try:
        with open(import_path, 'r', encoding='utf-8') as f:
            profile = json.load(f)

        # 重新设置时间戳
        profile["updated_at"] = datetime.now().isoformat()
        profile_id = profile.get("profile_id", "imported")

        # 保存
        save_profile(profile)
        add_behavior_record("profile_import", {"profile_id": profile_id})
        return True
    except (IOError, json.JSONDecodeError):
        return False


def show_status():
    """显示用户画像状态"""
    profile = load_profile()
    preferences = get_preferences()
    history_count = len(load_behavior_history())

    print(f"=== LLM-OS 用户画像状态 ===")
    print(f"当前用户: {profile.get('name', '未知')}")
    print(f"主题: {profile.get('appearance', {}).get('theme', 'unknown')}")
    print(f"语言: {profile.get('personal_info', {}).get('language', 'unknown')}")
    print(f"通知: {'已启用' if profile.get('notifications', {}).get('enabled', False) else '已禁用'}")
    print(f"自定义偏好数: {len(preferences)}")
    print(f"行为记录数: {history_count}")
    print(f"========================")


def show_profile():
    """显示完整用户画像"""
    profile = load_profile()
    print(f"=== 用户画像详情 ===")
    print(json.dumps(profile, ensure_ascii=False, indent=2))


def show_preferences():
    """显示偏好设置"""
    preferences = get_preferences()
    if preferences:
        print(f"=== 偏好设置 ===")
        for key, value in preferences.items():
            print(f"  {key}: {value}")
    else:
        print("暂无自定义偏好设置")


def show_behavior_history(limit=10):
    """显示行为历史"""
    history = get_behavior_history(limit)
    if history:
        print(f"=== 最近 {len(history)} 条行为记录 ===")
        for record in reversed(history):
            timestamp = record.get("timestamp", "")[:19]
            action = record.get("action", "")
            details = record.get("details", {})
            print(f"  {timestamp} - {action}: {details}")
    else:
        print("暂无行为记录")


def handle_command(args):
    """处理命令行参数"""
    if not args or args[0] == "--help":
        print("""
LLM-OS 用户画像与偏好管理模块

用法:
  python llm_os_user_profile.py --version              显示版本
  python llm_os_user_profile.py --status                显示状态
  python llm_os_user_profile.py --show-profile           显示完整画像
  python llm_os_user_profile.py --show-prefs            显示偏好设置
  python llm_os_user_profile.py --history [N]           显示最近N条行为历史
  python llm_os_user_profile.py --list-profiles         列出所有画像
  python llm_os_user_profile.py --set-theme <theme>    设置主题 (light/dark)
  python llm_os_user_profile.py --set-lang <lang>       设置语言
  python llm_os_user_profile.py --set-notify <on/off>   启用/禁用通知
  python llm_os_user_profile.py --add-pref <key> <value> 添加偏好设置
  python llm_os_user_profile.py --get-pref <key>       获取偏好设置
  python llm_os_user_profile.py --create-profile <id> <name> 创建新画像
  python llm_os_user_profile.py --delete-profile <id>  删除画像
  python llm_os_user_profile.py --export-profile        导出当前画像
  python llm_os_user_profile.py --import-profile <path> 导入画像
""")
        return

    arg = args[0]

    if arg == "--version":
        print(f"llm_os_user_profile.py version {get_version()}")
        return

    if arg == "--status":
        show_status()
        return

    if arg == "--show-profile":
        show_profile()
        return

    if arg == "--show-prefs":
        show_preferences()
        return

    if arg == "--history":
        limit = int(args[1]) if len(args) > 1 else 10
        show_behavior_history(limit)
        return

    if arg == "--list-profiles":
        profiles = list_profiles()
        print("=== 用户画像列表 ===")
        for p in profiles:
            print(f"  {p['id']}: {p['name']} (更新于 {p['updated_at'][:10]})")
        return

    if arg == "--set-theme":
        if len(args) < 2:
            print("错误: 请指定主题 (light/dark)")
            return
        theme = args[1]
        if set_theme(theme):
            print(f"主题已设置为: {theme}")
            add_behavior_record("manual_theme_change", {"theme": theme})
        else:
            print("设置主题失败")
        return

    if arg == "--set-lang":
        if len(args) < 2:
            print("错误: 请指定语言")
            return
        lang = args[1]
        if set_language(lang):
            print(f"语言已设置为: {lang}")
            add_behavior_record("manual_language_change", {"language": lang})
        else:
            print("设置语言失败")
        return

    if arg == "--set-notify":
        if len(args) < 2:
            print("错误: 请指定 on 或 off")
            return
        enabled = args[1].lower() == "on"
        if set_notification_enabled(enabled):
            print(f"通知已{'启用' if enabled else '禁用'}")
            add_behavior_record("manual_notification_change", {"enabled": enabled})
        else:
            print("设置通知失败")
        return

    if arg == "--add-pref":
        if len(args) < 3:
            print("错误: 请指定 key 和 value")
            return
        key, value = args[1], args[2]
        if update_preference(key, value):
            print(f"偏好设置已添加: {key} = {value}")
            add_behavior_record("preference_added", {"key": key, "value": value})
        else:
            print("添加偏好设置失败")
        return

    if arg == "--get-pref":
        if len(args) < 2:
            print("错误: 请指定 key")
            return
        key = args[1]
        value = get_preference(key)
        print(f"{key}: {value}")
        return

    if arg == "--create-profile":
        if len(args) < 3:
            print("错误: 请指定 profile_id 和 name")
            return
        profile_id, name = args[1], args[2]
        if create_profile(profile_id, name):
            print(f"用户画像已创建: {profile_id} ({name})")
            add_behavior_record("profile_created", {"profile_id": profile_id, "name": name})
        else:
            print("创建用户画像失败")
        return

    if arg == "--delete-profile":
        if len(args) < 2:
            print("错误: 请指定 profile_id")
            return
        profile_id = args[1]
        if delete_profile(profile_id):
            print(f"用户画像已删除: {profile_id}")
            add_behavior_record("profile_deleted", {"profile_id": profile_id})
        else:
            print("删除用户画像失败")
        return

    if arg == "--export-profile":
        path = export_profile()
        if path:
            print(f"用户画像已导出到: {path}")
        else:
            print("导出用户画像失败")
        return

    if arg == "--import-profile":
        if len(args) < 2:
            print("错误: 请指定导入文件路径")
            return
        import_path = args[1]
        if import_profile(import_path):
            print("用户画像导入成功")
        else:
            print("导入用户画像失败")
        return

    print(f"未知参数: {arg}")
    print("使用 --help 查看帮助")


if __name__ == "__main__":
    handle_command(sys.argv[1:])