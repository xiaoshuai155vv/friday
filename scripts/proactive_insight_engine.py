#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能主动预测与洞察引擎

让系统能够基于知识图谱、执行历史、用户行为，主动预测用户需求并提供前瞻性洞察。
实现从「被动响应」到「主动预测」的范式转变。

功能：
1. 需求预测 - 基于知识图谱关联、执行历史模式分析、用户行为趋势预测用户可能的需求
2. 主动洞察生成 - 从数据中发现用户可能感兴趣的信息
3. 前瞻性建议 - 推荐用户可能需要但尚未使用的功能

集成到 do.py 支持：「主动预测」「洞察」「前瞻」「主动建议」「预测需求」等关键词触发
"""

import sys
import os
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from knowledge_graph import KnowledgeGraph
except ImportError:
    KnowledgeGraph = None


class ProactiveInsightEngine:
    """智能主动预测与洞察引擎"""

    def __init__(self, state_dir="runtime/state", knowledge_graph_path="runtime/state/knowledge_graph.json"):
        """
        初始化主动预测与洞察引擎

        Args:
            state_dir: 状态目录
            knowledge_graph_path: 知识图谱文件路径
        """
        self.state_dir = state_dir
        self.knowledge_graph_path = knowledge_graph_path
        self.insights_file = os.path.join(state_dir, "proactive_insights.json")
        self.predictions_file = os.path.join(state_dir, "predictions_history.json")

        # 初始化知识图谱
        self.kg = None
        if KnowledgeGraph:
            try:
                self.kg = KnowledgeGraph(knowledge_graph_path)
            except Exception as e:
                print(f"知识图谱初始化失败: {e}")

        # 加载历史数据
        self.insights_history = self._load_insights()
        self.predictions_history = self._load_predictions()

    def _load_insights(self) -> List[Dict]:
        """加载历史洞察"""
        if os.path.exists(self.insights_file):
            try:
                with open(self.insights_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _load_predictions(self) -> List[Dict]:
        """加载历史预测"""
        if os.path.exists(self.predictions_file):
            try:
                with open(self.predictions_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_insights(self):
        """保存洞察历史"""
        try:
            os.makedirs(self.state_dir, exist_ok=True)
            with open(self.insights_file, 'w', encoding='utf-8') as f:
                json.dump(self.insights_history[-100:], f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存洞察历史失败: {e}")

    def _save_predictions(self):
        """保存预测历史"""
        try:
            os.makedirs(self.state_dir, exist_ok=True)
            with open(self.predictions_file, 'w', encoding='utf-8') as f:
                json.dump(self.predictions_history[-100:], f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存预测历史失败: {e}")

    def _load_recent_logs(self) -> List[Dict]:
        """加载最近的日志数据"""
        recent_logs_path = os.path.join(self.state_dir, "recent_logs.json")
        if os.path.exists(recent_logs_path):
            try:
                with open(recent_logs_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 支持字典格式（包含 entries 键）和列表格式
                    if isinstance(data, dict) and "entries" in data:
                        return data["entries"]
                    elif isinstance(data, list):
                        return data
                    return []
            except Exception:
                return []
        return []

    def predict_user_needs(self, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        预测用户可能的需求

        Args:
            context: 可选的上下文信息（如当前时间、用户状态等）

        Returns:
            包含预测结果的字典
        """
        predictions = {
            "timestamp": datetime.now().isoformat(),
            "predictions": [],
            "confidence_scores": {},
            "reasoning": []
        }

        # 1. 基于时间模式的预测
        time_predictions = self._predict_by_time_pattern()
        predictions["predictions"].extend(time_predictions["items"])
        predictions["reasoning"].append(time_predictions["reasoning"])

        # 2. 基于执行历史的预测
        history_predictions = self._predict_by_execution_history()
        predictions["predictions"].extend(history_predictions["items"])
        predictions["reasoning"].append(history_predictions["reasoning"])

        # 3. 基于知识图谱的预测
        kg_predictions = self._predict_by_knowledge_graph()
        predictions["predictions"].extend(kg_predictions["items"])
        predictions["reasoning"].append(kg_predictions["reasoning"])

        # 计算置信度
        for item in predictions["predictions"]:
            predictions["confidence_scores"][item] = self._calculate_confidence(item)

        # 按置信度排序，取前5个
        sorted_predictions = sorted(
            predictions["confidence_scores"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        predictions["top_predictions"] = [
            {"need": need, "confidence": round(confidence, 2)}
            for need, confidence in sorted_predictions
        ]

        # 保存预测结果
        self.predictions_history.append({
            "timestamp": predictions["timestamp"],
            "predictions": predictions["top_predictions"],
            "context": context
        })
        self._save_predictions()

        return predictions

    def _predict_by_time_pattern(self) -> Dict:
        """基于时间模式预测"""
        items = []
        now = datetime.now()
        hour = now.hour
        weekday = now.weekday()

        # 早上9-10点：检查日程/会议
        if 9 <= hour < 11:
            items.append("检查今日日程/会议安排")

        # 上午10-12点：工作进度检查
        if 10 <= hour < 12:
            items.append("回顾上午工作进度")

        # 下午2-3点：例会时间提醒
        if 14 <= hour < 15 and weekday < 5:
            items.append("提醒：检查下午例会材料")

        # 下午5-6点：日报/总结
        if 17 <= hour < 18 and weekday < 5:
            items.append("提醒：撰写日报/工作总结")

        # 周末：检查休息/娱乐相关
        if weekday >= 5:
            items.append("推荐：周末放松/娱乐活动")

        # 周一：周计划
        if weekday == 0:
            items.append("建议：制定本周工作计划")

        return {
            "items": items,
            "reasoning": f"基于当前时间({now.strftime('%H:%M')})和时间模式分析"
        }

    def _predict_by_execution_history(self) -> Dict:
        """基于执行历史预测"""
        items = []
        recent_logs = self._load_recent_logs()

        if not recent_logs:
            return {"items": [], "reasoning": "无执行历史数据"}

        # 统计高频操作
        operations = []
        for log in recent_logs[-50:]:
            if isinstance(log, dict):
                # 尝试从日志中提取操作
                action = log.get("action", "")
                if action:
                    operations.append(action)

        if operations:
            # 分析重复模式
            op_counter = Counter(operations)
            top_ops = op_counter.most_common(3)

            # 如果某个操作频繁出现，预测下一步
            if top_ops:
                most_common = top_ops[0][0]
                if "打开" in most_common:
                    items.append(f"可能需要再次打开{most_common.replace('打开 ', '')}")
                elif "查询" in most_common:
                    items.append("可能需要查询更多信息")
                elif "文件" in most_common:
                    items.append("可能需要整理或查找文件")

        # 基于最近执行但未完成的任务
        incomplete_indicators = ["进行中", "pending", "未完成"]
        for log in recent_logs[-10:]:
            if isinstance(log, dict):
                status = log.get("status", "")
                if any(indicator in str(status) for indicator in incomplete_indicators):
                    action = log.get("action", "")
                    if action:
                        items.append(f"继续：{action}")

        return {
            "items": items,
            "reasoning": f"基于最近{len(recent_logs)}条执行历史分析"
        }

    def _predict_by_knowledge_graph(self) -> Dict:
        """基于知识图谱预测"""
        items = []

        if not self.kg or not self.kg.graph.get("nodes"):
            return {"items": [], "reasoning": "知识图谱为空，无法预测"}

        # 获取用户相关的节点
        user_nodes = [
            node_id for node_id, node in self.kg.graph.get("nodes", {}).items()
            if node.get("type") == "user" or "user" in node_id.lower()
        ]

        # 获取最近交互的实体
        recent_entities = set()
        for edge in self.kg.graph.get("edges", [])[-20:]:
            recent_entities.add(edge.get("from"))
            recent_entities.add(edge.get("to"))

        # 基于关联发现潜在需求
        for entity in recent_entities:
            # 查找与该实体相关的其他实体
            try:
                related = self.kg.get_related_nodes(entity)
                if len(related) > 3:
                    items.append(f"探索：{entity} 相关内容")
            except Exception:
                pass

        # 分析知识图谱中常见的实体类型
        node_types = Counter()
        for node_id, node in self.kg.graph.get("nodes", {}).items():
            node_type = node.get("type", "unknown")
            node_types[node_type] += 1

        # 推荐最常用的功能类型
        if node_types:
            most_common_type = node_types.most_common(1)[0][0]
            items.append(f"探索：{most_common_type}相关知识")

        return {
            "items": items[:3],
            "reasoning": f"基于知识图谱分析，共{len(self.kg.graph.get('nodes', {}))}个实体"
        }

    def _calculate_confidence(self, item: str) -> float:
        """计算预测置信度"""
        base_confidence = 0.5

        # 时间相关预测通常置信度较高
        if any(kw in item for kw in ["提醒", "建议", "检查"]):
            base_confidence += 0.2

        # 基于历史重复的预测置信度更高
        recent_logs = self._load_recent_logs()
        for log in recent_logs[-20:]:
            if isinstance(log, dict):
                action = log.get("action", "")
                if action and item in action:
                    base_confidence += 0.15
                    break

        return min(base_confidence, 0.95)

    def generate_insights(self) -> Dict[str, Any]:
        """
        生成主动洞察

        Returns:
            包含洞察结果的字典
        """
        insights = {
            "timestamp": datetime.now().isoformat(),
            "insights": [],
            "categories": {
                "behavior_patterns": [],
                "opportunities": [],
                "recommendations": []
            }
        }

        # 1. 分析行为模式
        behavior_insights = self._analyze_behavior_patterns()
        insights["categories"]["behavior_patterns"] = behavior_insights["items"]
        insights["insights"].extend(behavior_insights["items"])

        # 2. 发现机会
        opportunity_insights = self._discover_opportunities()
        insights["categories"]["opportunities"] = opportunity_insights["items"]
        insights["insights"].extend(opportunity_insights["items"])

        # 3. 生成建议
        recommendation_insights = self._generate_recommendations()
        insights["categories"]["recommendations"] = recommendation_insights["items"]
        insights["insights"].extend(recommendation_insights["items"])

        # 保存洞察
        self.insights_history.append({
            "timestamp": insights["timestamp"],
            "insights_count": len(insights["insights"]),
            "categories": list(insights["categories"].keys())
        })
        self._save_insights()

        return insights

    def _analyze_behavior_patterns(self) -> Dict:
        """分析行为模式"""
        items = []
        recent_logs = self._load_recent_logs()

        if not recent_logs:
            return {"items": ["暂无足够的行为数据"], "reasoning": "无执行历史"}

        # 分析操作时间分布
        hours = []
        for log in recent_logs[-30:]:
            if isinstance(log, dict) and "timestamp" in log:
                try:
                    ts = datetime.fromisoformat(log["timestamp"].replace("Z", "+00:00"))
                    hours.append(ts.hour)
                except Exception:
                    pass

        if hours:
            avg_hour = sum(hours) / len(hours)
            if 9 <= avg_hour < 12:
                items.append("您倾向于在上午进行主要工作")
            elif 14 <= avg_hour < 18:
                items.append("您倾向于在下午进行主要工作")
            else:
                items.append("您的工作时间分布较为分散")

        # 分析高频操作
        actions = [log.get("action", "") for log in recent_logs[-30:] if isinstance(log, dict)]
        actions = [a for a in actions if a]
        if actions:
            action_counter = Counter(actions)
            top_actions = action_counter.most_common(3)
            if top_actions:
                most_common_action = top_actions[0][0]
                items.append(f"您最频繁的操作是：{most_common_action}")

        return {
            "items": items,
            "reasoning": f"基于最近{len(recent_logs)}条行为记录分析"
        }

    def _discover_opportunities(self) -> Dict:
        """发现机会"""
        items = []

        # 检查是否有未充分利用的功能
        recent_logs = self._load_recent_logs()
        log_count = len(recent_logs)

        if log_count < 10:
            items.append("系统正在学习您的使用习惯，请多使用以获得更精准的洞察")
        elif log_count < 50:
            items.append("已初步了解您的使用习惯，可以提供基础个性化建议")
        else:
            # 已有足够数据，可以提供更深入的洞察
            items.append("已积累足够的交互数据，可以提供深度个性化洞察")

        # 检查是否有可以自动化的重复操作
        if log_count >= 20:
            actions = [log.get("action", "") for log in recent_logs[-50:] if isinstance(log, dict)]
            action_counter = Counter(actions)
            for action, count in action_counter.most_common(5):
                if count >= 3 and "打开" in action:
                    items.append(f"检测到重复操作「{action}」，可考虑创建快捷方式")
                    break

        return {
            "items": items,
            "reasoning": f"基于{log_count}条交互数据分析"
        }

    def _generate_recommendations(self) -> Dict:
        """生成建议"""
        items = []

        # 基于知识图谱的建议
        if self.kg and self.kg.graph.get("nodes"):
            node_count = len(self.kg.graph["nodes"])
            if node_count < 10:
                items.append("建议：增加知识图谱内容以获得更好的推理支持")
            elif node_count > 50:
                items.append("您的知识库已相当丰富，可以尝试更复杂的多跳查询")

        # 基于执行历史的建议
        recent_logs = self._load_recent_logs()
        log_count = len(recent_logs)

        if log_count > 0:
            # 检查是否有跨引擎协作的机会
            engines = set()
            for log in recent_logs[-20:]:
                if isinstance(log, dict):
                    # 尝试识别引擎
                    action = log.get("action", "")
                    if action:
                        for engine_name in ["knowledge", "workflow", "execution", "recommendation", "prediction"]:
                            if engine_name in action.lower():
                                engines.add(engine_name)

            if len(engines) >= 3:
                items.append("检测到多引擎使用模式，尝试组合使用可能更高效")

        return {
            "items": items,
            "reasoning": "基于系统状态和使用模式生成"
        }

    def get_proactive_suggestions(self) -> Dict[str, Any]:
        """
        获取前瞻性建议

        Returns:
            包含前瞻性建议的字典
        """
        suggestions = {
            "timestamp": datetime.now().isoformat(),
            "suggestions": []
        }

        # 综合预测和洞察，生成前瞻性建议
        predictions = self.predict_user_needs()
        insights = self.generate_insights()

        # 合并建议
        all_suggestions = []

        # 从预测中添加
        for pred in predictions.get("top_predictions", []):
            all_suggestions.append({
                "type": "prediction",
                "content": pred["need"],
                "confidence": pred["confidence"]
            })

        # 从洞察中添加
        for insight in insights.get("insights", [])[:5]:
            all_suggestions.append({
                "type": "insight",
                "content": insight
            })

        # 按置信度排序
        all_suggestions.sort(key=lambda x: x.get("confidence", 0.5), reverse=True)

        suggestions["suggestions"] = all_suggestions[:5]

        return suggestions

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "engine": "ProactiveInsightEngine",
            "version": "1.0",
            "initialized": True,
            "knowledge_graph_loaded": self.kg is not None,
            "insights_count": len(self.insights_history),
            "predictions_count": len(self.predictions_history),
            "timestamp": datetime.now().isoformat()
        }


def main():
    """CLI 入口"""
    import argparse

    parser = argparse.ArgumentParser(description="智能主动预测与洞察引擎")
    parser.add_argument("command", choices=["predict", "insights", "suggestions", "status"],
                        help="要执行的命令")
    parser.add_argument("--context", type=str, help="上下文信息（JSON格式）")

    args = parser.parse_args()

    engine = ProactiveInsightEngine()

    if args.command == "predict":
        context = json.loads(args.context) if args.context else None
        result = engine.predict_user_needs(context)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "insights":
        result = engine.generate_insights()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "suggestions":
        result = engine.get_proactive_suggestions()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "status":
        result = engine.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()