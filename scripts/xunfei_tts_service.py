#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讯飞 TTS 服务：WebSocket 连接讯飞 v2/tts，PCM→WAV 播放。
参考 ai_vision_chat/lib/services/xunfei_tts_service.dart
"""
import base64
import hmac
import hashlib
import json
import os
import struct
import sys
import tempfile
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

from xunfei_config_loader import load_xunfei_config, is_configured


def _generate_tts_url():
    """生成 TTS WebSocket 鉴权 URL"""
    cfg = load_xunfei_config()
    host = "tts-api.xfyun.cn"
    path = "/v2/tts"
    date = formatdate(timeval=None, localtime=False, usegmt=True)
    sign_str = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
    key = cfg.get("api_secret", "").encode("utf-8")
    sig = hmac.new(key, sign_str.encode("utf-8"), hashlib.sha256).digest()
    signature = base64.b64encode(sig).decode("utf-8")
    auth = f'api_key="{cfg.get("api_key")}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'
    auth_b64 = base64.b64encode(auth.encode("utf-8")).decode("utf-8")
    return f"wss://{host}{path}?authorization={auth_b64}&date={quote(date)}&host={host}"


def _pcm_to_wav(pcm_bytes, sample_rate=16000, channels=1, bits=16):
    """PCM 转 WAV"""
    data_size = len(pcm_bytes)
    byte_rate = sample_rate * channels * bits // 8
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        36 + data_size,
        b"WAVE",
        b"fmt ",
        16,
        1,
        channels,
        sample_rate,
        byte_rate,
        channels * bits // 8,
        bits,
        b"data",
        data_size,
    )
    return header + pcm_bytes


def text_to_speech(text: str, play: bool = True) -> bytes:
    """
    文本转语音，返回 WAV 字节；若 play=True 则播放。
    """
    if not text or not text.strip():
        return b""
    if not is_configured():
        return b""
    if not HAS_WEBSOCKET:
        return b""

    cfg = load_xunfei_config()
    url = _generate_tts_url()
    chunks = []

    def on_message(ws, message):
        try:
            data = json.loads(message)
            if data.get("code") != 0:
                return
            d = data.get("data") or {}
            if d.get("audio"):
                chunks.append(base64.b64decode(d["audio"]))
        except Exception:
            pass

    def on_error(ws, err):
        pass

    def on_close(ws, close_status_code, close_msg):
        pass

    ws = websocket.WebSocketApp(
        url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    import threading
    t = threading.Thread(target=lambda: ws.run_forever())
    t.daemon = True
    t.start()
    import time
    time.sleep(0.15)
    req = {
        "common": {"app_id": cfg.get("app_id")},
        "business": {
            "aue": "raw",
            "tte": "UTF8",
            "ent": "intp65",
            "vcn": cfg.get("voice", "xiaoyan"),
            "pitch": int(cfg.get("pitch", 50)),
            "speed": int(cfg.get("speed", 50)),
            "volume": int(cfg.get("volume", 50)),
        },
        "data": {
            "status": 2,
            "text": base64.b64encode(text.encode("utf-8")).decode("utf-8"),
        },
    }
    ws.send(json.dumps(req))
    t.join(timeout=25)
    ws.close()
    if not chunks:
        return b""
    pcm = b"".join(chunks)
    wav = _pcm_to_wav(pcm)
    if play and wav:
        _play_wav(wav)
    return wav


def _play_wav(wav_bytes: bytes):
    """播放 WAV 字节"""
    try:
        if sys.platform == "win32":
            import winsound
            winsound.PlaySound(wav_bytes, winsound.SND_MEMORY)
        else:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(wav_bytes)
                path = f.name
            import subprocess
            subprocess.run(
                ["aplay", path] if os.path.exists("/usr/bin/aplay") else ["afplay", path],
                timeout=60,
                capture_output=True,
            )
            try:
                os.remove(path)
            except Exception:
                pass
    except Exception:
        pass


if __name__ == "__main__":
    t = sys.argv[1] if len(sys.argv) > 1 else "你好，我是星期五。"
    text_to_speech(t, play=True)
