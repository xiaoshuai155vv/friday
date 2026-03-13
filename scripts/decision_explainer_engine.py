"""
智能决策可解释性增强器 (Decision Explainer Engine)

让系统能够以自然语言详细解释每个决策的背后原因，提升系统透明度和用户信任。

功能：
1. 引擎推荐理由解释 - 分析任务需求，解释为什么选择这些引擎
2. 工作流执行路径解释 - 解释为什么按这个顺序执行，关键决策点是什么
3. 失败原因分析 - 步骤失败时提供原因和可能的解决方案
4. 执行过程实时解说 - 在执行工作流时逐步解释当前步骤的原因
"""

import json
import os
from datetime import datetime
from pathlib import Path


class DecisionExplainerEngine:
    """智能决策可解释性增强器"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.state_dir = self.base_dir / "runtime" / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # 引擎能力描述知识库
        self.engine_descriptions = {
            "conversation_execution_engine": "理解自然语言对话意图，提取关键实体和任务需求",
            "cross_engine_task_planner": "分析复杂任务，自动拆分为可执行的子任务",
            "engine_combination_recommender": "根据任务需求，智能推荐最优的引擎组合",
            "dynamic_engine_orchestrator": "根据实时任务需求动态编排引擎执行顺序",
            "auto_execution_engine": "自动执行编排计划，实现从建议到执行的闭环",
            "workflow_engine": "理解复杂意图，自动规划多步骤任务链",
            "scenario_recommender": "根据用户行为习惯和时间段推荐合适的场景计划",
            "unified_recommender": "整合多种推荐能力，提供统一的智能推荐入口",
            "intent_deep_reasoning_engine": "进行深层意图推理，理解用户的真实需求",
            "behavior_sequence_prediction_engine": "分析用户行为序列，预测下一步意图",
            "proactive_service_enhancer": "预测用户可能需要的服务并提前准备",
            "knowledge_graph": "构建知识关联网络，支持上下文推理",
            "adaptive_learning_engine": "从用户交互中学习行为模式，自动调整策略",
            "health_assurance_loop": "监控健康状态，提供保障服务",
            "proactive_operations_engine": "主动运维，优化系统资源",
            "execution_enhancement_engine": "追踪执行效果，优化执行策略"
        }

    def explain_engine_recommendation(self, task_description: str, recommended_engines: list) -> str:
        """
        解释为什么推荐这些引擎

        Args:
            task_description: 任务描述
            recommended_engines: 推荐的引擎列表

        Returns:
            自然语言解释
        """
        if not recommended_engines:
            return "没有找到合适的引擎来执行此任务。"

        explanations = []
        explanations.append(f"任务「{task_description}」的分析：")

        for i, engine in enumerate(recommended_engines, 1):
            desc = self.engine_descriptions.get(engine, "执行特定任务")
            explanations.append(f"{i}. **{engine}**：{desc}")

        # 添加选择理由
        explanations.append("\n**选择理由**：")
        if len(recommended_engines) == 1:
            explanations.append(f"此任务只需要「{recommended_engines[0]}」即可完成。")
        else:
            explanations.append("通过多引擎协同工作来确保任务完成的准确性和效率：")
            explanations.append("- 首先使用对话理解类引擎解析用户意图")
            explanations.append("- 然后使用规划类引擎拆分任务")
            explanations.append("- 最后使用执行类引擎完成具体操作")

        return "\n".join(explanations)

    def explain_workflow_path(self, workflow_steps: list) -> str:
        """
        解释工作流执行路径

        Args:
            workflow_steps: 工作流步骤列表

        Returns:
            自然语言解释
        """
        if not workflow_steps:
            return "工作流为空，无需执行。"

        explanations = []
        explanations.append("**工作流执行路径说明**：\n")

        for i, step in enumerate(workflow_steps, 1):
            step_type = step.get("do", step.get("type", "unknown"))
            step_desc = step.get("description", self._get_step_description(step))

            explanations.append(f"{i}. **{step_type}**：{step_desc}")

            # 添加关键决策点解释
            if step_type == "vision" or step_type == "vision_coords":
                explanations.append("   └─ 需要通过视觉理解来判断下一步操作")
            elif step_type == "click":
                explanations.append("   └─ 根据视觉分析结果确定点击位置")
            elif step_type == "type":
                content = step.get("content", "")
                if len(content) > 20:
                    content = content[:20] + "..."
                explanations.append(f"   └─ 输入内容：{content}")
            elif step_type == "run":
                explanations.append("   └─ 执行特定脚本来完成子任务")

        explanations.append("\n**执行顺序理由**：")
        explanations.append("- 先获取环境信息（截图、窗口状态）")
        explanations.append("- 然后进行分析决策（vision、推理）")
        explanations.append("- 最后执行具体操作（点击、输入）")

        return "\n".join(explanations)

    def _get_step_description(self, step: dict) -> str:
        """获取步骤的默认描述"""
        step_type = step.get("do", step.get("type", ""))
        if step_type == "screenshot":
            return "截取当前屏幕内容"
        elif step_type == "vision":
            return "分析截图内容，理解当前界面状态"
        elif step_type == "vision_coords":
            return "从图像中提取点击坐标"
        elif step_type == "click":
            return f"点击坐标 ({step.get('x', '?')}, {step.get('y', '?')})"
        elif step_type == "type":
            return "输入文本内容"
        elif step_type == "key":
            return f"按下键盘键 {step.get('key', '?')}"
        elif step_type == "paste":
            return "粘贴剪贴板内容"
        elif step_type == "scroll":
            return f"滚动页面 {step.get('delta', '?')} 像素"
        elif step_type == "wait":
            return f"等待 {step.get('seconds', '?')} 秒"
        elif step_type == "run":
            return f"执行脚本：{step.get('script', step.get('name', 'unknown'))}"
        elif step_type == "activate":
            return f"激活窗口：{step.get('title', '?')}"
        elif step_type == "maximize":
            return f"最大化窗口：{step.get('title', '?')}"
        return f"执行 {step_type} 操作"

    def explain_failure(self, step_index: int, step: dict, error_message: str) -> str:
        """
        解释失败原因并提供解决方案

        Args:
            step_index: 失败步骤索引
            step: 步骤信息
            error_message: 错误信息

        Returns:
            自然语言解释和解决方案
        """
        explanations = []
        explanations.append(f"**步骤 {step_index + 1} 执行失败**\n")

        step_type = step.get("do", step.get("type", "unknown"))
        explanations.append(f"失败的操作：{step_type}")

        # 分析常见错误并提供解决方案
        explanations.append("\n**可能原因分析**：")

        if "timeout" in error_message.lower() or "超时" in error_message:
            explanations.append("1. 操作超时 - 目标应用响应过慢")
            explanations.append("   → 建议：增加等待时间或检查应用是否卡顿")

        if "not found" in error_message.lower() or "未找到" in error_message:
            explanations.append("1. 目标元素未找到 - 界面可能已变化")
            explanations.append("   → 建议：重新截图分析当前界面状态")

        if "permission" in error_message.lower() or "权限" in error_message:
            explanations.append("1. 权限不足 - 缺少必要的系统权限")
            explanations.append("   → 建议：以管理员身份运行或检查权限设置")

        if "activate" in error_message.lower() or "激活" in error_message:
            explanations.append("1. 窗口激活失败 - 目标窗口可能被遮挡或最小化")
            explanations.append("   → 建议：确保窗口可见后再执行操作")

        if "vision" in error_message.lower() or "多模态" in error_message:
            explanations.append("1. 视觉分析失败 - 图像质量问题或 API 超时")
            explanations.append("   → 建议：确保截图清晰或检查网络连接")

        # 如果没有匹配到具体原因
        if len(explanations) <= 3:
            explanations.append(f"2. 未知错误：{error_message[:100]}")

        explanations.append("\n**建议解决方案**：")
        explanations.append("1. 重新执行工作流（从失败处开始）")
        explanations.append("2. 检查目标应用状态是否正常")
        explanations.append("3. 手动确认操作后再继续")

        return "\n".join(explanations)

    def explain_execution_progress(self, completed_steps: list, current_step: dict, remaining_steps: int) -> str:
        """
        解释执行进度

        Args:
            completed_steps: 已完成的步骤
            current_step: 当前步骤
            remaining_steps: 剩余步骤数

        Returns:
            进度说明
        """
        explanations = []
        total = len(completed_steps) + 1 + remaining_steps
        progress = (len(completed_steps) / total) * 100

        explanations.append(f"**执行进度**：{len(completed_steps)}/{total} ({progress:.0f}%)")
        explanations.append(f"正在执行：{self._get_step_description(current_step)}")

        if remaining_steps > 0:
            explanations.append(f"还有 {remaining_steps} 个步骤待执行")

        # 预测下一步
        explanations.append("\n**后续操作预测**：")
        if current_step.get("do") == "screenshot" or current_step.get("do") == "vision":
            explanations.append("→ 接下来需要分析界面内容来确定操作")
        elif current_step.get("do") == "click":
            explanations.append("→ 点击后需要等待响应并确认结果")
        elif current_step.get("do") == "type":
            explanations.append("→ 输入完成后可能需要按回车确认")

        return "\n".join(explanations)

    def get_decision_summary(self) -> dict:
        """
        获取决策解释能力的摘要

        Returns:
            包含能力信息的字典
        """
        return {
            "engine_name": "智能决策可解释性增强器",
            "capabilities": [
                "引擎推荐理由解释 - 分析任务需求，解释为什么选择特定引擎组合",
                "工作流执行路径解释 - 说明每个步骤的目的和执行顺序",
                "失败原因分析 - 提供错误原因和解决方案",
                "执行过程实时解说 - 逐步解释当前操作的原因"
            ],
            "supported_engines": list(self.engine_descriptions.keys()),
            "commands": {
                "explain_recommendation": "解释引擎推荐理由",
                "explain_workflow": "解释工作流执行路径",
                "explain_failure": "分析失败原因",
                "explain_progress": "说明执行进度"
            }
        }


def main():
    """CLI 入口"""
    import argparse

    parser = argparse.ArgumentParser(description="智能决策可解释性增强器")
    parser.add_argument("action", nargs="?", default="status",
                        choices=["status", "explain", "workflow", "failure", "progress"],
                        help="执行的操作")
    parser.add_argument("--task", "-t", help="任务描述")
    parser.add_argument("--engines", "-e", nargs="+", help="推荐的引擎列表")
    parser.add_argument("--steps", "-s", type=json.loads, help="工作流步骤（JSON）")
    parser.add_argument("--step-index", type=int, help="失败步骤索引")
    parser.add_argument("--error", help="错误信息")
    parser.add_argument("--completed", type=int, default=0, help="已完成步骤数")
    parser.add_argument("--remaining", type=int, default=0, help="剩余步骤数")

    args = parser.parse_args()

    engine = DecisionExplainerEngine()

    if args.action == "status":
        result = engine.get_decision_summary()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.action == "explain":
        if not args.task or not args.engines:
            print("错误：需要提供 --task 和 --engines 参数")
            return
        print(engine.explain_engine_recommendation(args.task, args.engines))
    elif args.action == "workflow":
        if not args.steps:
            print("错误：需要提供 --steps 参数（JSON 格式）")
            return
        print(engine.explain_workflow_path(args.steps))
    elif args.action == "failure":
        if args.step_index is None or not args.steps or not args.error:
            print("错误：需要提供 --step-index、--steps 和 --error 参数")
            return
        step = args.steps[args.step_index] if args.step_index < len(args.steps) else {}
        print(engine.explain_failure(args.step_index, step, args.error))
    elif args.action == "progress":
        current_step = {"do": args.steps[0]["do"]} if args.steps else {}
        print(engine.explain_execution_progress([], current_step, args.remaining))


if __name__ == "__main__":
    main()