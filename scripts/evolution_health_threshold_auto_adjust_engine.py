#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环健康分数阈值自动调整引擎
==================================================

round 399: 在 round 398 的健康阈值触发引擎基础上，增强阈值自动调整能力，
根据历史触发数据自动优化阈值设置

功能：
1. 基于历史触发数据的智能阈值分析
2. 触发频率与趋势分析
3. 自适应阈值优化逻辑
4. 与现有阈值触发引擎深度集成
5. 智能阈值建议生成

version: 1.0.0
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict

# 添加 scripts 目录到路径以导入依赖模块
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

# 尝试导入依赖引擎
try:
    from evolution_health_threshold_trigger_engine import (
        EvolutionHealthThresholdTriggerEngine,
        get_threshold_trigger_engine
    )
except ImportError:
    EvolutionHealthThresholdTriggerEngine = None


class ThresholdAnalysisEngine:
    """阈值分析引擎 - 分析历史触发数据"""

    def __init__(self, trigger_engine):
        """初始化阈值分析引擎"""
        self.trigger_engine = trigger_engine
        self.analysis_cache = {}
        self.cache_ttl = 300  # 缓存5分钟

    def analyze_trigger_frequency(self, days: int = 7) -> Dict[str, Any]:
        """分析触发频率

        Args:
            days: 分析天数

        Returns:
            触发频率分析结果
        """
        history = self.trigger_engine.get_trigger_history(limit=200)
        if not history:
            return {
                "total_triggers": 0,
                "frequency": "none",
                "recommendation": "没有足够的触发历史数据进行分析"
            }

        # 按日期分组统计
        date_counts = defaultdict(int)
        for record in history:
            try:
                timestamp = record.get("timestamp", "")
                if timestamp:
                    date = timestamp[:10]  # 取日期部分
                    date_counts[date] += 1
            except Exception:
                continue

        # 计算最近N天的触发次数
        recent_days = min(days, len(date_counts))
        if recent_days == 0:
            return {
                "total_triggers": len(history),
                "frequency": "none",
                "recommendation": "触发历史数据不足"
            }

        # 计算平均每天触发次数
        total_recent = sum(list(date_counts.values())[-recent_days:])
        avg_daily = total_recent / recent_days

        # 评估频率等级
        if avg_daily >= 3:
            frequency = "high"
            recommendation = "触发频率较高，建议降低阈值或增加系统容错能力"
        elif avg_daily >= 1:
            frequency = "medium"
            recommendation = "触发频率适中，保持当前阈值设置"
        else:
            frequency = "low"
            recommendation = "触发频率较低，可以适当提高阈值以更早发现问题"

        return {
            "total_triggers": len(history),
            "recent_days": recent_days,
            "total_recent": total_recent,
            "avg_daily": round(avg_daily, 2),
            "frequency": frequency,
            "by_level": self.trigger_engine.get_statistics().get("by_level", {}),
            "recommendation": recommendation
        }

    def analyze_trigger_trend(self) -> Dict[str, Any]:
        """分析触发趋势（递增/递减/稳定）"""
        history = self.trigger_engine.get_trigger_history(limit=50)
        if len(history) < 5:
            return {
                "trend": "insufficient_data",
                "recommendation": "触发历史数据不足，无法分析趋势"
            }

        # 将历史分成前后两半
        mid = len(history) // 2
        first_half = history[:mid]
        second_half = history[mid:]

        # 计算每半部分的触发次数
        first_count = len(first_half)
        second_count = len(second_half)

        # 计算趋势
        if second_count > first_count * 1.5:
            trend = "increasing"
            description = "触发次数呈上升趋势"
            recommendation = "系统健康可能正在恶化，建议检查系统状态并考虑调整阈值"
        elif second_count < first_count * 0.5:
            trend = "decreasing"
            description = "触发次数呈下降趋势"
            recommendation = "系统健康状况正在改善，阈值设置合理"
        else:
            trend = "stable"
            description = "触发次数保持稳定"
            recommendation = "系统运行稳定，当前阈值设置合适"

        return {
            "trend": trend,
            "description": description,
            "first_half_triggers": first_count,
            "second_half_triggers": second_count,
            "recommendation": recommendation
        }

    def analyze_trigger_time_distribution(self) -> Dict[str, Any]:
        """分析触发时间分布"""
        history = self.trigger_engine.get_trigger_history(limit=100)
        if not history:
            return {
                "distribution": {},
                "recommendation": "没有足够的触发历史数据"
            }

        # 按小时统计
        hour_counts = defaultdict(int)
        # 按星期几统计
        weekday_counts = defaultdict(int)

        for record in history:
            try:
                timestamp = record.get("timestamp", "")
                if timestamp:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    hour_counts[dt.hour] += 1
                    weekday_counts[dt.strftime("%A")] += 1
            except Exception:
                continue

        # 找出高峰时段
        if hour_counts:
            peak_hour = max(hour_counts.keys(), key=lambda h: hour_counts[h])
            peak_hour_count = hour_counts[peak_hour]
        else:
            peak_hour = None
            peak_hour_count = 0

        if weekday_counts:
            peak_day = max(weekday_counts.keys(), key=lambda d: weekday_counts[d])
            peak_day_count = weekday_counts[peak_day]
        else:
            peak_day = None
            peak_day_count = 0

        return {
            "by_hour": dict(hour_counts),
            "by_weekday": dict(weekday_counts),
            "peak_hour": peak_hour,
            "peak_hour_count": peak_hour_count,
            "peak_day": peak_day,
            "peak_day_count": peak_day_count,
            "recommendation": f"触发高峰时段: {peak_hour}:00 ({peak_day})"
        }

    def analyze_health_score_patterns(self) -> Dict[str, Any]:
        """分析健康分数模式"""
        history = self.trigger_engine.get_trigger_history(limit=100)
        if not history:
            return {
                "pattern": "insufficient_data",
                "recommendation": "没有足够的触发历史数据"
            }

        # 提取健康分数
        health_scores = [r.get("health_score", 0) for r in history if r.get("health_score")]

        if len(health_scores) < 5:
            return {
                "pattern": "insufficient_data",
                "recommendation": "数据不足"
            }

        avg_score = sum(health_scores) / len(health_scores)
        min_score = min(health_scores)
        max_score = max(health_scores)

        # 评估模式
        if avg_score < 30:
            pattern = "critical"
            description = "系统健康状况持续偏低"
        elif avg_score < 50:
            pattern = "warning"
            description = "系统健康状况时常处于警告水平"
        else:
            pattern = "stable"
            description = "系统健康状况总体稳定"

        return {
            "pattern": pattern,
            "description": description,
            "avg_health_score": round(avg_score, 1),
            "min_health_score": min_score,
            "max_health_score": max_score,
            "total_records": len(health_scores),
            "recommendation": f"平均触发健康分数: {round(avg_score, 1)}"
        }

    def comprehensive_analysis(self) -> Dict[str, Any]:
        """综合分析 - 整合所有分析结果"""
        return {
            "frequency": self.analyze_trigger_frequency(),
            "trend": self.analyze_trigger_trend(),
            "time_distribution": self.analyze_trigger_time_distribution(),
            "health_patterns": self.analyze_health_score_patterns()
        }


