#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""打开 Windows 计算器。用法: python launch_calc.py"""
import sys
import subprocess
import os

def main():
    if sys.platform != "win32":
        print("Windows only", file=sys.stderr)
        sys.exit(1)
    try:
        subprocess.Popen(["calc.exe"])
    except Exception:
        subprocess.run(["cmd", "/c", "start", "calc"], creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0)
    print("OK")

if __name__ == "__main__":
    main()
