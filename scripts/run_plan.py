#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
执行自动化计划：按顺序执行 截图/vision/点击/输入/按键，实现「点点点」与多模态决策。
计划为 JSON 数组，每步: screenshot | vision | click | right_click | middle_click | drag | type | key | paste | scroll | wait。
用法: python run_plan.py <plan.json>  或  python run_plan.py --stdin  (从 stdin 读 JSON)
"""
import sys
import os
import json
import subprocess
import time

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPTS)
STATE_DIR = os.path.join(PROJECT, "state")
VISION_LAST_OUTPUT = os.path.join(STATE_DIR, "vision_last_output.txt")

# 子进程统一用 UTF-8 输出，避免 vision/脚本输出 GBK 被当 UTF-8 解码导致乱码（含写入 vision_last_output.txt）
_SUBPROCESS_ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}

def run(cmd_list, cwd=None):
    return subprocess.run(
        cmd_list,
        cwd=cwd or PROJECT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=_SUBPROCESS_ENV,
    )

def step_screenshot(args):
    path = args.get("path") or os.path.join(PROJECT, "screenshots", "plan_capture.bmp")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    r = run([sys.executable, os.path.join(SCRIPTS, "screenshot_tool.py"), path], cwd=PROJECT)
    if r.returncode != 0:
        return False, r.stderr or "screenshot failed"
    return True, path.strip() if path else (r.stdout or "").strip()

def step_vision(args):
    img = args.get("image") or args.get("path")
    q = args.get("question") or args.get("q") or "描述画面内容与可点击元素。"
    if not img or not os.path.isfile(img):
        return False, "vision: image path missing or not found"
    r = run([sys.executable, os.path.join(SCRIPTS, "vision_proxy.py"), img, q])
    if r.returncode != 0:
        return False, r.stderr or "vision failed"
    return True, (r.stdout or "").strip()

def step_click(args):
    x, y = int(args.get("x", 0)), int(args.get("y", 0))
    r = run([sys.executable, os.path.join(SCRIPTS, "mouse_tool.py"), "click", str(x), str(y)])
    return r.returncode == 0, r.stderr or ""

def step_right_click(args):
    x, y = int(args.get("x", 0)), int(args.get("y", 0))
    r = run([sys.executable, os.path.join(SCRIPTS, "mouse_tool.py"), "right_click", str(x), str(y)])
    return r.returncode == 0, r.stderr or ""

def step_middle_click(args):
    x, y = int(args.get("x", 0)), int(args.get("y", 0))
    r = run([sys.executable, os.path.join(SCRIPTS, "mouse_tool.py"), "middle_click", str(x), str(y)])
    return r.returncode == 0, r.stderr or ""

def step_drag(args):
    x1, y1 = int(args.get("x1", 0)), int(args.get("y1", 0))
    x2, y2 = int(args.get("x2", 0)), int(args.get("y2", 0))
    r = run([sys.executable, os.path.join(SCRIPTS, "mouse_tool.py"), "drag", str(x1), str(y1), str(x2), str(y2)])
    return r.returncode == 0, r.stderr or ""

def step_scroll(args):
    delta = int(args.get("delta", 0))
    r = run([sys.executable, os.path.join(SCRIPTS, "mouse_tool.py"), "scroll", str(delta)])
    return r.returncode == 0, r.stderr or ""

def step_type(args):
    text = args.get("text") or args.get("t") or ""
    r = run([sys.executable, os.path.join(SCRIPTS, "keyboard_tool.py"), "type", text])
    return r.returncode == 0, r.stderr or ""

def step_key(args):
    vk = int(args.get("vk") or args.get("key") or 0)
    r = run([sys.executable, os.path.join(SCRIPTS, "keyboard_tool.py"), "key", str(vk)])
    return r.returncode == 0, r.stderr or ""

def step_paste(args):
    """Ctrl+V 粘贴（可用于粘贴剪贴板中的中文等）。"""
    r = run([sys.executable, os.path.join(SCRIPTS, "keyboard_tool.py"), "keys", "17", "86"])
    return r.returncode == 0, r.stderr or ""

def step_wait(args):
    t = float(args.get("sec") or args.get("seconds") or 1)
    time.sleep(t)
    return True, ""

def step_comment(args):
    return True, ""

def step_run(args):
    script = args.get("script") or args.get("cmd")
    if not script:
        return False, "run: missing script name"
    name = script.replace(".py", "") if script.endswith(".py") else script
    path = os.path.join(SCRIPTS, name + ".py")
    if not os.path.isfile(path):
        return False, "run: script not found " + path
    run_args = [str(a) for a in (args.get("args") or [])]
    r = subprocess.run(
        [sys.executable, path] + run_args,
        cwd=PROJECT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=_SUBPROCESS_ENV,
    )
    return r.returncode == 0, r.stderr or ""

def _safe_print_vision(out):
    """在 Windows 控制台 gbk 下安全打印 vision 输出（多为 UTF-8 文本）。"""
    try:
        print(out)
    except UnicodeEncodeError:
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            print(out)
        except (AttributeError, OSError):
            sys.stdout.buffer.write((out.encode("utf-8", errors="replace") + b"\n"))
            sys.stdout.buffer.flush()


def main():
    if "--stdin" in sys.argv:
        raw = sys.stdin.read()
    else:
        if len(sys.argv) < 2:
            print("usage: run_plan.py <plan.json>  |  run_plan.py --stdin", file=sys.stderr)
            sys.exit(1)
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            raw = f.read()
    try:
        plan = json.loads(raw)
    except Exception as e:
        print("invalid json:", e, file=sys.stderr)
        sys.exit(1)
    if not isinstance(plan, list):
        plan = plan.get("steps", plan) if isinstance(plan, dict) else []
    handlers = {
        "screenshot": step_screenshot,
        "vision": step_vision,
        "click": step_click,
        "right_click": step_right_click,
        "middle_click": step_middle_click,
        "drag": step_drag,
        "type": step_type,
        "key": step_key,
        "paste": step_paste,
        "scroll": step_scroll,
        "wait": step_wait,
        "comment": step_comment,
        "run": step_run,
    }
    for i, item in enumerate(plan):
        if not isinstance(item, dict):
            continue
        do = (item.get("do") or item.get("action") or "").lower()
        fn = handlers.get(do)
        if not fn:
            print("unknown step:", do, file=sys.stderr)
            continue
        ok, out = fn(item)
        if not ok:
            print("step {} {} failed: {}".format(i + 1, do, out), file=sys.stderr)
            sys.exit(1)
        if out and do == "vision":
            try:
                os.makedirs(STATE_DIR, exist_ok=True)
                with open(VISION_LAST_OUTPUT, "w", encoding="utf-8") as f:
                    f.write(out)
            except OSError:
                pass
            _safe_print_vision(out)
    print("plan done")

if __name__ == "__main__":
    main()
