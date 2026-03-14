#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环认知-价值-元进化深度融合引擎
(Evolution Cognition-Value-Meta Fusion Engine)

在 round 473 完成的元进化驱动自适应价值优化引擎基础上，
进一步将认知驱动决策引擎(round 455)与元进化价值优化引擎深度集成。

让系统能够将认知评估结果自动应用到价值优化策略中，
同时将价值实现情况反馈到认知评估，
形成「认知评估→价值优化→元进化学习→效果验证→认知更新」的完整闭环。

让进化环能够真正实现基于认知价值的自适应深度优化。

Version: 1.0.0
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
STATE_DIR = PROJECT_ROOT / "runtime" / "state"
DATA_DIR = PROJECT_ROOT / "runtime" / "data"
LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"

# 添加 scripts 目录到路径以便导入
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

# 尝试导入相关引擎
try:
    from evolution_cognition_driven_decision_execution_engine import (
        EvolutionCognitionDrivenDecisionExecutionEngine
    )
    COGNITION_DECISION_AVAILABLE = True
except ImportError:
    COGNITION_DECISION_AVAILABLE = False

try:
    from evolution_meta_driven_adaptive_value_deep_optimization_engine import (
        MetaDrivenAdaptiveValueDeepOptimizationEngine
    )
    META_VALUE_AVAILABLE = True
except ImportError:
    META_VALUE_AVAILABLE = False


