#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能进化架构自省与自我重构引擎 (Evolution Architecture Self-Refactor Engine)
让系统能够主动分析自身架构问题、识别优化机会、自动进行结构优化，实现真正的自主架构进化。

功能：
1. 架构自省 - 分析 scripts/ 目录下的模块结构、依赖关系、代码质量
2. 优化机会识别 - 检测重复代码、可合并模块、可以简化的逻辑
3. 自动结构优化 - 自动进行代码重构建议或执行优化
4. 架构进化追踪 - 记录架构变更历史，评估优化效果

集成：支持"架构自省"、"自我重构"、"架构优化"、"自我分析"、"架构进化"等关键词触发
"""

import os
import sys
import json
import ast
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict
import hashlib

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPTS)
RUNTIME_STATE = os.path.join(PROJECT, "runtime", "state")
RUNTIME_LOGS = os.path.join(PROJECT, "runtime", "logs")
REFERENCES = os.path.join(PROJECT, "references")


class EvolutionArchitectureSelfRefactor:
    """智能进化架构自省与自我重构引擎"""

    def __init__(self):
        self.name = "EvolutionArchitectureSelfRefactor"
        self.version = "1.0.0"
        self.analysis_path = os.path.join(RUNTIME_STATE, "architecture_analysis.json")
        self.refactor_path = os.path.join(RUNTIME_STATE, "architecture_refactor.json")
        self.evolution_path = os.path.join(RUNTIME_STATE, "architecture_evolution.json")

        self.analysis_data = self._load_analysis()
        self.refactor_data = self._load_refactor()
        self.evolution_data = self._load_evolution()

    def _load_analysis(self) -> Dict:
        """加载架构分析数据"""
        if os.path.exists(self.analysis_path):
            try:
                with open(self.analysis_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"modules": {}, "last_analysis": None}

    def _save_analysis(self):
        """保存架构分析数据"""
        try:
            with open(self.analysis_path, "w", encoding="utf-8") as f:
                json.dump(self.analysis_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存分析数据失败: {e}")

    def _load_refactor(self) -> Dict:
        """加载重构数据"""
        if os.path.exists(self.refactor_path):
            try:
                with open(self.refactor_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"pending": [], "completed": [], "rejected": []}

    def _save_refactor(self):
        """保存重构数据"""
        try:
            with open(self.refactor_path, "w", encoding="utf-8") as f:
                json.dump(self.refactor_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存重构数据失败: {e}")

    def _load_evolution(self) -> Dict:
        """加载架构进化历史"""
        if os.path.exists(self.evolution_path):
            try:
                with open(self.evolution_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"changes": [], "total_refactors": 0}

    def _save_evolution(self):
        """保存架构进化历史"""
        try:
            with open(self.evolution_path, "w", encoding="utf-8") as f:
                json.dump(self.evolution_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存进化历史失败: {e}")

    def analyze_architecture(self) -> Dict:
        """分析系统架构"""
        print("[架构自省] 正在分析系统架构...")

        modules = {}
        duplicate_analysis = {}
        dependency_graph = defaultdict(list)

        # 获取所有 Python 脚本
        script_files = []
        for root, dirs, files in os.walk(SCRIPTS):
            for f in files:
                if f.endswith('.py') and not f.startswith('__'):
                    script_files.append(os.path.join(root, f))

        print(f"[架构自省] 发现 {len(script_files)} 个 Python 模块")

        # 分析每个模块
        for script_path in script_files:
            try:
                with open(script_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 解析 AST
                try:
                    tree = ast.parse(content)
                except SyntaxError:
                    continue

                module_name = os.path.relpath(script_path, SCRIPTS).replace('\\', '/')

                # 提取模块信息
                module_info = {
                    "path": module_name,
                    "size": len(content),
                    "lines": len(content.split('\n')),
                    "imports": [],
                    "functions": [],
                    "classes": [],
                    "docstring": ast.get_docstring(tree) or ""
                }

                # 提取导入
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            module_info["imports"].append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            module_info["imports"].append(node.module)

                # 提取函数和类
                for node in ast.iter_child_nodes(tree):
                    if isinstance(node, ast.FunctionDef):
                        module_info["functions"].append({
                            "name": node.name,
                            "args": [arg.arg for arg in node.args.args],
                            "line": node.lineno
                        })
                    elif isinstance(node, ast.ClassDef):
                        methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                        module_info["classes"].append({
                            "name": node.name,
                            "methods": methods,
                            "line": node.lineno
                        })

                # 计算模块哈希（用于检测重复）
                content_hash = hashlib.md5(content.encode()).hexdigest()
                module_info["hash"] = content_hash

                modules[module_name] = module_info

            except Exception as e:
                print(f"[架构自省] 分析模块失败 {script_path}: {e}")

        # 检测重复代码
        hash_to_modules = defaultdict(list)
        for mod_name, mod_info in modules.items():
            if "hash" in mod_info:
                hash_to_modules[mod_info["hash"]].append(mod_name)

        duplicate_analysis = {
            mod_names: info
            for mod_names in hash_to_modules.values()
            if len(mod_names) > 1
            for mod_name in mod_names
            for info in [modules.get(mod_name, {})]
            if mod_names
        }

        self.analysis_data = {
            "modules": modules,
            "duplicate_analysis": duplicate_analysis,
            "module_count": len(modules),
            "last_analysis": datetime.now().isoformat()
        }

        self._save_analysis()

        print(f"[架构自省] 分析完成：{len(modules)} 个模块")

        return self.analysis_data

    def identify_optimization_opportunities(self) -> List[Dict]:
        """识别优化机会"""
        print("[架构自省] 正在识别优化机会...")

        opportunities = []

        if not self.analysis_data.get("modules"):
            self.analyze_architecture()

        modules = self.analysis_data.get("modules", {})

        # 1. 检测大文件（可拆分）
        for mod_name, mod_info in modules.items():
            if mod_info.get("lines", 0) > 500:
                opportunities.append({
                    "type": "large_module",
                    "severity": "medium",
                    "module": mod_name,
                    "description": f"模块过大 ({mod_info.get('lines')} 行)，建议拆分为多个子模块",
                    "suggestion": "将大型模块按功能拆分为多个小模块"
                })

        # 2. 检测功能相似的模块
        module_functions = defaultdict(list)
        for mod_name, mod_info in modules.items():
            for func in mod_info.get("functions", []):
                module_functions[func["name"]].append(mod_name)

        for func_name, mod_names in module_functions.items():
            if len(mod_names) > 1 and func_name not in ["__init__", "main", "run"]:
                opportunities.append({
                    "type": "similar_functions",
                    "severity": "low",
                    "modules": mod_names,
                    "description": f"函数 '{func_name}' 在多个模块中重复定义",
                    "suggestion": "考虑将重复函数提取到共享模块"
                })

        # 3. 检测缺少文档的模块
        for mod_name, mod_info in modules.items():
            if not mod_info.get("docstring") and mod_info.get("lines", 0) > 50:
                opportunities.append({
                    "type": "missing_docstring",
                    "severity": "low",
                    "module": mod_name,
                    "description": f"模块缺少文档字符串",
                    "suggestion": "添加模块级文档字符串"
                })

        # 4. 检测孤立模块（无导入其他模块）
        isolated_count = 0
        for mod_name, mod_info in modules.items():
            if not mod_info.get("imports"):
                isolated_count += 1

        if isolated_count > 5:
            opportunities.append({
                "type": "isolated_modules",
                "severity": "low",
                "count": isolated_count,
                "description": f"发现 {isolated_count} 个孤立模块（无外部依赖）",
                "suggestion": "考虑是否有可复用的功能可以提取"
            })

        # 5. 检测可能的重复代码块
        duplicate_modules = self.analysis_data.get("duplicate_analysis", {})
        for dup_modules in duplicate_modules.values():
            if len(dup_modules) > 1:
                opportunities.append({
                    "type": "duplicate_code",
                    "severity": "medium",
                    "modules": list(dup_modules.keys()) if isinstance(dup_modules, dict) else dup_modules,
                    "description": "检测到可能重复的代码",
                    "suggestion": "合并重复代码到共享模块"
                })

        print(f"[架构自省] 发现 {len(opportunities)} 个优化机会")

        return opportunities

    def generate_refactor_suggestions(self) -> List[Dict]:
        """生成重构建议"""
        opportunities = self.identify_optimization_opportunities()

        suggestions = []
        for opp in opportunities:
            if opp["severity"] in ["medium", "high"]:
                suggestions.append({
                    "priority": "high" if opp["severity"] == "high" else "medium",
                    "issue": opp["description"],
                    "suggestion": opp["suggestion"],
                    "type": opp["type"]
                })

        # 添加架构健康评分
        health_score = self._calculate_architecture_health()

        result = {
            "suggestions": suggestions,
            "opportunities_count": len(opportunities),
            "health_score": health_score,
            "timestamp": datetime.now().isoformat()
        }

        return result

    def _calculate_architecture_health(self) -> Dict:
        """计算架构健康评分"""
        if not self.analysis_data.get("modules"):
            self.analyze_architecture()

        modules = self.analysis_data.get("modules", {})
        opportunities = self.identify_optimization_opportunities()

        # 基础分数
        base_score = 100

        # 根据优化机会数量扣分
        deduction = min(len(opportunities) * 2, 30)

        # 根据模块数量调整
        module_count = len(modules)
        if module_count < 50:
            adjustment = -5
        elif module_count > 200:
            adjustment = -10
        else:
            adjustment = 0

        total_score = max(0, base_score - deduction + adjustment)

        return {
            "score": total_score,
            "grade": "A" if total_score >= 90 else "B" if total_score >= 70 else "C" if total_score >= 50 else "D",
            "module_count": module_count,
            "opportunities": len(opportunities)
        }

    def get_architecture_summary(self) -> Dict:
        """获取架构摘要"""
        if not self.analysis_data.get("modules"):
            self.analyze_architecture()

        modules = self.analysis_data.get("modules", {})
        health = self._calculate_architecture_health()

        # 统计模块类型
        script_count = sum(1 for m in modules.keys() if m.startswith("scripts/"))
        plan_count = sum(1 for m in modules.keys() if "plans" in m or "plan" in m)

        summary = {
            "total_modules": len(modules),
            "scripts_dir": script_count,
            "health": health,
            "last_analysis": self.analysis_data.get("last_analysis"),
            "module_stats": {
                "avg_lines": sum(m.get("lines", 0) for m in modules.values()) / max(len(modules), 1),
                "max_lines": max((m.get("lines", 0) for m in modules.values()), default=0),
                "min_lines": min((m.get("lines", 0) for m in modules.values()), default=0)
            }
        }

        return summary


def main():
    """主入口"""
    engine = EvolutionArchitectureSelfRefactor()

    args = sys.argv[1:] if len(sys.argv) > 1 else []

    if not args or "help" in args or "--help" in args:
        print("""
