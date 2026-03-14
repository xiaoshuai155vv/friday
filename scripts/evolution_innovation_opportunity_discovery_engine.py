#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环创新机会自动发现与主动进化引擎
version 1.0.0

功能：
1. 系统状态分析能力 - 分析当前引擎能力、运行状态、进化历史
2. 创新机会自动发现功能 - 从能力缺口、性能瓶颈、进化趋势中发现机会
3. 创新方案自动生成功能 - 基于发现的机会生成创新解决方案
4. 方案价值自动评估功能 - 评估创新方案的实施价值、可行性、风险
5. 主动进化驱动功能 - 将高价值创新方案转化为进化任务并触发执行
6. 与进化驾驶舱深度集成 - 可视化创新机会和方案

集成到 do.py 支持：创新发现、创新机会、主动进化、方案评估、机会分析等关键词触发

作者：AI Evolution System
日期：2026-03-15
"""

import os
import sys
import json
import re
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import argparse

SCRIPT_DIR = Path(__file__).parent
RUNTIME_DIR = SCRIPT_DIR / ".." / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"


class EvolutionInnovationOpportunityDiscoveryEngine:
    """创新机会自动发现与主动进化引擎 v1.0.0"""

    def __init__(self, base_path: str = None):
        self.version = "1.0.0"
        self.base_path = base_path or str(SCRIPT_DIR)
        self.runtime_path = os.path.join(self.base_path, 'runtime')
        self.state_path = os.path.join(self.runtime_path, 'state')
        self.logs_path = os.path.join(self.runtime_path, 'logs')

        # 状态文件
        self.state_file = Path(STATE_DIR) / "innovation_discovery_state.json"
        self.opportunities_file = Path(STATE_DIR) / "innovation_opportunities.json"
        self.solutions_file = Path(STATE_DIR) / "innovation_solutions.json"
        self.evaluations_file = Path(STATE_DIR) / "innovation_evaluations.json"

        # 尝试导入相关引擎
        self.knowledge_engine = None
        self.trend_engine = None
        self._init_engines()

    def _init_engines(self):
        """初始化相关引擎"""
        try:
            sys.path.insert(0, self.base_path)
            from evolution_knowledge_driven_full_loop_engine import EvolutionKnowledgeDrivenFullLoopEngine
            self.knowledge_engine = EvolutionKnowledgeDrivenFullLoopEngine(self.base_path)
        except ImportError as e:
            print(f"知识驱动引擎不可用: {e}")

        try:
            from evolution_execution_trend_analysis_engine import EvolutionExecutionTrendAnalysisEngine
            self.trend_engine = EvolutionExecutionTrendAnalysisEngine()
        except ImportError as e:
            print(f"趋势分析引擎不可用: {e}")

    def load_state(self) -> Dict[str, Any]:
        """加载引擎状态"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "version": self.version,
            "total_analysis": 0,
            "opportunities_discovered": 0,
            "solutions_generated": 0,
            "solutions_evaluated": 0,
            "evolutions_triggered": 0,
            "last_analysis": None
        }

    def save_state(self, state: Dict[str, Any]) -> None:
        """保存引擎状态"""
        state["last_updated"] = datetime.now().isoformat()
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def analyze_system_status(self) -> Dict[str, Any]:
        """
        分析系统当前状态

        Returns:
            系统状态分析结果
        """
        state = self.load_state()
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'engines': {},
            'evolution_history': {},
            'capabilities': {},
            'health': {}
        }

        # 分析已有引擎
        evolution_engines = list(SCRIPT_DIR.glob('evolution_*.py'))
        analysis['engines']['total_count'] = len(evolution_engines)
        analysis['engines']['recent_engines'] = [e.name for e in sorted(evolution_engines)[-10:]]

        # 分析进化历史
        try:
            completed_files = list(STATE_DIR.glob('evolution_completed_*.json'))
            completed_rounds = []

            for f in sorted(completed_files)[-20:]:
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        if data.get('status') == 'completed':
                            completed_rounds.append({
                                'round': data.get('loop_round'),
                                'goal': data.get('current_goal', ''),
                                'timestamp': data.get('updated_at', '')
                            })
                except Exception:
                    pass

            analysis['evolution_history']['recent_completed'] = completed_rounds
            analysis['evolution_history']['total_completed'] = len(completed_files)
        except Exception as e:
            print(f"分析进化历史失败: {e}")

        # 分析能力（从 capabilities.md 读取）
        try:
            capabilities_file = Path(self.base_path) / 'references' / 'capabilities.md'
            if capabilities_file.exists():
                with open(capabilities_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 统计能力数量
                    ability_count = len(re.findall(r'### \d+\.', content))
                    analysis['capabilities']['major_abilities'] = ability_count
        except Exception as e:
            print(f"分析能力文件失败: {e}")

        # 分析健康状态
        try:
            health_file = Path(STATE_DIR) / 'self_verify_result.json'
            if health_file.exists():
                with open(health_file, 'r', encoding='utf-8') as f:
                    health_data = json.load(f)
                    analysis['health']['passed'] = health_data.get('passed', 0)
                    analysis['health']['total'] = health_data.get('total', 0)
                    analysis['health']['score'] = round(health_data.get('passed', 0) / max(health_data.get('total', 1), 1) * 100, 1)
        except Exception:
            pass

        # 确保字段存在
        if 'total_analysis' not in state:
            state['total_analysis'] = 0
        state['total_analysis'] += 1
        state['last_analysis'] = datetime.now().isoformat()
        self.save_state(state)

        return analysis

    def discover_opportunities(self, analysis: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        从系统状态中发现创新机会

        Args:
            analysis: 系统状态分析结果（可选）

        Returns:
            发现的创新机会列表
        """
        if analysis is None:
            analysis = self.analyze_system_status()

        state = self.load_state()
        opportunities = []

        # 机会1：引擎数量已超400+ - 可以做跨引擎协同优化
        engine_count = analysis.get('engines', {}).get('total_count', 0)
        if engine_count > 300:
            opportunities.append({
                'id': 'opportunity_1',
                'type': 'cross_engine_collaboration',
                'title': f'跨{engine_count}引擎深度协同优化',
                'description': f'当前已有{engine_count}个进化引擎，可以深度分析引擎间的协同模式，识别跨引擎优化机会',
                'priority': 'high',
                'potential_impact': 0.85,
                'feasibility': 0.8,
                'source': 'engine_count_analysis'
            })

        # 机会2：检查进化历史是否有重复方向
        recent_completed = analysis.get('evolution_history', {}).get('recent_completed', [])
        if len(recent_completed) >= 5:
            # 分析最近进化方向的关键词
            keywords = []
            for item in recent_completed:
                goal = item.get('goal', '')
                # 提取关键词
                for kw in ['知识', '自动化', '驾驶舱', '集成', '优化', '触发', '决策', '执行']:
                    if kw in goal:
                        keywords.append(kw)

            # 统计关键词频率
            from collections import Counter
            kw_counts = Counter(keywords)
            most_common = kw_counts.most_common(1)
            if most_common and most_common[0][1] >= 3:
                opportunities.append({
                    'id': 'opportunity_2',
                    'type': 'evolution_diversity',
                    'title': '增加进化方向多样性',
                    'description': f'最近进化中"{most_common[0][0]}"关键词出现{most_common[0][1]}次，可能存在方向重复，建议探索新领域',
                    'priority': 'medium',
                    'potential_impact': 0.6,
                    'feasibility': 0.7,
                    'source': 'evolution_history_analysis'
                })

        # 机会3：健康分检查
        health_score = analysis.get('health', {}).get('score', 100)
        if health_score < 80:
            opportunities.append({
                'id': 'opportunity_3',
                'type': 'health_improvement',
                'title': f'系统健康分提升（当前{health_score}%）',
                'description': '系统健康分低于80%，建议分析低分原因并针对性优化',
                'priority': 'high',
                'potential_impact': 0.9,
                'feasibility': 0.85,
                'source': 'health_analysis'
            })

        # 机会4：自动化闭环增强
        opportunities.append({
            'id': 'opportunity_4',
            'type': 'full_automation',
            'title': '全流程自动化闭环增强',
            'description': '在现有知识驱动自动化基础上，进一步增强触发-执行-验证-学习的完整闭环',
            'priority': 'medium',
            'potential_impact': 0.75,
            'feasibility': 0.8,
            'source': 'trend_analysis'
        })

        # 机会5：元进化能力增强
        opportunities.append({
            'id': 'opportunity_5',
            'type': 'meta_evolution',
            'title': '元进化能力深度增强',
            'description': '让系统能够自主发现进化方法论中的优化空间，自动调整进化策略',
            'priority': 'medium',
            'potential_impact': 0.8,
            'feasibility': 0.65,
            'source': 'capability_analysis'
        })

        # 机会6：自主创新能力
        opportunities.append({
            'id': 'opportunity_6',
            'type': 'autonomous_innovation',
            'title': '主动创新实现能力增强',
            'description': '让系统能够主动发现"人类没想到但很有用"的新能力组合，生成创新工作流',
            'priority': 'high',
            'potential_impact': 0.9,
            'feasibility': 0.6,
            'source': 'innovation_potential'
        })

        # 只保留评分最高的前5个机会
        opportunities = sorted(opportunities, key=lambda x: x.get('potential_impact', 0) * 0.6 + x.get('feasibility', 0) * 0.4, reverse=True)[:5]

        # 保存机会
        self._save_opportunities(opportunities)

        state['opportunities_discovered'] = len(opportunities)
        self.save_state(state)

        return opportunities

    def generate_solutions(self, opportunities: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        为发现的机会生成创新解决方案

        Args:
            opportunities: 创新机会列表（可选）

        Returns:
            生成的解决方案列表
        """
        if opportunities is None:
            opportunities = self.discover_opportunities()

        state = self.load_state()
        solutions = []

        # 为每个机会生成解决方案
        for opportunity in opportunities:
            opp_type = opportunity.get('type', 'unknown')
            solutions_for_opp = []

            if opp_type == 'cross_engine_collaboration':
                solutions_for_opp = [
                    {
                        'id': f'solution_{opportunity["id"]}_1',
                        'opportunity_id': opportunity['id'],
                        'title': '跨引擎智能协同调度引擎',
                        'description': '创建统一的跨引擎协同调度引擎，自动分析任务需求，智能选择最优引擎组合，实现自适应任务分发',
                        'implementation_steps': [
                            '1. 分析现有引擎能力，建立能力矩阵',
                            '2. 设计协同调度算法',
                            '3. 实现任务分发与执行',
                            '4. 集成到 do.py 支持关键词触发'
                        ],
                        'expected_outcome': '提升跨引擎协作效率30%+',
                        'resources_needed': '中等',
                        'risk_level': 'low'
                    },
                    {
                        'id': f'solution_{opportunity["id"]}_2',
                        'opportunity_id': opportunity['id'],
                        'title': '引擎效能实时监控仪表盘',
                        'description': '创建统一的引擎效能监控面板，实时展示各引擎运行状态、性能指标、异常告警',
                        'implementation_steps': [
                            '1. 定义引擎效能指标',
                            '2. 实现实时数据采集',
                            '3. 创建可视化仪表盘',
                            '4. 集成到进化驾驶舱'
                        ],
                        'expected_outcome': '快速发现并定位引擎问题',
                        'resources_needed': '中低',
                        'risk_level': 'low'
                    }
                ]

            elif opp_type == 'evolution_diversity':
                solutions_for_opp = [
                    {
                        'id': f'solution_{opportunity["id"]}_1',
                        'opportunity_id': opportunity['id'],
                        'title': '创新方向探索引擎',
                        'description': '创建专门的创新方向探索引擎，从拟人化、LLM特有优势、前沿探索等维度主动发现新方向',
                        'implementation_steps': [
                            '1. 定义创新方向评估框架',
                            '2. 实现多维度创新机会扫描',
                            '3. 生成创新方案候选列表',
                            '4. 评估并推荐高价值方向'
                        ],
                        'expected_outcome': '发现更多元化的进化方向',
                        'resources_needed': '中等',
                        'risk_level': 'medium'
                    }
                ]

            elif opp_type == 'health_improvement':
                solutions_for_opp = [
                    {
                        'id': f'solution_{opportunity["id"]}_1',
                        'opportunity_id': opportunity['id'],
                        'title': '智能健康自愈增强引擎',
                        'description': '在现有健康监控基础上，增强自动诊断和自愈能力，实现问题自动发现-诊断-修复闭环',
                        'implementation_steps': [
                            '1. 增强问题诊断能力',
                            '2. 实现自动修复策略生成',
                            '3. 添加自动执行修复功能',
                            '4. 验证修复效果'
                        ],
                        'expected_outcome': '健康分提升至90%+',
                        'resources_needed': '中高',
                        'risk_level': 'medium'
                    }
                ]

            elif opp_type == 'full_automation':
                solutions_for_opp = [
                    {
                        'id': f'solution_{opportunity["id"]}_1',
                        'opportunity_id': opportunity['id'],
                        'title': '全自动进化闭环引擎',
                        'description': '增强从假设到反思的全流程自动化，实现真正的无人值守进化环',
                        'implementation_steps': [
                            '1. 增强假设阶段自动生成能力',
                            '2. 优化决策阶段智能选择',
                            '3. 增强执行阶段自动化',
                            '4. 完善验证和反思闭环'
                        ],
                        'expected_outcome': '进化环全自动化运行',
                        'resources_needed': '高',
                        'risk_level': 'medium'
                    }
                ]

            elif opp_type == 'meta_evolution':
                solutions_for_opp = [
                    {
                        'id': f'solution_{opportunity["id"]}_1',
                        'opportunity_id': opportunity['id'],
                        'title': '元进化策略自动优化引擎',
                        'description': '让系统能够自动分析进化方法论效率、识别优化空间、生成并执行优化策略',
                        'implementation_steps': [
                            '1. 建立方法论效率评估模型',
                            '2. 实现优化空间自动识别',
                            '3. 生成自适应优化策略',
                            '4. 验证并迭代优化效果'
                        ],
                        'expected_outcome': '进化方法论持续自我优化',
                        'resources_needed': '高',
                        'risk_level': 'high'
                    }
                ]

            elif opp_type == 'autonomous_innovation':
                solutions_for_opp = [
                    {
                        'id': f'solution_{opportunity["id"]}_1',
                        'opportunity_id': opportunity['id'],
                        'title': '主动创新工作流生成引擎',
                        'description': '基于对已有能力的深度理解，自动发现能力组合的创新用法，生成创新工作流',
                        'implementation_steps': [
                            '1. 建立能力组合分析模型',
                            '2. 实现创新机会自动发现',
                            '3. 生成创新工作流方案',
                            '4. 评估并验证创新价值'
                        ],
                        'expected_outcome': '持续发现"人类没想到"的能力组合',
                        'resources_needed': '高',
                        'risk_level': 'high'
                    }
                ]

            # 为没有特定解决方案的机会添加通用方案
            if not solutions_for_opp:
                solutions_for_opp = [
                    {
                        'id': f'solution_{opportunity["id"]}_generic',
                        'opportunity_id': opportunity['id'],
                        'title': f'针对"{opportunity.get("title", "unknown")}"的优化方案',
                        'description': opportunity.get('description', ''),
                        'implementation_steps': [
                            '1. 深入分析机会详情',
                            '2. 设计针对性解决方案',
                            '3. 实现并测试方案',
                            '4. 评估效果并迭代'
                        ],
                        'expected_outcome': '抓住创新机会',
                        'resources_needed': '待评估',
                        'risk_level': 'medium'
                    }
                ]

            solutions.extend(solutions_for_opp)

        # 保存解决方案
        self._save_solutions(solutions)

        state['solutions_generated'] = len(solutions)
        self.save_state(state)

        return solutions

    def evaluate_solutions(self, solutions: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        评估解决方案的价值

        Args:
            solutions: 解决方案列表（可选）

        Returns:
            评估结果列表
        """
        if solutions is None:
            solutions = self.generate_solutions()

        state = self.load_state()
        evaluations = []

        for solution in solutions:
            # 计算综合评分
            potential = solution.get('potential_impact', 0.5)
            feasibility = solution.get('feasibility', 0.5)

            # 风险调整
            risk_level = solution.get('risk_level', 'low')
            risk_adjustment = {'low': 1.0, 'medium': 0.8, 'high': 0.6}.get(risk_level, 0.7)

            # 资源需求调整
            resources = solution.get('resources_needed', '中等')
            resource_adjustment = {'低': 1.0, '中低': 0.9, '中等': 0.8, '中高': 0.6, '高': 0.4}.get(resources, 0.7)

            # 综合价值评分
            value_score = potential * 0.4 + feasibility * 0.3 + risk_adjustment * 0.15 + resource_adjustment * 0.15
            value_score = min(value_score, 1.0)

            evaluation = {
                'solution_id': solution['id'],
                'title': solution['title'],
                'value_score': round(value_score, 3),
                'potential_impact': potential,
                'feasibility': feasibility,
                'risk_level': risk_level,
                'resources_needed': resources,
                'priority_rank': 0,
                'recommendation': self._get_recommendation(value_score),
                'rationale': self._generate_rationale(solution, value_score)
            }

            evaluations.append(evaluation)

        # 按价值评分排序并分配优先级
        evaluations = sorted(evaluations, key=lambda x: x['value_score'], reverse=True)
        for i, ev in enumerate(evaluations):
            ev['priority_rank'] = i + 1

        # 保存评估结果
        self._save_evaluations(evaluations)

        state['solutions_evaluated'] = len(evaluations)
        self.save_state(state)

        return evaluations

    def trigger_evolution(self, solution_evaluation: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        将高价值解决方案转化为进化任务

        Args:
            solution_evaluation: 解决方案评估结果（可选）

        Returns:
            触发结果
        """
        if solution_evaluation is None:
            evaluations = self.evaluate_solutions()
            if evaluations:
                solution_evaluation = evaluations[0]  # 选择最高价值的方案
            else:
                return {'success': False, 'message': '无可触发方案'}

        state = self.load_state()

        # 构建进化任务
        evolution_task = {
            'triggered_at': datetime.now().isoformat(),
            'solution_id': solution_evaluation.get('solution_id'),
            'title': solution_evaluation.get('title'),
            'value_score': solution_evaluation.get('value_score'),
            'status': 'pending_execution',
            'round': self._get_current_round() + 1
        }

        # 保存到进化任务队列
        self._save_evolution_task(evolution_task)

        state['evolutions_triggered'] += 1
        self.save_state(state)

        return {
            'success': True,
            'message': f"已触发进化任务: {solution_evaluation.get('title')}",
            'task': evolution_task,
            'recommendation': solution_evaluation.get('recommendation')
        }

    def run_full_discovery_cycle(self) -> Dict[str, Any]:
        """
        运行完整的创新发现循环

        Returns:
            完整循环执行结果
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'phases': {},
            'success': True
        }

        # 阶段1：系统状态分析
        analysis = self.analyze_system_status()
        results['phases']['analysis'] = analysis

        # 阶段2：发现创新机会
        opportunities = self.discover_opportunities(analysis)
        results['phases']['opportunities'] = {
            'count': len(opportunities),
            'items': opportunities
        }

        # 阶段3：生成解决方案
        solutions = self.generate_solutions(opportunities)
        results['phases']['solutions'] = {
            'count': len(solutions),
            'items': solutions
        }

        # 阶段4：评估解决方案
        evaluations = self.evaluate_solutions(solutions)
        results['phases']['evaluations'] = {
            'count': len(evaluations),
            'top_solution': evaluations[0] if evaluations else None,
            'items': evaluations
        }

        # 阶段5：触发高价值进化
        if evaluations and evaluations[0].get('value_score', 0) > 0.6:
            trigger_result = self.trigger_evolution(evaluations[0])
            results['phases']['trigger'] = trigger_result

        return results

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        state = self.load_state()
        return {
            'version': self.version,
            'engine_status': 'active',
            'knowledge_engine_connected': self.knowledge_engine is not None,
            'trend_engine_connected': self.trend_engine is not None,
            'statistics': state
        }

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱数据"""
        state = self.load_state()

        opportunities = []
        evaluations = []

        if self.opportunities_file.exists():
            with open(self.opportunities_file, 'r', encoding='utf-8') as f:
                opportunities = json.load(f)

        if self.evaluations_file.exists():
            with open(self.evaluations_file, 'r', encoding='utf-8') as f:
                evaluations = json.load(f)

        return {
            'title': '创新机会自动发现与主动进化引擎',
            'version': self.version,
            'total_analysis': state.get('total_analysis', 0),
            'opportunities_discovered': state.get('opportunities_discovered', 0),
            'solutions_generated': state.get('solutions_generated', 0),
            'solutions_evaluated': state.get('solutions_evaluations', 0),
            'evolutions_triggered': state.get('evolutions_triggered', 0),
            'recent_opportunities': opportunities[:5] if opportunities else [],
            'top_evaluations': evaluations[:3] if evaluations else []
        }

    def get_opportunities(self, limit: int = 10) -> List[Dict]:
        """获取发现的创新机会"""
        if self.opportunities_file.exists():
            with open(self.opportunities_file, 'r', encoding='utf-8') as f:
                opportunities = json.load(f)
                return opportunities[:limit]
        return []

    def get_evaluations(self, limit: int = 10) -> List[Dict]:
        """获取解决方案评估结果"""
        if self.evaluations_file.exists():
            with open(self.evaluations_file, 'r', encoding='utf-8') as f:
                evaluations = json.load(f)
                return evaluations[:limit]
        return []

    def _get_current_round(self) -> int:
        """获取当前轮次"""
        mission_file = Path(STATE_DIR) / "current_mission.json"
        if mission_file.exists():
            try:
                with open(mission_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('loop_round', 462)
            except Exception:
                pass
        return 462

    def _get_recommendation(self, value_score: float) -> str:
        """根据价值评分获取推荐级别"""
        if value_score >= 0.8:
            return "强烈推荐 - 立即执行"
        elif value_score >= 0.6:
            return "推荐 - 尽快安排"
        elif value_score >= 0.4:
            return "可以考虑 - 后续安排"
        else:
            return "暂不推荐 - 观察为主"

    def _generate_rationale(self, solution: Dict, value_score: float) -> str:
        """生成评估理由"""
        rationale_parts = []
        rationale_parts.append(f"潜在影响力: {solution.get('potential_impact', 0.5) * 100:.0f}%")
        rationale_parts.append(f"可行性: {solution.get('feasibility', 0.5) * 100:.0f}%")
        rationale_parts.append(f"风险: {solution.get('risk_level', 'medium')}")
        return "; ".join(rationale_parts)

    def _save_opportunities(self, opportunities: List[Dict]) -> None:
        """保存创新机会"""
        try:
            with open(self.opportunities_file, 'w', encoding='utf-8') as f:
                json.dump(opportunities, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存创新机会失败: {e}")

    def _save_solutions(self, solutions: List[Dict]) -> None:
        """保存解决方案"""
        try:
            with open(self.solutions_file, 'w', encoding='utf-8') as f:
                json.dump(solutions, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存解决方案失败: {e}")

    def _save_evaluations(self, evaluations: List[Dict]) -> None:
        """保存评估结果"""
        try:
            with open(self.evaluations_file, 'w', encoding='utf-8') as f:
                json.dump(evaluations, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存评估结果失败: {e}")

    def _save_evolution_task(self, task: Dict) -> None:
        """保存进化任务"""
        task_file = Path(STATE_DIR) / "pending_evolution_tasks.json"
        tasks = []

        if task_file.exists():
            try:
                with open(task_file, 'r', encoding='utf-8') as f:
                    tasks = json.load(f)
            except Exception:
                pass

        tasks.append(task)
        tasks = tasks[-20:]  # 只保留最近20个

        try:
            with open(task_file, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存进化任务失败: {e}")


def main():
    """主函数 - 命令行入口"""
    parser = argparse.ArgumentParser(description='创新机会自动发现与主动进化引擎 v1.0.0')
    parser.add_argument('--status', action='store_true', help='显示引擎状态')
    parser.add_argument('--analyze', action='store_true', help='分析系统状态')
    parser.add_argument('--discover', action='store_true', help='发现创新机会')
    parser.add_argument('--generate', action='store_true', help='生成解决方案')
    parser.add_argument('--evaluate', action='store_true', help='评估解决方案')
    parser.add_argument('--trigger', action='store_true', help='触发高价值进化')
    parser.add_argument('--full-cycle', action='store_true', help='运行完整发现循环')
    parser.add_argument('--cockpit-data', action='store_true', help='获取驾驶舱数据')
    parser.add_argument('--opportunities', action='store_true', help='获取创新机会列表')
    parser.add_argument('--evaluations', action='store_true', help='获取评估结果')
    parser.add_argument('--limit', type=int, default=10, help='返回结果数量限制')

    args = parser.parse_args()

    engine = EvolutionInnovationOpportunityDiscoveryEngine()

    if args.status:
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.analyze:
        analysis = engine.analyze_system_status()
        print(json.dumps(analysis, ensure_ascii=False, indent=2))

    elif args.discover:
        opportunities = engine.discover_opportunities()
        print(json.dumps(opportunities, ensure_ascii=False, indent=2))

    elif args.generate:
        solutions = engine.generate_solutions()
        print(json.dumps(solutions, ensure_ascii=False, indent=2))

    elif args.evaluate:
        evaluations = engine.evaluate_solutions()
        print(json.dumps(evaluations, ensure_ascii=False, indent=2))

    elif args.trigger:
        result = engine.trigger_evolution()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.full_cycle:
        result = engine.run_full_discovery_cycle()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))

    elif args.opportunities:
        opportunities = engine.get_opportunities(args.limit)
        print(json.dumps(opportunities, ensure_ascii=False, indent=2))

    elif args.evaluations:
        evaluations = engine.get_evaluations(args.limit)
        print(json.dumps(evaluations, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == '__main__':
    main()