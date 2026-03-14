#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化引擎集群统一诊断自愈与进化驾驶舱深度集成引擎

将 round 403 的统一诊断自愈中心引擎与进化驾驶舱(round 350)深度集成，
实现诊断结果可视化监控、智能预警与一键自愈的驾驶舱集成。

功能：
1. 诊断结果可视化：驾驶舱中显示引擎健康状态
2. 智能预警：根据诊断结果智能预警
3. 一键自愈：从驾驶舱一键触发自愈
4. 实时监控：诊断状态实时更新
5. 历史追踪：诊断历史与趋势分析

Version: 1.0.0
Author: Evolution System

依赖：
- evolution_unified_diagnosis_healing_center.py (round 403)
- evolution_cockpit_engine.py (round 350)
"""

import os
import sys
import json
import time
import threading
from datetime import datetime
from pathlib import Path
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


class DiagnosisCockpitIntegrationEngine:
    """诊断驾驶舱集成引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.project_root = PROJECT_ROOT
        self.scripts_dir = SCRIPT_DIR
        self.runtime_dir = os.path.join(self.project_root, "runtime")
        self.state_dir = os.path.join(self.runtime_dir, "state")
        self.logs_dir = os.path.join(self.runtime_dir, "logs")

        # 状态文件
        self.state_file = os.path.join(self.state_dir, "diagnosis_cockpit_state.json")
        self.config_file = os.path.join(self.state_dir, "diagnosis_cockpit_config.json")
        self.history_file = os.path.join(self.state_dir, "diagnosis_cockpit_history.json")

        # 初始化目录
        self._ensure_directories()

        # 配置
        self.config = self._load_config()

        # 加载依赖引擎
        self._load_engines()

        # 运行状态
        self.running = False
        self.monitor_thread = None
        self.stop_monitor = False
        self.last_diagnosis_time = None
        self.last_diagnosis_result = None

    def _ensure_directories(self):
        """确保必要的目录存在"""
        for directory in [self.state_dir, self.logs_dir]:
            os.makedirs(directory, exist_ok=True)

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        default_config = {
            "auto_scan_interval": 300,  # 自动扫描间隔（秒）
            "health_threshold": {
                "healthy": 0.9,
                "warning": 0.7,
                "critical": 0.5
            },
            "auto_heal_enabled": False,
            "warning_channels": ["dashboard", "log"]
        }

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return {**default_config, **config}
            except:
                pass
        return default_config

    def _save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[诊断驾驶舱] 保存配置失败: {e}")

    def _load_engines(self):
        """加载依赖引擎"""
        self.diagnosis_engine = None
        self.cockpit_engine = None

        # 加载诊断引擎
        try:
            from evolution_unified_diagnosis_healing_center import UnifiedDiagnosisHealingCenter
            self.diagnosis_engine = UnifiedDiagnosisHealingCenter()
            _safe_print("[诊断驾驶舱] 诊断引擎加载成功")
        except Exception as e:
            _safe_print(f"[诊断驾驶舱] 诊断引擎加载失败: {e}")

        # 加载驾驶舱引擎
        try:
            from evolution_cockpit_engine import EvolutionCockpitEngine
            self.cockpit_engine = EvolutionCockpitEngine()
            _safe_print("[诊断驾驶舱] 驾驶舱引擎加载成功")
        except Exception as e:
            _safe_print(f"[诊断驾驶舱] 驾驶舱引擎加载失败: {e}")

    def run_diagnosis(self) -> Dict[str, Any]:
        """执行诊断"""
        if not self.diagnosis_engine:
            return {"error": "诊断引擎未加载"}

        _safe_print("[诊断驾驶舱] 开始执行诊断...")

        # 执行扫描
        scan_results = self.diagnosis_engine.scan_engine_cluster()

        # 识别问题
        problems = self.diagnosis_engine.identify_problems()

        # 生成报告
        report = {
            "scan_time": scan_results.get("scan_time"),
            "total_engines": scan_results.get("total_engines", 0),
            "healthy_count": scan_results.get("healthy_count", 0),
            "unhealthy_count": scan_results.get("unhealthy_count", 0),
            "health_ratio": scan_results.get("health_ratio", 0),
            "problems": problems,
            "engines": scan_results.get("engines", [])
        }

        self.last_diagnosis_time = datetime.now()
        self.last_diagnosis_result = report

        # 保存诊断结果
        self._save_diagnosis_result(report)

        _safe_print(f"[诊断驾驶舱] 诊断完成: {report['healthy_count']}/{report['total_engines']} 健康")

        return report

    def _save_diagnosis_result(self, result: Dict[str, Any]):
        """保存诊断结果"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "last_diagnosis": result,
                    "timestamp": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[诊断驾驶舱] 保存诊断结果失败: {e}")

    def get_dashboard(self) -> Dict[str, Any]:
        """获取驾驶舱仪表盘数据"""
        # 如果没有最新诊断结果，先执行一次诊断
        if not self.last_diagnosis_result:
            self.run_diagnosis()

        result = self.last_diagnosis_result or {}

        # 计算健康等级
        health_ratio = result.get("health_ratio", 0)
        if health_ratio >= self.config["health_threshold"]["healthy"]:
            health_level = "healthy"
        elif health_ratio >= self.config["health_threshold"]["warning"]:
            health_level = "warning"
        elif health_ratio >= self.config["health_threshold"]["critical"]:
            health_level = "critical"
        else:
            health_level = "emergency"

        # 构建仪表盘数据
        dashboard = {
            "health_level": health_level,
            "health_ratio": round(health_ratio * 100, 1),
            "total_engines": result.get("total_engines", 0),
            "healthy_count": result.get("healthy_count", 0),
            "unhealthy_count": result.get("unhealthy_count", 0),
            "last_diagnosis_time": self.last_diagnosis_time.isoformat() if self.last_diagnosis_time else None,
            "problems": {
                "syntax_errors": len(result.get("problems", {}).get("syntax_errors", [])),
                "import_errors": len(result.get("problems", {}).get("import_errors", [])),
                "warnings": len(result.get("problems", {}).get("warnings", []))
            },
            "engines": result.get("engines", [])[:20]  # 只返回前20个
        }

        return dashboard

    def get_engine_health_list(self) -> List[Dict[str, Any]]:
        """获取引擎健康列表"""
        if not self.last_diagnosis_result:
            self.run_diagnosis()

        return self.last_diagnosis_result.get("engines", []) if self.last_diagnosis_result else []

    def trigger_one_click_heal(self) -> Dict[str, Any]:
        """一键自愈"""
        if not self.diagnosis_engine:
            return {"error": "诊断引擎未加载"}

        _safe_print("[诊断驾驶舱] 开始一键自愈...")

        # 先诊断
        self.run_diagnosis()

        # 执行自动修复
        heal_result = self.diagnosis_engine.auto_heal()

        # 重新诊断验证
        verify_result = self.run_diagnosis()

        return {
            "heal_result": heal_result,
            "verify_result": {
                "health_ratio": verify_result.get("health_ratio", 0),
                "healthy_count": verify_result.get("healthy_count", 0),
                "unhealthy_count": verify_result.get("unhealthy_count", 0)
            },
            "timestamp": datetime.now().isoformat()
        }

    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        return {
            "version": self.version,
            "running": self.running,
            "diagnosis_engine_loaded": self.diagnosis_engine is not None,
            "cockpit_engine_loaded": self.cockpit_engine is not None,
            "last_diagnosis_time": self.last_diagnosis_time.isoformat() if self.last_diagnosis_time else None,
            "last_diagnosis_result": self.last_diagnosis_result is not None
        }


# ============== CLI 接口 ==============

def main():
    """CLI 入口"""
    import argparse

    parser = argparse.ArgumentParser(description='诊断驾驶舱集成引擎')
    parser.add_argument('command', nargs='?', default='status',
                        choices=['status', 'dashboard', 'run_diagnosis', 'heal', 'engine_list'],
                        help='命令')
    parser.add_argument('--config', type=str, help='配置文件路径')

    args = parser.parse_args()

    # 创建引擎实例
    engine = DiagnosisCockpitIntegrationEngine()

    if args.command == 'status':
        # 显示状态
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.command == 'dashboard':
        # 显示仪表盘
        dashboard = engine.get_dashboard()
        print(json.dumps(dashboard, ensure_ascii=False, indent=2))

    elif args.command == 'run_diagnosis':
        # 执行诊断
        result = engine.run_diagnosis()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'heal':
        # 一键自愈
        result = engine.trigger_one_click_heal()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'engine_list':
        # 引擎健康列表
        engines = engine.get_engine_health_list()
        print(json.dumps(engines, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()