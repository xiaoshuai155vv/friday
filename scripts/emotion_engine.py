"""
智能情感识别与响应引擎
让系统能够感知用户情绪并做出有温度的响应
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Tuple

class EmotionEngine:
    """情感识别与响应引擎"""

    def __init__(self):
        """初始化情感引擎"""
        # 情绪词汇库
        self.emotion_lexicon = {
            'happy': ['开心', '快乐', '高兴', '愉快', '喜悦', '兴奋', '激动', '欢乐', '笑', '乐'],
            'sad': ['难过', '悲伤', '沮丧', '失落', '忧郁', '痛苦', '绝望', '伤心', '流泪', '愁'],
            'angry': ['生气', '愤怒', '恼火', '暴怒', '愤慨', '恼怒', '气愤', '火大', '暴躁'],
            'surprised': ['惊讶', '吃惊', '震惊', '意外', '惊愕', '吃惊', '诧异'],
            'fear': ['害怕', '恐惧', '担忧', '焦虑', '紧张', '恐慌', '惊恐', '惧怕'],
            'disgusted': ['厌恶', '反感', '恶心', '嫌弃', '讨厌', '憎恶'],
            'calm': ['平静', '冷静', '安详', '镇定', '从容', '淡定', '沉着']
        }

        # 情绪响应模板
        self.emotion_responses = {
            'happy': [
                "听起来你今天很开心呢！有什么值得庆祝的事情吗？",
                "很高兴听到你这么开心！继续保持好心情哦~",
                "你的快乐感染了我！希望你能一直保持这种好心情。",
                "开心的时候做什么都特别有劲儿呢！"
            ],
            'sad': [
                "感觉你现在有些低落呢，要不要聊聊发生了什么？",
                "难过的时候记得有人关心你哦，我会在这里陪着你。",
                "每个人都会有情绪低落的时候，这是正常的。",
                "如果愿意的话，可以跟我说说心里的想法。"
            ],
            'angry': [
                "看起来你现在很生气呢，深呼吸一下，慢慢来。",
                "愤怒的时候容易冲动，不如先冷静一下再处理这件事。",
                "生气是正常的情绪反应，但要注意不要伤害到自己或他人。",
                "可以试着把愤怒说出来，或者做一些让自己放松的事情。"
            ],
            'surprised': [
                "哇，看来今天有些出乎意料的事情发生呢！",
                "惊讶的表情真可爱，有什么惊喜吗？",
                "遇到让你惊讶的事情了吗？这说明生活还是挺有趣的。",
                "有时候惊喜会让生活变得更加精彩呢！"
            ],
            'fear': [
                "担心和害怕都是正常的情绪，但不要让它控制你。",
                "勇敢面对恐惧，你会发现其实并没有那么可怕。",
                "害怕的时候可以告诉自己：我已经尽力了。",
                "深呼吸，相信自己有能力应对这些挑战。"
            ],
            'disgusted': [
                "看起来你对某些事情感到很不舒服呢。",
                "厌恶感往往源于我们对某些事物的强烈感受。",
                "不喜欢某样东西是很正常的，不要勉强自己。",
                "有时候我们需要给自己一点时间和空间来处理这些感受。"
            ],
            'calm': [
                "保持平静的心态很棒，这会让你更清晰地看待问题。",
                "内心平和的时候，往往能做出更好的判断。",
                "这份宁静很珍贵，愿你能一直拥有这样的状态。",
                "在平静中思考，总能找到解决问题的方法。"
            ]
        }

        # 情绪强度阈值
        self.emotion_thresholds = {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.8
        }

    def detect_emotion(self, text: str) -> Tuple[str, float]:
        """
        检测文本中的情绪

        Args:
            text (str): 输入文本

        Returns:
            Tuple[str, float]: (情绪标签, 强度)
        """
        if not text:
            return 'calm', 0.0

        # 统计各类情绪词汇出现次数
        emotion_scores = {}
        total_words = len(text.split())

        for emotion, keywords in self.emotion_lexicon.items():
            score = 0
            for keyword in keywords:
                # 对于中文，直接使用 count 统计出现次数
                # 避免使用正则表达式 \b（中文没有单词边界）
                score += text.count(keyword)

            # 计算情绪得分（归一化）
            if total_words > 0:
                emotion_scores[emotion] = score / total_words
            else:
                emotion_scores[emotion] = 0

        # 找出最高分的情绪
        if not emotion_scores:
            return 'calm', 0.0

        dominant_emotion = max(emotion_scores, key=emotion_scores.get)
        intensity = emotion_scores[dominant_emotion]

        # 如果强度很低，返回平静
        if intensity < self.emotion_thresholds['low']:
            return 'calm', 0.0

        return dominant_emotion, intensity

    def generate_response(self, emotion: str, intensity: float) -> str:
        """
        根据情绪生成响应

        Args:
            emotion (str): 情绪标签
            intensity (float): 情绪强度

        Returns:
            str: 响应文本
        """
        if emotion not in self.emotion_responses:
            emotion = 'calm'

        # 根据强度选择不同的响应
        if intensity < self.emotion_thresholds['medium']:
            # 弱情绪 - 选择温和的回应
            responses = self.emotion_responses[emotion][:2]
        elif intensity < self.emotion_thresholds['high']:
            # 中等情绪 - 选择适中的回应
            responses = self.emotion_responses[emotion][1:3]
        else:
            # 强情绪 - 选择积极的回应
            responses = self.emotion_responses[emotion]

        # 随机选择一个响应
        import random
        return random.choice(responses)

    def analyze_and_respond(self, text: str) -> str:
        """
        分析文本情绪并生成响应

        Args:
            text (str): 输入文本

        Returns:
            str: 情绪分析和响应
        """
        emotion, intensity = self.detect_emotion(text)
        response = self.generate_response(emotion, intensity)

        return f"[{emotion}({intensity:.2f})] {response}"

    def get_emotion_details(self, text: str) -> Dict:
        """
        获取详细的情绪分析结果

        Args:
            text (str): 输入文本

        Returns:
            Dict: 情绪分析详情
        """
        emotion, intensity = self.detect_emotion(text)
        return {
            'detected_emotion': emotion,
            'intensity': intensity,
            'timestamp': datetime.now().isoformat(),
            'input_text': text
        }

def main():
    """主函数 - 用于测试"""
    engine = EmotionEngine()

    # 测试用例
    test_cases = [
        "今天天气真好，我很开心！",
        "我今天心情有点不好，工作压力很大。",
        "气死我了！这简直太不公平了！",
        "哇，这个结果真是出乎意料！",
        "我有点害怕明天的演讲。",
        "这个菜的味道真差，我真受不了。",
        "一切都很好，我很平静。"
    ]

    print("=== 情感识别测试 ===")
    for text in test_cases:
        result = engine.analyze_and_respond(text)
        details = engine.get_emotion_details(text)
        print(f"输入: {text}")
        print(f"结果: {result}")
        print(f"详情: {details}")
        print("-" * 50)

if __name__ == "__main__":
    main()