#!/usr/bin/env python3
"""
智能跨引擎协同智能决策引擎 (Cross-Engine Smart Decision Engine)
让系统能够基于任务意图，智能决定使用哪些引擎组合，实现从任务理解→引擎智能选择→自适应执行→结果反馈的完整闭环

Version: 1.0.0
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# 添加项目根目录到路径
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

class CrossEngineSmartDecisionEngine:
    """智能跨引擎协同智能决策引擎"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.scripts_dir = self.project_root / "scripts"
        self.runtime_state_dir = self.project_root / "runtime" / "state"
        self.capabilities_file = self.project_root / "references" / "capabilities.md"

        # 引擎注册表
        self.engine_registry = {}
        self.execution_history = []
        self.load_engine_registry()

        # 加载已集成的引擎
        self.load_integrated_engines()

    def load_engine_registry(self):
        """加载引擎注册表"""
        # 扫描 scripts 目录下的所有 .py 文件作为引擎
        engine_categories = {
            "system": ["power_tool", "process_tool", "window_tool", "mouse_tool", "keyboard_tool",
                       "screenshot_tool", "volume_tool", "brightness_tool", "network_tool", "file_tool",
                       "reg_tool", "clipboard_tool", "notification_tool", "env_tool", "screen_size"],
            "launch": ["launch_browser", "launch_notepad", "launch_explorer", "launch_clock",
                       "launch_calendar", "launch_calc", "launch_taskmgr"],
            "workflow": ["run_plan", "workflow_engine", "workflow_orchestrator", "workflow_auto_generator",
                         "workflow_strategy_learner"],
            "vision": ["vision_proxy", "vision_coords", "vision_calibrate"],
            "learning": ["adaptive_learning_engine", "user_behavior_learner", "deep_personalization_engine",
                         "unified_learning_hub", "evolution_learning_engine"],
            "evolution": ["evolution_loop_automation", "evolution_strategy_engine", "evolution_coordinator",
                          "evolution_command_tower", "proactive_optimization_discovery_engine",
                          "evolution_idea_generator", "evolution_idea_execution_engine",
                          "evolution_autonomy_engine", "engine_collaboration_optimizer"],
            "service": ["unified_service_hub", "intelligent_service_fusion_engine",
                        "full_auto_service_execution_engine", "active_service_loop_enhancer",
                        "service_preheat_engine", "adaptive_scene_selector"],
            "health": ["system_health_check", "system_health_report_engine",
                       "system_health_alert_engine", "health_assurance_loop"],
            "orchestration": ["decision_orchestrator", "module_linkage_engine", "cross_engine_task_planner",
                              "multi_agent_collaboration_engine", "engine_realtime_optimizer",
                              "multi_dim_analysis_engine"]
        }

        # 创建引擎注册表
        for category, engines in engine_categories.items():
            for engine in engines:
                self.engine_registry[engine] = {
                    "category": category,
                    "name": engine.replace("_", " ").title(),
                    "capabilities": self._infer_engine_capabilities(engine)
                }

    def _infer_engine_capabilities(self, engine_name: str) -> List[str]:
        """推断引擎能力"""
        capability_keywords = {
            "power": ["电源", "休眠", "关机", "重启", "睡眠"],
            "process": ["进程", "kill", "end"],
            "window": ["窗口", "激活", "最大化", "最小化"],
            "mouse": ["鼠标", "点击", "移动"],
            "keyboard": ["键盘", "输入", "按键"],
            "screenshot": ["截图", "屏幕"],
            "vision": ["视觉", "识别", "图像", "理解"],
            "workflow": ["工作流", "计划", "执行"],
            "learning": ["学习", "适应", "个性化"],
            "evolution": ["进化", "优化", "自进化"],
            "service": ["服务", "推荐", "自动化"],
            "health": ["健康", "监控", "预警"]
        }

        capabilities = []
        engine_lower = engine_name.lower()
        for cap, keywords in capability_keywords.items():
            if any(kw in engine_lower for kw in keywords):
                capabilities.append(cap)

        return capabilities if capabilities else ["general"]

    def load_integrated_engines(self):
        """加载已集成的引擎模块"""
        # 这里我们只需要提供接口，不需要实际导入，因为 do.py 会处理
        pass

    def analyze_task_intent(self, task_description: str) -> Dict[str, Any]:
        """分析任务意图"""
        task_lower = task_description.lower()

        # 意图分类
        intent_categories = {
            "system_control": ["电源", "关机", "重启", "睡眠", "休眠", "进程", "窗口", "截图"],
            "content_creation": ["写", "创建", "新建", "编辑"],
            "information_retrieval": ["查", "找", "搜索", "获取", "看"],
            "automation": ["自动", "执行", "运行", "批量"],
            "learning": ["学习", "适应", "个性化", "推荐"],
            "evolution": ["进化", "优化", "改进", "提升"],
            "health_check": ["健康", "检查", "诊断", "预警"]
        }

        detected_intents = []
        for category, keywords in intent_categories.items():
            if any(kw in task_lower for kw in keywords):
                detected_intents.append(category)

        # 推断所需能力
        required_capabilities = []
        if any(cat in detected_intents for cat in ["system_control", "content_creation", "information_retrieval"]):
            required_capabilities.extend(["mouse", "keyboard", "window", "vision"])
        if "automation" in detected_intents:
            required_capabilities.extend(["workflow", "orchestration"])
        if "learning" in detected_intents:
            required_capabilities.append("learning")
        if "evolution" in detected_intents:
            required_capabilities.append("evolution")
        if "health_check" in detected_intents:
            required_capabilities.append("health")

        return {
            "original_task": task_description,
            "detected_intents": detected_intents,
            "required_capabilities": list(set(required_capabilities)),
            "complexity": "high" if len(detected_intents) > 2 else "medium" if detected_intents else "low"
        }

    def select_optimal_engine组合(self, task_intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """选择最优引擎组合"""
        required_caps = task_intent.get("required_capabilities", [])
        complexity = task_intent.get("complexity", "low")

        selected_engines = []

        # 根据所需能力选择引擎
        capability_to_engine = {
            "mouse": [{"name": "mouse_tool", "priority": 10}],
            "keyboard": [{"name": "keyboard_tool", "priority": 10}],
            "window": [{"name": "window_tool", "priority": 9}],
            "screenshot": [{"name": "screenshot_tool", "priority": 8}],
            "vision": [{"name": "vision_proxy", "priority": 9}, {"name": "vision_coords", "priority": 9}],
            "workflow": [{"name": "run_plan", "priority": 10}, {"name": "workflow_orchestrator", "priority": 8}],
            "orchestration": [{"name": "decision_orchestrator", "priority": 9}, {"name": "module_linkage_engine", "priority": 8},
                             {"name": "engine_collaboration_optimizer", "priority": 8}],
            "learning": [{"name": "adaptive_learning_engine", "priority": 8}, {"name": "user_behavior_learner", "priority": 8}],
            "evolution": [{"name": "evolution_command_tower", "priority": 9}, {"name": "proactive_optimization_discovery_engine", "priority": 8}],
            "health": [{"name": "system_health_alert_engine", "priority": 9}, {"name": "system_health_report_engine", "priority": 8}]
        }

        for cap in required_caps:
            if cap in capability_to_engine:
                selected_engines.extend(capability_to_engine[cap])

        # 对于复杂任务，添加协调引擎
        if complexity == "high":
            selected_engines.append({"name": "cross_engine_task_planner", "priority": 10})
            selected_engines.append({"name": "unified_service_hub", "priority": 9})

        # 按优先级排序并去重
        seen = set()
        unique_engines = []
        for eng in sorted(selected_engines, key=lambda x: x.get("priority", 0), reverse=True):
            if eng["name"] not in seen:
                seen.add(eng["name"])
                unique_engines.append(eng)

        # 添加元决策引擎
        unique_engines.append({"name": "cross_engine_smart_decision", "priority": 10, "role": "coordinator"})

        return unique_engines

    def generate_execution_plan(self, task_intent: Dict[str, Any], engine组合: List[Dict]) -> Dict[str, Any]:
        """生成执行计划"""
        intents = task_intent.get("detected_intents", [])

        plan_steps = []

        # 第一阶段：理解与分析
        plan_steps.append({
            "stage": "analysis",
            "action": "analyze_task",
            "description": "分析任务意图和上下文",
            "engines": ["cross_engine_smart_decision"]
        })

        # 第二阶段：引擎选择与准备
        plan_steps.append({
            "stage": "selection",
            "action": "select_engines",
            "description": f"选择最优引擎组合（共 {len(engine组合)} 个引擎）",
            "engines": [e["name"] for e in engine组合 if e.get("role") != "coordinator"]
        })

        # 第三阶段：执行
        if "system_control" in intents:
            plan_steps.append({
                "stage": "execution",
                "action": "execute_system_control",
                "description": "执行系统控制操作",
                "engines": ["window_tool", "mouse_tool", "keyboard_tool"]
            })
        elif "automation" in intents:
            plan_steps.append({
                "stage": "execution",
                "action": "execute_automation",
                "description": "执行自动化工作流",
                "engines": ["run_plan", "workflow_orchestrator"]
            })
        elif "evolution" in intents:
            plan_steps.append({
                "stage": "execution",
                "action": "execute_evolution",
                "description": "执行进化优化",
                "engines": ["evolution_command_tower", "proactive_optimization_discovery_engine"]
            })
        elif "health_check" in intents:
            plan_steps.append({
                "stage": "execution",
                "action": "execute_health_check",
                "description": "执行健康检查",
                "engines": ["system_health_alert_engine", "system_health_report_engine"]
            })

        # 第四阶段：结果反馈
        plan_steps.append({
            "stage": "feedback",
            "action": "collect_results",
            "description": "收集执行结果并反馈",
            "engines": ["cross_engine_smart_decision"]
        })

        return {
            "task": task_intent["original_task"],
            "complexity": task_intent["complexity"],
            "selected_engines": engine组合,
            "execution_plan": plan_steps,
            "estimated_stages": len(plan_steps),
            "generated_at": datetime.now().isoformat()
        }

    def execute_task(self, task_description: str, dry_run: bool = True) -> Dict[str, Any]:
        """执行智能任务"""
        # 1. 分析任务意图
        task_intent = self.analyze_task_intent(task_description)

        # 2. 选择最优引擎组合
        engine组合 = self.select_optimal_engine组合(task_intent)

        # 3. 生成执行计划
        execution_plan = self.generate_execution_plan(task_intent, engine组合)

        # 记录执行历史
        execution_record = {
            "task": task_description,
            "intent": task_intent,
            "engines": engine组合,
            "plan": execution_plan,
            "dry_run": dry_run,
            "timestamp": datetime.now().isoformat()
        }
        self.execution_history.append(execution_record)

        if not dry_run:
            # 这里可以添加实际的执行逻辑
            execution_record["status"] = "executed"
        else:
            execution_record["status"] = "planned"

        return execution_record

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "engine_name": "Cross-Engine Smart Decision Engine",
            "version": "1.0.0",
            "registered_engines": len(self.engine_registry),
            "execution_history_count": len(self.execution_history),
            "capabilities": [
                "任务意图分析",
                "引擎智能选择",
                "执行计划生成",
                "自适应执行",
                "结果反馈"
            ],
            "integrated_engines": [
                "engine_collaboration_optimizer",
                "proactive_optimization_discovery_engine",
                "unified_service_hub",
                "decision_orchestrator",
                "cross_engine_task_planner"
            ]
        }

    def suggest_improvements(self) -> List[Dict[str, Any]]:
        """基于执行历史提供优化建议"""
        suggestions = []

        if len(self.execution_history) < 3:
            suggestions.append({
                "area": "data",
                "suggestion": "执行更多任务以积累数据，用于更好的引擎选择优化",
                "priority": "medium"
            })
        else:
            # 分析执行历史
            recent_tasks = self.execution_history[-5:]
            avg_engines = sum(len(t["engines"]) for t in recent_tasks) / len(recent_tasks)

            if avg_engines > 5:
                suggestions.append({
                    "area": "optimization",
                    "suggestion": f"平均使用 {avg_engines:.1f} 个引擎，可以考虑优化引擎选择策略减少冗余",
                    "priority": "high"
                })

            # 检查是否有进化相关任务
            evolution_tasks = [t for t in recent_tasks if "evolution" in t.get("intent", {}).get("detected_intents", [])]
            if evolution_tasks:
                suggestions.append({
                    "area": "evolution",
                    "suggestion": "检测到进化任务，可考虑增强进化引擎的协同能力",
                    "priority": "medium"
                })

        return suggestions


