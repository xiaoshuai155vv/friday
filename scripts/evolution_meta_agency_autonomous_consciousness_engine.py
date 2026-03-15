#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环元进化智能体自主意识深度增强引擎

让系统能够在已有元进化能力基础上，实现更深层次的自主意识：
1. 主动评估自身状态（能力完整性、进化效率、健康状态）
2. 识别进化价值（哪些方向最有价值）
3. 自主决定进化方向（从被动优化到主动追求价值）

Version: 1.0.0
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 项目根目录
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"


class MetaAgencyAutonomousConsciousnessEngine:
    """元进化智能体自主意识深度增强引擎"""

    def __init__(self):
        self.name = "元进化智能体自主意识深度增强引擎"
        self.version = "1.0.0"
        self.state_dir = STATE_DIR
        self.logs_dir = LOGS_DIR

    def get_system_self_assessment(self):
        """
        获取系统自我评估数据
        分析：当前系统能力完整性、进化效率、健康状态
        """
        assessment = {
            "timestamp": datetime.now().isoformat(),
            "evolution_round": 0,
            "capability_completeness": 0.0,
            "evolution_efficiency": 0.0,
            "health_status": "unknown",
            "self_awareness_level": "shallow",
            "autonomous_decision_ability": 0.0
        }

        try:
            # 读取当前进化轮次
            mission_file = self.state_dir / "current_mission.json"
            if mission_file.exists():
                with open(mission_file, "r", encoding="utf-8") as f:
                    mission = json.load(f)
                    assessment["evolution_round"] = mission.get("loop_round", 0)

            # 读取进化完成状态统计
            completed_files = list(self.state_dir.glob("evolution_completed_*.json"))
            completed_count = len(completed_files)
            if completed_count > 0:
                assessment["capability_completeness"] = min(1.0, completed_count / 600.0)

            # 分析进化效率（基于历史数据）
            efficiency = self._analyze_evolution_efficiency()
            assessment["evolution_efficiency"] = efficiency

            # 检查系统健康状态
            health = self._check_system_health()
            assessment["health_status"] = health

            # 评估自主决策能力深度
            decision_ability = self._assess_autonomous_decision_ability()
            assessment["autonomous_decision_ability"] = decision_ability

            # 自我意识水平评估
            if decision_ability > 0.8 and efficiency > 0.8:
                assessment["self_awareness_level"] = "deep"
            elif decision_ability > 0.5 or efficiency > 0.5:
                assessment["self_awareness_level"] = "moderate"
            else:
                assessment["self_awareness_level"] = "shallow"

        except Exception as e:
            print(f"[ERROR] 获取系统自我评估失败: {e}")

        return assessment

    def _analyze_evolution_efficiency(self):
        """分析进化效率"""
        efficiency = 0.5  # 默认中等效率

        try:
            # 统计已完成进化轮数
            completed_files = list(self.state_dir.glob("evolution_completed_*.json"))
            completed_count = len(completed_files)

            # 基于完成率计算效率
            if completed_count > 0:
                # 假设高效进化应该保持较高完成率
                efficiency = min(1.0, completed_count / 500.0)

                # 检查是否有失败记录
                for f in completed_files:
                    try:
                        with open(f, "r", encoding="utf-8") as fp:
                            data = json.load(fp)
                            if data.get("status") == "stale_failed":
                                efficiency *= 0.9  # 失败降低效率
                    except:
                        pass
        except:
            pass

        return efficiency

    def _check_system_health(self):
        """检查系统健康状态"""
        health = "healthy"

        try:
            # 检查关键目录是否存在
            required_dirs = [self.state_dir, self.logs_dir]
            for d in required_dirs:
                if not d.exists():
                    return "critical"

            # 检查日志文件是否有最近的活动
            log_files = list(self.logs_dir.glob("behavior_*.log"))
            if log_files:
                # 检查最新日志的时间
                latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
                time_diff = datetime.now().timestamp() - latest_log.stat().st_mtime
                if time_diff > 3600 * 24:  # 24小时无活动
                    health = "inactive"
        except:
            health = "unknown"

        return health

    def _assess_autonomous_decision_ability(self):
        """评估自主决策能力"""
        ability = 0.0

        try:
            # 检查是否有决策引擎
            decision_engines = [
                "evolution_meta_decision_auto_execution_engine.py",
                "evolution_value_driven_meta_evolution_adaptive_decision_engine.py",
                "evolution_meta_strategy_autonomous_generation_engine.py",
                "evolution_meta_efficiency_adaptive_continual_optimizer.py"
            ]

            scripts_dir = PROJECT_ROOT / "scripts"
            found_engines = 0
            for engine in decision_engines:
                if (scripts_dir / engine).exists():
                    found_engines += 1

            ability = found_engines / len(decision_engines)
        except:
            pass

        return ability

    def identify_valuable_evolution_directions(self):
        """
        识别有价值的进化方向
        基于系统当前状态和进化历史，识别最有价值的进化机会
        """
        directions = []

        try:
            # 获取自我评估
            assessment = self.get_system_self_assessment()

            # 基于评估结果识别方向
            if assessment["capability_completeness"] < 0.8:
                directions.append({
                    "direction": "增强能力覆盖",
                    "value": 0.8 - assessment["capability_completeness"],
                    "description": "系统能力覆盖尚未饱和，仍有提升空间"
                })

            if assessment["evolution_efficiency"] < 0.7:
                directions.append({
                    "direction": "提升进化效率",
                    "value": 0.7 - assessment["evolution_efficiency"],
                    "description": "优化进化方法论，提高执行效率"
                })

            if assessment["autonomous_decision_ability"] < 0.8:
                directions.append({
                    "direction": "增强自主决策",
                    "value": 0.8 - assessment["autonomous_decision_ability"],
                    "description": "深化自主决策能力，减少人工干预"
                })

            if assessment["self_awareness_level"] == "shallow":
                directions.append({
                    "direction": "深化自我意识",
                    "value": 0.5,
                    "description": "增强系统自我认知和反思能力"
                })

            # 总是添加创新方向
            directions.append({
                "direction": "探索创新方向",
                "value": 0.3,
                "description": "发现人类未想到但有价值的创新机会"
            })

            # 按价值排序
            directions.sort(key=lambda x: x["value"], reverse=True)

        except Exception as e:
            print(f"[ERROR] 识别进化方向失败: {e}")

        return directions

    def generate_autonomous_evolution_decision(self):
        """
        生成自主进化决策
        基于价值分析自主选择最优进化方向
        """
        decision = {
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
            "selected_direction": None,
            "reasoning": "",
            "confidence": 0.0
        }

        try:
            # 获取有价值的进化方向
            directions = self.identify_valuable_evolution_directions()

            if not directions:
                decision["reasoning"] = "当前系统状态良好，无明确优化方向"
                decision["selected_direction"] = "保持现状"
                decision["confidence"] = 0.5
            else:
                # 选择价值最高的方向
                best_direction = directions[0]
                decision["selected_direction"] = best_direction["direction"]
                decision["reasoning"] = best_direction["description"]
                decision["confidence"] = min(1.0, best_direction["value"])

            decision["status"] = "completed"
            decision["all_directions"] = directions

        except Exception as e:
            print(f"[ERROR] 生成自主决策失败: {e}")
            decision["reasoning"] = f"决策生成失败: {e}"

        return decision

    def get_cockpit_data(self):
        """获取驾驶舱数据"""
        assessment = self.get_system_self_assessment()
        directions = self.identify_valuable_evolution_directions()
        decision = self.generate_autonomous_evolution_decision()

        return {
            "engine_name": self.name,
            "engine_version": self.version,
            "timestamp": datetime.now().isoformat(),
            "self_assessment": assessment,
            "valuable_directions": directions[:5],  # 前5个方向
            "autonomous_decision": decision,
            "description": "元进化智能体自主意识深度增强引擎 - 实现主动评估自身状态、识别进化价值、自主决定进化方向"
        }

    def run_full_cycle(self):
        """运行完整自主意识循环"""
        print("=== 元进化智能体自主意识深度增强引擎 ===")
        print(f"版本: {self.version}")
        print()

        # 1. 自我评估
        print("[1] 系统自我评估...")
        assessment = self.get_system_self_assessment()
        print(f"  - 进化轮次: {assessment['evolution_round']}")
        print(f"  - 能力完整度: {assessment['capability_completeness']:.2%}")
        print(f"  - 进化效率: {assessment['evolution_efficiency']:.2%}")
        print(f"  - 健康状态: {assessment['health_status']}")
        print(f"  - 自我意识水平: {assessment['self_awareness_level']}")
        print(f"  - 自主决策能力: {assessment['autonomous_decision_ability']:.2%}")
        print()

        # 2. 识别价值方向
        print("[2] 识别有价值的进化方向...")
        directions = self.identify_valuable_evolution_directions()
        for i, d in enumerate(directions[:5], 1):
            print(f"  {i}. {d['direction']} (价值: {d['value']:.2f})")
            print(f"     {d['description']}")
        print()

        # 3. 自主决策
        print("[3] 生成自主进化决策...")
        decision = self.generate_autonomous_evolution_decision()
        print(f"  - 选中方向: {decision['selected_direction']}")
        print(f"  - 置信度: {decision['confidence']:.2%}")
        print(f"  - 推理: {decision['reasoning']}")
        print()

        return {
            "assessment": assessment,
            "directions": directions,
            "decision": decision
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="元进化智能体自主意识深度增强引擎"
    )
    parser.add_argument("--version", action="store_true", help="显示版本")
    parser.add_argument("--status", action="store_true", help="显示引擎状态")
    parser.add_argument("--run", action="store_true", help="运行完整自主意识循环")
    parser.add_argument("--assess", action="store_true", help="执行系统自我评估")
    parser.add_argument("--directions", action="store_true", help="识别有价值进化方向")
    parser.add_argument("--decision", action="store_true", help="生成自主进化决策")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")

    args = parser.parse_args()

    engine = MetaAgencyAutonomousConsciousnessEngine()

    if args.version:
        print(f"{engine.name} v{engine.version}")
        return

    if args.status:
        assessment = engine.get_system_self_assessment()
        print(json.dumps(assessment, indent=2, ensure_ascii=False))
        return

    if args.assess:
        assessment = engine.get_system_self_assessment()
        print(json.dumps(assessment, indent=2, ensure_ascii=False))
        return

    if args.directions:
        directions = engine.identify_valuable_evolution_directions()
        print(json.dumps(directions, indent=2, ensure_ascii=False))
        return

    if args.decision:
        decision = engine.generate_autonomous_evolution_decision()
        print(json.dumps(decision, indent=2, ensure_ascii=False))
        return

    if args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    if args.run:
        result = engine.run_full_cycle()
        return

    # 默认显示状态
    print(f"{engine.name} v{engine.version}")
    print("使用 --help 查看可用命令")


if __name__ == "__main__":
    main()