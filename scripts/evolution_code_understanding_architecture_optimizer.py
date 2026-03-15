#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环代码理解与架构优化引擎
(Code Understanding & Architecture Optimization Engine)

让系统能够大规模分析70+进化引擎的代码结构、识别重复代码模式、
发现可复用模块、生成优化建议。这是LLM特有优势的应用，
可以让系统像人一样"阅读理解"自己的代码，并发现优化机会。

增强版(v1.1.0): 新增基于代码分析的自动修复与自优化能力
- 代码质量问题自动发现
- 智能修复方案自动生成
- 自动修复执行与效果验证

实现从「被动维护代码」到「主动理解与优化架构」的范式升级。

Version: 1.1.0
"""

import json
import os
import re
import sys
import ast
import hashlib
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from collections import defaultdict
from dataclasses import dataclass, field

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
STATE_DIR = PROJECT_ROOT / "runtime" / "state"
DATA_DIR = PROJECT_ROOT / "runtime" / "data"
LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# 添加 scripts 目录到路径以便导入
sys.path.insert(0, str(SCRIPTS_DIR))


@dataclass
class CodeModule:
    """代码模块信息"""
    path: str
    name: str
    size: int
    imports: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    docstring: str = ""
    complexity: int = 0


@dataclass
class CodePattern:
    """代码模式信息"""
    pattern_type: str  # "duplicate", "opportunity", "refactor_candidate"
    description: str
    files_involved: List[str]
    suggestion: str
    priority: str = "medium"  # "high", "medium", "low"


@dataclass
class CodeQualityIssue:
    """代码质量问题"""
    issue_type: str  # "complexity", "duplication", "style", "performance", "security"
    file_path: str
    location: str  # "module", "function", "class"
    target_name: str
    description: str
    severity: str = "medium"  # "critical", "high", "medium", "low"
    auto_fixable: bool = False


@dataclass
class AutoFix:
    """自动修复信息"""
    issue_id: str
    file_path: str
    original_content: str
    fixed_content: str
    fix_description: str
    applied: bool = False
    verified: bool = False


class CodeUnderstandingArchitectureOptimizer:
    """代码理解与架构优化引擎核心类"""

    def __init__(self):
        self.version = "1.1.0"
        self.name = "Code Understanding & Architecture Optimizer"
        self.runtime_dir = PROJECT_ROOT / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.data_dir = self.runtime_dir / "data"

        # 数据文件路径
        self.analysis_cache_file = self.data_dir / "code_understanding_cache.json"
        self.patterns_file = self.data_dir / "code_patterns.json"
        self.optimization_suggestions_file = self.data_dir / "code_optimization_suggestions.json"
        self.architecture_report_file = self.data_dir / "code_architecture_report.json"
        self.quality_issues_file = self.data_dir / "code_quality_issues.json"
        self.auto_fixes_file = self.data_dir / "code_auto_fixes.json"

        self._ensure_directories()
        self._initialize_data()

    def _ensure_directories(self):
        """确保必要的目录存在"""
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _initialize_data(self):
        """初始化数据文件"""
        if not self.analysis_cache_file.exists():
            self._save_json(self.analysis_cache_file, {
                "last_analysis": None,
                "modules": {}
            })

        if not self.patterns_file.exists():
            self._save_json(self.patterns_file, {
                "last_analysis": None,
                "patterns": []
            })

        if not self.optimization_suggestions_file.exists():
            self._save_json(self.optimization_suggestions_file, {
                "last_analysis": None,
                "suggestions": []
            })

        if not self.quality_issues_file.exists():
            self._save_json(self.quality_issues_file, {
                "last_scan": None,
                "issues": []
            })

        if not self.auto_fixes_file.exists():
            self._save_json(self.auto_fixes_file, {
                "last_fix": None,
                "fixes": []
            })

    def _save_json(self, file_path: Path, data: Any):
        """保存 JSON 数据"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_json(self, file_path: Path) -> Any:
        """加载 JSON 数据"""
        if not file_path.exists():
            return {}
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _get_all_python_files(self, directory: Path) -> List[Path]:
        """获取目录下所有 Python 文件"""
        python_files = []
        if not directory.exists():
            return python_files

        for item in directory.rglob("*.py"):
            # 跳过 __pycache__ 和测试文件
            if "__pycache__" in str(item) or "test_" in item.name:
                continue
            python_files.append(item)
        return python_files

    def _calculate_file_hash(self, file_path: Path) -> str:
        """计算文件内容哈希"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                return hashlib.md5(content.encode('utf-8')).hexdigest()
        except Exception:
            return ""

    def _analyze_python_file(self, file_path: Path) -> Optional[CodeModule]:
        """分析单个 Python 文件"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                tree = ast.parse(content, filename=str(file_path))

            module = CodeModule(
                path=str(file_path),
                name=file_path.stem,
                size=len(content),
                imports=[],
                functions=[],
                classes=[],
                complexity=0
            )

            # 提取导入
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module.imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module.imports.append(node.module)

            # 提取函数和类
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    module.functions.append(node.name)
                    # 简单计算复杂度
                    module.complexity += self._calculate_function_complexity(node)
                elif isinstance(node, ast.ClassDef):
                    module.classes.append(node.name)
                    # 提取类中的方法
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            module.functions.append(f"{node.name}.{item.name}")

            # 提取文档字符串
            if ast.get_docstring(tree):
                module.docstring = ast.get_docstring(tree)[:200]  # 限制长度

            return module

        except Exception as e:
            return None

    def _calculate_function_complexity(self, node: ast.FunctionDef) -> int:
        """计算函数复杂度"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def analyze_codebase(self) -> Dict[str, Any]:
        """分析整个代码库"""
        print("开始分析代码库...")

        # 获取 scripts 目录下的所有 Python 文件
        scripts_dir = PROJECT_ROOT / "scripts"
        python_files = self._get_all_python_files(scripts_dir)

        print(f"找到 {len(python_files)} 个 Python 文件")

        modules = []
        module_map = {}

        for file_path in python_files:
            module = self._analyze_python_file(file_path)
            if module:
                modules.append(module)
                module_map[module.path] = {
                    "name": module.name,
                    "size": module.size,
                    "imports": module.imports,
                    "functions": module.functions,
                    "classes": module.classes,
                    "complexity": module.complexity,
                    "docstring": module.docstring
                }

        # 保存分析结果
        cache_data = {
            "last_analysis": datetime.now().isoformat(),
            "total_files": len(modules),
            "total_size": sum(m.size for m in modules),
            "total_functions": sum(len(m.functions) for m in modules),
            "total_classes": sum(len(m.classes) for m in modules),
            "modules": module_map
        }
        self._save_json(self.analysis_cache_file, cache_data)

        print(f"分析完成：{len(modules)} 个模块，{sum(m.complexity for m in modules)} 总复杂度")

        return cache_data

    def find_duplicate_patterns(self) -> List[CodePattern]:
        """识别重复代码模式"""
        cache_data = self._load_json(self.analysis_cache_file)

        if not cache_data.get("modules"):
            print("缓存为空，先运行分析...")
            self.analyze_codebase()
            cache_data = self._load_json(self.analysis_cache_file)

        modules = cache_data.get("modules", {})
        patterns = []

        # 分析函数级别的重复
        function_bodies = defaultdict(list)
        function_bodies_by_name = defaultdict(list)

        for path, info in modules.items():
            for func in info.get("functions", []):
                # 简单按函数名分组（更精确的做法是分析函数体）
                function_bodies_by_name[func].append(path)

        # 找出同名函数出现在多个文件中的情况
        for func_name, paths in function_bodies_by_name.items():
            if len(paths) > 1:
                # 检查是否是辅助函数或通用函数
                if not func_name.startswith("_") and not "." in func_name:
                    patterns.append(CodePattern(
                        pattern_type="duplicate",
                        description=f"函数 '{func_name}' 在 {len(paths)} 个文件中出现",
                        files_involved=paths,
                        suggestion=f"考虑将 '{func_name}' 提取到共享工具模块",
                        priority="medium"
                    ))

        # 分析导入模式
        import_groups = defaultdict(list)
        for path, info in modules.items():
            imports = tuple(sorted(info.get("imports", [])))
            import_groups[imports].append(path)

        # 找出导入模式相似的文件组
        for imports, paths in import_groups.items():
            if len(paths) > 3 and len(imports) > 5:
                patterns.append(CodePattern(
                    pattern_type="opportunity",
                    description=f"{len(paths)} 个文件有相似的导入模式",
                    files_involved=paths,
                    suggestion="考虑创建共享的基础模块，统一管理这些依赖",
                    priority="low"
                ))

        # 保存模式结果
        patterns_data = {
            "last_analysis": datetime.now().isoformat(),
            "patterns": [
                {
                    "type": p.pattern_type,
                    "description": p.description,
                    "files": p.files_involved,
                    "suggestion": p.suggestion,
                    "priority": p.priority
                }
                for p in patterns
            ]
        }
        self._save_json(self.patterns_file, patterns_data)

        print(f"发现 {len(patterns)} 个代码模式")
        return patterns

    def discover_reusable_modules(self) -> Dict[str, Any]:
        """发现可复用模块"""
        cache_data = self._load_json(self.analysis_cache_file)

        if not cache_data.get("modules"):
            print("缓存为空，先运行分析...")
            self.analyze_codebase()
            cache_data = self._load_json(self.analysis_cache_file)

        modules = cache_data.get("modules", {})

        # 找出高价值的可复用模块
        # 标准：功能多、复杂度适中、导入少的模块
        reusable_candidates = []

        for path, info in modules.items():
            functions = info.get("functions", [])
            classes = info.get("classes", [])
            imports = info.get("imports", [])
            complexity = info.get("complexity", 0)

            # 计算可复用性评分
            score = len(functions) * 2 + len(classes) * 3
            if len(imports) < 10:  # 低耦合
                score *= 1.5

            if score > 5:
                reusable_candidates.append({
                    "path": path,
                    "name": info.get("name"),
                    "score": score,
                    "functions": len(functions),
                    "classes": len(classes),
                    "complexity": complexity,
                    "coupling": len(imports)
                })

        # 按评分排序
        reusable_candidates.sort(key=lambda x: x["score"], reverse=True)

        return {
            "last_analysis": datetime.now().isoformat(),
            "candidates": reusable_candidates[:20],  # 返回前20个
            "total_candidates": len(reusable_candidates)
        }

    def generate_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """生成优化建议"""
        cache_data = self._load_json(self.analysis_cache_file)
        patterns = self._load_json(self.patterns_file)
        reusable = self.discover_reusable_modules()

        suggestions = []

        # 基于复杂度分析
        high_complexity = []
        for path, info in cache_data.get("modules", {}).items():
            if info.get("complexity", 0) > 20:
                high_complexity.append({
                    "path": path,
                    "name": info.get("name"),
                    "complexity": info.get("complexity")
                })

        if high_complexity:
            suggestions.append({
                "category": "complexity",
                "title": "高复杂度模块",
                "description": f"发现 {len(high_complexity)} 个高复杂度模块，建议重构",
                "items": high_complexity[:5],
                "priority": "high"
            })

        # 基于重复模式
        if patterns.get("patterns"):
            suggestions.append({
                "category": "duplication",
                "title": "代码重复模式",
                "description": f"发现 {len(patterns['patterns'])} 个代码重复/优化机会",
                "items": patterns["patterns"][:3],
                "priority": "medium"
            })

        # 基于可复用性
        if reusable.get("candidates"):
            suggestions.append({
                "category": "reusability",
                "title": "可复用模块候选",
                "description": f"发现 {len(reusable['candidates'])} 个高可复用性模块",
                "items": reusable["candidates"][:5],
                "priority": "low"
            })

        # 保存建议
        suggestions_data = {
            "last_analysis": datetime.now().isoformat(),
            "suggestions": suggestions
        }
        self._save_json(self.optimization_suggestions_file, suggestions_data)

        return suggestions

    def generate_architecture_report(self) -> Dict[str, Any]:
        """生成架构报告"""
        cache_data = self._load_json(self.analysis_cache_file)
        patterns = self._load_json(self.patterns_file)
        suggestions = self._load_json(self.optimization_suggestions_file)

        # 统计概览
        total_files = cache_data.get("total_files", 0)
        total_functions = cache_data.get("total_functions", 0)
        total_classes = cache_data.get("total_classes", 0)
        total_size = cache_data.get("total_size", 0)

        # 分析模块间依赖
        all_imports = set()
        for path, info in cache_data.get("modules", {}).items():
            for imp in info.get("imports", []):
                all_imports.add(imp)

        # 生成报告
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_modules": total_files,
                "total_functions": total_functions,
                "total_classes": total_classes,
                "total_lines": total_size // 50,  # 估算
                "unique_imports": len(all_imports)
            },
            "patterns": patterns.get("patterns", []),
            "suggestions": suggestions.get("suggestions", []),
            "status": "analyzed"
        }

        self._save_json(self.architecture_report_file, report)

        return report

    def run_full_analysis(self) -> Dict[str, Any]:
        """运行完整分析流程"""
        print("=" * 50)
        print("开始代码理解与架构优化分析")
        print("=" * 50)

        # 1. 分析代码库
        analysis = self.analyze_codebase()

        # 2. 查找重复模式
        patterns = self.find_duplicate_patterns()

        # 3. 发现可复用模块
        reusable = self.discover_reusable_modules()

        # 4. 生成优化建议
        suggestions = self.generate_optimization_suggestions()

        # 5. 生成架构报告
        report = self.generate_architecture_report()

        print("=" * 50)
        print("分析完成")
        print("=" * 50)

        return {
            "analysis": analysis,
            "patterns_count": len(patterns),
            "reusable_count": len(reusable.get("candidates", [])),
            "suggestions_count": len(suggestions),
            "report": report
        }

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱数据接口"""
        report_data = self._load_json(self.architecture_report_file)
        suggestions_data = self._load_json(self.optimization_suggestions_file)

        summary = report_data.get("summary", {})
        suggestions = suggestions_data.get("suggestions", [])

        # 计算健康度评分
        health_score = 100
        high_priority = sum(1 for s in suggestions if s.get("priority") == "high")
        health_score -= high_priority * 15
        medium_priority = sum(1 for s in suggestions if s.get("priority") == "medium")
        health_score -= medium_priority * 8

        return {
            "module_name": "代码理解与架构优化引擎",
            "version": self.version,
            "status": "active",
            "last_analysis": report_data.get("generated_at"),
            "health_score": max(0, health_score),
            "total_modules": summary.get("total_modules", 0),
            "total_functions": summary.get("total_functions", 0),
            "total_classes": summary.get("total_classes", 0),
            "patterns_count": len(report_data.get("patterns", [])),
            "suggestions_count": len(suggestions),
            "high_priority_suggestions": high_priority,
            "recommendations": [
                s.get("title", "") for s in suggestions if s.get("priority") == "high"
            ]
        }

    def status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        cache_data = self._load_json(self.analysis_cache_file)
        quality_data = self._load_json(self.quality_issues_file)
        fixes_data = self._load_json(self.auto_fixes_file)
        return {
            "name": self.name,
            "version": self.version,
            "status": "active",
            "last_analysis": cache_data.get("last_analysis"),
            "total_modules_analyzed": cache_data.get("total_files", 0),
            "quality_issues_count": len(quality_data.get("issues", [])),
            "auto_fixes_applied": len([f for f in fixes_data.get("fixes", []) if f.get("applied")])
        }

    def detect_code_quality_issues(self) -> List[CodeQualityIssue]:
        """检测代码质量问题"""
        print("开始检测代码质量问题...")

        # 确保已有分析数据
        cache_data = self._load_json(self.analysis_cache_file)
        if not cache_data.get("modules"):
            self.analyze_codebase()
            cache_data = self._load_json(self.analysis_cache_file)

        issues = []
        modules = cache_data.get("modules", {})

        for path, info in modules.items():
            # 检查高复杂度
            complexity = info.get("complexity", 0)
            if complexity > 20:
                issues.append(CodeQualityIssue(
                    issue_type="complexity",
                    file_path=path,
                    location="module",
                    target_name=info.get("name", ""),
                    description=f"模块复杂度过高 ({complexity})，建议重构",
                    severity="high" if complexity > 30 else "medium",
                    auto_fixable=False
                ))

            # 检查过长的函数列表
            functions = info.get("functions", [])
            if len(functions) > 20:
                issues.append(CodeQualityIssue(
                    issue_type="style",
                    file_path=path,
                    location="module",
                    target_name=info.get("name", ""),
                    description=f"模块包含过多函数 ({len(functions)})，建议拆分",
                    severity="medium",
                    auto_fixable=False
                ))

            # 检查过多的导入
            imports = info.get("imports", [])
            if len(imports) > 20:
                issues.append(CodeQualityIssue(
                    issue_type="style",
                    file_path=path,
                    location="module",
                    target_name=info.get("name", ""),
                    description=f"模块导入过多依赖 ({len(imports)})，建议重构",
                    severity="low",
                    auto_fixable=False
                ))

        # 保存问题列表
        issues_data = {
            "last_scan": datetime.now().isoformat(),
            "issues": [
                {
                    "type": i.issue_type,
                    "file": i.file_path,
                    "location": i.location,
                    "target": i.target_name,
                    "description": i.description,
                    "severity": i.severity,
                    "auto_fixable": i.auto_fixable
                }
                for i in issues
            ]
        }
        self._save_json(self.quality_issues_file, issues_data)

        print(f"发现 {len(issues)} 个代码质量问题")
        return issues

    def generate_auto_fix(self, issue: CodeQualityIssue) -> Optional[AutoFix]:
        """为特定问题生成自动修复方案"""
        if not issue.auto_fixable:
            return None

        try:
            with open(issue.file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            # 简单的自动修复逻辑
            fixed_content = original_content

            if issue.issue_type == "style":
                # 添加缺失的文档字符串
                if "def " in original_content and '"""' not in original_content:
                    fixed_content = original_content.replace(
                        "def ",
                        'def """TODO: Add docstring"""\n    def '
                    )

            fix_id = hashlib.md5(f"{issue.file_path}{datetime.now().isoformat()}".encode()).hexdigest()[:8]

            return AutoFix(
                issue_id=fix_id,
                file_path=issue.file_path,
                original_content=original_content,
                fixed_content=fixed_content,
                fix_description=f"自动修复 {issue.issue_type} 问题",
                applied=False,
                verified=False
            )

        except Exception as e:
            print(f"生成修复方案失败: {e}")
            return None

    def apply_auto_fix(self, fix: AutoFix, dry_run: bool = False) -> bool:
        """应用自动修复"""
        try:
            # 先备份原文件
            backup_path = f"{fix.file_path}.bak"
            shutil.copy2(fix.file_path, backup_path)

            if dry_run:
                print(f"[Dry Run] 将在 {fix.file_path} 上应用修复")
                return True

            # 应用修复
            with open(fix.file_path, 'w', encoding='utf-8') as f:
                f.write(fix.fixed_content)

            print(f"已应用修复到 {fix.file_path}")
            return True

        except Exception as e:
            print(f"应用修复失败: {e}")
            return False

    def verify_fix(self, fix: AutoFix) -> bool:
        """验证修复效果"""
        try:
            # 简单验证：尝试导入修复后的模块
            if fix.file_path.endswith(".py"):
                result = subprocess.run(
                    [sys.executable, "-c", f"import sys; sys.path.insert(0, '{SCRIPTS_DIR}'); exec(open('{fix.file_path}').read())"],
                    capture_output=True,
                    timeout=10
                )
                return result.returncode == 0
            return True
        except Exception as e:
            print(f"验证修复失败: {e}")
            return False

    def run_auto_fix_cycle(self, dry_run: bool = False) -> Dict[str, Any]:
        """运行完整的自动修复周期"""
        print("=" * 50)
        print("开始代码自动修复周期")
        print("=" * 50)

        # 1. 检测问题
        issues = self.detect_code_quality_issues()

        # 2. 生成修复方案
        auto_fixable = [i for i in issues if i.auto_fixable]
        fixes = []
        for issue in auto_fixable:
            fix = self.generate_auto_fix(issue)
            if fix:
                fixes.append(fix)

        # 3. 应用修复
        applied = []
        for fix in fixes:
            if self.apply_auto_fix(fix, dry_run):
                fix.applied = True
                # 4. 验证修复
                if self.verify_fix(fix):
                    fix.verified = True
                applied.append(fix)

        # 保存修复记录
        fixes_data = {
            "last_fix": datetime.now().isoformat(),
            "fixes": [
                {
                    "issue_id": f.issue_id,
                    "file": f.file_path,
                    "description": f.fix_description,
                    "applied": f.applied,
                    "verified": f.verified
                }
                for f in fixes
            ]
        }
        self._save_json(self.auto_fixes_file, fixes_data)

        print("=" * 50)
        print(f"自动修复完成：{len(applied)} 个修复已应用")
        print("=" * 50)

        return {
            "issues_detected": len(issues),
            "auto_fixable": len(auto_fixable),
            "fixes_generated": len(fixes),
            "fixes_applied": len(applied),
            "fixes_verified": len([f for f in applied if f.verified])
        }

    def get_optimization_status(self) -> Dict[str, Any]:
        """获取优化状态"""
        quality_data = self._load_json(self.quality_issues_file)
        fixes_data = self._load_json(self.auto_fixes_file)

        return {
            "last_scan": quality_data.get("last_scan"),
            "total_issues": len(quality_data.get("issues", [])),
            "auto_fixes_applied": len([f for f in fixes_data.get("fixes", []) if f.get("applied")]),
            "auto_fixes_verified": len([f for f in fixes_data.get("fixes", []) if f.get("verified")])
        }


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="代码理解与架构优化引擎"
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="运行完整代码分析"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="查看引擎状态"
    )
    parser.add_argument(
        "--find-patterns",
        action="store_true",
        help="查找重复代码模式"
    )
    parser.add_argument(
        "--discover-reusable",
        action="store_true",
        help="发现可复用模块"
    )
    parser.add_argument(
        "--suggestions",
        action="store_true",
        help="生成优化建议"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="生成架构报告"
    )
    parser.add_argument(
        "--cockpit-data",
        action="store_true",
        help="获取驾驶舱数据接口"
    )
    parser.add_argument(
        "--detect-issues",
        action="store_true",
        help="检测代码质量问题"
    )
    parser.add_argument(
        "--auto-fix",
        action="store_true",
        help="运行自动修复周期"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="模拟运行自动修复，不实际修改文件"
    )
    parser.add_argument(
        "--optimization-status",
        action="store_true",
        help="获取优化状态"
    )

    args = parser.parse_args()

    engine = CodeUnderstandingArchitectureOptimizer()

    if args.analyze:
        result = engine.run_full_analysis()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.status:
        status = engine.status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    elif args.find_patterns:
        patterns = engine.find_duplicate_patterns()
        print(f"发现 {len(patterns)} 个代码模式")
        for p in patterns:
            print(f"  - {p.description}")
    elif args.discover_reusable:
        reusable = engine.discover_reusable_modules()
        print(json.dumps(reusable, ensure_ascii=False, indent=2))
    elif args.suggestions:
        suggestions = engine.generate_optimization_suggestions()
        print(json.dumps(suggestions, ensure_ascii=False, indent=2))
    elif args.report:
        report = engine.generate_architecture_report()
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
    elif args.detect_issues:
        issues = engine.detect_code_quality_issues()
        print(json.dumps({
            "total_issues": len(issues),
            "issues": [
                {
                    "type": i.issue_type,
                    "file": i.file_path,
                    "description": i.description,
                    "severity": i.severity,
                    "auto_fixable": i.auto_fixable
                }
                for i in issues
            ]
        }, ensure_ascii=False, indent=2))
    elif args.auto_fix:
        result = engine.run_auto_fix_cycle(dry_run=args.dry_run)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.optimization_status:
        status = engine.get_optimization_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    else:
        # 默认显示状态
        status = engine.status()
        print(json.dumps(status, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()