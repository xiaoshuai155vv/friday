#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环跨引擎知识实时更新与智能同步深度集成引擎
================================================================
在 round 490 完成的跨引擎知识自动推荐与智能预测触发引擎基础上，
进一步增强跨引擎知识的实时更新与智能同步能力。

让系统能够监控知识库变化、自动同步最新知识、实现跨引擎知识一致性保障、
形成知识动态更新闭环。实现从「被动推荐」到「主动实时更新」的范式升级，
让系统决策始终基于最新知识状态。

功能：
1. 知识库变化实时监控 - 监控各引擎知识存储变化
2. 跨引擎知识自动同步 - 实时同步最新知识到各引擎
3. 知识一致性保障 - 版本控制、冲突解决
4. 知识动态更新闭环 - 监控→同步→验证→反馈
5. 与进化驾驶舱深度集成
6. 集成到 do.py 支持知识实时更新、知识同步、动态知识、实时同步等关键词触发

version: 1.0.0
"""

import os
import sys
import json
import re
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict
import threading

# 解决 Windows 控制台 Unicode 输出问题
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# 路径配置
BASE_DIR = Path(__file__).parent.parent
RUNTIME_DIR = BASE_DIR / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
KNOWLEDGE_DIR = RUNTIME_DIR / "knowledge"
LOGS_DIR = RUNTIME_DIR / "logs"

# 存储文件路径
KNOWLEDGE_VERSION_FILE = STATE_DIR / "knowledge_version_control.json"
KNOWLEDGE_SYNC_STATE_FILE = STATE_DIR / "knowledge_sync_state.json"
KNOWLEDGE_CHANGE_LOG_FILE = STATE_DIR / "knowledge_change_log.json"
KNOWLEDGE_CONFLICT_FILE = STATE_DIR / "knowledge_conflicts.json"
UPDATE_CONFIG_FILE = STATE_DIR / "knowledge_update_config.json"


def _safe_print(text: str):
    """安全打印"""
    try:
        print(text)
    except UnicodeEncodeError:
        clean_text = re.sub(r'[^\x00-\x7F]+', '', text)
        print(clean_text)


class KnowledgeRealtimeUpdateSyncEngine:
    """跨引擎知识实时更新与智能同步深度集成引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.engine_name = "跨引擎知识实时更新与智能同步深度集成引擎"

        # 确保目录存在
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

        # 加载数据
        self.version_control = self._load_version_control()
        self.sync_state = self._load_sync_state()
        self.change_log = self._load_change_log()
        self.conflicts = self._load_conflicts()
        self.update_config = self._load_update_config()

        # 监控状态
        self.monitoring = False
        self.monitor_thread = None

        _safe_print(f"[{self.engine_name} v{self.version}] 初始化完成")

    def _load_version_control(self) -> Dict:
        """加载版本控制数据"""
        if KNOWLEDGE_VERSION_FILE.exists():
            try:
                with open(KNOWLEDGE_VERSION_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {"knowledge_versions": {}, "update_history": []}
        return {"knowledge_versions": {}, "update_history": []}

    def _save_version_control(self):
        """保存版本控制数据"""
        try:
            with open(KNOWLEDGE_VERSION_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.version_control, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[警告] 保存版本控制数据失败: {e}")

    def _load_sync_state(self) -> Dict:
        """加载同步状态"""
        if KNOWLEDGE_SYNC_STATE_FILE.exists():
            try:
                with open(KNOWLEDGE_SYNC_STATE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {"sync_records": [], "last_sync_time": None, "sync_status": "idle"}
        return {"sync_records": [], "last_sync_time": None, "sync_status": "idle"}

    def _save_sync_state(self):
        """保存同步状态"""
        try:
            with open(KNOWLEDGE_SYNC_STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.sync_state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[警告] 保存同步状态失败: {e}")

    def _load_change_log(self) -> Dict:
        """加载变更日志"""
        if KNOWLEDGE_CHANGE_LOG_FILE.exists():
            try:
                with open(KNOWLEDGE_CHANGE_LOG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {"changes": []}
        return {"changes": []}

    def _save_change_log(self):
        """保存变更日志"""
        try:
            with open(KNOWLEDGE_CHANGE_LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.change_log, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[警告] 保存变更日志失败: {e}")

    def _load_conflicts(self) -> List[Dict]:
        """加载冲突列表"""
        if KNOWLEDGE_CONFLICT_FILE.exists():
            try:
                with open(KNOWLEDGE_CONFLICT_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_conflicts(self):
        """保存冲突列表"""
        try:
            with open(KNOWLEDGE_CONFLICT_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.conflicts, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[警告] 保存冲突列表失败: {e}")

    def _load_update_config(self) -> Dict:
        """加载更新配置"""
        if UPDATE_CONFIG_FILE.exists():
            try:
                with open(UPDATE_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return self._get_default_update_config()
        return self._get_default_update_config()

    def _get_default_update_config(self) -> Dict:
        """获取默认更新配置"""
        return {
            "auto_sync_enabled": True,
            "sync_interval_seconds": 60,
            "version_check_enabled": True,
            "conflict_resolution": "latest",
            "monitored_paths": [
                str(STATE_DIR),
                str(KNOWLEDGE_DIR)
            ],
            "excluded_patterns": ["*.log", "*.tmp", "__pycache__"],
            "max_history_size": 100
        }

    def _save_update_config(self):
        """保存更新配置"""
        try:
            with open(UPDATE_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.update_config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[警告] 保存更新配置失败: {e}")

    def compute_file_hash(self, file_path: Path) -> Optional[str]:
        """计算文件哈希值"""
        try:
            if not file_path.exists() or file_path.is_dir():
                return None

            hasher = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return None

    def scan_knowledge_files(self) -> Dict[str, Dict]:
        """扫描知识文件并获取哈希"""
        knowledge_files = {}

        for base_path in self.update_config.get("monitored_paths", []):
            path = Path(base_path)
            if not path.exists():
                continue

            for file_path in path.rglob("*"):
                if file_path.is_file():
                    # 检查排除模式
                    excluded = False
                    for pattern in self.update_config.get("excluded_patterns", []):
                        if file_path.match(pattern):
                            excluded = True
                            break

                    if not excluded:
                        file_hash = self.compute_file_hash(file_path)
                        rel_path = str(file_path.relative_to(BASE_DIR))
                        knowledge_files[rel_path] = {
                            "hash": file_hash,
                            "modified": file_path.stat().st_mtime,
                            "size": file_path.stat().st_size,
                            "full_path": str(file_path)
                        }

        return knowledge_files

    def detect_changes(self) -> Dict:
        """检测知识文件变化"""
        current_files = self.scan_knowledge_files()
        version_control = self.version_control.get("knowledge_versions", {})

        changes = {
            "added": [],
            "modified": [],
            "deleted": [],
            "unchanged": []
        }

        # 检测新增和修改
        for file_path, file_info in current_files.items():
            if file_path not in version_control:
                changes["added"].append({
                    "path": file_path,
                    "info": file_info
                })
            elif version_control[file_path]["hash"] != file_info["hash"]:
                changes["modified"].append({
                    "path": file_path,
                    "old_hash": version_control[file_path]["hash"],
                    "new_hash": file_info["hash"],
                    "info": file_info
                })
            else:
                changes["unchanged"].append(file_path)

        # 检测删除
        for file_path in version_control:
            if file_path not in current_files:
                changes["deleted"].append({
                    "path": file_path,
                    "old_hash": version_control[file_path]["hash"]
                })

        return changes

    def record_change(self, change_type: str, file_path: str, file_info: Dict):
        """记录变更到日志"""
        change_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": change_type,
            "path": file_path,
            "info": file_info
        }

        self.change_log["changes"].append(change_entry)

        # 限制历史大小
        max_size = self.update_config.get("max_history_size", 100)
        if len(self.change_log["changes"]) > max_size:
            self.change_log["changes"] = self.change_log["changes"][-max_size:]

        self._save_change_log()

    def sync_knowledge(self, changes: Dict) -> Dict:
        """同步知识变更"""
        sync_result = {
            "success": True,
            "synced_files": [],
            "failed_files": [],
            "conflicts": [],
            "timestamp": datetime.now().isoformat()
        }

        # 处理新增文件
        for change in changes.get("added", []):
            file_path = change["path"]
            file_info = change["info"]

            try:
                # 更新版本控制
                self.version_control["knowledge_versions"][file_path] = {
                    "hash": file_info["hash"],
                    "modified": file_info["modified"],
                    "size": file_info["size"],
                    "first_seen": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "version": 1
                }

                # 记录同步记录
                self.sync_state["sync_records"].append({
                    "timestamp": datetime.now().isoformat(),
                    "action": "add",
                    "path": file_path,
                    "hash": file_info["hash"]
                })

                sync_result["synced_files"].append(file_path)

                # 记录变更
                self.record_change("add", file_path, file_info)

            except Exception as e:
                sync_result["failed_files"].append({
                    "path": file_path,
                    "error": str(e)
                })

        # 处理修改的文件
        for change in changes.get("modified", []):
            file_path = change["path"]
            new_info = change["info"]

            try:
                old_version = self.version_control["knowledge_versions"].get(file_path, {}).get("version", 0)

                # 更新版本控制
                self.version_control["knowledge_versions"][file_path] = {
                    "hash": new_info["hash"],
                    "modified": new_info["modified"],
                    "size": new_info["size"],
                    "last_updated": datetime.now().isoformat(),
                    "version": old_version + 1
                }

                # 记录同步记录
                self.sync_state["sync_records"].append({
                    "timestamp": datetime.now().isoformat(),
                    "action": "update",
                    "path": file_path,
                    "hash": new_info["hash"],
                    "old_version": old_version,
                    "new_version": old_version + 1
                })

                sync_result["synced_files"].append(file_path)

                # 记录变更
                self.record_change("update", file_path, new_info)

            except Exception as e:
                sync_result["failed_files"].append({
                    "path": file_path,
                    "error": str(e)
                })

        # 处理删除的文件
        for change in changes.get("deleted", []):
            file_path = change["path"]

            try:
                if file_path in self.version_control["knowledge_versions"]:
                    del self.version_control["knowledge_versions"][file_path]

                # 记录同步记录
                self.sync_state["sync_records"].append({
                    "timestamp": datetime.now().isoformat(),
                    "action": "delete",
                    "path": file_path
                })

                sync_result["synced_files"].append(file_path)

                # 记录变更
                self.record_change("delete", file_path, {})

            except Exception as e:
                sync_result["failed_files"].append({
                    "path": file_path,
                    "error": str(e)
                })

        # 更新同步状态
        self.sync_state["last_sync_time"] = datetime.now().isoformat()
        self.sync_state["sync_status"] = "completed"

        # 保存数据
        self._save_version_control()
        self._save_sync_state()

        return sync_result

    def run_sync_cycle(self) -> Dict:
        """运行完整同步周期"""
        _safe_print("\n=== 运行知识同步周期 ===")

        # 检测变化
        _safe_print("[1/3] 检测知识文件变化...")
        changes = self.detect_changes()

        _safe_print(f"  新增: {len(changes['added'])} 文件")
        _safe_print(f"  修改: {len(changes['modified'])} 文件")
        _safe_print(f"  删除: {len(changes['deleted'])} 文件")

        if not changes["added"] and not changes["modified"] and not changes["deleted"]:
            _safe_print("  无变化，跳过同步")
            return {
                "success": True,
                "message": "无变化",
                "changes": changes
            }

        # 同步
        _safe_print("[2/3] 同步知识变更...")
        sync_result = self.sync_knowledge(changes)

        _safe_print(f"  成功同步: {len(sync_result['synced_files'])} 文件")
        if sync_result["failed_files"]:
            _safe_print(f"  同步失败: {len(sync_result['failed_files'])} 文件")

        # 验证
        _safe_print("[3/3] 验证同步结果...")
        verification = self.verify_sync(sync_result)

        _safe_print(f"  验证通过: {verification['verified']}")
        _safe_print(f"  验证失败: {verification['failed']}")

        return {
            "success": sync_result["success"],
            "changes": changes,
            "sync_result": sync_result,
            "verification": verification,
            "timestamp": datetime.now().isoformat()
        }

    def verify_sync(self, sync_result: Dict) -> Dict:
        """验证同步结果"""
        verification = {
            "verified": 0,
            "failed": 0,
            "details": []
        }

        for file_path in sync_result.get("synced_files", []):
            try:
                # 重新检查文件哈希
                version_info = self.version_control.get("knowledge_versions", {}).get(file_path)
                if version_info:
                    file_full_path = Path(BASE_DIR) / file_path
                    current_hash = self.compute_file_hash(file_full_path)

                    if current_hash == version_info.get("hash"):
                        verification["verified"] += 1
                        verification["details"].append({
                            "path": file_path,
                            "status": "verified"
                        })
                    else:
                        verification["failed"] += 1
                        verification["details"].append({
                            "path": file_path,
                            "status": "failed",
                            "reason": "hash_mismatch"
                        })
            except Exception as e:
                verification["failed"] += 1
                verification["details"].append({
                    "path": file_path,
                    "status": "failed",
                    "reason": str(e)
                })

        return verification

    def start_monitoring(self, interval_seconds: int = 60):
        """启动实时监控"""
        if self.monitoring:
            _safe_print("[警告] 监控已在运行中")
            return

        self.monitoring = True
        self.update_config["sync_interval_seconds"] = interval_seconds
        self._save_update_config()

        def monitor_loop():
            _safe_print(f"[监控] 开始监控知识库变化 (间隔: {interval_seconds}秒)")
            while self.monitoring:
                try:
                    self.run_sync_cycle()
                except Exception as e:
                    _safe_print(f"[监控] 错误: {e}")

                # 等待下一个周期
                for _ in range(interval_seconds):
                    if not self.monitoring:
                        break
                    time.sleep(1)

            _safe_print("[监控] 监控已停止")

        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        _safe_print("[监控] 已请求停止监控")

    def get_status(self) -> Dict:
        """获取引擎状态"""
        return {
            "engine_name": self.engine_name,
            "version": self.version,
            "monitoring": self.monitoring,
            "last_sync_time": self.sync_state.get("last_sync_time"),
            "sync_status": self.sync_state.get("sync_status"),
            "total_tracked_files": len(self.version_control.get("knowledge_versions", {})),
            "total_changes": len(self.change_log.get("changes", [])),
            "total_sync_records": len(self.sync_state.get("sync_records", [])),
            "conflicts_count": len(self.conflicts),
            "update_config": self.update_config
        }

    def get_cockpit_data(self) -> Dict:
        """获取驾驶舱数据"""
        status = self.get_status()

        # 获取最近变更
        recent_changes = self.change_log.get("changes", [])[-10:]

        # 获取最近同步记录
        recent_sync = self.sync_state.get("sync_records", [])[-10:]

        # 获取版本分布
        version_distribution = defaultdict(int)
        for v in self.version_control.get("knowledge_versions", {}).values():
            version_distribution[v.get("version", 0)] += 1

        return {
            "engine_name": self.engine_name,
            "version": self.version,
            "status": status,
            "recent_changes": recent_changes,
            "recent_sync": recent_sync,
            "version_distribution": dict(version_distribution),
            "health_score": self._calculate_health_score()
        }

    def _calculate_health_score(self) -> float:
        """计算健康分数"""
        score = 100.0

        # 监控状态
        if not self.monitoring:
            score -= 10

        # 冲突数量
        conflict_penalty = min(len(self.conflicts) * 5, 30)
        score -= conflict_penalty

        # 同步失败
        failed_sync = len([r for r in self.sync_state.get("sync_records", [])
                          if "error" in r or r.get("action") == "failed"])
        failed_penalty = min(failed_sync * 2, 20)
        score -= failed_penalty

        return max(score, 0)

    def get_update_summary(self) -> Dict:
        """获取更新摘要"""
        return {
            "total_knowledge_items": len(self.version_control.get("knowledge_versions", {})),
            "total_changes_today": len([
                c for c in self.change_log.get("changes", [])
                if datetime.fromisoformat(c["timestamp"]).date() == datetime.now().date()
            ]),
            "last_sync_time": self.sync_state.get("last_sync_time"),
            "sync_status": self.sync_state.get("sync_status"),
            "monitoring_active": self.monitoring,
            "health_score": self._calculate_health_score()
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能全场景进化环跨引擎知识实时更新与智能同步深度集成引擎"
    )
    parser.add_argument("--sync", action="store_true", help="运行同步周期")
    parser.add_argument("--detect-changes", action="store_true", help="检测知识文件变化")
    parser.add_argument("--start-monitor", action="store_true", help="启动实时监控")
    parser.add_argument("--stop-monitor", action="store_true", help="停止实时监控")
    parser.add_argument("--verify", action="store_true", help="验证同步结果")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")
    parser.add_argument("--status", action="store_true", help="显示状态")
    parser.add_argument("--summary", action="store_true", help="获取更新摘要")

    args = parser.parse_args()

    engine = KnowledgeRealtimeUpdateSyncEngine()

    if args.detect_changes:
        changes = engine.detect_changes()
        print("\n=== 知识文件变化检测结果 ===")
        print(f"新增: {len(changes['added'])} 文件")
        print(f"修改: {len(changes['modified'])} 文件")
        print(f"删除: {len(changes['deleted'])} 文件")
        print(f"未变: {len(changes['unchanged'])} 文件")
        print(json.dumps(changes, ensure_ascii=False, indent=2))

    elif args.sync:
        result = engine.run_sync_cycle()
        print("\n=== 同步结果 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.start_monitor:
        interval = 60
        engine.start_monitoring(interval)
        print(f"\n=== 监控已启动 (间隔: {interval}秒) ===")
        print("按 Ctrl+C 停止监控")

        try:
            while engine.monitoring:
                time.sleep(1)
        except KeyboardInterrupt:
            engine.stop_monitoring()

    elif args.stop_monitor:
        engine.stop_monitoring()
        print("\n=== 监控已停止 ===")

    elif args.verify:
        sync_result = {"synced_files": list(engine.version_control.get("knowledge_versions", {}).keys())}
        verification = engine.verify_sync(sync_result)
        print("\n=== 验证结果 ===")
        print(json.dumps(verification, ensure_ascii=False, indent=2))

    elif args.cockpit_data:
        data = engine.get_cockpit_data()
        print("\n=== 驾驶舱数据 ===")
        print(json.dumps(data, ensure_ascii=False, indent=2))

    elif args.status:
        status = engine.get_status()
        print("\n=== 引擎状态 ===")
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.summary:
        summary = engine.get_update_summary()
        print("\n=== 更新摘要 ===")
        print(json.dumps(summary, ensure_ascii=False, indent=2))

    else:
        # 默认显示状态
        status = engine.get_status()
        print(f"\n=== {status['engine_name']} v{status['version']} ===")
        print(f"监控状态: {'运行中' if status['monitoring'] else '未运行'}")
        print(f"最后同步时间: {status['last_sync_time'] or '从未同步'}")
        print(f"同步状态: {status['sync_status']}")
        print(f"跟踪文件数: {status['total_tracked_files']}")
        print(f"变更记录数: {status['total_changes']}")
        print(f"健康分数: {status.get('health_score', 0):.1f}%")
        print(f"\n使用 --help 查看更多选项")


if __name__ == "__main__":
    main()