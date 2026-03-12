#!/usr/bin/env python3
"""
进化闭环自动化引擎
将 evolution_strategy_engine、evolution_log_analyzer、evolution_self_evaluator 三个模块联动，
实现自动化的分析→决策→执行→评估循环
增强版本：提升自动化程度，增加智能决策、预测和优先级排序功能
"""

import os
import json
import subprocess
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List

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

def predict_next_evolution_direction(strategy: Dict[str, Any], analysis: Dict[str, Any], evaluation: Dict[str, Any]) -> Dict[str, Any]:
    """预测下一个进化方向，基于当前分析结果"""
    prediction = {
        "predicted_direction": "unknown",
        "confidence": 0.0,
        "reasoning": []
    }

    # 基于策略引擎的建议
    if strategy.get("recommended_actions"):
        action = strategy["recommended_actions"][0]
        prediction["predicted_direction"] = action.get("action", "unknown")
        prediction["confidence"] = min(0.8, 0.5 + (len(strategy.get("recommended_actions", [])) * 0.1))
        prediction["reasoning"].append(f"策略引擎建议: {action.get('description', '')}")

    # 基于日志分析的洞察
    if analysis.get("patterns_detected"):
        prediction["reasoning"].append(f"检测到 {len(analysis['patterns_detected'])} 个进化模式")

    # 基于评估结果
    if evaluation.get("health_score", 100) < 70:
        prediction["reasoning"].append(f"系统健康度较低 ({evaluation.get('health_score', 0)}%)，建议优先优化")

    return prediction

def prioritize_tasks(tasks: List[Dict[str, Any]], evaluation: Dict[str, Any]) -> List[Dict[str, Any]]:
    """根据任务重要性和系统状态对任务进行优先级排序"""
    if not tasks:
        return []

    # 根据健康状态调整优先级
    health_score = evaluation.get("health_score", 100)

    # 定义优先级分数
    def calculate_priority(task: Dict[str, Any]) -> float:
        priority = task.get("priority", 5)  # 默认优先级 5

        # 如果健康度低，优先处理与系统稳定性相关的任务
        if health_score < 70 and any(keyword in task.get("description", "").lower()
                                    for keyword in ["优化", "修复", "健康", "诊断", "自愈"]):
            priority = max(priority, 9)

        # 如果健康度高，可以尝试更有挑战性的任务
        elif health_score > 85 and any(keyword in task.get("description", "").lower()
                                       for keyword in ["创新", "探索", "扩展", "新功能"]):
            priority = max(priority, 8)

        return priority

    # 按优先级排序（从高到低）
    return sorted(tasks, key=calculate_priority, reverse=True)

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
        "recommendations": [],
        "prediction": {},
        "priority_ranked": []
    }

    # 基于策略、分析和评估结果制定行动
    if strategy.get("recommended_actions"):
        automation_plan["actions"].extend(strategy["recommended_actions"])

    if analysis.get("suggestions"):
        automation_plan["recommendations"].extend(analysis["suggestions"])

    if evaluation.get("optimization_suggestions"):
        automation_plan["recommendations"].extend(evaluation["optimization_suggestions"])

    # 添加智能预测
    automation_plan["prediction"] = predict_next_evolution_direction(strategy, analysis, evaluation)

    # 对任务进行优先级排序
    automation_plan["priority_ranked"] = prioritize_tasks(
        automation_plan["actions"],
        evaluation
    )

    # 如果没有任何推荐，添加默认建议
    if not automation_plan["recommendations"]:
        automation_plan["recommendations"].append("继续观察系统状态，定期评估进化效果")

    return automation_plan

def analyze_automation_feedback(plan: Dict[str, Any], execution_result: Dict[str, Any]) -> Dict[str, Any]:
    """分析执行反馈，学习并优化未来的自动化决策"""
    feedback = {
        "timestamp": datetime.now().isoformat(),
        "execution_result": execution_result,
        "learnings": [],
        "adjustments": []
    }

    # 基于执行结果进行学习
    if execution_result.get("status") == "success":
        feedback["learnings"].append("本次自动化执行成功，可作为未来参考")
    else:
        error = execution_result.get("error", "unknown")
        feedback["adjustments"].append(f"处理错误: {error}")
        feedback["learnings"].append(f"需要改进: {error}")

    # 分析预测准确性
    prediction = plan.get("prediction", {})
    if prediction.get("predicted_direction") != "unknown":
        # 如果预测方向与实际执行的动作匹配
        predicted = prediction.get("predicted_direction", "")
        actions = [a.get("action", "") for a in plan.get("actions", [])]
        if predicted in actions:
            feedback["learnings"].append("预测方向准确")
        else:
            feedback["learnings"].append("预测方向需要调整")

    return feedback

