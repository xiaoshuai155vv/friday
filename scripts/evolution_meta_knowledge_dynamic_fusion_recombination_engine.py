#!/usr/bin/env python3
"""
智能全场景进化环元进化知识动态融合与自适应重组引擎
Evolution Meta Knowledge Dynamic Fusion and Adaptive Recombination Engine

version: 1.0.0
description: 在 round 669 完成的跨引擎知识自动蒸馏与深度传承引擎基础上，
构建让系统能够动态融合多源知识、根据任务需求自适应重组知识结构的能力，
形成知识从「静态存储」到「动态活用」的升级。

功能：
1. 多源知识动态融合能力（整合知识图谱、历史进化记忆、引擎知识库）
2. 任务感知知识检索（根据当前任务上下文智能检索相关知识）
3. 知识自适应重组（根据任务需求动态组合知识单元）
4. 知识融合效果评估与反馈
5. 驾驶舱数据接口

依赖：
- round 669: 元进化跨引擎知识自动蒸馏与深度传承引擎
- round 633: 元进化知识图谱动态推理与主动创新发现引擎
- round 625: 元进化记忆深度整合与跨轮次智慧涌现引擎
"""

import os
import sys
import json
import time
import logging
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Set
from pathlib import Path
from dataclasses import dataclass, field
from collections import defaultdict
import re

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 路径配置
SCRIPT_DIR = Path(__file__).parent
RUNTIME_DIR = SCRIPT_DIR.parent / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"
KNOWLEDGE_DIR = RUNTIME_DIR / "knowledge"


@dataclass
class KnowledgeSource:
    """知识源"""
    source_name: str  # knowledge_graph, distillation, memory, engine
    source_type: str  # 知识类型
    knowledge_items: List[Dict[str, Any]] = field(default_factory=list)
    relevance_weight: float = 1.0  # 相关性权重
    last_updated: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_name": self.source_name,
            "source_type": self.source_type,
            "knowledge_count": len(self.knowledge_items),
            "relevance_weight": self.relevance_weight,
            "last_updated": self.last_updated
        }


@dataclass
class TaskContext:
    """任务上下文"""
    task_description: str
    task_type: str  # optimization, diagnosis, planning, execution, etc.
    related_engines: List[str] = field(default_factory=list)
    required_capabilities: List[str] = field(default_factory=list)
    priority: str = "normal"  # high, normal, low

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_description": self.task_description,
            "task_type": self.task_type,
            "related_engines": self.related_engines,
            "required_capabilities": self.required_capabilities,
            "priority": self.priority
        }


@dataclass
class FusedKnowledgeUnit:
    """融合知识单元"""
    unit_id: str
    content: str
    source_knowledge: List[str] = field(default_factory=list)  # 源知识ID列表
    fusion_score: float = 0.0  # 融合得分
    applicability: str = ""  # 适用场景
    confidence: float = 0.0  # 置信度
    created_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "unit_id": self.unit_id,
            "content": self.content,
            "source_knowledge": self.source_knowledge,
            "fusion_score": self.fusion_score,
            "applicability": self.applicability,
            "confidence": self.confidence,
            "created_at": self.created_at
        }


