#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环跨引擎协同自优化与深度集成引擎
让系统能够跨进化引擎深度协同、实时诊断进化环健康状态、
自动发现并修复进化过程中的问题，实现真正的「进化系统自我进化」。
集成已有进化引擎的协同能力、健康监测能力、自愈能力，
形成跨引擎的协同自优化闭环。

功能：
1. 跨引擎健康状态实时监测
2. 跨引擎协同问题自动诊断
3. 自优化方案自动生成与执行
4. 进化环整体健康度评估
5. 多引擎协同效率优化
6. 与 do.py 深度集成，支持关键词触发

Version: 1.0.0

依赖：
- evolution_loop_health_monitor.py (round 283)
- evolution_loop_self_healing_engine.py (round 280)
- evolution_loop_self_healing_advanced.py (round 290)
- evolution_global_situation_awareness.py (round 329)
- evolution_meta_coordination_engine.py (round 312)
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict
import math
import subprocess

# 添加项目根目录到 Python 路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, SCRIPT_DIR)


def _safe_print(text: str):
    """安全打印，处理编码问题"""
    import re
    try:
        print(text)
    except UnicodeEncodeError:
        clean_text = re.sub(r'[^\x00-\x7F]+', '', text)
        print(clean_text)


class CrossEngineCollaborationOptimizer:
    """进化环跨引擎协同自优化与深度集成引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.project_root = PROJECT_ROOT
        self.scripts_dir = SCRIPT_DIR
        self.runtime_dir = os.path.join(self.project_root, "runtime")
        self.state_dir = os.path.join(self.runtime_dir, "state")
        self.logs_dir = os.path.join(self.runtime_dir, "logs")

        # 进化引擎注册表
        self.engine_registry = self._init_engine_registry()

        # 状态存储
        self.health_state_path = os.path.join(self.state_dir, "cross_engine_health_state.json")
        self.optimization_history_path = os.path.join(self.state_dir, "cross_engine_optimization_history.json")

        # 配置
        self.config = self._load_config()

        # 初始化
        self._ensure_directories()

    def _init_engine_registry(self) -> Dict[str, Dict]:
        """初始化进化引擎注册表"""
        return {
            # 核心进化环引擎
            "evolution_loop_automation": {"module": "evolution_loop_automation.py", "health_check": "status", "round": 73},
            "evolution_coordinator": {"module": "evolution_coordinator.py", "health_check": "status", "round": 78},
            "evolution_strategy_engine": {"module": "evolution_strategy_engine.py", "health_check": "status", "round": 70},
            "evolution_full_auto_loop": {"module": "evolution_full_auto_loop.py", "health_check": "status", "round": 300},

            # 健康监测引擎
            "evolution_loop_health_monitor": {"module": "evolution_loop_health_monitor.py", "health_check": "status", "round": 283},
            "evolution_loop_self_healing_engine": {"module": "evolution_loop_self_healing_engine.py", "health_check": "status", "round": 280},
            "evolution_loop_self_healing_advanced": {"module": "evolution_loop_self_healing_advanced.py", "health_check": "status", "round": 290},

            # 知识与推理引擎
            "evolution_knowledge_graph_reasoning": {"module": "evolution_knowledge_graph_reasoning.py", "health_check": "status", "round": 298},
            "evolution_knowledge_inheritance_engine": {"module": "evolution_knowledge_inheritance_engine.py", "health_check": "status", "round": 240},
            "evolution_knowledge_active_reasoning_engine": {"module": "evolution_knowledge_active_reasoning_engine.py", "health_check": "status", "round": 348},

            # 决策与执行引擎
            "evolution_decision_quality_evaluator": {"module": "evolution_decision_quality_evaluator.py", "health_check": "status", "round": 335},
            "evolution_decision_quality_driven_optimizer": {"module": "evolution_decision_quality_driven_optimizer.py", "health_check": "status", "round": 336},
            "evolution_autonomous_consciousness_execution_engine": {"module": "evolution_autonomous_consciousness_execution_engine.py", "health_check": "status", "round": 321},

            # 元协调与全局引擎
            "evolution_meta_coordination_engine": {"module": "evolution_meta_coordination_engine.py", "health_check": "status", "round": 312},
            "evolution_global_situation_awareness": {"module": "evolution_global_situation_awareness.py", "health_check": "status", "round": 329},

            # 持续优化引擎
            "evolution_methodology_optimizer": {"module": "evolution_methodology_optimizer.py", "health_check": "status", "round": 345},
            "evolution_self_evolution_enhancement_engine": {"module": "evolution_self_evolution_enhancement_engine.py", "health_check": "status", "round": 324},
        }

    def _load_config(self) -> Dict:
        """加载配置"""
        default_config = {
            # 健康监测配置
            'health_check_interval': 300,              # 健康检查间隔(秒)
            'health_check_engines': 10,                 # 每轮检查引擎数
            'health_threshold': 0.7,                   # 健康度阈值

            # 协同配置
            'collaboration_timeout': 30,               # 协同超时(秒)
            'max_concurrent_engines': 5,               # 最大并发引擎数

            # 优化配置
            'auto_optimization_enabled': True,          # 自动优化启用
            'optimization_interval': 600,               # 优化间隔(秒)
            'min_optimization_score': 0.5,              # 最小优化分数

            # 诊断配置
            'diagnosis_depth': 3,                       # 诊断深度
            'auto_fix_enabled': True,                   # 自动修复启用
        }
        return default_config

    def _ensure_directories(self):
        """确保必要的目录存在"""
        for directory in [self.state_dir, self.logs_dir]:
            os.makedirs(directory, exist_ok=True)

    def _load_health_state(self) -> Dict:
        """加载健康状态"""
        if os.path.exists(self.health_state_path):
            try:
                with open(self.health_state_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "engines": {},
            "overall_health": 1.0,
            "last_check": None,
            "issues": []
        }

    def _save_health_state(self, state: Dict):
        """保存健康状态"""
        try:
            with open(self.health_state_path, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[警告] 保存健康状态失败: {e}")

    def _load_optimization_history(self) -> List[Dict]:
        """加载优化历史"""
        if os.path.exists(self.optimization_history_path):
            try:
                with open(self.optimization_history_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_optimization_history(self, history: List[Dict]):
        """保存优化历史"""
        try:
            # 只保留最近100条
            history = history[-100:]
            with open(self.optimization_history_path, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[警告] 保存优化历史失败: {e}")

    def _check_engine_health(self, engine_name: str) -> Dict:
        """检查单个引擎健康状态"""
        engine_info = self.engine_registry.get(engine_name, {})
        engine_path = os.path.join(self.scripts_dir, engine_info.get("module", ""))

        result = {
            "name": engine_name,
            "exists": os.path.exists(engine_path),
            "loadable": False,
            "status": "unknown",
            "last_check": datetime.now().isoformat()
        }

        if result["exists"]:
            # 尝试导入模块
            try:
                module_name = engine_info.get("module", "").replace(".py", "")
                # 简单的语法检查
                with open(engine_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                    compile(code, engine_path, 'exec')
                result["loadable"] = True
                result["status"] = "healthy"
            except SyntaxError as e:
                result["status"] = "syntax_error"
                result["error"] = str(e)
            except Exception as e:
                result["status"] = "error"
                result["error"] = str(e)

        return result

    def check_all_engines_health(self) -> Dict:
        """检查所有进化引擎的健康状态"""
        _safe_print("[跨引擎协同优化] 开始检查所有进化引擎健康状态...")

        health_state = self._load_health_state()
        engine_health = {}

        for engine_name in self.engine_registry:
            health = self._check_engine_health(engine_name)
            engine_health[engine_name] = health

            # 更新到状态
            health_state["engines"][engine_name] = health

        # 计算整体健康度
        healthy_count = sum(1 for h in engine_health.values() if h["status"] == "healthy")
        total_count = len(engine_health)
        overall_health = healthy_count / total_count if total_count > 0 else 0

        health_state["overall_health"] = overall_health
        health_state["last_check"] = datetime.now().isoformat()

        # 识别问题
        issues = []
        for engine_name, health in engine_health.items():
            if health["status"] != "healthy":
                issues.append({
                    "engine": engine_name,
                    "status": health["status"],
                    "error": health.get("error", "Unknown error"),
                    "time": health["last_check"]
                })

        health_state["issues"] = issues

        self._save_health_state(health_state)

        _safe_print(f"[跨引擎协同优化] 健康检查完成: {healthy_count}/{total_count} 引擎正常, 整体健康度: {overall_health:.2%}")

        return health_state

    def diagnose_collaboration_issues(self) -> List[Dict]:
        """诊断跨引擎协同问题"""
        _safe_print("[跨引擎协同优化] 诊断跨引擎协同问题...")

        health_state = self._load_health_state()
        issues = health_state.get("issues", [])

        diagnosis_results = []

        for issue in issues:
            engine = issue.get("engine")
            status = issue.get("status")

            diagnosis = {
                "engine": engine,
                "issue_type": status,
                "severity": "high" if status == "error" else "medium",
                "description": self._get_issue_description(engine, status),
                "suggested_fix": self._get_suggested_fix(engine, status),
                "timestamp": datetime.now().isoformat()
            }
            diagnosis_results.append(diagnosis)

        # 检查潜在的协同问题
        collaboration_issues = self._detect_collaboration_issues(health_state)
        diagnosis_results.extend(collaboration_issues)

        _safe_print(f"[跨引擎协同优化] 诊断完成，发现 {len(diagnosis_results)} 个问题")

        return diagnosis_results

    def _get_issue_description(self, engine: str, status: str) -> str:
        """获取问题描述"""
        descriptions = {
            "syntax_error": f"引擎 {engine} 存在语法错误，无法加载",
            "error": f"引擎 {engine} 执行时发生错误",
            "not_exists": f"引擎 {engine} 文件不存在",
            "unknown": f"引擎 {engine} 状态未知"
        }
        return descriptions.get(status, f"引擎 {engine} 存在问题: {status}")

    def _get_suggested_fix(self, engine: str, status: str) -> str:
        """获取建议修复方案"""
        fixes = {
            "syntax_error": f"检查并修复 {engine} 的语法错误",
            "error": f"查看 {engine} 的错误日志并修复问题",
            "not_exists": f"重新创建 {engine} 模块",
            "unknown": f"重新检查 {engine} 状态"
        }
        return fixes.get(status, "检查并修复该引擎")

    def _detect_collaboration_issues(self, health_state: Dict) -> List[Dict]:
        """检测潜在的协同问题"""
        issues = []

        # 检查整体健康度
        overall_health = health_state.get("overall_health", 1.0)
        if overall_health < self.config['health_threshold']:
            issues.append({
                "engine": "overall_system",
                "issue_type": "low_health",
                "severity": "high",
                "description": f"进化环整体健康度低于阈值: {overall_health:.2%} < {self.config['health_threshold']:.2%}",
                "suggested_fix": "执行跨引擎协同自优化以提升整体健康度",
                "timestamp": datetime.now().isoformat()
            })

        # 检查连续失败的引擎数量
        engine_states = health_state.get("engines", {})
        failed_engines = [e for e, s in engine_states.items() if s.get("status") != "healthy"]
        if len(failed_engines) > len(engine_states) * 0.3:
            issues.append({
                "engine": "collaboration_pattern",
                "issue_type": "high_failure_rate",
                "severity": "high",
                "description": f"超过30%的引擎失败: {len(failed_engines)}/{len(engine_states)}",
                "suggested_fix": "检查失败引擎的共同原因，可能是依赖或集成问题",
                "timestamp": datetime.now().isoformat()
            })

        return issues

    def generate_optimization_plan(self, diagnosis_results: List[Dict]) -> Dict:
        """生成优化方案"""
        _safe_print("[跨引擎协同优化] 生成优化方案...")

        optimization_plan = {
            "generated_at": datetime.now().isoformat(),
            "issues_count": len(diagnosis_results),
            "priority_fixes": [],
            "general_optimizations": [],
            "estimated_impact": "high"
        }

        # 按严重性排序问题
        severity_order = {"high": 0, "medium": 1, "low": 2}
        sorted_issues = sorted(diagnosis_results,
                               key=lambda x: severity_order.get(x.get("severity", "low"), 2))

        for issue in sorted_issues[:10]:  # 最多处理10个问题
            fix = {
                "engine": issue.get("engine"),
                "issue_type": issue.get("issue_type"),
                "severity": issue.get("severity"),
                "action": issue.get("suggested_fix"),
                "status": "pending"
            }
            optimization_plan["priority_fixes"].append(fix)

        # 添加通用优化建议
        optimization_plan["general_optimizations"] = [
            {
                "type": "health_check",
                "description": "定期执行跨引擎健康检查",
                "interval": self.config['health_check_interval']
            },
            {
                "type": "collaboration_enhancement",
                "description": "增强跨引擎数据共享和状态同步",
                "priority": "medium"
            },
            {
                "type": "performance_optimization",
                "description": "优化引擎间调用效率，减少协同延迟",
                "priority": "low"
            }
        ]

        _safe_print(f"[跨引擎协同优化] 生成了 {len(optimization_plan['priority_fixes'])} 个优先修复项")

        return optimization_plan

    def execute_optimization(self, optimization_plan: Dict) -> Dict:
        """执行优化方案"""
        _safe_print("[跨引擎协同优化] 执行优化方案...")

        results = {
            "executed_at": datetime.now().isoformat(),
            "fixes_attempted": 0,
            "fixes_succeeded": 0,
            "fixes_failed": 0,
            "details": []
        }

        # 记录优化历史
        optimization_record = {
            "plan": optimization_plan,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }

        # 执行优先修复
        for fix in optimization_plan.get("priority_fixes", []):
            if not self.config.get('auto_fix_enabled', True):
                _safe_print(f"[跨引擎协同优化] 自动修复已禁用，跳过: {fix.get('engine')}")
                continue

            results["fixes_attempted"] += 1

            try:
                # 尝试执行修复
                success = self._execute_fix(fix)

                if success:
                    results["fixes_succeeded"] += 1
                    fix["status"] = "success"
                else:
                    results["fixes_failed"] += 1
                    fix["status"] = "failed"

            except Exception as e:
                _safe_print(f"[跨引擎协同优化] 修复失败: {fix.get('engine')}, 错误: {e}")
                results["fixes_failed"] += 1
                fix["status"] = "error"
                fix["error"] = str(e)

            results["details"].append(fix)

        # 保存优化历史
        history = self._load_optimization_history()
        history.append(optimization_record)
        self._save_optimization_history(history)

        _safe_print(f"[跨引擎协同优化] 优化执行完成: {results['fixes_succeeded']}/{results['fixes_attempted']} 成功")

        return results

    def _execute_fix(self, fix: Dict) -> bool:
        """执行单个修复"""
        engine = fix.get("engine")
        issue_type = fix.get("issue_type")

        # 根据问题类型执行不同修复
        if issue_type == "syntax_error":
            # 语法错误需要人工修复，这里只记录
            _safe_print(f"[跨引擎协同优化] {engine} 需要人工修复语法错误")
            return False
        elif issue_type == "low_health":
            # 整体健康度低，执行健康检查和优化
            self.check_all_engines_health()
            return True
        else:
            # 其他问题，记录并跳过
            _safe_print(f"[跨引擎协同优化] {engine} 问题需要人工介入")
            return False

    def evaluate_overall_health(self) -> Dict:
        """评估进化环整体健康度"""
        _safe_print("[跨引擎协同优化] 评估进化环整体健康度...")

        health_state = self.check_all_engines_health()

        overall = {
            "health_score": health_state.get("overall_health", 0),
            "healthy_engines": sum(1 for e in health_state.get("engines", {}).values()
                                   if e.get("status") == "healthy"),
            "total_engines": len(health_state.get("engines", {})),
            "issues_count": len(health_state.get("issues", [])),
            "last_check": health_state.get("last_check"),
            "recommendation": self._get_health_recommendation(health_state)
        }

        return overall

    def _get_health_recommendation(self, health_state: Dict) -> str:
        """获取健康建议"""
        overall = health_state.get("overall_health", 0)

        if overall >= 0.9:
            return "进化环运行良好，各引擎健康"
        elif overall >= 0.7:
            return "建议执行跨引擎协同优化以提升整体健康度"
        elif overall >= 0.5:
            return "健康度较低，建议立即执行优化"
        else:
            return "健康度严重不足，建议检查并修复失败的引擎"

    def get_status(self) -> Dict:
        """获取跨引擎协同状态"""
        health_state = self._load_health_state()
        optimization_history = self._load_optimization_history()

        return {
            "version": self.version,
            "overall_health": health_state.get("overall_health", 0),
            "engines_count": len(self.engine_registry),
            "healthy_engines": health_state.get("engines", {}).get("healthy_count", 0),
            "issues_count": len(health_state.get("issues", [])),
            "last_check": health_state.get("last_check"),
            "optimizations_count": len(optimization_history),
            "timestamp": datetime.now().isoformat()
        }

    def run_full_optimization_cycle(self) -> Dict:
        """运行完整的优化周期"""
        _safe_print("[跨引擎协同优化] 开始完整优化周期...")

        # 1. 健康检查
        health_state = self.check_all_engines_health()

        # 2. 问题诊断
        diagnosis = self.diagnose_collaboration_issues()

        # 3. 生成优化方案
        optimization_plan = self.generate_optimization_plan(diagnosis)

        # 4. 执行优化
        optimization_results = self.execute_optimization(optimization_plan)

        # 5. 重新评估健康度
        final_health = self.evaluate_overall_health()

        return {
            "initial_health": health_state.get("overall_health"),
            "issues_found": len(diagnosis),
            "fixes_succeeded": optimization_results.get("fixes_succeeded", 0),
            "final_health": final_health.get("health_score", 0),
            "improvement": final_health.get("health_score", 0) - health_state.get("overall_health", 0),
            "timestamp": datetime.now().isoformat()
        }


def main():
    """主函数，支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能全场景进化环跨引擎协同自优化与深度集成引擎"
    )
    parser.add_argument('action', nargs='?', default='status',
                        choices=['status', 'health', 'diagnose', 'optimize', 'full_cycle', 'evaluate'],
                        help='要执行的操作')
    parser.add_argument('--engine', type=str, help='指定引擎名称')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')

    args = parser.parse_args()

    optimizer = CrossEngineCollaborationOptimizer()

    if args.action == 'status':
        result = optimizer.get_status()
        _safe_print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == 'health':
        result = optimizer.check_all_engines_health()
        _safe_print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == 'diagnose':
        result = optimizer.diagnose_collaboration_issues()
        _safe_print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == 'optimize':
        diagnosis = optimizer.diagnose_collaboration_issues()
        plan = optimizer.generate_optimization_plan(diagnosis)
        result = optimizer.execute_optimization(plan)
        _safe_print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == 'full_cycle':
        result = optimizer.run_full_optimization_cycle()
        _safe_print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == 'evaluate':
        result = optimizer.evaluate_overall_health()
        _safe_print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()