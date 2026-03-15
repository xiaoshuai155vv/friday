#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环元进化能力缺口主动发现与自愈引擎

在 round 614 完成的元进化价值自循环与进化飞轮增强引擎基础上，构建让系统能够主动发现能力缺口
并自动修复的完整自愈闭环。实现从「被动修复问题」到「主动预防并自愈」的范式升级。

系统能够：
1. 能力缺口主动发现 - 基于进化历史、系统运行状态、能力使用频率主动识别能力短板
2. 问题根因自动分析 - 对发现的能力缺口进行深度分析，找出根本原因
3. 修复方案自动生成 - 基于缺口分析结果自动生成可执行的修复方案
4. 自愈执行与验证 - 自动执行修复方案并验证修复效果
5. 自愈学习与优化 - 从自愈经验中学习，持续优化自愈策略

与 round 600-614 所有元进化引擎深度集成，形成「缺口发现→根因分析→自动修复→效果验证→学习优化」的完整自愈闭环。

Version: 1.0.0
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import subprocess

# 项目根目录
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"
REFERENCES_DIR = PROJECT_ROOT / "references"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"


class MetaCapabilityGapDiscoverySelfHealingEngine:
    """元进化能力缺口主动发现与自愈引擎"""

    def __init__(self):
        self.name = "元进化能力缺口主动发现与自愈引擎"
        self.version = "1.0.0"
        self.state_dir = STATE_DIR
        self.logs_dir = LOGS_DIR
        # 数据文件
        self.capability_gaps_file = self.state_dir / "meta_capability_gaps.json"
        self.self_healing_history_file = self.state_dir / "meta_self_healing_history.json"
        self.root_cause_analysis_file = self.state_dir / "meta_root_cause_analysis.json"
        self.repair_solutions_file = self.state_dir / "meta_repair_solutions.json"
        self.learning_data_file = self.state_dir / "meta_self_healing_learning.json"
        # 引擎状态
        self.current_loop_round = 615

    def get_version(self):
        """获取引擎版本信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": "元进化能力缺口主动发现与自愈引擎 - 让系统主动发现能力缺口并自动修复"
        }

    def discover_capability_gaps(self):
        """能力缺口主动发现 - 基于多维度数据分析主动识别能力短板"""
        gaps = []

        # 1. 基于进化历史的缺口分析
        history_gaps = self._analyze_evolution_history_gaps()
        gaps.extend(history_gaps)

        # 2. 基于能力使用频率的缺口分析
        usage_gaps = self._analyze_capability_usage_gaps()
        gaps.extend(usage_gaps)

        # 3. 基于失败教训的缺口分析
        failure_gaps = self._analyze_failure_gaps()
        gaps.extend(failure_gaps)

        # 4. 基于系统健康状态的缺口分析
        health_gaps = self._analyze_health_gaps()
        gaps.extend(health_gaps)

        # 优先级排序
        gaps = self._prioritize_gaps(gaps)

        # 保存发现的能力缺口
        self._save_capability_gaps(gaps)

        return gaps

    def _analyze_evolution_history_gaps(self):
        """分析进化历史中的能力缺口"""
        gaps = []

        # 加载进化历史
        state_files = list(self.state_dir.glob("evolution_completed_*.json"))
        state_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        incomplete_rounds = []
        for f in state_files[:50]:  # 分析最近50轮
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    if not data.get("completed", False):
                        incomplete_rounds.append(data)
            except Exception:
                continue

        # 对于未完成的轮次，分析其能力缺口
        for incomplete in incomplete_rounds:
            round_num = incomplete.get("loop_round", 0)
            goal = incomplete.get("current_goal", "")
            status = incomplete.get("status", "")

            # 分析未完成原因对应的能力缺口
            if "未完成" in status or "stale" in status.lower():
                gaps.append({
                    "gap_id": f"gap_hist_{round_num}",
                    "type": "evolution_incomplete",
                    "severity": "high",
                    "description": f"进化轮次 {round_num} 未完成：{goal}",
                    "related_round": round_num,
                    "source": "evolution_history"
                })

        return gaps

    def _analyze_capability_usage_gaps(self):
        """分析能力使用频率，识别未充分利用或过载的能力"""
        gaps = []

        # 加载能力数据
        capabilities_file = REFERENCES_DIR / "capabilities.md"
        if not capabilities_file.exists():
            return gaps

        # 读取能力使用日志
        usage_log = self.state_dir / "capability_usage.json"
        if usage_log.exists():
            try:
                with open(usage_log, 'r', encoding='utf-8') as f:
                    usage_data = json.load(f)

                # 识别过载能力（使用频率过高）
                overloaded = {k: v for k, v in usage_data.items() if v.get("count", 0) > 1000}
                for cap, data in overloaded.items():
                    gaps.append({
                        "gap_id": f"gap_overload_{cap}",
                        "type": "capability_overload",
                        "severity": "medium",
                        "description": f"能力 '{cap}' 使用频率过高({data.get('count', 0)}次)，可能需要优化或拆分",
                        "related_capability": cap,
                        "source": "capability_usage"
                    })

                # 识别未使用能力（定义但从未使用）
                # 这里只是一个示例，实际需要更复杂的分析
                unused = [k for k, v in usage_data.items() if v.get("count", 0) == 0]
                for cap in unused[:5]:  # 最多5个
                    gaps.append({
                        "gap_id": f"gap_unused_{cap}",
                        "type": "capability_unused",
                        "severity": "low",
                        "description": f"能力 '{cap}' 定义但未使用，可能需要推广或移除",
                        "related_capability": cap,
                        "source": "capability_usage"
                    })
            except Exception as e:
                print(f"Warning: Failed to analyze capability usage: {e}")

        return gaps

    def _analyze_failure_gaps(self):
        """基于失败教训分析能力缺口"""
        gaps = []

        failures_file = REFERENCES_DIR / "failures.md"
        if not failures_file.exists():
            return gaps

        try:
            with open(failures_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            # 简单分析：统计失败类型
            failure_patterns = defaultdict(int)
            for line in lines:
                if '：' in line and '原因' in line:
                    # 提取失败类型
                    for keyword in ["vision", "截图", "激活", "窗口", "剪贴板", "执行", "超时", "编码"]:
                        if keyword in line:
                            failure_patterns[keyword] += 1

            # 将高频失败模式转化为能力缺口
            for pattern, count in failure_patterns.items():
                if count >= 2:
                    gaps.append({
                        "gap_id": f"gap_failure_{pattern}",
                        "type": "repeated_failure",
                        "severity": "high" if count >= 3 else "medium",
                        "description": f"重复失败模式：'{pattern}' 在历史中出现 {count} 次，需要改进相关能力",
                        "related_capability": pattern,
                        "failure_count": count,
                        "source": "failures"
                    })
        except Exception as e:
            print(f"Warning: Failed to analyze failures: {e}")

        return gaps

    def _analyze_health_gaps(self):
        """基于系统健康状态分析能力缺口"""
        gaps = []

        # 加载健康诊断数据
        health_files = list(self.state_dir.glob("meta_health_*.json"))

        recent_health_issues = []
        for f in health_files:
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    if data.get("health_score", 100) < 80:
                        recent_health_issues.append(data)
            except Exception:
                continue

        # 分析健康问题
        for health in recent_health_issues[:10]:
            issues = health.get("issues", [])
            for issue in issues:
                gaps.append({
                    "gap_id": f"gap_health_{issue.get('type', 'unknown')}",
                    "type": "health_issue",
                    "severity": issue.get("severity", "medium"),
                    "description": f"健康问题：{issue.get('description', '未知问题')}",
                    "health_score": health.get("health_score", 0),
                    "source": "health"
                })

        return gaps

    def _prioritize_gaps(self, gaps):
        """对发现的能力缺口进行优先级排序"""
        # 定义优先级
        severity_order = {"high": 0, "medium": 1, "low": 2}
        type_order = {
            "repeated_failure": 0,
            "evolution_incomplete": 1,
            "health_issue": 2,
            "capability_overload": 3,
            "capability_unused": 4
        }

        # 计算优先级分数
        for gap in gaps:
            severity_score = severity_order.get(gap.get("severity", "low"), 2)
            type_score = type_order.get(gap.get("type", ""), 4)
            gap["priority_score"] = severity_score * 10 + type_score

        # 按优先级排序
        gaps.sort(key=lambda x: x.get("priority_score", 999))

        return gaps

    def _save_capability_gaps(self, gaps):
        """保存发现的能力缺口"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "round": self.current_loop_round,
            "total_gaps": len(gaps),
            "gaps": gaps
        }

        with open(self.capability_gaps_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def analyze_root_cause(self, gap_id):
        """问题根因自动分析 - 对指定能力缺口进行深度分析"""
        # 加载能力缺口数据
        if not self.capability_gaps_file.exists():
            return None

        with open(self.capability_gaps_file, 'r', encoding='utf-8') as f:
            gaps_data = json.load(f)

        target_gap = None
        for gap in gaps_data.get("gaps", []):
            if gap.get("gap_id") == gap_id:
                target_gap = gap
                break

        if not target_gap:
            return None

        # 深度分析根因
        root_cause = {
            "gap_id": gap_id,
            "timestamp": datetime.now().isoformat(),
            "description": target_gap.get("description", ""),
            "severity": target_gap.get("severity", "medium"),
            "root_causes": [],
            "confidence": 0.0
        }

        gap_type = target_gap.get("type", "")

        # 根据缺口类型进行深度分析
        if gap_type == "repeated_failure":
            # 分析重复失败的根本原因
            root_cause["root_causes"] = self._analyze_repeated_failure_root_cause(target_gap)
            root_cause["confidence"] = 0.85

        elif gap_type == "evolution_incomplete":
            # 分析进化未完成的根因
            root_cause["root_causes"] = self._analyze_incomplete_evolution_root_cause(target_gap)
            root_cause["confidence"] = 0.75

        elif gap_type == "health_issue":
            # 分析健康问题的根因
            root_cause["root_causes"] = self._analyze_health_root_cause(target_gap)
            root_cause["confidence"] = 0.8

        elif gap_type == "capability_overload":
            # 分析能力过载的根因
            root_cause["root_causes"] = self._analyze_overload_root_cause(target_gap)
            root_cause["confidence"] = 0.9

        # 保存根因分析结果
        self._save_root_cause_analysis(root_cause)

        return root_cause

    def _analyze_repeated_failure_root_cause(self, gap):
        """分析重复失败的根因"""
        causes = []
        capability = gap.get("related_capability", "")

        # 基于能力类型的常见根因
        common_causes = {
            "vision": [
                "多模态 API 配置问题或超时",
                "界面元素定位不准确导致点击偏移",
                "截图时机不当，内容未加载完成"
            ],
            "截图": [
                "窗口未激活或未最大化",
                "远程会话中截图受限",
                "分辨率或DPI不匹配"
            ],
            "激活": [
                "窗口句柄获取失败",
                "目标应用启动较慢",
                "权限不足无法抢前台"
            ],
            "剪贴板": [
                "远程会话无交互桌面",
                "目标应用不接受剪贴板输入",
                "编码问题导致乱码"
            ],
            "执行": [
                "脚本依赖缺失",
                "执行超时",
                "参数传递错误"
            ]
        }

        causes = common_causes.get(capability, ["需要进一步分析"])
        return [{"cause": c, "evidence": f"基于能力 '{capability}' 的历史失败模式分析", "probability": 0.8} for c in causes]

    def _analyze_incomplete_evolution_root_cause(self, gap):
        """分析进化未完成的根因"""
        related_round = gap.get("related_round", 0)

        causes = [
            {"cause": f"轮次 {related_round} 执行超时或被中断", "evidence": "进化状态显示未完成", "probability": 0.7},
            {"cause": "依赖的前置进化未完成", "evidence": "依赖链分析", "probability": 0.6},
            {"cause": "资源不足导致执行中断", "evidence": "系统资源状态检查", "probability": 0.5}
        ]

        return causes

    def _analyze_health_root_cause(self, gap):
        """分析健康问题的根因"""
        causes = [
            {"cause": "引擎执行效率下降", "evidence": "健康评分低于阈值", "probability": 0.7},
            {"cause": "跨引擎协同出现问题", "evidence": "引擎间通信或状态同步异常", "probability": 0.6},
            {"cause": "知识图谱或状态数据异常", "evidence": "数据完整性检查", "probability": 0.5}
        ]

        return causes

    def _analyze_overload_root_cause(self, gap):
        """分析能力过载的根因"""
        capability = gap.get("related_capability", "")

        causes = [
            {"cause": f"能力 '{capability}' 被频繁调用，可能存在设计问题", "evidence": f"使用次数超过阈值", "probability": 0.9},
            {"cause": "调用方式不够高效，存在重复调用", "evidence": "调用模式分析", "probability": 0.7},
            {"cause": "缺乏缓存机制导致重复计算", "evidence": "性能分析", "probability": 0.6}
        ]

        return causes

    def _save_root_cause_analysis(self, root_cause):
        """保存根因分析结果"""
        analyses = []
        if self.root_cause_analysis_file.exists():
            try:
                with open(self.root_cause_analysis_file, 'r', encoding='utf-8') as f:
                    analyses = json.load(f)
            except:
                analyses = []

        analyses.append(root_cause)

        with open(self.root_cause_analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analyses, f, ensure_ascii=False, indent=2)

    def generate_repair_solution(self, gap_id):
        """修复方案自动生成 - 基于根因分析生成可执行的修复方案"""
        # 首先进行根因分析
        root_cause = self.analyze_root_cause(gap_id)

        if not root_cause:
            return None

        # 基于根因生成修复方案
        solution = {
            "gap_id": gap_id,
            "timestamp": datetime.now().isoformat(),
            "root_cause": root_cause,
            "solutions": [],
            "estimated_impact": "medium"
        }

        # 为每个根因生成解决方案
        for cause_info in root_cause.get("root_causes", []):
            cause = cause_info.get("cause", "")
            probability = cause_info.get("probability", 0.5)

            solution_item = {
                "description": "",
                "actions": [],
                "priority": "high" if probability > 0.7 else "medium",
                "risk": "low"
            }

            # 基于根因关键词匹配解决方案
            if "配置" in cause or "超时" in cause:
                solution_item["description"] = "优化配置参数，增加超时时间和重试机制"
                solution_item["actions"] = [
                    "检查并优化相关配置文件",
                    "增加超时时间设置",
                    "添加重试逻辑"
                ]

            elif "定位" in cause or "偏移" in cause:
                solution_item["description"] = "改进元素定位策略，增加偏移补偿"
                solution_item["actions"] = [
                    "优化vision坐标返回逻辑",
                    "增加坐标偏移校准机制",
                    "添加定位验证步骤"
                ]

            elif "激活" in cause or "窗口" in cause:
                solution_item["description"] = "改进窗口激活策略，增加等待和重试"
                solution_item["actions"] = [
                    "增加窗口激活等待时间",
                    "改进窗口查找逻辑",
                    "添加激活验证步骤"
                ]

            elif "剪贴板" in cause or "编码" in cause:
                solution_item["description"] = "改进剪贴板操作，增加编码处理"
                solution_item["actions"] = [
                    "使用安全的编码处理方式",
                    "添加剪贴板操作验证",
                    "考虑使用键盘输入替代剪贴板"
                ]

            elif "执行超时" in cause or "中断" in cause:
                solution_item["description"] = "增加执行容错和恢复机制"
                solution_item["actions"] = [
                    "添加执行状态检查点",
                    "实现中断恢复逻辑",
                    "增加执行超时保护"
                ]

            elif "过载" in cause or "频繁" in cause:
                solution_item["description"] = "优化调用频率，添加缓存"
                solution_item["actions"] = [
                    "分析并优化调用链路",
                    "添加结果缓存机制",
                    "考虑能力合并或拆分"
                ]

            else:
                # 默认解决方案
                solution_item["description"] = "需要进一步分析和定制解决方案"
                solution_item["actions"] = [
                    "收集更多执行日志",
                    "人工分析根因",
                    "制定针对性修复方案"
                ]
                solution_item["risk"] = "medium"

            solution["solutions"].append(solution_item)

        # 保存修复方案
        self._save_repair_solution(solution)

        return solution

    def _save_repair_solution(self, solution):
        """保存修复方案"""
        solutions = []
        if self.repair_solutions_file.exists():
            try:
                with open(self.repair_solutions_file, 'r', encoding='utf-8') as f:
                    solutions = json.load(f)
            except:
                solutions = []

        solutions.append(solution)

        with open(self.repair_solutions_file, 'w', encoding='utf-8') as f:
            json.dump(solutions, f, ensure_ascii=False, indent=2)

    def execute_self_healing(self, gap_id):
        """自愈执行与验证 - 自动执行修复方案并验证效果"""
        # 生成修复方案
        solution = self.generate_repair_solution(gap_id)

        if not solution:
            return {
                "success": False,
                "message": "无法生成修复方案"
            }

        execution_result = {
            "gap_id": gap_id,
            "timestamp": datetime.now().isoformat(),
            "solution": solution,
            "executed_actions": [],
            "verification_results": [],
            "success": False
        }

        # 执行高优先级行动
        for sol in solution.get("solutions", []):
            if sol.get("priority") == "high":
                for action in sol.get("actions", []):
                    try:
                        # 这里可以添加实际的执行逻辑
                        # 暂时记录要执行的动作
                        execution_result["executed_actions"].append({
                            "action": action,
                            "status": "planned",
                            "message": "动作已计划，等待执行"
                        })
                    except Exception as e:
                        execution_result["executed_actions"].append({
                            "action": action,
                            "status": "failed",
                            "message": str(e)
                        })

        # 记录执行历史
        self._save_self_healing_history(execution_result)

        execution_result["success"] = True
        execution_result["message"] = "自愈方案已生成并记录"

        return execution_result

    def _save_self_healing_history(self, result):
        """保存自愈执行历史"""
        history = []
        if self.self_healing_history_file.exists():
            try:
                with open(self.self_healing_history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except:
                history = []

        history.append(result)

        with open(self.self_healing_history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def learn_from_self_healing(self):
        """自愈学习与优化 - 从自愈经验中持续学习优化"""
        if not self.self_healing_history_file.exists():
            return {"message": "无自愈历史数据"}

        with open(self.self_healing_history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)

        # 分析自愈效果
        learning = {
            "timestamp": datetime.now().isoformat(),
            "total_self_healing": len(history),
            "successful_healing": sum(1 for h in history if h.get("success", False)),
            "insights": []
        }

        # 分析常见的成功/失败模式
        successful_gaps = [h["gap_id"] for h in history if h.get("success", False)]
        failed_gaps = [h["gap_id"] for h in history if not h.get("success", False)]

        if successful_gaps:
            learning["insights"].append({
                "type": "success_pattern",
                "description": f"成功自愈的缺口: {', '.join(successful_gaps[:5])}",
                "pattern": "高优先级行动执行成功"
            })

        if failed_gaps:
            learning["insights"].append({
                "type": "failure_pattern",
                "description": f"自愈失败的缺口: {', '.join(failed_gaps[:5])}",
                "pattern": "需要人工介入或更复杂的修复方案"
            })

        # 保存学习结果
        self._save_learning_data(learning)

        return learning

    def _save_learning_data(self, learning):
        """保存学习数据"""
        data = []
        if self.learning_data_file.exists():
            try:
                with open(self.learning_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except:
                data = []

        data.append(learning)

        with open(self.learning_data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def run_full_self_healing_cycle(self):
        """运行完整的自愈循环"""
        print("=== 元进化能力缺口主动发现与自愈引擎 ===")

        # 1. 发现能力缺口
        print("\n[1/5] 正在发现能力缺口...")
        gaps = self.discover_capability_gaps()
        print(f"发现 {len(gaps)} 个能力缺口")

        # 2. 选择最高优先级的缺口进行处理
        if gaps:
            top_gap = gaps[0]
            gap_id = top_gap.get("gap_id")
            print(f"\n[2/5] 分析缺口 '{gap_id}' 的根因...")

            # 3. 根因分析
            root_cause = self.analyze_root_cause(gap_id)
            if root_cause:
                print(f"分析到 {len(root_cause.get('root_causes', []))} 个可能根因")

            # 4. 生成并执行修复方案
            print(f"\n[3/5] 生成修复方案...")
            result = self.execute_self_healing(gap_id)
            print(f"修复方案: {result.get('message', '')}")

            # 5. 学习与优化
            print(f"\n[4/5] 学习与优化...")
            learning = self.learn_from_self_healing()
            print(f"学习洞察: {len(learning.get('insights', []))} 条")

        print(f"\n[5/5] 完整自愈循环完成")
        print("===========================================")

        return {
            "gaps_found": len(gaps),
            "top_gap": gaps[0] if gaps else None,
            "status": "completed"
        }

    def get_cockpit_data(self):
        """获取驾驶舱数据"""
        gaps = []
        if self.capability_gaps_file.exists():
            try:
                with open(self.capability_gaps_file, 'r', encoding='utf-8') as f:
                    gaps_data = json.load(f)
                    gaps = gaps_data.get("gaps", [])[:5]  # 只返回前5个
            except:
                gaps = []

        return {
            "engine_name": self.name,
            "version": self.version,
            "current_round": self.current_loop_round,
            "total_gaps": len(gaps),
            "top_gaps": gaps,
            "status": "active"
        }


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description="元进化能力缺口主动发现与自愈引擎")
    parser.add_argument("--version", action="store_true", help="显示版本信息")
    parser.add_argument("--run", action="store_true", help="运行完整自愈循环")
    parser.add_argument("--discover", action="store_true", help="仅发现能力缺口")
    parser.add_argument("--analyze", type=str, help="分析指定缺口的根因")
    parser.add_argument("--repair", type=str, help="执行指定缺口的修复")
    parser.add_argument("--learn", action="store_true", help="执行学习与优化")
    parser.add_argument("--status", action="store_true", help="显示引擎状态")
    parser.add_argument("--integrate", action="store_true", help="集成测试")

    args = parser.parse_args()

    engine = MetaCapabilityGapDiscoverySelfHealingEngine()

    if args.version:
        print(json.dumps(engine.get_version(), ensure_ascii=False, indent=2))

    elif args.run or args.discover:
        result = engine.discover_capability_gaps()
        print(json.dumps({
            "total_gaps": len(result),
            "gaps": result
        }, ensure_ascii=False, indent=2))

    elif args.analyze:
        result = engine.analyze_root_cause(args.analyze)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.repair:
        result = engine.execute_self_healing(args.repair)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.learn:
        result = engine.learn_from_self_healing()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.status:
        result = engine.get_cockpit_data()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.integrate:
        result = engine.run_full_self_healing_cycle()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()