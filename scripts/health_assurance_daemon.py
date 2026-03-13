#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
健康保障守护进程 (Health Assurance Daemon)
作为守护进程在后台持续运行，定期执行健康保障闭环。

功能：
- 周期性执行健康扫描（默认 5 分钟）
- 自动执行优化和修复
- 记录执行历史
- 与守护进程管理器集成

用法：
    python health_assurance_daemon.py              # 守护进程模式运行
    python health_assurance_daemon.py --interval 300  # 自定义间隔（秒）
    python health_assurance_daemon.py --run-once      # 只运行一次
"""

import os
import sys
import json
import time
import signal
import logging
import argparse
import threading
from datetime import datetime, timezone
from pathlib import Path

# 配置路径
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
LOG_DIR = PROJECT_ROOT / "runtime" / "logs"
STATE_DIR = PROJECT_ROOT / "runtime" / "state"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "health_assurance_daemon.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("health_assurance_daemon")

# 状态文件
DAEMON_STATE_FILE = STATE_DIR / "health_assurance_daemon_state.json"

# 导入健康保障闭环引擎
sys.path.insert(0, str(SCRIPT_DIR))

try:
    from health_assurance_loop import HealthAssuranceLoop, get_system_metrics
    HEALTH_ASSURANCE_AVAILABLE = True
except ImportError:
    HEALTH_ASSURANCE_AVAILABLE = False
    logger.warning("无法导入健康保障闭环引擎")


class HealthAssuranceDaemon:
    """健康保障守护进程"""

    def __init__(self, interval: int = 300, auto_execute: bool = True):
        """
        初始化守护进程

        Args:
            interval: 执行间隔（秒），默认 5 分钟
            auto_execute: 是否自动执行优化和修复
        """
        self.interval = interval
        self.auto_execute = auto_execute
        self.running = False
        self.engine = HealthAssuranceLoop() if HEALTH_ASSURANCE_AVAILABLE else None
        self._load_state()

    def _load_state(self):
        """加载守护进程状态"""
        if DAEMON_STATE_FILE.exists():
            try:
                with open(DAEMON_STATE_FILE, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    self.state = state
                    logger.info(f"已加载守护进程状态: {state.get('total_loops', 0)} 次循环")
            except Exception as e:
                logger.error(f"加载状态失败: {e}")
                self._init_state()
        else:
            self._init_state()

    def _init_state(self):
        """初始化状态"""
        self.state = {
            "running": False,
            "start_time": None,
            "last_run": None,
            "total_loops": 0,
            "issues_detected": 0,
            "fixes_applied": 0,
            "optimizations_executed": 0,
            "errors": []
        }
        self._save_state()

    def _save_state(self):
        """保存守护进程状态"""
        try:
            STATE_DIR.mkdir(parents=True, exist_ok=True)
            with open(DAEMON_STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存状态失败: {e}")

    def get_status(self) -> dict:
        """获取守护进程状态"""
        # 获取最新系统指标
        metrics = get_system_metrics() if HEALTH_ASSURANCE_AVAILABLE else {}

        return {
            "daemon": "health_assurance",
            "running": self.running,
            "interval": self.interval,
            "auto_execute": self.auto_execute,
            "start_time": self.state.get("start_time"),
            "last_run": self.state.get("last_run"),
            "total_loops": self.state.get("total_loops", 0),
            "issues_detected": self.state.get("issues_detected", 0),
            "fixes_applied": self.state.get("fixes_applied", 0),
            "optimizations_executed": self.state.get("optimizations_executed", 0),
            "system_metrics": metrics
        }

    def execute_loop(self) -> dict:
        """执行一次健康保障闭环"""
        if not self.engine:
            logger.error("健康保障引擎不可用")
            return {"success": False, "error": "Engine not available"}

        loop_result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "success": True
        }

        try:
            # 执行完整闭环
            result = self.engine.full_loop(auto_execute=self.auto_execute)

            # 更新状态
            self.state["last_run"] = loop_result["timestamp"]
            self.state["total_loops"] += 1
            self.state["issues_detected"] += len(result.get("issues_detected", []))
            self.state["fixes_applied"] += len(result.get("fixes_applied", []))
            self.state["optimizations_executed"] += len(result.get("optimizations_executed", []))

            loop_result.update({
                "issues_detected": len(result.get("issues_detected", [])),
                "fixes_applied": len(result.get("fixes_applied", [])),
                "optimizations": len(result.get("optimizations_executed", []))
            })

            # 获取系统指标
            metrics = get_system_metrics()
            loop_result["metrics_after"] = metrics

            logger.info(f"健康保障闭环完成: 发现 {loop_result['issues_detected']} 个问题, "
                       f"修复 {loop_result['fixes_applied']} 个, 执行 {loop_result['optimizations']} 项优化")

        except Exception as e:
            logger.error(f"执行健康保障闭环失败: {e}")
            loop_result["success"] = False
            loop_result["error"] = str(e)
            self.state["errors"].append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(e)
            })

        self._save_state()
        return loop_result

    def run(self):
        """守护进程主循环"""
        logger.info(f"健康保障守护进程启动，间隔: {self.interval} 秒")

        self.running = True
        self.state["running"] = True
        self.state["start_time"] = datetime.now(timezone.utc).isoformat()
        self._save_state()

        # 启动时立即执行一次
        logger.info("执行首次健康保障闭环...")
        self.execute_loop()

        # 周期性执行
        while self.running:
            try:
                time.sleep(self.interval)
                if self.running:
                    logger.info("执行周期性健康保障闭环...")
                    self.execute_loop()
            except Exception as e:
                logger.error(f"守护进程循环异常: {e}")
                time.sleep(60)  # 出错后等待一分钟后重试

        logger.info("健康保障守护进程已停止")

    def stop(self):
        """停止守护进程"""
        logger.info("正在停止健康保障守护进程...")
        self.running = False
        self.state["running"] = False
        self._save_state()

    def signal_handler(self, signum, frame):
        """信号处理"""
        logger.info(f"接收到信号 {signum}，停止守护进程")
        self.stop()
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="健康保障守护进程")
    parser.add_argument("--interval", type=int, default=300,
                        help="执行间隔（秒），默认 300 秒（5 分钟）")
    parser.add_argument("--no-auto", action="store_true",
                        help="不自动执行优化和修复")
    parser.add_argument("--run-once", action="store_true",
                        help="只运行一次，不持续运行")
    parser.add_argument("--status", action="store_true",
                        help="查看守护进程状态")

    args = parser.parse_args()

    # 设置信号处理
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))

    if args.status:
        # 查看状态
        if DAEMON_STATE_FILE.exists():
            with open(DAEMON_STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
                print(json.dumps(state, ensure_ascii=False, indent=2))
        else:
            print("守护进程尚未运行")
        return

    # 创建并启动守护进程
    daemon = HealthAssuranceDaemon(
        interval=args.interval,
        auto_execute=not args.no_auto
    )

    if args.run_once:
        # 只运行一次
        result = daemon.execute_loop()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 守护进程模式
        daemon.run()


if __name__ == "__main__":
    main()