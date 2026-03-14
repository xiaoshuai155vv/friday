#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环跨引擎知识推理与智能问答引擎
在 round 446 完成的跨引擎统一知识索引与智能检索引擎基础上，进一步构建跨引擎知识推理与智能问答能力。
让系统能够基于已有知识索引回答关于进化历史、方法论、能力缺口、引擎协同等方面的问题，
实现从「知识存储检索」到「知识理解推理」的范式升级。

功能：
1. 集成 round 446 知识索引引擎的检索能力
2. 基于知识图谱的推理能力（因果推理、关联推理）
3. 自然语言问答接口（回答进化相关问题）
4. 多轮对话上下文记忆
5. 知识引用溯源（回答中引用来源）
6. 与进化驾驶舱深度集成（可视化问答入口）
7. 集成到 do.py 支持知识问答、智能问答、进化问答、问我关于等关键词触发

Version: 1.0.0
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict

# 添加 scripts 目录到路径
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

# 尝试导入知识索引引擎
try:
    from evolution_cross_engine_knowledge_index_engine import CrossEngineKnowledgeIndex
    KNOWLEDGE_INDEX_AVAILABLE = True
except ImportError:
    KNOWLEDGE_INDEX_AVAILABLE = False

# 项目目录
PROJECT_DIR = os.path.dirname(SCRIPTS_DIR)
RUNTIME_DIR = os.path.join(PROJECT_DIR, "runtime")
STATE_DIR = os.path.join(RUNTIME_DIR, "state")
LOGS_DIR = os.path.join(RUNTIME_DIR, "logs")

# 对话历史文件
DIALOGUE_HISTORY_FILE = os.path.join(STATE_DIR, "knowledge_reasoning_dialogue.json")
REASONING_CACHE_FILE = os.path.join(STATE_DIR, "knowledge_reasoning_cache.json")


def _safe_print(text: str):
    """安全打印"""
    try:
        print(text)
    except UnicodeEncodeError:
        clean_text = re.sub(r'[^\x00-\x7F]+', '', text)
        print(clean_text)


