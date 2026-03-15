#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环跨引擎协同学习与知识共享深度增强引擎
(Cross-Engine Collaborative Learning & Knowledge Sharing Engine)

在 round 487 完成的自我进化效能分析引擎基础上，
进一步构建跨引擎协同学习能力。

让系统能够自动收集各引擎的执行经验、跨引擎共享学习成果、
智能识别可复用模式，形成「各引擎独立学习→跨引擎知识共享→整体协同进化」的完整闭环。

实现从「单引擎优化」到「多引擎协同进化」的范式升级，
让进化环能够像神经网络一样共享学习成果。

Version: 1.0.0
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from collections import defaultdict
import statistics
import copy
import hashlib

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
STATE_DIR = PROJECT_ROOT / "runtime" / "state"
DATA_DIR = PROJECT_ROOT / "runtime" / "data"
LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"

# 添加 scripts 目录到路径以便导入
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

# 尝试导入相关引擎
try:
    from evolution_self_evolution_effectiveness_analysis_engine import (
        SelfEvolutionEffectivenessAnalysisEngine
    )
    EFFECTIVENESS_ANALYSIS_AVAILABLE = True
except ImportError:
    EFFECTIVENESS_ANALYSIS_AVAILABLE = False


class CrossEngineCollaborativeLearningEngine:
    """跨引擎协同学习与知识共享引擎核心类"""

    def __init__(self):
        self.version = "1.0.0"
        self.name = "Cross-Engine Collaborative Learning Engine"
        self.runtime_dir = PROJECT_ROOT / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.data_dir = self.runtime_dir / "data"
        self.scripts_dir = PROJECT_ROOT / "scripts"

        # 数据文件路径
        self.config_file = self.data_dir / "cross_engine_collaborative_config.json"
        self.experience_db_file = self.data_dir / "cross_engine_experience_db.json"
        self.knowledge_sharing_file = self.data_dir / "cross_engine_knowledge_sharing.json"
        self.patterns_db_file = self.data_dir / "cross_engine_patterns_db.json"
        self.learning_metrics_file = self.data_dir / "cross_engine_learning_metrics.json"

        self._ensure_directories()
        self._initialize_data()
        self._discover_available_engines()

    def _ensure_directories(self):
        """确保必要的目录存在"""
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _initialize_data(self):
        """初始化数据文件"""
        # 配置文件
        if not self.config_file.exists():
            default_config = {
                "learning_enabled": True,
                "collection": {
                    "auto_collect": True,
                    "collection_interval_hours": 12,
                    "experience_retention_days": 90
                },
                "sharing": {
                    "auto_share": True,
                    "share_threshold": 0.7,  # 置信度阈值
                    "pattern_similarity_threshold": 0.6
                },
                "collaborative": {
                    "enabled": True,
                    "max_patterns_per_engine": 50,
                    "cross_engine_learning_weight": 0.3
                }
            }
            self._write_json(self.config_file, default_config)

        # 经验数据库
        if not self.experience_db_file.exists():
            self._write_json(self.experience_db_file, {"engines": {}, "last_updated": None})

        # 知识共享数据库
        if not self.knowledge_sharing_file.exists():
            self._write_json(self.knowledge_sharing_file, {"shared_knowledge": [], "sharing_history": []})

        # 模式数据库
        if not self.patterns_db_file.exists():
            self._write_json(self.patterns_db_file, {"patterns": [], "pattern_sources": {}})

        # 学习指标数据库
        if not self.learning_metrics_file.exists():
            self._write_json(self.learning_metrics_file, {"metrics": {}, "learning_effectiveness": {}})

    def _discover_available_engines(self):
        """发现可用的进化引擎"""
        self.available_engines = {}

        # 扫描 scripts 目录下的 evolution_*.py 文件
        if self.scripts_dir.exists():
            for py_file in self.scripts_dir.glob("evolution_*.py"):
                engine_name = py_file.stem
                # 提取引擎名称（去除 evolution_ 前缀并转换为可读格式）
                display_name = engine_name.replace("evolution_", "").replace("_", " ").title()
                self.available_engines[engine_name] = {
                    "file": str(py_file),
                    "display_name": display_name,
                    "discovered_at": datetime.now().isoformat()
                }

    def _write_json(self, file_path: Path, data: Any):
        """安全写入 JSON 文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _read_json(self, file_path: Path) -> Any:
        """安全读取 JSON 文件"""
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                # 文件损坏或编码问题，返回 None
                return None
        return None

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        config = self._read_json(self.config_file)
        experience_db = self._read_json(self.experience_db_file)
        patterns_db = self._read_json(self.patterns_db_file)
        metrics_db = self._read_json(self.learning_metrics_file)

        return {
            "name": self.name,
            "version": self.version,
            "status": "active",
            "config": config,
            "statistics": {
                "available_engines": len(self.available_engines),
                "engines_with_experience": len(experience_db.get("engines", {})),
                "total_patterns": len(patterns_db.get("patterns", [])),
                "shared_knowledge_items": len(self._read_json(self.knowledge_sharing_file).get("shared_knowledge", [])),
                "learning_metrics_tracked": len(metrics_db.get("metrics", {}))
            },
            "discovered_engines": list(self.available_engines.keys())[:20],  # 只显示前20个
            "timestamp": datetime.now().isoformat()
        }

    def collect_engine_experiences(self, engine_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        收集指定引擎的执行经验

        Args:
            engine_names: 要收集经验的引擎名称列表，None 表示所有引擎

        Returns:
            收集结果
        """
        if engine_names is None:
            engine_names = list(self.available_engines.keys())

        experience_db = self._read_json(self.experience_db_file)
        if experience_db is None:
            experience_db = {"engines": {}}

        collected_count = 0
        for engine_name in engine_names:
            if engine_name not in self.available_engines:
                continue

            # 从各引擎数据文件中收集经验
            engine_experiences = self._collect_from_engine_data(engine_name)

            if engine_name not in experience_db["engines"]:
                experience_db["engines"][engine_name] = {"experiences": [], "last_collected": None}

            experience_db["engines"][engine_name]["experiences"].extend(engine_experiences)
            experience_db["engines"][engine_name]["last_collected"] = datetime.now().isoformat()

            collected_count += len(engine_experiences)

        experience_db["last_updated"] = datetime.now().isoformat()
        self._write_json(self.experience_db_file, experience_db)

        return {
            "collected_engines": len(engine_names),
            "total_experiences": collected_count,
            "timestamp": datetime.now().isoformat()
        }

    def _collect_from_engine_data(self, engine_name: str) -> List[Dict[str, Any]]:
        """
        从引擎相关数据文件中收集执行经验
        """
        experiences = []

        # 尝试从引擎特定的数据文件中收集
        engine_data_patterns = [
            self.data_dir / f"{engine_name}_data.json",
            self.data_dir / f"{engine_name}_results.json",
            self.data_dir / f"{engine_name}_history.json"
        ]

        for data_file in engine_data_patterns:
            if data_file.exists():
                data = self._read_json(data_file)
                if data:
                    # 提取可学习的经验
                    extracted = self._extract_learning_experiences(engine_name, data)
                    experiences.extend(extracted)

        # 如果没有特定数据，尝试从通用数据文件中收集
        # 扫描已完成进化记录
        state_files = list(self.state_dir.glob("evolution_completed_*.json"))
        for state_file in state_files[-50:]:  # 最近50个
            state_data = self._read_json(state_file)
            if state_data and "做了什么" in state_data:
                # 检查是否与该引擎相关
                content = str(state_data)
                if engine_name.replace("evolution_", "") in content.lower():
                    experiences.append({
                        "source": state_file.stem,
                        "timestamp": state_data.get("updated_at", datetime.now().isoformat()),
                        "type": "evolution_result",
                        "data": state_data
                    })

        return experiences

    def _extract_learning_experiences(self, engine_name: str, data: Any) -> List[Dict[str, Any]]:
        """从数据中提取可学习的经验"""
        experiences = []

        if isinstance(data, dict):
            # 提取成功模式
            if "success" in data or "completed" in data:
                experiences.append({
                    "engine": engine_name,
                    "type": "success_pattern",
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                })

            # 提取优化建议
            if "optimization" in data or "suggestions" in data:
                experiences.append({
                    "engine": engine_name,
                    "type": "optimization",
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                })

            # 提取效能指标
            if "metrics" in data or "performance" in data:
                experiences.append({
                    "engine": engine_name,
                    "type": "metrics",
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                })

        return experiences

    def identify_reusable_patterns(self, min_confidence: float = 0.6) -> Dict[str, Any]:
        """
        识别可跨引擎复用的模式

        Args:
            min_confidence: 最小置信度阈值

        Returns:
            识别结果
        """
        experience_db = self._read_json(self.experience_db_file)
        patterns_db = self._read_json(self.patterns_db_file)

        if not experience_db or not experience_db.get("engines"):
            return {"patterns_found": 0, "message": "No experience data available"}

        identified_patterns = []

        # 分析各引擎的经验，识别可复用模式
        engines = experience_db.get("engines", {})

        for engine_name, engine_data in engines.items():
            experiences = engine_data.get("experiences", [])

            # 提取常见模式
            pattern_types = defaultdict(list)
            for exp in experiences:
                exp_type = exp.get("type", "unknown")
                pattern_types[exp_type].append(exp)

            # 对每种模式类型识别可复用特征
            for pattern_type, pattern_experiences in pattern_types.items():
                if len(pattern_experiences) >= 2:  # 至少2次出现才识别为模式
                    pattern = {
                        "id": self._generate_pattern_id(engine_name, pattern_type),
                        "engine": engine_name,
                        "type": pattern_type,
                        "occurrences": len(pattern_experiences),
                        "confidence": min(0.9, len(pattern_experiences) / 10.0 + 0.3),
                        "first_seen": pattern_experiences[0].get("timestamp"),
                        "last_seen": pattern_experiences[-1].get("timestamp"),
                        "sample_data": pattern_experiences[0].get("data", {})
                    }

                    if pattern["confidence"] >= min_confidence:
                        identified_patterns.append(pattern)

        # 更新模式数据库
        patterns_db["patterns"] = identified_patterns
        patterns_db["last_updated"] = datetime.now().isoformat()

        # 更新模式来源映射
        pattern_sources = {}
        for pattern in identified_patterns:
            engine = pattern["engine"]
            if engine not in pattern_sources:
                pattern_sources[engine] = []
            pattern_sources[engine].append(pattern["id"])

        patterns_db["pattern_sources"] = pattern_sources

        self._write_json(self.patterns_db_file, patterns_db)

        return {
            "patterns_found": len(identified_patterns),
            "patterns_by_engine": {k: len(v) for k, v in pattern_sources.items()},
            "min_confidence": min_confidence,
            "timestamp": datetime.now().isoformat()
        }

    def _generate_pattern_id(self, engine_name: str, pattern_type: str) -> str:
        """生成模式唯一 ID"""
        content = f"{engine_name}:{pattern_type}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def share_knowledge_to_engines(self, target_engines: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        将识别的模式共享给目标引擎

        Args:
            target_engines: 目标引擎列表，None 表示所有引擎

        Returns:
            共享结果
        """
        patterns_db = self._read_json(self.patterns_db_file)
        knowledge_sharing = self._read_json(self.knowledge_sharing_file)

        if not patterns_db or not patterns_db.get("patterns"):
            return {"shared_items": 0, "message": "No patterns to share"}

        config = self._read_json(self.config_file)
        share_threshold = config.get("sharing", {}).get("share_threshold", 0.7)

        shared_knowledge = []
        patterns = patterns_db.get("patterns", [])

        # 按置信度筛选可共享的模式
        high_confidence_patterns = [p for p in patterns if p.get("confidence", 0) >= share_threshold]

        if target_engines is None:
            # 共享给所有引擎
            target_engines = list(self.available_engines.keys())

        for pattern in high_confidence_patterns:
            for target_engine in target_engines:
                if target_engine != pattern["engine"]:  # 不共享给自身
                    share_record = {
                        "pattern_id": pattern["id"],
                        "from_engine": pattern["engine"],
                        "to_engine": target_engine,
                        "pattern_type": pattern["type"],
                        "confidence": pattern["confidence"],
                        "shared_at": datetime.now().isoformat()
                    }
                    shared_knowledge.append(share_record)

        # 更新共享历史
        knowledge_sharing["shared_knowledge"].extend(shared_knowledge)
        knowledge_sharing["sharing_history"].append({
            "timestamp": datetime.now().isoformat(),
            "patterns_shared": len(shared_knowledge),
            "target_engines": target_engines
        })

        # 限制历史记录数量
        if len(knowledge_sharing["sharing_history"]) > 100:
            knowledge_sharing["sharing_history"] = knowledge_sharing["sharing_history"][-100:]

        self._write_json(self.knowledge_sharing_file, knowledge_sharing)

        return {
            "shared_items": len(shared_knowledge),
            "target_engines": len(target_engines),
            "patterns_analyzed": len(patterns),
            "share_threshold": share_threshold,
            "timestamp": datetime.now().isoformat()
        }

    def get_collaborative_learning_effectiveness(self) -> Dict[str, Any]:
        """
        获取协同学习效果评估

        Returns:
            效果评估结果
        """
        metrics_db = self._read_json(self.learning_metrics_file)
        patterns_db = self._read_json(self.patterns_db_file)
        knowledge_sharing = self._read_json(self.knowledge_sharing_file)

        # 计算各项指标
        total_patterns = len(patterns_db.get("patterns", []))
        shared_knowledge = len(knowledge_sharing.get("shared_knowledge", []))
        sharing_events = len(knowledge_sharing.get("sharing_history", []))

        # 识别最有价值的模式
        all_patterns = patterns_db.get("patterns", [])
        top_patterns = sorted(all_patterns, key=lambda x: x.get("confidence", 0), reverse=True)[:10]

        return {
            "summary": {
                "total_patterns_identified": total_patterns,
                "knowledge_items_shared": shared_knowledge,
                "sharing_events": sharing_events,
                "available_engines": len(self.available_engines)
            },
            "top_patterns": [
                {
                    "id": p["id"],
                    "engine": p["engine"],
                    "type": p["type"],
                    "confidence": p["confidence"],
                    "occurrences": p["occurrences"]
                }
                for p in top_patterns
            ],
            "learning_effectiveness": {
                "pattern_reuse_rate": shared_knowledge / max(1, total_patterns),
                "cross_engine_collaboration_score": min(1.0, shared_knowledge / 50.0),
                "knowledge_accumulation_rate": total_patterns / max(1, sharing_events) if sharing_events > 0 else 0
            },
            "timestamp": datetime.now().isoformat()
        }

    def get_cockpit_data(self) -> Dict[str, Any]:
        """
        获取进化驾驶舱需要的数据

        Returns:
            驾驶舱数据
        """
        status = self.get_status()
        effectiveness = self.get_collaborative_learning_effectiveness()

        return {
            "engine_name": self.name,
            "version": self.version,
            "status": status,
            "effectiveness": effectiveness,
            "available_engines": list(self.available_engines.keys()),
            "recent_sharing": self._read_json(self.knowledge_sharing_file).get("sharing_history", [])[-5:] if self.knowledge_sharing_file.exists() else [],
            "timestamp": datetime.now().isoformat()
        }


def main():
    """主函数，支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(
        description="跨引擎协同学习与知识共享深度增强引擎"
    )
    parser.add_argument("--status", action="store_true", help="获取引擎状态")
    parser.add_argument("--collect", action="store_true", help="收集引擎执行经验")
    parser.add_argument("--engines", nargs="*", help="指定要收集经验的引擎名称")
    parser.add_argument("--identify-patterns", action="store_true", help="识别可复用模式")
    parser.add_argument("--share", action="store_true", help="共享知识到各引擎")
    parser.add_argument("--targets", nargs="*", help="指定目标引擎")
    parser.add_argument("--effectiveness", action="store_true", help="获取协同学习效果")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")

    args = parser.parse_args()

    engine = CrossEngineCollaborativeLearningEngine()

    if args.status:
        result = engine.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.collect:
        result = engine.collect_engine_experiences(args.engines)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.identify_patterns:
        result = engine.identify_reusable_patterns()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.share:
        result = engine.share_knowledge_to_engines(args.targets)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.effectiveness:
        result = engine.get_collaborative_learning_effectiveness()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.cockpit_data:
        result = engine.get_cockpit_data()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 默认显示状态
    result = engine.get_status()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()