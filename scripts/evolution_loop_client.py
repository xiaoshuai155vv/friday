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
    config = config or load_config()
    base_url = (config.get("ccr_base_url") or "").rstrip("/")
    api_key = (config.get("ccr_api_key") or "").strip()
    project_path = config.get("friday_project_path") or ROOT
    prompt = message or config.get("evolution_prompt") or DEFAULT_EVOLUTION_PROMPT
    if user_hint:
        uh = user_hint.strip()
        if uh:
            prompt = prompt.rstrip() + "\n\n【用户本轮的补充或优先级】\n" + uh
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
    自动进化环下一轮：生成「上一轮已做过什么 + 勿重复」的补充说明，随 user_hint 发给 CC。
    优先读 references/evolution_auto_last.md（反思阶段写入的摘要）；再拼 current_mission、track/decide、evolution_self_proposed。
    """
    parts = []
    # 轮次衔接：明确「历史 → 本轮」不断档
    round_hint = ""
    try:
        cm = os.path.join(STATE_DIR, "current_mission.json")
        if os.path.isfile(cm):
            with open(cm, "r", encoding="utf-8") as f:
                m = json.load(f)
            r = m.get("loop_round")
            ph = m.get("phase", "")
            if r is not None:
                round_hint = " current_mission: loop_round=%s phase=%s" % (r, ph)
    except Exception:
        pass
    parts.append("【自动进化环·上下文】定时触发；上一轮与历史已附下，假设阶段请先读再动手，避免重复已完成项。" + round_hint)
    # 上一轮直接写进仓库的摘要（与 capability_gaps/workflow 同级，下一轮假设必读）
    try:
        eal = os.path.join(ROOT, "references", "evolution_auto_last.md")
        if os.path.isfile(eal):
            with open(eal, "r", encoding="utf-8") as f:
                body = f.read()
            # 有实质内容再附（占位说明太多则只取后段）
            if body and len(body.strip()) > 120:
                parts.append("--- evolution_auto_last.md（上一轮摘要，勿重复）---")
                parts.append(body[:3500])
    except Exception:
        pass
    # current_mission
    try:
        cm = os.path.join(STATE_DIR, "current_mission.json")
        if os.path.isfile(cm):
            with open(cm, "r", encoding="utf-8") as f:
                m = json.load(f)
            parts.append("current_mission: loop_round=%s phase=%s mission=%s" % (
                m.get("loop_round", ""), m.get("phase", ""), (m.get("mission") or "")[:120]
            ))
    except Exception:
        pass
    # 最近 behavior 里 track / decide 摘要（避免重复）
    try:
        from datetime import datetime, timezone
        day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_path = os.path.join(LOG_DIR, "behavior_%s.log" % day)
        if os.path.isfile(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            picks = []
            for line in reversed(lines[-200:]):
                line = line.strip()
                if not line:
                    continue
                tab = line.split("\t", 5)
                if len(tab) >= 3 and tab[1] in ("track", "decide"):
                    picks.append("%s: %s" % (tab[1], (tab[2] or "")[:100]))
                if len(picks) >= 8:
                    break
            if picks:
                parts.append("最近 track/decide（勿重复做同一件事）:")
                parts.extend(reversed(picks))
    except Exception:
        pass
    # evolution_self_proposed 已完成
    try:
        esp = os.path.join(ROOT, "references", "evolution_self_proposed.md")
        if os.path.isfile(esp):
            n = 0
            with open(esp, "r", encoding="utf-8") as f:
                for line in f:
                    if "已完成" in line and "|" in line:
                        parts.append("已完成项: " + line.strip()[:150])
                        n += 1
                        if n >= 5:
                            break
    except Exception:
        pass
    parts.append("请基于上述与 behavior_log 全文，只做**尚未完成**的下一步；若已全部完成则写 decide 说明本轮无新动作。")
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser(description="Submit one evolution loop task to CCR /api/agent")
    ap.add_argument("--once", action="store_true", default=True, help="Run once (default)")
    ap.add_argument("--message", "-m", type=str, default=None, help="Override evolution_prompt")
    ap.add_argument("--user-hint-file", type=str, default=None, help="Append content as user hint to prompt")
    ap.add_argument("--auto-evolution", action="store_true", help="自动进化环：附带上一轮摘要，减少重复")
    args = ap.parse_args()

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
