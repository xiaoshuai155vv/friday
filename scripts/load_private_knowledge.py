#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按需加载私域知识：根据关键词或任务类型返回对应 reference 路径或摘要。
用法:
  python load_private_knowledge.py list
  python load_private_knowledge.py get domains
  python load_private_knowledge.py get user_assumptions
  python load_private_knowledge.py auto "用户意图关键词"
  python load_private_knowledge.py detect "ihaier 发送消息"
"""

import argparse
import os
import json
import hashlib
import time

REFS = os.path.join(os.path.dirname(__file__), "..", "references")
MEMORY = os.path.join(os.path.dirname(__file__), "..", "memory")
MAP = {
    "domains": "private_domains.md",
    "user_assumptions": "private_knowledge.md",
    "user_preferences": "user_preferences.json"
}

# 关键词到私域的映射
KEYWORD_TO_DOMAIN = {
    "ihaier": "domains",
    "办公平台": "domains",
    "i海螺": "domains",
    "绩效": "domains",
    "绩效管理": "domains",
    "消息": "domains",
    "联系人": "domains",
    "办公": "domains",
}

# 简单缓存
_CACHE = {}
_CACHE_TTL = 300  # 5分钟缓存


def _get_cache_key(key, content_hash):
    return f"{key}:{content_hash}"


def _load_content(path):
    """加载文件内容，带缓存"""
    if not os.path.isfile(path):
        return None

    mtime = os.path.getmtime(path)
    content_hash = f"{path}:{mtime}"
    cache_key = _get_cache_key(path, content_hash)

    if cache_key in _CACHE:
        cached_time, cached_content = _CACHE[cache_key]
        if time.time() - cached_time < _CACHE_TTL:
            return cached_content

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    _CACHE[cache_key] = (time.time(), content)
    return content


def list_refs():
    for key, fname in MAP.items():
        path = os.path.join(REFS, fname)
        exists = "yes" if os.path.isfile(path) else "no"
        print(f"{key}\t{path}\t{exists}")


def get_ref(key):
    fname = MAP.get(key)
    if not fname:
        print(f"Unknown key: {key}. Known: {list(MAP.keys())}")
        return
    path = os.path.join(REFS, fname)
    content = _load_content(path)
    if content is None:
        print("File not found:", path)
        return
    print(content)


def detect_domain(intent):
    """根据用户意图自动检测相关的私域知识"""
    matched_domains = []

    intent_lower = intent.lower()
    for keyword, domain_key in KEYWORD_TO_DOMAIN.items():
        if keyword.lower() in intent_lower:
            matched_domains.append(domain_key)

    # 去重
    matched_domains = list(set(matched_domains))

    if matched_domains:
        print(f"检测到相关私域: {matched_domains}")
        for domain in matched_domains:
            fname = MAP.get(domain)
            if fname:
                path = os.path.join(REFS, fname)
                content = _load_content(path)
                if content:
                    print(f"\n=== {fname} ===")
                    print(content[:2000])  # 限制输出长度
                    if len(content) > 2000:
                        print(f"\n... (共 {len(content)} 字符)")
    else:
        print("未检测到相关私域知识")

    return matched_domains


def auto_load(intent):
    """自动加载与意图相关的私域知识并输出（供其他脚本调用）"""
    matched_domains = []

    intent_lower = intent.lower()
    for keyword, domain_key in KEYWORD_TO_DOMAIN.items():
        if keyword.lower() in intent_lower:
            matched_domains.append(domain_key)

    matched_domains = list(set(matched_domains))

    result = {}
    for domain in matched_domains:
        fname = MAP.get(domain)
        if fname:
            path = os.path.join(REFS, fname)
            content = _load_content(path)
            if content:
                result[domain] = {
                    "file": fname,
                    "content": content[:5000],  # 限制长度
                }

    # 输出 JSON 格式，便于其他脚本解析
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("list")
    p_get = sp.add_parser("get")
    p_get.add_argument("key", choices=list(MAP.keys()))
    p_auto = sp.add_parser("auto")
    p_auto.add_argument("intent", nargs="+", help="用户意图关键词")
    p_detect = sp.add_parser("detect")
    p_detect.add_argument("intent", nargs="+", help="用户意图关键词")
    args = ap.parse_args()

    if args.cmd == "list":
        list_refs()
    elif args.cmd == "get":
        get_ref(args.key)
    elif args.cmd == "auto":
        intent = " ".join(args.intent)
        auto_load(intent)
    elif args.cmd == "detect":
        intent = " ".join(args.intent)
        detect_domain(intent)


if __name__ == "__main__":
    main()

def get_user_preferences():
    """获取用户偏好设置"""
    pref_path = os.path.join(MEMORY, "user_preferences.json")
    if os.path.isfile(pref_path):
        try:
            with open(pref_path, "r", encoding="utf-8") as f:
                prefs = json.load(f)
            return prefs
        except Exception as e:
            print(f"Error loading user preferences: {e}")
            return None
    return None

def get_ref(key):
    fname = MAP.get(key)
    if not fname:
        print(f"Unknown key: {key}. Known: {list(MAP.keys())}")
        return
    # 特殊处理用户偏好文件
    if key == "user_preferences":
        pref_path = os.path.join(MEMORY, fname)
        if os.path.isfile(pref_path):
            try:
                with open(pref_path, "r", encoding="utf-8") as f:
                    prefs = json.load(f)
                print(json.dumps(prefs, ensure_ascii=False, indent=2))
                return prefs
            except Exception as e:
                print(f"Error loading user preferences: {e}")
                return None
        else:
            print("User preferences file not found:", pref_path)
            return None
    
    path = os.path.join(REFS, fname)
    content = _load_content(path)
    if content is None:
        print("File not found:", path)
        return
    print(content)

