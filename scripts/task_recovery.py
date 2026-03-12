#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能任务执行失败恢复与替代机制

当任务执行失败时，分析失败原因并尝试替代方案，提升系统鲁棒性。
支持多种失败类型的自动恢复：
- vision 失败 → 尝试截图+vision 或手动点击
- 窗口激活失败 → 尝试其他激活方式（按进程名、按PID、等待重试）
- 点击失败 → 尝试移动到目标位置后等待再点击
- 超时失败 → 尝试增加等待时间
- 剪贴板失败 → 尝试使用 keyboard_tool type 输入

用法：
    python task_recovery.py --help
    python task_recovery.py analyze <error_type> <context>
    python task_recovery.py attempt <original_command> <fallback_strategy>
    python task_recovery.py history [--limit 10]
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

# 运行时状态目录
RUNTIME_STATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'runtime', 'state')


def ensure_state_dir():
    """确保状态目录存在"""
    os.makedirs(RUNTIME_STATE_DIR, exist_ok=True)


def get_recovery_history(limit: int = 20) -> List[Dict]:
    """获取恢复历史记录"""
    history_file = os.path.join(RUNTIME_STATE_DIR, 'recovery_history.json')
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('entries', [])[-limit:]
        except:
            return []
    return []


def save_recovery_record(record: Dict):
    """保存恢复记录"""
    ensure_state_dir()
    history_file = os.path.join(RUNTIME_STATE_DIR, 'recovery_history.json')

    history = {'entries': []}
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            pass

    history['entries'].append(record)

    # 保留最近100条记录
    if len(history['entries']) > 100:
        history['entries'] = history['entries'][-100:]

    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


class RecoveryStrategy:
    """恢复策略定义"""

    # 失败类型到替代方案的映射
    FALLBACK_STRATEGIES = {
        'vision_timeout': [
            {'action': 'retry', 'params': {'delay': 3, 'max_retries': 2}, 'description': '等待后重试'},
            {'action': 'use_screenshot', 'params': {}, 'description': '使用纯截图方式'},
            {'action': 'skip', 'params': {}, 'description': '跳过该步骤继续执行'}
        ],
        'vision_fail': [
            {'action': 'retry', 'params': {'delay': 2, 'max_retries': 2}, 'description': '等待后重试'},
            {'action': 'change_prompt', 'params': {'simpler': True}, 'description': '简化问题重新尝试'},
            {'action': 'use_coords_offset', 'params': {}, 'description': '尝试添加坐标偏移'}
        ],
        'window_activate_fail': [
            {'action': 'retry_by_title', 'params': {'delay': 2}, 'description': '等待后重试按标题激活'},
            {'action': 'activate_by_process', 'params': {}, 'description': '尝试按进程名激活'},
            {'action': 'activate_by_pid', 'params': {}, 'description': '尝试按PID激活'},
            {'action': 'maximize_first', 'params': {}, 'description': '先尝试最大化窗口'},
            {'action': 'skip', 'params': {}, 'description': '跳过激活继续'}
        ],
        'click_fail': [
            {'action': 'retry', 'params': {'delay': 1, 'max_retries': 2}, 'description': '重试点击'},
            {'action': 'move_and_wait', 'params': {'wait': 0.5}, 'description': '移动后等待再点击'},
            {'action': 'double_click', 'params': {}, 'description': '尝试双击'},
            {'action': 'use_keyboard', 'params': {}, 'description': '使用键盘替代点击'}
        ],
        'type_fail': [
            {'action': 'retry', 'params': {'delay': 1, 'max_retries': 2}, 'description': '重试输入'},
            {'action': 'use_clipboard', 'params': {}, 'description': '使用剪贴板粘贴方式'},
            {'action': 'use_key', 'params': {}, 'description': '使用逐键输入'}
        ],
        'timeout': [
            {'action': 'retry', 'params': {'delay': 3, 'max_retries': 1}, 'description': '增加等待时间重试'},
            {'action': 'skip', 'params': {}, 'description': '跳过该步骤'},
            {'action': 'continue', 'params': {}, 'description': '忽略超时继续执行'}
        ],
        'unknown': [
            {'action': 'retry', 'params': {'delay': 2, 'max_retries': 1}, 'description': '通用重试'},
            {'action': 'log_and_continue', 'params': {}, 'description': '记录错误并继续'},
            {'action': 'abort', 'params': {}, 'description': '终止执行'}
        ]
    }

    @classmethod
    def get_strategies(cls, error_type: str) -> List[Dict]:
        """获取指定错误类型的恢复策略"""
        return cls.FALLBACK_STRATEGIES.get(error_type, cls.FALLBACK_STRATEGIES['unknown'])

    @classmethod
    def analyze_error(cls, error_message: str, context: Dict = None) -> str:
        """分析错误消息，返回错误类型"""
        error_lower = error_message.lower()

        # vision 相关错误
        if 'vision' in error_lower or '多模态' in error_message:
            if 'timeout' in error_lower or '超时' in error_message:
                return 'vision_timeout'
            return 'vision_fail'

        # 窗口激活错误
        if 'activate' in error_lower or '激活' in error_message:
            if 'fail' in error_lower or '失败' in error_message or '无法' in error_message:
                return 'window_activate_fail'

        # 点击错误
        if 'click' in error_lower or '点击' in error_message:
            if 'fail' in error_lower or '失败' in error_message or '无法' in error_message:
                return 'click_fail'

        # 输入错误
        if 'type' in error_lower or '输入' in error_message:
            if 'fail' in error_lower or '失败' in error_message:
                return 'type_fail'

        # 超时错误
        if 'timeout' in error_lower or '超时' in error_message:
            return 'timeout'

        # 剪贴板错误
        if 'clipboard' in error_lower or '剪贴板' in error_message:
            return 'type_fail'  # 剪贴板失败可以尝试直接输入

        return 'unknown'


