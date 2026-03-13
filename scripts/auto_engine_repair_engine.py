#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能引擎自动修复引擎
让系统能够基于质量保障引擎的检测结果，自动分析失败原因并尝试修复，形成检测→分析→修复的完整闭环

功能：
1. 读取质量保障引擎的检测结果
2. 分析失败原因（依赖缺失、语法错误、导入问题等）
3. 尝试自动修复（安装依赖、修复语法错误等）
4. 验证修复效果
5. 生成修复报告
"""

import os
import sys
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
RUNTIME_STATE_DIR = PROJECT_ROOT / "runtime" / "state"


class AutoEngineRepairEngine:
    """智能引擎自动修复引擎"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.scripts_dir = SCRIPTS_DIR
        self.repair_results = {
            "timestamp": datetime.now().isoformat(),
            "total_failures": 0,
            "repaired": 0,
            "failed": 0,
            "cannot_repair": 0,
            "repairs": []
        }

    def load_quality_results(self):
        """加载质量保障引擎的检测结果"""
        results_file = RUNTIME_STATE_DIR / "auto_quality_assurance_results.json"

        if not results_file.exists():
            # 如果没有检测结果，先运行质量检测
            print("未找到质量检测结果，正在运行检测...")
            subprocess.run([sys.executable, str(PROJECT_ROOT / "scripts" / "auto_quality_assurance_engine.py"), "--run"])

        if results_file.exists():
            with open(results_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def analyze_failure(self, engine_name, error_message):
        """分析失败原因"""
        analysis = {
            "engine": engine_name,
            "error": error_message,
            "cause": None,
            "repair_action": None,
            "can_repair": False
        }

        error_lower = error_message.lower() if error_message else ""

        # 分析失败原因并确定修复方案
        if "no module named" in error_lower or "modulenotfounderror" in error_lower:
            # 缺少模块
            match = re.search(r"no module named ['\"]?([^'\"]+)['\"]?", error_lower)
            if match:
                module_name = match.group(1)
                analysis["cause"] = f"缺少依赖模块: {module_name}"
                analysis["repair_action"] = f"pip install {module_name}"
                analysis["can_repair"] = True

        elif "importerror" in error_lower or "import error" in error_lower:
            # 导入错误
            if "cannot import" in error_lower:
                match = re.search(r"cannot import ['\"]?([^'\"]+)['\"]?", error_lower)
                if match:
                    analysis["cause"] = f"导入错误: {match.group(1)}"
                    analysis["repair_action"] = "检查模块导入路径和依赖"
                    analysis["can_repair"] = True
            else:
                analysis["cause"] = "导入错误"
                analysis["repair_action"] = "检查模块代码和依赖"
                analysis["can_repair"] = True

        elif "syntaxerror" in error_lower:
            # 语法错误
            analysis["cause"] = "Python 语法错误"
            analysis["repair_action"] = "手动修复语法错误（需要人工）"
            analysis["can_repair"] = False

        elif "indentationerror" in error_lower:
            # 缩进错误
            analysis["cause"] = "缩进错误"
            analysis["repair_action"] = "手动修复缩进（需要人工）"
            analysis["can_repair"] = False

        elif "attributeerror" in error_lower:
            # 属性错误
            analysis["cause"] = "属性访问错误"
            analysis["repair_action"] = "检查对象属性和方法"
            analysis["can_repair"] = False

        elif "timeout" in error_lower:
            # 超时
            analysis["cause"] = "执行超时"
            analysis["repair_action"] = "增加超时时间或优化代码"
            analysis["can_repair"] = False

        elif "permission" in error_lower or "权限" in error_message:
            # 权限问题
            analysis["cause"] = "权限不足"
            analysis["repair_action"] = "检查文件权限"
            analysis["can_repair"] = False

        else:
            analysis["cause"] = "未知错误"
            analysis["repair_action"] = "需要人工分析"
            analysis["can_repair"] = False

        return analysis

    def repair_dependency(self, module_name):
        """尝试安装缺失的依赖"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", module_name],
                capture_output=True,
                text=True,
                timeout=120
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)

    def repair_engine(self, engine_info):
        """修复单个引擎"""
        engine_name = engine_info["name"]
        error = engine_info.get("import_result", {}).get("error") or \
                engine_info.get("capability_result", {}).get("error")

        if not error:
            return None

        # 分析失败原因
        analysis = self.analyze_failure(engine_name, error)

        repair_result = {
            "engine": engine_name,
            "analysis": analysis,
            "repair_attempted": False,
            "repair_successful": False,
            "repair_output": None
        }

        if analysis["can_repair"] and analysis["repair_action"]:
            repair_result["repair_attempted"] = True

            # 尝试修复
            if analysis["repair_action"].startswith("pip install"):
                # 尝试安装依赖
                module_name = analysis["repair_action"].replace("pip install ", "")
                print(f"尝试修复 {engine_name}: 安装依赖 {module_name}...")

                success, output = self.repair_dependency(module_name)
                repair_result["repair_successful"] = success
                repair_result["repair_output"] = output

                if success:
                    self.repair_results["repaired"] += 1
                else:
                    self.repair_results["cannot_repair"] += 1
            else:
                # 其他类型的修复需要人工
                repair_result["repair_output"] = analysis["repair_action"]
                self.repair_results["cannot_repair"] += 1
        else:
            self.repair_results["cannot_repair"] += 1

        return repair_result

    def run_quality_check(self):
        """运行质量检测获取最新结果"""
        print("=" * 60)
        print("智能引擎自动修复引擎")
        print("=" * 60)

        print("\n[1/4] 运行质量检测...")
        subprocess.run([sys.executable, str(PROJECT_ROOT / "scripts" / "auto_quality_assurance_engine.py"), "--run"])

    def analyze_and_repair(self):
        """分析失败并尝试修复"""
        print("\n[2/4] 分析失败原因...")

        # 加载质量检测结果
        quality_results = self.load_quality_results()

        if not quality_results:
            print("无法加载质量检测结果")
            return

        # 找到失败的引擎
        failed_engines = [
            e for e in quality_results.get("engines", [])
            if e.get("overall_status") == "fail"
        ]

        self.repair_results["total_failures"] = len(failed_engines)

        print(f"发现 {len(failed_engines)} 个失败的引擎")

        # 尝试修复每个失败的引擎
        for engine in failed_engines:
            print(f"\n分析引擎: {engine['name']}")
            result = self.repair_engine(engine)

            if result:
                self.repair_results["repairs"].append(result)

                if result["repair_attempted"]:
                    status = "成功" if result["repair_successful"] else "失败"
                    print(f"  修复尝试: {status}")
                    if result["repair_output"]:
                        # 只显示前几行
                        lines = result["repair_output"].strip().split('\n')[:3]
                        for line in lines:
                            print(f"    {line}")
                else:
                    print(f"  原因: {result['analysis']['cause']}")
                    print(f"  建议: {result['analysis']['repair_action']}")

    def verify_repairs(self):
        """验证修复效果"""
        print("\n[3/4] 验证修复效果...")

        # 重新运行质量检测
        subprocess.run([sys.executable, str(PROJECT_ROOT / "scripts" / "auto_quality_assurance_engine.py"), "--run"])

        # 加载新的结果
        quality_results = self.load_quality_results()

        if quality_results:
            self.repair_results["verification"] = {
                "total_engines": quality_results.get("total_engines", 0),
                "passed": quality_results.get("passed", 0),
                "failed": quality_results.get("failed", 0),
                "pass_rate": quality_results.get("passed", 0) / max(1, quality_results.get("total_engines", 1)) * 100
            }

    def generate_report(self):
        """生成修复报告"""
        print("\n[4/4] 生成修复报告...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_failures": self.repair_results["total_failures"],
                "repaired": self.repair_results["repaired"],
                "cannot_repair": self.repair_results["cannot_repair"],
                "repair_rate": f"{(self.repair_results['repaired'] / max(1, self.repair_results['total_failures'])) * 100:.1f}%"
            },
            "repairs": self.repair_results["repairs"],
            "verification": self.repair_results.get("verification", {})
        }

        # 保存报告
        report_file = RUNTIME_STATE_DIR / "auto_engine_repair_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        return report, str(report_file)

    def run(self):
        """运行自动修复流程"""
        print("=" * 60)
        print("智能引擎自动修复引擎")
        print("=" * 60)

        # 1. 运行质量检测
        print("\n[1/4] 运行质量检测...")
        subprocess.run([sys.executable, str(PROJECT_ROOT / "scripts" / "auto_quality_assurance_engine.py"), "--run"])

        # 2. 分析失败并尝试修复
        print("\n[2/4] 分析失败原因并尝试修复...")
        self.analyze_and_repair()

        # 3. 验证修复效果
        print("\n[3/4] 验证修复效果...")
        self.verify_repairs()

        # 4. 生成报告
        print("\n[4/4] 生成修复报告...")
        report, report_file = self.generate_report()

        # 打印摘要
        print("\n" + "=" * 60)
        print("修复结果摘要")
        print("=" * 60)
        print(f"总失败数: {report['summary']['total_failures']}")
        print(f"成功修复: {report['summary']['repaired']}")
        print(f"无法修复: {report['summary']['cannot_repair']}")
        print(f"修复率: {report['summary']['repair_rate']}")

        if "verification" in report and report["verification"]:
            print(f"\n验证结果:")
            print(f"  总引擎数: {report['verification'].get('total_engines', 0)}")
            print(f"  通过: {report['verification'].get('passed', 0)}")
            print(f"  失败: {report['verification'].get('failed', 0)}")
            print(f"  通过率: {report['verification'].get('pass_rate', 0):.1f}%")

        print(f"\n详细报告已保存至: {report_file}")

        return report


def main():
    """CLI 入口"""
    import argparse

    parser = argparse.ArgumentParser(description="智能引擎自动修复引擎")
    parser.add_argument("--run", action="store_true", help="运行自动修复")
    parser.add_argument("--repair", action="store_true", help="只运行修复分析")
    parser.add_argument("--status", action="store_true", help="查看修复状态")
    parser.add_argument("--verify", action="store_true", help="验证修复效果")

    args = parser.parse_args()

    engine = AutoEngineRepairEngine()

    if args.run or args.repair or args.status or args.verify:
        if args.run:
            engine.run()
        elif args.repair:
            engine.analyze_and_repair()
            report, _ = engine.generate_report()
            print("\n修复结果:")
            print(f"  总失败数: {report['summary']['total_failures']}")
            print(f"  成功修复: {report['summary']['repaired']}")
            print(f"  无法修复: {report['summary']['cannot_repair']}")
        elif args.status:
            report_file = RUNTIME_STATE_DIR / "auto_engine_repair_report.json"
            if report_file.exists():
                with open(report_file, 'r', encoding='utf-8') as f:
                    report = json.load(f)
                print(f"上次修复时间: {report.get('timestamp', '未知')}")
                print(f"总失败数: {report['summary']['total_failures']}")
                print(f"成功修复: {report['summary']['repaired']}")
                print(f"修复率: {report['summary']['repair_rate']}")
            else:
                print("尚未运行自动修复，请使用 --run 参数运行")
        elif args.verify:
            engine.verify_repairs()
            print("验证完成")
    else:
        # 默认运行
        engine.run()


if __name__ == "__main__":
    main()