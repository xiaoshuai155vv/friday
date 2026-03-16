#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-OS 智能工作流编排引擎

本模块实现复杂任务的智能编排能力，基于用户自然语言输入自动理解任务意图、
拆分为可执行的子任务、跨模块协同调度执行、实时追踪进度并汇总结果。

版本: 1.0.0
功能:
1. 意图理解 - 解析用户的自然语言复杂任务
2. 任务拆分 - 将复杂任务智能拆分为可执行的子任务序列
3. 跨应用协同 - 自动调度 LLM-OS 各模块协同工作
4. 执行编排 - 按依赖关系排序执行步骤，处理并行与串行任务
5. 进度追踪 - 实时监控工作流执行状态，处理异常与回退
6. 结果汇总 - 执行完成后生成执行报告

依赖: llm_os_control_panel, llm_os_scene_auto_discovery, llm_os_user_behavior_prediction 等
"""

import os
import sys
import json
import sqlite3
import subprocess
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import threading
import time

# 脚本目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(SCRIPT_DIR, "..", "runtime", "state")
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "runtime", "data")


def get_db_path():
    """获取工作流数据库路径"""
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, "workflow_orchestrator.db")


def init_db():
    """初始化工作流数据库"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # 工作流定义表
    c.execute('''CREATE TABLE IF NOT EXISTS workflows (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        task_type TEXT,
        created_at TEXT NOT NULL,
        last_executed TEXT,
        execution_count INTEGER DEFAULT 0,
        success_rate REAL DEFAULT 0.0
    )''')

    # 任务步骤表
    c.execute('''CREATE TABLE IF NOT EXISTS workflow_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        workflow_id INTEGER NOT NULL,
        step_order INTEGER NOT NULL,
        task_name TEXT NOT NULL,
        task_type TEXT NOT NULL,
        module_name TEXT,
        parameters TEXT,
        depends_on TEXT,
        status TEXT DEFAULT 'pending',
        result TEXT,
        error TEXT,
        started_at TEXT,
        completed_at TEXT,
        FOREIGN KEY (workflow_id) REFERENCES workflows(id)
    )''')

    # 执行历史表
    c.execute('''CREATE TABLE IF NOT EXISTS execution_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        workflow_id INTEGER NOT NULL,
        started_at TEXT NOT NULL,
        completed_at TEXT,
        status TEXT,
        result_summary TEXT,
        details TEXT,
        FOREIGN KEY (workflow_id) REFERENCES workflows(id)
    )''')

    # 任务模板表
    c.execute('''CREATE TABLE IF NOT EXISTS task_templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        keywords TEXT,
        task_type TEXT NOT NULL,
        module_name TEXT,
        default_params TEXT,
        description TEXT
    )''')

    conn.commit()
    conn.close()
    return db_path


def get_module_path(module_name):
    """获取模块路径"""
    return os.path.join(SCRIPT_DIR, module_name)


