#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能实时操作指导引擎
让系统能够实时观察用户操作、识别动作类型、预测意图，并提供智能辅助或自动完成后续步骤
实现"像人一样观察用户操作并主动帮助"的拟人化能力
"""

import json
import os
import time
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import deque
import sys

# 添加项目根目录到Python路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

# 状态文件路径
STATE_FILE = os.path.join(PROJECT_ROOT, 'runtime', 'state', 'realtime_guidance_status.json')
OPERATION_HISTORY_FILE = os.path.join(PROJECT_ROOT, 'runtime', 'state', 'realtime_operation_history.json')
GUIDANCE_CONFIG_FILE = os.path.join(PROJECT_ROOT, 'runtime', 'state', 'realtime_guidance_config.json')


class RealtimeGuidanceEngine:
    """智能实时操作指导引擎"""

    def __init__(self):
        self.is_monitoring = False
        self.monitor_thread = None
        self.operation_history = deque(maxlen=100)  # 保留最近100个操作
        self.current_context = {}
        self.predicted_intent = None
        self.suggestions = []
        self.monitor_interval = 2.0  # 监控间隔（秒）
        self._load_config()
        self._load_history()

    def _load_config(self):
        """加载配置"""
        if os.path.exists(GUIDANCE_CONFIG_FILE):
            try:
                with open(GUIDANCE_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.monitor_interval = config.get('monitor_interval', 2.0)
            except Exception:
                pass

    def _load_history(self):
        """加载历史操作"""
        if os.path.exists(OPERATION_HISTORY_FILE):
            try:
                with open(OPERATION_HISTORY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    history = data.get('operations', [])
                    self.operation_history = deque(history[-100:], maxlen=100)
            except Exception:
                pass

    def _save_history(self):
        """保存历史操作"""
        try:
            data = {
                'operations': list(self.operation_history),
                'updated_at': datetime.now().isoformat()
            }
            with open(OPERATION_HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史失败: {e}")

    def _get_active_window_info(self) -> Dict[str, Any]:
        """获取当前活动窗口信息"""
        try:
            import subprocess
            # 使用 PowerShell 获取活动窗口标题
            ps_script = '''
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")]
    public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);
}
"@
$hwnd = [Win32]::GetForegroundWindow()
$sb = New-Object System.Text.StringBuilder 256
[Win32]::GetWindowText($hwnd, $sb, 256) | Out-Null
$hwnd.ToString() + "|" + $sb.ToString()
'''
            result = subprocess.run(['powershell', '-Command', ps_script],
                                   capture_output=True, text=True, timeout=5)
            output = result.stdout.strip()
            if '|' in output:
                parts = output.split('|', 1)
                return {
                    'hwnd': parts[0],
                    'title': parts[1] if len(parts) > 1 else '',
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            pass
        return {'title': 'unknown', 'timestamp': datetime.now().isoformat()}

    def _capture_screen(self) -> Optional[str]:
        """截取屏幕"""
        try:
            screenshot_script = os.path.join(SCRIPT_DIR, 'screenshot_tool.py')
            if os.path.exists(screenshot_script):
                import subprocess
                temp_file = os.path.join(PROJECT_ROOT, 'runtime', 'temp', f'realtime_capture_{int(time.time())}.png')
                os.makedirs(os.path.dirname(temp_file), exist_ok=True)
                result = subprocess.run([sys.executable, screenshot_script, temp_file],
                                      capture_output=True, timeout=10)
                if os.path.exists(temp_file):
                    return temp_file
        except Exception as e:
            pass
        return None

    def _analyze_screen_content(self, screenshot_path: str) -> Dict[str, Any]:
        """分析屏幕内容（使用多模态）"""
        # 读取配置文件检查是否配置了 vision
        vision_config = os.path.join(PROJECT_ROOT, 'config', 'vision_config.json')
        has_vision = os.path.exists(vision_config)

        if not has_vision:
            return {'has_vision': False, 'elements': []}

        try:
            # 尝试使用 vision 分析
            vision_script = os.path.join(SCRIPT_DIR, 'vision_proxy.py')
            if os.path.exists(vision_script):
                import subprocess
                result = subprocess.run(
                    [sys.executable, vision_script, screenshot_path, "描述这个界面包含哪些可交互元素（如按钮、输入框、菜单）"],
                    capture_output=True, text=True, timeout=30
                )
                if result.returncode == 0:
                    return {
                        'has_vision': True,
                        'description': result.stdout.strip(),
                        'timestamp': datetime.now().isoformat()
                    }
        except Exception as e:
            pass
        return {'has_vision': False, 'elements': []}

    def _identify_operation_type(self, window_info: Dict, screen_analysis: Dict) -> str:
        """识别操作类型"""
        title = window_info.get('title', '').lower()

        # 基于窗口标题识别
        if 'explorer' in title or '文件夹' in title or '此电脑' in title:
            return 'file_browse'
        elif 'chrome' in title or 'edge' in title or '浏览器' in title:
            return 'web_browse'
        elif 'notepad' in title or '记事本' in title:
            return 'text_edit'
        elif 'word' in title or 'excel' in title or 'office' in title:
            return 'document_edit'
        elif 'visual studio' in title or 'code' in title:
            return 'code_edit'
        elif 'wechat' in title or '微信' in title:
            return 'chat'
        elif '钉钉' in title or 'dingtalk' in title:
            return 'chat'
        elif 'outlook' in title or '邮件' in title:
            return 'email'

        return 'unknown'

    def _predict_intent(self, operation_type: str, history: List[Dict]) -> Optional[str]:
        """基于历史预测用户意图"""
        if not history:
            return None

        # 简单的模式识别：基于最近的操作序列
        recent_types = [op.get('type') for op in history[-5:]]

        # 文件浏览模式
        if operation_type == 'file_browse':
            if 'file_browse' in recent_types:
                return '文件浏览中，可能在查找或打开文件'
            return '开始浏览文件'

        # 网页浏览模式
        elif operation_type == 'web_browse':
            if 'web_browse' in recent_types:
                return '浏览网页，可能在搜索或阅读内容'
            return '开始浏览网页'

        # 聊天模式
        elif operation_type == 'chat':
            if 'chat' in recent_types:
                return '聊天中，可能在发送消息'
            return '开始聊天'

        # 文档编辑
        elif operation_type == 'document_edit':
            if 'document_edit' in recent_types:
                return '编辑文档中'
            return '开始编辑文档'

        return None

    def _generate_suggestions(self, operation_type: str, intent: Optional[str]) -> List[Dict[str, Any]]:
        """生成智能建议"""
        suggestions = []

        if operation_type == 'file_browse':
            suggestions.append({
                'type': 'quick_action',
                'title': '文件浏览建议',
                'content': '可以使用「打开文件」或「搜索文件」来快速定位',
                'action': '如果需要找文件，可以尝试说「帮我找 xxx 文件」'
            })
        elif operation_type == 'web_browse':
            suggestions.append({
                'type': 'quick_action',
                'title': '网页浏览建议',
                'content': '我可以帮你搜索或打开特定网站',
                'action': '如果需要搜索，可以说「帮我搜索 xxx」'
            })
        elif operation_type == 'chat':
            suggestions.append({
                'type': 'quick_action',
                'title': '聊天辅助',
                'content': '我可以帮你快速输入内容或发送消息',
                'action': '可以直接告诉我需要发送的内容'
            })
        elif operation_type == 'document_edit':
            suggestions.append({
                'type': 'quick_action',
                'title': '文档编辑辅助',
                'content': '我可以帮你编辑、排版或保存文档',
                'action': '需要格式化或保存可以说「帮我xxx」'
            })

        # 基于意图的建议
        if intent:
            suggestions.append({
                'type': 'context',
                'title': '当前状态',
                'content': intent,
                'action': None
            })

        return suggestions

    def capture_and_analyze(self) -> Dict[str, Any]:
        """捕获并分析当前屏幕状态"""
        # 获取活动窗口
        window_info = self._get_active_window_info()

        # 截取屏幕
        screenshot_path = self._capture_screen()

        # 分析屏幕内容
        screen_analysis = {}
        if screenshot_path:
            screen_analysis = self._analyze_screen_content(screenshot_path)

        # 识别操作类型
        operation_type = self._identify_operation_type(window_info, screen_analysis)

        # 记录操作
        operation_record = {
            'type': operation_type,
            'window': window_info.get('title', ''),
            'timestamp': datetime.now().isoformat(),
            'screen_analysis': screen_analysis.get('has_vision', False)
        }
        self.operation_history.append(operation_record)

        # 预测意图
        predicted_intent = self._predict_intent(operation_type, list(self.operation_history))

        # 生成建议
        suggestions = self._generate_suggestions(operation_type, predicted_intent)

        # 保存状态
        self._save_history()
        self._save_status()

        return {
            'operation_type': operation_type,
            'window_title': window_info.get('title', ''),
            'intent': predicted_intent,
            'suggestions': suggestions,
            'has_vision': screen_analysis.get('has_vision', False),
            'timestamp': datetime.now().isoformat()
        }

    def _save_status(self):
        """保存状态"""
        try:
            state = {
                'is_monitoring': self.is_monitoring,
                'current_operation_type': self.predicted_intent,
                'suggestions': self.suggestions,
                'history_count': len(self.operation_history),
                'updated_at': datetime.now().isoformat()
            }
            with open(STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存状态失败: {e}")

    def start_monitoring(self):
        """开始监控"""
        if self.is_monitoring:
            return {'status': 'already_running'}

        self.is_monitoring = True

        def monitor_loop():
            while self.is_monitoring:
                try:
                    result = self.capture_and_analyze()
                    # 可以在这里添加通知逻辑
                except Exception as e:
                    pass
                time.sleep(self.monitor_interval)

        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()

        self._save_status()
        return {'status': 'started', 'interval': self.monitor_interval}

    def stop_monitoring(self):
        """停止监控"""
        if not self.is_monitoring:
            return {'status': 'not_running'}

        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

        self._save_status()
        return {'status': 'stopped'}

    def get_current_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        return {
            'is_monitoring': self.is_monitoring,
            'history_count': len(self.operation_history),
            'last_operation': list(self.operation_history)[-1] if self.operation_history else None,
            'status_file': STATE_FILE
        }

    def get_suggestions(self) -> List[Dict[str, Any]]:
        """获取当前建议"""
        # 触发一次分析获取最新建议
        result = self.capture_and_analyze()
        return result.get('suggestions', [])

    def get_operation_context(self) -> Dict[str, Any]:
        """获取操作上下文"""
        return {
            'recent_operations': list(self.operation_history)[-10:],
            'operation_types': list(set([op.get('type') for op in self.operation_history])),
            'timestamp': datetime.now().isoformat()
        }

    def clear_history(self):
        """清除历史记录"""
        self.operation_history.clear()
        self._save_history()
        return {'status': 'cleared'}


def main():
    """主函数"""
    engine = RealtimeGuidanceEngine()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python realtime_guidance_engine.py status    - 查看当前状态")
        print("  python realtime_guidance_engine.py analyze   - 立即分析当前屏幕")
        print("  python realtime_guidance_engine.py start     - 开始监控")
        print("  python realtime_guidance_engine.py stop      - 停止监控")
        print("  python realtime_guidance_engine.py suggestions - 获取建议")
        print("  python realtime_guidance_engine.py context   - 获取操作上下文")
        print("  python realtime_guidance_engine.py clear     - 清除历史")
        return

    command = sys.argv[1]

    if command == 'status':
        result = engine.get_current_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == 'analyze':
        result = engine.capture_and_analyze()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == 'start':
        result = engine.start_monitoring()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == 'stop':
        result = engine.stop_monitoring()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == 'suggestions':
        result = engine.get_suggestions()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == 'context':
        result = engine.get_operation_context()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == 'clear':
        result = engine.clear_history()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Unknown command: {command}")


if __name__ == '__main__':
    main()