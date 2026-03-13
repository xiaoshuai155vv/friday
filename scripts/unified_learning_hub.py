#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能统一学习中枢引擎
整合分散在60+引擎中的反馈学习、偏好学习、执行策略学习、元学习等能力，形成统一的自主学习体系

功能：
1. 学习能力整合 - 统一调用各学习模块（反馈学习、偏好学习、执行策略学习、元学习）
2. 跨模块学习协调 - 协调多个学习模块的输出，形成综合学习结果
3. 统一学习入口 - 提供一站式的学习统计和洞察
4. 学习效果评估 - 评估各学习模块的效果，优化学习策略
5. 主动学习建议 - 基于学习结果生成主动优化建议

工作原理：
- 反馈学习引擎：学习用户对推荐的反馈（接受/拒绝/忽略）
- 偏好学习引擎：学习用户的任务偏好设置
- 执行策略学习引擎：从工作流执行历史学习最优执行策略
- 元学习引擎：从进化历史中学习进化模式
- 本引擎作为统一入口，协调各模块并提供综合洞察
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

# 确保 scripts 目录在路径中
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RUNTIME_DIR = os.path.join(SCRIPT_DIR, '..')
STATE_DIR = os.path.join(RUNTIME_DIR, 'state')

# 导入各学习模块
sys.path.insert(0, SCRIPT_DIR)
try:
    from feedback_learning_engine import FeedbackLearningEngine, get_learning_engine as get_feedback_engine
except ImportError:
    FeedbackLearningEngine = None

try:
    from task_preference_engine import TaskPreferenceEngine, get_preference_engine
except ImportError:
    TaskPreferenceEngine = None

try:
    from adaptive_learning_engine import AdaptiveLearningEngine, get_adaptive_learning_engine
except ImportError:
    AdaptiveLearningEngine = None


