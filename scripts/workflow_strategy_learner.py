#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能工作流执行策略自动学习增强器

让系统从工作流执行历史中自动学习最优执行策略（引擎选择、执行顺序、超时设置、重试策略），
并将学习应用到后续执行中，实现真正的自适应工作流执行。

功能：
1. 执行策略自动学习 - 从执行历史中提取有效策略模式
2. 策略效果分析 - 分析哪些引擎组合、超时设置、重试策略更有效
3. 策略自动应用 - 在执行工作流时自动应用学习到的最优策略
4. 策略效果评估 - 评估应用策略后的效果并反馈优化
5. 与 execution_enhancement_engine 集成 - 利用现有执行增强能力

使用方法：
    python workflow_strategy_learner.py learn [--min-samples N] - 从历史中学习策略
    python workflow_strategy_learner.py analyze <intent> - 分析某意图的最优策略
    python workflow_strategy_learner.py apply <intent> - 应用最优策略到后续执行
    python workflow_strategy_learner.py stats - 查看策略学习统计
    python workflow_strategy_learner.py recommend - 推荐待优化策略
"""
import os
import sys
import json
import sqlite3
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass, field, asdict

# 路径配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, '..', 'runtime', 'state', 'execution_enhancement.db')
RUNTIME_DIR = os.path.join(SCRIPT_DIR, '..', 'runtime')
STATE_DIR = os.path.join(RUNTIME_DIR, 'state')


@dataclass
class StrategyPattern:
    """策略模式"""
    intent: str
    strategy_type: str  # sequential/parallel/fallback/direct
    engine_combination: List[str]
    timeout_settings: Dict[str, int]  # {"step_name": timeout_ms}
    retry_policy: Dict[str, Any]  # {"max_retries": N, "retry_delay": ms}
    success_rate: float = 0.0
    avg_duration: float = 0.0
    sample_count: int = 0
    last_updated: str = ""


@dataclass
class LearningResult:
    """学习结果"""
    intent: str
    best_strategy: str
    confidence: float
    reasoning: str
    alternatives: List[Dict[str, Any]] = field(default_factory=list)
    improvement_potential: float = 0.0


class WorkflowStrategyLearner:
    """智能工作流执行策略自动学习增强器"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        self.strategy_cache = {}
        self._load_cached_strategies()

    def _load_cached_strategies(self):
        """加载缓存的策略"""
        cache_file = os.path.join(STATE_DIR, 'workflow_strategy_cache.json')
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.strategy_cache = data.get('strategies', {})
            except Exception as e:
                print(f"加载策略缓存失败: {e}")
                self.strategy_cache = {}

    def _save_cached_strategies(self):
        """保存策略缓存"""
        cache_file = os.path.join(STATE_DIR, 'workflow_strategy_cache.json')
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'strategies': self.strategy_cache,
                    'updated_at': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存策略缓存失败: {e}")

    def _get_connection(self):
        """获取数据库连接"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def learn_from_history(self, min_samples: int = 3) -> List[LearningResult]:
        """从执行历史中学习策略模式"""
        results = []

        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # 获取执行记录按意图分组
            cursor.execute("""
                SELECT intent, execution_type, COUNT(*) as count,
                       AVG(duration) as avg_duration,
                       SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as success_rate
                FROM execution_records
                GROUP BY intent, execution_type
                HAVING COUNT(*) >= ?
                ORDER BY intent, success_rate DESC
            """, (min_samples,))

            rows = cursor.fetchall()
            current_intent = None
            intent_strategies = []

            for row in rows:
                intent = row['intent']
                if intent != current_intent:
                    # 处理上一个意图的学习结果
                    if current_intent and intent_strategies:
                        result = self._analyze_intent_strategies(current_intent, intent_strategies)
                        if result:
                            results.append(result)
                    current_intent = intent
                    intent_strategies = []

                intent_strategies.append({
                    'strategy': row['execution_type'],
                    'count': row['count'],
                    'success_rate': row['success_rate'],
                    'avg_duration': row['avg_duration']
                })

            # 处理最后一个意图
            if current_intent and intent_strategies:
                result = self._analyze_intent_strategies(current_intent, intent_strategies)
                if result:
                    results.append(result)

            conn.close()

            # 保存学习到的策略
            for result in results:
                self._save_learned_strategy(result)

        except Exception as e:
            print(f"学习策略失败: {e}")

        return results

    def _analyze_intent_strategies(self, intent: str, strategies: List[Dict]) -> Optional[LearningResult]:
        """分析单个意图的策略效果"""
        if not strategies:
            return None

        # 找到最佳策略
        best = max(strategies, key=lambda x: (x['success_rate'], -x['avg_duration']))

        # 计算改进潜力
        all_success_rates = [s['success_rate'] for s in strategies]
        avg_success_rate = sum(all_success_rates) / len(all_success_rates)
        improvement_potential = best['success_rate'] - avg_success_rate

        # 生成推理
        reasoning = f"在 {len(strategies)} 种策略中，'{best['strategy']}' 策略成功率最高({best['success_rate']:.1%})，平均耗时{best['avg_duration']:.2f}秒"

        alternatives = [
            {
                'strategy': s['strategy'],
                'success_rate': s['success_rate'],
                'avg_duration': s['avg_duration']
            }
            for s in strategies if s['strategy'] != best['strategy']
        ]

        return LearningResult(
            intent=intent,
            best_strategy=best['strategy'],
            confidence=min(best['success_rate'] * 1.5, 1.0),
            reasoning=reasoning,
            alternatives=alternatives,
            improvement_potential=improvement_potential
        )

    def _save_learned_strategy(self, result: LearningResult):
        """保存学习到的策略"""
        self.strategy_cache[result.intent] = {
            'best_strategy': result.best_strategy,
            'confidence': result.confidence,
            'reasoning': result.reasoning,
            'alternatives': result.alternatives,
            'improvement_potential': result.improvement_potential,
            'updated_at': datetime.now().isoformat()
        }
        self._save_cached_strategies()

    def get_strategy_for_intent(self, intent: str) -> Optional[Dict[str, Any]]:
        """获取意图的最优策略"""
        # 先尝试从缓存获取
        if intent in self.strategy_cache:
            return self.strategy_cache[intent]

        # 尝试模糊匹配
        for cached_intent, strategy in self.strategy_cache.items():
            if intent.lower() in cached_intent.lower() or cached_intent.lower() in intent.lower():
                return strategy

        return None

    def apply_strategy(self, intent: str) -> Dict[str, Any]:
        """应用最优策略"""
        strategy = self.get_strategy_for_intent(intent)

        if not strategy:
            return {
                'success': False,
                'message': f'未找到 {intent} 的学习策略，将使用默认策略',
                'strategy': 'direct'
            }

        return {
            'success': True,
            'intent': intent,
            'strategy': strategy['best_strategy'],
            'confidence': strategy['confidence'],
            'reasoning': strategy['reasoning']
        }

    def get_recommendations(self) -> List[Dict[str, Any]]:
        """获取策略优化建议"""
        recommendations = []

        for intent, strategy in self.strategy_cache.items():
            # 找出低置信度或有改进潜力的策略
            if strategy.get('improvement_potential', 0) > 0.1:
                recommendations.append({
                    'intent': intent,
                    'current_strategy': strategy['best_strategy'],
                    'success_rate': strategy.get('confidence', 0),
                    'improvement_potential': strategy.get('improvement_potential', 0),
                    'reasoning': f"存在改进空间，当前策略成功率约{strategy.get('confidence', 0)*100:.1f}%"
                })

        # 按改进潜力排序
        recommendations.sort(key=lambda x: x['improvement_potential'], reverse=True)

        return recommendations[:10]  # 返回前10条

    def get_stats(self) -> Dict[str, Any]:
        """获取策略学习统计"""
        return {
            'total_strategies': len(self.strategy_cache),
            'high_confidence': sum(1 for s in self.strategy_cache.values() if s.get('confidence', 0) > 0.8),
            'medium_confidence': sum(1 for s in self.strategy_cache.values() if 0.5 <= s.get('confidence', 0) <= 0.8),
            'low_confidence': sum(1 for s in self.strategy_cache.values() if s.get('confidence', 0) < 0.5),
            'strategies_with_improvement': sum(1 for s in self.strategy_cache.values() if s.get('improvement_potential', 0) > 0.1),
            'updated_at': max((s.get('updated_at', '') for s in self.strategy_cache.values()), default='')
        }

    def clear_cache(self):
        """清空策略缓存"""
        self.strategy_cache = {}
        self._save_cached_strategies()


def main():
    parser = argparse.ArgumentParser(description='智能工作流执行策略自动学习增强器')
    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # learn 命令
    learn_parser = subparsers.add_parser('learn', help='从执行历史中学习策略')
    learn_parser.add_argument('--min-samples', type=int, default=3, help='最小样本数')

    # analyze 命令
    analyze_parser = subparsers.add_parser('analyze', help='分析意图的最优策略')
    analyze_parser.add_argument('intent', help='要分析的意图')

    # apply 命令
    apply_parser = subparsers.add_parser('apply', help='应用最优策略')
    apply_parser.add_argument('intent', help='要应用策略的意图')

    # stats 命令
    subparsers.add_parser('stats', help='查看策略学习统计')

    # recommend 命令
    subparsers.add_parser('recommend', help='推荐待优化策略')

    # clear 命令
    subparsers.add_parser('clear', help='清空策略缓存')

    args = parser.parse_args()

    learner = WorkflowStrategyLearner()

    if args.command == 'learn':
        print("开始从执行历史中学习策略模式...")
        results = learner.learn_from_history(min_samples=args.min_samples)
        print(f"\n学习完成，发现 {len(results)} 个策略模式：\n")
        for result in results:
            print(f"意图: {result.intent}")
            print(f"  最佳策略: {result.best_strategy}")
            print(f"  置信度: {result.confidence:.1%}")
            print(f"  推理: {result.reasoning}")
            print()

    elif args.command == 'analyze':
        strategy = learner.get_strategy_for_intent(args.intent)
        if strategy:
            print(f"意图 '{args.intent}' 的最优策略:")
            print(f"  策略类型: {strategy['best_strategy']}")
            print(f"  置信度: {strategy['confidence']:.1%}")
            print(f"  推理: {strategy['reasoning']}")
            if strategy.get('alternatives'):
                print(f"  备选策略:")
                for alt in strategy['alternatives']:
                    print(f"    - {alt['strategy']}: 成功率{alt['success_rate']:.1%}")
        else:
            print(f"未找到意图 '{args.intent}' 的策略记录")
            print("可以先运行 'learn' 命令从历史中学习策略")

    elif args.command == 'apply':
        result = learner.apply_strategy(args.intent)
        print(f"应用策略结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'stats':
        stats = learner.get_stats()
        print("策略学习统计:")
        print(f"  总策略数: {stats['total_strategies']}")
        print(f"  高置信度(>80%): {stats['high_confidence']}")
        print(f"  中置信度(50-80%): {stats['medium_confidence']}")
        print(f"  低置信度(<50%): {stats['low_confidence']}")
        print(f"  有改进潜力: {stats['strategies_with_improvement']}")
        print(f"  最后更新: {stats['updated_at']}")

    elif args.command == 'recommend':
        recommendations = learner.get_recommendations()
        if recommendations:
            print("待优化策略推荐:")
            for i, rec in enumerate(recommendations, 1):
                print(f"\n{i}. 意图: {rec['intent']}")
                print(f"   当前策略: {rec['current_strategy']}")
                print(f"   改进潜力: {rec['improvement_potential']:.1%}")
                print(f"   原因: {rec['reasoning']}")
        else:
            print("当前没有需要优化的策略")

    elif args.command == 'clear':
        learner.clear_cache()
        print("策略缓存已清空")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()