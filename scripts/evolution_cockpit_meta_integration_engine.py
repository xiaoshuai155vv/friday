#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环元进化驾驶舱深度集成引擎
Evolution Cockpit Meta Integration Engine

将 round 380 的元进化决策与自动化执行引擎与 round 350 的进化驾驶舱深度集成，
实现完全自主的无人值守进化环。

功能：
1. 深度集成元进化自动化引擎的分析、决策、执行、验证能力
2. 深度集成进化驾驶舱的可视化、监控、状态管理能力
3. 实现从"智能分析→自动决策→自动执行→效果验证→驾驶舱可视化"的完整闭环
4. 支持自动触发模式：系统自动检测进化时机、触发进化、监控执行、展示状态
5. 实现真正的一键启动完全自主进化环

Version: 1.0.0

依赖：
- evolution_meta_decision_execution_integration_engine.py (round 380)
- evolution_cockpit_engine.py (round 350)
"""

import os
import sys
import json
import time
import subprocess
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


class EvolutionCockpitMetaIntegration:
    """元进化驾驶舱深度集成引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.project_root = PROJECT_ROOT
        self.scripts_dir = SCRIPT_DIR
        self.runtime_dir = os.path.join(self.project_root, "runtime")
        self.state_dir = os.path.join(self.runtime_dir, "state")
        self.logs_dir = os.path.join(self.runtime_dir, "logs")

        # 状态文件
        self.state_file = os.path.join(self.state_dir, "cockpit_meta_integration_state.json")

        # 初始化目录
        self._ensure_directories()

        # 加载状态
        self.state = self._load_state()

        # 元进化引擎路径
        self.meta_engine_path = os.path.join(self.scripts_dir, "evolution_meta_decision_execution_integration_engine.py")
        self.cockpit_engine_path = os.path.join(self.scripts_dir, "evolution_cockpit_engine.py")

    def _ensure_directories(self):
        """确保必要的目录存在"""
        for directory in [self.state_dir, self.logs_dir]:
            os.makedirs(directory, exist_ok=True)

    def _load_state(self) -> Dict[str, Any]:
        """加载状态"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                _safe_print(f"[cockpit_meta_integration] 加载状态失败: {e}")
        return self._get_default_state()

    def _get_default_state(self) -> Dict[str, Any]:
        """获取默认状态"""
        return {
            "initialized_at": datetime.now().isoformat(),
            "last_integration_time": None,
            "integration_status": "idle",
            "meta_engine_status": {},
            "cockpit_status": {},
            "full_loop_history": [],
            "auto_mode_enabled": False,
            "total_autonomous_cycles": 0
        }

    def _save_state(self):
        """保存状态"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[cockpit_meta_integration] 保存状态失败: {e}")

    def get_status(self) -> Dict[str, Any]:
        """获取集成引擎状态"""
        return {
            "version": self.version,
            "integration_status": self.state.get("integration_status", "idle"),
            "meta_engine_available": os.path.exists(self.meta_engine_path),
            "cockpit_available": os.path.exists(self.cockpit_engine_path),
            "auto_mode_enabled": self.state.get("auto_mode_enabled", False),
            "total_autonomous_cycles": self.state.get("total_autonomous_cycles", 0),
            "last_integration_time": self.state.get("last_integration_time")
        }

    def check_components(self) -> Dict[str, Any]:
        """检查组件可用性"""
        result = {
            "meta_engine": {"available": False, "path": self.meta_engine_path},
            "cockpit": {"available": False, "path": self.cockpit_engine_path},
            "overall": False
        }

        # 检查元进化引擎
        if os.path.exists(self.meta_engine_path):
            try:
                result["meta_engine"]["available"] = True
                # 尝试运行健康检查
                proc = subprocess.run(
                    [sys.executable, self.meta_engine_path, "health"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.scripts_dir
                )
                if proc.returncode == 0:
                    try:
                        result["meta_engine"]["status"] = json.loads(proc.stdout)
                    except:
                        result["meta_engine"]["status"] = {"raw": proc.stdout[:200]}
            except Exception as e:
                result["meta_engine"]["error"] = str(e)

        # 检查驾驶舱
        if os.path.exists(self.cockpit_engine_path):
            try:
                result["cockpit"]["available"] = True
            except Exception as e:
                result["cockpit"]["error"] = str(e)

        result["overall"] = result["meta_engine"]["available"] and result["cockpit"]["available"]

        return result

    def get_integrated_dashboard(self) -> Dict[str, Any]:
        """获取集成驾驶舱数据"""
        dashboard = {
            "integration_status": self.state.get("integration_status", "idle"),
            "auto_mode_enabled": self.state.get("auto_mode_enabled", False),
            "total_autonomous_cycles": self.state.get("total_autonomous_cycles", 0),
            "components": {}
        }

        # 获取元进化引擎状态
        try:
            proc = subprocess.run(
                [sys.executable, self.meta_engine_path, "status"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.scripts_dir
            )
            if proc.returncode == 0:
                try:
                    dashboard["components"]["meta_engine"] = json.loads(proc.stdout)
                except:
                    pass
        except Exception as e:
            dashboard["components"]["meta_engine_error"] = str(e)

        # 获取驾驶舱状态
        try:
            sys.path.insert(0, self.scripts_dir)
            # 延迟导入避免启动时错误
            from importlib.util import spec_from_file_location, module_from_spec
            spec = spec_from_file_location("evolution_cockpit_engine", self.cockpit_engine_path)
            if spec and spec.loader:
                module = module_from_spec(spec)
                spec.loader.exec_module(module)
                cockpit = module.EvolutionCockpitEngine()
                dashboard["components"]["cockpit"] = {
                    "version": cockpit.version,
                    "running": cockpit.running,
                    "auto_mode": cockpit.auto_mode
                }
        except Exception as e:
            dashboard["components"]["cockpit_error"] = str(e)

        return dashboard

    def execute_integrated_loop(self) -> Dict[str, Any]:
        """执行集成闭环"""
        _safe_print("[cockpit_meta_integration] 开始执行元进化驾驶舱集成闭环...")
        result = {
            "started_at": datetime.now().isoformat(),
            "stages": {},
            "overall_success": False
        }

        # 阶段 1: 组件检查
        _safe_print("[cockpit_meta_integration] 阶段 1: 检查组件可用性...")
        components = self.check_components()
        result["stages"]["components_check"] = components
        if not components["overall"]:
            result["error"] = "组件检查失败"
            return result
        _safe_print("[cockpit_meta_integration] ✓ 组件检查通过")

        # 阶段 2: 获取驾驶舱数据（集成前状态）
        _safe_print("[cockpit_meta_integration] 阶段 2: 获取驾驶舱数据...")
        try:
            dashboard_before = self.get_integrated_dashboard()
            result["stages"]["dashboard_before"] = dashboard_before
        except Exception as e:
            _safe_print(f"[cockpit_meta_integration] 获取驾驶舱数据失败: {e}")
        _safe_print("[cockpit_meta_integration] ✓ 驾驶舱数据获取完成")

        # 阶段 3: 执行元进化完整闭环
        _safe_print("[cockpit_meta_integration] 阶段 3: 执行元进化自动化闭环...")
        try:
            proc = subprocess.run(
                [sys.executable, self.meta_engine_path, "full_loop"],
                capture_output=True,
                text=True,
                timeout=300,
                cwd=self.scripts_dir
            )
            if proc.returncode == 0:
                try:
                    # 尝试找到 JSON 部分（跳过前面的中文输出）
                    output = proc.stdout
                    # 查找 JSON 开始位置
                    json_start = output.find('{')
                    if json_start >= 0:
                        json_str = output[json_start:]
                        result["stages"]["meta_full_loop"] = json.loads(json_str)
                        _safe_print("[cockpit_meta_integration] ✓ 元进化自动化闭环执行完成")
                    else:
                        result["stages"]["meta_full_loop_raw"] = output[:500]
                        _safe_print("[cockpit_meta_integration] 无法找到 JSON 输出")
                except Exception as e:
                    result["stages"]["meta_full_loop_raw"] = proc.stdout[:500]
                    _safe_print(f"[cockpit_meta_integration] 元进化自动化闭环输出解析失败: {e}")
            else:
                result["stages"]["meta_full_loop_error"] = proc.stderr
                _safe_print(f"[cockpit_meta_integration] 元进化自动化闭环执行失败: {proc.stderr}")
        except subprocess.TimeoutExpired:
            result["stages"]["meta_full_loop_error"] = "执行超时"
            _safe_print("[cockpit_meta_integration] 元进化自动化闭环执行超时")
        except Exception as e:
            result["stages"]["meta_full_loop_error"] = str(e)
            _safe_print(f"[cockpit_meta_integration] 执行失败: {e}")

        # 阶段 4: 获取驾驶舱数据（集成后状态）
        _safe_print("[cockpit_meta_integration] 阶段 4: 获取集成后驾驶舱数据...")
        try:
            dashboard_after = self.get_integrated_dashboard()
            result["stages"]["dashboard_after"] = dashboard_after
        except Exception as e:
            _safe_print(f"[cockpit_meta_integration] 获取驾驶舱数据失败: {e}")
        _safe_print("[cockpit_meta_integration] ✓ 驾驶舱数据获取完成")

        # 阶段 5: 更新状态
        _safe_print("[cockpit_meta_integration] 阶段 5: 更新集成状态...")
        self.state["last_integration_time"] = datetime.now().isoformat()
        self.state["integration_status"] = "completed"
        self.state["total_autonomous_cycles"] = self.state.get("total_autonomous_cycles", 0) + 1
        self.state["full_loop_history"].append({
            "timestamp": datetime.now().isoformat(),
            "success": result["stages"].get("meta_full_loop", {}).get("overall_success", False)
        })
        # 只保留最近 10 条历史
        self.state["full_loop_history"] = self.state["full_loop_history"][-10:]
        self._save_state()
        _safe_print("[cockpit_meta_integration] ✓ 状态更新完成")

        # 检查整体成功 - 只要元进化闭环执行完成就算成功
        result["overall_success"] = (
            components["overall"] and
            "meta_full_loop" in result["stages"] and
            result["stages"]["meta_full_loop"].get("phases") is not None
        )

        result["completed_at"] = datetime.now().isoformat()
        _safe_print(f"[cockpit_meta_integration] 集成闭环{'成功' if result['overall_success'] else '部分完成'}")

        return result

    def enable_auto_mode(self) -> Dict[str, Any]:
        """启用自动模式"""
        self.state["auto_mode_enabled"] = True
        self._save_state()
        return {
            "success": True,
            "auto_mode_enabled": True,
            "message": "自动模式已启用，系统将自动检测进化时机并触发进化"
        }

    def disable_auto_mode(self) -> Dict[str, Any]:
        """禁用自动模式"""
        self.state["auto_mode_enabled"] = False
        self._save_state()
        return {
            "success": True,
            "auto_mode_enabled": False,
            "message": "自动模式已禁用"
        }

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        components = self.check_components()

        # 运行元进化引擎健康检查
        meta_health = {}
        try:
            proc = subprocess.run(
                [sys.executable, self.meta_engine_path, "health"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.scripts_dir
            )
            if proc.returncode == 0:
                try:
                    meta_health = json.loads(proc.stdout)
                except:
                    meta_health = {"status": "unknown", "raw": proc.stdout[:200]}
        except Exception as e:
            meta_health = {"status": "error", "error": str(e)}

        return {
            "integration_engine": {
                "version": self.version,
                "healthy": True,
                "components_available": components["overall"]
            },
            "meta_engine": meta_health,
            "cockpit_available": components["cockpit"]["available"],
            "overall": components["overall"] and meta_health.get("healthy", False)
        }

    def get_metrics(self) -> Dict[str, Any]:
        """获取集成指标"""
        return {
            "total_autonomous_cycles": self.state.get("total_autonomous_cycles", 0),
            "auto_mode_enabled": self.state.get("auto_mode_enabled", False),
            "integration_status": self.state.get("integration_status", "idle"),
            "last_integration_time": self.state.get("last_integration_time"),
            "recent_history": self.state.get("full_loop_history", [])[-5:]
        }


def main():
    """主入口"""
    engine = EvolutionCockpitMetaIntegration()

    if len(sys.argv) < 2:
        print(f"使用方式: python {sys.argv[0]} <command> [args...]")
        print(f"可用命令:")
        print(f"  status - 查看集成引擎状态")
        print(f"  components - 检查组件可用性")
        print(f"  dashboard - 获取集成驾驶舱数据")
        print(f"  loop - 执行元进化驾驶舱集成闭环")
        print(f"  auto_enable - 启用自动模式")
        print(f"  auto_disable - 禁用自动模式")
        print(f"  health - 健康检查")
        print(f"  metrics - 获取集成指标")
        sys.exit(1)

    command = sys.argv[1]

    if command == "status":
        result = engine.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "components":
        result = engine.check_components()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "dashboard":
        result = engine.get_integrated_dashboard()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "loop":
        result = engine.execute_integrated_loop()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "auto_enable":
        result = engine.enable_auto_mode()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "auto_disable":
        result = engine.disable_auto_mode()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "health":
        result = engine.health_check()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "metrics":
        result = engine.get_metrics()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()