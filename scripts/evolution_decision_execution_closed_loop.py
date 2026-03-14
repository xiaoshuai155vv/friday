#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环决策-执行闭环深度集成引擎

将 round 371 的多维度智能协同决策与自适应规划引擎与进化执行引擎深度集成，
形成从「智能决策→自动规划→自主执行→效果验证→反馈学习」的完整闭环。

系统不仅能智能决定「现在最应该进化什么」和「如何规划」，还能将决策自动转化为
可执行的进化任务并完成整个循环，实现真正的「决策执行一体化」。

Version: 1.0.0
Author: Auto Evolution System
"""

import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# 基础路径配置
SCRIPT_DIR = Path(__file__).parent
RUNTIME_DIR = SCRIPT_DIR.parent / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"


class EvolutionDecisionExecutionClosedLoop:
    """
    决策-执行闭环深度集成引擎

    核心能力：
    1. 决策接收：接收来自多维度决策规划引擎的决策结果
    2. 任务转换：将决策结果转换为可执行的进化任务
    3. 自动执行：自动调度和执行进化任务
    4. 过程监控：实时监控执行进度和状态
    5. 效果验证：验证执行结果是否符合决策预期
    6. 反馈学习：将执行效果反馈到决策优化中
    """

    def __init__(self):
        self.engine_name = "decision_execution_closed_loop"
        self.version = "1.0.0"
        self.state_file = STATE_DIR / f"{self.engine_name}_state.json"
        self.history_file = STATE_DIR / f"{self.engine_name}_history.json"
        self.load_state()

    def load_state(self):
        """加载引擎状态"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                self.state = json.load(f)
        else:
            self.state = {
                "initialized": False,
                "last_execution": None,
                "pending_tasks": [],
                "completed_tasks": [],
                "failed_tasks": [],
                "metrics": {
                    "total_executions": 0,
                    "successful_executions": 0,
                    "failed_executions": 0,
                    "average_execution_time": 0
                }
            }

    def save_state(self):
        """保存引擎状态"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def load_history(self):
        """加载执行历史"""
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                self.history = json.load(f)
        else:
            self.history = []

    def save_history(self):
        """保存执行历史"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def receive_decision(self, decision_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        接收来自决策引擎的决策结果

        Args:
            decision_result: 来自多维度决策规划引擎的结果

        Returns:
            任务转换结果
        """
        print(f"[{self.engine_name}] 接收决策结果: {decision_result.get('goal', 'Unknown')}")

        # 解析决策结果
        task = {
            "id": f"task_{int(time.time())}",
            "goal": decision_result.get("goal", ""),
            "priority": decision_result.get("priority", 5),
            "strategy": decision_result.get("strategy", ""),
            "plan": decision_result.get("plan", []),
            "expected_outcome": decision_result.get("expected_outcome", ""),
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        }

        self.state["pending_tasks"].append(task)
        self.save_state()

        return {
            "success": True,
            "task_id": task["id"],
            "message": f"决策已接收，任务 {task['id']} 已加入执行队列"
        }

    def transform_to_executable(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        将任务转换为可执行的任务单元

        Args:
            task: 原始任务

        Returns:
            可执行的任务单元
        """
        executable = {
            "id": task["id"],
            "goal": task["goal"],
            "priority": task["priority"],
            "steps": [],
            "status": "ready"
        }

        # 将决策计划转换为可执行步骤
        plan = task.get("plan", [])
        for i, step in enumerate(plan):
            executable_step = {
                "step_id": f"{task['id']}_step_{i}",
                "description": step.get("description", ""),
                "action": step.get("action", ""),
                "params": step.get("params", {}),
                "timeout": step.get("timeout", 300),
                "retry": step.get("retry", 3),
                "status": "pending"
            }
            executable["steps"].append(executable_step)

        return executable

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行进化任务

        Args:
            task: 可执行任务

        Returns:
            执行结果
        """
        print(f"[{self.engine_name}] 开始执行任务: {task['id']}")
        start_time = time.time()

        # 确保加载历史
        self.load_history()

        task["status"] = "running"
        task["started_at"] = datetime.now().isoformat()
        self.save_state()

        execution_log = {
            "task_id": task["id"],
            "steps": [],
            "start_time": start_time
        }

        # 按顺序执行每个步骤
        for step in task.get("steps", []):
            step_result = self.execute_step(step)
            execution_log["steps"].append(step_result)

            if step_result["status"] == "failed":
                task["status"] = "failed"
                task["error"] = f"步骤 {step['step_id']} 执行失败: {step_result.get('error', '')}"
                break

            # 检查是否需要动态调整
            if step_result.get("needs_adjustment", False):
                self.adjust_remaining_steps(task, step_result)

        # 任务完成
        if task.get("status") != "failed":
            task["status"] = "completed"
            task["completed_at"] = datetime.now().isoformat()

        # 计算执行时间
        execution_time = time.time() - start_time
        execution_log["execution_time"] = execution_time
        execution_log["end_time"] = time.time()

        # 更新状态
        self.update_task_state(task, execution_time)

        # 记录历史
        self.history.append(execution_log)
        self.save_history()

        # 效果验证
        verification_result = self.verify_execution(task, execution_log)

        print(f"[{self.engine_name}] 任务执行完成: {task['id']}, 状态: {task['status']}, 耗时: {execution_time:.2f}s")

        return {
            "task_id": task["id"],
            "status": task["status"],
            "execution_time": execution_time,
            "verification": verification_result
        }

    def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行单个步骤

        Args:
            step: 步骤定义

        Returns:
            步骤执行结果
        """
        step_id = step["step_id"]
        action = step.get("action", "")
        params = step.get("params", {})
        timeout = step.get("timeout", 300)
        retry = step.get("retry", 3)

        print(f"[{self.engine_name}] 执行步骤: {step_id} - {action}")

        # 尝试执行
        for attempt in range(retry):
            try:
                result = self.execute_action(action, params, timeout)
                if result["success"]:
                    return {
                        "step_id": step_id,
                        "status": "completed",
                        "result": result,
                        "attempts": attempt + 1
                    }
            except Exception as e:
                print(f"[{self.engine_name}] 步骤 {step_id} 尝试 {attempt + 1} 失败: {e}")
                time.sleep(1)

        return {
            "step_id": step_id,
            "status": "failed",
            "error": f"重试 {retry} 次后仍失败",
            "attempts": retry
        }

    def execute_action(self, action: str, params: Dict[str, Any], timeout: int) -> Dict[str, Any]:
        """
        执行具体动作

        Args:
            action: 动作类型
            params: 参数
            timeout: 超时时间

        Returns:
            执行结果
        """
        # 根据动作类型执行不同的操作
        if action == "create_script":
            return self._create_script(params)
        elif action == "execute_script":
            return self._execute_script(params, timeout)
        elif action == "update_file":
            return self._update_file(params)
        elif action == "run_command":
            return self._run_command(params, timeout)
        elif action == "update_state":
            return self._update_state_file(params)
        else:
            return {
                "success": False,
                "error": f"未知动作类型: {action}"
            }

    def _create_script(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """创建脚本文件"""
        script_path = params.get("path", "")
        content = params.get("content", "")

        try:
            # 确保目录存在
            Path(script_path).parent.mkdir(parents=True, exist_ok=True)

            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return {
                "success": True,
                "message": f"脚本已创建: {script_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _execute_script(self, params: Dict[str, Any], timeout: int) -> Dict[str, Any]:
        """执行脚本"""
        script_path = params.get("path", "")
        args = params.get("args", [])

        try:
            cmd = ["python", script_path] + args
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='replace'
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"执行超时 ({timeout}s)"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _update_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """更新文件"""
        file_path = params.get("path", "")
        content = params.get("content", "")

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return {
                "success": True,
                "message": f"文件已更新: {file_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _run_command(self, params: Dict[str, Any], timeout: int) -> Dict[str, Any]:
        """运行命令"""
        command = params.get("command", "")

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='replace'
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"命令执行超时 ({timeout}s)"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _update_state_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """更新状态文件"""
        file_path = params.get("path", "")
        updates = params.get("updates", {})

        try:
            # 读取现有状态
            if Path(file_path).exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    state = json.load(f)
            else:
                state = {}

            # 更新状态
            state.update(updates)

            # 保存
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)

            return {
                "success": True,
                "message": f"状态已更新: {file_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def adjust_remaining_steps(self, task: Dict[str, Any], adjustment_info: Dict[str, Any]):
        """
        根据执行情况动态调整剩余步骤

        Args:
            task: 当前任务
            adjustment_info: 调整信息
        """
        print(f"[{self.engine_name}] 动态调整任务步骤")

        # 根据 adjustment_info 调整后续步骤
        adjustment_type = adjustment_info.get("type", "")
        current_step = adjustment_info.get("current_step", "")

        # 找到当前步骤的索引
        current_index = -1
        for i, step in enumerate(task["steps"]):
            if step["step_id"] == current_step:
                current_index = i
                break

        if adjustment_type == "skip":
            # 跳过某些步骤
            skip_from = adjustment_info.get("skip_from", current_index + 1)
            skip_to = adjustment_info.get("skip_to", len(task["steps"]))
            task["steps"] = task["steps"][:skip_from] + task["steps"][skip_to:]
        elif adjustment_type == "add":
            # 添加新步骤
            new_steps = adjustment_info.get("new_steps", [])
            task["steps"] = task["steps"][:current_index + 1] + new_steps + task["steps"][current_index + 1:]
        elif adjustment_type == "modify":
            # 修改后续步骤
            modifications = adjustment_info.get("modifications", {})
            for i in range(current_index + 1, len(task["steps"])):
                step_id = task["steps"][i]["step_id"]
                if step_id in modifications:
                    task["steps"][i].update(modifications[step_id])

    def update_task_state(self, task: Dict[str, Any], execution_time: float):
        """
        更新任务状态

        Args:
            task: 任务
            execution_time: 执行时间
        """
        # 从待执行队列移除
        self.state["pending_tasks"] = [t for t in self.state["pending_tasks"] if t["id"] != task["id"]]

        # 加入对应队列
        if task["status"] == "completed":
            self.state["completed_tasks"].append(task)
            self.state["metrics"]["successful_executions"] += 1
        elif task["status"] == "failed":
            self.state["failed_tasks"].append(task)
            self.state["metrics"]["failed_executions"] += 1

        # 更新指标
        self.state["metrics"]["total_executions"] += 1

        # 计算平均执行时间
        total = self.state["metrics"]["total_executions"]
        current_avg = self.state["metrics"]["average_execution_time"]
        self.state["metrics"]["average_execution_time"] = (
            (current_avg * (total - 1) + execution_time) / total
        )

        self.state["last_execution"] = {
            "task_id": task["id"],
            "status": task["status"],
            "time": datetime.now().isoformat()
        }

        self.save_state()

    def verify_execution(self, task: Dict[str, Any], execution_log: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证执行效果

        Args:
            task: 任务
            execution_log: 执行日志

        Returns:
            验证结果
        """
        print(f"[{self.engine_name}] 执行效果验证")

        # 基本验证
        verification = {
            "task_completed": task["status"] == "completed",
            "all_steps_completed": all(s["status"] == "completed" for s in execution_log.get("steps", [])),
            "execution_time": execution_log.get("execution_time", 0),
            "step_count": len(execution_log.get("steps", [])),
            "verification_time": datetime.now().isoformat()
        }

        # 计算成功率
        if verification["step_count"] > 0:
            completed_steps = sum(1 for s in execution_log.get("steps", []) if s["status"] == "completed")
            verification["step_success_rate"] = completed_steps / verification["step_count"]
        else:
            verification["step_success_rate"] = 0

        # 效果评估
        if verification["task_completed"] and verification["step_success_rate"] >= 0.8:
            verification["overall_result"] = "success"
        elif verification["task_completed"] and verification["step_success_rate"] >= 0.5:
            verification["overall_result"] = "partial"
        else:
            verification["overall_result"] = "failed"

        return verification

    def feedback_learning(self, task: Dict[str, Any], verification: Dict[str, Any]):
        """
        反馈学习：将执行效果反馈到决策优化

        Args:
            task: 任务
            verification: 验证结果
        """
        print(f"[{self.engine_name}] 执行反馈学习")

        # 生成学习报告
        learning_report = {
            "task_id": task["id"],
            "goal": task.get("goal", ""),
            "verification_result": verification.get("overall_result", ""),
            "success_rate": verification.get("step_success_rate", 0),
            "execution_time": verification.get("execution_time", 0),
            "learned_at": datetime.now().isoformat()
        }

        # 保存学习报告
        learning_file = STATE_DIR / f"decision_execution_learning_{datetime.now().strftime('%Y%m%d')}.json"

        # 读取或创建学习报告集合
        if learning_file.exists():
            with open(learning_file, 'r', encoding='utf-8') as f:
                learning_reports = json.load(f)
        else:
            learning_reports = []

        learning_reports.append(learning_report)

        # 只保留最近30天的报告
        if len(learning_reports) > 30:
            learning_reports = learning_reports[-30:]

        with open(learning_file, 'w', encoding='utf-8') as f:
            json.dump(learning_reports, f, ensure_ascii=False, indent=2)

        print(f"[{self.engine_name}] 学习报告已保存")

    def process_pending_tasks(self) -> Dict[str, Any]:
        """
        处理待执行的决策任务

        Returns:
            处理结果
        """
        pending = self.state.get("pending_tasks", [])

        if not pending:
            return {
                "success": True,
                "message": "无待处理任务"
            }

        # 按优先级排序
        pending.sort(key=lambda x: x.get("priority", 5), reverse=True)

        # 选择最高优先级任务执行
        task = pending[0]
        executable_task = self.transform_to_executable(task)

        # 执行任务
        result = self.execute_task(executable_task)

        # 反馈学习
        if result.get("verification"):
            self.feedback_learning(executable_task, result["verification"])

        return result

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "engine": self.engine_name,
            "version": self.version,
            "initialized": True,
            "pending_tasks": len(self.state.get("pending_tasks", [])),
            "completed_tasks": len(self.state.get("completed_tasks", [])),
            "failed_tasks": len(self.state.get("failed_tasks", [])),
            "metrics": self.state.get("metrics", {}),
            "last_execution": self.state.get("last_execution")
        }

    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取执行历史"""
        return self.history[-limit:] if self.history else []


def main():
    """主入口"""
    import sys

    engine = EvolutionDecisionExecutionClosedLoop()

    if len(sys.argv) < 2:
        print(f"决策-执行闭环深度集成引擎 v{engine.version}")
        print("\n用法:")
        print("  python evolution_decision_execution_closed_loop.py status           - 查看引擎状态")
        print("  python evolution_decision_execution_closed_loop.py process         - 处理待执行任务")
        print("  python evolution_decision_execution_closed_loop.py history [n]     - 查看执行历史")
        print("  python evolution_decision_execution_closed_loop.py test           - 测试完整流程")
        return

    command = sys.argv[1]

    if command == "status":
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif command == "process":
        result = engine.process_pending_tasks()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "history":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        history = engine.get_history(limit)
        print(json.dumps(history, ensure_ascii=False, indent=2))

    elif command == "test":
        # 测试完整流程
        print("=== 测试决策-执行闭环 ===")

        # 模拟接收决策
        test_decision = {
            "goal": "测试任务：创建测试脚本并执行",
            "priority": 10,
            "strategy": "create_and_execute",
            "plan": [
                {
                    "description": "创建测试脚本",
                    "action": "create_script",
                    "params": {
                        "path": str(SCRIPT_DIR / "test_evolution_decision_execution.py"),
                        "content": "#!/usr/bin/env python3\nprint('Test script executed successfully!')\n"
                    },
                    "timeout": 30,
                    "retry": 2
                },
                {
                    "description": "执行测试脚本",
                    "action": "execute_script",
                    "params": {
                        "path": str(SCRIPT_DIR / "test_evolution_decision_execution.py")
                    },
                    "timeout": 60,
                    "retry": 2
                }
            ],
            "expected_outcome": "测试脚本成功创建并执行"
        }

        # 接收决策
        result = engine.receive_decision(test_decision)
        print(f"\n1. 接收决策: {json.dumps(result, ensure_ascii=False, indent=2)}")

        # 处理任务
        result = engine.process_pending_tasks()
        print(f"\n2. 执行结果: {json.dumps(result, ensure_ascii=False, indent=2)}")

        # 清理测试文件
        test_file = SCRIPT_DIR / "test_evolution_decision_execution.py"
        if test_file.exists():
            test_file.unlink()
            print("\n3. 测试文件已清理")

        print("\n=== 测试完成 ===")


if __name__ == "__main__":
    main()