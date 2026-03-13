#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能进化预测与主动规划引擎
让进化环能够主动预测下一轮应该进化什么，基于历史效率、当前系统状态、能力缺口动态规划进化方向
实现从被动响应到主动预测的范式升级
"""

import os
import json
import glob
from datetime import datetime, timedelta
from pathlib import Path

# 项目根目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
RUNTIME_STATE_DIR = os.path.join(PROJECT_ROOT, "runtime", "state")
RUNTIME_LOGS_DIR = os.path.join(PROJECT_ROOT, "runtime", "logs")


class EvolutionPredictionPlanner:
    """智能进化预测与主动规划引擎"""

    def __init__(self):
        self.state_dir = RUNTIME_STATE_DIR
        self.logs_dir = RUNTIME_LOGS_DIR
        self.history_file = os.path.join(self.state_dir, "evolution_history.json")

    def get_evolution_history(self, limit=30):
        """获取进化历史数据"""
        history = []
        # 读取进化完成文件
        pattern = os.path.join(self.state_dir, "evolution_completed_ev_*.json")
        files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)[:limit]

        for f in files:
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    history.append(data)
            except Exception:
                pass

        return history

    def analyze_evolution_efficiency(self, history):
        """分析进化效率"""
        if not history:
            return {
                "total_rounds": 0,
                "completed": 0,
                "success_rate": 0,
                "avg_completion_time": 0,
                "efficiency_score": 0
            }

        total = len(history)
        # 确保每个 history 项都是字典且 result 是字典
        completed = 0
        for h in history:
            if not isinstance(h, dict):
                continue
            result = h.get("result")
            if isinstance(result, dict) and result.get("status") == "completed":
                completed += 1
        success_rate = completed / total if total > 0 else 0

        # 计算平均完成时间
        completion_times = []
        for h in history:
            if not isinstance(h, dict):
                continue
            completed_at = h.get("completed_at")
            if completed_at:
                try:
                    dt = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
                    completion_times.append(dt)
                except Exception:
                    pass

        avg_completion_time = 0
        if len(completion_times) > 1:
            time_diffs = []
            for i in range(1, len(completion_times)):
                try:
                    # 统一为 naive datetime 进行计算
                    t1 = completion_times[i-1].replace(tzinfo=None)
                    t2 = completion_times[i].replace(tzinfo=None)
                    diff = (t1 - t2).total_seconds()
                    time_diffs.append(diff)
                except Exception:
                    pass
            avg_completion_time = sum(time_diffs) / len(time_diffs) if time_diffs else 0

        # 效率评分（基于成功率）
        efficiency_score = success_rate * 100

        return {
            "total_rounds": total,
            "completed": completed,
            "success_rate": round(success_rate * 100, 2),
            "avg_completion_time_minutes": round(avg_completion_time / 60, 2) if avg_completion_time > 0 else 0,
            "efficiency_score": round(efficiency_score, 2)
        }

    def detect_evolution_patterns(self, history):
        """检测进化模式"""
        patterns = {
            "recent_focus": [],  # 近期重点领域
            "repeated_areas": [],  # 重复改进区域
            "neglected_areas": [],  # 被忽视的领域
            "trend": []  # 进化趋势
        }

        if not history:
            return patterns

        # 过滤出字典类型的项
        valid_history = [h for h in history if isinstance(h, dict)]

        # 分析近期焦点领域
        recent_goals = [h.get("current_goal", "")[:50] for h in valid_history[:10]]
        patterns["recent_focus"] = recent_goals[:5]

        # 检测重复改进
        goal_categories = {}
        for h in valid_history:
            goal = h.get("current_goal", "")
            # 提取关键词
            keywords = []
            if "引擎" in goal:
                # 提取引擎名称
                start = goal.find("智能")
                if start >= 0:
                    end = goal.find("引擎", start)
                    if end > start:
                        keywords.append(goal[start:end+2])
            for kw in keywords:
                goal_categories[kw] = goal_categories.get(kw, 0) + 1

        # 找出重复超过2次的领域
        repeated = [(k, v) for k, v in goal_categories.items() if v > 2]
        patterns["repeated_areas"] = [f"{k}({v}次)" for k, v in sorted(repeated, key=lambda x: -x[1])[:5]]

        return patterns

    def predict_next_evolution(self, history, efficiency, patterns):
        """预测下一轮进化方向"""
        predictions = []

        if not history:
            # 无历史时，基于通用原则预测
            predictions.append({
                "type": "foundation",
                "direction": "增强基础能力",
                "reason": "无进化历史，需要建立基础",
                "priority": 9
            })
            return predictions

        # 基于效率预测
        if efficiency.get("success_rate", 0) < 80:
            predictions.append({
                "type": "optimization",
                "direction": "优化进化策略",
                "reason": f"进化成功率较低({efficiency.get('success_rate', 0)}%)，需要改进策略",
                "priority": 9
            })

        # 基于模式预测
        if patterns.get("repeated_areas"):
            predictions.append({
                "type": "diversification",
                "direction": "探索新领域",
                "reason": f"检测到重复改进: {', '.join(patterns.get('repeated_areas', [])[:2])}",
                "priority": 7
            })

        # 基于近期重点预测
        recent_focus = patterns.get("recent_focus", [])
        if any("协同" in str(f) for f in recent_focus[:3]):
            predictions.append({
                "type": "integration",
                "direction": "深度集成与闭环",
                "reason": "近期重点在协同引擎，需要深度集成形成闭环",
                "priority": 8
            })

        # 基于时间预测 - 如果最近进化间隔较长，可能需要加速
        predictions.append({
            "type": "autonomy",
            "direction": "增强自主进化能力",
            "reason": "增强元进化能力，让进化环更智能",
            "priority": 8
        })

        # 添加创新方向
        predictions.append({
            "type": "innovation",
            "direction": "发现人没想到的新能力",
            "reason": "探索新场景、新组合、新用法",
            "priority": 7
        })

        # 按优先级排序
        predictions.sort(key=lambda x: x.get("priority", 0), reverse=True)

        return predictions[:5]

    def generate_evolution_plan(self, predictions, history):
        """生成进化计划"""
        plan = {
            "generated_at": datetime.now().isoformat(),
            "based_on_rounds": len(history),
            "recommendations": []
        }

        for i, pred in enumerate(predictions):
            plan["recommendations"].append({
                "rank": i + 1,
                "type": pred.get("type"),
                "direction": pred.get("direction"),
                "reason": pred.get("reason"),
                "priority": pred.get("priority")
            })

        return plan

    def get_system_status_summary(self):
        """获取系统状态摘要"""
        # 读取当前任务状态
        current_mission_path = os.path.join(self.state_dir, "current_mission.json")
        status = {}
        if os.path.exists(current_mission_path):
            try:
                with open(current_mission_path, 'r', encoding='utf-8') as f:
                    status = json.load(f)
            except Exception:
                pass

        # 统计引擎数量
        engines_count = 0
        scripts_dir = os.path.join(PROJECT_ROOT, "scripts")
        if os.path.exists(scripts_dir):
            engine_files = [f for f in os.listdir(scripts_dir) if f.endswith('_engine.py') or f.endswith('_enhancer.py') or f.endswith('_planner.py') or f.endswith('_optimizer.py')]
            engines_count = len(engine_files)

        return {
            "current_round": status.get("loop_round", 217),
            "current_phase": status.get("phase", "假设"),
            "engines_count": engines_count,
            "last_goal": status.get("current_goal", "")[:100]
        }

    def get_status(self):
        """获取引擎状态"""
        history = self.get_evolution_history(limit=30)
        efficiency = self.analyze_evolution_efficiency(history)
        patterns = self.detect_evolution_patterns(history)
        system_status = self.get_system_status_summary()
        predictions = self.predict_next_evolution(history, efficiency, patterns)
        plan = self.generate_evolution_plan(predictions, history)

        return {
            "engine": "智能进化预测与主动规划引擎",
            "status": "running",
            "current_round": system_status["current_round"],
            "engines_count": system_status["engines_count"],
            "efficiency_analysis": efficiency,
            "patterns_detected": patterns,
            "predictions": predictions,
            "evolution_plan": plan,
            "system_status": system_status,
            "timestamp": datetime.now().isoformat()
        }


def handle_command(args):
    """处理命令"""
    engine = EvolutionPredictionPlanner()

    if not args:
        # 默认返回状态
        return engine.get_status()

    command = args[0].lower()

    if command == "status":
        return engine.get_status()

    elif command == "analyze":
        history = engine.get_evolution_history(limit=30)
        efficiency = engine.analyze_evolution_efficiency(history)
        patterns = engine.detect_evolution_patterns(history)
        return {
            "history_rounds": len(history),
            "efficiency": efficiency,
            "patterns": patterns
        }

    elif command == "predict":
        history = engine.get_evolution_history(limit=30)
        efficiency = engine.analyze_evolution_efficiency(history)
        patterns = engine.detect_evolution_patterns(history)
        predictions = engine.predict_next_evolution(history, efficiency, patterns)
        return {
            "predictions": predictions
        }

    elif command == "plan":
        history = engine.get_evolution_history(limit=30)
        efficiency = engine.analyze_evolution_efficiency(history)
        patterns = engine.detect_evolution_patterns(history)
        predictions = engine.predict_next_evolution(history, efficiency, patterns)
        plan = engine.generate_evolution_plan(predictions, history)
        return plan

    elif command == "system":
        return engine.get_system_status_summary()

    else:
        return {"error": f"未知命令: {command}", "available_commands": ["status", "analyze", "predict", "plan", "system"]}


def main():
    """主入口"""
    import sys
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    result = handle_command(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()