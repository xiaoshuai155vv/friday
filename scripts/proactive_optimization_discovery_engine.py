#!/usr/bin/env python3
"""
智能主动优化发现引擎 (Proactive Optimization Discovery Engine)
让系统能够主动分析当前状态、识别可优化点、生成改进建议，实现从被动响应到主动优化的范式升级

version: 1.0.0
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# 项目根目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

class ProactiveOptimizationDiscoveryEngine:
    """智能主动优化发现引擎"""

    def __init__(self):
        self.name = "ProactiveOptimizationDiscoveryEngine"
        self.version = "1.0.0"
        self.state_file = os.path.join(PROJECT_ROOT, "runtime", "state", "current_mission.json")
        self.history_dir = os.path.join(PROJECT_ROOT, "runtime", "state")
        self.engines_dir = os.path.join(PROJECT_ROOT, "scripts")

    def _load_state(self):
        """加载当前状态"""
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            return {"phase": "unknown", "loop_round": 0}

    def _load_recent_logs(self):
        """加载近期日志"""
        logs_file = os.path.join(PROJECT_ROOT, "runtime", "state", "recent_logs.json")
        try:
            with open(logs_file, 'r', encoding='utf-8') as f:
                return json.load(f).get("entries", [])
        except Exception:
            return []

    def _load_evolution_history(self):
        """加载进化历史"""
        history_file = os.path.join(PROJECT_ROOT, "references", "evolution_auto_last.md")
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return ""

    def analyze_system_status(self):
        """分析系统当前状态"""
        print(f"[{self.name}] 分析系统当前状态...")

        state = self._load_state()
        logs = self._load_recent_logs()
        evolution_history = self._load_evolution_history()

        # 分析当前进化阶段
        current_round = state.get("loop_round", 0)
        current_phase = state.get("phase", "unknown")

        # 分析近期活动
        recent_activities = logs[-10:] if logs else []

        # 统计引擎数量
        engines_count = 0
        try:
            for f in os.listdir(self.engines_dir):
                if f.endswith('.py') and not f.startswith('_'):
                    engines_count += 1
        except Exception:
            pass

        status = {
            "current_round": current_round,
            "current_phase": current_phase,
            "engines_count": engines_count,
            "recent_activities_count": len(recent_activities),
            "evolution_history": evolution_history[:500] if evolution_history else ""
        }

        return status

    def identify_optimization_opportunities(self):
        """识别优化机会"""
        print(f"[{self.name}] 识别优化机会...")

        status = self.analyze_system_status()
        opportunities = []

        # 检查1：进化效率分析
        logs = self._load_recent_logs()
        if len(logs) >= 10:
            verify_fail_count = sum(1 for e in logs[-10:] if e.get("phase") == "verify" and e.get("result") == "fail")
            if verify_fail_count > 0:
                opportunities.append({
                    "type": "进化效率",
                    "description": f"近10轮中有{verify_fail_count}轮校验失败",
                    "priority": "high",
                    "suggestion": "分析失败原因，优化执行流程"
                })

        # 检查2：引擎协同分析
        engines_count = status.get("engines_count", 0)
        if engines_count > 200:
            opportunities.append({
                "type": "引擎协同",
                "description": f"系统拥有{engines_count}个引擎，存在协同优化空间",
                "priority": "medium",
                "suggestion": "优化引擎组合选择策略，提升协同效率"
            })

        # 检查3：自动化程度分析
        recent_logs = logs[-20:] if logs else []
        auto_execution_count = sum(1 for e in recent_logs if "自动化" in e.get("desc", "") or "自动" in e.get("desc", ""))
        if auto_execution_count < 5:
            opportunities.append({
                "type": "自动化程度",
                "description": "近期自动化执行较少，可增强自动化能力",
                "priority": "medium",
                "suggestion": "增强自动执行引擎能力，减少人工干预"
            })

        # 检查4：自学习能力分析
        has_learning = False
        for f in os.listdir(self.engines_dir):
            if "learning" in f.lower() or "adaptive" in f.lower():
                has_learning = True
                break

        if not has_learning:
            opportunities.append({
                "type": "自学习能力",
                "description": "缺乏自学习引擎，可增强学习能力",
                "priority": "medium",
                "suggestion": "增加自适应学习引擎，从执行历史中学习"
            })

        # 检查5：元进化能力分析
        has_meta_evolution = False
        for f in os.listdir(self.engines_dir):
            if "meta" in f.lower() and "evolution" in f.lower():
                has_meta_evolution = True
                break

        if not has_meta_evolution:
            opportunities.append({
                "type": "元进化能力",
                "description": "缺乏元进化引擎，可增强进化环本身的能力",
                "priority": "low",
                "suggestion": "增加元进化引擎，优化进化策略"
            })

        return opportunities

    def generate_optimization_suggestions(self):
        """生成优化建议"""
        print(f"[{self.name}] 生成优化建议...")

        opportunities = self.identify_optimization_opportunities()

        suggestions = []
        for i, opp in enumerate(opportunities, 1):
            suggestions.append(f"{i}. [{opp['type']}] {opp['description']}")
            suggestions.append(f"   优先级: {opp['priority']}")
            suggestions.append(f"   建议: {opp['suggestion']}")
            suggestions.append("")

        if not suggestions:
            suggestions.append("当前系统状态良好，未发现明显优化机会。")
            suggestions.append("可考虑：")
            suggestions.append("  1. 探索新能力组合，发现创新用法")
            suggestions.append("  2. 优化现有引擎性能")
            suggestions.append("  3. 增强用户体验")

        return "\n".join(suggestions)

    def discover_optimization(self):
        """执行完整的优化发现流程"""
        print(f"[{self.name}] 执行完整优化发现流程...")
        print("=" * 60)

        # 1. 分析系统状态
        print("\n【系统状态分析】")
        status = self.analyze_system_status()
        print(f"  当前轮次: {status['current_round']}")
        print(f"  当前阶段: {status['current_phase']}")
        print(f"  引擎数量: {status['engines_count']}")
        print(f"  近期活动: {status['recent_activities_count']}条")

        # 2. 识别优化机会
        print("\n【优化机会识别】")
        opportunities = self.identify_optimization_opportunities()
        if opportunities:
            for opp in opportunities:
                print(f"  - [{opp['priority'].upper()}] {opp['type']}: {opp['description']}")
        else:
            print("  未发现明显优化机会")

        # 3. 生成优化建议
        print("\n【优化建议】")
        suggestions = self.generate_optimization_suggestions()
        print(suggestions)

        print("\n" + "=" * 60)
        print(f"[{self.name}] 优化发现完成")

        return {
            "status": status,
            "opportunities": opportunities,
            "suggestions": suggestions
        }

    def status(self):
        """查看引擎状态"""
        status = self.analyze_system_status()
        print(f"\n=== {self.name} v{self.version} 状态 ===")
        print(f"当前轮次: {status['current_round']}")
        print(f"当前阶段: {status['current_phase']}")
        print(f"引擎数量: {status['engines_count']}")
        print(f"近期活动: {status['recent_activities_count']}条")
        return status


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="智能主动优化发现引擎")
    parser.add_argument("command", nargs="?", default="discover",
                        choices=["discover", "analyze", "identify", "suggestions", "status"],
                        help="要执行的命令")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    args = parser.parse_args()

    engine = ProactiveOptimizationDiscoveryEngine()

    if args.command == "discover" or args.command == "analyze":
        engine.discover_optimization()
    elif args.command == "identify":
        opportunities = engine.identify_optimization_opportunities()
        print("\n=== 优化机会 ===")
        for opp in opportunities:
            print(f"  [{opp['priority'].upper()}] {opp['type']}: {opp['description']}")
    elif args.command == "suggestions":
        suggestions = engine.generate_optimization_suggestions()
        print(suggestions)
    elif args.command == "status":
        engine.status()


if __name__ == "__main__":
    main()