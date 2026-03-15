"""
智能全场景进化环元进化方法论自省与递归优化引擎
version 1.0.0

让系统能够从600+轮进化历史中深度分析自身进化方法论的有效性，
自动发现进化策略的优化空间，识别低效模式和成功模式，
形成真正的「学会如何进化得更好」的递归优化能力。

功能：
1. 进化方法论深度分析 - 从600+轮进化历史中提取进化模式、效率评估、成功率分析
2. 进化策略优化空间发现 - 自动识别低效策略、高潜力策略
3. 递归优化能力 - 基于分析结果自动生成优化建议并可选择执行
4. 进化方向预测 - 预测下阶段最有效的进化方向
5. 驾驶舱数据接口
6. do.py 集成

依赖：600+轮进化历史、round 598 元认知自省引擎
"""

import os
import json
import glob
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

# 路径配置
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE_DIR = PROJECT_ROOT / "runtime" / "state"
RUNTIME_LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"
REFERENCES_DIR = PROJECT_ROOT / "references"


class MetaMethodologySelfReflectionOptimizer:
    """元进化方法论自省与递归优化引擎"""

    VERSION = "1.0.0"

    def __init__(self):
        self.evolution_history = []
        self.patterns = {}
        self.efficiency_metrics = {}
        self.optimization_suggestions = []
        self.predicted_directions = []

    def load_evolution_history(self) -> List[Dict]:
        """加载进化历史"""
        history = []

        # 加载 evolution_completed_*.json 文件
        completed_files = glob.glob(str(RUNTIME_STATE_DIR / "evolution_completed_*.json"))

        for file_path in completed_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    history.append(data)
            except Exception as e:
                print(f"Warning: Failed to load {file_path}: {e}")

        # 按时间排序
        history.sort(key=lambda x: x.get('updated_at', ''), reverse=True)

        self.evolution_history = history
        return history

    def analyze_evolution_patterns(self) -> Dict[str, Any]:
        """分析进化模式"""
        if not self.evolution_history:
            self.load_evolution_history()

        patterns = {
            "total_rounds": len(self.evolution_history),
            "completed_rounds": sum(1 for h in self.evolution_history if h.get('status') == 'completed'),
            "failed_rounds": sum(1 for h in self.evolution_history if h.get('status') == 'failed'),
            "category_distribution": defaultdict(int),
            "success_factors": [],
            "failure_patterns": [],
            "avg_completion_time": 0,
            "efficiency_trend": []
        }

        # 分析类别分布
        for h in self.evolution_history:
            goal = h.get('current_goal', '')
            if '元进化' in goal:
                patterns["category_distribution"]["元进化"] += 1
            elif '知识' in goal or '图谱' in goal:
                patterns["category_distribution"]["知识图谱"] += 1
            elif '创新' in goal:
                patterns["category_distribution"]["创新"] += 1
            elif '价值' in goal:
                patterns["category_distribution"]["价值"] += 1
            elif '健康' in goal or '自愈' in goal:
                patterns["category_distribution"]["健康"] += 1
            elif '执行' in goal or '自动化' in goal:
                patterns["category_distribution"]["执行"] += 1
            elif '决策' in goal:
                patterns["category_distribution"]["决策"] += 1
            else:
                patterns["category_distribution"]["其他"] += 1

        # 转换为普通 dict
        patterns["category_distribution"] = dict(patterns["category_distribution"])

        # 计算平均完成时间（如果有时间戳）
        completion_times = []
        for h in self.evolution_history:
            if 'updated_at' in h:
                try:
                    dt = datetime.fromisoformat(h['updated_at'].replace('+00:00', ''))
                    completion_times.append(dt)
                except:
                    pass

        if len(completion_times) >= 2:
            time_diffs = []
            for i in range(1, len(completion_times)):
                diff = (completion_times[i-1] - completion_times[i]).total_seconds() / 60
                time_diffs.append(diff)
            patterns["avg_completion_time"] = sum(time_diffs) / len(time_diffs) if time_diffs else 0

        self.patterns = patterns
        return patterns

    def discover_optimization_opportunities(self) -> Dict[str, Any]:
        """发现进化策略优化空间"""
        if not self.patterns:
            self.analyze_evolution_patterns()

        opportunities = {
            "inefficient_patterns": [],
            "high_potential_patterns": [],
            "resource_waste": [],
            "duplicate_efforts": [],
            "optimization_score": 0
        }

        # 分析低效模式
        category_dist = self.patterns.get("category_distribution", {})

        # 检查是否存在重复或过度集中的进化方向
        if category_dist:
            total = sum(category_dist.values())
            for category, count in category_dist.items():
                ratio = count / total if total > 0 else 0

                if ratio > 0.3:  # 超过30%的进化集中在一个方向
                    opportunities["inefficient_patterns"].append({
                        "type": "over_concentration",
                        "category": category,
                        "ratio": round(ratio, 3),
                        "suggestion": f"考虑分散进化方向到其他领域，当前{category}占比{ratio:.1%}"
                    })

        # 检查成功率低的模式
        completion_rate = self.patterns["completed_rounds"] / self.patterns["total_rounds"] if self.patterns["total_rounds"] > 0 else 0

        if completion_rate < 0.8:
            opportunities["inefficient_patterns"].append({
                "type": "low_completion_rate",
                "rate": round(completion_rate, 3),
                "suggestion": "整体完成率较低，建议优化进化流程和决策机制"
            })

        # 发现高潜力模式
        if completion_rate > 0.9:
            opportunities["high_potential_patterns"].append({
                "type": "high_completion",
                "rate": round(completion_rate, 3),
                "suggestion": "进化流程成熟，可尝试更具挑战性的目标"
            })

        # 识别资源浪费
        if self.patterns.get("avg_completion_time", 0) > 30:
            opportunities["resource_waste"].append({
                "type": "long_completion_time",
                "avg_time": round(self.patterns["avg_completion_time"], 1),
                "suggestion": "平均完成时间较长，可优化执行效率"
            })

        # 计算优化分数
        optimization_score = 100
        optimization_score -= len(opportunities["inefficient_patterns"]) * 15
        optimization_score -= len(opportunities["resource_waste"]) * 10
        optimization_score += len(opportunities["high_potential_patterns"]) * 10
        opportunities["optimization_score"] = max(0, min(100, optimization_score))

        self.efficiency_metrics = opportunities
        return opportunities

    def generate_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """生成优化建议"""
        if not self.efficiency_metrics:
            self.discover_optimization_opportunities()

        suggestions = []

        # 基于低效模式生成建议
        for inefficient in self.efficiency_metrics.get("inefficient_patterns", []):
            suggestions.append({
                "priority": "high",
                "category": "pattern_optimization",
                "description": inefficient.get("suggestion", ""),
                "action": f"调整{int(inefficient.get('ratio', 0) * 100) if 'ratio' in inefficient else 20}%的进化资源分配",
                "expected_impact": "提升进化多样性，降低重复风险"
            })

        # 基于资源浪费生成建议
        for waste in self.efficiency_metrics.get("resource_waste", []):
            suggestions.append({
                "priority": "medium",
                "category": "efficiency_optimization",
                "description": waste.get("suggestion", ""),
                "action": "优化执行流程，减少等待时间",
                "expected_impact": f"缩短完成时间至30分钟以内（当前{waste.get('avg_time', 0):.1f}分钟）"
            })

        # 基于高潜力模式生成建议
        for high_pot in self.efficiency_metrics.get("high_potential_patterns", []):
            suggestions.append({
                "priority": "low",
                "category": "growth_opportunity",
                "description": high_pot.get("suggestion", ""),
                "action": "设定更具挑战性的进化目标",
                "expected_impact": "推动系统向更高层次进化"
            })

        self.optimization_suggestions = suggestions
        return suggestions

    def predict_evolution_directions(self) -> List[Dict[str, Any]]:
        """预测进化方向"""
        if not self.patterns:
            self.analyze_evolution_patterns()

        directions = []

        # 基于当前能力缺口预测
        capability_gaps_path = REFERENCES_DIR / "capability_gaps.md"
        gaps_analyzed = False

        if capability_gaps_path.exists():
            try:
                with open(capability_gaps_path, 'r', encoding='utf-8') as f:
                    gaps_content = f.read()
                    if "已覆盖" not in gaps_content or "—" not in gaps_content:
                        directions.append({
                            "direction": "能力补全",
                            "confidence": 0.7,
                            "rationale": "根据能力缺口分析，存在待完善的能力方向"
                        })
                        gaps_analyzed = True
            except:
                pass

        # 基于进化趋势预测
        if self.patterns.get("efficiency_trend"):
            directions.append({
                "direction": "效率优化",
                "confidence": 0.8,
                "rationale": "基于效率趋势分析，优化执行效率将是高价值方向"
            })

        # 基于类别分布预测
        category_dist = self.patterns.get("category_distribution", {})
        if category_dist:
            # 找出最少的类别，作为潜在发展方向
            min_category = min(category_dist.items(), key=lambda x: x[1])
            if min_category[1] < self.patterns["total_rounds"] * 0.1:
                directions.append({
                    "direction": f"{min_category[0]}增强",
                    "confidence": 0.6,
                    "rationale": f"当前{min_category[0]}类进化较少，有发展空间"
                })

        # 通用方向预测
        directions.extend([
            {
                "direction": "元进化自省深化",
                "confidence": 0.85,
                "rationale": "600+轮进化积累了丰富的元数据，具备深度自省条件"
            },
            {
                "direction": "创新驱动增强",
                "confidence": 0.75,
                "rationale": "系统越成熟，越需要创新来突破瓶颈"
            },
            {
                "direction": "价值实现追踪",
                "confidence": 0.7,
                "rationale": "价值导向是进化的核心驱动力"
            }
        ])

        # 按置信度排序
        directions.sort(key=lambda x: x.get("confidence", 0), reverse=True)

        self.predicted_directions = directions
        return directions

    def run_full_analysis(self) -> Dict[str, Any]:
        """运行完整分析"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "version": self.VERSION,
            "patterns": self.analyze_evolution_patterns(),
            "optimization_opportunities": self.discover_optimization_opportunities(),
            "optimization_suggestions": self.generate_optimization_suggestions(),
            "predicted_directions": self.predict_evolution_directions()
        }

        return result

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱数据"""
        if not self.efficiency_metrics:
            self.discover_optimization_opportunities()

        return {
            "optimization_score": self.efficiency_metrics.get("optimization_score", 0),
            "total_rounds": self.patterns.get("total_rounds", 0),
            "completed_rounds": self.patterns.get("completed_rounds", 0),
            "completion_rate": round(
                self.patterns["completed_rounds"] / self.patterns["total_rounds"]
                if self.patterns["total_rounds"] > 0 else 0,
                3
            ),
            "categories": self.patterns.get("category_distribution", {}),
            "top_suggestions": [
                s["description"] for s in self.optimization_suggestions[:3]
            ] if self.optimization_suggestions else [],
            "predicted_directions": [
                d["direction"] for d in self.predicted_directions[:3]
            ] if self.predicted_directions else []
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="元进化方法论自省与递归优化引擎"
    )
    parser.add_argument("--version", action="store_true", help="显示版本号")
    parser.add_argument("--status", action="store_true", help="显示当前状态")
    parser.add_argument("--analyze", action="store_true", help="运行完整分析")
    parser.add_argument("--patterns", action="store_true", help="分析进化模式")
    parser.add_argument("--optimize", action="store_true", help="发现优化空间")
    parser.add_argument("--suggest", action="store_true", help="生成优化建议")
    parser.add_argument("--predict", action="store_true", help="预测进化方向")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")

    args = parser.parse_args()

    optimizer = MetaMethodologySelfReflectionOptimizer()

    if args.version:
        print(f"元进化方法论自省与递归优化引擎 v{optimizer.VERSION}")
        return

    if args.status:
        optimizer.load_evolution_history()
        patterns = optimizer.analyze_evolution_patterns()
        print(f"总进化轮次: {patterns['total_rounds']}")
        print(f"完成轮次: {patterns['completed_rounds']}")
        print(f"失败轮次: {patterns['failed_rounds']}")
        print(f"完成率: {patterns['completed_rounds']/patterns['total_rounds']*100:.1f}%" if patterns['total_rounds'] > 0 else "N/A")
        return

    if args.patterns:
        optimizer.load_evolution_history()
        result = optimizer.analyze_evolution_patterns()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.optimize:
        optimizer.load_evolution_history()
        result = optimizer.discover_optimization_opportunities()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.suggest:
        optimizer.load_evolution_history()
        result = optimizer.generate_optimization_suggestions()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.predict:
        optimizer.load_evolution_history()
        result = optimizer.predict_evolution_directions()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.cockpit_data:
        optimizer.load_evolution_history()
        result = optimizer.get_cockpit_data()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.analyze:
        result = optimizer.run_full_analysis()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 默认显示状态
    print(f"元进化方法论自省与递归优化引擎 v{optimizer.VERSION}")
    print("使用 --help 查看可用选项")


if __name__ == "__main__":
    main()