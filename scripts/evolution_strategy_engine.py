#!/usr/bin/env python3
"""
进化策略引擎 - 智能分析进化方向与优先级

功能：
1. 分析历史进化数据、系统状态和用户行为
2. 根据分析结果自动推荐进化方向和优先级
3. 输出进化策略建议到 runtime/state/evolution_strategy.json

使用方法：
    python evolution_strategy_engine.py analyze
    python evolution_strategy_engine.py recommend
    python evolution_strategy_engine.py status
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE = PROJECT_ROOT / "runtime" / "state"
RUNTIME_LOGS = PROJECT_ROOT / "runtime" / "logs"
REFERENCES = PROJECT_ROOT / "references"


class EvolutionStrategyEngine:
    """进化策略引擎"""

    def __init__(self):
        self.state_dir = RUNTIME_STATE
        self.logs_dir = RUNTIME_LOGS
        self.references_dir = REFERENCES

        # 确保目录存在
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # 进化策略输出路径
        self.strategy_file = self.state_dir / "evolution_strategy.json"
        self.strategy_history_file = self.state_dir / "evolution_strategy_history.json"

    def analyze(self) -> Dict[str, Any]:
        """分析历史进化数据和系统状态"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "round_analysis": self._analyze_rounds(),
            "capability_analysis": self._analyze_capabilities(),
            "failure_analysis": self._analyze_failures(),
            "trend_analysis": self._analyze_trends(),
            "recommendations": []
        }

        # 生成推荐
        analysis["recommendations"] = self._generate_recommendations(analysis)

        return analysis

    def _analyze_rounds(self) -> Dict[str, Any]:
        """分析历史进化轮次"""
        rounds = []
        evolution_last = self.references_dir / "evolution_auto_last.md"

        if evolution_last.exists():
            content = evolution_last.read_text(encoding="utf-8")

            # 提取 round 信息
            import re
            round_pattern = r"## (\d{4}-\d{2}-\d{2}) round (\d+)"
            matches = re.findall(round_pattern, content)

            for date_str, round_num in matches[-10:]:  # 最近10轮
                rounds.append({
                    "date": date_str,
                    "round": int(round_num)
                })

        return {
            "total_rounds": len(rounds),
            "recent_rounds": rounds[-5:] if rounds else []
        }

    def _analyze_capabilities(self) -> Dict[str, Any]:
        """分析当前能力"""
        caps_file = self.references_dir / "capability_gaps.md"

        if caps_file.exists():
            content = caps_file.read_text(encoding="utf-8")

            # 统计已覆盖的能力
            covered = content.count("已覆盖")
            gaps = content.count("—")

            return {
                "covered_count": covered,
                "gap_count": gaps,
                "status": "well_equipped" if covered > 15 else "needs_expansion"
            }

        return {"status": "unknown"}

    def _analyze_failures(self) -> Dict[str, Any]:
        """分析历史失败教训"""
        failures_file = self.references_dir / "failures.md"

        if failures_file.exists():
            content = failures_file.read_text(encoding="utf-8")

            # 统计失败条目
            failure_count = content.count("- 2026-")

            # 提取失败类型
            failure_types = []
            if "vision" in content:
                failure_types.append("vision")
            if "窗口" in content or "激活" in content:
                failure_types.append("window_activation")
            if "剪贴板" in content:
                failure_types.append("clipboard")
            if "坐标" in content:
                failure_types.append("coordinate")

            return {
                "total_failures": failure_count,
                "failure_types": list(set(failure_types)),
                "status": "high_failure_rate" if failure_count > 10 else "manageable"
            }

        return {"status": "no_failures"}

    def _analyze_trends(self) -> Dict[str, Any]:
        """分析进化趋势"""
        # 读取最近的行为日志
        recent_logs = []

        if self.logs_dir.exists():
            log_files = sorted(self.logs_dir.glob("behavior_*.log"))
            if log_files:
                recent_file = log_files[-1]
                content = recent_file.read_text(encoding="utf-8", errors="ignore")
                lines = content.split("\n")[-50:]  # 最近50行

                for line in lines:
                    if "track" in line or "verify" in line:
                        recent_logs.append(line.strip())

        return {
            "recent_activities": len(recent_logs),
            "activity_trend": "active" if len(recent_logs) > 20 else "slow"
        }

    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """根据分析生成推荐"""
        recommendations = []

        # 基于能力分析推荐
        if analysis["capability_analysis"].get("status") == "needs_expansion":
            recommendations.append({
                "priority": "high",
                "category": "capability",
                "title": "扩展能力覆盖",
                "description": "系统能力覆盖仍有缺口，建议继续扩展新的智能模块"
            })

        # 基于失败分析推荐
        if analysis["failure_analysis"].get("status") == "high_failure_rate":
            recommendations.append({
                "priority": "high",
                "category": "stability",
                "title": "增强系统稳定性",
                "description": "历史失败教训较多，建议加强错误处理和恢复机制"
            })

        # 基于趋势分析推荐
        if analysis["trend_analysis"].get("activity_trend") == "active":
            recommendations.append({
                "priority": "medium",
                "category": "optimization",
                "title": "优化现有模块",
                "description": "系统活跃度高，建议对现有模块进行优化整合"
            })

        # 元进化推荐
        recommendations.append({
            "priority": "medium",
            "category": "meta_evolution",
            "title": "改进进化环本身",
            "description": "设计更智能的进化策略引擎，让系统能够自动调整进化方向"
        })

        return recommendations

    def get_strategy(self) -> Dict[str, Any]:
        """获取当前进化策略"""
        if self.strategy_file.exists():
            with open(self.strategy_file, "r", encoding="utf-8") as f:
                return json.load(f)

        return {
            "status": "no_strategy",
            "message": "请先运行 analyze 命令生成进化策略"
        }

    def save_strategy(self, strategy: Dict[str, Any]) -> None:
        """保存进化策略"""
        with open(self.strategy_file, "w", encoding="utf-8") as f:
            json.dump(strategy, f, ensure_ascii=False, indent=2)

        # 同时保存到历史
        self._append_to_history(strategy)

    def _append_to_history(self, strategy: Dict[str, Any]) -> None:
        """追加到策略历史"""
        history = []

        if self.strategy_history_file.exists():
            with open(self.strategy_history_file, "r", encoding="utf-8") as f:
                history = json.load(f)

        # 添加当前策略
        history.append({
            "timestamp": strategy.get("timestamp"),
            "recommendations_count": len(strategy.get("recommendations", []))
        })

        # 保留最近20条
        history = history[-20:]

        with open(self.strategy_history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def recommend(self) -> Dict[str, Any]:
        """获取推荐"""
        strategy = self.analyze()
        return {
            "recommendations": strategy.get("recommendations", []),
            "priority_focus": self._get_priority_focus(strategy)
        }

    def _get_priority_focus(self, strategy: Dict[str, Any]) -> str:
        """获取优先级焦点"""
        recommendations = strategy.get("recommendations", [])

        # 按优先级排序
        priority_order = {"high": 0, "medium": 1, "low": 2}
        sorted_recs = sorted(recommendations,
                           key=lambda x: priority_order.get(x.get("priority", "low"), 2))

        if sorted_recs:
            return sorted_recs[0].get("title", "unknown")

        return "no_focus"

    def status(self) -> Dict[str, Any]:
        """获取进化策略状态"""
        strategy = self.get_strategy()

        return {
            "status": "active" if strategy.get("status") != "no_strategy" else "inactive",
            "current_strategy": strategy,
            "last_updated": strategy.get("timestamp", "never")
        }


def main():
    """主函数"""
    engine = EvolutionStrategyEngine()

    if len(sys.argv) < 2:
        print("进化策略引擎")
        print("用法:")
        print("  python evolution_strategy_engine.py analyze   - 分析并生成策略")
        print("  python evolution_strategy_engine.py recommend  - 获取推荐")
        print("  python evolution_strategy_engine.py status     - 查看状态")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "analyze":
        result = engine.analyze()
        engine.save_strategy(result)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "recommend":
        result = engine.recommend()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "status":
        result = engine.status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()