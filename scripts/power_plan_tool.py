#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电源计划控制（Windows）。
支持查询和切换系统电源计划。
"""
import sys
import subprocess
import json
if sys.platform != "win32":
    sys.exit(1)

def get_power_plans():
    """
    获取所有可用的电源计划及其描述。
    返回: dict - {plan_guid: plan_name}
    """
    try:
        # 使用 powercfg 查询所有电源计划
        result = subprocess.run(
            ["powercfg", "/L"],
            capture_output=True,
            check=True
        )

        # 处理输出编码
        try:
            output = result.stdout.decode('gbk')
        except:
            output = result.stdout.decode('utf-8', errors='ignore')

        plans = {}
        lines = output.strip().split('\n')

        for line in lines:
            # 查找 GUID
            if '{' in line and '}' in line:
                guid_start = line.find('{')
                guid_end = line.find('}')
                guid = line[guid_start:guid_end+1]

                # 提取计划名称（括号内的部分）
                if '(' in line and ')' in line:
                    name_start = line.rfind('(') + 1
                    name_end = line.rfind(')')
                    plan_name = line[name_start:name_end].strip()

                    # 判断是否是当前活动计划
                    is_active = '*' in line[:name_start]

                    if plan_name and guid:
                        plans[guid] = plan_name

        return plans
    except subprocess.CalledProcessError:
        return {}

def get_active_power_plan():
    """
    获取当前活动的电源计划。
    返回: str - 当前活动电源计划的 GUID
    """
    try:
        result = subprocess.run(
            ["powercfg", "/GETACTIVESCHEME"],
            capture_output=True,
            check=True
        )

        # 处理输出编码
        try:
            output = result.stdout.decode('gbk')
        except:
            output = result.stdout.decode('utf-8', errors='ignore')

        lines = output.strip().split('\n')
        for line in lines:
            if 'GUID' in line:
                guid_start = line.find('{')
                guid_end = line.find('}')
                if guid_start != -1 and guid_end != -1:
                    return line[guid_start:guid_end+1]
    except subprocess.CalledProcessError:
        pass

    return None

def set_power_plan(plan_guid):
    """
    设置指定的电源计划。
    plan_guid: str - 电源计划的 GUID
    """
    try:
        result = subprocess.run(
            ["powercfg", "/S", plan_guid],
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False

def list_power_plans():
    """
    列出所有电源计划并返回格式化的字符串。
    """
    plans = get_power_plans()
    active_plan = get_active_power_plan()

    if not plans:
        return "无法获取电源计划列表"

    result = []
    for guid, name in plans.items():
        if guid == active_plan:
            result.append(f"* {name} (当前)")
        else:
            result.append(f"  {name}")

    return "\n".join(result)

def switch_power_plan(plan_name):
    """
    根据名称切换电源计划。
    plan_name: str - 电源计划名称
    """
    plans = get_power_plans()

    # 查找匹配的电源计划
    target_guid = None
    for guid, name in plans.items():
        if name.lower() == plan_name.lower():
            target_guid = guid
            break

    if not target_guid:
        return f"未找到电源计划: {plan_name}"

    # 切换电源计划
    if set_power_plan(target_guid):
        return f"已切换到电源计划: {plan_name}"
    else:
        return f"切换电源计划失败: {plan_name}"

def main():
    if len(sys.argv) < 2:
        print("usage: power_plan_tool.py list | switch <plan_name>", file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "list":
        print(list_power_plans())
        return 0
    elif cmd == "switch":
        if len(sys.argv) < 3:
            print("usage: power_plan_tool.py switch <plan_name>", file=sys.stderr)
            sys.exit(1)
        plan_name = sys.argv[2]
        print(switch_power_plan(plan_name))
        return 0
    else:
        print("usage: power_plan_tool.py list | switch <plan_name>", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())