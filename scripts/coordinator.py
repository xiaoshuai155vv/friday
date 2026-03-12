#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能任务协调中心

功能：
- 协调多个智能模块（意图识别、场景匹配、策略选择、执行、健康建议）协同工作
- 接收用户任务请求，统一调度各模块
- 记录任务执行轨迹到 runtime/state/coordinator_history.json
- 作为统一入口，提供一站式任务处理体验
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# 确保 scripts 目录在路径中
SCRIPT_DIR = Path(__file__).parent
RUNTIME_DIR = SCRIPT_DIR.parent / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"

def ensure_dir(path):
    """确保目录存在"""
    path = Path(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    return path

def get_system_state():
    """获取当前系统状态"""
    state = {
        "timestamp": datetime.now().isoformat(),
        "time": datetime.now().strftime("%H:%M"),
        "is_working_hours": 9 <= datetime.now().hour < 18,
    }

    # 读取番茄钟状态
    focus_state_file = STATE_DIR / "focus_state.json"
    if focus_state_file.exists():
        try:
            with open(focus_state_file, "r", encoding="utf-8") as f:
                focus_data = json.load(f)
                state["focus_mode"] = focus_data.get("active", False)
                state["focus_remaining"] = focus_data.get("remaining_minutes", 0)
        except:
            pass

    # 读取健康检查状态
    health_file = STATE_DIR / "health_daemon_status.json"
    if health_file.exists():
        try:
            with open(health_file, "r", encoding="utf-8") as f:
                health_data = json.load(f)
                state["health_status"] = health_data.get("last_status", "unknown")
        except:
            pass

    return state

def recognize_intent(user_input):
    """调用意图识别模块"""
    script_path = SCRIPT_DIR / "intent_recognition.py"
    if not script_path.exists():
        return {"intent": "unknown", "confidence": 0, "recommendations": []}

    try:
        result = subprocess.run(
            [sys.executable, str(script_path), user_input],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0 and result.stdout:
            try:
                # 尝试从输出中解析推荐结果
                output = result.stdout
                # 读取 intent_recommendations.json
                rec_file = STATE_DIR / "intent_recommendations.json"
                if rec_file.exists():
                    with open(rec_file, "r", encoding="utf-8") as f:
                        return json.load(f)
            except:
                pass
    except:
        pass
    return {"intent": "unknown", "confidence": 0, "recommendations": []}

def get_execution_strategy(task_type):
    """获取任务执行策略"""
    script_path = SCRIPT_DIR / "task_execution_strategy.py"
    if not script_path.exists():
        return {"retry": 3, "wait": 2, "priority": "normal"}

    try:
        result = subprocess.run(
            [sys.executable, str(script_path), task_type],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0 and result.stdout:
            return json.loads(result.stdout)
    except:
        pass
    return {"retry": 3, "wait": 2, "priority": "normal"}

def match_scenario(intent_data, user_input):
    """根据意图匹配场景计划"""
    recommendations = intent_data.get("recommendations", [])
    plans_dir = SCRIPT_DIR.parent / "assets" / "plans"

    if not recommendations:
        return None

    for rec in recommendations:
        plan_name = rec.get("plan")
        if plan_name:
            plan_file = plans_dir / plan_name
            if plan_file.exists():
                return {"plan": plan_name, "path": str(plan_file), "reason": rec.get("reason", "")}

    return None

def execute_plan(plan_path):
    """执行场景计划"""
    script_path = SCRIPT_DIR / "run_plan.py"
    if not script_path.exists():
        return {"success": False, "error": "run_plan.py not found"}

    try:
        result = subprocess.run(
            [sys.executable, str(script_path), plan_path],
            capture_output=True,
            text=True,
            timeout=300
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout[:500] if result.stdout else "",
            "error": result.stderr[:200] if result.stderr else ""
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def generate_followup(task_result, context):
    """生成后续建议"""
    script_path = SCRIPT_DIR / "scenario_followup_recommender.py"
    if not script_path.exists():
        return []

    try:
        # 获取场景名称用于后续建议
        scenario = context.get("matched_plan", "general")
        result = subprocess.run(
            [sys.executable, str(script_path), scenario],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            rec_file = STATE_DIR / "scenario_followup_suggestions.json"
            if rec_file.exists():
                with open(rec_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("suggestions", [])
    except:
        pass
    return []

def save_coordinator_history(task_data):
    """保存任务历史"""
    history_file = STATE_DIR / "coordinator_history.json"
    ensure_dir(STATE_DIR)

    history = []
    if history_file.exists():
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        except:
            pass

    # 限制历史记录数量（保留最近100条）
    history = history[-99:] + [task_data]

    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def coordinate(user_input):
    """
    协调多模块处理用户任务
    返回处理结果
    """
    task_record = {
        "timestamp": datetime.now().isoformat(),
        "user_input": user_input,
        "steps": []
    }

    # 步骤1: 获取系统状态
    system_state = get_system_state()
    task_record["system_state"] = system_state
    task_record["steps"].append({"step": "get_system_state", "status": "done"})

    # 步骤2: 意图识别
    intent_data = recognize_intent(user_input)
    task_record["intent"] = intent_data
    task_record["steps"].append({"step": "recognize_intent", "status": "done"})

    # 步骤3: 策略选择
    task_type = intent_data.get("intent", "general")
    strategy = get_execution_strategy(task_type)
    task_record["strategy"] = strategy
    task_record["steps"].append({"step": "get_execution_strategy", "status": "done"})

    # 步骤4: 场景匹配
    matched = match_scenario(intent_data, user_input)
    task_record["matched_plan"] = matched.get("plan") if matched else None
    task_record["steps"].append({"step": "match_scenario", "status": "done", "result": matched})

    # 步骤5: 执行（如有匹配计划）
    result = None
    if matched:
        plan_path = matched.get("path")
        result = execute_plan(plan_path)
        task_record["execution_result"] = result
        task_record["steps"].append({"step": "execute_plan", "status": "done", "result": result})
    else:
        task_record["steps"].append({"step": "execute_plan", "status": "skipped", "reason": "no matching plan"})

    # 步骤6: 生成后续建议
    if result and result.get("success"):
        followups = generate_followup(result, task_record)
        task_record["followup_suggestions"] = followups

    task_record["steps"].append({"step": "generate_followup", "status": "done"})

    # 保存历史
    save_coordinator_history(task_record)

    # 输出结果摘要
    print("=" * 50)
    print("智能任务协调中心")
    print("=" * 50)
    print(f"输入: {user_input}")
    print(f"识别意图: {intent_data.get('intent', 'unknown')}")
    print(f"匹配计划: {matched.get('plan') if matched else '无'}")
    if result:
        print(f"执行结果: {'成功' if result.get('success') else '失败'}")
    if task_record.get("followup_suggestions"):
        print("后续建议:")
        for i, s in enumerate(task_record["followup_suggestions"][:3], 1):
            print(f"  {i}. {s}")
    print("=" * 50)

    return task_record

def show_status():
    """显示协调中心状态"""
    system_state = get_system_state()

    print("=" * 50)
    print("智能任务协调中心 - 状态")
    print("=" * 50)
    print(f"当前时间: {system_state.get('time', 'unknown')}")
    print(f"工作时间: {'是' if system_state.get('is_working_hours') else '否'}")
    print(f"专注模式: {'开启' if system_state.get('focus_mode') else '未开启'}")
    print(f"健康状态: {system_state.get('health_status', 'unknown')}")
    print("=" * 50)

    # 显示最近任务
    history_file = STATE_DIR / "coordinator_history.json"
    if history_file.exists():
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
                if history:
                    print("\n最近任务:")
                    for task in history[-5:]:
                        print(f"  - {task.get('user_input', 'unknown')} -> {task.get('matched_plan', '无匹配')}")
        except:
            pass

def main():
    if len(sys.argv) < 2:
        show_status()
        print("\n用法:")
        print("  python coordinator.py <用户输入>  - 处理用户任务")
        print("  python coordinator.py status      - 显示状态")
        print("  python coordinator.py history     - 显示历史")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "status":
        show_status()
    elif cmd == "history":
        history_file = STATE_DIR / "coordinator_history.json"
        if history_file.exists():
            with open(history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
                print(json.dumps(history[-10:], ensure_ascii=False, indent=2))
        else:
            print("暂无历史记录")
    else:
        # 将所有参数作为用户输入
        user_input = " ".join(sys.argv[1:])
        coordinate(user_input)

if __name__ == "__main__":
    main()