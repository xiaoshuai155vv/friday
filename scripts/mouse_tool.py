#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自包含鼠标工具（Windows ctypes）。
用法: click <x> <y> | right_click <x> <y> | middle_click <x> <y> | scroll <delta> | drag <x1> <y1> <x2> <y2> | pos
"""
import sys
if sys.platform != "win32":
    sys.exit(1)
import ctypes
from ctypes import wintypes
u = ctypes.windll.user32
MOUSEEVENTF_LEFTDOWN   = 0x0002
MOUSEEVENTF_LEFTUP     = 0x0004
MOUSEEVENTF_RIGHTDOWN  = 0x0008
MOUSEEVENTF_RIGHTUP    = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP   = 0x0040
MOUSEEVENTF_WHEEL      = 0x0800

class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

def _click_at(x, y, down_flag, up_flag):
    u.SetCursorPos(x, y)
    u.mouse_event(down_flag, 0, 0, 0, 0)
    u.mouse_event(up_flag, 0, 0, 0, 0)

def main():
    if len(sys.argv) < 2:
        print("usage: click <x> <y> | right_click <x> <y> | middle_click <x> <y> | scroll <delta> | pos", file=sys.stderr)
        sys.exit(1)
    cmd = sys.argv[1].lower()
    if cmd == "pos":
        p = POINT()
        u.GetCursorPos(ctypes.byref(p))
        print(p.x, p.y)
    elif cmd == "click" and len(sys.argv) >= 4:
        x, y = int(sys.argv[2]), int(sys.argv[3])
        _click_at(x, y, MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP)
    elif cmd == "right_click" and len(sys.argv) >= 4:
        x, y = int(sys.argv[2]), int(sys.argv[3])
        _click_at(x, y, MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP)
    elif cmd == "middle_click" and len(sys.argv) >= 4:
        x, y = int(sys.argv[2]), int(sys.argv[3])
        _click_at(x, y, MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP)
    elif cmd == "scroll" and len(sys.argv) >= 3:
        delta = int(sys.argv[2])
        u.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, delta, 0)
    elif cmd == "drag" and len(sys.argv) >= 6:
        x1, y1, x2, y2 = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
        u.SetCursorPos(x1, y1)
        u.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        u.SetCursorPos(x2, y2)
        u.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    else:
        print("usage: click <x> <y> | right_click <x> <y> | middle_click <x> <y> | scroll <delta> | drag <x1> <y1> <x2> <y2> | pos", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
