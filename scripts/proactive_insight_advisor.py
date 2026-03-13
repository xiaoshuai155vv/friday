#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能主动洞察与建议引擎

让系统能够基于已学习的跨引擎知识、模式、进化历史，主动提供前瞻性洞察和优化建议，
实现从「被动响应」到「主动价值提供」的范式升级。

功能：
1. 跨引擎知识洞察分析（基于 cross_engine_learning 数据）
2. 进化趋势预测与建议
3. 系统健康与优化建议
4. 用户行为洞察与主动服务建议
"""

import os
import json
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from pathlib import Path
import glob

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
LOGS_DIR = RUNTIME_DIR / "logs"
STATE_DIR = RUNTIME_DIR / "state"


class ProactiveInsightAdvisor:
    """智能主动洞察与建议引擎"""

    def __init__(self):
        self.learning_data_path = STATE_DIR / "cross_engine_learning_data.json"
        self.patterns_path = STATE_DIR / "cross_engine_patterns.json"
        self.learning_data = self._load_learning_data()
        self.patterns = self._load_patterns()
        self.insights_path = STATE_DIR / "proactive_insights.json"
        self.insights = self._load_insights()

    def _load_learning_data(self):
        """加载学习数据"""
        if self.learning_data_path.exists():
            try:
                with open(self.learning_data_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "interactions": [],
            "discovered_patterns": [],
            "innovation_suggestions": [],
            "learning_history": [],
            "last_updated": None
        }

    def _load_patterns(self):
        """加载模式数据"""
        if self.patterns_path.exists():
            try:
                with open(self.patterns_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "collaboration_patterns": [],
            "success_patterns": [],
            "failure_patterns": [],
            "innovation_patterns": []
        }

    def _load_insights(self):
        """加载洞察数据"""
        if self.insights_path.exists():
            try:
                with open(self.insights_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 兼容旧格式（列表）和新格式（字典）
                    if isinstance(data, list):
                        return {
                            "insights": [],
                            "recommendations": [],
                            "predictions": [],
                            "last_generated": None
                        }
                    return data
            except:
                pass
        return {
            "insights": [],
            "recommendations": [],
            "predictions": [],
            "last_generated": None
        }

    def _save_insights(self):
        """保存洞察数据"""
        self.insights["last_generated"] = datetime.now().isoformat()
        with open(self.insights_path, 'w', encoding='utf-8') as f:
            json.dump(self.insights, f, ensure_ascii=False, indent=2)

    def get_status(self):
        """获取洞察引擎状态"""
        return {
            "status": "active",
            "learning_data_count": len(self.learning_data.get("interactions", [])),
            "patterns_count": len(self.patterns.get("collaboration_patterns", [])),
            "insights_count": len(self.insights.get("insights", [])),
            "recommendations_count": len(self.insights.get("recommendations", [])),
            "last_generated": self.insights.get("last_generated")
        }

    def generate_cross_engine_insights(self):
        """生成跨引擎知识洞察"""
        insights = []

        # 分析交互数据
        interactions = self.learning_data.get("interactions", [])
        if interactions:
            # 统计最活跃的引擎
            engine_counter = Counter()
            for interaction in interactions:
                if "engines" in interaction:
                    for engine in interaction["engines"]:
                        engine_counter[engine] += 1

            top_engines = engine_counter.most_common(10)
            insights.append({
                "type": "engine_activity",
                "title": "最活跃引擎 Top 10",
                "content": f"基于 {len(interactions)} 条交互数据，当前最活跃的引擎为：{', '.join([e[0] for e in top_engines[:5]])}",
                "data": {"top_engines": dict(top_engines), "total_interactions": len(interactions)},
                "timestamp": datetime.now().isoformat()
            })

            # 分析协作模式效果
            patterns = self.patterns.get("collaboration_patterns", [])
            if patterns:
                high_success = [p for p in patterns if p.get("success_rate", 0) > 0.8]
                if high_success:
                    insights.append({
                        "type": "pattern_effectiveness",
                        "title": "高效协作模式",
                        "content": f"发现 {len(high_success)} 个高成功率(>80%)的协作模式，这些模式可以优先使用",
                        "data": {"high_success_patterns": len(high_success), "total_patterns": len(patterns)},
                        "timestamp": datetime.now().isoformat()
                    })

        # 分析创新建议
        innovations = self.learning_data.get("innovation_suggestions", [])
        if innovations:
            pending = [i for i in innovations if i.get("status") == "pending"]
            if pending:
                insights.append({
                    "type": "innovation_opportunity",
                    "title": "待验证的创新建议",
                    "content": f"有 {len(pending)} 个创新组合建议等待验证，可能带来突破性提升",
                    "data": {"pending_innovations": len(pending)},
                    "timestamp": datetime.now().isoformat()
                })

        return insights

    def generate_evolution_trends(self):
        """生成进化趋势洞察"""
        predictions = []

        # 分析进化历史
        completed_files = sorted(STATE_DIR.glob("evolution_completed_*.json"))
        if completed_files:
            # 获取最近 20 轮进化
            recent_files = completed_files[-20:] if len(completed_files) > 20 else completed_files

            # 统计进化类型
            evolution_types = defaultdict(int)
            for f in recent_files:
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        goal = data.get("current_goal", "")
                        # 简单分类
                        if "智能" in goal:
                            if "引擎" in goal:
                                evolution_types["引擎开发"] += 1
                            elif "优化" in goal:
                                evolution_types["优化增强"] += 1
                            elif "学习" in goal or "分析" in goal:
                                evolution_types["智能分析"] += 1
                            else:
                                evolution_types["其他"] += 1
                except:
                    pass

            if evolution_types:
                total = sum(evolution_types.values())
                predictions.append({
                    "type": "evolution_focus",
                    "title": "近期进化重点",
                    "content": f"近 {len(recent_files)} 轮进化中，{max(evolution_types, key=evolution_types.get)} 占比最高({evolution_types[max(evolution_types, key=evolution_types.get)]}/{total})",
                    "data": dict(evolution_types),
                    "timestamp": datetime.now().isoformat()
                })

            # 预测下一轮方向
            recent_goals = []
            for f in recent_files[-5:]:
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        recent_goals.append(data.get("current_goal", ""))
                except:
                    pass

            if recent_goals:
                # 基于最近趋势预测
                if any("学习" in g for g in recent_goals):
                    predictions.append({
                        "type": "trend_prediction",
                        "title": "进化趋势预测",
                        "content": "基于近期进化趋势，下一轮可能聚焦于：知识整合、跨域创新或自动化执行增强",
                        "data": {"based_on": "recent_5_rounds"},
                        "timestamp": datetime.now().isoformat()
                    })

        return predictions

    def generate_health_insights(self):
        """生成系统健康洞察"""
        recommendations = []

        # 检查关键文件状态
        checks = {
            "learning_data": self.learning_data_path.exists(),
            "patterns": self.patterns_path.exists(),
            "insights": self.insights_path.exists()
        }

        missing = [k for k, v in checks.items() if not v]
        if missing:
            recommendations.append({
                "type": "data_health",
                "title": "数据文件缺失",
                "content": f"以下数据文件缺失: {', '.join(missing)}，建议运行跨引擎学习引擎进行初始化",
                "severity": "warning",
                "timestamp": datetime.now().isoformat()
            })

        # 检查交互数据量
        interaction_count = len(self.learning_data.get("interactions", []))
        if interaction_count < 100:
            recommendations.append({
                "type": "data_volume",
                "title": "交互数据量偏低",
                "content": f"当前仅收集 {interaction_count} 条交互数据，建议增加引擎使用以积累更多学习样本",
                "severity": "info",
                "timestamp": datetime.now().isoformat()
            })
        else:
            recommendations.append({
                "type": "data_volume",
                "title": "交互数据充足",
                "content": f"已收集 {interaction_count} 条交互数据，学习基础良好",
                "severity": "success",
                "timestamp": datetime.now().isoformat()
            })

        # 检查模式发现
        pattern_count = len(self.patterns.get("collaboration_patterns", []))
        if pattern_count < 5:
            recommendations.append({
                "type": "pattern_discovery",
                "title": "协作模式待发现",
                "content": f"当前仅发现 {pattern_count} 个协作模式，运行 'do 跨引擎学习 discover' 可主动发现更多模式",
                "severity": "info",
                "timestamp": datetime.now().isoformat()
            })

        return recommendations

    def generate_behavior_insights(self):
        """生成用户行为洞察"""
        insights = []

        # 分析最近的交互日志
        log_files = sorted(LOGS_DIR.glob("behavior_*.log"))
        if log_files:
            recent_logs = []
            for f in log_files[-3:]:  # 最近3个日志文件
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        lines = fp.readlines()
                        recent_logs.extend(lines[-50:])  # 每个文件最后50行
                except:
                    pass

            if recent_logs:
                # 统计行为类型
                action_types = defaultdict(int)
                for line in recent_logs:
                    if "assume" in line:
                        action_types["假设"] += 1
                    elif "plan" in line:
                        action_types["规划"] += 1
                    elif "track" in line:
                        action_types["执行"] += 1
                    elif "verify" in line:
                        action_types["校验"] += 1
                    elif "decide" in line:
                        action_types["决策"] += 1

                if action_types:
                    dominant = max(action_types, key=action_types.get)
                    insights.append({
                        "type": "user_behavior",
                        "title": "近期行为模式",
                        "content": f"近期行为以「{dominant}」为主({action_types[dominant]}次)，系统正在{dominant}驱动下进化",
                        "data": dict(action_types),
                        "timestamp": datetime.now().isoformat()
                    })

        return insights

    def generate_all_insights(self):
        """生成所有洞察和建议"""
        all_insights = []
        all_recommendations = []
        all_predictions = []

        # 跨引擎知识洞察
        ce_insights = self.generate_cross_engine_insights()
        all_insights.extend(ce_insights)

        # 进化趋势
        trends = self.generate_evolution_trends()
        all_predictions.extend(trends)

        # 系统健康
        health = self.generate_health_insights()
        all_recommendations.extend(health)

        # 用户行为
        behavior = self.generate_behavior_insights()
        all_insights.extend(behavior)

        # 保存
        self.insights = {
            "insights": all_insights,
            "recommendations": all_recommendations,
            "predictions": all_predictions,
            "last_generated": datetime.now().isoformat()
        }
        self._save_insights()

        return {
            "insights": all_insights,
            "recommendations": all_recommendations,
            "predictions": all_predictions,
            "total": len(all_insights) + len(all_recommendations) + len(all_predictions)
        }

    def get_insights(self, insight_type=None):
        """获取洞察"""
        if insight_type == "insights":
            return self.insights.get("insights", [])
        elif insight_type == "recommendations":
            return self.insights.get("recommendations", [])
        elif insight_type == "predictions":
            return self.insights.get("predictions", [])
        else:
            return self.insights

    def generate_report(self):
        """生成综合洞察报告"""
        # 先确保有最新数据
        self.generate_all_insights()

        report = []
        report.append("=" * 60)
        report.append("智能主动洞察与建议报告")
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)

        # 洞察
        insights = self.insights.get("insights", [])
        if insights:
            report.append("\n【洞察】")
            for i, insight in enumerate(insights, 1):
                report.append(f"\n{i}. {insight.get('title', '未命名')}")
                report.append(f"   {insight.get('content', '')}")

        # 建议
        recommendations = self.insights.get("recommendations", [])
        if recommendations:
            report.append("\n\n【建议】")
            for i, rec in enumerate(recommendations, 1):
                severity = rec.get("severity", "info")
                severity_emoji = {"warning": "[!]", "info": "[i]", "success": "[OK]"}.get(severity, "[i]")
                report.append(f"\n{i}. {severity_emoji} {rec.get('title', '未命名')}")
                report.append(f"   {rec.get('content', '')}")

        # 预测
        predictions = self.insights.get("predictions", [])
        if predictions:
            report.append("\n\n【预测】")
            for i, pred in enumerate(predictions, 1):
                report.append(f"\n{i}. {pred.get('title', '未命名')}")
                report.append(f"   {pred.get('content', '')}")

        report.append("\n" + "=" * 60)
        report.append("报告结束")
        report.append("=" * 60)

        return "\n".join(report)


def main():
    """主函数"""
    import sys

    advisor = ProactiveInsightAdvisor()

    if len(sys.argv) < 2:
        print("智能主动洞察与建议引擎")
        print("\n用法:")
        print("  python proactive_insight_advisor.py status          - 查看状态")
        print("  python proactive_insight_advisor.py generate       - 生成洞察和建议")
        print("  python proactive_insight_advisor.py insights       - 获取洞察列表")
        print("  python proactive_insight_advisor.py recommendations - 获取建议列表")
        print("  python proactive_insight_advisor.py predictions    - 获取预测列表")
        print("  python proactive_insight_advisor.py report         - 生成完整报告")
        return

    command = sys.argv[1]

    if command == "status":
        status = advisor.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    elif command == "generate":
        result = advisor.generate_all_insights()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "insights":
        insights = advisor.get_insights("insights")
        print(json.dumps(insights, ensure_ascii=False, indent=2))
    elif command == "recommendations":
        recs = advisor.get_insights("recommendations")
        print(json.dumps(recs, ensure_ascii=False, indent=2))
    elif command == "predictions":
        preds = advisor.get_insights("predictions")
        print(json.dumps(preds, ensure_ascii=False, indent=2))
    elif command == "report":
        print(advisor.generate_report())
    else:
        print(f"未知命令: {command}")
        print("可用命令: status, generate, insights, recommendations, predictions, report")


if __name__ == "__main__":
    main()