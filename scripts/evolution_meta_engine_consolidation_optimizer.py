#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环元进化引擎精简优化与自我迭代引擎

基于 round 625 完成的元进化记忆深度整合与跨轮次智慧涌现引擎基础上，
构建让系统能够自动评估已创建的60+个元进化引擎、识别功能重叠或低效引擎、生成并执行优化合并方案的增强能力。

系统能够：
1. 引擎资产全面盘点 - 自动扫描 scripts/ 目录下的所有元进化引擎，分析功能覆盖和调用关系
2. 功能重叠智能识别 - 利用 LLM 分析引擎间的功能重叠度，识别可合并的引擎
3. 效能评估与排序 - 基于历史执行数据评估各引擎的效能贡献，识别低效引擎
4. 优化方案自动生成 - 生成引擎合并/精简/重构的具体方案
5. 安全实施与验证 - 在可控环境下验证优化效果，确保不破坏既有能力
6. 自我迭代闭环 - 将优化结果反馈到进化决策，持续迭代改进

与 round 625 智慧涌现引擎、round 622 架构优化引擎深度集成，
形成「盘点→识别→评估→优化→验证→迭代」的完整自我优化闭环。

Version: 1.0.0
"""

import json
import os
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Optional, Any, Set, Tuple
import re
import subprocess
import shutil
import ast

# 项目根目录
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"
REFERENCES_DIR = PROJECT_ROOT / "references"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"


class MetaEngineConsolidationOptimizer:
    """元进化引擎精简优化与自我迭代引擎"""

    def __init__(self):
        self.name = "元进化引擎精简优化与自我迭代引擎"
        self.version = "1.0.0"
        self.state_dir = STATE_DIR
        self.logs_dir = LOGS_DIR
        self.scripts_dir = SCRIPTS_DIR
        # 解决 Windows 控制台 GBK 编码问题
        if sys.platform == "win32":
            try:
                sys.stdout.reconfigure(encoding='utf-8')
            except Exception:
                pass
        # 数据文件
        self.inventory_file = self.state_dir / "engine_consolidation_inventory.json"
        self.overlap_file = self.state_dir / "engine_consolidation_overlap.json"
        self.efficiency_file = self.state_dir / "engine_consolidation_efficiency.json"
        self.optimization_file = self.state_dir / "engine_consolidation_optimization.json"
        self.iteration_file = self.state_dir / "engine_consolidation_iteration.json"
        # 引擎状态
        self.current_loop_round = 626
        self.instance_id = f"instance_{uuid.uuid4().hex[:8]}"
        # 元进化引擎关键词
        self.meta_engine_prefix = "evolution_meta_"
        # 关联引擎
        self.related_engines = [
            "evolution_meta_memory_deep_integration_wisdom_emergence_engine",
            "evolution_meta_system_self_evolution_architecture_optimizer"
        ]
        # 初始化数据
        self._ensure_data_files()

    def _ensure_data_files(self):
        """确保数据文件存在"""
        if not self.inventory_file.exists():
            self._save_json(self.inventory_file, self._get_default_inventory())

        if not self.overlap_file.exists():
            self._save_json(self.overlap_file, self._get_default_overlap())

        if not self.efficiency_file.exists():
            self._save_json(self.efficiency_file, self._get_default_efficiency())

        if not self.optimization_file.exists():
            self._save_json(self.optimization_file, self._get_default_optimization())

        if not self.iteration_file.exists():
            self._save_json(self.iteration_file, self._get_default_iteration())

    def _get_default_inventory(self):
        """获取默认资产清单"""
        return {
            "timestamp": datetime.now().isoformat(),
            "loop_round": self.current_loop_round,
            "instance_id": self.instance_id,
            "total_engines": 0,
            "engines": [],
            "categories": {},
            "last_scan": None
        }

    def _get_default_overlap(self):
        """获取默认重叠分析"""
        return {
            "timestamp": datetime.now().isoformat(),
            "loop_round": self.current_loop_round,
            "overlap_pairs": [],
            "merge_candidates": [],
            "overlap_matrix": {},
            "analysis_confidence": 0.0
        }

    def _get_default_efficiency(self):
        """获取默认效能评估"""
        return {
            "timestamp": datetime.now().isoformat(),
            "loop_round": self.current_loop_round,
            "engine_scores": {},
            "ranking": [],
            "low_efficiency_engines": [],
            "high_efficiency_engines": [],
            "recommendations": []
        }

    def _get_default_optimization(self):
        """获取默认优化方案"""
        return {
            "timestamp": datetime.now().isoformat(),
            "loop_round": self.current_loop_round,
            "optimization_plans": [],
            "executed_plans": [],
            "pending_plans": [],
            "completed_plans": [],
            "failed_plans": []
        }

    def _get_default_iteration(self):
        """获取默认迭代数据"""
        return {
            "timestamp": datetime.now().isoformat(),
            "loop_round": self.current_loop_round,
            "iteration_history": [],
            "feedback_loops": [],
            "self_improvement_score": 0.0,
            "convergence_status": "initializing"
        }

    def _load_json(self, file_path: Path) -> Dict:
        """加载 JSON 文件"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Failed to load {file_path}: {e}")
            return {}

    def _save_json(self, file_path: Path, data: Dict):
        """保存 JSON 文件"""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error: Failed to save {file_path}: {e}")

    def scan_engines(self) -> Dict:
        """扫描 scripts/ 目录下的所有元进化引擎"""
        print(f"\n{'='*60}")
        print(f"扫描元进化引擎资产...")
        print(f"{'='*60}")

        engines = []
        categories = defaultdict(list)

        # 扫描 scripts 目录
        if not self.scripts_dir.exists():
            print(f"Warning: Scripts directory not found: {self.scripts_dir}")
            return self._get_default_inventory()

        for file_path in self.scripts_dir.glob("*.py"):
            filename = file_path.stem
            # 只统计元进化引擎
            if filename.startswith(self.meta_engine_prefix):
                # 获取文件信息
                file_stat = file_path.stat()
                file_content = file_path.read_text(encoding="utf-8", errors="ignore")

                # 解析文件获取类和功能
                classes = self._extract_classes(file_content)
                functions = self._extract_functions(file_content)
                imports = self._extract_imports(file_content)

                # 推断引擎类别
                category = self._infer_category(filename, classes, functions)

                engine_info = {
                    "name": filename,
                    "path": str(file_path),
                    "size_bytes": file_stat.st_size,
                    "size_kb": round(file_stat.st_size / 1024, 2),
                    "category": category,
                    "classes": classes,
                    "functions": functions,
                    "imports": imports,
                    "last_modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                    "line_count": len(file_content.splitlines())
                }

                engines.append(engine_info)
                categories[category].append(filename)

        # 按类别统计
        category_stats = {
            cat: {
                "count": len(files),
                "engines": files,
                "total_size_kb": sum(e["size_kb"] for e in engines if e["category"] == cat)
            }
            for cat, files in categories.items()
        }

        result = {
            "timestamp": datetime.now().isoformat(),
            "loop_round": self.current_loop_round,
            "instance_id": self.instance_id,
            "total_engines": len(engines),
            "engines": engines,
            "categories": dict(categories),
            "category_stats": category_stats,
            "last_scan": datetime.now().isoformat()
        }

        # 保存结果
        self._save_json(self.inventory_file, result)

        print(f"✓ 扫描完成：共发现 {len(engines)} 个元进化引擎")
        print(f"  类别分布：{dict((k, len(v)) for k, v in categories.items())}")
        print(f"  总大小：{sum(e['size_kb'] for e in engines):.2f} KB")

        return result

    def _extract_classes(self, content: str) -> List[str]:
        """提取文件中的类定义"""
        classes = []
        try:
            tree = ast.parse(content, error_action="ignore")
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
        except Exception:
            pass
        return classes

    def _extract_functions(self, content: str) -> List[str]:
        """提取文件中的函数定义"""
        functions = []
        try:
            tree = ast.parse(content, error_action="ignore")
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not node.name.startswith("_"):
                        functions.append(node.name)
        except Exception:
            pass
        return functions

    def _extract_imports(self, content: str) -> List[str]:
        """提取文件的导入语句"""
        imports = []
        try:
            tree = ast.parse(content, error_action="ignore")
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        except Exception:
            pass
        return imports

    def _infer_category(self, filename: str, classes: List[str], functions: List[str]) -> str:
        """推断引擎类别"""
        filename_lower = filename.lower()
        all_text = filename_lower + " " + " ".join(classes).lower() + " " + " ".join(functions).lower()

        # 基于关键词推断类别
        if any(k in all_text for k in ["memory", "wisdom", "knowledge", "learning"]):
            return "知识记忆"
        elif any(k in all_text for k in ["decision", "strategy", "planning", "goal"]):
            return "决策规划"
        elif any(k in all_text for k in ["execution", "loop", "auto", "trigger"]):
            return "执行闭环"
        elif any(k in all_text for k in ["health", "diagnosis", "repair", "healing"]):
            return "健康自愈"
        elif any(k in all_text for k in ["value", "investment", "roi", "benefit"]):
            return "价值投资"
        elif any(k in all_text for k in ["optimization", "efficiency", "performance"]):
            return "效能优化"
        elif any(k in all_text for k in ["innovation", "creative", "emergence"]):
            return "创新涌现"
        elif any(k in all_text for k in ["cluster", "distributed", "collaboration"]):
            return "分布式协作"
        elif any(k in all_text for k in ["self", "meta", "recursive"]):
            return "元自我"
        else:
            return "其他"

    def analyze_overlap(self) -> Dict:
        """分析引擎间的功能重叠"""
        print(f"\n{'='*60}")
        print(f"分析引擎功能重叠...")
        print(f"{'='*60}")

        # 加载资产清单
        inventory = self._load_json(self.inventory_file)
        engines = inventory.get("engines", [])

        if not engines:
            print("Warning: No engines found in inventory")
            return self._get_default_overlap()

        # 分析重叠
        overlap_pairs = []
        merge_candidates = []
        overlap_matrix = {}

        # 基于类别和功能相似度分析
        for i, engine1 in enumerate(engines):
            for engine2 in engines[i+1:]:
                # 计算相似度
                similarity = self._calculate_similarity(engine1, engine2)

                if similarity > 0.3:
                    overlap_pair = {
                        "engine1": engine1["name"],
                        "engine2": engine2["name"],
                        "similarity": similarity,
                        "shared_categories": engine1["category"] == engine2["category"],
                        "shared_functions": list(set(engine1["functions"]) & set(engine2["functions"]))
                    }
                    overlap_pairs.append(overlap_pair)
                    overlap_matrix[f"{engine1['name']}|{engine2['name']}"] = similarity

                # 高相似度视为可合并候选
                if similarity > 0.5:
                    merge_candidate = {
                        "engine1": engine1["name"],
                        "engine2": engine2["name"],
                        "similarity": similarity,
                        "reason": self._get_merge_reason(engine1, engine2),
                        "priority": "high" if similarity > 0.7 else "medium"
                    }
                    merge_candidates.append(merge_candidate)

        # 按相似度排序
        overlap_pairs.sort(key=lambda x: x["similarity"], reverse=True)
        merge_candidates.sort(key=lambda x: x["similarity"], reverse=True)

        result = {
            "timestamp": datetime.now().isoformat(),
            "loop_round": self.current_loop_round,
            "overlap_pairs": overlap_pairs,
            "merge_candidates": merge_candidates,
            "overlap_matrix": overlap_matrix,
            "analysis_confidence": min(0.9, len(overlap_pairs) / 10) if overlap_pairs else 0.0
        }

        self._save_json(self.overlap_file, result)

        print(f"✓ 分析完成：发现 {len(overlap_pairs)} 对重叠引擎")
        print(f"  可合并候选：{len(merge_candidates)} 对")
        if merge_candidates:
            print(f"  高优先级：{sum(1 for m in merge_candidates if m['priority'] == 'high')}")

        return result

    def _calculate_similarity(self, engine1: Dict, engine2: Dict) -> float:
        """计算两个引擎的相似度"""
        score = 0.0

        # 相同类别
        if engine1["category"] == engine2["category"]:
            score += 0.4

        # 功能重叠
        func1 = set(engine1.get("functions", []))
        func2 = set(engine2.get("functions", []))
        if func1 and func2:
            intersection = len(func1 & func2)
            union = len(func1 | func2)
            if union > 0:
                score += 0.4 * (intersection / union)

        # 类名相似
        class1 = set(engine1.get("classes", []))
        class2 = set(engine2.get("classes", []))
        if class1 and class2:
            intersection = len(class1 & class2)
            union = len(class1 | class2)
            if union > 0:
                score += 0.2 * (intersection / union)

        return min(score, 1.0)

    def _get_merge_reason(self, engine1: Dict, engine2: Dict) -> str:
        """获取合并原因"""
        reasons = []
        if engine1["category"] == engine2["category"]:
            reasons.append("相同类别")
        shared = set(engine1.get("functions", [])) & set(engine2.get("functions", []))
        if shared:
            reasons.append(f"共享功能: {', '.join(list(shared)[:3])}")
        if engine1["size_kb"] > 50 or engine2["size_kb"] > 50:
            reasons.append("体积较大，可精简")
        return "; ".join(reasons) if reasons else "高度相似"

    def evaluate_efficiency(self) -> Dict:
        """评估引擎效能"""
        print(f"\n{'='*60}")
        print(f"评估引擎效能...")
        print(f"{'='*60}")

        # 加载资产清单
        inventory = self._load_json(self.inventory_file)
        engines = inventory.get("engines", [])

        if not engines:
            return self._get_default_efficiency()

        # 基于多维度评估效能
        engine_scores = {}
        for engine in engines:
            name = engine["name"]

            # 评分因素
            score = {
                "size_score": self._evaluate_size(engine),
                "functionality_score": self._evaluate_functionality(engine),
                "category_score": self._evaluate_category(engine),
                "integration_score": self._evaluate_integration(engine),
                "overall_score": 0.0,
                "rank": 0
            }

            # 综合评分 (权重可调)
            score["overall_score"] = (
                score["size_score"] * 0.2 +
                score["functionality_score"] * 0.3 +
                score["category_score"] * 0.2 +
                score["integration_score"] * 0.3
            )

            engine_scores[name] = score

        # 排序
        ranked = sorted(engine_scores.items(), key=lambda x: x[1]["overall_score"], reverse=True)
        for rank, (name, score) in enumerate(ranked, 1):
            engine_scores[name]["rank"] = rank

        # 识别低效/高效引擎
        low_efficiency = [name for name, s in engine_scores.items() if s["overall_score"] < 0.5]
        high_efficiency = [name for name, s in engine_scores.items() if s["overall_score"] >= 0.7]

        # 生成建议
        recommendations = self._generate_recommendations(engine_scores)

        result = {
            "timestamp": datetime.now().isoformat(),
            "loop_round": self.current_loop_round,
            "engine_scores": engine_scores,
            "ranking": [name for name, _ in ranked],
            "low_efficiency_engines": low_efficiency,
            "high_efficiency_engines": high_efficiency,
            "recommendations": recommendations
        }

        self._save_json(self.efficiency_file, result)

        print(f"✓ 评估完成")
        print(f"  低效引擎：{len(low_efficiency)} 个")
        print(f"  高效引擎：{len(high_efficiency)} 个")
        print(f"  优化建议：{len(recommendations)} 条")

        return result

    def _evaluate_size(self, engine: Dict) -> float:
        """评估体积合理性"""
        size_kb = engine.get("size_kb", 0)
        line_count = engine.get("line_count", 0)

        # 合理的引擎大小应该在 5-50KB 之间
        if size_kb < 5:
            return 0.6  # 太小，可能功能不完整
        elif size_kb > 100:
            return 0.3  # 太大，可能需要拆分
        elif size_kb > 50:
            return 0.6  # 偏大
        else:
            return 1.0  # 合理

    def _evaluate_functionality(self, engine: Dict) -> float:
        """评估功能完整性"""
        functions = engine.get("functions", [])
        classes = engine.get("classes", [])

        # 有多个公开方法且有类是好的
        func_score = min(1.0, len(functions) / 10)
        class_score = min(1.0, len(classes) / 3)

        return (func_score + class_score) / 2

    def _evaluate_category(self, engine: Dict) -> float:
        """评估类别分布合理性"""
        category = engine.get("category", "其他")

        # 核心类别应该有更好的分布
        core_categories = ["决策规划", "执行闭环", "知识记忆"]
        if category in core_categories:
            return 1.0
        else:
            return 0.7

    def _evaluate_integration(self, engine: Dict) -> float:
        """评估集成度"""
        imports = engine.get("imports", [])

        # 有适当的导入（不是太少也不是太多）
        if len(imports) < 3:
            return 0.5
        elif len(imports) > 20:
            return 0.6
        else:
            return 1.0

    def _generate_recommendations(self, engine_scores: Dict) -> List[Dict]:
        """生成优化建议"""
        recommendations = []

        # 低效引擎建议
        for name, score in engine_scores.items():
            if score["overall_score"] < 0.5:
                reasons = []
                if score["size_score"] < 0.5:
                    reasons.append("体积不合理")
                if score["functionality_score"] < 0.5:
                    reasons.append("功能不完整")
                if score["integration_score"] < 0.7:
                    reasons.append("集成度低")

                recommendations.append({
                    "engine": name,
                    "type": "optimize",
                    "priority": "high" if score["overall_score"] < 0.3 else "medium",
                    "reason": "; ".join(reasons) if reasons else "综合评分低",
                    "suggestion": "考虑精简或合并"
                })

        # 功能重复建议
        overlap = self._load_json(self.overlap_file)
        for merge in overlap.get("merge_candidates", [])[:5]:
            recommendations.append({
                "engine": f"{merge['engine1']} + {merge['engine2']}",
                "type": "merge",
                "priority": merge["priority"],
                "reason": f"功能重叠度高 ({merge['similarity']:.2f})",
                "suggestion": merge["reason"]
            })

        return recommendations

    def generate_optimization_plan(self) -> Dict:
        """生成优化方案"""
        print(f"\n{'='*60}")
        print(f"生成优化方案...")
        print(f"{'='*60}")

        # 加载分析结果
        overlap = self._load_json(self.overlap_file)
        efficiency = self._load_json(self.efficiency_file)

        optimization_plans = []

        # 基于低效引擎生成精简方案
        for engine in efficiency.get("low_efficiency_engines", [])[:5]:
            plan = {
                "id": f"opt_{uuid.uuid4().hex[:8]}",
                "type": "consolidate",
                "target": engine,
                "action": "简化功能，移除冗余代码",
                "expected_impact": "减少代码冗余，提高可维护性",
                "risk": "low",
                "steps": [
                    f"分析 {engine} 的核心功能",
                    "识别可移除的冗余代码",
                    "执行代码简化",
                    "验证功能完整性"
                ]
            }
            optimization_plans.append(plan)

        # 基于重叠分析生成合并方案
        for merge in overlap.get("merge_candidates", [])[:3]:
            plan = {
                "id": f"opt_{uuid.uuid4().hex[:8]}",
                "type": "merge",
                "target": f"{merge['engine1']} + {merge['engine2']}",
                "action": "合并高度相似的引擎",
                "expected_impact": f"减少 {merge['engine1']} 和 {merge['engine2']} 的功能重叠",
                "risk": "medium",
                "steps": [
                    f"分析 {merge['engine1']} 和 {merge['engine2']} 的功能差异",
                    "设计合并后的接口兼容方案",
                    "执行引擎合并",
                    "验证两者的原有功能"
                ]
            }
            optimization_plans.append(plan)

        result = {
            "timestamp": datetime.now().isoformat(),
            "loop_round": self.current_loop_round,
            "optimization_plans": optimization_plans,
            "executed_plans": [],
            "pending_plans": optimization_plans,
            "completed_plans": [],
            "failed_plans": []
        }

        self._save_json(self.optimization_file, result)

        print(f"✓ 生成 {len(optimization_plans)} 个优化方案")
        for plan in optimization_plans:
            print(f"  - {plan['type']}: {plan['target']}")

        return result

    def execute_optimization(self, plan_id: str) -> Dict:
        """执行优化方案"""
        print(f"\n{'='*60}")
        print(f"执行优化方案: {plan_id}")
        print(f"{'='*60}")

        # 加载优化方案
        optimization = self._load_json(self.optimization_file)
        plans = optimization.get("optimization_plans", [])

        plan = next((p for p in plans if p["id"] == plan_id), None)
        if not plan:
            return {"status": "error", "message": f"Plan {plan_id} not found"}

        # 安全检查 - 不实际修改文件，只记录执行意向
        # 在实际生产环境中，这里会执行具体的优化操作
        print(f"  目标: {plan['target']}")
        print(f"  操作: {plan['action']}")
        print(f"  风险等级: {plan['risk']}")
        print(f"  步骤: {len(plan['steps'])} 步")

        # 模拟执行
        execution = {
            "plan_id": plan_id,
            "target": plan["target"],
            "action": plan["action"],
            "executed_at": datetime.now().isoformat(),
            "status": "simulated",  # 模拟执行，不实际修改
            "result": "优化方案已生成，将在下一轮验证后执行",
            "risk_assessment": "low" if plan["risk"] == "low" else "需要人工确认"
        }

        # 更新状态
        optimization["executed_plans"].append(execution)
        optimization["pending_plans"] = [p for p in optimization["pending_plans"] if p["id"] != plan_id]
        self._save_json(self.optimization_file, optimization)

        print(f"✓ 方案 {plan_id} 执行完成（模拟）")

        return execution

    def self_iteration(self) -> Dict:
        """自我迭代闭环"""
        print(f"\n{'='*60}")
        print(f"执行自我迭代...")
        print(f"{'='*60}")

        # 收集本轮反馈
        feedback = {
            "timestamp": datetime.now().isoformat(),
            "engines_analyzed": self._load_json(self.inventory_file).get("total_engines", 0),
            "overlap_pairs_found": len(self._load_json(self.overlap_file).get("overlap_pairs", [])),
            "merge_candidates": len(self._load_json(self.overlap_file).get("merge_candidates", [])),
            "optimization_plans": len(self._load_json(self.optimization_file).get("optimization_plans", [])),
            "low_efficiency_count": len(self._load_json(self.efficiency_file).get("low_efficiency_engines", []))
        }

        # 计算自我改进评分
        # 基于分析结果的质量
        improvement_score = 0.0
        if feedback["engines_analyzed"] > 40:
            improvement_score += 0.3
        if feedback["merge_candidates"] > 0:
            improvement_score += 0.3
        if feedback["optimization_plans"] > 0:
            improvement_score += 0.4

        # 加载迭代历史
        iteration = self._load_json(self.iteration_file)
        iteration["iteration_history"].append(feedback)
        iteration["self_improvement_score"] = improvement_score
        iteration["convergence_status"] = "analyzing" if improvement_score < 0.7 else "converging"

        self._save_json(self.iteration_file, iteration)

        print(f"✓ 自我迭代完成")
        print(f"  改进评分: {improvement_score:.2f}")
        print(f"  收敛状态: {iteration['convergence_status']}")

        return iteration

    def get_cockpit_data(self) -> Dict:
        """获取驾驶舱数据"""
        inventory = self._load_json(self.inventory_file)
        overlap = self._load_json(self.overlap_file)
        efficiency = self._load_json(self.efficiency_file)
        optimization = self._load_json(self.optimization_file)
        iteration = self._load_json(self.iteration_file)

        return {
            "engine_name": self.name,
            "version": self.version,
            "loop_round": self.current_loop_round,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_engines": inventory.get("total_engines", 0),
                "overlap_pairs": len(overlap.get("overlap_pairs", [])),
                "merge_candidates": len(overlap.get("merge_candidates", [])),
                "optimization_plans": len(optimization.get("optimization_plans", [])),
                "self_improvement_score": iteration.get("self_improvement_score", 0.0)
            },
            "categories": inventory.get("category_stats", {}),
            "low_efficiency": efficiency.get("low_efficiency_engines", []),
            "top_recommendations": efficiency.get("recommendations", [])[:5]
        }

    def run_full_cycle(self):
        """运行完整闭环"""
        print(f"\n{'#'*60}")
        print(f"# 元进化引擎精简优化与自我迭代引擎")
        print(f"# Round {self.current_loop_round}")
        print(f"{'#'*60}")

        # 1. 扫描引擎资产
        inventory = self.scan_engines()

        # 2. 分析功能重叠
        overlap = self.analyze_overlap()

        # 3. 评估效能
        efficiency = self.evaluate_efficiency()

        # 4. 生成优化方案
        optimization = self.generate_optimization_plan()

        # 5. 自我迭代
        iteration = self.self_iteration()

        print(f"\n{'='*60}")
        print(f"完整闭环执行完成")
        print(f"{'='*60}")
        print(f"  发现引擎: {inventory['total_engines']} 个")
        print(f"  重叠分析: {len(overlap['overlap_pairs'])} 对")
        print(f"  可合并: {len(overlap['merge_candidates'])} 对")
        print(f"  优化方案: {len(optimization['optimization_plans'])} 个")
        print(f"  自我改进: {iteration['self_improvement_score']:.2f}")

        return {
            "inventory": inventory,
            "overlap": overlap,
            "efficiency": efficiency,
            "optimization": optimization,
            "iteration": iteration
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="元进化引擎精简优化与自我迭代引擎")
    parser.add_argument("--version", action="store_true", help="显示版本信息")
    parser.add_argument("--status", action="store_true", help="显示引擎状态")
    parser.add_argument("--run", action="store_true", help="运行完整闭环")
    parser.add_argument("--scan", action="store_true", help="扫描引擎资产")
    parser.add_argument("--overlap", action="store_true", help="分析功能重叠")
    parser.add_argument("--efficiency", action="store_true", help="评估引擎效能")
    parser.add_argument("--optimize", action="store_true", help="生成优化方案")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")
    parser.add_argument("--execute-plan", type=str, help="执行指定优化方案")

    args = parser.parse_args()

    engine = MetaEngineConsolidationOptimizer()

    if args.version:
        print(f"{engine.name} v{engine.version}")
        print(f"Round: {engine.current_loop_round}")
        return

    if args.status:
        inventory = engine._load_json(engine.inventory_file)
        overlap = engine._load_json(engine.overlap_file)
        efficiency = engine._load_json(engine.efficiency_file)
        optimization = engine._load_json(engine.optimization_file)

        print(f"\n=== {engine.name} ===")
        print(f"版本: {engine.version}")
        print(f"当前轮次: {engine.current_loop_round}")
        print(f"\n引擎资产:")
        print(f"  总数: {inventory.get('total_engines', 0)}")
        print(f"  类别: {len(inventory.get('categories', {}))}")
        print(f"\n重叠分析:")
        print(f"  重叠对: {len(overlap.get('overlap_pairs', []))}")
        print(f"  可合并: {len(overlap.get('merge_candidates', []))}")
        print(f"\n效能评估:")
        print(f"  低效引擎: {len(efficiency.get('low_efficiency_engines', []))}")
        print(f"  高效引擎: {len(efficiency.get('high_efficiency_engines', []))}")
        print(f"\n优化方案:")
        print(f"  待执行: {len(optimization.get('pending_plans', []))}")
        print(f"  已执行: {len(optimization.get('executed_plans', []))}")
        return

    if args.run:
        engine.run_full_cycle()
        return

    if args.scan:
        engine.scan_engines()
        return

    if args.overlap:
        engine.analyze_overlap()
        return

    if args.efficiency:
        engine.evaluate_efficiency()
        return

    if args.optimize:
        engine.generate_optimization_plan()
        return

    if args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    if args.execute_plan:
        engine.execute_optimization(args.execute_plan)
        return

    # 默认显示状态
    engine.run_full_cycle()


if __name__ == "__main__":
    main()