#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自拍：直接启动 camera_qt，等几秒后截屏保存到 screenshots/selfie_YYYYMMDD_HHMMSS.bmp"""
import os
import sys
import subprocess
import time
from datetime import datetime

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPTS)
OUT_DIR = os.path.join(PROJECT, "screenshots")
CAMERA_QT = os.path.join(SCRIPTS, "camera_qt.py")

WAIT_CAMERA_READY = 4.0   # 摄像头窗口启动后等待画面就绪
CLOSE_AFTER = 10         # 截图后窗口再保留 N 秒自动关闭

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    if not os.path.isfile(CAMERA_QT):
        print("camera_qt.py not found", file=sys.stderr)
        sys.exit(1)
    # 用「调用者 Python」运行 camera_qt（run_with_env 会传 FRIDAY_INVOKER_PYTHON，即用户执行的 python）
    interp = os.environ.get("FRIDAY_INVOKER_PYTHON") or sys.executable
    p = subprocess.Popen(
        [interp, CAMERA_QT, "--close-after", str(CLOSE_AFTER)],
        cwd=PROJECT,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    time.sleep(WAIT_CAMERA_READY)
    if p.poll() is not None:
        err = (p.stderr.read() or "").strip() if p.stderr else ""
        if err:
            print(err, file=sys.stderr)
        print("提示：若本机 python scripts/camera_qt.py 可正常启动，请直接用 python scripts/selfie.py（不用 run_with_env）", file=sys.stderr)
        sys.exit(1)
    out = os.path.join(OUT_DIR, "selfie_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".bmp")
    r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "screenshot_tool.py"), out], cwd=PROJECT)
    if r.returncode == 0:
        print(out)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
