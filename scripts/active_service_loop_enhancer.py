#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能主动服务闭环增强引擎（Active Service Loop Enhancer）

将服务预热引擎（round 219）、自适应场景选择引擎（round 215）、
场景执行联动引擎（round 216）深度集成，形成预测→场景选择→预热→执行的
完整主动服务闭环，实现更精准的主动服务。

功能：
1. 统一服务入口 - 一个命令完成预测、选择、预热、执行全流程
2. 服务链编排 - 协调三个引擎的工作流程
3. 上下文传递 - 在引擎之间传递上下文和参数
4. 结果聚合 - 汇总各引擎的执行结果

与 round 215（自适应场景选择）、round 216（场景执行联动）、round 219（服务预热）形成能力增强链。
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# 添加项目根目录到路径
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

# 数据存储路径
DATA_DIR = os.path.join(PROJECT_ROOT, 'runtime', 'state')
LOGS_DIR = os.path.join(PROJECT_ROOT, 'runtime', 'logs')

# 版本
VERSION = "1.0.0"


def load_json_safe(filepath, default=None):
    """安全加载JSON文件"""
    if default is None:
        default = {}
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"[警告] 加载文件失败 {filepath}: {e}")
    return default


def save_json_safe(filepath, data):
    """安全保存JSON文件"""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[警告] 保存文件失败 {filepath}: {e}")
        return False


