#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 vision 输出解析点击坐标：能解析则点击（可加 offset），否则发送按键（如回车选第一条）。
用于 run_plan 中 vision 返回「否」或无法解析时兜底，不中断计划。
用法: python click_from_vision_or_key.py [fallback_vk] [offset_x] [offset_y]
  默认 fallback_vk=13(回车)，offset_x=0，offset_y=0。
  例: python click_from_vision_or_key.py 13 210 0
"""
import sys
import os
import re

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPTS)
STATE_DIR = os.path.join(PROJECT, "runtime", "state")
VISION_LAST_OUTPUT = os.path.join(STATE_DIR, "vision_last_output.txt")

def _parse_xy(text):
    if not text or not text.strip():
        return None
    candidates = []
    for m in re.finditer(r"(\d+)\s+(\d+)", text):
        x, y = int(m.group(1)), int(m.group(2))
        if 0 <= x <= 5000 and 0 <= y <= 3000:
            candidates.append((x, y))
    for m in re.finditer(r"(\d+)\s*[,，]\s*(\d+)", text):
        x, y = int(m.group(1)), int(m.group(2))
        if 0 <= x <= 5000 and 0 <= y <= 3000:
            candidates.append((x, y))
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    return min(candidates, key=lambda p: p[0])

def main():
    fallback_vk = 13
    offset_x = offset_y = 0
    if len(sys.argv) >= 2:
        fallback_vk = int(sys.argv[1])
    if len(sys.argv) >= 3:
        offset_x = int(sys.argv[2])
    if len(sys.argv) >= 4:
        offset_y = int(sys.argv[3])

    content = ""
    if os.path.isfile(VISION_LAST_OUTPUT):
        try:
            with open(VISION_LAST_OUTPUT, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError:
            pass

    parsed = _parse_xy(content)
    if parsed:
        x, y = parsed[0] + offset_x, parsed[1] + offset_y
        try:
            from vision_calibration_helper import ensure_calibration
            cox, coy = ensure_calibration()
            x, y = x + cox, y + coy
        except Exception:
            pass
        r = __import__("subprocess").run(
            [sys.executable, os.path.join(SCRIPTS, "mouse_tool.py"), "click", str(x), str(y)],
            cwd=PROJECT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if r.returncode != 0:
            print("click failed:", r.stderr or "", file=sys.stderr)
            sys.exit(1)
        print("click (%s, %s)" % (x, y), file=sys.stderr)
    else:
        r = __import__("subprocess").run(
            [sys.executable, os.path.join(SCRIPTS, "keyboard_tool.py"), "key", str(fallback_vk)],
            cwd=PROJECT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if r.returncode != 0:
            print("key %s failed:" % fallback_vk, r.stderr or "", file=sys.stderr)
            sys.exit(1)
        print("fallback key %s (no coords parsed)" % fallback_vk, file=sys.stderr)

if __name__ == "__main__":
    main()