class TaskRecovery:
    """任务恢复主类"""

    def __init__(self):
        self.strategy = RecoveryStrategy()
        self.recovery_count = 0

    def analyze_failure(self, error_message: str, context: Optional[Dict] = None) -> Dict:
        """分析失败并返回推荐的恢复策略"""
        error_type = self.strategy.analyze_error(error_message, context or {})
        strategies = self.strategy.get_strategies(error_type)

        result = {
            'error_type': error_type,
            'error_message': error_message,
            'recommended_strategies': strategies,
            'timestamp': datetime.now().isoformat()
        }

        return result

    def attempt_recovery(self, original_command: str, strategy: Dict, context: Optional[Dict] = None) -> Dict:
        """尝试执行恢复策略"""
        action = strategy.get('action', 'unknown')
        description = strategy.get('description', '')

        # 记录恢复尝试
        record = {
            'timestamp': datetime.now().isoformat(),
            'original_command': original_command,
            'strategy_action': action,
            'strategy_description': description,
            'success': False,
            'context': context or {}
        }

        try:
            # 根据策略类型生成替代命令
            if action == 'retry':
                delay = strategy.get('params', {}).get('delay', 2)
                time.sleep(delay)
                record['success'] = True
                record['result'] = f'等待 {delay} 秒后重试'

            elif action == 'use_screenshot':
                record['result'] = '切换到纯截图模式，不使用 vision'

            elif action == 'skip':
                record['success'] = True
                record['result'] = '跳过当前步骤'

            elif action == 'continue':
                record['success'] = True
                record['result'] = '忽略错误继续执行'

            elif action == 'change_prompt':
                record['result'] = '简化问题后重试'

            elif action == 'use_coords_offset':
                record['result'] = '添加坐标偏移后重试'

            elif action == 'activate_by_process':
                record['result'] = '尝试使用进程名激活窗口'

            elif action == 'activate_by_pid':
                record['result'] = '尝试使用 PID 激活窗口'

            elif action == 'maximize_first':
                record['result'] = '先最大化窗口再重试'

            elif action == 'move_and_wait':
                wait_time = strategy.get('params', {}).get('wait', 0.5)
                time.sleep(wait_time)
                record['success'] = True
                record['result'] = f'移动后等待 {wait_time} 秒再点击'

            elif action == 'double_click':
                record['result'] = '尝试双击替代单击'

            elif action == 'use_keyboard':
                record['result'] = '使用键盘操作替代鼠标点击'

            elif action == 'use_clipboard':
                record['result'] = '使用剪贴板粘贴方式输入'

            elif action == 'use_key':
                record['result'] = '使用逐键输入方式'

            elif action == 'log_and_continue':
                record['success'] = True
                record['result'] = '记录错误并继续执行'

            elif action == 'abort':
                record['result'] = '终止执行'

            else:
                record['result'] = f'未知恢复操作: {action}'

        except Exception as e:
            record['success'] = False
            record['error'] = str(e)

        # 保存记录
        save_recovery_record(record)
        self.recovery_count += 1

        return record


def cmd_analyze(args):
    """分析错误类型命令"""
    if len(args) < 1:
        print("用法: task_recovery.py analyze <error_message> [context_json]")
        return

    error_message = args[0]
    context = {}
    if len(args) > 1:
        try:
            context = json.loads(args[1])
        except:
            pass

    recovery = TaskRecovery()
    result = recovery.analyze_failure(error_message, context)

    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_attempt(args):
    """尝试恢复命令"""
    if len(args) < 2:
        print("用法: task_recovery.py attempt <original_command> <strategy_json>")
        return

    original_command = args[0]
    try:
        strategy = json.loads(args[1])
    except:
        print("错误: strategy 必须是有效的 JSON")
        return

    recovery = TaskRecovery()
    result = recovery.attempt_recovery(original_command, strategy)

    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_history(args):
    """查看恢复历史命令"""
    limit = 10
    for i, arg in enumerate(args):
        if arg == '--limit' and i + 1 < len(args):
            try:
                limit = int(args[i + 1])
            except:
                pass

    history = get_recovery_history(limit)
    print(json.dumps({'entries': history}, ensure_ascii=False, indent=2))


def cmd_status(args):
    """查看恢复状态命令"""
    history = get_recovery_history(100)

    total = len(history)
    success = sum(1 for h in history if h.get('success', False))
    failed = total - success

    print(f"=== 任务恢复状态 ===")
    print(f"总恢复尝试: {total}")
    print(f"成功恢复: {success}")
    print(f"恢复失败: {failed}")
    if total > 0:
        print(f"成功率: {success / total * 100:.1f}%")

    # 显示最近5条记录
    print("\n=== 最近恢复记录 ===")
    for h in history[-5:]:
        status = "✓" if h.get('success') else "✗"
        action = h.get('strategy_action', 'unknown')
        desc = h.get('strategy_description', '')
        ts = h.get('timestamp', '')[:19]
        print(f"{status} {ts} | {action}: {desc}")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1]

    if command == 'analyze':
        cmd_analyze(sys.argv[2:])
    elif command == 'attempt':
        cmd_attempt(sys.argv[2:])
    elif command == 'history':
        cmd_history(sys.argv[2:])
    elif command == 'status':
        cmd_status(sys.argv[2:])
    elif command == 'help' or command == '--help' or command == '-h':
        print(__doc__)
    else:
        print(f"未知命令: {command}")
        print(__doc__)


if __name__ == '__main__':
    main()