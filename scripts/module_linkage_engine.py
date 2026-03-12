#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能模块联动推理引擎

功能：
- 分析用户请求，智能识别需要哪些模块协同工作
- 实现跨模块联动推理，根据上下文和系统状态动态组合模块
- 记录模块联动历史到 runtime/state/module_linkage_history.json
- 作为统一入口，提供一站式模块协同体验
- 让系统具备"1+1>2"的智能联动能力

模块联动规则：
- 用户请求 -> 意图识别 -> 需要哪些模块 -> 依次/并行调用 -> 综合响应
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

# 可用智能模块注册表
AVAILABLE_MODULES = {
    # 核心智能模块
    "intent_recognition": {
        "script": "intent_recognition.py",
        "purpose": "意图识别与推荐",
        "keywords": ["推荐", "建议", "干嘛", "好玩的", "无聊", "有啥"]
    },
    "active_suggestion": {
        "script": "active_suggestion_engine.py",
        "purpose": "主动建议推送",
        "keywords": ["主动建议", "智能建议", "现在能做什么"]
    },
    "context_memory": {
        "script": "context_memory.py",
        "purpose": "上下文记忆与意图预测",
        "keywords": ["记忆", "之前", "上次", "历史", "上下文"]
    },
    "emotional_interaction": {
        "script": "emotional_interaction.py",
        "purpose": "情感交互",
        "keywords": ["情感", "心情", "开心", "难过", "疲惫", "无聊"]
    },
    "scenario_followup": {
        "script": "scenario_followup_recommender.py",
        "purpose": "场景后续建议",
        "keywords": ["然后", "接下来", "之后", "后续"]
    },
    "user_behavior": {
        "script": "user_behavior_learner.py",
        "purpose": "用户行为学习",
        "keywords": ["习惯", "偏好", "学习", "通常"]
    },
    "coordinator": {
        "script": "coordinator.py",
        "purpose": "任务协调中心",
        "keywords": ["协调", "处理", "任务"]
    },
    "workflow_orchestrator": {
        "script": "workflow_orchestrator.py",
        "purpose": "工作流编排",
        "keywords": ["工作流", "编排", "流程"]
    },
    "nl_automation": {
        "script": "nl_automation.py",
        "purpose": "自然语言自动化",
        "keywords": ["自动", "帮我", "做", "执行"]
    },
}

