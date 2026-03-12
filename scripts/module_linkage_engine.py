#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能模块联动推理引擎（增强版）

功能：
- 分析用户请求，智能识别需要哪些模块协同工作
- 实现跨模块联动推理，根据上下文和系统状态动态组合模块
- 记录模块联动历史到 runtime/state/module_linkage_history.json
- 作为统一入口，提供一站式模块协同体验
- 让系统具备"1+1>2"的智能联动能力
- 集成跨模块状态共享总线，增强模块间协同能力
- 新增：智能场景模式识别、动态引擎编排、引擎协同效果评估
- 新增：安全卫士集成、跨模块上下文传递、结果智能聚合

模块联动规则：
- 用户请求 -> 意图识别 -> 需要哪些模块 -> 依次/并行调用 -> 综合响应
"""

# 智能场景模式定义
COMPLEX_SCENARIOS = {
    "文件整理+通知": {
        "modules": ["file_manager", "proactive_notification"],
        "description": "整理文件后发送通知",
        "sequential": True
    },
    "学习+推荐": {
        "modules": ["adaptive_learning", "scenario_recommender", "active_suggestion"],
        "description": "基于学习到的习惯推荐场景",
        "sequential": False
    },
    "情感+对话": {
        "modules": ["emotion_engine", "conversation_manager"],
        "description": "情感识别后进行上下文对话",
        "sequential": True
    },
    "情境感知+主动推荐": {
        "modules": ["context_awareness", "scenario_recommender", "proactive_notification"],
        "description": "感知环境后主动推荐",
        "sequential": True
    },
    "诊断+自愈": {
        "modules": ["self_healing", "system_health"],
        "description": "健康检测后自动修复",
        "sequential": True
    },
    "多引擎协同": {
        "modules": ["decision_orchestrator", "workflow_engine", "emotion_engine"],
        "description": "复杂任务的多引擎协同",
        "sequential": False
    },
    "语音+情感+TTS": {
        "modules": ["voice_interaction", "emotion_engine", "tts_engine"],
        "description": "语音交互完整流程",
        "sequential": True
    },
    "早晨工作准备": {
        "modules": ["context_awareness", "scenario_recommender", "adaptive_learning"],
        "description": "早晨自动推荐工作任务",
        "sequential": True
    },
    "晚间放松推荐": {
        "modules": ["context_awareness", "active_suggestion", "proactive_notification"],
        "description": "晚间推荐放松活动",
        "sequential": True
    },
    "复杂任务规划": {
        "modules": ["workflow_engine", "decision_orchestrator", "context_awareness"],
        "description": "复杂任务智能规划与执行",
        "sequential": False
    }
}

# 引擎协同效果评分（用于优化调度）
ENGINE_COLLABORATION_SCORES = {}

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

# 可用智能模块注册表（增强版 - 增加更多引擎联动）
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
    # 增强协同能力 - 新增模块联动
    "decision_orchestrator": {
        "script": "decision_orchestrator.py",
        "purpose": "决策编排中心 - 多引擎协同调度",
        "keywords": ["决策", "编排", "协同", "调度", "智能调度", "multi-engine"]
    },
    "self_healing": {
        "script": "self_healing_engine.py",
        "purpose": "问题诊断与自愈",
        "keywords": ["诊断", "自愈", "问题检测", "健康检测", "修复"]
    },
    "proactive_notification": {
        "script": "proactive_notification_engine.py",
        "purpose": "主动通知引擎",
        "keywords": ["通知", "提醒", "主动建议", "提醒我"]
    },
    "adaptive_learning": {
        "script": "adaptive_learning_engine.py",
        "purpose": "学习与适应引擎",
        "keywords": ["学习", "适应", "个性化", "习惯"]
    },
    "workflow_engine": {
        "script": "workflow_engine.py",
        "purpose": "智能工作流引擎",
        "keywords": ["工作流", "任务规划", "复杂任务"]
    },
    "file_manager": {
        "script": "file_manager_engine.py",
        "purpose": "智能文件管理引擎",
        "keywords": ["文件管理", "整理文件", "搜索文件", "分析文件"]
    },
    "scenario_recommender": {
        "script": "scenario_recommender.py",
        "purpose": "智能场景推荐引擎",
        "keywords": ["场景推荐", "推荐场景", "推荐计划"]
    },
    "voice_interaction": {
        "script": "voice_interaction_engine.py",
        "purpose": "语音交互引擎",
        "keywords": ["语音", "语音交互", "语音命令", "voice"]
    },
    "tts_engine": {
        "script": "tts_engine.py",
        "purpose": "语音合成引擎",
        "keywords": ["语音合成", "语音回复", "tts", "读出来"]
    },
    "conversation_manager": {
        "script": "conversation_manager.py",
        "purpose": "智能对话管理引擎",
        "keywords": ["对话", "多轮对话", "上下文", "对话历史"]
    },
    "emotion_engine": {
        "script": "emotion_engine.py",
        "purpose": "智能情感识别与响应引擎",
        "keywords": ["情感识别", "情绪感知", "情感分析"]
    },
    "context_awareness": {
        "script": "context_awareness_engine.py",
        "purpose": "智能情境感知引擎",
        "keywords": ["情境感知", "环境感知", "当前状态", "主动推荐"]
    },
    "system_health": {
        "script": "system_health_monitor.py",
        "purpose": "系统健康监控引擎",
        "keywords": ["系统监控", "健康监控", "系统状态", "性能监控"]
    },
    "evolution_coordinator": {
        "script": "evolution_coordinator.py",
        "purpose": "进化协调器",
        "keywords": ["进化", "协调进化", "统一进化"]
    },
    "evolution_strategy": {
        "script": "evolution_strategy_engine.py",
        "purpose": "进化策略引擎",
        "keywords": ["进化策略", "策略分析"]
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

def detect_complex_scenario(user_input, system_state):
    """检测是否匹配复杂场景模式"""
    user_input_lower = user_input.lower()
    matched_scenarios = []

    # 场景关键词映射
    scenario_keywords = {
        "文件整理+通知": ["整理文件", "整理文件夹", "整理桌面", "发通知"],
        "学习+推荐": ["推荐", "习惯", "根据我的习惯"],
        "情感+对话": ["情感", "心情", "和我聊聊"],
        "情境感知+主动推荐": ["现在能做什么", "当前状态", "推荐"],
        "诊断+自愈": ["检查", "诊断", "健康", "修复"],
        "语音+情感+TTS": ["语音", "说话", "读出来"],
        "早晨工作准备": ["早上好", "早晨", "工作准备"],
        "晚间放松推荐": ["晚上好", "放松", "休息"],
        "复杂任务规划": ["规划", "帮我做", "复杂任务"],
    }

    for scenario_name, keywords in scenario_keywords.items():
        if any(kw in user_input_lower for kw in keywords):
            matched_scenarios.append(scenario_name)

    # 时间段自动推断
    if system_state.get("is_morning") and "早晨" not in user_input:
        if "推荐" in user_input or "建议" in user_input or "干嘛" in user_input:
            matched_scenarios.append("早晨工作准备")
    elif system_state.get("is_evening") and "晚间" not in user_input:
        if "推荐" in user_input or "放松" in user_input:
            matched_scenarios.append("晚间放松推荐")

    return matched_scenarios


def optimize_engine_order(modules, scenario_name=None):
    """优化引擎执行顺序"""
    # 优先级映射
    priority_map = {
        "context_awareness": 1,  # 需要先感知环境
        "emotion_engine": 2,     # 情感需要先识别
        "adaptive_learning": 3,  # 学习数据需要提前
        "decision_orchestrator": 4,  # 决策需要前置信息
        "scenario_recommender": 5,   # 推荐需要决策后
        "active_suggestion": 6,      # 主动建议
        "proactive_notification": 7,  # 通知最后
        "workflow_engine": 4,         # 工作流需要决策
    }

    # 按优先级排序
    sorted_modules = sorted(modules, key=lambda m: priority_map.get(m, 10))
    return sorted_modules


def evaluate_collaboration(modules_used, results, system_state):
    """评估引擎协同效果"""
    success_count = sum(1 for r in results if r.get("success", False))
    total = len(results)
    success_rate = success_count / total if total > 0 else 0

    # 计算评分
    score = {
        "success_rate": success_rate,
        "modules_count": len(modules_used),
        "efficiency": "high" if success_rate >= 0.8 else "medium" if success_rate >= 0.5 else "low",
        "timestamp": datetime.now().isoformat()
    }

    # 更新协同评分缓存
    for module in modules_used:
        if module not in ENGINE_COLLABORATION_SCORES:
            ENGINE_COLLABORATION_SCORES[module] = []
        ENGINE_COLLABORATION_SCORES[module].append(success_rate)

    return score


def check_safety_guardian(user_input, modules):
    """检查是否需要安全卫士介入"""
    safety_keywords = ["删除", "格式化", "关机", "重启", "结束进程", "清空", "危险"]
    user_input_lower = user_input.lower()

    # 如果有危险操作且调用了文件管理或进程管理等模块
    needs_check = any(kw in user_input_lower for kw in safety_keywords)

    if needs_check and any(m in modules for m in ["file_manager", "coordinator", "self_healing"]):
        # 调用安全卫士检查
        safety_script = SCRIPT_DIR / "safety_guardian.py"
        if safety_script.exists():
            try:
                result = subprocess.run(
                    [sys.executable, str(safety_script), "check", user_input],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    return {"required": True, "message": "已通过安全卫士检查"}
            except:
                pass

    return {"required": False, "message": "无需安全检查"}


def execute_enhanced_linkage(user_input):
    """执行增强版模块联动推理"""
    # 1. 获取系统状态
    system_state = get_system_state()

    # 2. 检测复杂场景
    complex_scenarios = detect_complex_scenario(user_input, system_state)

    # 3. 分析需要哪些模块
    required = analyze_required_modules(user_input, system_state)
    required_modules = required["modules"]

    # 如果匹配复杂场景，扩展需要的模块
    if complex_scenarios:
        for scenario in complex_scenarios:
            if scenario in COMPLEX_SCENARIOS:
                scenario_modules = COMPLEX_SCENARIOS[scenario]["modules"]
                for mod in scenario_modules:
                    if mod not in required_modules:
                        required_modules.append(mod)

    # 4. 安全卫士检查
    safety_check = check_safety_guardian(user_input, required_modules)
    if safety_check.get("required"):
        required_modules.append("safety_guardian")

    # 5. 优化引擎执行顺序
    required_modules = optimize_engine_order(required_modules)

    # 6. 依次调用各模块
    module_results = []
    for module_name in required_modules:
        result = call_module(module_name, user_input, system_state)
        module_results.append(result)

    # 7. 评估协同效果
    collaboration_score = evaluate_collaboration(required_modules, module_results, system_state)

    # 8. 综合响应
    response = synthesize_response(module_results, required_modules)
    response["collaboration_score"] = collaboration_score
    response["complex_scenarios"] = complex_scenarios

    # 9. 记录历史
    record_linkage_history(user_input, required_modules, module_results, response)

    return {
        "user_input": user_input,
        "system_state": {
            "time": system_state.get("time"),
            "is_working_hours": system_state.get("is_working_hours"),
            "is_morning": system_state.get("is_morning"),
            "is_evening": system_state.get("is_evening")
        },
        "inference": required,
        "complex_scenarios_detected": complex_scenarios,
        "optimized_order": required_modules,
        "safety_check": safety_check,
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
        "complex_scenarios": len(COMPLEX_SCENARIOS),
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
            "自然语言自动化联动",
            "智能场景模式识别",
            "动态引擎编排优化",
            "安全卫士集成",
            "协同效果评估"
        ],
        "complex_scenarios_list": list(COMPLEX_SCENARIOS.keys())
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

    elif command in ["execute", "run", "e"] and len(sys.argv) > 2:
        # 执行增强版联动推理
        user_input = " ".join(sys.argv[2:])
        result = execute_enhanced_linkage(user_input)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "enhanced" and len(sys.argv) > 2:
        # 明确执行增强版
        user_input = " ".join(sys.argv[2:])
        result = execute_enhanced_linkage(user_input)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "scenarios":
        # 列出复杂场景
        print(json.dumps(COMPLEX_SCENARIOS, ensure_ascii=False, indent=2))

    elif command == "test":
        # 测试增强版联动
        test_inputs = [
            "有啥好玩的建议吗",
            "我现在应该做什么",
            "我之前在做什么",
            "早上好推荐今天的工作",
            "晚上好推荐点放松的"
        ]
        results = []
        for test_input in test_inputs:
            result = execute_enhanced_linkage(test_input)
            results.append({
                "input": test_input,
                "modules": result["inference"]["modules"],
                "complex_scenarios": result.get("complex_scenarios_detected", []),
                "optimized_order": result.get("optimized_order", []),
                "success": all(m.get("success", False) for m in result["response"].get("details", []))
            })

        print(json.dumps(results, ensure_ascii=False, indent=2))

    elif command in ["help", "h", "-h", "--help"]:
        print("""
智能模块联动推理引擎（增强版）

用法:
  python module_linkage_engine.py [command] [args]

命令:
  status/s              显示模块联动引擎状态
  execute <input>       执行增强版模块联动推理
  enhanced <input>      执行增强版模块联动推理（同execute）
  scenarios             列出复杂场景模式
  test                  测试增强版联动推理
  help                  显示帮助

新增功能:
  - 智能场景模式识别（10种复杂场景）
  - 动态引擎编排优化
  - 安全卫士集成
  - 协同效果评估
  - 时间感知的自动场景推荐

示例:
  python module_linkage_engine.py status
  python module_linkage_engine.py execute 好无聊推荐点东西
  python module_linkage_engine.py scenarios
  python module_linkage_engine.py test
        """)

    else:
        # 默认为 execute（增强版）
        user_input = command + " " + " ".join(sys.argv[2:]) if len(sys.argv) > 2 else command
        result = execute_enhanced_linkage(user_input)
        print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()