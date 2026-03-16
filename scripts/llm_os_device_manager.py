"""
LLM-OS 设备管理器模块
提供 USB 设备、蓝牙设备、打印机等设备管理能力
Version: 1.0.0
"""

import subprocess
import json
import re
import sys
import io
from typing import Dict, List, Any, Optional

# 设置标准输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def get_usb_devices() -> List[Dict[str, str]]:
    """获取 USB 设备列表"""
    devices = []
    try:
        # 使用 wmic 命令获取 USB 控制器和设备信息
        result = subprocess.run(
            ["wmic", "path", "win32_usbcontroller", "get", "name,status,deviceid", "/format:list"],
            capture_output=True, text=True, encoding='utf-8', errors='ignore'
        )
        if result.returncode == 0:
            current_device = {}
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line.startswith('DeviceID='):
                    current_device['device_id'] = line.split('=', 1)[1]
                elif line.startswith('Name='):
                    current_device['name'] = line.split('=', 1)[1]
                elif line.startswith('Status='):
                    current_device['status'] = line.split('=', 1)[1]
                    if current_device.get('device_id'):
                        devices.append(current_device)
                        current_device = {}
    except Exception as e:
        print(f"获取 USB 设备出错: {e}", file=sys.stderr)

    # 尝试获取 USB 设备详细信息
    try:
        result = subprocess.run(
            ["wmic", "path", "win32_usbhub", "get", "name,deviceid,status", "/format:list"],
            capture_output=True, text=True, encoding='utf-8', errors='ignore'
        )
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line.startswith('DeviceID=') or line.startswith('Name=') or line.startswith('Status='):
                    pass  # 已通过其他方式获取
    except Exception as e:
        pass

    return devices

def get_bluetooth_devices() -> List[Dict[str, Any]]:
    """获取蓝牙设备列表"""
    devices = []
    try:
        # 使用 powershell 获取蓝牙设备
        ps_script = """
        Get-PnpDevice -Class Bluetooth | Select-Object FriendlyName, Status, Manufacturer, InstanceId | ConvertTo-Json
        """
        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True, text=True, encoding='utf-8', errors='ignore'
        )
        if result.returncode == 0 and result.stdout.strip():
            try:
                data = json.loads(result.stdout)
                if isinstance(data, dict):
                    data = [data]
                for item in data:
                    devices.append({
                        'name': item.get('FriendlyName', 'Unknown'),
                        'status': item.get('Status', 'Unknown'),
                        'manufacturer': item.get('Manufacturer', 'Unknown'),
                        'instance_id': item.get('InstanceId', '')
                    })
            except json.JSONDecodeError:
                pass
    except Exception as e:
        print(f"获取蓝牙设备出错: {e}", file=sys.stderr)

    return devices

def get_printers() -> List[Dict[str, Any]]:
    """获取打印机列表"""
    printers = []
    try:
        result = subprocess.run(
            ["wmic", "path", "win32_printer", "get", "name,status,default,portname", "/format:list"],
            capture_output=True, text=True, encoding='utf-8', errors='ignore'
        )
        if result.returncode == 0:
            current_printer = {}
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line.startswith('Default='):
                    current_printer['default'] = line.split('=', 1)[1] == 'TRUE'
                elif line.startswith('Name='):
                    current_printer['name'] = line.split('=', 1)[1]
                elif line.startswith('PortName='):
                    current_printer['port'] = line.split('=', 1)[1]
                elif line.startswith('Status='):
                    current_printer['status'] = line.split('=', 1)[1]
                    if current_printer.get('name'):
                        printers.append(current_printer)
                        current_printer = {}
    except Exception as e:
        print(f"获取打印机出错: {e}", file=sys.stderr)

    return printers

def get_network_adapters() -> List[Dict[str, Any]]:
    """获取网络适配器列表"""
    adapters = []
    try:
        result = subprocess.run(
            ["wmic", "path", "win32_networkadapter", "get", "name,adaptertype,macaddress,netconnectionstatus", "/format:list"],
            capture_output=True, text=True, encoding='utf-8', errors='ignore'
        )
        if result.returncode == 0:
            current_adapter = {}
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line.startswith('AdapterType='):
                    current_adapter['type'] = line.split('=', 1)[1]
                elif line.startswith('MACAddress='):
                    current_adapter['mac'] = line.split('=', 1)[1]
                elif line.startswith('Name='):
                    current_adapter['name'] = line.split('=', 1)[1]
                elif line.startswith('NetConnectionStatus='):
                    status_map = {
                        '0': 'Disconnected',
                        '1': 'Connecting',
                        '2': 'Connected',
                        '3': 'Disconnecting',
                        '4': 'Hardware not present',
                        '5': 'Hardware disabled',
                        '6': 'Hardware malfunction',
                        '7': 'Media disconnected',
                        '8': 'Authenticating',
                        '9': 'Authentication succeeded',
                        '10': 'Authentication failed',
                        '11': 'Invalid address',
                        '12': 'Credentials required'
                    }
                    status_code = line.split('=', 1)[1]
                    current_adapter['status'] = status_map.get(status_code, f'Unknown({status_code})')
                    if current_adapter.get('name'):
                        adapters.append(current_adapter)
                        current_adapter = {}
    except Exception as e:
        print(f"获取网络适配器出错: {e}", file=sys.stderr)

    return adapters

