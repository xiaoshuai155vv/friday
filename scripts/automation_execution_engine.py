#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能自动化执行闭环引擎

让系统能够主动发现用户重复行为，自动生成并执行工作流，
形成「发现→生成→执行→反馈」的完整闭环。

区别于 automation_pattern_discovery（模式发现与场景生成）：
- Pattern Discovery：发现模式，生成场景计划（被动）
- Automation Execution：执行自动化任务，形成闭环（主动）

功能：
1. 自动化任务发现与分析：分析用户行为，识别可自动化的任务
2. 智能工作流生成：根据模式自动生成可执行的工作流
3. 自动执行能力：基于时间/事件触发自动执行
4. 效果评估与反馈：评估执行效果并反馈学习
5. 与其他引擎深度集成：协同模式发现、执行增强、偏好学习等引擎
"""

import os
import sys
import json
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict
from typing import List, Dict, Optional, Tuple, Any

# 项目根目录
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"
PLANS_DIR = PROJECT_ROOT / "assets" / "plans"

# 添加 scripts 目录到路径
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


class AutomationExecutionEngine:
    """智能自动化执行闭环引擎"""

    def __init__(self):
        self.min_pattern_occurrences = 2  # 最小重复次数
        self.analysis_days = 7  # 分析最近7天的数据
        self.auto_execution_enabled = False  # 默认不自动执行，需要用户确认
        self.execution_history: List[Dict] = []

        # 加载配置
        self.config = self._load_config()

        # 初始化集成引擎
        self._init_engines()

    def _load_config(self) -> Dict:
        """加载配置"""
        config_file = STATE_DIR / "automation_execution_config.json"
        default_config = {
            "auto_execution_enabled": False,
            "execution_interval_minutes": 60,
            "max_auto_tasks_per_day": 10,
            "require_confirmation": True,
            "max_execution_history": 100
        }

        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return {**default_config, **json.load(f)}
            except Exception:
                pass

        return default_config

    def _save_config(self):
        """保存配置"""
        config_file = STATE_DIR / "automation_execution_config.json"
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def _init_engines(self):
        """初始化集成引擎"""
        # 尝试导入模式发现引擎
        try:
            from automation_pattern_discovery import AutomationPatternDiscovery
            self.pattern_discovery = AutomationPatternDiscovery()
        except ImportError:
            self.pattern_discovery = None

        # 尝试导入执行增强引擎
        try:
            from execution_enhancement_engine import ExecutionEnhancementEngine
            self.execution_enhancement = ExecutionEnhancementEngine()
        except ImportError:
            self.execution_enhancement = None

        # 尝试导入偏好引擎
        try:
            from task_preference_engine import TaskPreferenceEngine
            self.preference_engine = TaskPreferenceEngine()
        except ImportError:
            self.preference_engine = None

    def analyze_automation_opportunities(self) -> Dict:
        """分析自动化机会"""
        result = {
            'opportunities': [],
            'patterns_analyzed': 0,
            'auto_tasks_found': 0,
            'recommendations': []
        }

        # 使用模式发现引擎分析
        if self.pattern_discovery:
            behavior_data = self.pattern_discovery.analyze_behavior_logs()
            patterns = self.pattern_discovery.find_repeated_patterns(behavior_data)
            result['patterns_analyzed'] = len(patterns)

            # 分析每个模式作为自动化机会
            for pattern in patterns:
                opportunity = self._analyze_pattern_opportunity(pattern)
                if opportunity:
                    result['opportunities'].append(opportunity)
                    result['auto_tasks_found'] += 1
        else:
            # 如果没有模式发现引擎，直接分析日志
            opportunities = self._direct_log_analysis()
            result['opportunities'] = opportunities
            result['auto_tasks_found'] = len(opportunities)

        # 生成建议
        if result['opportunities']:
            result['recommendations'] = [
                f"发现 {len(result['opportunities'])} 个可自动化的任务",
                "可启用自动执行来自动完成这些任务",
                "可通过 'auto-execute enable' 开启自动执行模式"
            ]
        else:
            result['recommendations'] = [
                "当前未发现明显的自动化机会",
                "系统会继续分析您的行为模式"
            ]

        return result

    def _analyze_pattern_opportunity(self, pattern: Dict) -> Optional[Dict]:
        """分析单个模式的自动化机会"""
        sequence = pattern.get('sequence', [])
        occurrences = pattern.get('occurrences', 0)

        if not sequence or occurrences < self.min_pattern_occurrences:
            return None

        # 计算自动化价值
        automation_value = self._calculate_automation_value(sequence, occurrences)

        if automation_value['score'] < 3:
            return None

        opportunity = {
            'pattern': sequence,
            'occurrences': occurrences,
            'automation_value': automation_value,
            'suggested_workflow': self._generate_workflow_template(sequence),
            'estimated_time_saved': automation_value.get('time_saved_minutes', 0)
        }

        return opportunity

    def _calculate_automation_value(self, sequence: List, occurrences: int) -> Dict:
        """计算自动化的价值"""
        # 基础分数：出现次数越多，自动化价值越高
        base_score = min(occurrences * 2, 10)

        # 序列长度分数：序列越长，自动化价值越高
        length_score = min(len(sequence) * 2, 10)

        # 计算预计节省时间（每次执行节省 1 分钟）
        time_saved = occurrences * len(sequence) * 1

        score = base_score + length_score

        return {
            'score': score,
            'base_score': base_score,
            'length_score': length_score,
            'time_saved_minutes': time_saved
        }

    def _generate_workflow_template(self, sequence: List) -> Dict:
        """生成工作流模板"""
        steps = []

        for i, action in enumerate(sequence):
            if isinstance(action, tuple):
                action = list(action)

            action_str = ' '.join(action).lower() if isinstance(action, list) else str(action).lower()

            # 根据操作类型生成步骤
            step = self._action_to_workflow_step(action_str, i)
            steps.append(step)

        return {
            'name': f"自动化任务_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'description': '自动执行的任务工作流',
            'triggers': ['自动化执行', 'auto_execute'],
            'steps': steps
        }

    def _action_to_workflow_step(self, action_str: str, index: int) -> Dict:
        """将操作转换为工作流步骤"""
        if '打开' in action_str or 'launch' in action_str:
            app_match = re.search(r'打开[的]?(\S+)', action_str)
            app_name = app_match.group(1) if app_match else "应用"
            return {
                "tool": "run",
                "command": f"do.py 打开应用 {app_name}",
                "wait": 2,
                "description": f"打开{app_name}"
            }
        elif '截图' in action_str or 'screenshot' in action_str:
            return {
                "tool": "screenshot",
                "description": "截图"
            }
        elif 'vision' in action_str or '分析' in action_str:
            return {
                "tool": "vision",
                "description": "分析屏幕内容"
            }
        elif '点击' in action_str or 'click' in action_str:
            return {
                "tool": "wait",
                "seconds": 1,
                "description": "等待点击操作"
            }
        elif '输入' in action_str or 'type' in action_str:
            return {
                "tool": "wait",
                "seconds": 1,
                "description": "等待输入操作"
            }
        else:
            return {
                "tool": "wait",
                "seconds": 1,
                "description": f"执行步骤 {index + 1}"
            }

    def _direct_log_analysis(self) -> List[Dict]:
        """直接分析日志"""
        opportunities = []
        recent_cutoff = datetime.now() - timedelta(days=self.analysis_days)

        # 读取最近日志
        log_files = list(LOGS_DIR.glob("behavior_*.log"))
        action_counter = Counter()

        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if 'run_plan' in line or 'execute' in line.lower():
                            # 提取关键操作
                            action_counter[line.strip()[:100]] += 1
            except Exception:
                continue

        # 找出高频操作
        for action, count in action_counter.most_common(10):
            if count >= self.min_pattern_occurrences:
                opportunities.append({
                    'action': action,
                    'occurrences': count,
                    'automation_value': {'score': count * 2}
                })

        return opportunities

    def execute_automated_task(self, workflow: Dict, dry_run: bool = False) -> Dict:
        """执行自动化任务"""
        result = {
            'workflow_name': workflow.get('name', '未命名'),
            'status': 'pending',
            'start_time': datetime.now().isoformat(),
            'steps_executed': 0,
            'steps_total': len(workflow.get('steps', [])),
            'success': False,
            'errors': []
        }

        if dry_run:
            result['status'] = 'dry_run'
            result['message'] = '模拟执行模式，未实际执行'
            return result

        # 保存执行历史
        self.execution_history.append({
            'workflow': workflow.get('name'),
            'start_time': result['start_time'],
            'status': 'running'
        })

        try:
            # 执行工作流步骤
            for i, step in enumerate(workflow.get('steps', [])):
                step_result = self._execute_step(step)
                result['steps_executed'] += 1

                if not step_result['success']:
                    result['errors'].append(f"步骤 {i+1} 失败: {step_result.get('error')}")
                    break

            # 标记完成
            result['success'] = len(result['errors']) == 0
            result['status'] = 'completed' if result['success'] else 'failed'
            result['end_time'] = datetime.now().isoformat()

            # 更新执行历史
            if self.execution_history:
                self.execution_history[-1]['status'] = 'completed' if result['success'] else 'failed'
                self.execution_history[-1]['end_time'] = result.get('end_time')

            # 反馈学习
            self._learn_from_execution(result)

        except Exception as e:
            result['status'] = 'error'
            result['errors'].append(str(e))

        return result

    def _execute_step(self, step: Dict) -> Dict:
        """执行单个步骤"""
        tool = step.get('tool', '')
        result = {'success': True}

        try:
            if tool == 'run':
                command = step.get('command', '')
                if command:
                    subprocess.run(command, shell=True, capture_output=True, timeout=30)
            elif tool == 'wait':
                import time
                time.sleep(step.get('seconds', 1))
            elif tool == 'screenshot':
                # 使用 screenshot_tool
                subprocess.run(
                    [sys.executable, str(SCRIPT_DIR / "screenshot_tool.py")],
                    capture_output=True, timeout=30
                )
            elif tool == 'vision':
                # 视觉分析不需要自动执行
                result['success'] = False
                result['error'] = 'vision 步骤需要用户交互，不适合自动执行'
            elif tool in ['click', 'type', 'key']:
                # 这些需要具体坐标或内容，不适合盲目自动执行
                result['success'] = False
                result['error'] = f'{tool} 步骤需要具体参数，不适合自动执行'
            else:
                # 未知工具
                result['success'] = False
                result['error'] = f'未知工具: {tool}'

        except subprocess.TimeoutExpired:
            result['success'] = False
            result['error'] = '执行超时'
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)

        return result

    def _learn_from_execution(self, result: Dict):
        """从执行结果中学习"""
        if not self.execution_enhancement:
            return

        try:
            # 记录执行数据供学习引擎使用
            learning_data = {
                'workflow_name': result.get('workflow_name'),
                'success': result.get('success', False),
                'steps_executed': result.get('steps_executed', 0),
                'steps_total': result.get('steps_total', 0),
                'errors': result.get('errors', []),
                'timestamp': datetime.now().isoformat()
            }

            # 保存到学习数据文件
            learning_file = STATE_DIR / "automation_execution_learning.json"
            existing_data = []

            if learning_file.exists():
                with open(learning_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)

            existing_data.append(learning_data)

            # 只保留最近 100 条
            existing_data = existing_data[-100:]

            with open(learning_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"学习记录保存失败: {e}")

    def get_execution_stats(self) -> Dict:
        """获取执行统计"""
        total_executions = len(self.execution_history)
        successful = sum(1 for h in self.execution_history if h.get('status') == 'completed')
        failed = sum(1 for h in self.execution_history if h.get('status') == 'failed')

        return {
            'total_executions': total_executions,
            'successful': successful,
            'failed': failed,
            'success_rate': round(successful / total_executions * 100, 1) if total_executions > 0 else 0,
            'auto_execution_enabled': self.config.get('auto_execution_enabled', False),
            'last_execution': self.execution_history[-1].get('start_time') if self.execution_history else None
        }

    def enable_auto_execution(self, enable: bool = True) -> Dict:
        """启用/禁用自动执行"""
        self.config['auto_execution_enabled'] = enable
        self._save_config()

        return {
            'auto_execution_enabled': enable,
            'message': f"自动执行已{'启用' if enable else '禁用'}"
        }

    def get_status(self) -> Dict:
        """获取引擎状态"""
        return {
            'name': '智能自动化执行闭环引擎',
            'status': 'active',
            'auto_execution_enabled': self.config.get('auto_execution_enabled', False),
            'analysis_days': self.analysis_days,
            'min_pattern_occurrences': self.min_pattern_occurrences,
            'last_analysis': datetime.now().isoformat(),
            'engines_available': {
                'pattern_discovery': self.pattern_discovery is not None,
                'execution_enhancement': self.execution_enhancement is not None,
                'preference_engine': self.preference_engine is not None
            },
            'execution_stats': self.get_execution_stats()
        }

    def generate_execution_report(self) -> Dict:
        """生成执行报告"""
        opportunities = self.analyze_automation_opportunities()

        report = {
            'generated_at': datetime.now().isoformat(),
            'opportunities_summary': {
                'total_opportunities': opportunities['auto_tasks_found'],
                'high_value_opportunities': sum(1 for o in opportunities['opportunities']
                                                if o.get('automation_value', {}).get('score', 0) >= 5)
            },
            'execution_stats': self.get_execution_stats(),
            'recommendations': opportunities['recommendations'],
            'integrations': {
                'pattern_discovery': self.pattern_discovery is not None,
                'auto_learning': True
            }
        }

        return report


def handle_command(args: List[str]) -> str:
    """处理命令"""
    engine = AutomationExecutionEngine()

    if not args:
        # 显示引擎状态
        status = engine.get_status()
        return json.dumps(status, ensure_ascii=False, indent=2)

    command = args[0]

    if command in ['status', '状态']:
        status = engine.get_status()
        return json.dumps(status, ensure_ascii=False, indent=2)

    elif command in ['analyze', '分析', 'analyze-opportunities']:
        result = engine.analyze_automation_opportunities()
        return json.dumps(result, ensure_ascii=False, indent=2)

    elif command in ['execute', '执行', 'run']:
        # 执行自动化任务
        if len(args) > 1:
            # 尝试从文件加载工作流
            workflow_file = PLANS_DIR / args[1]
            if workflow_file.exists():
                with open(workflow_file, 'r', encoding='utf-8') as f:
                    workflow = json.load(f)
            else:
                # 尝试直接作为 JSON
                try:
                    workflow = json.loads(args[1])
                except:
                    return json.dumps({'error': '无法解析工作流'}, ensure_ascii=False, indent=2)
        else:
            # 分析并使用第一个高价值机会
            opportunities = engine.analyze_automation_opportunities()
            if opportunities['opportunities']:
                workflow = opportunities['opportunities'][0].get('suggested_workflow', {})
            else:
                return json.dumps({'error': '没有可执行的自动化任务'}, ensure_ascii=False, indent=2)

        # 检查是否为 dry-run
        dry_run = '--dry-run' in args or '--dry' in args
        result = engine.execute_automated_task(workflow, dry_run=dry_run)
        return json.dumps(result, ensure_ascii=False, indent=2)

    elif command in ['enable', '启用', 'auto-execute-enable']:
        result = engine.enable_auto_execution(True)
        return json.dumps(result, ensure_ascii=False, indent=2)

    elif command in ['disable', '禁用', 'auto-execute-disable']:
        result = engine.enable_auto_execution(False)
        return json.dumps(result, ensure_ascii=False, indent=2)

    elif command in ['stats', '统计', 'execution-stats']:
        result = engine.get_execution_stats()
        return json.dumps(result, ensure_ascii=False, indent=2)

    elif command in ['report', '报告', 'execution-report']:
        result = engine.generate_execution_report()
        return json.dumps(result, ensure_ascii=False, indent=2)

    else:
        return json.dumps({
            'error': f'未知命令: {command}',
            'available_commands': [
                'status', 'analyze', 'execute', 'enable', 'disable',
                'stats', 'report'
            ]
        }, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    result = handle_command(args)
    print(result)