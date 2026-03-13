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

        # 引擎能力描述知识库（70+引擎）
        self.engine_descriptions = {
            # 核心执行引擎
            "conversation_execution_engine": "理解自然语言对话意图，提取关键实体和任务需求",
            "cross_engine_task_planner": "分析复杂任务，自动拆分为可执行的子任务",
            "engine_combination_recommender": "根据任务需求，智能推荐最优的引擎组合",
            "dynamic_engine_orchestrator": "根据实时任务需求动态编排引擎执行顺序",
            "auto_execution_engine": "自动执行编排计划，实现从建议到执行的闭环",
            "workflow_engine": "理解复杂意图，自动规划多步骤任务链",
            "automation_execution_engine": "执行端到端自动化工作流，协调多引擎协同工作",

            # 推荐与场景引擎
            "scenario_recommender": "根据用户行为习惯和时间段推荐合适的场景计划",
            "unified_recommender": "整合多种推荐能力，提供统一的智能推荐入口",
            "active_suggestion_engine": "主动推送建议，根据系统状态和时间提供智能提醒",
            "scene_adaptive_engine": "根据实时上下文自动调整场景执行策略",
            "intent_completion_engine": "理解模糊输入，主动补全用户意图并推荐操作",

            # 意图理解与推理
            "intent_deep_reasoning_engine": "进行深层意图推理，理解用户的真实需求和隐含意图",
            "behavior_sequence_prediction_engine": "分析用户行为序列，预测下一步意图",
            "context_awareness_engine": "感知当前环境、时间、用户状态，主动预测需求",
            "long_term_memory_engine": "记住长期目标、跨会话习惯和偏好，提供个性化服务",

            # 知识与推理引擎
            "knowledge_graph": "构建知识关联网络，支持上下文推理和智能推荐",
            "knowledge_evolution_engine": "从执行历史中提取新知识，更新知识图谱",
            "enhanced_knowledge_reasoning_engine": "进行因果推理、类比推理，发现隐藏关联",
            "knowledge_inheritance_engine": "传承历史经验，让新引擎快速继承已有能力",

            # 学习与适应引擎
            "adaptive_learning_engine": "从用户交互中学习行为模式，自动调整推荐策略",
            "feedback_learning_engine": "根据用户反馈自动优化推荐策略",
            "task_preference_engine": "记录用户对特定任务类型的偏好设置",
            "autonomous_learning_innovation_engine": "主动发现优化机会，实施自动改进",

            # 健康与保障引擎
            "self_healing_engine": "自动检测问题、分析原因并尝试自动修复",
            "health_assurance_loop": "监控健康状态，提供预测→运维→自愈→反馈的闭环保障",
            "system_health_report_engine": "自动进行全面健康检查，生成详细状态报告",
            "system_self_diagnosis_engine": "跨模块问题追踪和综合诊断能力",
            "security_monitor_engine": "主动监控异常行为、可疑进程、网络异常等安全威胁",

            # 主动服务引擎
            "proactive_operations_engine": "主动监控系统资源，预测资源瓶颈并优化",
            "proactive_notification_engine": "主动向用户推送有价值的信息和建议",
            "proactive_insight_engine": "基于知识图谱和执行历史提供前瞻性洞察",
            "proactive_decision_action_engine": "持续监控，主动识别优化机会并自动执行",
            "zero_click_service_engine": "基于简短输入自动识别完整任务链并执行",

            # 任务管理引擎
            "task_planning_engine": "理解自然语言目标，自动分解为可执行步骤链",
            "task_continuation_engine": "追踪长时间运行的任务状态，实现跨会话接续",
            "task_memory_engine": "跨模块任务追踪、意图预测和主动任务规划",
            "workflow_quality_engine": "监控工作流执行质量，自动分析失败原因并生成优化建议",

            # 代码与分析引擎
            "code_understanding_engine": "代码结构分析、依赖检测、代码质量评估、重构建议",
            "script_generation_engine": "根据自然语言需求自动生成可执行脚本",
            "data_insight_engine": "整合运行数据进行深度分析和可视化",
            "system_insight_engine": "统一分析引擎性能，预测潜在问题，提供前瞻性洞察",

            # 自动化与编排引擎
            "execution_enhancement_engine": "追踪执行效果，分析执行策略并自适应优化",
            "module_linkage_engine": "跨模块协同工作，自动组合多个模块协同响应",
            "service_orchestration_optimizer": "追踪端到端执行路径，发现瓶颈并生成优化建议",
            "cross_engine_optimizer": "分析引擎间协同模式，识别跨引擎优化机会",

            # 创新与进化引擎
            "intelligent_evolution_engine": "基于历史执行数据自动分析自身表现，持续优化决策",
            "evolution_strategy_engine": "根据系统状态和历史自动调整进化方向和优先级",
            "evolution_learning_engine": "从历史进化结果中学习，不断优化进化方向选择",
            "evolution_meta_learning_engine": "分析进化历史，识别进化模式并自动调整策略",
            "innovation_discovery_engine": "主动发现人没想到但很有用的新能力组合",
            "creative_generation_engine": "主动发现创新解决方案，生成超越期望的创意建议",
            "meta_evolution_engine": "统一的元进化层，集成所有进化引擎能力",

            # 多模态交互引擎
            "voice_interaction_engine": "响应语音输入，实现语音交互体验",
            "tts_engine": "语音合成，让系统能用语音回复用户",
            "emotion_engine": "感知用户情绪并做出有温度的响应",
            "ui_structure_engine": "解析界面元素层级，识别可交互组件",

            # 文件与操作引擎
            "file_manager_engine": "按类型/时间整理文件，提供搜索、分类功能",
            "code_understanding_engine": "代码结构分析、依赖检测、代码质量评估",
            "file_metadata_engine": "文件元数据提取、标签管理、智能分类",

            # 守护与协作引擎
            "daemon_linkage_engine": "跨守护进程任务传递和自动触发",
            "multi_agent_collaboration_engine": "引擎间任务自动分配、进度追踪、问题升级",
            "cross_device_engine": "发现和控制同一网络内的其他设备",

            # 质量保障引擎
            "auto_quality_assurance_engine": "自动测试各引擎功能，验证进化成果",
            "auto_engine_repair_engine": "基于检测结果自动分析失败原因并尝试修复",
            "scene_test_engine": "自动测试场景计划可用性，检测失效计划",
            "scene_plan_auto_repair_engine": "根据优化建议自动分析问题并执行修复",

            # 诊断与错误处理
            "error_diagnosis_engine": "智能错误诊断与根因分析",
            "error_pattern_learning_engine": "从执行历史学习错误模式，预测潜在问题",
            "system_diagnostic_engine": "跨模块综合诊断，生成统一诊断报告",

            # 其他专业引擎
            "meeting_assistant_engine": "管理会议、记录纪要、生成待办事项",
            "workflow_strategy_learner": "从工作流执行历史中学习最优执行策略",
            "system_dashboard_engine": "整合所有监控数据提供统一系统状态视图",
            "realtime_guidance_engine": "实时观察用户操作，识别动作，预测意图并提供辅助",
            "full_auto_service_engine": "统一的智能主动服务入口，实现预测→决策→执行→反馈闭环",

            # 新增分析引擎
            "multi_dim_analysis_engine": "多维融合智能分析，统一态势感知与跨引擎协同增强",
            "multi_dimension_fusion_engine": "融合多源数据，提供统一分析和决策支持",
            "unified_service_hub": "整合所有智能服务能力，提供统一的自然语言服务入口"
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

    def explain_why_not(self, task_description: str, candidate_engines: list, selected_engines: list) -> str:
        """
        解释为什么没有选择某些候选引擎

        Args:
            task_description: 任务描述
            candidate_engines: 所有候选引擎列表
            selected_engines: 被选中的引擎列表

        Returns:
            自然语言解释
        """
        not_selected = [e for e in candidate_engines if e not in selected_engines]

        if not not_selected:
            return "所有候选引擎都被选中了，没有被排除的引擎。"

        explanations = []
        explanations.append(f"任务「{task_description}」中未被选中的引擎分析：\n")

        for engine in not_selected:
            desc = self.engine_descriptions.get(engine, "执行特定任务")
            explanations.append(f"[X] **{engine}**：{desc}")
            explanations.append(f"   → 未被选中的原因：该引擎的能力与当前任务需求不直接匹配，"
                               f"或已有其他更合适的引擎覆盖了此功能")

        explanations.append("\n**选择决策总结**：")
        explanations.append(f"系统从 {len(candidate_engines)} 个候选引擎中选择了 "
                           f"{len(selected_engines)} 个最合适的引擎来执行任务。")

        return "\n".join(explanations)

    def explain_confidence(self, task_description: str, selected_engines: list, confidence_scores: dict) -> str:
        """
        解释决策置信度

        Args:
            task_description: 任务描述
            selected_engines: 被选中的引擎列表
            confidence_scores: 各引擎的置信度分数

        Returns:
            置信度解释
        """
        explanations = []
        explanations.append(f"任务「{task_description}」的决策置信度分析：\n")

        for engine in selected_engines:
            score = confidence_scores.get(engine, 0.5)
            confidence_level = "高" if score > 0.8 else ("中" if score > 0.5 else "低")

            explanations.append(f"[OK] **{engine}**：置信度 {score:.0%}（{confidence_level}）")

            if score > 0.8:
                explanations.append(f"   → 该引擎与任务高度匹配，选择理由充分")
            elif score > 0.5:
                explanations.append(f"   → 该引擎与任务较为匹配，作为备选或辅助")
            else:
                explanations.append(f"   → 该引擎可能不是最佳选择，但作为兜底方案")

        avg_confidence = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0
        explanations.append(f"\n**整体决策置信度**：{avg_confidence:.0%}")

        if avg_confidence > 0.8:
            explanations.append("→ 系统对这个决策非常有信心")
        elif avg_confidence > 0.6:
            explanations.append("→ 系统对这个决策有一定把握，但可能需要人工确认")
        else:
            explanations.append("→ 系统对这个决策信心不足，建议用户提供更多指导")

        return "\n".join(explanations)

    def explain_reasoning_chain(self, task: str, reasoning_steps: list) -> str:
        """
        解释完整的推理链条

        Args:
            task: 用户任务
            reasoning_steps: 推理步骤列表

        Returns:
            推理链解释
        """
        explanations = []
        explanations.append(f"**任务理解**：{task}\n")

        explanations.append("**推理过程**：")
        for i, step in enumerate(reasoning_steps, 1):
            step_type = step.get("type", "unknown")
            content = step.get("content", "")
            conclusion = step.get("conclusion", "")

            explanations.append(f"\n{i}. 【{step_type}】{content}")
            if conclusion:
                explanations.append(f"   → 推理结论：{conclusion}")

        explanations.append("\n**最终决策**：")
        if reasoning_steps:
            final = reasoning_steps[-1]
            explanations.append(f"基于以上 {len(reasoning_steps)} 步推理，系统做出了最终决策")

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
                "执行过程实时解说 - 逐步解释当前操作的原因",
                "未选中引擎解释 - 说明为什么某些候选引擎未被选中",
                "决策置信度解释 - 解释每个决策的置信度及其含义",
                "推理链解释 - 展示从理解任务到做出决策的完整推理过程"
            ],
            "supported_engines_count": len(self.engine_descriptions),
            "supported_engines": list(self.engine_descriptions.keys()),
            "commands": {
                "explain_recommendation": "解释引擎推荐理由",
                "explain_workflow": "解释工作流执行路径",
                "explain_failure": "分析失败原因",
                "explain_progress": "说明执行进度",
                "explain_why_not": "解释为什么未选中某些引擎",
                "explain_confidence": "解释决策置信度",
                "explain_reasoning": "解释完整推理链"
            }
        }


