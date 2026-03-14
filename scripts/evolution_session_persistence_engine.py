"""
智能全场景跨会话状态持久化与恢复引擎
(Evolution Session Persistence and Recovery Engine)

功能：
1. 跨会话状态持久化（进化环状态、任务进度、引擎状态）
2. 状态恢复（重启后恢复之前的进度）
3. 长时间任务支持（跨会话的复杂任务执行）
4. 中断恢复（意外中断后的自动恢复能力）
5. 与 do.py 深度集成

继承能力：
- evolution_loop_automation (round 73) - 进化闭环自动化
- evolution_full_auto_loop (round 300/306) - 全自动化进化环
- evolution_self_healing_advanced (round 290) - 深度自愈能力
- task_continuation_engine (round 149) - 跨会话任务接续

版本：1.0.0
"""

import json
import os
import sys
import shutil
import hashlib
import time
import signal
import atexit
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
from threading import Lock, Thread
import traceback

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 状态存储目录
STATE_DIR = PROJECT_ROOT / "runtime" / "state" / "session_persistence"
CHECKPOINT_DIR = STATE_DIR / "checkpoints"
BACKUP_DIR = STATE_DIR / "backups"


class PersistenceState(Enum):
    """持久化状态"""
    IDLE = "idle"
    SAVING = "saving"
    LOADING = "loading"
    RECOVERING = "recovering"
    ERROR = "error"