def get_disk_drives() -> List[Dict[str, Any]]:
    """获取磁盘驱动器列表"""
    drives = []
    try:
        result = subprocess.run(
            ["wmic", "path", "win32_diskdrive", "get", "model,size,mediatype,serialnumber,status", "/format:list"],
            capture_output=True, text=True, encoding='utf-8', errors='ignore'
        )
        if result.returncode == 0:
            current_drive = {}
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line.startswith('MediaType='):
                    current_drive['media_type'] = line.split('=', 1)[1]
                elif line.startswith('Model='):
                    current_drive['model'] = line.split('=', 1)[1]
                elif line.startswith('SerialNumber='):
                    current_drive['serial'] = line.split('=', 1)[1]
                elif line.startswith('Size='):
                    size_bytes = line.split('=', 1)[1]
                    try:
                        size_gb = int(size_bytes) / (1024**3) if size_bytes.isdigit() else 0
                        current_drive['size_gb'] = round(size_gb, 2)
                    except:
                        current_drive['size_gb'] = 0
                elif line.startswith('Status='):
                    current_drive['status'] = line.split('=', 1)[1]
                    if current_drive.get('model'):
                        drives.append(current_drive)
                        current_drive = {}
    except Exception as e:
        print(f"获取磁盘驱动器出错: {e}", file=sys.stderr)

    return drives

def get_battery_status() -> Dict[str, Any]:
    """获取电池状态"""
    battery = {}
    try:
        result = subprocess.run(
            ["wmic", "path", "win32_battery", "get", "estimatedchargeremaining,estimatedruntime,status", "/format:list"],
            capture_output=True, text=True, encoding='utf-8', errors='ignore'
        )
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line.startswith('EstimatedChargeRemaining='):
                    percent = line.split('=', 1)[1]
                    battery['charge_percent'] = int(percent) if percent.isdigit() else None
                elif line.startswith('EstimatedRunTime='):
                    minutes = line.split('=', 1)[1]
                    battery['estimated_runtime_minutes'] = int(minutes) if minutes.isdigit() else None
                elif line.startswith('Status='):
                    battery['status'] = line.split('=', 1)[1]
    except Exception as e:
        print(f"获取电池状态出错: {e}", file=sys.stderr)

    return battery

def get_device_summary() -> Dict[str, Any]:
    """获取设备摘要信息"""
    summary = {
        'usb_devices': get_usb_devices(),
        'bluetooth_devices': get_bluetooth_devices(),
        'printers': get_printers(),
        'network_adapters': get_network_adapters(),
        'disk_drives': get_disk_drives(),
        'battery': get_battery_status()
    }
    return summary

def print_device_summary(summary: Dict[str, Any], format: str = 'text') -> None:
    """打印设备摘要"""
    if format == 'json':
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return

    print("=" * 60)
    print("LLM-OS 设备管理器摘要")
    print("=" * 60)

    # USB 设备
    print(f"\n[USB] USB 设备 ({len(summary['usb_devices'])} 个):")
    if summary['usb_devices']:
        for dev in summary['usb_devices'][:5]:  # 最多显示5个
            print(f"  * {dev.get('name', 'Unknown')}")
        if len(summary['usb_devices']) > 5:
            print(f"  ... 还有 {len(summary['usb_devices']) - 5} 个")
    else:
        print("  (无 USB 设备信息)")

    # 蓝牙设备
    print(f"\n[蓝牙] 蓝牙设备 ({len(summary['bluetooth_devices'])} 个):")
    if summary['bluetooth_devices']:
        for dev in summary['bluetooth_devices'][:5]:
            status_icon = "[OK]" if dev.get('status') == 'OK' else "[X]"
            print(f"  {status_icon} {dev.get('name', 'Unknown')}")
        if len(summary['bluetooth_devices']) > 5:
            print(f"  ... 还有 {len(summary['bluetooth_devices']) - 5} 个")
    else:
        print("  (无蓝牙设备或未检测到)")

    # 打印机
    print(f"\n[打印机] 打印机 ({len(summary['printers'])} 个):")
    if summary['printers']:
        for printer in summary['printers']:
            default_marker = " [默认]" if printer.get('default') else ""
            print(f"  * {printer.get('name', 'Unknown')}{default_marker}")
    else:
        print("  (无打印机)")

    # 网络适配器
    print(f"\n[网络] 网络适配器 ({len(summary['network_adapters'])} 个):")
    if summary['network_adapters']:
        for adapter in summary['network_adapters'][:5]:
            status_icon = "[+]" if adapter.get('status') == 'Connected' else "[-]"
            print(f"  {status_icon} {adapter.get('name', 'Unknown')} ({adapter.get('type', 'N/A')})")
    else:
        print("  (无网络适配器)")

    # 磁盘驱动器
    print(f"\n[磁盘] 磁盘驱动器 ({len(summary['disk_drives'])} 个):")
    if summary['disk_drives']:
        for drive in summary['disk_drives']:
            size = drive.get('size_gb', 0)
            print(f"  * {drive.get('model', 'Unknown')} ({size:.1f} GB)")
    else:
        print("  (无磁盘驱动器信息)")

    # 电池状态
    battery = summary.get('battery', {})
    if battery:
        print(f"\n[电池] 电池状态:")
        if battery.get('charge_percent') is not None:
            print(f"  电量: {battery['charge_percent']}%")
        if battery.get('estimated_runtime_minutes'):
            print(f"  预计运行时间: {battery['estimated_runtime_minutes']} 分钟")
        print(f"  状态: {battery.get('status', 'Unknown')}")
    else:
        print(f"\n[电池] 电池状态: (未检测到电池或台式机)")

    print("\n" + "=" * 60)

