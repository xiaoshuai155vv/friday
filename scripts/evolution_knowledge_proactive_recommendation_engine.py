#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环跨引擎知识主动推荐与智能预警引擎
在 round 447 完成的知识推理与问答引擎基础上，进一步构建知识主动推荐与智能预警能力。
让系统能够根据用户当前上下文主动推荐相关知识、预测用户可能需要的信息、主动预警潜在问题，
实现从「被动问答」到「主动推荐」的范式升级。让进化环能够像一位主动的顾问，
不仅响应查询，还能预见需求、提前准备。

功能：
1. 集成 round 447 知识推理引擎的问答能力
2. 上下文感知推荐（基于当前任务、执行状态、用户意图）
3. 知识关联推荐（基于当前知识条目推荐相关条目）
4. 进化趋势预警（基于历史预测未来潜在问题并推荐知识）
5. 主动推送机制（条件触发时主动推荐知识）
6. 推荐效果追踪（记录用户对推荐的反馈，持续优化）
7. 与进化驾驶舱深度集成（可视化推荐历史和效果）
8. 集成到 do.py 支持知识推荐、智能推荐、推荐知识、主动预警等关键词触发

Version: 1.0.0
"""

import os
import sys
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict
import threading

# 添加 scripts 目录到路径
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

# 尝试导入知识推理引擎
try:
    from evolution_cross_engine_knowledge_reasoning_engine import KnowledgeReasoningEngine
    KNOWLEDGE_REASONING_AVAILABLE = True
except ImportError:
    KNOWLEDGE_REASONING_AVAILABLE = False

# 项目目录
PROJECT_DIR = os.path.dirname(SCRIPTS_DIR)
RUNTIME_DIR = os.path.join(PROJECT_DIR, "runtime")
STATE_DIR = os.path.join(RUNTIME_DIR, "state")
LOGS_DIR = os.path.join(RUNTIME_DIR, "logs")

# 存储文件路径
RECOMMENDATION_HISTORY_FILE = os.path.join(STATE_DIR, "knowledge_recommendation_history.json")
RECOMMENDATION_FEEDBACK_FILE = os.path.join(STATE_DIR, "knowledge_recommendation_feedback.json")
RECOMMENDATION_CACHE_FILE = os.path.join(STATE_DIR, "knowledge_recommendation_cache.json")
CONTEXT_FILE = os.path.join(STATE_DIR, "current_context.json")
TREND_WARNING_FILE = os.path.join(STATE_DIR, "trend_warnings.json")


def _safe_print(text: str):
    """安全打印"""
    try:
        print(text)
    except UnicodeEncodeError:
        clean_text = re.sub(r'[^\x00-\x7F]+', '', text)
        print(clean_text)


class KnowledgeProactiveRecommendationEngine:
    """跨引擎知识主动推荐与智能预警引擎"""

    def __init__(self):
        self.knowledge_reasoning = None
        self.recommendation_history = self._load_recommendation_history()
        self.recommendation_feedback = self._load_recommendation_feedback()
        self.recommendation_cache = self._load_recommendation_cache()
        self.current_context = self._load_current_context()
        self.trend_warnings = self._load_trend_warnings()

        # 尝试初始化知识推理引擎
        if KNOWLEDGE_REASONING_AVAILABLE:
            try:
                self.knowledge_reasoning = KnowledgeReasoningEngine()
            except Exception as e:
                _safe_print(f"初始化知识推理引擎失败: {e}")

        # 推荐阈值配置
        self.config = {
            'min_relevance_score': 0.3,  # 最小相关度分数
            'max_recommendations': 5,     # 最大推荐数量
            'cache_ttl': 3600,            # 缓存有效期（秒）
            'warning_threshold': 0.7,    # 预警阈值
            'context_window': 10,         # 上下文窗口大小
        }

    def _load_recommendation_history(self) -> Dict:
        """加载推荐历史"""
        default = {
            'recommendations': [],  # [{timestamp, context, recommendations, accepted}]
            'last_updated': None
        }
        try:
            if os.path.exists(RECOMMENDATION_HISTORY_FILE):
                with open(RECOMMENDATION_HISTORY_FILE, 'r', encoding='utf-8') as f:
                    default.update(json.load(f))
        except Exception as e:
            _safe_print(f"加载推荐历史失败: {e}")
        return default

    def _save_recommendation_history(self):
        """保存推荐历史"""
        try:
            os.makedirs(os.path.dirname(RECOMMENDATION_HISTORY_FILE), exist_ok=True)
            self.recommendation_history['last_updated'] = datetime.now().isoformat()
            with open(RECOMMENDATION_HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.recommendation_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"保存推荐历史失败: {e}")

    def _load_recommendation_feedback(self) -> Dict:
        """加载推荐反馈"""
        default = {
            'feedback': [],  # [{timestamp, recommendation_id, action (accepted/dismissed/clicked)}]
            'stats': {
                'total': 0,
                'accepted': 0,
                'dismissed': 0,
                'clicked': 0
            }
        }
        try:
            if os.path.exists(RECOMMENDATION_FEEDBACK_FILE):
                with open(RECOMMENDATION_FEEDBACK_FILE, 'r', encoding='utf-8') as f:
                    default.update(json.load(f))
        except Exception as e:
            _safe_print(f"加载推荐反馈失败: {e}")
        return default

    def _save_recommendation_feedback(self):
        """保存推荐反馈"""
        try:
            os.makedirs(os.path.dirname(RECOMMENDATION_FEEDBACK_FILE), exist_ok=True)
            with open(RECOMMENDATION_FEEDBACK_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.recommendation_feedback, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"保存推荐反馈失败: {e}")

    def _load_recommendation_cache(self) -> Dict:
        """加载推荐缓存"""
        default = {'cache': {}, 'last_cleanup': None}
        try:
            if os.path.exists(RECOMMENDATION_CACHE_FILE):
                with open(RECOMMENDATION_CACHE_FILE, 'r', encoding='utf-8') as f:
                    default.update(json.load(f))
        except Exception as e:
            _safe_print(f"加载推荐缓存失败: {e}")
        return default

    def _save_recommendation_cache(self):
        """保存推荐缓存"""
        try:
            os.makedirs(os.path.dirname(RECOMMENDATION_CACHE_FILE), exist_ok=True)
            # 清理过期缓存
            now = datetime.now()
            if self.recommendation_cache.get('cache'):
                expired_keys = []
                for key, value in self.recommendation_cache['cache'].items():
                    cached_time = datetime.fromisoformat(value.get('cached_at', '2000-01-01'))
                    if (now - cached_time).total_seconds() > self.config['cache_ttl']:
                        expired_keys.append(key)
                for key in expired_keys:
                    del self.recommendation_cache['cache'][key]
            self.recommendation_cache['last_cleanup'] = now.isoformat()
            with open(RECOMMENDATION_CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.recommendation_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"保存推荐缓存失败: {e}")

    def _load_current_context(self) -> Dict:
        """加载当前上下文"""
        default = {
            'current_task': None,
            'recent_queries': [],
            'active_engines': [],
            'system_state': {},
            'last_interaction': None
        }
        try:
            if os.path.exists(CONTEXT_FILE):
                with open(CONTEXT_FILE, 'r', encoding='utf-8') as f:
                    default.update(json.load(f))
        except Exception as e:
            _safe_print(f"加载当前上下文失败: {e}")
        return default

    def _load_trend_warnings(self) -> Dict:
        """加载趋势预警"""
        default = {
            'warnings': [],  # [{timestamp, type, severity, message, related_knowledge}]
            'last_check': None
        }
        try:
            if os.path.exists(TREND_WARNING_FILE):
                with open(TREND_WARNING_FILE, 'r', encoding='utf-8') as f:
                    default.update(json.load(f))
        except Exception as e:
            _safe_print(f"加载趋势预警失败: {e}")
        return default

    def update_context(self, context_type: str, context_data: Dict):
        """更新当前上下文"""
        self.current_context[context_type] = context_data
        self.current_context['last_interaction'] = datetime.now().isoformat()

        # 添加到最近查询
        if context_type == 'query':
            self.current_context['recent_queries'].append(context_data.get('query', ''))
            if len(self.current_context['recent_queries']) > self.config['context_window']:
                self.current_context['recent_queries'] = self.current_context['recent_queries'][-self.config['context_window']:]

        # 保存上下文
        try:
            os.makedirs(os.path.dirname(CONTEXT_FILE), exist_ok=True)
            with open(CONTEXT_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.current_context, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"保存上下文失败: {e}")

    def get_context_aware_recommendations(self, current_query: str = None) -> List[Dict]:
        """获取上下文感知推荐"""
        recommendations = []

        # 1. 基于当前查询推荐
        if current_query:
            recommendations.extend(self._query_based_recommendations(current_query))

        # 2. 基于历史查询推荐
        recommendations.extend(self._history_based_recommendations())

        # 3. 基于当前任务推荐
        if self.current_context.get('current_task'):
            recommendations.extend(self._task_based_recommendations())

        # 4. 去重并排序
        seen = set()
        unique_recs = []
        for rec in recommendations:
            rec_key = rec.get('id', rec.get('title', ''))
            if rec_key not in seen:
                seen.add(rec_key)
                unique_recs.append(rec)

        # 按相关度排序
        unique_recs.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

        return unique_recs[:self.config['max_recommendations']]

    def _query_based_recommendations(self, query: str) -> List[Dict]:
        """基于查询的推荐"""
        recs = []

        # 检查缓存
        cache_key = f"query_{hash(query)}"
        if cache_key in self.recommendation_cache.get('cache', {}):
            cached = self.recommendation_cache['cache'][cache_key]
            cached_time = datetime.fromisoformat(cached.get('cached_at', '2000-01-01'))
            if (datetime.now() - cached_time).total_seconds() < self.config['cache_ttl']:
                return cached.get('recommendations', [])

        # 如果有知识推理引擎，使用它来查找相关知识
        if self.knowledge_reasoning:
            try:
                # 获取与查询相关的知识
                related = self.knowledge_reasoning.answer_question(f"与'{query}'相关的知识有哪些？")
                if related:
                    recs.append({
                        'id': f"query_related_{hash(query)}",
                        'title': f"关于 '{query}' 的相关知识",
                        'content': related[:200] + "..." if len(related) > 200 else related,
                        'relevance_score': 0.9,
                        'type': 'query_related',
                        'source': 'knowledge_reasoning'
                    })
            except Exception as e:
                _safe_print(f"查询相关知识失败: {e}")

        # 缓存结果
        if cache_key not in self.recommendation_cache.get('cache', {}):
            self.recommendation_cache.setdefault('cache', {})[cache_key] = {
                'recommendations': recs,
                'cached_at': datetime.now().isoformat()
            }
            self._save_recommendation_cache()

        return recs

    def _history_based_recommendations(self) -> List[Dict]:
        """基于历史的推荐"""
        recs = []

        # 分析最近查询模式，推荐常见相关主题
        recent_queries = self.current_context.get('recent_queries', [])
        if len(recent_queries) >= 2:
            # 发现查询模式，推荐关联主题
            query_terms = set()
            for q in recent_queries[-5:]:
                query_terms.update(q.split())

            if '进化' in query_terms or 'evolution' in query_terms:
                recs.append({
                    'id': 'history_evolution_trend',
                    'title': '进化趋势分析',
                    'content': '查看最新的进化趋势和预测',
                    'relevance_score': 0.7,
                    'type': 'history_related',
                    'source': 'pattern_analysis'
                })

            if '知识' in query_terms or 'knowledge' in query_terms:
                recs.append({
                    'id': 'history_knowledge_graph',
                    'title': '知识图谱探索',
                    'content': '探索知识之间的关联关系',
                    'relevance_score': 0.6,
                    'type': 'history_related',
                    'source': 'pattern_analysis'
                })

        return recs

    def _task_based_recommendations(self) -> List[Dict]:
        """基于当前任务的推荐"""
        recs = []
        current_task = self.current_context.get('current_task', {})

        if isinstance(current_task, dict):
            task_type = current_task.get('type', '')
            task_goal = current_task.get('goal', '')

            # 根据任务类型推荐相关知识
            if '优化' in task_goal or 'optimize' in task_goal.lower():
                recs.append({
                    'id': 'task_optimization_knowledge',
                    'title': '优化相关知识',
                    'content': '系统优化相关的最佳实践和方法论',
                    'relevance_score': 0.8,
                    'type': 'task_related',
                    'source': 'task_analysis'
                })

            if '执行' in task_type or 'execution' in task_type.lower():
                recs.append({
                    'id': 'task_execution_knowledge',
                    'title': '执行相关知识',
                    'content': '任务执行和调度相关的知识和经验',
                    'relevance_score': 0.7,
                    'type': 'task_related',
                    'source': 'task_analysis'
                })

        return recs

    def get_association_recommendations(self, knowledge_id: str) -> List[Dict]:
        """获取知识关联推荐"""
        recs = []

        # 基于知识ID查找关联知识
        if self.knowledge_reasoning:
            try:
                # 询问与当前知识相关的其他知识
                related = self.knowledge_reasoning.answer_question(f"与这个知识点相关的其他重要知识有哪些？")
                if related:
                    recs.append({
                        'id': f"association_{knowledge_id}",
                        'title': '相关知识推荐',
                        'content': related[:200] + "..." if len(related) > 200 else related,
                        'relevance_score': 0.85,
                        'type': 'association',
                        'source': 'knowledge_graph'
                    })
            except Exception as e:
                _safe_print(f"获取关联知识失败: {e}")

        return recs

    def check_trend_warnings(self) -> List[Dict]:
        """检查趋势预警"""
        warnings = []

        # 1. 检查进化执行趋势
        evolution_history = self._get_evolution_history()
        if evolution_history:
            # 分析最近进化的成功率
            recent_success_rate = self._calculate_success_rate(evolution_history)
            if recent_success_rate < self.config['warning_threshold']:
                warnings.append({
                    'timestamp': datetime.now().isoformat(),
                    'type': 'evolution_success_rate',
                    'severity': 'high' if recent_success_rate < 0.5 else 'medium',
                    'message': f'近期进化成功率较低（{recent_success_rate:.1%}），建议检查进化策略',
                    'related_knowledge': ['进化策略优化', '方法论调整'],
                    'recommendation': '查看进化策略优化相关知识'
                })

            # 检查是否有重复进化
            duplicates = self._find_duplicate_evolutions(evolution_history)
            if duplicates:
                warnings.append({
                    'timestamp': datetime.now().isoformat(),
                    'type': 'duplicate_evolution',
                    'severity': 'low',
                    'message': f'检测到 {len(duplicates)} 个可能重复的进化方向',
                    'related_knowledge': ['进化去重', '知识整合'],
                    'recommendation': '考虑合并重复的进化方向'
                })

        # 2. 检查系统健康趋势
        system_health = self._get_system_health()
        if system_health.get('health_score', 100) < 70:
            warnings.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'system_health',
                'severity': 'high',
                'message': f'系统健康度较低（{system_health.get("health_score", 0)}）',
                'related_knowledge': ['健康保障', '自愈能力'],
                'recommendation': '查看系统健康保障相关知识'
            })

        # 保存预警
        if warnings:
            self.trend_warnings['warnings'].extend(warnings)
            self.trend_warnings['last_check'] = datetime.now().isoformat()
            try:
                os.makedirs(os.path.dirname(TREND_WARNING_FILE), exist_ok=True)
                with open(TREND_WARNING_FILE, 'w', encoding='utf-8') as f:
                    json.dump(self.trend_warnings, f, ensure_ascii=False, indent=2)
            except Exception as e:
                _safe_print(f"保存预警失败: {e}")

        return warnings

    def _get_evolution_history(self) -> List[Dict]:
        """获取进化历史"""
        history = []
        try:
            # 尝试从知识索引获取进化历史
            history_dir = os.path.join(STATE_DIR, "evolution_completed_*.json")
            import glob
            for f in glob.glob(os.path.join(STATE_DIR, "evolution_completed_ev_*.json")):
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        history.append(data)
                except:
                    pass
        except Exception as e:
            _safe_print(f"获取进化历史失败: {e}")
        return history

    def _calculate_success_rate(self, history: List[Dict]) -> float:
        """计算成功率"""
        if not history:
            return 1.0

        completed = [h for h in history if h.get('是否完成') == '已完成']
        if not completed:
            return 1.0

        return len(completed) / len(history)

    def _find_duplicate_evolutions(self, history: List[Dict]) -> List[Tuple]:
        """查找重复进化"""
        # 简单实现：检查目标相似的进化
        goals = {}
        duplicates = []

        for h in history:
            goal = h.get('current_goal', '')
            if goal:
                # 简单相似度检查
                for existing_goal, existing_data in goals.items():
                    if self._calculate_similarity(goal, existing_goal) > 0.8:
                        duplicates.append((existing_goal, goal))

                goals[goal] = h

        return duplicates

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        set1 = set(text1.lower().split())
        set2 = set(text2.lower().split())
        if not set1 or not set2:
            return 0.0
        return len(set1 & set2) / len(set1 | set2)

    def _get_system_health(self) -> Dict:
        """获取系统健康状态"""
        health = {'health_score': 100}
        try:
            # 尝试读取健康状态文件
            health_file = os.path.join(STATE_DIR, "system_health.json")
            if os.path.exists(health_file):
                with open(health_file, 'r', encoding='utf-8') as f:
                    health = json.load(f)
        except Exception as e:
            _safe_print(f"获取系统健康状态失败: {e}")
        return health

    def add_recommendation(self, context: Dict, recommendations: List[Dict]):
        """添加推荐到历史"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'context': context,
            'recommendations': recommendations,
            'accepted': []
        }
        self.recommendation_history['recommendations'].append(entry)

        # 限制历史长度
        max_history = 100
        if len(self.recommendation_history['recommendations']) > max_history:
            self.recommendation_history['recommendations'] = \
                self.recommendation_history['recommendations'][-max_history:]

        self._save_recommendation_history()

    def record_feedback(self, recommendation_id: str, action: str):
        """记录用户反馈"""
        feedback_entry = {
            'timestamp': datetime.now().isoformat(),
            'recommendation_id': recommendation_id,
            'action': action  # 'accepted', 'dismissed', 'clicked'
        }
        self.recommendation_feedback['feedback'].append(feedback_entry)

        # 更新统计
        self.recommendation_feedback['stats']['total'] += 1
        if action == 'accepted':
            self.recommendation_feedback['stats']['accepted'] += 1
        elif action == 'dismissed':
            self.recommendation_feedback['stats']['dismissed'] += 1
        elif action == 'clicked':
            self.recommendation_feedback['stats']['clicked'] += 1

        self._save_recommendation_feedback()

    def get_recommendation_stats(self) -> Dict:
        """获取推荐统计"""
        stats = self.recommendation_feedback.get('stats', {})
        if stats.get('total', 0) > 0:
            stats['acceptance_rate'] = stats.get('accepted', 0) / stats['total']
            stats['click_rate'] = stats.get('clicked', 0) / stats['total']
        else:
            stats['acceptance_rate'] = 0
            stats['click_rate'] = 0
        return stats

    def proactive_recommend(self, trigger_type: str, context: Dict = None) -> List[Dict]:
        """主动推荐（条件触发）"""
        recommendations = []

        if trigger_type == 'task_start':
            # 任务开始时推荐相关知识
            if context and context.get('task_type'):
                recommendations = self.get_context_aware_recommendations(
                    current_query=context.get('task_type')
                )

        elif trigger_type == 'query_complete':
            # 查询完成后推荐关联知识
            if context and context.get('query_result'):
                # 基于查询结果推荐
                recommendations = self._query_based_recommendations(
                    context.get('last_query', '')
                )

        elif trigger_type == 'periodic':
            # 定期推荐基于历史的知识
            recommendations = self.get_context_aware_recommendations()

        elif trigger_type == 'warning':
            # 预警触发时推荐相关知识
            warnings = self.check_trend_warnings()
            for warning in warnings:
                if warning.get('related_knowledge'):
                    recommendations.append({
                        'id': f"warning_knowledge_{warning['type']}",
                        'title': warning.get('message', '预警相关知识'),
                        'content': f"建议查看：{', '.join(warning.get('related_knowledge', []))}",
                        'relevance_score': 0.9,
                        'type': 'warning_related',
                        'source': 'trend_analysis',
                        'warning_type': warning.get('type')
                    })

        # 记录推荐
        if recommendations:
            self.add_recommendation(
                context={'trigger': trigger_type, **(context or {})},
                recommendations=recommendations
            )

        return recommendations


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(
        description='智能全场景进化环跨引擎知识主动推荐与智能预警引擎'
    )
    parser.add_argument('--recommend', type=str, help='获取上下文感知推荐（可指定查询关键词）')
    parser.add_argument('--associate', type=str, help='获取知识关联推荐（指定知识ID）')
    parser.add_argument('--warning', action='store_true', help='检查趋势预警')
    parser.add_argument('--stats', action='store_true', help='获取推荐统计')
    parser.add_argument('--proactive', type=str, help='主动推荐（触发类型：task_start/query_complete/periodic/warning）')
    parser.add_argument('--context', type=str, help='JSON格式的上下文数据')
    parser.add_argument('--update-context', type=str, help='更新上下文（类型:数据）')

    args = parser.parse_args()

    engine = KnowledgeProactiveRecommendationEngine()

    if args.recommend:
        # 上下文感知推荐
        recs = engine.get_context_aware_recommendations(current_query=args.recommend)
        _safe_print("=" * 50)
        _safe_print("知识推荐结果：")
        _safe_print("=" * 50)
        for i, rec in enumerate(recs, 1):
            _safe_print(f"\n{i}. {rec.get('title', '未命名')}")
            _safe_print(f"   类型: {rec.get('type', 'unknown')}")
            _safe_print(f"   相关度: {rec.get('relevance_score', 0):.2f}")
            _safe_print(f"   内容: {rec.get('content', '')[:100]}...")

    elif args.associate:
        # 知识关联推荐
        recs = engine.get_association_recommendations(args.associate)
        _safe_print("=" * 50)
        _safe_print("关联知识推荐：")
        _safe_print("=" * 50)
        for i, rec in enumerate(recs, 1):
            _safe_print(f"\n{i}. {rec.get('title', '未命名')}")
            _safe_print(f"   内容: {rec.get('content', '')[:100]}...")

    elif args.warning:
        # 趋势预警
        warnings = engine.check_trend_warnings()
        _safe_print("=" * 50)
        _safe_print("趋势预警：")
        _safe_print("=" * 50)
        if warnings:
            for w in warnings:
                _safe_print(f"\n类型: {w.get('type')}")
                _safe_print(f"严重程度: {w.get('severity')}")
                _safe_print(f"消息: {w.get('message')}")
                _safe_print(f"建议: {w.get('recommendation')}")
        else:
            _safe_print("未检测到预警")

    elif args.stats:
        # 推荐统计
        stats = engine.get_recommendation_stats()
        _safe_print("=" * 50)
        _safe_print("推荐统计：")
        _safe_print("=" * 50)
        _safe_print(f"总推荐次数: {stats.get('total', 0)}")
        _safe_print(f"接受次数: {stats.get('accepted', 0)}")
        _safe_print(f"忽略次数: {stats.get('dismissed', 0)}")
        _safe_print(f"点击次数: {stats.get('clicked', 0)}")
        _safe_print(f"接受率: {stats.get('acceptance_rate', 0):.1%}")
        _safe_print(f"点击率: {stats.get('click_rate', 0):.1%}")

    elif args.proactive:
        # 主动推荐
        context = {}
        if args.context:
            try:
                context = json.loads(args.context)
            except:
                _safe_print("上下文 JSON 解析失败")

        recs = engine.proactive_recommend(args.proactive, context)
        _safe_print("=" * 50)
        _safe_print(f"主动推荐（{args.proactive}）：")
        _safe_print("=" * 50)
        for i, rec in enumerate(recs, 1):
            _safe_print(f"\n{i}. {rec.get('title', '未命名')}")
            _safe_print(f"   内容: {rec.get('content', '')[:100]}...")

    elif args.update_context:
        # 更新上下文
        if ':' in args.update_context:
            context_type, context_data = args.update_context.split(':', 1)
            try:
                context_data = json.loads(context_data)
            except:
                context_data = {'data': context_data}
            engine.update_context(context_type, context_data)
            _safe_print(f"已更新上下文: {context_type}")
        else:
            _safe_print("请使用格式：类型:JSON数据")

    else:
        # 默认：显示帮助
        parser.print_help()
        _safe_print("\n示例：")
        _safe_print("  python evolution_knowledge_proactive_recommendation_engine.py --recommend '进化策略'")
        _safe_print("  python evolution_knowledge_proactive_recommendation_engine.py --warning")
        _safe_print("  python evolution_knowledge_proactive_recommendation_engine.py --stats")
        _safe_print("  python evolution_knowledge_proactive_recommendation_engine.py --proactive periodic")


if __name__ == '__main__':
    main()