#!/usr/bin/env python3
"""
智能全场景进化效能深度分析与优化建议引擎
基于大规模进化历史分析，识别低效模式、重复进化、资源浪费等问题，
自动生成可执行的优化建议，实现进化系统的持续自我优化。

功能：
1. 进化效率多维度分析（完成率、执行时间、成功率、趋势）
2. 低效模式自动识别（重复进化、效率低下、资源浪费）
3. 优化建议自动生成（可执行的改进方案）
4. 进化健康度综合评估
5. 与 do.py 深度集成
"""

import os
import sys
import json
import sqlite3
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter, defaultdict

# 添加项目根目录到 Python 路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

# 数据库路径
DB_PATH = "runtime/state/evolution_history.db"
COMPLETED_STATE_PATH = "runtime/state/evolution_completed_ev_*.json"

def _safe_print(text: str):
    """安全打印，处理编码问题"""
    try:
        print(text)
    except UnicodeEncodeError:
        # 移除非ASCII字符后打印
        import re
        clean_text = re.sub(r'[^\x00-\x7F]+', '', text)
        print(clean_text)


class EvolutionEfficiencyAnalyzer:
    """进化效能深度分析与优化建议引擎"""

    def __init__(self):
        self.db_path = os.path.join(PROJECT_ROOT, DB_PATH)
        self.completed_pattern = os.path.join(PROJECT_ROOT, "runtime/state/evolution_completed_ev_*.json")
        self.analysis_result = {}

    def load_evolution_history(self) -> List[Dict]:
        """加载进化历史数据"""
        history_data = []

        # 从 SQLite 数据库加载
        if os.path.exists(self.db_path):
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT round_number, timestamp, current_goal, status, execution_time, result
                    FROM evolution_rounds
                    ORDER BY round_number DESC
                    LIMIT 100
                """)
                rows = cursor.fetchall()
                for row in rows:
                    history_data.append({
                        'round': row[0],
                        'timestamp': row[1],
                        'goal': row[2],
                        'status': row[3],
                        'execution_time': row[4],
                        'result': row[5]
                    })
                conn.close()
            except Exception as e:
                print(f"加载进化历史数据库失败: {e}")

        # 从 JSON 文件补充
        import glob
        json_files = glob.glob(self.completed_pattern)
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 检查是否已存在
                    exists = any(h['round'] == data.get('loop_round', 0) for h in history_data)
                    if not exists and data.get('loop_round'):
                        history_data.append({
                            'round': data.get('loop_round', 0),
                            'timestamp': data.get('timestamp', data.get('completed_at', '')),
                            'goal': data.get('current_goal', ''),
                            'status': data.get('status', 'unknown'),
                            'execution_time': 0,
                            'result': data.get('summary', '')
                        })
            except Exception as e:
                print(f"加载 {json_file} 失败: {e}")

        # 按轮次排序
        history_data.sort(key=lambda x: x.get('round', 0), reverse=True)
        return history_data[:50]  # 取最近50轮

    def analyze_completion_rate(self, history: List[Dict]) -> Dict:
        """分析完成率"""
        total = len(history)
        if total == 0:
            return {'rate': 0, 'total': 0, 'completed': 0}

        completed = sum(1 for h in history if h.get('status') in ['已完成', 'success', 'completed', '完成'])
        return {
            'rate': round(completed / total * 100, 1) if total > 0 else 0,
            'total': total,
            'completed': completed,
            'failed': total - completed
        }

    def analyze_execution_time(self, history: List[Dict]) -> Dict:
        """分析执行时间趋势"""
        times = [h.get('execution_time', 0) for h in history if h.get('execution_time', 0) > 0]

        if not times:
            return {'avg': 0, 'trend': 'unknown', 'recent_avg': 0}

        avg_time = sum(times) / len(times)
        recent = times[:10] if len(times) >= 10 else times
        recent_avg = sum(recent) / len(recent)

        # 判断趋势
        if len(times) >= 20:
            older = times[20:]
            older_avg = sum(older) / len(older)
            if recent_avg < older_avg * 0.8:
                trend = 'improving'
            elif recent_avg > older_avg * 1.2:
                trend = 'degrading'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'

        return {
            'avg': round(avg_time, 2),
            'recent_avg': round(recent_avg, 2),
            'trend': trend,
            'min': min(times) if times else 0,
            'max': max(times) if times else 0
        }

    def detect_duplicate_evolutions(self, history: List[Dict]) -> List[Dict]:
        """检测重复进化模式"""
        # 提取关键词
        keywords = []
        for h in history:
            goal = h.get('goal', '')
            if goal:
                # 提取主要能力词
                words = re.findall(r'[\u4e00-\u9fa5]+', goal)
                keywords.extend(words[:3])  # 取前3个关键词

        # 统计词频
        counter = Counter(keywords)
        duplicates = []

        for word, count in counter.most_common(20):
            if count >= 3:
                duplicates.append({
                    'keyword': word,
                    'count': count,
                    'severity': 'high' if count >= 5 else 'medium'
                })

        return duplicates

    def detect_inefficient_patterns(self, history: List[Dict]) -> List[Dict]:
        """检测低效模式"""
        patterns = []

        # 检测1：检查连续失败的轮次
        consecutive_failures = 0
        max_consecutive_failures = 0
        for h in history:
            if h.get('status') not in ['已完成', 'success', 'completed', '完成']:
                consecutive_failures += 1
                max_consecutive_failures = max(max_consecutive_failures, consecutive_failures)
            else:
                consecutive_failures = 0

        if max_consecutive_failures >= 3:
            patterns.append({
                'type': 'consecutive_failures',
                'count': max_consecutive_failures,
                'severity': 'high',
                'description': f'连续{max_consecutive_failures}轮失败，需检查进化决策机制'
            })

        # 检测2：执行时间过长的轮次
        long_runs = [h for h in history if h.get('execution_time', 0) > 300]  # 超过5分钟
        if len(long_runs) >= 3:
            patterns.append({
                'type': 'long_execution_time',
                'count': len(long_runs),
                'severity': 'medium',
                'description': f'{len(long_runs)}轮执行时间超过5分钟，需优化执行效率'
            })

        # 检测3：缺少针对性验证的轮次
        # 检查最近10轮是否有足够的验证记录
        recent_rounds = history[:10]
        verified_count = sum(1 for h in recent_rounds if 'verification' in str(h.get('result', '')).lower())
        if verified_count < 5 and len(recent_rounds) >= 5:
            patterns.append({
                'type': 'insufficient_verification',
                'count': len(recent_rounds) - verified_count,
                'severity': 'medium',
                'description': f'最近{len(recent_rounds)}轮中仅{verified_count}轮有验证记录，需加强校验'
            })

        return patterns

    def analyze_goal_achievement(self, history: List[Dict]) -> Dict:
        """分析目标达成情况"""
        if not history:
            return {'achievement_rate': 0, 'avg_progress': 0}

        goals = [h.get('goal', '') for h in history]
        # 分析目标完成度
        completed_goals = [g for g in goals if g and any(s in str(g).lower() for s in ['完成', '实现', '集成', '创建'])]

        return {
            'total_goals': len(goals),
            'completed_goals': len(completed_goals),
            'achievement_rate': round(len(completed_goals) / len(goals) * 100, 1) if goals else 0
        }

    def generate_optimization_suggestions(self,
                                          completion_rate: Dict,
                                          execution_time: Dict,
                                          duplicates: List[Dict],
                                          patterns: List[Dict]) -> List[Dict]:
        """生成优化建议"""
        suggestions = []

        # 建议1：完成率优化
        if completion_rate.get('rate', 0) < 90:
            suggestions.append({
                'category': 'completion_rate',
                'priority': 'high',
                'suggestion': f'进化完成率为{completion_rate["rate"]}%，建议优化决策机制，确保每轮进化目标清晰可达成',
                'action': '建议检查未完成轮次的具体原因，加强决策阶段的目标可行性评估'
            })

        # 建议2：执行效率优化
        if execution_time.get('trend') == 'degrading':
            suggestions.append({
                'category': 'execution_efficiency',
                'priority': 'high',
                'suggestion': f'执行时间呈上升趋势（平均{execution_time["recent_avg"]}s），需优化执行效率',
                'action': '建议分析耗时较长的进化步骤，优化脚本执行和文件IO操作'
            })
        elif execution_time.get('trend') == 'improving':
            suggestions.append({
                'category': 'execution_efficiency',
                'priority': 'low',
                'suggestion': f'执行效率持续改善，当前平均{execution_time["recent_avg"]}s',
                'action': '继续保持当前优化策略'
            })

        # 建议3：重复进化检测
        if duplicates:
            top_dup = duplicates[0]
            suggestions.append({
                'category': 'duplicate_evolution',
                'priority': 'medium',
                'suggestion': f'检测到关键词「{top_dup["keyword"]}」重复{top_dup["count"]}次，可能存在重复进化',
                'action': '建议检查该方向的进化是否有明确差异，避免低效重复'
            })

        # 建议4：低效模式处理
        for pattern in patterns:
            if pattern['type'] == 'consecutive_failures':
                suggestions.append({
                    'category': 'failure_recovery',
                    'priority': 'high',
                    'suggestion': f'检测到连续{pattern["count"]}轮失败，需检查进化策略',
                    'action': '建议暂时降低进化目标难度，优先完成简单任务恢复信心'
                })

        # 建议5：如果没有明显问题的建议
        if not suggestions:
            suggestions.append({
                'category': 'general',
                'priority': 'low',
                'suggestion': '系统运行状态良好，未检测到明显问题',
                'action': '继续保持当前进化策略，可尝试更具挑战性的进化目标'
            })

        return suggestions

    def calculate_health_score(self,
                               completion_rate: Dict,
                               execution_time: Dict,
                               duplicates: List[Dict],
                               patterns: List[Dict]) -> int:
        """计算进化健康分数"""
        score = 100

        # 完成率扣分
        if completion_rate.get('rate', 0) < 50:
            score -= 30
        elif completion_rate.get('rate', 0) < 70:
            score -= 15
        elif completion_rate.get('rate', 0) < 90:
            score -= 5

        # 执行效率扣分
        if execution_time.get('trend') == 'degrading':
            score -= 15
        elif execution_time.get('trend') == 'unknown':
            score -= 5

        # 重复进化扣分
        if len(duplicates) >= 3:
            score -= 20
        elif len(duplicates) >= 1:
            score -= 10

        # 低效模式扣分
        high_severity = sum(1 for p in patterns if p.get('severity') == 'high')
        medium_severity = sum(1 for p in patterns if p.get('severity') == 'medium')
        score -= high_severity * 15
        score -= medium_severity * 5

        return max(0, min(100, score))

    def analyze(self) -> Dict:
        """执行完整分析"""
        _safe_print("=" * 60)
        _safe_print("进化效能深度分析引擎")
        _safe_print("=" * 60)

        # 1. 加载历史数据
        _safe_print("\n[1/6] 加载进化历史数据...")
        history = self.load_evolution_history()
        _safe_print(f"    已加载 {len(history)} 轮进化历史")

        # 2. 分析完成率
        _safe_print("[2/6] 分析进化完成率...")
        completion_rate = self.analyze_completion_rate(history)
        _safe_print(f"    完成率: {completion_rate['rate']}% ({completion_rate['completed']}/{completion_rate['total']})")

        # 3. 分析执行时间
        _safe_print("[3/6] 分析执行时间趋势...")
        execution_time = self.analyze_execution_time(history)
        _safe_print(f"    平均执行时间: {execution_time['avg']}s, 趋势: {execution_time['trend']}")

        # 4. 检测重复进化
        _safe_print("[4/6] 检测重复进化模式...")
        duplicates = self.detect_duplicate_evolutions(history)
        _safe_print(f"    发现 {len(duplicates)} 个可能重复的进化方向")

        # 5. 检测低效模式
        _safe_print("[5/6] 检测低效模式...")
        patterns = self.detect_inefficient_patterns(history)
        _safe_print(f"    发现 {len(patterns)} 个低效模式")

        # 6. 生成优化建议
        _safe_print("[6/6] 生成优化建议...")
        suggestions = self.generate_optimization_suggestions(
            completion_rate, execution_time, duplicates, patterns
        )
        _safe_print(f"    生成 {len(suggestions)} 条优化建议")

        # 计算健康分数
        health_score = self.calculate_health_score(
            completion_rate, execution_time, duplicates, patterns
        )
        _safe_print(f"\n进化健康分数: {health_score}/100")

        # 整合结果
        self.analysis_result = {
            'health_score': health_score,
            'completion_rate': completion_rate,
            'execution_time': execution_time,
            'duplicates': duplicates,
            'inefficient_patterns': patterns,
            'optimization_suggestions': suggestions,
            'total_rounds_analyzed': len(history),
            'timestamp': datetime.now().isoformat()
        }

        return self.analysis_result

    def print_report(self):
        """打印分析报告"""
        if not self.analysis_result:
            self.analyze()

        result = self.analysis_result

        _safe_print("\n" + "=" * 60)
        _safe_print("进化效能分析报告")
        _safe_print("=" * 60)

        _safe_print(f"\n健康分数: {result['health_score']}/100")

        _safe_print(f"\n完成率分析:")
        cr = result['completion_rate']
        _safe_print(f"   - 完成率: {cr['rate']}%")
        _safe_print(f"   - 已完成: {cr['completed']} 轮")
        _safe_print(f"   - 未完成: {cr['failed']} 轮")

        _safe_print(f"\n执行效率分析:")
        et = result['execution_time']
        _safe_print(f"   - 平均执行时间: {et['avg']}s")
        _safe_print(f"   - 近期平均: {et['recent_avg']}s")
        _safe_print(f"   - 趋势: {et['trend']}")

        if result['duplicates']:
            _safe_print(f"\n重复进化检测:")
            for dup in result['duplicates'][:3]:
                _safe_print(f"   - {dup['keyword']} 重复 {dup['count']} 次 (严重度: {dup['severity']})")

        if result['inefficient_patterns']:
            _safe_print(f"\n低效模式检测:")
            for p in result['inefficient_patterns']:
                _safe_print(f"   - {p['description']}")

        _safe_print(f"\n优化建议:")
        for i, s in enumerate(result['optimization_suggestions'], 1):
            priority = "[HIGH]" if s['priority'] == 'high' else "[MED]" if s['priority'] == 'medium' else "[LOW]"
            _safe_print(f"   {priority} [{s['category']}] {s['suggestion']}")
            _safe_print(f"      -> {s['action']}")

        _safe_print("\n" + "=" * 60)

    def save_report(self, output_path: str = None):
        """保存分析报告"""
        if not self.analysis_result:
            self.analyze()

        if output_path is None:
            output_path = "runtime/state/evolution_efficiency_report.json"

        output_path = os.path.join(PROJECT_ROOT, output_path)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_result, f, ensure_ascii=False, indent=2)

        _safe_print(f"\n报告已保存到: {output_path}")


def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser(description='进化效能深度分析与优化建议引擎')
    parser.add_argument('command', nargs='?', default='analyze',
                       help='命令: analyze, report, suggestions, health')
    parser.add_argument('--output', '-o', default=None,
                       help='输出文件路径')
    parser.add_argument('--format', '-f', choices=['text', 'json'], default='text',
                       help='输出格式')

    args = parser.parse_args()

    analyzer = EvolutionEfficiencyAnalyzer()

    if args.command == 'analyze' or args.command == 'report':
        analyzer.analyze()
        if args.format == 'text':
            analyzer.print_report()
        else:
            print(json.dumps(analyzer.analysis_result, ensure_ascii=False, indent=2))
        if args.output:
            analyzer.save_report(args.output)

    elif args.command == 'suggestions':
        analyzer.analyze()
        suggestions = analyzer.analysis_result.get('optimization_suggestions', [])
        for i, s in enumerate(suggestions, 1):
            print(f"{i}. [{s['category']}] {s['suggestion']}")
            print(f"   行动: {s['action']}\n")

    elif args.command == 'health':
        analyzer.analyze()
        print(analyzer.analysis_result.get('health_score', 0))

    else:
        parser.print_help()


if __name__ == '__main__':
    main()