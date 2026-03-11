#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
场景日志：以「用户场景」为维度记录请求与执行结果，便于积累成功/失败经验。
用法:
  python scenario_log.py "<用户输入或场景描述>" "<执行的意图/命令>" success [备注]
  python scenario_log.py "打开摄像头自拍" "do 自拍" fail "摄像头未打开"
结果写入 runtime/logs/scenario_YYYY-MM-DD.log 并追加到 runtime/state/scenario_experiences.json（近期条目）。
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_DIR = os.path.join(ROOT, "runtime", "logs")
STATE_DIR = os.path.join(ROOT, "runtime", "state")
SCENARIO_LOG_PREFIX = "scenario_"
EXPERIENCES_FILE = os.path.join(STATE_DIR, "scenario_experiences.json")
MAX_ENTRIES = 500


def _ensure_dirs():
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(STATE_DIR, exist_ok=True)


def log_scenario(user_input: str, intent_or_cmd: str, result: str, note: str = ""):
    """记录一条场景：用户输入、执行方式、结果、备注。"""
    _ensure_dirs()
    ts = datetime.now(timezone.utc).isoformat()
    day = ts[:10]
    log_path = os.path.join(LOG_DIR, f"{SCENARIO_LOG_PREFIX}{day}.log")
    line = f"{ts}\t{user_input}\t{intent_or_cmd}\t{result}\t{note}\n"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line)
    # 追加到 runtime/state/scenario_experiences.json（近期 N 条）
    entry = {
        "time": ts,
        "scene": user_input,
        "intent_or_cmd": intent_or_cmd,
        "result": result,
        "note": note,
    }
    experiences = []
    if os.path.isfile(EXPERIENCES_FILE):
        try:
            with open(EXPERIENCES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                experiences = data.get("entries") or []
        except Exception:
            experiences = []
    experiences.append(entry)
    if len(experiences) > MAX_ENTRIES:
        experiences = experiences[-MAX_ENTRIES:]
    with open(EXPERIENCES_FILE, "w", encoding="utf-8") as f:
        json.dump({"entries": experiences}, f, ensure_ascii=False, indent=0)
    return log_path


def main():
    ap = argparse.ArgumentParser(description="Record user scenario and execution result.")
    ap.add_argument("user_input", help="用户输入或场景描述，如：打开摄像头给我来个自拍")
    ap.add_argument("intent_or_cmd", help="实际执行的意图/命令，如：do 自拍")
    ap.add_argument("result", choices=["success", "fail"], help="执行结果：success 或 fail")
    ap.add_argument("note", nargs="?", default="", help="可选备注，如失败原因")
    args = ap.parse_args()
    path = log_scenario(
        args.user_input.strip(),
        args.intent_or_cmd.strip(),
        args.result.strip().lower(),
        (args.note or "").strip(),
    )
    print("Logged to", path)


if __name__ == "__main__":
    main()
