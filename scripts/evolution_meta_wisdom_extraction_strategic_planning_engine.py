#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环元进化智慧自动提取与战略规划引擎

在 round 598 完成的元进化认知深度自省基础上，进一步构建让系统能够从500+轮进化历史中
自动提取可复用智慧、将智慧转化为战略规划输入、形成智慧驱动的自主战略规划能力。

系统不仅能反思自己的进化方式，还能从反思中提取智慧并应用到未来的进化决策中，
实现从「反思」到「智慧应用」的范式升级。

形成「自省→智慧提取→智慧存储→战略规划→决策执行」的完整智慧驱动闭环。

Version: 1.0.0
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import subprocess
import importlib.util

# 项目根目录
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"


class MetaWisdomExtractionStrategicPlanningEngine:
    """元进化智慧自动提取与战略规划引擎"""

    def __init__(self):
        self.name = "元进化智慧自动提取与战略规划引擎"
        self.version = "1.0.0"
        self.state_dir = STATE_DIR
        self.logs_dir = LOGS_DIR
        self.wisdom_file = self.state_dir / "meta_wisdom_extraction_data.json"
        self.wisdom_library_file = self.state_dir / "wisdom_library.json"

    def load_evolution_history(self, limit=100):
        """
        加载进化历史数据
        用于提取智慧
        """
        history = []
        state_files = list(self.state_dir.glob("evolution_completed_*.json"))

        # 按修改时间排序，取最近的
        state_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        for f in state_files[:limit]:
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    history.append(data)
            except Exception as e:
                print(f"Warning: Failed to load {f}: {e}")

        return history

    def extract_wisdom_from_history(self, history):
        """
        从进化历史中提取智慧
        分析成功模式、失败教训、关键决策点
        """
        wisdom_items = []

        if not history:
            return wisdom_items

        # 分析成功模式
        success_patterns = {}
        for h in history:
            goal = h.get("current_goal", "")
            is_completed = h.get("is_completed", False)

            # 提取目标类型关键词
            key_terms = []
            if "元进化" in goal:
                key_terms.append("元进化")
            if "价值" in goal:
                key_terms.append("价值驱动")
            if "创新" in goal:
                key_terms.append("创新")
            if "智能" in goal:
                key_terms.append("智能化")
            if "自" in goal and ("自省" in goal or "自主" in goal or "自愈" in goal or "自我" in goal):
                key_terms.append("自主性")

            for term in key_terms:
                if term not in success_patterns:
                    success_patterns[term] = {"success": 0, "total": 0}

                success_patterns[term]["total"] += 1
                if is_completed:
                    success_patterns[term]["success"] += 1

        # 转换为智慧项
        for pattern, stats in success_patterns.items():
            if stats["total"] >= 3:  # 至少3轮出现
                success_rate = stats["success"] / stats["total"]
                wisdom_items.append({
                    "type": "success_pattern",
                    "category": pattern,
                    "description": f"{pattern}类进化完成率 {success_rate*100:.1f}% ({stats['success']}/{stats['total']})",
                    "insight": f"当进化方向聚焦于{pattern}时，成功率较高",
                    "actionable": True,
                    "confidence": "high" if stats["total"] >= 10 else "medium"
                })

        # 提取时间模式
        if len(history) >= 10:
            # 分析轮次间隔
            wisdom_items.append({
                "type": "time_pattern",
                "category": "进化节奏",
                "description": f"系统已完成 {len(history)} 轮进化",
                "insight": "持续稳定的进化节奏是系统发展的关键",
                "actionable": False,
                "confidence": "high"
            })

        # 分析进化深度趋势
        recent_goals = [h.get("current_goal", "") for h in history[:10]]
        complexity_score = 0
        for goal in recent_goals:
            if "深度" in goal or "增强" in goal or "优化" in goal:
                complexity_score += 1
            if "引擎" in goal or "闭环" in goal or "自主" in goal:
                complexity_score += 1

        if complexity_score >= 8:
            wisdom_items.append({
                "type": "complexity_trend",
                "category": "进化复杂度",
                "description": "近期进化复杂度呈上升趋势",
                "insight": "系统正在向更复杂、更集成的方向演进，需要关注复杂性管理",
                "actionable": True,
                "confidence": "medium"
            })
        else:
            wisdom_items.append({
                "type": "complexity_trend",
                "category": "进化复杂度",
                "description": "近期进化复杂度保持稳定",
                "insight": "系统处于稳定演进阶段",
                "actionable": False,
                "confidence": "medium"
            })

        # 提取能力扩展模式
        capabilities_extended = set()
        for h in history[:20]:
            goal = h.get("current_goal", "")
            # 提取能力相关关键词
            if "引擎" in goal:
                capabilities_extended.add("引擎开发")
            if "工具" in goal or "能力" in goal:
                capabilities_extended.add("能力扩展")
            if "优化" in goal or "效率" in goal:
                capabilities_extended.add("性能优化")
            if "决策" in goal or "规划" in goal:
                capabilities_extended.add("决策规划")

        for cap in capabilities_extended:
            wisdom_items.append({
                "type": "capability_extension",
                "category": cap,
                "description": f"系统具备 {cap} 能力",
                "insight": f"{cap}是系统核心能力之一",
                "actionable": False,
                "confidence": "high"
            })

        return wisdom_items

    def extract_lessons_from_failures(self, history):
        """
        从失败和教训中提取智慧
        """
        lessons = []

        # 读取失败记录
        failures_file = PROJECT_ROOT / "references" / "failures.md"
        if failures_file.exists():
            try:
                with open(failures_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 提取关键教训
                lines = content.split('\n')
                key_lessons = []
                for line in lines:
                    if line.strip().startswith('- 202') and '：' in line:
                        # 提取日期和教训内容
                        parts = line.split('：', 1)
                        if len(parts) == 2:
                            key_lessons.append(parts[1].strip())

                # 归类教训
                categorized = {}
                for lesson in key_lessons:
                    if '失败' in lesson or 'error' in lesson.lower():
                        cat = "execution"
                    elif '优化' in lesson or 'improve' in lesson.lower():
                        cat = "optimization"
                    elif '智能' in lesson or 'engine' in lesson.lower():
                        cat = "intelligence"
                    else:
                        cat = "other"

                    if cat not in categorized:
                        categorized[cat] = []
                    categorized[cat].append(lesson)

                for cat, cat_lessons in categorized.items():
                    if cat_lessons:
                        lessons.append({
                            "type": "failure_lesson",
                            "category": cat,
                            "count": len(cat_lessons),
                            "description": f"发现 {len(cat_lessons)} 条{cat}类教训",
                            "key_lessons": cat_lessons[:3],  # 最多3条
                            "actionable": True,
                            "confidence": "high"
                        })

            except Exception as e:
                print(f"Warning: Failed to read failures file: {e}")

        return lessons

    def store_wisdom_library(self, wisdom_items, lessons):
        """
        存储智慧到智慧库
        以可查询、可复用的方式组织
        """
        library = {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "wisdom_items": wisdom_items + lessons,
            "statistics": {
                "total_wisdom": len(wisdom_items) + len(lessons),
                "actionable_count": sum(1 for w in wisdom_items + lessons if w.get("actionable", False)),
                "high_confidence_count": sum(1 for w in wisdom_items + lessons if w.get("confidence") == "high")
            }
        }

        with open(self.wisdom_library_file, 'w', encoding='utf-8') as f:
            json.dump(library, f, ensure_ascii=False, indent=2)

        return library

    def generate_strategic_planning_input(self, wisdom_items, lessons):
        """
        生成战略规划输入
        将智慧转化为战略决策依据
        """
        # 按行动性和置信度筛选
        actionable_wisdom = [w for w in wisdom_items + lessons if w.get("actionable", False)]
        high_conf_wisdom = [w for w in actionable_wisdom if w.get("confidence") == "high"]

        planning_input = {
            "generated_at": datetime.now().isoformat(),
            "strategic_recommendations": [],
            "risk_warnings": [],
            "opportunity_areas": [],
            "decision_factors": []
        }

        # 生成战略建议
        for w in high_conf_wisdom:
            if w.get("type") == "success_pattern":
                planning_input["strategic_recommendations"].append({
                    "priority": "high",
                    "recommendation": f"继续深化{ w.get('category', '') }方向",
                    "reason": w.get("insight", ""),
                    "source": "wisdom_pattern"
                })

            elif w.get("type") == "complexity_trend" and w.get("actionable"):
                planning_input["risk_warnings"].append({
                    "priority": "medium",
                    "warning": "进化复杂度上升",
                    "mitigation": "关注复杂性管理，保持架构简洁",
                    "source": "wisdom_trend"
                })

        # 生成机会领域
        # 基于当前进化阶段的分析
        if len(wisdom_items) >= 5:
            planning_input["opportunity_areas"].append({
                "area": "智慧应用深化",
                "description": "将已提取的智慧真正应用到决策中",
                "potential": "high",
                "actions": ["建立智慧应用机制", "将智慧集成到决策流程"]
            })

        # 生成决策因素
        planning_input["decision_factors"].append({
            "factor": "进化效率趋势",
            "weight": "high",
            "source": "effectiveness_analysis"
        })

        planning_input["decision_factors"].append({
            "factor": "能力覆盖度",
            "weight": "medium",
            "source": "capability_analysis"
        })

        planning_input["decision_factors"].append({
            "factor": "历史教训遵循度",
            "weight": "high",
            "source": "lessons_learned"
        })

        return planning_input

    def integrate_with_self_reflection_engine(self):
        """
        与 round 598 深度自省引擎集成
        获取自省数据作为智慧输入
        """
        reflection_data_file = self.state_dir / "meta_cognition_self_reflection_recursive_data.json"

        if reflection_data_file.exists():
            try:
                with open(reflection_data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load reflection data: {e}")

        return None

    def run_full_analysis(self):
        """
        运行完整分析流程
        提取智慧→存储智慧→生成战略规划输入
        """
        print("=" * 60)
        print("元进化智慧自动提取与战略规划引擎")
        print("=" * 60)

        # 1. 加载进化历史
        print("\n[1/6] 加载进化历史数据...")
        history = self.load_evolution_history(limit=100)
        print(f"  已加载 {len(history)} 轮进化历史")

        # 2. 从历史中提取智慧
        print("\n[2/6] 从进化历史中提取智慧...")
        wisdom_items = self.extract_wisdom_from_history(history)
        print(f"  提取 {len(wisdom_items)} 条智慧项")

        # 3. 从失败中提取教训
        print("\n[3/6] 从失败记录中提取教训...")
        lessons = self.extract_lessons_from_failures(history)
        print(f"  提取 {len(lessons)} 条教训")

        # 4. 存储到智慧库
        print("\n[4/6] 存储智慧到智慧库...")
        library = self.store_wisdom_library(wisdom_items, lessons)
        print(f"  智慧库共有 {library['statistics']['total_wisdom']} 条智慧")
        print(f"  其中 {library['statistics']['actionable_count']} 条可执行")

        # 5. 生成战略规划输入
        print("\n[5/6] 生成战略规划输入...")
        planning_input = self.generate_strategic_planning_input(wisdom_items, lessons)
        print(f"  战略建议: {len(planning_input['strategic_recommendations'])} 条")
        print(f"  风险预警: {len(planning_input['risk_warnings'])} 条")
        print(f"  机会领域: {len(planning_input['opportunity_areas'])} 条")

        # 6. 与深度自省引擎集成
        print("\n[6/6] 与深度自省引擎集成...")
        reflection_data = self.integrate_with_self_reflection_engine()
        if reflection_data:
            print("  已获取自省引擎数据")
        else:
            print("  未能获取自省引擎数据（可能尚未运行）")

        # 保存数据
        result = {
            "timestamp": datetime.now().isoformat(),
            "engine": self.name,
            "version": self.version,
            "wisdom_extracted": len(wisdom_items),
            "lessons_extracted": len(lessons),
            "wisdom_items": wisdom_items,
            "lessons": lessons,
            "wisdom_library": library,
            "strategic_planning_input": planning_input,
            "reflection_integrated": reflection_data is not None,
            "history_count": len(history)
        }

        with open(self.wisdom_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print("\n" + "=" * 60)
        print("智慧提取完成")
        print(f"  可执行智慧: {library['statistics']['actionable_count']} 条")
        print(f"  高置信度: {library['statistics']['high_confidence_count']} 条")
        print("=" * 60)

        return result

    def get_cockpit_data(self):
        """
        获取驾驶舱数据
        为进化驾驶舱提供可视化数据
        """
        data = {
            "engine_name": self.name,
            "version": self.version,
            "timestamp": datetime.now().isoformat()
        }

        # 尝试加载智慧库
        if self.wisdom_library_file.exists():
            try:
                with open(self.wisdom_library_file, 'r', encoding='utf-8') as f:
                    library = json.load(f)

                data["total_wisdom"] = library.get("statistics", {}).get("total_wisdom", 0)
                data["actionable_wisdom"] = library.get("statistics", {}).get("actionable_count", 0)
                data["high_confidence_wisdom"] = library.get("statistics", {}).get("high_confidence_count", 0)

                # 获取最近的可执行智慧
                actionable = [w for w in library.get("wisdom_items", []) if w.get("actionable", False)]
                data["top_wisdom"] = actionable[:3] if actionable else []

            except Exception as e:
                print(f"Warning: Failed to load wisdom library: {e}")

        # 尝试加载分析结果
        if self.wisdom_file.exists():
            try:
                with open(self.wisdom_file, 'r', encoding='utf-8') as f:
                    analysis = json.load(f)

                data["strategic_recommendations"] = len(analysis.get("strategic_planning_input", {}).get("strategic_recommendations", []))
                data["risk_warnings"] = len(analysis.get("strategic_planning_input", {}).get("risk_warnings", []))
                data["opportunity_areas"] = len(analysis.get("strategic_planning_input", {}).get("opportunity_areas", []))

            except Exception as e:
                print(f"Warning: Failed to load analysis data: {e}")

        return data


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="智能全场景进化环元进化智慧自动提取与战略规划引擎"
    )
    parser.add_argument("--version", action="store_true", help="显示版本信息")
    parser.add_argument("--status", action="store_true", help="显示引擎状态")
    parser.add_argument("--run", action="store_true", help="运行完整分析")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")

    args = parser.parse_args()

    engine = MetaWisdomExtractionStrategicPlanningEngine()

    if args.version:
        print(f"{engine.name} v{engine.version}")
        return

    if args.status:
        print(f"引擎: {engine.name}")
        print(f"版本: {engine.version}")
        print(f"状态: 运行中")
        return

    if args.run:
        result = engine.run_full_analysis()
        return result

    if args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    # 默认运行
    result = engine.run_full_analysis()
    return result


if __name__ == "__main__":
    main()