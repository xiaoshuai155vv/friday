#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
行为日志：写入 runtime/logs/ 目录，便于溯源。
用法:
  python behavior_log.py <action_type> "<description>" [--mission ...] [--task-id ...] [--result ...]
  action_type: assume | plan | track | verify | decide | other
"""

import argparse
import os
from datetime import datetime, timezone

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "runtime", "logs")


def _ensure_dir():
    os.makedirs(LOG_DIR, exist_ok=True)


def log(action_type: str, description: str, mission: str = "", task_id: str = "", result: str = ""):
    _ensure_dir()
    ts = datetime.now(timezone.utc).isoformat()
    day = ts[:10]
    path = os.path.join(LOG_DIR, f"behavior_{day}.log")
    line = f"{ts}\t{action_type}\t{description}\tmission={mission}\ttask_id={task_id}\tresult={result}\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("action_type", choices=["assume", "plan", "track", "verify", "decide", "other"])
    ap.add_argument("description", help="Brief description of the action")
    ap.add_argument("--mission", default="")
    ap.add_argument("--task-id", default="")
    ap.add_argument("--result", default="")
    args = ap.parse_args()
    path = log(
        args.action_type,
        args.description,
        mission=args.mission,
        task_id=args.task_id,
        result=args.result,
    )
    print("Logged to", path)


if __name__ == "__main__":
    main()
