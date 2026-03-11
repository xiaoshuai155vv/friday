#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""打开文件资源管理器。用法: python launch_explorer.py [目录路径]"""
import sys
import subprocess
import os
path = os.path.abspath(sys.argv[1]) if len(sys.argv) >= 2 else os.path.expanduser("~")
subprocess.Popen(["explorer.exe", path])
print("OK")
