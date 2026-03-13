#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能推荐反馈学习引擎
基于用户对推荐的反馈（接受/拒绝/忽略）自动学习和优化推荐策略

功能：
1. 反馈收集 - 记录用户对推荐的接受、拒绝、忽略行为
2. 模式学习 - 分析反馈模式，学习用户偏好
3. 智能调整 - 根据学习结果自动调整推荐权重
4. 推荐优化 - 生成更符合用户需求的推荐

工作原理：
- 当用户接受推荐时，增加该类型推荐的权重
- 当用户拒绝推荐时，降低该类型推荐的权重
- 当用户忽略推荐时，中等程度降低权重
- 长期学习用户的时间模式、场景偏好等
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict

# 确保 scripts 目录在路径中
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RUNTIME_DIR = os.path.join(SCRIPT_DIR, '..')
STATE_DIR = os.path.join(RUNTIME_DIR, 'state')


class FeedbackLearningEngine:
    """智能推荐反馈学习引擎"""

    def __init__(self):
        self.feedback_file = os.path.join(STATE_DIR, 'recommendation_feedback.json')
        self.learned_weights_file = os.path.join(STATE_DIR, 'learned_recommendation_weights.json')
        self.user_preferences_file = os.path.join(STATE_DIR, 'user_recommendation_preferences.json')

        # 默认权重（未学习前的基准）
        self.default_weights = {
            "scene": 1.0,
            "workflow": 1.0,
            "action": 1.0,
            "engine": 1.0,
            "time_based": 1.0,  # 基于时间的推荐
            "habit_based": 1.0  # 基于习惯的推荐
        }

        # 加载已学习的权重
        self.learned_weights = self._load_learned_weights()

        # 加载用户偏好
        self.user_preferences = self._load_user_preferences()

    def _load_learned_weights(self) -> Dict[str, float]:
        """加载已学习的权重"""
        if os.path.exists(self.learned_weights_file):
            try:
                with open(self.learned_weights_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载学习权重失败: {e}")
        return self.default_weights.copy()

    def _save_learned_weights(self):
        """保存学习到的权重"""
        try:
            with open(self.learned_weights_file, 'w', encoding='utf-8') as f:
                json.dump(self.learned_weights, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存学习权重失败: {e}")

    def _load_user_preferences(self) -> Dict[str, Any]:
        """加载用户推荐偏好"""
        if os.path.exists(self.user_preferences_file):
            try:
                with open(self.user_preferences_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载用户偏好失败: {e}")
        return {
            "preferred_scenes": [],
            "preferred_workflows": [],
            "preferred_time_periods": [],
            "rejected_scenes": [],
            "rejected_workflows": [],
            "feedback_history": [],
            "last_updated": None
        }

    def _save_user_preferences(self):
        """保存用户偏好"""
        try:
            self.user_preferences["last_updated"] = datetime.now().isoformat()
            with open(self.user_preferences_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_preferences, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存用户偏好失败: {e}")

    def record_feedback(self, recommendation_id: str, recommendation: Dict[str, Any],
                        feedback_type: str) -> Dict[str, Any]:
        """记录用户反馈并学习

        Args:
            recommendation_id: 推荐ID
            recommendation: 推荐内容
            feedback_type: 反馈类型 (accepted/rejected/ignored)

        Returns:
            学习结果
        """
        result = {
            "success": False,
            "learned": False,
            "message": ""
        }

        try:
            rec_type = recommendation.get('type', recommendation.get('recommendation_type', 'unknown'))
            rec_name = recommendation.get('name', recommendation.get('scene', recommendation.get('workflow_name', 'unknown')))
            rec_action = recommendation.get('action', '')

            # 1. 记录反馈到反馈历史
            self._add_feedback_to_history(recommendation_id, recommendation, feedback_type)

            # 2. 更新权重
            self._update_weights(rec_type, feedback_type)

            # 3. 更新用户偏好
            self._update_user_preferences(rec_type, rec_name, rec_action, feedback_type)

            # 4. 保存所有更改
            self._save_learned_weights()
            self._save_user_preferences()

            result["success"] = True
            result["learned"] = True
            result["message"] = f"已记录反馈 '{feedback_type}' 并学习"

            print(f"[FeedbackLearning] 学习反馈: {rec_name} ({rec_type}) -> {feedback_type}")

        except Exception as e:
            result["message"] = f"记录反馈失败: {str(e)}"
            print(f"[FeedbackLearning] 记录反馈失败: {e}")

        return result

    def _add_feedback_to_history(self, recommendation_id: str, recommendation: Dict[str, Any], feedback_type: str):
        """添加反馈到历史记录"""
        feedback_data = {"feedbacks": []}

        if os.path.exists(self.feedback_file):
            try:
                with open(self.feedback_file, 'r', encoding='utf-8') as f:
                    feedback_data = json.load(f)
            except Exception as e:
                print(f"读取反馈历史失败: {e}")

        if "feedbacks" not in feedback_data:
            feedback_data["feedbacks"] = []

        # 添加新反馈
        feedback_data["feedbacks"].append({
            "recommendation_id": recommendation_id,
            "recommendation": recommendation,
            "feedback": feedback_type,
            "timestamp": datetime.now().isoformat(),
            "rec_type": recommendation.get('type', recommendation.get('recommendation_type', 'unknown')),
            "rec_name": recommendation.get('name', 'unknown')
        })

        # 只保留最近 200 条
        feedback_data["feedbacks"] = feedback_data["feedbacks"][-200:]

        # 保存
        try:
            with open(self.feedback_file, 'w', encoding='utf-8') as f:
                json.dump(feedback_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存反馈历史失败: {e}")

    def _update_weights(self, rec_type: str, feedback_type: str):
        """根据反馈更新权重

        权重调整策略：
        - accepted: 增加 10%
        - rejected: 减少 15%
        - ignored: 减少 5%
        """
        if rec_type not in self.learned_weights:
            self.learned_weights[rec_type] = 1.0

        if feedback_type == "accepted":
            self.learned_weights[rec_type] *= 1.10  # 增加 10%
        elif feedback_type == "rejected":
            self.learned_weights[rec_type] *= 0.85  # 减少 15%
        elif feedback_type == "ignored":
            self.learned_weights[rec_type] *= 0.95  # 减少 5%

        # 限制权重范围 [0.1, 3.0]
        self.learned_weights[rec_type] = max(0.1, min(3.0, self.learned_weights[rec_type]))

    def _update_user_preferences(self, rec_type: str, rec_name: str, rec_action: str, feedback_type: str):
        """更新用户偏好"""
        # 移除旧的反馈记录
        if rec_type == "scene":
            if rec_name in self.user_preferences["rejected_scenes"]:
                self.user_preferences["rejected_scenes"].remove(rec_name)
        elif rec_type == "workflow":
            if rec_name in self.user_preferences["rejected_workflows"]:
                self.user_preferences["rejected_workflows"].remove(rec_name)

        # 添加新的偏好
        if feedback_type == "accepted":
            if rec_type == "scene" and rec_name not in self.user_preferences["preferred_scenes"]:
                self.user_preferences["preferred_scenes"].append(rec_name)
            elif rec_type == "workflow" and rec_name not in self.user_preferences["preferred_workflows"]:
                self.user_preferences["preferred_workflows"].append(rec_name)

            # 记录时间偏好
            hour = datetime.now().hour
            time_period = self._get_time_period(hour)
            if time_period not in self.user_preferences["preferred_time_periods"]:
                self.user_preferences["preferred_time_periods"].append(time_period)

        elif feedback_type == "rejected":
            if rec_type == "scene" and rec_name not in self.user_preferences["rejected_scenes"]:
                self.user_preferences["rejected_scenes"].append(rec_name)
                # 从首选中移除
                if rec_name in self.user_preferences["preferred_scenes"]:
                    self.user_preferences["preferred_scenes"].remove(rec_name)
            elif rec_type == "workflow" and rec_name not in self.user_preferences["rejected_workflows"]:
                self.user_preferences["rejected_workflows"].append(rec_name)
                if rec_name in self.user_preferences["preferred_workflows"]:
                    self.user_preferences["preferred_workflows"].remove(rec_name)

    def _get_time_period(self, hour: int) -> str:
        """获取时间段名称"""
        if 6 <= hour < 9:
            return "morning"
        elif 9 <= hour < 12:
            return "forenoon"
        elif 12 <= hour < 14:
            return "noon"
        elif 14 <= hour < 18:
            return "afternoon"
        elif 18 <= hour < 22:
            return "evening"
        else:
            return "night"

    def get_adjusted_confidence(self, base_confidence: float, rec_type: str) -> float:
        """获取调整后的置信度

        根据学习到的权重调整推荐的置信度

        Args:
            base_confidence: 基础置信度
            rec_type: 推荐类型

        Returns:
            调整后的置信度
        """
        weight = self.learned_weights.get(rec_type, 1.0)
        # 调整后的置信度 = 基础置信度 * 权重
        adjusted = base_confidence * weight
        # 限制在 [0, 1] 范围内
        return max(0.0, min(1.0, adjusted))

    def get_filtered_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """获取过滤和调整后的推荐列表

        根据用户偏好过滤不喜欢的推荐，并调整置信度

        Args:
            recommendations: 原始推荐列表

        Returns:
            过滤和调整后的推荐列表
        """
        filtered = []

        for rec in recommendations:
            rec_type = rec.get('type', rec.get('recommendation_type', 'unknown'))
            rec_name = rec.get('name', rec.get('scene', rec.get('workflow_name', 'unknown')))

            # 过滤掉用户明确拒绝的推荐
            if rec_type == "scene" and rec_name in self.user_preferences.get("rejected_scenes", []):
                continue
            if rec_type == "workflow" and rec_name in self.user_preferences.get("rejected_workflows", []):
                continue

            # 调整置信度
            base_conf = rec.get('confidence', 0.5)
            adjusted_conf = self.get_adjusted_confidence(base_conf, rec_type)

            rec_copy = rec.copy()
            rec_copy['confidence'] = adjusted_conf
            rec_copy['original_confidence'] = base_conf
            rec_copy['weight_adjusted'] = adjusted_conf != base_conf

            filtered.append(rec_copy)

        # 按调整后的置信度排序
        filtered.sort(key=lambda x: x.get('confidence', 0), reverse=True)

        return filtered

    def get_learning_stats(self) -> Dict[str, Any]:
        """获取学习统计信息"""
        # 读取反馈历史
        feedback_data = {"feedbacks": []}
        if os.path.exists(self.feedback_file):
            try:
                with open(self.feedback_file, 'r', encoding='utf-8') as f:
                    feedback_data = json.load(f)
            except:
                pass

        feedbacks = feedback_data.get("feedbacks", [])

        # 统计各类反馈数量
        accepted_count = sum(1 for f in feedbacks if f.get('feedback') == 'accepted')
        rejected_count = sum(1 for f in feedbacks if f.get('feedback') == 'rejected')
        ignored_count = sum(1 for f in feedbacks if f.get('feedback') == 'ignored')

        # 统计各类型推荐
        type_counts = defaultdict(int)
        for f in feedbacks:
            rec_type = f.get('rec_type', 'unknown')
            type_counts[rec_type] += 1

        return {
            "total_feedbacks": len(feedbacks),
            "accepted": accepted_count,
            "rejected": rejected_count,
            "ignored": ignored_count,
            "type_counts": dict(type_counts),
            "learned_weights": self.learned_weights,
            "preferred_scenes": self.user_preferences.get("preferred_scenes", []),
            "preferred_workflows": self.user_preferences.get("preferred_workflows", []),
            "rejected_scenes": self.user_preferences.get("rejected_scenes", []),
            "rejected_workflows": self.user_preferences.get("rejected_workflows", []),
            "preferred_time_periods": self.user_preferences.get("preferred_time_periods", []),
            "last_updated": self.user_preferences.get("last_updated")
        }

    def analyze_feedback_patterns(self) -> Dict[str, Any]:
        """分析反馈模式，生成洞察"""
        stats = self.get_learning_stats()

        insights = {
            "summary": "",
            "recommendations": []
        }

        # 生成摘要
        total = stats["total_feedbacks"]
        if total == 0:
            insights["summary"] = "暂无反馈数据，请多使用推荐功能以帮助系统学习您的偏好"
            return insights

        accepted_rate = stats["accepted"] / total if total > 0 else 0
        insights["summary"] = f"共收集 {total} 条反馈，接受率 {int(accepted_rate*100)}%"

        # 生成建议
        if stats["rejected"] > stats["accepted"] * 0.5:
            insights["recommendations"].append({
                "type": "weight_adjustment",
                "message": "您拒绝了较多推荐，建议调整推荐算法灵敏度"
            })

        if stats["preferred_time_periods"]:
            top_time = max(set(stats["preferred_time_periods"]),
                         key=stats["preferred_time_periods"].count) if stats["preferred_time_periods"] else None
            if top_time:
                insights["recommendations"].append({
                    "type": "time_preference",
                    "message": f"您似乎更喜欢在 {top_time} 时段使用推荐功能"
                })

        return insights

    def reset_learning(self) -> Dict[str, Any]:
        """重置所有学习数据"""
        self.learned_weights = self.default_weights.copy()
        self.user_preferences = {
            "preferred_scenes": [],
            "preferred_workflows": [],
            "preferred_time_periods": [],
            "rejected_scenes": [],
            "rejected_workflows": [],
            "feedback_history": [],
            "last_updated": None
        }

        self._save_learned_weights()
        self._save_user_preferences()

        return {
            "success": True,
            "message": "已重置所有学习数据"
        }


# 全局实例
_learning_engine = None

def get_learning_engine() -> FeedbackLearningEngine:
    """获取学习引擎单例"""
    global _learning_engine
    if _learning_engine is None:
        _learning_engine = FeedbackLearningEngine()
    return _learning_engine


def record_recommendation_feedback(recommendation_id: str, recommendation: Dict[str, Any],
                                     feedback_type: str) -> Dict[str, Any]:
    """记录推荐反馈的便捷函数"""
    engine = get_learning_engine()
    return engine.record_feedback(recommendation_id, recommendation, feedback_type)


def get_filtered_recommendations(recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """获取过滤后的推荐的便捷函数"""
    engine = get_learning_engine()
    return engine.get_filtered_recommendations(recommendations)


# CLI 接口
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='智能推荐反馈学习引擎')
    parser.add_argument('action', nargs='?', default='stats',
                       choices=['stats', 'insights', 'reset', 'filter'],
                       help='动作: stats 查看统计, insights 查看洞察, reset 重置学习, filter 过滤推荐')
    parser.add_argument('--rec-id', help='推荐ID（用于记录反馈）')
    parser.add_argument('--rec-name', help='推荐名称')
    parser.add_argument('--rec-type', help='推荐类型')
    parser.add_argument('--action-type', help='推荐动作/命令')
    parser.add_argument('--feedback', choices=['accepted', 'rejected', 'ignored'],
                       help='反馈类型')
    parser.add_argument('--json', '-j', action='store_true', help='输出JSON格式')
    parser.add_argument('--limit', '-l', type=int, default=10, help='推荐数量限制')

    args = parser.parse_args()

    engine = get_learning_engine()

    if args.action == 'stats':
        stats = engine.get_learning_stats()
        if args.json:
            print(json.dumps(stats, ensure_ascii=False, indent=2))
        else:
            print("=== 推荐反馈学习统计 ===")
            print(f"总反馈数: {stats['total_feedbacks']}")
            print(f"  接受: {stats['accepted']}")
            print(f"  拒绝: {stats['rejected']}")
            print(f"  忽略: {stats['ignored']}")
            print("\n=== 学习权重 ===")
            for k, v in stats['learned_weights'].items():
                print(f"  {k}: {v:.2f}")
            print("\n=== 用户偏好 ===")
            print(f"首选场景: {stats['preferred_scenes']}")
            print(f"首选工作流: {stats['preferred_workflows']}")
            print(f"拒绝场景: {stats['rejected_scenes']}")
            print(f"拒绝工作流: {stats['rejected_workflows']}")
            print(f"偏好时段: {stats['preferred_time_periods']}")

    elif args.action == 'insights':
        insights = engine.analyze_feedback_patterns()
        if args.json:
            print(json.dumps(insights, ensure_ascii=False, indent=2))
        else:
            print("=== 反馈模式洞察 ===")
            print(insights.get('summary', ''))
            if insights.get('recommendations'):
                print("\n建议:")
                for r in insights['recommendations']:
                    print(f"  - {r.get('message', '')}")

    elif args.action == 'reset':
        result = engine.reset_learning()
        print(result['message'])

    elif args.action == 'filter':
        # 模拟推荐数据用于测试
        test_recommendations = [
            {"type": "scene", "name": "play_music.json", "confidence": 0.8, "action": "run_plan assets/plans/play_music.json"},
            {"type": "scene", "name": "ihaier_performance_declaration.json", "confidence": 0.7, "action": "run_plan assets/plans/ihaier_performance_declaration.json"},
            {"type": "workflow", "name": "文件整理", "confidence": 0.6, "action": "run_plan assets/plans/file_organization.json"},
            {"type": "action", "name": "开启专注模式", "confidence": 0.5, "action": "do 专注"}
        ]
        filtered = engine.get_filtered_recommendations(test_recommendations)
        if args.json:
            print(json.dumps(filtered, ensure_ascii=False, indent=2))
        else:
            print("=== 过滤后的推荐 ===")
            for i, rec in enumerate(filtered, 1):
                print(f"{i}. {rec['name']} (原始: {rec.get('original_confidence', rec['confidence']):.2f} -> 调整后: {rec['confidence']:.2f})")