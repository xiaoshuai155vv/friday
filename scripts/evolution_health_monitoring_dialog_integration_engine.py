#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环健康监测-效能对话深度集成引擎

将 round 547 的系统性健康持续监测与预警增强引擎与 round 546 的进化效能智能对话分析引擎
深度集成，实现从"监测预警"到"对话交互"的完整闭环。让用户能够通过自然语言对话了解健康状态、
效能问题、预警信息，并获得智能优化建议。系统能够根据健康监测数据自动生成效能对话内容，
实现主动健康管理。

实现从「监测预警」到「对话交互」的完整闭环。

Version: 1.0.0
Author: 进化环自动化
Date: 2026-03-15
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

# 路径配置
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

# 导入集成引擎
from evolution_systematic_health_monitoring_engine import EvolutionSystematicHealthMonitoringEngine
from evolution_efficiency_dialog_analysis_engine import EvolutionEfficiencyDialogEngine


class EvolutionHealthMonitoringDialogIntegrationEngine:
    """健康监测-效能对话深度集成引擎"""

    VERSION = "1.0.0"

    def __init__(self):
        """初始化引擎"""
        # 初始化两个集成引擎
        self.health_engine = EvolutionSystematicHealthMonitoringEngine()
        self.dialog_engine = EvolutionEfficiencyDialogEngine()

        # 集成状态文件路径
        self.state_dir = PROJECT_ROOT / "runtime" / "state"
        self.integration_state_path = self.state_dir / "health_dialog_integration_state.json"

    def get_health_status_for_dialog(self) -> Dict:
        """获取适合对话展示的健康状态

        Returns:
            对话友好的健康状态数据
        """
        # 获取健康状态
        health_status = self.health_engine.get_systematic_health_status()

        # 获取趋势预测
        trend = self.health_engine.predict_health_trend()

        # 获取预警
        warnings = self.health_engine.generate_enhanced_warnings()

        return {
            'health_score': health_status.get('overall_health_score', 0),
            'health_level': health_status.get('health_level', 'unknown'),
            'trend': trend,
            'warnings': warnings,
            'dimensions': health_status.get('dimensions', {}),
            'current_round': health_status.get('current_round', 0),
            'total_rounds': health_status.get('total_evolution_rounds', 0)
        }

    def generate_health_dialog_report(self) -> str:
        """生成健康监测对话报告

        Returns:
            自然语言健康报告
        """
        # 获取健康数据
        health_data = self.get_health_status_for_dialog()

        # 构建报告
        report_lines = [
            "# 健康监测对话报告",
            "",
            f"**当前健康评分**: {health_data['health_score']} ({health_data['health_level']})",
            f"**当前进化轮次**: Round {health_data['current_round']}",
            f"**历史进化轮数**: {health_data['total_rounds']} 轮",
            ""
        ]

        # 趋势分析
        trend = health_data.get('trend', {})
        if trend:
            report_lines.extend([
                "## 健康趋势",
                f"- 趋势方向: {trend.get('trend_direction', 'unknown')}",
                f"- 趋势预测: {trend.get('prediction', '无')}",
                f"- 预测置信度: {trend.get('confidence', 'unknown')}",
                ""
            ])

        # 预警信息
        warnings = health_data.get('warnings', [])
        if warnings:
            report_lines.append("## 活跃预警")
            for w in warnings:
                level_emoji = "[CRIT]" if w.get('level') == 'critical' else "[WARN]"
                report_lines.append(f"- {level_emoji} [{w.get('level', 'unknown').upper()}] {w.get('message', '')}")
            report_lines.append("")
        else:
            report_lines.extend([
                "## 预警状态",
                "✅ 当前无活跃预警",
                ""
            ])

        # 维度健康度
        dimensions = health_data.get('dimensions', {})
        if dimensions:
            report_lines.append("## 各维度健康度")
            for dim_name, dim_data in dimensions.items():
                if isinstance(dim_data, dict):
                    score = dim_data.get('score', 0)
                    level = dim_data.get('level', 'unknown')
                    desc = dim_data.get('description', '')
                    level_emoji = "[OK]" if level in ['excellent', 'good'] else ("[WARN]" if level == 'fair' else "[CRIT]")
                    report_lines.append(f"- {level_emoji} {dim_name}: {score} ({level}) - {desc}")
            report_lines.append("")

        # 效能信息
        efficiency_data = self.dialog_engine.load_efficiency_data()
        report_lines.extend([
            "## 进化效能",
            f"- 总进化轮次: {efficiency_data.get('total_rounds', 0)} 轮",
            f"- 整体成功率: {efficiency_data.get('success_rate', 0):.1f}%",
            ""
        ])

        return "\n".join(report_lines)

    def answer_health_question(self, question: str) -> str:
        """回答关于健康监测的问题

        Args:
            question: 用户问题

        Returns:
            自然语言回答
        """
        question_lower = question.lower()
        health_data = self.get_health_status_for_dialog()

        # 问题匹配
        if '健康' in question or '状态' in question or '评分' in question:
            score = health_data.get('health_score', 0)
            level = health_data.get('health_level', 'unknown')
            level_desc = {
                'excellent': '优秀',
                'good': '良好',
                'fair': '一般',
                'poor': '较差',
                'critical': '危险'
            }.get(level, level)

            return f"当前系统健康评分为 {score}（{level_desc}）。健康等级基于多维度综合评估（执行健康、知识健康、效能健康、创新健康）计算得出。"

        elif '预警' in question or '警告' in question:
            warnings = health_data.get('warnings', [])
            if not warnings:
                return "当前没有活跃预警，系统运行状态良好。"
            else:
                response = "当前有以下活跃预警：\n"
                for w in warnings:
                    level = w.get('level', '').upper()
                    msg = w.get('message', '')
                    response += f"- [{level}] {msg}\n"
                return response

        elif '趋势' in question or '预测' in question:
            trend = health_data.get('trend', {})
            prediction = trend.get('prediction', '无法预测')
            direction = trend.get('trend_direction', 'unknown')
            confidence = trend.get('confidence', 'unknown')

            direction_desc = {
                'improving': '上升',
                'declining': '下降',
                'stable': '稳定'
            }.get(direction, direction)

            return f"健康趋势预测：{prediction}。趋势方向：{direction_desc}（置信度：{confidence}）"

        elif '维度' in question or '各维' in question:
            dimensions = health_data.get('dimensions', {})
            if not dimensions:
                return "暂无维度健康数据"

            response = "各维度健康状况：\n"
            for dim_name, dim_data in dimensions.items():
                if isinstance(dim_data, dict):
                    score = dim_data.get('score', 0)
                    level = dim_data.get('level', 'unknown')
                    level_emoji = "[OK]" if level in ['excellent', 'good'] else ("[WARN]" if level == 'fair' else "[CRIT]")
                    response += f"- {level_emoji} {dim_name}: {score} 分 ({level})\n"
            return response

        elif '效能' in question or '效率' in question:
            return self.dialog_engine.answer_efficiency_question(question)

        elif '建议' in question or '优化' in question:
            score = health_data.get('health_score', 0)
            warnings = health_data.get('warnings', [])

            if score >= 90:
                return "系统健康状况优秀！建议：1) 继续保持当前策略；2) 可以尝试更复杂的进化任务；3) 定期进行健康监测保持良好状态。"
            elif score >= 75:
                return "系统健康状况良好。建议：1) 关注各维度健康平衡；2) 保持当前进化节奏；3) 定期检查预警信息。"
            elif score >= 60:
                return "系统健康状况一般。建议：1) 关注健康分下降原因；2) 简化复杂进化任务；3) 加强验证环节。"
            else:
                response = "系统健康状况需要关注。优化建议：\n"
                response += "1. 建议执行全面健康诊断\n"
                response += "2. 暂停复杂新功能开发\n"
                response += "3. 优先处理活跃预警\n"
                response += "4. 简化进化目标，确保质量"
                return response

        elif '多少' in question or '轮次' in question:
            return f"进化环目前已完成 {health_data['total_rounds']} 轮进化，当前处于 Round {health_data['current_round']}。"

        else:
            # 默认返回综合信息
            return self.generate_health_dialog_report()

    def interactive_dialog(self, user_input: str) -> str:
        """交互式对话接口

        Args:
            user_input: 用户输入

        Returns:
            回答
        """
        user_input = user_input.strip()

        if not user_input:
            return "请输入关于健康监测的问题，例如：\n- 当前健康状态如何？\n- 有哪些预警？\n- 健康趋势怎么样？\n- 有什么优化建议？\n- 进化效能如何？"

        # 回答健康相关问题
        return self.answer_health_question(user_input)

    def get_integrated_warnings_with_dialog(self) -> List[Dict]:
        """获取带有对话式描述的预警

        Returns:
            带有对话描述的预警列表
        """
        # 获取基础预警
        warnings = self.health_engine.generate_enhanced_warnings()

        # 为每个预警添加对话描述
        for warning in warnings:
            warning_type = warning.get('type', '')
            level = warning.get('level', '')

            if warning_type == 'health_score':
                warning['dialog_message'] = f"健康评分需要关注：{warning.get('message', '')}。建议查看详细健康报告了解详情。"
            elif warning_type == 'success_rate':
                warning['dialog_message'] = f"进化成功率偏低：{warning.get('message', '')}。建议分析失败原因并调整策略。"
            elif warning_type == 'health_trend':
                warning['dialog_message'] = f"健康趋势预警：{warning.get('message', '')}。建议关注趋势变化。"

            # 添加行动建议
            if level == 'critical':
                warning['action_suggestions'] = [
                    "建议立即查看详细健康报告",
                    "考虑执行健康诊断和自愈流程",
                    "降低进化频率确保质量"
                ]
            elif level == 'warning':
                warning['action_suggestions'] = [
                    "建议关注健康变化趋势",
                    "可以查看优化建议",
                    "保持当前监测频率"
                ]

        return warnings

    def generate_proactive_health_notification(self) -> str:
        """生成主动健康通知（用于预警驱动）

        Returns:
            主动通知内容
        """
        warnings = self.get_integrated_warnings_with_dialog()

        if not warnings:
            return None

        # 筛选需要主动通知的预警
        critical_warnings = [w for w in warnings if w.get('action_required', False)]

        if not critical_warnings:
            return None

        # 生成通知
        notification = "# 🚨 健康监测主动通知\n\n"

        for w in critical_warnings:
            notification += f"## {w.get('type', 'warning').upper()} 预警\n"
            notification += f"{w.get('message', '')}\n\n"

            if 'dialog_message' in w:
                notification += f"解读：{w['dialog_message']}\n\n"

            if 'action_suggestions' in w:
                notification += "建议行动：\n"
                for suggestion in w['action_suggestions']:
                    notification += f"- {suggestion}\n"
                notification += "\n"

        return notification

    def get_cockpit_data(self) -> Dict:
        """获取驾驶舱数据接口

        Returns:
            驾驶舱展示用数据
        """
        # 获取健康引擎数据
        health_cockpit = self.health_engine.get_cockpit_data()

        # 获取对话引擎数据
        dialog_cockpit = self.dialog_engine.get_cockpit_data()

        # 整合数据
        return {
            'health_score': health_cockpit.get('health_score', 0),
            'health_level': health_cockpit.get('health_level', 'unknown'),
            'trend_direction': health_cockpit.get('trend_direction', 'stable'),
            'warnings_count': health_cockpit.get('warnings_count', 0),
            'critical_warnings': health_cockpit.get('critical_warnings', []),
            'total_rounds': dialog_cockpit.get('total_rounds', 0),
            'success_rate': dialog_cockpit.get('success_rate', 0),
            'recent_success_rate': dialog_cockpit.get('recent_success_rate', 0),
            'integration_status': 'active',
            'timestamp': datetime.now().isoformat()
        }


