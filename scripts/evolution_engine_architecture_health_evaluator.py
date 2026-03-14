"""
智能进化引擎架构健康度评估与自动优化引擎
让系统能够自动评估进化引擎集群的健康状况，识别功能重叠和优化机会，
实现真正的"进化系统自我优化"

功能：
1. 扫描所有 evolution_*.py 模块
2. 分析功能重叠度（相似功能、重复代码）
3. 评估架构健康度（模块独立性、依赖关系）
4. 生成优化建议（合并建议、接口统一建议）
5. 可选自动执行简单优化

集成到 do.py 支持：
- 进化引擎健康评估
- 架构健康度分析
- 引擎优化建议
- 优化执行
"""

import os
import re
import json
import ast
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict
import subprocess

class EvolutionEngineArchitectureHealthEvaluator:
    def __init__(self):
        self.scripts_dir = Path(__file__).parent
        self.evolution_modules = []
        self.analysis_results = {}
        self.health_score = 0.0

    def scan_evolution_modules(self) -> List[Dict]:
        """扫描所有 evolution_*.py 模块"""
        modules = []
        for f in self.scripts_dir.glob("evolution*.py"):
            if f.name.startswith("evolution") and f.suffix == ".py":
                modules.append({
                    "name": f.stem,
                    "path": str(f),
                    "size": f.stat().st_size,
                    "modified": f.stat().st_mtime
                })
        self.evolution_modules = sorted(modules, key=lambda x: x["name"])
        return self.evolution_modules

    def extract_functionality(self, module_path: str) -> Dict:
        """提取模块功能描述"""
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取类名和函数名
            tree = ast.parse(content)
            classes = []
            functions = []
            docstring = ""

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                    if ast.get_docstring(node):
                        docstring = ast.get_docstring(node)
                elif isinstance(node, ast.FunctionDef):
                    functions.append(node.name)

            # 提取关键词用于功能匹配
            keywords = set()
            for word in re.findall(r'\b[a-z]{4,}\b', content.lower()):
                if word in ['function', 'engine', 'module', 'system', 'auto', 'smart',
                           'evolution', 'optimize', 'learn', 'adapt', 'predict', 'execute',
                           'manage', 'coordinate', 'collaborate', 'integrate', 'monitor']:
                    keywords.add(word)

            return {
                "classes": classes,
                "functions": functions,
                "keywords": list(keywords),
                "docstring": docstring[:200] if docstring else ""
            }
        except Exception as e:
            return {"classes": [], "functions": [], "keywords": [], "docstring": "", "error": str(e)}

    def calculate_functionality_overlap(self) -> Dict[Tuple[str, str], float]:
        """计算模块间功能重叠度"""
        module_functions = {}
        for module in self.evolution_modules:
            func_info = self.extract_functionality(module["path"])
            module_functions[module["name"]] = {
                "keywords": set(func_info.get("keywords", [])),
                "functions": set(func_info.get("functions", [])),
                "classes": set(func_info.get("classes", []))
            }

        overlaps = {}
        module_names = list(module_functions.keys())

        for i, mod1 in enumerate(module_names):
            for mod2 in module_names[i+1:]:
                kw_overlap = len(module_functions[mod1]["keywords"] & module_functions[mod2]["keywords"])
                fn_overlap = len(module_functions[mod1]["functions"] & module_functions[mod2]["functions"])

                # 计算综合重叠度
                overlap_score = (kw_overlap * 2 + fn_overlap) / 20
                overlap_score = min(overlap_score, 1.0)

                if overlap_score > 0.3:
                    overlaps[(mod1, mod2)] = overlap_score

        return overlaps

    def analyze_architecture_health(self) -> Dict:
        """分析架构健康度"""
        issues = []
        suggestions = []

        # 检查模块大小差异
        if self.evolution_modules:
            sizes = [m["size"] for m in self.evolution_modules]
            avg_size = sum(sizes) / len(sizes)

            # 识别过大或过小的模块
            for module in self.evolution_modules:
                if module["size"] > avg_size * 3:
                    issues.append(f"模块 {module['name']} 过大 ({module['size']} bytes)，可能承担过多职责")
                elif module["size"] < 500 and module["size"] > 0:
                    issues.append(f"模块 {module['name']} 过小 ({module['size']} bytes)，可能功能过于简单")

        # 检查功能重叠
        overlaps = self.calculate_functionality_overlap()
        if overlaps:
            sorted_overlaps = sorted(overlaps.items(), key=lambda x: x[1], reverse=True)
            for (mod1, mod2), score in sorted_overlaps[:5]:
                suggestions.append(f"模块 {mod1} 与 {mod2} 功能重叠度高 ({score:.1%})，建议合并或重构")

        # 检查命名一致性
        naming_patterns = defaultdict(list)
        for module in self.evolution_modules:
            name = module["name"]
            if "engine" in name:
                naming_patterns["engine"].append(name)
            elif "optimizer" in name:
                naming_patterns["optimizer"].append(name)
            elif "loop" in name:
                naming_patterns["loop"].append(name)
            elif "self" in name:
                naming_patterns["self"].append(name)

        # 架构评分
        health_score = 100.0
        health_score -= len(issues) * 5
        health_score -= len(overlaps) * 3
        health_score = max(health_score, 0)

        return {
            "health_score": health_score,
            "total_modules": len(self.evolution_modules),
            "issues": issues[:10],
            "suggestions": suggestions[:10],
            "overlap_count": len(overlaps),
            "naming_patterns": {k: len(v) for k, v in naming_patterns.items()}
        }

    def generate_optimization_plan(self) -> Dict:
        """生成优化计划"""
        overlaps = self.calculate_functionality_overlap()
        architecture = self.analyze_architecture_health()

        plan = {
            "priority_actions": [],
            "medium_priority": [],
            "low_priority": []
        }

        # 高优先级：处理高重叠度模块
        high_overlaps = [(k, v) for k, v in overlaps.items() if v > 0.5]
        for (mod1, mod2), score in high_overlaps:
            plan["priority_actions"].append({
                "action": "merge_or_refactor",
                "modules": [mod1, mod2],
                "reason": f"功能重叠度 {score:.1%}",
                "suggestion": f"考虑合并 {mod1} 和 {mod2} 或重构以减少重复"
            })

        # 中优先级：处理架构问题
        for issue in architecture["issues"][:5]:
            plan["medium_priority"].append({
                "action": "review",
                "issue": issue,
                "suggestion": "请人工评估此问题"
            })

        # 低优先级：优化建议
        for suggestion in architecture["suggestions"][:5]:
            plan["low_priority"].append({
                "action": "consider",
                "suggestion": suggestion
            })

        return plan

    def run_full_evaluation(self) -> Dict:
        """执行完整评估"""
        # 1. 扫描模块
        self.scan_evolution_modules()

        # 2. 分析功能重叠
        overlaps = self.calculate_functionality_overlap()

        # 3. 分析架构健康度
        architecture = self.analyze_architecture_health()

        # 4. 生成优化计划
        optimization_plan = self.generate_optimization_plan()

        self.analysis_results = {
            "modules_scanned": len(self.evolution_modules),
            "module_list": [m["name"] for m in self.evolution_modules],
            "overlaps": {f"{k[0]} <-> {k[1]}": v for k, v in overlaps.items()},
            "architecture": architecture,
            "optimization_plan": optimization_plan,
            "health_score": architecture["health_score"]
        }

        self.health_score = architecture["health_score"]

        return self.analysis_results

    def get_summary(self) -> str:
        """生成评估摘要"""
        if not self.analysis_results:
            return "请先运行 run_full_evaluation()"

        arch = self.analysis_results["architecture"]
        plan = self.analysis_results["optimization_plan"]

        summary = f"""
=== 进化引擎架构健康度评估报告 ===

📊 总体健康度: {arch['health_score']:.1f}/100
📦 模块总数: {arch['total_modules']}
⚠️ 功能重叠数: {arch['overlap_count']}

🔍 发现的问题:
"""
        for i, issue in enumerate(arch["issues"][:5], 1):
            summary += f"  {i}. {issue}\n"

        summary += "\n💡 优化建议:\n"
        for i, action in enumerate(plan["priority_actions"][:3], 1):
            summary += f"  {i}. [{action['action']}] {action['suggestion']}\n"

        return summary


def main():
    """主函数 - 命令行入口"""
    import argparse
    import io
    import sys as _sys

    # 设置 stdout 编码为 utf-8
    try:
        _sys.stdout = io.TextIOWrapper(_sys.stdout.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="智能进化引擎架构健康度评估")
    parser.add_argument("--eval", action="store_true", help="执行完整评估")
    parser.add_argument("--summary", action="store_true", help="显示评估摘要")
    parser.add_argument("--plan", action="store_true", help="显示优化计划")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")

    args = parser.parse_args()

    evaluator = EvolutionEngineArchitectureHealthEvaluator()

    if args.eval or args.summary or args.plan or args.json:
        results = evaluator.run_full_evaluation()

        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        elif args.summary:
            print(evaluator.get_summary())
        elif args.plan:
            print(json.dumps(results["optimization_plan"], indent=2, ensure_ascii=False))
        else:
            print(evaluator.get_summary())
    else:
        # 默认显示摘要
        results = evaluator.run_full_evaluation()
        print(evaluator.get_summary())


if __name__ == "__main__":
    main()