def execute_module(module_name, action, params=None):
    """执行指定模块"""
    module_path = get_module_path(module_name)
    if not os.path.exists(module_path):
        return {"success": False, "error": f"Module {module_name} not found"}

    cmd = [sys.executable, module_path, action]
    if params:
        for k, v in params.items():
            cmd.extend([f"--{k}", str(v)])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            encoding='utf-8',
            errors='replace'
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else None
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Execution timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def parse_natural_language_task(task_text):
    """
    解析自然语言任务，识别意图和关键信息
    返回: (task_type, entities, requirements)
    """
    task_text = task_text.lower()

    # 定义任务模式模板
    task_patterns = {
        "file_organize": {
            "keywords": ["整理", "归类", "分类", "排序", "整理文件", "文件整理"],
            "entities": {"target": None, "category": None, "path": None},
            "requirements": ["source_path", "target_path"]
        },
        "meeting_schedule": {
            "keywords": ["会议", "安排会议", "预约会议", "会议通知"],
            "entities": {"title": None, "time": None, "participants": None},
            "requirements": ["title", "time"]
        },
        "report_generation": {
            "keywords": ["报告", "生成报告", "工作报告", "汇总", "总结报告"],
            "entities": {"period": None, "type": None, "content": None},
            "requirements": ["period", "type"]
        },
        "app_automation": {
            "keywords": ["打开", "启动", "关闭", "运行", "执行"],
            "entities": {"app": None, "action": None},
            "requirements": ["app"]
        },
        "data_processing": {
            "keywords": ["处理", "转换", "提取", "分析", "批量"],
            "entities": {"input": None, "operation": None, "output": None},
            "requirements": ["input", "operation"]
        },
        "system_maintenance": {
            "keywords": ["清理", "优化", "维护", "清理", "释放"],
            "entities": {"target": None, "scope": None},
            "requirements": ["target"]
        }
    }

    # 匹配任务类型
    matched_type = None
    matched_score = 0

    for task_type, pattern_info in task_patterns.items():
        score = sum(1 for kw in pattern_info["keywords"] if kw in task_text)
        if score > matched_score:
            matched_score = score
            matched_type = task_type

    if not matched_type:
        matched_type = "general_task"

    # 提取实体信息
    entities = {}

    # 提取时间信息
    time_patterns = [
        (r"(\d{1,2})[月/-](\d{1,2})[号/日]?", "date"),
        (r"(今天|明天|后天|下周|本周|下周)", "relative_date"),
        (r"(上午|下午|早上|晚上|早晨)(\d{1,2})[点时]?", "time_of_day"),
        (r"(\d{1,2})[点时](?:(\d{1,2})分)?", "specific_time")
    ]

    for pattern, etype in time_patterns:
        match = re.search(pattern, task_text)
        if match:
            entities[etype] = match.group(0)

    # 提取文件路径
    path_patterns = [
        (r"[A-Za-z]:\\[^\s]+", "windows_path"),
        (r"/[^\s]+", "unix_path")
    ]

    for pattern, ptype in path_patterns:
        match = re.search(pattern, task_text)
        if match:
            entities["path"] = match.group(0)
            break

    # 提取应用名称
    common_apps = ["微信", "钉钉", "飞书", "Outlook", "Notepad", "Excel", "Word",
                   "PowerPoint", "浏览器", "Chrome", "Edge", "QQ", "邮箱", "邮件"]
    for app in common_apps:
        if app.lower() in task_text or app in task_text:
            entities["app"] = app
            break

    return matched_type, entities, task_patterns.get(matched_type, {}).get("requirements", [])


def generate_task_sequence(task_type, entities, requirements):
    """
    根据任务类型和实体生成任务步骤序列
    返回: [(step_name, module, action, params), ...]
    """
    task_sequences = {
        "file_organize": [
            ("scan_source_dir", "file_tool", "list", {"path": entities.get("path", ".")}),
            ("analyze_files", "llm_os_file_manager", "analyze", {}),
            ("organize_files", "llm_os_file_manager", "organize", {"path": entities.get("path", ".")})
        ],
        "meeting_schedule": [
            ("check_calendar", "llm_os_notification_center", "check", {}),
            ("create_meeting", "llm_os_notification_center", "schedule", {
                "title": entities.get("title", "会议"),
                "time": entities.get("time", "")
            }),
            ("send_notification", "notification_tool", "show", {
                "title": entities.get("title", "会议通知"),
                "message": "会议已安排"
            })
        ],
        "report_generation": [
            ("collect_data", "llm_os_file_manager", "list", {}),
            ("analyze_data", "llm_os_system_monitor", "status", {}),
            ("generate_report", "file_tool", "write", {
                "path": os.path.join(STATE_DIR, "report.txt"),
                "content": "报告内容"
            })
        ],
        "app_automation": [
            ("check_app", "installed_apps_tool", "list", {}),
            ("launch_app", "llm_os_app_launcher", "launch", {"app": entities.get("app", "")}),
            ("verify_launch", "window_tool", "list", {})
        ],
        "data_processing": [
            ("read_input", "file_tool", "read", {"path": entities.get("input", "")}),
            ("process_data", "llm_os_core_engine", "process", {}),
            ("save_output", "file_tool", "write", {
                "path": entities.get("output", ""),
                "content": ""
            })
        ],
        "system_maintenance": [
            ("check_system", "llm_os_system_monitor", "status", {}),
            ("optimize", "llm_os_settings", "optimize", {}),
            ("cleanup", "llm_os_clipboard_manager", "clear", {})
        ],
        "general_task": [
            ("analyze_task", "llm_os_control_panel", "status", {}),
            ("execute_task", "llm_os_control_panel", "execute", {})
        ]
    }

    return task_sequences.get(task_type, task_sequences["general_task"])


