#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能引擎编排优化器

功能：
1. 自动分析各引擎使用效果和协作效率
2. 动态优化引擎协作策略
3. 基于任务类型智能推荐最优引擎组合
4. 实现引擎性能的持续学习和自我优化
5. 集成到 do.py 支持关键词触发

核心能力：
- 引擎使用统计分析：记录各引擎调用次数、成功率、平均响应时间
- 协作模式发现：自动发现高效的引擎协作模式
- 动态编排优化：根据实时性能数据调整引擎调度策略
- 智能推荐：根据当前任务类型推荐最优引擎组合
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
import threading

# 确保 scripts 目录在路径中
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
RUNTIME_DIR = os.path.join(PROJECT_DIR, "runtime")
STATE_DIR = os.path.join(RUNTIME_DIR, "state")
LOGS_DIR = os.path.join(RUNTIME_DIR, "logs")

# 确保目录存在
os.makedirs(STATE_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)


@dataclass
class EngineUsageRecord:
    """引擎使用记录"""
    engine_name: str
    timestamp: str
    duration_ms: float
    success: bool
    task_type: str
    error_message: Optional[str] = None


@dataclass
class CollaborationPattern:
    """协作模式"""
    pattern_id: str
    engines: List[str]
    usage_count: int
    success_rate: float
    avg_duration_ms: float
    last_used: str
    score: float  # 综合评分


@dataclass
class OptimizationSuggestion:
    """优化建议"""
    suggestion_id: str
    category: str  # "schedule", "pattern", "resource", "cache"
    title: str
    description: str
    impact: str  # "high", "medium", "low"
    estimated_improvement: str


class EngineUsageTracker:
    """引擎使用追踪器"""

    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self.usage_history: deque = deque(maxlen=history_size)
        self.engine_stats: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def record_usage(
        self,
        engine_name: str,
        duration_ms: float,
        success: bool,
        task_type: str = "general",
        error_message: Optional[str] = None
    ):
        """记录引擎使用情况"""
        record = EngineUsageRecord(
            engine_name=engine_name,
            timestamp=datetime.now().isoformat(),
            duration_ms=duration_ms,
            success=success,
            task_type=task_type,
            error_message=error_message
        )

        with self._lock:
            self.usage_history.append(record)
            self._update_stats(engine_name)

    def _update_stats(self, engine_name: str):
        """更新引擎统计信息"""
        # 筛选该引擎的所有记录
        engine_records = [r for r in self.usage_history if r.engine_name == engine_name]

        if not engine_records:
            return

        # 计算统计数据
        total = len(engine_records)
        success_count = sum(1 for r in engine_records if r.success)
        avg_duration = sum(r.duration_ms for r in engine_records) / total
        min_duration = min(r.duration_ms for r in engine_records)
        max_duration = max(r.duration_ms for r in engine_records)

        # 按任务类型统计
        task_stats = defaultdict(lambda: {"count": 0, "success": 0, "total_duration": 0.0})
        for r in engine_records:
            task_stats[r.task_type]["count"] += 1
            if r.success:
                task_stats[r.task_type]["success"] += 1
            task_stats[r.task_type]["total_duration"] += r.duration_ms

        # 更新统计数据
        self.engine_stats[engine_name] = {
            "total_usage": total,
            "success_count": success_count,
            "success_rate": success_count / total if total > 0 else 0,
            "avg_duration_ms": avg_duration,
            "min_duration_ms": min_duration,
            "max_duration_ms": max_duration,
            "task_breakdown": {
                task: {
                    "count": stats["count"],
                    "success_rate": stats["success"] / stats["count"] if stats["count"] > 0 else 0,
                    "avg_duration": stats["total_duration"] / stats["count"] if stats["count"] > 0 else 0
                }
                for task, stats in task_stats.items()
            },
            "last_updated": datetime.now().isoformat()
        }

    def get_engine_stats(self, engine_name: Optional[str] = None) -> Dict[str, Any]:
        """获取引擎统计信息"""
        with self._lock:
            if engine_name:
                return self.engine_stats.get(engine_name, {})
            return dict(self.engine_stats)

    def get_top_engines(self, limit: int = 10, sort_by: str = "total_usage") -> List[Dict[str, Any]]:
        """获取最常用的引擎"""
        with self._lock:
            if not self.engine_stats:
                return []

            sorted_engines = sorted(
                self.engine_stats.items(),
                key=lambda x: x[1].get(sort_by, 0),
                reverse=True
            )

            return [
                {"engine_name": name, **stats}
                for name, stats in sorted_engines[:limit]
            ]


