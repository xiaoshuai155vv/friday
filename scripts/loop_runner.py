#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
闭环跑者：在无人参与时持续执行「假设→规划→追踪→校验→决策」一轮，并更新状态与日志。
用法:
  python loop_runner.py          # 执行一轮后退出
  python loop_runner.py --daemon [--interval 300]   # 每 interval 秒执行一轮，持续运行
用于：你启动后挂后台或设为计划任务，FRIDAY 的轮次与日志会持续前进，不会「停在那儿」。
注意：真正的「假设内容/规划内容」仍可由 Cursor/Agent 在对话中执行；本脚本负责推进轮次与自校验。
"""
import sys
import os
import json
import subprocess
import time
import argparse

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPTS)
STATE_FILE = os.path.join(PROJECT, "state", "current_mission.json")

def run(cmd_list, timeout=120):
    try:
        r = subprocess.run(
            cmd_list,
            cwd=PROJECT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        return r.returncode == 0
    except Exception:
        return False

def read_state():
    if not os.path.isfile(STATE_FILE):
        return {"loop_round": 0}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"loop_round": 0}

def one_round():
    s = read_state()
    r = (s.get("loop_round") or 0) + 1
    mission = "Round{} loop_runner".format(r)
    py = sys.executable
    run([py, os.path.join(SCRIPTS, "behavior_log.py"), "assume",
        "Round{} assume: capability extension".format(r), "--mission", mission])
    run([py, os.path.join(SCRIPTS, "behavior_log.py"), "plan",
        "Round{} plan: self_verify and state advance".format(r), "--mission", mission])
    run([py, os.path.join(SCRIPTS, "behavior_log.py"), "track",
        "Round{} track: running".format(r), "--mission", mission])
    ok = run([py, os.path.join(SCRIPTS, "self_verify_capabilities.py")], timeout=60)
    run([py, os.path.join(SCRIPTS, "behavior_log.py"), "verify",
        "Round{} verify: self_verify {}".format(r, "pass" if ok else "fail"),
        "--mission", mission, "--result", "pass" if ok else "fail"])
    run([py, os.path.join(SCRIPTS, "behavior_log.py"), "decide",
        "Round{} decide: continue".format(r), "--mission", mission])
    run([py, os.path.join(SCRIPTS, "state_tracker.py"), "set",
        "--mission", mission, "--phase", "assume", "--next", "plan", "--round", str(r)])
    run([py, os.path.join(SCRIPTS, "export_recent_logs.py"), "60"])
    return r

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--daemon", action="store_true", help="Run loop forever with interval")
    ap.add_argument("--interval", type=int, default=300, help="Seconds between rounds when daemon (default 300)")
    args = ap.parse_args()
    if args.daemon:
        while True:
            r = one_round()
            print("Round {} done, sleep {}s".format(r, args.interval))
            time.sleep(args.interval)
    else:
        r = one_round()
        print("Round {} done".format(r))
    return 0

if __name__ == "__main__":
    sys.exit(main())
