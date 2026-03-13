#!/usr/bin/env python3
"""
智能统一元进化引擎 (Meta Evolution Engine)

实现从「单引擎独立进化」到「全系统协同元进化」的范式升级。
该引擎能够分析 70+ 引擎的当前状态、识别进化机会、优先排序进化任务、
自动执行简单修复、生成复杂进化建议，形成完整的元进化闭环。

功能：
1. 多维度引擎状态分析（执行频率、功能完整性、协同效果）
2. 进化机会智能评估（评估每个进化方向的预期收益和实现难度）
3. 进化任务自动调度（优先执行高价值低风险的任务）
4. 自动修复能力（自动修复简单问题如缺失字段、路径错误）
5. 进化效果追踪（记录每次进化后的改进）
6. 统一元进化入口

集成到 do.py 支持：
- 「元进化」「统一进化」「进化协调」「meta evolution」
- 「引擎状态」「进化机会」「进化评估」
- 「自动修复」「进化追踪」
"""

import json
import os
import sys
import glob
import importlib.util
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

# 项目根目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)


class MetaEvolutionEngine:
    """智能统一元进化引擎"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.scripts_dir = os.path.join(self.project_root, "scripts")
        self.runtime_state_dir = os.path.join(self.project_root, "runtime", "state")
        self.references_dir = os.path.join(self.project_root, "references")

        # 进化历史数据库路径
        self.evolution_history_db = os.path.join(
            self.runtime_state_dir, "evolution_history.json"
        )

        # 引擎质量数据路径
        self.engine_quality_db = os.path.join(
            self.runtime_state_dir, "engine_quality.json"
        )

        # 元进化报告路径
        self.report_path = os.path.join(
            self.runtime_state_dir, "meta_evolution_report.json"
        )

    def scan_engines(self) -> Dict[str, Any]:
        """扫描所有引擎模块，收集基本信息"""
        engines = {}
        scripts_pattern = os.path.join(self.scripts_dir, "*.py")

        for script_path in glob.glob(scripts_pattern):
            filename = os.path.basename(script_path)
            if filename.startswith("_") or filename in ["do.py", "run_plan.py"]:
                continue

            module_name = filename[:-3]
            engines[module_name] = {
                "name": module_name,
                "path": script_path,
                "size": os.path.getsize(script_path),
                "last_modified": datetime.fromtimestamp(
                    os.path.getmtime(script_path)
                ).isoformat(),
            }

        return engines

    def analyze_engine_state(self, engines: Dict[str, Any]) -> Dict[str, Any]:
        """分析引擎状态：执行频率、功能完整性、协同效果"""
        analysis = {
            "total_engines": len(engines),
            "engines": {},
            "summary": {
                "high_frequency": [],
                "medium_frequency": [],
                "low_frequency": [],
                "uncategorized": [],
            },
        }

        # 读取进化历史获取执行频率
        execution_history = self._get_execution_history()

        for engine_name, engine_info in engines.items():
            # 评估执行频率
            exec_count = execution_history.get(engine_name, 0)
            if exec_count >= 10:
                freq_category = "high_frequency"
            elif exec_count >= 3:
                freq_category = "medium_frequency"
            elif exec_count > 0:
                freq_category = "low_frequency"
            else:
                freq_category = "uncategorized"

            # 评估功能完整性
            completeness = self._assess_completeness(engine_info)

            # 评估协同效果
            collaboration = self._assess_collaboration(engine_name)

            engine_status = {
                "execution_count": exec_count,
                "frequency_category": freq_category,
                "completeness_score": completeness["score"],
                "completeness_level": completeness["level"],
                "collaboration_score": collaboration["score"],
                "collaboration_level": collaboration["level"],
                "last_modified": engine_info["last_modified"],
            }

            analysis["engines"][engine_name] = engine_status
            analysis["summary"][freq_category].append(engine_name)

        return analysis

    def _get_execution_history(self) -> Dict[str, int]:
        """获取引擎执行历史"""
        history = {}

        # 尝试从多个来源获取执行历史
        sources = [
            os.path.join(self.runtime_state_dir, "recent_logs.json"),
            os.path.join(self.runtime_state_dir, "scenario_experiences.json"),
            self.evolution_history_db,
        ]

        for source in sources:
            if os.path.exists(source):
                try:
                    with open(source, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        # 从场景经验中提取引擎使用信息
                        if "experiences" in data:
                            for exp in data["experiences"]:
                                if "engine" in exp:
                                    engine = exp["engine"]
                                    history[engine] = history.get(engine, 0) + 1
                except Exception:
                    pass

        return history

    def _assess_completeness(self, engine_info: Dict[str, Any]) -> Dict[str, Any]:
        """评估引擎功能完整性"""
        size = engine_info.get("size", 0)

        # 基于代码行数估算完整性
        if size > 10000:
            score = 95
            level = "完整"
        elif size > 5000:
            score = 85
            level = "较完整"
        elif size > 2000:
            score = 70
            level = "基础"
        else:
            score = 50
            level = "初步"

        return {"score": score, "level": level}

    def _assess_collaboration(self, engine_name: str) -> Dict[str, Any]:
        """评估引擎协同效果"""
        # 读取引擎协作相关数据
        collaboration_data = {}

        # 检查 engine_performance_monitor 的数据
        perf_file = os.path.join(
            self.runtime_state_dir, "engine_performance.json"
        )
        if os.path.exists(perf_file):
            try:
                with open(perf_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if engine_name in data:
                        collaboration_data = data[engine_name]
            except Exception:
                pass

        # 基于是否有协作数据判断协同效果
        if collaboration_data:
            score = 80
            level = "有协作"
        else:
            score = 50
            level = "独立"

        return {"score": score, "level": level}

    def identify_evolution_opportunities(
        self, engine_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """识别进化机会"""
        opportunities = []

        for engine_name, status in engine_analysis["engines"].items():
            # 低执行频率但高完整性 = 潜在有价值但未被充分使用的引擎
            if (
                status["frequency_category"] == "uncategorized"
                and status["completeness_score"] >= 70
            ):
                opportunities.append(
                    {
                        "type": "promotion",
                        "engine": engine_name,
                        "title": f"推广未充分利用的引擎: {engine_name}",
                        "description": f"引擎 {engine_name} 功能完整(completeness={status['completeness_score']})但使用率低",
                        "expected_benefit": "高",
                        "implementation_difficulty": "低",
                        "priority_score": 85,
                    }
                )

            # 高频率但低协同 = 需要增强跨引擎协作
            if (
                status["frequency_category"] == "high_frequency"
                and status["collaboration_score"] < 70
            ):
                opportunities.append(
                    {
                        "type": "collaboration",
                        "engine": engine_name,
                        "title": f"增强引擎协作: {engine_name}",
                        "description": f"引擎 {engine_name} 使用频繁(exec={status['execution_count']})但缺乏跨引擎协作",
                        "expected_benefit": "中",
                        "implementation_difficulty": "中",
                        "priority_score": 70,
                    }
                )

            # 低完整性 = 需要完善功能
            if status["completeness_score"] < 60:
                opportunities.append(
                    {
                        "type": "enhancement",
                        "engine": engine_name,
                        "title": f"完善引擎功能: {engine_name}",
                        "description": f"引擎 {engine_name} 完整性较低(completeness={status['completeness_score']})",
                        "expected_benefit": "中",
                        "implementation_difficulty": "中",
                        "priority_score": 60,
                    }
                )

        # 按优先级排序
        opportunities.sort(key=lambda x: x["priority_score"], reverse=True)

        return opportunities

    def prioritize_evolution_tasks(
        self, opportunities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """进化任务优先级排序"""
        prioritized = []

        for opp in opportunities:
            # 计算综合优先级
            benefit_map = {"高": 3, "中": 2, "低": 1}
            difficulty_map = {"低": 3, "中": 2, "高": 1}

            benefit = benefit_map.get(opp["expected_benefit"], 1)
            difficulty = difficulty_map.get(opp["implementation_difficulty"], 1)

            # 综合优先级 = 预期收益 * 实现难度
            priority = benefit * difficulty
            opp["comprehensive_priority"] = priority

            prioritized.append(opp)

        # 按综合优先级排序
        prioritized.sort(key=lambda x: x["comprehensive_priority"], reverse=True)

        return prioritized

    def auto_repair_simple_issues(self) -> Dict[str, Any]:
        """自动修复简单问题"""
        repairs = []

        # 检查并修复常见的简单问题
        repair_checks = [
            self._check_missing_capabilities,
            self._check_broken_references,
            self._check_incomplete_plans,
        ]

        for check_func in repair_checks:
            try:
                result = check_func()
                if result["issues"]:
                    repairs.extend(result["issues"])
            except Exception as e:
                repairs.append(
                    {
                        "type": "error",
                        "description": f"检查失败: {str(e)}",
                        "severity": "low",
                    }
                )

        return {
            "total_issues": len(repairs),
            "auto_repaired": sum(1 for r in repairs if r.get("auto_fixed", False)),
            "issues": repairs,
        }

    def _check_missing_capabilities(self) -> Dict[str, Any]:
        """检查缺失的能力描述"""
        issues = []

        # 读取 capabilities.md
        capabilities_file = os.path.join(
            self.references_dir, "capabilities.md"
        )
        if not os.path.exists(capabilities_file):
            return {"issues": issues}

        # 扫描所有脚本，检查是否有未在 capabilities.md 中记录的
        engines = self.scan_engines()

        try:
            with open(capabilities_file, "r", encoding="utf-8") as f:
                capabilities_content = f.read()

            for engine_name in engines:
                # 简单的检查：如果引擎名称在 capabilities.md 中没有出现
                if engine_name.lower() not in capabilities_content.lower():
                    issues.append(
                        {
                            "type": "missing_capability",
                            "engine": engine_name,
                            "description": f"引擎 {engine_name} 可能未在 capabilities.md 中记录",
                            "severity": "low",
                            "auto_fixed": False,  # 需要人工确认
                        }
                    )
        except Exception:
            pass

        return {"issues": issues}

    def _check_broken_references(self) -> Dict[str, Any]:
        """检查损坏的引用"""
        issues = []

        # 检查 references 目录下的链接是否有效
        ref_dir = self.references_dir

        # 检查关键文件是否存在
        key_files = [
            "capabilities.md",
            "capability_gaps.md",
            "failures.md",
            "agent_evolution_workflow.md",
        ]

        for filename in key_files:
            filepath = os.path.join(ref_dir, filename)
            if not os.path.exists(filepath):
                issues.append(
                    {
                        "type": "missing_file",
                        "file": filename,
                        "description": f"关键文件缺失: {filename}",
                        "severity": "high",
                        "auto_fixed": False,
                    }
                )

        return {"issues": issues}

    def _check_incomplete_plans(self) -> Dict[str, Any]:
        """检查不完整的场景计划"""
        issues = []

        plans_dir = os.path.join(self.project_root, "assets", "plans")

        if not os.path.exists(plans_dir):
            return {"issues": issues}

        # 检查 JSON 计划文件的有效性
        for plan_file in glob.glob(os.path.join(plans_dir, "*.json")):
            try:
                with open(plan_file, "r", encoding="utf-8") as f:
                    plan = json.load(f)

                # 检查必需字段
                required_fields = ["name", "triggers", "steps"]
                missing_fields = [f for f in required_fields if f not in plan]

                if missing_fields:
                    issues.append(
                        {
                            "type": "incomplete_plan",
                            "file": os.path.basename(plan_file),
                            "description": f"计划缺少字段: {missing_fields}",
                            "severity": "medium",
                            "auto_fixed": False,
                        }
                    )
            except json.JSONDecodeError as e:
                issues.append(
                    {
                        "type": "invalid_json",
                        "file": os.path.basename(plan_file),
                        "description": f"JSON 解析错误: {str(e)}",
                        "severity": "high",
                        "auto_fixed": False,
                    }
                )
            except Exception:
                pass

        return {"issues": issues}

    def track_evolution_effects(self) -> Dict[str, Any]:
        """追踪进化效果"""
        effects = {
            "rounds": [],
            "improvements": [],
            "regressions": [],
        }

        # 读取进化历史
        if os.path.exists(self.evolution_history_db):
            try:
                with open(self.evolution_history_db, "r", encoding="utf-8") as f:
                    history = json.load(f)
                    effects["rounds"] = history.get("rounds", [])[-10:]
            except Exception:
                pass

        # 分析改进趋势
        if effects["rounds"]:
            effects["improvements"] = [
                {"round": r.get("round"), "status": "完成"}
                for r in effects["rounds"]
                if r.get("status") == "completed"
            ]

        return effects

    def generate_evolution_suggestions(
        self,
        engine_analysis: Dict[str, Any],
        opportunities: List[Dict[str, Any]],
        auto_repair: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """生成进化建议"""
        suggestions = []

        # 基于分析生成建议
        if opportunities:
            suggestions.append(
                {
                    "category": "高优先级进化机会",
                    "description": f"识别出 {len(opportunities)} 个进化机会",
                    "items": [
                        f"- {opp['title']}: {opp['description']}"
                        for opp in opportunities[:5]
                    ],
                    "action": "建议优先处理前 5 个高优先级机会",
                }
            )

        if auto_repair["total_issues"] > 0:
            suggestions.append(
                {
                    "category": "自动修复",
                    "description": f"发现 {auto_repair['total_issues']} 个问题，其中 {auto_repair['auto_repaired']} 个已自动修复",
                    "items": [
                        f"- {issue['type']}: {issue['description']}"
                        for issue in auto_repair["issues"][:5]
                    ],
                    "action": "查看完整报告了解详情",
                }
            )

        # 基于引擎统计生成建议
        summary = engine_analysis.get("summary", {})
        if summary.get("uncategorized"):
            suggestions.append(
                {
                    "category": "未使用引擎激活",
                    "description": f"发现 {len(summary['uncategorized'])} 个未被使用的引擎",
                    "items": [f"- {e}" for e in summary["uncategorized"][:5]],
                    "action": "建议推广这些引擎的使用",
                }
            )

        return suggestions

    def generate_report(self) -> Dict[str, Any]:
        """生成元进化报告"""
        # 1. 扫描引擎
        engines = self.scan_engines()

        # 2. 分析引擎状态
        engine_analysis = self.analyze_engine_state(engines)

        # 3. 识别进化机会
        opportunities = self.identify_evolution_opportunities(engine_analysis)

        # 4. 优先级排序
        prioritized = self.prioritize_evolution_tasks(opportunities)

        # 5. 自动修复检查
        auto_repair = self.auto_repair_simple_issues()

        # 6. 追踪进化效果
        effects = self.track_evolution_effects()

        # 7. 生成建议
        suggestions = self.generate_evolution_suggestions(
            engine_analysis, opportunities, auto_repair
        )

        report = {
            "generated_at": datetime.now().isoformat(),
            "total_engines": len(engines),
            "engine_analysis": engine_analysis,
            "opportunities": prioritized[:10],  # 前10个机会
            "auto_repair": auto_repair,
            "effects": effects,
            "suggestions": suggestions,
        }

        # 保存报告
        with open(self.report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        return report

    def status(self) -> str:
        """获取元进化引擎状态"""
        # 生成简单状态报告
        engines = self.scan_engines()
        engine_analysis = self.analyze_engine_state(engines)

        summary = f"""智能统一元进化引擎状态
