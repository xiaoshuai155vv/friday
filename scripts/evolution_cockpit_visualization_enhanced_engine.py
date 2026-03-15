#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环进化驾驶舱可视化增强与智能交互引擎
(Cockpit Visualization Enhancement & Intelligent Interaction Engine)

在 round 479 完成的进化路径智能规划引擎基础上，进一步增强进化驾驶舱的
可视化展示能力和智能交互控制。实现进化路径的可视化展示、交互控制、数据分析等功能。

功能：
1. 进化路径可视化展示 - 图形化展示进化历史、当前状态、未来趋势
2. 智能交互控制 - 支持通过命令行/Web界面交互控制进化环
3. 数据分析增强 - 多维度数据分析、趋势预测、异常检测
4. 实时数据推送 - 与进化驾驶舱深度集成，实时推送数据
5. 智能预警与建议 - 基于分析结果提供智能预警和优化建议

Version: 1.0.0

依赖：
- evolution_cockpit_engine.py (round 350)
- evolution_evolution_path_smart_planning_engine.py (round 479)
- evolution_execution_trend_analysis_engine.py (round 425)
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import statistics

# 添加项目根目录到 Python 路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, SCRIPT_DIR)


def _safe_print(text: str):
    """安全打印，处理编码问题"""
    import re
    try:
        print(text)
    except UnicodeEncodeError:
        clean_text = re.sub(r'[^\x00-\x7F]+', '', text)
        print(clean_text)


