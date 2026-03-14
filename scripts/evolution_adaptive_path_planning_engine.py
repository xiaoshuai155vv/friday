#!/usr/bin/env python3
"""
智能全场景进化环自适应进化路径规划与预测引擎（Evolution Adaptive Path Planning Engine）
version 1.0.0

让系统能够基于当前系统状态、进化历史、能力缺口自动生成最优进化路径，
预测各路径的成功率和预期价值，增强进化环的前瞻性和战略规划能力。

功能：
1. 系统状态分析（健康度、能力缺口、进化历史）
2. 多路径生成（生成多个候选进化路径）
3. 路径成功率预测（基于历史数据预测各路径成功率）
4. 预期价值评估（评估各路径的预期价值）
5. 最优路径选择（综合成功率和价值选择最优路径）
6. 与 do.py 深度集成

依赖：
- evolution_direction_discovery.py (round 239)
- evolution_value_quantization_engine.py (round 438)
- evolution_trend_prediction_prevention_engine.py (round 389)
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class EvolutionAdaptivePathPlanning:
    """自适应进化路径规划与预测引擎"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.runtime_dir = self.project_root / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.references_dir = self.project_root / "references"
        self.scripts_dir = self.project_root / "scripts"

    def analyze_system_state(self) -> Dict[str, Any]:
        """
        分析当前系统状态
        返回：系统状态分析结果
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "health_score": 0.0,
            "capability_coverage": 0.0,
            "active_engines": 0,
            "recent_evolution_count": 0,
            "success_rate": 0.0,
            "status": "analyzing"
        }

        try:
            # 1. 统计进化引擎数量
            if self.scripts_dir.exists():
                engine_count = len(list(self.scripts_dir.glob("evolution_*.py")))
                result["active_engines"] = engine_count

            # 2. 分析进化历史
            history = self._load_evolution_history()
            result["recent_evolution_count"] = len(history)

            if history:
                # 计算成功率
                completed = [h for h in history if h.get("status") == "completed"]
                result["success_rate"] = len(completed) / len(history) if history else 0.0

                # 计算平均健康分数
                health_scores = [h.get("baseline_verification_passed", False) for h in history]
                result["health_score"] = sum(health_scores) / len(health_scores) if health_scores else 0.5

            # 3. 分析能力覆盖
            caps = self._load_capabilities()
            gaps = self._load_capability_gaps()
            covered = sum(1 for g in gaps if g.get("status") == "已覆盖")
            result["capability_coverage"] = covered / len(gaps) if gaps else 1.0

            result["status"] = "completed"

        except Exception as e:
            result["error"] = str(e)
            result["status"] = "error"

        return result

    def _load_evolution_history(self) -> List[Dict]:
        """加载进化历史"""
        history = []
        if self.state_dir.exists():
            for f in self.state_dir.glob("evolution_completed_*.json"):
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        history.append(data)
                except:
                    pass
        history.sort(key=lambda x: x.get('loop_round', 0), reverse=True)
        return history[:50]

    def _load_capabilities(self) -> Dict:
        """加载已有能力"""
        caps_file = self.references_dir / "capabilities.md"
        if caps_file.exists():
            try:
                content = caps_file.read_text(encoding='utf-8')
                return {"loaded": True, "content_length": len(content)}
            except:
                pass
        return {}

    def _load_capability_gaps(self) -> List[Dict]:
        """加载能力缺口"""
        gaps_file = self.references_dir / "capability_gaps.md"
        gaps = []
        if gaps_file.exists():
            content = gaps_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            for line in lines:
                if '|' in line and '---' not in line and '类别' not in line:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 3:
                        status = parts[2].strip() if len(parts) > 2 else ""
                        gaps.append({
                            "category": parts[1] if len(parts) > 1 else "",
                            "status": status if status else "未覆盖"
                        })
        return gaps

    def generate_candidate_paths(self, num_paths: int = 5) -> List[Dict[str, Any]]:
        """
        生成候选进化路径
        参数：num_paths - 生成路径数量
        返回：候选路径列表
        """
        paths = []
        history = self._load_evolution_history()

        # 基于历史进化方向生成路径
        directions = [
            {
                "id": "path_1",
                "name": "跨引擎深度协同优化",
                "description": "增强多个进化引擎之间的协同工作能力，提升整体系统效率",
                "based_on": "round 402, 421 的跨引擎协同",
                "complexity": 7,
                "expected_value": 8.5
            },
            {
                "id": "path_2",
                "name": "元进化策略自动优化",
                "description": "让系统自动优化进化策略，提升进化决策的质量和效率",
                "based_on": "round 312, 387 的元进化能力",
                "complexity": 8,
                "expected_value": 9.0
            },
            {
                "id": "path_3",
                "name": "全场景智能预测增强",
                "description": "增强系统的预测能力，提前识别风险和机会",
                "based_on": "round 389 的趋势预测",
                "complexity": 6,
                "expected_value": 7.5
            },
            {
                "id": "path_4",
                "name": "自主意识决策闭环",
                "description": "增强自主意识驱动的决策和执行能力",
                "based_on": "round 321, 368 的自主意识",
                "complexity": 9,
                "expected_value": 9.5
            },
            {
                "id": "path_5",
                "name": "知识图谱深度推理",
                "description": "增强知识图谱的推理能力，发现更多隐藏关联",
                "based_on": "round 330, 298 的知识图谱",
                "complexity": 7,
                "expected_value": 8.0
            }
        ]

        # 根据历史成功模式调整预期价值
        for path in directions[:num_paths]:
            # 基于历史分析调整预测
            path["predicted_success_rate"] = self._predict_success_rate(path, history)
            path["risk_level"] = self._calculate_risk_level(path, history)
            paths.append(path)

        return paths

    def _predict_success_rate(self, path: Dict, history: List[Dict]) -> float:
        """
        基于历史数据预测路径成功率
        """
        if not history:
            return 0.7  # 默认成功率

        # 分析相关历史轮次的成功率
        related_keywords = path.get("based_on", "").lower()
        related_rounds = [h for h in history if any(kw in str(h.get("current_goal", "")).lower() for kw in related_keywords.split())]

        if related_rounds:
            success_count = sum(1 for h in related_rounds if h.get("status") == "completed")
            return success_count / len(related_rounds)

        # 基于复杂度估算（复杂度越高，成功率越低）
        complexity = path.get("complexity", 5)
        return max(0.5, 0.95 - (complexity - 5) * 0.1)

    def _calculate_risk_level(self, path: Dict, history: List[Dict]) -> str:
        """计算风险等级"""
        success_rate = path.get("predicted_success_rate", 0.7)
        complexity = path.get("complexity", 5)

        if success_rate >= 0.8 and complexity <= 7:
            return "low"
        elif success_rate >= 0.6:
            return "medium"
        else:
            return "high"

    def evaluate_path_value(self, path: Dict) -> Dict[str, Any]:
        """
        评估路径的预期价值
        """
        return {
            "path_id": path.get("id"),
            "path_name": path.get("name"),
            "expected_value": path.get("expected_value", 7.0),
            "success_rate": path.get("predicted_success_rate", 0.7),
            "risk_level": path.get("risk_level", "medium"),
            "complexity": path.get("complexity", 5),
            "value_score": self._calculate_value_score(path),
            "recommendation": self._generate_recommendation(path)
        }

    def _calculate_value_score(self, path: Dict) -> float:
        """计算综合价值分数"""
        expected_value = path.get("expected_value", 7.0)
        success_rate = path.get("predicted_success_rate", 0.7)
        complexity = path.get("complexity", 5)

        # 价值分数 = 预期价值 * 成功率 * 复杂度因子
        complexity_factor = 1.0 - (complexity - 5) * 0.05
        score = expected_value * success_rate * max(0.5, complexity_factor)
        return round(score, 2)

    def _generate_recommendation(self, path: Dict) -> str:
        """生成推荐建议"""
        value_score = path.get("value_score", 5.0)
        risk_level = path.get("risk_level", "medium")

        if value_score >= 7.0 and risk_level == "low":
            return "强烈推荐 - 高价值低风险"
        elif value_score >= 5.0 and risk_level in ["low", "medium"]:
            return "推荐 - 价值较高"
        elif value_score >= 4.0:
            return "可考虑 - 需要监控风险"
        else:
            return "暂不推荐 - 风险较高"

    def select_optimal_path(self, paths: List[Dict]) -> Dict[str, Any]:
        """
        选择最优路径
        """
        if not paths:
            return {"error": "没有可用的候选路径"}

        # 按价值分数排序
        evaluated = [self.evaluate_path_value(p) for p in paths]
        evaluated.sort(key=lambda x: x.get("value_score", 0), reverse=True)

        return {
            "optimal_path": evaluated[0] if evaluated else None,
            "alternatives": evaluated[1:4] if len(evaluated) > 1 else [],
            "selection_reason": f"基于价值分数 {evaluated[0].get('value_score', 0)} 和风险等级 {evaluated[0].get('risk_level', 'unknown')}"
        }

    def generate_planning_report(self) -> Dict[str, Any]:
        """
        生成完整的路径规划报告
        """
        # 1. 分析系统状态
        system_state = self.analyze_system_state()

        # 2. 生成候选路径
        candidate_paths = self.generate_candidate_paths(num_paths=5)

        # 3. 选择最优路径
        optimal = self.select_optimal_path(candidate_paths)

        return {
            "report_id": f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "system_state": system_state,
            "candidate_paths": candidate_paths,
            "optimal_path": optimal.get("optimal_path"),
            "alternatives": optimal.get("alternatives", []),
            "selection_reason": optimal.get("selection_reason"),
            "recommendations": self._generate总体_recommendations(system_state, optimal)
        }

    def _generate总体_recommendations(self, system_state: Dict, optimal: Dict) -> List[str]:
        """生成总体建议"""
        recommendations = []

        health_score = system_state.get("health_score", 0)
        if health_score < 0.7:
            recommendations.append("系统健康度较低，建议优先进行健康修复")

        success_rate = system_state.get("success_rate", 0)
        if success_rate < 0.8:
            recommendations.append("进化成功率有提升空间，建议优化进化策略")

        if optimal.get("optimal_path"):
            path_name = optimal["optimal_path"].get("path_name", "未知")
            recommendations.append(f"建议下一轮执行：{path_name}")

        return recommendations

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "engine": "EvolutionAdaptivePathPlanning",
            "version": "1.0.0",
            "status": "active",
            "capabilities": [
                "analyze_system_state",
                "generate_candidate_paths",
                "evaluate_path_value",
                "select_optimal_path",
                "generate_planning_report"
            ]
        }


# CLI 接口
def main():
    import argparse

    parser = argparse.ArgumentParser(description="自适应进化路径规划引擎")
    parser.add_argument("command", choices=["status", "analyze", "paths", "report", "optimal"], help="命令")
    parser.add_argument("--num", type=int, default=5, help="生成路径数量")

    args = parser.parse_args()
    engine = EvolutionAdaptivePathPlanning()

    if args.command == "status":
        result = engine.get_status()
    elif args.command == "analyze":
        result = engine.analyze_system_state()
    elif args.command == "paths":
        result = engine.generate_candidate_paths(args.num)
    elif args.command == "report":
        result = engine.generate_planning_report()
    elif args.command == "optimal":
        paths = engine.generate_candidate_paths(args.num)
        result = engine.select_optimal_path(paths)
    else:
        result = {"error": "未知命令"}

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()