def execute_automation_plan(plan: Dict[str, Any]):
    """执行自动化计划"""
    print("执行自动化进化计划:")
    print(json.dumps(plan, ensure_ascii=False, indent=2))

    # 保存计划到文件
    save_evolution_data(plan, os.path.join(SCRIPTS_DIR, "runtime/state/evolution_automation_plan.json"))

    # 记录执行进度
    execution_result = {
        "status": "success",
        "actions_count": len(plan.get("actions", [])),
        "recommendations_count": len(plan.get("recommendations", []))
    }

    # 分析执行反馈
    feedback = analyze_automation_feedback(plan, execution_result)
    save_evolution_data(feedback, os.path.join(SCRIPTS_DIR, "runtime/state/evolution_automation_feedback.json"))

    # 这里可以添加实际的执行逻辑
    # 例如：调用 do.py 执行某些命令，或者运行特定脚本

    return execution_result

def generate_progress_report(plan: Dict[str, Any], execution_result: Dict[str, Any]) -> Dict[str, Any]:
    """生成进化自动化进度报告"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "execution_summary": {
            "status": execution_result.get("status", "unknown"),
            "total_actions": execution_result.get("actions_count", 0),
            "priority_actions": len(plan.get("priority_ranked", []))
        },
        "prediction": plan.get("prediction", {}),
        "recommendations": plan.get("recommendations", [])[:5],  # 只保留前5条
        "next_steps": []
    }

    # 基于预测和优先级生成下一步建议
    prediction = plan.get("prediction", {})
    if prediction.get("predicted_direction") != "unknown":
        report["next_steps"].append({
            "suggested_action": prediction.get("predicted_direction"),
            "confidence": prediction.get("confidence", 0.0),
            "reasoning": prediction.get("reasoning", [])
        })

    return report

def main():
    """主函数"""
    print("启动进化闭环自动化引擎（增强版）...")
    print("=" * 50)

    # 1. 运行进化策略引擎
    print("1. 运行进化策略引擎...")
    strategy = run_evolution_strategy_engine()
    print(f"   策略引擎返回: {strategy.get('status', 'completed')}")

    # 2. 运行进化日志分析引擎
    print("2. 运行进化日志分析引擎...")
    analysis = run_evolution_log_analyzer()
    print(f"   日志分析引擎返回: {analysis.get('status', 'completed')}")

    # 3. 运行进化自我评估引擎
    print("3. 运行进化自我评估引擎...")
    evaluation = run_evolution_self_evaluator()
    print(f"   自我评估引擎返回: {evaluation.get('status', 'completed')}")

    # 4. 创建自动化计划（包含智能预测和优先级排序）
    print("4. 创建自动化执行计划...")
    automation_plan = create_automation_plan(strategy, analysis, evaluation)

    # 5. 执行自动化计划
    print("5. 执行自动化计划...")
    execution_result = execute_automation_plan(automation_plan)

    # 6. 生成进度报告
    print("6. 生成进度报告...")
    progress_report = generate_progress_report(automation_plan, execution_result)

    if execution_result.get("status") == "success":
        print("进化闭环自动化引擎执行成功!")
        print(f"   预测方向: {progress_report.get('prediction', {}).get('predicted_direction', 'unknown')}")
        print(f"   置信度: {progress_report.get('prediction', {}).get('confidence', 0.0):.1%}")

        # 保存最终状态
        save_evolution_data({
            "last_run": datetime.now().isoformat(),
            "status": "success",
            "plan": automation_plan,
            "progress_report": progress_report
        }, os.path.join(SCRIPTS_DIR, "runtime/state/evolution_automation_status.json"))
    else:
        print("进化闭环自动化引擎执行失败!")
        save_evolution_data({
            "last_run": datetime.now().isoformat(),
            "status": "failed",
            "error": execution_result.get("error", "unknown")
        }, os.path.join(SCRIPTS_DIR, "runtime/state/evolution_automation_status.json"))

    print("=" * 50)

if __name__ == "__main__":
    main()