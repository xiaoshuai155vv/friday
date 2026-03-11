#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""打开系统「闹钟和时钟」应用（Windows）。用法: python launch_clock.py"""
import sys
import subprocess
import os

def main():
    if sys.platform != "win32":
        print("Windows only", file=sys.stderr)
        sys.exit(1)
    try:
        subprocess.Popen("start ms-clock:", shell=True)
    except Exception:
        try:
            os.startfile("ms-clock:")
        except Exception:
            subprocess.run(
                ["cmd", "/c", "start", "ms-clock:"],
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
            )
    print("OK")

if __name__ == "__main__":
    main()
