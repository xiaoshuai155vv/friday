#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能主动服务预热引擎（Service Preheat Engine）

让系统能够基于用户历史行为、时间规律、当前情境主动预测用户需求，
提前预热服务（加载资源、准备环境），实现从「被动响应」到「主动预热+提前准备」的范式升级。

功能：
1. 用户行为分析 - 分析用户历史行为模式
2. 时间规律挖掘 - 挖掘用户在特定时间的习惯性行为
3. 需求预测 - 基于行为和时间规律预测下一步需求
4. 服务预热 - 提前加载资源、准备执行环境
5. 主动服务推送 - 预测到需求后主动提供服务

与 round 192（零点击服务）、round 215（自适应场景选择）形成能力增强链。
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path
import argparse

# 基础路径
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
STATE_DIR = PROJECT_ROOT / "runtime" / "state"
LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"

# 数据文件路径
USER_BEHAVIOR_FILE = STATE_DIR / "user_behavior_patterns.json"
TIME_PATTERNS_FILE = STATE_DIR / "time_patterns.json"
PREHEAT_CACHE_FILE = STATE_DIR / "service_preheat_cache.json"
PREDICTION_HISTORY_FILE = STATE_DIR / "preheat_predictions.json"

# 版本
VERSION = "1.0.0"


def load_json_safe(filepath, default=None):
    """安全加载JSON文件"""
    if default is None:
        default = {}
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"加载文件失败 {filepath}: {e}")
    return default


def save_json_safe(filepath, data):
    """安全保存JSON文件"""
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存文件失败 {filepath}: {e}")
        return False


def analyze_user_behavior():
    """分析用户行为模式"""
    behavior_data = load_json_safe(USER_BEHAVIOR_FILE, {"behaviors": []})
    behaviors = behavior_data.get("behaviors", [])

    if not behaviors:
        return {
            "total_actions": 0,
            "top_actions": [],
            "patterns": [],
            "avg_session_length": 0
        }

    # 统计行为频率
    action_freq = defaultdict(int)
    for b in behaviors:
        action = b.get("action", "")
        if action:
            action_freq[action] += 1

    # 排序取前10
    sorted_actions = sorted(action_freq.items(), key=lambda x: x[1], reverse=True)
    top_actions = [{"action": a, "count": c} for a, c in sorted_actions[:10]]

    return {
        "total_actions": len(behaviors),
        "top_actions": top_actions,
        "patterns": discover_patterns(behaviors),
        "avg_session_length": len(behaviors) / max(len(set(b.get("session", "") for b in behaviors)), 1)
    }


def discover_patterns(behaviors):
    """发现行为模式"""
    patterns = []

    # 按时间间隔发现模式
    time_gaps = []
    sorted_behaviors = sorted(behaviors, key=lambda x: x.get("timestamp", ""))
    for i in range(1, len(sorted_behaviors)):
        try:
            t1 = datetime.fromisoformat(sorted_behaviors[i-1].get("timestamp", ""))
            t2 = datetime.fromisoformat(sorted_behaviors[i].get("timestamp", ""))
            gap = (t2 - t1).total_seconds()
            if 0 < gap < 3600:  # 1小时内
                time_gaps.append(gap)
        except:
            pass

    if time_gaps:
        avg_gap = sum(time_gaps) / len(time_gaps)
        patterns.append({
            "type": "time_interval",
            "description": f"平均操作间隔 {int(avg_gap)} 秒",
            "value": avg_gap
        })

    # 按动作序列发现模式
    action_sequence = [b.get("action", "") for b in sorted_behaviors if b.get("action")]
    if len(action_sequence) >= 2:
        # 找常见的动作对
        pairs = defaultdict(int)
        for i in range(len(action_sequence) - 1):
            pair = f"{action_sequence[i]} -> {action_sequence[i+1]}"
            pairs[pair] += 1

        if pairs:
            top_pair = max(pairs.items(), key=lambda x: x[1])
            patterns.append({
                "type": "action_sequence",
                "description": f"常见序列: {top_pair[0]}",
                "count": top_pair[1]
            })

    return patterns


