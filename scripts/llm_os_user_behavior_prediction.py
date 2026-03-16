#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-OS 用户行为智能预测与主动服务增强引擎

本模块实现用户使用行为的智能分析和预测，基于700+轮进化历史的模式识别能力，
构建主动服务触发机制，让系统能够预测用户意图并主动提供服务。

版本: 1.0.0
功能:
1. 用户行为模式分析 - 分析用户使用应用、时间、场景等模式
2. 意图预测 - 基于历史行为预测用户可能的意图
3. 主动服务触发 - 根据预测主动提供服务
4. 个性化推荐 - 基于用户习惯推荐可能需要的功能/应用/场景

依赖: llm_os_app_manager, llm_os_app_launcher, behavior_learner 等
"""

import os
import sys
import json
import sqlite3
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict
import random

# 脚本目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(SCRIPT_DIR, "..", "runtime", "state")
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "runtime", "data")


def get_db_path():
    """获取行为数据库路径"""
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, "user_behavior.db")


def init_db():
    """初始化行为数据库"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # 用户行为记录表
    c.execute('''CREATE TABLE IF NOT EXISTS user_behavior (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        action_type TEXT NOT NULL,
        target TEXT,
        details TEXT,
        context TEXT
    )''')

    # 应用使用记录表
    c.execute('''CREATE TABLE IF NOT EXISTS app_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        app_name TEXT NOT NULL,
        duration_seconds INTEGER,
        category TEXT
    )''')

    # 时间模式表
    c.execute('''CREATE TABLE IF NOT EXISTS time_patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        day_of_week INTEGER,
        hour INTEGER,
        top_actions TEXT,
        top_apps TEXT,
        sample_count INTEGER
    )''')

    # 意图预测缓存表
    c.execute('''CREATE TABLE IF NOT EXISTS intent_predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        context TEXT NOT NULL,
        predicted_intent TEXT,
        confidence REAL,
        triggered_action TEXT
    )''')

    conn.commit()
    conn.close()
    return db_path


def record_behavior(action_type, target=None, details=None, context=None):
    """记录用户行为"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    timestamp = datetime.now().isoformat()
    c.execute(
        "INSERT INTO user_behavior (timestamp, action_type, target, details, context) VALUES (?, ?, ?, ?, ?)",
        (timestamp, action_type, target, json.dumps(details) if details else None,
         json.dumps(context) if context else None)
    )

    conn.commit()
    conn.close()
    return True


def record_app_usage(app_name, duration_seconds=0, category=None):
    """记录应用使用"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    timestamp = datetime.now().isoformat()
    c.execute(
        "INSERT INTO app_usage (timestamp, app_name, duration_seconds, category) VALUES (?, ?, ?, ?)",
        (timestamp, app_name, duration_seconds, category)
    )

    conn.commit()
    conn.close()
    return True


