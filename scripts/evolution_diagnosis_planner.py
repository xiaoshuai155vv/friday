#!/usr/bin/env python3
"""
智能全场景自进化诊断与规划引擎

基于统一质量保障系统数据，自动诊断系统健康状态、识别进化机会、规划进化路径，
形成"诊断→规划→执行→验证→优化"的完整自进化闭环。

功能：
1. 系统健康诊断 - 分析引擎质量、场景计划质量、守护进程状态
2. 进化机会识别 - 基于诊断结果识别可优化点
3. 进化路径规划 - 生成具体的进化建议和执行计划
4. 诊断报告生成 - 输出详细的诊断结果和规划建议
5. 自动执行支持 - 可选自动执行低风险的优化操作

用法：
    python evolution_diagnosis_planner.py [command] [options]

命令：
    diagnose    - 执行系统健康诊断
    plan        - 生成进化规划建议
    opportunities - 列出识别到的进化机会
    report      - 生成完整诊断报告
    auto        - 自动执行低风险优化（需确认）
    status      - 查看诊断引擎状态
"""

import json
import os
import sys
import glob
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE = PROJECT_ROOT / "runtime" / "state"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# 质量保障报告路径
QUALITY_REPORT = RUNTIME_STATE / "unified_quality_loop_report.json"
ENGINE_QUALITY = RUNTIME_STATE / "auto_quality_assurance_results.json"
SCENE_TEST = RUNTIME_STATE / "scene_test_report.json"
PLAN_OPTIMIZER = RUNTIME_STATE / "scenario_plan_optimizer_report.json"
AUTO_REPAIR = RUNTIME_STATE / "scene_plan_auto_repair_report.json"

# 进化历史路径
EVOLUTION_HISTORY = RUNTIME_STATE / "evolution_completed_*.json"


