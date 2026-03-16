#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音捕获：录音→讯飞 ASR→调用 do.py。
供 do.py「语音」意图或悬浮球语音浮层使用。
用法: python voice_capture.py [最大秒数]
"""
import os
import sys
import subprocess

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPTS)
sys.path.insert(0, SCRIPTS)

def main():
    duration = float(sys.argv[1]) if len(sys.argv) > 1 else 15.0
    try:
        from xunfei_asr_service import record_and_recognize, is_configured, HAS_SOUNDDEVICE, HAS_WEBSOCKET
    except ImportError:
        print("请安装: pip install websocket-client sounddevice numpy", file=sys.stderr)
        return 1
    if not is_configured():
        print("请配置讯飞 API: 复制 config/xunfei_config.example.json 到 runtime/config/xunfei_config.json", file=sys.stderr)
        return 1
    if not HAS_SOUNDDEVICE or not HAS_WEBSOCKET:
        print("依赖缺失: websocket-client, sounddevice", file=sys.stderr)
        return 1
    print("开始录音 %s 秒，说完后按 Ctrl+C 提前结束..." % int(duration), file=sys.stderr)
    text = record_and_recognize(duration_sec=duration, on_partial=lambda t: print("  ", t, file=sys.stderr))
    if not text or not text.strip():
        print("未识别到内容", file=sys.stderr)
        return 1
    print(text)
    subprocess.run(
        [sys.executable, os.path.join(SCRIPTS, "do.py"), text.strip()],
        cwd=ROOT,
    )
    return 0

if __name__ == "__main__":
    sys.exit(main())
