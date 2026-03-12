#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进化环定时触发守护进程（独立于悬浮球，无 PyQt 依赖）

从悬浮球中提取的「定时触发调用 CC 进化环」能力，供通用智能体、cron、Windows 计划任务等
在无 GUI 环境下使用。与悬浮球内的「开启自动进化环」逻辑等价。

用法:
  python scripts/evolution_loop_daemon.py              # 按配置间隔循环触发
  python scripts/evolution_loop_daemon.py --once         # 仅触发一轮后退出
  python scripts/evolution_loop_daemon.py --interval 600 # 指定间隔秒数

配置: runtime/config/evolution_loop.json
  auto_interval_seconds  默认间隔（秒），最小 60
  friday_project_path    技能项目路径（默认脚本所在项目根）
  ccr_base_url, ccr_api_key  同 evolution_loop_client
"""
from __future__ import print_function

import os
import sys
import json
import time
import glob
import subprocess
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS = os.path.join(ROOT, "scripts")
CONFIG_FILE = os.path.join(ROOT, "runtime", "config", "evolution_loop.json")
STATE_DIR = os.path.join(ROOT, "runtime", "state")
LOG_DIR = os.path.join(ROOT, "runtime", "logs")
EVOLUTION_LAST_STATUS_FILE = os.path.join(STATE_DIR, "evolution_last_status.json")


def _load_config(project_path=None):
    root = project_path or ROOT
    cfg_path = os.path.join(root, "runtime", "config", "evolution_loop.json")
    if os.path.isfile(cfg_path):
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _state_dir(project_path):
    return os.path.join(project_path or ROOT, "runtime", "state")


def _log_dir(project_path):
    return os.path.join(project_path or ROOT, "runtime", "logs")


def can_submit_evolution(project_path=None):
    """复用 evolution_loop_client 逻辑：上一轮是否已完成。"""
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from evolution_loop_client import can_submit_evolution as _can
        return _can(project_path or ROOT)
    except Exception:
        return True


def load_evolution_last_status(project_path=None):
    """读最近一次进化环请求状态。"""
    root = project_path or ROOT
    path = os.path.join(_state_dir(root), "evolution_last_status.json")
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                d = json.load(f)
            return d.get("status"), d.get("at", ""), d.get("message", "")
        except Exception:
            pass
    return None, "", ""


def cc_completed_after_timeout(timeout_at_iso, project_path=None):
    """超时后若 behavior 日志出现 decide，则认为 CC 已完成该轮。"""
    try:
        s = (timeout_at_iso or "").strip().replace("Z", "+00:00")
        t0 = datetime.fromisoformat(s)
        if t0.tzinfo is None:
            t0 = t0.replace(tzinfo=timezone.utc)

        root = project_path or ROOT
        log_dir = _log_dir(root)
        pattern = os.path.join(log_dir, "behavior_*.log")
        files = sorted(glob.glob(pattern))
        if not files:
            return False
        for path in reversed(files[-2:]):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    lines = f.readlines()[-400:]
                for line in reversed(lines):
                    line = (line or "").strip()
                    if not line:
                        continue
                    parts = line.split("\t", 5)
                    if len(parts) < 2:
                        continue
                    ts, phase = parts[0], parts[1]
                    if phase != "decide":
                        continue
                    try:
                        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc)
                        if dt > t0:
                            return True
                    except Exception:
                        continue
            except Exception:
                continue
    except Exception:
        pass
    return False


def run_ack_complete(project_path=None):
    """清除超时状态（CC 已跑完时）。"""
    root = project_path or ROOT
    client = os.path.join(root, "scripts", "evolution_loop_client.py")
    try:
        r = subprocess.run(
            [sys.executable, client, "--ack-complete"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=15,
            encoding="utf-8",
            errors="replace",
        )
        return r.returncode == 0
    except Exception:
        return False


def run_one_evolution(project_path=None):
    """提交一轮自动进化环（带 --auto-evolution）。"""
    root = project_path or ROOT
    client = os.path.join(root, "scripts", "evolution_loop_client.py")
    cfg = _load_config(root)
    timeout = max(60, int(cfg.get("request_timeout_seconds") or 300)) + 120
    try:
        proc = subprocess.run(
            [sys.executable, client, "--once", "--auto-evolution"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        return proc.returncode == 0, proc.stdout or "", proc.stderr or ""
    except subprocess.TimeoutExpired:
        return False, "", "timeout"
    except Exception as e:
        return False, "", str(e)


def main():
    import argparse
    ap = argparse.ArgumentParser(description="进化环定时触发守护进程（无 GUI）")
    ap.add_argument("--once", action="store_true", help="仅触发一轮后退出")
    ap.add_argument("--interval", "-i", type=int, default=None, help="间隔秒数，覆盖配置文件")
    ap.add_argument("--project", "-p", type=str, default=None, help="技能项目路径")
    args = ap.parse_args()

    project_path = os.path.abspath(args.project or ROOT)
    cfg = _load_config(project_path)
    interval = args.interval if args.interval is not None else max(60, int(cfg.get("auto_interval_seconds") or 300))

    if args.once:
        if not can_submit_evolution(project_path):
            status, at, _ = load_evolution_last_status(project_path)
            if status == "timeout" and at:
                try:
                    s = at.replace("Z", "+00:00")
                    dt = datetime.fromisoformat(s)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    elapsed = (datetime.now(timezone.utc) - dt).total_seconds()
                    if 0 < elapsed < 300 and cc_completed_after_timeout(at, project_path):
                        run_ack_complete(project_path)
                except Exception:
                    pass
            if not can_submit_evolution(project_path):
                print("上一轮未完成，跳过提交。", file=sys.stderr)
                return 1
        ok, out, err = run_one_evolution(project_path)
        if ok:
            print("OK:", out.strip() or "submitted")
            return 0
        print("FAIL:", err or out, file=sys.stderr)
        return 1

    # 循环模式
    print("evolution_loop_daemon: 每 %s 秒触发一轮，项目: %s" % (interval, project_path))
    while True:
        time.sleep(interval)
        if not can_submit_evolution(project_path):
            status, at, _ = load_evolution_last_status(project_path)
            if status == "timeout" and at:
                try:
                    s = at.replace("Z", "+00:00")
                    dt = datetime.fromisoformat(s)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    elapsed = (datetime.now(timezone.utc) - dt).total_seconds()
                    if 0 < elapsed < 300 and cc_completed_after_timeout(at, project_path):
                        run_ack_complete(project_path)
                    else:
                        time.sleep(60)
                        continue
                except Exception:
                    pass
            else:
                time.sleep(60)
                continue
        ok, out, err = run_one_evolution(project_path)
        ts = datetime.now().strftime("%H:%M:%S")
        if ok:
            print("[%s] OK" % ts)
        else:
            print("[%s] FAIL: %s" % (ts, (err or out)[:100]), file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main() or 0)
