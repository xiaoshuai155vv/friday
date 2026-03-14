#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化知识主动推理与创新发现引擎
将知识传承遗忘引擎与知识图谱推理引擎深度融合，
实现跨轮次知识的深度推理与主动发现能力。
让系统能够主动从已有知识中发现隐藏的关联、预测进化趋势、发现创新机会，
形成「知识积累→主动推理→创新发现→价值实现」的完整闭环。

功能：
1. 跨轮次知识深度关联分析 - 融合知识传承与图谱推理
2. 进化趋势预测 - 基于历史模式预测未来进化方向
3. 创新机会主动发现 - 知识组合创新、潜在优化点
4. 价值实现路径推荐 - 从发现到实现的完整闭环
5. 与 do.py 深度集成，支持关键词触发

Version: 1.0.0

依赖：
- evolution_knowledge_inheritance_forgetting_engine.py (round 347)
- evolution_knowledge_graph_reasoning.py (round 298)
- evolution_cross_round_knowledge_fusion_engine.py (round 332)
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict
import math

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


class KnowledgeActiveReasoningEngine:
    """进化知识主动推理与创新发现引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.project_root = PROJECT_ROOT
        self.runtime_dir = os.path.join(self.project_root, "runtime")
        self.state_dir = os.path.join(self.runtime_dir, "state")

        # 数据库路径
        self.kg_db_path = os.path.join(self.state_dir, "knowledge_value.db")
        self.graph_db_path = os.path.join(self.runtime_dir, "knowledge_graph", "evolution_kg.json")
        self.reasoning_state_path = os.path.join(self.state_dir, "knowledge_active_reasoning_state.json")

        # 配置
        self.config = self._load_config()

        # 初始化数据库
        self._init_reasoning_db()

    def _load_config(self) -> Dict:
        """加载配置"""
        default_config = {
            # 推理配置
            'deep_reasoning_depth': 3,              # 推理深度
            'association_threshold': 0.3,           # 关联阈值
            'innovation_min_score': 0.6,             # 创新分数阈值

            # 预测配置
            'trend_prediction_window': 20,           # 趋势预测窗口（轮）
            'trend_confidence_threshold': 0.5,       # 趋势置信度阈值

            # 创新发现配置
            'max_innovation_suggestions': 10,         # 最大创新建议数
            'knowledge_combination_count': 3,       # 知识组合数量

            # 自动执行
            'auto_reasoning_enabled': True,          # 自动推理启用
            'auto_innovation_discovery_enabled': True,  # 自动创新发现启用
            'reasoning_interval': 10,                # 推理间隔（轮）
        }

        config_path = os.path.join(self.state_dir, "knowledge_active_reasoning_config.json")
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    default_config.update(saved_config)
        except Exception as e:
            _safe_print(f"加载配置失败: {e}")

        return default_config

    def _save_config(self, config: Dict):
        """保存配置"""
        config_path = os.path.join(self.state_dir, "knowledge_active_reasoning_config.json")
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"保存配置失败: {e}")

    def _init_reasoning_db(self):
        """初始化推理数据库"""
        try:
            os.makedirs(self.state_dir, exist_ok=True)

            # 创建推理结果表
            conn = sqlite3.connect(self.kg_db_path)
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reasoning_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reasoning_type TEXT,
                    reasoning_round INTEGER,
                    input_knowledge_ids TEXT,
                    output_insights TEXT,
                    innovation_score REAL,
                    implemented INTEGER DEFAULT 0,
                    created_at TEXT
                )
            """)

            # 创建创新发现表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS innovation_discoveries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    discovery_type TEXT,
                    description TEXT,
                    related_knowledge_ids TEXT,
                    innovation_score REAL,
                    status TEXT DEFAULT 'discovered',
                    implemented_at TEXT,
                    created_at TEXT
                )
            """)

            # 创建趋势预测表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trend_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prediction_type TEXT,
                    predicted_round INTEGER,
                    prediction_content TEXT,
                    confidence REAL,
                    actual_result TEXT,
                    accuracy REAL,
                    created_at TEXT
                )
            """)

            conn.commit()
            conn.close()

        except Exception as e:
            _safe_print(f"初始化推理数据库失败: {e}")

    def get_current_round(self) -> int:
        """获取当前进化轮次"""
        try:
            db_path = os.path.join(self.state_dir, "evolution_history.db")
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT MAX(round_number) FROM evolution_rounds")
                result = cursor.fetchone()
                conn.close()
                if result and result[0]:
                    return result[0]
        except Exception as e:
            _safe_print(f"获取当前轮次失败: {e}")
        return 0

    def load_knowledge_data(self) -> Dict:
        """加载知识数据（从传承遗忘引擎和图谱引擎）"""
        knowledge_data = {
            'all_knowledge': [],
            'high_value_knowledge': [],
            'recent_knowledge': [],
            'knowledge_relationships': []
        }

        try:
            # 从知识价值数据库加载
            if os.path.exists(self.kg_db_path):
                conn = sqlite3.connect(self.kg_db_path)
                cursor = conn.cursor()

                # 获取所有活跃知识
                cursor.execute("""
                    SELECT knowledge_id, knowledge_type, category, value_score,
                           use_count, last_access_round, creation_round
                    FROM knowledge_values
                    WHERE is_forgotten = 0
                    ORDER BY value_score DESC
                """)

                rows = cursor.fetchall()
                for row in rows:
                    knowledge_data['all_knowledge'].append({
                        'id': row[0],
                        'type': row[1],
                        'category': row[2],
                        'value_score': row[3],
                        'use_count': row[4],
                        'last_access_round': row[5],
                        'creation_round': row[6]
                    })

                # 获取高价值知识（top 20%）
                threshold = len(knowledge_data['all_knowledge']) // 5
                knowledge_data['high_value_knowledge'] = knowledge_data['all_knowledge'][:max(threshold, 5)]

                # 获取最近知识（最近20轮）
                current_round = self.get_current_round()
                knowledge_data['recent_knowledge'] = [
                    k for k in knowledge_data['all_knowledge']
                    if current_round - k.get('creation_round', 0) <= 20
                ]

                # 获取传承关系
                cursor.execute("""
                    SELECT source_round, target_round, knowledge_id, inheritance_type
                    FROM inheritance_records
                    ORDER BY source_round DESC
                    LIMIT 100
                """)

                inheritance_rows = cursor.fetchall()
                for row in inheritance_rows:
                    knowledge_data['knowledge_relationships'].append({
                        'source_round': row[0],
                        'target_round': row[1],
                        'knowledge_id': row[2],
                        'type': row[3]
                    })

                conn.close()

            # 从知识图谱加载
            if os.path.exists(self.graph_db_path):
                try:
                    with open(self.graph_db_path, 'r', encoding='utf-8') as f:
                        kg_data = json.load(f)
                        knowledge_data['graph_nodes'] = kg_data.get('nodes', [])
                        knowledge_data['graph_edges'] = kg_data.get('edges', [])
                except Exception as e:
                    _safe_print(f"加载知识图谱失败: {e}")

        except Exception as e:
            _safe_print(f"加载知识数据失败: {e}")

        return knowledge_data

    def analyze_knowledge_associations(self, knowledge_data: Dict) -> Dict:
        """分析知识间的深度关联"""
        associations = []
        all_knowledge = knowledge_data.get('all_knowledge', [])

        # 基于类别和类型的关联
        category_map = defaultdict(list)
        type_map = defaultdict(list)

        for kw in all_knowledge:
            if kw.get('category'):
                category_map[kw['category']].append(kw)
            if kw.get('type'):
                type_map[kw['type']].append(kw)

        # 跨类别关联
        categories = list(category_map.keys())
        for i, cat1 in enumerate(categories):
            for cat2 in categories[i+1:]:
                kws1 = category_map[cat1]
                kws2 = category_map[cat2]

                # 找到有相似时间或使用模式的知识
                for kw1 in kws1:
                    for kw2 in kws2:
                        # 计算关联强度
                        strength = 0.0

                        # 时间关联（创建时间接近）
                        round_diff = abs(kw1.get('creation_round', 0) - kw2.get('creation_round', 0))
                        if round_diff <= 5:
                            strength += 0.4

                        # 使用模式关联
                        use_diff = abs(kw1.get('use_count', 0) - kw2.get('use_count', 0))
                        if use_diff <= 2:
                            strength += 0.3

                        # 价值关联（价值相近）
                        value_diff = abs(kw1.get('value_score', 0) - kw2.get('value_score', 0))
                        if value_diff <= 0.2:
                            strength += 0.3

                        if strength >= self.config.get('association_threshold', 0.3):
                            associations.append({
                                'knowledge_1': kw1['id'],
                                'knowledge_2': kw2['id'],
                                'category_1': cat1,
                                'category_2': cat2,
                                'strength': strength,
                                'association_type': 'cross_category'
                            })

        return {
            'total_associations': len(associations),
            'associations': associations[:50],  # 返回前50个最强关联
            'categories': categories
        }

    def predict_evolution_trends(self, knowledge_data: Dict) -> Dict:
        """预测进化趋势"""
        predictions = []
        current_round = self.get_current_round()
        window = self.config.get('trend_prediction_window', 20)

        try:
            # 读取历史进化数据
            history_db = os.path.join(self.state_dir, "evolution_history.db")
            if os.path.exists(history_db):
                conn = sqlite3.connect(history_db)
                cursor = conn.cursor()

                # 获取最近N轮的进化数据
                cursor.execute("""
                    SELECT round_number, goal, status, effectiveness_score
                    FROM evolution_rounds
                    WHERE round_number > ?
                    ORDER BY round_number ASC
                """, (current_round - window,))

                history_rows = cursor.fetchall()
                conn.close()

                if len(history_rows) >= 5:
                    # 分析进化效率趋势
                    scores = [r[3] for r in history_rows if r[3]]
                    if scores:
                        avg_score = sum(scores) / len(scores)
                        recent_avg = sum(scores[-5:]) / min(5, len(scores))

                        # 趋势判断
                        if recent_avg > avg_score * 1.1:
                            trend = "improving"
                            confidence = min(0.9, (recent_avg - avg_score) / avg_score + 0.5)
                        elif recent_avg < avg_score * 0.9:
                            trend = "declining"
                            confidence = min(0.9, (avg_score - recent_avg) / avg_score + 0.5)
                        else:
                            trend = "stable"
                            confidence = 0.6

                        predictions.append({
                            'type': 'efficiency_trend',
                            'trend': trend,
                            'confidence': confidence,
                            'current_round': current_round,
                            'window': window,
                            'avg_score': avg_score,
                            'recent_avg': recent_avg
                        })

                    # 分析进化方向趋势
                    goals = [r[1] for r in history_rows if r[1]]
                    goal_categories = defaultdict(int)
                    for goal in goals:
                        if goal:
                            # 简单分类
                            if 'knowledge' in goal.lower() or 'learning' in goal.lower():
                                goal_categories['knowledge'] += 1
                            elif 'decision' in goal.lower() or 'quality' in goal.lower():
                                goal_categories['decision'] += 1
                            elif 'self' in goal.lower() or 'evolution' in goal.lower():
                                goal_categories['self_evolution'] += 1
                            else:
                                goal_categories['other'] += 1

                    if goal_categories:
                        dominant_category = max(goal_categories, key=goal_categories.get)
                        predictions.append({
                            'type': 'direction_trend',
                            'dominant_category': dominant_category,
                            'category_distribution': dict(goal_categories),
                            'confidence': 0.7
                        })

            # 基于知识图谱的预测
            graph_nodes = knowledge_data.get('graph_nodes', [])
            if graph_nodes:
                # 预测下一轮可能的优化方向
                node_types = [n.get('type') for n in graph_nodes if n.get('type')]
                type_counts = defaultdict(int)
                for t in node_types:
                    type_counts[t] += 1

                if type_counts:
                    predictions.append({
                        'type': 'knowledge_distribution',
                        'type_distribution': dict(type_counts),
                        'insight': f"当前知识主要分布在 {max(type_counts, key=type_counts.get)} 领域",
                        'confidence': 0.65
                    })

        except Exception as e:
            _safe_print(f"预测进化趋势失败: {e}")

        return {
            'predictions': predictions,
            'prediction_count': len(predictions),
            'current_round': current_round
        }

    def discover_innovation_opportunities(self, knowledge_data: Dict,
                                           associations: Dict) -> Dict:
        """发现创新机会"""
        innovations = []
        all_knowledge = knowledge_data.get('all_knowledge', [])
        high_value = knowledge_data.get('high_value_knowledge', [])
        recent = knowledge_data.get('recent_knowledge', [])

        try:
            # 1. 知识组合创新
            combo_count = self.config.get('knowledge_combination_count', 3)
            for i in range(len(high_value)):
                for j in range(i+1, min(i+combo_count, len(high_value))):
                    kw1 = high_value[i]
                    kw2 = high_value[j]

                    # 计算创新分数
                    innovation_score = 0.0

                    # 基于价值组合
                    innovation_score += (kw1.get('value_score', 0) + kw2.get('value_score', 0)) / 2 * 0.3

                    # 基于使用频率
                    innovation_score += min(kw1.get('use_count', 0), kw2.get('use_count', 0)) / 10 * 0.2

                    # 基于关联强度
                    for assoc in associations.get('associations', []):
                        if (assoc['knowledge_1'] == kw1['id'] and
                            assoc['knowledge_2'] == kw2['id']) or \
                           (assoc['knowledge_1'] == kw2['id'] and
                            assoc['knowledge_2'] == kw1['id']):
                            innovation_score += assoc['strength'] * 0.5
                            break

                    if innovation_score >= self.config.get('innovation_min_score', 0.6):
                        innovations.append({
                            'type': 'knowledge_combination',
                            'description': f"将 {kw1['id']} 与 {kw2['id']} 组合可能产生新价值",
                            'related_knowledge': [kw1['id'], kw2['id']],
                            'innovation_score': innovation_score,
                            'category_1': kw1.get('category', 'unknown'),
                            'category_2': kw2.get('category', 'unknown')
                        })

            # 2. 跨领域优化机会
            for kw in recent:
                # 寻找与该知识相关但未被充分利用的领域
                for assoc in associations.get('associations', []):
                    if assoc.get('knowledge_1') == kw['id'] or assoc.get('knowledge_2') == kw['id']:
                        # 检查是否已有足够的应用
                        if assoc['strength'] < 0.5:  # 关联较弱，说明可能有优化空间
                            innovations.append({
                                'type': 'cross_domain_optimization',
                                'description': f"加强 {assoc['category_1']} 与 {assoc['category_2']} 的关联可能带来优化",
                                'related_knowledge': [assoc['knowledge_1'], assoc['knowledge_2']],
                                'innovation_score': assoc['strength'] + 0.2,
                                'categories': [assoc['category_1'], assoc['category_2']]
                            })

            # 3. 基于趋势预测的创新
            trends = self.predict_evolution_trends(knowledge_data)
            for pred in trends.get('predictions', []):
                if pred.get('type') == 'direction_trend':
                    innovations.append({
                        'type': 'trend_based',
                        'description': f"基于{dominant_category}趋势，可能存在创新机会",
                        'innovation_score': 0.7,
                        'based_on': pred
                    })

            # 按创新分数排序，返回前N个
            innovations.sort(key=lambda x: x.get('innovation_score', 0), reverse=True)
            max_suggestions = self.config.get('max_innovation_suggestions', 10)
            innovations = innovations[:max_suggestions]

        except Exception as e:
            _safe_print(f"发现创新机会失败: {e}")

        return {
            'innovations': innovations,
            'total_discovered': len(innovations),
            'innovation_types': list(set(i.get('type') for i in innovations))
        }

    def get_value_implementation_paths(self, innovations: List[Dict],
                                       knowledge_data: Dict) -> Dict:
        """获取价值实现路径推荐"""
        paths = []

        for innovation in innovations:
            path = {
                'innovation': innovation.get('description', ''),
                'innovation_type': innovation.get('type', ''),
                'score': innovation.get('innovation_score', 0),
                'implementation_steps': []
            }

            # 生成实现步骤
            if innovation.get('type') == 'knowledge_combination':
                related = innovation.get('related_knowledge', [])
                path['implementation_steps'] = [
                    f"1. 分析 {related[0] if len(related) > 0 else '知识A'} 的现有能力",
                    f"2. 分析 {related[1] if len(related) > 1 else '知识B'} 的现有能力",
                    "3. 识别两个知识的互补点",
                    "4. 设计集成方案",
                    "5. 实现并测试"
                ]
            elif innovation.get('type') == 'cross_domain_optimization':
                path['implementation_steps'] = [
                    "1. 分析两个领域的现有实现",
                    "2. 识别交叉优化的可能性",
                    "3. 设计跨领域协作机制",
                    "4. 实现并验证效果"
                ]
            else:
                path['implementation_steps'] = [
                    "1. 深入分析创新点",
                    "2. 评估技术可行性",
                    "3. 设计实现方案",
                    "4. 逐步实施"
                ]

            paths.append(path)

        return {
            'implementation_paths': paths,
            'total_paths': len(paths)
        }

    def run_full_reasoning_cycle(self, force: bool = False) -> Dict:
        """运行完整的主动推理与创新发现周期"""
        _safe_print("=" * 60)
        _safe_print("进化知识主动推理与创新发现引擎")
        _safe_print("=" * 60)

        current_round = self.get_current_round()

        # 检查是否需要运行
        last_run = self._get_last_run_info()
        if not force and last_run:
            rounds_since_last = current_round - last_run.get('round', 0)
            if rounds_since_last < self.config.get('reasoning_interval', 10):
                _safe_print(f"距离上次推理仅 {rounds_since_last} 轮，小于间隔 {self.config.get('reasoning_interval', 10)}，跳过")
                return {
                    'status': 'skipped',
                    'reason': 'interval_not_reached',
                    'rounds_since_last': rounds_since_last
                }

        # 1. 加载知识数据
        _safe_print("\n[1/5] 加载知识数据...")
        knowledge_data = self.load_knowledge_data()
        _safe_print(f"    知识总数: {len(knowledge_data.get('all_knowledge', []))}")
        _safe_print(f"    高价值知识: {len(knowledge_data.get('high_value_knowledge', []))}")
        _safe_print(f"    最近知识: {len(knowledge_data.get('recent_knowledge', []))}")

        # 2. 分析知识关联
        _safe_print("\n[2/5] 分析知识关联...")
        associations = self.analyze_knowledge_associations(knowledge_data)
        _safe_print(f"    发现关联数: {associations.get('total_associations', 0)}")

        # 3. 预测进化趋势
        _safe_print("\n[3/5] 预测进化趋势...")
        trends = self.predict_evolution_trends(knowledge_data)
        _safe_print(f"    预测数: {trends.get('prediction_count', 0)}")
        for pred in trends.get('predictions', [])[:2]:
            _safe_print(f"    - {pred.get('type')}: {pred.get('trend', pred.get('insight', 'N/A'))}")

        # 4. 发现创新机会
        _safe_print("\n[4/5] 发现创新机会...")
        innovations = self.discover_innovation_opportunities(knowledge_data, associations)
        _safe_print(f"    发现创新机会: {innovations.get('total_discovered', 0)}")
        for inn in innovations.get('innovations', [])[:3]:
            _safe_print(f"    - [{inn.get('type')}] {inn.get('description', '')[:50]}... (分数: {inn.get('innovation_score', 0):.2f})")

        # 5. 生成价值实现路径
        _safe_print("\n[5/5] 生成价值实现路径...")
        paths = self.get_value_implementation_paths(
            innovations.get('innovations', []),
            knowledge_data
        )
        _safe_print(f"    生成路径数: {paths.get('total_paths', 0)}")

        # 保存结果
        result = {
            'status': 'completed',
            'current_round': current_round,
            'knowledge_data': {
                'total_knowledge': len(knowledge_data.get('all_knowledge', [])),
                'high_value_count': len(knowledge_data.get('high_value_knowledge', [])),
                'recent_count': len(knowledge_data.get('recent_knowledge', []))
            },
            'associations': associations,
            'trends': trends,
            'innovations': innovations,
            'implementation_paths': paths
        }

        self._save_reasoning_result(result)
        self._update_last_run_info(current_round)

        _safe_print("\n推理与创新发现周期完成!")
        _safe_print("=" * 60)

        return result

    def _get_last_run_info(self) -> Optional[Dict]:
        """获取上次运行信息"""
        try:
            if os.path.exists(self.reasoning_state_path):
                with open(self.reasoning_state_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return None

    def _update_last_run_info(self, round_num: int):
        """更新上次运行信息"""
        try:
            os.makedirs(os.path.dirname(self.reasoning_state_path), exist_ok=True)
            with open(self.reasoning_state_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'round': round_num,
                    'timestamp': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"保存运行信息失败: {e}")

    def _save_reasoning_result(self, result: Dict):
        """保存推理结果"""
        try:
            result_path = os.path.join(self.state_dir, "knowledge_active_reasoning_result.json")
            os.makedirs(os.path.dirname(result_path), exist_ok=True)
            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"保存推理结果失败: {e}")

    def get_status(self) -> Dict:
        """获取引擎状态"""
        current_round = self.get_current_round()
        last_run = self._get_last_run_info()

        return {
            'status': 'active',
            'version': self.version,
            'current_round': current_round,
            'last_run_round': last_run.get('round') if last_run else None,
            'config': self.config
        }

    def update_config(self, key: str, value: Any) -> Dict:
        """更新配置"""
        self.config[key] = value
        self._save_config(self.config)
        return {'status': 'updated', 'key': key, 'value': value}


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description='智能进化知识主动推理与创新发现引擎')
    parser.add_argument('command', nargs='?', default='status',
                        help='命令: status, run, analyze, predict, innovate, paths, config')
    parser.add_argument('--force', action='store_true', help='强制执行')
    parser.add_argument('--set', nargs=2, metavar=('KEY', 'VALUE'), help='设置配置项')

    args = parser.parse_args()

    engine = KnowledgeActiveReasoningEngine()

    if args.command == 'run' or args.command == '推理':
        # 运行完整周期
        result = engine.run_full_reasoning_cycle(force=args.force)
        print("\n推理结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'analyze' or args.command == '分析':
        # 分析知识关联
        knowledge_data = engine.load_knowledge_data()
        associations = engine.analyze_knowledge_associations(knowledge_data)
        print("\n知识关联分析:")
        print(json.dumps(associations, ensure_ascii=False, indent=2))

    elif args.command == 'predict' or args.command == '预测':
        # 预测进化趋势
        knowledge_data = engine.load_knowledge_data()
        trends = engine.predict_evolution_trends(knowledge_data)
        print("\n进化趋势预测:")
        print(json.dumps(trends, ensure_ascii=False, indent=2))

    elif args.command == 'innovate' or args.command == '创新':
        # 发现创新机会
        knowledge_data = engine.load_knowledge_data()
        associations = engine.analyze_knowledge_associations(knowledge_data)
        innovations = engine.discover_innovation_opportunities(knowledge_data, associations)
        print("\n创新机会发现:")
        print(json.dumps(innovations, ensure_ascii=False, indent=2))

    elif args.command == 'paths' or args.command == '路径':
        # 生成价值实现路径
        knowledge_data = engine.load_knowledge_data()
        associations = engine.analyze_knowledge_associations(knowledge_data)
        innovations = engine.discover_innovation_opportunities(knowledge_data, associations)
        paths = engine.get_value_implementation_paths(
            innovations.get('innovations', []),
            knowledge_data
        )
        print("\n价值实现路径:")
        print(json.dumps(paths, ensure_ascii=False, indent=2))

    elif args.command == 'config':
        # 显示/修改配置
        if args.set:
            key, value = args.set
            if value.lower() in ['true', 'yes', '1']:
                value = True
            elif value.lower() in ['false', 'no', '0']:
                value = False
            elif value.isdigit():
                value = int(value)

            result = engine.update_config(key, value)
            print("\n配置更新结果:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            status = engine.get_status()
            print("\n当前配置:")
            print(json.dumps(status.get('config', {}), ensure_ascii=False, indent=2))

    else:
        # 默认显示状态
        status = engine.get_status()
        print("\n引擎状态:")
        print(json.dumps(status, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()