#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环统一智能体协同引擎与进化驾驶舱深度集成引擎 (version 1.0.0)

将 round 377 的统一智能体协同引擎与进化驾驶舱(round 350)深度集成，实现：
1. 跨引擎协同状态的可视化监控
2. 实时进度追踪
3. 智能调度控制
4. 统一状态共享
5. 双向数据流通

核心功能：
1. 驾驶舱集成 - 统一智能体引擎状态在驾驶舱中可视化
2. 任务分发 - 驾驶舱可直接触发智能体分析任务
3. 状态同步 - 引擎状态实时同步到驾驶舱
4. 协同监控 - 跨引擎执行过程全程监控

依赖：
- evolution_cockpit_engine.py (round 350)
- unified_evolution_agent_engine.py (round 377)
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
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


class EvolutionAgentCockpitIntegrationEngine:
    """统一智能体协同引擎与进化驾驶舱深度集成引擎"""

    def __init__(self, state_dir: str = "runtime/state"):
        self.state_dir = Path(state_dir)
        self.project_root = self.state_dir.parent.parent
        self.scripts_dir = self.project_root / "scripts"

        self.version = "1.0.0"

        # 状态文件
        self.state_file = self.state_dir / "agent_cockpit_integration_state.json"
        self.collaboration_file = self.state_dir / "agent_cockpit_collaboration.json"

        # 初始化状态
        self.state = {
            "version": self.version,
            "initialized": False,
            "integration_status": "initializing",
            "cockpit_connected": False,
            "agent_connected": False,
            "active_collaborations": [],
            "total_collaborations": 0,
            "successful_collaborations": 0,
            "failed_collaborations": 0,
            "last_sync_time": None,
        }

        # 初始化子引擎引用
        self.cockpit_engine = None
        self.agent_engine = None

        self._initialize()

    def _initialize(self):
        """初始化集成引擎"""
        _safe_print("[Agent-Cockpit Integration] 正在初始化深度集成引擎...")

        # 尝试加载进化驾驶舱
        self._load_cockpit()

        # 尝试加载统一智能体引擎
        self._load_agent_engine()

        self.state["initialized"] = True
        self.state["integration_status"] = "ready"

        # 保存状态
        self._save_state()

        _safe_print("[Agent-Cockpit Integration] 初始化完成")
        _safe_print(f"  驾驶舱连接: {'已连接' if self.state['cockpit_connected'] else '未连接'}")
        _safe_print(f"  智能体连接: {'已连接' if self.state['agent_connected'] else '未连接'}")

    def _load_cockpit(self):
        """加载进化驾驶舱"""
        try:
            from evolution_cockpit_engine import EvolutionCockpitEngine
            self.cockpit_engine = EvolutionCockpitEngine()
            self.state["cockpit_connected"] = True
            _safe_print("[Agent-Cockpit Integration] 驾驶舱引擎已加载")
        except ImportError as e:
            _safe_print(f"[Agent-Cockpit Integration] 驾驶舱加载失败: {e}")
            self.state["cockpit_connected"] = False
        except Exception as e:
            _safe_print(f"[Agent-Cockpit Integration] 驾驶舱初始化异常: {e}")
            self.state["cockpit_connected"] = False

    def _load_agent_engine(self):
        """加载统一智能体引擎"""
        try:
            from unified_evolution_agent_engine import UnifiedEvolutionAgentEngine
            self.agent_engine = UnifiedEvolutionAgentEngine(state_dir=str(self.state_dir))
            self.state["agent_connected"] = True
            _safe_print("[Agent-Cockpit Integration] 统一智能体引擎已加载")
        except ImportError as e:
            _safe_print(f"[Agent-Cockpit Integration] 统一智能体引擎加载失败: {e}")
            self.state["agent_connected"] = False
        except Exception as e:
            _safe_print(f"[Agent-Cockpit Integration] 统一智能体引擎初始化异常: {e}")
            self.state["agent_connected"] = False

    def _save_state(self):
        """保存状态"""
        try:
            self.state_dir.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[Agent-Cockpit Integration] 状态保存失败: {e}")

    def analyze_task_with_cockpit(self, task_description: str) -> Dict[str, Any]:
        """使用智能体分析任务并在驾驶舱中显示

        Args:
            task_description: 任务描述

        Returns:
            分析结果
        """
        _safe_print(f"[Agent-Cockpit Integration] 分析任务: {task_description}")

        if not self.state["agent_connected"]:
            return {
                "success": False,
                "message": "统一智能体引擎未连接",
                "task": task_description,
            }

        # 使用统一智能体引擎分析任务
        analysis_result = self.agent_engine.analyze_task(task_description)

        # 记录协作
        collaboration = {
            "task": task_description,
            "timestamp": datetime.now().isoformat(),
            "engines_used": len(analysis_result.get("selected_engines", [])),
            "status": "analyzed",
        }

        self.state["active_collaborations"].append(collaboration)
        self.state["total_collaborations"] += 1

        # 同步到驾驶舱
        self._sync_to_cockpit(analysis_result)

        self._save_state()

        return {
            "success": True,
            "message": "任务分析完成",
            "analysis": analysis_result,
            "collaboration_id": len(self.state["active_collaborations"]) - 1,
        }

    def execute_task_with_collaboration(self, task_description: str) -> Dict[str, Any]:
        """使用协作引擎执行任务

        Args:
            task_description: 任务描述

        Returns:
            执行结果
        """
        _safe_print(f"[Agent-Cockpit Integration] 执行任务: {task_description}")

        # 先分析任务
        analysis_result = self.analyze_task_with_cockpit(task_description)

        if not analysis_result.get("success", False):
            return analysis_result

        # 执行任务
        if self.state["agent_connected"]:
            execution_result = self.agent_engine.execute_task(analysis_result.get("analysis", {}))

            # 更新协作状态
            if self.state["active_collaborations"]:
                last_collab = self.state["active_collaborations"][-1]
                last_collab["status"] = "executed"
                last_collab["success"] = execution_result.get("success", False)
                last_collab["executed_engines"] = execution_result.get("executed_engines", 0)

                if execution_result.get("success", False):
                    self.state["successful_collaborations"] += 1
                else:
                    self.state["failed_collaborations"] += 1

            self._save_state()

            return {
                "success": True,
                "message": "任务执行完成",
                "analysis": analysis_result.get("analysis"),
                "execution": execution_result,
            }

        return {
            "success": False,
            "message": "智能体引擎未连接",
            "task": task_description,
        }

    def _sync_to_cockpit(self, analysis_result: Dict[str, Any]):
        """同步分析结果到驾驶舱"""
        if not self.state["cockpit_connected"]:
            return

        try:
            # 保存协作数据供驾驶舱读取
            collaboration_data = {
                "timestamp": datetime.now().isoformat(),
                "task": analysis_result.get("task", ""),
                "intent": analysis_result.get("intent", {}),
                "selected_engines": analysis_result.get("selected_engines", []),
                "execution_plan": analysis_result.get("execution_plan", {}),
            }

            with open(self.collaboration_file, "w", encoding="utf-8") as f:
                json.dump(collaboration_data, f, ensure_ascii=False, indent=2)

            self.state["last_sync_time"] = datetime.now().isoformat()

        except Exception as e:
            _safe_print(f"[Agent-Cockpit Integration] 同步到驾驶舱失败: {e}")

    def get_collaboration_status(self) -> Dict[str, Any]:
        """获取协作状态"""
        status = {
            "integration_version": self.version,
            "integration_status": self.state["integration_status"],
            "cockpit_connected": self.state["cockpit_connected"],
            "agent_connected": self.state["agent_connected"],
            "total_collaborations": self.state["total_collaborations"],
            "successful_collaborations": self.state["successful_collaborations"],
            "failed_collaborations": self.state["failed_collaborations"],
            "active_collaborations_count": len(self.state["active_collaborations"]),
            "last_sync_time": self.state["last_sync_time"],
        }

        # 获取子引擎状态
        if self.state["cockpit_connected"] and self.cockpit_engine:
            try:
                status["cockpit_status"] = {
                    "running": self.cockpit_engine.running,
                    "auto_mode": self.cockpit_engine.auto_mode,
                    "engine_health_score": self.cockpit_engine.check_all_engines_health().get("health_score", 0),
                }
            except Exception:
                pass

        if self.state["agent_connected"] and self.agent_engine:
            try:
                status["agent_status"] = self.agent_engine.get_status()
            except Exception:
                pass

        return status

    def get_unified_dashboard_data(self) -> Dict[str, Any]:
        """获取统一仪表盘数据 - 整合两个引擎的数据"""
        dashboard = {
            "timestamp": datetime.now().isoformat(),
            "integration": self.get_collaboration_status(),
        }

        # 添加驾驶舱数据
        if self.state["cockpit_connected"] and self.cockpit_engine:
            try:
                dashboard["cockpit"] = self.cockpit_engine.get_dashboard_data()
            except Exception as e:
                _safe_print(f"[Agent-Cockpit Integration] 获取驾驶舱数据失败: {e}")

        # 添加智能体数据
        if self.state["agent_connected"] and self.agent_engine:
            try:
                dashboard["agent"] = {
                    "status": self.agent_engine.get_status(),
                    "engines": self.agent_engine.get_engine_list(),
                }
            except Exception as e:
                _safe_print(f"[Agent-Cockpit Integration] 获取智能体数据失败: {e}")

        return dashboard

    def get_engines_health_summary(self) -> Dict[str, Any]:
        """获取引擎健康度汇总"""
        summary = {
            "total_engines": 0,
            "healthy_engines": 0,
            "by_source": {},
            "timestamp": datetime.now().isoformat(),
        }

        # 驾驶舱引擎健康度
        if self.state["cockpit_connected"] and self.cockpit_engine:
            try:
                health = self.cockpit_engine.check_all_engines_health()
                summary["by_source"]["cockpit"] = health
                summary["total_engines"] += health.get("total", 0)
                summary["healthy_engines"] += health.get("healthy", 0)
            except Exception as e:
                _safe_print(f"[Agent-Cockpit Integration] 驾驶舱健康度获取失败: {e}")

        # 智能体引擎健康度
        if self.state["agent_connected"] and self.agent_engine:
            try:
                agent_status = self.agent_engine.get_status()
                available = agent_status.get("available_engines", 0)
                registered = agent_status.get("registered_engines", 0)
                summary["by_source"]["agent"] = {
                    "total": registered,
                    "healthy": available,
                    "health_score": round(available / registered * 100, 1) if registered > 0 else 0,
                }
                summary["total_engines"] += registered
                summary["healthy_engines"] += available
            except Exception as e:
                _safe_print(f"[Agent-Cockpit Integration] 智能体健康度获取失败: {e}")

        # 总体健康度
        summary["overall_health_score"] = round(
            summary["healthy_engines"] / summary["total_engines"] * 100, 1
        ) if summary["total_engines"] > 0 else 0

        return summary

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        issues = []

        if not self.state["cockpit_connected"]:
            issues.append("驾驶舱引擎未连接")

        if not self.state["agent_connected"]:
            issues.append("统一智能体引擎未连接")

        # 检查文件存在性
        required_files = [
            "evolution_cockpit_engine.py",
            "unified_evolution_agent_engine.py",
        ]

        for filename in required_files:
            filepath = self.scripts_dir / filename
            if not filepath.exists():
                issues.append(f"缺少必要文件: {filename}")

        return {
            "healthy": len(issues) == 0,
            "issues": issues,
            "timestamp": datetime.now().isoformat(),
        }

    def status(self) -> str:
        """获取状态摘要"""
        status = self.get_collaboration_status()
        health = self.get_engines_health_summary()

        lines = [
            f"=== 智能体-驾驶舱集成引擎状态 (v{self.version}) ===",
            f"集成状态: {status['integration_status']}",
            f"驾驶舱连接: {'已连接' if status['cockpit_connected'] else '未连接'}",
            f"智能体连接: {'已连接' if status['agent_connected'] else '未连接'}",
            f"",
            f"=== 协作统计 ===",
            f"总协作次数: {status['total_collaborations']}",
            f"成功次数: {status['successful_collaborations']}",
            f"失败次数: {status['failed_collaborations']}",
            f"活跃协作: {status['active_collaborations_count']}",
            f"",
            f"=== 引擎健康度汇总 ===",
            f"总引擎数: {health['total_engines']}",
            f"健康引擎: {health['healthy_engines']}",
            f"总体健康度: {health['overall_health_score']}%",
        ]

        return "\n".join(lines)


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能全场景进化环统一智能体协同引擎与进化驾驶舱深度集成引擎"
    )
    parser.add_argument("command", nargs="?", default="status",
                        help="命令: status, analyze, execute, dashboard, health, help")
    parser.add_argument("--task", "-t", type=str,
                        help="任务描述（用于 analyze/execute 命令）")

    args = parser.parse_args()

    engine = EvolutionAgentCockpitIntegrationEngine()

    if args.command == "status":
        _safe_print(engine.status())

    elif args.command == "analyze":
        if not args.task:
            _safe_print("错误: 请使用 --task 指定任务描述")
            return

        result = engine.analyze_task_with_cockpit(args.task)
        _safe_print("=" * 50)
        _safe_print("任务分析结果")
        _safe_print("=" * 50)
        _safe_print(f"成功: {result.get('success')}")
        _safe_print(f"消息: {result.get('message')}")
        if result.get("analysis"):
            analysis = result["analysis"]
            _safe_print(f"任务: {analysis.get('task')}")
            _safe_print(f"主要意图: {analysis.get('intent', {}).get('primary_intent')}")
            _safe_print(f"推荐引擎数: {len(analysis.get('selected_engines', []))}")
        _safe_print("=" * 50)

    elif args.command == "execute":
        if not args.task:
            _safe_print("错误: 请使用 --task 指定任务描述")
            return

        result = engine.execute_task_with_collaboration(args.task)
        _safe_print("=" * 50)
        _safe_print("任务执行结果")
        _safe_print("=" * 50)
        _safe_print(f"成功: {result.get('success')}")
        _safe_print(f"消息: {result.get('message')}")
        if result.get("execution"):
            exec_data = result["execution"]
            _safe_print(f"执行引擎数: {exec_data.get('executed_engines')}")
            _safe_print(f"总体状态: {exec_data.get('aggregated_result', {}).get('overall_status')}")
        _safe_print("=" * 50)

    elif args.command == "dashboard":
        data = engine.get_unified_dashboard_data()
        _safe_print(json.dumps(data, indent=2, ensure_ascii=False))

    elif args.command == "health":
        health = engine.health_check()
        _safe_print(json.dumps(health, indent=2, ensure_ascii=False))

    elif args.command == "help":
        _safe_print("""
智能全场景进化环统一智能体协同引擎与进化驾驶舱深度集成引擎

用法:
  python evolution_agent_cockpit_integration_engine.py <command> [options]

命令:
  status       - 显示集成引擎状态
  analyze      - 分析任务（需要 --task）
  execute      - 执行任务（需要 --task）
  dashboard    - 获取统一仪表盘数据
  health       - 健康检查
  help         - 显示帮助信息

示例:
  python scripts/evolution_agent_cockpit_integration_engine.py status
  python scripts/evolution_agent_cockpit_integration_engine.py analyze --task "自主进化优化"
  python scripts/evolution_agent_cockpit_integration_engine.py execute --task "执行价值驱动进化"
  python scripts/evolution_agent_cockpit_integration_engine.py dashboard
        """)


if __name__ == "__main__":
    main()