#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能进化创意生成引擎
让系统能够主动发现进化方向，基于能力缺口、历史失败、现有能力组合、用户场景模拟等维度，
主动提出"还有什么可以进化"的创意，实现从"被动等指令"到"主动找事做"的范式升级

功能：
1. 多维度进化机会分析（capability_gaps、failures、capabilities、行为日志、模拟用户思维）
2. 创新进化方向生成（发现新能力、新组合、新场景）
3. 进化创意评估与优先级排序
4. 进化建议输出（推荐最值得做的进化方向）

version: 1.0.0
"""

import os
import json
import glob
import re
from datetime import datetime
from pathlib import Path

# 项目根目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
REFERENCES_DIR = os.path.join(PROJECT_ROOT, "references")
RUNTIME_STATE_DIR = os.path.join(PROJECT_ROOT, "runtime", "state")
RUNTIME_LOGS_DIR = os.path.join(PROJECT_ROOT, "runtime", "logs")


class EvolutionIdeaGenerator:
    """智能进化创意生成引擎"""

    def __init__(self):
        self.references_dir = REFERENCES_DIR
        self.state_dir = RUNTIME_STATE_DIR
        self.logs_dir = RUNTIME_LOGS_DIR
        self.capability_gaps_file = os.path.join(REFERENCES_DIR, "capability_gaps.md")
        self.failures_file = os.path.join(REFERENCES_DIR, "failures.md")
        self.capabilities_file = os.path.join(REFERENCES_DIR, "capabilities.md")
        self.recent_logs_file = os.path.join(RUNTIME_STATE_DIR, "recent_logs.json")

    def analyze_capability_gaps(self):
        """分析能力缺口"""
        gaps = []
        if not os.path.exists(self.capability_gaps_file):
            return gaps

        try:
            with open(self.capability_gaps_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 提取"可行方向"列中非"-"的内容
                lines = content.split('\n')
                for line in lines:
                    if '|' in line:
                        parts = line.split('|')
                        if len(parts) >= 3:
                            direction = parts[-1].strip()
                            if direction and direction != '—' and '已覆盖' not in direction:
                                gaps.append({
                                    "type": "capability_gap",
                                    "description": f"能力缺口: {parts[0].strip()}",
                                    "opportunity": direction,
                                    "source": "capability_gaps.md"
                                })
        except Exception as e:
            print(f"分析能力缺口失败: {e}")

        return gaps

    def analyze_failures(self):
        """分析历史失败，寻找改进机会"""
        opportunities = []
        if not os.path.exists(self.failures_file):
            return opportunities

        try:
            with open(self.failures_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 提取每次失败和教训
                lines = content.split('\n')
                for line in lines:
                    if '失败' in line or '原因' in line or '下次' in line:
                        # 提取日期和问题描述
                        match = re.search(r'(\d{4}-\d{2}-\d{2})[：:](.+)', line)
                        if match:
                            date, desc = match.groups()
                            opportunities.append({
                                "type": "failure_lesson",
                                "description": f"历史失败改进机会: {desc[:100]}",
                                "opportunity": f"从{date}失败中学习，避免类似问题并改进",
                                "source": "failures.md"
                            })
        except Exception as e:
            print(f"分析历史失败失败: {e}")

        return opportunities

    def analyze_existing_capabilities(self):
        """分析现有能力，发现可组合的新场景"""
        combinations = []
        if not os.path.exists(self.capabilities_file):
            return combinations

        try:
            with open(self.capabilities_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 提取能力关键词
                capabilities = []
                lines = content.split('\n')
                for line in lines:
                    # 提取 |xxx| 后面的描述
                    if '|' in line and '脚本' in line:
                        parts = line.split('|')
                        if len(parts) >= 3:
                            desc = parts[-1].strip()
                            if desc and desc != '说明':
                                capabilities.append(desc)

                # 生成能力组合建议
                if len(capabilities) >= 2:
                    # 取前5个能力作为组合候选
                    sample_caps = capabilities[:5]
                    combinations.append({
                        "type": "capability_combination",
                        "description": f"现有{len(capabilities)}种能力可组合创新",
                        "opportunity": "发现能力组合新用法，如多引擎协同自动化",
                        "source": "capabilities.md"
                    })
        except Exception as e:
            print(f"分析现有能力失败: {e}")

        return combinations

    def analyze_recent_behavior(self):
        """分析近期行为日志，发现低频/未覆盖场景"""
        insights = []
        if not os.path.exists(self.recent_logs_file):
            return insights

        try:
            with open(self.recent_logs_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    # 统计行为类型
                    action_types = {}
                    for entry in data:
                        action = entry.get('action', 'unknown')
                        action_types[action] = action_types.get(action, 0) + 1

                    # 找出低频行为（可能是未覆盖的场景）
                    low_freq = [k for k, v in action_types.items() if v <= 1]
                    if low_freq:
                        insights.append({
                            "type": "behavior_gap",
                            "description": f"发现{len(low_freq)}种低频行为",
                            "opportunity": "这些低频行为可能是未覆盖的场景，值得深入分析",
                            "source": "recent_logs.json"
                        })

                    # 统计用户意图
                    intents = {}
                    for entry in data:
                        mission = entry.get('mission', '')
                        if mission:
                            # 提取意图关键词
                            if '帮' in mission or '打开' in mission:
                                intents['task_execution'] = intents.get('task_execution', 0) + 1
                            elif '进化' in mission or 'evolve' in mission.lower():
                                intents['evolution'] = intents.get('evolution', 0) + 1
                            else:
                                intents['other'] = intents.get('other', 0) + 1

                    if intents:
                        insights.append({
                            "type": "intent_pattern",
                            "description": f"用户意图分布: {ints}",
                            "opportunity": "基于意图分布优化服务优先级",
                            "source": "recent_logs.json"
                        })
        except Exception as e:
            print(f"分析近期行为失败: {e}")

        return insights

    def simulate_user_perspective(self):
        """模拟用户视角，发现进化机会"""
        ideas = []

        # 用户用电脑的经典场景
        user_scenarios = [
            "鼠标键盘操作",
            "看屏幕/截图/录屏",
            "听歌/看电影/音频处理",
            "玩游戏",
            "办公软件操作",
            "上网浏览/搜索",
            "聊天/社交",
            "文件管理/整理",
            "编程/开发",
            "系统设置/优化"
        ]

        ideas.append({
            "type": "user_perspective",
            "description": "用户用电脑的经典场景分析",
            "opportunity": f"当前系统已覆盖{len(user_scenarios)}种用户场景中的大部分，但仍有细化空间",
            "source": "user_perspective_simulation"
        })

        return ideas

    def generate_evolution_ideas(self):
        """生成进化创意"""
        ideas = []

        # 1. 分析能力缺口
        gaps = self.analyze_capability_gaps()
        ideas.extend(gaps)

        # 2. 分析历史失败
        failures = self.analyze_failures()
        ideas.extend(failures)

        # 3. 分析现有能力
        capabilities = self.analyze_existing_capabilities()
        ideas.extend(capabilities)

        # 4. 分析近期行为
        behaviors = self.analyze_recent_behavior()
        ideas.extend(behaviors)

        # 5. 模拟用户视角
        user_ideas = self.simulate_user_perspective()
        ideas.extend(user_ideas)

        return ideas

    def evaluate_and_rank_ideas(self, ideas):
        """评估和排序进化创意"""
        if not ideas:
            return []

        # 评分标准
        scored_ideas = []
        for idea in ideas:
            score = 0
            reason = ""

            # 类型评分
            if idea.get('type') == 'capability_gap':
                score += 30
                reason = "能力缺口是最直接的改进方向"
            elif idea.get('type') == 'failure_lesson':
                score += 25
                reason = "从失败学习可避免重复错误"
            elif idea.get('type') == 'capability_combination':
                score += 20
                reason = "能力组合创新价值较高"
            elif idea.get('type') == 'behavior_gap':
                score += 25
                reason = "行为分析可发现真实需求"
            elif idea.get('type') == 'user_perspective':
                score += 15
                reason = "用户视角是创新的重要来源"

            scored_ideas.append({
                **idea,
                "score": score,
                "reason": reason
            })

        # 按分数排序
        scored_ideas.sort(key=lambda x: x.get('score', 0), reverse=True)

        return scored_ideas

    def get_top_ideas(self, limit=5):
        """获取最值得做的进化方向"""
        ideas = self.generate_evolution_ideas()
        ranked = self.evaluate_and_rank_ideas(ideas)
        return ranked[:limit]

    def generate_report(self):
        """生成进化创意报告"""
        top_ideas = self.get_top_ideas(5)

        report = {
            "generated_at": datetime.now().isoformat(),
            "total_ideas": len(self.generate_evolution_ideas()),
            "top_ideas": top_ideas,
            "summary": f"发现{len(top_ideas)}个高优先级进化方向"
        }

        return report


def main():
    """主函数 - 命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='智能进化创意生成引擎')
    parser.add_argument('command', nargs='?', default='generate',
                        help='命令: generate(生成创意), report(生成报告), top(获取Top建议)')
    parser.add_argument('--limit', type=int, default=5, help='返回建议数量')
    parser.add_argument('--json', action='store_true', help='JSON格式输出')

    args = parser.parse_args()

    generator = EvolutionIdeaGenerator()

    if args.command == 'generate' or args.command == 'top':
        ideas = generator.get_top_ideas(args.limit)

        if args.json:
            print(json.dumps(ideas, ensure_ascii=False, indent=2))
        else:
            print("=" * 60)
            print("智能进化创意生成引擎 - Top 进化建议")
            print("=" * 60)
            for i, idea in enumerate(ideas, 1):
                print(f"\n{i}. {idea.get('description', '未命名')}")
                print(f"   类型: {idea.get('type', 'unknown')}")
                print(f"   机会: {idea.get('opportunity', '无')}")
                print(f"   评分: {idea.get('score', 0)}")
                print(f"   来源: {idea.get('source', 'unknown')}")
                print(f"   理由: {idea.get('reason', '无')}")

    elif args.command == 'report':
        report = generator.generate_report()

        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print("=" * 60)
            print("智能进化创意报告")
            print("=" * 60)
            print(f"生成时间: {report['generated_at']}")
            print(f"总创意数: {report['total_ideas']}")
            print(f"\n{report['summary']}")
            print("\nTop 建议:")
            for i, idea in enumerate(report['top_ideas'], 1):
                print(f"  {i}. [{idea.get('score', 0)}分] {idea.get('description', '未命名')}")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()