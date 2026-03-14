#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环跨引擎统一知识索引与智能检索引擎
在 round 445 完成的优化建议自动执行闭环引擎基础上，进一步构建跨引擎统一知识索引与智能检索能力。
让系统能够自动聚合所有进化引擎产生的知识资产（优化建议、执行记录、方法论、洞察等）、
建立统一的跨引擎知识索引、实现基于语义和关键词的智能检索、生成知识关联图谱。
让进化环的「知识」真正变成可发现、可复用的智能资产。

功能：
1. 跨引擎知识自动聚合（从各进化引擎收集知识资产）
2. 统一知识索引构建（结构化存储与快速检索）
3. 语义和关键词智能检索功能
4. 知识关联图谱生成与可视化
5. 与进化驾驶舱深度集成（知识可视化与检索入口）
6. 集成到 do.py 支持知识索引、知识检索、跨引擎知识、查询知识等关键词触发

Version: 1.0.0
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict
import threading

# 添加 scripts 目录到路径
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

# 项目目录
PROJECT_DIR = os.path.dirname(SCRIPTS_DIR)
RUNTIME_DIR = os.path.join(PROJECT_DIR, "runtime")
STATE_DIR = os.path.join(RUNTIME_DIR, "state")
LOGS_DIR = os.path.join(RUNTIME_DIR, "logs")

# 数据文件路径
KNOWLEDGE_INDEX_FILE = os.path.join(STATE_DIR, "cross_engine_knowledge_index.json")
KNOWLEDGE_GRAPH_FILE = os.path.join(STATE_DIR, "knowledge_graph.json")
COCKPIT_INTEGRATION_FILE = os.path.join(STATE_DIR, "knowledge_index_cockpit_data.json")


def _safe_print(text: str):
    """安全打印"""
    try:
        print(text)
    except UnicodeEncodeError:
        clean_text = re.sub(r'[^\x00-\x7F]+', '', text)
        print(clean_text)