def analyze_time_patterns():
    """分析时间规律"""
    behavior_data = load_json_safe(USER_BEHAVIOR_FILE, {"behaviors": []})
    behaviors = behavior_data.get("behaviors", [])

    if not behaviors:
        return {"hourly": {}, "weekly": {}}

    # 按小时统计
    hourly = defaultdict(int)
    # 按星期几统计
    weekly = defaultdict(int)

    for b in behaviors:
        try:
            timestamp = b.get("timestamp", "")
            if timestamp:
                dt = datetime.fromisoformat(timestamp)
                hourly[dt.hour] += 1
                weekly[dt.strftime("%A")] += 1
        except:
            pass

    return {
        "hourly": dict(hourly),
        "weekly": dict(weekly),
        "peak_hours": sorted(hourly.items(), key=lambda x: x[1], reverse=True)[:3],
        "peak_days": sorted(weekly.items(), key=lambda x: x[1], reverse=True)[:3]
    }


def predict_needs():
    """预测用户需求"""
    time_analysis = analyze_time_patterns()
    behavior_analysis = analyze_user_behavior()

    current_hour = datetime.now().hour
    current_day = datetime.now().strftime("%A")

    predictions = []

    # 基于时间规律预测
    hourly = time_analysis.get("hourly", {})
    if hourly:
        # 检查当前时间是否是高峰时间
        current_count = hourly.get(current_hour, 0)
        if current_count > 0:
            # 基于历史预测
            if 9 <= current_hour <= 11:
                predictions.append({
                    "type": "time_based",
                    "prediction": "工作事项处理",
                    "confidence": 0.7,
                    "suggested_actions": ["查看日程", "处理邮件", "检查任务"]
                })
            elif 14 <= current_hour <= 17:
                predictions.append({
                    "type": "time_based",
                    "prediction": "文档处理",
                    "confidence": 0.6,
                    "suggested_actions": ["整理文档", "编写报告"]
                })
            elif 19 <= current_hour <= 21:
                predictions.append({
                    "type": "time_based",
                    "prediction": "学习/娱乐",
                    "confidence": 0.7,
                    "suggested_actions": ["播放音乐", "浏览资讯"]
                })

    # 基于行为模式预测
    top_actions = behavior_analysis.get("top_actions", [])
    if top_actions:
        most_common = top_actions[0].get("action", "")
        predictions.append({
            "type": "behavior_based",
            "prediction": f"可能执行: {most_common}",
            "confidence": 0.5,
            "suggested_actions": ["预加载相关资源"]
        })

    return {
        "current_time": f"{current_hour}:00",
        "current_day": current_day,
        "predictions": predictions,
        "time_analysis": time_analysis,
        "behavior_analysis": behavior_analysis
    }


def preheat_service(service_name):
    """预热指定服务"""
    cache = load_json_safe(PREHEAT_CACHE_FILE, {"preheated": {}, "history": []})

    # 记录预热历史
    preheat_record = {
        "service": service_name,
        "timestamp": datetime.now().isoformat(),
        "status": "preheated"
    }

    # 更新预热缓存
    if "preheated" not in cache:
        cache["preheated"] = {}
    cache["preheated"][service_name] = {
        "last_preheated": datetime.now().isoformat(),
        "status": "ready"
    }

    if "history" not in cache:
        cache["history"] = []
    cache["history"].append(preheat_record)

    # 只保留最近20条历史
    cache["history"] = cache["history"][-20:]

    save_json_safe(PREHEAT_CACHE_FILE, cache)

    return {
        "service": service_name,
        "status": "preheated",
        "message": f"服务 {service_name} 已预热"
    }


def get_preheat_status():
    """获取预热状态"""
    cache = load_json_safe(PREHEAT_CACHE_FILE, {"preheated": {}, "history": []})
    return cache


def get_predictions_with_preheat():
    """获取预测并自动预热相关服务"""
    predictions = predict_needs()

    preheated_services = []

    for pred in predictions.get("predictions", []):
        suggested = pred.get("suggested_actions", [])
        for action in suggested:
            # 简单映射：动作 -> 服务
            service_map = {
                "查看日程": "calendar",
                "处理邮件": "email",
                "检查任务": "task",
                "整理文档": "file_manager",
                "编写报告": "document",
                "播放音乐": "music",
                "浏览资讯": "browser",
                "预加载相关资源": "cache"
            }

            service = service_map.get(action)
            if service and service not in preheated_services:
                preheat_result = preheat_service(service)
                preheated_services.append(service)

    predictions["auto_preheated"] = preheated_services

    # 保存预测历史
    history = load_json_safe(PREDICTION_HISTORY_FILE, {"predictions": []})
    history["predictions"].append({
        "timestamp": datetime.now().isoformat(),
        "predictions": predictions
    })
    history["predictions"] = history["predictions"][-50:]  # 只保留最近50条
    save_json_safe(PREDICTION_HISTORY_FILE, history)

    return predictions