智能进化架构自省与自我重构引擎

用法:
    python evolution_architecture_self_refactor.py <命令>

命令:
    analyze       - 分析系统架构
    opportunities - 识别优化机会
    suggestions   - 生成重构建议
    summary       - 获取架构摘要
    health        - 计算架构健康评分
    status        - 获取完整状态
        """)
        return

    command = args[0].lower()

    if command == "analyze":
        result = engine.analyze_architecture()
        print(f"[完成] 架构分析完成，共 {result.get('module_count', 0)} 个模块")

    elif command == "opportunities":
        opportunities = engine.identify_optimization_opportunities()
        print(f"[完成] 发现 {len(opportunities)} 个优化机会")
        for i, opp in enumerate(opportunities[:5], 1):
            print(f"  {i}. [{opp['severity']}] {opp['description']}")

    elif command == "suggestions":
        result = engine.generate_refactor_suggestions()
        print(f"[完成] 健康评分: {result['health_score']['score']} ({result['health_score']['grade']})")
        print(f"[完成] 发现 {result['opportunities_count']} 个优化机会")
        for sug in result["suggestions"][:3]:
            print(f"  - [{sug['priority']}] {sug['issue']}")

    elif command == "summary":
        summary = engine.get_architecture_summary()
        print(f"[架构摘要]")
        print(f"  总模块数: {summary['total_modules']}")
        print(f"  健康评分: {summary['health']['score']} ({summary['health']['grade']})")
        print(f"  平均行数: {summary['module_stats']['avg_lines']:.1f}")

    elif command == "health":
        health = engine._calculate_architecture_health()
        print(f"[架构健康评分] {health['score']} ({health['grade']})")
        print(f"  模块数: {health['module_count']}")
        print(f"  优化机会: {health['opportunities']}")

    elif command == "status":
        summary = engine.get_architecture_summary()
        opportunities = engine.identify_optimization_opportunities()
        suggestions = engine.generate_refactor_suggestions()

        print(f"""
=== 智能进化架构自省与自我重构引擎 ===
版本: {engine.version}

【架构摘要】
  总模块数: {summary['total_modules']}
  健康评分: {summary['health']['score']} ({summary['health']['grade']})

【优化机会】: {len(opportunities)} 个
【重构建议】: {len(suggestions['suggestions'])} 条
【最后分析】: {summary['last_analysis']}
        """)

    else:
        print(f"[未知命令] {command}")
        print("使用 'python evolution_architecture_self_refactor.py help' 查看帮助")


if __name__ == "__main__":
    main()