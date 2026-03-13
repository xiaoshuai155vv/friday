#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能任务偏好记忆引擎
记录用户对特定任务类型的偏好设置，每次执行同类任务时自动应用这些偏好

功能：
1. 偏好记录 - 记录用户对特定任务类型的偏好设置
2. 偏好学习 - 从用户执行历史中自动提取偏好
3. 偏好应用 - 执行任务时自动加载和应用偏好
4. 偏好查询和编辑 - 支持查看、添加、修改、删除偏好

工作原理：
- 用户可以主动设置任务偏好（如"用iHaier时先打开办公平台"）
- 系统可以从执行历史中自动学习偏好（多次重复某操作后记录）
- 执行任务时自动加载偏好配置，应用于任务执行
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

# 确保 scripts 目录在路径中
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..'))
STATE_DIR = os.path.join(PROJECT_DIR, 'runtime', 'state')


class TaskPreferenceEngine:
    """智能任务偏好记忆引擎"""

    def __init__(self):
        self.preferences_file = os.path.join(STATE_DIR, 'task_preferences.json')
        self.history_file = os.path.join(STATE_DIR, 'task_preference_history.json')
        self.preferences = self._load_preferences()
        self.auto_learn_enabled = True

    def _load_preferences(self) -> Dict[str, Any]:
        """加载任务偏好设置"""
        # 确保目录存在
        os.makedirs(os.path.dirname(self.preferences_file), exist_ok=True)
        if os.path.exists(self.preferences_file):
            try:
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[TaskPreference] 加载偏好失败: {e}")
        return {
            "preferences": {},
            "auto_learn_patterns": [],
            "last_updated": None
        }

    def _save_preferences(self):
        """保存任务偏好设置"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.preferences_file), exist_ok=True)
            self.preferences["last_updated"] = datetime.now().isoformat()
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[TaskPreference] 保存偏好失败: {e}")

    def _load_history(self) -> List[Dict[str, Any]]:
        """加载偏好历史记录"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('history', [])
            except Exception as e:
                print(f"[TaskPreference] 加载历史失败: {e}")
        return []

    def _save_history(self, history: List[Dict[str, Any]]):
        """保存偏好历史记录"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            # 只保留最近 100 条
            history = history[-100:]
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump({"history": history}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[TaskPreference] 保存历史失败: {e}")

    def set_preference(self, task_type: str, preference_key: str,
                      preference_value: Any, auto_apply: bool = True) -> Dict[str, Any]:
        """设置任务偏好

        Args:
            task_type: 任务类型（如 "ihaier", "document", "music", "browser" 等）
            preference_key: 偏好键（如 "default_window_title", "preferred_app", "default_params" 等）
            preference_value: 偏好值
            auto_apply: 是否自动应用到执行

        Returns:
            设置结果
        """
        result = {
            "success": False,
            "message": ""
        }

        try:
            if task_type not in self.preferences["preferences"]:
                self.preferences["preferences"][task_type] = {}

            # 记录旧值用于历史
            old_value = self.preferences["preferences"].get(task_type, {}).get(preference_key)

            # 设置新值
            self.preferences["preferences"][task_type][preference_key] = {
                "value": preference_value,
                "auto_apply": auto_apply,
                "created_at": datetime.now().isoformat() if old_value is None else old_value.get("created_at"),
                "updated_at": datetime.now().isoformat()
            }

            self._save_preferences()

            # 记录到历史
            self._add_to_history("set", task_type, preference_key, old_value, preference_value)

            result["success"] = True
            result["message"] = f"已设置任务 [{task_type}] 的偏好 [{preference_key}] = {preference_value}"
            print(f"[TaskPreference] {result['message']}")

        except Exception as e:
            result["message"] = f"设置偏好失败: {str(e)}"
            print(f"[TaskPreference] 错误: {e}")

        return result

    def get_preferences(self, task_type: Optional[str] = None) -> Dict[str, Any]:
        """获取任务偏好

        Args:
            task_type: 任务类型，为 None 时返回所有偏好

        Returns:
            偏好字典
        """
        if task_type:
            return self.preferences["preferences"].get(task_type, {})
        return self.preferences.get("preferences", {})

    def get_preference(self, task_type: str, preference_key: str) -> Optional[Any]:
        """获取特定偏好值

        Args:
            task_type: 任务类型
            preference_key: 偏好键

        Returns:
            偏好值，不存在返回 None
        """
        task_prefs = self.preferences["preferences"].get(task_type, {})
        if preference_key in task_prefs:
            return task_prefs[preference_key].get("value")
        return None

    def get_auto_apply_preferences(self, task_type: str) -> Dict[str, Any]:
        """获取需要自动应用的偏好

        Args:
            task_type: 任务类型

        Returns:
            需要自动应用的偏好字典
        """
        auto_apply_prefs = {}
        task_prefs = self.preferences["preferences"].get(task_type, {})

        for key, pref_data in task_prefs.items():
            if pref_data.get("auto_apply", True):
                auto_apply_prefs[key] = pref_data.get("value")

        return auto_apply_prefs

    def delete_preference(self, task_type: str, preference_key: Optional[str] = None) -> Dict[str, Any]:
        """删除任务偏好

        Args:
            task_type: 任务类型
            preference_key: 偏好键，为 None 时删除整个任务类型偏好

        Returns:
            删除结果
        """
        result = {
            "success": False,
            "message": ""
        }

        try:
            if preference_key is None:
                # 删除整个任务类型
                if task_type in self.preferences["preferences"]:
                    old_value = self.preferences["preferences"].pop(task_type, {})
                    self._save_preferences()
                    self._add_to_history("delete", task_type, "*", old_value, None)
                    result["success"] = True
                    result["message"] = f"已删除任务 [{task_type}] 的所有偏好"
            else:
                # 删除特定偏好
                if task_type in self.preferences["preferences"]:
                    old_value = self.preferences["preferences"][task_type].pop(preference_key, None)
                    if old_value:
                        self._save_preferences()
                        self._add_to_history("delete", task_type, preference_key, old_value, None)
                        result["success"] = True
                        result["message"] = f"已删除任务 [{task_type}] 的偏好 [{preference_key}]"

            print(f"[TaskPreference] {result['message']}")

        except Exception as e:
            result["message"] = f"删除偏好失败: {str(e)}"
            print(f"[TaskPreference] 错误: {e}")

        return result

    def auto_learn_from_history(self, task_type: str, action_data: Dict[str, Any]) -> bool:
        """从执行历史中自动学习偏好

        Args:
            task_type: 任务类型
            action_data: 执行动作数据

        Returns:
            是否学习到新偏好
        """
        if not self.auto_learn_enabled:
            return False

        # 检查是否已有该任务的偏好
        existing_prefs = self.preferences["preferences"].get(task_type, {})

        # 简单的自动学习规则：
        # 1. 如果某窗口标题被多次使用，记录为默认窗口
        # 2. 如果某应用被多次启动，记录为首选应用

        learned = False

        # 记录窗口标题偏好
        if "window_title" in action_data:
            window_title = action_data["window_title"]
            key = "default_window_title"
            existing = existing_prefs.get(key, {}).get("value")

            if existing is None or existing != window_title:
                self.set_preference(task_type, key, window_title, auto_apply=True)
                learned = True

        # 记录首选应用
        if "app_name" in action_data:
            app_name = action_data["app_name"]
            key = "preferred_app"
            existing = existing_prefs.get(key, {}).get("value")

            if existing is None or existing != app_name:
                self.set_preference(task_type, key, app_name, auto_apply=True)
                learned = True

        return learned

    def apply_preferences_to_task(self, task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """将偏好应用到任务执行

        Args:
            task_type: 任务类型
            task_data: 任务数据

        Returns:
            应用偏好后的任务数据
        """
        auto_prefs = self.get_auto_apply_preferences(task_type)

        if not auto_prefs:
            return task_data

        # 合并偏好到任务数据
        result_data = task_data.copy()
        result_data["_applied_preferences"] = auto_prefs

        # 应用每个偏好
        for key, value in auto_prefs.items():
            if key == "default_window_title" and "window_title" not in result_data:
                result_data["window_title"] = value
            elif key == "preferred_app" and "app_name" not in result_data:
                result_data["app_name"] = value
            elif key == "default_params" and "params" not in result_data:
                result_data["params"] = value
            else:
                # 其他键值直接添加
                if key not in result_data:
                    result_data[key] = value

        return result_data

    def _add_to_history(self, action: str, task_type: str, preference_key: str,
                        old_value: Any, new_value: Any):
        """添加历史记录"""
        history = self._load_history()

        history.append({
            "action": action,
            "task_type": task_type,
            "preference_key": preference_key,
            "old_value": str(old_value) if old_value is not None else None,
            "new_value": str(new_value) if new_value is not None else None,
            "timestamp": datetime.now().isoformat()
        })

        self._save_history(history)

    def get_preference_stats(self) -> Dict[str, Any]:
        """获取偏好统计信息"""
        prefs = self.preferences.get("preferences", {})
        history = self._load_history()

        stats = {
            "total_task_types": len(prefs),
            "total_preferences": sum(len(v) for v in prefs.values()),
            "task_types": list(prefs.keys()),
            "auto_learn_enabled": self.auto_learn_enabled,
            "history_count": len(history),
            "last_updated": self.preferences.get("last_updated")
        }

        # 统计每种任务类型的偏好数量
        stats["preferences_per_task"] = {
            task: len(prefs[task]) for task in prefs
        }

        return stats

    def list_task_preferences(self) -> List[Dict[str, Any]]:
        """列出所有任务偏好"""
        result = []
        prefs = self.preferences.get("preferences", {})

        for task_type, task_prefs in prefs.items():
            for pref_key, pref_data in task_prefs.items():
                result.append({
                    "task_type": task_type,
                    "preference_key": pref_key,
                    "value": pref_data.get("value"),
                    "auto_apply": pref_data.get("auto_apply", True),
                    "created_at": pref_data.get("created_at"),
                    "updated_at": pref_data.get("updated_at")
                })

        return result

    def clear_all_preferences(self) -> Dict[str, Any]:
        """清除所有偏好"""
        self.preferences = {
            "preferences": {},
            "auto_learn_patterns": [],
            "last_updated": None
        }
        self._save_preferences()

        # 清空历史
        self._save_history([])

        return {
            "success": True,
            "message": "已清除所有任务偏好"
        }

    def export_preferences(self) -> Dict[str, Any]:
        """导出不包含敏感信息的偏好"""
        return {
            "preferences": self.preferences.get("preferences", {}),
            "exported_at": datetime.now().isoformat()
        }

    def import_preferences(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """导入偏好"""
        result = {
            "success": False,
            "message": ""
        }

        try:
            if "preferences" in data:
                # 合并偏好
                for task_type, task_prefs in data["preferences"].items():
                    if task_type not in self.preferences["preferences"]:
                        self.preferences["preferences"][task_type] = {}
                    for key, value in task_prefs.items():
                        if isinstance(value, dict):
                            self.preferences["preferences"][task_type][key] = value
                        else:
                            self.preferences["preferences"][task_type][key] = {
                                "value": value,
                                "auto_apply": True,
                                "created_at": datetime.now().isoformat(),
                                "updated_at": datetime.now().isoformat()
                            }

                self._save_preferences()
                result["success"] = True
                result["message"] = "偏好导入成功"
            else:
                result["message"] = "无效的导入数据格式"

        except Exception as e:
            result["message"] = f"导入失败: {str(e)}"

        return result


# 全局实例
_preference_engine = None


def get_preference_engine() -> TaskPreferenceEngine:
    """获取偏好引擎单例"""
    global _preference_engine
    if _preference_engine is None:
        _preference_engine = TaskPreferenceEngine()
    return _preference_engine


def set_task_preference(task_type: str, preference_key: str,
                       preference_value: Any, auto_apply: bool = True) -> Dict[str, Any]:
    """设置任务偏好的便捷函数"""
    engine = get_preference_engine()
    return engine.set_preference(task_type, preference_key, preference_value, auto_apply)


def get_task_preferences(task_type: Optional[str] = None) -> Dict[str, Any]:
    """获取任务偏好的便捷函数"""
    engine = get_preference_engine()
    return engine.get_preferences(task_type)


def apply_task_preferences(task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """应用任务偏好的便捷函数"""
    engine = get_preference_engine()
    return engine.apply_preferences_to_task(task_type, task_data)


# CLI 接口
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='智能任务偏好记忆引擎')
    parser.add_argument('action', nargs='?', default='list',
                       choices=['list', 'set', 'get', 'delete', 'stats', 'clear', 'apply', 'export', 'import'],
                       help='动作')
    parser.add_argument('--task', '-t', help='任务类型')
    parser.add_argument('--key', '-k', help='偏好键')
    parser.add_argument('--value', '-v', help='偏好值')
    parser.add_argument('--auto-apply', '-a', type=bool, default=True, help='是否自动应用')
    parser.add_argument('--json', '-j', action='store_true', help='输出JSON格式')
    parser.add_argument('--import-data', help='导入数据(JSON字符串)')

    args = parser.parse_args()

    engine = get_preference_engine()

    if args.action == 'list':
        prefs = engine.list_task_preferences()
        if args.json:
            print(json.dumps(prefs, ensure_ascii=False, indent=2))
        else:
            print("=== 任务偏好列表 ===")
            if not prefs:
                print("暂无偏好设置")
            for p in prefs:
                print(f"\n任务: {p['task_type']}")
                print(f"  偏好: {p['preference_key']} = {p['value']}")
                print(f"  自动应用: {p['auto_apply']}")
                print(f"  更新时间: {p.get('updated_at', 'N/A')}")

    elif args.action == 'set':
        if not args.task or not args.key or args.value is None:
            print("错误: 需要指定 --task, --key, --value")
        else:
            result = engine.set_preference(args.task, args.key, args.value, args.auto_apply)
            print(result['message'])

    elif args.action == 'get':
        if not args.task:
            print("错误: 需要指定 --task")
        else:
            prefs = engine.get_preferences(args.task)
            if args.json:
                print(json.dumps(prefs, ensure_ascii=False, indent=2))
            else:
                print(f"=== 任务 [{args.task}] 的偏好 ===")
                if not prefs:
                    print("暂无偏好")
                for k, v in prefs.items():
                    print(f"  {k}: {v}")

    elif args.action == 'delete':
        if not args.task:
            print("错误: 需要指定 --task")
        else:
            result = engine.delete_preference(args.task, args.key)
            print(result['message'])

    elif args.action == 'stats':
        stats = engine.get_preference_stats()
        if args.json:
            print(json.dumps(stats, ensure_ascii=False, indent=2))
        else:
            print("=== 偏好统计 ===")
            print(f"任务类型数: {stats['total_task_types']}")
            print(f"偏好总数: {stats['total_preferences']}")
            print(f"自动学习: {'已启用' if stats['auto_learn_enabled'] else '已禁用'}")
            print(f"历史记录: {stats['history_count']} 条")
            print(f"最后更新: {stats.get('last_updated', 'N/A')}")
            if stats.get('preferences_per_task'):
                print("\n各任务偏好数:")
                for task, count in stats['preferences_per_task'].items():
                    print(f"  {task}: {count} 个")

    elif args.action == 'clear':
        result = engine.clear_all_preferences()
        print(result['message'])

    elif args.action == 'apply':
        if not args.task:
            print("错误: 需要指定 --task")
        else:
            test_data = {"action": "test", "params": {}}
            result = engine.apply_preferences_to_task(args.task, test_data)
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(f"=== 应用任务 [{args.task}] 偏好 ===")
                print(f"原始数据: {test_data}")
                print(f"应用后: {result}")

    elif args.action == 'export':
        data = engine.export_preferences()
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print("=== 偏好导出 ===")
            print(f"任务类型数: {len(data.get('preferences', {}))}")

    elif args.action == 'import':
        if not args.import_data:
            print("错误: 需要指定 --import-data")
        else:
            try:
                import_data = json.loads(args.import_data)
                result = engine.import_preferences(import_data)
                print(result['message'])
            except json.JSONDecodeError:
                print("错误: 无效的JSON格式")