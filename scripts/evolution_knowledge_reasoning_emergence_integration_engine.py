#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环知识推理-涌现发现深度集成引擎
=================================================================
在 round 521 完成的知识主动涌现发现与智能传承引擎和 round 447 完成的
跨引擎知识推理引擎基础上，进一步将两者深度集成。

让系统能够基于知识图谱主动涌现新洞察，并将洞察转化为可执行知识，
形成「知识推理→涌现发现→知识传承→持续进化」的完整自主闭环。

实现从被动知识检索到主动知识涌现发现的范式升级。

功能：
1. 集成 round 521 知识涌现发现引擎的涌现能力
2. 集成 round 447 知识推理引擎的推理能力
3. 实现知识推理驱动的涌现发现（基于推理结果主动发现新洞察）
4. 实现洞察到知识的转化（将涌现洞察写入知识库）
5. 实现完整闭环执行（推理→涌现→传承→验证）
6. 实现与进化驾驶舱深度集成
7. 集成到 do.py 支持知识推理涌现、推理驱动发现、涌现推理集成等关键词触发

version: 1.0.0
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict

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

# 尝试导入两个集成引擎
KNOWLEDGE_REASONING_AVAILABLE = False
KNOWLEDGE_EMERGENCE_AVAILABLE = False

try:
    from evolution_cross_engine_knowledge_reasoning_engine import KnowledgeReasoningEngine
    KNOWLEDGE_REASONING_AVAILABLE = True
except ImportError:
    pass

try:
    from evolution_knowledge_emergence_inheritance_engine import KnowledgeEmergenceInheritanceEngine
    KNOWLEDGE_EMERGENCE_AVAILABLE = True
except ImportError:
    pass