def analyze_time_patterns():
    """分析时间模式"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # 获取过去7天的数据
    seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()

    patterns = {}

    # 按星期几和小时分析
    c.execute('''SELECT
        strftime('%w', timestamp) as dow,
        strftime('%H', timestamp) as hour,
        action_type,
        COUNT(*) as count
    FROM user_behavior
    WHERE timestamp > ?
    GROUP BY dow, hour, action_type
    ORDER BY count DESC''', (seven_days_ago,))

    for row in c.fetchall():
        dow, hour, action, count = row
        key = (dow, hour)
        if key not in patterns:
            patterns[key] = {'actions': Counter(), 'apps': Counter()}
        patterns[key]['actions'][action] = count

    # 分析应用使用时间模式
    c.execute('''SELECT
        strftime('%w', timestamp) as dow,
        strftime('%H', timestamp) as hour,
        app_name,
        COUNT(*) as count
    FROM app_usage
    WHERE timestamp > ?
    GROUP BY dow, hour, app_name
    ORDER BY count DESC''', (seven_days_ago,))

    for row in c.fetchall():
        dow, hour, app, count = row
        key = (dow, hour)
        if key in patterns:
            patterns[key]['apps'][app] = count

    conn.close()
    return patterns


def get_current_context():
    """获取当前上下文（时间、系统状态等）"""
    now = datetime.now()
    return {
        'day_of_week': now.weekday(),
        'hour': now.hour,
        'is_weekend': now.weekday() >= 5,
        'time_of_day': _get_time_period(now.hour),
        'date': now.strftime('%Y-%m-%d')
    }


def _get_time_period(hour):
    """获取时间段"""
    if 6 <= hour < 9:
        return 'morning_early'
    elif 9 <= hour < 12:
        return 'morning'
    elif 12 <= hour < 14:
        return 'noon'
    elif 14 <= hour < 18:
        return 'afternoon'
    elif 18 <= hour < 22:
        return 'evening'
    else:
        return 'night'


def predict_intent(context=None):
    """预测用户意图"""
    if context is None:
        context = get_current_context()

    patterns = analyze_time_patterns()

    # 基于时间模式的预测
    key = (str(context['day_of_week']), str(context['hour']))

    predictions = []

    if key in patterns:
        pattern = patterns[key]

        # 预测可能的行为
        if pattern['actions']:
            top_actions = pattern['actions'].most_common(3)
            for action, count in top_actions:
                if count >= 2:  # 至少出现2次
                    predictions.append({
                        'intent': action,
                        'confidence': min(count / 10.0, 0.9),
                        'reason': f'基于历史模式（{count}次）'
                    })

        # 预测可能使用的应用
        if pattern['apps']:
            top_apps = pattern['apps'].most_common(3)
            for app, count in top_apps:
                if count >= 2:
                    predictions.append({
                        'intent': f'use_app:{app}',
                        'confidence': min(count / 10.0, 0.85),
                        'reason': f'常用应用（{count}次）'
                    })

    # 基于时间段的默认预测
    time_predictions = _get_time_based_predictions(context)
    predictions.extend(time_predictions)

    # 按置信度排序
    predictions.sort(key=lambda x: x['confidence'], reverse=True)

    # 保存预测结果
    if predictions:
        _save_prediction(context, predictions[0])

    return predictions[:5]  # 返回前5个预测


def _get_time_based_predictions(context):
    """基于时间段的预测"""
    predictions = []

    # 工作日早上
    if not context['is_weekend'] and context['hour'] in [9, 10]:
        predictions.append({
            'intent': 'work_start',
            'confidence': 0.7,
            'reason': '工作日开始时间'
        })

    # 午餐时间
    if context['hour'] in [12, 13]:
        predictions.append({
            'intent': 'lunch_break',
            'confidence': 0.8,
            'reason': '午餐时间'
        })

    # 下午工作时间
    if not context['is_weekend'] and context['hour'] in [14, 15, 16]:
        predictions.append({
            'intent': 'work_afternoon',
            'confidence': 0.6,
            'reason': '下午工作时间'
        })

    # 傍晚
    if context['hour'] in [18, 19]:
        predictions.append({
            'intent': 'work_end',
            'confidence': 0.7,
            'reason': '下班时间'
        })

    return predictions


def _save_prediction(context, prediction):
    """保存预测结果"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    timestamp = datetime.now().isoformat()
    c.execute(
        "INSERT INTO intent_predictions (timestamp, context, predicted_intent, confidence) VALUES (?, ?, ?, ?)",
        (timestamp, json.dumps(context), prediction['intent'], prediction['confidence'])
    )

    conn.commit()
    conn.close()


def get_proactive_suggestions(context=None):
    """获取主动建议（基于预测的服务）"""
    predictions = predict_intent(context)
    suggestions = []

    for pred in predictions:
        intent = pred['intent']
        confidence = pred['confidence']

        if confidence < 0.3:
            continue

        # 基于预测意图生成建议
        if intent == 'work_start':
            suggestions.append({
                'type': 'action',
                'title': '开始工作',
                'description': '检测到工作日开始，是否打开常用工作应用？',
                'action': 'launch_work_apps',
                'confidence': confidence
            })
        elif intent == 'lunch_break':
            suggestions.append({
                'type': 'reminder',
                'title': '午餐时间',
                'description': '现在是午餐时间，建议休息一下',
                'action': 'none',
                'confidence': confidence
            })
        elif intent.startswith('use_app:'):
            app = intent.split(':')[1]
            suggestions.append({
                'type': 'app',
                'title': f'常用应用: {app}',
                'description': f'根据您的使用习惯，您可能需要打开 {app}',
                'action': f'launch:{app}',
                'confidence': confidence
            })
        elif intent == 'work_afternoon':
            suggestions.append({
                'type': 'action',
                'title': '下午工作提醒',
                'description': '下午工作时间，建议保持专注',
                'action': 'focus_mode',
                'confidence': confidence
            })

    # 添加一些通用建议
    suggestions.extend(_get_general_suggestions(context))

    return suggestions[:5]


