#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能学习与适应引擎
让系统从用户交互历史中学习行为模式，自动调整推荐和响应策略
实现真正的个性化智能助手
"""
import os
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict
from collections import defaultdict, Counter


# 数据存储路径
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runtime', 'state')
INTERACTION_LOG_FILE = os.path.join(DATA_DIR, 'user_interaction_log.json')
LEARNING_DATA_FILE = os.path.join(DATA_DIR, 'adaptive_learning_data.json')
USER_PREFERENCES_FILE = os.path.join(DATA_DIR, 'user_preferences.json')


@dataclass
class InteractionRecord:
    """交互记录"""
    timestamp: str
    user_input: str
    intent: str
    command: str
    success: bool
    response_time: float = 0.0
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserHabit:
    """用户习惯"""
    time_period_preferences: Dict[str, int] = field(default_factory=dict)  # 上午/下午/晚上/深夜
    intent_frequency: Dict[str, int] = field(default_factory=dict)
    command_frequency: Dict[str, int] = field(default_factory=dict)
    preferred_applications: List[str] = field(default_factory=list)
    success_rate: float = 0.0
    avg_response_time: float = 0.0
    last_updated: str = ""


@dataclass
class AdaptationSuggestion:
    """适应建议"""
    suggestion_type: str  # recommendation/optimization/prediction
    title: str
    description: str
    confidence: float  # 0-1
    related_intents: List[str] = field(default_factory=list)
    action: str = ""


class InteractionLogger:
    """交互记录器"""

    def __init__(self):
        self.log_file = INTERACTION_LOG_FILE
        self._ensure_data_dir()
        self._load_or_init_log()

    def _ensure_data_dir(self):
        """确保数据目录存在"""
        os.makedirs(DATA_DIR, exist_ok=True)

    def _load_or_init_log(self):
        """加载或初始化日志"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    self.log = json.load(f)
            except:
                self.log = {'interactions': [], 'metadata': {}}
        else:
            self.log = {'interactions': [], 'metadata': {}}

    def log_interaction(self, user_input: str, intent: str, command: str,
                        success: bool, response_time: float = 0.0,
                        context: Dict[str, Any] = None):
        """记录一次交互"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'intent': intent,
            'command': command,
            'success': success,
            'response_time': response_time,
            'context': context or {}
        }
        self.log['interactions'].append(record)

        # 保留最近1000条记录
        if len(self.log['interactions']) > 1000:
            self.log['interactions'] = self.log['interactions'][-1000:]

        self._save_log()

    def _save_log(self):
        """保存日志"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self.log, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存交互日志失败: {e}")

    def get_recent_interactions(self, count: int = 100) -> List[Dict]:
        """获取最近的交互记录"""
        return self.log['interactions'][-count:]

    def get_interactions_by_time_range(self, start_time: datetime,
                                       end_time: datetime) -> List[Dict]:
        """获取时间范围内的交互记录"""
        result = []
        for record in self.log['interactions']:
            try:
                record_time = datetime.fromisoformat(record['timestamp'])
                if start_time <= record_time <= end_time:
                    result.append(record)
            except:
                continue
        return result


class HabitAnalyzer:
    """习惯分析器"""

    def __init__(self):
        self.logger = InteractionLogger()
        self.learning_file = LEARNING_DATA_FILE
        self._load_or_init_learning_data()

    def _load_or_init_learning_data(self):
        """加载或初始化学习数据"""
        if os.path.exists(self.learning_file):
            try:
                with open(self.learning_file, 'r', encoding='utf-8') as f:
                    self.learning_data = json.load(f)
            except:
                self.learning_data = {'habits': {}, 'patterns': [], 'last_analyzed': None}
        else:
            self.learning_data = {'habits': {}, 'patterns': [], 'last_analyzed': None}

    def _save_learning_data(self):
        """保存学习数据"""
        try:
            with open(self.learning_file, 'w', encoding='utf-8') as f:
                json.dump(self.learning_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存学习数据失败: {e}")

    def analyze_habits(self, days: int = 7) -> UserHabit:
        """分析用户习惯"""
        # 获取指定天数内的交互记录
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)

        interactions = self.logger.get_interactions_by_time_range(start_time, end_time)

        if not interactions:
            return UserHabit()

        habit = UserHabit()

        # 分析时间段偏好
        time_periods = {'morning': 0, 'afternoon': 0, 'evening': 0, 'night': 0}
        for record in interactions:
            try:
                record_time = datetime.fromisoformat(record['timestamp'])
                hour = record_time.hour
                if 6 <= hour < 12:
                    time_periods['morning'] += 1
                elif 12 <= hour < 18:
                    time_periods['afternoon'] += 1
                elif 18 <= hour < 22:
                    time_periods['evening'] += 1
                else:
                    time_periods['night'] += 1
            except:
                continue

        habit.time_period_preferences = time_periods

        # 分析意图频率
        intents = [r.get('intent', 'unknown') for r in interactions]
        habit.intent_frequency = dict(Counter(intents))

        # 分析命令频率
        commands = [r.get('command', 'unknown') for r in interactions if r.get('command')]
        habit.command_frequency = dict(Counter(commands))

        # 计算成功率
        successful = sum(1 for r in interactions if r.get('success', False))
        habit.success_rate = successful / len(interactions) if interactions else 0.0

        # 计算平均响应时间
        response_times = [r.get('response_time', 0) for r in interactions if r.get('response_time', 0) > 0]
        habit.avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0

        habit.last_updated = datetime.now().isoformat()

        # 保存分析结果
        self.learning_data['habits'] = asdict(habit)
        self.learning_data['last_analyzed'] = datetime.now().isoformat()
        self._save_learning_data()

        return habit

    def get_habit_summary(self) -> Dict[str, Any]:
        """获取习惯摘要"""
        if not self.learning_data.get('habits'):
            return {'status': 'no_data', 'message': '暂无足够数据进行分析'}

        habit = self.learning_data['habits']

        # 找出最活跃的时间段
        time_prefs = habit.get('time_period_preferences', {})
        most_active_period = max(time_prefs.items(), key=lambda x: x[1])[0] if time_prefs else 'unknown'

        # 找出最常用的意图
        intent_freq = habit.get('intent_frequency', {})
        top_intents = sorted(intent_freq.items(), key=lambda x: x[1], reverse=True)[:5]

        # 找出最常用的命令
        cmd_freq = habit.get('command_frequency', {})
        top_commands = sorted(cmd_freq.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            'most_active_period': most_active_period,
            'top_intents': [{'intent': i, 'count': c} for i, c in top_intents],
            'top_commands': [{'command': c, 'count': cnt} for c, cnt in top_commands],
            'success_rate': habit.get('success_rate', 0),
            'avg_response_time': habit.get('avg_response_time', 0),
            'last_updated': habit.get('last_updated', 'unknown')
        }


