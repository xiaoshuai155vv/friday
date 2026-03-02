#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""输出主屏宽高，空格分隔。仅 Windows，自包含（ctypes）。"""
import sys
if sys.platform != "win32":
    print("0 0", file=sys.stderr)
    sys.exit(1)
import ctypes
u = ctypes.windll.user32
w = u.GetSystemMetrics(0)   # SM_CXSCREEN
h = u.GetSystemMetrics(1)   # SM_CYSCREEN
print(f"{w} {h}")
