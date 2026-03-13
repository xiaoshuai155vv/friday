#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能进化多轮迭代协同增强引擎 (Evolution Iteration Coordination Engine)
让更多引擎能够利用自适应优化结果，形成更紧密的「执行→分析→优化→再执行」闭环，
增强进化环的多轮持续进化能力。

功能：
1. 多引擎协同接口 - 让各引擎能够调用自适应优化引擎
2. 迭代状态追踪 - 追踪多轮进化状态和优化效果
3. 跨轮知识传递 - 将上一轮优化结果传递给下一轮
4. 闭环验证 - 验证闭环是否真正形成

集成：支持"多轮协同"、"迭代进化"、"协同进化"、"进化协调"等关键词触发
"""

import os
import sys
import json
import glob
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import importlib.util

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPTS)
RUNTIME_STATE = os.path.join(PROJECT, "runtime", "state")
RUNTIME_LOGS = os.path.join(PROJECT, "runtime", "logs")
REFERENCES = os.path.join(PROJECT, "references")


class EvolutionIterationCoordinator:
    """智能进化多轮迭代协同增强引擎"""

    def __init__(self):
        self.name = "EvolutionIterationCoordinator"
        self.version = "1.0.0"
        self.state_path = os.path.join(RUNTIME_STATE, "evolution_iteration_state.json")
        self.knowledge_path = os.path.join(RUNTIME_STATE, "evolution_cross_round_knowledge.json")
        self.closure_path = os.path.join(RUNTIME_STATE, "evolution_closure_verification.json")
        self.coordination_history_path = os.path.join(RUNTIME_STATE, "evolution_coordination_history.json")

        self.state = self._load_state()
        self.knowledge = self._load_knowledge()
        self.closure = self._load_closure()
        self.coordination_history = self._load_coordination_history()

        # 尝试加载自适应优化引擎
        self.optimizer = self._load_optimizer()

    def _load_state(self) -> Dict:
        """加载迭代状态"""
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "current_iteration": 0,
            "iterations": [],
            "active_engines": [],
            "engine_status": {},
            "last_coordination_time": None,
            "cross_iteration_data": {}
        }

    def _save_state(self):
        """保存迭代状态"""
        try:
            with open(self.state_path, "w", encoding="utf-8") as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存迭代状态失败: {e}")

    def _load_knowledge(self) -> Dict:
        """加载跨轮知识"""
        if os.path.exists(self.knowledge_path):
            try:
                with open(self.knowledge_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "learned_patterns": [],
            "optimization_results": [],
            "successful_strategies": [],
            "failed_strategies": [],
            "engine_effectiveness_history": {},
            "knowledge_transfers": []
        }

    def _save_knowledge(self):
        """保存跨轮知识"""
        try:
            with open(self.knowledge_path, "w", encoding="utf-8") as f:
                json.dump(self.knowledge, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存跨轮知识失败: {e}")

    def _load_closure(self) -> Dict:
        """加载闭环验证数据"""
        if os.path.exists(self.closure_path):
            try:
                with open(self.closure_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "verification_count": 0,
            "closure_detected": False,
            "closure_loops": [],
            "open_feedback_paths": [],
            "feedback_chain_integrity": 0.0
        }

    def _save_closure(self):
        """保存闭环验证数据"""
        try:
            with open(self.closure_path, "w", encoding="utf-8") as f:
                json.dump(self.closure, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存闭环验证数据失败: {e}")

    def _load_coordination_history(self) -> List[Dict]:
        """加载协同历史"""
        if os.path.exists(self.coordination_history_path):
            try:
                with open(self.coordination_history_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_coordination_history(self):
        """保存协同历史"""
        try:
            with open(self.coordination_history_path, "w", encoding="utf-8") as f:
                json.dump(self.coordination_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存协同历史失败: {e}")

    def _load_optimizer(self):
        """加载自适应优化引擎"""
        try:
            optimizer_path = os.path.join(SCRIPTS, "evolution_adaptive_optimizer.py")
            if os.path.exists(optimizer_path):
                spec = importlib.util.spec_from_file_location("evolution_adaptive_optimizer", optimizer_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    return module.EvolutionAdaptiveOptimizer()
        except Exception as e:
            print(f"加载自适应优化引擎失败: {e}")
        return None

    def register_engine(self, engine_name: str, engine_info: Dict) -> Dict:
        """注册引擎到协同网络"""
        if engine_name not in self.state["active_engines"]:
            self.state["active_engines"].append(engine_name)

        self.state["engine_status"][engine_name] = {
            "registered_at": datetime.now().isoformat(),
            "capabilities": engine_info.get("capabilities", []),
            "can_call_optimizer": engine_info.get("can_call_optimizer", True),
            "iteration_count": 0,
            "last_active": None,
            "coordination_count": 0
        }

        self._save_state()
        return {"status": "success", "engine": engine_name, "message": f"引擎 {engine_name} 已注册到协同网络"}

    def start_iteration(self, iteration_id: int, context: Dict) -> Dict:
        """开始新的迭代"""
        self.state["current_iteration"] = iteration_id

        iteration_data = {
            "iteration_id": iteration_id,
            "start_time": datetime.now().isoformat(),
            "context": context,
            "status": "in_progress",
            "engines_involved": [],
            "optimization_applied": False,
            "results": {}
        }

        self.state["iterations"].append(iteration_data)
        self.state["last_coordination_time"] = datetime.now().isoformat()

        self._save_state()
        return {"status": "success", "iteration_id": iteration_id, "message": f"迭代 {iteration_id} 已开始"}

    def apply_optimization(self, iteration_id: int) -> Dict:
        """在迭代中应用自适应优化"""
        if not self.optimizer:
            return {"status": "warning", "message": "自适应优化引擎不可用，使用默认策略"}

        try:
            # 获取优化建议
            recommendations = self.optimizer.get_adaptive_recommendations()

            # 更新迭代状态
            for iteration in self.state["iterations"]:
                if iteration.get("iteration_id") == iteration_id:
                    iteration["optimization_applied"] = True
                    iteration["optimization_results"] = recommendations
                    break

            # 保存优化结果到跨轮知识
            self.knowledge["optimization_results"].append({
                "iteration_id": iteration_id,
                "timestamp": datetime.now().isoformat(),
                "recommendations": recommendations
            })
            self._save_knowledge()

            # 记录协同历史
            self._record_coordination("optimization_applied", {
                "iteration_id": iteration_id,
                "recommendations": recommendations
            })

            self._save_state()
            return {"status": "success", "recommendations": recommendations}
        except Exception as e:
            return {"status": "error", "message": f"应用优化失败: {e}"}

    def track_engine_progress(self, engine_name: str, progress_data: Dict) -> Dict:
        """追踪引擎进度"""
        if engine_name not in self.state["engine_status"]:
            return {"status": "error", "message": f"引擎 {engine_name} 未注册"}

        self.state["engine_status"][engine_name]["iteration_count"] += 1
        self.state["engine_status"][engine_name]["last_active"] = datetime.now().isoformat()
        self.state["engine_status"][engine_name]["coordination_count"] += 1

        # 保存进度数据
        if engine_name not in self.state["cross_iteration_data"]:
            self.state["cross_iteration_data"][engine_name] = []

        self.state["cross_iteration_data"][engine_name].append({
            "timestamp": datetime.now().isoformat(),
            "progress": progress_data
        })

        self._save_state()
        return {"status": "success", "engine": engine_name, "message": "进度已追踪"}

    def transfer_knowledge(self, from_iteration: int, to_iteration: int) -> Dict:
        """跨轮知识传递"""
        # 从历史中提取相关知识
        transferred_knowledge = {
            "from_iteration": from_iteration,
            "to_iteration": to_iteration,
            "timestamp": datetime.now().isoformat(),
            "learned_patterns": [],
            "optimization_results": [],
            "strategy_adjustments": []
        }

        # 提取成功的策略
        for opt_result in self.knowledge["optimization_results"]:
            if opt_result.get("iteration_id") == from_iteration:
                transferred_knowledge["optimization_results"].append(opt_result)

        # 提取成功的模式
        for pattern in self.knowledge["successful_strategies"]:
            transferred_knowledge["learned_patterns"].append(pattern)

        # 记录知识传递
        self.knowledge["knowledge_transfers"].append(transferred_knowledge)
        self._save_knowledge()

        return {"status": "success", "knowledge": transferred_knowledge}

    def verify_closure(self) -> Dict:
        """验证闭环是否形成"""
        # 检查是否形成完整的反馈闭环
        closure_status = {
            "verification_time": datetime.now().isoformat(),
            "closure_detected": False,
            "feedback_chain": [],
            "integrity_score": 0.0,
            "open_paths": [],
            "recommendations": []
        }

        # 检查迭代数据是否完整
        has_iterations = len(self.state["iterations"]) > 0
        has_optimizations = any(it.get("optimization_applied", False) for it in self.state["iterations"])
        has_knowledge_transfer = len(self.knowledge.get("knowledge_transfers", [])) > 0

        # 构建反馈链
        if has_iterations:
            closure_status["feedback_chain"].append("迭代执行")
        if has_optimizations:
            closure_status["feedback_chain"].append("优化应用")
        if has_knowledge_transfer:
            closure_status["feedback_chain"].append("知识传递")

        # 计算闭环完整性
        required_links = 3
        actual_links = len(closure_status["feedback_chain"])
        closure_status["integrity_score"] = actual_links / required_links

        # 判断闭环是否形成
        closure_status["closure_detected"] = closure_status["integrity_score"] >= 0.67

        # 识别开放的反馈路径
        if not closure_status["closure_detected"]:
            if not has_iterations:
                closure_status["open_paths"].append("迭代执行路径未完成")
            if not has_optimizations:
                closure_status["open_paths"].append("优化应用路径未完成")
            if not has_knowledge_transfer:
                closure_status["open_paths"].append("知识传递路径未完成")

        # 生成建议
        if closure_status["closure_detected"]:
            closure_status["recommendations"].append("闭环已形成，可继续增强多轮协同")
        else:
            if not has_iterations:
                closure_status["recommendations"].append("建议先执行至少一个完整迭代")
            if not has_optimizations:
                closure_status["recommendations"].append("建议应用自适应优化结果")
            if not has_knowledge_transfer:
                closure_status["recommendations"].append("建议实现跨轮知识传递")

        # 更新闭环验证数据
        self.closure["verification_count"] += 1
        self.closure["closure_detected"] = closure_status["closure_detected"]
        self.closure["feedback_chain_integrity"] = closure_status["integrity_score"]
        self.closure["open_feedback_paths"] = closure_status["open_paths"]

        if closure_status["closure_detected"]:
            self.closure["closure_loops"].append({
                "timestamp": datetime.now().isoformat(),
                "integrity_score": closure_status["integrity_score"]
            })

        self._save_closure()

        return closure_status

    def get_coordination_status(self) -> Dict:
        """获取协同状态"""
        active_count = len(self.state["active_engines"])
        total_iterations = len(self.state["iterations"])
        completed_iterations = sum(1 for it in self.state["iterations"] if it.get("status") == "completed")
        optimizations_applied = sum(1 for it in self.state["iterations"] if it.get("optimization_applied", False))

        closure_status = self.verify_closure()

        return {
            "active_engines": active_count,
            "total_iterations": total_iterations,
            "completed_iterations": completed_iterations,
            "optimizations_applied": optimizations_applied,
            "closure_status": closure_status,
            "knowledge_transfers": len(self.knowledge.get("knowledge_transfers", [])),
            "last_coordination": self.state.get("last_coordination_time")
        }

    def get_engine_network(self) -> Dict:
        """获取引擎协同网络视图"""
        network = {
            "engines": [],
            "coordination_links": [],
            "total_coordinations": 0
        }

        for engine_name, status in self.state["engine_status"].items():
            network["engines"].append({
                "name": engine_name,
                "iterations": status.get("iteration_count", 0),
                "last_active": status.get("last_active"),
                "coordination_count": status.get("coordination_count", 0)
            })
            network["total_coordinations"] += status.get("coordination_count", 0)

        # 模拟协同链接（实际可根据调用关系生成）
        active_engines = list(self.state["engine_status"].keys())
        for i, engine_a in enumerate(active_engines):
            for engine_b in active_engines[i+1:]:
                network["coordination_links"].append({
                    "from": engine_a,
                    "to": engine_b,
                    "type": "collaboration"
                })

        return network

    def complete_iteration(self, iteration_id: int, results: Dict) -> Dict:
        """完成迭代"""
        for iteration in self.state["iterations"]:
            if iteration.get("iteration_id") == iteration_id:
                iteration["status"] = "completed"
                iteration["end_time"] = datetime.now().isoformat()
                iteration["results"] = results
                break

        # 记录协同历史
        self._record_coordination("iteration_completed", {
            "iteration_id": iteration_id,
            "results": results
        })

        self._save_state()
        return {"status": "success", "iteration_id": iteration_id, "message": "迭代已完成"}

    def _record_coordination(self, action: str, data: Dict):
        """记录协同操作"""
        self.coordination_history.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "data": data
        })

        # 保持历史记录在合理范围内
        if len(self.coordination_history) > 1000:
            self.coordination_history = self.coordination_history[-500:]

        self._save_coordination_history()

    def get_recommendations(self) -> Dict:
        """获取协同优化建议"""
        status = self.get_coordination_status()
        closure = status.get("closure_status", {})
        recommendations = []

        # 基于状态生成建议
        if not closure.get("closure_detected", False):
            for path in closure.get("open_paths", []):
                recommendations.append(f"修复: {path}")

        if status["active_engines"] < 3:
            recommendations.append("建议注册更多引擎到协同网络")

        if status["optimizations_applied"] == 0 and status["total_iterations"] > 0:
            recommendations.append("建议在迭代中应用自适应优化")

        if status["knowledge_transfers"] == 0 and status["total_iterations"] > 1:
            recommendations.append("建议实现跨轮知识传递")

        if closure.get("closure_detected", False):
            recommendations.append("闭环已形成，可增强多轮迭代深度")

        return {
            "status": "success",
            "recommendations": recommendations,
            "closure_ready": closure.get("closure_detected", False),
            "integrity_score": closure.get("integrity_score", 0.0)
        }


def main():
    """主函数 - 支持命令行调用"""
    import argparse
    parser = argparse.ArgumentParser(description="智能进化多轮迭代协同增强引擎")
    parser.add_argument("command", nargs="?", default="status",
                       help="命令: status/register/start/apply/track/transfer/verify/network/recommendations/complete")
    parser.add_argument("--engine", type=str, help="引擎名称")
    parser.add_argument("--info", type=str, help="引擎信息 (JSON)")
    parser.add_argument("--iteration", type=int, help="迭代ID")
    parser.add_argument("--context", type=str, help="上下文 (JSON)")
    parser.add_argument("--progress", type=str, help="进度数据 (JSON)")
    parser.add_argument("--from-iter", type=int, help="源迭代ID")
    parser.add_argument("--to-iter", type=int, help="目标迭代ID")
    parser.add_argument("--results", type=str, help="结果数据 (JSON)")

    args = parser.parse_args()
    coordinator = EvolutionIterationCoordinator()

    if args.command == "status":
        result = coordinator.get_coordination_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "register":
        if not args.engine:
            print("错误: 需要 --engine 参数")
            return
        engine_info = json.loads(args.info) if args.info else {}
        result = coordinator.register_engine(args.engine, engine_info)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "start":
        if args.iteration is None:
            print("错误: 需要 --iteration 参数")
            return
        context = json.loads(args.context) if args.context else {}
        result = coordinator.start_iteration(args.iteration, context)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "apply":
        if args.iteration is None:
            print("错误: 需要 --iteration 参数")
            return
        result = coordinator.apply_optimization(args.iteration)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "track":
        if not args.engine or not args.progress:
            print("错误: 需要 --engine 和 --progress 参数")
            return
        progress_data = json.loads(args.progress)
        result = coordinator.track_engine_progress(args.engine, progress_data)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "transfer":
        if args.from_iter is None or args.to_iter is None:
            print("错误: 需要 --from-iter 和 --to-iter 参数")
            return
        result = coordinator.transfer_knowledge(args.from_iter, args.to_iter)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "verify":
        result = coordinator.verify_closure()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "network":
        result = coordinator.get_engine_network()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "recommendations":
        result = coordinator.get_recommendations()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "complete":
        if args.iteration is None or not args.results:
            print("错误: 需要 --iteration 和 --results 参数")
            return
        results = json.loads(args.results)
        result = coordinator.complete_iteration(args.iteration, results)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {args.command}")
        print("可用命令: status, register, start, apply, track, transfer, verify, network, recommendations, complete")


if __name__ == "__main__":
    main()