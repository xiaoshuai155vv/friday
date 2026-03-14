#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环自适应学习与动态策略优化引擎

基于 round 351 的自适应触发与自主决策引擎，增强系统的自适应学习能力。
让系统能够自动分析进化执行结果、提取成功模式、识别失败原因、动态调整进化策略参数，
实现真正的「学会如何进化得更好」的递归优化能力。

功能：
1. 进化执行结果自动分析（成功率、效率、资源消耗）
2. 成功模式提取与失败原因识别
3. 策略参数动态调整（触发阈值、决策权重、执行策略）
4. 递归优化闭环（分析→学习→调整→执行→验证→再分析）
"""

import json
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import re


class AdaptiveLearningStrategyEngine:
    """自适应学习与动态策略优化引擎"""

    def __init__(self, runtime_dir: str = None):
        """初始化引擎"""
        if runtime_dir is None:
            self.runtime_dir = Path(__file__).parent.parent / "runtime"
        else:
            self.runtime_dir = Path(runtime_dir)

        self.state_dir = self.runtime_dir / "state"
        self.logs_dir = self.runtime_dir / "logs"
        self.data_dir = self.runtime_dir / "data"

        # 确保目录存在
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 策略参数存储文件
        self.strategy_params_file = self.data_dir / "adaptive_strategy_params.json"

        # 初始化默认策略参数
        self.default_params = {
            "trigger_thresholds": {
                "system_load_high": 80.0,
                "system_load_low": 30.0,
                "health_score_low": 60.0,
                "efficiency_low": 0.5,
                "time_since_last_evolution_minutes": 60
            },
            "decision_weights": {
                "system_load": 0.2,
                "health_score": 0.25,
                "efficiency": 0.2,
                "capability_gaps": 0.2,
                "time_based": 0.15
            },
            "execution_strategies": {
                "conservative": {"max_concurrent_engines": 3, "timeout_factor": 1.5},
                "balanced": {"max_concurrent_engines": 5, "timeout_factor": 1.0},
                "aggressive": {"max_concurrent_engines": 8, "timeout_factor": 0.8}
            },
            "learning_config": {
                "history_window_rounds": 50,
                "success_threshold": 0.7,
                "failure_threshold": 0.3,
                "adaptation_rate": 0.1,
                "min_samples_for_learning": 5
            }
        }

        # 加载策略参数
        self.strategy_params = self._load_strategy_params()

    def _load_strategy_params(self) -> Dict:
        """加载策略参数"""
        if self.strategy_params_file.exists():
            try:
                with open(self.strategy_params_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载策略参数失败: {e}，使用默认参数")

        return self.default_params.copy()

    def _save_strategy_params(self):
        """保存策略参数"""
        try:
            with open(self.strategy_params_file, 'w', encoding='utf-8') as f:
                json.dump(self.strategy_params, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存策略参数失败: {e}")
            return False

    def _get_evolution_history(self, rounds: int = 50) -> List[Dict]:
        """获取进化历史"""
        history = []

        # 尝试从 evolution_completed_*.json 文件中获取历史
        state_dir = self.state_dir
        if state_dir.exists():
            for f in state_dir.glob("evolution_completed_*.json"):
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        if 'loop_round' in data:
                            history.append(data)
                except Exception:
                    pass

        # 按轮次排序
        history.sort(key=lambda x: x.get('loop_round', 0), reverse=True)
        return history[:rounds]

    def analyze_evolution_results(self) -> Dict[str, Any]:
        """分析进化执行结果"""
        history = self._get_evolution_history(
            self.strategy_params.get("learning_config", {}).get("history_window_rounds", 50)
        )

        if not history:
            return {
                "status": "no_data",
                "message": "无足够进化历史数据进行分析",
                "statistics": {}
            }

        # 统计信息
        total_rounds = len(history)
        completed_rounds = sum(1 for h in history if h.get('status') == '已完成')
        failed_rounds = sum(1 for h in history if h.get('status') in ['失败', 'stale_failed'])

        # 计算成功率
        success_rate = completed_rounds / total_rounds if total_rounds > 0 else 0

        # 分析失败原因
        failure_reasons = {}
        for h in history:
            if h.get('status') in ['失败', 'stale_failed']:
                desc = h.get('做了什么', ['未知'])[0] if h.get('做了什么') else '未知'
                failure_reasons[desc] = failure_reasons.get(desc, 0) + 1

        # 分析成功模式
        successful_rounds = [h for h in history if h.get('status') == '已完成']
        common_patterns = {}

        for h in successful_rounds:
            actions = h.get('做了什么', [])
            for action in actions:
                # 提取关键模式
                if '创建' in action and '模块' in action:
                    common_patterns['create_module'] = common_patterns.get('create_module', 0) + 1
                if '集成' in action:
                    common_patterns['integration'] = common_patterns.get('integration', 0) + 1
                if '优化' in action:
                    common_patterns['optimization'] = common_patterns.get('optimization', 0) + 1

        return {
            "status": "success",
            "total_rounds": total_rounds,
            "completed_rounds": completed_rounds,
            "failed_rounds": failed_rounds,
            "success_rate": success_rate,
            "failure_reasons": failure_reasons,
            "successful_patterns": common_patterns,
            "recent_history": history[:10]
        }

    def extract_success_patterns(self) -> Dict[str, Any]:
        """提取成功模式"""
        history = self._get_evolution_history(
            self.strategy_params.get("learning_config", {}).get("history_window_rounds", 50)
        )

        successful = [h for h in history if h.get('status') == '已完成']

        if not successful:
            return {
                "status": "no_data",
                "message": "无成功案例可供分析"
            }

        # 分析成功案例的共同特征
        patterns = {
            "module_creation": 0,
            "integration": 0,
            "optimization": 0,
            "testing": 0
        }

        for h in successful:
            actions = h.get('做了什么', [])
            for action in actions:
                if '创建' in action and '模块' in action:
                    patterns['module_creation'] += 1
                if '集成' in action:
                    patterns['integration'] += 1
                if '优化' in action:
                    patterns['optimization'] += 1
                if '测试' in action or '校验' in action:
                    patterns['testing'] += 1

        # 计算权重
        total = sum(patterns.values())
        if total > 0:
            pattern_weights = {k: v / total for k, v in patterns.items()}
        else:
            pattern_weights = patterns

        return {
            "status": "success",
            "patterns": patterns,
            "pattern_weights": pattern_weights,
            "sample_size": len(successful)
        }

    def identify_failure_causes(self) -> Dict[str, Any]:
        """识别失败原因"""
        history = self._get_evolution_history(
            self.strategy_params.get("learning_config", {}).get("history_window_rounds", 50)
        )

        failed = [h for h in history if h.get('status') in ['失败', 'stale_failed', '未完成']]

        if not failed:
            return {
                "status": "no_failures",
                "message": "近期无失败案例"
            }

        # 分析失败原因模式
        causes = {}
        for h in failed:
            # 尝试从做了什么字段推断失败原因
            actions = h.get('做了什么', [])
            for action in actions:
                if '未' in action or '失败' in action:
                    causes[action] = causes.get(action, 0) + 1

        return {
            "status": "success",
            "failure_causes": causes,
            "failure_count": len(failed),
            "failure_rate": len(failed) / len(history) if history else 0
        }

    def adjust_strategy_params(self, analysis_result: Dict = None) -> Dict[str, Any]:
        """调整策略参数"""
        if analysis_result is None:
            analysis_result = self.analyze_evolution_results()

        if analysis_result.get('status') == 'no_data':
            return {
                "status": "skipped",
                "message": "无足够数据进行策略调整"
            }

        success_rate = analysis_result.get('success_rate', 0.5)
        learning_config = self.strategy_params.get("learning_config", {})
        adaptation_rate = learning_config.get("adaptation_rate", 0.1)

        # 基于成功率调整参数
        params = self.strategy_params

        # 调整触发阈值
        trigger_thresholds = params.get("trigger_thresholds", {})

        if success_rate > learning_config.get("success_threshold", 0.7):
            # 成功率高，可以更激进
            trigger_thresholds["system_load_high"] = max(50.0,
                trigger_thresholds.get("system_load_high", 80.0) - adaptation_rate * 10)
            trigger_thresholds["health_score_low"] = max(40.0,
                trigger_thresholds.get("health_score_low", 60.0) - adaptation_rate * 5)
        elif success_rate < learning_config.get("failure_threshold", 0.3):
            # 成功率低，应该更保守
            trigger_thresholds["system_load_high"] = min(95.0,
                trigger_thresholds.get("system_load_high", 80.0) + adaptation_rate * 10)
            trigger_thresholds["health_score_low"] = min(80.0,
                trigger_thresholds.get("health_score_low", 60.0) + adaptation_rate * 5)

        # 调整决策权重
        decision_weights = params.get("decision_weights", {})

        # 基于失败率调整权重
        failure_rate = 1 - success_rate
        if failure_rate > 0.3:
            # 失败率高，增加健康权重
            decision_weights["health_score"] = min(0.4,
                decision_weights.get("health_score", 0.25) + adaptation_rate * 0.05)
            decision_weights["efficiency"] = min(0.35,
                decision_weights.get("efficiency", 0.2) + adaptation_rate * 0.05)

        params["trigger_thresholds"] = trigger_thresholds
        params["decision_weights"] = decision_weights

        # 保存调整后的参数
        self._save_strategy_params()

        return {
            "status": "success",
            "adjusted_params": {
                "trigger_thresholds": trigger_thresholds,
                "decision_weights": decision_weights
            },
            "success_rate": success_rate,
            "adaptation_rate": adaptation_rate
        }

    def get_current_strategy(self) -> Dict[str, Any]:
        """获取当前策略配置"""
        return {
            "trigger_thresholds": self.strategy_params.get("trigger_thresholds", {}),
            "decision_weights": self.strategy_params.get("decision_weights", {}),
            "execution_strategies": self.strategy_params.get("execution_strategies", {}),
            "learning_config": self.strategy_params.get("learning_config", {})
        }

    def reset_to_defaults(self) -> Dict[str, Any]:
        """重置为默认策略"""
        self.strategy_params = self.default_params.copy()
        self._save_strategy_params()

        return {
            "status": "success",
            "message": "已重置为默认策略参数"
        }

    def run_full_cycle(self) -> Dict[str, Any]:
        """运行完整的学习优化周期"""
        # 1. 分析进化结果
        analysis = self.analyze_evolution_results()

        # 2. 提取成功模式
        patterns = self.extract_success_patterns()

        # 3. 识别失败原因
        failures = self.identify_failure_causes()

        # 4. 调整策略参数
        adjustment = self.adjust_strategy_params(analysis)

        # 5. 获取当前策略
        current_strategy = self.get_current_strategy()

        return {
            "analysis": analysis,
            "success_patterns": patterns,
            "failure_causes": failures,
            "adjustment": adjustment,
            "current_strategy": current_strategy,
            "completed_at": datetime.now().isoformat()
        }

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        analysis = self.analyze_evolution_results()
        current_strategy = self.get_current_strategy()

        return {
            "engine": "adaptive_learning_strategy",
            "version": "1.0.0",
            "status": "active",
            "current_strategy": current_strategy,
            "recent_analysis": {
                "total_rounds": analysis.get("total_rounds", 0),
                "success_rate": analysis.get("success_rate", 0),
                "failed_rounds": analysis.get("failed_rounds", 0)
            }
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能全场景进化环自适应学习与动态策略优化引擎"
    )

    parser.add_argument('--analyze', action='store_true',
                        help='分析进化执行结果')
    parser.add_argument('--patterns', action='store_true',
                        help='提取成功模式')
    parser.add_argument('--failures', action='store_true',
                        help='识别失败原因')
    parser.add_argument('--adjust', action='store_true',
                        help='调整策略参数')
    parser.add_argument('--strategy', action='store_true',
                        help='获取当前策略配置')
    parser.add_argument('--reset', action='store_true',
                        help='重置为默认策略')
    parser.add_argument('--full-cycle', action='store_true',
                        help='运行完整的学习优化周期')
    parser.add_argument('--status', action='store_true',
                        help='获取引擎状态')

    args = parser.parse_args()

    engine = AdaptiveLearningStrategyEngine()

    if args.analyze:
        result = engine.analyze_evolution_results()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.patterns:
        result = engine.extract_success_patterns()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.failures:
        result = engine.identify_failure_causes()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.adjust:
        result = engine.adjust_strategy_params()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.strategy:
        result = engine.get_current_strategy()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.reset:
        result = engine.reset_to_defaults()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.full_cycle:
        result = engine.run_full_cycle()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.status:
        result = engine.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 默认显示状态
        result = engine.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()