#!/usr/bin/env python3
"""
智能全场景进化知识图谱推理与元优化深度集成引擎
Evolution Knowledge Graph Reasoning & Meta-Optimization Deep Integration Engine

将 round 298 的知识图谱推理引擎与 round 297 的元优化引擎深度集成，
形成"图谱推理→优化建议→自动执行→验证"的完整元进化闭环。

让系统能够利用知识图谱的深度推理能力来驱动元优化决策，
实现从"图谱发现机会"到"自动优化执行"的完整闭环。

Version: 1.0.0
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# 添加脚本目录到路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

try:
    from evolution_knowledge_graph_reasoning import EvolutionKnowledgeGraphReasoning
except ImportError:
    EvolutionKnowledgeGraphReasoning = None

try:
    from evolution_meta_optimizer import EvolutionMetaOptimizer
except ImportError:
    EvolutionMetaOptimizer = None


def _safe_print(text: str):
    """安全打印，支持 UTF-8"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore'))


class EvolutionKGMetaIntegration:
    """
    进化知识图谱推理与元优化深度集成引擎

    实现功能：
    1. 知识图谱推理机会获取 - 从图谱引擎获取隐藏的优化机会和创新模式
    2. 优化建议智能转换 - 将图谱发现的机会转化为元优化引擎可执行的策略调整
    3. 自动优化执行 - 自动应用优化建议到进化策略
    4. 闭环验证 - 验证优化效果并反馈到知识图谱
    5. 统一状态追踪 - 追踪整个闭环流程的状态
    """

    def __init__(self):
        """初始化深度集成引擎"""
        self.kg_engine = None
        self.meta_optimizer = None
        self.integration_status = {
            "kg_engine_loaded": False,
            "meta_optimizer_loaded": False,
            "last_integration_time": None,
            "total闭环_executions": 0,
            "successful_optimizations": 0,
            "failed_optimizations": 0,
            "last_opportunity_count": 0,
            "last_optimization_count": 0
        }
        self._load_engines()

    def _load_engines(self):
        """加载知识图谱推理引擎和元优化引擎"""
        # 加载知识图谱推理引擎
        if EvolutionKnowledgeGraphReasoning:
            try:
                self.kg_engine = EvolutionKnowledgeGraphReasoning()
                self.integration_status["kg_engine_loaded"] = True
                _safe_print("[集成引擎] 知识图谱推理引擎加载成功")
            except Exception as e:
                _safe_print(f"[集成引擎] 知识图谱推理引擎加载失败: {e}")
        else:
            _safe_print("[集成引擎] 无法导入知识图谱推理引擎")

        # 加载元优化引擎
        if EvolutionMetaOptimizer:
            try:
                self.meta_optimizer = EvolutionMetaOptimizer()
                self.integration_status["meta_optimizer_loaded"] = True
                _safe_print("[集成引擎] 元优化引擎加载成功")
            except Exception as e:
                _safe_print(f"[集成引擎] 元优化引擎加载失败: {e}")
        else:
            _safe_print("[集成引擎] 无法导入元优化引擎")

    def get_kg_opportunities(self) -> List[Dict[str, Any]]:
        """
        从知识图谱推理引擎获取隐藏的优化机会

        Returns:
            优化机会列表
        """
        if not self.kg_engine:
            _safe_print("[错误] 知识图谱推理引擎未加载")
            return []

        try:
            # 使用知识图谱推理引擎发现隐藏机会
            opportunities = self.kg_engine.discover_hidden_opportunities()

            # 过滤出与优化相关的机会
            optimization_opportunities = []
            for opp in opportunities:
                # 根据机会类型和描述筛选可能对优化有帮助的机会
                if any(keyword in opp.get("type", "").lower() for keyword in
                       ["重复", "低效", "优化", "改进", "incomplete", "inefficient", "pattern"]):
                    optimization_opportunities.append(opp)

            # 也获取创新模式
            innovation_patterns = self.kg_engine.identify_innovation_patterns()
            for pattern in innovation_patterns:
                if pattern.get("pattern_type") == "首创性" or pattern.get("pattern_type") == "深层增强":
                    optimization_opportunities.append({
                        "type": "创新机会",
                        "description": f"基于创新模式: {pattern.get('description', '')}",
                        "source": "innovation_pattern",
                        "pattern": pattern
                    })

            self.integration_status["last_opportunity_count"] = len(optimization_opportunities)
            return optimization_opportunities

        except Exception as e:
            _safe_print(f"[错误] 获取知识图谱优化机会失败: {e}")
            return []

    def convert_opportunities_to_adjustments(self, opportunities: List[Dict]) -> List[Dict]:
        """
        将知识图谱发现的优化机会转化为元优化引擎可执行的策略调整

        Args:
            opportunities: 知识图谱发现的优化机会

        Returns:
            策略调整建议列表
        """
        if not self.meta_optimizer:
            _safe_print("[错误] 元优化引擎未加载")
            return []

        adjustments = []

        # 加载效率分析结果
        try:
            efficiency_analysis = self.meta_optimizer.load_efficiency_analysis()
            strategy_performance = self.meta_optimizer.analyze_strategy_performance()
        except Exception as e:
            _safe_print(f"[警告] 加载效率分析失败: {e}")
            efficiency_analysis = {}
            strategy_performance = {}

        # 根据知识图谱机会生成策略调整
        for opp in opportunities:
            adjustment = {
                "source": "知识图谱推理",
                "opportunity_type": opp.get("type", "未知"),
                "description": opp.get("description", ""),
                "reason": "",
                "suggested_actions": []
            }

            # 根据机会类型生成具体的调整建议
            opp_type = opp.get("type", "")

            if "重复" in opp_type or "重复" in opp.get("description", ""):
                adjustment["reason"] = "检测到重复进化领域，需要策略调整避免重复"
                adjustment["suggested_actions"] = [
                    {"action": "增加领域多样性权重", "priority": "高"},
                    {"action": "优先探索新领域", "priority": "高"},
                    {"action": "降低重复领域优先级", "priority": "中"}
                ]
            elif "低效" in opp_type or "低效" in opp.get("description", ""):
                adjustment["reason"] = "检测到低效进化模式，需要优化执行策略"
                adjustment["suggested_actions"] = [
                    {"action": "优化执行参数", "priority": "高"},
                    {"action": "调整超时设置", "priority": "中"},
                    {"action": "改进资源分配", "priority": "中"}
                ]
            elif "创新" in opp_type or "创新机会" in opp_type:
                adjustment["reason"] = "发现创新机会，需要增强创新能力"
                adjustment["suggested_actions"] = [
                    {"action": "提高创新引擎权重", "priority": "高"},
                    {"action": "增加创新探索预算", "priority": "中"}
                ]
            elif "未探索" in opp_type or "incomplete" in opp_type.lower():
                adjustment["reason"] = "发现未探索领域，需要扩展进化范围"
                adjustment["suggested_actions"] = [
                    {"action": "探索新领域", "priority": "高"},
                    {"action": "增加能力覆盖", "priority": "中"}
                ]
            else:
                # 通用调整建议
                adjustment["reason"] = f"知识图谱发现优化机会: {opp.get('description', '')}"
                adjustment["suggested_actions"] = [
                    {"action": "评估并应用优化建议", "priority": "中"}
                ]

            # 添加效率分析数据作为参考
            if efficiency_analysis:
                adjustment["efficiency_data"] = {
                    "avg_completion_time": efficiency_analysis.get("avg_completion_time", 0),
                    "success_rate": efficiency_analysis.get("success_rate", 0)
                }

            adjustments.append(adjustment)

        return adjustments

    def execute_optimization闭环(self) -> Dict[str, Any]:
        """
        执行完整的"图谱推理→优化建议→自动执行→验证"闭环

        Returns:
            闭环执行结果
        """
        result = {
            "status": "started",
            "steps_completed": [],
            "opportunities_found": 0,
            "adjustments_generated": 0,
            "optimizations_applied": 0,
            "verification_passed": False,
            "errors": []
        }

        self.integration_status["last_integration_time"] = datetime.now().isoformat()

        # 步骤1: 从知识图谱获取优化机会
        _safe_print("\n[闭环] 步骤1: 从知识图谱推理引擎获取优化机会...")
        try:
            opportunities = self.get_kg_opportunities()
            result["opportunities_found"] = len(opportunities)
            result["steps_completed"].append("kg_opportunity_discovery")
            _safe_print(f"[闭环] 发现 {len(opportunities)} 个优化机会")
        except Exception as e:
            result["errors"].append(f"知识图谱机会获取失败: {e}")
            _safe_print(f"[错误] 知识图谱机会获取失败: {e}")
            result["status"] = "failed"
            return result

        if not opportunities:
            result["status"] = "no_opportunities"
            result["message"] = "知识图谱未发现新的优化机会"
            return result

        # 步骤2: 将机会转化为策略调整
        _safe_print("\n[闭环] 步骤2: 将优化机会转化为策略调整...")
        try:
            adjustments = self.convert_opportunities_to_adjustments(opportunities)
            result["adjustments_generated"] = len(adjustments)
            result["steps_completed"].append("adjustment_generation")
            _safe_print(f"[闭环] 生成了 {len(adjustments)} 个策略调整建议")
        except Exception as e:
            result["errors"].append(f"策略调整生成失败: {e}")
            _safe_print(f"[错误] 策略调整生成失败: {e}")
            result["status"] = "failed"
            return result

        if not adjustments:
            result["status"] = "no_adjustments"
            return result

        # 步骤3: 自动执行优化
        _safe_print("\n[闭环] 步骤3: 自动执行优化...")
        try:
            if self.meta_optimizer:
                # 使用元优化引擎应用调整
                apply_result = self.meta_optimizer.apply_optimization(adjustments)
                result["optimization_result"] = apply_result
                result["optimizations_applied"] = len(adjustments)
                result["steps_completed"].append("optimization_execution")
                _safe_print(f"[闭环] 已应用 {len(adjustments)} 个优化调整")
            else:
                result["errors"].append("元优化引擎未加载")
                result["status"] = "failed"
                return result
        except Exception as e:
            result["errors"].append(f"优化执行失败: {e}")
            _safe_print(f"[错误] 优化执行失败: {e}")
            result["status"] = "failed"
            return result

        # 步骤4: 验证优化效果
        _safe_print("\n[闭环] 步骤4: 验证优化效果...")
        try:
            if self.meta_optimizer:
                verification = self.meta_optimizer.verify_optimization()
                result["verification"] = verification
                result["verification_passed"] = verification.get("status") == "success"
                result["steps_completed"].append("verification")
                _safe_print(f"[闭环] 验证完成: {verification.get('status', 'unknown')}")
        except Exception as e:
            result["errors"].append(f"验证失败: {e}")
            _safe_print(f"[警告] 验证失败: {e}")

        # 更新集成状态
        self.integration_status["total闭环_executions"] += 1
        if result["verification_passed"]:
            self.integration_status["successful_optimizations"] += 1
            result["status"] = "success"
        else:
            self.integration_status["failed_optimizations"] += 1
            if result["status"] != "failed":
                result["status"] = "partial_success"

        result["last_execution_time"] = datetime.now().isoformat()

        _safe_print(f"\n[闭环] 执行完成: {result['status']}")
        _safe_print(f"[闭环] 机会: {result['opportunities_found']}, 调整: {result['adjustments_generated']}, "
                   f"应用: {result['optimizations_applied']}, 验证: {'通过' if result['verification_passed'] else '未通过'}")

        return result

    def get_status(self) -> Dict[str, Any]:
        """
        获取集成引擎状态

        Returns:
            状态信息字典
        """
        status = {
            "integration_status": self.integration_status.copy(),
            "kg_engine_available": self.kg_engine is not None,
            "meta_optimizer_available": self.meta_optimizer is not None,
            "both_engines_loaded": self.integration_status["kg_engine_loaded"] and
                                  self.integration_status["meta_optimizer_loaded"]
        }

        # 如果两个引擎都加载了，获取它们的状态
        if self.kg_engine:
            try:
                kg_status = self.kg_engine.get_status()
                status["kg_engine_status"] = {
                    "node_count": kg_status.get("node_count", 0),
                    "edge_count": kg_status.get("edge_count", 0),
                    "last_analysis": kg_status.get("last_analysis_time", "unknown")
                }
            except Exception as e:
                status["kg_engine_status"] = {"error": str(e)}

        if self.meta_optimizer:
            try:
                meta_status = self.meta_optimizer.get_status()
                status["meta_optimizer_status"] = {
                    "total_optimizations": meta_status.get("total_optimizations", 0),
                    "last_optimization": meta_status.get("last_optimization_time", "unknown")
                }
            except Exception as e:
                status["meta_optimizer_status"] = {"error": str(e)}

        return status

    def run_deep_analysis(self) -> Dict[str, Any]:
        """
        运行深度分析：先做知识图谱推理，再基于结果做元优化

        Returns:
            深度分析结果
        """
        result = {
            "analysis_type": "kg_meta_deep_integration",
            "kg_analysis": None,
            "meta_analysis": None,
            "integration_insights": []
        }

        # 知识图谱深度分析
        if self.kg_engine:
            _safe_print("[深度分析] 运行知识图谱推理分析...")
            try:
                kg_result = self.kg_engine.run_full_analysis()
                result["kg_analysis"] = {
                    "opportunities": kg_result.get("hidden_opportunities", []),
                    "innovation_patterns": kg_result.get("innovation_patterns", []),
                    "analysis_complete": True
                }

                # 从图谱分析中提取洞察
                for opp in kg_result.get("hidden_opportunities", [])[:3]:
                    result["integration_insights"].append({
                        "type": "图谱机会",
                        "insight": opp.get("description", ""),
                        "priority": opp.get("priority", "中")
                    })
            except Exception as e:
                _safe_print(f"[警告] 知识图谱分析失败: {e}")
                result["kg_analysis"] = {"error": str(e)}

        # 元优化分析
        if self.meta_optimizer:
            _safe_print("[深度分析] 运行元优化分析...")
            try:
                efficiency = self.meta_optimizer.load_efficiency_analysis()
                performance = self.meta_optimizer.analyze_strategy_performance()

                result["meta_analysis"] = {
                    "efficiency": efficiency,
                    "performance": performance,
                    "analysis_complete": True
                }

                # 从元优化分析中提取洞察
                if performance.get("underperforming_strategies"):
                    result["integration_insights"].append({
                        "type": "元优化洞察",
                        "insight": f"发现 {len(performance.get('underperforming_strategies', []))} 个低效策略",
                        "priority": "高"
                    })
            except Exception as e:
                _safe_print(f"[警告] 元优化分析失败: {e}")
                result["meta_analysis"] = {"error": str(e)}

        return result


