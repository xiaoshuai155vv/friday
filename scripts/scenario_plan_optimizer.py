#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能场景计划深度验证与优化引擎

功能：
1. 深度验证场景计划引用的文件/应用是否存在
2. 检测步骤是否过期或命令是否有效
3. 生成优化建议
4. 可选自动修复

配合 scene_test_engine.py 形成：测试 → 验证 → 优化 完整闭环
"""

import os
import sys
import json
import re
import subprocess
import glob
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# 解决 Windows 控制台 GBK 编码问题
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass


def safe_print(*args, **kwargs):
    """安全打印，处理编码问题"""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # 移除 emoji 后打印
        msg = str(args[0]) if args else ""
        msg = msg.encode('gbk', errors='replace').decode('gbk')
        print(msg, **kwargs)


class ScenarioPlanOptimizer:
    """智能场景计划深度验证与优化引擎"""

    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.plans_dir = self.base_path / "assets" / "plans"
        self.results = {
            "scan_time": datetime.now().isoformat(),
            "total_plans": 0,
            "plans": [],
            "issues": [],
            "optimization_suggestions": []
        }

    def scan_plans(self) -> List[Dict]:
        """扫描所有场景计划"""
        plan_files = list(self.plans_dir.glob("*.json"))
        self.results["total_plans"] = len(plan_files)

        plans = []
        for plan_file in plan_files:
            try:
                with open(plan_file, 'r', encoding='utf-8') as f:
                    plan_data = json.load(f)
                plans.append({
                    "file": str(plan_file.relative_to(self.base_path)),
                    "name": plan_data.get("name", plan_file.stem),
                    "data": plan_data
                })
            except Exception as e:
                plans.append({
                    "file": str(plan_file.relative_to(self.base_path)),
                    "name": plan_file.stem,
                    "error": str(e)
                })

        self.results["plans"] = plans
        return plans

    def verify_file_references(self, plan_data: Dict) -> List[Dict]:
        """验证场景计划中引用的文件是否存在"""
        issues = []
        plan_text = json.dumps(plan_data, ensure_ascii=False)

        # 匹配文件路径（引号内的路径）
        file_patterns = [
            r'["\']([A-Za-z]:\\[^\'"]+)["\']',  # Windows 绝对路径
            r'["\'](/[^\'"]+)["\']',  # Unix 绝对路径
            r'"file":\s*"([^"]+)"',  # JSON 中的 file 字段
        ]

        for pattern in file_patterns:
            matches = re.findall(pattern, plan_text)
            for file_path in matches:
                if os.path.isabs(file_path):
                    if not os.path.exists(file_path):
                        issues.append({
                            "type": "file_not_found",
                            "severity": "warning",
                            "file_ref": file_path,
                            "message": f"引用的文件不存在: {file_path}"
                        })

        return issues

    def verify_app_references(self, plan_data: Dict) -> List[Dict]:
        """验证场景计划中引用的应用是否已安装"""
        issues = []
        plan_text = json.dumps(plan_data, ensure_ascii=False)

        # 常见的应用名称模式
        known_apps = {
            "iHaier": "iHaier2.0",
            "iHaier2.0": "iHaier2.0",
            "Chrome": "chrome",
            "Edge": "msedge",
            "Notepad": "notepad",
            "Calculator": "calc",
            "记事本": "notepad",
            "计算器": "calc",
            "浏览器": "chrome",
            "网易云音乐": "CloudMusic",
            "微信": "WeChat",
            "钉钉": "DingTalk",
            "腾讯会议": "wemeet",
        }

        for app_name, process_name in known_apps.items():
            if app_name in plan_text:
                # 检查应用是否通过 window_tool 或 run 引用
                if not self._check_app_installed(process_name):
                    issues.append({
                        "type": "app_not_installed",
                        "severity": "info",
                        "app": app_name,
                        "message": f"应用可能未安装或未运行: {app_name}"
                    })

        return issues

    def _check_app_installed(self, app_name: str) -> bool:
        """检查应用是否已安装或运行"""
        try:
            # 检查进程是否运行
            result = subprocess.run(
                ["powershell", "-Command", f"Get-Process -Name '{app_name}' -ErrorAction SilentlyContinue"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def verify_step_validity(self, plan_data: Dict) -> List[Dict]:
        """验证步骤的有效性"""
        issues = []

        # 兼容两种格式："steps" 字段或直接是数组
        steps = plan_data.get("steps", [])
        if not steps and isinstance(plan_data, list):
            steps = plan_data

        # 检查步骤类型
        valid_step_types = [
            "screenshot", "vision", "click", "type", "key", "scroll", "wait",
            "run", "activate", "maximize", "open", "close", "paste", "goto"
        ]

        for i, step in enumerate(steps):
            # 跳过非字典的步骤（如字符串）
            if not isinstance(step, dict):
                continue

            # 兼容 "type" 和 "do" 字段
            step_type = step.get("type") or step.get("do", "")

            # 检查无效的步骤类型
            if step_type and step_type not in valid_step_types:
                issues.append({
                    "type": "invalid_step_type",
                    "severity": "warning",
                    "step_index": i,
                    "step_type": step_type,
                    "message": f"步骤 {i+1} 使用了未知的类型: {step_type}"
                })

            # 检查缺少必要参数的步骤
            if step_type in ["click", "type", "run", "activate"]:
                if not any([step.get("x"), step.get("text"), step.get("cmd"), step.get("title")]):
                    issues.append({
                        "type": "missing_parameters",
                        "severity": "error",
                        "step_index": i,
                        "step_type": step_type,
                        "message": f"步骤 {i+1} 缺少必要的参数"
                    })

            # 检查过时的命令（如旧版本的 window_tool 参数）
            if step_type == "click" and "verify" in step:
                issues.append({
                    "type": "deprecated_option",
                    "severity": "info",
                    "step_index": i,
                    "message": f"步骤 {i+1} 使用了 verify 选项，考虑使用 vision_coords 替代"
                })

        return issues

    def analyze_plan_quality(self, plan_data: Dict) -> Dict[str, Any]:
        """分析场景计划的质量"""
        quality = {
            "score": 100,
            "issues": [],
            "suggestions": []
        }

        # 检查是否有 name
        if not plan_data.get("name"):
            quality["issues"].append("缺少 name 字段")
            quality["score"] -= 10

        # 检查是否有 description
        if not plan_data.get("description"):
            quality["issues"].append("缺少 description 字段")
            quality["score"] -= 5

        # 检查是否有 triggers
        if not plan_data.get("triggers"):
            quality["issues"].append("缺少 triggers 字段")
            quality["score"] -= 10
        else:
            # 检查 triggers 格式
            triggers = plan_data.get("triggers", [])
            if not isinstance(triggers, list):
                quality["issues"].append("triggers 应该是数组")
                quality["score"] -= 10
            elif len(triggers) == 0:
                quality["issues"].append("triggers 为空")
                quality["score"] -= 5

        # 检查是否有 steps
        if not plan_data.get("steps") and not isinstance(plan_data, list):
            quality["issues"].append("缺少 steps 字段")
            quality["score"] -= 20
        else:
            # 兼容两种格式
            steps = plan_data.get("steps", [])
            if not steps and isinstance(plan_data, list):
                steps = plan_data
            if len(steps) == 0:
                quality["issues"].append("steps 为空")
                quality["score"] -= 15

            # 检查第一步是否是截图/vision（好的实践）
            if steps and len(steps) > 0:
                first_step = steps[0] if isinstance(steps[0], dict) else {}
                first_type = first_step.get("type") or first_step.get("do", "")
                if first_type not in ["screenshot", "vision"]:
                    quality["suggestions"].append("建议第一步使用 screenshot 以便后续 vision 分析")

        # 检查是否有 maximize（好的实践）
        # 过滤出字典类型的步骤
        dict_steps = [s for s in steps if isinstance(s, dict)]
        if dict_steps:
            has_activate = any(s.get("type") or s.get("do") == "activate" for s in dict_steps)
            has_maximize = any(s.get("type") or s.get("do") == "maximize" for s in dict_steps)
            if has_activate and not has_maximize:
                quality["suggestions"].append("activate 后建议添加 maximize 以确保截图完整")

            # 检查是否有 wait（好的实践）
            if not any(s.get("type") or s.get("do") == "wait" for s in dict_steps):
                if len(steps) > 3:
                    quality["suggestions"].append("多步骤计划建议添加 wait 以确保稳定性")

        return quality

    def generate_optimization_suggestions(self, issues: List[Dict], quality: Dict) -> List[Dict]:
        """生成优化建议"""
        suggestions = []

        # 基于问题生成建议
        for issue in issues:
            if issue["type"] == "file_not_found":
                suggestions.append({
                    "category": "file_reference",
                    "priority": "high",
                    "suggestion": f"验证文件路径或移除对不存在文件的引用: {issue.get('file_ref')}"
                })
            elif issue["type"] == "app_not_installed":
                suggestions.append({
                    "category": "app_reference",
                    "priority": "medium",
                    "suggestion": f"确认应用已安装: {issue.get('app')}，或添加安装检测"
                })
            elif issue["type"] == "invalid_step_type":
                suggestions.append({
                    "category": "step_type",
                    "priority": "high",
                    "suggestion": f"修正步骤类型: {issue.get('step_type')}"
                })
            elif issue["type"] == "missing_parameters":
                suggestions.append({
                    "category": "parameters",
                    "priority": "high",
                    "suggestion": f"为步骤添加必要参数"
                })

        # 基于质量分析生成建议
        for suggestion in quality.get("suggestions", []):
            suggestions.append({
                "category": "quality",
                "priority": "low",
                "suggestion": suggestion
            })

        return suggestions

    def verify_all_plans(self) -> Dict:
        """验证所有场景计划"""
        safe_print("开始深度验证场景计划...")

        plans = self.scan_plans()
        safe_print(f"扫描到 {len(plans)} 个场景计划")

        all_issues = []
        all_suggestions = []

        for plan in plans:
            if "error" in plan:
                all_issues.append({
                    "plan": plan["file"],
                    "type": "parse_error",
                    "severity": "error",
                    "message": plan["error"]
                })
                continue

            plan_file = plan["file"]
            plan_data = plan["data"]

            # 验证文件引用
            file_issues = self.verify_file_references(plan_data)
            for issue in file_issues:
                issue["plan"] = plan_file
                all_issues.append(issue)

            # 验证应用引用
            app_issues = self.verify_app_references(plan_data)
            for issue in app_issues:
                issue["plan"] = plan_file
                all_issues.append(issue)

            # 验证步骤有效性
            step_issues = self.verify_step_validity(plan_data)
            for issue in step_issues:
                issue["plan"] = plan_file
                all_issues.append(issue)

            # 分析质量
            quality = self.analyze_plan_quality(plan_data)
            plan["quality"] = quality

            # 生成优化建议
            suggestions = self.generate_optimization_suggestions(file_issues + app_issues + step_issues, quality)
            for suggestion in suggestions:
                suggestion["plan"] = plan_file
                all_suggestions.append(suggestion)

        self.results["issues"] = all_issues
        self.results["optimization_suggestions"] = all_suggestions

        # 统计
        issue_counts = {
            "error": len([i for i in all_issues if i.get("severity") == "error"]),
            "warning": len([i for i in all_issues if i.get("severity") == "warning"]),
            "info": len([i for i in all_issues if i.get("severity") == "info"])
        }

        safe_print(f"\n验证结果统计:")
        safe_print(f"   错误: {issue_counts['error']}")
        safe_print(f"   警告: {issue_counts['warning']}")
        safe_print(f"   提示: {issue_counts['info']}")
        safe_print(f"   优化建议: {len(all_suggestions)}")

        return self.results

    def save_report(self, output_path: Optional[str] = None) -> str:
        """保存验证报告"""
        if output_path is None:
            output_path = self.base_path / "runtime" / "state" / "scenario_plan_optimizer_report.json"

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        return str(output_path)

    def get_summary(self) -> Dict:
        """获取验证摘要"""
        return {
            "total_plans": self.results["total_plans"],
            "total_issues": len(self.results["issues"]),
            "total_suggestions": len(self.results["optimization_suggestions"]),
            "plans_with_issues": len(set([i.get("plan") for i in self.results["issues"]]))
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="智能场景计划深度验证与优化引擎")
    parser.add_argument("--verify", "-v", action="store_true", help="运行验证")
    parser.add_argument("--output", "-o", help="报告输出路径")
    parser.add_argument("--summary", "-s", action="store_true", help="显示摘要")

    args = parser.parse_args()

    optimizer = ScenarioPlanOptimizer()

    if args.verify:
        results = optimizer.verify_all_plans()
        output_path = optimizer.save_report(args.output)

        if args.summary or not args.output:
            summary = optimizer.get_summary()
            safe_print("\n摘要:")
            safe_print(f"   总计划数: {summary['total_plans']}")
            safe_print(f"   有问题的计划: {summary['plans_with_issues']}")
            safe_print(f"   总问题数: {summary['total_issues']}")
            safe_print(f"   优化建议: {summary['total_suggestions']}")

        safe_print(f"\n报告已保存到: {output_path}")
    else:
        safe_print("使用 --verify 运行验证")
        safe_print("示例: python scenario_plan_optimizer.py --verify --summary")


if __name__ == "__main__":
    main()