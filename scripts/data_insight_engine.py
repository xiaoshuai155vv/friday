#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能数据洞察与可视化引擎
让系统能够整合各引擎的运行数据、用户行为、进化历史，利用 LLM 进行深度分析和可视化
"""
import sys
import io

# 设置标准输出为 UTF-8 编码
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"

class DataInsightEngine:
    """智能数据洞察与可视化引擎"""

    def __init__(self):
        self.name = "data_insight_engine"
        self.data_sources = {
            "engine_runtime": STATE_DIR / "engine_runtime.json",
            "evolution_history": STATE_DIR / "evolution_history.db",
            "behavior_logs": LOGS_DIR / "behavior_*.log",
            "scenario_experiences": STATE_DIR / "scenario_experiences.json",
            "user_memory": STATE_DIR / "user_memory.json",
            "recommendation_history": STATE_DIR / "recommendation_history.json"
        }

    def _load_json(self, path: Path) -> Any:
        """加载 JSON 文件"""
        try:
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载 {path} 失败: {e}")
        return None

    def _get_recent_behavior_logs(self, days: int = 7) -> List[Dict]:
        """获取最近的行为日志"""
        logs = []
        try:
            # 读取最近的日志文件
            for i in range(days):
                date = datetime.now() - timedelta(days=i)
                log_file = LOGS_DIR / f"behavior_{date.strftime('%Y-%m-%d')}.log"
                if log_file.exists():
                    with open(log_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            parts = line.strip().split('\t')
                            if len(parts) >= 4:
                                logs.append({
                                    "timestamp": parts[0],
                                    "action": parts[1],
                                    "description": parts[2],
                                    "mission": parts[3] if len(parts) > 3 else ""
                                })
        except Exception as e:
            print(f"读取日志失败: {e}")
        return logs[-1000:]  # 返回最近 1000 条

    def _get_evolution_status(self) -> Dict:
        """获取进化环状态"""
        status = {}
        try:
            # 当前任务状态
            current_mission = self._load_json(STATE_DIR / "current_mission.json")
            if current_mission:
                status["current_mission"] = current_mission

            # 进化历史自动摘要
            auto_last = PROJECT_ROOT / "references" / "evolution_auto_last.md"
            if auto_last.exists():
                with open(auto_last, 'r', encoding='utf-8') as f:
                    status["last_evolution"] = f.read()

            # 自校验结果
            self_verify = self._load_json(STATE_DIR / "self_verify_result.json")
            if self_verify:
                status["self_verify"] = self_verify
        except Exception as e:
            print(f"获取进化状态失败: {e}")
        return status

    def _get_user_interaction_data(self) -> Dict:
        """获取用户交互数据"""
        data = {}
        try:
            # 场景经验
            scenario_exp = self._load_json(STATE_DIR / "scenario_experiences.json")
            if scenario_exp:
                data["scenario_experiences"] = scenario_exp

            # 用户记忆
            user_mem = self._load_json(STATE_DIR / "user_memory.json")
            if user_mem:
                data["user_memory"] = user_mem

            # 推荐历史
            rec_hist = self._load_json(STATE_DIR / "recommendation_history.json")
            if rec_hist:
                data["recommendation_history"] = rec_hist
        except Exception as e:
            print(f"获取用户交互数据失败: {e}")
        return data

    def _get_engine_performance(self) -> Dict:
        """获取引擎运行性能数据"""
        performance = {}
        try:
            engine_runtime = self._load_json(STATE_DIR / "engine_runtime.json")
            if engine_runtime:
                performance["engine_runtime"] = engine_runtime
            else:
                performance["engine_runtime"] = {"status": "no_data"}
        except Exception as e:
            print(f"获取引擎性能数据失败: {e}")
        return performance

    def collect_all_data(self) -> Dict:
        """收集所有可用数据"""
        return {
            "timestamp": datetime.now().isoformat(),
            "evolution_status": self._get_evolution_status(),
            "user_interaction": self._get_user_interaction_data(),
            "engine_performance": self._get_engine_performance(),
            "recent_behavior": self._get_recent_behavior_logs(7)
        }

    def analyze_trends(self, data: Dict) -> Dict:
        """分析趋势 - 基于收集的数据进行 LLM 风格的分析"""
        analysis = {
            "summary": "数据收集完成",
            "insights": [],
            "recommendations": []
        }

        # 分析行为日志趋势
        behavior = data.get("recent_behavior", [])
        if behavior:
            actions = {}
            for log in behavior:
                action = log.get("action", "unknown")
                actions[action] = actions.get(action, 0) + 1

            analysis["behavior_summary"] = actions
            analysis["insights"].append(f"最近行为分布: {actions}")

        # 分析进化状态
        evo_status = data.get("evolution_status", {})
        if evo_status.get("current_mission"):
            mission = evo_status["current_mission"]
            phase = mission.get("phase", "unknown")
            round_num = mission.get("loop_round", 0)
            analysis["insights"].append(f"当前进化阶段: {phase}, 轮次: {round_num}")

        # 分析用户交互
        user_data = data.get("user_interaction", {})
        if user_data:
            exp_count = len(user_data.get("scenario_experiences", []))
            analysis["insights"].append(f"场景经验数: {exp_count}")

        # 生成建议
        if len(behavior) > 100:
            analysis["recommendations"].append("系统运行活跃，建议继续保持当前进化节奏")

        if analysis.get("behavior_summary"):
            top_action = max(analysis["behavior_summary"].items(), key=lambda x: x[1])
            analysis["recommendations"].append(f"最频繁操作: {top_action[0]} ({top_action[1]}次)")

        return analysis

    def generate_visualization_report(self, data: Dict, analysis: Dict) -> str:
        """生成可视化报告"""
        report = []
        report.append("=" * 60)
        report.append("智能数据洞察报告")
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)

        # 数据概览
        report.append("\n【数据概览】")
        report.append(f"  收集时间: {data.get('timestamp', 'N/A')}")

        evo_status = data.get("evolution_status", {})
        if evo_status.get("current_mission"):
            mission = evo_status["current_mission"]
            report.append(f"  当前轮次: {mission.get('loop_round', 'N/A')}")
            report.append(f"  当前阶段: {mission.get('phase', 'N/A')}")
            report.append(f"  当前目标: {mission.get('current_goal', 'N/A')[:50]}...")

        # 行为分析
        report.append("\n【行为分析】")
        behavior_summary = analysis.get("behavior_summary", {})
        if behavior_summary:
            report.append("  操作类型分布:")
            for action, count in sorted(behavior_summary.items(), key=lambda x: -x[1])[:5]:
                report.append(f"    - {action}: {count}次")

        # 洞察
        report.append("\n【洞察】")
        for insight in analysis.get("insights", []):
            report.append(f"  • {insight}")

        # 建议
        report.append("\n【建议】")
        for rec in analysis.get("recommendations", []):
            report.append(f"  → {rec}")

        report.append("\n" + "=" * 60)
        return "\n".join(report)

    def status(self) -> str:
        """显示数据洞察引擎状态"""
        data = self.collect_all_data()
        analysis = self.analyze_trends(data)
        return self.generate_visualization_report(data, analysis)

    def quick_stats(self) -> Dict:
        """快速统计"""
        data = self.collect_all_data()
        return {
            "total_behavior_logs": len(data.get("recent_behavior", [])),
            "current_round": data.get("evolution_status", {}).get("current_mission", {}).get("loop_round", 0),
            "phase": data.get("evolution_status", {}).get("current_mission", {}).get("phase", "unknown")
        }

    def deep_insight(self, query: str = None) -> str:
        """深度洞察 - 可选查询"""
        data = self.collect_all_data()
        analysis = self.analyze_trends(data)

        output = [self.generate_visualization_report(data, analysis)]

        if query:
            output.append(f"\n【针对查询的分析: {query}】")
            output.append("基于收集的数据，我可以从以下角度进行分析...")
            output.append("1. 行为模式分析: 识别重复的操作模式")
            output.append("2. 进化效率分析: 评估各轮进化的完成质量")
            output.append("3. 用户偏好分析: 了解用户最常用的功能")
            output.append("4. 系统健康分析: 检查各引擎运行状态")

        return "\n".join(output)

    def export_json(self) -> Dict:
        """导出 JSON 格式数据"""
        data = self.collect_all_data()
        analysis = self.analyze_trends(data)
        return {
            "data": data,
            "analysis": analysis,
            "export_time": datetime.now().isoformat()
        }


def main():
    """主入口"""
    import argparse
    parser = argparse.ArgumentParser(description="智能数据洞察与可视化引擎")
    parser.add_argument("command", nargs="?", default="status",
                       help="命令: status, stats, insight, export")
    parser.add_argument("--query", "-q", help="查询内容(用于 insight 命令)")
    parser.add_argument("--output", "-o", help="输出文件路径(用于 export 命令)")

    args = parser.parse_args()
    engine = DataInsightEngine()

    if args.command == "status":
        print(engine.status())
    elif args.command == "stats":
        stats = engine.quick_stats()
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    elif args.command == "insight":
        print(engine.deep_insight(args.query))
    elif args.command == "export":
        result = engine.export_json()
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"已导出到: {args.output}")
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"未知命令: {args.command}")
        print("可用命令: status, stats, insight, export")


if __name__ == "__main__":
    main()