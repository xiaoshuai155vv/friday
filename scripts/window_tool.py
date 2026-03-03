#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
窗口前后台（Windows ctypes）。activate <标题或部分标题>：将匹配的窗口提到前台。
用法: python window_tool.py activate "记事本" 或 activate "Notepad"
"""
import sys
if sys.platform != "win32":
    sys.exit(1)
import ctypes
from ctypes import wintypes

u = ctypes.windll.user32
WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

# 找到的窗口句柄与搜索串（回调用）
_found_hwnd = None
_search_title = ""

def _enum_callback(hwnd, lparam):
    global _found_hwnd
    length = u.GetWindowTextLengthW(hwnd) + 1
    if length <= 1:
        return True
    buf = ctypes.create_unicode_buffer(length)
    u.GetWindowTextW(hwnd, buf, length)
    title = buf.value or ""
    if _search_title and _search_title in title.lower():
        _found_hwnd = hwnd
        return False  # 停止枚举
    return True

def activate_by_title(partial_title):
    """将标题包含 partial_title 的窗口激活到前台。返回是否成功。"""
    global _found_hwnd, _search_title
    _found_hwnd = None
    _search_title = (partial_title or "").strip().lower()
    if not _search_title:
        return False
    u.EnumWindows.argtypes = [WNDENUMPROC, wintypes.LPARAM]
    u.EnumWindows(WNDENUMPROC(_enum_callback), 0)
    if _found_hwnd is None:
        return False
    # 若窗口最小化则先还原
    if u.IsIconic(_found_hwnd):
        u.ShowWindow(_found_hwnd, 9)  # SW_RESTORE
    return u.SetForegroundWindow(_found_hwnd) != 0

def main():
    if len(sys.argv) < 3 or sys.argv[1].lower() != "activate":
        print('usage: window_tool.py activate "标题或部分标题"', file=sys.stderr)
        sys.exit(1)
    title = sys.argv[2]
    if activate_by_title(title):
        print("OK")
    else:
        print("No matching window or SetForegroundWindow failed", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
