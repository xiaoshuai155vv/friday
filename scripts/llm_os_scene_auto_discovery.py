#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-OS 智能场景自动发现与执行引擎

本模块实现用户行为的智能分析，自动发现重复操作模式，
并生成可自动执行的场景计划。与用户行为预测引擎深度集成，
实现「行为分析→模式发现→场景生成→自动执行」的完整闭环。

版本: 1.0.0
功能:
1. 用户行为模式分析 - 分析连续行为序列，识别重复模式
2. 自动化场景发现 - 识别高频重复操作，生成场景计划
3. 场景执行 - 自动执行生成的场景计划
4. 与用户行为预测深度集成 - 利用预测结果优化场景发现

依赖: llm_os_user_behavior_prediction, llm_os_control_panel, run_plan
"""

import os
import sys
import json
import sqlite3
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict
import argparse


# 脚本目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(SCRIPT_DIR, "..", "runtime", "state")
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "runtime", "data")
PLANS_DIR = os.path.join(SCRIPT_DIR, "..", "assets", "plans")


def get_db_path():
    """获取场景自动发现数据库路径"""
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, "scene_auto_discovery.db")


def init_db():
    """初始化场景自动发现数据库"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # 行为序列记录表
    c.execute('''CREATE TABLE IF NOT EXISTS behavior_sequences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        sequence_data TEXT NOT NULL,
        action_count INTEGER,
        time_span_seconds INTEGER
    )''')

    # 发现的可自动化模式表
    c.execute('''CREATE TABLE IF NOT EXISTS discovered_patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pattern_type TEXT NOT NULL,
        pattern_data TEXT NOT NULL,
        frequency INTEGER,
        confidence REAL,
        first_seen TEXT,
        last_seen TEXT,
        auto_created BOOLEAN DEFAULT 0
    )''')

    # 生成的场景计划表
    c.execute('''CREATE TABLE IF NOT EXISTS auto_scenes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scene_name TEXT NOT NULL,
        scene_description TEXT,
        trigger_pattern TEXT,
        actions_json TEXT NOT NULL,
        created_at TEXT,
        last_triggered TEXT,
        trigger_count INTEGER DEFAULT 0,
        enabled BOOLEAN DEFAULT 1
    )''')

    # 执行历史表
    c.execute('''CREATE TABLE IF NOT EXISTS execution_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scene_id INTEGER,
        executed_at TEXT,
        result TEXT,
        details TEXT
    )''')

    conn.commit()
    conn.close()
    print(f"场景自动发现数据库初始化完成: {db_path}")
    return db_path


def record_behavior_sequence(sequence_data):
    """记录行为序列"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    timestamp = datetime.now().isoformat()
    action_count = len(sequence_data)
    # 计算时间跨度（假设序列中包含时间信息）
    time_span = 0

    c.execute('''INSERT INTO behavior_sequences
        (timestamp, sequence_data, action_count, time_span_seconds)
        VALUES (?, ?, ?, ?)''',
        (timestamp, json.dumps(sequence_data), action_count, time_span))

    conn.commit()
    conn.close()


def analyze_recent_sequences(min_count=3):
    """分析最近的行为序列，识别重复模式"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # 获取最近的行为序列
    c.execute('''SELECT timestamp, sequence_data, action_count
        FROM behavior_sequences
        ORDER BY timestamp DESC
        LIMIT 100''')

    sequences = c.fetchall()
    conn.close()

    if not sequences:
        return []

    # 分析序列模式
    pattern_counts = defaultdict(int)
    sequence_lists = {}

    for ts, seq_json, count in sequences:
        seq = json.loads(seq_json)
        # 将序列转换为可哈希的形式
        seq_key = tuple(seq[-3:])  # 取最后3个动作作为模式
        pattern_counts[seq_key] += 1
        if seq_key not in sequence_lists:
            sequence_lists[seq_key] = []
        sequence_lists[seq_key].append((ts, seq))

    # 找出高频模式
    frequent_patterns = []
    for pattern, count in pattern_counts.items():
        if count >= min_count:
            frequent_patterns.append({
                'pattern': list(pattern),
                'frequency': count,
                'sequences': sequence_lists[pattern]
            })

    return sorted(frequent_patterns, key=lambda x: x['frequency'], reverse=True)


def generate_scene_from_pattern(pattern_data):
    """根据模式生成场景计划"""
    pattern = pattern_data['pattern']
    actions = []

    # 基于模式动作生成场景步骤
    for action in pattern:
        if isinstance(action, dict):
            step = action
        else:
            # 通用动作
            step = {
                'tool': 'do',
                'args': [action]
            }
        actions.append(step)

    return {
        'name': f'Auto_Discovery_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
        'description': f'自动发现的场景模式 (频率: {pattern_data["frequency"]})',
        'trigger': 'manual',
        'steps': actions
    }


