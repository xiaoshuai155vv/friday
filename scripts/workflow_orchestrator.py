#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能任务编排与工作流自动化模块 (workflow_orchestrator.py)

功能：
1. 解析用户意图为多步骤工作流
2. 支持场景计划编排、依赖管理、顺序执行
3. 记录工作流执行历史
4. 与现有模块（coordinator、intent_recognition 等）联动

集成到 do.py，支持关键词：
- 工作流编排、执行工作流、创建工作流、运行工作流
"""

import json
import os
import re
import sys
import subprocess
from datetime import datetime
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE = PROJECT_ROOT / "runtime" / "state"
LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"

# 确保目录存在
RUNTIME_STATE.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

HISTORY_FILE = RUNTIME_STATE / "workflow_history.json"
ACTIVE_WORKFLOW_FILE = RUNTIME_STATE / "active_workflow.json"


def load_history():
    """加载工作流执行历史"""
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"workflows": [], "last_updated": None}
    return {"workflows": [], "last_updated": None}


def save_history(history):
    """保存工作流执行历史"""
    history["last_updated"] = datetime.now().isoformat()
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def load_plans():
    """加载所有场景计划"""
    plans_dir = PROJECT_ROOT / "assets" / "plans"
    plans = {}
    if plans_dir.exists():
        for f in plans_dir.glob("*.json"):
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    plan_data = json.load(fp)
                    plans[f.stem] = plan_data
            except Exception:
                pass
    return plans


def get_available_modules():
    """获取所有可用的脚本模块"""
    scripts_dir = PROJECT_ROOT / "scripts"
    modules = []

    if scripts_dir.exists():
        for f in scripts_dir.glob("*.py"):
            if f.stem not in ["__init__", "workflow_orchestrator"]:
                modules.append(f.stem)

    return modules


def analyze_dependencies(steps):
    """
    分析步骤之间的依赖关系，确定执行顺序

    Args:
        steps: 步骤列表

    Returns:
        排序后的步骤列表（已解决依赖顺序）
    """
    # 定义常见的依赖关系规则
    dependencies = {
        "activate": ["screenshot", "vision", "click", "type"],
        "maximize": ["screenshot", "vision", "click"],
        "screenshot": ["vision", "vision_coords"],
    }

    # 简单的依赖分析：检查步骤类型
    sorted_steps = []
    executed_types = set()

    for step in steps:
        step_type = step.get("type", "")
        # 检查是否有未满足的依赖
        if step_type in dependencies:
            required = dependencies[step_type]
            if not any(dep in executed_types for dep in required):
                # 插入需要的步骤
                for req in required:
                    if req not in executed_types and req in [s.get("type", "") for s in steps]:
                        # 找到对应步骤并添加
                        for s in steps:
                            if s.get("type") == req and s not in sorted_steps:
                                sorted_steps.append(s)
                                executed_types.add(req)

        if step not in sorted_steps:
            sorted_steps.append(step)
            executed_types.add(step_type)

    return sorted_steps if sorted_steps else steps


def auto_generate_steps(user_intent):
    """
    根据用户意图自动生成执行步骤

    Args:
        user_intent: 用户意图描述

    Returns:
        步骤列表
    """
    intent_lower = user_intent.lower()
    steps = []
    modules = get_available_modules()

    # 意图到模块的映射
    intent_module_map = {
        # 文件操作
        ("文件", "文件夹", "管理"): ["file_tool", "file_metadata", "file_watcher"],
        ("监控", "文件夹监控"): ["file_watcher"],
        ("元数据", "标签"): ["file_metadata"],
        ("预览", "查看"): ["quick_look"],

        # 系统操作
        ("电源", "节能", "高性能"): ["power_plan_tool"],
        ("剪贴板", "复制", "粘贴"): ["clipboard_tool", "clipboard_history"],
        ("托盘", "图标"): ["tray_icon_tool"],
        ("任务", "调度", "定时"): ["task_scheduler"],

        # 健康与状态
        ("健康", "检查", "诊断"): ["system_health_check", "health_check_daemon", "auto_fixer"],
        ("趋势", "预测"): ["trend_predictor"],
        ("日志", "分析"): ["execution_log_analyzer"],
        ("仪表板", "状态"): ["dashboard"],

        # 情感与交互
        ("情感", "心情"): ["emotional_interaction"],
        ("意图", "推荐"): ["intent_recognition"],
        ("行为", "习惯", "学习"): ["user_behavior_learner"],
        ("建议", "主动"): ["active_suggestion_engine"],

        # 协调与工作流
        ("协调", "中心"): ["coordinator"],
        ("编排", "工作流"): ["workflow_orchestrator"],

        # 专注与时间
        ("番茄", "专注", "提醒"): ["focus_reminder"],

        # 拍照与摄像头
        ("自拍", "摄像头", "拍照"): ["selfie", "camera_qt"],

        # iHaier
        ("消息", "邮件", "联系人"): ["window_tool", "launch_browser"],

        # 浏览器
        ("浏览器", "打开网页", "访问"): ["launch_browser"],
    }

    # 检测意图关键词并添加对应步骤
    for keywords, target_modules in intent_module_map.items():
        if any(kw in intent_lower for kw in keywords):
            for mod in target_modules:
                if mod in modules:
                    steps.append({
                        "type": "execute",
                        "module": mod,
                        "description": f"执行{mod}模块"
                    })

    # 如果没有匹配到任何模块，添加默认步骤
    if not steps:
        steps = [
            {"type": "execute", "module": "intent_recognition", "description": "解析用户意图"},
            {"type": "execute", "module": "coordinator", "description": "智能协调处理"}
        ]

    return steps


def smart_plan_task(user_intent, intent_recognition_module=None):
    """
    智能规划任务：将用户意图自动拆分为多个子任务并生成执行计划

    Args:
        user_intent: 用户意图描述
        intent_recognition_module: 可选的意图识别模块

    Returns:
        包含智能规划结果的工作流定义
    """
    # 1. 首先尝试使用内置工作流模板
    workflow = parse_intent_to_workflow(user_intent, intent_recognition_module)

    # 2. 如果工作流只有默认步骤，则尝试智能生成
    if len(workflow.get("steps", [])) <= 2:
        generated_steps = auto_generate_steps(user_intent)
        if generated_steps:
            workflow["steps"] = generated_steps

    # 3. 分析依赖并优化执行顺序
    if workflow.get("steps"):
        workflow["steps"] = analyze_dependencies(workflow["steps"])

    # 4. 添加元数据
    workflow["smart_planned"] = True
    workflow["planned_at"] = datetime.now().isoformat()
    workflow["intent"] = user_intent

    return workflow


def parse_intent_to_workflow(user_intent, intent_recognition_module=None):
    """
    解析用户意图为工作流

    Args:
        user_intent: 用户输入的意图描述
        intent_recognition_module: 可选的意图识别模块

    Returns:
        工作流定义字典
    """
    intent_lower = user_intent.lower()

    # 内置工作流模板
    workflows = {
        "早晨准备": {
            "name": "早晨准备",
            "description": "一系列早上常用的任务：看天气、听音乐、查看消息",
            "steps": [
                {"type": "plan", "plan": "check_weather", "description": "查看天气"},
                {"type": "plan", "plan": "play_music", "description": "播放音乐"},
                {"type": "plan", "plan": "ihaier_unread", "description": "查看未读消息"}
            ]
        },
        "工作总结": {
            "name": "工作总结",
            "description": "生成今日工作总结：查看代码提交、健康状态、系统状态",
            "steps": [
                {"type": "command", "command": "git log --oneline -10", "description": "查看最近提交"},
                {"type": "plan", "plan": "system_health_check", "description": "检查系统健康"},
                {"type": "plan", "plan": "dashboard", "description": "查看状态面板"}
            ]
        },
        "任务处理": {
            "name": "任务处理",
            "description": "处理多个任务：先检查待办，然后逐个处理",
            "steps": [
                {"type": "plan", "plan": "check_todos", "description": "查看待办事项"},
                {"type": "execute", "module": "coordinator", "description": "智能处理任务"}
            ]
        }
    }

    # 简单关键词匹配
    for key, workflow in workflows.items():
        if key in intent_lower or any(kw in intent_lower for kw in key):
            return workflow

    # 默认返回通用工作流
    return {
        "name": user_intent,
        "description": f"执行用户请求: {user_intent}",
        "steps": [
            {"type": "execute", "module": "intent_recognition", "description": "解析用户意图"},
            {"type": "execute", "module": "coordinator", "description": "智能处理"}
        ]
    }


def execute_workflow(workflow, dry_run=False):
    """
    执行工作流

    Args:
        workflow: 工作流定义
        dry_run: 是否仅预览不执行

    Returns:
        执行结果字典
    """
    results = {
        "workflow": workflow.get("name", "未命名工作流"),
        "started_at": datetime.now().isoformat(),
        "steps": [],
        "status": "running" if not dry_run else "dry_run"
    }

    if dry_run:
        results["steps"] = [
            {
                "step": i+1,
                "description": step.get("description", ""),
                "type": step.get("type", "unknown"),
                "status": "preview"
            }
            for i, step in enumerate(workflow.get("steps", []))
        ]
        results["status"] = "dry_run_completed"
        results["completed_at"] = datetime.now().isoformat()
        return results

    # 顺序执行每个步骤
    for i, step in enumerate(workflow.get("steps", [])):
        step_result = {
            "step": i+1,
            "description": step.get("description", ""),
            "type": step.get("type", "unknown"),
            "status": "pending"
        }

        step_type = step.get("type", "")

        try:
            if step_type == "plan":
                # 执行场景计划
                plan_name = step.get("plan", "")
                if plan_name:
                    plan_path = PROJECT_ROOT / "assets" / "plans" / f"{plan_name}.json"
                    if plan_path.exists():
                        result = subprocess.run(
                            [sys.executable, str(PROJECT_ROOT / "scripts" / "run_plan.py"), str(plan_path)],
                            capture_output=True, text=True, timeout=300
                        )
                        step_result["output"] = result.stdout[:500] if result.stdout else ""
                        step_result["returncode"] = result.returncode
                        step_result["status"] = "success" if result.returncode == 0 else "failed"
                    else:
                        step_result["status"] = "skipped"
                        step_result["note"] = f"计划 {plan_name} 不存在"
                else:
                    step_result["status"] = "skipped"

            elif step_type == "command":
                # 执行命令
                cmd = step.get("command", "")
                if cmd:
                    result = subprocess.run(
                        cmd, shell=True, capture_output=True, text=True, timeout=60
                    )
                    step_result["output"] = result.stdout[:500] if result.stdout else ""
                    step_result["returncode"] = result.returncode
                    step_result["status"] = "success" if result.returncode == 0 else "failed"
                else:
                    step_result["status"] = "skipped"

            elif step_type == "execute":
                # 调用其他模块
                module = step.get("module", "")
                if module == "intent_recognition":
                    # 调用意图识别
                    intent_path = RUNTIME_STATE / "intent_recommendations.json"
                    if intent_path.exists():
                        with open(intent_path, "r", encoding="utf-8") as f:
                            step_result["data"] = json.load(f)
                        step_result["status"] = "success"
                    else:
                        step_result["status"] = "skipped"
                        step_result["note"] = "意图识别结果不存在"
                elif module == "coordinator":
                    # 调用协调中心
                    coord_path = RUNTIME_STATE / "coordinator_history.json"
                    if coord_path.exists():
                        with open(coord_path, "r", encoding="utf-8") as f:
                            step_result["data"] = json.load(f)
                        step_result["status"] = "success"
                    else:
                        step_result["status"] = "skipped"
                        step_result["note"] = "协调中心历史不存在"
                else:
                    step_result["status"] = "skipped"
                    step_result["note"] = f"未知模块: {module}"

            else:
                step_result["status"] = "skipped"
                step_result["note"] = f"未知步骤类型: {step_type}"

        except subprocess.TimeoutExpired:
            step_result["status"] = "failed"
            step_result["note"] = "执行超时"
        except Exception as e:
            step_result["status"] = "failed"
            step_result["note"] = str(e)[:100]

        results["steps"].append(step_result)

    # 计算总体状态
    all_steps = results["steps"]
    if all_steps:
        statuses = [s.get("status", "") for s in all_steps]
        if all(s == "success" for s in statuses):
            results["status"] = "completed"
        elif any(s == "failed" for s in statuses):
            results["status"] = "partial_failure"
        else:
            results["status"] = "completed"

    results["completed_at"] = datetime.now().isoformat()

    return results


def list_workflows():
    """列出所有可用的工作流"""
    # 内置工作流
    builtin = {
        "早晨准备": "一系列早上常用的任务：看天气、听音乐、查看消息",
        "工作总结": "生成今日工作总结：查看代码提交、健康状态、系统状态",
        "任务处理": "处理多个任务：先检查待办，然后逐个处理"
    }

    # 用户自定义工作流（从历史中提取）
    history = load_history()
    user_workflows = {}

    for wf in history.get("workflows", []):
        name = wf.get("name", "")
        if name and name not in user_workflows:
            user_workflows[name] = wf.get("description", "")

    return {
        "builtin": builtin,
        "user_defined": user_workflows
    }


def status():
    """查看工作流状态"""
    history = load_history()
    active = None

    if ACTIVE_WORKFLOW_FILE.exists():
        try:
            with open(ACTIVE_WORKFLOW_FILE, "r", encoding="utf-8") as f:
                active = json.load(f)
        except Exception:
            pass

    return {
        "history_count": len(history.get("workflows", [])),
        "last_run": history.get("last_updated"),
        "active_workflow": active
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="智能任务编排与工作流自动化模块")
    parser.add_argument("action", nargs="?", choices=["list", "run", "status", "create", "plan", "analyze"], help="操作类型")
    parser.add_argument("--intent", "-i", help="用户意图描述")
    parser.add_argument("--workflow", "-w", help="工作流名称")
    parser.add_argument("--dry-run", "-d", action="store_true", help="仅预览不执行")
    parser.add_argument("--steps", "-s", help="工作流步骤（JSON 数组）")
    parser.add_argument("--smart", action="store_true", help="启用智能规划模式")

    args = parser.parse_args()

    if args.action == "analyze":
        # 智能分析用户意图
        if not args.intent:
            print("错误: --analyze 需要 --intent 参数")
            return

        print(f"=== 智能分析: {args.intent} ===\n")

        # 智能规划任务
        workflow = smart_plan_task(args.intent)
        steps = workflow.get("steps", [])

        print(f"工作流名称: {workflow.get('name', '未命名')}")
        print(f"描述: {workflow.get('description', '')}")
        print(f"智能规划: {'是' if workflow.get('smart_planned') else '否'}")
        print(f"生成步骤数: {len(steps)}")
        print()

        # 依赖分析
        print("--- 步骤详情 ---")
        for i, step in enumerate(steps, 1):
            step_type = step.get("type", "unknown")
            desc = step.get("description", "")
            module = step.get("module", "")
            plan = step.get("plan", "")
            cmd = step.get("command", "")

            print(f"\n步骤 {i}:")
            print(f"  类型: {step_type}")
            print(f"  描述: {desc}")

            if module:
                print(f"  模块: {module}")
            if plan:
                print(f"  计划: {plan}")
            if cmd:
                print(f"  命令: {cmd}")

        # 输出为 JSON 格式供程序使用
        print("\n--- JSON 输出 ---")
        print(json.dumps(workflow, ensure_ascii=False, indent=2))

    elif args.action == "plan" or args.smart:
        # 智能规划模式
        if not args.intent:
            print("错误: --plan 或 --smart 需要 --intent 参数")
            return

        print(f"=== 智能规划任务: {args.intent} ===\n")

        # 使用智能规划
        workflow = smart_plan_task(args.intent)

        print(f"工作流名称: {workflow.get('name', '未命名')}")
        print(f"描述: {workflow.get('description', '')}")
        print(f"智能规划: {'是' if workflow.get('smart_planned') else '否'}")
        print(f"步骤数: {len(workflow.get('steps', []))}")
        print()

        # 预览步骤
        print("--- 执行步骤预览 ---")
        for i, step in enumerate(workflow.get("steps", []), 1):
            step_type = step.get("type", "unknown")
            desc = step.get("description", "")

            if step_type == "execute":
                module = step.get("module", "")
                print(f"  {i}. [{step_type}] {desc} → 执行模块: {module}")
            elif step_type == "plan":
                plan = step.get("plan", "")
                print(f"  {i}. [{step_type}] {desc} → 运行计划: {plan}")
            elif step_type == "command":
                cmd = step.get("command", "")
                print(f"  {i}. [{step_type}] {desc} → 命令: {cmd}")
            else:
                print(f"  {i}. [{step_type}] {desc}")

        # 询问是否执行
        if not args.dry_run:
            print("\n使用 --dry-run 参数可仅预览不执行")

    elif args.action == "list" or args.action is None and not args.intent:
        # 列出可用工作流
        workflows = list_workflows()
        print("=== 可用工作流 ===")
        print("\n内置工作流:")
        for name, desc in workflows.get("builtin", {}).items():
            print(f"  - {name}: {desc}")
        if workflows.get("user_defined"):
            print("\n用户自定义工作流:")
            for name, desc in workflows.get("user_defined", {}).items():
                print(f"  - {name}: {desc}")

    elif args.action == "status":
        # 查看状态
        st = status()
        print("=== 工作流状态 ===")
        print(f"历史执行次数: {st['history_count']}")
        print(f"最后运行时间: {st['last_run'] or '无'}")
        if st.get("active_workflow"):
            print(f"当前活动工作流: {st['active_workflow'].get('name', '未知')}")

    elif args.action == "run" or args.intent:
        # 执行工作流
        if args.workflow:
            # 指定了工作流名称
            workflows = list_workflows()
            all_workflows = {**workflows.get("builtin", {}), **workflows.get("user_defined", {})}
            if args.workflow in all_workflows:
                workflow = {"name": args.workflow, "description": all_workflows[args.workflow]}
                if args.workflow == "早晨准备":
                    workflow = {
                        "name": "早晨准备",
                        "description": "一系列早上常用的任务",
                        "steps": [
                            {"type": "plan", "plan": "check_weather", "description": "查看天气"},
                            {"type": "plan", "plan": "play_music", "description": "播放音乐"},
                            {"type": "plan", "plan": "ihaier_unread", "description": "查看未读消息"}
                        ]
                    }
                elif args.workflow == "工作总结":
                    workflow = {
                        "name": "工作总结",
                        "description": "生成今日工作总结",
                        "steps": [
                            {"type": "command", "command": "git log --oneline -10", "description": "查看最近提交"},
                            {"type": "plan", "plan": "system_health_check", "description": "检查系统健康"},
                            {"type": "plan", "plan": "dashboard", "description": "查看状态面板"}
                        ]
                    }
                elif args.workflow == "任务处理":
                    workflow = {
                        "name": "任务处理",
                        "description": "处理多个任务",
                        "steps": [
                            {"type": "execute", "module": "intent_recognition", "description": "解析用户意图"},
                            {"type": "execute", "module": "coordinator", "description": "智能处理"}
                        ]
                    }
            else:
                print(f"错误: 未找到工作流 '{args.workflow}'")
                print("使用 'workflow_orchestrator.py list' 查看可用工作流")
                return
        else:
            # 解析用户意图
            user_intent = args.intent or "通用任务"
            workflow = parse_intent_to_workflow(user_intent)

        print(f"=== 执行工作流: {workflow.get('name', '未命名')} ===")
        print(f"描述: {workflow.get('description', '')}")
        print(f"步骤数: {len(workflow.get('steps', []))}")
        print()

        # 执行工作流
        result = execute_workflow(workflow, dry_run=args.dry_run)

        if args.dry_run:
            print("--- 预览模式 ---")
            for step in result.get("steps", []):
                print(f"  {step['step']}. {step['description']} ({step['type']})")
        else:
            print("--- 执行结果 ---")
            for step in result.get("steps", []):
                status_icon = "✓" if step.get("status") == "success" else "✗" if step.get("status") == "failed" else "○"
                print(f"  {status_icon} 步骤 {step['step']}: {step['description']} - {step.get('status', 'unknown')}")
                if step.get("note"):
                    print(f"      备注: {step['note']}")

            print(f"\n总体状态: {result.get('status', 'unknown')}")
            print(f"开始时间: {result.get('started_at', '')}")
            print(f"完成时间: {result.get('completed_at', '')}")

            # 保存到历史
            history = load_history()
            history["workflows"].append(result)
            # 只保留最近 50 条
            history["workflows"] = history["workflows"][-50:]
            save_history(history)
            print(f"\n已保存到执行历史 (共 {len(history['workflows'])} 条)")

    elif args.action == "create":
        # 创建新工作流
        if not args.steps:
            print("错误: 创建工作流需要 --steps 参数指定步骤 (JSON 数组)")
            return

        try:
            steps = json.loads(args.steps)
            workflow = {
                "name": args.workflow or "自定义工作流",
                "description": f"用户创建的工作流，包含 {len(steps)} 个步骤",
                "steps": steps,
                "created_at": datetime.now().isoformat()
            }

            # 保存到历史（作为用户自定义工作流）
            history = load_history()
            history["workflows"].append(workflow)
            save_history(history)
            print(f"工作流 '{workflow['name']}' 已创建")
        except json.JSONDecodeError as e:
            print(f"错误: JSON 解析失败 - {e}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()