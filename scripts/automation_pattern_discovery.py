#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能自动化模式发现与场景生成引擎

让系统能够从用户行为和执行历史中自动发现可自动化的重复模式，
主动创建新场景计划（JSON），实现从被动响应到主动创造的进化。

功能：
1. 行为模式分析：分析 run_plan 历史、behavior_log、用户交互记录
2. 可自动化模式识别：发现重复执行的操作序列
3. 场景计划自动生成：根据模式自动生成 JSON 场景计划
4. 主动推荐功能：向用户推荐新发现的自动化场景
5. 引擎深度协同（round 143）：与 task_preference_engine 集成，实现从模式发现到偏好学习的完整闭环
"""

import os
import sys
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict
from typing import List, Dict, Optional, Tuple

# 导入任务偏好引擎
SCRIPT_DIR = Path(__file__).parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
try:
    from task_preference_engine import TaskPreferenceEngine
except ImportError:
    TaskPreferenceEngine = None

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"
PLANS_DIR = PROJECT_ROOT / "assets" / "plans"


class AutomationPatternDiscovery:
    """智能自动化模式发现与场景生成引擎"""

    def __init__(self):
        self.min_pattern_occurrences = 2  # 最小重复次数
        self.analysis_days = 7  # 分析最近7天的数据
        self.max_steps_in_pattern = 5  # 最大步骤数

    def analyze_behavior_logs(self) -> Dict:
        """分析行为日志，提取操作序列"""
        patterns = defaultdict(list)
        recent_cutoff = datetime.now() - timedelta(days=self.analysis_days)

        # 读取行为日志
        log_files = list(LOGS_DIR.glob("behavior_*.log"))
        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.strip().split('\n')

                for line in lines:
                    if not line.strip():
                        continue
                    try:
                        # 解析日志行
                        if ': ' in line:
                            parts = line.split(': ', 2)
                            if len(parts) >= 3:
                                timestamp_str = parts[0]
                                phase = parts[1]
                                desc = parts[2]

                                # 提取操作关键词
                                keywords = self._extract_keywords(desc)
                                if keywords:
                                    patterns[phase].append({
                                        'keywords': keywords,
                                        'description': desc,
                                        'timestamp': timestamp_str
                                    })
                    except Exception:
                        continue
            except Exception:
                continue

        return dict(patterns)

    def _extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键操作词"""
        # 定义关键操作词
        action_keywords = [
            'run_plan', 'execute', 'launch', '打开', '点击', '输入', '打开应用',
            'activate', 'maximize', 'screenshot', 'vision', 'click', 'type',
            'scroll', 'wait', 'key', '打开文件', '发送', '搜索', '创建', '删除',
            '移动', '复制', '重命名', '发送消息', '查看', '关闭'
        ]

        found = []
        text_lower = text.lower()
        for kw in action_keywords:
            if kw.lower() in text_lower:
                found.append(kw)

        return found

    def analyze_run_plan_history(self) -> Dict:
        """分析 run_plan 执行历史"""
        history_data = {}

        # 读取 recent_logs.json
        recent_logs_file = STATE_DIR / "recent_logs.json"
        if recent_logs_file.exists():
            try:
                with open(recent_logs_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'entries' in data:
                        history_data['entries'] = data['entries']
            except Exception:
                pass

        # 读取 evolution 历史
        evolution_files = list(STATE_DIR.glob("evolution_completed_*.json"))
        evolution_history = []
        for ef in evolution_files:
            try:
                with open(ef, 'r', encoding='utf-8') as f:
                    evolution_history.append(json.load(f))
            except Exception:
                continue

        if evolution_history:
            history_data['evolution_history'] = evolution_history

        return history_data

    def find_repeated_patterns(self, behavior_data: Dict) -> List[Dict]:
        """发现重复的操作模式"""
        # 统计操作序列
        sequence_counter = Counter()

        # 分析每个阶段的日志
        for phase, entries in behavior_data.items():
            sequences = []
            current_sequence = []

            for entry in entries:
                keywords = entry.get('keywords', [])
                if keywords:
                    current_sequence.append(tuple(keywords))
                    if len(current_sequence) >= 2:
                        sequences.append(tuple(current_sequence))

            # 统计序列出现次数
            for seq in sequences:
                sequence_counter[seq] += 1

        # 找出重复次数超过阈值的模式
        repeated_patterns = []
        for seq, count in sequence_counter.items():
            if count >= self.min_pattern_occurrences:
                repeated_patterns.append({
                    'sequence': list(seq),
                    'occurrences': count,
                    'score': count * len(seq)  # 综合评分
                })

        # 按评分排序
        repeated_patterns.sort(key=lambda x: x['score'], reverse=True)

        return repeated_patterns[:10]  # 返回前10个模式

    def generate_scene_plan(self, pattern: Dict) -> Optional[Dict]:
        """根据模式自动生成场景计划"""
        sequence = pattern.get('sequence', [])
        if not sequence:
            return None

        # 构建场景计划
        steps = []
        for i, action in enumerate(sequence):
            if isinstance(action, tuple):
                action = list(action)

            # 将操作转换为场景计划步骤
            step = self._action_to_step(action, i)
            if step:
                steps.append(step)

        if not steps:
            return None

        # 生成场景计划
        plan = {
            "name": f"自动发现的场景_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "description": f"自动发现的重复模式，包含 {len(steps)} 个步骤，已执行 {pattern.get('occurrences', 0)} 次",
            "triggers": [self._generate_trigger_keyword(steps)],
            "steps": steps
        }

        return plan

    def _action_to_step(self, action: List[str], index: int) -> Optional[Dict]:
        """将操作转换为场景计划步骤"""
        action_str = ' '.join(action).lower() if isinstance(action, list) else str(action).lower()

        # 根据操作类型生成步骤
        if '打开' in action_str or 'launch' in action_str or '打开应用' in action_str:
            app_match = re.search(r'打开[的]?(\S+)', action_str)
            app_name = app_match.group(1) if app_match else "应用"
            return {
                "tool": "run",
                "command": f"do.py 打开应用 {app_name}",
                "wait": 2,
                "description": f"打开{app_name}"
            }
        elif '点击' in action_str or 'click' in action_str:
            return {
                "tool": "wait",
                "seconds": 1,
                "description": "等待点击操作"
            }
        elif '截图' in action_str or 'screenshot' in action_str:
            return {
                "tool": "screenshot",
                "description": "截图"
            }
        elif 'vision' in action_str or '分析' in action_str or '描述' in action_str:
            return {
                "tool": "vision",
                "description": "分析屏幕内容"
            }
        elif '输入' in action_str or 'type' in action_str:
            return {
                "tool": "wait",
                "seconds": 1,
                "description": "等待输入"
            }
        else:
            # 默认等待步骤
            return {
                "tool": "wait",
                "seconds": 1,
                "description": f"执行步骤 {index + 1}"
            }

    def _generate_trigger_keyword(self, steps: List[Dict]) -> str:
        """生成触发关键词"""
        keywords = []
        for step in steps[:2]:  # 取前两个步骤的关键词
            desc = step.get('description', '')
            if desc:
                keywords.append(desc)

        if keywords:
            return keywords[0]
        return "自动化场景"

    def discover_and_generate(self) -> Dict:
        """发现模式并生成场景计划"""
        result = {
            'patterns_found': [],
            'scenes_generated': [],
            'recommendations': []
        }

        # 1. 分析行为日志
        behavior_data = self.analyze_behavior_logs()

        # 2. 分析 run_plan 历史
        history_data = self.analyze_run_plan_history()

        # 3. 发现重复模式
        patterns = self.find_repeated_patterns(behavior_data)
        result['patterns_found'] = patterns

        # 4. 为每个模式生成场景计划
        for pattern in patterns:
            plan = self.generate_scene_plan(pattern)
            if plan:
                result['scenes_generated'].append(plan)

        # 5. 生成推荐
        if patterns:
            result['recommendations'] = [
                f"发现 {len(patterns)} 个可自动化的重复模式",
                f"已自动生成 {len(result['scenes_generated'])} 个场景计划",
                "建议：在「设置偏好」中开启自动场景发现功能"
            ]

        return result

    def save_discovered_scenes(self, scenes: List[Dict]) -> List[str]:
        """保存发现的场景到文件"""
        saved_files = []

        for scene in scenes:
            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"auto_discovered_{timestamp}.json"
            filepath = PLANS_DIR / filename

            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(scene, f, ensure_ascii=False, indent=2)
                saved_files.append(str(filepath))
            except Exception as e:
                print(f"保存场景失败: {e}")

        return saved_files

    def get_status(self) -> Dict:
        """获取引擎状态"""
        return {
            'name': '智能自动化模式发现与场景生成引擎',
            'status': 'active',
            'min_pattern_occurrences': self.min_pattern_occurrences,
            'analysis_days': self.analysis_days,
            'last_analysis': datetime.now().isoformat(),
            'preference_engine_available': TaskPreferenceEngine is not None
        }

    # ===== 引擎深度协同功能 (round 143) =====

    def _get_preference_engine(self) -> Optional[TaskPreferenceEngine]:
        """获取任务偏好引擎实例"""
        if TaskPreferenceEngine is None:
            return None
        return TaskPreferenceEngine()

    def learn_preferences_from_patterns(self, patterns: List[Dict]) -> Dict:
        """从发现的模式学习用户偏好

        当模式发现引擎识别到重复模式时，自动提取并学习用户偏好

        Args:
            patterns: 发现的重复模式列表

        Returns:
            学习结果
        """
        result = {
            'preferences_learned': [],
            'preferences_applied': [],
            'errors': []
        }

        pref_engine = self._get_preference_engine()
        if pref_engine is None:
            result['errors'].append('任务偏好引擎不可用')
            return result

        # 从模式中提取偏好
        for pattern in patterns:
            sequence = pattern.get('sequence', [])
            if not sequence:
                continue

            # 分析序列中的操作，提取偏好信息
            task_type = self._extract_task_type(sequence)
            if not task_type:
                continue

            # 检查操作顺序中的首选项
            first_action = sequence[0] if sequence else None
            if first_action:
                # 尝试设置偏好：例如首步操作
                pref_key = 'preferred_first_action'
                pref_value = first_action[0] if isinstance(first_action, (list, tuple)) else str(first_action)

                try:
                    pref_engine.set_preference(
                        task_type=task_type,
                        preference_key=pref_key,
                        preference_value=pref_value,
                        auto_apply=True
                    )
                    result['preferences_learned'].append({
                        'task_type': task_type,
                        'key': pref_key,
                        'value': pref_value
                    })
                except Exception as e:
                    result['errors'].append(f'学习偏好失败: {e}')

        return result

    def _extract_task_type(self, sequence: List) -> Optional[str]:
        """从操作序列中提取任务类型"""
        action_str = ' '.join([str(a) for a in sequence]).lower()

        # 根据操作关键词识别任务类型
        task_keywords = {
            'ihaier': ['ihaier', '办公平台', '消息', '联系人'],
            'browser': ['browser', '浏览器', 'chrome', 'edge', '打开网页'],
            'document': ['document', '文档', 'word', 'excel', 'notepad'],
            'music': ['music', '音乐', '播放', '网易云', '歌曲'],
            'file': ['file', '文件', 'explorer', '文件夹']
        }

        for task_type, keywords in task_keywords.items():
            if any(kw in action_str for kw in keywords):
                return task_type

        # 默认返回 "general"
        return 'general'

    def auto_apply_preferences(self, task_type: str) -> Dict:
        """自动应用偏好到任务执行

        当执行任务时，自动加载并应用相关偏好

        Args:
            task_type: 任务类型

        Returns:
            应用结果
        """
        result = {
            'task_type': task_type,
            'applied_preferences': {},
            'has_preferences': False
        }

        pref_engine = self._get_preference_engine()
        if pref_engine is None:
            result['error'] = '任务偏好引擎不可用'
            return result

        # 获取该任务类型的偏好
        preferences = pref_engine.get_preferences(task_type)
        if preferences:
            result['has_preferences'] = True
            result['applied_preferences'] = preferences

        return result

    def track_collaboration_effect(self, task_type: str, execution_result: Dict) -> Dict:
        """追踪引擎协同效果

        记录模式发现与偏好学习的协同效果，供后续优化参考

        Args:
            task_type: 任务类型
            execution_result: 执行结果

        Returns:
            追踪结果
        """
        result = {
            'task_type': task_type,
            'tracked': True,
            'timestamp': datetime.now().isoformat()
        }

        # 记录协同效果到文件
        collaboration_file = STATE_DIR / "engine_collaboration_tracking.json"
        try:
            # 读取现有数据
            tracking_data = {'collaborations': []}
            if collaboration_file.exists():
                with open(collaboration_file, 'r', encoding='utf-8') as f:
                    tracking_data = json.load(f)

            # 添加新记录
            tracking_data['collaborations'].append({
                'task_type': task_type,
                'execution_result': execution_result,
                'timestamp': result['timestamp']
            })

            # 只保留最近 50 条记录
            tracking_data['collaborations'] = tracking_data['collaborations'][-50:]

            # 保存
            with open(collaboration_file, 'w', encoding='utf-8') as f:
                json.dump(tracking_data, f, ensure_ascii=False, indent=2)

            result['saved'] = True
        except Exception as e:
            result['error'] = f'保存协同效果失败: {e}'

        return result

    def engine_collaboration_report(self) -> Dict:
        """获取引擎协同报告

        返回模式发现引擎与偏好引擎的协同状态

        Returns:
            协同报告
        """
        report = {
            'pattern_discovery_engine': {
                'name': '智能自动化模式发现引擎',
                'status': 'active',
                'min_pattern_occurrences': self.min_pattern_occurrences
            },
            'preference_engine': {
                'name': '任务偏好引擎',
                'available': TaskPreferenceEngine is not None
            },
            'collaboration_status': 'active' if TaskPreferenceEngine else 'unavailable',
            'integration_features': [
                '从模式自动学习偏好',
                '偏好自动应用到任务执行',
                '协同效果追踪'
            ]
        }

        # 添加协同效果统计
        collaboration_file = STATE_DIR / "engine_collaboration_tracking.json"
        if collaboration_file.exists():
            try:
                with open(collaboration_file, 'r', encoding='utf-8') as f:
                    tracking_data = json.load(f)
                    report['total_collaborations'] = len(tracking_data.get('collaborations', []))
            except Exception:
                pass

        return report


def handle_command(args: List[str]) -> str:
    """处理命令"""
    engine = AutomationPatternDiscovery()

    if not args:
        # 显示引擎状态
        status = engine.get_status()
        return json.dumps(status, ensure_ascii=False, indent=2)

    command = args[0]

    if command in ['status', '状态']:
        status = engine.get_status()
        return json.dumps(status, ensure_ascii=False, indent=2)

    elif command in ['discover', '发现', '模式发现']:
        result = engine.discover_and_generate()

        # 如果有生成的场景，保存它们
        if result['scenes_generated']:
            saved = engine.save_discovered_scenes(result['scenes_generated'])
            result['saved_files'] = saved

        return json.dumps(result, ensure_ascii=False, indent=2)

    elif command in ['analyze', '分析']:
        behavior_data = engine.analyze_behavior_logs()
        patterns = engine.find_repeated_patterns(behavior_data)

        return json.dumps({
            'patterns_found': len(patterns),
            'patterns': patterns[:5]
        }, ensure_ascii=False, indent=2)

    elif command in ['generate', '生成']:
        behavior_data = engine.analyze_behavior_logs()
        patterns = engine.find_repeated_patterns(behavior_data)

        scenes = []
        for pattern in patterns[:3]:
            plan = engine.generate_scene_plan(pattern)
            if plan:
                scenes.append(plan)

        # 保存场景
        saved = engine.save_discovered_scenes(scenes)

        return json.dumps({
            'scenes_generated': len(scenes),
            'saved_files': saved,
            'scenes': scenes
        }, ensure_ascii=False, indent=2)

    # ===== 引擎协同命令 (round 143) =====

    elif command in ['learn', '学习', '偏好学习', 'learn-preferences']:
        # 从发现的模式学习偏好
        behavior_data = engine.analyze_behavior_logs()
        patterns = engine.find_repeated_patterns(behavior_data)
        result = engine.learn_preferences_from_patterns(patterns)
        return json.dumps(result, ensure_ascii=False, indent=2)

    elif command in ['apply', '应用', '应用偏好', 'apply-preferences']:
        # 自动应用偏好到任务
        task_type = args[1] if len(args) > 1 else 'general'
        result = engine.auto_apply_preferences(task_type)
        return json.dumps(result, ensure_ascii=False, indent=2)

    elif command in ['collaboration', '协同', '引擎协同', 'engine-collab']:
        # 获取引擎协同报告
        result = engine.engine_collaboration_report()
        return json.dumps(result, ensure_ascii=False, indent=2)

    elif command in ['track', '追踪', 'track-effect']:
        # 追踪协同效果
        task_type = args[1] if len(args) > 1 else 'general'
        execution_result = {'status': 'success', 'task_type': task_type}
        result = engine.track_collaboration_effect(task_type, execution_result)
        return json.dumps(result, ensure_ascii=False, indent=2)

    else:
        return json.dumps({
            'error': f'未知命令: {command}',
            'available_commands': [
                'status', 'discover', 'analyze', 'generate',
                'learn', 'apply', 'collaboration', 'track'
            ]
        }, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    import sys

    args = sys.argv[1:] if len(sys.argv) > 1 else []
    result = handle_command(args)
    print(result)