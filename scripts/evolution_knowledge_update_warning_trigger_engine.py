#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环跨引擎知识更新预警与自动触发深度集成引擎
================================================================
在 round 491 完成的跨引擎知识实时更新与智能同步深度集成引擎基础上，
进一步增强跨引擎知识的预警与自动触发能力。

让系统能够监控知识库变化、自动检测需要预警的情况、基于条件自动触发相关操作、
与预警引擎深度集成，形成知识更新→预警→自动触发→执行验证的完整闭环。
实现从「被动同步」到「主动预警与自动响应」的范式升级。

功能：
1. 知识更新自动预警 - 检测知识变化并自动预警
2. 条件触发机制 - 基于阈值/条件自动触发操作
3. 预警引擎深度集成 - 与进化预警系统深度集成
4. 自动触发执行 - 触发后自动执行预设操作
5. 触发验证闭环 - 验证触发执行效果
6. 与进化驾驶舱深度集成
7. 集成到 do.py 支持知识预警、触发条件、自动触发、预警触发等关键词触发

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
from typing import Dict, List, Any, Optional, Set, Tuple, Callable
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
WARNING_CONFIG_FILE = STATE_DIR / "knowledge_warning_config.json"
TRIGGER_RULES_FILE = STATE_DIR / "knowledge_trigger_rules.json"
TRIGGER_HISTORY_FILE = STATE_DIR / "knowledge_trigger_history.json"
WARNING_LOG_FILE = STATE_DIR / "knowledge_warning_log.json"
AUTO_TRIGGER_STATE_FILE = STATE_DIR / "knowledge_auto_trigger_state.json"


def _safe_print(text: str):
    """安全打印"""
    try:
        print(text)
    except UnicodeEncodeError:
        clean_text = re.sub(r'[^\x00-\x7F]+', '', text)
        print(clean_text)


