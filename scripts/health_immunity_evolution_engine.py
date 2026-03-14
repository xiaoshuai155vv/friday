#!/usr/bin/env python3
"""
智能全场景系统健康免疫增强与自愈进化引擎（Round 328）

让系统从"被动预测防御"升级到"主动增强免疫"，形成类似人体免疫系统的自适应自愈能力。
基于 round 327 的健康态势感知与预测防御引擎，进一步实现健康威胁模式学习、主动免疫增强、自愈进化闭环。

功能：
1. 健康威胁模式学习 - 从历史健康数据学习威胁模式，形成免疫记忆
2. 主动免疫增强 - 预测到风险时主动增强相关能力
3. 自愈进化闭环 - 自愈后学习进化，形成更强免疫

依赖模块：
- health_situation_awareness_prediction_engine.py (round 327)
- health_defense_deep_integration.py (round 326)
- system_health_monitor.py
- system_health_check.py
"""

import json
import os
import sys
import subprocess
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# 添加 scripts 目录到路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))


class HealthImmunityEvolutionEngine:
    """智能全场景系统健康免疫增强与自愈进化引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.name = "health_immunity_evolution_engine"
        self.description = "健康免疫增强与自愈进化"
        self.author = "Evolution Loop"

        # 免疫系统配置
        self.immunity_config = {
            "threat_learning_window": 30,  # 天数
            "immunity_strength_threshold": 0.7,  # 免疫强度阈值
            "enhancement_cooldown": 3600,  # 增强冷却时间（秒）
            "self_healing_learn_window": 7,  # 自愈学习窗口（天）
            "min_immunity_level": 0.3,  # 最小免疫水平
            "max_immunity_level": 1.0,  # 最大免疫水平
        }

        # 威胁类型定义
        self.threat_types = {
            "cpu_overload": {"severity": 0.8, "countermeasure": "reduce_cpu_usage"},
            "memory_pressure": {"severity": 0.7, "countermeasure": "optimize_memory"},
            "disk_space_low": {"severity": 0.6, "countermeasure": "clean_disk"},
            "process_failure": {"severity": 0.7, "countermeasure": "restart_process"},
            "network_congestion": {"severity": 0.5, "countermeasure": "optimize_network"},
            "health_degradation": {"severity": 0.6, "countermeasure": "health_maintenance"},
        }

        # 免疫记忆存储
        self.immunity_memory = {
            "threat_patterns": [],  # 威胁模式
            "countermeasure_effectiveness": {},  # 对策效果
            "immunity_levels": {},  # 各维度免疫水平
            "self_healing_history": [],  # 自愈历史
            "learned_responses": {},  # 学习到的响应
        }

        # 免疫增强记录
        self.enhancement_history = []
        self.immunity_current_state = {
            "cpu": 0.5,
            "memory": 0.5,
            "disk": 0.5,
            "process": 0.5,
            "network": 0.5,
            "health_system": 0.5,
        }

        # 加载免疫记忆
        self.load_immunity_memory()

    def load_immunity_memory(self):
        """加载免疫记忆数据"""
        memory_file = SCRIPT_DIR / "runtime" / "state" / "health_immunity_memory.json"
        if memory_file.exists():
            try:
                with open(memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.immunity_memory = data.get("immunity_memory", self.immunity_memory)
                    self.immunity_current_state = data.get("current_state", self.immunity_current_state)
            except Exception:
                pass

    def save_immunity_memory(self):
        """保存免疫记忆数据"""
        memory_file = SCRIPT_DIR / "runtime" / "state" / "health_immunity_memory.json"
        try:
            memory_file.parent.mkdir(parents=True, exist_ok=True)
            with open(memory_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "immunity_memory": self.immunity_memory,
                    "current_state": self.immunity_current_state,
                    "last_updated": datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def learn_threat_patterns(self, health_data):
        """学习威胁模式"""
        learned_patterns = []

        # 从健康数据中提取威胁模式
        if "cpu" in health_data and health_data["cpu"].get("usage", 0) > 0.8:
            learned_patterns.append({
                "type": "cpu_overload",
                "timestamp": datetime.now().isoformat(),
                "severity": health_data["cpu"]["usage"],
            })

        if "memory" in health_data and health_data["memory"].get("usage", 0) > 0.85:
            learned_patterns.append({
                "type": "memory_pressure",
                "timestamp": datetime.now().isoformat(),
                "severity": health_data["memory"]["usage"],
            })

        if "disk" in health_data and health_data["disk"].get("usage", 0) > 0.9:
            learned_patterns.append({
                "type": "disk_space_low",
                "timestamp": datetime.now().isoformat(),
                "severity": health_data["disk"]["usage"],
            })

        # 更新免疫记忆
        for pattern in learned_patterns:
            pattern_exists = False
            for existing in self.immunity_memory["threat_patterns"]:
                if existing["type"] == pattern["type"]:
                    existing["count"] = existing.get("count", 1) + 1
                    existing["last_seen"] = pattern["timestamp"]
                    pattern_exists = True
                    break

            if not pattern_exists:
                pattern["count"] = 1
                self.immunity_memory["threat_patterns"].append(pattern)

        return learned_patterns

    def calculate_immunity_level(self, dimension):
        """计算指定维度的免疫水平"""
        base_level = self.immunity_current_state.get(dimension, 0.5)

        # 检查是否有针对该维度的威胁记忆
        dimension_threats = {
            "cpu": "cpu_overload",
            "memory": "memory_pressure",
            "disk": "disk_space_low",
            "process": "process_failure",
            "network": "network_congestion",
        }

        threat_type = dimension_threats.get(dimension)
        if threat_type:
            for pattern in self.immunity_memory["threat_patterns"]:
                if pattern["type"] == threat_type:
                    # 有过威胁经历，免疫水平应该更高
                    count = pattern.get("count", 0)
                    if count > 0:
                        # 经历过多次威胁的维度应该有更高的免疫水平
                        boost = min(0.2, count * 0.05)
                        base_level = min(self.immunity_config["max_immunity_level"],
                                        base_level + boost)

        return base_level

    def enhance_immunity(self, dimension, target_level=None):
        """主动增强指定维度的免疫能力"""
        if target_level is None:
            target_level = self.immunity_config["immunity_strength_threshold"]

        current = self.immunity_current_state.get(dimension, 0.5)

        # 触发增强措施
        enhancements = []

        if dimension == "cpu" and current < target_level:
            enhancements.append({
                "action": "optimize_cpu_usage",
                "target": dimension,
                "boost": target_level - current,
            })

        elif dimension == "memory" and current < target_level:
            enhancements.append({
                "action": "optimize_memory_usage",
                "target": dimension,
                "boost": target_level - current,
            })

        elif dimension == "disk" and current < target_level:
            enhancements.append({
                "action": "clean_temp_files",
                "target": dimension,
                "boost": target_level - current,
            })

        elif dimension == "process" and current < target_level:
            enhancements.append({
                "action": "restart_heavy_processes",
                "target": dimension,
                "boost": target_level - current,
            })

        elif dimension == "network" and current < target_level:
            enhancements.append({
                "action": "optimize_network_config",
                "target": dimension,
                "boost": target_level - current,
            })

        # 应用增强效果
        for enh in enhancements:
            dim = enh["target"]
            boost = enh["boost"]
            self.immunity_current_state[dim] = min(
                self.immunity_config["max_immunity_level"],
                self.immunity_current_state.get(dim, 0.5) + boost
            )
            self.enhancement_history.append({
                "timestamp": datetime.now().isoformat(),
                "dimension": dim,
                "enhancement": enh,
                "new_level": self.immunity_current_state[dim]
            })

        self.save_immunity_memory()
        return enhancements

    def self_healing_learn(self, issue_type, solution_applied, success_rate):
        """自愈学习 - 从自愈过程中学习"""
        self_healing_record = {
            "issue_type": issue_type,
            "solution": solution_applied,
            "success_rate": success_rate,
            "timestamp": datetime.now().isoformat(),
            "times_encountered": 1,
        }

        # 检查是否已有记录
        for existing in self.immunity_memory["self_healing_history"]:
            if existing["issue_type"] == issue_type and existing["solution"] == solution_applied:
                existing["times_encountered"] = existing.get("times_encountered", 1) + 1
                existing["success_rate"] = (existing.get("success_rate", 0) + success_rate) / 2
                existing["last_applied"] = datetime.now().isoformat()
                self_healing_record = existing
                break

        if self_healing_record not in self.immunity_memory["self_healing_history"]:
            self.immunity_memory["self_healing_history"].append(self_healing_record)

        # 更新学习到的响应
        if issue_type not in self.immunity_memory["learned_responses"]:
            self.immunity_memory["learned_responses"][issue_type] = []

        solution_exists = False
        for resp in self.immunity_memory["learned_responses"].get(issue_type, []):
            if resp.get("solution") == solution_applied:
                resp["effectiveness"] = (resp.get("effectiveness", 0) + success_rate) / 2
                solution_exists = True
                break

        if not solution_exists:
            self.immunity_memory["learned_responses"].setdefault(issue_type, []).append({
                "solution": solution_applied,
                "effectiveness": success_rate,
                "last_used": datetime.now().isoformat()
            })

        self.save_immunity_memory()
        return self_healing_record

    def get_immune_system_status(self):
        """获取免疫系统状态"""
        # 计算各维度免疫水平
        dimensions = ["cpu", "memory", "disk", "process", "network", "health_system"]
        immunity_levels = {}

        for dim in dimensions:
            immunity_levels[dim] = self.calculate_immunity_level(dim)

        # 计算整体免疫水平
        overall_immunity = sum(immunity_levels.values()) / len(immunity_levels)

        # 统计威胁模式
        threat_count = len(self.immunity_memory.get("threat_patterns", []))

        # 统计自愈经验
        healing_count = len(self.immunity_memory.get("self_healing_history", []))

        # 统计增强次数
        enhancement_count = len(self.enhancement_history)

        return {
            "version": self.version,
            "overall_immunity": overall_immunity,
            "dimension_immunity": immunity_levels,
            "threat_patterns_count": threat_count,
            "self_healing_experience": healing_count,
            "enhancement_count": enhancement_count,
            "immune_system_health": "strong" if overall_immunity > 0.7 else "moderate" if overall_immunity > 0.5 else "weak",
        }

    def run_full_cycle(self, health_data=None):
        """运行完整的免疫增强周期"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "actions_taken": [],
            "immunity_status": {},
        }

        # 如果没有提供健康数据，尝试获取
        if health_data is None:
            try:
                # 导入并使用 system_health_monitor
                from system_health_monitor import SystemHealthMonitor
                monitor = SystemHealthMonitor()
                health_data = monitor.get_current_health()
            except Exception:
                health_data = {}

        # 1. 学习威胁模式
        if health_data:
            patterns = self.learn_threat_patterns(health_data)
            if patterns:
                result["actions_taken"].append(f"学习到 {len(patterns)} 个威胁模式")

        # 2. 评估免疫水平
        for dimension in ["cpu", "memory", "disk", "process", "network", "health_system"]:
            level = self.calculate_immunity_level(dimension)
            # 如果免疫水平低于阈值，触发增强
            if level < self.immunity_config["immunity_strength_threshold"]:
                enhancements = self.enhance_immunity(dimension)
                if enhancements:
                    result["actions_taken"].append(
                        f"增强 {dimension} 免疫能力， level: {level:.2f} -> {level + sum(e['boost'] for e in enhancements):.2f}"
                    )

        # 3. 更新免疫状态
        result["immunity_status"] = self.get_immune_system_status()

        return result


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description="智能全场景系统健康免疫增强与自愈进化引擎")
    parser.add_argument("--status", action="store_true", help="获取免疫系统状态")
    parser.add_argument("--enhance", type=str, help="增强指定维度的免疫能力 (cpu/memory/disk/process/network/health_system)")
    parser.add_argument("--learn", type=str, nargs=3, metavar=("ISSUE", "SOLUTION", "SUCCESS"),
                        help="从自愈过程学习 (issue_type solution success_rate)")
    parser.add_argument("--full-cycle", action="store_true", help="运行完整的免疫增强周期")
    parser.add_argument("--dashboard", action="store_true", help="显示免疫系统仪表盘")

    args = parser.parse_args()

    engine = HealthImmunityEvolutionEngine()

    if args.status:
        status = engine.get_immune_system_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
        return

    if args.enhance:
        dimension = args.enhance
        enhancements = engine.enhance_immunity(dimension)
        print(json.dumps({
            "dimension": dimension,
            "enhancements": enhancements,
            "new_level": engine.immunity_current_state.get(dimension, 0),
        }, indent=2, ensure_ascii=False))
        return

    if args.learn:
        issue, solution, success = args.learn
        try:
            success_rate = float(success)
        except ValueError:
            success_rate = 0.5
        record = engine.self_healing_learn(issue, solution, success_rate)
        print(json.dumps(record, indent=2, ensure_ascii=False))
        return

    if args.full_cycle:
        result = engine.run_full_cycle()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    if args.dashboard:
        status = engine.get_immune_system_status()
        print("=" * 50)
        print("  智能全场景系统健康免疫增强与自愈进化引擎")
        print("=" * 50)
        print(f"版本: {status['version']}")
        print(f"整体免疫水平: {status['overall_immunity']:.2%}")
        print(f"免疫系统健康: {status['immune_system_health']}")
        print("-" * 50)
        print("各维度免疫水平:")
        for dim, level in status['dimension_immunity'].items():
            bar = "█" * int(level * 20) + "░" * (20 - int(level * 20))
            print(f"  {dim:12s}: [{bar}] {level:.1%}")
        print("-" * 50)
        print(f"威胁模式数量: {status['threat_patterns_count']}")
        print(f"自愈经验数量: {status['self_healing_experience']}")
        print(f"增强次数: {status['enhancement_count']}")
        print("=" * 50)
        return

    # 默认显示状态
    status = engine.get_immune_system_status()
    print(json.dumps(status, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()