def get_system_state():
    """获取当前系统状态用于推理"""
    state = {
        "timestamp": datetime.now().isoformat(),
        "time": datetime.now().strftime("%H:%M"),
        "hour": datetime.now().hour,
        "is_working_hours": 9 <= datetime.now().hour < 18,
        "is_morning": 6 <= datetime.now().hour < 12,
        "is_afternoon": 12 <= datetime.now().hour < 18,
        "is_evening": 18 <= datetime.now().hour < 22,
        "is_night": 22 <= datetime.now().hour or datetime.now().hour < 6,
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

    # 读取用户行为学习状态
    behavior_file = STATE_DIR / "user_behavior.json"
    if behavior_file.exists():
        try:
            with open(behavior_file, "r", encoding="utf-8") as f:
                behavior_data = json.load(f)
                state["has_user_behavior"] = len(behavior_data) > 0
                state["frequent_tasks"] = list(behavior_data.keys())[:3] if behavior_data else []
        except:
            pass

    return state

def analyze_required_modules(user_input, system_state):
    """分析用户请求，识别需要联动哪些模块"""
    user_input_lower = user_input.lower()

    # 模块关键词匹配
    required_modules = []
    reason = []

    for module_name, module_info in AVAILABLE_MODULES.items():
        for keyword in module_info["keywords"]:
            if keyword in user_input_lower:
                required_modules.append(module_name)
                reason.append(f"匹配关键词: {keyword}")
                break

    # 如果没有匹配到任何模块，基于系统状态进行推理
    if not required_modules:
        # 默认联动：意图识别 + 主动建议
        required_modules = ["intent_recognition", "active_suggestion"]
        reason.append("无明确模块匹配，启用默认联动")

        # 根据时间推荐
        if system_state.get("is_morning"):
            reason.append("早晨时段，优先提供工作建议")
        elif system_state.get("is_evening"):
            reason.append("晚间时段，优先提供休闲建议")

        # 如果用户有学习到的行为，加入行为模块
        if system_state.get("has_user_behavior"):
            required_modules.append("user_behavior")
            reason.append("用户有历史行为数据")

        # 如果用户刚完成某个任务，加入后续建议模块
        history_file = STATE_DIR / "coordinator_history.json"
        if history_file.exists():
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
                    if history and len(history) > 0:
                        required_modules.append("scenario_followup")
                        reason.append("有历史任务记录，可提供后续建议")
            except:
                pass

    # 去重
    required_modules = list(dict.fromkeys(required_modules))

    return {
        "modules": required_modules,
        "reason": reason,
        "inference": "基于关键词匹配和系统状态推理"
    }

def call_module(module_name, user_input, system_state):
    """调用指定模块并获取结果"""
    if module_name not in AVAILABLE_MODULES:
        return {"error": f"未知模块: {module_name}"}

    module_info = AVAILABLE_MODULES[module_name]
    script_path = SCRIPT_DIR / module_info["script"]

    if not script_path.exists():
        return {"error": f"模块脚本不存在: {module_info['script']}"}

    try:
        # 根据不同模块构造调用参数
        if module_name == "intent_recognition":
            result = subprocess.run(
                [sys.executable, str(script_path), user_input],
                capture_output=True,
                text=True,
                timeout=30
            )
        elif module_name == "active_suggestion":
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
        elif module_name == "context_memory":
            # 上下文记忆需要查询最近记忆
            result = subprocess.run(
                [sys.executable, str(script_path), "search", user_input],
                capture_output=True,
                text=True,
                timeout=30
            )
        elif module_name == "emotional_interaction":
            result = subprocess.run(
                [sys.executable, str(script_path), user_input],
                capture_output=True,
                text=True,
                timeout=30
            )
        elif module_name == "scenario_followup":
            # 场景后续建议需要获取最近场景
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
        elif module_name == "user_behavior":
            result = subprocess.run(
                [sys.executable, str(script_path), "stats"],
                capture_output=True,
                text=True,
                timeout=30
            )
        elif module_name == "coordinator":
            result = subprocess.run(
                [sys.executable, str(script_path), "status"],
                capture_output=True,
                text=True,
                timeout=30
            )
        elif module_name == "workflow_orchestrator":
            result = subprocess.run(
                [sys.executable, str(script_path), "list"],
                capture_output=True,
                text=True,
                timeout=30
            )
        elif module_name == "nl_automation":
            result = subprocess.run(
                [sys.executable, str(script_path), "execute", user_input],
                capture_output=True,
                text=True,
                timeout=60
            )
        else:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=30
            )

        if result.returncode == 0:
            output = result.stdout.strip()
            # 尝试解析 JSON
            try:
                if output:
                    return {"success": True, "data": json.loads(output), "module": module_name}
            except:
                return {"success": True, "data": output, "module": module_name}
        else:
            return {"success": False, "error": result.stderr, "module": module_name}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "模块执行超时", "module": module_name}
    except Exception as e:
        return {"success": False, "error": str(e), "module": module_name}

def synthesize_response(module_results, required_modules):
    """综合各模块结果，生成联动响应"""
    if not module_results:
        return {"response": "无法获取有效结果", "summary": {}}

    summary = {}
    combined_response = []

    for result in module_results:
        module_name = result.get("module", "unknown")
        if result.get("success"):
            data = result.get("data", {})
            summary[module_name] = "成功"
            # 提取关键信息
            if isinstance(data, dict):
                combined_response.append({
                    "module": module_name,
                    "highlights": extract_highlights(data)
                })
            elif isinstance(data, str):
                combined_response.append({
                    "module": module_name,
                    "content": data[:200]  # 限制长度
                })
        else:
            summary[module_name] = f"失败: {result.get('error', '未知错误')}"

    return {
        "response": "联动推理完成",
        "summary": summary,
        "details": combined_response,
        "modules_count": len(required_modules)
    }

