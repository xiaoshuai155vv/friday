#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-OS 系统监控模块 - 提供实时系统状态监控能力

本模块提供 CPU、内存、磁盘、网络等系统资源的实时监控功能，
是 LLM-OS 桌面操作系统的重要组成部分。

版本: 1.0.0
依赖: psutil
"""

import os
import sys
import json
import time
import argparse

# 尝试导入 psutil
try:
    import psutil
except ImportError:
    print("错误: 需要安装 psutil 库")
    print("请运行: pip install psutil")
    sys.exit(1)


def get_cpu_info():
    """获取 CPU 信息"""
    # CPU 使用率
    cpu_percent = psutil.cpu_percent(interval=0.5, percpu=False)
    cpu_percent_per_core = psutil.cpu_percent(interval=0.5, percpu=True)

    # CPU 频率
    try:
        cpu_freq = psutil.cpu_freq()
        freq_current = cpu_freq.current if cpu_freq else 0
        freq_min = cpu_freq.min if cpu_freq else 0
        freq_max = cpu_freq.max if cpu_freq else 0
    except:
        freq_current = freq_min = freq_max = 0

    # CPU 核心数
    cpu_count = psutil.cpu_count(logical=True)
    cpu_count_physical = psutil.cpu_count(logical=False)

    # CPU 统计信息
    cpu_stats = psutil.cpu_stats()
    ctx_switches = cpu_stats.ctx_switches
    interrupts = cpu_stats.interrupts
    soft_interrupts = cpu_stats.soft_interrupts

    return {
        "usage_percent": cpu_percent,
        "usage_per_core": cpu_percent_per_core,
        "frequency": {
            "current_mhz": round(freq_current, 2),
            "min_mhz": round(freq_min, 2),
            "max_mhz": round(freq_max, 2)
        },
        "cores": {
            "logical": cpu_count,
            "physical": cpu_count_physical
        },
        "stats": {
            "ctx_switches": ctx_switches,
            "interrupts": interrupts,
            "soft_interrupts": soft_interrupts
        }
    }


def get_memory_info():
    """获取内存信息"""
    virtual_mem = psutil.virtual_memory()
    swap_mem = psutil.swap_memory()

    return {
        "virtual": {
            "total_gb": round(virtual_mem.total / (1024**3), 2),
            "available_gb": round(virtual_mem.available / (1024**3), 2),
            "used_gb": round(virtual_mem.used / (1024**3), 2),
            "percent": virtual_mem.percent,
            "free_gb": round(virtual_mem.free / (1024**3), 2)
        },
        "swap": {
            "total_gb": round(swap_mem.total / (1024**3), 2),
            "used_gb": round(swap_mem.used / (1024**3), 2),
            "free_gb": round(swap_mem.free / (1024**3), 2),
            "percent": swap_mem.percent
        }
    }


def get_disk_info():
    """获取磁盘信息"""
    disk_info = []

    # 获取所有分区的磁盘使用情况
    partitions = psutil.disk_partitions()
    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_info.append({
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "fstype": partition.fstype,
                "total_gb": round(usage.total / (1024**3), 2),
                "used_gb": round(usage.used / (1024**3), 2),
                "free_gb": round(usage.free / (1024**3), 2),
                "percent": usage.percent
            })
        except PermissionError:
            continue
        except Exception:
            continue

    # 磁盘 I/O 统计
    try:
        disk_io = psutil.disk_io_counters()
        if disk_io:
            disk_io_info = {
                "read_count": disk_io.read_count,
                "write_count": disk_io.write_count,
                "read_bytes_mb": round(disk_io.read_bytes / (1024**2), 2),
                "write_bytes_mb": round(disk_io.write_bytes / (1024**2), 2),
                "read_time_ms": disk_io.read_time,
                "write_time_ms": disk_io.write_time
            }
        else:
            disk_io_info = None
    except:
        disk_io_info = None

    return {
        "partitions": disk_info,
        "io_stats": disk_io_info
    }


def get_network_info():
    """获取网络信息"""
    # 网络接口统计
    net_io = psutil.net_io_counters(pernic=True)

    interfaces = {}
    for iface, stats in net_io.items():
        interfaces[iface] = {
            "bytes_sent_mb": round(stats.bytes_sent / (1024**2), 2),
            "bytes_recv_mb": round(stats.bytes_recv / (1024**2), 2),
            "packets_sent": stats.packets_sent,
            "packets_recv": stats.packets_recv,
            "errin": stats.errin,
            "errout": stats.errout,
            "dropin": stats.dropin,
            "dropout": stats.dropout
        }

    # 网络连接统计
    try:
        connections = len(psutil.net_connections())
    except:
        connections = 0

    return {
        "interfaces": interfaces,
        "total_connections": connections
    }


def get_battery_info():
    """获取电池信息"""
    try:
        battery = psutil.sensors_battery()
        if battery is None:
            return None

        return {
            "percent": battery.percent,
            "seconds_left": battery.secsleft,
            "power_plugged": battery.power_plugged
        }
    except:
        return None


def get_system_summary():
    """获取系统监控摘要"""
    cpu = get_cpu_info()
    memory = get_memory_info()
    disk = get_disk_info()
    network = get_network_info()
    battery = get_battery_info()

    # 计算总网络流量
    total_sent = 0
    total_recv = 0
    for iface, stats in network["interfaces"].items():
        total_sent += stats["bytes_sent_mb"]
        total_recv += stats["bytes_recv_mb"]

    # 计算总磁盘使用
    total_disk_used = 0
    total_disk_total = 0
    for part in disk["partitions"]:
        total_disk_used += part["used_gb"]
        total_disk_total += part["total_gb"]

    summary = {
        "cpu": {
            "usage_percent": cpu["usage_percent"],
            "cores_logical": cpu["cores"]["logical"],
            "cores_physical": cpu["cores"]["physical"],
            "frequency_mhz": cpu["frequency"]["current_mhz"]
        },
        "memory": {
            "total_gb": memory["virtual"]["total_gb"],
            "used_gb": memory["virtual"]["used_gb"],
            "percent": memory["virtual"]["percent"]
        },
        "disk": {
            "total_gb": round(total_disk_total, 2),
            "used_gb": round(total_disk_used, 2),
            "percent": round((total_disk_used / total_disk_total * 100) if total_disk_total > 0 else 0, 1)
        },
        "network": {
            "total_sent_mb": round(total_sent, 2),
            "total_recv_mb": round(total_recv, 2)
        }
    }

    if battery:
        summary["battery"] = {
            "percent": battery["percent"],
            "power_plugged": battery["power_plugged"]
        }

    return summary


def format_output(data, format_type="json"):
    """格式化输出"""
    if format_type == "json":
        return json.dumps(data, indent=2, ensure_ascii=False)
    elif format_type == "compact":
        return json.dumps(data, ensure_ascii=False)
    elif format_type == "text":
        return format_as_text(data)
    else:
        return json.dumps(data, indent=2, ensure_ascii=False)


def format_as_text(data):
    """格式化为人类可读的文本"""
    lines = []
    lines.append("=== 系统监控摘要 ===")
    lines.append(f"CPU: {data['cpu']['usage_percent']}% (频率: {data['cpu']['frequency_mhz']} MHz)")
    lines.append(f"内存: {data['memory']['used_gb']:.1f}GB / {data['memory']['total_gb']:.1f}GB ({data['memory']['percent']}%)")
    lines.append(f"磁盘: {data['disk']['used_gb']:.1f}GB / {data['disk']['total_gb']:.1f}GB ({data['disk']['percent']}%)")
    lines.append(f"网络: 发送 {data['network']['total_sent_mb']:.1f}MB, 接收 {data['network']['total_recv_mb']:.1f}MB")

    if "battery" in data:
        battery = data["battery"]
        status = "充电中" if battery["power_plugged"] else "使用电池"
        lines.append(f"电池: {battery['percent']}% ({status})")

    return "\n".join(lines)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="LLM-OS 系统监控模块 - 提供实时系统状态监控能力",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python llm_os_system_monitor.py --summary          # 查看系统监控摘要
  python llm_os_system_monitor.py --cpu               # 查看 CPU 详细信息
  python llm_os_system_monitor.py --memory           # 查看内存详细信息
  python llm_os_system_monitor.py --disk             # 查看磁盘详细信息
  python llm_os_system_monitor.py --network          # 查看网络详细信息
  python llm_os_system_monitor.py --battery          # 查看电池详细信息
  python llm_os_system_monitor.py --all              # 查看所有信息
  python llm_os_system_monitor.py --text             # 文本格式输出
        """
    )

    parser.add_argument("--summary", "-s", action="store_true",
                        help="查看系统监控摘要")
    parser.add_argument("--cpu", "-c", action="store_true",
                        help="查看 CPU 详细信息")
    parser.add_argument("--memory", "-m", action="store_true",
                        help="查看内存详细信息")
    parser.add_argument("--disk", "-d", action="store_true",
                        help="查看磁盘详细信息")
    parser.add_argument("--network", "-n", action="store_true",
                        help="查看网络详细信息")
    parser.add_argument("--battery", "-b", action="store_true",
                        help="查看电池详细信息")
    parser.add_argument("--all", "-a", action="store_true",
                        help="查看所有信息")
    parser.add_argument("--format", "-f", choices=["json", "compact", "text"], default="json",
                        help="输出格式 (默认: json)")
    parser.add_argument("--wait", "-w", type=int, metavar="SECONDS",
                        help="持续监控指定秒数 (按 Ctrl+C 停止)")

    args = parser.parse_args()

    # 如果没有参数，显示摘要
    if len(sys.argv) == 1:
        print(format_output(get_system_summary(), "text"))
        return

    # 持续监控模式
    if args.wait:
        try:
            print("持续监控模式 (按 Ctrl+C 停止)...")
            print("-" * 50)
            while True:
                os.system('cls' if os.name == 'nt' else 'clear')
                print(f"监控时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                print("-" * 50)
                print(format_output(get_system_summary(), "text"))
                time.sleep(args.wait)
        except KeyboardInterrupt:
            print("\n监控已停止")
        return

    # 根据参数获取相应信息
    if args.summary or args.all:
        print(format_output(get_system_summary(), args.format))

    if args.cpu:
        print("=== CPU 详细信息 ===")
        print(format_output(get_cpu_info(), args.format))

    if args.memory:
        print("=== 内存详细信息 ===")
        print(format_output(get_memory_info(), args.format))

    if args.disk:
        print("=== 磁盘详细信息 ===")
        print(format_output(get_disk_info(), args.format))

    if args.network:
        print("=== 网络详细信息 ===")
        print(format_output(get_network_info(), args.format))

    if args.battery:
        battery_info = get_battery_info()
        if battery_info:
            print("=== 电池详细信息 ===")
            print(format_output(battery_info, args.format))
        else:
            print("电池信息不可用 (可能没有电池或不支持)")


if __name__ == "__main__":
    main()