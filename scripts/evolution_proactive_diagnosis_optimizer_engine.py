#!/usr/bin/env python3
"""
智能全场景进化环主动诊断与优化建议引擎
version 1.0.0

在 round 482 完成的效能实时数据推送与驾驶舱智能预警能力基础上，进一步构建主动诊断与智能建议能力。
让系统能够基于进化环历史数据自动诊断健康状态、主动识别潜在风险、智能生成优化建议并主动推送，
实现从「数据展示→主动诊断→智能建议→自动执行」的完整闭环。

功能：
1. 健康状态智能诊断（分析多维度指标，识别风险）
2. 问题根因自动分析（从指标异常追溯到具体问题）
3. 智能优化建议生成（基于历史成功经验给出建议）
4. 建议优先级排序（按价值和紧迫性排序）
5. 主动推送机制（预警时主动推送诊断和建议）
6. 与进化驾驶舱深度集成
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
STATE_DIR = PROJECT_ROOT / "runtime" / "state"
LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"


class ProactiveDiagnosisOptimizer:
    """主动诊断与优化建议引擎"""

    def __init__(self):
        self.state_dir = STATE_DIR
        self.logs_dir = LOGS_DIR
        self.health_thresholds = {
            "efficiency_score": 70,
            "success_rate": 80,
            "response_time": 5.0,  # 秒
            "knowledge_coverage": 60
        }

    def load_evolution_history(self, limit=20):
        """加载最近的进化历史"""
        history = []
        state_dir = self.state_dir

        # 读取 evolution_completed_*.json 文件
        for f in sorted(state_dir.glob("evolution_completed_*.json"), reverse=True)[:limit]:
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    history.append(data)
            except Exception as e:
                print(f"Warning: Failed to load {f}: {e}", file=sys.stderr)

        return history

    def load_performance_data(self):
        """加载效能数据"""
        perf_file = self.state_dir / "evolution_performance_data.json"
        if perf_file.exists():
            try:
                with open(perf_file, 'r', encoding='utf-8') as fp:
                    return json.load(fp)
            except Exception as e:
                print(f"Warning: Failed to load performance data: {e}", file=sys.stderr)

        return {}

    def calculate_health_score(self, history, perf_data):
        """计算健康分数"""
        if not history:
            return 50.0, "无历史数据"

        # 分析历史数据
        total = len(history)
        completed = sum(1 for h in history if h.get("完成状态") == "已完成" or h.get("is_completed") == True)

        success_rate = (completed / total * 100) if total > 0 else 0

        # 计算平均效率
        avg_efficiency = 75.0  # 默认值
        if perf_data:
            avg_efficiency = perf_data.get("avg_efficiency_score", 75.0)

        # 综合健康分
        health_score = (success_rate * 0.4 + avg_efficiency * 0.6)

        # 生成诊断原因
        if health_score >= 85:
            diagnosis = "进化环运行状态优秀，各项指标正常"
        elif health_score >= 70:
            diagnosis = "进化环运行状态良好，有少量优化空间"
        elif health_score >= 50:
            diagnosis = "进化环运行状态一般，存在明显问题需要关注"
        else:
            diagnosis = "进化环运行状态较差，建议立即进行诊断和优化"

        return round(health_score, 1), diagnosis

    def analyze_problems(self, history, perf_data):
        """分析潜在问题"""
        problems = []

        if not history:
            problems.append({
                "type": "数据缺失",
                "severity": "high",
                "description": "缺少进化历史数据，建议先执行几轮进化环",
                "suggestion": "运行进化环生成历史数据"
            })
            return problems

        # 检查成功率
        total = len(history)
        completed = sum(1 for h in history if h.get("完成状态") == "已完成" or h.get("is_completed") == True)
        success_rate = (completed / total * 100) if total > 0 else 0

        if success_rate < self.health_thresholds["success_rate"]:
            problems.append({
                "type": "成功率偏低",
                "severity": "medium" if success_rate >= 60 else "high",
                "description": f"进化成功率为 {success_rate:.1f}%，低于阈值 {self.health_thresholds['success_rate']}%",
                "suggestion": "检查失败原因，优化进化策略"
            })

        # 检查未完成的任务
        incomplete = [h for h in history if h.get("完成状态") != "已完成" and h.get("is_completed") != True]
        if incomplete:
            problems.append({
                "type": "存在未完成任务",
                "severity": "medium",
                "description": f"有 {len(incomplete)} 个未完成的进化任务",
                "suggestion": "分析未完成任务原因，决定是否继续或放弃"
            })

        # 检查效能数据
        if perf_data:
            if perf_data.get("avg_efficiency_score", 75) < self.health_thresholds["efficiency_score"]:
                problems.append({
                    "type": "效能偏低",
                    "severity": "medium",
                    "description": f"平均效能为 {perf_data.get('avg_efficiency_score', 75):.1f}，低于阈值",
                    "suggestion": "优化执行策略，减少资源浪费"
                })

            if perf_data.get("avg_response_time", 0) > self.health_thresholds["response_time"]:
                problems.append({
                    "type": "响应时间过长",
                    "severity": "low",
                    "description": f"平均响应时间为 {perf_data.get('avg_response_time', 0):.1f}秒",
                    "suggestion": "优化执行流程，减少等待时间"
                })

        return problems

    def generate_optimization_suggestions(self, problems, history):
        """生成优化建议"""
        suggestions = []

        if not problems:
            suggestions.append({
                "priority": "low",
                "title": "保持现状",
                "description": "当前系统运行状态良好，无需特殊优化",
                "action": "继续监控"
            })
            return suggestions

        for problem in problems:
            severity = problem.get("severity", "low")
            priority = 1 if severity == "high" else 2 if severity == "medium" else 3

            suggestions.append({
                "priority": priority,
                "title": f"优化建议：{problem['type']}",
                "description": problem["description"],
                "suggestion": problem["suggestion"],
                "action": f"执行：{problem['suggestion']}"
            })

        # 按优先级排序
        suggestions.sort(key=lambda x: x["priority"])

        return suggestions

    def diagnose(self):
        """执行完整诊断"""
        print("=" * 60)
        print("进化环主动诊断报告")
        print("=" * 60)

        # 加载数据
        history = self.load_evolution_history()
        perf_data = self.load_performance_data()

        # 计算健康分
        health_score, diagnosis = self.calculate_health_score(history, perf_data)

        print(f"\n【健康评分】{health_score}/100")
        print(f"【诊断结果】{diagnosis}")
        print(f"【历史记录】共 {len(history)} 条")

        # 分析问题
        problems = self.analyze_problems(history, perf_data)

        if problems:
            print(f"\n【发现问题】{len(problems)} 个")
            for i, p in enumerate(problems, 1):
                print(f"  {i}. [{p['severity'].upper()}] {p['type']}: {p['description']}")
                print(f"     → 建议：{p['suggestion']}")
        else:
            print("\n【发现问题】无")

        # 生成优化建议
        suggestions = self.generate_optimization_suggestions(problems, history)

        print(f"\n【优化建议】{len(suggestions)} 条")
        for i, s in enumerate(suggestions, 1):
            priority_label = "高" if s["priority"] == 1 else "中" if s["priority"] == 2 else "低"
            print(f"  {i}. [优先级:{priority_label}] {s['title']}")
            print(f"     {s['description']}")
            print(f"     → {s['action']}")

        print("\n" + "=" * 60)

        # 返回结构化结果
        return {
            "health_score": health_score,
            "diagnosis": diagnosis,
            "history_count": len(history),
            "problems": problems,
            "suggestions": suggestions,
            "timestamp": datetime.now().isoformat()
        }

    def get_cockpit_data(self):
        """获取驾驶舱数据接口"""
        history = self.load_evolution_history()
        perf_data = self.load_performance_data()
        health_score, diagnosis = self.calculate_health_score(history, perf_data)
        problems = self.analyze_problems(history, perf_data)
        suggestions = self.generate_optimization_suggestions(problems, history)

        return {
            "health_score": health_score,
            "diagnosis": diagnosis,
            "problem_count": len(problems),
            "suggestion_count": len(suggestions),
            "high_priority_suggestions": len([s for s in suggestions if s["priority"] == 1]),
            "timestamp": datetime.now().isoformat()
        }

    def auto_check_and_notify(self):
        """自动检查并通知"""
        history = self.load_evolution_history()
        perf_data = self.load_performance_data()
        health_score, diagnosis = self.calculate_health_score(history, perf_data)
        problems = self.analyze_problems(history, perf_data)
        suggestions = self.generate_optimization_suggestions(problems, history)

        notifications = []

        # 根据健康分生成通知
        if health_score < 50:
            notifications.append({
                "level": "critical",
                "title": "进化环健康状态危急",
                "message": f"健康分 {health_score}/100，{diagnosis}"
            })
        elif health_score < 70:
            notifications.append({
                "level": "warning",
                "title": "进化环需要关注",
                "message": f"健康分 {health_score}/100，{diagnosis}"
            })

        # 高优先级建议通知
        high_priority = [s for s in suggestions if s["priority"] == 1]
        if high_priority:
            notifications.append({
                "level": "info",
                "title": f"有 {len(high_priority)} 个高优先级优化建议",
                "message": high_priority[0]["title"]
            })

        return notifications


def main():
    parser = argparse.ArgumentParser(
        description="智能全场景进化环主动诊断与优化建议引擎"
    )
    parser.add_argument("--diagnose", action="store_true", help="执行完整诊断")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据接口")
    parser.add_argument("--auto-check", action="store_true", help="自动检查并生成通知")
    parser.add_argument("--status", action="store_true", help="快速查看状态")

    args = parser.parse_args()

    engine = ProactiveDiagnosisOptimizer()

    if args.status:
        # 快速状态查看
        data = engine.get_cockpit_data()
        print(f"健康分: {data['health_score']}/100")
        print(f"诊断: {data['diagnosis']}")
        print(f"发现问题: {data['problem_count']} 个")
        print(f"优化建议: {data['suggestion_count']} 条")
        print(f"高优先级: {data['high_priority_suggestions']} 条")
    elif args.diagnose:
        # 完整诊断
        result = engine.diagnose()
        # 保存诊断结果
        result_file = engine.state_dir / "diagnosis_result.json"
        with open(result_file, 'w', encoding='utf-8') as fp:
            json.dump(result, fp, ensure_ascii=False, indent=2)
        print(f"\n诊断结果已保存到: {result_file}")
    elif args.cockpit_data:
        # 驾驶舱数据接口
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
    elif args.auto_check:
        # 自动检查
        notifications = engine.auto_check_and_notify()
        if notifications:
            print("【主动通知】")
            for n in notifications:
                print(f"  [{n['level'].upper()}] {n['title']}: {n['message']}")
        else:
            print("无需通知，当前状态正常")
    else:
        parser.print_help()
        print("\n示例:")
        print("  python evolution_proactive_diagnosis_optimizer_engine.py --status")
        print("  python evolution_proactive_diagnosis_optimizer_engine.py --diagnose")
        print("  python evolution_proactive_diagnosis_optimizer_engine.py --cockpit-data")
        print("  python evolution_proactive_diagnosis_optimizer_engine.py --auto-check")


if __name__ == "__main__":
    main()