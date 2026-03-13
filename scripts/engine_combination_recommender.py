#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能引擎组合推荐系统
基于用户任务描述，智能分析并推荐最优的引擎/能力组合

功能：
1. 引擎能力注册与分类 - 40+引擎能力映射
2. 任务-引擎匹配分析 - 分析用户任务需求，推荐最优引擎组合
3. 组合执行编排 - 支持多引擎顺序/并行协同执行
4. 执行效果追踪与反馈学习 - 记录执行效果并优化推荐

工作原理：
- 系统维护所有可用引擎的能力注册表
- 用户描述任务需求后，系统分析任务类型和目标
- 根据任务特征匹配最适合的引擎组合
- 支持执行编排和效果追踪
"""

import os
import json
import subprocess
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

# 确保 scripts 目录在路径中
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..'))
STATE_DIR = os.path.join(PROJECT_DIR, 'runtime', 'state')


# 引擎能力注册表 - 映射引擎到其能力
ENGINE_CAPABILITIES = {
    # 基础交互引擎
    "screenshot_tool": {"category": "基础交互", "capabilities": ["截图", "屏幕捕获"], "keywords": ["截图", "屏幕", "capture"]},
    "vision_proxy": {"category": "视觉理解", "capabilities": ["图像理解", "坐标提取", "视觉分析"], "keywords": ["看", "识别", "理解图像", "vision"]},
    "mouse_tool": {"category": "基础交互", "capabilities": ["鼠标点击", "移动", "拖拽"], "keywords": ["点击", "鼠标", "click", "拖拽"]},
    "keyboard_tool": {"category": "基础交互", "capabilities": ["键盘输入", "快捷键"], "keywords": ["输入", "键盘", "type", "key"]},
    "window_tool": {"category": "窗口管理", "capabilities": ["窗口激活", "最大化", "最小化", "关闭"], "keywords": ["窗口", "激活", "最大化", "activate"]},

    # 文件操作引擎
    "file_tool": {"category": "文件操作", "capabilities": ["文件读写", "目录操作", "文件搜索"], "keywords": ["文件", "目录", "读写", "file"]},
    "file_manager_engine": {"category": "文件管理", "capabilities": ["智能分类", "整理", "分析"], "keywords": ["整理文件", "文件管理", "分类"]},
    "quick_look": {"category": "文件预览", "capabilities": ["快速预览", "元数据"], "keywords": ["预览", "quicklook"]},
    "file_metadata": {"category": "文件元数据", "capabilities": ["元数据提取", "标签管理"], "keywords": ["元数据", "标签"]},

    # 办公与效率引擎
    "workflow_engine": {"category": "工作流", "capabilities": ["任务规划", "多步骤编排"], "keywords": ["工作流", "任务规划", "复杂任务"]},
    "workflow_orchestrator": {"category": "任务编排", "capabilities": ["任务拆分", "自动规划"], "keywords": ["编排", "任务协调"]},
    "workflow_quality_engine": {"category": "工作流质量", "capabilities": ["质量监控", "失败分析"], "keywords": ["质量", "优化"]},
    "run_plan": {"category": "计划执行", "capabilities": ["执行场景计划", "JSON计划"], "keywords": ["run_plan", "执行计划"]},

    # 智能服务引擎
    "conversation_execution_engine": {"category": "对话执行", "capabilities": ["意图理解", "多轮对话", "引擎调度"], "keywords": ["对话", "聊天", "意图"]},
    "execution_enhancement_engine": {"category": "执行增强", "capabilities": ["效果追踪", "策略优化", "自适应执行"], "keywords": ["执行增强", "优化执行"]},
    "decision_orchestrator": {"category": "决策编排", "capabilities": ["意图分析", "引擎调度"], "keywords": ["决策", "编排", "调度"]},
    "module_linkage_engine": {"category": "模块联动", "capabilities": ["跨模块协同", "场景模式识别"], "keywords": ["联动", "协同"]},
    "unified_engine_hub": {"category": "引擎中心", "capabilities": ["引擎注册", "统一调度"], "keywords": ["引擎", "hub"]},
    "unified_recommender": {"category": "统一推荐", "capabilities": ["场景推荐", "工作流推荐"], "keywords": ["推荐"]},

    # 学习与适应引擎
    "adaptive_learning_engine": {"category": "自适应学习", "capabilities": ["行为学习", "习惯分析"], "keywords": ["学习", "适应", "习惯"]},
    "deep_personalization_engine": {"category": "深度个性化", "capabilities": ["多维度分析", "时间模式"], "keywords": ["个性化", "深度学习"]},
    "feedback_learning_engine": {"category": "反馈学习", "capabilities": ["推荐反馈", "策略优化"], "keywords": ["反馈", "学习"]},
    "user_behavior_learner": {"category": "行为学习", "capabilities": ["高频任务", "偏好分析"], "keywords": ["用户行为", "学习"]},

    # 知识与推理引擎
    "knowledge_graph": {"category": "知识图谱", "capabilities": ["知识关联", "图谱查询"], "keywords": ["知识", "图谱", "关联"]},
    "enhanced_knowledge_reasoning_engine": {"category": "知识推理", "capabilities": ["因果推理", "类比推理", "主动洞察"], "keywords": ["推理", "分析"]},
    "knowledge_evolution_engine": {"category": "知识进化", "capabilities": ["知识提取", "知识更新"], "keywords": ["知识进化", "知识更新"]},
    "context_memory": {"category": "上下文记忆", "capabilities": ["跨会话记忆", "意图预测"], "keywords": ["记忆", "上下文"]},
    "long_term_memory_engine": {"category": "长期记忆", "capabilities": ["目标跟踪", "跨会话记忆"], "keywords": ["长期记忆", "目标"]},

    # 预测与主动服务引擎
    "proactive_insight_engine": {"category": "主动洞察", "capabilities": ["需求预测", "主动建议"], "keywords": ["预测", "洞察", "主动"]},
    "predictive_prevention_engine": {"category": "预测预防", "capabilities": ["问题预测", "预防"], "keywords": ["预测", "预防", "预警"]},
    "proactive_notification_engine": {"category": "主动通知", "capabilities": ["定时提醒", "智能提醒"], "keywords": ["通知", "提醒"]},
    "proactive_service_trigger": {"category": "服务触发", "capabilities": ["条件触发", "自动执行"], "keywords": ["触发", "自动服务"]},
    "scenario_recommender": {"category": "场景推荐", "capabilities": ["场景推荐", "时间感知"], "keywords": ["场景", "推荐"]},
    "service_orchestration_optimizer": {"category": "服务编排优化", "capabilities": ["路径追踪", "效果分析"], "keywords": ["编排", "优化"]},

    # 创新与进化引擎
    "innovation_discovery_engine": {"category": "创新发现", "capabilities": ["创新推荐", "能力组合"], "keywords": ["创新", "发现"]},
    "intelligent_evolution_engine": {"category": "智能进化", "capabilities": ["自我分析", "自动优化"], "keywords": ["进化", "自进化"]},
    "evolution_strategy_engine": {"category": "进化策略", "capabilities": ["策略分析", "方向推荐"], "keywords": ["策略", "进化策略"]},
    "evolution_meta_learning_engine": {"category": "元学习", "capabilities": ["模式识别", "策略优化"], "keywords": ["元学习"]},
    "adaptive_priority_engine": {"category": "自适应优先级", "capabilities": ["动态调整", "负载感知"], "keywords": ["优先级", "自适应"]},

    # 系统工具引擎
    "power_tool": {"category": "电源管理", "capabilities": ["睡眠", "关机", "重启"], "keywords": ["电源", "睡眠", "关机"]},
    "volume_tool": {"category": "音量控制", "capabilities": ["音量调节", "静音"], "keywords": ["音量", "静音"]},
    "brightness_tool": {"category": "亮度控制", "capabilities": ["亮度调节"], "keywords": ["亮度"]},
    "network_tool": {"category": "网络管理", "capabilities": ["网络信息", "IP配置"], "keywords": ["网络", "IP"]},
    "process_tool": {"category": "进程管理", "capabilities": ["进程列表", "结束进程"], "keywords": ["进程", "结束"]},
    "clipboard_tool": {"category": "剪贴板", "capabilities": ["读写剪贴板"], "keywords": ["剪贴板", "复制", "粘贴"]},

    # 多媒体引擎
    "camera_qt": {"category": "摄像头", "capabilities": ["拍照", "自拍"], "keywords": ["摄像头", "自拍", "相机"]},
    "voice_interaction_engine": {"category": "语音交互", "capabilities": ["语音识别"], "keywords": ["语音", "说话"]},
    "tts_engine": {"category": "语音合成", "capabilities": ["文字转语音"], "keywords": ["tts", "语音合成"]},

    # 专用场景引擎
    "meeting_assistant_engine": {"category": "会议助手", "capabilities": ["会议管理", "纪要"], "keywords": ["会议", "纪要"]},
    "self_healing_engine": {"category": "自愈引擎", "capabilities": ["问题诊断", "自动修复"], "keywords": ["诊断", "自愈", "修复"]},
    "system_diagnostic_engine": {"category": "系统诊断", "capabilities": ["综合诊断", "跨模块分析"], "keywords": ["诊断", "系统"]},
    "code_understanding_engine": {"category": "代码理解", "capabilities": ["代码分析", "重构建议"], "keywords": ["代码", "分析", "重构"]},
    "script_generation_engine": {"category": "脚本生成", "capabilities": ["自然语言生成代码"], "keywords": ["生成脚本", "代码生成"]},
    "automation_pattern_discovery": {"category": "模式发现", "capabilities": ["行为分析", "自动化发现"], "keywords": ["模式", "发现", "自动化"]},
    "task_preference_engine": {"category": "任务偏好", "capabilities": ["偏好记录", "偏好学习"], "keywords": ["偏好", "记忆"]},
}


# 任务类型到引擎能力的映射
TASK_ENGINE_MAPPING = {
    "文件操作": ["file_tool", "file_manager_engine", "quick_look", "file_metadata"],
    "截图视觉": ["screenshot_tool", "vision_proxy", "mouse_tool", "keyboard_tool"],
    "办公流程": ["workflow_engine", "workflow_orchestrator", "run_plan", "workflow_quality_engine"],
    "智能对话": ["conversation_execution_engine", "module_linkage_engine", "context_memory"],
    "个性化推荐": ["unified_recommender", "scenario_recommender", "adaptive_learning_engine", "deep_personalization_engine"],
    "知识管理": ["knowledge_graph", "enhanced_knowledge_reasoning_engine", "knowledge_evolution_engine"],
    "预测主动服务": ["proactive_insight_engine", "predictive_prevention_engine", "proactive_notification_engine"],
    "学习适应": ["adaptive_learning_engine", "feedback_learning_engine", "user_behavior_learner"],
    "系统控制": ["power_tool", "volume_tool", "brightness_tool", "network_tool", "process_tool"],
    "多媒体": ["camera_qt", "voice_interaction_engine", "tts_engine"],
    "会议管理": ["meeting_assistant_engine"],
    "代码开发": ["code_understanding_engine", "script_generation_engine"],
    "故障处理": ["self_healing_engine", "system_diagnostic_engine"],
    "自动化": ["automation_pattern_discovery", "task_preference_engine", "proactive_service_trigger"],
    "进化优化": ["intelligent_evolution_engine", "evolution_strategy_engine", "evolution_meta_learning_engine"],
}


class EngineCombinationRecommender:
    """智能引擎组合推荐系统"""

    def __init__(self):
        self.engine_registry = ENGINE_CAPABILITIES
        self.task_mapping = TASK_ENGINE_MAPPING
        self.recommendation_history_file = os.path.join(STATE_DIR, 'engine_recommendation_history.json')
        self.execution_stats_file = os.path.join(STATE_DIR, 'engine_execution_stats.json')
        self.recommendation_history = self._load_history()
        self.execution_stats = self._load_stats()

    def _load_history(self) -> List[Dict[str, Any]]:
        """加载推荐历史"""
        if os.path.exists(self.recommendation_history_file):
            try:
                with open(self.recommendation_history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('history', [])
            except Exception as e:
                print(f"[EngineCombination] 加载历史失败: {e}")
        return []

    def _save_history(self):
        """保存推荐历史"""
        try:
            os.makedirs(os.path.dirname(self.recommendation_history_file), exist_ok=True)
            # 只保留最近 100 条
            self.recommendation_history = self.recommendation_history[-100:]
            with open(self.recommendation_history_file, 'w', encoding='utf-8') as f:
                json.dump({"history": self.recommendation_history}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[EngineCombination] 保存历史失败: {e}")

    def _load_stats(self) -> Dict[str, Any]:
        """加载执行统计"""
        if os.path.exists(self.execution_stats_file):
            try:
                with open(self.execution_stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[EngineCombination] 加载统计失败: {e}")
        return {"engine_usage": {}, "combination_effectiveness": {}, "last_updated": None}

    def _save_stats(self):
        """保存执行统计"""
        try:
            os.makedirs(os.path.dirname(self.execution_stats_file), exist_ok=True)
            self.execution_stats["last_updated"] = datetime.now().isoformat()
            with open(self.execution_stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.execution_stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[EngineCombination] 保存统计失败: {e}")

    def analyze_task(self, task_description: str) -> Dict[str, Any]:
        """分析任务描述，提取任务特征

        Args:
            task_description: 用户任务描述

        Returns:
            任务分析结果
        """
        task_lower = task_description.lower()

        # 识别任务类型
        task_types = []
        for task_type, keywords in TASK_ENGINE_MAPPING.items():
            for keyword in keywords:
                if keyword.lower() in task_lower:
                    task_types.append(task_type)
                    break

        if not task_types:
            task_types = ["通用任务"]

        # 识别需要的引擎能力
        required_capabilities = []
        for engine, info in self.engine_registry.items():
            for keyword in info.get("keywords", []):
                if keyword.lower() in task_lower:
                    required_capabilities.append(info.get("category", "未知"))
                    break

        if not required_capabilities:
            required_capabilities = ["基础交互", "智能分析"]

        return {
            "task_description": task_description,
            "task_types": task_types,
            "required_capabilities": list(set(required_capabilities)),
            "analyzed_at": datetime.now().isoformat()
        }

    def recommend_engines(self, task_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """根据任务分析推荐引擎组合

        Args:
            task_analysis: 任务分析结果

        Returns:
            推荐引擎列表
        """
        task_types = task_analysis.get("task_types", [])
        recommended = []

        # 根据任务类型匹配引擎
        for task_type in task_types:
            engines = self.task_mapping.get(task_type, [])
            for engine in engines:
                if engine not in [r["engine"] for r in recommended]:
                    engine_info = self.engine_registry.get(engine, {})
                    recommended.append({
                        "engine": engine,
                        "category": engine_info.get("category", "未知"),
                        "capabilities": engine_info.get("capabilities", []),
                        "reason": f"支持{task_type}任务"
                    })

        # 如果推荐数量太少，添加通用引擎
        if len(recommended) < 3:
            general_engines = ["conversation_execution_engine", "decision_orchestrator", "module_linkage_engine"]
            for engine in general_engines:
                if engine not in [r["engine"] for r in recommended]:
                    engine_info = self.engine_registry.get(engine, {})
                    recommended.append({
                        "engine": engine,
                        "category": engine_info.get("category", "未知"),
                        "capabilities": engine_info.get("capabilities", []),
                        "reason": "通用智能引擎"
                    })

        # 记录推荐历史
        self.recommendation_history.append({
            "task_description": task_analysis.get("task_description", ""),
            "recommended_engines": [r["engine"] for r in recommended],
            "recommended_at": datetime.now().isoformat()
        })
        self._save_history()

        return recommended

    def execute_combination(self, engines: List[str], task: str) -> Dict[str, Any]:
        """执行引擎组合

        Args:
            engines: 引擎列表
            task: 任务描述

        Returns:
            执行结果
        """
        results = []
        success_count = 0

        for engine in engines:
            try:
                # 检查引擎是否存在
                engine_path = os.path.join(SCRIPTS, f"{engine}.py")
                if os.path.exists(engine_path):
                    # 调用引擎
                    result = subprocess.run(
                        [sys.executable, engine_path, "status"],
                        cwd=PROJECT_DIR,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    results.append({
                        "engine": engine,
                        "status": "success" if result.returncode == 0 else "failed",
                        "output": result.stdout[:200] if result.stdout else ""
                    })
                    if result.returncode == 0:
                        success_count += 1
                else:
                    results.append({
                        "engine": engine,
                        "status": "not_found",
                        "output": f"引擎文件不存在: {engine_path}"
                    })
            except Exception as e:
                results.append({
                    "engine": engine,
                    "status": "error",
                    "output": str(e)
                })

        # 更新统计
        for engine in engines:
            if engine not in self.execution_stats["engine_usage"]:
                self.execution_stats["engine_usage"][engine] = 0
            self.execution_stats["engine_usage"][engine] += 1

        # 更新组合效果
        combo_key = "+".join(engines[:3])
        if combo_key not in self.execution_stats["combination_effectiveness"]:
            self.execution_stats["combination_effectiveness"][combo_key] = {"success": 0, "total": 0}

        self.execution_stats["combination_effectiveness"][combo_key]["total"] += 1
        if success_count == len(engines):
            self.execution_stats["combination_effectiveness"][combo_key]["success"] += 1

        self._save_stats()

        return {
            "task": task,
            "engines": engines,
            "results": results,
            "success_count": success_count,
            "total_engines": len(engines),
            "executed_at": datetime.now().isoformat()
        }

    def get_engine_stats(self) -> Dict[str, Any]:
        """获取引擎使用统计"""
        return {
            "total_engines": len(self.engine_registry),
            "engine_usage": self.execution_stats.get("engine_usage", {}),
            "combination_effectiveness": self.execution_stats.get("combination_effectiveness", {}),
            "recommendation_count": len(self.recommendation_history),
            "last_updated": self.execution_stats.get("last_updated")
        }

    def list_engines(self, category: str = None) -> List[Dict[str, Any]]:
        """列出引擎

        Args:
            category: 可选的分类过滤

        Returns:
            引擎列表
        """
        engines = []
        for engine, info in self.engine_registry.items():
            if category is None or info.get("category") == category:
                engines.append({
                    "engine": engine,
                    "category": info.get("category", "未知"),
                    "capabilities": info.get("capabilities", [])
                })
        return engines


# 全局实例
_recommender = None


def get_recommender() -> EngineCombinationRecommender:
    """获取推荐器实例"""
    global _recommender
    if _recommender is None:
        _recommender = EngineCombinationRecommender()
    return _recommender


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='智能引擎组合推荐系统')
    parser.add_argument('action', nargs='?', default='list',
                       choices=['list', 'recommend', 'execute', 'stats', 'analyze', 'search'],
                       help='动作')
    parser.add_argument('--task', '-t', help='任务描述')
    parser.add_argument('--engines', '-e', help='引擎列表（逗号分隔）')
    parser.add_argument('--category', '-c', help='分类过滤')
    parser.add_argument('--json', '-j', action='store_true', help='输出JSON格式')

    args = parser.parse_args()

    recommender = get_recommender()

    if args.action == 'list':
        engines = recommender.list_engines(args.category)
        if args.json:
            print(json.dumps(engines, ensure_ascii=False, indent=2))
        else:
            print("=== 引擎列表 ===")
            if args.category:
                print(f"分类: {args.category}")
            print(f"总数: {len(engines)} 个\n")
            current_category = None
            for e in engines:
                if e["category"] != current_category:
                    current_category = e["category"]
                    print(f"\n【{current_category}】")
                print(f"  - {e['engine']}: {', '.join(e['capabilities'][:2])}")

    elif args.action == 'analyze':
        if not args.task:
            print("错误: 需要指定 --task")
        else:
            analysis = recommender.analyze_task(args.task)
            if args.json:
                print(json.dumps(analysis, ensure_ascii=False, indent=2))
            else:
                print("=== 任务分析 ===")
                print(f"任务: {analysis['task_description']}")
                print(f"类型: {', '.join(analysis['task_types'])}")
                print(f"能力: {', '.join(analysis['required_capabilities'])}")

    elif args.action == 'recommend':
        if not args.task:
            print("错误: 需要指定 --task")
        else:
            # 分析任务
            analysis = recommender.analyze_task(args.task)
            # 推荐引擎
            recommended = recommender.recommend_engines(analysis)
            if args.json:
                print(json.dumps({
                    "analysis": analysis,
                    "recommendation": recommended
                }, ensure_ascii=False, indent=2))
            else:
                print("=== 任务分析 ===")
                print(f"任务: {analysis['task_description']}")
                print(f"类型: {', '.join(analysis['task_types'])}")
                print(f"\n=== 推荐引擎组合 ===")
                for i, r in enumerate(recommended, 1):
                    print(f"{i}. {r['engine']} ({r['category']})")
                    print(f"   能力: {', '.join(r['capabilities'])}")
                    print(f"   原因: {r['reason']}")

    elif args.action == 'execute':
        if not args.task or not args.engines:
            print("错误: 需要指定 --task 和 --engines")
        else:
            engines = args.engines.split(",")
            result = recommender.execute_combination(engines, args.task)
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print("=== 执行结果 ===")
                print(f"任务: {result['task']}")
                print(f"引擎数: {result['success_count']}/{result['total_engines']} 成功")
                print(f"执行时间: {result['executed_at']}")
                print("\n详细结果:")
                for r in result["results"]:
                    status_icon = "✓" if r["status"] == "success" else "✗"
                    print(f"  {status_icon} {r['engine']}: {r['status']}")

    elif args.action == 'stats':
        stats = recommender.get_engine_stats()
        if args.json:
            print(json.dumps(stats, ensure_ascii=False, indent=2))
        else:
            print("=== 引擎组合统计 ===")
            print(f"注册引擎数: {stats['total_engines']}")
            print(f"推荐次数: {stats['recommendation_count']}")
            print(f"\n引擎使用排行:")
            usage = sorted(stats['engine_usage'].items(), key=lambda x: x[1], reverse=True)
            for engine, count in usage[:10]:
                print(f"  {engine}: {count} 次")
            print(f"\n最后更新: {stats['last_updated']}")

    elif args.action == 'search':
        if not args.task:
            print("错误: 需要指定 --task")
        else:
            # 在引擎注册表中搜索
            results = []
            task_lower = args.task.lower()
            for engine, info in ENGINE_CAPABILITIES.items():
                score = 0
                for kw in info.get("keywords", []):
                    if kw.lower() in task_lower:
                        score += 1
                for cap in info.get("capabilities", []):
                    if cap.lower() in task_lower:
                        score += 1
                if score > 0:
                    results.append({
                        "engine": engine,
                        "category": info.get("category"),
                        "capabilities": info.get("capabilities"),
                        "score": score
                    })

            results.sort(key=lambda x: x["score"], reverse=True)
            if args.json:
                print(json.dumps(results, ensure_ascii=False, indent=2))
            else:
                print("=== 引擎搜索结果 ===")
                print(f"关键词: {args.task}\n")
                for r in results[:10]:
                    print(f"  {r['engine']} (匹配度: {r['score']})")
                    print(f"    分类: {r['category']}")
                    print(f"    能力: {', '.join(r['capabilities'])}")