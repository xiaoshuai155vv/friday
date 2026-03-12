#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能语音合成引擎 (TTS)
实现语音合成功能，让星期五能够用语音回复用户，实现完整的人机语音交互闭环
"""

import os
import sys
import time
import json
import threading
from typing import Optional, Dict, Any, Union
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Windows TTS 支持
try:
    import win32com.client
    import pythoncom
    HAS_SAPI = True
except ImportError:
    HAS_SAPI = False
    logger.warning("Windows SAPI 模块不可用，语音合成功能受限")

# pyttsx3 支持（跨平台 TTS 库）
try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False
    logger.warning("pyttsx3 库不可用，语音合成功能受限")

# gTTS 支持（Google TTS）
try:
    from gtts import gTTS
    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False
    logger.warning("gTTS 库不可用，在线语音合成功能受限")


class TTSEngine:
    """语音合成引擎类"""

    def __init__(self, voice_rate: int = 150, voice_volume: float = 1.0, voice_name: str = None):
        """
        初始化语音合成引擎

        Args:
            voice_rate: 语速，默认为 150（每分钟字数）
            voice_volume: 音量，0.0-1.0，默认为 1.0
            voice_name: 指定语音名称，None 为使用默认语音
        """
        self.voice_rate = voice_rate
        self.voice_volume = voice_volume
        self.voice_name = voice_name
        self.engine = None
        self.use_online = False  # 是否使用在线 TTS

        # 初始化 Windows SAPI 引擎
        if HAS_PYTTSX3:
            try:
                self.engine = pyttsx3.init()
                self._configure_engine()
                logger.info("pyttsx3 语音引擎初始化成功")
            except Exception as e:
                logger.warning(f"pyttsx3 初始化失败: {e}")
                self.engine = None
        elif HAS_SAPI:
            try:
                pythoncom.CoInitialize()
                self.engine = win32com.client.Dispatch("SAPI.SpVoice")
                logger.info("Windows SAPI 语音引擎初始化成功")
            except Exception as e:
                logger.warning(f"SAPI 初始化失败: {e}")
                self.engine = None
        else:
            logger.warning("无可用语音合成引擎")

    def _configure_engine(self):
        """配置语音引擎参数"""
        if self.engine and HAS_PYTTSX3:
            try:
                self.engine.setProperty('rate', self.voice_rate)
                self.engine.setProperty('volume', self.voice_volume)

                # 设置中文语音（如果可用）
                voices = self.engine.getProperty('voices')
                if voices:
                    if self.voice_name:
                        for voice in voices:
                            if self.voice_name in voice.name:
                                self.engine.setProperty('voice', voice.id)
                                break
                    else:
                        # 尝试找中文语音
                        for voice in voices:
                            if 'Chinese' in voice.name or 'Mandarin' in voice.name:
                                self.engine.setProperty('voice', voice.id)
                                logger.info(f"使用中文语音: {voice.name}")
                                break
            except Exception as e:
                logger.warning(f"配置语音引擎失败: {e}")

    def speak(self, text: str, block: bool = True) -> bool:
        """
        合成语音并播放

        Args:
            text: 要合成语音的文本
            block: 是否阻塞等待播放完成，默认为 True

        Returns:
            bool: 是否成功播放
        """
        if not text:
            logger.warning("语音文本为空")
            return False

        if not self.engine and not HAS_GTTS:
            logger.error("无可用语音合成引擎")
            return False

        try:
            # 优先使用本地引擎
            if HAS_PYTTSX3 and self.engine:
                return self._speak_pyttsx3(text, block)
            elif HAS_SAPI and self.engine:
                return self._speak_sapi(text, block)
            elif HAS_GTTS:
                return self._speak_gtts(text)
            else:
                logger.error("无支持的语音合成方式")
                return False

        except Exception as e:
            logger.error(f"语音合成失败: {e}")
            # 降级尝试 gTTS
            if HAS_GTTS and not self.use_online:
                logger.info("尝试使用 gTTS 在线语音合成...")
                return self._speak_gtts(text)
            return False

    def _speak_pyttsx3(self, text: str, block: bool) -> bool:
        """使用 pyttsx3 播放语音"""
        try:
            if block:
                self.engine.say(text)
                self.engine.runAndWait()
            else:
                # 非阻塞模式：在后台线程中播放
                thread = threading.Thread(target=self._async_speak_pyttsx3, args=(text,))
                thread.daemon = True
                thread.start()
            logger.info(f"语音播放成功: {text[:20]}...")
            return True
        except Exception as e:
            logger.error(f"pyttsx3 播放失败: {e}")
            return False

    def _async_speak_pyttsx3(self, text: str):
        """异步播放（pyttsx3）"""
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', self.voice_rate)
            engine.setProperty('volume', self.voice_volume)
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            logger.error(f"异步语音播放失败: {e}")

    def _speak_sapi(self, text: str, block: bool) -> bool:
        """使用 Windows SAPI 播放语音"""
        try:
            if block:
                self.engine.Speak(text)
            else:
                # SAPI 异步播放
                self.engine.Speak(text, 1)  # 1 = async
            logger.info(f"SAPI 语音播放成功: {text[:20]}...")
            return True
        except Exception as e:
            logger.error(f"SAPI 播放失败: {e}")
            return False

    def _speak_gtts(self, text: str) -> bool:
        """使用 Google TTS 在线合成并播放"""
        try:
            # 创建临时文件
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
                temp_file = f.name

            # 生成语音文件
            tts = gTTS(text=text, lang='zh-cn')
            tts.save(temp_file)

            # 使用系统默认播放器播放
            os.startfile(temp_file)
            logger.info(f"gTTS 语音播放成功: {text[:20]}...")

            # 延迟删除临时文件
            def cleanup():
                time.sleep(5)
                try:
                    os.remove(temp_file)
                except:
                    pass
            threading.Thread(target=cleanup, daemon=True).start()

            return True
        except Exception as e:
            logger.error(f"gTTS 播放失败: {e}")
            return False

    def set_rate(self, rate: int) -> bool:
        """
        设置语速

        Args:
            rate: 语速，每分钟字数

        Returns:
            bool: 是否设置成功
        """
        if rate < 50 or rate > 500:
            logger.warning("语速应在 50-500 之间")
            return False

        self.voice_rate = rate
        if self.engine and HAS_PYTTSX3:
            try:
                self.engine.setProperty('rate', rate)
                return True
            except Exception as e:
                logger.error(f"设置语速失败: {e}")
                return False
        return True

    def set_volume(self, volume: float) -> bool:
        """
        设置音量

        Args:
            volume: 音量，0.0-1.0

        Returns:
            bool: 是否设置成功
        """
        if volume < 0.0 or volume > 1.0:
            logger.warning("音量应在 0.0-1.0 之间")
            return False

        self.voice_volume = volume
        if self.engine and HAS_PYTTSX3:
            try:
                self.engine.setProperty('volume', volume)
                return True
            except Exception as e:
                logger.error(f"设置音量失败: {e}")
                return False
        return True

    def get_available_voices(self) -> list:
        """
        获取可用语音列表

        Returns:
            list: 可用语音列表
        """
        voices = []
        if self.engine and HAS_PYTTSX3:
            try:
                for voice in self.engine.getProperty('voices'):
                    voices.append({
                        'name': voice.name,
                        'languages': voice.languages,
                        'gender': voice.gender,
                        'id': voice.id
                    })
            except Exception as e:
                logger.error(f"获取语音列表失败: {e}")
        return voices

    def stop(self):
        """停止当前播放"""
        if self.engine and HAS_PYTTSX3:
            try:
                self.engine.stop()
            except:
                pass
        logger.info("语音播放已停止")

    def is_available(self) -> bool:
        """检查 TTS 是否可用"""
        return bool(self.engine) or HAS_GTTS


def speak_text(text: str, rate: int = 150, volume: float = 1.0) -> Dict[str, Any]:
    """
    便捷函数：合成并播放语音

    Args:
        text: 要播放的文本
        rate: 语速
        volume: 音量

    Returns:
        dict: 执行结果
    """
    engine = TTSEngine(voice_rate=rate, voice_volume=volume)
    success = engine.speak(text)
    return {
        "success": success,
        "text": text,
        "rate": rate,
        "volume": volume
    }


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description='智能语音合成引擎 (TTS)')
    parser.add_argument('text', nargs='?', help='要合成语音的文本')
    parser.add_argument('--rate', type=int, default=150, help='语速 (50-500, 默认150)')
    parser.add_argument('--volume', type=float, default=1.0, help='音量 (0.0-1.0, 默认1.0)')
    parser.add_argument('--list-voices', action='store_true', help='列出可用语音')
    parser.add_argument('--test', action='store_true', help='运行测试模式')

    args = parser.parse_args()

    # 创建 TTS 引擎
    engine = TTSEngine(voice_rate=args.rate, voice_volume=args.volume)

    if not engine.is_available():
        print("错误：无可用语音合成引擎")
        print("请安装以下任一依赖：")
        print("  - pyttsx3: pip install pyttsx3")
        print("  - gTTS: pip install gTTS")
        return 1

    # 列出可用语音
    if args.list_voices:
        voices = engine.get_available_voices()
        if voices:
            print(f"可用语音数量: {len(voices)}")
            for i, v in enumerate(voices):
                print(f"  {i+1}. {v['name']}")
        else:
            print("未找到可用语音")
        return 0

    # 测试模式
    if args.test:
        print("=" * 50)
        print("智能语音合成引擎 (TTS) 测试")
        print("=" * 50)

        # 显示可用语音
        voices = engine.get_available_voices()
        if voices:
            print(f"\n可用语音数量: {len(voices)}")
            for i, v in enumerate(voices[:5]):  # 只显示前5个
                print(f"  {i+1}. {v['name']}")

        # 测试语音播放
        print("\n测试语音播放...")
        test_texts = [
            "你好，我是星期五",
            "语音合成功能已成功运行",
            "现在你可以用语音与我交流了"
        ]

        for text in test_texts:
            print(f"  播放: {text}")
            engine.speak(text, block=True)
            time.sleep(0.5)

        print("\n测试完成！")
        return 0

    # 直接播放文本
    if args.text:
        print(f"正在合成语音: {args.text}")
        success = engine.speak(args.text, block=True)
        if success:
            print("语音合成成功")
            return 0
        else:
            print("语音合成失败")
            return 1
    else:
        # 无参数时显示帮助
        parser.print_help()
        return 0


if __name__ == "__main__":
    main()