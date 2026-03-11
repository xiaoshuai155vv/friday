#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""打开系统日历/日程（Windows：闹钟与时钟内日历或 Outlook）。用法: python launch_calendar.py"""
import sys
import subprocess
import os

def main():
    if sys.platform != "win32":
        print("Windows only", file=sys.stderr)
        sys.exit(1)
    # 优先打开「闹钟和时钟」（含日历）；备选 outlook:calendar
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
