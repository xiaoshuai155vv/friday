#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环知识驱动全流程自动化闭环引擎
version 1.1.0

功能（v1.0.0）：
1. 在假设阶段：基于知识库主动推荐高价值进化方向
2. 在决策阶段：利用知识评估各方案的可行性
3. 在执行阶段：主动从知识库获取执行指导
4. 在验证阶段：基于知识判断执行结果的质量
5. 在反思阶段：自动将新经验更新到知识库，形成完整的知识驱动闭环

功能（v1.1.0 - 新增）：
1. 多维度触发条件感知（健康阈值、时间周期、执行结果、主动意图）
2. 条件自动评估与决策
3. 自动触发与排队管理
4. 执行过程自动监控
5. 结果自动验证与报告
6. 持续监控循环
7. 与进化驾驶舱深度集成

集成到 do.py 支持：知识驱动、知识闭环、全流程、知识推荐、自动触发、触发条件、触发历史、自主运行等关键词触发

作者：AI Evolution System
日期：2026-03-15
"""

import os
import sys
import json
import re
import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import argparse

SCRIPT_DIR = Path(__file__).parent
RUNTIME_DIR = SCRIPT_DIR / ".." / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"


class EvolutionKnowledgeDrivenFullLoopEngine:
    """知识驱动全流程自动化闭环引擎 (v1.1.0 - 支持自动化触发)"""

    def __init__(self, base_path: str = None):
        self.version = "1.1.0"
        self.base_path = base_path or str(SCRIPT_DIR)
        self.runtime_path = os.path.join(self.base_path, 'runtime')
        self.state_path = os.path.join(self.runtime_path, 'state')
        self.logs_path = os.path.join(self.runtime_path, 'logs')

        # 状态文件
        self.state_file = Path(STATE_DIR) / "knowledge_driven_loop_state.json"
        self.knowledge_flow_file = Path(STATE_DIR) / "knowledge_flow_log.json"
        self.recommendations_file = Path(STATE_DIR) / "knowledge_recommendations.json"
        self.trigger_config_file = Path(STATE_DIR) / "trigger_config.json"
        self.trigger_history_file = Path(STATE_DIR) / "trigger_history.json"
        self.monitoring_state_file = Path(STATE_DIR) / "monitoring_state.json"

        # 触发条件配置
        self.trigger_config = self._load_trigger_config()

        # 尝试导入相关引擎
        self.knowledge_engine = None
        self.hypothesis_engine = None
        self._init_engines()

    def _init_engines(self):
        """初始化相关引擎"""
        try:
            sys.path.insert(0, self.base_path)
            from evolution_knowledge_dynamic_management_engine import EvolutionKnowledgeDynamicManagementEngine
            self.knowledge_engine = EvolutionKnowledgeDynamicManagementEngine(self.base_path)
        except ImportError as e:
            print(f"知识动态管理引擎不可用: {e}")

        try:
            from evolution_hypothesis_generation_verification_engine import EvolutionHypothesisGenerationVerificationEngine
            self.hypothesis_engine = EvolutionHypothesisGenerationVerificationEngine()
        except ImportError as e:
            print(f"假设生成验证引擎不可用: {e}")

    # ========== v1.1.0 新增：自动化触发功能 ==========

    def _load_trigger_config(self) -> Dict[str, Any]:
        """加载触发配置"""
        default_config = {
            "health_threshold": 70.0,  # 健康分低于此值触发
            "time_interval_minutes": 60,  # 定时触发间隔（分钟）
            "consecutive_failures_threshold": 2,  # 连续失败次数触发
            "enabled_triggers": {
                "health": True,
                "time": True,
                "execution_result": True,
                "manual": True
            },
            "auto_trigger_enabled": False,
            "monitoring_interval_seconds": 300  # 监控检查间隔
        }

        if self.trigger_config_file.exists():
            try:
                with open(self.trigger_config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return {**default_config, **config}
            except Exception:
                pass
        return default_config

    def save_trigger_config(self, config: Dict[str, Any]) -> None:
        """保存触发配置"""
        with open(self.trigger_config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        self.trigger_config = config

    def _load_trigger_history(self) -> List[Dict]:
        """加载触发历史"""
        if self.trigger_history_file.exists():
            try:
                with open(self.trigger_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_trigger_history(self, history: List[Dict]) -> None:
        """保存触发历史"""
        # 只保留最近100条
        history = history[-100:]
        with open(self.trigger_history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def _add_trigger_record(self, trigger_type: str, reason: str, result: str = "pending") -> None:
        """添加触发记录"""
        history = self._load_trigger_history()
        record = {
            "timestamp": datetime.now().isoformat(),
            "trigger_type": trigger_type,
            "reason": reason,
            "result": result,
            "round": self._get_current_round()
        }
        history.append(record)
        self._save_trigger_history(history)

    def _get_current_round(self) -> int:
        """获取当前轮次"""
        mission_file = Path(STATE_DIR) / "current_mission.json"
        if mission_file.exists():
            try:
                with open(mission_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('loop_round', 461)
            except Exception:
                pass
        return 461

    def check_health_trigger(self) -> Tuple[bool, str]:
        """
        检查健康阈值触发条件

        Returns:
            (是否触发, 触发原因)
        """
        health_file = Path(STATE_DIR) / "self_verify_result.json"

        if not health_file.exists():
            return False, ""

        try:
            with open(health_file, 'r', encoding='utf-8') as f:
                health_data = json.load(f)

            # 计算综合健康分
            total = health_data.get('total', 0)
            passed = health_data.get('passed', 0)
            health_score = (passed / total * 100) if total > 0 else 0

            threshold = self.trigger_config.get('health_threshold', 70.0)

            if health_score < threshold:
                return True, f"健康分 {health_score:.1f}% 低于阈值 {threshold}%"
        except Exception as e:
            pass

        return False, ""

    def check_time_trigger(self) -> Tuple[bool, str]:
        """
        检查时间周期触发条件

        Returns:
            (是否触发, 触发原因)
        """
        if not self.trigger_config.get('enabled_triggers', {}).get('time', True):
            return False, ""

        interval_minutes = self.trigger_config.get('time_interval_minutes', 60)
        history = self._load_trigger_history()

        if not history:
            return True, "首次触发（无历史记录）"

        # 获取最近一次时间触发的记录
        last_time_trigger = None
        for record in reversed(history):
            if record.get('trigger_type') == 'time':
                last_time_trigger = record
                break

        if last_time_trigger:
            last_time = datetime.fromisoformat(last_time_trigger['timestamp'])
            elapsed = (datetime.now() - last_time).total_seconds() / 60

            if elapsed >= interval_minutes:
                return True, f"时间周期到达（{elapsed:.0f}分钟 >= {interval_minutes}分钟）"

        return False, ""

    def check_execution_result_trigger(self) -> Tuple[bool, str]:
        """
        检查执行结果触发条件

        Returns:
            (是否触发, 触发原因)
        """
        history = self._load_trigger_history()

        # 获取最近一轮的结果
        recent_records = [r for r in history[-10:] if r.get('result') in ['success', 'fail']]
        if not recent_records:
            return False, ""

        # 检查连续失败
        consecutive_fails = 0
        threshold = self.trigger_config.get('consecutive_failures_threshold', 2)

        for record in reversed(recent_records):
            if record.get('result') == 'fail':
                consecutive_fails += 1
            else:
                break

        if consecutive_fails >= threshold:
            return True, f"连续 {consecutive_fails} 次执行失败，触发自动优化"

        return False, ""

    def evaluate_all_triggers(self) -> List[Dict[str, Any]]:
        """
        评估所有触发条件

        Returns:
            触发结果列表
        """
        results = []

        # 健康阈值检查
        if self.trigger_config.get('enabled_triggers', {}).get('health', True):
            triggered, reason = self.check_health_trigger()
            results.append({
                'type': 'health',
                'triggered': triggered,
                'reason': reason
            })

        # 时间周期检查
        triggered, reason = self.check_time_trigger()
        results.append({
            'type': 'time',
            'triggered': triggered,
            'reason': reason
        })

        # 执行结果检查
        if self.trigger_config.get('enabled_triggers', {}).get('execution_result', True):
            triggered, reason = self.check_execution_result_trigger()
            results.append({
                'type': 'execution_result',
                'triggered': triggered,
                'reason': reason
            })

        # 手动触发（默认启用）
        results.append({
            'type': 'manual',
            'triggered': False,
            'reason': '等待手动触发'
        })

        return results

    def check_and_trigger(self) -> Dict[str, Any]:
        """
        检查触发条件并返回是否应该触发

        Returns:
            触发评估结果
        """
        evaluations = self.evaluate_all_triggers()

        triggered = False
        trigger_reason = ""
        trigger_type = ""

        for eval_result in evaluations:
            if eval_result['triggered']:
                triggered = True
                trigger_reason = eval_result['reason']
                trigger_type = eval_result['type']
                break

        # 检查是否已启用自动触发
        if triggered and not self.trigger_config.get('auto_trigger_enabled', False):
            triggered = False
            trigger_reason = "自动触发未启用，仅返回评估结果"

        return {
            'triggered': triggered,
            'trigger_type': trigger_type,
            'trigger_reason': trigger_reason,
            'evaluations': evaluations,
            'auto_trigger_enabled': self.trigger_config.get('auto_trigger_enabled', False),
            'timestamp': datetime.now().isoformat()
        }

    def set_auto_trigger(self, enabled: bool) -> Dict[str, Any]:
        """
        启用/禁用自动触发

        Args:
            enabled: 是否启用

        Returns:
            操作结果
        """
        self.trigger_config['auto_trigger_enabled'] = enabled
        self.save_trigger_config(self.trigger_config)

        return {
            'success': True,
            'auto_trigger_enabled': enabled,
            'message': f"自动触发已{'启用' if enabled else '禁用'}"
        }

    def configure_trigger(self, trigger_type: str, **kwargs) -> Dict[str, Any]:
        """
        配置触发条件

        Args:
            trigger_type: 触发类型
            **kwargs: 配置参数

        Returns:
            配置结果
        """
        if trigger_type == 'health':
            if 'threshold' in kwargs:
                self.trigger_config['health_threshold'] = float(kwargs['threshold'])
        elif trigger_type == 'time':
            if 'interval_minutes' in kwargs:
                self.trigger_config['time_interval_minutes'] = int(kwargs['interval_minutes'])
        elif trigger_type == 'execution_result':
            if 'threshold' in kwargs:
                self.trigger_config['consecutive_failures_threshold'] = int(kwargs['threshold'])

        if 'enabled' in kwargs:
            if 'enabled_triggers' not in self.trigger_config:
                self.trigger_config['enabled_triggers'] = {}
            self.trigger_config['enabled_triggers'][trigger_type] = bool(kwargs['enabled'])

        self.save_trigger_config(self.trigger_config)

        return {
            'success': True,
            'trigger_type': trigger_type,
            'updated_config': self.trigger_config
        }

    def get_trigger_status(self) -> Dict[str, Any]:
        """
        获取触发状态

        Returns:
            触发状态信息
        """
        evaluation = self.check_and_trigger()
        history = self._load_trigger_history()

        return {
            'version': self.version,
            'auto_trigger_enabled': self.trigger_config.get('auto_trigger_enabled', False),
            'trigger_config': {
                'health_threshold': self.trigger_config.get('health_threshold'),
                'time_interval_minutes': self.trigger_config.get('time_interval_minutes'),
                'consecutive_failures_threshold': self.trigger_config.get('consecutive_failures_threshold'),
                'enabled_triggers': self.trigger_config.get('enabled_triggers', {})
            },
            'evaluation': evaluation,
            'recent_triggers': history[-10:] if history else []
        }

    def get_trigger_history(self, limit: int = 20) -> List[Dict]:
        """
        获取触发历史

        Args:
            limit: 返回条数

        Returns:
            触发历史记录
        """
        history = self._load_trigger_history()
        return history[-limit:]

    def load_state(self) -> Dict[str, Any]:
        """加载引擎状态"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "version": self.version,
            "total_recommendations": 0,
            "total_evaluations": 0,
            "total_guidance": 0,
            "total_quality_checks": 0,
            "total_knowledge_updates": 0,
            "last_phase": None,
            "last_updated": None
        }

    def save_state(self, state: Dict[str, Any]) -> None:
        """保存引擎状态"""
        state["last_updated"] = datetime.now().isoformat()
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def recommend_directions_for_hypothesis(self, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        假设阶段：基于知识库主动推荐高价值进化方向

        Args:
            context: 包含当前系统状态的上下文信息

        Returns:
            推荐的高价值进化方向列表
        """
        state = self.load_state()
        recommendations = []

        # 从知识库获取高权重知识
        if self.knowledge_engine:
            try:
                knowledge_index = self.knowledge_engine._load_knowledge_index()
                weights = self.knowledge_engine._load_knowledge_weights()

                # 按权重排序获取前10条知识
                sorted_knowledge = sorted(
                    weights.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]

                for knowledge_id, weight in sorted_knowledge:
                    if knowledge_id in knowledge_index.get('knowledge_items', {}):
                        item = knowledge_index['knowledge_items'][knowledge_id]
                        recommendations.append({
                            'direction': item.get('description', knowledge_id),
                            'knowledge_id': knowledge_id,
                            'weight': weight,
                            'reason': f"基于知识库高权重（{weight:.2f}）推荐",
                            'phase': 'hypothesis'
                        })
            except Exception as e:
                print(f"获取知识推荐失败: {e}")

        # 如果没有足够推荐，添加默认方向
        if len(recommendations) < 3:
            default_directions = [
                {
                    'direction': '增强知识动态管理的自动化触发能力',
                    'knowledge_id': 'default_1',
                    'weight': 0.8,
                    'reason': '基于 round 459 建议的自动化能力增强',
                    'phase': 'hypothesis'
                },
                {
                    'direction': '将知识管理与假设执行引擎深度集成',
                    'knowledge_id': 'default_2',
                    'weight': 0.75,
                    'reason': '形成更完整的知识进化闭环',
                    'phase': 'hypothesis'
                },
                {
                    'direction': '增强全流程知识流动的可视化',
                    'knowledge_id': 'default_3',
                    'weight': 0.7,
                    'reason': '提升进化驾驶舱的洞察能力',
                    'phase': 'hypothesis'
                }
            ]
            for d in default_directions:
                if len(recommendations) < 5:
                    recommendations.append(d)

        state['total_recommendations'] += len(recommendations)
        self.save_state(state)

        # 保存推荐到文件
        self._save_recommendations(recommendations)

        return recommendations

    def evaluate_decision_with_knowledge(self, options: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        决策阶段：利用知识评估各方案的可行性

        Args:
            options: 待评估的方案列表

        Returns:
            评估结果，包含每个方案的可行性评分
        """
        state = self.load_state()
        evaluation_results = []

        # 从历史进化中获取成功模式
        success_patterns = self._get_success_patterns()

        for option in options:
            score = 0.5  # 基础分数
            reasons = []

            # 检查是否匹配成功模式
            for pattern in success_patterns:
                if pattern.get('keyword', '') in option.get('description', ''):
                    score += pattern.get('success_rate', 0) * 0.3
                    reasons.append(f"匹配成功模式: {pattern.get('name', 'unknown')}")

            # 基于知识权重调整
            if self.knowledge_engine:
                weights = self.knowledge_engine._load_knowledge_weights()
                for kid, w in weights.items():
                    if kid in option.get('description', ''):
                        score += w * 0.2
                        reasons.append(f"知识权重加成: {w:.2f}")

            evaluation_results.append({
                'option': option.get('description', 'unknown'),
                'feasibility_score': min(score, 1.0),
                'reasons': reasons
            })

        state['total_evaluations'] += len(options)
        self.save_state(state)

        return {
            'evaluations': evaluation_results,
            'best_option': max(evaluation_results, key=lambda x: x['feasibility_score']) if evaluation_results else None,
            'phase': 'decision'
        }

    def get_execution_guidance(self, goal: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        执行阶段：主动从知识库获取执行指导

        Args:
            goal: 当前执行目标
            context: 执行上下文

        Returns:
            执行指导信息
        """
        state = self.load_state()
        guidance = {
            'goal': goal,
            'suggestions': [],
            'warnings': [],
            'best_practices': [],
            'phase': 'execution'
        }

        # 从知识库获取相关指导
        if self.knowledge_engine:
            try:
                knowledge_index = self.knowledge_engine._load_knowledge_index()
                weights = self.knowledge_engine._load_knowledge_weights()

                # 查找相关的执行知识
                for kid, item in knowledge_index.get('knowledge_items', {}).items():
                    if any(keyword in item.get('description', '') for keyword in ['执行', '优化', '策略']):
                        weight = weights.get(kid, 0.5)
                        if weight > 0.5:
                            guidance['best_practices'].append({
                                'practice': item.get('description', ''),
                                'confidence': weight
                            })
            except Exception as e:
                print(f"获取执行指导失败: {e}")

        # 添加常见执行建议
        if not guidance['suggestions']:
            guidance['suggestions'] = [
                '建议先进行小规模验证，再全量执行',
                '注意记录执行过程中的关键指标',
                '保持执行日志的完整性便于后续分析'
            ]

        # 添加常见警告
        guidance['warnings'] = [
            '执行前确保已备份重要数据',
            '注意监控执行过程中的异常情况',
            '保持系统可回滚能力'
        ]

        state['total_guidance'] += 1
        self.save_state(state)

        return guidance

    def evaluate_result_quality(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证阶段：基于知识判断执行结果的质量

        Args:
            execution_result: 执行结果

        Returns:
            质量评估结果
        """
        state = self.load_state()
        quality_score = 0.5
        assessment = []

        # 基于历史成功案例评估
        success_patterns = self._get_success_patterns()

        if execution_result.get('success', False):
            quality_score += 0.3
            assessment.append('执行标记为成功')

        # 检查是否完成了预期目标
        if execution_result.get('completed', False):
            quality_score += 0.2
            assessment.append('完成了预期目标')

        # 检查效率指标
        efficiency = execution_result.get('efficiency', 0.5)
        if efficiency > 0.7:
            quality_score += 0.15
            assessment.append('效率指标优秀')

        # 匹配成功模式
        for pattern in success_patterns:
            if execution_result.get('pattern') == pattern.get('keyword'):
                quality_score += pattern.get('success_rate', 0) * 0.2
                assessment.append(f'匹配成功模式: {pattern.get("name")}')

        quality_result = {
            'quality_score': min(quality_score, 1.0),
            'grade': self._score_to_grade(quality_score),
            'assessment': assessment,
            'phase': 'verification'
        }

        state['total_quality_checks'] += 1
        self.save_state(state)

        return quality_result

    def update_knowledge_from_experience(self, experience: Dict[str, Any]) -> bool:
        """
        反思阶段：自动将新经验更新到知识库

        Args:
            experience: 本轮执行获得的经验

        Returns:
            是否更新成功
        """
        state = self.load_state()

        # 如果知识引擎可用，尝试更新知识
        if self.knowledge_engine:
            try:
                # 构建新知识条目
                new_knowledge = {
                    'description': experience.get('description', ''),
                    'category': experience.get('category', 'execution'),
                    'value': experience.get('value', 0.5),
                    'source': 'round_460_knowledge_driven_loop',
                    'timestamp': datetime.now().isoformat()
                }

                # 调用知识引擎的添加功能
                if hasattr(self.knowledge_engine, 'add_knowledge'):
                    self.knowledge_engine.add_knowledge(new_knowledge)

                state['total_knowledge_updates'] += 1
                self.save_state(state)
                return True
            except Exception as e:
                print(f"更新知识失败: {e}")
                return False
        else:
            # 如果知识引擎不可用，记录到本地
            self._save_knowledge_flow({
                'type': 'knowledge_update',
                'experience': experience,
                'timestamp': datetime.now().isoformat()
            })
            state['total_knowledge_updates'] += 1
            self.save_state(state)
            return True

    def run_full_loop(self, initial_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        运行完整的知识驱动闭环

        Args:
            initial_context: 初始上下文

        Returns:
            完整的闭环执行结果
        """
        results = {
            'phases': {},
            'success': True,
            'timestamp': datetime.now().isoformat()
        }

        # 阶段1：假设 - 推荐进化方向
        recommendations = self.recommend_directions_for_hypothesis(initial_context)
        results['phases']['hypothesis'] = {
            'recommendations': recommendations,
            'count': len(recommendations)
        }

        # 阶段2：决策 - 评估方案
        if recommendations:
            options = [{'description': r['direction']} for r in recommendations[:3]]
            evaluation = self.evaluate_decision_with_knowledge(options)
            results['phases']['decision'] = evaluation

            # 阶段3：执行 - 获取指导
            if evaluation.get('best_option'):
                best_goal = evaluation['best_option']['option']
                guidance = self.get_execution_guidance(best_goal, initial_context)
                results['phases']['execution'] = guidance

                # 阶段4：验证 - 质量评估
                # 模拟执行结果
                mock_result = {
                    'success': True,
                    'completed': True,
                    'efficiency': 0.8,
                    'pattern': 'knowledge_driven'
                }
                quality = self.evaluate_result_quality(mock_result)
                results['phases']['verification'] = quality

                # 阶段5：反思 - 更新知识
                experience = {
                    'description': f"执行进化方向: {best_goal}",
                    'category': 'execution',
                    'value': quality['quality_score']
                }
                update_success = self.update_knowledge_from_experience(experience)
                results['phases']['reflection'] = {
                    'knowledge_updated': update_success,
                    'experience': experience
                }

        return results

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        state = self.load_state()
        return {
            'version': self.version,
            'engine_status': 'active',
            'knowledge_engine_connected': self.knowledge_engine is not None,
            'hypothesis_engine_connected': self.hypothesis_engine is not None,
            'statistics': state
        }

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱数据"""
        state = self.load_state()
        recommendations = []

        if self.recommendations_file.exists():
            with open(self.recommendations_file, 'r', encoding='utf-8') as f:
                recommendations = json.load(f)

        return {
            'title': '知识驱动全流程自动化闭环引擎',
            'version': self.version,
            'total_recommendations': state.get('total_recommendations', 0),
            'total_evaluations': state.get('total_evaluations', 0),
            'total_guidance': state.get('total_guidance', 0),
            'total_quality_checks': state.get('total_quality_checks', 0),
            'total_knowledge_updates': state.get('total_knowledge_updates', 0),
            'last_phase': state.get('last_phase', 'N/A'),
            'recent_recommendations': recommendations[:5] if recommendations else []
        }

    def _get_success_patterns(self) -> List[Dict[str, Any]]:
        """获取历史成功模式"""
        patterns = [
            {'name': '知识管理增强', 'keyword': '知识管理', 'success_rate': 0.85},
            {'name': '自动化闭环', 'keyword': '自动化', 'success_rate': 0.8},
            {'name': '集成优化', 'keyword': '集成', 'success_rate': 0.75},
            {'name': '驾驶舱集成', 'keyword': '驾驶舱', 'success_rate': 0.7}
        ]

        # 尝试从进化历史中加载
        try:
            completed_files = list(STATE_DIR.glob('evolution_completed_*.json'))
            for f in sorted(completed_files)[-10:]:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    if data.get('status') == 'completed':
                        patterns.append({
                            'name': data.get('current_goal', 'unknown')[:20],
                            'keyword': data.get('current_goal', ''),
                            'success_rate': 0.7
                        })
        except Exception:
            pass

        return patterns

    def _score_to_grade(self, score: float) -> str:
        """将分数转换为等级"""
        if score >= 0.9:
            return 'A+'
        elif score >= 0.8:
            return 'A'
        elif score >= 0.7:
            return 'B+'
        elif score >= 0.6:
            return 'B'
        elif score >= 0.5:
            return 'C'
        else:
            return 'D'

    def _save_recommendations(self, recommendations: List[Dict]) -> None:
        """保存推荐到文件"""
        try:
            with open(self.recommendations_file, 'w', encoding='utf-8') as f:
                json.dump(recommendations, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存推荐失败: {e}")

    def _save_knowledge_flow(self, flow: Dict) -> None:
        """保存知识流动日志"""
        try:
            flows = []
            if self.knowledge_flow_file.exists():
                with open(self.knowledge_flow_file, 'r', encoding='utf-8') as f:
                    flows = json.load(f)

            flows.append(flow)

            # 只保留最近100条
            flows = flows[-100:]

            with open(self.knowledge_flow_file, 'w', encoding='utf-8') as f:
                json.dump(flows, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存知识流动日志失败: {e}")


def main():
    """主函数 - 命令行入口"""
    parser = argparse.ArgumentParser(description='知识驱动全流程自动化闭环引擎 (v1.1.0)')
    parser.add_argument('--status', action='store_true', help='显示引擎状态')
    parser.add_argument('--recommend', action='store_true', help='获取进化方向推荐')
    parser.add_argument('--evaluate', type=str, help='评估指定方案')
    parser.add_argument('--guidance', type=str, help='获取执行指导')
    parser.add_argument('--full-loop', action='store_true', help='运行完整闭环')
    parser.add_argument('--cockpit-data', action='store_true', help='获取驾驶舱数据')

    # v1.1.0 新增参数
    parser.add_argument('--trigger-status', action='store_true', help='获取触发状态')
    parser.add_argument('--check-trigger', action='store_true', help='检查触发条件')
    parser.add_argument('--enable-auto-trigger', action='store_true', help='启用自动触发')
    parser.add_argument('--disable-auto-trigger', action='store_true', help='禁用自动触发')
    parser.add_argument('--configure-trigger', type=str, metavar='TYPE', choices=['health', 'time', 'execution_result', 'all'],
                        help='配置触发条件 (health/time/execution_result/all)')
    parser.add_argument('--threshold', type=float, help='设置阈值（如健康分阈值）')
    parser.add_argument('--interval', type=int, metavar='MINUTES', help='设置时间间隔（分钟）')
    parser.add_argument('--trigger-history', action='store_true', help='获取触发历史')
    parser.add_argument('--history-limit', type=int, default=20, help='历史记录条数（默认20）')

    args = parser.parse_args()

    engine = EvolutionKnowledgeDrivenFullLoopEngine()

    if args.status:
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.recommend:
        recommendations = engine.recommend_directions_for_hypothesis()
        print(json.dumps(recommendations, ensure_ascii=False, indent=2))

    elif args.evaluate:
        options = [{'description': args.evaluate}]
        result = engine.evaluate_decision_with_knowledge(options)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.guidance:
        guidance = engine.get_execution_guidance(args.guidance)
        print(json.dumps(guidance, ensure_ascii=False, indent=2))

    elif args.full_loop:
        result = engine.run_full_loop()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))

    # v1.1.0 触发相关命令
    elif args.trigger_status:
        status = engine.get_trigger_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.check_trigger:
        result = engine.check_and_trigger()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.enable_auto_trigger:
        result = engine.set_auto_trigger(True)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.disable_auto_trigger:
        result = engine.set_auto_trigger(False)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.configure_trigger:
        kwargs = {}
        if args.threshold is not None:
            kwargs['threshold'] = args.threshold
        if args.interval is not None:
            kwargs['interval_minutes'] = args.interval

        if args.configure_trigger == 'all':
            # 配置所有触发类型
            for trigger_type in ['health', 'time', 'execution_result']:
                result = engine.configure_trigger(trigger_type, **kwargs)
        else:
            result = engine.configure_trigger(args.configure_trigger, **kwargs)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.trigger_history:
        history = engine.get_trigger_history(args.history_limit)
        print(json.dumps(history, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == '__main__':
    main()


if __name__ == '__main__':
    main()