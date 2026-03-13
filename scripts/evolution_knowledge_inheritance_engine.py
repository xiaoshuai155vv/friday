#!/usr/bin/env python3
"""
智能跨代进化知识传承引擎（Evolution Knowledge Inheritance Engine）
version 1.0.0

让系统能够跨轮次传承和累积进化知识，实现真正的「元进化」能力 - 让每一轮的进化成果、
学习教训、最佳实践能够被后续轮次复用，形成持续累积的进化智慧。

功能：
1. 进化知识提取（从历史进化中提取可复用的模式、最佳实践）
2. 知识结构化存储（构建进化知识图谱）
3. 跨代知识检索与应用（在每轮进化时自动检索相关历史知识）
4. 知识有效性评估与更新
5. 与进化决策引擎深度集成

依赖：
- evolution_direction_discovery.py (round 239)
- evolution_iteration_coordination.py (round 238)
- evolution_adaptive_optimizer.py (round 237)
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class EvolutionKnowledgeInheritance:
    """智能跨代进化知识传承引擎"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.runtime_dir = self.project_root / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.references_dir = self.project_root / "references"

        # 知识库存储路径
        self.knowledge_db_dir = self.runtime_dir / "knowledge_db"
        self.knowledge_db_dir.mkdir(exist_ok=True)

        # 知识索引文件
        self.knowledge_index_file = self.knowledge_db_dir / "knowledge_index.json"
        self.knowledge_patterns_file = self.knowledge_db_dir / "knowledge_patterns.json"
        self.knowledge_best_practices_file = self.knowledge_db_dir / "knowledge_best_practices.json"

        # 加载或初始化知识库
        self.knowledge_index = self._load_knowledge_index()
        self.knowledge_patterns = self._load_knowledge_patterns()
        self.best_practices = self._load_best_practices()

    def _load_knowledge_index(self) -> Dict:
        """加载知识索引"""
        if self.knowledge_index_file.exists():
            try:
                with open(self.knowledge_index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "total_knowledge_entries": 0,
            "knowledge_categories": {},
            "cross_round_links": []
        }

    def _load_knowledge_patterns(self) -> List[Dict]:
        """加载知识模式"""
        if self.knowledge_patterns_file.exists():
            try:
                with open(self.knowledge_patterns_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return []

    def _load_best_practices(self) -> List[Dict]:
        """加载最佳实践"""
        if self.knowledge_best_practices_file.exists():
            try:
                with open(self.knowledge_best_practices_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return []

    def _save_knowledge_index(self):
        """保存知识索引"""
        self.knowledge_index["last_updated"] = datetime.now().isoformat()
        with open(self.knowledge_index_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_index, f, ensure_ascii=False, indent=2)

    def _save_knowledge_patterns(self):
        """保存知识模式"""
        with open(self.knowledge_patterns_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_patterns, f, ensure_ascii=False, indent=2)

    def _save_best_practices(self):
        """保存最佳实践"""
        with open(self.knowledge_best_practices_file, 'w', encoding='utf-8') as f:
            json.dump(self.best_practices, f, ensure_ascii=False, indent=2)

    def extract_knowledge_from_history(self) -> Dict[str, Any]:
        """
        从历史进化中提取知识
        返回：提取的知识摘要
        """
        extracted = {
            "patterns": [],
            "best_practices": [],
            "lessons_learned": [],
            "success_factors": [],
            "failure_patterns": []
        }

        # 加载所有进化历史
        state_dir = self.state_dir
        evolution_files = sorted(state_dir.glob("evolution_completed_*.json"))

        # 分析最近30轮进化
        recent_history = []
        for f in list(evolution_files)[-30:]:
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    recent_history.append(data)
            except:
                pass

        # 按轮次排序
        recent_history.sort(key=lambda x: x.get('loop_round', 0))

        # 提取进化模式
        for i, evo in enumerate(recent_history):
            goal = evo.get('current_goal', '')
            done = evo.get('做了什么', '')

            if goal and goal != 'TBD':
                # 提取领域关键词
                domains = []
                keywords = ['引擎', 'engine', '协同', '学习', '预测', '优化', '自动', '智能', '决策', '执行', '集成']
                for kw in keywords:
                    if kw.lower() in goal.lower():
                        domains.append(kw)

                if domains:
                    extracted["patterns"].append({
                        "round": evo.get('loop_round', i),
                        "goal": goal,
                        "domains": domains,
                        "status": evo.get('是否完成', 'unknown')
                    })

            # 提取成功要素
            if evo.get('是否完成') == '已完成':
                if '基线' in done and '通过' in done:
                    extracted["success_factors"].append({
                        "round": evo.get('loop_round', i),
                        "factor": "基线校验通过"
                    })
                if '针对性' in done and '通过' in done:
                    extracted["success_factors"].append({
                        "round": evo.get('loop_round', i),
                        "factor": "针对性验证通过"
                    })

        # 统计知识分类
        category_stats = defaultdict(int)
        for pattern in extracted["patterns"]:
            for domain in pattern.get("domains", []):
                category_stats[domain] += 1

        extracted["category_stats"] = dict(category_stats)

        return extracted

    def build_knowledge_graph(self) -> Dict[str, Any]:
        """
        构建进化知识图谱
        返回：知识图谱结构
        """
        graph = {
            "nodes": [],  # 进化节点
            "edges": [],  # 进化关联
            "clusters": []  # 领域聚类
        }

        # 加载进化历史
        state_dir = self.state_dir
        evolution_files = sorted(state_dir.glob("evolution_completed_*.json"))

        nodes = []
        for f in list(evolution_files)[-50:]:  # 最近50轮
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    node = {
                        "id": f"round_{data.get('loop_round', 0)}",
                        "round": data.get('loop_round', 0),
                        "goal": data.get('current_goal', ''),
                        "status": data.get('是否完成', 'unknown'),
                        "domains": self._extract_domains(data.get('current_goal', ''))
                    }
                    nodes.append(node)
            except:
                pass

        graph["nodes"] = nodes

        # 建立关联边（基于领域相似性）
        edges = []
        for i, node1 in enumerate(nodes):
            for j, node2 in enumerate(nodes[i+1:], i+1):
                # 检查是否有相同领域
                domains1 = set(node1.get("domains", []))
                domains2 = set(node2.get("domains", []))
                common = domains1 & domains2
                if common:
                    edges.append({
                        "source": node1["id"],
                        "target": node2["id"],
                        "weight": len(common),
                        "shared_domains": list(common)
                    })

        graph["edges"] = edges

        # 领域聚类
        domain_groups = defaultdict(list)
        for node in nodes:
            for domain in node.get("domains", []):
                domain_groups[domain].append(node["id"])

        for domain, node_ids in domain_groups.items():
            if len(node_ids) >= 2:
                graph["clusters"].append({
                    "domain": domain,
                    "rounds": node_ids,
                    "size": len(node_ids)
                })

        return graph

    def _extract_domains(self, goal: str) -> List[str]:
        """从目标中提取领域关键词"""
        domains = []
        keywords = ['引擎', 'engine', '协同', '学习', '预测', '优化', '自动', '智能',
                    '决策', '执行', '集成', '发现', '评估', '诊断', '监控', '分析']

        goal_lower = goal.lower()
        for kw in keywords:
            if kw.lower() in goal_lower:
                domains.append(kw)

        return domains

    def query_knowledge(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        跨代知识检索
        参数：
            query: 查询关键词
            max_results: 最大返回结果数
        返回：相关知识条目列表
        """
        results = []
        query_lower = query.lower()

        # 在知识模式中搜索
        for pattern in self.knowledge_patterns:
            if any(query_lower in str(v).lower() for v in pattern.values()):
                results.append({
                    "type": "pattern",
                    "data": pattern,
                    "relevance": self._calculate_relevance(query, pattern)
                })

        # 在最佳实践中搜索
        for practice in self.best_practices:
            if any(query_lower in str(v).lower() for v in practice.values()):
                results.append({
                    "type": "best_practice",
                    "data": practice,
                    "relevance": self._calculate_relevance(query, practice)
                })

        # 按相关性排序
        results.sort(key=lambda x: x.get('relevance', 0), reverse=True)

        return results[:max_results]

    def _calculate_relevance(self, query: str, data: Dict) -> float:
        """计算查询与数据的相关性"""
        query_lower = query.lower()
        score = 0.0

        for value in data.values():
            value_str = str(value).lower()
            if query_lower in value_str:
                score += 1.0

        return score

    def recommend_knowledge(self, current_goal: str) -> List[Dict[str, Any]]:
        """
        基于当前进化目标推荐相关知识
        参数：
            current_goal: 当前进化目标
        返回：推荐的知识条目
        """
        recommendations = []

        # 提取当前目标领域
        current_domains = self._extract_domains(current_goal)

        # 在历史中查找相关进化
        state_dir = self.state_dir
        evolution_files = sorted(state_dir.glob("evolution_completed_*.json"))

        for f in list(evolution_files)[-50:]:
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    goal = data.get('current_goal', '')
                    history_domains = self._extract_domains(goal)

                    # 计算领域重叠度
                    overlap = len(set(current_domains) & set(history_domains))

                    if overlap > 0 and data.get('是否完成') == '已完成':
                        recommendations.append({
                            "round": data.get('loop_round', 0),
                            "goal": goal,
                            "overlap": overlap,
                            "shared_domains": list(set(current_domains) & set(history_domains)),
                            "relevance_score": overlap * 2.0
                        })
            except:
                pass

        # 按相关性排序
        recommendations.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

        return recommendations[:5]

    def update_knowledge_from_current_round(self, evolution_data: Dict) -> bool:
        """
        从当前轮进化更新知识库
        参数：
            evolution_data: 当前轮进化数据
        返回：是否更新成功
        """
        try:
            # 提取知识
            goal = evolution_data.get('current_goal', '')
            done = evolution_data.get('做了什么', '')
            status = evolution_data.get('是否完成', 'unknown')
            round_num = evolution_data.get('loop_round', 0)

            # 添加新模式
            if goal and goal != 'TBD':
                new_pattern = {
                    "round": round_num,
                    "goal": goal,
                    "domains": self._extract_domains(goal),
                    "status": status,
                    "timestamp": datetime.now().isoformat()
                }

                # 检查是否已存在
                existing = False
                for p in self.knowledge_patterns:
                    if p.get('round') == round_num:
                        existing = True
                        break

                if not existing:
                    self.knowledge_patterns.append(new_pattern)

            # 如果成功完成，提取最佳实践
            if status == '已完成' and done:
                best_practice = {
                    "round": round_num,
                    "goal": goal,
                    "key_actions": self._extract_key_actions(done),
                    "success_factors": self._extract_success_factors(done),
                    "timestamp": datetime.now().isoformat()
                }

                # 检查是否已存在
                existing = False
                for bp in self.best_practices:
                    if bp.get('round') == round_num:
                        existing = True
                        break

                if not existing:
                    self.best_practices.append(best_practice)

            # 更新索引
            self.knowledge_index["total_knowledge_entries"] = len(self.knowledge_patterns) + len(self.best_practices)
            self.knowledge_index["knowledge_categories"] = self._count_categories()

            # 保存
            self._save_knowledge_index()
            self._save_knowledge_patterns()
            self._save_best_practices()

            return True
        except Exception as e:
            print(f"更新知识库失败: {e}")
            return False

    def _extract_key_actions(self, done_text: str) -> List[str]:
        """从进化记录中提取关键动作"""
        actions = []
        # 简单提取：按数字序号分割
        parts = done_text.split('\n')
        for part in parts:
            part = part.strip()
            if part and (part[0].isdigit() or part.startswith('-')):
                # 清理前缀
                clean = part.lstrip('0123456789.-) ').strip()
                if len(clean) > 5:
                    actions.append(clean[:100])  # 限制长度

        return actions[:5]

    def _extract_success_factors(self, done_text: str) -> List[str]:
        """提取成功要素"""
        factors = []

        if '基线' in done_text and '通过' in done_text:
            factors.append("基线校验通过")
        if '针对性' in done_text and '通过' in done_text:
            factors.append("针对性验证通过")
        if '模块' in done_text and '创建' in done_text:
            factors.append("成功创建模块")
        if '集成' in done_text and 'do.py' in done_text:
            factors.append("成功集成到主程序")

        return factors

    def _count_categories(self) -> Dict[str, int]:
        """统计知识分类"""
        counts = defaultdict(int)
        for pattern in self.knowledge_patterns:
            for domain in pattern.get("domains", []):
                counts[domain] += 1
        return dict(counts)

    def get_knowledge_status(self) -> Dict[str, Any]:
        """获取知识库状态"""
        return {
            "version": self.knowledge_index.get("version", "1.0.0"),
            "total_entries": self.knowledge_index.get("total_knowledge_entries", 0),
            "pattern_count": len(self.knowledge_patterns),
            "best_practice_count": len(self.best_practices),
            "categories": self.knowledge_index.get("knowledge_categories", {}),
            "last_updated": self.knowledge_index.get("last_updated", "unknown")
        }

    def analyze_knowledge_gaps(self) -> List[Dict[str, Any]]:
        """分析知识缺口"""
        gaps = []

        # 检查知识覆盖度
        all_domains = ['引擎', 'engine', '协同', '学习', '预测', '优化', '自动',
                       '智能', '决策', '执行', '集成', '发现', '评估']

        category_counts = self.knowledge_index.get("knowledge_categories", {})

        for domain in all_domains:
            count = category_counts.get(domain, 0)
            if count < 3:  # 少于3条记录
                gaps.append({
                    "domain": domain,
                    "current_count": count,
                    "recommended_min": 3,
                    "priority": "high" if count == 0 else "medium"
                })

        return gaps


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description='智能跨代进化知识传承引擎')
    parser.add_argument('command', nargs='?', default='status',
                       choices=['status', 'extract', 'graph', 'query', 'recommend', 'gaps', 'update'],
                       help='要执行的命令')
    parser.add_argument('--query', '-q', type=str, default='',
                       help='查询关键词')
    parser.add_argument('--goal', '-g', type=str, default='',
                       help='当前进化目标')
    parser.add_argument('--round', '-r', type=int, default=0,
                       help='轮次号')

    args = parser.parse_args()

    engine = EvolutionKnowledgeInheritance()

    if args.command == 'status':
        status = engine.get_knowledge_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.command == 'extract':
        result = engine.extract_knowledge_from_history()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'graph':
        result = engine.build_knowledge_graph()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'query':
        if not args.query:
            print("错误：查询命令需要 --query 参数")
            return
        results = engine.query_knowledge(args.query)
        print(json.dumps(results, ensure_ascii=False, indent=2))

    elif args.command == 'recommend':
        if not args.goal:
            print("错误：推荐命令需要 --goal 参数")
            return
        results = engine.recommend_knowledge(args.goal)
        print(json.dumps(results, ensure_ascii=False, indent=2))

    elif args.command == 'gaps':
        gaps = engine.analyze_knowledge_gaps()
        print(json.dumps(gaps, ensure_ascii=False, indent=2))

    elif args.command == 'update':
        if args.round == 0:
            print("错误：更新命令需要 --round 参数指定轮次")
            return
        # 从文件加载进化数据
        evo_file = Path(f"runtime/state/evolution_completed_ev_{args.round}.json")
        if evo_file.exists():
            with open(evo_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            success = engine.update_knowledge_from_current_round(data)
            print(json.dumps({"success": success}, ensure_ascii=False, indent=2))
        else:
            print(json.dumps({"error": f"未找到轮次 {args.round} 的进化记录"}, ensure_ascii=False))


if __name__ == '__main__':
    main()