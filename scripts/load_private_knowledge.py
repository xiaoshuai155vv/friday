#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按需加载私域知识：根据关键词或任务类型返回对应 reference 路径或摘要。
用法:
  python load_private_knowledge.py list
  python load_private_knowledge.py get ihaier
  python load_private_knowledge.py get user_assumptions
"""

import argparse
import os

REFS = os.path.join(os.path.dirname(__file__), "..", "references")
MAP = {
    "ihaier": "ihaier.md",
    "user_assumptions": "private_knowledge.md",
}


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
    if not os.path.isfile(path):
        print("File not found:", path)
        return
    with open(path, "r", encoding="utf-8") as f:
        print(f.read())


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("list")
    p_get = sp.add_parser("get")
    p_get.add_argument("key", choices=list(MAP.keys()))
    args = ap.parse_args()

    if args.cmd == "list":
        list_refs()
    elif args.cmd == "get":
        get_ref(args.key)


if __name__ == "__main__":
    main()
