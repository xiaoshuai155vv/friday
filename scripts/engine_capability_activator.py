#!/usr/bin/env python3
"""
智能引擎能力激活与自适应推荐引擎

让系统能够根据当前上下文（时间、任务类型、历史行为）主动推荐被忽视但可能非常有用的引擎能力，
实现从「被动等待调用」到「主动价值发现」的范式升级。

功能：
1. 扫描所有可用引擎及其使用情况
2. 分析引擎的能力分类和功能描述
3. 根据当前上下文推荐被忽视的引擎
4. 主动展示能力价值，引导用户使用
5. 跟踪推荐效果，学习最佳推荐策略
"""

import os
import json
import re
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# 项目根目录
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
RUNTIME_STATE = PROJECT_ROOT / "runtime" / "state"
RUNTIME_LOGS = PROJECT_ROOT / "runtime" / "logs"

class EngineCapabilityActivator:
    """智能引擎能力激活与自适应推荐引擎"""

    def __init__(self):
        self.scripts_dir = PROJECT_ROOT / "scripts"
        self.runtime_state = RUNTIME_STATE
        self.project_root = PROJECT_ROOT
        self.engine_data_file = RUNTIME_STATE / "engine_capability_activator_data.json"
        self.load_data()

    def load_data(self):
        """加载引擎激活数据"""
        if self.engine_data_file.exists():
            with open(self.engine_data_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            self.data = {
                "engines": {},
                "recommendations": [],
                "usage_history": [],
                "context_patterns": {}
            }

    def save_data(self):
        """保存引擎激活数据"""
        with open(self.engine_data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def scan_all_engines(self):
        """扫描所有可用引擎"""
        engines = {}

        # 1. 扫描 scripts 目录下的所有 Python 脚本
        for py_file in self.scripts_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue

            engine_name = py_file.stem
            # 读取文件获取功能描述
            description = self._extract_description(py_file)
            # 判断引擎类型
            engine_type = self._classify_engine(engine_name)

            engines[engine_name] = {
                "path": str(py_file),
                "description": description,
                "type": engine_type,
                "last_found": datetime.now().isoformat()
            }

        # 2. 从 capabilities.md 获取更多信息
        capabilities_file = PROJECT_ROOT / "references" / "capabilities.md"
        if capabilities_file.exists():
            with open(capabilities_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 提取已记录的引擎能力
                for engine_name, engine_info in engines.items():
                    if engine_name in content:
                        # 尝试提取更详细的描述
                        pattern = rf'{re.escape(engine_name)}.*?`([^`]+)`'
                        match = re.search(pattern, content)
                        if match:
                            engines[engine_name]["capability_desc"] = match.group(1)

        # 3. 从 meta_evolution_report 获取使用情况
        meta_report = RUNTIME_STATE / "meta_evolution_report.json"
        if meta_report.exists():
            try:
                with open(meta_report, 'r', encoding='utf-8') as f:
                    meta_data = json.load(f)

                # 标记未使用的引擎
                if "summary" in meta_data and "uncategorized" in meta_data["summary"]:
                    unused = meta_data["summary"]["uncategorized"]
                    for name in unused:
                        if name in engines:
                            engines[name]["usage_status"] = "unused"
            except:
                pass

        self.data["engines"] = engines
        self.save_data()
        return engines

    def _extract_description(self, py_file):
        """从 Python 文件提取功能描述"""
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read(2000)  # 只读开头部分

                # 查找文档字符串
                docstring_match = re.search(r'"""(.+?)"""', content, re.DOTALL)
                if docstring_match:
                    desc = docstring_match.group(1).strip().split('\n')[0]
                    return desc[:200]  # 限制长度

                # 查找注释中的功能描述
                comment_match = re.search(r'^#\s*(.+)', content, re.MULTILINE)
                if comment_match:
                    return comment_match.group(1).strip()[:200]
        except:
            pass

        return "功能描述未知"

    def _classify_engine(self, engine_name):
        """分类引擎类型"""
        name_lower = engine_name.lower()

        categories = {
            "evolution": ["evolution", "meta", "self_", "loop"],
            "monitoring": ["monitor", "health", "insight", "security", "diagnostic"],
            "automation": ["auto", "workflow", "orchestrator", "executor", "trigger"],
            "learning": ["learn", "adaptive", "personalization", "preference", "behavior"],
            "service": ["service", "notification", "proactive", "decision"],
            "interaction": ["conversation", "voice", "tts", "emotion", "intent"],
            "system": ["system", "process", "power", "network", "file", "clipboard"],
            "vision": ["vision", "screenshot", "ui_", "scene"],
            "execution": ["task", "execution", "run_", "do"],
            "data": ["knowledge", "graph", "memory", "context"],
        }

        for category, keywords in categories.items():
            if any(kw in name_lower for kw in keywords):
                return category

        return "general"

    def analyze_context(self):
        """分析当前上下文"""
        context = {
            "time": datetime.now(),
            "hour": datetime.now().hour,
            "day_of_week": datetime.now().weekday(),
            "recent_engines": self._get_recent_engines(),
            "system_state": self._get_system_state()
        }

        # 根据时间判断场景
        if 9 <= context["hour"] < 12:
            context["time_period"] = "morning"
        elif 12 <= context["hour"] < 14:
            context["time_period"] = "noon"
        elif 14 <= context["hour"] < 18:
            context["time_period"] = "afternoon"
        elif 18 <= context["hour"] < 22:
            context["time_period"] = "evening"
        else:
            context["time_period"] = "night"

        # 工作日判断
        context["is_weekend"] = context["day_of_week"] >= 5

        return context

    def _get_recent_engines(self):
        """获取最近使用的引擎"""
        recent = []
        try:
            recent_logs = RUNTIME_STATE / "recent_logs.json"
            if recent_logs.exists():
                with open(recent_logs, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                    if "entries" in logs:
                        for entry in logs["entries"][-20:]:  # 最近20条
                            if "desc" in entry:
                                recent.append(entry["desc"])
        except:
            pass

        return recent

    def _get_system_state(self):
        """获取系统状态"""
        state = {"has_ihaier": False, "has_browser": False}

        try:
            import psutil
            for proc in psutil.process_iter(['name']):
                name = proc.info['name'].lower() if proc.info['name'] else ""
                if 'ihaier' in name or 'iHaier' in name:
                    state["has_ihaier"] = True
                if 'msedge' in name or 'chrome' in name or 'firefox' in name:
                    state["has_browser"] = True
        except:
            pass

        return state

    def generate_recommendations(self, context=None):
        """根据上下文生成引擎推荐"""
        if context is None:
            context = self.analyze_context()

        if not self.data.get("engines"):
            self.scan_all_engines()

        recommendations = []

        # 按类型分组引擎
        engines_by_type = defaultdict(list)
        for name, info in self.data["engines"].items():
            engines_by_type[info.get("type", "general")].append((name, info))

        # 根据时间上下文推荐
        time_recommendations = {
            "morning": ["proactive_operations_engine", "task_scheduler", "focus_reminder"],
            "noon": ["health_assurance_loop", "proactive_notification_engine"],
            "afternoon": ["workflow_engine", "cross_engine_task_planner", "execution_enhancement_engine"],
            "evening": ["long_term_memory_engine", "task_continuation_engine"],
            "night": ["system_dashboard_engine", "security_monitor_engine"]
        }

        recommended_types = []

        # 添加时间相关推荐
        if context["time_period"] in time_recommendations:
            for engine in time_recommendations[context["time_period"]]:
                if engine in self.data["engines"]:
                    recommendations.append({
                        "engine": engine,
                        "reason": f"根据当前时段（{context['time_period']}）推荐",
                        "type": "time_based"
                    })
                    recommended_types.append(self.data["engines"][engine].get("type", "general"))

        # 添加未被充分利用但功能完整的引擎
        for name, info in self.data["engines"].items():
            usage_status = info.get("usage_status", "unknown")
            if usage_status == "unused" and info.get("type") not in recommended_types:
                # 避免推荐太多
                if len([r for r in recommendations if r["type"] == "unused"]) < 5:
                    recommendations.append({
                        "engine": name,
                        "reason": f"功能完整但未被使用的引擎: {info.get('description', '')[:50]}",
                        "type": "unused_gem"
                    })

        # 添加跨类型推荐（增加多样性）
        all_types = list(engines_by_type.keys())
        for engine_type in all_types:
            if engine_type not in recommended_types and engines_by_type[engine_type]:
                # 随机选一个
                name, info = engines_by_type[engine_type][0]
                recommendations.append({
                    "engine": name,
                    "reason": f"发现 {engine_type} 类引擎: {info.get('description', '')[:50]}",
                    "type": "discovery"
                })
                if len(recommendations) >= 8:
                    break

        # 保存推荐结果
        self.data["recommendations"] = recommendations
        self.save_data()

        return recommendations

    def show_dashboard(self):
        """显示引擎能力激活仪表盘"""
        if not self.data.get("engines"):
            self.scan_all_engines()

        context = self.analyze_context()

        # 统计各类型引擎数量
        type_counts = defaultdict(int)
        for name, info in self.data["engines"].items():
            type_counts[info.get("type", "general")] += 1

        # 统计未使用的引擎
        unused_count = sum(1 for info in self.data["engines"].values() if info.get("usage_status") == "unused")

        output = []
        output.append("=" * 60)
        output.append("Smart Engine Capability Activator")
        output.append("=" * 60)
        output.append(f"\n[*] Engine Stats:")
        output.append(f"    Total engines: {len(self.data['engines'])}")
        output.append(f"    Unused engines: {unused_count}")

        output.append(f"\n[#] Engine Type Distribution:")
        for engine_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            output.append(f"    {engine_type}: {count}")

        output.append(f"\n[@] Current Context:")
        output.append(f"    Time period: {context['time_period']} ({context['hour']}:00)")
        output.append(f"    Day: {'Weekend' if context['is_weekend'] else 'Weekday'}")

        # 生成推荐
        recommendations = self.generate_recommendations(context)

        output.append(f"\n[+] Recommended Engines ({len(recommendations)}):")
        for i, rec in enumerate(recommendations[:8], 1):
            engine_name = rec["engine"]
            desc = self.data["engines"].get(engine_name, {}).get("description", "")[:40]
            output.append(f"    {i}. {engine_name}")
            output.append(f"       Reason: {rec['reason']}")
            if desc and desc != "功能描述未知":
                output.append(f"       Description: {desc}")

        output.append("\n" + "=" * 60)
        output.append("Usage:")
        output.append("  engine_capability_activator.py scan - Scan all engines")
        output.append("  engine_capability_activator.py recommend - Generate recommendations")
        output.append("  engine_capability_activator.py dashboard - Show dashboard")
        output.append("  engine_capability_activator.py test <engine> - Test specific engine")
        output.append("=" * 60)

        return "\n".join(output)

    def test_engine(self, engine_name):
        """测试指定引擎是否可用"""
        engines = self.data.get("engines", {})

        if engine_name not in engines:
            return f"引擎 {engine_name} 未被扫描到，请先运行 scan"

        engine_info = engines[engine_name]
        engine_path = engine_info.get("path", "")

        if not engine_path or not Path(engine_path).exists():
            return f"引擎脚本不存在: {engine_path}"

        # 尝试导入并测试
        try:
            sys.path.insert(0, str(self.scripts_dir))
            module_name = Path(engine_path).stem

            # 尝试获取帮助信息
            import importlib.util
            spec = importlib.util.spec_from_file_location(module_name, engine_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)

                # 尝试获取帮助
                help_info = f"引擎模块: {module_name}\n"
                help_info += f"描述: {engine_info.get('description', '未知')}\n"
                help_info += f"类型: {engine_info.get('type', 'general')}\n"
                help_info += f"路径: {engine_path}\n"

                # 检查是否有命令行接口
                try:
                    spec.loader.exec_module(module)
                    if hasattr(module, '__doc__') and module.__doc__:
                        help_info += f"\n文档:\n{module.__doc__}"
                except Exception as e:
                    help_info += f"\n注意: 加载时出现警告 - {str(e)[:100]}"

                return help_info

        except Exception as e:
            return f"测试引擎失败: {str(e)}"

        return "引擎测试完成"

def safe_print(msg):
    """安全打印，处理编码问题"""
    try:
        print(msg)
    except UnicodeEncodeError:
        # 移除 emoji 后重试
        print(msg.encode('ascii', 'replace').decode('ascii'))

def main():
    """主入口"""
    activator = EngineCapabilityActivator()

    if len(sys.argv) < 2:
        print(activator.show_dashboard())
        return

    command = sys.argv[1].lower()

    if command == "scan":
        engines = activator.scan_all_engines()
        safe_print(f"[OK] Scan complete, found {len(engines)} engines")

    elif command == "recommend":
        context = activator.analyze_context()
        recommendations = activator.generate_recommendations(context)
        safe_print(f"[*] Generated {len(recommendations)} recommendations:")
        for i, rec in enumerate(recommendations, 1):
            safe_print(f"  {i}. {rec['engine']} - {rec['reason']}")

    elif command == "dashboard":
        safe_print(activator.show_dashboard())

    elif command == "test" and len(sys.argv) > 2:
        engine_name = sys.argv[2]
        safe_print(activator.test_engine(engine_name))

    elif command == "status":
        activator.load_data()
        safe_print(f"[*] Current Status:")
        safe_print(f"    Scanned engines: {len(activator.data.get('engines', {}))}")
        safe_print(f"    Recommendations: {len(activator.data.get('recommendations', []))}")

    else:
        safe_print("Unknown command")
        safe_print("Available commands: scan, recommend, dashboard, test <engine_name>, status")

if __name__ == "__main__":
    main()