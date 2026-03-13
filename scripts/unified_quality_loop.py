#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景质量保障闭环引擎
整合 rounds 182-186 质量保障链，创建端到端的自动质量保障服务

功能：
1. 引擎质量保障：自动测试各引擎功能、验证进化成果
2. 场景计划测试：自动测试所有场景计划的可用性
3. 计划优化分析：检测场景计划问题并生成优化建议
4. 自动修复：自动修复检测到的问题
5. 验证修复效果：验证修复后再次运行测试

形成完整的「质量保障→场景测试→问题检测→自动修复→验证」的闭环

集成模块：
- auto_quality_assurance_engine.py (round 182)
- scene_test_engine.py (round 184)
- scenario_plan_optimizer.py (round 185)
- scene_plan_auto_repair_engine.py (round 186)
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
import subprocess

# 项目根目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

from scripts.auto_quality_assurance_engine import AutoQualityAssuranceEngine
from scripts.scene_test_engine import SceneTestEngine


class UnifiedQualityLoop:
    """智能全场景质量保障闭环引擎"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.runtime_state_dir = Path(PROJECT_ROOT) / "runtime" / "state"
        self.quality_report_path = self.runtime_state_dir / "unified_quality_loop_report.json"

        # 各子引擎状态
        self.engine_status = {}
        self.loop_stats = {
            "start_time": datetime.now().isoformat(),
            "total_cycles": 0,
            "issues_found": 0,
            "issues_fixed": 0,
            "engines_tested": 0,
            "plans_tested": 0,
        }

    def run_engine_quality_check(self):
        """运行引擎质量保障"""
        print("\n" + "=" * 60)
        print("步骤 1: 引擎质量保障测试")
        print("=" * 60)

        try:
            # 导入并运行质量保障引擎
            engine = AutoQualityAssuranceEngine()
            engine.run()

            # 保存报告
            report_path = self.runtime_state_dir / "auto_quality_assurance_report.json"
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(engine.test_results, f, ensure_ascii=False, indent=2)

            self.engine_status["quality_assurance"] = {
                "status": "success",
                "total_engines": engine.test_results.get("total_engines", 0),
                "passed": engine.test_results.get("passed", 0),
                "failed": engine.test_results.get("failed", 0),
            }
            self.loop_stats["engines_tested"] = engine.test_results.get("total_engines", 0)

            print(f"  引擎质量保障完成：{engine.test_results.get('passed', 0)}/{engine.test_results.get('total_engines', 0)} 通过")
            return True

        except Exception as e:
            print(f"  引擎质量保障失败: {e}")
            self.engine_status["quality_assurance"] = {
                "status": "error",
                "error": str(e)
            }
            return False

    def run_scene_plan_test(self):
        """运行场景计划测试"""
        print("\n" + "=" * 60)
        print("步骤 2: 场景计划测试")
        print("=" * 60)

        try:
            engine = SceneTestEngine()
            engine.scan_plans()
            engine.run_full_test()

            # 保存报告
            report_path = self.runtime_state_dir / "scene_test_engine_report.json"
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(engine.results, f, ensure_ascii=False, indent=2)

            self.engine_status["scene_test"] = {
                "status": "success",
                "total_plans": engine.results.get("total_plans", 0),
                "valid_plans": engine.results.get("valid_plans", 0),
                "issues": len(engine.results.get("issues", [])),
            }
            self.loop_stats["plans_tested"] = engine.results.get("total_plans", 0)
            self.loop_stats["issues_found"] += len(engine.results.get("issues", []))

            print(f"  场景计划测试完成：{engine.results.get('valid_plans', 0)}/{engine.results.get('total_plans', 0)} 有效")
            return True

        except Exception as e:
            print(f"  场景计划测试失败: {e}")
            self.engine_status["scene_test"] = {
                "status": "error",
                "error": str(e)
            }
            return False

    def run_plan_optimizer(self):
        """运行场景计划优化引擎"""
        print("\n" + "=" * 60)
        print("步骤 3: 场景计划优化分析")
        print("=" * 60)

        try:
            # 运行计划优化引擎
            result = subprocess.run(
                [sys.executable, f"{SCRIPT_DIR}/scenario_plan_optimizer.py"],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                self.engine_status["plan_optimizer"] = {
                    "status": "success",
                    "output": result.stdout[:500] if result.stdout else ""
                }
                print("  场景计划优化分析完成")
                return True
            else:
                print(f"  场景计划优化分析失败: {result.stderr}")
                self.engine_status["plan_optimizer"] = {
                    "status": "error",
                    "error": result.stderr[:500]
                }
                return False

        except subprocess.TimeoutExpired:
            print("  场景计划优化分析超时")
            self.engine_status["plan_optimizer"] = {"status": "timeout"}
            return False
        except Exception as e:
            print(f"  场景计划优化分析异常: {e}")
            self.engine_status["plan_optimizer"] = {
                "status": "error",
                "error": str(e)
            }
            return False

    def run_auto_repair(self):
        """运行自动修复引擎"""
        print("\n" + "=" * 60)
        print("步骤 4: 自动修复")
        print("=" * 60)

        try:
            # 运行自动修复引擎
            result = subprocess.run(
                [sys.executable, f"{SCRIPT_DIR}/scene_plan_auto_repair_engine.py", "--auto"],
                capture_output=True,
                text=True,
                timeout=300
            )

            # 读取修复报告
            repair_report_path = self.runtime_state_dir / "scene_plan_auto_repair_report.json"
            if repair_report_path.exists():
                with open(repair_report_path, "r", encoding="utf-8") as f:
                    repair_report = json.load(f)
                    fixed_count = repair_report.get("stats", {}).get("fixed", 0)
                    self.loop_stats["issues_fixed"] = fixed_count
                    print(f"  自动修复完成：修复了 {fixed_count} 个问题")

            self.engine_status["auto_repair"] = {
                "status": "success" if result.returncode == 0 else "partial",
                "output": result.stdout[:500] if result.stdout else ""
            }
            return True

        except subprocess.TimeoutExpired:
            print("  自动修复超时")
            self.engine_status["auto_repair"] = {"status": "timeout"}
            return False
        except Exception as e:
            print(f"  自动修复异常: {e}")
            self.engine_status["auto_repair"] = {
                "status": "error",
                "error": str(e)
            }
            return False

    def run_verification(self):
        """运行验证测试"""
        print("\n" + "=" * 60)
        print("步骤 5: 验证修复效果")
        print("=" * 60)

        try:
            # 再次运行场景计划测试验证修复效果
            engine = SceneTestEngine()
            engine.scan_plans()
            engine.run_full_test()

            # 保存验证报告
            verification_path = self.runtime_state_dir / "quality_verification_report.json"
            with open(verification_path, "w", encoding="utf-8") as f:
                json.dump(engine.results, f, ensure_ascii=False, indent=2)

            issues_after = len(engine.results.get("issues", []))
            valid_after = engine.results.get("valid_plans", 0)

            print(f"  验证完成：{valid_after}/{engine.results.get('total_plans', 0)} 有效，剩余 {issues_after} 个问题")

            self.engine_status["verification"] = {
                "status": "success",
                "valid_plans": valid_after,
                "remaining_issues": issues_after
            }
            return True

        except Exception as e:
            print(f"  验证异常: {e}")
            self.engine_status["verification"] = {
                "status": "error",
                "error": str(e)
            }
            return False

    def run_full_loop(self, max_cycles=3):
        """运行完整的质量保障闭环"""
        print("\n" + "#" * 60)
        print("智能全场景质量保障闭环引擎")
        print("#" * 60)
        print(f"开始时间: {self.loop_stats['start_time']}")
        print(f"最大循环次数: {max_cycles}")

        self.loop_stats["total_cycles"] = 0

        for cycle in range(1, max_cycles + 1):
            print(f"\n{'='*60}")
            print(f"质量保障循环 {cycle}/{max_cycles}")
            print(f"{'='*60}")

            self.loop_stats["total_cycles"] = cycle

            # 步骤 1: 引擎质量保障
            self.run_engine_quality_check()

            # 步骤 2: 场景计划测试
            self.run_scene_plan_test()

            # 步骤 3: 计划优化分析
            self.run_plan_optimizer()

            # 步骤 4: 自动修复
            self.run_auto_repair()

            # 步骤 5: 验证修复效果
            self.run_verification()

            # 检查是否还有未解决的问题
            verification = self.engine_status.get("verification", {})
            remaining_issues = verification.get("remaining_issues", 0)

            if remaining_issues == 0:
                print(f"\n所有问题已修复，循环结束")
                break
            elif cycle == max_cycles:
                print(f"\n达到最大循环次数，仍有 {remaining_issues} 个问题待解决")

        # 生成最终报告
        self.generate_report()

    def generate_report(self):
        """生成统一质量保障报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "loop_stats": self.loop_stats,
            "engine_status": self.engine_status,
            "summary": self.generate_summary()
        }

        with open(self.quality_report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\n报告已保存到: {self.quality_report_path}")

    def generate_summary(self):
        """生成摘要"""
        summary = {
            "total_engines_tested": self.loop_stats["engines_tested"],
            "total_plans_tested": self.loop_stats["plans_tested"],
            "issues_found": self.loop_stats["issues_found"],
            "issues_fixed": self.loop_stats["issues_fixed"],
            "total_cycles": self.loop_stats["total_cycles"],
        }

        # 计算成功率
        if self.loop_stats["issues_found"] > 0:
            summary["fix_rate"] = round(
                self.loop_stats["issues_fixed"] / self.loop_stats["issues_found"] * 100, 2
            )
        else:
            summary["fix_rate"] = 100.0

        # 引擎状态摘要
        all_success = all(
            s.get("status") == "success"
            for s in self.engine_status.values()
            if "status" in s
        )
        summary["overall_status"] = "success" if all_success else "partial"

        return summary


def main():
    parser = argparse.ArgumentParser(description="智能全场景质量保障闭环引擎")
    parser.add_argument("--cycles", type=int, default=3, help="最大循环次数 (默认: 3)")
    parser.add_argument("--quick", action="store_true", help="快速模式：只运行一次循环")
    parser.add_argument("--status", action="store_true", help="查看当前质量状态")
    parser.add_argument("--report", action="store_true", help="查看最新报告")

    args = parser.parse_args()

    engine = UnifiedQualityLoop()

    if args.status:
        # 查看当前状态
        report_path = engine.quality_report_path
        if report_path.exists():
            with open(report_path, "r", encoding="utf-8") as f:
                report = json.load(f)
            print(json.dumps(report.get("summary", {}), ensure_ascii=False, indent=2))
        else:
            print("暂无质量报告，请先运行 --run")
        return

    if args.report:
        # 查看最新报告
        report_path = engine.quality_report_path
        if report_path.exists():
            with open(report_path, "r", encoding="utf-8") as f:
                print(f.read())
        else:
            print("暂无报告")
        return

    # 运行完整闭环
    cycles = 1 if args.quick else args.cycles
    engine.run_full_loop(max_cycles=cycles)

    # 打印摘要
    print("\n" + "=" * 60)
    print("质量保障闭环执行摘要")
    print("=" * 60)

    if engine.quality_report_path.exists():
        with open(engine.quality_report_path, "r", encoding="utf-8") as f:
            report = json.load(f)
            summary = report.get("summary", {})
            print(f"  测试引擎数: {summary.get('total_engines_tested', 0)}")
            print(f"  测试计划数: {summary.get('total_plans_tested', 0)}")
            print(f"  发现问题数: {summary.get('issues_found', 0)}")
            print(f"  修复问题数: {summary.get('issues_fixed', 0)}")
            print(f"  修复率: {summary.get('fix_rate', 0)}%")
            print(f"  总体状态: {summary.get('overall_status', 'unknown')}")


if __name__ == "__main__":
    main()