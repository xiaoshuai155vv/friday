#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证点击坐标是否正确：移动鼠标到 (x,y)、等待数秒，可选截图，便于核对多模态返回的坐标是否点到预期位置。
与 screenshot_tool、mouse_tool 使用同一套屏幕逻辑分辨率（GetSystemMetrics）。
用法: python click_verify.py <x> <y> [等待秒数] [--screenshot 截图路径]
示例: python click_verify.py 200 200 3
      python click_verify.py 260 240 5 --screenshot screenshots/verify.bmp
"""
import sys
import os
import time
if sys.platform != "win32":
    sys.exit(1)
import ctypes
from ctypes import wintypes

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPTS)

def main():
    u = ctypes.windll.user32
    screen_w = u.GetSystemMetrics(0)
    screen_h = u.GetSystemMetrics(1)
    if len(sys.argv) < 3:
        print(f"Screen size: {screen_w} x {screen_h}", file=sys.stderr)
        print("usage: click_verify.py <x> <y> [sec] [--screenshot path]", file=sys.stderr)
        sys.exit(1)
    x = int(sys.argv[1])
    y = int(sys.argv[2])
    sec = 3
    screenshot_path = None
    i = 3
    while i < len(sys.argv):
        if sys.argv[i] == "--screenshot" and i + 1 < len(sys.argv):
            screenshot_path = sys.argv[i + 1]
            i += 2
            continue
        if sys.argv[i].lstrip("-").isdigit():
            sec = int(sys.argv[i])
        i += 1
    print(f"Screen: {screen_w} x {screen_h}  ->  moving to ({x}, {y}), waiting {sec}s ...", file=sys.stderr)
    u.SetCursorPos(x, y)
    time.sleep(sec)
    if screenshot_path:
        os.makedirs(os.path.dirname(os.path.abspath(screenshot_path)) or ".", exist_ok=True)
        r = __import__("subprocess").run(
            [sys.executable, os.path.join(SCRIPTS, "screenshot_tool.py"), screenshot_path],
            cwd=PROJECT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if r.returncode == 0:
            print(f"Screenshot saved: {screenshot_path}", file=sys.stderr)
        else:
            print(r.stderr or "screenshot failed", file=sys.stderr)
    print(f"{x} {y}")

if __name__ == "__main__":
    main()
