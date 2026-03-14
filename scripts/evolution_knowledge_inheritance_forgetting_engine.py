#!/usr/bin/env python3
"""
智能全场景进化知识深度传承与自适应遗忘引擎
模拟人类记忆的深度遗忘机制，让系统能够智能评估进化知识的价值、
实现跨轮次的知识传承、管理知识的老化与更新，
实现「记住重要的、遗忘无用的」的进化知识管理能力，
让系统在持续进化中保持知识的新鲜度和相关性。

功能：
1. 进化知识价值评估（使用频率、相关性、时间衰减）
2. 知识传承机制（核心知识永久保留、衍生知识选择性传承）
3. 自适应遗忘（低价值知识自动降权或遗忘）
4. 知识老化检测与更新提醒
5. 与 do.py 深度集成，支持关键词触发

Version: 1.0.0
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import math

# 添加项目根目录到 Python 路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, SCRIPT_DIR)


def _safe_print(text: str):
    """安全打印，处理编码问题"""
    import re
    try:
        print(text)
    except UnicodeEncodeError:
        clean_text = re.sub(r'[^\x00-\x7F]+', '', text)
        print(clean_text)


class KnowledgeInheritanceForgettingEngine:
    """进化知识深度传承与自适应遗忘引擎"""

    def __init__(self):
        self.db_path = os.path.join(PROJECT_ROOT, "runtime/state/evolution_history.db")
        self.state_path = os.path.join(PROJECT_ROOT, "runtime/state/knowledge_inheritance_state.json")
        self.knowledge_db_path = os.path.join(PROJECT_ROOT, "runtime/state/knowledge_value.db")
        self.config = self._load_config()
        self._init_knowledge_db()

    def _load_config(self) -> Dict:
        """加载配置"""
        default_config = {
            # 价值评估参数
            'use_frequency_weight': 0.3,        # 使用频率权重
            'relevance_weight': 0.4,              # 相关性权重
            'recency_weight': 0.3,               # 时间衰减权重

            # 遗忘参数
            'forgetting_threshold': 0.2,         # 遗忘阈值（低于此值考虑遗忘）
            'forgetting_interval': 20,           # 每20轮检查一次遗忘
            'permanent_knowledge_threshold': 0.8, # 永久保留阈值

            # 传承参数
            'core_knowledge_categories': ['strategy', 'decision', 'pattern'],  # 核心知识类别
            'inheritance_retention_rate': 0.9,  # 传承保留率

            # 老化检测
            'aging_check_interval': 15,          # 老化检查间隔（轮）
            'aging_threshold': 0.5,              # 老化阈值

            # 自动执行
            'auto_forgetting_enabled': True,     # 自动遗忘启用
            'auto_aging_check_enabled': True,    # 自动老化检查启用
        }

        config_path = os.path.join(PROJECT_ROOT, "runtime/state/knowledge_inheritance_config.json")
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    default_config.update(saved_config)
        except Exception as e:
            _safe_print(f"加载配置失败: {e}")

        return default_config

    def _save_config(self, config: Dict):
        """保存配置"""
        config_path = os.path.join(PROJECT_ROOT, "runtime/state/knowledge_inheritance_config.json")
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"保存配置失败: {e}")

    def _init_knowledge_db(self):
        """初始化知识价值数据库"""
        try:
            os.makedirs(os.path.dirname(self.knowledge_db_path), exist_ok=True)
            conn = sqlite3.connect(self.knowledge_db_path)
            cursor = conn.cursor()

            # 创建知识价值表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_values (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    knowledge_id TEXT UNIQUE NOT NULL,
                    knowledge_type TEXT,
                    category TEXT,
                    creation_round INTEGER,
                    last_access_round INTEGER,
                    use_count INTEGER DEFAULT 0,
                    relevance_score REAL DEFAULT 0.5,
                    value_score REAL DEFAULT 0.5,
                    is_permanent INTEGER DEFAULT 0,
                    is_forgotten INTEGER DEFAULT 0,
                    aging_score REAL DEFAULT 0.0,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)

            # 创建传承记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inheritance_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_round INTEGER,
                    target_round INTEGER,
                    knowledge_id TEXT,
                    inheritance_type TEXT,
                    retained INTEGER DEFAULT 1,
                    created_at TEXT
                )
            """)

            conn.commit()
            conn.close()
        except Exception as e:
            _safe_print(f"初始化知识数据库失败: {e}")

    def get_current_round(self) -> int:
        """获取当前进化轮次"""
        try:
            if os.path.exists(self.db_path):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT MAX(round_number) FROM evolution_rounds")
                result = cursor.fetchone()
                conn.close()
                if result and result[0]:
                    return result[0]
        except Exception as e:
            _safe_print(f"获取当前轮次失败: {e}")
        return 0

    def evaluate_knowledge_value(self, knowledge_id: str, knowledge_type: str = 'general',
                                   category: str = 'general') -> Dict:
        """
        评估知识价值
        综合使用频率、相关性和时间衰减计算价值分数
        """
        try:
            conn = sqlite3.connect(self.knowledge_db_path)
            cursor = conn.cursor()

            # 获取知识使用数据
            cursor.execute("""
                SELECT use_count, last_access_round, relevance_score, creation_round
                FROM knowledge_values
                WHERE knowledge_id = ?
            """, (knowledge_id,))

            row = cursor.fetchone()
            conn.close()

            current_round = self.get_current_round()

            if not row:
                # 新知识，赋予基础价值
                return {
                    'knowledge_id': knowledge_id,
                    'value_score': 0.5,
                    'use_frequency_score': 0.5,
                    'relevance_score': 0.5,
                    'recency_score': 0.5,
                    'is_new': True
                }

            use_count, last_access_round, relevance, creation_round = row

            # 1. 使用频率分数（归一化到 0-1）
            max_use_count = 100  # 假设最大使用次数
            use_frequency_score = min(use_count / max_use_count, 1.0)

            # 2. 相关性分数（直接使用存储值）
            relevance_score = relevance if relevance else 0.5

            # 3. 时间衰减分数（基于最后访问时间）
            if last_access_round and current_round > last_access_round:
                rounds_since_access = current_round - last_access_round
                # 使用指数衰减
                decay_rate = 0.05  # 每轮衰减5%
                recency_score = math.exp(-decay_rate * rounds_since_access)
            else:
                recency_score = 1.0

            # 计算综合价值分数
            value_score = (
                use_frequency_score * self.config['use_frequency_weight'] +
                relevance_score * self.config['relevance_weight'] +
                recency_score * self.config['recency_weight']
            )

            return {
                'knowledge_id': knowledge_id,
                'value_score': value_score,
                'use_frequency_score': use_frequency_score,
                'relevance_score': relevance_score,
                'recency_score': recency_score,
                'use_count': use_count,
                'rounds_since_access': current_round - last_access_round if last_access_round else 0,
                'is_new': False
            }

        except Exception as e:
            _safe_print(f"评估知识价值失败: {e}")
            return {
                'knowledge_id': knowledge_id,
                'value_score': 0.5,
                'error': str(e)
            }

    def record_knowledge_access(self, knowledge_id: str, knowledge_type: str = 'general',
                                   category: str = 'general') -> Dict:
        """记录知识访问，增加使用次数"""
        try:
            current_round = self.get_current_round()

            conn = sqlite3.connect(self.knowledge_db_path)
            cursor = conn.cursor()

            # 检查知识是否存在
            cursor.execute("""
                SELECT id FROM knowledge_values WHERE knowledge_id = ?
            """, (knowledge_id,))

            row = cursor.fetchone()

            if row:
                # 更新使用次数和最后访问时间
                cursor.execute("""
                    UPDATE knowledge_values
                    SET use_count = use_count + 1,
                        last_access_round = ?,
                        updated_at = ?
                    WHERE knowledge_id = ?
                """, (current_round, datetime.now().isoformat(), knowledge_id))
            else:
                # 创建新记录
                cursor.execute("""
                    INSERT INTO knowledge_values
                    (knowledge_id, knowledge_type, category, creation_round, last_access_round,
                     use_count, relevance_score, value_score, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, 1, 0.5, 0.5, ?, ?)
                """, (knowledge_id, knowledge_type, category, current_round, current_round,
                      datetime.now().isoformat(), datetime.now().isoformat()))

            conn.commit()
            conn.close()

            return {'status': 'recorded', 'knowledge_id': knowledge_id}

        except Exception as e:
            _safe_print(f"记录知识访问失败: {e}")
            return {'status': 'failed', 'error': str(e)}

    def assess_knowledge_forgetting(self) -> Dict:
        """评估需要遗忘的知识"""
        forgetting_candidates = []
        current_round = self.get_current_round()

        try:
            conn = sqlite3.connect(self.knowledge_db_path)
            cursor = conn.cursor()

            # 获取所有非永久、非遗忘的知识
            cursor.execute("""
                SELECT knowledge_id, knowledge_type, category, value_score,
                       use_count, last_access_round, creation_round
                FROM knowledge_values
                WHERE is_permanent = 0 AND is_forgotten = 0
            """)

            rows = cursor.fetchall()
            conn.close()

            threshold = self.config.get('forgetting_threshold', 0.2)
            permanent_threshold = self.config.get('permanent_knowledge_threshold', 0.8)

            for row in rows:
                knowledge_id, knowledge_type, category, value_score, use_count, last_access_round, creation_round = row

                # 跳过核心知识类别
                if category in self.config.get('core_knowledge_categories', []):
                    continue

                # 计算价值分数
                value_result = self.evaluate_knowledge_value(knowledge_id, knowledge_type, category)
                current_value = value_result.get('value_score', 0.5)

                if current_value < threshold:
                    forgetting_candidates.append({
                        'knowledge_id': knowledge_id,
                        'knowledge_type': knowledge_type,
                        'category': category,
                        'value_score': current_value,
                        'use_count': use_count,
                        'rounds_since_access': current_round - last_access_round if last_access_round else current_round - creation_round,
                        'forgetting_reason': 'low_value'
                    })

            return {
                'forgetting_candidates': forgetting_candidates,
                'total_candidates': len(forgetting_candidates),
                'threshold': threshold
            }

        except Exception as e:
            _safe_print(f"评估遗忘候选失败: {e}")
            return {'forgetting_candidates': [], 'error': str(e)}

    def execute_forgetting(self, knowledge_ids: List[str] = None) -> Dict:
        """执行遗忘操作"""
        forgotten_knowledge = []

        try:
            conn = sqlite3.connect(self.knowledge_db_path)
            cursor = conn.cursor()

            if knowledge_ids:
                # 指定遗忘特定知识
                for kid in knowledge_ids:
                    cursor.execute("""
                        UPDATE knowledge_values
                        SET is_forgotten = 1, updated_at = ?
                        WHERE knowledge_id = ?
                    """, (datetime.now().isoformat(), kid))
                    forgotten_knowledge.append(kid)
            else:
                # 自动遗忘低价值知识
                candidates = self.assess_knowledge_forgetting()
                for candidate in candidates.get('forgetting_candidates', [])[:10]:  # 最多遗忘10条
                    kid = candidate['knowledge_id']
                    cursor.execute("""
                        UPDATE knowledge_values
                        SET is_forgotten = 1, updated_at = ?
                        WHERE knowledge_id = ?
                    """, (datetime.now().isoformat(), kid))
                    forgotten_knowledge.append(kid)

            conn.commit()
            conn.close()

            _safe_print(f"已完成 {len(forgotten_knowledge)} 条知识的遗忘操作")

            return {
                'status': 'completed',
                'forgotten_count': len(forgotten_knowledge),
                'forgotten_knowledge': forgotten_knowledge
            }

        except Exception as e:
            _safe_print(f"执行遗忘失败: {e}")
            return {'status': 'failed', 'error': str(e)}

    def check_knowledge_aging(self) -> Dict:
        """检测知识老化"""
        aging_knowledge = []
        current_round = self.get_current_round()

        try:
            conn = sqlite3.connect(self.knowledge_db_path)
            cursor = conn.cursor()

            # 获取所有知识
            cursor.execute("""
                SELECT knowledge_id, knowledge_type, category, creation_round, value_score
                FROM knowledge_values
                WHERE is_forgotten = 0
            """)

            rows = cursor.fetchall()
            conn.close()

            aging_threshold = self.config.get('aging_threshold', 0.5)

            for row in rows:
                knowledge_id, knowledge_type, category, creation_round, value_score = row

                # 计算老化分数（基于未更新的时间）
                rounds_since_creation = current_round - creation_round
                aging_score = min(rounds_since_creation / 100, 1.0)  # 100轮后完全老化

                if aging_score > aging_threshold and value_score < 0.6:
                    aging_knowledge.append({
                        'knowledge_id': knowledge_id,
                        'knowledge_type': knowledge_type,
                        'category': category,
                        'aging_score': aging_score,
                        'value_score': value_score,
                        'rounds_since_creation': rounds_since_creation,
                        'aging_reason': 'stale_and_low_value'
                    })

            return {
                'aging_knowledge': aging_knowledge,
                'total_aging': len(aging_knowledge),
                'aging_threshold': aging_threshold
            }

        except Exception as e:
            _safe_print(f"检测知识老化失败: {e}")
            return {'aging_knowledge': [], 'error': str(e)}

    def inherit_knowledge(self, source_round: int, target_round: int,
                          knowledge_category: str = 'general') -> Dict:
        """执行知识传承"""
        inherited_knowledge = []

        try:
            conn = sqlite3.connect(self.knowledge_db_path)
            cursor = conn.cursor()

            # 获取源轮次的高价值知识
            retention_rate = self.config.get('inheritance_retention_rate', 0.9)

            cursor.execute("""
                SELECT knowledge_id, knowledge_type, category, value_score
                FROM knowledge_values
                WHERE creation_round <= ? AND is_forgotten = 0
                ORDER BY value_score DESC
                LIMIT 50
            """, (source_round,))

            rows = cursor.fetchall()

            for row in rows:
                knowledge_id, knowledge_type, category, value_score = row

                # 核心知识类别永久保留
                if category in self.config.get('core_knowledge_categories', []):
                    retained = 1
                else:
                    # 根据价值决定是否保留
                    retained = 1 if value_score >= retention_rate else 0

                if retained:
                    # 记录传承
                    cursor.execute("""
                        INSERT INTO inheritance_records
                        (source_round, target_round, knowledge_id, inheritance_type, retained, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (source_round, target_round, knowledge_id, 'auto', retained,
                          datetime.now().isoformat()))

                    inherited_knowledge.append(knowledge_id)

            conn.commit()
            conn.close()

            _safe_print(f"知识传承完成：从 round {source_round} 传承到 round {target_round}，共 {len(inherited_knowledge)} 条")

            return {
                'status': 'completed',
                'source_round': source_round,
                'target_round': target_round,
                'inherited_count': len(inherited_knowledge),
                'inherited_knowledge': inherited_knowledge
            }

        except Exception as e:
            _safe_print(f"执行知识传承失败: {e}")
            return {'status': 'failed', 'error': str(e)}

    def get_knowledge_status(self) -> Dict:
        """获取知识管理状态"""
        current_round = self.get_current_round()

        try:
            conn = sqlite3.connect(self.knowledge_db_path)
            cursor = conn.cursor()

            # 统计知识数量
            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN is_forgotten = 1 THEN 1 ELSE 0 END) as forgotten,
                    SUM(CASE WHEN is_permanent = 1 THEN 1 ELSE 0 END) as permanent,
                    SUM(CASE WHEN is_forgotten = 0 AND is_permanent = 0 THEN 1 ELSE 0 END) as active
                FROM knowledge_values
            """)
            stats_row = cursor.fetchone()
            conn.close()

            # 评估遗忘候选
            forgetting = self.assess_knowledge_forgetting()

            # 检测老化
            aging = self.check_knowledge_aging()

            return {
                'status': 'active',
                'current_round': current_round,
                'knowledge_stats': {
                    'total': stats_row[0] if stats_row else 0,
                    'forgotten': stats_row[1] if stats_row else 0,
                    'permanent': stats_row[2] if stats_row else 0,
                    'active': stats_row[3] if stats_row else 0
                },
                'forgetting': {
                    'candidates_count': forgetting.get('total_candidates', 0)
                },
                'aging': {
                    'aging_count': aging.get('total_aging', 0)
                },
                'config': self.config
            }

        except Exception as e:
            _safe_print(f"获取知识状态失败: {e}")
            return {'status': 'error', 'error': str(e)}

    def run_full_cycle(self, force: bool = False) -> Dict:
        """运行完整的知识传承与遗忘周期"""
        _safe_print("=" * 60)
        _safe_print("进化知识深度传承与自适应遗忘引擎")
        _safe_print("=" * 60)

        current_round = self.get_current_round()

        # 1. 知识传承
        _safe_print("\n[1/4] 执行知识传承...")
        if current_round > 1:
            inherit_result = self.inherit_knowledge(current_round - 1, current_round)
            _safe_print(f"    传承知识数量: {inherit_result.get('inherited_count', 0)}")

        # 2. 评估遗忘候选
        _safe_print("\n[2/4] 评估遗忘候选...")
        forgetting = self.assess_knowledge_forgetting()
        _safe_print(f"    可遗忘知识数量: {forgetting.get('total_candidates', 0)}")

        # 3. 执行遗忘（如果启用且需要）
        _safe_print("\n[3/4] 执行自适应遗忘...")
        if self.config.get('auto_forgetting_enabled', True) or force:
            if forgetting.get('total_candidates', 0) > 0:
                forget_result = self.execute_forgetting()
                _safe_print(f"    已遗忘知识数量: {forget_result.get('forgotten_count', 0)}")
            else:
                _safe_print("    当前无需要遗忘的知识")
        else:
            _safe_print("    自动遗忘已禁用")

        # 4. 检测老化
        _safe_print("\n[4/4] 检测知识老化...")
        aging = self.check_knowledge_aging()
        _safe_print(f"    老化知识数量: {aging.get('total_aging', 0)}")

        # 保存状态
        state = {
            'last_cycle': datetime.now().isoformat(),
            'current_round': current_round,
            'forgetting_count': forgetting.get('total_candidates', 0),
            'aging_count': aging.get('total_aging', 0),
            'inheritance_count': inherit_result.get('inherited_count', 0) if current_round > 1 else 0
        }
        self._save_state(state)

        _safe_print("\n知识管理周期完成!")
        _safe_print("=" * 60)

        return {
            'status': 'completed',
            'inheritance': inherit_result if current_round > 1 else {'inherited_count': 0},
            'forgetting': forgetting,
            'aging': aging,
            'state': state
        }

    def _save_state(self, state: Dict):
        """保存状态"""
        try:
            os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
            with open(self.state_path, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"保存状态失败: {e}")

    def update_config(self, key: str, value: Any) -> Dict:
        """更新配置"""
        self.config[key] = value
        self._save_config(self.config)
        return {'status': 'updated', 'key': key, 'value': value}


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description='智能进化知识深度传承与自适应遗忘引擎')
    parser.add_argument('command', nargs='?', default='status',
                        help='命令: status, cycle, forget, aging, inherit, evaluate, config')
    parser.add_argument('--knowledge-id', type=str, help='知识ID')
    parser.add_argument('--type', type=str, default='general', help='知识类型')
    parser.add_argument('--category', type=str, default='general', help='知识类别')
    parser.add_argument('--force', action='store_true', help='强制执行')
    parser.add_argument('--set', nargs=2, metavar=('KEY', 'VALUE'), help='设置配置项')

    args = parser.parse_args()

    engine = KnowledgeInheritanceForgettingEngine()

    if args.command == 'cycle' or args.command == 'run':
        # 运行完整周期
        result = engine.run_full_cycle(force=args.force)
        print("\n执行结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'forget':
        # 执行遗忘
        if args.knowledge_id:
            result = engine.execute_forgetting([args.knowledge_id])
        else:
            result = engine.execute_forgetting()
        print("\n遗忘结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'aging':
        # 检测老化
        result = engine.check_knowledge_aging()
        print("\n老化检测结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'inherit':
        # 执行传承
        current_round = engine.get_current_round()
        result = engine.inherit_knowledge(current_round - 1, current_round, args.category)
        print("\n传承结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'evaluate':
        # 评估知识价值
        if args.knowledge_id:
            result = engine.evaluate_knowledge_value(args.knowledge_id, args.type, args.category)
            print("\n价值评估结果:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("请指定 --knowledge-id")

    elif args.command == 'record':
        # 记录知识访问
        if args.knowledge_id:
            result = engine.record_knowledge_access(args.knowledge_id, args.type, args.category)
            print("\n记录结果:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("请指定 --knowledge-id")

    elif args.command == 'config':
        # 显示/修改配置
        if args.set:
            key, value = args.set
            if value.lower() in ['true', 'yes', '1']:
                value = True
            elif value.lower() in ['false', 'no', '0']:
                value = False
            elif value.isdigit():
                value = int(value)

            result = engine.update_config(key, value)
            print("\n配置更新结果:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            status = engine.get_knowledge_status()
            print("\n当前配置:")
            print(json.dumps(status.get('config', {}), ensure_ascii=False, indent=2))

    else:
        # 默认显示状态
        status = engine.get_knowledge_status()
        print("\n知识管理状态:")
        print(json.dumps(status, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()