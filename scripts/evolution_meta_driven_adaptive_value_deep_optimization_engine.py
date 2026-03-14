#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环元进化驱动的自适应价值深度优化引擎
在 round 472 完成的自适应价值优化引擎基础上，进一步将价值优化与元进化引擎深度集成
实现基于元进化驱动的自适应价值深度优化能力

让系统能够从价值优化结果中自动学习，将学习到的知识应用到进化策略调整中，
形成「价值评估→元进化分析→策略学习→自动优化→效果验证」的完整闭环

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
    from evolution_adaptive_value_optimization_engine import AdaptiveValueOptimizationEngine
    ADAPTIVE_VALUE_AVAILABLE = True
except ImportError:
    ADAPTIVE_VALUE_AVAILABLE = False

try:
    from evolution_meta_evolution_enhancement_engine import (
        analyze_evolution_process,
        evaluate_evolution_methodology,
        get_optimization_suggestions
    )
    META_EVOLUTION_AVAILABLE = True
except ImportError:
    META_EVOLUTION_AVAILABLE = False


class MetaDrivenAdaptiveValueDeepOptimizationEngine:
    """元进化驱动的自适应价值深度优化引擎"""

    def __init__(self):
        self.runtime_dir = Path(__file__).parent.parent / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.data_dir = self.runtime_dir / "data"
        self.config_file = self.data_dir / "meta_driven_value_optimization_config.json"
        self.learning_log_file = self.data_dir / "meta_driven_value_optimization_learning.json"
        self.strategy_cache_file = self.data_dir / "meta_driven_value_strategy_cache.json"
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
                "meta_learning_enabled": True,
                "value_analysis": {
                    "focus_on_trends": True,
                    "prediction_window": 5,
                    "anomaly_detection": True
                },
                "strategy_adjustment": {
                    "auto_apply_learned": True,
                    "conservative_mode": False,
                    "learning_rate": 0.3
                },
                "闭环": {
                    "value_to_meta": True,
                    "meta_to_strategy": True,
                    "strategy_to_execution": True
                },
                "thresholds": {
                    "value_critical": 50,
                    "value_low": 65,
                    "value_high": 85,
                    "meta_confidence_threshold": 0.6
                },
                "learning_history": [],
                "last_updated": datetime.now().isoformat()
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)

        if not self.learning_log_file.exists():
            with open(self.learning_log_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "learning_records": [],
                    "insights_generated": [],
                    "last_updated": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)

        if not self.strategy_cache_file.exists():
            with open(self.strategy_cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "learned_strategies": {},
                    "strategy_effectiveness": {},
                    "last_updated": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)

    def _load_or_initialize_engines(self):
        """加载或初始化相关引擎"""
        self.adaptive_value_engine = None
        self.meta_evolution_engine = None

        if ADAPTIVE_VALUE_AVAILABLE:
            try:
                self.adaptive_value_engine = AdaptiveValueOptimizationEngine()
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

    def _load_learning_log(self) -> Dict:
        """加载学习日志"""
        try:
            with open(self.learning_log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"learning_records": [], "insights_generated": []}

    def _save_learning_log(self, data: Dict):
        """保存学习日志"""
        data["last_updated"] = datetime.now().isoformat()
        with open(self.learning_log_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_strategy_cache(self) -> Dict:
        """加载策略缓存"""
        try:
            with open(self.strategy_cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"learned_strategies": {}, "strategy_effectiveness": {}}

    def _save_strategy_cache(self, data: Dict):
        """保存策略缓存"""
        data["last_updated"] = datetime.now().isoformat()
        with open(self.strategy_cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        config = self._load_config()
        learning_log = self._load_learning_log()
        strategy_cache = self._load_strategy_cache()

        return {
            "engine": "元进化驱动的自适应价值深度优化引擎",
            "version": "1.0.0",
            "meta_learning_enabled": config.get("meta_learning_enabled", True),
            "total_learning_records": len(learning_log.get("learning_records", [])),
            "learned_strategies_count": len(strategy_cache.get("learned_strategies", {})),
            "insights_count": len(learning_log.get("insights_generated", [])),
            "adaptive_value_engine_available": self.adaptive_value_engine is not None,
            "闭环_enabled": config.get("闭环", {}),
            "thresholds": config.get("thresholds", {})
        }

    def analyze_value_with_meta_learning(self) -> Dict[str, Any]:
        """使用元学习分析价值表现"""
        result = {
            "value_analysis": {},
            "meta_insights": [],
            "learned_patterns": [],
            "status": "completed"
        }

        # 步骤1: 获取基础价值分析
        if self.adaptive_value_engine:
            try:
                value_analysis = self.adaptive_value_engine.analyze_value_performance()
                result["value_analysis"] = value_analysis
            except Exception as e:
                result["value_analysis"] = {"error": str(e)}
        else:
            result["value_analysis"] = {"message": "无自适应价值优化引擎数据"}

        # 步骤2: 从元进化引擎获取历史进化分析
        if META_EVOLUTION_AVAILABLE:
            try:
                # 加载进化历史
                from evolution_meta_evolution_enhancement_engine import load_evolution_completed_history
                history = load_evolution_completed_history()

                if history:
                    # 分析进化过程
                    process_analysis = analyze_evolution_process(history)
                    result["meta_insights"].append({
                        "type": "evolution_process",
                        "data": process_analysis
                    })

                    # 评估方法论
                    if len(history) >= 5:
                        methodology = evaluate_evolution_methodology(history)
                        result["meta_insights"].append({
                            "type": "methodology",
                            "data": methodology
                        })

                    # 获取优化建议
                    suggestions = get_optimization_suggestions(history)
                    if suggestions:
                        result["meta_insights"].append({
                            "type": "optimization_suggestions",
                            "data": suggestions
                        })

            except Exception as e:
                result["meta_insights"].append({
                    "type": "error",
                    "message": str(e)
                })

        # 步骤3: 识别学习到的模式
        result["learned_patterns"] = self._identify_learned_patterns(result)

        return result

    def _identify_learned_patterns(self, analysis_result: Dict) -> List[Dict]:
        """识别学习到的模式"""
        patterns = []

        value_analysis = analysis_result.get("value_analysis", {})
        meta_insights = analysis_result.get("meta_insights", [])

        # 基于价值分析识别模式
        value_score = value_analysis.get("current_value_score", 75)
        value_trend = value_analysis.get("value_trend", "平稳")

        if value_trend == "下降" and value_score < 65:
            patterns.append({
                "pattern": "value_decline",
                "description": "价值下降趋势明显",
                "strategy": "增加价值权重，减少效率权重",
                "confidence": 0.8
            })
        elif value_trend == "上升" and value_score > 85:
            patterns.append({
                "pattern": "value_improvement",
                "description": "价值持续上升",
                "strategy": "可适当增加效率优化权重",
                "confidence": 0.7
            })

        # 基于元进化洞察识别模式
        for insight in meta_insights:
            if insight.get("type") == "methodology":
                data = insight.get("data", {})
                success_rate = data.get("success_rate", 0)
                if success_rate > 0.9:
                    patterns.append({
                        "pattern": "high_success_rate",
                        "description": f"进化成功率很高 ({success_rate:.1%})",
                        "strategy": "可尝试更激进的优化策略",
                        "confidence": 0.6
                    })
                elif success_rate < 0.7:
                    patterns.append({
                        "pattern": "low_success_rate",
                        "description": f"进化成功率较低 ({success_rate:.1%})",
                        "strategy": "建议采用更保守的优化策略",
                        "confidence": 0.7
                    })

        return patterns

    def generate_meta_driven_optimization(self) -> Dict[str, Any]:
        """生成元进化驱动的优化建议"""
        config = self._load_config()
        result = {
            "optimization_type": "meta_driven",
            "value_based_adjustments": {},
            "meta_based_adjustments": {},
            "combined_strategy": {},
            "rationale": [],
            "status": "success"
        }

        # 步骤1: 获取价值分析结果
        analysis = self.analyze_value_with_meta_learning()

        # 步骤2: 基于价值的调整
        value_analysis = analysis.get("value_analysis", {})
        value_score = value_analysis.get("current_value_score", 75)
        value_trend = value_analysis.get("value_trend", "平稳")
        thresholds = config.get("thresholds", {})

        value_adjustments = {}
        if value_score < thresholds.get("value_critical", 50):
            value_adjustments = {
                "execution_timeout": 180,
                "retry_count": 4,
                "priority_weight_value": 0.8,
                "priority_weight_health": 0.3
            }
            result["rationale"].append("价值分数严重低下，需要大幅调整策略")
        elif value_score < thresholds.get("value_low", 65):
            value_adjustments = {
                "execution_timeout": 150,
                "retry_count": 3,
                "priority_weight_value": 0.6,
                "priority_weight_health": 0.25
            }
            result["rationale"].append("价值分数较低，需要增加价值权重")
        elif value_score > thresholds.get("value_high", 85):
            value_adjustments = {
                "execution_timeout": 90,
                "retry_count": 2,
                "priority_weight_efficiency": 0.4
            }
            result["rationale"].append("价值分数很高，可优化效率")

        result["value_based_adjustments"] = value_adjustments

        # 步骤3: 基于元进化的调整
        meta_adjustments = {}
        learned_patterns = analysis.get("learned_patterns", [])

        for pattern in learned_patterns:
            pattern_type = pattern.get("pattern", "")
            confidence = pattern.get("confidence", 0.5)

            if confidence >= config.get("thresholds", {}).get("meta_confidence_threshold", 0.6):
                if pattern_type == "value_decline":
                    meta_adjustments["strategy_mode"] = "recovery"
                    meta_adjustments["caution_level"] = "high"
                    result["rationale"].append(f"元学习识别: {pattern.get('description')}")
                elif pattern_type == "value_improvement":
                    meta_adjustments["strategy_mode"] = "optimization"
                    meta_adjustments["caution_level"] = "low"
                    result["rationale"].append(f"元学习识别: {pattern.get('description')}")
                elif pattern_type == "low_success_rate":
                    meta_adjustments["conservative_mode"] = True
                    result["rationale"].append(f"元学习识别: {pattern.get('description')}")

        result["meta_based_adjustments"] = meta_adjustments

        # 步骤4: 综合策略
        combined = {**value_adjustments, **meta_adjustments}
        result["combined_strategy"] = combined

        # 记录学习结果
        self._record_learning(analysis, result)

        return result

    def _record_learning(self, analysis: Dict, optimization: Dict):
        """记录学习结果"""
        learning_log = self._load_learning_log()

        record = {
            "timestamp": datetime.now().isoformat(),
            "value_analysis": analysis.get("value_analysis", {}),
            "learned_patterns": analysis.get("learned_patterns", []),
            "optimization_applied": optimization.get("combined_strategy", {}),
            "rationale": optimization.get("rationale", [])
        }

        learning_log["learning_records"].append(record)

        # 只保留最近30条记录
        if len(learning_log["learning_records"]) > 30:
            learning_log["learning_records"] = learning_log["learning_records"][-30:]

        # 生成洞察
        insights = self._generate_insights(learning_log)
        learning_log["insights_generated"] = insights

        self._save_learning_log(learning_log)

    def _generate_insights(self, learning_log: Dict) -> List[Dict]:
        """从学习记录中生成洞察"""
        insights = []
        records = learning_log.get("learning_records", [])

        if len(records) < 3:
            return insights

        # 分析趋势
        recent_records = records[-5:]
        value_scores = []

        for record in recent_records:
            va = record.get("value_analysis", {})
            if "current_value_score" in va:
                value_scores.append(va["current_value_score"])

        if len(value_scores) >= 3:
            if all(value_scores[i] >= value_scores[i+1] for i in range(len(value_scores)-1)):
                insights.append({
                    "type": "trend",
                    "description": "价值分数持续下降趋势",
                    "action": "需要采取恢复性策略"
                })
            elif all(value_scores[i] <= value_scores[i+1] for i in range(len(value_scores)-1)):
                insights.append({
                    "type": "trend",
                    "description": "价值分数持续上升趋势",
                    "action": "当前策略有效，可保持"
                })

        return insights

    def execute_meta_driven_optimization(self, optimization: Dict) -> Dict[str, Any]:
        """执行元进化驱动的优化"""
        result = {
            "status": "success",
            "applied_strategy": {},
            "message": ""
        }

        config = self._load_config()

        if not config.get("meta_learning_enabled", True):
            result["status"] = "disabled"
            result["message"] = "元学习已禁用"
            return result

        # 应用综合策略
        combined_strategy = optimization.get("combined_strategy", {})

        if not combined_strategy:
            result["status"] = "no_optimization"
            result["message"] = "无需优化"
            return result

        # 更新策略缓存
        strategy_cache = self._load_strategy_cache()

        strategy_key = f"strategy_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        strategy_cache["learned_strategies"][strategy_key] = {
            "timestamp": datetime.now().isoformat(),
            "strategy": combined_strategy,
            "rationale": optimization.get("rationale", [])
        }

        # 只保留最近20条策略
        if len(strategy_cache["learned_strategies"]) > 20:
            oldest_key = min(strategy_cache["learned_strategies"].keys())
            del strategy_cache["learned_strategies"][oldest_key]

        result["applied_strategy"] = combined_strategy

        # 如果配置了自动应用到自适应价值引擎
        if config.get("strategy_adjustment", {}).get("auto_apply_learned", True) and self.adaptive_value_engine:
            try:
                adjustments = {k: v for k, v in combined_strategy.items()
                             if k in ["execution_timeout", "retry_count", "priority_weight_value",
                                     "priority_weight_efficiency", "priority_weight_health"]}
                if adjustments:
                    exec_result = self.adaptive_value_engine.execute_optimization({
                        "adjustments": adjustments,
                        "reasons": optimization.get("rationale", []),
                        "based_on": {"source": "meta_driven", "timestamp": datetime.now().isoformat()}
                    })
                    result["applied_to_adaptive_value"] = exec_result.get("applied_adjustments", {})
            except Exception as e:
                result["warning"] = f"应用到自适应价值引擎失败: {e}"

        self._save_strategy_cache(strategy_cache)

        result["message"] = f"成功应用元进化驱动的优化策略，包含{len(combined_strategy)}项调整"
        return result

    def run_full_meta_driven_optimization_cycle(self) -> Dict[str, Any]:
        """运行完整的元进化驱动优化周期"""
        result = {
            "status": "success",
            "steps": []
        }

        # 步骤1: 元学习分析
        analysis = self.analyze_value_with_meta_learning()
        result["steps"].append({
            "step": "meta_learning_analysis",
            "status": "completed",
            "data": {
                "value_analysis": analysis.get("value_analysis", {}),
                "learned_patterns_count": len(analysis.get("learned_patterns", []))
            }
        })

        # 步骤2: 生成优化建议
        optimization = self.generate_meta_driven_optimization()
        result["steps"].append({
            "step": "generate_optimization",
            "status": "completed",
            "data": {
                "combined_strategy": optimization.get("combined_strategy", {}),
                "rationale": optimization.get("rationale", [])
            }
        })

        # 步骤3: 执行优化
        execution = self.execute_meta_driven_optimization(optimization)
        result["steps"].append({
            "step": "execute_optimization",
            "status": execution.get("status", "completed"),
            "data": execution
        })

        result["final_strategy"] = execution.get("applied_strategy", {})
        result["rationale"] = optimization.get("rationale", [])

        return result


def get_cockpit_data() -> Dict[str, Any]:
    """获取驾驶舱数据"""
    engine = MetaDrivenAdaptiveValueDeepOptimizationEngine()
    status = engine.get_status()

    # 获取学习日志
    learning_log = engine._load_learning_log()

    # 获取策略缓存
    strategy_cache = engine._load_strategy_cache()

    # 获取最新分析
    analysis = engine.analyze_value_with_meta_learning()

    return {
        "engine": "元进化驱动的自适应价值深度优化引擎",
        "version": "1.0.0",
        "status": status,
        "recent_learning": learning_log.get("learning_records", [])[-3:],
        "insights": learning_log.get("insights_generated", []),
        "learned_strategies": list(strategy_cache.get("learned_strategies", {}).keys()),
        "latest_analysis": {
            "value_score": analysis.get("value_analysis", {}).get("current_value_score", "N/A"),
            "value_trend": analysis.get("value_analysis", {}).get("value_trend", "N/A"),
            "patterns_count": len(analysis.get("learned_patterns", []))
        },
        "last_updated": datetime.now().isoformat()
    }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='智能全场景进化环元进化驱动的自适应价值深度优化引擎')
    parser.add_argument('--status', action='store_true', help='获取引擎状态')
    parser.add_argument('--analyze', action='store_true', help='执行元学习分析')
    parser.add_argument('--optimize', action='store_true', help='运行完整优化周期')
    parser.add_argument('--cockpit-data', action='store_true', help='获取驾驶舱数据')

    args = parser.parse_args()

    engine = MetaDrivenAdaptiveValueDeepOptimizationEngine()

    if args.status:
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    elif args.analyze:
        analysis = engine.analyze_value_with_meta_learning()
        print(json.dumps(analysis, ensure_ascii=False, indent=2))
    elif args.optimize:
        result = engine.run_full_meta_driven_optimization_cycle()
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