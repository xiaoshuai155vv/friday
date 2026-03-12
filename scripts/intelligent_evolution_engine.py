#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能进化引擎 - 实现基于历史执行数据的自我分析、自我优化能力
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntelligentEvolutionEngine:
    """智能进化引擎主类"""

    def __init__(self, data_dir: str = "runtime/state"):
        """
        初始化智能进化引擎

        Args:
            data_dir: 存储数据的目录
        """
        self.data_dir = data_dir
        self.execution_history_file = os.path.join(data_dir, "execution_history.json")
        self.evolution_rules_file = os.path.join(data_dir, "evolution_rules.json")
        self.performance_metrics_file = os.path.join(data_dir, "performance_metrics.json")

        # 确保目录存在
        os.makedirs(data_dir, exist_ok=True)

        # 加载现有规则
        self.evolution_rules = self._load_evolution_rules()

        # 初始化性能指标
        self.performance_metrics = self._load_performance_metrics()

    def _load_evolution_rules(self) -> Dict[str, Any]:
        """加载进化规则"""
        if os.path.exists(self.evolution_rules_file):
            try:
                with open(self.evolution_rules_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载进化规则失败: {e}")
                return {}
        return {}

    def _load_performance_metrics(self) -> Dict[str, Any]:
        """加载性能指标"""
        if os.path.exists(self.performance_metrics_file):
            try:
                with open(self.performance_metrics_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载性能指标失败: {e}")
                return {}
        return {}

    def record_execution(self, task_name: str, success: bool, duration: float,
                        metrics: Optional[Dict[str, Any]] = None) -> None:
        """
        记录任务执行历史

        Args:
            task_name: 任务名称
            success: 是否成功
            duration: 执行时长
            metrics: 执行指标
        """
        # 读取现有历史
        execution_history = []
        if os.path.exists(self.execution_history_file):
            try:
                with open(self.execution_history_file, 'r', encoding='utf-8') as f:
                    execution_history = json.load(f)
            except Exception as e:
                logger.warning(f"读取执行历史失败: {e}")

        # 添加新记录
        execution_record = {
            "timestamp": datetime.now().isoformat(),
            "task_name": task_name,
            "success": success,
            "duration": duration,
            "metrics": metrics or {}
        }

        execution_history.append(execution_record)

        # 保存历史
        try:
            with open(self.execution_history_file, 'w', encoding='utf-8') as f:
                json.dump(execution_history, f, ensure_ascii=False, indent=2)
            logger.info(f"记录执行历史: {task_name} - {'成功' if success else '失败'}")
        except Exception as e:
            logger.error(f"保存执行历史失败: {e}")

    def analyze_performance(self) -> Dict[str, Any]:
        """
        分析性能表现

        Returns:
            性能分析结果
        """
        if not os.path.exists(self.execution_history_file):
            return {"error": "没有执行历史数据"}

        try:
            with open(self.execution_history_file, 'r', encoding='utf-8') as f:
                execution_history = json.load(f)

            if not execution_history:
                return {"error": "执行历史为空"}

            # 统计信息
            total_tasks = len(execution_history)
            successful_tasks = sum(1 for record in execution_history if record.get('success'))
            success_rate = successful_tasks / total_tasks if total_tasks > 0 else 0

            # 计算平均执行时间
            durations = [record.get('duration', 0) for record in execution_history]
            avg_duration = sum(durations) / len(durations) if durations else 0

            # 按任务类型统计
            task_stats = defaultdict(lambda: {"total": 0, "success": 0, "avg_duration": 0})
            for record in execution_history:
                task_name = record.get('task_name', 'unknown')
                task_stats[task_name]["total"] += 1
                if record.get('success'):
                    task_stats[task_name]["success"] += 1

            # 计算各任务的成功率和平均耗时
            for task_name, stats in task_stats.items():
                stats["success_rate"] = stats["success"] / stats["total"] if stats["total"] > 0 else 0
                task_durations = [record.get('duration', 0) for record in execution_history
                                if record.get('task_name') == task_name]
                stats["avg_duration"] = sum(task_durations) / len(task_durations) if task_durations else 0

            # 记录性能指标
            self.performance_metrics = {
                "timestamp": datetime.now().isoformat(),
                "total_tasks": total_tasks,
                "successful_tasks": successful_tasks,
                "success_rate": success_rate,
                "average_duration": avg_duration,
                "task_statistics": dict(task_stats)
            }

            # 保存性能指标
            with open(self.performance_metrics_file, 'w', encoding='utf-8') as f:
                json.dump(self.performance_metrics, f, ensure_ascii=False, indent=2)

            return self.performance_metrics

        except Exception as e:
            logger.error(f"分析性能失败: {e}")
            return {"error": f"分析失败: {str(e)}"}

    def suggest_optimizations(self) -> List[Dict[str, Any]]:
        """
        基于历史数据分析优化建议

        Returns:
            优化建议列表
        """
        performance_data = self.analyze_performance()

        if "error" in performance_data:
            return [{"error": performance_data["error"]}]

        suggestions = []

        # 建议1: 识别低成功率任务
        low_success_rate_tasks = []
        for task_name, stats in performance_data.get("task_statistics", {}).items():
            if stats.get("success_rate", 0) < 0.8:  # 成功率低于80%
                low_success_rate_tasks.append({
                    "task": task_name,
                    "success_rate": stats["success_rate"],
                    "suggestion": f"该任务成功率较低({stats['success_rate']:.2%})，建议优化执行策略"
                })

        if low_success_rate_tasks:
            suggestions.extend(low_success_rate_tasks)

        # 建议2: 识别耗时较长任务
        slow_tasks = []
        for task_name, stats in performance_data.get("task_statistics", {}).items():
            if stats.get("avg_duration", 0) > 10:  # 平均耗时超过10秒
                slow_tasks.append({
                    "task": task_name,
                    "avg_duration": stats["avg_duration"],
                    "suggestion": f"该任务平均耗时较长({stats['avg_duration']:.2f}s)，建议优化执行效率"
                })

        if slow_tasks:
            suggestions.extend(slow_tasks)

        # 建议3: 全局成功率优化
        global_success_rate = performance_data.get("success_rate", 0)
        if global_success_rate < 0.9:  # 全局成功率低于90%
            suggestions.append({
                "category": "全局优化",
                "suggestion": f"系统整体成功率较低({global_success_rate:.2%})，建议进行全面优化"
            })

        # 建议4: 识别系统瓶颈
        if performance_data.get("average_duration", 0) > 5:
            suggestions.append({
                "category": "系统瓶颈",
                "suggestion": "系统平均执行时间较长，可能存在性能瓶颈，建议进行系统调优"
            })

        return suggestions

    def evolve(self) -> Dict[str, Any]:
        """
        执行进化过程

        Returns:
            进化结果
        """
        logger.info("开始智能进化分析...")

        # 分析性能
        performance_data = self.analyze_performance()

        # 生成优化建议
        optimizations = self.suggest_optimizations()

        # 生成进化报告
        evolution_report = {
            "timestamp": datetime.now().isoformat(),
            "performance_analysis": performance_data,
            "optimization_suggestions": optimizations,
            "evolution_actions": []
        }

        # 根据建议更新进化规则
        if optimizations:
            for suggestion in optimizations:
                if "error" not in suggestion:
                    # 更新进化规则
                    rule_key = f"optimization_{len(self.evolution_rules)}"
                    self.evolution_rules[rule_key] = {
                        "timestamp": datetime.now().isoformat(),
                        "suggestion": suggestion,
                        "status": "pending"
                    }

                    evolution_report["evolution_actions"].append({
                        "action": "update_rule",
                        "rule_key": rule_key,
                        "details": suggestion
                    })

        # 保存进化规则
        try:
            with open(self.evolution_rules_file, 'w', encoding='utf-8') as f:
                json.dump(self.evolution_rules, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存进化规则失败: {e}")

        logger.info("智能进化分析完成")
        return evolution_report

    def get_evolution_status(self) -> Dict[str, Any]:
        """
        获取进化状态

        Returns:
            进化状态信息
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "rules_count": len(self.evolution_rules),
            "metrics": self.performance_metrics,
            "last_update": self.performance_metrics.get("timestamp", "从未更新")
        }

def main():
    """主函数 - 支持命令行参数"""
    import argparse

    parser = argparse.ArgumentParser(description="智能进化引擎")
    parser.add_argument("command", nargs="?", default="analyze",
                       help="命令: analyze(分析), status(状态), suggest(建议), evolve(进化)")
    parser.add_argument("--task", help="任务名称")
    parser.add_argument("--success", default="true", help="是否成功 (true/false)")
    parser.add_argument("--duration", type=float, default=0, help="执行时长")

    args = parser.parse_args()

    engine = IntelligentEvolutionEngine()

    if args.command == "analyze":
        # 分析性能
        performance = engine.analyze_performance()
        print("=== 性能分析 ===")
        print(json.dumps(performance, ensure_ascii=False, indent=2))

    elif args.command == "status":
        # 查看状态
        status = engine.get_evolution_status()
        print("=== 进化状态 ===")
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.command == "suggest":
        # 获取建议
        suggestions = engine.suggest_optimizations()
        print("=== 优化建议 ===")
        print(json.dumps(suggestions, ensure_ascii=False, indent=2))

    elif args.command == "evolve":
        # 执行进化
        evolution = engine.evolve()
        print("=== 进化报告 ===")
        print(json.dumps(evolution, ensure_ascii=False, indent=2))

    elif args.command == "record":
        # 记录执行
        if args.task:
            engine.record_execution(args.task, args.success, args.duration)
            print(f"已记录执行: {args.task}")
        else:
            print("错误: 需要指定 --task 参数")
            parser.print_help()

    else:
        print(f"未知命令: {args.command}")
        parser.print_help()

if __name__ == "__main__":
    main()