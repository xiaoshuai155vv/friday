#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件监听与自动处理模块
实现文件夹监控与自动文件处理功能
"""

import os
import sys
import json
import time
import shutil
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable
import logging

# 添加项目路径以便导入其他模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 配置文件路径
WATCHER_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "runtime", "state", "file_watcher_config.json")
WATCHER_STATE_FILE = os.path.join(os.path.dirname(__file__), "..", "runtime", "state", "file_watcher_state.json")
WATCHER_HISTORY_FILE = os.path.join(os.path.dirname(__file__), "..", "runtime", "state", "file_watcher_history.json")

# 事件类型定义
EVENT_CREATED = "created"
EVENT_MODIFIED = "modified"
EVENT_DELETED = "deleted"

class FileWatcher:
    """文件监听器类"""

    def __init__(self, watch_folder: str, config_file: str = WATCHER_CONFIG_FILE):
        """
        初始化文件监听器

        Args:
            watch_folder (str): 要监听的文件夹路径
            config_file (str): 配置文件路径
        """
        self.watch_folder = os.path.abspath(watch_folder)
        self.config_file = config_file
        self.state_file = WATCHER_STATE_FILE
        self.history_file = WATCHER_HISTORY_FILE

        # 确保监听文件夹存在
        if not os.path.exists(self.watch_folder):
            raise FileNotFoundError(f"监听文件夹不存在: {self.watch_folder}")

        # 加载配置
        self.config = self._load_config()

        # 加载状态
        self.state = self._load_state()

        # 事件处理器
        self.event_handlers = {
            EVENT_CREATED: self._handle_created,
            EVENT_MODIFIED: self._handle_modified,
            EVENT_DELETED: self._handle_deleted
        }

        # 启动监控线程
        self.monitoring = False
        self.monitor_thread = None

    def _load_config(self) -> Dict:
        """加载配置文件"""
        default_config = {
            "rules": [
                {
                    "name": "默认规则",
                    "trigger_events": [EVENT_CREATED, EVENT_MODIFIED],
                    "conditions": {},
                    "actions": [
                        {
                            "type": "log",
                            "message": "文件 {file_path} 被 {event_type}"
                        }
                    ]
                }
            ],
            "polling_interval": 5,  # 轮询间隔（秒）
            "max_history_entries": 1000
        }

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                logger.warning(f"加载配置文件失败: {e}")

        return default_config

    def _save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")

    def _load_state(self) -> Dict:
        """加载监控状态"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载状态文件失败: {e}")
        return {"last_checked": 0, "file_states": {}}

    def _save_state(self):
        """保存监控状态"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存状态文件失败: {e}")

    def _load_history(self) -> List[Dict]:
        """加载历史记录"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载历史文件失败: {e}")
        return []

    def _save_history(self, history: List[Dict]):
        """保存历史记录"""
        try:
            # 限制历史记录数量
            if len(history) > self.config.get("max_history_entries", 1000):
                history = history[-self.config.get("max_history_entries", 1000):]

            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存历史文件失败: {e}")

    def _get_file_info(self, file_path: str) -> Dict:
        """获取文件信息"""
        try:
            stat = os.stat(file_path)
            return {
                "path": file_path,
                "name": os.path.basename(file_path),
                "size": stat.st_size,
                "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "is_directory": os.path.isdir(file_path),
                "extension": os.path.splitext(file_path)[1].lower() if not os.path.isdir(file_path) else ""
            }
        except Exception as e:
            logger.error(f"获取文件信息失败 {file_path}: {e}")
            return {}

    def _apply_rules(self, event_type: str, file_path: str, file_info: Dict):
        """应用规则处理事件"""
        logger.info(f"处理 {event_type} 事件: {file_path}")

        # 获取历史记录
        history = self._load_history()

        # 检查每个规则
        for rule in self.config.get("rules", []):
            # 检查触发事件是否匹配
            trigger_events = rule.get("trigger_events", [])
            if event_type not in trigger_events:
                continue

            # 检查条件
            conditions = rule.get("conditions", {})
            if not self._check_conditions(conditions, file_path, file_info):
                continue

            # 执行动作
            actions = rule.get("actions", [])
            for action in actions:
                self._execute_action(action, event_type, file_path, file_info)

            # 记录历史
            history_item = {
                "timestamp": datetime.now().isoformat(),
                "rule_name": rule.get("name", "Unnamed Rule"),
                "event_type": event_type,
                "file_path": file_path,
                "file_info": file_info,
                "action_result": "processed"
            }
            history.append(history_item)

        # 保存历史记录
        self._save_history(history)

    def _check_conditions(self, conditions: Dict, file_path: str, file_info: Dict) -> bool:
        """检查条件是否满足"""
        # 检查文件扩展名
        if "extensions" in conditions:
            extensions = conditions["extensions"]
            if file_info.get("extension") not in extensions:
                return False

        # 检查文件大小
        if "min_size" in conditions:
            min_size = conditions["min_size"]
            if file_info.get("size", 0) < min_size:
                return False

        if "max_size" in conditions:
            max_size = conditions["max_size"]
            if file_info.get("size", 0) > max_size:
                return False

        # 检查文件类型
        if "file_types" in conditions:
            file_types = conditions["file_types"]
            if file_info.get("is_directory") and "directory" not in file_types:
                return False
            if not file_info.get("is_directory") and "file" not in file_types:
                return False

        return True

    def _execute_action(self, action: Dict, event_type: str, file_path: str, file_info: Dict):
        """执行动作"""
        action_type = action.get("type")
        logger.info(f"执行动作: {action_type} - {file_path}")

        try:
            if action_type == "move":
                # 移动文件
                destination = action.get("destination")
                if destination:
                    dest_path = os.path.join(destination, file_info.get("name"))
                    os.makedirs(destination, exist_ok=True)
                    shutil.move(file_path, dest_path)
                    logger.info(f"文件已移动: {file_path} -> {dest_path}")

            elif action_type == "copy":
                # 复制文件
                destination = action.get("destination")
                if destination:
                    dest_path = os.path.join(destination, file_info.get("name"))
                    os.makedirs(destination, exist_ok=True)
                    shutil.copy2(file_path, dest_path)
                    logger.info(f"文件已复制: {file_path} -> {dest_path}")

            elif action_type == "rename":
                # 重命名文件
                new_name = action.get("new_name")
                if new_name:
                    new_path = os.path.join(os.path.dirname(file_path), new_name)
                    os.rename(file_path, new_path)
                    logger.info(f"文件已重命名: {file_path} -> {new_path}")

            elif action_type == "log":
                # 记录日志
                message_template = action.get("message", "")
                message = message_template.format(
                    file_path=file_path,
                    event_type=event_type,
                    file_name=file_info.get("name", ""),
                    file_size=file_info.get("size", 0)
                )
                logger.info(message)

            elif action_type == "classify":
                # 智能分类（简单示例）
                extension = file_info.get("extension", "")
                if extension:
                    # 根据扩展名分类到不同的文件夹
                    classification_map = {
                        ".jpg": "images",
                        ".jpeg": "images",
                        ".png": "images",
                        ".gif": "images",
                        ".mp3": "audio",
                        ".wav": "audio",
                        ".mp4": "videos",
                        ".avi": "videos",
                        ".pdf": "documents",
                        ".doc": "documents",
                        ".docx": "documents",
                        ".xls": "documents",
                        ".xlsx": "documents"
                    }

                    category = classification_map.get(extension, "others")
                    destination = os.path.join(self.watch_folder, category)
                    dest_path = os.path.join(destination, file_info.get("name"))
                    os.makedirs(destination, exist_ok=True)
                    shutil.move(file_path, dest_path)
                    logger.info(f"文件已分类: {file_path} -> {dest_path}")

        except Exception as e:
            logger.error(f"执行动作失败 {action_type}: {e}")

    def _handle_created(self, file_path: str, file_info: Dict):
        """处理文件创建事件"""
        self._apply_rules(EVENT_CREATED, file_path, file_info)

    def _handle_modified(self, file_path: str, file_info: Dict):
        """处理文件修改事件"""
        self._apply_rules(EVENT_MODIFIED, file_path, file_info)

    def _handle_deleted(self, file_path: str, file_info: Dict):
        """处理文件删除事件"""
        self._apply_rules(EVENT_DELETED, file_path, file_info)

    def _monitor_once(self):
        """单次监控检查"""
        current_time = time.time()

        # 获取当前文件列表
        current_files = {}
        for root, dirs, files in os.walk(self.watch_folder):
            for file in files:
                file_path = os.path.join(root, file)
                current_files[file_path] = self._get_file_info(file_path)

        # 检查文件变化
        for file_path, file_info in current_files.items():
            if file_path not in self.state["file_states"]:
                # 新文件
                self.event_handlers[EVENT_CREATED](file_path, file_info)
                self.state["file_states"][file_path] = file_info
            else:
                # 检查是否被修改
                old_info = self.state["file_states"][file_path]
                if file_info.get("modified_time") != old_info.get("modified_time"):
                    self.event_handlers[EVENT_MODIFIED](file_path, file_info)
                    self.state["file_states"][file_path] = file_info

        # 检查删除的文件
        for file_path in list(self.state["file_states"].keys()):
            if file_path not in current_files:
                file_info = self.state["file_states"][file_path]
                self.event_handlers[EVENT_DELETED](file_path, file_info)
                del self.state["file_states"][file_path]

        # 保存状态
        self.state["last_checked"] = current_time
        self._save_state()

    def start_monitoring(self):
        """开始监控"""
        if self.monitoring:
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info(f"开始监控文件夹: {self.watch_folder}")

    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("停止文件监控")

    def _monitor_loop(self):
        """监控循环"""
        while self.monitoring:
            try:
                self._monitor_once()
                time.sleep(self.config.get("polling_interval", 5))
            except Exception as e:
                logger.error(f"监控循环出错: {e}")
                time.sleep(self.config.get("polling_interval", 5))

    def add_rule(self, rule: Dict):
        """添加处理规则"""
        if "rules" not in self.config:
            self.config["rules"] = []
        self.config["rules"].append(rule)
        self._save_config()
        logger.info(f"添加规则: {rule.get('name', 'Unnamed Rule')}")

    def list_rules(self) -> List[Dict]:
        """列出所有规则"""
        return self.config.get("rules", [])

    def remove_rule(self, rule_name: str):
        """移除规则"""
        rules = self.config.get("rules", [])
        self.config["rules"] = [r for r in rules if r.get("name") != rule_name]
        self._save_config()
        logger.info(f"移除规则: {rule_name}")

