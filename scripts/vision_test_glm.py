#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试当前 vision 配置（默认 GLM）：调用 vision_proxy 一次，将 stdout/stderr 写入 state 便于查看。
用法: python vision_test_glm.py [图片路径] [问题]
      无参数时用 runtime/screenshots/ihaier_my_latest.bmp 和简单问题；失败时查看 runtime/state/vision_last_error.txt
"""
import sys
import os
import subprocess

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPTS)
STATE_DIR = os.path.join(PROJECT, "runtime", "state")
OUT_FILE = os.path.join(STATE_DIR, "vision_test_stdout.txt")
ERR_FILE = os.path.join(STATE_DIR, "vision_test_stderr.txt")

def main():
    img = sys.argv[1] if len(sys.argv) >= 2 else os.path.join(PROJECT, "runtime", "screenshots", "ihaier_my_latest.bmp")
    q = sys.argv[2] if len(sys.argv) >= 3 else "描述图中内容，一两句即可。"
    if not os.path.isfile(img):
        print("Image not found:", img, file=sys.stderr)
        print("Usage: vision_test_glm.py [image_path] [question]", file=sys.stderr)
        sys.exit(1)
    os.makedirs(STATE_DIR, exist_ok=True)
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    r = subprocess.run(
        [sys.executable, os.path.join(SCRIPTS, "vision_proxy.py"), img, q],
        cwd=PROJECT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(r.stdout or "")
    with open(ERR_FILE, "w", encoding="utf-8") as f:
        f.write(r.stderr or "")
    print("stdout ->", OUT_FILE)
    print("stderr ->", ERR_FILE)
    if r.returncode != 0:
        print("Exit code:", r.returncode)
        if os.path.isfile(os.path.join(STATE_DIR, "vision_last_error.txt")):
            print("API error detail -> runtime/state/vision_last_error.txt")
    sys.exit(r.returncode)

if __name__ == "__main__":
    main()
