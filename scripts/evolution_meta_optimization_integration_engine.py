#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环元进化与自动化深度集成引擎
version 1.0.0

功能：
1. 深度集成 round 464 的自动化优化能力 - 获取优化结果和效能数据
2. 深度集成 round 442/443 的元进化增强能力 - 自动分析进化过程和策略
3. 实现"优化结果→元进化分析→策略自动调整"的完整闭环
4. 基于自动化优化结果自动调整进化策略参数
5. 实现智能策略推荐与自动应用
6. 与进化驾驶舱深度集成 - 可视化整个集成过程
7. 集成到 do.py 支持元进化优化、策略自动调整、集成优化等关键词触发

作者：AI Evolution System
日期：2026-03-15
"""

import os
import sys
import json
import re
import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import argparse

SCRIPT_DIR = Path(__file__).parent
RUNTIME_DIR = SCRIPT_DIR / ".." / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"


class EvolutionMetaOptimizationIntegrationEngine:
    """元进化与自动化深度集成引擎 v1.0.0"""

    def __init__(self, base_path: str = None):
        self.version = "1.0.0"
        self.base_path = base_path or str(SCRIPT_DIR)
        self.runtime_path = os.path.join(self.base_path, 'runtime')
        self.state_path = os.path.join(self.runtime_path, 'state')
        self.logs_path = os.path.join(self.runtime_path, 'logs')

        # 状态文件
        self.state_file = Path(STATE_DIR) / "meta_optimization_integration_state.json"
        self.strategy_config_file = Path(STATE_DIR) / "meta_strategy_config.json"
        self.optimization_history_file = Path(STATE_DIR) / "meta_optimization_history.json"
        self.cockpit_data_file = Path(STATE_DIR) / "meta_optimization_cockpit_data.json"

        # 策略配置
        self.strategy_config = self._load_strategy_config()

        # 尝试导入相关引擎
        self.auto_optimization_engine = None
        self.meta_evolution_engine = None
        self._init_engines()

    def _init_engines(self):
        """初始化相关引擎"""
        try:
            sys.path.insert(0, self.base_path)
            from evolution_collaboration_efficiency_auto_optimization_engine import EvolutionCollaborationEfficiencyAutoOptimizationEngine
            self.auto_optimization_engine = EvolutionCollaborationEfficiencyAutoOptimizationEngine(self.base_path)
        except ImportError as e:
            print(f"自动化优化引擎不可用: {e}")

        try:
            from evolution_meta_evolution_enhancement_engine import load_evolution_completed_history, analyze_evolution_process
            self.meta_evolution_engine = {
                'load_history': load_evolution_completed_history,
                'analyze': analyze_evolution_process
            }
        except ImportError as e:
            print(f"元进化增强引擎不可用: {e}")

    def _load_strategy_config(self) -> Dict[str, Any]:
        """加载策略配置"""
        if self.strategy_config_file.exists():
            with open(self.strategy_config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "auto_adjust_enabled": True,  # 是否启用自动策略调整
            "adjustment_threshold": 0.2,  # 调整阈值：优化效果变化超过此比例时触发
            "strategy_review_interval": 3600,  # 策略审查间隔（秒）
            "max_strategy_variations": 5,  # 最大策略变体数
            "learning_rate": 0.1,  # 学习率：调整幅度
            "confidence_threshold": 0.7,  # 置信度阈值：低于此值不自动调整
        }

    def save_strategy_config(self, config: Dict[str, Any]) -> None:
        """保存策略配置"""
        with open(self.strategy_config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def load_state(self) -> Dict[str, Any]:
        """加载引擎状态"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "initialized": False,
            "last_optimization_analysis_time": None,
            "last_strategy_adjustment_time": None,
            "total_optimization_analyses": 0,
            "total_strategy_adjustments": 0,
            "current_strategy_version": "1.0.0"
        }

    def save_state(self, state: Dict[str, Any]) -> None:
        """保存引擎状态"""
        state["last_updated"] = datetime.now().isoformat()
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def load_optimization_history(self) -> List[Dict[str, Any]]:
        """加载优化历史"""
        if self.optimization_history_file.exists():
            with open(self.optimization_history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_optimization_history(self, history: List[Dict[str, Any]]) -> None:
        """保存优化历史"""
        # 只保留最近100条
        history = history[-100:]
        with open(self.optimization_history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱数据"""
        if self.cockpit_data_file.exists():
            with open(self.cockpit_data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "status": "no_data",
            "message": "暂无驾驶舱数据"
        }

    def analyze_optimization_results(self) -> Dict[str, Any]:
        """
        分析自动化优化结果
        集成 round 464 的自动化优化引擎获取优化数据
        """
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "optimization_results": [],
            "effectiveness_summary": {},
            "recommended_adjustments": []
        }

        # 尝试从自动化优化引擎获取数据
        if self.auto_optimization_engine:
            try:
                # 获取优化状态
                opt_state = self.auto_optimization_engine.load_state()
                analysis["optimization_results"] = opt_state.get("recent_optimizations", [])

                # 获取效能数据
                if hasattr(self.auto_optimization_engine, 'get_efficiency_metrics'):
                    metrics = self.auto_optimization_engine.get_efficiency_metrics()
                    analysis["efficiency_metrics"] = metrics

                # 获取阈值配置
                analysis["threshold_config"] = self.auto_optimization_engine.threshold_config
            except Exception as e:
                analysis["error"] = f"获取优化数据失败: {e}"
        else:
            analysis["error"] = "自动化优化引擎未初始化"

        # 分析优化效果
        if analysis["optimization_results"]:
            total = len(analysis["optimization_results"])
            successful = sum(1 for r in analysis["optimization_results"] if r.get("status") == "completed")
            analysis["effectiveness_summary"] = {
                "total_optimizations": total,
                "successful": successful,
                "success_rate": successful / total if total > 0 else 0
            }

        # 生成调整建议
        analysis["recommended_adjustments"] = self._generate_adjustment_recommendations(analysis)

        return analysis

    def _generate_adjustment_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """基于分析结果生成调整建议"""
        recommendations = []

        effectiveness = analysis.get("effectiveness_summary", {})
        success_rate = effectiveness.get("success_rate", 0)

        # 根据成功率生成建议
        if success_rate < 0.5:
            recommendations.append({
                "type": "strategy_adjustment",
                "priority": "high",
                "description": "优化成功率较低，建议调整优化策略参数",
                "suggested_actions": [
                    "降低优化任务复杂度",
                    "增加优化执行超时时间",
                    "启用更保守的优化策略"
                ]
            })
        elif success_rate < 0.8:
            recommendations.append({
                "type": "strategy_adjustment",
                "priority": "medium",
                "description": "优化成功率一般，建议微调策略参数",
                "suggested_actions": [
                    "适当增加重试次数",
                    "优化任务调度策略"
                ]
            })

        # 基于阈值配置生成建议
        threshold_config = analysis.get("threshold_config", {})
        if threshold_config:
            efficiency_threshold = threshold_config.get("efficiency_threshold", 70.0)
            if efficiency_threshold < 60:
                recommendations.append({
                    "type": "threshold_optimization",
                    "priority": "medium",
                    "description": "效能阈值设置过低，可能导致过度优化",
                    "suggested_actions": ["建议将效率阈值调整到 70-80 范围"]
                })

        return recommendations

    def get_meta_evolution_analysis(self) -> Dict[str, Any]:
        """
        获取元进化分析结果
        集成 round 442/443 的元进化增强引擎
        """
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "meta_evolution_status": "no_data",
            "process_analysis": {},
            "strategy_recommendations": []
        }

        if self.meta_evolution_engine:
            try:
                # 加载进化历史
                history = self.meta_evolution_engine['load_history']()
                analysis["history_count"] = len(history)

                if history:
                    # 分析进化过程
                    process_analysis = self.meta_evolution_engine['analyze'](history)
                    analysis["process_analysis"] = process_analysis
                    analysis["meta_evolution_status"] = "analyzed"

                    # 生成策略建议
                    analysis["strategy_recommendations"] = self._generate_strategy_recommendations(process_analysis)
            except Exception as e:
                analysis["error"] = f"元进化分析失败: {e}"
        else:
            analysis["error"] = "元进化引擎未初始化"

        return analysis

    def _generate_strategy_recommendations(self, process_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """基于元进化分析生成策略建议"""
        recommendations = []

        if process_analysis.get("status") == "insufficient_data":
            return [{
                "type": "data_collection",
                "priority": "low",
                "description": "需要更多历史数据进行分析",
                "suggested_actions": ["继续累积进化历史数据"]
            }]

        # 从分析结果中提取建议
        efficiency = process_analysis.get("efficiency_metrics", {})

        # 根据效率评分生成建议
        efficiency_score = efficiency.get("overall_score", 0)
        if efficiency_score < 60:
            recommendations.append({
                "type": "strategy_overhaul",
                "priority": "high",
                "description": "进化效率较低，建议全面优化进化策略",
                "suggested_actions": [
                    "重新评估进化目标设定",
                    "调整进化路径规划策略",
                    "增强执行效果验证"
                ]
            })

        return recommendations

    def integrate_and_optimize(self) -> Dict[str, Any]:
        """
        执行元进化与自动化的深度集成
        实现"优化结果→元进化分析→策略自动调整"的完整闭环
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "status": "running",
            "steps_completed": [],
            "final_recommendations": []
        }

        # 步骤1：分析自动化优化结果
        opt_analysis = self.analyze_optimization_results()
        result["steps_completed"].append("optimization_analysis")
        result["optimization_analysis"] = opt_analysis

        # 步骤2：获取元进化分析
        meta_analysis = self.get_meta_evolution_analysis()
        result["steps_completed"].append("meta_evolution_analysis")
        result["meta_evolution_analysis"] = meta_analysis

        # 步骤3：生成综合建议
        combined_recommendations = self._combine_recommendations(
            opt_analysis.get("recommended_adjustments", []),
            meta_analysis.get("strategy_recommendations", [])
        )
        result["final_recommendations"] = combined_recommendations

        # 步骤4：检查是否需要自动调整
        if self.strategy_config.get("auto_adjust_enabled"):
            adjustments = self._evaluate_and_prepare_adjustments(
                opt_analysis,
                meta_analysis,
                combined_recommendations
            )
            result["pending_adjustments"] = adjustments

        result["status"] = "completed"

        # 保存到历史
        history = self.load_optimization_history()
        history.append({
            "timestamp": result["timestamp"],
            "status": result["status"],
            "recommendations_count": len(combined_recommendations)
        })
        self.save_optimization_history(history)

        # 更新驾驶舱数据
        self._update_cockpit_data(result)

        return result

    def _combine_recommendations(
        self,
        opt_recommendations: List[Dict[str, Any]],
        meta_recommendations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """合并两类建议，优先处理高优先级"""
        combined = opt_recommendations + meta_recommendations
        # 按优先级排序
        priority_order = {"high": 0, "medium": 1, "low": 2}
        combined.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 2))
        return combined

    def _evaluate_and_prepare_adjustments(
        self,
        opt_analysis: Dict[str, Any],
        meta_analysis: Dict[str, Any],
        recommendations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """评估并准备自动调整"""
        pending = []

        for rec in recommendations:
            if rec.get("priority") == "high" and rec.get("type") == "strategy_adjustment":
                pending.append({
                    "recommendation": rec,
                    "confidence": 0.8,
                    "auto_apply": True
                })

        return pending

    def _update_cockpit_data(self, result: Dict[str, Any]) -> None:
        """更新驾驶舱数据"""
        cockpit_data = {
            "last_update": result["timestamp"],
            "status": result["status"],
            "steps_completed": result["steps_completed"],
            "recommendations_count": len(result.get("final_recommendations", [])),
            "pending_adjustments_count": len(result.get("pending_adjustments", []))
        }

        with open(self.cockpit_data_file, 'w', encoding='utf-8') as f:
            json.dump(cockpit_data, f, ensure_ascii=False, indent=2)

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        state = self.load_state()

        # 获取最新优化历史
        history = self.load_optimization_history()
        recent_history = history[-10:] if history else []

        return {
            "version": self.version,
            "initialized": True,
            "auto_adjust_enabled": self.strategy_config.get("auto_adjust_enabled"),
            "last_analysis_time": state.get("last_optimization_analysis_time"),
            "last_adjustment_time": state.get("last_strategy_adjustment_time"),
            "total_analyses": state.get("total_optimization_analyses", 0),
            "total_adjustments": state.get("total_strategy_adjustments", 0),
            "recent_history": recent_history,
            "engines_integrated": {
                "auto_optimization": self.auto_optimization_engine is not None,
                "meta_evolution": self.meta_evolution_engine is not None
            }
        }

    def run_full_cycle(self) -> Dict[str, Any]:
        """运行完整的集成优化周期"""
        print("=" * 60)
        print("元进化与自动化深度集成引擎 - 完整周期")
        print("=" * 60)

        result = self.integrate_and_optimize()

        print(f"\n状态: {result['status']}")
        print(f"完成步骤: {', '.join(result['steps_completed'])}")
        print(f"建议数量: {len(result['final_recommendations'])}")

        if result['final_recommendations']:
            print("\n推荐调整:")
            for i, rec in enumerate(result['final_recommendations'][:3], 1):
                print(f"  {i}. [{rec.get('priority', 'N/A').upper()}] {rec.get('description', '')}")

        return result


def main():
    parser = argparse.ArgumentParser(description="元进化与自动化深度集成引擎")
    parser.add_argument('--status', action='store_true', help='显示引擎状态')
    parser.add_argument('--integrate', action='store_true', help='执行深度集成分析')
    parser.add_argument('--cycle', action='store_true', help='运行完整周期')
    parser.add_argument('--cockpit-data', action='store_true', help='获取驾驶舱数据')
    parser.add_argument('--set-auto-adjust', type=str, choices=['true', 'false'], help='设置自动调整开关')
    parser.add_argument('--config', action='store_true', help='显示当前配置')

    args = parser.parse_args()

    engine = EvolutionMetaOptimizationIntegrationEngine()

    if args.status:
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.integrate:
        result = engine.integrate_and_optimize()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.cycle:
        result = engine.run_full_cycle()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))

    elif args.set_auto_adjust:
        config = engine.strategy_config
        config['auto_adjust_enabled'] = args.set_auto_adjust == 'true'
        engine.save_strategy_config(config)
        print(f"自动调整已设置为: {args.set_auto_adjust}")

    elif args.config:
        print(json.dumps(engine.strategy_config, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()