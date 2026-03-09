#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自包含视觉代理：读图 + 问题，调用 OpenAI 兼容的多模态 API，输出回答到 stdout。
配置：同目录或上级的 vision_config.json，或环境变量 VISION_API_KEY / VISION_BASE_URL / VISION_MODEL。
用法: python vision_proxy.py [--provider qwen|glm] [--model MODEL] <图片路径> "<问题>"
注：需要获取点击坐标时，请用 vision_coords.py（内部多轮取中位数，输出 x y）。
"""
import sys
import os
import re
import json
import base64
import urllib.request
import urllib.error
import ctypes

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPTS)
STATE_DIR = os.path.join(PROJECT, "state")
VISION_LAST_ERROR = os.path.join(STATE_DIR, "vision_last_error.txt")

def load_config():
    for d in [os.path.dirname(__file__), os.path.join(os.path.dirname(__file__), "..")]:
        p = os.path.join(d, "vision_config.json")
        if os.path.isfile(p):
            with open(p, "r", encoding="utf-8") as f:
                raw = json.load(f)
            # 多后端：若存在 "provider"（如 "glm" / "qwen"）且对应块存在，则用该块覆盖
            provider = raw.get("provider")
            if provider and isinstance(raw.get(provider), dict):
                block = raw[provider]
                return { **raw, **block }
            return raw
    return {
        "api_key": os.environ.get("VISION_API_KEY", ""),
        "base_url": os.environ.get("VISION_BASE_URL", "").rstrip("/"),
        "model_name": os.environ.get("VISION_MODEL", "qwen3-vl-30b-a3b-instruct"),
    }

def _ensure_utf8_stdout():
    """确保 stdout/stderr 以 UTF-8 输出，避免被父进程用 UTF-8 解码时出现乱码（含写入 vision_last_output.txt）。"""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except (OSError, AttributeError):
                pass


def _get_screen_size():
    """返回当前主屏逻辑分辨率 (width, height)，与截图/鼠标坐标一致。非 Windows 返回 None。"""
    if sys.platform != "win32":
        return None
    try:
        u = ctypes.windll.user32
        return (u.GetSystemMetrics(0), u.GetSystemMetrics(1))
    except Exception:
        return None


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
    provider_override = None
    model_override = None
    use_normalized = False
    verbose = os.environ.get("FRIDAY_VISION_VERBOSE", "").lower() in ("1", "true", "yes")
    args = sys.argv[1:]
    while len(args) >= 2 and args[0].startswith("--"):
        if args[0] == "--provider":
            provider_override = args[1]
            args = args[2:]
        elif args[0] == "--model":
            model_override = args[1]
            args = args[2:]
        elif args[0] == "--verbose":
            verbose = True
            args = args[1:]
        elif args[0] == "--normalized":
            use_normalized = True
            args = args[1:]
        else:
            break
    if len(args) < 2:
        print("usage: vision_proxy.py [--provider qwen|glm] [--model MODEL] [--verbose] [--normalized] <image_path> \"<question>\"", file=sys.stderr)
        sys.exit(1)
    img_path = args[0]
    question = args[1]
    if not os.path.isfile(img_path):
        print("File not found:", img_path, file=sys.stderr)
        sys.exit(1)
    # 注入图片尺寸与坐标约束
    dims = _get_image_size(img_path)
    if dims:
        if use_normalized:
            hint = "\n[重要：此图尺寸为 {}×{} 像素。请输出归一化坐标(0-1)，格式为 x y 两个小数，左上角(0,0)、右下角(1,1)。例如 0.5 0.5 表示图像中心。不要输出像素值。]"
            question = question.rstrip() + hint.format(dims[0], dims[1])
        else:
            hint = "\n[重要：此图尺寸为 {}×{} 像素。返回的 x y 必须是以整张图片最左上角(0,0)为原点的绝对像素坐标，不能缩放、不能只算某块区域、不能使用界面内相对坐标。]"
            question = question.rstrip() + hint.format(dims[0], dims[1])

    if verbose:
        print("--- vision_proxy 输入 ---", file=sys.stderr)
        print("image:", img_path, "dims:", dims, file=sys.stderr)
        print("prompt:", repr(question[:500] + ("..." if len(question) > 500 else "")), file=sys.stderr)
    cfg = load_config()
    # 支持 --provider / --model 覆盖，用于 benchmark 多 provider 测试
    provider = provider_override or cfg.get("provider") or "qwen"
    block = cfg.get(provider)
    if isinstance(block, dict) and block.get("base_url"):
        base_url = (block.get("base_url") or "").rstrip("/")
        api_key = (block.get("api_key") or "").strip()
        model = (model_override or block.get("model_name") or "").strip()
    else:
        base_url = (cfg.get("base_url") or "").rstrip("/")
        api_key = cfg.get("api_key") or ""
        model = (
            model_override
            or cfg.get("model_name")
            or cfg.get("model")
            or os.environ.get("VISION_MODEL", "qwen3-vl-30b-a3b-instruct")
        )
    if not api_key or not base_url:
        print("vision_config.json or VISION_API_KEY/VISION_BASE_URL required", file=sys.stderr)
        sys.exit(1)
    # 鉴权：默认 Bearer；若配置 auth_header 为 Api-Key 则用 Api-Key 头（部分 GLM 网关）
    headers = {"Content-Type": "application/json"}
    if (cfg.get("auth_header") or "").lower() == "api-key":
        headers["Api-Key"] = api_key
    else:
        headers["Authorization"] = "Bearer " + api_key
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
    extra = cfg.get("extra_body") or {}
    if isinstance(extra, dict) and extra:
        body.update(extra)

    try:
        req = urllib.request.Request(
            f"{base_url}/chat/completions",
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=90) as r:
            out = json.loads(r.read().decode("utf-8"))
        text = (out.get("choices") or [{}])[0].get("message", {}).get("content", "")
        m = re.search(r"<\|begin_of_box\|>(.*?)<\|end_of_box\|>", text, re.DOTALL)
        if m:
            text = m.group(1).strip()
        if verbose:
            print("--- vision_proxy 模型原始输出 ---", file=sys.stderr)
            print(text or "(空)", file=sys.stderr)
        print(text or "")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        try:
            os.makedirs(STATE_DIR, exist_ok=True)
            with open(VISION_LAST_ERROR, "w", encoding="utf-8") as f:
                f.write("HTTP {}\n\n{}".format(e.code, err_body))
        except OSError:
            pass
        print("HTTP {} - details saved to {}".format(e.code, VISION_LAST_ERROR), file=sys.stderr)
        print(err_body, file=sys.stderr)
        sys.exit(1)
    except (OSError, ValueError) as e:
        try:
            os.makedirs(STATE_DIR, exist_ok=True)
            with open(VISION_LAST_ERROR, "w", encoding="utf-8") as f:
                f.write(str(e))
        except OSError:
            pass
        print("Error: {} - saved to {}".format(e, VISION_LAST_ERROR), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
