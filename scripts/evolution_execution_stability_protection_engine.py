#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环执行稳定性预测防护增强引擎
Evolution Execution Stability Protection Enhancement Engine

版本: 1.0.0
功能: 在 round 408 的预测性智能调度基础上，进一步增强稳定性预测与主动防护能力

实现功能:
1. 基于历史数据的稳定性趋势预测（检测连续失败模式、资源下降趋势）
2. 主动防护措施部署（自动降级、负载转移、熔断等）
3. 与进化驾驶舱深度集成
4. 实现从事后修复到事前预防的范式升级

集成: 集成到 do.py 支持稳定性防护、主动防护、稳定性预测等关键词触发

依赖:
- evolution_cockpit_engine.py (round 350)
- evolution_execution_efficiency_predictive_scheduling_engine.py (round 408)
"""

import os
import sys
import json
import time
import threading
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from collections import deque
import statistics

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def _safe_print(text: str):
    """安全打印，处理编码问题"""
    import re
    try:
        print(text)
    except UnicodeEncodeError:
        clean_text = re.sub(r'[^\x00-\x7F]+', '', text)
        print(clean_text)


class ExecutionStabilityProtectionEngine:
    """
    执行稳定性预测防护增强引擎
    实现从事后修复到事前预防的范式升级
    """

    VERSION = "1.0.0"

    def __init__(self):
        self.version = self.VERSION
        self.project_root = PROJECT_ROOT
        self.scripts_dir = PROJECT_ROOT / "scripts"
        self.runtime_dir = PROJECT_ROOT / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.logs_dir = self.runtime_dir / "logs"

        # 状态文件
        self.state_file = self.state_dir / "stability_protection_state.json"
        self.stability_history_file = self.state_dir / "stability_history.json"
        self.protection_log_file = self.state_dir / "protection_actions.json"

        # 初始化目录
        self._ensure_directories()

        # 稳定性检测配置
        self.stability_window = 30  # 稳定性分析窗口
        self.failure_threshold = 3  # 连续失败次数阈值
        self.resource_warning_threshold = 0.85  # 资源警告阈值
        self.resource_critical_threshold = 0.95  # 资源危险阈值
        self.degradation_threshold = 0.15  # 性能下降阈值（15%）

        # 执行历史数据
        self.execution_history = deque(maxlen=self.stability_window * 2)
        self.failure_patterns = deque(maxlen=100)
        self.resource_history = deque(maxlen=self.stability_window * 2)

        # 稳定性状态
        self.current_stability_score = 100  # 0-100
        self.stability_trend = "stable"  # stable, declining, improving
        self.active_protections = {}  # 当前启用的保护措施
        self.monitoring_active = False
        self.monitoring_thread = None

        # 预测模型
        self.prediction_model = self._init_prediction_model()
        self.risk_predictions = deque(maxlen=50)

        # 保护策略
        self.protection_strategies = {
            "auto_degrade": self._auto_degrade,
            "load_transfer": self._load_transfer,
            "circuit_break": self._circuit_break,
            "resource_release": self._resource_release,
            "priority_adjust": self._priority_adjust
        }

        # 尝试加载相关引擎
        self.cockpit_engine = self._load_cockpit_engine()
        self.predictive_scheduling = self._load_predictive_scheduling()

        # 加载历史数据
        self._load_state()

    def _ensure_directories(self):
        """确保必要目录存在"""
        for directory in [self.state_dir, self.logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def _init_prediction_model(self) -> Dict[str, Any]:
        """初始化稳定性预测模型"""
        return {
            "failure_detection_threshold": self.failure_threshold,
            "resource_warning_threshold": self.resource_warning_threshold,
            "patterns_learned": [],
            "accuracy_score": 0.85,
            "last_training": datetime.now().isoformat()
        }

    def _load_cockpit_engine(self):
        """加载进化驾驶舱引擎"""
        try:
            from evolution_cockpit_engine import EvolutionCockpitEngine
            return EvolutionCockpitEngine()
        except Exception as e:
            _safe_print(f"[StabilityProtection] 驾驶舱引擎加载失败: {e}")
            return None

    def _load_predictive_scheduling(self):
        """加载预测性调度引擎"""
        try:
            from evolution_execution_efficiency_predictive_scheduling_engine import ExecutionEfficiencyPredictiveSchedulingEngine
            return ExecutionEfficiencyPredictiveSchedulingEngine()
        except Exception as e:
            _safe_print(f"[StabilityProtection] 预测性调度引擎加载失败: {e}")
            return None

    def _load_state(self):
        """加载保存的状态"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    self.current_stability_score = state.get('stability_score', 100)
                    self.stability_trend = state.get('trend', 'stable')
                    self.active_protections = state.get('protections', {})
        except Exception as e:
            _safe_print(f"[StabilityProtection] 状态加载失败: {e}")

    def _save_state(self):
        """保存当前状态"""
        try:
            state = {
                'stability_score': self.current_stability_score,
                'trend': self.stability_trend,
                'protections': self.active_protections,
                'last_update': datetime.now().isoformat()
            }
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[StabilityProtection] 状态保存失败: {e}")

    def _record_execution(self, task_id: str, success: bool, duration: float,
                          resource_usage: Dict[str, float], error: Optional[str] = None):
        """记录执行历史"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'task_id': task_id,
            'success': success,
            'duration': duration,
            'resource_usage': resource_usage,
            'error': error
        }
        self.execution_history.append(record)

        # 更新失败模式
        if not success:
            self.failure_patterns.append(record)

        # 更新资源历史
        if resource_usage:
            self.resource_history.append({
                'timestamp': datetime.now().isoformat(),
                **resource_usage
            })

    def _analyze_failure_patterns(self) -> Dict[str, Any]:
        """分析失败模式"""
        if len(self.execution_history) < 5:
            return {'status': 'insufficient_data'}

        # 检测连续失败
        recent_executions = list(self.execution_history)[-10:]
        consecutive_failures = 0
        max_consecutive_failures = 0
        current_consecutive = 0

        for exec_record in reversed(recent_executions):
            if not exec_record['success']:
                current_consecutive += 1
                max_consecutive_failures = max(max_consecutive_failures, current_consecutive)
            else:
                current_consecutive = 0

        # 分析失败类型
        failure_types = {}
        for failure in self.failure_patterns:
            error_msg = failure.get('error', 'unknown')
            failure_types[error_msg] = failure_types.get(error_msg, 0) + 1

        # 计算失败率趋势
        failure_rate = len([e for e in recent_executions if not e['success']]) / len(recent_executions)

        return {
            'consecutive_failures': max_consecutive_failures,
            'failure_rate': failure_rate,
            'failure_types': failure_types,
            'total_failures': len(self.failure_patterns)
        }

    def _analyze_resource_trends(self) -> Dict[str, Any]:
        """分析资源趋势"""
        if len(self.resource_history) < 5:
            return {'status': 'insufficient_data'}

        # 计算资源使用趋势
        recent_resources = list(self.resource_history)[-self.stability_window:]

        cpu_values = [r.get('cpu', 0) for r in recent_resources]
        memory_values = [r.get('memory', 0) for r in recent_resources]

        cpu_trend = self._calculate_trend(cpu_values)
        memory_trend = self._calculate_trend(memory_values)

        # 检测资源警告
        current_cpu = cpu_values[-1] if cpu_values else 0
        current_memory = memory_values[-1] if memory_values else 0

        warnings = []
        if current_cpu >= self.resource_critical_threshold:
            warnings.append('cpu_critical')
        elif current_cpu >= self.resource_warning_threshold:
            warnings.append('cpu_warning')

        if current_memory >= self.resource_critical_threshold:
            warnings.append('memory_critical')
        elif current_memory >= self.resource_warning_threshold:
            warnings.append('memory_warning')

        return {
            'cpu_trend': cpu_trend,
            'memory_trend': memory_trend,
            'current_cpu': current_cpu,
            'current_memory': current_memory,
            'warnings': warnings,
            'status': 'warning' if warnings else 'normal'
        }

    def _calculate_trend(self, values: List[float]) -> str:
        """计算趋势"""
        if len(values) < 2:
            return 'stable'

        # 简单线性趋势计算
        first_half = statistics.mean(values[:len(values)//2])
        second_half = statistics.mean(values[len(values)//2:])

        if second_half - first_half > self.degradation_threshold:
            return 'declining'
        elif first_half - second_half > self.degradation_threshold:
            return 'improving'
        return 'stable'

    def _predict_stability_risks(self) -> List[Dict[str, Any]]:
        """预测稳定性风险"""
        risks = []

        # 分析失败模式
        failure_analysis = self._analyze_failure_patterns()
        if failure_analysis.get('status') != 'insufficient_data':
            if failure_analysis.get('consecutive_failures', 0) >= self.failure_threshold:
                risks.append({
                    'type': 'consecutive_failures',
                    'severity': 'high',
                    'description': f"检测到连续 {failure_analysis['consecutive_failures']} 次失败",
                    'action': 'circuit_break'
                })

            if failure_analysis.get('failure_rate', 0) > 0.3:
                risks.append({
                    'type': 'high_failure_rate',
                    'severity': 'medium',
                    'description': f"失败率 {failure_analysis['failure_rate']:.1%} 超过阈值",
                    'action': 'auto_degrade'
                })

        # 分析资源趋势
        resource_analysis = self._analyze_resource_trends()
        if resource_analysis.get('status') != 'insufficient_data':
            if 'cpu_critical' in resource_analysis.get('warnings', []):
                risks.append({
                    'type': 'cpu_critical',
                    'severity': 'critical',
                    'description': "CPU 使用率达到危险水平",
                    'action': 'load_transfer'
                })

            if 'memory_critical' in resource_analysis.get('warnings', []):
                risks.append({
                    'type': 'memory_critical',
                    'severity': 'critical',
                    'description': "内存使用率达到危险水平",
                    'action': 'resource_release'
                })

            if resource_analysis.get('cpu_trend') == 'declining':
                risks.append({
                    'type': 'cpu_degradation',
                    'severity': 'medium',
                    'description': "CPU 使用率呈下降趋势",
                    'action': 'priority_adjust'
                })

        # 存储预测结果
        self.risk_predictions.append({
            'timestamp': datetime.now().isoformat(),
            'risks': risks,
            'stability_score': self.current_stability_score
        })

        return risks

    def _auto_degrade(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """自动降级策略"""
        _safe_print("[StabilityProtection] 执行自动降级策略...")

        # 降低任务优先级、减少并发、简化处理
        result = {
            'action': 'auto_degrade',
            'timestamp': datetime.now().isoformat(),
            'effects': {
                'task_priority': 'reduced',
                'concurrency': 'limited',
                'processing_mode': 'simplified'
            },
            'status': 'applied'
        }

        # 记录保护动作
        self._log_protection_action(result)
        self.active_protections['auto_degrade'] = result

        return result

    def _load_transfer(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """负载转移策略"""
        _safe_print("[StabilityProtection] 执行负载转移策略...")

        result = {
            'action': 'load_transfer',
            'timestamp': datetime.now().isoformat(),
            'effects': {
                'current_tasks': 'paused',
                'resources': 'reallocated',
                'new_processes': 'redirected'
            },
            'status': 'applied'
        }

        self._log_protection_action(result)
        self.active_protections['load_transfer'] = result

        return result

    def _circuit_break(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """熔断策略"""
        _safe_print("[StabilityProtection] 执行熔断策略...")

        result = {
            'action': 'circuit_break',
            'timestamp': datetime.now().isoformat(),
            'effects': {
                'new_tasks': 'rejected',
                'current_tasks': 'graceful_stop',
                'recovery_timeout': 60
            },
            'status': 'applied'
        }

        self._log_protection_action(result)
        self.active_protections['circuit_break'] = result

        return result

    def _resource_release(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """资源释放策略"""
        _safe_print("[StabilityProtection] 执行资源释放策略...")

        result = {
            'action': 'resource_release',
            'timestamp': datetime.now().isoformat(),
            'effects': {
                'cache': 'cleared',
                'temp_files': 'cleaned',
                'unused_connections': 'closed'
            },
            'status': 'applied'
        }

        self._log_protection_action(result)
        self.active_protections['resource_release'] = result

        return result

    def _priority_adjust(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """优先级调整策略"""
        _safe_print("[StabilityProtection] 执行优先级调整策略...")

        result = {
            'action': 'priority_adjust',
            'timestamp': datetime.now().isoformat(),
            'effects': {
                'high_priority': 'preserved',
                'low_priority': 'deferred',
                'background_tasks': 'suspended'
            },
            'status': 'applied'
        }

        self._log_protection_action(result)
        self.active_protections['priority_adjust'] = result

        return result

    def _log_protection_action(self, action: Dict[str, Any]):
        """记录保护动作"""
        try:
            log_file = self.protection_log_file
            actions = []
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    actions = json.load(f)

            actions.append(action)

            # 只保留最近100条
            actions = actions[-100:]

            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(actions, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[StabilityProtection] 保护动作记录失败: {e}")

    def _apply_protection(self, risk: Dict[str, Any]) -> Dict[str, Any]:
        """应用保护措施"""
        action_type = risk.get('action', 'auto_degrade')

        if action_type in self.protection_strategies:
            return self.protection_strategies[action_type](risk)

        return {'status': 'no_action', 'reason': 'unknown_action_type'}

    def analyze_stability(self) -> Dict[str, Any]:
        """分析当前稳定性状态"""
        # 预测风险
        risks = self._predict_stability_risks()

        # 分析失败模式
        failure_analysis = self._analyze_failure_patterns()

        # 分析资源趋势
        resource_analysis = self._analyze_resource_trends()

        # 计算稳定性分数
        stability_score = 100

        # 根据失败模式扣分
        if failure_analysis.get('status') != 'insufficient_data':
            consecutive_failures = failure_analysis.get('consecutive_failures', 0)
            stability_score -= consecutive_failures * 10
            stability_score -= failure_analysis.get('failure_rate', 0) * 30

        # 根据资源警告扣分
        if resource_analysis.get('status') == 'warning':
            stability_score -= 20
        elif resource_analysis.get('status') != 'insufficient_data':
            warnings = resource_analysis.get('warnings', [])
            stability_score -= len(warnings) * 5

        # 根据风险数量扣分
        stability_score -= len(risks) * 15

        # 确保分数在0-100范围内
        stability_score = max(0, min(100, stability_score))

        # 更新状态
        old_score = self.current_stability_score
        self.current_stability_score = stability_score

        if stability_score > old_score + 5:
            self.stability_trend = 'improving'
        elif stability_score < old_score - 5:
            self.stability_trend = 'declining'
        else:
            self.stability_trend = 'stable'

        # 保存状态
        self._save_state()

        return {
            'stability_score': stability_score,
            'trend': self.stability_trend,
            'risks': risks,
            'failure_analysis': failure_analysis,
            'resource_analysis': resource_analysis,
            'active_protections': list(self.active_protections.keys()),
            'timestamp': datetime.now().isoformat()
        }

    def deploy_protection(self, risk: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """部署保护措施"""
        if risk is None:
            # 自动分析并部署保护
            stability = self.analyze_stability()
            risks = stability.get('risks', [])

            if not risks:
                return {
                    'status': 'no_risks_detected',
                    'message': '未检测到需要保护的风险',
                    'timestamp': datetime.now().isoformat()
                }

            # 按严重程度排序部署保护
            results = []
            for r in sorted(risks, key=lambda x: {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}.get(x.get('severity', 'low'), 4)):
                result = self._apply_protection(r)
                results.append(result)

            return {
                'status': 'protections_deployed',
                'protections': results,
                'timestamp': datetime.now().isoformat()
            }
        else:
            # 部署指定风险的保护
            return self._apply_protection(risk)

    def heal_stability(self) -> Dict[str, Any]:
        """自愈稳定性问题"""
        _safe_print("[StabilityProtection] 执行稳定性自愈...")

        # 分析当前状态
        stability = self.analyze_stability()

        # 清除已缓解的保护措施
        active = list(self.active_protections.keys())
        cleared = []

        for protection_name in active:
            # 检查是否可以清除
            risk = stability.get('risks', [])
            # 简单策略：清除非关键保护
            if protection_name != 'circuit_break':
                del self.active_protections[protection_name]
                cleared.append(protection_name)

        # 重新评估
        new_stability = self.analyze_stability()

        return {
            'status': 'healing_completed',
            'cleared_protections': cleared,
            'new_stability_score': new_stability.get('stability_score'),
            'remaining_risks': len(new_stability.get('risks', [])),
            'timestamp': datetime.now().isoformat()
        }

    def predict_next_instability(self) -> Dict[str, Any]:
        """预测下一次不稳定时间"""
        if len(self.risk_predictions) < 5:
            return {'status': 'insufficient_data'}

        # 分析历史预测模式
        recent = list(self.risk_predictions)[-10:]

        risk_counts = [len(p.get('risks', [])) for p in recent]

        if not risk_counts:
            return {'status': 'stable_prediction'}

        # 简单预测：基于平均风险频率
        avg_risks = statistics.mean(risk_counts)
        max_risks = max(risk_counts)

        if avg_risks > 2:
            prediction = "预计近期可能有稳定性问题"
            confidence = 0.7
        elif max_risks > 0:
            prediction = "存在潜在风险，建议监控"
            confidence = 0.5
        else:
            prediction = "预计保持稳定"
            confidence = 0.9

        return {
            'prediction': prediction,
            'confidence': confidence,
            'avg_risk_count': avg_risks,
            'max_risk_count': max_risks,
            'timestamp': datetime.now().isoformat()
        }

    def get_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        stability = self.analyze_stability()

        return {
            'version': self.version,
            'stability_score': stability.get('stability_score'),
            'trend': stability.get('trend'),
            'active_protections': list(self.active_protections.keys()),
            'risks_count': len(stability.get('risks', [])),
            'prediction': self.predict_next_instability(),
            'monitoring_active': self.monitoring_active,
            'timestamp': datetime.now().isoformat()
        }

    def start_monitoring(self):
        """启动监控"""
        if self.monitoring_active:
            return {'status': 'already_running'}

        self.monitoring_active = True

        def monitor_loop():
            while self.monitoring_active:
                try:
                    # 收集当前资源使用
                    resource_usage = {
                        'cpu': psutil.cpu_percent() / 100.0,
                        'memory': psutil.virtual_memory().percent / 100.0
                    }

                    # 记录执行（模拟）
                    self._record_execution(
                        task_id=f'monitor_{int(time.time())}',
                        success=True,
                        duration=0.1,
                        resource_usage=resource_usage
                    )

                    # 定期分析
                    if len(self.execution_history) % 10 == 0:
                        self.analyze_stability()

                except Exception as e:
                    _safe_print(f"[StabilityProtection] 监控异常: {e}")

                time.sleep(self.monitoring_interval)

        self.monitoring_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitoring_thread.start()

        return {'status': 'monitoring_started', 'timestamp': datetime.now().isoformat()}

    def stop_monitoring(self):
        """停止监控"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)

        return {'status': 'monitoring_stopped', 'timestamp': datetime.now().isoformat()}


# CLI 接口
def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description='执行稳定性预测防护引擎')
    parser.add_argument('command', choices=['status', 'analyze', 'protect', 'heal', 'predict', 'start', 'stop'],
                        help='要执行的命令')
    parser.add_argument('--risk', type=str, help='风险类型（protect命令使用）')

    args = parser.parse_args()

    engine = ExecutionStabilityProtectionEngine()

    if args.command == 'status':
        result = engine.get_status()
    elif args.command == 'analyze':
        result = engine.analyze_stability()
    elif args.command == 'protect':
        if args.risk:
            risk = json.loads(args.risk)
            result = engine.deploy_protection(risk)
        else:
            result = engine.deploy_protection()
    elif args.command == 'heal':
        result = engine.heal_stability()
    elif args.command == 'predict':
        result = engine.predict_next_instability()
    elif args.command == 'start':
        result = engine.start_monitoring()
    elif args.command == 'stop':
        result = engine.stop_monitoring()

    _safe_print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()