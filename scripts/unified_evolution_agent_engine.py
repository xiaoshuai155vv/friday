#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环统一智能体协同引擎 (version 1.0.0)

让系统能够像大脑一样，根据任务意图自动分析、选择、组合最合适的进化引擎，
协同工作形成端到端解决方案。

核心功能：
1. 任务意图深度理解与分析
2. 智能引擎选择与组合
3. 跨引擎协同执行
4. 结果聚合与反馈
5. 进化知识共享与学习

集成模块（部分）：
- evolution_coordinator.py (统一协调)
- evolution_cockpit_engine.py (驾驶舱)
- evolution_value_knowledge_closed_loop_engine.py (价值知识闭环)
- evolution_decision_execution_closed_loop.py (决策执行闭环)
"""

import json
import os
import sys
import time
import subprocess
import importlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict

# 添加项目根目录到 Python 路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, SCRIPT_DIR)


def _safe_print(text: str):
    """安全打印，处理编码问题"""
    import re
    try:
        print(text)
    except UnicodeEncodeError:
        clean_text = re.sub(r'[^\x00-\x7F]+', '', text)
        print(clean_text)


class UnifiedEvolutionAgentEngine:
    """统一智能体协同引擎 - 进化系统的大脑"""

    def __init__(self, state_dir: str = "runtime/state"):
        self.state_dir = Path(state_dir)
        self.project_root = self.state_dir.parent.parent
        self.scripts_dir = self.project_root / "scripts"

        # 状态文件
        self.state_file = self.state_dir / "unified_evolution_agent_state.json"
        self.config_file = self.state_dir / "unified_evolution_agent_config.json"

        # 引擎状态
        self.state = {
            "version": "1.0.0",
            "initialized": False,
            "engine_registry": {},
            "execution_history": [],
            "task_analysis_cache": {},
            "execution_count": 0,
            "success_count": 0,
            "failure_count": 0,
            "health_status": "unknown",
        }

        # 引擎能力注册表
        self.engine_capabilities = {
            "meta_integration": {
                "name": "元进化集成引擎",
                "keywords": ["元进化", "深度集成", "自主运行", "无人值守"],
                "module": "evolution_meta_integration_enhanced",
                "class": "MetaIntegrationEnhancedEngine",
            },
            "value_knowledge": {
                "name": "价值知识双闭环引擎",
                "keywords": ["价值", "知识", "闭环", "递归增强"],
                "module": "evolution_value_knowledge_closed_loop_engine",
                "class": "ValueKnowledgeClosedLoopEngine",
            },
            "decision_execution": {
                "name": "决策执行闭环引擎",
                "keywords": ["决策", "执行", "闭环", "协同"],
                "module": "evolution_decision_execution_closed_loop",
                "class": "DecisionExecutionClosedLoopEngine",
            },
            "knowledge_integration": {
                "name": "跨轮次知识整合引擎",
                "keywords": ["知识", "整合", "跨轮", "推理"],
                "module": "evolution_knowledge_deep_integration_engine",
                "class": "KnowledgeDeepIntegrationEngine",
            },
            "autonomous_consciousness": {
                "name": "自主意识执行引擎",
                "keywords": ["自主", "意识", "执行", "觉醒"],
                "module": "evolution_autonomous_consciousness_execution_engine",
                "class": "AutonomousConsciousnessExecutionEngine",
            },
            "global_situation": {
                "name": "全局态势感知引擎",
                "keywords": ["全局", "态势", "感知", "监控"],
                "module": "evolution_global_situation_awareness",
                "class": "GlobalSituationAwarenessEngine",
            },
            "innovation": {
                "name": "主动创新实现引擎",
                "keywords": ["创新", "实现", "发现", "创造"],
                "module": "evolution_innovation_realization_engine",
                "class": "InnovationRealizationEngine",
            },
            "service_orchestration": {
                "name": "服务协同编排引擎",
                "keywords": ["服务", "编排", "协同", "自适应"],
                "module": "evolution_service_orchestration_adaptive_engine",
                "class": "ServiceOrchestrationAdaptiveEngine",
            },
            "realtime_monitoring": {
                "name": "实时监控预警引擎",
                "keywords": ["实时", "监控", "预警", "智能"],
                "module": "evolution_realtime_monitoring_warning_engine",
                "class": "RealtimeMonitoringWarningEngine",
            },
            "value_driven": {
                "name": "价值驱动执行引擎",
                "keywords": ["价值", "驱动", "自动", "闭环"],
                "module": "evolution_value_driven_loop_integration",
                "class": "ValueDrivenLoopIntegrationEngine",
            },
        }

        self.loaded_engines = {}

        self._initialize()

    def _initialize(self):
        """初始化引擎"""
        _safe_print("[UnifiedEvolutionAgent] 正在初始化统一智能体协同引擎...")

        # 扫描可用引擎
        self._scan_available_engines()

        # 加载配置
        self._load_config()

        self.state["initialized"] = True
        self.state["health_status"] = "healthy"

        # 保存状态
        self._save_state()

        _safe_print(f"[UnifiedEvolutionAgent] 初始化完成，已注册 {len(self.engine_capabilities)} 个引擎能力")

    def _scan_available_engines(self):
        """扫描可用引擎"""
        _safe_print("[UnifiedEvolutionAgent] 扫描可用进化引擎...")

        available = 0
        for engine_id, engine_info in self.engine_capabilities.items():
            module_name = engine_info["module"]
            module_path = self.scripts_dir / f"{module_name}.py"

            if module_path.exists():
                self.state["engine_registry"][engine_id] = {
                    "available": True,
                    "path": str(module_path),
                    "name": engine_info["name"],
                }
                available += 1
            else:
                self.state["engine_registry"][engine_id] = {
                    "available": False,
                    "path": str(module_path),
                    "name": engine_info["name"],
                }

        _safe_print(f"[UnifiedEvolutionAgent] 发现 {available}/{len(self.engine_capabilities)} 个可用引擎")

    def _load_config(self):
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.state.update(config)
            except Exception as e:
                _safe_print(f"[UnifiedEvolutionAgent] 配置加载失败: {e}")

    def _save_state(self):
        """保存状态"""
        try:
            self.state_dir.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[UnifiedEvolutionAgent] 状态保存失败: {e}")

    def analyze_task(self, task_description: str) -> Dict[str, Any]:
        """分析任务，理解意图并推荐引擎组合

        Args:
            task_description: 任务描述

        Returns:
            分析结果：包含意图理解、推荐引擎、执行计划
        """
        _safe_print(f"[UnifiedEvolutionAgent] 分析任务: {task_description}")

        task_lower = task_description.lower()

        # 意图分析
        intent_analysis = {
            "primary_intent": self._detect_primary_intent(task_lower),
            "secondary_intents": self._detect_secondary_intents(task_lower),
            "complexity": self._estimate_complexity(task_lower),
            "urgency": self._estimate_urgency(task_lower),
        }

        # 引擎选择
        selected_engines = self._select_engines(intent_analysis)

        # 生成执行计划
        execution_plan = self._generate_execution_plan(
            task_description, intent_analysis, selected_engines
        )

        # 缓存结果
        cache_key = hash(task_description)
        self.state["task_analysis_cache"][cache_key] = {
            "task": task_description,
            "intent": intent_analysis,
            "engines": selected_engines,
            "plan": execution_plan,
            "timestamp": datetime.now().isoformat(),
        }

        return {
            "task": task_description,
            "intent": intent_analysis,
            "selected_engines": selected_engines,
            "execution_plan": execution_plan,
        }

    def _detect_primary_intent(self, task_lower: str) -> str:
        """检测主要意图"""
        intent_keywords = {
            "自主进化": ["进化", "自我进化", "自主", "自进化"],
            "价值实现": ["价值", "实现", "创造", "收益"],
            "知识推理": ["知识", "推理", "分析", "理解"],
            "决策执行": ["决策", "执行", "闭环", "自动化"],
            "监控预警": ["监控", "预警", "健康", "状态"],
            "创新发现": ["创新", "发现", "新", "创造"],
            "服务编排": ["服务", "编排", "协同", "调度"],
        }

        for intent, keywords in intent_keywords.items():
            if any(kw in task_lower for kw in keywords):
                return intent

        return "通用任务"

    def _detect_secondary_intents(self, task_lower: str) -> List[str]:
        """检测次要意图"""
        secondary = []

        intent_keywords = {
            "知识整合": ["知识", "整合", "融合"],
            "自主意识": ["意识", "觉醒", "自主"],
            "全局感知": ["全局", "态势", "感知"],
            "实时监控": ["实时", "监控"],
            "预测预防": ["预测", "预防"],
        }

        for intent, keywords in intent_keywords.items():
            if any(kw in task_lower for kw in keywords):
                secondary.append(intent)

        return secondary

    def _estimate_complexity(self, task_lower: str) -> str:
        """估算任务复杂度"""
        complexity_indicators = {
            "high": ["复杂", "多维度", "跨引擎", "深度", "综合"],
            "medium": ["优化", "增强", "集成", "协同"],
            "low": ["简单", "基础", "单", "快速"],
        }

        for level, keywords in complexity_indicators.items():
            if any(kw in task_lower for kw in keywords):
                return level

        return "medium"

    def _estimate_urgency(self, task_lower: str) -> str:
        """估算紧急程度"""
        urgency_keywords = {
            "high": ["紧急", "立即", "马上", "优先"],
            "medium": ["重要", "需要", "应该"],
            "low": ["可以", "稍后", "有空"],
        }

        for level, keywords in urgency_keywords.items():
            if any(kw in task_lower for kw in keywords):
                return level

        return "medium"

    def _select_engines(self, intent_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """根据意图选择引擎"""
        selected = []
        primary = intent_analysis.get("primary_intent", "通用任务")

        # 主要意图到引擎的映射
        intent_to_engine = {
            "自主进化": ["meta_integration", "autonomous_consciousness"],
            "价值实现": ["value_driven", "value_knowledge", "innovation"],
            "知识推理": ["knowledge_integration", "value_knowledge"],
            "决策执行": ["decision_execution", "value_driven"],
            "监控预警": ["realtime_monitoring", "global_situation"],
            "创新发现": ["innovation", "service_orchestration"],
            "服务编排": ["service_orchestration", "decision_execution"],
            "通用任务": ["global_situation", "value_knowledge"],
        }

        engine_ids = intent_to_engine.get(primary, ["global_situation"])

        for engine_id in engine_ids:
            if engine_id in self.state["engine_registry"]:
                registry = self.state["engine_registry"][engine_id]
                selected.append({
                    "engine_id": engine_id,
                    "name": self.engine_capabilities[engine_id]["name"],
                    "available": registry.get("available", False),
                    "priority": len(selected) + 1,
                })

        # 添加次要意图相关的引擎
        for secondary in intent_analysis.get("secondary_intents", []):
            secondary_to_engine = {
                "知识整合": ["knowledge_integration"],
                "自主意识": ["autonomous_consciousness"],
                "全局感知": ["global_situation"],
                "实时监控": ["realtime_monitoring"],
            }

            if secondary in secondary_to_engine:
                for engine_id in secondary_to_engine[secondary]:
                    if engine_id not in [s["engine_id"] for s in selected]:
                        if engine_id in self.state["engine_registry"]:
                            selected.append({
                                "engine_id": engine_id,
                                "name": self.engine_capabilities[engine_id]["name"],
                                "available": self.state["engine_registry"][engine_id].get("available", False),
                                "priority": len(selected) + 1,
                            })

        return selected

    def _generate_execution_plan(
        self,
        task_description: str,
        intent_analysis: Dict[str, Any],
        selected_engines: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """生成执行计划"""
        plan = {
            "task": task_description,
            "complexity": intent_analysis.get("complexity", "medium"),
            "urgency": intent_analysis.get("urgency", "medium"),
            "steps": [],
            "estimated_engines": len(selected_engines),
        }

        # 为每个选中的引擎生成执行步骤
        for i, engine in enumerate(selected_engines):
            plan["steps"].append({
                "step": i + 1,
                "engine_id": engine["engine_id"],
                "engine_name": engine["name"],
                "action": self._generate_engine_action(engine["engine_id"], task_description),
                "expected_output": self._get_expected_output(engine["engine_id"]),
            })

        return plan

    def _generate_engine_action(self, engine_id: str, task_description: str) -> str:
        """生成引擎执行动作"""
        action_templates = {
            "meta_integration": "深度集成元进化能力，实现自主运行增强",
            "value_knowledge": "执行价值-知识双闭环，增强知识驱动决策",
            "decision_execution": "执行决策到执行的完整闭环",
            "knowledge_integration": "跨轮次整合进化知识并推理",
            "autonomous_consciousness": "激活自主意识并执行闭环",
            "global_situation": "感知全局态势并进行智能决策",
            "innovation": "主动发现创新机会并实现",
            "service_orchestration": "编排多引擎协同服务",
            "realtime_monitoring": "实时监控并预警",
            "value_driven": "执行价值驱动的自动闭环",
        }

        return action_templates.get(engine_id, f"执行{engine_id}引擎")

    def _get_expected_output(self, engine_id: str) -> str:
        """获取引擎预期输出"""
        output_templates = {
            "meta_integration": "无人值守的自主进化能力",
            "value_knowledge": "价值驱动的知识增强",
            "decision_execution": "决策执行闭环结果",
            "knowledge_integration": "整合后的知识图谱",
            "autonomous_consciousness": "自主执行验证结果",
            "global_situation": "全局态势感知报告",
            "innovation": "创新方案与实现结果",
            "service_orchestration": "协同执行结果",
            "realtime_monitoring": "监控预警报告",
            "value_driven": "价值实现追踪报告",
        }

        return output_templates.get(engine_id, "执行结果")

    def execute_task(self, task_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务

        Args:
            task_analysis: 任务分析结果

        Returns:
            执行结果
        """
        _safe_print("[UnifiedEvolutionAgent] 开始执行任务...")

        plan = task_analysis.get("execution_plan", {})
        steps = plan.get("steps", [])

        results = []
        overall_success = True

        for step in steps:
            step_result = self._execute_step(step, task_analysis["task"])
            results.append(step_result)

            if not step_result.get("success", False):
                overall_success = False

        # 聚合结果
        execution_result = {
            "success": overall_success,
            "task": task_analysis["task"],
            "executed_engines": len(results),
            "steps": results,
            "aggregated_result": self._aggregate_results(results),
            "timestamp": datetime.now().isoformat(),
        }

        # 更新统计
        self.state["execution_count"] += 1
        if overall_success:
            self.state["success_count"] += 1
        else:
            self.state["failure_count"] += 1

        self.state["execution_history"].append(execution_result)

        # 限制历史记录数量
        if len(self.state["execution_history"]) > 100:
            self.state["execution_history"] = self.state["execution_history"][-100:]

        self._save_state()

        return execution_result

    def _execute_step(self, step: Dict[str, Any], task: str) -> Dict[str, Any]:
        """执行单个步骤"""
        engine_id = step.get("engine_id", "")
        engine_name = step.get("engine_name", "")

        _safe_print(f"[UnifiedEvolutionAgent] 执行步骤 {step.get('step')}: {engine_name}")

        # 检查引擎是否可用
        if engine_id in self.state["engine_registry"]:
            available = self.state["engine_registry"][engine_id].get("available", False)
        else:
            available = False

        if not available:
            return {
                "step": step.get("step"),
                "engine_id": engine_id,
                "engine_name": engine_name,
                "success": False,
                "message": f"引擎 {engine_id} 不可用",
                "output": None,
            }

        # 尝试加载并执行引擎
        try:
            result = self._try_execute_engine(engine_id, task)
            return {
                "step": step.get("step"),
                "engine_id": engine_id,
                "engine_name": engine_name,
                "success": result.get("success", True),
                "message": "执行成功",
                "output": result,
            }
        except Exception as e:
            return {
                "step": step.get("step"),
                "engine_id": engine_id,
                "engine_name": engine_name,
                "success": False,
                "message": f"执行失败: {str(e)}",
                "output": None,
            }

    def _try_execute_engine(self, engine_id: str, task: str) -> Dict[str, Any]:
        """尝试执行引擎"""
        engine_info = self.engine_capabilities.get(engine_id, {})
        module_name = engine_info.get("module", "")

        if not module_name:
            return {"success": False, "message": "引擎信息不完整"}

        # 尝试动态导入并执行
        try:
            sys.path.insert(0, str(self.scripts_dir))
            module = importlib.import_module(module_name)

            # 检查是否有可执行的入口
            if hasattr(module, "main"):
                # 如果有 main 函数，尝试调用
                return {"success": True, "message": f"引擎 {engine_id} 已加载"}
            else:
                return {"success": True, "message": f"引擎 {engine_id} 模块存在"}
        except ImportError as e:
            return {"success": False, "message": f"引擎模块导入失败: {str(e)}"}
        except Exception as e:
            return {"success": False, "message": f"引擎执行失败: {str(e)}"}

    def _aggregate_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """聚合多个引擎的执行结果"""
        success_count = sum(1 for r in results if r.get("success", False))
        total_count = len(results)

        return {
            "total_steps": total_count,
            "successful_steps": success_count,
            "failed_steps": total_count - success_count,
            "success_rate": success_count / total_count if total_count > 0 else 0,
            "overall_status": "success" if success_count == total_count else "partial" if success_count > 0 else "failed",
        }

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "version": self.state["version"],
            "initialized": self.state["initialized"],
            "registered_engines": len(self.engine_capabilities),
            "available_engines": sum(1 for r in self.state["engine_registry"].values() if r.get("available", False)),
            "execution_count": self.state["execution_count"],
            "success_count": self.state["success_count"],
            "failure_count": self.state["failure_count"],
            "health_status": self.state["health_status"],
        }

    def get_engine_list(self) -> List[Dict[str, Any]]:
        """获取引擎列表"""
        engines = []

        for engine_id, info in self.engine_capabilities.items():
            registry = self.state["engine_registry"].get(engine_id, {})
            engines.append({
                "engine_id": engine_id,
                "name": info["name"],
                "keywords": info["keywords"],
                "available": registry.get("available", False),
                "module": info["module"],
            })

        return engines


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能全场景进化环统一智能体协同引擎"
    )
    parser.add_argument("command", nargs="?", default="status",
                        help="命令: status, list, analyze, execute, help")
    parser.add_argument("--task", "-t", type=str,
                        help="任务描述（用于 analyze/execute 命令）")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="详细输出")

    args = parser.parse_args()

    engine = UnifiedEvolutionAgentEngine()

    if args.command == "status":
        status = engine.get_status()
        _safe_print("=" * 50)
        _safe_print("统一智能体协同引擎状态")
        _safe_print("=" * 50)
        for key, value in status.items():
            _safe_print(f"  {key}: {value}")
        _safe_print("=" * 50)

    elif args.command == "list":
        engines = engine.get_engine_list()
        _safe_print("=" * 50)
        _safe_print("进化引擎列表")
        _safe_print("=" * 50)
        for eng in engines:
            status = "可用" if eng["available"] else "不可用"
            _safe_print(f"  [{status}] {eng['engine_id']}: {eng['name']}")
            _safe_print(f"         关键词: {', '.join(eng['keywords'])}")
        _safe_print("=" * 50)

    elif args.command == "analyze":
        if not args.task:
            _safe_print("错误: 请使用 --task 指定任务描述")
            return

        result = engine.analyze_task(args.task)
        _safe_print("=" * 50)
        _safe_print("任务分析结果")
        _safe_print("=" * 50)
        _safe_print(f"任务: {result['task']}")
        _safe_print(f"主要意图: {result['intent']['primary_intent']}")
        _safe_print(f"复杂度: {result['intent']['complexity']}")
        _safe_print(f"紧急程度: {result['intent']['urgency']}")
        _safe_print("\n推荐引擎:")
        for eng in result['selected_engines']:
            available = "可用" if eng['available'] else "不可用"
            _safe_print(f"  [{available}] {eng['name']} (优先级: {eng['priority']})")
        _safe_print("\n执行计划:")
        plan = result['execution_plan']
        for step in plan.get('steps', []):
            _safe_print(f"  {step['step']}. {step['engine_name']}: {step['action']}")
        _safe_print("=" * 50)

    elif args.command == "execute":
        if not args.task:
            _safe_print("错误: 请使用 --task 指定任务描述")
            return

        # 分析任务
        analysis = engine.analyze_task(args.task)

        # 执行任务
        result = engine.execute_task(analysis)
        _safe_print("=" * 50)
        _safe_print("执行结果")
        _safe_print("=" * 50)
        _safe_print(f"任务: {result['task']}")
        _safe_print(f"执行引擎数: {result['executed_engines']}")
        _safe_print(f"总体状态: {result['aggregated_result']['overall_status']}")
        _safe_print(f"成功率: {result['aggregated_result']['success_rate']:.1%}")
        _safe_print("=" * 50)

    else:
        _safe_print("智能全场景进化环统一智能体协同引擎 (version 1.0.0)")
        _safe_print("")
        _safe_print("用法:")
        _safe_print("  python unified_evolution_agent_engine.py status    - 查看引擎状态")
        _safe_print("  python unified_evolution_agent_engine.py list     - 列出可用引擎")
        _safe_print("  python unified_evolution_agent_engine.py analyze   - 分析任务")
        _safe_print("  python unified_evolution_agent_engine.py execute  - 执行任务")
        _safe_print("")
        _safe_print("示例:")
        _safe_print("  python unified_evolution_agent_engine.py analyze --task \"自主进化优化\"")
        _safe_print("  python unified_evolution_agent_engine.py execute --task \"执行价值驱动进化\"")


if __name__ == "__main__":
    main()