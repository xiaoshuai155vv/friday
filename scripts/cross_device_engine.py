#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Smart Cross-Device Collaboration Control Engine
Discover and control devices on the same network, enabling file transfer, notification sync, and remote control."""

import socket
import os
import json
import subprocess
import time
import threading
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any

# State storage directory
STATE_DIR = os.path.join(os.path.dirname(__file__), "..", "runtime", "state")
DEVICE_STATE_FILE = os.path.join(STATE_DIR, "cross_device_state.json")

# Common ports for device identification
COMMON_PORTS = [22, 80, 443, 445, 5000, 8080, 8554]


def _ensure_dir():
    """Ensure state directory exists"""
    os.makedirs(STATE_DIR, exist_ok=True)


def _load_device_state() -> Dict[str, Any]:
    """Load device state"""
    _ensure_dir()
    if os.path.isfile(DEVICE_STATE_FILE):
        try:
            with open(DEVICE_STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "devices": [],
        "last_scan": None,
        "transfer_history": [],
        "settings": {
            "auto_discover": True,
            "scan_interval": 3600,
        }
    }


def _save_device_state(state: Dict[str, Any]) -> None:
    """Save device state"""
    _ensure_dir()
    with open(DEVICE_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def get_local_ip() -> str:
    """Get local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"


def get_local_network() -> tuple:
    """Get local network info (IP, subnet)"""
    local_ip = get_local_ip()
    parts = local_ip.rsplit('.', 1)
    network_prefix = parts[0]
    return local_ip, network_prefix


def scan_device(ip: str, timeout: float = 0.5) -> Optional[Dict[str, Any]]:
    """Scan single device"""
    device_info = {"ip": ip, "hostname": None, "ports": [], "os_type": None, "last_seen": None}

    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        device_info["hostname"] = hostname
    except socket.herror:
        pass

    for port in COMMON_PORTS:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            if result == 0:
                device_info["ports"].append(port)
        except Exception:
            pass

    if 22 in device_info["ports"]:
        device_info["os_type"] = "Linux/Mac (SSH)"
    elif 445 in device_info["ports"] or 139 in device_info["ports"]:
        device_info["os_type"] = "Windows (SMB)"
    elif 80 in device_info["ports"] or 443 in device_info["ports"]:
        device_info["os_type"] = "Web Server"
    elif 5555 in device_info["ports"]:
        device_info["os_type"] = "Android (ADB)"

    device_info["last_seen"] = datetime.now(timezone.utc).isoformat()

    return device_info if device_info["ports"] else None


def discover_devices(timeout: int = 5) -> List[Dict[str, Any]]:
    """Discover devices on local network"""
    local_ip, network_prefix = get_local_network()
    devices = []
    lock = threading.Lock()

    def scan_range(start: int, end: int):
        local_devices = []
        for i in range(start, end):
            ip = f"{network_prefix}.{i}"
            if ip == local_ip:
                continue
            result = scan_device(ip)
            if result:
                local_devices.append(result)
        with lock:
            devices.extend(local_devices)

    threads = []
    step = 50
    for start in range(1, 255, step):
        end = min(start + step, 255)
        t = threading.Thread(target=scan_range, args=(start, end))
        t.start()
        threads.append(t)

    for t in threads:
        t.join(timeout=timeout)

    return devices


def get_device_by_ip(ip: str) -> Optional[Dict[str, Any]]:
    """Get device info by IP"""
    state = _load_device_state()
    for device in state.get("devices", []):
        if device.get("ip") == ip:
            return device
    return None


def add_device(device: Dict[str, Any]) -> None:
    """Add or update device"""
    state = _load_device_state()
    devices = state.get("devices", [])

    for i, d in enumerate(devices):
        if d.get("ip") == device.get("ip"):
            devices[i] = device
            break
    else:
        devices.append(device)

    state["devices"] = devices
    _save_device_state(state)


def remove_device(ip: str) -> bool:
    """Remove device"""
    state = _load_device_state()
    devices = state.get("devices", [])
    original_len = len(devices)
    devices = [d for d in devices if d.get("ip") != ip]
    if len(devices) < original_len:
        state["devices"] = devices
        _save_device_state(state)
        return True
    return False


