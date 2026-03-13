#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能自动化执行引擎

功能：
- 自动执行 dynamic_engine_orchestrator 生成的编排计划
- 实现从「编排建议→自动执行→结果反馈→学习优化」的完整闭环
- 执行模式配置（自动执行/需要确认/仅建议）
- 执行结果追踪与反馈收集
- 学习优化机制

区别于现有引擎的「生成计划等待用户确认」，本引擎可配置为自动执行模式，
在低风险场景下无需用户确认即可执行，形成真正的自主服务闭环。

这是「超越用户」的能力——用户收到计划后需要手动执行，AI 可以自动完成
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from enum import Enum

# 确保 scripts 目录在路径中
SCRIPT_DIR = Path(__file__).parent
RUNTIME_DIR = SCRIPT_DIR.parent / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"


class ExecutionMode(Enum):
    """执行模式"""
    AUTO = "auto"           # 自动执行，无需确认
    CONFIRM = "confirm"     # 需要确认后执行
    SUGGEST = "suggest"     # 仅提供建议，不执行


class AutoExecutionEngine:
    """智能自动化执行引擎"""

    def __init__(self):
        self.state_file = STATE_DIR / "auto_execution_state.json"
        self.execution_history_file = STATE_DIR / "auto_execution_history.json"
        self.preferences_file = STATE_DIR / "auto_execution_preferences.json"
        self.state = self._load_state()
        self.history = self._load_history()
        self.preferences = self._load_preferences()

    def _load_state(self) -> Dict:
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "mode": "auto",
            "enabled": True,
            "last_execution": None,
            "total_executions": 0,
            "successful_executions": 0,
        }

    def _save_state(self):
        """保存状态"""
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def _load_history(self) -> Dict:
        """加载执行历史"""
        if self.execution_history_file.exists():
            try:
                with open(self.execution_history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"executions": []}

    def _save_history(self):
        """保存执行历史"""
        # 只保留最近100条记录
        if len(self.history.get("executions", [])) > 100:
            self.history["executions"] = self.history["executions"][-100:]
        with open(self.execution_history_file, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def _load_preferences(self) -> Dict:
        """加载偏好设置"""
        if self.preferences_file.exists():
            try:
                with open(self.preferences_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "auto_mode_categories": ["文件整理", "系统维护", "数据备份", "健康检查"],
            "confirm_categories": ["数据删除", "配置修改", "敏感操作"],
            "learn_from_execution": True,
            "max_auto_retry": 2,
        }

    def set_mode(self, mode: str) -> Dict:
        """设置执行模式"""
        if mode not in ["auto", "confirm", "suggest"]:
            return {"success": False, "message": f"无效的执行模式: {mode}"}

        self.state["mode"] = mode
        self._save_state()
        return {"success": True, "message": f"执行模式已设置为: {mode}"}

    def get_mode(self) -> Dict:
        """获取当前执行模式"""
        return {
            "mode": self.state.get("mode", "auto"),
            "enabled": self.state.get("enabled", True),
        }

    def should_auto_execute(self, plan: Dict) -> bool:
        """判断是否应该自动执行"""
        if self.state.get("mode") == "suggest":
            return False

        if self.state.get("mode") == "confirm":
            return False

        # auto 模式下，检查是否在允许自动执行的分类中
        category = plan.get("category", "")
        auto_categories = self.preferences.get("auto_mode_categories", [])

        if category in auto_categories:
            return True

        # 检查风险等级
        risk_level = plan.get("risk_level", "low")
        return risk_level in ["low", "medium"]

    def execute_plan(self, plan: Dict, auto: bool = True) -> Dict:
        """
        执行编排计划

        Args:
            plan: 编排计划（来自 dynamic_engine_orchestrator）
            auto: 是否自动执行（忽略模式设置）

        Returns:
            执行结果
        """
        if not plan:
            return {"success": False, "message": "计划为空"}

        # 检查是否需要确认
        if not auto and not self.should_auto_execute(plan):
            return {
                "success": False,
                "needs_confirmation": True,
                "message": "此操作需要确认后才能执行",
                "plan_summary": self._summarize_plan(plan),
            }

        # 记录执行开始
        execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        result = {
            "execution_id": execution_id,
            "plan_id": plan.get("plan_id", ""),
            "task_description": plan.get("task_description", ""),
            "start_time": datetime.now().isoformat(),
            "steps": [],
            "success": True,
            "total_steps": 0,
            "completed_steps": 0,
            "failed_steps": 0,
        }

        # 获取执行步骤
        steps = plan.get("execution_steps", plan.get("steps", []))
        result["total_steps"] = len(steps)

        # 逐步执行
        for i, step in enumerate(steps):
            step_result = self._execute_step(step, i, len(steps))
            result["steps"].append(step_result)

            if step_result.get("success"):
                result["completed_steps"] += 1
            else:
                result["failed_steps"] += 1
                # 如果步骤失败，根据配置决定是否继续
                if not step.get("critical", True):
                    continue
                else:
                    result["success"] = False
                    break

        # 记录执行结束
        result["end_time"] = datetime.now().isoformat()
        result["duration_seconds"] = (
            datetime.fromisoformat(result["end_time"]) -
            datetime.fromisoformat(result["start_time"])
        ).total_seconds()

        # 更新统计
        self.state["last_execution"] = result["end_time"]
        self.state["total_executions"] = self.state.get("total_executions", 0) + 1
        if result["success"]:
            self.state["successful_executions"] = self.state.get("successful_executions", 0) + 1

        # 记录到历史
        self._record_execution(result)

        # 学习优化
        if self.preferences.get("learn_from_execution", True):
            self._learn_from_result(result, plan)

        self._save_state()

        return result

    def _execute_step(self, step: Dict, index: int, total: int) -> Dict:
        """执行单个步骤"""
        step_result = {
            "index": index,
            "description": step.get("description", f"步骤 {index + 1}"),
            "action": step.get("action", ""),
            "params": step.get("params", {}),
            "success": False,
            "message": "",
            "output": None,
        }

        action = step.get("action", "")
        params = step.get("params", {})

        try:
            # 根据动作类型执行
            if action == "run_script":
                # 运行脚本
                script_name = params.get("script", "")
                script_args = params.get("args", [])
                output = self._run_script(script_name, script_args)
                step_result["output"] = output
                step_result["success"] = output.get("returncode", 1) == 0

            elif action == "call_engine":
                # 调用引擎
                engine_name = params.get("engine", "")
                method = params.get("method", "")
                engine_args = params.get("args", {})
                output = self._call_engine(engine_name, method, engine_args)
                step_result["output"] = output
                step_result["success"] = output.get("success", False)

            elif action == "execute_command":
                # 执行命令
                command = params.get("command", "")
                output = self._execute_command(command)
                step_result["output"] = output
                step_result["success"] = output.get("returncode", 1) == 0

            elif action == "wait":
                # 等待
                import time
                duration = params.get("duration", 1)
                time.sleep(duration)
                step_result["success"] = True
                step_result["message"] = f"等待 {duration} 秒"

            else:
                # 未知动作，记录但不执行
                step_result["message"] = f"未知动作类型: {action}"
                step_result["success"] = True  # 视为跳过

            if not step_result.get("message"):
                step_result["message"] = "执行成功" if step_result["success"] else "执行失败"

        except Exception as e:
            step_result["success"] = False
            step_result["message"] = f"执行出错: {str(e)}"

        return step_result

    def _run_script(self, script_name: str, args: List[str]) -> Dict:
        """运行脚本"""
        script_path = SCRIPT_DIR / script_name
        if not script_path.exists():
            return {"returncode": 1, "error": f"脚本不存在: {script_name}"}

        cmd = [sys.executable, str(script_path)] + args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
            )
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except subprocess.TimeoutExpired:
            return {"returncode": 1, "error": "脚本执行超时"}
        except Exception as e:
            return {"returncode": 1, "error": str(e)}

    def _call_engine(self, engine_name: str, method: str, args: Dict) -> Dict:
        """调用引擎"""
        try:
            # 动态导入引擎模块
            engine_path = SCRIPT_DIR / f"{engine_name}.py"
            if not engine_path.exists():
                return {"success": False, "error": f"引擎不存在: {engine_name}"}

            # 使用 do.py 调用引擎
            cmd = [
                sys.executable,
                str(SCRIPT_DIR / "do.py"),
                f"{engine_name}.{method}",
            ]
            for key, value in args.items():
                cmd.append(f"{key}={value}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _execute_command(self, command: str) -> Dict:
        """执行系统命令"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300,
            )
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except subprocess.TimeoutExpired:
            return {"returncode": 1, "error": "命令执行超时"}
        except Exception as e:
            return {"returncode": 1, "error": str(e)}

    def _summarize_plan(self, plan: Dict) -> Dict:
        """生成计划摘要"""
        steps = plan.get("execution_steps", plan.get("steps", []))
        return {
            "task_description": plan.get("task_description", ""),
            "category": plan.get("category", ""),
            "risk_level": plan.get("risk_level", "low"),
            "total_steps": len(steps),
            "step_summaries": [
                {
                    "index": i,
                    "description": step.get("description", f"步骤 {i + 1}"),
                    "action": step.get("action", ""),
                }
                for i, step in enumerate(steps)
            ],
        }

    def _record_execution(self, result: Dict):
        """记录执行到历史"""
        self.history["executions"].append({
            "execution_id": result.get("execution_id"),
            "task_description": result.get("task_description"),
            "start_time": result.get("start_time"),
            "end_time": result.get("end_time"),
            "duration_seconds": result.get("duration_seconds"),
            "success": result.get("success"),
            "total_steps": result.get("total_steps"),
            "completed_steps": result.get("completed_steps"),
            "failed_steps": result.get("failed_steps"),
        })
        self._save_history()

    def _learn_from_result(self, result: Dict, plan: Dict):
        """从执行结果学习，优化偏好"""
        if not result.get("success"):
            # 记录失败类别，避免自动执行
            category = plan.get("category", "")
            if category not in self.preferences.get("confirm_categories", []):
                self.preferences.setdefault("confirm_categories", []).append(category)
                # 保存偏好
                with open(self.preferences_file, "w", encoding="utf-8") as f:
                    json.dump(self.preferences, f, ensure_ascii=False, indent=2)

    def get_execution_status(self) -> Dict:
        """获取执行状态"""
        return {
            "mode": self.state.get("mode", "auto"),
            "enabled": self.state.get("enabled", True),
            "total_executions": self.state.get("total_executions", 0),
            "successful_executions": self.state.get("successful_executions", 0),
            "success_rate": (
                self.state.get("successful_executions", 0) /
                max(self.state.get("total_executions", 1), 1)
            ),
            "last_execution": self.state.get("last_execution"),
        }

    def get_execution_history(self, limit: int = 10) -> Dict:
        """获取执行历史"""
        executions = self.history.get("executions", [])
        return {
            "total": len(executions),
            "recent": executions[-limit:] if len(executions) >= limit else executions,
        }

    def get_execution_suggestions(self, plan: Dict) -> Dict:
        """获取执行建议"""
        if self.should_auto_execute(plan):
            return {
                "suggestion": "auto",
                "message": "此计划可以自动执行",
                "confidence": 0.9,
            }
        elif self.state.get("mode") == "confirm":
            return {
                "suggestion": "confirm",
                "message": "此操作需要您确认后执行",
                "confidence": 0.8,
            }
        else:
            return {
                "suggestion": "suggest",
                "message": "此计划风险较高，仅提供建议",
                "confidence": 0.7,
            }


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description="智能自动化执行引擎")
    parser.add_argument("command", nargs="?", help="命令: status/history/suggest/set_mode/execute")
    parser.add_argument("--plan", type=str, help="计划 JSON 文件路径或 JSON 字符串")
    parser.add_argument("--mode", type=str, choices=["auto", "confirm", "suggest"], help="执行模式")

    args = parser.parse_args()

    engine = AutoExecutionEngine()

    if args.command == "status":
        print(json.dumps(engine.get_execution_status(), ensure_ascii=False, indent=2))

    elif args.command == "history":
        print(json.dumps(engine.get_execution_history(), ensure_ascii=False, indent=2))

    elif args.command == "set_mode" and args.mode:
        result = engine.set_mode(args.mode)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "execute" and args.plan:
        # 解析计划
        try:
            # 尝试作为文件路径
            if os.path.isfile(args.plan):
                with open(args.plan, "r", encoding="utf-8") as f:
                    plan = json.load(f)
            else:
                # 尝试作为 JSON 字符串
                plan = json.loads(args.plan)

            result = engine.execute_plan(plan)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        except Exception as e:
            print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False, indent=2))

    elif args.command == "suggest" and args.plan:
        # 解析计划
        try:
            if os.path.isfile(args.plan):
                with open(args.plan, "r", encoding="utf-8") as f:
                    plan = json.load(f)
            else:
                plan = json.loads(args.plan)

            result = engine.get_execution_suggestions(plan)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        except Exception as e:
            print(json.dumps({"error": str(e)}, ensure_ascii=False, indent=2))

    else:
        # 默认显示状态
        print(json.dumps(engine.get_execution_status(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()