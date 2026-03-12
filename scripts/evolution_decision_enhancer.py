#!/usr/bin/env python3
"""
进化决策增强引擎
将智能预测功能集成到实际进化决策中，使进化环更具前瞻性
"""

import os
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

# 添加 scripts 目录到路径
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

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

def enhance_decision_with_prediction(current_plan: Dict[str, Any], prediction: Dict[str, Any]) -> Dict[str, Any]:
    """
    基于预测结果增强进化决策

    Args:
        current_plan: 当前的进化计划
        prediction: 智能预测结果

    Returns:
        增强后的进化计划
    """
    enhanced_plan = current_plan.copy()

    # 添加预测信息到计划中
    enhanced_plan["enhanced_by_prediction"] = True
    enhanced_plan["prediction_info"] = prediction

    # 根据预测结果调整任务优先级
    if prediction.get("predicted_direction") and prediction.get("confidence", 0) > 0.6:
        predicted_direction = prediction["predicted_direction"]

        # 查找与预测方向匹配的任务
        matched_actions = []
        for action in enhanced_plan.get("actions", []):
            if predicted_direction.lower() in action.get("description", "").lower() or \
               predicted_direction.lower() in action.get("action", "").lower():
                matched_actions.append(action)

        # 如果找到匹配项，提升其优先级
        if matched_actions:
            # 为匹配的行动添加高优先级标记
            for action in enhanced_plan.get("actions", []):
                if action in matched_actions:
                    # 如果已经有优先级，增加一些权重
                    if "priority" in action:
                        action["priority"] = min(10, action["priority"] + 2)
                    else:
                        action["priority"] = 8  # 默认设置较高优先级

                    # 添加预测标签
                    if "tags" not in action:
                        action["tags"] = []
                    if "predicted" not in action["tags"]:
                        action["tags"].append("predicted")

            # 重新排序任务，确保预测方向的任务优先执行
            if "priority_ranked" in enhanced_plan:
                # 重新排序
                priority_ranked = enhanced_plan["priority_ranked"]
                predicted_actions = [action for action in priority_ranked if action in matched_actions]
                other_actions = [action for action in priority_ranked if action not in matched_actions]

                # 将预测匹配的任务放在前面
                enhanced_plan["priority_ranked"] = predicted_actions + other_actions

    return enhanced_plan

def create_decision_enhancement_report(current_plan: Dict[str, Any], prediction: Dict[str, Any]) -> Dict[str, Any]:
    """创建决策增强报告"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "enhancement_summary": {
            "prediction_used": prediction.get("predicted_direction", "unknown"),
            "confidence": prediction.get("confidence", 0.0),
            "enhancement_type": "prediction_based_prioritization" if prediction.get("predicted_direction") != "unknown" else "no_prediction"
        },
        "changes_made": [],
        "recommendations": []
    }

    # 根据预测结果生成建议
    if prediction.get("predicted_direction") != "unknown":
        report["recommendations"].append(f"根据预测({prediction.get('predicted_direction')})调整任务优先级")
        report["recommendations"].append(f"预测置信度: {prediction.get('confidence', 0.0):.1%}")

        # 如果预测基于历史，提供历史准确率参考
        if prediction.get("history_accuracy", 0) > 0:
            report["recommendations"].append(f"历史预测准确率: {prediction.get('history_accuracy', 0):.1%}")

    return report

def main():
    """主函数"""
    print("启动进化决策增强引擎...")

    # 从环境变量或参数中获取当前计划文件路径
    plan_file = os.environ.get("EVOLUTION_PLAN_FILE", os.path.join(SCRIPTS_DIR, "runtime/state/evolution_automation_plan.json"))

    # 加载当前进化计划
    try:
        current_plan = load_evolution_data(plan_file)
        if not current_plan:
            print("错误：无法加载进化计划")
            return
    except Exception as e:
        print(f"错误：加载进化计划失败 - {e}")
        return

    # 获取预测信息
    prediction = current_plan.get("prediction", {})

    if not prediction:
        print("警告：未找到预测信息，跳过决策增强")
        return

    # 增强决策
    enhanced_plan = enhance_decision_with_prediction(current_plan, prediction)

    # 生成增强报告
    enhancement_report = create_decision_enhancement_report(current_plan, prediction)

    # 保存增强后的计划
    enhanced_plan_file = os.path.join(SCRIPTS_DIR, "runtime/state/evolution_automation_plan_enhanced.json")
    save_evolution_data(enhanced_plan, enhanced_plan_file)

    # 保存增强报告
    report_file = os.path.join(SCRIPTS_DIR, "runtime/state/evolution_decision_enhancement_report.json")
    save_evolution_data(enhancement_report, report_file)

    print("进化决策增强完成!")
    print(f"增强计划已保存到: {enhanced_plan_file}")
    print(f"增强报告已保存到: {report_file}")

    # 显示增强摘要
    print("\n=== 增强摘要 ===")
    print(f"预测方向: {enhancement_report['enhancement_summary']['prediction_used']}")
    print(f"置信度: {enhancement_report['enhancement_summary']['confidence']:.1%}")

    if enhancement_report["recommendations"]:
        print("\n增强建议:")
        for rec in enhancement_report["recommendations"]:
            print(f"  - {rec}")

if __name__ == "__main__":
    main()