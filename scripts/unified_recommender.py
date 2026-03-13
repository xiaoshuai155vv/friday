#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能统一推荐引擎
整合场景推荐、工作流推荐、引擎编排等多个推荐能力，提供统一的智能推荐入口

功能：
1. 统一推荐接口 - 一个入口获取所有类型的推荐
2. 多引擎协作 - 整合场景推荐引擎、工作流推荐引擎
3. 智能排序 - 根据置信度和优先级对推荐进行综合排序
4. 推荐理由生成 - 为每个推荐生成清晰的推荐理由
5. 推荐历史记录 - 记录推荐反馈，持续优化推荐质量
"""

import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict

# 确保 scripts 目录在路径中
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RUNTIME_DIR = os.path.join(SCRIPT_DIR, '..')
STATE_DIR = os.path.join(RUNTIME_DIR, 'state')

# 导入已有的推荐引擎
sys.path.insert(0, SCRIPT_DIR)

# 尝试导入场景推荐引擎
try:
    from scenario_recommender import get_recommendations as get_scenario_recommendations, load_user_behavior, get_time_period, get_focus_state
    SCENARIO_RECOMMENDER_AVAILABLE = True
except ImportError:
    SCENARIO_RECOMMENDER_AVAILABLE = False

# 尝试导入工作流推荐引擎
try:
    from workflow_smart_recommender import WorkflowSmartRecommenderEngine
    WORKFLOW_RECOMMENDER_AVAILABLE = True
except ImportError:
    WORKFLOW_RECOMMENDER_AVAILABLE = False

# 尝试导入决策编排中心
try:
    from decision_orchestrator import DecisionOrchestrator
    DECISION_ORCHESTRATOR_AVAILABLE = True
except ImportError:
    DECISION_ORCHESTRATOR_AVAILABLE = False


@dataclass
class UnifiedRecommendation:
    """统一推荐"""
    recommendation_id: str
    recommendation_type: str  # scene, workflow, action, engine
    name: str
    description: str
    reason: str
    confidence: float  # 0-1
    priority: int  # 1-5, 1 最高
    source: str  # 来自哪个推荐引擎
    action: str  # 可执行的命令或动作
    metadata: Dict[str, Any] = field(default_factory=dict)


class UnifiedRecommenderEngine:
    """智能统一推荐引擎主类"""

    def __init__(self):
        self.recommendations_history_file = os.path.join(STATE_DIR, 'unified_recommendations_history.json')
        self.feedback_file = os.path.join(STATE_DIR, 'recommendation_feedback.json')

        # 初始化子引擎
        self.scenario_engine = None
        self.workflow_engine = None
        self.orchestrator = None

        if SCENARIO_RECOMMENDER_AVAILABLE:
            try:
                self.scenario_engine = True  # 标记可用
            except Exception as e:
                print(f"场景推荐引擎初始化失败: {e}")

        if WORKFLOW_RECOMMENDER_AVAILABLE:
            try:
                self.workflow_engine = WorkflowSmartRecommenderEngine()
            except Exception as e:
                print(f"工作流推荐引擎初始化失败: {e}")

        if DECISION_ORCHESTRATOR_AVAILABLE:
            try:
                self.orchestrator = DecisionOrchestrator()
            except Exception as e:
                print(f"决策编排中心初始化失败: {e}")

    def get_all_recommendations(self, context: Dict[str, Any] = None, limit: int = 10) -> List[UnifiedRecommendation]:
        """获取所有类型的推荐（统一入口）"""
        context = context or {}
        all_recommendations = []

        # 1. 获取场景推荐
        if self.scenario_engine:
            scene_recs = self._get_scenario_recommendations(context, limit)
            all_recommendations.extend(scene_recs)

        # 2. 获取工作流推荐
        if self.workflow_engine:
            workflow_recs = self._get_workflow_recommendations(context, limit)
            all_recommendations.extend(workflow_recs)

        # 3. 添加智能动作推荐
        action_recs = self._get_action_recommendations(context, limit)
        all_recommendations.extend(action_recs)

        # 4. 添加引擎推荐（推荐使用某个引擎）
        engine_recs = self._get_engine_recommendations(context, limit)
        all_recommendations.extend(engine_recs)

        # 综合排序
        sorted_recommendations = self._rank_recommendations(all_recommendations)

        return sorted_recommendations[:limit]

    def _get_scenario_recommendations(self, context: Dict[str, Any], limit: int) -> List[UnifiedRecommendation]:
        """获取场景推荐"""
        recommendations = []

        try:
            if SCENARIO_RECOMMENDER_AVAILABLE:
                # 调用场景推荐引擎
                result = get_scenario_recommendations()

                for i, rec in enumerate(result.get('recommendations', [])[:limit]):
                    recommendations.append(UnifiedRecommendation(
                        recommendation_id=f"scene_{i}_{datetime.now().timestamp()}",
                        recommendation_type="scene",
                        name=rec.get('scene', ''),
                        description=f"执行场景计划: {rec.get('scene', '')}",
                        reason=rec.get('reason', '基于时间段和用户偏好推荐'),
                        confidence=0.8 if rec.get('priority') == 'high' else 0.6,
                        priority=1 if rec.get('priority') == 'high' else 3,
                        source="scenario_recommender",
                        action=f"run_plan assets/plans/{rec.get('scene', '')}",
                        metadata={"scene": rec.get('scene'), "priority_label": rec.get('priority')}
                    ))
        except Exception as e:
            print(f"获取场景推荐失败: {e}")

        return recommendations

    def _get_workflow_recommendations(self, context: Dict[str, Any], limit: int) -> List[UnifiedRecommendation]:
        """获取工作流推荐"""
        recommendations = []

        try:
            if self.workflow_engine:
                # 调用工作流推荐引擎
                wf_recommendations = self.workflow_engine.get_recommendations(context, limit)

                for i, rec in enumerate(wf_recommendations):
                    recommendations.append(UnifiedRecommendation(
                        recommendation_id=f"workflow_{i}_{datetime.now().timestamp()}",
                        recommendation_type="workflow",
                        name=rec.get('workflow_name', ''),
                        description=rec.get('workflow_path', ''),
                        reason=rec.get('reason', '基于用户习惯和时间模式推荐'),
                        confidence=rec.get('confidence', 0.7),
                        priority=rec.get('priority', 2),
                        source="workflow_smart_recommender",
                        action=rec.get('workflow_path', ''),
                        metadata={"workflow_name": rec.get('workflow_name'), "based_on": rec.get('based_on', [])}
                    ))
        except Exception as e:
            print(f"获取工作流推荐失败: {e}")

        return recommendations

    def _get_action_recommendations(self, context: Dict[str, Any], limit: int) -> List[UnifiedRecommendation]:
        """获取动作推荐（基于系统状态和上下文的即时动作）"""
        recommendations = []

        # 获取当前时间段
        hour = datetime.now().hour
        dow = datetime.now().weekday()

        # 基于时间的动作推荐
        if 6 <= hour < 9:
            recommendations.append(UnifiedRecommendation(
                recommendation_id=f"action_{datetime.now().timestamp()}",
                recommendation_type="action",
                name="早晨检查",
                description="检查今日待办事项和消息",
                reason="早晨是检查工作消息的最佳时间",
                confidence=0.7,
                priority=2,
                source="unified_recommender",
                action="do 已安装应用",
                metadata={"time_period": "morning"}
            ))

        if 14 <= hour < 18:
            # 下午工作时间推荐
            focus_state = {}
            try:
                if SCENARIO_RECOMMENDER_AVAILABLE:
                    focus_state = get_focus_state()
            except:
                pass

            if not focus_state.get('active', False):
                recommendations.append(UnifiedRecommendation(
                    recommendation_id=f"action_{datetime.now().timestamp()}",
                    recommendation_type="action",
                    name="开启专注模式",
                    description="进入下午工作时段，开启专注模式",
                    reason="下午是高效工作时段，建议开启专注模式",
                    confidence=0.6,
                    priority=3,
                    source="unified_recommender",
                    action="do 专注",
                    metadata={"time_period": "afternoon"}
                ))

        # 基于星期的推荐
        if dow == 0:  # 周一
            recommendations.append(UnifiedRecommendation(
                recommendation_id=f"action_{datetime.now().timestamp()}",
                recommendation_type="action",
                name="周计划制定",
                description="制定本周工作计划",
                reason="周一适合规划本周工作",
                confidence=0.7,
                priority=2,
                source="unified_recommender",
                action="do 打开记事本",
                metadata={"day_of_week": "monday"}
            ))

        if dow == 4:  # 周五
            recommendations.append(UnifiedRecommendation(
                recommendation_id=f"action_{datetime.now().timestamp()}",
                recommendation_type="action",
                name="周末准备",
                description="检查本周任务完成情况",
                reason="周五适合回顾本周工作",
                confidence=0.6,
                priority=3,
                source="unified_recommender",
                action="do 打开日历",
                metadata={"day_of_week": "friday"}
            ))

        return recommendations[:limit]

    def _get_engine_recommendations(self, context: Dict[str, Any], limit: int) -> List[UnifiedRecommendation]:
        """获取引擎推荐（推荐使用某个智能引擎）"""
        recommendations = []

        # 根据用户需求推荐合适的引擎
        user_query = context.get('query', '').lower()

        # 如果用户提到特定关键词，推荐相应引擎
        if '学习' in user_query or '适应' in user_query or '个性化' in user_query:
            recommendations.append(UnifiedRecommendation(
                recommendation_id=f"engine_{datetime.now().timestamp()}",
                recommendation_type="engine",
                name="智能学习与适应引擎",
                description="从交互历史中学习行为模式，自动调整推荐策略",
                reason="您提到了学习/适应相关需求",
                confidence=0.9,
                priority=1,
                source="unified_recommender",
                action="do 学习",
                metadata={"recommended_engine": "adaptive_learning_engine"}
            ))

        if '预测' in user_query or '预防' in user_query or '预警' in user_query:
            recommendations.append(UnifiedRecommendation(
                recommendation_id=f"engine_{datetime.now().timestamp()}",
                recommendation_type="engine",
                name="主动预测与预防引擎",
                description="主动检测并预防潜在问题",
                reason="您提到了预测/预防相关需求",
                confidence=0.9,
                priority=1,
                source="unified_recommender",
                action="do 预测",
                metadata={"recommended_engine": "predictive_prevention_engine"}
            ))

        if '决策' in user_query or '编排' in user_query or '调度' in user_query:
            recommendations.append(UnifiedRecommendation(
                recommendation_id=f"engine_{datetime.now().timestamp()}",
                recommendation_type="engine",
                name="智能决策编排中心",
                description="综合分析意图和状态，智能调度引擎协同工作",
                reason="您提到了决策/编排相关需求",
                confidence=0.9,
                priority=1,
                source="unified_recommender",
                action="do 决策",
                metadata={"recommended_engine": "decision_orchestrator"}
            ))

        return recommendations[:limit]

    def _rank_recommendations(self, recommendations: List[UnifiedRecommendation]) -> List[UnifiedRecommendation]:
        """综合排序推荐"""
        # 综合考虑置信度、优先级和来源
        scored = []
        for rec in recommendations:
            # 计算综合得分
            score = (
                rec.confidence * 0.4 +  # 置信度权重 40%
                (6 - rec.priority) * 0.3 +  # 优先级权重 30% (priority 1-5, 转换到 5-1)
                0.3  # 基础分 30%
            )
            scored.append((score, rec))

        # 按得分降序排序
        scored.sort(key=lambda x: x[0], reverse=True)

        return [rec for _, rec in scored]

    def record_feedback(self, recommendation_id: str, feedback: str):
        """记录用户对推荐的反馈"""
        try:
            feedback_data = {}
            if os.path.exists(self.feedback_file):
                with open(self.feedback_file, 'r', encoding='utf-8') as f:
                    feedback_data = json.load(f)

            if 'feedbacks' not in feedback_data:
                feedback_data['feedbacks'] = []

            feedback_data['feedbacks'].append({
                'recommendation_id': recommendation_id,
                'feedback': feedback,
                'timestamp': datetime.now().isoformat()
            })

            with open(self.feedback_file, 'w', encoding='utf-8') as f:
                json.dump(feedback_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"记录反馈失败: {e}")

    def get_recommendation_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取推荐历史"""
        try:
            if os.path.exists(self.recommendations_history_file):
                with open(self.recommendations_history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    return history.get('recommendations', [])[-limit:]
        except Exception as e:
            print(f"获取推荐历史失败: {e}")
        return []

    def execute_recommendation(self, recommendation_id: str = None, recommendation: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行推荐 - 通过决策编排中心或直接执行推荐的操作

        实现推荐→决策→执行的自动闭环。支持：
        1. 通过决策编排中心执行（场景/工作流）
        2. 直接执行 run_plan 场景计划
        3. 直接执行 do.py 命令

        Args:
            recommendation_id: 推荐ID（如果已知）
            recommendation: 推荐对象（包含 action 等字段）

        Returns:
            执行结果字典
        """
        result = {
            "success": False,
            "recommendation_id": recommendation_id,
            "execution_result": None,
            "message": ""
        }

        try:
            # 获取推荐信息
            rec = recommendation

            # 如果只提供了 ID，需要先获取推荐
            if not rec and recommendation_id:
                recommendations = self.get_all_recommendations()
                for r in recommendations:
                    if r.recommendation_id == recommendation_id:
                        rec = {
                            'name': r.name,
                            'action': r.action,
                            'type': r.recommendation_type,
                            'metadata': r.metadata
                        }
                        break

            if not rec:
                result["message"] = "未找到指定的推荐"
                return result

            # 根据推荐类型执行不同的动作
            action = rec.get('action', '')
            rec_type = rec.get('type', '')
            rec_name = rec.get('name', '')

            # 首先检查是否是场景/工作流推荐，尝试直接执行 run_plan
            if rec_type in ('scene', 'workflow') and action:
                # 尝试直接执行 run_plan
                # action 可能是 "run_plan assets/plans/xxx.json" 或 "assets/plans/xxx.json" 或 "xxx.json"
                plan_path = action
                # 移除 "run_plan " 前缀
                if plan_path.startswith('run_plan '):
                    plan_path = plan_path[9:]  # 移除 "run_plan "
                # 添加 assets/plans/ 前缀（如果需要）
                if not plan_path.startswith('assets/plans/'):
                    plan_path = f"assets/plans/{plan_path}"

                # 检查计划文件是否存在
                import os
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                full_plan_path = os.path.join(project_root, plan_path)

                if os.path.exists(full_plan_path):
                    # 直接执行 run_plan
                    import subprocess
                    run_plan_script = os.path.join(project_root, 'scripts', 'run_plan.py')
                    exec_result = subprocess.run(
                        [sys.executable, run_plan_script, plan_path],
                        cwd=project_root,
                        capture_output=True,
                        text=True
                    )
                    result["success"] = exec_result.returncode == 0
                    result["execution_result"] = {
                        "method": "run_plan",
                        "plan": plan_path,
                        "stdout": exec_result.stdout,
                        "returncode": exec_result.returncode
                    }
                    result["message"] = f"执行场景计划「{rec_name}」: {'成功' if result['success'] else '失败'}"
                    self._save_execution_history(rec, result)
                    return result

            # 使用决策编排中心执行（如果可用）
            if self.orchestrator and action:
                # 将推荐动作转换为用户输入，交给决策编排中心处理
                user_input = action
                if rec_type == 'scene' or rec_type == 'workflow':
                    # 执行场景或工作流
                    execution = self.orchestrator.orchestrate(user_input)
                    result["success"] = execution.get("success", False)
                    result["execution_result"] = execution
                    result["message"] = f"通过决策编排中心执行推荐「{rec_name}」: {'成功' if result['success'] else '失败'}"
                else:
                    # 其他类型通过 do.py 或直接执行
                    result["execution_result"] = {"action": action, "type": rec_type}
                    result["success"] = True
                    result["message"] = f"推荐「{rec_name}」可直接执行: {action}"
            else:
                # 如果没有决策编排中心，直接返回可执行的动作
                result["success"] = True
                result["execution_result"] = {"action": action, "type": rec_type}
                result["message"] = f"推荐「{rec_name}」: {action}"

            # 记录执行历史
            self._save_execution_history(rec, result)

        except Exception as e:
            result["message"] = f"执行推荐失败: {str(e)}"
            print(f"[UnifiedRecommender] 执行推荐失败: {e}")

        return result

    def execute_auto(self, auto_confirm: bool = False) -> Dict[str, Any]:
        """自动执行最高置信度的推荐

        根据当前上下文获取推荐，并自动执行最高置信度的推荐。
        适用于用户授权后的自动化场景。

        Args:
            auto_confirm: 是否自动确认执行（需要用户预先授权）

        Returns:
            执行结果
        """
        result = {
            "success": False,
            "recommendations": [],
            "executed": None,
            "message": ""
        }

        try:
            # 获取当前推荐
            recommendations = self.get_all_recommendations()
            result["recommendations"] = [
                {
                    'id': r.recommendation_id,
                    'name': r.name,
                    'confidence': r.confidence,
                    'action': r.action
                }
                for r in recommendations[:5]
            ]

            if not recommendations:
                result["message"] = "当前无推荐可执行"
                return result

            # 选择最高置信度的推荐
            best_rec = recommendations[0]

            if auto_confirm:
                # 自动执行
                exec_result = self.execute_recommendation(
                    recommendation_id=best_rec.recommendation_id,
                    recommendation={
                        'name': best_rec.name,
                        'action': best_rec.action,
                        'type': best_rec.recommendation_type,
                        'metadata': best_rec.metadata
                    }
                )
                result["executed"] = exec_result
                result["success"] = exec_result.get("success", False)
                result["message"] = f"已自动执行推荐「{best_rec.name}」"
            else:
                # 返回推荐供用户确认
                result["success"] = True
                result["message"] = f"最高置信度推荐：「{best_rec.name}」(置信度 {int(best_rec.confidence*100)}%)"

        except Exception as e:
            result["message"] = f"自动执行失败: {str(e)}"
            print(f"[UnifiedRecommender] 自动执行失败: {e}")

        return result

    def _save_execution_history(self, recommendation: Dict[str, Any], result: Dict[str, Any]):
        """保存执行历史"""
        try:
            history_file = os.path.join(STATE_DIR, 'recommendation_execution_history.json')
            history_data = {"executions": []}

            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)

            if "executions" not in history_data:
                history_data["executions"] = []

            history_data["executions"].append({
                "recommendation": recommendation,
                "result": result,
                "timestamp": datetime.now().isoformat()
            })

            # 只保留最近 100 条
            history_data["executions"] = history_data["executions"][-100:]

            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"[UnifiedRecommender] 保存执行历史失败: {e}")


def get_unified_recommendations(context: Dict[str, Any] = None, limit: int = 10) -> List[Dict[str, Any]]:
    """获取统一推荐（主入口函数）"""
    engine = UnifiedRecommenderEngine()
    recommendations = engine.get_all_recommendations(context, limit)

    return [
        {
            'id': rec.recommendation_id,
            'type': rec.recommendation_type,
            'name': rec.name,
            'description': rec.description,
            'reason': rec.reason,
            'confidence': rec.confidence,
            'priority': rec.priority,
            'source': rec.source,
            'action': rec.action,
            'metadata': rec.metadata
        }
        for rec in recommendations
    ]


# CLI 接口
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='智能统一推荐引擎')
    parser.add_argument('action', nargs='?', default='recommend',
                       choices=['recommend', 'history', 'feedback', 'execute', 'auto'],
                       help='动作: recommend 获取推荐, history 查看历史, feedback 记录反馈, execute 执行推荐, auto 自动执行')
    parser.add_argument('--limit', '-l', type=int, default=10, help='推荐数量')
    parser.add_argument('--query', '-q', help='用户查询/意图')
    parser.add_argument('--json', '-j', action='store_true', help='输出JSON格式')
    parser.add_argument('--rec-id', help='推荐ID（用于反馈或执行）')
    parser.add_argument('--feedback', '-f', choices=['accepted', 'rejected', 'ignored'],
                       help='反馈类型')
    parser.add_argument('--confirm', '-c', action='store_true', help='自动确认执行（用于 auto 命令）')

    args = parser.parse_args()

    engine = UnifiedRecommenderEngine()

    if args.action == 'recommend':
        context = {'query': args.query or ''}
        recommendations = engine.get_all_recommendations(context, args.limit)

        if args.json:
            print(json.dumps({
                'recommendations': [
                    {
                        'id': rec.recommendation_id,
                        'type': rec.recommendation_type,
                        'name': rec.name,
                        'reason': rec.reason,
                        'confidence': rec.confidence,
                        'priority': rec.priority,
                        'action': rec.action
                    }
                    for rec in recommendations
                ]
            }, ensure_ascii=False, indent=2))
        else:
            print(f"智能统一推荐 (共 {len(recommendations)} 项):\n")
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. [{rec.recommendation_type}] {rec.name}")
                print(f"   原因: {rec.reason}")
                print(f"   置信度: {int(rec.confidence*100)}% | 优先级: {rec.priority}")
                print(f"   执行: {rec.action}")
                print()

    elif args.action == 'history':
        history = engine.get_recommendation_history(args.limit)
        if args.json:
            print(json.dumps({'history': history}, ensure_ascii=False, indent=2))
        else:
            print(f"推荐历史 (共 {len(history)} 条):\n")
            for i, item in enumerate(history, 1):
                print(f"{i}. {item.get('name', 'N/A')} - {item.get('reason', 'N/A')}")

    elif args.action == 'feedback':
        if args.rec_id and args.feedback:
            engine.record_feedback(args.rec_id, args.feedback)
            print(f"已记录反馈: {args.feedback} -> {args.rec_id}")

    elif args.action == 'execute':
        if args.rec_id:
            result = engine.execute_recommendation(recommendation_id=args.rec_id)
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(f"执行推荐: {result.get('message', '')}")
                if result.get('execution_result'):
                    print(f"执行结果: {result['execution_result']}")
        else:
            print("请提供 --rec-id 参数指定要执行的推荐")

    elif args.action == 'auto':
        result = engine.execute_auto(auto_confirm=args.confirm)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"自动执行: {result.get('message', '')}")
            if result.get('recommendations'):
                print("\n当前推荐列表:")
                for i, rec in enumerate(result['recommendations'], 1):
                    print(f"  {i}. {rec['name']} (置信度: {int(rec['confidence']*100)}%)")
            if result.get('executed'):
                print(f"\n已执行结果: {result['executed'].get('message', '')}")