"""
智能个性化深度学习引擎
让系统能够基于多维度用户数据（交互历史、时间模式、行为序列、场景偏好）进行深度学习，
实现更精准的个性化推荐和预测。

功能：
1. 多维度用户数据分析
2. 行为序列深度学习
3. 时间模式挖掘
4. 个性化预测与推荐
5. 与现有引擎集成
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter
import re


class DeepPersonalizationEngine:
    """智能个性化深度学习引擎"""

    def __init__(self, data_dir=None):
        if data_dir is None:
            base_dir = Path(__file__).parent.parent
            data_dir = base_dir / "runtime" / "state" / "personalization"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 用户数据存储路径
        self.user_profile_path = self.data_dir / "user_profile.json"
        self.behavior_sequences_path = self.data_dir / "behavior_sequences.json"
        self.time_patterns_path = self.data_dir / "time_patterns.json"
        self.predictions_path = self.data_dir / "predictions.json"

        # 加载现有数据
        self.user_profile = self._load_json(self.user_profile_path, {})
        self.behavior_sequences = self._load_json(self.behavior_sequences_path, {"sequences": []})
        self.time_patterns = self._load_json(self.time_patterns_path, {})
        self.predictions = self._load_json(self.predictions_path, {})

    def _load_json(self, path, default):
        """安全加载 JSON 文件"""
        try:
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载 {path} 失败: {e}")
        return default

    def _save_json(self, path, data):
        """安全保存 JSON 文件"""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存 {path} 失败: {e}")
            return False

    def record_interaction(self, interaction_type, content="", context=None):
        """
        记录用户交互
        interaction_type: 交互类型（如 "command", "scenario", "query" 等）
        content: 交互内容
        context: 附加上下文信息
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": interaction_type,
            "content": content,
            "context": context or {}
        }

        # 更新行为序列
        self.behavior_sequences["sequences"].append(entry)
        # 只保留最近 1000 条
        if len(self.behavior_sequences["sequences"]) > 1000:
            self.behavior_sequences["sequences"] = self.behavior_sequences["sequences"][-1000:]
        self._save_json(self.behavior_sequences_path, self.behavior_sequences)

        # 更新用户画像
        self._update_user_profile(interaction_type, content, context)

        return {"status": "recorded", "entry_count": len(self.behavior_sequences["sequences"])}

    def _update_user_profile(self, interaction_type, content, context):
        """更新用户画像"""
        # 确保 interactions 是 dict 类型
        if "interactions" not in self.user_profile or not isinstance(self.user_profile["interactions"], dict):
            self.user_profile["interactions"] = {}
        self.user_profile["interactions"][interaction_type] = self.user_profile["interactions"].get(interaction_type, 0) + 1

        # 记录关键词/命令频率
        if content:
            # 确保 keywords 是 dict 类型
            if "keywords" not in self.user_profile or not isinstance(self.user_profile["keywords"], dict):
                self.user_profile["keywords"] = {}
            # 提取关键词（简单分词）
            words = re.findall(r'\w+', content.lower())
            for word in words:
                self.user_profile["keywords"][word] = self.user_profile["keywords"].get(word, 0) + 1

        # 更新时间
        self.user_profile["last_updated"] = datetime.now().isoformat()
        self._save_json(self.user_profile_path, self.user_profile)

    def analyze_time_patterns(self):
        """分析时间模式"""
        if not self.behavior_sequences.get("sequences", []):
            return {"status": "no_data", "message": "无交互数据可供分析"}

        # 按小时、星期分析
        hour_counts = defaultdict(int)
        weekday_counts = defaultdict(int)
        date_counts = defaultdict(int)

        for entry in self.behavior_sequences["sequences"]:
            try:
                dt = datetime.fromisoformat(entry["timestamp"])
                hour_counts[dt.hour] += 1
                weekday_counts[dt.strftime("%A")] += 1
                date_counts[dt.date()] += 1
            except:
                continue

        # 找出高峰时段
        peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        peak_weekdays = sorted(weekday_counts.items(), key=lambda x: x[1], reverse=True)[:2]

        # 工作日 vs 周末
        weekday_total = sum(weekday_counts.get(day, 0) for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        weekend_total = sum(weekday_counts.get(day, 0) for day in ["Saturday", "Sunday"])

        self.time_patterns = {
            "peak_hours": [{"hour": h, "count": c} for h, c in peak_hours],
            "peak_weekdays": [{"day": d, "count": c} for d, c in peak_weekdays],
            "weekday_ratio": weekday_total / max(1, weekday_total + weekend_total),
            "weekend_ratio": weekend_total / max(1, weekday_total + weekend_total),
            "total_interactions": len(self.behavior_sequences["sequences"]),
            "analyzed_at": datetime.now().isoformat()
        }

        self._save_json(self.time_patterns_path, self.time_patterns)
        return self.time_patterns

    def analyze_behavior_sequences(self, window_size=5):
        """分析行为序列，发现常见模式"""
        if len(self.behavior_sequences["sequences"]) < window_size:
            return {"status": "insufficient_data", "message": f"需要至少 {window_size} 条交互记录"}

        sequences = self.behavior_sequences["sequences"]
        n = len(sequences)

        # 提取类型序列
        type_sequence = [s.get("type", "unknown") for s in sequences]

        # 查找常见模式（n-grams）
        patterns = defaultdict(int)
        for i in range(n - window_size + 1):
            pattern = tuple(type_sequence[i:i+window_size])
            patterns[pattern] += 1

        # 返回最常见的模式
        common_patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "patterns": [{"pattern": list(p), "count": c} for p, c in common_patterns],
            "total_sequences": n,
            "analyzed_at": datetime.now().isoformat()
        }

    def predict_next_action(self):
        """预测用户下一步可能想要什么"""
        if not self.behavior_sequences.get("sequences", []):
            return {"status": "no_data", "predictions": []}

        # 基于时间模式预测
        now = datetime.now()
        current_hour = now.hour
        current_weekday = now.strftime("%A")

        time_predictions = []

        # 检查当前时间是否是高峰时段
        if self.time_patterns.get("peak_hours"):
            for p in self.time_patterns["peak_hours"]:
                if p["hour"] == current_hour:
                    time_predictions.append({
                        "type": "time_based",
                        "reason": f"当前是高频使用时段 ({current_hour}点)",
                        "confidence": "high"
                    })
                    break

        # 基于最近行为预测
        recent_types = [s.get("type") for s in self.behavior_sequences["sequences"][-10:]]
        if recent_types:
            type_counter = Counter(recent_types)
            most_common = type_counter.most_common(1)[0]
            if most_common[1] >= 2:
                time_predictions.append({
                    "type": "behavior_based",
                    "reason": f"最近频繁使用 {most_common[0]}",
                    "confidence": "medium" if most_common[1] >= 3 else "low"
                })

        # 基于关键词预测
        if self.user_profile.get("keywords"):
            top_keywords = list(self.user_profile["keywords"].keys())[:5]
            if top_keywords:
                time_predictions.append({
                    "type": "keyword_based",
                    "reason": f"常用关键词: {', '.join(top_keywords[:3])}",
                    "confidence": "low"
                })

        # 保存预测结果
        self.predictions = {
            "current_time": now.isoformat(),
            "predictions": time_predictions,
            "generated_at": datetime.now().isoformat()
        }
        self._save_json(self.predictions_path, self.predictions)

        return self.predictions

    def get_personalized_recommendation(self, context=None):
        """
        获取个性化推荐
        基于用户画像、时间模式、行为序列进行综合推荐
        """
        context = context or {}

        recommendations = []

        # 基于时间模式推荐
        if self.time_patterns.get("peak_hours"):
            current_hour = datetime.now().hour
            for peak in self.time_patterns["peak_hours"]:
                if peak["hour"] == current_hour:
                    recommendations.append({
                        "type": "time_scenario",
                        "recommendation": "当前是您常用时段，是否需要执行常用操作？",
                        "confidence": "high"
                    })
                    break

        # 基于用户画像推荐
        if self.user_profile.get("interactions"):
            top_interactions = sorted(
                self.user_profile["interactions"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            if top_interactions:
                recommendations.append({
                    "type": "profile_based",
                    "recommendation": f"您最常使用的功能: {', '.join([i[0] for i in top_interactions])}",
                    "confidence": "high"
                })

        # 基于关键词推荐
        if self.user_profile.get("keywords"):
            top_keywords = list(self.user_profile["keywords"].keys())[:3]
            if top_keywords:
                recommendations.append({
                    "type": "keyword_scenario",
                    "recommendation": f"建议: {', '.join(top_keywords)} 相关的操作可能更适合您",
                    "confidence": "medium"
                })

        return {
            "recommendations": recommendations,
            "user_profile_summary": {
                "total_interactions": sum(self.user_profile.get("interactions", {}).values()),
                "unique_keywords": len(self.user_profile.get("keywords", {})),
                "last_updated": self.user_profile.get("last_updated")
            },
            "generated_at": datetime.now().isoformat()
        }

    def get_user_insights(self):
        """获取用户洞察报告"""
        insights = {
            "user_profile": {
                "total_interactions": sum(self.user_profile.get("interactions", {}).values()),
                "interaction_types": self.user_profile.get("interactions", {}),
                "top_keywords": list(self.user_profile.get("keywords", {}).keys())[:10] if self.user_profile.get("keywords") else []
            },
            "time_patterns": {
                "peak_hours": self.time_patterns.get("peak_hours", []),
                "peak_weekdays": self.time_patterns.get("peak_weekdays", []),
                "weekday_usage_ratio": self.time_patterns.get("weekday_ratio", 0),
                "weekend_usage_ratio": self.time_patterns.get("weekend_ratio", 0)
            },
            "behavior_analysis": self.analyze_behavior_sequences(),
            "predictions": self.predict_next_action(),
            "generated_at": datetime.now().isoformat()
        }

        return insights

    def clear_data(self):
        """清除所有学习数据"""
        self.user_profile = {}
        self.behavior_sequences = {"sequences": []}
        self.time_patterns = {}
        self.predictions = {}

        self._save_json(self.user_profile_path, self.user_profile)
        self._save_json(self.behavior_sequences_path, self.behavior_sequences)
        self._save_json(self.time_patterns_path, self.time_patterns)
        self._save_json(self.predictions_path, self.predictions)

        return {"status": "cleared", "message": "所有学习数据已清除"}


def main():
    """CLI 入口"""
    import sys

    engine = DeepPersonalizationEngine()

    if len(sys.argv) < 2:
        print("用法:")
        print("  python deep_personalization_engine.py record <类型> [内容] [上下文]")
        print("  python deep_personalization_engine.py analyze-time")
        print("  python deep_personalization_engine.py analyze-sequences")
        print("  python deep_personalization_engine.py predict")
        print("  python deep_personalization_engine.py recommend")
        print("  python deep_personalization_engine.py insights")
        print("  python deep_personalization_engine.py clear")
        return

    command = sys.argv[1]

    if command == "record":
        if len(sys.argv) < 3:
            print("错误: 需要指定交互类型")
            return
        interaction_type = sys.argv[2]
        content = sys.argv[3] if len(sys.argv) > 3 else ""
        result = engine.record_interaction(interaction_type, content)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "analyze-time":
        result = engine.analyze_time_patterns()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "analyze-sequences":
        result = engine.analyze_behavior_sequences()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "predict":
        result = engine.predict_next_action()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "recommend":
        result = engine.get_personalized_recommendation()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "insights":
        result = engine.get_user_insights()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "clear":
        result = engine.clear_data()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {command}")


if __name__ == "__main__":
    main()