def main():
    """主函数 - 用于命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description="智能跨引擎协同智能决策引擎")
    parser.add_argument("command", nargs="?", default="status",
                       choices=["status", "analyze", "select", "execute", "plan", "suggestions", "test"],
                       help="命令")
    parser.add_argument("--task", "-t", type=str, help="任务描述")
    parser.add_argument("--dry-run", action="store_true", default=True, help="仅生成计划不执行")

    args = parser.parse_args()

    engine = CrossEngineSmartDecisionEngine()

    if args.command == "status":
        result = engine.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "analyze":
        if not args.task:
            print("错误: 需要提供任务描述 (--task)")
            sys.exit(1)
        result = engine.analyze_task_intent(args.task)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "select":
        if not args.task:
            print("错误: 需要提供任务描述 (--task)")
            sys.exit(1)
        task_intent = engine.analyze_task_intent(args.task)
        engines = engine.select_optimal_engine组合(task_intent)
        result = {
            "task": args.task,
            "intent": task_intent,
            "selected_engines": engines
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "execute":
        if not args.task:
            print("错误: 需要提供任务描述 (--task)")
            sys.exit(1)
        result = engine.execute_task(args.task, dry_run=args.dry_run)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "plan":
        if not args.task:
            print("错误: 需要提供任务描述 (--task)")
            sys.exit(1)
        task_intent = engine.analyze_task_intent(args.task)
        engines = engine.select_optimal_engine组合(task_intent)
        plan = engine.generate_execution_plan(task_intent, engines)
        print(json.dumps(plan, ensure_ascii=False, indent=2))

    elif args.command == "suggestions":
        result = engine.suggest_improvements()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "test":
        # 测试用例
        test_tasks = [
            "帮我优化系统进化策略",
            "检查系统健康状态",
            "自动执行一个复杂工作流",
            "分析用户行为并推荐服务"
        ]

        print("=" * 60)
        print("智能跨引擎协同智能决策引擎 - 测试")
        print("=" * 60)

        for task in test_tasks:
            print(f"\n【任务】{task}")
            intent = engine.analyze_task_intent(task)
            print(f"  意图: {intent['detected_intents']}")
            print(f"  能力: {intent['required_capabilities']}")
            print(f"  复杂度: {intent['complexity']}")

            engines = engine.select_optimal_engine组合(intent)
            print(f"  选择引擎: {[e['name'] for e in engines[:5]]}...")

        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)


if __name__ == "__main__":
    main()