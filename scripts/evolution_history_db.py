#!/usr/bin/env python3
"""
进化历史数据库模块
用于持久化存储进化环的历史过程和结果，为未来的进化策略提供数据支持
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# 数据库文件路径
DB_PATH = "runtime/state/evolution_history.db"

def init_database():
    """
    初始化进化历史数据库
    """
    # 确保数据库目录存在
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 创建进化轮次表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS evolution_rounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            round_number INTEGER UNIQUE NOT NULL,
            timestamp TEXT NOT NULL,
            current_goal TEXT,
            status TEXT,
            execution_time REAL,
            result TEXT,
            metadata TEXT
        )
    ''')

    # 创建进化动作表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS evolution_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            round_id INTEGER,
            action_type TEXT NOT NULL,
            action_description TEXT,
            timestamp TEXT NOT NULL,
            result TEXT,
            FOREIGN KEY (round_id) REFERENCES evolution_rounds (id)
        )
    ''')

    # 创建性能指标表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS performance_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            round_id INTEGER,
            metric_name TEXT NOT NULL,
            metric_value TEXT,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (round_id) REFERENCES evolution_rounds (id)
        )
    ''')

    conn.commit()
    conn.close()

def save_evolution_round(round_number: int, current_goal: str, status: str,
                        execution_time: float = 0.0, result: str = "",
                        metadata: Dict[str, Any] = None):
    """
    保存进化轮次信息

    Args:
        round_number: 轮次数
        current_goal: 当前目标
        status: 状态 (success, failed, in_progress)
        execution_time: 执行时间
        result: 执行结果
        metadata: 其他元数据
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 插入轮次信息
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO evolution_rounds
            (round_number, timestamp, current_goal, status, execution_time, result, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            round_number,
            datetime.now().isoformat(),
            current_goal,
            status,
            execution_time,
            result,
            json.dumps(metadata) if metadata else "{}"
        ))

        conn.commit()
        round_id = cursor.lastrowid
        print(f"成功保存进化轮次 {round_number}")

    except Exception as e:
        print(f"保存进化轮次时发生错误: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()

def save_evolution_action(round_number: int, action_type: str, action_description: str,
                         result: str = ""):
    """
    保存进化动作信息

    Args:
        round_number: 轮次数
        action_type: 动作类型 (assume, plan, track, verify, decide)
        action_description: 动作描述
        result: 动作结果
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 先查找对应的轮次ID
        cursor.execute('SELECT id FROM evolution_rounds WHERE round_number = ?', (round_number,))
        result_row = cursor.fetchone()

        if not result_row:
            print(f"找不到轮次 {round_number}，无法保存动作")
            return

        round_id = result_row[0]

        # 插入动作信息
        cursor.execute('''
            INSERT INTO evolution_actions
            (round_id, action_type, action_description, timestamp, result)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            round_id,
            action_type,
            action_description,
            datetime.now().isoformat(),
            result
        ))

        conn.commit()
        print(f"成功保存进化动作: {action_type} (轮次 {round_number})")

    except Exception as e:
        print(f"保存进化动作时发生错误: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()

def save_performance_metric(round_number: int, metric_name: str, metric_value: str):
    """
    保存性能指标

    Args:
        round_number: 轮次数
        metric_name: 指标名称
        metric_value: 指标值
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 先查找对应的轮次ID
        cursor.execute('SELECT id FROM evolution_rounds WHERE round_number = ?', (round_number,))
        result_row = cursor.fetchone()

        if not result_row:
            print(f"找不到轮次 {round_number}，无法保存性能指标")
            return

        round_id = result_row[0]

        # 插入性能指标
        cursor.execute('''
            INSERT INTO performance_metrics
            (round_id, metric_name, metric_value, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (
            round_id,
            metric_name,
            metric_value,
            datetime.now().isoformat()
        ))

        conn.commit()
        print(f"成功保存性能指标: {metric_name} (轮次 {round_number})")

    except Exception as e:
        print(f"保存性能指标时发生错误: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()

def get_evolution_round(round_number: int) -> Optional[Dict[str, Any]]:
    """
    获取指定轮次的进化信息

    Args:
        round_number: 轮次数

    Returns:
        轮次信息字典或None
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 获取轮次基本信息
        cursor.execute('SELECT * FROM evolution_rounds WHERE round_number = ?', (round_number,))
        round_row = cursor.fetchone()

        if not round_row:
            return None

        # 获取动作信息
        cursor.execute('SELECT * FROM evolution_actions WHERE round_id = ?', (round_row[0],))
        actions_rows = cursor.fetchall()

        # 获取性能指标
        cursor.execute('SELECT * FROM performance_metrics WHERE round_id = ?', (round_row[0],))
        metrics_rows = cursor.fetchall()

        # 构造返回数据
        result = {
            "round_info": {
                "id": round_row[0],
                "round_number": round_row[1],
                "timestamp": round_row[2],
                "current_goal": round_row[3],
                "status": round_row[4],
                "execution_time": round_row[5],
                "result": round_row[6],
                "metadata": json.loads(round_row[7]) if round_row[7] else {}
            },
            "actions": [
                {
                    "id": row[0],
                    "round_id": row[1],
                    "action_type": row[2],
                    "action_description": row[3],
                    "timestamp": row[4],
                    "result": row[5]
                } for row in actions_rows
            ],
            "metrics": [
                {
                    "id": row[0],
                    "round_id": row[1],
                    "metric_name": row[2],
                    "metric_value": row[3],
                    "timestamp": row[4]
                } for row in metrics_rows
            ]
        }

        return result

    except Exception as e:
        print(f"获取进化轮次信息时发生错误: {str(e)}")
        return None
    finally:
        conn.close()

def get_all_evolution_rounds() -> List[Dict[str, Any]]:
    """
    获取所有进化轮次信息

    Returns:
        所有轮次信息列表
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 获取所有轮次基本信息
        cursor.execute('SELECT * FROM evolution_rounds ORDER BY round_number ASC')
        rounds_rows = cursor.fetchall()

        result = []
        for row in rounds_rows:
            # 获取动作信息
            cursor.execute('SELECT * FROM evolution_actions WHERE round_id = ?', (row[0],))
            actions_rows = cursor.fetchall()

            # 获取性能指标
            cursor.execute('SELECT * FROM performance_metrics WHERE round_id = ?', (row[0],))
            metrics_rows = cursor.fetchall()

            # 构造返回数据
            round_info = {
                "round_info": {
                    "id": row[0],
                    "round_number": row[1],
                    "timestamp": row[2],
                    "current_goal": row[3],
                    "status": row[4],
                    "execution_time": row[5],
                    "result": row[6],
                    "metadata": json.loads(row[7]) if row[7] else {}
                },
                "actions": [
                    {
                        "id": action_row[0],
                        "round_id": action_row[1],
                        "action_type": action_row[2],
                        "action_description": action_row[3],
                        "timestamp": action_row[4],
                        "result": action_row[5]
                    } for action_row in actions_rows
                ],
                "metrics": [
                    {
                        "id": metric_row[0],
                        "round_id": metric_row[1],
                        "metric_name": metric_row[2],
                        "metric_value": metric_row[3],
                        "timestamp": metric_row[4]
                    } for metric_row in metrics_rows
                ]
            }
            result.append(round_info)

        return result

    except Exception as e:
        print(f"获取所有进化轮次信息时发生错误: {str(e)}")
        return []
    finally:
        conn.close()

def get_latest_evolution_round() -> Optional[Dict[str, Any]]:
    """
    获取最新的进化轮次信息

    Returns:
        最新轮次信息或None
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 获取最新轮次
        cursor.execute('SELECT * FROM evolution_rounds ORDER BY round_number DESC LIMIT 1')
        round_row = cursor.fetchone()

        if not round_row:
            return None

        # 获取动作信息
        cursor.execute('SELECT * FROM evolution_actions WHERE round_id = ?', (round_row[0],))
        actions_rows = cursor.fetchall()

        # 获取性能指标
        cursor.execute('SELECT * FROM performance_metrics WHERE round_id = ?', (round_row[0],))
        metrics_rows = cursor.fetchall()

        # 构造返回数据
        result = {
            "round_info": {
                "id": round_row[0],
                "round_number": round_row[1],
                "timestamp": round_row[2],
                "current_goal": round_row[3],
                "status": round_row[4],
                "execution_time": round_row[5],
                "result": round_row[6],
                "metadata": json.loads(round_row[7]) if round_row[7] else {}
            },
            "actions": [
                {
                    "id": row[0],
                    "round_id": row[1],
                    "action_type": row[2],
                    "action_description": row[3],
                    "timestamp": row[4],
                    "result": row[5]
                } for row in actions_rows
            ],
            "metrics": [
                {
                    "id": row[0],
                    "round_id": row[1],
                    "metric_name": row[2],
                    "metric_value": row[3],
                    "timestamp": row[4]
                } for row in metrics_rows
            ]
        }

        return result

    except Exception as e:
        print(f"获取最新进化轮次信息时发生错误: {str(e)}")
        return None
    finally:
        conn.close()

def main():
    """主函数 - 用于测试数据库功能"""
    print("初始化进化历史数据库...")
    init_database()

    # 测试保存数据
    print("测试保存进化轮次...")
    save_evolution_round(
        round_number=76,
        current_goal="建立进化历史数据库：将每次进化过程和结果持久化存储，为未来的进化策略提供数据支持",
        status="success",
        execution_time=1.23,
        result="数据库模块创建成功",
        metadata={"author": "Evolution Agent", "version": "1.0"}
    )

    print("测试保存进化动作...")
    save_evolution_action(76, "track", "创建 evolution_history_db.py 模块")
    save_evolution_action(76, "verify", "模块功能测试通过")

    print("测试保存性能指标...")
    save_performance_metric(76, "execution_time", "1.23")
    save_performance_metric(76, "data_storage_size", "1.5KB")

    print("测试获取数据...")
    round_info = get_evolution_round(76)
    if round_info:
        print(f"获取轮次 {round_info['round_info']['round_number']} 信息成功")
        print(f"目标: {round_info['round_info']['current_goal']}")
        print(f"状态: {round_info['round_info']['status']}")
        print(f"动作数: {len(round_info['actions'])}")
        print(f"指标数: {len(round_info['metrics'])}")

    latest_round = get_latest_evolution_round()
    if latest_round:
        print(f"获取最新轮次 {latest_round['round_info']['round_number']} 信息成功")

    print("数据库功能测试完成!")

if __name__ == "__main__":
    main()