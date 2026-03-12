#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能工作流引擎
让星期五能够理解复杂用户意图，自动规划并执行多步骤任务链
实现从「单命令执行」到「复杂任务闭环」的进化
"""
import os
import json
import re
import subprocess
from datetime import datetime
from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass, field


@dataclass
class WorkflowStep:
    """工作流步骤"""
    id: str
    action: str  # 操作类型：run/do/screenshot/vision/click/type/wait/condition/loop
    params: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    condition: str = None  # 条件：if/while
    condition_expr: str = None  # 条件表达式
    loop_count: int = None  # 循环次数


@dataclass
class WorkflowExecution:
    """工作流执行结果"""
    workflow_id: str
    status: str  # running/completed/failed
    steps_completed: int = 0
    total_steps: int = 0
    results: List[Dict[str, Any]] = field(default_factory=list)
    error: str = None
    start_time: str = None
    end_time: str = None


class IntentParser:
    """意图解析器"""

    # 意图模式
    INTENT_PATTERNS = {
        'organize_and_send': [
            r'整理.*发.*邮件',
            r'整理.*并发送',
            r'整理.*发送.*邮'
        ],
        'search_and_open': [
            r'搜索.*打开',
            r'查找.*打开',
            r'找到.*打开'
        ],
        'backup_and_notify': [
            r'备份.*通知',
            r'备份.*并提醒',
            r'备份.*告诉'
        ],
        'collect_and_summary': [
            r'收集.*汇总',
            r'整理.*汇总',
            r'收集.*总结'
        ],
        'monitor_and_alert': [
            r'监控.*提醒',
            r'监控.*通知',
            r'监视.*报警'
        ]
    }

    ACTION_KEYWORDS = {
        'open': ['打开', '启动', '运行', '开'],
        'close': ['关闭', '退出', '关'],
        'search': ['搜索', '查找', '找', '搜'],
        'copy': ['复制', '拷贝'],
        'move': ['移动', '搬运', '转移'],
        'delete': ['删除', '移除', '去掉'],
        'read': ['读取', '查看', '看', '检查'],
        'write': ['写入', '写', '编辑'],
        'send': ['发送', '发', '寄'],
        'notify': ['通知', '提醒', '告诉'],
        'wait': ['等待', '等'],
        'click': ['点击', '按', '选'],
        'type': ['输入', '填写', '录入'],
    }

    def parse(self, user_input: str) -> Dict[str, Any]:
        """
        解析用户输入，提取意图和关键信息

        Args:
            user_input: 用户输入的自然语言

        Returns:
            解析结果字典
        """
        result = {
            'intent': self._detect_intent(user_input),
            'actions': self._extract_actions(user_input),
            'targets': self._extract_targets(user_input),
            'conditions': self._extract_conditions(user_input),
            'original_input': user_input
        }
        return result

    def _detect_intent(self, text: str) -> str:
        """检测意图类型"""
        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return intent
        return 'general_task'

    def _extract_actions(self, text: str) -> List[str]:
        """提取动作序列"""
        actions = []
        text_lower = text
        for action, keywords in self.ACTION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    actions.append(action)
                    break
        return actions if actions else ['execute']

    def _extract_targets(self, text: str) -> List[str]:
        """提取目标对象"""
        # 提取引号内的内容
        quoted = re.findall(r'["\']([^"\']+)["\']', text)
        if quoted:
            return quoted

        # 提取常见的目标模式
        targets = []
        patterns = [
            r'把\s+(.+?)\s+',
            r'对\s+(.+?)\s+',
            r'用\s+(.+?)\s+',
            r'(?:文件|文档|文件夹|应用|程序)\s+(.+?)\s+'
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text)
            targets.extend(matches)

        return targets

    def _extract_conditions(self, text: str) -> Dict[str, Any]:
        """提取条件"""
        conditions = {}

        # 如果...则...
        if_match = re.search(r'如果(.+?)，?(则|就)(.+)', text)
        if if_match:
            conditions['if'] = {
                'condition': if_match.group(1),
                'action': if_match.group(3)
            }

        # 循环
        loop_match = re.search(r'重复(\d+)次|循环(\d+)次', text)
        if loop_match:
            conditions['loop'] = loop_match.group(1) or loop_match.group(2)

        return conditions


class TaskPlanner:
    """任务规划器"""

    def __init__(self):
        self.intent_parser = IntentParser()

        # 预定义的任务模板
        self.task_templates = {
            'organize_and_send': [
                {'action': 'run', 'do': 'list_files', 'params': {}},
                {'action': 'run', 'do': 'organize_files', 'params': {}},
                {'action': 'run', 'do': 'send_email', 'params': {}}
            ],
            'search_and_open': [
                {'action': 'run', 'do': 'search', 'params': {}},
                {'action': 'run', 'do': 'open_result', 'params': {}}
            ],
            'backup_and_notify': [
                {'action': 'run', 'do': 'backup', 'params': {}},
                {'action': 'run', 'do': 'notify', 'params': {}}
            ],
            'collect_and_summary': [
                {'action': 'run', 'do': 'collect_data', 'params': {}},
                {'action': 'run', 'do': 'generate_summary', 'params': {}}
            ],
            'monitor_and_alert': [
                {'action': 'run', 'do': 'start_monitor', 'params': {}},
                {'action': 'condition', 'expr': 'alert_needed', 'do': 'send_alert', 'params': {}}
            ]
        }

    def plan(self, user_input: str) -> List[WorkflowStep]:
        """
        根据用户输入生成任务计划

        Args:
            user_input: 用户输入的自然语言

        Returns:
            工作流步骤列表
        """
        # 解析意图
        parsed = self.intent_parser.parse(user_input)
        intent = parsed['intent']

        steps = []

        # 使用模板或生成默认计划
        if intent in self.task_templates:
            template = self.task_templates[intent]
            for i, step in enumerate(template):
                steps.append(WorkflowStep(
                    id=f"step_{i+1}",
                    action=step['action'],
                    params=step.get('params', {}),
                    description=f"执行 {step.get('do', step['action'])}"
                ))
        else:
            # 生成通用计划
            actions = parsed['actions']
            targets = parsed['targets']

            for i, action in enumerate(actions):
                steps.append(WorkflowStep(
                    id=f"step_{i+1}",
                    action='do',
                    params={'command': action, 'target': targets[i] if i < len(targets) else None},
                    description=f"执行动作: {action}"
                ))

        # 添加条件
        if parsed['conditions']:
            for condition_key, condition_value in parsed['conditions'].items():
                if condition_key == 'loop':
                    if steps:
                        steps[-1].loop_count = int(condition_value)
                elif condition_key == 'if':
                    if steps:
                        steps[-1].condition = 'if'
                        steps[-1].condition_expr = condition_value['condition']

        return steps


class WorkflowExecutor:
    """工作流执行器"""

    def __init__(self):
        self.planner = TaskPlanner()
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

    def execute_workflow(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        执行工作流

        Args:
            user_input: 用户输入
            context: 执行上下文

        Returns:
            执行结果
        """
        context = context or {}

        # 生成计划
        steps = self.planner.plan(user_input)

        # 创建执行记录
        execution = WorkflowExecution(
            workflow_id=f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            status="running",
            total_steps=len(steps),
            start_time=datetime.now().isoformat()
        )

        results = []

        # 执行每一步
        for i, step in enumerate(steps):
            try:
                result = self._execute_step(step, context)
                results.append({
                    'step_id': step.id,
                    'action': step.action,
                    'status': 'success',
                    'result': result
                })
                execution.steps_completed += 1

                # 检查条件
                if step.condition == 'if' and not self._evaluate_condition(step.condition_expr, result):
                    break

                # 处理循环
                if step.loop_count:
                    loop_results = self._execute_loop(step, context, step.loop_count)
                    results.extend(loop_results)

            except Exception as e:
                results.append({
                    'step_id': step.id,
                    'action': step.action,
                    'status': 'error',
                    'error': str(e)
                })
                execution.status = 'failed'
                execution.error = str(e)
                break

        # 完成执行
        execution.end_time = datetime.now().isoformat()
        execution.results = results
        if execution.status != 'failed':
            execution.status = 'completed'

        return {
            'execution': {
                'workflow_id': execution.workflow_id,
                'status': execution.status,
                'steps_completed': execution.steps_completed,
                'total_steps': execution.total_steps,
                'start_time': execution.start_time,
                'end_time': execution.end_time,
                'error': execution.error
            },
            'steps': results
        }

    def _execute_step(self, step: WorkflowStep, context: Dict[str, Any]) -> Any:
        """执行单个步骤"""
        if step.action == 'run':
            # 执行 do.py 命令
            command = step.params.get('do', '')
            if command:
                return self._run_do_command(command, step.params)
            return {'status': 'no_command'}

        elif step.action == 'screenshot':
            # 截图
            return self._run_screenshot()

        elif step.action == 'wait':
            # 等待
            seconds = step.params.get('seconds', 1)
            import time
            time.sleep(seconds)
            return {'status': 'waited', 'seconds': seconds}

        elif step.action == 'click':
            # 点击
            x = step.params.get('x')
            y = step.params.get('y')
            if x is not None and y is not None:
                return self._run_click(x, y)
            return {'status': 'no_coords'}

        elif step.action == 'type':
            # 输入
            text = step.params.get('text', '')
            return self._run_type(text)

        else:
            return {'status': 'unknown_action', 'action': step.action}

    def _run_do_command(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """运行 do.py 命令"""
        do_script = os.path.join(self.base_dir, 'do.py')

        # 构建命令
        cmd_parts = ['python', do_script, command]
        for key, value in params.items():
            if key != 'do':
                cmd_parts.append(str(value))

        try:
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.base_dir
            )
            return {
                'status': 'success' if result.returncode == 0 else 'error',
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {'status': 'timeout', 'command': command}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def _run_screenshot(self) -> Dict[str, Any]:
        """运行截图"""
        return self._run_do_command('截图', {})

    def _run_click(self, x: int, y: int) -> Dict[str, Any]:
        """运行点击"""
        mouse_tool = os.path.join(self.base_dir, 'mouse_tool.py')
        try:
            result = subprocess.run(
                ['python', mouse_tool, 'click', str(x), str(y)],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.base_dir
            )
            return {'status': 'success', 'x': x, 'y': y}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def _run_type(self, text: str) -> Dict[str, Any]:
        """运行输入"""
        keyboard_tool = os.path.join(self.base_dir, 'keyboard_tool.py')
        try:
            result = subprocess.run(
                ['python', keyboard_tool, 'type', text],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.base_dir
            )
            return {'status': 'success', 'text': text}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def _execute_loop(self, step: WorkflowStep, context: Dict[str, Any], count: int) -> List[Dict[str, Any]]:
        """执行循环"""
        results = []
        for i in range(count):
            try:
                result = self._execute_step(step, context)
                results.append({
                    'step_id': f"{step.id}_loop_{i+1}",
                    'action': step.action,
                    'loop_iteration': i + 1,
                    'status': 'success',
                    'result': result
                })
            except Exception as e:
                results.append({
                    'step_id': f"{step.id}_loop_{i+1}",
                    'action': step.action,
                    'loop_iteration': i + 1,
                    'status': 'error',
                    'error': str(e)
                })
        return results

    def _evaluate_condition(self, condition_expr: str, context: Dict[str, Any]) -> bool:
        """评估条件表达式"""
        # 简化的条件评估
        # 实际可以通过更复杂的表达式解析器实现
        if not condition_expr:
            return True

        # 检查条件关键字
        positive_keywords = ['是', '有', '存在', '成功', '完成', 'true', 'yes']
        negative_keywords = ['否', '无', '不存在', '失败', 'false', 'no']

        for kw in positive_keywords:
            if kw in condition_expr:
                return True
        for kw in negative_keywords:
            if kw in condition_expr:
                return False

        return True


class WorkflowEngine:
    """智能工作流引擎主类"""

    def __init__(self):
        self.executor = WorkflowExecutor()
        self.planner = self.executor.planner
        self.intent_parser = self.planner.intent_parser

    def process(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理用户输入，执行工作流

        Args:
            user_input: 用户输入的自然语言
            context: 执行上下文

        Returns:
            处理结果
        """
        # 解析意图
        parsed = self.intent_parser.parse(user_input)

        # 生成计划
        steps = self.planner.plan(user_input)

        # 执行工作流
        result = self.executor.execute_workflow(user_input, context)

        # 返回完整结果
        return {
            'success': result['execution']['status'] == 'completed',
            'intent': parsed,
            'plan': [
                {
                    'id': s.id,
                    'action': s.action,
                    'description': s.description,
                    'condition': s.condition,
                    'loop_count': s.loop_count
                }
                for s in steps
            ],
            'execution': result['execution'],
            'steps': result['steps']
        }

    def get_available_templates(self) -> Dict[str, Any]:
        """获取可用的工作流模板"""
        return {
            'templates': list(self.planner.task_templates.keys()),
            'descriptions': {
                'organize_and_send': '整理文件并发送邮件',
                'search_and_open': '搜索并打开',
                'backup_and_notify': '备份并通知',
                'collect_and_summary': '收集并汇总',
                'monitor_and_alert': '监控并提醒'
            }
        }


# CLI 接口
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='智能工作流引擎')
    parser.add_argument('command', nargs='?', help='命令: process/plan/templates')
    parser.add_argument('--input', '-i', help='用户输入')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')

    args = parser.parse_args()

    engine = WorkflowEngine()

    if args.command == 'templates' or args.command == 'list':
        result = engine.get_available_templates()
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("可用工作流模板:")
            for template, desc in result['descriptions'].items():
                print(f"  - {template}: {desc}")

    elif args.command == 'plan':
        if args.input:
            steps = engine.planner.plan(args.input)
            print(f"任务计划 (共 {len(steps)} 步):")
            for i, step in enumerate(steps, 1):
                print(f"  {i}. [{step.action}] {step.description}")
        else:
            print("请提供 --input 参数")

    elif args.command == 'process':
        if args.input:
            result = engine.process(args.input)
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(f"执行状态: {result['execution']['status']}")
                print(f"完成步骤: {result['execution']['steps_completed']}/{result['execution']['total_steps']}")
        else:
            print("请提供 --input 参数")

    else:
        # 默认显示模板列表
        result = engine.get_available_templates()
        print("可用工作流模板:")
        for template, desc in result['descriptions'].items():
            print(f"  - {template}: {desc}")
        print("\n用法:")
        print("  python workflow_engine.py process --input \"整理文件并发送邮件\"")
        print("  python workflow_engine.py plan --input \"搜索并打开文档\"")
        print("  python workflow_engine.py templates")