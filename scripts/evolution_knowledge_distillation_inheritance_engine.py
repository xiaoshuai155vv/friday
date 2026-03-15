#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环跨引擎深度知识蒸馏与智能传承增强引擎
==================================================
在 round 488 完成的跨引擎协同学习与知识共享深度增强引擎基础上，进一步增强知识蒸馏与传承能力。

功能：
1. 知识自动蒸馏 - 从各引擎执行结果中提炼核心知识
2. 跨代知识传承机制 - 知识版本管理、跨轮次传递
3. 知识质量自动评估与筛选
4. 智能知识检索与推荐
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
from typing import Dict, List, Any, Optional, Tuple

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


class KnowledgeDistillationInheritanceEngine:
    """跨引擎深度知识蒸馏与智能传承增强引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.engine_name = "跨引擎深度知识蒸馏与智能传承增强引擎"

        # 确保目录存在
        KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
        (KNOWLEDGE_DIR / "distilled").mkdir(exist_ok=True)
        (KNOWLEDGE_DIR / "inheritance").mkdir(exist_ok=True)
        (KNOWLEDGE_DIR / "quality").mkdir(exist_ok=True)

        # 知识元数据存储
        self.metadata_file = KNOWLEDGE_DIR / "knowledge_metadata.json"
        self.metadata = self._load_metadata()

        print(f"[{self.engine_name} v{self.version}] 初始化完成")

    def _load_metadata(self) -> Dict:
        """加载知识元数据"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {"knowledge_entries": [], "version_history": [], "last_update": None}
        return {"knowledge_entries": [], "version_history": [], "last_update": None}

    def _save_metadata(self):
        """保存知识元数据"""
        self.metadata["last_update"] = datetime.now().isoformat()
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[警告] 保存元数据失败: {e}")

    def _compute_knowledge_hash(self, content: str) -> str:
        """计算知识内容的哈希值"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]

    def _load_evolution_history(self) -> List[Dict]:
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
        return sorted(history, key=lambda x: x.get('loop_round', 0), reverse=True)

    def distill_knowledge(self, max_entries: int = 50) -> Dict[str, Any]:
        """知识自动蒸馏 - 从进化历史中提炼核心知识"""
        print("\n=== 知识自动蒸馏 ===")

        history = self._load_evolution_history()
        distilled_knowledge = []

        for entry in history[:max_entries]:
            round_num = entry.get('loop_round', 0)
            goal = entry.get('current_goal', '')
            actions = entry.get('做了什么', [])

            # 提取核心知识要点
            if isinstance(actions, list):
                action_summary = '； '.join(str(a) for a in actions[:3])
            else:
                action_summary = str(actions)[:200]

            knowledge_entry = {
                "round": round_num,
                "goal": goal,
                "summary": action_summary,
                "status": entry.get('是否完成', '未知'),
                "timestamp": entry.get('updated_at', '')
            }
            distilled_knowledge.append(knowledge_entry)

        # 保存蒸馏后的知识
        distilled_file = KNOWLEDGE_DIR / "distilled" / "evolution_knowledge_distilled.json"
        with open(distilled_file, 'w', encoding='utf-8') as f:
            json.dump(distilled_knowledge, f, ensure_ascii=False, indent=2)

        # 更新元数据
        self.metadata["knowledge_entries"] = [
            {"round": e["round"], "goal": e["goal"], "hash": self._compute_knowledge_hash(e["goal"])}
            for e in distilled_knowledge
        ]
        self._save_metadata()

        result = {
            "distilled_count": len(distilled_knowledge),
            "knowledge_file": str(distilled_file),
            "latest_rounds": [e["round"] for e in distilled_knowledge[:10]]
        }

        print(f"[OK] Distilled {len(distilled_knowledge)} knowledge entries")
        print(f"[OK] Latest rounds: {result['latest_rounds'][:5]}")

        return result

    def inherit_knowledge(self, target_round: Optional[int] = None) -> Dict[str, Any]:
        """跨代知识传承 - 将知识传递到目标轮次"""
        print("\n=== 跨代知识传承 ===")

        history = self._load_evolution_history()

        # 确定目标轮次（默认最新轮次+1）
        if target_round is None:
            target_round = max([e.get('loop_round', 0) for e in history]) + 1

        # 选择要传承的知识（选取最有价值的）
        inherited_knowledge = []

        # 选取每个阶段的代表性知识
        stages = {}
        for entry in history[:100]:
            round_num = entry.get('loop_round', 0)
            goal = entry.get('current_goal', '')

            # 按百位分组
            stage_key = (round_num // 100) * 100
            if stage_key not in stages:
                stages[stage_key] = entry

        for stage_key in sorted(stages.keys()):
            entry = stages[stage_key]
            inherited_knowledge.append({
                "from_round": entry.get('loop_round', 0),
                "goal": entry.get('current_goal', ''),
                "status": entry.get('是否完成', ''),
                "value": "高" if entry.get('是否完成') == '已完成' else "中"
            })

        # 保存传承知识
        inheritance_file = KNOWLEDGE_DIR / "inheritance" / f"knowledge_inheritance_r{target_round}.json"
        with open(inheritance_file, 'w', encoding='utf-8') as f:
            json.dump({
                "target_round": target_round,
                "inherited_knowledge": inherited_knowledge,
                "generated_at": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)

        # 记录版本历史
        self.metadata["version_history"].append({
            "version": target_round,
            "inherited_count": len(inherited_knowledge),
            "timestamp": datetime.now().isoformat()
        })
        self._save_metadata()

        print(f"[OK] Generated knowledge inheritance package for round {target_round}")
        print(f"[OK] Contains {len(inherited_knowledge)} inherited knowledge entries")

        return {
            "target_round": target_round,
            "inherited_count": len(inherited_knowledge),
            "inheritance_file": str(inheritance_file)
        }

    def assess_quality(self) -> Dict[str, Any]:
        """知识质量自动评估"""
        print("\n=== 知识质量评估 ===")

        distilled_file = KNOWLEDGE_DIR / "distilled" / "evolution_knowledge_distilled.json"

        if not distilled_file.exists():
            return {"error": "请先执行知识蒸馏"}

        with open(distilled_file, 'r', encoding='utf-8') as f:
            knowledge = json.load(f)

        # 质量指标计算
        total = len(knowledge)
        completed = sum(1 for k in knowledge if k.get('status') == '已完成')
        success_rate = (completed / total * 100) if total > 0 else 0

        # 评估结果
        quality_report = {
            "total_knowledge": total,
            "completed": completed,
            "success_rate": round(success_rate, 2),
            "quality_score": min(100, success_rate + 10),  # 基础分+奖励
            "assessed_at": datetime.now().isoformat()
        }

        # 保存评估结果
        quality_file = KNOWLEDGE_DIR / "quality" / "knowledge_quality_report.json"
        with open(quality_file, 'w', encoding='utf-8') as f:
            json.dump(quality_report, f, ensure_ascii=False, indent=2)

        print(f"[OK] Total knowledge: {total}")
        print(f"[OK] Completion rate: {success_rate:.1f}%")
        print(f"[OK] Quality score: {quality_report['quality_score']}")

        return quality_report

    def search_knowledge(self, keyword: str) -> List[Dict[str, Any]]:
        """智能知识检索"""
        print(f"\n=== 知识检索: {keyword} ===")

        distilled_file = KNOWLEDGE_DIR / "distilled" / "evolution_knowledge_distilled.json"

        if not distilled_file.exists():
            return [{"error": "请先执行知识蒸馏"}]

        with open(distilled_file, 'r', encoding='utf-8') as f:
            knowledge = json.load(f)

        # 简单关键词匹配
        results = []
        keyword_lower = keyword.lower()
        for k in knowledge:
            if keyword_lower in k.get('goal', '').lower() or keyword_lower in k.get('summary', '').lower():
                results.append(k)

        print(f"[OK] Found {len(results)} matching results")

        return results[:10]

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱展示数据"""
        quality_file = KNOWLEDGE_DIR / "quality" / "knowledge_quality_report.json"
        distilled_file = KNOWLEDGE_DIR / "distilled" / "evolution_knowledge_distilled.json"

        data = {
            "engine": self.engine_name,
            "version": self.version,
            "status": "active",
            "last_update": datetime.now().isoformat()
        }

        if quality_file.exists():
            with open(quality_file, 'r', encoding='utf-8') as f:
                data["quality"] = json.load(f)

        if distilled_file.exists():
            with open(distilled_file, 'r', encoding='utf-8') as f:
                knowledge = json.load(f)
                data["knowledge_count"] = len(knowledge)
                data["latest_rounds"] = [k["round"] for k in knowledge[:5]]

        return data


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description='跨引擎深度知识蒸馏与智能传承增强引擎')
    parser.add_argument('--distill', action='store_true', help='执行知识蒸馏')
    parser.add_argument('--inherit', type=int, nargs='?', const=-1, help='执行知识传承')
    parser.add_argument('--assess-quality', action='store_true', help='执行知识质量评估')
    parser.add_argument('--search', type=str, help='搜索知识')
    parser.add_argument('--cockpit-data', action='store_true', help='获取驾驶舱数据')

    args = parser.parse_args()

    engine = KnowledgeDistillationInheritanceEngine()

    if args.distill:
        result = engine.distill_knowledge()
        print("\n【知识蒸馏结果】")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.inherit is not None:
        target = args.inherit if args.inherit > 0 else None
        result = engine.inherit_knowledge(target)
        print("\n【知识传承结果】")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.assess_quality:
        result = engine.assess_quality()
        print("\n【质量评估结果】")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.search:
        results = engine.search_knowledge(args.search)
        print("\n【检索结果】")
        print(json.dumps(results, ensure_ascii=False, indent=2))

    elif args.cockpit_data:
        data = engine.get_cockpit_data()
        print("\n【驾驶舱数据】")
        print(json.dumps(data, ensure_ascii=False, indent=2))

    else:
        # 默认执行完整流程
        print("执行完整知识蒸馏与传承流程...\n")

        # 1. 知识蒸馏
        distill_result = engine.distill_knowledge()

        # 2. 知识传承
        inherit_result = engine.inherit_knowledge()

        # 3. 质量评估
        quality_result = engine.assess_quality()

        print("\n" + "="*50)
        print("【完整流程执行完成】")
        print(f"蒸馏知识: {distill_result['distilled_count']} 条")
        print(f"传承知识: {inherit_result['inherited_count']} 条")
        print(f"质量得分: {quality_result['quality_score']}")


if __name__ == "__main__":
    main()