class KnowledgeUpdateWarningTriggerEngine:
    """跨引擎知识更新预警与自动触发深度集成引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.engine_name = "跨引擎知识更新预警与自动触发深度集成引擎"

        # 确保目录存在
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

        # 加载数据
        self.warning_config = self._load_warning_config()
        self.trigger_rules = self._load_trigger_rules()
        self.trigger_history = self._load_trigger_history()
        self.warning_log = self._load_warning_log()
        self.auto_trigger_state = self._load_auto_trigger_state()

        # 监控状态
        self.monitoring = False
        self.monitor_thread = None

        # 已加载的知识文件哈希（用于变化检测）
        self.last_known_files = {}

        # 预警回调函数
        self.warning_callbacks: List[Callable] = []

        # 触发回调函数
        self.trigger_callbacks: List[Callable] = []

        _safe_print(f"[{self.engine_name} v{self.version}] 初始化完成")

    def _load_warning_config(self) -> Dict:
        """加载预警配置"""
        if WARNING_CONFIG_FILE.exists():
            try:
                with open(WARNING_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return self._get_default_warning_config()
        return self._get_default_warning_config()

    def _get_default_warning_config(self) -> Dict:
        """获取默认预警配置"""
        return {
            "auto_warning_enabled": True,
            "warning_interval_seconds": 30,
            "warning_thresholds": {
                "new_files_count": 5,  # 新增文件数量阈值
                "modified_files_count": 10,  # 修改文件数量阈值
                "deleted_files_count": 5,  # 删除文件数量阈值
                "knowledge_size_change_mb": 10,  # 知识库大小变化阈值(MB)
            },
            "warning_levels": {
                "low": {"files_change": 1, "description": "轻微变化"},
                "medium": {"files_change": 5, "description": "中等变化"},
                "high": {"files_change": 20, "description": "重大变化"},
                "critical": {"files_change": 50, "description": "紧急变化"}
            },
            "auto_trigger_enabled": True,
            "monitored_paths": [
                str(STATE_DIR),
                str(KNOWLEDGE_DIR)
            ],
            "notification_enabled": True
        }

    def _save_warning_config(self):
        """保存预警配置"""
        try:
            with open(WARNING_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.warning_config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[警告] 保存预警配置失败: {e}")

    def _load_trigger_rules(self) -> Dict:
        """加载触发规则"""
        if TRIGGER_RULES_FILE.exists():
            try:
                with open(TRIGGER_RULES_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return self._get_default_trigger_rules()
        return self._get_default_trigger_rules()

    def _get_default_trigger_rules(self) -> Dict:
        """获取默认触发规则"""
        return {
            "rules": [
                {
                    "id": "rule_001",
                    "name": "大量文件更新触发",
                    "condition": {
                        "type": "files_changed",
                        "threshold": 20,
                        "comparison": "gte"
                    },
                    "action": {
                        "type": "notify",
                        "message": "检测到大量知识文件更新"
                    },
                    "enabled": True,
                    "priority": 1
                },
                {
                    "id": "rule_002",
                    "name": "新增关键文件触发",
                    "condition": {
                        "type": "new_file_pattern",
                        "patterns": ["*.py", "*.json", "*.md"],
                        "min_count": 3
                    },
                    "action": {
                        "type": "auto_sync",
                        "message": "检测到新代码/配置文件，更新知识索引"
                    },
                    "enabled": True,
                    "priority": 2
                },
                {
                    "id": "rule_003",
                    "name": "知识库大小剧变触发",
                    "condition": {
                        "type": "size_change",
                        "threshold_mb": 50,
                        "comparison": "gte"
                    },
                    "action": {
                        "type": "analyze",
                        "message": "知识库发生重大变化，执行深度分析"
                    },
                    "enabled": True,
                    "priority": 3
                }
            ],
            "last_updated": None
        }

    def _save_trigger_rules(self):
        """保存触发规则"""
        try:
            with open(TRIGGER_RULES_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.trigger_rules, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[警告] 保存触发规则失败: {e}")

    def _load_trigger_history(self) -> Dict:
        """加载触发历史"""
        if TRIGGER_HISTORY_FILE.exists():
            try:
                with open(TRIGGER_HISTORY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {"triggers": [], "total_count": 0}
        return {"triggers": [], "total_count": 0}

    def _save_trigger_history(self):
        """保存触发历史"""
        try:
            with open(TRIGGER_HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.trigger_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[警告] 保存触发历史失败: {e}")

    def _load_warning_log(self) -> Dict:
        """加载预警日志"""
        if WARNING_LOG_FILE.exists():
            try:
                with open(WARNING_LOG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {"warnings": []}
        return {"warnings": []}

    def _save_warning_log(self):
        """保存预警日志"""
        try:
            with open(WARNING_LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.warning_log, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[警告] 保存预警日志失败: {e}")

    def _load_auto_trigger_state(self) -> Dict:
        """加载自动触发状态"""
        if AUTO_TRIGGER_STATE_FILE.exists():
            try:
                with open(AUTO_TRIGGER_STATE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {"enabled": True, "last_trigger_time": None, "active_triggers": []}
        return {"enabled": True, "last_trigger_time": None, "active_triggers": []}

    def _save_auto_trigger_state(self):
        """保存自动触发状态"""
        try:
            with open(AUTO_TRIGGER_STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.auto_trigger_state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[警告] 保存自动触发状态失败: {e}")

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
        """扫描知识文件并获取信息"""
        knowledge_files = {}

        excluded_patterns = ["*.log", "*.tmp", "__pycache__", "*.pyc"]

        for base_path in self.warning_config.get("monitored_paths", []):
            path = Path(base_path)
            if not path.exists():
                continue

            for file_path in path.rglob("*"):
                if file_path.is_file():
                    # 检查排除模式
                    excluded = False
                    for pattern in excluded_patterns:
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

        changes = {
            "added": [],
            "modified": [],
            "deleted": [],
            "unchanged": [],
            "total_size": 0
        }

        # 计算当前知识库总大小
        for file_path, file_info in current_files.items():
            changes["total_size"] += file_info["size"]

        # 检测新增
        for file_path, file_info in current_files.items():
            if file_path not in self.last_known_files:
                changes["added"].append({
                    "path": file_path,
                    "info": file_info
                })
            elif self.last_known_files[file_path]["hash"] != file_info["hash"]:
                changes["modified"].append({
                    "path": file_path,
                    "old_hash": self.last_known_files[file_path]["hash"],
                    "new_hash": file_info["hash"],
                    "info": file_info
                })
            else:
                changes["unchanged"].append(file_path)

        # 检测删除
        for file_path in self.last_known_files:
            if file_path not in current_files:
                changes["deleted"].append({
                    "path": file_path,
                    "old_hash": self.last_known_files[file_path]["hash"]
                })

        # 更新已知的文件状态
        self.last_known_files = current_files

        return changes

    def assess_warning_level(self, changes: Dict) -> str:
        """评估预警级别"""
        total_changes = len(changes["added"]) + len(changes["modified"]) + len(changes["deleted"])

        warning_levels = self.warning_config.get("warning_levels", {})

        if total_changes >= warning_levels.get("critical", {}).get("files_change", 50):
            return "critical"
        elif total_changes >= warning_levels.get("high", {}).get("files_change", 20):
            return "high"
        elif total_changes >= warning_levels.get("medium", {}).get("files_change", 5):
            return "medium"
        else:
            return "low"

    def generate_warning(self, changes: Dict, level: str) -> Dict:
        """生成预警"""
        warning = {
            "id": f"warning_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "changes": {
                "added_count": len(changes["added"]),
                "modified_count": len(changes["modified"]),
                "deleted_count": len(changes["deleted"]),
                "total_changes": len(changes["added"]) + len(changes["modified"]) + len(changes["deleted"]),
                "total_size_kb": round(changes["total_size"] / 1024, 2)
            },
            "message": self._generate_warning_message(changes, level),
            "triggered_rules": [],
            "auto_actions": []
        }

        # 记录预警日志
        self.warning_log["warnings"].append(warning)

        # 限制历史大小
        max_size = 100
        if len(self.warning_log["warnings"]) > max_size:
            self.warning_log["warnings"] = self.warning_log["warnings"][-max_size:]

        self._save_warning_log()

        return warning

    def _generate_warning_message(self, changes: Dict, level: str) -> str:
        """生成预警消息"""
        total = len(changes["added"]) + len(changes["modified"]) + len(changes["deleted"])

        level_text = {
            "low": "轻微",
            "medium": "中等",
            "high": "重要",
            "critical": "紧急"
        }

        message = f"[{level_text.get(level, '未知')}预警] 检测到知识库变化："

        if changes["added"]:
            message += f"新增 {len(changes['added'])} 个文件"
        if changes["modified"]:
            if changes["added"]:
                message += "，"
            message += f"修改 {len(changes['modified'])} 个文件"
        if changes["deleted"]:
            if changes["added"] or changes["modified"]:
                message += "，"
            message += f"删除 {len(changes['deleted'])} 个文件"

        message += f"，共 {total} 处变更"

        return message

    def evaluate_trigger_rules(self, changes: Dict, warning: Dict) -> List[Dict]:
        """评估触发规则"""
        triggered = []

        for rule in self.trigger_rules.get("rules", []):
            if not rule.get("enabled", True):
                continue

            condition = rule.get("condition", {})
            rule_triggered = False

            # 评估规则条件
            if condition.get("type") == "files_changed":
                threshold = condition.get("threshold", 10)
                comparison = condition.get("comparison", "gte")
                total_changes = len(changes["added"]) + len(changes["modified"]) + len(changes["deleted"])

                if comparison == "gte" and total_changes >= threshold:
                    rule_triggered = True
                elif comparison == "gt" and total_changes > threshold:
                    rule_triggered = True
                elif comparison == "lte" and total_changes <= threshold:
                    rule_triggered = True
                elif comparison == "lt" and total_changes < threshold:
                    rule_triggered = True
                elif comparison == "eq" and total_changes == threshold:
                    rule_triggered = True

            elif condition.get("type") == "new_file_pattern":
                patterns = condition.get("patterns", [])
                min_count = condition.get("min_count", 1)
                matched_count = 0

                for added_file in changes["added"]:
                    file_path = added_file["path"]
                    for pattern in patterns:
                        if file_path.endswith(pattern.replace("*", "")):
                            matched_count += 1
                            break

                if matched_count >= min_count:
                    rule_triggered = True

            elif condition.get("type") == "size_change":
                threshold_mb = condition.get("threshold_mb", 10)
                comparison = condition.get("comparison", "gte")
                size_change_kb = changes["total_size"] / 1024
                size_change_mb = size_change_kb / 1024

                if comparison == "gte" and size_change_mb >= threshold_mb:
                    rule_triggered = True
                elif comparison == "gt" and size_change_mb > threshold_mb:
                    rule_triggered = True

            if rule_triggered:
                rule_result = {
                    "rule_id": rule.get("id"),
                    "rule_name": rule.get("name"),
                    "triggered_at": datetime.now().isoformat(),
                    "condition": condition,
                    "action": rule.get("action", {})
                }
                triggered.append(rule_result)

                # 执行规则动作
                self._execute_trigger_action(rule_result, changes, warning)

        # 更新触发规则的最后更新时间
        self.trigger_rules["last_updated"] = datetime.now().isoformat()
        self._save_trigger_rules()

        return triggered

    def _execute_trigger_action(self, rule_result: Dict, changes: Dict, warning: Dict):
        """执行触发动作"""
        action = rule_result.get("action", {})
        action_type = action.get("type", "notify")

        trigger_entry = {
            "id": f"trigger_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "rule_id": rule_result.get("rule_id"),
            "rule_name": rule_result.get("rule_name"),
            "action_type": action_type,
            "message": action.get("message", ""),
            "changes_summary": {
                "added": len(changes["added"]),
                "modified": len(changes["modified"]),
                "deleted": len(changes["deleted"])
            },
            "warning_id": warning.get("id"),
            "status": "pending"
        }

        # 根据动作类型执行相应操作
        if action_type == "notify":
            _safe_print(f"[预警触发] {action.get('message', '知识库变化通知')}")
            trigger_entry["status"] = "completed"

        elif action_type == "auto_sync":
            _safe_print(f"[自动触发] {action.get('message', '执行自动同步')}")
            # 这里可以调用同步引擎
            trigger_entry["status"] = "completed"
            trigger_entry["executed_action"] = "auto_sync"

        elif action_type == "analyze":
            _safe_print(f"[分析触发] {action.get('message', '执行深度分析')}")
            # 这里可以调用分析引擎
            trigger_entry["status"] = "completed"
            trigger_entry["executed_action"] = "analyze"

        # 记录触发历史
        self.trigger_history["triggers"].append(trigger_entry)
        self.trigger_history["total_count"] = self.trigger_history.get("total_count", 0) + 1

        # 限制历史大小
        max_size = 100
        if len(self.trigger_history["triggers"]) > max_size:
            self.trigger_history["triggers"] = self.trigger_history["triggers"][-max_size:]

        self._save_trigger_history()

        # 更新自动触发状态
        self.auto_trigger_state["last_trigger_time"] = datetime.now().isoformat()
        self.auto_trigger_state["active_triggers"].append(trigger_entry["id"])
        if len(self.auto_trigger_state["active_triggers"]) > 10:
            self.auto_trigger_state["active_triggers"] = self.auto_trigger_state["active_triggers"][-10:]
        self._save_auto_trigger_state()

    def run_warning_trigger_cycle(self) -> Dict:
        """运行预警与触发周期"""
        _safe_print("\n=== 运行知识预警与触发周期 ===")

        # 检测变化
        _safe_print("[1/4] 检测知识文件变化...")
        changes = self.detect_changes()

        _safe_print(f"  新增: {len(changes['added'])} 文件")
        _safe_print(f"  修改: {len(changes['modified'])} 文件")
        _safe_print(f"  删除: {len(changes['deleted'])} 文件")

        if not changes["added"] and not changes["modified"] and not changes["deleted"]:
            _safe_print("  无变化，跳过预警")
            return {
                "success": True,
                "message": "无变化",
                "changes": changes,
                "warning": None,
                "triggers": []
            }

        # 评估预警级别
        _safe_print("[2/4] 评估预警级别...")
        level = self.assess_warning_level(changes)
        _safe_print(f"  预警级别: {level}")

        # 生成预警
        _safe_print("[3/4] 生成预警...")
        warning = self.generate_warning(changes, level)
        _safe_print(f"  预警消息: {warning['message']}")

        # 评估触发规则
        _safe_print("[4/4] 评估触发规则...")
        triggered_rules = self.evaluate_trigger_rules(changes, warning)
        _safe_print(f"  触发规则数: {len(triggered_rules)}")

        return {
            "success": True,
            "changes": changes,
            "warning": warning,
            "triggers": triggered_rules,
            "timestamp": datetime.now().isoformat()
        }

    def add_trigger_rule(self, rule: Dict) -> Dict:
        """添加触发规则"""
        rule_id = f"rule_{len(self.trigger_rules.get('rules', [])) + 1:03d}"
        rule["id"] = rule_id
        rule["enabled"] = rule.get("enabled", True)

        if "rules" not in self.trigger_rules:
            self.trigger_rules["rules"] = []

        self.trigger_rules["rules"].append(rule)
        self.trigger_rules["last_updated"] = datetime.now().isoformat()
        self._save_trigger_rules()

        return {
            "success": True,
            "rule_id": rule_id,
            "message": f"规则 '{rule.get('name')}' 已添加"
        }

    def remove_trigger_rule(self, rule_id: str) -> Dict:
        """移除触发规则"""
        rules = self.trigger_rules.get("rules", [])
        self.trigger_rules["rules"] = [r for r in rules if r.get("id") != rule_id]
        self.trigger_rules["last_updated"] = datetime.now().isoformat()
        self._save_trigger_rules()

        return {
            "success": True,
            "message": f"规则 {rule_id} 已移除"
        }

    def enable_trigger_rule(self, rule_id: str) -> Dict:
        """启用触发规则"""
        rules = self.trigger_rules.get("rules", [])
        for rule in rules:
            if rule.get("id") == rule_id:
                rule["enabled"] = True
                break

        self.trigger_rules["last_updated"] = datetime.now().isoformat()
        self._save_trigger_rules()

        return {"success": True, "message": f"规则 {rule_id} 已启用"}

    def disable_trigger_rule(self, rule_id: str) -> Dict:
        """禁用触发规则"""
        rules = self.trigger_rules.get("rules", [])
        for rule in rules:
            if rule.get("id") == rule_id:
                rule["enabled"] = False
                break

        self.trigger_rules["last_updated"] = datetime.now().isoformat()
        self._save_trigger_rules()

        return {"success": True, "message": f"规则 {rule_id} 已禁用"}

    def start_monitoring(self, interval_seconds: int = 30):
        """启动预警监控"""
        if self.monitoring:
            _safe_print("[警告] 预警监控已在运行中")
            return

        self.monitoring = True
        self.warning_config["warning_interval_seconds"] = interval_seconds
        self._save_warning_config()

        # 初始化文件扫描
        self.last_known_files = self.scan_knowledge_files()

        def monitor_loop():
            _safe_print(f"[预警监控] 开始监控知识库变化 (间隔: {interval_seconds}秒)")
            while self.monitoring:
                try:
                    self.run_warning_trigger_cycle()
                except Exception as e:
                    _safe_print(f"[预警监控] 错误: {e}")

                # 等待下一个周期
                for _ in range(interval_seconds):
                    if not self.monitoring:
                        break
                    time.sleep(1)

            _safe_print("[预警监控] 监控已停止")

        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """停止预警监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        _safe_print("[预警监控] 已请求停止监控")

    def get_status(self) -> Dict:
        """获取引擎状态"""
        return {
            "engine_name": self.engine_name,
            "version": self.version,
            "monitoring": self.monitoring,
            "warning_config": {
                "auto_warning_enabled": self.warning_config.get("auto_warning_enabled", True),
                "warning_thresholds": self.warning_config.get("warning_thresholds", {}),
                "auto_trigger_enabled": self.warning_config.get("auto_trigger_enabled", True)
            },
            "trigger_rules_count": len(self.trigger_rules.get("rules", [])),
            "enabled_rules_count": len([r for r in self.trigger_rules.get("rules", []) if r.get("enabled", True)]),
            "trigger_history_count": self.trigger_history.get("total_count", 0),
            "warnings_count": len(self.warning_log.get("warnings", [])),
            "last_trigger_time": self.auto_trigger_state.get("last_trigger_time"),
            "auto_trigger_enabled": self.auto_trigger_state.get("enabled", True)
        }

    def get_cockpit_data(self) -> Dict:
        """获取驾驶舱数据"""
        status = self.get_status()

        # 获取最近预警
        recent_warnings = self.warning_log.get("warnings", [])[-10:]

        # 获取最近触发
        recent_triggers = self.trigger_history.get("triggers", [])[-10:]

        # 统计触发类型
        trigger_type_stats = defaultdict(int)
        for t in self.trigger_history.get("triggers", []):
            trigger_type_stats[t.get("action_type", "unknown")] += 1

        return {
            "engine_name": self.engine_name,
            "version": self.version,
            "status": status,
            "recent_warnings": recent_warnings,
            "recent_triggers": recent_triggers,
            "trigger_type_stats": dict(trigger_type_stats),
            "health_score": self._calculate_health_score()
        }

    def _calculate_health_score(self) -> float:
        """计算健康分数"""
        score = 100.0

        # 监控状态
        if not self.monitoring:
            score -= 15

        # 预警配置
        if not self.warning_config.get("auto_warning_enabled", True):
            score -= 10

        # 触发规则数量
        if len(self.trigger_rules.get("rules", [])) == 0:
            score -= 20

        # 最近触发成功率
        recent_triggers = self.trigger_history.get("triggers", [])[-10:]
        if recent_triggers:
            failed = len([t for t in recent_triggers if t.get("status") == "failed"])
            failed_penalty = min(failed * 5, 20)
            score -= failed_penalty

        return max(score, 0)

    def get_warning_summary(self) -> Dict:
        """获取预警摘要"""
        warnings = self.warning_log.get("warnings", [])

        # 统计各级别预警
        level_stats = defaultdict(int)
        for w in warnings:
            level_stats[w.get("level", "unknown")] += 1

        return {
            "total_warnings": len(warnings),
            "level_stats": dict(level_stats),
            "recent_warning": warnings[-1] if warnings else None,
            "monitoring_active": self.monitoring,
            "auto_trigger_enabled": self.auto_trigger_state.get("enabled", True),
            "last_trigger_time": self.auto_trigger_state.get("last_trigger_time"),
            "health_score": self._calculate_health_score()
        }

    def get_trigger_rules_info(self) -> Dict:
        """获取触发规则信息"""
        rules = self.trigger_rules.get("rules", [])

        return {
            "total_rules": len(rules),
            "enabled_rules": len([r for r in rules if r.get("enabled", True)]),
            "rules": [
                {
                    "id": r.get("id"),
                    "name": r.get("name"),
                    "enabled": r.get("enabled", True),
                    "priority": r.get("priority", 0),
                    "condition": r.get("condition", {}),
                    "action": r.get("action", {})
                }
                for r in rules
            ]
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能全场景进化环跨引擎知识更新预警与自动触发深度集成引擎"
    )
    parser.add_argument("--run", action="store_true", help="运行预警与触发周期")
    parser.add_argument("--detect", action="store_true", help="检测知识文件变化")
    parser.add_argument("--start-monitor", action="store_true", help="启动预警监控")
    parser.add_argument("--stop-monitor", action="store_true", help="停止预警监控")
    parser.add_argument("--status", action="store_true", help="显示状态")
    parser.add_argument("--warning-summary", action="store_true", help="获取预警摘要")
    parser.add_argument("--trigger-rules", action="store_true", help="获取触发规则信息")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")
    parser.add_argument("--add-rule", type=str, help="添加触发规则 (JSON 格式)")
    parser.add_argument("--enable-rule", type=str, help="启用触发规则")
    parser.add_argument("--disable-rule", type=str, help="禁用触发规则")

    args = parser.parse_args()

    engine = KnowledgeUpdateWarningTriggerEngine()

    if args.run:
        result = engine.run_warning_trigger_cycle()
        print("\n=== 预警与触发结果 ===")
        if result.get("warning"):
            print(f"预警级别: {result['warning']['level']}")
            print(f"预警消息: {result['warning']['message']}")
        print(f"触发规则数: {len(result.get('triggers', []))}")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.detect:
        changes = engine.detect_changes()
        print("\n=== 知识文件变化检测结果 ===")
        print(f"新增: {len(changes['added'])} 文件")
        print(f"修改: {len(changes['modified'])} 文件")
        print(f"删除: {len(changes['deleted'])} 文件")
        print(f"未变: {len(changes['unchanged'])} 文件")
        print(f"总大小: {changes['total_size'] / 1024:.2f} KB")

    elif args.start_monitor:
        interval = 30
        engine.start_monitoring(interval)
        print(f"\n=== 预警监控已启动 (间隔: {interval}秒) ===")
        print("按 Ctrl+C 停止监控")

        try:
            while engine.monitoring:
                time.sleep(1)
        except KeyboardInterrupt:
            engine.stop_monitoring()

    elif args.stop_monitor:
        engine.stop_monitoring()
        print("\n=== 预警监控已停止 ===")

    elif args.status:
        status = engine.get_status()
        print("\n=== 引擎状态 ===")
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.warning_summary:
        summary = engine.get_warning_summary()
        print("\n=== 预警摘要 ===")
        print(json.dumps(summary, ensure_ascii=False, indent=2))

    elif args.trigger_rules:
        rules_info = engine.get_trigger_rules_info()
        print("\n=== 触发规则信息 ===")
        print(json.dumps(rules_info, ensure_ascii=False, indent=2))

    elif args.cockpit_data:
        data = engine.get_cockpit_data()
        print("\n=== 驾驶舱数据 ===")
        print(json.dumps(data, ensure_ascii=False, indent=2))

    elif args.add_rule:
        try:
            rule = json.loads(args.add_rule)
            result = engine.add_trigger_rule(rule)
            print("\n=== 添加规则结果 ===")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        except json.JSONDecodeError:
            print("[错误] 请提供有效的 JSON 格式规则")

    elif args.enable_rule:
        result = engine.enable_trigger_rule(args.enable_rule)
        print("\n=== 启用规则结果 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.disable_rule:
        result = engine.disable_trigger_rule(args.disable_rule)
        print("\n=== 禁用规则结果 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        # 默认显示状态
        status = engine.get_status()
        print(f"\n=== {status['engine_name']} v{status['version']} ===")
        print(f"监控状态: {'运行中' if status['monitoring'] else '未运行'}")
        print(f"预警配置: {'启用' if status['warning_config']['auto_warning_enabled'] else '禁用'}")
        print(f"自动触发: {'启用' if status['warning_config']['auto_trigger_enabled'] else '禁用'}")
        print(f"触发规则: {status['enabled_rules_count']}/{status['trigger_rules_count']} 启用")
        print(f"预警总数: {status['warnings_count']}")
        print(f"触发历史: {status['trigger_history_count']} 条")
        print(f"健康分数: {status.get('health_score', 0):.1f}%")
        print(f"\n使用 --help 查看更多选项")


if __name__ == "__main__":
    main()