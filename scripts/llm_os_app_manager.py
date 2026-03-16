#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-OS 应用管理器 - 提供已安装应用分析、应用使用统计、应用分类、应用搜索等能力

本模块实现应用管理功能，支持：
1. 已安装应用列表（从注册表获取）
2. 应用使用统计（启动次数、最后使用时间）
3. 应用分类（系统应用、办公应用、开发工具等）
4. 应用搜索（按名称搜索应用）
5. 推荐常用应用（基于使用频率）

版本: 1.0.0
依赖: winreg (Windows注册表), os, json, datetime
"""

import os
import sys
import json
import subprocess
import winreg
import argparse
from datetime import datetime
from pathlib import Path

# 添加脚本目录到路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 配置文件路径
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".friday", "llm_os")
APP_STATS_FILE = os.path.join(CONFIG_DIR, "app_usage_stats.json")
APP_CATEGORIES_FILE = os.path.join(CONFIG_DIR, "app_categories.json")


def ensure_config_dir():
    """确保配置目录存在"""
    os.makedirs(CONFIG_DIR, exist_ok=True)


def get_installed_apps():
    """获取已安装的应用列表"""
    apps = []

    # 从注册表获取已安装应用
    registry_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]

    for hkey, path in registry_paths:
        try:
            key = winreg.OpenKey(hkey, path)
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey_path = path + "\\" + subkey_name

                    try:
                        subkey = winreg.OpenKey(hkey, subkey_path)
                        try:
                            name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                        except:
                            name = ""
                        display_version = ""
                        publisher = ""
                        install_location = ""
                        try:
                            display_version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                        except:
                            pass
                        try:
                            publisher = winreg.QueryValueEx(subkey, "Publisher")[0]
                        except:
                            pass
                        try:
                            install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                        except:
                            pass

                        # 过滤掉系统组件和无名应用
                        if name and not name.startswith("KB") and "Update" not in name:
                            # 检查是否已存在（去重）
                            if not any(app['name'] == name for app in apps):
                                apps.append({
                                    'name': name,
                                    'version': display_version,
                                    'publisher': publisher,
                                    'install_location': install_location
                                })
                        winreg.CloseKey(subkey)
                    except:
                        pass
                except OSError:
                    break
                i += 1
            winreg.CloseKey(key)
        except:
            pass

    # 按名称排序
    apps.sort(key=lambda x: x['name'].lower())
    return apps


def load_app_stats():
    """加载应用使用统计"""
    ensure_config_dir()
    if os.path.exists(APP_STATS_FILE):
        try:
            with open(APP_STATS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}


def save_app_stats(stats):
    """保存应用使用统计"""
    ensure_config_dir()
    with open(APP_STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


def record_app_launch(app_name):
    """记录应用启动"""
    stats = load_app_stats()
    app_key = app_name.lower()

    if app_key not in stats:
        stats[app_key] = {
            'name': app_name,
            'launch_count': 0,
            'first_launch': datetime.now().isoformat(),
            'last_launch': None
        }

    stats[app_key]['launch_count'] += 1
    stats[app_key]['last_launch'] = datetime.now().isoformat()
    save_app_stats(stats)


def get_app_categories():
    """获取应用分类配置"""
    ensure_config_dir()
    if os.path.exists(APP_CATEGORIES_FILE):
        try:
            with open(APP_CATEGORIES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass

    # 默认分类
    default_categories = {
        "系统工具": ["Windows", "Microsoft", "System", "Control Panel", "Settings"],
        "办公": ["Office", "Word", "Excel", "PowerPoint", "PDF", "WPS", "钉钉", "企业微信", "飞书"],
        "开发工具": ["Visual Studio", "VS Code", "IntelliJ", "PyCharm", "Git", "Python", "Node", "Java"],
        "浏览器": ["Chrome", "Edge", "Firefox", "Safari", "Browser", "浏览器"],
        "通讯": ["微信", "QQ", "钉钉", "企业微信", "飞书", "Slack", "Teams", "Zoom"],
        "多媒体": ["音乐", "视频", "播放器", "Media", "Player", "Camera", "截图"],
        "设计": ["Photoshop", "Illustrator", "Figma", "Sketch", "设计", "CAD"],
        "游戏": ["Game", "Steam", "Epic", "游戏"]
    }
    return default_categories


def categorize_app(app_name):
    """为应用分配类别"""
    categories = get_app_categories()

    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword.lower() in app_name.lower():
                return category

    return "其他"


def search_apps(keyword, apps):
    """搜索应用"""
    keyword_lower = keyword.lower()
    return [app for app in apps if keyword_lower in app['name'].lower()]


def get_top_apps(apps, stats, limit=10):
    """获取使用最频繁的应用"""
    app_stats = []

    for app in apps:
        app_key = app['name'].lower()
        if app_key in stats:
            app_stats.append({
                'name': app['name'],
                'version': app['version'],
                'launch_count': stats[app_key]['launch_count'],
                'last_launch': stats[app_key].get('last_launch')
            })
        else:
            app_stats.append({
                'name': app['name'],
                'version': app['version'],
                'launch_count': 0,
                'last_launch': None
            })

    # 按启动次数排序
    app_stats.sort(key=lambda x: x['launch_count'], reverse=True)
    return app_stats[:limit]


def list_apps_by_category(apps):
    """按类别列出应用"""
    categorized = {}

    for app in apps:
        category = categorize_app(app['name'])
        if category not in categorized:
            categorized[category] = []
        categorized[category].append(app)

    return categorized


def main():
    """主函数"""
    # 解决 Windows 控制台编码问题
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

    parser = argparse.ArgumentParser(
        description='LLM-OS 应用管理器 - 管理已安装应用、统计使用情况、提供搜索和推荐功能'
    )
    parser.add_argument('--version', action='store_true', help='显示版本信息')
    parser.add_argument('--list', action='store_true', help='列出所有已安装应用')
    parser.add_argument('--search', type=str, help='搜索应用')
    parser.add_argument('--stats', action='store_true', help='显示应用使用统计')
    parser.add_argument('--top', type=int, default=10, help='显示最常用的应用数量 (默认10)')
    parser.add_argument('--category', action='store_true', help='按类别显示应用')
    parser.add_argument('--record-launch', type=str, help='记录应用启动')
    parser.add_argument('--info', type=str, help='显示应用详情')

    args = parser.parse_args()

    if args.version:
        print("LLM-OS 应用管理器 version 1.0.0")
        return

    if args.list:
        apps = get_installed_apps()
        print(f"已安装应用数量: {len(apps)}")
        print("\n已安装应用列表:")
        for i, app in enumerate(apps, 1):
            print(f"  {i}. {app['name']} (v{app['version']}) - {app['publisher']}")
        return

    if args.search:
        apps = get_installed_apps()
        results = search_apps(args.search, apps)
        print(f"搜索结果: {len(results)} 个应用匹配 '{args.search}'")
        for i, app in enumerate(results, 1):
            print(f"  {i}. {app['name']} (v{app['version']})")
        return

    if args.stats:
        stats = load_app_stats()
        apps = get_installed_apps()
        top_apps = get_top_apps(apps, stats, args.top)

        print(f"应用使用统计 (Top {args.top}):")
        for i, app in enumerate(top_apps, 1):
            print(f"  {i}. {app['name']} - 启动 {app['launch_count']} 次")
            if app['last_launch']:
                print(f"     最后使用: {app['last_launch']}")
        return

    if args.category:
        apps = get_installed_apps()
        categorized = list_apps_by_category(apps)

        print("按类别显示应用:")
        for category, app_list in sorted(categorized.items()):
            print(f"\n{category} ({len(app_list)} 个应用):")
            for app in app_list[:5]:  # 每类只显示前5个
                print(f"  - {app['name']}")
            if len(app_list) > 5:
                print(f"  ... 还有 {len(app_list) - 5} 个")
        return

    if args.record_launch:
        record_app_launch(args.record_launch)
        print(f"已记录应用启动: {args.record_launch}")
        return

    if args.info:
        apps = get_installed_apps()
        for app in apps:
            if args.info.lower() in app['name'].lower():
                print(f"应用名称: {app['name']}")
                print(f"版本: {app['version']}")
                print(f"发布者: {app['publisher']}")
                print(f"安装位置: {app['install_location']}")

                # 显示使用统计
                stats = load_app_stats()
                app_key = app['name'].lower()
                if app_key in stats:
                    print(f"启动次数: {stats[app_key]['launch_count']}")
                    if stats[app_key].get('last_launch'):
                        print(f"最后使用: {stats[app_key]['last_launch']}")
                return
        print(f"未找到应用: {args.info}")
        return

    # 默认显示状态
    apps = get_installed_apps()
    stats = load_app_stats()
    print(f"LLM-OS 应用管理器 v1.0.0")
    print(f"已安装应用: {len(apps)} 个")
    print(f"已记录使用统计: {len(stats)} 个应用")
    print("\n使用 --help 查看更多选项")


if __name__ == '__main__':
    main()