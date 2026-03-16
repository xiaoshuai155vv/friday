#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-OS 窗口自动排列模块

实现窗口的自动排列功能，包括平铺、堆叠、居中、左/右半屏等排列方式。
基于 Windows API 实现精确的窗口位置和大小控制。

版本: 1.0.0
依赖: ctypes, pywin32 (可选)
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path

# 添加脚本目录到路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 尝试导入 win32api，如果不可用则使用 ctypes
try:
    import win32api
    import win32con
    import win32gui
    import win32process
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False
    # 使用 ctypes 作为备用
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        HAS_CTYPES = True
    except ImportError:
        HAS_CTYPES = False


def get_window_list():
    """获取所有可见窗口列表"""
    windows = []

    def enum_callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:  # 只获取有标题的窗口
                try:
                    rect = win32gui.GetWindowRect(hwnd)
                    windows.append({
                        'hwnd': hwnd,
                        'title': title,
                        'x': rect[0],
                        'y': rect[1],
                        'width': rect[2] - rect[0],
                        'height': rect[3] - rect[1]
                    })
                except:
                    pass
        return True

    if HAS_WIN32:
        win32gui.EnumWindows(enum_callback, None)

    return windows


def get_screen_size():
    """获取屏幕尺寸"""
    if HAS_WIN32:
        width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        return width, height
    elif HAS_CTYPES:
        width = user32.GetSystemMetrics(0)  # SM_CXSCREEN
        height = user32.GetSystemMetrics(1)  # SM_CYSCREEN
        return width, height
    return 1920, 1080  # 默认值


def arrange_windows_tile(windows, screen_width, screen_height):
    """平铺排列：所有窗口均匀分布在屏幕上"""
    if not windows:
        return False

    n = len(windows)
    # 计算最佳行列数
    cols = 1
    rows = 1
    min_diff = float('inf')

    for c in range(1, n + 1):
        r = (n + c - 1) // c
        diff = abs(c - r)
        if diff < min_diff:
            min_diff = diff
            cols = c
            rows = r

    # 限制每行/列的最大数量，避免窗口过小
    max_per_row = min(4, cols)
    if cols > max_per_row:
        cols = max_per_row
        rows = (n + cols - 1) // cols

    # 计算每个窗口的尺寸
    win_width = screen_width // cols
    win_height = screen_height // rows

    for i, window in enumerate(windows):
        col = i % cols
        row = i // cols

        x = col * win_width
        y = row * win_height
        width = win_width
        height = win_height

        if HAS_WIN32:
            try:
                win32gui.SetWindowPos(
                    window['hwnd'],
                    None,
                    x, y, width, height,
                    win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE
                )
            except:
                pass

    return True


def arrange_windows_cascade(windows, screen_width, screen_height):
    """堆叠排列：窗口按层级叠放，每个略微偏移"""
    if not windows:
        return False

    # 基础尺寸（屏幕的 70%）
    base_width = int(screen_width * 0.7)
    base_height = int(screen_height * 0.7)

    # 偏移量
    offset_x = 30
    offset_y = 30

    # 从下到上堆叠（最前的窗口在最后）
    for i, window in enumerate(windows):
        # 反向索引，让第一个窗口在最前面
        idx = len(windows) - 1 - i

        x = offset_x * idx
        y = offset_y * idx
        width = base_width
        height = base_height

        if HAS_WIN32:
            try:
                # 先显示窗口，再设置位置
                win32gui.ShowWindow(window['hwnd'], win32con.SW_RESTORE)
                win32gui.SetWindowPos(
                    window['hwnd'],
                    None,
                    x, y, width, height,
                    win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE
                )
            except:
                pass

    return True


def arrange_windows_center(windows, screen_width, screen_height):
    """居中排列：所有窗口居中显示"""
    if not windows:
        return False

    # 窗口尺寸为屏幕的 60%
    width = int(screen_width * 0.6)
    height = int(screen_height * 0.6)

    # 计算居中位置
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    for window in windows:
        if HAS_WIN32:
            try:
                win32gui.SetWindowPos(
                    window['hwnd'],
                    None,
                    x, y, width, height,
                    win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE
                )
            except:
                pass

    return True


def arrange_windows_left(windows, screen_width, screen_height):
    """左半屏排列：窗口占据左半边屏幕"""
    if not windows:
        return False

    width = screen_width // 2
    height = screen_height

    for i, window in enumerate(windows):
        x = 0
        y = 0

        if HAS_WIN32:
            try:
                win32gui.SetWindowPos(
                    window['hwnd'],
                    None,
                    x, y, width, height,
                    win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE
                )
            except:
                pass

    return True


