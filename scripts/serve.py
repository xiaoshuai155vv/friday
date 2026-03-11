#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地 HTTP 服务：静态文件 + /stream SSE 实时推送 runtime/state 与 runtime/logs。
启动后约 1.5 秒会自动拉起悬浮窗（无 CMD），无需再手动运行 launch_friday_floating.py。
用法: python serve.py [port]，默认 8765。浏览器打开 http://localhost:8765/assets/friday-ui.html
"""
import os
import sys
import json
import time
import http.server
import socketserver

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PORT = int(sys.argv[1]) if len(sys.argv) >= 2 else 8765
STATE_FILE = os.path.join(ROOT, "runtime", "state", "current_mission.json")
LOGS_FILE = os.path.join(ROOT, "runtime", "state", "recent_logs.json")


def read_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def read_logs():
    try:
        with open(LOGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"entries": []}


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_GET(self):
        if self.path == "/stream" or self.path == "/stream/":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            try:
                while True:
                    payload = {"state": read_state(), "logs": read_logs()}
                    data = json.dumps(payload, ensure_ascii=False)
                    self.wfile.write(("data: " + data + "\n\n").encode("utf-8"))
                    self.wfile.flush()
                    time.sleep(1)
            except (BrokenPipeError, ConnectionResetError):
                pass
            return
        return super().do_GET()


def main():
    import subprocess
    import threading
    os.chdir(ROOT)
    try:
        subprocess.run(
            [sys.executable, os.path.join(ROOT, "scripts", "export_recent_logs.py"), "50"],
            cwd=ROOT, capture_output=True, timeout=10
        )
    except Exception:
        pass
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("Serving at http://localhost:{}/  (UI: http://localhost:{}/assets/friday-ui.html)".format(PORT, PORT))

        def open_floating():
            time.sleep(1.5)
            try:
                launch = os.path.join(ROOT, "scripts", "launch_friday_floating.py")
                creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
                subprocess.Popen(
                    [sys.executable, launch],
                    cwd=ROOT,
                    creationflags=creationflags,
                    env={**os.environ, "FRIDAY_LAUNCH_NO_WINDOW": "1"},
                )
                print("悬浮窗已尝试启动（无 CMD），若未出现请稍等几秒或手动运行 scripts/launch_friday_floating.py）")
            except Exception as e:
                print("悬浮窗启动失败:", e)
        threading.Thread(target=open_floating, daemon=True).start()

        httpd.serve_forever()


if __name__ == "__main__":
    main()
