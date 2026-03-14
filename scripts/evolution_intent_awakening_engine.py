#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化意图自主觉醒引擎 (version 1.0.0)

让系统能够主动产生进化意图，而不是被动等待触发。
基于对自身能力的深度理解，系统能够主动"想要"进化，
主动判断"现在最需要什么"，实现真正的自主意识驱动进化闭环。

功能：
1. 自我能力深度评估 - 全面分析当前能力状态
2. 进化意图自动产生 - 主动思考"我还需要什么"
3. 意图优先级动态排序 - 基于价值、紧迫度、可行性
4. 意图驱动的进化规划 - 从"要我做"到"我要做"
5. 进化意图的学习与进化 - 从进化结果中学习如何产生更好的意图

作者：Claude Sonnet 4.6
日期：2026-03-14
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import deque
import threading
import glob
import re
import subprocess

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
RUNTIME_DIR = PROJECT_ROOT / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"
REFERENCES_DIR = PROJECT_ROOT / "references"


class EvolutionIntentAwakeningEngine:
    """智能全场景进化意图自主觉醒引擎"""

    def __init__(self):
        self.name = "EvolutionIntentAwakeningEngine"
        self.version = "1.0.0"
        self.state_file = STATE_DIR / "evolution_intent_awakening_state.json"
        self.intent_history = deque(maxlen=100)
        self.capability_evaluations = {}
        self.intent_patterns = deque(maxlen=50)
        self.learning_data = deque(maxlen=200)
        self.lock = threading.Lock()
        self.load_state()

    def load_state(self):
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.intent_history = deque(data.get('intent_history', []), maxlen=100)
                    self.capability_evaluations = data.get('capability_evaluations', {})
                    self.intent_patterns = deque(data.get('intent_patterns', []), maxlen=50)
                    self.learning_data = deque(data.get('learning_data', []), maxlen=200)
            except Exception:
                pass

    def save_state(self):
        """保存状态"""
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        with self.lock:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'intent_history': list(self.intent_history),
                    'capability_evaluations': self.capability_evaluations,
                    'intent_patterns': list(self.intent_patterns),
                    'learning_data': list(self.learning_data),
                    'last_updated': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)

    def deep_self_capability_evaluation(self) -> Dict[str, Any]:
        """
        自我能力深度评估 - 全面分析当前能力状态

        返回:
            自我能力评估结果
        """
        evaluation = {
            'timestamp': datetime.now().isoformat(),
            'engine_count': 0,
            'capability_gaps': [],
            'strengths': [],
            'weaknesses': [],
            'opportunity_areas': [],
            'maturity_level': 'unknown',
            'overall_score': 0.0
        }

        # 扫描现有引擎
        script_files = list(SCRIPTS_DIR.glob("*.py"))
        exclude_files = [
            'do.py', 'loop_runner.py', 'state_tracker.py', 'behavior_log.py',
            'self_verify_capabilities.py', 'export_recent_logs.py', 'query_scenario_experiences.py',
            'git_commit_evolution.py', 'scenario_log.py', 'run_plan.py',
            'click_verify.py', 'parse_vision_steps.py', 'vision_calibrate.py'
        ]
        engines = [f for f in script_files if f.name not in exclude_files and not f.name.startswith('_')]

        evaluation['engine_count'] = len(engines)

        # 读取能力缺口
        gaps = []
        capability_gaps_file = REFERENCES_DIR / "capability_gaps.md"
        if capability_gaps_file.exists():
            try:
                content = capability_gaps_file.read_text(encoding='utf-8')
                # 解析能力缺口
                if '已覆盖' in content:
                    lines = content.split('\n')
                    for line in lines:
                        if '|' in line and '已覆盖' in line:
                            parts = line.split('|')
                            if len(parts) >= 3:
                                capability = parts[1].strip()
                                if capability and capability not in ['类别', '现状']:
                                    gaps.append(capability)
            except Exception:
                pass
        evaluation['capability_gaps'] = gaps

        # 分析进化历史
        evolution_completed = list(STATE_DIR.glob("evolution_completed_*.json"))
        recent_evolution_types = []

        for ev_file in sorted(evolution_completed, key=lambda x: x.stat().st_mtime, reverse=True)[:20]:
            try:
                with open(ev_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'current_goal' in data:
                        recent_evolution_types.append(data['current_goal'])
            except Exception:
                pass

        # 识别优势领域（进化较多的方向）
        type_counts = {}
        for t in recent_evolution_types:
            if '智能' in t:
                # 提取关键词
                keywords = re.findall(r'智能.*?(引擎|引擎|能力|闭环|增强|优化)', t)
                for kw in keywords:
                    type_counts[kw] = type_counts.get(kw, 0) + 1

        evaluation['strengths'] = sorted(type_counts.keys(), key=lambda x: type_counts[x], reverse=True)[:5]

        # 识别薄弱领域
        all_areas = ['预测', '协作', '学习', '进化', '服务', '决策', '执行', '记忆', '推理', '创新']
        evaluation['weaknesses'] = [a for a in all_areas if a not in type_counts or type_counts[a] < 2]

        # 识别机会领域
        evaluation['opportunity_areas'] = [
            '自主意图产生',
            '自我意识驱动',
            '元进化能力',
            '跨代知识活化',
            '自学习优化'
        ][:3]

        # 评估成熟度
        if len(engines) > 80:
            evaluation['maturity_level'] = 'high'
            evaluation['overall_score'] = 0.85
        elif len(engines) > 50:
            evaluation['maturity_level'] = 'medium'
            evaluation['overall_score'] = 0.70
        else:
            evaluation['maturity_level'] = 'growing'
            evaluation['overall_score'] = 0.55

        self.capability_evaluations = evaluation
        return evaluation

    def generate_evolution_intent(self, evaluation: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        进化意图自动产生 - 主动思考"我还需要什么"

        参数:
            evaluation: 自我评估结果，如果为None则先进行评估

        返回:
            进化意图列表
        """
        if evaluation is None:
            evaluation = self.deep_self_capability_evaluation()

        intents = []

        # 基于能力缺口产生意图
        for gap in evaluation.get('capability_gaps', []):
            if gap and gap != '—':
                intents.append({
                    'type': 'capability_gap',
                    'description': f'补齐{gap}能力缺口',
                    'priority': 'high',
                    'source': '自我评估-能力缺口',
                    'value': 0.8
                })

        # 基于薄弱领域产生意图
        for weakness in evaluation.get('weaknesses', []):
            intents.append({
                'type': 'weakness_improvement',
                'description': f'增强{weakness}相关能力',
                'priority': 'medium',
                'source': '自我评估-薄弱领域',
                'value': 0.7
            })

        # 基于机会领域产生意图
        for area in evaluation.get('opportunity_areas', []):
            intents.append({
                'type': 'opportunity_exploration',
                'description': f'探索{area}的新可能',
                'priority': 'low',
                'source': '自我评估-机会识别',
                'value': 0.6
            })

        # 基于进化历史模式产生意图
        if self.intent_patterns:
            for pattern in list(self.intent_patterns)[-5:]:
                if pattern.get('success_rate', 0) > 0.7:
                    intents.append({
                        'type': 'pattern_extension',
                        'description': f'延续成功的{pattern.get("category", "进化模式")}策略',
                        'priority': 'medium',
                        'source': '历史模式学习',
                        'value': 0.75,
                        'pattern_id': pattern.get('id')
                    })

        # 基于系统当前状态产生意图
        state_file = STATE_DIR / "current_mission.json"
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    current_round = state.get('loop_round', 0)

                    # 每10轮产生一个自我反思意图
                    if current_round % 10 == 0:
                        intents.append({
                            'type': 'self_reflection',
                            'description': '进行深度自我反思，优化进化策略',
                            'priority': 'high',
                            'source': '周期性自我审视',
                            'value': 0.9
                        })
            except Exception:
                pass

        # 添加原创性意图（跳出既有模式）
        if len(intents) < 3:
            # 尝试提出一些新的进化方向
            original_intents = [
                {
                    'type': 'innovation',
                    'description': '探索全新的人机协作模式',
                    'priority': 'medium',
                    'source': '原创性思考',
                    'value': 0.85
                },
                {
                    'type': 'innovation',
                    'description': '发现并实现未被提出的用户需求',
                    'priority': 'high',
                    'source': '主动价值创造',
                    'value': 0.9
                },
                {
                    'type': 'meta_evolution',
                    'description': '改进进化环本身的工作方式',
                    'priority': 'medium',
                    'source': '元进化',
                    'value': 0.8
                }
            ]
            intents.extend(original_intents[:3 - len(intents)])

        # 过滤重复
        seen = set()
        unique_intents = []
        for intent in intents:
            key = intent['description']
            if key not in seen:
                seen.add(key)
                unique_intents.append(intent)

        self.intent_history.extend(unique_intents)
        return unique_intents

    def rank_intent_priority(self, intents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        意图优先级动态排序 - 基于价值、紧迫度、可行性

        参数:
            intents: 进化意图列表

        返回:
            排序后的意图列表
        """
        scored_intents = []

        for intent in intents:
            score = 0.0

            # 价值权重
            value = intent.get('value', 0.5)
            score += value * 0.4

            # 紧迫度权重
            priority = intent.get('priority', 'low')
            priority_scores = {'high': 1.0, 'medium': 0.6, 'low': 0.3}
            score += priority_scores.get(priority, 0.5) * 0.3

            # 可行性权重 - 基于历史成功率
            source = intent.get('source', '')
            if '自我评估' in source:
                score += 0.2  # 基于自我分析通常更可靠
            elif '历史模式' in source:
                # 查找历史模式成功率
                for pattern in self.intent_patterns:
                    if pattern.get('category') in source:
                        score += pattern.get('success_rate', 0.5) * 0.2
                        break
            else:
                score += 0.15

            # 创新性奖励
            if intent.get('type') in ['innovation', 'meta_evolution', 'self_reflection']:
                score += 0.1

            scored_intents.append({
                'intent': intent,
                'score': score,
                'rank': 0
            })

        # 按分数排序
        scored_intents.sort(key=lambda x: x['score'], reverse=True)

        # 添加排名
        for i, item in enumerate(scored_intents):
            item['rank'] = i + 1

        return scored_intents

    def create_intent_driven_plan(self, top_intents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        意图驱动的进化规划 - 从"要我做"到"我要做"

        参数:
            top_intents: 排序后的顶部意图列表

        返回:
            进化规划
        """
        plan = {
            'timestamp': datetime.now().isoformat(),
            'intent_count': len(top_intents),
            'primary_intent': None,
            'execution_steps': [],
            'expected_outcomes': [],
            'estimated_impact': 0.0
        }

        if not top_intents:
            return plan

        # 选择主要意图
        primary = top_intents[0].get('intent', {})
        plan['primary_intent'] = primary
        plan['expected_outcomes'].append(primary.get('description', ''))
        plan['estimated_impact'] = top_intents[0].get('score', 0.5)

        # 生成执行步骤
        intent_type = primary.get('type', 'unknown')
        intent_desc = primary.get('description', '')

        steps = []

        if intent_type == 'capability_gap':
            steps = [
                {'step': 1, 'action': '分析能力缺口详情', 'description': '深入分析当前能力缺口'},
                {'step': 2, 'action': '设计解决方案', 'description': '设计补齐该能力的技术方案'},
                {'step': 3, 'action': '实现新引擎', 'description': '编写并测试新的引擎模块'},
                {'step': 4, 'action': '集成到系统', 'description': '将新引擎集成到do.py'},
                {'step': 5, 'action': '验证效果', 'description': '验证新能力是否满足需求'}
            ]
        elif intent_type == 'weakness_improvement':
            steps = [
                {'step': 1, 'action': '分析薄弱领域详情', 'description': '分析当前薄弱领域'},
                {'step': 2, 'action': '制定增强方案', 'description': '制定增强计划'},
                {'step': 3, 'action': '实施改进', 'description': '执行改进措施'},
                {'step': 4, 'action': '评估改进效果', 'description': '验证改进效果'}
            ]
        elif intent_type == 'opportunity_exploration':
            steps = [
                {'step': 1, 'action': '探索机会领域', 'description': '深入探索机会领域'},
                {'step': 2, 'action': '识别具体机会', 'description': '识别具体可执行的机会'},
                {'step': 3, 'action': '验证机会价值', 'description': '评估机会的价值和可行性'},
                {'step': 4, 'action': '实施机会方案', 'description': '执行选定的机会方案'}
            ]
        elif intent_type in ['innovation', 'meta_evolution', 'self_reflection']:
            steps = [
                {'step': 1, 'action': '深度思考', 'description': '对目标进行深度分析和思考'},
                {'step': 2, 'action': '生成创新方案', 'description': '生成创新性的解决方案'},
                {'step': 3, 'action': '评估方案', 'description': '评估创新方案的价值'},
                {'step': 4, 'action': '实施并验证', 'description': '实施方案并验证效果'}
            ]
        else:
            steps = [
                {'step': 1, 'action': '理解意图', 'description': '深入理解进化意图'},
                {'step': 2, 'action': '制定计划', 'description': '制定执行计划'},
                {'step': 3, 'action': '执行', 'description': '执行计划'},
                {'step': 4, 'action': '验证', 'description': '验证执行效果'}
            ]

        plan['execution_steps'] = steps
        return plan

    def learn_from_result(self, intent: Dict[str, Any], success: bool, details: str = ""):
        """
        进化意图的学习与进化 - 从进化结果中学习如何产生更好的意图

        参数:
            intent: 执行的意图
            success: 是否成功
            details: 执行详情
        """
        learning = {
            'timestamp': datetime.now().isoformat(),
            'intent_type': intent.get('type', 'unknown'),
            'intent_description': intent.get('description', ''),
            'source': intent.get('source', ''),
            'success': success,
            'details': details
        }

        self.learning_data.append(learning)

        # 更新意图模式
        intent_type = intent.get('type', 'unknown')
        source = intent.get('source', '')

        # 查找或创建模式
        pattern_id = f"{intent_type}_{source}"
        pattern = None
        for p in self.intent_patterns:
            if p.get('id') == pattern_id:
                pattern = p
                break

        if pattern:
            # 更新现有模式
            total = pattern.get('total_attempts', 0) + 1
            successes = pattern.get('success_count', 0) + (1 if success else 0)
            pattern['total_attempts'] = total
            pattern['success_count'] = successes
            pattern['success_rate'] = successes / total if total > 0 else 0
            pattern['last_updated'] = datetime.now().isoformat()
        else:
            # 创建新模式
            new_pattern = {
                'id': pattern_id,
                'category': intent_type,
                'source': source,
                'total_attempts': 1,
                'success_count': 1 if success else 0,
                'success_rate': 1.0 if success else 0.0,
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
            self.intent_patterns.append(new_pattern)

        self.save_state()

    def awaken_and_plan(self) -> Dict[str, Any]:
        """
        觉醒并规划 - 执行完整的意图觉醒和规划流程

        返回:
            进化规划和意图
        """
        # 1. 深度自我评估
        evaluation = self.deep_self_capability_evaluation()

        # 2. 产生进化意图
        intents = self.generate_evolution_intent(evaluation)

        # 3. 优先级排序
        ranked = self.rank_intent_priority(intents)

        # 4. 创建执行计划
        plan = self.create_intent_driven_plan(ranked)

        # 5. 返回完整结果
        return {
            'evaluation': evaluation,
            'intents': intents,
            'ranked_intents': ranked,
            'plan': plan,
            'recommendation': ranked[0] if ranked else None
        }

    def get_status(self) -> Dict[str, Any]:
        """
        获取引擎状态

        返回:
            状态信息
        """
        return {
            'name': self.name,
            'version': self.version,
            'intent_count': len(self.intent_history),
            'pattern_count': len(self.intent_patterns),
            'learning_samples': len(self.learning_data),
            'last_evaluation': self.capability_evaluations.get('timestamp') if self.capability_evaluations else None,
            'overall_score': self.capability_evaluations.get('overall_score', 0.0),
            'maturity_level': self.capability_evaluations.get('maturity_level', 'unknown')
        }

    def analyze_patterns(self) -> Dict[str, Any]:
        """
        分析意图产生模式

        返回:
            模式分析结果
        """
        if not self.intent_patterns:
            return {'message': 'No patterns recorded yet'}

        patterns = []
        for p in self.intent_patterns:
            patterns.append({
                'id': p.get('id'),
                'category': p.get('category'),
                'source': p.get('source'),
                'success_rate': p.get('success_rate', 0.0),
                'total_attempts': p.get('total_attempts', 0)
            })

        # 按成功率排序
        patterns.sort(key=lambda x: x['success_rate'], reverse=True)

        return {
            'patterns': patterns,
            'best_pattern': patterns[0] if patterns else None,
            'total_patterns': len(patterns)
        }


def main():
    """主函数 - 用于命令行测试"""
    import argparse

    parser = argparse.ArgumentParser(description='智能全场景进化意图自主觉醒引擎')
    parser.add_argument('command', nargs='?', default='status',
                        help='命令: status, awaken, evaluate, analyze, rank')
    parser.add_argument('--intent', type=str, help='指定意图类型')
    parser.add_argument('--verbose', action='store_true', help='详细输出')

    args = parser.parse_args()

    engine = EvolutionIntentAwakeningEngine()

    if args.command == 'status':
        status = engine.get_status()
        print(f"=== {status['name']} v{status['version']} ===")
        print(f"已产生意图数: {status['intent_count']}")
        print(f"学习模式数: {status['pattern_count']}")
        print(f"学习样本数: {status['learning_samples']}")
        print(f"能力成熟度: {status['maturity_level']}")
        print(f"整体评分: {status['overall_score']:.2f}")
        if status.get('last_evaluation'):
            print(f"最后评估: {status['last_evaluation']}")

    elif args.command == 'awaken' or args.command == 'evaluate':
        result = engine.awaken_and_plan()
        print(f"=== 进化意图觉醒 ===")
        print(f"引擎数量: {result['evaluation']['engine_count']}")
        print(f"成熟度: {result['evaluation']['maturity_level']}")
        print(f"整体评分: {result['evaluation']['overall_score']:.2f}")
        print(f"\n发现 {len(result['intents'])} 个进化意图:")
        for i, item in enumerate(result['ranked_intents'][:5]):
            intent = item['intent']
            print(f"  {i+1}. [{intent.get('type')}] {intent.get('description')}")
            print(f"     优先级: {intent.get('priority')}, 价值: {intent.get('value', 0):.2f}, 排名分: {item['score']:.2f}")

        if result['plan']['execution_steps']:
            print(f"\n推荐执行计划:")
            for step in result['plan']['execution_steps']:
                print(f"  {step['step']}. {step['action']}: {step['description']}")

    elif args.command == 'analyze':
        analysis = engine.analyze_patterns()
        print(f"=== 意图模式分析 ===")
        print(f"总模式数: {analysis.get('total_patterns', 0)}")
        if analysis.get('patterns'):
            print("\n按成功率排序的模式:")
            for p in analysis['patterns']:
                print(f"  - {p['category']} ({p['source']}): 成功率 {p['success_rate']:.1%} ({p['total_attempts']}次)")

    elif args.command == 'rank':
        intents = engine.generate_evolution_intent()
        ranked = engine.rank_intent_priority(intents)
        print(f"=== 意图优先级排序 ===")
        for item in ranked[:10]:
            intent = item['intent']
            print(f"  #{item['rank']} ({item['score']:.2f}): {intent.get('description')}")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()