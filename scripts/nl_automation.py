#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自然语言自动化模块
将自然语言任务描述解析为可执行的系统操作步骤
"""

import re
import json
import os
import sys
from typing import List, Dict, Tuple, Optional

# 添加项目路径以便导入其他模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 尝试导入上下文记忆模块
try:
    from context_memory import ContextMemory
    CONTEXT_MEMORY_AVAILABLE = True
except ImportError:
    CONTEXT_MEMORY_AVAILABLE = False


class NaturalLanguageAutomation:
    """自然语言自动化处理器"""

    def __init__(self):
        if CONTEXT_MEMORY_AVAILABLE:
            self.context_memory = ContextMemory()
        else:
            self.context_memory = None

        # 预定义的意图模式
        self.intent_patterns = {
            'open_app': [
                r'(打开|启动|运行|开启)(.*)',
                r'(.*)应用',
                r'启动(.*)程序'
            ],
            'browse_web': [
                r'(浏览|访问|打开|查看)(.*)网站',
                r'访问(.*)网址',
                r'打开(.*)网页'
            ],
            'send_message': [
                r'(给|向)(.*)(发消息|发短信|发邮件)',
                r'(发|发送)(.*)给(.*)',
                r'给(.*)发(.*)'
            ],
            'file_operation': [
                r'(移动|复制|删除|重命名)(.*)文件',
                r'(查找|搜索)(.*)文件',
                r'创建(.*)文件'
            ],
            'system_task': [
                r'(设置|调整|更改)(.*)设置',
                r'(关闭|重启|休眠|睡眠)(.*)',
                r'执行(.*)任务'
            ]
        }

    def parse_natural_language(self, intent: str) -> Dict:
        """
        解析自然语言意图，返回结构化任务描述

        Args:
            intent: 用户输入的自然语言意图

        Returns:
            包含任务信息的字典
        """
        # 1. 检查上下文记忆
        context = {}
        if self.context_memory and hasattr(self.context_memory, "get_context"):
            try:
                context = self.context_memory.get_context()
            except Exception:
                context = {}

        # 2. 识别意图类型
        intent_type = self._identify_intent_type(intent)

        # 3. 提取关键信息
        extracted_info = self._extract_key_info(intent, intent_type)

        # 4. 构建执行计划
        plan = self._build_execution_plan(intent_type, extracted_info, context)

        return {
            'intent': intent,
            'intent_type': intent_type,
            'extracted_info': extracted_info,
            'plan': plan,
            'context_used': context
        }

    def _identify_intent_type(self, intent: str) -> str:
        """识别意图类型"""
        intent = intent.lower()

        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, intent):
                    return intent_type

        # 默认意图
        return 'general_task'

    def _extract_key_info(self, intent: str, intent_type: str) -> Dict:
        """提取关键信息"""
        info = {}

        # 根据意图类型提取特定信息
        if intent_type == 'open_app':
            # 提取应用名称
            match = re.search(r'(打开|启动|运行|开启)(.*)', intent)
            if match:
                app_name = match.group(2).strip()
                info['app_name'] = app_name

        elif intent_type == 'browse_web':
            # 提取网站名称或网址
            match = re.search(r'(浏览|访问|打开|查看)(.*)网站', intent)
            if match:
                website = match.group(2).strip()
                info['website'] = website

        elif intent_type == 'send_message':
            # 提取接收方和消息内容
            match = re.search(r'(给|向)(.*)(发消息|发短信|发邮件)', intent)
            if match:
                receiver = match.group(2).strip()
                info['receiver'] = receiver

        elif intent_type == 'file_operation':
            # 提取操作类型和文件名
            match = re.search(r'(移动|复制|删除|重命名)(.*)文件', intent)
            if match:
                operation = match.group(1)
                filename = match.group(2).strip()
                info['operation'] = operation
                info['filename'] = filename

        return info

    def _build_execution_plan(self, intent_type: str, info: Dict, context: Dict) -> List[Dict]:
        """根据意图类型和信息构建执行计划"""
        plan = []

        # 根据意图类型生成对应的步骤
        if intent_type == 'open_app':
            app_name = info.get('app_name', '')
            if app_name:
                plan.append({
                    'step': 'launch_app',
                    'app_name': app_name,
                    'description': f'启动应用程序: {app_name}'
                })

        elif intent_type == 'browse_web':
            website = info.get('website', '')
            if website:
                plan.append({
                    'step': 'launch_browser',
                    'website': website,
                    'description': f'打开浏览器访问网站: {website}'
                })

        elif intent_type == 'send_message':
            receiver = info.get('receiver', '')
            if receiver:
                plan.append({
                    'step': 'prepare_message',
                    'receiver': receiver,
                    'description': f'准备给 {receiver} 发送消息'
                })

        elif intent_type == 'file_operation':
            operation = info.get('operation', '')
            filename = info.get('filename', '')
            if operation and filename:
                plan.append({
                    'step': f'file_{operation}',
                    'filename': filename,
                    'description': f'{operation}文件: {filename}'
                })

        else:
            # 通用任务处理
            plan.append({
                'step': 'execute_general_task',
                'description': '执行通用任务'
            })

        return plan

    def execute_task(self, intent: str) -> Dict:
        """
        执行自然语言任务

        Args:
            intent: 自然语言任务描述

        Returns:
            执行结果
        """
        # 解析任务
        parsed_task = self.parse_natural_language(intent)

        # 执行计划
        execution_results = []
        for step in parsed_task['plan']:
            try:
                # 这里应该调用具体的执行函数
                # 为了演示，我们只记录执行过程
                execution_results.append({
                    'step': step['step'],
                    'description': step['description'],
                    'status': 'completed',
                    'error': None
                })
            except Exception as e:
                execution_results.append({
                    'step': step['step'],
                    'description': step['description'],
                    'status': 'failed',
                    'error': str(e)
                })

        return {
            'original_intent': intent,
            'parsed_task': parsed_task,
            'execution_results': execution_results,
            'success': True
        }

# 示例使用
if __name__ == "__main__":
    # 创建实例
    nl_automation = NaturalLanguageAutomation()

    # 测试自然语言解析
    test_intents = [
        "打开网易云音乐",
        "浏览百度网站",
        "给张三发消息",
        "移动文档到桌面"
    ]

    for intent in test_intents:
        result = nl_automation.parse_natural_language(intent)
        print(f"输入: {intent}")
        print(f"解析结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        print("-" * 50)