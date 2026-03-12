#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能语音交互引擎
实现语音识别和处理功能，让星期五能够响应语音输入
"""

import os
import sys
import threading
import time
import json
from typing import Optional, Dict, Any
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    # 尝试导入 Windows 语音识别相关模块
    import win32com.client
    import pythoncom
    HAS_SAPI = True
except ImportError:
    HAS_SAPI = False
    logger.warning("Windows SAPI 模块不可用，语音识别功能受限")

# 尝试导入语音识别库
try:
    import speech_recognition as sr
    HAS_SPEECH_RECOGNIZER = True
except ImportError:
    HAS_SPEECH_RECOGNIZER = False
    logger.warning("speech_recognition 库不可用，语音识别功能受限")

class VoiceInteractionEngine:
    """语音交互引擎类"""

    def __init__(self, wake_word: str = "星期五"):
        """
        初始化语音交互引擎

        Args:
            wake_word: 唤醒词，默认为"星期五"
        """
        self.wake_word = wake_word.lower()
        self.is_listening = False
        self.recognizer = None
        self.microphone = None

        # 初始化语音识别器
        if HAS_SPEECH_RECOGNIZER:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            # 调整麦克风噪声
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)

        # 语音识别线程
        self.voice_thread = None

        logger.info(f"语音交互引擎初始化完成，唤醒词: {wake_word}")

    def is_wake_word_detected(self, text: str) -> bool:
        """
        检查是否检测到唤醒词

        Args:
            text: 识别的文本

        Returns:
            bool: 是否包含唤醒词
        """
        return self.wake_word in text.lower()

    def recognize_speech(self) -> Optional[str]:
        """
        识别语音输入

        Returns:
            str: 识别的文本，失败返回None
        """
        if not HAS_SPEECH_RECOGNIZER or not self.recognizer or not self.microphone:
            logger.error("语音识别模块不可用")
            return None

        try:
            logger.info("正在监听语音...")
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)

            # 使用Google语音识别（需要网络）
            text = self.recognizer.recognize_google(audio, language="zh-CN")
            logger.info(f"识别到语音: {text}")
            return text

        except sr.WaitTimeoutError:
            logger.warning("语音监听超时")
            return None
        except sr.UnknownValueError:
            logger.warning("无法识别语音")
            return None
        except sr.RequestError as e:
            logger.error(f"语音识别服务出错: {e}")
            return None
        except Exception as e:
            logger.error(f"语音识别发生错误: {e}")
            return None

    def start_listening(self):
        """
        开始监听语音输入
        """
        if self.is_listening:
            logger.warning("语音监听已在进行中")
            return

        self.is_listening = True
        logger.info("开始语音监听...")

        try:
            while self.is_listening:
                # 识别语音
                text = self.recognize_speech()

                if text:
                    # 检查是否包含唤醒词
                    if self.is_wake_word_detected(text):
                        # 移除唤醒词后处理命令
                        command = text.replace(self.wake_word, "").strip()
                        if command:
                            logger.info(f"检测到命令: {command}")
                            # 这里应该调用 do.py 或相应的处理函数
                            # 为演示目的，我们只是打印出来
                            print(f"[语音命令] {command}")
                            # 实际应用中这里应该调用 do.py 或处理逻辑
                        else:
                            logger.info("唤醒词已检测但无具体命令")
                    else:
                        logger.info("未检测到唤醒词，忽略语音输入")

                # 短暂延时避免CPU占用过高
                time.sleep(0.1)

        except KeyboardInterrupt:
            logger.info("语音监听被用户中断")
        except Exception as e:
            logger.error(f"语音监听过程中发生错误: {e}")
        finally:
            self.is_listening = False
            logger.info("语音监听已停止")

    def stop_listening(self):
        """
        停止监听语音输入
        """
        self.is_listening = False
        logger.info("语音监听已停止")

    def process_voice_command(self, command: str) -> Dict[str, Any]:
        """
        处理语音命令

        Args:
            command: 语音命令字符串

        Returns:
            dict: 处理结果
        """
        # 这里应该是实际的命令处理逻辑
        # 为了演示，我们返回一个简单的结果
        result = {
            "success": True,
            "command": command,
            "response": f"已收到语音命令: {command}",
            "timestamp": time.time()
        }

        logger.info(f"语音命令处理完成: {command}")
        return result

def main():
    """主函数 - 用于测试语音引擎"""
    print("启动语音交互引擎...")
    engine = VoiceInteractionEngine(wake_word="星期五")

    try:
        # 启动监听
        engine.start_listening()
    except KeyboardInterrupt:
        print("\n正在关闭语音引擎...")
        engine.stop_listening()

if __name__ == "__main__":
    main()