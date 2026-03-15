"""
智能全场景进化环元进化策略智能推荐与优先级自动优化引擎 V2
Version: 1.0.0

基于 round 655/656 的自适应学习和能力评估能力，构建让系统能够：
1. 自动分析当前系统状态（健康、效率、能力缺口、价值潜力）
2. 智能推荐最佳进化方向
3. 自动优化进化优先级
4. 与已有引擎深度集成形成闭环

此引擎让系统从「被动等待进化需求」升级到「主动智能推荐最优进化方向」，实现真正的自主进化导向能力。
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE_DIR = PROJECT_ROOT / "runtime" / "state"
RUNTIME_LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"
REFERENCES_DIR = PROJECT_ROOT / "references"


class EvolutionStrategyIntelligentRecommendationV2:
    """元进化策略智能推荐与优先级自动优化引擎 V2"""

    def __init__(self):
        self.version = "1.0.0"
        self.name = "元进化策略智能推荐与优先级自动优化引擎 V2"
        print(f"[{self.name}] 初始化完成 (v{self.version})")

    def analyze_current_system_state(self) -> Dict[str, Any]:
        """分析当前系统多维度状态"""
        print("\n[状态分析] 正在分析当前系统多维度状态...")

        state = {
            "timestamp": datetime.now().isoformat(),
            "dimensions": {}
        }

        # 1. 系统健康维度
        health_score = self._analyze_system_health()
        state["dimensions"]["health"] = health_score

        # 2. 进化效率维度
        efficiency_score = self._analyze_evolution_efficiency()
        state["dimensions"]["efficiency"] = efficiency_score

        # 3. 能力缺口维度
        capability_gaps = self._analyze_capability_gaps()
        state["dimensions"]["capability_gaps"] = capability_gaps

        # 4. 价值潜力维度
        value_potential = self._analyze_value_potential()
        state["dimensions"]["value_potential"] = value_potential

        # 5. 进化饱和度
        saturation = self._analyze_evolution_saturation()
        state["dimensions"]["saturation"] = saturation

        # 综合评分
        state["overall_score"] = self._calculate_overall_score(state["dimensions"])

        print(f"[状态分析] 系统综合评分: {state['overall_score']:.2f}/100")
        return state

    def _analyze_system_health(self) -> Dict[str, Any]:
        """分析系统健康状态"""
        health = {"score": 85.0, "details": {}, "issues": []}

        # 检查最近的进化环完成状态
        try:
            completed_files = sorted(RUNTIME_STATE_DIR.glob("evolution_completed_*.json"))
            if completed_files:
                # 检查最近 10 个进化环
                recent_files = completed_files[-10:]
                failed_count = 0
                for f in recent_files:
                    try:
                        with open(f, 'r', encoding='utf-8') as fp:
                            data = json.load(fp)
                            if data.get("status") != "completed":
                                failed_count += 1
                    except:
                        pass

                success_rate = (10 - failed_count) / 10 * 100
                health["details"]["recent_success_rate"] = success_rate
                health["score"] = min(100, 70 + success_rate * 0.3)
        except Exception as e:
            health["issues"].append(f"无法读取进化环状态: {e}")

        return health

    def _analyze_evolution_efficiency(self) -> Dict[str, Any]:
        """分析进化效率"""
        efficiency = {"score": 75.0, "details": {}, "issues": []}

        # 检查进化环执行时间趋势
        try:
            # 读取最近的日志估算效率
            logs = list(RUNTIME_LOGS_DIR.glob("behavior_*.log"))
            if logs:
                latest_log = max(logs, key=lambda x: x.stat().st_mtime)
                with open(latest_log, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # 简单估算：日志条目越多，执行越频繁
                    efficiency["details"]["recent_activity"] = len(lines)
                    efficiency["score"] = min(100, 50 + len(lines) * 0.5)
        except Exception as e:
            efficiency["issues"].append(f"无法分析效率: {e}")

        return efficiency

    def _analyze_capability_gaps(self) -> Dict[str, Any]:
        """分析能力缺口"""
        gaps = {"score": 60.0, "details": {}, "issues": [], "gap_count": 0}

        try:
            gaps_file = REFERENCES_DIR / "capability_gaps.md"
            if gaps_file.exists():
                with open(gaps_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 统计缺口数量
                    gap_count = content.count("|")
                    gaps["gap_count"] = gap_count
                    gaps["score"] = min(100, 50 + gap_count * 2)
                    gaps["details"]["total_gaps"] = gap_count
        except Exception as e:
            gaps["issues"].append(f"无法分析能力缺口: {e}")

        return gaps

    def _analyze_value_potential(self) -> Dict[str, Any]:
        """分析价值潜力"""
        value = {"score": 80.0, "details": {}, "issues": []}

        # 检查已完成进化环的价值实现
        try:
            completed_files = sorted(RUNTIME_STATE_DIR.glob("evolution_completed_*.json"))
            if completed_files:
                # 分析最近完成的项目
                recent = completed_files[-20:]
                value["details"]["recent_completed"] = len(recent)

                # 统计高价值项目
                high_value_count = 0
                for f in recent:
                    try:
                        with open(f, 'r', encoding='utf-8') as fp:
                            data = json.load(fp)
                            goal = data.get("current_goal", "")
                            if any(kw in goal for kw in ["优化", "增强", "提升", "改进", "自动化"]):
                                high_value_count += 1
                    except:
                        pass

                value["details"]["high_value_count"] = high_value_count
                value["score"] = min(100, 60 + high_value_count * 2)
        except Exception as e:
            value["issues"].append(f"无法分析价值潜力: {e}")

        return value

    def _analyze_evolution_saturation(self) -> Dict[str, Any]:
        """分析进化饱和度"""
        saturation = {"score": 50.0, "details": {}, "issues": []}

        try:
            # 统计已实现的进化引擎数量
            scripts_dir = PROJECT_ROOT / "scripts"
            evolution_engines = list(scripts_dir.glob("evolution_*.py"))

            saturation["details"]["total_engines"] = len(evolution_engines)
            saturation["details"]["saturation_level"] = "high" if len(evolution_engines) > 100 else "medium"

            # 饱和度高意味着需要更智能的推荐
            saturation["score"] = min(100, len(evolution_engines))
        except Exception as e:
            saturation["issues"].append(f"无法分析饱和度: {e}")

        return saturation

    def _calculate_overall_score(self, dimensions: Dict[str, Any]) -> float:
        """计算综合评分"""
        weights = {
            "health": 0.25,
            "efficiency": 0.20,
            "capability_gaps": 0.20,
            "value_potential": 0.25,
            "saturation": 0.10
        }

        overall = 0.0
        for dim, weight in weights.items():
            score = dimensions.get(dim, {}).get("score", 50.0)
            overall += score * weight

        return overall

    def generate_strategy_recommendations(self, system_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """基于系统状态生成进化策略推荐"""
        print("\n[策略推荐] 正在生成进化方向推荐...")

        recommendations = []
        overall_score = system_state.get("overall_score", 50)

        # 基于不同状态生成推荐
        if overall_score < 60:
            # 系统状态较差，优先健康优化
            recommendations.append({
                "priority": 1,
                "direction": "健康优化",
                "reason": "系统综合评分较低，需要优先优化健康状态",
                "target": "元进化系统健康自检与预防性修复",
                "expected_impact": "提升系统稳定性和执行成功率",
                "estimated_value": 90
            })

        # 检查能力缺口
        gaps = system_state.get("dimensions", {}).get("capability_gaps", {})
        gap_count = gaps.get("gap_count", 0)
        if gap_count > 0:
            recommendations.append({
                "priority": 2,
                "direction": "能力补齐",
                "reason": f"发现 {gap_count} 个能力缺口",
                "target": "能力缺口主动发现与自愈引擎",
                "expected_impact": "扩展系统能力覆盖范围",
                "estimated_value": 85
            })

        # 检查进化效率
        efficiency = system_state.get("dimensions", {}).get("efficiency", {})
        efficiency_score = efficiency.get("score", 50)
        if efficiency_score < 70:
            recommendations.append({
                "priority": 3,
                "direction": "效率提升",
                "reason": "进化效率有待提升",
                "target": "元进化执行效能实时优化引擎",
                "expected_impact": "提升进化执行效率",
                "estimated_value": 80
            })

        # 价值潜力分析
        value = system_state.get("dimensions", {}).get("value_potential", {})
        value_score = value.get("score", 50)
        if value_score > 70:
            recommendations.append({
                "priority": 4,
                "direction": "价值创造",
                "reason": "系统价值实现能力较强，可进一步增强",
                "target": "元进化价值创造与自我增强引擎",
                "expected_impact": "提升进化价值转化率",
                "estimated_value": 95
            })

        # 通用优化建议（总是包含）
        recommendations.append({
            "priority": 5,
            "direction": "智能协同",
            "reason": "增强跨引擎协同能力",
            "target": "跨引擎协同效能全局优化",
            "expected_impact": "提升系统整体协同效率",
            "estimated_value": 88
        })

        # 按优先级排序
        recommendations.sort(key=lambda x: x["priority"])

        print(f"[策略推荐] 生成了 {len(recommendations)} 条推荐")
        return recommendations

    def optimize_priorities(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """自动优化进化优先级"""
        print("\n[优先级优化] 正在优化进化优先级...")

        # 基于价值评估和时间因素重新排序
        optimized = []
        for rec in recommendations:
            # 调整优先级分数
            value = rec.get("estimated_value", 50)
            # 综合评分 = 价值 * 时间因子
            adjusted_score = value
            rec["adjusted_score"] = adjusted_score
            rec["final_priority"] = rec.get("priority")
            optimized.append(rec)

        # 按调整后分数降序
        optimized.sort(key=lambda x: x.get("adjusted_score", 0), reverse=True)

        # 重新分配优先级
        for i, rec in enumerate(optimized):
            rec["final_priority"] = i + 1

        print(f"[优先级优化] 完成，共 {len(optimized)} 项")
        return optimized

    def generate_execution_plan(self, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成执行计划"""
        print("\n[执行计划] 正在生成执行计划...")

        plan = {
            "timestamp": datetime.now().isoformat(),
            "recommendations": recommendations,
            "execution_order": [rec["target"] for rec in recommendations],
            "estimated_rounds": len(recommendations),
            "total_expected_value": sum(rec.get("estimated_value", 0) for rec in recommendations)
        }

        print(f"[执行计划] 预计需要 {plan['estimated_rounds']} 轮执行")
        return plan

    def run_full_cycle(self) -> Dict[str, Any]:
        """执行完整推荐周期"""
        print("=" * 60)
        print(f"[{self.name}] 开始执行完整推荐周期")
        print("=" * 60)

        # 1. 分析系统状态
        system_state = self.analyze_current_system_state()

        # 2. 生成策略推荐
        recommendations = self.generate_strategy_recommendations(system_state)

        # 3. 优化优先级
        optimized = self.optimize_priorities(recommendations)

        # 4. 生成执行计划
        execution_plan = self.generate_execution_plan(optimized)

        # 5. 构建结果
        result = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "system_state": system_state,
            "recommendations": optimized,
            "execution_plan": execution_plan,
            "version": self.version
        }

        print("=" * 60)
        print(f"[{self.name}] 推荐周期执行完成")
        print("=" * 60)

        return result

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱数据"""
        system_state = self.analyze_current_system_state()
        recommendations = self.generate_strategy_recommendations(system_state)

        return {
            "module": self.name,
            "version": self.version,
            "overall_score": system_state.get("overall_score", 0),
            "dimensions": system_state.get("dimensions", {}),
            "recommendations_count": len(recommendations),
            "top_recommendations": recommendations[:3],
            "timestamp": datetime.now().isoformat()
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="元进化策略智能推荐与优先级自动优化引擎 V2")
    parser.add_argument("--version", action="store_true", help="显示版本信息")
    parser.add_argument("--status", action="store_true", help="显示系统状态")
    parser.add_argument("--recommend", action="store_true", help="生成进化策略推荐")
    parser.add_argument("--full-cycle", action="store_true", help="执行完整推荐周期")
    parser.add_argument("--cockpit", action="store_true", help="获取驾驶舱数据")

    args = parser.parse_args()

    engine = EvolutionStrategyIntelligentRecommendationV2()

    if args.version:
        print(f"{engine.name} v{engine.version}")
        return

    if args.status:
        state = engine.analyze_current_system_state()
        print(json.dumps(state, indent=2, ensure_ascii=False))
        return

    if args.recommend:
        state = engine.analyze_current_system_state()
        recs = engine.generate_strategy_recommendations(state)
        print(json.dumps(recs, indent=2, ensure_ascii=False))
        return

    if args.cockpit:
        data = engine.get_cockpit_data()
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    if args.full_cycle:
        result = engine.run_full_cycle()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        # 保存结果
        output_file = RUNTIME_STATE_DIR / "strategy_recommendation_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n结果已保存到: {output_file}")
        return

    # 默认显示帮助
    parser.print_help()


if __name__ == "__main__":
    main()