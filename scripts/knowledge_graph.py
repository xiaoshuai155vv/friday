#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版知识图谱测试模块
"""

import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict
from pathlib import Path

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

class KnowledgeGraph:
    """简化版知识图谱引擎用于测试"""

    def __init__(self, storage_path="runtime/state/knowledge_graph.json"):
        """
        初始化知识图谱引擎

        Args:
            storage_path: 存储知识图谱的文件路径
        """
        self.storage_path = storage_path
        self.graph = {
            "nodes": {},  # 节点集合 {node_id: {"type": "...", "properties": {...}}}
            "edges": [],  # 边集合 [{"from": "...", "to": "...", "relation": "...", "properties": {...}}]
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "version": "1.0"
            }
        }

        # 加载已有知识图谱
        self._load_graph()

    def _load_graph(self):
        """从文件加载知识图谱"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    loaded_graph = json.load(f)
                    # 兼容旧版本结构
                    if isinstance(loaded_graph, dict) and 'nodes' in loaded_graph:
                        self.graph = loaded_graph
                    else:
                        # 如果是旧格式，转换为新格式
                        self.graph = {
                            "nodes": {},
                            "edges": [],
                            "metadata": {
                                "created_at": datetime.now().isoformat(),
                                "updated_at": datetime.now().isoformat(),
                                "version": "1.0"
                            }
                        }
            except Exception as e:
                print(f"加载知识图谱失败: {e}")
                self.graph = {
                    "nodes": {},
                    "edges": [],
                    "metadata": {
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat(),
                        "version": "1.0"
                    }
                }

    def _save_graph(self):
        """保存知识图谱到文件"""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            self.graph["metadata"]["updated_at"] = datetime.now().isoformat()
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.graph, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存知识图谱失败: {e}")

    def add_node(self, node_id: str, node_type: str, properties: Dict[str, Any] = None):
        """
        添加节点到知识图谱

        Args:
            node_id: 节点唯一标识
            node_type: 节点类型 (user, scene, behavior, knowledge)
            properties: 节点属性
        """
        if properties is None:
            properties = {}

        self.graph["nodes"][node_id] = {
            "type": node_type,
            "properties": properties,
            "created_at": datetime.now().isoformat()
        }
        self._save_graph()

    def add_edge(self, from_node: str, to_node: str, relation: str, properties: Dict[str, Any] = None):
        """
        添加边到知识图谱

        Args:
            from_node: 起始节点
            to_node: 目标节点
            relation: 关系类型
            properties: 边属性
        """
        if properties is None:
            properties = {}

        edge = {
            "from": from_node,
            "to": to_node,
            "relation": relation,
            "properties": properties,
            "created_at": datetime.now().isoformat()
        }

        # 避免重复边
        if edge not in self.graph["edges"]:
            self.graph["edges"].append(edge)
            self._save_graph()

    def get_nodes_by_type(self, node_type: str) -> List[Dict]:
        """
        根据类型获取节点

        Args:
            node_type: 节点类型

        Returns:
            节点列表
        """
        nodes = []
        for node_id, node_data in self.graph["nodes"].items():
            if node_data["type"] == node_type:
                node_info = {
                    "id": node_id,
                    "type": node_data["type"],
                    "properties": node_data["properties"]
                }
                nodes.append(node_info)
        return nodes

    def get_related_nodes(self, node_id: str, relation_type: str = None) -> List[Dict]:
        """
        获取相关节点

        Args:
            node_id: 起始节点ID
            relation_type: 关系类型（可选）

        Returns:
            相关节点列表
        """
        related = []
        for edge in self.graph["edges"]:
            if edge["from"] == node_id:
                if relation_type is None or edge["relation"] == relation_type:
                    target_node = self.graph["nodes"].get(edge["to"])
                    if target_node:
                        related.append({
                            "node_id": edge["to"],
                            "node_type": target_node["type"],
                            "relation": edge["relation"],
                            "properties": target_node["properties"]
                        })
        return related

    def query_relationship(self, node1_id: str, node2_id: str) -> List[str]:
        """
        查询两个节点之间的关系

        Args:
            node1_id: 第一个节点ID
            node2_id: 第二个节点ID

        Returns:
            关系列表
        """
        relations = []
        for edge in self.graph["edges"]:
            if ((edge["from"] == node1_id and edge["to"] == node2_id) or
                (edge["from"] == node2_id and edge["to"] == node1_id)):
                relations.append(edge["relation"])
        return relations

    def infer_contextual_knowledge(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        基于上下文推断知识

        Args:
            context: 上下文信息

        Returns:
            推断的知识结果
        """
        inference_result = {
            "context": context,
            "related_knowledge": [],
            "suggested_actions": [],
            "confidence": 0.0
        }

        # 从上下文中提取关键信息
        user_id = context.get("user_id", "default_user")
        current_scene = context.get("scene", "default_scene")
        current_time = context.get("time", datetime.now().isoformat())

        # 添加用户节点
        self.add_node(
            f"user_{user_id}",
            "user",
            {"name": f"用户_{user_id}", "preferences": ["通用偏好"]}
        )

        # 添加场景节点
        self.add_node(
            f"scene_{current_scene}",
            "scene",
            {"name": current_scene, "timestamp": current_time}
        )

        # 添加用户与场景的关联
        self.add_edge(
            f"user_{user_id}",
            f"scene_{current_scene}",
            "operates_in",
            {"timestamp": current_time}
        )

        # 推荐与当前场景相关的知识
        scene_knowledge = [
            {"topic": "办公效率", "type": "scene_based"},
            {"topic": "时间管理", "type": "scene_based"},
            {"topic": "系统优化", "type": "scene_based"}
        ]

        for k in scene_knowledge:
            knowledge_id = f"knowledge_{k['topic'].replace(' ', '_')}"
            self.add_node(knowledge_id, "knowledge", k)
            self.add_edge(
                f"scene_{current_scene}",
                knowledge_id,
                "requires",
                {"confidence": 0.7}
            )

            # 添加到推荐列表
            inference_result["related_knowledge"].append({
                "topic": k["topic"],
                "confidence": 0.7
            })

        # 设置置信度
        inference_result["confidence"] = 0.75

        return inference_result

    def get_graph_statistics(self) -> Dict[str, Any]:
        """
        获取知识图谱统计信息

        Returns:
            统计信息
        """
        node_types = defaultdict(int)
        edge_relations = defaultdict(int)

        for node in self.graph["nodes"].values():
            node_types[node["type"]] += 1

        for edge in self.graph["edges"]:
            edge_relations[edge["relation"]] += 1

        return {
            "total_nodes": len(self.graph["nodes"]),
            "total_edges": len(self.graph["edges"]),
            "node_distribution": dict(node_types),
            "edge_distribution": dict(edge_relations),
            "metadata": self.graph["metadata"]
        }

    def get_node_details(self, node_id: str) -> Optional[Dict]:
        """
        获取节点详细信息

        Args:
            node_id: 节点ID

        Returns:
            节点详细信息
        """
        return self.graph["nodes"].get(node_id)

    def get_edge_details(self, from_node: str, to_node: str) -> List[Dict]:
        """
        获取边的详细信息

        Args:
            from_node: 起始节点
            to_node: 目标节点

        Returns:
            边的详细信息列表
        """
        edges = []
        for edge in self.graph["edges"]:
            if edge["from"] == from_node and edge["to"] == to_node:
                edges.append(edge)
        return edges

def main():
    """主函数 - 用于测试"""
    # 创建知识图谱实例
    kg = KnowledgeGraph()

    # 测试添加节点
    kg.add_node("user_001", "user", {"name": "张三", "preferences": ["办公", "学习"]})
    kg.add_node("scene_office", "scene", {"name": "办公室", "location": "公司"})
    kg.add_node("knowledge_productivity", "knowledge", {"topic": "办公效率", "type": "productivity"})

    # 测试添加边
    kg.add_edge("user_001", "scene_office", "operates_in", {"timestamp": "2026-03-12T10:00:00"})
    kg.add_edge("user_001", "knowledge_productivity", "interested_in", {"confidence": 0.8})

    # 测试查询
    print("节点查询:")
    print(kg.get_nodes_by_type("user"))

    print("\n关系查询:")
    print(kg.query_relationship("user_001", "scene_office"))

    # 测试上下文推理
    context = {
        "user_id": "001",
        "scene": "办公室",
        "time": "2026-03-12T10:00:00"
    }

    print("\n上下文推理:")
    inference = kg.infer_contextual_knowledge(context)
    print(inference)

    # 测试统计
    print("\n图谱统计:")
    stats = kg.get_graph_statistics()
    print(stats)

if __name__ == "__main__":
    main()