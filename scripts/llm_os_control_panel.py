#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-OS 控制面板 - 整合现有能力的统一入口

本脚本整合窗口管理、进程管理、应用启动等能力，提供统一的 LLM-OS 桌面操作系统控制能力。
基于已有的大量进化引擎能力，构建桌面操作系统级别的控制接口。

版本: 1.0.0
依赖: window_tool, process_tool, launch_* 脚本, file_tool 等
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# 添加脚本目录到路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def list_windows():
    """列出所有打开的窗口"""
    window_tool = os.path.join(SCRIPT_DIR, "window_tool.py")
    result = subprocess.run(
        [sys.executable, window_tool, "list"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.stdout


def list_processes():
    """列出所有运行中的进程"""
    process_tool = os.path.join(SCRIPT_DIR, "process_tool.py")
    result = subprocess.run(
        [sys.executable, process_tool, "list"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.stdout


def list_installed_apps():
    """列出已安装的应用"""
    installed_apps = os.path.join(SCRIPT_DIR, "installed_apps_tool.py")
    result = subprocess.run(
        [sys.executable, installed_apps],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.stdout


def activate_window(title):
    """激活指定窗口"""
    window_tool = os.path.join(SCRIPT_DIR, "window_tool.py")
    result = subprocess.run(
        [sys.executable, window_tool, "activate", title],
        capture_output=True,
        text=True
    )
    return result.returncode == 0


def maximize_window(title):
    """最大化指定窗口"""
    window_tool = os.path.join(SCRIPT_DIR, "window_tool.py")
    result = subprocess.run(
        [sys.executable, window_tool, "maximize", title],
        capture_output=True,
        text=True
    )
    return result.returncode == 0


def minimize_window(title):
    """最小化指定窗口"""
    window_tool = os.path.join(SCRIPT_DIR, "window_tool.py")
    result = subprocess.run(
        [sys.executable, window_tool, "minimize", title],
        capture_output=True,
        text=True
    )
    return result.returncode == 0


def close_window(title):
    """关闭指定窗口"""
    window_tool = os.path.join(SCRIPT_DIR, "window_tool.py")
    result = subprocess.run(
        [sys.executable, window_tool, "close", title],
        capture_output=True,
        text=True
    )
    return result.returncode == 0


def get_system_info():
    """获取系统信息 - 使用系统已有命令"""
    import platform
    import subprocess
    import os

    info = {
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.architecture(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }

    # 获取内存信息 (Windows)
    if os.name == 'nt':
        try:
            result = subprocess.run(
                ["wmic", "OS", "get", "FreePhysicalMemory,TotalVisibleMemorySize", "/Value"],
                capture_output=True, text=True
            )
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'FreePhysicalMemory' in line:
                    info["free_memory_kb"] = line.split('=')[-1]
                elif 'TotalVisibleMemorySize' in line:
                    info["total_memory_kb"] = line.split('=')[-1]
        except:
            pass

    # 获取 CPU 使用率
    try:
        result = subprocess.run(
            ["wmic", "cpu", "get", "loadpercentage"],
            capture_output=True, text=True
        )
        lines = result.stdout.strip().split('\n')
        for line in lines:
            if line.isdigit():
                info["cpu_percent"] = int(line)
                break
    except:
        pass

    return info


def launch_app(app_name):
    """启动应用"""
    # 尝试使用 do.py 打开应用
    do_py = os.path.join(SCRIPT_DIR, "..", "do.py")
    if os.path.exists(do_py):
        result = subprocess.run(
            [sys.executable, do_py, "打开应用", app_name],
            capture_output=True,
            text=True
        )
        return result.returncode == 0

    # 备用：使用 Win+R 启动
    keyboard_tool = os.path.join(SCRIPT_DIR, "keyboard_tool.py")
    subprocess.run([sys.executable, keyboard_tool, "keys", "91", "82"])  # Win+R
    import time
    time.sleep(0.5)
    subprocess.run([sys.executable, keyboard_tool, "type", app_name])
    time.sleep(0.5)
    subprocess.run([sys.executable, keyboard_tool, "key", "13"])  # Enter
    return True


def arrange_windows(action):
    """执行窗口排列操作"""
    window_arrange = os.path.join(SCRIPT_DIR, "llm_os_window_arrange.py")
    result = subprocess.run(
        [sys.executable, window_arrange, action],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.stdout, result.returncode


def launch_app_launcher(action, target=None):
    """执行虚拟应用启动器操作"""
    app_launcher = os.path.join(SCRIPT_DIR, "llm_os_app_launcher.py")
    cmd = [sys.executable, app_launcher]

    if action == "list":
        cmd.append("--list")
    elif action == "status":
        cmd.append("--status")
    elif action == "launch-app" and target:
        cmd.extend(["--launch-app", target])
    elif action == "launch-website" and target:
        cmd.extend(["--launch-website", target])
    elif action == "launch-system" and target:
        cmd.extend(["--launch-system", target])

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.stdout, result.returncode


def multidisplay_list():
    """列出所有显示器信息"""
    multidisplay = os.path.join(SCRIPT_DIR, "llm_os_multidisplay.py")
    result = subprocess.run(
        [sys.executable, multidisplay, "--list"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.stdout


def multidisplay_move_window(window_title, display_index):
    """将窗口移动到指定显示器"""
    multidisplay = os.path.join(SCRIPT_DIR, "llm_os_multidisplay.py")
    result = subprocess.run(
        [sys.executable, multidisplay, "--move-window", window_title, str(display_index)],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.stdout, result.returncode


def multidisplay_mirror_window(window_title, display_index):
    """将窗口镜像到指定显示器"""
    multidisplay = os.path.join(SCRIPT_DIR, "llm_os_multidisplay.py")
    result = subprocess.run(
        [sys.executable, multidisplay, "--mirror-window", window_title, str(display_index)],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.stdout, result.returncode


def multidisplay_window_display(window_title):
    """获取窗口当前所在的显示器"""
    multidisplay = os.path.join(SCRIPT_DIR, "llm_os_multidisplay.py")
    result = subprocess.run(
        [sys.executable, multidisplay, "--window-display", window_title],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.stdout, result.returncode


def task_manager_list(top_n=None):
    """获取进程列表（任务管理器）"""
    task_manager = os.path.join(SCRIPT_DIR, "llm_os_task_manager.py")
    cmd = [sys.executable, task_manager]
    if top_n:
        cmd.extend(["--top", str(top_n)])
    else:
        cmd.append("--list")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.stdout


def task_manager_resources():
    """获取系统资源使用情况"""
    task_manager = os.path.join(SCRIPT_DIR, "llm_os_task_manager.py")
    result = subprocess.run(
        [sys.executable, task_manager, "--resources"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.stdout


def task_manager_kill(process_name):
    """结束进程"""
    task_manager = os.path.join(SCRIPT_DIR, "llm_os_task_manager.py")
    result = subprocess.run(
        [sys.executable, task_manager, "--kill", process_name],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.stdout, result.returncode


def task_manager_services():
    """列出 Windows 服务"""
    task_manager = os.path.join(SCRIPT_DIR, "llm_os_task_manager.py")
    result = subprocess.run(
        [sys.executable, task_manager, "--services"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.stdout


# ========== 文件管理器函数 ==========

def file_manager_list(path=None, show_hidden=False, sort_by="name"):
    """列出目录内容"""
    file_manager = os.path.join(SCRIPT_DIR, "llm_os_file_manager.py")
    cmd = [sys.executable, file_manager, "list"]
    if path:
        cmd.append(path)
    if show_hidden:
        cmd.append("--hidden")
    cmd.extend(["--sort", sort_by])

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.stdout


def file_manager_search(path, pattern, recursive=False, max_results=100):
    """搜索文件"""
    file_manager = os.path.join(SCRIPT_DIR, "llm_os_file_manager.py")
    cmd = [sys.executable, file_manager, "search", path, pattern]
    if recursive:
        cmd.append("-r")
    cmd.extend(["-m", str(max_results)])

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.stdout


def file_manager_info(path):
    """获取文件信息"""
    file_manager = os.path.join(SCRIPT_DIR, "llm_os_file_manager.py")
    result = subprocess.run(
        [sys.executable, file_manager, "info", path],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.stdout


def file_manager_copy(source, destination, force=False):
    """复制文件或目录"""
    file_manager = os.path.join(SCRIPT_DIR, "llm_os_file_manager.py")
    cmd = [sys.executable, file_manager, "copy", source, destination]
    if force:
        cmd.append("-f")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.stdout, result.returncode


def file_manager_move(source, destination, force=False):
    """移动/重命名文件或目录"""
    file_manager = os.path.join(SCRIPT_DIR, "llm_os_file_manager.py")
    cmd = [sys.executable, file_manager, "move", source, destination]
    if force:
        cmd.append("-f")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.stdout, result.returncode


def file_manager_delete(path, recursive=False):
    """删除文件或目录"""
    file_manager = os.path.join(SCRIPT_DIR, "llm_os_file_manager.py")
    cmd = [sys.executable, file_manager, "delete", path]
    if recursive:
        cmd.append("-r")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.stdout, result.returncode


def file_manager_create(path, is_directory=False, content=""):
    """新建文件或目录"""
    file_manager = os.path.join(SCRIPT_DIR, "llm_os_file_manager.py")
    cmd = [sys.executable, file_manager, "create", path]
    if is_directory:
        cmd.append("-d")
    if content:
        cmd.extend(["-c", content])

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.stdout, result.returncode


def file_manager_disk(path=None):
    """获取磁盘使用情况"""
    file_manager = os.path.join(SCRIPT_DIR, "llm_os_file_manager.py")
    cmd = [sys.executable, file_manager, "disk"]
    if path:
        cmd.append(path)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.stdout


def file_manager_quick():
    """获取快速访问位置"""
    file_manager = os.path.join(SCRIPT_DIR, "llm_os_file_manager.py")
    result = subprocess.run(
        [sys.executable, file_manager, "quick"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.stdout


# ========== 系统设置函数 ==========

def settings_brightness(action, value=None):
    """亮度控制"""
    settings = os.path.join(SCRIPT_DIR, "llm_os_settings.py")
    cmd = [sys.executable, settings, "--brightness"]
    if action == "get":
        cmd.append("get")
    elif action == "set" and value is not None:
        cmd.extend(["--brightness", str(value)])
    elif action == "up":
        cmd.append("up")
    elif action == "down":
        cmd.append("down")

    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return result.stdout


def settings_volume(action, value=None):
    """音量控制"""
    settings = os.path.join(SCRIPT_DIR, "llm_os_settings.py")
    cmd = [sys.executable, settings, "--volume"]
    if action == "get":
        cmd.append("get")
    elif action == "set" and value is not None:
        cmd.extend(["--volume", str(value)])
    elif action == "up":
        cmd.append("up")
    elif action == "down":
        cmd.append("down")
    elif action == "mute":
        cmd.append("mute")

    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return result.stdout


def settings_battery():
    """电池状态"""
    settings = os.path.join(SCRIPT_DIR, "llm_os_settings.py")
    result = subprocess.run(
        [sys.executable, settings, "--battery", "status"],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    return result.stdout


def settings_power(action, plan=None):
    """电源管理"""
    settings = os.path.join(SCRIPT_DIR, "llm_os_settings.py")
    if action == "get":
        result = subprocess.run(
            [sys.executable, settings, "--power", "plan"],
            capture_output=True, text=True, encoding='utf-8', errors='replace'
        )
    elif action == "set" and plan:
        result = subprocess.run(
            [sys.executable, settings, "--power", "set", plan],
            capture_output=True, text=True, encoding='utf-8', errors='replace'
        )
    else:
        return "用法: --settings-power get 或 --settings-power set <plan>"
    return result.stdout


def settings_dark_mode(action):
    """深色模式"""
    settings = os.path.join(SCRIPT_DIR, "llm_os_settings.py")
    cmd = [sys.executable, settings, "--dark-mode"]
    if action == "get":
        cmd.append("status")
    elif action == "on":
        cmd.append("on")
    elif action == "off":
        cmd.append("off")
    elif action == "toggle":
        cmd.append("toggle")
    else:
        return "用法: --settings-dark-mode status|on|off|toggle"

    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return result.stdout


def settings_airplane_mode(action):
    """飞行模式"""
    settings = os.path.join(SCRIPT_DIR, "llm_os_settings.py")
    cmd = [sys.executable, settings, "--airplane-mode"]
    if action == "get":
        cmd.append("status")
    elif action == "on":
        cmd.append("on")
    elif action == "off":
        cmd.append("off")
    else:
        return "用法: --settings-airplane status|on|off"

    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return result.stdout


def settings_scale():
    """显示缩放"""
    settings = os.path.join(SCRIPT_DIR, "llm_os_settings.py")
    result = subprocess.run(
        [sys.executable, settings, "--scale", "status"],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    return result.stdout


def settings_wallpaper(action, path=None):
    """壁纸控制"""
    settings = os.path.join(SCRIPT_DIR, "llm_os_settings.py")
    cmd = [sys.executable, settings, "--wallpaper"]
    if action == "get":
        cmd.append("get")
    elif action == "set" and path:
        cmd.extend(["set", path])
    else:
        return "用法: --settings-wallpaper get 或 --settings-wallpaper set <path>"

    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return result.stdout


def settings_all():
    """获取所有设置概览"""
    settings = os.path.join(SCRIPT_DIR, "llm_os_settings.py")
    result = subprocess.run(
        [sys.executable, settings, "--all"],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    return result.stdout


def show_menu():
    """显示 LLM-OS 控制面板菜单"""
    menu = """
╔═══════════════════════════════════════════════════════════╗
║           LLM-OS 桌面操作系统控制面板 v1.5.0              ║
╠═══════════════════════════════════════════════════════════╣
║  1. 窗口管理                                             ║
║     - list_windows: 列出所有窗口                         ║
║     - activate <title>: 激活窗口                          ║
║     - maximize <title>: 最大化窗口                        ║
║     - minimize <title>: 最小化窗口                        ║
║     - close <title>: 关闭窗口                             ║
║                                                         ║
║  2. 窗口排列                                             ║
║     - tile: 平铺排列                                     ║
║     - cascade: 堆叠排列                                   ║
║     - center: 居中排列                                    ║
║     - left: 左半屏                                       ║
║     - right: 右半屏                                      ║
║     - maximize_all: 全部最大化                            ║
║     - minimize_all: 全部最小化                            ║
║                                                         ║
║  3. 进程管理                                             ║
║     - list_processes: 列出所有进程                       ║
║     - kill <name/pid>: 结束进程                          ║
║                                                         ║
║  4. 应用管理                                             ║
║     - list_apps: 列出已安装应用                          ║
║     - launch <name>: 启动应用                            ║
║                                                         ║
║  5. 虚拟应用启动器                                       ║
║     - list_shortcuts: 列出所有快捷方式                   ║
║     - launcher_status: 获取启动器状态                    ║
║     - quick_launch <name>: 快速启动                      ║
║                                                         ║
║  6. 系统信息                                             ║
║     - sysinfo: 获取系统信息                              ║
║                                                         ║
║  7. 文件管理 (新增!)                                    ║
║     - file_list: 列出目录内容                            ║
║     - file_search: 搜索文件                              ║
║     - file_info: 获取文件信息                            ║
║     - file_copy/move/delete: 文件操作                   ║
║     - file_disk: 磁盘使用情况                            ║
║     - file_quick: 快速访问位置                            ║
║                                                         ║
║  8. 多显示器支持 (新增!)                                 ║
║     - list_displays: 列出所有显示器                      ║
║     - move_window <title> <index>: 移动窗口到显示器      ║
║     - mirror_window <title> <index>: 镜像窗口到显示器    ║
║     - window_display <title>: 查看窗口所在显示器         ║
║                                                         ║
║  9. 任务管理器 (新增!)                                  ║
║     - task_list: 列出所有进程                            ║
║     - task_top <N>: 列出前N个进程                         ║
║     - task_resources: 查看系统资源                       ║
║     - task_kill <name/pid>: 结束进程                     ║
║     - task_services: 列出Windows服务                      ║
║                                                         ║
║  10. 任务管理器 (新增!)                                  ║
║     - task_list: 列出所有进程                            ║
║     - task_top <N>: 列出前N个进程                         ║
║     - task_resources: 查看系统资源                        ║
║     - task_kill <name\pid>: 结束进程                     ║
║     - task_services: 列出Windows服务                      ║
║                                                         ║
║  11. 系统设置 (新增!)                                    ║
║     - settings-brightness get/up/down/set <0-100>        ║
║     - settings-volume get/up/down/mute/set <0-100>      ║
║     - settings-battery: 查看电池状态                     ║
║     - settings-power get: 查看电源计划                   ║
║     - settings-power-plan <balanced/power_saver/high>   ║
║     - settings-dark-mode status/on/off/toggle           ║
║     - settings-airplane status/on/off                    ║
║     - settings-scale: 显示缩放比例                       ║
║     - settings-wallpaper get/set <path>                 ║
║     - settings-all: 所有设置概览                        ║
║                                                         ║
║  12. 退出                                                 ║
╚═══════════════════════════════════════════════════════════╝
"""
    return menu


def main():
    import argparse
    import io

    # 设置标准输出编码为 UTF-8
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    parser = argparse.ArgumentParser(
        description="LLM-OS 桌面操作系统控制面板",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=show_menu()
    )

    # 窗口管理
    parser.add_argument("--list-windows", "-lw", action="store_true",
                        help="列出所有打开的窗口")
    parser.add_argument("--activate", "-a", type=str,
                        help="激活指定窗口（按标题）")
    parser.add_argument("--maximize", "-m", type=str,
                        help="最大化指定窗口")
    parser.add_argument("--minimize", "-n", type=str,
                        help="最小化指定窗口")
    parser.add_argument("--close-window", "-c", type=str,
                        help="关闭指定窗口")

    # 窗口排列
    parser.add_argument("--tile", action="store_true",
                        help="平铺排列所有窗口")
    parser.add_argument("--cascade", action="store_true",
                        help="堆叠排列所有窗口")
    parser.add_argument("--center", action="store_true",
                        help="居中排列所有窗口")
    parser.add_argument("--left", action="store_true",
                        help="左半屏排列")
    parser.add_argument("--right", action="store_true",
                        help="右半屏排列")
    parser.add_argument("--maximize-all", action="store_true",
                        help="最大化所有窗口")
    parser.add_argument("--minimize-all", action="store_true",
                        help="最小化所有窗口")

    # 进程管理
    parser.add_argument("--list-processes", "-lp", action="store_true",
                        help="列出所有运行中的进程")
    parser.add_argument("--kill", "-k", type=str,
                        help="结束进程（进程名或PID）")

    # 应用管理
    parser.add_argument("--list-apps", "-la", action="store_true",
                        help="列出已安装应用")
    parser.add_argument("--launch", "-l", type=str,
                        help="启动应用")

    # 系统信息
    parser.add_argument("--sysinfo", "-s", action="store_true",
                        help="获取系统信息")
    parser.add_argument("--menu", action="store_true",
                        help="显示控制面板菜单")

    # 文件管理
    parser.add_argument("--explore", "-e", nargs="?", const=".",
                        help="打开文件管理器（默认当前目录）")

    # 虚拟应用启动器
    parser.add_argument("--list-shortcuts", action="store_true",
                        help="列出所有可用快捷方式")
    parser.add_argument("--launcher-status", action="store_true",
                        help="获取虚拟应用启动器状态")
    parser.add_argument("--quick-launch", "-ql", type=str,
                        help="快速启动应用/网站/系统功能（根据名称自动识别）")

    # 多显示器支持
    parser.add_argument("--list-displays", "-ld", action="store_true",
                        help="列出所有显示器信息")
    parser.add_argument("--move-window", "-mw", type=str, nargs=2,
                        metavar=('WINDOW_TITLE', 'DISPLAY_INDEX'),
                        help="将窗口移动到指定显示器（0=主显示器，1=显示器2，...）")
    parser.add_argument("--mirror-window", "-mir", type=str, nargs=2,
                        metavar=('WINDOW_TITLE', 'DISPLAY_INDEX'),
                        help="将窗口镜像到指定显示器（保持相对位置）")
    parser.add_argument("--window-display", "-wd", type=str,
                        help="查看窗口当前所在的显示器")

    # 任务管理器支持
    parser.add_argument("--task-list", "-tl", action="store_true",
                        help="列出所有进程（任务管理器）")
    parser.add_argument("--task-top", "-tt", type=int, metavar="N",
                        help="列出资源占用最高的N个进程")
    parser.add_argument("--task-resources", "-tr", action="store_true",
                        help="查看系统资源使用情况")
    parser.add_argument("--task-kill", "-tk", type=str,
                        help="结束进程（进程名或PID）")
    parser.add_argument("--task-services", "-ts", action="store_true",
                        help="列出 Windows 服务")

    # 文件管理器支持
    parser.add_argument("--file-list", "-fl", nargs="?", const=".", metavar="PATH",
                        help="列出目录内容（默认当前目录）")
    parser.add_argument("--file-hidden", action="store_true",
                        help="列出目录时显示隐藏文件（与 --file-list 配合）")
    parser.add_argument("--file-sort", choices=["name", "size", "date", "type"], default="name",
                        help="目录列表排序方式（与 --file-list 配合）")
    parser.add_argument("--file-search", "-fs", nargs=2, metavar=('PATH', 'PATTERN'),
                        help="搜索文件 (路径 搜索模式)")
    parser.add_argument("-r", "--recursive", action="store_true",
                        help="递归搜索（与 --file-search 配合）")
    parser.add_argument("--file-info", "-fi", metavar="PATH",
                        help="获取文件/目录详细信息")
    parser.add_argument("--file-copy", "-fcp", nargs=2, metavar=('SOURCE', 'DEST'),
                        help="复制文件或目录")
    parser.add_argument("--file-move", "-fmv", nargs=2, metavar=('SOURCE', 'DEST'),
                        help="移动/重命名文件或目录")
    parser.add_argument("--file-delete", "-fdel", metavar="PATH",
                        help="删除文件或目录")
    parser.add_argument("--file-create", "-fcr", metavar="PATH",
                        help="新建文件")
    parser.add_argument("--file-mkdir", "-fdir", metavar="PATH",
                        help="新建目录")
    parser.add_argument("--file-disk", "-fdisk", nargs="?", const=".", metavar="PATH",
                        help="查看磁盘使用情况")
    parser.add_argument("--file-quick", "-fquick", action="store_true",
                        help="获取快速访问位置")

    # 系统设置支持
    parser.add_argument("--settings-brightness", "-sb", nargs="?", const="get",
                        help="亮度控制: get, set <0-100>, up, down")
    parser.add_argument("--settings-volume", "-sv", nargs="?", const="get",
                        help="音量控制: get, set <0-100>, up, down, mute")
    parser.add_argument("--settings-battery", "-sbat", action="store_true",
                        help="获取电池状态")
    parser.add_argument("--settings-power", "-sp", nargs="?", const="get", metavar="ACTION",
                        help="电源管理: get, set <balanced|power_saver|high_performance>")
    parser.add_argument("--settings-power-plan", "-spp", type=str,
                        help="设置电源计划（平衡/节能/高性能）")
    parser.add_argument("--settings-dark-mode", "-sd", nargs="?", const="get",
                        help="深色模式: status, on, off, toggle")
    parser.add_argument("--settings-airplane", "-sa", nargs="?", const="get",
                        help="飞行模式: status, on, off")
    parser.add_argument("--settings-scale", "-ss", action="store_true",
                        help="获取显示缩放比例")
    parser.add_argument("--settings-wallpaper", "-sw", nargs="+", metavar="ACTION",
                        help="壁纸: get, set <path>")
    parser.add_argument("--settings-all", "-sall", action="store_true",
                        help="获取所有设置概览")

    args = parser.parse_args()

    # 如果没有参数，显示菜单
    if len(sys.argv) == 1:
        print(show_menu())
        return

    # 执行相应的操作
    if args.list_windows:
        print("=== 打开的窗口 ===")
        print(list_windows())

    if args.activate:
        print(f"激活窗口: {args.activate}")
        if activate_window(args.activate):
            print("✓ 窗口已激活")
        else:
            print("✗ 激活失败")

    if args.maximize:
        print(f"最大化窗口: {args.maximize}")
        if maximize_window(args.maximize):
            print("✓ 窗口已最大化")
        else:
            print("✗ 最大化失败")

    if args.minimize:
        print(f"最小化窗口: {args.minimize}")
        if minimize_window(args.minimize):
            print("✓ 窗口已最小化")
        else:
            print("✗ 最小化失败")

    if args.close_window:
        print(f"关闭窗口: {args.close_window}")
        if close_window(args.close_window):
            print("✓ 窗口已关闭")
        else:
            print("✗ 关闭失败")

    # 窗口排列操作
    if args.tile:
        output, code = arrange_windows("tile")
        print(output if output else "✓ 平铺排列完成")

    if args.cascade:
        output, code = arrange_windows("cascade")
        print(output if output else "✓ 堆叠排列完成")

    if args.center:
        output, code = arrange_windows("center")
        print(output if output else "✓ 居中排列完成")

    if args.left:
        output, code = arrange_windows("left")
        print(output if output else "✓ 左半屏排列完成")

    if args.right:
        output, code = arrange_windows("right")
        print(output if output else "✓ 右半屏排列完成")

    if args.maximize_all:
        output, code = arrange_windows("maximize")
        print(output if output else "✓ 全部最大化完成")

    if args.minimize_all:
        output, code = arrange_windows("minimize")
        print(output if output else "✓ 全部最小化完成")

    if args.list_processes:
        print("=== 运行中的进程 ===")
        print(list_processes())

    if args.kill:
        process_tool = os.path.join(SCRIPT_DIR, "process_tool.py")
        result = subprocess.run(
            [sys.executable, process_tool, "kill", args.kill],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✓ 进程已结束: {args.kill}")
        else:
            print(f"✗ 结束进程失败: {result.stderr}")

    if args.list_apps:
        print("=== 已安装应用 ===")
        print(list_installed_apps())

    if args.launch:
        print(f"启动应用: {args.launch}")
        if launch_app(args.launch):
            print("✓ 应用已启动")
        else:
            print("✗ 启动失败")

    if args.sysinfo:
        print("=== 系统信息 ===")
        info = get_system_info()
        print(json.dumps(info, indent=2, ensure_ascii=False))

    if args.explore:
        launch_explorer = os.path.join(SCRIPT_DIR, "launch_explorer.py")
        subprocess.run([sys.executable, launch_explorer, args.explore])
        print(f"✓ 文件管理器已打开: {args.explore}")

    # 虚拟应用启动器
    if args.list_shortcuts:
        output, code = launch_app_launcher("list")
        print(output if output else "✓ 快捷方式列表已显示")

    if args.launcher_status:
        output, code = launch_app_launcher("status")
        print(output if output else "✓ 启动器状态已显示")

    if args.quick_launch:
        # 尝试识别类型并启动
        target = args.quick_launch
        config_path = os.path.join(os.path.expanduser("~"), ".friday", "llm_os", "app_launcher_config.json")

        # 尝试作为应用启动
        output, code = launch_app_launcher("launch-app", target)
        if code == 0:
            print(f"✓ 应用 {target} 已启动")
        else:
            # 尝试作为网站启动
            output, code = launch_app_launcher("launch-website", target)
            if code == 0:
                print(f"✓ 网站 {target} 已打开")
            else:
                # 尝试作为系统功能启动
                output, code = launch_app_launcher("launch-system", target)
                if code == 0:
                    print(f"✓ 系统功能 {target} 已启动")
                else:
                    print(f"✗ 未找到: {target}")

    # 多显示器操作
    if args.list_displays:
        print(multidisplay_list())

    if args.move_window:
        window_title = args.move_window[0]
        display_index = int(args.move_window[1])
        output, code = multidisplay_move_window(window_title, display_index)
        print(output if output else f"✓ 窗口已移动到显示器 {display_index}")

    if args.mirror_window:
        window_title = args.mirror_window[0]
        display_index = int(args.mirror_window[1])
        output, code = multidisplay_mirror_window(window_title, display_index)
        print(output if output else f"✓ 窗口已镜像到显示器 {display_index}")

    if args.window_display:
        output, code = multidisplay_window_display(args.window_display)
        print(output if output else "未找到窗口")

    # 任务管理器操作
    if args.task_list:
        print(task_manager_list())

    if args.task_top:
        print(task_manager_list(args.task_top))

    if args.task_resources:
        print(task_manager_resources())

    if args.task_kill:
        output, code = task_manager_kill(args.task_kill)
        print(output if output else f"✓ 进程 {args.task_kill} 已结束")

    if args.task_services:
        print(task_manager_services())

    # ========== 文件管理器操作 ==========
    if args.file_list:
        print("=== 目录内容 ===")
        print(file_manager_list(args.file_list, args.file_hidden, args.file_sort))

    if args.file_search:
        path, pattern = args.file_search
        print(f"=== 搜索: {pattern} ===")
        print(file_manager_search(path, pattern, args.recursive))

    if args.file_info:
        print("=== 文件信息 ===")
        print(file_manager_info(args.file_info))

    if args.file_copy:
        source, dest = args.file_copy
        output, code = file_manager_copy(source, dest)
        print(output if output else f"✓ 已复制: {source} -> {dest}")

    if args.file_move:
        source, dest = args.file_move
        output, code = file_manager_move(source, dest)
        print(output if output else f"✓ 已移动: {source} -> {dest}")

    if args.file_delete:
        output, code = file_manager_delete(args.file_delete)
        print(output if output else f"✓ 已删除: {args.file_delete}")

    if args.file_create:
        output, code = file_manager_create(args.file_create)
        print(output if output else f"✓ 已创建文件: {args.file_create}")

    if args.file_mkdir:
        output, code = file_manager_create(args.file_mkdir, is_directory=True)
        print(output if output else f"✓ 已创建目录: {args.file_mkdir}")

    if args.file_disk:
        print("=== 磁盘使用情况 ===")
        print(file_manager_disk(args.file_disk))

    if args.file_quick:
        print("=== 快速访问位置 ===")
        print(file_manager_quick())

    # ========== 系统设置操作 ==========
    if args.settings_brightness:
        if args.settings_brightness == "get":
            print(settings_brightness("get"))
        elif args.settings_brightness == "up":
            print(settings_brightness("up"))
        elif args.settings_brightness == "down":
            print(settings_brightness("down"))
        elif args.settings_brightness.isdigit():
            print(settings_brightness("set", int(args.settings_brightness)))

    if args.settings_volume:
        if args.settings_volume == "get":
            print(settings_volume("get"))
        elif args.settings_volume == "up":
            print(settings_volume("up"))
        elif args.settings_volume == "down":
            print(settings_volume("down"))
        elif args.settings_volume == "mute":
            print(settings_volume("mute"))
        elif args.settings_volume.isdigit():
            print(settings_volume("set", int(args.settings_volume)))

    if args.settings_battery:
        print("=== 电池状态 ===")
        print(settings_battery())

    if args.settings_power == "get":
        print("=== 电源计划 ===")
        print(settings_power("get"))

    if args.settings_power_plan:
        print(settings_power("set", args.settings_power_plan))

    if args.settings_dark_mode:
        print(settings_dark_mode(args.settings_dark_mode))

    if args.settings_airplane:
        print(settings_airplane_mode(args.settings_airplane))

    if args.settings_scale:
        print("=== 显示缩放 ===")
        print(settings_scale())

    if args.settings_wallpaper:
        action = args.settings_wallpaper[0]
        path = args.settings_wallpaper[1] if len(args.settings_wallpaper) > 1 else None
        if action == "get":
            print(settings_wallpaper("get"))
        elif action == "set" and path:
            print(settings_wallpaper("set", path))

    if args.settings_all:
        print("=== 系统设置概览 ===")
        print(settings_all())


if __name__ == "__main__":
    main()