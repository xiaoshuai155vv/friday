#!/usr/bin/env python3
"""
智能代码理解与重构引擎

利用 LLM 的代码理解能力，提供代码分析、依赖检测、重构建议等功能。
支持代码结构分析、依赖检测、代码质量评估、智能重构建议。

集成到 do.py 支持：
- 代码分析
- 代码理解
- 代码重构
等关键词触发
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class CodeStructure:
    """代码结构信息"""
    file_path: str
    language: str
    functions: List[Dict] = field(default_factory=list)
    classes: List[Dict] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)
    dependencies: List[Dict] = field(default_factory=list)


@dataclass
class CodeQuality:
    """代码质量评估结果"""
    file_path: str
    complexity: int = 0
    lines_of_code: int = 0
    comment_ratio: float = 0.0
    issues: List[str] = field(default_factory=list)
    score: float = 0.0


@dataclass
class RefactoringSuggestion:
    """重构建议"""
    file_path: str
    issue: str
    suggestion: str
    priority: str  # high, medium, low
    impact: str  # performance, readability, maintainability, security


class CodeUnderstandingEngine:
    """智能代码理解与重构引擎"""

    def __init__(self, project_path: str = None):
        self.project_path = project_path or self._get_default_project_path()
        self.analysis_cache = {}
        self.supported_languages = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.cs': 'csharp',
        }

    def _get_default_project_path(self) -> str:
        """获取默认项目路径"""
        # 尝试获取当前工作目录
        return os.getcwd()

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """分析单个代码文件"""
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        ext = os.path.splitext(file_path)[1].lower()
        language = self.supported_languages.get(ext, 'unknown')

        result = {
            "file_path": file_path,
            "language": language,
            "structure": self._extract_structure(file_path, language),
            "quality": self._assess_quality(file_path, language),
        }

        # 缓存结果
        self.analysis_cache[file_path] = result
        return result

    def analyze_directory(self, dir_path: str, extensions: List[str] = None) -> Dict[str, Any]:
        """分析整个目录"""
        if not os.path.exists(dir_path):
            return {"error": f"Directory not found: {dir_path}"}

        if extensions is None:
            extensions = list(self.supported_languages.keys())

        files_analyzed = []
        structure = CodeStructure(file_path=dir_path, language="mixed")

        for root, _, files in os.walk(dir_path):
            # 跳过特定目录
            if any(skip in root for skip in ['node_modules', '.git', '__pycache__', 'venv', '.venv']):
                continue

            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in extensions:
                    file_path = os.path.join(root, file)
                    try:
                        result = self.analyze_file(file_path)
                        if "error" not in result:
                            files_analyzed.append(result)
                            # 收集导入和依赖
                            structure.imports.extend(result["structure"].get("imports", []))
                            structure.dependencies.extend(result["structure"].get("dependencies", []))
                    except Exception as e:
                        print(f"Warning: Failed to analyze {file_path}: {e}")

        return {
            "directory": dir_path,
            "total_files": len(files_analyzed),
            "files": files_analyzed,
            "aggregated_imports": list(set(structure.imports)),
            "unique_dependencies": self._aggregate_dependencies(structure.dependencies),
        }

    def _extract_structure(self, file_path: str, language: str) -> Dict[str, Any]:
        """提取代码结构"""
        structure = {
            "functions": [],
            "classes": [],
            "imports": [],
            "exports": [],
        }

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            if language == 'python':
                structure = self._extract_python_structure(content)
            elif language in ['javascript', 'typescript']:
                structure = self._extract_js_structure(content, language)
            elif language == 'java':
                structure = self._extract_java_structure(content)
            elif language in ['cpp', 'c']:
                structure = self._extract_c_structure(content)
            else:
                # 通用提取
                structure = self._extract_generic_structure(content)

        except Exception as e:
            structure["error"] = str(e)

        return structure

    def _extract_python_structure(self, content: str) -> Dict[str, Any]:
        """提取 Python 代码结构"""
        structure = {"functions": [], "classes": [], "imports": [], "exports": []}

        # 提取导入
        import_pattern = r'^(?:from\s+(\S+)\s+import\s+|import\s+(\S+))'
        for match in re.finditer(import_pattern, content, re.MULTILINE):
            module = match.group(1) or match.group(2)
            if module:
                structure["imports"].append(module)

        # 提取函数定义
        func_pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        for match in re.finditer(func_pattern, content):
            structure["functions"].append({"name": match.group(1), "line": content[:match.start()].count('\n') + 1})

        # 提取类定义
        class_pattern = r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:\([^)]*\))?:'
        for match in re.finditer(class_pattern, content):
            structure["classes"].append({"name": match.group(1), "line": content[:match.start()].count('\n') + 1})

        # 提取导出（__all__）
        all_pattern = r'^__all__\s*=\s*\[(.*?)\]'
        match = re.search(all_pattern, content, re.MULTILINE | re.DOTALL)
        if match:
            exports = re.findall(r'"([^"]+)"', match.group(1))
            structure["exports"] = exports

        return structure

    def _extract_js_structure(self, content: str, language: str) -> Dict[str, Any]:
        """提取 JavaScript/TypeScript 代码结构"""
        structure = {"functions": [], "classes": [], "imports": [], "exports": []}

        # ES6 导入
        import_pattern = r'import\s+(?:{[^}]+}|[\w*]+)\s+from\s+[\'"]([^\'"]+)[\'"]'
        for match in re.finditer(import_pattern, content):
            structure["imports"].append(match.group(1))

        # CommonJS 导入
        cjs_import = r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
        for match in re.finditer(cjs_import, content):
            structure["imports"].append(match.group(1))

        # 函数定义 (function, arrow function, async)
        func_patterns = [
            r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
            r'(?:const|let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>',
            r'(?:const|let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*async\s+function',
        ]
        for pattern in func_patterns:
            for match in re.finditer(pattern, content):
                structure["functions"].append({"name": match.group(1), "line": content[:match.start()].count('\n') + 1})

        # 类定义
        class_pattern = r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:extends\s+\w+)?\s*{'
        for match in re.finditer(class_pattern, content):
            structure["classes"].append({"name": match.group(1), "line": content[:match.start()].count('\n') + 1})

        # 导出
        export_patterns = [
            r'export\s+(?:default\s+)?(?:class|function|const|let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'export\s+{\s*([^}]+)\s*}',
        ]
        for pattern in export_patterns:
            for match in re.finditer(pattern, content):
                name = match.group(1).strip()
                if ',' in name:
                    structure["exports"].extend([n.strip() for n in name.split(',')])
                else:
                    structure["exports"].append(name)

        return structure

    def _extract_java_structure(self, content: str) -> Dict[str, Any]:
        """提取 Java 代码结构"""
        structure = {"functions": [], "classes": [], "imports": [], "exports": []}

        # 导入
        import_pattern = r'import\s+([a-zA-Z0-9_.]+);'
        for match in re.finditer(import_pattern, content):
            structure["imports"].append(match.group(1))

        # 方法定义
        method_pattern = r'(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)'
        for match in re.finditer(method_pattern, content):
            structure["functions"].append({"name": match.group(1), "line": content[:match.start()].count('\n') + 1})

        # 类定义
        class_pattern = r'(?:public\s+)?class\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        for match in re.finditer(class_pattern, content):
            structure["classes"].append({"name": match.group(1), "line": content[:match.start()].count('\n') + 1})

        return structure

    def _extract_c_structure(self, content: str) -> Dict[str, Any]:
        """提取 C/C++ 代码结构"""
        structure = {"functions": [], "classes": [], "imports": [], "exports": []}

        # 头文件包含
        include_pattern = r'#include\s+[<"]([^>"]+)[>"]'
        for match in re.finditer(include_pattern, content):
            structure["imports"].append(match.group(1))

        # 函数定义
        func_pattern = r'(?:void|int|char|float|double|bool|long|short|auto)\s+\*?\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*{'
        for match in re.finditer(func_pattern, content):
            structure["functions"].append({"name": match.group(1), "line": content[:match.start()].count('\n') + 1})

        # 类定义 (C++)
        class_pattern = r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*{'
        for match in re.finditer(class_pattern, content):
            structure["classes"].append({"name": match.group(1), "line": content[:match.start()].count('\n') + 1})

        return structure

    def _extract_generic_structure(self, content: str) -> Dict[str, Any]:
        """通用代码结构提取"""
        structure = {"functions": [], "classes": [], "imports": [], "exports": []}
        lines = content.split('\n')

        # 简单统计
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('def ') or stripped.startswith('function '):
                structure["functions"].append({"name": "unknown", "line": i})
            elif stripped.startswith('class '):
                structure["classes"].append({"name": "unknown", "line": i})

        return structure

    def _assess_quality(self, file_path: str, language: str) -> Dict[str, Any]:
        """评估代码质量"""
        quality = {
            "lines_of_code": 0,
            "comment_lines": 0,
            "blank_lines": 0,
            "complexity": 0,
            "issues": [],
        }

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            lines = content.split('\n')
            quality["lines_of_code"] = len([l for l in lines if l.strip()])
            quality["blank_lines"] = len([l for l in lines if not l.strip()])

            # 注释统计
            if language == 'python':
                quality["comment_lines"] = len([l for l in lines if l.strip().startswith('#')])
            elif language in ['javascript', 'typescript']:
                quality["comment_lines"] = len([l for l in lines if l.strip().startswith('//')])
            else:
                quality["comment_lines"] = len([l for l in lines if l.strip().startswith('//') or l.strip().startswith('/*')])

            # 注释比例
            if quality["lines_of_code"] > 0:
                quality["comment_ratio"] = quality["comment_lines"] / quality["lines_of_code"]

            # 复杂度估算（基于缩进和条件）
            complexity_indicators = ['if', 'elif', 'for', 'while', 'and', 'or', '?', 'switch']
            quality["complexity"] = sum(content.lower().count(i) for i in complexity_indicators)

            # 生成问题列表
            if quality["comment_ratio"] < 0.1 and quality["lines_of_code"] > 50:
                quality["issues"].append("注释不足，建议增加文档注释")

            if quality["complexity"] > 20:
                quality["issues"].append(f"复杂度较高({quality['complexity']})，建议拆分函数")

            if quality["lines_of_code"] > 500:
                quality["issues"].append(f"文件行数过多({quality['lines_of_code']})，建议拆分为多个模块")

            # 计算质量分数
            score = 100
            score -= min(30, quality["complexity"] * 2)  # 复杂度扣分
            score -= 10 if quality["comment_ratio"] < 0.1 else 0  # 注释不足扣分
            score -= 10 if len(quality["issues"]) > 2 else 0  # 问题过多扣分
            quality["score"] = max(0, score)

        except Exception as e:
            quality["error"] = str(e)

        return quality

    def _aggregate_dependencies(self, dependencies: List[Dict]) -> List[str]:
        """聚合依赖关系"""
        unique_deps = {}
        for dep in dependencies:
            if isinstance(dep, dict) and "name" in dep:
                if dep["name"] not in unique_deps:
                    unique_deps[dep["name"]] = dep
        return list(unique_deps.keys())

    def detect_dependencies(self, file_path: str = None, dir_path: str = None) -> Dict[str, Any]:
        """检测代码依赖关系"""
        if file_path:
            analysis = self.analyze_file(file_path)
            if "error" in analysis:
                return analysis

            deps = analysis["structure"].get("imports", [])
            return {"file": file_path, "dependencies": deps, "count": len(deps)}

        elif dir_path:
            analysis = self.analyze_directory(dir_path)
            if "error" in analysis:
                return analysis

            return {
                "directory": dir_path,
                "dependencies": analysis.get("aggregated_imports", []),
                "total_files": analysis.get("total_files", 0),
            }

        return {"error": "Please specify file_path or dir_path"}

    def generate_refactoring_suggestions(self, file_path: str) -> List[Dict[str, Any]]:
        """生成重构建议"""
        if not os.path.exists(file_path):
            return [{"error": f"File not found: {file_path}"}]

        analysis = self.analyze_file(file_path)
        if "error" in analysis:
            return [analysis]

        suggestions = []
        quality = analysis.get("quality", {})
        structure = analysis.get("structure", {})

        # 基于质量问题生成建议
        for issue in quality.get("issues", []):
            if "注释不足" in issue:
                suggestions.append({
                    "file_path": file_path,
                    "issue": "代码注释不足",
                    "suggestion": "为公共函数和类添加文档字符串((docstring)，提高代码可维护性",
                    "priority": "medium",
                    "impact": "maintainability"
                })

            if "复杂度" in issue:
                suggestions.append({
                    "file_path": file_path,
                    "issue": "代码复杂度较高",
                    "suggestion": "将复杂函数拆分为多个小型函数，每个函数只做一件事",
                    "priority": "high",
                    "impact": "readability"
                })

            if "行数过多" in issue:
                suggestions.append({
                    "file_path": file_path,
                    "issue": "文件过大",
                    "suggestion": "将文件拆分为多个模块，使用包(package)组织",
                    "priority": "medium",
                    "impact": "maintainability"
                })

        # 基于结构生成建议
        functions = structure.get("functions", [])
        if len(functions) > 20:
            suggestions.append({
                "file_path": file_path,
                "issue": "函数过多",
                "suggestion": f"检测到 {len(functions)} 个函数，考虑将相关函数组织到不同的模块或类中",
                "priority": "medium",
                "impact": "maintainability"
            })

        # 通用建议
        if quality.get("score", 100) < 70:
            suggestions.append({
                "file_path": file_path,
                "issue": "代码质量待提升",
                "suggestion": "整体代码质量评分较低，建议进行系统性重构",
                "priority": "high",
                "impact": "maintainability"
            })

        return suggestions if suggestions else [{
            "file_path": file_path,
            "issue": "无明显问题",
            "suggestion": "代码质量良好，继续保持",
            "priority": "low",
            "impact": "maintainability"
        }]

    def analyze_codebase(self, path: str, use_llm: bool = False) -> Dict[str, Any]:
        """综合代码库分析"""
        if os.path.isfile(path):
            result = self.analyze_file(path)
            result["suggestions"] = self.generate_refactoring_suggestions(path)
            return result
        elif os.path.isdir(path):
            result = self.analyze_directory(path)
            # 为每个文件生成建议
            for file_result in result.get("files", []):
                file_result["suggestions"] = self.generate_refactoring_suggestions(file_result["file_path"])
            return result
        else:
            return {"error": f"Invalid path: {path}"}


def main():
    """命令行入口"""
    import argparse
    parser = argparse.ArgumentParser(description="智能代码理解与重构引擎")
    parser.add_argument("path", help="要分析的代码文件或目录路径")
    parser.add_argument("--analyze", action="store_true", help="综合分析代码")
    parser.add_argument("--structure", action="store_true", help="提取代码结构")
    parser.add_argument("--quality", action="store_true", help="评估代码质量")
    parser.add_argument("--suggest", action="store_true", help="生成重构建议")
    parser.add_argument("--deps", action="store_true", help="检测依赖关系")
    parser.add_argument("--output", "-o", help="输出文件路径(JSON)")

    args = parser.parse_args()

    engine = CodeUnderstandingEngine()

    if args.analyze:
        result = engine.analyze_codebase(args.path)
    elif args.structure:
        result = engine.analyze_file(args.path)
    elif args.quality:
        result = engine.analyze_file(args.path)
        result = result.get("quality", {})
    elif args.suggest:
        result = {"suggestions": engine.generate_refactoring_suggestions(args.path)}
    elif args.deps:
        result = engine.detect_dependencies(file_path=args.path)
    else:
        result = engine.analyze_file(args.path)

    # 输出结果
    output = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"结果已保存到: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()