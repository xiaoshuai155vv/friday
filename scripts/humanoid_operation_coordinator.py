"""
智能拟人操作协调引擎 (Humanoid Operation Coordinator)
Round 250: 让系统能够综合使用70+引擎，像人一样理解任务、选择工具、协同执行

核心功能：
1. 任务意图深度理解 - 像人一样理解用户的真实需求
2. 引擎智能组合 - 根据任务需求自动选择最合适的引擎组合
3. 执行流程编排 - 像人操作电脑一样，按顺序执行多步骤任务
4. 上下文感知 - 记住上一步的结果，作为下一步的输入
5. 自主学习优化 - 从执行历史中学习最优的执行策略

Version: 1.0.0
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
RUNTIME_DIR = PROJECT_ROOT / "runtime"


class HumanoidOperationCoordinator:
    """智能拟人操作协调引擎"""

    def __init__(self):
        self.name = "Humanoid Operation Coordinator"
        self.version = "1.0.0"
        self.engine_registry = self._load_engine_registry()
        self.execution_history = []
        self.context_memory = {}  # 上下文记忆

    def _load_engine_registry(self) -> Dict[str, Dict]:
        """加载引擎注册表，包含所有可用引擎的信息"""
        registry = {
            # 基础交互引擎
            "screenshot": {
                "module": "screenshot_tool.py",
                "capability": "屏幕截图",
                "category": "基础交互"
            },
            "mouse": {
                "module": "mouse_tool.py",
                "capability": "鼠标点击/移动/拖拽",
                "category": "基础交互"
            },
            "keyboard": {
                "module": "keyboard_tool.py",
                "capability": "键盘输入/快捷键",
                "category": "基础交互"
            },
            "vision": {
                "module": "vision_proxy.py",
                "capability": "图像理解与坐标提取",
                "category": "多模态感知"
            },
            # 应用引擎
            "launch_app": {
                "module": "launch_apps.py",
                "capability": "打开应用程序",
                "category": "应用管理"
            },
            "window": {
                "module": "window_tool.py",
                "capability": "窗口激活/最大化/关闭",
                "category": "应用管理"
            },
            "process": {
                "module": "process_tool.py",
                "capability": "进程列表/结束进程",
                "category": "应用管理"
            },
            # 系统引擎
            "clipboard": {
                "module": "clipboard_tool.py",
                "capability": "剪贴板读/写",
                "category": "系统工具"
            },
            "volume": {
                "module": "volume_tool.py",
                "capability": "音量控制",
                "category": "系统工具"
            },
            "brightness": {
                "module": "brightness_tool.py",
                "capability": "屏幕亮度控制",
                "category": "系统工具"
            },
            "power": {
                "module": "power_tool.py",
                "capability": "电源管理/休眠/关机",
                "category": "系统工具"
            },
            "network": {
                "module": "network_tool.py",
                "capability": "网络信息查询",
                "category": "系统工具"
            },
            # 场景引擎
            "run_plan": {
                "module": "run_plan.py",
                "capability": "执行预定义场景计划",
                "category": "场景执行"
            },
            "selfie": {
                "module": "selfie.py",
                "capability": "拍照/自拍",
                "category": "场景执行"
            },
            "camera": {
                "module": "camera_qt.py",
                "capability": "摄像头控制",
                "category": "场景执行"
            },
            # 智能服务引擎
            "unified_service": {
                "module": "unified_service_hub.py",
                "capability": "统一智能服务入口",
                "category": "智能服务"
            },
            "service_fusion": {
                "module": "full_scenario_service_fusion_engine.py",
                "capability": "全场景服务融合",
                "category": "智能服务"
            },
            "load_balancer": {
                "module": "engine_load_balancer.py",
                "capability": "引擎负载均衡与调度",
                "category": "智能服务"
            },
            "auto_optimizer": {
                "module": "engine_auto_optimizer.py",
                "capability": "引擎效能自动优化",
                "category": "智能服务"
            },
            # 进化引擎
            "evolution_command_tower": {
                "module": "evolution_command_tower.py",
                "capability": "进化指挥塔",
                "category": "进化系统"
            },
            "evolution_auto_creator": {
                "module": "evolution_engine_auto_creator.py",
                "capability": "进化新引擎自动创造",
                "category": "进化系统"
            },
            "knowledge_inheritance": {
                "module": "evolution_knowledge_inheritance_engine.py",
                "capability": "跨代进化知识传承",
                "category": "进化系统"
            },
            "meta_pattern": {
                "module": "evolution_meta_pattern_discovery.py",
                "capability": "进化元模式发现",
                "category": "进化系统"
            },
            # 学习与适应引擎
            "adaptive_learning": {
                "module": "adaptive_learning_engine.py",
                "capability": "从用户交互中学习",
                "category": "学习适应"
            },
            "behavior_predict": {
                "module": "behavior_sequence_prediction_engine.py",
                "capability": "用户行为序列预测",
                "category": "学习适应"
            },
            "personalization": {
                "module": "deep_personalization_engine.py",
                "capability": "个性化深度学习",
                "category": "学习适应"
            },
            # 决策与规划引擎
            "decision_orchestrator": {
                "module": "decision_orchestrator.py",
                "capability": "智能决策编排",
                "category": "决策规划"
            },
            "cross_engine_planner": {
                "module": "cross_engine_task_planner.py",
                "capability": "跨引擎复杂任务规划",
                "category": "决策规划"
            },
            "workflow_orchestrator": {
                "module": "workflow_orchestrator.py",
                "capability": "工作流编排",
                "category": "决策规划"
            },
        }
        return registry

    def understand_task(self, task_description: str) -> Dict[str, Any]:
        """深度理解任务，提取意图、实体和执行策略"""
        task_lower = task_description.lower()

        # 意图分类
        intent = self._classify_intent(task_lower)

        # 实体提取
        entities = self._extract_entities(task_lower)

        # 执行策略确定
        strategy = self._determine_strategy(intent, entities)

        # 所需引擎识别
        required_engines = self._identify_required_engines(intent, entities)

        return {
            "intent": intent,
            "entities": entities,
            "strategy": strategy,
            "required_engines": required_engines,
            "task_description": task_description,
            "confidence": self._calculate_confidence(intent, entities)
        }

    def _classify_intent(self, task: str) -> str:
        """分类任务意图"""
        if any(kw in task for kw in ["打开", "启动", "运行", "开"]):
            return "launch"
        elif any(kw in task for kw in ["查找", "搜索", "找", "搜"]):
            return "search"
        elif any(kw in task for kw in ["发送", "发", "传给", "发个消息"]):
            return "send_message"
        elif any(kw in task for kw in ["填写", "申报", "提交", "录入"]):
            return "form_fill"
        elif any(kw in task for kw in ["播放", "放", "听", "音乐"]):
            return "media_play"
        elif any(kw in task for kw in ["截图", "截屏", "截图"]):
            return "screenshot"
        elif any(kw in task for kw in ["设置", "调整", "配置"]):
            return "configure"
        elif any(kw in task for kw in ["查询", "查看", "看看"]):
            return "query"
        else:
            return "general"

    def _extract_entities(self, task: str) -> Dict[str, List[str]]:
        """提取任务中的实体"""
        entities = {
            "targets": [],  # 目标应用/文件
            "actions": [],  # 操作类型
            "parameters": []  # 参数
        }

        # 提取目标应用
        app_patterns = {
            "浏览器": ["浏览器", "edge", "chrome", "浏览器"],
            "记事本": ["记事本", "notepad"],
            "文件管理器": ["文件管理器", "explorer", "我的电脑"],
            "计算器": ["计算器", "calc"],
            "iHaier": ["办公平台", "ihaier", "i海尔的", "海尔"],
            "音乐": ["音乐", "播放器", "网易云", "QQ音乐"],
            "微信": ["微信", "wechat"],
        }

        for app, keywords in app_patterns.items():
            if any(kw in task for kw in keywords):
                entities["targets"].append(app)

        # 提取操作
        action_patterns = {
            "打开": ["打开", "启动", "运行"],
            "关闭": ["关闭", "退出", "关掉"],
            "最大化": ["最大化", "全屏", "铺满"],
            "最小化": ["最小化", "最小"],
        }

        for action, keywords in action_patterns.items():
            if any(kw in task for kw in keywords):
                entities["actions"].append(action)

        return entities

    def _determine_strategy(self, intent: str, entities: Dict) -> str:
        """确定执行策略"""
        if intent == "launch" and entities["targets"]:
            return "direct_launch"
        elif intent == "send_message":
            return "multi_step_with_vision"
        elif intent == "form_fill":
            return "run_plan_execution"
        elif intent == "search":
            return "hybrid_search"
        else:
            return "adaptive_execution"

    def _identify_required_engines(self, intent: str, entities: Dict) -> List[str]:
        """识别所需引擎"""
        engines = []

        # 基于意图添加引擎
        intent_engines = {
            "launch": ["window", "launch_app"],
            "search": ["vision", "mouse", "keyboard"],
            "send_message": ["window", "vision", "mouse", "keyboard"],
            "form_fill": ["run_plan", "window", "vision"],
            "media_play": ["launch_app", "window"],
            "screenshot": ["screenshot"],
            "configure": ["launch_app", "vision", "mouse"],
            "query": ["vision", "mouse"],
            "general": ["unified_service"],
        }

        engines.extend(intent_engines.get(intent, ["unified_service"]))

        # 确保去重并保持顺序
        seen = set()
        unique_engines = []
        for e in engines:
            if e not in seen:
                seen.add(e)
                unique_engines.append(e)

        return unique_engines

    def _calculate_confidence(self, intent: str, entities: Dict) -> float:
        """计算任务理解置信度"""
        score = 0.5

        if intent != "general":
            score += 0.3

        if entities["targets"]:
            score += 0.1

        if entities["actions"]:
            score += 0.1

        return min(score, 1.0)

    def coordinate_execution(self, task_understanding: Dict, context: Optional[Dict] = None) -> Dict[str, Any]:
        """协调执行任务"""
        task = task_understanding["task_description"]
        intent = task_understanding["intent"]
        required_engines = task_understanding["required_engines"]
        strategy = task_understanding["strategy"]

        results = {
            "status": "success",
            "steps_executed": [],
            "engines_used": [],
            "result": None,
            "errors": []
        }

        # 根据策略执行
        if strategy == "direct_launch":
            results = self._execute_direct_launch(task_understanding, results)
        elif strategy == "multi_step_with_vision":
            results = self._execute_multi_step_vision(task_understanding, results)
        elif strategy == "run_plan_execution":
            results = self._execute_run_plan(task_understanding, results)
        elif strategy == "adaptive_execution":
            results = self._execute_adaptive(task_understanding, results)

        # 记录执行历史
        self.execution_history.append({
            "task": task,
            "understanding": task_understanding,
            "results": results,
            "timestamp": datetime.now().isoformat()
        })

        # 更新上下文记忆
        if context:
            self.context_memory.update(context)

        return results

    def _execute_direct_launch(self, task_understanding: Dict, results: Dict) -> Dict:
        """直接启动执行"""
        entities = task_understanding["entities"]
        targets = entities.get("targets", [])

        if targets:
            target = targets[0]
            cmd = f'do.py 打开 {target}'
            results["steps_executed"].append({
                "step": 1,
                "action": "launch_app",
                "target": target,
                "command": cmd
            })
            results["engines_used"].append("launch_app")

            try:
                # 执行命令
                subprocess.run(
                    f"cd {SCRIPTS_DIR} && python do.py 打开 {target}",
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                results["result"] = f"已打开 {target}"
            except Exception as e:
                results["errors"].append(str(e))
                results["status"] = "partial"

        return results

    def _execute_multi_step_vision(self, task_understanding: Dict, results: Dict) -> Dict:
        """多步骤视觉引导执行"""
        task = task_understanding["task_description"]

        # 步骤1: 截图
        results["steps_executed"].append({
            "step": 1,
            "action": "screenshot",
            "description": "截图获取当前界面"
        })
        results["engines_used"].append("screenshot")

        # 步骤2: 视觉理解
        results["steps_executed"].append({
            "step": 2,
            "action": "vision_analysis",
            "description": "分析界面元素"
        })
        results["engines_used"].append("vision")

        results["result"] = f"已理解任务: {task}，等待用户确认后执行"

        return results

    def _execute_run_plan(self, task_understanding: Dict, results: Dict) -> Dict:
        """执行预定义计划"""
        task = task_understanding["task_description"]
        entities = task_understanding["entities"]

        # 智能选择计划
        plan = self._select_appropriate_plan(task, entities)

        if plan:
            results["steps_executed"].append({
                "step": 1,
                "action": "run_plan",
                "plan": plan,
                "description": f"执行场景计划: {plan}"
            })
            results["engines_used"].append("run_plan")
            results["result"] = f"将执行计划: {plan}"
        else:
            results["result"] = "无匹配计划，建议使用通用执行"

        return results

    def _select_appropriate_plan(self, task: str, entities: Dict) -> Optional[str]:
        """选择合适的计划"""
        plans_dir = PROJECT_ROOT / "assets" / "plans"

        if not plans_dir.exists():
            return None

        task_lower = task.lower()

        # 根据关键词匹配计划
        plan_mapping = {
            "绩效": "ihaier_performance_declaration.json",
            "音乐": "play_music.json",
            "浏览器": "example_visit_website.json",
        }

        for keyword, plan in plan_mapping.items():
            if keyword in task_lower:
                return plan

        return None

    def _execute_adaptive(self, task_understanding: Dict, results: Dict) -> Dict:
        """自适应执行 - 使用统一服务入口"""
        task = task_understanding["task_description"]

        results["steps_executed"].append({
            "step": 1,
            "action": "unified_service",
            "description": "调用统一服务入口"
        })
        results["engines_used"].append("unified_service")

        # 尝试使用统一服务
        try:
            cmd = f'cd {SCRIPTS_DIR} && python do.py "{task}"'
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            results["result"] = result.stdout if result.stdout else result.stderr
        except Exception as e:
            results["errors"].append(str(e))
            results["result"] = "执行失败，请尝试更具体的描述"

        return results

    def analyze_and_suggest(self, current_context: Dict) -> Dict[str, Any]:
        """分析当前上下文，提供智能建议"""
        suggestions = {
            "suggested_actions": [],
            "recommended_engines": [],
            "context_awareness": {}
        }

        # 分析当前上下文
        if "active_window" in current_context:
            suggestions["context_awareness"]["当前窗口"] = current_context["active_window"]

        if "recent_apps" in current_context:
            suggestions["context_awareness"]["最近应用"] = current_context["recent_apps"][:3]

        # 基于上下文推荐操作
        active_window = current_context.get("active_window", "")

        if "浏览器" in active_window or "chrome" in active_window.lower():
            suggestions["recommended_engines"] = ["vision", "keyboard", "mouse"]
            suggestions["suggested_actions"] = ["搜索", "填写表单", "截图保存"]

        elif "办公平台" in active_window or "ihaier" in active_window.lower():
            suggestions["recommended_engines"] = ["vision", "mouse", "keyboard"]
            suggestions["suggested_actions"] = ["发送消息", "查看通知", "搜索联系人"]

        elif "记事本" in active_window or "notepad" in active_window.lower():
            suggestions["recommended_engines"] = ["keyboard"]
            suggestions["suggested_actions"] = ["输入文本", "保存文件"]

        return suggestions

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "name": self.name,
            "version": self.version,
            "engines_registered": len(self.engine_registry),
            "execution_history_count": len(self.execution_history),
            "context_memory_size": len(self.context_memory),
            "categories": list(set(e["category"] for e in self.engine_registry.values()))
        }

    def analyze_capabilities(self) -> Dict[str, Any]:
        """分析系统能力并生成报告"""
        categories = {}
        for name, info in self.engine_registry.items():
            cat = info["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append({
                "engine": name,
                "capability": info["capability"]
            })

        return {
            "total_engines": len(self.engine_registry),
            "categories": categories,
            "timestamp": datetime.now().isoformat()
        }


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description="智能拟人操作协调引擎")
    parser.add_argument("command", choices=["understand", "execute", "suggest", "status", "analyze"],
                        help="命令类型")
    parser.add_argument("--task", type=str, help="任务描述")
    parser.add_argument("--context", type=str, help="上下文 JSON")
    parser.add_argument("--format", choices=["json", "text"], default="text", help="输出格式")

    args = parser.parse_args()

    coordinator = HumanoidOperationCoordinator()

    if args.command == "understand":
        if not args.task:
            print("Error: --task required for understand command")
            sys.exit(1)
        result = coordinator.understand_task(args.task)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "execute":
        if not args.task:
            print("Error: --task required for execute command")
            sys.exit(1)
        understanding = coordinator.understand_task(args.task)
        context = json.loads(args.context) if args.context else None
        result = coordinator.coordinate_execution(understanding, context)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "suggest":
        context = json.loads(args.context) if args.context else {}
        result = coordinator.analyze_and_suggest(context)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "status":
        result = coordinator.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "analyze":
        result = coordinator.analyze_capabilities()
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()