#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环跨引擎深度协同自适应优化增强引擎
================================================================

round 421: 基于 round 402/349 的跨引擎协同引擎和 round 237/363 的自适应优化引擎，
创建深度协同自适应优化增强引擎，实现跨引擎智能协同与自适应优化的完整闭环。

功能：
1. 跨引擎智能协同增强 - 让进化引擎能够更智能地协同工作
2. 自适应优化增强 - 从历史执行中自动发现优化机会
3. 深度集成 - 实现协同→优化→验证→学习完整闭环
4. 智能调度 - 基于实时状态动态调整引擎协作策略
5. 效果验证与反馈学习 - 自动验证优化效果并持续改进

version: 1.0.0
"""

import json
import os
import sys
import time
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from collections import deque, defaultdict
from dataclasses import dataclass, field

# 添加 scripts 目录到路径以导入依赖模块
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

# 路径定义
RUNTIME_STATE = os.path.join(PROJECT_ROOT, "runtime", "state")
RUNTIME_LOGS = os.path.join(PROJECT_ROOT, "runtime", "logs")
REFERENCES = os.path.join(PROJECT_ROOT, "references")


@dataclass
class EngineCollaborationMetrics:
    """引擎协作指标"""
    engine_pair: str = ""
    collaboration_count: int = 0
    success_rate: float = 1.0
    avg_execution_time: float = 0.0
    last_collaboration: str = ""


@dataclass
class OptimizationOpportunity:
    """优化机会"""
    opportunity_id: str = ""
    opportunity_type: str = ""
    description: str = ""
    affected_engines: List[str] = field(default_factory=list)
    expected_improvement: float = 0.0
    confidence: float = 0.0
    status: str = "identified"  # identified, analyzed, applied, verified
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CollaborationResult:
    """协作结果"""
    collaboration_id: str = ""
    engines: List[str] = field(default_factory=list)
    task_type: str = ""
    success: bool = False
    execution_time: float = 0.0
    optimization_applied: bool = False
    improvement_score: float = 0.0
    lessons_learned: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class CrossEngineDeepCollaborationOptimizer:
    """跨引擎深度协同自适应优化增强引擎"""

    def __init__(self):
        self.name = "CrossEngineDeepCollaborationOptimizer"
        self.version = "1.0.0"

        # 数据存储路径
        self.collaboration_metrics_path = os.path.join(
            RUNTIME_STATE, "cross_engine_collaboration_metrics.json"
        )
        self.optimization_opportunities_path = os.path.join(
            RUNTIME_STATE, "optimization_opportunities.json"
        )
        self.collaboration_history_path = os.path.join(
            RUNTIME_STATE, "collaboration_history.json"
        )
        self.config_path = os.path.join(
            RUNTIME_STATE, "cross_engine_deep_config.json"
        )

        # 加载数据
        self.collaboration_metrics = self._load_collaboration_metrics()
        self.optimization_opportunities = self._load_optimization_opportunities()
        self.collaboration_history = self._load_collaboration_history()
        self.config = self._load_config()

        # 内存缓存
        self._metrics_cache = deque(maxlen=1000)
        self._optimization_cache = deque(maxlen=100)
        self._lock = threading.Lock()

    def _load_collaboration_metrics(self) -> Dict[str, EngineCollaborationMetrics]:
        """加载协作指标"""
        if os.path.exists(self.collaboration_metrics_path):
            try:
                with open(self.collaboration_metrics_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return {k: EngineCollaborationMetrics(**v) for k, v in data.items()}
            except Exception:
                pass
        return {}

    def _save_collaboration_metrics(self):
        """保存协作指标"""
        try:
            os.makedirs(RUNTIME_STATE, exist_ok=True)
            with open(self.collaboration_metrics_path, "w", encoding="utf-8") as f:
                data = {k: v.__dict__ for k, v in self.collaboration_metrics.items()}
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存协作指标失败: {e}")

    def _load_optimization_opportunities(self) -> List[OptimizationOpportunity]:
        """加载优化机会"""
        if os.path.exists(self.optimization_opportunities_path):
            try:
                with open(self.optimization_opportunities_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return [OptimizationOpportunity(**item) for item in data]
            except Exception:
                pass
        return []

    def _save_optimization_opportunities(self):
        """保存优化机会"""
        try:
            os.makedirs(RUNTIME_STATE, exist_ok=True)
            with open(self.optimization_opportunities_path, "w", encoding="utf-8") as f:
                data = [opp.__dict__ for opp in self.optimization_opportunities]
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存优化机会失败: {e}")

    def _load_collaboration_history(self) -> List[CollaborationResult]:
        """加载协作历史"""
        if os.path.exists(self.collaboration_history_path):
            try:
                with open(self.collaboration_history_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return [CollaborationResult(**item) for item in data]
            except Exception:
                pass
        return []

    def _save_collaboration_history(self):
        """保存协作历史"""
        try:
            os.makedirs(RUNTIME_STATE, exist_ok=True)
            with open(self.collaboration_history_path, "w", encoding="utf-8") as f:
                data = [result.__dict__ for result in self.collaboration_history[-1000:]]
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存协作历史失败: {e}")

    def _load_config(self) -> Dict:
        """加载配置"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "optimization_enabled": True,
            "auto_apply_optimizations": True,
            "min_confidence_threshold": 0.6,
            "max_concurrent_optimizations": 3,
            "collaboration_analysis_interval": 300,  # 5分钟
            "learning_rate": 0.1,
            "opportunity_retention_days": 7,
            "metrics_retention_count": 1000,
        }

    # ==================== 核心功能 ====================

    def analyze_collaboration_patterns(self) -> Dict[str, Any]:
        """分析跨引擎协作模式"""
        with self._lock:
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "total_collaborations": len(self.collaboration_history),
                "patterns": [],
                "insights": []
            }

            if not self.collaboration_history:
                analysis["insights"].append("暂无协作历史数据")
                return analysis

            # 统计引擎协作频率
            engine_pair_counts = defaultdict(int)
            engine_success_counts = defaultdict(lambda: {"success": 0, "total": 0})

            for result in self.collaboration_history[-200:]:
                if len(result.engines) >= 2:
                    for i in range(len(result.engines)):
                        for j in range(i + 1, len(result.engines)):
                            pair = f"{result.engines[i]}<->{result.engines[j]}"
                            engine_pair_counts[pair] += 1
                            engine_success_counts[pair]["total"] += 1
                            if result.success:
                                engine_success_counts[pair]["success"] += 1

            # 生成模式分析
            for pair, count in sorted(engine_pair_counts.items(), key=lambda x: -x[1])[:10]:
                success_rate = (
                    engine_success_counts[pair]["success"] / engine_success_counts[pair]["total"]
                    if engine_success_counts[pair]["total"] > 0 else 0
                )
                analysis["patterns"].append({
                    "engine_pair": pair,
                    "collaboration_count": count,
                    "success_rate": round(success_rate, 3),
                    "efficiency": "high" if success_rate >= 0.8 else "medium" if success_rate >= 0.5 else "low"
                })

            # 生成洞察
            high_efficiency_pairs = [p for p in analysis["patterns"] if p["efficiency"] == "high"]
            low_efficiency_pairs = [p for p in analysis["patterns"] if p["efficiency"] == "low"]

            if high_efficiency_pairs:
                top_pair = high_efficiency_pairs[0]
                analysis["insights"].append(
                    f"高效协作: {top_pair['engine_pair']} 协作成功率达 {top_pair['success_rate']*100}%"
                )

            if low_efficiency_pairs:
                bottom_pair = low_efficiency_pairs[0]
                analysis["insights"].append(
                    f"优化机会: {bottom_pair['engine_pair']} 协作成功率仅 {bottom_pair['success_rate']*100}%，建议优化"
                )

            return analysis

    def discover_optimization_opportunities(self) -> List[OptimizationOpportunity]:
        """发现优化机会"""
        opportunities = []
        analysis = self.analyze_collaboration_patterns()

        # 基于模式分析发现优化机会
        for pattern in analysis.get("patterns", []):
            if pattern.get("efficiency") == "low" and pattern.get("success_rate", 0) < 0.5:
                opp = OptimizationOpportunity(
                    opportunity_id=f"opp_{int(time.time() * 1000)}",
                    opportunity_type="collaboration_optimization",
                    description=f"优化引擎对 {pattern['engine_pair']} 的协作策略，当前成功率 {pattern['success_rate']*100}%",
                    affected_engines=pattern["engine_pair"].split("<->"),
                    expected_improvement=(0.8 - pattern["success_rate"]) * 100,
                    confidence=0.7,
                    status="identified"
                )
                opportunities.append(opp)

        # 检查历史执行数据发现优化机会
        recent_history = self.collaboration_history[-50:] if self.collaboration_history else []
        if recent_history:
            # 计算平均执行时间
            avg_time = sum(r.execution_time for r in recent_history) / len(recent_history)
            slow_executions = [r for r in recent_history if r.execution_time > avg_time * 1.5]

            if slow_executions:
                # 找出经常一起出现但执行慢的引擎组合
                engine_time_sum = defaultdict(float)
                engine_time_count = defaultdict(int)

                for r in slow_executions:
                    for engine in r.engines:
                        engine_time_sum[engine] += r.execution_time
                        engine_time_count[engine] += 1

                for engine, total_time in engine_time_sum.items():
                    if engine_time_count[engine] >= 2:
                        avg_exec_time = total_time / engine_time_count[engine]
                        opp = OptimizationOpportunity(
                            opportunity_id=f"opp_{int(time.time() * 1000)}_speed",
                            opportunity_type="execution_optimization",
                            description=f"优化引擎 {engine} 的执行效率，平均执行时间 {avg_exec_time:.2f}秒",
                            affected_engines=[engine],
                            expected_improvement=20.0,
                            confidence=0.6,
                            status="identified"
                        )
                        opportunities.append(opp)

        # 添加到缓存并保存
        with self._lock:
            for opp in opportunities:
                if opp.opportunity_id not in [o.opportunity_id for o in self.optimization_opportunities]:
                    self.optimization_opportunities.append(opp)

            self._optimization_cache.extend(opportunities)

        self._save_optimization_opportunities()
        return opportunities

    def apply_optimization(self, opportunity: OptimizationOpportunity) -> bool:
        """应用优化"""
        if opportunity.confidence < self.config["min_confidence_threshold"]:
            return False

        try:
            # 根据优化类型应用不同的优化策略
            if opportunity.opportunity_type == "collaboration_optimization":
                # 协作优化：调整引擎选择权重
                self._apply_collaboration_optimization(opportunity)
            elif opportunity.opportunity_type == "execution_optimization":
                # 执行优化：调整执行参数
                self._apply_execution_optimization(opportunity)

            opportunity.status = "applied"
            self._save_optimization_opportunities()

            return True
        except Exception as e:
            print(f"应用优化失败: {e}")
            return False

    def _apply_collaboration_optimization(self, opportunity: OptimizationOpportunity):
        """应用协作优化"""
        # 更新配置中的引擎权重
        if "engine_selection_weight" in self.config:
            self.config["engine_selection_weight"] = min(
                1.0, self.config["engine_selection_weight"] * (1 + self.config["learning_rate"])
            )

        # 保存配置
        self._save_config()

    def _apply_execution_optimization(self, opportunity: OptimizationOpportunity):
        """应用执行优化"""
        # 增加超时时间或调整并行度
        if "execution_timeout" not in self.config:
            self.config["execution_timeout"] = 300

        self.config["execution_timeout"] = min(
            600, self.config["execution_timeout"] * 1.2
        )

        self._save_config()

    def _save_config(self):
        """保存配置"""
        try:
            os.makedirs(RUNTIME_STATE, exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def verify_optimization_effect(self, opportunity: OptimizationOpportunity) -> Dict[str, Any]:
        """验证优化效果"""
        verification = {
            "opportunity_id": opportunity.opportunity_id,
            "verification_time": datetime.now().isoformat(),
            "improvement_observed": False,
            "improvement_score": 0.0,
            "recommendations": []
        }

        # 查找应用优化后的协作结果
        applied_time = datetime.fromisoformat(opportunity.timestamp.replace("Z", "+00:00"))
        recent_results = [
            r for r in self.collaboration_history
            if datetime.fromisoformat(r.timestamp.replace("Z", "+00:00")) > applied_time
        ]

        if recent_results:
            # 比较优化前后的成功率
            old_results = [
                r for r in self.collaboration_history
                if datetime.fromisoformat(r.timestamp.replace("Z", "+00:00")) <= applied_time
            ][-20:] if self.collaboration_history else []

            if old_results and recent_results:
                old_success_rate = sum(1 for r in old_results if r.success) / len(old_results)
                new_success_rate = sum(1 for r in recent_results if r.success) / len(recent_results)

                improvement = new_success_rate - old_success_rate
                verification["improvement_observed"] = improvement > 0
                verification["improvement_score"] = improvement * 100

                if improvement > 0:
                    verification["recommendations"].append(
                        f"优化有效，成功率提升 {improvement*100:.1f}%"
                    )
                    opportunity.status = "verified"
                else:
                    verification["recommendations"].append(
                        "优化效果不明显，建议调整策略"
                    )
                    opportunity.status = "needs_adjustment"

        self._save_optimization_opportunities()
        return verification

    def record_collaboration(self, engines: List[str], task_type: str,
                            success: bool, execution_time: float,
                            optimization_applied: bool = False,
                            lessons_learned: List[str] = None):
        """记录协作结果"""
        result = CollaborationResult(
            collaboration_id=f"collab_{int(time.time() * 1000)}",
            engines=engines,
            task_type=task_type,
            success=success,
            execution_time=execution_time,
            optimization_applied=optimization_applied,
            improvement_score=0.0,
            lessons_learned=lessons_learned or []
        )

        with self._lock:
            self.collaboration_history.append(result)
            self._metrics_cache.append(result)

        self._save_collaboration_history()
        return result

    def get_collaboration_status(self) -> Dict[str, Any]:
        """获取协作状态"""
        recent = self.collaboration_history[-50:] if self.collaboration_history else []

        status = {
            "timestamp": datetime.now().isoformat(),
            "version": self.version,
            "total_collaborations": len(self.collaboration_history),
            "recent_success_rate": 0.0,
            "optimization_opportunities": len([
                o for o in self.optimization_opportunities
                if o.status in ["identified", "analyzed"]
            ]),
            "optimizations_applied": len([
                o for o in self.optimization_opportunities
                if o.status == "applied"
            ]),
            "config": {
                "optimization_enabled": self.config["optimization_enabled"],
                "auto_apply": self.config["auto_apply_optimizations"]
            }
        }

        if recent:
            status["recent_success_rate"] = sum(1 for r in recent if r.success) / len(recent)

        return status

    def run_full_cycle(self) -> Dict[str, Any]:
        """运行完整的协作优化周期"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "cycle_completed": False,
            "stages": {}
        }

        try:
            # 阶段1: 分析协作模式
            analysis = self.analyze_collaboration_patterns()
            result["stages"]["analysis"] = analysis

            # 阶段2: 发现优化机会
            opportunities = self.discover_optimization_opportunities()
            result["stages"]["opportunity_discovery"] = {
                "opportunities_found": len(opportunities)
            }

            # 阶段3: 应用优化
            applied_count = 0
            if self.config["auto_apply_optimizations"]:
                for opp in opportunities:
                    if opp.status == "identified" and opp.confidence >= self.config["min_confidence_threshold"]:
                        if self.apply_optimization(opp):
                            applied_count += 1

            result["stages"]["optimization_apply"] = {
                "optimizations_applied": applied_count
            }

            # 阶段4: 验证效果
            verified_opportunities = []
            for opp in self.optimization_opportunities:
                if opp.status == "applied":
                    verification = self.verify_optimization_effect(opp)
                    verified_opportunities.append(verification)

            result["stages"]["verification"] = {
                "verifications_done": len(verified_opportunities)
            }

            # 阶段5: 记录状态
            status = self.get_collaboration_status()
            result["stages"]["status"] = status

            result["cycle_completed"] = True

        except Exception as e:
            result["error"] = str(e)

        return result


# 全局单例
_global_instance = None


def get_cross_engine_deep_optimizer() -> CrossEngineDeepCollaborationOptimizer:
    """获取全局单例"""
    global _global_instance
    if _global_instance is None:
        _global_instance = CrossEngineDeepCollaborationOptimizer()
    return _global_instance


# CLI 入口
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="跨引擎深度协同自适应优化增强引擎")
    parser.add_argument("action", choices=["analyze", "discover", "apply", "verify", "status", "full_cycle"],
                       help="执行的操作")
    parser.add_argument("--opportunity-id", help="优化机会ID（用于verify和apply）")
    parser.add_argument("--engines", nargs="+", help="引擎列表（用于record）")
    parser.add_argument("--task-type", help="任务类型")
    parser.add_argument("--success", type=lambda x: x.lower() == "true", help="是否成功")
    parser.add_argument("--execution-time", type=float, help="执行时间")

    args = parser.parse_args()
    optimizer = get_cross_engine_deep_optimizer()

    if args.action == "analyze":
        result = optimizer.analyze_collaboration_patterns()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == "discover":
        opportunities = optimizer.discover_optimization_opportunities()
        print(f"发现 {len(opportunities)} 个优化机会:")
        for opp in opportunities:
            print(f"  - {opp.description}")

    elif args.action == "apply":
        if args.opportunity_id:
            for opp in optimizer.optimization_opportunities:
                if opp.opportunity_id == args.opportunity_id:
                    success = optimizer.apply_optimization(opp)
                    print(f"应用优化 {'成功' if success else '失败'}")
                    break
        else:
            print("请提供 --opportunity-id")

    elif args.action == "verify":
        if args.opportunity_id:
            for opp in optimizer.optimization_opportunities:
                if opp.opportunity_id == args.opportunity_id:
                    result = optimizer.verify_optimization_effect(opp)
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                    break
        else:
            print("请提供 --opportunity-id")

    elif args.action == "status":
        status = optimizer.get_collaboration_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.action == "full_cycle":
        result = optimizer.run_full_cycle()
        print(json.dumps(result, ensure_ascii=False, indent=2))