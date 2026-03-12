#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进化环统一 CLI 入口 - 提供一站式的进化环操作体验

功能：
1. 统一所有进化模块的 CLI 接口
2. 提供友好的命令行交互体验
3. 支持状态查看、运行分析、调度控制等
4. 与 do.py 深度集成

使用方法：
    python evolution_cli.py status           - 查看整体进化状态
    python evolution_cli.py analyze          - 运行进化分析
    python evolution_cli.py run              - 执行完整进化流程
    python evolution_cli.py scheduler        - 管理定时任务
    python evolution_cli.py history          - 查看进化历史
    python evolution_cli.py health           - 检查各模块健康度
    python evolution_cli.py dashboard        - 启动可视化面板
    python evolution_cli.py --help           - 显示帮助信息
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# 解决 Windows 控制台中文编码问题
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE = PROJECT_ROOT / "runtime" / "state"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# 确保目录存在
RUNTIME_STATE.mkdir(parents=True, exist_ok=True)


def load_json_file(filepath: Path) -> Dict[str, Any]:
    """加载 JSON 文件"""
    if filepath.exists():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def run_module(script_name: str, command: str = "") -> Dict[str, Any]:
    """运行指定的进化模块脚本"""
    script_path = SCRIPTS_DIR / script_name

    if not script_path.exists():
        return {"error": f"模块不存在: {script_name}"}

    try:
        cmd = [sys.executable, str(script_path)]
        if command:
            cmd.append(command)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        # 解析 JSON 输出
        output = result.stdout.strip()
        if output.startswith('{'):
            return json.loads(output)
        else:
            # 非 JSON 输出，尝试提取 JSON 部分
            json_start = output.find('{')
            if json_start != -1:
                try:
                    return json.loads(output[json_start:])
                except:
                    return {"raw_output": output, "returncode": result.returncode}
            return {"raw_output": output, "returncode": result.returncode}
    except subprocess.TimeoutExpired:
        return {"error": "模块执行超时"}
    except Exception as e:
        return {"error": str(e)}


def cmd_status(args) -> None:
    """查看整体进化状态"""
    print("=" * 60)
    print("🧬 进化环整体状态")
    print("=" * 60)

    # 读取 current_mission
    mission = load_json_file(RUNTIME_STATE / "current_mission.json")
    if mission:
        print(f"\n当前轮次: Round {mission.get('loop_round', 'N/A')}")
        print(f"当前阶段: {mission.get('phase', 'N/A')}")
        print(f"当前目标: {mission.get('current_goal', 'N/A')}")
        print(f"下一步: {mission.get('next_action', 'N/A')}")
    else:
        print("\n无法获取当前任务状态")

    # 检查各模块健康度
    print("\n📊 模块健康度检查:")
    modules = [
        ("strategy", "evolution_strategy_engine.py"),
        ("analyzer", "evolution_log_analyzer.py"),
        ("evaluator", "evolution_self_evaluator.py"),
        ("automation", "evolution_loop_automation.py"),
        ("history", "evolution_history_db.py"),
        ("learning", "evolution_learning_engine.py"),
        ("coordinator", "evolution_coordinator.py"),
        ("dashboard", "evolution_dashboard.py"),
        ("scheduler", "evolution_scheduler.py"),
    ]

    healthy_count = 0
    for name, script in modules:
        script_path = SCRIPTS_DIR / script
        status = "✅ 正常" if script_path.exists() else "❌ 缺失"
        if script_path.exists():
            healthy_count += 1
        print(f"  {name:12s}: {status}")

    print(f"\n健康度: {healthy_count}/{len(modules)} 模块正常")

    # 进化统计
    completed_files = list(RUNTIME_STATE.glob("evolution_completed_*.json"))
    print(f"\n已完成进化轮次: {len(completed_files)}")

    print("\n" + "=" * 60)


def cmd_analyze(args) -> None:
    """运行进化分析"""
    print("🔍 正在运行进化分析...")

    result = run_module("evolution_log_analyzer.py")
    if "error" in result:
        print(f"❌ 分析失败: {result['error']}")
    else:
        print("✅ 分析完成")
        if result.get("summary"):
            print(f"\n摘要: {result['summary']}")

    # 同时运行策略分析
    print("\n🎯 运行策略分析...")
    strategy_result = run_module("evolution_strategy_engine.py")
    if "error" in strategy_result:
        print(f"⚠️ 策略分析: {strategy_result['error']}")
    else:
        print("✅ 策略分析完成")


def cmd_run(args) -> None:
    """执行完整进化流程"""
    print("🚀 正在执行完整进化流程...")

    # 使用协调器执行
    result = run_module("evolution_coordinator.py", "run")
    if "error" in result:
        print(f"❌ 执行失败: {result['error']}")
    else:
        print("✅ 进化流程执行完成")
        if result.get("status"):
            print(f"状态: {result['status']}")


def cmd_scheduler(args) -> None:
    """管理定时任务"""
    if args.start:
        print("⏰ 启动定时进化任务...")
        result = run_module("evolution_scheduler.py", "start")
        print(result.get("message", "已启动"))
    elif args.stop:
        print("⏹️ 停止定时进化任务...")
        result = run_module("evolution_scheduler.py", "stop")
        print(result.get("message", "已停止"))
    elif args.status:
        result = run_module("evolution_scheduler.py", "status")
        if "error" in result:
            print(f"状态: {result.get('status', '未知')}")
        else:
            print(f"定时任务状态: {result.get('status', '未知')}")
    else:
        print("请指定: --start, --stop, 或 --status")


