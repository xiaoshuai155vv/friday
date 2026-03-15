#!/usr/bin/env python3
"""
智能全场景进化环元进化跨引擎知识自动蒸馏与深度传承引擎
Evolution Meta Cross-Engine Knowledge Distillation and Inheritance Engine

version: 1.0.0
description: 让系统能够自动从600+轮进化历史和100+进化引擎中提取可复用的元知识，
形成结构化的知识传承体系，支持新引擎快速学习和复用历史经验。

功能：
1. 进化引擎元知识自动提取 - 从引擎代码、配置、执行结果中提取
2. 跨引擎知识关联分析 - 发现引擎间的知识关联与依赖
3. 结构化知识图谱构建 - 形成可查询的知识网络
4. 知识传承能力 - 支持新引擎快速学习历史经验
5. 驾驶舱数据接口

依赖：
- round 489: 跨引擎深度知识蒸馏与智能传承增强引擎
- round 599: 元进化智慧自动提取与战略规划引擎
- round 625: 元进化记忆深度整合与跨轮次智慧涌现引擎
- round 633: 元进化知识图谱动态推理与主动创新发现引擎
"""

import os
import sys
import json
import time
import logging
import ast
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from collections import defaultdict

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
class EngineMetaKnowledge:
    """引擎元知识"""
    engine_name: str
    engine_file: str
    version: str
    core_capabilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    execution_patterns: List[str] = field(default_factory=list)
    success_patterns: List[str] = field(default_factory=list)
    failure_patterns: List[str] = field(default_factory=list)
    knowledge_tags: List[str] = field(default_factory=list)
    extracted_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "engine_name": self.engine_name,
            "engine_file": self.engine_file,
            "version": self.version,
            "core_capabilities": self.core_capabilities,
            "dependencies": self.dependencies,
            "execution_patterns": self.execution_patterns,
            "success_patterns": self.success_patterns,
            "failure_patterns": self.failure_patterns,
            "knowledge_tags": self.knowledge_tags,
            "extracted_at": self.extracted_at
        }


@dataclass
class Knowledge传承Unit:
    """知识传承单元"""
    knowledge_id: str
    knowledge_type: str  # pattern, capability, insight, lesson
    content: str
    source_engines: List[str] = field(default_factory=list)
    applicability: str = ""  # 适用场景
    reuse_count: int = 0
    quality_score: float = 0.0
    created_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "knowledge_id": self.knowledge_id,
            "knowledge_type": self.knowledge_type,
            "content": self.content,
            "source_engines": self.source_engines,
            "applicability": self.applicability,
            "reuse_count": self.reuse_count,
            "quality_score": self.quality_score,
            "created_at": self.created_at
        }


