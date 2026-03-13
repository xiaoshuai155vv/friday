#!/usr/bin/env python3
"""
智能全系统引擎协同调度引擎

让系统能够根据任务需求智能选择和调度引擎组合，实现自适应任务分发与执行优化。
利用 LLM 的大规模分析能力和系统性自动化设计，实现真正的智能协同调度。

功能：
1. 扫描所有可用引擎及其能力分类
2. 分析任务需求，识别需要的引擎能力
3. 智能选择最合适的引擎组合
4. 优化执行顺序和参数
5. 实时追踪执行状态和结果
6. 学习最优调度策略

Version: 1.0.0
"""

import os
import json
import re
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import subprocess

# 项目根目录
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
RUNTIME_STATE = PROJECT_ROOT / "runtime" / "state"
RUNTIME_LOGS = PROJECT_ROOT / "runtime" / "logs"

# 引擎能力分类映射
ENGINE_CATEGORIES = {
    # 系统操作类
    "system_operations": ["power_tool", "process_tool", "network_tool", "window_tool", "volume_tool", "brightness_tool"],
    # 自动化执行类
    "automation": ["workflow_engine", "workflow_orchestrator", "run_plan", "automation_execution_engine"],
    # 智能服务类
    "intelligent_service": ["unified_service_hub", "intelligent_service_loop", "adaptive_scene_selector", "service_preheat_engine"],
    # 进化与学习类
    "evolution_learning": ["evolution_loop_automation", "evolution_strategy_engine", "evolution_learning_engine", "evolution_command_tower"],
    # 监控与诊断类
    "monitoring": ["system_health_check", "system_health_report_engine", "self_healing_engine", "security_monitor_engine"],
    # 用户交互类
    "user_interaction": ["conversation_manager", "emotion_engine", "active_suggestion_engine", "intent_deep_reasoning_engine"],
    # 数据分析类
    "data_analysis": ["data_insight_engine", "multi_dim_analysis_engine", "execution_log_analyzer", "behavior_sequence_prediction_engine"],
    # 知识管理类
    "knowledge": ["knowledge_graph", "knowledge_evolution_engine", "context_memory", "long_term_memory_engine"],
    # 跨引擎协同类
    "cross_engine": ["module_linkage_engine", "multi_agent_collaboration_engine", "engine_capability_activator", "cross_engine_optimizer"],
    # 文件操作类
    "file_operations": ["file_tool", "file_manager_engine", "file_watcher", "quick_look", "file_metadata"],
    # 媒体类
    "media": ["camera_qt", "selfie", "voice_interaction_engine", "tts_engine"],
    # 场景执行类
    "scenario": ["scenario_executor", "scene_execution_linkage_engine", "scenario_recommender", "scenario_followup_recommender"]
}


