#!/usr/bin/env python3
"""
进化闭环自动化引擎
将 evolution_strategy_engine、evolution_log_analyzer、evolution_self_evaluator 三个模块联动，
实现自动化的分析→决策→执行→评估循环
"""

import os
import json
import subprocess
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# 添加 scripts 目录到路径
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

def parse_json_output(output: str) -> Dict[str, Any]:
    """安全解析 JSON 输出，处理模块输出的额外文本"""
    if not output:
        return {"error": "empty_output"}

    # 查找 JSON 开始位置
    json_start = output.find('{')
    if json_start == -1:
        return {"error": "no_json_found", "output": output}

    json_str = output[json_start:]

    # 尝试解析，找不到完整的 JSON 就逐字符尝试
    for i in range(len(json_str), 0, -1):
        try:
            return json.loads(json_str[:i])
        except json.JSONDecodeError:
            continue

    # 如果完全解析失败，查找最后一个 } 位置
    last_brace = json_str.rfind('}')
    if last_brace != -1:
        try:
            return json.loads(json_str[:last_brace+1])
        except json.JSONDecodeError:
            pass

    return {"error": "parse_failed", "raw_output": output}

def load_evolution_data(file_path: str) -> Dict[str, Any]:
    """加载进化数据文件"""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_evolution_data(data: Dict[str, Any], file_path: str):
    """保存进化数据到文件"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_latest_evolution_log() -> str:
    """获取最新的进化日志文件"""
    logs_dir = os.path.join(SCRIPTS_DIR, "runtime/logs")
    if not os.path.exists(logs_dir):
        return ""

    log_files = [f for f in os.listdir(logs_dir) if f.startswith("behavior_") and f.endswith(".log")]
    if not log_files:
        return ""

    # 按文件名排序，获取最新文件
    latest_log = sorted(log_files)[-1]
    return os.path.join(logs_dir, latest_log)

def run_evolution_strategy_engine() -> Dict[str, Any]:
    """运行进化策略引擎"""
    try:
        result = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS_DIR, "evolution_strategy_engine.py"), "analyze"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=SCRIPTS_DIR
        )
        if result.returncode == 0:
            return parse_json_output(result.stdout)
        return {"status": "failed", "output": result.stdout, "error": result.stderr}
    except Exception as e:
        print(f"运行进化策略引擎失败: {e}")
        return {"error": str(e)}

def run_evolution_log_analyzer() -> Dict[str, Any]:
    """运行进化日志分析引擎"""
    try:
        latest_log = get_latest_evolution_log()
        if not latest_log:
            return {"status": "no_logs", "message": "未找到进化日志"}

        result = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS_DIR, "evolution_log_analyzer.py"), "analyze", latest_log],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=SCRIPTS_DIR
        )
        if result.returncode == 0:
            return parse_json_output(result.stdout)
        return {"status": "failed", "output": result.stdout, "error": result.stderr}
    except Exception as e:
        print(f"运行进化日志分析引擎失败: {e}")
        return {"error": str(e)}

def run_evolution_self_evaluator() -> Dict[str, Any]:
    """运行进化自我评估引擎"""
    try:
        result = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS_DIR, "evolution_self_evaluator.py"), "evaluate"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=SCRIPTS_DIR
        )
        if result.returncode == 0:
            return parse_json_output(result.stdout)
        return {"status": "failed", "output": result.stdout, "error": result.stderr}
    except Exception as e:
        print(f"运行进化自我评估引擎失败: {e}")
        return {"error": str(e)}

def create_automation_plan(strategy: Dict[str, Any], analysis: Dict[str, Any], evaluation: Dict[str, Any]) -> Dict[str, Any]:
    """根据三个模块的结果创建自动化执行计划"""
    automation_plan = {
        "timestamp": datetime.now().isoformat(),
        "strategy_input": strategy,
        "analysis_input": analysis,
        "evaluation_input": evaluation,
        "actions": [],
        "recommendations": []
    }

    # 基于策略、分析和评估结果制定行动
    if strategy.get("recommended_actions"):
        automation_plan["actions"].extend(strategy["recommended_actions"])

    if analysis.get("suggestions"):
        automation_plan["recommendations"].extend(analysis["suggestions"])

    if evaluation.get("optimization_suggestions"):
        automation_plan["recommendations"].extend(evaluation["optimization_suggestions"])

    # 如果没有任何推荐，添加默认建议
    if not automation_plan["recommendations"]:
        automation_plan["recommendations"].append("继续观察系统状态，定期评估进化效果")

    return automation_plan

def execute_automation_plan(plan: Dict[str, Any]):
    """执行自动化计划"""
    print("执行自动化进化计划:")
    print(json.dumps(plan, ensure_ascii=False, indent=2))

    # 保存计划到文件
    save_evolution_data(plan, os.path.join(SCRIPTS_DIR, "runtime/state/evolution_automation_plan.json"))

    # 这里可以添加实际的执行逻辑
    # 例如：调用 do.py 执行某些命令，或者运行特定脚本

    return True

def main():
    """主函数"""
    print("启动进化闭环自动化引擎...")

    # 1. 运行进化策略引擎
    print("1. 运行进化策略引擎...")
    strategy = run_evolution_strategy_engine()

    # 2. 运行进化日志分析引擎
    print("2. 运行进化日志分析引擎...")
    analysis = run_evolution_log_analyzer()

    # 3. 运行进化自我评估引擎
    print("3. 运行进化自我评估引擎...")
    evaluation = run_evolution_self_evaluator()

    # 4. 创建自动化计划
    print("4. 创建自动化执行计划...")
    automation_plan = create_automation_plan(strategy, analysis, evaluation)

    # 5. 执行自动化计划
    print("5. 执行自动化计划...")
    success = execute_automation_plan(automation_plan)

    if success:
        print("进化闭环自动化引擎执行成功!")
        # 保存最终状态
        save_evolution_data({
            "last_run": datetime.now().isoformat(),
            "status": "success",
            "plan": automation_plan
        }, os.path.join(SCRIPTS_DIR, "runtime/state/evolution_automation_status.json"))
    else:
        print("进化闭环自动化引擎执行失败!")
        save_evolution_data({
            "last_run": datetime.now().isoformat(),
            "status": "failed"
        }, os.path.join(SCRIPTS_DIR, "runtime/state/evolution_automation_status.json"))

if __name__ == "__main__":
    main()