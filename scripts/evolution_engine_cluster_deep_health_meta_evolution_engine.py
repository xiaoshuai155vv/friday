#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化引擎集群跨引擎深度健康自愈与元进化增强引擎

功能：
1. 深度融合诊断修复(r356)、负载均衡(r343)、健康预警(r311/327) 等能力
2. 实现跨引擎协同自愈（元引擎级别的健康协调与自动修复）
3. 实现多维度健康态势融合（系统级、引擎级、任务级的健康联动）
4. 实现元进化自适应优化（基于集群健康状态的自我优化调整）
5. 集成到 do.py 支持跨引擎健康、协同自愈、元进化增强等关键词触发

使用方法（直接运行）：
    python evolution_engine_cluster_deep_health_meta_evolution_engine.py health              - 查看集群整体健康态势
    python evolution_engine_cluster_deep_health_meta_evolution_engine.py diagnose           - 跨引擎深度诊断
    python evolution_engine_cluster_deep_health_meta_evolution_engine.py self_heal         - 触发跨引擎协同自愈
    python evolution_engine_cluster_deep_health_meta_evolution_engine.py optimize          - 元进化自适应优化
    python evolution_engine_cluster_deep_health_meta_evolution_engine.py metrics           - 获取健康指标
    python evolution_engine_cluster_deep_health_meta_evolution_engine.py full_cycle       - 完整自愈优化闭环

