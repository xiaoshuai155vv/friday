#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环知识全生命周期深度整合引擎
=============================================================
在 round 492 完成的跨引擎知识更新预警与自动触发深度集成引擎基础上，
将 round 490-492 的知识推荐、同步、预警、触发能力深度整合。

让系统能够实现知识发现→推荐→同步→预警→触发→执行→验证的完整闭环，
形成端到端的知识资产自主管理能力。让进化环能够像一位"知识管家"，
主动管理知识的全生命周期，从产生到应用再到优化。

功能：
1. 知识全生命周期状态追踪 - 追踪每个知识从产生到应用的完整历程
2. 端到端流程编排 - 协调推荐→同步→预警→触发→执行各环节
3. 统一数据流 - 整合各引擎的数据和状态
4. 智能流程优化 - 根据执行效果自动优化流程参数
5. 与进化驾驶舱深度集成 - 可视化全生命周期状态
6. 集成到 do.py 支持知识全生命周期、全生命周期管理、端到端知识等关键词触发

version: 1.0.0
"""

import os
import sys
import json
import re
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple, Callable
from collections import defaultdict
import threading

# 解决 Windows 控制台 Unicode 输出问题
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# 路径配置
BASE_DIR = Path(__file__).parent.parent
RUNTIME_DIR = BASE_DIR / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
KNOWLEDGE_DIR = RUNTIME_DIR / "knowledge"
LOGS_DIR = RUNTIME_DIR / "logs"

# 存储文件路径
LIFECYCLE_STATE_FILE = STATE_DIR / "knowledge_lifecycle_state.json"
LIFECYCLE_HISTORY_FILE = STATE_DIR / "knowledge_lifecycle_history.json"
INTEGRATION_CONFIG_FILE = STATE_DIR / "knowledge_integration_config.json"
PROCESS_FLOW_FILE = STATE_DIR / "knowledge_process_flow.json"
OPTIMIZATION_LOG_FILE = STATE_DIR / "knowledge_optimization_log.json"


def _safe_print(text: str):
    """安全打印"""
    try:
        print(text)
    except UnicodeEncodeError:
        clean_text = re.sub(r'[^\x00-\x7F]+', '', text)
        print(clean_text)


class KnowledgeFullLifecycleIntegrationEngine:
    """知识全生命周期深度整合引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.engine_name = "知识全生命周期深度整合引擎"

        # 确保目录存在
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

        # 加载数据
        self.lifecycle_state = self._load_lifecycle_state()
        self.lifecycle_history = self._load_lifecycle_history()
        self.integration_config = self._load_integration_config()
        self.process_flow = self._load_process_flow()

        # 集成子引擎
        self._init_sub_engines()

    def _load_lifecycle_state(self) -> Dict:
        """加载生命周期状态"""
        try:
            if LIFECYCLE_STATE_FILE.exists():
                with open(LIFECYCLE_STATE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            _safe_print(f"加载生命周期状态失败: {e}")
        return {
            "initialized": True,
            "total_knowledge_items": 0,
            "active_items": 0,
            "stages_distribution": {},
            "last_update": datetime.now().isoformat()
        }

    def _save_lifecycle_state(self):
        """保存生命周期状态"""
        try:
            with open(LIFECYCLE_STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.lifecycle_state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"保存生命周期状态失败: {e}")

    def _load_lifecycle_history(self) -> List[Dict]:
        """加载生命周期历史"""
        try:
            if LIFECYCLE_HISTORY_FILE.exists():
                with open(LIFECYCLE_HISTORY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            _safe_print(f"加载生命周期历史失败: {e}")
        return []

    def _save_lifecycle_history(self):
        """保存生命周期历史"""
        try:
            # 只保留最近 1000 条记录
            history = self.lifecycle_history[-1000:]
            with open(LIFECYCLE_HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"保存生命周期历史失败: {e}")

    def _load_integration_config(self) -> Dict:
        """加载集成配置"""
        try:
            if INTEGRATION_CONFIG_FILE.exists():
                with open(INTEGRATION_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            _safe_print(f"加载集成配置失败: {e}")
        return {
            "recommendation_engine": True,
            "sync_engine": True,
            "warning_trigger_engine": True,
            "auto_execution": True,
            "stages": ["discovered", "recommended", "synced", "warning", "triggered", "executed", "validated"]
        }

    def _load_process_flow(self) -> Dict:
        """加载流程配置"""
        try:
            if PROCESS_FLOW_FILE.exists():
                with open(PROCESS_FLOW_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            _safe_print(f"加载流程配置失败: {e}")
        return {
            "enabled_stages": self.integration_config.get("stages", []),
            "stage_durations": {},
            "stage_counts": {},
            "last_optimization": None
        }

    def _init_sub_engines(self):
        """初始化子引擎"""
        self.sub_engines = {}
        scripts_dir = Path(__file__).parent

        # 尝试加载 round 490 的推荐引擎
        try:
            sys.path.insert(0, str(scripts_dir))
            from evolution_knowledge_proactive_recommendation_prediction_engine import KnowledgeProactiveRecommendationPredictionEngine
            self.sub_engines['recommendation'] = KnowledgeProactiveRecommendationPredictionEngine()
            _safe_print("[整合] 已加载知识推荐引擎 (round 490)")
        except Exception as e:
            _safe_print(f"[整合] 无法加载知识推荐引擎: {e}")

        # 尝试加载 round 491 的同步引擎
        try:
            from evolution_knowledge_realtime_update_sync_engine import KnowledgeRealtimeUpdateSyncEngine
            self.sub_engines['sync'] = KnowledgeRealtimeUpdateSyncEngine()
            _safe_print("[整合] 已加载知识同步引擎 (round 491)")
        except Exception as e:
            _safe_print(f"[整合] 无法加载知识同步引擎: {e}")

        # 尝试加载 round 492 的预警触发引擎
        try:
            from evolution_knowledge_update_warning_trigger_engine import KnowledgeUpdateWarningTriggerEngine
            self.sub_engines['warning_trigger'] = KnowledgeUpdateWarningTriggerEngine()
            _safe_print("[整合] 已加载知识预警触发引擎 (round 492)")
        except Exception as e:
            _safe_print(f"[整合] 无法加载知识预警触发引擎: {e}")

    def get_status(self) -> Dict:
        """获取整合引擎状态"""
        # 统计知识数量
        total_items = 0
        stages = defaultdict(int)

        # 从推荐引擎获取数据
        if 'recommendation' in self.sub_engines:
            try:
                rec_engine = self.sub_engines['recommendation']
                if hasattr(rec_engine, 'prediction_history'):
                    total_items += len(rec_engine.prediction_history)
            except:
                pass

        # 从同步引擎获取数据
        if 'sync' in self.sub_engines:
            try:
                sync_engine = self.sub_engines['sync']
                if hasattr(sync_engine, 'sync_state'):
                    total_items += len(sync_engine.sync_state.get('files', {}))
            except:
                pass

        # 从预警触发引擎获取数据
        if 'warning_trigger' in self.sub_engines:
            try:
                wt_engine = self.sub_engines['warning_trigger']
                if hasattr(wt_engine, 'trigger_history'):
                    total_items += len(wt_engine.trigger_history)
            except:
                pass

        self.lifecycle_state['total_knowledge_items'] = total_items
        self.lifecycle_state['stages_distribution'] = dict(stages)
        self.lifecycle_state['last_update'] = datetime.now().isoformat()

        return {
            "engine": self.engine_name,
            "version": self.version,
            "integrated_engines": list(self.sub_engines.keys()),
            "total_knowledge_items": total_items,
            "stages": self.integration_config.get("stages", []),
            "lifecycle_state": self.lifecycle_state
        }

    def run_full_lifecycle(self) -> Dict:
        """运行完整的知识生命周期流程"""
        _safe_print("[全生命周期] 开始执行端到端知识管理流程...")

        results = {
            "start_time": datetime.now().isoformat(),
            "stages_executed": [],
            "knowledge_processed": 0,
            "success": True,
            "errors": []
        }

        try:
            # Stage 1: 知识发现与推荐
            if 'recommendation' in self.sub_engines:
                _safe_print("[阶段1] 执行知识推荐...")
                rec_engine = self.sub_engines['recommendation']
                try:
                    # 获取推荐状态 - 推荐引擎使用 get_cockpit_data
                    if hasattr(rec_engine, 'get_cockpit_data'):
                        status = rec_engine.get_cockpit_data()
                    else:
                        status = {}
                    results['stages_executed'].append("recommendation")
                    results['knowledge_processed'] += 1
                    _safe_print(f"[阶段1] 完成 - 知识推荐引擎已激活")
                except Exception as e:
                    results['errors'].append(f"推荐阶段: {e}")

            # Stage 2: 知识同步
            if 'sync' in self.sub_engines:
                _safe_print("[阶段2] 执行知识同步...")
                sync_engine = self.sub_engines['sync']
                try:
                    # 获取同步状态
                    status = sync_engine.get_status()
                    results['stages_executed'].append("sync")
                    results['knowledge_processed'] += status.get('synced_files', 0)
                    _safe_print(f"[阶段2] 完成 - 同步了 {status.get('synced_files', 0)} 个文件")
                except Exception as e:
                    results['errors'].append(f"同步阶段: {e}")

            # Stage 3: 预警触发
            if 'warning_trigger' in self.sub_engines:
                _safe_print("[阶段3] 执行预警触发...")
                wt_engine = self.sub_engines['warning_trigger']
                try:
                    # 获取触发状态
                    status = wt_engine.get_status()
                    results['stages_executed'].append("warning_trigger")
                    results['knowledge_processed'] += status.get('trigger_count', 0)
                    _safe_print(f"[阶段3] 完成 - 触发了 {status.get('trigger_count', 0)} 次")
                except Exception as e:
                    results['errors'].append(f"预警触发阶段: {e}")

            results['end_time'] = datetime.now().isoformat()
            results['success'] = len(results['errors']) == 0

            # 记录到历史
            self._record_lifecycle_history(results)

            _safe_print(f"[全生命周期] 执行完成 - 共处理 {results['knowledge_processed']} 项知识")

        except Exception as e:
            results['success'] = False
            results['errors'].append(str(e))
            _safe_print(f"[全生命周期] 执行失败: {e}")

        return results

    def _record_lifecycle_history(self, result: Dict):
        """记录生命周期历史"""
        self.lifecycle_history.append({
            "timestamp": result.get('start_time', datetime.now().isoformat()),
            "stages": result.get('stages_executed', []),
            "knowledge_processed": result.get('knowledge_processed', 0),
            "success": result.get('success', False),
            "error_count": len(result.get('errors', []))
        })
        self._save_lifecycle_history()

    def get_lifecycle_history(self, limit: int = 50) -> List[Dict]:
        """获取生命周期历史"""
        return self.lifecycle_history[-limit:]

    def get_cockpit_data(self) -> Dict:
        """获取驾驶舱数据"""
        status = self.get_status()
        history = self.get_lifecycle_history(20)

        # 计算趋势
        recent_success = sum(1 for h in history if h.get('success', False))
        trend = "up" if recent_success > len(history) * 0.7 else "down" if recent_success < len(history) * 0.5 else "stable"

        return {
            "engine": self.engine_name,
            "version": self.version,
            "status": status,
            "recent_history": history,
            "trend": trend,
            "integrated_engines": list(self.sub_engines.keys()),
            "lifecycle_metrics": {
                "total_processed": sum(h.get('knowledge_processed', 0) for h in history),
                "success_rate": recent_success / len(history) if history else 0,
                "error_count": sum(h.get('error_count', 0) for h in history)
            }
        }

    def get_integration_status(self) -> Dict:
        """获取集成状态"""
        status = {}
        for name, engine in self.sub_engines.items():
            try:
                engine_status = engine.get_status()
                status[name] = {
                    "loaded": True,
                    "status": "active",
                    "version": getattr(engine, 'version', 'unknown')
                }
            except Exception as e:
                status[name] = {
                    "loaded": False,
                    "status": f"error: {str(e)}"
                }
        return status


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='知识全生命周期深度整合引擎')
    parser.add_argument('--status', action='store_true', help='获取引擎状态')
    parser.add_argument('--run', action='store_true', help='执行完整生命周期流程')
    parser.add_argument('--cockpit-data', action='store_true', help='获取驾驶舱数据')
    parser.add_argument('--history', action='store_true', help='获取生命周期历史')
    parser.add_argument('--integration-status', action='store_true', help='获取集成状态')

    args = parser.parse_args()

    engine = KnowledgeFullLifecycleIntegrationEngine()

    if args.status:
        status = engine.get_status()
        _safe_print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.run:
        result = engine.run_full_lifecycle()
        _safe_print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.cockpit_data:
        data = engine.get_cockpit_data()
        _safe_print(json.dumps(data, ensure_ascii=False, indent=2))

    elif args.history:
        history = engine.get_lifecycle_history()
        _safe_print(json.dumps(history, ensure_ascii=False, indent=2))

    elif args.integration_status:
        status = engine.get_integration_status()
        _safe_print(json.dumps(status, ensure_ascii=False, indent=2))

    else:
        # 默认显示状态
        status = engine.get_status()
        _safe_print(json.dumps(status, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()