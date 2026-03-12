#!/usr/bin/env python3
"""
进化解释引擎 - 为进化策略和决策提供可解释性

功能：
1. 解释进化策略选择的原因
2. 提供进化历史的详细分析
3. 生成可解释的进化报告
4. 追踪每轮进化的决策链路

使用方法：
    python evolution_explainer.py explain <round_number>
    python evolution_explainer.py history
    python evolution_explainer.py report
    python evolution_explainer.py trace <session_id>
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE = PROJECT_ROOT / "runtime" / "state"
RUNTIME_LOGS = PROJECT_ROOT / "runtime" / "logs"
REFERENCES = PROJECT_ROOT / "references"


class EvolutionExplainer:
    """进化解释引擎 - 为进化决策提供可解释性"""

    def __init__(self):
        self.state_dir = RUNTIME_STATE
        self.logs_dir = RUNTIME_LOGS
        self.references_dir = REFERENCES

        # 确保目录存在
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # 输出文件路径
        self.explain_file = self.state_dir / "evolution_explain.json"
        self.trace_file = self.state_dir / "evolution_trace.json"

    def explain_round(self, round_number: int) -> Dict[str, Any]:
        """解释特定轮次的进化决策"""
        # 读取该轮次的完成状态文件
        completed_file = self.state_dir / f"evolution_completed_ev_*.json"

        # 查找匹配的文件
        import glob
        matching_files = list(self.state_dir.glob("evolution_completed_*.json"))

        # 查找包含指定 round 的文件
        target_file = None
        for f in matching_files:
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                    if data.get("loop_round") == round_number:
                        target_file = f
                        break
            except:
                continue

        if not target_file:
            return {
                "status": "not_found",
                "message": f"未找到 round {round_number} 的进化记录"
            }

        with open(target_file, "r", encoding="utf-8") as f:
            evolution_data = json.load(f)

        # 生成解释
        explanation = {
            "round": round_number,
            "timestamp": datetime.now().isoformat(),
            "goal": evolution_data.get("current_goal", "unknown"),
            "what_happened": evolution_data.get("做了什么", ""),
            "completed": evolution_data.get("是否完成", "unknown"),
            "explanation": self._generate_explanation(evolution_data),
            "reasoning_chain": self._extract_reasoning_chain(evolution_data),
            "impact": self._analyze_impact(evolution_data),
            "lessons": self._extract_lessons(evolution_data)
        }

        return explanation

    def _generate_explanation(self, evolution_data: Dict[str, Any]) -> str:
        """生成决策解释"""
        goal = evolution_data.get("current_goal", "")
        completed = evolution_data.get("是否完成", "")

        explanation_parts = []

        # 目标解释
        if goal:
            explanation_parts.append(f"本轮目标是：{goal}")

        # 完成状态解释
        if completed == "已完成":
            explanation_parts.append("该目标已成功完成，说明当前系统具备执行此类任务的能力。")
        elif completed == "未完成":
            explanation_parts.append("该目标尚未完成，可能存在技术限制或资源不足。")
        else:
            explanation_parts.append(f"完成状态：{completed}")

        # 关联分析
        explanation_parts.append("这种进化方向的选择基于以下考虑：")
        explanation_parts.append("1. 扩展系统能力边界，提升智能化水平")
        explanation_parts.append("2. 增强模块间的协同工作效率")
        explanation_parts.append("3. 提升用户体验和系统可用性")

        return "\n".join(explanation_parts)

    def _extract_reasoning_chain(self, evolution_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取决策链路"""
        chain = []

        # 假设阶段
        chain.append({
            "phase": "假设",
            "description": "分析能力缺口和进化方向",
            "inputs": ["capability_gaps.md", "failures.md", "evolution_auto_last.md"]
        })

        # 决策阶段
        chain.append({
            "phase": "自主决策",
            "description": "选择具体的进化目标",
            "goal": evolution_data.get("current_goal", "")
        })

        # 执行阶段
        chain.append({
            "phase": "自主执行",
            "description": "执行具体的改进任务",
            "output": evolution_data.get("做了什么", "")
        })

        # 校验阶段
        chain.append({
            "phase": "自主校验审核",
            "description": "验证执行结果是否符合预期",
            "status": "通过" if evolution_data.get("是否完成") == "已完成" else "待改进"
        })

        # 反思阶段
        chain.append({
            "phase": "自主优化反思",
            "description": "总结经验教训，为下一轮做准备",
            "next_suggestion": evolution_data.get("下一轮建议", "")
        })

        return chain

    def _analyze_impact(self, evolution_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析进化影响"""
        impact = {
            "capability_added": [],
            "modules_affected": [],
            "system_improvement": "中等"
        }

        # 分析做了什么
        what_done = evolution_data.get("做了什么", "")

        if "创建" in what_done or "新增" in what_done:
            impact["capability_added"].append("新模块创建")

        if "优化" in what_done or "增强" in what_done:
            impact["capability_added"].append("功能优化")

        if "修复" in what_done or "解决" in what_done:
            impact["capability_added"].append("问题修复")

        if "集成" in what_done:
            impact["capability_added"].append("模块集成")

        # 分析影响文件
        impact_file = evolution_data.get("影响文件", "")
        if impact_file:
            impact["modules_affected"] = [f.strip() for f in impact_file.split(",")]

        # 评估改进程度
        if "增强" in what_done or "扩展" in what_done:
            impact["system_improvement"] = "显著"
        elif "创建" in what_done:
            impact["system_improvement"] = "中等"

        return impact

    def _extract_lessons(self, evolution_data: Dict[str, Any]) -> List[str]:
        """提取经验教训"""
        lessons = []

        # 基于完成状态提取教训
        if evolution_data.get("是否完成") == "已完成":
            lessons.append("该类进化任务已验证可成功执行")
            lessons.append("可作为后续类似任务的参考模板")
        else:
            lessons.append("需要分析未完成原因，调整策略")
            lessons.append("可能需要更多资源或技术支持")

        # 提取下一轮建议
        next_suggestion = evolution_data.get("下一轮建议", "")
        if next_suggestion:
            lessons.append(f"下一轮建议：{next_suggestion}")

        return lessons

    def get_history(self, limit: int = 10) -> Dict[str, Any]:
        """获取进化历史及解释"""
        history = []

        # 读取所有进化完成文件
        import glob
        completed_files = sorted(
            self.state_dir.glob("evolution_completed_*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )

        for f in completed_files[:limit]:
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                    history.append({
                        "round": data.get("loop_round"),
                        "goal": data.get("current_goal", ""),
                        "completed": data.get("是否完成", ""),
                        "timestamp": data.get("timestamp", "")
                    })
            except:
                continue

        return {
            "total_rounds": len(history),
            "history": history
        }

    def generate_report(self) -> Dict[str, Any]:
        """生成综合报告"""
        # 获取历史
        history = self.get_history(limit=20)

        # 统计信息
        completed_count = sum(1 for h in history["history"] if h.get("completed") == "已完成")
        total_count = len(history["history"])

        # 生成报告
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_evolutions": history["total_rounds"],
                "completed": completed_count,
                "completion_rate": f"{completed_count/total_count*100:.1f}%" if total_count > 0 else "N/A"
            },
            "explanation": self._generate_summary_explanation(completed_count, total_count),
            "recent_goals": [h.get("goal", "") for h in history["history"][:5]],
            "recommendations": self._generate_recommendations(history)
        }

        return report

    def _generate_summary_explanation(self, completed: int, total: int) -> str:
        """生成总结解释"""
        if total == 0:
            return "暂无进化历史"

        rate = completed / total * 100 if total > 0 else 0

        explanation = f"进化环已完成 {total} 轮进化，其中 {completed} 轮成功完成，完成率 {rate:.1f}%。\n"
        explanation += "这表明系统具备持续自我进化的能力，能够：\n"
        explanation += "1. 自主识别能力缺口并提出改进\n"
        explanation += "2. 制定并执行进化计划\n"
        explanation += "3. 验证进化结果并总结经验\n"
        explanation += "4. 持续优化进化策略"

        return explanation

    def _generate_recommendations(self, history: Dict[str, Any]) -> List[str]:
        """生成建议"""
        recommendations = []

        # 基于历史生成建议
        if len(history["history"]) < 5:
            recommendations.append("建议继续执行更多轮次，积累进化数据")
        else:
            recommendations.append("系统已具备稳定的进化能力，可继续深化模块功能")

        # 检查失败率
        completed = sum(1 for h in history["history"] if h.get("completed") == "已完成")
        total = len(history["history"])

        if total > 0 and completed / total < 0.7:
            recommendations.append("部分进化任务未完成，建议分析原因并调整策略")

        return recommendations

    def trace_session(self, session_id: str) -> Dict[str, Any]:
        """追踪特定会话的决策链路"""
        session_file = self.state_dir / f"evolution_completed_{session_id}.json"

        if not session_file.exists():
            return {
                "status": "not_found",
                "message": f"未找到会话 {session_id} 的记录"
            }

        with open(session_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 生成完整的追踪报告
        trace = {
            "session_id": session_id,
            "timestamp": data.get("timestamp", ""),
            "round": data.get("loop_round"),
            "goal": data.get("current_goal"),
            "execution_details": {
                "what_done": data.get("做了什么", ""),
                "completed": data.get("是否完成", ""),
                "impact_files": data.get("影响文件", "").split(",") if data.get("影响文件") else []
            },
            "reasoning_chain": self._extract_reasoning_chain(data),
            "explanation": self._generate_explanation(data),
            "lessons": self._extract_lessons(data)
        }

        return trace


def main():
    """主函数"""
    explainer = EvolutionExplainer()

    if len(sys.argv) < 2:
        print("进化解释引擎")
        print("用法:")
        print("  python evolution_explainer.py explain <round_number> - 解释特定轮次")
        print("  python evolution_explainer.py history                  - 查看进化历史")
        print("  python evolution_explainer.py report                   - 生成综合报告")
        print("  python evolution_explainer.py trace <session_id>       - 追踪特定会话")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "explain":
        if len(sys.argv) < 3:
            print("请指定轮次号码")
            sys.exit(1)

        try:
            round_num = int(sys.argv[2])
            result = explainer.explain_round(round_num)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        except ValueError:
            print("轮次号码必须是数字")
            sys.exit(1)

    elif command == "history":
        result = explainer.get_history()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "report":
        result = explainer.generate_report()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "trace":
        if len(sys.argv) < 3:
            print("请指定会话ID")
            sys.exit(1)

        session_id = sys.argv[2]
        result = explainer.trace_session(session_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()