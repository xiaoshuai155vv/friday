#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时工具：等待 N 秒后执行可选操作。用法：timer_tool.py <秒数> [run <脚本名>] 或 无第二参数则仅等待后退出。
例如：timer_tool.py 5  → 等 5 秒；timer_tool.py 10 run launch_notepad  → 10 秒后执行 scripts/launch_notepad.py。
"""
import sys
import os
import time
import subprocess

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPTS)

def main():
    if len(sys.argv) < 2:
        print("usage: timer_tool.py <seconds> [run <script_name>]", file=sys.stderr)
        sys.exit(1)
    try:
        sec = float(sys.argv[1])
    except ValueError:
        print("seconds must be a number", file=sys.stderr)
        sys.exit(1)
    if sec < 0:
        sec = 0
    time.sleep(sec)
    if len(sys.argv) >= 4 and sys.argv[2].lower() == "run":
        script = sys.argv[3]
        if not script.endswith(".py"):
            script += ".py"
        path = os.path.join(SCRIPTS, script)
        if os.path.isfile(path):
            subprocess.Popen(
                [sys.executable, path],
                cwd=PROJECT,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
    return 0

if __name__ == "__main__":
    sys.exit(main())
