#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环进化效能智能对话分析与趋势预测引擎

在 round 545 完成的进化效能自动化归因与智能建议引擎基础上，进一步构建智能对话式效能分析
与趋势预测能力。让系统能够用自然语言与用户或系统进行关于进化效能的对话交互，回答关于
进化历史、当前状态、趋势预测、优化建议等问题。

实现从「单向报告」到「交互式对话」的范式升级。

Version: 1.0.0
Author: 进化环自动化
Date: 2026-03-15
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import statistics

# 路径配置
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
RUNTIME_STATE_DIR = PROJECT_ROOT / "runtime" / "state"
RUNTIME_LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"
REFERENCES_DIR = PROJECT_ROOT / "references"


class EvolutionEfficiencyDialogEngine:
    """进化效能智能对话分析与趋势预测引擎"""

    VERSION = "1.0.0"

    def __init__(self):
        """初始化引擎"""
        self.state_dir = RUNTIME_STATE_DIR
        self.logs_dir = RUNTIME_LOGS_DIR
        self.references_dir = REFERENCES_DIR

        # 归因引擎数据路径
        self.attribution_state_path = self.state_dir / "effectiveness_attribution_state.json"

        # 进化历史数据缓存
        self._evolution_history_cache = None
        self._efficiency_data_cache = None

    def load_evolution_history(self) -> List[Dict]:
        """加载进化历史数据"""
        if self._evolution_history_cache is not None:
            return self._evolution_history_cache

        history = []

        # 尝试从归因引擎加载
        if self.attribution_state_path.exists():
            try:
                with open(self.attribution_state_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'history' in data:
                        history = data['history']
            except Exception as e:
                print(f"Warning: 加载归因数据失败: {e}")

        # 补充从 evolution_completed_*.json 文件加载
        completed_files = list(self.state_dir.glob("evolution_completed_*.json"))
        for f in completed_files:
            try:
                with open(f, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 提取关键信息
                    entry = {
                        'round': data.get('loop_round', 0),
                        'goal': data.get('current_goal', ''),
                        'completed': data.get('status') == 'completed',
                        'baseline_result': data.get('baseline_result', ''),
                        'targeted_result': data.get('targeted_result', ''),
                        'timestamp': data.get('timestamp', '')
                    }
                    if entry['round'] > 0 and entry not in history:
                        history.append(entry)
            except Exception as e:
                print(f"Warning: 加载 {f.name} 失败: {e}")

        # 按轮次排序
        history.sort(key=lambda x: x.get('round', 0), reverse=True)

        self._evolution_history_cache = history
        return history

    def load_efficiency_data(self) -> Dict:
        """加载效能数据"""
        if self._efficiency_data_cache is not None:
            return self._efficiency_data_cache

        data = {
            'total_rounds': 0,
            'success_rate': 0.0,
            'avg_completion_time': 0,
            'recent_trends': [],
            'engine_performance': {}
        }

        # 尝试从归因引擎加载
        if self.attribution_state_path.exists():
            try:
                with open(self.attribution_state_path, 'r', encoding='utf-8') as f:
                    attribution_data = json.load(f)
                    data.update(attribution_data)
            except Exception as e:
                print(f"Warning: 加载归因数据失败: {e}")

        # 计算统计信息
        history = self.load_evolution_history()
        if history:
            data['total_rounds'] = len(history)
            completed = sum(1 for h in history if h.get('completed', False))
            if data['total_rounds'] > 0:
                data['success_rate'] = completed / data['total_rounds'] * 100

        self._efficiency_data_cache = data
        return data

    def predict_efficiency_trend(self, rounds_ahead: int = 5) -> Dict:
        """预测效能趋势

        Args:
            rounds_ahead: 预测轮次数

        Returns:
            趋势预测结果
        """
        history = self.load_evolution_history()

        if len(history) < 3:
            return {
                'prediction': '数据不足，无法预测',
                'confidence': 'low',
                'rounds_ahead': rounds_ahead
            }

        # 简单的线性趋势分析
        recent = history[:min(20, len(history))]
        success_counts = []

        for h in reversed(recent):
            success_counts.append(1 if h.get('completed', False) else 0)

        if len(success_counts) >= 3:
            # 计算趋势
            avg_success = statistics.mean(success_counts)

            # 简单预测：基于历史平均值
            trend = 'stable'
            if avg_success > 0.7:
                trend = 'improving'
            elif avg_success < 0.5:
                trend = 'declining'

            return {
                'prediction': f"基于 {len(success_counts)} 轮历史数据，预测未来 {rounds_ahead} 轮将保持 {trend} 趋势",
                'confidence': 'medium' if len(success_counts) >= 10 else 'low',
                'historical_success_rate': round(avg_success * 100, 1),
                'trend': trend,
                'rounds_analyzed': len(success_counts),
                'rounds_ahead': rounds_ahead
            }

        return {
            'prediction': '数据不足以进行趋势预测',
            'confidence': 'low',
            'rounds_ahead': rounds_ahead
        }

    def analyze_recent_performance(self, rounds: int = 10) -> Dict:
        """分析近期性能

        Args:
            rounds: 分析的轮次数

        Returns:
            分析结果
        """
        history = self.load_evolution_history()
        recent = history[:min(rounds, len(history))]

        if not recent:
            return {
                'summary': '无历史数据',
                'rounds_analyzed': 0
            }

        completed = sum(1 for h in recent if h.get('completed', False))
        success_rate = completed / len(recent) * 100 if recent else 0

        # 分析失败原因
        failures = [h for h in recent if not h.get('completed', False)]
        failure_reasons = []

        for f in failures:
            goal = f.get('goal', '')
            if goal:
                # 简单提取关键词
                if '未' in goal or '未完成' in goal:
                    failure_reasons.append('任务未完成')
                elif '失败' in goal:
                    failure_reasons.append('执行失败')
                elif '验证' in goal:
                    failure_reasons.append('验证不通过')
                else:
                    failure_reasons.append('未知原因')

        return {
            'summary': f"最近 {len(recent)} 轮完成 {completed} 轮，成功率 {success_rate:.1f}%",
            'rounds_analyzed': len(recent),
            'completed': completed,
            'failed': len(failures),
            'success_rate': round(success_rate, 1),
            'failure_reasons': failure_reasons[:3] if failure_reasons else [],
            'recent_goals': [h.get('goal', '')[:50] for h in recent[:5]]
        }

    def answer_efficiency_question(self, question: str) -> str:
        """回答关于进化效能的问题

        Args:
            question: 用户问题

        Returns:
            自然语言回答
        """
        question = question.lower()
        data = self.load_efficiency_data()
        history = self.load_evolution_history()

        # 统计信息
        total = data.get('total_rounds', len(history))
        success_rate = data.get('success_rate', 0)

        # 匹配问题类型
        if '多少' in question or '总数' in question or '轮次' in question:
            return f"进化环目前已完成 {total} 轮进化。"

        elif '成功' in question or '完成率' in question:
            return f"进化环整体成功率为 {success_rate:.1f}%。（基于 {total} 轮历史数据）"

        elif '趋势' in question or '预测' in question:
            prediction = self.predict_efficiency_trend()
            return f"效能趋势预测：{prediction['prediction']}（置信度：{prediction['confidence']}）"

        elif '近期' in question or '最近' in question or '表现' in question:
            recent = self.analyze_recent_performance()
            return f"近期表现：{recent['summary']}"

        elif '效率' in question or '效能' in question:
            recent = self.analyze_recent_performance()
            if recent.get('success_rate', 0) >= 70:
                return f"进化效率良好。{recent['summary']}。建议继续保持当前进化策略。"
            elif recent.get('success_rate', 0) >= 50:
                return f"进化效率一般。{recent['summary']}。建议关注失败原因，调整进化策略。"
            else:
                return f"进化效率需要改善。{recent['summary']}。建议暂停新功能开发，优先解决基础问题。"

        elif '问题' in question or '失败' in question:
            recent = self.analyze_recent_performance()
            if recent.get('failure_reasons'):
                reasons = '、'.join(recent['failure_reasons'])
                return f"近期失败原因包括：{reasons}。建议针对性优化。"
            else:
                return "近期无失败记录，所有进化任务均成功完成。"

        elif '建议' in question or '优化' in question:
            recent = self.analyze_recent_performance()
            if recent.get('success_rate', 0) >= 70:
                return "当前状态良好，可以继续推进新功能进化。建议：1) 保持当前策略；2) 关注长期可持续发展；3) 定期进行健康检查。"
            elif recent.get('success_rate', 0) >= 50:
                return "需要关注效率提升。建议：1) 分析失败原因；2) 简化进化目标；3) 加强验证环节；4) 考虑降低任务复杂度。"
            else:
                return "建议暂停新功能开发。建议：1) 优先解决系统稳定性问题；2) 进行全面健康检查；3) 修复已知问题后再继续进化。"

        elif '历史' in question or '过去' in question:
            recent = self.analyze_recent_performance(rounds=20)
            return f"过去 20 轮：{recent['summary']}。"

        else:
            # 默认返回综合信息
            recent = self.analyze_recent_performance()
            prediction = self.predict_efficiency_trend()
            return f"进化效能概览：{recent['summary']}。趋势预测：{prediction['prediction']}。"

    def generate_efficiency_report(self) -> str:
        """生成进化效能报告（自然语言）"""
        data = self.load_efficiency_data()
        recent = self.analyze_recent_performance()
        prediction = self.predict_efficiency_trend()

        report = f"""# 进化效能智能分析报告

## 总体统计
- 总进化轮次：{data.get('total_rounds', 0)} 轮
- 整体成功率：{data.get('success_rate', 0):.1f}%

## 近期表现（最近 10 轮）
{recent['summary']}
- 完成：{recent.get('completed', 0)} 轮
- 失败：{recent.get('failed', 0)} 轮
- 成功率：{recent.get('success_rate', 0):.1f}%

## 趋势预测
{prediction['prediction']}
- 置信度：{prediction.get('confidence', 'unknown')}
- 预测依据：{prediction.get('rounds_analyzed', 0)} 轮历史数据

## 优化建议
"""
        if recent.get('success_rate', 0) >= 70:
            report += """1. 当前状态良好，建议继续保持
2. 可以适度增加进化任务的复杂性
3. 定期进行系统健康检查以维持良好状态"""
        elif recent.get('success_rate', 0) >= 50:
            report += """1. 需要关注效率提升
2. 建议简化部分复杂进化任务
3. 加强验证环节，减少失败风险"""
        else:
            report += """1. 建议优先解决系统稳定性问题
2. 暂停新功能开发，进行全面检修
3. 修复已知问题后再继续进化"""

        return report

    def get_cockpit_data(self) -> Dict:
        """获取驾驶舱数据接口

        Returns:
            驾驶舱展示用数据
        """
        data = self.load_efficiency_data()
        recent = self.analyze_recent_performance()
        prediction = self.predict_efficiency_trend()

        return {
            'total_rounds': data.get('total_rounds', 0),
            'success_rate': data.get('success_rate', 0),
            'recent_success_rate': recent.get('success_rate', 0),
            'trend': prediction.get('trend', 'unknown'),
            'confidence': prediction.get('confidence', 'unknown'),
            'summary': recent.get('summary', ''),
            'timestamp': datetime.now().isoformat()
        }

    def interactive_dialog(self, user_input: str) -> str:
        """交互式对话接口

        Args:
            user_input: 用户输入

        Returns:
            回答
        """
        # 清理输入
        user_input = user_input.strip()

        if not user_input:
            return "请输入关于进化效能的问题，例如：\n- 进化了多少轮？\n- 成功率是多少？\n- 近期表现如何？\n- 有什么优化建议？"

        # 回答问题
        return self.answer_efficiency_question(user_input)


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(
        description='进化效能智能对话分析与趋势预测引擎'
    )
    parser.add_argument(
        '--ask', '-a',
        type=str,
        help='用自然语言提问关于进化效能的问题'
    )
    parser.add_argument(
        '--report', '-r',
        action='store_true',
        help='生成进化效能报告'
    )
    parser.add_argument(
        '--predict', '-p',
        type=int,
        default=5,
        nargs='?',
        const=5,
        help='预测未来N轮效能趋势（默认5轮）'
    )
    parser.add_argument(
        '--recent', '-n',
        type=int,
        default=10,
        help='分析最近N轮表现（默认10轮）'
    )
    parser.add_argument(
        '--cockpit-data',
        action='store_true',
        help='获取驾驶舱数据接口'
    )
    parser.add_argument(
        '--version',
        action='store_true',
        help='显示版本信息'
    )

    args = parser.parse_args()

    engine = EvolutionEfficiencyDialogEngine()

    # 显示版本
    if args.version:
        print(f"evolution_efficiency_dialog_analysis_engine.py v{engine.VERSION}")
        return

    # 问答模式
    if args.ask:
        result = engine.interactive_dialog(args.ask)
        print(result)
        return

    # 生成报告
    if args.report:
        print(engine.generate_efficiency_report())
        return

    # 预测模式
    if args.predict:
        prediction = engine.predict_efficiency_trend(args.predict)
        print(f"趋势预测：{prediction['prediction']}")
        print(f"置信度：{prediction['confidence']}")
        return

    # 近期分析
    if args.recent:
        recent = engine.analyze_recent_performance(args.recent)
        print(recent['summary'])
        return

    # 驾驶舱数据
    if args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    # 默认显示帮助
    parser.print_help()


if __name__ == "__main__":
    main()