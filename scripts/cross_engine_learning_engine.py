#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能跨引擎知识融合与持续学习引擎

让系统能够从70+引擎的实际交互中持续学习，自动发现跨引擎协作新模式、
生成创新组合建议，形成持续学习→发现→创新的完整闭环。

功能：
1. 跨引擎交互数据收集与分析
2. 协作模式自动发现与学习
3. 创新组合自动生成与评估
4. 持续学习闭环
"""

import os
import json
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from pathlib import Path
import glob

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
LOGS_DIR = RUNTIME_DIR / "logs"
STATE_DIR = RUNTIME_DIR / "state"


class CrossEngineLearningEngine:
    """跨引擎知识融合与持续学习引擎"""

    def __init__(self):
        self.engine_names = self._load_engine_names()
        self.learning_data_path = STATE_DIR / "cross_engine_learning_data.json"
        self.learning_data = self._load_learning_data()
        self.patterns_path = STATE_DIR / "cross_engine_patterns.json"
        self.patterns = self._load_patterns()

    def _load_engine_names(self):
        """加载所有引擎名称"""
        engine_names = set()
        scripts_dir = PROJECT_ROOT / "scripts"

        # 从 scripts 目录扫描所有 _engine.py 文件
        for f in scripts_dir.glob("*_engine.py"):
            engine_names.add(f.stem.replace("_engine", ""))

        # 添加其他常见脚本
        for f in scripts_dir.glob("*.py"):
            name = f.stem
            if "tool" in name or "launch" in name or name in ["do", "run_plan", "selfie", "screenshot_tool"]:
                engine_names.add(name)

        return sorted(engine_names)

    def _load_learning_data(self):
        """加载学习数据"""
        if self.learning_data_path.exists():
            try:
                with open(self.learning_data_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "interactions": [],
            "discovered_patterns": [],
            "innovation_suggestions": [],
            "learning_history": [],
            "last_updated": None
        }

    def _save_learning_data(self):
        """保存学习数据"""
        self.learning_data["last_updated"] = datetime.now().isoformat()
        with open(self.learning_data_path, 'w', encoding='utf-8') as f:
            json.dump(self.learning_data, f, ensure_ascii=False, indent=2)

    def _load_patterns(self):
        """加载已发现的模式"""
        if self.patterns_path.exists():
            try:
                with open(self.patterns_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "collaboration_patterns": [],
            "success_patterns": [],
            "failure_patterns": [],
            "innovation_patterns": []
        }

    def _save_patterns(self):
        """保存模式"""
        with open(self.patterns_path, 'w', encoding='utf-8') as f:
            json.dump(self.patterns, f, ensure_ascii=False, indent=2)

    def collect_interactions(self, days=7):
        """收集跨引擎交互数据"""
        interactions = []
        cutoff_date = datetime.now() - timedelta(days=days)

        # 从行为日志收集
        for log_file in LOGS_DIR.glob("behavior_*.log"):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 解析日志行
                    for line in content.split('\n'):
                        if not line.strip():
                            continue
                        # 提取时间戳
                        timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2})', line)
                        if timestamp_match:
                            timestamp = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d')
                            if timestamp < cutoff_date:
                                continue

                        # 提取引擎调用模式
                        for engine in self.engine_names:
                            if engine in line.lower():
                                interactions.append({
                                    "timestamp": timestamp_match.group(1) if timestamp_match else datetime.now().strftime('%Y-%m-%d'),
                                    "engine": engine,
                                    "context": line[:200]
                                })
            except Exception as e:
                print(f"Warning: Failed to read {log_file}: {e}")

        # 从进化历史收集
        for ev_file in STATE_DIR.glob("evolution_completed_*.json"):
            try:
                with open(ev_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "impacted_files" in data:
                        for f in data["impacted_files"]:
                            if "scripts/" in f:
                                engine = f.replace("scripts/", "").replace(".py", "")
                                interactions.append({
                                    "timestamp": data.get("completed_at", "")[:10],
                                    "engine": engine,
                                    "context": f"evolution_round_{data.get('loop_round', 'unknown')}"
                                })
            except Exception as e:
                print(f"Warning: Failed to read {ev_file}: {e}")

        self.learning_data["interactions"] = interactions
        self._save_learning_data()
        return f"收集了 {len(interactions)} 条跨引擎交互数据"

    def discover_patterns(self):
        """发现协作模式"""
        interactions = self.learning_data.get("interactions", [])

        if not interactions:
            return "没有足够的交互数据进行分析"

        # 按引擎分组统计
        engine_counts = Counter(i["engine"] for i in interactions)

        # 发现频繁共现模式（简化版：基于时间窗口）
        patterns = []
        for i in range(len(interactions) - 1):
            if interactions[i]["timestamp"] == interactions[i+1]["timestamp"]:
                pattern = f"{interactions[i]['engine']} -> {interactions[i+1]['engine']}"
                patterns.append(pattern)

        # 统计模式频率
        pattern_counts = Counter(patterns)
        top_patterns = pattern_counts.most_common(10)

        # 更新模式
        self.patterns["collaboration_patterns"] = [
            {"pattern": p, "count": c} for p, c in top_patterns
        ]

        # 分析成功模式（从进化历史）
        success_engines = []
        for ev_file in STATE_DIR.glob("evolution_completed_*.json"):
            try:
                with open(ev_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get("result", {}).get("status") == "completed":
                        for f in data.get("impacted_files", []):
                            if "scripts/" in f:
                                engine = f.replace("scripts/", "").replace(".py", "")
                                success_engines.append(engine)
            except:
                pass

        success_counts = Counter(success_engines)
        self.patterns["success_patterns"] = [
            {"engine": e, "success_count": c} for e, c in success_counts.most_common(20)
        ]

        self._save_patterns()

        return f"发现 {len(top_patterns)} 个协作模式和 {len(success_counts)} 个成功引擎"

    def generate_innovations(self):
        """生成创新组合建议"""
        if not self.patterns.get("collaboration_patterns") or not self.patterns.get("success_patterns"):
            return "没有足够的模式数据生成创新建议"

        suggestions = []

        # 基于成功引擎生成组合建议
        success_engines = [p["engine"] for p in self.patterns["success_patterns"][:10]]
        top_interaction_engines = [p["pattern"].split(" -> ")[0] for p in self.patterns["collaboration_patterns"][:5]]

        # 建议1：成功引擎 + 频繁交互引擎
        for success_engine in success_engines[:5]:
            for interaction_engine in top_interaction_engines:
                if success_engine != interaction_engine:
                    suggestions.append({
                        "type": "combination",
                        "description": f"将 {success_engine} 与 {interaction_engine} 结合",
                        "engines": [success_engine, interaction_engine],
                        "rationale": "基于成功引擎和频繁交互模式的组合",
                        "confidence": 0.7
                    })

        # 基于进化历史生成创新
        # 读取最近的进化目标寻找灵感
        recent_goals = []
        for ev_file in sorted(STATE_DIR.glob("evolution_completed_*.json"))[-5:]:
            try:
                with open(ev_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    recent_goals.append(data.get("current_goal", ""))
            except:
                pass

        # 生成元学习建议
        suggestions.append({
            "type": "meta_learning",
            "description": "跨引擎元学习机制",
            "engines": ["evolution_learning_engine", "cross_engine_learning_engine"],
            "rationale": "让进化引擎能够从跨引擎学习数据中持续优化",
            "confidence": 0.8
        })

        # 生成主动服务建议
        suggestions.append({
            "type": "active_service",
            "description": "基于模式发现的主动服务触发",
            "engines": ["proactive_decision_action_engine", "pattern_matcher"],
            "rationale": "根据发现的协作模式主动预测和触发服务",
            "confidence": 0.75
        })

        self.learning_data["innovation_suggestions"] = suggestions[:10]
        self._save_learning_data()

        return f"生成了 {len(suggestions)} 个创新组合建议"

    def analyze_learning_insights(self):
        """分析学习洞察"""
        insights = []

        # 分析引擎使用频率
        interactions = self.learning_data.get("interactions", [])
        engine_counts = Counter(i["engine"] for i in interactions)

        if engine_counts:
            most_used = engine_counts.most_common(5)
            insights.append({
                "type": "usage_frequency",
                "finding": f"最常用的5个引擎: {', '.join([e[0] for e in most_used])}",
                "recommendation": "可优化这些高频引擎的性能和可靠性"
            })

        # 分析协作效率
        if self.patterns.get("collaboration_patterns"):
            top_pattern = self.patterns["collaboration_patterns"][0]
            insights.append({
                "type": "collaboration_efficiency",
                "finding": f"最频繁的协作模式: {top_pattern['pattern']} (出现 {top_pattern['count']} 次)",
                "recommendation": "可将此类模式固化为标准工作流"
            })

        # 分析创新机会
        if self.learning_data.get("innovation_suggestions"):
            insights.append({
                "type": "innovation_opportunity",
                "finding": f"有 {len(self.learning_data['innovation_suggestions'])} 个待验证的创新组合",
                "recommendation": "建议在下一轮进化中优先验证高置信度建议"
            })

        return insights

    def continuous_learning(self):
        """持续学习闭环"""
        # 1. 收集新数据
        collect_result = self.collect_interactions(days=7)

        # 2. 发现新模式
        pattern_result = self.discover_patterns()

        # 3. 生成创新
        innovation_result = self.generate_innovations()

        # 4. 记录学习历史
        self.learning_data["learning_history"].append({
            "timestamp": datetime.now().isoformat(),
            "actions": [collect_result, pattern_result, innovation_result]
        })
        self._save_learning_data()

        return {
            "status": "success",
            "actions": [collect_result, pattern_result, innovation_result],
            "insights": self.analyze_learning_insights()
        }

    def get_status(self):
        """获取学习引擎状态"""
        return {
            "total_interactions": len(self.learning_data.get("interactions", [])),
            "discovered_patterns": len(self.patterns.get("collaboration_patterns", [])),
            "innovation_suggestions": len(self.learning_data.get("innovation_suggestions", [])),
            "learning_rounds": len(self.learning_data.get("learning_history", [])),
            "last_updated": self.learning_data.get("last_updated")
        }

    def get_suggestions(self, limit=5):
        """获取创新建议"""
        suggestions = self.learning_data.get("innovation_suggestions", [])
        return suggestions[:limit]

    def get_patterns(self):
        """获取发现的模式"""
        return self.patterns


def main():
    """主函数 - 支持命令行调用"""
    import sys

    engine = CrossEngineLearningEngine()

    if len(sys.argv) < 2:
        # 默认显示状态
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return

    command = sys.argv[1].lower()

    if command == "status":
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif command == "collect":
        result = engine.collect_interactions()
        print(result)

    elif command == "discover":
        result = engine.discover_patterns()
        print(result)

    elif command == "innovate":
        result = engine.generate_innovations()
        print(result)

    elif command == "learn":
        result = engine.continuous_learning()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "insights":
        insights = engine.analyze_learning_insights()
        print(json.dumps(insights, ensure_ascii=False, indent=2))

    elif command == "suggestions":
        suggestions = engine.get_suggestions()
        print(json.dumps(suggestions, ensure_ascii=False, indent=2))

    elif command == "patterns":
        patterns = engine.get_patterns()
        print(json.dumps(patterns, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {command}")
        print("可用命令: status, collect, discover, innovate, learn, insights, suggestions, patterns")


if __name__ == "__main__":
    main()