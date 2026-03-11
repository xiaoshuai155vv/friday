#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
执行自动化计划：按顺序执行 截图/vision/点击/输入/按键，实现「点点点」与多模态决策。
计划为 JSON 数组，每步: screenshot | vision | vision_coords | click | ...。vision=通用看图；vision_coords=获取点击坐标（多轮取中位数）。click 可设 "from_vision_coords": true 从上一步 vision/vision_coords 输出解析 x y。
用法: python run_plan.py <plan.json> [--var k=v] [--contact 名] [--period 月度|季度|年度] [--verbose] [--no-floating] [--max-retry N] [--retry-delay SEC] [--resume[N]] 或 --stdin
  默认打印多模态提示词与模型输出；--no-verbose 可关闭
  默认启动时自动拉起 Qt 悬浮球，进度与输出在悬浮球上可见；--no-floating 可跳过
  --max-retry N: 关键步骤失败时最大重试次数（默认0，不重试）；--retry-delay SEC: 重试间隔秒数（默认2）
  --resume: 从上一个中断点恢复执行；--resume N: 从第 N 步恢复执行
"""
import sys
import os
import json
import re
import subprocess
import time
from datetime import datetime

# 导入任务状态推送模块（用于推送到 task_status.json）
try:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    import task_status_pusher
    _TASK_PUSHER_AVAILABLE = True
except ImportError:
    # 如果无法导入，定义空实现
    _TASK_PUSHER_AVAILABLE = False
    class task_status_pusher:
        @staticmethod
        def update_task_status(*args, **kwargs):
            pass
        @staticmethod
        def clear_task_status(*args, **kwargs):
            pass
        @staticmethod
        def get_task_status(*args, **kwargs):
            return None

# 导入任务状态管理模块
try:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    import task_state_manager
    _TASK_STATE_MANAGER_AVAILABLE = True
except ImportError:
    # 如果无法导入，定义空实现
    _TASK_STATE_MANAGER_AVAILABLE = False
    class task_state_manager:
        @staticmethod
        def save_task_state(*args, **kwargs):
            return True
        @staticmethod
        def clear_interrupted_task(*args, **kwargs):
            pass

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPTS)
STATE_DIR = os.path.join(PROJECT, "runtime", "state")
VISION_LAST_OUTPUT = os.path.join(STATE_DIR, "vision_last_output.txt")
CURRENT_MISSION_FILE = os.path.join(STATE_DIR, "current_mission.json")
LOG_DIR = os.path.join(PROJECT, "runtime", "logs")

# 子进程统一用 UTF-8 输出，避免 vision/脚本输出 GBK 被当 UTF-8 解码导致乱码（含写入 vision_last_output.txt）
_SUBPROCESS_ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}

_CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) if sys.platform == "win32" else 0

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
    path = args.get("path") or os.path.join(PROJECT, "runtime", "screenshots", "plan_capture.bmp")
    # 生成带时间戳的路径，便于区分多轮截图、大模型与人工排查
    dirname, basename = os.path.split(path)
    name, ext = os.path.splitext(basename)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path_ts = os.path.join(dirname, name + "_" + ts + ext) if dirname else (name + "_" + ts + ext)
    path_ts = os.path.normpath(path_ts)
    abs_dir = os.path.join(PROJECT, dirname) if dirname else os.path.join(PROJECT, "runtime", "screenshots")
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
    # vision 通用看图；vision_coords 或 coords:true 用 vision_coords（多轮取中位数）
    use_coords = args.get("coords") or args.get("runs", 1) > 1
    if use_coords:
        cmd = [sys.executable, os.path.join(SCRIPTS, "vision_coords.py"), "--runs", "3"]
        if args.get("normalized", True):
            cmd.append("--normalized")
        elif args.get("pixel"):
            cmd.append("--pixel")
        if os.environ.get("FRIDAY_VISION_VERBOSE", "").lower() in ("1", "true", "yes"):
            cmd.append("--verbose")
        cmd.extend([img, q])
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
    cmd = [sys.executable, os.path.join(SCRIPTS, "mouse_tool.py"), "scroll", str(delta)]
    if "x" in args and "y" in args:
        cmd.extend([str(int(args["x"])), str(int(args["y"]))])
    r = run(cmd)
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
    """从 argv 解析 --var k=v、--contact、--period、--no-verbose、--no-floating、--max-retry、--retry-delay、--fallback、--resume，返回 (vars_dict, verbose, no_floating, max_retry, retry_delay, fallback_path, resume_from_step)。"""
    out = {}
    verbose = True  # 默认开启
    no_floating = False
    max_retry = 0
    retry_delay = 2
    fallback_path = None
    resume_from_step = None  # 从中断点恢复的步骤索引
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
        if argv[i] == "--period" and i + 1 < len(argv):
            out["period"] = argv[i + 1]
            i += 2
            continue
        if argv[i] == "--no-verbose":
            verbose = False
            i += 1
            continue
        if argv[i] == "--no-floating":
            no_floating = True
            i += 1
            continue
        if argv[i] == "--max-retry" and i + 1 < len(argv):
            try:
                max_retry = int(argv[i + 1])
                i += 2
            except ValueError:
                i += 1
            continue
        if argv[i] == "--retry-delay" and i + 1 < len(argv):
            try:
                retry_delay = float(argv[i + 1])
                i += 1
            except ValueError:
                i += 1
            continue
        if argv[i] == "--fallback" and i + 1 < len(argv):
            fallback_path = argv[i + 1]
            i += 2
            continue
        if argv[i] == "--resume":
            # 解析恢复步骤索引，如 --resume=5 或 --resume
            if i + 1 < len(argv) and argv[i + 1].isdigit():
                resume_from_step = int(argv[i + 1])
                i += 2
            elif i + 1 < len(argv) and argv[i + 1].startswith("--"):
                # --resume 后面跟着另一个参数，表示从上一个中断点恢复
                resume_from_step = 0  # 0 表示从上一个中断点恢复
                i += 1
            else:
                # --resume 没有参数，表示从上一个中断点恢复
                resume_from_step = 0  # 0 表示从上一个中断点恢复
                i += 1
            continue
        i += 1
    return out, verbose, no_floating, max_retry, retry_delay, fallback_path, resume_from_step


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


# 错误码定义（基于 failures.md 高频错误类型）
ERROR_CODES = {
    "ERR_ENCODING": {"code": "E001", "desc": "编码错误", "category": "encoding"},
    "ERR_WINDOW_ACTIVATE": {"code": "E002", "desc": "窗口激活失败", "category": "window"},
    "ERR_WINDOW_MAXIMIZE": {"code": "E003", "desc": "窗口最大化失败", "category": "window"},
    "ERR_VISION": {"code": "E004", "desc": "多模态/vision错误", "category": "vision"},
    "ERR_VISION_TIMEOUT": {"code": "E005", "desc": "vision超时", "category": "vision"},
    "ERR_VISION_COORDS": {"code": "E006", "desc": "vision坐标错误", "category": "vision"},
    "ERR_CLIPBOARD": {"code": "E007", "desc": "剪贴板失败", "category": "clipboard"},
    "ERR_PROCESS": {"code": "E008", "desc": "进程错误", "category": "process"},
    "ERR_QT_PLATFORM": {"code": "E009", "desc": "Qt平台插件错误", "category": "platform"},
    "ERR_CAMERA": {"code": "E010", "desc": "摄像头错误", "category": "hardware"},
    "ERR_GENERIC": {"code": "E999", "desc": "通用错误", "category": "unknown"},
}


def _log_structured_error(error_type, description, context=None):
    """记录结构化错误日志，便于问题溯源和错误统计。"""
    error_info = ERROR_CODES.get(error_type, ERROR_CODES["ERR_GENERIC"])
    error_record = {
        "timestamp": datetime.now().isoformat(),
        "error_type": error_type,
        "error_code": error_info["code"],
        "error_desc": error_info["desc"],
        "error_category": error_info["category"],
        "description": description,
        "context": context or {},
    }
    # 写入错误日志文件
    error_log_path = os.path.join(LOG_DIR, "run_plan_errors.json")
    errors = []
    if os.path.exists(error_log_path):
        try:
            with open(error_log_path, "r", encoding="utf-8") as f:
                errors = json.load(f)
        except (json.JSONDecodeError, OSError):
            errors = []
    errors.append(error_record)
    # 保留最近100条错误记录
    errors = errors[-100:]
    try:
        with open(error_log_path, "w", encoding="utf-8") as f:
            json.dump(errors, f, ensure_ascii=False, indent=2)
    except OSError:
        pass
    return error_record


def _run_fallback_plan(fallback_plan, vars_dict, handlers, max_retry, retry_delay, plan_verbose):
    """执行 fallback 计划。当主计划失败时调用此函数尝试备用方案。"""
    print("=== FALLBACK: trying alternative plan with %d steps ===" % len(fallback_plan), file=sys.stderr)
    fallback_vars = _substitute_vars(fallback_plan, vars_dict)
    last_screenshot_plan_path = None
    last_screenshot_actual_path = None

    for i, item in enumerate(fallback_vars):
        if not isinstance(item, dict):
            continue
        do = (item.get("do") or item.get("action") or "").lower()
        fn = handlers.get(do)
        if not fn:
            print("fallback unknown step:", do, file=sys.stderr)
            continue
        print("fallback step %d: %s" % (i + 1, do), file=sys.stderr)

        if do in ("vision", "vision_coords") and last_screenshot_plan_path and last_screenshot_actual_path:
            item = dict(item)
            img = (item.get("image") or item.get("path") or "").strip()
            if img and os.path.normpath(img) == last_screenshot_plan_path:
                item["image"] = last_screenshot_actual_path

        # 重试逻辑
        retries = 0
        ok = False
        out = ""

        while not ok and retries <= max_retry:
            ok, out = fn(item)
            if not ok and retries < max_retry:
                print("fallback step %d %s failed (attempt %d/%d): %s, retrying..." % (i + 1, do, retries + 1, max_retry + 1, out), file=sys.stderr)
                time.sleep(retry_delay)
                retries += 1
            elif not ok and retries >= max_retry:
                break
            else:
                break

        if not ok:
            print("fallback step %d %s failed: %s" % (i + 1, do, out), file=sys.stderr)
            return False, "fallback failed at step %d: %s" % (i + 1, out)

        if do == "screenshot" and ok and out:
            last_screenshot_plan_path = os.path.normpath(item.get("path") or "")
            last_screenshot_actual_path = out
        if out and do in ("vision", "vision_coords"):
            try:
                os.makedirs(STATE_DIR, exist_ok=True)
                with open(VISION_LAST_OUTPUT, "w", encoding="utf-8") as f:
                    f.write(out)
            except OSError:
                pass
            if plan_verbose:
                _safe_print_vision(out)

    print("=== FALLBACK: alternative plan completed successfully ===", file=sys.stderr)
    return True, "fallback completed"


def _launch_floating_ball():
    """无 CMD 窗口启动 Qt 悬浮球，供悬浮球显示 run_plan 进度。"""
    try:
        launch_script = os.path.join(SCRIPTS, "launch_friday_floating.py")
        if os.path.isfile(launch_script):
            subprocess.Popen(
                [sys.executable, launch_script],
                cwd=PROJECT,
                creationflags=_CREATE_NO_WINDOW,
                env={**os.environ, "PYTHONIOENCODING": "utf-8", "FRIDAY_LAUNCH_NO_WINDOW": "1"},
            )
    except Exception:
        pass


def _update_floating_state(plan_name, step_idx, do, phase_display, desc_display):
    """更新 runtime/state/current_mission.json 和 runtime/logs/behavior_*.log，供悬浮球实时显示。"""
    mission = os.path.basename(plan_name) if plan_name else "run_plan"
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        state = {
            "mission": mission,
            "phase": do,
            "loop_round": step_idx,
        }
        with open(CURRENT_MISSION_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=0)
    except OSError:
        pass
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        today = datetime.now().strftime("%Y-%m-%d")
        log_path = os.path.join(LOG_DIR, "behavior_%s.log" % today)
        ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        # 悬浮球弹框显示 phase · desc
        line = "%s\t%s\t%s\tmission=%s\n" % (ts, phase_display, desc_display, mission)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line)
    except OSError:
        pass


def main():
    argv = sys.argv[1:]
    if "--stdin" in argv:
        raw = sys.stdin.read()
        plan_path_idx = -1
    else:
        if not argv or argv[0].startswith("--"):
            print("usage: run_plan.py <plan.json> [--var k=v] [--contact 名] [--period 月度|季度|年度] [--no-verbose] [--no-floating] [--max-retry N] [--retry-delay SEC] [--fallback fallback.json] [--resume[N]]  |  run_plan.py --stdin", file=sys.stderr)
            sys.exit(1)
        plan_path_idx = 0
        with open(argv[0], "r", encoding="utf-8") as f:
            raw = f.read()
    try:
        plan_data = json.loads(raw)
    except Exception as e:
        print("invalid json:", e, file=sys.stderr)
        sys.exit(1)
    # 支持 plan 顶层包含 fallback 字段
    fallback_plan = None
    if isinstance(plan_data, dict):
        fallback_plan = plan_data.get("fallback")
        if fallback_plan and isinstance(fallback_plan, list) and fallback_plan:
            print("Found fallback plan in JSON with %d steps" % len(fallback_plan), file=sys.stderr)
        plan = plan_data.get("steps", plan_data)
    else:
        plan = plan_data
    vars_dict, plan_verbose, no_floating, max_retry, retry_delay, fallback_path, resume_from_step = _parse_plan_vars(sys.argv)
    # 默认开启 verbose，打印多模态提示词与模型输出；--no-verbose 可关闭
    if plan_verbose:
        os.environ["FRIDAY_VISION_VERBOSE"] = "1"
    plan_path = argv[0] if plan_path_idx >= 0 and argv else ""
    if "performance_declaration" in plan_path and "period" not in vars_dict:
        vars_dict["period"] = "月度"
    if vars_dict:
        plan = _substitute_vars(plan, vars_dict)
    # 加载外部 fallback 计划
    if fallback_path:
        try:
            with open(fallback_path, "r", encoding="utf-8") as f:
                fallback_plan = json.load(f)
            if isinstance(fallback_plan, dict):
                fallback_plan = fallback_plan.get("steps", fallback_plan)
            print("Loaded external fallback plan from %s with %d steps" % (fallback_path, len(fallback_plan) if fallback_plan else 0), file=sys.stderr)
        except Exception as e:
            print("Failed to load fallback plan: %s" % e, file=sys.stderr)
            fallback_plan = None
    if not no_floating:
        _launch_floating_ball()
    last_screenshot_plan_path = None
    last_screenshot_actual_path = None
    def step_vision_coords(args):
        args = dict(args)
        args["coords"] = True
        return step_vision(args)

    handlers = {
        "screenshot": step_screenshot,
        "vision": step_vision,
        "vision_coords": step_vision_coords,
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

    # 初始化任务状态推送（推送到 task_status.json）
    if _TASK_PUSHER_AVAILABLE:
        task_id = os.path.basename(plan_path) if plan_path else "run_plan"
        total_steps = len([p for p in plan if isinstance(p, dict)])
        task_status_pusher.update_task_status(
            task_id, "running",
            f"开始执行计划，共 {total_steps} 个步骤",
            0
        )

    # 检查是否有未完成的任务可以恢复
    start_step = 0  # 默认从第一步开始
    if _TASK_STATE_MANAGER_AVAILABLE and plan_path:
        interrupted_tasks = task_state_manager.get_interrupted_tasks()
        # 查找当前计划的中断任务
        current_interrupted = [t for t in interrupted_tasks if t.get("plan_path") == plan_path and t.get("status") == "interrupted"]
        if current_interrupted:
            last_task = current_interrupted[-1]
            if resume_from_step is not None:
                # 用户指定了恢复步骤
                if resume_from_step == 0:
                    # --resume 不带参数，从上一个中断点恢复
                    start_step = last_task.get("step_index", 0)
                else:
                    # --resume=N，从指定步骤恢复
                    start_step = resume_from_step
                print("Resuming from step %d (previous: step %d '%s')" % (
                    start_step,
                    last_task.get("step_index", 0),
                    last_task.get("step_name", "")
                ), file=sys.stderr)
            else:
                print("Found interrupted task from previous session:", file=sys.stderr)
                print("  Last completed step: %d/%d (%s) at %s" % (
                    last_task.get("step_index", 0),
                    last_task.get("total_steps", 0),
                    last_task.get("step_name", ""),
                    last_task.get("saved_at", "")
                ), file=sys.stderr)
                print("  Use --resume flag to resume from last step", file=sys.stderr)

    for i, item in enumerate(plan):
        # 跳过已完成的步骤（恢复执行时）
        if i < start_step:
            print("step %d: %s (skipped - already completed)" % (i + 1, item.get("do", "unknown")), file=sys.stderr)
            continue
        if not isinstance(item, dict):
            continue
        do = (item.get("do") or item.get("action") or "").lower()
        fn = handlers.get(do)
        if not fn:
            print("unknown step:", do, file=sys.stderr)
            continue
        print("step %d: %s" % (i + 1, do), file=sys.stderr)
        _update_floating_state(plan_path, i + 1, do, "step %d: %s" % (i + 1, do), "…")
        # 推送任务状态（步骤开始）
        if _TASK_PUSHER_AVAILABLE:
            total = len([p for p in plan if isinstance(p, dict)])
            progress = int((i / total) * 100) if total > 0 else 0
            task_status_pusher.update_task_status(
                task_id, "running",
                f"步骤 {i+1}/{total}: {do}",
                progress
            )
        if do in ("vision", "vision_coords") and last_screenshot_plan_path and last_screenshot_actual_path:
            item = dict(item)
            img = (item.get("image") or item.get("path") or "").strip()
            if img and os.path.normpath(img) == last_screenshot_plan_path:
                item["image"] = last_screenshot_actual_path

        # 重试逻辑
        max_retries = max_retry if max_retry > 0 else 0
        retries = 0
        ok = False
        out = ""

        while not ok and retries <= max_retries:
            ok, out = fn(item)
            if not ok and retries < max_retries:
                print("step %d %s failed (attempt %d/%d): %s, retrying in %.1f seconds..." % (i + 1, do, retries + 1, max_retries + 1, out, retry_delay), file=sys.stderr)
                time.sleep(retry_delay)
                retries += 1
            elif not ok and retries >= max_retries:
                break
            else:
                break

        if ok and out and do in ("vision", "vision_coords"):
            result_str = (str(out)[:50] + "…") if len(str(out)) > 50 else str(out)
        elif ok:
            result_str = "ok"
        else:
            result_str = "fail: " + ((str(out)[:50] + "…") if out and len(str(out)) > 50 else (str(out) or ""))
        _update_floating_state(plan_path, i + 1, do, "step %d: %s" % (i + 1, do), result_str)
        if not ok:
            print("step %d %s failed: %s" % (i + 1, do, out), file=sys.stderr)
            # 尝试 fallback
            if fallback_plan:
                print("Trying fallback plan...", file=sys.stderr)
                fallback_ok, fallback_msg = _run_fallback_plan(fallback_plan, vars_dict, handlers, max_retry, retry_delay, plan_verbose)
                if fallback_ok:
                    print("Fallback succeeded, continuing main plan", file=sys.stderr)
                    # fallback 成功后继续执行主计划的后续步骤
                    continue
                else:
                    print("Fallback failed: %s" % fallback_msg, file=sys.stderr)
            sys.exit(1)
        if do == "screenshot" and ok and out:
            last_screenshot_plan_path = os.path.normpath(item.get("path") or "")
            last_screenshot_actual_path = out
        if out and do in ("vision", "vision_coords"):
            try:
                os.makedirs(STATE_DIR, exist_ok=True)
                with open(VISION_LAST_OUTPUT, "w", encoding="utf-8") as f:
                    f.write(out)
            except OSError:
                pass
            _safe_print_vision(out)

        # 保存任务状态（每个步骤执行后保存，支持中断恢复）
        if _TASK_STATE_MANAGER_AVAILABLE and plan_path:
            task_state_manager.save_task_state(
                plan_path=plan_path,
                step_index=i + 1,
                step_name=do,
                step_result="ok" if ok else "fail",
                total_steps=total_steps,
                plan_data=plan
            )

    _update_floating_state(plan_path, 0, "done", "plan done", "ok")
    # 推送任务完成状态
    if _TASK_PUSHER_AVAILABLE:
        task_status_pusher.update_task_status(
            task_id, "success",
            "计划执行完成",
            100
        )

    # 清除中断任务状态（任务成功完成）
    if _TASK_STATE_MANAGER_AVAILABLE and plan_path:
        task_state_manager.clear_interrupted_task(plan_path)

    print("plan done")

if __name__ == "__main__":
    main()