class ActiveServiceLoopEnhancer:
    """智能主动服务闭环增强引擎"""

    def __init__(self):
        self.version = VERSION
        self.data_dir = DATA_DIR
        self.logs_dir = LOGS_DIR

        # 导入三个引擎
        try:
            import service_preheat_engine as preheat_module
            self.preheat_module = preheat_module
            self._preheat_available = True
        except ImportError as e:
            print(f"[信息] 服务预热引擎不可用: {e}")
            self._preheat_available = False

        try:
            from adaptive_scene_selector import AdaptiveSceneSelector, ContextCollector
            self.scene_selector = AdaptiveSceneSelector()
            self.context_collector = ContextCollector()
            self._scene_selector_available = True
        except ImportError as e:
            print(f"[信息] 自适应场景选择引擎不可用: {e}")
            self._scene_selector_available = False

        try:
            from scene_execution_linkage_engine import SceneExecutionLinkageEngine
            self.scene_linkage = SceneExecutionLinkageEngine()
            self._scene_linkage_available = True
        except ImportError as e:
            print(f"[信息] 场景执行联动引擎不可用: {e}")
            self._scene_linkage_available = False

        # 服务闭环历史记录
        self.loop_history_file = os.path.join(DATA_DIR, "active_service_loop_history.json")

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "version": self.version,
            "engines": {
                "service_preheat": {
                    "available": self._preheat_available,
                    "name": "服务预热引擎 (round 219)"
                },
                "adaptive_scene_selector": {
                    "available": self._scene_selector_available,
                    "name": "自适应场景选择引擎 (round 215)"
                },
                "scene_execution_linkage": {
                    "available": self._scene_linkage_available,
                    "name": "场景执行联动引擎 (round 216)"
                }
            },
            "integration_status": "ready" if all([
                self._preheat_available,
                self._scene_selector_available,
                self._scene_linkage_available
            ]) else "partial",
            "capabilities": [
                "统一服务入口",
                "服务链编排",
                "上下文传递",
                "结果聚合",
                "完整闭环执行"
            ]
        }

    def predict_and_recommend(self, context: Optional[Dict] = None) -> Dict[str, Any]:
        """预测需求并推荐场景"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "prediction": None,
            "recommended_scenes": [],
            "preheat_actions": [],
            "status": "success"
        }

        # 1. 需求预测（使用服务预热引擎）
        if self._preheat_available:
            try:
                prediction = self.preheat_module.predict_needs()
                result["prediction"] = prediction
                # 提取预热建议
                predictions_list = prediction.get("predictions", [])
                if predictions_list:
                    preheat_actions = []
                    for pred in predictions_list:
                        preheat_actions.extend(pred.get("suggested_actions", []))
                    result["preheat_actions"] = preheat_actions
            except Exception as e:
                result["prediction"] = {"error": str(e)}

        # 2. 场景选择（使用自适应场景选择引擎）
        if self._scene_selector_available:
            try:
                # 获取场景推荐
                decision = self.scene_selector.analyze_and_select("")
                result["recommended_scenes"] = [
                    {
                        "scene_name": c.scene_name,
                        "match_score": c.match_score,
                        "match_reasons": c.match_reasons,
                        "auto_execute": c.auto_execute
                    }
                    for c in decision.candidates[:5]
                ]
            except Exception as e:
                result["recommended_scenes"] = [{"error": str(e)}]

        return result

    def execute_complete_loop(
        self,
        target_scene: Optional[str] = None,
        context: Optional[Dict] = None,
        auto_preheat: bool = True,
        auto_execute: bool = False
    ) -> Dict[str, Any]:
        """执行完整的主动服务闭环

        Args:
            target_scene: 目标场景名称，如果为 None 则自动推荐
            context: 上下文信息
            auto_preheat: 是否自动预热
            auto_execute: 是否自动执行

        Returns:
            执行结果字典
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "steps": [],
            "final_status": "success",
            "error": None
        }

        try:
            # 步骤 1: 需求预测与服务预热
            step1_result = {"step": "preheat", "status": "skipped"}
            if auto_preheat and self._preheat_available:
                try:
                    prediction = self.preheat_module.predict_needs()
                    # 自动预热服务
                    preheat_result = self.preheat_module.get_predictions_with_preheat()
                    step1_result = {
                        "step": "preheat",
                        "status": "completed",
                        "prediction": prediction,
                        "preheat_actions": preheat_result.get("auto_preheated", [])
                    }
                except Exception as e:
                    step1_result = {
                        "step": "preheat",
                        "status": "error",
                        "error": str(e)
                    }
            result["steps"].append(step1_result)

            # 步骤 2: 场景选择
            step2_result = {"step": "scene_selection", "status": "skipped"}
            if self._scene_selector_available:
                try:
                    if target_scene:
                        # 手动指定场景
                        decision = self.scene_selector.analyze_and_select(target_scene)
                    else:
                        # 自动推荐场景
                        decision = self.scene_selector.analyze_and_select("")

                    step2_result = {
                        "step": "scene_selection",
                        "status": "completed",
                        "selected_scene": decision.selected_scene,
                        "confidence": decision.confidence,
                        "reasoning": decision.reasoning
                    }
                except Exception as e:
                    step2_result = {
                        "step": "scene_selection",
                        "status": "error",
                        "error": str(e)
                    }
            result["steps"].append(step2_result)

            # 步骤 3: 场景执行联动
            step3_result = {"step": "scene_execution", "status": "skipped"}
            if auto_execute and self._scene_linkage_available:
                selected_scene = step2_result.get("selected_scene")
                if selected_scene:
                    try:
                        # 分析任务并创建场景链
                        chain = self.scene_linkage.analyze_task_and_plan_chain(selected_scene)
                        # 执行场景链
                        exec_result = self.scene_linkage.execute_scene_chain(chain)
                        step3_result = {
                            "step": "scene_execution",
                            "status": "completed",
                            "chain_id": chain.chain_id,
                            "execution_status": exec_result.status
                        }
                    except Exception as e:
                        step3_result = {
                            "step": "scene_execution",
                            "status": "error",
                            "error": str(e)
                        }
            result["steps"].append(step3_result)

            # 保存执行历史
            self._save_loop_history(result)

        except Exception as e:
            result["final_status"] = "error"
            result["error"] = str(e)

        return result

    def analyze_opportunities(self) -> Dict[str, Any]:
        """分析协同优化机会"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "opportunities": [],
            "status": "success"
        }

        # 分析三个引擎之间的协同机会
        opportunities = []

        # 机会 1: 预测 → 场景选择联动
        if self._preheat_available and self._scene_selector_available:
            opportunities.append({
                "type": "prediction_to_scene",
                "description": "需求预测结果可以直接传递给场景选择引擎，实现预测驱动的场景推荐",
                "benefit": "提高场景推荐的准确性"
            })

        # 机会 2: 场景选择 → 场景执行联动
        if self._scene_selector_available and self._scene_linkage_available:
            opportunities.append({
                "type": "scene_to_execution",
                "description": "选中的场景可以直接触发场景执行联动引擎，形成选择→执行闭环",
                "benefit": "实现端到端自动化"
            })

        # 机会 3: 预热 → 执行联动
        if self._preheat_available and self._scene_linkage_available:
            opportunities.append({
                "type": "preheat_to_execution",
                "description": "预热的服务可以直接为场景执行准备环境，提高执行效率",
                "benefit": "减少服务启动时间"
            })

        # 机会 4: 完整闭环
        if all([self._preheat_available, self._scene_selector_available, self._scene_linkage_available]):
            opportunities.append({
                "type": "full_loop",
                "description": "三个引擎深度集成，形成预测→选择→预热→执行的完整闭环",
                "benefit": "实现真正的智能主动服务"
            })

        result["opportunities"] = opportunities
        return result

    def _save_loop_history(self, result: Dict):
        """保存闭环执行历史"""
        history = load_json_safe(self.loop_history_file, {"loops": []})
        history["loops"].append(result)
        # 只保留最近 100 条
        history["loops"] = history["loops"][-100:]
        save_json_safe(self.loop_history_file, history)


def main():
    """主函数 - 命令行入口"""
    parser = argparse.ArgumentParser(
        description="智能主动服务闭环增强引擎 - 将服务预热、场景选择、场景执行深度集成"
    )
    parser.add_argument("command", nargs="?", default="status",
                        help="命令: status, predict, analyze, execute")
    parser.add_argument("--scene", "-s", type=str, default=None,
                        help="指定目标场景")
    parser.add_argument("--auto-preheat", action="store_true",
                        help="自动预热服务")
    parser.add_argument("--auto-execute", "-e", action="store_true",
                        help="自动执行场景")
    parser.add_argument("--version", "-v", action="store_true",
                        help="显示版本")

    args = parser.parse_args()

    engine = ActiveServiceLoopEnhancer()

    if args.version:
        print(f"智能主动服务闭环增强引擎 v{VERSION}")
        return

    if args.command == "status":
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.command == "predict":
        result = engine.predict_and_recommend()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "analyze":
        result = engine.analyze_opportunities()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "execute":
        result = engine.execute_complete_loop(
            target_scene=args.scene,
            auto_preheat=args.auto_preheat,
            auto_execute=args.auto_execute
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {args.command}")
        print("可用命令: status, predict, analyze, execute")
        parser.print_help()


if __name__ == "__main__":
    main()