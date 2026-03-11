#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自主校验能力链：截图、鼠标、键盘、子进程链、剪贴板（已知远程会话可能失败）、vision（可选）。
供闭环「完成校验」阶段调用，不向用户汇报，结果写 runtime/state/self_verify_result.json。

注意：
- 本脚本是**基线烟测**（底座未坏），不替代「本轮假设/执行产出的能力」的针对性校验；针对性校验见 workflow「自主校验审核」。
- 不启动记事本等 GUI 应用，避免每次校验都弹窗；应用启动能力由场景 plan 或人工抽检覆盖。
"""
import sys
import os
import json
import subprocess

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPTS)
STATE_DIR = os.path.join(PROJECT, "runtime", "state")
RESULT_FILE = os.path.join(STATE_DIR, "self_verify_result.json")

def run(cmd_list, cwd=None, timeout=15):
    try:
        r = subprocess.run(
            cmd_list, cwd=cwd or PROJECT,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=timeout
        )
        return r.returncode == 0, (r.stdout or "").strip(), (r.stderr or "").strip()
    except subprocess.TimeoutExpired:
        return False, "", "timeout"
    except Exception as e:
        return False, "", str(e)

def main():
    os.makedirs(STATE_DIR, exist_ok=True)
    os.makedirs(os.path.join(PROJECT, "runtime", "screenshots"), exist_ok=True)
    result = {"items": [], "all_ok": True, "updated_at": ""}
    from datetime import datetime, timezone
    result["updated_at"] = datetime.now(timezone.utc).isoformat()

    # 1. 截图
    path_bmp = os.path.join(PROJECT, "runtime", "screenshots", "self_verify.bmp")
    ok, out, err = run([sys.executable, os.path.join(SCRIPTS, "screenshot_tool.py"), path_bmp])
    if ok and os.path.isfile(path_bmp):
        result["items"].append({"name": "screenshot", "ok": True, "detail": path_bmp})
    else:
        result["items"].append({"name": "screenshot", "ok": False, "detail": err or out})
        result["all_ok"] = False

    # 2. 鼠标位置
    ok, out, err = run([sys.executable, os.path.join(SCRIPTS, "mouse_tool.py"), "pos"])
    has_xy = ok and out and len(out.split()) >= 2 and out.replace(" ", "").replace("\n", "").isdigit() or (out.strip() and any(c.isdigit() for c in out))
    if ok:
        result["items"].append({"name": "mouse_pos", "ok": True, "detail": out[:80]})
    else:
        result["items"].append({"name": "mouse_pos", "ok": False, "detail": err or out})
        result["all_ok"] = False

    # 3. 键盘（发一个无害键 VK_CAPITAL 20 或 0）
    ok, out, err = run([sys.executable, os.path.join(SCRIPTS, "keyboard_tool.py"), "key", "0"])
    result["items"].append({"name": "keyboard", "ok": ok, "detail": err or out or "key 0 sent"})
    if not ok:
        result["all_ok"] = False

    # 4. 子进程/脚本链（无 GUI：screen_size 仅读屏尺寸，不弹窗；原 launch_notepad 已去掉，避免每次校验都打开记事本）
    ok, out, err = run([sys.executable, os.path.join(SCRIPTS, "screen_size.py")], timeout=8)
    result["items"].append({"name": "script_chain", "ok": ok, "detail": (out or err or "ok")[:80]})
    if not ok:
        result["all_ok"] = False

    # 5. 剪贴板（读写一轮；失败不拉低 all_ok，因可能被其他进程占用）
    ok, out, err = run([sys.executable, os.path.join(SCRIPTS, "clipboard_tool.py"), "set", "FRIDAY_verify"])
    if ok:
        ok2, out2, err2 = run([sys.executable, os.path.join(SCRIPTS, "clipboard_tool.py"), "get"])
        if ok2 and "FRIDAY_verify" in (out2 or ""):
            result["items"].append({"name": "clipboard", "ok": True, "detail": "get/set OK"})
        else:
            result["items"].append({"name": "clipboard", "ok": False, "detail": err2 or out2 or "get mismatch"})
    else:
        result["items"].append({"name": "clipboard", "ok": False, "detail": err or out})

    # 6. vision（可选：无配置则跳过）
    if os.path.isfile(path_bmp):
        cfg = os.path.join(SCRIPTS, "vision_config.json")
        if os.path.isfile(cfg) or os.environ.get("VISION_API_KEY") or os.environ.get("OPENAI_API_KEY"):
            ok, out, err = run(
                [sys.executable, os.path.join(SCRIPTS, "vision_proxy.py"), path_bmp, "画面里有什么？一句话。"],
                timeout=30
            )
            result["items"].append({"name": "vision", "ok": ok, "detail": (out or err)[:120]})
            if not ok:
                result["all_ok"] = False
        else:
            result["items"].append({"name": "vision", "ok": None, "detail": "skip: no vision_config"})

    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return 0 if result["all_ok"] else 1

if __name__ == "__main__":
    sys.exit(main())