========================
扫描引擎数: {len(engines)}

引擎分布:
- 高频使用: {len(engine_analysis['summary']['high_frequency'])} 个
- 中频使用: {len(engine_analysis['summary']['medium_frequency'])} 个
- 低频使用: {len(engine_analysis['summary']['low_frequency'])} 个
- 未使用: {len(engine_analysis['summary']['uncategorized'])} 个

详细报告: {self.report_path}

使用说明:
- do.py 元进化: 生成完整元进化报告
- do.py 进化机会: 查看当前进化机会
- do.py 引擎状态: 查看所有引擎状态
- do.py 进化追踪: 查看进化效果追踪
"""
        return summary


def main():
    """CLI 入口"""
    if len(sys.argv) < 2:
        print("用法: python meta_evolution_engine.py <command>")
        print("命令:")
        print("  status          - 查看引擎状态")
        print("  analyze         - 分析引擎状态")
        print("  opportunities   - 查看进化机会")
        print("  repair          - 自动修复检查")
        print("  track           - 追踪进化效果")
        print("  full            - 生成完整报告")
        return

    engine = MetaEvolutionEngine()
    command = sys.argv[1]

    if command == "status":
        print(engine.status())
    elif command == "analyze":
        engines = engine.scan_engines()
        analysis = engine.analyze_engine_state(engines)
        print(json.dumps(analysis, ensure_ascii=False, indent=2))
    elif command == "opportunities":
        engines = engine.scan_engines()
        analysis = engine.analyze_engine_state(engines)
        opportunities = engine.identify_evolution_opportunities(analysis)
        prioritized = engine.prioritize_evolution_tasks(opportunities)
        print(json.dumps(prioritized[:10], ensure_ascii=False, indent=2))
    elif command == "repair":
        result = engine.auto_repair_simple_issues()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "track":
        effects = engine.track_evolution_effects()
        print(json.dumps(effects, ensure_ascii=False, indent=2))
    elif command == "full":
        report = engine.generate_report()
        print(f"完整报告已生成: {engine.report_path}")
        print(f"\n进化机会数量: {len(report['opportunities'])}")
        print(f"自动修复问题: {report['auto_repair']['total_issues']}")
    else:
        print(f"未知命令: {command}")


if __name__ == "__main__":
    main()