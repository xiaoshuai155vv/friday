#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自包含鼠标工具（Windows ctypes）。
用法: click <x> <y>  |  scroll <delta>
"""
import sys
if sys.platform != "win32":
    sys.exit(1)
import ctypes
u = ctypes.windll.user32
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP   = 0x0004
MOUSEEVENTF_WHEEL    = 0x0800

def main():
    if len(sys.argv) < 2:
        print("usage: click <x> <y>  |  scroll <delta>", file=sys.stderr)
        sys.exit(1)
    cmd = sys.argv[1].lower()
    if cmd == "click" and len(sys.argv) >= 4:
        x, y = int(sys.argv[2]), int(sys.argv[3])
        u.SetCursorPos(x, y)
        u.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        u.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    elif cmd == "scroll" and len(sys.argv) >= 3:
        delta = int(sys.argv[2])
        u.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, delta, 0)
    else:
        print("usage: click <x> <y>  |  scroll <delta>", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
