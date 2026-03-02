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
        "model_name": os.environ.get("VISION_MODEL", "qwen3-vl-30b-a3b-instruct"),
    }

def main():
    if len(sys.argv) < 3:
        print("usage: vision_proxy.py <image_path> \"<question>\"", file=sys.stderr)
        sys.exit(1)
    img_path = sys.argv[1]
    question = sys.argv[2]
    if not os.path.isfile(img_path):
        print("File not found:", img_path, file=sys.stderr)
        sys.exit(1)
    cfg = load_config()
    api_key = cfg.get("api_key") or cfg.get("api_key")
    base_url = (cfg.get("base_url") or "").rstrip("/")
    model = cfg.get("model_name") or cfg.get("model", "qwen3-vl-30b-a3b-instruct")
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
