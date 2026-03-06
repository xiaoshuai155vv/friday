#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一入口：优先使用项目内便携 Python（python/python.exe），若无则使用当前解释器。
用法: python run_with_env.py <脚本名不含.py> [参数...]
例如: python run_with_env.py do 截图
      python run_with_env.py run_with_env do 截图  （也可写全脚本名）
脚本名可带或不带 .py；会在 scripts/ 下查找。
"""
import sys
import os
import subprocess

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPTS)
LOCAL_PYTHON = os.path.join(PROJECT, "python", "python.exe")

def main():
    if len(sys.argv) < 2:
        print("usage: python run_with_env.py <脚本名> [参数...]", file=sys.stderr)
        sys.exit(1)
    script_name = sys.argv[1].strip()
    args = sys.argv[2:]
    if not script_name.endswith(".py"):
        script_name += ".py"
    script_path = os.path.join(SCRIPTS, script_name)
    if not os.path.isfile(script_path):
        print("script not found:", script_path, file=sys.stderr)
        sys.exit(1)
    if os.path.isfile(LOCAL_PYTHON):
        interp = LOCAL_PYTHON
    else:
        interp = sys.executable
    cmd = [interp, script_path] + args
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "FRIDAY_INVOKER_PYTHON": sys.executable}
    sys.exit(subprocess.run(cmd, cwd=PROJECT, env=env).returncode)

if __name__ == "__main__":
    main()
