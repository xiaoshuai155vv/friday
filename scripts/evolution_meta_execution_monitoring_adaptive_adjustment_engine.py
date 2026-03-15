#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环元进化执行过程实时监控与自适应调整引擎
让系统能够实时追踪目标执行进度、根据执行反馈自动调整策略、形成「设定→执行→监控→调整」的完整闭环。

版本: 1.0.0
依赖: round 639 目标设定引擎, round 635-638 三角闭环引擎
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
import time

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class MetaExecutionMonitoringAdaptiveAdjustmentEngine:
    """元进化执行过程实时监控与自适应调整引擎"""

    VERSION = "1.0.0"

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.runtime_dir = self.project_root / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.logs_dir = self.runtime_dir / "logs"
        self.monitoring_data_file = self.state_dir / "execution_monitoring_data.json"

    def get_goal_setting_data(self):
        """获取目标设定引擎的数据"""
        goal_engine_file = self.project_root / "scripts" / "evolution_meta_goal_autonomous_setting_engine.py"
        if not goal_engine_file.exists():
            return None

        # 尝试从 current_mission 读取当前目标
        mission_file = self.state_dir / "current_mission.json"
        if mission_file.exists():
            with open(mission_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def load_monitoring_data(self):
        """加载监控数据"""
        if self.monitoring_data_file.exists():
            with open(self.monitoring_data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "active_goals": [],
            "execution_records": [],
            "adjustment_history": [],
            "anomalies": []
        }

    def save_monitoring_data(self, data):
        """保存监控数据"""
        with open(self.monitoring_data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def track_execution_progress(self, goal_id, progress_info):
        """追踪执行进度"""
        data = self.load_monitoring_data()

        # 更新或添加目标进度
        found = False
        for goal in data.get("active_goals", []):
            if goal.get("goal_id") == goal_id:
                goal.update({
                    "progress": progress_info.get("progress", 0),
                    "status": progress_info.get("status", "running"),
                    "last_update": datetime.now().isoformat(),
                    "metrics": progress_info.get("metrics", {})
                })
                found = True
                break

        if not found:
            data.setdefault("active_goals", []).append({
                "goal_id": goal_id,
                "goal_text": progress_info.get("goal_text", ""),
                "progress": progress_info.get("progress", 0),
                "status": progress_info.get("status", "running"),
                "created_at": datetime.now().isoformat(),
                "last_update": datetime.now().isoformat(),
                "metrics": progress_info.get("metrics", {})
            })

        self.save_monitoring_data(data)
        return data

    def analyze_execution_feedback(self, goal_id):
        """分析执行反馈"""
        data = self.load_monitoring_data()

        # 查找目标执行记录
        goal_record = None
        for goal in data.get("active_goals", []):
            if goal.get("goal_id") == goal_id:
                goal_record = goal
                break

        if not goal_record:
            return {"error": "目标不存在", "suggestions": []}

        # 分析反馈
        progress = goal_record.get("progress", 0)
        status = goal_record.get("status", "unknown")
        metrics = goal_record.get("metrics", {})

        suggestions = []

        # 基于进度的分析
        if progress < 30 and status == "running":
            suggestions.append({
                "type": "acceleration",
                "description": "执行进度较慢，考虑增加资源投入或优化执行策略",
                "priority": "high"
            })
        elif progress > 80 and status == "running":
            suggestions.append({
                "type": "completion",
                "description": "目标即将完成，建议做好收尾和验证工作",
                "priority": "medium"
            })

        # 基于指标的分析
        if metrics:
            if metrics.get("execution_time", 0) > 300:  # 超过5分钟
                suggestions.append({
                    "type": "optimization",
                    "description": "执行时间较长，考虑优化执行效率",
                    "priority": "medium"
                })
            if metrics.get("error_count", 0) > 3:
                suggestions.append({
                    "type": "error_handling",
                    "description": "错误次数较多，建议检查执行路径",
                    "priority": "high"
                })

        return {
            "goal_id": goal_id,
            "current_progress": progress,
            "status": status,
            "analysis": "执行反馈分析完成",
            "suggestions": suggestions
        }

    def adaptive_adjustment(self, goal_id, adjustment_plan):
        """自适应调整"""
        data = self.load_monitoring_data()

        adjustment_record = {
            "goal_id": goal_id,
            "adjustment_type": adjustment_plan.get("type", "unknown"),
            "description": adjustment_plan.get("description", ""),
            "old_strategy": adjustment_plan.get("old_strategy", ""),
            "new_strategy": adjustment_plan.get("new_strategy", ""),
            "timestamp": datetime.now().isoformat(),
            "success": True
        }

        # 记录调整历史
        data.setdefault("adjustment_history", []).append(adjustment_record)

        # 更新目标状态
        for goal in data.get("active_goals", []):
            if goal.get("goal_id") == goal_id:
                goal["last_adjustment"] = adjustment_plan.get("type", "")
                goal["last_adjustment_time"] = datetime.now().isoformat()
                break

        self.save_monitoring_data(data)
        return {
            "status": "success",
            "adjustment_record": adjustment_record,
            "message": f"已应用调整策略: {adjustment_plan.get('description', '')}"
        }

    def detect_anomalies(self):
        """检测执行异常"""
        data = self.load_monitoring_data()
        anomalies = []

        for goal in data.get("active_goals", []):
            # 检查停滞目标（超过10分钟无更新）
            last_update = goal.get("last_update", "")
            if last_update:
                try:
                    last_time = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                    time_diff = (datetime.now() - last_time.replace(tzinfo=None)).total_seconds()
                    if time_diff > 600 and goal.get("status") == "running":
                        anomalies.append({
                            "goal_id": goal.get("goal_id"),
                            "type": "stagnation",
                            "description": f"目标 {goal.get('goal_id')} 执行停滞超过10分钟",
                            "timestamp": datetime.now().isoformat(),
                            "severity": "warning"
                        })
                except:
                    pass

            # 检查低进度目标
            if goal.get("progress", 0) < 10 and goal.get("status") == "running":
                created_at = goal.get("created_at", "")
                if created_at:
                    try:
                        created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        time_diff = (datetime.now() - created_time.replace(tzinfo=None)).total_seconds()
                        if time_diff > 300:  # 超过5分钟
                            anomalies.append({
                                "goal_id": goal.get("goal_id"),
                                "type": "low_progress",
                                "description": f"目标 {goal.get('goal_id')} 进度低于10%且超过5分钟",
                                "timestamp": datetime.now().isoformat(),
                                "severity": "warning"
                            })
                    except:
                        pass

        # 保存异常记录
        if anomalies:
            data["anomalies"] = anomalies
            self.save_monitoring_data(data)

        return anomalies

    def get_execution_summary(self):
        """获取执行摘要"""
        data = self.load_monitoring_data()

        active_count = len([g for g in data.get("active_goals", []) if g.get("status") == "running"])
        completed_count = len([g for g in data.get("active_goals", []) if g.get("status") == "completed"])
        anomaly_count = len(data.get("anomalies", []))
        adjustment_count = len(data.get("adjustment_history", []))

        return {
            "total_goals": len(data.get("active_goals", [])),
            "active_goals": active_count,
            "completed_goals": completed_count,
            "anomaly_count": anomaly_count,
            "adjustment_count": adjustment_count,
            "timestamp": datetime.now().isoformat()
        }

    def get_cockpit_data(self):
        """获取驾驶舱数据"""
        data = self.load_monitoring_data()
        summary = self.get_execution_summary()

        return {
            "version": self.VERSION,
            "summary": summary,
            "active_goals": data.get("active_goals", []),
            "recent_adjustments": data.get("adjustment_history", [])[-5:],
            "anomalies": data.get("anomalies", [])
        }

    def run(self):
        """执行引擎主逻辑"""
        # 模拟执行过程
        goal_data = self.get_goal_setting_data()

        # 加载监控数据
        monitoring_data = self.load_monitoring_data()

        # 模拟追踪当前目标（如果有）
        if goal_data and goal_data.get("current_goal"):
            goal_id = f"goal_{goal_data.get('loop_round', 640)}"

            # 检查是否已存在
            existing = [g for g in monitoring_data.get("active_goals", []) if g.get("goal_id") == goal_id]
            if not existing:
                # 添加新目标
                tracking_result = self.track_execution_progress(goal_id, {
                    "goal_text": goal_data.get("current_goal", ""),
                    "progress": 0,
                    "status": "initialized",
                    "metrics": {
                        "execution_time": 0,
                        "error_count": 0,
                        "last_checkpoint": datetime.now().isoformat()
                    }
                })
                print(f"[执行监控] 追踪目标: {goal_id}")
                print(f"[执行监控] 目标内容: {goal_data.get('current_goal', '')[:50]}...")

        # 分析执行反馈
        if monitoring_data.get("active_goals"):
            for goal in monitoring_data.get("active_goals", []):
                if goal.get("status") == "running":
                    analysis = self.analyze_execution_feedback(goal.get("goal_id"))
                    if analysis.get("suggestions"):
                        print(f"[执行监控] 分析建议: {len(analysis.get('suggestions', []))} 条")

        # 检测异常
        anomalies = self.detect_anomalies()
        if anomalies:
            print(f"[执行监控] 检测到 {len(anomalies)} 个异常")

        # 获取摘要
        summary = self.get_execution_summary()
        print(f"[执行监控] 执行摘要: {summary.get('active_goals', 0)} 个活跃目标, "
              f"{summary.get('completed_goals', 0)} 个已完成, "
              f"{summary.get('adjustment_count', 0)} 次调整")

        return {
            "status": "success",
            "version": self.VERSION,
            "summary": summary,
            "message": "元进化执行过程实时监控与自适应调整引擎运行完成"
        }


def main():
    parser = argparse.ArgumentParser(
        description="智能全场景进化环元进化执行过程实时监控与自适应调整引擎"
    )
    parser.add_argument("--version", action="store_true", help="显示版本信息")
    parser.add_argument("--status", action="store_true", help="显示引擎状态")
    parser.add_argument("--run", action="store_true", help="运行引擎")
    parser.add_argument("--track", type=str, help="追踪目标进度 (goal_id:progress:status)")
    parser.add_argument("--analyze", type=str, help="分析执行反馈 (goal_id)")
    parser.add_argument("--adjust", type=str, help="执行自适应调整 (goal_id:adjustment_type:description)")
    parser.add_argument("--detect-anomalies", action="store_true", help="检测执行异常")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")

    args = parser.parse_args()

    engine = MetaExecutionMonitoringAdaptiveAdjustmentEngine()

    if args.version:
        print(f"元进化执行过程实时监控与自适应调整引擎 v{engine.VERSION}")
        return

    if args.status:
        summary = engine.get_execution_summary()
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return

    if args.run:
        result = engine.run()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.track:
        parts = args.track.split(":")
        if len(parts) >= 3:
            goal_id, progress, status = parts[0], int(parts[1]), parts[2]
            result = engine.track_execution_progress(goal_id, {
                "progress": progress,
                "status": status
            })
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.analyze:
        result = engine.analyze_execution_feedback(args.analyze)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.adjust:
        parts = args.adjust.split(":")
        if len(parts) >= 3:
            goal_id, adjustment_type, description = parts[0], parts[1], parts[2]
            result = engine.adaptive_adjustment(goal_id, {
                "type": adjustment_type,
                "description": description
            })
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.detect_anomalies:
        anomalies = engine.detect_anomalies()
        print(json.dumps(anomalies, ensure_ascii=False, indent=2))
        return

    if args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    # 默认显示状态
    summary = engine.get_execution_summary()
    print(f"元进化执行过程实时监控与自适应调整引擎 v{engine.VERSION}")
    print(f"活跃目标: {summary.get('active_goals', 0)}")
    print(f"已完成: {summary.get('completed_goals', 0)}")
    print(f"调整次数: {summary.get('adjustment_count', 0)}")
    print(f"异常数量: {summary.get('anomaly_count', 0)}")


if __name__ == "__main__":
    main()