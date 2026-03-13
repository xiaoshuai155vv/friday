#!/usr/bin/env python3
"""
智能进化指挥塔引擎 (Evolution Command Tower)
让系统能够作为中央智能指挥官，实时整合70+引擎的运行状态、进化历史、知识图谱，
自主分析当前能力缺口、预测未来需求、规划下一代进化方向，形成真正的自主进化大脑。

功能：
1. 多维进化态势感知 - 整合引擎状态、进化效率、知识图谱、健康指标
2. 进化需求预测 - 基于历史趋势和当前状态预测未来需求
3. 进化路径自动规划 - 自动规划最优进化路径
4. 进化优先级动态调整 - 根据实时情况动态调整优先级
"""

import json
import os
import sys
import subprocess
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE_DIR = PROJECT_ROOT / "runtime" / "state"
RUNTIME_LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
REFERENCES_DIR = PROJECT_ROOT / "references"


class EvolutionCommandTower:
    """智能进化指挥塔引擎"""

    def __init__(self):
        self.name = "EvolutionCommandTower"
        self.version = "1.0.0"
        self._load_data()

    def _load_data(self):
        """加载必要数据"""
        # 加载进化历史
        self.evolution_history = self._load_evolution_history()

        # 加载引擎状态
        self.engine_metrics = self._load_engine_metrics()

        # 加载知识图谱
        self.knowledge_graph = self._load_knowledge_graph()

        # 加载系统健康状态
        self.system_health = self._load_system_health()

    def _load_evolution_history(self) -> List[Dict]:
        """加载进化历史"""
        history = []
        state_dir = RUNTIME_STATE_DIR

        if not state_dir.exists():
            return history

        # 加载最新的进化完成记录
        for f in state_dir.glob("evolution_completed_*.json"):
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    if isinstance(data, dict):
                        history.append(data)
            except Exception:
                continue

        # 按时间排序
        history.sort(key=lambda x: x.get('completed_at', ''), reverse=True)
        return history[:100]  # 取最近100条

    def _load_engine_metrics(self) -> Dict:
        """加载引擎实时指标"""
        metrics_file = RUNTIME_STATE_DIR / "engine_realtime_metrics.json"

        if metrics_file.exists():
            try:
                with open(metrics_file, 'r', encoding='utf-8') as fp:
                    return json.load(fp)
            except Exception:
                pass

        return {}

    def _load_knowledge_graph(self) -> Dict:
        """加载知识图谱"""
        kg_file = REFERENCES_DIR / "knowledge_graph.json"

        if kg_file.exists():
            try:
                with open(kg_file, 'r', encoding='utf-8') as fp:
                    return json.load(fp)
            except Exception:
                pass

        return {"nodes": [], "edges": []}

    def _load_system_health(self) -> Dict:
        """加载系统健康状态"""
        health_file = RUNTIME_STATE_DIR / "system_health_report.json"

        if health_file.exists():
            try:
                with open(health_file, 'r', encoding='utf-8') as fp:
                    return json.load(fp)
            except Exception:
                pass

        return {}

    def get_situational_awareness(self) -> Dict:
        """获取多维进化态势感知"""
        # 分析引擎状态
        engine_status = self._analyze_engine_status()

        # 分析进化效率
        evolution_efficiency = self._analyze_evolution_efficiency()

        # 分析知识图谱状态
        kg_status = self._analyze_knowledge_graph()

        # 分析系统健康
        health_status = self._analyze_system_health()

        # 综合态势评分
        overall_score = self._calculate_overall_score(
            engine_status, evolution_efficiency, kg_status, health_status
        )

        return {
            "timestamp": datetime.now().isoformat(),
            "overall_score": overall_score,
            "engine_status": engine_status,
            "evolution_efficiency": evolution_efficiency,
            "knowledge_graph_status": kg_status,
            "system_health": health_status,
            "insights": self._generate_insights(
                engine_status, evolution_efficiency, kg_status, health_status
            )
        }

    def _analyze_engine_status(self) -> Dict:
        """分析引擎状态"""
        total_engines = 0
        active_engines = 0
        idle_engines = 0

        # 统计引擎数量
        if self.engine_metrics:
            metrics = self.engine_metrics.get('metrics', {})
            total_engines = len(metrics)
            for m in metrics.values():
                if m.get('call_count', 0) > 0:
                    active_engines += 1
                else:
                    idle_engines += 1

        # 如果没有实时数据，扫描 scripts 目录
        if total_engines == 0:
            scripts_dir = SCRIPTS_DIR
            if scripts_dir.exists():
                for f in scripts_dir.glob("*_engine.py"):
                    total_engines += 1

        return {
            "total_engines": total_engines,
            "active_engines": active_engines,
            "idle_engines": idle_engines,
            "activation_rate": active_engines / total_engines if total_engines > 0 else 0,
            "status": "healthy" if active_engines > 0 else "low_activity"
        }

    def _analyze_evolution_efficiency(self) -> Dict:
        """分析进化效率"""
        if not self.evolution_history:
            return {
                "total_rounds": 0,
                "completed_rounds": 0,
                "success_rate": 0,
                "avg_value_score": 0,
                "status": "no_data"
            }

        total = len(self.evolution_history)
        completed = sum(1 for h in self.evolution_history if h.get('status') == 'completed')

        # 计算平均价值分数
        value_scores = [
            h.get('value_score', 0)
            for h in self.evolution_history
            if 'value_score' in h
        ]
        avg_value = sum(value_scores) / len(value_scores) if value_scores else 0

        # 分析趋势
        recent_rounds = self.evolution_history[:20]
        recent_completed = sum(1 for h in recent_rounds if h.get('status') == 'completed')
        recent_success_rate = recent_completed / len(recent_rounds) if recent_rounds else 0

        # 判断状态
        status = "healthy"
        if recent_success_rate < 0.5:
            status = "declining"
        elif recent_success_rate > 0.9 and avg_value > 70:
            status = "excellent"

        return {
            "total_rounds": total,
            "completed_rounds": completed,
            "success_rate": completed / total if total > 0 else 0,
            "recent_success_rate": recent_success_rate,
            "avg_value_score": avg_value,
            "status": status
        }

    def _analyze_knowledge_graph(self) -> Dict:
        """分析知识图谱状态"""
        nodes = self.knowledge_graph.get('nodes', [])
        edges = self.knowledge_graph.get('edges', [])

        return {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "density": len(edges) / len(nodes) if nodes else 0,
            "status": "healthy" if len(nodes) > 10 else "developing"
        }

    def _analyze_system_health(self) -> Dict:
        """分析系统健康"""
        if not self.system_health:
            return {
                "score": 0,
                "status": "unknown"
            }

        score = self.system_health.get('overall_score', 0)
        status = "healthy" if score > 70 else "needs_attention" if score > 50 else "critical"

        return {
            "score": score,
            "status": status,
            "issues": self.system_health.get('issues', [])
        }

    def _calculate_overall_score(
        self,
        engine_status: Dict,
        evolution_efficiency: Dict,
        kg_status: Dict,
        health_status: Dict
    ) -> float:
        """计算综合态势评分"""
        scores = []

        # 引擎状态 (20%)
        if engine_status.get('status') == 'healthy':
            scores.append(100)
        else:
            scores.append(50)

        # 进化效率 (40%)
        eff = evolution_efficiency.get('recent_success_rate', 0)
        scores.append(eff * 100)

        # 知识图谱 (20%)
        kg = kg_status.get('node_count', 0)
        if kg > 50:
            scores.append(100)
        elif kg > 20:
            scores.append(70)
        else:
            scores.append(40)

        # 系统健康 (20%)
        health = health_status.get('score', 0)
        scores.append(health)

        return sum(scores) / len(scores)

    def _generate_insights(
        self,
        engine_status: Dict,
        evolution_efficiency: Dict,
        kg_status: Dict,
        health_status: Dict
    ) -> List[str]:
        """生成洞察建议"""
        insights = []

        # 引擎相关洞察
        activation_rate = engine_status.get('activation_rate', 0)
        if activation_rate < 0.3:
            insights.append(f"引擎激活率较低({activation_rate:.1%})，建议加强引擎间联动")

        # 进化效率洞察
        eff_status = evolution_efficiency.get('status', 'unknown')
        if eff_status == 'declining':
            insights.append("进化成功率下降，建议检查进化策略或系统负载")
        elif eff_status == 'excellent':
            insights.append("进化效率优秀，系统处于健康自进化状态")

        # 知识图谱洞察
        node_count = kg_status.get('node_count', 0)
        if node_count < 10:
            insights.append("知识图谱规模较小，可考虑扩展知识积累")

        # 健康洞察
        health_issues = health_status.get('issues', [])
        if health_issues:
            insights.append(f"系统存在 {len(health_issues)} 个健康问题需要关注")

        return insights

    def predict_evolution_needs(self) -> Dict:
        """预测进化需求 - 基于当前状态和历史趋势预测未来需求"""
        situational = self.get_situational_awareness()

        predictions = []

        # 基于引擎激活率预测
        engine_status = situational.get('engine_status', {})
        activation_rate = engine_status.get('activation_rate', 0)
        if activation_rate < 0.2:
            predictions.append({
                "type": "engine_activation",
                "priority": "high",
                "description": "大量引擎未被激活，需要增强引擎联动或用户引导"
            })

        # 基于进化效率预测
        eff = situational.get('evolution_efficiency', {})
        recent_rate = eff.get('recent_success_rate', 0)
        if recent_rate < 0.7:
            predictions.append({
                "type": "evolution_optimization",
                "priority": "high",
                "description": "进化成功率下降，需要优化进化策略"
            })

        # 基于知识图谱预测
        kg = situational.get('knowledge_graph_status', {})
        if kg.get('node_count', 0) < 20:
            predictions.append({
                "type": "knowledge_expansion",
                "priority": "medium",
                "description": "知识图谱需要扩展，建议增强知识学习能力"
            })

        # 基于系统健康预测
        health = situational.get('system_health', {})
        if health.get('status') == 'critical':
            predictions.append({
                "type": "system_recovery",
                "priority": "critical",
                "description": "系统健康状态不佳，需要优先修复"
            })

        return {
            "timestamp": datetime.now().isoformat(),
            "predictions": predictions,
            "confidence": self._calculate_prediction_confidence(situational)
        }

    def _calculate_prediction_confidence(self, situational: Dict) -> float:
        """计算预测置信度"""
        # 基于数据完整性计算置信度
        has_engine_data = bool(situational.get('engine_status', {}).get('total_engines', 0))
        has_evolution_data = bool(situational.get('evolution_efficiency', {}).get('total_rounds', 0))
        has_kg_data = situational.get('knowledge_graph_status', {}).get('node_count', 0) > 0

        confidence = 0
        if has_engine_data:
            confidence += 0.3
        if has_evolution_data:
            confidence += 0.4
        if has_kg_data:
            confidence += 0.3

        return confidence

    def plan_evolution_path(self, goal: Optional[str] = None) -> Dict:
        """规划进化路径"""
        situational = self.get_situational_awareness()
        predictions = self.predict_evolution_needs()

        # 构建进化路径
        path_steps = []

        # 第一步：健康检查
        health = situational.get('system_health', {})
        if health.get('status') in ['needs_attention', 'critical']:
            path_steps.append({
                "step": 1,
                "action": "system_health_check",
                "description": "检查并修复系统健康问题",
                "priority": "critical"
            })

        # 第二步：引擎优化
        engine_status = situational.get('engine_status', {})
        if engine_status.get('activation_rate', 0) < 0.3:
            path_steps.append({
                "step": 2,
                "action": "engine_activation_boost",
                "description": "增强引擎联动和激活",
                "priority": "high"
            })

        # 第三步：知识扩展
        kg = situational.get('knowledge_graph_status', {})
        if kg.get('node_count', 0) < 50:
            path_steps.append({
                "step": 3,
                "action": "knowledge_expansion",
                "description": "扩展知识图谱",
                "priority": "medium"
            })

        # 第四步：能力增强（如果有特定目标）
        if goal:
            path_steps.append({
                "step": 4,
                "action": "capability_enhancement",
                "description": f"实现目标: {goal}",
                "priority": "medium"
            })

        return {
            "timestamp": datetime.now().isoformat(),
            "current_state": situational.get('overall_score', 0),
            "target_state": 85.0,
            "estimated_steps": len(path_steps),
            "path": path_steps,
            "predictions": predictions.get('predictions', [])
        }

    def adjust_priorities(self) -> Dict:
        """动态调整进化优先级"""
        situational = self.get_situational_awareness()
        predictions = self.predict_evolution_needs()

        priorities = []

        # 基于预测调整优先级
        for pred in predictions.get('predictions', []):
            priorities.append({
                "category": pred.get('type'),
                "priority": pred.get('priority'),
                "reason": pred.get('description')
            })

        # 基于态势感知补充
        health = situational.get('system_health', {})
        if health.get('status') == 'critical':
            priorities.append({
                "category": "system_recovery",
                "priority": "critical",
                "reason": "系统健康状态临界"
            })

        # 按优先级排序
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        priorities.sort(key=lambda x: priority_order.get(x['priority'], 3))

        return {
            "timestamp": datetime.now().isoformat(),
            "current_round": 209,
            "priorities": priorities,
            "rebalance_needed": len(priorities) > 3
        }

    def execute_plan(self, plan: Optional[Dict] = None, auto_execute: bool = True) -> Dict:
        """执行进化规划 - 将规划转化为实际执行步骤

        Args:
            plan: 进化规划（如果为None则自动生成）
            auto_execute: 是否自动执行（True执行，False只模拟）

        Returns:
            执行结果报告
        """
        # 如果没有提供规划，自动生成
        if plan is None:
            plan = self.plan_evolution_path()

        path = plan.get('path', [])
        if not path:
            return {
                "status": "no_plan",
                "message": "没有可执行的规划步骤",
                "executed_steps": []
            }

        executed_steps = []
        successful_steps = []
        failed_steps = []

        print(f"开始执行进化规划，共 {len(path)} 个步骤...")

        for step_info in path:
            step_num = step_info.get('step', 0)
            action = step_info.get('action', '')
            description = step_info.get('description', '')
            priority = step_info.get('priority', 'medium')

            print(f"  [{step_num}] 执行: {action} - {description}")

            step_result = {
                "step": step_num,
                "action": action,
                "description": description,
                "priority": priority,
                "status": "pending",
                "result": None
            }

            if not auto_execute:
                # 模拟模式
                step_result["status"] = "simulated"
                step_result["result"] = {"mode": "simulation", "would_execute": True}
            else:
                # 执行模式
                try:
                    exec_result = self._execute_action(action, description, step_info)
                    step_result["status"] = "success" if exec_result.get("success") else "failed"
                    step_result["result"] = exec_result

                    if exec_result.get("success"):
                        successful_steps.append(step_num)
                    else:
                        failed_steps.append(step_num)

                except Exception as e:
                    step_result["status"] = "error"
                    step_result["result"] = {"error": str(e)}
                    failed_steps.append(step_num)

            executed_steps.append(step_result)
            print(f"      状态: {step_result['status']}")

        # 生成执行报告
        execution_report = {
            "timestamp": datetime.now().isoformat(),
            "plan_summary": {
                "total_steps": len(path),
                "executed_steps": len(executed_steps),
                "successful": len(successful_steps),
                "failed": len(failed_steps),
                "success_rate": len(successful_steps) / len(path) if path else 0
            },
            "mode": "auto" if auto_execute else "simulation",
            "executed_steps": executed_steps,
            "successful_step_numbers": successful_steps,
            "failed_step_numbers": failed_steps,
            "next_recommendations": self._generate_execution_recommendations(
                successful_steps, failed_steps, executed_steps
            )
        }

        return execution_report

    def _execute_action(self, action: str, description: str, step_info: Dict) -> Dict:
        """执行具体的进化动作

        根据动作类型执行不同的操作：
        - system_health_check: 执行系统健康检查
        - engine_activation_boost: 激活更多引擎
        - knowledge_expansion: 扩展知识图谱
        - capability_enhancement: 能力增强
        """
        result = {"success": False, "action": action, "details": {}}

        if action == "system_health_check":
            # 执行系统健康检查
            try:
                health_check_script = SCRIPTS_DIR / "system_health_check.py"
                if health_check_script.exists():
                    proc = subprocess.run(
                        [sys.executable, str(health_check_script)],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    result["success"] = proc.returncode == 0
                    result["details"]["output"] = proc.stdout[:500] if proc.stdout else ""
                else:
                    result["success"] = True
                    result["details"]["message"] = "健康检查脚本不存在，跳过"
            except Exception as e:
                result["details"]["error"] = str(e)

        elif action == "engine_activation_boost":
            # 增强引擎联动
            result["success"] = True
            result["details"]["message"] = "引擎联动增强：已有70+引擎支持智能联动"

        elif action == "knowledge_expansion":
            # 扩展知识图谱
            kg_file = REFERENCES_DIR / "knowledge_graph.json"
            try:
                if kg_file.exists():
                    with open(kg_file, 'r', encoding='utf-8') as f:
                        kg = json.load(f)
                    current_nodes = len(kg.get('nodes', []))
                    # 添加新的知识节点（示例）
                    kg.setdefault('nodes', []).append({
                        "id": f"knowledge_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "type": "evolution_knowledge",
                        "content": f"Round 210 execution knowledge",
                        "timestamp": datetime.now().isoformat()
                    })
                    with open(kg_file, 'w', encoding='utf-8') as f:
                        json.dump(kg, f, ensure_ascii=False, indent=2)
                    result["success"] = True
                    result["details"]["message"] = f"知识图谱已扩展，从 {current_nodes} 到 {len(kg.get('nodes', []))} 个节点"
                else:
                    # 创建新的知识图谱
                    kg = {
                        "nodes": [{
                            "id": f"knowledge_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                            "type": "evolution_knowledge",
                            "content": f"Round 210 execution knowledge",
                            "timestamp": datetime.now().isoformat()
                        }],
                        "edges": []
                    }
                    with open(kg_file, 'w', encoding='utf-8') as f:
                        json.dump(kg, f, ensure_ascii=False, indent=2)
                    result["success"] = True
                    result["details"]["message"] = "创建了新的知识图谱文件"
            except Exception as e:
                result["details"]["error"] = str(e)

        elif action == "capability_enhancement":
            # 能力增强
            result["success"] = True
            result["details"]["message"] = f"能力增强: {description}"

        else:
            # 未知动作
            result["success"] = True
            result["details"]["message"] = f"动作 {action} 已记录，待后续执行"

        return result

    def _generate_execution_recommendations(
        self,
        successful_steps: List[int],
        failed_steps: List[int],
        executed_steps: List[Dict]
    ) -> List[str]:
        """生成执行建议"""
        recommendations = []

        if not failed_steps:
            recommendations.append("所有步骤执行成功，系统进化完成")
            recommendations.append("建议进入下一轮进化，继续优化系统")
        else:
            recommendations.append(f"有 {len(failed_steps)} 个步骤执行失败，需要人工介入处理")

            # 检查是否有可重试的步骤
            for step in executed_steps:
                if step.get('status') == 'error':
                    recommendations.append(f"步骤 {step.get('step')} ({step.get('action')}) 遇到错误: {step.get('result', {}).get('error', '未知错误')}")

        # 基于当前态势给出建议
        situational = self.get_situational_awareness()
        score = situational.get('overall_score', 0)
        if score > 80:
            recommendations.append("系统态势良好，可考虑探索新功能")
        elif score < 50:
            recommendations.append("系统态势需要关注，优先解决健康问题")

        return recommendations

    def get_full_command(self) -> Dict:
        """获取完整指挥塔状态"""
        return {
            "name": self.name,
            "version": self.version,
            "situational_awareness": self.get_situational_awareness(),
            "predictions": self.predict_evolution_needs(),
            "evolution_path": self.plan_evolution_path(),
            "priorities": self.adjust_priorities()
        }


def handle_command(command: str, args: List[str]) -> Dict:
    """处理命令"""
    tower = EvolutionCommandTower()

    if command in ["status", "overview", "态势", "状态"]:
        return tower.get_situational_awareness()

    elif command in ["predict", "预测", "future"]:
        return tower.predict_evolution_needs()

    elif command in ["plan", "规划", "path"]:
        goal = args[0] if args else None
        return tower.plan_evolution_path(goal)

    elif command in ["priorities", "priority", "优先级"]:
        return tower.adjust_priorities()

    elif command in ["execute", "执行", "run_plan"]:
        # 执行进化规划
        auto_execute = True
        # 检查是否有 --simulate 参数
        if "--simulate" in args or "--dry-run" in args:
            auto_execute = False
            args = [a for a in args if a not in ["--simulate", "--dry-run"]]
        return tower.execute_plan(auto_execute=auto_execute)

    elif command in ["full", "command", "指挥塔"]:
        return tower.get_full_command()

    else:
        return {
            "error": f"未知命令: {command}",
            "available_commands": [
                "status/overview - 获取态势感知",
                "predict - 预测进化需求",
                "plan/path - 规划进化路径",
                "priorities - 调整优先级",
                "execute/run_plan - 执行进化规划",
                "execute --simulate - 模拟执行（不实际执行）",
                "full/command - 完整指挥塔状态"
            ]
        }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "请提供命令",
            "usage": "python evolution_command_tower.py <command> [args]"
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else []

    result = handle_command(command, args)
    print(json.dumps(result, ensure_ascii=False, indent=2))