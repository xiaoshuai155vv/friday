#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 vision 自然语言输出解析出 run_plan 步骤。用法: python parse_vision_steps.py [vision_output.txt] 或 stdin"""
import sys
import os
import re
import json

def parse(text):
    steps = []
    if not text:
        return steps
    # 点击 (x, y) 或 click x y
    for m in re.finditer(r'点击\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)', text):
        steps.append({"do": "click", "x": int(m.group(1)), "y": int(m.group(2))})
    for m in re.finditer(r'click\s+(\d+)\s+(\d+)', text, re.I):
        steps.append({"do": "click", "x": int(m.group(1)), "y": int(m.group(2))})
    # 输入 "xxx" 或 type "xxx"
    for m in re.finditer(r'输入\s*["\']([^"\']*)["\']', text):
        steps.append({"do": "type", "text": m.group(1)})
    for m in re.finditer(r'type\s+["\']([^"\']*)["\']', text, re.I):
        steps.append({"do": "type", "text": m.group(1)})
    # key VK
    for m in re.finditer(r'按键\s+(\d+)', text):
        steps.append({"do": "key", "vk": int(m.group(1))})
    for m in re.finditer(r'key\s+(\d+)', text, re.I):
        steps.append({"do": "key", "vk": int(m.group(1))})
    return steps

def main():
    if len(sys.argv) >= 2:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()
    steps = parse(text)
    print(json.dumps(steps, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