class EvolutionDiagnosisPlanner:
    """智能全场景自进化诊断与规划引擎"""

    def __init__(self):
        self.diagnosis_data = {}
        self.opportunities = []
        self.plans = []
        self.report = {}

    def load_quality_data(self) -> Dict[str, Any]:
        """加载质量保障数据"""
        data = {
            "engines": {},
            "scenes": {},
            "daemons": {},
            "overall": {}
        }

        # 加载统一质量报告
        if QUALITY_REPORT.exists():
            try:
                with open(QUALITY_REPORT, "r", encoding="utf-8") as f:
                    data["overall"] = json.load(f)
            except Exception as e:
                print(f"警告：加载统一质量报告失败: {e}")

        # 加载引擎质量数据
        if ENGINE_QUALITY.exists():
            try:
                with open(ENGINE_QUALITY, "r", encoding="utf-8") as f:
                    data["engines"] = json.load(f)
            except Exception as e:
                print(f"警告：加载引擎质量数据失败: {e}")

        # 加载场景测试数据
        if SCENE_TEST.exists():
            try:
                with open(SCENE_TEST, "r", encoding="utf-8") as f:
                    data["scenes"] = json.load(f)
            except Exception as e:
                print(f"警告：加载场景测试数据失败: {e}")

        # 加载场景计划优化数据
        if PLAN_OPTIMIZER.exists():
            try:
                with open(PLAN_OPTIMIZER, "r", encoding="utf-8") as f:
                    data["scenes"]["optimizer"] = json.load(f)
            except Exception as e:
                print(f"警告：加载场景计划优化数据失败: {e}")

        # 加载自动修复数据
        if AUTO_REPAIR.exists():
            try:
                with open(AUTO_REPAIR, "r", encoding="utf-8") as f:
                    data["scenes"]["repair"] = json.load(f)
            except Exception as e:
                print(f"警告：加载自动修复数据失败: {e}")

        return data

    def diagnose_system_health(self) -> Dict[str, Any]:
        """诊断系统整体健康状态"""
        quality_data = self.load_quality_data()

        diagnosis = {
            "timestamp": datetime.now().isoformat(),
            "overall_score": 0,
            "engine_health": {},
            "scene_health": {},
            "daemon_health": {},
            "issues": [],
            "summary": ""
        }

        # 分析引擎健康状态
        if "engines" in quality_data and quality_data["engines"]:
            engines_data = quality_data["engines"]
            if "results" in engines_data:
                results = engines_data["results"]
                passed = sum(1 for r in results if r.get("status") == "pass")
                total = len(results)
                engine_score = (passed / total * 100) if total > 0 else 0
                diagnosis["engine_health"] = {
                    "total": total,
                    "passed": passed,
                    "failed": total - passed,
                    "score": round(engine_score, 1)
                }
                diagnosis["issues"].extend([
                    {
                        "type": "engine",
                        "engine": r.get("engine"),
                        "issue": r.get("error", "未知错误"),
                        "severity": "high" if r.get("status") != "pass" else "low"
                    }
                    for r in results if r.get("status") != "pass"
                ][:10])  # 最多10个

        # 分析场景计划健康状态
        if "scenes" in quality_data and quality_data["scenes"]:
            scenes_data = quality_data["scenes"]
            total_scenes = scenes_data.get("total_scenes", 0)
            issues_count = scenes_data.get("issues_count", 0)
            scene_score = ((total_scenes - issues_count) / total_scenes * 100) if total_scenes > 0 else 100
            diagnosis["scene_health"] = {
                "total": total_scenes,
                "issues": issues_count,
                "score": round(scene_score, 1)
            }

            # 从优化器报告添加问题
            if "optimizer" in scenes_data:
                opt = scenes_data["optimizer"]
                if "problems" in opt:
                    for prob in opt["problems"][:5]:
                        diagnosis["issues"].append({
                            "type": "scene",
                            "scene": prob.get("file", "unknown"),
                            "issue": prob.get("problem", ""),
                            "severity": prob.get("severity", "medium")
                        })

        # 计算整体健康分数
        scores = []
        if diagnosis["engine_health"]:
            scores.append(diagnosis["engine_health"].get("score", 0))
        if diagnosis["scene_health"]:
            scores.append(diagnosis["scene_health"].get("score", 0))
        diagnosis["overall_score"] = round(sum(scores) / len(scores), 1) if scores else 0

        # 生成总结
        if diagnosis["overall_score"] >= 80:
            diagnosis["summary"] = "系统整体健康状态良好，建议继续保持当前进化方向"
        elif diagnosis["overall_score"] >= 60:
            diagnosis["summary"] = "系统存在一定问题，建议优先处理高优先级问题后继续进化"
        else:
            diagnosis["summary"] = "系统健康状态较差，建议先进行修复优化再继续进化"

        self.diagnosis_data = diagnosis
        return diagnosis

    def identify_evolution_opportunities(self) -> List[Dict[str, Any]]:
        """识别进化机会"""
        opportunities = []

        # 基于诊断结果识别机会
        if not self.diagnosis_data:
            self.diagnose_system_health()

        # 机会 1: 引擎优化机会
        if self.diagnosis_data.get("engine_health", {}).get("failed", 0) > 0:
            opportunities.append({
                "id": "engine_optimization",
                "title": "引擎质量优化机会",
                "description": f"检测到 {self.diagnosis_data['engine_health']['failed']} 个引擎存在问题，需要修复",
                "priority": "high",
                "category": "engine",
                "estimated_impact": "提升系统稳定性和功能完整性",
                "actions": [
                    "运行 auto_quality_assurance_engine.py 分析失败原因",
                    "使用 auto_engine_repair_engine.py 自动修复",
                    "更新引擎依赖"
                ]
            })

        # 机会 2: 场景计划优化机会
        if self.diagnosis_data.get("scene_health", {}).get("issues", 0) > 0:
            opportunities.append({
                "id": "scene_optimization",
                "title": "场景计划优化机会",
                "description": f"检测到 {self.diagnosis_data['scene_health']['issues']} 个场景计划问题",
                "priority": "medium",
                "category": "scene",
                "estimated_impact": "提升场景执行成功率和用户体验",
                "actions": [
                    "运行 scenario_plan_optimizer.py 深度验证",
                    "使用 scene_plan_auto_repair_engine.py 自动修复",
                    "验证修复效果"
                ]
            })

        # 机会 3: 跨引擎协同优化
        opportunities.append({
            "id": "cross_engine_orchestration",
            "title": "跨引擎协同优化机会",
            "description": "基于已有 70+ 引擎，可以进一步优化引擎间的协同工作",
            "priority": "medium",
            "category": "integration",
            "estimated_impact": "提升多引擎联动效率和智能决策能力",
            "actions": [
                "分析引擎调用频率和依赖关系",
                "优化引擎组合和调度策略",
                "增强引擎间数据共享"
            ]
        })

        # 机会 4: 主动服务增强
        opportunities.append({
            "id": "proactive_service",
            "title": "主动服务增强机会",
            "description": "基于用户行为分析和上下文感知，增强主动服务能力",
            "priority": "low",
            "category": "service",
            "estimated_impact": "提升用户满意度和系统智能化水平",
            "actions": [
                "分析用户行为模式",
                "增强场景自适应能力",
                "优化主动推荐算法"
            ]
        })

        # 机会 5: 进化环自优化
        opportunities.append({
            "id": "evolution_self_optimization",
            "title": "进化环自优化机会",
            "description": "优化进化环本身的效率和决策质量",
            "priority": "low",
            "category": "meta",
            "estimated_impact": "提升进化效率和智能化水平",
            "actions": [
                "分析历史进化数据",
                "优化进化决策策略",
                "增强预测准确性"
            ]
        })

        self.opportunities = opportunities
        return opportunities

    def generate_evolution_plan(self) -> Dict[str, Any]:
        """生成进化规划"""
        if not self.opportunities:
            self.identify_evolution_opportunities()

        # 按优先级排序
        priority_order = {"high": 0, "medium": 1, "low": 2}
        sorted_opportunities = sorted(
            self.opportunities,
            key=lambda x: priority_order.get(x.get("priority", "low"), 2)
        )

        # 生成规划
        plan = {
            "timestamp": datetime.now().isoformat(),
            "current_round": 188,
            "diagnosis": self.diagnosis_data,
            "opportunities": sorted_opportunities,
            "recommended_actions": [],
            "next_evolution_suggestions": []
        }

        # 推荐行动（基于高优先级机会）
        for opp in sorted_opportunities[:3]:
            if opp.get("priority") in ["high", "medium"]:
                plan["recommended_actions"].append({
                    "opportunity": opp["title"],
                    "actions": opp.get("actions", []),
                    "priority": opp.get("priority"),
                    "estimated_impact": opp.get("estimated_impact")
                })

        # 下一轮进化建议
        if self.diagnosis_data.get("overall_score", 0) < 80:
            plan["next_evolution_suggestions"] = [
                "优先处理高优先级问题（引擎修复、场景计划优化）",
                "运行 unified_quality_loop.py 进行完整质量保障",
                "增强自动修复能力"
            ]
        else:
            plan["next_evolution_suggestions"] = [
                "继续增强跨引擎协同能力",
                "提升主动服务水平",
                "探索创新功能"
            ]

        self.plans = plan
        return plan

    def generate_full_report(self) -> Dict[str, Any]:
        """生成完整诊断报告"""
        if not self.diagnosis_data:
            self.diagnose_system_health()
        if not self.opportunities:
            self.identify_evolution_opportunities()
        if not self.plans:
            self.generate_evolution_plan()

        report = {
            "report_id": f"ev_diagnosis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "system_health": self.diagnosis_data,
            "opportunities": self.opportunities,
            "evolution_plan": self.plans,
            "conclusion": self.diagnosis_data.get("summary", "")
        }

        self.report = report

        # 保存报告
        report_path = RUNTIME_STATE / f"evolution_diagnosis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"诊断报告已保存到: {report_path}")
        return report

    def print_diagnosis(self):
        """打印诊断结果"""
        if not self.diagnosis_data:
            self.diagnose_system_health()

        print("\n" + "="*60)
        print("智能全场景自进化诊断报告")
        print("="*60)
        print(f"\n整体健康分数: {self.diagnosis_data.get('overall_score', 0)}/100")
        print(f"诊断时间: {self.diagnosis_data.get('timestamp', '')}")
        print(f"\n总结: {self.diagnosis_data.get('summary', '')}")

        # 引擎健康
        engine_health = self.diagnosis_data.get("engine_health", {})
        if engine_health:
            print(f"\n【引擎健康】")
            print(f"  总数: {engine_health.get('total', 0)}")
            print(f"  通过: {engine_health.get('passed', 0)}")
            print(f"  失败: {engine_health.get('failed', 0)}")
            print(f"  分数: {engine_health.get('score', 0)}")

        # 场景健康
        scene_health = self.diagnosis_data.get("scene_health", {})
        if scene_health:
            print(f"\n【场景计划健康】")
            print(f"  总数: {scene_health.get('total', 0)}")
            print(f"  问题: {scene_health.get('issues', 0)}")
            print(f"  分数: {scene_health.get('score', 0)}")

        # 问题列表
        issues = self.diagnosis_data.get("issues", [])
        if issues:
            print(f"\n【发现的问题】")
            for i, issue in enumerate(issues[:5], 1):
                print(f"  {i}. [{issue.get('type', 'unknown')}] {issue.get('issue', 'N/A')}")

        print("\n" + "="*60)

    def print_opportunities(self):
        """打印进化机会"""
        if not self.opportunities:
            self.identify_evolution_opportunities()

        print("\n" + "="*60)
        print("识别到的进化机会")
        print("="*60)

        for i, opp in enumerate(self.opportunities, 1):
            print(f"\n{i}. [{opp.get('priority', 'low').upper()}] {opp.get('title', 'N/A')}")
            print(f"   描述: {opp.get('description', 'N/A')}")
            print(f"   类别: {opp.get('category', 'N/A')}")
            print(f"   预期影响: {opp.get('estimated_impact', 'N/A')}")
            print(f"   建议行动: {', '.join(opp.get('actions', [])[:2])}")

        print("\n" + "="*60)

    def print_plan(self):
        """打印进化规划"""
        if not self.plans:
            self.generate_evolution_plan()

        print("\n" + "="*60)
        print("进化规划建议")
        print("="*60)

        print(f"\n【推荐行动】")
        for i, action in enumerate(self.plans.get("recommended_actions", []), 1):
            print(f"\n{i}. {action.get('opportunity', 'N/A')} [{action.get('priority', '').upper()}]")
            print(f"   影响: {action.get('estimated_impact', 'N/A')}")
            for act in action.get("actions", [])[:2]:
                print(f"   - {act}")

        print(f"\n【下一轮进化建议】")
        for suggestion in self.plans.get("next_evolution_suggestions", []):
            print(f"  - {suggestion}")

        print("\n" + "="*60)

    def print_report(self):
        """打印完整报告"""
        if not self.report:
            self.generate_full_report()

        print("\n" + "="*60)
        print("智能全场景自进化诊断与规划 - 完整报告")
        print("="*60)
        print(f"报告ID: {self.report.get('report_id', '')}")
        print(f"生成时间: {self.report.get('generated_at', '')}")

        self.print_diagnosis()
        self.print_opportunities()
        self.print_plan()

        print("\n【结论】")
        print(f"  {self.report.get('conclusion', '')}")
        print("="*60)

    def get_status(self) -> Dict[str, Any]:
        """获取诊断引擎状态"""
        status = {
            "engine": "active",
            "last_diagnosis": self.diagnosis_data.get("timestamp", "未诊断"),
            "opportunities_count": len(self.opportunities),
            "has_plan": bool(self.plans),
            "report_path": str(RUNTIME_STATE / f"evolution_diagnosis_report_{datetime.now().strftime('%Y%m%d')}.json")
        }

        # 检查可用的质量数据
        available_data = []
        if QUALITY_REPORT.exists():
            available_data.append("unified_quality_loop")
        if ENGINE_QUALITY.exists():
            available_data.append("engine_quality")
        if SCENE_TEST.exists():
            available_data.append("scene_test")
        if PLAN_OPTIMIZER.exists():
            available_data.append("plan_optimizer")

        status["available_data"] = available_data
        status["data_count"] = len(available_data)

        return status