def main():
    """CLI 入口"""
    import argparse

    parser = argparse.ArgumentParser(description="智能决策可解释性增强器")
    parser.add_argument("action", nargs="?", default="status",
                        choices=["status", "explain", "workflow", "failure", "progress", "why_not", "confidence", "reasoning"],
                        help="执行的操作")
    parser.add_argument("--task", "-t", help="任务描述")
    parser.add_argument("--engines", "-e", nargs="+", help="引擎列表")
    parser.add_argument("--candidates", "-c", nargs="+", help="候选引擎列表（用于 why_not）")
    parser.add_argument("--scores", "-s", type=json.loads, help="置信度分数（JSON格式，用于 confidence）")
    parser.add_argument("--steps", type=json.loads, help="工作流步骤（JSON）")
    parser.add_argument("--step-index", type=int, help="失败步骤索引")
    parser.add_argument("--error", help="错误信息")
    parser.add_argument("--completed", type=int, default=0, help="已完成步骤数")
    parser.add_argument("--remaining", type=int, default=0, help="剩余步骤数")
    parser.add_argument("--reasoning-steps", type=json.loads, help="推理步骤（JSON格式，用于 reasoning）")

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
    elif args.action == "why_not":
        if not args.task or not args.candidates or not args.engines:
            print("错误：需要提供 --task、--candidates（候选引擎）和 --engines（选中引擎）参数")
            return
        print(engine.explain_why_not(args.task, args.candidates, args.engines))
    elif args.action == "confidence":
        if not args.task or not args.engines or not args.scores:
            print("错误：需要提供 --task、--engines 和 --scores 参数")
            return
        print(engine.explain_confidence(args.task, args.engines, args.scores))
    elif args.action == "reasoning":
        if not args.task or not args.reasoning_steps:
            print("错误：需要提供 --task 和 --reasoning-steps 参数")
            return
        print(engine.explain_reasoning_chain(args.task, args.reasoning_steps))


if __name__ == "__main__":
    main()