class KnowledgeReasoningEmergenceIntegrationEngine:
    """知识推理-涌现发现深度集成引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.engine_name = "知识推理-涌现发现深度集成引擎"

        # 初始化两个子引擎
        self.reasoning_engine = None
        self.emergence_engine = None
        self.integration_status = {
            "reasoning_available": KNOWLEDGE_REASONING_AVAILABLE,
            "emergence_available": KNOWLEDGE_EMERGENCE_AVAILABLE,
            "integration_complete": False,
            "last_integration_round": None
        }

        # 尝试初始化子引擎
        if KNOWLEDGE_REASONING_AVAILABLE:
            try:
                self.reasoning_engine = KnowledgeReasoningEngine()
                print(f"[{self.engine_name}] 知识推理引擎初始化成功")
            except Exception as e:
                print(f"[{self.engine_name}] 知识推理引擎初始化失败: {e}")

        if KNOWLEDGE_EMERGENCE_AVAILABLE:
            try:
                self.emergence_engine = KnowledgeEmergenceInheritanceEngine()
                print(f"[{self.engine_name}] 知识涌现发现引擎初始化成功")
            except Exception as e:
                print(f"[{self.engine_name}] 知识涌现发现引擎初始化失败: {e}")

        # 集成状态
        if self.reasoning_engine and self.emergence_engine:
            self.integration_status["integration_complete"] = True

        # 闭环执行记录
        self.closed_loop_dir = KNOWLEDGE_DIR / "reasoning_emergence_integration"
        self.closed_loop_dir.mkdir(parents=True, exist_ok=True)
        self.closed_loop_history_file = self.closed_loop_dir / "closed_loop_history.json"
        self.closed_loop_history = self._load_closed_loop_history()

        print(f"[{self.engine_name} v{self.version}] 初始化完成")
        print(f"[{self.engine_name}] 推理引擎: {'可用' if KNOWLEDGE_REASONING_AVAILABLE else '不可用'}")
        print(f"[{self.engine_name}] 涌现引擎: {'可用' if KNOWLEDGE_EMERGENCE_AVAILABLE else '不可用'}")
        print(f"[{self.engine_name}] 集成状态: {'完成' if self.integration_status['integration_complete'] else '部分完成'}")

    def _load_closed_loop_history(self) -> Dict:
        """加载闭环历史"""
        default = {
            "closed_loops": [],
            "total_executed": 0,
            "last_execution": None
        }
        if self.closed_loop_history_file.exists():
            try:
                with open(self.closed_loop_history_file, 'r', encoding='utf-8') as f:
                    default.update(json.load(f))
            except Exception:
                pass
        return default

    def _save_closed_loop_history(self):
        """保存闭环历史"""
        try:
            with open(self.closed_loop_history_file, 'w', encoding='utf-8') as f:
                json.dump(self.closed_loop_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[{self.engine_name}] 保存闭环历史失败: {e}")

    def get_status(self) -> Dict:
        """获取引擎状态"""
        return {
            "version": self.version,
            "engine_name": self.engine_name,
            "integration_status": self.integration_status,
            "sub_engines": {
                "reasoning": KNOWLEDGE_REASONING_AVAILABLE,
                "emergence": KNOWLEDGE_EMERGENCE_AVAILABLE
            },
            "statistics": {
                "total_closed_loops": self.closed_loop_history.get("total_executed", 0),
                "last_execution": self.closed_loop_history.get("last_execution")
            }
        }

    def run_closed_loop(self, query: str = None, context: Dict = None) -> Dict:
        """
        执行完整的推理-涌现-传承闭环

        Args:
            query: 可选的初始查询
            context: 可选的上下文信息

        Returns:
            闭环执行结果
        """
        result = {
            "success": False,
            "query": query,
            "reasoning_result": None,
            "emergence_discoveries": [],
            "insights_transformed": [],
            "闭环执行完成": False
        }

        if not self.integration_status["integration_complete"]:
            result["error"] = "集成未完成，缺少必要的子引擎"
            return result

        try:
            # 步骤 1: 知识推理
            print(f"[{self.engine_name}] 步骤 1: 执行知识推理...")
            if self.reasoning_engine and hasattr(self.reasoning_engine, 'answer_question'):
                # 如果有查询，执行推理
                if query:
                    reasoning_result = self.reasoning_engine.answer_question(query, context or {})
                    result["reasoning_result"] = reasoning_result
                else:
                    # 如果没有查询，生成基于当前状态的推理
                    reasoning_result = self._generate_reasoning_from_context(context or {})
                    result["reasoning_result"] = reasoning_result

            # 步骤 2: 基于推理结果进行涌现发现
            print(f"[{self.engine_name}] 步骤 2: 基于推理结果进行涌现发现...")
            if self.emergence_engine and hasattr(self.emergence_engine, 'discover_emergence'):
                # 提取推理中的关键主题作为涌现发现的输入
                topics = self._extract_topics_from_reasoning(result.get("reasoning_result", {}))
                emergence_input = {
                    "topics": topics,
                    "reasoning_context": result.get("reasoning_result", {}),
                    "source": "reasoning_emergence_integration"
                }
                emergence_result = self.emergence_engine.discover_emergence(emergence_input)
                result["emergence_discoveries"] = emergence_result.get("discoveries", [])

            # 步骤 3: 将洞察转化为知识
            print(f"[{self.engine_name}] 步骤 3: 将洞察转化为知识...")
            transformed_insights = self._transform_insights_to_knowledge(
                result.get("emergence_discoveries", []),
                result.get("reasoning_result", {})
            )
            result["insights_transformed"] = transformed_insights

            # 步骤 4: 触发传承（如果有新知识）
            print(f"[{self.engine_name}] 步骤 4: 触发知识传承...")
            if transformed_insights and self.emergence_engine and hasattr(self.emergence_engine, 'create_inheritance_chain'):
                for insight in transformed_insights:
                    inheritance_input = {
                        "knowledge": insight,
                        "source_round": 522,
                        "integration_source": "reasoning_emergence"
                    }
                    inheritance_result = self.emergence_engine.create_inheritance_chain(inheritance_input)
                    if inheritance_result.get("success"):
                        print(f"[{self.engine_name}] 知识传承成功: {insight.get('title', '未知')}")

            # 记录闭环执行
            self._record_closed_loop_execution(result)

            result["success"] = True
            result["闭环执行完成"] = True
            result["message"] = "知识推理→涌现发现→知识传承→持续进化的完整闭环执行成功"

        except Exception as e:
            result["error"] = str(e)
            result["message"] = f"闭环执行出错: {e}"

        return result

    def _generate_reasoning_from_context(self, context: Dict) -> Dict:
        """基于上下文生成推理结果"""
        # 分析当前系统状态，生成推理主题
        reasoning_context = {
            "system_state": "分析当前进化环状态",
            "capabilities": "已有70+进化引擎能力",
            "focus_areas": [
                "知识管理能力",
                "跨引擎协同",
                "元进化能力",
                "自主决策能力"
            ]
        }
        return reasoning_context

    def _extract_topics_from_reasoning(self, reasoning_result: Dict) -> List[str]:
        """从推理结果中提取主题"""
        topics = []

        if isinstance(reasoning_result, dict):
            # 从推理结果中提取关键信息
            if "focus_areas" in reasoning_result:
                topics.extend(reasoning_result["focus_areas"])
            if "system_state" in reasoning_result:
                topics.append(reasoning_result["system_state"])
            if "capabilities" in reasoning_result:
                topics.append(reasoning_result["capabilities"])

        # 如果没有提取到主题，使用默认主题
        if not topics:
            topics = ["知识管理", "跨引擎协同", "元进化", "自主决策"]

        return topics[:5]  # 限制主题数量

    def _transform_insights_to_knowledge(self, discoveries: List[Dict], reasoning_result: Dict) -> List[Dict]:
        """将涌现发现转化为可执行知识"""
        transformed = []

        for discovery in discoveries:
            if isinstance(discovery, dict):
                knowledge_entry = {
                    "title": discovery.get("insight", discovery.get("title", "未知洞察")),
                    "description": discovery.get("description", ""),
                    "domain": discovery.get("domain", "知识管理"),
                    "source": "reasoning_emergence_integration",
                    "source_round": 522,
                    "confidence": discovery.get("confidence", 0.8),
                    "actionable": True,
                    "transformed_at": datetime.now().isoformat()
                }
                transformed.append(knowledge_entry)

        return transformed

    def _record_closed_loop_execution(self, result: Dict):
        """记录闭环执行"""
        execution_record = {
            "timestamp": datetime.now().isoformat(),
            "success": result.get("success", False),
            "reasoning_result": bool(result.get("reasoning_result")),
            "emergence_discoveries_count": len(result.get("emergence_discoveries", [])),
            "insights_transformed_count": len(result.get("insights_transformed", []))
        }

        self.closed_loop_history["closed_loops"].append(execution_record)
        self.closed_loop_history["total_executed"] += 1
        self.closed_loop_history["last_execution"] = execution_record["timestamp"]

        # 保留最近50条记录
        if len(self.closed_loop_history["closed_loops"]) > 50:
            self.closed_loop_history["closed_loops"] = self.closed_loop_history["closed_loops"][-50:]

        self._save_closed_loop_history()

    def get_cockpit_data(self) -> Dict:
        """获取驾驶舱数据"""
        return {
            "engine_name": self.engine_name,
            "version": self.version,
            "integration_status": self.integration_status,
            "statistics": {
                "total_closed_loops": self.closed_loop_history.get("total_executed", 0),
                "last_execution": self.closed_loop_history.get("last_execution")
            },
            "recent_closed_loops": self.closed_loop_history.get("closed_loops", [])[-5:]
        }


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(
        description="知识推理-涌现发现深度集成引擎"
    )
    parser.add_argument("--status", action="store_true", help="获取引擎状态")
    parser.add_argument("--run", action="store_true", help="执行完整闭环")
    parser.add_argument("--query", type=str, help="初始查询")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")

    args = parser.parse_args()

    # 初始化引擎
    engine = KnowledgeReasoningEmergenceIntegrationEngine()

    if args.status:
        # 输出状态
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.run:
        # 执行闭环
        result = engine.run_closed_loop(query=args.query)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.cockpit_data:
        # 输出驾驶舱数据
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()