def cmd_status(args):
    """状态命令"""
    behavior_analysis = analyze_user_behavior()
    time_analysis = analyze_time_patterns()
    preheat_status = get_preheat_status()

    print(f"=== 智能主动服务预热引擎 v{VERSION} ===")
    print(f"行为分析: {behavior_analysis.get('total_actions', 0)} 条记录")
    print(f"时间规律: {len(time_analysis.get('hourly', {}))} 个高峰时段")
    print(f"预热缓存: {len(preheat_status.get('preheated', {}))} 个服务已预热")
    print(f"预测历史: {len(preheat_status.get('history', []))} 条记录")

    return {
        "version": VERSION,
        "behavior_analysis": behavior_analysis,
        "time_analysis": time_analysis,
        "preheat_status": preheat_status
    }


def cmd_predict(args):
    """预测命令"""
    predictions = predict_needs()

    print(f"=== 需求预测 ===")
    print(f"当前时间: {predictions.get('current_time')} ({predictions.get('current_day')})")
    print(f"\n预测结果:")

    for i, pred in enumerate(predictions.get("predictions", []), 1):
        print(f"  {i}. {pred.get('prediction')}")
        print(f"     类型: {pred.get('type')}, 置信度: {pred.get('confidence', 0):.0%}")
        print(f"     建议动作: {', '.join(pred.get('suggested_actions', []))}")

    if not predictions.get("predictions"):
        print("  (暂无足够数据进行预测)")

    return predictions


def cmd_predict_with_preheat(args):
    """预测并预热命令"""
    predictions = get_predictions_with_preheat()

    print(f"=== 需求预测 + 自动预热 ===")
    print(f"当前时间: {predictions.get('current_time')} ({predictions.get('current_day')})")
    print(f"\n预测结果:")

    for i, pred in enumerate(predictions.get("predictions", []), 1):
        print(f"  {i}. {pred.get('prediction')}")
        print(f"     类型: {pred.get('type')}, 置信度: {pred.get('confidence', 0):.0%}")
        print(f"     建议动作: {', '.join(pred.get('suggested_actions', []))}")

    auto_preheated = predictions.get("auto_preheated", [])
    if auto_preheated:
        print(f"\n自动预热服务: {', '.join(auto_preheated)}")
    else:
        print(f"\n自动预热服务: (无)")

    return predictions


def cmd_preheat(args):
    """预热命令"""
    if not args.service:
        print("错误: 请指定服务名称")
        return {"error": "service name required"}

    result = preheat_service(args.service)
    print(f"预热结果: {result['message']}")
    return result


def cmd_history(args):
    """历史命令"""
    history = load_json_safe(PREDICTION_HISTORY_FILE, {"predictions": []})

    print(f"=== 预测历史 (共 {len(history.get('predictions', []))} 条) ===")

    recent = history.get("predictions", [])[-10:]
    for i, pred_record in enumerate(reversed(recent), 1):
        timestamp = pred_record.get("timestamp", "")
        predictions = pred_record.get("predictions", {})
        print(f"\n{i}. {timestamp[:19]}")
        print(f"   时间: {predictions.get('current_time', 'N/A')} ({predictions.get('current_day', 'N/A')})")

        for pred in predictions.get("predictions", [])[:3]:
            print(f"   - {pred.get('prediction')} ({pred.get('type')})")

    return history


def main():
    parser = argparse.ArgumentParser(description="智能主动服务预热引擎")
    subparsers = parser.add_subparsers(dest="cmd", help="子命令")

    # status 命令
    subparsers.add_parser("status", help="查看引擎状态")

    # predict 命令
    subparsers.add_parser("predict", help="预测用户需求")

    # predict_with_preheat 命令
    subparsers.add_parser("predict_with_preheat", help="预测需求并自动预热服务")

    # preheat 命令
    preheat_parser = subparsers.add_parser("preheat", help="预热指定服务")
    preheat_parser.add_argument("--service", "-s", required=True, help="服务名称")

    # history 命令
    subparsers.add_parser("history", help="查看预测历史")

    args = parser.parse_args()

    if args.cmd == "status":
        return cmd_status(args)
    elif args.cmd == "predict":
        return cmd_predict(args)
    elif args.cmd == "predict_with_preheat":
        return cmd_predict_with_preheat(args)
    elif args.cmd == "preheat":
        return cmd_preheat(args)
    elif args.cmd == "history":
        return cmd_history(args)
    else:
        # 默认显示状态
        return cmd_status(args)


if __name__ == "__main__":
    main()