class UnifiedLearningHub:
    """智能统一学习中枢引擎"""

    def __init__(self):
        self.learning_modules = {}
        self._initialize_learning_modules()
        self.hub_state_file = os.path.join(STATE_DIR, 'unified_learning_hub_state.json')

    def _initialize_learning_modules(self):
        """初始化各学习模块"""
        # 反馈学习模块
        if FeedbackLearningEngine:
            try:
                self.learning_modules['feedback_learning'] = get_feedback_engine()
                print("[UnifiedLearningHub] 已加载反馈学习模块")
            except Exception as e:
                print(f"[UnifiedLearningHub] 加载反馈学习模块失败: {e}")

        # 偏好学习模块
        if TaskPreferenceEngine:
            try:
                self.learning_modules['preference_learning'] = get_preference_engine()
                print("[UnifiedLearningHub] 已加载偏好学习模块")
            except Exception as e:
                print(f"[UnifiedLearningHub] 加载偏好学习模块失败: {e}")

        # 自适应学习模块
        if AdaptiveLearningEngine:
            try:
                self.learning_modules['adaptive_learning'] = get_adaptive_learning_engine()
                print("[UnifiedLearningHub] 已加载自适应学习模块")
            except Exception as e:
                print(f"[UnifiedLearningHub] 加载自适应学习模块失败: {e}")

        print(f"[UnifiedLearningHub] 共加载 {len(self.learning_modules)} 个学习模块")

    def get_hub_status(self) -> Dict[str, Any]:
        """获取学习中枢状态"""
        status = {
            "hub_active": True,
            "modules_loaded": list(self.learning_modules.keys()),
            "module_count": len(self.learning_modules),
            "last_updated": datetime.now().isoformat()
        }

        # 获取各模块状态
        module_status = {}
        for name, module in self.learning_modules.items():
            try:
                if hasattr(module, 'get_learning_stats'):
                    stats = module.get_learning_stats()
                    module_status[name] = {
                        "active": True,
                        "data_points": stats.get("total_feedbacks", stats.get("total_interactions", 0))
                    }
                elif hasattr(module, 'get_stats'):
                    stats = module.get_stats()
                    module_status[name] = {
                        "active": True,
                        "data_points": stats.get("total", 0)
                    }
                else:
                    module_status[name] = {"active": True}
            except Exception as e:
                module_status[name] = {"active": False, "error": str(e)}

        status["module_details"] = module_status
        return status

    def get_unified_stats(self) -> Dict[str, Any]:
        """获取统一的统计数据"""
        unified_stats = {
            "hub_status": self.get_hub_status(),
            "module_stats": {}
        }

        # 收集各模块统计
        for name, module in self.learning_modules.items():
            try:
                if hasattr(module, 'get_learning_stats'):
                    unified_stats["module_stats"][name] = module.get_learning_stats()
                elif hasattr(module, 'get_stats'):
                    unified_stats["module_stats"][name] = module.get_stats()
            except Exception as e:
                unified_stats["module_stats"][name] = {"error": str(e)}

        # 计算总体数据点
        total_data_points = 0
        for name, stats in unified_stats["module_stats"].items():
            if "error" not in stats:
                total_data_points += stats.get("total_feedbacks", stats.get("total_interactions", stats.get("total", 0)))

        unified_stats["total_data_points"] = total_data_points
        unified_stats["active_modules"] = len(self.learning_modules)

        return unified_stats

    def get_unified_insights(self) -> Dict[str, Any]:
        """获取统一的洞察"""
        insights = {
            "hub_active": True,
            "module_insights": {},
            "cross_module_insights": [],
            "recommendations": []
        }

        # 收集各模块洞察
        for name, module in self.learning_modules.items():
            try:
                if hasattr(module, 'analyze_feedback_patterns'):
                    insights["module_insights"][name] = module.analyze_feedback_patterns()
                elif hasattr(module, 'get_insights'):
                    insights["module_insights"][name] = module.get_insights()
            except Exception as e:
                insights["module_insights"][name] = {"error": str(e)}

        # 生成跨模块洞察
        all_preferences = []
        for name, module_insight in insights["module_insights"].items():
            if "preferred_scenes" in module_insight:
                all_preferences.extend(module_insight.get("preferred_scenes", []))
            if "preferred_workflows" in module_insight:
                all_preferences.extend(module_insight.get("preferred_workflows", []))

        if all_preferences:
            # 找出最常见的偏好
            from collections import Counter
            pref_counts = Counter(all_preferences)
            top_prefs = pref_counts.most_common(3)
            if top_prefs:
                insights["cross_module_insights"].append({
                    "type": "user_preference",
                    "message": f"根据多模块学习，您最喜欢的功能包括: {', '.join([p[0] for p in top_prefs])}"
                })

        # 生成主动建议
        if len(self.learning_modules) >= 2:
            insights["recommendations"].append({
                "type": "integration",
                "message": f"已整合 {len(self.learning_modules)} 个学习模块，可以提供更全面的用户画像"
            })

        total_data = insights.get("total_data_points", 0)
        if total_data < 10:
            insights["recommendations"].append({
                "type": "data_growth",
                "message": "学习数据较少，建议多使用推荐功能以帮助系统学习您的偏好"
            })

        return insights

    def record_feedback(self, recommendation_id: str, recommendation: Dict[str, Any],
                        feedback_type: str) -> Dict[str, Any]:
        """记录反馈并学习（委托给反馈学习模块）"""
        if 'feedback_learning' in self.learning_modules:
            return self.learning_modules['feedback_learning'].record_feedback(
                recommendation_id, recommendation, feedback_type
            )
        return {"success": False, "message": "反馈学习模块未加载"}

    def get_preference(self, task_type: str) -> Optional[Dict[str, Any]]:
        """获取任务偏好（委托给偏好学习模块）"""
        if 'preference_learning' in self.learning_modules:
            return self.learning_modules['preference_learning'].get_preference(task_type)
        return None

    def get_adaptive_strategy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """获取自适应策略（委托给自适应学习模块）"""
        if 'adaptive_learning' in self.learning_modules:
            return self.learning_modules['adaptive_learning'].get_adaptive_strategy(context)
        return {"strategy": "default", "confidence": 0.5}

    def learn_from_execution(self, task_type: str, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """从执行结果学习"""
        result = {
            "success": True,
            "learned_by": []
        }

        # 让各模块从执行结果学习
        for name, module in self.learning_modules.items():
            try:
                if hasattr(module, 'learn_from_execution'):
                    module.learn_from_execution(task_type, execution_result)
                    result["learned_by"].append(name)
                elif hasattr(module, 'record_execution'):
                    module.record_execution(task_type, execution_result)
                    result["learned_by"].append(name)
            except Exception as e:
                print(f"[UnifiedLearningHub] 模块 {name} 学习失败: {e}")

        return result

    def get_learning_coverage(self) -> Dict[str, Any]:
        """获取学习覆盖范围"""
        coverage = {
            "feedback_learning": False,
            "preference_learning": False,
            "adaptive_learning": False,
            "strategy_learning": False,
            "meta_learning": False
        }

        for name in self.learning_modules.keys():
            if 'feedback' in name:
                coverage["feedback_learning"] = True
            if 'preference' in name:
                coverage["preference_learning"] = True
            if 'adaptive' in name:
                coverage["adaptive_learning"] = True
            if 'strategy' in name:
                coverage["strategy_learning"] = True
            if 'meta' in name:
                coverage["meta_learning"] = True

        coverage["total_covered"] = sum(coverage.values())
        coverage["total_types"] = len(coverage) - 1  # 减去 total_covered

        return coverage


# 全局实例
_hub_instance = None

def get_unified_learning_hub() -> UnifiedLearningHub:
    """获取统一学习中枢单例"""
    global _hub_instance
    if _hub_instance is None:
        _hub_instance = UnifiedLearningHub()
    return _hub_instance


# CLI 接口
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='智能统一学习中枢引擎')
    parser.add_argument('action', nargs='?', default='status',
                       choices=['status', 'stats', 'insights', 'coverage', 'learn'],
                       help='动作')
    parser.add_argument('--json', '-j', action='store_true', help='输出JSON格式')
    parser.add_argument('--task-type', help='任务类型')
    parser.add_argument('--feedback-type', choices=['accepted', 'rejected', 'ignored'],
                       help='反馈类型')
    parser.add_argument('--rec-id', help='推荐ID')
    parser.add_argument('--rec-json', help='推荐内容(JSON)')

    args = parser.parse_args()

    hub = get_unified_learning_hub()

    if args.action == 'status':
        status = hub.get_hub_status()
        if args.json:
            print(json.dumps(status, ensure_ascii=False, indent=2))
        else:
            print("=== 统一学习中枢状态 ===")
            print(f"中枢活跃: {status['hub_active']}")
            print(f"已加载模块: {', '.join(status['modules_loaded'])}")
            print(f"模块数量: {status['module_count']}")
            print(f"最后更新: {status['last_updated']}")

    elif args.action == 'stats':
        stats = hub.get_unified_stats()
        if args.json:
            print(json.dumps(stats, ensure_ascii=False, indent=2))
        else:
            print("=== 统一学习统计 ===")
            print(f"活跃模块数: {stats['active_modules']}")
            print(f"总数据点: {stats['total_data_points']}")
            print("\n各模块统计:")
            for name, module_stats in stats.get('module_stats', {}).items():
                if 'error' not in module_stats:
                    print(f"\n[{name}]")
                    for k, v in module_stats.items():
                        if isinstance(v, dict):
                            print(f"  {k}: {json.dumps(v, ensure_ascii=False)}")
                        else:
                            print(f"  {k}: {v}")

    elif args.action == 'insights':
        insights = hub.get_unified_insights()
        if args.json:
            print(json.dumps(insights, ensure_ascii=False, indent=2))
        else:
            print("=== 统一学习洞察 ===")
            if insights.get('cross_module_insights'):
                print("\n跨模块洞察:")
                for insight in insights['cross_module_insights']:
                    print(f"  - {insight.get('message', '')}")
            if insights.get('recommendations'):
                print("\n建议:")
                for rec in insights['recommendations']:
                    print(f"  - [{rec.get('type', '')}] {rec.get('message', '')}")

    elif args.action == 'coverage':
        coverage = hub.get_learning_coverage()
        if args.json:
            print(json.dumps(coverage, ensure_ascii=False, indent=2))
        else:
            print("=== 学习能力覆盖 ===")
            for k, v in coverage.items():
                if k != 'total_types':
                    print(f"  {k}: 是" if v else f"  {k}: 否")
            print(f"\n覆盖率: {coverage['total_covered']}/{coverage['total_types']}")

    elif args.action == 'learn':
        if args.task_type:
            result = hub.learn_from_execution(args.task_type, {"result": "success"})
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(f"学习结果: 被以下模块处理 {result.get('learned_by', [])}")
        else:
            print("请指定 --task-type")