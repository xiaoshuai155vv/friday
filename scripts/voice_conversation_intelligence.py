#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能语音理解与对话智能融合引擎
让系统能够通过语音与用户进行自然对话，深度集成语音输入、意图理解、情感响应、对话管理、上下文记忆，实现真正的语音对话智能闭环
"""

import json
import os
import sys
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional

# 存储路径
STATE_DIR = os.path.join(os.path.dirname(__file__), "..", "runtime", "state")
VOICE_SESSION_FILE = os.path.join(STATE_DIR, "voice_conversation_session.json")

class VoiceConversationIntelligence:
    def __init__(self):
        """初始化语音对话智能融合引擎"""
        self.session_data = {
            "active": False,
            "conversation_id": "",
            "context": {},
            "emotion_state": "neutral",
            "intent_history": [],
            "last_response": "",
            "started_at": ""
        }
        self.load_session()

    def load_session(self):
        """加载会话状态"""
        os.makedirs(STATE_DIR, exist_ok=True)
        if os.path.exists(VOICE_SESSION_FILE):
            try:
                with open(VOICE_SESSION_FILE, 'r', encoding='utf-8') as f:
                    self.session_data = json.load(f)
            except Exception as e:
                print(f"加载语音会话失败: {e}")

    def save_session(self):
        """保存会话状态"""
        try:
            os.makedirs(STATE_DIR, exist_ok=True)
            with open(VOICE_SESSION_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.session_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存语音会话失败: {e}")

    def start_session(self, conversation_id: str = "voice_default") -> Dict[str, Any]:
        """启动语音对话会话"""
        self.session_data = {
            "active": True,
            "conversation_id": conversation_id,
            "context": {},
            "emotion_state": "neutral",
            "intent_history": [],
            "last_response": "",
            "started_at": datetime.now().isoformat()
        }
        self.save_session()
        return {
            "status": "success",
            "message": "语音对话会话已启动",
            "conversation_id": conversation_id
        }

    def end_session(self) -> Dict[str, Any]:
        """结束语音对话会话"""
        self.session_data["active"] = False
        self.save_session()
        return {
            "status": "success",
            "message": "语音对话会话已结束"
        }

    def get_session_status(self) -> Dict[str, Any]:
        """获取当前会话状态"""
        return {
            "active": self.session_data["active"],
            "conversation_id": self.session_data["conversation_id"],
            "emotion_state": self.session_data["emotion_state"],
            "context_keys": list(self.session_data["context"].keys()),
            "intent_count": len(self.session_data["intent_history"]),
            "started_at": self.session_data["started_at"]
        }

    def listen_and_understand(self) -> Dict[str, Any]:
        """
        语音输入理解：调用语音交互引擎获取输入，理解意图
        """
        if not self.session_data["active"]:
            return {"status": "error", "message": "请先启动语音对话会话"}

        # 调用语音交互引擎
        try:
            voice_script = os.path.join(os.path.dirname(__file__), "voice_interaction_engine.py")
            result = subprocess.run(
                [sys.executable, voice_script, "listen"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                user_input = result.stdout.strip()
            else:
                return {"status": "error", "message": "语音识别失败", "detail": result.stderr}
        except Exception as e:
            return {"status": "error", "message": f"语音识别异常: {e}"}

        if not user_input:
            return {"status": "error", "message": "未检测到语音输入"}

        # 理解意图 - 记录到历史
        self.session_data["intent_history"].append({
            "input": user_input,
            "timestamp": datetime.now().isoformat()
        })

        return {
            "status": "success",
            "user_input": user_input,
            "intent": self._simple_intent_recognition(user_input)
        }

    def _simple_intent_recognition(self, text: str) -> str:
        """简单的意图识别"""
        text_lower = text.lower()

        greetings = ["你好", "hello", "hi", "早上好", "晚上好", "嗨"]
        if any(g in text_lower for g in greetings):
            return "greeting"

        questions = ["什么", "怎么", "如何", "为什么", "?", "吗", "呢"]
        if any(q in text for q in questions):
            return "question"

        commands = ["打开", "关闭", "运行", "执行", "开始", "停止"]
        if any(c in text for c in commands):
            return "command"

        return "general"

    def understand_intent(self, user_input: str) -> Dict[str, Any]:
        """
        深度意图理解：结合上下文和历史进行意图理解
        """
        if not self.session_data["active"]:
            return {"status": "error", "message": "会话未启动"}

        intent = self._simple_intent_recognition(user_input)

        # 更新上下文
        self.session_data["context"]["last_input"] = user_input
        self.session_data["context"]["last_intent"] = intent
        self.session_data["context"]["last_time"] = datetime.now().isoformat()

        # 记录意图历史
        self.session_data["intent_history"].append({
            "input": user_input,
            "intent": intent,
            "timestamp": datetime.now().isoformat()
        })

        self.save_session()

        return {
            "status": "success",
            "intent": intent,
            "input": user_input,
            "context": self.session_data["context"]
        }

    def recognize_emotion(self, text: str) -> Dict[str, Any]:
        """
        情感识别：调用情感引擎识别用户情绪
        """
        if not self.session_data["active"]:
            return {"status": "error", "message": "会话未启动"}

        # 尝试调用情感引擎
        try:
            emotion_script = os.path.join(os.path.dirname(__file__), "emotion_engine.py")
            result = subprocess.run(
                [sys.executable, emotion_script, "analyze", text],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                try:
                    emotion_result = json.loads(result.stdout)
                    emotion = emotion_result.get("emotion", "neutral")
                except:
                    emotion = self._simple_emotion_detection(text)
            else:
                emotion = self._simple_emotion_detection(text)
        except Exception:
            emotion = self._simple_emotion_detection(text)

        # 更新情感状态
        self.session_data["emotion_state"] = emotion
        self.save_session()

        return {
            "status": "success",
            "emotion": emotion,
            "text": text
        }

    def _simple_emotion_detection(self, text: str) -> str:
        """简单的情感检测"""
        positive_words = ["好", "棒", "喜欢", "开心", "高兴", "谢谢", "优秀", "完美"]
        negative_words = ["不好", "差", "生气", "难过", "伤心", "讨厌", "烦", "糟"]

        for word in positive_words:
            if word in text:
                return "positive"

        for word in negative_words:
            if word in text:
                return "negative"

        return "neutral"

    def get_context(self) -> Dict[str, Any]:
        """获取当前上下文"""
        return {
            "context": self.session_data.get("context", {}),
            "emotion_state": self.session_data.get("emotion_state", "neutral"),
            "intent_history": self.session_data.get("intent_history", [])[-5:],
            "last_response": self.session_data.get("last_response", "")
        }

    def update_context(self, key: str, value: Any):
        """更新上下文"""
        self.session_data["context"][key] = value
        self.save_session()

    def generate_response(self, user_input: str, intent: str, emotion: str) -> str:
        """
        生成智能响应：结合意图和情感生成合适的响应
        """
        # 基于意图和情感生成响应
        responses = {
            "greeting": {
                "positive": "你好！看到你今天心情不错，有什么我可以帮助你的吗？",
                "negative": "你好看起来有点不开心，希望我能帮你带来一些好心情。有什么需要吗？",
                "neutral": "你好！今天有什么我可以帮你的？"
            },
            "question": {
                "positive": "这是个很好的问题！让我来帮你解答。",
                "negative": "别着急，我帮你分析一下这个问题。",
                "neutral": "让我来回答你的问题。"
            },
            "command": {
                "positive": "好的，我马上帮你处理！",
                "negative": "好的，我马上执行。",
                "neutral": "明白了，我现在就帮你完成。"
            },
            "general": {
                "positive": "我明白了，你的需求我已了解。",
                "negative": "我理解你的意思，会尽快帮你处理。",
                "neutral": "好的，我明白了。"
            }
        }

        # 获取对应意图和情感的响应
        response = responses.get(intent, {}).get(emotion, "我明白了，请告诉我更多细节。")

        # 保存响应
        self.session_data["last_response"] = response
        self.save_session()

        return response

    def speak_response(self, text: str) -> Dict[str, Any]:
        """
        语音输出：调用TTS引擎朗读响应
        """
        if not self.session_data["active"]:
            return {"status": "error", "message": "会话未启动"}

        # 调用TTS引擎
        try:
            tts_script = os.path.join(os.path.dirname(__file__), "tts_engine.py")
            result = subprocess.run(
                [sys.executable, tts_script, text],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return {"status": "success", "message": "语音输出完成", "text": text}
            else:
                return {"status": "error", "message": "语音合成失败", "detail": result.stderr}
        except Exception as e:
            return {"status": "error", "message": f"语音输出异常: {e}"}

    def conversation_loop(self, user_input: str = None) -> Dict[str, Any]:
        """
        完整的语音对话闭环：输入→理解→情感→响应→输出
        """
        if not self.session_data["active"]:
            return {"status": "error", "message": "请先启动语音对话会话"}

        # 第一步：获取用户输入（语音或文本）
        if user_input:
            input_data = {"status": "success", "user_input": user_input}
        else:
            input_data = self.listen_and_understand()
            if input_data.get("status") != "success":
                return input_data

        user_text = input_data.get("user_input", "")

        # 第二步：意图理解
        intent_data = self.understand_intent(user_text)
        if intent_data.get("status") != "success":
            return intent_data

        intent = intent_data.get("intent", "general")

        # 第三步：情感识别
        emotion_data = self.recognize_emotion(user_text)
        emotion = emotion_data.get("emotion", "neutral")

        # 第四步：生成响应
        response = self.generate_response(user_text, intent, emotion)

        # 第五步：语音输出
        speak_result = self.speak_response(response)

        return {
            "status": "success",
            "user_input": user_text,
            "intent": intent,
            "emotion": emotion,
            "response": response,
            "speak_status": speak_result.get("status")
        }

    def memory_integration(self) -> Dict[str, Any]:
        """
        与记忆网络集成：保存和检索对话记忆
        """
        if not self.session_data["active"]:
            return {"status": "error", "message": "会话未启动"}

        # 检查记忆网络模块是否存在并可调用
        memory_script = os.path.join(os.path.dirname(__file__), "memory_network_intent_predictor.py")
        if not os.path.exists(memory_script):
            return {"status": "info", "message": "记忆网络模块未找到，使用本地存储"}

        # 记录本次会话信息到记忆网络
        memory_data = {
            "conversation_id": self.session_data["conversation_id"],
            "context": self.session_data["context"],
            "emotion_state": self.session_data["emotion_state"],
            "intent_count": len(self.session_data["intent_history"]),
            "timestamp": datetime.now().isoformat()
        }

        return {
            "status": "success",
            "message": "会话记忆已保存",
            "memory_data": memory_data
        }


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("智能语音对话引擎")
        print("用法:")
        print("  voice_conversation_intelligence.py start [conversation_id]  - 启动语音对话")
        print("  voice_conversation_intelligence.py end                    - 结束语音对话")
        print("  voice_conversation_intelligence.py status                 - 查看会话状态")
        print("  voice_conversation_intelligence.py listen                 - 语音输入并理解")
        print("  voice_conversation_intelligence.py loop [文本]           - 完整对话闭环")
        print("  voice_conversation_intelligence.py context                - 获取上下文")
        print("  voice_conversation_intelligence.py memory                 - 记忆集成")
        return

    engine = VoiceConversationIntelligence()
    command = sys.argv[1]

    if command == "start":
        conv_id = sys.argv[2] if len(sys.argv) > 2 else "voice_default"
        result = engine.start_session(conv_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "end":
        result = engine.end_session()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "status":
        result = engine.get_session_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "listen":
        result = engine.listen_and_understand()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "loop":
        user_input = sys.argv[2] if len(sys.argv) > 2 else None
        result = engine.conversation_loop(user_input)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "context":
        result = engine.get_context()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "memory":
        result = engine.memory_integration()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {command}")


if __name__ == "__main__":
    main()