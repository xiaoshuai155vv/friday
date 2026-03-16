#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音会话文件管理：与 CC 对话时，会话记录写入 runtime/voice_sessions/ 下的 md 文件。

格式约定：
- ## 你：用户输入（ASR 转文字）
- ## CC：CC 的回复
- --日志：CC 执行日志行（CC 写入时每行前加此前缀）
- --已完成：CC 处理完成标记（CC 在最终回答后加此行）

CC 收到提示词后需：1) 实时将执行日志写入该文件（每行前加 --日志）；2) 最终结果写完后加 --已完成
"""
import os
import re
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SESSIONS_DIR = os.path.join(ROOT, "runtime", "voice_sessions")


def create_session():
    """新建语音会话，返回 (session_id, session_path)"""
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    sid = "voice_%s" % ts
    path = os.path.join(SESSIONS_DIR, "%s.md" % sid)
    header = """# 语音会话 %s
# 格式: ## 你 / ## CC / --日志(日志行) / --已完成(完成标记)

""" % datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(path, "w", encoding="utf-8") as f:
        f.write(header)
    return sid, path


def append_user(session_path, text):
    """追加用户输入到会话文件"""
    if not session_path or not os.path.isfile(session_path):
        return
    block = "\n## 你\n%s\n\n## CC\n" % (text or "").strip()
    with open(session_path, "a", encoding="utf-8") as f:
        f.write(block)


def get_cc_prompt_block(session_path, user_text):
    """生成要传给 CC 的提示词块，告知文件位置和格式要求"""
    abs_path = os.path.abspath(session_path)
    return """

【语音会话文件】
%s

【格式要求】
- 执行过程日志：每行前加 --日志
- 最终回答：写在 ## CC 区块内，完成后加一行 --已完成

【用户当前输入】
%s
""" % (abs_path, user_text)


def read_cc_content_after(session_path, after_marker="## CC"):
    """
    读取会话文件中最后一个 ## CC 区块的内容。
    返回 (content, is_completed)
    - content: CC 区块的文本（不含 --日志 前缀，但保留内容）
    - is_completed: 是否包含 --已完成
    """
    if not session_path or not os.path.isfile(session_path):
        return "", False
    try:
        with open(session_path, "r", encoding="utf-8") as f:
            raw = f.read()
    except Exception:
        return "", False
    parts = re.split(r"\n## CC\n", raw)
    if len(parts) < 2:
        return "", False
    last_cc = parts[-1].strip()
    is_completed = "--已完成" in last_cc
    lines = []
    for line in last_cc.split("\n"):
        if line.strip() == "--已完成":
            break
        if line.strip().startswith("--日志"):
            lines.append(line.strip()[4:].strip())
        else:
            lines.append(line)
    content = "\n".join(lines).strip()
    return content, is_completed
