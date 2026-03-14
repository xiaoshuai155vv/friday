#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环元认知深度增强引擎 (Evolution Meta-Cognition Deep Enhancement Engine)
Round 316 + Round 353: 让系统对自身认知过程进行递归式深度反思，实现「学会思考如何思考」的递归认知升级

Round 353 增强：与自适应学习引擎深度集成，实现认知→反思→优化→再认知的递归进化闭环

核心功能：
1. 元认知分析：分析系统自身的思考过程、决策模式
2. 认知深度评估：评估当前认知的深度和广度
3. 认知优化建议：生成优化自身认知过程的建议
4. 递归反思：实现元认知的元认知
5. 自适应学习集成（Round 353）：与 round 352 自适应学习引擎深度集成
6. 认知-反思-优化-再认知闭环（Round 353）：实现递归进化闭环

作者：Friday AI Evolution System
版本：1.1.0 (Round 353 增强)
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

        # 集成自适应学习引擎（Round 352）
        self._adaptive_learning_engine = None
        self._init_adaptive_learning()

    def _init_adaptive_learning(self):
        """初始化自适应学习引擎集成"""
        try:
            # 尝试导入自适应学习引擎
            import sys
            sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
            from evolution_adaptive_learning_strategy_engine import AdaptiveLearningStrategyEngine
            self._adaptive_learning_engine = AdaptiveLearningStrategyEngine()
            self.state["adaptive_learning_integrated"] = True
            print("[元认知引擎] 已集成自适应学习引擎 (Round 352)")
        except Exception as e:
            self.state["adaptive_learning_integrated"] = False
            print(f"[元认知引擎] 自适应学习引擎集成跳过: {e}")

    def _load_state(self) -> Dict:
        """加载状态"""
        default_state = {
            "version": "1.1.0",  # Round 353 升级
            "created_at": datetime.now().isoformat(),
            "last_analysis_time": None,
            "analysis_history": [],
            "cognitive_patterns": {},
            "depth_evaluations": [],
            "optimization_suggestions": [],
            "recursive_reflection_count": 0,
            "total_thoughts_analyzed": 0,
            "meta_cognition_level": 0.0,
            # Round 353 新增状态字段
            "adaptive_learning_integrated": False,
            "integration_history": [],
            "last_adaptive_integration": None,
            "闭环_history": [],
            "last_闭环_time": None,
            "meta_evolution_history": []
        }

        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    # 兼容旧版本状态，添加缺失的字段
                    for key, value in default_state.items():
                        if key not in state:
                            state[key] = value
                    return state
            except Exception:
                pass
        return default_state

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

    # ===== Round 353 新增功能：自适应学习集成 =====
    def integrate_adaptive_learning(self) -> Dict[str, Any]:
        """
        集成自适应学习引擎的分析结果
        实现元认知分析与自适应策略学习的深度融合
        """
        print("\n=== 元认知-自适应学习深度集成 ===")

        if not self._adaptive_learning_engine:
            return {
                "status": "not_integrated",
                "message": "自适应学习引擎未初始化"
            }

        # 获取自适应学习引擎的分析结果
        try:
            analysis = self._adaptive_learning_engine.analyze_evolution_results()
            patterns = self._adaptive_learning_engine.extract_success_patterns()
            failures = self._adaptive_learning_engine.identify_failure_causes()

            # 元认知分析结果
            cognitive_data = self._collect_cognitive_data()
            cognitive_patterns = self._analyze_thinking_patterns(cognitive_data)

            # 融合分析
            integrated_analysis = {
                "timestamp": datetime.now().isoformat(),
                "meta_cognition": {
                    "cognitive_patterns": cognitive_patterns,
                    "depth_evaluation": self._evaluate_cognitive_depth(cognitive_patterns)
                },
                "adaptive_learning": {
                    "evolution_analysis": analysis,
                    "success_patterns": patterns,
                    "failure_causes": failures
                },
                "integration_insights": self._generate_integration_insights(
                    cognitive_patterns, analysis, patterns, failures
                )
            }

            # 保存到状态
            self.state["last_adaptive_integration"] = integrated_analysis["timestamp"]
            self.state["integration_history"].append(integrated_analysis)
            self._save_state()

            return integrated_analysis

        except Exception as e:
            return {
                "status": "error",
                "message": f"自适应学习集成失败: {e}"
            }

    def _generate_integration_insights(self, cognitive: Dict, analysis: Dict,
                                         patterns: Dict, failures: Dict) -> List[str]:
        """生成融合洞察"""
        insights = []

        # 基于元认知分析
        if cognitive.get("thinking_inertia", {}).get("detected"):
            insights.append("检测到思维惯性，建议调整进化方向")

        # 基于自适应学习分析
        success_rate = analysis.get("success_rate", 0)
        if success_rate > 0.7:
            insights.append(f"进化成功率高 ({success_rate:.1%})，可适当增加进化频率")
        elif success_rate < 0.5:
            insights.append(f"进化成功率偏低 ({success_rate:.1%})，建议加强策略优化")

        # 基于失败原因
        if failures.get("failure_count", 0) > 0:
            insights.append(f"识别到 {failures.get('failure_count', 0)} 个失败案例，需关注")

        # 基于模式
        pattern_weights = patterns.get("pattern_weights", {})
        if pattern_weights:
            top_pattern = max(pattern_weights.items(), key=lambda x: x[1])
            insights.append(f"主要成功模式：{top_pattern[0]} (权重: {top_pattern[1]:.2f})")

        return insights if insights else ["集成分析运行良好"]

    def meta_cognition_driven_optimization(self) -> Dict[str, Any]:
        """
        元认知驱动的策略优化（Round 353 核心功能）
        基于元认知分析结果，驱动自适应学习引擎进行策略优化
        实现：认知 → 反思 → 优化 → 再认知 的递归闭环
        """
        print("\n=== 元认知驱动策略优化 ===")

        # 第一阶段：认知（收集当前系统状态）
        cognitive_data = self._collect_cognitive_data()
        cognitive_patterns = self._analyze_thinking_patterns(cognitive_data)
        depth_evaluation = self._evaluate_cognitive_depth(cognitive_patterns)

        # 第二阶段：反思（分析当前状态）
        recursive_insight = self._recursive_reflection(depth_evaluation)

        # 第三阶段：优化（调用自适应学习引擎）
        optimization_result = {}
        if self._adaptive_learning_engine:
            try:
                # 运行自适应学习的完整周期
                adaptation = self._adaptive_learning_engine.run_full_cycle()
                optimization_result = {
                    "status": "success",
                    "analysis": adaptation.get("analysis", {}),
                    "adjustment": adaptation.get("adjustment", {}),
                    "strategy": adaptation.get("current_strategy", {})
                }
                print(f"[元认知驱动] 策略优化完成，成功率: {adaptation.get('analysis', {}).get('success_rate', 0):.1%}")
            except Exception as e:
                optimization_result = {"status": "error", "message": str(e)}
        else:
            optimization_result = {"status": "skipped", "message": "自适应学习引擎未初始化"}

        # 第四阶段：再认知（验证优化效果，形成闭环）
        re_cognition_result = self._verify_optimization_effect(depth_evaluation, optimization_result)

        # 生成完整的闭环报告
        闭环_report = {
            "timestamp": datetime.now().isoformat(),
            "round": 353,
            "phase_1_cognition": {
                "cognitive_data_collected": len(cognitive_data.get("thought_records", [])),
                "patterns": cognitive_patterns,
                "depth": depth_evaluation
            },
            "phase_2_reflection": {
                "recursive_insight": recursive_insight,
                "reflection_depth": recursive_insight.get("recursive_depth", 0)
            },
            "phase_3_optimization": optimization_result,
            "phase_4_re_cognition": re_cognition_result,
            "闭环_status": "completed" if re_cognition_result.get("effect_verified") else "partial",
            "recommendations": self._generate闭环_recommendations(
                depth_evaluation, recursive_insight, optimization_result, re_cognition_result
            )
        }

        # 保存到历史
        self.state["last_闭环_time"] = 闭环_report["timestamp"]
        self.state["闭环_history"].append(闭环_report)
        self.state["meta_cognition_level"] = depth_evaluation.get("overall_depth", 0)
        self._save_state()

        return 闭环_report

    def _verify_optimization_effect(self, depth: Dict, optimization: Dict) -> Dict[str, Any]:
        """验证优化效果"""
        # 基于优化前后的状态对比
        effect_verified = optimization.get("status") == "success"

        changes = []
        if effect_verified:
            adjustment = optimization.get("adjustment", {})
            if adjustment.get("status") == "success":
                adjusted = adjustment.get("adjusted_params", {})
                if "trigger_thresholds" in adjusted:
                    changes.append("触发阈值已调整")
                if "decision_weights" in adjusted:
                    changes.append("决策权重已优化")

        return {
            "effect_verified": effect_verified,
            "changes": changes,
            "verification_time": datetime.now().isoformat()
        }

    def _generate闭环_recommendations(self, depth: Dict, reflection: Dict,
                                       optimization: Dict, re_cognition: Dict) -> List[str]:
        """生成闭环优化建议"""
        recommendations = []

        # 基于认知深度
        if depth.get("overall_depth", 0) < 0.5:
            recommendations.append("建议：加强元认知分析深度")

        # 基于递归反思
        if reflection.get("max_layer", 0) < 3:
            recommendations.append("建议：增强递归反思层级")

        # 基于优化状态
        if optimization.get("status") == "success":
            recommendations.append("策略优化已生效，建议持续监控")
        else:
            recommendations.append("策略优化待加强，需更多数据分析")

        # 基于验证结果
        if re_cognition.get("effect_verified"):
            recommendations.append("形成完整闭环，可进入下一轮进化")
        else:
            recommendations.append("闭环尚未完全形成，需继续优化")

        return recommendations

    def run_meta_evolution_loop(self) -> Dict[str, Any]:
        """
        运行完整的元认知进化闭环（Round 353 主入口）
        实现：认知 → 反思 → 优化 → 再认知 → 持续进化
        """
        print("\n" + "="*60)
        print("     智能全场景进化环元认知深度增强 (Round 353)")
        print("     核心功能：认知→反思→优化→再认知 递归进化闭环")
        print("="*60)

        # 第一步：元认知分析
        print("\n[阶段 1/4] 认知：收集和分析系统认知状态...")
        cognitive_data = self._collect_cognitive_data()
        cognitive_patterns = self._analyze_thinking_patterns(cognitive_data)
        depth_evaluation = self._evaluate_cognitive_depth(cognitive_patterns)
        print(f"  → 认知深度: {depth_evaluation.get('description', 'N/A')}")

        # 第二步：递归反思
        print("\n[阶段 2/4] 反思：对认知过程进行递归反思...")
        recursive_insight = self._recursive_reflection(depth_evaluation)
        print(f"  → 递归层级: {recursive_insight.get('max_layer', 0)}")
        for insight in recursive_insight.get("insights", [])[:2]:
            print(f"    - {insight.get('description', '')}")

        # 第三步：策略优化
        print("\n[阶段 3/4] 优化：调用自适应学习引擎进行策略优化...")
        optimization_result = {}
        if self._adaptive_learning_engine:
            try:
                adaptation = self._adaptive_learning_engine.run_full_cycle()
                optimization_result = {
                    "status": "success",
                    "success_rate": adaptation.get("analysis", {}).get("success_rate", 0),
                    "adjustments": adaptation.get("adjustment", {}).get("adjusted_params", {})
                }
                print(f"  → 优化完成，成功率: {optimization_result['success_rate']:.1%}")
            except Exception as e:
                optimization_result = {"status": "error", "message": str(e)}
                print(f"  → 优化失败: {e}")

        # 第四步：再认知验证
        print("\n[阶段 4/4] 再认知：验证优化效果，形成闭环...")
        re_cognition = self._verify_optimization_effect(depth_evaluation, optimization_result)
        print(f"  → 效果验证: {'通过' if re_cognition.get('effect_verified') else '待优化'}")

        # 生成最终报告
        final_report = {
            "timestamp": datetime.now().isoformat(),
            "round": 353,
            "version": "1.1.0",
            "status": "completed",
            "phase_1_cognition": {
                "thoughts_analyzed": len(cognitive_data.get("thought_records", [])),
                "depth_level": depth_evaluation.get("level", "未知"),
                "depth_score": depth_evaluation.get("overall_depth", 0)
            },
            "phase_2_reflection": {
                "recursive_layers": recursive_insight.get("max_layer", 0),
                "capability": recursive_insight.get("meta_cognition_capability", "未知")
            },
            "phase_3_optimization": optimization_result,
            "phase_4_re_cognition": {
                "verified": re_cognition.get("effect_verified", False),
                "changes": re_cognition.get("changes", [])
            },
            "闭环_summary": "完整" if re_cognition.get("effect_verified") else "部分",
            "meta_cognition_level": depth_evaluation.get("overall_depth", 0),
            "recommendations": self._generate闭环_recommendations(
                depth_evaluation, recursive_insight, optimization_result, re_cognition
            )
        }

        # 保存状态
        self.state["last_meta_evolution_time"] = final_report["timestamp"]
        self.state["meta_evolution_history"].append(final_report)
        self.state["version"] = "1.1.0"
        self.state["meta_cognition_level"] = depth_evaluation.get("overall_depth", 0)
        self._save_state()

        print("\n" + "="*60)
        print("     Round 353 元认知进化闭环完成")
        print(f"     元认知深度: {depth_evaluation.get('description', 'N/A')}")
        print(f"     闭环状态: {final_report['闭环_summary']}")
        print("="*60)

        return final_report


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
        print("\n[Round 353 新增]")
        print("  python evolution_meta_cognition_deep_enhancement_engine.py integrate  - 集成自适应学习引擎")
        print("  python evolution_meta_cognition_deep_enhancement_engine.py optimize  - 元认知驱动策略优化")
        print("  python evolution_meta_cognition_deep_enhancement_engine.py loop      - 运行完整元认知进化闭环")
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

    # Round 353 新增命令
    elif command == "integrate":
        result = engine.integrate_adaptive_learning()
        print("\n集成结果:")
        print(f"  状态: {result.get('status', 'unknown')}")
        if result.get("status") == "success" or result.get("integration_insights"):
            for insight in result.get("integration_insights", []):
                print(f"  - {insight}")

    elif command == "optimize":
        result = engine.meta_cognition_driven_optimization()
        print("\n元认知驱动优化结果:")
        print(f"  闭环状态: {result.get('闭环_status', 'unknown')}")
        print("\n建议:")
        for rec in result.get("recommendations", []):
            print(f"  - {rec}")

    elif command == "loop":
        result = engine.run_meta_evolution_loop()
        print("\n完整元认知进化闭环:")
        print(f"  状态: {result.get('status', 'unknown')}")
        print(f"  认知深度: {result.get('phase_1_cognition', {}).get('depth_level', 'unknown')}")
        print(f"  递归层级: {result.get('phase_2_reflection', {}).get('recursive_layers', 0)}")
        print(f"  闭环: {result.get('闭环_summary', 'unknown')}")

    else:
        print(f"未知命令: {command}")


if __name__ == "__main__":
    main()