def discover_and_create_scenes(min_frequency=3):
    """发现可自动化场景并创建"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # 分析模式
    patterns = analyze_recent_sequences(min_frequency)

    created_scenes = []
    for pattern_data in patterns:
        # 检查是否已存在类似场景
        pattern_key = json.dumps(pattern_data['pattern'])

        c.execute('''SELECT id FROM discovered_patterns
            WHERE pattern_data = ? AND confidence >= 0.5''',
            (pattern_key,))

        existing = c.fetchone()

        if not existing:
            # 记录新发现的模式
            first_seen = datetime.now().isoformat()
            confidence = min(pattern_data['frequency'] / 10.0, 1.0)

            c.execute('''INSERT INTO discovered_patterns
                (pattern_type, pattern_data, frequency, confidence, first_seen, last_seen)
                VALUES (?, ?, ?, ?, ?, ?)''',
                ('sequence', pattern_key, pattern_data['frequency'],
                 confidence, first_seen, first_seen))

            pattern_id = c.lastrowid

            # 生成场景计划
            scene = generate_scene_from_pattern(pattern_data)

            c.execute('''INSERT INTO auto_scenes
                (scene_name, scene_description, trigger_pattern, actions_json, created_at)
                VALUES (?, ?, ?, ?, ?)''',
                (scene['name'], scene['description'], pattern_key,
                 json.dumps(scene['steps']), datetime.now().isoformat()))

            created_scenes.append(scene)

    conn.commit()
    conn.close()

    return created_scenes


def list_auto_scenes():
    """列出所有自动发现的场景"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute('''SELECT id, scene_name, scene_description, trigger_count, enabled, created_at
        FROM auto_scenes ORDER BY created_at DESC''')

    scenes = c.fetchall()
    conn.close()

    return [{
        'id': s[0],
        'name': s[1],
        'description': s[2],
        'trigger_count': s[3],
        'enabled': s[4],
        'created_at': s[5]
    } for s in scenes]


def enable_scene(scene_id, enabled=True):
    """启用/禁用场景"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute('UPDATE auto_scenes SET enabled = ? WHERE id = ?', (enabled, scene_id))
    conn.commit()
    conn.close()
    return enabled


def delete_scene(scene_id):
    """删除场景"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute('DELETE FROM auto_scenes WHERE id = ?', (scene_id,))
    conn.commit()
    conn.close()


def get_scene_details(scene_id):
    """获取场景详情"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute('''SELECT id, scene_name, scene_description, trigger_pattern,
        actions_json, created_at, trigger_count, enabled
        FROM auto_scenes WHERE id = ?''', (scene_id,))

    scene = c.fetchone()
    conn.close()

    if scene:
        return {
            'id': scene[0],
            'name': scene[1],
            'description': scene[2],
            'trigger_pattern': scene[3],
            'actions': json.loads(scene[4]),
            'created_at': scene[5],
            'trigger_count': scene[6],
            'enabled': scene[7]
        }
    return None


def execute_scene(scene_id):
    """执行自动发现的场景"""
    scene = get_scene_details(scene_id)
    if not scene:
        return {'success': False, 'error': 'Scene not found'}

    if not scene['enabled']:
        return {'success': False, 'error': 'Scene is disabled'}

    # 更新触发计数
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''UPDATE auto_scenes SET trigger_count = trigger_count + 1,
        last_triggered = ? WHERE id = ?''',
        (datetime.now().isoformat(), scene_id))
    conn.commit()
    conn.close()

    # 执行场景动作
    results = []
    for action in scene['actions']:
        if 'tool' in action:
            tool = action['tool']
            args = action.get('args', [])
            cmd = ['python', os.path.join(SCRIPT_DIR, f'{tool}.py')] + args
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                results.append({
                    'tool': tool,
                    'success': result.returncode == 0,
                    'output': result.stdout[:200] if result.stdout else ''
                })
            except Exception as e:
                results.append({
                    'tool': tool,
                    'success': False,
                    'error': str(e)
                })

    # 记录执行历史
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''INSERT INTO execution_history
        (scene_id, executed_at, result, details)
        VALUES (?, ?, ?, ?)''',
        (scene_id, datetime.now().isoformat(),
         'success' if all(r.get('success', False) for r in results) else 'partial',
         json.dumps(results)))
    conn.commit()
    conn.close()

    return {
        'success': True,
        'scene_id': scene_id,
        'results': results
    }


def get_discovery_summary():
    """获取发现摘要统计"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # 模式统计
    c.execute('SELECT COUNT(*) FROM discovered_patterns')
    pattern_count = c.fetchone()[0]

    # 场景统计
    c.execute('SELECT COUNT(*) FROM auto_scenes')
    scene_count = c.fetchone()[0]

    c.execute('SELECT COUNT(*) FROM auto_scenes WHERE enabled = 1')
    enabled_count = c.fetchone()[0]

    # 执行统计
    c.execute('SELECT COUNT(*) FROM execution_history')
    execution_count = c.fetchone()[0]

    c.execute('SELECT COUNT(*) FROM execution_history WHERE result = "success"')
    success_count = c.fetchone()[0]

    conn.close()

    return {
        'discovered_patterns': pattern_count,
        'total_scenes': scene_count,
        'enabled_scenes': enabled_count,
        'total_executions': execution_count,
        'successful_executions': success_count,
        'success_rate': round(success_count / execution_count * 100, 1) if execution_count > 0 else 0
    }


def main():
    parser = argparse.ArgumentParser(
        description='LLM-OS 智能场景自动发现与执行引擎'
    )
    parser.add_argument('--init', action='store_true',
                        help='初始化数据库')
    parser.add_argument('--analyze', action='store_true',
                        help='分析行为模式')
    parser.add_argument('--discover', action='store_true',
                        help='发现并创建自动化场景')
    parser.add_argument('--min-freq', type=int, default=3,
                        help='最小发现频率 (默认: 3)')
    parser.add_argument('--list-scenes', action='store_true',
                        help='列出自动发现的场景')
    parser.add_argument('--scene-details', type=int, metavar='ID',
                        help='获取场景详情')
    parser.add_argument('--execute', type=int, metavar='ID',
                        help='执行场景')
    parser.add_argument('--enable', type=int, metavar='ID',
                        help='启用场景')
    parser.add_argument('--disable', type=int, metavar='ID',
                        help='禁用场景')
    parser.add_argument('--delete', type=int, metavar='ID',
                        help='删除场景')
    parser.add_argument('--summary', action='store_true',
                        help='获取发现摘要统计')
    parser.add_argument('--version', action='store_true',
                        help='显示版本信息')

    args = parser.parse_args()

    if args.version:
        print('llm_os_scene_auto_discovery.py version 1.0.0')
        return

    if args.init:
        init_db()
        return

    if args.analyze:
        patterns = analyze_recent_sequences()
        print(f'发现 {len(patterns)} 个行为模式:')
        for p in patterns[:10]:
            print(f'  - 模式: {p["pattern"]}, 频率: {p["frequency"]}')
        return

    if args.discover:
        scenes = discover_and_create_scenes(args.min_freq)
        print(f'创建了 {len(scenes)} 个自动化场景:')
        for s in scenes:
            print(f'  - {s["name"]}: {s["description"]}')
        return

    if args.list_scenes:
        scenes = list_auto_scenes()
        print(f'自动发现的场景 ({len(scenes)} 个):')
        for s in scenes:
            status = '✓' if s['enabled'] else '✗'
            print(f'  [{status}] {s["name"]}: {s["description"]} (触发: {s["trigger_count"]}次)')
        return

    if args.scene_details:
        details = get_scene_details(args.scene_details)
        if details:
            print(f'场景: {details["name"]}')
            print(f'描述: {details["description"]}')
            print(f'启用: {details["enabled"]}')
            print(f'触发次数: {details["trigger_count"]}')
            print(f'创建时间: {details["created_at"]}')
            print(f'动作: {json.dumps(details["actions"], ensure_ascii=False)}')
        else:
            print(f'未找到场景 ID: {args.scene_details}')
        return

    if args.execute:
        result = execute_scene(args.execute)
        if result['success']:
            print(f'场景执行成功, 触发了 {len(result["results"])} 个动作')
        else:
            print(f'场景执行失败: {result.get("error", "未知错误")}')
        return

    if args.enable:
        enable_scene(args.enable, True)
        print(f'场景 {args.enable} 已启用')
        return

    if args.disable:
        enable_scene(args.enable, False)
        print(f'场景 {args.enable} 已禁用')
        return

    if args.delete:
        delete_scene(args.delete)
        print(f'场景 {args.delete} 已删除')
        return

    if args.summary:
        stats = get_discovery_summary()
        print('=== 场景自动发现统计 ===')
        print(f'发现模式数: {stats["discovered_patterns"]}')
        print(f'总场景数: {stats["total_scenes"]}')
        print(f'启用场景数: {stats["enabled_scenes"]}')
        print(f'总执行次数: {stats["total_executions"]}')
        print(f'成功次数: {stats["successful_executions"]}')
        print(f'成功率: {stats["success_rate"]}%')
        return

    parser.print_help()


if __name__ == '__main__':
    main()