def extract_highlights(data):
    """从模块结果中提取关键信息"""
    highlights = []

    # 尝试提取常见字段
    if isinstance(data, dict):
        for key in ["recommendations", "suggestions", "intent", "result", "status", "output"]:
            if key in data:
                highlights.append({key: data[key]})

    return highlights[:3]  # 最多3个

def record_linkage_history(user_input, required_modules, module_results, response):
    """记录模块联动历史"""
    ensure_dir(STATE_DIR)
    history_file = STATE_DIR / "module_linkage_history.json"

    history = []
    if history_file.exists():
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        except:
            history = []

    # 添加新记录
    record = {
        "timestamp": datetime.now().isoformat(),
        "user_input": user_input,
        "modules": required_modules,
        "results": {
            m.get("module", "unknown"): m.get("success", False)
            for m in module_results
        },
        "response": response.get("response", "")
    }

    history.append(record)

    # 保留最近50条
    history = history[-50:]

    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def execute_linkage(user_input):
    """执行模块联动推理主流程"""
    # 1. 获取系统状态
    system_state = get_system_state()

    # 2. 分析需要哪些模块
    required = analyze_required_modules(user_input, system_state)
    required_modules = required["modules"]

    # 3. 依次调用各模块
    module_results = []
    for module_name in required_modules:
        result = call_module(module_name, user_input, system_state)
        module_results.append(result)

    # 4. 综合响应
    response = synthesize_response(module_results, required_modules)

    # 5. 记录历史
    record_linkage_history(user_input, required_modules, module_results, response)

    return {
        "user_input": user_input,
        "system_state": {
            "time": system_state.get("time"),
            "is_working_hours": system_state.get("is_working_hours")
        },
        "inference": required,
        "response": response
    }

def show_status():
    """显示模块联动引擎状态"""
    # 检查各模块是否存在
    modules_status = {}
    for name, info in AVAILABLE_MODULES.items():
        script_path = SCRIPT_DIR / info["script"]
        modules_status[name] = {
            "exists": script_path.exists(),
            "purpose": info["purpose"]
        }

    # 读取历史记录数
    history_file = STATE_DIR / "module_linkage_history.json"
    history_count = 0
    if history_file.exists():
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
                history_count = len(history)
        except:
            pass

    return {
        "available_modules": len(AVAILABLE_MODULES),
        "modules_status": modules_status,
        "history_count": history_count,
        "capabilities": [
            "意图识别联动",
            "主动建议联动",
            "上下文记忆联动",
            "情感交互联动",
            "后续建议联动",
            "用户行为联动",
            "工作流编排联动",
            "自然语言自动化联动"
        ]
    }

def main():
    if len(sys.argv) < 2:
        # 默认显示状态
        result = show_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    command = sys.argv[1]

    if command in ["status", "s"]:
        # 显示状态
        result = show_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "execute" and len(sys.argv) > 2:
        # 执行联动推理
        user_input = " ".join(sys.argv[2:])
        result = execute_linkage(user_input)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "test":
        # 测试联动
        test_inputs = [
            "有啥好玩的建议吗",
            "我现在应该做什么",
            "我之前在做什么"
        ]
        results = []
        for test_input in test_inputs:
            result = execute_linkage(test_input)
            results.append({
                "input": test_input,
                "modules": result["inference"]["modules"],
                "success": all(m.get("success", False) for m in result["response"].get("details", []))
            })

        print(json.dumps(results, ensure_ascii=False, indent=2))

    elif command in ["help", "h", "-h", "--help"]:
        print("""
智能模块联动推理引擎

用法:
  python module_linkage_engine.py [command] [args]

命令:
  status/s              显示模块联动引擎状态
  execute <input>       执行模块联动推理
  test                  测试联动推理
  help                  显示帮助

示例:
  python module_linkage_engine.py status
  python module_linkage_engine.py execute 好无聊推荐点东西
  python module_linkage_engine.py test
        """)

    else:
        # 默认为 execute
        user_input = command + " " + " ".join(sys.argv[2:]) if len(sys.argv) > 2 else command
        result = execute_linkage(user_input)
        print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()