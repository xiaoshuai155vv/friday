#!/usr/bin/env python3
"""
智能创意工作流自动生成与执行引擎
基于用户意图自动生成复杂的可执行工作流，并自动执行，实现从想法到执行的完整闭环

Version: 1.0.0
"""

import json
import os
import sys
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path

# 添加 scripts 目录到路径
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

try:
    import do
except ImportError:
    do = None


class CreativeWorkflowGenerator:
    """创意工作流自动生成与执行引擎"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.capabilities_file = PROJECT_ROOT / "references" / "capabilities.md"
        self.plans_dir = PROJECT_ROOT / "assets" / "plans"
        self.runtime_state_dir = PROJECT_ROOT / "runtime" / "state"

        # 加载能力清单
        self.capabilities = self._load_capabilities()

        # 工作流历史
        self.workflow_history_file = self.runtime_state_dir / "creative_workflow_history.json"
        self.workflow_history = self._load_history()

    def _load_capabilities(self):
        """加载能力清单"""
        capabilities = []
        try:
            if self.capabilities_file.exists():
                content = self.capabilities_file.read_text(encoding='utf-8')
                # 提取命令表格中的命令
                matches = re.findall(r'\|\s*([^|]+?)\s*\|\s*`([^`]+)`\s*\|', content)
                for name, cmd in matches:
                    capabilities.append({
                        'name': name.strip(),
                        'command': cmd.strip()
                    })
        except Exception as e:
            print(f"加载能力清单失败: {e}")
        return capabilities

    def _load_history(self):
        """加载工作流历史"""
        try:
            if self.workflow_history_file.exists():
                with open(self.workflow_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {"workflows": [], "stats": {"total": 0, "success": 0, "failed": 0}}

    def _save_history(self):
        """保存工作流历史"""
        try:
            self.runtime_state_dir.mkdir(parents=True, exist_ok=True)
            with open(self.workflow_history_file, 'w', encoding='utf-8') as f:
                json.dump(self.workflow_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史失败: {e}")

    def analyze_intent(self, user_input):
        """
        深度理解用户意图

        Args:
            user_input: 用户输入的自然语言描述

        Returns:
            dict: 解析后的意图结构
        """
        # 转换为小写进行匹配
        input_lower = user_input.lower()

        # 意图类型分类
        intent_types = []

        # 媒体相关
        if any(kw in input_lower for kw in ['播放', '放', '听', '音乐', '歌']):
            intent_types.append('media')

        # 办公相关
        if any(kw in input_lower for kw in ['文档', '编辑', '写', '新建', '保存']):
            intent_types.append('office')

        # 沟通相关
        if any(kw in input_lower for kw in ['发消息', '聊天', '通知', '联系']):
            intent_types.append('communication')

        # 信息获取
        if any(kw in input_lower for kw in ['查', '找', '搜索', '看', '获取']):
            intent_types.append('information')

        # 系统操作
        if any(kw in input_lower for kw in ['打开', '关闭', '启动', '运行', '执行']):
            intent_types.append('system')

        # 自动化任务
        if any(kw in input_lower for kw in ['定时', '自动', '定期', '循环']):
            intent_types.append('automation')

        # 提取关键实体
        entities = {
            'apps': self._extract_apps(user_input),
            'files': self._extract_files(user_input),
            'times': self._extract_times(user_input),
            'actions': self._extract_actions(user_input)
        }

        return {
            'raw_input': user_input,
            'intent_types': intent_types,
            'entities': entities,
            'complexity': self._estimate_complexity(user_input)
        }

    def _extract_apps(self, text):
        """提取应用名称"""
        apps = []
        app_keywords = ['微信', '钉钉', '邮箱', 'outlook', 'notepad', '记事本', '浏览器',
                       'chrome', 'edge', 'vscode', 'word', 'excel', 'powerpoint',
                       '网易云', '音乐', '播放器', 'ihaier', '办公平台']

        for app in app_keywords:
            if app.lower() in text.lower():
                apps.append(app)
        return apps

    def _extract_files(self, text):
        """提取文件路径"""
        # 简单的文件路径提取
        file_patterns = [
            r'([A-Za-z]:\\[\w\\\.]+)',  # Windows 路径
            r'([\w\-]+\.[\w]+)'  # 文件名
        ]

        files = []
        for pattern in file_patterns:
            matches = re.findall(pattern, text)
            files.extend(matches)
        return files

    def _extract_times(self, text):
        """提取时间信息"""
        times = []
        time_patterns = [
            (r'(\d+)\s*秒', 'seconds'),
            (r'(\d+)\s*分钟', 'minutes'),
            (r'(\d+)\s*小时', 'hours'),
            (r'(\d+)\s*天', 'days'),
        ]

        for pattern, unit in time_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                times.append({'value': int(match), 'unit': unit})

        return times

    def _extract_actions(self, text):
        """提取动作"""
        action_keywords = {
            'open': ['打开', '启动', '运行'],
            'close': ['关闭', '退出', '停止'],
            'create': ['新建', '创建', '生成'],
            'read': ['读取', '查看', '浏览'],
            'write': ['写入', '编辑', '修改', '保存'],
            'send': ['发送', '发', '推送'],
            'copy': ['复制', '拷贝'],
            'paste': ['粘贴', '黏贴'],
        }

        actions = []
        for action, keywords in action_keywords.items():
            if any(kw in text for kw in keywords):
                actions.append(action)

        return actions

    def _estimate_complexity(self, text):
        """估算任务复杂度"""
        # 基于关键词数量和句子结构估算
        complexity_score = 1

        # 多步骤指示词
        multi_step_keywords = ['然后', '再', '接着', '之后', '首先', '其次', '最后', '和', '与', '以及']
        for kw in multi_step_keywords:
            if kw in text:
                complexity_score += 1

        # 条件词
        conditional_keywords = ['如果', '当', '当...时', '条件']
        for kw in conditional_keywords:
            if kw in text:
                complexity_score += 1

        return min(complexity_score, 5)  # 最高5级

    def generate_workflow(self, intent):
        """
        基于意图生成工作流

        Args:
            intent: analyze_intent 返回的意图结构

        Returns:
            dict: 可执行的工作流计划
        """
        workflow = {
            'name': f"创意工作流_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'description': f"基于用户输入「{intent['raw_input']}」自动生成的工作流",
            'created_at': datetime.now().isoformat(),
            'steps': [],
            'metadata': {
                'intent': intent,
                'complexity': intent['complexity']
            }
        }

        intent_types = intent.get('intent_types', [])

        # 根据意图类型生成对应步骤
        if 'media' in intent_types:
            workflow['steps'].extend(self._generate_media_steps(intent))

        if 'office' in intent_types:
            workflow['steps'].extend(self._generate_office_steps(intent))

        if 'communication' in intent_types:
            workflow['steps'].extend(self._generate_communication_steps(intent))

        if 'information' in intent_types:
            workflow['steps'].extend(self._generate_information_steps(intent))

        if 'system' in intent_types:
            workflow['steps'].extend(self._generate_system_steps(intent))

        if 'automation' in intent_types:
            workflow['steps'].extend(self._generate_automation_steps(intent))

        # 如果没有匹配到任何类型，使用通用步骤
        if not workflow['steps']:
            workflow['steps'] = self._generate_generic_steps(intent)

        return workflow

    def _generate_media_steps(self, intent):
        """生成媒体相关步骤"""
        steps = []
        apps = intent['entities'].get('apps', [])

        # 查找音乐播放器
        has_music = any(app in ['网易云', '音乐', '播放器'] for app in apps)

        if has_music or '音乐' in intent['raw_input'] or '歌' in intent['raw_input']:
            steps.append({
                'do': 'run',
                'script': 'do.py',
                'args': ['已安装应用'],
                'description': '获取已安装应用列表'
            })
            steps.append({
                'do': 'wait',
                'seconds': 2,
                'description': '等待应用列表加载'
            })

        return steps

    def _generate_office_steps(self, intent):
        """生成办公相关步骤"""
        steps = []
        actions = intent['entities'].get('actions', [])

        if 'create' in actions:
            steps.append({
                'do': 'run',
                'script': 'do.py',
                'args': ['打开记事本'],
                'description': '打开记事本'
            })
            steps.append({
                'do': 'wait',
                'seconds': 2,
                'description': '等待记事本启动'
            })

        return steps

    def _generate_communication_steps(self, intent):
        """生成沟通相关步骤"""
        steps = []
        apps = intent['entities'].get('apps', [])

        # 检查是否需要打开通讯应用
        if not apps:
            # 默认尝试打开微信或钉钉
            steps.append({
                'do': 'run',
                'script': 'do.py',
                'args': ['打开应用', '微信'],
                'description': '打开微信'
            })

        return steps

    def _generate_information_steps(self, intent):
        """生成信息获取步骤"""
        steps = []
        apps = intent['entities'].get('apps', [])

        # 如果需要获取系统信息
        if any(kw in intent['raw_input'] for kw in ['系统信息', '网络', '进程']):
            steps.append({
                'do': 'run',
                'script': 'do.py',
                'args': ['网络信息'],
                'description': '获取网络信息'
            })

        return steps

    def _generate_system_steps(self, intent):
        """生成系统操作步骤"""
        steps = []
        apps = intent['entities'].get('apps', [])

        if apps:
            for app in apps:
                steps.append({
                    'do': 'run',
                    'script': 'do.py',
                    'args': ['打开应用', app],
                    'description': f'打开应用: {app}'
                })
                steps.append({
                    'do': 'wait',
                    'seconds': 2,
                    'description': f'等待 {app} 启动'
                })

        return steps

    def _generate_automation_steps(self, intent):
        """生成自动化步骤"""
        steps = []
        times = intent['entities'].get('times', [])

        if times:
            # 使用定时器
            for time_info in times:
                value = time_info['value']
                unit = time_info['unit']

                if unit == 'seconds':
                    steps.append({
                        'do': 'run',
                        'script': 'timer_tool.py',
                        'args': [str(value)],
                        'description': f'等待 {value} 秒'
                    })

        return steps

    def _generate_generic_steps(self, intent):
        """生成通用步骤"""
        # 尝试使用 do.py 理解并执行
        return [{
            'do': 'run',
            'script': 'do.py',
            'args': intent['raw_input'].split(),
            'description': f'执行用户请求: {intent["raw_input"]}'
        }]

    def execute_workflow(self, workflow, dry_run=False):
        """
        执行工作流

        Args:
            workflow: 生成的工作流
            dry_run: 是否仅预览不执行

        Returns:
            dict: 执行结果
        """
        result = {
            'workflow_name': workflow['name'],
            'status': 'success',
            'steps_executed': 0,
            'steps_failed': 0,
            'results': [],
            'start_time': datetime.now().isoformat()
        }

        if dry_run:
            result['status'] = 'dry_run'
            result['message'] = '仅预览模式，未实际执行'
            result['workflow'] = workflow
            return result

        # 执行每个步骤
        for i, step in enumerate(workflow.get('steps', [])):
            step_result = {
                'step': i + 1,
                'description': step.get('description', ''),
                'status': 'pending'
            }

            try:
                step_result = self._execute_step(step)
                if step_result['status'] == 'success':
                    result['steps_executed'] += 1
                else:
                    result['steps_failed'] += 1

                result['results'].append(step_result)

                # 等待指定时间
                wait_seconds = step.get('wait', step.get('seconds', 0))
                if wait_seconds > 0:
                    time.sleep(wait_seconds)

            except Exception as e:
                step_result['status'] = 'error'
                step_result['error'] = str(e)
                result['steps_failed'] += 1
                result['results'].append(step_result)

                # 继续执行其他步骤
                continue

        result['end_time'] = datetime.now().isoformat()

        if result['steps_failed'] > 0:
            result['status'] = 'partial' if result['steps_executed'] > 0 else 'failed'
        else:
            result['status'] = 'success'

        # 记录到历史
        self._record_workflow(workflow, result)

        return result

    def _execute_step(self, step):
        """执行单个步骤"""
        result = {
            'status': 'pending',
            'description': step.get('description', '')
        }

        do_action = step.get('do', '')

        if do_action == 'run':
            # 执行脚本
            script = step.get('script', '')
            args = step.get('args', [])

            if script == 'do.py':
                # 使用 do.py 执行
                cmd = [sys.executable, str(SCRIPT_DIR / 'do.py')] + args
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                result['output'] = proc.stdout
                result['returncode'] = proc.returncode
                result['status'] = 'success' if proc.returncode == 0 else 'failed'

            elif script.endswith('.py'):
                # 执行 Python 脚本
                cmd = [sys.executable, str(SCRIPT_DIR / script)] + args
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                result['output'] = proc.stdout
                result['returncode'] = proc.returncode
                result['status'] = 'success' if proc.returncode == 0 else 'failed'

        elif do_action == 'wait':
            # 等待
            seconds = step.get('seconds', 1)
            time.sleep(seconds)
            result['status'] = 'success'
            result['waited'] = seconds

        elif do_action == 'screenshot':
            # 截图
            result['status'] = 'success'

        elif do_action == 'click':
            # 点击
            x = step.get('x', 0)
            y = step.get('y', 0)
            result['status'] = 'success'
            result['clicked'] = f"({x}, {y})"

        else:
            result['status'] = 'unknown_action'
            result['message'] = f'未知动作: {do_action}'

        return result

    def _record_workflow(self, workflow, result):
        """记录工作流到历史"""
        record = {
            'workflow': workflow,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }

        self.workflow_history['workflows'].append(record)
        self.workflow_history['stats']['total'] += 1

        if result['status'] == 'success':
            self.workflow_history['stats']['success'] += 1
        elif result['status'] == 'failed':
            self.workflow_history['stats']['failed'] += 1

        # 保留最近100条
        if len(self.workflow_history['workflows']) > 100:
            self.workflow_history['workflows'] = self.workflow_history['workflows'][-100:]

        self._save_history()

    def get_suggestions(self, user_input):
        """
        获取创意建议

        Args:
            user_input: 用户输入

        Returns:
            list: 建议列表
        """
        suggestions = []
        intent = self.analyze_intent(user_input)

        # 基于意图类型提供建议
        if 'media' in intent['intent_types']:
            suggestions.append({
                'type': 'workflow',
                'title': '播放音乐',
                'description': '自动查找并播放音乐播放器'
            })

        if 'office' in intent['intent_types']:
            suggestions.append({
                'type': 'workflow',
                'title': '创建文档',
                'description': '打开合适的应用创建文档'
            })

        if 'automation' in intent['intent_types']:
            suggestions.append({
                'type': 'workflow',
                'title': '设置定时任务',
                'description': '创建自动化定时执行任务'
            })

        # 提供一些通用创意建议
        suggestions.extend([
            {
                'type': 'idea',
                'title': '批量文件处理',
                'description': '对多个文件执行相同操作'
            },
            {
                'type': 'idea',
                'title': '多应用协同',
                'description': '同时操作多个应用完成复杂任务'
            }
        ])

        return suggestions


def generate_creative_workflow(user_input, auto_execute=False):
    """
    便捷函数：基于用户输入生成并可选执行创意工作流

    Args:
        user_input: 用户自然语言输入
        auto_execute: 是否自动执行

    Returns:
        dict: 工作流或执行结果
    """
    generator = CreativeWorkflowGenerator()

    # 分析意图
    intent = generator.analyze_intent(user_input)

    # 生成工作流
    workflow = generator.generate_workflow(intent)

    if auto_execute:
        # 执行工作流
        result = generator.execute_workflow(workflow)
        return result
    else:
        # 返回工作流供预览
        return workflow


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description='智能创意工作流自动生成与执行引擎')
    parser.add_argument('input', nargs='?', help='用户自然语言输入')
    parser.add_argument('--execute', '-e', action='store_true', help='自动执行生成的工作流')
    parser.add_argument('--dry-run', '-d', action='store_true', help='仅预览不执行')
    parser.add_argument('--suggest', '-s', action='store_true', help='获取创意建议')
    parser.add_argument('--interactive', '-i', action='store_true', help='交互模式')

    args = parser.parse_args()

    generator = CreativeWorkflowGenerator()

    if args.interactive:
        # 交互模式
        print("=== 智能创意工作流自动生成与执行引擎 ===")
        print("输入您想做的事情，我会帮您生成并执行工作流")
        print("输入 'quit' 或 'exit' 退出\n")

        while True:
            user_input = input("\n> ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break

            if not user_input:
                continue

            # 分析意图
            print("\n[分析意图...]")
            intent = generator.analyze_intent(user_input)
            print(f"意图类型: {', '.join(intent['intent_types']) or '未识别'}")
            print(f"复杂度: {intent['complexity']} 级")
            print(f"实体: {intent['entities']}")

            # 生成工作流
            print("\n[生成工作流...]")
            workflow = generator.generate_workflow(intent)
            print(f"工作流名称: {workflow['name']}")
            print(f"步骤数: {len(workflow['steps'])}")

            for i, step in enumerate(workflow['steps'], 1):
                print(f"  {i}. {step.get('description', step)}")

            # 确认执行
            confirm = input("\n是否执行? (y/n): ").strip().lower()
            if confirm == 'y':
                print("\n[执行工作流...]")
                result = generator.execute_workflow(workflow)
                print(f"状态: {result['status']}")
                print(f"成功: {result['steps_executed']}, 失败: {result['steps_failed']}")

    elif args.suggest:
        # 创意建议模式
        suggestions = generator.get_suggestions(args.input or "")
        print("=== 创意建议 ===")
        for i, s in enumerate(suggestions, 1):
            print(f"{i}. {s['title']} - {s['description']}")

    elif args.input:
        # 命令行模式
        user_input = args.input

        if args.dry_run:
            # 仅预览
            workflow = generate_creative_workflow(user_input, auto_execute=False)
            print(json.dumps(workflow, ensure_ascii=False, indent=2))
        elif args.execute:
            # 自动执行
            result = generate_creative_workflow(user_input, auto_execute=True)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            # 默认预览
            workflow = generate_creative_workflow(user_input, auto_execute=False)
            print(json.dumps(workflow, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == '__main__':
    main()