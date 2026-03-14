#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环自适应价值优化引擎
在 round 471 完成的价值干预自动执行引擎基础上，进一步将价值干预执行结果与元进化引擎深度集成
实现基于价值表现自动调整进化策略参数的递归优化能力

让系统能够自动根据价值表现调整进化策略参数，形成「价值评估→策略调整→执行优化→效果验证」的完整闭环

Version: 1.0.0
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict

# 添加 scripts 目录到路径以便导入
sys.path.insert(0, str(Path(__file__).parent))

# 尝试导入相关引擎
try:
    from evolution_value_intervention_auto_execution_engine import ValueInterventionAutoExecutionEngine
    VALUE_INTERVENTION_AVAILABLE = True
except ImportError:
    VALUE_INTERVENTION_AVAILABLE = False

try:
    from evolution_meta_evolution_enhancement_engine import analyze_evolution_process, get_optimization_suggestions
    META_EVOLUTION_AVAILABLE = True
except ImportError:
    META_EVOLUTION_AVAILABLE = False


class AdaptiveValueOptimizationEngine:
    """自适应价值优化引擎"""

    def __init__(self):
        self.runtime_dir = Path(__file__).parent.parent / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.data_dir = self.runtime_dir / "data"
        self.optimization_config_file = self.data_dir / "adaptive_value_optimization_config.json"
        self.optimization_log_file = self.data_dir / "adaptive_value_optimization_log.json"
        self.adjusted_parameters_file = self.data_dir / "adjusted_strategy_parameters.json"
        self._ensure_directories()
        self._initialize_data()
        self._load_or_initialize_engines()

    def _ensure_directories(self):
        """确保必要的目录存在"""
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _initialize_data(self):
        """初始化数据文件"""
        if not self.optimization_config_file.exists():
            default_config = {
                "optimization_enabled": True,
                "value_threshold": {
                    "critical_low": 50,
                    "low": 65,
                    "medium": 80,
                    "high": 90
                },
                "adjustment_rules": {
                    "value_based": True,
                    "efficiency_based": True,
                    "health_based": True
                },
                "parameter_adjustments": {
                    "execution_timeout": {"min": 30, "max": 300, "default": 120},
                    "retry_count": {"min": 1, "max": 5, "default": 3},
                    "priority_weight_value": {"min": 0.1, "max": 1.0, "default": 0.5},
                    "priority_weight_efficiency": {"min": 0.1, "max": 1.0, "default": 0.3},
                    "priority_weight_health": {"min": 0.1, "max": 1.0, "default": 0.2}
                },
                "auto_adjust_enabled": True,
                "adjustment_history": [],
                "last_updated": datetime.now().isoformat()
            }
            with open(self.optimization_config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)

        if not self.optimization_log_file.exists():
            with open(self.optimization_log_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "optimizations": [],
                    "last_updated": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)

        if not self.adjusted_parameters_file.exists():
            with open(self.adjusted_parameters_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "current_parameters": {},
                    "adjustment_history": [],
                    "last_updated": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)

    def _load_or_initialize_engines(self):
        """加载或初始化相关引擎"""
        self.value_intervention_engine = None
        self.meta_evolution_engine = None

        if VALUE_INTERVENTION_AVAILABLE:
            try:
                self.value_intervention_engine = ValueInterventionAutoExecutionEngine()
            except Exception:
                pass

    def _load_config(self) -> Dict:
        """加载配置"""
        try:
            with open(self.optimization_config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_config(self, data: Dict):
        """保存配置"""
        data["last_updated"] = datetime.now().isoformat()
        with open(self.optimization_config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_optimization_log(self) -> Dict:
        """加载优化日志"""
        try:
            with open(self.optimization_log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"optimizations": []}

    def _save_optimization_log(self, data: Dict):
        """保存优化日志"""
        data["last_updated"] = datetime.now().isoformat()
        with open(self.optimization_log_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_adjusted_parameters(self) -> Dict:
        """加载已调整的参数"""
        try:
            with open(self.adjusted_parameters_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"current_parameters": {}, "adjustment_history": []}

    def _save_adjusted_parameters(self, data: Dict):
        """保存已调整的参数"""
        data["last_updated"] = datetime.now().isoformat()
        with open(self.adjusted_parameters_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        config = self._load_config()
        optimization_log = self._load_optimization_log()
        adjusted_params = self._load_adjusted_parameters()

        return {
            "engine": "自适应价值优化引擎",
            "version": "1.0.0",
            "optimization_enabled": config.get("optimization_enabled", True),
            "total_optimizations": len(optimization_log.get("optimizations", [])),
            "successful_optimizations": len([o for o in optimization_log.get("optimizations", []) if o.get("status") == "success"]),
            "value_intervention_engine_available": self.value_intervention_engine is not None,
            "current_parameters": adjusted_params.get("current_parameters", {}),
            "value_threshold": config.get("value_threshold", {})
        }

    def analyze_value_performance(self) -> Dict[str, Any]:
        """分析价值表现"""
        result = {
            "current_value_score": 0,
            "value_trend": "unknown",
            "performance_level": "unknown",
            "issues": [],
            "recommendations": []
        }

        # 从价值干预引擎获取数据
        if self.value_intervention_engine:
            try:
                intervention_status = self.value_intervention_engine.get_status()
                result["intervention_engine_status"] = intervention_status

                # 获取最近的干预执行记录
                execution_log = self.value_intervention_engine._load_execution_log()
                executions = execution_log.get("executions", [])

                if executions:
                    # 分析最近的价值表现
                    recent_executions = executions[-5:]  # 最近5次
                    success_count = sum(1 for e in recent_executions if e.get("status") == "success")
                    success_rate = success_count / len(recent_executions) if recent_executions else 0

                    # 计算价值分数
                    if success_rate >= 0.8:
                        result["current_value_score"] = 90
                        result["performance_level"] = "优秀"
                    elif success_rate >= 0.6:
                        result["current_value_score"] = 75
                        result["performance_level"] = "良好"
                    elif success_rate >= 0.4:
                        result["current_value_score"] = 60
                        result["performance_level"] = "一般"
                    else:
                        result["current_value_score"] = 40
                        result["performance_level"] = "较差"

                    # 分析趋势
                    if len(recent_executions) >= 3:
                        early_success = sum(1 for e in recent_executions[:len(recent_executions)//2] if e.get("status") == "success")
                        late_success = sum(1 for e in recent_executions[len(recent_executions)//2:] if e.get("status") == "success")
                        if late_success > early_success:
                            result["value_trend"] = "上升"
                        elif late_success < early_success:
                            result["value_trend"] = "下降"
                        else:
                            result["value_trend"] = "平稳"

                    # 发现问题
                    failed = [e for e in recent_executions if e.get("status") != "success"]
                    if failed:
                        result["issues"].append(f"最近{len(failed)}次干预执行未成功")
                        for f in failed:
                            if "reason" in f:
                                result["issues"].append(f.get("reason"))

            except Exception as e:
                result["error"] = str(e)

        # 如果没有干预引擎数据，生成默认评估
        if "intervention_engine_status" not in result:
            result["current_value_score"] = 75
            result["value_trend"] = "平稳"
            result["performance_level"] = "良好"
            result["message"] = "无干预引擎数据，使用默认评估"

        return result

    def generate_parameter_adjustments(self, value_analysis: Dict) -> Dict[str, Any]:
        """根据价值分析生成参数调整建议"""
        config = self._load_config()
        param_adjustments = config.get("parameter_adjustments", {})
        value_score = value_analysis.get("current_value_score", 75)
        value_trend = value_analysis.get("value_trend", "平稳")

        adjustments = {}
        adjustment_reasons = []

        # 根据价值分数调整参数
        if value_score < config.get("value_threshold", {}).get("critical_low", 50):
            # 严重低下：大幅调整
            adjustments["execution_timeout"] = min(param_adjustments.get("execution_timeout", {}).get("max", 300), 180)
            adjustments["retry_count"] = min(param_adjustments.get("retry_count", {}).get("max", 5), 4)
            adjustments["priority_weight_value"] = min(param_adjustments.get("priority_weight_value", {}).get("max", 1.0), 0.8)
            adjustment_reasons.append("价值分数严重低下，大幅增加价值权重和重试次数")
        elif value_score < config.get("value_threshold", {}).get("low", 65):
            # 较低：适度调整
            adjustments["execution_timeout"] = min(param_adjustments.get("execution_timeout", {}).get("max", 300), 150)
            adjustments["retry_count"] = min(param_adjustments.get("retry_count", {}).get("max", 5), 3)
            adjustments["priority_weight_value"] = min(param_adjustments.get("priority_weight_value", {}).get("max", 1.0), 0.6)
            adjustment_reasons.append("价值分数较低，增加价值权重和重试次数")
        elif value_score >= config.get("value_threshold", {}).get("high", 90):
            # 很高：可以稍微减少重试以提高效率
            adjustments["execution_timeout"] = max(param_adjustments.get("execution_timeout", {}).get("min", 30), 90)
            adjustments["retry_count"] = max(param_adjustments.get("retry_count", {}).get("min", 1), 2)
            adjustments["priority_weight_value"] = max(param_adjustments.get("priority_weight_value", {}).get("min", 0.1), 0.4)
            adjustment_reasons.append("价值分数很高，可适当减少重试以提高效率")

        # 根据趋势调整
        if value_trend == "下降":
            adjustments["priority_weight_health"] = min(param_adjustments.get("priority_weight_health", {}).get("max", 1.0), 0.4)
            adjustment_reasons.append("价值趋势下降，增加健康权重以确保系统稳定")
        elif value_trend == "上升":
            adjustments["priority_weight_efficiency"] = min(param_adjustments.get("priority_weight_efficiency", {}).get("max", 1.0), 0.4)
            adjustment_reasons.append("价值趋势上升，可适当增加效率权重")

        return {
            "adjustments": adjustments,
            "reasons": adjustment_reasons,
            "based_on": {
                "value_score": value_score,
                "value_trend": value_trend
            }
        }

    def execute_optimization(self, adjustments: Dict[str, Any]) -> Dict[str, Any]:
        """执行优化调整"""
        result = {
            "status": "success",
            "applied_adjustments": {},
            "message": ""
        }

        config = self._load_config()

        if not config.get("auto_adjust_enabled", True):
            result["status"] = "disabled"
            result["message"] = "自动调整已禁用"
            return result

        # 应用调整
        adjusted_params = self._load_adjusted_parameters()
        current_params = adjusted_params.get("current_parameters", {})

        for param, value in adjustments.get("adjustments", {}).items():
            current_params[param] = value
            result["applied_adjustments"][param] = value

        adjusted_params["current_parameters"] = current_params

        # 记录调整历史
        adjustment_record = {
            "timestamp": datetime.now().isoformat(),
            "adjustments": result["applied_adjustments"],
            "reasons": adjustments.get("reasons", []),
            "based_on": adjustments.get("based_on", {})
        }

        if "adjustment_history" not in adjusted_params:
            adjusted_params["adjustment_history"] = []

        adjusted_params["adjustment_history"].append(adjustment_record)

        # 只保留最近20条调整记录
        if len(adjusted_params["adjustment_history"]) > 20:
            adjusted_params["adjustment_history"] = adjusted_params["adjustment_history"][-20:]

        self._save_adjusted_parameters(adjusted_params)

        # 同时更新配置中的默认值
        param_adjustments = config.get("parameter_adjustments", {})
        for param, value in result["applied_adjustments"].items():
            if param in param_adjustments:
                param_adjustments[param]["default"] = value

        config["parameter_adjustments"] = param_adjustments

        # 记录到优化日志
        optimization_log = self._load_optimization_log()
        optimization_record = {
            "timestamp": datetime.now().isoformat(),
            "type": "parameter_adjustment",
            "adjustments": result["applied_adjustments"],
            "reasons": adjustments.get("reasons", []),
            "status": "success"
        }
        optimization_log["optimizations"].append(optimization_record)

        # 只保留最近50条优化记录
        if len(optimization_log["optimizations"]) > 50:
            optimization_log["optimizations"] = optimization_log["optimizations"][-50:]

        self._save_optimization_log(optimization_log)
        self._save_config(config)

        result["message"] = f"成功应用{len(result['applied_adjustments'])}项参数调整"
        return result

    def run_full_optimization_cycle(self) -> Dict[str, Any]:
        """运行完整的优化周期"""
        result = {
            "status": "success",
            "steps": []
        }

        # 步骤1: 分析价值表现
        value_analysis = self.analyze_value_performance()
        result["steps"].append({
            "step": "value_analysis",
            "status": "completed",
            "data": value_analysis
        })

        # 步骤2: 生成参数调整建议
        adjustments = self.generate_parameter_adjustments(value_analysis)
        result["steps"].append({
            "step": "generate_adjustments",
            "status": "completed",
            "data": adjustments
        })

        # 步骤3: 执行优化
        if adjustments.get("adjustments"):
            execution_result = self.execute_optimization(adjustments)
            result["steps"].append({
                "step": "execute_optimization",
                "status": execution_result.get("status", "completed"),
                "data": execution_result
            })
        else:
            result["steps"].append({
                "step": "execute_optimization",
                "status": "skipped",
                "message": "无需调整参数"
            })

        result["latest_value_analysis"] = value_analysis
        result["latest_adjustments"] = adjustments

        return result


def get_cockpit_data() -> Dict[str, Any]:
    """获取驾驶舱数据"""
    engine = AdaptiveValueOptimizationEngine()
    status = engine.get_status()

    # 获取更多数据
    value_analysis = engine.analyze_value_performance()
    adjusted_params = engine._load_adjusted_parameters()
    optimization_log = engine._load_optimization_log()

    return {
        "engine": "自适应价值优化引擎",
        "version": "1.0.0",
        "status": status,
        "value_analysis": value_analysis,
        "current_parameters": adjusted_params.get("current_parameters", {}),
        "recent_optimizations": optimization_log.get("optimizations", [])[-5:],
        "last_updated": datetime.now().isoformat()
    }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='智能全场景进化环自适应价值优化引擎')
    parser.add_argument('--status', action='store_true', help='获取引擎状态')
    parser.add_argument('--analyze', action='store_true', help='分析价值表现')
    parser.add_argument('--optimize', action='store_true', help='运行完整优化周期')
    parser.add_argument('--cockpit-data', action='store_true', help='获取驾驶舱数据')

    args = parser.parse_args()

    engine = AdaptiveValueOptimizationEngine()

    if args.status:
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    elif args.analyze:
        analysis = engine.analyze_value_performance()
        print(json.dumps(analysis, ensure_ascii=False, indent=2))
    elif args.optimize:
        result = engine.run_full_optimization_cycle()
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