#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能创意生成与评估引擎 (Creative Generation & Evaluation Engine)

功能：让系统能够主动发现"人没想到但很有用的"新能力组合、生成创新解决方案、提供超越用户期望的创意建议。

核心能力：
1. 创新组合发现 - 分析现有60+引擎能力，识别潜在有用组合
2. 创意解决方案生成 - 根据用户需求/问题生成创新解决方案
3. 创新评估 - 评估创意的价值、可行性和潜在影响
4. 主动创意建议 - 主动向用户推荐超越期望的创意

与 innovation_discovery_engine 的区别：
- innovation_discovery: 被动发现已有能力的新用法
- creative_generation: 主动生成全新的创意组合和解决方案

集成：
- engine_combination_recommender: 引擎能力分析
- innovation_discovery_engine: 已有创新发现
- unified_recommender: 统一推荐
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import defaultdict
from itertools import combinations

# 路径处理
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)


class CreativeGenerationEngine:
    """智能创意生成与评估引擎"""

    def __init__(self):
        self.name = "Creative Generation Engine"
        self.version = "1.0.0"
        self.state_file = os.path.join(PROJECT_ROOT, "runtime", "state", "creative_generation_state.json")
        self.creatives_file = os.path.join(PROJECT_ROOT, "runtime", "state", "creative_ideas.json")

        # 已注册的引擎能力（60+引擎）
        self.registered_engines = {
            # 基础交互引擎
            "screenshot": {"category": "基础交互", "capabilities": ["截图", "视觉理解"]},
            "mouse": {"category": "基础交互", "capabilities": ["点击", "拖拽", "右键"]},
            "keyboard": {"category": "基础交互", "capabilities": ["输入", "快捷键"]},
            "vision": {"category": "基础交互", "capabilities": ["图像理解", "坐标提取"]},

            # 应用控制引擎
            "launch_app": {"category": "应用控制", "capabilities": ["打开应用", "启动应用"]},
            "window": {"category": "应用控制", "capabilities": ["窗口管理", "激活", "最大化"]},
            "process": {"category": "应用控制", "capabilities": ["进程管理", "结束进程"]},

            # 数据处理引擎
            "clipboard": {"category": "数据处理", "capabilities": ["读取", "写入", "图片"]},
            "file_tool": {"category": "数据处理", "capabilities": ["文件操作", "目录操作"]},
            "knowledge_graph": {"category": "数据处理", "capabilities": ["知识存储", "知识推理"]},

            # 智能引擎
            "conversation_execution": {"category": "智能服务", "capabilities": ["意图理解", "对话执行"]},
            "decision_orchestrator": {"category": "智能服务", "capabilities": ["智能决策", "引擎调度"]},
            "workflow_engine": {"category": "智能服务", "capabilities": ["工作流编排", "任务规划"]},
            "cross_engine_task_planner": {"category": "智能服务", "capabilities": ["任务规划", "跨引擎协同"]},
            "intent_deep_reasoning": {"category": "智能服务", "capabilities": ["意图推理", "深层理解"]},

            # 学习与适应引擎
            "adaptive_learning": {"category": "学习适应", "capabilities": ["行为学习", "偏好适应"]},
            "feedback_learning": {"category": "学习适应", "capabilities": ["反馈学习", "策略优化"]},
            "workflow_strategy_learner": {"category": "学习适应", "capabilities": ["策略学习", "执行优化"]},
            "task_preference": {"category": "学习适应", "capabilities": ["偏好记忆", "任务偏好"]},
            "deep_personalization": {"category": "学习适应", "capabilities": ["深度个性化", "行为预测"]},

            # 预测与主动服务引擎
            "predictive_prevention": {"category": "预测服务", "capabilities": ["问题预测", "主动预防"]},
            "proactive_insight": {"category": "预测服务", "capabilities": ["主动洞察", "需求预测"]},
            "proactive_decision_action": {"category": "预测服务", "capabilities": ["主动决策", "自动执行"]},
            "intelligent_service_loop": {"category": "预测服务", "capabilities": ["智能服务闭环", "主动服务"]},

            # 系统管理引擎
            "system_health": {"category": "系统管理", "capabilities": ["健康监控", "性能分析"]},
            "self_healing": {"category": "系统管理", "capabilities": ["问题诊断", "自动修复"]},
            "daemon_manager": {"category": "系统管理", "capabilities": ["守护进程", "后台服务"]},

            # 知识与推理引擎
            "knowledge_evolution": {"category": "知识推理", "capabilities": ["知识进化", "知识更新"]},
            "enhanced_knowledge_reasoning": {"category": "知识推理", "capabilities": ["因果推理", "类比推理"]},
            "context_awareness": {"category": "知识推理", "capabilities": ["情境感知", "环境理解"]},

            # 场景与推荐引擎
            "scenario_recommender": {"category": "场景推荐", "capabilities": ["场景推荐", "场景联动"]},
            "unified_recommender": {"category": "场景推荐", "capabilities": ["统一推荐", "综合推荐"]},
            "workflow_smart_recommender": {"category": "场景推荐", "capabilities": ["工作流推荐", "智能推荐"]},
            "engine_combination_recommender": {"category": "场景推荐", "capabilities": ["引擎组合推荐", "智能组合"]},

            # 自动化引擎
            "workflow_auto_generator": {"category": "自动化", "capabilities": ["工作流自动生成", "计划生成"]},
            "automation_pattern_discovery": {"category": "自动化", "capabilities": ["模式发现", "场景自动生成"]},
            "task_continuation": {"category": "自动化", "capabilities": ["任务接续", "跨会话"]},
            "proactive_service_trigger": {"category": "自动化", "capabilities": ["条件触发", "自动服务"]},

            # 通信与通知引擎
            "notification": {"category": "通信", "capabilities": ["推送通知", "主动提醒"]},
            "email": {"category": "通信", "capabilities": ["邮件发送", "邮件读取"]},

            # 媒体引擎
            "voice_interaction": {"category": "媒体", "capabilities": ["语音识别", "语音交互"]},
            "tts": {"category": "媒体", "capabilities": ["语音合成", "TTS"]},
            "camera": {"category": "媒体", "capabilities": ["摄像头", "拍照"]},

            # 特定场景引擎
            "ihaier": {"category": "特定场景", "capabilities": ["企业通讯", "办公自动化"]},
            "meeting_assistant": {"category": "特定场景", "capabilities": ["会议管理", "会议纪要"]},
            "file_manager": {"category": "特定场景", "capabilities": ["文件管理", "智能分类"]},
            "play_music": {"category": "特定场景", "capabilities": ["音乐播放", "媒体控制"]},

            # 进化引擎
            "evolution_coordinator": {"category": "进化", "capabilities": ["进化协调", "自动进化"]},
            "evolution_strategy": {"category": "进化", "capabilities": ["策略分析", "方向选择"]},
            "evolution_loop_automation": {"category": "进化", "capabilities": ["闭环自动化", "持续进化"]},
            "evolution_meta_learning": {"category": "进化", "capabilities": ["元学习", "模式识别"]},
            "autonomous_learning_innovation": {"category": "进化", "capabilities": ["自主学习", "自我创新"]},
        }

        # 创意模式库
        self.creative_patterns = {
            "chain_reaction": {
                "name": "链式反应创意",
                "description": "当A引擎执行后，自动触发B引擎，形成自动化链",
                "example": "截图→vision分析→自动执行对应动作"
            },
            "cross_domain": {
                "name": "跨域融合创意",
                "description": "将不同领域的引擎能力组合创造新价值",
                "example": "知识图谱+预测引擎→主动推荐"
            },
            "enhancement": {
                "name": "增强型创意",
                "description": "在现有能力基础上增强功能",
                "example": "基础截图+AI理解=智能截图"
            },
            "automation": {
                "name": "自动化创意",
                "description": "将手动操作变为自动化流程",
                "example": "定期自动整理文件+主动通知"
            },
            "prediction": {
                "name": "预测型创意",
                "description": "基于历史数据预测未来需求",
                "example": "学习用户行为→提前准备"
            },
            "creative_composition": {
                "name": "创造性组合",
                "description": "将看似无关的能力组合产生新功能",
                "example": "摄像头+知识图谱+通知=智能看护"
            }
        }

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "name": self.name,
            "version": self.version,
            "engines_count": len(self.registered_engines),
            "creative_patterns": len(self.creative_patterns),
            "state_file": self.state_file,
            "capabilities": [
                "创新组合发现",
                "创意解决方案生成",
                "创新评估",
                "主动创意建议"
            ]
        }

    def discover_innovative_combinations(self, min_value: str = "中") -> List[Dict[str, Any]]:
        """发现创新组合 - 分析现有引擎能力，识别潜在有用组合"""
        value_map = {"高": 3, "中": 2, "低": 1}
        min_value_level = value_map.get(min_value, 2)

        # 预定义的创新组合（基于60+引擎能力）
        innovative_combos = [
            {
                "id": "combo_001",
                "name": "智能自动化工作流生成器",
                "description": "结合用户行为学习+模式发现+工作流自动生成，实现从重复行为到自动执行的完整闭环",
                "engines": ["adaptive_learning", "automation_pattern_discovery", "workflow_auto_generator", "proactive_service_trigger"],
                "categories": ["学习适应", "自动化", "智能服务"],
                "value": "高",
                "feasibility": "高",
                "impact": "用户无需手动创建工作流，系统自动发现并生成"
            },
            {
                "id": "combo_002",
                "name": "主动问题预防系统",
                "description": "结合系统健康监控+预测预防+主动决策+自动修复，实现问题发生前主动预防",
                "engines": ["system_health", "predictive_prevention", "proactive_decision_action", "self_healing"],
                "categories": ["系统管理", "预测服务", "智能服务"],
                "value": "高",
                "feasibility": "高",
                "impact": "系统自动维护，大幅减少用户干预"
            },
            {
                "id": "combo_003",
                "name": "个性化智能助手",
                "description": "结合深度个性化+意图深度推理+任务偏好，为每个用户提供定制化服务",
                "engines": ["deep_personalization", "intent_deep_reasoning", "task_preference", "feedback_learning"],
                "categories": ["学习适应", "智能服务"],
                "value": "高",
                "feasibility": "高",
                "impact": "系统越来越懂你，提供精准服务"
            },
            {
                "id": "combo_004",
                "name": "智能创意工作流引擎",
                "description": "结合创意生成+引擎组合推荐+跨引擎任务规划+执行增强，实现端到端智能服务",
                "engines": ["creative_generation", "engine_combination_recommender", "cross_engine_task_planner", "execution_enhancement"],
                "categories": ["智能服务", "场景推荐"],
                "value": "高",
                "feasibility": "中",
                "impact": "用户只需描述需求，系统自动生成完整解决方案"
            },
            {
                "id": "combo_005",
                "name": "知识进化与洞察系统",
                "description": "结合知识进化+增强知识推理+主动洞察，实现知识的自我进化和主动分享",
                "engines": ["knowledge_evolution", "enhanced_knowledge_reasoning", "proactive_insight"],
                "categories": ["知识推理", "预测服务"],
                "value": "中",
                "feasibility": "高",
                "impact": "系统主动学习和分享知识"
            },
            {
                "id": "combo_006",
                "name": "跨会话智能记忆系统",
                "description": "结合长期记忆+任务接续+情境感知，跨越对话记住用户意图和任务",
                "engines": ["long_term_memory", "task_continuation", "context_awareness", "cross_engine_task_planner"],
                "categories": ["知识推理", "自动化", "智能服务"],
                "value": "高",
                "feasibility": "高",
                "impact": "用户关闭对话后再打开，系统记住之前的工作"
            },
            {
                "id": "combo_007",
                "name": "智能会议与日程闭环",
                "description": "结合会议助手+主动通知+情境感知+任务偏好，实现智能会议管理",
                "engines": ["meeting_assistant", "notification", "context_awareness", "task_preference"],
                "categories": ["特定场景", "通信", "学习适应"],
                "value": "中",
                "feasibility": "高",
                "impact": "系统主动管理会议，提醒准备材料，跟踪待办"
            },
            {
                "id": "combo_008",
                "name": "多模态智能交互中心",
                "description": "结合语音交互+TTS+视觉理解+情感识别，提供全方位智能交互",
                "engines": ["voice_interaction", "tts", "vision", "emotion_engine"],
                "categories": ["基础交互", "媒体"],
                "value": "高",
                "feasibility": "中",
                "impact": "用户可以用语音、视觉等多种方式与系统交互"
            }
        ]

        # 过滤按价值等级
        filtered = [
            c for c in innovative_combos
            if value_map.get(c["value"], 0) >= min_value_level
        ]

        return filtered

    def generate_creative_solution(self, user_problem: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """生成创意解决方案 - 根据用户问题生成创新解决方案"""
        # 分析问题类型
        problem_keywords = {
            "complex": ["复杂", "多步骤", "一系列", "一系列操作"],
            "efficiency": ["更快", "效率", "自动化", "省事"],
            "smart": ["智能", "主动", "预测", "懂我"],
            "personalized": ["定制", "个人", "习惯", "偏好"],
            "diagnosis": ["问题", "错误", "故障", "诊断"],
            "knowledge": ["知识", "学习", "了解", "分析"]
        }

        # 中文类型映射
        type_mapping = {
            "complex": "复杂任务",
            "efficiency": "效率提升",
            "smart": "智能化",
            "personalized": "个性化",
            "diagnosis": "问题诊断",
            "knowledge": "知识",
            "general": "通用"
        }

        problem_type_key = "general"
        for kw_type, keywords in problem_keywords.items():
            if any(kw in user_problem for kw in keywords):
                problem_type_key = kw_type
                break

        # 根据问题类型生成创意方案（使用英文key避免编码问题）
        solutions = {
            "complex": {
                "title": "智能任务规划与执行闭环",
                "description": "使用跨引擎任务规划器分析需求，自动拆分子任务，协调多个引擎协同执行，追踪进度并反馈结果",
                "steps": [
                    "1. 使用 intent_deep_reasoning 理解深层需求",
                    "2. 使用 cross_engine_task_planner 拆分任务",
                    "3. 使用 decision_orchestrator 调度引擎",
                    "4. 使用 task_continuation 追踪状态",
                    "5. 使用 notification 反馈结果"
                ],
                "engines": ["intent_deep_reasoning", "cross_engine_task_planner", "decision_orchestrator", "task_continuation", "notification"]
            },
            "efficiency": {
                "title": "自动化效率提升方案",
                "description": "通过模式发现自动识别重复操作，使用工作流自动生成和条件触发实现全自动化",
                "steps": [
                    "1. 使用 adaptive_learning 分析行为模式",
                    "2. 使用 automation_pattern_discovery 发现可自动化模式",
                    "3. 使用 workflow_auto_generator 生成自动化工作流",
                    "4. 使用 proactive_service_trigger 设置触发条件",
                    "5. 自动执行并持续优化"
                ],
                "engines": ["adaptive_learning", "automation_pattern_discovery", "workflow_auto_generator", "proactive_service_trigger"]
            },
            "smart": {
                "title": "主动智能服务方案",
                "description": "系统主动感知环境、学习习惯、预测需求，在用户开口前主动提供服务",
                "steps": [
                    "1. 使用 context_awareness 感知当前情境",
                    "2. 使用 deep_personalization 分析用户习惯",
                    "3. 使用 proactive_insight 预测需求",
                    "4. 使用 proactive_decision_action 生成行动计划",
                    "5. 主动执行或建议用户确认"
                ],
                "engines": ["context_awareness", "deep_personalization", "proactive_insight", "proactive_decision_action"]
            },
            "personalized": {
                "title": "深度个性化服务方案",
                "description": "记住用户的偏好、习惯和风格，每次服务都比上次更懂用户",
                "steps": [
                    "1. 使用 task_preference 记录任务偏好",
                    "2. 使用 feedback_learning 学习反馈",
                    "3. 使用 deep_personalization 深度分析",
                    "4. 使用 intent_deep_reasoning 理解独特需求",
                    "5. 自动应用到每次服务中"
                ],
                "engines": ["task_preference", "feedback_learning", "deep_personalization", "intent_deep_reasoning"]
            },
            "diagnosis": {
                "title": "智能诊断与自愈方案",
                "description": "系统自动检测问题、分析原因，尝试自动修复或提供解决方案",
                "steps": [
                    "1. 使用 system_health 监控系统状态",
                    "2. 使用 self_healing 诊断问题",
                    "3. 使用 predictive_prevention 预测潜在问题",
                    "4. 自动尝试修复或建议方案",
                    "5. 记录学习避免重复问题"
                ],
                "engines": ["system_health", "self_healing", "predictive_prevention"]
            },
            "knowledge": {
                "title": "智能知识进化方案",
                "description": "系统自动从交互中学习知识、更新知识图谱，主动提供洞察",
                "steps": [
                    "1. 使用 knowledge_evolution 提取新知识",
                    "2. 使用 knowledge_graph 更新知识图谱",
                    "3. 使用 enhanced_knowledge_reasoning 推理关联",
                    "4. 使用 proactive_insight 生成主动洞察",
                    "5. 分享给用户或应用到服务中"
                ],
                "engines": ["knowledge_evolution", "knowledge_graph", "enhanced_knowledge_reasoning", "proactive_insight"]
            },
            "general": {
                "title": "通用智能解决方案",
                "description": "综合使用多种引擎能力，为用户提供定制化的智能服务方案",
                "steps": [
                    "1. 使用 intent_deep_reasoning 理解需求",
                    "2. 使用 cross_engine_task_planner 规划任务",
                    "3. 使用 decision_orchestrator 选择最佳引擎组合",
                    "4. 使用 workflow_engine 执行工作流",
                    "5. 使用 notification 反馈执行结果"
                ],
                "engines": ["intent_deep_reasoning", "cross_engine_task_planner", "decision_orchestrator", "workflow_engine", "notification"]
            }
        }

        solution = solutions.get(problem_type_key, solutions["general"])
        problem_type_display = type_mapping.get(problem_type_key, "通用")

        return {
            "problem": user_problem,
            "problem_type": problem_type_display,
            "solution": solution,
            "confidence": 0.85 if problem_type_key != "general" else 0.7,
            "timestamp": datetime.now().isoformat()
        }

    def evaluate_creativity(self, creative_id: Optional[str] = None) -> Dict[str, Any]:
        """评估创意 - 评估已有创意的价值和可行性"""
        # 如果指定了创意ID，评估该创意
        if creative_id:
            combos = self.discover_innovative_combinations(min_value="低")
            target = next((c for c in combos if c["id"] == creative_id), None)
            if target:
                return self._evaluate_single_creative(target)

        # 否则评估所有创意
        combos = self.discover_innovative_combinations(min_value="中")
        evaluations = [self._evaluate_single_creative(c) for c in combos]

        return {
            "total_evaluated": len(evaluations),
            "high_value_count": sum(1 for e in evaluations if e["value_rating"] == "高"),
            "high_feasibility_count": sum(1 for e in evaluations if e["feasibility_rating"] == "高"),
            "recommendations": sorted(evaluations, key=lambda x: x["overall_score"], reverse=True)[:3],
            "timestamp": datetime.now().isoformat()
        }

    def _evaluate_single_creative(self, creative: Dict) -> Dict[str, Any]:
        """评估单个创意"""
        value_score = {"高": 5, "中": 3, "低": 1}.get(creative.get("value", "中"), 3)
        feasibility_score = {"高": 5, "中": 3, "low": 1}.get(creative.get("feasibility", "中"), 3)

        # 引擎数量加分（组合越多说明越复杂有价值）
        engine_count = len(creative.get("engines", []))
        complexity_score = min(engine_count * 0.5, 3)

        overall_score = (value_score + feasibility_score + complexity_score) / 3

        return {
            "id": creative.get("id"),
            "name": creative.get("name"),
            "value_rating": creative.get("value", "中"),
            "feasibility_rating": creative.get("feasibility", "中"),
            "overall_score": round(overall_score, 2),
            "value_explanation": f"组合{engine_count}个引擎，覆盖{','.join(creative.get('categories', []))}",
            "impact": creative.get("impact", "")
        }

    def suggest_creatives(self, context: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """主动创意建议 - 根据当前上下文主动推荐创意"""
        suggestions = []

        # 基于时间段的建议
        hour = datetime.now().hour
        if 9 <= hour < 12:
            suggestions.append({
                "type": "时段推荐",
                "title": "早晨效率方案",
                "description": "使用智能任务规划+主动洞察，为一天的工作做好准备",
                "creatives": ["combo_001", "combo_003"]
            })
        elif 14 <= hour < 18:
            suggestions.append({
                "type": "时段推荐",
                "title": "下午生产力提升",
                "description": "使用模式发现+自动化工作流，减少重复劳动",
                "creatives": ["combo_001"]
            })

        # 基于系统状态
        if context and context.get("low_resources"):
            suggestions.append({
                "type": "系统状态推荐",
                "title": "资源优化方案",
                "description": "使用问题预防+自愈系统，优化系统资源",
                "creatives": ["combo_002"]
            })

        # 默认推荐
        suggestions.extend([
            {
                "type": "推荐",
                "title": "智能自动化工作流",
                "description": "从重复行为自动生成自动化工作流，节省时间",
                "creatives": ["combo_001"],
                "priority": "高"
            },
            {
                "type": "推荐",
                "title": "个性化智能助手",
                "description": "让系统越来越懂你，每次服务都比上次更精准",
                "creatives": ["combo_003"],
                "priority": "中"
            }
        ])

        return suggestions


def main():
    """CLI 入口"""
    import argparse
    parser = argparse.ArgumentParser(description="智能创意生成与评估引擎")
    parser.add_argument("command", nargs="?", default="status",
                       choices=["status", "discover", "generate", "evaluate", "suggest"],
                       help="命令: status/discover/generate/evaluate/suggest")
    parser.add_argument("--problem", "-p", type=str, help="用户问题描述（用于generate命令）")
    parser.add_argument("--context", "-c", type=str, help="上下文JSON（用于generate/suggest命令）")
    parser.add_argument("--creative-id", type=str, help="创意ID（用于evaluate命令）")
    parser.add_argument("--min-value", type=str, default="中", choices=["高", "中", "低"],
                       help="最小价值等级（用于discover命令）")

    args = parser.parse_args()
    engine = CreativeGenerationEngine()

    if args.command == "status":
        print(json.dumps(engine.get_status(), ensure_ascii=False, indent=2))
    elif args.command == "discover":
        result = engine.discover_innovative_combinations(min_value=args.min_value)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "generate":
        problem = args.problem or "帮我更高效地完成工作"
        context = json.loads(args.context) if args.context else None
        result = engine.generate_creative_solution(problem, context)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "evaluate":
        result = engine.evaluate_creativity(args.creative_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "suggest":
        context = json.loads(args.context) if args.context else None
        result = engine.suggest_creatives(context)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()