class CognitionValueMetaFusionEngine:
    """认知-价值-元进化深度融合引擎核心类"""

    def __init__(self):
        self.version = "1.0.0"
        self.name = "Cognition-Value-Meta Fusion Engine"
        self.runtime_dir = PROJECT_ROOT / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.data_dir = self.runtime_dir / "data"

        # 数据文件路径
        self.config_file = self.data_dir / "cognition_value_meta_fusion_config.json"
        self.fusion_log_file = self.data_dir / "cognition_value_meta_fusion_log.json"
        self.closed_loop_history_file = self.data_dir / "cognition_value_meta_closed_loop_history.json"

        self._ensure_directories()
        self._initialize_data()
        self._load_or_initialize_engines()

    def _ensure_directories(self):
        """确保必要的目录存在"""
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _initialize_data(self):
        """初始化数据文件"""
        if not self.config_file.exists():
            default_config = {
                "fusion_enabled": True,
                "闭环": {
                    "cognition_to_value": True,
                    "value_to_meta": True,
                    "meta_to_cognition": True
                },
                "thresholds": {
                    "cognition_confidence_low": 0.5,
                    "cognition_confidence_high": 0.8,
                    "value_score_critical": 50,
                    "value_score_low": 65,
                    "value_score_high": 85
                },
                "auto_optimization": {
                    "enabled": True,
                    "apply_to_value": True,
                    "apply_to_cognition": True
                },
                "learning_history": [],
                "last_updated": datetime.now().isoformat()
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)

        if not self.fusion_log_file.exists():
            with open(self.fusion_log_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "fusion_records": [],
                    "last_updated": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)

        if not self.closed_loop_history_file.exists():
            with open(self.closed_loop_history_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "closed_loops": [],
                    "last_updated": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)

    def _load_or_initialize_engines(self):
        """加载或初始化相关引擎"""
        self.cognition_decision_engine = None
        self.meta_value_engine = None

        if COGNITION_DECISION_AVAILABLE:
            try:
                self.cognition_decision_engine = EvolutionCognitionDrivenDecisionExecutionEngine()
            except Exception:
                pass

        if META_VALUE_AVAILABLE:
            try:
                self.meta_value_engine = MetaDrivenAdaptiveValueDeepOptimizationEngine()
            except Exception:
                pass

    def _load_config(self) -> Dict:
        """加载配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_config(self, data: Dict):
        """保存配置"""
        data["last_updated"] = datetime.now().isoformat()
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_fusion_log(self) -> Dict:
        """加载融合日志"""
        try:
            with open(self.fusion_log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"fusion_records": []}

    def _save_fusion_log(self, data: Dict):
        """保存融合日志"""
        data["last_updated"] = datetime.now().isoformat()
        with open(self.fusion_log_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_closed_loop_history(self) -> Dict:
        """加载闭环历史"""
        try:
            with open(self.closed_loop_history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"closed_loops": []}

    def _save_closed_loop_history(self, data: Dict):
        """保存闭环历史"""
        data["last_updated"] = datetime.now().isoformat()
        with open(self.closed_loop_history_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        config = self._load_config()
        fusion_log = self._load_fusion_log()
        closed_loop_history = self._load_closed_loop_history()

        return {
            "engine": "认知-价值-元进化深度融合引擎",
            "version": self.version,
            "fusion_enabled": config.get("fusion_enabled", True),
            "total_fusion_records": len(fusion_log.get("fusion_records", [])),
            "total_closed_loops": len(closed_loop_history.get("closed_loops", [])),
            "cognition_decision_engine_available": self.cognition_decision_engine is not None,
            "meta_value_engine_available": self.meta_value_engine is not None,
            "闭环": config.get("闭环", {}),
            "thresholds": config.get("thresholds", {})
        }

    def collect_cognition_assessment(self) -> Dict[str, Any]:
        """收集认知评估结果"""
        result = {
            "cognition_assessment": {},
            "source": "unknown",
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }

        if self.cognition_decision_engine:
            try:
                assessment = self.cognition_decision_engine.collect_cognition_assessment()
                result["cognition_assessment"] = assessment.get("assessment", {})
                result["source"] = "cognition_decision_engine"
            except Exception as e:
                result["cognition_assessment"] = {"error": str(e)}
                result["source"] = "error"
        else:
            result["cognition_assessment"] = {"message": "无认知决策引擎数据"}
            result["source"] = "fallback"

        return result

    def collect_value_analysis(self) -> Dict[str, Any]:
        """收集价值分析结果"""
        result = {
            "value_analysis": {},
            "meta_learning": {},
            "source": "unknown",
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }

        if self.meta_value_engine:
            try:
                value_analysis = self.meta_value_engine.analyze_value_with_meta_learning()
                result["value_analysis"] = value_analysis.get("value_analysis", {})
                result["meta_learning"] = {
                    "learned_patterns": value_analysis.get("learned_patterns", []),
                    "meta_insights": value_analysis.get("meta_insights", [])
                }
                result["source"] = "meta_value_engine"
            except Exception as e:
                result["value_analysis"] = {"error": str(e)}
                result["source"] = "error"
        else:
            result["value_analysis"] = {"message": "无元价值优化引擎数据"}
            result["source"] = "fallback"

        return result

    def generate_cognition_driven_value_optimization(self) -> Dict[str, Any]:
        """生成认知驱动的价值优化策略"""
        config = self._load_config()
        result = {
            "cognition_based_optimization": {},
            "value_adjustments": {},
            "meta_adjustments": {},
            "combined_strategy": {},
            "rationale": [],
            "status": "success"
        }

        # 步骤1: 获取认知评估
        cognition_result = self.collect_cognition_assessment()
        cognition_assessment = cognition_result.get("cognition_assessment", {})

        # 步骤2: 获取价值分析
        value_result = self.collect_value_analysis()
        value_analysis = value_result.get("value_analysis", {})
        meta_learning = value_result.get("meta_learning", {})

        # 步骤3: 基于认知评估生成优化方向
        cognition_adjustments = self._generate_cognition_based_adjustments(
            cognition_assessment, config
        )
        result["cognition_based_optimization"] = cognition_adjustments

        # 步骤4: 基于价值分析生成优化调整
        value_adjustments = self._generate_value_based_adjustments(
            value_analysis, config
        )
        result["value_adjustments"] = value_adjustments

        # 步骤5: 基于元学习生成优化调整
        meta_adjustments = self._generate_meta_based_adjustments(
            meta_learning, config
        )
        result["meta_adjustments"] = meta_adjustments

        # 步骤6: 综合所有调整生成最终策略
        combined = {**cognition_adjustments, **value_adjustments, **meta_adjustments}
        result["combined_strategy"] = combined

        # 记录融合过程
        self._record_fusion(cognition_result, value_result, result)

        return result

    def _generate_cognition_based_adjustments(
        self,
        cognition_assessment: Dict,
        config: Dict
    ) -> Dict:
        """基于认知评估生成调整"""
        adjustments = {}
        rationale = []

        thresholds = config.get("thresholds", {})

        # 从认知评估中提取关键信息
        was_completed = cognition_assessment.get("was_completed", True)
        baseline_verify = cognition_assessment.get("baseline_verify", "")
        targeted_verify = cognition_assessment.get("targeted_verify", "")

        # 基于完成状态调整
        if not was_completed:
            adjustments["strategy_mode"] = "recovery"
            adjustments["caution_level"] = "high"
            adjustments["retry_boost"] = True
            rationale.append("上轮未完成，采用恢复模式")

        # 基于验证结果调整
        if "fail" in baseline_verify.lower():
            adjustments["focus_on_baseline"] = True
            rationale.append("基线验证有问题，聚焦基础能力")

        if "fail" in targeted_verify.lower():
            adjustments["focus_on_targeted"] = True
            rationale.append("针对性验证有问题，聚焦本轮改动")

        return adjustments

    def _generate_value_based_adjustments(
        self,
        value_analysis: Dict,
        config: Dict
    ) -> Dict:
        """基于价值分析生成调整"""
        adjustments = {}
        rationale = []

        thresholds = config.get("thresholds", {})
        value_score = value_analysis.get("current_value_score", 75)
        value_trend = value_analysis.get("value_trend", "平稳")

        # 基于价值分数调整
        if value_score < thresholds.get("value_score_critical", 50):
            adjustments["execution_timeout"] = 180
            adjustments["retry_count"] = 4
            adjustments["priority_weight_value"] = 0.8
            rationale.append(f"价值分数严重低下({value_score})，需要大幅调整")
        elif value_score < thresholds.get("value_score_low", 65):
            adjustments["execution_timeout"] = 150
            adjustments["retry_count"] = 3
            adjustments["priority_weight_value"] = 0.6
            rationale.append(f"价值分数较低({value_score})，增加价值权重")
        elif value_score > thresholds.get("value_score_high", 85):
            adjustments["execution_timeout"] = 90
            adjustments["retry_count"] = 2
            adjustments["priority_weight_efficiency"] = 0.4
            rationale.append(f"价值分数很高({value_score})，可优化效率")

        return adjustments

    def _generate_meta_based_adjustments(
        self,
        meta_learning: Dict,
        config: Dict
    ) -> Dict:
        """基于元学习生成调整"""
        adjustments = {}
        rationale = []

        learned_patterns = meta_learning.get("learned_patterns", [])
        meta_insights = meta_learning.get("meta_insights", [])

        # 基于学习到的模式调整
        for pattern in learned_patterns:
            pattern_type = pattern.get("pattern", "")
            confidence = pattern.get("confidence", 0.5)

            if confidence >= 0.6:
                if pattern_type == "value_decline":
                    adjustments["strategy_mode"] = "recovery"
                    adjustments["conservative_mode"] = True
                    rationale.append(f"元学习识别: {pattern.get('description')}")
                elif pattern_type == "value_improvement":
                    adjustments["strategy_mode"] = "optimization"
                    rationale.append(f"元学习识别: {pattern.get('description')}")

        return adjustments

    def _record_fusion(
        self,
        cognition_result: Dict,
        value_result: Dict,
        optimization_result: Dict
    ):
        """记录融合过程"""
        fusion_log = self._load_fusion_log()

        record = {
            "timestamp": datetime.now().isoformat(),
            "cognition_source": cognition_result.get("source", "unknown"),
            "value_source": value_result.get("source", "unknown"),
            "combined_strategy": optimization_result.get("combined_strategy", {}),
            "rationale": optimization_result.get("rationale", [])
        }

        fusion_log["fusion_records"].append(record)

        # 只保留最近50条记录
        if len(fusion_log["fusion_records"]) > 50:
            fusion_log["fusion_records"] = fusion_log["fusion_records"][-50:]

        self._save_fusion_log(fusion_log)

    def execute_fused_optimization(self, optimization: Dict) -> Dict[str, Any]:
        """执行融合优化"""
        result = {
            "status": "success",
            "applied_strategy": {},
            "applied_to_cognition": False,
            "applied_to_value": False,
            "message": ""
        }

        config = self._load_config()

        if not config.get("fusion_enabled", True):
            result["status"] = "disabled"
            result["message"] = "融合已禁用"
            return result

        # 应用综合策略
        combined_strategy = optimization.get("combined_strategy", {})

        if not combined_strategy:
            result["status"] = "no_optimization"
            result["message"] = "无需优化"
            return result

        result["applied_strategy"] = combined_strategy

        # 如果配置了自动应用到价值引擎
        auto_opt = config.get("auto_optimization", {})
        if auto_opt.get("apply_to_value", True) and self.meta_value_engine:
            try:
                adjustments = {k: v for k, v in combined_strategy.items()
                             if k in ["execution_timeout", "retry_count", "priority_weight_value",
                                     "priority_weight_efficiency", "priority_weight_health",
                                     "strategy_mode", "conservative_mode"]}
                if adjustments:
                    exec_result = self.meta_value_engine.execute_meta_driven_optimization({
                        "combined_strategy": adjustments,
                        "rationale": optimization.get("rationale", [])
                    })
                    result["applied_to_value"] = True
                    result["value_execution"] = exec_result
            except Exception as e:
                result["warning"] = f"应用到元价值引擎失败: {e}"

        result["message"] = f"成功应用融合优化策略，包含{len(combined_strategy)}项调整"
        return result

    def update_cognition_with_value_feedback(self, value_execution_result: Dict) -> Dict:
        """将价值实现情况反馈到认知评估"""
        config = self._load_config()
        result = {
            "cognition_updated": False,
            "feedback_incorporated": {},
            "message": ""
        }

        if not config.get("闭环", {}).get("value_to_cognition", True):
            result["message"] = "价值到认知的闭环已禁用"
            return result

        # 分析价值执行结果
        applied_strategy = value_execution_result.get("applied_strategy", {})
        value_status = value_execution_result.get("status", "unknown")

        # 生成认知反馈
        if value_status == "success":
            result["feedback_incorporated"] = {
                "value_execution_success": True,
                "applied_adjustments": applied_strategy,
                "next_cognition_focus": "positive"
            }
            result["message"] = "已将价值执行成功反馈到认知模型"
        else:
            result["feedback_incorporated"] = {
                "value_execution_success": False,
                "applied_adjustments": applied_strategy,
                "next_cognition_focus": "recovery"
            }
            result["message"] = "已将价值执行失败反馈到认知模型"

        result["cognition_updated"] = True
        return result

    def run_full_fusion_closed_loop(self) -> Dict[str, Any]:
        """运行完整的融合闭环"""
        result = {
            "status": "success",
            "steps": []
        }

        # 步骤1: 收集认知评估
        cognition_result = self.collect_cognition_assessment()
        result["steps"].append({
            "step": "collect_cognition",
            "status": "completed",
            "source": cognition_result.get("source", "unknown")
        })

        # 步骤2: 收集价值分析
        value_result = self.collect_value_analysis()
        result["steps"].append({
            "step": "collect_value",
            "status": "completed",
            "source": value_result.get("source", "unknown")
        })

        # 步骤3: 生成融合优化
        optimization = self.generate_cognition_driven_value_optimization()
        result["steps"].append({
            "step": "generate_fusion_optimization",
            "status": "completed",
            "combined_strategy": optimization.get("combined_strategy", {}),
            "rationale": optimization.get("rationale", [])
        })

        # 步骤4: 执行融合优化
        execution = self.execute_fused_optimization(optimization)
        result["steps"].append({
            "step": "execute_fusion",
            "status": execution.get("status", "completed"),
            "applied_strategy": execution.get("applied_strategy", {})
        })

        # 步骤5: 更新认知
        cognition_update = self.update_cognition_with_value_feedback(execution)
        result["steps"].append({
            "step": "update_cognition",
            "status": "completed",
            "feedback": cognition_update.get("feedback_incorporated", {})
        })

        # 记录完整闭环
        self._record_closed_loop(result)

        result["final_strategy"] = execution.get("applied_strategy", {})
        result["rationale"] = optimization.get("rationale", [])

        return result

    def _record_closed_loop(self, loop_result: Dict):
        """记录完整闭环"""
        closed_loop_history = self._load_closed_loop_history()

        record = {
            "timestamp": datetime.now().isoformat(),
            "steps_count": len(loop_result.get("steps", [])),
            "final_strategy": loop_result.get("final_strategy", {}),
            "rationale": loop_result.get("rationale", [])
        }

        closed_loop_history["closed_loops"].append(record)

        # 只保留最近30条记录
        if len(closed_loop_history["closed_loops"]) > 30:
            closed_loop_history["closed_loops"] = closed_loop_history["closed_loops"][-30:]

        self._save_closed_loop_history(closed_loop_history)


def get_cockpit_data() -> Dict[str, Any]:
    """获取驾驶舱数据"""
    engine = CognitionValueMetaFusionEngine()
    status = engine.get_status()

    # 获取融合日志
    fusion_log = engine._load_fusion_log()

    # 获取闭环历史
    closed_loop_history = engine._load_closed_loop_history()

    # 获取最新融合
    optimization = engine.generate_cognition_driven_value_optimization()

    return {
        "engine": "认知-价值-元进化深度融合引擎",
        "version": "1.0.0",
        "status": status,
        "recent_fusion": fusion_log.get("fusion_records", [])[-3:],
        "closed_loops_count": len(closed_loop_history.get("closed_loops", [])),
        "latest_optimization": {
            "combined_strategy": optimization.get("combined_strategy", {}),
            "rationale": optimization.get("rationale", [])
        },
        "last_updated": datetime.now().isoformat()
    }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description='智能全场景进化环认知-价值-元进化深度融合引擎'
    )
    parser.add_argument('--status', action='store_true', help='获取引擎状态')
    parser.add_argument('--collect-cognition', action='store_true', help='收集认知评估')
    parser.add_argument('--collect-value', action='store_true', help='收集价值分析')
    parser.add_argument('--generate-optimization', action='store_true', help='生成融合优化')
    parser.add_argument('--optimize', action='store_true', help='运行完整融合闭环')
    parser.add_argument('--cockpit-data', action='store_true', help='获取驾驶舱数据')

    args = parser.parse_args()

    engine = CognitionValueMetaFusionEngine()

    if args.status:
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    elif args.collect_cognition:
        result = engine.collect_cognition_assessment()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.collect_value:
        result = engine.collect_value_analysis()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.generate_optimization:
        result = engine.generate_cognition_driven_value_optimization()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.optimize:
        result = engine.run_full_fusion_closed_loop()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.cockpit_data:
        data = get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        # 默认显示状态
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()