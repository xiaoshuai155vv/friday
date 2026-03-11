#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""输出当前系统时间（ISO）。用法: time_tool.py [--local]"""
import sys
from datetime import datetime, timezone

def main():
    local = "--local" in sys.argv or "-l" in sys.argv
    if local:
        t = datetime.now()
    else:
        t = datetime.now(timezone.utc)
    print(t.isoformat())
    return 0

if __name__ == "__main__":
    sys.exit(main())