class TaskState(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Checkpoint:
    """检查点数据"""
    checkpoint_id: str
    timestamp: str
    mission_state: Dict[str, Any]
    task_states: List[Dict[str, Any]]
    engine_states: Dict[str, Any]
    session_data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "checkpoint_id": self.checkpoint_id,
            "timestamp": self.timestamp,
            "mission_state": self.mission_state,
            "task_states": self.task_states,
            "engine_states": self.engine_states,
            "session_data": self.session_data,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Checkpoint':
        return cls(
            checkpoint_id=data.get("checkpoint_id", ""),
            timestamp=data.get("timestamp", ""),
            mission_state=data.get("mission_state", {}),
            task_states=data.get("task_states", []),
            engine_states=data.get("engine_states", {}),
            session_data=data.get("session_data", {}),
            metadata=data.get("metadata", {})
        )


@dataclass
class LongRunningTask:
    """长时间运行任务"""
    task_id: str
    name: str
    description: str
    current_step: int
    total_steps: int
    state: TaskState
    progress: float  # 0.0 - 1.0
    state_snapshot: Dict[str, Any]  # 任务状态快照
    created_at: str
    updated_at: str
    checkpoint_id: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "state": self.state.value,
            "progress": self.progress,
            "state_snapshot": self.state_snapshot,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "checkpoint_id": self.checkpoint_id
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'LongRunningTask':
        return cls(
            task_id=data.get("task_id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            current_step=data.get("current_step", 0),
            total_steps=data.get("total_steps", 1),
            state=TaskState(data.get("state", "pending")),
            progress=data.get("progress", 0.0),
            state_snapshot=data.get("state_snapshot", {}),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            checkpoint_id=data.get("checkpoint_id")
        )


class SessionPersistenceEngine:
    """智能全场景跨会话状态持久化与恢复引擎"""

    def __init__(self, auto_save_interval: int = 300, max_checkpoints: int = 10, enable_backup: bool = True):
        """
        初始化引擎

        Args:
            auto_save_interval: 自动保存间隔（秒），默认 5 分钟
            max_checkpoints: 最大保存的检查点数量，默认 10
            enable_backup: 是否启用备份，默认 True
        """
        self.auto_save_interval = auto_save_interval
        self.max_checkpoints = max_checkpoints
        self.enable_backup = enable_backup
        self.state = PersistenceState.IDLE

        # 初始化目录
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
        if enable_backup:
            BACKUP_DIR.mkdir(parents=True, exist_ok=True)

        # 当前会话数据
        self.current_session = {
            "session_id": self._generate_session_id(),
            "start_time": datetime.now().isoformat(),
            "last_save_time": None,
            "mission_state": {},
            "task_states": [],
            "engine_states": {},
            "metadata": {}
        }

        # 长时运行任务
        self.long_running_tasks: Dict[str, LongRunningTask] = {}

        # 线程安全
        self._lock = Lock()
        self._auto_save_thread: Optional[Thread] = None
        self._stop_auto_save = False

        # 注册退出处理
        atexit.register(self._emergency_save)

        # 信号处理（支持 Ctrl+C 等）
        try:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
        except (ValueError, OSError):
            pass  # 某些环境不支持信号

    def _generate_session_id(self) -> str:
        """生成会话 ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_part = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        return f"session_{timestamp}_{random_part}"

    def _signal_handler(self, signum, frame):
        """信号处理器：确保退出前保存状态"""
        print(f"[SessionPersistence] 收到退出信号 {signum}，正在保存状态...")
        self._emergency_save()
        sys.exit(0)

    def _emergency_save(self):
        """紧急保存（退出时调用）"""
        try:
            with self._lock:
                self._save_session()
        except Exception as e:
            print(f"[SessionPersistence] 紧急保存失败: {e}")

    def save_state(self, mission_state: Optional[Dict] = None,
                   task_states: Optional[List[Dict]] = None,
                   engine_states: Optional[Dict] = None,
                   metadata: Optional[Dict] = None,
                   force: bool = False) -> bool:
        """
        保存当前状态

        Args:
            mission_state: 进化环状态
            task_states: 任务状态列表
            engine_states: 引擎状态
            metadata: 元数据
            force: 是否强制保存（忽略状态检查）

        Returns:
            保存是否成功
        """
        if not force and self.state == PersistenceState.SAVING:
            return False

        with self._lock:
            self.state = PersistenceState.SAVING
            try:
                # 更新当前会话数据
                if mission_state is not None:
                    self.current_session["mission_state"] = mission_state
                if task_states is not None:
                    self.current_session["task_states"] = task_states
                if engine_states is not None:
                    self.current_session["engine_states"] = engine_states
                if metadata is not None:
                    self.current_session["metadata"] = metadata

                # 保存会话
                success = self._save_session()

                # 如果有长时任务，同时保存检查点
                if self.long_running_tasks:
                    self._create_checkpoint("auto")

                return success
            except Exception as e:
                print(f"[SessionPersistence] 保存状态失败: {e}")
                self.state = PersistenceState.ERROR
                return False
            finally:
                if self.state != PersistenceState.ERROR:
                    self.state = PersistenceState.IDLE

    def _save_session(self) -> bool:
        """保存会话到文件"""
        try:
            # 更新保存时间
            self.current_session["last_save_time"] = datetime.now().isoformat()

            # 保存当前会话
            session_file = STATE_DIR / f"{self.current_session['session_id']}.json"
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_session, f, ensure_ascii=False, indent=2)

            # 保存最新的会话引用
            latest_file = STATE_DIR / "latest_session.json"
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "session_id": self.current_session["session_id"],
                    "last_save_time": self.current_session["last_save_time"],
                    "start_time": self.current_session["start_time"]
                }, f, ensure_ascii=False, indent=2)

            # 备份
            if self.enable_backup and BACKUP_DIR.exists():
                backup_file = BACKUP_DIR / f"{self.current_session['session_id']}.json"
                shutil.copy(session_file, backup_file)

            print(f"[SessionPersistence] 会话已保存: {self.current_session['session_id']}")
            return True
        except Exception as e:
            print(f"[SessionPersistence] 保存会话失败: {e}")
            return False

    def load_state(self) -> Optional[Dict]:
        """
        加载上一个会话的状态

        Returns:
            会话数据，如果无则返回 None
        """
        with self._lock:
            self.state = PersistenceState.LOADING
            try:
                # 查找最新的会话文件
                latest_file = STATE_DIR / "latest_session.json"
                if not latest_file.exists():
                    print("[SessionPersistence] 无历史会话可恢复")
                    return None

                with open(latest_file, 'r', encoding='utf-8') as f:
                    latest_info = json.load(f)

                session_id = latest_info.get("session_id")
                if not session_id:
                    return None

                session_file = STATE_DIR / f"{session_id}.json"
                if not session_file.exists():
                    # 尝试从备份恢复
                    backup_file = BACKUP_DIR / f"{session_id}.json"
                    if backup_file.exists():
                        session_file = backup_file
                    else:
                        return None

                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)

                # 更新当前会话
                self.current_session = session_data
                print(f"[SessionPersistence] 会话已恢复: {session_id}")
                return session_data

            except Exception as e:
                print(f"[SessionPersistence] 加载会话失败: {e}")
                self.state = PersistenceState.ERROR
                return None
            finally:
                if self.state != PersistenceState.ERROR:
                    self.state = PersistenceState.IDLE

    def recover_from_checkpoint(self, checkpoint_id: Optional[str] = None) -> Optional[Checkpoint]:
        """
        从检查点恢复

        Args:
            checkpoint_id: 检查点 ID，如果为 None 则使用最新的

        Returns:
            检查点数据，如果无则返回 None
        """
        with self._lock:
            self.state = PersistenceState.RECOVERING
            try:
                if checkpoint_id is None:
                    # 获取最新的检查点
                    checkpoints = list(CHECKPOINT_DIR.glob("checkpoint_*.json"))
                    if not checkpoints:
                        return None
                    checkpoints.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                    checkpoint_file = checkpoints[0]
                else:
                    checkpoint_file = CHECKPOINT_DIR / f"checkpoint_{checkpoint_id}.json"
                    if not checkpoint_file.exists():
                        return None

                with open(checkpoint_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                checkpoint = Checkpoint.from_dict(data)
                print(f"[SessionPersistence] 检查点已恢复: {checkpoint.checkpoint_id}")
                return checkpoint

            except Exception as e:
                print(f"[SessionPersistence] 恢复检查点失败: {e}")
                self.state = PersistenceState.ERROR
                return None
            finally:
                if self.state != PersistenceState.ERROR:
                    self.state = PersistenceState.IDLE

    def create_task(self, task_id: str, name: str, description: str,
                    total_steps: int, initial_state: Optional[Dict] = None) -> bool:
        """
        创建长时运行任务

        Args:
            task_id: 任务 ID
            name: 任务名称
            description: 任务描述
            total_steps: 总步骤数
            initial_state: 初始状态

        Returns:
            创建是否成功
        """
        with self._lock:
            if task_id in self.long_running_tasks:
                return False

            now = datetime.now().isoformat()
            task = LongRunningTask(
                task_id=task_id,
                name=name,
                description=description,
                current_step=0,
                total_steps=total_steps,
                state=TaskState.PENDING,
                progress=0.0,
                state_snapshot=initial_state or {},
                created_at=now,
                updated_at=now
            )
            self.long_running_tasks[task_id] = task
            print(f"[SessionPersistence] 长时任务已创建: {task_id} - {name}")
            return True

    def update_task_progress(self, task_id: str, current_step: int,
                            state_snapshot: Optional[Dict] = None) -> bool:
        """
        更新任务进度

        Args:
            task_id: 任务 ID
            current_step: 当前步骤
            state_snapshot: 状态快照

        Returns:
            更新是否成功
        """
        with self._lock:
            if task_id not in self.long_running_tasks:
                return False

            task = self.long_running_tasks[task_id]
            task.current_step = current_step
            task.progress = current_step / task.total_steps if task.total_steps > 0 else 0.0
            task.updated_at = datetime.now().isoformat()

            if state_snapshot is not None:
                task.state_snapshot = state_snapshot

            # 自动创建检查点
            if current_step % 5 == 0:  # 每 5 步创建一个检查点
                self._create_checkpoint(f"task_{task_id}")

            return True

    def pause_task(self, task_id: str) -> bool:
        """暂停任务"""
        with self._lock:
            if task_id not in self.long_running_tasks:
                return False

            task = self.long_running_tasks[task_id]
            task.state = TaskState.PAUSED
            task.updated_at = datetime.now().isoformat()

            # 保存检查点
            self._create_checkpoint(f"pause_{task_id}")
            return True

    def resume_task(self, task_id: str) -> bool:
        """恢复任务"""
        with self._lock:
            if task_id not in self.long_running_tasks:
                return False

            task = self.long_running_tasks[task_id]
            if task.state != TaskState.PAUSED:
                return False

            task.state = TaskState.RUNNING
            task.updated_at = datetime.now().isoformat()
            return True

    def complete_task(self, task_id: str, final_state: Optional[Dict] = None) -> bool:
        """完成任务"""
        with self._lock:
            if task_id not in self.long_running_tasks:
                return False

            task = self.long_running_tasks[task_id]
            task.state = TaskState.COMPLETED
            task.progress = 1.0
            task.current_step = task.total_steps
            task.updated_at = datetime.now().isoformat()

            if final_state:
                task.state_snapshot = final_state

            # 保存检查点
            self._create_checkpoint(f"complete_{task_id}")
            return True

    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        with self._lock:
            if task_id not in self.long_running_tasks:
                return False

            task = self.long_running_tasks[task_id]
            task.state = TaskState.CANCELLED
            task.updated_at = datetime.now().isoformat()
            return True

    def get_task_state(self, task_id: str) -> Optional[Dict]:
        """获取任务状态"""
        with self._lock:
            if task_id not in self.long_running_tasks:
                return None
            return self.long_running_tasks[task_id].to_dict()

    def list_tasks(self) -> List[Dict]:
        """列出所有任务"""
        with self._lock:
            return [task.to_dict() for task in self.long_running_tasks.values()]

    def _create_checkpoint(self, reason: str = "manual") -> Optional[str]:
        """创建检查点"""
        try:
            checkpoint_id = f"cp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(reason.encode()).hexdigest()[:6]}"
            checkpoint = Checkpoint(
                checkpoint_id=checkpoint_id,
                timestamp=datetime.now().isoformat(),
                mission_state=self.current_session.get("mission_state", {}),
                task_states=[task.to_dict() for task in self.long_running_tasks.values()],
                engine_states=self.current_session.get("engine_states", {}),
                session_data={
                    "session_id": self.current_session["session_id"],
                    "start_time": self.current_session["start_time"]
                },
                metadata={"reason": reason}
            )

            checkpoint_file = CHECKPOINT_DIR / f"checkpoint_{checkpoint_id}.json"
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint.to_dict(), f, ensure_ascii=False, indent=2)

            # 清理旧的检查点
            self._cleanup_old_checkpoints()

            print(f"[SessionPersistence] 检查点已创建: {checkpoint_id}")
            return checkpoint_id

        except Exception as e:
            print(f"[SessionPersistence] 创建检查点失败: {e}")
            return None

    def _cleanup_old_checkpoints(self):
        """清理旧的检查点"""
        try:
            checkpoints = list(CHECKPOINT_DIR.glob("checkpoint_*.json"))
            if len(checkpoints) > self.max_checkpoints:
                checkpoints.sort(key=lambda x: x.stat().st_mtime)
                for cp in checkpoints[:-self.max_checkpoints]:
                    cp.unlink()
        except Exception as e:
            print(f"[SessionPersistence] 清理检查点失败: {e}")

    def start_auto_save(self):
        """启动自动保存"""
        if self._auto_save_thread is not None and self._auto_save_thread.is_alive():
            return

        self._stop_auto_save = False
        self._auto_save_thread = Thread(target=self._auto_save_loop, daemon=True)
        self._auto_save_thread.start()
        print(f"[SessionPersistence] 自动保存已启动（间隔: {self.auto_save_interval}秒）")

    def stop_auto_save(self):
        """停止自动保存"""
        self._stop_auto_save = True
        if self._auto_save_thread is not None:
            self._auto_save_thread.join(timeout=5)
        print("[SessionPersistence] 自动保存已停止")

    def _auto_save_loop(self):
        """自动保存循环"""
        while not self._stop_auto_save:
            time.sleep(self.auto_save_interval)
            if not self._stop_auto_save:
                self.save_state(force=True)

    def get_status(self) -> Dict:
        """获取引擎状态"""
        return {
            "state": self.state.value,
            "session_id": self.current_session.get("session_id"),
            "start_time": self.current_session.get("start_time"),
            "last_save_time": self.current_session.get("last_save_time"),
            "task_count": len(self.long_running_tasks),
            "checkpoint_count": len(list(CHECKPOINT_DIR.glob("checkpoint_*.json"))) if CHECKPOINT_DIR.exists() else 0
        }


# 全局实例
_persistence_engine: Optional[SessionPersistenceEngine] = None


def get_persistence_engine() -> SessionPersistenceEngine:
    """获取全局持久化引擎实例"""
    global _persistence_engine
    if _persistence_engine is None:
        _persistence_engine = SessionPersistenceEngine()
    return _persistence_engine


# CLI 接口
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="智能全场景跨会话状态持久化与恢复引擎")
    parser.add_argument("action", choices=["save", "load", "checkpoint", "recover", "task", "status", "list"],
                        help="执行的动作")
    parser.add_argument("--mission", type=str, help="mission_state JSON 文件路径")
    parser.add_argument("--tasks", type=str, help="task_states JSON 文件路径")
    parser.add_argument("--engines", type=str, help="engine_states JSON 文件路径")
    parser.add_argument("--task-id", type=str, help="任务 ID")
    parser.add_argument("--task-name", type=str, help="任务名称")
    parser.add_argument("--task-steps", type=int, help="任务总步骤数")
    parser.add_argument("--checkpoint-id", type=str, help="检查点 ID")
    parser.add_argument("--force", action="store_true", help="强制执行")

    args = parser.parse_args()
    engine = get_persistence_engine()

    if args.action == "save":
        mission_state = None
        task_states = None
        engine_states = None

        if args.mission:
            with open(args.mission, 'r', encoding='utf-8') as f:
                mission_state = json.load(f)
        if args.tasks:
            with open(args.tasks, 'r', encoding='utf-8') as f:
                task_states = json.load(f)
        if args.engines:
            with open(args.engines, 'r', encoding='utf-8') as f:
                engine_states = json.load(f)

        success = engine.save_state(mission_state, task_states, engine_states, force=args.force)
        print(f"保存结果: {'成功' if success else '失败'}")

    elif args.action == "load":
        session_data = engine.load_state()
        if session_data:
            print(f"会话已恢复: {session_data.get('session_id')}")
        else:
            print("无法恢复会话")

    elif args.action == "checkpoint":
        checkpoint_id = engine._create_checkpoint("manual")
        print(f"检查点已创建: {checkpoint_id}" if checkpoint_id else "创建失败")

    elif args.action == "recover":
        checkpoint = engine.recover_from_checkpoint(args.checkpoint_id)
        if checkpoint:
            print(f"检查点已恢复: {checkpoint.checkpoint_id}")
            print(f"任务状态: {len(checkpoint.task_states)} 个")
        else:
            print("无法恢复检查点")

    elif args.action == "task":
        if not args.task_id or not args.task_name or not args.task_steps:
            print("错误: 需要 --task-id, --task-name, --task-steps")
        else:
            engine.create_task(args.task_id, args.task_name, "", args.task_steps)
            print(f"任务已创建: {args.task_id}")

    elif args.action == "status":
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.action == "list":
        tasks = engine.list_tasks()
        print(json.dumps(tasks, ensure_ascii=False, indent=2))