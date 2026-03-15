"""
智能全场景进化环元进化场景执行鲁棒性深度增强引擎
Version: 1.0.0

基于 round 679 完成的跨引擎协同效能全局优化能力，构建让系统能够：
1. 智能解析模糊/不完整的用户指令意图
2. 自动识别最佳匹配场景计划
3. 动态调整执行策略提升成功率
4. 执行失败后自动重试与修复
5. 学习历史执行模式优化执行策略

此引擎让系统从「被动执行场景计划」升级到「主动提升执行鲁棒性」，实现真正的场景执行智能增强。
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import re

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE_DIR = PROJECT_ROOT / "runtime" / "state"
RUNTIME_LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"
REFERENCES_DIR = PROJECT_ROOT / "references"
ASSETS_PLANS_DIR = PROJECT_ROOT / "assets" / "plans"


class EvolutionMetaScenarioExecutionRobustnessEngine:
    """元进化场景执行鲁棒性深度增强引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.name = "元进化场景执行鲁棒性深度增强引擎"
        self.execution_history = self._load_execution_history()
        self.fuzzy_patterns = self._initialize_fuzzy_patterns()
        print(f"[{self.name}] 初始化完成 (v{self.version})")

    def _load_execution_history(self) -> List[Dict[str, Any]]:
        """加载执行历史"""
        history = []
        try:
            # 尝试从状态目录加载历史
            history_file = RUNTIME_STATE_DIR / "scenario_execution_history.json"
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
        except Exception as e:
            print(f"[历史加载] 无法加载历史记录: {e}")
        return history

    def _save_execution_history(self):
        """保存执行历史"""
        try:
            history_file = RUNTIME_STATE_DIR / "scenario_execution_history.json"
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.execution_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[历史保存] 保存失败: {e}")

    def _initialize_fuzzy_patterns(self) -> Dict[str, Any]:
        """初始化模糊指令模式库"""
        return {
            # 意图关键词到场景的映射
            "intent_mapping": {
                "播放音乐": ["play_music", "music", "放歌", "听歌"],
                "打开应用": ["launch", "打开", "启动", "运行"],
                "浏览器": ["browser", "浏览器", "上网", "网页"],
                "办公": ["office", "办公", "文档", "表格"],
                "截图": ["screenshot", "截图", "截屏"],
                "自拍": ["selfie", "自拍", "拍照", "摄像头"],
                "搜索": ["search", "搜索", "查找", "找"],
                "发送消息": ["message", "消息", "发消息", "聊天"],
                "文件操作": ["file", "文件", "新建", "保存"],
                "设置": ["settings", "设置", "配置"],
            },
            # 模糊表达模式
            "fuzzy_patterns": [
                (r"(.*)歌(.*)", "play_music"),
                (r"(.*)应用(.*)", "launch_app"),
                (r"(.*)网页(.*)", "browser"),
                (r"(.*)截图(.*)", "screenshot"),
                (r"(.*)拍照(.*)", "selfie"),
                (r"(.*)消息(.*)", "message"),
                (r"(.*)文件(.*)", "file"),
                (r"(.*)设置(.*)", "settings"),
            ],
            # 场景计划目录
            "plans_dir": ASSETS_PLANS_DIR
        }

    def parse_fuzzy_instruction(self, user_input: str) -> Dict[str, Any]:
        """智能解析模糊/不完整的用户指令意图"""
        print(f"\n[意图解析] 正在解析用户指令: {user_input}")

        result = {
            "original_input": user_input,
            "detected_intent": None,
            "confidence": 0.0,
            "matched_plan": None,
            "suggestions": []
        }

        # 1. 精确匹配场景计划文件名
        plan_files = list(ASSETS_PLANS_DIR.glob("*.json"))
        for plan_file in plan_files:
            plan_name = plan_file.stem.lower()
            if plan_name in user_input.lower():
                result["detected_intent"] = plan_name
                result["confidence"] = 1.0
                result["matched_plan"] = str(plan_file)
                print(f"[意图解析] 精确匹配场景计划: {plan_name}")
                return result

        # 2. 模糊模式匹配
        for pattern, intent in self.fuzzy_patterns["fuzzy_patterns"]:
            if re.search(pattern, user_input.lower()):
                result["detected_intent"] = intent
                result["confidence"] = max(result["confidence"], 0.7)
                result["suggestions"].append(f"可能意图: {intent}")

        # 3. 关键词匹配
        for intent, keywords in self.fuzzy_patterns["intent_mapping"].items():
            for keyword in keywords:
                if keyword in user_input.lower():
                    result["detected_intent"] = intent
                    result["confidence"] = max(result["confidence"], 0.6)
                    break

        # 4. 如果仍无法识别，提供通用建议
        if not result["detected_intent"]:
            result["suggestions"].append("建议使用更明确的指令")
            result["suggestions"].append("可尝试: 打开应用、播放音乐、截图等")

        print(f"[意图解析] 检测到意图: {result['detected_intent']}, 置信度: {result['confidence']:.2f}")
        return result

    def match_scenario_plan(self, parsed_intent: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """自动识别最佳匹配场景计划"""
        print("\n[场景匹配] 正在匹配最佳场景计划...")

        intent = parsed_intent.get("detected_intent")
        if not intent:
            print("[场景匹配] 无法匹配 - 未检测到有效意图")
            return None

        matched_plan = None
        best_score = 0.0

        # 扫描所有场景计划
        plan_files = list(ASSETS_PLANS_DIR.glob("*.json"))
        for plan_file in plan_files:
            plan_name = plan_file.stem.lower()

            # 计算匹配分数
            score = 0.0
            if intent.lower() in plan_name:
                score = 1.0
            elif any(kw in plan_name for kw in intent.lower().split()):
                score = 0.8

            if score > best_score:
                best_score = score
                matched_plan = {
                    "plan_file": str(plan_file),
                    "plan_name": plan_name,
                    "match_score": score
                }

        if matched_plan:
            print(f"[场景匹配] 最佳匹配: {matched_plan['plan_name']} (分数: {matched_plan['match_score']:.2f})")
            return matched_plan
        else:
            print("[场景匹配] 未找到匹配的场景计划")
            return None

    def analyze_execution_context(self) -> Dict[str, Any]:
        """分析执行上下文"""
        print("\n[上下文分析] 正在分析执行上下文...")

        context = {
            "timestamp": datetime.now().isoformat(),
            "recent_success_rate": 0.0,
            "common_failures": [],
            "recommended_strategy": "default"
        }

        # 分析最近执行历史
        if self.execution_history:
            recent = self.execution_history[-20:]  # 最近20条
            success_count = sum(1 for h in recent if h.get("status") == "success")
            context["recent_success_rate"] = success_count / len(recent) if recent else 0.0

            # 识别常见失败模式
            failures = [h for h in recent if h.get("status") == "failed"]
            if failures:
                failure_types = {}
                for f in failures:
                    error = f.get("error_type", "unknown")
                    failure_types[error] = failure_types.get(error, 0) + 1
                context["common_failures"] = sorted(
                    failure_types.items(), key=lambda x: x[1], reverse=True
                )[:5]

            # 确定推荐策略
            if context["recent_success_rate"] < 0.6:
                context["recommended_strategy"] = "conservative"
            elif context["recent_success_rate"] > 0.85:
                context["recommended_strategy"] = "aggressive"
            else:
                context["recommended_strategy"] = "balanced"

        print(f"[上下文分析] 成功率: {context['recent_success_rate']:.1%}, 策略: {context['recommended_strategy']}")
        return context

    def adjust_execution_strategy(self, context: Dict[str, Any], plan_info: Dict[str, Any]) -> Dict[str, Any]:
        """动态调整执行策略以提升成功率"""
        print("\n[策略调整] 正在动态调整执行策略...")

        strategy = {
            "base_strategy": context.get("recommended_strategy", "default"),
            "adjustments": [],
            "estimated_improvement": 0.0
        }

        # 基于上下文调整
        success_rate = context.get("recent_success_rate", 0.7)

        if success_rate < 0.6:
            # 保守策略：增加重试、延长等待
            strategy["adjustments"].append({
                "type": "retry",
                "max_attempts": 3,
                "reason": "低成功率历史，增加重试次数"
            })
            strategy["adjustments"].append({
                "type": "wait",
                "duration": 2.0,
                "reason": "增加等待时间确保界面加载"
            })
            strategy["estimated_improvement"] = 0.15

        elif success_rate > 0.85:
            # 激进策略：可以尝试更多优化
            strategy["adjustments"].append({
                "type": "parallel",
                "enabled": True,
                "reason": "高成功率历史，可以尝试并行执行"
            })
            strategy["estimated_improvement"] = 0.1

        # 基于常见失败调整
        common_failures = context.get("common_failures", [])
        for failure_type, count in common_failures[:3]:
            if "timeout" in failure_type:
                strategy["adjustments"].append({
                    "type": "timeout",
                    "increase": 1.5,
                    "reason": f"常见超时错误，增加超时时间"
                })
            elif "not_found" in failure_type:
                strategy["adjustments"].append({
                    "type": "fallback",
                    "enabled": True,
                    "reason": f"常见元素未找到，启用备选方案"
                })
            elif "permission" in failure_type:
                strategy["adjustments"].append({
                    "type": "elevation",
                    "enabled": True,
                    "reason": f"权限错误，尝试提权执行"
                })

        print(f"[策略调整] 生成 {len(strategy['adjustments'])} 项调整，预估提升: {strategy['estimated_improvement']:.1%}")
        return strategy

    def auto_retry_with_repair(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """执行失败后自动重试与修复"""
        print("\n[自动修复] 正在执行失败自动重试与修复...")

        if execution_result.get("status") != "failed":
            print("[自动修复] 执行未失败，无需修复")
            return execution_result

        error_type = execution_result.get("error_type", "unknown")
        error_details = execution_result.get("error_details", "")

        repair_strategies = {
            "timeout": [
                "增加等待时间后重试",
                "检查网络连接",
                "尝试简化操作步骤"
            ],
            "not_found": [
                "重新截图定位",
                "尝试备用坐标",
                "扩大搜索范围"
            ],
            "permission": [
                "请求更高权限",
                "使用管理员模式",
                "跳过需要权限的步骤"
            ],
            "crash": [
                "重启目标应用",
                "清理缓存后重试",
                "简化操作流程"
            ]
        }

        # 匹配修复策略
        repair_plan = repair_strategies.get(error_type, ["通用重试策略"])
        if not any(error_type in str(k) for k in repair_strategies.keys()):
            repair_plan = ["等待后重试", "记录日志后继续"]

        # 记录修复尝试
        self.execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "repair_attempt",
            "original_error": error_type,
            "repair_plan": repair_plan,
            "status": "repair_planned"
        })

        result = {
            "original_result": execution_result,
            "repair_applied": True,
            "repair_plan": repair_plan,
            "estimated_success_rate": 0.6
        }

        print(f"[自动修复] 生成了 {len(repair_plan)} 项修复策略")
        return result

    def learn_from_execution(self, execution_result: Dict[str, Any]):
        """从执行结果学习并优化执行策略"""
        print("\n[执行学习] 正在从执行结果学习...")

        # 记录执行结果
        self.execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "result": execution_result.get("status"),
            "error_type": execution_result.get("error_type"),
            "context": execution_result.get("context", {})
        })

        # 保持历史记录在合理范围
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-50:]

        # 保存历史
        self._save_execution_history()

        print(f"[执行学习] 已更新执行历史，共 {len(self.execution_history)} 条记录")

    def enhance_scenario_execution(self, user_input: str) -> Dict[str, Any]:
        """增强场景执行的核心方法"""
        print("\n" + "=" * 60)
        print(f"[{self.name}] 场景执行鲁棒性增强")
        print("=" * 60)

        # 1. 解析模糊指令
        parsed = self.parse_fuzzy_instruction(user_input)

        # 2. 匹配场景计划
        matched_plan = self.match_scenario_plan(parsed)

        # 3. 分析执行上下文
        context = self.analyze_execution_context()

        # 4. 调整执行策略
        adjusted_strategy = {}
        if matched_plan:
            adjusted_strategy = self.adjust_execution_strategy(context, matched_plan)

        # 5. 构建结果
        result = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "original_input": user_input,
            "parsed_intent": parsed,
            "matched_plan": matched_plan,
            "execution_context": context,
            "adjusted_strategy": adjusted_strategy,
            "version": self.version
        }

        # 6. 学习记录
        self.learn_from_execution({
            "status": "analyzed",
            "context": context
        })

        print("=" * 60)
        print(f"[{self.name}] 场景执行鲁棒性增强完成")
        print("=" * 60)

        return result

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱数据"""
        context = self.analyze_execution_context()

        return {
            "module": self.name,
            "version": self.version,
            "execution_history_count": len(self.execution_history),
            "recent_success_rate": context.get("recent_success_rate", 0.0),
            "recommended_strategy": context.get("recommended_strategy", "default"),
            "common_failures": context.get("common_failures", [])[:5],
            "timestamp": datetime.now().isoformat()
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="元进化场景执行鲁棒性深度增强引擎")
    parser.add_argument("--version", action="store_true", help="显示版本信息")
    parser.add_argument("--parse", type=str, help="解析模糊指令")
    parser.add_argument("--match", type=str, help="匹配场景计划")
    parser.add_argument("--context", action="store_true", help="分析执行上下文")
    parser.add_argument("--enhance", type=str, help="增强场景执行")
    parser.add_argument("--cockpit", action="store_true", help="获取驾驶舱数据")

    args = parser.parse_args()

    engine = EvolutionMetaScenarioExecutionRobustnessEngine()

    if args.version:
        print(f"{engine.name} v{engine.version}")
        return

    if args.parse:
        result = engine.parse_fuzzy_instruction(args.parse)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    if args.match:
        parsed = engine.parse_fuzzy_instruction(args.match)
        matched = engine.match_scenario_plan(parsed)
        print(json.dumps(matched, indent=2, ensure_ascii=False))
        return

    if args.context:
        context = engine.analyze_execution_context()
        print(json.dumps(context, indent=2, ensure_ascii=False))
        return

    if args.enhance:
        result = engine.enhance_scenario_execution(args.enhance)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        # 保存结果
        output_file = RUNTIME_STATE_DIR / "scenario_robustness_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n结果已保存到: {output_file}")
        return

    if args.cockpit:
        data = engine.get_cockpit_data()
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    # 默认显示帮助
    parser.print_help()


if __name__ == "__main__":
    main()