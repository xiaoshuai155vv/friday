#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讯飞 ASR 服务：麦克风录音 + IAT WebSocket，支持按需录音（电脑端：快捷键/点击触发）。
参考 ai_vision_chat/lib/services/true_realtime_speech_service.dart
"""
import base64
import hmac
import hashlib
import json
import os
import sys
import threading
from email.utils import formatdate
from urllib.parse import quote

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS = os.path.join(ROOT, "scripts")
sys.path.insert(0, SCRIPTS)

try:
    import websocket
    HAS_WEBSOCKET = True
except ImportError:
    HAS_WEBSOCKET = False

try:
    import sounddevice as sd
    import numpy as np
    HAS_SOUNDDEVICE = True
except ImportError:
    HAS_SOUNDDEVICE = False

from xunfei_config_loader import load_xunfei_config, is_configured

SAMPLE_RATE = 16000
CHUNK_MS = 40
CHUNK_SAMPLES = int(SAMPLE_RATE * CHUNK_MS / 1000)


def _generate_iat_url():
    """生成 IAT WebSocket 鉴权 URL"""
    cfg = load_xunfei_config()
    host = "iat-api.xfyun.cn"
    path = "/v2/iat"
    date = formatdate(timeval=None, localtime=False, usegmt=True)
    sign_str = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
    key = cfg.get("api_secret", "").encode("utf-8")
    sig = hmac.new(key, sign_str.encode("utf-8"), hashlib.sha256).digest()
    signature = base64.b64encode(sig).decode("utf-8")
    auth = f'api_key="{cfg.get("api_key")}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'
    auth_b64 = base64.b64encode(auth.encode("utf-8")).decode("utf-8")
    return f"wss://{host}{path}?authorization={quote(auth_b64)}&date={quote(date)}&host={host}"


def _parse_result(data):
    """解析讯飞识别结果 data.result"""
    text = []
    result = data.get("result")
    if not result:
        return ""
    ws = result.get("ws") or []
    for item in ws:
        for cw in (item.get("cw") or []):
            w = cw.get("w")
            if w:
                text.append(w)
    return "".join(text)


def record_and_recognize(
    duration_sec: float = 10.0,
    on_partial=None,
    stop_event=None,
    device_id=None,
) -> str:
    """
    录音并识别，返回最终文本。
    duration_sec: 最大录音时长
    on_partial: 部分结果回调 (text) -> None
    stop_event: threading.Event，set() 时提前结束
    device_id: 麦克风设备 ID，None 为默认
    """
    if not is_configured() or not HAS_WEBSOCKET or not HAS_SOUNDDEVICE:
        return ""

    cfg = load_xunfei_config()
    url = _generate_iat_url()
    final_text = []
    partial_text = []

    def on_message(ws, message):
        try:
            data = json.loads(message)
            if data.get("code") != 0:
                return
            d = data.get("data") or {}
            txt = _parse_result(d)
            if txt:
                partial_text.append(txt)
                if data.get("data", {}).get("status") == 2:
                    final_text.append(txt)
                if on_partial:
                    on_partial("".join(partial_text))
        except Exception:
            pass

    ws = websocket.WebSocketApp(url, on_message=on_message)
    t = threading.Thread(target=lambda: ws.run_forever())
    t.daemon = True
    t.start()

    import time
    time.sleep(0.4)

    # 首帧
    first = {
        "common": {"app_id": cfg.get("app_id")},
        "business": {
            "language": "zh_cn",
            "domain": "iat",
            "accent": "mandarin",
            "vad_eos": 10000,
            "dwa": "wpgs",
        },
        "data": {
            "status": 0,
            "format": "audio/L16;rate=16000",
            "audio": "",
            "encoding": "raw",
        },
    }
    try:
        ws.send(json.dumps(first))
    except Exception:
        return ""

    stop = stop_event or threading.Event()
    start = time.time()
    chunk_bytes = CHUNK_SAMPLES * 2

    def record_callback(indata, frames, time_info, status):
        if status:
            return
        if stop.is_set():
            return
        raw = indata[:, 0].astype(np.int16).tobytes()
        frame = {
            "data": {
                "status": 1,
                "format": "audio/L16;rate=16000",
                "audio": base64.b64encode(raw).decode("utf-8"),
                "encoding": "raw",
            },
        }
        try:
            ws.send(json.dumps(frame))
        except Exception:
            pass

    stream = sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16",
        blocksize=CHUNK_SAMPLES,
        callback=record_callback,
        device=device_id,
    )
    stream.start()

    while (time.time() - start < duration_sec) and not stop.is_set():
        time.sleep(0.1)

    stream.stop()
    stream.close()

    # 结束帧
    end_frame = {
        "data": {
            "status": 2,
            "format": "audio/L16;rate=16000",
            "audio": "",
            "encoding": "raw",
        },
    }
    try:
        ws.send(json.dumps(end_frame))
    except Exception:
        pass
    time.sleep(0.5)
    ws.close()

    return "".join(final_text) if final_text else "".join(partial_text)


if __name__ == "__main__":
    print("开始录音 5 秒...")
    text = record_and_recognize(5.0, on_partial=lambda t: print("  partial:", t))
    print("识别结果:", text or "(无)")
