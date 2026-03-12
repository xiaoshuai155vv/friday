#!/usr/bin/env python3
"""
进化学习引擎 - 让策略引擎能够从历史进化结果中学习

功能：
1. 分析历史进化数据，提取有效特征
2. 建立进化效果评估模型（基于规则的学习）
3. 实现自适应进化方向推荐
4. 与 evolution_strategy_engine 和 evolution_history_db 集成

使用方法：
    python evolution_learning_engine.py analyze
    python evolution_learning_engine.py learn
    python evolution_learning_engine.py recommend
    python evolution_learning_engine.py status
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE = PROJECT_ROOT / "runtime" / "state"
RUNTIME_LOGS = PROJECT_ROOT / "runtime" / "logs"
REFERENCES = PROJECT_ROOT / "references"

# 尝试导入进化历史数据库
try:
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    from evolution_history_db import (
        get_all_evolution_rounds,
        get_evolution_round,
        get_latest_evolution_round,
        init_database
    )
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False


class EvolutionLearningEngine:
    """进化学习引擎 - 从历史数据中学习和优化"""

    def __init__(self):
        self.state_dir = RUNTIME_STATE
        self.logs_dir = RUNTIME_LOGS
        self.references_dir = REFERENCES

        # 确保目录存在
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # 学习模型输出路径
        self.model_file = self.state_dir / "evolution_learning_model.json"
        self.insights_file = self.state_dir / "evolution_learning_insights.json"
        self.recommendations_file = self.state_dir / "evolution_learning_recommendations.json"

    def analyze(self) -> Dict[str, Any]:
        """分析历史进化数据，提取特征"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "data_source": "database" if DB_AVAILABLE else "files",
            "features": self._extract_features(),
            "statistics": self._compute_statistics(),
            "patterns": self._identify_patterns(),
            "learned_insights": []
        }

        # 基于分析生成学习洞察
        analysis["learned_insights"] = self._generate_insights(analysis)

        return analysis

    def _extract_features(self) -> Dict[str, Any]:
        """从历史数据中提取特征"""
        features = {
            "total_rounds": 0,
            "success_rate": 0.0,
            "avg_execution_time": 0.0,
            "goal_categories": defaultdict(int),
            "status_distribution": defaultdict(int),
            "time_trends": []
        }

        rounds_data = []

        # 优先从数据库获取
        if DB_AVAILABLE:
            try:
                all_rounds = get_all_evolution_rounds()
                for round_data in all_rounds:
                    info = round_data.get("round_info", {})
                    rounds_data.append(info)
            except Exception as e:
                print(f"数据库查询失败: {e}")

        # 解析文件作为备选
        if not rounds_data:
            rounds_data = self._extract_from_files()

        if not rounds_data:
            return features

        features["total_rounds"] = len(rounds_data)

        # 计算统计特征
        success_count = 0
        total_time = 0.0

        for round_info in rounds_data:
            status = round_info.get("status", "")
            if status == "success":
                success_count += 1

            exec_time = round_info.get("execution_time", 0.0) or 0.0
            total_time += exec_time

            # 分类统计
            goal = round_info.get("current_goal", "")
            if goal:
                # 提取目标类别
                if "数据库" in goal or "DB" in goal or "db" in goal:
                    features["goal_categories"]["database"] += 1
                elif "策略" in goal or "策略引擎" in goal:
                    features["goal_categories"]["strategy"] += 1
                elif "自动化" in goal or "引擎" in goal:
                    features["goal_categories"]["automation"] += 1
                elif "评估" in goal or "分析" in goal:
                    features["goal_categories"]["analysis"] += 1
                elif "学习" in goal or "智能" in goal:
                    features["goal_categories"]["learning"] += 1
                else:
                    features["goal_categories"]["other"] += 1

            features["status_distribution"][status] += 1

        # 计算衍生特征
        if features["total_rounds"] > 0:
            features["success_rate"] = success_count / features["total_rounds"]
            features["avg_execution_time"] = total_time / features["total_rounds"]

        # 将 defaultdict 转换为普通 dict
        features["goal_categories"] = dict(features["goal_categories"])
        features["status_distribution"] = dict(features["status_distribution"])

        return features

    def _extract_from_files(self) -> List[Dict[str, Any]]:
        """从文件中提取历史数据"""
        rounds = []

        # 从 evolution_auto_last.md 提取
        last_file = self.references_dir / "evolution_auto_last.md"
        if last_file.exists():
            content = last_file.read_text(encoding="utf-8")
            import re

            # 提取 round 信息
            round_pattern = r"## (\d{4}-\d{2}-\d{2}) round (\d+)"
            matches = re.findall(round_pattern, content)

            for date_str, round_num in matches:
                rounds.append({
                    "round_number": int(round_num),
                    "timestamp": date_str,
                    "status": "success"  # 从历史看都是成功的
                })

        # 从 evolution_completed_*.json 提取
        completed_dir = self.state_dir
        if completed_dir.exists():
            for json_file in sorted(completed_dir.glob("evolution_completed_*.json")):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        rounds.append({
                            "round_number": data.get("loop_round", 0),
                            "timestamp": data.get("timestamp", ""),
                            "status": data.get("status", "unknown"),
                            "current_goal": data.get("current_goal", ""),
                            "execution_time": data.get("execution_time", 0.0)
                        })
                except Exception:
                    pass

        return rounds

    def _compute_statistics(self) -> Dict[str, Any]:
        """计算统计指标"""
        features = self._extract_features()

        stats = {
            "total_evolution_rounds": features["total_rounds"],
            "success_rate": features["success_rate"],
            "avg_execution_time": features["avg_execution_time"],
            "goal_category_distribution": features["goal_categories"],
            "status_breakdown": features["status_distribution"]
        }

        return stats

    def _identify_patterns(self) -> List[Dict[str, Any]]:
        """识别进化模式"""
        patterns = []

        features = self._extract_features()

        # 模式1：高频成功
        if features["success_rate"] > 0.8:
            patterns.append({
                "name": "high_success_rate",
                "description": "进化环成功率较高，系统运行稳定",
                "confidence": features["success_rate"]
            })

        # 模式2：目标集中
        categories = features["goal_categories"]
        if categories:
            top_category = max(categories.items(), key=lambda x: x[1])
            if top_category[1] >= 3:
                patterns.append({
                    "name": "focused_goals",
                    "description": f"进化目标集中在「{top_category[0]}」领域",
                    "confidence": top_category[1] / features["total_rounds"]
                })

        # 模式3：元进化趋势
        if "meta_evolution" in str(categories) or "learning" in str(categories):
            patterns.append({
                "name": "meta_evolution_trend",
                "description": "系统倾向于进化自身（元进化），这是高级智能的标志",
                "confidence": 0.7
            })

        return patterns

    def _generate_insights(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """基于分析生成学习洞察"""
        insights = []
        features = analysis.get("features", {})
        patterns = analysis.get("patterns", [])

        # 洞察1：基于成功率的建议
        success_rate = features.get("success_rate", 0)
        if success_rate > 0.9:
            insights.append({
                "type": "positive",
                "category": "stability",
                "insight": "进化环非常稳定，成功率超过90%",
                "action": "可以尝试更具挑战性的进化方向"
            })
        elif success_rate > 0.7:
            insights.append({
                "type": "positive",
                "category": "stability",
                "insight": "进化环运行良好，成功率超过70%",
                "action": "继续保持当前策略，适度探索新方向"
            })

        # 洞察2：基于时间效率的建议
        avg_time = features.get("avg_execution_time", 0)
        if avg_time > 2.0:
            insights.append({
                "type": "optimization",
                "category": "efficiency",
                "insight": f"平均进化执行时间较长（{avg_time:.2f}秒），有优化空间",
                "action": "考虑并行化或简化执行流程"
            })

        # 洞察3：基于模式识别的建议
        for pattern in patterns:
            if pattern.get("name") == "meta_evolution_trend":
                insights.append({
                    "type": "positive",
                    "category": "intelligence",
                    "insight": "系统展现出自进化能力，持续改进自身",
                    "action": "这是正确的方向，继续强化元进化能力"
                })

        # 洞察4：基于类别分布的建议
        categories = features.get("goal_categories", {})
        if "learning" not in categories and "strategy" not in categories:
            insights.append({
                "type": "suggestion",
                "category": "intelligence",
                "insight": "建议增强学习能力和策略优化",
                "action": "本轮正是要实现这个目标"
            })

        return insights

    def learn(self) -> Dict[str, Any]:
        """执行学习过程，更新模型"""
        # 分析数据
        analysis = self.analyze()

        # 构建学习模型
        model = {
            "timestamp": datetime.now().isoformat(),
            "version": "1.0",
            "features": analysis["features"],
            "patterns": analysis["patterns"],
            "insights": analysis["learned_insights"],
            "learned_weights": self._compute_learned_weights(analysis)
        }

        # 保存模型
        self._save_model(model)

        # 生成增强推荐
        recommendations = self._generate_enhanced_recommendations(analysis)
        self._save_recommendations(recommendations)

        return model

    def _compute_learned_weights(self, analysis: Dict[str, Any]) -> Dict[str, float]:
        """计算学习权重 - 基于历史数据调整进化方向优先级"""
        weights = {
            "meta_evolution": 0.3,
            "capability_expansion": 0.2,
            "stability_improvement": 0.2,
            "efficiency_optimization": 0.15,
            "integration": 0.15
        }

        features = analysis.get("features", {})
        patterns = analysis.get("patterns", [])

        # 根据成功率调整权重
        success_rate = features.get("success_rate", 0)
        if success_rate > 0.8:
            weights["meta_evolution"] = 0.4  # 高成功率时更敢于尝试元进化
            weights["capability_expansion"] = 0.2

        # 根据执行时间调整
        avg_time = features.get("avg_execution_time", 0)
        if avg_time > 2.0:
            weights["efficiency_optimization"] = 0.3  # 时间长时更关注效率

        # 根据模式调整
        for pattern in patterns:
            if pattern.get("name") == "meta_evolution_trend":
                weights["meta_evolution"] = min(0.5, weights["meta_evolution"] + 0.1)

        return weights

    def _generate_enhanced_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成基于学习的增强推荐"""
        recommendations = []
        features = analysis.get("features", {})
        insights = analysis.get("learned_insights", [])
        weights = self._compute_learned_weights(analysis)

        # 推荐1：基于权重的优先级
        sorted_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        top_weight = sorted_weights[0]

        recommendations.append({
            "priority": "high",
            "category": "strategy",
            "title": f"基于学习的优先级调整",
            "description": f"根据历史学习，当前最高优先级应为「{top_weight[0]}」（权重 {top_weight[1]:.2f}）",
            "confidence": 0.85,
            "based_on": "learned_weights"
        })

        # 推荐2：洞察转化
        for insight in insights:
            if insight.get("type") == "suggestion":
                recommendations.append({
                    "priority": "medium",
                    "category": insight.get("category", "general"),
                    "title": "学习洞察建议",
                    "description": insight.get("insight", ""),
                    "action": insight.get("action", ""),
                    "confidence": 0.7,
                    "based_on": "insights"
                })

        # 推荐3：元进化增强
        if weights.get("meta_evolution", 0) > 0.3:
            recommendations.append({
                "priority": "high",
                "category": "meta_evolution",
                "title": "强化元进化能力",
                "description": "系统展现出良好的自进化能力，建议继续深化",
                "action": "持续优化进化环自身",
                "confidence": 0.8,
                "based_on": "pattern_recognition"
            })

        return recommendations

    def _save_model(self, model: Dict[str, Any]) -> None:
        """保存学习模型"""
        with open(self.model_file, "w", encoding="utf-8") as f:
            json.dump(model, f, ensure_ascii=False, indent=2)

        # 保存洞察
        insights_data = {
            "timestamp": model["timestamp"],
            "insights": model["insights"],
            "patterns": model["patterns"]
        }
        with open(self.insights_file, "w", encoding="utf-8") as f:
            json.dump(insights_data, f, ensure_ascii=False, indent=2)

    def _save_recommendations(self, recommendations: List[Dict[str, Any]]) -> None:
        """保存推荐结果"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "recommendations": recommendations
        }
        with open(self.recommendations_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def recommend(self) -> Dict[str, Any]:
        """获取学习增强的推荐"""
        # 如果已有模型，直接返回
        if self.recommendations_file.exists():
            with open(self.recommendations_file, "r", encoding="utf-8") as f:
                return json.load(f)

        # 否则重新学习
        model = self.learn()
        return {
            "recommendations": model.get("learned_insights", []),
            "learned_weights": model.get("learned_weights", {})
        }

    def get_model(self) -> Dict[str, Any]:
        """获取当前学习模型"""
        if self.model_file.exists():
            with open(self.model_file, "r", encoding="utf-8") as f:
                return json.load(f)

        return {
            "status": "no_model",
            "message": "请先运行 learn 命令生成学习模型"
        }

    def status(self) -> Dict[str, Any]:
        """获取学习引擎状态"""
        model_exists = self.model_file.exists()
        model = self.get_model() if model_exists else None

        return {
            "status": "active" if model_exists else "inactive",
            "model_version": model.get("version") if model else None,
            "last_updated": model.get("timestamp") if model else "never",
            "total_insights": len(model.get("learned_insights", [])) if model else 0,
            "total_patterns": len(model.get("patterns", [])) if model else 0
        }


def main():
    """主函数"""
    engine = EvolutionLearningEngine()

    if len(sys.argv) < 2:
        print("进化学习引擎")
        print("用法:")
        print("  python evolution_learning_engine.py analyze  - 分析历史数据，提取特征")
        print("  python evolution_learning_engine.py learn    - 执行学习，更新模型")
        print("  python evolution_learning_engine.py recommend - 获取学习增强的推荐")
        print("  python evolution_learning_engine.py status   - 查看学习引擎状态")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "analyze":
        result = engine.analyze()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "learn":
        result = engine.learn()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "recommend":
        result = engine.recommend()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "status":
        result = engine.status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()