def main():
    """主函数"""
    engine = EvolutionDiagnosisPlanner()

    if len(sys.argv) < 2:
        # 默认显示状态
        status = engine.get_status()
        print("智能全场景自进化诊断与规划引擎")
        print("="*40)
        print(f"引擎状态: {status.get('engine', 'unknown')}")
        print(f"上次诊断: {status.get('last_diagnosis', 'N/A')}")
        print(f"可用数据: {status.get('data_count', 0)} 项")
        print(f"已识别机会: {status.get('opportunities_count', 0)} 个")
        print(f"有规划: {'是' if status.get('has_plan') else '否'}")
        print("\n可用命令: diagnose, plan, opportunities, report, status")
        return

    command = sys.argv[1].lower()

    if command == "diagnose":
        engine.diagnose_system_health()
        engine.print_diagnosis()
    elif command == "opportunities":
        engine.identify_evolution_opportunities()
        engine.print_opportunities()
    elif command == "plan":
        engine.generate_evolution_plan()
        engine.print_plan()
    elif command == "report":
        engine.generate_full_report()
        engine.print_report()
    elif command == "status":
        status = engine.get_status()
        print("诊断引擎状态:")
        print(json.dumps(status, ensure_ascii=False, indent=2))
    elif command == "auto":
        print("自动执行模式需要确认后运行")
        print("建议先运行 'report' 查看完整诊断结果")
    else:
        print(f"未知命令: {command}")
        print("可用命令: diagnose, plan, opportunities, report, status")


if __name__ == "__main__":
    main()