def main():
    """主函数：处理命令行参数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能全场景进化知识图谱推理与元优化深度集成引擎"
    )
    parser.add_argument("command", nargs="?", default="status",
                       help="命令: status, integrate, analyze, opportunities, help")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="详细输出")

    args = parser.parse_args()
    args.command = args.command.lower()

    engine = EvolutionKGMetaIntegration()

    if args.command == "status":
        _safe_print("\n=== 进化知识图谱推理与元优化深度集成引擎 ===\n")
        status = engine.get_status()

        _safe_print("集成状态:")
        _safe_print(f"  知识图谱引擎加载: {'是' if status['kg_engine_available'] else '否'}")
        _safe_print(f"  元优化引擎加载: {'是' if status['meta_optimizer_available'] else '否'}")
        _safe_print(f"  双引擎深度集成: {'是' if status['both_engines_loaded'] else '否'}")
        _safe_print(f"  总闭环执行次数: {status['integration_status']['total闭环_executions']}")
        _safe_print(f"  成功优化次数: {status['integration_status']['successful_optimizations']}")
        _safe_print(f"  失败优化次数: {status['integration_status']['failed_optimizations']}")

        if status.get("kg_engine_status") and not status["kg_engine_status"].get("error"):
            _safe_print("\n知识图谱引擎状态:")
            _safe_print(f"  节点数: {status['kg_engine_status'].get('node_count', 0)}")
            _safe_print(f"  边数: {status['kg_engine_status'].get('edge_count', 0)}")

        if status.get("meta_optimizer_status") and not status["meta_optimizer_status"].get("error"):
            _safe_print("\n元优化引擎状态:")
            _safe_print(f"  总优化次数: {status['meta_optimizer_status'].get('total_optimizations', 0)}")

    elif args.command == "integrate" or args.command == "闭环":
        _safe_print("\n=== 执行图谱推理与元优化深度集成闭环 ===\n")
        result = engine.execute_optimization闭环()

        _safe_print("\n闭环执行结果:")
        _safe_print(f"  状态: {result['status']}")
        _safe_print(f"  发现机会: {result['opportunities_found']}")
        _safe_print(f"  生成调整: {result['adjustments_generated']}")
        _safe_print(f"  应用优化: {result['optimizations_applied']}")
        _safe_print(f"  验证通过: {'是' if result['verification_passed'] else '否'}")

        if result.get("errors"):
            _safe_print(f"  错误: {result['errors']}")

    elif args.command == "analyze" or args.command == "分析":
        _safe_print("\n=== 运行深度分析 ===\n")
        result = engine.run_deep_analysis()

        _safe_print("\n深度分析结果:")
        _safe_print(f"  分析类型: {result['analysis_type']}")

        if result.get("kg_analysis") and result["kg_analysis"].get("analysis_complete"):
            _safe_print(f"  知识图谱分析: 完成")
            _safe_print(f"    机会数: {len(result['kg_analysis'].get('opportunities', []))}")
            _safe_print(f"    创新模式数: {len(result['kg_analysis'].get('innovation_patterns', []))}")

        if result.get("meta_analysis") and result["meta_analysis"].get("analysis_complete"):
            _safe_print(f"  元优化分析: 完成")

        _safe_print(f"\n集成洞察 ({len(result['integration_insights'])} 条):")
        for i, insight in enumerate(result["integration_insights"], 1):
            _safe_print(f"  {i}. [{insight['type']}] {insight['insight']} (优先级: {insight['priority']})")

    elif args.command == "opportunities" or args.command == "机会":
        _safe_print("\n=== 获取知识图谱优化机会 ===\n")
        opportunities = engine.get_kg_opportunities()

        _safe_print(f"发现 {len(opportunities)} 个优化机会:\n")
        for i, opp in enumerate(opportunities, 1):
            _safe_print(f"{i}. [{opp.get('type', '未知类型')}]")
            _safe_print(f"   描述: {opp.get('description', '无')}")
            _safe_print(f"   优先级: {opp.get('priority', '中')}")
            _safe_print("")

    elif args.command == "help" or args.command == "?":
        _safe_print("""
智能全场景进化知识图谱推理与元优化深度集成引擎

命令:
  status          - 查看集成引擎状态
  integrate/闭环  - 执行完整的图谱推理→优化建议→自动执行→验证闭环
  analyze/分析    - 运行深度分析（知识图谱+元优化）
  opportunities/机会 - 获取知识图谱优化机会
  help            - 显示帮助信息

示例:
  python evolution_kg_meta_integration.py status
  python evolution_kg_meta_integration.py integrate
  python evolution_kg_meta_integration.py analyze
        """)
    else:
        _safe_print(f"未知命令: {args.command}")
        _safe_print("使用 'help' 查看可用命令")


if __name__ == "__main__":
    main()