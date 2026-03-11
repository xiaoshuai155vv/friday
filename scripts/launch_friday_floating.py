#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""启动 Qt 版悬浮球（friday_floating_qt.py）。仅 Qt 版，需 pip install PyQt5。"""
import sys
import os
import subprocess
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
flags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)

# 用户直接运行时保留控制台以便看到错误；由 serve/run_plan 等调用时用 CREATE_NO_WINDOW
_use_no_window = os.environ.get("FRIDAY_LAUNCH_NO_WINDOW", "").lower() in ("1", "true", "yes")
creationflags = flags if _use_no_window else 0

def _launch():
    p = subprocess.Popen(
        [sys.executable, os.path.join(ROOT, "scripts", "friday_floating_qt.py")],
        cwd=ROOT,
        creationflags=creationflags,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    time.sleep(0.8)
    if p.poll() is not None:
        out, err = p.communicate()
        msg = (err or out or b"").decode("utf-8", errors="replace").strip()
        if msg:
            sys.stderr.write("悬浮球启动失败:\n%s\n" % msg)
            sys.stderr.flush()
        if creationflags == 0:
            sys.stderr.write("提示: 需 pip install PyQt5；可 python scripts/friday_floating_qt.py 直接运行查看完整错误\n")
            sys.stderr.flush()
        return False
    if creationflags == 0:
        sys.stderr.write("悬浮球已启动（若未看到窗口，可能被其他窗口遮挡）\n")
        sys.stderr.flush()
    return True

try:
    import friday_floating_qt  # noqa: F401
    _launch()
except ImportError as e:
    sys.stderr.write("悬浮球启动失败: 需 pip install PyQt5\n%s\n" % e)
    sys.stderr.flush()
    sys.exit(1)
