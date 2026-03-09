#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
执行自动化计划：按顺序执行 截图/vision/点击/输入/按键，实现「点点点」与多模态决策。
计划为 JSON 数组，每步: screenshot | vision | click | right_click | middle_click | drag | type | key | paste | scroll | wait | run。click 可设 "from_vision_coords": true，则从上一步 vision 输出中解析 x y 再点击（不写死坐标）。
用法: python run_plan.py <plan.json> [--var k=v] [--contact 名] 或 --stdin；计划内 {{key}} 会被替换
"""
import sys
import os
import json
import re
import subprocess
import time
from datetime import datetime

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
    # 生成带时间戳的路径，便于区分多轮截图、大模型与人工排查
    dirname, basename = os.path.split(path)
    name, ext = os.path.splitext(basename)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path_ts = os.path.join(dirname, name + "_" + ts + ext) if dirname else (name + "_" + ts + ext)
    path_ts = os.path.normpath(path_ts)
    abs_dir = os.path.join(PROJECT, dirname) if dirname else os.path.join(PROJECT, "screenshots")
    os.makedirs(abs_dir, exist_ok=True)
    r = run([sys.executable, os.path.join(SCRIPTS, "screenshot_tool.py"), path_ts], cwd=PROJECT)
    if r.returncode != 0:
        return False, r.stderr or "screenshot failed"
    return True, path_ts

def step_vision(args):
    img = args.get("image") or args.get("path")
    q = args.get("question") or args.get("q") or "描述画面内容与可点击元素。"
    if not img or not os.path.isfile(img):
        return False, "vision: image path missing or not found"
    # 坐标需求用 vision_coords（内部多轮取中位数）；非坐标用 vision_proxy
    if args.get("coords") or args.get("runs", 1) > 1:
        cmd = [sys.executable, os.path.join(SCRIPTS, "vision_coords.py"), "--runs", "3", img, q]
    else:
        cmd = [sys.executable, os.path.join(SCRIPTS, "vision_proxy.py"), img, q]
    r = run(cmd)
    if r.stderr:
        print(r.stderr, file=sys.stderr, end="")
    if r.returncode != 0:
        return False, r.stderr or "vision failed"
    return True, (r.stdout or "").strip()

def _parse_xy_from_text(text):
    """从文本中解析 x y 坐标，支持多种 vision 输出格式。返回 (x,y) 或 None。"""
    if not text or not text.strip():
        return None
    # 收集所有可能的坐标对（屏幕范围约 0-5000 x 0-3000）
    candidates = []
    for m in re.finditer(r"(\d+)\s+(\d+)", text):
        x, y = int(m.group(1)), int(m.group(2))
        if 0 <= x <= 5000 and 0 <= y <= 3000:
            candidates.append((x, y))
    for m in re.finditer(r"(\d+)\s*[,，]\s*(\d+)", text):
        x, y = int(m.group(1)), int(m.group(2))
        if 0 <= x <= 5000 and 0 <= y <= 3000:
            candidates.append((x, y))
    # 多对时优先取 x 较小的（左侧列表）；单对直接返回
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    # 左侧会话列表通常 x < 400，取 x 最小的作为列表项
    return min(candidates, key=lambda p: p[0])


def step_click(args):
    if args.get("from_vision_coords") or args.get("use_last_vision_coords"):
        if not os.path.isfile(VISION_LAST_OUTPUT):
            return False, "click(from_vision_coords): no vision output file, run vision step first"
        try:
            with open(VISION_LAST_OUTPUT, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError as e:
            return False, "click(from_vision_coords): " + str(e)
        parsed = _parse_xy_from_text(content)
        if not parsed:
            return False, "click(from_vision_coords): could not parse x y from last vision output (raw: %s)" % (content[:200].replace("\n", " "))
        x, y = parsed
        # 可选：对 vision 坐标做固定偏移（如 ihaier 左侧栏导致模型返回相对内容区坐标时，x 少约 210）
        offset = args.get("vision_coords_offset")
        if isinstance(offset, dict):
            x += int(offset.get("x", 0))
            y += int(offset.get("y", 0))
            print("click(from_vision_coords): offset applied (%s, %s) -> (%s, %s)" % (parsed[0], parsed[1], x, y), file=sys.stderr)
        else:
            print("click(from_vision_coords): parsed (%s, %s)" % (x, y), file=sys.stderr)
        # 校准：按当前分辨率查校准数据，不存在则自动校准一次，再加上校准偏移
        try:
            from vision_calibration_helper import ensure_calibration
            cox, coy = ensure_calibration()
            if cox or coy:
                x, y = x + cox, y + coy
                print("click(from_vision_coords): calibration applied (+%s, +%s) -> (%s, %s)" % (cox, coy, x, y), file=sys.stderr)
        except Exception:
            pass
    else:
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
    if r.stderr:
        print(r.stderr, file=sys.stderr, end="")
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
    if r.stderr:
        print(r.stderr, file=sys.stderr, end="")
    return r.returncode == 0, r.stderr or ""

def _substitute_vars(obj, vars_dict):
    """递归替换 obj 中字符串里的 {{key}} 为 vars_dict[key]。"""
    if not vars_dict:
        return obj
    if isinstance(obj, str):
        for k, v in vars_dict.items():
            obj = obj.replace("{{" + k + "}}", str(v))
        return obj
    if isinstance(obj, dict):
        return {key: _substitute_vars(val, vars_dict) for key, val in obj.items()}
    if isinstance(obj, list):
        return [_substitute_vars(item, vars_dict) for item in obj]
    return obj


def _parse_plan_vars(argv):
    """从 argv 解析 --var k=v 和 --contact 联系人，返回 dict。"""
    out = {}
    i = 1
    while i < len(argv):
        if argv[i] == "--var" and i + 1 < len(argv):
            part = argv[i + 1]
            i += 2
            if "=" in part:
                k, v = part.split("=", 1)
                out[k.strip()] = v.strip()
            continue
        if argv[i] == "--contact" and i + 1 < len(argv):
            out["contact"] = argv[i + 1]
            i += 2
            continue
        i += 1
    return out


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
    argv = sys.argv[1:]
    if "--stdin" in argv:
        raw = sys.stdin.read()
        plan_path_idx = -1
    else:
        if not argv or argv[0].startswith("--"):
            print("usage: run_plan.py <plan.json> [--var k=v] [--contact 名]  |  run_plan.py --stdin", file=sys.stderr)
            sys.exit(1)
        plan_path_idx = 0
        with open(argv[0], "r", encoding="utf-8") as f:
            raw = f.read()
    try:
        plan = json.loads(raw)
    except Exception as e:
        print("invalid json:", e, file=sys.stderr)
        sys.exit(1)
    if not isinstance(plan, list):
        plan = plan.get("steps", plan) if isinstance(plan, dict) else []
    vars_dict = _parse_plan_vars(sys.argv)
    if vars_dict:
        plan = _substitute_vars(plan, vars_dict)
    last_screenshot_plan_path = None
    last_screenshot_actual_path = None
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
        print("step %d: %s" % (i + 1, do), file=sys.stderr)
        if do == "vision" and last_screenshot_plan_path and last_screenshot_actual_path:
            item = dict(item)
            img = (item.get("image") or item.get("path") or "").strip()
            if img and os.path.normpath(img) == last_screenshot_plan_path:
                item["image"] = last_screenshot_actual_path
        ok, out = fn(item)
        if not ok:
            print("step %d %s failed: %s" % (i + 1, do, out), file=sys.stderr)
            sys.exit(1)
        if do == "screenshot" and ok and out:
            last_screenshot_plan_path = os.path.normpath(item.get("path") or "")
            last_screenshot_actual_path = out
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
