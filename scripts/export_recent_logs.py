#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将近期行为日志导出为 JSON，供 UI 拉取展示。用法: python export_recent_logs.py [条数，默认50]"""
import os
import sys
import json
import glob

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "runtime", "logs")
OUT_FILE = os.path.join(os.path.dirname(__file__), "..", "runtime", "state", "recent_logs.json")

def main():
    n = int(sys.argv[1]) if len(sys.argv) >= 2 else 50
    pattern = os.path.join(LOG_DIR, "behavior_*.log")
    files = sorted(glob.glob(pattern), reverse=True)
    rows = []
    for path in files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split("\t", 5)
                    if len(parts) >= 3:
                        rows.append({
                            "time": parts[0],
                            "phase": parts[1],
                            "desc": parts[2],
                            "mission": parts[3].replace("mission=", "") if len(parts) > 3 else "",
                            "result": parts[5].replace("result=", "") if len(parts) > 5 else "",
                        })
        except Exception:
            continue
        if len(rows) >= n:
            break
    rows = rows[-n:]
    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump({"entries": rows}, f, ensure_ascii=False, indent=0)
    print(OUT_FILE)

if __name__ == "__main__":
    main()
