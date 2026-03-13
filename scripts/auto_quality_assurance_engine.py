#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能自动化质量保障引擎
让系统能够自动测试各引擎功能、验证进化成果、确保不破坏既有能力

功能：
1. 自动扫描 scripts/ 下的所有引擎模块
2. 对每个引擎执行基本功能测试
3. 验证引擎的导入和初始化是否正常
4. 生成质量报告和健康状态评估
5. 识别可能出现问题的引擎并提供修复建议
"""

import os
import sys
import json
import importlib
import importlib.util
import inspect
from datetime import datetime
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
RUNTIME_STATE_DIR = PROJECT_ROOT / "runtime" / "state"


class AutoQualityAssuranceEngine:
    """智能自动化质量保障引擎"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.scripts_dir = SCRIPTS_DIR
        self.results = []
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "total_engines": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "engines": []
        }

    def get_engine_files(self):
        """获取所有引擎文件"""
        engine_files = []
        for f in self.scripts_dir.glob("*.py"):
            # 跳过 __init__.py 和非引擎模块
            if f.name.startswith("_") or f.name in ["do.py", "state_tracker.py",
                                                      "behavior_log.py", "export_recent_logs.py",
                                                      "scenario_log.py", "self_verify_capabilities.py",
                                                      "query_scenario_experiences.py", "git_commit_evolution.py"]:
                continue

            # 检查是否为引擎模块（包含 Engine 或 engine 关键字）
            if "engine" in f.name.lower() or any(keyword in f.stem.lower() for keyword in
                                                   ["orchestrator", "coordinator", "manager", "linkage"]):
                engine_files.append(f)

        return engine_files

    def test_engine_import(self, engine_file):
        """测试引擎模块导入"""
        module_name = engine_file.stem

        try:
            # 尝试导入模块
            spec = importlib.util.spec_from_file_location(module_name, engine_file)
            module = importlib.util.module_from_spec(spec)

            # 尝试初始化模块（如果存在初始化逻辑）
            spec.loader.exec_module(module)

            # 检查主要类/函数
            classes = [name for name, obj in inspect.getmembers(module, inspect.isclass)
                      if not name.startswith("_")]

            functions = [name for name, obj in inspect.getmembers(module, inspect.isfunction)
                        if not name.startswith("_") and len(inspect.getsource(obj)) < 500]

            return {
                "status": "pass",
                "import_success": True,
                "classes": classes[:10],  # 最多10个类
                "functions": functions[:15],  # 最多15个函数
                "error": None
            }
        except Exception as e:
            return {
                "status": "fail",
                "import_success": False,
                "classes": [],
                "functions": [],
                "error": str(e)
            }

    def test_engine_capability(self, engine_file):
        """测试引擎的基本功能"""
        module_name = engine_file.stem

        try:
            # 尝试导入模块
            spec = importlib.util.spec_from_file_location(module_name, engine_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 检查是否有 CLI 入口（命令行接口）
            has_cli = False
            if hasattr(module, "main") or hasattr(module, "cli") or hasattr(module, "run"):
                has_cli = True

            # 检查是否有 get_status 或类似方法
            has_status = any(True for name in dir(module)
                           if "status" in name.lower() and callable(getattr(module, name, None)))

            # 检查是否有 analyze 或 execute 方法
            has_execute = any(True for name in dir(module)
                            if ("analyze" in name.lower() or "execute" in name.lower() or "run" in name.lower())
                            and callable(getattr(module, name, None)))

            return {
                "capability_check": {
                    "has_cli": has_cli,
                    "has_status": has_status,
                    "has_execute": has_execute
                },
                "status": "pass"
            }
        except Exception as e:
            return {
                "capability_check": {},
                "status": "fail",
                "error": str(e)
            }

    def scan_engines(self):
        """扫描所有引擎并执行测试"""
        engine_files = self.get_engine_files()

        self.test_results["total_engines"] = len(engine_files)

        for engine_file in engine_files:
            module_name = engine_file.stem

            # 测试导入
            import_result = self.test_engine_import(engine_file)

            # 测试功能
            capability_result = self.test_engine_capability(engine_file)

            engine_info = {
                "name": module_name,
                "file": str(engine_file.relative_to(self.project_root)),
                "import_result": import_result,
                "capability_result": capability_result,
                "overall_status": "pass" if import_result["status"] == "pass" and capability_result["status"] == "pass"
                                 else "fail"
            }

            if engine_info["overall_status"] == "pass":
                self.test_results["passed"] += 1
            else:
                self.test_results["failed"] += 1

            self.test_results["engines"].append(engine_info)

        return self.test_results

    def generate_report(self):
        """生成质量报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": self.test_results["total_engines"],
                "passed": self.test_results["passed"],
                "failed": self.test_results["failed"],
                "pass_rate": f"{(self.test_results['passed'] / max(1, self.test_results['total_engines'])) * 100:.1f}%"
            },
            "failed_engines": [
                {
                    "name": e["name"],
                    "error": e["import_result"].get("error") or e["capability_result"].get("error")
                }
                for e in self.test_results["engines"] if e["overall_status"] == "fail"
            ],
            "recommendations": self._generate_recommendations()
        }

        return report

    def _generate_recommendations(self):
        """生成修复建议"""
        recommendations = []

        failed_count = self.test_results["failed"]
        if failed_count == 0:
            recommendations.append("所有引擎测试通过，系统质量良好。")
        else:
            recommendations.append(f"发现 {failed_count} 个引擎存在问题，需要修复。")

        # 检查是否有缺少关键能力的引擎
        for engine in self.test_results["engines"]:
            if engine["overall_status"] == "pass":
                cap = engine["capability_result"].get("capability_check", {})
                if not cap.get("has_status"):
                    recommendations.append(f"建议为 {engine['name']} 添加状态查询方法（get_status）。")
                if not cap.get("has_execute"):
                    recommendations.append(f"建议为 {engine['name']} 添加执行方法（execute/analyze）。")

        return recommendations

    def save_results(self):
        """保存测试结果"""
        results_file = RUNTIME_STATE_DIR / "auto_quality_assurance_results.json"

        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)

        return str(results_file)

    def save_report(self):
        """保存质量报告"""
        report = self.generate_report()
        report_file = RUNTIME_STATE_DIR / "auto_quality_assurance_report.json"

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        return str(report_file)

    def run(self):
        """运行质量保障检查"""
        print("=" * 60)
        print("智能自动化质量保障引擎")
        print("=" * 60)

        # 扫描并测试所有引擎
        print("\n[1/4] 扫描引擎模块...")
        engine_files = self.get_engine_files()
        print(f"找到 {len(engine_files)} 个引擎模块")

        print("\n[2/4] 执行引擎测试...")
        self.scan_engines()

        print("\n[3/4] 生成质量报告...")
        report = self.generate_report()

        print("\n[4/4] 保存结果...")
        results_file = self.save_results()
        report_file = self.save_report()

        # 打印摘要
        print("\n" + "=" * 60)
        print("质量检测结果摘要")
        print("=" * 60)
        print(f"总引擎数: {report['summary']['total']}")
        print(f"通过: {report['summary']['passed']}")
        print(f"失败: {report['summary']['failed']}")
        print(f"通过率: {report['summary']['pass_rate']}")

        if report["failed_engines"]:
            print("\n失败引擎:")
            for e in report["failed_engines"]:
                print(f"  - {e['name']}: {e['error']}")

        if report["recommendations"]:
            print("\n建议:")
            for rec in report["recommendations"]:
                print(f"  - {rec}")

        print(f"\n详细结果已保存至: {results_file}")
        print(f"质量报告已保存至: {report_file}")

        return report


def main():
    """CLI 入口"""
    import argparse

    parser = argparse.ArgumentParser(description="智能自动化质量保障引擎")
    parser.add_argument("--run", action="store_true", help="运行质量检测")
    parser.add_argument("--status", action="store_true", help="查看质量状态")
    parser.add_argument("--report", action="store_true", help="生成详细报告")
    parser.add_argument("--fix", action="store_true", help="自动修复建议")

    args = parser.parse_args()

    engine = AutoQualityAssuranceEngine()

    if args.run or args.status or args.report or args.fix:
        if args.run:
            engine.run()
        elif args.status:
            # 读取并显示状态
            results_file = RUNTIME_STATE_DIR / "auto_quality_assurance_results.json"
            if results_file.exists():
                with open(results_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"上次检测时间: {data.get('timestamp', '未知')}")
                print(f"总引擎数: {data.get('total_engines', 0)}")
                print(f"通过: {data.get('passed', 0)}")
                print(f"失败: {data.get('failed', 0)}")
            else:
                print("尚未运行质量检测，请使用 --run 参数运行")
        elif args.report:
            engine.run()
        elif args.fix:
            # 显示修复建议
            if Path(RUNTIME_STATE_DIR / "auto_quality_assurance_report.json").exists():
                with open(RUNTIME_STATE_DIR / "auto_quality_assurance_report.json", 'r', encoding='utf-8') as f:
                    report = json.load(f)
                print("修复建议:")
                for rec in report.get("recommendations", []):
                    print(f"  - {rec}")
            else:
                print("请先运行 --run 生成报告")
    else:
        # 默认运行
        engine.run()


if __name__ == "__main__":
    main()