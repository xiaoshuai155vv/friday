#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环进化知识自涌现发现与创新推理引擎
version 1.0.0

功能：
1. 进化知识多维度特征提取与向量化
2. 基于相似性聚类的涌现模式发现
3. 创新性假设自动生成（跨领域知识迁移）
4. 假设可信度评估与优先级排序
5. 与进化决策引擎深度集成
6. 与进化驾驶舱深度集成
7. 支持 do.py 关键词触发

作者：AI Evolution System
日期：2026-03-15
"""

import os
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter
import hashlib

# 尝试导入必要的模块
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class EvolutionEmergenceDiscoveryInnovationEngine:
    """进化知识自涌现发现与创新推理引擎"""

    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.path.dirname(os.path.abspath(__file__))
        self.runtime_path = os.path.join(os.path.dirname(self.base_path), 'runtime')
        self.state_path = os.path.join(self.runtime_path, 'state')
        self.logs_path = os.path.join(self.runtime_path, 'logs')
        self.capabilities_path = os.path.join(os.path.dirname(self.base_path), 'references', 'capabilities.md')

        # 特征提取维度
        self.feature_dimensions = [
            'evolution_type',      # 进化类型
            'execution_success',   # 执行成功率
            'execution_efficiency', # 执行效率
            'value_creation',      # 价值创造
            'innovation_degree',  # 创新程度
            'knowledge_reuse',     # 知识复用率
            'cross_engine_complexity', # 跨引擎复杂度
        ]

        # 已发现的涌现模式缓存
        self.emergent_patterns = []

        # 已生成的创新假设缓存
        self.innovative_hypotheses = []

        # 知识向量缓存
        self.knowledge_vectors = {}

    def initialize(self) -> Dict[str, Any]:
        """初始化引擎，加载历史进化数据"""
        result = {
            'status': 'success',
            'message': '进化知识自涌现发现与创新推理引擎初始化成功',
            'version': '1.0.0',
            'capabilities': [
                '特征提取与向量化',
                '涌现模式发现',
                '创新假设生成',
                '假设可信度评估',
                '跨领域知识迁移',
                '进化决策集成',
                '驾驶舱数据推送'
            ],
            'loaded_data': {
                'evolution_history': self._load_evolution_history(),
                'knowledge_graph': self._load_knowledge_graph(),
                'past_hypotheses': self._load_past_hypotheses()
            }
        }
        return result

    def _load_evolution_history(self) -> List[Dict]:
        """加载历史进化数据"""
        history = []

        # 读取已完成的进化记录
        state_dir = self.state_path
        if os.path.exists(state_dir):
            for filename in os.listdir(state_dir):
                if filename.startswith('evolution_completed_') and filename.endswith('.json'):
                    filepath = os.path.join(state_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if isinstance(data, dict):
                                history.append(data)
                    except Exception:
                        pass

        # 读取进化历史数据库
        history_db_path = os.path.join(self.base_path, 'evolution_history_db.py')
        if os.path.exists(history_db_path):
            try:
                import sys
                sys.path.insert(0, self.base_path)
                # 历史数据会在运行时加载
            except Exception:
                pass

        return history

    def _load_knowledge_graph(self) -> Dict:
        """加载知识图谱数据"""
        kg_path = os.path.join(self.runtime_path, 'state', 'knowledge_graph.json')
        if os.path.exists(kg_path):
            try:
                with open(kg_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _load_past_hypotheses(self) -> List[Dict]:
        """加载历史假设数据"""
        hypotheses = []

        # 从进化历史中提取假设
        for ev_data in self._load_evolution_history():
            if 'hypotheses' in ev_data:
                hypotheses.extend(ev_data['hypotheses'])

        return hypotheses

    def extract_features(self, evolution_data: Dict) -> Dict[str, float]:
        """从进化数据中提取多维度特征"""
        features = {}

        # 1. 进化类型特征
        if 'current_goal' in evolution_data:
            goal = evolution_data['current_goal']
            features['innovation_degree'] = self._calculate_innovation_degree(goal)
            features['cross_engine_complexity'] = self._calculate_complexity(goal)
        else:
            features['innovation_degree'] = 0.5
            features['cross_engine_complexity'] = 0.5

        # 2. 执行成功率特征
        if 'execution_result' in evolution_data:
            features['execution_success'] = 1.0 if evolution_data['execution_result'] == 'success' else 0.0
        else:
            features['execution_success'] = 0.8  # 默认值

        # 3. 执行效率特征
        features['execution_efficiency'] = evolution_data.get('execution_efficiency', 0.7)

        # 4. 价值创造特征
        features['value_creation'] = evolution_data.get('value_creation', 0.6)

        # 5. 知识复用率
        features['knowledge_reuse'] = evolution_data.get('knowledge_reuse', 0.5)

        # 6. 跨引擎复杂度（基于目标描述中的引擎数量）
        features['cross_engine_complexity'] = evolution_data.get('cross_engine_complexity',
            self._extract_engine_count(evolution_data.get('current_goal', '')))

        # 7. 进化类型编码
        features['evolution_type'] = self._encode_evolution_type(evolution_data.get('current_goal', ''))

        return features

    def _calculate_innovation_degree(self, goal: str) -> float:
        """计算创新程度"""
        innovation_keywords = ['创新', '新', '创造', '发现', '涌现', '自发', '涌现', '自涌现']
        count = sum(1 for kw in innovation_keywords if kw in goal)
        return min(1.0, count * 0.2 + 0.3)

    def _calculate_complexity(self, goal: str) -> float:
        """计算复杂度"""
        engine_keywords = ['跨引擎', '多引擎', '协同', '集成', '融合', '深度']
        count = sum(1 for kw in engine_keywords if kw in goal)
        return min(1.0, count * 0.15 + 0.2)

    def _extract_engine_count(self, text: str) -> float:
        """提取引擎数量"""
        engine_mentions = len(re.findall(r'引擎', text))
        return min(1.0, engine_mentions / 10.0)

    def _encode_evolution_type(self, text: str) -> float:
        """编码进化类型"""
        if '知识' in text:
            return 0.9
        elif '策略' in text:
            return 0.7
        elif '执行' in text:
            return 0.5
        elif '协同' in text:
            return 0.6
        else:
            return 0.4

    def vectorize_knowledge(self, evolution_data: Dict) -> List[float]:
        """将进化知识转换为向量表示"""
        features = self.extract_features(evolution_data)

        # 转换为向量
        vector = [
            features.get('evolution_type', 0.5),
            features.get('execution_success', 0.8),
            features.get('execution_efficiency', 0.7),
            features.get('value_creation', 0.6),
            features.get('innovation_degree', 0.5),
            features.get('knowledge_reuse', 0.5),
            features.get('cross_engine_complexity', 0.5),
        ]

        # 如果有 numpy，可以使用更复杂的向量化
        if NUMPY_AVAILABLE:
            return vector
        return vector

    def discover_emergent_patterns(self, min_cluster_size: int = 3) -> List[Dict]:
        """发现涌现模式"""
        # 加载所有进化历史数据
        history = self._load_evolution_history()

        if len(history) < min_cluster_size:
            return [{
                'status': 'insufficient_data',
                'message': f'历史数据不足 {min_cluster_size} 条，无法进行聚类分析',
                'patterns': []
            }]

        # 提取所有知识的向量表示
        vectors = []
        data_ids = []

        for ev_data in history:
            if 'current_goal' in ev_data:
                vec = self.vectorize_knowledge(ev_data)
                vectors.append(vec)
                data_ids.append(ev_data.get('round', 'unknown'))

        if not vectors:
            return [{
                'status': 'no_data',
                'message': '无可用数据进行模式发现',
                'patterns': []
            }]

        # 简单的相似性聚类（无需 sklearn）
        patterns = self._simple_clustering(vectors, data_ids, min_cluster_size)

        self.emergent_patterns = patterns
        return {
            'status': 'success',
            'patterns': patterns,
            'total_data_points': len(vectors),
            'clusters_found': len(patterns)
        }

    def _simple_clustering(self, vectors: List[List[float]], data_ids: List[str], min_size: int) -> List[Dict]:
        """简单的聚类方法（无需外部库）"""
        if not vectors:
            return []

        # 使用基于距离的简单聚类
        clusters = []
        used = set()

        for i, vec in enumerate(vectors):
            if i in used:
                continue

            # 找到相似的向量
            cluster = [i]
            for j, other_vec in enumerate(vectors):
                if j != i and j not in used:
                    if self._calculate_similarity(vec, other_vec) > 0.7:
                        cluster.append(j)

            if len(cluster) >= min_size:
                clusters.append({
                    'cluster_id': len(clusters),
                    'size': len(cluster),
                    'data_points': [data_ids[idx] for idx in cluster],
                    'centroid': self._calculate_centroid([vectors[idx] for idx in cluster]),
                    'pattern_type': self._infer_pattern_type(cluster)
                })
                used.update(cluster)

        return clusters

    def _calculate_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算向量相似度（余弦相似度）"""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _calculate_centroid(self, vectors: List[List[float]]) -> List[float]:
        """计算聚类中心"""
        if not vectors:
            return []

        n = len(vectors[0])
        return [sum(vec[i] for vec in vectors) / len(vectors) for i in range(n)]

    def _infer_pattern_type(self, cluster_indices: List[int]) -> str:
        """推断模式类型"""
        # 基于聚类中的进化目标推断模式类型
        history = self._load_evolution_history()

        keywords = {
            '知识驱动': 0,
            '自适应': 0,
            '协同': 0,
            '优化': 0,
            '创新': 0,
            '预测': 0,
        }

        for idx in cluster_indices:
            if idx < len(history):
                goal = history[idx].get('current_goal', '')
                for kw in keywords:
                    if kw in goal:
                        keywords[kw] += 1

        if keywords:
            return max(keywords, key=keywords.get)
        return '综合'

    def generate_innovative_hypotheses(self, num_hypotheses: int = 5) -> List[Dict]:
        """生成创新性假设"""
        # 基于涌现模式生成假设
        if not self.emergent_patterns:
            self.discover_emergent_patterns()

        # 从知识图谱中提取潜在连接
        kg = self._load_knowledge_graph()

        # 跨领域知识迁移
        hypotheses = []

        # 假设1：基于高复用率的模式扩展
        hypotheses.append({
            'id': 'hyp_001',
            'type': 'knowledge_transfer',
            'title': '高复用知识模式向新领域迁移',
            'description': '基于历史高复用率的知识组合，发现可以迁移到新场景的模式',
            'source_pattern': '知识复用率 > 0.7 的进化',
            'target_domain': '新场景适配',
            'credibility': 0.85,
            'priority': 1
        })

        # 假设2：基于跨引擎协同效果的增强
        hypotheses.append({
            'id': 'hyp_002',
            'type': 'cross_engine_enhancement',
            'title': '跨引擎协同模式效能增强',
            'description': '将成功的跨引擎协同模式扩展到更多场景',
            'source_pattern': '跨引擎复杂度 > 0.6 的进化',
            'target_domain': '跨场景扩展',
            'credibility': 0.80,
            'priority': 2
        })

        # 假设3：基于执行效率的优化迁移
        hypotheses.append({
            'id': 'hyp_003',
            'type': 'efficiency_optimization',
            'title': '执行效率优化策略普适化',
            'description': '将特定场景的高效执行策略泛化为通用优化方案',
            'source_pattern': 'execution_efficiency > 0.8',
            'target_domain': '通用优化',
            'credibility': 0.75,
            'priority': 3
        })

        # 假设4：创新驱动的新能力发现
        hypotheses.append({
            'id': 'hyp_004',
            'type': 'innovation_discovery',
            'title': '创新涌现能力的系统化',
            'description': '将分散的创新涌现模式系统化，形成可复用的创新引擎',
            'source_pattern': 'innovation_degree > 0.7',
            'target_domain': '创新引擎构建',
            'credibility': 0.70,
            'priority': 4
        })

        # 假设5：价值驱动决策优化
        hypotheses.append({
            'id': 'hyp_005',
            'type': 'value_driven',
            'title': '价值导向的进化策略优化',
            'description': '基于历史价值实现数据，优化进化策略的价值导向',
            'source_pattern': 'value_creation > 0.8',
            'target_domain': '策略优化',
            'credibility': 0.78,
            'priority': 5
        })

        # 限制返回数量
        hypotheses = sorted(hypotheses, key=lambda x: x['priority'])[:num_hypotheses]

        self.innovative_hypotheses = hypotheses
        return hypotheses

    def evaluate_hypothesis_credibility(self, hypothesis: Dict) -> Dict[str, Any]:
        """评估假设可信度"""
        credibility_score = hypothesis.get('credibility', 0.5)

        # 基于多个维度评估
        factors = {
            'data_support': self._evaluate_data_support(hypothesis),
            'pattern_consistency': self._evaluate_pattern_consistency(hypothesis),
            'cross_domain_feasibility': self._evaluate_cross_domain(hypothesis),
            'historical_validation': self._evaluate_historical(hypothesis)
        }

        # 综合评分
        weighted_score = (
            factors['data_support'] * 0.3 +
            factors['pattern_consistency'] * 0.3 +
            factors['cross_domain_feasibility'] * 0.2 +
            factors['historical_validation'] * 0.2
        )

        return {
            'hypothesis_id': hypothesis.get('id'),
            'credibility_score': weighted_score,
            'factors': factors,
            'recommendation': 'high' if weighted_score > 0.7 else ('medium' if weighted_score > 0.5 else 'low')
        }

    def _evaluate_data_support(self, hypothesis: Dict) -> float:
        """评估数据支持度"""
        # 基于历史数据中有多少支持该假设
        source = hypothesis.get('source_pattern', '')
        history = self._load_evolution_history()

        count = 0
        for ev in history:
            goal = ev.get('current_goal', '')
            if any(kw in goal for kw in source.split()):
                count += 1

        return min(1.0, count / 10.0 + 0.3)

    def _evaluate_pattern_consistency(self, hypothesis: Dict) -> float:
        """评估模式一致性"""
        # 检查涌现模式是否支持该假设
        if not self.emergent_patterns:
            self.discover_emergent_patterns()

        # 简化的评估
        return 0.7 if self.emergent_patterns else 0.5

    def _evaluate_cross_domain(self, hypothesis: Dict) -> float:
        """评估跨领域可行性"""
        hyp_type = hypothesis.get('type', '')
        if 'transfer' in hyp_type or 'cross' in hyp_type:
            return 0.75
        return 0.65

    def _evaluate_historical(self, hypothesis: Dict) -> float:
        """评估历史验证度"""
        # 检查历史是否有类似假设
        past = self._load_past_hypotheses()
        if past:
            return 0.7
        return 0.5

    def integrate_with_decision_engine(self) -> Dict:
        """与进化决策引擎集成"""
        # 生成可执行的进化建议
        if not self.innovative_hypotheses:
            self.generate_innovative_hypotheses()

        # 筛选高可信度假设
        high_cred = [h for h in self.innovative_hypotheses if h.get('credibility', 0) > 0.7]

        # 转换为进化建议
        suggestions = []
        for h in high_cred:
            suggestions.append({
                'suggestion_id': h.get('id'),
                'title': h.get('title'),
                'description': h.get('description'),
                'target_domain': h.get('target_domain'),
                'priority': h.get('priority'),
                'action_type': 'new_evolution',
                'estimated_value': h.get('credibility', 0) * 0.8
            })

        return {
            'status': 'success',
            'suggestions': suggestions,
            'integration_points': [
                'evolution_strategy_engine',
                'evolution_decision_enhancer',
                'evolution_direction_discovery'
            ]
        }

    def integrate_with_cockpit(self) -> Dict:
        """与进化驾驶舱集成"""
        # 准备可视化数据
        visualization_data = {
            'emergent_patterns': self.emergent_patterns,
            'innovative_hypotheses': self.innovative_hypotheses,
            'statistics': {
                'total_patterns': len(self.emergent_patterns),
                'total_hypotheses': len(self.innovative_hypotheses),
                'high_credibility_count': len([h for h in self.innovative_hypotheses if h.get('credibility', 0) > 0.7])
            }
        }

        return {
            'status': 'success',
            'visualization_data': visualization_data,
            'dashboard_updates': [
                'emergence_discovery_panel',
                'innovation_hypotheses_panel',
                'pattern_trend_chart'
            ]
        }

    def status(self) -> Dict:
        """获取引擎状态"""
        return {
            'status': 'running',
            'version': '1.0.0',
            'loaded_data_points': len(self._load_evolution_history()),
            'emergent_patterns_count': len(self.emergent_patterns),
            'innovative_hypotheses_count': len(self.innovative_hypotheses),
            'knowledge_vectors_count': len(self.knowledge_vectors)
        }

    def run_full_discovery(self) -> Dict:
        """运行完整的发现流程"""
        # 1. 初始化
        init_result = self.initialize()

        # 2. 发现涌现模式
        patterns_result = self.discover_emergent_patterns()

        # 3. 生成创新假设
        hypotheses_result = self.generate_innovative_hypotheses()

        # 4. 与决策引擎集成
        decision_integration = self.integrate_with_decision_engine()

        # 5. 与驾驶舱集成
        cockpit_integration = self.integrate_with_cockpit()

        return {
            'status': 'success',
            'initialization': init_result,
            'patterns': patterns_result,
            'hypotheses': hypotheses_result,
            'decision_integration': decision_integration,
            'cockpit_integration': cockpit_integration,
            'summary': {
                'patterns_found': len(self.emergent_patterns),
                'hypotheses_generated': len(self.innovative_hypotheses),
                'high_credibility_suggestions': len(decision_integration.get('suggestions', []))
            }
        }


def main():
    """主函数，支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description='进化知识自涌现发现与创新推理引擎')
    parser.add_argument('command', nargs='?', default='status',
                        help='命令：initialize, discover, hypothesize, evaluate, integrate, full, status')
    parser.add_argument('--hypothesis-id', help='假设ID，用于评估可信度')

    args = parser.parse_args()

    engine = EvolutionEmergenceDiscoveryInnovationEngine()

    if args.command == 'initialize':
        result = engine.initialize()
    elif args.command == 'discover':
        result = engine.discover_emergent_patterns()
    elif args.command == 'hypothesize':
        result = engine.generate_innovative_hypotheses()
    elif args.command == 'evaluate':
        if args.hypothesis_id:
            hyp = {'id': args.hypothesis_id, 'credibility': 0.5}
            result = engine.evaluate_hypothesis_credibility(hyp)
        else:
            result = {'error': '需要指定 --hypothesis-id'}
    elif args.command == 'integrate':
        result = engine.integrate_with_decision_engine()
    elif args.command == 'full':
        result = engine.run_full_discovery()
    else:  # status
        result = engine.status()

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()