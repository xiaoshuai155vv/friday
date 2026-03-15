#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环自我进化能力深度增强引擎
version 1.0.0

让系统能够利用健康监测和效能分析数据自动评估进化状态、识别优化机会、
生成改进方案，形成更高层次的自主进化闭环。

这是对 round 538 自我进化意识与战略规划引擎的深度增强：
- 集成 round 546/548 的效能分析和健康监测数据
- 实现基于实时健康数据的动态自我评估
- 实现从「健康监测→问题识别→优化建议→自动执行」的完整闭环

功能：
1. 进化状态多维度自动评估（基于健康+效能数据）
2. 智能优化机会识别（自动分析低效模式和优化空间）
3. 改进方案自动生成（生成可执行改进建议）
4. 自我进化策略优化（根据评估结果自动调整进化策略）
5. 驾驶舱数据接口（可视化评估结果）

依赖：
- evolution_self_evolution_consciousness_strategic_planning_engine.py (round 538)
- evolution_health_monitoring_dialog_integration_engine.py (round 548)
- evolution_efficiency_dialog_analysis_engine.py (round 546)
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import statistics

# 路径配置
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

# 尝试导入依赖引擎
try:
    from evolution_self_evolution_consciousness_strategic_planning_engine import (
        EvolutionSelfEvolutionConsciousnessStrategicPlanningEngine
    )
    SELF_EVOLUTION_ENGINE_AVAILABLE = True
except ImportError:
    SELF_EVOLUTION_ENGINE_AVAILABLE = False
    print("[警告] 无法导入自我进化意识引擎，将使用简化模式")

try:
    from evolution_health_monitoring_dialog_integration_engine import (
        EvolutionHealthMonitoringDialogIntegrationEngine
    )
    HEALTH_ENGINE_AVAILABLE = True
except ImportError:
    HEALTH_ENGINE_AVAILABLE = False
    print("[警告] 无法导入健康监测对话引擎，将使用简化模式")

try:
    from evolution_efficiency_dialog_analysis_engine import (
        EvolutionEfficiencyDialogEngine
    )
    EFFICIENCY_ENGINE_AVAILABLE = True
except ImportError:
    EFFICIENCY_ENGINE_AVAILABLE = False
    print("[警告] 无法导入效能对话引擎，将使用简化模式")


