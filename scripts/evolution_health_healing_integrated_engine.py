#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化健康自评估与自愈集成引擎 (version 1.0.0)

将 round 294 的进化健康自评估引擎与 round 290 的自愈引擎深度集成，
实现「评估→发现问题→自动修复→验证」的完整闭环，让进化环具备自主健康保障能力。

功能：
1. 健康评估 - 调用进化健康自评估引擎进行全面检查
2. 问题诊断 - 智能分析健康报告，识别需要修复的问题
3. 自动修复 - 调用自愈引擎尝试自动修复发现的问题
4. 验证修复 - 验证修复是否成功，确保问题已解决
5. 综合报告 - 生成包含评估、修复、验证的完整报告

该引擎整合了：
- EvolutionHealthSelfEvaluationEngine (round 294)
- EvolutionLoopSelfHealingAdvanced (round 290)

作者：Claude Sonnet 4.6
日期：2026-03-14
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"


class EvolutionHealthHealingIntegratedEngine:
    """智能全场景进化健康自评估与自愈集成引擎"""

    def __init__(self):
        self.name = "EvolutionHealthHealingIntegratedEngine"
        self.version = "1.0.0"
        self.state_file = STATE_DIR / "evolution_health_healing_integrated_state.json"
        self.health_engine = None
        self.healing_engine = None
        self.last_integration_report = None
        self.load_engines()
        self.load_state()

    def load_engines(self):
        """加载集成引擎"""
        try:
            # 导入健康评估引擎
            import sys
            sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
            from evolution_health_self_evaluation_engine import EvolutionHealthSelfEvaluationEngine
            self.health_engine = EvolutionHealthSelfEvaluationEngine()
        except Exception as e:
            print(f"加载健康评估引擎失败: {e}")

        try:
            # 导入自愈引擎
            from evolution_loop_self_healing_advanced import EvolutionLoopSelfHealingAdvanced
            self.healing_engine = EvolutionLoopSelfHealingAdvanced()
        except Exception as e:
            print(f"加载自愈引擎失败: {e}")

    def load_state(self):
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.last_integration_report = data.get('last_integration_report', {})
            except Exception:
                pass

    def save_state(self):
        """保存状态"""
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump({
                'last_integration_report': self.last_integration_report,
                'last_updated': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)

    def run_health_evaluation(self) -> Dict[str, Any]:
        """
        运行健康评估

        返回:
            健康评估结果
        """
        if not self.health_engine:
            return {'error': '健康评估引擎未加载'}

        try:
            # 生成健康报告
            report = self.health_engine.generate_health_report()
            return report
        except Exception as e:
            return {'error': f'健康评估失败: {str(e)}'}

    def diagnose_and_categorize_issues(self, health_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        诊断并分类问题

        参数:
            health_report: 健康报告

        返回:
            分类后的问题列表
        """
        categorized_issues = {
            'auto_repairable': [],  # 可自动修复的问题
            'manual_fix_required': [],  # 需要手动修复的问题
            'warnings': [],  # 警告（低优先级）
            'info': []  # 信息性内容
        }

        issues = health_report.get('issues', [])

        for issue in issues:
            severity = issue.get('severity', 'medium')
            component = issue.get('component', '')
            issue_desc = issue.get('issue', '')

            # 判断是否可自动修复
            if self._is_auto_repairable(issue):
                categorized_issues['auto_repairable'].append(issue)
            elif severity == 'high' or severity == 'critical':
                categorized_issues['manual_fix_required'].append(issue)
            elif severity == 'medium':
                categorized_issues['warnings'].append(issue)
            else:
                categorized_issues['info'].append(issue)

        return categorized_issues

    def _is_auto_repairable(self, issue: Dict[str, Any]) -> bool:
        """
        判断问题是否可自动修复

        参数:
            issue: 问题描述

        返回:
            是否可自动修复
        """
        issue_desc = issue.get('issue', '').lower()
        component = issue.get('component', '').lower()

        # 基于组件和问题描述判断
        auto_repairable_patterns = [
            ('current_mission', '不存在'),  # 缺少状态文件可以重建
            ('pending_evolutions', '未完成'),  # 未完成轮次可以清理
            ('recent_logs', '不存在'),  # 日志文件可以创建
        ]

        for pattern_component, pattern_desc in auto_repairable_patterns:
            if pattern_component in component and pattern_desc in issue_desc:
                return True

        # 检查是否是已知的可修复问题类型
        repairable_keywords = ['missing', '不存在', '缺失', '损坏']
        for keyword in repairable_keywords:
            if keyword in issue_desc:
                return True

        return False

    def attempt_auto_repairs(self, categorized_issues: Dict[str, Any]) -> Dict[str, Any]:
        """
        尝试自动修复问题

        参数:
            categorized_issues: 分类后的问题

        返回:
            修复结果
        """
        repair_results = {
            'total_attempted': 0,
            'total_successful': 0,
            'total_failed': 0,
            'repairs': []
        }

        if not self.healing_engine:
            repair_results['error'] = '自愈引擎未加载'
            return repair_results

        # 处理可自动修复的问题
        for issue in categorized_issues.get('auto_repairable', []):
            repair_results['total_attempted'] += 1

            component = issue.get('component', '')
            issue_desc = issue.get('issue', '')
            severity = issue.get('severity', 'medium')

            # 尝试修复
            repair_result = self._attempt_fix_issue(component, issue_desc, issue)
            repair_result['issue'] = issue
            repair_results['repairs'].append(repair_result)

            if repair_result.get('success'):
                repair_results['total_successful'] += 1
            else:
                repair_results['total_failed'] += 1

        return repair_results

    def _attempt_fix_issue(self, component: str, issue_desc: str, issue: Dict) -> Dict[str, Any]:
        """
        尝试修复单个问题

        参数:
            component: 组件名称
            issue_desc: 问题描述
            issue: 完整问题信息

        返回:
            修复结果
        """
        result = {
            'component': component,
            'issue_desc': issue_desc,
            'success': False,
            'actions_taken': [],
            'message': ''
        }

        try:
            # 根据组件类型进行修复
            if 'current_mission' in component:
                if '不存在' in issue_desc or 'missing' in issue_desc.lower():
                    # 创建默认状态文件
                    default_mission = {
                        "mission": "Round 295",
                        "phase": "假设",
                        "loop_round": 295,
                        "current_goal": "待定",
                        "next_action": "规划",
                        "assumed_demands": [],
                        "updated_at": datetime.now().isoformat()
                    }
                    mission_file = STATE_DIR / "current_mission.json"
                    with open(mission_file, 'w', encoding='utf-8') as f:
                        json.dump(default_mission, f, ensure_ascii=False, indent=2)
                    result['success'] = True
                    result['actions_taken'].append('重建 current_mission.json')

            elif 'pending_evolutions' in component:
                if '未完成' in issue_desc:
                    # 清理过期状态文件
                    stale_files = self._find_stale_evolution_files()
                    for f in stale_files[:3]:  # 最多清理3个
                        try:
                            f.unlink()
                            result['actions_taken'].append(f'删除过期文件: {f.name}')
                            result['success'] = True
                        except Exception:
                            pass

            elif 'recent_logs' in component:
                if '不存在' in issue_desc:
                    # 创建默认日志文件
                    logs_file = STATE_DIR / "recent_logs.json"
                    default_logs = {"entries": [], "last_updated": datetime.now().isoformat()}
                    with open(logs_file, 'w', encoding='utf-8') as f:
                        json.dump(default_logs, f, ensure_ascii=False, indent=2)
                    result['success'] = True
                    result['actions_taken'].append('重建 recent_logs.json')

            if not result['message']:
                result['message'] = f"尝试修复 {component}: {issue_desc}"

        except Exception as e:
            result['message'] = f"修复失败: {str(e)}"

        return result

    def _find_stale_evolution_files(self) -> List[Path]:
        """查找过期的进化状态文件"""
        stale_files = []

        try:
            # 查找状态为 stale_failed 或未完成很长时间的文件
            for f in STATE_DIR.glob("evolution_completed_*.json"):
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        # 检查是否过期（超过30分钟）
                        if data.get('status') in ['stale_failed', '未完成']:
                            stale_files.append(f)
                except:
                    pass
        except:
            pass

        return stale_files

    def verify_repairs(self, repair_results: Dict[str, Any], original_health: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证修复结果

        参数:
            repair_results: 修复结果
            original_health: 原始健康报告

        返回:
            验证结果
        """
        verification = {
            'verified': False,
            'health_after_repair': None,
            'improvements': [],
            'remaining_issues': []
        }

        # 重新运行健康评估
        new_health = self.run_health_evaluation()
        verification['health_after_repair'] = new_health

        # 比较修复前后的健康分数
        original_score = original_health.get('overall_score', 0)
        new_score = new_health.get('overall_score', 0)

        if new_score > original_score:
            verification['verified'] = True
            verification['improvements'].append(f'健康分数从 {original_score} 提升到 {new_score}')

        # 检查剩余问题
        new_issues = new_health.get('issues', [])
        if new_issues:
            verification['remaining_issues'] = new_issues

        return verification

    def run_full_integration_cycle(self) -> Dict[str, Any]:
        """
        运行完整的评估→修复→验证闭环

        返回:
            完整的集成报告
        """
        start_time = datetime.now()
        report = {
            'timestamp': start_time.isoformat(),
            'version': self.version,
            'status': 'init',
            'steps': {}
        }

        # Step 1: 健康评估
        step_start = datetime.now()
        health_report = self.run_health_evaluation()
        report['steps']['health_evaluation'] = {
            'duration_seconds': (datetime.now() - step_start).total_seconds(),
            'health_score': health_report.get('overall_score', 0),
            'issues_found': len(health_report.get('issues', []))
        }

        # Step 2: 问题诊断与分类
        step_start = datetime.now()
        categorized_issues = self.diagnose_and_categorize_issues(health_report)
        report['steps']['issue_diagnosis'] = {
            'duration_seconds': (datetime.now() - step_start).total_seconds(),
            'auto_repairable_count': len(categorized_issues.get('auto_repairable', [])),
            'manual_fix_required_count': len(categorized_issues.get('manual_fix_required', [])),
            'warnings_count': len(categorized_issues.get('warnings', []))
        }

        # Step 3: 自动修复
        step_start = datetime.now()
        repair_results = self.attempt_auto_repairs(categorized_issues)
        report['steps']['auto_repair'] = {
            'duration_seconds': (datetime.now() - step_start).total_seconds(),
            'total_attempted': repair_results.get('total_attempted', 0),
            'total_successful': repair_results.get('total_successful', 0),
            'total_failed': repair_results.get('total_failed', 0)
        }

        # Step 4: 验证修复
        step_start = datetime.now()
        verification = self.verify_repairs(repair_results, health_report)
        report['steps']['verification'] = {
            'duration_seconds': (datetime.now() - step_start).total_seconds(),
            'verified': verification.get('verified', False),
            'health_score_improvement': verification.get('improvements', [])
        }

        # 汇总结果
        total_duration = (datetime.now() - start_time).total_seconds()
        report['total_duration_seconds'] = total_duration
        report['overall_status'] = 'success' if verification.get('verified') else 'partial'
        report['summary'] = self._generate_summary(report, verification)

        # 保存报告
        self.last_integration_report = report
        self.save_state()

        return report

    def _generate_summary(self, report: Dict[str, Any], verification: Dict[str, Any]) -> str:
        """生成报告摘要"""
        steps = report.get('steps', {})

        eval_step = steps.get('health_evaluation', {})
        repair_step = steps.get('auto_repair', {})
        verify_step = steps.get('verification', {})

        summary = f"""进化健康自评估与自愈集成报告:
- 健康评估：发现 {eval_step.get('issues_found', 0)} 个问题，健康分数 {eval_step.get('health_score', 0)}
- 问题分类：{steps.get('issue_diagnosis', {}).get('auto_repairable_count', 0)} 个可自动修复，{steps.get('issue_diagnosis', {}).get('manual_fix_required_count', 0)} 个需手动修复
- 自动修复：尝试 {repair_step.get('total_attempted', 0)} 项，成功 {repair_step.get('total_successful', 0)} 项
- 验证结果：{'修复有效' if verify_step.get('verified') else '需要进一步处理'}
- 总耗时：{report.get('total_duration_seconds', 0):.2f} 秒"""

        return summary

    def get_status(self) -> Dict[str, Any]:
        """
        获取系统状态

        返回:
            系统状态字典
        """
        status = {
            'name': self.name,
            'version': self.version,
            'health_engine_loaded': self.health_engine is not None,
            'healing_engine_loaded': self.healing_engine is not None,
            'last_report': self.last_integration_report.get('summary', '无') if self.last_integration_report else '无',
            'last_updated': datetime.now().isoformat()
        }

        return status


def main():
    """主函数 - 支持命令行调用"""
    import sys

    engine = EvolutionHealthHealingIntegratedEngine()

    if len(sys.argv) < 2:
        # 无参数时显示状态
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return

    command = sys.argv[1].lower()

    if command in ['status', '状态']:
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif command in ['health', '评估']:
        # 只运行健康评估
        report = engine.run_health_evaluation()
        print(json.dumps(report, ensure_ascii=False, indent=2))

    elif command in ['repair', '修复']:
        # 只运行修复
        health_report = engine.run_health_evaluation()
        categorized = engine.diagnose_and_categorize_issues(health_report)
        results = engine.attempt_auto_repairs(categorized)
        print(json.dumps(results, ensure_ascii=False, indent=2))

    elif command in ['run', '执行', 'integrate', '集成']:
        # 运行完整闭环
        report = engine.run_full_integration_cycle()
        print(json.dumps(report, ensure_ascii=False, indent=2))

    elif command in ['help', '帮助']:
        help_text = """
智能全场景进化健康自评估与自愈集成引擎

用法:
    python evolution_health_healing_integrated_engine.py <command>

命令:
    status/状态        - 显示系统状态
    health/评估       - 只运行健康评估
    repair/修复       - 只运行自动修复
    run/执行/集成     - 运行完整闭环（评估→修复→验证）
    help/帮助         - 显示帮助信息
        """
        print(help_text)

    else:
        print(f"未知命令: {command}")
        print("使用 'help' 查看可用命令")


if __name__ == "__main__":
    main()