#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环知识蒸馏与进化驾驶舱可视化集成引擎
Evolution Distillation Cockpit Integration Engine

将 round 433 创建的知识蒸馏引擎与进化驾驶舱（round 350）深度集成，
实现蒸馏过程和智慧库的可视化展示、实时数据推送、动态指标刷新。

功能：
1. 蒸馏过程实时可视化（数据收集、模式提取、知识固化进度）
2. 智慧库内容可视化（知识条目、成功模式、优化建议）
3. 实时数据推送与动态指标刷新
4. 与进化驾驶舱深度集成

Version: 1.0.0

依赖：
- evolution_knowledge_distillation_engine.py (round 433)
- evolution_cockpit_engine.py (round 350)
"""

import os
import sys
import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict

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


class EvolutionDistillationCockpitIntegrationEngine:
    """知识蒸馏与进化驾驶舱可视化集成引擎"""

    def __init__(self, base_path: str = None):
        self.version = "1.0.0"
        self.base_path = base_path or PROJECT_ROOT
        self.scripts_dir = SCRIPT_DIR
        self.runtime_dir = os.path.join(self.base_path, "runtime")
        self.state_dir = os.path.join(self.runtime_dir, "state")
        self.logs_dir = os.path.join(self.runtime_dir, "logs")

        # 状态文件
        self.state_file = os.path.join(self.state_dir, "distillation_cockpit_state.json")
        self.visual_data_file = os.path.join(self.state_dir, "distillation_cockpit_visual_data.json")

        # 初始化目录
        self._ensure_directories()

        # 加载知识蒸馏引擎
        self.distillation_engine = self._load_distillation_engine()

        # 加载进化驾驶舱
        self.cockpit_engine = self._load_cockpit_engine()

        # 可视化数据
        self.visual_data = self._load_visual_data()

        # 配置
        self.config = {
            'refresh_interval': 5,  # 秒
            'max_visual_history': 50,
            'enable_realtime_push': True,
            'metrics_to_show': [
                'total_patterns',
                'wisdom_count',
                'optimization_count',
                'distillation_progress',
                'engine_coverage'
            ]
        }

        # 更新历史记录
        self._update_visual_data()

    def _ensure_directories(self):
        """确保必要的目录存在"""
        for directory in [self.state_dir, self.logs_dir]:
            os.makedirs(directory, exist_ok=True)

    def _load_distillation_engine(self):
        """加载知识蒸馏引擎"""
        try:
            from evolution_knowledge_distillation_engine import EvolutionKnowledgeDistillationEngine
            return EvolutionKnowledgeDistillationEngine(self.base_path)
        except Exception as e:
            _safe_print(f"[DistillationCockpit] 加载知识蒸馏引擎失败: {e}")
            return None

    def _load_cockpit_engine(self):
        """加载进化驾驶舱"""
        try:
            from evolution_cockpit_engine import EvolutionCockpitEngine
            return EvolutionCockpitEngine()
        except Exception as e:
            _safe_print(f"[DistillationCockpit] 加载进化驾驶舱失败: {e}")
            return None

    def _load_visual_data(self):
        """加载可视化数据"""
        if os.path.exists(self.visual_data_file):
            try:
                with open(self.visual_data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            'last_update': None,
            'distillation_summary': {},
            'wisdom_library': {},
            'success_patterns': [],
            'optimization_suggestions': [],
            'realtime_metrics': {},
            'history': []
        }

    def _save_visual_data(self):
        """保存可视化数据"""
        try:
            with open(self.visual_data_file, 'w', encoding='utf-8') as f:
                json.dump(self.visual_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[DistillationCockpit] 保存可视化数据失败: {e}")

    def _update_visual_data(self):
        """更新可视化数据"""
        if not self.distillation_engine:
            return

        # 获取蒸馏摘要
        distillation_summary = {
            'total_engines_analyzed': len(self.distillation_engine.engine_history),
            'total_patterns_extracted': len(self.distillation_engine.success_patterns),
            'wisdom_entries': len(self.distillation_engine.wisdom_library),
            'optimization_decisions': len(self.distillation_engine.optimization_decisions),
            'last_distillation_time': getattr(self.distillation_engine, 'last_distillation_time', None)
        }

        # 获取智慧库摘要
        wisdom_summary = {}
        for engine_name, wisdom in self.distillation_engine.wisdom_library.items():
            wisdom_summary[engine_name] = {
                'entry_count': len(wisdom.get('patterns', [])),
                'last_updated': wisdom.get('last_updated'),
                'success_rate': wisdom.get('success_rate', 0)
            }

        # 获取成功模式
        success_patterns = []
        for pattern_id, pattern in self.distillation_engine.success_patterns.items():
            success_patterns.append({
                'id': pattern_id,
                'type': pattern.get('type'),
                'frequency': pattern.get('frequency', 0),
                'success_rate': pattern.get('success_rate', 0),
                'description': pattern.get('description', '')[:100]
            })
        # 按频率排序，取前10
        success_patterns = sorted(success_patterns, key=lambda x: x['frequency'], reverse=True)[:10]

        # 获取优化建议
        optimization_suggestions = []
        for decision in self.distillation_engine.optimization_decisions[-10:]:
            optimization_suggestions.append({
                'id': decision.get('id'),
                'timestamp': decision.get('timestamp'),
                'type': decision.get('type'),
                'recommendation': decision.get('recommendation', '')[:150],
                'status': decision.get('status', 'pending')
            })

        # 计算蒸馏进度
        total_engines = len(self.distillation_engine.engine_history)
        processed_engines = len(self.distillation_engine.wisdom_library)
        distillation_progress = (processed_engines / total_engines * 100) if total_engines > 0 else 0

        # 实时指标
        realtime_metrics = {
            'distillation_progress': round(distillation_progress, 1),
            'engine_coverage': f"{processed_engines}/{total_engines}",
            'pattern_extraction_rate': len(self.distillation_engine.success_patterns) / max(total_engines, 1),
            'wisdom_density': len(self.distillation_engine.wisdom_library) / max(len(self.distillation_engine.success_patterns), 1)
        }

        # 更新可视化数据
        self.visual_data = {
            'last_update': datetime.now().isoformat(),
            'distillation_summary': distillation_summary,
            'wisdom_library': wisdom_summary,
            'success_patterns': success_patterns,
            'optimization_suggestions': optimization_suggestions,
            'realtime_metrics': realtime_metrics,
            'history': self.visual_data.get('history', [])
        }

        # 添加到历史记录
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'distillation_summary': distillation_summary,
            'realtime_metrics': realtime_metrics
        }
        self.visual_data['history'].append(history_entry)

        # 保持历史记录数量
        if len(self.visual_data['history']) > self.config['max_visual_history']:
            self.visual_data['history'] = self.visual_data['history'][-self.config['max_visual_history']:]

        self._save_visual_data()

    def get_status(self) -> Dict[str, Any]:
        """获取集成引擎状态"""
        status = {
            'version': self.version,
            'distillation_engine_loaded': self.distillation_engine is not None,
            'cockpit_engine_loaded': self.cockpit_engine is not None,
            'last_update': self.visual_data.get('last_update'),
            'total_engines': self.visual_data.get('distillation_summary', {}).get('total_engines_analyzed', 0),
            'total_patterns': self.visual_data.get('distillation_summary', {}).get('total_patterns_extracted', 0),
            'wisdom_entries': self.visual_data.get('distillation_summary', {}).get('wisdom_entries', 0),
            'distillation_progress': self.visual_data.get('realtime_metrics', {}).get('distillation_progress', 0)
        }
        return status

    def get_distillation_visualization(self) -> Dict[str, Any]:
        """获取蒸馏过程可视化数据"""
        return {
            'summary': self.visual_data.get('distillation_summary', {}),
            'realtime_metrics': self.visual_data.get('realtime_metrics', {}),
            'progress': {
                'bar': self.visual_data.get('realtime_metrics', {}).get('distillation_progress', 0),
                'label': f"蒸馏进度: {self.visual_data.get('realtime_metrics', {}).get('distillation_progress', 0):.1f}%"
            }
        }

    def get_wisdom_library_visualization(self) -> Dict[str, Any]:
        """获取智慧库可视化数据"""
        return {
            'summary': self.visual_data.get('wisdom_library', {}),
            'top_patterns': self.visual_data.get('success_patterns', [])[:5],
            'total_entries': self.visual_data.get('distillation_summary', {}).get('wisdom_entries', 0)
        }

    def get_optimization_visualization(self) -> Dict[str, Any]:
        """获取优化建议可视化数据"""
        return {
            'suggestions': self.visual_data.get('optimization_suggestions', []),
            'total_decisions': self.visual_data.get('distillation_summary', {}).get('optimization_decisions', 0)
        }

    def refresh(self) -> Dict[str, Any]:
        """刷新可视化数据"""
        self._update_visual_data()
        return {
            'status': 'success',
            'timestamp': self.visual_data.get('last_update'),
            'metrics': self.visual_data.get('realtime_metrics', {})
        }

    def push_to_cockpit(self) -> Dict[str, Any]:
        """推送数据到进化驾驶舱"""
        if not self.cockpit_engine:
            return {'status': 'error', 'message': '驾驶舱未加载'}

        try:
            # 更新驾驶舱的蒸馏相关数据
            self._update_visual_data()

            # 构建推送到驾驶舱的数据
            cockpit_data = {
                'type': 'distillation_integration',
                'timestamp': datetime.now().isoformat(),
                'data': {
                    'distillation_progress': self.visual_data.get('realtime_metrics', {}).get('distillation_progress', 0),
                    'total_patterns': self.visual_data.get('distillation_summary', {}).get('total_patterns_extracted', 0),
                    'wisdom_entries': self.visual_data.get('distillation_summary', {}).get('wisdom_entries', 0),
                    'engine_coverage': self.visual_data.get('realtime_metrics', {}).get('engine_coverage', '0/0')
                }
            }

            # 保存到驾驶舱数据文件
            cockpit_data_file = os.path.join(self.state_dir, 'distillation_cockpit_push.json')
            with open(cockpit_data_file, 'w', encoding='utf-8') as f:
                json.dump(cockpit_data, f, ensure_ascii=False, indent=2)

            return {'status': 'success', 'data': cockpit_data['data']}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def initialize(self) -> Dict[str, Any]:
        """初始化集成引擎"""
        result = {
            'status': 'success',
            'version': self.version,
            'message': '知识蒸馏与驾驶舱集成引擎初始化完成'
        }

        # 检查依赖引擎
        if not self.distillation_engine:
            result['warnings'] = result.get('warnings', [])
            result['warnings'].append('知识蒸馏引擎未加载')
            result['status'] = 'partial'

        if not self.cockpit_engine:
            result['warnings'] = result.get('warnings', [])
            result['warnings'].append('进化驾驶舱未加载')
            result['status'] = 'partial'

        # 初始化时刷新数据
        self._update_visual_data()

        return result


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='知识蒸馏与进化驾驶舱可视化集成引擎')
    parser.add_argument('command', choices=['status', 'visualization', 'wisdom', 'optimization', 'refresh', 'push', 'initialize'],
                        help='执行命令')
    parser.add_argument('--format', choices=['json', 'text'], default='text', help='输出格式')

    args = parser.parse_args()

    engine = EvolutionDistillationCockpitIntegrationEngine()

    if args.command == 'status':
        result = engine.get_status()
    elif args.command == 'visualization':
        result = engine.get_distillation_visualization()
    elif args.command == 'wisdom':
        result = engine.get_wisdom_library_visualization()
    elif args.command == 'optimization':
        result = engine.get_optimization_visualization()
    elif args.command == 'refresh':
        result = engine.refresh()
    elif args.command == 'push':
        result = engine.push_to_cockpit()
    elif args.command == 'initialize':
        result = engine.initialize()
    else:
        result = {'error': '未知命令'}

    if args.format == 'json':
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        _safe_print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()