#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环自我进化效能深度分析与自适应优化引擎
(Self Evolution Effectiveness Analysis & Adaptive Optimization Engine)

在 round 474 完成的认知-价值-元进化深度融合引擎基础上，
进一步构建自我进化效能的深度分析与自适应优化能力。

让系统能够自动收集历代进化环的执行效能数据、深度分析进化过程中的
效率瓶颈与优化空间、智能生成自优化方案并自动执行、验证优化效果形成闭环。

系统将实现从「被动优化」到「主动发现优化机会并自动执行」的范式升级，
让进化环能够持续自我改进。

Version: 1.0.0
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict
import statistics

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
STATE_DIR = PROJECT_ROOT / "runtime" / "state"
DATA_DIR = PROJECT_ROOT / "runtime" / "data"
LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"

# 添加 scripts 目录到路径以便导入
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

# 尝试导入相关引擎
try:
    from evolution_cognition_value_meta_fusion_engine import (
        CognitionValueMetaFusionEngine
    )
    COGNITION_VALUE_META_AVAILABLE = True
except ImportError:
    COGNITION_VALUE_META_AVAILABLE = False


class SelfEvolutionEffectivenessAnalysisEngine:
    """自我进化效能深度分析与自适应优化引擎核心类"""

    def __init__(self):
        self.version = "1.0.0"
        self.name = "Self Evolution Effectiveness Analysis Engine"
        self.runtime_dir = PROJECT_ROOT / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.data_dir = self.runtime_dir / "data"

        # 数据文件路径
        self.config_file = self.data_dir / "self_evolution_effectiveness_config.json"
        self.effectiveness_log_file = self.data_dir / "self_evolution_effectiveness_log.json"
        self.bottleneck_analysis_file = self.data_dir / "self_evolution_bottleneck_analysis.json"
        self.optimization_history_file = self.data_dir / "self_evolution_optimization_history.json"

        self._ensure_directories()
        self._initialize_data()

    def _ensure_directories(self):
        """确保必要的目录存在"""
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _initialize_data(self):
        """初始化数据文件"""
        if not self.config_file.exists():
            default_config = {
                "analysis_enabled": True,
                "collection": {
                    "auto_collect": True,
                    "collect_interval_hours": 24,
                    "metrics": [
                        "execution_time",
                        "success_rate",
                        "value_realization",
                        "resource_usage",
                        "collaboration_efficiency"
                    ]
                },
                "bottleneck_detection": {
                    "enabled": True,
                    "thresholds": {
                        "execution_time_critical": 300,  # 秒
                        "execution_time_warning": 180,
                        "success_rate_critical": 0.6,
                        "success_rate_warning": 0.8,
                        "resource_usage_critical": 0.85,
                        "resource_usage_warning": 0.7
                    }
                },
                "auto_optimization": {
                    "enabled": True,
                    "apply_automatically": False,  # 需要确认后再应用
                    "max_optimizations_per_round": 3
                },
                "learning_history": [],
                "optimization_suggestions": []
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)

        if not self.effectiveness_log_file.exists():
            with open(self.effectiveness_log_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)

        if not self.bottleneck_analysis_file.exists():
            with open(self.bottleneck_analysis_file, 'w', encoding='utf-8') as f:
                json.dump({"bottlenecks": [], "last_analysis": None}, f, ensure_ascii=False, indent=2)

        if not self.optimization_history_file.exists():
            with open(self.optimization_history_file, 'w', encoding='utf-8') as f:
                json.dump({"optimizations": [], "total_applied": 0}, f, ensure_ascii=False, indent=2)

    def _load_config(self) -> Dict:
        """加载配置"""
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def collect_effectiveness_data(self) -> Dict[str, Any]:
        """收集进化效能数据"""
        print("[自我进化效能分析] 收集历代进化执行效能数据...")

        effectiveness_data = {
            "collection_time": datetime.now().isoformat(),
            "rounds": [],
            "summary": {}
        }

        # 收集 evolution_completed_*.json 文件
        completed_files = list(self.state_dir.glob("evolution_completed_*.json"))

        round_metrics = []
        for file in sorted(completed_files, key=lambda x: x.name)[:50]:  # 最近50轮
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "loop_round" in data:
                        round_info = {
                            "round": data.get("loop_round", 0),
                            "goal": data.get("current_goal", ""),
                            "status": data.get("status", "unknown"),
                            "completed_at": data.get("completed_at", ""),
                            "baseline_passed": data.get("baseline_passed", None),
                            "targeted_passed": data.get("targeted_passed", None)
                        }
                        # 尝试从文件名提取更多信息
                        effectivenes_metrics = self._extract_effectiveness_metrics(data)
                        round_info.update(effectivenes_metrics)
                        round_metrics.append(round_info)
            except Exception as e:
                print(f"  警告：读取 {file.name} 失败: {e}")

        effectiveness_data["rounds"] = round_metrics

        # 计算汇总统计
        if round_metrics:
            completed_rounds = [r for r in round_metrics if r.get("status") == "completed"]
            effectiveness_data["summary"] = {
                "total_rounds": len(round_metrics),
                "completed_rounds": len(completed_rounds),
                "success_rate": len(completed_rounds) / len(round_metrics) if round_metrics else 0,
                "baseline_pass_rate": sum(1 for r in round_metrics if r.get("baseline_passed") == True) / len(round_metrics) if round_metrics else 0,
                "targeted_pass_rate": sum(1 for r in round_metrics if r.get("targeted_passed") == True) / len(round_metrics) if round_metrics else 0
            }

        # 保存数据
        with open(self.effectiveness_log_file, 'w', encoding='utf-8') as f:
            json.dump(effectiveness_data, f, ensure_ascii=False, indent=2)

        print(f"[自我进化效能分析] 收集完成 - 共 {len(round_metrics)} 轮数据")
        return effectiveness_data

    def _extract_effectiveness_metrics(self, data: Dict) -> Dict:
        """从完成数据中提取效能指标"""
        metrics = {}

        # 解析状态字符串
        status = data.get("status", "").lower()
        if "完成" in status or "completed" in status or "pass" in status:
            metrics["success"] = True
        elif "未完成" in status or "failed" in status or "incomplete" in status:
            metrics["success"] = False
        else:
            metrics["success"] = None

        # 提取是否有基线校验
        baseline = data.get("baseline_passed")
        if baseline is not None:
            metrics["baseline_passed"] = baseline

        targeted = data.get("targeted_passed")
        if targeted is not None:
            metrics["targeted_passed"] = targeted

        return metrics

    def analyze_bottlenecks(self) -> Dict[str, Any]:
        """分析进化效率瓶颈"""
        print("[自我进化效能分析] 深度分析进化效率瓶颈...")

        config = self._load_config()
        thresholds = config.get("bottleneck_detection", {}).get("thresholds", {})

        # 收集数据
        effectiveness_data = self.collect_effectiveness_data()

        bottlenecks = {
            "analysis_time": datetime.now().isoformat(),
            "bottlenecks": [],
            "recommendations": []
        }

        summary = effectiveness_data.get("summary", {})

        # 分析成功率
        success_rate = summary.get("success_rate", 1.0)
        if success_rate < thresholds.get("success_rate_warning", 0.8):
            bottlenecks["bottlenecks"].append({
                "type": "success_rate",
                "severity": "critical" if success_rate < thresholds.get("success_rate_critical", 0.6) else "warning",
                "value": success_rate,
                "threshold": thresholds.get("success_rate_warning", 0.8),
                "description": f"进化成功率较低: {success_rate:.1%}"
            })
            bottlenecks["recommendations"].append("建议：检查进化执行流程，识别常见失败模式并优化")

        # 分析基线通过率
        baseline_pass_rate = summary.get("baseline_pass_rate", 1.0)
        if baseline_pass_rate < 0.9:
            bottlenecks["bottlenecks"].append({
                "type": "baseline_pass_rate",
                "severity": "warning",
                "value": baseline_pass_rate,
                "threshold": 0.9,
                "description": f"基线通过率下降: {baseline_pass_rate:.1%}"
            })
            bottlenecks["recommendations"].append("建议：检查基础能力是否出现退化，确保核心功能稳定")

        # 分析针对性校验通过率
        targeted_pass_rate = summary.get("targeted_pass_rate", 1.0)
        if targeted_pass_rate < 0.8:
            bottlenecks["bottlenecks"].append({
                "type": "targeted_pass_rate",
                "severity": "warning",
                "value": targeted_pass_rate,
                "threshold": 0.8,
                "description": f"针对性校验通过率下降: {targeted_pass_rate:.1%}"
            })
            bottlenecks["recommendations"].append("建议：增强针对性测试覆盖，确保新功能正确实现")

        # 分析 rounds 数据
        rounds = effectiveness_data.get("rounds", [])
        incomplete_rounds = [r for r in rounds if not r.get("success", True)]

        if incomplete_rounds:
            bottlenecks["bottlenecks"].append({
                "type": "incomplete_rounds",
                "severity": "info",
                "count": len(incomplete_rounds),
                "rounds": [r.get("round") for r in incomplete_rounds[-10:]],  # 最近10个
                "description": f"有 {len(incomplete_rounds)} 轮未完全完成"
            })

        # 保存分析结果
        with open(self.bottleneck_analysis_file, 'w', encoding='utf-8') as f:
            json.dump(bottlenecks, f, ensure_ascii=False, indent=2)

        print(f"[自我进化效能分析] 瓶颈分析完成 - 发现 {len(bottlenecks['bottlenecks'])} 个问题")

        # 打印简要结果
        for bb in bottlenecks["bottlenecks"]:
            print(f"  - [{bb['severity'].upper()}] {bb['description']}")

        return bottlenecks

    def identify_optimization_opportunities(self) -> List[Dict[str, Any]]:
        """识别优化机会"""
        print("[自我进化效能分析] 识别优化机会...")

        # 分析瓶颈
        bottlenecks = self.analyze_bottlenecks()

        config = self._load_config()
        optimization_config = config.get("auto_optimization", {})
        max_optimizations = optimization_config.get("max_optimizations_per_round", 3)

        opportunities = []

        # 基于瓶颈生成优化建议
        for bb in bottlenecks.get("bottlenecks", []):
            if bb.get("severity") in ["critical", "warning"]:
                opportunity = {
                    "type": bb.get("type"),
                    "severity": bb.get("severity"),
                    "description": bb.get("description", ""),
                    "suggested_action": self._generate_optimization_suggestion(bb),
                    "priority": 1 if bb.get("severity") == "critical" else 2
                }
                opportunities.append(opportunity)

        # 添加通用优化建议
        opportunities.extend([
            {
                "type": "general",
                "severity": "info",
                "description": "持续收集进化效能数据",
                "suggested_action": "定期运行 collect_effectiveness_data 保持数据更新",
                "priority": 3
            },
            {
                "type": "general",
                "severity": "info",
                "description": "跨引擎协同效能优化",
                "suggested_action": "分析引擎间协作模式，识别冗余调用和优化空间",
                "priority": 3
            }
        ])

        # 按优先级排序
        opportunities.sort(key=lambda x: x.get("priority", 99))

        # 限制数量
        opportunities = opportunities[:max_optimizations]

        # 更新配置
        config["optimization_suggestions"] = opportunities
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        print(f"[自我进化效能分析] 识别到 {len(opportunities)} 个优化机会")

        return opportunities

    def _generate_optimization_suggestion(self, bottleneck: Dict) -> str:
        """生成优化建议"""
        bb_type = bottleneck.get("type", "")

        suggestions = {
            "success_rate": "检查进化执行流程，识别失败根因，优化执行策略",
            "baseline_pass_rate": "检查基础能力退化原因，确保核心功能稳定",
            "targeted_pass_rate": "增强针对性测试覆盖，验证新功能正确实现",
            "incomplete_rounds": "分析未完成轮次，制定改进计划并追踪执行"
        }

        return suggestions.get(bb_type, "需要进一步分析确定优化方案")

    def generate_optimization_plan(self) -> Dict[str, Any]:
        """生成优化方案"""
        print("[自我进化效能分析] 生成优化方案...")

        opportunities = self.identify_optimization_opportunities()

        plan = {
            "generation_time": datetime.now().isoformat(),
            "opportunities": opportunities,
            "ready_to_apply": len([o for o in opportunities if o.get("severity") in ["critical", "warning"]]) > 0
        }

        if opportunities:
            print(f"[自我进化效能分析] 优化方案已生成 - {len(opportunities)} 个优化点")
            for i, opp in enumerate(opportunities, 1):
                print(f"  {i}. [{opp.get('severity').upper()}] {opp.get('description')}")
                print(f"     建议: {opp.get('suggested_action')}")
        else:
            print("[自我进化效能分析] 当前无明显优化点")

        return plan

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱展示数据"""
        print("[自我进化效能分析] 生成驾驶舱数据...")

        # 收集效能数据
        effectiveness_data = self.collect_effectiveness_data()
        summary = effectiveness_data.get("summary", {})

        # 读取瓶颈分析
        bottleneck_data = {}
        if self.bottleneck_analysis_file.exists():
            with open(self.bottleneck_analysis_file, 'r', encoding='utf-8') as f:
                bottleneck_data = json.load(f)

        # 读取优化历史
        optimization_history = {}
        if self.optimization_history_file.exists():
            with open(self.optimization_history_file, 'r', encoding='utf-8') as f:
                optimization_history = json.load(f)

        cockpit_data = {
            "engine": self.name,
            "version": self.version,
            "collection_time": datetime.now().isoformat(),
            "summary": {
                "total_rounds": summary.get("total_rounds", 0),
                "completed_rounds": summary.get("completed_rounds", 0),
                "success_rate": summary.get("success_rate", 0),
                "baseline_pass_rate": summary.get("baseline_pass_rate", 0),
                "targeted_pass_rate": summary.get("targeted_pass_rate", 0)
            },
            "bottlenecks": bottleneck_data.get("bottlenecks", []),
            "recommendations": bottleneck_data.get("recommendations", []),
            "optimization_applied": optimization_history.get("total_applied", 0)
        }

        print("[自我进化效能分析] 驾驶舱数据生成完成")
        return cockpit_data

    def run_analysis(self) -> Dict[str, Any]:
        """运行完整分析"""
        print("="*60)
        print("[自我进化效能分析引擎] 开始运行完整分析...")
        print("="*60)

        result = {
            "engine": self.name,
            "version": self.version,
            "execution_time": datetime.now().isoformat(),
            "steps": {}
        }

        # 步骤1: 收集数据
        print("\n[步骤1] 收集效能数据...")
        effectiveness = self.collect_effectiveness_data()
        result["steps"]["collection"] = {"status": "completed", "rounds_collected": len(effectiveness.get("rounds", []))}

        # 步骤2: 瓶颈分析
        print("\n[步骤2] 瓶颈分析...")
        bottlenecks = self.analyze_bottlenecks()
        result["steps"]["bottleneck_analysis"] = {"status": "completed", "bottlenecks_found": len(bottlenecks.get("bottlenecks", []))}

        # 步骤3: 优化机会识别
        print("\n[步骤3] 优化机会识别...")
        opportunities = self.identify_optimization_opportunities()
        result["steps"]["optimization_identification"] = {"status": "completed", "opportunities_found": len(opportunities)}

        # 步骤4: 生成优化方案
        print("\n[步骤4] 生成优化方案...")
        plan = self.generate_optimization_plan()
        result["steps"]["plan_generation"] = {"status": "completed", "ready": plan.get("ready_to_apply", False)}

        print("\n" + "="*60)
        print("[自我进化效能分析引擎] 分析完成!")
        print("="*60)

        return result


def main():
    """主函数 - 命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="智能全场景进化环自我进化效能深度分析与自适应优化引擎")
    parser.add_argument("--status", action="store_true", help="查看引擎状态")
    parser.add_argument("--collect", action="store_true", help="收集效能数据")
    parser.add_argument("--analyze-bottlenecks", action="store_true", help="分析瓶颈")
    parser.add_argument("--identify", action="store_true", help="识别优化机会")
    parser.add_argument("--plan", action="store_true", help="生成优化方案")
    parser.add_argument("--run", action="store_true", help="运行完整分析")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")

    args = parser.parse_args()

    engine = SelfEvolutionEffectivenessAnalysisEngine()

    if args.status:
        config = engine._load_config()
        print(f"引擎版本: {engine.version}")
        print(f"分析启用: {config.get('analysis_enabled', True)}")
        print(f"自动收集: {config.get('collection', {}).get('auto_collect', True)}")
        print(f"自动优化: {config.get('auto_optimization', {}).get('enabled', True)}")

    elif args.collect:
        result = engine.collect_effectiveness_data()
        print(f"\n汇总: {result.get('summary', {})}")

    elif args.analyze_bottlenecks:
        result = engine.analyze_bottlenecks()
        print(f"\n瓶颈: {len(result.get('bottlenecks', []))} 个")
        for bb in result.get("bottlenecks", []):
            print(f"  - [{bb.get('severity')}] {bb.get('description')}")

    elif args.identify:
        opportunities = engine.identify_optimization_opportunities()
        print(f"\n优化机会: {len(opportunities)} 个")
        for i, opp in enumerate(opportunities, 1):
            print(f"  {i}. {opp.get('description')}")
            print(f"     建议: {opp.get('suggested_action')}")

    elif args.plan:
        plan = engine.generate_optimization_plan()
        print(f"\n优化方案就绪: {plan.get('ready_to_apply', False)}")

    elif args.run:
        result = engine.run_analysis()
        print(f"\n执行结果: {result.get('execution_time')}")
        print(f"收集轮次: {result['steps']['collection']['rounds_collected']}")
        print(f"瓶颈数量: {result['steps']['bottleneck_analysis']['bottlenecks_found']}")
        print(f"优化机会: {result['steps']['optimization_identification']['opportunities_found']}")

    elif args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()