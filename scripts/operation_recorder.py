#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能操作演示与回放引擎
记录用户操作序列，智能转换为可复用的演示脚本或自动化计划

功能：
1. 操作录制 - 记录鼠标、键盘、窗口操作序列
2. 操作转换 - 将录制操作转换为 run_plan JSON
3. 操作回放 - 重新执行录制的操作序列
4. 演示生成 - 生成带解说的操作步骤文档

工作原理：
- 启动录制后，系统持续监听和记录用户操作
- 停止录制后，生成可复用的操作序列
- 支持将操作序列转换为 run_plan 格式
- 支持回放操作序列
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

# Windows 特定的模块
try:
    import ctypes
    from ctypes import wintypes
except ImportError:
    ctypes = None

# 确保 scripts 目录在路径中
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..'))
STATE_DIR = os.path.join(PROJECT_DIR, 'runtime', 'state')


class OperationRecorder:
    """智能操作演示与回放引擎"""

    def __init__(self):
        self.recording_file = os.path.join(STATE_DIR, 'operation_recording.json')
        self.operations = []
        self.is_recording = False
        self.start_time = None

    def start_recording(self) -> Dict[str, Any]:
        """开始录制操作序列"""
        self.operations = []
        self.is_recording = True
        self.start_time = datetime.now()
        return {
            "status": "started",
            "message": "开始录制操作序列，请执行要记录的操作...",
            "start_time": self.start_time.isoformat()
        }

    def stop_recording(self) -> Dict[str, Any]:
        """停止录制操作序列"""
        if not self.is_recording:
            return {
                "status": "error",
                "message": "当前未在录制状态"
            }

        self.is_recording = False
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        # 保存录制内容
        recording_data = {
            "metadata": {
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "operation_count": len(self.operations)
            },
            "operations": self.operations
        }

        # 确保目录存在
        os.makedirs(os.path.dirname(self.recording_file), exist_ok=True)
        with open(self.recording_file, 'w', encoding='utf-8') as f:
            json.dump(recording_data, f, ensure_ascii=False, indent=2)

        return {
            "status": "stopped",
            "message": f"录制完成，共记录 {len(self.operations)} 个操作",
            "duration_seconds": duration,
            "file": self.recording_file
        }

    def add_operation(self, operation_type: str, details: Dict[str, Any]):
        """添加操作到录制序列"""
        if not self.is_recording:
            return

        operation = {
            "type": operation_type,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.operations.append(operation)

    def record_click(self, x: int, y: int, button: str = "left") -> Dict[str, Any]:
        """记录鼠标点击操作"""
        details = {"x": x, "y": y, "button": button}
        self.add_operation("click", details)
        return {"status": "recorded", "operation": "click", "position": f"({x}, {y})"}

    def record_type(self, text: str) -> Dict[str, Any]:
        """记录键盘输入操作"""
        details = {"text": text}
        self.add_operation("type", details)
        return {"status": "recorded", "operation": "type", "text": text[:50]}

    def record_key(self, key: str, vk: int = None) -> Dict[str, Any]:
        """记录键盘按键操作"""
        details = {"key": key}
        if vk:
            details["vk"] = vk
        self.add_operation("key", details)
        return {"status": "recorded", "operation": "key", "key": key}

    def record_activate(self, window_title: str) -> Dict[str, Any]:
        """记录窗口激活操作"""
        details = {"window_title": window_title}
        self.add_operation("activate", details)
        return {"status": "recorded", "operation": "activate", "window": window_title}

    def record_maximize(self, window_title: str) -> Dict[str, Any]:
        """记录窗口最大化操作"""
        details = {"window_title": window_title}
        self.add_operation("maximize", details)
        return {"status": "recorded", "operation": "maximize", "window": window_title}

    def record_scroll(self, delta: int, x: int = None, y: int = None) -> Dict[str, Any]:
        """记录滚动操作"""
        details = {"delta": delta}
        if x is not None:
            details["x"] = x
        if y is not None:
            details["y"] = y
        self.add_operation("scroll", details)
        return {"status": "recorded", "operation": "scroll", "delta": delta}

    def record_screenshot(self, description: str = "") -> Dict[str, Any]:
        """记录截图操作"""
        details = {"description": description}
        self.add_operation("screenshot", details)
        return {"status": "recorded", "operation": "screenshot", "description": description}

    def get_recording_status(self) -> Dict[str, Any]:
        """获取录制状态"""
        return {
            "is_recording": self.is_recording,
            "operation_count": len(self.operations),
            "start_time": self.start_time.isoformat() if self.start_time else None
        }

    def load_recording(self, file_path: str = None) -> Dict[str, Any]:
        """加载已保存的录制内容"""
        path = file_path or self.recording_file
        if not os.path.exists(path):
            return {"status": "error", "message": f"文件不存在: {path}"}

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return {"status": "success", "data": data}
        except Exception as e:
            return {"status": "error", "message": f"加载失败: {e}"}

    def convert_to_run_plan(self, file_path: str = None, plan_name: str = "录制操作") -> Dict[str, Any]:
        """将录制操作转换为 run_plan JSON 格式"""
        load_result = self.load_recording(file_path)
        if load_result.get("status") != "success":
            return load_result

        recording = load_result["data"]
        operations = recording.get("operations", [])

        steps = []
        for op in operations:
            op_type = op.get("type")
            details = op.get("details", {})

            step = {}
            if op_type == "click":
                step = {"do": "click", "x": details.get("x"), "y": details.get("y")}
            elif op_type == "type":
                step = {"do": "type", "text": details.get("text")}
            elif op_type == "key":
                key = details.get("key")
                if key == "Enter":
                    step = {"do": "key", "key": 13}
                elif key == "Escape":
                    step = {"do": "key", "key": 27}
                else:
                    step = {"do": "key", "key": key}
            elif op_type == "activate":
                step = {"run": "window_tool", "args": ["activate", details.get("window_title")]}
            elif op_type == "maximize":
                step = {"run": "window_tool", "args": ["maximize", details.get("window_title")]}
            elif op_type == "scroll":
                delta = details.get("delta")
                x = details.get("x")
                y = details.get("y")
                if x is not None and y is not None:
                    step = {"do": "scroll", "delta": delta, "x": x, "y": y}
                else:
                    step = {"do": "scroll", "delta": delta}
            elif op_type == "screenshot":
                step = {"do": "screenshot"}

            if step:
                steps.append(step)

        # 生成 run_plan 格式
        run_plan = {
            "name": plan_name,
            "triggers": [plan_name],
            "steps": steps
        }

        # 保存转换后的计划
        plan_file = os.path.join(PROJECT_DIR, 'assets', 'plans', f'{plan_name}.json')
        os.makedirs(os.path.dirname(plan_file), exist_ok=True)
        with open(plan_file, 'w', encoding='utf-8') as f:
            json.dump(run_plan, f, ensure_ascii=False, indent=2)

        return {
            "status": "success",
            "message": f"已转换为 run_plan: {plan_file}",
            "plan_file": plan_file,
            "step_count": len(steps)
        }

    def generate_demo_script(self, file_path: str = None) -> Dict[str, Any]:
        """生成带解说的操作演示脚本"""
        load_result = self.load_recording(file_path)
        if load_result.get("status") != "success":
            return load_result

        recording = load_result["data"]
        operations = recording.get("operations", [])
        metadata = recording.get("metadata", {})

        script_lines = [
            f"# 操作演示脚本",
            f"# 生成时间: {datetime.now().isoformat()}",
            f"# 原始录制: {metadata.get('start_time')}",
            f"# 操作数量: {len(operations)}",
            f"# 时长: {metadata.get('duration_seconds', 0):.1f} 秒",
            "",
            "## 操作步骤",
            ""
        ]

        for i, op in enumerate(operations, 1):
            op_type = op.get("type")
            details = op.get("details", {})
            timestamp = op.get("timestamp", "")

            if op_type == "click":
                script_lines.append(f"### 步骤 {i}: 鼠标点击")
                script_lines.append(f"- 时间: {timestamp}")
                script_lines.append(f"- 位置: ({details.get('x')}, {details.get('y')})")
                script_lines.append(f"- 按钮: {details.get('button', 'left')}")
                script_lines.append("```bash")
                script_lines.append(f"mouse_tool click {details.get('x')} {details.get('y')}")
                script_lines.append("```")
            elif op_type == "type":
                script_lines.append(f"### 步骤 {i}: 键盘输入")
                script_lines.append(f"- 时间: {timestamp}")
                script_lines.append(f"- 输入内容: {details.get('text')}")
                script_lines.append("```bash")
                script_lines.append(f'keyboard_tool type "{details.get("text")}"')
                script_lines.append("```")
            elif op_type == "key":
                script_lines.append(f"### 步骤 {i}: 键盘按键")
                script_lines.append(f"- 时间: {timestamp}")
                script_lines.append(f"- 按键: {details.get('key')}")
                script_lines.append("```bash")
                script_lines.append(f"keyboard_tool key {details.get('key')}")
                script_lines.append("```")
            elif op_type == "activate":
                script_lines.append(f"### 步骤 {i}: 激活窗口")
                script_lines.append(f"- 时间: {timestamp}")
                script_lines.append(f"- 窗口标题: {details.get('window_title')}")
                script_lines.append("```bash")
                script_lines.append(f'window_tool activate "{details.get("window_title")}"')
                script_lines.append("```")
            elif op_type == "maximize":
                script_lines.append(f"### 步骤 {i}: 最大化窗口")
                script_lines.append(f"- 时间: {timestamp}")
                script_lines.append(f"- 窗口标题: {details.get('window_title')}")
                script_lines.append("```bash")
                script_lines.append(f'window_tool maximize "{details.get("window_title")}"')
                script_lines.append("```")
            elif op_type == "scroll":
                script_lines.append(f"### 步骤 {i}: 滚动屏幕")
                script_lines.append(f"- 时间: {timestamp}")
                script_lines.append(f"- 滚动量: {details.get('delta')}")
                if 'x' in details:
                    script_lines.append(f"- 位置: ({details.get('x')}, {details.get('y')})")
                script_lines.append("```bash")
                script_lines.append(f"mouse_tool scroll {details.get('delta')}")
                script_lines.append("```")
            elif op_type == "screenshot":
                script_lines.append(f"### 步骤 {i}: 截图")
                script_lines.append(f"- 时间: {timestamp}")
                if details.get("description"):
                    script_lines.append(f"- 描述: {details.get('description')}")
                script_lines.append("```bash")
                script_lines.append("screenshot_tool")
                script_lines.append("```")

            script_lines.append("")

        script_content = "\n".join(script_lines)

        # 保存演示脚本
        demo_file = os.path.join(STATE_DIR, 'operation_demo.md')
        with open(demo_file, 'w', encoding='utf-8') as f:
            f.write(script_content)

        return {
            "status": "success",
            "message": f"已生成演示脚本: {demo_file}",
            "demo_file": demo_file,
            "step_count": len(operations)
        }

    def playback_operations(self, file_path: str = None, delay: float = 0.5) -> Dict[str, Any]:
        """回放录制的操作序列"""
        load_result = self.load_recording(file_path)
        if load_result.get("status") != "success":
            return load_result

        recording = load_result["data"]
        operations = recording.get("operations", [])

        if not operations:
            return {"status": "error", "message": "没有可回放的操作"}

        results = []
        for op in operations:
            op_type = op.get("type")
            details = op.get("details", {})

            result = {"type": op_type, "details": details}
            try:
                if op_type == "click":
                    # 使用 mouse_tool 点击
                    import subprocess
                    x, y = details.get("x"), details.get("y")
                    subprocess.run([
                        sys.executable,
                        os.path.join(SCRIPT_DIR, "mouse_tool.py"),
                        "click", str(x), str(y)
                    ], capture_output=True)
                    result["status"] = "success"

                elif op_type == "type":
                    import subprocess
                    text = details.get("text", "")
                    subprocess.run([
                        sys.executable,
                        os.path.join(SCRIPT_DIR, "keyboard_tool.py"),
                        "type", text
                    ], capture_output=True)
                    result["status"] = "success"

                elif op_type == "key":
                    import subprocess
                    key = details.get("key", "")
                    vk = details.get("vk")
                    if vk:
                        subprocess.run([
                            sys.executable,
                            os.path.join(SCRIPT_DIR, "keyboard_tool.py"),
                            "key", str(vk)
                        ], capture_output=True)
                    else:
                        subprocess.run([
                            sys.executable,
                            os.path.join(SCRIPT_DIR, "keyboard_tool.py"),
                            "key", key
                        ], capture_output=True)
                    result["status"] = "success"

                elif op_type == "activate":
                    import subprocess
                    title = details.get("window_title", "")
                    subprocess.run([
                        sys.executable,
                        os.path.join(SCRIPT_DIR, "window_tool.py"),
                        "activate", title
                    ], capture_output=True)
                    result["status"] = "success"

                elif op_type == "maximize":
                    import subprocess
                    title = details.get("window_title", "")
                    subprocess.run([
                        sys.executable,
                        os.path.join(SCRIPT_DIR, "window_tool.py"),
                        "maximize", title
                    ], capture_output=True)
                    result["status"] = "success"

                elif op_type == "scroll":
                    import subprocess
                    delta = details.get("delta", 120)
                    subprocess.run([
                        sys.executable,
                        os.path.join(SCRIPT_DIR, "mouse_tool.py"),
                        "scroll", str(delta)
                    ], capture_output=True)
                    result["status"] = "success"

                elif op_type == "screenshot":
                    import subprocess
                    subprocess.run([
                        sys.executable,
                        os.path.join(SCRIPT_DIR, "screenshot_tool.py")
                    ], capture_output=True)
                    result["status"] = "success"

            except Exception as e:
                result["status"] = "error"
                result["error"] = str(e)

            results.append(result)
            time.sleep(delay)

        success_count = sum(1 for r in results if r.get("status") == "success")
        return {
            "status": "completed",
            "message": f"回放完成: {success_count}/{len(operations)} 成功",
            "results": results
        }


def main():
    """CLI 入口"""
    if len(sys.argv) < 2:
        print("""智能操作演示与回放引擎

用法:
  python operation_recorder.py start           - 开始录制
  python operation_recorder.py stop            - 停止录制
  python operation_recorder.py status           - 查看录制状态
  python operation_recorder.py convert [文件]   - 转换为 run_plan
  python operation_recorder.py demo [文件]     - 生成演示脚本
  python operation_recorder.py play [文件]     - 回放操作
  python operation_recorder.py load [文件]     - 加载录制内容
""")
        return

    recorder = OperationRecorder()
    command = sys.argv[1]

    if command == "start":
        result = recorder.start_recording()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "stop":
        result = recorder.stop_recording()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "status":
        result = recorder.get_recording_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "convert":
        file_path = sys.argv[2] if len(sys.argv) > 2 else None
        result = recorder.convert_to_run_plan(file_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "demo":
        file_path = sys.argv[2] if len(sys.argv) > 2 else None
        result = recorder.generate_demo_script(file_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "play":
        file_path = sys.argv[2] if len(sys.argv) > 2 else None
        result = recorder.playback_operations(file_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "load":
        file_path = sys.argv[2] if len(sys.argv) > 2 else None
        result = recorder.load_recording(file_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {command}")


if __name__ == "__main__":
    main()