def cmd_history(args) -> None:
    """查看进化历史"""
    print("📜 进化历史记录:")
    print("-" * 40)

    completed_files = sorted(RUNTIME_STATE.glob("evolution_completed_*.json"), reverse=True)

    if not completed_files:
        print("暂无进化记录")
        return

    limit = args.limit if hasattr(args, 'limit') else 10
    for i, f in enumerate(completed_files[:limit]):
        data = load_json_file(f)
        round_num = data.get('loop_round', 'N/A')
        goal = data.get('current_goal', 'N/A')[:40]
        status = "✅" if data.get('completed') else "❌"
        print(f"{status} Round {round_num}: {goal}")

    if len(completed_files) > limit:
        print(f"\n... 共 {len(completed_files)} 条记录")

    print("-" * 40)


def cmd_health(args) -> None:
    """检查各模块健康度"""
    print("🏥 进化模块健康检查:")
    print("-" * 40)

    modules = [
        ("策略引擎", "evolution_strategy_engine.py"),
        ("日志分析", "evolution_log_analyzer.py"),
        ("自我评估", "evolution_self_evaluator.py"),
        ("自动化", "evolution_loop_automation.py"),
        ("历史数据库", "evolution_history_db.py"),
        ("学习引擎", "evolution_learning_engine.py"),
        ("协调器", "evolution_coordinator.py"),
        ("监控面板", "evolution_dashboard.py"),
        ("定时器", "evolution_scheduler.py"),
        ("CLI入口", "evolution_cli.py"),
    ]

    for name, script in modules:
        script_path = SCRIPTS_DIR / script
        exists = script_path.exists()
        size = script_path.stat().st_size if exists else 0
        status = "✅" if exists else "❌"
        print(f"{status} {name:10s}: {script} ({size} bytes)" if exists else f"{status} {name:10s}: {script} [不存在]")

    print("-" * 40)


def cmd_dashboard(args) -> None:
    """启动可视化面板"""
    print("📊 启动进化监控面板...")
    result = run_module("evolution_dashboard.py")

    if "error" in result:
        print(f"❌ 启动失败: {result['error']}")
    else:
        print("✅ 面板已启动")
        print(f"输出文件: {result.get('output_file', 'N/A')}")


def cmd_learn(args) -> None:
    """运行学习引擎"""
    print("🧠 运行进化学习引擎...")
    result = run_module("evolution_learning_engine.py")

    if "error" in result:
        print(f"❌ 学习失败: {result['error']}")
    else:
        print("✅ 学习完成")
        if result.get("insights"):
            print(f"\n洞察: {result['insights']}")


def cmd_evaluate(args) -> None:
    """运行自我评估"""
    print("📈 运行进化自我评估...")
    result = run_module("evolution_self_evaluator.py")

    if "error" in result:
        print(f"❌ 评估失败: {result['error']}")
    else:
        print("✅ 评估完成")
        if result.get("health_score"):
            print(f"\n健康分数: {result['health_score']}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="🧬 进化环统一 CLI 入口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python evolution_cli.py status           查看整体状态
  python evolution_cli.py analyze          运行进化分析
  python evolution_cli.py run              执行完整进化流程
  python evolution_cli.py health            检查模块健康度
  python evolution_cli.py history           查看进化历史
  python evolution_cli.py scheduler --status 查看定时任务状态
  python evolution_cli.py dashboard        启动监控面板
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # status 命令
    subparsers.add_parser("status", help="查看整体进化状态")

    # analyze 命令
    subparsers.add_parser("analyze", help="运行进化分析")

    # run 命令
    subparsers.add_parser("run", help="执行完整进化流程")

    # scheduler 命令
    scheduler_parser = subparsers.add_parser("scheduler", help="管理定时任务")
    scheduler_parser.add_argument("--start", action="store_true", help="启动定时任务")
    scheduler_parser.add_argument("--stop", action="store_true", help="停止定时任务")
    scheduler_parser.add_argument("--status", action="store_true", help="查看定时任务状态")

    # history 命令
    history_parser = subparsers.add_parser("history", help="查看进化历史")
    history_parser.add_argument("--limit", type=int, default=10, help="显示记录数")

    # health 命令
    subparsers.add_parser("health", help="检查各模块健康度")

    # dashboard 命令
    subparsers.add_parser("dashboard", help="启动可视化面板")

    # learn 命令
    subparsers.add_parser("learn", help="运行学习引擎")

    # evaluate 命令
    subparsers.add_parser("evaluate", help="运行自我评估")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # 执行对应命令
    command_map = {
        "status": cmd_status,
        "analyze": cmd_analyze,
        "run": cmd_run,
        "scheduler": cmd_scheduler,
        "history": cmd_history,
        "health": cmd_health,
        "dashboard": cmd_dashboard,
        "learn": cmd_learn,
        "evaluate": cmd_evaluate,
    }

    command_map[args.command](args)


if __name__ == "__main__":
    main()