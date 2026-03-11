#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取当前前台窗口信息。
返回当前活动窗口的标题和进程名。
用法: get_foreground_window.py
"""

import sys
import subprocess
import re
if sys.platform != "win32":
    print("错误：此脚本仅支持 Windows 系统")
    sys.exit(1)

import ctypes
from ctypes import wintypes

u = ctypes.windll.user32

def get_foreground_window_info():
    """获取前台窗口信息：标题和进程名"""
    # 获取前台窗口句柄
    hwnd = u.GetForegroundWindow()
    if hwnd == 0:
        return None, None

    # 获取窗口标题
    length = u.GetWindowTextLengthW(hwnd) + 1
    if length <= 1:
        title = ""
    else:
        buf = ctypes.create_unicode_buffer(length)
        u.GetWindowTextW(hwnd, buf, length)
        title = buf.value or ""

    # 获取进程 PID
    pid = wintypes.DWORD()
    u.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    process_id = pid.value

    # 获取进程名
    try:
        # 使用 tasklist 获取进程名
        r = subprocess.run(
            ["tasklist", "/FO", "CSV", "/NH", "/FI", f"PID eq {process_id}"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15
        )
        out = (r.stdout or "").strip()
        if out:
            # CSV格式：进程名, PID, ...
            parts = re.findall(r'"([^"]*)"', out)
            if len(parts) >= 1:
                process_name = parts[0]
            else:
                process_name = ""
        else:
            process_name = ""
    except Exception:
        process_name = ""

    return title, process_name

def main():
    title, process_name = get_foreground_window_info()
    if title is None:
        print("无法获取前台窗口信息")
        sys.exit(1)

    # 输出 JSON 格式的结果
    import json
    result = {
        "title": title,
        "process_name": process_name
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()