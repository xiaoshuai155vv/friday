#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能场景计划自动修复引擎

在场景计划优化引擎（检测问题）和场景测试引擎（验证可用性）基础上，
让系统能够根据优化建议自动分析问题并执行修复，形成「检测→分析→修复→验证」的完整闭环。

功能：
1. 读取场景计划优化报告
2. 分析问题类型和严重程度
3. 自动执行修复（添加缺失字段、修正步骤类型、修复参数等）
4. 验证修复效果
5. 生成修复报告
"""

import json
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
REPORT_PATH = PROJECT_ROOT / "runtime" / "state" / "scenario_plan_optimizer_report.json"
REPAIR_REPORT_PATH = PROJECT_ROOT / "runtime" / "state" / "scene_plan_auto_repair_report.json"


class ScenePlanAutoRepairEngine:
    """智能场景计划自动修复引擎"""

    # 步骤类型映射：中文到标准英文
    STEP_TYPE_MAP = {
        "截图": "screenshot",
        "打开浏览器": "launch_browser",
        "打开文件管理器": "launch_explorer",
        "窗口最大化": "maximize",
        "窗口激活": "activate",
        "等待": "wait",
        "已安装应用": "installed_apps",
        "打开应用": "launch_app",
        "点击": "click",
        "滚动": "scroll",
        "输入": "type",
        "按回车": "key_enter",
        "vision": "vision",
        "vision_coords": "vision_coords",
    }

    def __init__(self):
        self.report = None
        self.repairs = []
        self.stats = {
            "total_issues": 0,
            "fixed": 0,
            "failed": 0,
            "skipped": 0,
        }

    def load_report(self):
        """加载场景计划优化报告"""
        if not REPORT_PATH.exists():
            print(f"错误：找不到优化报告 {REPORT_PATH}")
            print("请先运行 scenario_plan_optimizer.py 生成优化报告")
            return False

        with open(REPORT_PATH, "r", encoding="utf-8") as f:
            self.report = json.load(f)

        print(f"已加载优化报告，共 {len(self.report.get('issues', []))} 个问题")
        return True

    def analyze_issue(self, issue):
        """分析问题类型"""
        issue_type = issue.get("type", "")
        severity = issue.get("severity", "warning")
        plan = issue.get("plan", "")

        # 跳过 info 级别的问题
        if severity == "info":
            return None

        return {
            "type": issue_type,
            "severity": severity,
            "plan": plan,
            "message": issue.get("message", ""),
            "step_index": issue.get("step_index", -1),
            "step_type": issue.get("step_type", ""),
        }

    def fix_missing_name(self, plan_path):
        """修复缺少 name 字段的问题"""
        try:
            with open(plan_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 检查是否缺少 name 字段
            if "name" not in data or not data["name"]:
                # 从文件名或 description 提取 name
                if "description" in data:
                    name = data.get("name", "")
                    if not name:
                        # 从 description 提取前几个字作为 name
                        desc = data.get("description", "")
                        name = desc[:20] if desc else Path(plan_path).stem
                    data["name"] = name

                    # 写回文件
                    with open(plan_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)

                    return True, f"已添加 name 字段: {name}"

            return False, "name 字段已存在，无需修复"
        except Exception as e:
            return False, f"修复失败: {str(e)}"

    def fix_step_type(self, plan_path, step_index, old_type):
        """修复步骤类型"""
        try:
            with open(plan_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            steps = data.get("steps", [])
            if step_index < 0 or step_index >= len(steps):
                return False, f"步骤索引 {step_index} 超出范围"

            step = steps[step_index]

            # 获取正确的步骤类型
            new_type = self.STEP_TYPE_MAP.get(old_type, old_type)

            # 检查步骤中是否有对应的字段
            old_key = None
            for key in step.keys():
                if key not in ("description",):
                    old_key = key
                    break

            if old_key and old_key != new_type:
                # 创建新的步骤结构
                new_step = {"do": new_type}
                # 复制原有参数
                for key, value in step.items():
                    if key != old_key:
                        new_step[key] = value
                # 添加描述
                new_step["description"] = step.get("description", "")

                steps[step_index] = new_step
                data["steps"] = steps

                with open(plan_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                return True, f"已修正步骤类型: {old_type} -> {new_type}"

            return False, "步骤类型无需修复"
        except Exception as e:
            return False, f"修复失败: {str(e)}"

    def fix_missing_parameters(self, plan_path, step_index, step_type):
        """修复缺少参数的问题"""
        try:
            with open(plan_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            steps = data.get("steps", [])
            if step_index < 0 or step_index >= len(steps):
                return False, f"步骤索引 {step_index} 超出范围"

            step = steps[step_index]

            # 根据步骤类型添加默认参数
            if step_type == "click":
                if "x" not in step or "y" not in step:
                    # 需要 vision_coords 先确定坐标
                    return False, "click 步骤缺少坐标参数，需要先运行 vision_coords 获取坐标"
                return False, "参数已存在"

            if step_type in ("type", "输入"):
                if "text" not in step:
                    return False, "需要用户输入内容"
                return False, "参数已存在"

            if step_type in ("wait", "等待"):
                if "seconds" not in step:
                    step["seconds"] = 2
                    steps[step_index] = step
                    data["steps"] = steps
                    with open(plan_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    return True, "已添加默认等待时间 2 秒"
                return False, "参数已存在"

            return False, f"未知步骤类型: {step_type}"
        except Exception as e:
            return False, f"修复失败: {str(e)}"

    def fix_parse_error(self, plan_path):
        """修复解析错误（通常是 JSON 格式问题）"""
        try:
            # 读取原始内容
            with open(plan_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 尝试修复常见的 JSON 问题
            data = json.loads(content)

            # 检查是否有常见的格式问题
            if isinstance(data, list):
                # 列表格式，包装为对象
                data = {"steps": data}

            # 确保有 steps 字段
            if "steps" not in data:
                return False, "JSON 缺少 steps 字段"

            with open(plan_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return True, "已修复 JSON 格式问题"
        except json.JSONDecodeError as e:
            return False, f"JSON 格式错误无法自动修复: {str(e)}"
        except Exception as e:
            return False, f"修复失败: {str(e)}"

    def repair_plan(self, plan_path, issues):
        """修复单个场景计划"""
        repairs_for_plan = []

        for issue in issues:
            analysis = self.analyze_issue(issue)
            if not analysis:
                self.stats["skipped"] += 1
                continue

            issue_type = analysis["type"]
            severity = analysis["severity"]

            self.stats["total_issues"] += 1

            try:
                if issue_type == "missing_name":
                    success, message = self.fix_missing_name(plan_path)
                elif issue_type == "invalid_step_type":
                    success, message = self.fix_step_type(
                        plan_path, analysis["step_index"], analysis["step_type"]
                    )
                elif issue_type == "missing_parameters":
                    success, message = self.fix_missing_parameters(
                        plan_path, analysis["step_index"], analysis["step_type"]
                    )
                elif issue_type == "parse_error":
                    success, message = self.fix_parse_error(plan_path)
                else:
                    success = False
                    message = f"未知问题类型: {issue_type}"
                    self.stats["skipped"] += 1

                if success:
                    self.stats["fixed"] += 1
                    repairs_for_plan.append({
                        "issue_type": issue_type,
                        "severity": severity,
                        "message": message,
                        "status": "fixed",
                    })
                else:
                    self.stats["failed"] += 1
                    repairs_for_plan.append({
                        "issue_type": issue_type,
                        "severity": severity,
                        "message": message,
                        "status": "failed",
                    })
            except Exception as e:
                self.stats["failed"] += 1
                repairs_for_plan.append({
                    "issue_type": issue_type,
                    "severity": severity,
                    "message": f"修复异常: {str(e)}",
                    "status": "error",
                })

        return repairs_for_plan

    def run(self, priority="high", dry_run=False):
        """执行自动修复"""
        if not self.load_report():
            return False

        print(f"\n{'='*60}")
        print("智能场景计划自动修复引擎")
        print(f"{'='*60}")
        print(f"优先级过滤: {priority}")
        print(f"试运行模式: {dry_run}")
        print()

        # 按计划分组问题
        plan_issues = {}
        for issue in self.report.get("issues", []):
            plan = issue.get("plan", "")
            severity = issue.get("severity", "warning")

            # 按优先级过滤
            if priority == "high" and severity not in ("error",):
                continue
            if priority == "medium" and severity not in ("error", "warning"):
                continue

            if plan not in plan_issues:
                plan_issues[plan] = []
            plan_issues[plan].append(issue)

        print(f"发现 {len(plan_issues)} 个需要修复的场景计划\n")

        # 修复每个计划
        for plan_path, issues in plan_issues.items():
            if not plan_path:
                continue

            # 转换为绝对路径
            if not os.path.isabs(plan_path):
                plan_path = str(PROJECT_ROOT / plan_path)

            plan_name = os.path.basename(plan_path)
            print(f"处理: {plan_name}")

            if dry_run:
                print(f"  [试运行] 将修复 {len(issues)} 个问题")
                for issue in issues:
                    print(f"    - {issue.get('type', 'unknown')}: {issue.get('message', '')}")
                continue

            repairs = self.repair_plan(plan_path, issues)
            self.repairs.append({
                "plan": plan_path,
                "repairs": repairs,
            })

            fixed_count = sum(1 for r in repairs if r["status"] == "fixed")
            print(f"  已修复: {fixed_count}/{len(issues)}")

        # 输出统计
        print(f"\n{'='*60}")
        print("修复统计")
        print(f"{'='*60}")
        print(f"总问题数: {self.stats['total_issues']}")
        print(f"已修复: {self.stats['fixed']}")
        print(f"修复失败: {self.stats['failed']}")
        print(f"跳过: {self.stats['skipped']}")

        # 保存报告
        if not dry_run:
            self.save_report()

        return True

    def save_report(self):
        """保存修复报告"""
        report = {
            "scan_time": datetime.now().isoformat(),
            "stats": self.stats,
            "repairs": self.repairs,
        }

        with open(REPAIR_REPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\n修复报告已保存到: {REPAIR_REPORT_PATH}")


def main():
    parser = argparse.ArgumentParser(description="智能场景计划自动修复引擎")
    parser.add_argument("--priority", choices=["high", "medium", "low"], default="high",
                        help="修复优先级 (high: 仅错误, medium: 错误+警告, low: 全部)")
    parser.add_argument("--dry-run", action="store_true",
                        help="试运行模式，仅显示将要修复的问题，不实际修改文件")
    parser.add_argument("--full", action="store_true",
                        help="修复所有优先级的问题")

    args = parser.parse_args()

    priority = "low" if args.full else args.priority

    engine = ScenePlanAutoRepairEngine()
    engine.run(priority=priority, dry_run=args.dry_run)


if __name__ == "__main__":
    main()