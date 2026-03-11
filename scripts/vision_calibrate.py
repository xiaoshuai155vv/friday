#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vision 坐标校准：在屏幕已知位置画红点 → 截图 → 多模态识别红点坐标 → 计算 vision 与真实坐标的偏移并保存。
后续 run_plan / click_from_vision_or_key 会自动加上该偏移，提高点击准确率。

偏移计算方式：
  - 在 4 个角画红点，真实坐标 expected 已知（如 15%/85% 宽高）。
  - 对同一张截图跑 vision，解析出 4 个 (x,y)，与 expected 用匈牙利算法一对一配对（最小总距离）。
  - 每对得到该点偏移 (dx, dy) = (expected - vision)；最终保存的 offset_x/offset_y 是这 4 个 dx、4 个 dy 的
    「平均值」，即一个全局偏移量，后续所有 vision 点击都会加上这一个 (offset_x, offset_y)。
  - 所以：不是四个点各用一个偏移，而是用「四个点偏移的平均」作为统一偏移。

为何每次校准结果不一样：
  - 多模态模型对同一张图多次调用时输出会波动（非确定性），所以每次解析出的 4 个坐标不同 → 配对与平均
    得到的 offset 就会变。若四个点各自偏移差异很大（见 show），说明模型在不同区域偏差不一致，单次平均
    也不稳定。可用 calibrate [N] 多跑 N 次 vision 取中位数来稳定结果。

用法:
  python vision_calibrate.py calibrate [N]  # 全流程；N=多轮 vision 取中位数，默认 1
  python vision_calibrate.py benchmark [N] # 配置里各多模态模型各跑 N 次，比较偏差稳定性（std 越小越稳）
  python vision_calibrate.py draw           # 步骤1：仅画红点并截图
  python vision_calibrate.py vision         # 步骤2：对已有截图跑多模态
  python vision_calibrate.py compute       # 步骤3：用 vision 输出算偏移并保存
  python vision_calibrate.py show          # 查看当前校准及每点对比（可看四个点偏移是否一致）
  python vision_calibrate.py get-offset    # 输出当前 offset_x offset_y