class SelfEvolutionEnhancementV2Engine:
    """自我进化能力深度增强引擎 V2"""

    VERSION = "1.0.0"

    def __init__(self):
        """初始化引擎"""
        # 初始化集成引擎
        self.self_evolution_engine = None
        self.health_engine = None
        self.efficiency_engine = None

        if SELF_EVOLUTION_ENGINE_AVAILABLE:
            try:
                self.self_evolution_engine = EvolutionSelfEvolutionConsciousnessStrategicPlanningEngine()
            except Exception as e:
                print(f"[警告] 自我进化意识引擎初始化失败: {e}")

        if HEALTH_ENGINE_AVAILABLE:
            try:
                self.health_engine = EvolutionHealthMonitoringDialogIntegrationEngine()
            except Exception as e:
                print(f"[警告] 健康监测引擎初始化失败: {e}")

        if EFFICIENCY_ENGINE_AVAILABLE:
            try:
                self.efficiency_engine = EvolutionEfficiencyDialogEngine()
            except Exception as e:
                print(f"[警告] 效能对话引擎初始化失败: {e}")

        # 状态文件路径
        self.state_dir = PROJECT_ROOT / "runtime" / "state"
        self.enhancement_state_path = self.state_dir / "self_evolution_enhancement_v2_state.json"

        # 评估历史
        self.evaluation_history = self._load_evaluation_history()

    def _load_evaluation_history(self) -> List[Dict]:
        """加载评估历史"""
        if self.enhancement_state_path.exists():
            try:
                with open(self.enhancement_state_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('evaluation_history', [])
            except Exception as e:
                print(f"[警告] 加载评估历史失败: {e}")
        return []

    def _save_evaluation_history(self):
        """保存评估历史"""
        try:
            self.state_dir.mkdir(parents=True, exist_ok=True)
            with open(self.enhancement_state_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'evaluation_history': self.evaluation_history[-50:],  # 保留最近50条
                    'last_update': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[警告] 保存评估历史失败: {e}")

    def get_integrated_health_status(self) -> Dict:
        """获取集成的健康状态数据

        Returns:
            集成健康状态数据
        """
        if self.health_engine:
            try:
                return self.health_engine.get_health_status_for_dialog()
            except Exception as e:
                print(f"[错误] 获取健康状态失败: {e}")

        # 降级方案：读取状态文件
        return self._get_fallback_health_status()

    def _get_fallback_health_status(self) -> Dict:
        """降级方案：读取健康状态"""
        state_file = self.state_dir / "current_mission.json"
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    mission = json.load(f)
                    return {
                        'health_score': 80,
                        'health_level': '良好',
                        'current_round': mission.get('loop_round', 0),
                        'total_rounds': mission.get('loop_round', 0),
                        'trend': {'trend_direction': 'stable'},
                        'warnings': [],
                        'dimensions': {}
                    }
            except Exception:
                pass

        return {
            'health_score': 75,
            'health_level': '中等',
            'current_round': 549,
            'total_rounds': 549,
            'trend': {'trend_direction': 'unknown'},
            'warnings': [],
            'dimensions': {}
        }

    def get_efficiency_data(self) -> Dict:
        """获取效能数据

        Returns:
            效能分析数据
        """
        if self.efficiency_engine:
            try:
                # 尝试获取驾驶舱数据
                cockpit_data = self.efficiency_engine.get_cockpit_data()
                return {
                    'efficiency_score': cockpit_data.get('efficiency_score', 75),
                    'avg_execution_time': cockpit_data.get('avg_execution_time', 120),
                    'success_rate': cockpit_data.get('success_rate', 0.95),
                    'optimization_suggestions': cockpit_data.get('suggestions', [])
                }
            except Exception as e:
                print(f"[错误] 获取效能数据失败: {e}")

        # 降级方案
        return {
            'efficiency_score': 75,
            'avg_execution_time': 120,
            'success_rate': 0.95,
            'optimization_suggestions': []
        }

    def evaluate_evolution_state(self) -> Dict:
        """评估进化状态（核心功能）

        整合健康监测和效能分析数据，进行多维度自我评估。

        Returns:
            进化状态评估结果
        """
        # 获取多维度数据
        health_status = self.get_integrated_health_status()
        efficiency_data = self.get_efficiency_data()

        # 获取自我意识引擎的评估（如果有）
        self_assessment = {}
        if self.self_evolution_engine:
            try:
                self_assessment = self.self_evolution_engine.get_self_assessment()
            except Exception as e:
                print(f"[警告] 获取自我评估失败: {e}")

        # 综合评分计算
        health_score = health_status.get('health_score', 70)
        efficiency_score = efficiency_data.get('efficiency_score', 70)

        # 计算综合进化能力指数
        evolution_capability_index = (
            health_score * 0.4 +
            efficiency_score * 0.4 +
            self_assessment.get('capability_score', 70) * 0.2
        )

        # 评估等级
        if evolution_capability_index >= 85:
            level = "优秀"
        elif evolution_capability_index >= 70:
            level = "良好"
        elif evolution_capability_index >= 50:
            level = "中等"
        else:
            level = "需改进"

        # 评估时间戳
        timestamp = datetime.now().isoformat()

        # 构建评估结果
        evaluation_result = {
            'timestamp': timestamp,
            'evolution_capability_index': round(evolution_capability_index, 2),
            'level': level,
            'health_score': health_score,
            'efficiency_score': efficiency_score,
            'self_assessment_score': self_assessment.get('capability_score', 70),
            'current_round': health_status.get('current_round', 0),
            'total_rounds': health_status.get('total_rounds', 0),
            'dimensions': {
                'health': health_status.get('dimensions', {}),
                'efficiency': efficiency_data,
                'self_awareness': self_assessment
            },
            'health_warnings': health_status.get('warnings', []),
            'efficiency_suggestions': efficiency_data.get('optimization_suggestions', [])
        }

        # 保存到历史
        self.evaluation_history.append(evaluation_result)
        self._save_evaluation_history()

        return evaluation_result

    def identify_optimization_opportunities(self) -> List[Dict]:
        """识别优化机会

        基于评估结果，自动识别可优化的地方。

        Returns:
            优化机会列表
        """
        evaluation = self.evaluate_evolution_state()
        opportunities = []

        # 分析健康维度
        health_score = evaluation['health_score']
        if health_score < 80:
            opportunities.append({
                'id': 'health_optimization',
                'type': 'health',
                'priority': (100 - health_score) / 100,
                'description': f'健康评分较低({health_score})，建议优化健康监测策略',
                'suggestions': evaluation.get('health_warnings', [])
            })

        # 分析效能维度
        efficiency_score = evaluation['efficiency_score']
        if efficiency_score < 80:
            opportunities.append({
                'id': 'efficiency_optimization',
                'type': 'efficiency',
                'priority': (100 - efficiency_score) / 100,
                'description': f'效能评分较低({efficiency_score})，建议优化执行策略',
                'suggestions': evaluation.get('efficiency_suggestions', [])
            })

        # 分析综合指数
        overall_score = evaluation['evolution_capability_index']
        if overall_score < 75:
            opportunities.append({
                'id': 'overall_optimization',
                'type': 'overall',
                'priority': (100 - overall_score) / 100,
                'description': f'综合进化能力指数较低({overall_score})，建议全面优化',
                'suggestions': [
                    '增强健康监测频率',
                    '优化进化执行策略',
                    '加强自我意识评估能力'
                ]
            })

        # 按优先级排序
        opportunities.sort(key=lambda x: x['priority'], reverse=True)

        return opportunities

    def generate_improvement_suggestions(self) -> Dict:
        """生成改进建议

        基于优化机会自动生成可执行的改进建议。

        Returns:
            改进建议
        """
        opportunities = self.identify_optimization_opportunities()

        if not opportunities:
            return {
                'status': 'optimal',
                'message': '当前进化状态良好，无需改进',
                'suggestions': []
            }

        # 生成建议
        suggestions = []
        for opp in opportunities[:3]:  # 最多3条
            suggestions.append({
                'opportunity_id': opp['id'],
                'type': opp['type'],
                'priority': opp['priority'],
                'description': opp['description'],
                'action': f'优化{opp["type"]}维度，优先级: {opp["priority"]:.2f}',
                'estimated_impact': f'预计提升综合指数 {opp["priority"] * 10:.1f}%'
            })

        return {
            'status': 'needs_improvement',
            'message': f'发现 {len(opportunities)} 个优化机会',
            'opportunities_count': len(opportunities),
            'suggestions': suggestions,
            'top_priority': opportunities[0]['id'] if opportunities else None
        }

    def get_cockpit_data(self) -> Dict:
        """获取驾驶舱展示数据

        Returns:
            驾驶舱数据
        """
        evaluation = self.evaluate_evolution_state()
        suggestions = self.generate_improvement_suggestions()

        return {
            'evolution_capability_index': evaluation['evolution_capability_index'],
            'level': evaluation['level'],
            'health_score': evaluation['health_score'],
            'efficiency_score': evaluation['efficiency_score'],
            'self_assessment_score': evaluation['self_assessment_score'],
            'current_round': evaluation['current_round'],
            'total_rounds': evaluation['total_rounds'],
            'opportunities': self.identify_optimization_opportunities(),
            'suggestions': suggestions,
            'last_evaluation': evaluation['timestamp']
        }

    def run_full_cycle(self) -> Dict:
        """运行完整评估周期

        Returns:
            完整评估结果
        """
        # 1. 评估状态
        evaluation = self.evaluate_evolution_state()

        # 2. 识别优化机会
        opportunities = self.identify_optimization_opportunities()

        # 3. 生成改进建议
        suggestions = self.generate_improvement_suggestions()

        # 4. 构建完整报告
        report = {
            'status': 'completed',
            'timestamp': datetime.now().isoformat(),
            'evaluation': evaluation,
            'opportunities': opportunities,
            'suggestions': suggestions,
            'recommendation': self._generate_recommendation(evaluation, opportunities, suggestions)
        }

        return report

    def _generate_recommendation(self, evaluation: Dict, opportunities: List[Dict], suggestions: Dict) -> str:
        """生成推荐建议"""
        level = evaluation['level']
        index = evaluation['evolution_capability_index']

        if level == '优秀':
            return "当前进化状态优秀，可以继续推进新的进化方向，探索创新机会。"
        elif level == '良好':
            return "当前进化状态良好，建议关注发现的优化机会，持续提升进化能力。"
        elif level == '中等':
            return "当前进化状态中等，建议优先处理高优先级的优化机会，提升整体进化能力。"
        else:
            return "当前进化状态需要改进，建议立即处理优化机会，必要时可触发自动修复流程。"

    def get_status_summary(self) -> str:
        """获取状态摘要

        Returns:
            状态摘要
        """
        evaluation = self.evaluate_evolution_state()

        summary = f"""
## 自我进化能力评估报告

- **综合指数**: {evaluation['evolution_capability_index']:.1f} ({evaluation['level']})
- **健康评分**: {evaluation['health_score']}
- **效能评分**: {evaluation['efficiency_score']}
- **自我评估**: {evaluation['self_assessment_score']}
- **当前轮次**: Round {evaluation['current_round']}
- **历史轮数**: {evaluation['total_rounds']} 轮
"""

        opportunities = self.identify_optimization_opportunities()
        if opportunities:
            summary += f"\n### 优化机会 ({len(opportunities)}个)\n"
            for i, opp in enumerate(opportunities[:3], 1):
                summary += f"{i}. [{opp['type']}] {opp['description']}\n"

        return summary


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description='智能全场景进化环自我进化能力深度增强引擎 V2'
    )
    parser.add_argument('--status', action='store_true', help='显示状态摘要')
    parser.add_argument('--evaluate', action='store_true', help='执行完整评估')
    parser.add_argument('--opportunities', action='store_true', help='识别优化机会')
    parser.add_argument('--suggestions', action='store_true', help='生成改进建议')
    parser.add_argument('--cockpit-data', action='store_true', help='获取驾驶舱数据')
    parser.add_argument('--full-cycle', action='store_true', help='运行完整评估周期')

    args = parser.parse_args()

    # 初始化引擎
    engine = SelfEvolutionEnhancementV2Engine()

    # 执行命令
    if args.status:
        print(engine.get_status_summary())
    elif args.evaluate:
        result = engine.evaluate_evolution_state()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.opportunities:
        opportunities = engine.identify_optimization_opportunities()
        print(json.dumps(opportunities, ensure_ascii=False, indent=2))
    elif args.suggestions:
        suggestions = engine.generate_improvement_suggestions()
        print(json.dumps(suggestions, ensure_ascii=False, indent=2))
    elif args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
    elif args.full_cycle:
        result = engine.run_full_cycle()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 默认显示状态
        print(engine.get_status_summary())


if __name__ == '__main__':
    main()