def main():
    """
    主函数 - 用于命令行测试
    """
    if len(sys.argv) < 2:
        print("用法: python file_watcher.py <命令> [参数...]")
        print("命令:")
        print("  start <文件夹路径>           - 开始监控文件夹")
        print("  stop                         - 停止监控")
        print("  add-rule <规则JSON>          - 添加处理规则")
        print("  list-rules                   - 列出所有规则")
        print("  remove-rule <规则名称>       - 移除规则")
        print("  test <文件路径>              - 测试单个文件处理")
        return

    command = sys.argv[1]

    if command == "start":
        if len(sys.argv) < 3:
            print("请提供要监控的文件夹路径")
            return
        folder_path = sys.argv[2]
        try:
            watcher = FileWatcher(folder_path)
            watcher.start_monitoring()
            print(f"正在监控文件夹: {folder_path}")
            print("按 Ctrl+C 停止监控")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                watcher.stop_monitoring()
                print("监控已停止")
        except Exception as e:
            print(f"启动监控失败: {e}")

    elif command == "stop":
        # 停止监控的实现比较复杂，通常通过外部信号控制
        print("停止监控需要通过进程控制实现")

    elif command == "add-rule":
        if len(sys.argv) < 3:
            print("请提供规则JSON")
            return
        try:
            rule_json = sys.argv[2]
            rule = json.loads(rule_json)
            # 这里需要指定监控文件夹路径
            watcher = FileWatcher(".")  # 临时创建
            watcher.add_rule(rule)
            print("规则已添加")
        except Exception as e:
            print(f"添加规则失败: {e}")

    elif command == "list-rules":
        watcher = FileWatcher(".")
        rules = watcher.list_rules()
        print(json.dumps(rules, ensure_ascii=False, indent=2))

    elif command == "remove-rule":
        if len(sys.argv) < 3:
            print("请提供规则名称")
            return
        rule_name = sys.argv[2]
        watcher = FileWatcher(".")
        watcher.remove_rule(rule_name)
        print(f"规则 '{rule_name}' 已移除")

    elif command == "test":
        if len(sys.argv) < 3:
            print("请提供文件路径")
            return
        file_path = sys.argv[2]
        try:
            # 创建临时监听器来测试
            watcher = FileWatcher(".")
            file_info = watcher._get_file_info(file_path)
            print(f"文件信息: {json.dumps(file_info, ensure_ascii=False, indent=2)}")
        except Exception as e:
            print(f"测试失败: {e}")

if __name__ == "__main__":
    main()