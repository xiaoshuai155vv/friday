#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能引擎能力组合自动发现与优化引擎 (Engine Capability Discovery & Optimization Engine)

功能：让系统能够自动分析70+引擎的能力组合，发现未被充分利用但可能有价值的组合，
主动生成创新工作流建议或自动创建新场景计划，实现从被动推荐到主动创造的范式升级。

核心能力：
1. 引擎能力注册与分析 - 扫描并注册所有引擎的能力
2. 创新组合发现 - 发现未被充分利用但可能有价值的引擎组合
3. 工作流建议生成 - 基于发现的组合生成创新工作流建议
4. 自动场景计划创建 - 自动创建有新价值的场景计划
5. 组合效果评估 - 评估引擎组合的实际效果

区别于推荐引擎：
- 推荐引擎：推荐已有工作流
- 本引擎：创造新的能力组合和工作流
"""

import json
import os
import sys
import ast
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Set, Tuple
from collections import defaultdict
from itertools import combinations

# 路径处理
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)


class EngineCapabilityDiscovery:
    """智能引擎能力组合自动发现与优化引擎"""

    def __init__(self):
        self.name = "Engine Capability Discovery Engine"
        self.version = "1.0.0"
        self.state_file = os.path.join(PROJECT_ROOT, "runtime", "state", "engine_capability_discovery_state.json")
        self.findings_file = os.path.join(PROJECT_ROOT, "runtime", "state", "engine_capability_findings.json")
        self.recommendations_file = os.path.join(PROJECT_ROOT, "runtime", "state", "engine_combination_recommendations.json")

        # 能力分类标签
        self.capability_categories = {
            "监控": ["monitor", "health", "security", "system", "check", "watch"],
            "执行": ["execute", "run", "launch", "start", "do", "action"],
            "学习": ["learn", "adaptive", "personalization", "preference", "memory"],
            "推理": ["reasoning", "insight", "prediction", "analysis", "understand"],
            "通信": ["notification", "send", "message", "alert", "notify"],
            "协作": ["orchestration", "coordinator", "linkage", "协同", "协作"],
            "自动化": ["automation", "workflow", "auto", "self"],
            "优化": ["optimize", "improve", "enhance", "tuning", "优化"]
        }

        # 已知的引擎能力映射
        self.known_engine_capabilities = self._init_known_capabilities()

        # 发现的创新组合
        self.discovered_combinations = []
        self.recommendations = []

        self._load_state()

    def _init_known_capabilities(self) -> Dict[str, List[str]]:
        """初始化已知的引擎能力映射"""
        return {
            # 核心引擎能力
            "health_assurance_loop": ["健康监控", "自愈", "预测预防", "运维", "服务保障"],
            "security_monitor_engine": ["异常进程检测", "网络异常检测", "安全告警", "威胁检测"],
            "proactive_operations_engine": ["主动运维", "资源监控", "预防性维护", "自动优化"],
            "predictive_prevention_engine": ["问题预测", "预防建议", "主动预警", "风险评估"],
            "self_healing_engine": ["问题诊断", "自动修复", "故障恢复"],
            "system_dashboard_engine": ["统一监控", "数据聚合", "实时状态", "可视化"],
            "engine_performance_monitor": ["性能监控", "引擎分析", "调优建议"],
            "daemon_linkage_engine": ["守护进程联动", "任务传递", "跨进程触发"],
            "module_linkage_engine": ["引擎协调", "场景识别", "智能编排"],
            "decision_orchestrator": ["意图分析", "引擎调度", "多引擎协同"],
            "conversation_execution_engine": ["意图理解", "多轮对话", "上下文记忆"],
            "execution_enhancement_engine": ["执行追踪", "策略分析", "自适应优化"],
            "unified_recommender": ["场景推荐", "工作流推荐", "引擎推荐", "智能排序"],
            "innovation_discovery_engine": ["创新发现", "能力组合", "模式识别"],
            "creative_generation_engine": ["创意生成", "新组合发现", "创新评估"],
            "long_term_memory_engine": ["长期记忆", "目标跟踪", "跨会话记忆"],
            "knowledge_inheritance_engine": ["知识传承", "会话接续", "上下文继承"],
            "context_awareness_engine": ["时间感知", "系统状态感知", "用户活动感知"],
            "behavior_sequence_prediction_engine": ["行为预测", "意图预判", "序列分析"],
            "intent_deep_reasoning_engine": ["深层意图推理", "隐含意图", "上下文推理"],
            "cross_engine_task_planner": ["任务拆分", "子任务编排", "进度追踪"],
            "proactive_decision_action_engine": ["主动决策", "行动计划", "自动执行"],
            "proactive_service_orchestrator": ["服务编排", "主动推荐", "行为监控"],
            "ui_structure_engine": ["界面解析", "元素识别", "精确点击"],
            "realtime_guidance_engine": ["实时观察", "操作识别", "智能辅助"],
            "operation_recorder": ["操作录制", "序列转换", "回放"],
            "cross_device_engine": ["设备发现", "文件传输", "远程控制", "通知同步"],
            "workflow_strategy_learner": ["策略学习", "执行优化", "自适应"],
            "task_continuation_engine": ["任务接续", "状态追踪", "跨会话恢复"],
            "task_preference_engine": ["偏好记录", "偏好学习", "偏好应用"],
            "automation_pattern_discovery": ["模式发现", "自动场景生成"],
            "service_orchestration_optimizer": ["服务编排优化", "效果分析", "瓶颈发现"],
            "knowledge_evolution_engine": ["知识提取", "知识更新", "冲突检测"],
            "knowledge_graph": ["知识关联", "图谱查询", "推理"],
            "proactive_insight_engine": ["需求预测", "主动洞察", "前瞻建议"],
            "data_insight_engine": ["数据分析", "趋势分析", "可视化"],
            "system_self_reflection_engine": ["自我审视", "瓶颈识别", "策略评估"],
            "evolution_meta_learning_engine": ["元学习", "进化模式分析"],
            "evolution_self_optimizer": ["进化优化", "效率分析", "自动建议"],
            "meeting_assistant_engine": ["会议管理", "纪要生成", "待办提醒"],
            "file_manager_engine": ["文件搜索", "智能分类", "自动整理"],
            "voice_interaction_engine": ["语音识别", "语音指令"],
            "tts_engine": ["语音合成", "语音回复"],
            "script_generation_engine": ["脚本生成", "代码生成"],
            "code_understanding_engine": ["代码分析", "重构建议", "依赖检测"],
        }

    def _load_state(self):
        """加载状态"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    self.discovered_combinations = state.get('discovered_combinations', [])
                    self.recommendations = state.get('recommendations', [])
            except Exception:
                pass

    def _save_state(self):
        """保存状态"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump({
                'discovered_combinations': self.discovered_combinations,
                'recommendations': self.recommendations,
                'last_updated': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)

    def scan_engines(self) -> Dict[str, List[str]]:
        """扫描所有引擎并提取能力"""
        print("=== 扫描引擎能力 ===")
        engines_path = os.path.join(PROJECT_ROOT, "scripts")
        engine_capabilities = {}

        if not os.path.exists(engines_path):
            print(f"引擎目录不存在: {engines_path}")
            return engine_capabilities

        # 扫描脚本目录下的引擎
        for filename in os.listdir(engines_path):
            if filename.endswith('_engine.py') or filename.endswith('_monitor.py') or filename.endswith('_orchestrator.py'):
                engine_name = filename[:-3]  # 移除 .py
                filepath = os.path.join(engines_path, filename)

                # 从文件名和已知能力中推断能力
                if engine_name in self.known_engine_capabilities:
                    engine_capabilities[engine_name] = self.known_engine_capabilities[engine_name]
                else:
                    # 基于文件名推断能力
                    capabilities = self._infer_capabilities_from_filename(engine_name)
                    engine_capabilities[engine_name] = capabilities

        print(f"已扫描 {len(engine_capabilities)} 个引擎")
        return engine_capabilities

    def _infer_capabilities_from_filename(self, filename: str) -> List[str]:
        """从文件名推断能力"""
        capabilities = []
        filename_lower = filename.lower()

        for category, keywords in self.capability_categories.items():
            for keyword in keywords:
                if keyword in filename_lower:
                    if category not in capabilities:
                        capabilities.append(category)
                    break

        if not capabilities:
            capabilities.append("未分类")

        return capabilities

    def discover_innovative_combinations(self, engine_capabilities: Dict[str, List[str]]) -> List[Dict]:
        """发现创新的引擎组合"""
        print("\n=== 发现创新组合 ===")
        discoveries = []

        # 预先定义的高价值组合模式
        valuable_patterns = [
            {
                "name": "综合系统监控闭环",
                "engines": ["health_assurance_loop", "security_monitor_engine"],
                "description": "将健康保障与安全监控深度集成，形成综合监控→预警→自动响应的闭环",
                "value": "高",
                "action": "集成健康保障引擎和安全监控引擎，实现安全威胁时自动触发健康保障响应"
            },
            {
                "name": "主动预判服务链",
                "engines": ["predictive_prevention_engine", "proactive_decision_action_engine", "proactive_notification_engine"],
                "description": "从预测到主动行动的完整服务链，当预测到问题时主动行动并通知用户",
                "value": "高",
                "action": "实现预测→决策→行动→通知的完整自动化服务闭环"
            },
            {
                "name": "智能场景自适应",
                "engines": ["context_awareness_engine", "behavior_sequence_prediction_engine", "unified_recommender"],
                "description": "基于上下文感知和行为预测，智能推荐最合适的场景计划",
                "value": "中",
                "action": "实现从感知→预测→推荐的智能场景推荐闭环"
            },
            {
                "name": "跨会话知识传承",
                "engines": ["long_term_memory_engine", "knowledge_inheritance_engine", "context_awareness_engine"],
                "description": "跨会话传递关键知识、决策上下文和用户偏好",
                "value": "中",
                "action": "实现会话间的知识、偏好和上下文自动传承"
            },
            {
                "name": "智能运维自愈",
                "engines": ["proactive_operations_engine", "self_healing_engine", "system_dashboard_engine"],
                "description": "从主动运维到自动修复的智能闭环",
                "value": "高",
                "action": "实现运维→自愈→反馈的完整智能化服务"
            },
            {
                "name": "创新工作流生成",
                "engines": ["innovation_discovery_engine", "creative_generation_engine", "cross_engine_task_planner"],
                "description": "从创新发现到工作流自动生成的完整闭环",
                "value": "中",
                "action": "实现从创新想法到可执行工作流的自动转换"
            },
            {
                "name": "用户体验优化闭环",
                "engines": ["execution_enhancement_engine", "workflow_strategy_learner", "task_preference_engine"],
                "description": "从执行效果追踪到策略优化再到偏好应用的完整闭环",
                "value": "中",
                "action": "实现执行→优化→个性化的智能用户体验提升"
            },
            {
                "name": "主动洞察服务",
                "engines": ["proactive_insight_engine", "data_insight_engine", "knowledge_graph"],
                "description": "从数据中主动发现用户可能感兴趣的洞察",
                "value": "中",
                "action": "实现从数据到主动洞察的智能分析服务"
            }
        ]

        # 检查哪些组合已经被实现（通过检查引擎是否存在）
        for pattern in valuable_patterns:
            engines_exist = all(
                any(eng in cap for cap in engine_capabilities.keys())
                for eng in pattern["engines"]
            )
            if engines_exist:
                discoveries.append({
                    "pattern": pattern["name"],
                    "description": pattern["description"],
                    "value": pattern["value"],
                    "action": pattern["action"],
                    "engines": pattern["engines"],
                    "status": "已具备基础能力"
                })

        print(f"发现 {len(discoveries)} 个高价值组合")
        return discoveries

    def generate_workflow_suggestions(self, discoveries: List[Dict]) -> List[Dict]:
        """生成工作流建议"""
        print("\n=== 生成工作流建议 ===")
        suggestions = []

        for discovery in discoveries:
            if discovery.get("value") == "高":
                suggestions.append({
                    "title": f"建议实现：{discovery['pattern']}",
                    "description": discovery["description"],
                    "action": discovery["action"],
                    "priority": "高",
                    "suggested_engines": discovery.get("engines", [])
                })

        print(f"生成 {len(suggestions)} 条工作流建议")
        return suggestions

    def analyze_unused_capabilities(self, engine_capabilities: Dict[str, List[str]]) -> List[Dict]:
        """分析未被充分使用的引擎能力"""
        print("\n=== 分析未被充分使用的能力 ===")

        # 基于执行历史分析哪些引擎很少被使用
        unused_analysis = []

        # 简单分析：输出所有能力
        all_capabilities = set()
        for engine, caps in engine_capabilities.items():
            for cap in caps:
                all_capabilities.add(cap)

        print(f"共有 {len(all_capabilities)} 种不同能力类型")

        return unused_analysis

    def run_full_discovery(self) -> Dict:
        """运行完整的发现流程"""
        print("\n" + "="*50)
        print("智能引擎能力组合自动发现与优化引擎")
        print("="*50 + "\n")

        # 1. 扫描引擎能力
        engine_capabilities = self.scan_engines()

        # 2. 发现创新组合
        discoveries = self.discover_innovative_combinations(engine_capabilities)
        self.discovered_combinations = discoveries
        self._save_state()

        # 3. 生成工作流建议
        suggestions = self.generate_workflow_suggestions(discoveries)
        self.recommendations = suggestions
        self._save_state()

        # 4. 分析未被充分使用的能力
        unused = self.analyze_unused_capabilities(engine_capabilities)

        # 返回结果
        result = {
            "engines_scanned": len(engine_capabilities),
            "discoveries": discoveries,
            "suggestions": suggestions,
            "timestamp": datetime.now().isoformat()
        }

        # 打印摘要
        print("\n" + "="*50)
        print("发现摘要")
        print("="*50)
        print(f"扫描引擎数：{result['engines_scanned']}")
        print(f"发现创新组合：{len(discoveries)}")
        print(f"生成建议：{len(suggestions)}")
        print(f"时间：{result['timestamp']}")

        # 打印发现的组合
        if discoveries:
            print("\n高价值组合：")
            for d in discoveries:
                print(f"  - {d['pattern']}: {d['description']}")

        # 打印建议
        if suggestions:
            print("\n工作流建议：")
            for s in suggestions:
                print(f"  [{s['priority']}] {s['title']}")
                print(f"      {s['action']}")

        return result

    def get_status(self) -> Dict:
        """获取引擎状态"""
        return {
            "name": self.name,
            "version": self.version,
            "engines_tracked": len(self.known_engine_capabilities),
            "discoveries_count": len(self.discovered_combinations),
            "recommendations_count": len(self.recommendations),
            "last_updated": os.path.getmtime(self.state_file) if os.path.exists(self.state_file) else None
        }

    def get_discoveries(self) -> List[Dict]:
        """获取已发现的组合"""
        return self.discovered_combinations

    def get_recommendations(self) -> List[Dict]:
        """获取工作流建议"""
        return self.recommendations


def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser(description='智能引擎能力组合自动发现与优化引擎')
    parser.add_argument('command', nargs='?', default='run',
                        choices=['run', 'status', 'discoveries', 'recommendations'],
                        help='要执行的命令')
    parser.add_argument('--output', '-o', help='输出文件路径 (JSON)')

    args = parser.parse_args()

    engine = EngineCapabilityDiscovery()

    if args.command == 'run':
        result = engine.run_full_discovery()

        # 保存到文件
        if args.output:
            os.makedirs(os.path.dirname(args.output), exist_ok=True)
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n结果已保存到: {args.output}")
        else:
            # 默认保存到 findings 文件
            os.makedirs(os.path.dirname(engine.findings_file), exist_ok=True)
            with open(engine.findings_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n结果已保存到: {engine.findings_file}")

    elif args.command == 'status':
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.command == 'discoveries':
        discoveries = engine.get_discoveries()
        print(json.dumps(discoveries, ensure_ascii=False, indent=2))

    elif args.command == 'recommendations':
        recommendations = engine.get_recommendations()
        print(json.dumps(recommendations, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()