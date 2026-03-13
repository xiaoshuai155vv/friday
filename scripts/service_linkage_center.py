#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能服务联动中心引擎 (Service Linkage Center Engine)

功能：实现跨引擎的自动触发协同修复闭环
- 统一管理跨引擎的自动触发机制
- 监听各引擎产生的预警/问题事件
- 定义事件→引擎的映射规则
- 当某引擎发现问题，自动触发相关引擎执行协同修复
- 记录联动执行效果

集成到 do.py 支持以下关键词触发：
- 服务联动、联动中心、联动状态、查看联动
- 自动触发、触发规则、联动执行
"""

import json
import os
import subprocess
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

# 基础路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUNTIME_DIR = os.path.join(BASE_DIR, "..", "runtime", "state")
LINKAGE_CONFIG = os.path.join(RUNTIME_DIR, "service_linkage_config.json")
LINKAGE_LOG = os.path.join(RUNTIME_DIR, "service_linkage_log.json")


class ServiceLinkageCenter:
    """智能服务联动中心"""

    def __init__(self):
        self.config = self._load_config()
        self.linkage_log = self._load_linkage_log()

    def _load_config(self) -> Dict:
        """加载联动配置"""
        default_config = {
            "linkage_rules": [
                {
                    "id": "rule_1",
                    "name": "健康保障触发主动运维",
                    "trigger_event": "health_warning",
                    "source_engine": "health_assurance_loop",
                    "target_engines": ["proactive_operations_engine"],
                    "auto_execute": True,
                    "enabled": True,
                    "description": "当健康保障引擎检测到问题时，自动触发主动运维引擎执行优化"
                },
                {
                    "id": "rule_2",
                    "name": "性能监控触发协同优化",
                    "trigger_event": "performance_degradation",
                    "source_engine": "engine_performance_monitor",
                    "target_engines": ["cross_engine_optimizer"],
                    "auto_execute": False,
                    "enabled": True,
                    "description": "当性能监控引擎检测到性能下降时，生成协同优化建议"
                },
                {
                    "id": "rule_3",
                    "name": "安全监控触发自愈引擎",
                    "trigger_event": "security_threat",
                    "source_engine": "security_monitor_engine",
                    "target_engines": ["self_healing_engine"],
                    "auto_execute": True,
                    "enabled": True,
                    "description": "当安全监控引擎检测到安全威胁时，自动触发自愈引擎尝试修复"
                },
                {
                    "id": "rule_4",
                    "name": "主动运维触发健康保障",
                    "trigger_event": "optimization_completed",
                    "source_engine": "proactive_operations_engine",
                    "target_engines": ["health_assurance_loop"],
                    "auto_execute": False,
                    "enabled": True,
                    "description": "主动运维完成后，通知健康保障引擎重新评估系统状态"
                }
            ],
            "event_queue": [],
            "last_update": ""
        }

        if os.path.exists(LINKAGE_CONFIG):
            try:
                with open(LINKAGE_CONFIG, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return default_config

    def _save_config(self):
        """保存联动配置"""
        self.config["last_update"] = datetime.now(timezone.utc).isoformat()
        os.makedirs(RUNTIME_DIR, exist_ok=True)
        with open(LINKAGE_CONFIG, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def _load_linkage_log(self) -> List[Dict]:
        """加载联动日志"""
        if os.path.exists(LINKAGE_LOG):
            try:
                with open(LINKAGE_LOG, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_linkage_log(self):
        """保存联动日志"""
        # 只保留最近100条
        self.linkage_log = self.linkage_log[-100:]
        os.makedirs(RUNTIME_DIR, exist_ok=True)
        with open(LINKAGE_LOG, "w", encoding="utf-8") as f:
            json.dump(self.linkage_log, f, ensure_ascii=False, indent=2)

    def register_event(self, event_type: str, source_engine: str, event_data: Dict) -> str:
        """
        注册事件，触发联动规则

        Args:
            event_type: 事件类型 (health_warning, performance_degradation, security_threat, optimization_completed 等)
            source_engine: 事件来源引擎
            event_data: 事件数据

        Returns:
            事件ID
        """
        event_id = f"event_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}"
        event = {
            "id": event_id,
            "type": event_type,
            "source": source_engine,
            "data": event_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        self.config["event_queue"].append(event)
        self._save_config()

        # 触发联动
        triggered_actions = self._trigger_linkage(event)

        # 记录日志
        log_entry = {
            "event_id": event_id,
            "event_type": event_type,
            "source": source_engine,
            "triggered_actions": triggered_actions,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.linkage_log.append(log_entry)
        self._save_linkage_log()

        return event_id

    def _trigger_linkage(self, event: Dict) -> List[Dict]:
        """触发联动规则"""
        triggered = []

        for rule in self.config.get("linkage_rules", []):
            if not rule.get("enabled", True):
                continue
            if rule["trigger_event"] != event["type"]:
                continue
            if rule["source_engine"] != event["source"]:
                continue

            action = {
                "rule_id": rule["id"],
                "rule_name": rule["name"],
                "target_engines": rule["target_engines"],
                "auto_execute": rule.get("auto_execute", False)
            }

            if rule.get("auto_execute", False):
                # 自动执行
                for engine in rule["target_engines"]:
                    result = self._execute_engine_action(engine, event)
                    action["results"] = action.get("results", [])
                    action["results"].append({
                        "engine": engine,
                        "result": result
                    })

            triggered.append(action)

        return triggered

    def _execute_engine_action(self, engine: str, event: Dict) -> Dict:
        """执行引擎动作"""
        try:
            if engine == "proactive_operations_engine":
                # 调用主动运维引擎执行优化
                result = subprocess.run(
                    ["python", os.path.join(BASE_DIR, "do.py"), "自动优化"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                return {"status": "success", "output": result.stdout}
            elif engine == "self_healing_engine":
                # 调用自愈引擎
                result = subprocess.run(
                    ["python", os.path.join(BASE_DIR, "do.py"), "系统自愈"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                return {"status": "success", "output": result.stdout}
            elif engine == "health_assurance_loop":
                # 触发健康保障重新评估
                result = subprocess.run(
                    ["python", os.path.join(BASE_DIR, "do.py"), "健康保障状态"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return {"status": "success", "output": result.stdout}
            elif engine == "cross_engine_optimizer":
                # 触发跨引擎优化分析
                result = subprocess.run(
                    ["python", os.path.join(BASE_DIR, "do.py"), "协同优化分析"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                return {"status": "success", "output": result.stdout}
            else:
                return {"status": "unknown_engine", "message": f"未知的引擎: {engine}"}
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "message": "执行超时"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_linkage_status(self) -> Dict:
        """获取联动状态"""
        return {
            "active_rules": sum(1 for r in self.config.get("linkage_rules", []) if r.get("enabled", True)),
            "total_rules": len(self.config.get("linkage_rules", [])),
            "pending_events": len(self.config.get("event_queue", [])),
            "recent_actions": len([l for l in self.linkage_log if self._is_recent(l.get("timestamp", ""))]),
            "rules": self.config.get("linkage_rules", [])
        }

    def _is_recent(self, timestamp: str) -> bool:
        """检查是否近期事件"""
        try:
            event_time = datetime.fromisoformat(timestamp.replace("+00:00", ""))
            now = datetime.now(timezone.utc)
            return (now - event_time).total_seconds() < 3600  # 1小时内
        except Exception:
            return False

    def get_linkage_history(self, limit: int = 10) -> List[Dict]:
        """获取联动历史"""
        return self.linkage_log[-limit:]

    def add_linkage_rule(self, rule: Dict) -> Dict:
        """添加联动规则"""
        rule["id"] = f"rule_{len(self.config.get('linkage_rules', [])) + 1}"
        self.config["linkage_rules"].append(rule)
        self._save_config()
        return {"status": "success", "rule_id": rule["id"]}

    def remove_linkage_rule(self, rule_id: str) -> Dict:
        """移除联动规则"""
        rules = self.config.get("linkage_rules", [])
        self.config["linkage_rules"] = [r for r in rules if r.get("id") != rule_id]
        self._save_config()
        return {"status": "success"}

    def enable_rule(self, rule_id: str) -> Dict:
        """启用联动规则"""
        for rule in self.config.get("linkage_rules", []):
            if rule.get("id") == rule_id:
                rule["enabled"] = True
                self._save_config()
                return {"status": "success"}
        return {"status": "not_found"}

    def disable_rule(self, rule_id: str) -> Dict:
        """禁用联动规则"""
        for rule in self.config.get("linkage_rules", []):
            if rule.get("id") == rule_id:
                rule["enabled"] = False
                self._save_config()
                return {"status": "success"}
        return {"status": "not_found"}

    def clear_event_queue(self) -> Dict:
        """清空事件队列"""
        self.config["event_queue"] = []
        self._save_config()
        return {"status": "success"}


def main():
    """CLI 入口"""
    import argparse
    parser = argparse.ArgumentParser(description="智能服务联动中心")
    parser.add_argument("action", nargs="?", choices=["status", "history", "clear"], default="status",
                        help="操作类型")
    parser.add_argument("--rule-id", help="规则ID")
    parser.add_argument("--enable", action="store_true", help="启用规则")
    parser.add_argument("--disable", action="store_true", help="禁用规则")

    args = parser.parse_args()
    center = ServiceLinkageCenter()

    if args.action == "status":
        status = center.get_linkage_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    elif args.action == "history":
        history = center.get_linkage_history()
        print(json.dumps(history, ensure_ascii=False, indent=2))
    elif args.action == "clear":
        result = center.clear_event_queue()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.enable and args.rule_id:
        result = center.enable_rule(args.rule_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.disable and args.rule_id:
        result = center.disable_rule(args.rule_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()