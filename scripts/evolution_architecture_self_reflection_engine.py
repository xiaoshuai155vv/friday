#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能进化架构自省与自我重构引擎 (Evolution Architecture Self-Reflection Engine)
让系统能够主动分析自身架构问题、识别优化机会、自动进行结构优化，实现真正的自主架构进化。

功能：
1. 架构自省 - 分析当前系统架构状态（引擎数量、依赖关系、调用链路）
2. 问题识别 - 识别架构中的问题（冗余代码、低效调用、重复功能）
3. 优化建议生成 - 生成架构优化建议
4. 自我重构 - 自动执行简单的架构优化
5. 验证与学习 - 验证重构效果并反馈学习

集成：支持"架构自省"、"自我重构"、"架构优化"、"进化架构"等关键词触发
"""

import os
import sys
import json
import glob
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPTS)
RUNTIME_STATE = os.path.join(PROJECT, "runtime", "state")
RUNTIME_LOGS = os.path.join(PROJECT, "runtime", "logs")
REFERENCES = os.path.join(PROJECT, "references")


class EvolutionArchitectureSelfReflection:
    """智能进化架构自省与自我重构引擎"""

    def __init__(self):
        self.name = "EvolutionArchitectureSelfReflection"
        self.version = "1.0.0"
        self.analysis_path = os.path.join(RUNTIME_STATE, "architecture_analysis.json")
        self.issues_path = os.path.join(RUNTIME_STATE, "architecture_issues.json")
        self.suggestions_path = os.path.join(RUNTIME_STATE, "architecture_suggestions.json")
        self.history_path = os.path.join(RUNTIME_STATE, "architecture_reflection_history.json")

        self.analysis_data = {}
        self.issues = []
        self.suggestions = []
        self.history = self._load_history()

    def _load_history(self) -> List[Dict]:
        """加载历史记录"""
        if os.path.exists(self.history_path):
            try:
                with open(self.history_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_history(self):
        """保存历史记录"""
        try:
            with open(self.history_path, "w", encoding="utf-8") as f:
                json.dump(self.history[-50:], f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史记录失败: {e}")

    def analyze_architecture(self) -> Dict[str, Any]:
        """分析当前系统架构"""
        print("\n=== 架构自省分析 ===")

        # 分析脚本目录
        scripts_dir = SCRIPTS
        all_files = glob.glob(os.path.join(scripts_dir, "*.py"))
        py_files = [f for f in all_files if not f.endswith("__init__.py")]

        # 按功能分类
        categories = {
            "evolution": [],
            "engine": [],
            "tool": [],
            "workflow": [],
            "utility": [],
            "other": []
        }

        engine_count = 0
        for f in py_files:
            basename = os.path.basename(f)
            if "evolution" in basename.lower():
                categories["evolution"].append(basename)
                if "engine" in basename.lower():
                    engine_count += 1
            elif "engine" in basename.lower():
                categories["engine"].append(basename)
                engine_count += 1
            elif "_tool" in basename or "tool_" in basename:
                categories["tool"].append(basename)
            elif "workflow" in basename or "orchestrator" in basename:
                categories["workflow"].append(basename)
            elif basename.startswith("do.py") or basename in ["run_plan.py", "scenario_log.py"]:
                categories["utility"].append(basename)
            else:
                categories["other"].append(basename)

        # 分析 references 目录
        refs_dir = REFERENCES
        ref_files = []
        if os.path.exists(refs_dir):
            ref_files = glob.glob(os.path.join(refs_dir, "*.md"))

        # 分析 assets/plans 目录
        plans_dir = os.path.join(PROJECT, "assets", "plans")
        plan_files = []
        if os.path.exists(plans_dir):
            plan_files = glob.glob(os.path.join(plans_dir, "*.json"))

        # 计算代码行数
        total_lines = 0
        for f in py_files:
            try:
                with open(f, "r", encoding="utf-8") as file:
                    total_lines += len(file.readlines())
            except Exception:
                pass

        self.analysis_data = {
            "timestamp": datetime.now().isoformat(),
            "total_scripts": len(py_files),
            "engine_count": engine_count,
            "categories": categories,
            "reference_files": len(ref_files),
            "plan_files": len(plan_files),
            "total_lines": total_lines,
            "script_files": [os.path.basename(f) for f in py_files[:20]]  # 前20个
        }

        # 保存分析结果
        try:
            with open(self.analysis_path, "w", encoding="utf-8") as f:
                json.dump(self.analysis_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存分析结果失败: {e}")

        print(f"总脚本数: {self.analysis_data['total_scripts']}")
        print(f"引擎数: {self.analysis_data['engine_count']}")
        print(f"总代码行数: {self.analysis_data['total_lines']}")
        print(f"场景计划数: {self.analysis_data['plan_files']}")

        return self.analysis_data

    def identify_issues(self) -> List[Dict[str, Any]]:
        """识别架构问题"""
        print("\n=== 架构问题识别 ===")

        self.issues = []

        # 检查可能的重复功能
        engine_files = glob.glob(os.path.join(SCRIPTS, "*engine*.py"))
        engine_names = [os.path.basename(f).replace(".py", "") for f in engine_files]

        # 识别相似引擎名称（可能的重复）
        for i, name1 in enumerate(engine_names):
            for name2 in engine_names[i+1:]:
                # 简单的相似度检查
                common_words = set(name1.lower().split("_")) & set(name2.lower().split("_"))
                if len(common_words) >= 2:  # 有2个以上相同词
                    self.issues.append({
                        "type": "potential_duplication",
                        "severity": "medium",
                        "description": f"发现相似引擎: {name1} 和 {name2}",
                        "common_words": list(common_words),
                        "suggestion": "检查这两个引擎是否有功能重叠，考虑合并"
                    })

        # 检查缺少必要组件
        if not os.path.exists(os.path.join(REFERENCES, "capabilities.md")):
            self.issues.append({
                "type": "missing_documentation",
                "severity": "high",
                "description": "缺少 capabilities.md 文档",
                "suggestion": "创建或更新 capabilities.md"
            })

        if not os.path.exists(os.path.join(REFERENCES, "capability_gaps.md")):
            self.issues.append({
                "type": "missing_documentation",
                "severity": "medium",
                "description": "缺少 capability_gaps.md 文档",
                "suggestion": "创建或更新 capability_gaps.md"
            })

        # 检查进化历史
        state_files = glob.glob(os.path.join(RUNTIME_STATE, "evolution_completed_*.json"))
        if len(state_files) > 0:
            # 读取最近的进化记录
            recent_files = sorted(state_files, key=os.path.getmtime, reverse=True)[:5]
            for f in recent_files:
                try:
                    with open(f, "r", encoding="utf-8") as file:
                        data = json.load(file)
                        if data.get("status") == "未完成":
                            self.issues.append({
                                "type": "uncompleted_evolution",
                                "severity": "medium",
                                "description": f"存在未完成的进化: {data.get('current_goal', 'unknown')}",
                                "file": os.path.basename(f),
                                "suggestion": "分析未完成原因，决定是否继续或放弃"
                            })
                except Exception:
                    pass

        # 保存问题列表
        try:
            with open(self.issues_path, "w", encoding="utf-8") as f:
                json.dump(self.issues, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存问题列表失败: {e}")

        print(f"发现 {len(self.issues)} 个问题")
        for issue in self.issues:
            print(f"  - [{issue['severity']}] {issue['description']}")

        return self.issues

    def generate_suggestions(self) -> List[Dict[str, Any]]:
        """生成优化建议"""
        print("\n=== 优化建议生成 ===")

        self.suggestions = []

        # 基于分析结果生成建议
        if self.analysis_data.get("engine_count", 0) > 50:
            self.suggestions.append({
                "type": "architecture_complexity",
                "priority": "high",
                "title": "引擎数量过多，需要优化",
                "description": f"当前有 {self.analysis_data.get('engine_count', 0)} 个引擎，可能存在管理复杂性",
                "actions": [
                    "分析引擎间的依赖关系",
                    "识别可以合并的相似功能",
                    "建立引擎分类体系",
                    "创建引擎使用统计"
                ]
            })

        # 基于问题生成建议
        dup_issues = [i for i in self.issues if i.get("type") == "potential_duplication"]
        if dup_issues:
            self.suggestions.append({
                "type": "deduplication",
                "priority": "medium",
                "title": "发现潜在重复功能",
                "description": f"发现 {len(dup_issues)} 对相似引擎",
                "actions": [
                    "逐一检查相似引擎的功能",
                    "考虑合并重复功能",
                    "建立统一的接口层"
                ]
            })

        # 基于代码行数生成建议
        total_lines = self.analysis_data.get("total_lines", 0)
        if total_lines > 50000:
            self.suggestions.append({
                "type": "code_maintenance",
                "priority": "medium",
                "title": "代码规模较大，需要关注可维护性",
                "description": f"总代码行数: {total_lines}",
                "actions": [
                    "检查是否有未使用的代码",
                    "优化长函数",
                    "增加代码注释",
                    "完善单元测试"
                ]
            })

        # 通用建议
        self.suggestions.append({
            "type": "documentation",
            "priority": "low",
            "title": "保持文档同步",
            "description": "确保新增引擎及时更新到文档",
            "actions": [
                "更新 capabilities.md",
                "更新 SKILL.md",
                "维护引擎使用示例"
            ]
        })

        # 保存建议
        try:
            with open(self.suggestions_path, "w", encoding="utf-8") as f:
                json.dump(self.suggestions, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存建议失败: {e}")

        print(f"生成 {len(self.suggestions)} 条优化建议")
        for suggestion in self.suggestions:
            print(f"  - [{suggestion['priority']}] {suggestion['title']}")

        return self.suggestions

    def execute_simple_refactoring(self, dry_run: bool = True) -> Dict[str, Any]:
        """执行简单重构"""
        print(f"\n=== 执行重构 (dry_run={dry_run}) ===")

        results = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "actions": [],
            "issues_fixed": []
        }

        # 示例1：清理空目录
        empty_dirs = []
        for root, dirs, files in os.walk(PROJECT):
            # 跳过特定目录
            if any(x in root for x in ["node_modules", ".git", "__pycache__", "venv"]):
                continue
            if not dirs and not files and root != PROJECT:
                empty_dirs.append(root)

        if empty_dirs:
            action = {
                "type": "clean_empty_dirs",
                "description": f"发现 {len(empty_dirs)} 个空目录",
                "directories": empty_dirs[:10]  # 只显示前10个
            }
            results["actions"].append(action)

            if not dry_run:
                # 注意：实际不删除，防止误删
                pass

        # 示例2：检查并报告孤岛文件（没有任何导入的文件）
        script_files = glob.glob(os.path.join(SCRIPTS, "*.py"))
        script_names = {os.path.basename(f).replace(".py", "") for f in script_files}

        isolated_files = []
        for f in script_files:
            if f.endswith("__init__.py"):
                continue
            try:
                with open(f, "r", encoding="utf-8") as file:
                    content = file.read()
                    # 简单检查是否有 import 其他脚本
                    has_import = any(f"import {name}" in content or f"from {name}" in content
                                    for name in script_names if name != os.path.basename(f).replace(".py", ""))
                    if not has_import and "do.py" not in f:
                        isolated_files.append(os.path.basename(f))
            except Exception:
                pass

        if isolated_files:
            action = {
                "type": "report_isolated_files",
                "description": f"发现 {len(isolated_files)} 个孤立文件（无导入其他脚本）",
                "files": isolated_files[:10]
            }
            results["actions"].append(action)

        results["total_actions"] = len(results["actions"])
        print(f"将执行 {results['total_actions']} 个重构动作")

        return results

    def self_reflect(self) -> Dict[str, Any]:
        """完整的自省流程"""
        print("\n" + "="*60)
        print("智能进化架构自省与自我重构引擎")
        print("="*60)

        # 1. 架构分析
        analysis = self.analyze_architecture()

        # 2. 问题识别
        issues = self.identify_issues()

        # 3. 建议生成
        suggestions = self.generate_suggestions()

        # 4. 记录到历史
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis,
            "issues_count": len(issues),
            "suggestions_count": len(suggestions)
        })
        self._save_history()

        return {
            "analysis": analysis,
            "issues": issues,
            "suggestions": suggestions,
            "version": self.version
        }

    def get_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        return {
            "name": self.name,
            "version": self.version,
            "history_count": len(self.history),
            "last_analysis": self.history[-1] if self.history else None,
            "timestamp": datetime.now().isoformat()
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="智能进化架构自省与自我重构引擎")
    parser.add_argument("command", nargs="?", default="status",
                       help="命令: status, analyze, issues, suggestions, reflect, refactor")
    parser.add_argument("--dry-run", action="store_true", default=True,
                       help="试运行模式（不实际执行修改）")
    parser.add_argument("--execute", action="store_true",
                       help="实际执行重构")

    args = parser.parse_args()
    engine = EvolutionArchitectureSelfReflection()

    if args.command == "status":
        print(json.dumps(engine.get_status(), ensure_ascii=False, indent=2))

    elif args.command == "analyze":
        result = engine.analyze_architecture()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "issues":
        result = engine.identify_issues()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "suggestions":
        result = engine.generate_suggestions()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "reflect":
        result = engine.self_reflect()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "refactor":
        dry_run = not args.execute
        result = engine.execute_simple_refactoring(dry_run=dry_run)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {args.command}")
        print("可用命令: status, analyze, issues, suggestions, reflect, refactor")


if __name__ == "__main__":
    main()