class EngineCollaborationOptimizer:
    """智能全系统引擎协同调度引擎"""

    def __init__(self):
        self.scripts_dir = PROJECT_ROOT / "scripts"
        self.runtime_state = RUNTIME_STATE
        self.project_root = PROJECT_ROOT
        self.optimizer_data_file = RUNTIME_STATE / "engine_collaboration_optimizer_data.json"
        self.load_data()

    def load_data(self):
        """加载调度优化数据"""
        if self.optimizer_data_file.exists():
            with open(self.optimizer_data_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            self.data = {
                "engines": {},
                "execution_history": [],
                "optimization_rules": {},
                "strategy_patterns": {}
            }

    def save_data(self):
        """保存调度优化数据"""
        with open(self.optimizer_data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def scan_all_engines(self):
        """扫描所有可用引擎"""
        engines = {}

        # 扫描 scripts 目录
        for py_file in self.scripts_dir.glob("*.py"):
            if py_file.name.startswith("_") or py_file.stem in ["do", "launch", "run_plan"]:
                continue

            engine_name = py_file.stem
            description = self._extract_description(py_file)
            engine_type = self._classify_engine(engine_name)

            engines[engine_name] = {
                "path": str(py_file),
                "description": description,
                "type": engine_type,
                "category": self._get_category(engine_name),
                "last_found": datetime.now().isoformat()
            }

        # 扫描 capabilities.md 获取更多信息
        capabilities_file = PROJECT_ROOT / "references" / "capabilities.md"
        if capabilities_file.exists():
            with open(capabilities_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 提取更多引擎信息
                for engine_name in engines:
                    if engine_name in content:
                        engines[engine_name]["in_capabilities"] = True

        self.data["engines"] = engines
        self.save_data()
        return engines

    def _extract_description(self, py_file):
        """从 Python 文件提取描述"""
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read(2000)
                # 查找文档字符串
                match = re.search(r'"""(.+?)"""', content, re.DOTALL)
                if match:
                    return match.group(1).strip().split('\n')[0][:100]
        except Exception:
            pass
        return "引擎功能描述"

    def _classify_engine(self, engine_name):
        """分类引擎"""
        name_lower = engine_name.lower()

        if any(x in name_lower for x in ["evolution", "learning", "meta", "self_"]):
            return "evolution_learning"
        elif any(x in name_lower for x in ["health", "monitor", "diagnos", "repair"]):
            return "monitoring"
        elif any(x in name_lower for x in ["service", "recommend", "suggest", "insight"]):
            return "intelligent_service"
        elif any(x in name_lower for x in ["workflow", "orchestrat", "plan", "auto"]):
            return "automation"
        elif any(x in name_lower for x in ["cross", "linkage", "multi_agent", "collaboration"]):
            return "cross_engine"
        elif any(x in name_lower for x in ["intent", "behavior", "context", "memory"]):
            return "user_interaction"
        elif any(x in name_lower for x in ["knowledge", "reasoning", "insight"]):
            return "knowledge"
        elif any(x in name_lower for x in ["file", "quick_look", "metadata"]):
            return "file_operations"
        elif any(x in name_lower for x in ["power", "process", "network", "window", "volume", "brightness"]):
            return "system_operations"
        elif any(x in name_lower for x in ["vision", "screenshot", "mouse", "keyboard"]):
            return "user_interaction"
        else:
            return "general"

    def _get_category(self, engine_name):
        """获取引擎类别"""
        for category, engines in ENGINE_CATEGORIES.items():
            if engine_name in engines:
                return category
        return "general"

    def analyze_task_requirements(self, task_description):
        """分析任务需求，识别需要的引擎能力"""
        task_lower = task_description.lower()

        required_engines = []
        required_categories = set()

        # 基于关键词匹配识别需求
        keyword_mapping = {
            "系统健康": ["system_health_check", "system_health_report_engine"],
            "监控": ["security_monitor_engine", "system_health_check"],
            "优化": ["self_healing_engine", "cross_engine_optimizer"],
            "自动执行": ["workflow_engine", "workflow_orchestrator"],
            "服务": ["unified_service_hub", "intelligent_service_loop"],
            "进化": ["evolution_loop_automation", "evolution_command_tower"],
            "学习": ["evolution_learning_engine", "adaptive_learning_engine"],
            "推荐": ["scenario_recommender", "unified_recommender"],
            "洞察": ["data_insight_engine", "proactive_insight_engine"],
            "知识": ["knowledge_graph", "knowledge_evolution_engine"],
            "文件": ["file_tool", "file_manager_engine"],
            "窗口": ["window_tool"],
            "进程": ["process_tool"],
            "网络": ["network_tool"],
            "电源": ["power_tool"],
            "通知": ["notification_tool"],
            "截图": ["screenshot_tool"],
            "鼠标": ["mouse_tool"],
            "键盘": ["keyboard_tool"],
        }

        for keyword, engines in keyword_mapping.items():
            if keyword in task_lower:
                required_engines.extend(engines)
                required_categories.add(self._get_category(engines[0]))

        return {
            "task_description": task_description,
            "required_engines": list(set(required_engines)),
            "required_categories": list(required_categories),
            "keywords_found": [k for k in keyword_mapping if k in task_lower]
        }

    def select_optimal_engines(self, task_requirements):
        """智能选择最优引擎组合"""
        available_engines = self.data.get("engines", {})
        required = task_requirements.get("required_engines", [])
        categories = task_requirements.get("required_categories", [])

        # 如果没有扫描过，先扫描
        if not available_engines:
            available_engines = self.scan_all_engines()

        selected = []
        used_categories = set()

        # 首先选择直接匹配的引擎
        for engine_name in required:
            if engine_name in available_engines:
                selected.append({
                    "engine": engine_name,
                    "reason": "直接匹配任务需求",
                    "priority": 1
                })

        # 然后添加类别代表性引擎
        for category in categories:
            if not selected or len(selected) < 3:
                # 选择该类别的代表性引擎
                for engine_name, info in available_engines.items():
                    if info.get("category") == category and engine_name not in [s["engine"] for s in selected]:
                        selected.append({
                            "engine": engine_name,
                            "reason": f"类别 {category} 代表引擎",
                            "priority": 2
                        })
                        break

        return selected

    def optimize_execution_order(self, selected_engines):
        """优化引擎执行顺序"""
        # 基于依赖关系的排序
        priority_order = {
            "system_operations": 1,
            "monitoring": 2,
            "knowledge": 3,
            "intelligent_service": 4,
            "automation": 5,
            "cross_engine": 6,
            "data_analysis": 7,
            "evolution_learning": 8,
            "user_interaction": 9,
            "file_operations": 10,
            "media": 11,
            "scenario": 12
        }

        sorted_engines = sorted(selected_engines, key=lambda x:
            priority_order.get(
                self.data.get("engines", {}).get(x["engine"], {}).get("category", "general"),
                99
            ))

        return sorted_engines

    def execute_collaboration(self, task_description, dry_run=True):
        """执行引擎协同调度"""
        # 1. 分析任务需求
        requirements = self.analyze_task_requirements(task_description)

        # 2. 选择最优引擎
        selected = self.select_optimal_engines(requirements)

        # 3. 优化执行顺序
        optimized = self.optimize_execution_order(selected)

        result = {
            "task_description": task_description,
            "requirements": requirements,
            "selected_engines": optimized,
            "execution_mode": "dry_run" if dry_run else "execute",
            "timestamp": datetime.now().isoformat()
        }

        # 记录到历史
        self.data["execution_history"].append(result)
        self.save_data()

        return result

    def get_optimizer_status(self):
        """获取优化器状态"""
        engines = self.data.get("engines", {})
        history = self.data.get("execution_history", [])

        return {
            "total_engines": len(engines),
            "total_executions": len(history),
            "categories": len(ENGINE_CATEGORIES),
            "last_scan": engines.get(list(engines.keys())[0], {}).get("last_found", "N/A") if engines else "N/A"
        }

    def suggest_optimizations(self):
        """生成优化建议"""
        history = self.data.get("execution_history", [])
        if not history:
            return "暂无执行历史，建议先执行一次协同调度"

        # 分析执行模式
        engine_usage = defaultdict(int)
        category_usage = defaultdict(int)

        for exec_item in history:
            for selected in exec_item.get("selected_engines", []):
                engine_name = selected.get("engine")
                engine_usage[engine_name] += 1

                # 统计类别使用
                engine_info = self.data.get("engines", {}).get(engine_name, {})
                category = engine_info.get("category", "general")
                category_usage[category] += 1

        suggestions = []
        suggestions.append(f"系统共有 {len(self.data.get('engines', {}))} 个可用引擎")
        suggestions.append(f"历史执行 {len(history)} 次")

        # 找出使用频率最低但可能有价值的引擎
        unused_engines = [e for e in self.data.get("engines", {}).keys()
                         if e not in engine_usage]
        if unused_engines:
            suggestions.append(f"建议尝试未使用过的引擎: {', '.join(unused_engines[:5])}")

        return "\n".join(suggestions)


def main():
    """主函数 - 支持命令行调用"""
    if len(sys.argv) < 2:
        print("智能全系统引擎协同调度引擎")
        print("\n用法:")
        print("  python engine_collaboration_optimizer.py scan           - 扫描所有引擎")
        print("  python engine_collaboration_optimizer.py analyze <任务>  - 分析任务需求")
        print("  python engine_collaboration_optimizer.py select <任务>   - 选择最优引擎")
        print("  python engine_collaboration_optimizer.py execute <任务>  - 执行协同调度")
        print("  python engine_collaboration_optimizer.py status          - 查看状态")
        print("  python engine_collaboration_optimizer.py suggest        - 获取优化建议")
        return

    optimizer = EngineCollaborationOptimizer()
    command = sys.argv[1].lower()

    if command == "scan":
        engines = optimizer.scan_all_engines()
        print(f"扫描完成，共发现 {len(engines)} 个引擎:")
        for name, info in engines.items():
            print(f"  - {name} ({info.get('category', 'general')}): {info.get('description', '')[:50]}")

    elif command == "analyze":
        task = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "系统优化"
        result = optimizer.analyze_task_requirements(task)
        print(f"任务需求分析: {task}")
        print(f"需要引擎: {result.get('required_engines', [])}")
        print(f"需要类别: {result.get('required_categories', [])}")

    elif command == "select":
        task = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "系统优化"
        result = optimizer.analyze_task_requirements(task)
        selected = optimizer.select_optimal_engines(result)
        print(f"为任务 '{task}' 选择的引擎:")
        for s in selected:
            print(f"  - {s['engine']} (优先级: {s['priority']}, 原因: {s['reason']})")

    elif command == "execute":
        task = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "系统优化"
        result = optimizer.execute_collaboration(task, dry_run=True)
        print(f"协同调度结果:")
        print(f"  任务: {result['task_description']}")
        print(f"  选中引擎数: {len(result['selected_engines'])}")
        for s in result['selected_engines']:
            print(f"    - {s['engine']}")

    elif command == "status":
        status = optimizer.get_optimizer_status()
        print("引擎协同调度器状态:")
        print(f"  总引擎数: {status['total_engines']}")
        print(f"  总执行次数: {status['total_executions']}")
        print(f"  引擎类别数: {status['categories']}")
        print(f"  最后扫描: {status['last_scan']}")

    elif command == "suggest":
        suggestions = optimizer.suggest_optimizations()
        print("优化建议:")
        print(suggestions)

    else:
        print(f"未知命令: {command}")
        print("支持的命令: scan, analyze, select, execute, status, suggest")


if __name__ == "__main__":
    main()