def arrange_windows_right(windows, screen_width, screen_height):
    """右半屏排列：窗口占据右半边屏幕"""
    if not windows:
        return False

    width = screen_width // 2
    height = screen_height

    for i, window in enumerate(windows):
        x = screen_width // 2
        y = 0

        if HAS_WIN32:
            try:
                win32gui.SetWindowPos(
                    window['hwnd'],
                    None,
                    x, y, width, height,
                    win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE
                )
            except:
                pass

    return True


def arrange_windows_maximize(windows):
    """最大化所有窗口"""
    if not windows:
        return False

    for window in windows:
        if HAS_WIN32:
            try:
                win32gui.ShowWindow(window['hwnd'], win32con.SW_MAXIMIZE)
            except:
                pass

    return True


def arrange_windows_minimize(windows):
    """最小化所有窗口"""
    if not windows:
        return False

    for window in windows:
        if HAS_WIN32:
            try:
                win32gui.ShowWindow(window['hwnd'], win32con.SW_MINIMIZE)
            except:
                pass

    return True


def main():
    """主函数 - 命令行入口"""
    parser = argparse.ArgumentParser(
        description='LLM-OS 窗口自动排列模块',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python llm_os_window_arrange.py list                    # 列出所有窗口
  python llm_os_window_arrange.py tile                    # 平铺排列
  python llm_os_window_arrange.py cascade                 # 堆叠排列
  python llm_os_window_arrange.py center                  # 居中排列
  python llm_os_window_arrange.py left                    # 左半屏
  python llm_os_window_arrange.py right                   # 右半屏
  python llm_os_window_arrange.py maximize                # 最大化
  python llm_os_window_arrange.py minimize                # 最小化

版本: 1.0.0
        """
    )

    parser.add_argument('action', nargs='?', default='list',
                        help='操作: list/tile/cascade/center/left/right/maximize/minimize')
    parser.add_argument('--version', action='version', version='1.0.0')
    parser.add_argument('--status', action='store_true', help='显示模块状态')

    args = parser.parse_args()

    if args.status:
        print("LLM-OS 窗口自动排列模块")
        print(f"版本: 1.0.0")
        print(f"Win32 支持: {HAS_WIN32}")
        print(f"ctypes 支持: {HAS_CTYPES if not HAS_WIN32 else 'N/A'}")
        print()
        print("可用操作:")
        print("  list      - 列出所有窗口")
        print("  tile      - 平铺排列")
        print("  cascade   - 堆叠排列")
        print("  center    - 居中排列")
        print("  left      - 左半屏排列")
        print("  right     - 右半屏排列")
        print("  maximize  - 最大化所有窗口")
        print("  minimize  - 最小化所有窗口")
        return

    # 获取窗口列表
    windows = get_window_list()
    screen_width, screen_height = get_screen_size()

    if args.action == 'list':
        print(f"屏幕尺寸: {screen_width} x {screen_height}")
        print(f"窗口数量: {len(windows)}")
        print()
        for i, w in enumerate(windows, 1):
            print(f"{i}. {w['title']}")
            print(f"   位置: ({w['x']}, {w['y']}) 尺寸: {w['width']} x {w['height']}")
        return

    # 根据动作执行排列
    action_map = {
        'tile': lambda: arrange_windows_tile(windows, screen_width, screen_height),
        'cascade': lambda: arrange_windows_cascade(windows, screen_width, screen_height),
        'center': lambda: arrange_windows_center(windows, screen_width, screen_height),
        'left': lambda: arrange_windows_left(windows, screen_width, screen_height),
        'right': lambda: arrange_windows_right(windows, screen_width, screen_height),
        'maximize': lambda: arrange_windows_maximize(windows),
        'minimize': lambda: arrange_windows_minimize(windows),
    }

    if args.action not in action_map:
        print(f"未知操作: {args.action}")
        print("可用操作: list, tile, cascade, center, left, right, maximize, minimize")
        sys.exit(1)

    success = action_map[args.action]()

    if success:
        print(f"执行成功: {args.action}")
        print(f"处理窗口数: {len(windows)}")
    else:
        print(f"执行失败: {args.action}")
        sys.exit(1)


if __name__ == '__main__':
    main()