class KnowledgeReasoningEngine:
    """跨引擎知识推理与智能问答引擎"""

    def __init__(self):
        self.knowledge_index = None
        self.dialogue_history = self._load_dialogue_history()
        self.reasoning_cache = self._load_reasoning_cache()

        # 尝试初始化知识索引
        if KNOWLEDGE_INDEX_AVAILABLE:
            try:
                self.knowledge_index = CrossEngineKnowledgeIndex()
            except Exception as e:
                _safe_print(f"初始化知识索引失败: {e}")

    def _load_dialogue_history(self) -> Dict:
        """加载对话历史"""
        default = {
            'conversations': {},  # {session_id: [messages]}
            'last_session_id': None,
            'max_history_per_session': 20
        }
        try:
            if os.path.exists(DIALOGUE_HISTORY_FILE):
                with open(DIALOGUE_HISTORY_FILE, 'r', encoding='utf-8') as f:
                    default.update(json.load(f))
        except Exception as e:
            _safe_print(f"加载对话历史失败: {e}")
        return default

    def _save_dialogue_history(self):
        """保存对话历史"""
        try:
            os.makedirs(os.path.dirname(DIALOGUE_HISTORY_FILE), exist_ok=True)
            with open(DIALOGUE_HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.dialogue_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"保存对话历史失败: {e}")

    def _load_reasoning_cache(self) -> Dict:
        """加载推理缓存"""
        default = {
            'reasoning_results': {},  # {query_hash: result}
            'last_updated': None
        }
        try:
            if os.path.exists(REASONING_CACHE_FILE):
                with open(REASONING_CACHE_FILE, 'r', encoding='utf-8') as f:
                    default.update(json.load(f))
        except Exception as e:
            _safe_print(f"加载推理缓存失败: {e}")
        return default

    def _save_reasoning_cache(self):
        """保存推理缓存"""
        try:
            os.makedirs(os.path.dirname(REASONING_CACHE_FILE), exist_ok=True)
            self.reasoning_cache['last_updated'] = datetime.now().isoformat()
            # 限制缓存大小
            if len(self.reasoning_cache['reasoning_results']) > 1000:
                # 保留最近的 500 条
                items = list(self.reasoning_cache['reasoning_results'].items())
                self.reasoning_cache['reasoning_results'] = dict(items[-500:])
            with open(REASONING_CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.reasoning_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"保存推理缓存失败: {e}")

    def add_message_to_history(self, session_id: str, role: str, content: str):
        """添加消息到对话历史"""
        if session_id not in self.dialogue_history['conversations']:
            self.dialogue_history['conversations'][session_id] = []

        messages = self.dialogue_history['conversations'][session_id]
        messages.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })

        # 限制历史长度
        if len(messages) > self.dialogue_history['max_history_per_session']:
            messages.pop(0)

        self.dialogue_history['last_session_id'] = session_id
        self._save_dialogue_history()

    def get_conversation_context(self, session_id: str, max_messages: int = 10) -> List[Dict]:
        """获取对话上下文"""
        messages = self.dialogue_history['conversations'].get(session_id, [])
        return messages[-max_messages:] if max_messages > 0 else messages

    def parse_question_type(self, question: str) -> Tuple[str, List[str]]:
        """解析问题类型和关键实体"""
        question = question.strip()
        question_lower = question.lower()

        # 问题类型分类
        question_type = 'general'
        entities = []

        # 轮次相关
        if any(kw in question_lower for kw in ['round', '轮次', '第几轮', '哪一轮']):
            question_type = 'round_query'
            # 尝试提取轮次数字
            round_nums = re.findall(r'(\d+)', question)
            entities.extend([int(n) for n in round_nums if int(n) > 100])

        # 引擎相关
        if any(kw in question_lower for kw in ['引擎', 'engine', '模块', '能力']):
            question_type = 'engine_query'

        # 方法论相关
        if any(kw in question_lower for kw in ['方法论', '方法', '策略', 'approach', 'strategy']):
            question_type = 'methodology_query'

        # 知识相关
        if any(kw in question_lower for kw in ['知识', 'knowledge', '学习', '传承']):
            question_type = 'knowledge_query'

        # 健康/状态相关
        if any(kw in question_lower for kw in ['健康', '状态', 'health', 'status', '表现']):
            question_type = 'health_query'

        # 优化/改进相关
        if any(kw in question_lower for kw in ['优化', '改进', 'improve', '优化建议']):
            question_type = 'optimization_query'

        # 决策相关
        if any(kw in question_lower for kw in ['决策', 'decision', '决定', '选择']):
            question_type = 'decision_query'

        # 执行相关
        if any(kw in question_lower for kw in ['执行', 'execute', '运行', '完成']):
            question_type = 'execution_query'

        # 趋势/预测相关
        if any(kw in question_lower for kw in ['趋势', '预测', 'trend', 'future', '将来']):
            question_type = 'trend_query'

        # "怎么做"类问题
        if any(kw in question_lower for kw in ['如何', '怎么做', 'how to', '怎样', '怎么']):
            question_type = 'howto_query'

        # "是什么"类问题
        if any(kw in question_lower for kw in ['是什么', 'what is', '什么是', '定义']):
            question_type = 'whatis_query'

        # "为什么"类问题
        if any(kw in question_lower for kw in ['为什么', 'why', '原因', '为何']):
            question_type = 'why_query'

        return question_type, entities

    def reason_from_knowledge_graph(self, question: str, question_type: str) -> Dict:
        """基于知识图谱进行推理"""
        result = {
            'reasoning_steps': [],
            'relevant_items': [],
            'inferred_answer': '',
            'confidence': 0.0,
            'sources': []
        }

        if not self.knowledge_index:
            result['inferred_answer'] = "知识索引引擎未初始化，无法进行推理"
            return result

        # 根据问题类型构建查询
        if question_type == 'round_query':
            # 轮次查询
            round_nums = re.findall(r'(\d+)', question)
            for rn in round_nums:
                if int(rn) > 100:
                    items = self.knowledge_index.search_by_round(int(rn))
                    result['relevant_items'].extend(items)
                    result['reasoning_steps'].append(f"查询 Round {rn} 相关知识")

        elif question_type in ['engine_query', 'methodology_query', 'knowledge_query']:
            # 关键词搜索
            keywords = self._extract_query_keywords(question)
            for kw in keywords:
                items = self.knowledge_index.search_by_keyword(kw, max_results=15)
                result['relevant_items'].extend(items)
            result['reasoning_steps'].append(f"基于关键词搜索: {keywords}")

        elif question_type == 'health_query':
            # 健康状态查询
            items = self.knowledge_index.search_by_keyword('健康', max_results=10)
            items.extend(self.knowledge_index.search_by_keyword('自愈', max_results=10))
            result['relevant_items'].extend(items)
            result['reasoning_steps'].append("查询健康与自愈相关知识")

        elif question_type == 'optimization_query':
            # 优化相关
            items = self.knowledge_index.search_by_keyword('优化', max_results=15)
            result['relevant_items'].extend(items)
            result['reasoning_steps'].append("查询优化相关知识")

        elif question_type == 'execution_query':
            # 执行相关
            items = self.knowledge_index.search_by_keyword('执行', max_results=15)
            result['relevant_items'].extend(items)
            result['reasoning_steps'].append("查询执行相关知识")

        else:
            # 通用搜索
            keywords = self._extract_query_keywords(question)
            for kw in keywords[:3]:  # 限制搜索词数量
                items = self.knowledge_index.search_by_keyword(kw, max_results=10)
                result['relevant_items'].extend(items)
            result['reasoning_steps'].append(f"通用搜索: {keywords}")

        # 去重
        seen = set()
        unique_items = []
        for item in result['relevant_items']:
            if item.get('id') not in seen:
                seen.add(item.get('id'))
                unique_items.append(item)
        result['relevant_items'] = unique_items[:20]  # 限制数量

        # 计算置信度
        if result['relevant_items']:
            result['confidence'] = min(0.9, 0.3 + 0.1 * len(result['relevant_items']))

        # 生成引用来源
        for item in result['relevant_items'][:5]:
            result['sources'].append({
                'round': item.get('round', 'N/A'),
                'title': item.get('title', 'Unknown')[:60],
                'categories': item.get('categories', [])
            })

        return result

    def _extract_query_keywords(self, question: str) -> List[str]:
        """从问题中提取查询关键词"""
        # 移除常见停用词
        stop_words = {'什么', '怎么', '如何', '为什么', '哪个', '哪些', '是否', '有没有',
                      'the', 'a', 'an', 'is', 'are', 'was', 'were', 'what', 'how', 'why',
                      'can', 'could', 'should', 'would', 'do', 'does', 'did', 'to', 'of',
                      'in', 'on', 'at', 'by', 'for', 'with', 'about', '请', '帮我', '告诉我'}

        # 提取中英文词
        words = re.findall(r'[\u4e00-\u9fa5a-zA-Z0-9]{2,}', question)
        keywords = [w for w in words if w.lower() not in stop_words and len(w) >= 2]

        # 返回有意义的关键词
        return keywords[:5]

    def generate_answer(self, question: str, reasoning_result: Dict, question_type: str) -> str:
        """基于推理结果生成答案"""
        relevant_items = reasoning_result.get('relevant_items', [])
        confidence = reasoning_result.get('confidence', 0.0)

        if not relevant_items:
            return "抱歉，我在当前知识库中没有找到与您问题相关的答案。"

        # 根据问题类型生成不同风格的答案
        if question_type == 'round_query':
            return self._generate_round_answer(question, relevant_items, confidence)
        elif question_type == 'whatis_query':
            return self._generate_whatis_answer(question, relevant_items, confidence)
        elif question_type == 'howto_query':
            return self._generate_howto_answer(question, relevant_items, confidence)
        elif question_type == 'why_query':
            return self._generate_why_answer(question, relevant_items, confidence)
        else:
            return self._generate_general_answer(question, relevant_items, confidence)

    def _generate_round_answer(self, question: str, items: List[Dict], confidence: float) -> str:
        """生成轮次相关答案"""
        if not items:
            return "未找到相关轮次信息。"

        round_info = items[0]
        answer = f"根据 Round {round_info.get('round', 'N/A')} 的记录：\n\n"
        answer += f"**{round_info.get('title', 'Unknown')}**\n"
        answer += f"分类: {', '.join(round_info.get('categories', []))}\n"

        if len(items) > 1:
            answer += f"\n该轮还涉及到: {', '.join([i.get('title', '')[:30] for i in items[1:4]])}"

        return answer

    def _generate_whatis_answer(self, question: str, items: List[Dict], confidence: float) -> str:
        """生成是什么类问题的答案"""
        answer = f"关于「{question}」，根据我的知识库：\n\n"

        # 提取关键信息
        key_info = []
        for item in items[:5]:
            title = item.get('title', '')[:50]
            if title:
                key_info.append(f"• {title}")

        answer += '\n'.join(key_info[:5])

        if len(items) > 5:
            answer += f"\n\n...还有 {len(items) - 5} 条相关信息"

        return answer

    def _generate_howto_answer(self, question: str, items: List[Dict], confidence: float) -> str:
        """生成怎么做类问题的答案"""
        answer = f"关于「{question}」的实现方法：\n\n"

        # 寻找相关执行记录
        execution_items = [i for i in items if '执行' in str(i.get('categories', []))]
        if execution_items:
            answer += "**相关执行经验：**\n"
            for item in execution_items[:3]:
                answer += f"• Round {item.get('round', 'N/A')}: {item.get('title', '')[:40]}\n"
        else:
            answer += "**建议方向：**\n"
            for item in items[:5]:
                answer += f"• {item.get('title', '')[:40]}\n"

        return answer

    def _generate_why_answer(self, question: str, items: List[Dict], confidence: float) -> str:
        """生成为什么类问题的答案"""
        answer = f"关于「{question}」的原因：\n\n"

        # 寻找相关失败教训
        fail_items = [i for i in items if '失败' in str(i.get('title', '')) or '教训' in str(i.get('title', ''))]
        if fail_items:
            answer += "**相关经验教训：**\n"
            for item in fail_items[:3]:
                answer += f"• Round {item.get('round', 'N/A')}: {item.get('title', '')[:40]}\n"
        else:
            answer += "**可能的原因：**\n"
            for item in items[:5]:
                answer += f"• {item.get('title', '')[:40]}\n"

        return answer

    def _generate_general_answer(self, question: str, items: List[Dict], confidence: float) -> str:
        """生成通用答案"""
        answer = f"针对「{question}」，我找到了 {len(items)} 条相关信息：\n\n"

        # 按轮次分组显示
        for item in items[:8]:
            round_num = item.get('round', 'N/A')
            title = item.get('title', 'Unknown')[:50]
            cats = ', '.join(item.get('categories', [])[:2])
            answer += f"**Round {round_num}** - {title}\n"
            if cats:
                answer += f"  分类: {cats}\n"
            answer += "\n"

        if len(items) > 8:
            answer += f"...还有 {len(items) - 8} 条相关记录"

        return answer

    def answer_question(self, question: str, session_id: str = 'default') -> Dict:
        """回答问题"""
        # 缓存键
        cache_key = str(hash(question))[:16]

        # 检查缓存
        if cache_key in self.reasoning_cache['reasoning_results']:
            cached = self.reasoning_cache['reasoning_results'][cache_key]
            # 验证缓存不太旧（1小时内）
            cached_time = datetime.fromisoformat(cached.get('timestamp', '2000-01-01'))
            if (datetime.now() - cached_time).total_seconds() < 3600:
                # 添加对话历史
                self.add_message_to_history(session_id, 'user', question)
                self.add_message_to_history(session_id, 'assistant', cached['answer'])
                return cached

        # 解析问题类型
        question_type, entities = self.parse_question_type(question)

        # 知识图谱推理
        reasoning_result = self.reason_from_knowledge_graph(question, question_type)

        # 生成答案
        answer = self.generate_answer(question, reasoning_result, question_type)

        # 构建结果
        result = {
            'question': question,
            'question_type': question_type,
            'answer': answer,
            'confidence': reasoning_result.get('confidence', 0.0),
            'reasoning_steps': reasoning_result.get('reasoning_steps', []),
            'sources': reasoning_result.get('sources', []),
            'relevant_items_count': len(reasoning_result.get('relevant_items', [])),
            'timestamp': datetime.now().isoformat()
        }

        # 缓存结果
        self.reasoning_cache['reasoning_results'][cache_key] = result
        self._save_reasoning_cache()

        # 添加到对话历史
        self.add_message_to_history(session_id, 'user', question)
        self.add_message_to_history(session_id, 'assistant', answer)

        return result

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        stats = {
            'dialogue_sessions': len(self.dialogue_history['conversations']),
            'total_messages': sum(len(msgs) for msgs in self.dialogue_history['conversations'].values()),
            'cached_queries': len(self.reasoning_cache['reasoning_results']),
            'knowledge_index_available': KNOWLEDGE_INDEX_AVAILABLE,
            'last_dialogue_update': self.dialogue_history.get('last_session_id'),
            'cache_last_updated': self.reasoning_cache.get('last_updated')
        }

        if self.knowledge_index:
            index_stats = self.knowledge_index.get_statistics()
            stats['knowledge_index_stats'] = index_stats

        return stats


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='跨引擎知识推理与智能问答引擎')
    parser.add_argument('--ask', type=str, help='提问')
    parser.add_argument('--session', type=str, default='default', help='会话ID')
    parser.add_argument('--stats', action='store_true', help='获取统计信息')
    parser.add_argument('--history', type=str, help='查看会话历史')
    parser.add_argument('--clear-cache', action='store_true', help='清空推理缓存')
    parser.add_argument('--clear-history', action='store_true', help='清空对话历史')

    args = parser.parse_args()

    engine = KnowledgeReasoningEngine()

    if args.ask:
        result = engine.answer_question(args.ask, args.session)
        _safe_print(f"\n问题: {result['question']}")
        _safe_print(f"\n答案: {result['answer']}")
        _safe_print(f"\n置信度: {result['confidence']:.2f}")
        _safe_print(f"相关条目: {result['relevant_items_count']}")

        if result['sources']:
            _safe_print("\n参考来源:")
            for src in result['sources'][:3]:
                _safe_print(f"  Round {src['round']}: {src['title']}")

    elif args.stats:
        stats = engine.get_statistics()
        _safe_print(json.dumps(stats, ensure_ascii=False, indent=2))

    elif args.history:
        context = engine.get_conversation_context(args.history)
        _safe_print(f"会话 {args.history} 的最近 {len(context)} 条消息:")
        for msg in context:
            _safe_print(f"  [{msg['role']}] {msg['content'][:80]}")

    elif args.clear_cache:
        engine.reasoning_cache['reasoning_results'] = {}
        engine._save_reasoning_cache()
        _safe_print("推理缓存已清空")

    elif args.clear_history:
        engine.dialogue_history['conversations'] = {}
        engine._save_dialogue_history()
        _safe_print("对话历史已清空")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()