class CollaborationPatternMiner:
    """协作模式挖掘器"""

    def __init__(self):
        self.patterns: Dict[str, CollaborationPattern] = {}
        self.recent_collaborations: deque = deque(maxlen=100)

    def analyze_collaboration(
        self,
        engine_sequence: List[str],
        duration_ms: float,
        success: bool,
        task_type: str = "general"
    ):
        """分析引擎协作"""
        if len(engine_sequence) < 2:
            return

        # 创建模式标识（排序以忽略顺序差异）
        pattern_key = "+".join(sorted(engine_sequence))

        if pattern_key in self.patterns:
            pattern = self.patterns[pattern_key]
            pattern.usage_count += 1

            # 更新成功率
            if success:
                pattern.success_rate = (
                    pattern.success_rate * (pattern.usage_count - 1) + 1.0
                ) / pattern.usage_count
            else:
                pattern.success_rate = (
                    pattern.success_rate * (pattern.usage_count - 1)
                ) / pattern.usage_count

            # 更新平均响应时间
            pattern.avg_duration_ms = (
                pattern.avg_duration_ms * (pattern.usage_count - 1) + duration_ms
            ) / pattern.usage_count

            pattern.last_used = datetime.now().isoformat()
        else:
            # 创建新模式
            pattern = CollaborationPattern(
                pattern_id=pattern_key,
                engines=engine_sequence,
                usage_count=1,
                success_rate=1.0 if success else 0.0,
                avg_duration_ms=duration_ms,
                last_used=datetime.now().isoformat(),
                score=0.0
            )

            self.patterns[pattern_key] = pattern

        # 计算模式评分
        self._calculate_pattern_score(pattern)

        # 记录协作历史
        self.recent_collaborations.append({
            "pattern": pattern_key,
            "engines": engine_sequence,
            "duration_ms": duration_ms,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "task_type": task_type
        })

    def _calculate_pattern_score(self, pattern: CollaborationPattern):
        """计算模式评分"""
        # 综合考虑成功率、响应时间和使用频率
        success_weight = 0.5
        speed_weight = 0.3
        usage_weight = 0.2

        # 成功率评分 (0-1)
        success_score = pattern.success_rate

        # 速度评分 (0-1，越快越高)
        # 假设 1000ms 为最慢可接受时间
        speed_score = max(0, 1 - pattern.avg_duration_ms / 1000)

        # 使用频率评分 (0-1)
        usage_score = min(1.0, pattern.usage_count / 10)

        # 计算综合评分
        pattern.score = (
            success_score * success_weight +
            speed_weight * speed_score +
            usage_weight * usage_score
        )

    def get_top_patterns(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最佳协作模式"""
        sorted_patterns = sorted(
            self.patterns.values(),
            key=lambda p: p.score,
            reverse=True
        )

        return [asdict(p) for p in sorted_patterns[:limit]]

    def suggest_optimization(self) -> List[OptimizationSuggestion]:
        """生成优化建议"""
        suggestions = []

        # 分析低效模式
        low_efficiency_patterns = [
            p for p in self.patterns.values()
            if p.score < 0.5 and p.usage_count >= 3
        ]

        for pattern in low_efficiency_patterns:
            suggestions.append(OptimizationSuggestion(
                suggestion_id=f"opt_{pattern.pattern_id}_{int(time.time())}",
                category="pattern",
                title=f"优化引擎组合: {pattern.pattern_id}",
                description=f"该引擎组合成功率为 {pattern.success_rate*100:.1f}%，平均耗时 {pattern.avg_duration_ms:.0f}ms，建议重新评估是否必要",
                impact="high" if pattern.usage_count > 5 else "medium",
                estimated_improvement="预计可提升 20-40% 效率"
            ))

        # 分析慢引擎
        for pattern in self.patterns.values():
            if pattern.avg_duration_ms > 2000:  # 超过2秒
                suggestions.append(OptimizationSuggestion(
                    suggestion_id=f"perf_{pattern.pattern_id}_{int(time.time())}",
                    category="performance",
                    title=f"优化 {pattern.pattern_id} 响应速度",
                    description=f"该引擎组合平均响应时间为 {pattern.avg_duration_ms:.0f}ms，建议优化或异步处理",
                    impact="medium",
                    estimated_improvement="预计可减少 30-50% 等待时间"
                ))

        return suggestions


class DynamicOrchestrator:
    """动态编排器"""

    def __init__(self):
        self.schedule_weights: Dict[str, float] = {}
        self.task_engine_mapping: Dict[str, List[str]] = defaultdict(list)
        self._load_config()

    def _load_config(self):
        """加载配置"""
        config_file = os.path.join(STATE_DIR, "orchestration_config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.schedule_weights = config.get("weights", {})
                    self.task_engine_mapping = defaultdict(list, config.get("task_mapping", {}))
            except Exception:
                pass

    def _save_config(self):
        """保存配置"""
        config_file = os.path.join(STATE_DIR, "orchestration_config.json")
        config = {
            "weights": self.schedule_weights,
            "task_mapping": dict(self.task_engine_mapping),
            "updated_at": datetime.now().isoformat()
        }
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def optimize_schedule(
        self,
        engine_stats: Dict[str, Dict[str, Any]],
        patterns: List[CollaborationPattern]
    ):
        """优化调度策略"""
        # 基于性能数据调整权重
        for engine_name, stats in engine_stats.items():
            success_rate = stats.get("success_rate", 1.0)
            avg_duration = stats.get("avg_duration_ms", 1000)

            # 成功率高且响应快的引擎获得更高权重
            success_score = success_rate
            speed_score = max(0, 1 - avg_duration / 2000)

            self.schedule_weights[engine_name] = (success_score * 0.6 + speed_score * 0.4)

        # 基于最佳模式优化任务映射
        for pattern in patterns[:5]:  # 取前5个最佳模式
            # 简化模式，只取前两个引擎
            if len(pattern.engines) >= 2:
                task_type = "optimized_" + pattern.engines[0]
                self.task_engine_mapping[task_type] = pattern.engines

        self._save_config()

    def get_optimal_sequence(self, task_type: str, available_engines: List[str]) -> List[str]:
        """获取最优引擎序列"""
        # 优先使用已知的最优序列
        if task_type in self.task_engine_mapping:
            return self.task_engine_mapping[task_type]

        # 否则按权重排序
        sorted_engines = sorted(
            available_engines,
            key=lambda e: self.schedule_weights.get(e, 0.5),
            reverse=True
        )

        return sorted_engines


class EngineOrchestrationOptimizer:
    """智能引擎编排优化器 - 主类"""

    def __init__(self):
        self.usage_tracker = EngineUsageTracker()
        self.pattern_miner = CollaborationPatternMiner()
        self.orchestrator = DynamicOrchestrator()
        self.optimization_enabled = True
        self._lock = threading.Lock()

    def record_engine_call(
        self,
        engine_name: str,
        duration_ms: float,
        success: bool,
        task_type: str = "general",
        error_message: Optional[str] = None
    ):
        """记录引擎调用"""
        self.usage_tracker.record_usage(
            engine_name, duration_ms, success, task_type, error_message
        )

    def record_collaboration(
        self,
        engine_sequence: List[str],
        duration_ms: float,
        success: bool,
        task_type: str = "general"
    ):
        """记录引擎协作"""
        self.pattern_miner.analyze_collaboration(
            engine_sequence, duration_ms, success, task_type
        )

    def run_optimization(self) -> Dict[str, Any]:
        """运行优化分析"""
        with self._lock:
            # 获取统计信息
            engine_stats = self.usage_tracker.get_engine_stats()
            top_engines = self.usage_tracker.get_top_engines(limit=10)
            top_patterns = self.pattern_miner.get_top_patterns(limit=10)
            suggestions = self.pattern_miner.suggest_optimization()

            # 执行优化
            if self.optimization_enabled and engine_stats:
                patterns = [p for p in self.pattern_miner.patterns.values()]
                self.orchestrator.optimize_schedule(engine_stats, patterns)

            # 生成报告
            report = {
                "timestamp": datetime.now().isoformat(),
                "optimization_summary": {
                    "total_engines_tracked": len(engine_stats),
                    "total_patterns_discovered": len(self.pattern_miner.patterns),
                    "suggestions_count": len(suggestions)
                },
                "top_engines": top_engines,
                "top_patterns": top_patterns,
                "suggestions": [asdict(s) for s in suggestions],
                "schedule_weights": self.orchestrator.schedule_weights,
                "task_mappings": dict(self.orchestrator.task_engine_mapping)
            }

            # 保存报告
            report_file = os.path.join(STATE_DIR, "engine_optimization_report.json")
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

            return report

    def get_recommendation(self, task_type: str, available_engines: List[str]) -> Dict[str, Any]:
        """获取任务推荐"""
        optimal_sequence = self.orchestrator.get_optimal_sequence(task_type, available_engines)

        # 获取相关的最佳模式
        related_patterns = [
            asdict(p) for p in self.pattern_miner.patterns.values()
            if any(e in p.engines for e in available_engines[:3])
        ][:3]

        return {
            "recommended_sequence": optimal_sequence,
            "confidence": 0.8 if optimal_sequence else 0.3,
            "related_patterns": related_patterns,
            "reasoning": "基于历史性能数据和协作模式分析" if optimal_sequence else "无足够历史数据，使用默认权重"
        }

    def simulate_engine_call(
        self,
        engine_name: str,
        task_type: str = "general"
    ) -> Tuple[bool, float]:
        """模拟引擎调用（用于测试）"""
        start_time = time.time()

        # 模拟引擎执行
        # 在实际使用中，这里会调用真实的引擎
        time.sleep(0.01)  # 模拟短暂执行

        duration_ms = (time.time() - start_time) * 1000

        # 随机决定成功/失败（90%成功率）
        import random
        success = random.random() < 0.9

        # 记录使用
        self.record_engine_call(engine_name, duration_ms, success, task_type)

        return success, duration_ms


# 全局引擎实例
_optimizer: Optional[EngineOrchestrationOptimizer] = None


def get_optimizer() -> EngineOrchestrationOptimizer:
    """获取优化器实例"""
    global _optimizer
    if _optimizer is None:
        _optimizer = EngineOrchestrationOptimizer()
    return _optimizer


def run_optimization_analysis() -> Dict[str, Any]:
    """运行优化分析"""
    print("=" * 60)
    print("智能引擎编排优化器")
    print("=" * 60)

    # 模拟一些引擎调用以生成数据
    optimizer = get_optimizer()

    print("\n[1/3] 模拟引擎调用数据...")
    test_engines = [
        "decision_orchestrator", "predictive_prevention", "context_awareness",
        "adaptive_learning", "workflow_engine", "emotion_engine",
        "scenario_recommender", "proactive_notification", "self_healing"
    ]
    test_tasks = ["general", "file_operation", "communication", "analysis", "automation"]

    import random
    for _ in range(50):  # 模拟50次调用
        engine = random.choice(test_engines)
        task = random.choice(test_tasks)
        optimizer.simulate_engine_call(engine, task)

    print(f"    模拟完成，生成了 {len(optimizer.usage_tracker.usage_history)} 条记录")

    # 模拟协作调用
    print("\n[2/3] 分析引擎协作模式...")
    collaboration_sequences = [
        ["context_awareness", "scenario_recommender", "proactive_notification"],
        ["predictive_prevention", "decision_orchestrator", "self_healing"],
        ["adaptive_learning", "emotion_engine", "conversation_manager"],
        ["workflow_engine", "decision_orchestrator"],
    ]

    for sequence in collaboration_sequences:
        duration = random.uniform(100, 500)
        success = random.random() < 0.85
        optimizer.record_collaboration(sequence, duration, success, "general")

    print(f"    发现 {len(optimizer.pattern_miner.patterns)} 个协作模式")

    # 运行优化分析
    print("\n[3/3] 运行优化分析...")
    result = optimizer.run_optimization()

    # 打印摘要
    print("\n" + "=" * 60)
    print("优化分析摘要")
    print("=" * 60)

    print(f"\n[统计概览]")
    print(f"  - 追踪的引擎数量: {result['optimization_summary']['total_engines_tracked']}")
    print(f"  - 发现的协作模式: {result['optimization_summary']['total_patterns_discovered']}")
    print(f"  - 优化建议数量: {result['optimization_summary']['suggestions_count']}")

    if result.get('top_engines'):
        print(f"\n[最常用引擎 TOP 5]")
        for i, engine in enumerate(result['top_engines'][:5], 1):
            print(f"  {i}. {engine['engine_name']}: {engine['total_usage']} 次调用, 成功率 {engine['success_rate']*100:.1f}%")

    if result.get('top_patterns'):
        print(f"\n[最佳协作模式 TOP 3]")
        for i, pattern in enumerate(result['top_patterns'][:3], 1):
            print(f"  {i}. {' + '.join(pattern['engines'])}: 评分 {pattern['score']:.2f}, 使用 {pattern['usage_count']} 次")

    if result.get('suggestions'):
        print(f"\n[优化建议]")
        for suggestion in result['suggestions'][:3]:
            print(f"  - [{suggestion['impact'].upper()}] {suggestion['title']}")
            print(f"    {suggestion['description']}")

    print(f"\n结果已保存到: {os.path.join(STATE_DIR, 'engine_optimization_report.json')}")

    return result


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="智能引擎编排优化器")
    parser.add_argument("--analyze", action="store_true", help="运行优化分析")
    parser.add_argument("--recommend", type=str, help="获取任务推荐 (指定任务类型)")
    parser.add_argument("--engines", type=str, help="可用引擎列表 (逗号分隔)")
    parser.add_argument("--simulate", action="store_true", help="模拟引擎调用")
    parser.add_argument("--format", choices=["json", "text"], default="text", help="输出格式")

    args = parser.parse_args()

    # 如果没有指定参数，默认运行分析
    if not any([args.analyze, args.recommend, args.simulate]):
        args.analyze = True

    optimizer = get_optimizer()

    if args.analyze:
        result = run_optimization_analysis()
        if args.format == "json":
            print("\n" + "=" * 60)
            print("JSON 输出:")
            print("=" * 60)
            print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.recommend:
        available_engines = args.engines.split(",") if args.engines else []
        recommendation = optimizer.get_recommendation(args.recommend, available_engines)

        if args.format == "json":
            print(json.dumps(recommendation, ensure_ascii=False, indent=2))
        else:
            print(f"\n任务类型: {args.recommend}")
            print(f"推荐引擎序列: {' -> '.join(recommendation['recommended_sequence'])}")
            print(f"置信度: {recommendation['confidence']*100:.0f}%")
            print(f"推理: {recommendation['reasoning']}")

    elif args.simulate:
        print("模拟引擎调用...")
        test_engines = ["decision_orchestrator", "context_awareness", "workflow_engine"]

        for engine in test_engines:
            success, duration = optimizer.simulate_engine_call(engine, "test")
            status = "[OK]" if success else "[FAIL]"
            print(f"  {engine}: {status} ({duration:.1f}ms)")

        print("\n运行优化分析...")
        result = optimizer.run_optimization()
        print(f"优化建议数量: {len(result['suggestions'])}")


if __name__ == "__main__":
    main()