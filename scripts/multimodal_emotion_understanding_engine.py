"""
智能多模态情感理解与智能响应增强引擎 (Multimodal Emotion Understanding Engine)
让系统能够综合文本、时间、行为模式、历史交互等多维度理解用户情绪，
做出更精准、更有温度的响应。

这是对 emotion_engine 的增强版本（version 1.0.0）。
"""

import json
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# 尝试导入原有 emotion_engine
try:
    from emotion_engine import EmotionEngine
    BASE_EMOTION_ENGINE = True
except ImportError:
    BASE_EMOTION_ENGINE = False


class MultimodalEmotionUnderstandingEngine:
    """
    多模态情感理解与智能响应增强引擎

    功能：
    1. 文本情感分析（基于原有 emotion_engine）
    2. 时间维度分析（基于当前时间段推断情绪）
    3. 行为模式分析（基于用户最近的操作频率和活跃度）
    4. 历史交互分析（基于最近的情绪历史趋势）
    5. 多维度综合分析（融合以上所有维度）
    6. 与情境感知引擎集成（如果可用）
    7. 智能响应生成（基于综合分析结果）
    """

    VERSION = "1.0.0"

    def __init__(self):
        """初始化多模态情感理解引擎"""
        # 基础文本情感分析引擎
        self.base_emotion_engine = EmotionEngine() if BASE_EMOTION_ENGINE else None

        # 时间段情绪模式映射
        self.time_emotion_patterns = {
            'morning': {  # 6:00 - 12:00
                'typical': 'calm',
                'positive_weight': 0.2,  # 早上通常更有活力
                'description': '早晨时段，用户通常更有活力'
            },
            'afternoon': {  # 12:00 - 18:00
                'typical': 'calm',
                'positive_weight': 0.1,
                'description': '下午时段，工作状态'
            },
            'evening': {  # 18:00 - 22:00
                'typical': 'calm',
                'positive_weight': 0.0,
                'description': '晚间时段，可能放松或疲惫'
            },
            'night': {  # 22:00 - 6:00
                'typical': 'calm',
                'negative_weight': 0.1,  # 深夜可能疲惫
                'description': '深夜时段，用户可能疲惫'
            }
        }

        # 行为模式指标阈值
        self.behavior_thresholds = {
            'high_activity': 50,  # 高活跃度阈值（每天操作次数）
            'low_activity': 5,    # 低活跃度阈值
            'sudden_change_ratio': 0.5,  # 突变的阈值（变化超过50%）
        }

        # 情感历史存储路径
        self.emotion_history_path = Path("runtime/state/emotion_history.json")
        self._ensure_emotion_history_file()

        # 多维度权重配置
        self.dimension_weights = {
            'text': 0.5,       # 文本分析权重
            'time': 0.15,      # 时间维度权重
            'behavior': 0.2,   # 行为模式权重
            'history': 0.15    # 历史趋势权重
        }

    def _ensure_emotion_history_file(self):
        """确保情感历史文件存在"""
        if not self.emotion_history_path.exists():
            self.emotion_history_path.parent.mkdir(parents=True, exist_ok=True)
            self._save_emotion_history({})

    def _load_emotion_history(self) -> Dict:
        """加载情感历史"""
        try:
            with open(self.emotion_history_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_emotion_history(self, history: Dict):
        """保存情感历史"""
        try:
            with open(self.emotion_history_path, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _get_time_period(self) -> str:
        """获取当前时间段"""
        hour = datetime.now().hour
        if 6 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 18:
            return 'afternoon'
        elif 18 <= hour < 22:
            return 'evening'
        else:
            return 'night'

    def analyze_time_dimension(self) -> Dict:
        """
        分析时间维度对情绪的影响

        Returns:
            Dict: 时间维度分析结果
        """
        time_period = self._get_time_period()
        pattern = self.time_emotion_patterns[time_period]

        return {
            'time_period': time_period,
            'typical_emotion': pattern['typical'],
            'positive_weight': pattern.get('positive_weight', 0),
            'negative_weight': pattern.get('negative_weight', 0),
            'description': pattern['description'],
            'confidence': 0.3  # 时间维度的置信度相对较低
        }

    def analyze_behavior_dimension(self) -> Dict:
        """
        分析行为模式维度

        基于用户最近的操作频率和活跃度变化推断情绪状态

        Returns:
            Dict: 行为模式分析结果
        """
        # 尝试加载用户行为数据
        behavior_data = self._load_user_behavior_data()

        if not behavior_data:
            return {
                'emotion': 'calm',
                'confidence': 0.0,
                'description': '无行为数据',
                'activity_level': 'unknown'
            }

        # 计算最近的操作次数
        recent_operations = behavior_data.get('recent_operations', [])
        operation_count = len(recent_operations)

        # 推断活动水平
        if operation_count >= self.behavior_thresholds['high_activity']:
            activity_level = 'high'
            # 高活跃度可能是积极或焦虑
            inferred_emotion = 'happy'
        elif operation_count <= self.behavior_thresholds['low_activity']:
            activity_level = 'low'
            # 低活跃度可能是平静、疲惫或沮丧
            inferred_emotion = 'sad'
        else:
            activity_level = 'normal'
            inferred_emotion = 'calm'

        # 检查是否有突然变化
        change_ratio = behavior_data.get('change_ratio', 0)
        if abs(change_ratio) > self.behavior_thresholds['sudden_change_ratio']:
            # 有显著变化，可能有特殊情况
            if change_ratio > 0:
                inferred_emotion = 'surprised'
            else:
                inferred_emotion = 'fear'

        return {
            'emotion': inferred_emotion,
            'confidence': 0.4,  # 行为分析的置信度
            'activity_level': activity_level,
            'operation_count': operation_count,
            'change_ratio': change_ratio,
            'description': f'基于行为模式分析：活动水平{inferred_emotion}'
        }

    def _load_user_behavior_data(self) -> Dict:
        """加载用户行为数据"""
        behavior_path = Path("runtime/state/user_behavior_history.json")
        try:
            if behavior_path.exists():
                with open(behavior_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def analyze_history_dimension(self) -> Dict:
        """
        分析历史情绪趋势维度

        基于用户最近的情绪历史推断当前情绪

        Returns:
            Dict: 历史趋势分析结果
        """
        history = self._load_emotion_history()

        if not history or 'records' not in history or len(history['records']) == 0:
            return {
                'emotion': 'calm',
                'confidence': 0.0,
                'description': '无历史数据',
                'trend': 'stable'
            }

        # 获取最近的情绪记录（最近10条）
        recent_records = history['records'][-10:]

        # 统计最近的情绪分布
        emotion_counts = {}
        for record in recent_records:
            emotion = record.get('emotion', 'calm')
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        # 找出最常见的情绪
        if emotion_counts:
            dominant_emotion = max(emotion_counts, key=emotion_counts.get)
            # 计算趋势（最近是否有明显变化）
            if len(recent_records) >= 3:
                recent_emotions = [r.get('emotion', 'calm') for r in recent_records[-3:]]
                if len(set(recent_emotions)) == 1:
                    trend = 'stable'
                else:
                    trend = 'changing'
            else:
                trend = 'insufficient_data'
        else:
            dominant_emotion = 'calm'
            trend = 'stable'

        # 计算置信度（基于记录数量和一致性）
        confidence = min(0.5, len(recent_records) * 0.05)

        return {
            'emotion': dominant_emotion,
            'confidence': confidence,
            'description': f'基于历史趋势：{dominant_emotion}',
            'trend': trend,
            'recent_count': len(recent_records),
            'emotion_distribution': emotion_counts
        }

    def analyze_text_dimension(self, text: str) -> Dict:
        """
        分析文本维度（基于原有 emotion_engine）

        Args:
            text (str): 用户输入文本

        Returns:
            Dict: 文本情感分析结果
        """
        if self.base_emotion_engine:
            emotion, intensity = self.base_emotion_engine.detect_emotion(text)
            return {
                'emotion': emotion,
                'intensity': intensity,
                'confidence': min(0.9, intensity + 0.3),  # 文本分析的置信度较高
                'description': f'基于文本分析：{emotion}({intensity:.2f})'
            }
        else:
            # 如果没有基础引擎，做简单的关键词分析
            return self._simple_text_analysis(text)

    def _simple_text_analysis(self, text: str) -> Dict:
        """简单的文本分析（当 emotion_engine 不可用时）"""
        positive_words = ['开心', '快乐', '高兴', '好', '棒', '喜欢', '感谢', '谢谢', '太好了']
        negative_words = ['难过', '生气', '愤怒', '伤心', '失望', '糟糕', '烦', '讨厌', '累']

        pos_count = sum(1 for word in positive_words if word in text)
        neg_count = sum(1 for word in negative_words if word in text)

        if pos_count > neg_count:
            return {'emotion': 'happy', 'confidence': 0.6, 'description': '基于简单文本分析'}
        elif neg_count > pos_count:
            return {'emotion': 'sad', 'confidence': 0.6, 'description': '基于简单文本分析'}
        else:
            return {'emotion': 'calm', 'confidence': 0.3, 'description': '基于简单文本分析'}

    def analyze_context_dimension(self, context_data: Optional[Dict] = None) -> Dict:
        """
        分析情境维度（与 context_aware_service_orchestrator 集成）

        Args:
            context_data (Dict): 情境感知数据（可选）

        Returns:
            Dict: 情境维度分析结果
        """
        if not context_data:
            return {
                'emotion': 'calm',
                'confidence': 0.0,
                'description': '无情境数据'
            }

        # 基于情境数据推断情绪
        # 例如：用户正在执行复杂任务 -> 可能焦虑
        # 用户正在娱乐 -> 开心

        context_type = context_data.get('context_type', 'unknown')

        context_emotion_map = {
            'focus_work': {'emotion': 'calm', 'description': '专注工作状态'},
            'entertainment': {'emotion': 'happy', 'description': '娱乐状态'},
            'stress': {'emotion': 'fear', 'description': '压力状态'},
            'relaxation': {'emotion': 'calm', 'description': '放松状态'},
            'meeting': {'emotion': 'calm', 'description': '会议状态'},
            'communication': {'emotion': 'happy', 'description': '交流状态'}
        }

        if context_type in context_emotion_map:
            info = context_emotion_map[context_type]
            return {
                'emotion': info['emotion'],
                'confidence': 0.5,
                'description': f'基于情境分析：{info["description"]}',
                'context_type': context_type
            }

        return {
            'emotion': 'calm',
            'confidence': 0.0,
            'description': '无法从情境推断情绪',
            'context_type': context_type
        }

    def comprehensive_analysis(self, text: str, context_data: Optional[Dict] = None) -> Dict:
        """
        多维度综合情感分析

        融合文本、时间、行为、历史、情境等多个维度的分析结果

        Args:
            text (str): 用户输入文本
            context_data (Dict): 情境感知数据（可选）

        Returns:
            Dict: 综合分析结果
        """
        # 各维度分析
        text_analysis = self.analyze_text_dimension(text)
        time_analysis = self.analyze_time_dimension()
        behavior_analysis = self.analyze_behavior_dimension()
        history_analysis = self.analyze_history_dimension()
        context_analysis = self.analyze_context_dimension(context_data)

        # 计算加权综合情绪得分
        emotion_scores = {}

        # 各维度的分析结果列表
        dimensions = [
            ('text', text_analysis, self.dimension_weights['text']),
            ('time', time_analysis, self.dimension_weights['time']),
            ('behavior', behavior_analysis, self.dimension_weights['behavior']),
            ('history', history_analysis, self.dimension_weights['history']),
        ]

        # 如果有情境数据，加入综合分析
        if context_data and context_analysis.get('confidence', 0) > 0:
            dimensions.append(('context', context_analysis, 0.1))

        # 计算各情绪的加权得分
        emotions = ['happy', 'sad', 'angry', 'surprised', 'fear', 'disgusted', 'calm']

        for emotion in emotions:
            score = 0.0
            for dim_name, analysis, weight in dimensions:
                if analysis.get('emotion') == emotion:
                    confidence = analysis.get('confidence', 0.3)
                    score += confidence * weight

            emotion_scores[emotion] = score

        # 找出最高分的情绪
        if not emotion_scores:
            dominant_emotion = 'calm'
        else:
            dominant_emotion = max(emotion_scores, key=emotion_scores.get)

        # 计算综合置信度
        total_confidence = sum(analysis.get('confidence', 0) * weight
                               for _, analysis, weight in dimensions)

        # 保存当前情绪到历史
        self._record_emotion(dominant_emotion, text)

        return {
            'dominant_emotion': dominant_emotion,
            'confidence': min(0.95, total_confidence),
            'emotion_scores': emotion_scores,
            'dimensions': {
                'text': text_analysis,
                'time': time_analysis,
                'behavior': behavior_analysis,
                'history': history_analysis,
                'context': context_analysis
            },
            'timestamp': datetime.now().isoformat(),
            'input_text': text
        }

    def _record_emotion(self, emotion: str, text: str):
        """记录情绪到历史"""
        history = self._load_emotion_history()

        if 'records' not in history:
            history['records'] = []

        # 添加新记录
        record = {
            'emotion': emotion,
            'text': text[:50] if text else '',  # 只保存前50字
            'timestamp': datetime.now().isoformat()
        }

        history['records'].append(record)

        # 只保留最近100条记录
        if len(history['records']) > 100:
            history['records'] = history['records'][-100:]

        self._save_emotion_history(history)

    def generate_response(self, analysis_result: Dict) -> str:
        """
        根据综合分析结果生成智能响应

        Args:
            analysis_result (Dict): comprehensive_analysis 的结果

        Returns:
            str: 响应文本
        """
        emotion = analysis_result['dominant_emotion']
        confidence = analysis_result['confidence']
        text = analysis_result.get('input_text', '')

        # 响应模板（增强版）
        enhanced_responses = {
            'happy': [
                "听到你这么说我也感到很开心呢！有什么好事分享一下吗？",
                "你的好心情真是感染到我了！继续保持哦~",
                "太棒了！能让你开心的事情一定很有意义吧？"
            ],
            'sad': [
                "感觉你今天有点低落呢。我在这里陪你聊聊可以吗？",
                "每个人都会有情绪低落的时候，说出来可能会好受些。",
                "如果愿意的话，可以跟我倾诉一下，我认真听。"
            ],
            'angry': [
                "能感觉到你现在很生气。先深呼吸一下，我们一起想办法解决。",
                "愤怒是很正常的情绪，但别让它伤害到自己。",
                "先冷静一下，不管发生什么，我们一起面对。"
            ],
            'surprised': [
                "哇，真的很出乎意料呢！怎么回事呀？",
                "这个惊喜太大了吧！快说说发生了什么。",
                "确实很让人震惊呢！到底是怎么回事？"
            ],
            'fear': [
                "别担心，不管发生什么，我都会帮你的。",
                "勇敢一点，你不是一个人。",
                "让我们一起想办法，没什么过不去的坎。"
            ],
            'disgusted': [
                "确实让人很不舒服呢。到底发生了什么？",
                "我能理解你的感受。有什么我可以帮忙的吗？",
                "这种情况确实让人很无奈。"
            ],
            'calm': [
                "保持这样的心态很棒呢。有什么我可以帮你的吗？",
                "很欣赏你现在平和的状态。",
                "从容面对一切，这是很珍贵的品质。"
            ]
        }

        # 根据置信度调整响应
        if confidence < 0.3:
            # 低置信度，使用更温和的响应
            base_responses = enhanced_responses.get(emotion, enhanced_responses['calm'])
            response = random.choice(base_responses[:1])
        else:
            # 高置信度，使用完整响应
            base_responses = enhanced_responses.get(emotion, enhanced_responses['calm'])
            response = random.choice(base_responses)

        # 如果文本中有明确的需求，结合文本内容
        if text and len(text) > 5:
            # 可以根据文本内容添加个性化回应
            pass

        return response

    def analyze_and_respond(self, text: str, context_data: Optional[Dict] = None) -> str:
        """
        分析用户情绪并生成响应（主要接口）

        Args:
            text (str): 用户输入文本
            context_data (Dict): 情境感知数据（可选）

        Returns:
            str: 响应文本
        """
        # 综合分析
        analysis_result = self.comprehensive_analysis(text, context_data)

        # 生成响应
        response = self.generate_response(analysis_result)

        # 添加情绪标签（可选）
        emotion = analysis_result['dominant_emotion']
        confidence = analysis_result['confidence']

        return f"[{emotion}({confidence:.2f})] {response}"

    def get_emotion_status(self) -> Dict:
        """
        获取当前情绪状态（用于外部查询）

        Returns:
            Dict: 当前情绪状态
        """
        history = self._load_emotion_history()

        if not history or 'records' not in history or len(history['records']) == 0:
            return {
                'current_emotion': 'calm',
                'confidence': 0.0,
                'description': '暂无情绪数据'
            }

        # 获取最近的情绪
        recent = history['records'][-1]
        return {
            'current_emotion': recent.get('emotion', 'calm'),
            'timestamp': recent.get('timestamp', ''),
            'description': '基于历史记录'
        }


def main():
    """主函数 - 用于测试"""
    engine = MultimodalEmotionUnderstandingEngine()

    print("=== 多模态情感理解引擎测试 ===")
    print(f"版本: {engine.VERSION}")
    print()

    # 测试用例
    test_cases = [
        "今天天气真好，我很开心！",
        "我今天心情有点不好，工作压力很大。",
        "气死我了！这简直太不公平了！",
        "哇，这个结果真是出乎意料！",
    ]

    print("--- 单次分析测试 ---")
    for text in test_cases:
        result = engine.analyze_and_respond(text)
        print(f"输入: {text}")
        print(f"响应: {result}")
        print("-" * 50)

    print()
    print("--- 综合分析测试 ---")
    text = "今天工作完成了，感觉还不错"
    analysis = engine.comprehensive_analysis(text)
    print(f"输入: {text}")
    print(f"综合分析结果:")
    print(f"  主情绪: {analysis['dominant_emotion']}")
    print(f"  置信度: {analysis['confidence']:.2f}")
    print(f"  各维度分析:")
    for dim, data in analysis['dimensions'].items():
        print(f"    {dim}: {data.get('emotion', 'N/A')} (置信度: {data.get('confidence', 0):.2f})")
    print("-" * 50)

    print()
    print("--- 时间维度分析 ---")
    time_analysis = engine.analyze_time_dimension()
    print(f"当前时段: {time_analysis['time_period']}")
    print(f"典型情绪: {time_analysis['typical_emotion']}")
    print(f"描述: {time_analysis['description']}")


if __name__ == "__main__":
    main()