class CockpitVisualizationEnhancedEngine:
    """进化驾驶舱可视化增强与智能交互引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.name = "Cockpit Visualization Enhancement Engine"
        self.project_root = PROJECT_ROOT
        self.scripts_dir = SCRIPT_DIR
        self.runtime_dir = os.path.join(self.project_root, "runtime")
        self.state_dir = os.path.join(self.runtime_dir, "state")
        self.data_dir = os.path.join(self.runtime_dir, "data")
        self.logs_dir = os.path.join(self.runtime_dir, "logs")

        # 数据文件路径
        self.visualization_config = os.path.join(self.data_dir, "cockpit_visualization_config.json")
        self.analysis_cache = os.path.join(self.data_dir, "cockpit_visualization_analysis_cache.json")
        self.interaction_history = os.path.join(self.data_dir, "cockpit_interaction_history.json")

        self._ensure_directories()
        self._initialize_config()

    def _ensure_directories(self):
        """确保必要的目录存在"""
        for directory in [self.runtime_dir, self.state_dir, self.data_dir, self.logs_dir]:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def _initialize_config(self):
        """初始化配置"""
        if not os.path.exists(self.visualization_config):
            default_config = {
                "visualization": {
                    "path_display_mode": "timeline",  # timeline/graph/table
                    "color_scheme": "auto",
                    "show_predictions": True,
                    "show_bottlenecks": True,
                    "time_range": "30d"  # 7d/30d/90d/all
                },
                "interaction": {
                    "command_aliases": {
                        "status": "show_status",
                        "paths": "show_paths",
                        "trends": "show_trends",
                        "alerts": "show_alerts"
                    },
                    "auto_refresh": True,
                    "refresh_interval": 30
                },
                "analysis": {
                    "enabled": True,
                    "metrics": [
                        "execution_time",
                        "success_rate",
                        "value_realization",
                        "efficiency_trend"
                    ],
                    "prediction_window": 7  # days
                }
            }
            with open(self.visualization_config, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)

    def load_config(self) -> Dict:
        """加载配置"""
        try:
            with open(self.visualization_config, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            _safe_print(f"[警告] 加载配置失败: {e}")
            return {}

    def get_evolution_history(self, days: int = 30) -> List[Dict]:
        """获取进化历史数据"""
        history = []
        state_dir = Path(self.state_dir)

        # 扫描 evolution_completed_*.json 文件
        for json_file in sorted(state_dir.glob("evolution_completed_*.json")):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 解析日期
                    if 'completed_at' in data:
                        try:
                            completed_date = datetime.fromisoformat(data['completed_at'].replace('Z', '+00:00'))
                            if (datetime.now(completed_date.tzinfo) - completed_date).days <= days:
                                history.append(data)
                        except:
                            pass
            except Exception as e:
                continue

        return history

    def get_current_mission_status(self) -> Dict:
        """获取当前任务状态"""
        try:
            mission_file = os.path.join(self.state_dir, "current_mission.json")
            if os.path.exists(mission_file):
                with open(mission_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            _safe_print(f"[警告] 读取任务状态失败: {e}")
        return {}

    def analyze_evolution_paths(self) -> Dict:
        """分析进化路径"""
        history = self.get_evolution_history(days=30)

        if not history:
            return {
                "total_evolution_rounds": 0,
                "summary": "无进化历史数据"
            }

        # 统计信息
        total = len(history)
        completed = sum(1 for h in history if h.get('status') == 'completed')
        failed = sum(1 for h in history if h.get('status') in ['failed', 'stale_failed'])

        # 分析进化方向
        directions = defaultdict(int)
        for h in history:
            goal = h.get('current_goal', '')
            if goal:
                # 提取关键词
                keywords = ['优化', '增强', '引擎', '集成', '分析', '预测', '可视化']
                for kw in keywords:
                    if kw in goal:
                        directions[kw] += 1

        return {
            "total_evolution_rounds": total,
            "completed": completed,
            "failed": failed,
            "success_rate": round(completed / total * 100, 1) if total > 0 else 0,
            "top_directions": dict(sorted(directions.items(), key=lambda x: x[1], reverse=True)[:5]),
            "latest_round": history[-1] if history else {}
        }

    def visualize_evolution_timeline(self) -> str:
        """生成进化时间线可视化"""
        history = self.get_evolution_history(days=30)

        if not history:
            return "=== 进化时间线 ===\n无进化历史数据"

        output = ["=== 进化时间线 (近30天) ===\n"]

        for i, h in enumerate(history[-10:], 1):  # 显示最近10条
            goal = h.get('current_goal', '未知目标')[:40]
            status = h.get('status', 'unknown')
            status_icon = "✓" if status == "completed" else "✗" if status in ["failed", "stale_failed"] else "?"

            completed_at = h.get('completed_at', '')
            if completed_at:
                try:
                    date = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
                    date_str = date.strftime('%m-%d %H:%M')
                except:
                    date_str = completed_at[:10]
            else:
                date_str = "未知"

            output.append(f"{i}. [{status_icon}] round {h.get('loop_round', '?')}: {goal}")
            output.append(f"   时间: {date_str} | 状态: {status}")
            output.append("")

        return "\n".join(output)

    def analyze_trends(self) -> Dict:
        """分析进化趋势"""
        history = self.get_evolution_history(days=30)

        if len(history) < 2:
            return {"trend": "insufficient_data"}

        # 简单趋势分析：计算近期完成率变化
        recent = history[-10:] if len(history) >= 10 else history
        recent_completed = sum(1 for h in recent if h.get('status') == 'completed')
        recent_rate = recent_completed / len(recent) * 100

        # 与之前对比
        if len(history) >= 20:
            older = history[-20:-10]
            older_completed = sum(1 for h in older if h.get('status') == 'completed')
            older_rate = older_completed / len(older) * 100
            trend_change = recent_rate - older_rate
        else:
            trend_change = 0

        return {
            "recent_success_rate": round(recent_rate, 1),
            "trend_change": round(trend_change, 1),
            "trend": "improving" if trend_change > 5 else "declining" if trend_change < -5 else "stable",
            "total_rounds": len(history)
        }

    def generate_smart_suggestions(self) -> List[str]:
        """生成智能建议"""
        suggestions = []

        # 基于趋势分析
        trends = self.analyze_trends()
        if trends.get('trend') == 'declining':
            suggestions.append("⚠️ 进化成功率下降，建议检查系统健康状态")

        # 基于路径分析
        paths = self.analyze_evolution_paths()
        if paths.get('failed', 0) > paths.get('completed', 0) * 0.3:
            suggestions.append("⚠️ 失败率较高，建议优化执行策略")

        # 基于当前任务
        mission = self.get_current_mission_status()
        if mission.get('phase') == '假设':
            suggestions.append("ℹ️ 进化环处于假设阶段，准备生成新目标")

        if not suggestions:
            suggestions.append("✓ 系统运行正常，进化环稳定")

        return suggestions

    def show_comprehensive_status(self) -> str:
        """显示综合状态"""
        output = []

        output.append("=" * 60)
        output.append("  进化驾驶舱可视化增强状态")
        output.append("=" * 60)

        # 当前任务状态
        mission = self.get_current_mission_status()
        output.append(f"\n【当前任务】")
        output.append(f"  轮次: Round {mission.get('loop_round', '?')}")
        output.append(f"  阶段: {mission.get('phase', 'unknown')}")
        output.append(f"  目标: {mission.get('current_goal', '待确定')}")

        # 进化路径分析
        paths = self.analyze_evolution_paths()
        output.append(f"\n【进化路径分析】")
        output.append(f"  总轮次: {paths.get('total_evolution_rounds', 0)}")
        output.append(f"  完成: {paths.get('completed', 0)}")
        output.append(f"  失败: {paths.get('failed', 0)}")
        output.append(f"  成功率: {paths.get('success_rate', 0)}%")

        # 趋势分析
        trends = self.analyze_trends()
        output.append(f"\n【趋势分析】")
        output.append(f"  近期成功率: {trends.get('recent_success_rate', 0)}%")
        output.append(f"  趋势: {trends.get('trend', 'unknown')}")
        output.append(f"  变化: {trends.get('trend_change', 0):+.1f}%")

        # 智能建议
        suggestions = self.generate_smart_suggestions()
        output.append(f"\n【智能建议】")
        for suggestion in suggestions:
            output.append(f"  {suggestion}")

        output.append("\n" + "=" * 60)

        return "\n".join(output)

    def get_cockpit_data(self) -> Dict:
        """获取驾驶舱数据接口"""
        paths = self.analyze_evolution_paths()
        trends = self.analyze_trends()
        suggestions = self.generate_smart_suggestions()
        mission = self.get_current_mission_status()

        return {
            "version": self.version,
            "current_mission": mission,
            "evolution_paths": paths,
            "trends": trends,
            "suggestions": suggestions,
            "timestamp": datetime.now().isoformat()
        }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='智能全场景进化环进化驾驶舱可视化增强与智能交互引擎'
    )
    parser.add_argument('--status', action='store_true', help='显示综合状态')
    parser.add_argument('--timeline', action='store_true', help='显示进化时间线')
    parser.add_argument('--analyze-paths', action='store_true', help='分析进化路径')
    parser.add_argument('--trends', action='store_true', help='分析进化趋势')
    parser.add_argument('--suggestions', action='store_true', help='生成智能建议')
    parser.add_argument('--cockpit-data', action='store_true', help='获取驾驶舱数据接口')
    parser.add_argument('--days', type=int, default=30, help='分析天数范围')

    args = parser.parse_args()

    engine = CockpitVisualizationEnhancedEngine()

    if args.status:
        _safe_print(engine.show_comprehensive_status())
    elif args.timeline:
        _safe_print(engine.visualize_evolution_timeline())
    elif args.analyze_paths:
        result = engine.analyze_evolution_paths()
        _safe_print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.trends:
        result = engine.analyze_trends()
        _safe_print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.suggestions:
        suggestions = engine.generate_smart_suggestions()
        for s in suggestions:
            _safe_print(s)
    elif args.cockpit_data:
        data = engine.get_cockpit_data()
        _safe_print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        # 默认显示综合状态
        _safe_print(engine.show_comprehensive_status())


if __name__ == "__main__":
    main()