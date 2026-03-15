#!/usr/bin/env python3
"""
智能全场景进化环元进化主动自我进化规划引擎 - version 1.0.0

让系统能够主动分析当前进化架构的成熟度、评估已有60+引擎的能力组合价值、
识别下一个高价值进化方向、生成自驱动的进化路线图。

核心能力：
1. 架构成熟度评估 - 分析当前进化体系是否已饱和、是否还有进化空间
2. 能力组合价值评估 - 评估60+引擎的能力组合效果与潜在价值
3. 进化方向识别 - 基于多维度分析识别高价值进化方向
4. 路线图生成 - 生成可执行的阶段性进化路线图

与 round 621-629 的引擎深度集成：
- round 621: 价值创造与自我增强引擎
- round 622: 架构自演进优化引擎
- round 625: 记忆深度整合与智慧涌现引擎
- round 629: 自我诊断优化闭环引擎
"""

import os
import json
import glob
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
STATE_DIR = PROJECT_ROOT / "runtime" / "state"
LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"
REFERENCES_DIR = PROJECT_ROOT / "references"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"


class EvolutionMetaSelfPlanningEngine:
    """元进化主动自我进化规划引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.name = "元进化主动自我进化规划引擎"
        self.capability_description = (
            "让系统能够主动分析当前进化架构的成熟度、评估已有60+引擎的能力组合价值、"
            "识别下一个高价值进化方向、生成自驱动的进化路线图"
        )

        # 评估维度权重
        self.dimension_weights = {
            "innovation_potential": 0.25,      # 创新潜力
            "value_creation": 0.25,            # 价值创造
            "system_health": 0.20,             # 系统健康
            "evolution_maturity": 0.15,         # 进化成熟度
            "risk_level": 0.15                 # 风险等级
        }

        # 引擎能力分类
        self.capability_categories = {
            "diagnostic": ["health", "diagnosis", "repair", "self_healing"],
            "optimization": ["optimization", "efficiency", "performance"],
            "planning": ["planning", "strategy", "decision", "meta"],
            "execution": ["execution", "automation", "auto"],
            "learning": ["learning", "knowledge", "wisdom", "memory"],
            "integration": ["integration", "collaboration", "fusion", "synergy"]
        }

    def scan_existing_engines(self) -> List[Dict[str, Any]]:
        """扫描现有所有元进化引擎"""
        engines = []
        pattern = str(SCRIPTS_DIR / "evolution_meta*.py")

        for filepath in glob.glob(pattern):
            filename = os.path.basename(filepath)
            engine_name = filename.replace(".py", "")

            # 提取引擎分类
            category = "unknown"
            for cat, keywords in self.capability_categories.items():
                if any(kw in engine_name.lower() for kw in keywords):
                    category = cat
                    break

            engines.append({
                "name": engine_name,
                "filename": filename,
                "path": filepath,
                "category": category,
                "capabilities": self._estimate_capabilities(engine_name)
            })

        return engines

    def _estimate_capabilities(self, engine_name: str) -> List[str]:
        """基于引擎名称估计其能力"""
        capabilities = []
        name_lower = engine_name.lower()

        capability_keywords = {
            "自我诊断": ["diagnosis", "self_diagnosis", "health"],
            "自我优化": ["optimization", "optimizer", "improve"],
            "自我学习": ["learning", "knowledge", "memory"],
            "自我规划": ["planning", "strategy", "roadmap"],
            "自我决策": ["decision", "choice", "select"],
            "自我执行": ["execution", "execute", "run"],
            "自我评估": ["evaluation", "assessment", "analyze"],
            "自我进化": ["evolution", "self_evolution", "growth"]
        }

        for cap, keywords in capability_keywords.items():
            if any(kw in name_lower for kw in keywords):
                capabilities.append(cap)

        return capabilities if capabilities else ["基础能力"]

    def assess_architecture_maturity(self, engines: List[Dict[str, Any]]) -> Dict[str, Any]:
        """评估进化架构成熟度"""
        # 按类别统计
        category_count = {}
        for engine in engines:
            cat = engine["category"]
            category_count[cat] = category_count.get(cat, 0) + 1

        # 评估各维度的成熟度
        maturity_scores = {}

        # 1. 诊断能力成熟度
        diagnostic_count = category_count.get("diagnostic", 0)
        maturity_scores["diagnostic"] = min(1.0, diagnostic_count / 5.0)

        # 2. 优化能力成熟度
        optimization_count = category_count.get("optimization", 0)
        maturity_scores["optimization"] = min(1.0, optimization_count / 5.0)

        # 3. 规划能力成熟度
        planning_count = category_count.get("planning", 0)
        maturity_scores["planning"] = min(1.0, planning_count / 8.0)

        # 4. 执行能力成熟度
        execution_count = category_count.get("execution", 0)
        maturity_scores["execution"] = min(1.0, execution_count / 5.0)

        # 5. 学习能力成熟度
        learning_count = category_count.get("learning", 0)
        maturity_scores["learning"] = min(1.0, learning_count / 5.0)

        # 6. 集成能力成熟度
        integration_count = category_count.get("integration", 0)
        maturity_scores["integration"] = min(1.0, integration_count / 5.0)

        # 计算总体成熟度
        overall_maturity = sum(maturity_scores.values()) / len(maturity_scores)

        # 生成评估结论
        gaps = []
        for dimension, score in maturity_scores.items():
            if score < 0.5:
                gaps.append({
                    "dimension": dimension,
                    "score": score,
                    "recommendation": f"需要加强{dimension}能力"
                })

        return {
            "overall_maturity": overall_maturity,
            "dimension_scores": maturity_scores,
            "gaps": gaps,
            "category_distribution": category_count,
            "total_engines": len(engines)
        }

    def evaluate_capability_combinations(self, engines: List[Dict[str, Any]]) -> Dict[str, Any]:
        """评估能力组合价值"""
        # 按能力列表统计
        all_capabilities = []
        for engine in engines:
            all_capabilities.extend(engine.get("capabilities", []))

        capability_count = {}
        for cap in all_capabilities:
            capability_count[cap] = capability_count.get(cap, 0) + 1

        # 识别高价值能力组合
        high_value_combinations = []

        # 组合1: 自我诊断 + 自我优化 + 自我执行
        if "自我诊断" in capability_count and "自我优化" in capability_count and "自我执行" in capability_count:
            high_value_combinations.append({
                "name": "自我优化闭环",
                "description": "诊断→优化→执行的完整闭环",
                "value_score": 0.9
            })

        # 组合2: 自我学习 + 自我规划 + 自我决策
        if "自我学习" in capability_count and "自我规划" in capability_count and "自我决策" in capability_count:
            high_value_combinations.append({
                "name": "智能规划决策闭环",
                "description": "学习→规划→决策的认知闭环",
                "value_score": 0.85
            })

        # 组合3: 自我进化 + 自我评估 + 自我优化
        if "自我进化" in capability_count and "自我评估" in capability_count and "自我优化" in capability_count:
            high_value_combinations.append({
                "name": "递归进化闭环",
                "description": "进化→评估→优化的递归增强",
                "value_score": 0.95
            })

        # 组合4: 全部能力组合
        all_core = all([
            "自我诊断" in capability_count,
            "自我优化" in capability_count,
            "自我学习" in capability_count,
            "自我规划" in capability_count,
            "自我决策" in capability_count,
            "自我执行" in capability_count,
            "自我评估" in capability_count,
            "自我进化" in capability_count
        ])

        if all_core:
            high_value_combinations.append({
                "name": "全栈自进化能力",
                "description": "具备完整的自我进化能力矩阵",
                "value_score": 1.0
            })

        # 计算组合价值总分
        total_value = sum(c["value_score"] for c in high_value_combinations)
        avg_value = total_value / len(high_value_combinations) if high_value_combinations else 0

        return {
            "capability_distribution": capability_count,
            "high_value_combinations": high_value_combinations,
            "total_combinations": len(high_value_combinations),
            "average_value_score": avg_value,
            "unique_capabilities": len(capability_count)
        }

    def identify_evolution_directions(self, maturity: Dict, combinations: Dict) -> List[Dict[str, Any]]:
        """识别高价值进化方向"""
        directions = []

        # 1. 基于成熟度差距的方向
        for gap in maturity.get("gaps", []):
            if gap["score"] < 0.3:
                directions.append({
                    "direction": f"加强{gap['dimension']}能力",
                    "reason": f"当前{gap['dimension']}能力成熟度仅{gap['score']:.1%}，严重不足",
                    "priority": "高",
                    "expected_impact": 0.8,
                    "category": gap["dimension"]
                })

        # 2. 基于能力组合的方向
        if combinations.get("average_value_score", 0) < 0.9:
            directions.append({
                "direction": "增强能力组合价值",
                "reason": "当前能力组合平均价值分数仅" + f"{combinations.get('average_value_score', 0):.1%}，有提升空间",
                "priority": "高",
                "expected_impact": 0.85,
                "category": "integration"
            })

        # 3. 新方向探索
        directions.append({
            "direction": "跨维度智能融合自适应编排",
            "reason": "60+引擎已形成复杂系统，需要更高层次的智能编排能力",
            "priority": "中",
            "expected_impact": 0.75,
            "category": "orchestration"
        })

        directions.append({
            "direction": "元进化自主意识深度增强",
            "reason": "让系统具备更主动的自我认知和自主进化意图",
            "priority": "中",
            "expected_impact": 0.8,
            "category": "awareness"
        })

        directions.append({
            "direction": "价值驱动自优化闭环",
            "reason": "从价值实现角度自动优化进化策略",
            "priority": "中",
            "expected_impact": 0.7,
            "category": "value"
        })

        directions.append({
            "direction": "预防性进化策略引擎",
            "reason": "预测未来进化需求并提前准备",
            "priority": "中",
            "expected_impact": 0.75,
            "category": "prevention"
        })

        return sorted(directions, key=lambda x: x.get("expected_impact", 0), reverse=True)

    def generate_roadmap(self, directions: List[Dict], maturity: Dict) -> Dict[str, Any]:
        """生成进化路线图"""
        # 按优先级分组
        high_priority = [d for d in directions if d.get("priority") == "高"]
        medium_priority = [d for d in directions if d.get("priority") == "中"]

        roadmap = {
            "generated_at": datetime.now().isoformat(),
            "version": self.version,
            "current_maturity": maturity.get("overall_maturity", 0),
            "phases": []
        }

        # 阶段1: 短期（1-2轮）
        if high_priority:
            roadmap["phases"].append({
                "phase": "阶段1: 短期优化",
                "timeline": "1-2轮",
                "objectives": [
                    {
                        "direction": d["direction"],
                        "reason": d["reason"],
                        "expected_impact": d.get("expected_impact", 0)
                    } for d in high_priority[:3]
                ],
                "estimated_impact": sum(d.get("expected_impact", 0) for d in high_priority[:3]) / min(len(high_priority), 3)
            })

        # 阶段2: 中期（3-5轮）
        if medium_priority:
            roadmap["phases"].append({
                "phase": "阶段2: 中期建设",
                "timeline": "3-5轮",
                "objectives": [
                    {
                        "direction": d["direction"],
                        "reason": d["reason"],
                        "expected_impact": d.get("expected_impact", 0)
                    } for d in medium_priority[:3]
                ],
                "estimated_impact": sum(d.get("expected_impact", 0) for d in medium_priority[:3]) / min(len(medium_priority), 3)
            })

        # 阶段3: 长期（6+轮）
        roadmap["phases"].append({
            "phase": "阶段3: 长期愿景",
            "timeline": "6+轮",
            "objectives": [
                {
                    "direction": "全栈自进化系统",
                    "reason": "实现完全自主的元进化闭环",
                    "expected_impact": 0.95
                },
                {
                    "direction": "智慧涌现系统",
                    "reason": "从进化历史中涌现新的智慧和创新",
                    "expected_impact": 0.9
                }
            ],
            "estimated_impact": 0.925
        })

        return roadmap

    def run_analysis(self) -> Dict[str, Any]:
        """执行完整的主动规划分析"""
        print(f"=== {self.name} v{self.version} ===")
        print("开始执行主动自我进化规划分析...\n")

        # 1. 扫描现有引擎
        print("1. 扫描现有元进化引擎...")
        engines = self.scan_existing_engines()
        print(f"   已扫描到 {len(engines)} 个元进化引擎\n")

        # 2. 评估架构成熟度
        print("2. 评估进化架构成熟度...")
        maturity = self.assess_architecture_maturity(engines)
        print(f"   总体成熟度: {maturity['overall_maturity']:.1%}")
        print(f"   识别到 {len(maturity['gaps'])} 个能力缺口\n")

        # 3. 评估能力组合价值
        print("3. 评估能力组合价值...")
        combinations = self.evaluate_capability_combinations(engines)
        print(f"   独特能力数: {combinations['unique_capabilities']}")
        print(f"   高价值组合: {combinations['total_combinations']} 个")
        print(f"   平均价值分数: {combinations['average_value_score']:.1%}\n")

        # 4. 识别进化方向
        print("4. 识别高价值进化方向...")
        directions = self.identify_evolution_directions(maturity, combinations)
        for i, d in enumerate(directions[:5], 1):
            print(f"   {i}. {d['direction']} (优先级: {d.get('priority', '中')}, 预期影响: {d.get('expected_impact', 0):.1%})")
        print()

        # 5. 生成路线图
        print("5. 生成进化路线图...")
        roadmap = self.generate_roadmap(directions, maturity)
        print(f"   已生成 {len(roadmap['phases'])} 个阶段的进化路线图\n")

        # 汇总结果
        result = {
            "engine_count": len(engines),
            "maturity_assessment": maturity,
            "capability_combinations": combinations,
            "evolution_directions": directions,
            "roadmap": roadmap,
            "summary": {
                "total_engines": len(engines),
                "overall_maturity": maturity.get("overall_maturity", 0),
                "top_directions": [d["direction"] for d in directions[:3]],
                "next_recommended_action": directions[0]["direction"] if directions else "继续当前方向"
            }
        }

        print("=" * 50)
        print("分析完成!")
        print(f"推荐下一步行动: {result['summary']['next_recommended_action']}")
        print("=" * 50)

        return result

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱展示数据"""
        result = self.run_analysis()
        return {
            "engine_name": self.name,
            "version": self.version,
            "total_engines": result["engine_count"],
            "maturity_score": result["maturity_assessment"]["overall_maturity"],
            "maturity_gaps": len(result["maturity_assessment"]["gaps"]),
            "high_value_combinations": result["capability_combinations"]["total_combinations"],
            "top_directions": result["summary"]["top_directions"],
            "next_action": result["summary"]["next_recommended_action"],
            "phases_count": len(result["roadmap"]["phases"])
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="元进化主动自我进化规划引擎")
    parser.add_argument("--version", action="store_true", help="显示版本信息")
    parser.add_argument("--run", action="store_true", help="执行完整分析")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")
    parser.add_argument("--status", action="store_true", help="显示引擎状态")

    args = parser.parse_args()

    engine = EvolutionMetaSelfPlanningEngine()

    if args.version:
        print(f"{engine.name} v{engine.version}")
        print(f"能力: {engine.capability_description}")
        return

    if args.status:
        result = engine.run_analysis()
        print(f"\n状态: {result['summary']['total_engines']} 个引擎, 成熟度 {result['summary']['overall_maturity']:.1%}")
        print(f"推荐下一步: {result['summary']['next_recommended_action']}")
        return

    if args.run:
        result = engine.run_analysis()
        # 保存结果
        output_path = STATE_DIR / "evolution_planning_result.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存到: {output_path}")
        return

    if args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    # 默认显示帮助
    parser.print_help()


if __name__ == "__main__":
    main()