class KnowledgeDynamicFusionRecombinationEngine:
    """元进化知识动态融合与自适应重组引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.engine_name = "元进化知识动态融合与自适应重组引擎"

        # 确保目录存在
        KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
        (KNOWLEDGE_DIR / "fusion").mkdir(exist_ok=True)
        (KNOWLEDGE_DIR / "recombination").mkdir(exist_ok=True)

        # 知识存储
        self.fusion_cache_file = KNOWLEDGE_DIR / "fusion" / "fusion_cache.json"
        self.recombination_file = KNOWLEDGE_DIR / "recombination" / "knowledge_recombination.json"
        self.evaluation_file = KNOWLEDGE_DIR / "fusion" / "fusion_evaluation.json"

        # 知识缓存
        self.knowledge_sources: Dict[str, KnowledgeSource] = {}
        self.fused_knowledge: Dict[str, FusedKnowledgeUnit] = {}
        self.task_history: List[Dict[str, Any]] = []

        self._load_knowledge()

        print(f"[{self.engine_name} v{self.version}] 初始化完成")

    def _load_knowledge(self):
        """加载已有知识"""
        # 加载融合缓存
        if self.fusion_cache_file.exists():
            try:
                with open(self.fusion_cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for unit_data in data.get("fused_knowledge", []):
                        unit = FusedKnowledgeUnit(**unit_data)
                        self.fused_knowledge[unit.unit_id] = unit
            except Exception as e:
                logger.warning(f"加载融合知识失败: {e}")

        # 加载知识源
        self._load_knowledge_sources()

        # 加载任务历史
        if self.recombination_file.exists():
            try:
                with open(self.recombination_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.task_history = data.get("task_history", [])
            except Exception as e:
                logger.warning(f"加载任务历史失败: {e}")

    def _load_knowledge_sources(self):
        """加载多源知识"""
        # 1. 从知识图谱加载
        kg_file = KNOWLEDGE_DIR / "knowledge_graph" / "engine_knowledge_graph.json"
        if kg_file.exists():
            try:
                with open(kg_file, 'r', encoding='utf-8') as f:
                    kg_data = json.load(f)
                    self.knowledge_sources["knowledge_graph"] = KnowledgeSource(
                        source_name="knowledge_graph",
                        source_type="知识图谱",
                        knowledge_items=kg_data.get("nodes", []),
                        relevance_weight=0.9,
                        last_updated=kg_data.get("updated_at", "")
                    )
            except Exception as e:
                logger.warning(f"加载知识图谱失败: {e}")

        # 2. 从知识蒸馏加载
        dist_file = KNOWLEDGE_DIR / "distillation" / "cross_engine_knowledge.json"
        if dist_file.exists():
            try:
                with open(dist_file, 'r', encoding='utf-8') as f:
                    dist_data = json.load(f)
                    self.knowledge_sources["distillation"] = KnowledgeSource(
                        source_name="distillation",
                        source_type="知识蒸馏",
                        knowledge_items=dist_data.get("knowledge_units", []),
                        relevance_weight=0.85,
                        last_updated=dist_data.get("updated_at", "")
                    )
            except Exception as e:
                logger.warning(f"加载知识蒸馏失败: {e}")

        # 3. 从进化记忆加载
        memory_file = RUNTIME_DIR / "evolution_completed" / "summary.json"
        if memory_file.exists():
            try:
                with open(memory_file, 'r', encoding='utf-8') as f:
                    memory_data = json.load(f)
                    self.knowledge_sources["memory"] = KnowledgeSource(
                        source_name="memory",
                        source_type="进化记忆",
                        knowledge_items=memory_data.get("evolutions", []),
                        relevance_weight=0.7,
                        last_updated=memory_data.get("updated_at", "")
                    )
            except Exception as e:
                logger.warning(f"加载进化记忆失败: {e}")

    def _calculate_relevance(self, knowledge_item: Dict[str, Any], task_context: TaskContext) -> float:
        """计算知识与任务的相关性得分"""
        score = 0.0

        # 任务类型匹配
        task_keywords = task_context.task_description.lower().split()
        item_text = json.dumps(knowledge_item).lower()

        for keyword in task_keywords:
            if keyword in item_text:
                score += 0.1

        # 引擎关联匹配
        for engine in task_context.related_engines:
            if engine.lower() in item_text:
                score += 0.2

        # 能力匹配
        for cap in task_context.required_capabilities:
            if cap.lower() in item_text:
                score += 0.15

        return min(score, 1.0)

    def _fuse_knowledge(self, relevant_items: List[Dict[str, Any]], task_context: TaskContext) -> List[FusedKnowledgeUnit]:
        """融合相关知识"""
        fused_units = []

        # 按相似度分组
        groups = defaultdict(list)
        for item in relevant_items:
            key = item.get("knowledge_type", "general")
            groups[key].append(item)

        # 融合每组知识
        for group_key, items in groups.items():
            if not items:
                continue

            # 生成融合单元ID
            unit_id = hashlib.md5(f"{task_context.task_description}:{group_key}:{len(items)}".encode()).hexdigest()[:12]

            # 融合内容
            contents = [json.dumps(item, ensure_ascii=False) for item in items[:5]]  # 最多融合5条
            fused_content = f"【{group_key}知识融合】\n" + "\n---\n".join(contents[:3])

            # 计算融合得分
            fusion_score = min(len(items) * 0.15, 0.9)

            # 创建融合单元
            unit = FusedKnowledgeUnit(
                unit_id=unit_id,
                content=fused_content,
                source_knowledge=[item.get("knowledge_id", f"src_{i}") for i, item in enumerate(items[:5])],
                fusion_score=fusion_score,
                applicability=task_context.task_type,
                confidence=min(0.5 + fusion_score * 0.5, 0.95),
                created_at=datetime.now().isoformat()
            )
            fused_units.append(unit)

        return fused_units

    def _recombine_knowledge(self, fused_units: List[FusedKnowledgeUnit], task_context: TaskContext) -> List[FusedKnowledgeUnit]:
        """自适应重组知识"""
        recombined = []

        # 根据任务类型和优先级排序
        priority_scores = {"high": 1.0, "normal": 0.7, "low": 0.4}
        priority_score = priority_scores.get(task_context.priority, 0.7)

        # 按融合得分和置信度排序
        sorted_units = sorted(
            fused_units,
            key=lambda x: (x.fusion_score * priority_score + x.confidence * 0.5, x.confidence),
            reverse=True
        )

        # 选择top知识进行重组
        max_units = min(len(sorted_units), 5)
        selected = sorted_units[:max_units]

        # 重组知识单元
        for i, unit in enumerate(selected):
            # 增加重组标记
            recombined_unit = FusedKnowledgeUnit(
                unit_id=f"{unit.unit_id}_r{i}",
                content=f"{unit.content}\n\n【任务适配】{task_context.task_description}",
                source_knowledge=unit.source_knowledge,
                fusion_score=min(unit.fusion_score + 0.1, 1.0),
                applicability=f"{task_context.task_type} -> {unit.applicability}",
                confidence=min(unit.confidence + 0.05, 1.0),
                created_at=datetime.now().isoformat()
            )
            recombined.append(recombined_unit)

        return recombined

    def dynamic_fusion(self, task_context: TaskContext) -> Dict[str, Any]:
        """动态融合多源知识"""
        logger.info(f"开始动态融合，任务: {task_context.task_description}")

        all_relevant = []

        # 从各知识源检索相关知识
        for source_name, source in self.knowledge_sources.items():
            for item in source.knowledge_items:
                relevance = self._calculate_relevance(item, task_context)
                if relevance > 0.1:
                    item_with_relevance = dict(item)
                    item_with_relevance["relevance_score"] = relevance
                    item_with_relevance["source"] = source_name
                    all_relevant.append(item_with_relevance)

        # 按相关性排序
        all_relevant.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

        # 取top相关知识进行融合
        top_knowledge = all_relevant[:20]
        logger.info(f"找到 {len(top_knowledge)} 条相关知识")

        # 融合知识
        fused_units = self._fuse_knowledge(top_knowledge, task_context)

        # 记录到缓存
        for unit in fused_units:
            self.fused_knowledge[unit.unit_id] = unit

        self._save_fusion_cache()

        return {
            "task": task_context.to_dict(),
            "fused_count": len(fused_units),
            "source_count": len(top_knowledge),
            "fused_knowledge": [unit.to_dict() for unit in fused_units]
        }

    def adaptive_recombination(self, task_context: TaskContext) -> Dict[str, Any]:
        """自适应知识重组"""
        logger.info(f"开始自适应重组，任务: {task_context.task_description}")

        # 动态融合
        fusion_result = self.dynamic_fusion(task_context)
        fused_units = [
            FusedKnowledgeUnit(
                unit_id=u["unit_id"],
                content=u["content"],
                source_knowledge=u["source_knowledge"],
                fusion_score=u["fusion_score"],
                applicability=u["applicability"],
                confidence=u["confidence"],
                created_at=u["created_at"]
            )
            for u in fusion_result["fused_knowledge"]
        ]

        # 知识重组
        recombined = self._recombine_knowledge(fused_units, task_context)

        # 记录任务历史
        task_record = {
            "task_description": task_context.task_description,
            "task_type": task_context.task_type,
            "fused_count": len(fused_units),
            "recombined_count": len(recombined),
            "timestamp": datetime.now().isoformat()
        }
        self.task_history.append(task_record)

        # 保存重组结果
        self._save_recombination()

        return {
            "task": task_context.to_dict(),
            "recombined_count": len(recombined),
            "recombined_knowledge": [unit.to_dict() for unit in recombined]
        }

    def evaluate_fusion(self, task_result: Dict[str, Any]) -> Dict[str, Any]:
        """评估知识融合效果"""
        task_desc = task_result.get("task", {}).get("task_description", "")

        # 分析历史数据
        related_tasks = [t for t in self.task_history if task_desc in t.get("task_description", "")]

        # 计算各项指标
        avg_fused = sum(t.get("fused_count", 0) for t in related_tasks) / max(len(related_tasks), 1)
        avg_recombined = sum(t.get("recombined_count", 0) for t in related_tasks) / max(len(related_tasks), 1)

        evaluation = {
            "task_description": task_desc,
            "evaluation_time": datetime.now().isoformat(),
            "metrics": {
                "average_fused_count": round(avg_fused, 2),
                "average_recombined_count": round(avg_recombined, 2),
                "total_tasks": len(related_tasks)
            },
            "recommendation": self._generate_recommendation(avg_fused, avg_recombined)
        }

        # 保存评估结果
        self._save_evaluation(evaluation)

        return evaluation

    def _generate_recommendation(self, avg_fused: float, avg_recombined: float) -> str:
        """生成优化建议"""
        if avg_fused < 5:
            return "建议扩展知识源覆盖范围，增加更多领域的知识"
        elif avg_recombined < 3:
            return "建议优化知识重组算法，提高知识组合的有效性"
        else:
            return "知识融合与重组效果良好，可继续使用当前策略"

    def _save_fusion_cache(self):
        """保存融合缓存"""
        data = {
            "fused_knowledge": [unit.to_dict() for unit in self.fused_knowledge.values()],
            "updated_at": datetime.now().isoformat()
        }
        try:
            with open(self.fusion_cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存融合缓存失败: {e}")

    def _save_recombination(self):
        """保存重组结果"""
        data = {
            "task_history": self.task_history[-100:],  # 保留最近100条
            "updated_at": datetime.now().isoformat()
        }
        try:
            with open(self.recombination_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存重组结果失败: {e}")

    def _save_evaluation(self, evaluation: Dict[str, Any]):
        """保存评估结果"""
        data = {"evaluations": []}
        if self.evaluation_file.exists():
            try:
                with open(self.evaluation_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except:
                pass

        data["evaluations"].append(evaluation)
        data["evaluations"] = data["evaluations"][-50:]  # 保留最近50条
        data["updated_at"] = datetime.now().isoformat()

        try:
            with open(self.evaluation_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存评估结果失败: {e}")

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱数据"""
        return {
            "engine_name": self.engine_name,
            "version": self.version,
            "metrics": {
                "knowledge_sources": len(self.knowledge_sources),
                "fused_knowledge_units": len(self.fused_knowledge),
                "task_history_count": len(self.task_history)
            },
            "sources": [s.to_dict() for s in self.knowledge_sources.values()],
            "timestamp": datetime.now().isoformat()
        }

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "engine_name": self.engine_name,
            "version": self.version,
            "status": "running",
            "knowledge_sources": list(self.knowledge_sources.keys()),
            "fused_knowledge_count": len(self.fused_knowledge),
            "task_history_count": len(self.task_history)
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="元进化知识动态融合与自适应重组引擎")
    parser.add_argument("--version", action="store_true", help="显示版本信息")
    parser.add_argument("--status", action="store_true", help="显示引擎状态")
    parser.add_argument("--fusion", type=str, help="执行动态融合，传入任务描述")
    parser.add_argument("--recombine", type=str, help="执行自适应重组，传入任务描述")
    parser.add_argument("--evaluate", type=str, help="评估融合效果，传入任务描述")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")
    parser.add_argument("--task-type", type=str, default="general", help="任务类型")
    parser.add_argument("--priority", type=str, default="normal", choices=["high", "normal", "low"], help="任务优先级")

    args = parser.parse_args()

    engine = KnowledgeDynamicFusionRecombinationEngine()

    if args.version:
        print(f"{engine.engine_name} v{engine.version}")
        return

    if args.status:
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return

    if args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    if args.fusion:
        task = TaskContext(
            task_description=args.fusion,
            task_type=args.task_type,
            priority=args.priority
        )
        result = engine.dynamic_fusion(task)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.recombine:
        task = TaskContext(
            task_description=args.recombine,
            task_type=args.task_type,
            priority=args.priority
        )
        result = engine.adaptive_recombination(task)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.evaluate:
        # 模拟任务结果用于评估
        task_result = {"task": {"task_description": args.evaluate}}
        result = engine.evaluate_fusion(task_result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 默认显示帮助
    parser.print_help()


if __name__ == "__main__":
    main()