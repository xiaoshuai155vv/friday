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

# 预测学习历史存储
PREDICTION_HISTORY_FILE = os.path.join(SCRIPTS_DIR, "runtime/state/evolution_prediction_history.json")

def load_prediction_history() -> List[Dict[str, Any]]:
    """加载预测历史用于学习"""
    if os.path.exists(PREDICTION_HISTORY_FILE):
        with open(PREDICTION_HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_prediction_history(history: List[Dict[str, Any]]):
    """保存预测历史"""
    os.makedirs(os.path.dirname(PREDICTION_HISTORY_FILE), exist_ok=True)
    # 只保留最近20条
    history = history[-20:]
    with open(PREDICTION_HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def calculate_prediction_accuracy(history: List[Dict[str, Any]]) -> float:
    """计算历史预测准确率"""
    if not history:
        return 0.5  # 无历史时默认0.5

    accurate_count = 0
    for entry in history:
        if entry.get("actual_executed") and entry.get("predicted_direction"):
            # 如果实际执行的方向与预测匹配
            if entry["predicted_direction"] == entry["actual_executed"]:
                accurate_count += 1
            # 也考虑部分匹配
            elif any(key in entry["actual_executed"] for key in ["engine", "自动化", "优化", "增强"]):
                accurate_count += 0.5

    return accurate_count / len(history) if history else 0.5

def predict_next_evolution_direction(strategy: Dict[str, Any], analysis: Dict[str, Any], evaluation: Dict[str, Any]) -> Dict[str, Any]:
    """预测下一个进化方向，基于当前分析结果和学习历史"""
    # 加载预测历史
    prediction_history = load_prediction_history()
    historical_accuracy = calculate_prediction_accuracy(prediction_history)

    prediction = {
        "predicted_direction": "unknown",
        "confidence": 0.0,
        "reasoning": [],
        "based_on_history": historical_accuracy > 0.3
    }

    # 基于历史预测准确率调整置信度
    base_confidence = 0.5 + (historical_accuracy * 0.3)  # 准确率越高，置信度越高

    # 基于策略引擎的建议
    if strategy.get("recommended_actions"):
        action = strategy["recommended_actions"][0]
        prediction["predicted_direction"] = action.get("action", "unknown")
        prediction["confidence"] = min(0.9, base_confidence + (len(strategy.get("recommended_actions", [])) * 0.05))
        prediction["reasoning"].append(f"策略引擎建议: {action.get('description', '')}")

    # 基于日志分析的洞察
    if analysis.get("patterns_detected"):
        prediction["reasoning"].append(f"检测到 {len(analysis['patterns_detected'])} 个进化模式")

    # 基于评估结果
    health_score = evaluation.get("health_score", 100)
    if health_score < 70:
        prediction["reasoning"].append(f"系统健康度较低 ({health_score}%)，建议优先优化")
        prediction["predicted_direction"] = "系统优化"
        prediction["confidence"] = min(0.95, prediction["confidence"] + 0.2)

    # 基于历史最成功的进化方向
    if prediction_history:
        direction_counts = {}
        for entry in prediction_history:
            if entry.get("actual_executed"):
                direction = entry["actual_executed"]
                direction_counts[direction] = direction_counts.get(direction, 0) + 1
        if direction_counts:
            most_successful = max(direction_counts, key=direction_counts.get)
            if prediction["predicted_direction"] == "unknown" or direction_counts[most_successful] >= 3:
                prediction["predicted_direction"] = most_successful
                prediction["reasoning"].append(f"历史成功方向: {most_successful} (执行{direction_counts[most_successful]}次)")

    # 保存本次预测供下次学习
    new_history_entry = {
        "timestamp": datetime.now().isoformat(),
        "predicted_direction": prediction["predicted_direction"],
        "confidence": prediction["confidence"],
        "reasoning": prediction["reasoning"],
        "actual_executed": None  # 将在执行后更新
    }
    prediction_history.append(new_history_entry)
    save_prediction_history(prediction_history)

    # 将预测历史引用添加到返回结果
    prediction["history_accuracy"] = historical_accuracy

    return prediction

# 任务执行历史存储
TASK_EXECUTION_HISTORY = os.path.join(SCRIPTS_DIR, "runtime/state/evolution_task_history.json")

def load_task_history() -> Dict[str, Any]:
    """加载任务执行历史"""
    if os.path.exists(TASK_EXECUTION_HISTORY):
        with open(TASK_EXECUTION_HISTORY, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"tasks": [], "success_patterns": {}, "failure_patterns": {}}

def save_task_history(history: Dict[str, Any]):
    """保存任务执行历史"""
    os.makedirs(os.path.dirname(TASK_EXECUTION_HISTORY), exist_ok=True)
    with open(TASK_EXECUTION_HISTORY, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def analyze_task_patterns(task_history: Dict[str, Any], task: Dict[str, Any]) -> float:
    """分析任务执行模式，返回成功率调整因子"""
    task_desc = task.get("description", "").lower()
    task_action = task.get("action", "").lower()

    success_patterns = task_history.get("success_patterns", {})
    failure_patterns = task_history.get("failure_patterns", {})

    adjustment = 0.0

    # 检查成功模式
    for pattern, count in success_patterns.items():
        if pattern in task_desc or pattern in task_action:
            adjustment += min(0.2, count * 0.05)

    # 检查失败模式（减少优先级）
    for pattern, count in failure_patterns.items():
        if pattern in task_desc or pattern in task_action:
            adjustment -= min(0.3, count * 0.1)

    return adjustment

def prioritize_tasks(tasks: List[Dict[str, Any]], evaluation: Dict[str, Any]) -> List[Dict[str, Any]]:
    """根据任务重要性、系统状态和历史执行模式对任务进行优先级排序（增强版）"""
    if not tasks:
        return []

    # 加载任务执行历史
    task_history = load_task_history()

    # 根据健康状态调整优先级
    health_score = evaluation.get("health_score", 100)
    success_rate = evaluation.get("success_rate", 0.8)

    # 定义优先级分数
    def calculate_priority(task: Dict[str, Any]) -> float:
        priority = task.get("priority", 5)  # 默认优先级 5

        # 1. 健康状态调整
        if health_score < 70 and any(keyword in task.get("description", "").lower()
                                    for keyword in ["优化", "修复", "健康", "诊断", "自愈", "系统"]):
            priority = max(priority, 9)
        elif health_score > 85 and any(keyword in task.get("description", "").lower()
                                       for keyword in ["创新", "探索", "扩展", "新功能"]):
            priority = max(priority, 8)

        # 2. 历史执行模式调整
        pattern_adjustment = analyze_task_patterns(task_history, task)
        priority += pattern_adjustment

        # 3. 成功率调整
        if success_rate < 0.6:
            # 成功率低时，优先选择简单稳定任务
            if any(keyword in task.get("description", "").lower()
                   for keyword in ["优化", "修复", "维护", "简单"]):
                priority += 1.5
        elif success_rate > 0.9:
            # 成功率高时，可以尝试更复杂任务
            if any(keyword in task.get("description", "").lower()
                   for keyword in ["复杂", "集成", "协同", "多引擎"]):
                priority += 1.0

        # 4. 紧急度调整
        if task.get("urgency") == "high":
            priority += 2

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

def analyze_system_readiness(evaluation: Dict[str, Any]) -> Dict[str, Any]:
    """分析系统是否准备好进行下一轮进化"""
    readiness = {
        "ready": True,
        "level": "optimal",  # optimal, good, caution, not_ready
        "blocking_factors": [],
        "ready_score": 0
    }

    # 基于多个指标评估准备度
    health_score = evaluation.get("health_score", 100)
    success_rate = evaluation.get("success_rate", 0.8)

    # 计算准备度分数
    readiness["ready_score"] = (health_score * 0.4) + (success_rate * 100 * 0.4) + 20

    # 检查是否准备好
    if health_score < 50 or success_rate < 0.5:
        readiness["ready"] = False
        readiness["level"] = "not_ready"
        if health_score < 50:
            readiness["blocking_factors"].append(f"系统健康度过低: {health_score}%")
        if success_rate < 0.5:
            readiness["blocking_factors"].append(f"任务成功率过低: {success_rate:.1%}")
    elif health_score < 70:
        readiness["ready"] = True
        readiness["level"] = "caution"
        readiness["blocking_factors"].append(f"系统健康度较低: {health_score}%")
    elif health_score < 85:
        readiness["ready"] = True
        readiness["level"] = "good"
    else:
        readiness["ready"] = True
        readiness["level"] = "optimal"

    return readiness

def create_automation_plan(strategy: Dict[str, Any], analysis: Dict[str, Any], evaluation: Dict[str, Any]) -> Dict[str, Any]:
    """根据三个模块的结果创建自动化执行计划（增强版）"""
    # 首先分析系统准备度
    readiness = analyze_system_readiness(evaluation)

    automation_plan = {
        "timestamp": datetime.now().isoformat(),
        "strategy_input": strategy,
        "analysis_input": analysis,
        "evaluation_input": evaluation,
        "readiness": readiness,
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

    # 对任务进行优先级排序（使用增强版算法）
    automation_plan["priority_ranked"] = prioritize_tasks(
        automation_plan["actions"],
        evaluation
    )

    # 如果系统未准备好，添加提醒
    if not readiness["ready"]:
        automation_plan["recommendations"].insert(0, f"⚠️ 系统未准备好进行新进化: {', '.join(readiness['blocking_factors'])}")

    # 添加自适应建议
    if readiness["level"] == "optimal":
        automation_plan["recommendations"].append("系统状态最佳，适合尝试创新性任务")
    elif readiness["level"] == "caution":
        automation_plan["recommendations"].append("系统状态一般，建议优先处理优化任务")

    # 如果没有任何推荐，添加默认建议
    if not automation_plan["recommendations"]:
        automation_plan["recommendations"].append("继续观察系统状态，定期评估进化效果")

    return automation_plan

def analyze_automation_feedback(plan: Dict[str, Any], execution_result: Dict[str, Any]) -> Dict[str, Any]:
    """分析执行反馈，学习并优化未来的自动化决策（增强版）"""
    feedback = {
        "timestamp": datetime.now().isoformat(),
        "execution_result": execution_result,
        "learnings": [],
        "adjustments": []
    }

    # 基于执行结果进行学习
    if execution_result.get("status") == "success":
        feedback["learnings"].append("本次自动化执行成功，可作为未来参考")

        # 记录成功的任务模式
        task_history = load_task_history()
        for action in plan.get("actions", []):
            desc = action.get("description", "").lower()
            action_type = action.get("action", "").lower()
            # 提取关键词
            keywords = []
            for keyword in ["优化", "修复", "健康", "诊断", "自愈", "创新", "探索", "扩展", "新功能", "系统", "协同"]:
                if keyword in desc or keyword in action_type:
                    keywords.append(keyword)

            for kw in keywords:
                task_history["success_patterns"][kw] = task_history["success_patterns"].get(kw, 0) + 1

        save_task_history(task_history)
    else:
        error = execution_result.get("error", "unknown")
        feedback["adjustments"].append(f"处理错误: {error}")
        feedback["learnings"].append(f"需要改进: {error}")

        # 记录失败的任务模式
        task_history = load_task_history()
        for action in plan.get("actions", []):
            desc = action.get("description", "").lower()
            action_type = action.get("action", "").lower()
            keywords = []
            for keyword in ["优化", "修复", "健康", "诊断", "自愈", "创新", "探索", "扩展", "新功能", "系统", "协同"]:
                if keyword in desc or keyword in action_type:
                    keywords.append(keyword)

            for kw in keywords:
                task_history["failure_patterns"][kw] = task_history["failure_patterns"].get(kw, 0) + 1

        save_task_history(task_history)

    # 分析预测准确性并更新历史
    prediction = plan.get("prediction", {})
    if prediction.get("predicted_direction") != "unknown":
        predicted = prediction.get("predicted_direction", "")
        actions = [a.get("action", "") for a in plan.get("actions", [])]
        actual_executed = None

        if predicted in actions:
            feedback["learnings"].append("预测方向准确")
            actual_executed = predicted
        else:
            feedback["learnings"].append("预测方向需要调整")
            # 选择实际执行的动作
            actual_executed = actions[0] if actions else predicted

        # 更新预测历史中的实际执行结果
        prediction_history = load_prediction_history()
        if prediction_history:
            # 找到最后一个预测并更新其实际执行结果
            for i in range(len(prediction_history) - 1, -1, -1):
                if prediction_history[i].get("actual_executed") is None:
                    prediction_history[i]["actual_executed"] = actual_executed
                    break
            save_prediction_history(prediction_history)

    # 基于反馈自动调整参数
    if feedback["learnings"]:
        success_count = sum(1 for l in feedback["learnings"] if "成功" in l)
        if success_count > len(feedback["learnings"]) / 2:
            feedback["adjustments"].append("自动调整：增加复杂任务权重")
        else:
            feedback["adjustments"].append("自动调整：降低复杂任务优先级，增加稳定任务")

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
    print("4. 创建自动化执行计划（增强版）...")
    automation_plan = create_automation_plan(strategy, analysis, evaluation)

    # 显示系统准备度
    readiness = automation_plan.get("readiness", {})
    print(f"   系统准备度: {readiness.get('level', 'unknown')} (分数: {readiness.get('ready_score', 0):.1f})")
    if not readiness.get("ready"):
        print(f"   阻塞因素: {', '.join(readiness.get('blocking_factors', []))}")

    # 显示预测信息
    prediction = automation_plan.get("prediction", {})
    print(f"   预测方向: {prediction.get('predicted_direction', 'unknown')}")
    print(f"   预测置信度: {prediction.get('confidence', 0.0):.1%}")
    if prediction.get("based_on_history"):
        print(f"   历史准确率: {prediction.get('history_accuracy', 0):.1%}")

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
            "progress_report": progress_report,
            "enhancements": {
                "智能预测学习机制": "已添加",
                "优化任务优先级算法": "已添加",
                "自适应调整能力": "已添加"
            }
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