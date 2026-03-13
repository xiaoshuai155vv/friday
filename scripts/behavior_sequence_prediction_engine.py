"""
智能用户行为序列预测与演进引擎

让系统能够深度分析用户行为序列，预测下一步意图，并实现从被动响应到主动预判的进化。

功能：
1. 行为序列分析 - 分析用户在会话中的行为序列
2. 意图预测 - 基于历史模式预测用户下一步意图
3. 演进分析 - 分析用户意图的演变趋势
4. 主动建议 - 根据预测结果主动提供服务
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path

# 基础路径
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
STATE_DIR = PROJECT_ROOT / "runtime" / "state"
LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"

# 数据文件路径
BEHAVIOR_SEQUENCE_FILE = STATE_DIR / "behavior_sequences.json"
USER_INTENT_HISTORY_FILE = STATE_DIR / "user_intent_history.json"
PREDICTION_MODELS_FILE = STATE_DIR / "prediction_models.json"

def load_json_safe(filepath, default=None):
    """安全加载JSON文件"""
    if default is None:
        default = {}
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"加载文件失败 {filepath}: {e}")
    return default

def save_json_safe(filepath, data):
    """安全保存JSON文件"""
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存文件失败 {filepath}: {e}")
        return False

def analyze_behavior_sequence(sequence_data):
    """分析行为序列模式"""
    if not sequence_data:
        return {
            "patterns": [],
            "frequency": {},
            "avg_length": 0,
            "most_common": []
        }

    # 统计行为频率
    frequency = defaultdict(int)
    for item in sequence_data:
        action = item.get("action", "")
        if action:
            frequency[action] += 1

    # 计算序列长度
    avg_length = len(sequence_data) / max(len(sequence_data), 1)

    # 找最常见的行为
    sorted_actions = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
    most_common = [action for action, _ in sorted_actions[:5]]

    # 发现连续模式（n-gram）
    patterns = discover_ngrams(sequence_data, n=3)

    return {
        "patterns": patterns,
        "frequency": dict(frequency),
        "avg_length": avg_length,
        "most_common": most_common
    }

def discover_ngrams(sequence_data, n=3):
    """发现N-gram模式"""
    if len(sequence_data) < n:
        return []

    ngrams = defaultdict(int)
    for i in range(len(sequence_data) - n + 1):
        ngram = tuple(item.get("action", "") for item in sequence_data[i:i+n])
        if all(ngram):
            ngrams[ngram] += 1

    # 返回出现频率较高的模式
    return [{"pattern": list(k), "count": v} for k, v in sorted(ngrams.items(), key=lambda x: x[1], reverse=True) if v >= 2]

def predict_next_intent(user_id, current_sequence=None):
    """预测用户下一步意图"""
    # 加载历史数据
    behavior_data = load_json_safe(BEHAVIOR_SEQUENCE_FILE)
    user_history = behavior_data.get(user_id, {})

    predictions = []

    # 基于历史频率预测
    if user_history:
        all_actions = []
        for seq in user_history.get("sequences", []):
            all_actions.extend(seq)

        frequency = defaultdict(int)
        for action in all_actions:
            frequency[action] += 1

        if frequency:
            sorted_actions = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
            predictions.append({
                "type": "frequency_based",
                "predictions": [{"action": a, "confidence": c/max(sum(frequency.values()),1)} for a, c in sorted_actions[:3]]
            })

    # 基于当前序列预测
    if current_sequence and len(current_sequence) >= 2:
        # 最近2个行为预测下一个
        recent = current_sequence[-2:]
        behavior_data = load_json_safe(BEHAVIOR_SEQUENCE_FILE)
        user_data = behavior_data.get(user_id, {})

        for seq in user_data.get("sequences", []):
            for i in range(len(seq) - 1):
                if i + 2 <= len(seq):
                    # 检查是否匹配最近的行为序列
                    if len(seq) >= 2 and tuple(seq[i:i+2].get("action", "") for i in range(len(seq)-1)):
                        pass

        # 简单预测：当前序列的下一个最可能是之前见过最频繁的
        if predictions and current_sequence:
            last_action = current_sequence[-1].get("action", "")
            # 查找在 last_action 之后最常出现的行为
            transitions = defaultdict(lambda: defaultdict(int))
            for seq in user_data.get("sequences", []):
                for i in range(len(seq) - 1):
                    curr = seq[i].get("action", "")
                    next_act = seq[i+1].get("action", "")
                    if curr and next_act:
                        transitions[curr][next_act] += 1

            if last_action in transitions:
                next_freq = transitions[last_action]
                total = sum(next_freq.values())
                sorted_next = sorted(next_freq.items(), key=lambda x: x[1], reverse=True)
                predictions.append({
                    "type": "transition_based",
                    "given": last_action,
                    "predictions": [{"action": a, "confidence": c/total} for a, c in sorted_next[:3]]
                })

    return predictions

def analyze_intent_evolution(user_id):
    """分析用户意图演变"""
    history_file = load_json_safe(USER_INTENT_HISTORY_FILE)
    user_history = history_file.get(user_id, {})

    if not user_history:
        return {"status": "no_history", "evolution": []}

    # 按时间分析意图变化
    timeline = sorted(user_history.get("intents", []), key=lambda x: x.get("timestamp", ""))

    if not timeline:
        return {"status": "no_data", "evolution": []}

    # 分析意图类型的变化趋势
    intent_types = defaultdict(list)
    for item in timeline:
        intent = item.get("intent", "")
        timestamp = item.get("timestamp", "")
        if intent and timestamp:
            intent_types[intent].append(timestamp)

    # 找出最频繁的意图及时间分布
    evolution = []
    for intent, times in intent_types.items():
        evolution.append({
            "intent": intent,
            "occurrences": len(times),
            "first_seen": min(times) if times else None,
            "last_seen": max(times) if times else None,
            "trend": "increasing" if len(times) > 3 else "stable"
        })

    evolution.sort(key=lambda x: x["occurrences"], reverse=True)

    return {
        "status": "analyzed",
        "evolution": evolution[:10],
        "total_intents": len(timeline)
    }

def record_behavior(user_id, action, metadata=None):
    """记录用户行为"""
    behavior_data = load_json_safe(BEHAVIOR_SEQUENCE_FILE)

    if user_id not in behavior_data:
        behavior_data[user_id] = {"sequences": [], "last_update": None}

    user_data = behavior_data[user_id]

    # 添加到当前序列
    if "current_sequence" not in user_data:
        user_data["current_sequence"] = []

    user_data["current_sequence"].append({
        "action": action,
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata or {}
    })

    # 限制序列长度
    if len(user_data["current_sequence"]) > 50:
        # 保存到历史并开始新序列
        if user_data["current_sequence"]:
            user_data["sequences"].append(user_data["current_sequence"][-20:])
        user_data["current_sequence"] = user_data["current_sequence"][-10:]

    user_data["last_update"] = datetime.now().isoformat()

    save_json_safe(BEHAVIOR_SEQUENCE_FILE, behavior_data)
    return True

def get_proactive_suggestions(user_id):
    """根据预测结果主动提供建议"""
    predictions = predict_next_intent(user_id)
    evolution = analyze_intent_evolution(user_id)

    suggestions = []

    # 基于预测提供建议
    if predictions:
        for pred in predictions:
            if pred.get("type") == "frequency_based":
                top_actions = pred.get("predictions", [])
                if top_actions and top_actions[0].get("confidence", 0) > 0.3:
                    suggestions.append({
                        "type": "predicted_action",
                        "action": top_actions[0].get("action"),
                        "confidence": top_actions[0].get("confidence"),
                        "message": f"根据您的使用习惯，您可能想要：{top_actions[0].get('action')}"
                    })

    # 基于演进趋势提供建议
    if evolution.get("evolution"):
        for item in evolution["evolution"][:2]:
            if item.get("trend") == "increasing":
                suggestions.append({
                    "type": "trend_insight",
                    "intent": item.get("intent"),
                    "message": f"您最近更频繁地使用「{item.get('intent')}」功能"
                })

    return suggestions

def get_status(user_id="default"):
    """获取引擎状态"""
    behavior_data = load_json_safe(BEHAVIOR_SEQUENCE_FILE)
    user_data = behavior_data.get(user_id, {})

    seq_count = len(user_data.get("sequences", []))
    current_len = len(user_data.get("current_sequence", []))

    return {
        "engine": "行为序列预测引擎",
        "status": "running",
        "user_id": user_id,
        "total_sequences": seq_count,
        "current_sequence_length": current_len,
        "last_update": user_data.get("last_update")
    }

# CLI 接口
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法:")
        print("  python behavior_sequence_prediction_engine.py status [user_id]")
        print("  python behavior_sequence_prediction_engine.py record <user_id> <action>")
        print("  python behavior_sequence_prediction_engine.py predict [user_id]")
        print("  python behavior_sequence_prediction_engine.py evolve [user_id]")
        print("  python behavior_sequence_prediction_engine.py suggest [user_id]")
        sys.exit(1)

    command = sys.argv[1]
    user_id = sys.argv[2] if len(sys.argv) > 2 else "default"

    if command == "status":
        result = get_status(user_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "record":
        if len(sys.argv) < 4:
            print("用法: record <user_id> <action>")
            sys.exit(1)
        action = sys.argv[3]
        metadata = None
        if len(sys.argv) > 4:
            try:
                metadata = json.loads(sys.argv[4])
            except:
                pass
        record_behavior(user_id, action, metadata)
        print(f"已记录: user={user_id}, action={action}")

    elif command == "predict":
        result = predict_next_intent(user_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "evolve":
        result = analyze_intent_evolution(user_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "suggest":
        result = get_proactive_suggestions(user_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {command}")
        sys.exit(1)