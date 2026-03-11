#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用默认浏览器打开 URL，并自动激活、最大化窗口。用法: python launch_browser.py [url]，默认 https://www.bing.com"""
import sys
import time
import subprocess
import webbrowser
from pathlib import Path

url = sys.argv[1] if len(sys.argv) >= 2 else "https://www.bing.com"
webbrowser.open(url)
print("OK", url)

# 等待浏览器窗口出现后，激活并最大化（按常见默认浏览器顺序尝试）
if sys.platform == "win32":
    time.sleep(2.0)
    script_dir = Path(__file__).resolve().parent
    wt = script_dir / "window_tool.py"
    for proc in ("msedge", "chrome", "iexplore", "firefox"):
        r = subprocess.run([sys.executable, str(wt), "maximize_process", proc], capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            print("maximized:", proc)
            break
