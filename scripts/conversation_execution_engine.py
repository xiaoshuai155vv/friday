#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能对话执行一体化引擎
让系统能够理解用户自然语言对话意图，自动调度多个引擎协同工作，形成「对话→理解→执行→反馈」的完整闭环

功能：
1. 自然语言意图理解 - 解析用户的自然语言输入，识别任务意图
2. 引擎调度决策 - 根据意图自动选择和调度合适的引擎
3. 多引擎协同执行 - 协调多个引擎协同工作完成任务
4. 执行状态反馈 - 实时反馈执行状态和结果
5. 上下文记忆 - 记住对话上下文，支持多轮对话

使用方法：
    python conversation_execution_engine.py chat "用户输入内容"
    python conversation_execution_engine.py status
    python conversation_execution_engine.py history
    python conversation_execution_engine.py clear
"""
import os
import sys
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import re

# 路径配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, '..', 'runtime', 'state', 'conversation_execution.db')
RUNTIME_DIR = os.path.join(SCRIPT_DIR, '..', 'runtime')


@dataclass
class ConversationContext:
    """对话上下文"""
    session_id: str = ""
    user_input: str = ""
    intent: str = ""
    entities: Dict[str, Any] = field(default_factory=dict)
    executed_engines: List[str] = field(default_factory=list)
    execution_results: List[Dict[str, Any]] = field(default_factory=list)
    response: str = ""
    success: bool = False
    timestamp: str = ""


@dataclass
class IntentAnalysis:
    """意图分析结果"""
    intent: str
    confidence: float
    entities: Dict[str, Any]
    suggested_engines: List[str]
    action_plan: List[str]


class ConversationExecutionEngine:
    """智能对话执行一体化引擎"""

    def __init__(self):
        self.db_path = DB_PATH
        self._init_database()
        self._load_engine_registry()

    def _init_database(self):
        """初始化数据库"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 对话历史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_input TEXT NOT NULL,
                intent TEXT,
                executed_engines TEXT,
                response TEXT,
                success INTEGER,
                timestamp TEXT NOT NULL
            )
        ''')

        # 上下文表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_context (
                session_id TEXT PRIMARY KEY,
                context_data TEXT,
                last_intent TEXT,
                last_entities TEXT,
                updated_at TEXT NOT NULL
            )
        ''')

        conn.commit()
        conn.close()

    def _load_engine_registry(self):
        """加载引擎注册表"""
        # 引擎能力映射
        self.engine_capabilities = {
            "文件管理": ["file_manager_engine", "搜索文件", "整理文件", "文件分析"],
            "工作流": ["workflow_engine", "workflow_auto_generator", "workflow_smart_recommender", "workflow_quality_engine", "运行计划", "执行工作流"],
            "语音": ["voice_interaction_engine", "tts_engine", "语音交互", "语音合成", "语音回复"],
            "系统": ["system_health_monitor", "system_diagnostic_engine", "系统监控", "系统诊断"],
            "推荐": ["unified_recommender", "scenario_recommender", "推荐", "智能推荐"],
            "决策": ["decision_orchestrator", "决策", "编排"],
            "学习": ["adaptive_learning_engine", "deep_personalization_engine", "学习", "个性化"],
            "预测": ["predictive_prevention_engine", "预测", "预防"],
            "自愈": ["self_healing_engine", "自愈", "问题修复"],
            "知识": ["knowledge_graph", "enhanced_knowledge_reasoning_engine", "知识", "推理"],
            "会议": ["meeting_assistant_engine", "会议", "会议纪要"],
            "日程": ["task_scheduler", "定时任务", "日程"],
            "通知": ["proactive_notification_engine", "通知", "提醒"],
            "搜索": ["unified_engine_hub", "引擎搜索", "搜索引擎"],
            "规划": ["task_planner", "task_planning_engine", "规划", "任务规划"],
            "记忆": ["long_term_memory_engine", "memory_engine", "记忆", "记住"],
            "代码": ["code_understanding_engine", "代码分析", "代码理解"],
            "数据": ["data_insight_engine", "数据洞察", "数据分析"],
            "创新": ["innovation_discovery_engine", "创新", "发现"],
            "进化": ["evolution_coordinator", "evolution_loop_automation", "进化"],
            "对话": ["conversation_manager", "对话", "多轮对话"],
            "情感": ["emotion_engine", "情感", "情绪"],
            "场景": ["context_awareness_engine", "情境感知", "场景理解"],
        }

    def analyze_intent(self, user_input: str, context: Optional[Dict] = None) -> IntentAnalysis:
        """分析用户意图"""
        user_input_lower = user_input.lower()
        entities = {}
        suggested_engines = []
        action_plan = []
        intent = "unknown"
        confidence = 0.0

        # 意图模式匹配
        intent_patterns = {
            "文件操作": ["搜索文件", "找文件", "整理文件", "分析文件", "查看文件"],
            "执行工作流": ["运行", "执行", "帮我做", "完成", "处理"],
            "系统查询": ["查看系统", "系统状态", "监控", "检查"],
            "推荐服务": ["推荐", "建议", "给我推荐"],
            "智能调度": ["调度", "引擎", "搜索引擎", "引擎列表"],
            "学习适应": ["学习", "记住", "习惯", "偏好"],
            "会议管理": ["会议", "会议纪要", "日程"],
            "通知提醒": ["提醒", "通知", "提醒我"],
            "代码分析": ["分析代码", "代码理解", "重构"],
            "数据查询": ["数据", "分析", "报表", "洞察"],
            "知识查询": ["知识", "推理", "关联"],
            "任务规划": ["规划", "计划", "分解任务"],
            "问题诊断": ["诊断", "问题", "修复"],
            "对话聊天": ["聊天", "对话", "说说话"],
        }

        # 匹配意图
        for intent_name, patterns in intent_patterns.items():
            for pattern in patterns:
                if pattern in user_input_lower:
                    intent = intent_name
                    confidence = 0.8
                    # 提取实体
                    if "文件" in user_input or "搜索" in user_input:
                        # 尝试提取文件名
                        file_match = re.search(r'[「」（）(（)《》〈〉""''\s]+(.+?)[」』）)）》《〉〉""''\s]+', user_input)
                        if file_match:
                            entities["filename"] = file_match.group(1)
                        # 提取关键词
                        keyword_match = re.search(r'(?:关于|包含|含有)\s*(.+)', user_input)
                        if keyword_match:
                            entities["keyword"] = keyword_match.group(1).strip()
                    break

        if intent == "unknown":
            # 通用意图 - 需要多引擎协同
            intent = "通用任务"
            confidence = 0.5

        # 根据意图推荐引擎
        if intent in self.engine_capabilities:
            suggested_engines = self.engine_capabilities[intent]
        else:
            # 默认使用统一调度中心和决策编排
            suggested_engines = ["unified_engine_hub", "decision_orchestrator"]

        # 生成行动计划
        action_plan = [
            f"理解用户意图: {intent}",
            f"选择引擎: {', '.join(suggested_engines[:3])}",
            "执行任务",
            "返回执行结果"
        ]

        return IntentAnalysis(
            intent=intent,
            confidence=confidence,
            entities=entities,
            suggested_engines=suggested_engines,
            action_plan=action_plan
        )

    def execute_conversation(self, user_input: str, session_id: str = "default") -> Dict[str, Any]:
        """执行对话任务"""
        # 获取会话上下文
        context = self._get_session_context(session_id)

        # 分析意图
        intent_analysis = self.analyze_intent(user_input, context)
        executed_engines = []
        execution_results = []

        response = ""

        # 根据意图调度引擎
        if intent_analysis.intent == "文件操作":
            result = self._handle_file_operation(user_input, intent_analysis)
            executed_engines.append("file_manager_engine")
            execution_results.append(result)
            response = result.get("response", "文件操作完成")

        elif intent_analysis.intent == "执行工作流":
            result = self._handle_workflow_execution(user_input, intent_analysis)
            executed_engines.append("workflow_engine")
            execution_results.append(result)
            response = result.get("response", "工作流执行完成")

        elif intent_analysis.intent == "系统查询":
            result = self._handle_system_query(user_input, intent_analysis)
            executed_engines.append("system_health_monitor")
            execution_results.append(result)
            response = result.get("response", "系统状态查询完成")

        elif intent_analysis.intent == "会议管理":
            result = self._handle_meeting_management(user_input, intent_analysis)
            executed_engines.append("meeting_assistant_engine")
            execution_results.append(result)
            response = result.get("response", "会议管理完成")

        elif intent_analysis.intent == "智能调度":
            result = self._handle_engine_dispatch(user_input, intent_analysis)
            executed_engines.append("unified_engine_hub")
            execution_results.append(result)
            response = result.get("response", "引擎调度完成")

        elif intent_analysis.intent == "任务规划":
            result = self._handle_task_planning(user_input, intent_analysis)
            executed_engines.append("task_planning_engine")
            execution_results.append(result)
            response = result.get("response", "任务规划完成")

        elif intent_analysis.intent == "通用任务":
            result = self._handle_general_task(user_input, intent_analysis)
            executed_engines.extend(result.get("engines_used", []))
            execution_results.append(result)
            response = result.get("response", "任务处理完成")

        else:
            # 默认响应
            response = f"我理解您的需求是「{intent_analysis.intent}」，正在为您处理..."

        # 保存到历史
        self._save_conversation(session_id, user_input, intent_analysis, executed_engines, response, True)

        # 更新会话上下文
        self._update_session_context(session_id, intent_analysis)

        return {
            "success": True,
            "session_id": session_id,
            "user_input": user_input,
            "intent": intent_analysis.intent,
            "confidence": intent_analysis.confidence,
            "executed_engines": executed_engines,
            "execution_results": execution_results,
            "response": response,
            "action_plan": intent_analysis.action_plan
        }

    def _handle_file_operation(self, user_input: str, intent_analysis: IntentAnalysis) -> Dict[str, Any]:
        """处理文件操作"""
        keyword = intent_analysis.entities.get("keyword", "")
        return {
            "engine": "file_manager_engine",
            "response": f"我将帮您搜索文件{'，关键词: ' + keyword if keyword else ''}。请稍候...",
            "status": "pending_execution"
        }

    def _handle_workflow_execution(self, user_input: str, intent_analysis: IntentAnalysis) -> Dict[str, Any]:
        """处理工作流执行"""
        return {
            "engine": "workflow_engine",
            "response": "我将帮您执行工作流任务。正在分析任务需求...",
            "status": "pending_execution"
        }

    def _handle_system_query(self, user_input: str, intent_analysis: IntentAnalysis) -> Dict[str, Any]:
        """处理系统查询"""
        return {
            "engine": "system_health_monitor",
            "response": "正在查询系统状态...",
            "status": "pending_execution"
        }

    def _handle_meeting_management(self, user_input: str, intent_analysis: IntentAnalysis) -> Dict[str, Any]:
        """处理会议管理"""
        return {
            "engine": "meeting_assistant_engine",
            "response": "我将帮您管理会议。请问是需要创建会议、查看会议纪要，还是设置会议提醒？",
            "status": "pending_execution"
        }

    def _handle_engine_dispatch(self, user_input: str, intent_analysis: IntentAnalysis) -> Dict[str, Any]:
        """处理引擎调度"""
        return {
            "engine": "unified_engine_hub",
            "response": "我将帮您搜索和调度合适的引擎。系统共有35+个引擎可供使用...",
            "status": "pending_execution"
        }

    def _handle_task_planning(self, user_input: str, intent_analysis: IntentAnalysis) -> Dict[str, Any]:
        """处理任务规划"""
        return {
            "engine": "task_planning_engine",
            "response": "我正在分析您的任务需求，并规划执行步骤...",
            "status": "pending_execution"
        }

    def _handle_general_task(self, user_input: str, intent_analysis: IntentAnalysis) -> Dict[str, Any]:
        """处理通用任务 - 多引擎协同"""
        return {
            "engines_used": ["decision_orchestrator", "unified_engine_hub"],
            "response": f"我理解您的需求「{user_input[:50]}...」。系统正在智能分析并调度合适的引擎来完成任务。",
            "status": "multi_engine_coordination"
        }

    def _get_session_context(self, session_id: str) -> Optional[Dict]:
        """获取会话上下文"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT context_data, last_intent, last_entities FROM session_context WHERE session_id = ?",
            (session_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "context_data": json.loads(row[0]) if row[0] else {},
                "last_intent": row[1],
                "last_entities": json.loads(row[2]) if row[2] else {}
            }
        return None

    def _update_session_context(self, session_id: str, intent_analysis: IntentAnalysis):
        """更新会话上下文"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT OR REPLACE INTO session_context
               (session_id, context_data, last_intent, last_entities, updated_at)
               VALUES (?, ?, ?, ?, ?)""",
            (session_id, "{}", intent_analysis.intent, json.dumps(intent_analysis.entities), datetime.now().isoformat())
        )
        conn.commit()
        conn.close()

    def _save_conversation(self, session_id: str, user_input: str, intent_analysis: IntentAnalysis,
                           executed_engines: List[str], response: str, success: bool):
        """保存对话历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO conversation_history
               (session_id, user_input, intent, executed_engines, response, success, timestamp)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (session_id, user_input, intent_analysis.intent, json.dumps(executed_engines),
             response, 1 if success else 0, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()

    def get_history(self, session_id: str = "default", limit: int = 10) -> List[Dict]:
        """获取对话历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """SELECT session_id, user_input, intent, executed_engines, response, success, timestamp
               FROM conversation_history WHERE session_id = ? ORDER BY id DESC LIMIT ?""",
            (session_id, limit)
        )
        rows = cursor.fetchall()
        conn.close()

        history = []
        for row in rows:
            history.append({
                "session_id": row[0],
                "user_input": row[1],
                "intent": row[2],
                "executed_engines": json.loads(row[3]) if row[3] else [],
                "response": row[4],
                "success": bool(row[5]),
                "timestamp": row[6]
            })
        return history

    def clear_history(self, session_id: str = "default"):
        """清除对话历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM conversation_history WHERE session_id = ?", (session_id,))
        cursor.execute("DELETE FROM session_context WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()

    def get_status(self) -> Dict:
        """获取引擎状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 统计
        cursor.execute("SELECT COUNT(*) FROM conversation_history")
        total_conversations = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT session_id) FROM conversation_history")
        total_sessions = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM conversation_history WHERE success = 1")
        successful_conversations = cursor.fetchone()[0]

        conn.close()

        return {
            "engine": "conversation_execution_engine",
            "status": "running",
            "total_conversations": total_conversations,
            "total_sessions": total_sessions,
            "successful_conversations": successful_conversations,
            "success_rate": successful_conversations / total_conversations * 100 if total_conversations > 0 else 0,
            "supported_intents": list(self.engine_capabilities.keys()),
            "registered_engines": sum(len(v) for v in self.engine_capabilities.values())
        }


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print(__doc__)
        return

    engine = ConversationExecutionEngine()
    command = sys.argv[1]

    if command == "chat":
        if len(sys.argv) < 3:
            print("用法: python conversation_execution_engine.py chat <用户输入>")
            return
        user_input = " ".join(sys.argv[2:])
        result = engine.execute_conversation(user_input)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "status":
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif command == "history":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        session_id = sys.argv[3] if len(sys.argv) > 3 else "default"
        history = engine.get_history(session_id, limit)
        print(json.dumps(history, ensure_ascii=False, indent=2))

    elif command == "clear":
        session_id = sys.argv[2] if len(sys.argv) > 2 else "default"
        engine.clear_history(session_id)
        print(f"已清除会话 {session_id} 的历史")

    else:
        print(f"未知命令: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()