"""
import sys
import os
import re
import json
import subprocess
from datetime import datetime

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPTS)
STATE_DIR = os.path.join(PROJECT, "runtime", "state")
CALIBRATION_JSON = os.path.join(STATE_DIR, "vision_calibration.json")
CALIBRATION_SCREENSHOT = os.path.join(STATE_DIR, "calibration_capture.bmp")
CALIBRATION_VISION_OUTPUT = os.path.join(STATE_DIR, "calibration_vision_output.txt")
_SUBPROCESS_ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}
CALIBRATION_QUESTION = "图中是电脑桌面，有且仅有 4 个红色圆形标记（左上、右上、左下、右下四个角）。必须输出 4 行，每行一个 x 空格 y，按从左到右、从上到下顺序。"


def _get_screen_size():
    if sys.platform != "win32":
        return None, None
    try:
        u = __import__("ctypes").windll.user32
        return u.GetSystemMetrics(0), u.GetSystemMetrics(1)
    except Exception:
        return None, None


def _default_calibration_points(w, h):
    """4 个角点：左上、右上、左下、右下（不含中心，避免多模态漏掉中心导致错配）。"""
    return [
        (int(0.15 * w), int(0.15 * h)),
        (int(0.85 * w), int(0.15 * h)),
        (int(0.15 * w), int(0.85 * h)),
        (int(0.85 * w), int(0.85 * h)),
    ]


def _draw_markers(points, hold_sec=1.5, screenshot_path=None):
    """先在屏幕上显示红点（可目视确认），再截图、再关窗。截图在位图上画红点保存，保证 bmp 里一定有红点。"""
    if not screenshot_path:
        return False
    try:
        import tkinter as tk
        import time
    except ImportError:
        # 无 tkinter 时仅截屏并在位图上画红点
        return _screenshot_inline(screenshot_path, draw_points=points)
    root = tk.Tk()
    root.withdraw()
    size = 36
    half = size // 2
    windows = []
    for (px, py) in points:
        win = tk.Toplevel(root)
        win.overrideredirect(1)
        win.attributes("-topmost", 1)
        win.geometry("%dx%d+%d+%d" % (size, size, max(0, px - half), max(0, py - half)))
        win.configure(bg="red")
        canvas = tk.Canvas(win, width=size, height=size, bg="red", highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        canvas.create_oval(2, 2, size - 2, size - 2, fill="red", outline="darkred", width=2)
        windows.append(win)
    root.update()
    root.update_idletasks()
    time.sleep(hold_sec)
    root.update()
    # 红点仍在屏幕上时截图；在位图上画红点保存，不依赖窗口是否被 BitBlt 截到
    ok = _screenshot_inline(screenshot_path, draw_points=points)
    for w in windows:
        try:
            w.destroy()
        except Exception:
            pass
    try:
        root.destroy()
    except Exception:
        pass
    return ok


def _screenshot(path):
    r = subprocess.run(
        [sys.executable, os.path.join(SCRIPTS, "screenshot_tool.py"), path],
        cwd=PROJECT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=_SUBPROCESS_ENV,
        timeout=15,
    )
    return r.returncode == 0


def _screenshot_inline(path, draw_points=None):
    """在同进程内用 ctypes 截全屏并保存 BMP。若 draw_points=[(x,y),...] 则在位图上直接画红点再保存，不依赖 tkinter 窗口是否被截到。"""
    if sys.platform != "win32":
        return False
    try:
        import ctypes
        from ctypes import wintypes
        u = ctypes.windll.user32
        g = ctypes.windll.gdi32
        w = u.GetSystemMetrics(0)
        h = u.GetSystemMetrics(1)
        hdc = u.GetDC(0)
        memdc = g.CreateCompatibleDC(hdc)
        bmp = g.CreateCompatibleBitmap(hdc, w, h)
        g.SelectObject(memdc, bmp)
        g.BitBlt(memdc, 0, 0, w, h, hdc, 0, 0, 0x00CC0020)
        u.ReleaseDC(0, hdc)
        # 在位图上直接画红点（不依赖窗口是否出现在截屏里）
        if draw_points:
            red = g.CreateSolidBrush(0x0000FF)  # BGR 红
            old_br = g.SelectObject(memdc, red)
            for (px, py) in draw_points:
                r = 18
                g.Ellipse(memdc, px - r, py - r, px + r, py + r)
            g.SelectObject(memdc, old_br)
            g.DeleteObject(red)
        class BITMAPFILEHEADER(ctypes.Structure):
            _fields_ = [("bfType", wintypes.WORD), ("bfSize", wintypes.DWORD), ("bfReserved1", wintypes.WORD),
                        ("bfReserved2", wintypes.WORD), ("bfOffBits", wintypes.DWORD)]
        class BITMAPINFOHEADER(ctypes.Structure):
            _fields_ = [("biSize", wintypes.DWORD), ("biWidth", wintypes.LONG), ("biHeight", wintypes.LONG),
                        ("biPlanes", wintypes.WORD), ("biBitCount", wintypes.WORD), ("biCompression", wintypes.DWORD),
                        ("biSizeImage", wintypes.DWORD), ("biXPelsPerMeter", wintypes.LONG), ("biYPelsPerMeter", wintypes.LONG),
                        ("biClrUsed", wintypes.DWORD), ("biClrImportant", wintypes.DWORD)]
        bmi = BITMAPINFOHEADER()
        bmi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.biWidth, bmi.biHeight = w, -h
        bmi.biPlanes, bmi.biBitCount = 1, 24
        row = (w * 3 + 3) // 4 * 4
        size = row * h
        buf = (ctypes.c_ubyte * size)()
        g.GetDIBits(memdc, bmp, 0, h, ctypes.byref(buf), ctypes.byref(bmi), 0)
        g.DeleteObject(bmp)
        g.DeleteDC(memdc)
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "wb") as f:
            f.write(b"BM")
            f.write((14 + 40 + size).to_bytes(4, "little"))
            f.write((0).to_bytes(2, "little"))
            f.write((0).to_bytes(2, "little"))
            f.write((14 + 40).to_bytes(4, "little"))
            f.write(bytes(bmi))
            f.write(bytes(buf))
        return True
    except Exception as e:
        import traceback
        print("_screenshot_inline failed:", e, file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return False


def _run_vision(img_path, question, model_override=None, provider_override=None):
    cmd = [sys.executable, os.path.join(SCRIPTS, "vision_proxy.py")]
    if provider_override:
        cmd.extend(["--provider", str(provider_override)])
    if model_override:
        cmd.extend(["--model", str(model_override)])
    cmd.extend([img_path, question])
    r = subprocess.run(
        cmd,
        cwd=PROJECT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=_SUBPROCESS_ENV,
        timeout=90,
    )
    if r.returncode != 0:
        return None
    return (r.stdout or "").strip()


def _parse_xy_pairs(text, max_points=10):
    """解析多组 x y，返回 [(x,y), ...]，按 (y,x) 排序（从上到下、从左到右）。"""
    candidates = []
    for m in re.finditer(r"(\d+)\s+(\d+)", text):
        x, y = int(m.group(1)), int(m.group(2))
        if 0 <= x <= 5000 and 0 <= y <= 3000:
            candidates.append((x, y))
    for m in re.finditer(r"(\d+)\s*[,，]\s*(\d+)", text):
        x, y = int(m.group(1)), int(m.group(2))
        if 0 <= x <= 5000 and 0 <= y <= 3000:
            candidates.append((x, y))
    if len(candidates) > max_points:
        candidates = candidates[:max_points]
    if not candidates:
        return []
    # 去重并保持顺序；再按 (y, x) 排序与 expected 一致
    seen = set()
    unique = []
    for p in candidates:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    unique.sort(key=lambda p: (p[1], p[0]))
    return unique


def _hungarian_pairing(expected_list, vision_list):
    """最小总距离的一对一配对。优先用 scipy.optimize.linear_sum_assignment，否则贪心。"""
    try:
        from scipy.optimize import linear_sum_assignment
        import numpy as np
        cost = np.zeros((len(expected_list), len(vision_list)))
        for i, (ex, ey) in enumerate(expected_list):
            for j, (vx, vy) in enumerate(vision_list):
                cost[i, j] = (ex - vx) ** 2 + (ey - vy) ** 2
        row_ind, col_ind = linear_sum_assignment(cost)
        pairs = []
        for i, j in zip(row_ind, col_ind):
            ex, ey = expected_list[i]
            vx, vy = vision_list[j]
            pairs.append((ex, ey, vx, vy))
        return pairs
    except Exception:
        return None


def _compute_offset(expected_list, vision_list):
    """一对一配对（优先匈牙利最小总距离），再逐对求 offset 取平均。vision 少于 expected 时按每个 vision 找最近未配对的 expected。"""
    if not expected_list or not vision_list:
        return None, None, []
    n = min(len(expected_list), len(vision_list))
    # 点数相等时用匈牙利最优配对，避免“顺序错位”导致错配（如中心点被当成别的点）
    if len(expected_list) == len(vision_list) and n >= 3:
        pairs = _hungarian_pairing(expected_list, vision_list)
        if pairs:
            samples = []
            dx_sum = dy_sum = 0
            for (ex, ey, vx, vy) in pairs:
                dx, dy = ex - vx, ey - vy
                samples.append({"expected": [ex, ey], "vision": [vx, vy], "offset": [dx, dy]})
                dx_sum += dx
                dy_sum += dy
            k = len(samples)
            return round(dx_sum / k), round(dy_sum / k), samples
    # 一对一配对：若 vision 更少，则每个 vision 找最近未配对的 expected；否则每个 expected 找最近未配对的 vision
    if len(vision_list) < len(expected_list):
        used_e = set()
        pairs = []
        for (vx, vy) in vision_list:
            best_e, best_d = None, float("inf")
            for i, (ex, ey) in enumerate(expected_list):
                if i in used_e:
                    continue
                d = (ex - vx) ** 2 + (ey - vy) ** 2
                if d < best_d:
                    best_d, best_e = d, i
            if best_e is not None:
                used_e.add(best_e)
                ex, ey = expected_list[best_e]
                pairs.append((ex, ey, vx, vy))
    else:
        used = set()
        pairs = []
        for (ex, ey) in expected_list[:n]:
            best_v, best_d = None, float("inf")
            for j, (vx, vy) in enumerate(vision_list):
                if j in used:
                    continue
                d = (ex - vx) ** 2 + (ey - vy) ** 2
                if d < best_d:
                    best_d, best_v = d, j
            if best_v is not None:
                used.add(best_v)
                vx, vy = vision_list[best_v]
                pairs.append((ex, ey, vx, vy))
    if not pairs:
        return None, None, []
    samples = []
    dx_sum = dy_sum = 0
    for (ex, ey, vx, vy) in pairs:
        dx, dy = ex - vx, ey - vy
        samples.append({"expected": [ex, ey], "vision": [vx, vy], "offset": [dx, dy]})
        dx_sum += dx
        dy_sum += dy
    k = len(samples)
    return round(dx_sum / k), round(dy_sum / k), samples


def _median(values):
    """取中位数，不依赖 numpy。"""
    if not values:
        return None
    s = sorted(values)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) // 2


def _std(values):
    """样本标准差。"""
    if not values or len(values) < 2:
        return 0.0
    m = sum(values) / len(values)
    return (sum((x - m) ** 2 for x in values) / len(values)) ** 0.5


def _load_vision_providers():
    """
    从 vision_config.json 读取所有要测的 provider+model。
    新结构：顶层 qwen/glm/... 各块 { base_url, api_key, model_name } → [(provider, model_name), ...]。
    旧结构：单 model → [(None, model)]。
    """
    path = os.path.join(SCRIPTS, "vision_config.json")
    if not os.path.isfile(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        out = []
        for key, val in cfg.items():
            if key == "provider":
                continue
            if isinstance(val, dict) and val.get("base_url") and val.get("model_name"):
                out.append((key, str(val.get("model_name", "")).strip()))
        if out:
            return out
        m = cfg.get("model")
        if m:
            return [(None, str(m).strip())]
    except Exception:
        pass
    return []


def cmd_benchmark(runs=10):
    """对配置里每个多模态模型在同一截图上各跑 N 次，比较稳定性（偏差波动越小越好）。"""
    w, h = _get_screen_size()
    if not w or not h:
        print("get screen size failed", file=sys.stderr)
        return 1
    points = _default_calibration_points(w, h)
    expected_sorted = sorted(points, key=lambda p: (p[1], p[0]))
    os.makedirs(STATE_DIR, exist_ok=True)

    providers = _load_vision_providers()
    if not providers:
        providers = [(None, None)]  # 用 config 默认

    print("Drawing red markers once, then each provider runs vision %d times..." % runs, file=sys.stderr)
    if not _draw_markers(points, hold_sec=1.5, screenshot_path=CALIBRATION_SCREENSHOT):
        print("draw failed", file=sys.stderr)
        return 1

    runs = max(1, int(runs))
    rows = []  # (model, mean_x, mean_y, std_x, std_y, ok_count)

    total_providers = len(providers)
    for pidx, (provider, model) in enumerate(providers):
        label = "%s/%s" % (provider or "default", model or "-") if provider or model else "(default)"
        print("  [%d/%d] %s ..." % (pidx + 1, total_providers, label), file=sys.stderr)
        ox_list, oy_list = [], []
        for i in range(runs):
            print("    run %d/%d" % (i + 1, runs), file=sys.stderr, end=" ", flush=True)
            out = _run_vision(
                CALIBRATION_SCREENSHOT,
                CALIBRATION_QUESTION,
                model_override=model,
                provider_override=provider,
            )
            if not out:
                print("fail", file=sys.stderr)
                continue
            vision_list = _parse_xy_pairs(out, max_points=10)
            if len(vision_list) < len(expected_sorted):
                print("fail", file=sys.stderr)
                continue
            vision_sorted = vision_list[: len(expected_sorted)]
            ox, oy, _ = _compute_offset(expected_sorted, vision_sorted)
            if ox is None:
                print("fail", file=sys.stderr)
                continue
            ox_list.append(ox)
            oy_list.append(oy)
            print("ok", file=sys.stderr)
        if not ox_list:
            print("  -> 0 ok, skip", file=sys.stderr)
            rows.append((label, None, None, None, None, 0))
            continue
        print("  -> %d/%d ok" % (len(ox_list), runs), file=sys.stderr)
        mx, my = sum(ox_list) / len(ox_list), sum(oy_list) / len(oy_list)
        sx, sy = _std(ox_list), _std(oy_list)
        rows.append((label, mx, my, sx, sy, len(ox_list)))

    # 按稳定性排序：std_x + std_y 越小越稳定
    rows.sort(key=lambda r: (r[3] or 9999) + (r[4] or 9999))

    print("\n=== 多模态模型偏差稳定性（同一截图各跑 %d 次，std 越小越稳定）===" % runs, file=sys.stderr)
    print("%-28s %6s %6s %8s %8s %s" % ("model", "mean_x", "mean_y", "std_x", "std_y", "ok"), file=sys.stderr)
    print("-" * 62, file=sys.stderr)
    for r in rows:
        label, mx, my, sx, sy, ok = r
        if mx is None:
            print("%-28s %6s %6s %8s %8s %s" % (label, "-", "-", "-", "-", "0"), file=sys.stderr)
        else:
            print("%-28s %6.0f %6.0f %8.1f %8.1f %d" % (label, mx, my, sx, sy, ok), file=sys.stderr)
    if rows and rows[0][3] is not None:
        best = rows[0][0]
        print("Most stable (lowest std): %s" % best, file=sys.stderr)
    return 0


def cmd_calibrate(runs=1):
    w, h = _get_screen_size()
    if not w or not h:
        print("get screen size failed", file=sys.stderr)
        return 1
    points = _default_calibration_points(w, h)
    expected_sorted = sorted(points, key=lambda p: (p[1], p[0]))
    os.makedirs(STATE_DIR, exist_ok=True)

    print("Drawing %d red markers (screenshot while visible)..." % len(points), file=sys.stderr)
    if not _draw_markers(points, hold_sec=1.5, screenshot_path=CALIBRATION_SCREENSHOT):
        print("draw failed", file=sys.stderr)
        return 1

    runs = max(1, int(runs))
    results = []  # [(offset_x, offset_y, samples), ...]

    for run in range(runs):
        if runs > 1:
            print("Running vision (run %d/%d)..." % (run + 1, runs), file=sys.stderr)
        else:
            print("Running vision...", file=sys.stderr)
        out = _run_vision(CALIBRATION_SCREENSHOT, CALIBRATION_QUESTION)
        if not out:
            print("vision failed or no output", file=sys.stderr)
            return 1
        vision_list = _parse_xy_pairs(out, max_points=10)
        if len(vision_list) < len(expected_sorted):
            print("vision returned %d points, expected %d. raw:\n%s" % (len(vision_list), len(expected_sorted), out[:500]), file=sys.stderr)
            return 1
        vision_sorted = vision_list[: len(expected_sorted)]
        ox, oy, samples = _compute_offset(expected_sorted, vision_sorted)
        if ox is None:
            print("compute offset failed", file=sys.stderr)
            return 1
        results.append((ox, oy, samples))

    if runs > 1:
        offset_x = _median([r[0] for r in results])
        offset_y = _median([r[1] for r in results])
        # 取与中位数最接近的一轮的 samples 保存，便于 show 查看
        _, _, samples = min(results, key=lambda r: (r[0] - offset_x) ** 2 + (r[1] - offset_y) ** 2)
        print("Used median of %d runs: offset_x=%d offset_y=%d" % (runs, offset_x, offset_y), file=sys.stderr)
    else:
        offset_x, offset_y, samples = results[0]

    # 打印四个点各自偏移的范围，便于判断是否稳定
    dxs = [s["offset"][0] for s in samples]
    dys = [s["offset"][1] for s in samples]
    print("Per-point offset range: dx [%d, %d]  dy [%d, %d]" % (min(dxs), max(dxs), min(dys), max(dys)), file=sys.stderr)

    data = {
        "offset_x": offset_x,
        "offset_y": offset_y,
        "screen_w": w,
        "screen_h": h,
        "samples": samples,
        "updated_at": datetime.now().isoformat(),
    }
    with open(CALIBRATION_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Calibration saved: offset_x=%d offset_y=%d (screen %dx%d)" % (offset_x, offset_y, w, h), file=sys.stderr)
    print("%d %d" % (offset_x, offset_y))
    return 0


def cmd_draw():
    """仅画点并截图（红点显示时截图，图中会有红点），不调 vision。用于手动核对。"""
    w, h = _get_screen_size()
    if not w or not h:
        print("get screen size failed", file=sys.stderr)
        return 1
    points = _default_calibration_points(w, h)
    os.makedirs(STATE_DIR, exist_ok=True)
    ok = _draw_markers(points, hold_sec=2, screenshot_path=CALIBRATION_SCREENSHOT)
    print("Screenshot: %s" % (CALIBRATION_SCREENSHOT if ok and os.path.isfile(CALIBRATION_SCREENSHOT) else "failed"), file=sys.stderr)
    return 0 if ok else 1


def cmd_vision():
    """对 runtime/state/calibration_capture.bmp 跑多模态，打印原始输出与解析出的坐标，并写入 runtime/state/calibration_vision_output.txt 供 compute 使用。"""
    if not os.path.isfile(CALIBRATION_SCREENSHOT):
        print("No screenshot. Run 'draw' first: %s" % CALIBRATION_SCREENSHOT, file=sys.stderr)
        return 1
    print("Question: %s" % CALIBRATION_QUESTION, file=sys.stderr)
    print("Running vision...", file=sys.stderr)
    out = _run_vision(CALIBRATION_SCREENSHOT, CALIBRATION_QUESTION)
    if not out:
        print("vision failed or no output", file=sys.stderr)
        return 1
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(CALIBRATION_VISION_OUTPUT, "w", encoding="utf-8") as f:
        f.write(out)
    print("--- Vision 原始输出 ---", file=sys.stderr)
    print(out, file=sys.stderr)
    print("--- 解析出的坐标 (x y) ---", file=sys.stderr)
    pts = _parse_xy_pairs(out, max_points=10)
    for i, (x, y) in enumerate(pts, 1):
        print("  %d: %d %d" % (i, x, y), file=sys.stderr)
    print("Saved to %s (for 'compute')" % CALIBRATION_VISION_OUTPUT, file=sys.stderr)
    return 0


def cmd_compute():
    """用当前屏幕的 5 个预期点 + runtime/state/calibration_vision_output.txt 算偏移并保存。需先执行 draw 再 vision。"""
    w, h = _get_screen_size()
    if not w or not h:
        print("get screen size failed", file=sys.stderr)
        return 1
    if not os.path.isfile(CALIBRATION_VISION_OUTPUT):
        print("No vision output. Run 'vision' first: %s" % CALIBRATION_VISION_OUTPUT, file=sys.stderr)
        return 1
    with open(CALIBRATION_VISION_OUTPUT, "r", encoding="utf-8") as f:
        out = f.read()
    expected_sorted = sorted(_default_calibration_points(w, h), key=lambda p: (p[1], p[0]))
    vision_list = _parse_xy_pairs(out, max_points=10)
    if len(vision_list) < 2:
        print("vision returned %d points, need at least 2. Run 'vision' again." % len(vision_list), file=sys.stderr)
        return 1
    if len(vision_list) < len(expected_sorted):
        print("vision returned %d points (expected 5), will use %d pairs." % (len(vision_list), len(vision_list)), file=sys.stderr)
    offset_x, offset_y, samples = _compute_offset(expected_sorted, vision_list)
    if offset_x is None:
        print("compute offset failed", file=sys.stderr)
        return 1
    data = {
        "offset_x": offset_x,
        "offset_y": offset_y,
        "screen_w": w,
        "screen_h": h,
        "samples": samples,
        "updated_at": datetime.now().isoformat(),
    }
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(CALIBRATION_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Calibration saved: offset_x=%d offset_y=%d (screen %dx%d)" % (offset_x, offset_y, w, h), file=sys.stderr)
    print("%d %d" % (offset_x, offset_y))
    return 0


def cmd_show():
    """查看 runtime/state/vision_calibration.json：分辨率、总偏移、每点「真实坐标 / vision 返回 / 该点偏移」。"""
    if not os.path.isfile(CALIBRATION_JSON):
        print("No calibration yet. Run 'calibrate' or draw→vision→compute.", file=sys.stderr)
        return 1
    with open(CALIBRATION_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    print("屏幕: %d x %d" % (data.get("screen_w", 0), data.get("screen_h", 0)), file=sys.stderr)
    print("总偏移: offset_x=%s  offset_y=%s" % (data.get("offset_x"), data.get("offset_y")), file=sys.stderr)
    print("更新时间: %s" % data.get("updated_at", ""), file=sys.stderr)
    print("--- 每点对比（真实坐标 / vision 返回 / 该点偏移）---", file=sys.stderr)
    for i, s in enumerate(data.get("samples", []), 1):
        e = s.get("expected", [0, 0])
        v = s.get("vision", [0, 0])
        o = s.get("offset", [0, 0])
        print("  %d: 真实 (%s,%s)  vision (%s,%s)  偏移 (+%s,+%s)" % (i, e[0], e[1], v[0], v[1], o[0], o[1]), file=sys.stderr)
    print("--- 完整 JSON 见 runtime/state/vision_calibration.json ---", file=sys.stderr)
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


def cmd_get_offset():
    from vision_calibration_helper import get_calibration_offset
    ox, oy = get_calibration_offset()  # 仅读取，不触发自动校准
    print("%d %d" % (ox, oy))
    return 0


def main():
    if len(sys.argv) < 2:
        print("usage: vision_calibrate.py calibrate [N] | draw | vision | compute | show | get-offset", file=sys.stderr)
        return 1
    cmd = sys.argv[1].lower()
    if cmd == "calibrate":
        runs = 1
        if len(sys.argv) > 2:
            try:
                runs = int(sys.argv[2])
            except ValueError:
                pass
        return cmd_calibrate(runs)
    if cmd == "benchmark":
        runs = 10
        if len(sys.argv) > 2:
            try:
                runs = int(sys.argv[2])
            except ValueError:
                pass
        return cmd_benchmark(runs)
    if cmd == "draw":
        return cmd_draw()
    if cmd == "vision":
        return cmd_vision()
    if cmd == "compute":
        return cmd_compute()
    if cmd == "show":
        return cmd_show()
    if cmd == "get-offset":
        return cmd_get_offset()
    print("unknown command: %s" % sys.argv[1], file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
