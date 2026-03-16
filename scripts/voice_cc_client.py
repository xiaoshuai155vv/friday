#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音对话 CC 客户端：向 CCR /api/agent 提交用户语音转文字，并告知会话文件路径与格式要求。
CC 需将执行日志和结果写入该文件，完成后加 --已完成。
"""
import os
import sys
import json
import urllib.request
import urllib.error
import ssl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_FILE = os.path.join(ROOT, "runtime", "config", "evolution_loop.json")


def load_config():
    cfg = {}
    if os.path.isfile(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            pass
    return cfg


def call_cc_voice(session_path, user_text, timeout_sec=600):
    """
    调用 CCR /api/agent 处理用户语音输入。
    提示词中包含会话文件路径和格式要求。
    返回 (success, result_or_error)
    """
    cfg = load_config()
    base_url = (cfg.get("ccr_base_url") or "").rstrip("/")
    api_key = (cfg.get("ccr_api_key") or "").strip()
    project_path = os.path.abspath(cfg.get("friday_project_path") or ROOT)
    if not base_url or not api_key:
        return False, "未配置 CCR: 请检查 runtime/config/evolution_loop.json 的 ccr_base_url 和 ccr_api_key"

    abs_path = os.path.abspath(session_path)
    prompt = """用户通过语音说: %s

请处理此请求。

【重要】会话日志文件路径: %s

【格式要求】
- 执行过程日志：每行前加 --日志
- 最终回答：写在当前 ## CC 区块内，完成后加一行 --已完成

请将你的执行日志和最终结果实时写入该文件，完成后务必加上 --已完成。""" % (user_text, abs_path)

    url = "%s/api/agent" % base_url
    body = {
        "projectPath": project_path,
        "message": prompt,
        "provider": "claude",
        "stream": False,
    }
    data = json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if api_key:
        headers["x-api-key"] = api_key

    try:
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        ctx = ssl.create_default_context()
        if base_url.startswith("https"):
            ctx.check_hostname = True
            ctx.verify_mode = ssl.CERT_REQUIRED
        with urllib.request.urlopen(req, timeout=timeout_sec, context=ctx) as resp:
            raw = resp.read().decode("utf-8")
            out = json.loads(raw) if raw.strip() else {}
            return True, out
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8") if e.fp else ""
        return False, "HTTP %s: %s" % (e.code, err_body[:300])
    except urllib.error.URLError as e:
        return False, str(e.reason)
    except Exception as e:
        return False, str(e)
