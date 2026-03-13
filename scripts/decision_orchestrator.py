"""
智能决策编排中心 - 综合分析用户意图和系统状态，智能选择并调度多个引擎协同工作

功能：
- 分析用户意图，识别需要多引擎协同的场景
- 根据系统状态和历史行为选择最优引擎组合
- 支持多引擎顺序/并行执行
- 提供可解释的决策过程
- 记录执行结果供学习引擎使用

集成到 do.py：支持「决策」「编排」「协同」「最佳方案」「智能调度」「multi-engine」等关键词触发
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# 注册的引擎模块
REGISTERED_ENGINES = {
    "self_healing": {
        "module": "self_healing_engine",
        "class": "SelfHealingEngine",
        "triggers": ["诊断", "自愈", "问题检测", "健康检测", "修复"],
    },
    "memory": {
        "module": "memory_engine",
        "class": "MemoryEngine",
        "triggers": ["记忆", "记住", "存储", "recall", "memory"],
    },
    "notification": {
        "module": "proactive_notification_engine",
        "class": "ProactiveNotificationEngine",
        "triggers": ["通知", "提醒", "主动建议", "notification", "reminder"],
    },
    "learning": {
        "module": "adaptive_learning_engine",
        "class": "AdaptiveLearningEngine",
        "triggers": ["学习", "适应", "个性化", "习惯"],
    },
    "workflow": {
        "module": "workflow_engine",
        "class": "WorkflowEngine",
        "triggers": ["工作流", "任务规划", "复杂任务", "workflow"],
    },
    "file_manager": {
        "module": "file_manager_engine",
        "class": "FileManagerEngine",
        "triggers": ["文件管理", "整理文件", "搜索文件", "分析文件"],
    },
    "tts": {
        "module": "tts_engine",
        "class": "TTSEngine",
        "triggers": ["语音合成", "语音回复", "tts", "text to speech", "读出来"],
    },
    "voice": {
        "module": "voice_interaction_engine",
        "class": "VoiceInteractionEngine",
        "triggers": ["语音交互", "语音命令", "voice", "语音识别"],
    },
    "scenario": {
        "module": "scenario_recommender",
        "class": "ScenarioRecommender",
        "triggers": ["场景推荐", "推荐场景", "推荐计划"],
    },
    # 集成预测与预防引擎
    "predictive_prevention": {
        "module": "predictive_prevention_engine",
        "class": "PredictivePreventionEngine",
        "triggers": ["预测", "预防", "预警", "风险", "系统扫描", "健康扫描", "主动预防", "predictive", "prevention"],
    },
}


class DecisionOrchestrator:
    """智能决策编排中心"""

    def __init__(self):
        self.engines = {}
        self.decision_history = []
        self._load_engines()

    def _load_engines(self):
        """加载已注册的引擎模块"""
        import sys
        from importlib import import_module
        from importlib.util import spec_from_file_location, module_from_spec
        import os

        # 添加 scripts 目录到 Python 路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)

        # 动态加载引擎模块
        for engine_name, engine_config in REGISTERED_ENGINES.items():
            try:
                # 直接导入模块
                module_name = engine_config['module']
                class_name = engine_config['class']

                # 尝试直接导入
                if module_name in sys.modules:
                    module = sys.modules[module_name]
                else:
                    # 尝试从文件加载
                    module_file = os.path.join(script_dir, f"{module_name}.py")
                    if os.path.exists(module_file):
                        spec = spec_from_file_location(module_name, module_file)
                        if spec and spec.loader:
                            module = module_from_spec(spec)
                            sys.modules[module_name] = module
                            spec.loader.exec_module(module)
                    else:
                        # 使用 importlib
                        module = import_module(module_name)

                engine_class = getattr(module, class_name)
                self.engines[engine_name] = engine_class()
                print(f"[DecisionOrchestrator] 已加载引擎: {engine_name}")
            except Exception as e:
                # 加载失败不中断，记录即可
                print(f"[DecisionOrchestrator] 引擎 {engine_name} 暂不可用: {type(e).__name__}")

    def analyze_intent(self, user_input: str) -> Dict[str, Any]:
        """分析用户意图，识别需要调用的引擎组合"""
        user_input_lower = user_input.lower()

        # 识别需要多引擎协同的场景
        multi_engine_scenarios = {
            ("整理", "提醒"): ["file_manager", "notification"],
            ("学习", "推荐"): ["learning", "scenario"],
            ("诊断", "修复"): ["self_healing", "notification"],
            ("文件", "语音"): ["file_manager", "tts"],
            ("工作流", "通知"): ["workflow", "notification"],
            ("记忆", "学习"): ["memory", "learning"],
        }

        # 单引擎关键词匹配
        engine_scores = {}
        for engine_name, config in REGISTERED_ENGINES.items():
            score = 0
            for trigger in config["triggers"]:
                if trigger in user_input_lower:
                    score += 1
            if score > 0:
                engine_scores[engine_name] = score

        # 检查多引擎场景
        selected_engines = []
        for keywords, engines in multi_engine_scenarios.items():
            if all(kw in user_input_lower for kw in keywords):
                selected_engines = engines
                break

        # 如果没有多引擎匹配，使用单引擎最高分
        if not selected_engines and engine_scores:
            if engine_scores:
                max_score = max(engine_scores.values())
                top_engines = [e for e, s in engine_scores.items() if s == max_score]
                selected_engines = top_engines[:2]  # 最多选择2个引擎

        return {
            "user_input": user_input,
            "selected_engines": selected_engines or list(engine_scores.keys())[:1],
            "confidence": len(selected_engines) > 0,
            "reasoning": self._generate_reasoning(user_input, selected_engines or list(engine_scores.keys())[:1]),
        }

    def _generate_reasoning(self, user_input: str, engines: List[str]) -> str:
        """生成决策解释"""
        if not engines:
            return "未能识别需要调用的引擎"

        engine_names = {
            "self_healing": "问题诊断与自愈引擎",
            "memory": "智能记忆系统",
            "notification": "主动通知引擎",
            "learning": "学习与适应引擎",
            "workflow": "工作流引擎",
            "file_manager": "文件管理引擎",
            "tts": "语音合成引擎",
            "voice": "语音交互引擎",
            "scenario": "场景推荐引擎",
        }

        names = [engine_names.get(e, e) for e in engines]
        if len(names) == 1:
            return f"根据用户输入「{user_input}」，选择调用 {names[0]} 处理请求"
        else:
            return f"根据用户输入「{user_input}」，协同调用 {' + '.join(names)} 处理请求"

    def orchestrate(self, user_input: str) -> Dict[str, Any]:
        """执行智能编排"""
        # 1. 分析意图
        intent_analysis = self.analyze_intent(user_input)

        # 2. 决策记录
        decision = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "intent_analysis": intent_analysis,
            "execution_results": [],
            "status": "pending",
        }

        # 3. 执行选中的引擎
        results = []
        for engine_name in intent_analysis["selected_engines"]:
            if engine_name in self.engines:
                try:
                    engine = self.engines[engine_name]
                    # 尝试调用引擎的默认方法
                    if hasattr(engine, "process"):
                        result = engine.process(user_input)
                    elif hasattr(engine, "analyze"):
                        result = engine.analyze(user_input)
                    elif hasattr(engine, "execute"):
                        result = engine.execute(user_input)
                    else:
                        result = {"status": "success", "engine": engine_name, "message": f"引擎 {engine_name} 已加载"}

                    results.append({
                        "engine": engine_name,
                        "result": result,
                        "status": "success",
                    })
                    print(f"[DecisionOrchestrator] 引擎 {engine_name} 执行成功")
                except Exception as e:
                    results.append({
                        "engine": engine_name,
                        "error": str(e),
                        "status": "failed",
                    })
                    print(f"[DecisionOrchestrator] 引擎 {engine_name} 执行失败: {e}")

        decision["execution_results"] = results
        decision["status"] = "completed" if results else "no_engine"

        # 保存决策历史
        self.decision_history.append(decision)
        self._save_decision(decision)

        return decision

    def _save_decision(self, decision: Dict[str, Any]):
        """保存决策到文件"""
        try:
            os.makedirs("runtime/state", exist_ok=True)
            output_file = "runtime/state/decision_orchestrator_history.json"
            history = []

            if os.path.exists(output_file):
                with open(output_file, "r", encoding="utf-8") as f:
                    history = json.load(f)

            history.append(decision)
            # 保留最近20条记录
            history = history[-20:]

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)

            print(f"[DecisionOrchestrator] 决策已保存到 {output_file}")
        except Exception as e:
            print(f"[DecisionOrchestrator] 保存决策失败: {e}")

    def get_status(self) -> Dict[str, Any]:
        """获取编排中心状态"""
        return {
            "loaded_engines": list(self.engines.keys()),
            "total_decisions": len(self.decision_history),
            "registered_engines": list(REGISTERED_ENGINES.keys()),
        }

    def suggest_engines(self, context: str) -> List[Dict[str, Any]]:
        """根据上下文推荐合适的引擎"""
        suggestions = []

        for engine_name, config in REGISTERED_ENGINES.items():
            # 基于关键词匹配
            matches = sum(1 for t in config["triggers"] if t in context.lower())

            if matches > 0:
                suggestions.append({
                    "engine": engine_name,
                    "name": config["class"],
                    "relevance": matches,
                    "triggers": config["triggers"],
                })

        # 按相关性排序
        suggestions.sort(key=lambda x: x["relevance"], reverse=True)
        return suggestions[:5]

    def get_predictive_service(self) -> Dict[str, Any]:
        """获取基于预测的主动服务 - 整合预测引擎与决策编排

        Returns:
            包含预测结果和主动建议的字典
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "status": "no_predictive_engine",
            "prediction": None,
            "recommended_actions": [],
            "auto_action_needed": False,
        }

        # 尝试加载并调用预测引擎
        try:
            from predictive_prevention_engine import PredictivePreventionEngine
            predictor = PredictivePreventionEngine()
            prediction = predictor.scan_and_predict()
            result["prediction"] = prediction
            result["status"] = "success"

            # 分析预测结果，生成推荐行动
            if prediction.get("risk_level") in ["critical", "high"]:
                # 高风险：生成紧急行动建议
                result["auto_action_needed"] = True
                result["recommended_actions"] = [
                    {
                        "priority": "urgent",
                        "action": "通知用户",
                        "detail": f"系统风险等级: {prediction.get('risk_level')}",
                        "engines": ["notification"],
                    }
                ]

                # 如果有具体问题，添加对应的引擎建议
                for issue in prediction.get("detected_issues", []):
                    result["recommended_actions"].append({
                        "priority": "high",
                        "action": "问题修复",
                        "detail": f"{issue.get('description')}: {issue.get('prevention')}",
                        "engines": ["self_healing"],
                    })

            # 基于用户需求预测生成建议
            for pred in prediction.get("predictions", []):
                result["recommended_actions"].append({
                    "priority": "medium",
                    "action": "主动服务",
                    "detail": f"{pred.get('description')} (置信度: {pred.get('confidence', 0):.0%})",
                    "suggested_actions": pred.get("suggested_actions", []),
                    "engines": ["scenario", "notification"],
                })

            # 预防建议
            for suggestion in prediction.get("prevention_suggestions", []):
                if suggestion.get("action_type") != "none":
                    result["recommended_actions"].append({
                        "priority": "low" if suggestion.get("severity") == "low" else "medium",
                        "action": "预防建议",
                        "detail": suggestion.get("suggestion"),
                        "engines": ["notification"],
                    })

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        return result

    def proactive_service_from_prediction(self) -> str:
        """基于预测执行主动服务，返回格式化报告

        Returns:
            格式化的主动服务报告
        """
        service_result = self.get_predictive_service()

        if service_result["status"] != "success":
            return f"预测服务暂不可用: {service_result.get('error', '未知错误')}"

        prediction = service_result.get("prediction", {})
        risk_level = prediction.get("risk_level", "unknown")

        report_lines = [
            "=" * 50,
            f"基于预测的主动服务报告 - {service_result['timestamp']}",
            "=" * 50,
            "",
            f"【系统风险等级】{risk_level.upper()}",
            "",
        ]

        # 系统指标
        metrics = prediction.get("system_metrics", {})
        if metrics:
            report_lines.append("【系统状态】")
            if "memory_percent" in metrics:
                report_lines.append(f"  内存: {metrics['memory_percent']:.1f}%")
            if "cpu_percent" in metrics:
                report_lines.append(f"  CPU: {metrics['cpu_percent']:.1f}%")
            if "disk_percent" in metrics:
                report_lines.append(f"  磁盘: {metrics['disk_percent']:.1f}%")
            report_lines.append("")

        # 检测的问题
        issues = prediction.get("detected_issues", [])
        if issues:
            report_lines.append("【检测到的问题】")
            for issue in issues:
                report_lines.append(f"  [{issue.get('severity', 'unknown').upper()}] {issue.get('description')}")
                report_lines.append(f"    当前: {issue.get('current_value')} | 阈值: {issue.get('threshold')}")
                report_lines.append(f"    建议: {issue.get('prevention')}")
            report_lines.append("")

        # 预测的用户需求
        predictions = prediction.get("predictions", [])
        if predictions:
            report_lines.append("【预测的用户需求】")
            for pred in predictions:
                report_lines.append(f"  {pred.get('description')} (置信度: {pred.get('confidence', 0):.0%})")
                actions = pred.get("suggested_actions", [])
                if actions:
                    report_lines.append(f"    建议操作: {', '.join(actions)}")
            report_lines.append("")

        # 推荐的行动
        if service_result["recommended_actions"]:
            report_lines.append("【推荐行动】")
            for action in service_result["recommended_actions"]:
                priority_marker = "!" if action["priority"] == "urgent" else "!"
                report_lines.append(f"  [{action['priority'].upper()}{priority_marker}] {action['action']}")
                report_lines.append(f"    {action['detail']}")
            report_lines.append("")

        # 是否需要自动执行
        if service_result["auto_action_needed"]:
            report_lines.append("【自动执行】检测到高风险，需要主动干预")
        else:
            report_lines.append("【自动执行】系统运行正常，无需干预")

        report_lines.append("=" * 50)

        return "\n".join(report_lines)


