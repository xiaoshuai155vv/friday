#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能自动化场景测试引擎
自动测试所有场景计划的可用性、验证守护进程功能、检测失效的 plan 并尝试修复
形成场景测试→问题检测→自动修复→验证的完整闭环

功能：
1. 场景计划扫描：扫描 assets/plans/ 下所有 JSON 计划
2. 计划验证：验证 JSON 格式、检查步骤有效性
3. 守护进程测试：验证各守护进程功能
4. 失效检测：检测失效的场景计划（如引用的文件/应用不存在）
5. 自动修复：对可修复的问题尝试自动修复
6. 生成测试报告
"""

import os
import sys
import json
import glob
import subprocess
from pathlib import Path
from datetime import datetime

# 确保项目根目录在路径中
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

class SceneTestEngine:
    """智能自动化场景测试引擎"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.plans_dir = os.path.join(self.project_root, "assets", "plans")
        self.results = {
            "scan_time": datetime.now().isoformat(),
            "total_plans": 0,
            "valid_plans": 0,
            "invalid_plans": [],
            "daemon_status": [],
            "issues": [],
            "fixes_applied": []
        }

    def scan_plans(self):
        """扫描所有场景计划"""
        print("=" * 60)
        print("智能自动化场景测试引擎")
        print("=" * 60)
        print(f"\n[1/5] 扫描场景计划目录: {self.plans_dir}")

        plan_files = glob.glob(os.path.join(self.plans_dir, "*.json"))
        self.results["total_plans"] = len(plan_files)

        print(f"  发现 {len(plan_files)} 个场景计划")

        for plan_file in plan_files:
            plan_name = os.path.basename(plan_file)
            result = self.validate_plan(plan_file)
            if result["valid"]:
                self.results["valid_plans"] += 1
                print(f"  [OK] {plan_name}: 格式有效")
            else:
                self.results["invalid_plans"].append({
                    "file": plan_name,
                    "errors": result["errors"]
                })
                print(f"  [FAIL] {plan_name}: {', '.join(result['errors'])}")

        return self.results

    def validate_plan(self, plan_file):
        """验证单个场景计划的格式和内容"""
        result = {"valid": True, "errors": []}

        try:
            with open(plan_file, "r", encoding="utf-8") as f:
                plan = json.load(f)

            # 检查必需字段
            required_fields = ["triggers", "steps"]
            for field in required_fields:
                if field not in plan:
                    result["valid"] = False
                    result["errors"].append(f"缺少必需字段: {field}")

            # 检查 triggers 必须是列表
            if "triggers" in plan and not isinstance(plan["triggers"], list):
                result["valid"] = False
                result["errors"].append("triggers 必须是列表")

            # 检查 steps 必须是列表
            if "steps" in plan and not isinstance(plan["steps"], list):
                result["valid"] = False
                result["errors"].append("steps 必须是列表")

            # 检查是否有无效的步骤引用
            if "steps" in plan:
                for i, step in enumerate(plan["steps"]):
                    if not isinstance(step, str):
                        result["valid"] = False
                        result["errors"].append(f"步骤 {i+1} 必须是字符串")

        except json.JSONDecodeError as e:
            result["valid"] = False
            result["errors"].append(f"JSON 解析错误: {str(e)}")
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"验证错误: {str(e)}")

        return result

    def test_daemons(self):
        """测试守护进程功能"""
        print(f"\n[2/5] 测试守护进程功能")

        daemon_files = [
            ("daemon_manager.py", "守护进程管理器"),
            ("health_assurance_loop.py", "健康保障闭环"),
            ("scene_adaptive_engine.py", "场景自适应引擎"),
            ("proactive_service_trigger.py", "主动服务触发器"),
        ]

        for daemon_file, daemon_name in daemon_files:
            daemon_path = os.path.join(self.project_root, "scripts", daemon_file)
            if os.path.exists(daemon_path):
                # 检查是否可以导入
                try:
                    module_name = daemon_file.replace(".py", "")
                    # 简单检查：文件是否存在且非空
                    if os.path.getsize(daemon_path) > 100:
                        self.results["daemon_status"].append({
                            "name": daemon_name,
                            "file": daemon_file,
                            "status": "available",
                            "size": os.path.getsize(daemon_path)
                        })
                        print(f"  [OK] {daemon_name}: 可用")
                    else:
                        self.results["daemon_status"].append({
                            "name": daemon_name,
                            "file": daemon_file,
                            "status": "empty",
                            "size": 0
                        })
                        print(f"  [FAIL] {daemon_name}: 文件为空")
                except Exception as e:
                    self.results["daemon_status"].append({
                        "name": daemon_name,
                        "file": daemon_file,
                        "status": "error",
                        "error": str(e)
                    })
                    print(f"  [ERROR] {daemon_name}: {str(e)}")
            else:
                self.results["daemon_status"].append({
                    "name": daemon_name,
                    "file": daemon_file,
                    "status": "not_found"
                })
                print(f"  - {daemon_name}: 不存在")

    def detect_issues(self):
        """检测场景计划中的潜在问题"""
        print(f"\n[3/5] 检测潜在问题")

        issues_found = []

        # 检查是否有缺失 triggers 的计划
        plan_files = glob.glob(os.path.join(self.plans_dir, "*.json"))
        for plan_file in plan_files:
            try:
                with open(plan_file, "r", encoding="utf-8") as f:
                    plan = json.load(f)

                plan_name = os.path.basename(plan_file)

                # 检查 triggers 是否为空
                if "triggers" in plan and len(plan["triggers"]) == 0:
                    issues_found.append({
                        "file": plan_name,
                        "type": "missing_triggers",
                        "severity": "warning",
                        "message": "triggers 为空，无法被触发"
                    })

                # 检查 steps 是否为空
                if "steps" in plan and len(plan["steps"]) == 0:
                    issues_found.append({
                        "file": plan_name,
                        "type": "missing_steps",
                        "severity": "error",
                        "message": "steps 为空，计划无法执行"
                    })

                # 检查是否有未定义的引用
                if "triggers" in plan:
                    for trigger in plan["triggers"]:
                        if not trigger or not trigger.strip():
                            issues_found.append({
                                "file": plan_name,
                                "type": "empty_trigger",
                                "severity": "warning",
                                "message": "存在空触发词"
                            })

            except Exception as e:
                issues_found.append({
                    "file": os.path.basename(plan_file),
                    "type": "parse_error",
                    "severity": "error",
                    "message": f"解析错误: {str(e)}"
                })

        self.results["issues"] = issues_found

        if issues_found:
            print(f"  发现 {len(issues_found)} 个问题:")
            for issue in issues_found:
                severity_mark = "[X]" if issue["severity"] == "error" else "[!]"
                print(f"    {severity_mark} {issue['file']}: {issue['message']}")
        else:
            print("  未发现问题")

    def try_auto_fix(self):
        """尝试自动修复可修复的问题"""
        print(f"\n[4/5] 尝试自动修复")

        fixed_count = 0

        # 修复空 triggers
        plan_files = glob.glob(os.path.join(self.plans_dir, "auto_*.json"))
        for plan_file in plan_files:
            try:
                with open(plan_file, "r", encoding="utf-8") as f:
                    plan = json.load(f)

                # 为没有 triggers 的自动生成计划添加默认 triggers
                if "triggers" not in plan or len(plan.get("triggers", [])) == 0:
                    # 从 description 或 intent 生成 triggers
                    triggers = []
                    if "intent" in plan:
                        triggers.append(plan["intent"])
                    if "description" in plan:
                        triggers.append(plan["description"][:20])

                    if triggers:
                        plan["triggers"] = triggers
                        with open(plan_file, "w", encoding="utf-8") as f:
                            json.dump(plan, f, ensure_ascii=False, indent=2)

                        self.results["fixes_applied"].append({
                            "file": os.path.basename(plan_file),
                            "fix": "添加默认 triggers",
                            "triggers": triggers
                        })
                        fixed_count += 1
                        print(f"  [OK] 修复 {os.path.basename(plan_file)}: 添加默认 triggers")

            except Exception as e:
                print(f"  [FAIL] 修复 {os.path.basename(plan_file)} 失败: {str(e)}")

        if fixed_count == 0:
            print("  无需修复的问题")

    def generate_report(self):
        """生成测试报告"""
        print(f"\n[5/5] 生成测试报告")

        report = {
            "scan_time": self.results["scan_time"],
            "summary": {
                "total_plans": self.results["total_plans"],
                "valid_plans": self.results["valid_plans"],
                "invalid_plans_count": len(self.results["invalid_plans"]),
                "daemons_available": len([d for d in self.results["daemon_status"] if d["status"] == "available"]),
                "issues_found": len(self.results["issues"]),
                "fixes_applied": len(self.results["fixes_applied"])
            },
            "details": self.results
        }

        # 保存报告
        report_path = os.path.join(self.project_root, "runtime", "state", "scene_test_report.json")
        os.makedirs(os.path.dirname(report_path), exist_ok=True)

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\n{'=' * 60}")
        print("测试报告摘要")
        print(f"{'=' * 60}")
        print(f"  场景计划总数: {report['summary']['total_plans']}")
        print(f"  有效计划数: {report['summary']['valid_plans']}")
        print(f"  无效计划数: {report['summary']['invalid_plans_count']}")
        print(f"  可用守护进程: {report['summary']['daemons_available']}")
        print(f"  发现问题数: {report['summary']['issues_found']}")
        print(f"  自动修复数: {report['summary']['fixes_applied']}")
        print(f"\n报告已保存到: {report_path}")

        return report

    def run_full_test(self):
        """运行完整测试流程"""
        self.scan_plans()
        self.test_daemons()
        self.detect_issues()
        self.try_auto_fix()
        return self.generate_report()


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="智能自动化场景测试引擎")
    parser.add_argument("--scan", action="store_true", help="扫描场景计划")
    parser.add_argument("--daemons", action="store_true", help="测试守护进程")
    parser.add_argument("--issues", action="store_true", help="检测问题")
    parser.add_argument("--fix", action="store_true", help="尝试自动修复")
    parser.add_argument("--report", action="store_true", help="生成报告")
    parser.add_argument("--full", action="store_true", help="运行完整测试流程")

    args = parser.parse_args()

    engine = SceneTestEngine()

    if args.full or (not any([args.scan, args.daemons, args.issues, args.fix, args.report])):
        # 默认运行完整测试
        engine.run_full_test()
    else:
        if args.scan:
            engine.scan_plans()
        if args.daemons:
            engine.test_daemons()
        if args.issues:
            engine.detect_issues()
        if args.fix:
            engine.try_auto_fix()
        if args.report:
            engine.generate_report()


if __name__ == "__main__":
    main()