def create_workflow(name, description, task_type, task_sequence):
    """创建工作流"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    now = datetime.now().isoformat()

    # 插入工作流
    c.execute('''INSERT INTO workflows (name, description, task_type, created_at, execution_count)
                 VALUES (?, ?, ?, ?, 0)''', (name, description, task_type, now))

    workflow_id = c.lastrowid

    # 插入任务步骤
    for idx, (step_name, module, action, params) in enumerate(task_sequence):
        c.execute('''INSERT INTO workflow_tasks
                     (workflow_id, step_order, task_name, task_type, module_name, parameters, status)
                     VALUES (?, ?, ?, ?, ?, ?, 'pending')''',
                  (workflow_id, idx, step_name, action, module, json.dumps(params)))

    conn.commit()
    conn.close()

    return workflow_id


def execute_workflow(workflow_id, context=None):
    """执行工作流"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # 获取工作流信息
    c.execute("SELECT * FROM workflows WHERE id = ?", (workflow_id,))
    workflow = c.fetchone()

    if not workflow:
        conn.close()
        return {"success": False, "error": "Workflow not found"}

    # 获取任务步骤
    c.execute('''SELECT id, step_order, task_name, task_type, module_name, parameters, depends_on
                 FROM workflow_tasks WHERE workflow_id = ? ORDER BY step_order''',
              (workflow_id,))
    tasks = c.fetchall()

    # 创建执行记录
    started_at = datetime.now().isoformat()
    c.execute('''INSERT INTO execution_history (workflow_id, started_at, status)
                 VALUES (?, ?, 'running')''', (workflow_id, started_at))
    execution_id = c.lastrowid
    conn.commit()

    results = []
    task_results = {}

    # 按依赖关系执行任务
    for task in tasks:
        task_id, step_order, task_name, task_type, module_name, params_str, depends_on = task

        # 检查依赖是否满足
        if depends_on:
            dep_task = json.loads(depends_on)
            for dep in dep_task:
                if dep not in task_results or not task_results[dep].get("success", False):
                    # 更新任务状态为 blocked
                    c.execute("UPDATE workflow_tasks SET status = 'blocked' WHERE id = ?", (task_id,))
                    conn.commit()
                    continue

        # 更新任务状态为 running
        c.execute("UPDATE workflow_tasks SET status = 'running', started_at = ? WHERE id = ?",
                  (datetime.now().isoformat(), task_id))
        conn.commit()

        # 执行任务
        params = json.loads(params_str) if params_str else {}
        if context:
            params.update(context)

        result = execute_module(module_name, task_type, params)

        # 更新任务结果
        completed_at = datetime.now().isoformat()
        status = "completed" if result.get("success", False) else "failed"

        c.execute('''UPDATE workflow_tasks
                     SET status = ?, result = ?, error = ?, completed_at = ?
                     WHERE id = ?''',
                  (status, json.dumps(result), result.get("error"), completed_at, task_id))

        task_results[task_name] = result
        results.append({
            "task": task_name,
            "status": status,
            "result": result
        })

        conn.commit()

        # 如果任务失败且不可跳过，则停止执行
        if not result.get("success", False):
            break

    # 更新执行记录
    completed_at = datetime.now().isoformat()
    overall_status = "completed" if all(r.get("status") == "completed" for r in results) else "failed"

    c.execute('''UPDATE execution_history
                 SET completed_at = ?, status = ?, result_summary = ?
                 WHERE id = ?''',
              (completed_at, overall_status, json.dumps(results), execution_id))

    # 更新工作流统计
    c.execute('''UPDATE workflows
                 SET last_executed = ?, execution_count = execution_count + 1
                 WHERE id = ?''', (completed_at, workflow_id))

    conn.commit()
    conn.close()

    return {
        "success": overall_status == "completed",
        "workflow_id": workflow_id,
        "execution_id": execution_id,
        "status": overall_status,
        "results": results
    }


def get_workflow_status(workflow_id):
    """获取工作流状态"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # 获取工作流信息
    c.execute("SELECT * FROM workflows WHERE id = ?", (workflow_id,))
    workflow = c.fetchone()

    if not workflow:
        conn.close()
        return None

    # 获取任务步骤
    c.execute('''SELECT step_order, task_name, task_type, status, result, error, started_at, completed_at
                 FROM workflow_tasks WHERE workflow_id = ? ORDER BY step_order''',
              (workflow_id,))
    tasks = c.fetchall()

    conn.close()

    return {
        "workflow": {
            "id": workflow[0],
            "name": workflow[1],
            "description": workflow[2],
            "task_type": workflow[3],
            "created_at": workflow[4],
            "last_executed": workflow[5],
            "execution_count": workflow[6],
            "success_rate": workflow[7]
        },
        "tasks": [
            {
                "step_order": t[0],
                "task_name": t[1],
                "task_type": t[2],
                "status": t[3],
                "result": json.loads(t[4]) if t[4] else None,
                "error": t[5],
                "started_at": t[6],
                "completed_at": t[7]
            }
            for t in tasks
        ]
    }


def list_workflows():
    """列出所有工作流"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("SELECT id, name, description, task_type, created_at, execution_count, success_rate FROM workflows")
    workflows = c.fetchall()

    conn.close()

    return [
        {
            "id": w[0],
            "name": w[1],
            "description": w[2],
            "task_type": w[3],
            "created_at": w[4],
            "execution_count": w[5],
            "success_rate": w[6]
        }
        for w in workflows
    ]


