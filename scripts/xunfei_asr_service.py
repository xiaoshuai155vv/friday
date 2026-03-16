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


def _resample_to_16k(arr_float, orig_sr):
    """将任意采样率转为 16kHz"""
    if orig_sr == SAMPLE_RATE:
        return arr_float
    try:
        from scipy import signal
        n = int(len(arr_float) * SAMPLE_RATE / orig_sr)
        return signal.resample(arr_float, n)
    except Exception:
        return arr_float


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
    debug=False,
    gain=1.0,
    save_wav_path=None,
) -> str:
    """
    录音并识别，返回最终文本。流式返回：每收到讯飞 partial 即回调 on_partial。
    duration_sec: 最大录音时长
    on_partial: 部分结果回调 (text) -> None，实时流式
    stop_event: threading.Event，set() 时提前结束
    device_id: 麦克风设备 ID，None 时用 sounddevice 默认（通常为 Realtek 麦克风）
    """
    if not is_configured() or not HAS_WEBSOCKET or not HAS_SOUNDDEVICE:
        return ""

    cfg = load_xunfei_config()
    url = _generate_iat_url()
    # 动态修正 wpgs：pgs="apd" 追加，pgs="rpl" 替换 rg 指定范围
    result_segments = []
    last_full_text = [""]

    def on_message(ws, message):
        try:
            data = json.loads(message)
            if debug:
                print("[DEBUG] 讯飞响应:", json.dumps(data, ensure_ascii=False)[:300])
            if data.get("code") != 0:
                if debug:
                    print("[DEBUG] 错误码:", data.get("code"), data.get("message", ""))
                return
            d = data.get("data") or {}
            txt = _parse_result(d)
            if not txt:
                return
            res = d.get("result") or {}
            pgs = res.get("pgs", "apd")
            rg = res.get("rg") or [1, 1]
            if pgs == "apd":
                result_segments.append(txt)
            else:
                i0, i1 = max(0, rg[0] - 1), rg[1]
                result_segments[i0:i1] = [txt]
            full = "".join(result_segments)
            last_full_text[0] = full
            if d.get("status") == 2:
                pass
            if on_partial:
                on_partial(full)
        except Exception:
            pass

    def on_error(ws, err):
        if debug:
            print("[DEBUG] WebSocket 错误:", err)

    ws = websocket.WebSocketApp(url, on_message=on_message, on_error=on_error)
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
    chunk_count = [0]
    rms_samples = []
    all_chunks = [] if save_wav_path else None

    def record_callback(indata, frames, time_info, status):
        if status:
            return
        if stop.is_set():
            return
        arr = np.asarray(indata, dtype=np.float32).flatten()
        if debug and chunk_count[0] < 5:
            rms = np.sqrt(np.mean(arr ** 2)) * 32768
            rms_samples.append(rms)
        # 与 test_record_native 一致：InputStream 返回 [-1,1]，用 32767 转 int16
        arr = (arr * 32767 * gain).clip(-32768, 32767).astype(np.int16)
        raw = arr.tobytes()
        if all_chunks is not None:
            all_chunks.append(arr)
        chunk_count[0] += 1
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

    dev_info = sd.query_devices(device_id, "input")
    dev_sr = int(dev_info.get("default_samplerate", 44100))
    use_sr = dev_sr if dev_sr in (44100, 48000, 96000) else 44100
    block = max(256, int(use_sr * CHUNK_MS / 1000))

    def record_callback_wrap(indata, frames, time_info, status):
        arr = np.asarray(indata, dtype=np.float32).flatten()
        arr = _resample_to_16k(arr, use_sr)
        if len(arr) == 0:
            return
        record_callback(arr.reshape(-1, 1), frames, time_info, status)

    # 用 InputStream（与 test_record_native 一致），返回归一化 [-1,1]
    stream = sd.InputStream(
        samplerate=use_sr,
        channels=1,
        dtype="float32",
        blocksize=block,
        callback=record_callback_wrap,
        device=device_id,
    )
    stream.start()

    while (time.time() - start < duration_sec) and not stop.is_set():
        time.sleep(0.1)

    stream.stop()
    stream.close()

    if debug and rms_samples:
        avg_rms = sum(rms_samples) / len(rms_samples)
        print("[DEBUG] 录音采样率: %d Hz（设备原生）→ 16k 发送" % use_sr)
        print("[DEBUG] 前5帧 RMS: %.0f, 共 %d 帧" % (avg_rms, chunk_count[0]))

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
    time.sleep(1.5)
    ws.close()

    if save_wav_path and all_chunks:
        import struct
        pcm = np.concatenate(all_chunks).tobytes()
        wav = struct.pack("<4sI4s4sIHHIIHH4sI", b"RIFF", 36 + len(pcm), b"WAVE", b"fmt ", 16, 1, 1, SAMPLE_RATE, SAMPLE_RATE * 2, 2, 16, b"data", len(pcm)) + pcm
        with open(save_wav_path, "wb") as f:
            f.write(wav)

    return last_full_text[0]


if __name__ == "__main__":
    print("开始录音 5 秒...")
    text = record_and_recognize(5.0, on_partial=lambda t: print("  partial:", t))
    print("识别结果:", text or "(无)")