class CrossEngineKnowledgeDistillationInheritanceEngine:
    """元进化跨引擎知识自动蒸馏与深度传承引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.engine_name = "元进化跨引擎知识自动蒸馏与深度传承引擎"

        # 确保目录存在
        KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
        (KNOWLEDGE_DIR / "distillation").mkdir(exist_ok=True)
        (KNOWLEDGE_DIR / "inheritance").mkdir(exist_ok=True)
        (KNOWLEDGE_DIR / "knowledge_graph").mkdir(exist_ok=True)

        # 知识存储
        self.knowledge_file = KNOWLEDGE_DIR / "distillation" / "cross_engine_knowledge.json"
        self.knowledge_graph_file = KNOWLEDGE_DIR / "knowledge_graph" / "engine_knowledge_graph.json"
        self.inheritance_file = KNOWLEDGE_DIR / "inheritance" / "knowledge_inheritance.json"

        self.engine_knowledge: Dict[str, EngineMetaKnowledge] = {}
        self.knowledge_units: Dict[str, Knowledge传承Unit] = {}
        self.knowledge_graph: Dict[str, List[str]] = {}  # 引擎 -> 关联引擎

        self._load_knowledge()

        print(f"[{self.engine_name} v{self.version}] 初始化完成")

    def _load_knowledge(self):
        """加载已有知识"""
        # 加载引擎知识
        if self.knowledge_file.exists():
            try:
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for ek_data in data.get("engine_knowledge", []):
                        ek = EngineMetaKnowledge(**ek_data)
                        self.engine_knowledge[ek.engine_name] = ek
            except Exception as e:
                logger.warning(f"加载引擎知识失败: {e}")

        # 加载知识单元
        if self.knowledge_file.exists():
            try:
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for ku_data in data.get("knowledge_units", []):
                        ku = Knowledge传承Unit(**ku_data)
                        self.knowledge_units[ku.knowledge_id] = ku
            except Exception as e:
                logger.warning(f"加载知识单元失败: {e}")

        # 加载知识图谱
        if self.knowledge_graph_file.exists():
            try:
                with open(self.knowledge_graph_file, 'r', encoding='utf-8') as f:
                    self.knowledge_graph = json.load(f)
            except Exception as e:
                logger.warning(f"加载知识图谱失败: {e}")

    def _save_knowledge(self):
        """保存知识"""
        data = {
            "engine_knowledge": [ek.to_dict() for ek in self.engine_knowledge.values()],
            "knowledge_units": [ku.to_dict() for ku in self.knowledge_units.values()],
            "last_update": datetime.now().isoformat()
        }
        try:
            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存知识失败: {e}")

        # 保存知识图谱
        try:
            with open(self.knowledge_graph_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_graph, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存知识图谱失败: {e}")

    def extract_engine_knowledge(self, engine_file: Path) -> Optional[EngineMetaKnowledge]:
        """从引擎文件提取元知识"""
        try:
            with open(engine_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取引擎名称和版本
            engine_name = engine_file.stem
            version = "1.0.0"

            # 从 docstring 提取版本和描述
            version_match = re.search(r'version:\s*([0-9.]+)', content)
            if version_match:
                version = version_match.group(1)

            # 提取核心能力 (从功能列表)
            capabilities = []
            func_match = re.search(r'功能[：:]\s*\n((?:\d+\..+\n?)+)', content)
            if func_match:
                for line in func_match.group(1).strip().split('\n'):
                    cap = re.sub(r'^\d+[\.\)]\s*', '', line).strip()
                    if cap:
                        capabilities.append(cap)

            # 提取依赖
            dependencies = []
            dep_match = re.search(r'依赖[：:]\s*\n((?:-\s*.+\n?)+)', content)
            if dep_match:
                for line in dep_match.group(1).strip().split('\n'):
                    dep = re.sub(r'^-\s*', '', line).strip()
                    if dep:
                        dependencies.append(dep)

            # 提取知识标签
            tags = []
            tag_match = re.search(r'功能[：:](.+?)(?:\n\n|\n依赖)', content, re.DOTALL)
            if tag_match:
                text = tag_match.group(1)
                # 提取关键词作为标签
                keywords = re.findall(r'[\u4e00-\u9fa5]{2,6}', text)
                tags = list(set(keywords))[:10]

            # 构建元知识
            meta_knowledge = EngineMetaKnowledge(
                engine_name=engine_name,
                engine_file=str(engine_file),
                version=version,
                core_capabilities=capabilities,
                dependencies=dependencies,
                execution_patterns=[],
                success_patterns=[],
                failure_patterns=[],
                knowledge_tags=tags,
                extracted_at=datetime.now().isoformat()
            )

            return meta_knowledge

        except Exception as e:
            logger.warning(f"提取引擎知识失败 {engine_file}: {e}")
            return None

    def scan_all_engines(self) -> List[EngineMetaKnowledge]:
        """扫描所有进化引擎并提取知识"""
        print("\n=== 扫描所有进化引擎 ===")

        # 扫描 scripts 目录下的进化引擎
        script_files = list(SCRIPT_DIR.glob("evolution_*.py"))

        extracted = []
        for sf in script_files:
            # 跳过非引擎文件
            if any(x in sf.name for x in ["_test", "helper", "tool", "util"]):
                continue

            meta = self.extract_engine_knowledge(sf)
            if meta:
                self.engine_knowledge[meta.engine_name] = meta
                extracted.append(meta)

        print(f"已扫描 {len(extracted)} 个进化引擎")

        # 构建知识图谱
        self._build_knowledge_graph()

        # 蒸馏知识单元
        self._distill_knowledge_units()

        # 保存知识
        self._save_knowledge()

        return extracted

    def _build_knowledge_graph(self):
        """构建知识图谱"""
        print("\n=== 构建知识图谱 ===")

        # 基于依赖关系构建图谱
        for eng_name, eng_meta in self.engine_knowledge.items():
            neighbors = []

            # 添加依赖的引擎
            for dep in eng_meta.dependencies:
                for other_eng in self.engine_knowledge.values():
                    if dep.lower() in other_eng.engine_name.lower():
                        neighbors.append(other_eng.engine_name)

            # 添加基于知识标签的关联
            for tag in eng_meta.knowledge_tags[:3]:  # 取前3个标签
                for other_eng in self.engine_knowledge.values():
                    if other_eng.engine_name != eng_name:
                        if tag in other_eng.knowledge_tags:
                            if other_eng.engine_name not in neighbors:
                                neighbors.append(other_eng.engine_name)

            self.knowledge_graph[eng_name] = list(set(neighbors))

        print(f"知识图谱包含 {len(self.knowledge_graph)} 个节点")

    def _distill_knowledge_units(self):
        """蒸馏知识单元"""
        print("\n=== 蒸馏知识单元 ===")

        # 从引擎能力中提取可复用的知识模式
        knowledge_id_counter = 1

        for eng_name, eng_meta in self.engine_knowledge.items():
            # 从核心能力中提取知识
            for cap in eng_meta.core_capabilities[:3]:  # 取前3个能力
                if len(cap) > 5:  # 过滤太短的
                    ku_id = f"KU{knowledge_id_counter:04d}"
                    knowledge_id_counter += 1

                    # 检查是否已存在相似知识
                    existing = False
                    for existing_ku in self.knowledge_units.values():
                        if existing_ku.content == cap:
                            existing = True
                            break

                    if not existing:
                        ku = Knowledge传承Unit(
                            knowledge_id=ku_id,
                            knowledge_type="capability",
                            content=cap,
                            source_engines=[eng_name],
                            applicability=eng_name,
                            reuse_count=0,
                            quality_score=0.8,
                            created_at=datetime.now().isoformat()
                        )
                        self.knowledge_units[ku_id] = ku

        print(f"已蒸馏 {len(self.knowledge_units)} 个知识单元")

    def get_knowledge_for_new_engine(self, engine_context: str) -> List[Knowledge传承Unit]:
        """为新引擎获取相关知识"""
        print(f"\n=== 为新引擎获取相关知识: {engine_context} ===")

        # 基于关键词匹配找到相关知识
        context_keywords = re.findall(r'[\u4e00-\u9fa5]{2,}', engine_context)

        relevant_knowledge = []
        for ku in self.knowledge_units.values():
            # 检查知识内容是否包含上下文关键词
            for kw in context_keywords:
                if kw in ku.content or kw in ku.applicability:
                    relevant_knowledge.append(ku)
                    break

            # 检查知识标签
            for eng_name, eng_meta in self.engine_knowledge.items():
                if eng_name in engine_context or engine_context in eng_name:
                    if ku.source_engines and ku.source_engines[0] == eng_name:
                        relevant_knowledge.append(ku)

        # 去重并按质量排序
        seen = set()
        unique_knowledge = []
        for ku in relevant_knowledge:
            if ku.knowledge_id not in seen:
                seen.add(ku.knowledge_id)
                unique_knowledge.append(ku)

        unique_knowledge.sort(key=lambda x: x.quality_score, reverse=True)

        # 增加重用计数
        for ku in unique_knowledge:
            ku.reuse_count += 1

        if unique_knowledge:
            self._save_knowledge()

        return unique_knowledge[:10]  # 返回前10个最相关的

    def get_engine_relationships(self, engine_name: str) -> List[str]:
        """获取引擎的关联引擎"""
        return self.knowledge_graph.get(engine_name, [])

    def get_knowledge_statistics(self) -> Dict[str, Any]:
        """获取知识统计"""
        return {
            "total_engines": len(self.engine_knowledge),
            "total_knowledge_units": len(self.knowledge_units),
            "knowledge_graph_nodes": len(self.knowledge_graph),
            "knowledge_types": self._count_knowledge_types(),
            "top_source_engines": self._get_top_source_engines(),
            "last_update": datetime.now().isoformat()
        }

    def _count_knowledge_types(self) -> Dict[str, int]:
        """统计知识类型"""
        counts = defaultdict(int)
        for ku in self.knowledge_units.values():
            counts[ku.knowledge_type] += 1
        return dict(counts)

    def _get_top_source_engines(self) -> List[Tuple[str, int]]:
        """获取知识最多的引擎"""
        counts = defaultdict(int)
        for ku in self.knowledge_units.values():
            for eng in ku.source_engines:
                counts[eng] += 1
        return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]

    def run_distillation_cycle(self) -> Dict[str, Any]:
        """运行完整的蒸馏循环"""
        print("\n" + "="*60)
        print(f"启动 {self.engine_name}")
        print("="*60)

        # 1. 扫描所有引擎
        engines = self.scan_all_engines()

        # 2. 获取统计
        stats = self.get_knowledge_statistics()

        print("\n=== 知识统计 ===")
        print(f"总引擎数: {stats['total_engines']}")
        print(f"总知识单元: {stats['total_knowledge_units']}")
        print(f"知识图谱节点: {stats['knowledge_graph_nodes']}")
        print(f"知识类型分布: {stats['knowledge_types']}")

        return {
            "status": "success",
            "engines_scanned": len(engines),
            "knowledge_units": stats['total_knowledge_units'],
            "statistics": stats
        }

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱数据"""
        stats = self.get_knowledge_statistics()

        return {
            "engine_name": self.engine_name,
            "version": self.version,
            "statistics": stats,
            "recent_knowledge_units": [
                ku.to_dict() for ku in sorted(
                    self.knowledge_units.values(),
                    key=lambda x: x.created_at,
                    reverse=True
                )[:5]
            ]
        }


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description='元进化跨引擎知识自动蒸馏与深度传承引擎')
    parser.add_argument('--version', action='store_true', help='显示版本信息')
    parser.add_argument('--status', action='store_true', help='显示状态')
    parser.add_argument('--scan', action='store_true', help='扫描并提取所有引擎知识')
    parser.add_argument('--get-knowledge', type=str, help='为指定引擎获取相关知识')
    parser.add_argument('--relationships', type=str, help='获取引擎的关联引擎')
    parser.add_argument('--cockpit-data', action='store_true', help='获取驾驶舱数据')

    args = parser.parse_args()

    engine = CrossEngineKnowledgeDistillationInheritanceEngine()

    if args.version:
        print(f"{engine.engine_name} v{engine.version}")
        return

    if args.status:
        stats = engine.get_knowledge_statistics()
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        return

    if args.scan:
        result = engine.run_distillation_cycle()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.get_knowledge:
        knowledge = engine.get_knowledge_for_new_engine(args.get_knowledge)
        print(f"为 '{args.get_knowledge}' 找到 {len(knowledge)} 个相关知识单元:")
        for ku in knowledge:
            print(f"  - [{ku.knowledge_id}] {ku.content[:50]}... (质量: {ku.quality_score})")
        return

    if args.relationships:
        rels = engine.get_engine_relationships(args.relationships)
        print(f"'{args.relationships}' 的关联引擎: {rels if rels else '无'}")
        return

    if args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    # 默认显示帮助
    parser.print_help()


if __name__ == "__main__":
    main()