class CrossEngineKnowledgeIndex:
    """跨引擎统一知识索引与智能检索引擎"""

    def __init__(self):
        self.index_file = KNOWLEDGE_INDEX_FILE
        self.graph_file = KNOWLEDGE_GRAPH_FILE
        self.cockpit_file = COCKPIT_INTEGRATION_FILE
        self.knowledge_index = self._load_index()
        self.knowledge_graph = self._load_graph()

    def _load_index(self) -> Dict:
        """加载知识索引"""
        default_index = {
            'knowledge_items': {},  # {item_id: knowledge_item}
            'keyword_index': defaultdict(set),  # {keyword: set of item_ids}
            'category_index': defaultdict(set),  # {category: set of item_ids}
            'round_index': defaultdict(set),  # {round_number: set of item_ids}
            'tag_index': defaultdict(set),  # {tag: set of item_ids}
            'last_updated': None,
            'total_items': 0
        }
        try:
            if os.path.exists(self.index_file):
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 将列表转换回 set
                    if 'keyword_index' in data:
                        default_index['keyword_index'] = defaultdict(set, {k: set(v) for k, v in data.get('keyword_index', {}).items()})
                    if 'category_index' in data:
                        default_index['category_index'] = defaultdict(set, {k: set(v) for k, v in data.get('category_index', {}).items()})
                    if 'round_index' in data:
                        default_index['round_index'] = defaultdict(set, {k: set(v) for k, v in data.get('round_index', {}).items()})
                    if 'tag_index' in data:
                        default_index['tag_index'] = defaultdict(set, {k: set(v) for k, v in data.get('tag_index', {}).items()})
                    default_index['knowledge_items'] = data.get('knowledge_items', {})
                    default_index['last_updated'] = data.get('last_updated')
                    default_index['total_items'] = data.get('total_items', 0)
        except Exception as e:
            _safe_print(f"加载知识索引失败: {e}")
        return default_index

    def _save_index(self):
        """保存知识索引"""
        try:
            os.makedirs(os.path.dirname(self.index_file), exist_ok=True)
            self.knowledge_index['last_updated'] = datetime.now().isoformat()

            # 转换 defaultdict(set) 为可 JSON 序列化的格式
            serializable_index = {
                'knowledge_items': self.knowledge_index['knowledge_items'],
                'keyword_index': {k: list(v) for k, v in self.knowledge_index['keyword_index'].items()},
                'category_index': {k: list(v) for k, v in self.knowledge_index['category_index'].items()},
                'round_index': {k: list(v) for k, v in self.knowledge_index['round_index'].items()},
                'tag_index': {k: list(v) for k, v in self.knowledge_index['tag_index'].items()},
                'last_updated': self.knowledge_index['last_updated'],
                'total_items': self.knowledge_index['total_items']
            }

            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"保存知识索引失败: {e}")

    def _load_graph(self) -> Dict:
        """加载知识图谱"""
        default_graph = {
            'nodes': {},  # {node_id: node_data}
            'edges': [],  # [{from, to, relation}]
            'clusters': defaultdict(list),  # {cluster_id: [node_ids]}
            'last_updated': None
        }
        try:
            if os.path.exists(self.graph_file):
                with open(self.graph_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    default_graph.update(data)
        except Exception as e:
            _safe_print(f"加载知识图谱失败: {e}")
        return default_graph

    def _save_graph(self):
        """保存知识图谱"""
        try:
            os.makedirs(os.path.dirname(self.graph_file), exist_ok=True)
            self.knowledge_graph['last_updated'] = datetime.now().isoformat()
            with open(self.graph_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_graph, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"保存知识图谱失败: {e}")

    def collect_knowledge_from_completed_evolutions(self) -> int:
        """从已完成进化中收集知识资产"""
        collected_count = 0
        if not os.path.exists(STATE_DIR):
            return 0

        for f in os.listdir(STATE_DIR):
            if f.startswith("evolution_completed_") and f.endswith(".json"):
                file_path = os.path.join(STATE_DIR, f)
                try:
                    with open(file_path, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        item_id = self._add_knowledge_item(data)
                        if item_id:
                            collected_count += 1
                except Exception as e:
                    _safe_print(f"处理 {f} 失败: {e}")

        # 收集优化建议
        optimization_files = [
            os.path.join(STATE_DIR, "optimization_auto_execution_state.json"),
            os.path.join(STATE_DIR, "methodology_auto_optimization_state.json"),
            os.path.join(STATE_DIR, "execution_feedback_data.json"),
            os.path.join(STATE_DIR, "trend_analysis_data.json")
        ]
        for opt_file in optimization_files:
            if os.path.exists(opt_file):
                try:
                    with open(opt_file, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        self._add_knowledge_item({
                            'type': 'state_file',
                            'source': os.path.basename(opt_file),
                            'data': data,
                            'loop_round': data.get('loop_round', 0)
                        })
                        collected_count += 1
                except Exception as e:
                    _safe_print(f"处理 {opt_file} 失败: {e}")

        # 保存索引
        if collected_count > 0:
            self._save_index()

        return collected_count

    def _add_knowledge_item(self, data: Dict) -> Optional[str]:
        """添加知识条目"""
        try:
            loop_round = data.get('loop_round', 0)
            if loop_round == 0:
                loop_round = data.get('round', 0)

            # 生成唯一ID
            item_id = f"knowledge_{loop_round}_{len(self.knowledge_index['knowledge_items'])}"

            # 提取关键词
            content = json.dumps(data, ensure_ascii=False)
            keywords = self._extract_keywords(content)

            # 提取分类
            categories = self._extract_categories(data)

            # 提取标签
            tags = self._extract_tags(data)

            # 创建知识条目
            item = {
                'id': item_id,
                'round': loop_round,
                'type': data.get('type', 'evolution_completed'),
                'title': data.get('mission', data.get('current_goal', 'Unknown')),
                'content': content,
                'keywords': keywords,
                'categories': categories,
                'tags': tags,
                'created_at': data.get('completed_at', datetime.now().isoformat()),
                'source': data.get('mission', '')
            }

            # 添加到索引
            self.knowledge_index['knowledge_items'][item_id] = item

            # 关键词索引
            for kw in keywords:
                self.knowledge_index['keyword_index'][kw.lower()].add(item_id)

            # 分类索引
            for cat in categories:
                self.knowledge_index['category_index'][cat].add(item_id)

            # 轮次索引
            if loop_round > 0:
                self.knowledge_index['round_index'][loop_round].add(item_id)

            # 标签索引
            for tag in tags:
                self.knowledge_index['tag_index'][tag].add(item_id)

            self.knowledge_index['total_items'] = len(self.knowledge_index['knowledge_items'])

            return item_id
        except Exception as e:
            _safe_print(f"添加知识条目失败: {e}")
            return None

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 移除JSON结构，保留文本
        text = re.sub(r'[{}"\[\]]', ' ', text)
        words = re.findall(r'[\u4e00-\u9fa5a-zA-Z0-9]{2,}', text)

        # 过滤常见词和短词
        stop_words = {'的', '是', '在', '和', '与', '或', '为', '了', '在', 'the', 'a', 'an', 'is', 'are', 'and', 'or', 'to', 'of', 'for'}
        keywords = [w for w in words if len(w) >= 2 and w.lower() not in stop_words]

        # 提取有意义的词组
        meaningful_keywords = []
        for i in range(len(words) - 1):
            phrase = words[i] + words[i+1]
            if len(phrase) >= 4:
                meaningful_keywords.append(phrase)

        return list(set(keywords + meaningful_keywords))[:50]  # 限制关键词数量

    def _extract_categories(self, data: Dict) -> List[str]:
        """提取分类"""
        categories = []

        # 从mission字段提取
        mission = data.get('mission', '')
        if '优化' in mission:
            categories.append('优化')
        if '引擎' in mission:
            categories.append('引擎')
        if '知识' in mission:
            categories.append('知识')
        if '决策' in mission:
            categories.append('决策')
        if '执行' in mission:
            categories.append('执行')
        if '反馈' in mission:
            categories.append('反馈')
        if '协同' in mission:
            categories.append('协同')
        if '集成' in mission:
            categories.append('集成')
        if '预测' in mission or '预防' in mission:
            categories.append('预测预防')
        if '自愈' in mission or '健康' in mission:
            categories.append('健康自愈')
        if '驾驶舱' in mission or '可视化' in mission:
            categories.append('可视化')

        if not categories:
            categories.append('其他')

        return categories

    def _extract_tags(self, data: Dict) -> List[str]:
        """提取标签"""
        tags = []

        # 从current_goal提取
        goal = data.get('current_goal', '')
        if '自动' in goal:
            tags.append('自动化')
        if '智能' in goal:
            tags.append('智能化')
        if '深度' in goal:
            tags.append('深度增强')
        if '增强' in goal:
            tags.append('增强')
        if '引擎' in goal:
            tags.append('引擎')
        if '闭环' in goal:
            tags.append('闭环')
        if '集成' in goal:
            tags.append('集成')

        # 从做了什么提取
        actions = data.get('做了什么', [])
        if isinstance(actions, list):
            for action in actions:
                if '创建' in action:
                    tags.append('新建模块')
                if '增强' in action or '升级' in action:
                    tags.append('功能增强')
                if '集成' in action:
                    tags.append('集成')

        return list(set(tags)) if tags else ['general']

    def search_by_keyword(self, keyword: str, max_results: int = 10) -> List[Dict]:
        """按关键词搜索"""
        results = []
        keyword_lower = keyword.lower()

        # 搜索关键词索引
        matched_ids = self.knowledge_index['keyword_index'].get(keyword_lower, set())

        # 也搜索包含该关键词的条目
        for item_id, item in self.knowledge_index['knowledge_items'].items():
            if keyword_lower in item.get('title', '').lower() or keyword_lower in item.get('content', '').lower():
                matched_ids.add(item_id)

        # 获取匹配的条目
        for item_id in list(matched_ids)[:max_results]:
            item = self.knowledge_index['knowledge_items'].get(item_id)
            if item:
                results.append({
                    'id': item['id'],
                    'round': item['round'],
                    'title': item['title'],
                    'categories': item['categories'],
                    'tags': item['tags'],
                    'source': item['source']
                })

        return results

    def search_by_category(self, category: str, max_results: int = 20) -> List[Dict]:
        """按分类搜索"""
        results = []
        matched_ids = self.knowledge_index['category_index'].get(category, set())

        for item_id in list(matched_ids)[:max_results]:
            item = self.knowledge_index['knowledge_items'].get(item_id)
            if item:
                results.append({
                    'id': item['id'],
                    'round': item['round'],
                    'title': item['title'],
                    'categories': item['categories'],
                    'tags': item['tags']
                })

        return results

    def search_by_round(self, round_number: int) -> List[Dict]:
        """按轮次搜索"""
        results = []
        matched_ids = self.knowledge_index['round_index'].get(round_number, set())

        for item_id in matched_ids:
            item = self.knowledge_index['knowledge_items'].get(item_id)
            if item:
                results.append({
                    'id': item['id'],
                    'round': item['round'],
                    'title': item['title'],
                    'categories': item['categories']
                })

        return results

    def get_recent_knowledge(self, limit: int = 10) -> List[Dict]:
        """获取最近的知识条目"""
        items = sorted(
            self.knowledge_index['knowledge_items'].values(),
            key=lambda x: x.get('round', 0),
            reverse=True
        )
        return [{
            'id': item['id'],
            'round': item['round'],
            'title': item['title'],
            'categories': item['categories'],
            'tags': item['tags']
        } for item in items[:limit]]

    def build_knowledge_graph(self) -> Dict:
        """构建知识关联图谱"""
        nodes = {}
        edges = []

        # 创建节点
        for item_id, item in self.knowledge_index['knowledge_items'].items():
            nodes[item_id] = {
                'id': item_id,
                'label': item['title'][:50],  # 截断长标题
                'round': item['round'],
                'categories': item['categories'],
                'type': item['type']
            }

        # 创建边（基于关键词重叠）
        item_list = list(self.knowledge_index['knowledge_items'].values())
        for i, item1 in enumerate(item_list):
            for item2 in item_list[i+1:]:
                # 计算关键词重叠
                keywords1 = set(item1.get('keywords', []))
                keywords2 = set(item2.get('keywords', []))
                overlap = len(keywords1 & keywords2)

                if overlap >= 2:  # 至少2个共同关键词
                    edges.append({
                        'from': item1['id'],
                        'to': item2['id'],
                        'relation': 'keyword_overlap',
                        'weight': overlap
                    })

        # 创建边（基于分类）
        category_groups = defaultdict(list)
        for item_id, item in self.knowledge_index['knowledge_items'].items():
            for cat in item.get('categories', []):
                category_groups[cat].append(item_id)

        for cat, item_ids in category_groups.items():
            if len(item_ids) >= 2:
                for i in range(len(item_ids) - 1):
                    edges.append({
                        'from': item_ids[i],
                        'to': item_ids[i+1],
                        'relation': 'same_category',
                        'weight': 1
                    })

        # 识别聚类
        clusters = defaultdict(list)
        for item_id, item in self.knowledge_index['knowledge_items'].items():
            primary_cat = item.get('categories', ['other'])[0]
            clusters[primary_cat].append(item_id)

        self.knowledge_graph = {
            'nodes': nodes,
            'edges': edges,
            'clusters': dict(clusters),
            'last_updated': datetime.now().isoformat()
        }

        self._save_graph()
        return self.knowledge_graph

    def get_statistics(self) -> Dict:
        """获取知识索引统计信息"""
        return {
            'total_items': self.knowledge_index['total_items'],
            'total_keywords': len(self.knowledge_index['keyword_index']),
            'total_categories': len(self.knowledge_index['category_index']),
            'total_rounds': len(self.knowledge_index['round_index']),
            'total_tags': len(self.knowledge_index['tag_index']),
            'last_updated': self.knowledge_index.get('last_updated'),
            'graph_nodes': len(self.knowledge_graph.get('nodes', {})),
            'graph_edges': len(self.knowledge_graph.get('edges', []))
        }

    def push_to_cockpit(self) -> bool:
        """推送到进化驾驶舱"""
        try:
            os.makedirs(os.path.dirname(self.cockpit_file), exist_ok=True)

            data = {
                'timestamp': datetime.now().isoformat(),
                'statistics': self.get_statistics(),
                'recent_knowledge': self.get_recent_knowledge(5),
                'categories': list(self.knowledge_index['category_index'].keys()),
                'rounds_covered': sorted(list(self.knowledge_index['round_index'].keys()), reverse=True)[:20]
            }

            with open(self.cockpit_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            _safe_print(f"推送驾驶舱数据失败: {e}")
            return False


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='跨引擎知识索引与检索引擎')
    parser.add_argument('--collect', action='store_true', help='收集知识资产')
    parser.add_argument('--search', type=str, help='按关键词搜索')
    parser.add_argument('--category', type=str, help='按分类搜索')
    parser.add_argument('--round', type=int, help='按轮次搜索')
    parser.add_argument('--recent', action='store_true', help='获取最近知识')
    parser.add_argument('--build-graph', action='store_true', help='构建知识图谱')
    parser.add_argument('--stats', action='store_true', help='获取统计信息')
    parser.add_argument('--cockpit', action='store_true', help='推送到驾驶舱')
    parser.add_argument('--full-update', action='store_true', help='完整更新（收集+图谱+驾驶舱）')

    args = parser.parse_args()

    engine = CrossEngineKnowledgeIndex()

    if args.full_update:
        _safe_print("执行完整更新...")
        count = engine.collect_knowledge_from_completed_evolutions()
        _safe_print(f"已收集 {count} 个知识条目")
        engine.build_knowledge_graph()
        _safe_print("知识图谱已构建")
        engine.push_to_cockpit()
        _safe_print("驾驶舱数据已推送")
        stats = engine.get_statistics()
        _safe_print(f"统计信息: {json.dumps(stats, ensure_ascii=False, indent=2)}")

    elif args.collect:
        count = engine.collect_knowledge_from_completed_evolutions()
        _safe_print(f"已收集 {count} 个知识条目")
        engine._save_index()
        _safe_print("知识索引已保存")

    elif args.search:
        results = engine.search_by_keyword(args.search)
        _safe_print(f"搜索 '{args.search}' 结果 ({len(results)} 条):")
        for r in results:
            _safe_print(f"  [Round {r['round']}] {r['title']}")
            _safe_print(f"    分类: {r['categories']}, 标签: {r['tags']}")

    elif args.category:
        results = engine.search_by_category(args.category)
        _safe_print(f"分类 '{args.category}' 结果 ({len(results)} 条):")
        for r in results:
            _safe_print(f"  [Round {r['round']}] {r['title']}")

    elif args.round:
        results = engine.search_by_round(args.round)
        _safe_print(f"Round {args.round} 相关知识 ({len(results)} 条):")
        for r in results:
            _safe_print(f"  {r['title']} - 分类: {r['categories']}")

    elif args.recent:
        results = engine.get_recent_knowledge()
        _safe_print(f"最近知识 ({len(results)} 条):")
        for r in results:
            _safe_print(f"  [Round {r['round']}] {r['title']}")

    elif args.build_graph:
        graph = engine.build_knowledge_graph()
        _safe_print(f"知识图谱已构建: {len(graph['nodes'])} 节点, {len(graph['edges'])} 边")

    elif args.stats:
        stats = engine.get_statistics()
        _safe_print(json.dumps(stats, ensure_ascii=False, indent=2))

    elif args.cockpit:
        if engine.push_to_cockpit():
            _safe_print("驾驶舱数据推送成功")
        else:
            _safe_print("驾驶舱数据推送失败")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()