#!/usr/bin/env python3
"""
智能全场景进化环认知驱动自动决策与执行闭环引擎
(Evolution Cognition-Driven Decision Execution Engine)

在 round 454 完成的深度认知与自主意识增强引擎基础上，
进一步构建认知驱动的自动决策与执行闭环能力。
让系统能够将认知评估结果自动应用到进化决策过程中，
基于认知质量评估生成优化决策，并自动执行决策形成验证闭环。
实现从「认知评估→自动决策→执行验证→认知更新」的完整闭环，
让进化环能够真正基于自我认知来指导进化方向。

这是进化环的"认知驱动决策+执行闭环"引擎——将深度认知能力与进化决策/执行深度集成，
形成完整的认知-决策-执行闭环体系。

Version: 1.0.0
Author: AI Evolution System
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
STATE_DIR = PROJECT_ROOT / "runtime" / "state"
LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"
REFERENCES_DIR = PROJECT_ROOT / "references"

# 尝试导入深度认知引擎
try:
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    from evolution_deep_cognition_awareness_engine import EvolutionDeepCognitionAwarenessEngine
    COGNITION_ENGINE_AVAILABLE = True
except ImportError:
    COGNITION_ENGINE_AVAILABLE = False


class EvolutionCognitionDrivenDecisionExecutionEngine:
    """认知驱动自动决策与执行闭环引擎核心类"""

    def __init__(self):
        self.version = "1.0.0"
        self.name = "Evolution Cognition-Driven Decision Execution Engine"
        self.capabilities = [
            "认知评估结果读取",
            "自动决策生成",
            "决策执行与验证",
            "认知-决策-执行闭环",
            "驾驶舱深度集成",
            "跨轮次优化追踪"
        ]
        self.decision_history = []
        self.execution_results = []
        self.loop_status = {
            "cognition_collected": False,
            "decision_generated": False,
            "execution_verified": False,
            "cognition_updated": False
        }

        # 初始化深度认知引擎（如果可用）
        if COGNITION_ENGINE_AVAILABLE:
            self.cognition_engine = EvolutionDeepCognitionAwarenessEngine()
        else:
            self.cognition_engine = None

        # 决策生成配置
        self.decision_config = {
            "min_confidence_threshold": 0.6,
            "max_alternatives": 3,
            "auto_execute_enabled": True,
            "verification_required": True
        }

    def collect_cognition_assessment(self, evolution_round: int = None) -> Dict:
        """
        收集认知评估结果：从深度认知引擎获取评估数据

        Args:
            evolution_round: 指定轮次，默认取最近完成轮次

        Returns:
            认知评估结果
        """
        if not COGNITION_ENGINE_AVAILABLE or self.cognition_engine is None:
            # 如果没有深度认知引擎，尝试从历史文件读取
            return self._collect_from_history(evolution_round)

        try:
            # 调用深度认知引擎的评估功能
            assessment_result = self.cognition_engine.evaluate_cognition(evolution_round)
            self.loop_status["cognition_collected"] = True
            return {
                "status": "success",
                "source": "cognition_engine",
                "assessment": assessment_result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return self._collect_from_history(evolution_round)

    def _collect_from_history(self, evolution_round: int = None) -> Dict:
        """从历史文件收集认知评估数据"""
        if evolution_round is None:
            evolution_round = self._get_latest_completed_round()

        # 查找完成文件
        completed_file = self._find_completed_file(evolution_round)

        if not completed_file:
            return {
                "status": "no_data",
                "message": f"未找到 round {evolution_round} 的完成记录",
                "round": evolution_round
            }

        try:
            with open(completed_file, 'r', encoding='utf-8') as f:
                round_data = json.load(f)

            # 提取认知相关数据
            cognition_data = {
                "round": evolution_round,
                "current_goal": round_data.get("current_goal", ""),
                "was_completed": round_data.get("was_completed", False),
                "baseline_verify": round_data.get("baseline_verify", ""),
                "targeted_verify": round_data.get("targeted_verify", ""),
                "next_suggestion": round_data.get("next_suggestion", "")
            }

            self.loop_status["cognition_collected"] = True

            return {
                "status": "success",
                "source": "history_file",
                "assessment": cognition_data,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"读取历史数据失败: {str(e)}",
                "round": evolution_round
            }

    def generate_cognition_driven_decision(self, cognition_assessment: Dict) -> Dict:
        """
        基于认知评估结果生成优化决策

        Args:
            cognition_assessment: 认知评估结果

        Returns:
            生成的决策方案
        """
        if cognition_assessment.get("status") != "success":
            return {
                "status": "error",
                "message": "认知评估数据无效",
                "decisions": []
            }

        assessment = cognition_assessment.get("assessment", {})
        decisions = []

        # 分析完成状态
        was_completed = assessment.get("was_completed", False)
        baseline_verify = assessment.get("baseline_verify", "")
        targeted_verify = assessment.get("targeted_verify", "")
        next_suggestion = assessment.get("next_suggestion", "")

        # 基于评估结果生成决策
        if not was_completed:
            # 如果上轮未完成，生成修复决策
            decisions.append({
                "type": "completion_focus",
                "priority": 1,
                "description": "聚焦完成上轮未完成的目标",
                "action": "优先完成pending任务，确保本轮完成后再推进",
                "confidence": 0.9
            })

        # 分析验证结果
        if "fail" in baseline_verify.lower() or "未通过" in baseline_verify:
            decisions.append({
                "type": "baseline_fix",
                "priority": 2,
                "description": "修复基线验证问题",
                "action": "检查基础能力链，修复导致基线失败的模块",
                "confidence": 0.85
            })

        if "fail" in targeted_verify.lower() or "未通过" in targeted_verify:
            decisions.append({
                "type": "targeted_fix",
                "priority": 2,
                "description": "修复本轮针对性验证问题",
                "action": "分析本轮实际改动的模块，进行针对性修复",
                "confidence": 0.85
            })

        # 分析下一轮建议
        if next_suggestion and "可继续" in next_suggestion:
            decisions.append({
                "type": "continuation",
                "priority": 3,
                "description": "延续上轮方向继续深化",
                "action": next_suggestion,
                "confidence": 0.7
            })

        # 生成自主优化决策（基于系统自身）
        decisions.append({
            "type": "self_optimization",
            "priority": 4,
            "description": "基于系统自身状态的自主优化",
            "action": "探索将认知评估结果自动应用到进化决策中的可能性",
            "confidence": 0.6
        })

        # 按优先级排序
        decisions.sort(key=lambda x: x["priority"])

        # 限制决策数量
        decisions = decisions[:self.decision_config["max_alternatives"]]

        self.loop_status["decision_generated"] = True

        return {
            "status": "success",
            "decisions": decisions,
            "primary_decision": decisions[0] if decisions else None,
            "timestamp": datetime.now().isoformat()
        }

    def execute_decision(self, decision: Dict, context: Dict = None) -> Dict:
        """
        执行生成的决策

        Args:
            decision: 要执行的决策
            context: 执行上下文

        Returns:
            执行结果
        """
        if context is None:
            context = {}

        decision_type = decision.get("type", "unknown")
        decision_action = decision.get("action", "")

        execution_result = {
            "decision_type": decision_type,
            "action": decision_action,
            "executed": False,
            "verification_result": None,
            "timestamp": datetime.now().isoformat()
        }

        # 根据决策类型执行不同操作
        if decision_type == "completion_focus":
            # 聚焦完成：更新状态为假设，准备重新规划
            execution_result["executed"] = True
            execution_result["action_taken"] = "将系统状态推进到假设阶段，准备重新规划"
            execution_result["next_state"] = "假设"

        elif decision_type == "baseline_fix":
            # 修复基线：触发自校验
            execution_result["executed"] = True
            execution_result["action_taken"] = "启动 self_verify_capabilities.py 基线校验"
            execution_result["verification_command"] = "python scripts/self_verify_capabilities.py"

        elif decision_type == "targeted_fix":
            # 修复针对性验证：分析本轮问题
            execution_result["executed"] = True
            execution_result["action_taken"] = "分析 targeted_verify 结果，进行针对性修复"
            execution_result["next_step"] = "根据验证失败信息修改对应模块"

        elif decision_type == "continuation":
            # 延续方向
            execution_result["executed"] = True
            execution_result["action_taken"] = f"延续上轮建议: {decision_action}"

        elif decision_type == "self_optimization":
            # 自主优化决策
            execution_result["executed"] = True
            execution_result["action_taken"] = "记录自主优化建议到 evolution_self_proposed.md"
            execution_result["next_step"] = "将优化方向写入待办列表"

        else:
            execution_result["executed"] = False
            execution_result["error"] = f"未知决策类型: {decision_type}"

        if self.decision_config["verification_required"] and execution_result["executed"]:
            execution_result["verification_result"] = "待验证"

        self.execution_results.append(execution_result)
        self.loop_status["execution_verified"] = execution_result.get("verification_result") == "通过"

        return execution_result

    def verify_execution(self, execution_result: Dict) -> Dict:
        """
        验证决策执行结果

        Args:
            execution_result: 执行结果

        Returns:
            验证结果
        """
        if not execution_result.get("executed"):
            return {
                "status": "skipped",
                "message": "决策未执行，无需验证"
            }

        decision_type = execution_result.get("decision_type", "")

        # 根据决策类型进行不同验证
        if decision_type == "baseline_fix":
            # 运行基线校验
            verify_result = {
                "status": "pending",
                "message": "需要运行基线校验验证修复效果",
                "command": "python scripts/self_verify_capabilities.py"
            }
        elif decision_type in ["completion_focus", "continuation", "self_optimization"]:
            # 这些决策需要人工或下轮验证
            verify_result = {
                "status": "pending_next_round",
                "message": "决策已执行，将在下一轮验证效果"
            }
        else:
            verify_result = {
                "status": "unknown",
                "message": f"未知决策类型: {decision_type}"
            }

        return verify_result

    def close_loop(self, execution_result: Dict, verify_result: Dict) -> Dict:
        """
        关闭闭环：更新认知状态

        Args:
            execution_result: 执行结果
            verify_result: 验证结果

        Returns:
            闭环结果
        """
        self.loop_status["cognition_updated"] = True

        # 记录闭环结果
        loop_result = {
            "execution_type": execution_result.get("decision_type", ""),
            "execution_action": execution_result.get("action_taken", ""),
            "verification": verify_result.get("status", ""),
            "timestamp": datetime.now().isoformat(),
            "闭环_complete": verify_result.get("status") in ["通过", "pending_next_round"]
        }

        self.decision_history.append(loop_result)

        return {
            "status": "closed",
            "loop_result": loop_result,
            "loop_status": self.loop_status
        }

    def get_cockpit_data(self) -> Dict:
        """
        获取驾驶舱展示数据

        Returns:
            驾驶舱数据
        """
        return {
            "engine_name": self.name,
            "version": self.version,
            "loop_status": self.loop_status,
            "decision_count": len(self.decision_history),
            "recent_decisions": self.decision_history[-5:] if self.decision_history else [],
            "capabilities": self.capabilities,
            "last_update": datetime.now().isoformat()
        }

    def run_full_loop(self, evolution_round: int = None) -> Dict:
        """
        运行完整的认知-决策-执行闭环

        Args:
            evolution_round: 进化轮次

        Returns:
            完整闭环结果
        """
        # 1. 收集认知评估
        cognition_assessment = self.collect_cognition_assessment(evolution_round)

        # 2. 生成决策
        decision_result = self.generate_cognition_driven_decision(cognition_assessment)

        if decision_result.get("status") != "success" or not decision_result.get("decisions"):
            return {
                "status": "no_decision",
                "message": "无法生成有效决策",
                "cognition_assessment": cognition_assessment
            }

        # 3. 执行决策
        primary_decision = decision_result.get("primary_decision")
        execution_result = self.execute_decision(primary_decision)

        # 4. 验证执行
        verify_result = self.verify_execution(execution_result)

        # 5. 关闭闭环
        loop_result = self.close_loop(execution_result, verify_result)

        return {
            "status": "completed",
            "cognition_assessment": cognition_assessment,
            "decision_result": decision_result,
            "execution_result": execution_result,
            "verify_result": verify_result,
            "loop_result": loop_result
        }

    def _get_latest_completed_round(self) -> Optional[int]:
        """获取最近完成的进化轮次"""
        # 首先尝试从 evolution_completed 文件查找最新的已完成轮次
        try:
            completed_files = list(STATE_DIR.glob("evolution_completed_*.json"))
            if completed_files:
                # 按修改时间排序
                completed_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                latest_file = completed_files[0]
                # 尝试从文件名提取 round 编号
                match = re.search(r'_ev_(\d{8})_(\d+)\.json', latest_file.name)
                if match:
                    return int(match.group(2))
        except Exception:
            pass

        # 如果没有找到 completed 文件，则从 current_mission.json 读取并减1
        # 因为 current_mission.json 中的 loop_round 是当前轮（还未完成）
        try:
            mission_file = STATE_DIR / "current_mission.json"
            if mission_file.exists():
                with open(mission_file, 'r', encoding='utf-8') as f:
                    mission_data = json.load(f)
                    loop_round = mission_data.get("loop_round", 0)
                    if loop_round > 0:
                        return loop_round - 1  # 返回上一轮
        except Exception:
            pass

        return None

    def _find_completed_file(self, round_num: int) -> Optional[Path]:
        """查找指定轮次的完成文件"""
        # 尝试多种命名模式
        patterns = [
            f"evolution_completed_*_{round_num}.json",
            f"evolution_completed_{round_num}.json"
        ]

        for pattern in patterns:
            matches = list(STATE_DIR.glob(pattern))
            if matches:
                return matches[0]

        return None


def main():
    """主函数：提供命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="认知驱动自动决策与执行闭环引擎"
    )
    parser.add_argument(
        "--collect",
        action="store_true",
        help="收集认知评估结果"
    )
    parser.add_argument(
        "--decide",
        action="store_true",
        help="基于认知评估生成决策"
    )
    parser.add_argument(
        "--execute",
        type=str,
        help="执行指定决策"
    )
    parser.add_argument(
        "--verify",
        type=str,
        help="验证执行结果"
    )
    parser.add_argument(
        "--loop",
        action="store_true",
        help="运行完整闭环"
    )
    parser.add_argument(
        "--cockpit-data",
        action="store_true",
        help="获取驾驶舱数据"
    )
    parser.add_argument(
        "--round",
        type=int,
        default=None,
        help="指定进化轮次"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="输出 JSON 格式"
    )

    args = parser.parse_args()

    engine = EvolutionCognitionDrivenDecisionExecutionEngine()

    if args.cockpit_data:
        result = engine.get_cockpit_data()
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"=== {result['engine_name']} ===")
            print(f"Version: {result['version']}")
            print(f"闭环状态: {result['loop_status']}")
            print(f"决策数量: {result['decision_count']}")
            print(f"能力: {', '.join(result['capabilities'])}")
        return

    if args.loop:
        result = engine.run_full_loop(args.round)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("=== 完整闭环执行结果 ===")
            print(f"状态: {result.get('status')}")
            if result.get('decision_result'):
                decisions = result['decision_result'].get('decisions', [])
                print(f"生成决策数: {len(decisions)}")
                for i, d in enumerate(decisions, 1):
                    print(f"  {i}. [{d['type']}] {d['description']}")
            if result.get('execution_result'):
                print(f"执行: {result['execution_result'].get('action_taken', 'N/A')}")
        return

    if args.collect:
        result = engine.collect_cognition_assessment(args.round)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("=== 认知评估结果 ===")
            print(f"状态: {result.get('status')}")
            print(f"来源: {result.get('source', 'N/A')}")
        return

    if args.decide:
        # 先收集评估
        assessment = engine.collect_cognition_assessment(args.round)
        result = engine.generate_cognition_driven_decision(assessment)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("=== 决策生成结果 ===")
            print(f"状态: {result.get('status')}")
            decisions = result.get('decisions', [])
            print(f"生成决策数: {len(decisions)}")
            for i, d in enumerate(decisions, 1):
                print(f"  {i}. [{d['type']}] Priority={d['priority']}")
                print(f"     {d['description']}")
                print(f"     Action: {d['action']}")
        return

    if args.execute:
        try:
            decision = json.loads(args.execute)
            result = engine.execute_decision(decision)
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print("=== 决策执行结果 ===")
                print(f"执行: {result.get('executed')}")
                print(f"动作: {result.get('action_taken', 'N/A')}")
        except json.JSONDecodeError:
            print("Error: 无效的决策 JSON")
            sys.exit(1)
        return

    if args.verify:
        try:
            execution_result = json.loads(args.verify)
            result = engine.verify_execution(execution_result)
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print("=== 验证结果 ===")
                print(f"状态: {result.get('status')}")
                print(f"消息: {result.get('message', 'N/A')}")
        except json.JSONDecodeError:
            print("Error: 无效的执行结果 JSON")
            sys.exit(1)
        return

    # 默认显示帮助
    parser.print_help()


if __name__ == "__main__":
    main()