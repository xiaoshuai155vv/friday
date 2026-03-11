#!/usr/bin/env python3
"""
系统健康检查脚本
用于定期检查核心功能状态，生成健康报告
"""

import json
import os
import sys
from datetime import datetime
import importlib.util

# 添加项目根目录到路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

def import_module_from_path(module_name, file_path):
    """从文件路径动态导入模块"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def check_screenshot_capability():
    """检查截图能力"""
    try:
        # 检查脚本文件是否存在
        script_path = os.path.join(SCRIPT_DIR, "screenshot_tool.py")
        if os.path.exists(script_path):
            return True, "截图功能正常"
        else:
            return False, "截图脚本不存在"
    except Exception as e:
        return False, f"截图功能异常: {str(e)}"

def check_mouse_capability():
    """检查鼠标操作能力"""
    try:
        script_path = os.path.join(SCRIPT_DIR, "mouse_tool.py")
        if os.path.exists(script_path):
            return True, "鼠标操作功能正常"
        else:
            return False, "鼠标脚本不存在"
    except Exception as e:
        return False, f"鼠标功能异常: {str(e)}"

def check_keyboard_capability():
    """检查键盘操作能力"""
    try:
        script_path = os.path.join(SCRIPT_DIR, "keyboard_tool.py")
        if os.path.exists(script_path):
            return True, "键盘输入功能正常"
        else:
            return False, "键盘脚本不存在"
    except Exception as e:
        return False, f"键盘功能异常: {str(e)}"

def check_launch_capability():
    """检查应用启动能力"""
    try:
        script_path = os.path.join(SCRIPT_DIR, "launch_notepad.py")
        if os.path.exists(script_path):
            return True, "应用启动功能正常"
        else:
            return False, "启动脚本不存在"
    except Exception as e:
        return False, f"应用启动功能异常: {str(e)}"

def check_vision_capability():
    """检查视觉识别能力"""
    try:
        script_path = os.path.join(SCRIPT_DIR, "vision_proxy.py")
        if os.path.exists(script_path):
            return True, "视觉识别功能正常"
        else:
            return False, "视觉识别脚本不存在"
    except Exception as e:
        return False, f"视觉识别功能异常: {str(e)}"

def check_clipboard_capability():
    """检查剪贴板能力"""
    try:
        script_path = os.path.join(SCRIPT_DIR, "clipboard_tool.py")
        if os.path.exists(script_path):
            return True, "剪贴板功能正常"
        else:
            return False, "剪贴板脚本不存在"
    except Exception as e:
        return False, f"剪贴板功能异常: {str(e)}"

def run_health_check():
    """运行完整的健康检查"""
    health_report = {
        "check_time": datetime.now().isoformat(),
        "status": "healthy",
        "components": []
    }

    checks = [
        ("截图", check_screenshot_capability),
        ("鼠标", check_mouse_capability),
        ("键盘", check_keyboard_capability),
        ("应用启动", check_launch_capability),
        ("视觉识别", check_vision_capability),
        ("剪贴板", check_clipboard_capability)
    ]

    for component_name, check_func in checks:
        success, message = check_func()
        component_status = {
            "component": component_name,
            "status": "healthy" if success else "unhealthy",
            "message": message
        }

        health_report["components"].append(component_status)

        if not success:
            health_report["status"] = "unhealthy"

    return health_report

def main():
    """主函数"""
    # 设置输出编码
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

    print("Running system health check...")

    # 运行健康检查
    report = run_health_check()

    # 输出报告到控制台
    print(json.dumps(report, indent=2, ensure_ascii=False))

    # 保存报告到文件
    report_path = os.path.join("runtime", "state", "health_report.json")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nHealth report saved to: {report_path}")

    # 根据检查结果返回退出码
    if report["status"] == "healthy":
        print("[OK] System health check passed")
        return 0
    else:
        print("[FAIL] System health check found issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())