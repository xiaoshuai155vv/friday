#!/usr/bin/env python3
"""
进化环 REST API 服务

将进化环功能通过 HTTP API 暴露，支持外部系统调用
为 Web 界面和定时任务提供后端支持

功能：
1. 提供 REST API 访问进化环状态和数据
2. 支持健康检查、状态查询、模块管理
3. 可触发进化环执行
4. 集成现有进化模块功能

使用方法：
    python evolution_api_server.py [--port 8080] [--host 0.0.0.0]
    python evolution_api_server.py --daemon  # 后台运行

API 端点：
    GET  /                     - 欢迎信息
    GET  /api/health           - 健康检查
    GET  /api/status           - 获取进化环状态
    GET  /api/modules          - 获取所有模块状态
    GET  /api/dashboard        - 获取监控面板数据
    GET  /api/history          - 获取进化历史
    GET  /api/strategy         - 获取策略分析
    GET  /api/evaluate         - 获取评估结果
    POST /api/run              - 触发进化环执行
"""

import json
import os
import sys
import subprocess
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Any, Dict, Optional
import argparse
import socketserver

# 添加 scripts 目录到路径
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPTS_DIR)
sys.path.insert(0, SCRIPTS_DIR)

# 定义路径常量
RUNTIME_DIR = os.path.join(PROJECT_ROOT, "runtime")
STATE_DIR = os.path.join(RUNTIME_DIR, "state")
LOGS_DIR = os.path.join(RUNTIME_DIR, "logs")

# 进化环相关文件路径
EVOLUTION_STATE_FILE = os.path.join(STATE_DIR, "current_mission.json")
EVOLUTION_AUTO_LAST = os.path.join(PROJECT_ROOT, "references/evolution_auto_last.md")
SELF_VERIFY_RESULT = os.path.join(STATE_DIR, "self_verify_result.json")
DASHBOARD_DATA = os.path.join(STATE_DIR, "evolution_dashboard.json")

# 模块路径
MODULE_PATHS = {
    "strategy_engine": os.path.join(SCRIPTS_DIR, "evolution_strategy_engine.py"),
    "log_analyzer": os.path.join(SCRIPTS_DIR, "evolution_log_analyzer.py"),
    "self_evaluator": os.path.join(SCRIPTS_DIR, "evolution_self_evaluator.py"),
    "loop_automation": os.path.join(SCRIPTS_DIR, "evolution_loop_automation.py"),
    "history_db": os.path.join(SCRIPTS_DIR, "evolution_history_db.py"),
    "learning_engine": os.path.join(SCRIPTS_DIR, "evolution_learning_engine.py"),
    "coordinator": os.path.join(SCRIPTS_DIR, "evolution_coordinator.py"),
    "scheduler": os.path.join(SCRIPTS_DIR, "evolution_scheduler.py"),
    "dashboard": os.path.join(SCRIPTS_DIR, "evolution_dashboard.py"),
    "cli": os.path.join(SCRIPTS_DIR, "evolution_cli.py"),
}


