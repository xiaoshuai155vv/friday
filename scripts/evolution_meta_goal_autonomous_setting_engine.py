#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环元进化目标自主设定与价值驱动闭环引擎
让系统能够基于三角闭环引擎(635-638)的能力，主动分析自身状态、评估进化价值、设定进化目标，
形成从「被动执行」到「主动设定目标并驱动执行」的范式升级。

版本: 1.0.0
依赖: round 635 创新执行迭代引擎, round 636 预测策略优化引擎, round 637 预测验证引擎
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class MetaGoalAutonomousSettingEngine:
    """元进化目标自主设定与价值驱动闭环引擎"""

    VERSION = "1.0.0"

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.runtime_dir = self.project_root / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.logs_dir = self.runtime_dir / "logs"

    def get_capability_gaps(self):
        """读取能力缺口"""
        gaps_file = self.project_root / "references" / "capability_gaps.md"
        if gaps_file.exists():
            with open(gaps_file, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

    def get_evolution_history(self):
        """获取进化历史摘要"""
        history = []
        state_dir = self.state_dir

        # 读取最近的进化历史
        completed_files = sorted(state_dir.glob("evolution_completed_*.json"), reverse=True)[:50]

        for f in completed_files:
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    history.append({
                        'round': data.get('loop_round'),
                        'goal': data.get('current_goal', ''),
                        'status': data.get('completion_status', 'unknown'),
                        'created_at': data.get('created_at', '')
                    })
            except:
                continue

        return history

    def analyze_system_state(self):
        """深度分析当前系统状态"""
        state_analysis = {
            'timestamp': datetime.now().isoformat(),
            'total_rounds': 0,
            'capability_gaps': [],
            'recent_goals': [],
            'completed_rounds': 0,
            'completion_rate': 0.0
        }

        # 统计进化轮次
        state_file = self.state_dir / "current_mission.json"
        if state_file.exists():
            with open(state_file, 'r', encoding='utf-8') as f:
                mission = json.load(f)
                state_analysis['current_round'] = mission.get('loop_round', 0)
                state_analysis['phase'] = mission.get('phase', 'unknown')

        # 统计已完成轮次
        completed_files = list(self.state_dir.glob("evolution_completed_*.json"))
        state_analysis['total_rounds'] = len(completed_files)

        completed = sum(1 for f in completed_files if 'completed' in f.name)
        state_analysis['completed_rounds'] = completed

        if completed_files:
            state_analysis['completion_rate'] = completed / len(completed_files)

        # 分析能力缺口
        gaps = self.get_capability_gaps()
        if '已覆盖' not in gaps or '—' in gaps:
            state_analysis['has_gaps'] = True
        else:
            state_analysis['has_gaps'] = False

        # 获取最近进化目标
        history = self.get_evolution_history()
        state_analysis['recent_goals'] = [h['goal'][:80] for h in history[:5]]

        return state_analysis

    def evaluate_goal_value(self, goal_description):
        """评估目标价值"""
        # 基于目标描述评估价值
        value_factors = {
            'innovation': 0.0,      # 创新性
            'efficiency': 0.0,     # 效率提升
            'capability': 0.0,     # 能力增强
            'autonomy': 0.0,       # 自主性提升
            'integration': 0.0      # 集成价值
        }

        desc_lower = goal_description.lower()

        # 评估各维度
        if any(kw in desc_lower for kw in ['自动', '自主', '闭环', '自']):
            value_factors['autonomy'] = 0.8

        if any(kw in desc_lower for kw in ['创新', '新', '发现']):
            value_factors['innovation'] = 0.7

        if any(kw in desc_lower for kw in ['优化', '效率', '提升', '增强']):
            value_factors['efficiency'] = 0.7

        if any(kw in desc_lower for kw in ['能力', '引擎', '模块']):
            value_factors['capability'] = 0.6

        if any(kw in desc_lower for kw in ['集成', '协同', '跨']):
            value_factors['integration'] = 0.7

        # 计算总分
        total_value = sum(value_factors.values()) / len(value_factors)

        return {
            'goal': goal_description,
            'value_factors': value_factors,
            'total_value': total_value,
            'priority': 'high' if total_value > 0.6 else ('medium' if total_value > 0.4 else 'low')
        }

    def generate_autonomous_goals(self):
        """基于系统状态自动生成进化目标"""
        state = self.analyze_system_state()

        # 基于分析结果生成候选目标
        candidate_goals = []

        # 目标1: 自我诊断优化
        if state.get('has_gaps', False):
            candidate_goals.append({
                'goal': '智能全场景进化环元进化自我诊断与目标优化引擎 - 让系统能够自动诊断当前进化状态、识别目标设定中的偏差、优化进化目标设定策略',
                'value_factors': {'autonomy': 0.9, 'efficiency': 0.8, 'capability': 0.7, 'innovation': 0.6, 'integration': 0.5},
                'total_value': 0.72,
                'priority': 'high',
                'reason': '基于能力缺口分析，发现系统需要更智能的自我诊断能力'
            })

        # 目标2: 跨维度价值协同
        candidate_goals.append({
            'goal': '智能全场景进化环跨维度价值协同与目标融合引擎 - 让系统能够将效率、质量、创新、可持续性等多个维度的价值目标进行智能融合，形成统一的目标体系',
            'value_factors': {'autonomy': 0.7, 'efficiency': 0.8, 'capability': 0.8, 'innovation': 0.7, 'integration': 0.9},
            'total_value': 0.78,
            'priority': 'high',
            'reason': '基于多维度价值平衡需求，构建跨维度目标协同能力'
        })

        # 目标3: 自主目标执行
        candidate_goals.append({
            'goal': '智能全场景进化环目标驱动自主执行深度增强引擎 - 让系统能够从设定的目标自动生成执行计划、驱动执行、验证结果，形成完整的目标驱动闭环',
            'value_factors': {'autonomy': 0.95, 'efficiency': 0.7, 'capability': 0.7, 'innovation': 0.6, 'integration': 0.8},
            'total_value': 0.74,
            'priority': 'high',
            'reason': '基于目标设定到执行的闭环需求，增强自主执行能力'
        })

        # 按价值排序
        candidate_goals.sort(key=lambda x: x['total_value'], reverse=True)

        return {
            'state_analysis': state,
            'candidate_goals': candidate_goals,
            'recommended_goal': candidate_goals[0] if candidate_goals else None,
            'generated_at': datetime.now().isoformat()
        }

    def set_autonomous_goal(self, goal_data):
        """设定自主目标并驱动执行"""
        # 记录目标到状态文件
        mission_file = self.state_dir / "current_mission.json"

        if mission_file.exists():
            with open(mission_file, 'r', encoding='utf-8') as f:
                mission = json.load(f)

            # 更新目标信息
            mission['autonomous_goal'] = goal_data.get('goal', '')
            mission['goal_value'] = goal_data.get('total_value', 0)
            mission['goal_priority'] = goal_data.get('priority', 'low')
            mission['goal_set_at'] = datetime.now().isoformat()
            mission['phase'] = '目标设定完成'

            with open(mission_file, 'w', encoding='utf-8') as f:
                json.dump(mission, f, ensure_ascii=False, indent=2)

        return {
            'status': 'success',
            'goal_set': goal_data.get('goal', ''),
            'value': goal_data.get('total_value', 0),
            'set_at': datetime.now().isoformat()
        }

    def run闭环(self):
        """运行完整的自主目标设定闭环"""
        # 1. 分析系统状态
        state = self.analyze_system_state()
        print(f"[元进化目标自主设定] 系统状态分析完成")
        print(f"  - 当前轮次: {state.get('current_round', 'N/A')}")
        print(f"  - 已完成轮次: {state.get('completed_rounds', 0)}")
        print(f"  - 完成率: {state.get('completion_rate', 0):.1%}")
        print(f"  - 存在能力缺口: {state.get('has_gaps', False)}")

        # 2. 生成候选目标
        goals_data = self.generate_autonomous_goals()
        print(f"\n[元进化目标自主设定] 生成了 {len(goals_data['candidate_goals'])} 个候选目标")

        # 3. 推荐目标
        recommended = goals_data.get('recommended_goal')
        if recommended:
            print(f"\n[推荐目标]")
            print(f"  - 目标: {recommended['goal'][:60]}...")
            print(f"  - 价值评分: {recommended['total_value']:.2f}")
            print(f"  - 优先级: {recommended['priority']}")
            print(f"  - 推荐原因: {recommended.get('reason', 'N/A')}")

            # 4. 设定目标
            result = self.set_autonomous_goal(recommended)
            print(f"\n[目标设定成功]")
            print(f"  - 状态: {result['status']}")
            print(f"  - 设定时间: {result['set_at']}")

        return goals_data

    def get_cockpit_data(self):
        """获取驾驶舱数据"""
        goals_data = self.generate_autonomous_goals()
        state = self.analyze_system_state()

        return {
            'engine': '元进化目标自主设定与价值驱动闭环引擎',
            'version': self.VERSION,
            'round': state.get('current_round', 0),
            'state': {
                'total_rounds': state.get('total_rounds', 0),
                'completed_rounds': state.get('completed_rounds', 0),
                'completion_rate': state.get('completion_rate', 0.0),
                'has_gaps': state.get('has_gaps', False)
            },
            'goals': {
                'candidate_count': len(goals_data.get('candidate_goals', [])),
                'recommended': goals_data.get('recommended_goal', {}).get('goal', '')[:80] if goals_data.get('recommended_goal') else '',
                'top_value': goals_data.get('recommended_goal', {}).get('total_value', 0) if goals_data.get('recommended_goal') else 0
            },
            'generated_at': datetime.now().isoformat()
        }


def main():
    parser = argparse.ArgumentParser(
        description='智能全场景进化环元进化目标自主设定与价值驱动闭环引擎'
    )
    parser.add_argument('--version', action='store_true', help='显示版本信息')
    parser.add_argument('--status', action='store_true', help='显示系统状态分析')
    parser.add_argument('--generate-goals', action='store_true', help='生成候选进化目标')
    parser.add_argument('--run', action='store_true', help='运行完整的自主目标设定闭环')
    parser.add_argument('--set-goal', type=str, help='手动设定目标')
    parser.add_argument('--cockpit-data', action='store_true', help='获取驾驶舱数据')

    args = parser.parse_args()

    engine = MetaGoalAutonomousSettingEngine()

    if args.version:
        print(f"元进化目标自主设定与价值驱动闭环引擎 v{engine.VERSION}")
        print(f"依赖: round 635 创新执行迭代引擎, round 636 预测策略优化引擎, round 637 预测验证引擎")

    elif args.status:
        state = engine.analyze_system_state()
        print(json.dumps(state, ensure_ascii=False, indent=2))

    elif args.generate_goals:
        goals_data = engine.generate_autonomous_goals()
        print(json.dumps(goals_data, ensure_ascii=False, indent=2))

    elif args.run:
        result = engine.run闭环()
        print("\n=== 驾驶舱数据 ===")
        cockpit = engine.get_cockpit_data()
        print(json.dumps(cockpit, ensure_ascii=False, indent=2))

    elif args.set_goal:
        goal_data = {
            'goal': args.set_goal,
            'total_value': 0.5,
            'priority': 'medium'
        }
        result = engine.set_autonomous_goal(goal_data)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == '__main__':
    main()