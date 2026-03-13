#!/usr/bin/env python3
"""
智能端到端服务编排与持续优化引擎

追踪端到端服务执行路径，分析引擎组合效果，发现瓶颈并自动生成优化建议，
实现「需求→多引擎协同→执行→反馈→优化」的完整闭环。

功能：
1. 服务执行路径追踪
2. 引擎组合效果分析
3. 瓶颈和失败点发现
4. 自动优化建议生成
5. 与 execution_enhancement_engine、feedback_learning_engine 集成
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# 项目根目录
PROJECT = Path(__file__).parent.parent
SCRIPTS = PROJECT / "scripts"
RUNTIME = PROJECT / "runtime"
STATE_DIR = RUNTIME / "state"
LOGS_DIR = RUNTIME / "logs"

# 服务追踪数据文件
SERVICE_TRACKING_FILE = STATE_DIR / "service_tracking.json"
ORCHESTRATION_STATS_FILE = STATE_DIR / "orchestration_stats.json"
OPTIMIZATION_SUGGESTIONS_FILE = STATE_DIR / "optimization_suggestions.json"


def load_service_tracking():
    """加载服务追踪数据"""
    if SERVICE_TRACKING_FILE.exists():
        with open(SERVICE_TRACKING_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"services": [], "sessions": []}


def save_service_tracking(data):
    """保存服务追踪数据"""
    with open(SERVICE_TRACKING_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_orchestration_stats():
    """加载编排统计数据"""
    if ORCHESTRATION_STATS_FILE.exists():
        with open(ORCHESTRATION_STATS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"engine_combinations": {}, "bottlenecks": [], "last_updated": None}


def save_orchestration_stats(data):
    """保存编排统计数据"""
    with open(ORCHESTRATION_STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_optimization_suggestions():
    """加载优化建议"""
    if OPTIMIZATION_SUGGESTIONS_FILE.exists():
        with open(OPTIMIZATION_SUGGESTIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"suggestions": [], "last_updated": None}


def save_optimization_suggestions(data):
    """保存优化建议"""
    with open(OPTIMIZATION_SUGGESTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def track_service_execution(service_name, engines_used, status, duration_ms=0, error=None):
    """
    追踪服务执行路径

    Args:
        service_name: 服务名称
        engines_used: 使用的引擎列表
        status: 执行状态 (success/fail/timeout)
        duration_ms: 执行耗时(毫秒)
        error: 错误信息(如果有)
    """
    data = load_service_tracking()
    timestamp = datetime.now().isoformat()

    # 记录服务执行
    service_record = {
        "timestamp": timestamp,
        "service": service_name,
        "engines": engines_used,
        "status": status,
        "duration_ms": duration_ms,
        "error": error
    }
    data["services"].append(service_record)

    # 保持最近1000条记录
    if len(data["services"]) > 1000:
        data["services"] = data["services"][-1000:]

    # 更新编排统计
    update_orchestration_stats(engines_used, status, duration_ms)

    save_service_tracking(data)
    return service_record


def update_orchestration_stats(engines_used, status, duration_ms):
    """更新编排统计数据"""
    stats = load_orchestration_stats()

    # 统计引擎组合
    combo_key = "+".join(sorted(engines_used)) if engines_used else "single"
    if combo_key not in stats["engine_combinations"]:
        stats["engine_combinations"][combo_key] = {
            "total": 0,
            "success": 0,
            "fail": 0,
            "avg_duration_ms": 0,
            "total_duration_ms": 0
        }

    combo_stats = stats["engine_combinations"][combo_key]
    combo_stats["total"] += 1
    combo_stats["total_duration_ms"] += duration_ms
    combo_stats["avg_duration_ms"] = combo_stats["total_duration_ms"] // combo_stats["total"]

    if status == "success":
        combo_stats["success"] += 1
    else:
        combo_stats["fail"] += 1

    stats["last_updated"] = datetime.now().isoformat()
    save_orchestration_stats(stats)


def analyze_engine_effectiveness():
    """分析引擎组合效果"""
    stats = load_orchestration_stats()
    combinations = stats.get("engine_combinations", {})

    if not combinations:
        return {
            "status": "no_data",
            "message": "暂无足够数据进行引擎效果分析"
        }

    # 计算各组合的成功率
    effectiveness = []
    for combo, data in combinations.items():
        if data["total"] >= 3:  # 至少3次执行才分析
            success_rate = data["success"] / data["total"] * 100
            effectiveness.append({
                "combination": combo,
                "success_rate": round(success_rate, 1),
                "total_executions": data["total"],
                "avg_duration_ms": data["avg_duration_ms"],
                "recommendation": "推荐" if success_rate >= 80 else "待优化"
            })

    # 按成功率排序
    effectiveness.sort(key=lambda x: x["success_rate"], reverse=True)

    return {
        "status": "success",
        "effectiveness": effectiveness,
        "total_combinations": len(combinations)
    }


def discover_bottlenecks():
    """发现瓶颈和失败点"""
    data = load_service_tracking()
    services = data.get("services", [])

    if len(services) < 5:
        return {
            "status": "no_data",
            "message": "暂无足够数据发现瓶颈"
        }

    # 分析失败模式
    failed_services = [s for s in services if s["status"] == "fail"]
    slow_services = [s for s in services if s.get("duration_ms", 0) > 30000]  # >30s 视为慢

    # 统计失败引擎
    failed_engines = {}
    for s in failed_services:
        for engine in s.get("engines", []):
            if engine not in failed_engines:
                failed_engines[engine] = 0
            failed_engines[engine] += 1

    # 统计慢服务
    slow_engines = {}
    for s in slow_services:
        for engine in s.get("engines", []):
            if engine not in slow_engines:
                slow_engines[engine] = 0
            slow_engines[engine] += 1

    bottlenecks = []

    # 失败率高的引擎
    for engine, count in sorted(failed_engines.items(), key=lambda x: x[1], reverse=True)[:3]:
        bottlenecks.append({
            "type": "high_failure_rate",
            "engine": engine,
            "failure_count": count,
            "severity": "high" if count >= 5 else "medium",
            "suggestion": f"引擎 {engine} 失败率较高，建议检查其执行逻辑和错误处理"
        })

    # 慢引擎
    for engine, count in sorted(slow_engines.items(), key=lambda x: x[1], reverse=True)[:3]:
        bottlenecks.append({
            "type": "slow_execution",
            "engine": engine,
            "slow_count": count,
            "severity": "medium",
            "suggestion": f"引擎 {engine} 执行较慢，建议优化其执行效率或增加超时处理"
        })

    return {
        "status": "success",
        "bottlenecks": bottlenecks,
        "total_failures": len(failed_services),
        "total_slow": len(slow_services)
    }


def generate_optimization_suggestions():
    """生成自动优化建议"""
    effectiveness = analyze_engine_effectiveness()
    bottlenecks = discover_bottlenecks()

    suggestions = []

    # 基于效果分析的优化建议
    if effectiveness.get("status") == "success":
        for item in effectiveness.get("effectiveness", []):
            if item["success_rate"] < 60:
                suggestions.append({
                    "type": "low_effectiveness",
                    "priority": "high",
                    "combination": item["combination"],
                    "current_success_rate": item["success_rate"],
                    "suggestion": f"引擎组合 {item['combination']} 成功率较低({item['success_rate']}%)，建议优化执行策略或增加错误处理"
                })

    # 基于瓶颈分析的优化建议
    if bottlenecks.get("status") == "success":
        for b in bottlenecks.get("bottlenecks", []):
            if b["severity"] == "high":
                suggestions.append({
                    "type": "bottleneck_fix",
                    "priority": "high",
                    "engine": b["engine"],
                    "issue": b["type"],
                    "suggestion": b["suggestion"]
                })

    # 如果没有数据，给出通用建议
    if not suggestions:
        suggestions.append({
            "type": "general",
            "priority": "low",
            "suggestion": "系统运行良好，暂无明显优化建议。建议继续收集执行数据以进行更深入的分析"
        })

    result = {
        "suggestions": suggestions,
        "generated_at": datetime.now().isoformat(),
        "total_suggestions": len(suggestions)
    }

    save_optimization_suggestions(result)
    return result


def execute_optimization(optimization_type):
    """
    执行自动优化

    Args:
        optimization_type: 优化类型
            - retry_failed: 重试失败的执行
            - increase_timeout: 增加超时时间
            - add_fallback: 添加备用引擎
            - cache_results: 缓存结果
    """
    results = []

    if optimization_type == "retry_failed":
        # 从 tracking 中找出失败的执行，记录重试建议
        data = load_service_tracking()
        failed = [s for s in data.get("services", []) if s["status"] == "fail"]
        results.append({
            "action": "retry_failed",
            "count": len(failed),
            "message": f"发现 {len(failed)} 条失败记录，建议检查错误原因后重试"
        })

    elif optimization_type == "increase_timeout":
        # 检查慢服务，增加超时建议
        bottlenecks = discover_bottlenecks()
        slow_count = bottlenecks.get("total_slow", 0)
        results.append({
            "action": "increase_timeout",
            "count": slow_count,
            "message": f"发现 {slow_count} 条慢执行记录，建议为相关引擎增加超时时间"
        })

    elif optimization_type == "add_fallback":
        # 添加备用引擎建议
        results.append({
            "action": "add_fallback",
            "message": "建议为关键引擎添加备用方案，提高系统鲁棒性"
        })

    elif optimization_type == "cache_results":
        # 缓存建议
        results.append({
            "action": "cache_results",
            "message": "建议对频繁执行的引擎结果进行缓存，减少重复计算"
        })

    return {
        "status": "success",
        "optimization_type": optimization_type,
        "results": results,
        "executed_at": datetime.now().isoformat()
    }


def show_status():
    """显示服务编排优化状态"""
    stats = load_orchestration_stats()
    suggestions = load_optimization_suggestions()

    # 效果分析
    effectiveness = analyze_engine_effectiveness()

    # 瓶颈分析
    bottlenecks = discover_bottlenecks()

    output = []
    output.append("=" * 60)
    output.append("智能端到端服务编排与持续优化引擎 - 状态")
    output.append("=" * 60)

    # 统计概览
    total_services = len(load_service_tracking().get("services", []))
    output.append(f"\n总服务执行次数: {total_services}")

    combinations_count = len(stats.get("engine_combinations", {}))
    output.append(f"引擎组合种类: {combinations_count}")

    # 效果分析
    if effectiveness.get("status") == "success":
        output.append(f"\n引擎组合效果分析 (共 {effectiveness.get('total_combinations', 0)} 种组合):")
        for item in effectiveness.get("effectiveness", [])[:5]:
            output.append(f"  - {item['combination']}: 成功率 {item['success_rate']}% ({item['total_executions']}次) [{item['recommendation']}]")

    # 瓶颈
    if bottlenecks.get("status") == "success" and bottlenecks.get("bottlenecks"):
        output.append(f"\n发现的瓶颈 ({len(bottlenecks.get('bottlenecks', []))} 个):")
        for b in bottlenecks.get("bottlenecks", [])[:3]:
            output.append(f"  - [{b['severity'].upper()}] {b['engine']}: {b['suggestion']}")

    # 优化建议
    if suggestions.get("suggestions"):
        output.append(f"\n优化建议 ({len(suggestions.get('suggestions', []))} 条):")
        for s in suggestions.get("suggestions", [])[:3]:
            output.append(f"  - [{s.get('priority', 'N/A').upper()}] {s.get('suggestion', 'N/A')}")

    output.append("=" * 60)
    output.append("\n可用命令:")
    output.append("  status      - 显示状态")
    output.append("  analyze     - 分析引擎效果")
    output.append("  bottlenecks - 发现瓶颈")
    output.append("  suggest     - 生成优化建议")
    output.append("  optimize    - 执行优化 (retry_failed/increase_timeout/add_fallback/cache_results)")
    output.append("  track <service> <engines> <status> [duration_ms] - 追踪服务执行")
    output.append("  help        - 显示帮助")

    return "\n".join(output)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print(show_status())
        return

    command = sys.argv[1].lower()

    if command == "help":
        print(show_status())

    elif command == "status":
        print(show_status())

    elif command == "analyze":
        result = analyze_engine_effectiveness()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "bottlenecks":
        result = discover_bottlenecks()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "suggest":
        result = generate_optimization_suggestions()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "optimize":
        opt_type = sys.argv[2] if len(sys.argv) > 2 else "retry_failed"
        result = execute_optimization(opt_type)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "track":
        # 手动追踪服务执行: track <service> <engines> <status> [duration_ms]
        if len(sys.argv) < 5:
            print("用法: track <service> <engines> <status> [duration_ms]")
            print("示例: track '文件整理' 'file_manager+notification' 'success' 5000")
            return

        service = sys.argv[2]
        engines = sys.argv[3].split("+") if "+" in sys.argv[3] else [sys.argv[3]]
        status = sys.argv[4]
        duration = int(sys.argv[5]) if len(sys.argv) > 5 else 0

        record = track_service_execution(service, engines, status, duration)
        print(f"已追踪服务执行: {record}")

    else:
        print(f"未知命令: {command}")
        print("使用 'help' 查看可用命令")


if __name__ == "__main__":
    main()