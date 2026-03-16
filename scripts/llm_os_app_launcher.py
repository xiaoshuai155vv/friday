#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-OS 虚拟应用启动器 - 提供快速启动常用应用、常用网站、系统功能的统一入口

本模块实现虚拟应用启动器功能，支持：
1. 常用应用快捷启动（用户配置或自动学习）
2. 常用网站快捷启动（打开浏览器并导航到URL）
3. 系统功能快速访问（控制面板、系统设置等）
4. 快捷方式管理（添加、删除、查看）

版本: 1.0.0
依赖: launch_* 脚本, launch_browser, keyboard_tool, window_tool 等
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path

# 添加脚本目录到路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 配置文件路径
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".friday", "llm_os")
CONFIG_FILE = os.path.join(CONFIG_DIR, "app_launcher_config.json")


def load_config():
    """加载配置文件"""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    # 返回默认配置
    return get_default_config()


def save_config(config):
    """保存配置文件"""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def get_default_config():
    """获取默认配置（常用应用和网站）"""
    return {
        "apps": {
            "微信": "WeChat",
            "钉钉": "DingTalk",
            "QQ": "QQ",
            "钉钉": "DingTalk",
            "记事本": "notepad",
            "计算器": "calculator",
            "画图": "mspaint",
            "截图": "snippingtool",
            "命令提示符": "cmd",
            "PowerShell": "powershell",
            "文件管理器": "explorer",
            "浏览器": "msedge",
            "网易云音乐": "cloudmusic",
            "VS Code": "Code",
            "Notepad++": "notepad++"
        },
        "websites": {
            "百度": "https://www.baidu.com",
            "谷歌": "https://www.google.com",
            "知乎": "https://www.zhihu.com",
            "GitHub": "https://github.com",
            "B站": "https://www.bilibili.com",
            "邮箱": "https://mail.qq.com",
            "淘宝": "https://www.taobao.com",
            "京东": "https://www.jd.com"
        },
        "system": {
            "控制面板": "control",
            "设置": "ms-settings:",
            "任务管理器": "taskmgr",
            "设备管理器": "devmgmt.msc",
            "磁盘管理": "diskmgmt.msc",
            "网络连接": "ncpa.cpl",
            "系统信息": "msinfo32",
            "命令提示符": "cmd",
            "PowerShell": "powershell",
            "资源管理器": "explorer",
            "计算器": "calc",
            "截图工具": "snippingtool",
            "画图": "mspaint"
        },
        "favorites": []  # 用户收藏的快捷方式
    }


