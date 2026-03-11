#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进化环客户端：向 CCR (Claude Code Router) 的 /api/agent 提交一轮进化任务，
由 Claude Code 在本项目内执行 agent_evolution_workflow 的一轮闭环。

用法:
  python scripts/evolution_loop_client.py [--once] [--message "自定义任务"]
  --once  只跑一轮（默认）
  --message  覆盖配置中的 evolution_prompt

配置: runtime/config/evolution_loop.json
  ccr_base_url, ccr_api_key, friday_project_path, evolution_prompt, auto_interval_seconds
"""
from __future__ import print_function

import os
import sys
import json
import argparse
import urllib.request
import urllib.error
import ssl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_DIR = os.path.join(ROOT, "runtime", "config")
CONFIG_FILE = os.path.join(CONFIG_DIR, "evolution_loop.json")
LOG_DIR = os.path.join(ROOT, "runtime", "logs")
STATE_DIR = os.path.join(ROOT, "runtime", "state")
EVOLUTION_LOG = os.path.join(LOG_DIR, "evolution_loop.log")
EVOLUTION_LAST_STATUS_FILE = os.path.join(STATE_DIR, "evolution_last_status.json")
EVOLUTION_SESSION_PENDING = "evolution_session_pending.json"
EVOLUTION_COMPLETED_PREFIX = "evolution_completed_"

DEFAULT_EVOLUTION_PROMPT = """请读取本项目 references/agent_evolution_workflow.md，按其中「通用智能体执行清单」执行**一轮**进化环：
1）读 current_mission.json
2）假设：读 capability_gaps、failures，写 assume 日志
3）自主决策：定 current_goal 与 next_action，写 plan 日志
4）自主执行：执行脚本/改文档，写 track 日志
5）自主校验：运行 self_verify_capabilities.py（基线）+ 按本轮执行做针对性校验，写 verify 日志
6）自主反思：更新 failures 等，写 decide 日志，loop_round+1，phase 设回假设。
请在本项目目录下执行并写入 state 与 behavior_log。"""

DEFAULT_CONFIG = {
    "ccr_base_url": "http://localhost:3001",
    "ccr_api_key": "",
    "friday_project_path": ROOT,
    "evolution_prompt": DEFAULT_EVOLUTION_PROMPT,
    "auto_interval_seconds": 0,
    "request_timeout_seconds": 300,
}


def _log(msg):
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(EVOLUTION_LOG, "a", encoding="utf-8") as f:
            f.write("%s\n" % msg)
            f.flush()
    except Exception:
        pass


def _state_dir(project_path=None):
    return os.path.join(project_path or ROOT, "runtime", "state")


def can_submit_evolution(project_path=None):
    """上一轮会话是否已完成（已写入 evolution_completed_<session_id>.json）。未完成则不可提交下一轮。"""
    state_dir = _state_dir(project_path)
    pending_path = os.path.join(state_dir, EVOLUTION_SESSION_PENDING)
    if not os.path.isfile(pending_path):
        return True
    try:
        with open(pending_path, "r", encoding="utf-8") as f:
            d = json.load(f)
        sid = (d.get("session_id") or "").strip()
        if not sid:
            return True
        completed_path = os.path.join(state_dir, EVOLUTION_COMPLETED_PREFIX + sid + ".json")
        return os.path.isfile(completed_path)
    except Exception:
        return True


def load_config():
    if os.path.isfile(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            for k, v in DEFAULT_CONFIG.items():
                if k not in cfg:
                    cfg[k] = v
            return cfg
        except Exception as e:
            _log("evolution_loop load_config error: %s" % e)
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)
    _log("evolution_loop created default config at %s (please set ccr_api_key)" % CONFIG_FILE)
    return DEFAULT_CONFIG.copy()


def run_once(message=None, config=None, user_hint=None):
    from datetime import datetime, timezone

    config = config or load_config()
    base_url = (config.get("ccr_base_url") or "").rstrip("/")
    api_key = (config.get("ccr_api_key") or "").strip()
    project_path = os.path.abspath(config.get("friday_project_path") or ROOT)
    prompt = message or config.get("evolution_prompt") or DEFAULT_EVOLUTION_PROMPT
    if user_hint:
        uh = user_hint.strip()
        if uh:
            prompt = prompt.rstrip() + "\n\n【用户本轮的补充或优先级】\n" + uh

    # 生成会话 ID，写入 pending，并告知智能体完成时须写 completed 文件
    session_id = "ev_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    state_dir = _state_dir(project_path)
    os.makedirs(state_dir, exist_ok=True)
    pending_path = os.path.join(state_dir, EVOLUTION_SESSION_PENDING)
    try:
        with open(pending_path, "w", encoding="utf-8") as f:
            json.dump({
                "session_id": session_id,
                "started_at": datetime.now(timezone.utc).isoformat(),
                "project_path": project_path,
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        _log("evolution_loop write pending error: %s" % e)
    session_block = (
        "\n\n【本任务会话 ID】%s\n"
        "完成本轮后（自主优化反思结束时）必须在 runtime/state/ 下写入 evolution_completed_%s.json，"
        "包含会话详细信息（current_goal、做了什么、是否完成、loop_round 等），否则下一轮无法提交。"
    ) % (session_id, session_id)
    prompt = prompt.rstrip() + session_block

    timeout = max(60, int(config.get("request_timeout_seconds") or 300))

    url = "%s/api/agent" % base_url
    body = {
        "projectPath": os.path.abspath(project_path),
        "message": prompt,
        "provider": "claude",
        "stream": False,
    }
    data = json.dumps(body).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if api_key:
        headers["x-api-key"] = api_key

    _log("evolution_loop POST %s (timeout=%ss)" % (url, timeout))
    try:
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        ctx = ssl.create_default_context()
        if base_url.startswith("https"):
            ctx.check_hostname = True
            ctx.verify_mode = ssl.CERT_REQUIRED
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            raw = resp.read().decode("utf-8")
            out = json.loads(raw) if raw.strip() else {}
            _log("evolution_loop success: %s" % json.dumps(out, ensure_ascii=False)[:500])
            return True, out
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8") if e.fp else ""
        _log("evolution_loop HTTP %s: %s" % (e.code, err_body[:300]))
        return False, {"error": "HTTP %s" % e.code, "body": err_body}
    except urllib.error.URLError as e:
        _log("evolution_loop URLError: %s" % e.reason)
        return False, {"error": str(e.reason)}
    except Exception as e:
        _log("evolution_loop exception: %s" % e)
        return False, {"error": str(e)}


def build_auto_evolution_hint():
    """
    自动进化环下一轮：仅附带「本轮总结 + 历史轮次总结」作为背景，避免提示过长。
    内容来自 references/evolution_auto_last.md（反思阶段写入的摘要与目录/影响文件）。
    """
    parts = []
    parts.append("【自动进化环·背景】以下为上一轮与历史轮次总结（references/evolution_auto_last.md），假设阶段请先读再动手，避免重复。")
    try:
        eal = os.path.join(ROOT, "references", "evolution_auto_last.md")
        if os.path.isfile(eal):
            with open(eal, "r", encoding="utf-8") as f:
                body = f.read()
            if body and len(body.strip()) > 80:
                parts.append(body[:3200])
    except Exception:
        pass
    parts.append("（以上为背景信息；**以 references/agent_evolution_workflow.md 为准（基线）**。请基于本文与 capability_gaps/failures 做尚未完成的下一步，若已全部完成则 decide 说明本轮无新动作。具体细节可读 runtime/logs/behavior_*.log。）")
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser(description="Submit one evolution loop task to CCR /api/agent")
    ap.add_argument("--once", action="store_true", default=True, help="Run once (default)")
    ap.add_argument("--message", "-m", type=str, default=None, help="Override evolution_prompt")
    ap.add_argument("--user-hint-file", type=str, default=None, help="Append content as user hint to prompt")
    ap.add_argument("--auto-evolution", action="store_true", help="自动进化环：附带上一轮摘要，减少重复")
    ap.add_argument(
        "--ack-complete",
        action="store_true",
        help="上一轮在客户端超时但 CC 已跑完时：将 evolution_last_status 标为成功，自动进化环可立即再提交",
    )
    ap.add_argument(
        "--check-only",
        action="store_true",
        help="上一轮会话是否已完成（evolution_completed_<session_id>.json 已存在）；0=可提交，1=不可提交",
    )
    args = ap.parse_args()

    if getattr(args, "check_only", False):
        config = load_config()
        project_path = os.path.abspath(config.get("friday_project_path") or ROOT)
        ok = can_submit_evolution(project_path)
        print("ok" if ok else "blocked")
        return 0 if ok else 1

    if getattr(args, "ack_complete", False):
        _write_last_status("ok", "user_ack: CC 已跑完，清除超时状态")
        config = load_config()
        project_path = os.path.abspath(config.get("friday_project_path") or ROOT)
        state_dir = _state_dir(project_path)
        pending_path = os.path.join(state_dir, EVOLUTION_SESSION_PENDING)
        if os.path.isfile(pending_path):
            try:
                with open(pending_path, "r", encoding="utf-8") as f:
                    d = json.load(f)
                sid = (d.get("session_id") or "").strip()
                if sid:
                    completed_path = os.path.join(state_dir, EVOLUTION_COMPLETED_PREFIX + sid + ".json")
                    if not os.path.isfile(completed_path):
                        from datetime import datetime, timezone
                        with open(completed_path, "w", encoding="utf-8") as f:
                            json.dump({"session_id": sid, "message": "user_ack", "completed_at": datetime.now(timezone.utc).isoformat()}, f, ensure_ascii=False, indent=2)
                        print("OK: 已写入 evolution_completed_%s.json，下一轮可提交。" % sid)
            except Exception as e:
                print("WARN: 写入 completed 失败: %s" % e)
        print("OK: evolution_last_status 已标为成功，自动进化环将不再因上一轮超时而跳过。")
        return 0

    user_hint = None
    if args.user_hint_file and os.path.isfile(args.user_hint_file):
        try:
            with open(args.user_hint_file, "r", encoding="utf-8") as f:
                user_hint = f.read()
        except Exception:
            pass
    if args.auto_evolution:
        auto_block = build_auto_evolution_hint()
        user_hint = (user_hint + "\n\n" + auto_block).strip() if user_hint else auto_block
    ok, result = run_once(message=args.message, user_hint=user_hint)
    err = result.get("error") or ""
    if ok:
        _write_last_status("ok", "")
        print("OK:", result.get("sessionId", ""), result.get("tokens", {}))
        return 0
    status = "timeout" if (err == "timeout" or "timed out" in str(err).lower()) else "error"
    _write_last_status(status, err)
    print("FAIL:", err or result, file=sys.stderr)
    return 1


def _write_last_status(status, message):
    """写入最近一次进化环请求状态，供过程·结果与防重复提交判断。"""
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        from datetime import datetime, timezone
        with open(EVOLUTION_LAST_STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "status": status,
                "at": datetime.now(timezone.utc).isoformat(),
                "message": (message or "")[:200],
            }, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


if __name__ == "__main__":
    sys.exit(main())
