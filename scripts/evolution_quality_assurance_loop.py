"""
智能全场景进化质量保障与持续改进闭环引擎
Evolution Quality Assurance and Continuous Improvement Loop Engine

版本: 1.0.0
创建日期: 2026-03-14
功能描述:
  让进化环具备端到端的质量保障能力，确保每个进化都能被自动测试、验证，
  并形成持续的质量改进闭环。

主要功能:
1. 自动模块验证 - 验证新创建的模块能否正确导入
2. 依赖检查 - 检查模块间的依赖关系
3. 集成测试 - 验证模块与现有系统的集成
4. 质量报告生成 - 生成进化质量评估报告
5. 持续改进建议 - 基于质量分析生成改进建议

触发关键词: 进化质量保障、质量保障、持续改进、模块验证、集成测试
"""

import os
import sys
import json
import importlib
import importlib.util
import inspect
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


class EvolutionQualityAssuranceLoop:
    """进化质量保障与持续改进闭环引擎"""

    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.scripts_path = self.base_path / "scripts"
        self.runtime_path = self.base_path / "runtime" / "state"
        self.quality_report_path = self.runtime_path / "quality_reports"

        # 确保质量报告目录存在
        self.quality_report_path.mkdir(parents=True, exist_ok=True)

        # 已验证的模块缓存
        self.verified_modules: Dict[str, bool] = {}

        # 质量指标
        self.quality_metrics = {
            "total_modules": 0,
            "verified_modules": 0,
            "failed_modules": 0,
            "integration_tests": 0,
            "passed_tests": 0,
            "last_check": None
        }

    def verify_module_import(self, module_name: str) -> Tuple[bool, str]:
        """
        验证模块能否正确导入

        Args:
            module_name: 模块名称（不含.py后缀）

        Returns:
            (是否成功, 错误信息)
        """
        try:
            # 添加 scripts 目录到 sys.path
            scripts_dir = str(self.scripts_path)
            if scripts_dir not in sys.path:
                sys.path.insert(0, scripts_dir)

            # 尝试直接导入模块
            try:
                module = importlib.import_module(module_name)
                return True, "模块导入成功"
            except ImportError:
                # 尝试添加 scripts 前缀
                try:
                    module = importlib.import_module(f"scripts.{module_name}")
                    return True, "模块导入成功"
                except ImportError:
                    return False, f"模块 {module_name} 不存在"
        except Exception as e:
            return False, f"模块导入失败: {str(e)}"

    def check_module_dependencies(self, module_name: str) -> Dict[str, Any]:
        """
        检查模块的依赖关系

        Args:
            module_name: 模块名称

        Returns:
            依赖检查结果
        """
        result = {
            "module": module_name,
            "dependencies": [],
            "missing_dependencies": [],
            "status": "unknown"
        }

        try:
            # 尝试导入模块
            module = importlib.import_module(module_name)

            # 分析模块的导入语句
            source_file = self.scripts_path / f"{module_name}.py"
            if source_file.exists():
                with open(source_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 简单分析 import 语句
                    import_lines = [line.strip() for line in content.split('\n')
                                   if line.strip().startswith('import ')
                                   or line.strip().startswith('from ')]

                    # 提取依赖
                    for line in import_lines:
                        if line.startswith('from '):
                            parts = line.split()
                            if len(parts) >= 2:
                                dep = parts[1]
                                if dep not in ['typing', 'os', 'sys', 'json', 'datetime',
                                              'pathlib', 'random', 'time', 're']:
                                    result["dependencies"].append(dep)

            # 检查依赖是否可用
            for dep in result["dependencies"]:
                dep_available, _ = self.verify_module_import(dep)
                if not dep_available:
                    result["missing_dependencies"].append(dep)

            result["status"] = "ok" if not result["missing_dependencies"] else "missing_deps"

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        return result

    def run_integration_test(self, module_name: str) -> Dict[str, Any]:
        """
        运行模块的集成测试

        Args:
            module_name: 模块名称

        Returns:
            集成测试结果
        """
        result = {
            "module": module_name,
            "test_passed": False,
            "test_message": "",
            "execution_time": 0
        }

        import time
        start_time = time.time()

        try:
            # 尝试实例化模块
            module = importlib.import_module(module_name)

            # 检查是否有可调用的方法
            has_init = hasattr(module, '__init__')
            has_execute = hasattr(module, 'execute') or hasattr(module, 'run')

            if has_init:
                # 尝试实例化
                try:
                    # 查找类
                    classes = [name for name, obj in inspect.getmembers(module, inspect.isclass)
                             if name.endswith('Engine') or name.endswith('Manager')]

                    if classes:
                        cls = getattr(module, classes[0])
                        instance = cls()
                        result["test_passed"] = True
                        result["test_message"] = f"成功实例化 {classes[0]}"
                    else:
                        result["test_passed"] = True
                        result["test_message"] = "模块无需实例化"
                except Exception as e:
                    result["test_message"] = f"实例化失败: {str(e)}"
            else:
                result["test_passed"] = True
                result["test_message"] = "模块无可实例化类"

        except Exception as e:
            result["test_message"] = f"集成测试失败: {str(e)}"

        result["execution_time"] = time.time() - start_time
        return result

    def scan_all_modules(self) -> Dict[str, Any]:
        """
        扫描所有进化相关模块

        Returns:
            扫描结果
        """
        result = {
            "total": 0,
            "verified": 0,
            "failed": 0,
            "modules": []
        }

        # 扫描 scripts 目录下的进化相关模块
        evolution_keywords = ['evolution', 'quality', 'assurance', 'loop']

        for py_file in self.scripts_path.glob("*.py"):
            if py_file.name.startswith('_'):
                continue

            module_name = py_file.stem

            # 只检查进化相关模块
            if not any(kw in module_name.lower() for kw in evolution_keywords):
                continue

            result["total"] += 1

            # 验证模块
            verified, msg = self.verify_module_import(module_name)

            module_info = {
                "name": module_name,
                "verified": verified,
                "message": msg
            }

            if verified:
                result["verified"] += 1

                # 运行集成测试
                test_result = self.run_integration_test(module_name)
                module_info["integration_test"] = test_result
            else:
                result["failed"] += 1

            result["modules"].append(module_info)

        # 更新质量指标
        self.quality_metrics["total_modules"] = result["total"]
        self.quality_metrics["verified_modules"] = result["verified"]
        self.quality_metrics["failed_modules"] = result["failed"]
        self.quality_metrics["last_check"] = datetime.now().isoformat()

        return result

    def generate_quality_report(self) -> Dict[str, Any]:
        """
        生成质量报告

        Returns:
            质量报告
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "quality_metrics": self.quality_metrics,
            "scan_results": self.scan_all_modules(),
            "recommendations": []
        }

        # 生成改进建议
        scan_results = report["scan_results"]

        # 检查通过率
        if scan_results["total"] > 0:
            pass_rate = scan_results["verified"] / scan_results["total"] * 100
            report["pass_rate"] = pass_rate

            if pass_rate < 80:
                report["recommendations"].append({
                    "priority": "high",
                    "category": "integration",
                    "message": f"模块通过率为 {pass_rate:.1f}%，建议检查失败的模块"
                })

        # 检查失败的模块
        failed_modules = [m for m in scan_results["modules"] if not m["verified"]]
        if failed_modules:
            report["recommendations"].append({
                "priority": "medium",
                "category": "verification",
                "message": f"发现 {len(failed_modules)} 个无法验证的模块: {', '.join([m['name'] for m in failed_modules])}"
            })

        # 检查缺少测试的模块
        modules_without_tests = []
        for m in scan_results["modules"]:
            if m["verified"]:
                test_result = m.get("integration_test", {})
                if not test_result.get("test_passed"):
                    modules_without_tests.append(m["name"])

        if modules_without_tests:
            report["recommendations"].append({
                "priority": "low",
                "category": "testing",
                "message": f"建议为以下模块添加测试: {', '.join(modules_without_tests)}"
            })

        # 保存报告
        report_file = self.quality_report_path / f"quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        report["report_file"] = str(report_file)

        return report

    def continuous_improvement_check(self) -> Dict[str, Any]:
        """
        持续改进检查

        Returns:
            改进检查结果
        """
        # 加载历史报告
        report_files = sorted(self.quality_report_path.glob("quality_report_*.json"))

        result = {
            "has_history": len(report_files) > 0,
            "trends": {},
            "improvements": []
        }

        if len(report_files) >= 2:
            # 比较最近两次报告
            latest_report = json.loads(report_files[-1].read_text(encoding='utf-8'))
            previous_report = json.loads(report_files[-2].read_text(encoding='utf-8'))

            # 计算趋势
            latest_pass_rate = latest_report.get("pass_rate", 0)
            previous_pass_rate = previous_report.get("pass_rate", 0)

            result["trends"]["pass_rate_change"] = latest_pass_rate - previous_pass_rate

            # 生成改进建议
            if latest_pass_rate > previous_pass_rate:
                result["improvements"].append({
                    "type": "positive",
                    "message": f"质量通过率提升了 {latest_pass_rate - previous_pass_rate:.1f}%"
                })
            elif latest_pass_rate < previous_pass_rate:
                result["improvements"].append({
                    "type": "negative",
                    "message": f"质量通过率下降了 {previous_pass_rate - latest_pass_rate:.1f}%，需要检查新引入的变更"
                })
            else:
                result["improvements"].append({
                    "type": "neutral",
                    "message": "质量通过率保持稳定"
                })

        return result

    def execute_full_cycle(self) -> Dict[str, Any]:
        """
        执行完整的质量保障循环

        Returns:
            执行结果
        """
        result = {
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "steps": {}
        }

        # 1. 扫描所有模块
        result["steps"]["scan"] = self.scan_all_modules()

        # 2. 生成质量报告
        result["steps"]["report"] = self.generate_quality_report()

        # 3. 持续改进检查
        result["steps"]["improvement"] = self.continuous_improvement_check()

        # 4. 汇总结果
        result["summary"] = {
            "total_modules": self.quality_metrics["total_modules"],
            "verified_modules": self.quality_metrics["verified_modules"],
            "pass_rate": result["steps"]["report"].get("pass_rate", 0),
            "recommendations_count": len(result["steps"]["report"]["recommendations"])
        }

        return result


# ==================== 入口点 ====================

def execute_quality_assurance(mode: str = "full", module_name: str = None) -> Dict[str, Any]:
    """
    质量保障入口函数

    Args:
        mode: 执行模式 (full/scan/report/improve)
        module_name: 指定模块名称

    Returns:
        执行结果
    """
    engine = EvolutionQualityAssuranceLoop()

    if mode == "full":
        # 完整循环
        return engine.execute_full_cycle()

    elif mode == "scan":
        # 扫描模式
        return engine.scan_all_modules()

    elif mode == "report":
        # 报告模式
        return engine.generate_quality_report()

    elif mode == "improve":
        # 改进模式
        return engine.continuous_improvement_check()

    elif mode == "verify" and module_name:
        # 验证指定模块
        return {
            "import": engine.verify_module_import(module_name),
            "dependencies": engine.check_module_dependencies(module_name),
            "integration": engine.run_integration_test(module_name)
        }

    else:
        return {"error": f"未知模式: {mode}"}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="进化质量保障与持续改进闭环引擎")
    parser.add_argument("--mode", choices=["full", "scan", "report", "improve", "verify"],
                       default="full", help="执行模式")
    parser.add_argument("--module", type=str, help="指定模块名称（verify模式用）")

    args = parser.parse_args()

    result = execute_quality_assurance(args.mode, args.module)

    # 输出结果
    print(json.dumps(result, ensure_ascii=False, indent=2))