class AdaptationEngine:
    """适应引擎"""

    def __init__(self):
        self.logger = InteractionLogger()
        self.analyzer = HabitAnalyzer()
        self.preferences_file = USER_PREFERENCES_FILE
        self._load_or_init_preferences()

    def _load_or_init_preferences(self):
        """加载或初始化用户偏好"""
        if os.path.exists(self.preferences_file):
            try:
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    self.preferences = json.load(f)
            except:
                self.preferences = {'adaptations': [], 'custom_rules': {}}
        else:
            self.preferences = {'adaptations': [], 'custom_rules': {}}

    def _save_preferences(self):
        """保存用户偏好"""
        try:
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存用户偏好失败: {e}")

    def generate_adaptations(self) -> List[AdaptationSuggestion]:
        """生成适应建议"""
        suggestions = []

        # 分析习惯
        habit = self.analyzer.analyze_habits()

        if not habit.last_updated:
            return [AdaptationSuggestion(
                suggestion_type='info',
                title='数据收集中',
                description='系统正在收集您的交互数据，请继续使用以帮助学习。',
                confidence=1.0
            )]

        # 基于时间段的建议
        time_prefs = habit.time_period_preferences
        if time_prefs:
            most_active = max(time_prefs.items(), key=lambda x: x[1])[0]
            if most_active == 'morning':
                suggestions.append(AdaptationSuggestion(
                    suggestion_type='prediction',
                    title='早晨工作模式',
                    description='您倾向于在早晨使用系统，建议提前准备常用场景。',
                    confidence=0.8,
                    related_intents=list(habit.intent_frequency.keys())
                ))
            elif most_active == 'evening':
                suggestions.append(AdaptationSuggestion(
                    suggestion_type='prediction',
                    title='晚间工作模式',
                    description='您在晚间更活跃，可能需要处理文档或娱乐需求。',
                    confidence=0.8,
                    related_intents=list(habit.intent_frequency.keys())
                ))

        # 基于成功率的建议
        if habit.success_rate < 0.7:
            suggestions.append(AdaptationSuggestion(
                suggestion_type='optimization',
                title='提升成功率',
                description=f'当前任务成功率为 {habit.success_rate*100:.1f}%，建议简化任务步骤或提供更多上下文。',
                confidence=0.9,
                related_intents=list(habit.intent_frequency.keys())
            ))

        # 基于响应时间的建议
        if habit.avg_response_time > 5.0:
            suggestions.append(AdaptationSuggestion(
                suggestion_type='optimization',
                title='优化响应速度',
                description=f'平均响应时间为 {habit.avg_response_time:.1f}秒，可考虑优化执行路径。',
                confidence=0.7,
                related_intents=[]
            ))

        # 基于高频意图的推荐
        if habit.intent_frequency:
            top_intent = max(habit.intent_frequency.items(), key=lambda x: x[1])[0]
            suggestions.append(AdaptationSuggestion(
                suggestion_type='recommendation',
                title=f'常用功能: {top_intent}',
                description=f'您最常使用 {top_intent} 功能，已优化相关响应。',
                confidence=0.85,
                related_intents=[top_intent]
            ))

        # 保存适应建议
        self.preferences['adaptions'] = [asdict(s) for s in suggestions]
        self._save_preferences()

        return suggestions


