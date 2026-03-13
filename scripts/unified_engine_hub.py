#!/usr/bin/env python3
"""
智能跨引擎协同调度中心 (Unified Engine Hub)

功能：
1. 引擎能力统一注册与管理
2. 智能场景识别与引擎推荐
3. 跨引擎任务编排与执行
4. 统一的引擎状态监控

集成已有引擎：
- workflow_quality_engine (工作流质量)
- script_generation_engine (脚本生成)
- task_planning_engine (任务规划)
- meeting_assistant_engine (会议助手)
- data_insight_engine (数据洞察)
- long_term_memory_engine (长期记忆)
- innovation_discovery_engine (创新发现)
- self_evolution_optimizer (自我进化)
- workflow_auto_generator (工作流自动生成)
- deep_personalization_engine (深度个性化)
- enhanced_knowledge_reasoning_engine (知识推理)
- system_diagnostic_engine (系统诊断)
- proactive_notification_engine (主动通知)
- 以及其他引擎...
"""

import json
import os
import sys
import importlib.util
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
ENGINES_DIR = PROJECT_ROOT / "scripts"


class UnifiedEngineHub:
    """智能跨引擎协同调度中心"""

    def __init__(self):
        self.engines: Dict[str, Dict[str, Any]] = {}
        self.engine_registry_path = PROJECT_ROOT / "runtime" / "state" / "engine_registry.json"
        self._load_or_init_registry()

    def _load_or_init_registry(self):
        """加载或初始化引擎注册表"""
        if self.engine_registry_path.exists():
            try:
                with open(self.engine_registry_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.engines = data.get('engines', {})
            except Exception as e:
                print(f"加载引擎注册表失败: {e}")
                self.engines = {}
        else:
            self.engines = {}
            self._scan_and_register_engines()

    def _scan_and_register_engines(self):
        """扫描并注册所有引擎模块"""
        engine_files = [
            # 核心引擎
            ("workflow_quality_engine", "工作流质量", "监控工作流执行质量，分析失败原因并生成优化建议"),
            ("script_generation_engine", "脚本生成", "根据自然语言需求自动生成可执行脚本"),
            ("task_planning_engine", "任务规划", "理解高级目标，自动分解为可执行步骤"),
            ("meeting_assistant_engine", "会议助手", "管理会议、记录会议纪要、生成待办事项"),
            ("data_insight_engine", "数据洞察", "整合运行数据、深度分析和可视化"),
            ("long_term_memory_engine", "长期记忆", "记住用户长期目标、跨会话习惯和偏好"),
            ("innovation_discovery_engine", "创新发现", "主动发现新能力、新用法、新组合"),
            ("self_healing_engine", "自愈引擎", "自动检测问题、分析原因并尝试修复"),
            ("workflow_auto_generator", "工作流自动生成", "根据自然语言需求自动生成可执行计划"),
            ("deep_personalization_engine", "深度个性化", "基于多维度用户数据进行个性化推荐"),
            ("enhanced_knowledge_reasoning_engine", "知识推理", "因果推理、类比推理、知识关联发现"),
            ("system_diagnostic_engine", "系统诊断", "跨模块问题追踪和综合诊断"),
            ("proactive_notification_engine", "主动通知", "主动推送有价值的信息和建议"),
            ("predictive_prevention_engine", "预测预防", "问题发生前主动发现并预防"),
            ("adaptive_learning_engine", "自适应学习", "从交互历史中学习行为模式"),
            ("module_linkage_engine", "模块联动", "跨模块协同工作、智能场景模式识别"),
            ("code_understanding_engine", "代码理解", "代码结构分析、依赖检测、重构建议"),
            ("decision_orchestrator", "决策编排", "综合分析用户意图和系统状态"),
            ("context_awareness_engine", "情境感知", "感知当前环境、时间、用户状态"),
            ("active_suggestion_engine", "主动建议", "根据系统状态主动推送建议"),
            ("file_manager_engine", "文件管理", "自动整理文件、搜索、分析、智能分类"),
            ("conversation_manager", "对话管理", "多轮对话和上下文记忆"),
            ("emotion_engine", "情感识别", "感知用户情绪并做出响应"),
            ("voice_interaction_engine", "语音交互", "响应语音输入"),
            ("tts_engine", "语音合成", "用语音回复用户"),
            ("scenario_recommender", "场景推荐", "根据用户习惯主动推荐场景计划"),
            ("evolution_coordinator", "进化协调", "统一现有进化模块接口"),
            ("evolution_strategy_engine", "进化策略", "根据系统状态和历史自动调整进化方向"),
            ("evolution_log_analyzer", "进化日志分析", "进化过程可视化和分析"),
            ("evolution_self_evaluator", "进化自评", "进化环自身的性能评估"),
            ("unified_recommender", "统一推荐", "整合多种推荐能力"),
            ("feedback_learning_engine", "推荐反馈学习", "根据用户接受/拒绝行为优化推荐"),
            ("intelligent_service_loop", "智能服务闭环", "预测→决策→执行→反馈完整自动化"),
            ("adaptive_priority_engine", "自适应优先级", "根据系统负载动态调整优先级"),
            ("workflow_smart_recommender", "工作流智能推荐", "基于历史推荐合适工作流"),
        ]

        for engine_name, display_name, description in engine_files:
            self.engines[engine_name] = {
                "name": display_name,
                "description": description,
                "registered_at": datetime.now().isoformat(),
                "status": "ready"
            }

        self._save_registry()

    def _save_registry(self):
        """保存引擎注册表"""
        self.engine_registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.engine_registry_path, 'w', encoding='utf-8') as f:
            json.dump({
                "engines": self.engines,
                "updated_at": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)

    def get_all_engines(self) -> Dict[str, Dict[str, Any]]:
        """获取所有已注册的引擎"""
        return self.engines

    def get_engine_info(self, engine_name: str) -> Optional[Dict[str, Any]]:
        """获取指定引擎的信息"""
        return self.engines.get(engine_name)

    def search_engines(self, keyword: str) -> List[Dict[str, Any]]:
        """根据关键词搜索引擎"""
        keyword = keyword.lower()
        results = []
        for name, info in self.engines.items():
            if (keyword in name.lower() or
                keyword in info.get("name", "").lower() or
                keyword in info.get("description", "").lower()):
                results.append({
                    "engine_name": name,
                    **info
                })
        return results

    def recommend_engines(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """根据上下文智能推荐引擎

        context 包含:
        - user_intent: 用户意图
        - time_of_day: 时间段
        - system_state: 系统状态
        - recent_activities: 最近活动
        """
        recommendations = []
        user_intent = context.get("user_intent", "").lower()
        time_of_day = context.get("time_of_day", "")
        system_state = context.get("system_state", {})

        # 根据用户意图推荐引擎
        intent_engine_mapping = {
            "工作流": ["workflow_quality_engine", "workflow_auto_generator", "workflow_smart_recommender"],
            "脚本": ["script_generation_engine"],
            "任务": ["task_planning_engine", "workflow_engine"],
            "会议": ["meeting_assistant_engine"],
            "数据": ["data_insight_engine"],
            "记忆": ["long_term_memory_engine"],
            "创新": ["innovation_discovery_engine"],
            "问题": ["self_healing_engine", "system_diagnostic_engine"],
            "预测": ["predictive_prevention_engine"],
            "学习": ["adaptive_learning_engine", "deep_personalization_engine"],
            "知识": ["enhanced_knowledge_reasoning_engine", "knowledge_graph"],
            "代码": ["code_understanding_engine"],
            "文件": ["file_manager_engine"],
            "对话": ["conversation_manager", "emotion_engine"],
            "语音": ["voice_interaction_engine", "tts_engine"],
            "通知": ["proactive_notification_engine"],
            "推荐": ["unified_recommender", "scenario_recommender", "feedback_learning_engine"],
            "决策": ["decision_orchestrator"],
            "场景": ["context_awareness_engine", "scenario_recommender", "module_linkage_engine"],
            "进化": ["evolution_strategy_engine", "evolution_coordinator", "self_healing_engine"],
        }

        for intent, engine_list in intent_engine_mapping.items():
            if intent in user_intent:
                for engine in engine_list:
                    if engine in self.engines:
                        recommendations.append({
                            "engine_name": engine,
                            **self.engines[engine],
                            "reason": f"用户意图「{intent}」相关"
                        })

        # 根据时间段推荐
        if time_of_day:
            if "morning" in time_of_day or "上午" in time_of_day:
                recommendations.append({
                    "engine_name": "meeting_assistant_engine",
                    **self.engines.get("meeting_assistant_engine", {}),
                    "reason": "早晨适合查看会议安排"
                })
            elif "afternoon" in time_of_day or "下午" in time_of_day:
                recommendations.append({
                    "engine_name": "data_insight_engine",
                    **self.engines.get("data_insight_engine", {}),
                    "reason": "下午适合查看数据报告"
                })

        # 去重并返回
        seen = set()
        unique_results = []
        for rec in recommendations:
            if rec["engine_name"] not in seen:
                seen.add(rec["engine_name"])
                unique_results.append(rec)

        return unique_results

    def orchestrate_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """跨引擎任务编排

        task 包含:
        - goal: 目标描述
        - required_engines: 需要调用的引擎列表
        - context: 上下文信息
        """
        goal = task.get("goal", "")
        required_engines = task.get("required_engines", [])
        context = task.get("context", {})

        results = []
        for engine_name in required_engines:
            if engine_name in self.engines:
                results.append({
                    "engine": engine_name,
                    "status": "ready",
                    "info": self.engines[engine_name]
                })
            else:
                results.append({
                    "engine": engine_name,
                    "status": "not_found"
                })

        return {
            "goal": goal,
            "orchestration": results,
            "total_engines": len(required_engines),
            "available": len([r for r in results if r["status"] == "ready"])
        }

    def get_stats(self) -> Dict[str, Any]:
        """获取引擎统计信息"""
        return {
            "total_engines": len(self.engines),
            "engines": list(self.engines.keys()),
            "categories": {
                "workflow": len([e for e in self.engines if "workflow" in e]),
                "learning": len([e for e in self.engines if "learning" in e or "personalization" in e]),
                "intelligence": len([e for e in self.engines if "intelligent" in e or "smart" in e]),
                "analysis": len([e for e in self.engines if "analysis" in e or "insight" in e]),
                "interaction": len([e for e in self.engines if "interaction" in e or "emotion" in e]),
                "system": len([e for e in self.engines if "system" in e or "diagnostic" in e]),
            },
            "updated_at": datetime.now().isoformat()
        }


def main():
    """主入口 - 支持的命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="智能跨引擎协同调度中心")
    parser.add_argument("command", choices=["list", "search", "recommend", "orchestrate", "stats"],
                        help="要执行的命令")
    parser.add_argument("--keyword", "-k", help="搜索关键词")
    parser.add_argument("--intent", "-i", help="用户意图")
    parser.add_argument("--engines", "-e", nargs="+", help="需要调度的引擎列表")
    parser.add_argument("--goal", "-g", help="任务目标描述")

    args = parser.parse_args()
    hub = UnifiedEngineHub()

    if args.command == "list":
        engines = hub.get_all_engines()
        print(f"\n=== 已注册的引擎 ({len(engines)} 个) ===\n")
        for name, info in engines.items():
            print(f"  {name}")
            print(f"    名称: {info.get('name', 'N/A')}")
            print(f"    描述: {info.get('description', 'N/A')}")
            print()

    elif args.command == "search":
        if not args.keyword:
            print("请提供搜索关键词 --keyword")
            sys.exit(1)
        results = hub.search_engines(args.keyword)
        print(f"\n=== 搜索「{args.keyword}」结果 ({len(results)} 个) ===\n")
        for r in results:
            print(f"  {r['engine_name']}")
            print(f"    名称: {r.get('name', 'N/A')}")
            print(f"    描述: {r.get('description', 'N/A')}")
            print()

    elif args.command == "recommend":
        intent = args.intent or "一般任务"
        context = {"user_intent": intent}
        results = hub.recommend_engines(context)
        print(f"\n=== 推荐引擎 (意图: {intent}) ({len(results)} 个) ===\n")
        for r in results:
            print(f"  {r['engine_name']}")
            print(f"    原因: {r.get('reason', 'N/A')}")
            print()

    elif args.command == "orchestrate":
        if not args.engines or not args.goal:
            print("请提供任务目标 --goal 和引擎列表 --engines")
            sys.exit(1)
        task = {
            "goal": args.goal,
            "required_engines": args.engines,
            "context": {}
        }
        result = hub.orchestrate_task(task)
        print(f"\n=== 任务编排结果 ===")
        print(f"目标: {result['goal']}")
        print(f"总引擎数: {result['total_engines']}")
        print(f"可用引擎: {result['available']}")
        print("\n编排详情:")
        for r in result['orchestration']:
            status = "✓" if r['status'] == "ready" else "✗"
            print(f"  {status} {r['engine']}: {r['status']}")

    elif args.command == "stats":
        stats = hub.get_stats()
        print(f"\n=== 引擎统计 ===")
        print(f"总引擎数: {stats['total_engines']}")
        print(f"\n分类统计:")
        for cat, count in stats['categories'].items():
            print(f"  {cat}: {count}")


if __name__ == "__main__":
    main()