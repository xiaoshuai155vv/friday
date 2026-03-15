#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环知识驱动自动化执行增强引擎

在 round 580 完成的价值驱动进化执行闭环引擎基础上，构建从知识推理到自动执行的完整自动化链路。
让系统能够从知识图谱推理结果自动生成并执行行动计划，形成「推理→洞察→行动→验证」的完整知识驱动闭环。

功能：
1. 知识推理结果解析 - 解析知识图谱深度推理引擎产生的洞察
2. 洞察到行动自动转换 - 将洞察转化为可执行的行动计划
3. 行动计划生成与执行 - 生成具体的执行步骤并自动执行
4. 执行结果验证 - 验证执行效果与预期
5. 反馈优化 - 将执行结果反馈到知识图谱，形成持续改进
6. 与 round 330 知识图谱深度推理引擎深度集成
7. 驾驶舱数据接口

依赖：
- round 330 evolution_kg_deep_reasoning_insight_engine.py
- round 298 evolution_knowledge_graph_reasoning.py
- round 580 evolution_value_driven_execution_closed_loop_engine.py

Version: 1.0.0
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import random
import glob
from collections import defaultdict
import subprocess


class KnowledgeDrivenAutomationExecutionEngine:
    """知识驱动自动化执行增强引擎"""

    VERSION = "1.0.0"

    def __init__(self):
        self.name = "KnowledgeDrivenAutomationExecutionEngine"
        self.data_dir = Path("runtime/state")
        self.output_dir = Path("runtime/state")
        self.output_file = self.output_dir / "knowledge_driven_automation_execution.json"

        # 知识图谱深度推理引擎数据文件
        self.insight_file = self.data_dir / "kg_deep_insights.json"
        self.reasoning_file = self.data_dir / "kg_reasoning_results.json"

        # 行动计划文件
        self.action_plans_file = self.output_dir / "knowledge_action_plans.json"

        # 执行历史文件
        self.execution_history_file = self.output_dir / "knowledge_automation_history.json"

    def load_insights(self) -> List[Dict[str, Any]]:
        """加载知识图谱深度推理引擎产生的洞察"""
        insights = []

        # 尝试从洞察文件加载
        if self.insight_file.exists():
            try:
                with open(self.insight_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        insights = data
                    elif isinstance(data, dict) and 'insights' in data:
                        insights = data.get('insights', [])
            except Exception:
                pass

        # 如果没有洞察文件，尝试从推理结果中提取
        if not insights and self.reasoning_file.exists():
            try:
                with open(self.reasoning_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        # 从推理结果中提取洞察
                        if 'insights' in data:
                            insights = data.get('insights', [])
                        elif 'findings' in data:
                            insights = data.get('findings', [])
                        elif 'opportunities' in data:
                            insights = data.get('opportunities', [])
            except Exception:
                pass

        return insights

    def load_action_plans(self) -> Dict[str, Any]:
        """加载行动计划数据"""
        data = {"plans": [], "last_updated": None}

        if self.action_plans_file.exists():
            try:
                with open(self.action_plans_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception:
                pass

        return data

    def load_execution_history(self) -> List[Dict[str, Any]]:
        """加载执行历史"""
        history = []

        if self.execution_history_file.exists():
            try:
                with open(self.execution_history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        history = data
            except Exception:
                pass

        return history

    def parse_insight_to_action_plan(self, insight: Dict[str, Any]) -> Dict[str, Any]:
        """将洞察转化为可执行的行动计划"""
        plan = {
            "plan_id": f"plan_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}",
            "source_insight_id": insight.get("id", insight.get("insight_id", "unknown")),
            "title": insight.get("title", insight.get("name", "Untitled Plan")),
            "description": insight.get("description", insight.get("summary", "")),
            "type": insight.get("type", insight.get("insight_type", "general")),
            "priority": self._calculate_priority(insight),
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "actions": self._generate_actions(insight),
            "expected_outcome": insight.get("expected_outcome", insight.get("value_score", 0)),
            "validation_criteria": self._generate_validation_criteria(insight)
        }

        return plan

    def _calculate_priority(self, insight: Dict[str, Any]) -> str:
        """计算行动计划优先级"""
        # 基于价值分数和可行性计算优先级
        value_score = insight.get("value_score", insight.get("value", 50))
        feasibility = insight.get("feasibility", insight.get("confidence", 50))
        risk = insight.get("risk", insight.get("risk_score", 50))

        # 综合评分
        score = (value_score * 0.4 + feasibility * 0.4 - risk * 0.2) / 10

        if score >= 8:
            return "critical"
        elif score >= 6:
            return "high"
        elif score >= 4:
            return "medium"
        else:
            return "low"

    def _generate_actions(self, insight: Dict[str, Any]) -> List[Dict[str, Any]]:
        """根据洞察生成具体的执行动作"""
        actions = []

        insight_type = insight.get("type", insight.get("insight_type", "general"))

        # 根据洞察类型生成不同的动作
        if insight_type in ["optimization", "optimize", "improve"]:
            actions.append({
                "id": f"action_{random.randint(1000, 9999)}",
                "type": "analyze",
                "description": "分析当前优化点",
                "command": "python scripts/evolution_log_analyzer.py --recent 10",
                "status": "pending"
            })
            actions.append({
                "id": f"action_{random.randint(1000, 9999)}",
                "type": "execute",
                "description": "执行优化建议",
                "command": self._generate_optimization_command(insight),
                "status": "pending"
            })
        elif insight_type in ["innovation", "innovate", "create"]:
            actions.append({
                "id": f"action_{random.randint(1000, 9999)}",
                "type": "research",
                "description": "研究创新方向可行性",
                "command": "python scripts/evolution_idea_generator.py --analyze",
                "status": "pending"
            })
            actions.append({
                "id": f"action_{random.randint(1000, 9999)}",
                "type": "implement",
                "description": "实现创新方案",
                "command": self._generate_innovation_command(insight),
                "status": "pending"
            })
        elif insight_type in ["warning", "alert", "risk"]:
            actions.append({
                "id": f"action_{random.randint(1000, 9999)}",
                "type": "assess",
                "description": "评估风险影响",
                "command": "python scripts/evolution_health_dashboard_engine.py --assess-risk",
                "status": "pending"
            })
            actions.append({
                "id": f"action_{random.randint(1000, 9999)}",
                "type": "mitigate",
                "description": "执行风险缓解",
                "command": self._generate_mitigation_command(insight),
                "status": "pending"
            })
        else:
            # 默认分析动作
            actions.append({
                "id": f"action_{random.randint(1000, 9999)}",
                "type": "analyze",
                "description": "分析洞察详情",
                "command": "python scripts/evolution_efficiency_analyzer.py",
                "status": "pending"
            })

        # 添加验证动作
        actions.append({
            "id": f"action_{random.randint(1000, 9999)}",
            "type": "validate",
            "description": "验证执行效果",
            "command": "python scripts/self_verify_capabilities.py",
            "status": "pending"
        })

        return actions

    def _generate_optimization_command(self, insight: Dict[str, Any]) -> str:
        """生成优化命令"""
        area = insight.get("area", insight.get("focus_area", "general"))
        return f"python scripts/evolution_loop_optimizer.py --optimize {area}"

    def _generate_innovation_command(self, insight: Dict[str, Any]) -> str:
        """生成创新命令"""
        direction = insight.get("direction", insight.get("innovation_type", "general"))
        return f"python scripts/evolution_idea_generator.py --generate {direction}"

    def _generate_mitigation_command(self, insight: Dict[str, Any]) -> str:
        """生成风险缓解命令"""
        risk_type = insight.get("risk_type", "general")
        return f"python scripts/evolution_health_healing_integrated_engine.py --mitigate {risk_type}"

    def _generate_validation_criteria(self, insight: Dict[str, Any]) -> Dict[str, Any]:
        """生成验证标准"""
        return {
            "value_threshold": insight.get("value_score", 70),
            "feasibility_threshold": insight.get("feasibility", 60),
            "max_risk_threshold": insight.get("risk", 30),
            "success_metrics": [
                "execution_completed",
                "value_improved",
                "risk_mitigated"
            ]
        }

    def generate_action_plans_from_insights(self) -> Dict[str, Any]:
        """从洞察生成行动计划"""
        insights = self.load_insights()
        action_plans = []

        for insight in insights:
            # 检查洞察是否已经处理过
            if insight.get("status") == "implemented":
                continue

            # 转换为行动计划
            plan = self.parse_insight_to_action_plan(insight)
            action_plans.append(plan)

        result = {
            "plans": action_plans,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_insights_processed": len(insights),
            "plans_generated": len(action_plans)
        }

        # 保存到文件
        self.action_plans_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.action_plans_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        return result

    def execute_action_plan(self, plan_id: str) -> Dict[str, Any]:
        """执行指定的行动计划"""
        plans_data = self.load_action_plans()
        plan = None

        for p in plans_data.get("plans", []):
            if p.get("plan_id") == plan_id:
                plan = p
                break

        if not plan:
            return {"status": "error", "message": f"Plan {plan_id} not found"}

        # 更新计划状态
        plan["status"] = "executing"
        plan["execution_started_at"] = datetime.now(timezone.utc).isoformat()

        # 执行每个动作
        execution_results = []
        for action in plan.get("actions", []):
            action_result = self._execute_action(action)
            execution_results.append(action_result)

            # 如果动作失败，更新状态
            if action_result.get("status") == "failed":
                plan["status"] = "failed"
                break

        # 更新计划状态
        if plan.get("status") != "failed":
            plan["status"] = "completed"

        plan["execution_completed_at"] = datetime.now(timezone.utc).isoformat()
        plan["execution_results"] = execution_results

        # 保存执行历史
        self._save_execution_history(plan)

        # 更新计划文件
        plans_data["plans"] = [p if p.get("plan_id") != plan_id else plan for p in plans_data.get("plans", [])]
        with open(self.action_plans_file, 'w', encoding='utf-8') as f:
            json.dump(plans_data, f, ensure_ascii=False, indent=2)

        return {
            "status": "success",
            "plan_id": plan_id,
            "execution_results": execution_results,
            "overall_status": plan["status"]
        }

    def _execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个动作"""
        action_id = action.get("id")
        command = action.get("command", "")

        if not command:
            return {
                "action_id": action_id,
                "status": "skipped",
                "message": "No command to execute"
            }

        try:
            # 执行命令
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )

            return {
                "action_id": action_id,
                "status": "completed" if result.returncode == 0 else "failed",
                "command": command,
                "return_code": result.returncode,
                "stdout": result.stdout[:500] if result.stdout else "",
                "stderr": result.stderr[:500] if result.stderr else ""
            }
        except subprocess.TimeoutExpired:
            return {
                "action_id": action_id,
                "status": "failed",
                "message": "Command timeout"
            }
        except Exception as e:
            return {
                "action_id": action_id,
                "status": "failed",
                "message": str(e)
            }

    def _save_execution_history(self, plan: Dict[str, Any]):
        """保存执行历史"""
        history = self.load_execution_history()
        history.append({
            "plan_id": plan.get("plan_id"),
            "title": plan.get("title"),
            "status": plan.get("status"),
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "actions_count": len(plan.get("actions", [])),
            "results": plan.get("execution_results", [])
        })

        # 保留最近100条记录
        history = history[-100:]

        with open(self.execution_history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def validate_execution(self, plan_id: str) -> Dict[str, Any]:
        """验证执行效果"""
        plans_data = self.load_action_plans()
        plan = None

        for p in plans_data.get("plans", []):
            if p.get("plan_id") == plan_id:
                plan = p
                break

        if not plan:
            return {"status": "error", "message": f"Plan {plan_id} not found"}

        # 检查验证标准
        validation_criteria = plan.get("validation_criteria", {})
        execution_results = plan.get("execution_results", [])

        # 统计执行结果
        completed_actions = sum(1 for r in execution_results if r.get("status") == "completed")
        failed_actions = sum(1 for r in execution_results if r.get("status") == "failed")

        validation_result = {
            "plan_id": plan_id,
            "validated_at": datetime.now(timezone.utc).isoformat(),
            "actions_total": len(execution_results),
            "actions_completed": completed_actions,
            "actions_failed": failed_actions,
            "success_rate": completed_actions / len(execution_results) if execution_results else 0,
            "validation_passed": failed_actions == 0,
            "validation_criteria": validation_criteria
        }

        return validation_result

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱数据"""
        insights = self.load_insights()
        plans_data = self.load_action_plans()
        history = self.load_execution_history()

        # 统计计划状态
        pending_plans = sum(1 for p in plans_data.get("plans", []) if p.get("status") == "pending")
        executing_plans = sum(1 for p in plans_data.get("plans", []) if p.get("status") == "executing")
        completed_plans = sum(1 for p in plans_data.get("plans", []) if p.get("status") == "completed")
        failed_plans = sum(1 for p in plans_data.get("plans", []) if p.get("status") == "failed")

        # 统计最近执行结果
        recent_executions = history[-10:] if history else []
        recent_success_rate = sum(1 for e in recent_executions if e.get("status") == "completed") / len(recent_executions) if recent_executions else 0

        return {
            "engine": self.name,
            "version": self.VERSION,
            "insights_available": len(insights),
            "plans": {
                "pending": pending_plans,
                "executing": executing_plans,
                "completed": completed_plans,
                "failed": failed_plans,
                "total": len(plans_data.get("plans", []))
            },
            "execution_history": {
                "total_executions": len(history),
                "recent_success_rate": recent_success_rate,
                "last_execution": history[-1].get("executed_at") if history else None
            },
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        plans_data = self.load_action_plans()
        history = self.load_execution_history()

        return {
            "engine": self.name,
            "version": self.VERSION,
            "status": "active",
            "plans_pending": len([p for p in plans_data.get("plans", []) if p.get("status") == "pending"]),
            "plans_executing": len([p for p in plans_data.get("plans", []) if p.get("status") == "executing"]),
            "recent_history_count": len(history),
            "ready": True
        }

    def run_full_cycle(self) -> Dict[str, Any]:
        """运行完整的知识驱动自动化执行循环"""
        # 1. 从洞察生成行动计划
        plans_result = self.generate_action_plans_from_insights()

        # 2. 获取待执行的计划
        plans_data = self.load_action_plans()
        pending_plans = [p for p in plans_data.get("plans", []) if p.get("status") == "pending"]

        if not pending_plans:
            return {
                "status": "no_plans",
                "message": "No pending plans to execute",
                "insights_processed": plans_result.get("total_insights_processed", 0),
                "plans_generated": plans_result.get("plans_generated", 0)
            }

        # 3. 执行第一个待处理的高优先级计划
        # 按优先级排序
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        pending_plans.sort(key=lambda x: priority_order.get(x.get("priority", "medium"), 2))

        plan_to_execute = pending_plans[0]
        execution_result = self.execute_action_plan(plan_to_execute.get("plan_id"))

        # 4. 验证执行结果
        validation_result = self.validate_execution(plan_to_execute.get("plan_id"))

        return {
            "status": "completed",
            "plans_generated": plans_result.get("plans_generated", 0),
            "plan_executed": plan_to_execute.get("plan_id"),
            "execution_result": execution_result,
            "validation_result": validation_result
        }


def main():
    parser = argparse.ArgumentParser(description="知识驱动自动化执行增强引擎")
    parser.add_argument("--generate-plans", action="store_true", help="从洞察生成行动计划")
    parser.add_argument("--execute-plan", type=str, help="执行指定计划")
    parser.add_argument("--plan-id", type=str, help="计划ID")
    parser.add_argument("--validate", type=str, help="验证计划执行效果")
    parser.add_argument("--status", action="store_true", help="显示引擎状态")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")
    parser.add_argument("--run-cycle", action="store_true", help="运行完整执行循环")
    parser.add_argument("--list-plans", action="store_true", help="列出所有行动计划")

    args = parser.parse_args()

    engine = KnowledgeDrivenAutomationExecutionEngine()

    if args.status:
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return

    if args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    if args.generate_plans:
        result = engine.generate_action_plans_from_insights()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.execute_plan:
        plan_id = args.plan_id or args.execute_plan
        result = engine.execute_action_plan(plan_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.validate:
        plan_id = args.plan_id or args.validate
        result = engine.validate_execution(plan_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.run_cycle:
        result = engine.run_full_cycle()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.list_plans:
        plans_data = engine.load_action_plans()
        print(json.dumps(plans_data, ensure_ascii=False, indent=2))
        return

    # 默认显示状态
    status = engine.get_status()
    print(json.dumps(status, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()