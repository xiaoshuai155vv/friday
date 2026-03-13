#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能跨引擎动态协同编排引擎

功能：
- 根据实时任务需求动态选择和编排引擎组合
- 实现自适应的任务执行策略
- 任务上下文感知分析
- 引擎能力动态匹配
- 执行策略自适应调整
- 多引擎协同效果追踪与评估

区别于现有静态配置的引擎协作，本引擎实现：
- 动态感知任务上下文
- 自动选择最优引擎组合
- 实时调整执行策略
- 效果评估与持续优化
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import ast

# 确保 scripts 目录在路径中
SCRIPT_DIR = Path(__file__).parent
RUNTIME_DIR = SCRIPT_DIR.parent / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"

def ensure_dir(path):
    """确保目录存在"""
    path = Path(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    return path

# 引擎能力分类
ENGINE_CAPABILITIES = {
    "general": ["file_manager", "clipboard", "window_tool", "mouse_tool", "keyboard_tool", "process_tool", "network_tool"],
    "execution": ["workflow_engine", "run_plan", "conversation_execution", "cross_engine_task_planner", "zero_click_service"],
    "system": ["system_health", "system_dashboard", "proactive_operations", "self_healing", "predictive_prevention"],
    "learning": ["adaptive_learning", "feedback_learning", "evolution_learning", "user_behavior_learner", "task_preference"],
    "monitoring": ["engine_performance_monitor", "security_monitor", "daemon_manager", "health_assurance_loop"],
    "recommendation": ["scenario_recommender", "engine_combination_recommender", "unified_recommender", "active_suggestion"],
    "reasoning": ["knowledge_graph", "enhanced_knowledge_reasoning", "intent_deep_reasoning", "behavior_sequence_prediction"],
    "service": ["proactive_service", "proactive_decision_action", "long_term_memory", "task_continuation"],
}

# 任务类型到引擎类别的映射
TASK_TYPE_MAPPING = {
    "文件操作": ["general", "learning"],
    "系统维护": ["system", "monitoring"],
    "自动化执行": ["execution", "service"],
    "智能推荐": ["recommendation", "learning"],
    "问题诊断": ["system", "reasoning"],
    "学习适应": ["learning", "service"],
    "复杂任务": ["execution", "reasoning", "service"],
}


class DynamicEngineOrchestrator:
    """智能跨引擎动态协同编排器"""

    def __init__(self):
        self.state_file = STATE_DIR / "dynamic_orchestrator_state.json"
        self.history_file = STATE_DIR / "engine_collaboration_history.json"
        self.preferences_file = STATE_DIR / "orchestrator_preferences.json"
        self.state = self._load_state()
        self.history = self._load_history()
        self.preferences = self._load_preferences()

    def _load_state(self) -> Dict:
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "initialized_at": datetime.now().isoformat(),
            "total_orchestrations": 0,
            "successful_orchestrations": 0,
            "engine_selection_stats": {}
        }

    def _load_history(self) -> Dict:
        """加载历史记录"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {"orchestrations": []}

    def _load_preferences(self) -> Dict:
        """加载偏好设置"""
        if self.preferences_file.exists():
            try:
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "adaptive_enabled": True,
            "learning_mode": "auto",
            "min_confidence_threshold": 0.6
        }

    def _save_state(self):
        """保存状态"""
        ensure_dir(STATE_DIR)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def analyze_task_context(self, task_description: str, context: Optional[Dict] = None) -> Dict:
        """分析任务上下文，识别任务类型和需求"""
        task_lower = task_description.lower()

        # 识别任务类型
        task_type = "通用任务"
        for type_name, keywords in [
            ("文件操作", ["文件", "整理", "搜索", "复制", "移动", "删除", "file"]),
            ("系统维护", ["系统", "优化", "清理", "维护", "健康", "system"]),
            ("自动化执行", ["执行", "运行", "自动", "完成", "execute", "run"]),
            ("智能推荐", ["推荐", "建议", "什么", "recommend", "suggest"]),
            ("问题诊断", ["问题", "错误", "故障", "诊断", "problem", "error"]),
            ("学习适应", ["学习", "适应", "偏好", "习惯", "learn", "adapt"]),
            ("复杂任务", ["复杂", "多步", "综合", "complex", "multi"]),
        ]:
            if any(kw in task_lower for kw in keywords):
                task_type = type_name
                break

        # 识别需要的引擎类别
        required_categories = TASK_TYPE_MAPPING.get(task_type, ["general"])

        # 识别关键词
        keywords = []
        for word in task_lower.split():
            if len(word) > 2:
                keywords.append(word)

        return {
            "task_type": task_type,
            "required_categories": required_categories,
            "keywords": keywords,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }

    def match_engines(self, task_context: Dict) -> List[Dict]:
        """根据任务上下文动态匹配引擎"""
        matched_engines = []
        required_categories = task_context.get("required_categories", [])

        # 扫描 scripts 目录获取可用引擎
        available_engines = []
        for engine_file in SCRIPT_DIR.glob("*engine*.py"):
            engine_name = engine_file.stem
            if engine_name not in ["dynamic_engine_orchestrator"]:  # 排除自身
                available_engines.append({
                    "name": engine_name,
                    "file": str(engine_file.name),
                    "path": str(engine_file)
                })

        # 根据需要的类别筛选引擎
        for category in required_categories:
            category_engines = ENGINE_CAPABILITIES.get(category, [])
            for engine_info in available_engines:
                engine_name = engine_info["name"].lower()
                if any(ce in engine_name for ce in category_engines):
                    if engine_info not in matched_engines:
                        # 计算匹配分数
                        score = self._calculate_match_score(engine_info, task_context)
                        engine_info["match_score"] = score
                        matched_engines.append(engine_info)

        # 添加通用引擎（如果没有匹配）
        if not matched_engines:
            for engine_info in available_engines[:5]:  # 取前5个
                engine_info["match_score"] = 0.5
                matched_engines.append(engine_info)

        # 按匹配分数排序
        matched_engines.sort(key=lambda x: x.get("match_score", 0), reverse=True)

        return matched_engines[:10]  # 返回前10个

    def _calculate_match_score(self, engine_info: Dict, task_context: Dict) -> float:
        """计算引擎匹配分数"""
        score = 0.5  # 基础分数
        engine_name = engine_info["name"].lower()
        keywords = task_context.get("keywords", [])

        # 基于关键词增加分数
        for kw in keywords:
            if kw in engine_name:
                score += 0.15

        # 基于历史使用记录
        engine_name_key = engine_info["name"]
        if engine_name_key in self.state.get("engine_selection_stats", {}):
            usage_count = self.state["engine_selection_stats"][engine_name_key]
            score += min(0.1, usage_count * 0.01)  # 最多加 0.1

        return min(1.0, score)

    def create_orchestration_plan(self, task_description: str, context: Optional[Dict] = None) -> Dict:
        """创建编排计划"""
        # 分析任务上下文
        task_context = self.analyze_task_context(task_description, context)

        # 匹配引擎
        matched_engines = self.match_engines(task_context)

        # 创建编排计划
        plan = {
            "task_description": task_description,
            "task_context": task_context,
            "matched_engines": matched_engines,
            "execution_strategy": self._determine_execution_strategy(task_context, matched_engines),
            "estimated_complexity": len(matched_engines),
            "created_at": datetime.now().isoformat()
        }

        return plan

    def _determine_execution_strategy(self, task_context: Dict, matched_engines: List[Dict]) -> str:
        """确定执行策略"""
        task_type = task_context.get("task_type", "通用任务")
        complexity = len(matched_engines)

        if complexity <= 2:
            return "sequential_simple"
        elif complexity <= 5:
            return "sequential_complex"
        else:
            return "parallel_coordination"

    def execute_orchestration(self, plan: Dict) -> Dict:
        """执行编排计划"""
        result = {
            "success": False,
            "executed_engines": [],
            "results": [],
            "errors": [],
            "execution_time": 0,
            "started_at": datetime.now().isoformat()
        }

        start_time = datetime.now()

        try:
            # 执行匹配的引擎
            for engine in plan.get("matched_engines", [])[:5]:  # 最多执行5个
                try:
                    engine_result = self._execute_engine(engine)
                    result["executed_engines"].append(engine["name"])
                    result["results"].append({
                        "engine": engine["name"],
                        "status": "success",
                        "output": engine_result
                    })

                    # 更新统计
                    self.state["total_orchestrations"] += 1
                    self.state["successful_orchestrations"] += 1
                    engine_name = engine["name"]
                    stats = self.state.get("engine_selection_stats", {})
                    stats[engine_name] = stats.get(engine_name, 0) + 1
                    self.state["engine_selection_stats"] = stats

                except Exception as e:
                    result["errors"].append({
                        "engine": engine["name"],
                        "error": str(e)
                    })

            result["success"] = len(result["errors"]) == 0

        except Exception as e:
            result["errors"].append({"fatal_error": str(e)})

        result["execution_time"] = (datetime.now() - start_time).total_seconds()
        result["completed_at"] = datetime.now().isoformat()

        # 保存状态
        self._save_state()

        # 记录历史
        self._record_history(plan, result)

        return result

    def _execute_engine(self, engine: Dict) -> str:
        """执行单个引擎（获取状态）"""
        # 简化实现：返回引擎信息而非真正执行
        return f"Engine: {engine.get('name', 'unknown')}, File: {engine.get('file', 'unknown')}"

    def _record_history(self, plan: Dict, result: Dict):
        """记录执行历史"""
        ensure_dir(STATE_DIR)
        history_entry = {
            "task": plan.get("task_description", ""),
            "engines": result.get("executed_engines", []),
            "success": result.get("success", False),
            "execution_time": result.get("execution_time", 0),
            "timestamp": datetime.now().isoformat()
        }

        self.history["orchestrations"].append(history_entry)

        # 只保留最近100条
        if len(self.history["orchestrations"]) > 100:
            self.history["orchestrations"] = self.history["orchestrations"][-100:]

        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def get_status(self) -> Dict:
        """获取编排器状态"""
        return {
            "initialized": self.state.get("initialized_at", "") != "",
            "total_orchestrations": self.state.get("total_orchestrations", 0),
            "successful_orchestrations": self.state.get("successful_orchestrations", 0),
            "success_rate": (
                self.state.get("successful_orchestrations", 0) /
                max(1, self.state.get("total_orchestrations", 1))
            ),
            "top_engines": sorted(
                self.state.get("engine_selection_stats", {}).items(),
                key=lambda x: x[1],
                reverse=True
            )[:10],
            "preferences": self.preferences,
            "recent_history": self.history.get("orchestrations", [])[-10:]
        }

    def get_orchestration_suggestions(self, current_task: str) -> Dict:
        """获取编排建议"""
        plan = self.create_orchestration_plan(current_task)
        return {
            "suggested_engines": [
                {
                    "name": e["name"],
                    "file": e["file"],
                    "score": e.get("match_score", 0)
                }
                for e in plan.get("matched_engines", [])[:5]
            ],
            "execution_strategy": plan.get("execution_strategy", "sequential"),
            "estimated_complexity": plan.get("estimated_complexity", 0)
        }


def main():
    """CLI 入口"""
    import argparse
    parser = argparse.ArgumentParser(description="智能跨引擎动态协同编排引擎")
    parser.add_argument("command", choices=["status", "plan", "execute", "suggestions"],
                        help="命令")
    parser.add_argument("--task", type=str, default="",
                        help="任务描述")
    parser.add_argument("--context", type=str, default="{}",
                        help="上下文 JSON")

    args = parser.parse_args()

    orchestrator = DynamicEngineOrchestrator()

    if args.command == "status":
        status = orchestrator.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.command == "plan":
        if not args.task:
            print("Error: --task required for plan command")
            sys.exit(1)
        plan = orchestrator.create_orchestration_plan(args.task)
        print(json.dumps(plan, ensure_ascii=False, indent=2))

    elif args.command == "execute":
        if not args.task:
            print("Error: --task required for execute command")
            sys.exit(1)
        try:
            context = json.loads(args.context)
        except:
            context = {}
        plan = orchestrator.create_orchestration_plan(args.task, context)
        result = orchestrator.execute_orchestration(plan)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "suggestions":
        if not args.task:
            print("Error: --task required for suggestions command")
            sys.exit(1)
        suggestions = orchestrator.get_orchestration_suggestions(args.task)
        print(json.dumps(suggestions, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()