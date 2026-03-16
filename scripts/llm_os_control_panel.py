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


def show_menu():
    """显示 LLM-OS 控制面板菜单"""
    menu = """
╔═══════════════════════════════════════════════════════════╗
║           LLM-OS 桌面操作系统控制面板 v1.0.0              ║
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
║  5. 系统信息                                             ║
║     - sysinfo: 获取系统信息                              ║
║                                                         ║
║  6. 文件管理                                             ║
║     - explore: 打开文件管理器                            ║
║                                                         ║
║  7. 退出                                                 ║
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


if __name__ == "__main__":
    main()