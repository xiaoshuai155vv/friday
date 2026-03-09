#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""供 run_plan、click_from_vision_or_key 等读取 vision 校准偏移；不存在则自动校准一次。"""
import os
import json
import subprocess
import sys

_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
_PROJECT = os.path.dirname(_SCRIPTS)
_STATE_DIR = os.path.join(_PROJECT, "state")
_CALIBRATION_JSON = os.path.join(_STATE_DIR, "vision_calibration.json")


def get_screen_size():
    try:
        import ctypes
        u = ctypes.windll.user32
        return u.GetSystemMetrics(0), u.GetSystemMetrics(1)
    except Exception:
        return None, None


def has_calibration_for_current_resolution():
    """当前分辨率下是否已有校准数据。"""
    cw, ch = get_screen_size()
    if not cw or not ch:
        return False
    if not os.path.isfile(_CALIBRATION_JSON):
        return False
    try:
        with open(_CALIBRATION_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return False
    return (data.get("screen_w"), data.get("screen_h")) == (cw, ch)


def _use_calibration():
    """是否启用校准。默认不启用，设 FRIDAY_USE_VISION_CALIBRATION=1 启用。"""
    return os.environ.get("FRIDAY_USE_VISION_CALIBRATION", "").lower() in ("1", "true", "yes")


def get_calibration_offset():
    """若存在校准且分辨率与当前屏一致，返回 (offset_x, offset_y)，否则 (0, 0)。未启用校准则返回 (0, 0)。"""
    if not _use_calibration():
        return 0, 0
    if not has_calibration_for_current_resolution():
        return 0, 0
    try:
        with open(_CALIBRATION_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return 0, 0
    return int(data.get("offset_x", 0)), int(data.get("offset_y", 0))


def ensure_calibration():
    """若当前分辨率无校准数据则自动跑一次 calibrate，再返回 (offset_x, offset_y)。未启用校准则返回 (0, 0)。"""
    if not _use_calibration():
        return 0, 0
    if has_calibration_for_current_resolution():
        return get_calibration_offset()
    os.makedirs(_STATE_DIR, exist_ok=True)
    try:
        subprocess.run(
            [sys.executable, os.path.join(_SCRIPTS, "vision_calibrate.py"), "calibrate"],
            cwd=_PROJECT,
            capture_output=True,
            timeout=120,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
    except Exception:
        pass
    return get_calibration_offset()
