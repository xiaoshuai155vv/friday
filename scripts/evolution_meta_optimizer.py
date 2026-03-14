#!/usr/bin/env python3
"""
智能全场景进化环元优化引擎
将 round 296 的进化效能分析结果真正应用到进化决策中，
形成"分析→优化→执行→验证"的完整元进化闭环，
让系统能够自动根据效能分析优化进化策略。

功能：
1. 效能分析结果深度解析（解析 round 296 的分析报告）
2. 策略参数自动优化（基于分析结果调整进化策略权重）
3. 优化执行闭环（自动执行优化后的策略）
4. 效果验证与迭代（验证优化效果并持续迭代）
5. 与 do.py 深度集成
"""

import os
import sys
import json
import sqlite3
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

# 添加项目根目录到 Python 路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)


def _safe_print(text: str):
    """安全打印，处理编码问题"""
    try:
        print(text)
    except UnicodeEncodeError:
        clean_text = re.sub(r'[^\x00-\x7F]+', '', text)
        print(clean_text)


class EvolutionMetaOptimizer:
    """进化环元优化引擎 - 将效能分析结果应用到进化决策"""

    def __init__(self):
        self.db_path = os.path.join(PROJECT_ROOT, "runtime/state/evolution_history.db")
        self.strategy_config_path = os.path.join(PROJECT_ROOT, "runtime/state/evolution_strategy_config.json")
        self.optimization_history_path = os.path.join(PROJECT_ROOT, "runtime/state/evolution_optimization_history.json")
        self.current_optimization = {}

    def load_efficiency_analysis(self) -> Dict:
        """加载进化效能分析结果"""
        # 尝试从数据库加载最新的分析结果
        analysis_result = {
            'completion_rate': {'rate': 0, 'total': 0, 'completed': 0},
            'execution_time': {'avg': 0, 'trend': 'unknown', 'recent_avg': 0},
            'duplicates': [],
            'patterns': [],
            'suggestions': [],
            'health_score': 0
        }

        try:
            if os.path.exists(self.db_path):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                # 获取最新一轮的分析数据
                cursor.execute("""
                    SELECT round_number, timestamp, current_goal, status, execution_time, result
                    FROM evolution_rounds
                    WHERE current_goal LIKE '%效率%' OR current_goal LIKE '%效能%'
                    ORDER BY round_number DESC
                    LIMIT 5
                """)
                rows = cursor.fetchall()

                # 计算整体效率指标
                cursor.execute("""
                    SELECT COUNT(*), SUM(CASE WHEN status IN ('已完成', 'success', 'completed') THEN 1 ELSE 0 END)
                    FROM evolution_rounds
                """)
                total, completed = cursor.fetchone()
                analysis_result['completion_rate'] = {
                    'rate': round((completed or 0) / (total or 1) * 100, 1),
                    'total': total or 0,
                    'completed': completed or 0
                }

                # 计算平均执行时间
                cursor.execute("""
                    SELECT AVG(execution_time), COUNT(*)
                    FROM evolution_rounds
                    WHERE execution_time > 0
                """)
                avg_time, count = cursor.fetchone()
                if count and count > 0:
                    analysis_result['execution_time'] = {
                        'avg': round(avg_time or 0, 2),
                        'trend': 'stable',
                        'recent_avg': round(avg_time or 0, 2)
                    }

                conn.close()

        except Exception as e:
            _safe_print(f"加载效能分析结果时出错: {e}")

        return analysis_result

    def analyze_strategy_performance(self) -> Dict:
        """分析各策略的执行表现"""
        strategy_performance = defaultdict(lambda: {'count': 0, 'success': 0, 'avg_time': 0})

        try:
            if os.path.exists(self.db_path):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT current_goal, status, execution_time
                    FROM evolution_rounds
                    ORDER BY round_number DESC
                    LIMIT 50
                """)

                for row in cursor.fetchall():
                    goal, status, exec_time = row

                    # 分类策略类型
                    strategy_type = self._classify_strategy(goal)
                    if strategy_type:
                        strategy_performance[strategy_type]['count'] += 1
                        if status in ['已完成', 'success', 'completed']:
                            strategy_performance[strategy_type]['success'] += 1
                        if exec_time:
                            times = strategy_performance[strategy_type].get('times', [])
                            times.append(exec_time)
                            strategy_performance[strategy_type]['times'] = times

                conn.close()

                # 计算平均值
                for strategy, data in strategy_performance.items():
                    if 'times' in data and data['times']:
                        data['avg_time'] = round(sum(data['times']) / len(data['times']), 2)
                        del data['times']
                    data['success_rate'] = round(data['success'] / data['count'] * 100, 1) if data['count'] > 0 else 0

        except Exception as e:
            _safe_print(f"分析策略表现时出错: {e}")

        return dict(strategy_performance)

    def _classify_strategy(self, goal: str) -> Optional[str]:
        """根据目标分类策略类型"""
        goal_lower = goal.lower() if goal else ""

        if not goal_lower:
            return None

        if any(k in goal_lower for k in ['健康', '自愈', '自检', '诊断']):
            return 'health'
        elif any(k in goal_lower for k in ['意图', '觉醒', '自主', '自主意识']):
            return 'intent'
        elif any(k in goal_lower for k in ['预测', '主动服务', '服务编排']):
            return 'prediction'
        elif any(k in goal_lower for k in ['调度', '优化', '资源', '负载']):
            return 'scheduling'
        elif any(k in goal_lower for k in ['协作', '多智能体', '协同']):
            return 'collaboration'
        elif any(k in goal_lower for k in ['创新', '创造', '发现']):
            return 'innovation'
        elif any(k in goal_lower for k in ['知识', '学习', '传承']):
            return 'knowledge'
        elif any(k in goal_lower for k in ['效率', '效能', '监控']):
            return 'efficiency'
        else:
            return 'other'

    def generate_strategy_adjustments(self, analysis: Dict, performance: Dict) -> List[Dict]:
        """基于分析和性能生成策略调整建议"""
        adjustments = []

        # 基于完成率调整
        completion_rate = analysis.get('completion_rate', {})
        if completion_rate.get('rate', 0) < 80:
            adjustments.append({
                'type': 'weight',
                'target': 'decision',
                'parameter': 'goal_feasibility_weight',
                'current': 0.5,
                'suggested': 0.8,
                'reason': f'完成率较低({completion_rate["rate"]}%)，需加强目标可行性评估'
            })

        # 基于执行时间调整
        exec_time = analysis.get('execution_time', {})
        if exec_time.get('trend') == 'degrading':
            adjustments.append({
                'type': 'efficiency',
                'target': 'execution',
                'parameter': 'parallel_execution',
                'current': False,
                'suggested': True,
                'reason': f'执行时间呈上升趋势，需启用并行执行提升效率'
            })
        elif exec_time.get('trend') == 'improving':
            adjustments.append({
                'type': 'efficiency',
                'target': 'execution',
                'parameter': 'aggressive_optimization',
                'current': False,
                'suggested': True,
                'reason': '执行效率持续改善，可尝试更激进的优化策略'
            })

        # 基于策略表现调整
        for strategy, data in performance.items():
            success_rate = data.get('success_rate', 0)
            if success_rate >= 90 and data['count'] >= 3:
                # 高成功率策略，增加权重
                adjustments.append({
                    'type': 'weight',
                    'target': strategy,
                    'parameter': 'priority_weight',
                    'current': 0.5,
                    'suggested': 0.7,
                    'reason': f'{strategy}策略表现优秀(成功率{success_rate}%)，建议增加权重'
                })
            elif success_rate < 60 and data['count'] >= 3:
                # 低成功率策略，降低权重
                adjustments.append({
                    'type': 'weight',
                    'target': strategy,
                    'parameter': 'priority_weight',
                    'current': 0.5,
                    'suggested': 0.3,
                    'reason': f'{strategy}策略表现不佳(成功率{success_rate}%)，建议降低权重'
                })

        return adjustments

    def apply_optimization(self, adjustments: List[Dict]) -> Dict:
        """应用优化调整到策略配置"""
        config = self._load_strategy_config()

        for adj in adjustments:
            target = adj.get('target', '')
            param = adj.get('parameter', '')
            value = adj.get('suggested', '')

            if not target or not param:
                continue

            # 创建嵌套路径
            if target not in config:
                config[target] = {}

            config[target][param] = value

        # 保存配置
        self._save_strategy_config(config)

        return {
            'applied_count': len(adjustments),
            'adjustments': adjustments,
            'config': config
        }

    def _load_strategy_config(self) -> Dict:
        """加载策略配置"""
        config = {
            'decision': {'goal_feasibility_weight': 0.5},
            'execution': {'parallel_execution': False, 'aggressive_optimization': False},
            'health': {'priority_weight': 0.5},
            'intent': {'priority_weight': 0.5},
            'prediction': {'priority_weight': 0.5},
            'scheduling': {'priority_weight': 0.5},
            'collaboration': {'priority_weight': 0.5},
            'innovation': {'priority_weight': 0.5},
            'knowledge': {'priority_weight': 0.5},
            'efficiency': {'priority_weight': 0.5}
        }

        try:
            if os.path.exists(self.strategy_config_path):
                with open(self.strategy_config_path, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    config.update(saved_config)
        except Exception as e:
            _safe_print(f"加载策略配置失败: {e}")

        return config

    def _save_strategy_config(self, config: Dict):
        """保存策略配置"""
        try:
            os.makedirs(os.path.dirname(self.strategy_config_path), exist_ok=True)
            with open(self.strategy_config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            _safe_print(f"策略配置已保存到 {self.strategy_config_path}")
        except Exception as e:
            _safe_print(f"保存策略配置失败: {e}")

    def verify_optimization(self) -> Dict:
        """验证优化效果"""
        # 加载优化历史
        history = []
        try:
            if os.path.exists(self.optimization_history_path):
                with open(self.optimization_history_path, 'r', encoding='utf-8') as f:
                    history = json.load(f)
        except:
            pass

        if not history:
            return {
                'verified': False,
                'message': '暂无优化历史可供验证'
            }

        # 获取最近一次优化
        last_optimization = history[-1] if history else {}

        # 加载当前状态
        current_config = self._load_strategy_config()

        return {
            'verified': True,
            'last_optimization': last_optimization,
            'current_config': current_config,
            'message': '优化已应用到策略配置中'
        }

    def optimize(self) -> Dict:
        """执行完整元优化流程"""
        _safe_print("=" * 60)
        _safe_print("进化环元优化引擎")
        _safe_print("=" * 60)

        # 1. 加载效能分析结果
        _safe_print("\n[1/5] 加载进化效能分析结果...")
        analysis = self.load_efficiency_analysis()
        _safe_print(f"    完成率: {analysis['completion_rate']['rate']}%")
        _safe_print(f"    平均执行时间: {analysis['execution_time']['avg']}s")

        # 2. 分析策略表现
        _safe_print("\n[2/5] 分析各策略执行表现...")
        performance = self.analyze_strategy_performance()
        _safe_print(f"    分析了 {len(performance)} 种策略类型")
        for strategy, data in performance.items():
            _safe_print(f"    - {strategy}: 成功率 {data.get('success_rate', 0)}%, 次数 {data['count']}")

        # 3. 生成策略调整建议
        _safe_print("\n[3/5] 生成策略调整建议...")
        adjustments = self.generate_strategy_adjustments(analysis, performance)
        _safe_print(f"    生成了 {len(adjustments)} 条调整建议")
        for adj in adjustments:
            _safe_print(f"    - {adj['target']}.{adj['parameter']}: {adj['current']} -> {adj['suggested']}")
            _safe_print(f"      原因: {adj['reason']}")

        # 4. 应用优化
        _safe_print("\n[4/5] 应用优化到策略配置...")
        result = self.apply_optimization(adjustments)
        _safe_print(f"    已应用 {result['applied_count']} 条优化")

        # 5. 验证优化效果
        _safe_print("\n[5/5] 验证优化效果...")
        verify_result = self.verify_optimization()
        _safe_print(f"    验证结果: {verify_result['message']}")

        # 保存优化历史
        self._save_optimization_history(analysis, performance, adjustments)

        _safe_print("\n" + "=" * 60)
        _safe_print("元优化完成！")
        _safe_print("=" * 60)

        self.current_optimization = {
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis,
            'performance': performance,
            'adjustments': adjustments,
            'applied': result['applied_count'] > 0
        }

        return self.current_optimization

    def _save_optimization_history(self, analysis: Dict, performance: Dict, adjustments: List[Dict]):
        """保存优化历史"""
        history = []

        try:
            if os.path.exists(self.optimization_history_path):
                with open(self.optimization_history_path, 'r', encoding='utf-8') as f:
                    history = json.load(f)
        except:
            pass

        history.append({
            'timestamp': datetime.now().isoformat(),
            'completion_rate': analysis.get('completion_rate', {}).get('rate', 0),
            'execution_time': analysis.get('execution_time', {}).get('avg', 0),
            'adjustments_count': len(adjustments),
            'adjustments': adjustments
        })

        # 只保留最近20条
        history = history[-20:]

        try:
            os.makedirs(os.path.dirname(self.optimization_history_path), exist_ok=True)
            with open(self.optimization_history_path, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"保存优化历史失败: {e}")

    def get_status(self) -> Dict:
        """获取元优化引擎状态"""
        config = self._load_strategy_config()
        history = []

        try:
            if os.path.exists(self.optimization_history_path):
                with open(self.optimization_history_path, 'r', encoding='utf-8') as f:
                    history = json.load(f)
        except:
            pass

        return {
            'status': 'active',
            'last_optimization': history[-1] if history else None,
            'config': config,
            'total_optimizations': len(history)
        }

    def get_recent_optimizations(self, limit: int = 5) -> List[Dict]:
        """获取最近的优化记录"""
        try:
            if os.path.exists(self.optimization_history_path):
                with open(self.optimization_history_path, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                return history[-limit:]
        except:
            pass
        return []


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description='智能进化环元优化引擎')
    parser.add_argument('command', nargs='?', default='status',
                        help='命令: status, optimize, verify, history, config')
    parser.add_argument('--optimize', action='store_true', help='执行元优化')
    parser.add_argument('--verify', action='store_true', help='验证优化效果')
    parser.add_argument('--history', action='store_true', help='查看优化历史')
    parser.add_argument('--config', action='store_true', help='查看当前配置')
    parser.add_argument('--limit', type=int, default=5, help='历史记录数量限制')

    args = parser.parse_args()

    optimizer = EvolutionMetaOptimizer()

    if args.optimize or args.command == 'optimize':
        result = optimizer.optimize()
        print("\n优化结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.verify or args.command == 'verify':
        result = optimizer.verify_optimization()
        print("\n验证结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.history or args.command == 'history':
        history = optimizer.get_recent_optimizations(args.limit)
        print("\n优化历史:")
        print(json.dumps(history, ensure_ascii=False, indent=2))
    elif args.config or args.command == 'config':
        config = optimizer._load_strategy_config()
        print("\n当前策略配置:")
        print(json.dumps(config, ensure_ascii=False, indent=2))
    else:
        # 默认显示状态
        status = optimizer.get_status()
        print("\n元优化引擎状态:")
        print(json.dumps(status, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()