class ThresholdAutoAdjustEngine:
    """阈值自动调整引擎"""

    VERSION = "1.0.0"

    # 自动调整参数
    ADJUSTMENT_CONFIG = {
        "min_threshold": 10,      # 最小阈值（防止过度降低）
        "max_threshold": 90,     # 最大阈值（防止设置过高）
        "adjust_step": 5,        # 每次调整步长
        "stability_window": 10,  # 稳定性评估窗口（最近N次触发）
        "increase_threshold": 3, # 连续N次稳定后提高阈值
        "decrease_threshold": 3  # 连续N次触发后降低阈值
    }

    def __init__(self):
        """初始化阈值自动调整引擎"""
        self.trigger_engine = None
        self.analysis_engine = None
        self.adjustment_log: List[Dict[str, Any]] = []
        self._load_trigger_engine()
        self._load_adjustment_log()
        self.config = self._load_config()

    def _load_trigger_engine(self):
        """加载阈值触发引擎"""
        if EvolutionHealthThresholdTriggerEngine:
            try:
                self.trigger_engine = get_threshold_trigger_engine()
                self.analysis_engine = ThresholdAnalysisEngine(self.trigger_engine)
            except Exception as e:
                print(f"加载阈值触发引擎失败: {e}")
                self.trigger_engine = None

    def _load_config(self) -> Dict[str, Any]:
        """加载自动调整配置"""
        config_file = os.path.join(
            PROJECT_ROOT, "runtime", "state",
            "health_threshold_auto_adjust_config.json"
        )

        if os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        # 默认配置
        return {
            "enabled": True,  # 默认启用
            "auto_adjust_enabled": True,
            "adjust_interval_hours": 24,  # 调整间隔（小时）
            "last_adjust_time": None,
            "stability_counter": 0,  # 稳定性计数器
            "consecutive_triggers": 0,  # 连续触发计数器
            "config": self.ADJUSTMENT_CONFIG.copy()
        }

    def _save_config(self):
        """保存自动调整配置"""
        config_file = os.path.join(
            PROJECT_ROOT, "runtime", "state",
            "health_threshold_auto_adjust_config.json"
        )
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        try:
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存自动调整配置失败: {e}")

    def _load_adjustment_log(self):
        """加载调整日志"""
        log_file = os.path.join(
            PROJECT_ROOT, "runtime", "state",
            "health_threshold_adjustment_log.json"
        )
        if os.path.exists(log_file):
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    self.adjustment_log = json.load(f)
            except Exception:
                self.adjustment_log = []

        # 只保留最近100条
        if len(self.adjustment_log) > 100:
            self.adjustment_log = self.adjustment_log[-100:]

    def _save_adjustment_log(self):
        """保存调整日志"""
        log_file = os.path.join(
            PROJECT_ROOT, "runtime", "state",
            "health_threshold_adjustment_log.json"
        )
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        try:
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(self.adjustment_log, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存调整日志失败: {e}")

    def _add_adjustment_record(self, adjustment_type: str, old_value: int, new_value: int, level: str, reason: str):
        """添加调整记录"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "adjustment_type": adjustment_type,
            "level": level,
            "old_value": old_value,
            "new_value": new_value,
            "reason": reason
        }
        self.adjustment_log.append(record)
        self._save_adjustment_log()

    def analyze_and_suggest(self) -> Dict[str, Any]:
        """分析并给出阈值优化建议"""
        if not self.trigger_engine or not self.analysis_engine:
            return {
                "success": False,
                "message": "阈值触发引擎未加载"
            }

        current_thresholds = self.trigger_engine.get_thresholds()
        analysis = self.analysis_engine.comprehensive_analysis()

        suggestions = []
        new_thresholds = current_thresholds.copy()
        config = self.config.get("config", self.ADJUSTMENT_CONFIG)

        # 基于频率分析
        freq_analysis = analysis.get("frequency", {})
        freq = freq_analysis.get("frequency", "none")
        avg_daily = freq_analysis.get("avg_daily", 0)

        if freq == "high":
            # 触发频率高，降低阈值让系统更早发现问题
            for level in ["warning", "critical", "emergency"]:
                current = new_thresholds.get(level, 60 if level == "warning" else 40 if level == "critical" else 20)
                new_value = max(current - config["adjust_step"], config["min_threshold"])
                if new_value != current:
                    new_thresholds[level] = new_value
                    suggestions.append(f"{level}阈值从{current}降低到{new_value}（触发频率高）")
        elif freq == "low":
            # 触发频率低，可以适当提高阈值
            for level in ["warning", "critical", "emergency"]:
                current = new_thresholds.get(level, 60 if level == "warning" else 40 if level == "critical" else 20)
                new_value = min(current + config["adjust_step"], config["max_threshold"])
                if new_value != current:
                    new_thresholds[level] = new_value
                    suggestions.append(f"{level}阈值从{current}提高到{new_value}（触发频率低）")

        # 基于趋势分析
        trend_analysis = analysis.get("trend", {})
        trend = trend_analysis.get("trend", "stable")

        if trend == "increasing":
            suggestions.append("触发呈上升趋势，建议加强系统监控")
        elif trend == "decreasing":
            suggestions.append("触发呈下降趋势，系统健康状况改善")

        # 基于健康分数模式
        pattern_analysis = analysis.get("health_patterns", {})
        pattern = pattern_analysis.get("pattern", "stable")

        if pattern == "critical":
            suggestions.append("系统健康分数持续偏低，建议全面检查系统状态")
        elif pattern == "warning":
            suggestions.append("系统健康时常处于警告水平，建议优化资源配置")

        return {
            "success": True,
            "current_thresholds": current_thresholds,
            "suggested_thresholds": new_thresholds if suggestions else current_thresholds,
            "suggestions": suggestions,
            "analysis": analysis,
            "recommendation": "建议" + "；".join(suggestions) if suggestions else "当前阈值设置合理，无需调整"
        }

    def execute_auto_adjust(self, dry_run: bool = False) -> Dict[str, Any]:
        """执行自动调整

        Args:
            dry_run: 如果为True，只分析和建议不实际执行

        Returns:
            调整结果
        """
        if not self.trigger_engine:
            return {
                "success": False,
                "message": "阈值触发引擎未加载"
            }

        if not self.config.get("enabled", True):
            return {
                "success": False,
                "message": "自动调整已禁用"
            }

        # 分析并获取建议
        analysis_result = self.analyze_and_suggest()
        if not analysis_result.get("success"):
            return analysis_result

        current_thresholds = analysis_result.get("current_thresholds", {})
        suggested_thresholds = analysis_result.get("suggested_thresholds", {})
        suggestions = analysis_result.get("suggestions", [])

        if not suggestions or current_thresholds == suggested_thresholds:
            return {
                "success": True,
                "message": "当前阈值设置合理，无需调整",
                "analysis": analysis_result.get("analysis", {})
            }

        # 执行调整
        if not dry_run:
            try:
                # 应用新阈值
                for level, value in suggested_thresholds.items():
                    if level in current_thresholds and current_thresholds[level] != value:
                        old_value = current_thresholds[level]
                        self.trigger_engine.set_threshold(level, value)
                        self._add_adjustment_record(
                            "auto_adjust",
                            old_value,
                            value,
                            level,
                            "; ".join(suggestions)
                        )

                # 更新配置
                self.config["last_adjust_time"] = datetime.now().isoformat()
                self._save_config()

                return {
                    "success": True,
                    "message": "自动调整完成",
                    "old_thresholds": current_thresholds,
                    "new_thresholds": suggested_thresholds,
                    "adjustments": suggestions,
                    "analysis": analysis_result.get("analysis", {})
                }

            except Exception as e:
                return {
                    "success": False,
                    "message": f"自动调整失败: {e}"
                }
        else:
            return {
                "success": True,
                "message": "模拟模式：建议的调整",
                "suggested_thresholds": suggested_thresholds,
                "suggestions": suggestions,
                "analysis": analysis_result.get("analysis", {})
            }

    def force_adjust_threshold(self, level: str, value: int) -> Dict[str, Any]:
        """强制调整指定阈值

        Args:
            level: 阈值级别 (warning/critical/emergency)
            value: 新阈值

        Returns:
            调整结果
        """
        if not self.trigger_engine:
            return {
                "success": False,
                "message": "阈值触发引擎未加载"
            }

        try:
            old_value = self.trigger_engine.get_thresholds().get(level)
            self.trigger_engine.set_threshold(level, value)

            # 记录手动调整
            self._add_adjustment_record(
                "manual_adjust",
                old_value,
                value,
                level,
                "手动调整"
            )

            return {
                "success": True,
                "message": f"{level}阈值已从{old_value}调整为{value}",
                "old_value": old_value,
                "new_value": value
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"调整失败: {e}"
            }

    def get_adjustment_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取调整历史"""
        return self.adjustment_log[-limit:]

    def get_analysis_summary(self) -> Dict[str, Any]:
        """获取分析摘要"""
        if not self.analysis_engine:
            return {
                "success": False,
                "message": "分析引擎未加载"
            }

        return self.analysis_engine.comprehensive_analysis()

    def enable_auto_adjust(self):
        """启用自动调整"""
        self.config["enabled"] = True
        self._save_config()

    def disable_auto_adjust(self):
        """禁用自动调整"""
        self.config["enabled"] = False
        self._save_config()

    def reset_stability_counter(self):
        """重置稳定性计数器"""
        self.config["stability_counter"] = 0
        self.config["consecutive_triggers"] = 0
        self._save_config()

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        health = {
            "engine": "EvolutionHealthThresholdAutoAdjustEngine",
            "version": self.VERSION,
            "healthy": True,
            "components": {}
        }

        # 检查触发引擎
        if self.trigger_engine:
            health["components"]["trigger_engine"] = "ok"
        else:
            health["components"]["trigger_engine"] = "not_loaded"
            health["healthy"] = False

        # 检查分析引擎
        if self.analysis_engine:
            health["components"]["analysis_engine"] = "ok"
        else:
            health["components"]["analysis_engine"] = "not_loaded"

        # 检查配置
        health["components"]["auto_adjust_enabled"] = self.config.get("enabled", True)
        health["components"]["config"] = "ok"

        return health


def get_auto_adjust_engine() -> ThresholdAutoAdjustEngine:
    """获取自动调整引擎单例"""
    return ThresholdAutoAdjustEngine()


def main():
    """主函数：处理命令行调用"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python evolution_health_threshold_auto_adjust_engine.py analyze")
        print("  python evolution_health_threshold_auto_adjust_engine.py auto_adjust")
        print("  python evolution_health_threshold_auto_adjust_engine.py dry_run")
        print("  python evolution_health_threshold_auto_adjust_engine.py set <level> <value>")
        print("  python evolution_health_threshold_auto_adjust_engine.py history")
        print("  python evolution_health_threshold_auto_adjust_engine.py summary")
        print("  python evolution_health_threshold_auto_adjust_engine.py enable")
        print("  python evolution_health_threshold_auto_adjust_engine.py disable")
        print("  python evolution_health_threshold_auto_adjust_engine.py health")
        return

    engine = get_auto_adjust_engine()
    command = sys.argv[1].lower()

    if command == "analyze":
        result = engine.analyze_and_suggest()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "auto_adjust":
        result = engine.execute_auto_adjust(dry_run=False)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "dry_run":
        result = engine.execute_auto_adjust(dry_run=True)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "set" and len(sys.argv) == 4:
        level = sys.argv[2].lower()
        try:
            value = int(sys.argv[3])
            result = engine.force_adjust_threshold(level, value)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        except ValueError as e:
            print(f"设置失败: {e}")

    elif command == "history":
        result = engine.get_adjustment_history()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "summary":
        result = engine.get_analysis_summary()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "enable":
        engine.enable_auto_adjust()
        print("已启用自动调整")

    elif command == "disable":
        engine.disable_auto_adjust()
        print("已禁用自动调整")

    elif command == "health":
        result = engine.health_check()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {command}")
        print("可用命令: analyze, auto_adjust, dry_run, set, history, summary, enable, disable, health")


if __name__ == "__main__":
    main()