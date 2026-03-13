#!/usr/bin/env python3
"""
智能进化协同增强引擎 (Evolution Collaboration Enhancer)
让70+引擎能够像神经网络一样协同工作，共享信息、自主触发、形成闭环，
实现真正的分布式智能自进化。

功能：
1. 引擎间信息共享机制 - 建立引擎通信总线，实现信息实时共享
2. 智能协同触发 - 基于事件驱动，自动触发相关引擎协同工作
3. 闭环协作 - 实现感知→分析→决策→执行→反馈完整闭环
4. 协同状态追踪 - 实时追踪协同任务状态，优化协同策略
"""

import json
import os
import sys
import subprocess
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from collections import defaultdict

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE_DIR = PROJECT_ROOT / "runtime" / "state"
RUNTIME_LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
REFERENCES_DIR = PROJECT_ROOT / "references"


class EvolutionCollaborationEnhancer:
    """智能进化协同增强引擎"""

    def __init__(self):
        self.name = "EvolutionCollaborationEnhancer"
        self.version = "1.0.0"
        self.collaboration_state_file = RUNTIME_STATE_DIR / "evolution_collaboration_state.json"
        self.event_bus_file = RUNTIME_STATE_DIR / "evolution_event_bus.json"
        self.collaboration_log_file = RUNTIME_LOGS_DIR / "evolution_collaboration.log"

        # 初始化协同状态
        self.collaboration_state = self._load_collaboration_state()
        self.event_bus = self._load_event_bus()

    def _load_collaboration_state(self) -> Dict:
        """加载协同状态"""
        if self.collaboration_state_file.exists():
            try:
                with open(self.collaboration_state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "active_collaborations": [],
            "completed_collaborations": [],
            "engine_relationships": {},
            "collaboration_patterns": [],
            "last_updated": datetime.now().isoformat()
        }

    def _load_event_bus(self) -> Dict:
        """加载事件总线"""
        if self.event_bus_file.exists():
            try:
                with open(self.event_bus_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "events": [],
            "subscribers": {},
            "pending_events": []
        }

    def _save_collaboration_state(self):
        """保存协同状态"""
        self.collaboration_state["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.collaboration_state_file, 'w', encoding='utf-8') as f:
                json.dump(self.collaboration_state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存协同状态失败: {e}")

    def _save_event_bus(self):
        """保存事件总线"""
        try:
            with open(self.event_bus_file, 'w', encoding='utf-8') as f:
                json.dump(self.event_bus, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存事件总线失败: {e}")

    def _log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        try:
            with open(self.collaboration_log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception:
            pass

    def get_status(self) -> Dict:
        """获取协同引擎状态"""
        # 分析引擎关系
        engine_relationships = self._analyze_engine_relationships()

        # 统计协同数据
        total_collaborations = len(self.collaboration_state.get("active_collaborations", [])) + \
                              len(self.collaboration_state.get("completed_collaborations", []))

        # 统计事件
        total_events = len(self.event_bus.get("events", []))

        # 统计协同模式
        total_patterns = len(self.collaboration_state.get("collaboration_patterns", []))

        return {
            "engine": self.name,
            "version": self.version,
            "status": "running",
            "total_collaborations": total_collaborations,
            "active_collaborations": len(self.collaboration_state.get("active_collaborations", [])),
            "total_events": total_events,
            "collaboration_patterns": total_patterns,
            "engine_relationships_count": len(engine_relationships),
            "last_updated": self.collaboration_state.get("last_updated", "")
        }

    def _analyze_engine_relationships(self) -> Dict:
        """分析引擎间关系"""
        relationships = defaultdict(list)

        # 扫描所有进化相关脚本
        script_files = list(SCRIPTS_DIR.glob("evolution*.py"))

        # 提取引擎名称和关系
        for script_file in script_files:
            engine_name = script_file.stem

            # 读取脚本内容查找依赖
            try:
                with open(script_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                    # 查找 import 语句中的其他引擎
                    for other_script in script_files:
                        other_name = other_script.stem
                        if other_name != engine_name and other_name in content:
                            if engine_name not in relationships[other_name]:
                                relationships[other_name].append(engine_name)

            except Exception:
                continue

        return dict(relationships)

    def register_event(self, event_type: str, event_data: Dict, source_engine: str) -> Dict:
        """注册事件到事件总线"""
        event = {
            "id": f"evt_{datetime.now().timestamp()}",
            "type": event_type,
            "data": event_data,
            "source": source_engine,
            "timestamp": datetime.now().isoformat(),
            "status": "pending"
        }

        self.event_bus["events"].append(event)
        self.event_bus["pending_events"].append(event["id"])

        # 自动触发相关订阅者
        triggered_engines = self._trigger_subscribers(event)

        self._save_event_bus()

        self._log(f"事件已注册: {event_type} from {source_engine}, 触发 {len(triggered_engines)} 个引擎")

        return {
            "event_id": event["id"],
            "event_type": event_type,
            "triggered_engines": triggered_engines,
            "status": "registered"
        }

    def subscribe_event(self, event_type: str, target_engine: str, callback_action: str):
        """订阅事件"""
        if event_type not in self.event_bus["subscribers"]:
            self.event_bus["subscribers"][event_type] = []

        self.event_bus["subscribers"][event_type].append({
            "engine": target_engine,
            "action": callback_action,
            "subscribed_at": datetime.now().isoformat()
        })

        self._save_event_bus()

        return {"status": "subscribed", "event_type": event_type, "engine": target_engine}

    def _trigger_subscribers(self, event: Dict) -> List[str]:
        """触发事件订阅者"""
        triggered = []
        event_type = event.get("type", "")

        subscribers = self.event_bus.get("subscribers", {}).get(event_type, [])

        for subscriber in subscribers:
            engine = subscriber.get("engine", "")
            action = subscriber.get("action", "")

            # 在实际实现中，这里会触发引擎执行
            triggered.append(engine)

            self._log(f"触发引擎 {engine} 执行动作 {action}")

        return triggered

    def create_collaboration(self, task_id: str, participating_engines: List[str],
                            task_type: str, priority: int = 5) -> Dict:
        """创建协同任务"""
        collaboration = {
            "id": task_id,
            "status": "active",
            "participating_engines": participating_engines,
            "task_type": task_type,
            "priority": priority,
            "created_at": datetime.now().isoformat(),
            "progress": 0,
            "completed_engines": [],
            "failed_engines": [],
            "events": []
        }

        self.collaboration_state["active_collaborations"].append(collaboration)

        # 更新引擎关系
        self._update_engine_relationships(participating_engines)

        # 发现协同模式
        self._discover_collaboration_pattern(task_type, participating_engines)

        self._save_collaboration_state()

        self._log(f"创建协同任务 {task_id}, 参与引擎: {', '.join(participating_engines)}")

        return {"status": "created", "collaboration_id": task_id}

    def _update_engine_relationships(self, engines: List[str]):
        """更新引擎关系"""
        relationships = self.collaboration_state.get("engine_relationships", {})

        # 为每个引擎建立关系
        for i, engine in enumerate(engines):
            if engine not in relationships:
                relationships[engine] = {"collaborated_with": [], "collaboration_count": 0}

            # 添加与其他引擎的协作关系
            for j, other_engine in enumerate(engines):
                if i != j and other_engine not in relationships[engine]["collaborated_with"]:
                    relationships[engine]["collaborated_with"].append(other_engine)

            relationships[engine]["collaboration_count"] += 1

        self.collaboration_state["engine_relationships"] = relationships

    def _discover_collaboration_pattern(self, task_type: str, engines: List[str]):
        """发现协同模式"""
        patterns = self.collaboration_state.get("collaboration_patterns", [])

        # 检查是否已存在相同模式
        existing_pattern = None
        for pattern in patterns:
            if pattern.get("task_type") == task_type:
                existing_pattern = pattern
                break

        if existing_pattern:
            # 更新模式使用次数
            existing_pattern["usage_count"] = existing_pattern.get("usage_count", 0) + 1
            existing_pattern["last_used"] = datetime.now().isoformat()
        else:
            # 创建新模式
            new_pattern = {
                "task_type": task_type,
                "engine_sequence": engines,
                "usage_count": 1,
                "first_used": datetime.now().isoformat(),
                "last_used": datetime.now().isoformat()
            }
            patterns.append(new_pattern)

        self.collaboration_state["collaboration_patterns"] = patterns

    def update_collaboration_progress(self, task_id: str, engine: str,
                                     progress: int, status: str = "running") -> Dict:
        """更新协同任务进度"""
        for collab in self.collaboration_state.get("active_collaborations", []):
            if collab.get("id") == task_id:
                collab["progress"] = progress

                if status == "completed":
                    collab["completed_engines"].append(engine)
                elif status == "failed":
                    collab["failed_engines"].append(engine)

                # 检查是否全部完成
                completed = len(collab.get("completed_engines", []))
                total = len(collab.get("participating_engines", []))

                if completed >= total:
                    collab["status"] = "completed"
                    collab["completed_at"] = datetime.now().isoformat()

                    # 移动到已完成列表
                    self.collaboration_state["active_collaborations"].remove(collab)
                    self.collaboration_state["completed_collaborations"].append(collab)

                self._save_collaboration_state()

                self._log(f"协同任务 {task_id} 进度更新: {progress}%, 引擎 {engine} 状态: {status}")

                return {"status": "updated", "progress": progress}

        return {"status": "not_found", "task_id": task_id}

    def get_recommended_collaboration(self, task_type: str) -> Dict:
        """获取推荐协同方案"""
        patterns = self.collaboration_state.get("collaboration_patterns", [])

        # 查找相似任务类型的模式
        best_pattern = None
        for pattern in patterns:
            if pattern.get("task_type") == task_type:
                if best_pattern is None or pattern.get("usage_count", 0) > best_pattern.get("usage_count", 0):
                    best_pattern = pattern

        if best_pattern:
            return {
                "recommended": True,
                "task_type": task_type,
                "engine_sequence": best_pattern.get("engine_sequence", []),
                "usage_count": best_pattern.get("usage_count", 0),
                "confidence": min(best_pattern.get("usage_count", 0) / 10, 1.0)
            }

        # 无历史模式，返回默认推荐
        return {
            "recommended": False,
            "task_type": task_type,
            "message": "无历史协同模式，建议手动指定引擎组合"
        }

    def analyze_collaboration_efficiency(self) -> Dict:
        """分析协同效率"""
        completed = self.collaboration_state.get("completed_collaborations", [])

        if not completed:
            return {
                "total_collaborations": 0,
                "average_completion_time": 0,
                "success_rate": 0,
                "top_engines": []
            }

        # 统计完成时间
        total_time = 0
        successful = 0

        for collab in completed:
            if "created_at" in collab and "completed_at" in collab:
                try:
                    start = datetime.fromisoformat(collab["created_at"])
                    end = datetime.fromisoformat(collab["completed_at"])
                    total_time += (end - start).total_seconds()

                    if collab.get("status") == "completed":
                        successful += 1
                except Exception:
                    pass

        avg_time = total_time / len(completed) if completed else 0
        success_rate = successful / len(completed) if completed else 0

        # 统计最活跃引擎
        engine_counts = defaultdict(int)
        for collab in completed:
            for engine in collab.get("participating_engines", []):
                engine_counts[engine] += 1

        top_engines = sorted(engine_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "total_collaborations": len(completed),
            "average_completion_time_seconds": avg_time,
            "success_rate": success_rate,
            "top_engines": [{"engine": e, "count": c} for e, c in top_engines]
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="智能进化协同增强引擎")
    parser.add_argument("command", nargs="?", default="status",
                       help="命令: status/create/subscribe/trigger/analyze/recommend")
    parser.add_argument("--task-id", help="任务ID")
    parser.add_argument("--engines", help="引擎列表，逗号分隔")
    parser.add_argument("--task-type", help="任务类型")
    parser.add_argument("--event-type", help="事件类型")
    parser.add_argument("--event-data", help="事件数据JSON")
    parser.add_argument("--source", help="源引擎")
    parser.add_argument("--target", help="目标引擎")
    parser.add_argument("--action", help="回调动作")
    parser.add_argument("--engine", help="引擎名称")
    parser.add_argument("--progress", type=int, help="进度百分比")

    args = parser.parse_args()

    enhancer = EvolutionCollaborationEnhancer()

    if args.command == "status":
        result = enhancer.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "create":
        if not args.task_id or not args.engines or not args.task_type:
            print("错误: 需要 --task-id --engines --task-type")
            sys.exit(1)

        engines = [e.strip() for e in args.engines.split(",")]
        result = enhancer.create_collaboration(args.task_id, engines, args.task_type)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "subscribe":
        if not args.event_type or not args.target or not args.action:
            print("错误: 需要 --event-type --target --action")
            sys.exit(1)

        result = enhancer.subscribe_event(args.event_type, args.target, args.action)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "trigger":
        if not args.event_type or not args.source:
            print("错误: 需要 --event-type --source")
            sys.exit(1)

        event_data = {}
        if args.event_data:
            try:
                event_data = json.loads(args.event_data)
            except Exception:
                pass

        result = enhancer.register_event(args.event_type, event_data, args.source)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "update":
        if not args.task_id or not args.engine or args.progress is None:
            print("错误: 需要 --task-id --engine --progress")
            sys.exit(1)

        status = "completed" if args.progress >= 100 else "running"
        result = enhancer.update_collaboration_progress(args.task_id, args.engine, args.progress, status)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "recommend":
        if not args.task_type:
            print("错误: 需要 --task-type")
            sys.exit(1)

        result = enhancer.get_recommended_collaboration(args.task_type)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "analyze":
        result = enhancer.analyze_collaboration_efficiency()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "relationships":
        result = enhancer._analyze_engine_relationships()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {args.command}")
        parser.print_help()


if __name__ == "__main__":
    main()