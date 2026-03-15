#!/usr/bin/env python3
"""
智能全场景进化环进化效能自动化归因与智能建议引擎

版本: 1.0.0
功能: 让系统能够自动分析每轮进化的成效，识别成功/失败的根本原因，并智能生成可执行的改进建议。
      这是 LLM 特有的大规模分析优势应用——利用对500+轮进化历史的深度理解，自动归因成效并给出改进建议。

依赖:
- round 207 的进化效果自动评估引擎
- round 524 的效能深度分析优化执行引擎
- round 538 的自我进化意识与战略规划引擎
- 可用的进化历史数据

集成到 do.py 支持: 归因分析、根因分析、改进建议、效果归因、attribution 等关键词触发
"""

import os
import sys
import json
import time
import argparse
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from collections import defaultdict
import random

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
RUNTIME_DIR = PROJECT_ROOT / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"


class EvolutionEffectivenessAttributionAdviceEngine:
    """进化效能自动化归因与智能建议引擎"""

    VERSION = "1.0.0"

    def __init__(self):
        self.name = "EvolutionEffectivenessAttributionAdviceEngine"
        self.version = self.VERSION
        self.state_file = STATE_DIR / "effectiveness_attribution_state.json"
        self.history_db = STATE_DIR / "evolution_history.db"
        self.effectiveness_file = STATE_DIR / "evolution_effectiveness_state.json"

    def _load_json(self, filepath: Path, default: Any = None) -> Any:
        """安全加载 JSON 文件"""
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载文件失败 {filepath}: {e}")
        return default if default is not None else {}

    def _save_json(self, filepath: Path, data: Any) -> bool:
        """安全保存 JSON 文件"""
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存文件失败 {filepath}: {e}")
            return False

    def get_evolution_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取进化历史数据"""
        # 尝试从多个数据源获取进化历史
        history_data = []

        # 从 state 文件获取
        state_files = list(STATE_DIR.glob("evolution_completed_*.json"))
        state_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        for f in state_files[:limit]:
            data = self._load_json(f)
            if data:
                history_data.append(data)

        # 从效果评估引擎获取
        effectiveness_data = self._load_json(self.effectiveness_file, {})
        if effectiveness_data:
            history_data.append(effectiveness_data)

        return history_data

    def analyze_effectiveness_attribution(self, history_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析进化成效归因"""
        if not history_data:
            return {
                "status": "no_data",
                "message": "没有足够的进化历史数据进行分析",
                "attribution_results": []
            }

        attribution_results = []

        for entry in history_data:
            # 分析每轮进化的成效归因
            current_goal = entry.get("current_goal", "")
            what_done = entry.get("做了什么", "")
            completion_status = entry.get("是否完成", "未知")
            baseline_check = entry.get("基线校验", "")
            targeted_check = entry.get("针对性校验", "")
            risk_level = entry.get("风险等级", "")

            # 识别成效因素
            success_factors = []
            failure_factors = []
            improvement_areas = []

            # 基于完成状态和校验结果判断
            if "完成" in completion_status and "通过" in targeted_check:
                success_factors.append("目标明确且可执行")
                if "创新" in current_goal:
                    success_factors.append("创新方向明确")
            elif "未完成" in completion_status:
                failure_factors.append("目标执行不完整")
                improvement_areas.append("需要更清晰的目标定义")

            # 基于校验结果判断
            if "通过" in baseline_check:
                success_factors.append("基础能力保持完好")
            else:
                failure_factors.append("基础能力存在问题")
                improvement_areas.append("需要检查基础能力")

            # 基于风险等级判断
            if "低" in risk_level:
                success_factors.append("风险控制良好")
            elif "高" in risk_level:
                failure_factors.append("存在较高风险")
                improvement_areas.append("需要加强风险评估")

            # 生成归因结果
            attribution_results.append({
                "round": entry.get("loop_round", "unknown"),
                "goal": current_goal[:100] + "..." if len(current_goal) > 100 else current_goal,
                "completion": completion_status,
                "success_factors": success_factors,
                "failure_factors": failure_factors,
                "improvement_areas": improvement_areas,
                "root_cause": self._identify_root_cause(success_factors, failure_factors, improvement_areas)
            })

        # 统计分析
        total_rounds = len(attribution_results)
        success_count = sum(1 for r in attribution_results if r["success_factors"])
        failure_count = sum(1 for r in attribution_results if r["failure_factors"])

        return {
            "status": "success",
            "total_analyzed": total_rounds,
            "success_rate": success_count / total_rounds if total_rounds > 0 else 0,
            "failure_rate": failure_count / total_rounds if total_rounds > 0 else 0,
            "attribution_results": attribution_results,
            "summary": self._generate_summary(attribution_results)
        }

    def _identify_root_cause(self, success_factors: List[str], failure_factors: List[str],
                              improvement_areas: List[str]) -> str:
        """识别根本原因"""
        if failure_factors and not success_factors:
            return "主要存在失败因素，需要全面改进"
        elif success_factors and not failure_factors:
            return "主要成功因素，执行良好"
        elif success_factors and failure_factors:
            return "有成功也有失败，需要针对性改进"
        else:
            return "因素不明确，需要更多数据"

    def _generate_summary(self, attribution_results: List[Dict[str, Any]]) -> str:
        """生成归因摘要"""
        if not attribution_results:
            return "没有足够的归因数据"

        all_success = []
        all_failure = []
        all_improvement = []

        for r in attribution_results:
            all_success.extend(r.get("success_factors", []))
            all_failure.extend(r.get("failure_factors", []))
            all_improvement.extend(r.get("improvement_areas", []))

        # 统计最常见的因素
        from collections import Counter
        success_counter = Counter(all_success)
        failure_counter = Counter(all_failure)
        improvement_counter = Counter(all_improvement)

        summary_parts = []

        if success_counter:
            top_success = success_counter.most_common(3)
            summary_parts.append(f"成功因素: {'; '.join([f'{k}({v}次)' for k, v in top_success])}")

        if failure_counter:
            top_failure = failure_counter.most_common(3)
            summary_parts.append(f"失败因素: {'; '.join([f'{k}({v}次)' for k, v in top_failure])}")

        if improvement_counter:
            top_improvement = improvement_counter.most_common(3)
            summary_parts.append(f"改进方向: {'; '.join([f'{k}({v}次)' for k, v in top_improvement])}")

        return " | ".join(summary_parts) if summary_parts else "数据不足以生成摘要"

    def generate_improvement_advice(self, attribution_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """基于归因结果生成改进建议"""
        advice_list = []

        if attribution_result.get("status") == "no_data":
            return [{
                "priority": "high",
                "category": "data_collection",
                "advice": "需要积累更多进化历史数据以进行有效归因分析",
                "action": "继续执行进化环，积累至少20轮数据后再进行归因分析"
            }]

        summary = attribution_result.get("summary", "")
        success_rate = attribution_result.get("success_rate", 0)

        # 基于成功率生成建议
        if success_rate < 0.5:
            advice_list.append({
                "priority": "high",
                "category": "strategy",
                "advice": "当前进化成功率偏低，需要重新评估进化策略",
                "action": "建议回顾最近的失败案例，分析失败根本原因；考虑降低每次进化的复杂度"
            })
        elif success_rate < 0.8:
            advice_list.append({
                "priority": "medium",
                "category": "optimization",
                "advice": "进化成功率有提升空间，建议关注执行细节",
                "action": "分析每轮进化的针对性校验结果，确保执行质量"
            })
        else:
            advice_list.append({
                "priority": "low",
                "category": "innovation",
                "advice": "进化成功率很高，可以尝试更具挑战性的进化方向",
                "action": "考虑探索新的能力边界，尝试创新性更强的进化"
            })

        # 基于摘要中的改进方向生成建议
        if "目标定义" in summary:
            advice_list.append({
                "priority": "high",
                "category": "goal_setting",
                "advice": "目标定义需要更清晰",
                "action": "在假设阶段确保目标具体、可衡量、可达成"
            })

        if "基础能力" in summary:
            advice_list.append({
                "priority": "medium",
                "category": "infrastructure",
                "advice": "基础能力可能存在问题",
                "action": "在每轮执行后运行 self_verify_capabilities.py 确保基础能力完好"
            })

        if "风险" in summary:
            advice_list.append({
                "priority": "medium",
                "category": "risk_management",
                "advice": "需要加强风险管理",
                "action": "在规划阶段增加风险评估步骤，使用价值-风险平衡优化引擎"
            })

        # 添加通用的元进化建议
        advice_list.append({
            "priority": "low",
            "category": "meta_evolution",
            "advice": "持续利用进化效能归因引擎优化进化策略",
            "action": "定期运行归因分析，持续改进进化方法论"
        })

        return advice_list

    def execute_attribution_analysis(self, limit: int = 50) -> Dict[str, Any]:
        """执行归因分析"""
        print(f"=== 进化效能自动化归因分析 ===")
        print(f"分析最近 {limit} 轮进化历史...")

        # 获取进化历史
        history_data = self.get_evolution_history(limit)
        print(f"获取到 {len(history_data)} 条进化历史数据")

        # 分析归因
        attribution_result = self.analyze_effectiveness_attribution(history_data)

        # 生成改进建议
        advice_list = self.generate_improvement_advice(attribution_result)

        # 整合结果
        result = {
            "timestamp": datetime.now().isoformat(),
            "version": self.version,
            "analysis_limit": limit,
            "attribution": attribution_result,
            "advice": advice_list
        }

        # 保存状态
        self._save_json(self.state_file, result)

        print(f"\n=== 归因分析完成 ===")
        print(f"分析轮次: {attribution_result.get('total_analyzed', 0)}")
        print(f"成功率: {attribution_result.get('success_rate', 0):.1%}")
        print(f"失败率: {attribution_result.get('failure_rate', 0):.1%}")
        print(f"\n摘要: {attribution_result.get('summary', 'N/A')}")
        print(f"\n改进建议数量: {len(advice_list)}")

        return result

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱数据"""
        state_data = self._load_json(self.state_file, {})

        if not state_data:
            return {
                "status": "no_data",
                "message": "没有可用的归因分析数据"
            }

        attribution = state_data.get("attribution", {})
        advice = state_data.get("advice", [])

        return {
            "status": "ok",
            "total_analyzed": attribution.get("total_analyzed", 0),
            "success_rate": attribution.get("success_rate", 0),
            "failure_rate": attribution.get("failure_rate", 0),
            "summary": attribution.get("summary", ""),
            "advice_count": len(advice),
            "top_advice": advice[:3] if advice else []
        }


def main():
    parser = argparse.ArgumentParser(
        description="智能全场景进化环进化效能自动化归因与智能建议引擎"
    )
    parser.add_argument("--analyze", action="store_true", help="执行归因分析")
    parser.add_argument("--limit", type=int, default=50, help="分析的历史轮次数量，默认50")
    parser.add_argument("--advice", action="store_true", help="生成改进建议")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")

    args = parser.parse_args()

    engine = EvolutionEffectivenessAttributionAdviceEngine()

    if args.analyze or args.advice:
        result = engine.execute_attribution_analysis(limit=args.limit)
        print("\n=== 改进建议 ===")
        for i, advice in enumerate(result.get("advice", []), 1):
            print(f"\n{i}. [{advice['priority'].upper()}] {advice['category']}")
            print(f"   建议: {advice['advice']}")
            print(f"   操作: {advice['action']}")

    elif args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()