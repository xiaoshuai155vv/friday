"""
智能引擎深度集成协同引擎 (Engine Deep Integration Coordinator)

Round 251: 将 round 250 的拟人操作协调引擎与 round 249 的全场景服务融合引擎深度集成，
实现更智能的服务推荐和上下文保持能力，形成更紧密的服务协同闭环。

核心功能：
1. 深度引擎集成 - 将 humanoid_operation_coordinator 与 full_scenario_service_fusion_engine 融合
2. 智能服务推荐增强 - 基于任务理解和上下文提供更精准的服务推荐
3. 上下文保持 - 在多轮对话中保持上下文连贯性
4. 统一服务入口 - 提供一个统一的入口访问两个引擎的能力

Version: 1.0.0
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


class EngineDeepIntegrationCoordinator:
    """智能引擎深度集成协同引擎"""

    def __init__(self):
        self.name = "Engine Deep Integration Coordinator"
        self.version = "1.0.0"
        self.project_root = PROJECT_ROOT
        self.scripts_dir = SCRIPTS_DIR
        self.state_dir = self.project_root / "runtime" / "state"

        # 上下文记忆
        self.context_memory = {}
        self.conversation_history = []

        # 导入并初始化两个核心引擎
        try:
            from humanoid_operation_coordinator import HumanoidOperationCoordinator
            from full_scenario_service_fusion_engine import FullScenarioServiceFusionEngine

            self.humanoid_coordinator = HumanoidOperationCoordinator()
            self.service_fusion = FullScenarioServiceFusionEngine()
            self.engines_loaded = True
        except ImportError as e:
            print(f"Warning: Failed to import engine modules: {e}")
            self.humanoid_coordinator = None
            self.service_fusion = None
            self.engines_loaded = False

    def status(self) -> Dict[str, Any]:
        """返回引擎状态"""
        return {
            "name": self.name,
            "version": self.version,
            "engines_loaded": self.engines_loaded,
            "context_memory_size": len(self.context_memory),
            "conversation_history_size": len(self.conversation_history),
            "integrated_engines": [
                "humanoid_operation_coordinator",
                "full_scenario_service_fusion_engine"
            ]
        }

    def analyze(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        深度分析用户输入，同时利用两个引擎的能力

        Args:
            user_input: 用户输入
            context: 可选的上下文信息

        Returns:
            包含分析结果的字典
        """
        if not self.engines_loaded:
            return {"error": "Engines not loaded properly"}

        # 更新上下文记忆
        if context:
            self.context_memory.update(context)

        # 1. 使用全场景服务融合引擎进行深度意图分析
        fusion_result = self.service_fusion.analyze_intent_deeply(user_input)

        # 2. 使用拟人操作协调引擎进行任务理解
        task_understanding = self.humanoid_coordinator.understand_task(user_input)

        # 3. 综合两个引擎的结果
        integrated_result = {
            "user_input": user_input,
            "timestamp": datetime.now().isoformat(),
            "intent_analysis": fusion_result,
            "task_understanding": task_understanding,
            "recommended_engines": self._merge_engine_recommendations(
                fusion_result, task_understanding
            ),
            "execution_strategy": self._determine_execution_strategy(
                fusion_result, task_understanding
            ),
            "context": self.context_memory
        }

        # 记录到对话历史
        self.conversation_history.append({
            "input": user_input,
            "result": integrated_result,
            "timestamp": datetime.now().isoformat()
        })

        # 保持对话历史在合理范围内
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]

        return integrated_result

    def _merge_engine_recommendations(
        self,
        fusion_result: Dict,
        task_result: Dict
    ) -> List[str]:
        """合并两个引擎推荐的引擎列表"""
        engines = set()

        # 从融合引擎获取推荐
        if "recommended_engines" in fusion_result:
            engines.update(fusion_result.get("recommended_engines", []))
        if "engines" in fusion_result:
            engines.update(fusion_result.get("engines", []))

        # 从拟人协调引擎获取推荐
        if "recommended_engines" in task_result:
            engines.update(task_result.get("recommended_engines", []))
        if "execution_plan" in task_result and "engines" in task_result["execution_plan"]:
            engines.update(task_result["execution_plan"].get("engines", []))

        return list(engines)

    def _determine_execution_strategy(
        self,
        fusion_result: Dict,
        task_result: Dict
    ) -> str:
        """确定执行策略"""
        # 基于分析结果确定执行策略
        fusion_confidence = fusion_result.get("confidence", 0.5)
        task_complexity = task_result.get("complexity", "simple")

        if task_complexity == "complex" or fusion_confidence < 0.6:
            return "multi_step"
        elif task_complexity == "medium":
            return "orchestrated"
        else:
            return "direct"

    def execute_integrated(
        self,
        user_input: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        集成执行用户请求

        Args:
            user_input: 用户输入
            context: 可选的上下文

        Returns:
            执行结果
        """
        # 首先进行分析
        analysis = self.analyze(user_input, context)

        if "error" in analysis:
            return analysis

        strategy = analysis.get("execution_strategy", "direct")
        engines = analysis.get("recommended_engines", [])

        return {
            "status": "ready_to_execute",
            "analysis": analysis,
            "strategy": strategy,
            "engines_to_use": engines,
            "message": f"准备使用 {len(engines)} 个引擎执行任务，策略: {strategy}"
        }

    def get_context_summary(self) -> Dict[str, Any]:
        """获取上下文摘要"""
        return {
            "memory_items": len(self.context_memory),
            "conversation_turns": len(self.conversation_history),
            "recent_context": dict(list(self.context_memory.items())[-5:]) if self.context_memory else {}
        }

    def clear_context(self) -> Dict[str, Any]:
        """清除上下文记忆"""
        cleared = {
            "context_memory": len(self.context_memory),
            "conversation_history": len(self.conversation_history)
        }
        self.context_memory = {}
        self.conversation_history = []
        return cleared


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能引擎深度集成协同引擎"
    )
    parser.add_argument(
        "command",
        choices=["status", "analyze", "execute", "context", "clear"],
        help="要执行的命令"
    )
    parser.add_argument(
        "--input", "-i",
        help="用户输入（用于 analyze/execute 命令）"
    )
    parser.add_argument(
        "--context", "-c",
        help="上下文 JSON 字符串"
    )

    args = parser.parse_args()

    engine = EngineDeepIntegrationCoordinator()

    if args.command == "status":
        result = engine.status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "analyze":
        if not args.input:
            print("Error: --input is required for analyze command")
            sys.exit(1)

        context = json.loads(args.context) if args.context else None
        result = engine.analyze(args.input, context)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "execute":
        if not args.input:
            print("Error: --input is required for execute command")
            sys.exit(1)

        context = json.loads(args.context) if args.context else None
        result = engine.execute_integrated(args.input, context)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "context":
        result = engine.get_context_summary()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "clear":
        result = engine.clear_context()
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()