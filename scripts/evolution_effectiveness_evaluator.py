#!/usr/bin/env python3
"""
智能进化效果自动评估引擎
用于评估每轮进化的实际价值，识别高价值/低价值/重复改进，生成进化效率报告和优化建议

功能：
1. 分析每轮进化创建的模块/能力，评估其实际价值
2. 识别重复改进和低价值轮次
3. 生成进化效率评分和趋势分析
4. 提供优化建议
5. 集成到 do.py 支持「进化评估」「效果评估」「效率评估」等关键词触发

使用方法：
    python evolution_effectiveness_evaluator.py evaluate
    python evolution_effectiveness_evaluator.py report
    python evolution_effectiveness_evaluator.py trends
    python evolution_effectiveness_evaluator.py value <round_id>
"""

import json
import os
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from collections import Counter, defaultdict

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE = PROJECT_ROOT / "runtime" / "state"
RUNTIME_LOGS = PROJECT_ROOT / "runtime" / "logs"
REFERENCES = PROJECT_ROOT / "references"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"


class EvolutionEffectivenessEvaluator:
    """进化效果评估器 - 评估每轮进化的实际价值"""

    # 关键词权重：不同类型的改进有不同的价值权重
    VALUE_KEYWORDS = {
        # 高价值关键词
        "高": [
            "引擎", "核心", "闭环", "自主", "智能", "统一", "自适应",
            "协同", "协作", "决策", "预测", "分析", "优化", "学习",
            "创新", "突破", "自动化", "集成", "深度"
        ],
        # 中等价值关键词
        "中": [
            "增强", "扩展", "改进", "完善", "支持", "添加", "实现",
            "功能", "能力", "服务", "接口", "模块"
        ],
        # 低价值关键词
        "低": [
            "修复", "调整", "优化", "精简", "清理", "文档"
        ]
    }

    def __init__(self):
        self.state_dir = RUNTIME_STATE
        self.logs_dir = RUNTIME_LOGS
        self.references_dir = REFERENCES
        self.scripts_dir = SCRIPTS_DIR

        # 评估结果输出路径
        self.evaluation_file = self.state_dir / "evolution_effectiveness_evaluation.json"
        self.evaluation_history_file = self.state_dir / "evolution_effectiveness_history.json"

        # 确保目录存在
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def evaluate_all(self) -> Dict[str, Any]:
        """评估所有进化轮次的效果"""
        evaluation = {
            "timestamp": datetime.now().isoformat(),
            "total_rounds": 0,
            "high_value_rounds": [],
            "medium_value_rounds": [],
            "low_value_rounds": [],
            "duplicate_rounds": [],
            "value_distribution": {},
            "trend_analysis": {},
            "recommendations": []
        }

        # 收集所有进化完成文件
        completed_files = sorted(self.state_dir.glob("evolution_completed_*.json"))
        evaluation["total_rounds"] = len(completed_files)

        # 评估每轮
        round_analyses = []
        created_modules = set()  # 追踪已创建的模块，检测重复

        for f in completed_files:
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    analysis = self._analyze_round(data, created_modules)
                    round_analyses.append(analysis)

                    # 检测重复
                    if analysis.get("is_duplicate"):
                        evaluation["duplicate_rounds"].append({
                            "round_id": data.get("loop_round", "unknown"),
                            "reason": analysis.get("duplicate_reason", ""),
                            "similar_to": analysis.get("similar_to", "")
                        })

                    # 分类
                    value_level = analysis.get("value_level", "中")
                    round_info = {
                        "round_id": data.get("loop_round", "unknown"),
                        "goal": data.get("current_goal", ""),
                        "value_score": analysis.get("value_score", 0),
                        "modules_created": analysis.get("modules_created", [])
                    }

                    if value_level == "高":
                        evaluation["high_value_rounds"].append(round_info)
                    elif value_level == "中":
                        evaluation["medium_value_rounds"].append(round_info)
                    else:
                        evaluation["low_value_rounds"].append(round_info)

                    # 更新已创建模块集合
                    for mod in analysis.get("modules_created", []):
                        created_modules.add(mod)

            except Exception as e:
                print(f"分析文件 {f} 时出错: {e}", file=sys.stderr)

        # 计算价值分布
        evaluation["value_distribution"] = {
            "高价值": len(evaluation["high_value_rounds"]),
            "中等价值": len(evaluation["medium_value_rounds"]),
            "低价值": len(evaluation["low_value_rounds"]),
            "重复": len(evaluation["duplicate_rounds"])
        }

        # 趋势分析
        evaluation["trend_analysis"] = self._analyze_trends(round_analyses)

        # 生成优化建议
        evaluation["recommendations"] = self._generate_recommendations(evaluation)

        return evaluation

    def _analyze_round(self, data: Dict[str, Any], existing_modules: Set[str]) -> Dict[str, Any]:
        """分析单轮进化"""
        goal = data.get("current_goal", "")

        # 处理「做了什么」字段，可能是字符串或列表
        track_desc_raw = data.get("做了什么", "")
        if isinstance(track_desc_raw, list):
            track_desc = " ".join(str(item) for item in track_desc_raw)
        else:
            track_desc = str(track_desc_raw) if track_desc_raw else ""

        loop_round = data.get("loop_round", 0)

        analysis = {
            "round_id": loop_round,
            "goal": goal,
            "value_score": 0,
            "value_level": "中",
            "modules_created": [],
            "is_duplicate": False,
            "duplicate_reason": "",
            "similar_to": ""
        }

        # 1. 计算价值分数
        score = 0

        # 基于目标关键词计算分数
        for keyword in self.VALUE_KEYWORDS["高"]:
            if keyword in goal:
                score += 10

        for keyword in self.VALUE_KEYWORDS["中"]:
            if keyword in goal:
                score += 5

        for keyword in self.VALUE_KEYWORDS["低"]:
            if keyword in goal:
                score += 2

        # 2. 提取创建的模块
        modules = self._extract_modules(track_desc)
        analysis["modules_created"] = modules

        # 3. 检测重复
        for mod in modules:
            if mod in existing_modules:
                analysis["is_duplicate"] = True
                analysis["duplicate_reason"] = f"模块 {mod} 已在之前的轮次中创建"
                analysis["similar_to"] = "之前轮次"
                score = max(score - 10, 0)  # 重复改进扣分

        # 4. 基于是否完成
        if data.get("status") == "completed":
            score += 5

        # 5. 基于是否有具体实现
        if "创建" in track_desc or "实现" in track_desc:
            score += 3

        analysis["value_score"] = score

        # 6. 确定价值等级
        if score >= 20:
            analysis["value_level"] = "高"
        elif score >= 10:
            analysis["value_level"] = "中"
        else:
            analysis["value_level"] = "低"

        return analysis

    def _extract_modules(self, text: str) -> List[str]:
        """从描述中提取创建的模块名"""
        modules = []

        # 匹配 .py 文件
        py_files = re.findall(r'(\w+\.py)', text)
        modules.extend(py_files)

        # 匹配创建/实现/添加的 xxx.py/xxx_engine/xxx_module 等
        patterns = [
            r'(?:创建|实现|添加|开发)\s+(\w+(?:_engine|_module|_tool|_engine))\.py',
            r'(\w+(?:_engine|_module|_tool)\.py)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            modules.extend(matches)

        # 去重
        return list(set(modules))

    def _analyze_trends(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析进化趋势"""
        if not analyses:
            return {}

        # 按时间分组
        recent_10 = analyses[-10:] if len(analyses) >= 10 else analyses

        avg_score = sum(a.get("value_score", 0) for a in recent_10) / len(recent_10)

        high_count = sum(1 for a in recent_10 if a.get("value_level") == "高")
        medium_count = sum(1 for a in recent_10 if a.get("value_level") == "中")
        low_count = sum(1 for a in recent_10 if a.get("value_level") == "低")

        return {
            "avg_value_score": round(avg_score, 2),
            "recent_10_high_value": high_count,
            "recent_10_medium_value": medium_count,
            "recent_10_low_value": low_count,
            "trend": "上升" if avg_score >= 15 else "平稳" if avg_score >= 10 else "下降"
        }

    def _generate_recommendations(self, evaluation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成优化建议"""
        recommendations = []

        # 基于重复检测
        if len(evaluation.get("duplicate_rounds", [])) > 5:
            recommendations.append({
                "category": "optimization",
                "priority": "high",
                "issue": "存在较多重复改进",
                "suggestion": "在进化前检查已创建的模块，避免重复开发类似功能"
            })

        # 基于价值分布
        dist = evaluation.get("value_distribution", {})
        low_ratio = dist.get("低价值", 0) / max(dist.get("total_rounds", 1), 1)

        if low_ratio > 0.3:
            recommendations.append({
                "category": "quality",
                "priority": "medium",
                "issue": "低价值改进占比过高",
                "suggestion": "增加高价值进化方向，如跨引擎集成、元进化能力、自适应学习等"
            })

        # 基于趋势
        trend = evaluation.get("trend_analysis", {})
        if trend.get("trend") == "下降":
            recommendations.append({
                "category": "strategy",
                "priority": "high",
                "issue": "进化价值呈下降趋势",
                "suggestion": "考虑更大胆的创新方向，或进行架构层面的改进"
            })

        if trend.get("avg_value_score", 0) >= 15:
            recommendations.append({
                "category": "strategy",
                "priority": "low",
                "issue": "进化效果良好",
                "suggestion": "当前进化策略有效，可保持或探索新方向"
            })

        return recommendations

    def evaluate_single(self, round_id: str) -> Dict[str, Any]:
        """评估单个进化轮次"""
        # 查找对应的完成文件
        pattern = f"evolution_completed_*{round_id}*.json"

        # 尝试多种模式
        candidates = []
        for pattern in [
            f"evolution_completed_{round_id}.json",
            f"evolution_completed_*{round_id}*.json"
        ]:
            candidates.extend(self.state_dir.glob(pattern))

        if not candidates:
            return {
                "status": "not_found",
                "message": f"未找到轮次 {round_id} 的记录"
            }

        try:
            with open(candidates[0], 'r', encoding='utf-8') as fp:
                data = json.load(fp)

            analysis = self._analyze_round(data, set())

            return {
                "status": "success",
                "round_id": round_id,
                "analysis": analysis
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"分析失败: {str(e)}"
            }

    def get_trends(self) -> Dict[str, Any]:
        """获取进化趋势"""
        evaluation = self.evaluate_all()
        return evaluation.get("trend_analysis", {})

    def save_evaluation(self, evaluation: Dict[str, Any]) -> None:
        """保存评估结果"""
        with open(self.evaluation_file, "w", encoding="utf-8") as f:
            json.dump(evaluation, f, ensure_ascii=False, indent=2)

    def get_evaluation(self) -> Dict[str, Any]:
        """获取当前评估结果"""
        if self.evaluation_file.exists():
            with open(self.evaluation_file, "r", encoding="utf-8") as f:
                return json.load(f)

        return {
            "status": "no_evaluation",
            "message": "请先运行 evaluate 命令生成评估报告"
        }


def main():
    """主函数"""
    evaluator = EvolutionEffectivenessEvaluator()

    if len(sys.argv) < 2:
        print("智能进化效果自动评估引擎")
        print("用法:")
        print("  python evolution_effectiveness_evaluator.py evaluate  - 评估所有进化轮次")
        print("  python evolution_effectiveness_evaluator.py report    - 获取完整报告")
        print("  python evolution_effectiveness_evaluator.py trends   - 获取趋势分析")
        print("  python evolution_effectiveness_evaluator.py value <round_id> - 评估单个轮次")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "evaluate":
        result = evaluator.evaluate_all()
        evaluator.save_evaluation(result)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "report":
        result = evaluator.evaluate_all()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "trends":
        result = evaluator.get_trends()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "value":
        if len(sys.argv) < 3:
            print("请指定轮次 ID")
            sys.exit(1)
        round_id = sys.argv[2]
        result = evaluator.evaluate_single(round_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()