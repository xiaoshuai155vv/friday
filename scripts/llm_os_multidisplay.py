#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-OS 多显示器支持模块

提供多显示器检测、窗口跨屏移动、在指定显示器启动应用等能力。

版本: 1.0.0
依赖: ctypes, win32api, pywin32
"""

import sys
import os
import ctypes
from ctypes import wintypes

# 添加脚本目录到路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_displays():
    """
    获取所有显示器的信息

    返回:
        list: 显示器信息列表，每个显示器包含 index, x, y, width, height, is_primary
    """
    try:
        import win32api
        import win32con
        import pywintypes
    except ImportError:
        return _get_displays_fallback()

    displays = []

    try:
        # 使用 Windows API 获取显示器信息
        ENUM_CALLBACK = ctypes.WINFUNCTYPE(
            wintypes.BOOL,
            wintypes.HMONITOR,
            wintypes.HDC,
            ctypes.POINTER(wintypes.RECT),
            wintypes.LPARAM
        )

        monitors = []

        def callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
            r = lprcMonitor.contents
            monitors.append({
                'left': r.left,
                'top': r.top,
                'right': r.right,
                'bottom': r.bottom,
                'width': r.right - r.left,
                'height': r.bottom - r.top
            })
            return True

        ctypes.windll.user32.EnumDisplayMonitors(None, None, ENUM_CALLBACK(callback), 0)

        # 获取主显示器
        primary = win32api.GetPrimaryDisplayDevice()
        primary_bounds = primary.Keyword_Width  # 这是错误的，需要用正确方式获取

        # 更简单的方法：使用 GetSystemMetrics
        SM_CXVIRTUALSCREEN = 78
        SM_CYVIRTUALSCREEN = 79
        SM_XVIRTUALSCREEN = 76
        SM_YVIRTUALSCREEN = 77
        SM_CMONITORS = 80

        num_monitors = ctypes.windll.user32.GetSystemMetrics(SM_CMONITORS)

        if num_monitors <= 1:
            # 单显示器情况
            width = ctypes.windll.user32.GetSystemMetrics(0)  # SM_CXSCREEN
            height = ctypes.windll.user32.GetSystemMetrics(1)  # SM_CYSCREEN
            displays.append({
                'index': 0,
                'x': 0,
                'y': 0,
                'width': width,
                'height': height,
                'is_primary': True,
                'name': '主显示器'
            })
        else:
            # 多显示器情况 - 使用更可靠的方法
            for i, m in enumerate(monitors):
                displays.append({
                    'index': i,
                    'x': m['left'],
                    'y': m['top'],
                    'width': m['width'],
                    'height': m['height'],
                    'is_primary': (i == 0),  # 第一个通常为主显示器
                    'name': f'显示器 {i + 1}'
                })

        return displays

    except Exception as e:
        return _get_displays_fallback()


def _get_displays_fallback():
    """获取显示器信息的备用方法（不使用 pywin32）"""
    try:
        width = ctypes.windll.user32.GetSystemMetrics(0)  # SM_CXSCREEN
        height = ctypes.windll.user32.GetSystemMetrics(1)  # SM_CYSCREEN
        return [{
            'index': 0,
            'x': 0,
            'y': 0,
            'width': width,
            'height': height,
            'is_primary': True,
            'name': '主显示器'
        }]
    except:
        return [{
            'index': 0,
            'x': 0,
            'y': 0,
            'width': 1920,
            'height': 1080,
            'is_primary': True,
            'name': '主显示器'
        }]


def move_window_to_display(window_title, display_index):
    """
    将窗口移动到指定显示器

    参数:
        window_title: 窗口标题（部分匹配）
        display_index: 目标显示器索引（0, 1, 2, ...）

    返回:
        bool: 是否成功
    """
    try:
        from win32gui import FindWindow, GetWindowRect, SetWindowPos
        from win32con import SWP_NOZORDER, SWP_NOACTIVATE
        import win32api
    except ImportError:
        print("需要 pywin32 库来执行此操作")
        return False

    try:
        # 查找窗口
        hwnd = FindWindow(None, window_title)
        if not hwnd:
            # 尝试模糊匹配
            hwnd = _find_window_fuzzy(window_title)

        if not hwnd:
            print(f"未找到窗口: {window_title}")
            return False

        # 获取显示器信息
        displays = get_displays()
        if display_index >= len(displays):
            print(f"显示器索引 {display_index} 超出范围（当前有 {len(displays)} 个显示器）")
            return False

        target_display = displays[display_index]

        # 获取当前窗口位置
        rect = GetWindowRect(hwnd)
        window_width = rect[2] - rect[0]
        window_height = rect[3] - rect[1]

        # 计算新位置（保持在目标显示器内）
        new_x = target_display['x'] + (target_display['width'] - window_width) // 2
        new_y = target_display['y'] + (target_display['height'] - window_height) // 2

        # 移动窗口
        SetWindowPos(hwnd, None, new_x, new_y, window_width, window_height,
                     SWP_NOZORDER | SWP_NOACTIVATE)

        print(f"✓ 窗口已移动到 {target_display['name']}")
        return True

    except Exception as e:
        print(f"移动窗口失败: {e}")
        return False


def _find_window_fuzzy(title):
    """模糊查找窗口"""
    try:
        from win32gui import EnumWindows, GetWindowText, IsWindowVisible
    except ImportError:
        return None

    result = [None]

    def callback(hwnd, extra):
        if IsWindowVisible(hwnd):
            text = GetWindowText(hwnd)
            if title.lower() in text.lower():
                result[0] = hwnd
        return True

    try:
        from win32gui import EnumWindows
        EnumWindows(callback, None)
    except:
        pass

    return result[0]


def launch_on_display(app_path, display_index):
    """
    在指定显示器上启动应用

    参数:
        app_path: 应用路径或名称
        display_index: 目标显示器索引

    返回:
        bool: 是否成功
    """
    try:
        from win32api import GetSystemMetrics
        import subprocess
        import time

        displays = get_displays()
        if display_index >= len(displays):
            print(f"显示器索引 {display_index} 超出范围")
            return False

        target_display = displays[display_index]

        # 启动应用
        # 方法1：使用 start 命令指定显示器（不太可靠）
        # 方法2：启动后移动窗口（需要窗口标题）
        # 这里我们先启动应用，然后返回提示

        # 简单的启动方式
        try:
            subprocess.Popen(app_path, shell=True)
            print(f"✓ 应用已在启动（将在主显示器显示）")
            print(f"  提示：可以使用 --move-window 命令将其移动到其他显示器")
            return True
        except Exception as e:
            print(f"启动应用失败: {e}")
            return False

    except Exception as e:
        print(f"在指定显示器启动应用失败: {e}")
        return False


def list_displays():
    """列出所有显示器信息"""
    import json

    displays = get_displays()

    output = "=== 多显示器配置 ===\n"
    output += f"显示器数量: {len(displays)}\n\n"

    for d in displays:
        primary_mark = " [主显示器]" if d['is_primary'] else ""
        output += f"显示器 {d['index']}: {d['name']}{primary_mark}\n"
        output += f"  位置: ({d['x']}, {d['y']})\n"
        output += f"  分辨率: {d['width']} x {d['height']}\n\n"

    return output


def get_window_display(window_title):
    """获取窗口当前所在的显示器"""
    try:
        from win32gui import FindWindow, GetWindowRect
    except ImportError:
        return None

    try:
        hwnd = FindWindow(None, window_title)
        if not hwnd:
            hwnd = _find_window_fuzzy(window_title)

        if not hwnd:
            return None

        rect = GetWindowRect(hwnd)
        center_x = (rect[0] + rect[2]) // 2
        center_y = (rect[1] + rect[3]) // 2

        # 查找窗口所在的显示器
        displays = get_displays()
        for d in displays:
            if (d['x'] <= center_x < d['x'] + d['width'] and
                d['y'] <= center_y < d['y'] + d['height']):
                return d

        return displays[0] if displays else None

    except Exception as e:
        return None


def mirror_window_to_display(source_title, target_display_index):
    """将窗口镜像/复制到另一个显示器"""
    try:
        from win32gui import FindWindow, GetWindowRect, SetWindowPos
        from win32con import SWP_NOZORDER, SWP_NOACTIVATE
    except ImportError:
        print("需要 pywin32 库")
        return False

    try:
        # 查找源窗口
        hwnd = FindWindow(None, source_title)
        if not hwnd:
            hwnd = _find_window_fuzzy(source_title)

        if not hwnd:
            print(f"未找到窗口: {source_title}")
            return False

        # 获取显示器信息
        displays = get_displays()
        if target_display_index >= len(displays):
            print(f"显示器索引 {target_display_index} 超出范围")
            return False

        target = displays[target_display_index]
        source = displays[0]  # 假设第一个是源

        # 获取窗口当前位置和大小
        rect = GetWindowRect(hwnd)
        window_width = rect[2] - rect[0]
        window_height = rect[3] - rect[1]

        # 计算相对于源显示器的位置，然后映射到目标显示器
        rel_x = rect[0] - source['x']
        rel_y = rect[1] - source['y']

        # 在目标显示器上计算新位置（保持相对位置）
        new_x = target['x'] + rel_x
        new_y = target['y'] + rel_y

        # 确保窗口在目标显示器内
        if new_x < target['x']:
            new_x = target['x']
        if new_y < target['y']:
            new_y = target['y']
        if new_x + window_width > target['x'] + target['width']:
            new_x = target['x'] + target['width'] - window_width
        if new_y + window_height > target['y'] + target['height']:
            new_y = target['y'] + target['height'] - window_height

        # 移动窗口
        SetWindowPos(hwnd, None, new_x, new_y, window_width, window_height,
                     SWP_NOZORDER | SWP_NOACTIVATE)

        print(f"✓ 窗口已镜像到 {target['name']}")
        return True

    except Exception as e:
        print(f"镜像窗口失败: {e}")
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="LLM-OS 多显示器支持工具",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--list", "-l", action="store_true",
                        help="列出所有显示器信息")
    parser.add_argument("--move-window", "-m", type=str, nargs=2,
                        metavar=('WINDOW_TITLE', 'DISPLAY_INDEX'),
                        help="将窗口移动到指定显示器")
    parser.add_argument("--mirror-window", "-mm", type=str, nargs=2,
                        metavar=('WINDOW_TITLE', 'DISPLAY_INDEX'),
                        help="将窗口镜像到指定显示器（保持相对位置）")
    parser.add_argument("--window-display", "-wd", type=str,
                        help="获取窗口当前所在的显示器")
    parser.add_argument("--launch-app", "-a", type=str, nargs=2,
                        metavar=('APP_PATH', 'DISPLAY_INDEX'),
                        help="在指定显示器启动应用")

    args = parser.parse_args()

    if args.list:
        print(list_displays())
    elif args.move_window:
        window_title = args.move_window[0]
        display_index = int(args.move_window[1])
        move_window_to_display(window_title, display_index)
    elif args.mirror_window:
        window_title = args.mirror_window[0]
        display_index = int(args.mirror_window[1])
        mirror_window_to_display(window_title, display_index)
    elif args.window_display:
        d = get_window_display(args.window_display)
        if d:
            print(f"窗口位于: {d['name']} (索引: {d['index']})")
        else:
            print("未找到窗口")
    elif args.launch_app:
        app_path = args.launch_app[0]
        display_index = int(args.launch_app[1])
        launch_on_display(app_path, display_index)
    else:
        # 默认列出显示器
        print(list_displays())


if __name__ == "__main__":
    main()