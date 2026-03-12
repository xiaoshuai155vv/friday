#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""统一入口：用户意图 → 执行对应脚本。用法: python do.py <意图> [参数...]"""
import sys
import os
import json
import re
import time
import datetime

# 诊断：无论 stdout 是否可见，都写文件 + stderr，便于确认是否执行到本脚本
try:
    _here = os.path.dirname(os.path.abspath(__file__))
    _debug_path = os.path.normpath(os.path.join(_here, "..", "vol_debug.txt"))
    with open(_debug_path, "w", encoding="utf-8") as _f:
        _f.write("do.py loaded argv=%r\n" % (sys.argv,))
except Exception:
    pass
try:
    sys.stderr.write("do.py stderr argv=%r\n" % (sys.argv,))
    sys.stderr.flush()
except Exception:
    pass
import subprocess

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPTS)


def _parse_compound_intent(intent):
    """解析复合指令，支持'然后''接着''再''并且''和''并且'等连接词

    返回: [(intent1, args1), (intent2, args2), ...]
    """
    # 连接词模式
    connectors = [
        r'\s+然后\s+',
        r'\s+接着\s+',
        r'\s+再\s+',
        r'\s+并且\s+',
        r'\s+和\s+',
        r'\s+并且\s+',
        r'\s+之后\s+',
        r'\s+完成后\s+',
    ]
    pattern = '|'.join(connectors)

    # 按连接词拆分
    parts = re.split(pattern, intent, flags=re.IGNORECASE)

    if len(parts) <= 1:
        return None  # 非复合指令

    result = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # 尝试分离意图和参数
        # 例如 "打开网易云音乐 参数1 参数2" -> ("打开网易云音乐", ["参数1", "参数2"])
        words = part.split()
        if words:
            intent_part = words[0]
            args = words[1:] if len(words) > 1 else []
            result.append((intent_part, args))
    return result


def main():
    if len(sys.argv) < 2:
        print("用法: python do.py <意图> [参数...]", file=sys.stderr)
        sys.exit(1)

    intent = sys.argv[1]

    # 原来的代码保持不变...

    # 智能知识关联与推理引擎
    elif intent in ("知识图谱", "知识关联", "智能知识", "关联分析", "智能推理"):
        print(f"[知识图谱] 正在处理您的请求...", file=sys.stderr)
        # 加载知识图谱模块
        from knowledge_graph import KnowledgeGraph
        kg = KnowledgeGraph()

        if "统计" in intent or "统计信息" in intent:
            # 查看图谱统计
            stats = kg.get_graph_statistics()
            print("知识图谱统计信息:")
            print("  节点总数:", stats["total_nodes"])
            print("  边总数:", stats["total_edges"])
            print("  节点分布:")
            for node_type, count in stats["node_distribution"].items():
                print("    -", node_type, ":", count)
            print("  边分布:")
            for relation, count in stats["edge_distribution"].items():
                print("    -", relation, ":", count)
        elif "推理" in intent or "推断" in intent:
            # 基于上下文进行知识推理
            context = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
            # 简单的上下文构造
            if not context:
                context = {
                    "user_id": "default_user",
                    "scene": "default_scene",
                    "time": datetime.datetime.now().isoformat()
                }
            else:
                # 尝试解析上下文
                context = {
                    "user_id": "default_user",
                    "scene": "default_scene",
                    "time": datetime.datetime.now().isoformat(),
                    "custom": context
                }

            inference = kg.infer_contextual_knowledge(context)
            print("知识推理结果:")
            print("  置信度:", f"{inference['confidence']:.2%}")
            print("  相关知识:")
            for knowledge in inference["related_knowledge"]:
                print("    -", knowledge["topic"], "(置信度:", f"{knowledge['confidence']:.2%}", ")")
            print("  建议动作:")
            for action in inference["suggested_actions"]:
                print("    -", action["action"], "(置信度:", f"{action['confidence']:.2%}", ")")
        else:
            # 默认显示图谱统计
            stats = kg.get_graph_statistics()
            print("知识图谱统计信息:")
            print("  节点总数:", stats["total_nodes"])
            print("  边总数:", stats["total_edges"])
            print("  节点分布:")
            for node_type, count in stats["node_distribution"].items():
                print("    -", node_type, ":", count)

    # 保持原有的其他代码...

if __name__ == "__main__":
    main()