def main():
    """主函数：命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description='智能全场景进化环健康监测-效能对话深度集成引擎'
    )
    parser.add_argument(
        '--ask', '-a',
        type=str,
        help='用自然语言提问关于健康监测的问题'
    )
    parser.add_argument(
        '--report', '-r',
        action='store_true',
        help='生成健康监测对话报告'
    )
    parser.add_argument(
        '--warnings', '-w',
        action='store_true',
        help='获取带有对话描述的预警'
    )
    parser.add_argument(
        '--notify', '-n',
        action='store_true',
        help='生成主动健康通知'
    )
    parser.add_argument(
        '--status', '-s',
        action='store_true',
        help='获取健康状态'
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

    engine = EvolutionHealthMonitoringDialogIntegrationEngine()

    # 显示版本
    if args.version:
        print(f"evolution_health_monitoring_dialog_integration_engine.py v{engine.VERSION}")
        return

    # 问答模式
    if args.ask:
        result = engine.interactive_dialog(args.ask)
        print(result)
        return

    # 生成报告
    if args.report:
        print(engine.generate_health_dialog_report())
        return

    # 获取预警
    if args.warnings:
        warnings = engine.get_integrated_warnings_with_dialog()
        print(json.dumps(warnings, ensure_ascii=False, indent=2))
        return

    # 主动通知
    if args.notify:
        notification = engine.generate_proactive_health_notification()
        if notification:
            print(notification)
        else:
            print("当前无需主动通知")
        return

    # 获取状态
    if args.status:
        status = engine.get_health_status_for_dialog()
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return

    # 驾驶舱数据
    if args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    # 默认显示帮助
    parser.print_help()


if __name__ == '__main__':
    main()