# 单元测试
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="智能决策编排中心")
    parser.add_argument("command", nargs="?", default="test", help="命令: status, orchestrate, predictive-service, proactive, test")
    parser.add_argument("--input", "-i", help="用户输入（用于 orchestrate 命令）")
    parser.add_argument("--json", "-j", action="store_true", help="JSON 格式输出")

    args = parser.parse_args()

    orchestrator = DecisionOrchestrator()

    if args.command in ["predictive-service", "proactive", "预测服务", "主动服务"]:
        # 基于预测的主动服务
        if args.json:
            result = orchestrator.get_predictive_service()
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            report = orchestrator.proactive_service_from_prediction()
            print(report)

    elif args.command == "status":
        # 显示状态
        status = orchestrator.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.command == "orchestrate":
        # 执行编排
        if not args.input:
            print("错误: orchestrate 命令需要 --input 参数")
            sys.exit(1)
        result = orchestrator.orchestrate(args.input)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"状态: {result['status']}")
            print(f"选择引擎: {result['intent_analysis']['selected_engines']}")
            print(f"决策理由: {result['intent_analysis']['reasoning']}")
            print(f"执行结果数: {len(result['execution_results'])}")

    else:
        # 默认执行测试
        print("=== 智能决策编排中心测试 ===")

        # 测试状态获取
        print("\n1. 获取状态:")
        status = orchestrator.get_status()
        print(f"   已加载引擎: {status['loaded_engines']}")
        print(f"   注册引擎: {status['registered_engines']}")

        # 测试意图分析
        print("\n2. 测试意图分析:")
        test_inputs = [
            "帮我整理文件并提醒我",
            "诊断系统问题并修复",
            "记住我最喜欢的工作模式",
            "学习我的使用习惯并推荐场景",
        ]

        for test_input in test_inputs:
            intent = orchestrator.analyze_intent(test_input)
            print(f"\n   输入: {test_input}")
            print(f"   选择引擎: {intent['selected_engines']}")
            print(f"   决策理由: {intent['reasoning']}")

        # 测试编排执行
        print("\n3. 测试编排执行:")
        result = orchestrator.orchestrate("诊断系统问题")
        print(f"   状态: {result['status']}")
        print(f"   执行结果数: {len(result['execution_results'])}")

        # 测试预测主动服务
        print("\n4. 测试基于预测的主动服务:")
        proactive_report = orchestrator.proactive_service_from_prediction()
        print(proactive_report)

        print("\n=== 测试完成 ===")
    result = orchestrator.orchestrate("诊断系统问题")
    print(f"   状态: {result['status']}")
    print(f"   执行结果数: {len(result['execution_results'])}")

    print("\n=== 测试完成 ===")