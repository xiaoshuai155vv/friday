#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能跨模态深度融合引擎
将视觉、语音、文本等多种模态能力更深层次融合，实现真正的跨模态理解和协作
"""

import json
import os
import sys
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional

# 存储路径
STATE_DIR = os.path.join(os.path.dirname(__file__), "..", "runtime", "state")
CROSS_MODAL_SESSION_FILE = os.path.join(STATE_DIR, "cross_modal_session.json")

class CrossModalFusionEngine:
    def __init__(self):
        """初始化跨模态深度融合引擎"""
        self.session_data = {
            "active": False,
            "session_id": "",
            "context": {},
            "input_history": [],
            "fusion_results": [],
            "started_at": ""
        }
        self.load_session()

    def load_session(self):
        """加载会话状态"""
        os.makedirs(STATE_DIR, exist_ok=True)
        if os.path.exists(CROSS_MODAL_SESSION_FILE):
            try:
                with open(CROSS_MODAL_SESSION_FILE, 'r', encoding='utf-8') as f:
                    self.session_data = json.load(f)
            except Exception as e:
                print(f"加载跨模态会话失败: {e}")

    def save_session(self):
        """保存会话状态"""
        try:
            os.makedirs(STATE_DIR, exist_ok=True)
            with open(CROSS_MODAL_SESSION_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.session_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存跨模态会话失败: {e}")

    def start_session(self, session_id: str = "cross_modal_default") -> Dict[str, Any]:
        """启动跨模态融合会话"""
        self.session_data = {
            "active": True,
            "session_id": session_id,
            "context": {},
            "input_history": [],
            "fusion_results": [],
            "started_at": datetime.now().isoformat()
        }
        self.save_session()
        return {
            "status": "success",
            "message": "跨模态融合会话已启动",
            "session_id": session_id
        }

    def end_session(self) -> Dict[str, Any]:
        """结束跨模态融合会话"""
        self.session_data["active"] = False
        self.save_session()
        return {
            "status": "success",
            "message": "跨模态融合会话已结束"
        }

    def get_session_status(self) -> Dict[str, Any]:
        """获取当前会话状态"""
        return {
            "active": self.session_data["active"],
            "session_id": self.session_data["session_id"],
            "context_keys": list(self.session_data["context"].keys()),
            "input_count": len(self.session_data["input_history"]),
            "fusion_count": len(self.session_data["fusion_results"]),
            "started_at": self.session_data["started_at"]
        }

    def capture_visual(self) -> Dict[str, Any]:
        """
        捕获视觉输入：截取屏幕
        """
        if not self.session_data["active"]:
            return {"status": "error", "message": "请先启动跨模态融合会话"}

        try:
            screenshot_script = os.path.join(os.path.dirname(__file__), "screenshot_tool.py")
            result = subprocess.run(
                [sys.executable, screenshot_script],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # 解析输出获取截图路径
                try:
                    output = json.loads(result.stdout)
                    image_path = output.get("image_path", "")
                except:
                    image_path = result.stdout.strip()

                # 记录输入历史
                self.session_data["input_history"].append({
                    "modality": "visual",
                    "timestamp": datetime.now().isoformat(),
                    "image_path": image_path
                })
                self.save_session()

                return {
                    "status": "success",
                    "modality": "visual",
                    "image_path": image_path,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"status": "error", "message": "截图失败", "detail": result.stderr}
        except Exception as e:
            return {"status": "error", "message": f"视觉捕获异常: {e}"}

    def understand_visual(self, image_path: str = None) -> Dict[str, Any]:
        """
        理解视觉输入：调用vision_proxy分析图像
        """
        if not self.session_data["active"]:
            return {"status": "error", "message": "请先启动跨模态融合会话"}

        if not image_path:
            # 如果没有指定图像，先截取屏幕
            capture_result = self.capture_visual()
            if capture_result.get("status") != "success":
                return capture_result
            image_path = capture_result.get("image_path", "")

        if not image_path:
            return {"status": "error", "message": "没有可分析的图像"}

        try:
            vision_script = os.path.join(os.path.dirname(__file__), "vision_proxy.py")
            result = subprocess.run(
                [sys.executable, vision_script, image_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                vision_description = result.stdout.strip()

                # 记录融合结果
                self.session_data["fusion_results"].append({
                    "type": "visual_understanding",
                    "input": image_path,
                    "output": vision_description,
                    "timestamp": datetime.now().isoformat()
                })
                self.save_session()

                return {
                    "status": "success",
                    "modality": "visual",
                    "vision_description": vision_description,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"status": "error", "message": "视觉理解失败", "detail": result.stderr}
        except Exception as e:
            return {"status": "error", "message": f"视觉理解异常: {e}"}

    def capture_audio(self) -> Dict[str, Any]:
        """
        捕获语音输入：调用语音交互引擎
        """
        if not self.session_data["active"]:
            return {"status": "error", "message": "请先启动跨模态融合会话"}

        try:
            voice_script = os.path.join(os.path.dirname(__file__), "voice_interaction_engine.py")
            result = subprocess.run(
                [sys.executable, voice_script, "listen"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                audio_text = result.stdout.strip()

                # 记录输入历史
                self.session_data["input_history"].append({
                    "modality": "audio",
                    "timestamp": datetime.now().isoformat(),
                    "text": audio_text
                })
                self.save_session()

                return {
                    "status": "success",
                    "modality": "audio",
                    "text": audio_text,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"status": "error", "message": "语音识别失败", "detail": result.stderr}
        except Exception as e:
            return {"status": "error", "message": f"语音捕获异常: {e}"}

    def text_input(self, text: str) -> Dict[str, Any]:
        """
        文本输入
        """
        if not self.session_data["active"]:
            return {"status": "error", "message": "请先启动跨模态融合会话"}

        if not text:
            return {"status": "error", "message": "文本不能为空"}

        # 记录输入历史
        self.session_data["input_history"].append({
            "modality": "text",
            "timestamp": datetime.now().isoformat(),
            "text": text
        })
        self.save_session()

        return {
            "status": "success",
            "modality": "text",
            "text": text,
            "timestamp": datetime.now().isoformat()
        }

    def fuse_modalities(self, modalities: List[str]) -> Dict[str, Any]:
        """
        多模态融合：综合多种输入模态进行理解和分析
        modalities: 要融合的模态列表 ["visual", "audio", "text"]
        """
        if not self.session_data["active"]:
            return {"status": "error", "message": "请先启动跨模态融合会话"}

        fusion_data = {
            "modalities": modalities,
            "inputs": {},
            "fusion_insight": "",
            "timestamp": datetime.now().isoformat()
        }

        # 收集各模态输入
        for modality in modalities:
            if modality == "visual":
                result = self.capture_visual()
                if result.get("status") == "success":
                    # 理解视觉内容
                    vision_result = self.understand_visual(result.get("image_path", ""))
                    fusion_data["inputs"]["visual"] = vision_result.get("vision_description", "无法理解视觉")

            elif modality == "audio":
                result = self.capture_audio()
                if result.get("status") == "success":
                    fusion_data["inputs"]["audio"] = result.get("text", "")

            elif modality == "text":
                # 文本需要从上下文获取
                last_text = None
                for item in reversed(self.session_data["input_history"]):
                    if item.get("modality") == "text":
                        last_text = item.get("text", "")
                        break
                fusion_data["inputs"]["text"] = last_text

        # 生成融合洞察
        fusion_data["fusion_insight"] = self._generate_fusion_insight(fusion_data["inputs"])

        # 记录融合结果
        self.session_data["fusion_results"].append({
            "type": "multi_modal_fusion",
            "modalities": modalities,
            "inputs": fusion_data["inputs"],
            "insight": fusion_data["fusion_insight"],
            "timestamp": datetime.now().isoformat()
        })
        self.save_session()

        return {
            "status": "success",
            "fusion_data": fusion_data
        }

    def _generate_fusion_insight(self, inputs: Dict[str, str]) -> str:
        """生成跨模态融合洞察"""
        insights = []

        if "visual" in inputs and inputs["visual"]:
            insights.append(f"视觉内容: {inputs['visual'][:100]}")

        if "audio" in inputs and inputs["audio"]:
            insights.append(f"语音输入: {inputs['audio']}")

        if "text" in inputs and inputs["text"]:
            insights.append(f"文本输入: {inputs['text']}")

        if not insights:
            return "未检测到有效输入"

        # 生成综合理解
        insight_text = "；".join(insights)
        return insight_text

    def vision_to_speech(self, question: str = None) -> Dict[str, Any]:
        """
        视觉到语音的闭环：看图后理解并语音回答
        """
        if not self.session_data["active"]:
            return {"status": "error", "message": "请先启动跨模态融合会话"}

        # 1. 捕获并理解视觉
        visual_result = self.understand_visual()
        if visual_result.get("status") != "success":
            return visual_result

        vision_description = visual_result.get("vision_description", "")

        # 2. 如果有额外问题，结合问题理解
        response_text = vision_description
        if question:
            response_text = f"你问的问题是：{question}。我看到的画面是：{vision_description}"

        # 3. 语音输出
        try:
            tts_script = os.path.join(os.path.dirname(__file__), "tts_engine.py")
            result = subprocess.run(
                [sys.executable, tts_script, response_text],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return {
                    "status": "success",
                    "vision_description": vision_description,
                    "response": response_text,
                    "speech_status": "success"
                }
            else:
                return {
                    "status": "success",
                    "vision_description": vision_description,
                    "response": response_text,
                    "speech_status": "failed"
                }
        except Exception as e:
            return {
                "status": "success",
                "vision_description": vision_description,
                "response": response_text,
                "speech_error": str(e)
            }

    def speech_to_action(self, command: str = None) -> Dict[str, Any]:
        """
        语音到行动的闭环：语音输入后执行操作并反馈
        """
        if not self.session_data["active"]:
            return {"status": "error", "message": "请先启动跨模态融合会话"}

        # 1. 获取语音输入
        if not command:
            audio_result = self.capture_audio()
            if audio_result.get("status") != "success":
                return audio_result
            command = audio_result.get("text", "")

        if not command:
            return {"status": "error", "message": "没有获取到有效指令"}

        # 2. 解析命令意图（简单实现）
        action_result = self._parse_and_execute_command(command)

        # 3. 语音反馈
        feedback = action_result.get("message", "命令执行完成")
        try:
            tts_script = os.path.join(os.path.dirname(__file__), "tts_engine.py")
            subprocess.run(
                [sys.executable, tts_script, feedback],
                capture_output=True,
                text=True,
                timeout=30
            )
        except:
            pass

        return action_result

    def _parse_and_execute_command(self, command: str) -> Dict[str, Any]:
        """解析并执行简单命令"""
        command_lower = command.lower()

        # 简单命令解析
        if "打开" in command or "启动" in command:
            # 提取应用名称
            app_name = command.replace("打开", "").replace("启动", "").strip()
            if app_name:
                try:
                    # 使用 do.py 打开应用
                    do_script = os.path.join(os.path.dirname(__file__), "do.py")
                    result = subprocess.run(
                        [sys.executable, do_script, f"打开{app_name}"],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    return {
                        "status": "success",
                        "command": command,
                        "action": f"打开{app_name}",
                        "message": f"已打开{app_name}"
                    }
                except Exception as e:
                    return {
                        "status": "error",
                        "command": command,
                        "message": f"执行失败: {e}"
                    }

        if "截图" in command:
            result = self.capture_visual()
            if result.get("status") == "success":
                return {
                    "status": "success",
                    "command": command,
                    "action": "screenshot",
                    "message": "截图已完成"
                }

        # 默认返回理解到的命令
        return {
            "status": "success",
            "command": command,
            "message": f"已理解命令: {command}"
        }

    def get_context(self) -> Dict[str, Any]:
        """获取当前上下文"""
        return {
            "context": self.session_data.get("context", {}),
            "input_history": self.session_data.get("input_history", [])[-10:],
            "fusion_results": self.session_data.get("fusion_results", [])[-5:]
        }

    def get_capabilities(self) -> Dict[str, Any]:
        """获取引擎能力"""
        return {
            "name": "跨模态深度融合引擎",
            "version": "1.0.0",
            "modality_support": ["visual", "audio", "text"],
            "capabilities": [
                "capture_visual: 捕获屏幕截图",
                "understand_visual: 理解视觉内容",
                "capture_audio: 捕获语音输入",
                "text_input: 文本输入",
                "fuse_modalities: 多模态融合分析",
                "vision_to_speech: 看图后语音回答",
                "speech_to_action: 语音命令执行"
            ],
            "integration": [
                "vision_proxy: 视觉理解",
                "voice_interaction_engine: 语音输入",
                "tts_engine: 语音输出",
                "do.py: 执行操作"
            ]
        }


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("跨模态深度融合引擎")
        print("用法:")
        print("  cross_modal_fusion_engine.py start [session_id]     - 启动会话")
        print("  cross_modal_fusion_engine.py end                    - 结束会话")
        print("  cross_modal_fusion_engine.py status                 - 查看状态")
        print("  cross_modal_fusion_engine.py capture                - 捕获视觉")
        print("  cross_modal_fusion_engine.py understand             - 理解视觉")
        print("  cross_modal_fusion_engine.py audio                  - 捕获语音")
        print("  cross_modal_fusion_engine.py text <文本>            - 文本输入")
        print("  cross_modal_fusion_engine.py fuse <模态列表>        - 多模态融合")
        print("  cross_modal_fusion_engine.py vision_speech [问题]   - 看图说话")
        print("  cross_modal_fusion_engine.py speech_action [命令]   - 语音执行")
        print("  cross_modal_fusion_engine.py capabilities            - 查看能力")
        print("  cross_modal_fusion_engine.py context                 - 获取上下文")
        return

    engine = CrossModalFusionEngine()
    command = sys.argv[1]

    if command == "start":
        session_id = sys.argv[2] if len(sys.argv) > 2 else "cross_modal_default"
        result = engine.start_session(session_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "end":
        result = engine.end_session()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "status":
        result = engine.get_session_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "capture":
        result = engine.capture_visual()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "understand":
        result = engine.understand_visual()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "audio":
        result = engine.capture_audio()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "text":
        if len(sys.argv) > 2:
            text = sys.argv[2]
            result = engine.text_input(text)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("请提供文本内容")

    elif command == "fuse":
        if len(sys.argv) > 2:
            modalities = sys.argv[2].split(",")
            result = engine.fuse_modalities(modalities)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("请提供模态列表，如: visual,audio,text")

    elif command == "vision_speech":
        question = sys.argv[2] if len(sys.argv) > 2 else None
        result = engine.vision_to_speech(question)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "speech_action":
        command_text = sys.argv[2] if len(sys.argv) > 2 else None
        result = engine.speech_to_action(command_text)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "capabilities":
        result = engine.get_capabilities()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "context":
        result = engine.get_context()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {command}")


if __name__ == "__main__":
    main()