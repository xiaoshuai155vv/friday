#!/usr/bin/env python3
"""
智能全场景进化环预防-诊断-修复完整闭环引擎
version 1.0.0 (round 486)

在 round 485 完成的预防性维护增强引擎和 round 483/484 的主动诊断与自动修复引擎基础上，
将预防性维护能力与自动诊断/修复能力深度集成，形成「预测→预警→自动诊断→自动修复→验证」的完整闭环。

让系统能够在预测到潜在问题时，不仅发出预警，还能自动启动诊断流程、生成修复方案并执行修复，
形成真正的「预防→诊断→修复」完整自动化闭环。

功能：
1. 预防-诊断联动：预测到问题时自动触发深度诊断
2. 诊断-修复联动：诊断出可修复问题时自动执行修复
3. 修复效果验证：修复后自动验证效果
4. 完整闭环追踪：记录整个闭环过程
5. 与进化驾驶舱深度集成
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
STATE_DIR = PROJECT_ROOT / "runtime" / "state"
LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"

# 导入相关引擎
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
try:
    from evolution_preventive_maintenance_enhancement_engine import PreventiveMaintenanceEngine
    from evolution_proactive_diagnosis_optimizer_engine import ProactiveDiagnosisOptimizer
    IMPORTS_OK = True
except ImportError as e:
    IMPORTS_OK = False
    IMPORT_ERROR = str(e)


class PreventionDiagnosisRepairClosedLoop:
    """预防-诊断-修复完整闭环引擎"""

    def __init__(self):
        self.state_dir = STATE_DIR
        self.logs_dir = LOGS_DIR

        # 初始化相关引擎
        if IMPORTS_OK:
            self.prevention_engine = PreventiveMaintenanceEngine()
            self.diagnosis_engine = ProactiveDiagnosisOptimizer()
        else:
            self.prevention_engine = None
            self.diagnosis_engine = None

        # 闭环配置
        self.loop_config = {
            "auto_diagnose_on_prediction": True,  # 预测到问题时自动诊断
            "auto_fix_on_diagnosis": True,  # 诊断出问题时自动修复
            "auto_verify_after_fix": True,  # 修复后自动验证
            "min_risk_threshold": 0.4,  # 触发自动诊断的风险阈值
            "min_problem_severity": "medium"  # 触发自动修复的问题严重级别
        }

        # 问题类型到修复动作的映射
        self.fix_action_map = {
            "health_degradation": "optimize_strategy",
            "failure_risk": "enhance_validation",
            "efficiency_decline": "resource_optimization",
            "accumulated_issues": "cleanup_and_repair",
            "success_rate_low": "enhance_validation",
            "efficiency_low": "resource_optimization",
            "response_time_high": "optimize_strategy"
        }

    def load_evolution_history(self, limit=50):
        """加载进化历史数据"""
        history = []
        state_dir = self.state_dir

        for f in sorted(state_dir.glob("evolution_completed_*.json"), reverse=True)[:limit]:
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    history.append(data)
            except Exception as e:
                print(f"Warning: Failed to load {f}: {e}", file=sys.stderr)

        return history

    def load_performance_data(self):
        """加载效能数据"""
        perf_file = self.state_dir / "evolution_performance_data.json"
        if perf_file.exists():
            try:
                with open(perf_file, 'r', encoding='utf-8') as fp:
                    return json.load(fp)
            except Exception as e:
                print(f"Warning: Failed to load performance data: {e}", file=sys.stderr)

        return {}

    def predict_and_diagnose(self, history, perf_data):
        """预测并诊断：利用预防引擎预测，利用诊断引擎诊断"""
        loop_result = {
            "stage": "predict_and_diagnose",
            "timestamp": datetime.now().isoformat(),
            "prevention_result": None,
            "diagnosis_result": None,
            "should_continue": False
        }

        # 阶段1：预防性预测
        if self.prevention_engine:
            trend = self.prevention_engine.analyze_health_trend(history)
            risk = self.prevention_engine.predict_failure_risk(history, perf_data)
            opportunities, _, _ = self.prevention_engine.identify_prevention_opportunities(history, perf_data)

            loop_result["prevention_result"] = {
                "trend": trend,
                "risk": risk,
                "opportunities": opportunities
            }

            print("=" * 60)
            print("【阶段1】预防性预测")
            print("=" * 60)
            print(f"健康趋势: {trend['trend']} - {trend['prediction']}")
            print(f"失败风险: {risk['risk_level']} ({risk['failure_probability']:.0%})")
            print(f"预防机会: {len(opportunities)} 个")

            # 判断是否需要继续诊断
            should_diagnose = (
                risk["failure_probability"] >= self.loop_config["min_risk_threshold"] or
                any(o.get("severity") in ["high", "critical"] for o in opportunities)
            )

            if not should_diagnose:
                print("\n风险较低，无需深度诊断")
                return loop_result
        else:
            # 模拟预防结果
            loop_result["prevention_result"] = {"error": "预防引擎未加载"}
            should_diagnose = True

        # 阶段2：深度诊断
        if should_diagnose and self.diagnosis_engine:
            health_score, diagnosis = self.diagnosis_engine.calculate_health_score(history, perf_data)
            problems = self.diagnosis_engine.analyze_problems(history, perf_data)
            suggestions = self.diagnosis_engine.generate_optimization_suggestions(problems, history)

            loop_result["diagnosis_result"] = {
                "health_score": health_score,
                "diagnosis": diagnosis,
                "problems": problems,
                "suggestions": suggestions
            }

            print("\n" + "=" * 60)
            print("【阶段2】深度诊断")
            print("=" * 60)
            print(f"健康分数: {health_score:.1f}")
            print(f"诊断: {diagnosis}")
            print(f"发现问题: {len(problems)} 个")
            for p in problems[:3]:  # 只显示前3个
                print(f"  - [{p['severity'].upper()}] {p['type']}: {p['description']}")

            loop_result["should_continue"] = len(problems) > 0
        else:
            loop_result["diagnosis_result"] = {"error": "诊断引擎未加载或无需诊断"}
            loop_result["should_continue"] = False

        return loop_result

    def diagnose_and_fix(self, diagnosis_result, history, perf_data, dry_run=False):
        """诊断并修复：根据诊断结果执行自动修复"""
        loop_result = {
            "stage": "diagnose_and_fix",
            "timestamp": datetime.now().isoformat(),
            "fixable_problems": [],
            "fix_results": [],
            "fix_summary": ""
        }

        if not diagnosis_result or "problems" not in diagnosis_result:
            loop_result["fix_summary"] = "无需修复"
            return loop_result

        problems = diagnosis_result.get("problems", [])

        # 识别可自动修复的问题
        if self.diagnosis_engine:
            fixable = self.diagnosis_engine.get_auto_fixable_problems(problems)
            loop_result["fixable_problems"] = fixable

            print("\n" + "=" * 60)
            print("【阶段3】自动修复")
            print("=" * 60)
            print(f"可修复问题: {len(fixable)} 个")

            if not fixable:
                print("无可自动修复的问题")
                loop_result["fix_summary"] = "无可自动修复的问题"
                return loop_result

            # 执行修复
            for fix_item in fixable:
                problem = fix_item.get("problem", {})
                problem_type = problem.get("type", fix_item.get("description", "unknown"))
                fix_action = fix_item.get("fix_action", "general_optimization")

                if dry_run:
                    print(f"  [模拟] 将修复: {problem_type}")
                    loop_result["fix_results"].append({
                        "problem": fix_item,
                        "result": {"status": "simulated", "message": "模拟执行"}
                    })
                else:
                    # 使用 fix_item 中提供的修复动作
                    result = self.diagnosis_engine.execute_auto_fix(fix_action, {"problem": problem})
                    print(f"  [{result.get('status', 'unknown')}] {problem_type}: {result.get('message', '')}")
                    loop_result["fix_results"].append({
                        "problem": fix_item,
                        "result": result
                    })

            success_count = sum(1 for r in loop_result["fix_results"] if r["result"].get("status") == "completed")
            loop_result["fix_summary"] = f"成功修复 {success_count}/{len(fixable)} 个问题"
        else:
            loop_result["fix_summary"] = "诊断引擎未加载，无法执行修复"

        return loop_result

    def verify_fix_effectiveness(self, history, perf_data, fix_results):
        """验证修复效果"""
        loop_result = {
            "stage": "verify_fix_effectiveness",
            "timestamp": datetime.now().isoformat(),
            "verification_results": [],
            "overall_effectiveness": "unknown"
        }

        if not fix_results:
            loop_result["overall_effectiveness"] = "no_fixes_to_verify"
            return loop_result

        print("\n" + "=" * 60)
        print("【阶段4】修复效果验证")
        print("=" * 60)

        # 重新加载数据以验证
        new_history = self.load_evolution_history()
        new_perf_data = self.load_performance_data()

        if self.prevention_engine:
            new_trend = self.prevention_engine.analyze_health_trend(new_history)
            new_risk = self.prevention_engine.predict_failure_risk(new_history, new_perf_data)

            loop_result["verification_results"] = {
                "new_trend": new_trend,
                "new_risk": new_risk
            }

            print(f"修复后健康趋势: {new_trend['trend']}")
            print(f"修复后失败风险: {new_risk['risk_level']} ({new_risk['failure_probability']:.0%})")

            # 判断效果
            if new_risk["risk_level"] in ["low", "unknown"]:
                loop_result["overall_effectiveness"] = "effective"
                print("修复效果: 有效")
            elif new_risk["failure_probability"] < 0.3:
                loop_result["overall_effectiveness"] = "partially_effective"
                print("修复效果: 部分有效")
            else:
                loop_result["overall_effectiveness"] = "ineffective"
                print("修复效果: 需要进一步处理")
        else:
            loop_result["overall_effectiveness"] = "verification_skipped"

        return loop_result

    def _map_problem_to_fix_action(self, problem):
        """将问题类型映射到修复动作"""
        problem_type = problem.get("type", "").lower()

        for key, action in self.fix_action_map.items():
            if key in problem_type:
                return action

        return "general_optimization"

    def run_full_loop(self, auto_fix=True, dry_run=False):
        """运行完整的预防-诊断-修复闭环"""
        print("=" * 70)
        print("智能全场景进化环 预防-诊断-修复 完整闭环")
        print("=" * 70)

        if not IMPORTS_OK:
            print(f"\n警告: 引擎导入失败 - {IMPORT_ERROR}")
            print("完整闭环需要预防引擎和诊断引擎同时可用")
            return {
                "status": "import_error",
                "error": IMPORT_ERROR,
                "timestamp": datetime.now().isoformat()
            }

        # 加载数据
        history = self.load_evolution_history()
        perf_data = self.load_performance_data()

        print(f"\n当前状态: {len(history)} 条进化历史记录")

        # 阶段1-2: 预测并诊断
        predict_diagnose_result = self.predict_and_diagnose(history, perf_data)

        # 阶段3: 诊断并修复
        if auto_fix and predict_diagnose_result.get("should_continue"):
            diagnose_fix_result = self.diagnose_and_fix(
                predict_diagnose_result.get("diagnosis_result"),
                history,
                perf_data,
                dry_run
            )
        else:
            diagnose_fix_result = {
                "stage": "diagnose_and_fix",
                "fix_summary": "跳过修复阶段（auto_fix=False 或无需诊断）",
                "fix_results": []
            }

        # 阶段4: 验证修复效果
        verify_result = self.verify_fix_effectiveness(
            history,
            perf_data,
            diagnose_fix_result.get("fix_results", [])
        )

        # 生成完整闭环报告
        loop_report = {
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "predict_diagnose": predict_diagnose_result,
            "diagnose_fix": diagnose_fix_result,
            "verify": verify_result,
            "overall_status": self._generate_overall_status(predict_diagnose_result, diagnose_fix_result, verify_result)
        }

        # 保存报告
        report_file = self.state_dir / "prevention_diagnosis_repair_loop_result.json"
        with open(report_file, 'w', encoding='utf-8') as fp:
            json.dump(loop_report, fp, ensure_ascii=False, indent=2)

        print("\n" + "=" * 70)
        print("完整闭环执行完成")
        print("=" * 70)
        print(f"总体状态: {loop_report['overall_status']}")
        print(f"详细报告已保存到: {report_file}")

        return loop_report

    def _generate_overall_status(self, predict_diagnose, diagnose_fix, verify):
        """生成总体状态评估"""
        # 检查预防阶段
        if predict_diagnose.get("prevention_result"):
            risk = predict_diagnose["prevention_result"].get("risk", {})
            risk_level = risk.get("risk_level", "unknown")
            if risk_level in ["critical", "high"]:
                return "needs_attention"

        # 检查修复阶段
        fix_summary = diagnose_fix.get("fix_summary", "")
        if "成功修复" in fix_summary:
            success_rate = fix_summary.split("/")[0].split()[-1]
            try:
                if int(success_rate) > 0:
                    pass  # 有修复
            except:
                pass

        # 检查验证阶段
        effectiveness = verify.get("overall_effectiveness", "unknown")
        if effectiveness == "effective":
            return "healthy"
        elif effectiveness == "partially_effective":
            return "recovering"
        elif effectiveness == "ineffective":
            return "needs_more_attention"

        return "stable"

    def get_cockpit_data(self):
        """获取驾驶舱数据接口"""
        history = self.load_evolution_history()
        perf_data = self.load_performance_data()

        # 获取预防数据
        prevention_data = {}
        if self.prevention_engine:
            prevention_data = self.prevention_engine.get_cockpit_data()

        # 获取诊断数据
        diagnosis_data = {}
        if self.diagnosis_engine:
            health_score, diagnosis = self.diagnosis_engine.calculate_health_score(history, perf_data)
            problems = self.diagnosis_engine.analyze_problems(history, perf_data)
            diagnosis_data = {
                "health_score": health_score,
                "diagnosis": diagnosis,
                "problem_count": len(problems),
                "high_severity_problems": len([p for p in problems if p.get("severity") == "high"])
            }

        return {
            "prevention": prevention_data,
            "diagnosis": diagnosis_data,
            "loop_status": self._generate_overall_status(
                {"prevention_result": prevention_data.get("failure_risk")},
                {"fix_summary": ""},
                {"overall_effectiveness": "unknown"}
            ),
            "timestamp": datetime.now().isoformat()
        }

    def quick_status(self):
        """快速状态查看"""
        print("=" * 60)
        print("预防-诊断-修复闭环状态")
        print("=" * 60)

        if not IMPORTS_OK:
            print(f"引擎状态: 导入失败 - {IMPORT_ERROR}")
            return

        data = self.get_cockpit_data()

        print("\n【预防状态】")
        prev = data.get("prevention", {})
        if prev:
            print(f"  健康趋势: {prev.get('trend', {}).get('trend', 'unknown')}")
            print(f"  失败风险: {prev.get('failure_risk', {}).get('risk_level', 'unknown')}")
            print(f"  预防机会: {prev.get('prevention_opportunities', 0)} 个")

        print("\n【诊断状态】")
        diag = data.get("diagnosis", {})
        if diag:
            print(f"  健康分数: {diag.get('health_score', 0):.1f}")
            print(f"  问题数量: {diag.get('problem_count', 0)} 个")
            print(f"  高严重问题: {diag.get('high_severity_problems', 0)} 个")

        print(f"\n【闭环状态】: {data.get('loop_status', 'unknown')}")


def main():
    parser = argparse.ArgumentParser(
        description="智能全场景进化环预防-诊断-修复完整闭环引擎"
    )
    parser.add_argument("--run", action="store_true", help="运行完整闭环")
    parser.add_argument("--auto-fix", action="store_true", default=True, help="自动执行修复（默认启用）")
    parser.add_argument("--dry-run", action="store_true", help="模拟模式，不实际执行")
    parser.add_argument("--status", action="store_true", help="快速查看闭环状态")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据接口")

    args = parser.parse_args()

    engine = PreventionDiagnosisRepairClosedLoop()

    if args.status:
        engine.quick_status()
    elif args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
    elif args.run:
        result = engine.run_full_loop(
            auto_fix=args.auto_fix,
            dry_run=args.dry_run
        )
        print(f"\n总体状态: {result.get('overall_status', 'unknown')}")
    else:
        parser.print_help()
        print("\n示例:")
        print("  python evolution_prevention_diagnosis_repair_closed_loop_engine.py --status")
        print("  python evolution_prevention_diagnosis_repair_closed_loop_engine.py --run")
        print("  python evolution_prevention_diagnosis_repair_closed_loop_engine.py --run --dry-run")
        print("  python evolution_prevention_diagnosis_repair_closed_loop_engine.py --cockpit-data")


if __name__ == "__main__":
    main()