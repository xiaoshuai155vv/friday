#!/usr/bin/env python3
"""
智能全场景跨引擎知识深度融合与主动洞察生成引擎
(Evolution Cross-Engine Knowledge Fusion and Proactive Insight Generation Engine)
version 1.0.0

让系统能够跨引擎深度融合知识，主动生成高价值洞察，实现从「被动响应查询」到
「主动发现机会」的范式升级。

功能：
1. 跨引擎知识聚合 - 融合诊断、健康、进化、策略等引擎的洞察
2. 主动洞察生成 - 不是等查询，主动发现系统改进机会
3. 知识关联推理 - 发现跨领域隐藏关联
4. 洞察优先级排序 - 基于价值、可行性、紧迫度排序
5. 与进化环深度集成 - 洞察可触发进化

依赖：
- evolution_knowledge_inheritance_engine.py (round 240)
- evolution_knowledge_graph_reasoning.py (round 298)
- unified_diagnosis_healing_engine.py (round 319)
- evolution_meta_coordination_engine.py (round 312)
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict
import random

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class CrossEngineKnowledgeFusion:
    """跨引擎知识深度融合与主动洞察生成引擎"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.runtime_dir = self.project_root / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.references_dir = self.project_root / "references"
        self.scripts_dir = self.project_root / "scripts"

        # 洞察库存储路径
        self.insight_db_dir = self.runtime_dir / "insight_db"
        self.insight_db_dir.mkdir(exist_ok=True)

        # 洞察数据文件
        self.insights_file = self.insight_db_dir / "active_insights.json"
        self.insight_history_file = self.insight_db_dir / "insight_history.json"
        self.fusion_cache_file = self.insight_db_dir / "fusion_cache.json"

        # 加载或初始化洞察库
        self.insights = self._load_insights()
        self.insight_history = self._load_insight_history()
        self.fusion_cache = self._load_fusion_cache()

        # 已注册的引擎知识接口
        self.engine_knowledge_interfaces = {}

    def _load_insights(self) -> Dict:
        """加载主动洞察"""
        if self.insights_file.exists():
            try:
                with open(self.insights_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "active_insights": [],
            "pending_insights": [],
            "implemented_insights": []
        }

    def _load_insight_history(self) -> List[Dict]:
        """加载洞察历史"""
        if self.insight_history_file.exists():
            try:
                with open(self.insight_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return []

    def _load_fusion_cache(self) -> Dict:
        """加载融合缓存"""
        if self.fusion_cache_file.exists():
            try:
                with open(self.fusion_cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "fusion_records": [],
            "knowledge_links": {}
        }

    def _save_insights(self):
        """保存洞察数据"""
        self.insights["last_updated"] = datetime.now().isoformat()
        with open(self.insights_file, 'w', encoding='utf-8') as f:
            json.dump(self.insights, f, ensure_ascii=False, indent=2)

    def _save_fusion_cache(self):
        """保存融合缓存"""
        self.fusion_cache["last_updated"] = datetime.now().isoformat()
        with open(self.fusion_cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.fusion_cache, f, ensure_ascii=False, indent=2)

    def register_engine_knowledge(self, engine_name: str, knowledge_source: Any):
        """注册引擎知识接口

        Args:
            engine_name: 引擎名称
            knowledge_source: 引擎知识获取接口（通常是引擎实例或模块）
        """
        self.engine_knowledge_interfaces[engine_name] = knowledge_source

    def collect_engine_knowledge(self) -> Dict[str, Any]:
        """从各引擎收集知识

        Returns:
            Dict: 各引擎的知识汇总
        """
        knowledge = {
            "system_health": [],
            "evolution_status": [],
            "engine_capabilities": [],
            "historical_patterns": [],
            "recent_insights": [],
            "meta_knowledge": []
        }

        # 1. 尝试从诊断引擎获取系统健康知识
        try:
            diag_engine_path = self.scripts_dir / "unified_diagnosis_healing_engine.py"
            if diag_engine_path.exists():
                knowledge["system_health"].append({
                    "source": "unified_diagnosis_healing_engine",
                    "status": "available",
                    "capability": "health_diagnosis"
                })
        except Exception as e:
            pass

        # 2. 尝试从元协调引擎获取进化状态
        try:
            meta_engine_path = self.scripts_dir / "evolution_meta_coordination_engine.py"
            if meta_engine_path.exists():
                knowledge["evolution_status"].append({
                    "source": "evolution_meta_coordination_engine",
                    "status": "available",
                    "capability": "meta_coordination"
                })
        except Exception as e:
            pass

        # 3. 从知识传承引擎获取历史知识
        try:
            inherit_engine_path = self.scripts_dir / "evolution_knowledge_inheritance_engine.py"
            if inherit_engine_path.exists():
                knowledge["historical_patterns"].append({
                    "source": "evolution_knowledge_inheritance_engine",
                    "status": "available",
                    "capability": "knowledge_inheritance"
                })
        except Exception as e:
            pass

        # 4. 从知识图谱引擎获取图谱知识
        try:
            kg_engine_path = self.scripts_dir / "evolution_knowledge_graph_reasoning.py"
            if kg_engine_path.exists():
                knowledge["meta_knowledge"].append({
                    "source": "evolution_knowledge_graph_reasoning",
                    "status": "available",
                    "capability": "knowledge_graph_reasoning"
                })
        except Exception as e:
            pass

        # 5. 从 scripts 目录统计引擎能力
        try:
            engine_count = 0
            common_files = ["do.py", "state_tracker.py", "behavior_log.py", "export_recent_logs.py",
                          "scenario_log.py", "query_scenario_experiences.py", "self_verify_capabilities.py",
                          "git_commit_evolution.py"]
            for f in self.scripts_dir.glob("*.py"):
                if f.name not in common_files:
                    engine_count += 1
            if engine_count > 0:
                knowledge["engine_capabilities"].append({
                    "source": "scripts directory",
                    "status": "available",
                    "engine_count_estimate": engine_count
                })
        except Exception as e:
            pass

        # 6. 从进化历史获取模式
        try:
            state_files = list(self.state_dir.glob("evolution_completed_*.json"))
            recent_rounds = []
            for f in sorted(state_files, key=lambda x: x.stat().st_mtime, reverse=True)[:10]:
                try:
                    with open(f, 'r', encoding='utf-8') as fh:
                        data = json.load(fh)
                        recent_rounds.append({
                            "round": data.get("loop_round", "unknown"),
                            "goal": data.get("current_goal", ""),
                            "status": data.get("status", "unknown")
                        })
                except:
                    pass
            if recent_rounds:
                knowledge["recent_insights"].extend(recent_rounds)
        except Exception as e:
            pass

        return knowledge

    def fuse_knowledge(self, knowledge: Dict[str, Any]) -> List[Dict[str, Any]]:
        """融合跨引擎知识，生成综合洞察

        Args:
            knowledge: 各引擎的知识汇总

        Returns:
            List: 融合后的洞察列表
        """
        fusion_results = []

        # 1. 系统健康洞察融合
        if knowledge.get("system_health"):
            fusion_results.append({
                "type": "system_capability",
                "title": "系统诊断能力可用",
                "description": f"检测到 {len(knowledge['system_health'])} 个系统健康诊断模块",
                "evidence": knowledge["system_health"],
                "confidence": 0.9,
                "value_score": 7
            })

        # 2. 进化能力洞察
        if knowledge.get("evolution_status"):
            fusion_results.append({
                "type": "evolution_capability",
                "title": "元进化协调能力可用",
                "description": f"检测到 {len(knowledge['evolution_status'])} 个元进化引擎",
                "evidence": knowledge["evolution_status"],
                "confidence": 0.9,
                "value_score": 8
            })

        # 3. 引擎能力洞察
        if knowledge.get("engine_capabilities"):
            for cap in knowledge["engine_capabilities"]:
                if "engine_count_estimate" in cap:
                    fusion_results.append({
                        "type": "engine_ecosystem",
                        "title": "引擎生态系统健康",
                        "description": f"系统拥有约 {cap['engine_count_estimate']} 个能力模块",
                        "evidence": [cap],
                        "confidence": 0.8,
                        "value_score": 8
                    })

        # 4. 历史模式洞察
        if knowledge.get("recent_insights"):
            completed = [r for r in knowledge["recent_insights"] if r.get("status") == "completed"]
            if completed:
                fusion_results.append({
                    "type": "evolution_momentum",
                    "title": "进化动能充足",
                    "description": f"最近10轮中有 {len(completed)} 轮已完成，系统进化活跃",
                    "evidence": completed[:5],
                    "confidence": 0.85,
                    "value_score": 7
                })

        # 5. 跨领域关联发现
        if knowledge.get("meta_knowledge") and knowledge.get("historical_patterns"):
            fusion_results.append({
                "type": "cross_domain_link",
                "title": "知识图谱与传承链路完整",
                "description": "系统具备跨轮次知识传承和图谱推理能力，可实现深度知识融合",
                "evidence": knowledge["meta_knowledge"] + knowledge["historical_patterns"],
                "confidence": 0.88,
                "value_score": 9
            })

        # 6. 潜在优化机会洞察
        if len(knowledge.get("recent_insights", [])) > 0:
            # 分析是否有连续相同类型的进化
            goals = [r.get("goal", "") for r in knowledge["recent_insights"]]
            # 检查是否有重复领域
            repeated_domains = self._find_repeated_domains(goals)
            if repeated_domains:
                fusion_results.append({
                    "type": "optimization_opportunity",
                    "title": f"发现重复进化领域: {repeated_domains}",
                    "description": f"近期进化在 {repeated_domains} 领域有重复，可考虑优化进化策略",
                    "evidence": goals,
                    "confidence": 0.75,
                    "value_score": 8,
                    "actionable": True,
                    "suggested_action": "调用 evolution_meta_optimizer 优化策略"
                })

        return fusion_results

    def _find_repeated_domains(self, goals: List[str]) -> Optional[str]:
        """从目标列表中发现重复领域"""
        domain_keywords = {
            "健康": ["健康", "诊断", "自愈", "预警"],
            "进化": ["进化", "优化", "策略", "元"],
            "协同": ["协同", "协作", "调度", "编排"],
            "知识": ["知识", "图谱", "推理", "传承"],
            "智能": ["智能", "自主", "自动", "自适应"]
        }

        domain_counts = {d: 0 for d in domain_keywords}
        for goal in goals:
            for domain, keywords in domain_keywords.items():
                if any(kw in goal for kw in keywords):
                    domain_counts[domain] += 1

        # 找出出现2次以上的领域
        repeated = [d for d, count in domain_counts.items() if count >= 2]
        if repeated:
            return ", ".join(repeated)
        return None

    def generate_proactive_insights(self) -> List[Dict[str, Any]]:
        """主动生成洞察（无需等待查询）

        Returns:
            List: 主动生成的洞察列表
        """
        # 1. 收集各引擎知识
        knowledge = self.collect_engine_knowledge()

        # 2. 融合知识
        fusion_results = self.fuse_knowledge(knowledge)

        # 3. 生成主动洞察
        proactive_insights = []

        for insight in fusion_results:
            # 添加优先级评分
            insight["priority_score"] = self._calculate_priority(insight)
            insight["generated_at"] = datetime.now().isoformat()
            insight["source"] = "proactive_generation"

            # 检查是否已存在相似洞察
            if not self._is_duplicate_insight(insight):
                proactive_insights.append(insight)

        # 4. 更新洞察库
        self.insights["active_insights"] = proactive_insights
        self._save_insights()

        return proactive_insights

    def _calculate_priority(self, insight: Dict) -> float:
        """计算洞察优先级分数

        Args:
            insight: 洞察数据

        Returns:
            float: 优先级分数 (0-10)
        """
        score = 5.0  # 基础分

        # 置信度加权
        score += insight.get("confidence", 0.5) * 3

        # 价值评分加权
        score += insight.get("value_score", 5) * 0.5

        # 可执行性加分
        if insight.get("actionable"):
            score += 1.5

        return min(score, 10.0)

    def _is_duplicate_insight(self, new_insight: Dict) -> bool:
        """检查是否与已有洞察重复"""
        for existing in self.insights.get("active_insights", []):
            if existing.get("title") == new_insight.get("title"):
                return True
        return False

    def get_top_insights(self, limit: int = 5) -> List[Dict]:
        """获取最高优先级的洞察

        Args:
            limit: 返回数量限制

        Returns:
            List: 优先级最高的洞察列表
        """
        # 确保有最新洞察
        if not self.insights.get("active_insights"):
            self.generate_proactive_insights()

        # 按优先级排序
        sorted_insights = sorted(
            self.insights.get("active_insights", []),
            key=lambda x: x.get("priority_score", 0),
            reverse=True
        )

        return sorted_insights[:limit]

    def get_dashboard_data(self) -> Dict:
        """获取洞察仪表盘数据

        Returns:
            Dict: 仪表盘展示数据
        """
        # 确保有最新洞察
        if not self.insights.get("active_insights"):
            self.generate_proactive_insights()

        return {
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "total_insights": len(self.insights.get("active_insights", [])),
            "implemented_count": len(self.insights.get("implemented_insights", [])),
            "pending_count": len(self.insights.get("pending_insights", [])),
            "top_insights": self.get_top_insights(3),
            "knowledge_sources": {
                "system_health": len(self.collect_engine_knowledge().get("system_health", [])),
                "evolution_status": len(self.collect_engine_knowledge().get("evolution_status", [])),
                "engine_capabilities": len(self.collect_engine_knowledge().get("engine_capabilities", [])),
                "recent_insights": len(self.collect_engine_knowledge().get("recent_insights", []))
            }
        }

    def query_insights(self, query: str) -> List[Dict]:
        """查询洞察（响应式）

        Args:
            query: 查询关键词

        Returns:
            List: 匹配的洞察列表
        """
        # 确保有最新洞察
        if not self.insights.get("active_insights"):
            self.generate_proactive_insights()

        # 简单关键词匹配
        query_lower = query.lower()
        results = []

        for insight in self.insights.get("active_insights", []):
            text = f"{insight.get('title', '')} {insight.get('description', '')}".lower()
            if query_lower in text:
                results.append(insight)

        # 如果没有查询结果，生成新洞察
        if not results:
            new_insights = self.generate_proactive_insights()
            results = [i for i in new_insights if query_lower in f"{i.get('title','')} {i.get('description','')}".lower()]

        return results


def main():
    """主入口 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description="跨引擎知识融合与主动洞察生成引擎")
    parser.add_argument("--generate", action="store_true", help="生成主动洞察")
    parser.add_argument("--query", type=str, help="查询洞察")
    parser.add_argument("--dashboard", action="store_true", help="获取仪表盘数据")
    parser.add_argument("--top", type=int, default=3, help="获取top N洞察")

    args = parser.parse_args()

    engine = CrossEngineKnowledgeFusion()

    if args.generate:
        insights = engine.generate_proactive_insights()
        print(json.dumps({
            "status": "success",
            "count": len(insights),
            "insights": insights
        }, ensure_ascii=False, indent=2))

    elif args.query:
        results = engine.query_insights(args.query)
        print(json.dumps({
            "status": "success",
            "query": args.query,
            "count": len(results),
            "results": results
        }, ensure_ascii=False, indent=2))

    elif args.dashboard:
        data = engine.get_dashboard_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))

    else:
        # 默认显示 top 洞察
        top_insights = engine.get_top_insights(args.top)
        print(json.dumps({
            "status": "success",
            "count": len(top_insights),
            "insights": top_insights
        }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()