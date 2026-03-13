#!/usr/bin/env python3
"""
智能进化执行闭环增强引擎
用于自动追踪进化执行结果、生成进化报告、分析进化趋势，实现真正的自主进化管理

功能：
1. 自动追踪进化执行结果（创建模块、修改文件、状态变化）
2. 生成进化执行报告（执行效率、完成度、影响范围）
3. 分析进化趋势（轮次效率、模式识别、预测）
4. 集成到 do.py 支持相关关键词触发

使用方法：
    python evolution_execution_tracker.py track
    python evolution_execution_tracker.py report
    python evolution_execution_tracker.py trends
    python evolution_execution_tracker.py status
"""

import json
import os
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from collections import Counter, defaultdict

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE = PROJECT_ROOT / "runtime" / "state"
RUNTIME_LOGS = PROJECT_ROOT / "runtime" / "logs"
REFERENCES = PROJECT_ROOT / "references"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"


class EvolutionExecutionTracker:
    """进化执行追踪器 - 自动追踪进化执行结果和趋势"""

    def __init__(self):
        self.state_dir = RUNTIME_STATE
        self.logs_dir = RUNTIME_LOGS
        self.references_dir = REFERENCES
        self.scripts_dir = SCRIPTS_DIR

        # 追踪结果输出路径
        self.tracking_file = self.state_dir / "evolution_execution_tracking.json"
        self.report_file = self.state_dir / "evolution_execution_report.json"
        self.trends_file = self.state_dir / "evolution_execution_trends.json"

        # 确保目录存在
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def track(self) -> Dict[str, Any]:
        """追踪进化执行结果"""
        tracking = {
            "timestamp": datetime.now().isoformat(),
            "rounds_tracked": 0,
            "total_modules_created": 0,
            "total_files_modified": 0,
            "execution_summary": [],
            "status": "active"
        }

        # 收集所有进化完成文件
        completed_files = sorted(self.state_dir.glob("evolution_completed_*.json"))

        round_data = []
        for f in completed_files:
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    round_data.append(data)
            except Exception as e:
                print(f"Warning: Failed to read {f}: {e}")

        # 分析每轮执行
        all_modules = set()
        all_files = set()

        for rd in round_data:
            tracking["rounds_tracked"] += 1

            # 统计创建的模块
            if "impacted_files" in rd:
                for fp in rd["impacted_files"]:
                    all_files.add(fp)
                    if fp.startswith("scripts/") and not fp.endswith(".md"):
                        module_name = Path(fp).stem
                        all_modules.add(module_name)

            # 提取执行摘要 - 处理不同格式
            # 新格式: result is dict with status
            # 旧格式: "是否完成" is boolean
            if "result" in rd and isinstance(rd.get("result"), dict):
                status = rd.get("result", {}).get("status", "unknown")
                baseline_verify = rd.get("result", {}).get("baseline_verify", "N/A")
                targeted_verify = rd.get("result", {}).get("targeted_verify", "N/A")
            else:
                # 旧格式
                status = "completed" if rd.get("是否完成", False) else "incomplete"
                baseline_verify = rd.get("基线校验", "N/A")
                targeted_verify = rd.get("针对性校验", "N/A")

            # 获取目标
            goal = rd.get("current_goal")
            if not goal:
                assumed = rd.get("assumed_demands", [])
                goal = assumed[0] if assumed else "unknown"

            summary = {
                "round": rd.get("loop_round", "unknown"),
                "goal": goal,
                "status": status,
                "baseline_verify": baseline_verify,
                "targeted_verify": targeted_verify
            }
            tracking["execution_summary"].append(summary)

        tracking["total_modules_created"] = len(all_modules)
        tracking["total_files_modified"] = len(all_files)

        # 保存追踪结果
        with open(self.tracking_file, 'w', encoding='utf-8') as fp:
            json.dump(tracking, fp, ensure_ascii=False, indent=2)

        print(f"Tracking complete: {tracking['rounds_tracked']} rounds, {tracking['total_modules_created']} modules, {tracking['total_files_modified']} files")
        return tracking

    def report(self) -> Dict[str, Any]:
        """生成进化执行报告"""
        # 先追踪最新数据
        tracking = self.track()

        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_rounds": tracking["rounds_tracked"],
                "total_modules": tracking["total_modules_created"],
                "total_files": tracking["total_files_modified"],
                "execution_status": tracking["status"]
            },
            "rounds_detail": tracking["execution_summary"],
            "completion_rate": self._calculate_completion_rate(tracking),
            "performance_metrics": self._calculate_performance_metrics(tracking),
            "recommendations": self._generate_recommendations(tracking)
        }

        # 保存报告
        with open(self.report_file, 'w', encoding='utf-8') as fp:
            json.dump(report, fp, ensure_ascii=False, indent=2)

        # 打印报告摘要
        print("\n=== Evolution Execution Report ===")
        print(f"Total Rounds: {report['summary']['total_rounds']}")
        print(f"Total Modules Created: {report['summary']['total_modules']}")
        print(f"Total Files Modified: {report['summary']['total_files']}")
        print(f"Completion Rate: {report['completion_rate']}%")
        print(f"Performance Metrics: {report['performance_metrics']}")
        print(f"Recommendations: {report['recommendations']}")

        return report

    def trends(self) -> Dict[str, Any]:
        """分析进化趋势"""
        # 收集历史数据
        completed_files = sorted(self.state_dir.glob("evolution_completed_*.json"))

        trends = {
            "timestamp": datetime.now().isoformat(),
            "total_analyzed": len(completed_files),
            "rounds_by_month": defaultdict(int),
            "rounds_by_status": defaultdict(int),
            "modules_by_type": defaultdict(int),
            "avg_completion_time": 0,
            "trend_analysis": {}
        }

        # 分析每月轮次
        for f in completed_files:
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    completed_at = data.get("completed_at", "")
                    if completed_at:
                        month = completed_at[:7]  # YYYY-MM
                        trends["rounds_by_month"][month] += 1

                    # 统计状态 - 处理不同格式
                    if "result" in data and isinstance(data.get("result"), dict):
                        status = data.get("result", {}).get("status", "unknown")
                    else:
                        status = "completed" if data.get("是否完成", False) else "incomplete"
                    trends["rounds_by_status"][status] += 1

                    # 统计模块类型
                    if "impacted_files" in data:
                        for fp in data["impacted_files"]:
                            if fp.startswith("scripts/"):
                                module_type = Path(fp).stem
                                if "evolution" in module_type:
                                    trends["modules_by_type"]["evolution"] += 1
                                elif "service" in module_type:
                                    trends["modules_by_type"]["service"] += 1
                                elif "engine" in module_type:
                                    trends["modules_by_type"]["engine"] += 1
                                else:
                                    trends["modules_by_type"]["other"] += 1

            except Exception as e:
                print(f"Warning: Failed to analyze {f}: {e}")

        # 生成趋势分析
        trends["trend_analysis"] = {
            "monthly_distribution": dict(trends["rounds_by_month"]),
            "status_distribution": dict(trends["rounds_by_status"]),
            "module_type_distribution": dict(trends["modules_by_type"]),
            "growth_rate": self._calculate_growth_rate(trends),
            "prediction": self._predict_next_round(trends)
        }

        # 保存趋势数据
        with open(self.trends_file, 'w', encoding='utf-8') as fp:
            json.dump(trends, fp, ensure_ascii=False, indent=2)

        # 打印趋势摘要
        print("\n=== Evolution Trends Analysis ===")
        print(f"Total Analyzed: {trends['total_analyzed']}")
        print(f"Monthly Distribution: {trends['trend_analysis']['monthly_distribution']}")
        print(f"Status Distribution: {trends['trend_analysis']['status_distribution']}")
        print(f"Growth Rate: {trends['trend_analysis']['growth_rate']}")
        print(f"Prediction: {trends['trend_analysis']['prediction']}")

        return trends

    def status(self) -> Dict[str, Any]:
        """获取进化执行状态"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "tracker_version": "1.0.0",
            "tracking_file": str(self.tracking_file),
            "report_file": str(self.report_file),
            "trends_file": str(self.trends_file),
            "current_round": self._get_current_round()
        }

        # 检查文件是否存在
        status["tracking_exists"] = self.tracking_file.exists()
        status["report_exists"] = self.report_file.exists()
        status["trends_exists"] = self.trends_file.exists()

        print("\n=== Evolution Execution Tracker Status ===")
        print(f"Version: {status['tracker_version']}")
        print(f"Current Round: {status['current_round']}")
        print(f"Tracking File: {status['tracking_file']} - {'OK' if status['tracking_exists'] else 'Missing'}")
        print(f"Report File: {status['report_file']} - {'OK' if status['report_exists'] else 'Missing'}")
        print(f"Trends File: {status['trends_file']} - {'OK' if status['trends_exists'] else 'Missing'}")

        return status

    def _calculate_completion_rate(self, tracking: Dict) -> float:
        """计算完成率"""
        completed = sum(1 for s in tracking["execution_summary"] if s.get("status") == "completed")
        total = len(tracking["execution_summary"])
        return round(completed / total * 100, 2) if total > 0 else 0

    def _calculate_performance_metrics(self, tracking: Dict) -> Dict[str, Any]:
        """计算性能指标"""
        metrics = {
            "avg_modules_per_round": 0,
            "avg_files_per_round": 0,
            "success_rate": 0
        }

        if tracking["rounds_tracked"] > 0:
            metrics["avg_modules_per_round"] = round(tracking["total_modules_created"] / tracking["rounds_tracked"], 2)
            metrics["avg_files_per_round"] = round(tracking["total_files_modified"] / tracking["rounds_tracked"], 2)

        completed = sum(1 for s in tracking["execution_summary"] if s.get("status") == "completed")
        total = len(tracking["execution_summary"])
        metrics["success_rate"] = round(completed / total * 100, 2) if total > 0 else 0

        return metrics

    def _generate_recommendations(self, tracking: Dict) -> List[str]:
        """生成优化建议"""
        recommendations = []

        # 基于完成率建议
        completion_rate = self._calculate_completion_rate(tracking)
        if completion_rate < 80:
            recommendations.append("进化完成率较低，建议加强规划和验证环节")

        # 基于模块数量建议
        if tracking["total_modules_created"] < tracking["rounds_tracked"]:
            recommendations.append("部分轮次未创建新模块，建议评估是否需要更多创新")

        # 基于执行摘要分析
        recent_rounds = tracking["execution_summary"][-5:] if len(tracking["execution_summary"]) >= 5 else tracking["execution_summary"]
        failed = sum(1 for r in recent_rounds if r.get("status") != "completed")
        if failed > 2:
            recommendations.append(f"近期有 {failed} 轮未完成，建议检查执行流程")

        if not recommendations:
            recommendations.append("进化执行状态良好，继续保持")

        return recommendations

    def _calculate_growth_rate(self, trends: Dict) -> float:
        """计算增长率"""
        monthly = sorted(trends["rounds_by_month"].items())
        if len(monthly) < 2:
            return 0

        # 计算月均增长率
        values = [v for _, v in monthly]
        if len(values) > 1:
            growth = (values[-1] - values[0]) / len(values[:-1]) if len(values) > 1 else 0
            return round(growth, 2)

        return 0

    def _predict_next_round(self, trends: Dict) -> Dict[str, Any]:
        """预测下一轮"""
        monthly = sorted(trends["rounds_by_month"].items())

        prediction = {
            "suggested_focus": "基于近期进化趋势，建议关注执行效果追踪和报告生成",
            "expected_modules": 1,
            "confidence": "medium"
        }

        # 基于趋势预测
        if len(monthly) >= 3:
            recent_avg = sum(v for _, v in monthly[-3:]) / 3
            prediction["expected_rounds_next_month"] = round(recent_avg)

        return prediction

    def _get_current_round(self) -> int:
        """获取当前轮次"""
        try:
            mission_file = self.state_dir / "current_mission.json"
            if mission_file.exists():
                with open(mission_file, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    return data.get("loop_round", 222)
        except Exception:
            pass
        return 222


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nAvailable commands:")
        print("  track   - 追踪进化执行结果")
        print("  report  - 生成进化执行报告")
        print("  trends  - 分析进化趋势")
        print("  status  - 查看追踪状态")
        sys.exit(1)

    command = sys.argv[1].lower()
    tracker = EvolutionExecutionTracker()

    if command == "track":
        result = tracker.track()
        print("\nTracking completed successfully!")
    elif command == "report":
        result = tracker.report()
        print("\nReport generated successfully!")
    elif command == "trends":
        result = tracker.trends()
        print("\nTrends analysis completed successfully!")
    elif command == "status":
        result = tracker.status()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()