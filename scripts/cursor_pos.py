#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持续输出当前鼠标坐标，便于把鼠标移到目标位置（如 ihaier 圆形「我的」）后查看该处坐标。
用法: python cursor_pos.py [刷新间隔秒数，默认 0.2]
      按 Ctrl+C 结束。将鼠标移到目标位置，看终端输出的 x y 即可。
"""
import sys
import time
if sys.platform != "win32":
    sys.exit(1)
import ctypes
from ctypes import wintypes

u = ctypes.windll.user32
class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

def main():
    interval = 0.2
    if len(sys.argv) >= 2:
        try:
            interval = float(sys.argv[1])
        except ValueError:
            pass
    print("Move mouse to target (e.g. 我的 circle). Press Ctrl+C to stop.", file=sys.stderr)
    print("x\ty", file=sys.stderr)
    try:
        while True:
            p = POINT()
            u.GetCursorPos(ctypes.byref(p))
            print(f"{p.x}\t{p.y}", flush=True)
            time.sleep(interval)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
