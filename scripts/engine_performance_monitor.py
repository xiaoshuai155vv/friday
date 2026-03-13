#!/usr/bin/env python3
"""
智能引擎性能监控与自动调优引擎

功能：
1. 引擎性能数据收集 - 记录各引擎的执行时间、成功率、资源消耗
2. 性能分析 - 分析各引擎的执行效率，识别瓶颈
3. 低效引擎识别 - 自动识别执行效率较低的引擎
4. 自动调优建议 - 生成优化建议，帮助提升性能

使用方法：
    python engine_performance_monitor.py status          # 查看各引擎性能状态
    python engine_performance_monitor.py analyze         # 分析引擎性能
    python engine_performance_monitor.py recommend       # 获取调优建议
    python engine_performance_monitor.py record <engine> <duration> <success>  # 记录执行数据
    python engine_performance_monitor.py clear           # 清除性能数据
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import threading

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"


class EnginePerformanceMonitor:
    """智能引擎性能监控与自动调优引擎"""

    def __init__(self):
        self.state_file = STATE_DIR / "engine_performance.json"
        self.lock = threading.Lock()
        self.load_state()

    def load_state(self):
        """加载性能数据"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                self.state = json.load(f)
        else:
            self.state = {
                "initialized_at": datetime.now().isoformat(),
                "engine_stats": {},  # {engine_name: {executions: [], avg_time: 0, success_rate: 0}}
                "alerts": []
            }

    def save_state(self):
        """保存性能数据"""
        with self.lock:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)

    def record_execution(self, engine_name, duration_ms, success, error=None):
        """记录引擎执行数据"""
        with self.lock:
            if engine_name not in self.state["engine_stats"]:
                self.state["engine_stats"][engine_name] = {
                    "executions": [],
                    "total_time_ms": 0,
                    "success_count": 0,
                    "failure_count": 0,
                    "avg_time_ms": 0,
                    "success_rate": 0,
                    "last_execution": None
                }

            stats = self.state["engine_stats"][engine_name]

            # 记录执行
            execution = {
                "timestamp": datetime.now().isoformat(),
                "duration_ms": duration_ms,
                "success": success,
                "error": error
            }
            stats["executions"].append(execution)

            # 只保留最近100条记录
            if len(stats["executions"]) > 100:
                stats["executions"] = stats["executions"][-100:]

            # 更新统计
            stats["total_time_ms"] += duration_ms
            if success:
                stats["success_count"] += 1
            else:
                stats["failure_count"] += 1

            # 计算平均值（使用最近10次）
            recent = stats["executions"][-10:]
            stats["avg_time_ms"] = sum(e["duration_ms"] for e in recent) / len(recent) if recent else 0

            total = stats["success_count"] + stats["failure_count"]
            stats["success_rate"] = stats["success_count"] / total if total > 0 else 0
            stats["last_execution"] = datetime.now().isoformat()

            self.save_state()

    def get_engine_status(self):
        """获取各引擎性能状态"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "engines": {}
        }

        for engine_name, stats in self.state.get("engine_stats", {}).items():
            status["engines"][engine_name] = {
                "total_executions": stats["success_count"] + stats["failure_count"],
                "avg_time_ms": round(stats["avg_time_ms"], 2),
                "success_rate": round(stats["success_rate"] * 100, 2),
                "last_execution": stats.get("last_execution")
            }

        return status

    def analyze_performance(self):
        """分析引擎性能，识别低效引擎"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "low_performance_engines": [],
            "high_success_rate_engines": [],
            "slow_engines": [],
            "recommendations": []
        }

        for engine_name, stats in self.state.get("engine_stats", {}).items():
            total = stats["success_count"] + stats["failure_count"]
            if total < 3:
                continue  # 跳过执行次数太少的引擎

            # 识别低性能引擎（成功率低于80%）
            if stats["success_rate"] < 0.8:
                analysis["low_performance_engines"].append({
                    "engine": engine_name,
                    "success_rate": round(stats["success_rate"] * 100, 2),
                    "reason": f"成功率仅 {stats['success_rate']*100:.1f}%"
                })

            # 识别高成功率引擎（用于推荐）
            if stats["success_rate"] >= 0.95:
                analysis["high_success_rate_engines"].append({
                    "engine": engine_name,
                    "success_rate": round(stats["success_rate"] * 100, 2)
                })

            # 识别慢引擎（平均执行时间超过5秒）
            if stats["avg_time_ms"] > 5000:
                analysis["slow_engines"].append({
                    "engine": engine_name,
                    "avg_time_ms": round(stats["avg_time_ms"], 2),
                    "reason": f"平均执行时间 {stats['avg_time_ms']/1000:.1f}秒"
                })

        # 生成优化建议
        for engine in analysis["low_performance_engines"]:
            analysis["recommendations"].append({
                "engine": engine["engine"],
                "priority": "high",
                "type": "reliability",
                "suggestion": f"该引擎成功率较低（{engine['success_rate']}%），建议检查错误原因并优化",
                "action": "检查引擎日志，识别失败模式"
            })

        for engine in analysis["slow_engines"]:
            analysis["recommendations"].append({
                "engine": engine["engine"],
                "priority": "medium",
                "type": "performance",
                "suggestion": f"该引擎执行较慢（{engine['avg_time_ms']/1000:.1f}秒），建议优化执行逻辑",
                "action": "分析执行流程，识别瓶颈步骤"
            })

        # 如果没有足够数据，提供通用建议
        if len(self.state.get("engine_stats", {})) < 5:
            analysis["recommendations"].append({
                "engine": "system",
                "priority": "low",
                "type": "data_collection",
                "suggestion": "性能数据不足，建议多使用各引擎以积累数据",
                "action": "继续使用各功能以收集更多数据"
            })

        return analysis

    def generate_recommendations(self):
        """生成调优建议"""
        analysis = self.analyze_performance()
        return analysis.get("recommendations", [])

    def get_top_engines(self, limit=5, by="success_rate"):
        """获取最佳引擎"""
        engines = []

        for engine_name, stats in self.state.get("engine_stats", {}).items():
            total = stats["success_count"] + stats["failure_count"]
            if total >= 3:  # 至少执行3次
                engines.append({
                    "engine": engine_name,
                    "success_rate": stats["success_rate"],
                    "avg_time_ms": stats["avg_time_ms"],
                    "total_executions": total
                })

        if by == "success_rate":
            engines.sort(key=lambda x: x["success_rate"], reverse=True)
        elif by == "speed":
            engines.sort(key=lambda x: x["avg_time_ms"])
        else:
            engines.sort(key=lambda x: x["total_executions"], reverse=True)

        return engines[:limit]

    def clear_data(self):
        """清除性能数据"""
        self.state = {
            "initialized_at": datetime.now().isoformat(),
            "engine_stats": {},
            "alerts": []
        }
        self.save_state()
        return {"status": "cleared", "message": "性能数据已清除"}


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1].lower()
    monitor = EnginePerformanceMonitor()

    if command == "status":
        # 查看性能状态
        status = monitor.get_engine_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif command == "analyze":
        # 分析性能
        analysis = monitor.analyze_performance()
        print(json.dumps(analysis, ensure_ascii=False, indent=2))

    elif command == "recommend" or command == "recommends":
        # 获取建议
        recommendations = monitor.generate_recommendations()
        print(json.dumps(recommendations, ensure_ascii=False, indent=2))

    elif command == "record":
        # 记录执行数据
        if len(sys.argv) < 5:
            print("用法: python engine_performance_monitor.py record <engine_name> <duration_ms> <success>")
            return

        engine_name = sys.argv[2]
        try:
            duration_ms = float(sys.argv[3])
            success = sys.argv[4].lower() in ("true", "1", "yes", "success")
            monitor.record_execution(engine_name, duration_ms, success)
            print(json.dumps({"status": "recorded", "engine": engine_name}, ensure_ascii=False))
        except ValueError:
            print(f"错误: duration_ms 应该是数字")
            return

    elif command == "top":
        # 获取最佳引擎
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        by = sys.argv[3] if len(sys.argv) > 3 else "success_rate"
        top_engines = monitor.get_top_engines(limit, by)
        print(json.dumps(top_engines, ensure_ascii=False, indent=2))

    elif command == "clear":
        # 清除数据
        result = monitor.clear_data()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command in ["-h", "--help", "help"]:
        print(__doc__)

    else:
        print(f"未知命令: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()