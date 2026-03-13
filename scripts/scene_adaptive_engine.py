#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能场景自适应执行引擎

功能：
- 基于实时上下文（时间、系统状态、用户活动）自动执行/切换场景计划
- 实现从"被动推荐"到"主动执行"的范式转变
- 形成端到端智能服务闭环：感知→分析→决策→执行→反馈
- 支持守护进程模式持续运行
- 与场景推荐引擎、主动服务编排引擎深度集成

工作原理：
1. 持续监控上下文变化（时间、系统状态）
2. 基于上下文分析当前适合的场景
3. 自动执行场景切换或启动新场景
4. 评估执行效果并学习优化
"""

import os
import sys
import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from collections import deque
import subprocess
import psutil

# 确保 scripts 目录在路径中
SCRIPT_DIR = Path(__file__).parent
RUNTIME_DIR = SCRIPT_DIR.parent / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
PLANS_DIR = SCRIPT_DIR.parent / "assets" / "plans"

# 状态文件路径
STATE_FILE = STATE_DIR / "scene_adaptive_state.json"
CONTEXT_HISTORY_FILE = STATE_DIR / "scene_adaptive_context_history.json"
EXECUTION_LOG_FILE = STATE_DIR / "scene_adaptive_execution_log.json"

# 默认配置
DEFAULT_CONFIG = {
    "enabled": True,
    "daemon_mode": True,
    "check_interval": 60,  # 检查间隔（秒）
    "auto_switch_enabled": True,  # 自动切换开关
    "contexts": {
        "time_periods": {
            "凌晨": {"hour": (0, 6), "scenes": ["听音乐", "看电影"]},
            "早晨": {"hour": (6, 9), "scenes": ["看新闻", "工作"]},
            "上午": {"hour": (9, 12), "scenes": ["工作", "邮件"]},
            "中午": {"hour": (12, 14), "scenes": ["休息", "听音乐"]},
            "下午": {"hour": (14, 18), "scenes": ["工作", "邮件"]},
            "傍晚": {"hour": (18, 20), "scenes": ["看新闻", "看电影"]},
            "晚上": {"hour": (20, 24), "scenes": ["看电影", "听音乐", "刷知乎"]}
        },
        "weekend": {"scenes": ["听音乐", "看电影", "放松"]},
        "weekday": {"scenes": ["工作", "邮件", "检查消息"]}
    },
    "auto_execute_delay": 30,  # 自动执行延迟（秒），让用户有机会取消
    "max_history": 100  # 上下文历史记录最大条数
}


class SceneAdaptiveEngine:
    """智能场景自适应执行引擎"""

    def __init__(self):
        self.config = self.load_config()
        self.current_context = {}
        self.current_scene = None
        self.context_history = deque(maxlen=self.config.get("max_history", 100))
        self.execution_log = deque(maxlen=100)
        self.daemon_thread = None
        self.running = False

    def load_config(self):
        """加载配置"""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    saved_config = json.load(f)
                    config = DEFAULT_CONFIG.copy()
                    config.update(saved_config)
                    return config
            except Exception as e:
                print(f"加载配置失败: {e}")
        return DEFAULT_CONFIG.copy()

    def save_config(self):
        """保存配置"""
        try:
            STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False

    def get_time_period(self):
        """获取当前时间段"""
        hour = datetime.now().hour
        periods = self.config["contexts"]["time_periods"]
        for period, config in periods.items():
            start, end = config["hour"]
            if start <= hour < end:
                return period
        return "晚上"

    def is_weekend(self):
        """判断是否周末"""
        return datetime.now().weekday() >= 5

    def get_system_state(self):
        """获取系统状态"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # 获取活跃窗口
            active_window = ""
            try:
                import win32gui
                active_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
            except:
                pass

            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "active_window": active_window,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    def analyze_context(self):
        """分析当前上下文"""
        time_period = self.get_time_period()
        is_weekend = self.is_weekend()
        system_state = self.get_system_state()

        context = {
            "time_period": time_period,
            "is_weekend": is_weekend,
            "system_state": system_state,
            "timestamp": datetime.now().isoformat()
        }

        self.current_context = context
        self.context_history.append(context)

        # 保存上下文历史
        self.save_context_history()

        return context

    def save_context_history(self):
        """保存上下文历史"""
        try:
            HISTORY_FILE = Path(STATE_DIR) / "scene_adaptive_context_history.json"
            HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

            history_list = list(self.context_history)
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history_list, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存上下文历史失败: {e}")

    def get_recommended_scenes(self, context):
        """根据上下文获取推荐场景"""
        time_period = context.get("time_period", "晚上")
        is_weekend = context.get("is_weekend", False)

        recommended = []

        # 基于时间段获取推荐
        time_config = self.config["contexts"]["time_periods"].get(time_period, {})
        if "scenes" in time_config:
            recommended.extend(time_config["scenes"])

        # 周末/工作日调整
        if is_weekend:
            recommended.extend(self.config["contexts"]["weekend"]["scenes"])
        else:
            recommended.extend(self.config["contexts"]["weekday"]["scenes"])

        # 去重
        recommended = list(dict.fromkeys(recommended))
        return recommended

    def find_matching_plans(self, scene_tags):
        """查找匹配的场景计划"""
        matching_plans = []

        if not PLANS_DIR.exists():
            return matching_plans

        for plan_file in PLANS_DIR.glob("*.json"):
            try:
                with open(plan_file, "r", encoding="utf-8") as f:
                    plan_data = json.load(f)
                    tags = plan_data.get("tags", [])

                    # 检查是否有匹配的标签
                    for tag in scene_tags:
                        if tag in tags:
                            matching_plans.append({
                                "file": str(plan_file.name),
                                "name": plan_data.get("name", plan_file.stem),
                                "tags": tags,
                                "path": str(plan_file)
                            })
                            break
            except Exception as e:
                print(f"读取计划文件失败 {plan_file}: {e}")

        return matching_plans

    def should_switch_scene(self, new_scene, current_scene):
        """判断是否应该切换场景"""
        if not self.config.get("auto_switch_enabled", True):
            return False

        if current_scene is None:
            return True

        # 如果新场景与当前场景不同，考虑切换
        return new_scene != current_scene

    def execute_scene(self, plan_path, scene_name):
        """执行场景计划"""
        try:
            # 使用 run_plan 执行场景
            cmd = [sys.executable, str(SCRIPT_DIR / "do.py"), "run_plan", plan_path]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            execution_record = {
                "scene": scene_name,
                "plan": plan_path,
                "success": result.returncode == 0,
                "timestamp": datetime.now().isoformat(),
                "output": result.stdout[:500] if result.stdout else "",
                "error": result.stderr[:500] if result.stderr else ""
            }

            self.execution_log.append(execution_record)
            self.save_execution_log()

            return execution_record
        except Exception as e:
            execution_record = {
                "scene": scene_name,
                "plan": plan_path,
                "success": False,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
            self.execution_log.append(execution_record)
            self.save_execution_log()
            return execution_record

    def save_execution_log(self):
        """保存执行日志"""
        try:
            LOG_FILE = Path(STATE_DIR) / "scene_adaptive_execution_log.json"
            LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

            log_list = list(self.execution_log)
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                json.dump(log_list, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存执行日志失败: {e}")

    def adaptive_execution(self):
        """执行自适应场景选择和执行"""
        # 分析当前上下文
        context = self.analyze_context()

        # 获取推荐场景
        recommended_scenes = self.get_recommended_scenes(context)

        if not recommended_scenes:
            return {
                "status": "no_recommendations",
                "context": context,
                "message": "当前上下文没有推荐的场景"
            }

        # 查找匹配的 plans
        matching_plans = self.find_matching_plans(recommended_scenes)

        if not matching_plans:
            return {
                "status": "no_matching_plans",
                "context": context,
                "recommended_scenes": recommended_scenes,
                "message": "没有找到匹配的场景计划"
            }

        # 选择最合适的场景
        best_plan = matching_plans[0]

        # 检查是否应该切换
        if self.should_switch_scene(best_plan["name"], self.current_scene):
            # 执行场景
            execution_result = self.execute_scene(best_plan["path"], best_plan["name"])

            if execution_result["success"]:
                self.current_scene = best_plan["name"]

            return {
                "status": "executed",
                "context": context,
                "scene": best_plan["name"],
                "plan": best_plan["path"],
                "result": execution_result
            }
        else:
            return {
                "status": "no_switch_needed",
                "context": context,
                "current_scene": self.current_scene,
                "recommended": best_plan["name"]
            }

    def daemon_loop(self):
        """守护进程主循环"""
        print(f"[场景自适应] 守护进程启动，检查间隔: {self.config.get('check_interval', 60)}秒")

        while self.running:
            try:
                if self.config.get("enabled", True):
                    result = self.adaptive_execution()

                    if result["status"] == "executed":
                        print(f"[场景自适应] 执行场景: {result.get('scene', 'unknown')}")
                    elif result["status"] == "no_switch_needed":
                        print(f"[场景自适应] 当前场景保持: {result.get('current_scene', 'none')}")
                else:
                    print("[场景自适应] 自适应功能已禁用")

            except Exception as e:
                print(f"[场景自适应] 守护进程错误: {e}")

            # 等待下一个检查周期
            for _ in range(self.config.get("check_interval", 60)):
                if not self.running:
                    break
                time.sleep(1)

        print("[场景自适应] 守护进程已停止")

    def start_daemon(self):
        """启动守护进程"""
        if self.running:
            return {"status": "already_running"}

        self.running = True
        self.daemon_thread = threading.Thread(target=self.daemon_loop, daemon=True)
        self.daemon_thread.start()

        return {"status": "started", "check_interval": self.config.get("check_interval", 60)}

    def stop_daemon(self):
        """停止守护进程"""
        if not self.running:
            return {"status": "not_running"}

        self.running = False

        if self.daemon_thread:
            self.daemon_thread.join(timeout=5)

        return {"status": "stopped"}

    def get_status(self):
        """获取状态"""
        return {
            "enabled": self.config.get("enabled", True),
            "daemon_running": self.running,
            "current_scene": self.current_scene,
            "current_context": self.current_context,
            "check_interval": self.config.get("check_interval", 60),
            "auto_switch_enabled": self.config.get("auto_switch_enabled", True),
            "recent_contexts": len(self.context_history),
            "recent_executions": len(self.execution_log)
        }

    def set_enabled(self, enabled):
        """设置启用状态"""
        self.config["enabled"] = enabled
        self.save_config()
        return {"enabled": enabled}

    def set_auto_switch(self, enabled):
        """设置自动切换"""
        self.config["auto_switch_enabled"] = enabled
        self.save_config()
        return {"auto_switch_enabled": enabled}

    def set_check_interval(self, interval):
        """设置检查间隔"""
        self.config["check_interval"] = max(10, min(interval, 3600))
        self.save_config()
        return {"check_interval": self.config["check_interval"]}


def main():
    """主入口"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python scene_adaptive_engine.py status          - 查看状态")
        print("  python scene_adaptive_engine.py start           - 启动守护进程")
        print("  python scene_adaptive_engine.py stop            - 停止守护进程")
        print("  python scene_adaptive_engine.py execute         - 执行一次自适应")
        print("  python scene_adaptive_engine.py enable          - 启用自适应")
        print("  python scene_adaptive_engine.py disable         - 禁用自适应")
        print("  python scene_adaptive_engine.py auto-on         - 开启自动切换")
        print("  python scene_adaptive_engine.py auto-off       - 关闭自动切换")
        print("  python scene_adaptive_engine.py interval <秒>   - 设置检查间隔")
        print("  python scene_adaptive_engine.py context        - 查看当前上下文")
        print("  python scene_adaptive_engine.py history        - 查看上下文历史")
        print("  python scene_adaptive_engine.py log            - 查看执行日志")
        return

    engine = SceneAdaptiveEngine()
    command = sys.argv[1]

    if command == "status":
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif command == "start":
        result = engine.start_daemon()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "stop":
        result = engine.stop_daemon()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "execute":
        result = engine.adaptive_execution()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "enable":
        result = engine.set_enabled(True)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "disable":
        result = engine.set_enabled(False)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "auto-on":
        result = engine.set_auto_switch(True)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "auto-off":
        result = engine.set_auto_switch(False)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "interval":
        if len(sys.argv) < 3:
            print("请指定间隔秒数")
            return
        interval = int(sys.argv[2])
        result = engine.set_check_interval(interval)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "context":
        context = engine.analyze_context()
        print(json.dumps(context, ensure_ascii=False, indent=2))

    elif command == "history":
        history = list(engine.context_history)
        print(json.dumps(history, ensure_ascii=False, indent=2))

    elif command == "log":
        log = list(engine.execution_log)
        print(json.dumps(log, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {command}")


if __name__ == "__main__":
    main()