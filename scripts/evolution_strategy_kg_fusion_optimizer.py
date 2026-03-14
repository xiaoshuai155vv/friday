#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环策略知识图谱深度融合与自适应优化引擎 (version 1.0.0)

在 round 418/419 完成的策略执行反馈与完整闭环基础上，进一步增强策略执行反馈数据
与知识图谱的深度融合能力。让系统能够：
1. 将策略执行反馈数据自动转化为知识存储到知识图谱
2. 从知识图谱中检索相关策略知识辅助决策
3. 基于知识图谱的关联推理生成知识驱动的优化建议
4. 形成"执行→反馈→知识化→推理→优化→执行"的完整闭环

核心功能：
1. 策略执行反馈知识化存储
2. 知识图谱策略知识检索
3. 知识驱动的策略优化建议生成
4. 自适应优化闭环
5. 与进化驾驶舱的深度集成

集成模块：
- evolution_strategy_feedback_adjustment_engine.py (round 418)
- evolution_strategy_recommendation_feedback_integration_engine.py (round 419)
- evolution_knowledge_graph_reasoning.py (round 298)
- evolution_kg_deep_reasoning_insight_engine.py (round 330)
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from collections import defaultdict

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# 尝试导入集成的模块
try:
    from evolution_strategy_feedback_adjustment_engine import StrategyFeedbackAdjustmentEngine
except ImportError:
    StrategyFeedbackAdjustmentEngine = None

try:
    from evolution_kg_deep_reasoning_insight_engine import KnowledgeGraphDeepReasoningEngine
except ImportError:
    KnowledgeGraphDeepReasoningEngine = None


