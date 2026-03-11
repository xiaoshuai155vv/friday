#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""打开记事本。用法: python launch_notepad.py [文件路径]"""
import sys
import subprocess
import os
path = sys.argv[1] if len(sys.argv) >= 2 else None
if path and os.path.isabs(path):
    subprocess.Popen(["notepad.exe", path])
else:
    subprocess.Popen(["notepad.exe"])
print("OK")
