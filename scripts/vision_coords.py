#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取坐标的多模态脚本：对同一张图多次调用 vision_proxy，解析 (x,y) 取中位数输出。
用于需要点击坐标的场景（如 run_plan 中 coords: true），提高坐标稳定性。
用法: python vision_coords.py <图片路径> "<问题>" [--runs 3]
输出: 仅 stdout 一行 "x y"，失败则输出空或原始文本。
"""
import sys
import os
import re
import subprocess

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPTS)
_SUBPROCESS_ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}


def _get_image_size(img_path):
    """返回 (width, height) 或 None。支持 BMP、PNG。"""
    try:
        with open(img_path, "rb") as f:
            head = f.read(30)
        if len(head) < 26:
            return None
        if head[:2] == b"BM":
            w = int.from_bytes(head[18:22], "little")
            h = int.from_bytes(head[22:26], "little")
            if h < 0:
                h = -h
            return (w, h)
        if head[:8] == b"\x89PNG\r\n\x1a\n" and len(head) >= 24:
            w = int.from_bytes(head[16:20], "big")
            h = int.from_bytes(head[20:24], "big")
            return (w, h)
    except (OSError, ValueError):
        pass
    return None


def _parse_xy(text):
    """从文本解析单个 (x,y)，多候选时取 x 最小的（如左侧列表项）。"""
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


def _parse_normalized_xy(text):
    """解析归一化坐标 (0-1)，返回 (nx, ny) 或 None。支持 0.5 0.5、.5 .5、1.0 0 等格式。"""
    if not text or not text.strip():
        return None
    candidates = []
    for m in re.finditer(r"(\d*\.?\d+)\s+(\d*\.?\d+)", text):
        try:
            nx, ny = float(m.group(1)), float(m.group(2))
            if 0 <= nx <= 1 and 0 <= ny <= 1:
                candidates.append((nx, ny))
        except ValueError:
            pass
    for m in re.finditer(r"(\d*\.?\d+)\s*[,，]\s*(\d*\.?\d+)", text):
        try:
            nx, ny = float(m.group(1)), float(m.group(2))
            if 0 <= nx <= 1 and 0 <= ny <= 1:
                candidates.append((nx, ny))
        except ValueError:
            pass
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    return min(candidates, key=lambda p: p[0])


def _median(vals):
    if not vals:
        return None
    s = sorted(vals)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) // 2


def main():
    runs = 3
    use_normalized = False
    extra_args = []  # --provider / --model / --verbose 透传给 vision_proxy
    args = sys.argv[1:]
    while len(args) >= 2 and args[0].startswith("--"):
        if args[0] == "--runs":
            try:
                runs = max(1, min(10, int(args[1])))
            except (ValueError, IndexError):
                runs = 3
            args = args[2:]
        elif args[0] == "--normalized":
            use_normalized = True
            args = args[1:]
        elif args[0] in ("--provider", "--model") and len(args) >= 2:
            extra_args.extend(args[:2])
            args = args[2:]
        elif args[0] == "--verbose":
            extra_args.extend(["--verbose"])
            args = args[1:]
        else:
            break
    if os.environ.get("FRIDAY_VISION_VERBOSE", "").lower() in ("1", "true", "yes"):
        extra_args.append("--verbose")
    if len(args) < 2:
        print("usage: vision_coords.py [--runs 3] [--normalized] [--verbose] [--provider qwen|glm] [--model MODEL] <image_path> \"<question>\"", file=sys.stderr)
        sys.exit(1)
    img_path = args[0]
    question = args[1]
    if not os.path.isfile(img_path):
        print("File not found:", img_path, file=sys.stderr)
        sys.exit(1)

    vision_proxy = os.path.join(SCRIPTS, "vision_proxy.py")
    coords_list = []
    last_text = ""

    if use_normalized:
        extra_args.append("--normalized")
    dims = _get_image_size(img_path) if use_normalized else None
    if use_normalized and not dims:
        print("vision_coords: --normalized 需要图片尺寸，当前无法解析，回退到像素坐标解析", file=sys.stderr)

    for i in range(runs):
        if runs > 1:
            print("vision_coords run %d/%d" % (i + 1, runs), file=sys.stderr)
        cmd = [sys.executable, vision_proxy] + extra_args + [img_path, question]
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
        if r.stderr:
            print(r.stderr, file=sys.stderr, end="")
        if r.returncode != 0:
            print("vision_proxy failed (run %d)" % (i + 1), file=sys.stderr)
            sys.exit(1)
        text = (r.stdout or "").strip()
        last_text = text
        parsed = None
        if use_normalized and dims:
            norm = _parse_normalized_xy(text)
            if norm:
                px = int(norm[0] * dims[0])
                py = int(norm[1] * dims[1])
                parsed = (px, py)
                if runs > 1:
                    print("  normalized %s -> (%d, %d)" % (norm, px, py), file=sys.stderr)
        if not parsed:
            parsed = _parse_xy(text)
        if parsed:
            coords_list.append(parsed)

    if coords_list:
        mx = _median([p[0] for p in coords_list])
        my = _median([p[1] for p in coords_list])
        if runs > 1:
            print("vision_coords median of %d runs: (%d, %d)" % (len(coords_list), mx, my), file=sys.stderr)
        print("%d %d" % (mx, my))
    else:
        if runs > 1:
            print("vision_coords: no coords parsed from %d runs, output raw" % runs, file=sys.stderr)
        print(last_text or "")


if __name__ == "__main__":
    main()