def _get_general_suggestions(context):
    """获取通用建议"""
    suggestions = []

    # 检查系统资源
    try:
        import psutil
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()

        if memory.percent > 85:
            suggestions.append({
                'type': 'system',
                'title': '内存使用率高',
                'description': f'内存使用率 {memory.percent}%，建议关闭一些应用',
                'action': 'memory_cleanup',
                'confidence': 0.9
            })

        if cpu_percent > 90:
            suggestions.append({
                'type': 'system',
                'title': 'CPU使用率高',
                'description': f'CPU使用率 {cpu_percent}%，可能有程序占用资源',
                'action': 'cpu_check',
                'confidence': 0.9
            })
    except ImportError:
        pass

    return suggestions


def analyze_user_preferences():
    """分析用户偏好"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    preferences = {
        'favorite_apps': [],
        'active_hours': [],
        'frequent_actions': [],
        'productivity_score': 0.0
    }

    # 获取最常用的应用
    c.execute('''SELECT app_name, COUNT(*) as count
    FROM app_usage
    GROUP BY app_name
    ORDER BY count DESC
    LIMIT 10''')

    preferences['favorite_apps'] = [row[0] for row in c.fetchall()]

    # 获取最常用的行为
    c.execute('''SELECT action_type, COUNT(*) as count
    FROM user_behavior
    GROUP BY action_type
    ORDER BY count DESC
    LIMIT 10''')

    preferences['frequent_actions'] = [row[0] for row in c.fetchall()]

    # 获取活跃时间段
    c.execute('''SELECT DISTINCT strftime('%H', timestamp) as hour
    FROM user_behavior
    ORDER BY hour''')

    preferences['active_hours'] = [row[0] for row in c.fetchall()]

    # 计算生产力分数（基于行为多样性）
    c.execute('SELECT COUNT(DISTINCT action_type) FROM user_behavior')
    action_diversity = c.fetchone()[0]

    c.execute('SELECT COUNT(*) FROM user_behavior')
    total_actions = c.fetchone()[0]

    if total_actions > 0:
        preferences['productivity_score'] = min(action_diversity / 20.0, 1.0)

    conn.close()
    return preferences


def get_behavior_summary(days=7):
    """获取行为摘要"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    since = (datetime.now() - timedelta(days=days)).isoformat()

    summary = {
        'period_days': days,
        'total_actions': 0,
        'top_actions': [],
        'top_apps': [],
        'daily_average': 0.0
    }

    c.execute('SELECT COUNT(*) FROM user_behavior WHERE timestamp > ?', (since,))
    summary['total_actions'] = c.fetchone()[0]

    c.execute('''SELECT action_type, COUNT(*) as count
    FROM user_behavior
    WHERE timestamp > ?
    GROUP BY action_type
    ORDER BY count DESC
    LIMIT 5''', (since,))

    summary['top_actions'] = [{'action': row[0], 'count': row[1]} for row in c.fetchall()]

    c.execute('''SELECT app_name, COUNT(*) as count
    FROM app_usage
    WHERE timestamp > ?
    GROUP BY app_name
    ORDER BY count DESC
    LIMIT 5''', (since,))

    summary['top_apps'] = [{'app': row[0], 'count': row[1]} for row in c.fetchall()]

    if days > 0:
        summary['daily_average'] = summary['total_actions'] / days

    conn.close()
    return summary


