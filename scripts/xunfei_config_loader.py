#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讯飞 API 配置加载
从 runtime/config/xunfei_config.json 或环境变量读取
"""
import os
import json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_DIR = os.path.join(ROOT, "runtime", "config")
CONFIG_FILE = os.path.join(CONFIG_DIR, "xunfei_config.json")
EXAMPLE_FILE = os.path.join(ROOT, "config", "xunfei_config.example.json")


def load_xunfei_config():
    """加载讯飞配置，优先从 runtime/config/xunfei_config.json，其次环境变量。
    用户需复制 config/xunfei_config.example.json 到 runtime/config/xunfei_config.json 并填入密钥。"""
    cfg = {}
    if os.path.isfile(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            pass
    cfg.setdefault("app_id", os.environ.get("XUNFEI_APP_ID", ""))
    cfg.setdefault("api_key", os.environ.get("XUNFEI_API_KEY", ""))
    cfg.setdefault("api_secret", os.environ.get("XUNFEI_API_SECRET", ""))
    cfg.setdefault("voice", "xiaoyan")
    cfg.setdefault("speed", 50)
    cfg.setdefault("volume", 50)
    cfg.setdefault("pitch", 50)
    return cfg


def is_configured():
    """检查讯飞是否已配置"""
    c = load_xunfei_config()
    return (
        bool(c.get("app_id"))
        and len(str(c.get("app_id", ""))) > 5
        and bool(c.get("api_key"))
        and len(str(c.get("api_key", ""))) > 10
        and bool(c.get("api_secret"))
        and len(str(c.get("api_secret", ""))) > 10
    )
