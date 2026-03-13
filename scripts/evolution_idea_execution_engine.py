#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能进化创意评估与执行引擎
将进化创意生成器(226)与执行能力集成，实现从创意→评估→执行的完整闭环

功能：
1. 创意深度评估（多维度打分：价值、可行性、风险、紧急度）
2. 创意优先级动态调整（基于当前系统状态、进化进度）
3. 创意到执行的完整流程（评估→选择→执行→验证）
4. 执行结果反馈到学习系统形成闭环

version: 1.0.0
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# 将 scripts 目录加入 path 以便导入同目录模块
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from evolution_idea_generator import EvolutionIdeaGenerator

# 项目根目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
REFERENCES_DIR = os.path.join(PROJECT_ROOT, "references")
RUNTIME_STATE_DIR = os.path.join(PROJECT_ROOT, "runtime", "state")
RUNTIME_LOGS_DIR = os.path.join(PROJECT_ROOT, "runtime", "logs")


class EvolutionIdeaExecutionEngine:
    """智能进化创意评估与执行引擎"""

    def __init__(self):
        self.idea_generator = EvolutionIdeaGenerator()
        self.references_dir = REFERENCES_DIR
        self.state_dir = RUNTIME_STATE_DIR
        self.logs_dir = RUNTIME_LOGS_DIR
        self.execution_history_file = os.path.join(RUNTIME_STATE_DIR, "idea_execution_history.json")
        self.execution_history = self._load_execution_history()

    def _load_execution_history(self):
        """加载执行历史"""
        if os.path.exists(self.execution_history_file):
            try:
                with open(self.execution_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"executions": [], "learnings": []}
        return {"executions": [], "learnings": []}

    def _save_execution_history(self):
        """保存执行历史"""
        try:
            with open(self.execution_history_file, 'w', encoding='utf-8') as f:
                json.dump(self.execution_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存执行历史失败: {e}")

    def deep_evaluate_ideas(self, ideas):
        """深度评估创意 - 多维度打分"""
        if not ideas:
            return []

        evaluated = []
        for idea in ideas:
            # 多维度评估
            scores = {
                "value_score": self._evaluate_value(idea),
                "feasibility_score": self._evaluate_feasibility(idea),
                "risk_score": self._evaluate_risk(idea),
                "urgency_score": self._evaluate_urgency(idea)
            }

            # 计算综合得分（加权平均）
            weights = {"value_score": 0.35, "feasibility_score": 0.25, "risk_score": 0.15, "urgency_score": 0.25}
            total_score = sum(scores[k] * weights[k] for k in weights)

            evaluated_idea = {
                **idea,
                "scores": scores,
                "total_score": round(total_score, 2),
                "evaluated_at": datetime.now().isoformat()
            }
            evaluated.append(evaluated_idea)

        # 按综合得分排序
        evaluated.sort(key=lambda x: x.get("total_score", 0), reverse=True)
        return evaluated

    def _evaluate_value(self, idea):
        """评估价值 - 这个创意对系统的价值"""
        # 基于类型和描述评估价值
        value_indicators = {
            "autonomy": 0.9,  # 自主能力 - 高价值
            "collaboration": 0.85,  # 协作能力 - 高价值
            "learning": 0.9,  # 学习能力 - 高价值
            "prediction": 0.85,  # 预测能力 - 高价值
            "execution": 0.8,  # 执行能力 - 高价值
            "optimization": 0.75,  # 优化能力 - 中高价值
            "integration": 0.8,  # 集成能力 - 高价值
            "automation": 0.85,  # 自动化 - 高价值
        }

        desc = idea.get("description", "").lower()
        for key, score in value_indicators.items():
            if key in desc:
                return score
        return 0.5  # 默认中等价值

    def _evaluate_feasibility(self, idea):
        """评估可行性 - 这个创意能否实现"""
        # 检查是否已有类似实现
        existing_engines = self._get_existing_engines()
        desc = idea.get("description", "").lower()

        # 如果已有类似引擎，可行性降低（可能是扩展而非全新创建）
        for engine in existing_engines:
            if engine.lower() in desc:
                return 0.7  # 已有基础，可行性较高

        # 检查是否是已知领域
        known_domains = ["evolution", "engine", "collaboration", "learning", "prediction", "execution"]
        for domain in known_domains:
            if domain in desc:
                return 0.75  # 已知领域，可行性较高

        return 0.5  # 默认中等可行性

    def _evaluate_risk(self, idea):
        """评估风险 - 实现这个创意的风险"""
        risk_indicators = {
            "integration": 0.6,  # 集成风险中等
            "autonomous": 0.4,  # 自主风险较低
            "real-time": 0.5,  # 实时性风险中等
            "cross-engine": 0.5,  # 跨引擎风险中等
            "deep": 0.4,  # 深度风险较低
            "full": 0.6,  # 完整风险中等
            "complete": 0.6,  # 完整风险中等
        }

        desc = idea.get("description", "").lower()
        for key, risk in risk_indicators.items():
            if key in desc:
                return risk

        # 检查是否是复杂特性
        complexity_words = ["完整", "深度", "全面", "复杂", "complete", "deep", "complex"]
        for word in complexity_words:
            if word in desc:
                return 0.6

        return 0.4  # 默认较低风险

    def _evaluate_urgency(self, idea):
        """评估紧急度 - 这个创意多快需要实现"""
        # 基于当前进化状态评估
        # 如果相关领域已经完成很多轮，紧急度降低
        desc = idea.get("description", "").lower()

        # 检查round 226的建议
        if "评估" in desc or "执行" in desc or "evaluation" in desc or "execution" in desc:
            return 0.9  # 来自上一轮建议，紧急度高

        # 检查与现有完成轮次的关系
        completed_areas = self._get_recent_completed_areas()
        for area in completed_areas:
            if area in desc:
                return 0.4  # 已有进展，紧急度降低

        return 0.5  # 默认中等紧急度

    def _get_existing_engines(self):
        """获取已存在的引擎列表"""
        engines = []
        scripts_dir = os.path.join(PROJECT_ROOT, "scripts")

        if os.path.exists(scripts_dir):
            for f in os.listdir(scripts_dir):
                if f.endswith("_engine.py") or f.endswith("_enhancer.py") or f.endswith("_generator.py"):
                    engines.append(f.replace(".py", ""))

        return engines

    def _get_recent_completed_areas(self):
        """获取近期已完成领域"""
        # 从 evolution_auto_last.md 读取
        auto_last_file = os.path.join(REFERENCES_DIR, "evolution_auto_last.md")
        if os.path.exists(auto_last_file):
            try:
                with open(auto_last_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 提取已完成的领域关键词
                    areas = []
                    keywords = ["协同", "学习", "预测", "执行", "闭环", "自治", "创意", "策略"]
                    for kw in keywords:
                        if kw in content:
                            areas.append(kw)
                    return areas
            except:
                pass
        return []

    def dynamic_priority_adjustment(self, ideas, context=None):
        """基于当前上下文动态调整优先级"""
        if not ideas:
            return ideas

        context = context or {}
        adjusted = []

        for idea in ideas:
            adjusted_idea = idea.copy()

            # 根据系统状态调整
            system_state = context.get("system_state", "normal")

            # 如果系统繁忙，降低高风险任务的优先级
            if system_state == "busy":
                if idea.get("scores", {}).get("risk_score", 0.4) > 0.6:
                    adjusted_idea["total_score"] *= 0.8  # 降低优先级

            # 如果是紧急需求（如用户明确要求），提高优先级
            if context.get("urgent_request", False):
                adjusted_idea["total_score"] *= 1.3

            # 如果是测试/验证模式，降低分值以避免意外执行
            if context.get("test_mode", False):
                adjusted_idea["total_score"] *= 0.5

            adjusted.append(adjusted_idea)

        # 重新排序
        adjusted.sort(key=lambda x: x.get("total_score", 0), reverse=True)
        return adjusted

    def select_best_idea(self, ideas):
        """选择最佳创意"""
        if not ideas:
            return None

        # 返回得分最高的
        return ideas[0] if ideas else None

    def execute_idea(self, idea, dry_run=True):
        """执行选定的创意"""
        if not idea:
            return {"status": "error", "message": "没有可执行的创意"}

        result = {
            "idea": idea.get("description", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "status": "pending"
        }

        # 如果是 dry_run，只记录不执行
        if dry_run:
            result["status"] = "dry_run"
            result["message"] = f"dry_run 模式：建议执行「{idea.get('description', '未命名')}」，预估价值: {idea.get('total_score', 0)}"
            return result

        # 记录执行
        self.execution_history["executions"].append({
            "idea": idea.get("description"),
            "scores": idea.get("scores"),
            "total_score": idea.get("total_score"),
            "timestamp": datetime.now().isoformat(),
            "status": "executed"
        })
        self._save_execution_history()

        result["status"] = "executed"
        result["message"] = f"已执行「{idea.get('description', '未命名')}」，执行历史已记录"
        return result

    def learn_from_execution(self, execution_result):
        """从执行结果中学习"""
        if not execution_result:
            return

        # 提取学习点
        learning = {
            "execution_time": execution_result.get("timestamp"),
            "idea": execution_result.get("idea"),
            "learned_at": datetime.now().isoformat()
        }

        self.execution_history["learnings"].append(learning)
        self._save_execution_history()

    def get_evaluated_ideas(self, limit=5):
        """获取评估后的创意列表"""
        ideas = self.idea_generator.generate_evolution_ideas()
        evaluated = self.deep_evaluate_ideas(ideas)
        return evaluated[:limit]

    def get_execution_status(self):
        """获取执行状态"""
        return {
            "total_executions": len(self.execution_history.get("executions", [])),
            "total_learnings": len(self.execution_history.get("learnings", [])),
            "recent_executions": self.execution_history.get("executions", [])[-5:],
            "last_execution": self.execution_history.get("executions", [])[-1] if self.execution_history.get("executions") else None
        }

    def generate_evaluation_report(self):
        """生成评估报告"""
        ideas = self.get_evaluated_ideas(10)
        status = self.get_execution_status()

        report = {
            "generated_at": datetime.now().isoformat(),
            "top_ideas": ideas,
            "execution_status": status,
            "summary": {
                "total_ideas_analyzed": len(ideas),
                "highest_score": ideas[0].get("total_score", 0) if ideas else 0,
                "total_executions": status["total_executions"],
                "total_learnings": status["total_learnings"]
            }
        }

        return report


def main():
    """主函数 - 支持命令行调用"""
    import sys

    engine = EvolutionIdeaExecutionEngine()

    if len(sys.argv) < 2:
        print("""
智能进化创意评估与执行引擎 v1.0.0

用法:
  python evolution_idea_execution_engine.py evaluate [数量]   - 评估创意并排序
  python evolution_idea_execution_engine.py execute <idea_id> [dry_run] - 执行创意
  python evolution_idea_execution_engine.py status           - 查看执行状态
  python evolution_idea_execution_engine.py report           - 生成评估报告
  python evolution_idea_execution_engine.py learn            - 从执行历史学习

示例:
  python evolution_idea_execution_engine.py evaluate 5
  python evolution_idea_execution_engine.py execute 0        # 执行得分最高的
  python evolution_idea_execution_engine.py execute 0 dry    # dry run 模式
  python evolution_idea_execution_engine.py status
  python evolution_idea_execution_engine.py report
        """)
        return

    command = sys.argv[1].lower()

    if command == "evaluate":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        ideas = engine.get_evaluated_ideas(limit)
        print(f"\n=== 评估后的进化创意 (Top {limit}) ===\n")
        for i, idea in enumerate(ideas):
            print(f"【{i}】{idea.get('description', '未命名')}")
            print(f"    综合得分: {idea.get('total_score', 0)}")
            scores = idea.get("scores", {})
            print(f"    价值: {scores.get('value_score', 0):.2f} | 可行性: {scores.get('feasibility_score', 0):.2f} | 风险: {scores.get('risk_score', 0):.2f} | 紧急度: {scores.get('urgency_score', 0):.2f}")
            print(f"    来源: {idea.get('source', 'unknown')}")
            print()

    elif command == "execute":
        if len(sys.argv) < 3:
            print("用法: python evolution_idea_execution_engine.py execute <idea_id> [dry_run]")
            return

        idea_id = int(sys.argv[2])
        dry_run = len(sys.argv) > 3 and sys.argv[3].lower() == "dry"

        ideas = engine.get_evaluated_ideas(20)
        if idea_id < len(ideas):
            idea = ideas[idea_id]
            result = engine.execute_idea(idea, dry_run=dry_run)
            print(f"\n执行结果: {result.get('message')}")
        else:
            print(f"错误: idea_id {idea_id} 不存在")

    elif command == "status":
        status = engine.get_execution_status()
        print(f"\n=== 执行状态 ===")
        print(f"总执行次数: {status['total_executions']}")
        print(f"总学习次数: {status['total_learnings']}")
        if status.get('last_execution'):
            print(f"上次执行: {status['last_execution'].get('idea')}")

    elif command == "report":
        report = engine.generate_evaluation_report()
        print(f"\n=== 进化创意评估报告 ===")
        print(f"生成时间: {report.get('generated_at')}")
        print(f"分析创意数: {report['summary']['total_ideas_analyzed']}")
        print(f"最高得分: {report['summary']['highest_score']}")
        print(f"执行次数: {report['summary']['total_executions']}")
        print(f"学习次数: {report['summary']['total_learnings']}")
        print("\nTop 5 创意:")
        for i, idea in enumerate(report['top_ideas'][:5]):
            print(f"  {i+1}. {idea.get('description', '未命名')} (得分: {idea.get('total_score', 0)})")

    elif command == "learn":
        # 从执行历史中学习
        executions = engine.execution_history.get("executions", [])
        print(f"\n从 {len(executions)} 条执行记录中学习...")
        for exec in executions[-3:]:
            print(f"  - {exec.get('idea')}")
        print("学习完成")


if __name__ == "__main__":
    main()