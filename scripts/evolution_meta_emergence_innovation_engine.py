#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环元进化主动创新涌现引擎

在 round 599 完成的元进化智慧自动提取与战略规划引擎基础上，
构建让系统能够基于智慧库主动发现创新机会、生成高价值创新假设、
评估可行性并转化为进化任务的完整能力。

系统不仅能从进化历史中提取智慧，还能主动利用这些智慧发现"人类没想到但很有用"
的创新机会，形成「智慧→创新发现→假设生成→可行性评估→任务转化」的完整闭环。

让系统真正具备「主动创新涌现」的能力，实现从「被动执行」到「主动创造」的范式升级。

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
REFERENCES_DIR = PROJECT_ROOT / "references"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"


class MetaEmergenceInnovationEngine:
    """元进化主动创新涌现引擎"""

    def __init__(self):
        self.name = "元进化主动创新涌现引擎"
        self.version = "1.0.0"
        self.state_dir = STATE_DIR
        self.logs_dir = LOGS_DIR
        self.innovation_file = self.state_dir / "meta_emergence_innovation_data.json"
        self.wisdom_library_file = self.state_dir / "wisdom_library.json"
        self.ideas_file = self.state_dir / "emergence_ideas.json"

    def load_wisdom_library(self):
        """加载智慧库数据"""
        if not self.wisdom_library_file.exists():
            return {
                "wisdom_items": [],
                "success_patterns": {},
                "failure_lessons": [],
                "strategic_insights": []
            }

        try:
            with open(self.wisdom_library_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load wisdom library: {e}")
            return {
                "wisdom_items": [],
                "success_patterns": {},
                "failure_lessons": [],
                "strategic_insights": []
            }

    def load_capabilities(self):
        """加载当前能力列表"""
        capabilities_file = REFERENCES_DIR / "capabilities.md"
        if not capabilities_file.exists():
            return []

        try:
            with open(capabilities_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 简单解析能力列表
                capabilities = []
                lines = content.split('\n')
                for line in lines:
                    # 检测能力项（简单规则：| 开头或 - 开头）
                    if line.strip().startswith('|') and '已覆盖' in line:
                        parts = line.split('|')
                        if len(parts) >= 3:
                            capability = parts[2].strip()
                            if capability and capability != '现状':
                                capabilities.append(capability)
                return capabilities
        except Exception as e:
            print(f"Warning: Failed to load capabilities: {e}")
            return []

    def load_recent_evolution_history(self, limit=20):
        """加载最近的进化历史"""
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

    def discover_innovation_opportunities(self):
        """
        发现创新机会
        基于智慧库、当前能力、最近进化历史分析潜在创新点
        """
        wisdom = self.load_wisdom_library()
        capabilities = self.load_capabilities()
        history = self.load_recent_evolution_history()

        opportunities = []

        # 分析智慧库中的战略性洞察
        strategic_insights = wisdom.get("strategic_insights", [])
        for insight in strategic_insights:
            opportunities.append({
                "type": "智慧驱动",
                "description": f"基于智慧库洞察: {insight.get('insight', 'Unknown')}",
                "potential": insight.get("value_score", 0.7),
                "source": "wisdom_library"
            })

        # 分析成功模式找创新机会
        success_patterns = wisdom.get("success_patterns", {})
        for pattern, data in success_patterns.items():
            if data.get("success_rate", 0) > 0.8:
                opportunities.append({
                    "type": "成功模式扩展",
                    "description": f"扩展高成功率的 {pattern} 模式到新领域",
                    "potential": 0.8,
                    "source": "success_patterns"
                })

        # 分析最近进化发现能力缺口
        recent_goals = [h.get("current_goal", "") for h in history[:10]]
        for goal in recent_goals:
            if "自动化" in goal or "自动" in goal:
                opportunities.append({
                    "type": "自动化深化",
                    "description": f"深化 {goal[:30]}... 的自动化程度",
                    "potential": 0.75,
                    "source": "recent_evolution"
                })

        # 基于能力组合发现创新
        if len(capabilities) >= 5:
            opportunities.append({
                "type": "能力组合创新",
                "description": f"探索 {len(capabilities)} 种现有能力的新组合方式",
                "potential": 0.85,
                "source": "capability_fusion"
            })

        # 分析失败教训找改进机会
        failure_lessons = wisdom.get("failure_lessons", [])
        for lesson in failure_lessons[-5:]:
            opportunities.append({
                "type": "教训驱动改进",
                "description": f"解决历史问题: {lesson.get('lesson', 'Unknown')[:40]}",
                "potential": 0.7,
                "source": "failure_lessons"
            })

        # 排序并返回
        opportunities.sort(key=lambda x: x.get("potential", 0), reverse=True)
        return opportunities[:10]  # 返回前10个机会

    def generate_innovation_hypotheses(self, opportunities):
        """
        生成创新假设
        基于发现的机会生成可验证的创新假设
        """
        hypotheses = []

        for opp in opportunities:
            # 为每个机会生成一个创新假设
            hypothesis = {
                "id": f"hyp_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(hypotheses)}",
                "opportunity_type": opp.get("type", "未知"),
                "description": f"创新假设: {opp.get('description', '')}",
                "expected_value": opp.get("potential", 0.5),
                "feasibility": self._estimate_feasibility(opp),
                "risk_level": self._estimate_risk(opp),
                "status": "generated",
                "created_at": datetime.now().isoformat()
            }
            hypotheses.append(hypothesis)

        return hypotheses

    def _estimate_feasibility(self, opportunity):
        """评估机会的可行性"""
        # 简化评估：基于类型和来源
        type_scores = {
            "智慧驱动": 0.8,
            "成功模式扩展": 0.9,
            "能力组合创新": 0.7,
            "自动化深化": 0.85,
            "教训驱动改进": 0.75
        }
        return type_scores.get(opportunity.get("type", ""), 0.6)

    def _estimate_risk(self, opportunity):
        """评估机会的风险"""
        # 简化评估：基于类型
        type_risks = {
            "智慧驱动": "低",
            "成功模式扩展": "低",
            "能力组合创新": "中",
            "自动化深化": "低",
            "教训驱动改进": "中"
        }
        return type_risks.get(opportunity.get("type", ""), "中")

    def evaluate_hypotheses(self, hypotheses):
        """
        评估创新假设
        综合评估假设的价值和可行性，筛选高价值假设
        """
        evaluated = []

        for h in hypotheses:
            # 综合评分 = 期望价值 * 可行性
            score = h.get("expected_value", 0) * h.get("feasibility", 0)

            # 风险惩罚
            if h.get("risk_level") == "高":
                score *= 0.7
            elif h.get("risk_level") == "中":
                score *= 0.9

            h["evaluation_score"] = round(score, 3)
            h["status"] = "evaluated"
            h["evaluated_at"] = datetime.now().isoformat()

            evaluated.append(h)

        # 按评分排序
        evaluated.sort(key=lambda x: x.get("evaluation_score", 0), reverse=True)
        return evaluated

    def transform_to_evolution_tasks(self, hypotheses):
        """
        将高价值假设转化为可执行的进化任务
        """
        tasks = []

        # 筛选高评分假设（>=0.5）
        high_value = [h for h in hypotheses if h.get("evaluation_score", 0) >= 0.5]

        for h in high_value:
            task = {
                "task_id": f"task_{h.get('id', '')}",
                "hypothesis_id": h.get("id", ""),
                "description": h.get("description", ""),
                "expected_value": h.get("expected_value", 0),
                "feasibility": h.get("feasibility", 0),
                "evaluation_score": h.get("evaluation_score", 0),
                "status": "ready_to_execute",
                "created_at": datetime.now().isoformat()
            }
            tasks.append(task)

        return tasks

    def run_emergence_cycle(self):
        """
        执行完整的主动创新涌现循环
        1. 发现创新机会
        2. 生成创新假设
        3. 评估假设价值
        4. 转化为进化任务
        """
        # 步骤1: 发现创新机会
        opportunities = self.discover_innovation_opportunities()

        # 步骤2: 生成创新假设
        hypotheses = self.generate_innovation_hypotheses(opportunities)

        # 步骤3: 评估假设
        evaluated = self.evaluate_hypotheses(hypotheses)

        # 步骤4: 转化为任务
        tasks = self.transform_to_evolution_tasks(evaluated)

        # 保存结果
        result = {
            "opportunities": opportunities,
            "hypotheses": hypotheses,
            "evaluated_hypotheses": evaluated,
            "tasks": tasks,
            "summary": {
                "opportunities_found": len(opportunities),
                "hypotheses_generated": len(hypotheses),
                "high_value_hypotheses": len(evaluated),
                "tasks_created": len(tasks)
            }
        }

        # 保存到文件
        with open(self.innovation_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        # 保存假设到 ideas 文件
        ideas_data = {
            "hypotheses": hypotheses,
            "tasks": tasks,
            "last_updated": datetime.now().isoformat()
        }
        with open(self.ideas_file, 'w', encoding='utf-8') as f:
            json.dump(ideas_data, f, ensure_ascii=False, indent=2)

        return result

    def get_cockpit_data(self):
        """获取驾驶舱数据"""
        # 加载历史数据
        data = {
            "engine_name": self.name,
            "version": self.version,
            "last_run": datetime.now().isoformat()
        }

        if self.innovation_file.exists():
            try:
                with open(self.innovation_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    data["last_summary"] = history.get("summary", {})
                    data["last_opportunities"] = len(history.get("opportunities", []))
                    data["last_tasks_created"] = len(history.get("tasks", []))
            except:
                pass

        # 添加与智慧库的集成状态
        wisdom = self.load_wisdom_library()
        data["wisdom_library_status"] = "connected" if wisdom.get("wisdom_items") else "empty"
        data["wisdom_items_count"] = len(wisdom.get("wisdom_items", []))

        return data

    def get_status(self):
        """获取引擎状态"""
        data = self.get_cockpit_data()
        return {
            "name": self.name,
            "version": self.version,
            "status": "ready",
            "wisdom_items": data.get("wisdom_items_count", 0),
            "last_run": data.get("last_run", "never"),
            "last_opportunities": data.get("last_opportunities", 0),
            "last_tasks_created": data.get("last_tasks_created", 0)
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能全场景进化环元进化主动创新涌现引擎"
    )
    parser.add_argument('--version', action='store_true', help='显示版本信息')
    parser.add_argument('--status', action='store_true', help='获取引擎状态')
    parser.add_argument('--run', action='store_true', help='运行完整创新涌现循环')
    parser.add_argument('--discover', action='store_true', help='只发现创新机会')
    parser.add_argument('--generate', action='store_true', help='只生成创新假设')
    parser.add_argument('--evaluate', action='store_true', help='只评估创新假设')
    parser.add_argument('--cockpit-data', action='store_true', help='获取驾驶舱数据')

    args = parser.parse_args()

    engine = MetaEmergenceInnovationEngine()

    if args.version:
        print(f"{engine.name} v{engine.version}")
        print("在 round 599 完成的智慧提取引擎基础上，构建主动创新涌现能力")
        return

    if args.status:
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return

    if args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    if args.run or args.discover or args.generate or args.evaluate:
        result = engine.run_emergence_cycle()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 默认显示帮助
    parser.print_help()


if __name__ == "__main__":
    main()