class AdaptiveLearningEngine:
    """智能学习与适应引擎主类"""

    def __init__(self):
        self.logger = InteractionLogger()
        self.analyzer = HabitAnalyzer()
        self.adaptation = AdaptationEngine()

    def process(self, user_input: str, intent: str = None, command: str = None,
                success: bool = True, response_time: float = 0.0,
                context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理学习与适应

        Args:
            user_input: 用户输入
            intent: 识别的意图
            command: 执行的命令
            success: 是否成功
            response_time: 响应时间(秒)
            context: 额外上下文

        Returns:
            处理结果
        """
        # 记录交互
        self.logger.log_interaction(
            user_input=user_input,
            intent=intent or 'unknown',
            command=command or '',
            success=success,
            response_time=response_time,
            context=context or {}
        )

        # 生成适应建议
        suggestions = self.adaptation.generate_adaptations()

        return {
            'success': True,
            'logged': True,
            'suggestions_count': len(suggestions),
            'message': '交互已记录并分析'
        }

    def analyze_habits(self, days: int = 7) -> Dict[str, Any]:
        """分析用户习惯

        Args:
            days: 分析天数

        Returns:
            习惯分析结果
        """
        habit = self.analyzer.analyze_habits(days)
        return asdict(habit)

    def get_habit_summary(self) -> Dict[str, Any]:
        """获取习惯摘要"""
        return self.analyzer.get_habit_summary()

    def get_adaptations(self) -> List[Dict[str, Any]]:
        """获取适应建议"""
        suggestions = self.adaptation.generate_adaptations()
        return [asdict(s) for s in suggestions]

    def get_status(self) -> Dict[str, Any]:
        """获取学习引擎状态"""
        summary = self.analyzer.get_habit_summary()
        recent_count = len(self.logger.get_recent_interactions(10))

        return {
            'status': 'active',
            'total_interactions': len(self.logger.log.get('interactions', [])),
            'recent_interactions': recent_count,
            'last_analyzed': self.analyzer.learning_data.get('last_analyzed'),
            'summary': summary
        }


# CLI 接口
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='智能学习与适应引擎')
    parser.add_argument('command', nargs='?', help='命令: analyze/summary/adaptations/status/process')
    parser.add_argument('--input', '-i', help='用户输入')
    parser.add_argument('--intent', help='意图')
    parser.add_argument('--command', '-c', help='执行的命令')
    parser.add_argument('--success', action='store_true', default=True, help='是否成功')
    parser.add_argument('--time', '-t', type=float, default=0.0, help='响应时间(秒)')
    parser.add_argument('--days', '-d', type=int, default=7, help='分析天数')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')

    args = parser.parse_args()

    engine = AdaptiveLearningEngine()

    if args.command == 'analyze':
        result = engine.analyze_habits(args.days)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"习惯分析 (最近 {args.days} 天):")
            print(f"  时间段偏好: {result.get('time_period_preferences', {})}")
            print(f"  意图频率: {result.get('intent_frequency', {})}")
            print(f"  命令频率: {result.get('command_frequency', {})}")
            print(f"  成功率: {result.get('success_rate', 0)*100:.1f}%")
            print(f"  平均响应时间: {result.get('avg_response_time', 0):.2f}秒")

    elif args.command == 'summary':
        result = engine.get_habit_summary()
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            if result.get('status') == 'no_data':
                print(result.get('message', '暂无数据'))
            else:
                print("习惯摘要:")
                print(f"  最活跃时间段: {result.get('most_active_period')}")
                print(f"  常用意图: {result.get('top_intents')}")
                print(f"  常用命令: {result.get('top_commands')}")
                print(f"  成功率: {result.get('success_rate', 0)*100:.1f}%")

    elif args.command == 'adaptations' or args.command == 'suggestions':
        result = engine.get_adaptations()
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("适应建议:")
            for i, s in enumerate(result, 1):
                print(f"  {i}. [{s['suggestion_type']}] {s['title']}")
                print(f"     {s['description']}")

    elif args.command == 'status':
        result = engine.get_status()
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("学习引擎状态:")
            print(f"  状态: {result['status']}")
            print(f"  总交互数: {result['total_interactions']}")
            print(f"  最近10条: {result['recent_interactions']}")
            print(f"  最后分析: {result['last_analyzed']}")

    elif args.command == 'process':
        if args.input:
            result = engine.process(
                user_input=args.input,
                intent=args.intent,
                command=args.command,
                success=args.success,
                response_time=args.time
            )
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(f"状态: {result['message']}")
                print(f"建议数: {result['suggestions_count']}")
        else:
            print("请提供 --input 参数")

    else:
        # 默认显示状态
        result = engine.get_status()
        print("智能学习与适应引擎")
        print(f"  状态: {result['status']}")
        print(f"  总交互数: {result['total_interactions']}")
        print("\n用法:")
        print("  python adaptive_learning_engine.py status")
        print("  python adaptive_learning_engine.py analyze --days 7")
        print("  python adaptive_learning_engine.py summary")
        print("  python adaptive_learning_engine.py adaptations")
        print("  python adaptive_learning_engine.py process --input '打开浏览器' --intent 'open_app'")