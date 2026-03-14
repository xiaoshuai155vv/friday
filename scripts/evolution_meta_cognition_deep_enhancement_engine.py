#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环元认知深度增强引擎 (Evolution Meta-Cognition Deep Enhancement Engine)
Round 316: 让系统对自身认知过程进行递归式深度反思，实现「学会思考如何思考」的递归认知升级

核心功能：
1. 元认知分析：分析系统自身的思考过程、决策模式
2. 认知深度评估：评估当前认知的深度和广度
3. 认知优化建议：生成优化自身认知过程的建议
4. 递归反思：实现元认知的元认知

作者：Friday AI Evolution System
版本：1.0.0
"""

import os
import sys

# 解决 Windows GBK 控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"


class EvolutionMetaCognitionDeepEnhancementEngine:
    """进化环元认知深度增强引擎"""

    def __init__(self):
        self.state_file = STATE_DIR / "evolution_meta_cognition_state.json"
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "last_analysis_time": None,
            "analysis_history": [],
            "cognitive_patterns": {},
            "depth_evaluations": [],
            "optimization_suggestions": [],
            "recursive_reflection_count": 0,
            "total_thoughts_analyzed": 0,
            "meta_cognition_level": 0.0
        }

    def _save_state(self):
        """保存状态"""
        try:
            STATE_DIR.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[EvolutionMetaCognition] 保存状态失败: {e}")

    def analyze_meta_cognition(self) -> Dict[str, Any]:
        """
        执行元认知深度分析
        分析系统自身的思考过程、决策模式
        """
        print("\n=== 元认知深度分析 ===")

        # 1. 收集认知数据
        cognitive_data = self._collect_cognitive_data()

        # 2. 分析思维模式
        patterns = self._analyze_thinking_patterns(cognitive_data)

        # 3. 评估认知深度
        depth_evaluation = self._evaluate_cognitive_depth(patterns)

        # 4. 执行递归反思
        recursive_insight = self._recursive_reflection(depth_evaluation)

        # 5. 生成分析报告
        analysis_report = {
            "timestamp": datetime.now().isoformat(),
            "total_thoughts_analyzed": len(cognitive_data.get("thought_records", [])),
            "patterns": patterns,
            "depth_evaluation": depth_evaluation,
            "recursive_insight": recursive_insight,
            "optimization_suggestions": self._generate_optimization_suggestions(patterns, depth_evaluation)
        }

        # 保存到历史
        self.state["last_analysis_time"] = analysis_report["timestamp"]
        self.state["analysis_history"].append(analysis_report)
        self.state["total_thoughts_analyzed"] += len(cognitive_data.get("thought_records", []))
        self.state["cognitive_patterns"] = patterns
        self.state["depth_evaluations"].append(depth_evaluation)
        self.state["recursive_reflection_count"] += 1
        self.state["meta_cognition_level"] = depth_evaluation.get("overall_depth", 0.0)
        self._save_state()

        return analysis_report

    def _collect_cognitive_data(self) -> Dict:
        """收集认知数据"""
        thought_records = []

        # 1. 读取进化决策日志
        if LOGS_DIR.exists():
            for f in LOGS_DIR.glob("behavior_*.log"):
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        lines = fp.readlines()
                        for line in lines[-300:]:  # 最近300行
                            try:
                                # 提取决策类日志
                                if "decide" in line.lower() or "plan" in line.lower():
                                    thought_records.append({
                                        "type": "decision",
                                        "content": line.strip()[:200],
                                        "timestamp": datetime.now().isoformat()
                                    })
                                elif "assume" in line.lower():
                                    thought_records.append({
                                        "type": "assumption",
                                        "content": line.strip()[:200],
                                        "timestamp": datetime.now().isoformat()
                                    })
                            except Exception:
                                pass
                except Exception:
                    pass

        # 2. 读取进化完成记录
        evolution_records = []
        if STATE_DIR.exists():
            for f in STATE_DIR.glob("evolution_completed_ev_*.json"):
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        evolution_records.append(data)
                except Exception:
                    pass

        return {
            "thought_records": thought_records[-50:],  # 最近50条
            "evolution_records": sorted(evolution_records, key=lambda x: x.get("timestamp", ""), reverse=True)[:30]
        }

    def _analyze_thinking_patterns(self, data: Dict) -> Dict[str, Any]:
        """分析思维模式"""
        thoughts = data.get("thought_records", [])
        evolutions = data.get("evolution_records", [])

        # 1. 分析决策频率
        decision_count = sum(1 for t in thoughts if t.get("type") == "decision")
        assumption_count = sum(1 for t in thoughts if t.get("type") == "assumption")

        # 2. 分析进化领域分布
        domain_distribution = defaultdict(int)
        for e in evolutions:
            goal = e.get("current_goal", "")
            if "引擎" in goal or "engine" in goal.lower():
                domain_distribution["引擎开发"] += 1
            elif "优化" in goal:
                domain_distribution["优化改进"] += 1
            elif "智能" in goal:
                domain_distribution["智能增强"] += 1
            elif "自动" in goal:
                domain_distribution["自动化"] += 1
            else:
                domain_distribution["其他"] += 1

        # 3. 分析决策模式
        decision_patterns = {
            "data_driven": decision_count > assumption_count,
            "hypothesis_based": assumption_count > 0,
            "balance_ratio": decision_count / (assumption_count + 1),
            "recent_domains": list(domain_distribution.keys())[:5]
        }

        # 4. 检测思维惯性
        inertia = self._detect_thinking_inertia(evolutions)

        # 5. 评估反思深度
        reflection_depth = self._evaluate_reflection_depth(thoughts)

        return {
            "decision_count": decision_count,
            "assumption_count": assumption_count,
            "domain_distribution": dict(domain_distribution),
            "decision_patterns": decision_patterns,
            "thinking_inertia": inertia,
            "reflection_depth": reflection_depth,
            "total_records": len(thoughts) + len(evolutions)
        }

    def _detect_thinking_inertia(self, evolutions: List[Dict]) -> Dict[str, Any]:
        """检测思维惯性"""
        if len(evolutions) < 5:
            return {"detected": False, "reason": "数据不足"}

        # 检查最近进化是否有重复领域
        recent_domains = []
        for e in evolutions[:10]:
            goal = e.get("current_goal", "")
            if "元" in goal or "meta" in goal.lower():
                recent_domains.append("元进化")
            elif "自" in goal:
                recent_domains.append("自我增强")
            elif "智能" in goal:
                recent_domains.append("智能")
            else:
                recent_domains.append("其他")

        # 计算连续重复
        repeats = 0
        for i in range(1, len(recent_domains)):
            if recent_domains[i] == recent_domains[i-1]:
                repeats += 1

        return {
            "detected": repeats > 4,
            "repeat_count": repeats,
            "description": "检测到思维惯性" if repeats > 4 else "思维模式多样"
        }

    def _evaluate_reflection_depth(self, thoughts: List[Dict]) -> Dict[str, Any]:
        """评估反思深度"""
        # 基于日志中是否有多种类型的思考
        types = set(t.get("type", "") for t in thoughts)

        # 深度评分
        depth_score = min(1.0, len(types) / 4)  # 最多4种类型

        return {
            "diversity_score": len(types),
            "depth_score": depth_score,
            "assessment": "深入" if depth_score > 0.7 else "一般" if depth_score > 0.4 else "浅层"
        }

    def _evaluate_cognitive_depth(self, patterns: Dict) -> Dict[str, Any]:
        """评估认知深度"""
        # 多维度评估
        dimensions = {
            "pattern_recognition": min(1.0, patterns.get("total_records", 0) / 100),
            "decision_balance": min(1.0, patterns.get("decision_patterns", {}).get("balance_ratio", 0) / 2),
            "diversity": min(1.0, len(patterns.get("domain_distribution", {})) / 5),
            "reflection_depth": patterns.get("reflection_depth", {}).get("depth_score", 0),
            "inertia_awareness": 0.5 if patterns.get("thinking_inertia", {}).get("detected") else 1.0
        }

        # 计算综合深度
        overall_depth = sum(dimensions.values()) / len(dimensions)

        # 深度等级
        if overall_depth >= 0.8:
            level = "卓越"
        elif overall_depth >= 0.6:
            level = "优秀"
        elif overall_depth >= 0.4:
            level = "良好"
        else:
            level = "基础"

        return {
            "dimensions": dimensions,
            "overall_depth": overall_depth,
            "level": level,
            "description": f"元认知深度 {level}级 ({overall_depth:.2f})"
        }

    def _recursive_reflection(self, depth_evaluation: Dict) -> Dict[str, Any]:
        """
        执行递归反思
        对自身认知过程本身的思考
        """
        print("\n--- 递归反思：思考如何思考 ---")

        overall = depth_evaluation.get("overall_depth", 0)
        level = depth_evaluation.get("level", "基础")

        # 递归层级分析
        recursive_insights = []

        # 第一层：反思当前思考
        if overall > 0.3:
            recursive_insights.append({
                "layer": 1,
                "description": "已具备基本自我反思能力",
                "confidence": 0.8
            })

        # 第二层：反思思考模式
        if overall > 0.5:
            recursive_insights.append({
                "layer": 2,
                "description": "能够识别自身思维模式惯性",
                "confidence": 0.7
            })

        # 第三层：优化思考过程
        if overall > 0.7:
            recursive_insights.append({
                "layer": 3,
                "description": "能够主动优化认知过程",
                "confidence": 0.6
            })

        # 第四层：元认知循环
        if overall > 0.85:
            recursive_insights.append({
                "layer": 4,
                "description": "实现元认知的递归循环，持续自我提升",
                "confidence": 0.5
            })

        return {
            "max_layer": len(recursive_insights),
            "insights": recursive_insights,
            "meta_cognition_capability": level,
            "recursive_depth": overall
        }

    def _generate_optimization_suggestions(self, patterns: Dict, depth: Dict) -> List[str]:
        """生成认知优化建议"""
        suggestions = []

        # 基于思维惯性
        if patterns.get("thinking_inertia", {}).get("detected"):
            suggestions.append("建议：打破思维惯性，主动探索新的进化方向")

        # 基于决策平衡
        balance = patterns.get("decision_patterns", {}).get("balance_ratio", 0)
        if balance > 3:
            suggestions.append("建议：增加假设验证比例，提高决策质量")
        elif balance < 0.3:
            suggestions.append("建议：增加数据驱动决策，减少纯假设")

        # 基于多样性
        if len(patterns.get("domain_distribution", {})) < 3:
            suggestions.append("建议：扩展进化领域多样性，避免单一方向过度进化")

        # 基于反思深度
        if depth.get("overall_depth", 0) < 0.5:
            suggestions.append("建议：深化元认知能力，加强自我反思")

        if not suggestions:
            suggestions.append("元认知能力运行良好，继续保持")

        return suggestions

    def get_meta_cognition_status(self) -> Dict[str, Any]:
        """获取元认知状态"""
        latest_eval = self.state["depth_evaluations"][-1] if self.state["depth_evaluations"] else {}
        latest_insight = self.state["analysis_history"][-1].get("recursive_insight", {}) if self.state["analysis_history"] else {}

        return {
            "version": self.state["version"],
            "last_analysis_time": self.state["last_analysis_time"],
            "total_analyses": len(self.state["analysis_history"]),
            "recursive_reflection_count": self.state["recursive_reflection_count"],
            "total_thoughts_analyzed": self.state["total_thoughts_analyzed"],
            "meta_cognition_level": self.state["meta_cognition_level"],
            "current_depth": latest_eval.get("description", "未评估"),
            "max_recursive_layer": latest_insight.get("max_layer", 0)
        }

    def meta_cognition_dashboard(self) -> str:
        """生成元认知仪表盘"""
        status = self.get_meta_cognition_status()

        level = status.get("meta_cognition_level", 0)
        if level >= 0.8:
            color = "[卓越]"
        elif level >= 0.6:
            color = "[优秀]"
        elif level >= 0.4:
            color = "[良好]"
        else:
            color = "[基础]"

        dashboard = f"""