def analyze_complex_task(task_text):
    """
    分析复杂任务，返回任务分解建议
    """
    task_type, entities, requirements = parse_natural_language_task(task_text)
    task_sequence = generate_task_sequence(task_type, entities, requirements)

    return {
        "task_type": task_type,
        "entities": entities,
        "requirements": requirements,
        "task_count": len(task_sequence),
        "estimated_duration": len(task_sequence) * 30,  # 假设每步30秒
        "suggested_steps": [
            {
                "step": idx + 1,
                "name": step[0],
                "module": step[1],
                "action": step[2],
                "params": step[3]
            }
            for idx, step in enumerate(task_sequence)
        ]
    }


def create_and_execute_workflow(task_text, context=None):
    """
    创建并执行工作流的便捷函数
    """
    # 分析任务
    analysis = analyze_complex_task(task_text)

    # 创建工作流
    workflow_id = create_workflow(
        name=f"Workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        description=task_text,
        task_type=analysis["task_type"],
        task_sequence=[(s["name"], s["module"], s["action"], s["params"]) for s in analysis["suggested_steps"]]
    )

    # 执行工作流
    result = execute_workflow(workflow_id, context)

    return {
        "analysis": analysis,
        "workflow_id": workflow_id,
        "execution": result
    }


def get_statistics():
    """获取工作流编排统计"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # 工作流总数
    c.execute("SELECT COUNT(*) FROM workflows")
    total_workflows = c.fetchone()[0]

    # 执行总数
    c.execute("SELECT COUNT(*) FROM execution_history")
    total_executions = c.fetchone()[0]

    # 成功率
    c.execute("SELECT COUNT(*) FROM execution_history WHERE status = 'completed'")
    successful_executions = c.fetchone()[0]

    # 平均执行时间
    c.execute('''SELECT AVG((julianday(completed_at) - julianday(started_at)) * 86400)
                 FROM execution_history WHERE completed_at IS NOT NULL''')
    avg_duration = c.fetchone()[0] or 0

    conn.close()

    return {
        "total_workflows": total_workflows,
        "total_executions": total_executions,
        "successful_executions": successful_executions,
        "success_rate": successful_executions / total_executions if total_executions > 0 else 0,
        "average_duration_seconds": avg_duration
    }


def main():
    """主函数 - 命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="LLM-OS 智能工作流编排引擎")
    parser.add_argument("--init", action="store_true", help="初始化数据库")
    parser.add_argument("--analyze", type=str, help="分析任务并返回分解建议")
    parser.add_argument("--create", type=str, help="创建工作流")
    parser.add_argument("--execute", type=int, help="执行工作流（指定workflow_id）")
    parser.add_argument("--status", type=int, help="查看工作流状态")
    parser.add_argument("--list", action="store_true", help="列出所有工作流")
    parser.add_argument("--stats", action="store_true", help="查看统计信息")

    args = parser.parse_args()

    # 初始化
    if args.init:
        db_path = init_db()
        print(f"数据库初始化完成: {db_path}")
        return

    # 分析任务
    if args.analyze:
        result = analyze_complex_task(args.analyze)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 创建工作流
    if args.create:
        result = create_and_execute_workflow(args.create)
        print(json.dumps({
            "workflow_id": result["workflow_id"],
            "execution_status": result["execution"]["status"]
        }, ensure_ascii=False, indent=2))
        return

    # 执行工作流
    if args.execute:
        result = execute_workflow(args.execute)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 查看状态
    if args.status:
        result = get_workflow_status(args.status)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 列出工作流
    if args.list:
        result = list_workflows()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 统计信息
    if args.stats:
        result = get_statistics()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 默认显示帮助
    parser.print_help()


if __name__ == "__main__":
    main()