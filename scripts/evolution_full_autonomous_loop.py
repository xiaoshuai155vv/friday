#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能进化全自主闭环引擎 (Evolution Full Autonomous Loop Engine)
版本: 1.0.0
功能: 让进化环能够真正自主运行、主动触发、形成完整闭环。
     1) 自动检测进化需求（基于系统状态、能力缺口、历史进化等）
     2) 主动触发进化环
     3) 自主执行进化流程
     4) 自动验证进化效果
     5) 自主优化进化策略

集成到 do.py 支持关键词：
- 全自主进化、自主闭环、进化自主运行
- 自动进化检测、主动进化触发
- 自主进化执行、进化效果验证
"""

import json
import os
import sys
import time
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

# 添加脚本目录到路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))


class AutonomousLevel(Enum):
    """自主等级"""
    MANUAL = "manual"           # 手动触发
    SEMI_AUTONOMOUS = "semi"    # 半自动（需要确认）
    FULLY_AUTONOMOUS = "full"   # 完全自主


class EvolutionNeedType(Enum):
    """进化需求类型"""
    CAPABILITY_GAP = "capability_gap"     # 能力缺口
    FAILURE_PATTERN = "failure_pattern"    # 失败模式
    PERFORMANCE = "performance"           # 性能优化
    SYSTEM_HEALTH = "system_health"        # 系统健康
    OPPORTUNITY = "opportunity"           # 优化机会
    SCHEDULED = "scheduled"                # 定时任务


@dataclass
class EvolutionNeed:
    """进化需求"""
    id: str
    type: str
    priority: int  # 1-10, 10 最高
    description: str
    source: str  # 来源（capability_gaps, failures, system_health 等）
    detected_at: str
    auto_approved: bool = False
    executed: bool = False


@dataclass
class EvolutionExecution:
    """进化执行记录"""
    need_id: str
    round: int
    goal: str
    started_at: str
    completed_at: Optional[str] = None
    status: str = "pending"  # pending, running, completed, failed
    result: Dict[str, Any] = field(default_factory=dict)
    verification_passed: bool = False


class EvolutionFullAutonomousLoop:
    """智能进化全自主闭环引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.state_dir = SCRIPT_DIR / ".." / "runtime" / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # 状态
        self.autonomous_level = AutonomousLevel.FULLY_AUTONOMOUS
        self.evolution_needs: List[EvolutionNeed] = []
        self.executions: List[EvolutionExecution] = []
        self.is_running = False
        self.monitor_thread = None
        self._stop_event = threading.Event()

        # 加载状态
        self._load_state()

        # 初始化组件
        self._init_components()

    def _load_state(self):
        """加载状态"""
        state_file = self.state_dir / "evolution_autonomous_state.json"
        if state_file.exists():
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.autonomous_level = AutonomousLevel(
                        data.get("autonomous_level", "full")
                    )
                    # 加载进化需求
                    self.evolution_needs = [
                        EvolutionNeed(**n) for n in data.get("needs", [])
                    ]
                    # 加载执行记录
                    self.executions = [
                        EvolutionExecution(**e) for e in data.get("executions", [])
                    ]
            except Exception as e:
                print(f"加载状态失败: {e}")

    def _save_state(self):
        """保存状态"""
        state_file = self.state_dir / "evolution_autonomous_state.json"
        try:
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump({
                    "autonomous_level": self.autonomous_level.value,
                    "needs": [
                        {
                            "id": n.id,
                            "type": n.type,
                            "priority": n.priority,
                            "description": n.description,
                            "source": n.source,
                            "detected_at": n.detected_at,
                            "auto_approved": n.auto_approved,
                            "executed": n.executed
                        } for n in self.evolution_needs
                    ],
                    "executions": [
                        {
                            "need_id": e.need_id,
                            "round": e.round,
                            "goal": e.goal,
                            "started_at": e.started_at,
                            "completed_at": e.completed_at,
                            "status": e.status,
                            "result": e.result,
                            "verification_passed": e.verification_passed
                        } for e in self.executions
                    ],
                    "last_updated": datetime.now(timezone.utc).isoformat()
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存状态失败: {e}")

    def _init_components(self):
        """初始化组件"""
        # 尝试导入相关模块
        self.conditional_trigger = None
        self.adaptive_optimizer = None
        self.direction_discovery = None
        self.effectiveness_evaluator = None

        try:
            from evolution_conditional_trigger import EvolutionConditionalTriggerEngine
            self.conditional_trigger = EvolutionConditionalTriggerEngine()
        except ImportError:
            pass

        try:
            from evolution_adaptive_optimizer import EvolutionAdaptiveOptimizer
            self.adaptive_optimizer = EvolutionAdaptiveOptimizer()
        except ImportError:
            pass

        try:
            from evolution_direction_discovery import EvolutionDirectionDiscoveryEngine
            self.direction_discovery = EvolutionDirectionDiscoveryEngine()
        except ImportError:
            pass

        try:
            from evolution_effectiveness_evaluator import EvolutionEffectivenessEvaluator
            self.effectiveness_evaluator = EvolutionEffectivenessEvaluator()
        except ImportError:
            pass

    def detect_evolution_needs(self) -> List[EvolutionNeed]:
        """检测进化需求"""
        needs = []

        # 1. 检测能力缺口
        gaps_file = SCRIPT_DIR / ".." / "references" / "capability_gaps.md"
        if gaps_file.exists():
            try:
                content = gaps_file.read_text(encoding="utf-8")
                # 检查是否有新的可行方向
                for line in content.split("\n"):
                    if "—" in line and "已覆盖" not in line:
                        # 发现潜在进化点
                        need = EvolutionNeed(
                            id=f"need_{int(time.time())}",
                            type=EvolutionNeedType.CAPABILITY_GAP.value,
                            priority=5,
                            description=f"能力缺口: {line.strip()}",
                            source="capability_gaps",
                            detected_at=datetime.now(timezone.utc).isoformat()
                        )
                        needs.append(need)
            except Exception as e:
                print(f"检测能力缺口失败: {e}")

        # 2. 检测失败模式
        failures_file = SCRIPT_DIR / ".." / "references" / "failures.md"
        if failures_file.exists():
            try:
                content = failures_file.read_text(encoding="utf-8")
                # 检查最近的失败
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if "2026-03-" in line and "→" in line:
                        need = EvolutionNeed(
                            id=f"need_{int(time.time())}_{i}",
                            type=EvolutionNeedType.FAILURE_PATTERN.value,
                            priority=7,
                            description=f"失败教训: {line.strip()}",
                            source="failures",
                            detected_at=datetime.now(timezone.utc).isoformat()
                        )
                        needs.append(need)
            except Exception as e:
                print(f"检测失败模式失败: {e}")

        # 3. 检测系统健康问题
        try:
            # 读取当前任务状态
            mission_file = self.state_dir / "current_mission.json"
            if mission_file.exists():
                with open(mission_file, "r", encoding="utf-8") as f:
                    mission = json.load(f)
                    if mission.get("phase") == "假设":
                        need = EvolutionNeed(
                            id=f"need_{int(time.time())}_health",
                            type=EvolutionNeedType.SYSTEM_HEALTH.value,
                            priority=6,
                            description="系统处于假设阶段，可以主动触发进化",
                            source="system_state",
                            detected_at=datetime.now(timezone.utc).isoformat()
                        )
                        needs.append(need)
        except Exception as e:
            print(f"检测系统健康失败: {e}")

        # 4. 使用方向发现引擎
        if self.direction_discovery:
            try:
                directions = self.direction_discovery.discover_directions()
                for d in directions.get("directions", [])[:3]:
                    need = EvolutionNeed(
                        id=f"need_{int(time.time())}_dir",
                        type=EvolutionNeedType.OPPORTUNITY.value,
                        priority=d.get("priority", 5),
                        description=f"优化机会: {d.get('name', '未知')}",
                        source="direction_discovery",
                        detected_at=datetime.now(timezone.utc).isoformat()
                    )
                    needs.append(need)
            except Exception as e:
                print(f"方向发现失败: {e}")

        # 更新需求列表
        self.evolution_needs = needs
        self._save_state()

        return needs

    def should_auto_trigger(self) -> bool:
        """判断是否应该自动触发"""
        if self.autonomous_level == AutonomousLevel.MANUAL:
            return False

        # 检测是否有高优先级需求
        high_priority = [n for n in self.evolution_needs if n.priority >= 7]
        if high_priority:
            return True

        # 检查是否在假设阶段（可以主动触发）
        mission_file = self.state_dir / "current_mission.json"
        try:
            with open(mission_file, "r", encoding="utf-8") as f:
                mission = json.load(f)
                if mission.get("phase") == "假设":
                    # 半自动模式需要确认
                    if self.autonomous_level == AutonomousLevel.SEMI_AUTONOMOUS:
                        return False  # 需要用户确认
                    return True
        except:
            pass

        return False

    def get_current_round(self) -> int:
        """获取当前轮次"""
        mission_file = self.state_dir / "current_mission.json"
        try:
            with open(mission_file, "r", encoding="utf-8") as f:
                mission = json.load(f)
                return mission.get("loop_round", 254)
        except:
            return 254

    def trigger_evolution(self, need: Optional[EvolutionNeed] = None) -> Dict[str, Any]:
        """触发进化"""
        if need is None:
            # 自动选择最高优先级的需求
            sorted_needs = sorted(self.evolution_needs, key=lambda x: x.priority, reverse=True)
            if sorted_needs:
                need = sorted_needs[0]
            else:
                return {"success": False, "reason": "no_need", "message": "没有检测到进化需求"}

        # 创建执行记录
        current_round = self.get_current_round() + 1
        execution = EvolutionExecution(
            need_id=need.id,
            round=current_round,
            goal=need.description,
            started_at=datetime.now(timezone.utc).isoformat(),
            status="pending"
        )

        # 更新需求状态
        for n in self.evolution_needs:
            if n.id == need.id:
                n.auto_approved = True

        self.executions.append(execution)
        self._save_state()

        return {
            "success": True,
            "need": {
                "id": need.id,
                "type": need.type,
                "description": need.description,
                "priority": need.priority
            },
            "execution": {
                "round": current_round,
                "goal": need.description
            },
            "message": f"已触发 round {current_round} 进化: {need.description}"
        }

    def verify_evolution(self, round_num: int) -> Dict[str, Any]:
        """验证进化效果"""
        # 读取验证结果
        verify_file = self.state_dir / "self_verify_result.json"
        result = {
            "round": round_num,
            "verified_at": datetime.now(timezone.utc).isoformat(),
            "passed": False,
            "details": {}
        }

        if verify_file.exists():
            try:
                with open(verify_file, "r", encoding="utf-8") as f:
                    verify_data = json.load(f)
                    result["passed"] = verify_data.get("passed", False)
                    result["details"] = verify_data
            except Exception as e:
                result["details"]["error"] = str(e)

        # 更新执行记录
        for exec in self.executions:
            if exec.round == round_num:
                exec.completed_at = datetime.now(timezone.utc).isoformat()
                exec.status = "completed" if result["passed"] else "failed"
                exec.verification_passed = result["passed"]
                exec.result = result["details"]

        self._save_state()

        # 使用效果评估器
        if self.effectiveness_evaluator and result["passed"]:
            try:
                eval_result = self.effectiveness_evaluator.evaluate_round(round_num)
                result["effectiveness"] = eval_result
            except Exception as e:
                print(f"效果评估失败: {e}")

        return result

    def start_autonomous_loop(self):
        """启动全自主进化闭环"""
        if self.is_running:
            return {"success": False, "message": "已经在运行"}

        self.is_running = True
        self._stop_event.clear()

        def monitor_loop():
            while not self._stop_event.is_set():
                try:
                    # 1. 检测进化需求
                    needs = self.detect_evolution_needs()

                    # 2. 判断是否触发
                    if self.should_auto_trigger():
                        # 3. 触发进化
                        trigger_result = self.trigger_evolution()

                        # 4. 等待执行完成（简单模拟）
                        time.sleep(5)

                        # 5. 验证进化效果
                        current_round = self.get_current_round()
                        verify_result = self.verify_evolution(current_round)

                        # 6. 优化策略
                        if self.adaptive_optimizer and not verify_result["passed"]:
                            try:
                                self.adaptive_optimizer.adjust_strategy(
                                    current_round,
                                    verify_result
                                )
                            except Exception as e:
                                print(f"策略优化失败: {e}")

                except Exception as e:
                    print(f"自主进化循环错误: {e}")

                # 等待下一轮检测（5分钟）
                self._stop_event.wait(300)

        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()

        self._save_state()
        return {"success": True, "message": "全自主进化闭环已启动"}

    def stop_autonomous_loop(self):
        """停止全自主进化闭环"""
        if not self.is_running:
            return {"success": False, "message": "未在运行"}

        self._stop_event.set()
        self.is_running = False
        self._save_state()
        return {"success": True, "message": "全自主进化闭环已停止"}

    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        return {
            "version": self.version,
            "autonomous_level": self.autonomous_level.value,
            "is_running": self.is_running,
            "needs_count": len(self.evolution_needs),
            "executions_count": len(self.executions),
            "recent_needs": [
                {
                    "id": n.id,
                    "type": n.type,
                    "priority": n.priority,
                    "description": n.description[:50],
                    "auto_approved": n.auto_approved,
                    "executed": n.executed
                } for n in self.evolution_needs[:5]
            ],
            "recent_executions": [
                {
                    "round": e.round,
                    "goal": e.goal[:50],
                    "status": e.status,
                    "verification_passed": e.verification_passed
                } for e in self.executions[-5:]
            ]
        }

    def set_autonomous_level(self, level: str) -> Dict[str, Any]:
        """设置自主等级"""
        try:
            self.autonomous_level = AutonomousLevel(level)
            self._save_state()
            return {
                "success": True,
                "autonomous_level": self.autonomous_level.value,
                "message": f"已设置为 {self.autonomous_level.value} 模式"
            }
        except ValueError:
            return {
                "success": False,
                "message": f"无效的自主等级: {level}，可选: manual, semi, full"
            }

    def run_autonomous_cycle(self) -> Dict[str, Any]:
        """运行一个完整的自主进化周期"""
        # 1. 检测进化需求
        needs = self.detect_evolution_needs()

        if not needs:
            return {
                "success": True,
                "message": "当前没有检测到进化需求",
                "needs_count": 0
            }

        # 2. 触发进化
        trigger_result = self.trigger_evolution()

        # 3. 返回状态
        return {
            "success": True,
            "needs_detected": len(needs),
            "trigger_result": trigger_result,
            "message": f"检测到 {len(needs)} 个进化需求，已触发进化"
        }


# CLI 接口
def main():
    import argparse
    parser = argparse.ArgumentParser(description="智能进化全自主闭环引擎")
    parser.add_argument("command", nargs="?", help="命令: status, detect, trigger, verify, start, stop, level")
    parser.add_argument("--level", help="自主等级: manual, semi, full")
    parser.add_argument("--round", type=int, help="轮次号（验证用）")

    args = parser.parse_args()
    engine = EvolutionFullAutonomousLoop()

    if args.command == "status":
        print(json.dumps(engine.get_status(), ensure_ascii=False, indent=2))
    elif args.command == "detect":
        needs = engine.detect_evolution_needs()
        print(json.dumps({
            "needs": [
                {
                    "id": n.id,
                    "type": n.type,
                    "priority": n.priority,
                    "description": n.description
                } for n in needs
            ],
            "count": len(needs)
        }, ensure_ascii=False, indent=2))
    elif args.command == "trigger":
        result = engine.trigger_evolution()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "verify" and args.round:
        result = engine.verify_evolution(args.round)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "start":
        result = engine.start_autonomous_loop()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "stop":
        result = engine.stop_autonomous_loop()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "level" and args.level:
        result = engine.set_autonomous_level(args.level)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "cycle":
        result = engine.run_autonomous_cycle()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 默认显示状态
        print(json.dumps(engine.get_status(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()