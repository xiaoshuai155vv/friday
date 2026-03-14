"""
智能全场景进化环高质量假设自动执行与价值实现引擎
让系统能够自动筛选高质量假设、转化为进化任务、自动执行并追踪价值实现，
形成从假设生成→验证评估→自动执行→价值实现的完整闭环

Version: 1.0.0
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# 确保能导入进化环模块
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from scripts.evolution_hypothesis_generation_verification_engine import EvolutionHypothesisGenerationVerificationEngine
except ImportError:
    EvolutionHypothesisGenerationVerificationEngine = None

try:
    from scripts.evolution_value_realization_optimization_engine import EvolutionValueRealizationOptimizationEngine
except ImportError:
    EvolutionValueRealizationOptimizationEngine = None


class EvolutionHypothesisExecutionValueEngine:
    """高质量假设自动执行与价值实现引擎"""

    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else PROJECT_ROOT
        self.state_dir = self.project_root / "runtime" / "state"
        self.hypothesis_file = self.state_dir / "hypothesis_cache.json"
        self.execution_log_file = self.state_dir / "hypothesis_execution_log.json"
        self.value_tracking_file = self.state_dir / "hypothesis_value_tracking.json"

        # 质量阈值
        self.HIGH_QUALITY_THRESHOLD = 0.7  # 高质量假设的综合评分阈值
        self.AUTO_EXECUTE_THRESHOLD = 0.85  # 自动执行的综合评分阈值

        # 初始化相关引擎
        self.hypothesis_engine = None
        self.value_engine = None
        self._initialize_engines()

    def _initialize_engines(self):
        """初始化相关引擎"""
        if EvolutionHypothesisGenerationVerificationEngine:
            try:
                self.hypothesis_engine = EvolutionHypothesisGenerationVerificationEngine(str(self.project_root))
            except Exception as e:
                print(f"[WARN] 初始化假设生成引擎失败: {e}")

        if EvolutionValueRealizationOptimizationEngine:
            try:
                self.value_engine = EvolutionValueRealizationOptimizationEngine(str(self.project_root))
            except Exception as e:
                print(f"[WARN] 初始化价值追踪引擎失败: {e}")

    def load_hypotheses(self) -> List[Dict]:
        """加载当前假设缓存"""
        if not self.hypothesis_file.exists():
            # 尝试从假设生成引擎获取最新假设
            if self.hypothesis_engine:
                try:
                    status = self.hypothesis_engine.get_status()
                    if status.get("hypotheses"):
                        return status["hypotheses"]
                except:
                    pass
            return []

        try:
            with open(self.hypothesis_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("hypotheses", [])
        except Exception as e:
            print(f"[ERROR] 加载假设缓存失败: {e}")
            return []

    def filter_high_quality_hypotheses(self, hypotheses: List[Dict]) -> List[Dict]:
        """筛选高质量假设"""
        high_quality = []
        for hypothesis in hypotheses:
            score = hypothesis.get("confidence_score", 0) * hypothesis.get("potential_score", 0)
            comprehensive = hypothesis.get("comprehensive_score", score)
            if comprehensive >= self.HIGH_QUALITY_THRESHOLD:
                hypothesis["quality_score"] = comprehensive
                high_quality.append(hypothesis)

        # 按综合评分排序
        high_quality.sort(key=lambda x: x.get("quality_score", 0), reverse=True)
        return high_quality

    def select_auto_execute_hypotheses(self, hypotheses: List[Dict]) -> List[Dict]:
        """选择可自动执行的假设"""
        auto_execute = []
        for hypothesis in hypotheses:
            comprehensive = hypothesis.get("comprehensive_score", 0)
            if comprehensive >= self.AUTO_EXECUTE_THRESHOLD:
                # 检查验证实验设计是否完整
                experiments = hypothesis.get("experiments", [])
                if experiments:
                    hypothesis["selected_for_execution"] = True
                    auto_execute.append(hypothesis)

        return auto_execute

    def convert_hypothesis_to_task(self, hypothesis: Dict) -> Dict:
        """将假设转化为进化任务"""
        task = {
            "task_id": f"hyp_exec_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hypothesis.get('id', 'unknown')}",
            "hypothesis_id": hypothesis.get("id", "unknown"),
            "hypothesis_title": hypothesis.get("title", ""),
            "description": hypothesis.get("description", ""),
            "expected_value": hypothesis.get("expected_value", ""),
            "quality_score": hypothesis.get("quality_score", 0),
            "experiments": hypothesis.get("experiments", []),
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "execution_history": []
        }
        return task

    def execute_hypothesis(self, hypothesis: Dict) -> Dict:
        """执行假设（模拟执行，返回执行计划）"""
        task = self.convert_hypothesis_to_task(hypothesis)
        experiments = hypothesis.get("experiments", [])

        # 生成执行计划
        execution_plan = {
            "phase_1_validation": {
                "description": "第一阶段：验证假设的基本可行性",
                "steps": [
                    "收集当前系统状态数据",
                    "设计小型验证实验",
                    "执行验证并记录结果"
                ],
                "estimated_time": "10分钟"
            },
            "phase_2_execution": {
                "description": "第二阶段：执行完整的进化任务",
                "steps": [
                    "实施假设对应的改进",
                    "执行验证实验",
                    "收集执行数据"
                ],
                "estimated_time": "30分钟"
            },
            "phase_3_value_realization": {
                "description": "第三阶段：价值实现评估",
                "steps": [
                    "评估进化效果",
                    "计算价值实现度",
                    "生成价值报告"
                ],
                "estimated_time": "15分钟"
            }
        }

        task["execution_plan"] = execution_plan
        task["status"] = "ready_to_execute"
        task["executed_at"] = datetime.now().isoformat()

        # 记录到执行日志
        self._log_execution(task)

        return task

    def _log_execution(self, task: Dict):
        """记录执行日志"""
        if not self.execution_log_file.exists():
            execution_log = {"executions": []}
        else:
            try:
                with open(self.execution_log_file, 'r', encoding='utf-8') as f:
                    execution_log = json.load(f)
            except:
                execution_log = {"executions": []}

        execution_log["executions"].append(task)

        # 保留最近50条记录
        if len(execution_log["executions"]) > 50:
            execution_log["executions"] = execution_log["executions"][-50:]

        try:
            with open(self.execution_log_file, 'w', encoding='utf-8') as f:
                json.dump(execution_log, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ERROR] 记录执行日志失败: {e}")

    def track_value_realization(self, task: Dict) -> Dict:
        """追踪价值实现"""
        value_tracking = {
            "task_id": task.get("task_id"),
            "hypothesis_title": task.get("hypothesis_title"),
            "expected_value": task.get("expected_value", ""),
            "quality_score": task.get("quality_score", 0),
            "status": task.get("status", "unknown"),
            "value_metrics": {
                "execution_completeness": 0.0,
                "value_realization_rate": 0.0,
                "efficiency_improvement": 0.0,
                "system_capability_gain": 0.0
            },
            "tracking_started_at": datetime.now().isoformat(),
            "milestones": []
        }

        # 如果有价值引擎，可以调用它来获取更详细的追踪
        if self.value_engine:
            try:
                value_analysis = self.value_engine.quantify_evolution_value([])
                value_tracking["value_metrics"]["value_realization_rate"] = value_analysis.get("overall_value_score", 0.5)
            except:
                pass

        # 保存追踪数据
        self._save_value_tracking(value_tracking)

        return value_tracking

    def _save_value_tracking(self, tracking: Dict):
        """保存价值追踪数据"""
        if not self.value_tracking_file.exists():
            tracking_data = {"trackings": []}
        else:
            try:
                with open(self.value_tracking_file, 'r', encoding='utf-8') as f:
                    tracking_data = json.load(f)
            except:
                tracking_data = {"trackings": []}

        tracking_data["trackings"].append(tracking)

        # 保留最近50条记录
        if len(tracking_data["trackings"]) > 50:
            tracking_data["trackings"] = tracking_data["trackings"][-50:]

        try:
            with open(self.value_tracking_file, 'w', encoding='utf-8') as f:
                json.dump(tracking_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ERROR] 保存价值追踪数据失败: {e}")

    def get_execution_summary(self) -> Dict:
        """获取执行摘要"""
        hypotheses = self.load_hypotheses()
        high_quality = self.filter_high_quality_hypotheses(hypotheses)
        auto_execute = self.select_auto_execute_hypotheses(hypotheses)

        summary = {
            "total_hypotheses": len(hypotheses),
            "high_quality_count": len(high_quality),
            "auto_execute_count": len(auto_execute),
            "high_quality_hypotheses": [
                {
                    "id": h.get("id"),
                    "title": h.get("title"),
                    "quality_score": h.get("quality_score", 0)
                }
                for h in high_quality[:5]
            ],
            "auto_execute_hypotheses": [
                {
                    "id": h.get("id"),
                    "title": h.get("title"),
                    "comprehensive_score": h.get("comprehensive_score", 0)
                }
                for h in auto_execute[:5]
            ]
        }

        # 添加执行日志统计
        if self.execution_log_file.exists():
            try:
                with open(self.execution_log_file, 'r', encoding='utf-8') as f:
                    execution_log = json.load(f)
                    summary["total_executions"] = len(execution_log.get("executions", []))
                    summary["pending_executions"] = sum(
                        1 for e in execution_log.get("executions", [])
                        if e.get("status") == "pending"
                    )
                    summary["ready_executions"] = sum(
                        1 for e in execution_log.get("executions", [])
                        if e.get("status") == "ready_to_execute"
                    )
            except:
                pass

        return summary

    def get_cockpit_data(self) -> Dict:
        """获取驾驶舱数据"""
        summary = self.get_execution_summary()

        return {
            "hypothesis_execution_engine": {
                "status": "active",
                "version": "1.0.0",
                "summary": summary
            },
            "timestamp": datetime.now().isoformat()
        }

    def run_cycle(self) -> Dict:
        """运行一个完整的假设执行与价值实现循环"""
        results = {
            "cycle_status": "started",
            "timestamp": datetime.now().isoformat(),
            "steps_completed": []
        }

        # 步骤1：加载假设
        hypotheses = self.load_hypotheses()
        results["steps_completed"].append("load_hypotheses")
        results["hypotheses_loaded"] = len(hypotheses)

        # 步骤2：筛选高质量假设
        high_quality = self.filter_high_quality_hypotheses(hypotheses)
        results["steps_completed"].append("filter_high_quality")
        results["high_quality_count"] = len(high_quality)

        # 步骤3：选择可自动执行的假设
        auto_execute = self.select_auto_execute_hypotheses(high_quality)
        results["steps_completed"].append("select_auto_execute")
        results["auto_execute_count"] = len(auto_execute)

        # 步骤4：执行高质量假设
        executed_tasks = []
        for hypothesis in auto_execute[:3]:  # 最多执行3个
            task = self.execute_hypothesis(hypothesis)
            executed_tasks.append(task)

            # 步骤5：追踪价值实现
            self.track_value_realization(task)

        results["steps_completed"].append("execute_and_track")
        results["executed_count"] = len(executed_tasks)
        results["cycle_status"] = "completed"

        return results


def main():
    """命令行入口"""
    import argparse
    parser = argparse.ArgumentParser(description="高质量假设自动执行与价值实现引擎")
    parser.add_argument("--status", action="store_true", help="获取引擎状态")
    parser.add_argument("--filter", action="store_true", help="筛选高质量假设")
    parser.add_argument("--auto-execute", action="store_true", help="选择可自动执行的假设")
    parser.add_argument("--execute", action="store_true", help="执行高质量假设")
    parser.add_argument("--cycle", action="store_true", help="运行完整循环")
    parser.add_argument("--summary", action="store_true", help="获取执行摘要")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")
    parser.add_argument("--project-root", type=str, default=None, help="项目根目录")

    args = parser.parse_args()

    engine = EvolutionHypothesisExecutionValueEngine(args.project_root)

    if args.status:
        result = engine.get_execution_summary()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.filter:
        hypotheses = engine.load_hypotheses()
        high_quality = engine.filter_high_quality_hypotheses(hypotheses)
        print(f"高质量假设数量: {len(high_quality)}")
        for h in high_quality[:5]:
            print(f"  - {h.get('title')}: 质量分数={h.get('quality_score', 0):.2f}")
    elif args.auto_execute:
        hypotheses = engine.load_hypotheses()
        high_quality = engine.filter_high_quality_hypotheses(hypotheses)
        auto_execute = engine.select_auto_execute_hypotheses(high_quality)
        print(f"可自动执行的假设数量: {len(auto_execute)}")
        for h in auto_execute[:5]:
            print(f"  - {h.get('title')}: 综合评分={h.get('comprehensive_score', 0):.2f}")
    elif args.execute:
        hypotheses = engine.load_hypotheses()
        high_quality = engine.filter_high_quality_hypotheses(hypotheses)
        auto_execute = engine.select_auto_execute_hypotheses(high_quality)
        executed = []
        for h in auto_execute[:3]:
            task = engine.execute_hypothesis(h)
            engine.track_value_realization(task)
            executed.append(task.get("task_id"))
        print(f"已执行 {len(executed)} 个假设")
        for tid in executed:
            print(f"  - {tid}")
    elif args.cycle:
        result = engine.run_cycle()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.summary:
        result = engine.get_execution_summary()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.cockpit_data:
        result = engine.get_cockpit_data()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()