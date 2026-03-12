"""
智能对话管理引擎
让系统能够进行更自然的多轮对话和上下文记忆，实现真正拟人化的对话体验
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

# 对话历史存储路径
CONVERSATION_HISTORY_FILE = "runtime/state/conversation_history.json"

class ConversationManager:
    def __init__(self):
        """初始化对话管理器"""
        self.conversations = {}
        self.load_history()

    def load_history(self):
        """从文件加载对话历史"""
        if os.path.exists(CONVERSATION_HISTORY_FILE):
            try:
                with open(CONVERSATION_HISTORY_FILE, 'r', encoding='utf-8') as f:
                    self.conversations = json.load(f)
            except Exception as e:
                print(f"加载对话历史失败: {e}")
                self.conversations = {}

    def save_history(self):
        """保存对话历史到文件"""
        try:
            os.makedirs(os.path.dirname(CONVERSATION_HISTORY_FILE), exist_ok=True)
            with open(CONVERSATION_HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.conversations, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存对话历史失败: {e}")

    def start_conversation(self, conversation_id: str):
        """开始一个新的对话"""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = {
                "id": conversation_id,
                "messages": [],
                "started_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
            self.save_history()
            return True
        return False

    def add_message(self, conversation_id: str, role: str, content: str, metadata: Dict[str, Any] = None):
        """添加一条消息到对话中"""
        if conversation_id not in self.conversations:
            self.start_conversation(conversation_id)

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }

        if metadata:
            message["metadata"] = metadata

        self.conversations[conversation_id]["messages"].append(message)
        self.conversations[conversation_id]["last_updated"] = datetime.now().isoformat()
        self.save_history()

    def get_conversation_history(self, conversation_id: str, limit: int = None) -> List[Dict]:
        """获取对话历史记录"""
        if conversation_id not in self.conversations:
            return []

        history = self.conversations[conversation_id]["messages"]
        if limit:
            history = history[-limit:]
        return history

    def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """获取对话摘要"""
        if conversation_id not in self.conversations:
            return {}

        conv = self.conversations[conversation_id]
        return {
            "id": conv["id"],
            "message_count": len(conv["messages"]),
            "started_at": conv["started_at"],
            "last_updated": conv["last_updated"]
        }

    def clear_conversation(self, conversation_id: str):
        """清除指定对话的历史记录"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            self.save_history()
            return True
        return False

    def get_all_conversations(self) -> List[Dict]:
        """获取所有对话的摘要信息"""
        return [
            {
                "id": conv_id,
                "message_count": len(conv["messages"]),
                "started_at": conv["started_at"],
                "last_updated": conv["last_updated"]
            }
            for conv_id, conv in self.conversations.items()
        ]

# 全局对话管理器实例
conversation_manager = ConversationManager()

def start_conversation(conversation_id: str):
    """开始新对话"""
    return conversation_manager.start_conversation(conversation_id)

def add_message(conversation_id: str, role: str, content: str, metadata: Dict[str, Any] = None):
    """添加消息到对话"""
    conversation_manager.add_message(conversation_id, role, content, metadata)

def get_conversation_history(conversation_id: str, limit: int = None):
    """获取对话历史"""
    return conversation_manager.get_conversation_history(conversation_id, limit)

def get_conversation_summary(conversation_id: str):
    """获取对话摘要"""
    return conversation_manager.get_conversation_summary(conversation_id)

def clear_conversation(conversation_id: str):
    """清除对话历史"""
    return conversation_manager.clear_conversation(conversation_id)

def get_all_conversations():
    """获取所有对话"""
    return conversation_manager.get_all_conversations()

# 示例使用方式
if __name__ == "__main__":
    # 测试对话管理功能
    conv_id = "test_conv_001"

    # 开始对话
    start_conversation(conv_id)

    # 添加消息
    add_message(conv_id, "user", "你好，我想了解系统的功能")
    add_message(conv_id, "assistant", "您好！我是星期五助手，我可以帮您管理文件、执行任务、提供信息等。有什么我可以帮助您的吗？")
    add_message(conv_id, "user", "你能帮我整理文件吗？")

    # 获取对话历史
    history = get_conversation_history(conv_id)
    print("对话历史:")
    for msg in history:
        print(f"{msg['role']}: {msg['content']}")

    # 获取对话摘要
    summary = get_conversation_summary(conv_id)
    print("\n对话摘要:", summary)