#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能创新发现引擎 (Innovation Discovery Engine)

功能：主动发现"人没想到但很有用的"新能力、新用法、新组合。
核心能力：
1. 能力组合分析 - 分析现有能力，识别潜在有用组合
2. 用户行为模式创新发现 - 从用户行为中发现可自动化的重复模式
3. 知识关联创新发现 - 从知识图谱中发现隐藏的新关联
4. 创新推荐功能 - 主动向用户推荐发现的创新用法

集成：
- adaptive_learning_engine: 用户行为分析能力
- knowledge_graph: 知识关联分析
- workflow_engine: 自动化工作流
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict
from itertools import combinations

# 路径处理
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)


class InnovationDiscoveryEngine:
    """智能创新发现引擎"""

    def __init__(self):
        self.name = "Innovation Discovery Engine"
        self.version = "1.0.0"
        self.state_file = os.path.join(PROJECT_ROOT, "runtime", "state", "innovation_discovery_state.json")
        self.findings_file = os.path.join(PROJECT_ROOT, "runtime", "state", "innovation_findings.json")

        # 能力组合模式库（预设的潜在有用组合）
        self.capability_combinations = {
            "auto_workflow_from_repetition": {
                "description": "从重复行为自动生成工作流",
                "required_capabilities": ["行为记录", "模式识别", "工作流生成"],
                "value": "高"
            },
            "cross_app_automation": {
                "description": "跨应用自动化链",
                "required_capabilities": ["应用控制", "剪贴板", "数据转换"],
                "value": "高"
            },
            "smart_notification_routing": {
                "description": "智能通知路由（根据内容/紧急程度自动处理）",
                "required_capabilities": ["通知理解", "智能分类", "自动回复"],
                "value": "中"
            },
            "context_aware_suggestions": {
                "description": "基于上下文的主动建议（时间+地点+活动）",
                "required_capabilities": ["情境感知", "历史学习", "建议生成"],
                "value": "高"
            },
            "predictive_file_organization": {
                "description": "预测性文件整理（根据使用模式自动归类）",
                "required_capabilities": ["文件监控", "使用模式分析", "自动整理"],
                "value": "中"
            }
        }

        # 创新能力类型
        self.innovation_types = [
            "能力组合创新",
            "自动化模式创新",
            "知识关联创新",
            "用户体验创新",
            "跨域融合创新"
        ]

        # 加载现有状态
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        """加载状态"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "discoveries": [],
            "recommendations": [],
            "last_discovery_time": None,
            "total_discoveries": 0
        }

    def _save_state(self):
        """保存状态"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def analyze_capability_combinations(self) -> List[Dict]:
        """分析能力组合，发现潜在创新点"""
        discoveries = []

        # 读取现有能力列表
        capabilities_file = os.path.join(PROJECT_ROOT, "references", "capabilities.md")
        existing_capabilities = []

        if os.path.exists(capabilities_file):
            try:
                with open(capabilities_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 简单提取能力关键词
                    capability_keywords = [
                        "截图", "鼠标", "键盘", "vision", "窗口", "进程", "文件",
                        "剪贴板", "通知", "语音", "摄像头", "浏览器", "应用"
                    ]
                    for kw in capability_keywords:
                        if kw in content:
                            existing_capabilities.append(kw)
            except Exception:
                pass

        # 分析预设的能力组合
        for combo_name, combo_info in self.capability_combinations.items():
            # 检查组合中已有多少能力被实现
            matched_capabilities = []
            for cap in combo_info["required_capabilities"]:
                for existing in existing_capabilities:
                    if any(c in existing for c in cap):
                        matched_capabilities.append(cap)
                        break

            if len(matched_capabilities) >= 2 and len(matched_capabilities) < len(combo_info["required_capabilities"]):
                # 发现部分满足的组合，可以作为创新点
                missing = [c for c in combo_info["required_capabilities"] if c not in matched_capabilities]
                discoveries.append({
                    "type": "能力组合创新",
                    "name": combo_name,
                    "description": combo_info["description"],
                    "value": combo_info["value"],
                    "matched_capabilities": matched_capabilities,
                    "missing_capabilities": missing,
                    "suggestion": f"建议开发{missing[0] if missing else ''}能力，实现{combo_info['description']}"
                })

        return discoveries

    def discover_user_behavior_patterns(self) -> List[Dict]:
        """从用户行为中发现可自动化的模式"""
        discoveries = []

        # 读取用户行为学习数据
        learning_state_file = os.path.join(PROJECT_ROOT, "runtime", "state", "adaptive_learning_state.json")

        if os.path.exists(learning_state_file):
            try:
                with open(learning_state_file, 'r', encoding='utf-8') as f:
                    learning_data = json.load(f)

                # 分析用户行为模式
                if "behavior_patterns" in learning_data:
                    patterns = learning_data["behavior_patterns"]

                    for pattern_name, pattern_data in patterns.items():
                        # 检查重复次数
                        if "frequency" in pattern_data and pattern_data["frequency"] >= 3:
                            # 建议自动化
                            discoveries.append({
                                "type": "自动化模式创新",
                                "name": pattern_name,
                                "description": f"用户经常执行: {pattern_data.get('description', pattern_name)}",
                                "frequency": pattern_data.get("frequency", 0),
                                "suggestion": f"创建自动化工作流，一键执行此操作序列",
                                "priority": "high" if pattern_data.get("frequency", 0) >= 5 else "medium"
                            })
            except Exception:
                pass

        # 从场景执行历史发现模式
        scenario_exp_file = os.path.join(PROJECT_ROOT, "runtime", "state", "scenario_experiences.json")
        if os.path.exists(scenario_exp_file):
            try:
                with open(scenario_exp_file, 'r', encoding='utf-8') as f:
                    scenario_data = json.load(f)

                # 分析连续执行模式
                if isinstance(scenario_data, list) and len(scenario_data) >= 2:
                    recent = scenario_data[-5:] if len(scenario_data) > 5 else scenario_data
                    scenarios = [s.get("scenario", s.get("name", "")) for s in recent]

                    # 检查是否有固定顺序
                    if len(set(scenarios)) < len(scenarios):
                        # 发现重复序列
                        discoveries.append({
                            "type": "自动化模式创新",
                            "name": "sequential_execution_pattern",
                            "description": "检测到顺序执行的场景模式",
                            "scenarios": scenarios,
                            "suggestion": "创建复合工作流，一次性执行多个场景"
                        })
            except Exception:
                pass

        return discoveries

    def discover_knowledge_associations(self) -> List[Dict]:
        """从知识图谱中发现隐藏的新关联"""
        discoveries = []

        # 读取知识图谱数据
        kg_file = os.path.join(PROJECT_ROOT, "runtime", "state", "knowledge_graph.json")

        if os.path.exists(kg_file):
            try:
                with open(kg_file, 'r', encoding='utf-8') as f:
                    kg_data = json.load(f)

                # 分析实体关系
                if "entities" in kg_data and "relations" in kg_data:
                    entities = kg_data.get("entities", {})
                    relations = kg_data.get("relations", [])

                    # 统计关系类型
                    relation_types = defaultdict(list)
                    for rel in relations:
                        rel_type = rel.get("type", "unknown")
                        relation_types[rel_type].append(rel)

                    # 查找可能的隐含关联
                    # 例如：同时与A和B有关系的实体可能存在某种联系
                    entity_relations = defaultdict(list)
                    for rel in relations:
                        src = rel.get("source", "")
                        tgt = rel.get("target", "")
                        if src:
                            entity_relations[src].append(tgt)
                        if tgt:
                            entity_relations[tgt].append(src)

                    # 发现与多个实体有强关联的实体
                    for entity, related in entity_relations.items():
                        if len(related) >= 3:
                            discoveries.append({
                                "type": "知识关联创新",
                                "name": f"hub_entity_{entity}",
                                "description": f"发现中心实体: {entity}",
                                "related_entities": related,
                                "suggestion": f"{entity} 连接了多个实体，可能适合作为智能推荐的入口点"
                            })
            except Exception:
                pass

        return discoveries

    def generate_recommendations(self, discoveries: List[Dict]) -> List[Dict]:
        """生成创新推荐"""
        recommendations = []

        for discovery in discoveries:
            rec = {
                "innovation_type": discovery.get("type", "未知类型"),
                "name": discovery.get("name", "未命名"),
                "description": discovery.get("description", ""),
                "suggestion": discovery.get("suggestion", ""),
                "value": discovery.get("value", "中"),
                "priority": discovery.get("priority", "medium"),
                "timestamp": datetime.now().isoformat()
            }
            recommendations.append(rec)

        # 按优先级排序
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 1))

        return recommendations

    def full_discovery(self) -> Dict:
        """执行完整创新发现"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "capability_combinations": self.analyze_capability_combinations(),
            "behavior_patterns": self.discover_user_behavior_patterns(),
            "knowledge_associations": self.discover_knowledge_associations()
        }

        # 合并所有发现
        all_discoveries = (
            results["capability_combinations"] +
            results["behavior_patterns"] +
            results["knowledge_associations"]
        )

        # 生成推荐
        results["recommendations"] = self.generate_recommendations(all_discoveries)

        # 更新状态
        self.state["discoveries"] = all_discoveries
        self.state["recommendations"] = results["recommendations"]
        self.state["last_discovery_time"] = results["timestamp"]
        self.state["total_discoveries"] = len(all_discoveries)
        self._save_state()

        # 保存详细结果
        os.makedirs(os.path.dirname(self.findings_file), exist_ok=True)
        with open(self.findings_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        return results

    def get_status(self) -> Dict:
        """获取引擎状态"""
        return {
            "name": self.name,
            "version": self.version,
            "total_discoveries": self.state.get("total_discoveries", 0),
            "last_discovery_time": self.state.get("last_discovery_time"),
            "innovation_types": self.innovation_types
        }

    def get_recommendations(self, limit: int = 5) -> List[Dict]:
        """获取创新推荐"""
        return self.state.get("recommendations", [])[:limit]


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description="智能创新发现引擎")
    parser.add_argument("command", nargs="?", default="status",
                       help="命令: status, discover, recommendations")
    parser.add_argument("--limit", type=int, default=5, help="推荐数量限制")

    args = parser.parse_args()

    engine = InnovationDiscoveryEngine()

    if args.command == "status":
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    elif args.command == "discover":
        results = engine.full_discovery()
        print(f"发现 {len(results['capability_combinations'])} 个能力组合创新点")
        print(f"发现 {len(results['behavior_patterns'])} 个行为模式创新点")
        print(f"发现 {len(results['knowledge_associations'])} 个知识关联创新点")
        print(f"\n生成 {len(results['recommendations'])} 个创新推荐")
        print(f"\n详细结果已保存到: {engine.findings_file}")
    elif args.command == "recommendations":
        recs = engine.get_recommendations(args.limit)
        print(json.dumps(recs, ensure_ascii=False, indent=2))
    else:
        print(f"未知命令: {args.command}")
        print("可用命令: status, discover, recommendations")


if __name__ == "__main__":
    main()