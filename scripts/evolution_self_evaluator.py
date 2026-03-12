#!/usr/bin/env python3
"""
进化环自我评估模块
用于评估进化环本身的性能、效率和健康状况

功能：
1. 分析进化效率、成功率、资源消耗等指标
2. 生成评估报告并提出优化建议
3. 集成到 do.py 支持「进化评估」「自我评估」等关键词触发

使用方法：
    python evolution_self_evaluator.py evaluate
    python evolution_self_evaluator.py report
    python evolution_self_evaluator.py health
"""

import json
import os
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE = PROJECT_ROOT / "runtime" / "state"
RUNTIME_LOGS = PROJECT_ROOT / "runtime" / "logs"
REFERENCES = PROJECT_ROOT / "references"


class EvolutionSelfEvaluator:
    """进化环自我评估器"""

    def __init__(self):
        self.state_dir = RUNTIME_STATE
        self.logs_dir = RUNTIME_LOGS
        self.references_dir = REFERENCES

        # 确保目录存在
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # 评估结果输出路径
        self.evaluation_file = self.state_dir / "evolution_self_evaluation.json"
        self.evaluation_history_file = self.state_dir / "evolution_evaluation_history.json"

    def evaluate(self) -> Dict[str, Any]:
        """执行全面评估"""
        evaluation = {
            "timestamp": datetime.now().isoformat(),
            "efficiency_metrics": self._evaluate_efficiency(),
            "success_metrics": self._evaluate_success_rate(),
            "stability_metrics": self._evaluate_stability(),
            "health_score": 0,
            "recommendations": []
        }

        # 计算综合健康分数
        evaluation["health_score"] = self._calculate_health_score(evaluation)

        # 生成优化建议
        evaluation["recommendations"] = self._generate_recommendations(evaluation)

        # 添加总体评价
        evaluation["overall_grade"] = self._get_grade(evaluation["health_score"])

        return evaluation

    def _evaluate_efficiency(self) -> Dict[str, Any]:
        """评估进化效率"""
        efficiency = {
            "avg_rounds_per_day": 0,
            "rounds_completed_this_week": 0,
            "avg_execution_time_per_round": 0,
            "idle_time_ratio": 0,
            "evolution_velocity": 0
        }

        # 统计进化轮次
        evolution_last = self.references_dir / "evolution_auto_last.md"
        rounds_count = 0

        if evolution_last.exists():
            content = evolution_last.read_text(encoding="utf-8")
            # 统计 round 数量
            rounds = re.findall(r'round (\d+)', content)
            rounds_count = len(rounds)

        # 统计本周完成的轮次
        now = datetime.now()
        week_ago = now - timedelta(days=7)

        week_rounds = 0
        if self.state_dir.exists():
            for f in self.state_dir.glob("evolution_completed_*.json"):
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        if "created_at" in data:
                            created = datetime.fromisoformat(data["created_at"].replace('Z', '+00:00'))
                            if created.replace(tzinfo=None) >= week_ago:
                                week_rounds += 1
                except:
                    pass

        efficiency["rounds_completed_this_week"] = week_rounds
        efficiency["evolution_velocity"] = "fast" if week_rounds >= 3 else "normal" if week_rounds >= 1 else "slow"

        # 分析行为日志获取效率数据
        if self.logs_dir.exists():
            log_files = sorted(self.logs_dir.glob("behavior_*.log"))
            if log_files:
                recent_file = log_files[-1]
                content = recent_file.read_text(encoding="utf-8", errors='ignore')
                lines = content.split('\n')

                # 统计各阶段耗时
                phases = {"假设": [], "规划": [], "执行": [], "校验": [], "反思": []}
                current_phase = None

                for line in lines[-100:]:  # 最近100行
                    if '\t' not in line:
                        continue
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        action = parts[1]
                        if action in phases:
                            current_phase = action

                efficiency["recent_activities"] = len([l for l in lines if l.strip()])

        return efficiency

    def _evaluate_success_rate(self) -> Dict[str, Any]:
        """评估成功率"""
        success = {
            "total_rounds": 0,
            "completed_rounds": 0,
            "failed_rounds": 0,
            "success_rate": 0,
            "completion_rate": 0,
            "stale_count": 0
        }

        # 统计完成/失败/过期的轮次
        if self.state_dir.exists():
            completed = list(self.state_dir.glob("evolution_completed_*.json"))
            success["total_rounds"] = len(completed)

            completed_count = 0
            failed_count = 0
            stale_count = 0

            for f in completed:
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        status = data.get("status", "")
                        if status == "completed":
                            completed_count += 1
                        elif status == "stale_failed":
                            stale_count += 1
                        elif status == "failed":
                            failed_count += 1
                except:
                    pass

            success["completed_rounds"] = completed_count
            success["failed_rounds"] = failed_count + stale_count

            if success["total_rounds"] > 0:
                success["completion_rate"] = completed_count / success["total_rounds"] * 100

        return success

    def _evaluate_stability(self) -> Dict[str, Any]:
        """评估稳定性"""
        stability = {
            "failure_recovery_time": 0,
            "consecutive_failures": 0,
            "stability_score": 100,
            "risk_factors": []
        }

        # 分析失败教训
        failures_file = self.references_dir / "failures.md"
        if failures_file.exists():
            content = failures_file.read_text(encoding="utf-8")
            failure_count = content.count("- 2026-")

            # 计算稳定性分数
            if failure_count > 20:
                stability["stability_score"] = 50
                stability["risk_factors"].append("历史失败较多")
            elif failure_count > 10:
                stability["stability_score"] = 75
            elif failure_count > 5:
                stability["stability_score"] = 85
            else:
                stability["stability_score"] = 95

            # 检查最近是否有连续失败
            if self.state_dir.exists():
                recent_completed = sorted(self.state_dir.glob("evolution_completed_*.json"))[-5:]
                consecutive_failures = 0

                for f in recent_completed:
                    try:
                        with open(f, 'r', encoding='utf-8') as fp:
                            data = json.load(fp)
                            if data.get("status") == "completed":
                                break
                            consecutive_failures += 1
                    except:
                        pass

                stability["consecutive_failures"] = consecutive_failures

        return stability

    def _calculate_health_score(self, evaluation: Dict[str, Any]) -> float:
        """计算综合健康分数"""
        score = 100.0

        # 效率扣分
        efficiency = evaluation.get("efficiency_metrics", {})
        velocity = efficiency.get("evolution_velocity", "normal")
        if velocity == "slow":
            score -= 20
        elif velocity == "normal":
            score -= 10

        # 成功率扣分
        success = evaluation.get("success_metrics", {})
        completion_rate = success.get("completion_rate", 100)
        if completion_rate < 50:
            score -= 30
        elif completion_rate < 80:
            score -= 15

        # 稳定性扣分
        stability = evaluation.get("stability_metrics", {})
        stability_score = stability.get("stability_score", 100)
        score = min(score, stability_score)

        return max(0, score)

    def _generate_recommendations(self, evaluation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成优化建议"""
        recommendations = []

        # 基于效率的建议
        efficiency = evaluation.get("efficiency_metrics", {})
        if efficiency.get("evolution_velocity") == "slow":
            recommendations.append({
                "category": "efficiency",
                "priority": "high",
                "issue": "进化速度较慢",
                "suggestion": "考虑增加自动化执行频率，或优化进化流程减少等待时间"
            })

        # 基于成功的建议
        success = evaluation.get("success_metrics", {})
        if success.get("completion_rate", 100) < 80:
            recommendations.append({
                "category": "success",
                "priority": "high",
                "issue": "进化完成率较低",
                "suggestion": "分析未完成轮次的原因，优化执行策略或降低任务复杂度"
            })

        # 基于稳定的建议
        stability = evaluation.get("stability_metrics", {})
        risk_factors = stability.get("risk_factors", [])
        if risk_factors:
            recommendations.append({
                "category": "stability",
                "priority": "medium",
                "issue": f"存在稳定性风险: {', '.join(risk_factors)}",
                "suggestion": "加强错误处理和恢复机制，减少失败"
            })

        # 总体建议
        if evaluation.get("health_score", 0) >= 80:
            recommendations.append({
                "category": "general",
                "priority": "low",
                "issue": "系统状态良好",
                "suggestion": "可考虑增加探索性进化，尝试新方向"
            })

        return recommendations

    def _get_grade(self, score: float) -> str:
        """根据分数获取等级"""
        if score >= 90:
            return "A (优秀)"
        elif score >= 80:
            return "B (良好)"
        elif score >= 70:
            return "C (中等)"
        elif score >= 60:
            return "D (及格)"
        else:
            return "F (需改进)"

    def save_evaluation(self, evaluation: Dict[str, Any]) -> None:
        """保存评估结果"""
        with open(self.evaluation_file, "w", encoding="utf-8") as f:
            json.dump(evaluation, f, ensure_ascii=False, indent=2)

        # 同时保存到历史
        self._append_to_history(evaluation)

    def _append_to_history(self, evaluation: Dict[str, Any]) -> None:
        """追加到评估历史"""
        history = []

        if self.evaluation_history_file.exists():
            with open(self.evaluation_history_file, "r", encoding="utf-8") as f:
                history = json.load(f)

        # 添加当前评估
        history.append({
            "timestamp": evaluation.get("timestamp"),
            "health_score": evaluation.get("health_score"),
            "overall_grade": evaluation.get("overall_grade")
        })

        # 保留最近20条
        history = history[-20:]

        with open(self.evaluation_history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def get_evaluation(self) -> Dict[str, Any]:
        """获取当前评估结果"""
        if self.evaluation_file.exists():
            with open(self.evaluation_file, "r", encoding="utf-8") as f:
                return json.load(f)

        return {
            "status": "no_evaluation",
            "message": "请先运行 evaluate 命令生成评估报告"
        }

    def health(self) -> Dict[str, Any]:
        """快速健康检查"""
        evaluation = self.evaluate()
        return {
            "status": "healthy" if evaluation["health_score"] >= 70 else "needs_attention",
            "health_score": evaluation["health_score"],
            "overall_grade": evaluation["overall_grade"],
            "main_issues": [r["issue"] for r in evaluation["recommendations"] if r["priority"] == "high"]
        }

    def report(self) -> Dict[str, Any]:
        """获取完整报告"""
        return self.evaluate()


def main():
    """主函数"""
    evaluator = EvolutionSelfEvaluator()

    if len(sys.argv) < 2:
        print("进化环自我评估器")
        print("用法:")
        print("  python evolution_self_evaluator.py evaluate  - 执行全面评估")
        print("  python evolution_self_evaluator.py report    - 获取完整报告")
        print("  python evolution_self_evaluator.py health    - 快速健康检查")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "evaluate":
        result = evaluator.evaluate()
        evaluator.save_evaluation(result)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "report":
        result = evaluator.report()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "health":
        result = evaluator.health()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()