#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能进化闭环自适应增强引擎 (Evolution Adaptive Loop Enhancer)
让进化环能够根据实时执行反馈自动调整进化策略，实现真正的自适应进化闭环。
让系统能够从每轮进化中学习并动态优化决策。

功能：
1. 进化执行实时反馈收集 - 收集每轮进化的实时执行数据
2. 进化策略自适应调整 - 基于反馈动态优化策略参数
3. 自适应决策选择 - 自动选择最佳进化路径
4. 闭环验证与学习 - 验证效果并反馈到决策

集成：支持"自适应进化"、"动态进化"、"闭环增强"、"自适应增强"等关键词触发
"""

import os
import sys
import json
import glob
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPTS)
RUNTIME_STATE = os.path.join(PROJECT, "runtime", "state")
RUNTIME_LOGS = os.path.join(PROJECT, "runtime", "logs")
REFERENCES = os.path.join(PROJECT, "references")


class EvolutionAdaptiveLoopEnhancer:
    """智能进化闭环自适应增强引擎"""

    def __init__(self):
        self.name = "EvolutionAdaptiveLoopEnhancer"
        self.version = "1.0.0"
        self.feedback_path = os.path.join(RUNTIME_STATE, "adaptive_loop_feedback.json")
        self.strategy_path = os.path.join(RUNTIME_STATE, "adaptive_loop_strategy.json")
        self.learning_path = os.path.join(RUNTIME_STATE, "adaptive_loop_learning.json")
        self.config_path = os.path.join(RUNTIME_STATE, "adaptive_loop_config.json")

        self.feedback_data = self._load_feedback()
        self.strategy = self._load_strategy()
        self.learning_data = self._load_learning()
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """加载配置"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "feedback_settings": {
                "collect_execution_time": True,
                "collect_resource_usage": True,
                "collect_success_metrics": True,
                "collect_failure_patterns": True,
                "realtime_monitoring": True
            },
            "adaptation_settings": {
                "enable_auto_adjust": True,
                "learning_rate": 0.1,  # 学习率
                "min_samples_for_adaptation": 3,  # 最少样本数
                "decay_factor": 0.95,  # 衰减因子
                "exploration_rate": 0.2  # 探索率
            },
            "strategy_settings": {
                "enable_adaptive_selection": True,
                "multi_path_evaluation": True,
                "risk_aware_selection": True,
                "confidence_threshold": 0.7
            },
            "learning_settings": {
                "enable_online_learning": True,
                "batch_size": 5,
                "forgetting_factor": 0.8,
                "patternRetention": True
            },
            "last_update": None,
            "total_adaptations": 0
        }

    def _save_config(self):
        """保存配置"""
        try:
            self.config["last_update"] = datetime.now().isoformat()
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def _load_feedback(self) -> Dict:
        """加载反馈数据"""
        if os.path.exists(self.feedback_path):
            try:
                with open(self.feedback_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "feedback_records": [],
            "realtime_metrics": {},
            "last_collected": None
        }

    def _save_feedback(self):
        """保存反馈数据"""
        try:
            self.feedback_data["last_collected"] = datetime.now().isoformat()
            with open(self.feedback_path, "w", encoding="utf-8") as f:
                json.dump(self.feedback_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存反馈数据失败: {e}")

    def _load_strategy(self) -> Dict:
        """加载策略数据"""
        if os.path.exists(self.strategy_path):
            try:
                with open(self.strategy_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "current_strategy": {
                "assume_weight": 0.2,
                "decision_weight": 0.25,
                "execution_weight": 0.3,
                "verify_weight": 0.15,
                "reflect_weight": 0.1
            },
            "path_scores": {},
            "adaptation_history": [],
            "last_adapted": None
        }

    def _save_strategy(self):
        """保存策略数据"""
        try:
            self.strategy["last_adapted"] = datetime.now().isoformat()
            with open(self.strategy_path, "w", encoding="utf-8") as f:
                json.dump(self.strategy, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存策略数据失败: {e}")

    def _load_learning(self) -> Dict:
        """加载学习数据"""
        if os.path.exists(self.learning_path):
            try:
                with open(self.learning_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "learned_patterns": {},
            "successful_strategies": [],
            "failed_strategies": [],
            "adaptation_effects": [],
            "last_learned": None
        }

    def _save_learning(self):
        """保存学习数据"""
        try:
            self.learning_data["last_learned"] = datetime.now().isoformat()
            with open(self.learning_path, "w", encoding="utf-8") as f:
                json.dump(self.learning_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存学习数据失败: {e}")

    def _load_completed_evolutions(self, limit: int = 20) -> List[Dict]:
        """加载已完成的进化记录"""
        evolutions = []
        state_dir = RUNTIME_STATE

        pattern = os.path.join(state_dir, "evolution_completed_*.json")
        files = glob.glob(pattern)

        files.sort(key=os.path.getmtime, reverse=True)

        for file in files[:limit]:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    evolutions.append(data)
            except Exception:
                continue

        return evolutions

    def collect_realtime_feedback(self) -> Dict[str, Any]:
        """收集实时反馈数据"""
        rounds = self._load_completed_evolutions(10)

        if not rounds:
            return {
                "status": "no_data",
                "message": "暂无进化数据可供收集反馈"
            }

        feedback_records = []

        for round_data in rounds:
            record = {
                "round": round_data.get("loop_round", 0),
                "goal": round_data.get("current_goal", ""),
                "status": round_data.get("status", "unknown"),
                "is_completed": round_data.get("is_completed", False),
                "completed_at": round_data.get("completed_at", ""),
                "execution_duration": round_data.get("execution_duration", 0),
                "metrics": self._extract_metrics(round_data)
            }
            feedback_records.append(record)

        self.feedback_data["feedback_records"] = feedback_records
        self.feedback_data["realtime_metrics"] = self._calculate_realtime_metrics(feedback_records)
        self._save_feedback()

        return {
            "status": "collected",
            "records_count": len(feedback_records),
            "metrics": self.feedback_data["realtime_metrics"]
        }

    def _extract_metrics(self, round_data: Dict) -> Dict:
        """提取指标"""
        metrics = {
            "success": round_data.get("is_completed", False),
            "execution_time": round_data.get("execution_duration", 0)
        }

        # 从描述中提取更多信息
        desc = str(round_data.get("做了什么", ""))
        if "校验通过" in desc or "pass" in desc.lower():
            metrics["verification_passed"] = True
        else:
            metrics["verification_passed"] = False

        return metrics

    def _calculate_realtime_metrics(self, records: List[Dict]) -> Dict:
        """计算实时指标"""
        if not records:
            return {}

        total = len(records)
        successful = sum(1 for r in records if r.get("metrics", {}).get("success", False))
        verified = sum(1 for r in records if r.get("metrics", {}).get("verification_passed", False))

        avg_execution_time = sum(
            r.get("execution_duration", 0) for r in records if r.get("execution_duration", 0) > 0
        ) / total if total > 0 else 0

        return {
            "total_rounds": total,
            "successful_rounds": successful,
            "verified_rounds": verified,
            "success_rate": successful / total if total > 0 else 0,
            "verification_rate": verified / total if total > 0 else 0,
            "avg_execution_time": avg_execution_time
        }

    def adapt_strategy(self) -> Dict[str, Any]:
        """自适应调整策略"""
        if not self.config["adaptation_settings"]["enable_auto_adjust"]:
            return {
                "status": "disabled",
                "message": "自适应调整功能已禁用"
            }

        # 收集最新反馈
        feedback_result = self.collect_realtime_feedback()

        if feedback_result.get("status") == "no_data":
            return {
                "status": "no_data",
                "message": "暂无数据可供自适应调整"
            }

        # 基于反馈调整策略
        metrics = self.feedback_data.get("realtime_metrics", {})
        current_strategy = dict(self.strategy["current_strategy"])

        adjustments = []
        new_strategy = dict(current_strategy)

        # 调整1：基于成功率
        success_rate = metrics.get("success_rate", 0)
        if success_rate < 0.7:
            # 成功率低，增加决策和校验权重
            new_strategy["decision_weight"] = min(0.4, current_strategy["decision_weight"] + 0.1)
            new_strategy["verify_weight"] = min(0.25, current_strategy["verify_weight"] + 0.05)
            adjustments.append("成功率低，增加决策和校验权重")
        elif success_rate > 0.9:
            # 成功率高，增加执行和创新权重
            new_strategy["execution_weight"] = min(0.45, current_strategy["execution_weight"] + 0.1)
            adjustments.append("成功率高，增加执行权重尝试更多创新")

        # 调整2：基于验证率
        verification_rate = metrics.get("verification_rate", 0)
        if verification_rate < 0.6:
            new_strategy["verify_weight"] = min(0.3, new_strategy["verify_weight"] + 0.1)
            adjustments.append("验证率低，增加校验权重")

        # 调整3：基于执行时间
        avg_time = metrics.get("avg_execution_time", 0)
        if avg_time > 300:  # 超过5分钟
            new_strategy["execution_weight"] = min(0.5, current_strategy["execution_weight"] + 0.1)
            new_strategy["assume_weight"] = max(0.1, current_strategy["assume_weight"] - 0.05)
            adjustments.append("执行时间长，增加执行权重，减少假设时间")

        # 应用衰减因子
        learning_rate = self.config["adaptation_settings"]["learning_rate"]
        for key in new_strategy:
            if new_strategy[key] != current_strategy[key]:
                diff = new_strategy[key] - current_strategy[key]
                new_strategy[key] = current_strategy[key] + diff * learning_rate

        # 归一化权重
        total = sum(new_strategy.values())
        if abs(total - 1.0) > 0.01:
            for key in new_strategy:
                new_strategy[key] = new_strategy[key] / total

        # 保存策略调整
        self.strategy["current_strategy"] = new_strategy
        self.strategy["adaptation_history"].append({
            "time": datetime.now().isoformat(),
            "original": current_strategy,
            "new": new_strategy,
            "adjustments": adjustments,
            "metrics": metrics
        })
        self.strategy["adaptation_history"] = self.strategy["adaptation_history"][-20:]  # 保留最近20条
        self._save_strategy()

        # 更新配置
        self.config["total_adaptations"] = self.config.get("total_adaptations", 0) + 1
        self._save_config()

        # 记录学习数据
        if success_rate >= 0.8:
            self.learning_data["successful_strategies"].append({
                "time": datetime.now().isoformat(),
                "strategy": new_strategy,
                "metrics": metrics
            })
            self.learning_data["successful_strategies"] = self.learning_data["successful_strategies"][-20:]
        else:
            self.learning_data["failed_strategies"].append({
                "time": datetime.now().isoformat(),
                "strategy": new_strategy,
                "metrics": metrics
            })
            self.learning_data["failed_strategies"] = self.learning_data["failed_strategies"][-20:]

        self.learning_data["adaptation_effects"].append({
            "time": datetime.now().isoformat(),
            "adjustments": adjustments,
            "success_rate": success_rate
        })
        self.learning_data["adaptation_effects"] = self.learning_data["adaptation_effects"][-20:]
        self._save_learning()

        return {
            "status": "adapted",
            "original_strategy": current_strategy,
            "new_strategy": new_strategy,
            "adjustments": adjustments,
            "metrics": metrics,
            "adaptation_count": self.config["total_adaptations"]
        }

    def adaptive_decision_select(self, options: List[Dict]) -> Dict[str, Any]:
        """自适应决策选择 - 自动选择最佳进化路径"""
        if not self.config["strategy_settings"]["enable_adaptive_selection"]:
            return {
                "status": "disabled",
                "message": "自适应选择功能已禁用"
            }

        if not options:
            return {
                "status": "no_options",
                "message": "没有可选择的选项"
            }

        # 获取当前策略权重
        strategy = self.strategy["current_strategy"]

        # 为每个选项打分
        scored_options = []
        for i, option in enumerate(options):
            score = self._calculate_option_score(option, strategy)
            scored_options.append({
                "index": i,
                "option": option,
                "score": score,
                "confidence": self._calculate_confidence(option, score)
            })

        # 按分数排序
        scored_options.sort(key=lambda x: x["score"], reverse=True)

        # 考虑探索率
        exploration_rate = self.config["adaptation_settings"]["exploration_rate"]
        if len(scored_options) > 1 and scored_options[0]["score"] > 0:
            # 有一定概率选择非最优选项进行探索
            import random
            if random.random() < exploration_rate and len(scored_options) > 2:
                selected = scored_options[random.randint(1, min(2, len(scored_options) - 1))]
            else:
                selected = scored_options[0]
        else:
            selected = scored_options[0] if scored_options else {"index": 0, "option": options[0], "score": 0, "confidence": 0}

        # 记录路径得分
        for so in scored_options:
            self.strategy["path_scores"][str(so["index"])] = so["score"]
        self._save_strategy()

        return {
            "status": "selected",
            "selected_index": selected["index"],
            "selected_option": selected["option"],
            "score": selected["score"],
            "confidence": selected["confidence"],
            "all_scores": [{"index": s["index"], "score": s["score"]} for s in scored_options]
        }

    def _calculate_option_score(self, option: Dict, strategy: Dict) -> float:
        """计算选项得分"""
        score = 0.5  # 基础分

        goal = str(option.get("goal", "") or option.get("current_goal", ""))

        # 基于当前策略权重调整得分
        if "假设" in goal or "assume" in goal.lower():
            score += strategy.get("assume_weight", 0.2) * 0.3
        if "决策" in goal or "规划" in goal or "plan" in goal.lower():
            score += strategy.get("decision_weight", 0.25) * 0.3
        if "执行" in goal or "implement" in goal.lower():
            score += strategy.get("execution_weight", 0.3) * 0.3
        if "校验" in goal or "验证" in goal or "verify" in goal.lower():
            score += strategy.get("verify_weight", 0.15) * 0.3
        if "反思" in goal or "优化" in goal or "reflect" in goal.lower():
            score += strategy.get("reflect_weight", 0.1) * 0.3

        # 基于历史学习调整
        learned = self.learning_data.get("learned_patterns", {})
        for pattern, data in learned.items():
            if pattern.lower() in goal.lower():
                score += data.get("weight", 0) * 0.2

        # 基于历史成功/失败调整
        successful = self.learning_data.get("successful_strategies", [])
        for s in successful[-5:]:
            if s.get("strategy"):
                for key, val in s["strategy"].items():
                    if key in goal.lower():
                        score += 0.1

        return min(1.0, max(0.0, score))

    def _calculate_confidence(self, option: Dict, score: float) -> float:
        """计算置信度"""
        # 基于样本数量和分数稳定性计算置信度
        min_samples = self.config["adaptation_settings"]["min_samples_for_adaptation"]
        total_adaptations = self.config.get("total_adaptations", 0)

        if total_adaptations < min_samples:
            return score * 0.5  # 样本少，置信度低

        # 检查分数是否稳定
        recent_adaptations = self.strategy.get("adaptation_history", [])[-5:]
        if len(recent_adaptations) >= 3:
            scores = [a.get("metrics", {}).get("success_rate", 0) for a in recent_adaptations]
            if scores:
                variance = sum((s - sum(scores)/len(scores))**2 for s in scores) / len(scores)
                stability = max(0, 1 - variance * 10)
                return score * (0.5 + 0.5 * stability)

        return score * 0.8

    def verify_and_learn(self, round_id: str, result: Dict) -> Dict[str, Any]:
        """闭环验证与学习"""
        # 记录结果
        feedback_record = {
            "round_id": round_id,
            "time": datetime.now().isoformat(),
            "result": result,
            "verified": result.get("is_completed", False)
        }

        self.feedback_data["feedback_records"].append(feedback_record)
        self.feedback_data["feedback_records"] = self.feedback_data["feedback_records"][-50:]  # 保留最近50条
        self._save_feedback()

        # 学习成功模式
        if result.get("is_completed", False):
            # 提取成功特征
            success_pattern = {
                "goal_type": result.get("current_goal", "")[:50],
                "weight": 1.0
            }

            goal_type = success_pattern["goal_type"]
            if goal_type not in self.learning_data["learned_patterns"]:
                self.learning_data["learned_patterns"][goal_type] = {"count": 0, "weight": 0.5}

            self.learning_data["learned_patterns"][goal_type]["count"] += 1
            current_weight = self.learning_data["learned_patterns"][goal_type]["weight"]
            self.learning_data["learned_patterns"][goal_type]["weight"] = min(1.0,
                current_weight + self.config["adaptation_settings"]["learning_rate"]
            )
        else:
            # 学习失败模式
            goal_type = result.get("current_goal", "")[:50]
            if goal_type in self.learning_data["learned_patterns"]:
                current_weight = self.learning_data["learned_patterns"][goal_type]["weight"]
                self.learning_data["learned_patterns"][goal_type]["weight"] = max(0.1,
                    current_weight - self.config["adaptation_settings"]["learning_rate"]
                )

        self._save_learning()

        # 判断是否需要触发自适应调整
        total_rounds = len(self.feedback_data["feedback_records"])
        if total_rounds >= self.config["adaptation_settings"]["min_samples_for_adaptation"]:
            recent_records = self.feedback_data["feedback_records"][-5:]
            recent_success_rate = sum(1 for r in recent_records if r.get("verified", False)) / len(recent_records)

            needs_adaptation = recent_success_rate < self.config["strategy_settings"]["confidence_threshold"]

            return {
                "status": "learned",
                "round_id": round_id,
                "verified": result.get("is_completed", False),
                "needs_adaptation": needs_adaptation,
                "recent_success_rate": recent_success_rate
            }

        return {
            "status": "learned",
            "round_id": round_id,
            "verified": result.get("is_completed", False),
            "needs_adaptation": False,
            "message": "样本不足，暂不触发自适应调整"
        }

    def get_adaptive_status(self) -> Dict[str, Any]:
        """获取自适应状态"""
        # 获取最新反馈
        feedback = self.feedback_data.get("realtime_metrics", {})

        return {
            "name": self.name,
            "version": self.version,
            "config": {
                "auto_adjust": self.config["adaptation_settings"]["enable_auto_adjust"],
                "adaptive_selection": self.config["strategy_settings"]["enable_adaptive_selection"],
                "total_adaptations": self.config.get("total_adaptations", 0)
            },
            "current_strategy": self.strategy["current_strategy"],
            "metrics": {
                "total_feedback": len(self.feedback_data.get("feedback_records", [])),
                "success_rate": feedback.get("success_rate", 0),
                "verification_rate": feedback.get("verification_rate", 0)
            },
            "learning": {
                "learned_patterns": len(self.learning_data.get("learned_patterns", {})),
                "successful_strategies": len(self.learning_data.get("successful_strategies", [])),
                "failed_strategies": len(self.learning_data.get("failed_strategies", []))
            },
            "adaptation_history": len(self.strategy.get("adaptation_history", []))
        }

    def get_adaptive_recommendations(self) -> Dict[str, Any]:
        """获取自适应建议"""
        # 收集反馈
        feedback = self.collect_realtime_feedback()

        if feedback.get("status") == "no_data":
            return {
                "status": "no_data",
                "recommendations": ["暂无足够数据进行自适应建议"]
            }

        recommendations = []

        metrics = self.feedback_data.get("realtime_metrics", {})

        # 基于当前状态生成建议
        success_rate = metrics.get("success_rate", 0)
        if success_rate < 0.7:
            recommendations.append({
                "type": "warning",
                "priority": "high",
                "description": f"当前成功率较低 ({success_rate:.1%})",
                "action": "建议调用 adapt_strategy() 进行策略自适应调整"
            })

        # 检查策略是否需要更新
        total_adaptations = self.config.get("total_adaptations", 0)
        if total_adaptations == 0:
            recommendations.append({
                "type": "suggestion",
                "priority": "medium",
                "description": "尚未进行过策略自适应调整",
                "action": "建议调用 adapt_strategy() 初始化自适应策略"
            })

        # 检查学习效果
        learned_count = len(self.learning_data.get("learned_patterns", {}))
        if learned_count < 3:
            recommendations.append({
                "type": "suggestion",
                "priority": "low",
                "description": f"学习数据较少 ({learned_count}个模式)",
                "action": "继续执行更多进化轮次以积累学习数据"
            })

        return {
            "status": "ready",
            "recommendations": recommendations,
            "current_metrics": metrics,
            "strategy": self.strategy["current_strategy"]
        }


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="智能进化闭环自适应增强引擎")
    parser.add_argument("command", nargs="?", default="status",
                       help="命令: status|collect|adapt|select|verify|recommend")
    parser.add_argument("--options", type=str, help="选项列表(JSON格式，用于select命令)")
    parser.add_argument("--round-id", type=str, help="轮次ID(用于verify命令)")
    parser.add_argument("--result", type=str, help="结果(JSON格式，用于verify命令)")

    args = parser.parse_args()

    enhancer = EvolutionAdaptiveLoopEnhancer()

    if args.command == "status":
        result = enhancer.get_adaptive_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "collect":
        result = enhancer.collect_realtime_feedback()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "adapt":
        result = enhancer.adapt_strategy()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "select":
        try:
            options = json.loads(args.options) if args.options else []
            result = enhancer.adaptive_decision_select(options)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"解析选项失败: {e}")
            sys.exit(1)

    elif args.command == "verify":
        if not args.round_id or not args.result:
            print("错误: verify命令需要 --round-id 和 --result 参数")
            sys.exit(1)
        try:
            result_data = json.loads(args.result)
            result = enhancer.verify_and_learn(args.round_id, result_data)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"解析结果失败: {e}")
            sys.exit(1)

    elif args.command == "recommend":
        result = enhancer.get_adaptive_recommendations()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {args.command}")
        print("可用命令: status, collect, adapt, select, verify, recommend")
        sys.exit(1)


if __name__ == "__main__":
    main()