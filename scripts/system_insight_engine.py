"""
智能全系统洞察与预测引擎
Intelligent System-Wide Insight and Prediction Engine

功能：
- 统一分析70+引擎的性能和状态
- 识别跨引擎模式和问题
- 预测潜在问题
- 提供前瞻性洞察和建议

这是"超越用户"的能力 - 用户无法轻易看到系统级的模式和预测问题
"""

import os
import json
import glob
from datetime import datetime, timedelta
from pathlib import Path
import sys

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE = PROJECT_ROOT / "runtime" / "state"
RUNTIME_LOGS = PROJECT_ROOT / "runtime" / "logs"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"


class SystemInsightEngine:
    """智能全系统洞察与预测引擎"""

    def __init__(self):
        self.name = "system_insight_engine"
        self.description = "统一分析70+引擎性能、预测问题、提供主动洞察"
        self.engines = self._discover_engines()

    def _discover_engines(self):
        """发现所有引擎模块"""
        engines = []
        for f in SCRIPTS_DIR.glob("*_engine.py"):
            engines.append(f.stem)
        return engines

    def get_system_overview(self):
        """获取系统整体概览"""
        # 统计引擎数量
        engine_count = len(self.engines)

        # 检查各状态文件
        state_files = {}
        for f in RUNTIME_STATE.glob("*.json"):
            if f.name not in ["current_mission.json"]:
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        state_files[f.name] = json.load(fp)
                except:
                    pass

        # 检查最近的行为日志
        recent_logs = []
        log_file = RUNTIME_LOGS / f"behavior_{datetime.now().strftime('%Y-%m-%d')}.log"
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                recent_logs = lines[-20:] if len(lines) > 20 else lines

        return {
            "engine_count": engine_count,
            "engines": sorted(self.engines),
            "state_files_count": len(state_files),
            "recent_logs_count": len(recent_logs),
            "timestamp": datetime.now().isoformat()
        }

    def analyze_engine_performance(self):
        """分析引擎执行性能"""
        # 读取最近的行为日志
        log_file = RUNTIME_LOGS / f"behavior_{datetime.now().strftime('%Y-%m-%d')}.log"
        engine_stats = {}

        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        # 解析日志行
                        if '"phase"' in line and '"track"' in line:
                            for engine in self.engines:
                                if engine in line:
                                    if engine not in engine_stats:
                                        engine_stats[engine] = 0
                                    engine_stats[engine] += 1
                    except:
                        pass

        # 统计执行次数
        total_executions = sum(engine_stats.values())

        return {
            "engine_stats": engine_stats,
            "total_executions": total_executions,
            "most_active": sorted(engine_stats.items(), key=lambda x: x[1], reverse=True)[:10] if engine_stats else []
        }

    def predict_issues(self):
        """预测潜在问题"""
        predictions = []

        # 检查内存使用
        try:
            import psutil
            memory = psutil.virtual_memory()
            if memory.percent > 85:
                predictions.append({
                    "type": "memory",
                    "severity": "high",
                    "message": f"内存使用率较高 ({memory.percent}%)，建议清理不必要进程",
                    "action": "运行主动运维引擎的自动清理功能"
                })
            elif memory.percent > 70:
                predictions.append({
                    "type": "memory",
                    "severity": "medium",
                    "message": f"内存使用率 ({memory.percent}%)，建议关注"
                })
        except ImportError:
            pass

        # 检查磁盘空间
        try:
            disk = psutil.disk_usage('/')
            if disk.percent > 90:
                predictions.append({
                    "type": "disk",
                    "severity": "high",
                    "message": f"磁盘空间紧张 ({disk.percent}%)，建议清理",
                    "action": "运行主动运维引擎的自动清理功能"
                })
        except:
            pass

        # 检查守护进程状态
        daemon_state_file = RUNTIME_STATE / "daemon_linkage_state.json"
        if daemon_state_file.exists():
            try:
                with open(daemon_state_file, 'r', encoding='utf-8') as f:
                    daemon_state = json.load(f)
                    active_daemons = [d for d in daemon_state.get("daemons", []) if d.get("status") == "running"]
                    if len(active_daemons) < 2:
                        predictions.append({
                            "type": "daemon",
                            "severity": "low",
                            "message": f"当前只有 {len(active_daemons)} 个守护进程运行，可能影响主动服务能力"
                        })
            except:
                pass

        return predictions

    def generate_insights(self):
        """生成前瞻性洞察"""
        insights = []

        # 基于时间段的洞察
        hour = datetime.now().hour
        if 9 <= hour < 12:
            insights.append({
                "type": "time_based",
                "title": "上午高效时段",
                "message": "当前是上午高效时段，适合执行复杂任务和重要工作"
            })
        elif 14 <= hour < 17:
            insights.append({
                "type": "time_based",
                "title": "下午专注时段",
                "message": "下午适合执行需要持续专注的任务"
            })
        elif 20 <= hour < 23:
            insights.append({
                "type": "time_based",
                "title": "晚间总结时段",
                "message": "晚间适合回顾一天工作、规划次日任务"
            })

        # 基于引擎数量的洞察
        if len(self.engines) >= 50:
            insights.append({
                "type": "capability",
                "title": "能力库丰富",
                "message": f"系统已具备 {len(self.engines)} 个引擎，能力库非常丰富"
            })

        # 检查最近是否有新引擎
        recent_evolution = RUNTIME_STATE / "evolution_completed_ev_{}.json".format(
            datetime.now().strftime("%Y%m%d_%H%M%S")[:15]
        )

        return insights

    def get_cross_engine_patterns(self):
        """识别跨引擎模式"""
        # 读取最近的evolution历史
        patterns = []

        # 检查已完成的历史
        completed_files = sorted(RUNTIME_STATE.glob("evolution_completed_*.json"))

        if len(completed_files) >= 10:
            recent_rounds = []
            for f in completed_files[-10:]:
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        recent_rounds.append(data.get("current_goal", ""))
                except:
                    pass

            # 识别主题模式
            theme_counts = {}
            for goal in recent_rounds:
                if "智能" in goal:
                    # 提取主题
                    theme = goal.split("智能")[-1].split("引擎")[0] if "引擎" in goal else goal
                    theme_counts[theme] = theme_counts.get(theme, 0) + 1

            if theme_counts:
                patterns.append({
                    "type": "theme",
                    "description": "近期进化主题分布",
                    "data": theme_counts
                })

        return patterns

    def get_comprehensive_report(self):
        """生成综合报告"""
        overview = self.get_system_overview()
        performance = self.analyze_engine_performance()
        predictions = self.predict_issues()
        insights = self.generate_insights()
        patterns = self.get_cross_engine_patterns()

        return {
            "overview": overview,
            "performance": performance,
            "predictions": predictions,
            "insights": insights,
            "patterns": patterns,
            "generated_at": datetime.now().isoformat()
        }


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="智能全系统洞察与预测引擎")
    parser.add_argument("command", nargs="?", default="overview",
                        choices=["overview", "performance", "predictions", "insights", "patterns", "report"],
                        help="要执行的命令")
    parser.add_argument("--json", action="store_true", help="输出JSON格式")

    args = parser.parse_args()

    engine = SystemInsightEngine()

    if args.command == "overview":
        result = engine.get_system_overview()
    elif args.command == "performance":
        result = engine.analyze_engine_performance()
    elif args.command == "predictions":
        result = {"predictions": engine.predict_issues()}
    elif args.command == "insights":
        result = {"insights": engine.generate_insights()}
    elif args.command == "patterns":
        result = {"patterns": engine.get_cross_engine_patterns()}
    else:  # report
        result = engine.get_comprehensive_report()

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 人类可读格式
        if args.command == "overview":
            print(f"=== 系统概览 ===")
            print(f"引擎数量: {result['engine_count']}")
            print(f"状态文件: {result['state_files_count']}")
            print(f"最近日志: {result['recent_logs_count']} 条")
            print(f"时间: {result['timestamp']}")
        elif args.command == "report":
            print(f"=== 综合洞察报告 ===")
            print(f"\n--- 系统概览 ---")
            print(f"引擎数量: {result['overview']['engine_count']}")
            print(f"\n--- 性能分析 ---")
            print(f"总执行次数: {result['performance']['total_executions']}")
            if result['performance']['most_active']:
                print("最活跃引擎:")
                for engine, count in result['performance']['most_active']:
                    print(f"  {engine}: {count} 次")
            print(f"\n--- 预测 ---")
            for p in result['predictions']:
                print(f"[{p['severity']}] {p['type']}: {p['message']}")
            print(f"\n--- 洞察 ---")
            for i in result['insights']:
                print(f"{i['title']}: {i['message']}")
            print(f"\n生成时间: {result['generated_at']}")
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()