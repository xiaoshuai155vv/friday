#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
维护 runtime/state/current_mission.json，读写「当前要干什么」。
用法:
  python state_tracker.py read
  python state_tracker.py set --mission "..." [--phase ...] [--goal ...] [--next ...]
  python state_tracker.py get  (同 read，输出 JSON)
"""

import argparse
import json
import os
from datetime import datetime, timezone

STATE_DIR = os.path.join(os.path.dirname(__file__), "..", "runtime", "state")
STATE_FILE = os.path.join(STATE_DIR, "current_mission.json")

DEFAULT_STATE = {
    "mission": "未设置",
    "phase": "假设",
    "current_goal": "",
    "next_action": "",
    "task_id": "",
    "loop_round": 0,
    "updated_at": "",
}


def _ensure_dir():
    os.makedirs(STATE_DIR, exist_ok=True)


def read_state():
    _ensure_dir()
    if not os.path.isfile(STATE_FILE):
        return dict(DEFAULT_STATE)
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return dict(DEFAULT_STATE)


def write_state(data):
    _ensure_dir()
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("read")
    sp.add_parser("get")
    p_set = sp.add_parser("set")
    p_set.add_argument("--mission", default=None)
    p_set.add_argument("--phase", default=None)
    p_set.add_argument("--goal", default=None, dest="current_goal")
    p_set.add_argument("--next", default=None, dest="next_action")
    p_set.add_argument("--task-id", default=None, dest="task_id")
    p_set.add_argument("--round", type=int, default=None, dest="loop_round")
    args = ap.parse_args()

    if args.cmd in ("read", "get"):
        s = read_state()
        print(json.dumps(s, ensure_ascii=False, indent=2))
        return

    if args.cmd == "set":
        s = read_state()
        if args.mission is not None:
            s["mission"] = args.mission
        if args.phase is not None:
            s["phase"] = args.phase
        if args.current_goal is not None:
            s["current_goal"] = args.current_goal
        if args.next_action is not None:
            s["next_action"] = args.next_action
        if args.task_id is not None:
            s["task_id"] = args.task_id
        if args.loop_round is not None:
            s["loop_round"] = args.loop_round
        write_state(s)
        print("OK:", json.dumps(read_state(), ensure_ascii=False, indent=2))
        return

    ap.print_help()


if __name__ == "__main__":
    main()