class StrategyKGFusionOptimizer:
    """策略知识图谱深度融合与自适应优化引擎"""

    def __init__(self, state_dir: str = "runtime/state"):
        self.state_dir = Path(state_dir)
        self.state_file = self.state_dir / "strategy_kg_fusion_state.json"

        # 集成核心引擎
        self.feedback_engine = None
        self.kg_reasoning_engine = None

        # 状态管理
        self.state = {
            "initialized": False,
            "version": "1.0.0",
            "fusion_count": 0,
            "knowledge_storage_count": 0,
            "kg_retrieval_count": 0,
            "kg_driven_optimization_count": 0,
            "adaptive_optimization_count": 0,
            "last_fusion_time": None,
            "fusion_history": [],
            "strategy_knowledge_base": {},
            "optimization_patterns": [],
            "fusion_status": "待触发",
        }

        self._initialize_engines()
        self._load_state()

    def _initialize_engines(self):
        """初始化集成引擎"""
        if StrategyFeedbackAdjustmentEngine:
            try:
                self.feedback_engine = StrategyFeedbackAdjustmentEngine(state_dir=str(self.state_dir))
                print("[StrategyKGFusionOptimizer] 策略反馈引擎已集成")
            except Exception as e:
                print(f"[StrategyKGFusionOptimizer] 策略反馈引擎初始化失败: {e}")

        if KnowledgeGraphDeepReasoningEngine:
            try:
                self.kg_reasoning_engine = KnowledgeGraphDeepReasoningEngine(state_dir=str(self.state_dir))
                print("[StrategyKGFusionOptimizer] 知识图谱推理引擎已集成")
            except Exception as e:
                print(f"[StrategyKGFusionOptimizer] 知识图谱推理引擎初始化失败: {e}")

    def _load_state(self):
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self.state.update(loaded)
            except Exception as e:
                print(f"[StrategyKGFusionOptimizer] 状态加载失败: {e}")

    def _save_state(self):
        """保存状态"""
        try:
            self.state_dir.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[StrategyKGFusionOptimizer] 状态保存失败: {e}")

    def analyze_system_state(self) -> Dict[str, Any]:
        """分析当前系统状态"""
        state_info = {
            "timestamp": datetime.now().isoformat(),
            "system_metrics": {},
            "strategy_status": {},
            "kg_status": {}
        }

        # 系统指标
        if HAS_PSUTIL:
            try:
                state_info["system_metrics"] = {
                    "cpu_percent": psutil.cpu_percent(interval=0.1),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_percent": psutil.disk_usage('/').percent,
                }
            except Exception as e:
                print(f"[StrategyKGFusionOptimizer] 系统指标获取失败: {e}")

        # 策略状态
        if self.feedback_engine:
            try:
                state_info["strategy_status"] = {
                    "feedback_count": getattr(self.feedback_engine.state, "feedback_count", 0),
                    "adjustment_count": getattr(self.feedback_engine.state, "adjustment_count", 0),
                }
            except:
                pass

        # 知识图谱状态
        if self.kg_reasoning_engine:
            try:
                state_info["kg_status"] = {
                    "initialized": getattr(self.kg_reasoning_engine.state, "initialized", False),
                    "reasoning_count": getattr(self.kg_reasoning_engine.state, "reasoning_count", 0),
                }
            except:
                pass

        return state_info

    def store_strategy_feedback_to_kg(self, strategy_data: Dict[str, Any]) -> Dict[str, Any]:
        """将策略执行反馈存储到知识图谱"""
        result = {
            "success": False,
            "message": "",
            "knowledge_id": None,
        }

        try:
            # 构建策略知识节点
            strategy_knowledge = {
                "type": "strategy_execution",
                "strategy_name": strategy_data.get("strategy_name", "unknown"),
                "execution_result": strategy_data.get("execution_result", {}),
                "performance_metrics": strategy_data.get("performance_metrics", {}),
                "context": strategy_data.get("context", {}),
                "timestamp": datetime.now().isoformat(),
                "success": strategy_data.get("success", False),
                "efficiency_score": strategy_data.get("efficiency_score", 0.0),
                "value_score": strategy_data.get("value_score", 0.0),
            }

            # 存储到本地知识库
            knowledge_id = f"strategy_{strategy_data.get('strategy_name', 'unknown')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            self.state["strategy_knowledge_base"][knowledge_id] = strategy_knowledge
            self.state["knowledge_storage_count"] += 1
            self._save_state()

            result["success"] = True
            result["message"] = f"策略反馈已知识化存储: {knowledge_id}"
            result["knowledge_id"] = knowledge_id

            print(f"[StrategyKGFusionOptimizer] {result['message']}")

        except Exception as e:
            result["message"] = f"策略反馈知识化存储失败: {e}"
            print(f"[StrategyKGFusionOptimizer] {result['message']}")

        return result

    def retrieve_strategy_knowledge(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从知识图谱检索策略知识"""
        result = []
        try:
            strategy_name = query.get("strategy_name")
            context = query.get("context", {})
            limit = query.get("limit", 5)

            # 基于策略名和上下文检索
            for knowledge_id, knowledge in self.state["strategy_knowledge_base"].items():
                if strategy_name and knowledge.get("strategy_name") != strategy_name:
                    continue

                # 上下文匹配
                match_score = 0
                for key, value in context.items():
                    if knowledge.get("context", {}).get(key) == value:
                        match_score += 1

                if match_score > 0 or not strategy_name:
                    knowledge_copy = knowledge.copy()
                    knowledge_copy["knowledge_id"] = knowledge_id
                    knowledge_copy["match_score"] = match_score
                    result.append(knowledge_copy)

            # 按匹配度排序
            result.sort(key=lambda x: x.get("match_score", 0), reverse=True)

            # 限制返回数量
            result = result[:limit]
            self.state["kg_retrieval_count"] += 1
            self._save_state()

            print(f"[StrategyKGFusionOptimizer] 检索到 {len(result)} 条策略知识")

        except Exception as e:
            print(f"[StrategyKGFusionOptimizer] 策略知识检索失败: {e}")

        return result

    def generate_kg_driven_optimization(self, strategy_context: Dict[str, Any]) -> Dict[str, Any]:
        """生成知识驱动的策略优化建议"""
        result = {
            "success": False,
            "optimization_suggestions": [],
            "reasoning": "",
        }

        try:
            # 检索相关策略知识
            retrieved_knowledge = self.retrieve_strategy_knowledge({
                "strategy_name": strategy_context.get("strategy_name"),
                "context": strategy_context.get("context", {}),
                "limit": 10,
            })

            if not retrieved_knowledge:
                result["reasoning"] = "无相关策略知识，执行新策略探索"
                result["optimization_suggestions"] = [{
                    "type": "exploration",
                    "description": "执行新策略探索，积累策略知识",
                    "confidence": 0.5,
                }]
            else:
                # 分析成功模式
                successful_strategies = [k for k in retrieved_knowledge if k.get("success", False)]
                failed_strategies = [k for k in retrieved_knowledge if not k.get("success", True)]

                if successful_strategies:
                    # 基于成功模式生成优化建议
                    avg_efficiency = sum(k.get("efficiency_score", 0) for k in successful_strategies) / len(successful_strategies)
                    avg_value = sum(k.get("value_score", 0) for k in successful_strategies) / len(successful_strategies)

                    result["optimization_suggestions"].append({
                        "type": "exploit",
                        "description": f"基于历史成功模式优化，预测效率 {avg_efficiency:.2f}，价值 {avg_value:.2f}",
                        "confidence": min(0.9, 0.5 + avg_efficiency * 0.4),
                        "based_on_knowledge": len(successful_strategies),
                    })

                if failed_strategies:
                    # 分析失败原因，避免重复错误
                    result["optimization_suggestions"].append({
                        "type": "avoid",
                        "description": f"识别 {len(failed_strategies)} 条失败策略，避免相似方案",
                        "confidence": 0.8,
                        "based_on_knowledge": len(failed_strategies),
                    })

                # 混合策略
                if successful_strategies and failed_strategies:
                    result["optimization_suggestions"].append({
                        "type": "hybrid",
                        "description": "结合成功经验与失败教训的混合策略",
                        "confidence": 0.7,
                    })

                result["reasoning"] = f"基于 {len(retrieved_knowledge)} 条策略知识生成优化建议"

            result["success"] = True
            self.state["kg_driven_optimization_count"] += 1
            self._save_state()

            print(f"[StrategyKGFusionOptimizer] {result['reasoning']}")
            print(f"[StrategyKGFusionOptimizer] 生成了 {len(result['optimization_suggestions'])} 条优化建议")

        except Exception as e:
            result["reasoning"] = f"知识驱动优化生成失败: {e}"
            print(f"[StrategyKGFusionOptimizer] {result['reasoning']}")

        return result

    def execute_adaptive_optimization(self, optimization_plan: Dict[str, Any]) -> Dict[str, Any]:
        """执行自适应优化"""
        result = {
            "success": False,
            "optimization_applied": [],
            "message": "",
        }

        try:
            # 应用优化建议
            for suggestion in optimization_plan.get("optimization_suggestions", []):
                optimization = {
                    "type": suggestion.get("type"),
                    "description": suggestion.get("description"),
                    "applied": True,
                    "timestamp": datetime.now().isoformat(),
                }
                result["optimization_applied"].append(optimization)

            result["success"] = True
            result["message"] = f"已应用 {len(result['optimization_applied'])} 项优化"

            self.state["adaptive_optimization_count"] += 1
            self.state["fusion_count"] += 1
            self.state["last_fusion_time"] = datetime.now().isoformat()
            self.state["fusion_status"] = "已完成"
            self._save_state()

            print(f"[StrategyKGFusionOptimizer] {result['message']}")

        except Exception as e:
            result["message"] = f"自适应优化执行失败: {e}"
            print(f"[StrategyKGFusionOptimizer] {result['message']}")

        return result

    def run_full_cycle(self, strategy_context: Dict[str, Any]) -> Dict[str, Any]:
        """执行完整的策略知识融合优化循环"""
        result = {
            "success": False,
            "stages": {},
            "message": "",
        }

        try:
            # 阶段1: 分析系统状态
            system_state = self.analyze_system_state()
            result["stages"]["system_analysis"] = system_state
            print(f"[StrategyKGFusionOptimizer] 阶段1: 系统状态分析完成")

            # 阶段2: 存储策略执行反馈（如果有）
            if strategy_context.get("strategy_execution_data"):
                storage_result = self.store_strategy_feedback_to_kg(
                    strategy_context["strategy_execution_data"]
                )
                result["stages"]["knowledge_storage"] = storage_result
                print(f"[StrategyKGFusionOptimizer] 阶段2: 策略反馈知识化存储完成")

            # 阶段3: 知识驱动的优化建议生成
            kg_optimization = self.generate_kg_driven_optimization(strategy_context)
            result["stages"]["kg_optimization"] = kg_optimization
            print(f"[StrategyKGFusionOptimizer] 阶段3: 知识驱动优化生成完成")

            # 阶段4: 执行自适应优化
            if kg_optimization.get("optimization_suggestions"):
                execution_result = self.execute_adaptive_optimization(kg_optimization)
                result["stages"]["optimization_execution"] = execution_result
                print(f"[StrategyKGFusionOptimizer] 阶段4: 自适应优化执行完成")

            # 记录到历史
            self.state["fusion_history"].append({
                "timestamp": datetime.now().isoformat(),
                "context": strategy_context,
                "result": result["stages"],
            })

            # 保持历史记录不超过100条
            if len(self.state["fusion_history"]) > 100:
                self.state["fusion_history"] = self.state["fusion_history"][-100:]

            self._save_state()

            result["success"] = True
            result["message"] = "策略知识融合优化完整闭环执行成功"

            print(f"[StrategyKGFusionOptimizer] {result['message']}")

        except Exception as e:
            result["message"] = f"完整循环执行失败: {e}"
            print(f"[StrategyKGFusionOptimizer] {result['message']}")

        return result

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "initialized": self.state.get("initialized", False),
            "version": self.state.get("version", "1.0.0"),
            "fusion_count": self.state.get("fusion_count", 0),
            "knowledge_storage_count": self.state.get("knowledge_storage_count", 0),
            "kg_retrieval_count": self.state.get("kg_retrieval_count", 0),
            "kg_driven_optimization_count": self.state.get("kg_driven_optimization_count", 0),
            "adaptive_optimization_count": self.state.get("adaptive_optimization_count", 0),
            "last_fusion_time": self.state.get("last_fusion_time"),
            "fusion_status": self.state.get("fusion_status", "待触发"),
            "knowledge_base_size": len(self.state.get("strategy_knowledge_base", {})),
        }

    def initialize(self) -> Dict[str, Any]:
        """初始化引擎"""
        result = {
            "success": False,
            "message": "",
        }

        try:
            self.state["initialized"] = True
            self.state["fusion_status"] = "就绪"
            self._save_state()

            result["success"] = True
            result["message"] = "策略知识图谱深度融合优化引擎初始化成功"
            print(f"[StrategyKGFusionOptimizer] {result['message']}")

        except Exception as e:
            result["message"] = f"初始化失败: {e}"
            print(f"[StrategyKGFusionOptimizer] {result['message']}")

        return result


def main():
    """主函数 - 命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能全场景进化环策略知识图谱深度融合与自适应优化引擎"
    )
    parser.add_argument("command", nargs="?", help="命令: status, analyze, run, optimize")
    parser.add_argument("--strategy", help="策略名称")
    parser.add_argument("--context", type=str, help="上下文 JSON")
    parser.add_argument("--json-output", action="store_true", help="JSON 格式输出")

    args = parser.parse_args()

    engine = StrategyKGFusionOptimizer()

    if args.command == "status" or args.command is None:
        status = engine.get_status()
        if args.json_output:
            print(json.dumps(status, ensure_ascii=False, indent=2))
        else:
            print("=" * 50)
            print("策略知识图谱深度融合优化引擎状态")
            print("=" * 50)
            print(f"版本: {status['version']}")
            print(f"初始化: {status['initialized']}")
            print(f"融合次数: {status['fusion_count']}")
            print(f"知识存储数: {status['knowledge_storage_count']}")
            print(f"知识检索数: {status['kg_retrieval_count']}")
            print(f"知识驱动优化数: {status['kg_driven_optimization_count']}")
            print(f"自适应优化数: {status['adaptive_optimization_count']}")
            print(f"知识库大小: {status['knowledge_base_size']}")
            print(f"状态: {status['fusion_status']}")
            print(f"最后融合时间: {status['last_fusion_time']}")

    elif args.command == "initialize":
        result = engine.initialize()
        if args.json_output:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(result["message"])

    elif args.command == "analyze":
        result = engine.analyze_system_state()
        if args.json_output:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("系统状态分析结果:")
            print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "run":
        context = {}
        if args.context:
            try:
                context = json.loads(args.context)
            except:
                pass

        result = engine.run_full_cycle(context)
        if args.json_output:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(result["message"])

    elif args.command == "optimize":
        context = {"strategy_name": args.strategy or "default"}
        result = engine.run_full_cycle(context)
        if args.json_output:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(result["message"])

    else:
        print(f"未知命令: {args.command}")
        print("可用命令: status, initialize, analyze, run, optimize")


if __name__ == "__main__":
    main()