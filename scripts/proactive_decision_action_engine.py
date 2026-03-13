#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能主动决策与行动引擎
让系统具备持续监控、主动识别优化机会、生成行动计划并自动执行的能力

功能：
1. 持续监控系统状态 - 监控执行历史、引擎活跃度、用户行为模式
2. 主动识别优化机会 - 基于多维度分析发现可优化的点
3. 生成行动计划 - 自动生成可执行的步骤链
4. 执行或确认 - 自动执行或征询用户同意后执行
5. 效果评估与学习 - 记录执行效果，反馈优化

工作原理：
- 持续运行（守护进程模式或定时触发）
- 收集和分析来自各引擎的数据（执行历史、用户行为、系统状态）
- 识别优化机会（如：重复操作可自动化、低效流程可优化、潜在问题可预防）
- 生成行动计划（基于场景计划模板或动态生成）
- 执行并评估效果
- 反馈学习，持续改进识别和执行策略
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict

# 确保 scripts 目录在路径中
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..'))
STATE_DIR = os.path.join(PROJECT_DIR, 'runtime', 'state')
LOGS_DIR = os.path.join(PROJECT_DIR, 'runtime', 'logs')


class ProactiveDecisionActionEngine:
    """智能主动决策与行动引擎"""

    def __init__(self):
        self.state_file = os.path.join(STATE_DIR, 'proactive_engine_state.json')
        self.opportunities_file = os.path.join(STATE_DIR, 'proactive_opportunities.json')
        self.actions_file = os.path.join(STATE_DIR, 'proactive_actions.json')
        self.state = self._load_state()
        self.min_confidence = 0.6  # 最小置信度阈值

    def _load_state(self) -> Dict[str, Any]:
        """加载引擎状态"""
        os.makedirs(STATE_DIR, exist_ok=True)
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[ProactiveEngine] 加载状态失败: {e}")
        return {
            "enabled": True,
            "mode": "auto",  # auto: 自动执行, semi_auto: 确认后执行, passive: 只推荐
            "monitor_interval": 300,  # 监控间隔（秒）
            "last_check": None,
            "opportunities_found": 0,
            "actions_executed": 0,
            "success_rate": 0.0,
            "learned_patterns": []
        }

    def _save_state(self):
        """保存引擎状态"""
        try:
            os.makedirs(STATE_DIR, exist_ok=True)
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ProactiveEngine] 保存状态失败: {e}")

    def _load_recent_logs(self, hours: int = 24) -> List[Dict[str, Any]]:
        """加载最近的执行日志"""
        logs = []
        recent_logs_file = os.path.join(STATE_DIR, 'recent_logs.json')

        if os.path.exists(recent_logs_file):
            try:
                with open(recent_logs_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 过滤最近 N 小时的日志
                    cutoff = datetime.now() - timedelta(hours=hours)
                    for entry in data.get('logs', []):
                        try:
                            ts = datetime.fromisoformat(entry.get('timestamp', '').replace('Z', '+00:00'))
                            if ts.replace(tzinfo=None) > cutoff:
                                logs.append(entry)
                        except:
                            pass
            except Exception as e:
                print(f"[ProactiveEngine] 加载日志失败: {e}")

        return logs

    def _load_execution_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """加载执行历史"""
        history = []

        # 尝试从 run_plan 历史加载
        run_plan_history = os.path.join(STATE_DIR, 'run_plan_history.json')
        if os.path.exists(run_plan_history):
            try:
                with open(run_plan_history, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    cutoff = datetime.now() - timedelta(hours=hours)
                    for entry in data.get('history', []):
                        try:
                            ts = datetime.fromisoformat(entry.get('timestamp', '').replace('Z', '+00:00'))
                            if ts.replace(tzinfo=None) > cutoff:
                                history.append(entry)
                        except:
                            pass
            except Exception as e:
                print(f"[ProactiveEngine] 加载执行历史失败: {e}")

        return history

    def analyze_opportunities(self) -> List[Dict[str, Any]]:
        """分析并识别优化机会"""
        opportunities = []

        # 1. 分析执行日志，识别重复操作
        recent_logs = self._load_recent_logs(hours=24)
        action_counts = defaultdict(int)
        for log in recent_logs:
            action = log.get('action', log.get('type', 'unknown'))
            action_counts[action] += 1

        # 识别高频操作（可考虑自动化）
        for action, count in action_counts.items():
            if count >= 3 and action not in ['screenshot', 'vision', 'mouse_move']:
                opportunities.append({
                    "type": "frequent_action",
                    "action": action,
                    "count": count,
                    "suggestion": f"检测到频繁操作「{action}」{count}次，建议创建自动化场景",
                    "confidence": min(0.9, 0.5 + count * 0.1),
                    "auto_actionable": True
                })

        # 2. 分析执行历史，识别低效流程
        execution_history = self._load_execution_history(hours=48)
        failed_count = sum(1 for h in execution_history if h.get('status') == 'failed')
        total_count = len(execution_history)

        if total_count > 0:
            failure_rate = failed_count / total_count
            if failure_rate > 0.3:
                opportunities.append({
                    "type": "high_failure_rate",
                    "failure_rate": failure_rate,
                    "suggestion": f"检测到较高失败率({failure_rate:.1%})，建议分析失败原因并优化执行策略",
                    "confidence": min(0.95, 0.6 + failure_rate * 0.3),
                    "auto_actionable": False
                })

        # 3. 识别时间模式机会
        current_hour = datetime.now().hour

        # 早上 9 点：推荐检查日程/待办
        if 8 <= current_hour <= 10:
            opportunities.append({
                "type": "time_pattern",
                "pattern": "morning_check",
                "suggestion": "早晨时间，建议检查今日日程和待办事项",
                "confidence": 0.85,
                "auto_actionable": True,
                "action_type": "recommendation"
            })

        # 下午 2 点：推荐检查未完成任务
        if 13 <= current_hour <= 15:
            opportunities.append({
                "type": "time_pattern",
                "pattern": "afternoon_check",
                "suggestion": "下午时间，建议检查上午未完成任务",
                "confidence": 0.75,
                "auto_actionable": True,
                "action_type": "recommendation"
            })

        # 4. 基于已学习模式的机会
        learned_patterns = self.state.get('learned_patterns', [])
        for pattern in learned_patterns:
            opportunities.append({
                "type": "learned_pattern",
                "pattern": pattern,
                "suggestion": f"根据学习到的模式：{pattern.get('description', '用户习惯')}",
                "confidence": pattern.get('confidence', 0.7),
                "auto_actionable": pattern.get('auto_actionable', False),
                "action_type": pattern.get('action_type', 'recommendation')
            })

        # 保存机会列表
        self._save_opportunities(opportunities)

        # 更新状态
        self.state['opportunities_found'] = len(opportunities)
        self.state['last_check'] = datetime.now().isoformat()
        self._save_state()

        return opportunities

    def _save_opportunities(self, opportunities: List[Dict[str, Any]]):
        """保存识别的机会"""
        try:
            os.makedirs(STATE_DIR, exist_ok=True)
            with open(self.opportunities_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "opportunities": opportunities
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ProactiveEngine] 保存机会失败: {e}")

    def generate_action_plan(self, opportunity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """根据机会生成行动计划"""
        opp_type = opportunity.get('type', '')

        if opp_type == 'frequent_action':
            # 频繁操作 -> 建议创建自动化场景
            action = opportunity.get('action', '')
            return {
                "plan_type": "create_automation",
                "title": f"创建「{action}」自动化场景",
                "description": f"检测到频繁执行「{action}」，建议创建自动化场景计划",
                "steps": [
                    {"action": "analyze", "target": f"分析{action}操作的执行流程"},
                    {"action": "create_plan", "target": f"创建{action}场景计划 JSON"},
                    {"action": "test", "target": "测试自动化场景"}
                ],
                "confidence": opportunity.get('confidence', 0.7)
            }

        elif opp_type == 'high_failure_rate':
            # 高失败率 -> 建议分析优化
            return {
                "plan_type": "optimize_strategy",
                "title": "优化执行策略",
                "description": "检测到较高执行失败率，建议分析原因并优化",
                "steps": [
                    {"action": "analyze_failures", "target": "分析最近失败记录"},
                    {"action": "identify_issues", "target": "识别主要问题"},
                    {"action": "optimize", "target": "生成优化建议"}
                ],
                "confidence": opportunity.get('confidence', 0.7)
            }

        elif opp_type == 'time_pattern':
            # 时间模式 -> 主动服务
            pattern = opportunity.get('pattern', '')
            if pattern == 'morning_check':
                return {
                    "plan_type": "morning_service",
                    "title": "早晨主动服务",
                    "description": "早晨时间，主动提供日程和待办检查服务",
                    "steps": [
                        {"action": "check_schedule", "target": "检查今日日程"},
                        {"action": "check_todos", "target": "检查待办事项"},
                        {"action": "summarize", "target": "总结今日任务"}
                    ],
                    "auto_execute": True,
                    "confidence": opportunity.get('confidence', 0.7)
                }
            elif pattern == 'afternoon_check':
                return {
                    "plan_type": "afternoon_service",
                    "title": "下午主动服务",
                    "description": "下午时间，检查上午未完成任务",
                    "steps": [
                        {"action": "check_pending", "target": "检查未完成事项"},
                        {"action": "remind", "target": "提醒待处理任务"}
                    ],
                    "auto_execute": True,
                    "confidence": opportunity.get('confidence', 0.7)
                }

        elif opp_type == 'learned_pattern':
            # 学习到的模式 -> 应用偏好
            pattern = opportunity.get('pattern', {})
            return {
                "plan_type": "apply_learned",
                "title": pattern.get('title', '应用学习到的偏好'),
                "description": pattern.get('description', ''),
                "steps": pattern.get('steps', []),
                "auto_execute": pattern.get('auto_execute', False),
                "confidence": opportunity.get('confidence', 0.7)
            }

        return None

    def evaluate_and_learn(self, action_result: Dict[str, Any]):
        """评估行动结果并学习"""
        success = action_result.get('success', False)
        action_type = action_result.get('action_type', 'unknown')

        # 更新成功率
        total = self.state.get('actions_executed', 0)
        current_rate = self.state.get('success_rate', 0.0)

        if total > 0:
            new_rate = (current_rate * total + (1.0 if success else 0.0)) / (total + 1)
            self.state['success_rate'] = new_rate

        self.state['actions_executed'] = total + 1

        # 从成功案例中学习
        if success and action_type == 'learned_pattern':
            pattern = action_result.get('pattern', {})
            if pattern:
                patterns = self.state.get('learned_patterns', [])
                # 增强置信度
                pattern['confidence'] = min(0.95, pattern.get('confidence', 0.7) + 0.05)
                patterns.append(pattern)
                # 保留最近的 20 条
                self.state['learned_patterns'] = patterns[-20:]

        self._save_state()

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "enabled": self.state.get('enabled', True),
            "mode": self.state.get('mode', 'auto'),
            "last_check": self.state.get('last_check'),
            "opportunities_found": self.state.get('opportunities_found', 0),
            "actions_executed": self.state.get('actions_executed', 0),
            "success_rate": self.state.get('success_rate', 0.0),
            "learned_patterns_count": len(self.state.get('learned_patterns', []))
        }

    def scan_and_recommend(self) -> Dict[str, Any]:
        """扫描并返回推荐"""
        opportunities = self.analyze_opportunities()

        recommendations = []
        for opp in opportunities:
            if opp.get('confidence', 0) >= self.min_confidence:
                plan = self.generate_action_plan(opp)
                if plan:
                    recommendations.append({
                        "opportunity": opp,
                        "action_plan": plan,
                        "confidence": opp.get('confidence', 0)
                    })

        # 按置信度排序
        recommendations.sort(key=lambda x: x.get('confidence', 0), reverse=True)

        return {
            "status": self.get_status(),
            "opportunities_count": len(opportunities),
            "recommendations": recommendations[:5]  # 最多返回 5 条
        }

    def set_mode(self, mode: str) -> Dict[str, Any]:
        """设置引擎模式"""
        if mode not in ['auto', 'semi_auto', 'passive']:
            return {"success": False, "message": f"无效模式: {mode}"}

        self.state['mode'] = mode
        self._save_state()
        return {"success": True, "message": f"模式已设置为: {mode}"}

    def enable(self):
        """启用引擎"""
        self.state['enabled'] = True
        self._save_state()

    def disable(self):
        """禁用引擎"""
        self.state['enabled'] = False
        self._save_state()


def main():
    """CLI 入口"""
    import sys

    engine = ProactiveDecisionActionEngine()

    if len(sys.argv) < 2:
        print("=== 智能主动决策与行动引擎 ===")
        print("用法:")
        print("  python proactive_decision_action_engine.py status    - 查看状态")
        print("  python proactive_decision_action_engine.py scan       - 扫描并推荐")
        print("  python proactive_decision_action_engine.py analyze   - 分析机会")
        print("  python proactive_decision_action_engine.py enable   - 启用引擎")
        print("  python proactive_decision_action_engine.py disable   - 禁用引擎")
        print("  python proactive_decision_action_engine.py mode <auto|semi_auto|passive> - 设置模式")
        return

    command = sys.argv[1]

    if command == "status":
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif command == "scan":
        result = engine.scan_and_recommend()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "analyze":
        opportunities = engine.analyze_opportunities()
        print(json.dumps({
            "count": len(opportunities),
            "opportunities": opportunities
        }, ensure_ascii=False, indent=2))

    elif command == "enable":
        engine.enable()
        print("引擎已启用")

    elif command == "disable":
        engine.disable()
        print("引擎已禁用")

    elif command == "mode":
        if len(sys.argv) < 3:
            print("请指定模式: auto, semi_auto, passive")
        else:
            result = engine.set_mode(sys.argv[2])
            print(result.get("message", ""))

    else:
        print(f"未知命令: {command}")


if __name__ == "__main__":
    main()