╔══════════════════════════════════════════════════════════════════╗
║     进化环元认知深度增强引擎 (Round 316)                          ║
╠══════════════════════════════════════════════════════════════════╣
║  版本: {status['version']}                                                      ║
║  状态: {color} {status['current_depth']}                                    ║
╠══════════════════════════════════════════════════════════════════╣
║  [统计] 元认知统计                                                  ║
║     分析次数: {status['total_analyses']}                                                      ║
║     递归反思: {status['recursive_reflection_count']} 次                                          ║
║     思考记录: {status['total_thoughts_analyzed']}                                            ║
║     递归层级: {status['max_recursive_layer']} 层                                            ║
╚══════════════════════════════════════════════════════════════════╝
"""
        return dashboard

    def deep_think(self, topic: str = None) -> Dict[str, Any]:
        """
        深度思考：对特定主题进行元认知分析
        """
        print(f"\n=== 深度思考：{topic or '系统认知过程'} ===")

        # 分析认知数据
        cognitive_data = self._collect_cognitive_data()

        # 分析思维模式
        patterns = self._analyze_thinking_patterns(cognitive_data)

        # 评估深度
        depth_evaluation = self._evaluate_cognitive_depth(patterns)

        # 递归反思
        recursive_insight = self._recursive_reflection(depth_evaluation)

        # 生成洞察
        insight = {
            "topic": topic or "系统认知过程",
            "timestamp": datetime.now().isoformat(),
            "patterns": patterns,
            "depth_evaluation": depth_evaluation,
            "recursive_insight": recursive_insight,
            "key_findings": self._extract_key_findings(patterns, depth_evaluation)
        }

        return insight

    def _extract_key_findings(self, patterns: Dict, depth: Dict) -> List[str]:
        """提取关键发现"""
        findings = []

        # 基于模式发现
        inertia = patterns.get("thinking_inertia", {})
        if inertia.get("detected"):
            findings.append(f"发现思维惯性：连续 {inertia.get('repeat_count', 0)} 次相似方向")

        # 基于深度发现
        if depth.get("overall_depth", 0) > 0.6:
            findings.append(f"元认知能力{depth.get('level', '良好')}")

        # 基于多样性发现
        if len(patterns.get("domain_distribution", {})) > 4:
            findings.append("进化方向多样性良好")

        return findings


# ==================== CLI 接口 ====================

def main():
    """CLI 入口"""
    import sys

    engine = EvolutionMetaCognitionDeepEnhancementEngine()

    if len(sys.argv) < 2:
        # 默认显示状态
        print(engine.meta_cognition_dashboard())
        print("\n用法:")
        print("  python evolution_meta_cognition_deep_enhancement_engine.py analyze   - 执行元认知分析")
        print("  python evolution_meta_cognition_deep_enhancement_engine.py think     - 深度思考")
        print("  python evolution_meta_cognition_deep_enhancement_engine.py status    - 查看状态")
        return

    command = sys.argv[1]

    if command == "analyze":
        result = engine.analyze_meta_cognition()
        print("\n元认知分析报告:")
        print(f"  分析记录: {result['total_thoughts_analyzed']}")
        print(f"  认知深度: {result['depth_evaluation']['description']}")
        print(f"  递归层级: {result['recursive_insight']['max_layer']}")
        print("\n优化建议:")
        for suggestion in result["optimization_suggestions"]:
            print(f"  - {suggestion}")

    elif command == "think":
        topic = sys.argv[2] if len(sys.argv) > 2 else None
        result = engine.deep_think(topic)
        print("\n深度思考结果:")
        print(f"  主题: {result['topic']}")
        print(f"  认知深度: {result['depth_evaluation']['description']}")
        print("\n关键发现:")
        for finding in result.get("key_findings", []):
            print(f"  - {finding}")

    elif command == "status":
        print(engine.meta_cognition_dashboard())

    else:
        print(f"未知命令: {command}")


if __name__ == "__main__":
    main()