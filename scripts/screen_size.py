#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
输出当前主屏逻辑尺寸（与 screenshot_tool / 鼠标坐标一致），用于多模态坐标校验与计划编写。
用法: python screen_size.py
输出: W H （空格分隔，如 1920 1080）
"""
import sys
if sys.platform != "win32":
    sys.exit(1)
import ctypes
u = ctypes.windll.user32
w = u.GetSystemMetrics(0)
h = u.GetSystemMetrics(1)
print(w, h)
