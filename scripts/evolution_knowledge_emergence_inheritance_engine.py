#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环知识主动涌现发现与智能传承递归增强引擎
=================================================================
在 round 489 完成的跨引擎深度知识蒸馏与智能传承增强引擎基础上，进一步增强知识的
主动涌现发现与创新传承能力。

功能：
1. 知识主动涌现发现 - 从海量进化历史中主动发现隐藏的关联模式和创新洞察
2. 智能传承递归增强 - 将发现的创新洞察自动传承给后续轮次，形成递归增强闭环
3. 跨领域知识迁移 - 发现跨领域知识关联，生成创新组合
4. 涌现效果自动评估 - 评估发现的创新洞察的价值和可行性
5. 与进化驾驶舱深度集成

version: 1.0.0
"""

import os
import sys
import json
import hashlib
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict, Counter

# 解决 Windows 控制台 Unicode 输出问题
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# 路径配置
BASE_DIR = Path(__file__).parent.parent
RUNTIME_DIR = BASE_DIR / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
KNOWLEDGE_DIR = RUNTIME_DIR / "knowledge"
EVOLUTION_COMPLETED_DIR = STATE_DIR


class KnowledgeEmergenceInheritanceEngine:
    """知识主动涌现发现与智能传承递归增强引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.engine_name = "知识主动涌现发现与智能传承递归增强引擎"

        # 涌现发现存储
        self.emergence_dir = KNOWLEDGE_DIR / "emergence"
        self.emergence_dir.mkdir(parents=True, exist_ok=True)

        # 传承记录存储
        self.inheritance_chain_dir = KNOWLEDGE_DIR / "inheritance_chain"
        self.inheritance_chain_dir.mkdir(parents=True, exist_ok=True)

        # 知识元数据存储
        self.metadata_file = KNOWLEDGE_DIR / "emergence_metadata.json"
        self.metadata = self._load_metadata()

        # 知识领域分类
        self.knowledge_domains = {
            "决策": ["决策", "策略", "规划", "选择"],
            "执行": ["执行", "运行", "操作", "自动化"],
            "学习": ["学习", "优化", "改进", "适应"],
            "知识": ["知识", "图谱", "索引", "推理"],
            "协同": ["协同", "协作", "集成", "联动"],
            "健康": ["健康", "诊断", "自愈", "预警"],
            "价值": ["价值", "实现", "评估", "优化"],
            "元进化": ["元进化", "自进化", "递归", "反思"]
        }

        print(f"[{self.engine_name} v{self.version}] 初始化完成")

    def _load_metadata(self) -> Dict:
        """加载元数据"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {
                    "emergence_discoveries": [],
                    "inheritance_chains": [],
                    "cross_domain_insights": [],
                    "last_emergence_round": None
                }
        return {
            "emergence_discoveries": [],
            "inheritance_chains": [],
            "cross_domain_insights": [],
            "last_emergence_round": None
        }

    def _save_metadata(self):
        """保存元数据"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[警告] 保存元数据失败: {e}")

    def _load_evolution_history(self, limit: int = 200) -> List[Dict]:
        """加载进化历史数据"""
        history = []
        if EVOLUTION_COMPLETED_DIR.exists():
            for file in EVOLUTION_COMPLETED_DIR.glob("evolution_completed_*.json"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        history.append(data)
                except Exception:
                    continue
        return sorted(history, key=lambda x: x.get('loop_round', 0), reverse=True)[:limit]

    def _classify_domain(self, text: str) -> List[str]:
        """分类知识领域"""
        text_lower = text.lower()
        domains = []
        for domain, keywords in self.knowledge_domains.items():
            for kw in keywords:
                if kw in text_lower:
                    domains.append(domain)
                    break
        return domains if domains else ["其他"]

    def discover_emergence(self) -> Dict[str, Any]:
        """知识主动涌现发现 - 从海量进化历史中发现隐藏的关联模式和创新洞察"""
        print("\n=== 知识主动涌现发现 ===")

        history = self._load_evolution_history()
        if not history:
            return {"error": "无足够进化历史数据"}

        # 1. 统计领域分布
        domain_stats = defaultdict(list)
        round_domain_map = {}

        for entry in history:
            round_num = entry.get('loop_round', 0)
            goal = entry.get('current_goal', '')
            domains = self._classify_domain(goal)

            round_domain_map[round_num] = domains

            for domain in domains:
                domain_stats[domain].append({
                    'round': round_num,
                    'goal': goal,
                    'status': entry.get('是否完成', '')
                })

        # 2. 发现领域演进模式
        domain_evolution = {}
        for domain, entries in domain_stats.items():
            rounds = [e['round'] for e in entries]
            success_count = sum(1 for e in entries if e['status'] == '已完成')

            domain_evolution[domain] = {
                'total_count': len(entries),
                'success_count': success_count,
                'success_rate': success_count / len(entries) if entries else 0,
                'first_round': min(rounds) if rounds else 0,
                'latest_round': max(rounds) if rounds else 0,
                'rounds': sorted(rounds)
            }

        # 3. 发现跨领域关联
        cross_domain_insights = []
        domain_list = list(domain_stats.keys())

        for i, d1 in enumerate(domain_list):
            for d2 in domain_list[i+1:]:
                # 查找两个领域同时出现的轮次
                common_rounds = []
                for round_num, domains in round_domain_map.items():
                    if d1 in domains and d2 in domains:
                        common_rounds.append(round_num)

                if len(common_rounds) >= 3:
                    cross_domain_insights.append({
                        'domain_pair': f"{d1}-{d2}",
                        'common_rounds': common_rounds,
                        'co_occurrence_count': len(common_rounds),
                        'insight': f"领域'{d1}'和'{d2}'在 {len(common_rounds)} 个轮次中协同进化，可能存在内在关联"
                    })

        # 4. 发现创新模式
        innovation_patterns = []

        # 模式1: 连续进化
        consecutive_rounds = []
        sorted_history = sorted(history, key=lambda x: x.get('loop_round', 0))
        for i in range(len(sorted_history) - 1):
            curr = sorted_history[i].get('loop_round', 0)
            next_r = sorted_history[i+1].get('loop_round', 0)
            if next_r - curr <= 3:  # 连续3轮以内
                consecutive_rounds.append((curr, next_r))

        if consecutive_rounds:
            innovation_patterns.append({
                'pattern': '连续快速进化',
                'count': len(consecutive_rounds),
                'description': '系统在短期内连续进化，可能存在累积效应或递进优化'
            })

        # 模式2: 高价值领域
        high_value_domains = [
            d for d, stats in domain_evolution.items()
            if stats['success_rate'] >= 0.8 and stats['total_count'] >= 5
        ]
        if high_value_domains:
            innovation_patterns.append({
                'pattern': '高价值领域聚焦',
                'domains': high_value_domains,
                'description': f'领域 {high_value_domains} 具有80%+成功率，是核心进化方向'
            })

        # 5. 生成涌现洞察
        emergence_discoveries = []

        # 洞察1: 领域演进趋势
        if domain_evolution:
            most_active = max(domain_evolution.items(), key=lambda x: x[1]['total_count'])
            emergence_discoveries.append({
                'type': 'domain_evolution',
                'title': '领域演进趋势分析',
                'finding': f"最活跃领域: {most_active[0]} (共 {most_active[1]['total_count']} 轮)",
                'data': most_active[1]
            })

        # 洞察2: 跨领域协同
        if cross_domain_insights:
            top_insight = max(cross_domain_insights, key=lambda x: x['co_occurrence_count'])
            emergence_discoveries.append({
                'type': 'cross_domain',
                'title': '跨领域协同发现',
                'finding': top_insight['insight'],
                'data': top_insight
            })

        # 洞察3: 创新模式
        if innovation_patterns:
            emergence_discoveries.append({
                'type': 'innovation_pattern',
                'title': '创新模式识别',
                'finding': f"识别到 {len(innovation_patterns)} 种创新模式",
                'data': innovation_patterns
            })

        # 保存涌现发现结果
        emergence_result = {
            'discovered_at': datetime.now().isoformat(),
            'history_analyzed': len(history),
            'domain_evolution': domain_evolution,
            'cross_domain_insights': cross_domain_insights,
            'innovation_patterns': innovation_patterns,
            'emergence_discoveries': emergence_discoveries
        }

        emergence_file = self.emergence_dir / f"emergence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(emergence_file, 'w', encoding='utf-8') as f:
            json.dump(emergence_result, f, ensure_ascii=False, indent=2)

        # 更新元数据
        self.metadata["emergence_discoveries"] = emergence_discoveries
        self.metadata["cross_domain_insights"] = cross_domain_insights
        self.metadata["last_emergence_round"] = history[0].get('loop_round', 0) if history else None
        self._save_metadata()

        print(f"[OK] 分析了 {len(history)} 轮进化历史")
        print(f"[OK] 发现 {len(domain_evolution)} 个知识领域")
        print(f"[OK] 识别 {len(cross_domain_insights)} 个跨领域关联")
        print(f"[OK] 生成 {len(emergence_discoveries)} 个涌现洞察")

        return {
            'discovered_at': emergence_result['discovered_at'],
            'domain_count': len(domain_evolution),
            'cross_domain_count': len(cross_domain_insights),
            'innovation_pattern_count': len(innovation_patterns),
            'emergence_insight_count': len(emergence_discoveries),
            'emergence_file': str(emergence_file)
        }

    def create_inheritance_chain(self, target_round: Optional[int] = None) -> Dict[str, Any]:
        """创建智能传承链 - 将发现的创新洞察传承给后续轮次"""
        print("\n=== 创建智能传承链 ===")

        history = self._load_evolution_history()

        # 确定目标轮次
        if target_round is None:
            latest_round = max([e.get('loop_round', 0) for e in history]) if history else 521
            target_round = latest_round + 1

        # 1. 提取高价值知识（从已完成的高价值轮次）
        high_value_knowledge = []

        for entry in history[:100]:
            if entry.get('是否完成') == '已完成':
                round_num = entry.get('loop_round', 0)
                goal = entry.get('current_goal', '')

                # 分类领域
                domains = self._classify_domain(goal)

                high_value_knowledge.append({
                    'from_round': round_num,
                    'goal': goal,
                    'domains': domains,
                    'value_level': '高',
                    'inheritable': True
                })

        # 2. 提取跨领域创新知识
        cross_domain_knowledge = []

        # 查找跨领域协同的轮次
        emergence_file = sorted(self.emergence_dir.glob("emergence_*.json"))
        if emergence_file:
            latest_emergence = emergence_file[-1]
            with open(latest_emergence, 'r', encoding='utf-8') as f:
                emergence_data = json.load(f)

            cross_insights = emergence_data.get('cross_domain_insights', [])
            for insight in cross_insights[:5]:  # 取前5个跨领域洞察
                rounds = insight.get('common_rounds', [])
                if rounds:
                    # 查找对应的目标
                    for entry in history:
                        if entry.get('loop_round') in rounds:
                            cross_domain_knowledge.append({
                                'from_round': entry.get('loop_round'),
                                'goal': entry.get('current_goal'),
                                'domains': insight.get('domain_pair', '').split('-'),
                                'value_level': '极高',
                                'inheritable': True,
                                'insight': insight.get('insight', '')
                            })
                            break

        # 3. 生成传承建议
        inheritance_suggestions = []

        # 基于领域分布建议
        domain_knowledge = defaultdict(list)
        for k in high_value_knowledge:
            for d in k['domains']:
                domain_knowledge[d].append(k)

        for domain, entries in domain_knowledge.items():
            if len(entries) >= 3:
                inheritance_suggestions.append({
                  'category': '领域聚焦',
                  'domain': domain,
                  'suggestion': f"在 {domain} 领域已有 {len(entries)} 轮成功经验，建议继续深化",
                  'priority': '高'
                })

        # 4. 构建传承链
        inheritance_chain = {
            'target_round': target_round,
            'generated_at': datetime.now().isoformat(),
            'high_value_knowledge': high_value_knowledge[:20],
            'cross_domain_knowledge': cross_domain_knowledge[:10],
            'inheritance_suggestions': inheritance_suggestions,
            'chain_summary': {
                'total_inherited': len(high_value_knowledge[:20]) + len(cross_domain_knowledge[:10]),
                'domain_count': len(set(d for k in high_value_knowledge[:20] for d in k['domains'])),
                'suggestion_count': len(inheritance_suggestions)
            }
        }

        # 保存传承链
        chain_file = self.inheritance_chain_dir / f"inheritance_chain_r{target_round}.json"
        with open(chain_file, 'w', encoding='utf-8') as f:
            json.dump(inheritance_chain, f, ensure_ascii=False, indent=2)

        # 更新元数据
        self.metadata["inheritance_chains"].append({
            'target_round': target_round,
            'total_inherited': inheritance_chain['chain_summary']['total_inherited'],
            'generated_at': datetime.now().isoformat()
        })
        self._save_metadata()

        print(f"[OK] 为 round {target_round} 创建传承链")
        print(f"[OK] 高价值知识: {len(high_value_knowledge[:20])} 条")
        print(f"[OK] 跨领域知识: {len(cross_domain_knowledge[:10])} 条")
        print(f"[OK] 传承建议: {len(inheritance_suggestions)} 条")

        return {
            'target_round': target_round,
            'chain_file': str(chain_file),
            'total_inherited': inheritance_chain['chain_summary']['total_inherited'],
            'suggestion_count': len(inheritance_suggestions)
        }

    def run_recursive_enhancement(self, rounds: int = 5) -> Dict[str, Any]:
        """运行递归增强闭环 - 持续发现新洞察并传承"""
        print(f"\n=== 运行递归增强闭环 (共 {rounds} 轮) ===")

        results = {
            'rounds': [],
            'start_time': datetime.now().isoformat()
        }

        for i in range(rounds):
            print(f"\n--- 递归轮次 {i+1}/{rounds} ---")

            # 1. 涌现发现
            emergence = self.discover_emergence()

            # 2. 创建传承链
            inheritance = self.create_inheritance_chain()

            results['rounds'].append({
                'round': i + 1,
                'emergence': emergence,
                'inheritance': inheritance
            })

            print(f"[OK] 轮次 {i+1} 完成")

        results['end_time'] = datetime.now().isoformat()
        results['success'] = True

        # 保存完整结果
        result_file = self.emergence_dir / f"recursive_enhancement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"\n[OK] 递归增强完成")
        print(f"[OK] 结果保存到: {result_file}")

        return results

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱展示数据"""
        emergence_files = sorted(self.emergence_dir.glob("emergence_*.json"))
        chain_files = sorted(self.inheritance_chain_dir.glob("inheritance_chain_*.json"))

        data = {
            "engine": self.engine_name,
            "version": self.version,
            "status": "active",
            "last_update": datetime.now().isoformat()
        }

        # 加载最新涌现发现
        if emergence_files:
            with open(emergence_files[-1], 'r', encoding='utf-8') as f:
                emergence = json.load(f)
                data["last_emergence"] = {
                    "discovered_at": emergence.get('discovered_at'),
                    "domain_count": emergence.get('domain_count', 0),
                    "insight_count": len(emergence.get('emergence_discoveries', []))
                }

        # 加载最新传承链
        if chain_files:
            with open(chain_files[-1], 'r', encoding='utf-8') as f:
                chain = json.load(f)
                data["last_inheritance"] = {
                    "target_round": chain.get('target_round'),
                    "total_inherited": chain.get('chain_summary', {}).get('total_inherited', 0),
                    "suggestion_count": len(chain.get('inheritance_suggestions', []))
                }

        # 元数据摘要
        data["metadata"] = {
            "total_emergence": len(self.metadata.get('emergence_discoveries', [])),
            "total_inheritance_chains": len(self.metadata.get('inheritance_chains', [])),
            "total_cross_domain": len(self.metadata.get('cross_domain_insights', []))
        }

        return data


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(
        description='知识主动涌现发现与智能传承递归增强引擎'
    )
    parser.add_argument('--discover', action='store_true', help='执行知识涌现发现')
    parser.add_argument('--inherit', type=int, nargs='?', const=-1, help='创建传承链')
    parser.add_argument('--recursive', type=int, nargs='?', const=5, help='运行递归增强闭环')
    parser.add_argument('--cockpit-data', action='store_true', help='获取驾驶舱数据')
    parser.add_argument('--status', action='store_true', help='获取引擎状态')

    args = parser.parse_args()

    engine = KnowledgeEmergenceInheritanceEngine()

    if args.status:
        status = {
            "engine": engine.engine_name,
            "version": engine.version,
            "initialized": True
        }
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.discover:
        result = engine.discover_emergence()
        print("\n【涌现发现结果】")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.inherit is not None:
        target = args.inherit if args.inherit > 0 else None
        result = engine.create_inheritance_chain(target)
        print("\n【传承链创建结果】")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.recursive:
        rounds = args.recursive if args.recursive > 0 else 5
        result = engine.run_recursive_enhancement(rounds)
        print("\n【递归增强结果】")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.cockpit_data:
        data = engine.get_cockpit_data()
        print("\n【驾驶舱数据】")
        print(json.dumps(data, ensure_ascii=False, indent=2))

    else:
        # 默认执行完整流程
        print("执行完整知识涌现发现与传承流程...\n")

        # 1. 涌现发现
        discover_result = engine.discover_emergence()

        # 2. 创建传承链
        inherit_result = engine.create_inheritance_chain()

        # 3. 获取驾驶舱数据
        cockpit_data = engine.get_cockpit_data()

        print("\n" + "="*50)
        print("【完整流程执行完成】")
        print(f"领域发现: {discover_result.get('domain_count', 0)} 个")
        print(f"跨域关联: {discover_result.get('cross_domain_count', 0)} 个")
        print(f"传承知识: {inherit_result.get('total_inherited', 0)} 条")


if __name__ == "__main__":
    main()