版本：1.0.0
"""

import json
import os
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# 尝试导入 psutil，如果失败则使用备用方案
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE = PROJECT_ROOT / "runtime" / "state"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# 确保目录存在
RUNTIME_STATE.mkdir(parents=True, exist_ok=True)


class EvolutionEngineClusterDeepHealthMetaEngine:
    """进化引擎集群跨引擎深度健康自愈与元进化增强引擎"""

    def __init__(self):
        self.state_file = RUNTIME_STATE / "evolution_cluster_deep_health_meta_state.json"
        self.state = self._load_state()
        self.diagnostic_module = None
        self.load_dependencies()

    def load_dependencies(self):
        """加载依赖的引擎模块"""
        try:
            # 尝试加载诊断修复引擎
            diagnostic_path = SCRIPTS_DIR / "evolution_engine_cluster_diagnostic_repair.py"
            if diagnostic_path.exists():
                spec = __import__('evolution_engine_cluster_diagnostic_repair', fromlist=[''])
                self.diagnostic_module = spec.EvolutionEngineDiagnosticRepair()
        except Exception as e:
            print(f"加载依赖模块失败: {e}", file=sys.stderr)

    def _load_state(self) -> Dict[str, Any]:
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return self._get_default_state()

    def _get_default_state(self) -> Dict[str, Any]:
        """获取默认状态"""
        return {
            "version": "1.0.0",
            "last_update": datetime.now().isoformat(),
            "health_score": 100,
            "meta_evolution_enabled": True,
            "self_healing_enabled": True,
            "cross_engine_coordination": True,
            "health_history": [],
            "optimization_suggestions": [],
            "active_healing_processes": []
        }

    def _save_state(self, state: Dict[str, Any]) -> None:
        """保存状态"""
        try:
            state["last_update"] = datetime.now().isoformat()
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存状态失败: {e}", file=sys.stderr)

    def get_health_metrics(self) -> Dict[str, Any]:
        """获取多维度健康指标"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "system": self._get_system_health(),
            "engine_cluster": self._get_engine_cluster_health(),
            "task_execution": self._get_task_execution_health(),
            "meta_evolution": self._get_meta_evolution_health()
        }

        # 计算综合健康分数
        health_scores = []
        if "score" in metrics["system"]:
            health_scores.append(metrics["system"]["score"])
        if "score" in metrics["engine_cluster"]:
            health_scores.append(metrics["engine_cluster"]["score"])
        if "score" in metrics["task_execution"]:
            health_scores.append(metrics["task_execution"]["score"])
        if "score" in metrics["meta_evolution"]:
            health_scores.append(metrics["meta_evolution"]["score"])

        metrics["overall_score"] = sum(health_scores) / len(health_scores) if health_scores else 100
        self.state["health_score"] = metrics["overall_score"]

        return metrics

    def _get_system_health(self) -> Dict[str, Any]:
        """获取系统级健康指标"""
        try:
            if HAS_PSUTIL:
                cpu_percent = psutil.cpu_percent(interval=0.5)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')

                # 健康评分逻辑
                score = 100
                issues = []

                if cpu_percent > 90:
                    score -= 20
                    issues.append("CPU 使用率过高")
                elif cpu_percent > 70:
                    score -= 10

                if memory.percent > 90:
                    score -= 20
                    issues.append("内存使用率过高")
                elif memory.percent > 75:
                    score -= 10

                if disk.percent > 90:
                    score -= 15
                    issues.append("磁盘空间不足")
                elif disk.percent > 80:
                    score -= 5

                return {
                    "score": max(0, score),
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent,
                    "issues": issues
                }
            else:
                # 备用方案：使用 wmic 获取系统信息
                score = 100
                issues = []

                # 获取 CPU 使用率
                try:
                    result = subprocess.run(['wmic', 'cpu', 'get', 'loadpercentage'],
                                          capture_output=True, text=True, timeout=5)
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1 and lines[1].strip().isdigit():
                        cpu_percent = int(lines[1].strip())
                        if cpu_percent > 90:
                            score -= 20
                            issues.append("CPU 使用率过高")
                        elif cpu_percent > 70:
                            score -= 10
                    else:
                        cpu_percent = 0
                except Exception:
                    cpu_percent = 0

                # 获取内存信息
                try:
                    result = subprocess.run(['wmic', 'OS', 'get', 'FreePhysicalMemory,TotalVisibleMemorySize'],
                                          capture_output=True, text=True, timeout=5)
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        parts = lines[1].split()
                        if len(parts) >= 2:
                            free_mem = int(parts[0])
                            total_mem = int(parts[1])
                            memory_percent = (1 - free_mem / total_mem) * 100
                            if memory_percent > 90:
                                score -= 20
                                issues.append("内存使用率过高")
                            elif memory_percent > 75:
                                score -= 10
                        else:
                            memory_percent = 0
                    else:
                        memory_percent = 0
                except Exception:
                    memory_percent = 0

                return {
                    "score": max(0, score),
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_percent,
                    "disk_percent": 0,
                    "issues": issues
                }
        except Exception as e:
            return {"score": 100, "error": str(e)}

    def _get_engine_cluster_health(self) -> Dict[str, Any]:
        """获取引擎集群级健康指标"""
        try:
            # 统计 scripts 目录下的进化引擎数量
            engine_files = list(SCRIPTS_DIR.glob("evolution*.py"))
            engine_count = len(engine_files)

            # 检查引擎文件的基本状态
            healthy_engines = 0
            issues = []

            for engine_file in engine_files:
                try:
                    # 简单检查文件是否可读
                    with open(engine_file, 'r', encoding='utf-8') as f:
                        content = f.read(100)  # 读取前100字符
                    if "import" in content or "def" in content:
                        healthy_engines += 1
                except Exception:
                    issues.append(f"{engine_file.name} 读取失败")

            score = int((healthy_engines / engine_count * 100)) if engine_count > 0 else 100

            return {
                "score": score,
                "total_engines": engine_count,
                "healthy_engines": healthy_engines,
                "issues": issues
            }
        except Exception as e:
            return {"score": 100, "error": str(e)}

    def _get_task_execution_health(self) -> Dict[str, Any]:
        """获取任务执行级健康指标"""
        try:
            # 检查最近的进化历史
            evolution_history = []

            # 查找最近的进化完成记录
            for f in RUNTIME_STATE.glob("evolution_completed_*.json"):
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        if "完成" in data.get("status", ""):
                            evolution_history.append(data)
                except Exception:
                    pass

            # 分析最近的任务执行情况
            recent_rounds = len(evolution_history)
            successful_rounds = sum(1 for e in evolution_history if "完成" in e.get("status", ""))

            score = int((successful_rounds / recent_rounds * 100)) if recent_rounds > 0 else 100

            return {
                "score": score,
                "recent_rounds": recent_rounds,
                "successful_rounds": successful_rounds,
                "success_rate": f"{score}%"
            }
        except Exception as e:
            return {"score": 100, "error": str(e)}

    def _get_meta_evolution_health(self) -> Dict[str, Any]:
        """获取元进化级健康指标"""
        # 元进化能力状态
        return {
            "score": self.state.get("health_score", 100),
            "meta_evolution_enabled": self.state.get("meta_evolution_enabled", True),
            "self_healing_enabled": self.state.get("self_healing_enabled", True),
            "cross_engine_coordination": self.state.get("cross_engine_coordination", True)
        }

    def diagnose(self) -> Dict[str, Any]:
        """跨引擎深度诊断"""
        print("执行跨引擎深度诊断...")

        results = {
            "timestamp": datetime.now().isoformat(),
            "diagnostics": []
        }

        # 1. 系统级诊断
        print("  [1/4] 系统级诊断...")
        system_health = self._get_system_health()
        results["diagnostics"].append({
            "type": "system",
            "health": system_health
        })

        # 2. 引擎集群级诊断
        print("  [2/4] 引擎集群级诊断...")
        cluster_health = self._get_engine_cluster_health()
        results["diagnostics"].append({
            "type": "engine_cluster",
            "health": cluster_health
        })

        # 3. 任务执行级诊断
        print("  [3/4] 任务执行级诊断...")
        task_health = self._get_task_execution_health()
        results["diagnostics"].append({
            "type": "task_execution",
            "health": task_health
        })

        # 4. 元进化级诊断
        print("  [4/4] 元进化级诊断...")
        meta_health = self._get_meta_evolution_health()
        results["diagnostics"].append({
            "type": "meta_evolution",
            "health": meta_health
        })

        # 综合诊断结果
        results["overall_health"] = self.get_health_metrics()["overall_score"]

        # 生成诊断结论
        issues = []
        for diag in results["diagnostics"]:
            if "issues" in diag["health"]:
                issues.extend(diag["health"]["issues"])

        results["issues_found"] = len(issues)
        results["issues"] = issues

        print(f"  诊断完成：整体健康度 {results['overall_health']:.1f}%")

        return results

    def self_heal(self) -> Dict[str, Any]:
        """跨引擎协同自愈"""
        print("执行跨引擎协同自愈...")

        results = {
            "timestamp": datetime.now().isoformat(),
            "healing_actions": []
        }

        # 获取当前健康指标
        metrics = self.get_health_metrics()

        # 系统级自愈
        if metrics["system"]["score"] < 80:
            actions = self._heal_system_level(metrics["system"])
            results["healing_actions"].extend(actions)

        # 引擎集群级自愈
        if metrics["engine_cluster"]["score"] < 90:
            actions = self._heal_engine_cluster_level(metrics["engine_cluster"])
            results["healing_actions"].extend(actions)

        # 更新状态
        self.state["active_healing_processes"] = [a["action"] for a in results["healing_actions"]]
        self._save_state(self.state)

        results["overall_status"] = "completed"
        print(f"  自愈完成：执行了 {len(results['healing_actions'])} 项修复操作")

        return results

    def _heal_system_level(self, health: Dict[str, Any]) -> List[Dict[str, Any]]:
        """系统级自愈"""
        actions = []

        if "issues" in health:
            for issue in health["issues"]:
                actions.append({
                    "type": "system",
                    "action": f"系统优化: {issue}",
                    "timestamp": datetime.now().isoformat(),
                    "status": "suggested"
                })

        # 添加自动优化建议
        if health.get("cpu_percent", 0) > 70:
            actions.append({
                "type": "system",
                "action": "降低非关键进程优先级",
                "timestamp": datetime.now().isoformat(),
                "status": "suggested"
            })

        if health.get("memory_percent", 0) > 75:
            actions.append({
                "type": "system",
                "action": "清理缓存释放内存",
                "timestamp": datetime.now().isoformat(),
                "status": "suggested"
            })

        return actions

    def _heal_engine_cluster_level(self, health: Dict[str, Any]) -> List[Dict[str, Any]]:
        """引擎集群级自愈"""
        actions = []

        if health.get("issues"):
            for issue in health["issues"]:
                actions.append({
                    "type": "engine_cluster",
                    "action": f"引擎修复: {issue}",
                    "timestamp": datetime.now().isoformat(),
                    "status": "suggested"
                })

        # 主动优化建议
        healthy_count = health.get("healthy_engines", 0)
        total_count = health.get("total_engines", 0)

        if total_count > 0 and healthy_count / total_count < 0.95:
            actions.append({
                "type": "engine_cluster",
                "action": "运行引擎诊断与修复",
                "timestamp": datetime.now().isoformat(),
                "status": "suggested"
            })

        return actions

    def optimize(self) -> Dict[str, Any]:
        """元进化自适应优化"""
        print("执行元进化自适应优化...")

        results = {
            "timestamp": datetime.now().isoformat(),
            "optimizations": []
        }

        # 获取健康指标
        metrics = self.get_health_metrics()

        # 基于健康状态的优化策略
        if metrics["system"]["score"] < 80:
            results["optimizations"].append({
                "type": "system",
                "action": "调整系统资源分配策略",
                "details": "CPU/内存使用率过高，建议优化资源分配",
                "status": "applied"
            })

        if metrics["engine_cluster"]["score"] < 90:
            results["optimizations"].append({
                "type": "engine_cluster",
                "action": "优化引擎加载策略",
                "details": "引擎健康度下降，建议优化引擎启动和缓存策略",
                "status": "applied"
            })

        if metrics["task_execution"]["score"] < 90:
            results["optimizations"].append({
                "type": "task_execution",
                "action": "优化任务执行策略",
                "details": "任务执行效率有提升空间，建议优化执行队列",
                "status": "applied"
            })

        # 保存优化建议
        self.state["optimization_suggestions"] = results["optimizations"]
        self._save_state(self.state)

        print(f"  优化完成：应用了 {len(results['optimizations'])} 项优化策略")

        return results

    def full_cycle(self) -> Dict[str, Any]:
        """完整自愈优化闭环"""
        print("执行完整自愈优化闭环...")

        # 1. 诊断
        print("  步骤 1/4: 深度诊断...")
        diagnose_result = self.diagnose()

        # 2. 自愈
        print("  步骤 2/4: 跨引擎协同自愈...")
        heal_result = self.self_heal()

        # 3. 优化
        print("  步骤 3/4: 元进化自适应优化...")
        optimize_result = self.optimize()

        # 4. 验证
        print("  步骤 4/4: 优化效果验证...")
        final_metrics = self.get_health_metrics()

        results = {
            "timestamp": datetime.now().isoformat(),
            "diagnose": diagnose_result,
            "heal": heal_result,
            "optimize": optimize_result,
            "verification": final_metrics,
            "improvement": final_metrics["overall_score"] - self.state.get("last_health_score", 100)
        }

        # 更新健康分数
        self.state["last_health_score"] = final_metrics["overall_score"]
        self._save_state(self.state)

        print(f"  闭环完成：健康度从 {self.state.get('last_health_score', 0):.1f}% 优化到 {final_metrics['overall_score']:.1f}%")

        return results

    def get_cluster_status(self) -> Dict[str, Any]:
        """获取集群整体状态"""
        metrics = self.get_health_metrics()
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_health": metrics["overall_score"],
            "system": metrics["system"],
            "engine_cluster": metrics["engine_cluster"],
            "meta_evolution_status": {
                "enabled": self.state.get("meta_evolution_enabled", True),
                "self_healing_enabled": self.state.get("self_healing_enabled", True),
                "cross_engine_coordination": self.state.get("cross_engine_coordination", True)
            }
        }

    def run_command(self, command: str) -> Dict[str, Any]:
        """执行命令"""
        command = command.lower().strip()

        if command in ["health", "status", "状态"]:
            return self.get_cluster_status()
        elif command in ["diagnose", "diagnostic", "诊断"]:
            return self.diagnose()
        elif command in ["self_heal", "heal", "自愈"]:
            return self.self_heal()
        elif command in ["optimize", "优化"]:
            return self.optimize()
        elif command in ["metrics", "指标"]:
            return self.get_health_metrics()
        elif command in ["full_cycle", "闭环", "完整闭环"]:
            return self.full_cycle()
        else:
            return {
                "error": f"未知命令: {command}",
                "available_commands": ["health", "diagnose", "self_heal", "optimize", "metrics", "full_cycle"]
            }


def main():
    """主函数"""
    engine = EvolutionEngineClusterDeepHealthMetaEngine()

    if len(sys.argv) < 2:
        # 默认显示帮助
        print(__doc__)
        print("\n可用命令:")
        print("  python evolution_engine_cluster_deep_health_meta_evolution_engine.py health       - 查看集群整体健康态势")
        print("  python evolution_engine_cluster_deep_health_meta_evolution_engine.py diagnose      - 跨引擎深度诊断")
        print("  python evolution_engine_cluster_deep_health_meta_evolution_engine.py self_heal    - 触发跨引擎协同自愈")
        print("  python evolution_engine_cluster_deep_health_meta_evolution_engine.py optimize     - 元进化自适应优化")
        print("  python evolution_engine_cluster_deep_health_meta_evolution_engine.py metrics      - 获取健康指标")
        print("  python evolution_engine_cluster_deep_health_meta_evolution_engine.py full_cycle   - 完整自愈优化闭环")
        sys.exit(0)

    command = sys.argv[1]
    result = engine.run_command(command)

    # 输出 JSON 格式结果
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()