#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化闭环健康自评估与自适应优化引擎 (version 1.0.0)

让系统能够自动评估自身进化健康状态、识别进化过程中的问题、生成健康报告
并指导后续进化方向，形成「进化健康监测→问题诊断→报告生成→优化指导」的完整闭环。

该引擎整合了：
- 进化环健康监控 (round 283, 290)
- 进化效果评估 (round 207)
- 进化策略优化 (round 211)
- 自我优化 (round 242)

功能：
1. 进化健康状态评估：综合评估进化环的整体健康状况
2. 问题自动识别与诊断：检测进化过程中的各类问题
3. 健康报告生成：生成详细的进化健康报告
4. 优化建议生成：提供具体可执行的优化建议
5. 进化方向指导：基于健康状态给出后续进化建议

作者：Claude Sonnet 4.6
日期：2026-03-14
"""

import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import subprocess

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"


class EvolutionHealthSelfEvaluationEngine:
    """智能全场景进化闭环健康自评估与自适应优化引擎"""

    def __init__(self):
        self.name = "EvolutionHealthSelfEvaluationEngine"
        self.version = "1.0.0"
        self.state_file = STATE_DIR / "evolution_health_self_evaluation_state.json"
        self.health_reports = []
        self.issues = []
        self.optimization_recommendations = []
        self.load_state()

    def load_state(self):
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.health_reports = data.get('health_reports', [])
                    self.issues = data.get('issues', [])
                    self.optimization_recommendations = data.get('optimization_recommendations', [])
            except Exception:
                pass

    def save_state(self):
        """保存状态"""
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump({
                'health_reports': self.health_reports,
                'issues': self.issues,
                'optimization_recommendations': self.optimization_recommendations,
                'last_updated': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)

    def check_evolution_cycle_health(self) -> Dict[str, Any]:
        """
        检查进化环整体健康状况

        返回:
            健康检查结果字典
        """
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'overall_score': 0,
            'components': {},
            'issues': [],
            'recommendations': []
        }

        # 1. 检查进化状态文件
        current_mission_path = STATE_DIR / "current_mission.json"
        if current_mission_path.exists():
            try:
                with open(current_mission_path, 'r', encoding='utf-8') as f:
                    mission_data = json.load(f)
                    health_status['components']['current_mission'] = {
                        'status': 'ok',
                        'mission': mission_data.get('mission', 'unknown'),
                        'phase': mission_data.get('phase', 'unknown'),
                        'loop_round': mission_data.get('loop_round', 0)
                    }
            except Exception as e:
                health_status['components']['current_mission'] = {
                    'status': 'error',
                    'error': str(e)
                }
                health_status['issues'].append('进化状态文件读取失败')
        else:
            health_status['components']['current_mission'] = {
                'status': 'missing',
            }
            health_status['issues'].append('缺少 current_mission.json 文件')

        # 2. 检查最近进化日志
        log_health = self._check_recent_evolution_logs()
        health_status['components']['recent_logs'] = log_health

        # 3. 检查进化历史数据库
        history_health = self._check_evolution_history()
        health_status['components']['history_db'] = history_health

        # 4. 检查未完成/失败的进化轮次
        pending_health = self._check_pending_evolutions()
        health_status['components']['pending_evolutions'] = pending_health

        # 5. 计算整体健康分数
        health_status['overall_score'] = self._calculate_health_score(health_status['components'])

        return health_status

    def _check_recent_evolution_logs(self) -> Dict[str, Any]:
        """检查最近进化日志"""
        log_status = {'status': 'ok', 'entries': 0, 'issues': []}

        try:
            recent_logs_path = STATE_DIR / "recent_logs.json"
            if recent_logs_path.exists():
                with open(recent_logs_path, 'r', encoding='utf-8') as f:
                    logs_data = json.load(f)
                    entries = logs_data.get('entries', [])
                    log_status['entries'] = len(entries)

                    # 检查最近的日志条目
                    if entries:
                        last_entry = entries[-1]
                        log_status['last_phase'] = last_entry.get('phase', 'unknown')
                        log_status['last_mission'] = last_entry.get('mission', 'unknown')

                        # 检查是否有长时间未完成的阶段
                        phases = [e.get('phase') for e in entries[-10:]]
                        if phases.count('track') > 5:
                            log_status['issues'].append('存在长时间未完成的执行阶段')
            else:
                log_status['issues'].append('recent_logs.json 不存在')
                log_status['status'] = 'warning'
        except Exception as e:
            log_status['status'] = 'error'
            log_status['issues'].append(f'日志读取失败: {str(e)}')

        return log_status

    def _check_evolution_history(self) -> Dict[str, Any]:
        """检查进化历史数据库"""
        history_status = {'status': 'ok', 'total_rounds': 0, 'completed': 0, 'failed': 0}

        try:
            # 统计 evolution_completed_*.json 文件
            completed_files = list(STATE_DIR.glob("evolution_completed_*.json"))
            history_status['total_rounds'] = len(completed_files)

            # 统计完成和失败
            completed_count = 0
            failed_count = 0
            for f in completed_files:
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        status = data.get('status', 'unknown')
                        if '完成' in str(status) or status == 'completed':
                            completed_count += 1
                        elif '未完成' in str(status) or status in ['failed', 'stale_failed']:
                            failed_count += 1
                except:
                    pass

            history_status['completed'] = completed_count
            history_status['failed'] = failed_count

            if failed_count > completed_count * 0.3:
                history_status['status'] = 'warning'
                history_status['issues'].append(f'失败率较高: {failed_count}/{completed_count + failed_count}')

        except Exception as e:
            history_status['status'] = 'error'
            history_status['issues'].append(f'历史检查失败: {str(e)}')

        return history_status

    def _check_pending_evolutions(self) -> Dict[str, Any]:
        """检查未完成/卡住的进化"""
        pending_status = {'status': 'ok', 'pending_rounds': [], 'stale_count': 0}

        try:
            # 查找所有 evolution_completed_*.json 中状态为"未完成"的
            completed_files = list(STATE_DIR.glob("evolution_completed_*.json"))
            for f in completed_files:
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        if '未完成' in str(data.get('status', '')) or data.get('status') in ['stale_failed']:
                            pending_status['pending_rounds'].append({
                                'file': f.name,
                                'status': data.get('status', 'unknown')
                            })
                except:
                    pass

            pending_status['stale_count'] = len(pending_status['pending_rounds'])
            if pending_status['stale_count'] > 5:
                pending_status['status'] = 'warning'
                pending_status['issues'].append(f'存在 {pending_status["stale_count"]} 个未完成的进化轮次')

        except Exception as e:
            pending_status['status'] = 'error'
            pending_status['issues'].append(f'检查失败: {str(e)}')

        return pending_status

    def _calculate_health_score(self, components: Dict[str, Any]) -> float:
        """计算整体健康分数 (0-100)"""
        score = 100.0

        # 检查各组件状态
        for component_name, component_data in components.items():
            if isinstance(component_data, dict):
                status = component_data.get('status', 'unknown')
                issues = component_data.get('issues', [])

                if status == 'error':
                    score -= 20
                elif status == 'warning':
                    score -= 10

                score -= len(issues) * 5

        return max(0, min(100, score))

    def diagnose_issues(self, health_status: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        诊断问题 - 基于健康检查结果识别具体问题

        参数:
            health_status: 健康检查结果

        返回:
            问题列表
        """
        issues = []

        # 分析各组件问题
        for component_name, component_data in health_status.get('components', {}).items():
            if isinstance(component_data, dict):
                issues_list = component_data.get('issues', [])
                for issue in issues_list:
                    issues.append({
                        'component': component_name,
                        'issue': issue,
                        'severity': 'high' if component_data.get('status') == 'error' else 'medium'
                    })

        # 检查整体健康分数
        if health_status.get('overall_score', 100) < 50:
            issues.append({
                'component': 'overall',
                'issue': f'整体健康分数过低: {health_status.get("overall_score", 0)}',
                'severity': 'high'
            })
        elif health_status.get('overall_score', 100) < 70:
            issues.append({
                'component': 'overall',
                'issue': f'整体健康分数偏低: {health_status.get("overall_score", 0)}',
                'severity': 'medium'
            })

        return issues

    def generate_health_report(self) -> Dict[str, Any]:
        """
        生成进化健康报告

        返回:
            健康报告字典
        """
        # 1. 执行健康检查
        health_status = self.check_evolution_cycle_health()

        # 2. 诊断问题
        issues = self.diagnose_issues(health_status)

        # 3. 生成优化建议
        recommendations = self._generate_optimization_recommendations(health_status, issues)

        # 4. 构建报告
        report = {
            'timestamp': datetime.now().isoformat(),
            'version': self.version,
            'overall_score': health_status.get('overall_score', 0),
            'health_status': health_status,
            'issues': issues,
            'recommendations': recommendations,
            'summary': self._generate_summary(health_status, issues, recommendations)
        }

        # 保存报告
        self.health_reports.append(report)
        if len(self.health_reports) > 50:
            self.health_reports = self.health_reports[-50:]
        self.issues = issues
        self.optimization_recommendations = recommendations
        self.save_state()

        return report

    def _generate_optimization_recommendations(self, health_status: Dict[str, Any],
                                                issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成优化建议"""
        recommendations = []

        # 基于问题生成建议
        for issue in issues:
            component = issue.get('component', '')
            issue_desc = issue.get('issue', '')

            if 'current_mission' in component:
                if '读取失败' in issue_desc or '不存在' in issue_desc:
                    recommendations.append({
                        'priority': 'high',
                        'category': 'mission_state',
                        'recommendation': '检查并修复 current_mission.json 文件',
                        'action': 'run_plan 检查或重建状态文件'
                    })

            if 'pending_evolutions' in component:
                pending_count = health_status.get('components', {}).get('pending_evolutions', {}).get('stale_count', 0)
                if pending_count > 0:
                    recommendations.append({
                        'priority': 'high',
                        'category': 'stale_rounds',
                        'recommendation': f'存在 {pending_count} 个未完成的进化轮次，需要清理或完成',
                        'action': '手动检查这些轮次的状态文件并修复'
                    })

            if 'overall' in component:
                score = health_status.get('overall_score', 0)
                if score < 50:
                    recommendations.append({
                        'priority': 'critical',
                        'category': 'overall_health',
                        'recommendation': '进化环整体健康状态较差，需要全面检查和修复',
                        'action': '运行 system_health_report_engine 进行全面检查'
                    })
                elif score < 70:
                    recommendations.append({
                        'priority': 'medium',
                        'category': 'overall_health',
                        'recommendation': '进化环健康状态一般，建议优化',
                        'action': '检查低分组件并修复'
                    })

        # 基于健康组件状态生成建议
        for component_name, component_data in health_status.get('components', {}).items():
            if isinstance(component_data, dict) and component_data.get('status') == 'ok':
                # 正常的组件可以加强
                if component_name == 'history_db':
                    completed = component_data.get('completed', 0)
                    if completed > 100:
                        recommendations.append({
                            'priority': 'low',
                            'category': 'optimization',
                            'recommendation': f'已完成 {completed} 轮进化，历史数据丰富，可进行深度分析',
                            'action': '使用 evolution_meta_pattern_discovery 进行模式挖掘'
                        })

        return recommendations

    def _generate_summary(self, health_status: Dict[str, Any],
                         issues: List[Dict[str, Any]],
                         recommendations: List[Dict[str, Any]]) -> str:
        """生成报告摘要"""
        score = health_status.get('overall_score', 0)
        issue_count = len(issues)
        rec_count = len(recommendations)

        if score >= 90:
            status_text = "优秀"
        elif score >= 70:
            status_text = "良好"
        elif score >= 50:
            status_text = "一般"
        else:
            status_text = "较差"

        summary = f"""进化环健康状态：{status_text} (分数: {score}/100)
- 发现 {issue_count} 个问题
- 生成 {rec_count} 条优化建议
- 建议优先处理 {sum(1 for r in recommendations if r.get('priority') in ['high', 'critical'])} 条高优先级建议"""

        return summary

    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """获取当前的优化建议"""
        if not self.optimization_recommendations:
            # 如果没有缓存的报告，先生成一份
            self.generate_health_report()
        return self.optimization_recommendations

    def analyze_evolution_trends(self, rounds: int = 30) -> Dict[str, Any]:
        """
        分析进化趋势

        参数:
            rounds: 分析的轮次数量

        返回:
            趋势分析结果
        """
        trends = {
            'timestamp': datetime.now().isoformat(),
            'analyzed_rounds': rounds,
            'success_rate': 0,
            'avg_completion_time': 0,
            'common_issues': [],
            'improvement_suggestions': []
        }

        try:
            # 读取最近的进化完成记录
            completed_files = sorted(
                STATE_DIR.glob("evolution_completed_*.json"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )[:rounds]

            completed = 0
            failed = 0

            for f in completed_files:
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        if '完成' in str(data.get('status', '')):
                            completed += 1
                        elif '未完成' in str(data.get('status', '')):
                            failed += 1
                except:
                    pass

            total = completed + failed
            if total > 0:
                trends['success_rate'] = round(completed / total * 100, 1)

        except Exception as e:
            trends['error'] = str(e)

        return trends


def main():
    """主函数 - 支持命令行调用"""
    import sys

    engine = EvolutionHealthSelfEvaluationEngine()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "health" or command == "check":
            # 健康检查
            result = engine.check_evolution_cycle_health()
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif command == "report" or command == "generate":
            # 生成健康报告
            report = engine.generate_health_report()
            print(json.dumps(report, ensure_ascii=False, indent=2))

        elif command == "recommendations" or command == "advice":
            # 获取优化建议
            recommendations = engine.get_optimization_recommendations()
            print(json.dumps(recommendations, ensure_ascii=False, indent=2))

        elif command == "trends" or command == "analyze":
            # 分析进化趋势
            rounds = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            trends = engine.analyze_evolution_trends(rounds)
            print(json.dumps(trends, ensure_ascii=False, indent=2))

        elif command == "status":
            # 简单状态概览
            health = engine.check_evolution_cycle_health()
            print(f"进化环健康分数: {health.get('overall_score', 0)}/100")
            print(f"组件状态: {json.dumps({k: v.get('status', 'unknown') for k, v in health.get('components', {}).items()}, ensure_ascii=False)}")

        else:
            print(f"未知命令: {command}")
            print("可用命令: health, report, recommendations, trends, status")
    else:
        # 默认生成健康报告
        report = engine.generate_health_report()
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()