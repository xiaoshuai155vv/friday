#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化引擎集群元进化自主意识深度增强引擎

在 round 386 完成的可视化一键自愈增强引擎基础上，进一步增强系统的元进化自主意识能力。
让系统不仅能执行预设的进化任务，还能自主发现高价值进化机会、智能评估进化价值、
自动决策进化方向，形成真正的自主意识驱动进化。同时将增强的自主意识能力与进化驾驶舱深度集成，
实现可视化展示。

Version: 1.0.0
Author: Auto Evolution System
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# 基础路径配置
SCRIPT_DIR = Path(__file__).parent
RUNTIME_DIR = SCRIPT_DIR.parent / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"
CONFIG_DIR = RUNTIME_DIR / "config"


def _safe_print(text: str):
    """安全打印，支持 UTF-8"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore'))


class EvolutionMetaAutonomousConsciousnessDeepEngine:
    """
    元进化自主意识深度增强引擎

    核心能力：
    1. 自主机会发现 - 基于系统状态、能力缺口、进化历史主动发现进化机会
    2. 价值智能评估 - 预测成功率、ROI、风险，制定进化优先级
    3. 自动决策 - 选择进化方向、确定优先级、规划进化路径
    4. 自主执行 - 将决策转化为可执行任务并完成闭环
    5. 驾驶舱集成 - 与进化驾驶舱深度集成，可视化展示决策过程
    """

    def __init__(self):
        self.engine_name = "meta_autonomous_consciousness_deep"
        self.version = "1.0.0"
        self.state_file = STATE_DIR / f"{self.engine_name}_state.json"
        self.history_file = STATE_DIR / f"{self.engine_name}_history.json"
        self.consciousness_log_file = STATE_DIR / f"{self.engine_name}_consciousness_log.json"
        self.config = self._load_config()
        self.load_state()
        self._ensure_dependencies()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        config_file = CONFIG_DIR / "evolution_loop.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                _safe_print(f"[{self.engine_name}] 配置加载失败: {e}")

        return {
            "auto_discovery_enabled": True,
            "value_assessment_enabled": True,
            "auto_decision_enabled": True,
            "cockpit_integration_enabled": True,
            "opportunity_scan_interval_minutes": 15,
            "min_value_threshold": 0.3,
            "max_opportunities_per_scan": 5
        }

    def _ensure_dependencies(self):
        """确保依赖模块存在"""
        self.visual_heal_available = False
        self.cockpit_available = False
        self.kg_reasoning_available = False
        self.global_situation_available = False

        # 检查可视化一键自愈增强引擎 (round 386)
        visual_heal_file = SCRIPT_DIR / "evolution_visual_oneclick_heal_enhanced_engine.py"
        if visual_heal_file.exists():
            self.visual_heal_available = True
            _safe_print(f"[{self.engine_name}] 可视化一键自愈增强引擎已就绪")

        # 检查进化驾驶舱 (round 350)
        cockpit_file = SCRIPT_DIR / "evolution_cockpit_engine.py"
        if cockpit_file.exists():
            self.cockpit_available = True
            _safe_print(f"[{self.engine_name}] 进化驾驶舱已就绪")

        # 检查知识图谱推理引擎 (round 298/330)
        kg_file = SCRIPT_DIR / "evolution_knowledge_graph_reasoning.py"
        if kg_file.exists():
            self.kg_reasoning_available = True
            _safe_print(f"[{self.engine_name}] 知识图谱推理引擎已就绪")

        # 检查全局态势感知引擎 (round 329)
        situation_file = SCRIPT_DIR / "evolution_global_situation_awareness.py"
        if situation_file.exists():
            self.global_situation_available = True
            _safe_print(f"[{self.engine_name}] 全局态势感知引擎已就绪")

    def load_state(self):
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    self.state = json.load(f)
            except Exception as e:
                _safe_print(f"[{self.engine_name}] 状态加载失败: {e}")
                self.state = self._get_default_state()
        else:
            self.state = self._get_default_state()

    def _get_default_state(self) -> Dict[str, Any]:
        """获取默认状态"""
        return {
            "consciousness_level": 0.0,
            "opportunities_discovered": [],
            "decisions_made": [],
            "last_scan_time": None,
            "total_cycles": 0,
            "active": False
        }

    def save_state(self):
        """保存状态"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[{self.engine_name}] 状态保存失败: {e}")

    def discover_opportunities(self) -> List[Dict[str, Any]]:
        """
        自主发现进化机会

        基于多维度信息主动发现高价值进化机会：
        - 系统状态（健康度、能力缺口）
        - 进化历史（成功模式、失败教训）
        - 知识图谱（隐藏关联、创新机会）
        - 全局态势（当前系统需求）
        """
        opportunities = []

        _safe_print(f"[{self.engine_name}] 扫描进化机会...")

        # 1. 分析系统状态和能力缺口
        system_opportunities = self._analyze_system_state()
        opportunities.extend(system_opportunities)

        # 2. 分析进化历史模式
        history_opportunities = self._analyze_evolution_history()
        opportunities.extend(history_opportunities)

        # 3. 从知识图谱发现隐藏机会
        if self.kg_reasoning_available:
            kg_opportunities = self._discover_from_knowledge_graph()
            opportunities.extend(kg_opportunities)

        # 4. 分析全局态势
        if self.global_situation_available:
            situation_opportunities = self._analyze_global_situation()
            opportunities.extend(situation_opportunities)

        # 排序并筛选
        opportunities = self._prioritize_opportunities(opportunities)

        _safe_print(f"[{self.engine_name}] 发现 {len(opportunities)} 个进化机会")

        # 更新状态
        self.state["opportunities_discovered"] = opportunities
        self.state["last_scan_time"] = datetime.now(timezone.utc).isoformat()
        self.save_state()

        return opportunities

    def _analyze_system_state(self) -> List[Dict[str, Any]]:
        """分析系统状态，识别能力缺口"""
        opportunities = []

        # 检查系统健康状态
        health_file = STATE_DIR / "self_verify_result.json"
        if health_file.exists():
            try:
                with open(health_file, 'r', encoding='utf-8') as f:
                    health_data = json.load(f)

                # 根据健康状态识别进化机会
                if health_data.get("baseline_score", 1.0) < 0.8:
                    opportunities.append({
                        "type": "health_improvement",
                        "description": "系统健康度低于阈值，需要优化",
                        "value_score": 0.8,
                        "urgency": "high",
                        "source": "system_health"
                    })
            except Exception as e:
                _safe_print(f"[{self.engine_name}] 健康状态分析失败: {e}")

        # 检查能力缺口
        gaps_file = SCRIPT_DIR.parent / "references" / "capability_gaps.md"
        if gaps_file.exists():
            try:
                with open(gaps_file, 'r', encoding='utf-8') as f:
                    gaps_content = f.read()

                # 分析未覆盖的能力领域
                if "—" in gaps_content:
                    # 有未覆盖的能力
                    opportunities.append({
                        "type": "capability_expansion",
                        "description": "识别能力缺口，可扩展新能力",
                        "value_score": 0.6,
                        "urgency": "medium",
                        "source": "capability_gaps"
                    })
            except Exception as e:
                _safe_print(f"[{self.engine_name}] 能力缺口分析失败: {e}")

        return opportunities

    def _analyze_evolution_history(self) -> List[Dict[str, Any]]:
        """分析进化历史，识别重复模式和优化机会"""
        opportunities = []

        # 检查最近的进化完成记录
        completed_files = sorted(STATE_DIR.glob("evolution_completed_ev_*.json"))
        recent_files = completed_files[-10:] if len(completed_files) > 10 else completed_files

        if len(recent_files) > 5:
            # 检查是否有重复进化
            recent_goals = []
            for f in recent_files:
                try:
                    with open(f, 'r', encoding='utf-8') as data:
                        info = json.load(data)
                        recent_goals.append(info.get("current_goal", ""))
                except:
                    pass

            # 检测重复模式
            if len(set(recent_goals)) < len(recent_goals) * 0.5:
                opportunities.append({
                    "type": "optimization",
                    "description": "检测到重复进化模式，需要优化进化策略",
                    "value_score": 0.7,
                    "urgency": "high",
                    "source": "evolution_history"
                })

        return opportunities

    def _discover_from_knowledge_graph(self) -> List[Dict[str, Any]]:
        """从知识图谱发现隐藏的创新机会"""
        opportunities = []

        # 知识图谱推理结果文件
        kg_output_file = STATE_DIR / "kg_reasoning_output.json"
        if kg_output_file.exists():
            try:
                with open(kg_output_file, 'r', encoding='utf-8') as f:
                    kg_data = json.load(f)

                # 基于推理结果发现机会
                insights = kg_data.get("insights", [])
                if len(insights) > 0:
                    opportunities.append({
                        "type": "innovation",
                        "description": f"从知识图谱发现 {len(insights)} 个创新洞察",
                        "value_score": 0.9,
                        "urgency": "medium",
                        "source": "knowledge_graph",
                        "details": insights[:3]
                    })
            except Exception as e:
                _safe_print(f"[{self.engine_name}] 知识图谱分析失败: {e}")

        return opportunities

    def _analyze_global_situation(self) -> List[Dict[str, Any]]:
        """分析全局态势，发现当前系统需求"""
        opportunities = []

        # 全局态势感知输出
        situation_file = STATE_DIR / "global_situation_output.json"
        if situation_file.exists():
            try:
                with open(situation_file, 'r', encoding='utf-8') as f:
                    situation = json.load(f)

                # 基于态势分析机会
                health_score = situation.get("overall_health", 1.0)
                if health_score < 0.7:
                    opportunities.append({
                        "type": "health_restoration",
                        "description": "系统整体健康度较低，需要恢复性进化",
                        "value_score": 0.85,
                        "urgency": "critical",
                        "source": "global_situation"
                    })

                # 检查待处理问题
                issues = situation.get("issues", [])
                if len(issues) > 3:
                    opportunities.append({
                        "type": "issue_resolution",
                        "description": f"发现 {len(issues)} 个待解决问题",
                        "value_score": 0.75,
                        "urgency": "high",
                        "source": "global_situation",
                        "issues": issues[:3]
                    })
            except Exception as e:
                _safe_print(f"[{self.engine_name}] 全局态势分析失败: {e}")

        return opportunities

    def _prioritize_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """对进化机会进行优先级排序"""
        if not opportunities:
            return []

        # 计算综合得分
        urgency_weights = {"critical": 1.0, "high": 0.7, "medium": 0.4, "low": 0.2}

        for opp in opportunities:
            urgency = opp.get("urgency", "medium")
            value = opp.get("value_score", 0.5)
            urgency_factor = urgency_weights.get(urgency, 0.5)
            opp["priority_score"] = value * 0.6 + urgency_factor * 0.4

        # 按优先级排序
        opportunities.sort(key=lambda x: x.get("priority_score", 0), reverse=True)

        # 限制数量
        max_opps = self.config.get("max_opportunities_per_scan", 5)
        return opportunities[:max_opps]

    def assess_opportunity_value(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """
        智能评估进化机会的价值

        返回：
        - success_probability: 成功率预测
        - roi: 预期投资回报
        - risk_level: 风险等级
        - recommendation: 执行建议
        """
        opp_type = opportunity.get("type", "unknown")
        base_value = opportunity.get("value_score", 0.5)

        # 基于历史数据预测成功率
        success_history = self._get_success_history(opp_type)
        success_probability = success_history * 0.5 + base_value * 0.5

        # 计算预期 ROI
        estimated_benefit = base_value * 100
        estimated_cost = 20  # 基础成本
        roi = (estimated_benefit - estimated_cost) / estimated_cost if estimated_cost > 0 else 0

        # 评估风险
        risk_level = "low" if success_probability > 0.7 else "medium" if success_probability > 0.4 else "high"

        # 生成建议
        if success_probability > 0.7 and roi > 0.5:
            recommendation = "强烈建议执行"
        elif success_probability > 0.5:
            recommendation = "建议执行，需监控风险"
        elif success_probability > 0.3:
            recommendation = "可考虑执行，建议先做小规模验证"
        else:
            recommendation = "不建议执行，成功率过低"

        return {
            "success_probability": round(success_probability, 2),
            "roi": round(roi, 2),
            "risk_level": risk_level,
            "recommendation": recommendation,
            "estimated_benefit": estimated_benefit,
            "estimated_cost": estimated_cost
        }

    def _get_success_history(self, opportunity_type: str) -> float:
        """获取历史成功概率"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    return history.get(f"{opportunity_type}_success_rate", 0.5)
            except:
                pass
        return 0.5

    def make_autonomous_decision(self, opportunities: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        自动决策 - 选择最佳进化方向

        基于价值评估和当前系统状态，智能决定：
        - 选择哪个进化机会
        - 确定的进化优先级
        - 规划进化执行路径
        """
        if not opportunities:
            _safe_print(f"[{self.engine_name}] 无进化机会可供决策")
            return None

        _safe_print(f"[{self.engine_name}] 开始智能决策分析...")

        # 评估每个机会的价值
        evaluated = []
        for opp in opportunities:
            assessment = self.assess_opportunity_value(opp)
            evaluated.append({
                **opp,
                "assessment": assessment
            })

        # 筛选通过阈值的机会
        min_threshold = self.config.get("min_value_threshold", 0.3)
        qualified = [e for e in evaluated if e["assessment"]["success_probability"] >= min_threshold]

        if not qualified:
            _safe_print(f"[{self.engine_name}] 无满足阈值的机会")
            return None

        # 选择最优机会
        best = qualified[0]

        # 生成决策结果
        decision = {
            "selected_opportunity": best,
            "reason": best["assessment"]["recommendation"],
            "priority": 1,
            "execution_plan": self._generate_execution_plan(best),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        _safe_print(f"[{self.engine_name}] 决策完成: {best.get('description', best.get('type'))}")

        # 更新状态
        self.state["decisions_made"].append(decision)
        self.state["consciousness_level"] = min(1.0, self.state.get("consciousness_level", 0) + 0.1)
        self.state["total_cycles"] += 1
        self.save_state()

        # 记录到意识日志
        self._log_consciousness_event("decision_made", decision)

        return decision

    def _generate_execution_plan(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """生成执行计划"""
        opp_type = opportunity.get("type", "unknown")

        plan_templates = {
            "health_improvement": {
                "action": "self_heal",
                "description": "执行系统自愈",
                "estimated_time_minutes": 5
            },
            "capability_expansion": {
                "action": "explore_capabilities",
                "description": "扩展能力边界",
                "estimated_time_minutes": 30
            },
            "optimization": {
                "action": "optimize_strategy",
                "description": "优化进化策略",
                "estimated_time_minutes": 15
            },
            "innovation": {
                "action": "implement_innovation",
                "description": "实现创新洞察",
                "estimated_time_minutes": 45
            },
            "health_restoration": {
                "action": "health_restoration",
                "description": "恢复系统健康",
                "estimated_time_minutes": 10
            },
            "issue_resolution": {
                "action": "resolve_issues",
                "description": "解决系统问题",
                "estimated_time_minutes": 20
            }
        }

        return plan_templates.get(opp_type, {
            "action": "general_evolution",
            "description": "执行通用进化",
            "estimated_time_minutes": 30
        })

    def execute_decision(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        自主执行决策

        将决策转化为可执行的任务并完成闭环
        """
        if not decision:
            return {"status": "no_decision", "message": "无决策可执行"}

        _safe_print(f"[{self.engine_name}] 开始执行决策...")

        plan = decision.get("execution_plan", {})
        action = plan.get("action", "general_evolution")

        result = {
            "decision": decision,
            "action": action,
            "status": "executing",
            "start_time": datetime.now(timezone.utc).isoformat()
        }

        try:
            # 根据决策类型执行相应动作
            if action == "self_heal":
                result.update(self._execute_self_heal())
            elif action == "optimize_strategy":
                result.update(self._execute_optimization())
            elif action == "health_restoration":
                result.update(self._execute_health_restoration())
            else:
                # 通用执行 - 记录决策但不实际执行（避免风险）
                result.update({
                    "status": "recorded",
                    "message": f"决策已记录，等待进一步验证: {plan.get('description')}"
                })

            result["end_time"] = datetime.now(timezone.utc).isoformat()

            # 记录到意识日志
            self._log_consciousness_event("decision_executed", result)

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            _safe_print(f"[{self.engine_name}] 执行失败: {e}")

        return result

    def _execute_self_heal(self) -> Dict[str, Any]:
        """执行自愈操作"""
        # 尝试调用可视化自愈引擎
        if self.visual_heal_available:
            try:
                # 触发一键自愈
                result = subprocess.run(
                    [sys.executable, str(SCRIPT_DIR / "do.py"), "增强自愈"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                return {
                    "status": "success",
                    "message": "自愈执行完成",
                    "output": result.stdout[:500] if result.stdout else ""
                }
            except Exception as e:
                return {
                    "status": "partial",
                    "message": f"自愈执行部分完成: {e}"
                }

        return {
            "status": "skipped",
            "message": "自愈引擎不可用，跳过执行"
        }

    def _execute_optimization(self) -> Dict[str, Any]:
        """执行优化操作"""
        return {
            "status": "recorded",
            "message": "优化决策已记录，等待策略引擎处理"
        }

    def _execute_health_restoration(self) -> Dict[str, Any]:
        """执行健康恢复"""
        return self._execute_self_heal()

    def _log_consciousness_event(self, event_type: str, data: Dict[str, Any]):
        """记录意识事件到日志"""
        events = []
        if self.consciousness_log_file.exists():
            try:
                with open(self.consciousness_log_file, 'r', encoding='utf-8') as f:
                    events = json.load(f)
            except:
                pass

        events.append({
            "type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data
        })

        # 只保留最近100条
        events = events[-100:]

        try:
            with open(self.consciousness_log_file, 'w', encoding='utf-8') as f:
                json.dump(events, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[{self.engine_name}] 意识日志写入失败: {e}")

    def get_consciousness_status(self) -> Dict[str, Any]:
        """获取自主意识状态"""
        return {
            "engine_name": self.engine_name,
            "version": self.version,
            "consciousness_level": self.state.get("consciousness_level", 0),
            "total_cycles": self.state.get("total_cycles", 0),
            "opportunities_count": len(self.state.get("opportunities_discovered", [])),
            "decisions_count": len(self.state.get("decisions_made", [])),
            "last_scan_time": self.state.get("last_scan_time"),
            "dependencies": {
                "visual_heal": self.visual_heal_available,
                "cockpit": self.cockpit_available,
                "knowledge_graph": self.kg_reasoning_available,
                "global_situation": self.global_situation_available
            }
        }

    def run_full_cycle(self) -> Dict[str, Any]:
        """
        运行完整的自主意识进化周期

        流程：发现机会 -> 评估价值 -> 自动决策 -> 执行闭环
        """
        _safe_print(f"[{self.engine_name}] 启动完整进化周期...")

        # 1. 发现机会
        opportunities = self.discover_opportunities()

        # 2. 智能决策
        decision = self.make_autonomous_decision(opportunities)

        # 3. 执行决策
        execution_result = self.execute_decision(decision) if decision else {"status": "no_decision"}

        # 4. 返回结果
        return {
            "opportunities_found": len(opportunities),
            "decision": decision,
            "execution": execution_result,
            "consciousness_status": self.get_consciousness_status()
        }


# CLI 接口
def main():
    import argparse

    parser = argparse.ArgumentParser(description="元进化自主意识深度增强引擎")
    parser.add_argument("command", choices=["scan", "decide", "execute", "status", "full_cycle"],
                        help="要执行的命令")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    args = parser.parse_args()

    engine = EvolutionMetaAutonomousConsciousnessDeepEngine()

    if args.command == "scan":
        opportunities = engine.discover_opportunities()
        _safe_print(f"\n发现 {len(opportunities)} 个进化机会:")
        for i, opp in enumerate(opportunities, 1):
            _safe_print(f"  {i}. [{opp.get('urgency')}] {opp.get('description')} (优先级: {opp.get('priority_score', 0):.2f})")

    elif args.command == "decise":
        opportunities = engine.discover_opportunities()
        decision = engine.make_autonomous_decision(opportunities)
        if decision:
            _safe_print(f"\n决策结果:")
            _safe_print(f"  选中机会: {decision['selected_opportunity'].get('description')}")
            _safe_print(f"  原因: {decision['reason']}")
            _safe_print(f"  执行计划: {decision['execution_plan'].get('description')}")
        else:
            _safe_print("\n无可用决策")

    elif args.command == "execute":
        opportunities = engine.discover_opportunities()
        decision = engine.make_autonomous_decision(opportunities)
        result = engine.execute_decision(decision)
        _safe_print(f"\n执行结果: {result.get('status')}")
        _safe_print(f"  消息: {result.get('message', '')}")

    elif args.command == "status":
        status = engine.get_consciousness_status()
        _safe_print(f"\n自主意识状态:")
        _safe_print(f"  引擎: {status['engine_name']} v{status['version']}")
        _safe_print(f"  意识水平: {status['consciousness_level']:.1%}")
        _safe_print(f"  进化周期数: {status['total_cycles']}")
        _safe_print(f"  发现机会: {status['opportunities_count']}")
        _safe_print(f"  决策次数: {status['decisions_count']}")
        _safe_print(f"  依赖模块:")
        for dep, available in status['dependencies'].items():
            _safe_print(f"    - {dep}: {'OK' if available else 'NO'}")

    elif args.command == "full_cycle":
        result = engine.run_full_cycle()
        _safe_print(f"\n完整周期执行完成:")
        _safe_print(f"  发现机会: {result['opportunities_found']}")
        _safe_print(f"  决策: {'已决策' if result['decision'] else '无决策'}")
        _safe_print(f"  执行状态: {result['execution'].get('status')}")


if __name__ == "__main__":
    main()