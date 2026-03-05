#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自包含视觉代理：读图 + 问题，调用 OpenAI 兼容的多模态 API，输出回答到 stdout。
配置：同目录或上级的 vision_config.json，或环境变量 VISION_API_KEY / VISION_BASE_URL / VISION_MODEL。
用法: python vision_proxy.py <图片路径> "<问题>"
"""
import sys
import os
import json
import base64
import urllib.request
import urllib.error

def load_config():
    for d in [os.path.dirname(__file__), os.path.join(os.path.dirname(__file__), "..")]:
        p = os.path.join(d, "vision_config.json")
        if os.path.isfile(p):
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    return {
        "api_key": os.environ.get("VISION_API_KEY", ""),
        "base_url": os.environ.get("VISION_BASE_URL", "").rstrip("/"),
        "model_name": os.environ.get("VISION_MODEL", "Qwen2.5-VL-7B-Instruct"),
    }

def _ensure_utf8_stdout():
    """确保 stdout/stderr 以 UTF-8 输出，避免被父进程用 UTF-8 解码时出现乱码（含写入 vision_last_output.txt）。"""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except (OSError, AttributeError):
                pass


def _get_image_size(img_path):
    """返回 (width, height) 或 None。支持 BMP；PNG/JPEG 仅 BMP 可靠用于截图坐标。"""
    try:
        with open(img_path, "rb") as f:
            head = f.read(30)
        if len(head) < 26:
            return None
        if head[:2] == b"BM":
            # BMP: width at 18, height at 22 (4 bytes LE each)
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


def main():
    _ensure_utf8_stdout()
    if len(sys.argv) < 3:
        print("usage: vision_proxy.py <image_path> \"<question>\"", file=sys.stderr)
        sys.exit(1)
    img_path = sys.argv[1]
    question = sys.argv[2]
    if not os.path.isfile(img_path):
        print("File not found:", img_path, file=sys.stderr)
        sys.exit(1)
    # 将图片像素尺寸注入提示，便于多模态返回与屏幕一致的点击坐标（避免 API 缩图导致坐标错位）
    size_hint = ""
    dims = _get_image_size(img_path)
    if dims:
        w, h = dims
        size_hint = f"\n[系统：此图片像素尺寸为 宽{w} 高{h}，与屏幕逻辑分辨率一致。若需返回点击坐标，请在此尺寸下给出整数 x y（仅输出两数、空格分隔），勿使用相对或归一化坐标。]"
    question = question.rstrip() + size_hint
    cfg = load_config()
    api_key = cfg.get("api_key") or ""
    base_url = (cfg.get("base_url") or "").rstrip("/")
    # 优先 Qwen2.5-VL-7B，其次 config，再兜底 qwen3
    model = (
        cfg.get("model_name")
        or cfg.get("model")
        or os.environ.get("VISION_MODEL", "Qwen2.5-VL-7B-Instruct")
    )
    if not api_key or not base_url:
        print("vision_config.json or VISION_API_KEY/VISION_BASE_URL required", file=sys.stderr)
        sys.exit(1)
    with open(img_path, "rb") as f:
        b64 = base64.standard_b64encode(f.read()).decode("ascii")
    ext = os.path.splitext(img_path)[1].lower()
    media_type = "image/bmp" if ext == ".bmp" else "image/png" if ext == ".png" else "image/jpeg"
    body = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {"type": "image_url", "image_url": {"url": f"data:{media_type};base64,{b64}"}},
                ],
            }
        ],
        "max_tokens": 1024,
    }
    # 与你们调用方式一致：支持 extra_body（如 stop_token_ids）
    extra = cfg.get("extra_body") or {}
    if isinstance(extra, dict):
        body.update(extra)
    req = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            out = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(e.read().decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(1)
    text = (out.get("choices") or [{}])[0].get("message", {}).get("content", "")
    print(text)

if __name__ == "__main__":
    main()