def launch_application(app_name):
    """启动应用程序"""
    # 尝试直接通过名称启动
    do_py = os.path.join(SCRIPT_DIR, "..", "do.py")
    if os.path.exists(do_py):
        result = subprocess.run(
            [sys.executable, do_py, "打开应用", app_name],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return True, f"应用 {app_name} 已启动"

    # 备用：使用 Win+R 启动
    try:
        keyboard_tool = os.path.join(SCRIPT_DIR, "keyboard_tool.py")

        # 按 Win+R
        subprocess.run([sys.executable, keyboard_tool, "key", "91"], timeout=2)
        time.sleep(0.3)
        subprocess.run([sys.executable, keyboard_tool, "key", "82"], timeout=2)
        time.sleep(0.5)

        # 输入应用名称
        subprocess.run([sys.executable, keyboard_tool, "type", app_name], timeout=2)
        time.sleep(0.5)

        # 按 Enter
        subprocess.run([sys.executable, keyboard_tool, "key", "13"], timeout=2)

        return True, f"应用 {app_name} 已通过 Win+R 启动"
    except Exception as e:
        return False, f"启动失败: {str(e)}"


def launch_website(name, url=None):
    """启动网站"""
    # 如果没有提供 URL，尝试从配置中查找
    if url is None:
        config = load_config()
        url = config.get("websites", {}).get(name)

    if url is None:
        return False, f"未找到网站: {name}"

    # 使用 launch_browser 打开网站
    launch_browser = os.path.join(SCRIPT_DIR, "launch_browser.py")
    if os.path.exists(launch_browser):
        result = subprocess.run(
            [sys.executable, launch_browser, url],
            capture_output=True,
            text=True,
            timeout=15
        )
        if result.returncode == 0:
            # 等待浏览器启动并最大化
            time.sleep(1)
            window_tool = os.path.join(SCRIPT_DIR, "window_tool.py")
            # 尝试获取浏览器窗口并最大化
            browser_title = url.split("//")[-1].split("/")[0] if "://" in url else url
            subprocess.run(
                [sys.executable, window_tool, "maximize", browser_title],
                capture_output=True,
                timeout=5
            )
            return True, f"网站 {name} 已打开: {url}"

    # 备用：使用系统默认浏览器
    try:
        os.startfile(url)
        return True, f"网站 {name} 已通过系统默认浏览器打开"
    except Exception as e:
        return False, f"打开网站失败: {str(e)}"


def launch_system_function(function_name):
    """启动系统功能"""
    config = load_config()
    system_cmds = config.get("system", {})

    cmd = system_cmds.get(function_name)
    if cmd is None:
        return False, f"未找到系统功能: {function_name}"

    try:
        # 使用系统命令启动
        subprocess.run(cmd, shell=True, timeout=5)
        return True, f"系统功能 {function_name} 已启动"
    except Exception as e:
        return False, f"启动失败: {str(e)}"


def list_shortcuts():
    """列出所有可用快捷方式"""
    config = load_config()

    output = ["=== 常用应用 ==="]
    for name in config.get("apps", {}).keys():
        output.append(f"  - {name}")

    output.append("\n=== 常用网站 ===")
    for name in config.get("websites", {}).keys():
        output.append(f"  - {name}")

    output.append("\n=== 系统功能 ===")
    for name in config.get("system", {}).keys():
        output.append(f"  - {name}")

    if config.get("favorites"):
        output.append("\n=== 收藏夹 ===")
        for fav in config.get("favorites", []):
            output.append(f"  - {fav}")

    return "\n".join(output)


def add_favorite(name, target, type="app"):
    """添加收藏"""
    config = load_config()
    favorites = config.get("favorites", [])

    # 检查是否已存在
    for fav in favorites:
        if fav.get("name") == name:
            return False, f"收藏 {name} 已存在"

    favorites.append({
        "name": name,
        "target": target,
        "type": type
    })
    config["favorites"] = favorites
    save_config(config)
    return True, f"已添加收藏: {name}"


def remove_favorite(name):
    """删除收藏"""
    config = load_config()
    favorites = config.get("favorites", [])

    new_favorites = [f for f in favorites if f.get("name") != name]
    if len(new_favorites) == len(favorites):
        return False, f"未找到收藏: {name}"

    config["favorites"] = new_favorites
    save_config(config)
    return True, f"已删除收藏: {name}"


def launch_favorite(name):
    """启动收藏"""
    config = load_config()
    favorites = config.get("favorites", [])

    for fav in favorites:
        if fav.get("name") == name:
            fav_type = fav.get("type", "app")
            target = fav.get("target")

            if fav_type == "app":
                return launch_application(target)
            elif fav_type == "website":
                return launch_website(target)  # target 是 URL
            elif fav_type == "system":
                return launch_system_function(target)

    return False, f"未找到收藏: {name}"


def get_status():
    """获取启动器状态"""
    config = load_config()
    return {
        "apps_count": len(config.get("apps", {})),
        "websites_count": len(config.get("websites", {})),
        "system_count": len(config.get("system", {})),
        "favorites_count": len(config.get("favorites", []))
    }


def main():
    import argparse
    import io

    # 设置标准输出编码为 UTF-8
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    parser = argparse.ArgumentParser(
        description="LLM-OS 虚拟应用启动器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
用法示例:
  python llm_os_app_launcher.py --launch-app 微信
  python llm_os_app_launcher.py --launch-website 百度
  python llm_os_app_launcher.py --launch-system 控制面板
  python llm_os_app_launcher.py --list
  python llm_os_app_launcher.py --add-favorite 我的应用 微信 app
  python llm_os_app_launcher.py --status
        """
    )

    # 启动应用
    parser.add_argument("--launch-app", "-la", type=str,
                        help="启动应用程序（按名称）")

    # 启动网站
    parser.add_argument("--launch-website", "-lw", type=str,
                        help="启动网站（按名称或URL）")

    # 启动系统功能
    parser.add_argument("--launch-system", "-ls", type=str,
                        help="启动系统功能（按名称）")

    # 列出快捷方式
    parser.add_argument("--list", "-l", action="store_true",
                        help="列出所有可用快捷方式")

    # 收藏夹管理
    parser.add_argument("--add-favorite", "-af", nargs=3, metavar=("NAME", "TARGET", "TYPE"),
                        help="添加收藏: NAME TARGET TYPE(app/website/system)")
    parser.add_argument("--remove-favorite", "-rf", type=str,
                        help="删除收藏")
    parser.add_argument("--launch-favorite", "-lf", type=str,
                        help="启动收藏")

    # 状态
    parser.add_argument("--status", "-s", action="store_true",
                        help="获取启动器状态")

    # 版本
    parser.add_argument("--version", "-v", action="store_true",
                        help="显示版本信息")

    args = parser.parse_args()

    if args.version:
        print("LLM-OS 虚拟应用启动器 v1.0.0")
        return

    if args.status:
        status = get_status()
        print("=== 虚拟应用启动器状态 ===")
        print(f"  应用快捷: {status['apps_count']} 个")
        print(f"  网站快捷: {status['websites_count']} 个")
        print(f"  系统功能: {status['system_count']} 个")
        print(f"  收藏夹:   {status['favorites_count']} 个")
        return

    if args.list:
        print("=== LLM-OS 快捷方式列表 ===")
        print(list_shortcuts())
        return

    if args.launch_app:
        success, msg = launch_application(args.launch_app)
        print("✓" if success else "✗", msg)
        sys.exit(0 if success else 1)

    if args.launch_website:
        success, msg = launch_website(args.launch_website)
        print("✓" if success else "✗", msg)
        sys.exit(0 if success else 1)

    if args.launch_system:
        success, msg = launch_system_function(args.launch_system)
        print("✓" if success else "✗", msg)
        sys.exit(0 if success else 1)

    if args.add_favorite:
        name, target, fav_type = args.add_favorite
        success, msg = add_favorite(name, target, fav_type)
        print("✓" if success else "✗", msg)
        sys.exit(0 if success else 1)

    if args.remove_favorite:
        success, msg = remove_favorite(args.remove_favorite)
        print("✓" if success else "✗", msg)
        sys.exit(0 if success else 1)

    if args.launch_favorite:
        success, msg = launch_favorite(args.launch_favorite)
        print("✓" if success else "✗", msg)
        sys.exit(0 if success else 1)

    # 如果没有参数，显示帮助
    parser.print_help()


if __name__ == "__main__":
    main()