def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser(description='LLM-OS 设备管理器')
    parser.add_argument('--usb', action='store_true', help='获取 USB 设备列表')
    parser.add_argument('--bluetooth', action='store_true', help='获取蓝牙设备列表')
    parser.add_argument('--printers', action='store_true', help='获取打印机列表')
    parser.add_argument('--network', action='store_true', help='获取网络适配器列表')
    parser.add_argument('--disks', action='store_true', help='获取磁盘驱动器列表')
    parser.add_argument('--battery', action='store_true', help='获取电池状态')
    parser.add_argument('--summary', action='store_true', help='获取设备摘要')
    parser.add_argument('--format', choices=['text', 'json'], default='text', help='输出格式')
    parser.add_argument('--all', action='store_true', help='获取所有设备信息')

    args = parser.parse_args()

    # 默认显示摘要
    if args.all or (not args.usb and not args.bluetooth and not args.printers
        and not args.network and not args.disks and not args.battery):
        args.summary = True

    if args.summary or args.all:
        summary = get_device_summary()
        print_device_summary(summary, args.format)
    elif args.usb:
        devices = get_usb_devices()
        if args.format == 'json':
            print(json.dumps(devices, indent=2, ensure_ascii=False))
        else:
            print(f"USB 设备 ({len(devices)} 个):")
            for dev in devices:
                print(f"  • {dev.get('name', 'Unknown')} - {dev.get('status', 'N/A')}")
    elif args.bluetooth:
        devices = get_bluetooth_devices()
        if args.format == 'json':
            print(json.dumps(devices, indent=2, ensure_ascii=False))
        else:
            print(f"蓝牙设备 ({len(devices)} 个):")
            for dev in devices:
                print(f"  • {dev.get('name', 'Unknown')} ({dev.get('status', 'N/A')})")
    elif args.printers:
        printers = get_printers()
        if args.format == 'json':
            print(json.dumps(printers, indent=2, ensure_ascii=False))
        else:
            print(f"打印机 ({len(printers)} 个):")
            for printer in printers:
                default = " [默认]" if printer.get('default') else ""
                print(f"  • {printer.get('name', 'Unknown')}{default}")
    elif args.network:
        adapters = get_network_adapters()
        if args.format == 'json':
            print(json.dumps(adapters, indent=2, ensure_ascii=False))
        else:
            print(f"网络适配器 ({len(adapters)} 个):")
            for adapter in adapters:
                print(f"  • {adapter.get('name', 'Unknown')} - {adapter.get('status', 'N/A')}")
    elif args.disks:
        drives = get_disk_drives()
        if args.format == 'json':
            print(json.dumps(drives, indent=2, ensure_ascii=False))
        else:
            print(f"磁盘驱动器 ({len(drives)} 个):")
            for drive in drives:
                print(f"  • {drive.get('model', 'Unknown')} ({drive.get('size_gb', 0):.1f} GB)")
    elif args.battery:
        battery = get_battery_status()
        if args.format == 'json':
            print(json.dumps(battery, indent=2, ensure_ascii=False))
        else:
            print("电池状态:")
            if battery.get('charge_percent') is not None:
                print(f"  电量: {battery['charge_percent']}%")
            if battery.get('estimated_runtime_minutes'):
                print(f"  预计运行时间: {battery['estimated_runtime_minutes']} 分钟")
            print(f"  状态: {battery.get('status', 'Unknown')}")

if __name__ == '__main__':
    main()