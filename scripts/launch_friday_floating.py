#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""无控制台启动悬浮窗：默认启动 Qt 版悬浮球（friday_floating_qt.py），无 PyQt5 时再走 main 回退 WebView。"""
import sys
import os
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if sys.platform == "win32":
    os.environ.setdefault("WEBVIEW2_DEFAULT_BACKGROUND_COLOR", "0")
flags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)

# 优先直接启动 Qt 版悬浮球（当前版本默认）；失败再走统一入口 main（会尝试 Qt 再回退 WebView）
try:
    import friday_floating_qt  # noqa: F401
    subprocess.Popen(
        [sys.executable, os.path.join(ROOT, "scripts", "friday_floating_qt.py")],
        cwd=ROOT,
        creationflags=flags,
    )
except ImportError:
    subprocess.Popen(
        [sys.executable, os.path.join(ROOT, "scripts", "friday_floating_main.py")],
        cwd=ROOT,
        creationflags=flags,
    )
