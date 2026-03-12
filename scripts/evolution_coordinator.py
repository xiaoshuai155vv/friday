#!/usr/bin/env python3
"""
智能进化协调器 - 统一现有进化模块接口，增强整体智能联动

功能：
1. 统一调用所有进化模块（策略、分析、评估、自动化、学习、历史）
2. 提供一键智能进化能力
3. 智能调度和联动各模块
4. 输出统一的进化报告

使用方法：
    python evolution_coordinator.py status      - 查看整体状态
    python evolution_coordinator.py run        - 执行完整进化流程
    python evolution_coordinator.py analyze    - 分析当前状态
    python evolution_coordinator.py learn       - 运行学习引擎
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE = PROJECT_ROOT / "runtime" / "state"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# 确保目录存在
RUNTIME_STATE.mkdir(parents=True, exist_ok=True)


class EvolutionCoordinator:
    """智能进化协调器"""

    def __init__(self):
        self.state_dir = RUNTIME_STATE
        self.scripts_dir = SCRIPTS_DIR
        self.output_file = self.state_dir / "evolution_coordinator_status.json"

        # 进化模块列表
        self.modules = {
            "strategy": "evolution_strategy_engine.py",
            "analyzer": "evolution_log_analyzer.py",
            "evaluator": "evolution_self_evaluator.py",
            "automation": "evolution_loop_automation.py",
            "history": "evolution_history_db.py",
            "learning": "evolution_learning_engine.py"
        }

    def run_module(self, module_name: str, command: str = "status") -> Dict[str, Any]:
        """运行指定的进化模块"""
        if module_name not in self.modules:
            return {"error": f"未知模块: {module_name}"}

        script_path = self.scripts_dir / self.modules[module_name]

        if not script_path.exists():
            return {"error": f"模块不存在: {script_path}"}

        try:
            result = subprocess.run(
                [sys.executable, str(script_path), command],
                capture_output=True,
                text=True,
                timeout=60
            )

            # 解析 JSON 输出
            output = result.stdout.strip()
            if output.startswith('{'):
                return json.loads(output)
            else:
                # 非 JSON 输出，尝试提取 JSON 部分
                json_start = output.find('{')
                if json_start != -1:
                    return json.loads(output[json_start:])
                return {"raw_output": output, "returncode": result.returncode}

        except subprocess.TimeoutExpired:
            return {"error": f"模块执行超时: {module_name}"}
        except Exception as e:
            return {"error": str(e)}

    def check_module_status(self, module_name: str) -> Dict[str, Any]:
        """检查单个模块状态"""
        script_path = self.scripts_dir / self.modules.get(module_name, "")

        if not script_path.exists():
            return {"available": False, "error": "模块文件不存在"}

        return {
            "available": True,
            "path": str(script_path),
            "size": script_path.stat().st_size if script_path.exists() else 0
        }

    def get_all_modules_status(self) -> Dict[str, Any]:
        """获取所有模块状态"""
        status = {"modules": {}, "summary": {}}

        available_count = 0
        for module_name in self.modules:
            module_status = self.check_module_status(module_name)
            status["modules"][module_name] = module_status
            if module_status.get("available"):
                available_count += 1

        status["summary"] = {
            "total": len(self.modules),
            "available": available_count,
            "timestamp": datetime.now().isoformat()
        }

        return status

    def run_full_evolution_cycle(self) -> Dict[str, Any]:
        """运行完整进化周期"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "cycle_started": True,
            "modules_executed": [],
            "module_results": {}
        }

        # 按顺序执行各模块
        execution_order = ["strategy", "analyzer", "evaluator", "learning"]

        for module in execution_order:
            results["modules_executed"].append(module)
            try:
                # 每个模块执行 analyze 或 status 命令
                if module == "strategy":
                    result = self.run_module(module, "analyze")
                elif module == "analyzer":
                    result = self.run_module(module, "analyze")
                elif module == "evaluator":
                    result = self.run_module(module, "evaluate")
                elif module == "learning":
                    result = self.run_module(module, "learn")
                else:
                    result = self.run_module(module, "status")

                results["module_results"][module] = result

            except Exception as e:
                results["module_results"][module] = {"error": str(e)}

        results["cycle_completed"] = True
        return results

    def analyze_current_state(self) -> Dict[str, Any]:
        """分析当前状态"""
        # 获取所有模块状态
        modules_status = self.get_all_modules_status()

        # 尝试运行各模块获取数据
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "modules_status": modules_status,
            "overall_health": self._calculate_health(modules_status),
            "recommendations": self._generate_recommendations(modules_status)
        }

        return analysis

    def _calculate_health(self, modules_status: Dict[str, Any]) -> Dict[str, Any]:
        """计算整体健康度"""
        summary = modules_status.get("summary", {})
        total = summary.get("total", 0)
        available = summary.get("available", 0)

        health_score = (available / total * 100) if total > 0 else 0

        return {
            "score": health_score,
            "status": "healthy" if health_score >= 80 else "degraded" if health_score >= 50 else "critical",
            "modules_ready": available,
            "modules_total": total
        }

    def _generate_recommendations(self, modules_status: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成推荐"""
        recommendations = []
        health = self._calculate_health(modules_status)

        if health["status"] == "critical":
            recommendations.append({
                "priority": "critical",
                "action": "修复缺失的进化模块",
                "description": "多个进化模块不可用，需要修复"
            })
        elif health["status"] == "degraded":
            recommendations.append({
                "priority": "medium",
                "action": "补充缺失模块功能",
                "description": "部分进化模块缺失，建议补充"
            })
        else:
            recommendations.append({
                "priority": "low",
                "action": "执行完整进化周期",
                "description": "所有模块就绪，可以执行智能进化"
            })

        # 添加优化建议
        recommendations.append({
            "priority": "low",
            "action": "优化模块联动",
            "description": "考虑增强各模块间的数据共享和联动能力"
        })

        return recommendations

    def get_status(self) -> Dict[str, Any]:
        """获取整体状态"""
        analysis = self.analyze_current_state()

        return {
            "coordinator": "EvolutionCoordinator",
            "version": "1.0",
            "status": "active",
            "health": analysis["overall_health"],
            "modules": list(self.modules.keys()),
            "timestamp": datetime.now().isoformat()
        }

    def save_status(self, status: Dict[str, Any]) -> None:
        """保存状态到文件"""
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(status, f, ensure_ascii=False, indent=2)


def main():
    """主函数"""
    coordinator = EvolutionCoordinator()

    if len(sys.argv) < 2:
        print("智能进化协调器")
        print("用法:")
        print("  python evolution_coordinator.py status    - 查看整体状态")
        print("  python evolution_coordinator.py run       - 执行完整进化流程")
        print("  python evolution_coordinator.py analyze  - 分析当前状态")
        print("  python evolution_coordinator.py modules  - 查看所有模块状态")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "status":
        result = coordinator.get_status()
        coordinator.save_status(result)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "run":
        result = coordinator.run_full_evolution_cycle()
        coordinator.save_status(result)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "analyze":
        result = coordinator.analyze_current_state()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "modules":
        result = coordinator.get_all_modules_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()