class EvolutionAPIHandler(BaseHTTPRequestHandler):
    """进化环 API 请求处理器"""

    def _set_headers(self, status: int = 200, content_type: str = "application/json"):
        """设置响应头"""
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _read_json_body(self) -> Optional[Dict[str, Any]]:
        """读取 JSON 请求体"""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            body = self.rfile.read(content_length)
            return json.loads(body.decode("utf-8"))
        return None

    def _send_json_response(self, data: Dict[str, Any], status: int = 200):
        """发送 JSON 响应"""
        self._set_headers(status, "application/json")
        response = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response.encode("utf-8"))

    def _send_error(self, message: str, status: int = 500):
        """发送错误响应"""
        self._send_json_response({"error": message}, status)

    def _run_module(self, module_name: str, command: str = "status") -> Dict[str, Any]:
        """运行指定的进化模块"""
        if module_name not in MODULE_PATHS:
            return {"error": f"未知模块: {module_name}"}

        script_path = MODULE_PATHS[module_name]

        if not os.path.exists(script_path):
            return {"error": f"模块不存在: {script_path}"}

        try:
            result = subprocess.run(
                [sys.executable, script_path, command],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=SCRIPTS_DIR
            )

            # 解析 JSON 输出
            output = result.stdout.strip()
            if output.startswith("{"):
                return json.loads(output)
            else:
                # 非 JSON 输出，尝试提取 JSON 部分
                json_start = output.find("{")
                if json_start != -1:
                    return json.loads(output[json_start:])
                return {"raw_output": output, "returncode": result.returncode}

        except subprocess.TimeoutExpired:
            return {"error": f"模块执行超时: {module_name}"}
        except Exception as e:
            return {"error": str(e)}

    def do_GET(self):
        """处理 GET 请求"""
        path = self.path.split("?")[0]  # 去掉查询参数

        # 根路径
        if path == "/":
            self._set_headers()
            response = {
                "name": "Evolution API Server",
                "version": "1.0",
                "description": "Friday Evolution Ring REST API",
                "endpoints": [
                    "GET  /api/health           - Health check",
                    "GET  /api/status           - Current evolution status",
                    "GET  /api/modules          - All modules status",
                    "GET  /api/dashboard        - Dashboard data",
                    "GET  /api/history         - Evolution history",
                    "GET  /api/strategy         - Strategy analysis",
                    "GET  /api/evaluate         - Evaluation results",
                    "POST /api/run              - Trigger evolution cycle"
                ]
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False, indent=2).encode("utf-8"))
            return

        # 健康检查
        if path == "/api/health":
            self._send_json_response({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": "evolution_api_server"
            })
            return

        # 进化环状态
        if path == "/api/status":
            status = self._get_current_mission()
            self._send_json_response(status)
            return

        # 所有模块状态
        if path == "/api/modules":
            modules_status = self._get_modules_status()
            self._send_json_response(modules_status)
            return

        # 监控面板数据
        if path == "/api/dashboard":
            dashboard = self._get_dashboard_data()
            self._send_json_response(dashboard)
            return

        # 进化历史
        if path == "/api/history":
            history = self._get_evolution_history()
            self._send_json_response(history)
            return

        # 策略分析
        if path == "/api/strategy":
            strategy = self._run_module("strategy_engine", "analyze")
            self._send_json_response(strategy)
            return

        # 评估结果
        if path == "/api/evaluate":
            evaluation = self._run_module("self_evaluator", "evaluate")
            self._send_json_response(evaluation)
            return

        # 默认 404
        self._send_error(f"Not Found: {path}", 404)

    def do_POST(self):
        """处理 POST 请求"""
        path = self.path

        # 触发进化环执行
        if path == "/api/run":
            body = self._read_json_body() or {}
            mode = body.get("mode", "full")  # full, quick, analyze

            result = self._trigger_evolution(mode)
            self._send_json_response(result)
            return

        self._send_error(f"Unknown endpoint: {path}", 404)

    def do_OPTIONS(self):
        """处理 OPTIONS 请求（预检）"""
        self._set_headers(204)
        self.end_headers()

    def _get_current_mission(self) -> Dict[str, Any]:
        """获取当前任务状态"""
        if os.path.exists(EVOLUTION_STATE_FILE):
            try:
                with open(EVOLUTION_STATE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"phase": "unknown", "loop_round": 0, "current_goal": "unknown"}

    def _get_modules_status(self) -> Dict[str, Any]:
        """获取所有模块状态"""
        status = {"modules": {}, "summary": {}}

        available_count = 0
        for module_name, module_path in MODULE_PATHS.items():
            exists = os.path.exists(module_path)
            if exists:
                available_count += 1
                status["modules"][module_name] = {
                    "available": True,
                    "path": module_path
                }
            else:
                status["modules"][module_name] = {
                    "available": False,
                    "path": module_path
                }

        status["summary"] = {
            "total": len(MODULE_PATHS),
            "available": available_count,
            "timestamp": datetime.now().isoformat()
        }

        return status

    def _get_dashboard_data(self) -> Dict[str, Any]:
        """获取监控面板数据"""
        # 尝试读取已生成的 dashboard 数据
        if os.path.exists(DASHBOARD_DATA):
            try:
                with open(DASHBOARD_DATA, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        # 如果没有，生成新数据
        return {
            "generated_at": datetime.now().isoformat(),
            "current_mission": self._get_current_mission(),
            "modules_health": self._get_modules_status(),
            "note": "Data generated on demand"
        }

    def _get_evolution_history(self) -> Dict[str, Any]:
        """获取进化历史"""
        history = {"rounds": [], "count": 0}

        if os.path.exists(EVOLUTION_AUTO_LAST):
            try:
                with open(EVOLUTION_AUTO_LAST, "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")
                    current_round = {}

                    for line in lines:
                        if line.startswith("## 2026-"):
                            if current_round:
                                history["rounds"].append(current_round)
                            current_round = {}
                        elif line.startswith("- **current_goal**：") and current_round is not None:
                            current_round["goal"] = line.replace("- **current_goal**：", "").strip()
                        elif "- **做了什么**：" in line and current_round is not None:
                            current_round["action"] = line.split("：**做了什么**：")[1].strip() if "：**做了什么**：" in line else ""
                        elif "- **是否完成**：" in line and current_round is not None:
                            current_round["status"] = line.replace("- **是否完成**：", "").strip()

                    if current_round:
                        history["rounds"].append(current_round)

                history["count"] = len(history["rounds"])
            except Exception:
                pass

        return history

    def _trigger_evolution(self, mode: str = "full") -> Dict[str, Any]:
        """触发进化环执行"""
        result = {
            "triggered_at": datetime.now().isoformat(),
            "mode": mode,
            "status": "started"
        }

        try:
            if mode == "full":
                # 执行完整进化周期
                run_result = self._run_module("coordinator", "run")
                result["result"] = run_result
            elif mode == "analyze":
                # 只执行分析
                run_result = self._run_module("coordinator", "analyze")
                result["result"] = run_result
            else:
                # 快速模式 - 只更新状态
                result["result"] = {"message": "Quick mode - status updated"}

            result["status"] = "completed"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        return result

    def log_message(self, format, *args):
        """重写日志方法以减少输出"""
        pass  # 静默日志


class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    """支持多线程的 HTTP 服务器"""
    allow_reuse_address = True


def start_server(host: str = "0.0.0.0", port: int = 8080, daemon: bool = False):
    """启动 API 服务器"""
    server_address = (host, port)
    httpd = ThreadedHTTPServer(server_address, EvolutionAPIHandler)

    if daemon:
        # 后台运行模式
        import daemon
        with daemon.DaemonContext():
            print(f"Evolution API Server running on http://{host}:{port}")
            httpd.serve_forever()
    else:
        print(f"Evolution API Server running on http://{host}:{port}")
        print("Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.shutdown()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="进化环 REST API 服务")
    parser.add_argument("--host", default="0.0.0.0", help="Server host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8080, help="Server port (default: 8080)")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")

    args = parser.parse_args()

    start_server(args.host, args.port, args.daemon)


if __name__ == "__main__":
    main()