#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进化轮次 / 功能改动后，对「非 runtime」的代码与文档做一次本地 git 提交，便于追溯。
不提交 runtime/（已在 .gitignore），仅提交 scripts/、references/、assets/、VERSION、SKILL.md 等。

用法:
  python scripts/git_commit_evolution.py [--message "提交说明"] [--bump-version] [--dry-run]
  --message  自定义提交说明；未指定则从 current_mission.json 生成
  --bump-version  先递增 VERSION 再提交（0.3.29 -> 0.3.30）
  --dry-run  只打印将要 add/commit 的内容，不执行
"""
from __future__ import print_function

import os
import sys
import json
import argparse
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STATE_FILE = os.path.join(ROOT, "runtime", "state", "current_mission.json")
VERSION_FILE = os.path.join(ROOT, "VERSION")

# 只提交这些路径（功能相关），不提交 runtime/
ADD_PATHS = ["scripts/", "references/", "assets/", "VERSION", "SKILL.md", ".gitignore"]


def _run(cmd, cwd=None, capture=True):
    try:
        r = subprocess.run(
            cmd,
            cwd=cwd or ROOT,
            capture_output=capture,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()
    except Exception as e:
        return -1, "", str(e)


def _build_message_from_state():
    msg = "evolution: 功能改动"
    try:
        if os.path.isfile(STATE_FILE):
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                s = json.load(f)
            r = s.get("loop_round") or 0
            mission = (s.get("mission") or "").strip()[:50]
            goal = (s.get("current_goal") or "").strip()[:50]
            msg = "evolution: round %s - %s" % (r, goal or mission or "功能改动")
    except Exception:
        pass
    return msg


def bump_version():
    """0.3.29 -> 0.3.30"""
    try:
        if not os.path.isfile(VERSION_FILE):
            return None
        with open(VERSION_FILE, "r", encoding="utf-8") as f:
            line = f.read().strip()
        parts = line.split(".")
        if not parts:
            return None
        last = parts[-1]
        if last.isdigit():
            parts[-1] = str(int(last) + 1)
            new_ver = ".".join(parts)
            with open(VERSION_FILE, "w", encoding="utf-8") as f:
                f.write(new_ver + "\n")
            return new_ver
    except Exception:
        pass
    return None


def main():
    ap = argparse.ArgumentParser(description="功能改动后本地 git 提交，便于追溯")
    ap.add_argument("--message", "-m", type=str, default=None, help="提交说明")
    ap.add_argument("--bump-version", action="store_true", help="先递增 VERSION 再提交")
    ap.add_argument("--dry-run", action="store_true", help="仅打印不执行")
    args = ap.parse_args()

    if not os.path.isdir(os.path.join(ROOT, ".git")):
        print("非 git 仓库，跳过提交", file=sys.stderr)
        return 0

    if args.bump_version and not args.dry_run:
        new_ver = bump_version()
        if new_ver:
            print("VERSION -> %s" % new_ver)

    # 只 add 指定路径（git 会尊重 .gitignore，这些路径下若有被 ignore 的也不会进）
    for p in ADD_PATHS:
        path = os.path.join(ROOT, p) if not os.path.isabs(p) else p
        if os.path.exists(path):
            code, out, err = _run(["git", "add", p], capture=True)
            if args.dry_run and (code != 0 or out or err):
                print("git add %s -> %s %s" % (p, out, err))

    code, out, err = _run(["git", "status", "--short"], capture=True)
    if code != 0:
        print("git status 失败: %s" % err, file=sys.stderr)
        return 1
    if not out.strip():
        print("无变更需要提交（仅跟踪 scripts/references/assets/VERSION/SKILL.md 等）")
        return 0

    message = args.message or _build_message_from_state()
    if args.dry_run:
        print("将提交:")
        print(out)
        print("提交说明: %s" % message)
        return 0

    code, out, err = _run(["git", "commit", "-m", message], capture=True)
    if code != 0:
        print("git commit 失败: %s" % (err or out), file=sys.stderr)
        return 1
    print("已提交: %s" % message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