def trigger_proactive_service(action):
    """触发主动服务"""
    result = {'success': False, 'message': ''}

    if action == 'launch_work_apps':
        # 启动常用工作应用
        try:
            import subprocess
            # 尝试打开常见的办公应用
            apps = ['notepad', 'explorer', 'chrome']
            for app in apps[:2]:
                subprocess.Popen(f'start {app}', shell=True)
            result['success'] = True
            result['message'] = '已启动常用工作应用'
        except Exception as e:
            result['message'] = f'启动失败: {str(e)}'

    elif action == 'focus_mode':
        # 进入专注模式
        try:
            notification_tool = os.path.join(SCRIPT_DIR, "notification_tool.py")
            subprocess.run([sys.executable, notification_tool, "show", "专注模式", "已开启专注模式，请保持专注！"])
            result['success'] = True
            result['message'] = '已开启专注模式'
        except Exception as e:
            result['message'] = f'操作失败: {str(e)}'

    elif action == 'memory_cleanup':
        # 内存清理建议
        result['message'] = '建议手动关闭不常用的应用程序以释放内存'

    elif action.startswith('launch:'):
        app = action.split(':')[1]
        try:
            keyboard_tool = os.path.join(SCRIPT_DIR, "keyboard_tool.py")
            subprocess.run([sys.executable, keyboard_tool, "keys", "91", "82"])  # Win+R
            import time
            time.sleep(0.5)
            subprocess.run([sys.executable, keyboard_tool, "type", app])
            time.sleep(0.5)
            subprocess.run([sys.executable, keyboard_tool, "key", "13"])  # Enter
            result['success'] = True
            result['message'] = f'正在启动 {app}'
        except Exception as e:
            result['message'] = f'启动失败: {str(e)}'

    else:
        result['message'] = f'未知操作: {action}'

    # 记录触发的服务
    if result['success']:
        record_behavior('proactive_service', target=action, context={'result': result['message']})

    return result


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description='LLM-OS 用户行为智能预测与主动服务增强引擎',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--init-db", "-init", action="store_true",
                        help="初始化行为数据库")

    parser.add_argument("--record-behavior", "-rb", nargs=2, metavar=('TYPE', 'TARGET'),
                        help="记录用户行为 (action_type target)")

    parser.add_argument("--record-app", "-ra", nargs=1, metavar=('APP_NAME'),
                        help="记录应用使用")

    parser.add_argument("--analyze-patterns", "-ap", action="store_true",
                        help="分析时间模式")

    parser.add_argument("--predict", "-p", action="store_true",
                        help="预测用户意图")

    parser.add_argument("--suggestions", "-s", action="store_true",
                        help="获取主动建议")

    parser.add_argument("--preferences", "-pf", action="store_true",
                        help="分析用户偏好")

    parser.add_argument("--summary", "-sum", nargs='?', const=7, type=int, metavar="DAYS",
                        help="获取行为摘要（默认7天）")

    parser.add_argument("--trigger", "-t", type=str,
                        help="触发主动服务")

    parser.add_argument("--context", "-c", action="store_true",
                        help="获取当前上下文")

    args = parser.parse_args()

    # 初始化数据库
    if args.init_db:
        db_path = init_db()
        print(f"数据库已初始化: {db_path}")
        return

    # 确保数据库存在
    if not os.path.exists(get_db_path()):
        init_db()

    # 记录行为
    if args.record_behavior:
        action_type, target = args.record_behavior
        record_behavior(action_type, target=target)
        print(f"已记录行为: {action_type} -> {target}")
        return

    # 记录应用使用
    if args.record_app:
        app_name = args.record_app[0]
        record_app_usage(app_name)
        print(f"已记录应用使用: {app_name}")
        return

    # 获取当前上下文
    if args.context:
        context = get_current_context()
        print(json.dumps(context, ensure_ascii=False, indent=2))
        return

    # 分析时间模式
    if args.analyze_patterns:
        patterns = analyze_time_patterns()
        print(json.dumps(patterns, ensure_ascii=False, indent=2))
        return

    # 预测用户意图
    if args.predict:
        context = get_current_context()
        predictions = predict_intent(context)
        print(json.dumps(predictions, ensure_ascii=False, indent=2))
        return

    # 获取主动建议
    if args.suggestions:
        context = get_current_context()
        suggestions = get_proactive_suggestions(context)
        print(json.dumps(suggestions, ensure_ascii=False, indent=2))
        return

    # 分析用户偏好
    if args.preferences:
        prefs = analyze_user_preferences()
        print(json.dumps(prefs, ensure_ascii=False, indent=2))
        return

    # 获取行为摘要
    if args.summary is not None:
        summary = get_behavior_summary(args.summary)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return

    # 触发主动服务
    if args.trigger:
        result = trigger_proactive_service(args.trigger)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 默认显示帮助
    parser.print_help()


if __name__ == "__main__":
    main()