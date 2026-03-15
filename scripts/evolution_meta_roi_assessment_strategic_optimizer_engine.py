"""
元进化投资回报智能评估与战略优化引擎
让系统能够深度分析 600+ 轮进化的投资回报率，识别哪些引擎/能力组合产生了最大价值，
发现进化过程中的隐藏模式（低效投资、重复建设等），为未来的进化资源分配提供智能决策支持，
生成战略优化建议。

基于 round 625 记忆深度整合、round 606/644 方法论自省、round 560/578/609 价值预测等能力，
构建进化投资回报的量化评估与战略优化闭环。

版本: 1.0.0
"""

import os
import json
import glob
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict


class EvolutionROIAssessmentEngine:
    """进化投资回报智能评估与战略优化引擎"""

    def __init__(self, project_root: str = None):
        if project_root is None:
            self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        else:
            self.project_root = project_root

        self.runtime_state_dir = os.path.join(self.project_root, "runtime", "state")
        self.runtime_logs_dir = os.path.join(self.project_root, "runtime", "logs")
        self.evolutions_completed_dir = self.runtime_state_dir

        # 引擎元信息
        self.engine_name = "元进化投资回报智能评估与战略优化引擎"
        self.version = "1.0.0"
        self.round = 654

    def load_evolution_history(self) -> List[Dict[str, Any]]:
        """加载进化历史数据"""
        evolutions = []

        # 读取 evolution_completed_*.json 文件
        completed_files = glob.glob(
            os.path.join(self.evolutions_completed_dir, "evolution_completed_*.json")
        )

        for filepath in completed_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'round' in data:
                        evolutions.append(data)
                    elif isinstance(data, list):
                        evolutions.extend([e for e in data if isinstance(e, dict) and 'round' in e])
            except Exception as e:
                print(f"Warning: Failed to load {filepath}: {e}")

        # 按 round 排序
        evolutions.sort(key=lambda x: x.get('round', 0))
        return evolutions

    def load_recent_logs(self) -> List[Dict[str, Any]]:
        """加载最近日志"""
        recent_logs_path = os.path.join(self.runtime_state_dir, "recent_logs.json")
        if os.path.exists(recent_logs_path):
            try:
                with open(recent_logs_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('entries', [])
            except Exception:
                pass
        return []

    def assess_roi(self, evolutions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """评估进化投资回报率"""
        if not evolutions:
            return {
                "total_evolutions": 0,
                "roi_analysis": "No evolution data available",
                "value_contributions": [],
                "inefficiency_patterns": [],
                "strategic_recommendations": []
            }

        # 基础统计
        total_rounds = len(evolutions)
        completed_rounds = sum(1 for e in evolutions if e.get('status') in ['completed', '已完成', 'pass'])
        completion_rate = completed_rounds / total_rounds if total_rounds > 0 else 0

        # 分析每轮的价值贡献
        value_by_category = defaultdict(lambda: {"count": 0, "total_value": 0, "rounds": []})

        for evo in evolutions:
            goal = evo.get('current_goal', evo.get('goal', ''))
            status = evo.get('status', evo.get('is_completed', ''))
            round_num = evo.get('round', 0)

            # 分类统计
            if '价值' in goal or '投资' in goal or '优化' in goal:
                category = "价值优化类"
            elif '创新' in goal or '涌现' in goal or '发现' in goal:
                category = "创新驱动类"
            elif '健康' in goal or '诊断' in goal or '自愈' in goal:
                category = "健康保障类"
            elif '执行' in goal or '自动化' in goal or '闭环' in goal:
                category = "执行效率类"
            elif '知识' in goal or '记忆' in goal or '学习' in goal:
                category = "知识学习类"
            elif '决策' in goal or '策略' in goal or '规划' in goal:
                category = "决策策略类"
            else:
                category = "其他类"

            value_by_category[category]["count"] += 1
            value_by_category[category]["rounds"].append(round_num)

            # 为完成的轮次分配更高价值
            if status in ['completed', '已完成', 'pass']:
                value_by_category[category]["total_value"] += 1.0
            else:
                value_by_category[category]["total_value"] += 0.5

        # 计算各类别的 ROI
        value_contributions = []
        for category, data in value_by_category.items():
            avg_value = data["total_value"] / data["count"] if data["count"] > 0 else 0
            value_contributions.append({
                "category": category,
                "count": data["count"],
                "total_value": data["total_value"],
                "average_value": round(avg_value, 3),
                "rounds": sorted(data["rounds"])
            })

        # 按价值排序
        value_contributions.sort(key=lambda x: x["total_value"], reverse=True)

        # 识别低效模式
        inefficiency_patterns = self._identify_inefficiency_patterns(evolutions)

        # 生成战略建议
        strategic_recommendations = self._generate_strategic_recommendations(
            evolutions, value_contributions, inefficiency_patterns
        )

        return {
            "total_evolutions": total_rounds,
            "completed_evolutions": completed_rounds,
            "completion_rate": round(completion_rate, 3),
            "value_contributions": value_contributions,
            "inefficiency_patterns": inefficiency_patterns,
            "strategic_recommendations": strategic_recommendations,
            "highest_value_categories": [vc["category"] for vc in value_contributions[:3]],
            "roi_summary": self._generate_roi_summary(value_contributions, completion_rate)
        }

    def _identify_inefficiency_patterns(self, evolutions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """识别低效模式"""
        patterns = []

        # 检查重复进化
        goal_keywords = defaultdict(list)
        for evo in evolutions:
            goal = evo.get('current_goal', evo.get('goal', ''))
            round_num = evo.get('round', 0)

            # 提取关键词
            for keyword in ['引擎', '优化', '增强', '闭环', '学习', '创新', '价值']:
                if keyword in goal:
                    goal_keywords[keyword].append({"round": round_num, "goal": goal[:50]})

        # 检测重复模式
        for keyword, items in goal_keywords.items():
            if len(items) > 10:  # 超过10轮包含相同关键词
                rounds = [item["round"] for item in items]
                avg_gap = (max(rounds) - min(rounds)) / len(rounds) if len(rounds) > 1 else 0
                if avg_gap < 5:  # 平均间隔小于5轮
                    patterns.append({
                        "type": "重复进化",
                        "keyword": keyword,
                        "occurrences": len(items),
                        "description": f"关键词'{keyword}'在{len(items)}轮中重复出现，可能存在重复建设",
                        "recommendation": f"考虑合并或减少'{keyword}'相关进化，聚焦差异化创新"
                    })

        # 检查失败/未完成
        failed_rounds = [e.get('round', 0) for e in evolutions
                        if e.get('status') not in ['completed', '已完成', 'pass']]
        current_total_rounds = len(evolutions)
        if len(failed_rounds) > current_total_rounds * 0.2:  # 失败率超过20%
            patterns.append({
                "type": "高失败率",
                "failed_count": len(failed_rounds),
                "description": f"失败/未完成轮次占比超过20%，需要提升进化执行质量",
                "recommendation": "加强执行前的验证和规划，提升进化执行的成功率"
            })

        return patterns

    def _generate_strategic_recommendations(
        self,
        evolutions: List[Dict[str, Any]],
        value_contributions: List[Dict[str, Any]],
        inefficiency_patterns: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """生成战略优化建议"""
        recommendations = []

        # 基于价值贡献的建议
        if value_contributions:
            top_category = value_contributions[0]
            recommendations.append({
                "priority": "high",
                "category": "资源分配",
                "title": f"加大{top_category['category']}投资",
                "description": f"该类别已有{top_category['count']}轮进化，贡献价值{top_category['total_value']}，是投资回报最高的领域",
                "action": f"在下一阶段优先投资{top_category['category']}相关能力"
            })

            # 找出投资不足的领域
            if len(value_contributions) > 3:
                low_category = value_contributions[-1]
                if low_category['count'] < 5:
                    recommendations.append({
                        "priority": "medium",
                        "category": "能力补齐",
                        "title": f"关注{low_category['category']}",
                        "description": f"该类别进化较少({low_category['count']}轮)，可能是被忽视的价值洼地",
                        "action": f"探索{low_category['category']}的潜在价值"
                    })

        # 基于低效模式的建议
        for pattern in inefficiency_patterns[:2]:  # 最多2条
            recommendations.append({
                "priority": "high" if pattern.get("type") == "高失败率" else "medium",
                "category": "效率提升",
                "title": f"解决{pattern['type']}问题",
                "description": pattern.get("description", ""),
                "action": pattern.get("recommendation", "")
            })

        # 基于轮次历史的建议
        total_rounds = len(evolutions)
        if total_rounds > 500:
            recommendations.append({
                "priority": "medium",
                "category": "知识传承",
                "title": "强化进化知识传承",
                "description": f"系统已完成{total_rounds}轮进化，积累了大量经验",
                "action": "建立更完善的进化知识传承机制，避免重复踩坑"
            })

        return recommendations

    def _generate_roi_summary(
        self,
        value_contributions: List[Dict[str, Any]],
        completion_rate: float
    ) -> str:
        """生成 ROI 总结"""
        if not value_contributions:
            return "数据不足，无法生成 ROI 总结"

        total_value = sum(vc["total_value"] for vc in value_contributions)
        top3_value = sum(vc["total_value"] for vc in value_contributions[:3])

        summary = f"""进化投资回报分析:
- 总进化轮次: {len(value_contributions[0].get('rounds', [])) if value_contributions else 0}+
- 完成率: {completion_rate*100:.1f}%
- 总价值贡献: {total_value:.1f}
- Top 3 类别价值占比: {top3_value/total_value*100:.1f}% (聚焦效应)
- 最高价值类别: {value_contributions[0]['category'] if value_contributions else 'N/A'}"""

        return summary

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱数据"""
        evolutions = self.load_evolution_history()
        roi_data = self.assess_roi(evolutions)

        return {
            "engine_name": self.engine_name,
            "version": self.version,
            "round": self.round,
            "data": roi_data,
            "timestamp": datetime.now().isoformat()
        }


def main():
    """主入口"""
    engine = EvolutionROIAssessmentEngine()

    import argparse
    parser = argparse.ArgumentParser(description=engine.engine_name)
    parser.add_argument('--version', action='store_true', help='显示版本信息')
    parser.add_argument('--assess-roi', action='store_true', help='执行 ROI 评估')
    parser.add_argument('--cockpit-data', action='store_true', help='获取驾驶舱数据')
    parser.add_argument('--recommendations', action='store_true', help='生成战略建议')
    parser.add_argument('--json', action='store_true', help='JSON 格式输出')

    args = parser.parse_args()

    if args.version:
        print(f"{engine.engine_name} v{engine.version}")
        print(f"Round: {engine.round}")
        return

    if args.cockpit_data:
        data = engine.get_cockpit_data()
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(f"=== {data['engine_name']} ===")
            print(f"版本: {data['version']}")
            print(f"轮次: {data['round']}")
            print(f"\nROI 摘要:")
            roi = data['data']
            print(roi.get('roi_summary', 'N/A'))
            print(f"\n高价值类别: {roi.get('highest_value_categories', [])}")
            print(f"\n战略建议数量: {len(roi.get('strategic_recommendations', []))}")
        return

    if args.assess_roi or args.recommendations:
        evolutions = engine.load_evolution_history()
        roi_data = engine.assess_roi(evolutions)

        if args.json:
            print(json.dumps(roi_data, ensure_ascii=False, indent=2))
        else:
            print(f"=== 进化投资回报评估 ===")
            print(f"总进化轮次: {roi_data['total_evolutions']}")
            print(f"完成率: {roi_data['completion_rate']*100:.1f}%")

            print(f"\n--- 价值贡献排名 ---")
            for i, vc in enumerate(roi_data['value_contributions'][:5], 1):
                print(f"{i}. {vc['category']}: {vc['count']}轮, 价值{vc['total_value']:.1f}")

            print(f"\n--- 战略建议 ---")
            for rec in roi_data['strategic_recommendations'][:3]:
                print(f"[{rec['priority'].upper()}] {rec['title']}")
                print(f"  {rec['description']}")
                print(f"  → {rec['action']}\n")

        return

    # 默认显示版本
    print(f"{engine.engine_name} v{engine.version}")
    print(f"使用 --assess-roi 执行 ROI 评估")
    print(f"使用 --cockpit-data 获取驾驶舱数据")
    print(f"使用 --recommendations 生成战略建议")


if __name__ == "__main__":
    main()