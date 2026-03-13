#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能知识进化引擎
让系统能够自动从执行历史、用户交互中提取新知识，更新知识图谱，
形成知识→执行→新知识的闭环，实现知识的自主进化。
"""

import sys
import os
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from pathlib import Path
import hashlib

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    import knowledge_graph
except ImportError:
    knowledge_graph = None


class KnowledgeEvolutionEngine:
    """智能知识进化引擎"""

    def __init__(self, storage_path="runtime/state/knowledge_evolution.json"):
        """
        初始化智能知识进化引擎

        Args:
            storage_path: 存储进化状态的文件路径
        """
        self.storage_path = storage_path
        self.state = {
            "knowledge_sources": [],  # 知识来源列表
            "extracted_knowledge": [],  # 提取的知识
            "evolution_history": [],    # 进化历史
            "last_evolution": None,      # 上次进化时间
            "total_extractions": 0,      # 总提取次数
            "total_updates": 0,          # 总更新次数
            "conflict_count": 0,         # 冲突数量
            "resolved_conflicts": 0      # 已解决冲突数量
        }

        self.kg = None
        if knowledge_graph:
            try:
                self.kg = knowledge_graph.KnowledgeGraph()
            except Exception as e:
                print(f"警告: 无法初始化知识图谱: {e}")

        self._load_state()

    def _load_state(self):
        """从文件加载状态"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    self.state = json.load(f)
            except Exception as e:
                print(f"加载知识进化状态失败: {e}")

    def _save_state(self):
        """保存状态到文件"""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存知识进化状态失败: {e}")

    def _generate_node_id(self, entity_type: str, entity_name: str) -> str:
        """生成节点唯一ID"""
        hash_input = f"{entity_type}:{entity_name}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]

    def extract_from_execution_logs(self, log_dir: str = "runtime/logs") -> List[Dict]:
        """
        从执行日志中提取新知识

        Args:
            log_dir: 日志目录

        Returns:
            提取的知识列表
        """
        extracted = []
        log_files = []

        if os.path.exists(log_dir):
            for f in os.listdir(log_dir):
                if f.startswith("behavior_") and f.endswith(".log"):
                    log_files.append(os.path.join(log_dir, f))

        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # 提取关键模式
                    patterns = {
                        "engine": r'创建\s+(\S+?Engine)',
                        "capability": r'(\S+?Engine)\s+实现',
                        "intent": r'意图[：:]\s*(\S+)',
                        "tool": r'(window_tool|mouse_tool|keyboard_tool|screenshot_tool|vision)',
                        "action": r'(activate|click|type|scroll|maximize|send_keys)'
                    }

                    for match in re.finditer(patterns["engine"], content):
                        entity = match.group(1)
                        extracted.append({
                            "type": "engine",
                            "entity": entity,
                            "source": log_file,
                            "timestamp": datetime.now().isoformat()
                        })

                    for match in re.finditer(patterns["tool"], content):
                        tool = match.group(1)
                        extracted.append({
                            "type": "capability",
                            "entity": tool,
                            "source": log_file,
                            "timestamp": datetime.now().isoformat()
                        })

            except Exception as e:
                print(f"读取日志文件失败 {log_file}: {e}")

        self.state["extracted_knowledge"].extend(extracted)
        self.state["total_extractions"] += len(extracted)
        self.state["knowledge_sources"].append({
            "source": "execution_logs",
            "extracted_count": len(extracted),
            "timestamp": datetime.now().isoformat()
        })

        return extracted

    def extract_from_recent_logs(self) -> List[Dict]:
        """从 recent_logs.json 提取知识"""
        extracted = []
        recent_logs_path = "runtime/state/recent_logs.json"

        if not os.path.exists(recent_logs_path):
            return extracted

        try:
            with open(recent_logs_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for entry in data.get("entries", []):
                phase = entry.get("phase", "")
                desc = entry.get("desc", "")
                mission = entry.get("mission", "")

                # 提取引擎名称
                engine_patterns = [
                    r'创建\s+(\S+?Engine)',
                    r'(\S+?Engine)\s+模块',
                    r'(\S+?Engine)\s+实现'
                ]

                for pattern in engine_patterns:
                    for match in re.finditer(pattern, desc):
                        engine_name = match.group(1)
                        extracted.append({
                            "type": "engine",
                            "entity": engine_name,
                            "source": "recent_logs",
                            "mission": mission,
                            "timestamp": entry.get("time", "")
                        })

                # 提取关键词（能力）
                capability_keywords = [
                    "执行", "推荐", "学习", "推理", "规划", "分析", "优化",
                    "管理", "监控", "诊断", "预测", "生成", "理解", "联动"
                ]

                for keyword in capability_keywords:
                    if keyword in desc:
                        extracted.append({
                            "type": "capability",
                            "entity": keyword,
                            "source": "recent_logs",
                            "mission": mission,
                            "timestamp": entry.get("time", "")
                        })

        except Exception as e:
            print(f"读取 recent_logs 失败: {e}")

        self.state["extracted_knowledge"].extend(extracted)
        self.state["total_extractions"] += len(extracted)
        self.state["knowledge_sources"].append({
            "source": "recent_logs",
            "extracted_count": len(extracted),
            "timestamp": datetime.now().isoformat()
        })

        return extracted

    def extract_from_capabilities(self) -> List[Dict]:
        """从 capabilities.md 提取知识"""
        extracted = []
        capabilities_path = "references/capabilities.md"

        if not os.path.exists(capabilities_path):
            return extracted

        try:
            with open(capabilities_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取工具名称
            tool_patterns = [
                r'###\s+(\S+?Tool)',
                r'`(\S+?_tool)`',
                r'do\s+(\S+)',
            ]

            for pattern in tool_patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    tool_name = match.group(1)
                    extracted.append({
                        "type": "tool",
                        "entity": tool_name,
                        "source": "capabilities",
                        "timestamp": datetime.now().isoformat()
                    })

        except Exception as e:
            print(f"读取 capabilities 失败: {e}")

        self.state["extracted_knowledge"].extend(extracted)
        self.state["total_extractions"] += len(extracted)

        return extracted

    def detect_conflicts(self, new_knowledge: Dict) -> List[Dict]:
        """
        检测知识冲突

        Args:
            new_knowledge: 新知识

        Returns:
            冲突列表
        """
        conflicts = []
        existing = self.state.get("extracted_knowledge", [])

        for existing_k in existing:
            if (new_knowledge.get("type") == existing_k.get("type") and
                new_knowledge.get("entity") == existing_k.get("entity") and
                new_knowledge.get("source") != existing_k.get("source")):

                conflicts.append({
                    "type": "duplicate",
                    "new": new_knowledge,
                    "existing": existing_k,
                    "resolution": "keep_both"
                })

        self.state["conflict_count"] += len(conflicts)
        return conflicts

    def resolve_conflict(self, conflict: Dict, resolution: str = "keep_new") -> Dict:
        """
        解决知识冲突

        Args:
            conflict: 冲突信息
            resolution: 解决策略 (keep_new, keep_existing, merge, discard)

        Returns:
            解决结果
        """
        result = {"conflict": conflict, "resolution": resolution}

        if resolution == "discard":
            result["action"] = "discarded"
        elif resolution == "keep_existing":
            result["action"] = "kept_existing"
        elif resolution == "merge":
            result["action"] = "merged"
        else:  # keep_new
            result["action"] = "kept_new"

        self.state["resolved_conflicts"] += 1
        return result

    def evaluate_knowledge(self, knowledge: Dict) -> Tuple[float, str]:
        """
        评估知识的有效性

        Args:
            knowledge: 知识条目

        Returns:
            (有效性分数, 评估说明)
        """
        score = 0.5  # 基础分数

        # 来源可靠性评估
        source = knowledge.get("source", "")
        if source == "recent_logs":
            score += 0.3
        elif source == "execution_logs":
            score += 0.2
        elif source == "capabilities":
            score += 0.1

        # 时间衰减
        timestamp = knowledge.get("timestamp", "")
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                age_days = (datetime.now() - dt.replace(tzinfo=None)).days
                if age_days < 1:
                    score += 0.2
                elif age_days < 7:
                    score += 0.1
                elif age_days > 30:
                    score -= 0.2
            except:
                pass

        # 类型权重
        if knowledge.get("type") == "engine":
            score += 0.1
        elif knowledge.get("type") == "capability":
            score += 0.1

        # 归一化到 0-1
        score = max(0, min(1, score))

        if score >= 0.7:
            validity = "high"
        elif score >= 0.4:
            validity = "medium"
        else:
            validity = "low"

        return score, validity

    def update_knowledge_graph(self, knowledge_list: List[Dict] = None) -> Dict:
        """
        更新知识图谱

        Args:
            knowledge_list: 知识列表，默认使用提取的知识

        Returns:
            更新结果
        """
        result = {"added_nodes": 0, "added_edges": 0, "errors": []}

        if not self.kg:
            result["errors"].append("知识图谱引擎未初始化")
            return result

        if knowledge_list is None:
            knowledge_list = self.state.get("extracted_knowledge", [])

        # 按实体分组
        entities_by_type = defaultdict(list)
        for k in knowledge_list:
            entities_by_type[k.get("type", "unknown")].append(k)

        # 添加节点
        for entity_type, entities in entities_by_type.items():
            for entity in entities:
                score, validity = self.evaluate_knowledge(entity)

                # 过滤低有效性知识
                if score < 0.4:
                    continue

                node_id = self._generate_node_id(entity_type, entity.get("entity", ""))

                try:
                    self.kg.add_node(
                        node_id=node_id,
                        node_type=entity_type,
                        properties={
                            "name": entity.get("entity", ""),
                            "source": entity.get("source", ""),
                            "validity": validity,
                            "score": score,
                            "discovered_at": entity.get("timestamp", datetime.now().isoformat())
                        }
                    )
                    result["added_nodes"] += 1
                except Exception as e:
                    result["errors"].append(f"添加节点失败: {e}")

        # 添加边（基于共现关系）
        engine_entities = entities_by_type.get("engine", [])
        capability_entities = entities_by_type.get("capability", [])

        for engine in engine_entities:
            for cap in capability_entities:
                edge_id = f"edge_{self._generate_node_id('edge', engine.get('entity', '') + cap.get('entity', ''))}"
                try:
                    self.kg.add_edge(
                        from_node=self._generate_node_id("engine", engine.get("entity", "")),
                        to_node=self._generate_node_id("capability", cap.get("entity", "")),
                        relation="provides",
                        properties={"source": "knowledge_evolution"}
                    )
                    result["added_edges"] += 1
                except:
                    pass  # 边可能已存在

        self.kg._save_graph()
        self.state["total_updates"] += 1
        self.state["last_evolution"] = datetime.now().isoformat()

        return result

    def evolve(self, sources: List[str] = None) -> Dict:
        """
        执行知识进化

        Args:
            sources: 知识来源列表 (execution_logs, recent_logs, capabilities)

        Returns:
            进化结果
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "sources_used": [],
            "extracted_count": 0,
            "conflicts_found": 0,
            "updates": {}
        }

        if sources is None:
            sources = ["recent_logs", "execution_logs", "capabilities"]

        # 提取知识
        for source in sources:
            if source == "execution_logs":
                extracted = self.extract_from_execution_logs()
                result["sources_used"].append("execution_logs")
                result["extracted_count"] += len(extracted)
            elif source == "recent_logs":
                extracted = self.extract_from_recent_logs()
                result["sources_used"].append("recent_logs")
                result["extracted_count"] += len(extracted)
            elif source == "capabilities":
                extracted = self.extract_from_capabilities()
                result["sources_used"].append("capabilities")
                result["extracted_count"] += len(extracted)

        # 检测冲突
        all_knowledge = self.state.get("extracted_knowledge", [])
        recent = all_knowledge[-10:]  # 只检查最近的知识
        for k in recent:
            conflicts = self.detect_conflicts(k)
            result["conflicts_found"] += len(conflicts)

        # 更新知识图谱
        result["updates"] = self.update_knowledge_graph()

        # 记录进化历史
        self.state["evolution_history"].append({
            "timestamp": result["timestamp"],
            "extracted_count": result["extracted_count"],
            "conflicts_found": result["conflicts_found"],
            "updates": result["updates"]
        })

        # 只保留最近100条历史
        if len(self.state["evolution_history"]) > 100:
            self.state["evolution_history"] = self.state["evolution_history"][-100:]

        self._save_state()

        return result

    def get_status(self) -> Dict:
        """获取引擎状态"""
        return {
            "total_extractions": self.state.get("total_extractions", 0),
            "total_updates": self.state.get("total_updates", 0),
            "conflict_count": self.state.get("conflict_count", 0),
            "resolved_conflicts": self.state.get("resolved_conflicts", 0),
            "last_evolution": self.state.get("last_evolution", "从未"),
            "knowledge_sources": len(self.state.get("knowledge_sources", [])),
            "evolution_history_count": len(self.state.get("evolution_history", []))
        }

    def get_insights(self) -> List[Dict]:
        """获取知识进化洞察"""
        insights = []

        # 统计各类型知识
        type_counts = defaultdict(int)
        for k in self.state.get("extracted_knowledge", []):
            type_counts[k.get("type", "unknown")] += 1

        insights.append({
            "type": "statistics",
            "title": "知识统计",
            "content": f"共提取 {len(self.state.get('extracted_knowledge', []))} 条知识，其中引擎类 {type_counts.get('engine', 0)} 条，能力类 {type_counts.get('capability', 0)} 条，工具类 {type_counts.get('tool', 0)} 条"
        })

        # 进化趋势
        history = self.state.get("evolution_history", [])
        if len(history) >= 2:
            recent = history[-5:]
            trend = "上升" if recent[-1].get("extracted_count", 0) > recent[0].get("extracted_count", 0) else "稳定"
            insights.append({
                "type": "trend",
                "title": "进化趋势",
                "content": f"最近5次进化提取知识数量趋势{trend}，最近一次提取 {recent[-1].get('extracted_count', 0)} 条"
            })

        # 冲突分析
        conflict_rate = 0
        if self.state.get("total_extractions", 0) > 0:
            conflict_rate = self.state.get("conflict_count", 0) / self.state.get("total_extractions", 1)

        insights.append({
            "type": "conflict",
            "title": "冲突分析",
            "content": f"发现 {self.state.get('conflict_count', 0)} 个冲突，已解决 {self.state.get('resolved_conflicts', 0)} 个，冲突率 {conflict_rate:.1%}"
        })

        return insights


def main():
    """CLI 入口"""
    import argparse

    parser = argparse.ArgumentParser(description="智能知识进化引擎")
    parser.add_argument("command", nargs="?", default="status",
                       help="命令: status/evolve/insights/update/stats")
    parser.add_argument("--sources", nargs="+",
                       help="知识来源: execution_logs recent_logs capabilities")
    parser.add_argument("--auto", action="store_true",
                       help="自动执行完整进化流程")

    args = parser.parse_args()

    engine = KnowledgeEvolutionEngine()

    if args.command == "status" or args.command == "stats":
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return

    elif args.command == "evolve" or args.auto:
        sources = args.sources if args.sources else None
        result = engine.evolve(sources=sources)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    elif args.command == "update":
        result = engine.update_knowledge_graph()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    elif args.command == "insights":
        insights = engine.get_insights()
        for insight in insights:
            print(f"\n## {insight['title']}")
            print(insight['content'])
        return

    else:
        # 尝试调用知识图谱方法
        if hasattr(engine, args.command):
            method = getattr(engine, args.command)
            if callable(method):
                result = method()
                print(json.dumps(result, ensure_ascii=False, indent=2))
                return

        parser.print_help()


if __name__ == "__main__":
    main()