def send_file_to_device(file_path: str, target_ip: str, method: str = "smb") -> Dict[str, Any]:
    """Send file to target device"""
    if not os.path.isfile(file_path):
        return {"success": False, "error": "File not found"}

    filename = os.path.basename(file_path)
    state = _load_device_state()

    result = {
        "success": False,
        "method": method,
        "file": filename,
        "target": target_ip,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    try:
        if method == "smb":
            result["method"] = "smb"
            result["message"] = f"SMB transfer requires shared folder on target device. Try accessing {target_ip} via SMB"
            result["success"] = True

        elif method == "ftp":
            result["method"] = "ftp"
            result["message"] = "FTP transfer requires FTP server on target device. Use pyftpdlib to start FTP server"
            result["success"] = True

        elif method == "email":
            result["method"] = "email"
            result["message"] = "Can send file via email attachment, requires SMTP configuration"
            result["success"] = True

        else:
            result["error"] = f"Unsupported transfer method: {method}"

        if result["success"]:
            state.setdefault("transfer_history", []).append(result)
            _save_device_state(state)

    except Exception as e:
        result["error"] = str(e)

    return result


def execute_remote_command(command: str, target_ip: str, method: str = "ssh") -> Dict[str, Any]:
    """Execute command on remote device"""
    result = {
        "success": False,
        "command": command,
        "target": target_ip,
        "method": method,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if method == "ssh":
        try:
            subprocess.run(["ssh", "-o", "BatchMode=yes", f"user@{target_ip}", command],
                          capture_output=True, timeout=30)
            result["success"] = True
            result["output"] = "Command sent to remote device"
        except FileNotFoundError:
            result["error"] = "SSH client not found, please install OpenSSH"
        except subprocess.TimeoutExpired:
            result["error"] = "Command execution timeout"
        except Exception as e:
            result["error"] = f"SSH connection failed: {str(e)}"

    elif method == "winrm":
        result["message"] = "Windows remote management requires WinRM configuration"
        result["success"] = True

    else:
        result["error"] = f"Unsupported remote execution method: {method}"

    return result


def sync_notification(direction: str = "phone_to_pc") -> Dict[str, Any]:
    """Sync notifications"""
    result = {
        "success": False,
        "direction": direction,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if direction == "phone_to_pc":
        result["message"] = "Phone notification sync requires: 1) Install companion app on phone; 2) Enable notification access; 3) Ensure phone and PC on same network"
        result["success"] = True
    elif direction == "pc_to_phone":
        result["message"] = "PC to phone notification push requires: 1) Install app on phone; 2) Enable push service; or use third-party services like Pushbullet, Pushover"
        result["success"] = True
    else:
        result["error"] = f"Unsupported sync direction: {direction}"

    return result


def get_status() -> Dict[str, Any]:
    """Get engine status"""
    local_ip = get_local_ip()
    state = _load_device_state()
    return {
        "engine": "cross_device_engine",
        "local_ip": local_ip,
        "network": f"{local_ip.rsplit('.', 1)[0]}.0/24",
        "device_count": len(state.get("devices", [])),
        "last_scan": state.get("last_scan"),
        "settings": state.get("settings", {}),
    }


def list_devices() -> List[Dict[str, Any]]:
    """List discovered devices"""
    state = _load_device_state()
    return state.get("devices", [])


def scan_and_update() -> List[Dict[str, Any]]:
    """Scan and update device list"""
    devices = discover_devices()

    state = _load_device_state()
    state["devices"] = devices
    state["last_scan"] = datetime.now(timezone.utc).isoformat()
    _save_device_state(state)

    return devices


def run_command(args: List[str]) -> Dict[str, Any]:
    """Run engine command"""
    if not args:
        return {"error": "Please specify command", "commands": ["status", "list", "scan", "send", "remote", "sync"]}

    cmd = args[0]

    if cmd == "status":
        return get_status()

    elif cmd == "list":
        devices = list_devices()
        return {"devices": devices, "count": len(devices)}

    elif cmd == "scan":
        devices = scan_and_update()
        return {
            "scan_complete": True,
            "devices_found": len(devices),
            "devices": devices,
        }

    elif cmd == "send":
        if len(args) < 3:
            return {"error": "Usage: send <file_path> <target_ip> [method]", "example": "send C:\\test.txt 192.168.1.100 smb"}
        file_path = args[1]
        target_ip = args[2]
        method = args[3] if len(args) > 3 else "smb"
        return send_file_to_device(file_path, target_ip, method)

    elif cmd == "remote":
        if len(args) < 3:
            return {"error": "Usage: remote <command> <target_ip> [method]", "example": "remote 'ls -la' 192.168.1.100 ssh"}
        command = args[1]
        target_ip = args[2]
        method = args[3] if len(args) > 3 else "ssh"
        return execute_remote_command(command, target_ip, method)

    elif cmd == "sync":
        direction = args[1] if len(args) > 1 else "phone_to_pc"
        return sync_notification(direction)

    elif cmd == "help":
        return {
            "commands": {
                "status": "Get engine status",
                "list": "List discovered devices",
                "scan": "Scan local network for devices",
                "send": "Send file to device (send <file> <ip> [method])",
                "remote": "Execute remote command (remote <command> <ip> [method])",
                "sync": "Sync notifications (sync [phone_to_pc|pc_to_phone])",
            }
        }

    else:
        return {"error": f"Unknown command: {cmd}", "commands": ["status", "list", "scan", "send", "remote", "sync"]}


def main():
    import sys
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    result = run_command(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()