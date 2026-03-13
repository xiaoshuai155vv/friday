#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能任务理解与自动规划引擎
让系统能够理解用户自然语言描述的目标，自动分解为可执行步骤链
利用 LLM 的理解、推理、生成能力来处理任务规划
"""
import os
import json
import re
import subprocess
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
import tempfile


# 可用的基础能力（用于任务分解）
AVAILABLE_ACTIONS = {
    # 文件操作
    'list_files': {'category': 'file', 'description': '列出目录文件'},
    'read_file': {'category': 'file', 'description': '读取文件内容'},
    'write_file': {'category': 'file', 'description': '写入文件'},
    'organize_files': {'category': 'file', 'description': '整理文件'},
    'delete_file': {'category': 'file', 'description': '删除文件'},
    'move_file': {'category': 'file', 'description': '移动文件'},
    'copy_file': {'category': 'file', 'description': '复制文件'},
    'search_files': {'category': 'file', 'description': '搜索文件'},

    # 应用操作
    'open_app': {'category': 'app', 'description': '打开应用'},
    'close_app': {'category': 'app', 'description': '关闭应用'},
    'switch_app': {'category': 'app', 'description': '切换应用'},

    # 浏览器操作
    'open_browser': {'category': 'browser', 'description': '打开浏览器'},
    'open_url': {'category': 'browser', 'description': '打开网址'},
    'search_web': {'category': 'browser', 'description': '网页搜索'},

    # 通讯
    'send_email': {'category': 'communication', 'description': '发送邮件'},
    'send_message': {'category': 'communication', 'description': '发送消息'},

    # 系统操作
    'screenshot': {'category': 'system', 'description': '截取屏幕'},
    'get_system_info': {'category': 'system', 'description': '获取系统信息'},
    'notify': {'category': 'system', 'description': '发送通知'},
    'play_music': {'category': 'system', 'description': '播放音乐'},

    # 窗口操作
    'activate_window': {'category': 'window', 'description': '激活窗口'},
    'maximize_window': {'category': 'window', 'description': '最大化窗口'},
    'click': {'category': 'interaction', 'description': '点击坐标'},
    'type': {'category': 'interaction', 'description': '输入文本'},
    'scroll': {'category': 'interaction', 'description': '滚动屏幕'},
    'wait': {'category': 'interaction', 'description': '等待'},

    # 特定场景
    'ihaier_message': {'category': 'scenario', 'description': '发送iHaier消息'},
    'performance_declaration': {'category': 'scenario', 'description': '绩效申报'},
}


# 常见任务模式（用于快速匹配）
TASK_PATTERNS = {
    r'整理.*桌面': {
        'steps': [
            {'action': 'list_files', 'target': 'Desktop'},
            {'action': 'organize_files', 'target': 'Desktop'},
        ]
    },
    r'整理.*文件.*并发送': {
        'steps': [
            {'action': 'list_files', 'target': ''},
            {'action': 'organize_files', 'target': ''},
            {'action': 'send_email', 'target': ''},
        ]
    },
    r'搜索.*打开': {
        'steps': [
            {'action': 'search_web', 'target': ''},
            {'action': 'open_url', 'target': ''},
        ]
    },
    r'备份.*通知': {
        'steps': [
            {'action': 'copy_file', 'target': ''},
            {'action': 'notify', 'target': '备份完成'},
        ]
    },
}


class LLMTaskPlanner:
    """基于 LLM 的智能任务规划器"""

    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.planning_history = []
        self._load_examples()

    def _load_examples(self):
        """加载示例任务规划"""
        self.examples = [
            {
                'input': '帮我整理桌面并发送到邮箱',
                'decomposition': [
                    {'step': 1, 'action': 'list_files', 'target': 'Desktop', 'reason': '先查看桌面文件'},
                    {'step': 2, 'action': 'organize_files', 'target': 'Desktop', 'reason': '整理文件'},
                    {'step': 3, 'action': 'send_email', 'target': '', 'reason': '发送整理结果'}
                ]
            },
            {
                'input': '打开浏览器搜索今天天气',
                'decomposition': [
                    {'step': 1, 'action': 'open_browser', 'target': '', 'reason': '打开浏览器'},
                    {'step': 2, 'action': 'search_web', 'target': '今天天气', 'reason': '搜索天气'}
                ]
            },
            {
                'input': '帮我打开iHaier给老板发个消息说项目完成了',
                'decomposition': [
                    {'step': 1, 'action': 'activate_window', 'target': 'iHaier办公平台', 'reason': '打开iHaier'},
                    {'step': 2, 'action': 'ihaier_message', 'target': '老板', 'reason': '找到联系人'},
                    {'step': 3, 'action': 'type', 'target': '项目完成了', 'reason': '输入消息内容'},
                    {'step': 4, 'action': 'send_message', 'target': '', 'reason': '发送消息'}
                ]
            }
        ]

    def plan(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        根据用户输入生成任务计划

        Args:
            user_input: 用户输入的自然语言目标描述
            context: 可选的上下文信息

        Returns:
            任务计划字典
        """
        context = context or {}

        # 1. 快速模式匹配
        for pattern, template in TASK_PATTERNS.items():
            if re.search(pattern, user_input):
                return self._apply_template(template, user_input)

        # 2. 使用 LLM 进行智能规划
        try:
            return self._llm_plan(user_input, context)
        except Exception as e:
            # 3. 回退到基于规则的分析
            return self._rule_based_plan(user_input, context)

    def _apply_template(self, template: Dict, user_input: str) -> Dict[str, Any]:
        """应用预定义模板"""
        steps = []
        for i, step in enumerate(template['steps'], 1):
            steps.append({
                'step': i,
                'action': step['action'],
                'target': self._extract_target(user_input, step['action']),
                'reason': step.get('reason', ''),
                'params': {}
            })

        return {
            'success': True,
            'original_input': user_input,
            'decomposition': steps,
            'total_steps': len(steps),
            'planning_method': 'pattern_match'
        }

    def _llm_plan(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """使用 LLM 进行任务规划"""
        # 构建提示词
        available_actions_str = json.dumps(AVAILABLE_ACTIONS, ensure_ascii=False, indent=2)
        examples_str = json.dumps(self.examples[:2], ensure_ascii=False, indent=2)

        prompt = f"""用户目标：{user_input}

可用的基础能力：
{available_actions_str}

任务分解示例：
{examples_str}

请将用户目标分解为具体的可执行步骤。只输出一个JSON对象，包含以下字段：
- decomposition: 步骤数组，每个步骤包含 step(序号)、action(动作)、target(目标)、reason(原因)
- total_steps: 总步骤数

规则：
1. 只使用上面列出的可用能力
2. 步骤应该按逻辑顺序排列
3. 动作应该是 AVAILABLE_ACTIONS 中定义的
4. 目标应该是具体的文件、应用、联系人等
5. 原因应该简洁说明为什么需要这个步骤

请只输出JSON，不要其他内容："""

        # 尝试调用 vision_proxy 作为 LLM 接口
        result = self._call_llm(prompt)

        if result:
            try:
                parsed = json.loads(result)
                return {
                    'success': True,
                    'original_input': user_input,
                    'decomposition': parsed.get('decomposition', []),
                    'total_steps': parsed.get('total_steps', 0),
                    'planning_method': 'llm'
                }
            except json.JSONDecodeError:
                pass

        # LLM 调用失败，回退到规则分析
        return self._rule_based_plan(user_input, context)

    def _call_llm(self, prompt: str) -> Optional[str]:
        """调用 LLM 接口"""
        try:
            # 尝试使用环境中的 LLM 接口
            # 这里可以接入不同的 LLM API
            # 先尝试 vision_proxy（如果有配置）
            vision_proxy = os.path.join(self.base_dir, 'vision_proxy.py')
            if os.path.exists(vision_proxy):
                # 创建一个临时文件保存 prompt
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                    f.write(prompt)
                    prompt_file = f.name

                try:
                    result = subprocess.run(
                        ['python', vision_proxy, prompt_file, '请分析这个任务规划需求并输出JSON结果'],
                        capture_output=True,
                        text=True,
                        timeout=30,
                        cwd=self.base_dir
                    )
                    if result.returncode == 0 and result.stdout:
                        return result.stdout.strip()
                except Exception:
                    pass
                finally:
                    try:
                        os.unlink(prompt_file)
                    except Exception:
                        pass
        except Exception:
            pass
        return None

    def _rule_based_plan(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """基于规则的任务规划"""
        steps = []

        # 分析用户输入中的动作和目标
        action_targets = self._analyze_input(user_input)

        for i, (action, target) in enumerate(action_targets, 1):
            steps.append({
                'step': i,
                'action': action,
                'target': target,
                'reason': self._get_action_reason(action),
                'params': {}
            })

        # 如果没有识别到任何动作，添加一个默认步骤
        if not steps:
            steps.append({
                'step': 1,
                'action': 'analyze',
                'target': user_input,
                'reason': '需要进一步分析用户意图',
                'params': {}
            })

        return {
            'success': True,
            'original_input': user_input,
            'decomposition': steps,
            'total_steps': len(steps),
            'planning_method': 'rule_based'
        }

    def _analyze_input(self, text: str) -> List[tuple]:
        """分析用户输入，提取动作和目标"""
        actions = []

        # 动作关键词映射
        action_keywords = {
            'open_app': ['打开', '启动', '运行', '开'],
            'close_app': ['关闭', '退出', '关'],
            'list_files': ['列出', '查看', '看'],
            'search_files': ['搜索', '查找', '找'],
            'organize_files': ['整理', '归类'],
            'send_email': ['发送邮件', '发邮件', '发到邮箱'],
            'send_message': ['发送消息', '发消息', '发个消息'],
            'screenshot': ['截图', '截屏'],
            'notify': ['通知', '提醒', '告诉'],
            'play_music': ['播放音乐', '放歌', '放个歌'],
            'search_web': ['搜索', '搜'],
            'click': ['点击', '按'],
            'type': ['输入', '填写'],
            'wait': ['等待', '等'],
        }

        # 识别动作
        recognized_actions = []
        for action, keywords in action_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    recognized_actions.append(action)
                    break

        # 提与目标
        targets = self._extract_targets(text)

        # 组合动作和目标
        for i, action in enumerate(recognized_actions):
            target = targets[i] if i < len(targets) else ''
            actions.append((action, target))

        # 如果只有一个动作且没有目标，添加默认目标
        if len(actions) == 1 and not actions[0][1]:
            action = actions[0][0]
            if action in ['send_email', 'send_message']:
                actions[0] = (action, '默认')

        return actions

    def _extract_targets(self, text: str) -> List[str]:
        """提取目标"""
        targets = []

        # 提取引号内容
        quoted = re.findall(r'["\']([^"\']+)["\']', text)
        targets.extend(quoted)

        # 提取特定模式的目标
        patterns = [
            r'给(.+?)发',
            r'把(.+?)整理',
            r'对(.+?)操作',
            r'(?:桌面|文件夹|目录)(.+)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            targets.extend(matches)

        return targets

    def _extract_target(self, text: str, action: str) -> str:
        """根据动作从文本中提取目标"""
        if action == 'list_files':
            if '桌面' in text:
                return 'Desktop'
            elif '下载' in text:
                return 'Downloads'
            elif '文档' in text:
                return 'Documents'

        if action in ['send_email', 'send_message']:
            # 提取接收者
            match = re.search(r'给(.+?)发', text)
            if match:
                return match.group(1)

        if action == 'search_web':
            # 提取搜索词
            match = re.search(r'(?:搜索|搜)(.+?)(?:的|情况|信息|怎么样|$)', text)
            if match:
                return match.group(1)
            # 简单提取最后一个词作为搜索词
            words = text.split()
            if words:
                return words[-1]

        if action == 'type':
            # 提取要输入的内容
            match = re.search(r'说(.+?)$|输入(.+?)$', text)
            if match:
                return match.group(1) or match.group(2)

        return ''

    def _get_action_reason(self, action: str) -> str:
        """获取动作的原因说明"""
        reasons = {
            'open_app': '需要打开应用程序',
            'close_app': '需要关闭应用程序',
            'list_files': '需要查看文件列表',
            'search_files': '需要搜索文件',
            'organize_files': '需要整理文件',
            'send_email': '需要发送邮件',
            'send_message': '需要发送消息',
            'screenshot': '需要截取屏幕',
            'notify': '需要发送通知',
            'play_music': '需要播放音乐',
            'search_web': '需要搜索网页',
            'click': '需要点击操作',
            'type': '需要输入内容',
            'wait': '需要等待操作完成',
            'activate_window': '需要激活窗口',
        }
        return reasons.get(action, '执行该操作')


class TaskPlannerEngine:
    """智能任务规划引擎主类"""

    def __init__(self):
        self.planner = LLMTaskPlanner()
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

    def plan(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        规划任务

        Args:
            user_input: 用户输入的自然语言目标描述
            context: 可选的上下文信息

        Returns:
            任务计划
        """
        return self.planner.plan(user_input, context)

    def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行任务计划

        Args:
            plan: 任务计划字典

        Returns:
            执行结果
        """
        if not plan.get('success'):
            return {
                'status': 'failed',
                'error': '无效的任务计划'
            }

        decomposition = plan.get('decomposition', [])
        if not decomposition:
            return {
                'status': 'failed',
                'error': '任务计划为空'
            }

        results = []
        for step_info in decomposition:
            try:
                result = self._execute_step(step_info)
                results.append({
                    'step': step_info.get('step'),
                    'action': step_info.get('action'),
                    'status': 'success',
                    'result': result
                })
            except Exception as e:
                results.append({
                    'step': step_info.get('step'),
                    'action': step_info.get('action'),
                    'status': 'error',
                    'error': str(e)
                })

        return {
            'status': 'completed' if all(r.get('status') == 'success' for r in results) else 'partial',
            'total_steps': len(decomposition),
            'completed_steps': sum(1 for r in results if r.get('status') == 'success'),
            'results': results
        }

    def _execute_step(self, step_info: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个步骤"""
        action = step_info.get('action')
        target = step_info.get('target', '')

        # 调用对应的能力
        if action == 'screenshot':
            return self._run_screenshot()
        elif action == 'notify':
            return self._run_notify(target)
        elif action == 'play_music':
            return self._run_play_music()
        elif action == 'open_browser':
            return self._run_open_browser(target)
        elif action == 'search_web':
            return self._run_search_web(target)
        elif action == 'list_files':
            return self._run_list_files(target)
        elif action == 'open_app':
            return self._run_open_app(target)
        else:
            return {
                'status': 'skipped',
                'message': f'动作 {action} 需要手动执行或通过其他方式执行'
            }

    def _run_screenshot(self) -> Dict[str, Any]:
        """执行截图"""
        return self._run_do_command('截图')

    def _run_notify(self, message: str) -> Dict[str, Any]:
        """执行通知"""
        return self._run_do_command(f'通知 {message}')

    def _run_play_music(self) -> Dict[str, Any]:
        """执行播放音乐"""
        return self._run_do_command('放个歌')

    def _run_open_browser(self, url: str) -> Dict[str, Any]:
        """执行打开浏览器"""
        if url:
            return self._run_do_command(f'打开浏览器 {url}')
        return self._run_do_command('打开浏览器')

    def _run_search_web(self, query: str) -> Dict[str, Any]:
        """执行网页搜索"""
        return self._run_do_command(f'搜索 {query}')

    def _run_list_files(self, path: str) -> Dict[str, Any]:
        """执行列目录"""
        if path:
            return self._run_do_command(f'列目录 {path}')
        return self._run_do_command('列目录')

    def _run_open_app(self, app_name: str) -> Dict[str, Any]:
        """执行打开应用"""
        return self._run_do_command(f'打开应用 {app_name}')

    def _run_do_command(self, command: str) -> Dict[str, Any]:
        """运行 do.py 命令"""
        do_script = os.path.join(self.base_dir, 'do.py')

        try:
            result = subprocess.run(
                ['python', do_script] + command.split(),
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.base_dir
            )
            return {
                'status': 'success' if result.returncode == 0 else 'error',
                'stdout': result.stdout[:200] if result.stdout else '',
                'stderr': result.stderr[:200] if result.stderr else ''
            }
        except subprocess.TimeoutExpired:
            return {'status': 'timeout', 'command': command}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def get_available_actions(self) -> Dict[str, Any]:
        """获取可用的动作列表"""
        return {
            'actions': AVAILABLE_ACTIONS,
            'total': len(AVAILABLE_ACTIONS)
        }


def main():
    """CLI 入口"""
    import argparse

    parser = argparse.ArgumentParser(description='智能任务理解与自动规划引擎')
    parser.add_argument('command', nargs='?', help='命令: plan/execute/actions')
    parser.add_argument('--input', '-i', help='用户输入')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    parser.add_argument('--execute', '-e', action='store_true', help='执行计划')

    args = parser.parse_args()

    engine = TaskPlannerEngine()

    if args.command == 'actions' or args.command == 'list':
        result = engine.get_available_actions()
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("可用动作 (共 {} 个):".format(result['total']))
            for action, info in result['actions'].items():
                print(f"  - {action}: {info['description']}")

    elif args.command == 'plan':
        if args.input:
            result = engine.plan(args.input)
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(f"任务计划 (共 {result['total_steps']} 步，使用 {result['planning_method']}):")
                for step in result['decomposition']:
                    print(f"  {step['step']}. {step['action']} -> {step['target']} ({step['reason']})")

                if args.execute:
                    print("\n执行计划...")
                    exec_result = engine.execute_plan(result)
                    print(f"执行状态: {exec_result['status']}")
                    print(f"完成步骤: {exec_result['completed_steps']}/{exec_result['total_steps']}")
        else:
            print("请提供 --input 参数")

    elif args.command == 'execute':
        if args.input:
            result = engine.plan(args.input)
            exec_result = engine.execute_plan(result)
            if args.json:
                print(json.dumps(exec_result, ensure_ascii=False, indent=2))
            else:
                print(f"执行状态: {exec_result['status']}")
                print(f"完成步骤: {exec_result['completed_steps']}/{exec_result['total_steps']}")
                for r in exec_result.get('results', []):
                    print(f"  步骤 {r['step']}: {r['action']} -> {r['status']}")
        else:
            print("请提供 --input 参数")

    else:
        print("智能任务理解与自动规划引擎")
        print("\n用法:")
        print("  python task_planner.py plan --input \"帮我整理桌面并发送到邮箱\"")
        print("  python task_planner.py plan --input \"搜索今天天气\" --execute")
        print("  python task_planner.py actions")
        print("\n命令:")
        print("  plan     - 规划任务")
        print("  execute  - 规划并执行任务")
        print("  actions  - 列出可用动作")


if __name__ == '__main__':
    main()