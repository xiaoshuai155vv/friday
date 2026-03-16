#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-OS 任务管理器模块 - 提供系统级任务管理能力

本模块提供 Windows 任务管理器级别的功能：
- 进程列表（带 CPU、内存使用率）
- 资源监控（CPU、内存、磁盘、网络）
- 进程详情
- 结束进程
- 服务管理（可选）

版本: 1.0.0
依赖: psutil, subprocess, platform
"""

import os
import sys
import json
import subprocess
import argparse
from datetime import datetime

# 尝试导入 psutil
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("警告: psutil 未安装，部分功能可能受限")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_process_list():
    """获取进程列表（带资源使用信息）"""
    if not PSUTIL_AVAILABLE:
        # 使用 process_tool 作为后备
        process_tool = os.path.join(SCRIPT_DIR, "process_tool.py")
        result = subprocess.run(
            [sys.executable, process_tool, "list"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.stdout

    processes = []
    try:
        # 尝试使用 attrs 参数（新版 psutil）
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                info = proc.info
                if isinstance(info, dict):
                    processes.append({
                        'pid': info.get('pid', 0),
                        'name': info.get('name', 'Unknown'),
                        'cpu_percent': info.get('cpu_percent', 0) or 0.0,
                        'memory_percent': info.get('memory_percent', 0) or 0.0,
                        'status': info.get('status', 'unknown')
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                pass
    except TypeError:
        # 旧版 psutil 不支持 attrs 参数，使用默认方式
        for proc in psutil.process_iter():
            try:
                proc_cpu = proc.cpu_percent(interval=0.01)
                proc_mem = proc.memory_percent()
                processes.append({
                    'pid': proc.pid,
                    'name': proc.name(),
                    'cpu_percent': proc_cpu or 0.0,
                    'memory_percent': proc_mem or 0.0,
                    'status': proc.status()
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

    # 按 CPU 使用率排序
    if processes and isinstance(processes[0], dict):
        processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)

    return processes


def get_process_details(pid):
    """获取指定进程的详细信息"""
    if not PSUTIL_AVAILABLE:
        return None

    try:
        proc = psutil.Process(pid)
        info = {
            'pid': proc.pid,
            'name': proc.name(),
            'status': proc.status(),
            'cpu_percent': proc.cpu_percent(interval=0.1),
            'memory_percent': proc.memory_percent(),
            'memory_info': proc.memory_info()._asdict(),
            'create_time': datetime.fromtimestamp(proc.create_time()).isoformat(),
            'num_threads': proc.num_threads(),
            'exe': proc.exe(),
            'cmdline': proc.cmdline(),
        }
        return info
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        return None


def get_system_resources():
    """获取系统资源使用情况"""
    resources = {}

    if PSUTIL_AVAILABLE:
        resources['cpu'] = {
            'percent': psutil.cpu_percent(interval=0.5),
            'count': psutil.cpu_count(),
            'per_cpu': psutil.cpu_percent(interval=0.5, percpu=True)
        }

        memory = psutil.virtual_memory()
        resources['memory'] = {
            'total_gb': round(memory.total / (1024**3), 2),
            'available_gb': round(memory.available / (1024**3), 2),
            'used_gb': round(memory.used / (1024**3), 2),
            'percent': memory.percent
        }

        disk = psutil.disk_usage('C:\\')
        resources['disk'] = {
            'total_gb': round(disk.total / (1024**3), 2),
            'used_gb': round(disk.used / (1024**3), 2),
            'free_gb': round(disk.free / (1024**3), 2),
            'percent': disk.percent
        }

        try:
            net_io = psutil.net_io_counters()
            resources['network'] = {
                'bytes_sent_mb': round(net_io.bytes_sent / (1024**2), 2),
                'bytes_recv_mb': round(net_io.bytes_recv / (1024**2), 2),
            }
        except:
            pass

    # Windows 特定信息（使用 wmic 作为后备）
    if os.name == 'nt':
        try:
            result = subprocess.run(
                ["wmic", "OS", "get", "FreePhysicalMemory,TotalVisibleMemorySize", "/Value"],
                capture_output=True, text=True
            )
            if not PSUTIL_AVAILABLE:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'FreePhysicalMemory' in line:
                        free_kb = int(line.split('=')[-1])
                    elif 'TotalVisibleMemorySize' in line:
                        total_kb = int(line.split('=')[-1])
                if 'total_kb' in dir():
                    resources['memory'] = {
                        'total_gb': round(total_kb / (1024*1024), 2),
                        'available_gb': round(free_kb / 1024, 2),
                        'used_gb': round((total_kb - free_kb) / (1024*1024), 2),
                        'percent': round((total_kb - free_kb) / total_kb * 100, 1)
                    }
        except:
            pass

    return resources


def kill_process(pid_or_name):
    """结束进程（支持 PID 或进程名）"""
    if not PSUTIL_AVAILABLE:
        process_tool = os.path.join(SCRIPT_DIR, "process_tool.py")
        result = subprocess.run(
            [sys.executable, process_tool, "kill", str(pid_or_name)],
            capture_output=True,
            text=True
        )
        return result.returncode == 0

    # 尝试作为 PID 处理
    try:
        pid = int(pid_or_name)
        proc = psutil.Process(pid)
        proc.terminate()
        return True
    except ValueError:
        pass
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False

    # 尝试作为进程名处理
    killed = False
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'].lower() == pid_or_name.lower():
                proc.terminate()
                killed = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return killed


def list_services():
    """列出 Windows 服务"""
    if os.name != 'nt':
        return "仅支持 Windows 系统"

    result = subprocess.run(
        ["sc", "query", "state=", "all"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )

    services = []
    current_service = {}
    for line in result.stdout.split('\n'):
        if line.strip().startswith('SERVICE_NAME:'):
            if current_service:
                services.append(current_service)
            current_service = {'name': line.split(':', 1)[1].strip()}
        elif line.strip().startswith('DISPLAY_NAME:'):
            current_service['display_name'] = line.split(':', 1)[1].strip()
        elif line.strip().startswith('STATE:'):
            state = line.split(':', 1)[1].strip()
            current_service['state'] = state

    if current_service:
        services.append(current_service)

    return services


def format_process_table(processes, top_n=None):
    """格式化进程列表为表格"""
    # 如果是字符串（来自 process_tool 后备），直接返回
    if isinstance(processes, str):
        return processes

    if top_n:
        processes = processes[:top_n]

    header = f"{'PID':>8} {'名称':<30} {'CPU%':>8} {'内存%':>8} {'状态':<10}"
    separator = "-" * 80
    lines = [header, separator]

    for proc in processes:
        # 兼容字典和字符串
        if isinstance(proc, dict):
            name = proc.get('name', 'Unknown')[:28]
            pid = proc.get('pid', 0)
            cpu = proc.get('cpu_percent', 0)
            mem = proc.get('memory_percent', 0)
            status = proc.get('status', 'unknown')[:8]
        else:
            # 字符串格式
            lines.append(str(proc))
            continue
        lines.append(f"{pid:>8} {name:<30} {cpu:>7.1f}% {mem:>7.1f}% {status:<10}")

    return '\n'.join(lines)


def format_resources(resources):
    """格式化系统资源为可读格式"""
    lines = []
    lines.append("=== 系统资源使用情况 ===")

    if 'cpu' in resources:
        cpu = resources['cpu']
        lines.append(f"CPU: {cpu['percent']:.1f}% (共 {cpu['count']} 核心)")

    if 'memory' in resources:
        mem = resources['memory']
        lines.append(f"内存: {mem['used_gb']:.1f}GB / {mem['total_gb']:.1f}GB ({mem['percent']:.1f}%)")

    if 'disk' in resources:
        disk = resources['disk']
        lines.append(f"磁盘: {disk['used_gb']:.1f}GB / {disk['total_gb']:.1f}GB ({disk['percent']:.1f}%)")

    if 'network' in resources:
        net = resources['network']
        lines.append(f"网络: 已发送 {net['bytes_sent_mb']:.1f}MB, 已接收 {net['bytes_recv_mb']:.1f}MB")

    return '\n'.join(lines)


def main():
    import io

    # 设置标准输出编码
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    parser = argparse.ArgumentParser(
        description="LLM-OS 任务管理器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python llm_os_task_manager.py --list                      # 列出所有进程（按CPU排序）
  python llm_os_task_manager.py --top 10                   # 列出前10个进程
  python llm_os_task_manager.py --resources                # 查看系统资源
  python llm_os_task_manager.py --details 1234             # 查看PID 1234的详情
  python llm_os_task_manager.py --kill notepad.exe          # 结束进程
  python llm_os_task_manager.py --services                  # 列出服务
        """
    )

    parser.add_argument("--list", "-l", action="store_true",
                       help="列出所有进程（按CPU使用率排序）")
    parser.add_argument("--top", "-t", type=int, metavar="N",
                       help="列出前N个进程")
    parser.add_argument("--resources", "-r", action="store_true",
                       help="查看系统资源使用情况")
    parser.add_argument("--details", "-d", type=int, metavar="PID",
                       help="查看指定进程的详细信息")
    parser.add_argument("--kill", "-k", type=str, metavar="进程名或PID",
                       help="结束进程")
    parser.add_argument("--services", "-s", action="store_true",
                       help="列出 Windows 服务")
    parser.add_argument("--json", "-j", action="store_true",
                       help="输出 JSON 格式")

    args = parser.parse_args()

    # 如果没有参数，显示帮助
    if len(sys.argv) == 1:
        parser.print_help()
        return

    # 列出进程
    if args.list or args.top:
        processes = get_process_list()
        if args.json:
            print(json.dumps(processes, ensure_ascii=False, indent=2))
        else:
            if args.top:
                print(f"=== 资源占用最高的 {args.top} 个进程 ===")
                print(format_process_table(processes, args.top))
            else:
                print("=== 所有进程（按CPU使用率排序）===")
                print(format_process_table(processes))

    # 系统资源
    if args.resources:
        resources = get_system_resources()
        if args.json:
            print(json.dumps(resources, ensure_ascii=False, indent=2))
        else:
            print(format_resources(resources))

    # 进程详情
    if args.details:
        details = get_process_details(args.details)
        if details:
            if args.json:
                print(json.dumps(details, ensure_ascii=False, indent=2))
            else:
                print(f"=== 进程 {args.details} 详细信息 ===")
                for key, value in details.items():
                    if key != 'cmdline':
                        print(f"  {key}: {value}")
                if details.get('cmdline'):
                    print(f"  cmdline: {' '.join(details['cmdline'])}")
        else:
            print(f"无法获取进程 {args.details} 的信息")

    # 结束进程
    if args.kill:
        if kill_process(args.kill):
            print(f"✓ 进程已结束: {args.kill}")
        else:
            print(f"✗ 结束进程失败: {args.kill}")

    # 服务列表
    if args.services:
        services = list_services()
        if isinstance(services, str):
            print(services)
        else:
            print("=== Windows 服务列表 ===")
            for svc in services[:20]:  # 显示前20个
                name = svc.get('name', 'N/A')
                display = svc.get('display_name', name)
                state = svc.get('state', 'N/A')
                print(f"  {name:<30} {state}")


if __name__ == "__main__":
    main()