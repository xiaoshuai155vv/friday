#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""统一入口：用户意图 → 执行对应脚本。用法: python do.py <意图> [参数...]"""
import sys
import os
import json
import re
import time

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

    return result if len(result) > 1 else None


def _load_session_context():
    """加载会话上下文（增强版：支持跨会话任务上下文保持）"""
    context_path = os.path.join(PROJECT, "runtime", "state", "session_context.json")
    default_context = {
        "last_intent": None,
        "last_args": [],
        "history": [],
        # 增强字段：跨会话任务上下文
        "last_task": None,           # 上一次执行的任务类型
        "last_task_detail": None,    # 上一次任务的详细信息
        "task_progress": {},         # 任务进度 {task_id: progress}
        "pending_tasks": [],        # 待处理任务列表
        "completed_tasks": [],       # 已完成任务列表（跨会话）
        "session_id": None,          # 当前会话ID
        "previous_session_summary": None,  # 上一个会话的摘要
        "user_preferences": {},      # 用户偏好
    }
    if os.path.isfile(context_path):
        try:
            with open(context_path, "r", encoding="utf-8") as f:
                context = json.load(f)
                # 确保所有默认字段都存在
                for key, value in default_context.items():
                    if key not in context:
                        context[key] = value
                return context
        except Exception:
            pass
    # 生成新的会话ID
    import uuid
    default_context["session_id"] = str(uuid.uuid4())
    return default_context


def _save_session_context(context):
    """保存会话上下文（增强版：支持跨会话任务上下文保持）"""
    context_path = os.path.join(PROJECT, "runtime", "state", "session_context.json")
    os.makedirs(os.path.dirname(context_path), exist_ok=True)
    try:
        with open(context_path, "w", encoding="utf-8") as f:
            json.dump(context, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _generate_session_summary():
    """生成会话摘要（用于跨会话上下文保持）

    Returns:
        dict: 会话摘要信息
    """
    context = _load_session_context()
    summary = {
        "session_id": context.get("session_id"),
        "last_intent": context.get("last_intent"),
        "last_task": context.get("last_task"),
        "pending_tasks": [t.get("task_type") for t in context.get("pending_tasks", [])],
        "completed_tasks_count": len(context.get("completed_tasks", [])),
        "history_count": len(context.get("history", [])),
    }
    return summary


def get_cross_session_context():
    """获取跨会话任务上下文（供其他模块调用）

    Returns:
        dict: 包含上一个会话的任务上下文信息
    """
    context = _load_session_context()
    return {
        "last_task": context.get("last_task"),
        "last_task_detail": context.get("last_task_detail"),
        "pending_tasks": context.get("pending_tasks", []),
        "completed_tasks": context.get("completed_tasks", []),
        "previous_session_summary": context.get("previous_session_summary"),
        "user_preferences": context.get("user_preferences", {}),
    }


def _update_session_context(intent, args, task_info=None):
    """更新会话上下文（增强版：支持跨会话任务上下文）

    Args:
        intent: 意图
        args: 参数
        task_info: 可选的任务信息 dict，包含 task_type, task_detail, status 等
    """
    context = _load_session_context()
    context["last_intent"] = intent
    context["last_args"] = args
    context["history"].append({
        "intent": intent,
        "args": args,
        "timestamp": time.time()
    })
    # 保留最近10条历史
    context["history"] = context["history"][-10:]

    # 更新任务上下文
    if task_info:
        task_type = task_info.get("task_type")
        task_detail = task_info.get("task_detail")
        status = task_info.get("status", "in_progress")

        context["last_task"] = task_type
        context["last_task_detail"] = task_detail

        # 更新待处理/完成任务列表
        if status == "completed":
            # 移到已完成列表
            if task_type not in context["completed_tasks"]:
                context["completed_tasks"].append({
                    "task_type": task_type,
                    "task_detail": task_detail,
                    "completed_at": time.time()
                })
                # 保留最近20条已完成任务
                context["completed_tasks"] = context["completed_tasks"][-20:]
            # 从待处理中移除
            context["pending_tasks"] = [t for t in context["pending_tasks"]
                                        if t.get("task_type") != task_type]
        elif status == "pending":
            # 添加到待处理列表
            if not any(t.get("task_type") == task_type for t in context["pending_tasks"]):
                context["pending_tasks"].append({
                    "task_type": task_type,
                    "task_detail": task_detail,
                    "added_at": time.time()
                })

    _save_session_context(context)


def _execute_intent_recursive(intent_with_args):
    """递归执行意图（支持复合意图）

    返回: (success, message)
    """
    # 解析复合指令
    compound_intents = _parse_compound_intent(intent_with_args)

    if compound_intents:
        # 复合指令：逐个执行
        print(f"[复合指令] 检测到 {len(compound_intents)} 个子指令，将依次执行", file=sys.stderr)
        success_count = 0
        for i, (intent, args) in enumerate(compound_intents, 1):
            print(f"[复合指令] 执行 {i}/{len(compound_intents)}: {intent} {args}", file=sys.stderr)
            # 构造临时 argv 来执行
            original_argv = sys.argv
            sys.argv = [sys.argv[0], intent] + args
            try:
                # 临时设置全局 intent 用于单步执行
                result = _execute_single_intent(intent, args)
                if result:
                    success_count += 1
                else:
                    print(f"[复合指令] 子指令 '{intent}' 执行失败", file=sys.stderr)
            except SystemExit as e:
                if e.code == 0:
                    success_count += 1
                else:
                    print(f"[复合指令] 子指令 '{intent}' 退出码: {e.code}", file=sys.stderr)
            finally:
                sys.argv = original_argv
                # 每个子指令后更新上下文
                _update_session_context(intent, args)

        return success_count == len(compound_intents), f"完成 {success_count}/{len(compound_intents)} 个子指令"

    else:
        # 单个指令
        words = intent_with_args.split()
        intent = words[0]
        args = words[1:] if len(words) > 1 else []
        result = _execute_single_intent(intent, args)
        _update_session_context(intent, args)
        return result, "执行完成"


def _execute_single_intent(intent, args):
    """执行单个意图，返回 True/False"""
    # 这里只处理最常见的场景，其他的让原始 main 处理
    # 通过 subprocess 调用自身来执行
    cmd = [sys.executable, os.path.join(SCRIPTS, "do.py"), intent] + args
    result = subprocess.run(cmd, cwd=PROJECT, capture_output=True)
    return result.returncode == 0


def _auto_load_private_knowledge(intent):
    """自动加载与用户意图相关的私域知识"""
    load_knowledge_script = os.path.join(SCRIPTS, "load_private_knowledge.py")
    if not os.path.isfile(load_knowledge_script):
        sys.stderr.write("警告: 私域知识脚本不存在，跳过加载\n")
        sys.stderr.flush()
        return

    try:
        result = subprocess.run(
            [sys.executable, load_knowledge_script, "auto", intent],
            cwd=PROJECT,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.stdout:
            try:
                knowledge = json.loads(result.stdout)
                if knowledge:
                    sys.stderr.write("\n=== 私域知识已加载 ===\n")
                    for domain, data in knowledge.items():
                        sys.stderr.write(f"- {data['file']}: {len(data['content'])} 字符\n")
                    sys.stderr.flush()
                else:
                    sys.stderr.write("无匹配的私域知识\n")
                    sys.stderr.flush()
            except json.JSONDecodeError as e:
                sys.stderr.write(f"JSON 解析错误: {e}\n")
                sys.stderr.flush()
        elif result.stderr:
            sys.stderr.write(f"私域知识加载错误: {result.stderr}\n")
            sys.stderr.flush()
    except subprocess.TimeoutExpired:
        sys.stderr.write("警告: 私域知识加载超时\n")
        sys.stderr.flush()
    except Exception as e:
        sys.stderr.write(f"私域知识加载异常: {e}\n")
        sys.stderr.flush()  # 更好的错误处理，让使用者知道发生了什么

def _load_user_preferences():
    """加载用户偏好设置"""
    # 优先使用 memory 目录下的 user_preferences.json
    pref_path = os.path.join(PROJECT, "memory", "user_preferences.json")
    if os.path.isfile(pref_path):
        try:
            with open(pref_path, "r", encoding="utf-8") as f:
                prefs = json.load(f)
            if prefs:
                sys.stderr.write("\n=== 用户偏好已加载 ===\n")
                sys.stderr.write(f"偏好设置: {len(prefs.get('preferences', {}))} 项\n")
                sys.stderr.flush()
                return prefs
        except Exception as e:
            sys.stderr.write(f"加载用户偏好失败: {e}\n")
            sys.stderr.flush()

    # 回退到 load_private_knowledge
    load_knowledge_script = os.path.join(SCRIPTS, "load_private_knowledge.py")
    if not os.path.isfile(load_knowledge_script):
        sys.stderr.write("警告: 私域知识脚本不存在，跳过用户偏好加载\n")
        sys.stderr.flush()
        return {}

    try:
        result = subprocess.run(
            [sys.executable, load_knowledge_script, "get", "user_preferences"],
            cwd=PROJECT,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.stdout:
            try:
                prefs = json.loads(result.stdout)
                if prefs:
                    sys.stderr.write("\n=== 用户偏好已加载 ===\n")
                    sys.stderr.write(f"偏好设置: {len(prefs.get('preferences', {}))} 项\n")
                    sys.stderr.flush()
                    return prefs
                else:
                    sys.stderr.write("无用户偏好设置\n")
                    sys.stderr.flush()
            except json.JSONDecodeError as e:
                sys.stderr.write(f"JSON 解析错误: {e}\n")
                sys.stderr.flush()
        elif result.stderr:
            sys.stderr.write(f"用户偏好加载错误: {result.stderr}\n")
            sys.stderr.flush()
    except subprocess.TimeoutExpired:
        sys.stderr.write("警告: 用户偏好加载超时\n")
        sys.stderr.flush()
    except Exception as e:
        sys.stderr.write(f"用户偏好加载异常: {e}\n")
        sys.stderr.flush()
    return {}


def _learn_user_preference(pref_type, value):
    """记录用户偏好学习"""
    learner_script = os.path.join(SCRIPTS, "user_preference_learner.py")
    if not os.path.isfile(learner_script):
        return

    try:
        subprocess.run(
            [sys.executable, learner_script, "record", pref_type, value],
            cwd=PROJECT,
            capture_output=True,
            timeout=5,
        )
    except Exception:
        pass  # 学习失败不阻断主流程


def _get_smart_scenario_recommendations(intent, user_prefs=None):
    """智能场景推荐：根据用户意图和历史偏好推荐场景计划"""
    import json
    import glob
    import os

    plans_dir = os.path.join(PROJECT, "assets", "plans")
    recommendations = []

    if not os.path.isdir(plans_dir):
        return recommendations

    # 场景关键词到计划文件的映射（用于基于用户偏好的推荐）
    scenario_keywords = {
        "music": ["play_music.json", "listen_to_music.json"],
        "news": ["news_reader.json", "read_news.json"],
        "video": [],
        "ihaier": ["example_ihaier_send_message.json", "example_ihaier_who_contacted_me.json", "ihaier_performance_declaration.json"],
        "chat": ["example_ihaier_send_message.json", "send_to_zhouxiaoshuai.json"],
        "performance": ["ihaier_performance_declaration.json"],
        "zhihu": ["browse_zhihu.json"],
    }

    # 基于用户偏好计算推荐分数
    pref_score = 0
    if user_prefs:
        prefs = user_prefs.get("preferences", {})
        usage = user_prefs.get("usage_history", {})

        # 基于偏好计算分数
        preferred_music = prefs.get("preferred_music_player", "").lower()
        preferred_news = prefs.get("preferred_news_source", "").lower()

        # 用户偏好推荐
        if "music" in intent.lower() and preferred_music:
            pref_score += 2
        if "news" in intent.lower() and preferred_news:
            pref_score += 2
        if "ihaier" in intent.lower() or "办公" in intent:
            # 如果用户经常使用 iHaier 相关功能，提高推荐分数
            frequent_ops = usage.get("frequent_operations", [])
            if any("ihaier" in str(op).lower() for op in frequent_ops):
                pref_score += 3

    # 搜索匹配的计划
    for plan_file in glob.glob(os.path.join(plans_dir, "*.json")):
        try:
            with open(plan_file, encoding="utf-8") as f:
                plan_data = json.load(f)
                triggers = plan_data.get("triggers", [])
                intent_name = plan_data.get("intent", "")

                match_score = 0
                matched_trigger = None
                for trigger in triggers:
                    if trigger in intent or intent in trigger:
                        match_score = 10  # 精确匹配
                        matched_trigger = trigger
                        break
                    elif any(keyword in trigger.lower() for keyword in intent.lower().split()):
                        match_score = 5  # 关键词匹配
                        matched_trigger = trigger

                if match_score > 0:
                    # 添加基于用户偏好的额外分数
                    total_score = match_score + pref_score
                    recommendations.append({
                        "plan": os.path.basename(plan_file),
                        "intent": intent_name,
                        "trigger": matched_trigger,
                        "score": total_score,
                    })
        except Exception:
            pass

    # 按分数排序，返回前 5 个推荐
    recommendations.sort(key=lambda x: x["score"], reverse=True)
    return recommendations[:5]


def _get_user_preferences():
    """获取用户偏好数据用于场景推荐"""
    pref_path = os.path.join(PROJECT, "memory", "user_preferences.json")
    if os.path.isfile(pref_path):
        try:
            with open(pref_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None


def _get_foreground_based_recommendations():
    """获取基于前台窗口的推荐"""
    scene_perception_script = os.path.join(SCRIPTS, "scene_perception.py")
    if not os.path.isfile(scene_perception_script):
        return []

    try:
        result = subprocess.run(
            [sys.executable, scene_perception_script, "--output", "json"],
            cwd=PROJECT,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.stdout:
            try:
                data = json.loads(result.stdout)
                recommendations = data.get("recommendations", [])
                return recommendations
            except json.JSONDecodeError:
                pass
    except Exception:
        pass
    return []


def _launch_via_win_r(app_name):
    """Win+R 输入应用名回车，用于启动未在 do 中显式列出的应用。"""
    import time
    kbd = os.path.join(SCRIPTS, "keyboard_tool.py")
    subprocess.run([sys.executable, kbd, "keys", "91", "82"], cwd=PROJECT)  # Win+R
    time.sleep(0.5)
    subprocess.run([sys.executable, kbd, "type", app_name], cwd=PROJECT)
    time.sleep(0.3)
    subprocess.run([sys.executable, kbd, "key", "13"], cwd=PROJECT)  # Enter


# 全局变量：是否跳过复合指令检查（用于递归执行子指令时）
_SKIP_COMPOUND_CHECK = False


def _run_autonomous_decision():
    """运行自主决策模块，让系统在无用户指令时主动给出建议"""
    script_path = os.path.join(SCRIPTS, "autonomous_decision_maker.py")
    result = subprocess.run([sys.executable, script_path], cwd=PROJECT, capture_output=True, text=True)
    # 输出结果
    if result.stdout:
        print(result.stdout)
    if result.returncode != 0 and result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode


def main():
    global _SKIP_COMPOUND_CHECK

    if len(sys.argv) < 2:
        print("用法: do.py 自拍|打开摄像头|截图|已安装应用|打开网易云音乐|...|剪贴板读|电源计划|防休眠|...|run <脚本名> [参数...]", file=sys.stderr)
        sys.exit(1)

    # 检查是否请求自主决策/系统建议
    intent_with_args = " ".join(sys.argv[1:]).lower()
    autonomous_keywords = ["自主决策", "系统建议", "主动建议", "ai建议", "智能建议", "给我建议"]
    for keyword in autonomous_keywords:
        if keyword in intent_with_args:
            print(f"[自主决策] 检测到请求: {keyword}", file=sys.stderr)
            ret = _run_autonomous_decision()
            sys.exit(ret)

    # 检查是否请求自然语言自动化
    nl_automation_keywords = ["自然语言", "自然自动化", "描述任务", "帮我做", "帮我执行", "执行自然语言"]
    if any(keyword in intent_with_args for keyword in nl_automation_keywords):
        # 提取任务描述（去掉关键词）
        task_description = intent_with_args
        for kw in nl_automation_keywords:
            task_description = task_description.replace(kw, "").strip()
        if not task_description:
            task_description = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        if task_description:
            print(f"[自然语言自动化] 解析任务: {task_description}", file=sys.stderr)
            script_path = os.path.join(SCRIPTS, "nl_automation.py")
            result = subprocess.run([sys.executable, script_path, task_description], cwd=PROJECT, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            if result.returncode != 0 and result.stderr:
                print(result.stderr, file=sys.stderr)
            sys.exit(result.returncode)

    # 检查是否请求主动任务执行
    proactive_keywords = ["主动任务", "生成任务建议", "执行主动任务", "智能任务推荐"]
    for keyword in proactive_keywords:
        if keyword in " ".join(sys.argv[1:]):
            print(f"[主动任务] 检测到请求: {keyword}", file=sys.stderr)
            script_path = os.path.join(SCRIPTS, "proactive_task_executor.py")
            result = subprocess.run([sys.executable, script_path], cwd=PROJECT, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            if result.returncode != 0 and result.stderr:
                print(result.stderr, file=sys.stderr)
            sys.exit(result.returncode)

    # 检查是否请求趋势分析/预测
    import json as _json_module  # 确保 json 在局部作用域可用
    trend_keywords = ["趋势分析", "趋势预测", "执行趋势", "预测分析", "行为趋势"]
    for keyword in trend_keywords:
        if keyword in " ".join(sys.argv[1:]):
            print(f"[趋势分析] 检测到请求: {keyword}", file=sys.stderr)
            script_path = os.path.join(SCRIPTS, "trend_predictor.py")
            result = subprocess.run([sys.executable, script_path], cwd=PROJECT, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            if result.returncode != 0 and result.stderr:
                print(result.stderr, file=sys.stderr)
            # 读取并输出趋势报告
            trend_file = os.path.join(PROJECT, "runtime", "state", "trend_predictions.json")
            if os.path.exists(trend_file):
                with open(trend_file, "r", encoding="utf-8") as f:
                    trend_data = _json_module.loads(f.read())
                    print("\n=== 趋势分析报告 ===", file=sys.stderr)
                    print(f"分析日志数: {trend_data.get('total_logs', 0)}", file=sys.stderr)
                    print(f"活跃度趋势: {trend_data.get('time_series', {}).get('trend', 'unknown')}", file=sys.stderr)
                    print(f"执行成功率: {trend_data.get('success_trend', {}).get('success_rate', 0)}%", file=sys.stderr)
                    print("\n预测:", file=sys.stderr)
                    for pred in trend_data.get("predictions", []):
                        print(f"  - {pred.get('prediction', '')} ({pred.get('confidence', '')}置信度)", file=sys.stderr)
                        print(f"    {pred.get('detail', '')}", file=sys.stderr)
                    print(f"\n详细报告: {trend_file}", file=sys.stderr)
            sys.exit(0 if result.returncode == 0 else result.returncode)

    # 检查是否请求趋势可视化
    viz_keywords = ["趋势可视化", "可视化趋势", "查看趋势图表", "趋势图表", "趋势状态"]
    for keyword in viz_keywords:
        if keyword in " ".join(sys.argv[1:]):
            print(f"[趋势可视化] 检测到请求: {keyword}", file=sys.stderr)
            script_path = os.path.join(SCRIPTS, "trend_visualizer.py")
            result = subprocess.run([sys.executable, script_path], cwd=PROJECT, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            if result.returncode != 0 and result.stderr:
                print(result.stderr, file=sys.stderr)
            sys.exit(0 if result.returncode == 0 else result.returncode)

    # 检查是否请求统一系统监控仪表盘
    system_dashboard_keywords = ["系统监控仪表盘", "统一系统状态", "系统概览", "系统监控视图", "监控仪表盘", "system dashboard", "unified status", "系统全貌"]
    for keyword in system_dashboard_keywords:
        if keyword in " ".join(sys.argv[1:]):
            print(f"[统一系统监控仪表盘] 检测到请求: {keyword}", file=sys.stderr)
            script_path = os.path.join(SCRIPTS, "system_dashboard_engine.py")
            cmd = [sys.executable, script_path]
            if "json" in " ".join(sys.argv[1:]):
                cmd.append("json")
            else:
                cmd.append("summary")
            result = subprocess.run(cmd, cwd=PROJECT, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            if result.returncode != 0 and result.stderr:
                print(result.stderr, file=sys.stderr)
            sys.exit(0 if result.returncode == 0 else result.returncode)

    # 检查是否请求智能全系统洞察与预测引擎
    system_insight_keywords = ["系统洞察", "全系统洞察", "系统预测", "洞察引擎", "预测引擎", "系统分析", "system insight", "predictive insight", "跨引擎分析", "系统趋势"]
    for keyword in system_insight_keywords:
        if keyword in " ".join(sys.argv[1:]):
            print(f"[智能全系统洞察与预测引擎] 检测到请求: {keyword}", file=sys.stderr)
            script_path = os.path.join(SCRIPTS, "system_insight_engine.py")
            cmd = [sys.executable, script_path]
            # 解析子命令
            if "overview" in " ".join(sys.argv[1:]) or "概览" in " ".join(sys.argv[1:]):
                cmd.append("overview")
            elif "performance" in " ".join(sys.argv[1:]) or "性能" in " ".join(sys.argv[1:]):
                cmd.append("performance")
            elif "predictions" in " ".join(sys.argv[1:]) or "预测" in " ".join(sys.argv[1:]):
                cmd.append("predictions")
            elif "insights" in " ".join(sys.argv[1:]) or "洞察" in " ".join(sys.argv[1:]):
                cmd.append("insights")
            elif "patterns" in " ".join(sys.argv[1:]) or "模式" in " ".join(sys.argv[1:]):
                cmd.append("patterns")
            elif "json" in " ".join(sys.argv[1:]):
                cmd.append("--json")
            else:
                cmd.append("report")  # 默认输出完整报告
            result = subprocess.run(cmd, cwd=PROJECT, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            if result.returncode != 0 and result.stderr:
                print(result.stderr, file=sys.stderr)
            sys.exit(0 if result.returncode == 0 else result.returncode)

    # 检查是否请求智能跨引擎协同优化引擎
    cross_engine_optimizer_keywords = ["跨引擎协同", "协同优化", "引擎协同", "跨引擎优化", "cross engine", "coordination optimization", "engine coordination", "引擎优化"]
    for keyword in cross_engine_optimizer_keywords:
        if keyword in " ".join(sys.argv[1:]):
            print(f"[智能跨引擎协同优化引擎] 检测到请求: {keyword}", file=sys.stderr)
            script_path = os.path.join(SCRIPTS, "cross_engine_optimizer.py")
            cmd = [sys.executable, script_path]
            # 解析子命令
            if "status" in " ".join(sys.argv[1:]) or "状态" in " ".join(sys.argv[1:]):
                cmd.append("status")
            elif "analyze" in " ".join(sys.argv[1:]) or "分析" in " ".join(sys.argv[1:]):
                cmd.append("analyze")
            elif "recommend" in " ".join(sys.argv[1:]) or "建议" in " ".join(sys.argv[1:]):
                cmd.append("recommend")
            elif "execute" in " ".join(sys.argv[1:]) or "执行" in " ".join(sys.argv[1:]):
                cmd.append("execute")
                # 提取建议ID
                if "-r" in sys.argv:
                    idx = sys.argv.index("-r")
                    if idx + 1 < len(sys.argv):
                        cmd.extend(["--recommendation-id", sys.argv[idx + 1]])
                if "--auto" in sys.argv or "自动" in " ".join(sys.argv[1:]):
                    cmd.append("--auto")
            else:
                cmd.append("status")  # 默认输出状态
            result = subprocess.run(cmd, cwd=PROJECT, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            if result.returncode != 0 and result.stderr:
                print(result.stderr, file=sys.stderr)
            sys.exit(0 if result.returncode == 0 else result.returncode)

    # 检查是否请求智能服务联动中心引擎
    service_linkage_keywords = ["服务联动", "联动中心", "联动状态", "查看联动", "自动触发", "触发规则", "联动执行", "service linkage", "linkage center", "联动"]
    for keyword in service_linkage_keywords:
        if keyword in " ".join(sys.argv[1:]):
            print(f"[智能服务联动中心引擎] 检测到请求: {keyword}", file=sys.stderr)
            script_path = os.path.join(SCRIPTS, "service_linkage_center.py")
            cmd = [sys.executable, script_path]
            # 解析子命令
            if "status" in " ".join(sys.argv[1:]) or "状态" in " ".join(sys.argv[1:]):
                cmd.append("status")
            elif "history" in " ".join(sys.argv[1:]) or "历史" in " ".join(sys.argv[1:]):
                cmd.append("history")
            elif "clear" in " ".join(sys.argv[1:]) or "清空" in " ".join(sys.argv[1:]):
                cmd.append("clear")
            else:
                cmd.append("status")  # 默认输出状态
            result = subprocess.run(cmd, cwd=PROJECT, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            if result.returncode != 0 and result.stderr:
                print(result.stderr, file=sys.stderr)
            sys.exit(0 if result.returncode == 0 else result.returncode)

    # 检查是否请求状态仪表板
    dashboard_keywords = ["状态面板", "系统状态", "进化状态", "dashboard", "仪表板", "状态概览"]
    for keyword in dashboard_keywords:
        if keyword in " ".join(sys.argv[1:]):
            print(f"[状态仪表板] 检测到请求: {keyword}", file=sys.stderr)
            script_path = os.path.join(SCRIPTS, "dashboard.py")
            full_flag = "--full" if "详细" in " ".join(sys.argv[1:]) or "完整" in " ".join(sys.argv[1:]) else ""
            cmd = [full_flag] if full_flag else []
            result = subprocess.run([sys.executable, script_path] + cmd, cwd=PROJECT, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            if result.returncode != 0 and result.stderr:
                print(result.stderr, file=sys.stderr)
            sys.exit(0 if result.returncode == 0 else result.returncode)

    # 检查是否请求日志分析与智能建议
    log_analysis_keywords = ["日志分析", "执行分析", "分析日志", "智能建议", "log analyzer", "execution analysis"]
    # 自动修复关键词（触发带 --auto-fix 的分析）
    auto_fix_keywords = ["自动修复", "自动修复建议", "auto fix", "智能修复"]

    # 检测是否需要自动修复
    needs_auto_fix = any(kw in " ".join(sys.argv[1:]) for kw in auto_fix_keywords)

    for keyword in log_analysis_keywords:
        if keyword in " ".join(sys.argv[1:]):
            print(f"[日志分析] 检测到请求: {keyword}", file=sys.stderr)
            script_path = os.path.join(SCRIPTS, "execution_log_analyzer.py")
            cmd = [sys.executable, script_path]
            if needs_auto_fix:
                cmd.append("--auto-fix")
                print(f"[日志分析] 自动修复模式已启用", file=sys.stderr)
            result = subprocess.run(cmd, cwd=PROJECT, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            if result.returncode != 0 and result.stderr:
                print(result.stderr, file=sys.stderr)
            sys.exit(0 if result.returncode == 0 else result.returncode)

    # 检查是否请求健康检查守护进程
    health_daemon_keywords = {
        "健康检查守护进程": ["--start"],
        "启动健康检查": ["--start"],
        "自动健康检查": ["--start"],
        "健康检查状态": ["--status"],
        "健康检查历史": ["--history"],
        "执行健康检查": ["--once"],
        "健康报告": ["--status"],
    }
    for keyword, subcmd in health_daemon_keywords.items():
        if keyword in " ".join(sys.argv[1:]):
            print(f"[健康检查守护进程] 检测到请求: {keyword}", file=sys.stderr)
            script_path = os.path.join(SCRIPTS, "health_check_daemon.py")
            cmd = subcmd if isinstance(subcmd, list) else [subcmd]
            # 解析额外的参数如 --interval
            if "--interval" in " ".join(sys.argv[1:]):
                try:
                    idx = sys.argv.index("--interval")
                    if idx + 1 < len(sys.argv):
                        cmd.extend(["--interval", sys.argv[idx + 1]])
                except Exception:
                    pass
            result = subprocess.run([sys.executable, script_path] + cmd, cwd=PROJECT, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            if result.returncode != 0 and result.stderr:
                print(result.stderr, file=sys.stderr)
            sys.exit(0 if result.returncode == 0 else result.returncode)

    # 检查是否请求进化环（定时触发 CC 的能力，独立于悬浮球）
    evolution_keywords = {
        "提交进化环": ["evolution_loop_client", "--once", "--auto-evolution"],
        "进化环": ["evolution_loop_client", "--once", "--auto-evolution"],
        "自动进化": ["evolution_loop_client", "--once", "--auto-evolution"],
        "进化环守护": ["evolution_loop_daemon"],
        "进化环循环": ["evolution_loop_daemon"],
        "启动进化环守护": ["evolution_loop_daemon"],
    }
    for keyword, subcmd in evolution_keywords.items():
        if keyword in " ".join(sys.argv[1:]):
            script_name = subcmd[0]
            args = subcmd[1:] if len(subcmd) > 1 else []
            print(f"[进化环] 检测到请求: {keyword}", file=sys.stderr)
            script_path = os.path.join(SCRIPTS, script_name + ".py")
            # 守护进程模式：后台运行，不阻塞
            if script_name == "evolution_loop_daemon":
                kw = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if sys.platform == "win32" else {}
                subprocess.Popen([sys.executable, script_path] + args, cwd=PROJECT, **kw)
                print("进化环守护进程已后台启动，按配置间隔定时触发。", file=sys.stderr)
                sys.exit(0)
            result = subprocess.run([sys.executable, script_path] + args, cwd=PROJECT, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            if result.returncode != 0 and result.stderr:
                print(result.stderr, file=sys.stderr)
            sys.exit(0 if result.returncode == 0 else result.returncode)

    # 检查是否请求守护进程管理
    daemon_keywords = {
        "守护进程列表": ["list"],
        "守护进程状态": ["status"],
        "查看守护进程": ["status"],
        "启动守护进程": ["start"],
        "停止守护进程": ["stop"],
        "重启守护进程": ["restart"],
        "启用守护进程": ["enable"],
        "禁用守护进程": ["disable"],
    }
    for keyword, subcmd in daemon_keywords.items():
        if keyword in " ".join(sys.argv[1:]):
            # 尝试提取守护进程名称
            daemon_name = None
            argv_str = " ".join(sys.argv[1:])
            for name in ["health_check", "evolution_loop", "health_assurance", "daemon_linkage"]:
                if name in argv_str:
                    daemon_name = name
                    break
            print(f"[守护进程管理] 检测到请求: {keyword}", file=sys.stderr)
            script_path = os.path.join(SCRIPTS, "daemon_manager.py")
            cmd = [subcmd]
            if daemon_name:
                cmd.append(daemon_name)
            result = subprocess.run([sys.executable, script_path] + cmd, cwd=PROJECT, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            if result.returncode != 0 and result.stderr:
                print(result.stderr, file=sys.stderr)
            sys.exit(0 if result.returncode == 0 else result.returncode)

    # 检查是否请求守护进程间联动引擎
    linkage_keywords = ["联动", "linkage", "守护进程联动", "daemon_linkage"]
    if any(kw in " ".join(sys.argv[1:]) for kw in linkage_keywords):
        # 提取子命令
        subcmd = None
        argv_str = " ".join(sys.argv[1:])
        for cmd in ["list", "status", "add", "remove", "enable", "disable", "trigger", "run"]:
            if cmd in argv_str:
                subcmd = cmd
                break
        if subcmd is None:
            subcmd = "status"  # 默认显示状态

        # 提取参数
        cmd_args = []
        if subcmd == "add" or subcmd == "remove" or subcmd == "enable" or subcmd == "disable" or subcmd == "trigger":
            # 提取额外参数
            args = argv_str.replace(subcmd, "").strip().split()
            cmd_args = [a for a in args if a and not any(kw in a for kw in linkage_keywords)]

        print(f"[守护进程间联动] 检测到请求: {subcmd}", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "daemon_linkage_engine.py")
        cmd = [subcmd] + cmd_args
        result = subprocess.run([sys.executable, script_path] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 检查是否请求告警相关操作
    alert_keywords = {
        "告警状态": ["status"],
        "告警配置": ["config"],
        "查看告警": ["config"],
        "设置告警": ["config"],
        "告警检查": ["check"],
        "告警设置": ["config"],
        "启用告警": ["enable"],
        "关闭告警": ["disable"],
    }
    for keyword, subcmd in alert_keywords.items():
        if keyword in " ".join(sys.argv[1:]):
            print(f"[告警系统] 检测到请求: {keyword}", file=sys.stderr)
            script_path = os.path.join(SCRIPTS, "alert_system.py")
            cmd = subcmd if isinstance(subcmd, list) else [subcmd]
            result = subprocess.run([sys.executable, script_path] + cmd, cwd=PROJECT, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            if result.returncode != 0 and result.stderr:
                print(result.stderr, file=sys.stderr)
            sys.exit(0 if result.returncode == 0 else result.returncode)

    # 检查是否请求系统自动修复
    auto_fixer_keywords = {
        "系统诊断": ["diagnose"],
        "自动修复": ["fix", "all"],
        "磁盘修复": ["fix", "disk"],
        "内存修复": ["fix", "memory"],
        "进程修复": ["fix", "process"],
        "修复历史": ["history"],
        "修复状态": ["status"],
        "系统健康": ["diagnose"],
    }
    for keyword, subcmd in auto_fixer_keywords.items():
        if keyword in " ".join(sys.argv[1:]):
            print(f"[系统自动修复] 检测到请求: {keyword}", file=sys.stderr)
            script_path = os.path.join(SCRIPTS, "auto_fixer.py")
            cmd = subcmd if isinstance(subcmd, list) else [subcmd]
            # 解析额外的参数
            if "磁盘" in " ".join(sys.argv[1:]):
                cmd = ["fix", "disk"]
            elif "内存" in " ".join(sys.argv[1:]):
                cmd = ["fix", "memory"]
            elif "进程" in " ".join(sys.argv[1:]):
                cmd = ["fix", "process"]
            elif "全部" in " ".join(sys.argv[1:]) or "所有" in " ".join(sys.argv[1:]):
                cmd = ["fix", "all"]
            result = subprocess.run([sys.executable, script_path] + cmd, cwd=PROJECT, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            if result.returncode != 0 and result.stderr:
                print(result.stderr, file=sys.stderr)
            sys.exit(0 if result.returncode == 0 else result.returncode)

    # 先解析是否复合指令（除非已在递归执行中）
    if not _SKIP_COMPOUND_CHECK:
        intent_with_args = " ".join(sys.argv[1:])
        compound_intents = _parse_compound_intent(intent_with_args)

        if compound_intents:
            # 复合指令：逐个执行
            print(f"[复合指令] 检测到 {len(compound_intents)} 个子指令，将依次执行", file=sys.stderr)
            success_count = 0
            for i, (intent, args) in enumerate(compound_intents, 1):
                print(f"[复合指令] 执行 {i}/{len(compound_intents)}: {intent} {args}", file=sys.stderr)
                # 构造临时 argv 来执行
                original_argv = sys.argv
                original_skip = _SKIP_COMPOUND_CHECK
                _SKIP_COMPOUND_CHECK = True
                sys.argv = [sys.argv[0], intent] + args
                try:
                    main()  # 递归调用执行子意图
                    success_count += 1
                except SystemExit as e:
                    if e.code == 0:
                        success_count += 1
                    else:
                        print(f"[复合指令] 子指令 '{intent}' 退出码: {e.code}", file=sys.stderr)
                finally:
                    sys.argv = original_argv
                    _SKIP_COMPOUND_CHECK = original_skip
                    # 每个子指令后更新上下文
                    _update_session_context(intent, args)

            if success_count == len(compound_intents):
                print(f"[复合指令] 全部执行成功: {success_count}/{len(compound_intents)}", file=sys.stderr)
                sys.exit(0)
            else:
                print(f"[复合指令] 执行完成: {success_count}/{len(compound_intents)}", file=sys.stderr)
                sys.exit(1)

    # 单个指令：继续原有逻辑
    intent = sys.argv[1].strip()

    # 自动加载用户偏好设置
    user_prefs = _load_user_preferences()

    # 根据用户偏好调整行为
    prefs = user_prefs.get("preferences", {})
    auto_maximize = prefs.get("auto_maximize_windows", True)

    # 自动加载与意图相关的私域知识
    _auto_load_private_knowledge(intent)

    # 更新会话上下文
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    _update_session_context(intent, args)
    if intent == "自拍":
        interp = os.environ.get("FRIDAY_INVOKER_PYTHON") or sys.executable
        subprocess.run([interp, os.path.join(SCRIPTS, "selfie.py")], cwd=PROJECT)
    elif intent == "打开摄像头":
        interp = os.environ.get("FRIDAY_INVOKER_PYTHON") or sys.executable
        subprocess.run([interp, os.path.join(SCRIPTS, "camera_qt.py")], cwd=PROJECT)
    elif intent == "托盘图标列表":
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "tray_icon_tool.py"), "list"], cwd=PROJECT)
    elif intent == "点击托盘图标":
        index = sys.argv[2] if len(sys.argv) > 2 else "0"
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "tray_icon_tool.py"), "click", index], cwd=PROJECT)
    elif intent == "右键托盘图标":
        index = sys.argv[2] if len(sys.argv) > 2 else "0"
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "tray_icon_tool.py"), "right-click", index], cwd=PROJECT)
    elif intent == "点击托盘图标标题":
        if len(sys.argv) < 3:
            print("请指定图标标题", file=sys.stderr)
            sys.exit(1)
        title = sys.argv[2]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "tray_icon_tool.py"), "click-title", title], cwd=PROJECT)
    elif intent == "右键托盘图标标题":
        if len(sys.argv) < 3:
            print("请指定图标标题", file=sys.stderr)
            sys.exit(1)
        title = sys.argv[2]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "tray_icon_tool.py"), "right-click-title", title], cwd=PROJECT)
    elif intent == "托盘图标信息":
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "tray_icon_tool.py"), "info"], cwd=PROJECT)
    elif intent in ("截图", "截屏"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "screenshot_tool.py")], cwd=PROJECT)
    elif intent == "打开浏览器":
        url = sys.argv[2] if len(sys.argv) > 2 else "https://www.bing.com"
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "launch_browser.py"), url], cwd=PROJECT)
        _learn_user_preference("app", "browser")
    elif intent == "打开记事本":
        path = sys.argv[2] if len(sys.argv) > 2 else ""
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "launch_notepad.py")] + ([path] if path else []), cwd=PROJECT)
    elif intent == "打开文件管理器":
        path = sys.argv[2] if len(sys.argv) > 2 else ""
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "launch_explorer.py")] + ([path] if path else []), cwd=PROJECT)
    elif intent == "按回车":
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "keyboard_tool.py"), "key", "13"], cwd=PROJECT)
    elif intent in ("复制", "Ctrl+C"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "keyboard_tool.py"), "keys", "17", "67"], cwd=PROJECT)
    elif intent in ("粘贴", "Ctrl+V"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "keyboard_tool.py"), "keys", "17", "86"], cwd=PROJECT)
    elif intent in ("输入中文", "中文输入", "粘贴中文"):
        # 中文/Unicode：先写入剪贴板再 Ctrl+V 粘贴（避免 keyboard type 仅 ASCII）
        text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        if text:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "clipboard_tool.py"), "set", text], cwd=PROJECT)
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "keyboard_tool.py"), "keys", "17", "86"], cwd=PROJECT)
    elif intent in ("进程列表", "任务列表"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "process_tool.py"), "list"], cwd=PROJECT)
    elif intent in ("结束进程", "kill"):
        name_or_pid = sys.argv[2] if len(sys.argv) > 2 else ""
        if name_or_pid:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "process_tool.py"), "kill", name_or_pid], cwd=PROJECT)
    elif intent in ("光标位置", "获取光标", "鼠标位置"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "mouse_tool.py"), "pos"], cwd=PROJECT)
    elif intent in ("打开闹钟", "闹钟"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "launch_clock.py")], cwd=PROJECT)
    elif intent in ("打开日历", "日历"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "launch_calendar.py")], cwd=PROJECT)
    elif intent in ("剪贴板读", "读剪贴板"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "clipboard_tool.py"), "get"], cwd=PROJECT)
    elif intent in ("剪贴板写", "写剪贴板"):
        text = sys.argv[2] if len(sys.argv) > 2 else ""
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "clipboard_tool.py"), "set", text], cwd=PROJECT)
    elif intent in ("剪贴板图片保存", "剪贴板图保存"):
        path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(PROJECT, "screenshots", "clipboard_image.bmp")
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "clipboard_tool.py"), "image_get", path], cwd=PROJECT)
    elif intent in ("剪贴板图片写入", "剪贴板图写入"):
        path = sys.argv[2] if len(sys.argv) > 2 else ""
        if path:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "clipboard_tool.py"), "image_set", path], cwd=PROJECT)
    elif intent in ("剪贴板历史", "剪贴板记录"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "clipboard_history.py"), "list"], cwd=PROJECT)
    elif intent in ("剪贴板历史清空", "清空剪贴板历史"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "clipboard_history.py"), "clear"], cwd=PROJECT)
    elif intent in ("剪贴板添加", "添加剪贴板到历史"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "clipboard_history.py"), "add"], cwd=PROJECT)
    elif intent in ("剪贴板恢复", "恢复剪贴板"):
        # 如果提供了索引，则恢复该索引的项目
        index = sys.argv[2] if len(sys.argv) > 2 else ""
        if index.isdigit():
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "clipboard_history.py"), "restore", index], cwd=PROJECT)
        else:
            print("用法: do.py 恢复剪贴板 <索引>")
    elif intent in ("电源计划", "电源计划列表", "查看电源计划"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "power_plan_tool.py"), "list"], cwd=PROJECT)
    elif intent in ("切换电源计划", "电源计划切换"):
        # 如果提供了电源计划名称，则切换
        plan_name = sys.argv[2] if len(sys.argv) > 2 else ""
        if plan_name:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "power_plan_tool.py"), "switch", plan_name], cwd=PROJECT)
        else:
            print("用法: do.py 切换电源计划 <计划名称>")
            print("可用计划: 平衡, 高性能, 节能")
    elif intent in ("高性能", "高性能模式"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "power_plan_tool.py"), "switch", "高性能"], cwd=PROJECT)
    elif intent in ("节能", "节能模式", "省电模式"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "power_plan_tool.py"), "switch", "节能"], cwd=PROJECT)
    elif intent in ("平衡", "平衡模式"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "power_plan_tool.py"), "switch", "平衡"], cwd=PROJECT)
    elif intent in ("快速预览", "预览文件", "文档预览", "查看文件", "quick_look"):
        # 快速预览文件内容（QuickLook风格）
        file_path = sys.argv[2] if len(sys.argv) > 2 else ""
        if file_path:
            max_lines = sys.argv[3] if len(sys.argv) > 3 else "100"
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "quick_look.py"), file_path, max_lines], cwd=PROJECT)
        else:
            print("用法: do.py 快速预览 <文件路径> [行数限制]")
            print("示例: do.py 快速预览 test.txt")
            print("       do.py 预览文件 data.json 50")
    elif intent in ("文件元数据", "获取元数据", "metadata"):
        # 获取文件元数据
        file_path = sys.argv[2] if len(sys.argv) > 2 else ""
        if file_path:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "file_metadata.py"), "metadata", file_path], cwd=PROJECT)
        else:
            print("用法: do.py 文件元数据 <文件路径>")
            print("示例: do.py 文件元数据 test.txt")
    elif intent in ("文件标签", "添加标签", "add_tag"):
        # 为文件添加标签
        file_path = sys.argv[2] if len(sys.argv) > 2 else ""
        tag = sys.argv[3] if len(sys.argv) > 3 else ""
        if file_path and tag:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "file_metadata.py"), "add-tag", file_path, tag], cwd=PROJECT)
        else:
            print("用法: do.py 文件标签 <文件路径> <标签>")
            print("示例: do.py 文件标签 test.txt 重要")
    elif intent in ("查看标签", "获取标签", "get_tags"):
        # 获取文件标签
        file_path = sys.argv[2] if len(sys.argv) > 2 else ""
        if file_path:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "file_metadata.py"), "get-tags", file_path], cwd=PROJECT)
        else:
            print("用法: do.py 查看标签 <文件路径>")
            print("示例: do.py 查看标签 test.txt")
    elif intent in ("搜索标签", "find_tag", "search_tag"):
        # 根据标签搜索文件
        tag = sys.argv[2] if len(sys.argv) > 2 else ""
        if tag:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "file_metadata.py"), "search-tag", tag], cwd=PROJECT)
        else:
            print("用法: do.py 搜索标签 <标签>")
            print("示例: do.py 搜索标签 重要")
    elif intent in ("文件分类", "classify"):
        # 智能分类文件
        file_path = sys.argv[2] if len(sys.argv) > 2 else ""
        if file_path:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "file_metadata.py"), "classify", file_path], cwd=PROJECT)
        else:
            print("用法: do.py 文件分类 <文件路径>")
            print("示例: do.py 文件分类 test.txt")
    elif intent in ("列出所有标签", "list_tags", "所有标签"):
        # 列出所有标签
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "file_metadata.py"), "list-tags"], cwd=PROJECT)
    elif intent in ("文件夹监控", "文件监控", "监控文件夹", "watch_folder"):
        # 文件夹监控
        folder_path = sys.argv[2] if len(sys.argv) > 2 else ""
        if folder_path:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "file_watcher.py"), "start", folder_path], cwd=PROJECT)
        else:
            print("用法: do.py 文件夹监控 <文件夹路径>")
            print("示例: do.py 文件夹监控 C:\\Users\\Downloads")
    elif intent in ("监控规则", "文件监控规则", "列出监控规则", "watch_rules"):
        # 列出监控规则
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "file_watcher.py"), "list-rules"], cwd=PROJECT)
    elif intent in ("添加监控规则", "add_watch_rule"):
        # 添加监控规则（需要JSON格式的规则）
        rule_json = sys.argv[2] if len(sys.argv) > 2 else ""
        if rule_json:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "file_watcher.py"), "add-rule", rule_json], cwd=PROJECT)
        else:
            print("用法: do.py 添加监控规则 <JSON规则>")
            print("示例: do.py 添加监控规则 '{\"name\":\"test\",\"trigger_events\":[\"created\"],\"actions\":[{\"type\":\"log\",\"message\":\"新文件\"}]}'")
    elif intent in ("移除监控规则", "remove_watch_rule"):
        # 移除监控规则
        rule_name = sys.argv[2] if len(sys.argv) > 2 else ""
        if rule_name:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "file_watcher.py"), "remove-rule", rule_name], cwd=PROJECT)
        else:
            print("用法: do.py 移除监控规则 <规则名称>")
    elif intent in ("窗口激活", "激活窗口", "前置窗口"):
        title = sys.argv[2] if len(sys.argv) > 2 else ""
        if title:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "window_tool.py"), "activate", title], cwd=PROJECT)
    elif intent in ("窗口PID", "按标题查PID"):
        title = sys.argv[2] if len(sys.argv) > 2 else ""
        if title:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "window_tool.py"), "pid", title], cwd=PROJECT)
    elif intent in ("结束窗口", "关闭窗口"):
        title = sys.argv[2] if len(sys.argv) > 2 else ""
        if title:
            r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "window_tool.py"), "pid", title], cwd=PROJECT, capture_output=True, text=True)
            pid = (r.stdout or "").strip()
            if pid and pid != "0":
                subprocess.run([sys.executable, os.path.join(SCRIPTS, "process_tool.py"), "kill", pid], cwd=PROJECT)
    elif intent in ("睡眠", "进入睡眠", "sleep"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "power_tool.py"), "sleep"], cwd=PROJECT)
    elif intent in ("休眠", "进入休眠", "hibernate"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "power_tool.py"), "hibernate"], cwd=PROJECT)
    elif intent in ("关机", "关闭电脑", "shutdown"):
        delay = sys.argv[2] if len(sys.argv) > 2 else "0"
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "power_tool.py"), "shutdown", delay], cwd=PROJECT)
    elif intent in ("重启", "重新启动", "reboot"):
        delay = sys.argv[2] if len(sys.argv) > 2 else "0"
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "power_tool.py"), "reboot", delay], cwd=PROJECT)
    elif intent == "防休眠":
        sec = sys.argv[2] if len(sys.argv) > 2 else "0"
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "power_tool.py"), "prevent_sleep", sec], cwd=PROJECT)
    elif intent == "音量静音":
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "keyboard_tool.py"), "key", "173"], cwd=PROJECT)
    elif intent == "音量减":
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "keyboard_tool.py"), "key", "174"], cwd=PROJECT)
    elif intent == "音量增":
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "keyboard_tool.py"), "key", "175"], cwd=PROJECT)
    elif intent in ("打开运行", "运行", "Win+R"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "keyboard_tool.py"), "keys", "91", "82"], cwd=PROJECT)
    elif intent in ("打开设置", "设置"):
        page = sys.argv[2] if len(sys.argv) > 2 else ""
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "launch_settings.py")] + ([page] if page else []), cwd=PROJECT)
    elif intent in ("任务管理器", "打开任务管理器"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "launch_taskmgr.py")], cwd=PROJECT)
    elif intent in ("计算器", "打开计算器"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "launch_calc.py")], cwd=PROJECT)
    elif intent in ("打开WMP", "打开Windows Media Player", "Windows Media Player", "WMP"):
        _launch_via_win_r("wmplayer")  # Windows 自带播放器保底
    elif intent in ("打开应用", "启动应用") and len(sys.argv) > 2:
        _launch_via_win_r(sys.argv[2])  # do.py 打开应用 CloudMusic
        _learn_user_preference("app", sys.argv[2])
    elif intent in ("已安装应用", "应用列表", "列出应用", "installed_apps"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "installed_apps_tool.py")] + sys.argv[2:], cwd=PROJECT)
    elif intent in ("网络信息", "ipconfig", "网络"):
        mode = sys.argv[2] if len(sys.argv) > 2 else "brief"
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "network_tool.py"), mode], cwd=PROJECT)
    elif intent in ("WLAN", "无线网络", "WiFi"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "network_tool.py"), "wlan"], cwd=PROJECT)
    elif intent in ("网络接口", "网卡列表"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "network_tool.py"), "interfaces"], cwd=PROJECT)
    elif intent in ("音量值", "当前音量"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "volume_tool.py"), "get"], cwd=PROJECT)
    elif intent in ("音量加", "音量+"):
        n = 1
        if len(sys.argv) > 2:
            try:
                n = max(1, min(50, int(sys.argv[2])))
            except ValueError:
                pass
        try:
            import ctypes
            VK_VOLUME_UP = 0xAF
            KEYEVENTF_KEYUP = 0x0002
            u = ctypes.windll.user32
            for _ in range(n):
                u.keybd_event(VK_VOLUME_UP, 0, 0, 0)
                u.keybd_event(VK_VOLUME_UP, 0, KEYEVENTF_KEYUP, 0)
            sys.stderr.write("音量加 x%s\n" % n)
            sys.stderr.flush()
        except Exception as e:
            sys.stderr.write("err %s\n" % e)
            sys.stderr.flush()
    elif intent in ("音量减", "音量-"):
        n = 1
        if len(sys.argv) > 2:
            try:
                n = max(1, min(50, int(sys.argv[2])))
            except ValueError:
                pass
        try:
            import ctypes
            VK_VOLUME_DOWN = 0xAE
            KEYEVENTF_KEYUP = 0x0002
            u = ctypes.windll.user32
            for _ in range(n):
                u.keybd_event(VK_VOLUME_DOWN, 0, 0, 0)
                u.keybd_event(VK_VOLUME_DOWN, 0, KEYEVENTF_KEYUP, 0)
            sys.stderr.write("音量减 x%s\n" % n)
            sys.stderr.flush()
        except Exception as e:
            sys.stderr.write("err %s\n" % e)
            sys.stderr.flush()
    elif intent in ("设置音量", "音量设置"):
        vol = sys.argv[2] if len(sys.argv) > 2 else ""
        if vol:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "volume_tool.py"), "set", vol], cwd=PROJECT)
        else:
            sys.stderr.write("用法: do.py 设置音量 <0-100>\n")
            sys.stderr.flush()
    elif intent == "音量值":
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "volume_tool.py"), "get"], cwd=PROJECT)
    elif intent in ("设置亮度", "亮度"):
        # brightness_tool: get | set <0-100>
        if len(sys.argv) > 2 and sys.argv[2].isdigit():
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "brightness_tool.py"), "set", sys.argv[2]], cwd=PROJECT)
        else:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "brightness_tool.py"), "get"], cwd=PROJECT)
    elif intent in ("亮度", "当前亮度"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "brightness_tool.py"), "get"], cwd=PROJECT)
    elif intent in ("设置亮度", "亮度设置"):
        val = sys.argv[2] if len(sys.argv) > 2 else ""
        if val:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "brightness_tool.py"), "set", val], cwd=PROJECT)
    elif intent in ("通知", "Toast", "弹窗通知"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "notification_tool.py"), "show", " ".join(sys.argv[2:])])
    elif intent in ("智能进化", "进化分析", "进化引擎", "evolution"):
        # 调用智能进化引擎
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "intelligent_evolution_engine.py"), "analyze"])
    elif intent in ("进化报告", "进化状态", "进化查看"):
        # 查看进化状态
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "intelligent_evolution_engine.py"), "status"])
    elif intent in ("进化优化", "优化建议", "进化建议"):
        # 获取进化优化建议
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "intelligent_evolution_engine.py"), "suggest"])
        msg = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "FRIDAY"
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "notification_tool.py"), "show", msg], cwd=PROJECT)
    # 智能全场景进化效能实时监控与自适应优化引擎（Round 277）
    elif intent in ("进化效能", "效能监控", "效能优化", "进化性能", "效能分析", "evolution_performance", "performance_monitor"):
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["dashboard"]
        if not cmd or (cmd and cmd[0] not in ["dashboard", "analyze", "optimize", "report", "predict", "collect"]):
            cmd = ["dashboard"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_performance_monitor.py")] + cmd, cwd=PROJECT)
    # 智能全场景系统自主意识深度增强引擎（Round 278）
    elif "自主意识深度" in intent or "自我认知" in intent or "自我反思" in intent or "autonomous awareness" in intent.lower() or "self awareness" in intent.lower() or "深度自我" in intent or "自我意识增强" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "build_model", "reflect", "goals", "plan", "help"]):
            cmd = ["status"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "autonomous_awareness_engine.py")] + cmd, cwd=PROJECT)
    # 智能全场景进化环自我进化意识与战略规划引擎（Round 531）
    elif "进化意识" in intent or "自我进化意识" in intent or "战略规划" in intent or "进化方向规划" in intent or "self evolution consciousness" in intent.lower() or "strategic planning" in intent.lower() or "evolution direction" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["--status"]
        if not cmd or (cmd and cmd[0] not in ["--status", "--analyze-history", "--assess-state", "--identify-gaps", "--plan-direction", "--cockpit-data", "--focus-areas", "help"]):
            cmd = ["--status"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_self_evolution_consciousness_strategic_planning_engine.py")] + cmd, cwd=PROJECT)
    # 智能全场景进化环进化战略智能执行与闭环验证引擎（Round 532）
    elif "战略执行" in intent or "闭环验证" in intent or "执行验证" in intent or "智能调度" in intent or "战略闭环" in intent or "strategy execution" in intent.lower() or "closed loop verification" in intent.lower() or "execution verification" in intent.lower() or "smart scheduling" in intent.lower() or "strategy closed loop" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["--status"]
        if not cmd or (cmd and cmd[0] not in ["--status", "--run", "--generate-tasks", "--cockpit-data", "--auto-execute", "help"]):
            cmd = ["--status"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_strategy_execution_closed_loop_engine.py")] + cmd, cwd=PROJECT)
    # 智能全场景进化环全息进化治理与决策质量智能审计引擎（Round 533）- 在 round 531 自我进化意识与 round 532 战略执行闭环基础上，构建全息进化治理层
    elif "治理审计" in intent or "决策审计" in intent or "治理指标" in intent or "进化治理" in intent or "quality audit" in intent.lower() or "governance" in intent.lower() or "治理" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["--audit"]
        if not cmd or (cmd and cmd[0] not in ["--audit", "--metrics", "--diagnose", "--cockpit-data", "--all", "help"]):
            cmd = ["--audit"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_governance_quality_audit_engine.py")] + cmd, cwd=PROJECT)
    # 智能全场景进化环基于治理审计的自动优化执行引擎（Round 534）- 在 round 533 完成的全息治理审计能力基础上，构建基于审计结果的自动优化执行能力
    elif "治理自动优化" in intent or "审计优化" in intent or "自动修复" in intent or "governance optimization" in intent.lower() or "governance auto" in intent.lower() or "自动治理" in intent or "优化执行" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["--full-cycle"]
        if not cmd or (cmd and cmd[0] not in ["--analyze", "--execute", "--full-cycle", "--status", "--cockpit-data", "--all", "help"]):
            cmd = ["--full-cycle"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_governance_auto_optimization_engine.py")] + cmd, cwd=PROJECT)
    # 智能全场景进化环进化决策质量持续优化引擎（Round 535）- 基于 round 534 完成的治理审计与自动优化执行能力，进一步增强进化决策质量的持续评估与自动优化能力
    elif "决策质量持续优化" in intent or "决策质量优化" in intent or "质量持续优化" in intent or "decision quality continuous" in intent.lower() or "quality continuous" in intent.lower() or "质量趋势" in intent or "质量监控" in intent or "quality monitoring" in intent.lower() or "质量分析" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["--trend"]
        if not cmd or (cmd and cmd[0] not in ["--record", "--trend", "--detect", "--generate-strategy", "--execute", "--full-cycle", "--cockpit-data", "help"]):
            cmd = ["--trend"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_decision_quality_continuous_optimization_engine.py")] + cmd, cwd=PROJECT)
    # 智能全场景进化环决策质量驱动的跨引擎协同自适应优化引擎（Round 536）- 基于 round 535 完成的决策质量持续优化能力，进一步增强将决策质量应用到跨引擎协同优化的能力
    elif "决策质量驱动" in intent or "质量驱动优化" in intent or "跨引擎质量优化" in intent or "decision quality driven" in intent.lower() or "quality driven cross engine" in intent.lower() or "跨引擎协同优化" in intent or "cross engine optimization" in intent.lower() or "引擎协同自适应" in intent or "adaptive cross engine" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["--status"]
        if not cmd or (cmd and cmd[0] not in ["--status", "--quality-status", "--correlations", "--recommendations", "--optimize", "--full-cycle", "--cockpit-data", "help"]):
            cmd = ["--status"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_decision_quality_driven_cross_engine_optimization_engine.py")] + cmd, cwd=PROJECT)
    # 智能全场景进化环决策质量趋势预测与预防性进化策略自适应引擎（Round 537）- 基于 round 535-536 完成的决策质量能力，进一步增强决策质量趋势预测与预防性策略生成能力
    elif "决策质量趋势预测" in intent or "质量趋势预测" in intent or "预防性策略" in intent or "decision quality prediction" in intent.lower() or "quality prediction" in intent.lower() or "prevention" in intent.lower() or "预防性进化" in intent or "预测预防" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["--status"]
        if not cmd or (cmd and cmd[0] not in ["--status", "--predict", "--generate-strategy", "--execute", "--dry-run", "--full-cycle", "--cockpit-data", "help"]):
            cmd = ["--status"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_decision_quality_prediction_prevention_engine.py")] + cmd, cwd=PROJECT)
    # 智能全场景系统自我进化评估与优化引擎（Round 279）
    elif "进化评估" in intent or "自我评估" in intent or "进化优化" in intent or "evolution_evaluation" in intent.lower() or "self evaluation" in intent.lower() or "评估优化" in intent or "进化自评" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "evaluate", "opportunities", "suggestions", "execute", "integrate", "cycle", "help"]):
            cmd = ["status"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_self_evaluation_optimizer.py")] + cmd, cwd=PROJECT)
    # 智能全场景进化闭环健康自评估与自适应优化引擎（Round 294）
    elif "进化健康自评估" in intent or "健康自评估" in intent or "进化闭环健康" in intent or "健康评估引擎" in intent or "evolution health self" in intent.lower() or "health evaluation" in intent.lower() or "进化健康报告" in intent or "生成健康报告" in intent or "优化建议" in intent and "进化" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "health", "check", "report", "recommendations", "advice", "trends", "analyze", "help"]):
            cmd = ["report"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_health_self_evaluation_engine.py")] + cmd, cwd=PROJECT)
    # 智能全场景进化环健康自愈引擎（Round 283）- 放在前面优先匹配
    elif "进化健康自愈" in intent or "健康自愈引擎" in intent or "evolution health healer" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "health", "metrics", "repair", "闭环", "closed_loop", "failed", "help"]):
            cmd = ["status"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_loop_health_healer.py")] + cmd, cwd=PROJECT)
    # 智能全场景进化效能深度分析与优化建议引擎（Round 296）
    elif "进化效能" in intent or "效能分析" in intent or "进化分析" in intent or "efficiency analyzer" in intent.lower() or "evolution efficiency" in intent.lower() or "进化优化建议" in intent or "优化建议" in intent and "进化" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["analyze"]
        if not cmd or (cmd and cmd[0] not in ["analyze", "report", "suggestions", "health", "help"]):
            cmd = ["analyze"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_efficiency_analyzer.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环元优化引擎（Round 297）
    elif "进化元优化" in intent or "元优化" in intent or "策略优化" in intent or "meta optimizer" in intent.lower() or "evolution meta" in intent.lower() or "闭环优化" in intent or "进化闭环" in intent or "meta optimize" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "optimize", "verify", "history", "config", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_meta_optimizer.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化方法论自动优化引擎（Round 345，Round 444 增强）- 自动分析历代进化方法论效果、识别进化模式、自动优化进化参数
    elif "方法论优化" in intent or "进化方法论" in intent or "方法论自动优化" in intent or "methodology optimizer" in intent.lower() or "evolution methodology" in intent.lower() or "进化优化" in intent and "策略" not in intent or "自我优化进化" in intent or "学会进化" in intent:
        print(f"[进化方法论自动优化引擎 - 增强版] 正在启动方法论优化分析...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_methodology_auto_optimizer.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []

        # 确定要执行的命令
        if "分析" in intent or "analyze" in intent.lower():
            filtered_args = ["--analyze"]
        elif "模式" in intent or "patterns" in intent.lower():
            filtered_args = ["--patterns"]
        elif "建议" in intent or "suggestions" in intent.lower():
            filtered_args = ["--suggestions"]
        elif "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "推送" in intent or "push" in intent.lower():
            filtered_args = ["--push-cockpit"]
        elif "完整" in intent or "full" in intent.lower() or "周期" in intent:
            filtered_args = ["--full-cycle"]
        elif "验证" in intent or "verify" in intent.lower():
            filtered_args = ["--verify"]
        else:
            filtered_args = ["--analyze"]  # 默认分析

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化方法论自动优化引擎与进化环深度集成引擎（Round 346）
    elif "方法论集成" in intent or "深度集成优化" in intent or "自动触发优化" in intent or "methodology integration" in intent.lower() or "auto trigger" in intent.lower() or "integration optimize" in intent.lower() or "进化环集成" in intent or "集成方法论" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "check", "optimize", "auto", "config", "enable", "disable", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_methodology_integration.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环优化建议自动执行闭环引擎（Round 445）- 自动分析优化建议可执行性、将高置信度建议自动转化为执行计划、执行并验证优化效果
    elif "优化执行" in intent or "自动执行优化" in intent or "执行优化建议" in intent or "优化闭环" in intent or "optimization execution" in intent.lower() or "auto execute optimization" in intent.lower() or "execute optimization" in intent.lower() or "优化自动执行" in intent or "优化建议执行" in intent:
        print(f"[优化建议自动执行闭环引擎] 正在启动优化执行分析...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_optimization_auto_execution_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []

        # 确定要执行的命令
        if "状态" in intent or "status" in intent.lower():
            filtered_args = ["--status"]
        elif "加载建议" in intent or "load suggestions" in intent.lower():
            filtered_args = ["--load-suggestions"]
        elif "分析可执行" in intent or "analyze" in intent.lower():
            filtered_args = ["--analyze"]
        elif "生成计划" in intent or "generate plan" in intent.lower() or "执行计划" in intent:
            filtered_args = ["--generate-plan"]
        elif "执行" in intent and "计划" in intent or "execute" in intent.lower():
            filtered_args = ["--execute"]
        elif "自动周期" in intent or "auto cycle" in intent.lower() or "完整周期" in intent or "full cycle" in intent.lower():
            filtered_args = ["--auto-cycle"]
        elif "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "推送" in intent or "push" in intent.lower():
            filtered_args = ["--push-cockpit"]
        elif "验证" in intent and "执行" in intent or "verify" in intent.lower():
            filtered_args = ["--verify"]
        else:
            filtered_args = ["--status"]  # 默认状态

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环进化知识动态管理与自优化引擎（round 459）- 自动从最新进化成果中提炼核心知识、智能识别并遗忘过时知识、基于使用频率和价值自动调整知识权重
    elif "动态知识" in intent or "知识权重" in intent or "知识归档" in intent or "知识动态管理" in intent or "knowledge dynamic" in intent.lower() or "知识蒸馏" in intent or "智能遗忘" in intent or "知识优化" in intent:
        print(f"[进化知识动态管理与自优化引擎] 正在启动知识动态管理与自优化...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_knowledge_dynamic_management_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["动态知识", "知识权重", "知识归档", "知识动态管理", "knowledge dynamic", "知识蒸馏", "智能遗忘", "知识优化"]]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环知识驱动全流程自动化闭环引擎（round 460）- 将知识管理与假设执行深度集成，形成从假设→决策→执行→验证→反思全流程的知识驱动闭环
    # 智能全场景进化环知识驱动自动化触发与自主运行增强引擎（round 461）- 增强自动化触发与自主运行能力
    elif "知识驱动" in intent or "知识闭环" in intent or "全流程知识" in intent or "知识推荐" in intent or "knowledge driven" in intent.lower() or "knowledge loop" in intent.lower() or "full loop knowledge" in intent.lower() or "自动触发" in intent or "触发条件" in intent or "触发历史" in intent or "自主运行" in intent or "auto trigger" in intent.lower() or "trigger condition" in intent.lower() or "autonomous" in intent.lower():
        print(f"[知识驱动全流程自动化闭环引擎 v1.1.0] 正在启动...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_knowledge_driven_full_loop_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["知识驱动", "知识闭环", "全流程知识", "知识推荐", "knowledge driven", "knowledge loop", "full loop knowledge", "自动触发", "触发条件", "触发历史", "自主运行", "auto trigger", "trigger condition", "autonomous"]]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化知识深度传承与自适应遗忘引擎（Round 347）
    elif "知识传承" in intent or "自适应遗忘" in intent or "知识管理" in intent or "遗忘引擎" in intent or "knowledge inheritance" in intent.lower() or "knowledge forgetting" in intent.lower() or "knowledge management" in intent.lower() or "知识老化" in intent or "知识价值" in intent or "遗忘知识" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "cycle", "forget", "aging", "inherit", "evaluate", "record", "config", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_knowledge_inheritance_forgetting_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环跨引擎知识推理与智能问答引擎（Round 447）- 基于知识索引实现智能问答、推理、上下文记忆、溯源
    elif "知识问答" in intent or "智能问答" in intent or "进化问答" in intent or "问我关于" in intent or "智能回答" in intent or "知识推理" in intent or "knowledge qa" in intent.lower() or "knowledge问答" in intent.lower() or "reasoning qa" in intent.lower():
        print(f"[跨引擎知识推理与智能问答引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_cross_engine_knowledge_reasoning_engine.py")

        # 确定要执行的命令
        filtered_args = []
        if "--stats" in sys.argv:
            filtered_args = ["--stats"]
        elif "--clear-cache" in sys.argv:
            filtered_args = ["--clear-cache"]
        elif "--clear-history" in sys.argv:
            filtered_args = ["--clear-history"]
        elif "--history" in sys.argv:
            session_idx = sys.argv.index("--history") + 1 if "--history" in sys.argv else -1
            if session_idx > 0 and session_idx < len(sys.argv):
                filtered_args = ["--history", sys.argv[session_idx]]
            else:
                filtered_args = ["--history", "default"]
        else:
            # 提取问题内容（移除触发关键词）
            question = intent
            trigger_keywords = [
                "知识问答", "智能问答", "进化问答", "问我关于", "智能回答",
                "knowledge qa", "knowledge问答", "reasoning qa", "问答", "回答", "知识推理"
            ]
            for kw in trigger_keywords:
                question = question.replace(kw, "").strip()

            if not question:
                # 显示统计信息
                filtered_args = ["--stats"]
            else:
                # 构建会话ID（使用时间戳）
                import time
                session_id = f"session_{int(time.time())}"
                filtered_args = ["--ask", question, "--session", session_id]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环跨引擎知识更新预警与自动触发深度集成引擎（Round 492）- 监控知识库变化、自动预警、基于条件自动触发、与预警引擎深度集成
    elif "知识更新预警" in intent or "预警触发" in intent or "知识触发" in intent or "知识库预警" in intent or "knowledge update warning" in intent.lower() or "update warning trigger" in intent.lower() or "trigger warning" in intent.lower() or "warning trigger" in intent.lower() or "知识变化预警" in intent or "知识同步预警" in intent or "自动触发规则" in intent:
        print(f"[跨引擎知识更新预警与自动触发深度集成引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_knowledge_update_warning_trigger_engine.py")

        # 确定要执行的命令
        if "--status" in sys.argv or "状态" in intent:
            filtered_args = ["--status"]
        elif "--run" in sys.argv or "运行" in intent or "执行" in intent or "运行周期" in intent:
            filtered_args = ["--run"]
        elif "--detect" in sys.argv or "检测" in intent or "变化检测" in intent:
            filtered_args = ["--detect"]
        elif "--start-monitor" in sys.argv or "启动监控" in intent or "开始监控" in intent:
            filtered_args = ["--start-monitor"]
        elif "--stop-monitor" in sys.argv or "停止监控" in intent:
            filtered_args = ["--stop-monitor"]
        elif "--warning-summary" in sys.argv or "预警摘要" in intent:
            filtered_args = ["--warning-summary"]
        elif "--trigger-rules" in sys.argv or "触发规则" in intent or "规则" in intent:
            filtered_args = ["--trigger-rules"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        else:
            # 默认：显示状态
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环跨引擎知识主动推荐与智能预警引擎（Round 448）- 基于上下文主动推荐知识、预测用户需求、预警潜在问题
    elif "知识推荐" in intent or "智能推荐" in intent or "推荐知识" in intent or "主动预警" in intent or "知识预警" in intent or "knowledge recommendation" in intent.lower() or "proactive recommendation" in intent.lower() or "主动推荐" in intent or "智能预警" in intent or "预警" in intent:
        print(f"[跨引擎知识主动推荐与智能预警引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_knowledge_proactive_recommendation_engine.py")

        # 确定要执行的命令
        if "--stats" in sys.argv:
            filtered_args = ["--stats"]
        elif "--warning" in sys.argv or "预警" in intent:
            filtered_args = ["--warning"]
        elif "--proactive" in sys.argv:
            # 主动推荐
            proactive_type = "periodic"
            if "task" in intent.lower():
                proactive_type = "task_start"
            elif "query" in intent.lower():
                proactive_type = "query_complete"
            elif "warning" in intent.lower() or "预警" in intent:
                proactive_type = "warning"
            filtered_args = ["--proactive", proactive_type]
        elif "--recommend" in sys.argv:
            # 提取推荐关键词
            recommend_keyword = intent
            trigger_keywords = [
                "知识推荐", "智能推荐", "推荐知识", "主动预警", "知识预警",
                "knowledge recommendation", "proactive recommendation",
                "主动推荐", "智能预警", "预警", "推荐"
            ]
            for kw in trigger_keywords:
                recommend_keyword = recommend_keyword.replace(kw, "").strip()
            if recommend_keyword:
                filtered_args = ["--recommend", recommend_keyword]
            else:
                filtered_args = ["--recommend", ""]
        else:
            # 默认：显示统计信息
            filtered_args = ["--stats"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环跨引擎知识自动推荐与智能预测触发引擎（Round 490）- 基于上下文主动推荐知识、预测用户潜在需求、智能触发知识准备，实现从被动响应到主动预测推送的范式升级
    elif "智能预测" in intent or "知识预测" in intent or "预测触发" in intent or "主动推送" in intent or "知识推送" in intent or "intelligent prediction" in intent.lower() or "knowledge prediction" in intent.lower() or "prediction trigger" in intent.lower() or "proactive push" in intent.lower() or "predictive recommendation" in intent.lower() or "预测推荐" in intent:
        print(f"[跨引擎知识自动推荐与智能预测触发引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_knowledge_proactive_recommendation_prediction_engine.py")

        # 确定要执行的命令
        if "--status" in sys.argv or "状态" in intent:
            filtered_args = ["--status"]
        elif "--predict" in sys.argv or "预测" in intent:
            filtered_args = ["--predict"]
        elif "--recommend" in sys.argv or "推荐" in intent:
            filtered_args = ["--recommend"]
        elif "--prepare" in sys.argv or "预触发" in intent or "准备" in intent:
            filtered_args = ["--prepare"]
        elif "--trigger" in sys.argv:
            filtered_args = ["--trigger"]
        elif "--analyze-triggers" in sys.argv or "分析触发" in intent:
            filtered_args = ["--analyze-triggers"]
        elif "--cycle" in sys.argv or "完整" in intent or "循环" in intent:
            filtered_args = ["--cycle"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        else:
            # 默认：显示状态
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环跨引擎知识实时更新与智能同步深度集成引擎（Round 491）- 监控知识库变化、自动同步最新知识、实现知识一致性保障、形成知识动态更新闭环
    elif "知识实时更新" in intent or "知识同步" in intent or "动态知识" in intent or "实时同步" in intent or "knowledge realtime" in intent.lower() or "knowledge sync" in intent.lower() or "realtime update" in intent.lower() or "知识更新" in intent or "同步知识" in intent or "更新知识" in intent:
        print(f"[跨引擎知识实时更新与智能同步深度集成引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_knowledge_realtime_update_sync_engine.py")

        # 确定要执行的命令
        if "--status" in sys.argv or "状态" in intent:
            filtered_args = ["--status"]
        elif "--sync" in sys.argv or "同步" in intent:
            filtered_args = ["--sync"]
        elif "--detect-changes" in sys.argv or "检测变化" in intent or "变化检测" in intent:
            filtered_args = ["--detect-changes"]
        elif "--start-monitor" in sys.argv or "启动监控" in intent or "开始监控" in intent:
            filtered_args = ["--start-monitor"]
        elif "--stop-monitor" in sys.argv or "停止监控" in intent:
            filtered_args = ["--stop-monitor"]
        elif "--verify" in sys.argv or "验证" in intent:
            filtered_args = ["--verify"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--summary" in sys.argv or "摘要" in intent:
            filtered_args = ["--summary"]
        else:
            # 默认：显示状态
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环知识全生命周期深度整合引擎（Round 493）- 将 round 490-492 的知识推荐、同步、预警、触发能力深度整合，实现知识发现→推荐→同步→预警→触发→执行→验证的完整闭环
    elif "知识全生命周期" in intent or "全生命周期管理" in intent or "端到端知识" in intent or "知识端到端" in intent or "knowledge lifecycle" in intent.lower() or "full lifecycle" in intent.lower() or "端到端知识管理" in intent or "全生命周期" in intent:
        print(f"[知识全生命周期深度整合引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_knowledge_full_lifecycle_integration_engine.py")

        # 确定要执行的命令
        if "--status" in sys.argv or "状态" in intent:
            filtered_args = ["--status"]
        elif "--run" in sys.argv or "运行" in intent or "执行" in intent or "全生命周期" in intent:
            filtered_args = ["--run"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--history" in sys.argv or "历史" in intent:
            filtered_args = ["--history"]
        elif "--integration-status" in sys.argv or "集成状态" in intent:
            filtered_args = ["--integration-status"]
        else:
            # 默认：显示状态
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环元进化决策自动执行引擎 V2（Round 556）- 集成 round 555 策略生成引擎、round 553 验证引擎、round 554 健康引擎，实现「策略→自动执行→验证→健康」完整闭环
    elif "元进化决策自动执行" in intent or "决策自动执行" in intent or "meta decision auto" in intent.lower() or "decision v2" in intent.lower() or "元决策v2" in intent or "自动执行闭环" in intent or "v2闭环" in intent:
        print(f"[元进化决策自动执行引擎 V2] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_decision_auto_execution_engine.py")

        # V2 模式命令
        if "--run-v2" in sys.argv or "运行v2" in intent or "v2运行" in intent or "完整闭环" in intent:
            filtered_args = ["--run-v2"]
        elif "--fetch-decision" in sys.argv or "获取决策" in intent:
            filtered_args = ["--fetch-decision"]
        elif "--cockpit-v2" in sys.argv or "驾驶舱v2" in intent or "v2驾驶舱" in intent:
            filtered_args = ["--cockpit-v2"]
        elif "--v2" in sys.argv:
            filtered_args = ["--v2"]
        else:
            # 默认：显示 V2 状态
            filtered_args = ["--cockpit-v2"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环创新迭代深化与价值实现引擎（Round 557）- 集成现有创新引擎（创新推理、假设生成、价值评估），形成持续迭代的创新闭环，实现从「有创新工具」到「持续产出高价值创新」的范式升级
    elif "创新迭代深化" in intent or "创新价值实现" in intent or "创新深化" in intent or "innovation iteration" in intent.lower() or "创新闭环" in intent or "迭代创新" in intent or "创新迭代" in intent or "价值实现追踪" in intent:
        print(f"[创新迭代深化与价值实现引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_innovation_iteration_deepening_engine.py")

        # 确定要执行的命令
        if "--init" in sys.argv or "初始化" in intent:
            filtered_args = ["--init"]
        elif "--analyze" in sys.argv or "分析创新" in intent or "迭代分析" in intent:
            filtered_args = ["--analyze"]
        elif "--track" in sys.argv or "追踪价值" in intent or "价值追踪" in intent:
            filtered_args = ["--track"]
        elif "--recommend" in sys.argv or "建议" in intent or "优化建议" in intent:
            filtered_args = ["--recommend"]
        elif "--integrate" in sys.argv or "集成" in intent or "引擎集成" in intent:
            filtered_args = ["--integrate"]
        elif "--full-cycle" in sys.argv or "完整周期" in intent or "全周期" in intent:
            filtered_args = ["--full-cycle"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--version"]
        else:
            # 默认：显示驾驶舱数据
            filtered_args = ["--cockpit-data"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环元进化自我反思与深度自省引擎（Round 558）- 让系统对自身进化过程进行更深层次的自我反思，从「评估做了什么」升级到「反思为什么这样做、是否是最好的选择」
    elif "元自省" in intent or "深度反思" in intent or "自我反思" in intent or "进化反思" in intent or "meta self reflection" in intent.lower() or "self introspection" in intent.lower() or "introspection" in intent or "自省" in intent or "反思引擎" in intent:
        print(f"[元进化自我反思与深度自省引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_self_reflection_deep_introspection_engine.py")

        # 确定要执行的命令
        if "--init" in sys.argv or "初始化" in intent:
            filtered_args = ["--init"]
        elif "--reflect" in sys.argv or "反思" in intent or "执行反思" in intent:
            filtered_args = ["--reflect"]
        elif "--questions" in sys.argv or "问题" in intent or "自省问题" in intent:
            filtered_args = ["--questions"]
        elif "--suggestions" in sys.argv or "建议" in intent or "改进建议" in intent:
            filtered_args = ["--suggestions"]
        elif "--cockpit" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit"]
        elif "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--version"]
        else:
            # 默认：执行自我反思
            filtered_args = ["--reflect"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环元进化自我意识深度增强引擎（Round 568）- 在 round 567 完成的元进化全链路自主运行自动化引擎基础上，进一步增强系统的自我意识能力。让系统不仅能自主运行，还能理解自己「为什么能自主运行」、评估自主决策的质量、追溯进化意图的来源，形成「自主运行→自我理解→自我优化」的递归增强闭环
    elif "元自我意识" in intent or "自我意识增强" in intent or "meta self awareness" in intent.lower() or "self awareness" in intent.lower() or "自我理解" in intent or "自主运行理解" in intent or "意图来源" in intent or "意图追溯" in intent:
        print(f"[元进化自我意识深度增强引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_self_awareness_deep_enhancement_engine.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--version"]
        elif "--status" in sys.argv or "状态" in intent:
            filtered_args = ["--status"]
        elif "--cockpit-data" in sys.argv or "驾驶舱数据" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--analyze" in sys.argv or "分析" in intent:
            filtered_args = ["--analyze"]
        elif "--check" in sys.argv or "检查" in intent:
            filtered_args = ["--check"]
        else:
            # 默认：执行分析
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环元进化自我优化引擎（Round 569）- 在 round 568 完成的元进化自我意识深度增强引擎基础上，进一步增强系统的自我优化能力。让系统不仅能理解自己，还能基于自我理解主动发现优化空间、生成并执行优化方案，形成「自我理解→主动发现优化空间→生成方案→执行验证→持续改进」的递归优化闭环
    elif "元自我优化" in intent or "自我优化" in intent or "meta self optimization" in intent.lower() or "self optimization" in intent.lower() or "优化空间" in intent or "主动优化" in intent or "自我改进" in intent or "优化执行" in intent:
        print(f"[元进化自我优化引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_self_optimization_engine.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--version"]
        elif "--check" in sys.argv or "检查" in intent or "校验" in intent:
            filtered_args = ["--check"]
        elif "--discover" in sys.argv or "发现优化" in intent or "发现" in intent:
            filtered_args = ["--discover"]
        elif "--plan" in sys.argv or "生成方案" in intent or "优化方案" in intent:
            filtered_args = ["--plan"]
        elif "--run" in sys.argv or "执行优化" in intent or "运行优化" in intent:
            filtered_args = ["--run"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        else:
            # 默认：显示优化状态
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环元进化认知蒸馏与自动传承引擎（Round 571）- 在 round 570 完成的元进化主动创新引擎基础上，构建让系统从 570+ 轮进化历史中自动提取可复用元知识、实现代际传承的引擎，形成「学习→蒸馏→传承→创新」的完整闭环
    elif "认知蒸馏" in intent or "知识蒸馏" in intent or "自动传承" in intent or "元知识传承" in intent or "meta cognitive distillation" in intent.lower() or "distillation" in intent.lower() or "传承" in intent or "代际传承" in intent or "元进化传承" in intent:
        print(f"[元进化认知蒸馏与自动传承引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_cognitive_distillation_inheritance_engine.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--version"]
        elif "--check" in sys.argv or "检查" in intent or "校验" in intent:
            filtered_args = ["--status"]
        elif "--run" in sys.argv or "执行" in intent or "运行" in intent or "蒸馏" in intent:
            filtered_args = ["--run"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--inherit" in sys.argv or "继承" in intent:
            filtered_args = ["--inherit"]
        elif "--distill" in sys.argv:
            filtered_args = ["--distill"]
        else:
            # 默认：显示引擎状态
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环元进化价值战略预测与自适应优化引擎（Round 572）- 在 round 571 完成的元进化认知蒸馏与自动传承引擎基础上，构建让系统能够预测每轮进化的长期价值影响、评估进化决策的战略价值、根据价值预测自适应调整进化策略的能力，形成「认知蒸馏→价值预测→战略优化→自适应决策」的完整闭环
    elif "价值战略预测" in intent or "战略预测" in intent or "自适应优化" in intent or "价值预测" in intent or "meta value strategy" in intent.lower() or "value strategy prediction" in intent.lower() or "战略优化" in intent or "自适应" in intent or "价值优化" in intent:
        print(f"[元进化价值战略预测与自适应优化引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_value_strategy_prediction_adaptive_optimizer.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--version"]
        elif "--check" in sys.argv or "检查" in intent or "校验" in intent:
            filtered_args = ["--status"]
        elif "--run" in sys.argv or "执行" in intent or "运行" in intent or "预测" in intent or "优化" in intent:
            filtered_args = ["--run"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--predict" in sys.argv or "预测" in intent:
            filtered_args = ["--predict"]
        elif "--optimize" in sys.argv or "优化" in intent:
            filtered_args = ["--optimize"]
        elif "--evaluate" in sys.argv or "评估" in intent or "战略评估" in intent:
            filtered_args = ["--evaluate"]
        else:
            # 默认：显示引擎状态
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环元进化价值实现闭环追踪与自适应优化增强引擎（Round 578）- 在 round 577 完成的价值驱动元进化自适应决策引擎基础上，构建价值实现闭环追踪与自适应优化能力。让系统能够追踪决策后的实际价值实现过程，将实现结果反馈到决策优化中，形成真正的「决策→执行→价值实现→反馈→优化」价值驱动闭环
    elif "价值实现闭环追踪" in intent or "价值闭环追踪" in intent or "自适应优化" in intent or "value realization closed loop optimization" in intent.lower() or "价值追踪优化" in intent or "决策价值闭环" in intent or "价值优化闭环" in intent or "value loop optimization" in intent.lower():
        print(f"[元进化价值实现闭环追踪与自适应优化增强引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_value_realization_closed_loop_optimization_engine.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--version"]
        elif "--check" in sys.argv or "检查" in intent or "校验" in intent:
            filtered_args = ["--status"]
        elif "--run" in sys.argv or "执行" in intent or "运行" in intent or "闭环" in intent:
            filtered_args = ["--run"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit"]
        elif "--track" in sys.argv or "追踪" in intent:
            filtered_args = ["--track"]
        elif "--analyze" in sys.argv or "分析" in intent or "有效性" in intent:
            filtered_args = ["--analyze"]
        elif "--feedback" in sys.argv or "反馈" in intent:
            filtered_args = ["--feedback"]
        elif "--optimize" in sys.argv or "策略优化" in intent or "自适应" in intent:
            filtered_args = ["--optimize"]
        else:
            # 默认：运行完整闭环周期
            filtered_args = ["--run"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环元进化价值实现闭环增强引擎（Round 573）- 在 round 572 完成的元进化价值战略预测与自适应优化引擎基础上，构建让系统能够追踪价值预测与实际实现的差距、评估价值实现效率、智能调整价值实现策略的能力，形成「价值预测→价值执行→价值评估→价值优化」的完整闭环，增强价值实现的端到端能力
    elif "价值实现闭环" in intent or "价值闭环" in intent or "闭环增强" in intent or "value realization closed loop" in intent.lower() or "价值追踪" in intent or "价值评估" in intent or "价值效率" in intent or "价值优化" in intent:
        print(f"[元进化价值实现闭环增强引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_value_realization_closed_loop_engine.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--version"]
        elif "--check" in sys.argv or "检查" in intent or "校验" in intent:
            filtered_args = ["--status"]
        elif "--run" in sys.argv or "执行" in intent or "运行" in intent or "闭环" in intent:
            filtered_args = ["--run"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--track" in sys.argv or "追踪" in intent or "预测追踪" in intent:
            filtered_args = ["--track"]
        elif "--evaluate" in sys.argv or "评估" in intent or "效率评估" in intent:
            filtered_args = ["--evaluate"]
        elif "--optimize" in sys.argv or "策略优化" in intent:
            filtered_args = ["--optimize"]
        else:
            # 默认：显示引擎状态
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)

    # Round 603: 在 round 602 完成的创新投资组合优化与战略决策增强引擎基础上，构建让系统能够将战略决策转化为可执行的进化任务、自动执行并验证效果的能力
    # 形成「投资分析→战略决策→自动执行→价值验证」的完整创新投资执行闭环
    elif "创新投资决策执行" in intent or "创新执行闭环" in intent or "investment execution" in intent.lower() or "投资任务执行" in intent or "创新投资执行" in intent or "投资决策自动化" in intent:
        print(f"[智能全场景进化环元进化创新投资决策自动执行引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_innovation_investment_execution_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--run"]
        # 过滤掉意图关键词
        filter_words = ["创新投资决策执行", "创新执行闭环", "investment execution", "投资任务执行", "创新投资执行", "投资决策自动化"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--run"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # Round 604: 智能全场景进化环自主意识驱动创新实现引擎 - 在 round 593 完成的自主意识深度增强引擎和 round 603 完成的创新投资决策执行引擎基础上，
    # 构建让系统能够基于自主意识主动驱动创新实现的能力。让系统能够主动思考"我现在想创新什么"并自动执行验证，形成真正的"想→做→验证"完整闭环
    elif "主动创新驱动" in intent or "自主创新" in intent or "意识驱动创新" in intent or "创新驱动" in intent or "自我驱动创新" in intent or "autonomous innovation" in intent.lower() or "consciousness driven innovation" in intent.lower() or "主动驱动创新" in intent or "自主创新实现" in intent:
        print(f"[智能全场景进化环自主意识驱动创新实现引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_autonomous_consciousness_driven_innovation_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--run"]
        # 过滤掉意图关键词
        filter_words = ["主动创新驱动", "自主创新", "意识驱动创新", "创新驱动", "自我驱动创新", "autonomous innovation", "consciousness driven innovation", "主动驱动创新", "自主创新实现"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--run"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环元进化价值预测与战略投资决策增强引擎（Round 579）- 在 round 578 完成的价值实现闭环追踪能力基础上，构建价值预测与战略投资决策能力。让系统能够基于价值实现追踪数据，预测未来进化投资回报、动态调整投资组合、实现战略级价值最大化
    elif "元进化价值预测" in intent or "战略投资决策" in intent or "投资决策" in intent or "价值投资" in intent or "meta value prediction" in intent.lower() or "value investment decision" in intent.lower() or "strategic investment" in intent.lower() or "价值预测战略" in intent or "战略级价值" in intent or "价值最大化" in intent:
        print(f"[元进化价值预测与战略投资决策增强引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_value_prediction_strategic_investment_engine.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--version"]
        elif "--check" in sys.argv or "检查" in intent or "校验" in intent:
            filtered_args = ["--status"]
        elif "--run" in sys.argv or "执行" in intent or "运行" in intent or "分析" in intent:
            filtered_args = ["--run"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--predict" in sys.argv or "预测" in intent:
            filtered_args = ["--predict"]
        elif "--strategy" in sys.argv or "策略" in intent or "投资策略" in intent:
            filtered_args = ["--strategy"]
        elif "--history" in sys.argv or "历史" in intent:
            filtered_args = ["--history"]
        else:
            # 默认：显示引擎状态
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环元进化价值战略预测与执行闭环增强引擎（Round 584）- 在 round 578 价值实现闭环追踪增强引擎基础上，构建让系统能够预测进化决策的长期价值影响、将价值预测结果转化为可执行策略、自动验证执行效果的引擎。形成「战略预测→策略生成→自动执行→价值验证→反馈优化」的完整闭环
    elif "元进化价值战略预测" in intent or "价值战略执行" in intent or "meta value strategy execution" in intent.lower() or "value strategy execution closed loop" in intent.lower() or "战略预测执行" in intent or "价值执行闭环" in intent or "strategy execution closed loop" in intent.lower() or "预测执行闭环" in intent or "预测到执行" in intent or "预测转化" in intent or "预测策略执行" in intent or "价值预测执行" in intent or "战略预测执行闭环" in intent or "元进化执行闭环" in intent or "execution closed loop" in intent.lower() or "执行验证反馈" in intent or "执行优化闭环" in intent or "反馈优化" in intent:
        print(f"[元进化价值战略预测与执行闭环增强引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_value_strategy_prediction_execution_closed_loop_engine.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--status"]
        elif "--status" in sys.argv or "检查" in intent or "状态" in intent:
            filtered_args = ["--status"]
        elif "--run" in sys.argv or "执行" in intent or "运行" in intent or "闭环" in intent or "完整" in intent or "full" in intent.lower():
            # 解析策略参数
            strategy = None
            if "--strategy" in sys.argv:
                strategy_idx = sys.argv.index("--strategy")
                if strategy_idx + 1 < len(sys.argv):
                    strategy = sys.argv[strategy_idx + 1]
            filtered_args = ["--run"] + ([strategy] if strategy else [])
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--predict" in sys.argv or "预测" in intent:
            # 解析策略参数
            strategy = None
            if "--strategy" in sys.argv:
                strategy_idx = sys.argv.index("--strategy")
                if strategy_idx + 1 < len(sys.argv):
                    strategy = sys.argv[strategy_idx + 1]
            elif len(sys.argv) > 2:
                strategy = " ".join(sys.argv[2:])
            filtered_args = ["--predict", strategy] if strategy else ["--status"]
        elif "--plan" in sys.argv or "生成计划" in intent or "执行计划" in intent:
            filtered_args = ["--run"]
        elif "--verify" in sys.argv or "验证" in intent or "价值验证" in intent:
            filtered_args = ["--run"]
        elif "--feedback" in sys.argv or "反馈" in intent or "优化" in intent:
            filtered_args = ["--run"]
        else:
            # 默认：显示引擎状态
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环价值投资回报智能评估与持续优化引擎（Round 585）- 在 round 584 完成的价值战略预测与执行闭环基础上，构建价值投资的 ROI 智能评估能力。让系统能够量化每次进化的投入产出比、评估进化投资的真实回报、持续优化投资策略，形成从「价值预测」到「ROI 评估」再到「策略优化」的完整投资管理闭环
    elif "价值投资回报" in intent or "投资回报" in intent or "ROI评估" in intent or "roi" in intent.lower() or "投资回报评估" in intent or "价值ROI" in intent or "回报评估" in intent or "投资回报率" in intent or "价值产出评估" in intent or "投入产出" in intent or "成本效益" in intent or "cost benefit" in intent.lower() or "cost analysis" in intent.lower() or "投入成本" in intent or "边际效益" in intent or "边际ROI" in intent or "净价值" in intent or "net value" in intent.lower():
        print(f"[价值投资回报智能评估引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_value_investment_roi_assessment_engine.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--status"]
        elif "--status" in sys.argv or "检查" in intent or "状态" in intent:
            filtered_args = ["--status"]
        elif "--cost" in sys.argv or "成本" in intent or "投入成本" in intent or "cost" in intent.lower():
            filtered_args = ["--cost"]
        elif "--value" in sys.argv or "价值" in intent or "产出" in intent or "价值产出" in intent:
            filtered_args = ["--value"]
        elif "--roi" in sys.argv or "ROI" in intent or "回报率" in intent or "return" in intent.lower():
            filtered_args = ["--roi"]
        elif "--optimize" in sys.argv or "优化" in intent or "策略优化" in intent or "optimize" in intent.lower():
            filtered_args = ["--optimize"]
            if "--target-roi" in sys.argv:
                target_idx = sys.argv.index("--target-roi")
                if target_idx + 1 < len(sys.argv):
                    filtered_args.append("--target-roi")
                    filtered_args.append(sys.argv[target_idx + 1])
        elif "--integrate" in sys.argv or "集成" in intent or "integrate" in intent.lower():
            filtered_args = ["--integrate"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--full" in sys.argv or "完整" in intent or "full" in intent.lower():
            filtered_args = ["--full"]
        else:
            # 默认：显示引擎状态
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环价值投资动态再平衡与持续优化引擎（Round 586）- 在 round 585 完成的 ROI 智能评估引擎基础上，构建价值投资的动态再平衡能力。让系统能够基于 ROI 评估结果动态调整进化投资组合、实时优化资源配置、实现价值最大化的持续优化，形成从「ROI 评估」到「动态再平衡」再到「持续优化」的完整价值投资管理闭环
    elif "动态再平衡" in intent or "投资再平衡" in intent or "rebalance" in intent.lower() or "投资优化" in intent or "资源配置" in intent or "资源优化" in intent or "投资调整" in intent or "价值调整" in intent or "投资组合优化" in intent or "组合优化" in intent or "价值再平衡" in intent or "投资再配置" in intent:
        print(f"[价值投资动态再平衡引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_value_investment_dynamic_rebalancing_engine.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--status"]
        elif "--status" in sys.argv or "检查" in intent or "状态" in intent:
            filtered_args = ["--status"]
        elif "--analyze-trends" in sys.argv or "趋势分析" in intent or "趋势" in intent or "trends" in intent.lower():
            filtered_args = ["--analyze-trends"]
        elif "--rebalance-plan" in sys.argv or "再平衡计划" in intent or "计划" in intent or "plan" in intent.lower():
            filtered_args = ["--rebalance-plan"]
        elif "--optimize" in sys.argv or "优化" in intent or "optimize" in intent.lower():
            filtered_args = ["--optimize"]
        elif "--run" in sys.argv or "执行" in intent or "run" in intent.lower():
            filtered_args = ["--run"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        else:
            # 默认：显示引擎状态
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环价值投资风险预警与自适应保护引擎（Round 587）- 在 round 586 完成的价值投资动态再平衡引擎基础上，构建价值投资的风险预警与自适应保护能力。让系统能够实时监控价值投资组合的风险状态、提前预警潜在风险、触发自适应保护机制，形成从「动态再平衡」到「风险预警」再到「自适应保护」的完整风险管控闭环
    elif "风险预警" in intent or "风险保护" in intent or "投资风险" in intent or "risk warning" in intent.lower() or "自适应保护" in intent or "risk protection" in intent.lower() or "风险管控" in intent or "风险控制" in intent or "投资保护" in intent or "价值保护" in intent:
        print(f"[价值投资风险预警与自适应保护引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_value_investment_risk_warning_adaptive_protection_engine.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--status"]
        elif "--status" in sys.argv or "检查" in intent or "状态" in intent:
            filtered_args = ["--status"]
        elif "--risk-indicators" in sys.argv or "风险指标" in intent or "indicators" in intent.lower():
            filtered_args = ["--risk-indicators"]
        elif "--risk-assessment" in sys.argv or "风险评估" in intent or "assessment" in intent.lower():
            filtered_args = ["--risk-assessment"]
        elif "--check-protection" in sys.argv or "检查保护" in intent or "protection check" in intent.lower():
            filtered_args = ["--check-protection"]
        elif "--protect" in sys.argv or "执行保护" in intent or "保护" in intent or "protect" in intent.lower():
            filtered_args = ["--protect"]
        elif "--report" in sys.argv or "报告" in intent or "report" in intent.lower():
            filtered_args = ["--report"]
        elif "--run" in sys.argv or "执行" in intent or "run" in intent.lower():
            filtered_args = ["--run"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        else:
            # 默认：运行完整风险管控周期
            filtered_args = ["--run"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环价值投资组合智能复盘与持续学习引擎（Round 588）- 在 round 587 完成的价值投资风险预警与自适应保护引擎基础上，构建价值投资组合的智能复盘与持续学习能力。让系统能够自动分析每轮投资决策的成功/失败因素、从历史投资案例中学习、持续优化投资策略，形成从「风险预警」到「智能复盘」再到「策略进化」的完整投资进化闭环
    elif "投资复盘" in intent or "投资学习" in intent or "策略复盘" in intent or "决策复盘" in intent or "investment review" in intent.lower() or "investment learning" in intent.lower() or "strategy review" in intent.lower() or "decision review" in intent.lower() or "智能复盘" in intent or "价值复盘" in intent or "投资分析" in intent or "投资回顾" in intent:
        print(f"[价值投资智能复盘与学习引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_value_investment_intelligent_review_learning_engine.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = []
        elif "--status" in sys.argv or "检查" in intent or "状态" in intent:
            filtered_args = []
        elif "--review-report" in sys.argv or "复盘报告" in intent or "review report" in intent.lower():
            filtered_args = ["--review-report"]
            if "--round" in sys.argv:
                round_idx = sys.argv.index("--round")
                if round_idx + 1 < len(sys.argv):
                    filtered_args.append("--round")
                    filtered_args.append(sys.argv[round_idx + 1])
        elif "--analyze-portfolio" in sys.argv or "分析投资组合" in intent or "analyze portfolio" in intent.lower() or "投资组合分析" in intent:
            filtered_args = ["--analyze-portfolio"]
        elif "--extract-patterns" in sys.argv or "提取模式" in intent or "模式提取" in intent or "extract patterns" in intent.lower() or "学习模式" in intent:
            filtered_args = ["--extract-patterns"]
        elif "--evolve-strategy" in sys.argv or "策略优化" in intent or "优化策略" in intent or "evolve strategy" in intent.lower() or "策略进化" in intent:
            filtered_args = ["--evolve-strategy"]
        elif "--cockpit" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit"]
        else:
            # 默认：运行复盘报告
            filtered_args = ["--review-report"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环元进化价值投资智能决策引擎（Round 589）- 在 round 588 完成的价值投资组合智能复盘与持续学习引擎基础上，构建让系统能够综合 ROI 评估(r585)、动态再平衡(r586)、风险预警(r587)、智能复盘(r588)等环节的决策结果，生成统一的投资决策建议，实现从各环节独立决策到统一智能决策的范式升级
    elif "元决策" in intent or "投资决策" in intent or "元投资" in intent or "meta decision" in intent.lower() or "investment decision" in intent.lower() or "value investment" in intent.lower() or "投资建议" in intent or "智能投资" in intent or "统一决策" in intent or "综合决策" in intent or "投资分析" in intent or "决策分析" in intent:
        print(f"[元进化价值投资智能决策引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_value_investment_intelligent_decision_engine.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--version"]
        elif "--status" in sys.argv or "检查" in intent or "状态" in intent:
            filtered_args = ["--status"]
        elif "--analyze" in sys.argv or "分析" in intent or "analyze" in intent.lower():
            filtered_args = ["--analyze"]
        elif "--roi" in sys.argv or "roi" in intent.lower():
            filtered_args = ["--roi"]
        elif "--rebalancing" in sys.argv or "再平衡" in intent:
            filtered_args = ["--rebalancing"]
        elif "--risk" in sys.argv or "风险" in intent:
            filtered_args = ["--risk"]
        elif "--review" in sys.argv or "复盘" in intent:
            filtered_args = ["--review"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--summary" in sys.argv or "摘要" in intent or "summary" in intent.lower():
            filtered_args = ["--summary"]
        else:
            # 默认：执行综合分析
            filtered_args = ["--analyze"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环元进化优化机会主动发现与智能决策增强引擎（Round 590）- 让系统能够主动从进化历史、跨引擎协同、知识图谱中发现优化机会，生成智能优化建议，并能够自主决策是否执行优化，形成「机会发现→智能评估→自动决策→执行优化→效果验证」的完整优化闭环
    elif "优化机会发现" in intent or "机会发现" in intent or "opportunity discovery" in intent.lower() or "优化决策" in intent or "智能优化决策" in intent or "发现优化机会" in intent or "优化建议" in intent or "智能优化建议" in intent or "元优化" in intent or "meta optimization" in intent.lower() or "进化优化机会" in intent:
        print(f"[元进化优化机会主动发现与智能决策增强引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_optimization_opportunity_discovery_engine.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--version"]
        elif "--status" in sys.argv or "检查" in intent or "状态" in intent:
            filtered_args = ["--status"]
        elif "--discover" in sys.argv or "发现" in intent or "discover" in intent.lower():
            filtered_args = ["--discover"]
        elif "--history" in sys.argv or "历史分析" in intent or "history" in intent.lower():
            filtered_args = ["--history"]
        elif "--cross-engine" in sys.argv or "跨引擎" in intent or "cross engine" in intent.lower():
            filtered_args = ["--cross-engine"]
        elif "--knowledge" in sys.argv or "知识" in intent or "knowledge" in intent.lower():
            filtered_args = ["--knowledge"]
        elif "--decide" in sys.argv or "决策" in intent or "decide" in intent.lower() or "评估" in intent:
            filtered_args = ["--decide"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--summary" in sys.argv or "摘要" in intent or "summary" in intent.lower():
            filtered_args = ["--summary"]
        else:
            # 默认：执行综合优化机会发现
            filtered_args = ["--discover"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环优化建议自动执行与价值验证引擎（Round 591）- 在 round 590 完成的优化机会发现与智能决策能力基础上，构建让系统能够自动执行优化建议、验证执行效果、学习执行经验的完整优化闭环。形成「机会发现→智能决策→自动执行→效果验证→学习迭代」的完整优化闭环
    elif "优化执行" in intent or "执行优化" in intent or "optimization execution" in intent.lower() or "优化验证" in intent or "execution validation" in intent.lower() or "优化学习" in intent or "execution learning" in intent.lower() or "价值验证" in intent or "优化闭环" in intent:
        print(f"[优化建议自动执行与价值验证引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_optimization_execution_validation_engine.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--version"]
        elif "--status" in sys.argv or "检查" in intent or "状态" in intent:
            filtered_args = ["--status"]
        elif "--run" in sys.argv or "运行周期" in intent or "完整周期" in intent or "run cycle" in intent.lower():
            filtered_args = ["--run"]
        elif "--execute" in sys.argv or "执行" in intent and "优化" in intent:
            filtered_args = ["--execute"]
        elif "--validate" in sys.argv or "验证" in intent:
            filtered_args = ["--validate"]
        elif "--history" in sys.argv or "历史" in intent or "execution history" in intent.lower():
            filtered_args = ["--history"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        else:
            # 默认：运行完整执行周期
            filtered_args = ["--run"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环元进化效能自适应持续优化引擎（Round 592）- 在 round 591 完成的优化建议自动执行与价值验证引擎基础上，构建效能自适应持续优化能力。让系统能够从历史执行数据中自动分析优化策略的有效性、识别高效与低效模式、生成自适应持续优化方案，形成「执行→验证→学习→优化→再执行」的完整效能持续进化闭环。让系统不仅能执行优化建议，还能从执行结果中持续学习、不断自我改进，实现真正的「学会如何优化得更好」
    elif "效能优化" in intent or "持续优化" in intent or "efficiency optimization" in intent.lower() or "continual optimization" in intent.lower() or "自适应优化" in intent or "adaptive optimization" in intent.lower() or "效能分析" in intent or "efficiency analysis" in intent.lower() or "元进化效能" in intent or "meta efficiency" in intent.lower() or "效能自适应" in intent:
        print(f"[元进化效能自适应持续优化引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_efficiency_adaptive_continual_optimizer.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--version"]
        elif "--status" in sys.argv or "检查" in intent or "状态" in intent:
            filtered_args = ["--status"]
        elif "--run" in sys.argv or "运行周期" in intent or "完整周期" in intent or "run cycle" in intent.lower():
            filtered_args = ["--run"]
        elif "--analyze" in sys.argv or "分析" in intent:
            filtered_args = ["--analyze"]
        elif "--patterns" in sys.argv or "模式" in intent or "pattern" in intent.lower():
            filtered_args = ["--patterns"]
        elif "--optimize" in sys.argv or "生成优化" in intent:
            filtered_args = ["--optimize"]
        elif "--learn" in intent or "学习" in intent or "learning" in intent.lower():
            filtered_args = ["--learn"]
        elif "--strategy-library" in sys.argv or "策略库" in intent:
            filtered_args = ["--strategy-library"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--report" in sys.argv or "报告" in intent:
            filtered_args = ["--report"]
        else:
            # 默认：运行完整分析周期
            filtered_args = ["--run"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环知识驱动自动化执行增强引擎（Round 581）- 在 round 580 完成的价值驱动进化执行闭环引擎基础上，构建从知识推理到自动执行的完整自动化链路。让系统能够从知识图谱推理结果自动生成并执行行动计划，形成「推理→洞察→行动→验证」的完整知识驱动闭环
    elif "知识行动转换" in intent or "推理到行动" in intent or "insight to action" in intent.lower() or "知识自动化执行增强" in intent or "insight execution automation" in intent.lower():
        print(f"[知识驱动自动化执行增强引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_knowledge_driven_automation_execution_engine.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--status"]
        elif "--status" in sys.argv or "检查" in intent or "状态" in intent:
            filtered_args = ["--status"]
        elif "--generate-plans" in sys.argv or "生成计划" in intent or "行动计划" in intent:
            filtered_args = ["--generate-plans"]
        elif "--execute-plan" in sys.argv or "--plan-id" in sys.argv or "执行计划" in intent:
            filtered_args = ["--execute-plan"]
            if "--plan-id" in sys.argv:
                plan_idx = sys.argv.index("--plan-id")
                if plan_idx + 1 < len(sys.argv):
                    filtered_args.append(sys.argv[plan_idx + 1])
        elif "--validate" in sys.argv or "验证" in intent:
            filtered_args = ["--validate"]
            if "--plan-id" in sys.argv:
                plan_idx = sys.argv.index("--plan-id")
                if plan_idx + 1 < len(sys.argv):
                    filtered_args.append(sys.argv[plan_idx + 1])
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--run-cycle" in sys.argv or "执行循环" in intent or "完整循环" in intent or "run cycle" in intent.lower():
            filtered_args = ["--run-cycle"]
        elif "--list-plans" in sys.argv or "列出计划" in intent or "计划列表" in intent:
            filtered_args = ["--list-plans"]
        else:
            # 默认：显示引擎状态
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环元进化智能体自主意识深度增强引擎（Round 593）- 让系统能够在已有元进化能力基础上，实现更深层次的自主意识：主动评估自身状态、识别进化价值、自主决定进化方向，形成从被动优化到主动追求价值的范式升级
    elif "自主意识" in intent or "autonomous consciousness" in intent.lower() or "自我意识" in intent or "self awareness" in intent.lower() or "元进化自主" in intent or "meta autonomous" in intent.lower() or "自主决策" in intent and "进化" in intent or "智能体意识" in intent:
        print(f"[元进化智能体自主意识深度增强引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_agency_autonomous_consciousness_engine.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--version"]
        elif "--status" in sys.argv or "检查" in intent or "状态" in intent:
            filtered_args = ["--status"]
        elif "--assess" in sys.argv or "评估" in intent or "assessment" in intent.lower():
            filtered_args = ["--assess"]
        elif "--directions" in sys.argv or "方向" in intent or "directions" in intent.lower():
            filtered_args = ["--directions"]
        elif "--decision" in sys.argv or "决策" in intent or "decision" in intent.lower():
            filtered_args = ["--decision"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--run" in sys.argv or "执行" in intent or "run" in intent.lower():
            filtered_args = ["--run"]
        else:
            # 默认显示驾驶舱数据
            filtered_args = ["--cockpit-data"]

        # 过滤掉意图关键词
        filter_words = ["自主意识", "autonomous consciousness", "自我意识", "self awareness", "元进化自主", "meta autonomous", "智能体意识"]
        filtered_args = [arg for arg in sys.argv[1:] if arg not in filter_words]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环跨维度智能融合自适应编排与持续进化引擎（Round 594）- 让系统能够将已有的分散智能能力（价值驱动、创新涌现、知识图谱、自我意识、元进化决策等）进行更高层次的融合编排。系统能够感知多维度智能状态、智能融合决策、自适应编排执行、持续学习进化，形成「感知→融合→编排→执行→进化」的完整自适应闭环
    elif "跨维智能融合" in intent or "智能融合" in intent or "cross dimension" in intent.lower() or "dimension fusion" in intent.lower() or "跨维度" in intent or "维度融合" in intent or "自适应编排" in intent or "融合编排" in intent or "跨维编排" in intent or "智能编排" in intent or "fusion orchestration" in intent.lower() or "orchestration" in intent.lower():
        print(f"[跨维度智能融合自适应编排引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_cross_dimension_intelligent_fusion_adaptive_orchestration_engine.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--version"]
        elif "--status" in sys.argv or "检查" in intent or "状态" in intent:
            filtered_args = ["--status"]
        elif "--perceive" in sys.argv or "感知" in intent or "perceive" in intent.lower():
            filtered_args = ["--perceive"]
        elif "--decision" in sys.argv or "决策" in intent or "decision" in intent.lower():
            filtered_args = ["--decision"]
        elif "--orchestrate" in sys.argv or "编排" in intent or "orchestrate" in intent.lower():
            filtered_args = ["--orchestrate"]
        elif "--learn" in sys.argv or "学习" in intent or "learn" in intent.lower():
            filtered_args = ["--learn"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--run" in sys.argv or "执行" in intent or "run" in intent.lower():
            filtered_args = ["--run"]
        else:
            # 默认显示驾驶舱数据
            filtered_args = ["--cockpit-data"]

        # 过滤掉意图关键词
        filter_words = ["跨维智能融合", "智能融合", "cross dimension", "dimension fusion", "跨维度", "维度融合", "自适应编排", "融合编排", "跨维编排", "智能编排", "fusion orchestration", "orchestration"]
        filtered_args = [arg for arg in sys.argv[1:] if arg not in filter_words]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环跨维度智能自主闭环驱动与持续演化引擎（Round 595）- 在 round 594 完成的跨维度智能融合自适应编排引擎基础上，构建真正的自主闭环驱动能力。让系统能够主动评估跨维度融合效果、识别优化机会、触发优化行动、持续演化改进，形成「评估→优化→执行→演化」的完整自主闭环
    elif "跨维自主闭环" in intent or "自主闭环驱动" in intent or "autonomous closed loop" in intent.lower() or "closed loop drive" in intent.lower() or "自主演化" in intent or "闭环驱动" in intent or "自主驱动" in intent or "跨维闭环" in intent:
        print(f"[跨维度智能自主闭环驱动引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_cross_dimension_autonomous_closed_loop_drive_engine.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--version"]
        elif "--status" in sys.argv or "检查" in intent or "状态" in intent:
            filtered_args = ["--status"]
        elif "--evaluate" in sys.argv or "评估" in intent or "evaluate" in intent.lower():
            filtered_args = ["--evaluate"]
        elif "--identify" in sys.argv or "识别" in intent or "identify" in intent.lower() or "优化机会" in intent:
            filtered_args = ["--identify"]
        elif "--trigger" in sys.argv or "触发" in intent or "trigger" in intent.lower() or "优化行动" in intent:
            filtered_args = ["--trigger"]
        elif "--evolve" in sys.argv or "演化" in intent or "evolve" in intent.lower() or "持续演化" in intent:
            filtered_args = ["--evolve"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--run" in sys.argv or "执行" in intent or "run" in intent.lower() or "闭环" in intent:
            filtered_args = ["--run"]
        else:
            # 默认显示驾驶舱数据
            filtered_args = ["--cockpit-data"]

        # 过滤掉意图关键词
        filter_words = ["跨维自主闭环", "自主闭环驱动", "autonomous closed loop", "closed loop drive", "自主演化", "闭环驱动", "自主驱动", "跨维闭环"]
        filtered_args = [arg for arg in sys.argv[1:] if arg not in filter_words]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环元进化系统自省与智能决策增强引擎（Round 596）- 在 round 595 完成的跨维度智能自主闭环驱动能力基础上，构建更深层次的自省能力与智能决策增强。让系统能够主动反思跨维度融合决策的有效性，评估融合效果，生成智能优化建议，形成「自省→决策→执行→验证」的完整闭环
    elif "元自省决策" in intent or "系统自省" in intent or "meta self reflection" in intent.lower() or "self reflection decision" in intent.lower() or "自省增强" in intent or "智能决策分析" in intent or "决策自省" in intent or "元决策增强" in intent or "reflection" in intent.lower() and "meta" in intent.lower():
        print(f"[元进化系统自省与智能决策增强引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_self_reflection_intelligent_decision_engine.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--version"]
        elif "--status" in sys.argv or "检查" in intent or "状态" in intent:
            filtered_args = ["--status"]
        elif "--reflect" in sys.argv or "自省" in intent or "reflect" in intent.lower() or "决策自省" in intent:
            filtered_args = ["--reflect"]
        elif "--evaluate" in sys.argv or "评估" in intent or "evaluate" in intent.lower() or "效果评估" in intent:
            filtered_args = ["--evaluate"]
        elif "--suggest" in sys.argv or "建议" in intent or "suggest" in intent.lower() or "优化建议" in intent:
            filtered_args = ["--suggest"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--run" in sys.argv or "执行" in intent or "run" in intent.lower() or "自省闭环" in intent:
            filtered_args = ["--run"]
        else:
            # 默认显示驾驶舱数据
            filtered_args = ["--cockpit-data"]

        # 过滤掉意图关键词
        filter_words = ["元自省决策", "系统自省", "meta self reflection", "self reflection decision", "自省增强", "智能决策分析", "决策自省", "元决策增强"]
        filtered_args = [arg for arg in sys.argv[1:] if arg not in filter_words]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环元进化全链路智能编排与自主演进引擎（Round 597）- 将已有的元进化组件（自省596、决策555-556、验证553、健康554、跨维度594-595）统一编排，形成从自省→智能决策→自动执行→效果验证→持续优化的完整自主演进闭环。系统能够感知多引擎状态、统一编排决策、执行闭环、持续演进，实现真正的元进化全链路自主运行
    elif "元进化全链路" in intent or "全链路编排" in intent or "全链路演进" in intent or "full link orchestration" in intent.lower() or "meta full link" in intent.lower() or "全链路智能编排" in intent or "自主演进" in intent or "autonomous evolution" in intent.lower() or "编排引擎" in intent or "orchestration engine" in intent.lower() or "元进化编排" in intent or "全链路" in intent:
        print(f"[元进化全链路智能编排与自主演进引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_evolution_full_link_smart_orchestration_engine.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--version"]
        elif "--status" in sys.argv or "检查" in intent or "状态" in intent:
            filtered_args = ["--status"]
        elif "--sense" in sys.argv or "感知" in intent or "sense" in intent.lower() or "引擎状态" in intent:
            filtered_args = ["--sense"]
        elif "--decision" in sys.argv or "决策" in intent or "编排决策" in intent:
            filtered_args = ["--decision"]
        elif "--closed-loop" in sys.argv or "闭环" in intent or "closed loop" in intent.lower() or "演进" in intent:
            filtered_args = ["--closed-loop"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--run" in sys.argv or "执行" in intent or "运行" in intent or "run" in intent.lower() or "全链路运行" in intent:
            filtered_args = ["--run"]
        else:
            # 默认显示驾驶舱数据
            filtered_args = ["--cockpit-data"]

        # 过滤掉意图关键词
        filter_words = ["元进化全链路", "全链路编排", "全链路演进", "full link orchestration", "meta full link", "全链路智能编排", "自主演进", "autonomous evolution", "编排引擎", "orchestration engine", "元进化编排", "全链路"]
        filtered_args = [arg for arg in sys.argv[1:] if arg not in filter_words]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环元进化认知深度自省与递归优化引擎（Round 598）- 在 round 597 完成的元进化全链路智能编排引擎基础上，进一步构建让系统能够反思自身进化方法论本身的能力。系统不仅能执行进化，还能思考"我的进化方式是否正确"、"如何进化得更好"，实现「学会如何进化得更好」的递归优化
    elif "认知自省" in intent or "递归优化" in intent or "方法论反思" in intent or "cognition self reflection" in intent.lower() or "recursive optimizer" in intent.lower() or "meta cognition" in intent.lower() or "进化反思" in intent or "self reflection" in intent.lower() or "方法论优化" in intent or "认知深度" in intent:
        print(f"[元进化认知深度自省与递归优化引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_cognition_deep_self_reflection_recursive_optimizer_engine.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--version"]
        elif "--status" in sys.argv or "检查" in intent or "状态" in intent:
            filtered_args = ["--status"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--run" in sys.argv or "执行" in intent or "运行" in intent or "run" in intent.lower() or "分析" in intent or "自省" in intent or "反思" in intent:
            filtered_args = ["--run"]
        else:
            # 默认显示驾驶舱数据
            filtered_args = ["--cockpit-data"]

        # 过滤掉意图关键词
        filter_words = ["认知自省", "递归优化", "方法论反思", "cognition self reflection", "recursive optimizer", "meta cognition", "进化反思", "self reflection", "方法论优化", "认知深度"]
        filtered_args = [arg for arg in sys.argv[1:] if arg not in filter_words]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环元进化智慧自动提取与战略规划引擎（Round 599）- 在 round 598 完成的元进化认知深度自省基础上，进一步构建让系统能够从500+轮进化历史中自动提取可复用智慧、将智慧转化为战略规划输入、形成智慧驱动的自主战略规划能力
    elif "智慧提取" in intent or "战略规划" in intent or "wisdom extraction" in intent.lower() or "strategic planning" in intent.lower() or "元智慧" in intent or "智慧驱动" in intent or "智慧应用" in intent or "提取智慧" in intent or "智慧库" in intent:
        print(f"[元进化智慧自动提取与战略规划引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_wisdom_extraction_strategic_planning_engine.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--version"]
        elif "--status" in sys.argv or "检查" in intent or "状态" in intent:
            filtered_args = ["--status"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--run" in sys.argv or "执行" in intent or "运行" in intent or "run" in intent.lower() or "分析" in intent or "提取" in intent:
            filtered_args = ["--run"]
        else:
            # 默认显示驾驶舱数据
            filtered_args = ["--cockpit-data"]

        # 过滤掉意图关键词
        filter_words = ["智慧提取", "战略规划", "wisdom extraction", "strategic planning", "元智慧", "智慧驱动", "智慧应用", "提取智慧", "智慧库"]
        filtered_args = [arg for arg in sys.argv[1:] if arg not in filter_words]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环元进化主动创新涌现引擎（Round 600）- 在 round 599 完成的智慧提取引擎基础上，构建让系统能够基于智慧库主动发现创新机会、生成高价值创新假设、评估可行性并转化为进化任务的完整能力
    elif "元进化主动创新涌现" in intent or "创新涌现引擎" in intent or "meta emergence innovation" in intent.lower() or "emergence innovation" in intent.lower() or "主动创新涌现" in intent or "智慧驱动创新" in intent:
        print(f"[元进化主动创新涌现引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_emergence_innovation_engine.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--version"]
        elif "--status" in sys.argv or "检查" in intent or "状态" in intent:
            filtered_args = ["--status"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--run" in sys.argv or "执行" in intent or "运行" in intent or "run" in intent.lower() or "创新涌现" in intent or "发现机会" in intent:
            filtered_args = ["--run"]
        elif "--discover" in sys.argv or "发现" in intent:
            filtered_args = ["--discover"]
        elif "--generate" in sys.argv or "生成" in intent:
            filtered_args = ["--generate"]
        elif "--evaluate" in sys.argv or "评估" in intent:
            filtered_args = ["--evaluate"]
        else:
            # 默认显示驾驶舱数据
            filtered_args = ["--cockpit-data"]

        # 过滤掉意图关键词
        filter_words = ["元进化主动创新涌现", "创新涌现引擎", "meta emergence innovation", "emergence innovation", "主动创新涌现", "智慧驱动创新"]
        filtered_args_base = [arg for arg in sys.argv[1:] if arg not in filter_words]

        result = subprocess.run([sys.executable, script_path] + filtered_args + filtered_args_base, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)

    # 智能全场景进化环元进化创新价值自动实现与迭代深化引擎（Round 601）- 在 round 600 完成的元进化主动创新涌现引擎基础上，构建让系统能够自动执行创新假设、验证价值实现、持续迭代深化的完整创新价值闭环
    elif "创新价值自动实现" in intent or "价值自动实现" in intent or "创新价值实现" in intent or "价值迭代深化" in intent or "迭代深化" in intent or "创新闭环" in intent or "创新价值" in intent or "innovation value automated" in intent.lower() or "value iteration" in intent.lower() or "迭代深化引擎" in intent:
        print(f"[元进化创新价值自动实现与迭代深化引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_innovation_value_automated_execution_iteration_deepening_engine.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--version"]
        elif "--status" in sys.argv or "检查" in intent or "状态" in intent:
            filtered_args = ["--status"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--run" in sys.argv or "执行" in intent or "运行" in intent or "run" in intent.lower() or "价值实现" in intent:
            filtered_args = ["--run"]
        elif "--execute" in sys.argv or "执行任务" in intent:
            filtered_args = ["--execute"]
        elif "--verify" in sys.argv or "验证" in intent:
            filtered_args = ["--verify"]
        elif "--iterate" in sys.argv or "迭代" in intent:
            filtered_args = ["--iterate"]
        elif "--summary" in sys.argv or "摘要" in intent:
            filtered_args = ["--summary"]
        else:
            # 默认显示驾驶舱数据
            filtered_args = ["--cockpit-data"]

        # 过滤掉意图关键词
        filter_words = ["创新价值自动实现", "价值自动实现", "创新价值实现", "价值迭代深化", "迭代深化", "创新闭环", "创新价值", "innovation value automated", "value iteration", "迭代深化引擎"]
        filtered_args_base = [arg for arg in sys.argv[1:] if arg not in filter_words]

        result = subprocess.run([sys.executable, script_path] + filtered_args + filtered_args_base, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)

    # 智能全场景进化环主动创新假设自动生成与自涌现发现引擎（Round 582）- 在 round 581 完成的知识驱动自动化执行增强引擎基础上，构建让系统能够主动发现创新机会、生成创新假设、发现新的进化方向的引擎。让系统不仅能执行知识推理结果，还能主动思考"我可以进化什么新的方向"，实现从「被动执行知识推理结果」到「主动发现进化机会」的范式升级
    elif "创新假设" in intent or "假设生成" in intent or "innovation hypothesis" in intent.lower() or "hypothesis generation" in intent.lower() or "创新发现" in intent or "主动发现" in intent or "emergence discovery" in intent.lower() or "创新涌现" in intent or "自涌现" in intent or "创新机会" in intent:
        print(f"[主动创新假设自动生成与自涌现发现引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_innovation_hypothesis_emergence_engine.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--status"]
        elif "--status" in sys.argv or "检查" in intent or "状态" in intent:
            filtered_args = ["--status"]
        elif "--discover" in sys.argv or "发现" in intent or "探索" in intent:
            filtered_args = ["--discover"]
        elif "--list-hypotheses" in sys.argv or "列出假设" in intent or "假设列表" in intent:
            filtered_args = ["--list-hypotheses"]
        elif "--list-patterns" in sys.argv or "模式" in intent or "patterns" in intent.lower():
            filtered_args = ["--list-patterns"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        else:
            # 默认：显示引擎状态
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环创新假设自动验证与执行闭环引擎（Round 583）- 在 round 582 完成的创新假设自动生成与自涌现发现引擎基础上，构建让系统能够自动验证创新假设价值并执行的引擎。形成「假设生成→自动验证→执行→价值评估→迭代优化」的完整创新价值实现闭环。让系统不仅能生成创新假设，还能自动设计验证实验、执行验证、评估假设价值，实现从「有创新假设」到「真正验证并实现价值」的范式升级
    elif "假设验证" in intent or "验证假设" in intent or "hypothesis verification" in intent.lower() or "假设执行" in intent or "hypothesis execution" in intent.lower() or "创新闭环" in intent or "创新执行" in intent or "验证执行" in intent or "innovation closed loop" in intent.lower() or "假设价值" in intent or "价值验证" in intent or "迭代优化" in intent or "iteration optimization" in intent.lower() or "创新价值实现" in intent:
        print(f"[创新假设自动验证与执行闭环引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_innovation_hypothesis_verification_execution_engine.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--status"]
        elif "--status" in sys.argv or "检查" in intent or "状态" in intent:
            filtered_args = ["--status"]
        elif "--verify" in sys.argv or "验证" in intent or "运行" in intent or "执行" in intent or "完整" in intent or "full" in intent.lower():
            filtered_args = ["--verify"]
        elif "--list-verified" in sys.argv or "已验证" in intent or "验证列表" in intent:
            filtered_args = ["--list-verified"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        else:
            # 默认：显示引擎状态
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环价值驱动进化执行闭环引擎（Round 580）- 在 round 579 完成的元进化价值预测与战略投资决策增强引擎基础上，构建从投资策略到自动执行的完整闭环。让系统能够将投资决策转化为可执行任务、执行并追踪结果、反馈到决策优化，形成「预测→决策→执行→验证→优化」的完整闭环
    elif "价值驱动执行" in intent or "执行闭环" in intent or "投资执行" in intent or "价值执行" in intent or "value driven execution" in intent.lower() or "execution closed loop" in intent.lower() or "投资策略执行" in intent or "策略执行" in intent or "execution loop" in intent.lower() or "执行优化反馈" in intent or "执行效果评估" in intent or "价值反馈" in intent:
        print(f"[价值驱动进化执行闭环引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_value_driven_execution_closed_loop_engine.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--status"]
        elif "--status" in sys.argv or "检查" in intent or "状态" in intent:
            filtered_args = ["--status"]
        elif "--run" in sys.argv or "执行" in intent or "运行" in intent or "完整" in intent or "full" in intent.lower():
            filtered_args = ["--run"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--execute-cycle" in sys.argv or "执行周期" in intent:
            filtered_args = ["--execute-cycle"]
        elif "--tasks" in sys.argv or "任务" in intent:
            filtered_args = ["--tasks"]
        else:
            # 默认：显示引擎状态
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环知识图谱主动推理与前瞻性洞察生成引擎（round 605）
    elif "前瞻洞察生成" in intent or "洞察预测引擎" in intent or "insight prediction" in intent.lower() or "insight engine" in intent.lower() and "kg" in intent.lower():
        print(f"[知识图谱主动推理与前瞻性洞察生成引擎] 正在分析知识图谱并生成前瞻性洞察...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_kg_proactive_reasoning_insight_engine.py")
        cmd_args = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd_args:
            cmd_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环元进化知识图谱自涌现与主动创新引擎（Round 574）- 在 round 573 完成的价值实现闭环基础上，构建让系统能够从进化历史和知识图谱中主动涌现创新方向、生成创新假设、验证创新价值的能力，形成「价值驱动→知识涌现→主动创新」的完整闭环
    elif "知识图谱涌现" in intent or "知识涌现" in intent or "涌现创新" in intent or "knowledge emergence" in intent.lower() or "emergence innovation" in intent.lower() or "知识图谱创新" in intent or "创新涌现" in intent or "emergence" in intent.lower() and "创新" in intent or "涌现" in intent and "创新" in intent or "kg emergence" in intent.lower():
        print(f"[元进化知识图谱自涌现与主动创新引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_knowledge_graph_emergence_innovation_engine.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--status"]
        elif "--check" in sys.argv or "检查" in intent or "校验" in intent:
            filtered_args = ["--status"]
        elif "--run" in sys.argv or "执行" in intent or "运行" in intent or "完整" in intent or "full" in intent.lower():
            filtered_args = ["--run"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--discover" in sys.argv or "发现" in intent or "涌现" in intent:
            filtered_args = ["--discover"]
        elif "--generate" in sys.argv or "生成假设" in intent or "假设生成" in intent:
            filtered_args = ["--generate"]
        elif "--validate" in sys.argv or "验证" in intent:
            filtered_args = ["--validate"]
        else:
            # 默认：显示引擎状态
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环创新价值自动化实现与迭代深化引擎（Round 575）- 在 round 574 完成的元进化知识图谱自涌现与主动创新引擎基础上，构建让系统能够将验证通过的创新假设自动转化为可执行任务、追踪价值实现过程、持续迭代优化的能力，形成从「涌现→验证→执行→价值实现→迭代深化」的完整创新闭环
    elif "创新价值自动化" in intent or "创新自动化执行" in intent or "价值自动化实现" in intent or "创新迭代深化" in intent or "innovation value automated" in intent.lower() or "automated execution" in intent.lower() or "value realization" in intent.lower() or "创新执行" in intent or "自动化实现" in intent or "迭代深化" in intent or "innovation execution" in intent.lower() or "execution iteration" in intent.lower() or "价值实现追踪" in intent or "创新价值实现" in intent:
        print(f"[创新价值自动化实现与迭代深化引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_innovation_value_automated_execution_iteration_engine.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--version"]
        elif "--status" in sys.argv or "检查" in intent or "状态" in intent:
            filtered_args = ["--status"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--discover" in sys.argv or "发现" in intent:
            filtered_args = ["--discover"]
        elif "--track" in sys.argv or "追踪" in intent or "价值追踪" in intent:
            filtered_args = ["--track"]
        elif "--iterate" in sys.argv or "迭代" in intent or "深化" in intent:
            filtered_args = ["--iterate"]
        elif "--run" in sys.argv or "执行" in intent or "运行" in intent or "完整" in intent or "full" in intent.lower():
            filtered_args = ["--run"]
        else:
            # 默认：显示引擎状态
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)

    # 智能全场景进化环元进化系统自演进架构优化引擎 (Round 622)
    # 让系统能够主动评估自身进化架构与工作流效率，发现优化空间并自动生成改进方案，
    # 形成「架构自省→优化发现→安全执行→效果验证」的完整自演进闭环
    elif "元进化系统自演进" in intent or "元进化架构优化" in intent or "自演进架构" in intent or "self evolution architecture" in intent.lower() or "架构自省" in intent or "自演进引擎" in intent or "架构优化引擎" in intent or "进化架构优化" in intent or "系统自演进" in intent or "架构演进优化" in intent:
        print(f"[智能全场景进化环元进化系统自演进架构优化引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_system_self_evolution_architecture_optimizer.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["元进化系统自演进", "元进化架构优化", "自演进架构", "self evolution architecture", "架构自省", "自演进引擎", "架构优化引擎", "进化架构优化", "系统自演进", "架构演进优化"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环元进化自演进方案自动实施与持续优化引擎 (Round 623)
    # 基于 round 622 完成的元进化系统自演进架构优化引擎（架构自省评分87分，识别5个优化机会，生成3个优化方案）基础上，
    # 构建让系统能够自动实施优化方案并持续跟踪效果的增强能力
    elif "自演进实施" in intent or "优化实施" in intent or "方案执行" in intent or "自演进执行" in intent or "自演进方案" in intent or "方案自动实施" in intent or "自演进持续优化" in intent or "plan execution" in intent.lower() or "optimization execution" in intent.lower():
        print(f"[智能全场景进化环元进化自演进方案自动实施与持续优化引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_self_evolution_plan_execution_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["自演进实施", "优化实施", "方案执行", "自演进执行", "自演进方案", "方案自动实施", "自演进持续优化", "plan execution", "optimization execution"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环元进化集群分布式协作与跨实例知识共享引擎 (Round 624)
    # 基于 round 616 完成的元进化智能体集群协同优化引擎和 round 623 完成的自演进方案自动实施引擎基础上，
    # 构建让系统能够实现多实例分布式协作进化与跨实例知识实时共享的增强能力
    elif "分布式协作" in intent or "跨实例知识" in intent or "集群负载" in intent or "实例容错" in intent or "任务迁移" in intent or "distributed collaboration" in intent.lower() or "cluster" in intent.lower() or "知识共享" in intent or "跨实例" in intent or "集群协作" in intent or "多实例" in intent:
        print(f"[智能全场景进化环元进化集群分布式协作与跨实例知识共享引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_cluster_distributed_collaboration_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["分布式协作", "跨实例知识", "集群负载", "实例容错", "任务迁移", "distributed collaboration", "cluster", "知识共享", "跨实例", "集群协作", "多实例"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环元进化记忆深度整合与跨轮次智慧涌现引擎 (Round 625)
    # 基于 round 599 完成的智慧自动提取与战略规划引擎和 round 606 完成的元进化方法论自省与递归优化引擎基础上，
    # 构建让系统能够深度整合600+轮进化记忆、发现跨轮次隐藏模式、生成前瞻性战略洞察、实现智慧涌现的增强能力
    elif "记忆整合" in intent or "跨轮次" in intent or "智慧涌现" in intent or "模式发现" in intent or "memory integration" in intent.lower() or "wisdom emergence" in intent.lower() or "cross-round" in intent.lower() or "pattern discovery" in intent.lower() or "洞察生成" in intent or "前瞻洞察" in intent or "历史整合" in intent or "进化记忆" in intent or "记忆深度" in intent or "跨轮学习" in intent:
        print(f"[智能全场景进化环元进化记忆深度整合与跨轮次智慧涌现引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_memory_deep_integration_wisdom_emergence_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["记忆整合", "跨轮次", "智慧涌现", "模式发现", "memory integration", "wisdom emergence", "cross-round", "pattern discovery", "洞察生成", "前瞻洞察", "历史整合", "进化记忆", "记忆深度", "跨轮学习"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环元进化引擎精简优化与自我迭代引擎 (Round 626)
    # 基于 round 625 完成的元进化记忆深度整合与跨轮次智慧涌现引擎基础上，
    # 构建让系统能够自动评估已创建的60+个元进化引擎、识别功能重叠或低效引擎、生成并执行优化合并方案的增强能力
    elif "引擎精简" in intent or "引擎优化" in intent or "引擎盘点" in intent or "引擎合并" in intent or "engine consolidation" in intent.lower() or "engine optimize" in intent.lower() or "engine inventory" in intent.lower() or "engine merge" in intent.lower() or "引擎效能" in intent or "engine efficiency" in intent.lower() or "重叠分析" in intent or "功能重叠" in intent or "overlap analysis" in intent.lower() or "engine cleanup" in intent.lower() or "引擎清理" in intent:
        print(f"[智能全场景进化环元进化引擎精简优化与自我迭代引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_engine_consolidation_optimizer.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["引擎精简", "引擎优化", "引擎盘点", "引擎合并", "engine consolidation", "engine optimize", "engine inventory", "engine merge", "引擎效能", "engine efficiency", "重叠分析", "功能重叠", "overlap analysis", "engine cleanup", "引擎清理"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环元进化引擎协同效能深度预测与预防性优化引擎 (Round 627)
    # 基于 round 626 完成的元进化引擎精简优化与自我迭代引擎（已识别58个引擎、231对重叠引擎、35个低效引擎、生成5个优化方案）基础上，
    # 构建让系统能够深度预测引擎间协同效能、预判协同瓶颈、主动部署预防性优化措施的增强能力
    # 实现从「被动优化」（问题发生后分析）升级到「主动预防」（问题发生前预测并避免）
    elif "协同预测" in intent or "瓶颈预警" in intent or "预防性优化" in intent or "协同效能预测" in intent or "collaboration prediction" in intent.lower() or "bottleneck warning" in intent.lower() or "preventive optimization" in intent.lower() or "efficiency prediction" in intent.lower() or "协同瓶颈" in intent or "效能趋势" in intent or "趋势预测" in intent or "efficiency trend" in intent.lower() or "协同效能" in intent or "collaboration efficiency" in intent.lower():
        print(f"[智能全场景进化环元进化引擎协同效能深度预测与预防性优化引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_collaboration_efficiency_prediction_prevention_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["协同预测", "瓶颈预警", "预防性优化", "协同效能预测", "collaboration prediction", "bottleneck warning", "preventive optimization", "efficiency prediction", "协同瓶颈", "效能趋势", "趋势预测", "efficiency trend", "协同效能", "collaboration efficiency", "引擎协同"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环元进化引擎健康预测与预防性自愈深度增强引擎 (Round 628)
    # 基于 round 627 完成的元进化引擎协同效能深度预测与预防性优化引擎（预测协同瓶颈、部署预防措施）基础上，
    # 构建让系统能够深度预测引擎健康状态、预判潜在故障、主动部署预防性自愈措施的增强能力
    # 实现从「被动修复」（问题发生后诊断）升级到「主动预防」（问题发生前预测并自愈）
    elif "健康预测" in intent or "预防性自愈" in intent or "故障预判" in intent or "engine health prediction" in intent.lower() or "preventive self-healing" in intent.lower() or "fault prediction" in intent.lower() or "引擎健康" in intent or "自愈引擎" in intent or "预防自愈" in intent:
        print(f"[智能全场景进化环元进化引擎健康预测与预防性自愈深度增强引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_engine_health_prediction_preventive_self_healing_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["健康预测", "预防性自愈", "故障预判", "engine health prediction", "preventive self-healing", "fault prediction", "引擎健康", "自愈引擎", "预防自愈"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环元进化自我诊断优化闭环增强引擎 (Round 629)
    # 基于 round 628 完成的元进化引擎健康预测与预防性自愈深度增强引擎（健康预测、故障预判、预防性自愈）、
    # round 618 完成的元进化系统深度健康诊断与智能修复闭环增强引擎、round 620 完成的元进化执行效能实时优化引擎、
    # round 622 完成的元进化系统自演进架构优化引擎基础上，构建让系统能够自动整合多引擎诊断结果、生成综合优化方案并自动执行的增强能力
    # 实现从「单一引擎优化」升级到「多引擎协同优化」
    elif "自我诊断优化" in intent or "多维诊断" in intent or "综合优化" in intent or "闭环优化" in intent or "self diagnosis" in intent.lower() or "self-diagnosis" in intent.lower() or "comprehensive optimization" in intent.lower() or "multi-dimensional diagnosis" in intent.lower() or "closed loop" in intent.lower() or "自诊断" in intent or "诊断优化" in intent or "诊断闭环" in intent:
        print(f"[智能全场景进化环元进化自我诊断优化闭环增强引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_self_diagnosis_optimization_closed_loop_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["自我诊断优化", "多维诊断", "综合优化", "闭环优化", "self diagnosis", "self-diagnosis", "comprehensive optimization", "multi-dimensional diagnosis", "closed loop", "自诊断", "诊断优化", "诊断闭环"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # round 630: 智能全场景进化环元进化主动自我进化规划引擎 - 让系统能够主动分析当前进化架构的成熟度、评估已有60+引擎的能力组合价值、识别下一个高价值进化方向、生成自驱动的进化路线图
    # 在 round 621 价值创造引擎、round 622 架构优化引擎、round 625 记忆整合引擎、round 629 自我诊断优化引擎基础上，构建让系统能够主动规划自身进化方向的增强能力
    # 实现从「被动优化」升级到「主动规划」
    elif "自我进化规划" in intent or "主动规划" in intent or "进化路线图" in intent or "架构成熟度" in intent or "self evolution planning" in intent.lower() or "proactive planning" in intent.lower() or "roadmap" in intent.lower() or "规划引擎" in intent or "主动自我进化" in intent or "进化方向识别" in intent or "自我规划" in intent:
        print(f"[智能全场景进化环元进化主动自我进化规划引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_self_evolution_planning_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["自我进化规划", "主动规划", "进化路线图", "架构成熟度", "self evolution planning", "proactive planning", "roadmap", "规划引擎", "主动自我进化", "进化方向识别", "自我规划"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # round 631: 智能全场景进化环元进化方法论有效性评估与持续优化引擎 - 让系统能够评估自身进化方法论的有效性、识别低效模式、自动生成优化建议，形成持续改进进化方法的递归闭环
    # 在 round 630 完成的主动自我进化规划引擎基础上，构建让系统能够评估自身进化方法论有效性的深度增强能力
    # 实现从「被动优化方法论」升级到「主动评估并优化方法论」
    elif "方法论有效性" in intent or "方法论评估" in intent or "进化方法论" in intent or "methodology effectiveness" in intent.lower() or "methodology evaluation" in intent.lower() or "methodology assessment" in intent.lower() or "评估进化方法" in intent or "方法论优化" in intent or "优化方法论" in intent or "low efficiency" in intent.lower() or "inefficiency pattern" in intent.lower() or "低效模式" in intent:
        print(f"[智能全场景进化环元进化方法论有效性评估与持续优化引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_methodology_effectiveness_evaluation_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["方法论有效性", "方法论评估", "进化方法论", "methodology effectiveness", "methodology evaluation", "methodology assessment", "评估进化方法", "方法论优化", "优化方法论", "low efficiency", "inefficiency pattern", "低效模式"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # round 632: 智能全场景进化环元进化方法论自动学习与自适应优化引擎 - 基于 round 631 完成的元进化方法论有效性评估引擎，构建让系统能够自动学习方法论优化建议的有效性并将学习结果应用到未来进化决策的增强能力
    # 实现「评估→建议→执行→学习→应用」的完整方法论优化闭环
    # 注意：此引擎需放在其他"自适应优化"相关引擎之前，以确保"方法论学习"能正确匹配
    elif "方法论学习" in intent or "策略调整" in intent or "methodology learning" in intent.lower() or "strategy adjustment" in intent.lower() or "方法论自适应" in intent or "学习有效性" in intent or "有效性学习" in intent or ("方法论" in intent and "优化" in intent) or ("methodology" in intent.lower() and "learning" in intent.lower()):
        print(f"[智能全场景进化环元进化方法论自动学习与自适应优化引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_methodology_auto_learning_adaptive_optimizer_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["方法论学习", "策略调整", "methodology learning", "strategy adjustment", "方法论自适应", "学习有效性", "有效性学习", "方法论优化", "优化方法论"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # round 644: 智能全场景进化环元进化自适应学习与策略自动优化引擎 V2 - 在 round 551/606/632 的方法论学习基础上，构建更深层次的自适应学习能力
    # 让系统能够从进化历史中自动提取有效模式、基于执行反馈自动调整策略、实现进化方法的自我进化
    elif "自适应学习" in intent or "元学习" in intent or "策略优化" in intent or "adaptive learning" in intent.lower() or "meta learning" in intent.lower() or "strategy optimization" in intent.lower() or "参数调整" in intent or "模式提取" in intent or "进化模式" in intent:
        print(f"[智能全场景进化环元进化自适应学习与策略自动优化引擎 V2 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_adaptive_learning_strategy_optimizer_v2.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["自适应学习", "元学习", "策略优化", "adaptive learning", "meta learning", "strategy optimization", "参数调整", "模式提取", "进化模式"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # round 634: 智能全场景进化环创新建议自动验证与价值优先级排序引擎 - 基于 round 633 知识图谱引擎（已发现388条待执行创新建议）基础上，构建让系统能够自动验证创新建议价值并智能排序优先级的增强能力
    # 实现「发现→验证→排序→优化→执行」的完整创新价值实现闭环
    elif "创新验证" in intent or "价值排序" in intent or "优先级" in intent or "innovation verify" in intent.lower() or "value priority" in intent.lower() or "priority rank" in intent.lower() or "价值评估" in intent or "创新价值" in intent or "价值评分" in intent:
        print(f"[智能全场景进化环创新建议自动验证与价值优先级排序引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_innovation_value_verification_priority_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["创新验证", "价值排序", "优先级", "innovation verify", "value priority", "priority rank", "价值评估", "创新价值", "价值评分"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # round 635: 智能全场景进化环创新建议自动执行与迭代深化引擎 - 基于 round 633 知识图谱发现创新建议和 round 634 价值验证排序基础上，构建让系统能够自动将高优先级创新建议转化为可执行任务、执行验证、迭代优化的完整闭环
    # 实现「发现→验证→排序→执行→迭代」的完整创新价值实现闭环
    elif "创新执行" in intent or "执行创新" in intent or "创新迭代" in intent or "innovation execution" in intent.lower() or "execute innovation" in intent.lower() or "innovation iterate" in intent.lower() or "执行建议" in intent or "任务执行" in intent or "执行任务" in intent or "创新转化" in intent:
        print(f"[智能全场景进化环创新建议自动执行与迭代深化引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_innovation_execution_iteration_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["创新执行", "执行创新", "创新迭代", "innovation execution", "execute innovation", "innovation iterate", "执行建议", "任务执行", "执行任务", "创新转化"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # round 636: 智能全场景进化环元进化结果预测与自适应策略深度优化引擎 - 基于 round 635 创新执行迭代引擎和历史进化数据，构建让系统能够基于历史进化结果训练预测模型、预测不同进化方向的预期效果、主动选择最优进化路径的能力
    # 实现「学习历史→预测未来→主动选择→优化执行」的完整闭环
    elif "进化预测" in intent or "结果预测" in intent or "策略优化" in intent or "evolution prediction" in intent.lower() or "result prediction" in intent.lower() or "strategy optimization" in intent.lower() or "预测效果" in intent or "自适应策略" in intent or "路径选择" in intent or "预测未来" in intent or "效果预测" in intent:
        print(f"[智能全场景进化环元进化结果预测与自适应策略深度优化引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_evolution_result_prediction_adaptive_strategy_optimizer_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["进化预测", "结果预测", "策略优化", "evolution prediction", "result prediction", "strategy optimization", "预测效果", "自适应策略", "路径选择", "预测未来", "效果预测"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # round 637: 智能全场景进化环元进化预测准确性验证与自适应优化引擎 - 基于 round 636 预测模型，构建让系统能够自动验证预测模型准确性、持续优化预测算法、形成预测→验证→优化的完整闭环
    elif "预测验证" in intent or "预测准确性" in intent or "prediction accuracy" in intent.lower() or "预测优化" in intent or "accuracy verification" in intent.lower() or "预测校准" in intent or "置信度校准" in intent or "参数优化" in intent or "model calibration" in intent.lower():
        print(f"[智能全场景进化环元进化预测准确性验证与自适应优化引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_prediction_accuracy_verification_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["预测验证", "预测准确性", "prediction accuracy", "预测优化", "accuracy verification", "预测校准", "置信度校准", "参数优化", "model calibration"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # round 638: 智能全场景进化环元进化预测-验证-优化三角闭环深度协同引擎 - 基于 round 635（创新执行）、round 636（预测策略）、round 637（预测验证）三个引擎，构建让系统能够将三个引擎深度协同，形成三角闭环的持续自增强能力
    # 实现「验证→预测优化→执行调整→验证」的三角闭环协同
    elif "三角闭环" in intent or "协同优化" in intent or "闭环协同" in intent or "triangular" in intent.lower() or "closed loop" in intent.lower() or "collaboration" in intent.lower() or "三角协同" in intent or "自增强" in intent or "反馈优化" in intent:
        print(f"[智能全场景进化环元进化预测-验证-优化三角闭环深度协同引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_triangular_closed_loop_collaboration_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["三角闭环", "协同优化", "闭环协同", "triangular", "closed loop", "collaboration", "三角协同", "自增强", "反馈优化"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # round 639: 智能全场景进化环元进化目标自主设定与价值驱动闭环引擎 - 让系统能够基于三角闭环引擎(635-638)的能力，主动分析自身状态、评估进化价值、设定进化目标，形成从「被动执行」到「主动设定目标并驱动执行」的范式升级
    # 实现「状态分析→价值评估→目标设定→驱动执行」的完整闭环
    elif "目标设定" in intent or "自主目标" in intent or "价值目标" in intent or "目标驱动" in intent or "goal setting" in intent.lower() or "autonomous goal" in intent.lower() or "value goal" in intent.lower() or "目标自主" in intent or "目标融合" in intent or "跨维目标" in intent or "目标闭环" in intent:
        print(f"[智能全场景进化环元进化目标自主设定与价值驱动闭环引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_goal_autonomous_setting_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--run"]
        # 过滤掉意图关键词
        filter_words = ["目标设定", "自主目标", "价值目标", "目标驱动", "goal setting", "autonomous goal", "value goal", "目标自主", "目标融合", "跨维目标", "目标闭环"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--run"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # round 640: 智能全场景进化环元进化执行过程实时监控与自适应调整引擎 - 填补 round 639 目标设定后的执行监控与动态调整闭环，让系统能够实时追踪目标执行进度、根据执行反馈自动调整策略、形成「设定→执行→监控→调整」的完整闭环
    # 实现「目标→执行→监控→调整」的完整闭环
    elif "执行监控" in intent or "执行追踪" in intent or "自适应调整" in intent or "execution monitoring" in intent.lower() or "execution tracking" in intent.lower() or "adaptive adjustment" in intent.lower() or "执行调整" in intent or "执行反馈" in intent or "进度追踪" in intent or "目标监控" in intent or "execution adjust" in intent.lower() or "目标追踪" in intent or "监控调整" in intent or "execution monitor" in intent.lower():
        print(f"[智能全场景进化环元进化执行过程实时监控与自适应调整引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_execution_monitoring_adaptive_adjustment_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--run"]
        # 过滤掉意图关键词
        filter_words = ["执行监控", "执行追踪", "自适应调整", "execution monitoring", "execution tracking", "adaptive adjustment", "执行调整", "执行反馈", "进度追踪", "目标监控", "execution adjust", "目标追踪", "监控调整", "execution monitor"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--run"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # round 633: 智能全场景进化环元进化知识图谱动态推理与主动创新发现引擎 - 基于 round 625 记忆整合和 round 632 方法论学习，构建让系统能够构建动态进化的知识图谱、进行图谱实时推理、主动发现创新机会并生成可执行创新建议
    # 实现「构建→推理→发现→建议→演化」的完整知识图谱创新闭环
    elif "知识图谱" in intent or "图谱推理" in intent or "创新发现" in intent or "knowledge graph" in intent.lower() or "kg" in intent.lower() or "图谱动态" in intent or "kg reasoning" in intent.lower() or "innovation discovery" in intent.lower() or "graph reasoning" in intent.lower() or "图谱分析" in intent or "kg reasoning" in intent.lower():
        print(f"[智能全场景进化环元进化知识图谱动态推理与主动创新发现引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_knowledge_graph_dynamic_reasoning_innovation_discovery_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["知识图谱", "图谱推理", "创新发现", "knowledge graph", "kg", "图谱动态", "kg reasoning", "innovation discovery", "graph reasoning", "图谱分析"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环元进化系统自涌现深度增强引擎（Round 576）- 在 round 575 完成的创新价值自动化实现与迭代深化引擎基础上，进一步增强系统的自涌现能力。让系统能够基于已有能力组合、进化历史数据、知识图谱，自动涌现新的创新方向、生成高价值创新假设、形成自驱动创新涌现的深度增强能力
    elif "元涌现" in intent or "自涌现" in intent or "创新涌现" in intent or "能力涌现" in intent or "meta emergence" in intent.lower() or "system emergence" in intent.lower() or "emergence deep" in intent.lower() or "元进化系统" in intent or "系统自涌现" in intent or "涌现增强" in intent or "涌现引擎" in intent or "涌现分析" in intent:
        print(f"[元进化系统自涌现深度增强引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_system_emergence_deep_enhancement_engine.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--version"]
        elif "--status" in sys.argv or "检查" in intent or "状态" in intent:
            filtered_args = ["--status"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--discover" in sys.argv or "发现" in intent:
            filtered_args = ["--discover"]
        elif "--run" in sys.argv or "执行" in intent or "运行" in intent or "分析" in intent or "完整" in intent or "full" in intent.lower():
            filtered_args = ["--run"]
        else:
            # 默认：显示引擎状态
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环元进化主动创新引擎（Round 570）- 在 round 569 完成的元进化自我优化引擎基础上，构建让系统主动发现创新机会、生成创新假设、验证创新价值的闭环，形成「理解→优化→创新」的递归增强，让系统不仅能优化已知问题，还能主动创造新价值
    elif "主动创新" in intent or "元进化主动创新" in intent or "meta active innovation" in intent.lower() or "innovation discovery" in intent.lower() or "创新发现" in intent or "创新假设" in intent or "创新验证" in intent or "创新价值" in intent or "创新引擎" in intent or "主动创新引擎" in intent:
        print(f"[元进化主动创新引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_active_innovation_engine.py")

        # 确定要执行的命令
        if "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--version"]
        elif "--check" in sys.argv or "检查" in intent or "校验" in intent:
            filtered_args = ["--check"]
        elif "--discover" in sys.argv or "发现创新" in intent or "发现" in intent:
            filtered_args = ["--discover"]
        elif "--hypotheses" in sys.argv or "生成假设" in intent or "创新假设" in intent:
            filtered_args = ["--hypotheses"]
        elif "--validate" in sys.argv or "验证创新" in intent or "创新验证" in intent:
            filtered_args = ["--validate"]
        elif "--run" in sys.argv or "执行创新" in intent or "运行创新" in intent:
            filtered_args = ["--run"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        else:
            # 默认：显示引擎状态
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环跨轮次价值实现追踪与量化增强引擎（Round 559）- 在 round 558 完成的元进化自我反思与深度自省引擎基础上，进一步将自省结果量化为可衡量的价值指标，实现「自省→量化→价值反馈→优化决策」的完整价值驱动进化闭环
    elif "价值追踪" in intent or "价值量化" in intent or "价值反馈" in intent or "价值驱动" in intent or "value tracking" in intent.lower() or "value quantum" in intent.lower() or "value realization" in intent.lower() or "价值实现" in intent or "跨轮次价值" in intent or "价值增强" in intent:
        print(f"[跨轮次价值实现追踪与量化增强引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_value_realization_tracking_quantum_engine.py")

        # 确定要执行的命令
        if "--track" in sys.argv or "追踪" in intent or "执行追踪" in intent:
            filtered_args = ["--track"]
        elif "--feedback" in sys.argv or "反馈" in intent or "生成反馈" in intent:
            filtered_args = ["--feedback"]
        elif "--summary" in sys.argv or "摘要" in intent or "汇总" in intent:
            filtered_args = ["--summary"]
        elif "--cockpit" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit"]
        elif "--check" in sys.argv or "检查" in intent or "校验" in intent:
            filtered_args = ["--check"]
        elif "--version" in sys.argv or "版本" in intent:
            filtered_args = ["--version"]
        else:
            # 默认：显示驾驶舱数据
            filtered_args = ["--cockpit"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环元进化智能决策自动策略生成与执行增强引擎（Round 494）- 在 round 474 认知-价值-元进化融合和 round 475/481 自我进化效能分析基础上，增强元进化智能决策能力，实现深度分析→智能决策→自动执行→效果验证闭环
    elif "元进化决策" in intent or "自动策略" in intent or "元决策" in intent or "智能策略生成" in intent or "meta decision" in intent.lower() or "auto strategy" in intent.lower() or "strategy generation" in intent.lower() or "meta evolution decision" in intent.lower() or "智能决策" in intent:
        print(f"[元进化智能决策自动策略生成与执行增强引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_decision_auto_execution_engine.py")

        # 确定要执行的命令
        if "--status" in sys.argv or "状态" in intent:
            filtered_args = ["--status"]
        elif "--run" in sys.argv or "运行" in intent or "执行" in intent or "完整循环" in intent:
            filtered_args = ["--run"]
        elif "--dry-run" in sys.argv or "模拟" in intent or "模拟运行" in intent:
            filtered_args = ["--run", "--dry-run"]
        elif "--analyze" in sys.argv or "分析" in intent:
            filtered_args = ["--analyze"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--history" in sys.argv or "历史" in intent:
            filtered_args = ["--history"]
        elif "--execute" in sys.argv:
            filtered_args = ["--execute"]
            if len(sys.argv) > sys.argv.index("--execute") + 1:
                next_arg = sys.argv[sys.argv.index("--execute") + 1]
                if not next_arg.startswith("--"):
                    filtered_args.append(next_arg)
        else:
            # 默认：显示状态
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环自我进化元认知深度优化引擎（Round 495）- 在 round 494 的元进化智能决策引擎基础上，进一步增强自我进化的元认知深度优化能力。主动分析进化过程质量、评估元进化策略有效性、生成认知优化反馈，形成更深入的自我反思与递归优化闭环
    elif "元认知深度优化" in intent or "自我反思" in intent or "元认知优化" in intent or "meta cognition" in intent.lower() or "deep reflection" in intent.lower() or "自我进化反思" in intent or "认知反馈" in intent or "自我反思优化" in intent:
        print(f"[自我进化元认知深度优化引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_self_evolution_meta_cognition_deep_optimization_engine.py")

        # 确定要执行的命令
        if "--status" in sys.argv or "状态" in intent:
            filtered_args = ["--status"]
        elif "--run" in sys.argv or "运行" in intent or "执行" in intent or "完整循环" in intent:
            filtered_args = ["--run"]
        elif "--dry-run" in sys.argv or "模拟" in intent or "模拟运行" in intent:
            filtered_args = ["--run", "--dry-run"]
        elif "--analyze-quality" in sys.argv or "分析质量" in intent or "进化质量" in intent:
            filtered_args = ["--analyze-quality"]
        elif "--evaluate-strategy" in sys.argv or "评估策略" in intent or "策略评估" in intent:
            filtered_args = ["--evaluate-strategy"]
        elif "--generate-feedback" in sys.argv or "生成反馈" in intent or "认知反馈" in intent:
            filtered_args = ["--generate-feedback"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--history" in sys.argv or "历史" in intent:
            filtered_args = ["--history"]
        else:
            # 默认：显示状态
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环元认知-元进化深度集成引擎（Round 496）- 在 round 494 元进化智能决策引擎和 round 495 元认知深度优化引擎基础上，将元认知分析结果直接驱动策略生成和参数调整，形成认知→决策→执行→验证→认知更新完整闭环
    elif "元认知决策" in intent or "认知驱动策略" in intent or "元认知元进化" in intent or "元认知集成" in intent or "cognition decision" in intent.lower() or "cognition driven" in intent.lower() or "cognitive strategy" in intent.lower() or "元认知驱动" in intent or "认知驱动" in intent or ("元认知" in intent and "决策" in intent) or ("meta cognition" in intent.lower() and "decision" in intent.lower()) or "cognition_meta_integration" in intent.lower() or "元认知-元进化" in intent:
        print(f"[元认知-元进化深度集成引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_cognition_meta_decision_integration_engine.py")

        # 确定要执行的命令
        if "--status" in sys.argv or "状态" in intent:
            filtered_args = ["--status"]
        elif "--analyze" in sys.argv or "分析" in intent:
            filtered_args = ["--analyze"]
        elif "--run" in sys.argv or "执行闭环" in intent or "运行闭环" in intent:
            filtered_args = ["--run"]
        elif "--dry-run" in sys.argv or "模拟" in intent or "dry run" in intent.lower():
            filtered_args = ["--dry-run"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--history" in sys.argv or "历史" in intent:
            filtered_args = ["--history"]
        else:
            # 默认：显示状态
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环元进化内部健康诊断与自愈深度增强引擎（Round 497, 498增强）- 自动诊断进化引擎间的依赖问题、识别内部健康风险、智能生成修复方案并自动执行；增强版支持健康预警、趋势预测、预防性自愈
    elif "元进化健康诊断" in intent or "内部健康诊断" in intent or "引擎健康自愈" in intent or "meta health diagnosis" in intent.lower() or "engine health" in intent.lower() or "meta self healing" in intent.lower() or "自愈引擎" in intent or "健康自愈" in intent or ("元进化" in intent and "诊断" in intent) or ("meta" in intent.lower() and "health" in intent.lower()) or ("元进化" in intent and "自愈" in intent) or "健康预警" in intent or "预防性自愈" in intent or "预警增强" in intent or "健康趋势" in intent or "趋势预测" in intent or "preventive" in intent.lower() or "prediction" in intent.lower():
        print(f"[元进化内部健康诊断与自愈引擎（增强版）] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_evolution_internal_health_diagnosis_self_healing_engine.py")

        # 确定要执行的命令
        if "--status" in sys.argv or "状态" in intent:
            filtered_args = ["--status"]
        elif "--diagnose" in sys.argv or "诊断" in intent:
            filtered_args = ["--diagnose"]
        elif "--repair" in sys.argv or "修复" in intent or "自动修复" in intent:
            filtered_args = ["--repair"]
        elif "--dry-run" in sys.argv or "模拟" in intent or "dry run" in intent.lower():
            filtered_args = ["--repair", "--dry-run"]
        elif "--run" in sys.argv or "完整闭环" in intent or "运行闭环" in intent or "full loop" in intent.lower():
            filtered_args = ["--run"]
        elif "--auto-repair" in sys.argv:
            filtered_args = ["--run", "--auto-repair"]
        elif "--health-score" in sys.argv or "健康评分" in intent or "评分" in intent:
            filtered_args = ["--health-score"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--history" in sys.argv or "历史" in intent:
            filtered_args = ["--history"]
        elif "--predict-trend" in sys.argv or "预测趋势" in intent or "趋势预测" in intent or "predict" in intent.lower() or "trend prediction" in intent.lower():
            filtered_args = ["--predict-trend"]
        elif "--preventive-strategies" in sys.argv or "预防策略" in intent or "预防性策略" in intent or "preventive strategy" in intent.lower():
            filtered_args = ["--preventive-strategies"]
        elif "--execute-prevention" in sys.argv or "执行预防" in intent or "预防执行" in intent or "execute prevention" in intent.lower():
            filtered_args = ["--execute-prevention"]
        elif "--check-warn" in sys.argv or "预警" in intent or "warn" in intent.lower() or "warning" in intent.lower():
            filtered_args = ["--check-warn"]
        else:
            # 默认：显示状态
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环代码理解与架构优化引擎（Round 499/500）- 大规模分析70+进化引擎代码结构、识别重复代码模式、发现可复用模块、生成优化建议、自动修复
    elif "代码分析" in intent or "代码理解" in intent or "架构优化" in intent or "code analysis" in intent.lower() or "code understanding" in intent.lower() or "architecture optimization" in intent.lower() or "代码优化" in intent or "架构分析" in intent or "pattern" in intent.lower() or "模式发现" in intent or "代码模式" in intent or "代码架构" in intent or "代码自动修复" in intent or "自动修复代码" in intent or "代码质量优化" in intent or "code auto fix" in intent.lower() or "代码修复" in intent or "代码自优化" in intent:
        print(f"[代码理解与架构优化引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_code_understanding_architecture_optimizer.py")

        # 确定要执行的命令
        if "--analyze" in sys.argv or "分析" in intent:
            filtered_args = ["--analyze"]
        elif "--status" in sys.argv or "状态" in intent:
            filtered_args = ["--status"]
        elif "--find-patterns" in sys.argv or "模式" in intent or "重复" in intent:
            filtered_args = ["--find-patterns"]
        elif "--discover-reusable" in sys.argv or "可复用" in intent or "复用" in intent:
            filtered_args = ["--discover-reusable"]
        elif "--suggestions" in sys.argv or "建议" in intent or "优化建议" in intent:
            filtered_args = ["--suggestions"]
        elif "--report" in sys.argv or "报告" in intent or "架构报告" in intent:
            filtered_args = ["--report"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--detect-issues" in sys.argv or "检测问题" in intent or "质量问题" in intent:
            filtered_args = ["--detect-issues"]
        elif "--auto-fix" in sys.argv or "自动修复" in intent or "auto fix" in intent.lower() or "代码自动修复" in intent:
            filtered_args = ["--auto-fix"]
        elif "--dry-run" in sys.argv or "模拟运行" in intent:
            filtered_args = ["--auto-fix", "--dry-run"]
        elif "--optimization-status" in sys.argv or "优化状态" in intent:
            filtered_args = ["--optimization-status"]
        else:
            # 默认：运行完整分析
            filtered_args = ["--analyze"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)

    # 智能全场景进化环创新假设自动生成与验证引擎（Round 501）- 主动发现优化机会、生成创新性假设、验证假设价值，形成从被动修复到主动创新的范式升级
    elif "创新假设" in intent or "假设生成" in intent or "创新假设" in intent or "hypothesis generation" in intent.lower() or "假设验证" in intent or "验证假设" in intent or "创新发现" in intent or "主动创新" in intent or "假设执行" in intent or "创新假设生成" in intent or "生成创新假设" in intent:
        print(f"[创新假设自动生成与验证引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_innovation_hypothesis_generation_verification_engine.py")

        # 确定要执行的命令 - 更具体的关键词优先
        if "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--status" in sys.argv or "状态" in intent:
            filtered_args = ["--status"]
        elif "--discover" in sys.argv or "发现机会" in intent or "发现创新" in intent or "创新机会" in intent:
            filtered_args = ["--discover"]
        elif "--run" in sys.argv or "完整周期" in intent or "运行周期" in intent:
            filtered_args = ["--run"]
            if "--max-hypotheses" in sys.argv:
                idx = sys.argv.index("--max-hypotheses")
                if idx + 1 < len(sys.argv):
                    filtered_args.extend(["--max-hypotheses", sys.argv[idx + 1]])
        elif "--generate" in sys.argv or "生成假设" in intent or ("假设" in intent and "驾驶舱" not in intent and "状态" not in intent and "完整周期" not in intent):
            filtered_args = ["--generate"]
            if "--max-hypotheses" in sys.argv:
                idx = sys.argv.index("--max-hypotheses")
                if idx + 1 < len(sys.argv):
                    filtered_args.extend(["--max-hypotheses", sys.argv[idx + 1]])
            else:
                filtered_args.extend(["--max-hypotheses", "3"])
        elif "--validate" in sys.argv:
            if "--hypothesis" in sys.argv:
                idx = sys.argv.index("--hypothesis")
                if idx + 1 < len(sys.argv):
                    filtered_args = ["--validate", sys.argv[idx + 1]]
            else:
                filtered_args = ["--status"]
        else:
            filtered_args = ["--run", "--max-hypotheses", "3"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)

    # 智能全场景进化环创新方案智能执行与深度优化引擎 (Round 505) - 在 round 504 跨引擎深度融合创新实现引擎基础上，进一步增强创新方案的智能执行能力，将高价值创新方案自动转化为可执行代码、自动执行优化、验证优化效果
    elif "创新方案执行" in intent or "方案智能执行" in intent or "创新优化执行" in intent or "代码生成执行创新" in intent or "方案转代码" in intent or "代码执行创新" in intent:
        print(f"[智能全场景进化环创新方案智能执行与深度优化引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_innovation_execution_optimizer_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["创新方案执行", "方案智能执行", "创新优化执行", "代码生成执行创新", "方案转代码", "代码执行创新"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环创新投资回报自动评估与策略优化引擎 (Round 506) - 在 round 505 完成的创新方案执行引擎基础上，进一步增强投资回报自动评估能力，自动分析各进化方向的投入产出比、智能选择最高效的进化路径、持续优化进化策略
    elif "投资回报" in intent or "ROI" in intent or "策略优化" in intent or "价值评估" in intent or "进化投资" in intent or "回报评估" in intent or "roi" in intent.lower() or "return on investment" in intent.lower() or "投资回报优化" in intent or "创新回报" in intent or "价值优化" in intent and "进化" in intent:
        print(f"[智能全场景进化环创新投资回报自动评估与策略优化引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_roi_auto_assessment_engine.py")

        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["投资回报", "ROI", "策略优化", "价值评估", "进化投资", "回报评估", "投资回报优化", "创新回报", "价值优化"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]

        # 确定要执行的命令
        if "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--trends" in sys.argv or "趋势" in intent or "trend" in intent.lower():
            filtered_args = ["--trends"]
        elif "--predict" in sys.argv:
            idx = sys.argv.index("--predict")
            if idx + 1 < len(sys.argv):
                filtered_args = ["--predict", sys.argv[idx + 1]]
        elif "--optimize" in sys.argv or "优化" in intent or "optimize" in intent.lower():
            filtered_args = ["--optimize"]
        elif "--recommendations" in sys.argv or "建议" in intent or "recommendation" in intent.lower():
            filtered_args = ["--recommendations"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环跨引擎统一元知识图谱深度推理引擎 (Round 507) - 在已有知识索引与推理能力基础上，构建统一的元知识图谱，实现跨引擎知识的深度语义关联与创新性推理发现
    elif "元知识图谱" in intent or "知识图谱推理" in intent or "深度推理" in intent or "知识推理" in intent or "meta knowledge" in intent.lower() or "knowledge graph" in intent.lower() or "kg reasoning" in intent.lower() or ("图谱" in intent and "推理" in intent) or ("知识" in intent and "关联" in intent) or ("跨引擎" in intent and "知识" in intent):
        print(f"[智能全场景进化环跨引擎统一元知识图谱深度推理引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_knowledge_graph_reasoning_engine.py")

        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["元知识图谱", "知识图谱推理", "深度推理", "知识推理", "meta knowledge", "knowledge graph", "kg reasoning", "图谱", "关联", "跨引擎知识"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]

        # 确定要执行的命令
        if "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--build-kg" in sys.argv or "构建图谱" in intent or "build kg" in intent.lower():
            filtered_args = ["--build-kg"]
        elif "--reasoning" in sys.argv or "推理" in intent or "reasoning" in intent.lower():
            filtered_args = ["--reasoning"]
        elif "--discover" in sys.argv or "发现" in intent or "discover" in intent.lower() or "创新" in intent:
            filtered_args = ["--discover"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环基于代码理解的跨引擎自动修复与深度自优化增强引擎 (Round 508) - 基于代码理解能力，对跨引擎进行自动问题诊断、智能修复方案生成、自动执行修复、效果验证，形成完整的「分析→诊断→修复→验证→优化」闭环
    elif "跨引擎自动修复" in intent or "跨引擎自优化" in intent or "引擎自动修复" in intent or "引擎自优化" in intent or "cross engine" in intent.lower() and "repair" in intent.lower() or "cross engine" in intent.lower() and "optim" in intent.lower() or "auto repair" in intent.lower() or "self optimize" in intent.lower() or "自优化" in intent or "自动修复" in intent and "跨引擎" in intent or "跨引擎修复" in intent:
        print(f"[智能全场景进化环基于代码理解的跨引擎自动修复与深度自优化增强引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_cross_engine_auto_repair_self_optimizer_engine.py")

        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["跨引擎自动修复", "跨引擎自优化", "引擎自动修复", "引擎自优化", "cross engine", "auto repair", "self optimize", "自优化", "自动修复", "跨引擎修复"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]

        # 确定要执行的命令
        if "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--analyze" in sys.argv or "分析" in intent or "analyze" in intent.lower():
            filtered_args = ["--analyze"]
        elif "--detect" in sys.argv or "检测" in intent or "detect" in intent.lower() or "问题" in intent:
            filtered_args = ["--detect"]
        elif "--optimize" in sys.argv or "优化" in intent or "optimize" in intent.lower() or "自优化" in intent:
            filtered_args = ["--optimize"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环多引擎协同智能决策深度集成引擎（Round 509）- 聚合多个进化引擎的决策信息、统一权重计算、智能冲突仲裁、决策执行路径优化，形成真正的「多引擎协同智能决策」闭环
    elif "多引擎协同决策" in intent or "协同决策" in intent or "多引擎决策" in intent or "决策集成" in intent or "multi engine" in intent.lower() and "decision" in intent.lower() or "collaborative decision" in intent.lower() or "决策深度集成" in intent:
        print(f"[智能全场景进化环多引擎协同智能决策深度集成引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_multi_engine_collaborative_decision_integration_engine.py")

        # 解析命令参数
        filtered_args = []
        if "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--status" in sys.argv or "状态" in intent:
            filtered_args = ["--status"]
        elif "--decide" in sys.argv or "决策" in intent or "decide" in intent.lower():
            filtered_args = ["--decide"]
        elif "--collect" in sys.argv or "收集" in intent or "collect" in intent.lower():
            filtered_args = ["--collect"]
        elif "--weights" in sys.argv or "权重" in intent or "weights" in intent.lower():
            filtered_args = ["--weights"]
        elif "--path" in sys.argv or "路径" in intent or "path" in intent.lower():
            filtered_args = ["--path"]
        else:
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环决策-执行-学习完整闭环深度集成引擎（Round 514）- 将决策执行引擎（round 510）和决策学习优化引擎（round 511）深度集成，实现从决策到执行到学习的完整数据流转、决策效果的实时反馈、学习结果直接驱动下一轮决策，形成「决策→执行→学习→优化决策」的持续改进闭环
    elif "决策执行学习闭环" in intent or "完整闭环" in intent or "决策执行集成" in intent or "decision execution learning" in intent.lower() or "decision execution integration" in intent.lower() or "闭环集成" in intent or "学习闭环" in intent or "decision learning loop" in intent.lower() or "决策闭环" in intent or "执行学习闭环" in intent:
        print(f"[智能全场景进化环决策-执行-学习完整闭环深度集成引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_decision_execution_learning_integration_engine.py")

        # 解析命令参数
        filtered_args = []
        if "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--status" in sys.argv or "状态" in intent:
            filtered_args = ["--status"]
        elif "--recent" in sys.argv:
            filtered_args = ["--recent"]
            # 获取数量参数
            for i, arg in enumerate(sys.argv):
                if arg == "--recent" and i + 1 < len(sys.argv):
                    try:
                        filtered_args.append(str(int(sys.argv[i + 1])))
                    except ValueError:
                        filtered_args.append("5")
                    break
        elif "最近" in intent:
            import re
            match = re.search(r"最近(\d+)", intent)
            if match:
                filtered_args = ["--recent", match.group(1)]
            else:
                filtered_args = ["--recent", "5"]
        elif "--execute-loop" in sys.argv or "执行闭环" in intent or "execute loop" in intent.lower():
            filtered_args = ["--execute-loop", "{}"]
        elif "--generate-insights" in sys.argv or "生成洞察" in intent or "generate insights" in intent.lower() or "洞察" in intent:
            filtered_args = ["--generate-insights"]
        elif "--apply-learning" in sys.argv or "应用学习" in intent or "apply learning" in intent.lower():
            filtered_args = ["--apply-learning", "{}"]
        else:
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环跨轮次决策-执行-学习深度集成增强引擎（Round 515）- 将跨轮次学习记忆引擎（round 512/513）与决策-执行-学习闭环（round 514）深度集成，实现跨轮次的经验传承、策略复用和递归优化，形成真正的「代际进化」能力
    elif "跨轮次闭环" in intent or "决策传承" in intent or "执行复用" in intent or "跨轮学习" in intent or "cross round" in intent.lower() or "cross-round" in intent.lower() or "cross_round" in intent.lower() or "代际进化" in intent or "inheritance" in intent.lower() or "experience inheritance" in intent.lower():
        print(f"[智能全场景进化环跨轮次决策-执行-学习深度集成增强引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_cross_round_del_execution_learning_engine.py")

        # 解析命令参数
        filtered_args = []
        if "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--status" in sys.argv or "状态" in intent:
            filtered_args = ["--status"]
        elif "--recent" in sys.argv:
            filtered_args = ["--recent"]
            # 获取数量参数
            for i, arg in enumerate(sys.argv):
                if arg == "--recent" and i + 1 < len(sys.argv):
                    try:
                        filtered_args.append(str(int(sys.argv[i + 1])))
                    except ValueError:
                        filtered_args.append("5")
                    break
        elif "最近" in intent:
            import re
            match = re.search(r"最近(\d+)", intent)
            if match:
                filtered_args = ["--recent", match.group(1)]
            else:
                filtered_args = ["--recent", "5"]
        elif "--execute-loop" in sys.argv or "执行闭环" in intent or "execute loop" in intent.lower():
            filtered_args = ["--execute-loop", "{}"]
        elif "--generate-insights" in sys.argv or "生成洞察" in intent or "generate insights" in intent.lower() or "洞察" in intent:
            filtered_args = ["--generate-insights"]
        elif "--apply-learning" in sys.argv or "应用学习" in intent or "apply learning" in intent.lower():
            filtered_args = ["--apply-learning", "{}"]
        elif "--extract-experiences" in sys.argv or "提取经验" in intent or "extract experiences" in intent.lower():
            filtered_args = ["--extract-experiences"]
        elif "--value-assessment" in sys.argv or "价值评估" in intent or "value assessment" in intent.lower():
            filtered_args = ["--value-assessment"]
        else:
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环多引擎协同智能调度深度优化引擎（Round 517）- 让系统能够智能调度多个进化引擎，实现更高效的资源利用和协同工作，包括任务智能分发、负载均衡优化、执行顺序动态调整、调度效率实时分析等核心功能
    elif "多引擎调度" in intent or "引擎协同调度" in intent or "智能调度优化" in intent or "调度优化" in intent or "multi engine schedule" in intent.lower() or "engine schedule optimizer" in intent.lower() or "多引擎协同优化" in intent or "调度效率" in intent or "任务分发" in intent or "执行顺序优化" in intent or "load balance optimization" in intent.lower():
        print(f"[智能全场景进化环多引擎协同智能调度深度优化引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_multi_engine_collaboration_scheduling_optimizer.py")

        # 解析命令参数
        filtered_args = []
        if "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--status" in intent or "状态" in intent:
            filtered_args = ["status"]
        elif "--dispatch" in sys.argv or "分发" in intent or "dispatch" in intent.lower():
            filtered_args = ["dispatch"]
        elif "--optimize" in sys.argv or "优化" in intent:
            filtered_args = ["optimize"]
        elif "--efficiency" in sys.argv or "效率" in intent or "efficiency" in intent.lower():
            filtered_args = ["efficiency"]
        elif "--order" in sys.argv or "顺序" in intent or "order" in intent.lower():
            filtered_args = ["order"]
        else:
            filtered_args = ["status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环自动化性能基准测试与回归检测引擎（Round 518）- 让系统能够追踪进化环自身的执行效率变化、自动发现性能回归、预测优化机会，实现从被动响应性能问题到主动预防的范式升级
    elif "性能基准" in intent or "回归检测" in intent or "性能回归" in intent or "performance benchmark" in intent.lower() or "regression detection" in intent.lower() or "性能趋势" in intent or "performance trend" in intent.lower() or "基准测试" in intent or "性能分析" in intent:
        print(f"[智能全场景进化环自动化性能基准测试与回归检测引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_performance_benchmark_regression_engine.py")

        # 解析命令参数
        filtered_args = []
        if "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--status" in sys.argv or "状态" in intent:
            filtered_args = ["--status"]
        elif "--establish-baseline" in sys.argv or "建立基准" in intent or "establish baseline" in intent.lower():
            filtered_args = ["--establish-baseline"]
        elif "--detect-regression" in sys.argv or "检测回归" in intent or "detect regression" in intent.lower():
            filtered_args = ["--detect-regression"]
        elif "--predict-trend" in sys.argv or "预测趋势" in intent or "predict trend" in intent.lower():
            filtered_args = ["--predict-trend"]
        elif "--identify-optimizations" in sys.argv or "识别优化" in intent or "identify optimizations" in intent.lower():
            filtered_args = ["--identify-optimizations"]
        elif "--run" in sys.argv or "运行" in intent or "完整分析" in intent:
            filtered_args = ["--run"]
        else:
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环预防性维护自动化深度集成引擎（Round 520）- 在 round 519 完成的性能趋势预测与预防性优化增强引擎基础上，进一步将预防性优化与元进化引擎深度集成，实现完全无人值守的自动化预防性维护
    # 注意：此引擎必须放在 round 519 引擎之前，因为 round 519 的关键词会匹配"预防性"
    elif "预防性维护自动化" in intent or "自动化预防" in intent or "维护自动化" in intent or "preventive maintenance automation" in intent.lower() or "maintenance automation" in intent.lower() or "自动维护" in intent or "预防维护" in intent:
        print(f"[智能全场景进化环预防性维护自动化深度集成引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_preventive_maintenance_automation_integration_engine.py")

        # 解析命令参数
        filtered_args = []
        if "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--status" in sys.argv or "状态" in intent:
            filtered_args = ["--status"]
        elif "--run" in sys.argv or "运行" in intent or "执行维护" in intent:
            filtered_args = ["--run"]
        elif "--check-trigger" in sys.argv or "检查触发" in intent or "check trigger" in intent.lower():
            filtered_args = ["--check-trigger"]
        elif "--configure" in sys.argv or "配置" in intent or "configure" in intent.lower():
            filtered_args = ["--configure"]
            if "--performance-threshold" in sys.argv:
                idx = sys.argv.index("--performance-threshold")
                if idx + 1 < len(sys.argv):
                    filtered_args.extend(["--performance-threshold", sys.argv[idx + 1]])
            if "--trend-threshold" in sys.argv:
                idx = sys.argv.index("--trend-threshold")
                if idx + 1 < len(sys.argv):
                    filtered_args.extend(["--trend-threshold", sys.argv[idx + 1]])
            if "--health-threshold" in sys.argv:
                idx = sys.argv.index("--health-threshold")
                if idx + 1 < len(sys.argv):
                    filtered_args.extend(["--health-threshold", sys.argv[idx + 1]])
            if "--auto-trigger" in sys.argv:
                idx = sys.argv.index("--auto-trigger")
                if idx + 1 < len(sys.argv):
                    filtered_args.extend(["--auto-trigger", sys.argv[idx + 1]])
        else:
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环性能趋势预测与预防性优化增强引擎（Round 519）- 在 round 518 完成的性能基准测试与回归检测引擎基础上，进一步增强趋势预测能力，实现从「检测回归」到「预测趋势→预防性优化」的完整闭环
    elif "性能趋势预测" in intent or "预防性优化" in intent or "趋势预防" in intent or "performance trend prediction" in intent.lower() or "prevention" in intent.lower() or "预防性" in intent:
        print(f"[智能全场景进化环性能趋势预测与预防性优化增强引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_performance_trend_prediction_prevention_engine.py")

        # 解析命令参数
        filtered_args = []
        if "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--status" in sys.argv or "状态" in intent:
            filtered_args = ["--status"]
        elif "--predict-trend" in sys.argv or "预测趋势" in intent or "predict trend" in intent.lower():
            filtered_args = ["--predict-trend"]
        elif "--execute-prevention" in sys.argv or "执行预防" in intent or "execute prevention" in intent.lower():
            filtered_args = ["--execute-prevention"]
        elif "--verify-effect" in sys.argv or "验证效果" in intent or "verify effect" in intent.lower():
            filtered_args = ["--verify-effect"]
        elif "--run" in sys.argv or "运行" in intent or "完整分析" in intent:
            filtered_args = ["--run"]
        else:
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环决策自动执行与动态调整引擎（Round 510）- 将多引擎协同智能决策结果自动转化为可执行动作、智能调整执行参数、动态处理异常、验证执行效果，形成从「智能决策→自动执行→动态调整→效果验证」的完整闭环
    elif "决策执行" in intent or "自动执行" in intent or "执行决策" in intent or "decision execution" in intent.lower() or "auto execute decision" in intent.lower() or "决策动态调整" in intent or "decision auto" in intent.lower():
        print(f"[智能全场景进化环决策自动执行与动态调整引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_decision_auto_execution_engine.py")

        # 解析命令参数
        filtered_args = []
        if "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--status" in sys.argv or "状态" in intent:
            filtered_args = ["--status"]
        elif "--load-decisions" in sys.argv or "加载决策" in intent or "load decisions" in intent.lower():
            filtered_args = ["--load-decisions"]
        elif "--execute" in sys.argv or "执行" in intent:
            # 尝试获取决策ID
            decision_id = None
            if "--execute" in sys.argv:
                idx = sys.argv.index("--execute")
                if idx + 1 < len(sys.argv):
                    decision_id = sys.argv[idx + 1]
            if decision_id:
                filtered_args = ["--execute", decision_id]
            else:
                filtered_args = ["--status"]
        elif "--report" in sys.argv or "报告" in intent or "report" in intent.lower():
            # 尝试获取决策ID
            decision_id = None
            if "--report" in sys.argv:
                idx = sys.argv.index("--report")
                if idx + 1 < len(sys.argv):
                    decision_id = sys.argv[idx + 1]
            if decision_id:
                filtered_args = ["--report", decision_id]
            else:
                filtered_args = ["--status"]
        else:
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环决策执行结果学习与深度优化引擎（Round 511）- 从决策执行结果中自动学习、智能分析执行模式、生成优化建议并自动执行优化，形成从「决策→执行→学习→优化」的完整闭环。这是 round 510 完成的决策自动执行引擎的后续增强
    elif "决策学习" in intent or "执行学习" in intent or "结果学习" in intent or "decision learning" in intent.lower() or "执行优化" in intent or "decision optimization" in intent.lower() or "学习优化" in intent or "学习与优化" in intent or "执行结果分析" in intent or "决策分析" in intent:
        print(f"[智能全场景进化环决策执行结果学习与深度优化引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_decision_learning_optimizer_engine.py")

        # 解析命令参数
        filtered_args = []
        if "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--status" in sys.argv or "状态" in intent:
            filtered_args = ["--status"]
        elif "--collect" in sys.argv or "收集" in intent or "collect" in intent.lower():
            filtered_args = ["--collect"]
        elif "--analyze" in sys.argv or "分析" in intent or "analyze" in intent.lower():
            filtered_args = ["--analyze"]
        elif "--suggest" in sys.argv or "建议" in intent or "suggest" in intent.lower():
            filtered_args = ["--suggest"]
        elif "--apply" in sys.argv or "应用" in intent or "apply" in intent.lower():
            filtered_args = ["--apply"]
        elif "--full-cycle" in sys.argv or "完整循环" in intent or "full cycle" in intent.lower():
            filtered_args = ["--full-cycle"]
        else:
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环跨轮次长期学习记忆引擎（Round 512）- 在 round 511 完成的决策执行结果学习引擎基础上，进一步增强跨轮次的长期学习记忆能力。让系统能够长期记忆存储关键学习成果、自动从历史进化中提取学习数据、基于上下文智能检索和复用历史学习成果、评估记忆复用效果并持续优化
    elif "长期学习记忆" in intent or "长期记忆" in intent or "跨轮次学习" in intent or "跨轮记忆" in intent or "long term learning" in intent.lower() or "long term memory" in intent.lower() or "cross round learning" in intent.lower() or "learning memory" in intent or "记忆引擎" in intent:
        print(f"[智能全场景进化环跨轮次长期学习记忆引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_long_term_learning_memory_engine.py")

        # 解析命令参数
        filtered_args = []
        if "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--status" in sys.argv or "状态" in intent:
            filtered_args = ["--status"]
        elif "--collect" in sys.argv or "收集" in intent or "collect" in intent.lower():
            filtered_args = ["--collect"]
        elif "--store" in sys.argv or "存储" in intent or "store" in intent.lower():
            filtered_args = ["--store"]
        elif "--retrieve" in sys.argv or "检索" in intent or "retrieve" in intent.lower():
            filtered_args = ["--retrieve"]
            # 尝试获取检索关键词
            for i, arg in enumerate(sys.argv):
                if arg in ["--retrieve", "检索"] and i + 1 < len(sys.argv):
                    filtered_args.append(sys.argv[i + 1])
                    break
        elif "--full-cycle" in sys.argv or "完整循环" in intent or "full cycle" in intent.lower():
            filtered_args = ["--full-cycle"]
        elif "--patterns" in sys.argv or "模式" in intent or "patterns" in intent.lower():
            filtered_args = ["--patterns"]
            # 尝试获取上下文关键词
            for i, arg in enumerate(sys.argv):
                if arg in ["--patterns", "模式"] and i + 1 < len(sys.argv):
                    filtered_args.append(sys.argv[i + 1])
                    break
        else:
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环跨轮次学习记忆深度增强引擎（Round 513）- 在 round 512 完成的长期学习记忆引擎基础上，进一步增强跨轮次的学习记忆能力。实现跨时间窗口知识整合（跨月/季/年的学习成果聚合）、记忆衰减与强化机制（重要知识强化，过时知识淡化）、基于当前上下文智能检索相关经验
    elif "跨轮次学习记忆深度增强" in intent or "跨轮次学习增强" in intent or "学习记忆增强" in intent or "记忆深度增强" in intent or "cross round learning enhanced" in intent.lower() or "enhanced learning memory" in intent.lower() or "学习记忆深度" in intent or "记忆强化" in intent or "记忆衰减" in intent or "时间窗口" in intent or "time window" in intent.lower() or "上下文感知" in intent or "context aware" in intent.lower():
        print(f"[智能全场景进化环跨轮次学习记忆深度增强引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_cross_round_learning_memory_engine.py")

        # 解析命令参数
        filtered_args = []
        if "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--status" in intent or "状态" in intent:
            filtered_args = ["--status"]
        elif "--migrate" in sys.argv or "迁移" in intent or "migrate" in intent.lower():
            filtered_args = ["--migrate"]
        elif "--decay" in sys.argv or "衰减" in intent or "decay" in intent.lower():
            filtered_args = ["--decay"]
        elif "--decay-dry-run" in sys.argv:
            filtered_args = ["--decay-dry-run"]
        elif "--aggregate" in sys.argv:
            filtered_args = ["--aggregate"]
            # 获取聚合类型
            for i, arg in enumerate(sys.argv):
                if arg == "--aggregate" and i + 1 < len(sys.argv):
                    filtered_args.append(sys.argv[i + 1])
                    break
        elif "monthly" in intent.lower() or "月度" in intent:
            filtered_args = ["--aggregate", "monthly"]
        elif "quarterly" in intent.lower() or "季度" in intent:
            filtered_args = ["--aggregate", "quarterly"]
        elif "yearly" in intent.lower() or "年度" in intent:
            filtered_args = ["--aggregate", "yearly"]
        elif "--integrate" in sys.argv or "整合" in intent or "integrate" in intent.lower():
            filtered_args = ["--integrate"]
        elif "--retrieve" in sys.argv or "检索" in intent or "retrieve" in intent.lower():
            filtered_args = ["--retrieve"]
            # 尝试获取检索关键词
            for i, arg in enumerate(sys.argv):
                if arg in ["--retrieve", "检索"] and i + 1 < len(sys.argv):
                    filtered_args.append(sys.argv[i + 1])
                    break
        elif "--full-cycle" in sys.argv or "完整循环" in intent or "full cycle" in intent.lower():
            filtered_args = ["--full-cycle"]
        else:
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环创新验证结果自动执行与价值实现引擎（Round 502）- 将验证通过的创新假设自动转化为可执行任务、智能评估执行价值、自动执行创新方案、追踪价值实现
    # 排除"价值实现预测"以避免与 Round 516 引擎冲突
    elif ("创新执行" in intent or "价值实现" in intent or "执行验证" in intent or "创新实现" in intent or "假设执行" in intent or "验证执行" in intent or "value realization" in intent.lower() or "execute innovation" in intent.lower() or "创新价值" in intent or "创新任务" in intent or "实现创新" in intent or "创新方案执行" in intent or "方案执行" in intent) and "价值实现预测" not in intent:
        print(f"[创新验证结果自动执行与价值实现引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_innovation_value_realization_engine.py")

        # 确定要执行的命令 - 更具体的关键词优先
        if "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--status" in sys.argv or "状态" in intent:
            filtered_args = ["--status"]
        elif "--collect-hypotheses" in sys.argv or "收集假设" in intent or "已验证假设" in intent:
            filtered_args = ["--collect-hypotheses"]
        elif "--evaluate" in sys.argv or "评估价值" in intent or "执行评估" in intent or "价值评估" in intent:
            filtered_args = ["--evaluate"]
            if "--hypothesis" in sys.argv:
                idx = sys.argv.index("--hypothesis")
                if idx + 1 < len(sys.argv):
                    filtered_args = ["--evaluate", sys.argv[idx + 1]]
        elif "--generate-task" in sys.argv or "生成任务" in intent or "任务生成" in intent:
            filtered_args = ["--generate-task"]
            if "--hypothesis" in sys.argv:
                idx = sys.argv.index("--hypothesis")
                if idx + 1 < len(sys.argv):
                    filtered_args = ["--generate-task", sys.argv[idx + 1]]
        elif "--execute-task" in sys.argv or "执行任务" in intent or "任务执行" in intent:
            filtered_args = ["--execute-task"]
            if "--task" in sys.argv:
                idx = sys.argv.index("--task")
                if idx + 1 < len(sys.argv):
                    filtered_args = ["--execute-task", sys.argv[idx + 1]]
            if "--dry-run" in sys.argv or "干运行" in intent:
                filtered_args.append("--dry-run")
        elif "--track-value" in sys.argv or "追踪价值" in intent or "价值追踪" in intent or "实现追踪" in intent:
            filtered_args = ["--track-value"]
            if "--task" in sys.argv:
                idx = sys.argv.index("--task")
                if idx + 1 < len(sys.argv):
                    filtered_args = ["--track-value", sys.argv[idx + 1]]
            if "--metrics" in sys.argv:
                idx = sys.argv.index("--metrics")
                if idx + 1 < len(sys.argv):
                    filtered_args.extend(["--metrics", sys.argv[idx + 1]])
        elif "--run" in sys.argv or "完整周期" in intent or "运行周期" in intent or "执行周期" in intent:
            filtered_args = ["--run"]
            if "--dry-run" in sys.argv or "干运行" in intent:
                filtered_args.append("--dry-run")
        else:
            # 默认：获取状态
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)

    # 智能全场景进化环执行策略自优化深度增强引擎（Round 449）- 自动分析引擎执行效果、识别协作低效模式、智能生成并执行优化策略
    elif "策略优化" in intent or "执行优化" in intent or "自优化" in intent or "优化策略" in intent or "strategy optimization" in intent.lower() or "execution optimization" in intent.lower() or "self-optimization" in intent.lower() or "optimize strategy" in intent.lower() or "策略自优化" in intent or "执行策略优化" in intent:
        print(f"[执行策略自优化深度增强引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_execution_strategy_self_optimizer.py")

        # 确定要执行的命令
        if "--stats" in sys.argv:
            filtered_args = ["--stats"]
        elif "--cycle" in sys.argv or "完整优化" in intent or "优化周期" in intent:
            filtered_args = ["--cycle"]
        elif "--analyze" in sys.argv or "分析" in intent:
            filtered_args = ["--analyze"]
            if "--engine" in sys.argv:
                idx = sys.argv.index("--engine")
                if idx + 1 < len(sys.argv):
                    filtered_args.extend(["--engine", sys.argv[idx + 1]])
        elif "--identify" in sys.argv or "识别" in intent or "模式" in intent:
            filtered_args = ["--identify"]
        elif "--generate" in sys.argv or "生成策略" in intent or "生成优化" in intent:
            filtered_args = ["--generate"]
        elif "--execute" in sys.argv:
            filtered_args = ["--execute"]
            if len(sys.argv) > sys.argv.index("--execute") + 1:
                next_arg = sys.argv[sys.argv.index("--execute") + 1]
                if not next_arg.startswith("--"):
                    filtered_args.append(next_arg)
        elif "--verify" in sys.argv or "验证" in intent:
            filtered_args = ["--verify"]
        else:
            # 默认：显示统计信息
            filtered_args = ["--stats"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环执行策略自优化与进化驾驶舱深度集成引擎（Round 450）- 将执行策略自优化能力与进化驾驶舱深度集成，实现可视化展示和驾驶舱控制
    elif "驾驶舱优化" in intent or "优化驾驶舱" in intent or "优化集成" in intent or "策略驾驶舱" in intent or "cockpit optimization" in intent.lower() or "optimization cockpit" in intent.lower() or "strategy cockpit" in intent.lower() or "optimization integration" in intent.lower() or "驾驶舱集成" in intent or "策略集成" in intent:
        print(f"[执行策略自优化与进化驾驶舱深度集成引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_strategy_cockpit_integration_engine.py")

        # 确定要执行的命令
        if "--dashboard" in sys.argv or "仪表盘" in intent or "dashboard" in intent.lower():
            filtered_args = ["--dashboard"]
        elif "--status" in sys.argv or "状态" in intent:
            filtered_args = ["--status"]
        elif "--summary" in sys.argv or "摘要" in intent:
            filtered_args = ["--summary"]
        elif "--viz" in sys.argv or "可视化" in intent:
            filtered_args = ["--viz"]
        elif "--trigger" in sys.argv or "触发" in intent:
            filtered_args = ["--trigger"]
        elif "--history" in sys.argv or "历史" in intent:
            filtered_args = ["--history"]
        elif "--trend" in sys.argv or "趋势" in intent:
            filtered_args = ["--trend", "response_time"]
        elif "--push" in sys.argv or "推送" in intent:
            filtered_args = ["--push"]
        else:
            # 默认：显示仪表盘数据
            filtered_args = ["--dashboard"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环进化系统自诊断与深度自愈增强引擎（Round 451）- 自动诊断100+进化引擎运行状态、识别性能瓶颈、生成并执行修复策略
    elif "系统自诊断" in intent or "自诊断" in intent or "深度自愈" in intent or "诊断自愈" in intent or "健康诊断" in intent or "system diagnosis" in intent.lower() or "self diagnosis" in intent.lower() or "self-healing" in intent.lower() or "health diagnosis" in intent.lower() or "自愈" in intent or "self healing" in intent.lower() or "预测诊断" in intent or "predictive diagnosis" in intent.lower():
        print(f"[进化系统自诊断与深度自愈增强引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_system_diagnosis_self_healing_enhanced_engine.py")

        # 确定要执行的命令
        if "--diagnose" in sys.argv or "诊断" in intent:
            filtered_args = ["--diagnose"]
        elif "--level" in sys.argv:
            # 传递诊断级别
            filtered_args = ["--diagnose", "--level", "deep"]
        elif "--repair" in sys.argv or "修复" in intent or "自动修复" in intent:
            filtered_args = ["--repair"]
        elif "--predict" in sys.argv or "预测" in intent:
            filtered_args = ["--predict"]
        elif "--cockpit" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower() or "状态" in intent:
            filtered_args = ["--cockpit"]
        elif "--history" in sys.argv or "历史" in intent:
            filtered_args = ["--history"]
        else:
            # 默认：运行标准诊断
            filtered_args = ["--diagnose"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环智能预警与主动干预深度集成引擎（Round 452）- 将主动预警与自愈能力深度集成，形成预测→预警→自动干预→自愈验证的完整闭环
    elif "预警干预" in intent or "主动干预" in intent or "预警集成" in intent or "干预引擎" in intent or "warning intervention" in intent.lower() or "预警执行" in intent or "预警自愈" in intent:
        print(f"[智能预警与主动干预深度集成引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_warning_intervention_deep_integration_engine.py")

        # 确定要执行的命令
        if "--analyze" in sys.argv or "分析预警" in intent:
            filtered_args = ["--analyze"]
        elif "--intervention" in sys.argv or "干预" in intent:
            filtered_args = ["--intervention"]
        elif "--cycle" in sys.argv or "闭环" in intent or "预警干预闭环" in intent:
            filtered_args = ["--cycle"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        else:
            # 默认：分析预警
            filtered_args = ["--analyze"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环进化价值实现追踪与自动优化引擎（Round 453）- 在预警与干预能力基础上，增强价值量化追踪与自动优化能力
    # 排除"价值实现预测"以避免与 Round 516 引擎冲突
    elif ("价值实现追踪" in intent or "价值自动优化" in intent or "价值优化" in intent or "价值追踪" in intent or "value optimization" in intent.lower() or "value tracking" in intent.lower() or "价值分析" in intent or "价值评估" in intent) and "价值实现预测" not in intent:
        print(f"[进化价值实现追踪与自动优化引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_value_realization_optimization_engine.py")

        # 确定要执行的命令
        if "--status" in sys.argv or "状态" in intent:
            filtered_args = ["--status"]
        elif "--track" in sys.argv or "追踪" in intent:
            filtered_args = ["--track"]
        elif "--quantify" in sys.argv or "量化" in intent:
            filtered_args = ["--quantify"]
        elif "--suggestions" in sys.argv or "建议" in intent or "优化建议" in intent:
            filtered_args = ["--suggestions"]
        elif "--auto-execute" in sys.argv or "自动执行" in intent or "执行优化" in intent:
            filtered_args = ["--auto-execute"]
        elif "--verify" in sys.argv or "验证" in intent or "效果" in intent:
            filtered_args = ["--verify"]
        elif "--predict" in sys.argv or "预测" in intent:
            filtered_args = ["--predict"]
        elif "--cycle" in sys.argv or "闭环" in intent or "自动循环" in intent:
            filtered_args = ["--cycle"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        else:
            # 默认：获取状态
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景深度认知与自主意识增强引擎（Round 454）- 增强深度认知与自主意识能力，实现自我反思、认知评估、认知优化策略生成
    elif "认知增强" in intent or "自主意识" in intent or "自我反思" in intent or "认知评估" in intent or "意识增强" in intent or "cognition" in intent.lower() or "awareness" in intent.lower() or "self reflection" in intent.lower() or "cognitive" in intent.lower() or "deep cognition" in intent.lower():
        print(f"[深度认知与自主意识增强引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_deep_cognition_awareness_engine.py")

        # 确定要执行的命令
        if "--reflect" in sys.argv or "自我反思" in intent or "self reflect" in intent.lower():
            filtered_args = ["--reflect"]
        elif "--evaluate" in sys.argv or "评估" in intent or "evaluate" in intent.lower() or "认知质量" in intent:
            filtered_args = ["--evaluate"]
        elif "--optimize" in sys.argv or "优化" in intent or "optimize" in intent.lower() or "策略" in intent:
            filtered_args = ["--optimize"]
        elif "--awareness" in sys.argv or "意识" in intent or "awareness" in intent.lower():
            filtered_args = ["--awareness"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--all" in sys.argv or "全部" in intent or "all" in intent.lower():
            filtered_args = ["--all"]
        else:
            # 默认：获取状态
            filtered_args = []

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景认知驱动自动决策与执行闭环引擎（Round 455）- 将深度认知引擎的评估结果自动应用到进化决策过程中，基于认知质量评估生成优化决策，并自动执行决策形成验证闭环
    elif "认知决策" in intent or "驱动决策" in intent or "自动决策" in intent or "认知执行" in intent or "cognition decision" in intent.lower() or "cognition driven" in intent.lower() or "decision execution" in intent.lower() or "cognitive decision" in intent.lower() or "认知驱动" in intent or "决策闭环" in intent or "decision loop" in intent.lower() or "cognition loop" in intent.lower() or "认知驱动决策" in intent:
        print(f"[认知驱动自动决策与执行闭环引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_cognition_driven_decision_execution_engine.py")

        # 确定要执行的命令
        if "--collect" in sys.argv or "收集" in intent or "collect" in intent.lower():
            filtered_args = ["--collect"]
        elif "--decide" in sys.argv or "决策" in intent or "decide" in intent.lower() or "生成决策" in intent:
            filtered_args = ["--decide"]
        elif "--execute" in sys.argv or "执行" in intent or "execute" in intent.lower():
            # 需要传递决策 JSON
            filtered_args = ["--execute", json.dumps({"type": "self_optimization", "description": "命令行执行", "action": "test action"})]
        elif "--loop" in sys.argv or "闭环" in intent or "loop" in intent.lower() or "完整闭环" in intent:
            filtered_args = ["--loop"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--json" in sys.argv or "json" in intent.lower():
            filtered_args = ["--json"]
        else:
            # 默认：获取驾驶舱数据
            filtered_args = ["--cockpit-data"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)

    # 智能全场景进化环认知-价值-涌现三维深度融合与自主进化引擎（Round 456）- 融合深度认知(r454)、价值实现追踪(r453)、知识自涌现(r440)能力，形成认知→价值→涌现的三维闭环
    elif "三维融合" in intent or "融合闭环" in intent or "价值涌现融合" in intent or "cognition_value_emergence" in intent.lower() or "cognition_value" in intent.lower() or "value_emergence_fusion" in intent.lower():
        print(f"[认知-价值-涌现三维融合引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_cognition_value_emergence_fusion_engine.py")

        # 确定要执行的命令
        if "--cognition-value" in sys.argv or "认知价值" in intent or "cognition value" in intent.lower() or "关联分析" in intent:
            filtered_args = ["--cognition-value"]
        elif "--value-emergence" in sys.argv or "价值涌现" in intent or "value emergence" in intent.lower() or "涌现追踪" in intent:
            filtered_args = ["--value-emergence"]
        elif "--emergence-cognition" in sys.argv or "涌现认知" in intent or "emergence cognition" in intent.lower() or "反馈" in intent:
            filtered_args = ["--emergence-cognition"]
        elif "--analyze" in sys.argv or "分析" in intent or "analyze" in intent.lower() or "三维分析" in intent:
            filtered_args = ["--analyze"]
        elif "--closed-loop" in sys.argv or "闭环" in intent or "closed loop" in intent.lower() or "完整闭环" in intent:
            filtered_args = ["--closed-loop"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        else:
            # 默认：获取驾驶舱数据
            filtered_args = ["--cockpit-data"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)

    # 智能全场景进化环创新假设自动生成与验证引擎（Round 457）- 让系统能够主动发现进化机会、生成创新性假设、设计验证实验、自动评估假设价值，形成从假设生成到验证的完整闭环
    elif "假设生成" in intent or "验证假设" in intent or "创新假设" in intent or "假设评估" in intent or "生成假设" in intent or "hypothesis generation" in intent.lower() or "hypothesis" in intent.lower() or "验证创新" in intent or "创新验证" in intent or "假设引擎" in intent:
        print(f"[创新假设自动生成与验证引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_hypothesis_generation_verification_engine.py")

        # 确定要执行的命令
        if "--status" in sys.argv or "状态" in intent or "status" in intent.lower():
            filtered_args = ["--status"]
        elif "--generate" in sys.argv or "生成" in intent or "generate" in intent.lower() or "生成假设" in intent:
            filtered_args = ["--cycle"]
        elif "--cockpit-data" in sys.argv or "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "--evaluate" in sys.argv or "评估" in intent or "evaluate" in intent.lower():
            # 提取假设ID
            import re
            match = re.search(r'(hyp_\w+)', intent)
            if match:
                filtered_args = ["--evaluate", match.group(1)]
            else:
                filtered_args = ["--cockpit-data"]
        else:
            # 默认：获取状态
            filtered_args = ["--status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)

    # 智能全场景进化环跨引擎统一知识索引与智能检索引擎（Round 446）- 聚合所有进化引擎产生的知识资产、建立统一知识索引、实现智能检索、生成知识关联图谱
    elif "知识索引" in intent or "知识检索" in intent or "跨引擎知识" in intent or "查询知识" in intent or "知识图谱" in intent or "knowledge index" in intent.lower() or "knowledge search" in intent.lower() or "knowledge graph" in intent.lower() or "知识发现" in intent or "搜索知识" in intent:
        print(f"[跨引擎知识索引与检索引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_cross_engine_knowledge_index_engine.py")

        # 确定要执行的命令
        if "收集" in intent or "collect" in intent.lower():
            filtered_args = ["--collect"]
        elif "搜索" in intent or "查询" in intent or "search" in intent.lower() or "query" in intent.lower():
            # 提取搜索关键词
            search_keyword = intent
            # 移除触发关键词
            trigger_keywords = [
                "搜索", "查询", "search", "query", "知识索引", "知识检索", "跨引擎知识",
                "查询知识", "知识图谱", "knowledge index", "knowledge search",
                "knowledge graph", "知识发现", "搜索知识"
            ]
            for kw in trigger_keywords:
                search_keyword = search_keyword.replace(kw, "").strip()
            # 如果剩余部分太短，使用默认统计
            if len(search_keyword) < 2:
                filtered_args = ["--stats"]
            else:
                filtered_args = ["--search", search_keyword]
        elif "分类" in intent or "category" in intent.lower():
            for kw in ["知识索引", "知识检索", "跨引擎知识", "查询知识", "分类", "category"]:
                intent = intent.replace(kw, "").strip()
            filtered_args = ["--category", intent] if intent else ["--stats"]
        elif "轮次" in intent or "round" in intent.lower() or "Round" in intent:
            import re
            match = re.search(r'(\d+)', intent)
            if match:
                filtered_args = ["--round", match.group(1)]
            else:
                filtered_args = ["--recent"]
        elif "最近" in intent or "recent" in intent.lower():
            filtered_args = ["--recent"]
        elif "图谱" in intent or "graph" in intent.lower():
            filtered_args = ["--build-graph"]
        elif "统计" in intent or "stats" in intent.lower() or "状态" in intent:
            filtered_args = ["--stats"]
        elif "驾驶舱" in intent or "cockpit" in intent.lower():
            filtered_args = ["--cockpit"]
        elif "完整更新" in intent or "full update" in intent.lower():
            filtered_args = ["--full-update"]
        else:
            filtered_args = ["--stats"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化知识主动推理与创新发现引擎（Round 348）
    elif "知识推理" in intent or "创新发现" in intent or "主动推理" in intent or "知识分析" in intent or "knowledge reasoning" in intent.lower() or "innovation discovery" in intent.lower() or "active reasoning" in intent.lower() or "知识趋势" in intent or "进化趋势" in intent or "知识关联" in intent or "创新机会" in intent or "知识组合" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "run", "analyze", "predict", "innovate", "paths", "config", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_knowledge_active_reasoning_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环跨引擎协同知识蒸馏引擎（Round 410）- 从多个进化引擎执行结果中自动提取和蒸馏关键知识
    elif "知识蒸馏" in intent or "蒸馏知识" in intent or "知识提取" in intent or "knowledge distillation" in intent.lower() or "distill knowledge" in intent.lower() or "知识提炼" in intent or "跨引擎知识" in intent or "引擎知识提取" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["distill"]
        if not cmd or (cmd and cmd[0] not in ["distill", "auto_distill", "get", "statistics", "stats", "help"]):
            cmd = ["distill"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_cross_engine_knowledge_distillation_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环知识驱动自动触发与自优化引擎（Round 411）- 基于 round 410 蒸馏的知识，自动分析系统状态、智能识别进化方向、自动触发相应进化引擎
    elif "知识触发" in intent or "知识驱动" in intent or "知识优化" in intent or "自动触发优化" in intent or "knowledge trigger" in intent.lower() or "knowledge driven" in intent.lower() or "knowledge optimize" in intent.lower() or "知识分析" in intent or "进化方向识别" in intent or "触发推荐" in intent or "自优化" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["analyze"]
        if not cmd or (cmd and cmd[0] not in ["analyze", "trigger", "recommend", "recommends", "optimize", "optimization", "record", "status", "help"]):
            cmd = ["analyze"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_knowledge_driven_trigger_optimizer.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环触发推荐自动执行深度集成引擎（Round 412）- 将触发推荐与进化执行引擎深度集成，实现从推荐到自动执行的完整闭环
    elif "触发执行" in intent or "自动执行" in intent or "触发推荐执行" in intent or "推荐执行" in intent or "trigger execute" in intent.lower() or "auto execute" in intent.lower() or "execute recommendation" in intent.lower() or "推荐自动执行" in intent or "执行闭环" in intent or "trigger execution" in intent.lower() or "execution integration" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["execute", "status", "verify", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_trigger_execution_integration.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环执行结果知识图谱反馈闭环引擎（Round 413）- 将执行结果反馈到知识图谱进行更新，形成知识→触发→执行→验证→知识更新的递归增强闭环
    elif "知识反馈" in intent or "知识图谱反馈" in intent or "执行反馈" in intent or "知识更新闭环" in intent or "knowledge feedback" in intent.lower() or "kg feedback" in intent.lower() or "execution feedback" in intent.lower() or "知识闭环" in intent or "反馈闭环" in intent or "知识→执行" in intent or "knowledge to execution" in intent.lower() or "执行结果反馈" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "health", "analyze", "feedback", "optimize", "close_loop", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_execution_feedback_kg_integration.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环知识驱动递归增强闭环深度集成引擎（Round 414/416）- 将知识图谱推理、主动价值发现、自适应学习能力深度集成，形成知识→价值→执行→优化→新知识的完整递归增强闭环
    elif "知识驱动递归" in intent or "递归增强闭环" in intent or "知识驱动递归增强" in intent or "knowledge driven recursive" in intent.lower() or "recursive enhancement" in intent.lower() or "递归知识增强" in intent or "递归闭环" in intent or "知识递归" in intent or "递归知识" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "health", "report", "run_cycle", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_knowledge_driven_recursive_enhancement_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环跨轮次知识积累与复用可视化引擎（Round 415）- 基于 round 414 的知识驱动递归增强引擎，增强跨轮次知识积累与复用的可视化能力
    elif "知识可视化" in intent or "知识积累可视化" in intent or "知识复用可视化" in intent or "knowledge visualization" in intent.lower() or "knowledge accumulation visualization" in intent.lower() or "知识图谱可视化" in intent or "知识趋势" in intent or "knowledge trend" in intent.lower() or "知识网络" in intent or "知识关联" in intent or "knowledge correlation" in intent.lower() or "知识价值分布" in intent or "knowledge value" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["report"]
        if not cmd or (cmd and cmd[0] not in ["report", "status", "health", "history", "trend", "network", "distribution", "help"]):
            cmd = ["report"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_knowledge_visualization_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环跨引擎协同自优化与深度集成引擎（Round 349）
    elif "进化协同" in intent or "引擎协同优化" in intent or "跨引擎健康" in intent or "协同自优化" in intent or "跨引擎" in intent or "引擎健康" in intent or "进化引擎健康" in intent or "cross engine" in intent.lower() or "engine collaboration" in intent.lower() or "collaboration optimizer" in intent.lower() or "跨引擎协同" in intent or "引擎协作" in intent or "协同优化" in intent or "进化环健康" in intent or "evolution health" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "health", "diagnose", "optimize", "full_cycle", "evaluate", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_cross_engine_collaboration_optimizer.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环统一监控数据与进化驾驶舱深度集成引擎（Round 396）- 将统一监控数据与进化驾驶舱深度集成，在驾驶舱中实现统一监控视图展示
    elif "unified monitoring cockpit" in intent.lower() or "cockpit unified monitoring" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "integrated_status", "dashboard", "run_cycle", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_cockpit_unified_monitoring_integration_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环统一监控驾驶舱与完全无人值守进化环深度集成引擎（Round 397）- 将统一监控驾驶舱(round 396)与完全无人值守进化环(round 382)深度集成，实现基于监控数据的自动触发执行
    elif "统一监控驾驶舱" in intent or "monitoring unattended" in intent.lower() or "监控无人值守" in intent or "监控自动触发" in intent or "unified monitoring unattended" in intent.lower() or "监控执行集成" in intent or "监控驱动进化" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "dashboard", "enable", "disable", "cycle", "check_trigger", "check", "health", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_unified_monitoring_unattended_integration_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环健康分数阈值自动触发进化引擎（Round 398）- 在统一监控驾驶舱与完全无人值守进化环深度集成基础上，实现基于健康分数阈值的自动触发进化能力
    elif "健康分数阈值" in intent or "阈值触发" in intent or "健康阈值" in intent or "health threshold" in intent.lower() or "阈值自动触发" in intent or "基于阈值的触发" in intent or "auto trigger" in intent and ("health" in intent.lower() or "阈值" in intent or "健康" in intent) or "阈值进化" in intent or "健康驱动" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "check", "thresholds", "set", "reset", "history", "stats", "enable", "disable", "health", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_health_threshold_trigger_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环健康分数阈值自动调整引擎（Round 399）- 在健康阈值触发引擎基础上，增强阈值自动调整能力，根据历史触发数据自动优化阈值设置
    elif "阈值自动调整" in intent or "阈值优化" in intent or "阈值自适应" in intent or "auto adjust threshold" in intent.lower() or "阈值调整" in intent or "智能阈值" in intent or "threshold auto" in intent.lower() or "阈值分析" in intent or "阈值建议" in intent or "阈值趋势" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["analyze"]
        if not cmd or (cmd and cmd[0] not in ["analyze", "auto_adjust", "dry_run", "set", "history", "summary", "enable", "disable", "health", "help"]):
            cmd = ["analyze"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_health_threshold_auto_adjust_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环实时阈值动态调整引擎（Round 400）- 在阈值自动调整引擎基础上，增强实时阈值动态调整能力，根据实时系统状态动态调整阈值
    elif "实时阈值" in intent or "阈值动态" in intent or "动态阈值" in intent or "realtime threshold" in intent.lower() or "dynamic threshold" in intent.lower() or "实时动态阈值" in intent or "预防性阈值" in intent or "阈值预测" in intent or "趋势阈值" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["state"]
        if not cmd or (cmd and cmd[0] not in ["state", "adjust", "history", "enable", "disable", "health", "help"]):
            cmd = ["state"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_realtime_threshold_dynamic_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环多维度系统指标融合与预防性阈值管理增强引擎（Round 401）- 在实时阈值动态调整引擎基础上，增强磁盘IO、网络延迟、进程状态等多维度系统指标融合能力，实现更精准的预防性阈值管理
    elif "多维度指标" in intent or "多维度融合" in intent or "系统指标" in intent or "磁盘IO" in intent or "网络延迟" in intent or "进程状态" in intent or "multidim" in intent.lower() or "multi-dim" in intent.lower() or "metrics fusion" in intent.lower() or "disk io" in intent.lower() or "network latency" in intent.lower() or "多维度阈值" in intent or "指标融合" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "health", "history", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_multidim_system_metrics_fusion_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环跨引擎协同深度集成引擎（Round 402）- 将多维度指标分析结果与进化环其他引擎（健康评估、预测预防、决策执行）深度集成，形成更全面的智能决策闭环
    elif "跨引擎协同" in intent or "跨引擎集成" in intent or "引擎协同" in intent or "引擎集成" in intent or "cross engine" in intent.lower() or "跨引擎深度" in intent or "深度集成" in intent or "智能决策闭环" in intent or "集成决策" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "health", "analyze", "decide", "synergy", "start", "stop", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_cross_engine_collaboration_deep_integration_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化引擎集群统一诊断自愈与进化驾驶舱深度集成引擎（Round 404）- 将诊断自愈中心与进化驾驶舱深度集成
    elif "诊断驾驶舱" in intent or "诊断集成" in intent or "诊断可视化" in intent or "diagnosis cockpit" in intent.lower() or "diagnose cockpit" in intent.lower() or "诊断状态" in intent or "引擎诊断" in intent or "诊断视图" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["dashboard"]
        if not cmd or (cmd and cmd[0] not in ["status", "dashboard", "run_diagnosis", "heal", "engine_list", "help"]):
            cmd = ["dashboard"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_diagnosis_cockpit_integration_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化引擎集群跨引擎智能修复与深度自愈集成引擎（Round 405）- 将诊断结果自动转化为修复行动
    elif "智能修复" in intent or "深度自愈" in intent or "跨引擎修复" in intent or "自动修复" in intent or "smart repair" in intent.lower() or "deep healing" in intent.lower() or "auto repair" in intent.lower() or "跨引擎自愈" in intent or "智能自愈" in intent or "修复引擎" in intent or "自愈引擎" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "history", "auto_repair", "analyze", "enable", "disable", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_cross_engine_smart_repair_deep_healing_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环执行效率智能优化引擎（Round 406）
    elif "效率优化" in intent or "智能调度" in intent or "执行优化" in intent or "动态调度" in intent or "efficiency optimization" in intent.lower() or "intelligent scheduling" in intent.lower() or "execution optimization" in intent.lower() or "dynamic scheduling" in intent.lower() or "负载优化" in intent or "资源调度" in intent or "任务调度" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "history", "analyze", "optimize", "heal", "start", "stop", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_execution_efficiency_intelligent_optimizer.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环执行效率可视化监控与驾驶舱深度集成引擎（Round 407）
    elif "效率监控" in intent or "负载可视化" in intent or "效率可视化" in intent or "可视化负载" in intent or "execution monitoring" in intent.lower() or "load visualization" in intent.lower() or "efficiency visualization" in intent.lower() or "驾驶舱集成" in intent or "可视化监控" in intent or "load monitor" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "analyze", "optimize", "heal", "start", "stop", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_execution_efficiency_cockpit_integration_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环执行效率预测性智能调度增强引擎（Round 408）
    elif "预测性调度" in intent or "预测调度" in intent or "智能预测调度" in intent or "predictive scheduling" in intent.lower() or "predictive" in intent.lower() and "schedule" in intent.lower() or "负载预测" in intent or "预测负载" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "analyze", "optimize", "heal", "start", "stop", "predict", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_execution_efficiency_predictive_scheduling_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环执行稳定性预测防护增强引擎（Round 409）
    elif "稳定性防护" in intent or "主动防护" in intent or "稳定性预测" in intent or "stability protection" in intent.lower() or "stability predict" in intent.lower() or "主动稳定" in intent or "防护增强" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "analyze", "protect", "heal", "predict", "start", "stop", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_execution_stability_protection_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环全局智能驾驶舱与一键启动引擎（Round 350）
    elif "驾驶舱" in intent or "进化驾驶舱" in intent or "一键启动" in intent or "进化控制台" in intent or "cockpit" in intent.lower() or "evolution cockpit" in intent.lower() or "一键进化" in intent or "进化状态" in intent and ("控制" in intent or "台" in intent or "一键" in intent):
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "start", "stop", "pause", "resume", "health", "diagnose", "full_cycle", "evaluate", "toggle_auto", "dashboard", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_cockpit_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环自适应触发与自主决策增强引擎（Round 351）
    elif "自适应触发" in intent or "自主决策" in intent or "自适应进化环" in intent or "智能触发" in intent or "adaptive trigger" in intent.lower() or "adaptive decision" in intent.lower() or "决策增强" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "health", "diagnose", "evaluate", "decide", "execute", "full_cycle", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_adaptive_trigger_decision_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环自适应学习与动态策略优化引擎（Round 352）
    elif "自适应学习" in intent or "策略优化" in intent or "动态调整" in intent or "adaptive learning" in intent.lower() or "strategy optimization" in intent.lower() or "dynamic adjust" in intent.lower() or "学习优化" in intent or "参数调整" in intent or "策略自适应" in intent or "递归优化" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "analyze", "patterns", "failures", "adjust", "strategy", "reset", "full_cycle", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_adaptive_learning_strategy_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环自我修复能力增强引擎（Round 353）
    elif "自我修复" in intent or "主动预防" in intent or "问题预测" in intent or "self repair" in intent.lower() or "主动修复" in intent or "预防性修复" in intent or "predict problem" in intent.lower() or "问题预测" in intent or "自愈增强" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "predict", "prevent", "repair", "verify", "full_cycle", "meta_repair", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_self_repair_enhancement_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化引擎集群统一导航与智能入口引擎（Round 355）
    elif "进化引擎导航" in intent or "引擎导航" in intent or "进化导航" in intent or "进化引擎集群" in intent or "引擎列表" in intent or "搜索进化引擎" in intent or "evolution engine navigator" in intent.lower() or "engine navigator" in intent.lower() or "engine cluster" in intent.lower() or "evolution cluster" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["list"]
        if not cmd or (cmd and cmd[0] not in ["list", "search", "info", "status", "run", "--refresh", "help"]):
            cmd = ["list"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_engine_cluster_navigator.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化引擎集群智能诊断与自动修复引擎（Round 356）
    elif "引擎诊断" in intent or "诊断修复" in intent or "进化引擎诊断" in intent or "engine diagnostic" in intent.lower() or "diagnostic repair" in intent.lower() or "引擎集群健康" in intent or "集群诊断" in intent or "集群修复" in intent or "进化引擎状态" in intent or "进化引擎健康度" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["health"]
        if not cmd or (cmd and cmd[0] not in ["list", "diagnose", "repair", "report", "health", "--force", "help"]):
            cmd = ["health"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_engine_cluster_diagnostic_repair.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化引擎集群统一智能诊断与自愈中心引擎（Round 403）- 将分散的诊断自愈能力统一
    elif "统一诊断自愈" in intent or "诊断自愈中心" in intent or "引擎统一诊断" in intent or "unified diagnosis healing" in intent.lower() or "diagnosis healing center" in intent.lower() or "统一诊断中心" in intent or "自愈中心" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["scan", "diagnose", "heal", "health", "status", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_unified_diagnosis_healing_center.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化引擎集群协同优化与性能预测增强引擎（Round 357）
    elif "性能预测" in intent or "协同优化" in intent or "预测优化" in intent or "预防性维护" in intent or "engine predictive" in intent.lower() or "predictive optimizer" in intent.lower() or "协同" in intent and "进化" in intent or "引擎优化" in intent or "优化引擎" in intent or "性能优化" in intent or "健康预测" in intent or "引擎趋势" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["predict", "optimize", "prevent", "verify", "status", "--days", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_engine_cluster_predictive_optimizer.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化引擎集群跨引擎深度健康自愈与元进化增强引擎（Round 384）
    elif "跨引擎健康" in intent or "协同自愈" in intent or "元进化增强" in intent or "深度健康" in intent or "集群自愈" in intent or "cross engine" in intent.lower() and "health" in intent.lower() or "deep health" in intent.lower() or "meta evolution" in intent.lower() or "协同修复" in intent or "跨引擎深度" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["health"]
        if not cmd or (cmd and cmd[0] not in ["health", "diagnose", "self_heal", "optimize", "metrics", "full_cycle", "status", "help"]):
            cmd = ["health"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_engine_cluster_deep_health_meta_evolution_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化引擎集群驾驶舱深度集成引擎（Round 385）
    elif "集群驾驶舱可视化" in intent or "引擎集群驾驶舱" in intent or "深度驾驶舱集成" in intent or "cluster cockpit integration" in intent.lower() or "集成可视化监控" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["dashboard", "health", "self_heal", "visualize", "status", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_engine_cluster_cockpit_integration_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化引擎集群可视化一键自愈增强引擎（Round 386）
    elif "可视化一键自愈" in intent or "增强自愈" in intent or "可视化自愈" in intent or "visual one click heal" in intent.lower() or "一键自愈增强" in intent or "visual one-click" in intent.lower() or "增强可视化自愈" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["dashboard", "health", "self_heal", "visualize", "status", "verify", "monitor", "start_monitor", "stop_monitor", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_visual_oneclick_heal_enhanced_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环主动创新实现引擎（Round 358）
    elif "主动创新" in intent or "创新实现" in intent or "创新发现" in intent or "创新机会" in intent or "主动发现创新" in intent or "innovation realization" in intent.lower() or "创新闭环" in intent or "创新引擎" in intent or "发现并实现" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["discover", "evaluate", "plan", "execute", "cycle", "status", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_innovation_realization_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景服务协同编排与自适应执行引擎（Round 359）
    elif "服务编排" in intent or "自适应执行" in intent or "智能协同" in intent or "端到端服务" in intent or "service orchestration" in intent.lower() or "自适应" in intent and "执行" in intent or "协同编排" in intent or "任务拆分" in intent or "智能服务" in intent and "闭环" in intent or "一站式服务执行" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["execute", "understand", "plan", "status", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_service_orchestration_adaptive_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景跨会话状态持久化与恢复引擎（Round 360）
    elif "会话持久化" in intent or "状态保存" in intent or "状态恢复" in intent or "跨会话" in intent or "session persistence" in intent.lower() or "save state" in intent.lower() or "restore state" in intent.lower() or "中断恢复" in intent or "长时任务" in intent or "checkpoint" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["save", "load", "checkpoint", "recover", "task", "status", "list", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_session_persistence_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景主动预测与预防性服务增强引擎（Round 361）
    elif "主动预测" in intent or "预测服务" in intent or "预防性服务" in intent or "需求预测" in intent or "服务预热" in intent or "predictive service" in intent.lower() or "predict" in intent.lower() and "service" in intent.lower() or "pre-service" in intent.lower() or "pre_service" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["predict"]
        if not cmd or (cmd and cmd[0] not in ["predict", "status", "record", "feedback", "pre-service", "pre_service", "help"]):
            cmd = ["predict"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_predictive_service_enhancement_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环实时监控与智能预警增强引擎（Round 362）
    elif "实时监控" in intent or "智能预警" in intent or "状态监控" in intent or "预警查询" in intent or "监控状态" in intent or "realtime monitoring" in intent.lower() or "real-time monitor" in intent.lower() or "智能监控" in intent or "预警" in intent and "进化" in intent or "monitoring" in intent.lower() and "warning" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "check", "warnings", "acknowledge", "start", "stop", "summary", "clear", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_realtime_monitoring_warning_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环执行效率自适应深度优化引擎（Round 363）
    elif "执行效率" in intent or "自适应优化" in intent or "效率优化" in intent or "execution efficiency" in intent.lower() or "efficiency optimization" in intent.lower() or "效率分析" in intent or "自适应深度优化" in intent or "深度优化" in intent or "优化引擎" in intent and "进化" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "analyze", "reports", "start", "stop", "summary", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_execution_efficiency_optimizer.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环价值实现追踪深度量化引擎（Round 364，增强 Round 438）
    elif "价值量化" in intent or "价值追踪" in intent and "量化" in intent or "ROI分析" in intent or "价值分析" in intent or "value quantization" in intent.lower() or "roi analysis" in intent.lower() or "量化价值" in intent or "价值得分" in intent or "价值指标" in intent or "量化分析" in intent or "价值优化" in intent or "价值模式" in intent or "价值闭环" in intent or "增强价值" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "analyze", "trends", "recommend", "report", "summary", "help", "optimize", "patterns", "predict", "cockpit", "adjust", "validate", "enhanced_loop", "full_loop"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_value_quantization_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环价值量化评估增强引擎（Round 503）
    elif "增强价值量化" in intent or "价值量化增强" in intent or "多维度价值" in intent or "多维价值分析" in intent or "enhanced value quantization" in intent.lower() or "value quantization enhanced" in intent.lower() or "多维度价值评估" in intent or "价值智能推荐" in intent or "智能任务推荐" in intent and "价值" in intent or "创新价值分析" in intent or "价值创新分析" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "analyze", "innovation", "recommend", "trends", "cockpit", "full", "summary", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_value_quantization_enhanced_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环自适应进化路径规划与预测引擎（Round 439）
    elif "路径规划" in intent or "进化路径" in intent or "路径预测" in intent or "规划进化" in intent or "自适应路径" in intent or "path planning" in intent.lower() or "进化规划" in intent or "自适应规划" in intent or "智能规划" in intent and "进化" in intent or "战略规划" in intent or "路径选择" in intent or "最佳路径" in intent or "optimal path" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["report"]
        if not cmd or (cmd and cmd[0] not in ["status", "analyze", "paths", "report", "optimal", "help"]):
            cmd = ["report"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_adaptive_path_planning_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环价值驱动决策自动执行引擎（Round 365）
    elif "价值驱动决策" in intent or "价值决策" in intent and "自动" in intent or "value driven decision" in intent.lower() or "价值驱动" in intent and "决策" in intent or "自动决策" in intent and "价值" in intent or "决策自动化" in intent or "价值自适应" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "analyze", "decide", "adjust", "cycle", "recommend", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_value_driven_decision_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环价值驱动自动执行闭环引擎（Round 366）
    elif "价值驱动自动闭环" in intent or "价值驱动自动执行" in intent or "价值闭环" in intent or "价值进化闭环" in intent or "value driven loop" in intent.lower() or "value driven auto" in intent.lower() or "价值驱动进化" in intent or "价值自动进化" in intent or "自动进化闭环" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "check", "conditions", "execute", "run", "loop", "closed-loop", "enable", "disable", "config", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_value_driven_loop_integration.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景多维智能协同闭环增强引擎（Round 367）
    elif "多维智能协同" in intent or "多维协同" in intent or "智能协同闭环" in intent or "multi dim" in intent.lower() or "multi-dim" in intent.lower() or "协同增强" in intent or "多维融合" in intent or "协同编排" in intent or "smart orchestration" in intent.lower() or "多维" in intent and ("协同" in intent or "智能" in intent):
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "execute", "analyze", "history", "plan", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_multi_dim_smart_orchestration_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环自主意识驱动执行增强引擎（Round 368）
    elif "自主意识驱动" in intent or "自主执行增强" in intent or "意识驱动执行" in intent or "autonomous execution" in intent.lower() or "意识执行" in intent or "意图驱动" in intent or "自主意图" in intent or "自主驱动" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "analyze", "decide", "execute", "verify", "cycle", "history", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_autonomous_execution_enhancement_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环多维度自主意识融合深度增强引擎（Round 369）
    elif "多维度融合" in intent or "多维度意识融合" in intent or "意识融合" in intent or "multidimensional fusion" in intent.lower() or "multi-dim consciousness" in intent.lower() or "consciousness fusion" in intent.lower() or "融合模式" in intent or "自适应模式" in intent or "模式选择" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["--dashboard"]
        if not cmd or (cmd and cmd[0] not in ["--status", "--full-loop", "--fusion-status", "--analyze-context", "--dashboard", "--help"]):
            cmd = ["--dashboard"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_multidimensional_consciousness_fusion_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环统一智能体深度集成引擎（Round 370）
    elif "统一智能体" in intent or "深度集成" in intent or "统一集成" in intent or "unified agent" in intent.lower() or "deep integration" in intent.lower() or "跨引擎集成" in intent or "统一调度" in intent or "递归优化" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["--dashboard"]
        if not cmd or (cmd and cmd[0] not in ["--status", "--full-loop", "--integration-status", "--unified-dispatch", "--analyze-state", "--dashboard", "--help"]):
            cmd = ["--dashboard"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_unified_agent_deep_integration_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环多维度智能协同决策与自适应规划引擎（Round 371）
    elif "多维度决策" in intent or "智能协同决策" in intent or "自适应规划" in intent or "multidim decision" in intent.lower() or "adaptive planning" in intent.lower() or "协同规划" in intent or "智能规划" in intent or "决策规划" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["--dashboard"]
        if not cmd or (cmd and cmd[0] not in ["--full-loop", "--decision-analysis", "--adaptive-plan", "--dashboard", "--version", "--help"]):
            cmd = ["--dashboard"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_multidim_decision_planning_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环决策-执行闭环深度集成引擎（Round 372）- 将决策能力与执行引擎深度集成
    elif "决策执行闭环" in intent or "决策执行集成" in intent or "决策到执行" in intent or "decision execution" in intent.lower() or "decision execute" in intent.lower() or "闭环执行" in intent or "执行一体化" in intent or "decision_execution" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "process", "history", "test", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_decision_execution_closed_loop.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环跨轮次知识深度整合与智能推理引擎（Round 373）- 跨轮次知识收集、图谱构建、趋势分析、创新发现
    elif "知识整合" in intent or "知识推理" in intent or "跨轮推理" in intent or "知识分析" in intent or "knowledge integration" in intent.lower() or "knowledge reasoning" in intent.lower() or "知识网络" in intent or "图谱构建" in intent or "趋势分析" in intent or "创新发现" in intent or "跨轮知识" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "collect", "build", "analyze", "discover", "integrate", "cycle", "test", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_knowledge_deep_integration_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环价值闭环自动执行增强引擎（Round 374）- 价值闭环、价值执行、机会实现、自动价值
    # 排除"价值实现预测"以避免与 Round 516 引擎冲突
    elif ("价值闭环" in intent or "价值执行" in intent or "机会实现" in intent or "自动价值" in intent or "value closed" in intent.lower() or "value loop" in intent.lower() or "value execution" in intent.lower() or "机会执行" in intent or "价值实现" in intent) and "价值实现预测" not in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "discover", "evaluate", "plan", "execute", "validate", "metrics", "cycle", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_value_closed_loop_execution_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环价值-知识双闭环递归增强引擎（Round 375）- 价值知识闭环、知识价值融合、递归增强、双闭环
    elif "价值知识闭环" in intent or "知识价值融合" in intent or "递归增强" in intent or "双闭环" in intent or "value knowledge" in intent.lower() or "knowledge value" in intent.lower() or "recursive" in intent.lower() and "enhance" in intent.lower() or "value-knowledge" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "metrics", "cycle", "insights", "feedback", "prioritize", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_value_knowledge_closed_loop_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环统一元进化引擎深度集成与自主运行增强引擎（Round 376）- 元进化集成、深度集成、自主运行增强、无人值守
    elif "元进化集成" in intent or "深度集成" in intent or "自主运行增强" in intent or "无人值守" in intent or "meta integration" in intent.lower() or "unified meta" in intent.lower() or "元进化增强" in intent or "meta enhanced" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "metrics", "execute", "run", "loop", "closed-loop", "full_cycle", "cycle", "full", "enable", "on", "disable", "off", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_meta_integration_enhanced.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环统一智能体协同引擎（Round 377）- 统一智能体、跨引擎协同、智能组合、引擎组合、协同执行
    elif "统一智能体" in intent or "跨引擎协同" in intent or "智能组合" in intent or "引擎组合" in intent or "协同执行" in intent or "unified agent" in intent.lower() or "engine collaboration" in intent.lower() or "multi engine" in intent.lower() or "engine coordination" in intent.lower() or "统一进化智能体" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "list", "analyze", "execute", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "unified_evolution_agent_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环统一智能体协同引擎与进化驾驶舱深度集成引擎（Round 378）- 智能体驾驶舱集成、agent cockpit、集成引擎、统一监控
    elif "智能体驾驶舱" in intent or "agent cockpit" in intent.lower() or "集成引擎" in intent or "统一监控" in intent or "智能体与驾驶舱" in intent or "agent cockpit integration" in intent.lower() or "集成驾驶舱" in intent or "智能体集成" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "analyze", "execute", "dashboard", "health", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_agent_cockpit_integration_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环元进化自主决策深度增强引擎（Round 379）- 元进化决策、智能进化决策、进化策略分析、自主决策增强
    elif "元进化决策" in intent or "智能进化决策" in intent or "进化策略分析" in intent or "自主决策增强" in intent or "meta decision" in intent.lower() or "meta evolution" in intent.lower() and "decision" in intent.lower() or "evolution decision" in intent.lower() or "元决策" in intent or "决策增强" in intent or "meta_decision" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "analyze", "select", "predict", "execute", "health", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_meta_decision_deep_enhancement_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环元进化决策与自动化执行深度集成引擎（Round 380）- 元进化自动化、决策执行集成、自动化决策执行
    elif "元进化自动化" in intent or "决策执行集成" in intent or "自动化决策执行" in intent or "meta execution" in intent.lower() or "decision execution" in intent.lower() or "meta auto" in intent.lower() or "元进化执行" in intent or "自动化集成" in intent or "meta_decision_execution" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "analyze", "decide", "execute", "verify", "optimize", "full_loop", "health", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_meta_decision_execution_integration_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环完全无人值守自主进化增强引擎（Round 382）- 增强完全无人值守的自主进化能力（必须放在 round 381 之前以确保精确匹配）
    elif "完全无人值守" in intent or "无人值守进化增强" in intent or "自主进化增强" in intent or "auto unattended" in intent.lower() or "autonomous enhancement" in intent.lower() or "unattended evolution" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "enable", "disable", "trigger", "metrics", "run", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_autonomous_unattended_enhancement_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环完全无人值守自主进化与进化驾驶舱深度集成引擎（Round 383）- 将完全无人值守自主进化增强引擎与进化驾驶舱深度集成，实现更智能的可视化监控
    elif "无人值守驾驶舱" in intent or "驾驶舱无人值守" in intent or "unattended cockpit" in intent.lower() or "深度集成" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "start", "stop", "pause", "resume", "dashboard", "recommendations", "clear_alerts", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_unattended_cockpit_deep_integration_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化引擎集群元进化自主意识深度增强引擎（Round 387）- 元进化自主意识、自主意识进化、智能进化决策、意识驱动
    elif "元进化自主意识" in intent or "自主意识进化" in intent or "智能进化决策" in intent or "意识驱动" in intent or "meta autonomous" in intent.lower() or "autonomous consciousness" in intent.lower() or "consciousness driven" in intent.lower() or "meta_consciousness" in intent.lower() or "意识增强" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "scan", "decide", "execute", "full_cycle", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_meta_autonomous_consciousness_deep_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环自我评估与策略迭代优化引擎（Round 388）- 自我评估、策略优化、决策迭代、评估驱动
    elif "自我评估" in intent or "策略优化" in intent or "决策迭代" in intent or "评估驱动" in intent or "self evaluation" in intent.lower() or "strategy iteration" in intent.lower() or "decision iteration" in intent.lower() or "evaluation driven" in intent.lower() or "策略迭代" in intent or "自我评价" in intent or "决策评估" in intent or "策略调整" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "evaluate", "identify", "optimize", "full_cycle", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_self_evaluation_strategy_iteration_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环进化趋势预测与预防性决策增强引擎（Round 389）- 趋势预测、预防性决策、风险评估、动态策略调整
    elif "进化趋势预测" in intent or "趋势预测" in intent or "预测进化" in intent or "预防性决策" in intent or "预防决策" in intent or "风险预防" in intent or "trend prediction" in intent.lower() or "prevention decision" in intent.lower() or "risk prevention" in intent.lower() or "风险评估" in intent or "进化风险" in intent or "风险检测" in intent or "动态策略调整" in intent or "策略预测调整" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "predict", "risk", "help", "趋势预测", "风险评估", "风险检测"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_trend_prediction_prevention_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环评估-预测-预防一体化深度集成引擎（Round 390）- 将 round 389 的趋势预测预防引擎与 round 388 的自我评估引擎深度集成
    elif "评估预测融合" in intent or "评估预测一体化" in intent or "融合分析" in intent or "evaluation prediction" in intent.lower() or "evaluation fusion" in intent.lower() or "评估-预测" in intent or "评估和预测" in intent or "动态策略闭环" in intent or "闭环优化" in intent or "adaptive prevention" in intent.lower() or "prevention闭环" in intent or "prediction learning" in intent.lower() or "预测学习" in intent or "模型优化" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "fusion", "prevention", "closed_loop", "learning", "full_cycle", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_evaluation_prediction_prevention_integration_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环评估-预测-预防引擎与进化驾驶舱深度集成引擎（Round 391）- 将评估-预测-预防引擎与进化驾驶舱深度集成
    elif "评估驾驶舱" in intent or "评估预测驾驶舱" in intent or "可视化监控" in intent or "evaluation cockpit" in intent.lower() or "驾驶舱可视化" in intent or "一体化监控" in intent or "评估状态" in intent or "预测状态" in intent or "预防状态" in intent or "evaluation status" in intent.lower() or "prevention status" in intent.lower() or "评估预测集成" in intent or "evaluation integration" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "display", "full_cycle", "enable_cockpit", "disable_cockpit", "enable_warning", "disable_warning", "history", "clear_history", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_evaluation_prediction_cockpit_integration_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环评估-预测-预防能力与完全无人值守进化环深度集成引擎（Round 392）- 将评估-预测-预防能力与完全无人值守进化环深度集成，实现基于评估结果的自动化触发执行
    elif "评估无人值守" in intent or "无人值守集成" in intent or "自动触发进化" in intent or "evaluation unattended" in intent.lower() or "auto trigger" in intent.lower() or "无人值守自动化" in intent or "评估自动触发" in intent or "评估驱动自动化" in intent or "evaluation auto" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "full_cycle", "evaluate", "enable", "disable", "config", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_evaluation_unattended_integration_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景统一进化智能体深度融合引擎（Round 393）- 将评估、预测、决策、执行、学习等多维度智能深度融合，构建统一进化智能体核心
    elif "统一进化智能体" in intent or "智能体融合" in intent or "进化智能体" in intent or "unified intelligent" in intent.lower() or "intelligent body fusion" in intent.lower() or "智能融合引擎" in intent or "多维智能融合" in intent or "进化大脑" in intent or "unified body" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "full_cycle", "evaluate", "decision", "execution", "learning", "health", "history", "enable", "disable", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_unified_intelligent_body_fusion_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景统一智能体融合驾驶舱集成引擎（Round 394）- 将统一智能体融合引擎与进化驾驶舱深度集成，实现可视化融合状态监控
    elif "融合驾驶舱" in intent or "融合状态监控" in intent or "融合可视化" in intent or "fusion cockpit" in intent.lower() or "unified fusion" in intent.lower() or "融合引擎状态" in intent or "fusion status" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "full_cycle", "fusion_status", "cockpit_status", "history", "alerts", "start_monitor", "stop_monitor", "enable_fusion", "disable_fusion", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_unified_fusion_cockpit_integration_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环实时监控与融合状态深度集成引擎（Round 395）- 将融合状态监控数据与进化环实时监控引擎深度集成，实现更丰富的可视化展示
    elif "融合监控" in intent or "深度集成监控" in intent or "融合实时监控" in intent or "unified monitoring" in intent.lower() or "fusion integration monitoring" in intent.lower() or "融合状态集成" in intent or "实时融合监控" in intent or "统一监控视图" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "check", "visualization", "warnings", "fusion_status", "monitoring_status", "start", "stop", "summary", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_realtime_monitoring_fusion_integration_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环元进化能力增强引擎（round 442）- 让系统能够自动分析自身进化过程、评估进化方法论效率、生成更优的进化策略，形成"学会如何进化"的递归优化能力
    # round 443 新增：元进化驾驶舱深度集成 - 元进化可视化、元进化推送、驾驶舱集成（优先匹配）
    elif "元进化驾驶舱" in intent or "元进化可视化" in intent or "元进化推送" in intent or "meta cockpit" in intent.lower() or "meta visualization" in intent.lower() or "meta push" in intent.lower():
        print(f"[进化环元进化能力增强引擎 - 驾驶舱集成] 正在启动元进化驾驶舱深度集成...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_evolution_enhancement_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []

        # 确定要执行的命令
        if "摘要" in intent or "summary" in intent.lower():
            filtered_args = ["--cockpit-summary"]
        elif "数据" in intent or "data" in intent.lower():
            filtered_args = ["--cockpit-data"]
        elif "推送" in intent or "push" in intent.lower():
            if "启动" in intent or "start" in intent.lower():
                filtered_args = ["--start-push"]
            elif "停止" in intent or "stop" in intent.lower():
                filtered_args = ["--stop-push"]
            else:
                filtered_args = ["--cockpit"]
        elif "启动" in intent or "start" in intent.lower():
            filtered_args = ["--start-push"]
        elif "停止" in intent or "stop" in intent.lower():
            filtered_args = ["--stop-push"]
        else:
            filtered_args = ["--cockpit-summary"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环统一监控数据与进化驾驶舱深度集成引擎（Round 396）- 将统一监控数据与进化驾驶舱深度集成，在驾驶舱中实现统一监控视图展示
    elif "unified monitoring cockpit" in intent.lower() or "cockpit unified monitoring" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "integrated_status", "dashboard", "run_cycle", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_cockpit_unified_monitoring_integration_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环元进化驾驶舱深度集成引擎（Round 381）- 将元进化自动化引擎与进化驾驶舱深度集成
    elif "元进化驾驶舱" in intent or "驾驶舱集成" in intent or "无人值守进化环" in intent or "完全自主进化" in intent or "auto evolution" in intent.lower() or "unmanned evolution" in intent.lower() or "cockpit meta" in intent.lower() or "进化驾驶舱" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "components", "dashboard", "loop", "auto_enable", "auto_disable", "health", "metrics", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_cockpit_meta_integration_engine.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能全场景进化环目标自优化引擎（Round 317）
    elif "目标自优化" in intent or "进化目标优化" in intent or "目标评估" in intent or "目标价值" in intent or "goal self" in intent.lower() or "goal optimize" in intent.lower() or "目标体系" in intent or "目标遗漏" in intent or "发现目标" in intent or "目标优化" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "analyze", "evaluate", "discover", "validate", "optimize", "think", "help"]):
            cmd = ["status"]
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_goal_self_optimizer.py")] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    # 智能进化环全局调度与优先级自动优化引擎（Round 284）
    elif "进化调度" in intent or "全局调度" in intent or "智能调度" in intent or "进化优先级" in intent or "优先级优化" in intent or "evolution scheduler" in intent.lower() or "global scheduler" in intent.lower() or "priority" in intent.lower() and "进化" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "schedule", "load", "efficiency", "urgency", "adjust", "help"]):
            cmd = ["status"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_global_scheduler.py")] + cmd, cwd=PROJECT)
    # 智能进化环自主创新能力增强引擎（Round 285）
    elif "自主创新能力" in intent or "进化创新" in intent or "创新引擎" in intent or "autonomous innovation" in intent.lower() or "innovation engine" in intent.lower() or "创新发现" in intent or "发现创新" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "scan", "discover", "evaluate", "plan", "history", "help"]):
            cmd = ["status"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_autonomous_innovation_engine.py")] + cmd, cwd=PROJECT)
    # 智能全场景预测驱动主动服务编排引擎（Round 286）
    elif "预测驱动" in intent or "主动服务编排" in intent or "predictive service" in intent.lower() or "服务预测" in intent or "需求预测" in intent or "主动预测" in intent or "预测服务" in intent or "predict orchestrator" in intent.lower() or "predict_and_orchestrate" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "predict", "orchestrate", "execute", "patterns", "help"]):
            cmd = ["status"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "predictive_service_orchestrator.py")] + cmd, cwd=PROJECT)

    # 智能全场景进化环元进化价值创造与自我增强引擎 (Round 621)
    # 让系统能够主动评估自身能力组合的价值潜力，发现并创造新的价值实现方式，
    # 基于价值驱动实现自我增强与持续进化，形成「价值发现→价值创造→价值实现→价值增强」的完整价值创造闭环
    elif "元进化价值创造" in intent or "元进化自我增强" in intent or "能力组合价值" in intent or "meta value creation" in intent.lower() or "meta self enhancement" in intent.lower() or "capability value" in intent.lower() or "价值创造引擎" in intent or "自我增强引擎" in intent or "价值潜力评估" in intent or "能力价值" in intent:
        print(f"[智能全场景进化环元进化价值创造与自我增强引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_value_creation_self_enhancement_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["元进化价值创造", "元进化自我增强", "能力组合价值", "meta value creation", "meta self enhancement", "capability value", "价值创造引擎", "自我增强引擎", "价值潜力评估", "能力价值"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环元进化价值创造与知识资产持续变现引擎 (Round 641)
    # 让系统能够将640轮积累的进化知识资产转化为实际价值，识别高价值应用机会，主动创造新价值，形成知识资产的价值实现闭环
    elif "知识资产" in intent or "价值变现" in intent or "资产变现" in intent or "knowledge asset" in intent.lower() or "asset monetization" in intent.lower() or "知识价值" in intent or "资产价值" in intent or "价值创造引擎" in intent and "元进化" in intent or "知识资产变现" in intent:
        print(f"[智能全场景进化环元进化价值创造与知识资产持续变现引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_value_creation_knowledge_asset_monetization_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["知识资产", "价值变现", "资产变现", "knowledge asset", "asset monetization", "知识价值", "资产价值", "价值创造引擎", "元进化", "知识资产变现"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环创新价值完整实现闭环引擎 (Round 642)
    # 填补 round 633-641 构建的「创新发现→验证排序→价值变现」体系中的执行闭环缺口
    # 让验证通过的创新建议能够自动执行并转化为实际价值
    elif ("创新价值闭环" in intent or "创新实现闭环" in intent or "价值实现闭环" in intent
          or "innovation closed loop" in intent.lower() or "value closed loop" in intent.lower()
          or "创新价值完整实现" in intent
          or ("完整实现" in intent and "创新" in intent)
          or "创新闭环执行" in intent):
        print(f"[智能全场景进化环创新价值完整实现闭环引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_innovation_value_closed_loop_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["创新价值闭环", "创新实现闭环", "价值实现闭环", "innovation closed loop", "value closed loop", "创新价值完整实现", "完整实现", "创新闭环执行"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环全自动化闭环深度增强引擎 (Round 643)
    # 在 round 642 完成的创新价值闭环基础上，进一步增强完全无人值守的进化能力
    # 让系统能够自主触发、主动发现优化机会、自动执行验证，形成真正的自主进化闭环
    elif ("全自动化闭环" in intent or "自动化闭环增强" in intent or "auto loop deep" in intent.lower()
          or "全自动化进化" in intent or "无人值守进化" in intent or "auto evolution" in intent.lower()
          or "闭环深度增强" in intent or "deep enhancement" in intent.lower()
          or ("自动" in intent and "闭环" in intent)
          or "自动触发进化" in intent
          or "智能触发" in intent):
        print(f"[智能全场景进化环全自动化闭环深度增强引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_full_auto_loop_deep_enhancement_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["全自动化闭环", "自动化闭环增强", "auto loop deep", "全自动化进化", "无人值守进化", "auto evolution",
                        "闭环深度增强", "deep enhancement", "自动", "闭环", "自动触发进化", "智能触发"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景超级预测与主动价值创造引擎（Round 287）
    elif "超级预测" in intent or "主动价值创造" in intent or "机会发现" in intent or "super prediction" in intent.lower() or "opportunity discovery" in intent.lower() or "create value" in intent.lower() or "价值创造" in intent or "趋势分析" in intent or "trends analysis" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "analyze", "list", "proposal", "help"]):
            cmd = ["status"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "super_prediction_opportunity_engine.py")] + cmd, cwd=PROJECT)
    # 智能进化闭环自愈与预防引擎（Round 280）
    elif "进化自愈" in intent or "进化修复" in intent or "进化预防" in intent or "evolution self heal" in intent.lower() or "self healing" in intent.lower() or "进化健康" in intent or "进化闭环自愈" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "health", "analyze", "patterns", "repair", "prevent", "heal", "cycle", "help"]):
            cmd = ["status"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_loop_self_healing_engine.py")] + cmd, cwd=PROJECT)
    # 智能全场景进化闭环深度自愈与容错增强引擎（Round 290）
    elif "深度自愈" in intent or "容错增强" in intent or "fault tolerance" in intent.lower() or "智能回滚" in intent or "状态快照" in intent or "错误检测" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "snapshot", "restore", "monitor", "help"]):
            cmd = ["status"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_loop_self_healing_advanced.py")] + cmd, cwd=PROJECT)
    # 智能全场景进化健康自评估与自愈集成引擎（Round 295）
    elif "进化健康自愈集成" in intent or "健康自愈集成" in intent or "评估修复闭环" in intent or "health healing integrated" in intent.lower() or "health and healing" in intent.lower() or "健康修复" in intent or "评估后修复" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "health", "repair", "run", "integrate", "help"]):
            cmd = ["run"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_health_healing_integrated_engine.py")] + cmd, cwd=PROJECT)
    # 智能全场景进化环健康指数实时仪表盘引擎（Round 311）
    elif "进化健康仪表盘" in intent or "健康仪表盘" in intent or "健康指数" in intent or "健康可视化" in intent or "evolution health dashboard" in intent.lower() or "health index" in intent.lower() or "health viz" in intent.lower() or ("健康状态" in intent and "进化" in intent):
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "dashboard", "summary", "refresh", "update", "help"]):
            cmd = ["status"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_health_dashboard_engine.py")] + cmd, cwd=PROJECT)
    # 智能全场景进化环深度优化引擎（Round 281）
    elif "进化优化" in intent or "进化环优化" in intent or "evolution optimize" in intent.lower() or "深度优化" in intent or "进化效率" in intent or "optimization" in intent.lower() or "进化效能" in intent or "优化引擎" in intent or "效能优化" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "health", "analyze", "optimize", "patterns", "help"]):
            cmd = ["status"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_loop_deep_optimizer.py")] + cmd, cwd=PROJECT)
    # 智能全场景进化环实时监控与预警引擎（Round 283）
    elif "进化环监控" in intent or "进化预警" in intent or "evolution monitor" in intent.lower() or "监控预警" in intent or "进化状态" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "monitor", "metrics", "anomalies", "trends", "alerts", "clear", "help"]):
            cmd = ["status"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_loop_health_monitor.py")] + cmd, cwd=PROJECT)
    # 智能进化引擎架构健康度评估与自动优化引擎（Round 291）
    elif "架构健康" in intent or "引擎评估" in intent or "架构评估" in intent or "engine health" in intent.lower() or "architecture health" in intent.lower() or "进化引擎健康" in intent or "引擎优化" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["--summary"]
        if not cmd or (cmd and cmd[0] not in ["--eval", "--summary", "--plan", "--json", "help"]):
            cmd = ["--summary"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_engine_architecture_health_evaluator.py")] + cmd, cwd=PROJECT)
    # 智能全场景进化意图自主觉醒引擎（Round 288）
    elif "进化意图" in intent or "主动进化" in intent or "自主意图" in intent or "intent" in intent.lower() and "evolution" in intent.lower() or "意图驱动" in intent or "我想进化" in intent or "我需要进化" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "awaken", "evaluate", "analyze", "rank", "plan", "help"]):
            cmd = ["status"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_intent_awakening_engine.py")] + cmd, cwd=PROJECT)
    # 智能全场景自主进化意图执行闭环引擎（Round 289）
    elif "自主进化执行" in intent or "进化闭环" in intent or "意图执行" in intent or "execution loop" in intent.lower() or "进化循环" in intent or "闭环进化" in intent or "意图闭环" in intent or "进化意图执行" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["execute", "status", "history", "loops", "insights", "help"]):
            cmd = ["status"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_intent_execution_loop.py")] + cmd, cwd=PROJECT)
    # 智能全场景进化系统自我意识深度觉醒引擎（Round 304）
    elif "自我意识" in intent or "自我觉醒" in intent or "深度自我" in intent or "自我反思" in intent or "自我认知" in intent or "self_awareness" in intent.lower() or "自我意识引擎" in intent or "意识觉醒" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "reflect", "goals", "monitor", "help"]):
            cmd = ["status"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_self_awareness_deep_awakening_engine.py")] + cmd, cwd=PROJECT)
    # 智能全场景系统自主演进与持续创新引擎（Round 305）
    elif "自主演进" in intent or "持续创新" in intent or "自动进化" in intent or "演进引擎" in intent or "创新执行" in intent or "autonomous" in intent.lower() and "evolution" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "scan", "solution", "execute", "evaluate", "help"]):
            cmd = ["status"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "evolution_autonomous_evolution_engine.py")] + cmd, cwd=PROJECT)
    # 统一引擎调度中心
    elif "引擎" in intent or "engine hub" in intent.lower() or "统一调度" in intent or "引擎列表" in intent or "所有引擎" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["list"]
        # 支持 list/search/recommend/orchestrate/stats 命令
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "unified_engine_hub.py")] + cmd, cwd=PROJECT)
    # 智能对话执行一体化引擎
    elif "对话执行" in intent or "对话引擎" in intent or "智能对话" in intent or "chat" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else []
        if not cmd or (cmd and cmd[0] not in ["chat", "status", "history", "clear"]):
            cmd = ["status"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "conversation_execution_engine.py")] + cmd, cwd=PROJECT)
    # 智能执行增强与自适应优化引擎
    elif "执行增强" in intent or "策略优化" in intent or "自适应执行" in intent or "execution" in intent.lower() or "优化执行" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["recommend"]
        if not cmd or (cmd and cmd[0] not in ["track", "analyze", "optimize", "recommend", "stats"]):
            cmd = ["recommend"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "execution_enhancement_engine.py")] + cmd, cwd=PROJECT)
    # 智能工作流执行策略自动学习增强器
    elif "策略学习" in intent or "执行优化" in intent or "工作流优化" in intent or "学习策略" in intent or "workflow_strategy" in intent.lower() or "strategy_learner" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else []
        if not cmd or (cmd and cmd[0] not in ["learn", "analyze", "apply", "stats", "recommend", "clear"]):
            cmd = ["stats"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "workflow_strategy_learner.py")] + cmd, cwd=PROJECT)
    # 智能跨会话任务接续引擎
    elif "任务接续" in intent or "恢复任务" in intent or "任务进度" in intent or "未完成任务" in intent or "task_continuation" in intent.lower() or "任务追踪" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else []
        if not cmd or (cmd and cmd[0] not in ["start", "status", "resume", "complete", "fail", "list", "history", "snapshot", "delete", "env"]):
            cmd = ["list"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "task_continuation_engine.py")] + cmd, cwd=PROJECT)
    # 智能知识进化引擎
    elif "知识进化" in intent or "知识更新" in intent or "知识提取" in intent or "knowledge" in intent.lower() or "knowledge_evolution" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "evolve", "insights", "update", "stats"]):
            cmd = ["status"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "knowledge_evolution_engine.py")] + cmd, cwd=PROJECT)
    # 智能端到端服务编排与持续优化引擎
    elif "服务编排优化" in intent or "端到端优化" in intent or "协同优化" in intent or "service_orchestration" in intent.lower() or "编排优化" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "analyze", "bottlenecks", "suggest", "optimize", "track", "help"]):
            cmd = ["status"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "service_orchestration_optimizer.py")] + cmd, cwd=PROJECT)
    # 智能引擎组合推荐系统
    elif "引擎组合" in intent or "推荐引擎" in intent or "智能组合" in intent or "engine_combination" in intent.lower() or "组合推荐" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["list"]
        if not cmd or (cmd and cmd[0] not in ["list", "recommend", "execute", "stats", "analyze", "search", "help"]):
            cmd = ["list"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "engine_combination_recommender.py")] + cmd, cwd=PROJECT)
    # 智能系统自省与元认知引擎
    elif "系统自省" in intent or "自我分析" in intent or ("元认知" in intent and ("闭环" in intent or "集成" in intent or "优化" in intent or "loop" in intent.lower() or "integrate" in intent.lower() or "optimize" in intent.lower())) or "进化反思" in intent or "self_reflection" in intent.lower() or ("metacognition" in intent.lower() and ("loop" in intent.lower() or "integrate" in intent.lower() or "optimize" in intent.lower())):
        # Round 353 元认知增强：闭环/集成/优化关键词调用增强引擎
        script_path = os.path.join(SCRIPTS, "evolution_meta_cognition_deep_enhancement_engine.py")
        cmd_args = sys.argv[2:] if len(sys.argv) > 2 else []
        if "闭环" in intent or "loop" in intent.lower():
            filtered_args = ["loop"]
        elif "集成" in intent or "integrate" in intent.lower():
            filtered_args = ["integrate"]
        elif "优化" in intent or "optimize" in intent.lower():
            filtered_args = ["optimize"]
        else:
            filtered_args = cmd_args if cmd_args else ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    elif "系统自省" in intent or "自我分析" in intent or "元认知" in intent or "进化反思" in intent or "self_reflection" in intent.lower() or "metacognition" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["full"]
        if not cmd or (cmd and cmd[0] not in ["full", "health", "bottlenecks", "strategy", "recommendations", "--help", "-h", "help"]):
            cmd = ["full"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "system_self_reflection_engine.py")] + cmd, cwd=PROJECT)
    # 智能主动预测与洞察引擎
    elif "主动预测" in intent or "洞察" in intent or "前瞻" in intent or "主动建议" in intent or "预测需求" in intent or "proactive" in intent.lower() or "insight" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "predict", "insights", "suggestions", "help"]):
            cmd = ["status"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "proactive_insight_engine.py")] + cmd, cwd=PROJECT)
    # 智能用户行为序列预测与演进引擎
    elif "行为预测" in intent or "意图预测" in intent or "行为序列" in intent or "序列预测" in intent or "behavior_sequence" in intent.lower() or "intent_prediction" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "record", "predict", "evolve", "suggest", "help"]):
            cmd = ["status"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "behavior_sequence_prediction_engine.py")] + cmd, cwd=PROJECT)
    # 智能主动服务预热引擎
    elif "服务预热" in intent or "预热服务" in intent or "主动预热" in intent or "preheat" in intent.lower() or "service_preheat" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "predict", "predict_with_preheat", "preheat", "history", "help"]):
            cmd = ["status"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "service_preheat_engine.py")] + cmd, cwd=PROJECT)
    # 智能主动服务闭环增强引擎
    elif "主动服务闭环" in intent or "服务闭环" in intent or "完整服务" in intent or "主动服务增强" in intent or "service_loop" in intent.lower() or "active_service_loop" in intent.lower():
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "predict", "analyze", "execute", "help"]):
            cmd = ["status"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "active_service_loop_enhancer.py")] + cmd, cwd=PROJECT)
    # 智能全自动化服务执行引擎
    elif "全自动" in intent or "一键执行" in intent or "自动执行" in intent or "full_auto" in intent.lower() or "一键式" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "trigger", "history", "help"]):
            cmd = ["status"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "full_auto_service_execution_engine.py")] + cmd, cwd=PROJECT)
    # 智能意图深度推理引擎
    elif "意图深度" in intent or "深层意图" in intent or "意图推理" in intent or "intent_reasoning" in intent.lower() or "deep_intent" in intent.lower() or "分析意图" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "analyze", "predict", "batch", "insights", "help"]):
            cmd = ["status"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "intent_deep_reasoning_engine.py")] + cmd, cwd=PROJECT)
    # 智能用户意图自动补全引擎
    elif "意图补全" in intent or "意图增强" in intent or "补全意图" in intent or "intent_completion" in intent.lower() or "模糊输入" in intent or "理解模糊" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd or (cmd and cmd[0] not in ["status", "complete", "clear", "help"]):
            cmd = ["status"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "intent_completion_engine.py")] + cmd, cwd=PROJECT)
    # 智能跨引擎协同智能决策引擎（round 234）
    elif "跨引擎协同决策" in intent or "智能决策引擎" in intent or "引擎智能选择" in intent or "cross engine decision" in intent.lower() or "任务引擎组合" in intent or "引擎决策" in intent:
        print(f"[智能跨引擎协同智能决策引擎] 正在分析任务意图并选择最优引擎组合...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "cross_engine_smart_decision_engine.py")
        cmd_args = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        filtered_args = [arg for arg in cmd_args if arg not in ["跨引擎协同决策", "智能决策引擎", "引擎智能选择", "cross engine decision", "任务引擎组合", "引擎决策"]]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能跨引擎复杂任务规划引擎
    elif "任务规划" in intent or "复杂任务" in intent or "任务拆分" in intent or "协同执行" in intent or "task_planner" in intent.lower() or "跨引擎" in intent or "多引擎" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else []
        if not cmd or (cmd and cmd[0] not in ["plan", "execute", "status", "list", "history", "analyze", "help"]):
            cmd = ["analyze", "帮我整理今天的工作成果"]
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "cross_engine_task_planner.py")] + cmd, cwd=PROJECT)
    # 番茄钟功能
    elif "番茄钟" in intent or "pomodoro" in intent.lower() or "专注" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else []
        if "开始" in intent or "启动" in intent or "start" in intent.lower():
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "focus_reminder.py"), "pomodoro", "start"] + cmd, cwd=PROJECT)
        elif "停止" in intent or "结束" in intent or "stop" in intent.lower():
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "focus_reminder.py"), "pomodoro", "stop"], cwd=PROJECT)
        elif "状态" in intent or "status" in intent.lower():
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "focus_reminder.py"), "pomodoro", "status"], cwd=PROJECT)
        else:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "focus_reminder.py"), "pomodoro", "status"], cwd=PROJECT)
    # 休息提醒功能
    elif "休息提醒" in intent or "休息" in intent and "提醒" in intent:
        cmd = sys.argv[2:] if len(sys.argv) > 2 else []
        if "开始" in intent or "启动" in intent or "设置" in intent:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "focus_reminder.py"), "rest", "reminder"] + cmd, cwd=PROJECT)
        elif "停止" in intent or "结束" in intent or "取消" in intent:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "focus_reminder.py"), "rest", "reminder", "stop"], cwd=PROJECT)
        else:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "focus_reminder.py"), "status"], cwd=PROJECT)
    # 智能模块联动推理引擎
    elif "模块联动" in intent or "智能联动" in intent or "联动引擎" in intent or "module_linkage" in intent.lower():
        print(f"[智能模块联动引擎] 正在分析并协调多个智能模块...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "module_linkage_engine.py")
        user_input = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "有啥好玩的"
        result = subprocess.run([sys.executable, script_path, "execute", user_input], cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能跨引擎动态协同编排引擎
    elif "动态编排" in intent or "引擎协同" in intent or "自适应执行" in intent or "智能编排" in intent or "dynamic_orchestrator" in intent.lower():
        print(f"[智能跨引擎动态协同编排引擎] 正在动态分析并编排引擎组合...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "dynamic_engine_orchestrator.py")
        user_input = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
        cmd = ["status"]
        if user_input:
            cmd = ["suggestions", "--task", user_input]
        result = subprocess.run([sys.executable, script_path] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能自动化执行引擎
    elif "自动执行" in intent or "执行计划" in intent or "执行编排" in intent or "auto_execution" in intent.lower() or "auto execute" in intent.lower():
        print(f"[智能自动化执行引擎] 正在自动执行编排计划...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "auto_execution_engine.py")
        user_input = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
        cmd = []
        if user_input:
            # 解析命令
            parts = user_input.split()
            if parts[0] in ["status", "history", "set_mode", "execute", "suggest"]:
                cmd = [parts[0]]
                if parts[0] == "set_mode" and len(parts) > 1:
                    cmd.extend(["--mode", parts[1]])
                elif parts[0] in ["execute", "suggest"] and len(parts) > 1:
                    # 剩余部分作为计划
                    plan_input = " ".join(parts[1:])
                    cmd.extend(["--" + ("plan" if parts[0] == "execute" else "plan"), plan_input])
        if not cmd:
            cmd = ["status"]
        result = subprocess.run([sys.executable, script_path] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能进化执行智能决策集成引擎（round 235）
    elif "进化决策集成" in intent or "进化智能决策" in intent or "智能进化执行" in intent or "evolution decision" in intent.lower() or "进化引擎选择" in intent:
        print(f"[智能进化执行智能决策集成引擎] 正在分析进化任务并智能选择引擎组合...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_decision_integration.py")
        cmd_args = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd_args:
            cmd_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能进化决策与执行深度集成引擎（round 236）
    elif "进化决策执行" in intent or "决策执行闭环" in intent or "decision execution" in intent.lower() or "进化闭环" in intent:
        print(f"[智能进化决策与执行深度集成引擎] 正在执行决策-执行完整闭环...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_decision_execution_loop.py")
        cmd_args = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd_args:
            cmd_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能自适应进化策略动态调优引擎（round 237）
    elif "进化自适应调优" in intent or "自适应优化" in intent or "策略动态调整" in intent or "adaptive optimize" in intent.lower() or "进化优化" in intent or "策略调优" in intent:
        print(f"[智能自适应进化策略动态调优引擎] 正在执行策略动态调优...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_adaptive_optimizer.py")
        cmd_args = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd_args:
            cmd_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能进化多轮迭代协同增强引擎（round 238）
    elif "多轮协同" in intent or "迭代进化" in intent or "协同进化" in intent or "进化协调" in intent or "iteration coordination" in intent.lower() or "evolution iteration" in intent.lower():
        print(f"[智能进化多轮迭代协同增强引擎] 正在执行多轮迭代协同...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_iteration_coordination.py")
        cmd_args = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd_args:
            cmd_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能进化闭环自我优化引擎（round 242）
    elif "进化自我优化" in intent or "闭环优化" in intent or "自我迭代" in intent or "优化进化环" in intent or "self optimize" in intent.lower() or "loop self" in intent.lower() or "进化环优化" in intent:
        print(f"[智能进化闭环自我优化引擎] 正在执行进化环自我优化...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_loop_self_optimizer.py")
        cmd_args = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd_args:
            cmd_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能进化闭环自动集成执行引擎（round 243）
    elif "进化自动集成" in intent or "集成优化" in intent or "闭环执行" in intent or "auto integrate" in intent.lower() or "集成执行" in intent or "进化闭环自动化" in intent:
        print(f"[智能进化闭环自动集成执行引擎] 正在执行进化闭环自动集成...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_auto_integrated_executor.py")
        cmd_args = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd_args:
            cmd_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化知识图谱深度推理引擎（round 298）
    elif "知识图谱推理" in intent or "图谱推理" in intent or "知识推理" in intent or "kg reasoning" in intent.lower() or "knowledge graph" in intent.lower() or "图谱分析" in intent or "进化知识图谱" in intent or "隐藏机会" in intent or "创新模式识别" in intent:
        print(f"[智能全场景进化知识图谱深度推理引擎] 正在分析进化知识图谱...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_knowledge_graph_reasoning.py")
        cmd_args = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd_args:
            cmd_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化知识图谱推理与元优化深度集成引擎（round 299）
    elif "知识图谱元优化" in intent or "图谱元优化" in intent or "kg meta" in intent.lower() or "图谱优化" in intent or "图谱推理优化" in intent or "知识图谱深度集成" in intent or "evolution kg meta" in intent.lower() or "kg_meta" in intent.lower() or "图谱驱动优化" in intent or "深度集成闭环" in intent:
        print(f"[智能全场景进化知识图谱推理与元优化深度集成引擎] 正在执行深度集成闭环...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_kg_meta_integration.py")
        cmd_args = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd_args:
            cmd_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环知识图谱主动推理与前瞻性洞察生成引擎（round 605）
    elif "知识图谱前瞻" in intent or "kg前瞻" in intent or "kg预测" in intent or "图谱主动推理" in intent or "proactive insight engine" in intent.lower() or "kg_proactive" in intent.lower() or "insight generation engine" in intent.lower() or "洞察生成引擎" in intent or ("前瞻" in intent and "洞察" in intent):
        print(f"[知识图谱主动推理与前瞻性洞察生成引擎] 正在分析知识图谱并生成前瞻性洞察...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_kg_proactive_reasoning_insight_engine.py")
        cmd_args = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd_args:
            cmd_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环元进化方法论自省与递归优化引擎（round 606）
    elif "元进化自省" in intent or "方法论优化" in intent or "进化策略分析" in intent or "meta methodology" in intent.lower() or "self reflection optimizer" in intent.lower() or "元方法论" in intent or "方法论自省" in intent or "递归优化" in intent:
        print(f"[元进化方法论自省与递归优化引擎] 正在分析进化方法论并生成优化建议...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_methodology_self_reflection_optimizer.py")
        cmd_args = sys.argv[2:] if len(sys.argv) > 2 else ["--status"]
        if not cmd_args:
            cmd_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环元进化多模态感知深度融合与自适应增强引擎（round 607）
    elif "多模态融合" in intent or "跨模态感知" in intent or "多模态感知" in intent or "multimodal fusion" in intent.lower() or "multimodal perception" in intent.lower() or "跨模态" in intent or "模态融合" in intent or "模态感知" in intent or "multimodal" in intent.lower() or "多模态增强" in intent or "多模态分析" in intent:
        print(f"[元进化多模态感知深度融合与自适应增强引擎] 正在处理多模态感知融合...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_multimodal_perception_deep_fusion_engine.py")
        cmd_args = sys.argv[2:] if len(sys.argv) > 2 else ["--status"]
        if not cmd_args:
            cmd_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景跨引擎知识深度融合与主动洞察生成引擎（round 320）
    elif "知识融合" in intent or "跨引擎洞察" in intent or "主动洞察" in intent or "深度融合" in intent or "智能洞察" in intent or "洞察生成" in intent or "cross engine fusion" in intent.lower() or "knowledge fusion" in intent.lower() or "proactive insight" in intent.lower() or "主动洞察生成" in intent or "跨引擎知识" in intent:
        print(f"[智能全场景跨引擎知识深度融合与主动洞察生成引擎] 正在融合跨引擎知识并生成洞察...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_cross_engine_knowledge_fusion.py")
        # 始终生成主动洞察
        cmd_args = ["--generate"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景自主进化闭环全自动化引擎（round 300）
    elif "进化全自动化" in intent or "全自动进化" in intent or "无人值守进化" in intent or "一键进化" in intent or "进化环自动" in intent or "自动进化环" in intent or "full auto" in intent.lower() or "auto loop" in intent.lower() or "evolution auto" in intent.lower() or "全自动化闭环" in intent:
        print(f"[智能全场景自主进化闭环全自动化引擎] 正在执行全自动化进化闭环...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_full_auto_loop.py")
        cmd_args = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd_args:
            cmd_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环持续创新引擎（round 307）
    elif "创新机会发现" in intent or "持续创新引擎" in intent or "进化创新分析" in intent or "进化创新计划" in intent or "创新趋势分析" in intent or "continuous innovation engine" in intent.lower() or "innovation opportunities" in intent.lower() or "进化环创新" in intent:
        print(f"[智能全场景进化环持续创新引擎] 正在执行持续创新分析...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_continuous_innovation_engine.py")
        cmd_args = sys.argv[2:] if len(sys.argv) > 2 else ["analyze"]
        if not cmd_args:
            cmd_args = ["analyze"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环跨模态协同增强引擎（round 308）
    elif "跨模态进化" in intent or "模态协同" in intent or "多模态增强" in intent or "cross-modal" in intent.lower() or "跨模态" in intent or "多模态" in intent or "模态融合" in intent or "crossmodal" in intent.lower():
        print(f"[智能全场景进化环跨模态协同增强引擎] 正在执行跨模态协同分析...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_crossmodal_enhancer.py")
        cmd_args = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd_args:
            cmd_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环自主实验与假设验证引擎（round 309）
    elif "进化实验" in intent or "假设验证" in intent or "实验验证" in intent or "方法论" in intent or "hypothesis" in intent.lower() or "experiment" in intent.lower() or "验证假设" in intent:
        print(f"[智能全场景进化环自主实验与假设验证引擎] 正在执行进化假设验证...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_hypothesis_verification_engine.py")
        cmd_args = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd_args:
            cmd_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化质量保障与持续改进闭环引擎（round 302）
    elif "进化质量保障" in intent or "质量保障" in intent and "进化" in intent or "持续改进" in intent or "模块验证" in intent or "集成测试" in intent or "质量报告" in intent or "quality assurance" in intent.lower() or "quality loop" in intent.lower() or "evolution quality" in intent.lower() or "qa loop" in intent.lower() or "质量闭环" in intent:
        print(f"[智能全场景进化质量保障与持续改进闭环引擎] 正在执行质量保障循环...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_quality_assurance_loop.py")
        cmd_args = sys.argv[2:] if len(sys.argv) > 2 else ["full"]
        if not cmd_args:
            cmd_args = ["full"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环智能协同与自主决策增强引擎（round 303）
    elif "智能协同" in intent or "协同编排" in intent or "协同决策" in intent or "协同增强" in intent or "多引擎协同" in intent or "collaboration intelligence" in intent.lower() or "智能团队" in intent:
        print(f"[智能全场景进化环智能协同与自主决策增强引擎] 正在分析任务并组建协同团队...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_collaboration_intelligence_enhancer.py")
        cmd_args = sys.argv[2:] if len(sys.argv) > 2 else ["recommend", "--task", intent]
        if not cmd_args or len(cmd_args) < 2:
            cmd_args = ["recommend", "--task", intent]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能进化元模式发现引擎（round 244）
    elif "进化元模式" in intent or "元模式发现" in intent or "meta pattern" in intent.lower() or "meta" in intent.lower() or "进化模式分析" in intent or "模式发现" in intent or intent == "patterns":
        print(f"[智能进化元模式发现引擎] 正在分析进化模式...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_pattern_discovery.py")
        cmd_args = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd_args:
            cmd_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能进化新引擎自动创造引擎（round 245）
    elif "创造新引擎" in intent or "自动创造引擎" in intent or "生成新能力" in intent or "engine creator" in intent.lower() or "auto create" in intent.lower() or "创造能力" in intent or "自动生成模块" in intent:
        print(f"[智能进化新引擎自动创造引擎] 正在分析并创造新引擎...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_engine_auto_creator.py")
        cmd_args = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd_args:
            cmd_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能进化新引擎实用化引擎（round 246）
    elif "practical" in intent.lower() or "实用化" in intent or "引擎实用化" in intent or "engine practical" in intent.lower() or "真正创造" in intent or "新引擎实用" in intent:
        print(f"[智能进化新引擎实用化引擎] 正在将自动创造能力实用化...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_engine_practicalizer.py")
        cmd_args = sys.argv[2:] if len(sys.argv) > 2 else ["status"]
        if not cmd_args:
            cmd_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能决策可解释性增强器
    elif "解释决策" in intent or "为什么推荐" in intent or "执行解释" in intent or "决策解释" in intent or "explain" in intent.lower():
        print(f"[智能决策可解释性增强器] 正在解释决策原因...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "decision_explainer_engine.py")
        user_input = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
        cmd = []
        if user_input:
            parts = user_input.split()
            if parts[0] in ["status", "explain", "workflow", "failure", "progress"]:
                cmd = [parts[0]]
                # 处理后续参数
                if len(parts) > 1:
                    if parts[0] == "explain" and "--task" in user_input:
                        # 提取 task 和 engines
                        try:
                            task_idx = parts.index("--task") + 1 if "--task" in parts else -1
                            engines_idx = parts.index("--engines") + 1 if "--engines" in parts else -1
                            if task_idx > 0 and engines_idx > 0:
                                cmd = ["explain", "--task", " ".join(parts[task_idx:engines_idx-1])]
                                # 找到 engines 后的引擎列表
                                engines = []
                                for i in range(engines_idx, len(parts)):
                                    if parts[i].startswith("--"):
                                        break
                                    engines.append(parts[i])
                                cmd.extend(["--engines"] + engines)
                        except:
                            cmd = ["status"]
                    elif parts[0] in ["workflow", "failure", "progress"]:
                        cmd = [parts[0]]
                        if len(parts) > 1:
                            cmd.extend(parts[1:])
        if not cmd:
            cmd = ["status"]
        result = subprocess.run([sys.executable, script_path] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能推荐-编排-执行-解释完整闭环引擎
    elif "服务闭环" in intent or "完整闭环" in intent or "推荐编排" in intent or "编排执行" in intent or "推荐执行" in intent or "service_loop" in intent.lower() or "闭环引擎" in intent:
        print(f"[智能推荐-编排-执行-解释完整闭环引擎] 正在执行完整服务闭环...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "service_loop_closer.py")
        user_input = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
        cmd = []
        if user_input:
            parts = user_input.split()
            if parts[0] in ["status", "run", "explain"]:
                cmd = [parts[0]]
                if len(parts) > 1 and parts[0] == "run":
                    # 合并剩余部分作为 intent
                    cmd.extend(["--intent", " ".join(parts[1:])])
            elif parts[0].startswith("--"):
                cmd = ["run", "--intent", user_input]
            else:
                cmd = ["run", "--intent", user_input]
        if not cmd:
            cmd = ["status"]
        result = subprocess.run([sys.executable, script_path] + cmd, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能任务协调中心
    elif "协调中心" in intent or "智能处理" in intent or "coordinator" in intent.lower():
        print(f"[智能任务协调中心] 正在协调处理您的任务...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "coordinator.py")
        user_input = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "有啥好玩的"
        result = subprocess.run([sys.executable, script_path, user_input], cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能模块协同调度中心
    elif "模块协同" in intent or "智能协同" in intent or "模块调度" in intent or "module_coordinator" in intent.lower():
        print(f"[智能模块协同调度中心] 正在分析并调度相关模块...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "intelligent_module_coordinator.py")
        user_input = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "有啥好玩的"
        result = subprocess.run([sys.executable, script_path, "execute", user_input], cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 用户行为自动学习与适应
    elif "行为" in intent or "学习" in intent or "习惯" in intent or "偏好" in intent or "用户行为" in intent or "我的习惯" in intent:
        print(f"[用户行为学习] 正在分析您的行为模式...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "user_behavior_learner.py")
        # 参数处理
        cmd_args = []
        if "高频" in intent or "频繁" in intent or "最常用" in intent:
            cmd_args = ["frequent"]
        elif "推荐" in intent and ("建议" in intent or "智能" in intent):
            cmd_args = ["recommend"]
        elif "时间" in intent and "偏好" in intent:
            # 提取具体时间段
            for period in ["凌晨", "早晨", "上午", "中午", "下午", "傍晚", "晚上"]:
                if period in intent:
                    cmd_args = ["preference", period]
                    break
            if not cmd_args:
                cmd_args = ["preference"]
        elif "最近" in intent or "历史" in intent:
            limit = 5
            if any(str(i) in intent for i in range(1, 10)):
                for i in range(1, 10):
                    if str(i) in intent:
                        limit = i
                        break
            cmd_args = ["recent", str(limit)]
        elif "统计" in intent or "成功率" in intent:
            cmd_args = ["stats"]
        elif "摘要" in intent or "总结" in intent or "概览" in intent:
            cmd_args = ["summary"]
        elif "清除" in intent or "重置" in intent:
            cmd_args = ["clear"]
        elif "开启" in intent or "启用" in intent:
            cmd_args = ["enable"]
        elif "关闭" in intent or "停用" in intent:
            cmd_args = ["disable"]
        else:
            cmd_args = []  # 默认显示摘要

        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景记忆网络与主动意图预测引擎（Round 259）
    elif "记忆网络" in intent or "memory network" in intent.lower() or "intent predictor" in intent.lower() or "行为模式学习" in intent or "预测需求" in intent or "提前准备服务" in intent:
        print(f"[智能全场景记忆网络与主动意图预测引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "memory_network_intent_predictor.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["status"]
        # 过滤掉意图关键词
        filter_words = ["记忆网络", "memory network", "intent predictor", "行为模式学习", "预测需求", "提前准备服务"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words and not any(w in arg.lower() for w in filter_words)]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能语音理解与对话智能融合引擎（Round 260）
    elif "语音对话" in intent or "语音聊天" in intent or "voice conversation" in intent.lower() or "语音智能" in intent or "语音理解" in intent or "voice_intelligence" in intent.lower():
        print(f"[智能语音理解与对话智能融合引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "voice_conversation_intelligence.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["status"]
        # 过滤掉意图关键词
        filter_words = ["语音对话", "语音聊天", "voice conversation", "语音智能", "语音理解", "voice_intelligence"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words and not any(w in arg.lower() for w in filter_words)]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 上下文记忆与意图预测
    elif "上下文" in intent or "记忆" in intent or "历史记录" in intent or "意图预测" in intent or "预测意图" in intent or "上下文记忆" in intent:
        print(f"[上下文记忆] 正在处理您的请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "context_memory.py")
        # 参数处理
        cmd_args = []
        if "添加" in intent or "记录" in intent or "记住" in intent or "记录" in intent:
            # 提取要记录的内容 - 跳过关键词后的内容
            skip_words = ["添加", "记录", "记住", "上下文", "记忆", "历史记录", "意图预测", "预测意图", "上下文记忆"]
            content_parts = [arg for arg in sys.argv[1:] if not any(sw in arg for sw in skip_words)]
            if content_parts:
                cmd_args = ["add", " ".join(content_parts)]
            else:
                cmd_args = ["add", intent]
        elif "预测" in intent or "下一个" in intent:
            cmd_args = ["predict"]
            if "当前" in intent:
                skip_words = ["上下文", "记忆", "历史记录", "意图预测", "预测意图", "上下文记忆", "当前", "预测", "下一个"]
                content_parts = [arg for arg in sys.argv[1:] if not any(sw in arg for sw in skip_words)]
                if content_parts:
                    cmd_args = ["predict", "--current", content_parts[0]]
        elif "最近" in intent or "历史" in intent:
            cmd_args = ["recent"]
            for i in range(1, 10):
                if str(i) in intent:
                    cmd_args = ["recent", "--count", str(i)]
                    break
        elif "搜索" in intent or "查找" in intent:
            skip_words = ["上下文", "记忆", "历史记录", "意图预测", "预测意图", "上下文记忆", "搜索", "查找"]
            content_parts = [arg for arg in sys.argv[1:] if not any(sw in arg for sw in skip_words)]
            if content_parts:
                cmd_args = ["search", content_parts[0]]
            else:
                cmd_args = ["search", intent]
        elif "清空" in intent or "清除" in intent:
            cmd_args = ["clear"]
        elif "统计" in intent:
            cmd_args = ["stats"]
        else:
            cmd_args = ["stats"]

        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能任务记忆与预测中心
    elif intent in ("任务记忆", "任务历史", "任务回顾", "任务统计", "任务分析"):
        print(f"[任务记忆] 正在处理您的请求...", file=sys.stderr)
        # 加载任务记忆模块
        from scripts.task_memory import TaskMemory
        tm = TaskMemory()
        if "历史" in intent or "回顾" in intent:
            # 查看任务历史
            history = tm.get_task_history(10)
            if history:
                print("最近任务历史:")
                for task in history:
                    print(f"  - {task['id']} ({task['timestamp']}): {task['info']}")
            else:
                print("暂无任务历史记录")
        elif "统计" in intent or "分析" in intent:
            # 查看任务统计
            stats = tm.get_statistics()
            print("任务统计信息:")
            print(f"  总任务数: {stats['total_tasks']}")
            print(f"  成功任务数: {stats['completed_tasks']}")
            print(f"  失败任务数: {stats['failed_tasks']}")
            print(f"  完成率: {stats['completion_rate']:.2%}")
            if stats['intent_distribution']:
                print("任务意图分布:")
                for intent, count in stats['intent_distribution'].items():
                    print(f"  - {intent}: {count} 次")
        else:
            # 默认显示任务历史
            history = tm.get_task_history(5)
            if history:
                print("最近任务历史:")
                for task in history:
                    print(f"  - {task['id']} ({task['timestamp']}): {task['info']}")
            else:
                print("暂无任务历史记录")
    elif intent in ("意图预测", "预测意图", "主动任务", "主动规划", "智能规划"):
        print(f"[智能规划] 正在处理您的请求...", file=sys.stderr)
        # 加载任务记忆模块进行意图预测和主动规划
        from scripts.task_memory import TaskMemory
        tm = TaskMemory()
        if "预测" in intent or "意图" in intent:
            # 预测用户意图
            context = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
            prediction = tm.predict_user_intent(context)
            print("用户意图预测:")
            print(f"  预测结果: {prediction['predicted_intent']}")
            if prediction['suggestions']:
                print("  建议:")
                for suggestion in prediction['suggestions']:
                    print(f"    - {suggestion}")
        elif "主动" in intent or "规划" in intent:
            # 主动规划任务
            context = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
            plan = tm.plan_active_task(context)
            print("主动任务规划:")
            print(f"  时间戳: {plan['timestamp']}")
            print(f"  上下文: {plan['context']}")
            print(f"  优先级: {plan['priority']}")
            if plan['suggested_tasks']:
                print("  建议任务:")
                for task in plan['suggested_tasks']:
                    print(f"    - {task['description']} (优先级: {task['priority']})")
    # 智能任务编排与工作流自动化
    elif "工作流" in intent or "编排" in intent or "workflow" in intent.lower() or "执行多个任务" in intent or "一系列任务" in intent or "智能规划" in intent:
        print(f"[智能任务编排] 正在处理您的工作流请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "workflow_orchestrator.py")
        # 参数映射：中文 -> 英文
        param_mapping = {
            "列表": "list", "查看列表": "list", "列出": "list",
            "状态": "status", "查看状态": "status",
            "执行": "run", "运行": "run",
            "创建": "create",
            "预览": "--dry-run", "dry-run": "--dry-run", "干跑": "--dry-run",
            "分析": "analyze", "智能分析": "analyze",
            "规划": "plan", "智能规划": "plan",
            "smart": "--smart"
        }
        # 过滤掉触发关键词
        skip_keywords = ["工作流", "编排", "workflow", "执行多个任务", "一系列任务", "智能规划"]
        cmd_args = []
        for arg in sys.argv[1:]:
            if arg in skip_keywords:
                continue  # 跳过触发关键词
            mapped = param_mapping.get(arg)
            if mapped:
                cmd_args.append(mapped)
            elif arg.startswith("-"):
                cmd_args.append(arg)  # 保留原始参数如 --intent
            else:
                cmd_args.append(arg)
        if not cmd_args:
            cmd_args = ["list"]  # 默认列出工作流
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 主动建议引擎
    elif "主动建议" in intent or "智能建议" in intent or "获取建议" in intent or "active suggestion" in intent.lower():
        print(f"[主动建议引擎] 正在生成主动建议...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "active_suggestion_engine.py")
        result = subprocess.run([sys.executable, script_path], cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 定时任务调度器
    elif "定时任务" in intent or "任务调度" in intent or "schedule" in intent.lower() or "scheduler" in intent.lower():
        print(f"[定时任务调度器] 正在处理您的定时任务请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "task_scheduler.py")
        # 参数处理
        cmd_args = []
        for arg in sys.argv[1:]:
            if arg in ["定时任务", "任务调度", "schedule", "scheduler"]:
                continue  # 跳过触发关键词
            cmd_args.append(arg)
        if not cmd_args:
            cmd_args = ["--list"]  # 默认列出任务
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 场景后续建议
    elif "后续建议" in intent or "场景建议" in intent or "任务建议" in intent or "followup" in intent.lower():
        # 从参数中获取场景名称
        scenario_name = None
        if len(sys.argv) > 2:
            scenario_name = sys.argv[2]
        if not scenario_name:
            # 尝试从 intent 中提取场景名
            for kw in ["看电影", "听音乐", "刷知乎", "看新闻", "iHaier", "绩效", "消息"]:
                if kw in intent:
                    scenario_name = kw
                    break

        if scenario_name:
            print(f"[场景后续建议] 正在为场景 '{scenario_name}' 生成后续建议...", file=sys.stderr)
            script_path = os.path.join(SCRIPTS, "scenario_followup_recommender.py")
            result = subprocess.run([sys.executable, script_path, scenario_name], cwd=PROJECT, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            if result.returncode != 0 and result.stderr:
                print(result.stderr, file=sys.stderr)
            sys.exit(0 if result.returncode == 0 else result.returncode)
        else:
            print("用法: do.py 后续建议 <场景名>", file=sys.stderr)
            print("示例: do.py 后续建议 看电影", file=sys.stderr)
            sys.exit(1)
    # 多模态情感理解与智能响应增强引擎 (需要在普通情感交互之前匹配)
    elif "多模态情感" in intent or "多维度情感" in intent or "情感理解" in intent or "情感增强" in intent or "multimodal emotion" in intent.lower() or "emotion understanding" in intent.lower():
        print(f"[多模态情感理解引擎] 正在综合分析您的情感状态...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "multimodal_emotion_understanding_engine.py")
        user_input = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
        if user_input:
            # 使用 -c 选项执行代码，需要先添加路径
            import_path = SCRIPTS.replace('\\', '\\\\')
            result = subprocess.run([sys.executable, "-c",
                f"import sys; sys.path.insert(0, r'{import_path}'); "
                f"from multimodal_emotion_understanding_engine import MultimodalEmotionUnderstandingEngine; "
                f"engine = MultimodalEmotionUnderstandingEngine(); "
                f"print(engine.analyze_and_respond('''{user_input}'''))"],
                cwd=PROJECT, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            if result.returncode != 0 and result.stderr:
                print(result.stderr, file=sys.stderr)
            sys.exit(0 if result.returncode == 0 else result.returncode)
    # 跨模态深度融合推理引擎
    elif "跨模态" in intent or "多模态融合" in intent or "cross modal" in intent.lower() or "multi-modal" in intent.lower() or "fusion" in intent.lower() or "看图说话" in intent or "视觉语音" in intent or "语音执行" in intent or "深度融合" in intent or "融合推理" in intent or "跨模态理解" in intent:
        print(f"[跨模态深度融合推理引擎] 正在处理多模态融合请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "cross_modal_fusion_reasoning_engine.py")
        # 确定子命令：如果用户输入中包含特定关键词则执行相应功能
        if "状态" in intent or "status" in intent.lower():
            cmd_args = ["status"]
        elif "能力" in intent or "capabilities" in intent.lower() or "列表" in intent:
            cmd_args = ["capabilities"]
        elif "融合" in intent or "reason" in intent.lower() or "推理" in intent:
            cmd_args = ["fusion"]
        else:
            cmd_args = ["capabilities"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 情感交互
    elif "情感" in intent or "心情" in intent or "好累" in intent or "好困" in intent or "开心" in intent or "难过" in intent or "焦虑" in intent or "emotion" in intent.lower() or "feeling" in intent.lower() or "疲惫" in intent:
        print(f"[情感交互] 正在分析您的情感状态...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "emotional_interaction.py")
        # 传递用户的完整输入作为参数
        user_input = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
        if user_input:
            result = subprocess.run([sys.executable, script_path, user_input], cwd=PROJECT, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            if result.returncode != 0 and result.stderr:
                print(result.stderr, file=sys.stderr)
            sys.exit(0 if result.returncode == 0 else result.returncode)
    # 意图智能识别与推荐
    elif "推荐" in intent or "有啥" in intent or "干嘛" in intent or "干什么" in intent or "无聊" in intent or "suggest" in intent.lower() or "recommend" in intent.lower():
        print(f"[意图识别] 正在分析您的意图并生成推荐...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "intent_recognition.py")
        # 传递用户的完整输入作为参数
        user_input = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "有啥好玩的"
        result = subprocess.run([sys.executable, script_path, user_input], cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 语音交互引擎
    elif "语音交互" in intent or "语音命令" in intent or "voice" in intent.lower() or "语音识别" in intent:
        print(f"[语音交互引擎] 正在启动语音交互...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "voice_interaction_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--help"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["语音交互", "语音命令", "语音识别", "voice"]]
        if not filtered_args:
            filtered_args = ["--help"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 语音合成引擎 (TTS)
    elif "语音合成" in intent or "语音回复" in intent or "tts" in intent.lower() or "text to speech" in intent.lower() or "读出来" in intent or "读一下" in intent:
        print(f"[语音合成引擎] 正在合成语音...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "tts_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--help"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["语音合成", "语音回复", "tts", "text to speech", "读出来", "读一下"]]
        if not filtered_args:
            filtered_args = ["--help"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能场景推荐
    elif "场景推荐" in intent or "推荐场景" in intent or "推荐计划" in intent or "场景计划" in intent or "recommend" in intent.lower() or "suggestion" in intent.lower():
        print(f"[智能场景推荐] 正在为您生成个性化场景推荐...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "scenario_recommender.py")
        # 传递参数给推荐引擎
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["get"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["场景推荐", "推荐场景", "推荐计划", "场景计划"]]
        if not filtered_args:
            filtered_args = ["get"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能自适应场景选择引擎
    elif "自适应场景" in intent or "智能场景选择" in intent or "场景选择" in intent or "adaptive scene" in intent.lower() or "context aware" in intent.lower() or "当前情境" in intent:
        print(f"[智能自适应场景选择引擎] 正在分析当前情境并选择最佳场景...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "adaptive_scene_selector.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["analyze"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["自适应场景", "智能场景选择", "场景选择", "adaptive scene", "context aware", "当前情境"]]
        if not filtered_args:
            filtered_args = ["analyze"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能场景执行联动引擎
    elif "场景执行联动" in intent or "场景链" in intent or "场景串联" in intent or "执行多个场景" in intent or "scene execution" in intent.lower() or "scene chain" in intent.lower() or "execute scene" in intent.lower():
        print(f"[智能场景执行联动引擎] 正在分析任务并执行场景链...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "scene_execution_linkage_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--help"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["场景执行联动", "场景链", "场景串联", "执行多个场景", "scene execution", "scene chain", "execute scene"]]
        if not filtered_args:
            filtered_args = ["--help"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能跨场景协同推理引擎
    elif "跨场景" in intent or "场景协同" in intent or "多场景分析" in intent or "cross scene" in intent.lower() or "scene reasoning" in intent.lower() or "多场景" in intent or "场景推理" in intent:
        print(f"[智能跨场景协同推理引擎] 正在分析跨场景任务...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "cross_scene_reasoning_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--help"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["跨场景", "场景协同", "多场景分析", "cross scene", "scene reasoning", "多场景", "场景推理"]]
        if not filtered_args:
            filtered_args = ["--help"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景智能体自主协作与社会化推理引擎
    elif "智能体协作" in intent or "多智能体" in intent or "社会化推理" in intent or "智能体社会" in intent or "multi agent" in intent.lower() or "agent collaboration" in intent.lower() or "social reasoning" in intent.lower() or "协作解决问题" in intent:
        print(f"[智能体自主协作引擎] 正在启动多智能体协作...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "multi_agent_social_reasoning_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--help"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["智能体协作", "多智能体", "社会化推理", "智能体社会", "multi agent", "agent collaboration", "social reasoning", "协作解决问题"]]
        if not filtered_args:
            filtered_args = ["--help"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景智能体元协作与社会化学习增强引擎（round 266）
    elif "元协作" in intent or "智能体学习" in intent or "群体智慧" in intent or "经验共享" in intent or "meta collaboration" in intent.lower() or "collective wisdom" in intent.lower() or "experience sharing" in intent.lower() or "社会化学习" in intent or "协作进化" in intent:
        print(f"[智能体元协作与社会化学习引擎] 正在启动增强版多智能体协作...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "multi_agent_meta_collaboration_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--help"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["元协作", "智能体学习", "群体智慧", "经验共享", "meta collaboration", "collective wisdom", "experience sharing", "社会化学习", "协作进化"]]
        if not filtered_args:
            filtered_args = ["--help"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景智能体协作闭环增强引擎
    elif "协作闭环" in intent or "智能体协作闭环" in intent or "团队协作增强" in intent or "collaboration loop" in intent.lower() or "closed loop collaboration" in intent.lower() or "智能体进化" in intent or "collaboration evolution" in intent.lower():
        print(f"[智能全场景智能体协作闭环增强引擎] 正在启动协作闭环...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "multi_agent_collaboration_closed_loop_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--help"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["协作闭环", "智能体协作闭环", "团队协作增强", "collaboration loop", "closed loop collaboration", "智能体进化", "collaboration evolution"]]
        if not filtered_args:
            filtered_args = ["--help"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景统一智能体协同调度引擎 (Round 268)
    elif "统一调度" in intent or "智能体调度" in intent or "协同调度" in intent or "统一智能体" in intent or "unified orchestrator" in intent.lower() or "agent orchestration" in intent.lower() or "multi-agent orch" in intent.lower() or "统一调度引擎" in intent:
        print(f"[智能全场景统一智能体协同调度引擎] 正在启动统一调度...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "unified_multi_agent_orchestrator.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--help"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["统一调度", "智能体调度", "协同调度", "统一智能体", "unified orchestrator", "agent orchestration", "multi-agent orch", "统一调度引擎"]]
        if not filtered_args:
            filtered_args = ["--help"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景自主进化闭环引擎 (Round 269)
    elif "自主进化" in intent or "进化闭环" in intent or "自动进化" in intent or "autonomous evolution" in intent.lower() or "evolution loop" in intent.lower() or "自动发现能力" in intent or "能力组合创新" in intent:
        print(f"[智能全场景自主进化闭环引擎] 正在启动自主进化...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "autonomous_evolution_loop_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--help"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["自主进化", "进化闭环", "自动进化", "autonomous evolution", "evolution loop", "自动发现能力", "能力组合创新"]]
        if not filtered_args:
            filtered_args = ["--help"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景自主进化闭环与统一调度引擎深度集成 (Round 270)
    elif "深度集成进化" in intent or "进化调度" in intent or "自主进化调度" in intent or "智能进化协同" in intent or "evolution orchestrate" in intent.lower() or "evolution integration" in intent.lower():
        print(f"[智能全场景自主进化闭环与统一调度引擎深度集成] 正在启动深度集成...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_orchestrator_deep_integration.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--help"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["深度集成进化", "进化调度", "自主进化调度", "智能进化协同", "evolution orchestrate", "evolution integration"]]
        if not filtered_args:
            filtered_args = ["--help"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景智能体自主决策与执行闭环引擎 (Round 276)
    elif "自主决策" in intent or "决策执行" in intent or "自主执行" in intent or "autonomous decision" in intent.lower() or "auto decision" in intent.lower() or "decision execution" in intent.lower() or "自主决策执行" in intent or "智能决策闭环" in intent:
        print(f"[智能全场景智能体自主决策与执行闭环引擎] 正在启动自主决策与执行...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "autonomous_decision_execution_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--help"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["自主决策", "决策执行", "自主执行", "autonomous decision", "auto decision", "decision execution", "自主决策执行", "智能决策闭环"]]
        if not filtered_args:
            filtered_args = ["--help"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能文件管理引擎
    elif "文件管理" in intent or "整理文件" in intent or "文件整理" in intent or "搜索文件" in intent or "文件搜索" in intent or "分析文件" in intent or "文件分析" in intent or "file manager" in intent.lower() or "organize files" in intent.lower():
        print(f"[智能文件管理引擎] 正在处理文件管理请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "file_manager_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--help"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["文件管理", "整理文件", "文件整理", "搜索文件", "文件搜索", "分析文件", "文件分析", "file manager", "organize files"]]
        if not filtered_args:
            filtered_args = ["--help"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能工作流引擎
    elif "工作流" in intent or "任务规划" in intent or "复杂任务" in intent or "workflow" in intent.lower() or "task plan" in intent.lower() or "plan task" in intent.lower():
        print(f"[智能工作流引擎] 正在处理工作流请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "workflow_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--help"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["工作流", "任务规划", "复杂任务", "workflow", "task plan", "plan task"]]
        if not filtered_args:
            filtered_args = ["templates"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能工作流推荐与优化引擎
    elif "工作流推荐" in intent or "智能推荐工作流" in intent or "workflow recommend" in intent.lower() or "工作流优化" in intent or "workflow optimize" in intent.lower() or "智能工作流" in intent or "推荐工作流" in intent:
        print(f"[智能工作流推荐与优化引擎] 正在处理工作流推荐请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "workflow_smart_recommender.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["recommend"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["工作流推荐", "智能推荐工作流", "workflow recommend", "工作流优化", "workflow optimize", "智能工作流", "推荐工作流"]]
        if not filtered_args:
            filtered_args = ["recommend"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能工作流自动生成引擎
    elif "生成工作流" in intent or "自动生成工作流" in intent or "generate workflow" in intent.lower() or "创建工作流" in intent or "生成任务步骤" in intent or "自动生成步骤" in intent or "生成计划" in intent or "工作流生成" in intent:
        print(f"[智能工作流自动生成引擎] 正在生成工作流...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "workflow_auto_generator.py")
        # 解析命令参数 - 提取任务描述
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 过滤掉意图关键词，保留任务描述
        filter_kw = ["生成工作流", "自动生成工作流", "generate workflow", "创建工作流", "生成任务步骤", "自动生成步骤", "生成计划", "工作流生成"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_kw]
        if not filtered_args:
            filtered_args = ["--help"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能工作流质量保障与自动优化引擎
    elif "工作流质量" in intent or "质量分析" in intent or "质量监控" in intent or "工作流统计" in intent or "workflow quality" in intent.lower() or "质量建议" in intent or "自动优化工作流" in intent:
        print(f"[智能工作流质量保障与自动优化引擎] 正在分析工作流质量...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "workflow_quality_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 过滤掉意图关键词
        filter_kw = ["工作流质量", "质量分析", "质量监控", "工作流统计", "workflow quality", "质量建议", "自动优化工作流"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_kw]
        if not filtered_args:
            # 默认显示统计
            filtered_args = ["stats"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能自动化质量保障引擎
    elif "质量保障" in intent or "自动质量" in intent or "引擎测试" in intent or "测试引擎" in intent or "auto quality" in intent.lower() or "quality assurance" in intent.lower() or "质量检测" in intent:
        print(f"[智能自动化质量保障引擎] 正在检测引擎质量...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "auto_quality_assurance_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 过滤掉意图关键词
        filter_kw = ["质量保障", "自动质量", "引擎测试", "测试引擎", "auto quality", "quality assurance", "质量检测"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_kw]
        if not filtered_args:
            # 默认运行检测
            filtered_args = ["--run"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能引擎自动修复引擎
    elif "自动修复" in intent or "引擎修复" in intent or "repair engine" in intent.lower() or "auto repair" in intent.lower() or "修复引擎" in intent:
        print(f"[智能引擎自动修复引擎] 正在自动修复失败的引擎...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "auto_engine_repair_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 过滤掉意图关键词
        filter_kw = ["自动修复", "引擎修复", "repair engine", "auto repair", "修复引擎"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_kw]
        if not filtered_args:
            # 默认运行修复
            filtered_args = ["--run"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能自动化场景测试引擎
    elif "场景测试" in intent or "测试场景" in intent or "scene test" in intent.lower() or "测试计划" in intent or "plan test" in intent.lower() or "场景计划测试" in intent or "测试守护进程" in intent:
        print(f"[智能自动化场景测试引擎] 正在测试场景计划...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "scene_test_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--full"]
        # 过滤掉意图关键词
        filter_kw = ["场景测试", "测试场景", "scene test", "测试计划", "plan test", "场景计划测试", "测试守护进程"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_kw]
        if not filtered_args:
            filtered_args = ["--full"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能场景计划深度验证与优化引擎
    elif "场景计划优化" in intent or "优化场景计划" in intent or "plan optimizer" in intent.lower() or "场景深度验证" in intent or "计划质量" in intent:
        print(f"[智能场景计划深度验证与优化引擎] 正在验证和优化场景计划...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "scenario_plan_optimizer.py")
        cmd_args = ["--verify"]
        if "--summary" in sys.argv or "-s" in sys.argv:
            cmd_args.append("--summary")
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能场景计划自动修复引擎
    elif "场景计划自动修复" in intent or "自动修复场景计划" in intent or "scene plan repair" in intent.lower() or "修复场景计划" in intent or "计划自动修复" in intent:
        print(f"[智能场景计划自动修复引擎] 正在自动修复场景计划...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "scene_plan_auto_repair_engine.py")
        cmd_args = []
        if "--dry-run" in sys.argv or "试运行" in intent or "模拟" in intent:
            cmd_args.append("--dry-run")
        if "--full" in sys.argv or "全部" in intent or "完整" in intent:
            cmd_args.append("--full")
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景质量保障闭环引擎
    elif "全场景质量保障" in intent or "统一质量" in intent or "质量闭环" in intent or "质量服务" in intent or "unified quality" in intent.lower() or "质量循环" in intent or "质量状态" in intent:
        print(f"[智能全场景质量保障闭环引擎] 正在执行质量保障服务...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "unified_quality_loop.py")
        cmd_args = []
        if "--quick" in sys.argv or "快速" in intent or "quick" in intent.lower():
            cmd_args.append("--quick")
        elif "--status" in sys.argv or "状态" in intent:
            cmd_args.append("--status")
        elif "--report" in sys.argv or "报告" in intent:
            cmd_args.append("--report")
        else:
            # 默认运行完整闭环
            cmd_args.append("--cycles")
            # 从参数中提取循环次数
            cycles = 3
            for i, arg in enumerate(sys.argv):
                if arg == "--cycles" and i + 1 < len(sys.argv):
                    try:
                        cycles = int(sys.argv[i + 1])
                    except:
                        pass
            cmd_args.append(str(cycles))
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景自进化诊断与规划引擎
    elif "进化诊断" in intent or "自进化诊断" in intent or "诊断规划" in intent or "evolution diagnosis" in intent.lower() or "进化规划" in intent or "自进化" in intent:
        print(f"[智能全场景自进化诊断与规划引擎] 正在执行诊断与规划...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_diagnosis_planner.py")
        cmd_args = []
        if "--diagnose" in sys.argv or "诊断" in intent:
            cmd_args.append("diagnose")
        elif "--opportunities" in sys.argv or "机会" in intent:
            cmd_args.append("opportunities")
        elif "--plan" in sys.argv or "规划" in intent:
            cmd_args.append("plan")
        elif "--report" in sys.argv or "报告" in intent or "完整" in intent:
            cmd_args.append("report")
        elif "--status" in sys.argv or "状态" in intent:
            cmd_args.append("status")
        else:
            # 默认显示状态
            cmd_args.append("status")
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能统一推荐引擎 - 自动执行
    elif "自动执行推荐" in intent or "自动执行" in intent or "auto execute" in intent.lower() or "auto run" in intent.lower():
        print(f"[智能统一推荐引擎] 正在执行自动推荐...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "unified_recommender.py")
        cmd_args = ["auto"]
        # 如果用户明确确认执行，添加 --confirm 参数
        if "确认" in intent or "yes" in intent.lower() or "是" in intent:
            cmd_args.append("--confirm")
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能推荐反馈学习引擎 - 学习统计
    elif "推荐学习统计" in intent or "反馈学习" in intent or "推荐反馈" in intent and "统计" in intent or "learning stats" in intent.lower() or "推荐权重" in intent:
        print(f"[智能推荐反馈学习引擎] 正在获取学习统计...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "unified_recommender.py")
        cmd_args = ["learn-stats"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能推荐反馈学习引擎 - 学习洞察
    elif "推荐洞察" in intent or "推荐建议" in intent and "学习" in intent or "learning insights" in intent.lower() or "推荐分析" in intent:
        print(f"[智能推荐反馈学习引擎] 正在获取学习洞察...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "unified_recommender.py")
        cmd_args = ["learn-insights"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能统一学习中枢引擎 - 学习状态/统计/洞察
    elif "统一学习" in intent or "学习中枢" in intent or "学习中心" in intent or "unified learning" in intent.lower() or "learning hub" in intent.lower() or "学习整合" in intent or "学习状态" in intent or "学习统计" in intent:
        print(f"[智能统一学习中枢引擎] 正在处理请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "unified_learning_hub.py")
        # 根据意图选择动作
        if "统计" in intent or "stats" in intent.lower():
            cmd_args = ["stats"]
        elif "洞察" in intent or "insights" in intent.lower() or "建议" in intent:
            cmd_args = ["insights"]
        elif "覆盖" in intent or "coverage" in intent.lower() or "能力" in intent:
            cmd_args = ["coverage"]
        else:
            cmd_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能个性化深度学习引擎 - 用户洞察
    elif "个性化洞察" in intent or "深度学习" in intent or "用户洞察" in intent or "personalization insights" in intent.lower() or "深度个性化" in intent or "用户画像" in intent:
        print(f"[智能个性化深度学习引擎] 正在获取用户洞察...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "deep_personalization_engine.py")
        cmd_args = ["insights"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能个性化深度学习引擎 - 个性化推荐
    elif "个性化推荐" in intent or "个性化建议" in intent or "personalized recommend" in intent.lower() or "个人推荐" in intent or "深度推荐" in intent:
        print(f"[智能个性化深度学习引擎] 正在生成个性化推荐...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "deep_personalization_engine.py")
        cmd_args = ["recommend"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能个性化深度学习引擎 - 行为预测
    elif "行为预测" in intent or "预测下一步" in intent or "predict next" in intent.lower() or "预测我的" in intent:
        print(f"[智能个性化深度学习引擎] 正在预测用户行为...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "deep_personalization_engine.py")
        cmd_args = ["predict"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能个性化深度学习引擎 - 时间模式分析
    elif "时间模式" in intent or "使用时段" in intent or "time pattern" in intent.lower() or "使用习惯" in intent:
        print(f"[智能个性化深度学习引擎] 正在分析时间模式...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "deep_personalization_engine.py")
        cmd_args = ["analyze-time"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能自我进化优化器 - 系统状态
    elif "自我进化状态" in intent or "进化优化器状态" in intent or "self evolution status" in intent.lower() or "evolution optimizer status" in intent.lower():
        print(f"[智能自我进化优化器] 正在获取系统状态...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_self_optimizer.py")
        cmd_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能自我进化优化器 - 分析优化机会
    elif "自我进化分析" in intent or "进化优化分析" in intent or "self evolution analyze" in intent.lower() or "evolution optimize analyze" in intent.lower() or "优化机会" in intent or "识别优化" in intent:
        print(f"[智能自我进化优化器] 正在分析优化机会...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_self_optimizer.py")
        cmd_args = ["analyze"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能自我进化优化器 - 生成建议
    elif "自我进化建议" in intent or "进化优化建议" in intent or "self evolution recommend" in intent.lower() or "evolution optimize recommend" in intent.lower() or "进化建议" in intent or "优化建议" in intent:
        print(f"[智能自我进化优化器] 正在生成优化建议...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_self_optimizer.py")
        cmd_args = ["recommend"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能自我进化优化器 - 执行优化
    elif "执行优化" in intent or "自我优化" in intent or "execute optimize" in intent.lower() or "do optimize" in intent.lower() or "执行进化优化" in intent:
        print(f"[智能自我进化优化器] 正在执行优化...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_self_optimizer.py")
        cmd_args = ["optimize"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能引擎性能监控 - 状态查询
    elif "引擎性能" in intent or "性能监控" in intent or "engine performance" in intent.lower() or "engine monitor" in intent.lower() or "调优引擎" in intent or "引擎调优" in intent:
        print(f"[智能引擎性能监控] 正在获取引擎性能状态...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "engine_performance_monitor.py")
        cmd_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能引擎性能监控 - 分析
    elif "分析引擎" in intent or "引擎分析" in intent or "analyze engine" in intent.lower() or "engine analyze" in intent.lower() or "性能分析" in intent:
        print(f"[智能引擎性能监控] 正在分析引擎性能...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "engine_performance_monitor.py")
        cmd_args = ["analyze"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能引擎性能监控 - 建议
    elif "引擎建议" in intent or "性能建议" in intent or "engine recommend" in intent.lower() or "engine suggestions" in intent.lower() or "调优建议" in intent:
        print(f"[智能引擎性能监控] 正在生成调优建议...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "engine_performance_monitor.py")
        cmd_args = ["recommend"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能引擎性能监控 - 最佳引擎
    elif "最佳引擎" in intent or "top engine" in intent.lower() or "引擎排行" in intent or "最快引擎" in intent:
        print(f"[智能引擎性能监控] 正在获取最佳引擎...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "engine_performance_monitor.py")
        cmd_args = ["top", "5", "success_rate"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能进化指挥塔引擎（round 209）
    elif "进化指挥塔" in intent or "command tower" in intent.lower() or "evolution command" in intent.lower() or "指挥塔" in intent or "进化态势" in intent or "evolution situational" in intent.lower() or "进化预测" in intent or "evolution predict" in intent.lower() or "进化规划" in intent or "进化优先级" in intent or "执行进化" in intent or "execute evolution" in intent.lower() or "进化执行" in intent:
        print(f"[智能进化指挥塔引擎] 正在分析进化态势...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_command_tower.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["进化指挥塔", "command tower", "evolution command", "指挥塔", "进化态势", "evolution situational", "进化预测", "evolution predict", "进化规划", "进化优先级", "执行进化", "execute evolution", "进化执行"]]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能进化策略自适应优化引擎（round 211）
    elif "进化策略优化" in intent or "优化进化方向" in intent or "智能进化建议" in intent or "evolution strategy" in intent.lower() or "strategy optimizer" in intent.lower() or "进化策略自适应" in intent or "自适应进化策略" in intent or "策略优化" in intent and "进化" in intent:
        print(f"[智能进化策略自适应优化引擎] 正在分析进化历史并优化策略...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_strategy_optimizer.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["进化策略优化", "优化进化方向", "智能进化建议", "evolution strategy", "strategy optimizer", "进化策略自适应", "自适应进化策略", "策略优化"]]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能进化学习策略自动优化引擎（round 282）
    elif "进化学习策略" in intent or "策略自动优化" in intent or "学习如何进化" in intent or "自动策略应用" in intent or "learning strategy" in intent.lower() or "strategy learning" in intent.lower() or "学会进化" in intent or "进化策略自动" in intent or "自动学习策略" in intent:
        print(f"[智能进化学习策略自动优化引擎] 正在从历史进化中学习最优策略...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_learning_strategy_optimizer.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["进化学习策略", "策略自动优化", "学习如何进化", "自动策略应用", "learning strategy", "strategy learning", "学会进化", "进化策略自动", "自动学习策略"]]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环进化策略智能推荐与自动选择引擎（round 417）
    elif "策略推荐" in intent or "智能推荐进化" in intent or "进化方向推荐" in intent or "strategy recommend" in intent.lower() or "recommend strategy" in intent.lower() or "智能推荐" in intent and "进化" in intent or "进化策略智能" in intent:
        print(f"[智能进化策略推荐引擎] 正在分析系统状态并推荐最优进化策略...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_strategy_intelligent_recommendation_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["策略推荐", "智能推荐进化", "进化方向推荐", "strategy recommend", "recommend strategy", "智能推荐", "进化策略智能"]]
        if not filtered_args:
            filtered_args = ["recommend"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环策略执行效果实时反馈与动态调整深度集成引擎（round 418）
    elif "策略反馈" in intent or "动态调整" in intent or "执行分析" in intent or "strategy feedback" in intent.lower() or "execution analysis" in intent.lower() or "adjust strategy" in intent.lower() or "策略调整" in intent or "执行效果" in intent or "反馈调整" in intent:
        print(f"[策略执行效果实时反馈与动态调整引擎] 正在分析策略执行效果并生成动态调整...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_strategy_feedback_adjustment_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["策略反馈", "动态调整", "执行分析", "strategy feedback", "execution analysis", "adjust strategy", "策略调整", "执行效果", "反馈调整"]]
        if not filtered_args:
            filtered_args = ["loop", "--strategy", "test_strategy"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环策略推荐-执行-反馈-调整完整闭环引擎（round 419）
    elif "策略闭环" in intent or "策略推荐反馈" in intent or "推荐反馈集成" in intent or "strategy loop" in intent.lower() or "recommendation feedback" in intent.lower() or "strategy integration" in intent.lower() or "推荐反馈闭环" in intent or "策略完整闭环" in intent:
        print(f"[策略推荐-执行-反馈-调整完整闭环引擎] 正在启动完整的策略闭环...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_strategy_recommendation_feedback_integration_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["策略闭环", "策略推荐反馈", "推荐反馈集成", "strategy loop", "recommendation feedback", "strategy integration", "推荐反馈闭环", "策略完整闭环"]]
        if not filtered_args:
            filtered_args = ["start"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环执行效果实时反馈与进化驾驶舱深度集成引擎（round 420, 426 增强）
    elif "反馈驾驶舱" in intent or "执行效果显示" in intent or "反馈驾驶舱集成" in intent or "feedback cockpit" in intent.lower() or "execution display" in intent.lower() or "feedback integration" in intent.lower() or "执行反馈驾驶舱" in intent or "效果驾驶舱" in intent or "execution feedback cockpit" in intent.lower() or "实时反馈驾驶舱" in intent or "执行效果反馈" in intent or "趋势反馈集成" in intent or "realtime feedback" in intent.lower():
        print(f"[进化环执行效果实时反馈与进化驾驶舱深度集成引擎 v1.1.0] 正在启动执行效果反馈与驾驶舱集成...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_execution_feedback_cockpit_integration_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["反馈驾驶舱", "执行效果显示", "反馈驾驶舱集成", "feedback cockpit", "execution display", "feedback integration", "执行反馈驾驶舱", "效果驾驶舱", "execution feedback cockpit", "实时反馈驾驶舱", "执行效果反馈", "趋势反馈集成", "realtime feedback"]]
        if not filtered_args:
            filtered_args = ["dashboard"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环策略自适应迭代优化引擎（round 427）
    elif ("策略自适应迭代" in intent or "迭代优化" in intent or "自适应优化" in intent or "adaptive iteration" in intent.lower() or "strategy adaptive" in intent.lower() or "迭代闭环" in intent or "自适应迭代" in intent or "策略迭代" in intent or "迭代自优化" in intent) and "元" not in intent and "meta" not in intent.lower():
        print(f"[策略自适应迭代优化引擎] 正在启动策略自适应迭代优化...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_strategy_adaptive_iteration_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["策略自适应迭代", "迭代优化", "自适应优化", "adaptive iteration", "strategy adaptive", "迭代闭环", "自适应迭代", "策略迭代", "迭代自优化"]]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环策略元自适应迭代优化引擎（round 428）
    elif "策略元自适应迭代" in intent or "元迭代优化" in intent or "meta iteration" in intent.lower() or "元优化" in intent or "策略元优化" in intent or "元自适应" in intent or "meta adaptive" in intent.lower() or "策略递归优化" in intent or "递归迭代优化" in intent or "meta strategy" in intent.lower():
        print(f"[策略元自适应迭代优化引擎] 正在启动策略元自适应迭代优化...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_strategy_meta_adaptive_iteration_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["策略元自适应迭代", "元迭代优化", "meta iteration", "元优化", "策略元优化", "元自适应", "meta adaptive", "策略递归优化", "递归迭代优化", "meta strategy"]]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环跨引擎元进化协同深度增强引擎（round 429）
    elif "跨引擎元进化协同" in intent or "元进化协同" in intent or "cross engine meta" in intent.lower() or "meta collaboration" in intent.lower() or "元协同" in intent or "跨引擎协同" in intent or "cross-engine collaboration" in intent.lower() or "跨引擎元数据" in intent or "meta data sharing" in intent.lower():
        print(f"[跨引擎元进化协同深度增强引擎] 正在启动跨引擎元进化协同...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_cross_engine_meta_collaboration_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["跨引擎元进化协同", "元进化协同", "cross engine meta", "meta collaboration", "元协同", "跨引擎协同", "cross-engine collaboration", "跨引擎元数据", "meta data sharing"]]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环进化知识自涌现发现与创新推理引擎（round 430）
    elif "涌现发现" in intent or "创新推理" in intent or "emergence discovery" in intent.lower() or "innovation reasoning" in intent.lower() or "自涌现" in intent or "知识涌现" in intent or "模式发现" in intent or "pattern discovery" in intent.lower() or "创新假设" in intent or "跨领域迁移" in intent:
        print(f"[进化知识自涌现发现与创新推理引擎] 正在启动进化知识自涌现发现与创新推理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_emergence_discovery_innovation_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["涌现发现", "创新推理", "emergence discovery", "innovation reasoning", "自涌现", "知识涌现", "模式发现", "pattern discovery", "创新假设", "跨领域迁移"]]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环创新假设自动执行与价值实现引擎（round 431）
    elif "假设执行" in intent or "假设转化" in intent or "hypothesis execution" in intent.lower() or "假设自动执行" in intent or "创新假设执行" in intent or ("假设" in intent and "价值" in intent) or "hypothesis_value" in intent.lower() or "创新假设转化" in intent:
        print(f"[创新假设自动执行与价值实现引擎] 正在启动创新假设自动执行与价值实现...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_hypothesis_execution_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["假设执行", "假设转化", "hypothesis execution", "假设自动执行", "创新假设执行", "价值实现", "value realization", "假设价值"]]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环高质量假设自动执行与价值实现引擎（round 458）
    elif "假设价值实现" in intent or "高质量假设执行" in intent or "hypothesis_value_execution" in intent.lower() or "假设自动筛选" in intent or "假设转化任务" in intent or ("假设" in intent and "执行" in intent and "价值" in intent) or "quality_hypothesis" in intent.lower():
        print(f"[高质量假设自动执行与价值实现引擎] 正在启动高质量假设自动执行与价值实现...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_hypothesis_execution_value_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["假设价值实现", "高质量假设执行", "hypothesis_value_execution", "假设自动筛选", "假设转化任务", "quality_hypothesis"]]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环价值-涌现闭环增强引擎（round 432）
    elif "价值涌现闭环" in intent or "价值闭环" in intent or "涌现闭环" in intent or "value emergence loop" in intent.lower() or "闭环增强" in intent or "价值涌现" in intent or "execution_feedback" in intent.lower() or "反馈涌现" in intent or "闭环反馈" in intent:
        print(f"[价值-涌现闭环增强引擎] 正在启动价值-涌现闭环增强...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_value_emergence_closed_loop_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["价值涌现闭环", "价值闭环", "涌现闭环", "value emergence loop", "闭环增强", "价值涌现", "反馈涌现", "闭环反馈"]]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环跨引擎知识蒸馏与自主优化引擎（round 433）
    elif "蒸馏优化" in intent or "模式提取" in intent or "knowledge_distillation" in intent.lower() or "模式发现" in intent or "wisdom_library" in intent.lower() or "蒸馏引擎" in intent or "智能蒸馏" in intent or "success_pattern" in intent.lower():
        print(f"[跨引擎知识蒸馏与自主优化引擎] 正在启动知识蒸馏与自主优化...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_knowledge_distillation_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["蒸馏优化", "模式提取", "knowledge_distillation", "模式发现", "wisdom_library", "蒸馏引擎", "智能蒸馏", "success_pattern"]]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环进化知识动态管理与自优化引擎（round 459）- 自动从最新进化成果中提炼核心知识、智能识别并遗忘过时知识、基于使用频率和价值自动调整知识权重
    elif "知识管理" in intent or "知识优化" in intent or "知识蒸馏" in intent or "智能遗忘" in intent or "动态知识" in intent or "knowledge management" in intent.lower() or "knowledge optimization" in intent.lower() or "dynamic knowledge" in intent.lower() or "知识动态" in intent or "知识权重" in intent or "遗忘引擎" in intent or "知识归档" in intent:
        print(f"[进化知识动态管理与自优化引擎] 正在启动知识动态管理与自优化...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_knowledge_dynamic_management_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["知识管理", "知识优化", "知识蒸馏", "智能遗忘", "动态知识", "knowledge management", "knowledge optimization", "dynamic knowledge", "知识动态", "知识权重", "遗忘引擎", "知识归档"]]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环知识蒸馏与进化驾驶舱可视化集成引擎（round 434）
    elif "蒸馏可视化" in intent or "蒸馏驾驶舱" in intent or "distillation cockpit" in intent.lower() or "蒸馏集成" in intent or "蒸馏进度" in intent or "知识蒸馏可视化" in intent or "distillation visual" in intent.lower() or "蒸馏数据推送" in intent or "蒸馏集成" in intent:
        print(f"[知识蒸馏与驾驶舱集成引擎] 正在启动知识蒸馏与驾驶舱可视化集成...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_distillation_cockpit_integration_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["蒸馏可视化", "蒸馏驾驶舱", "distillation cockpit", "蒸馏集成", "蒸馏进度", "知识蒸馏可视化", "distillation visual", "蒸馏数据推送"]]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环跨引擎深度知识融合与主动推理增强引擎（round 435）
    elif "跨引擎知识融合" in intent or "深度知识融合" in intent or "知识推理增强" in intent or "knowledge fusion" in intent.lower() or "knowledge reasoning" in intent.lower() or "cross engine knowledge" in intent.lower() or "融合推理" in intent or "知识主动推理" in intent or "knowledge deep" in intent.lower() or "深度推理" in intent:
        print(f"[跨引擎深度知识融合与主动推理增强引擎] 正在启动跨引擎知识融合与主动推理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_cross_engine_knowledge_fusion_deep_enhancement_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["跨引擎知识融合", "深度知识融合", "知识推理增强", "knowledge fusion", "knowledge reasoning", "cross engine knowledge", "融合推理", "知识主动推理", "knowledge deep", "深度推理"]]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环从知识融合到假设执行的完整闭环（round 436）- 新增
    elif "知识融合执行" in intent or "知识到执行" in intent or "融合执行闭环" in intent or "knowledge to execution" in intent.lower() or "fusion execution loop" in intent.lower() or "知识闭环执行" in intent:
        print(f"[知识融合到假设执行闭环引擎] 正在启动从知识融合到假设执行的完整闭环...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_cross_engine_knowledge_fusion_deep_enhancement_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["知识融合执行", "知识到执行", "融合执行闭环", "knowledge to execution", "fusion execution loop", "知识闭环执行"]]
        if not filtered_args:
            filtered_args = ["execute_loop"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环进化路径自动执行与闭环优化引擎（round 441）- 将自适应路径规划引擎(r439)、价值量化引擎(r438)、知识驱动触发引擎(r437)深度串联，形成端到端的「规划→执行→评估→反馈→优化」完整闭环
    elif "路径自动执行" in intent or "闭环优化" in intent or "路径执行闭环" in intent or "path execution" in intent.lower() or "closed loop optimization" in intent.lower() or "执行闭环" in intent or "进化闭环优化" in intent or "路径优化闭环" in intent or "path auto" in intent.lower():
        print(f"[进化路径自动执行与闭环优化引擎] 正在启动进化路径自动执行与闭环优化...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_path_execution_closed_loop_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["路径自动执行", "闭环优化", "路径执行闭环", "path execution", "closed loop optimization", "执行闭环", "进化闭环优化", "路径优化闭环", "path auto"]]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环元进化能力增强引擎（round 442）- 让系统能够自动分析自身进化过程、评估进化方法论效率、生成更优的进化策略，形成"学会如何进化"的递归优化能力
    elif "元进化增强" in intent or "元进化能力" in intent or "学会进化" in intent or "meta evolution enhancement" in intent.lower() or "evolution meta" in intent.lower() and "enhance" in intent.lower() or "进化方法论" in intent or "methodology evolution" in intent.lower() or "递归优化进化" in intent or "元进化分析" in intent:
        print(f"[进化环元进化能力增强引擎] 正在启动元进化能力增强分析...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_evolution_enhancement_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["元进化增强", "元进化能力", "学会进化", "meta evolution enhancement", "进化方法论", "methodology evolution", "递归优化进化", "元进化分析"]]
        if not filtered_args:
            filtered_args = ["--analyze"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环跨引擎深度协同自适应优化增强引擎（round 421）
    elif "跨引擎深度协同" in intent or "深度协同优化" in intent or "自适应协同" in intent or "collaboration optimization" in intent.lower() or "deep collaboration" in intent.lower() or "cross engine optimization" in intent.lower() or "协作优化" in intent or "协同自适应" in intent:
        print(f"[跨引擎深度协同自适应优化增强引擎] 正在启动跨引擎深度协同与自适应优化...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_cross_engine_deep_collaboration_optimizer.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["跨引擎深度协同", "深度协同优化", "自适应协同", "collaboration optimization", "deep collaboration", "cross engine optimization", "协作优化", "协同自适应"]]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环知识驱动决策-执行闭环深度增强引擎（round 423）
    elif "知识驱动决策" in intent or "决策执行闭环" in intent or "知识决策" in intent or "knowledge driven decision" in intent.lower() or "decision execution" in intent.lower() or "知识驱动执行" in intent or "决策知识闭环" in intent or "knowledge execution loop" in intent.lower() or "知识闭环" in intent:
        print(f"[知识驱动决策-执行闭环深度增强引擎] 正在启动知识驱动的决策-执行闭环...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_knowledge_driven_decision_execution_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["知识驱动决策", "决策执行闭环", "知识决策", "knowledge driven decision", "decision execution", "知识驱动执行", "决策知识闭环", "knowledge execution loop", "知识闭环"]]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环知识驱动自动触发与自优化深度增强引擎（round 424）
    elif "知识驱动自动触发" in intent or "自优化引擎" in intent or "知识触发" in intent or "knowledge driven trigger" in intent.lower() or "self optimization" in intent.lower() or "trigger optimization" in intent.lower() or "知识自优化" in intent or "自动触发优化" in intent or "trigger self" in intent.lower():
        print(f"[知识驱动自动触发与自优化深度增强引擎] 正在启动知识驱动的自动触发与自优化...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_knowledge_driven_trigger_optimization_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["知识驱动自动触发", "自优化引擎", "knowledge driven trigger", "self optimization", "trigger optimization", "知识自优化", "自动触发优化", "trigger self"]]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环执行效果跨轮对比分析与趋势预测增强引擎（round 425）
    elif "跨轮对比" in intent or "趋势分析" in intent or "进化趋势" in intent or "趋势预测" in intent or "cross round comparison" in intent.lower() or "trend analysis" in intent.lower() or "evolution trend" in intent.lower() or "trend prediction" in intent.lower() or "效果对比" in intent or "执行对比" in intent or "轮次对比" in intent or "优化建议" in intent and "趋势" in intent or "趋势建议" in intent:
        print(f"[进化环执行效果跨轮对比分析与趋势预测增强引擎] 正在启动跨轮对比分析与趋势预测...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_execution_trend_analysis_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["跨轮对比", "趋势分析", "进化趋势", "趋势预测", "cross round comparison", "trend analysis", "evolution trend", "trend prediction", "效果对比", "执行对比", "轮次对比", "优化建议", "趋势建议"]]
        if not filtered_args:
            filtered_args = ["analyze"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环策略知识图谱深度融合与自适应优化引擎（round 422）
    elif "策略知识图谱融合" in intent or "策略知识融合" in intent or "知识驱动策略" in intent or "strategy kg fusion" in intent.lower() or "strategy knowledge" in intent.lower() or "knowledge driven strategy" in intent.lower() or "策略KG融合" in intent or "知识化策略" in intent or "策略自适应优化" in intent:
        print(f"[策略知识图谱深度融合与自适应优化引擎] 正在启动策略知识融合与自适应优化...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_strategy_kg_fusion_optimizer.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["策略知识图谱融合", "策略知识融合", "知识驱动策略", "strategy kg fusion", "strategy knowledge", "knowledge driven strategy", "策略KG融合", "知识化策略", "策略自适应优化"]]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化策略自动生成与动态评估引擎（round 310）
    elif "策略生成" in intent or "策略评估" in intent or "动态策略" in intent or "智能策略选择" in intent or "strategy generation" in intent.lower() or "strategy evaluate" in intent.lower() or "generate strategy" in intent.lower() or "策略智能选择" in intent or "进化策略生成" in intent or "生成进化策略" in intent:
        print(f"[智能进化策略自动生成与动态评估引擎] 正在生成和评估进化策略...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_strategy_generation_evaluator.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["策略生成", "策略评估", "动态策略", "智能策略选择", "strategy generation", "strategy evaluate", "generate strategy", "策略智能选择", "进化策略生成", "生成进化策略"]]
        if not filtered_args:
            filtered_args = ["--generate", "--num", "3"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景元进化统一协同引擎（round 312）
    elif "元进化协同" in intent or "进化智慧" in intent or "协同洞察" in intent or "meta coordination" in intent.lower() or "evolution intelligence" in intent.lower() or "元进化大脑" in intent or "统一协同" in intent or "evolution meta" in intent.lower() or "meta evolve" in intent.lower():
        print(f"[智能全场景元进化统一协同引擎] 正在协调各元进化引擎，生成统一进化洞察...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_coordination_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["元进化协同", "进化智慧", "协同洞察", "meta coordination", "evolution intelligence", "元进化大脑", "统一协同", "evolution meta", "meta evolve"]]
        if not filtered_args:
            filtered_args = ["--coordination"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景统一智能决策与执行中枢引擎（round 313）
    elif "智能决策" in intent or "决策中枢" in intent or "执行大脑" in intent or "unified decision" in intent.lower() or "decision hub" in intent.lower() or "智能执行" in intent or "决策执行" in intent or "全场景决策" in intent or "统一决策" in intent or "intelligent decision" in intent.lower():
        print(f"[智能全场景统一智能决策与执行中枢引擎] 正在执行感知→决策→执行→学习完整闭环...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "unified_intelligent_decision_execution_hub.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["智能决策", "决策中枢", "执行大脑", "unified decision", "decision hub", "智能执行", "决策执行", "全场景决策", "统一决策", "intelligent decision", "状态", "查询"]]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化智慧深度觉醒引擎（round 314）
    elif "智慧觉醒" in intent or "哲学思考" in intent or "进化哲学" in intent or "智慧洞察" in intent or "wisdom" in intent.lower() and "awakening" in intent.lower() or "philosophy" in intent.lower() or "智慧深度" in intent or "深度智慧" in intent or "进化意义" in intent or "意义评估" in intent:
        print(f"[智能全场景进化智慧深度觉醒引擎] 正在思考进化的意义与价值...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_wisdom_deep_awakening_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["智慧觉醒", "哲学思考", "进化哲学", "智慧洞察", "wisdom", "awakening", "philosophy", "智慧深度", "深度智慧", "进化意义", "意义评估", "状态", "查询"]]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环自省与递归优化引擎（round 315）
    elif "进化环自省" in intent or "递归优化" in intent or "自我反思" in intent or "自省" in intent or "loop self reflection" in intent.lower() or "递归" in intent and "优化" in intent or "优化进化环" in intent or "进化环优化" in intent or "自我审视" in intent:
        print(f"[智能全场景进化环自省与递归优化引擎] 正在对进化环进行深度自省和递归优化...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_loop_self_reflection_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["进化环自省", "递归优化", "自我反思", "自省", "loop self reflection", "递归", "优化", "优化进化环", "进化环优化", "自我审视", "状态", "查询", "分析"]]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环元认知深度增强引擎（round 316 + round 353 增强）
    elif "元认知" in intent or "meta cognition" in intent.lower() or "元认知深度" in intent or "认知反思" in intent or "学会思考" in intent or "思考如何思考" in intent or "递归认知" in intent or "meta cognitive" in intent.lower() or "深度反思" in intent or "认知升级" in intent or "认知闭环" in intent or "元认知闭环" in intent or "meta evolution" in intent.lower():
        print(f"[智能全场景进化环元认知深度增强引擎 v1.1.0] 正在对自身认知过程进行递归式深度反思...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_cognition_deep_enhancement_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["元认知", "meta cognition", "元认知深度", "认知反思", "学会思考", "思考如何思考", "递归认知", "meta cognitive", "深度反思", "认知升级", "状态", "查询", "分析", "认知闭环", "元认知闭环", "meta evolution", "集成", "integrate", "优化", "optimize", "闭环", "loop"]]
        if not filtered_args:
            filtered_args = ["status"]
        # Round 353 新增：识别子命令
        if "集成" in intent or "integrate" in intent.lower():
            filtered_args = ["integrate"]
        elif "优化" in intent or "optimize" in intent.lower():
            filtered_args = ["optimize"]
        elif "闭环" in intent or "loop" in intent.lower() or "meta evolution" in intent.lower():
            filtered_args = ["loop"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环目标自优化引擎（round 317）
    elif "目标自优化" in intent or "目标优化" in intent or "进化目标" in intent or "目标评估" in intent or "目标反思" in intent or "goal optimizer" in intent.lower() or "目标体系" in intent or "元目标" in intent or "优化目标" in intent:
        print(f"[智能全场景进化环目标自优化引擎] 正在评估和优化进化目标体系...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_goal_optimizer_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["目标自优化", "目标优化", "进化目标", "目标评估", "目标反思", "goal optimizer", "目标体系", "元目标", "优化目标", "状态", "查询", "分析"]]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环价值创造与意义实现引擎（round 318）
    elif "价值创造" in intent or "意义实现" in intent or "价值评估" in intent or "进化价值" in intent or "value creation" in intent.lower() or "value assessment" in intent.lower() or "价值驱动" in intent or "意义" in intent and "进化" in intent or "价值链" in intent:
        print(f"[智能全场景进化环价值创造与意义实现引擎] 正在评估进化的真实价值贡献，连接进化与用户实际价值...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_value_creation_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["价值创造", "意义实现", "价值评估", "进化价值", "value creation", "value assessment", "价值驱动", "意义", "价值链", "状态", "查询", "分析"]]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化价值实现追踪与闭环优化引擎（round 323）
    # 排除"价值实现预测"以避免与 Round 516 引擎冲突
    elif ("价值追踪" in intent or "价值实现" in intent or "价值闭环" in intent or "value tracking" in intent.lower() or "价值趋势" in intent or "价值驱动" in intent and "优化" in intent or "追踪价值" in intent or "价值量化" in intent) and "价值实现预测" not in intent:
        print(f"[智能全场景进化价值实现追踪与闭环优化引擎] 正在追踪进化的价值实现过程，进行价值量化和闭环优化...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_value_tracking_loop_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["价值追踪", "价值实现", "价值闭环", "value tracking", "价值趋势", "价值驱动", "追踪价值", "价值量化", "状态", "查询", "分析", "仪表盘", "dashboard"]]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环自我进化增强引擎（round 324）
    elif "自我进化" in intent or "进化增强" in intent or "自我优化" in intent or "self evolution" in intent.lower() or "evolution enhance" in intent.lower() or "学会进化" in intent or "进化如何进化" in intent or "递归进化" in intent or "自我改进" in intent or "进化环改进" in intent or "自我进化分析" in intent or "进化环分析" in intent or "优化进化环" in intent:
        print(f"[智能全场景进化环自我进化增强引擎] 正在分析进化环自身表现，发现优化空间，生成并执行自我改进方案...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_self_evolution_enhancement_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["自我进化", "进化增强", "自我优化", "self evolution", "evolution enhance", "学会进化", "进化如何进化", "递归进化", "自我改进", "进化环改进", "自我进化分析", "进化环分析", "优化进化环", "状态", "查询", "分析", "仪表盘", "dashboard", "执行", "execute", "循环", "cycle"]]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环自我进化能力深度增强引擎 V2（round 549）- 集成健康监测和效能分析数据，实现更智能的自我进化评估
    elif "自我进化能力" in intent or "进化能力深度" in intent or "能力增强" in intent or "自我进化评估" in intent or "进化状态评估" in intent or "self evolution capability" in intent.lower() or "deep enhancement" in intent.lower() or "进化指数" in intent or "能力指数" in intent:
        print(f"[智能全场景进化环自我进化能力深度增强引擎 V2] 正在评估进化能力，整合健康监测和效能分析数据...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_self_evolution_enhancement_v2.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["自我进化能力", "进化能力深度", "能力增强", "自我进化评估", "进化状态评估", "self evolution capability", "deep enhancement", "进化指数", "能力指数", "状态", "查询", "分析", "仪表盘", "dashboard", "执行", "execute", "循环", "cycle"]]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环自我进化效能趋势预测与预防性策略动态调整引擎（round 550）- 基于历史效能数据预测未来趋势，提前识别风险并生成预防性策略
    elif "进化趋势预测" in intent or "效能趋势预测" in intent or "预防性策略调整" in intent or "趋势预防性" in intent or "进化风险预测" in intent or "自我进化趋势" in intent or "evolution trend prediction" in intent.lower() or "trend prevention" in intent.lower() or "risk prediction" in intent.lower() or "策略动态调整" in intent or "动态策略" in intent:
        print(f"[智能全场景进化环自我进化效能趋势预测与预防性策略动态调整引擎] 正在分析进化效能趋势并生成预防性策略...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_self_evolution_trend_prediction_prevention_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["进化趋势预测", "效能趋势预测", "预防性策略调整", "趋势预防性", "进化风险预测", "自我进化趋势", "evolution trend prediction", "trend prevention", "risk prediction", "策略动态调整", "动态策略", "状态", "status", "仪表盘", "dashboard", "执行", "execute", "循环", "cycle", "预测", "predict", "风险", "risk", "策略", "strategy"]]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环跨轮次深度学习与自适应策略迭代优化引擎（round 551）- 从500+轮进化历史中深度学习，自动识别高效进化模式，智能优化策略参数
    elif "跨轮次深度学习" in intent or "跨轮学习" in intent or "策略迭代优化" in intent or "自适应策略优化" in intent or "cross round learning" in intent.lower() or "deep learning iteration" in intent.lower() or "策略参数优化" in intent or "学习迭代" in intent or "adaptive strategy" in intent.lower() or "迭代优化" in intent or "模式识别" in intent and "进化" in intent:
        print(f"[智能全场景进化环跨轮次深度学习与自适应策略迭代优化引擎] 正在分析进化历史并优化策略参数...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_cross_round_deep_learning_iteration_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["跨轮次深度学习", "跨轮学习", "策略迭代优化", "自适应策略优化", "cross round learning", "deep learning iteration", "策略参数优化", "学习迭代", "adaptive strategy", "迭代优化", "模式识别", "状态", "status", "仪表盘", "dashboard", "执行", "execute", "循环", "cycle", "分析", "analyze", "优化", "optimize"]]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环元进化方法论自动优化引擎（round 552）- 分析自身进化方法论的有效性，自动发现进化策略的优化空间，形成「学会如何进化得更好」的递归优化能力
    elif "元进化方法论" in intent or "方法论优化" in intent or "元进化优化" in intent or "进化方法论分析" in intent or "meta methodology" in intent.lower() or "meta optimization" in intent.lower() or "methodology auto" in intent.lower() or "进化策略分析" in intent or "策略分析引擎" in intent:
        print(f"[智能全场景进化环元进化方法论自动优化引擎] 正在分析进化方法论并生成优化建议...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_methodology_auto_optimizer.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["元进化方法论", "方法论优化", "元进化优化", "进化方法论分析", "meta methodology", "meta optimization", "methodology auto", "进化策略分析", "策略分析引擎", "状态", "status", "仪表盘", "dashboard", "执行", "execute", "循环", "cycle", "分析", "analyze", "优化", "optimize", "建议", "recommend", "机会", "opportunity"]]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环元进化策略执行验证与闭环优化引擎（round 553）- 自动执行元进化方法论优化引擎生成的优化建议，验证执行效果，形成「分析→优化→执行→验证」的完整元进化闭环
    elif "元进化执行" in intent or "策略执行验证" in intent or "元进化闭环" in intent or "meta execution" in intent.lower() or "strategy verify" in intent.lower() or "执行验证" in intent or "闭环验证" in intent or "优化执行" in intent:
        print(f"[智能全场景进化环元进化策略执行验证与闭环优化引擎] 正在执行优化建议并验证效果...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_strategy_execution_verification_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["元进化执行", "策略执行验证", "元进化闭环", "meta execution", "strategy verify", "执行验证", "闭环验证", "优化执行", "状态", "status", "仪表盘", "dashboard", "执行", "execute", "循环", "cycle", "分析", "analyze", "验证", "verify"]]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环元健康诊断与自愈增强引擎（round 554）- 让系统能够持续监控元进化环本身的健康状态，实时检测进化过程中的异常模式，自动诊断问题根因并生成自愈方案，形成元进化层面的免疫系统
    elif "元进化健康" in intent or "meta immune" in intent.lower() or "元免疫" in intent or "meta_health" in intent.lower():
        print(f"[智能全场景进化环元健康诊断与自愈增强引擎] 正在监控元进化环健康状态并执行自愈...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_health_diagnosis_self_healing_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["元健康诊断", "元自愈", "进化环健康", "meta health", "meta healing", "evolution health", "元免疫", "meta immune", "自愈增强", "健康自愈", "状态", "status", "仪表盘", "dashboard", "检测", "detect", "诊断", "diagnose", "自愈", "heal", "循环", "cycle", "完整", "full"]]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环元进化策略自动生成与自主决策增强引擎（round 555）- 让系统能够基于当前的元进化状态自动生成新的进化策略，并自主决定下一轮的进化方向，形成完整的元进化闭环
    elif "策略自动生成" in intent or "元策略自动" in intent or "autonomous strategy" in intent.lower() or "strategy autonomous" in intent.lower() or "策略生成与决策" in intent or "元进化策略生成" in intent:
        print(f"[智能全场景进化环元进化策略自动生成与自主决策增强引擎] 正在分析元进化状态并生成决策...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_strategy_autonomous_generation_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["策略自动生成", "元策略自动", "autonomous strategy", "strategy autonomous", "策略生成与决策", "元进化策略生成", "状态", "status", "仪表盘", "dashboard", "分析", "analyze", "生成", "generate", "决策", "decide", "循环", "cycle"]]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环自我进化与决策深度集成引擎（round 325）
    elif "进化决策集成" in intent or "自我决策集成" in intent or "分析决策执行" in intent or "integrated evolution" in intent.lower() or "进化闭环" in intent or "进化自优化" in intent or "自动化进化优化" in intent:
        print(f"[智能全场景进化环自我进化与决策深度集成引擎] 正在深度集成自我进化引擎与决策引擎，形成分析→决策→执行→验证→优化完整闭环...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_self_decision_integration.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["进化决策集成", "自我决策集成", "分析决策执行", "integrated evolution", "进化闭环", "进化自优化", "自动化进化优化", "状态", "status", "仪表盘", "dashboard", "执行", "execute", "循环", "cycle"]]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能跨引擎知识融合与持续学习引擎（round 212）
    elif "跨引擎学习" in intent or "跨引擎知识" in intent or "引擎持续学习" in intent or "cross engine learning" in intent.lower() or "知识融合" in intent or "模式发现" in intent or "创新组合" in intent:
        print(f"[智能跨引擎知识融合与持续学习引擎] 正在分析跨引擎交互数据并生成创新建议...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "cross_engine_learning_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["跨引擎学习", "跨引擎知识", "引擎持续学习", "cross engine learning", "知识融合", "模式发现", "创新组合"]]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能决策质量预测性优化与预防性增强引擎（round 337）
    elif ("质量预测" in intent or "predictive quality" in intent.lower() or
          "预测性优化" in intent or "preventive optimizer" in intent.lower() or
          "预测优化引擎" in intent or "predict optimizer" in intent.lower() or
          "预防性增强" in intent or "decision quality prediction" in intent.lower()):
        print(f"[智能决策质量预测性优化与预防性增强引擎 v1.0] 正在处理预测性优化...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_decision_predictive_optimizer.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "摘要" in intent or "summary" in intent.lower() or "预测摘要" in intent:
            action = "--summary"
        elif "测试" in intent or "test" in intent.lower() or "执行" in intent or "运行" in intent:
            action = "--test"
        elif "配置" in intent or "config" in intent.lower():
            action = "--config"
        # 过滤掉意图关键词
        filter_words = ["质量预测", "predictive quality", "预测性优化", "preventive optimizer",
                       "预测优化引擎", "predict optimizer", "预防性增强", "decision quality prediction",
                       "摘要", "summary", "预测摘要", "测试", "test", "执行", "运行", "配置", "config",
                       "状态", "status"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加动作前缀
        if action not in filtered_args and not any(arg.startswith("--") for arg in filtered_args):
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能决策质量跨轮持续学习与自适应进化引擎（round 338）
    elif ("决策持续学习" in intent or "decision continuous learning" in intent.lower() or
          "决策进化优化" in intent or "decision evolution optimization" in intent.lower() or
          "决策自适应进化" in intent or "decision adaptive evolution" in intent.lower() or
          "质量学习闭环" in intent or "quality learning loop" in intent.lower() or
          "质量预测学习" in intent or "quality prediction learning" in intent.lower() or
          "持续学习引擎" in intent or "continuous learning engine" in intent.lower() or
          "自适应进化引擎" in intent or "adaptive evolution engine" in intent.lower() or
          "学习闭环引擎" in intent or "learning loop engine" in intent.lower() or
          "跨轮学习" in intent):
        print(f"[智能决策质量跨轮持续学习与自适应进化引擎 v1.0] 正在执行持续学习与自适应优化...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_decision_continuous_learning.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "摘要" in intent or "summary" in intent.lower() or "学习摘要" in intent:
            action = "--summary"
        elif "测试" in intent or "test" in intent.lower() or "执行" in intent or "运行" in intent:
            action = "--test"
        elif "记录" in intent or "record" in intent.lower():
            action = "--record"
        elif "分析" in intent or "analyze" in intent.lower():
            action = "--analyze"
        elif "洞察" in intent or "insights" in intent.lower():
            action = "--insights"
        elif "配置" in intent or "config" in intent.lower():
            action = "--config"
        # 过滤掉意图关键词
        filter_words = ["持续学习", "continuous learning", "进化优化", "evolution optimization",
                       "自适应进化", "adaptive evolution", "学习闭环", "learning loop",
                       "预测学习", "prediction learning",
                       "摘要", "summary", "学习摘要", "测试", "test", "执行", "运行", "配置", "config",
                       "记录", "record", "分析", "analyze", "洞察", "insights",
                       "状态", "status"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加动作前缀
        if action not in filtered_args and not any(arg.startswith("--") for arg in filtered_args):
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能主动价值发现与自主意识执行深度集成引擎（round 340）
    elif ("价值执行融合" in intent or "value execution fusion" in intent.lower() or
          "主动执行闭环" in intent or "价值自主执行" in intent or
          "融合引擎" in intent and "执行" in intent or
          "自主价值发现" in intent):
        print(f"[智能主动价值发现与自主意识执行深度集成引擎 v1.0] 正在执行价值-执行融合...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_value_execution_fusion_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        action = "status"
        if "完整闭环" in intent or "full cycle" in intent.lower() or "执行闭环" in intent:
            action = "--full-cycle"
        elif "历史" in intent or "history" in intent.lower():
            action = "--history"
        filter_words = ["价值执行融合", "value execution fusion", "主动执行闭环", "价值自主执行",
                       "融合引擎", "执行", "完整闭环", "full cycle", "历史", "history", "状态", "status"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        if action not in filtered_args and not any(arg.startswith("--") for arg in filtered_args):
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景跨维度智能融合与递归进化引擎（round 341）
    elif ("跨维度融合" in intent or "cross dimension" in intent.lower() or
          "递归进化" in intent or "recursive evolution" in intent.lower() or
          "智能融合" in intent or "维度融合" in intent or
          "融合引擎" in intent and "多维度" in intent or
          "超级智能体" in intent):
        print(f"[智能全场景跨维度智能融合与递归进化引擎 v1.0] 正在执行跨维度智能融合...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_cross_dimension_fusion_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        action = "status"
        if "完整闭环" in intent or "full cycle" in intent.lower() or "执行闭环" in intent:
            action = "--full-cycle"
        elif "自动" in intent or "auto" in intent.lower():
            action = "--auto"
            # 检查是否指定了循环次数
            for arg in cmd_args:
                if arg.isdigit():
                    action = f"--auto --cycles {arg}"
                    break
        elif "历史" in intent or "history" in intent.lower():
            action = "--history"
        filter_words = ["跨维度融合", "cross dimension", "recursive evolution", "递归进化",
                       "智能融合", "维度融合", "融合引擎", "多维度", "超级智能体",
                       "完整闭环", "full cycle", "自动", "auto", "历史", "history", "状态", "status"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        if action not in filtered_args and not any(arg.startswith("--") for arg in filtered_args):
            if isinstance(action, str) and action.startswith("--auto"):
                parts = action.split()
                filtered_args = parts + filtered_args
            else:
                filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化体自我克隆与分布式协作引擎（round 342）
    elif ("自我克隆" in intent or "clone" in intent.lower() or
          "分布式协作" in intent or "distributed collaboration" in intent.lower() or
          "群体智慧" in intent or "swarm intelligence" in intent.lower() or
          "协作引擎" in intent or "collaboration engine" in intent.lower() or
          "多实例" in intent or "multi-instance" in intent.lower() or
          "克隆协作" in intent):
        print(f"[智能全场景进化体自我克隆与分布式协作引擎 v1.0] 正在执行克隆与协作...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_self_clone_collaboration_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        action = ""  # 不添加 action 前缀，让模块自行处理
        if "完整闭环" in intent or "full cycle" in intent.lower() or "执行闭环" in intent:
            action = "--full-cycle"
        elif "克隆" in intent and "任务" in intent:
            action = "--clone"
        elif "实例" in intent and "状态" in intent:
            action = "--instances"
        elif "协作" in intent and "任务" in intent:
            action = "--collaborate"
        elif "知识" in intent and "共享" in intent:
            action = "--knowledge"
        elif "聚合" in intent or "aggregate" in intent.lower():
            action = "--aggregation"
        filter_words = ["进化体自我克隆与分布式协作", "自我克隆", "clone", "分布式协作", "distributed collaboration",
                       "群体智慧", "swarm intelligence", "协作引擎", "collaboration engine",
                       "多实例", "multi-instance", "克隆协作", "完整闭环", "full cycle",
                       "克隆", "任务", "协作", "知识", "共享", "聚合", "状态", "status", "--status"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        if action and action not in filtered_args and not any(arg.startswith("--") for arg in filtered_args):
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化体动态负载均衡与弹性伸缩引擎（round 343）
    elif ("负载均衡" in intent or "load balancer" in intent.lower() or
          "弹性伸缩" in intent or "elastic scaling" in intent.lower() or
          "动态调度" in intent or "dynamic scheduling" in intent.lower() or
          "自动扩容" in intent or "auto scale" in intent.lower() or
          "缩容" in intent or "scale in" in intent.lower() or
          "扩容" in intent or "scale out" in intent.lower() or
          "资源调度" in intent or "resource scheduling" in intent.lower()):
        print(f"[智能全场景进化体动态负载均衡与弹性伸缩引擎 v1.0] 正在执行负载均衡与伸缩调度...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_dynamic_load_balancer.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        action = ""  # 不添加 action 前缀，让模块自行处理
        if "完整闭环" in intent or "full cycle" in intent.lower() or "执行闭环" in intent:
            action = "--full-cycle"
        elif "状态" in intent or "status" in intent.lower():
            action = "--status"
        elif "分发" in intent or "dispatch" in intent.lower():
            action = "--dispatch"
        elif "指标" in intent or "metrics" in intent.lower():
            action = "--metrics"
        elif "配置" in intent or "config" in intent.lower():
            action = "--config"
        filter_words = ["负载均衡", "load balancer", "弹性伸缩", "elastic scaling",
                       "动态调度", "dynamic scheduling", "自动扩容", "auto scale",
                       "缩容", "scale in", "扩容", "scale out", "资源调度", "resource scheduling",
                       "完整闭环", "full cycle", "状态", "status", "分发", "dispatch",
                       "指标", "metrics", "配置", "config"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        if action and action not in filtered_args and not any(arg.startswith("--") for arg in filtered_args):
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化体创新实现深化引擎（round 344）
    elif ("创新实现" in intent or "创新深化" in intent or "闭环创新" in intent or
          "innovation implementation" in intent.lower() or "innovation engine" in intent.lower() or
          "创新机会" in intent or "发现创新" in intent or "创新方案" in intent):
        print(f"[智能全场景进化体创新实现深化引擎 v1.0] 正在执行创新实现与闭环...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_innovation_implementation_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        action = ""  # 不添加 action 前缀，让模块自行处理
        if "完整闭环" in intent or "full cycle" in intent.lower() or "执行闭环" in intent:
            action = "--full-cycle"
        elif "状态" in intent or "status" in intent.lower():
            action = "status"
        elif "发现" in intent or "discover" in intent.lower():
            action = "discover"
        elif "评估" in intent or "evaluate" in intent.lower():
            action = "evaluate"
        elif "方案" in intent or "plan" in intent.lower():
            action = "plan"
        filter_words = ["创新实现", "创新深化", "闭环创新", "innovation implementation",
                       "innovation engine", "创新机会", "发现创新", "创新方案",
                       "完整闭环", "full cycle", "状态", "status", "发现", "discover",
                       "评估", "evaluate", "方案", "plan"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        if action and action not in filtered_args and not any(arg.startswith("--") for arg in filtered_args):
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能主动价值发现与智能决策闭环增强引擎（round 339）
    elif ("主动价值发现" in intent or "价值发现" in intent or "主动决策" in intent or
          "active value discovery" in intent.lower() or "value discovery engine" in intent.lower() or
          "智能决策闭环" in intent or "决策闭环" in intent or "价值驱动" in intent or
          "主动发现" in intent or "发现机会" in intent):
        print(f"[智能主动价值发现与智能决策闭环增强引擎 v1.0] 正在执行主动价值发现与智能决策...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_active_value_discovery_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "发现" in intent or "discover" in intent.lower():
            action = "--discover"
        elif "完整闭环" in intent or "full cycle" in intent.lower() or "执行闭环" in intent:
            action = "--full-cycle"
        elif "配置" in intent or "config" in intent.lower():
            action = "--config"
        # 过滤掉意图关键词
        filter_words = ["主动价值发现", "价值发现", "主动决策", "active value discovery", "value discovery engine",
                       "智能决策闭环", "决策闭环", "价值驱动", "主动发现", "发现机会",
                       "发现", "discover", "完整闭环", "full cycle", "执行闭环",
                       "配置", "config", "状态", "status"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加动作前缀
        if action not in filtered_args and not any(arg.startswith("--") for arg in filtered_args):
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能主动洞察与建议引擎（round 213）
    elif "主动洞察" in intent or "主动建议" in intent or "洞察" in intent or "主动价值" in intent or "proactive insight" in intent.lower() or "insight advisor" in intent.lower() or "洞察引擎" in intent or "建议引擎" in intent or "趋势分析" in intent or "进化趋势" in intent or "预测" in intent:
        print(f"[智能主动洞察与建议引擎] 正在分析跨引擎知识、进化趋势和系统状态，生成主动洞察与建议...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "proactive_insight_advisor.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["主动洞察", "主动建议", "洞察", "主动价值", "proactive insight", "insight advisor", "洞察引擎", "建议引擎", "趋势分析", "进化趋势", "预测"]]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能进化预测与主动规划引擎（round 217）- 放在其他"主动规划"之前
    elif "进化预测" in intent or "预测进化" in intent or "evolution prediction" in intent.lower() or "进化规划" in intent or "下一轮进化" in intent or ("进化" in intent and "规划" in intent):
        print(f"[智能进化预测与主动规划引擎] 正在分析进化历史、检测模式、预测下一轮进化方向并生成主动规划...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_prediction_planner.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["进化预测", "预测进化", "evolution prediction", "进化规划", "下一轮进化"]]
        if not filtered_args:
            filtered_args = ["plan"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能引擎组合实时监控与自适应优化引擎（round 208）
    elif "引擎实时监控" in intent or "引擎组合优化" in intent or "实时优化" in intent or "engine realtime" in intent.lower() or "engine monitor" in intent.lower() or "组合分析" in intent or "engine combo" in intent.lower() or "引擎自适应" in intent:
        print(f"[智能引擎组合实时监控与自适应优化引擎] 正在分析引擎组合并生成优化建议...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "engine_realtime_optimizer.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["引擎实时监控", "引擎组合优化", "实时优化", "engine realtime", "engine monitor", "组合分析", "engine combo", "引擎自适应"]]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能引擎效能自动优化引擎（round 247）- 将优化建议自动执行
    elif "引擎效能优化" in intent or "引擎自动优化" in intent or "engine auto" in intent.lower() or "自动优化" in intent or "效能优化" in intent or "引擎优化" in intent or "engine optimization" in intent.lower():
        print(f"[智能引擎效能自动优化引擎] 正在执行引擎效能自动优化...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "engine_auto_optimizer.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["引擎效能优化", "引擎自动优化", "engine auto", "自动优化", "效能优化", "引擎优化", "engine optimization"]]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景执行自适应优化引擎（round 265）- 实时分析执行效果、自动调整执行参数、优化执行路径
    elif "执行自适应优化" in intent or "自适应执行" in intent or "execution adaptive" in intent.lower() or "执行优化" in intent or "adaptive execution" in intent.lower() or "自适应执行优化" in intent or "执行参数优化" in intent or "执行路径优化" in intent:
        print(f"[智能全场景执行自适应优化引擎] 正在执行自适应优化分析...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "adaptive_execution_optimizer.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["执行自适应优化", "自适应执行", "execution adaptive", "执行优化", "adaptive execution", "自适应执行优化", "执行参数优化", "执行路径优化"]]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能引擎负载均衡与协同调度引擎（round 248）- 多引擎并发时智能分配资源
    elif "负载均衡" in intent or "引擎负载" in intent or "load balance" in intent.lower() or "资源分配" in intent or "引擎调度" in intent or "engine load" in intent.lower():
        print(f"[智能引擎负载均衡与协同调度引擎] 正在执行引擎负载均衡...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "engine_load_balancer.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        filtered_args = [arg for arg in cmd_args if arg not in ["负载均衡", "引擎负载", "load balance", "资源分配", "引擎调度", "engine load"]]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能引擎能力组合自动发现与优化引擎（round 174）
    elif "引擎能力发现" in intent or "能力组合" in intent or "创新组合" in intent or "engine capability" in intent.lower() or "组合发现" in intent or "工作流建议" in intent:
        print(f"[智能引擎能力组合自动发现与优化引擎] 正在分析引擎能力组合...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "engine_capability_discovery.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["run"]
        filtered_args = [arg for arg in cmd_args if arg not in ["引擎能力发现", "能力组合", "创新组合", "engine capability", "组合发现", "工作流建议"]]
        if not filtered_args:
            filtered_args = ["run"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全系统引擎协同调度引擎（round 232）
    elif "引擎协同调度" in intent or "引擎调度" in intent or "智能调度" in intent or "engine collaboration" in intent.lower() or "engine schedule" in intent.lower() or "引擎选择" in intent or "自适应调度" in intent:
        print(f"[智能全系统引擎协同调度引擎] 正在分析任务需求并选择最优引擎组合...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "engine_collaboration_optimizer.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["run"]
        filtered_args = [arg for arg in cmd_args if arg not in ["引擎协同调度", "引擎调度", "智能调度", "engine collaboration", "engine schedule", "引擎选择", "自适应调度"]]
        if not filtered_args:
            filtered_args = ["run"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景决策质量驱动自适应优化执行引擎 (Round 336) - 需要放在 round 233 前面以避免被"优化执行"拦截
    elif ("决策质量驱动" in intent or "质量驱动优化" in intent or "质量优化执行" in intent or
          "quality driven" in intent.lower() or "quality optimizer" in intent.lower() or
          "决策优化闭环" in intent or "质量闭环" in intent or
          "驱动自适应" in intent or "quality execution" in intent.lower() or
          "质量驱动" in intent or "决策质量执行" in intent):
        print(f"[智能决策质量驱动自适应优化执行引擎 v1.0] 正在处理决策质量驱动的优化...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_decision_quality_driven_optimizer.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "摘要" in intent or "summary" in intent.lower() or "优化摘要" in intent:
            action = "--summary"
        elif "测试" in intent or "test" in intent.lower() or "执行" in intent or "运行" in intent:
            action = "--test"
        elif "配置" in intent or "config" in intent.lower():
            action = "--config"
        # 过滤掉意图关键词
        filter_words = ["决策质量驱动", "质量驱动优化", "质量优化执行", "quality driven", "quality optimizer",
                       "决策优化闭环", "质量闭环", "驱动自适应", "quality execution",
                       "质量驱动", "决策质量执行",
                       "摘要", "summary", "优化摘要", "测试", "test", "执行", "运行", "配置", "config",
                       "状态", "status"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加动作前缀
        if action not in filtered_args and not any(arg.startswith("--") for arg in filtered_args):
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环进化效能预测与预防性优化引擎 (Round 476) - 放在其他预测引擎之前
    elif "进化效能预测" in intent or "进化趋势预测" in intent or "进化未来效能" in intent or "evolution effectiveness prediction" in intent.lower() or "effectiveness prediction" in intent.lower() or "进化预防" in intent or "效能预防" in intent:
        print(f"[智能全场景进化环进化效能预测与预防性优化引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_effectiveness_prediction_prevention_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["进化效能预测", "进化趋势预测", "进化未来效能", "evolution effectiveness prediction", "effectiveness prediction", "进化预防", "效能预防"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环跨引擎协同效能预测增强引擎 (Round 477)
    elif "跨引擎协同效能预测" in intent or "跨引擎预测" in intent or "协同效能预测" in intent or "cross engine collaboration prediction" in intent.lower() or "collaboration prediction" in intent.lower() or "跨引擎协同" in intent:
        print(f"[智能全场景进化环跨引擎协同效能预测增强引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_cross_engine_collaboration_prediction_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["跨引擎协同效能预测", "跨引擎预测", "协同效能预测", "cross engine collaboration prediction", "collaboration prediction", "跨引擎协同"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环动态阈值自适应优化引擎 (Round 478)
    elif "动态阈值自适应优化" in intent or "阈值自适应优化" in intent or "自适应阈值优化" in intent or "adaptive threshold optimization" in intent.lower() or "threshold adaptive optimization" in intent.lower() or "动态阈值优化" in intent or "阈值自优化" in intent or "智能阈值自适应" in intent:
        print(f"[智能全场景进化环动态阈值自适应优化引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_dynamic_threshold_adaptive_optimization_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["status"]
        # 过滤掉意图关键词
        filter_words = ["动态阈值自适应优化", "阈值自适应优化", "自适应阈值优化", "adaptive threshold optimization", "threshold adaptive optimization", "动态阈值优化", "阈值自优化", "智能阈值自适应"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环进化路径智能规划与自适应演进引擎 (Round 479)
    elif "进化路径智能规划" in intent or "路径智能规划" in intent or "自适应演进引擎" in intent or "智能演进引擎" in intent or "进化演进" in intent or "演进规划" in intent or "smart path planning" in intent.lower() or "adaptive evolution" in intent.lower():
        print(f"[智能全场景进化环进化路径智能规划与自适应演进引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_evolution_path_smart_planning_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["进化路径智能规划", "路径智能规划", "自适应演进引擎", "智能演进引擎", "进化演进", "演进规划", "smart path planning", "adaptive evolution"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环进化驾驶舱可视化增强与智能交互引擎 (Round 480)
    elif "驾驶舱可视化增强" in intent or "可视化增强" in intent or "驾驶舱增强" in intent or "cockpit visualization" in intent.lower() or "visualization enhanced" in intent.lower() or "智能交互" in intent or "interaction" in intent.lower() or "进化路径可视化" in intent or "path visualization" in intent.lower():
        print(f"[智能全场景进化环进化驾驶舱可视化增强与智能交互引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_cockpit_visualization_enhanced_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["驾驶舱可视化增强", "可视化增强", "驾驶舱增强", "cockpit visualization", "visualization enhanced", "智能交互", "interaction", "进化路径可视化", "path visualization"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能决策质量预测性优化与预防性增强引擎（round 337）
    elif ("预测性" in intent or "predictive" in intent.lower() or
          "预防性" in intent or "preventive" in intent.lower() or
          "预测优化" in intent or "predictive optimization" in intent.lower() or
          "预防性增强" in intent or "事前预测" in intent or
          "决策预测" in intent or "quality prediction" in intent.lower() or
          "predict optimizer" in intent.lower()):
        print(f"[智能决策质量预测性优化与预防性增强引擎 v1.0] 正在处理预测性优化...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_decision_predictive_optimizer.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "摘要" in intent or "summary" in intent.lower() or "预测摘要" in intent:
            action = "--summary"
        elif "测试" in intent or "test" in intent.lower() or "执行" in intent or "运行" in intent:
            action = "--test"
        elif "配置" in intent or "config" in intent.lower():
            action = "--config"
        # 过滤掉意图关键词
        filter_words = ["预测性", "predictive", "预防性", "preventive", "预测优化", "predictive optimization",
                       "预防性增强", "事前预测", "决策预测", "quality prediction", "predict optimizer",
                       "摘要", "summary", "预测摘要", "测试", "test", "执行", "运行", "配置", "config",
                       "状态", "status"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加动作前缀
        if action not in filtered_args and not any(arg.startswith("--") for arg in filtered_args):
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能主动优化发现引擎（round 233）
    elif "主动优化发现" in intent or "优化发现" in intent or "主动优化" in intent or "optimization discovery" in intent.lower() or "主动优化引擎" in intent or "发现优化" in intent or "优化机会" in intent:
        print(f"[智能主动优化发现引擎] 正在分析系统状态并发现优化机会...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "proactive_optimization_discovery_engine.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["discover"]
        filtered_args = [arg for arg in cmd_args if arg not in ["主动优化发现", "优化发现", "主动优化", "optimization discovery", "主动优化引擎", "发现优化", "优化机会"]]
        if not filtered_args:
            filtered_args = ["discover"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能工作流自动实现引擎（round 175）
    elif "工作流自动实现" in intent or "自动实现工作流" in intent or "实现工作流建议" in intent or "workflow auto implement" in intent.lower() or "auto implement workflow" in intent.lower():
        print(f"[智能工作流自动实现引擎] 正在将工作流建议转化为可执行计划...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "workflow_auto_implementer.py")
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["run"]
        filtered_args = [arg for arg in cmd_args if arg not in ["工作流自动实现", "自动实现工作流", "实现工作流建议", "workflow auto implement", "auto implement workflow"]]
        if not filtered_args:
            filtered_args = ["run"]
        # 检查是否有 -e 或 --execute 参数
        auto_execute = "-e" in cmd_args or "--execute" in cmd_args
        if auto_execute:
            filtered_args.append("--execute")
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能系统安全监控 - 状态查询
    elif "安全监控" in intent or "系统安全" in intent or "security monitor" in intent.lower() or "安全状态" in intent:
        print(f"[智能系统安全监控] 正在获取安全状态...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "security_monitor_engine.py")
        cmd_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能系统安全监控 - 安全扫描
    elif "安全扫描" in intent or "scan security" in intent.lower() or "扫描安全" in intent or "安全检测" in intent:
        print(f"[智能系统安全监控] 正在执行安全扫描...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "security_monitor_engine.py")
        cmd_args = ["scan"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能系统安全监控 - 告警查看
    elif "安全告警" in intent or "security alert" in intent.lower() or "告警" in intent or "安全警报" in intent:
        print(f"[智能系统安全监控] 正在获取安全告警...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "security_monitor_engine.py")
        cmd_args = ["alerts"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能系统安全监控 - 持续监控
    elif "启动安全监控" in intent or "start security monitor" in intent.lower() or "开启安全监控" in intent:
        print(f"[智能系统安全监控] 正在启动持续监控...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "security_monitor_engine.py")
        cmd_args = ["monitor"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能创新发现引擎 - 状态查询
    elif "创新发现" in intent or "创新推荐" in intent or "发现新功能" in intent or "创新" in intent and ("发现" in intent or "推荐" in intent) or "innovation" in intent.lower() or "discover innovation" in intent.lower() or "new capability" in intent.lower():
        print(f"[智能创新发现引擎] 正在分析创新机会...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "innovation_discovery_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["status"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["创新发现", "创新推荐", "发现新功能", "创新", "innovation", "discover", "innovation discover"]]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能自主学习与创新引擎
    elif "自主学习" in intent or "主动进化" in intent or "系统自省" in intent or "自我优化" in intent or "autonomous" in intent.lower() or "self learning" in intent.lower() or "主动分析" in intent or "分析系统" in intent or "学习创新" in intent:
        print(f"[智能自主学习与创新引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "autonomous_learning_innovation_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["status"]
        # 过滤掉意图关键词
        filter_words = ["自主学习", "主动进化", "系统自省", "自我优化", "autonomous", "self learning", "主动分析", "分析系统", "学习创新"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words and not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环创新机会自动发现与主动进化引擎（Round 462）
    elif ("创新机会" in intent or "机会发现" in intent or "主动进化" in intent or "方案评估" in intent or "机会分析" in intent or "innovation opportunity" in intent.lower() or "opportunity discovery" in intent.lower()) and ("发现" in intent or "自动" in intent or "分析" in intent or "引擎" in intent or "status" in intent.lower()):
        print(f"[创新机会自动发现与主动进化引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_innovation_opportunity_discovery_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["创新机会", "发现", "自动", "分析", "引擎", "主动进化", "方案评估", "机会分析", "innovation", "opportunity", "discovery"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能跨引擎深度协同闭环增强器
    elif "深度协同" in intent or "闭环增强" in intent or "引擎集成" in intent or "深度集成" in intent or "跨引擎" in intent or "integration" in intent.lower() or "闭环" in intent or "集成" in intent:
        print(f"[智能跨引擎深度协同闭环增强器] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "deep_integration_orchestrator.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["status"]
        # 过滤掉意图关键词
        filter_words = ["深度协同", "闭环增强", "引擎集成", "深度集成", "跨引擎", "integration", "闭环", "集成"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words and not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 跨引擎协同效能深度分析与自优化引擎
    elif "协作效能" in intent or "效能分析" in intent or "跨引擎优化" in intent or "协作优化" in intent or "效能优化" in intent or "efficiency" in intent.lower() or "collaboration efficiency" in intent.lower() or "optimization" in intent.lower():
        print(f"[跨引擎协同效能深度分析与自优化引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_cross_engine_collaboration_efficiency_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["协作效能", "效能分析", "跨引擎优化", "协作优化", "效能优化", "efficiency", "collaboration", "optimization"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 跨引擎协同效能自动优化与知识驱动触发深度集成引擎 (Round 464)
    elif "效能自动优化" in intent or "自动优化" in intent or "协作效能自动化" in intent or "效能触发" in intent or "efficiency auto" in intent.lower() or "auto optimization" in intent.lower() or "optimization trigger" in intent.lower():
        print(f"[跨引擎协同效能自动优化与知识驱动触发深度集成引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_collaboration_efficiency_auto_optimization_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["效能自动优化", "自动优化", "协作效能自动化", "效能触发", "efficiency auto", "auto optimization", "optimization trigger"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 元进化与自动化深度集成引擎 (Round 465)
    elif "元进化优化" in intent or "策略自动调整" in intent or "元优化" in intent or "meta optimization" in intent.lower() or "strategy auto" in intent.lower() or "集成优化" in intent:
        print(f"[元进化与自动化深度集成引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_optimization_integration_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["元进化优化", "策略自动调整", "元优化", "meta optimization", "strategy auto", "集成优化"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 预警驱动自动策略调整引擎 (Round 466)
    elif "预警驱动" in intent or "预警策略" in intent or "warning driven" in intent.lower() or "预警调整" in intent or "自动策略调整" in intent or "策略预警" in intent or "warning strategy" in intent.lower() or "预警联动" in intent or "warning adjustment" in intent.lower():
        print(f"[预警驱动自动策略调整引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_warning_driven_strategy_adjustment_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["status"]
        # 过滤掉意图关键词
        filter_words = ["预警驱动", "预警策略", "warning driven", "预警调整", "自动策略调整", "策略预警", "warning strategy", "预警联动", "warning adjustment"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 预警驱动策略调整与进化驾驶舱深度集成引擎 (Round 467)
    elif "预警驾驶舱" in intent or "预警可视化" in intent or "warning cockpit" in intent.lower() or "预警集成" in intent or "策略调整可视化" in intent or "预警趋势驾驶舱" in intent or "warning integration" in intent.lower() or "预警数据推送" in intent:
        print(f"[预警驱动策略调整与进化驾驶舱深度集成引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_warning_cockpit_integration_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["status"]
        # 过滤掉意图关键词
        filter_words = ["预警驾驶舱", "预警可视化", "warning cockpit", "预警集成", "策略调整可视化", "预警趋势驾驶舱", "warning integration", "预警数据推送"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 跨维度自适应协同与全自动化价值实现追踪引擎 (Round 469)
    elif "跨维度协同" in intent or "跨维度自适应" in intent or "价值追踪" in intent or "价值实现" in intent or "cross dimension" in intent.lower() or "value tracking" in intent.lower() or "value realization" in intent.lower() or "跨维度" in intent or "自适应协同" in intent or "价值驱动" in intent:
        print(f"[跨维度自适应协同与全自动化价值实现追踪引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_cross_dimension_adaptive_collaboration_value_tracking_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["跨维度协同", "跨维度自适应", "价值追踪", "价值实现", "cross dimension", "value tracking", "value realization", "跨维度", "自适应协同", "价值驱动"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环跨引擎深度融合创新实现引擎 (Round 504) - 深度融合代码理解引擎、价值量化引擎、知识推荐引擎等已有能力，构建跨引擎创新组合自动发现与价值实现闭环
    elif "跨引擎融合" in intent or "融合创新" in intent or "跨引擎创新" in intent or "深度融合" in intent or "cross engine fusion" in intent.lower() or "fusion innovation" in intent.lower() or "引擎融合" in intent or "融合引擎" in intent or "创新融合" in intent or "跨引擎深度融合" in intent or "deep fusion" in intent.lower() or "cross-fusion" in intent.lower():
        print(f"[智能全场景进化环跨引擎深度融合创新实现引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_cross_engine_deep_fusion_innovation_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["跨引擎融合", "融合创新", "跨引擎创新", "深度融合", "cross engine fusion", "fusion innovation", "引擎融合", "融合引擎", "创新融合", "跨引擎深度融合", "deep fusion", "cross-fusion"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环价值预测与主动干预引擎 (Round 470) - 移除了与 Round 516 冲突的关键词
    elif "主动干预" in intent or "预防性价值" in intent or "价值趋势预测" in intent or "proactive intervention" in intent.lower() or "干预策略" in intent or "价值干预" in intent:
        print(f"[智能全场景进化环价值预测与主动干预引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_value_prediction_intervention_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["主动干预", "预防性价值", "价值趋势预测", "proactive intervention", "干预策略", "价值干预"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环价值实现预测与预防性增强引擎 (Round 516)
    elif "价值实现预测" in intent or "预测预防增强" in intent or "价值预测预防" in intent or "value_pred_prevent" in intent.lower() or "predict_prevent" in intent.lower():
        print(f"[智能全场景进化环价值实现预测与预防性增强引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_value_prediction_prevention_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["价值实现预测", "预测预防增强", "价值预测预防", "value_pred_prevent", "predict_prevent"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环价值实现预测与预防性增强引擎 (Round 525) - 在 round 524 完成的效能分析优化闭环基础上，进一步增强价值实现预测与预防性干预能力
    elif "价值实现趋势" in intent or "预防性干预策略" in intent or "价值预测干预" in intent or "value realization prediction" in intent.lower() or "prevention intervention" in intent.lower() or "价值实现效能" in intent or "效能价值预测" in intent or "value_effectiveness_predict" in intent.lower() or "round525" in intent.lower():
        print(f"[智能全场景进化环价值实现预测与预防性增强引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_value_realization_prediction_prevention_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 检测功能关键词
        if "预测趋势" in intent or "predict" in intent.lower() or "趋势预测" in intent:
            cmd_args = ["--predict"]
        elif "生成策略" in intent or "strategies" in intent.lower() or "干预策略" in intent:
            cmd_args = ["--strategies"]
        elif "执行干预" in intent or "execute" in intent.lower() or "预防执行" in intent:
            cmd_args = ["--execute"]
        elif "验证效果" in intent or "verify" in intent.lower():
            cmd_args = ["--verify"]
        elif "完整闭环" in intent or "closed loop" in intent.lower() or "full loop" in intent.lower():
            cmd_args = ["--closed-loop"]
        elif "驾驶舱" in intent or "cockpit" in intent.lower():
            cmd_args = ["--cockpit-data"]
        # 过滤掉意图关键词
        filter_words = ["价值实现趋势", "预防性干预策略", "价值预测干预", "value realization prediction", "prevention intervention", "价值实现效能", "效能价值预测", "value_effectiveness_predict", "round525", "预测趋势", "predict", "趋势预测", "生成策略", "strategies", "干预策略", "执行干预", "execute", "预防执行", "验证效果", "verify", "完整闭环", "closed loop", "full loop", "驾驶舱", "cockpit"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环预防性干预效果评估与持续优化引擎 (Round 527-528)
    elif "干预效果评估" in intent or "效果评估" in intent or "干预优化" in intent or "评估优化" in intent or "intervention evaluation" in intent.lower() or "effectiveness evaluation" in intent.lower() or "intervention optimization" in intent.lower() or "效果趋势分析" in intent or "趋势分析" in intent or "价值趋势预测" in intent or "预防性干预" in intent or "预测价值" in intent:
        print(f"[智能全场景进化环预防性干预效果评估与持续优化引擎 v1.1.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_preventive_intervention_evaluation_optimizer_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--cockpit-data"]
        # 检测功能关键词（增强 round 528）
        if "价值趋势预测" in intent or "预测价值" in intent or "predict" in intent.lower():
            cmd_args = ["--predict", "--prediction-days", "7"]
        elif "完整闭环" in intent or "full loop" in intent.lower() or "闭环" in intent:
            cmd_args = ["--full-loop"]
        elif "预防性策略" in intent or "策略生成" in intent or "strategy" in intent.lower():
            cmd_args = ["--generate-strategy"]
        elif "执行干预" in intent or "execute" in intent.lower():
            cmd_args = ["--execute"]
        elif "驾驶舱" in intent or "cockpit" in intent.lower():
            cmd_args = ["--cockpit-data"]
        elif "趋势" in intent or "trend" in intent.lower() or "分析" in intent:
            cmd_args = ["--analyze-trend"]
        elif "建议" in intent or "recommendation" in intent.lower() or "优化建议" in intent:
            cmd_args = ["--recommendations"]
        elif "评估" in intent or "evaluate" in intent.lower():
            cmd_args = ["--evaluate", "--intervention-id", "iv001", "--strategy-type", "ps001"]
        elif "指标" in intent or "metrics" in intent.lower():
            cmd_args = ["--metrics"]
        # 过滤掉意图关键词
        filter_words = ["干预效果评估", "效果评估", "干预优化", "评估优化", "intervention evaluation", "effectiveness evaluation", "intervention optimization", "效果趋势分析", "趋势分析", "趋势", "trend", "分析", "建议", "recommendation", "优化建议", "评估", "evaluate", "指标", "metrics", "价值趋势预测", "预防性干预", "预测价值", "完整闭环", "闭环", "预防性策略", "策略生成", "执行干预", "驾驶舱", "cockpit"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--cockpit-data"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环元进化价值预测与预防性优化引擎 V2 (Round 609) - 优先匹配
    elif "元进化价值预测V2" in intent or "元价值预测V2" in intent or "价值预测V2" in intent or "meta value predict v2" in intent.lower() or "meta_value_predict_v2" in intent.lower() or "价值预测增强" in intent or "价值预防优化V2" in intent or "价值预测与预防" in intent:
        print(f"[智能全场景进化环元进化价值预测与预防性优化引擎 V2.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_value_prediction_prevention_v2_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 检测功能关键词
        if "趋势分析" in intent or "trend" in intent.lower():
            cmd_args = ["--trend"]
        elif "预测" in intent or "predict" in intent.lower():
            cmd_args = ["--predict"]
        elif "异常检测" in intent or "anomaly" in intent.lower():
            cmd_args = ["--anomaly"]
        elif "优化" in intent or "optimize" in intent.lower():
            cmd_args = ["--optimize"]
        elif "调整" in intent or "adjust" in intent.lower():
            cmd_args = ["--adjust"]
        elif "集成" in intent or "integrate" in intent.lower():
            cmd_args = ["--integrate"]
        elif "完整循环" in intent or "run" in intent.lower():
            cmd_args = ["--run"]
        elif "驾驶舱" in intent or "cockpit" in intent.lower():
            cmd_args = ["--cockpit-data"]
        # 过滤掉意图关键词
        filter_words = ["元进化价值预测V2", "元价值预测V2", "价值预测V2", "meta value predict v2", "meta_value_predict_v2", "价值预测增强", "价值预防优化V2", "价值预测与预防", "趋势分析", "trend", "预测", "predict", "异常检测", "anomaly", "优化", "optimize", "调整", "adjust", "集成", "integrate", "完整循环", "run", "驾驶舱", "cockpit"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环元进化价值预测与预防性优化引擎 (Round 560)
    elif "元进化价值预测" in intent or "元价值预测" in intent or "meta value predict" in intent.lower() or "meta_value_predict" in intent.lower() or "元价值预防" in intent or "价值趋势预警" in intent or "价值异常检测" in intent:
        print(f"[智能全场景进化环元进化价值预测与预防性优化引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_value_prediction_prevention_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 检测功能关键词
        if "预测趋势" in intent or "predict" in intent.lower() or "趋势预测" in intent:
            cmd_args = ["--predict"]
        elif "异常检测" in intent or "anomaly" in intent.lower():
            cmd_args = ["--anomaly"]
        elif "生成策略" in intent or "strategies" in intent.lower():
            cmd_args = ["--strategies"]
        elif "执行优化" in intent or "execute" in intent.lower() or "预防执行" in intent:
            cmd_args = ["--execute"]
        elif "完整闭环" in intent or "closed loop" in intent.lower():
            cmd_args = ["--closed-loop"]
        elif "驾驶舱" in intent or "cockpit" in intent.lower():
            cmd_args = ["--cockpit-data"]
        # 过滤掉意图关键词
        filter_words = ["元进化价值预测", "元价值预测", "meta value predict", "meta_value_predict", "元价值预防", "价值趋势预警", "价值异常检测", "预测趋势", "predict", "趋势预测", "异常检测", "anomaly", "生成策略", "strategies", "执行优化", "execute", "预防执行", "完整闭环", "closed loop", "驾驶舱", "cockpit"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环元进化价值投资组合优化与风险对冲引擎 (Round 561)
    elif "元进化价值投资" in intent or "价值投资" in intent or "投资组合" in intent or "风险对冲" in intent or "portfolio" in intent.lower() or "hedge" in intent.lower() or "value investment" in intent.lower() or "投资优化" in intent or "组合优化" in intent:
        print(f"[智能全场景进化环元进化价值投资组合优化与风险对冲引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_value_investment_portfolio_optimizer.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--cockpit-data"]
        # 检测功能关键词
        if "分析" in intent or "analyze" in intent.lower():
            cmd_args = ["--analyze"]
        elif "分配" in intent or "allocation" in intent.lower():
            cmd_args = ["--allocation"]
        elif "优化策略" in intent or "optimize" in intent.lower():
            cmd_args = ["--optimize"]
        elif "对冲" in intent or "hedge" in intent.lower():
            cmd_args = ["--hedge"]
        elif "绩效" in intent or "performance" in intent.lower():
            cmd_args = ["--performance"]
        elif "驾驶舱" in intent or "cockpit" in intent.lower():
            cmd_args = ["--cockpit-data"]
        elif "完整" in intent or "full" in intent.lower():
            cmd_args = ["--full"]
        # 过滤掉意图关键词
        filter_words = ["元进化价值投资", "价值投资", "投资组合", "风险对冲", "portfolio", "hedge", "value investment", "投资优化", "组合优化", "分析", "analyze", "分配", "allocation", "优化策略", "optimize", "对冲", "绩效", "performance", "驾驶舱", "cockpit", "完整", "full"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--cockpit-data"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True, encoding='utf-8', errors='replace')
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环价值知识图谱深度推理与智能决策增强引擎 (Round 562)
    elif "价值知识图谱" in intent or "知识图谱推理" in intent or "知识推理决策" in intent or "价值推理" in intent or "kg reasoning" in intent.lower() or "value kg" in intent.lower() or "知识图谱增强" in intent or "推理增强" in intent:
        print(f"[智能全场景进化环价值知识图谱深度推理与智能决策增强引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_value_knowledge_graph_reasoning_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--cockpit-data"]
        # 检测功能关键词
        if "构建" in intent or "build" in intent.lower():
            cmd_args = ["--build-kg"]
        elif "推理" in intent or "reason" in intent.lower():
            cmd_args = ["--reason"]
        elif "推荐" in intent or "recommend" in intent.lower():
            cmd_args = ["--recommend"]
        elif "增强" in intent or "enhance" in intent.lower():
            cmd_args = ["--enhance"]
        elif "驾驶舱" in intent or "cockpit" in intent.lower():
            cmd_args = ["--cockpit-data"]
        elif "完整" in intent or "full" in intent.lower():
            cmd_args = ["--full"]
        # 过滤掉意图关键词
        filter_words = ["价值知识图谱", "知识图谱推理", "知识推理决策", "价值推理", "kg reasoning", "value kg", "知识图谱增强", "推理增强", "构建", "build", "推理", "reason", "推荐", "recommend", "增强", "enhance", "驾驶舱", "cockpit", "完整", "full"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--cockpit-data"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True, encoding='utf-8', errors='replace')
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环多维度价值协同融合与自适应决策增强引擎 (Round 563)
    elif "多维度价值" in intent or "价值协同" in intent or "价值融合" in intent or "自适应决策" in intent or "多维价值优化" in intent or "multi dimension value" in intent.lower() or "value synergy" in intent.lower() or "value fusion" in intent.lower() or "adaptive decision" in intent.lower():
        print(f"[智能全场景进化环多维度价值协同融合与自适应决策增强引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_multi_dimension_value_synergy_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--cockpit-data"]
        # 检测功能关键词
        if "整合" in intent or "integrate" in intent.lower():
            cmd_args = ["--integrate"]
        elif "协同" in intent or "synergy" in intent.lower():
            cmd_args = ["--reason"]
        elif "决策" in intent or "decision" in intent.lower():
            cmd_args = ["--decide"]
        elif "路径" in intent or "path" in intent.lower():
            cmd_args = ["--path"]
        elif "驾驶舱" in intent or "cockpit" in intent.lower():
            cmd_args = ["--cockpit-data"]
        elif "完整" in intent or "full" in intent.lower():
            cmd_args = ["--full"]
        # 过滤掉意图关键词
        filter_words = ["多维度价值", "价值协同", "价值融合", "自适应决策", "多维价值优化", "multi dimension value", "value synergy", "value fusion", "adaptive decision", "整合", "integrate", "协同", "synergy", "决策", "decision", "路径", "path", "驾驶舱", "cockpit", "完整", "full"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--cockpit-data"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True, encoding='utf-8', errors='replace')
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环创新驱动价值实现增强引擎 (Round 564)
    elif "创新驱动价值" in intent or "价值实现" in intent or "创新价值" in intent or "创新实现" in intent or "innovation driven value" in intent.lower() or "value realization" in intent.lower() or "innovation value" in intent.lower():
        print(f"[智能全场景进化环创新驱动价值实现增强引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_innovation_driven_value_realization_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 检测功能关键词
        if "发现" in intent or "discover" in intent.lower():
            cmd_args = ["--discover"]
        elif "评估" in intent or "evaluate" in intent.lower():
            cmd_args = ["--evaluate"]
        elif "驱动" in intent or "drive" in intent.lower():
            cmd_args = ["--drive"]
        elif "驾驶舱" in intent or "cockpit" in intent.lower():
            cmd_args = ["--cockpit-data"]
        elif "完整" in intent or "闭环" in intent or "full" in intent.lower() or "run" in intent.lower():
            cmd_args = ["--run"]
        # 过滤掉意图关键词
        filter_words = ["创新驱动价值", "价值实现", "创新价值", "创新实现", "innovation driven value", "value realization", "innovation value", "发现", "discover", "评估", "evaluate", "驱动", "drive", "驾驶舱", "cockpit", "完整", "闭环", "full", "run"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--cockpit-data"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True, encoding='utf-8', errors='replace')
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环价值驱动元进化自适应决策引擎 (Round 565)
    elif "价值驱动元进化" in intent or "元进化决策" in intent or "价值自适应" in intent or "驱动决策" in intent or "value driven meta" in intent.lower() or "meta evolution decision" in intent.lower() or "value adaptive" in intent.lower() or "value driven decision" in intent.lower():
        print(f"[智能全场景进化环价值驱动元进化自适应决策引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_value_driven_meta_evolution_adaptive_decision_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--analyze"]
        # 检测功能关键词
        if "分析" in intent or "analyze" in intent.lower():
            cmd_args = ["--analyze"]
        elif "决策" in intent or "decision" in intent.lower():
            cmd_args = ["--decisions"]
        elif "驾驶舱" in intent or "cockpit" in intent.lower():
            cmd_args = ["--cockpit-data"]
        elif "自适应" in intent or "adapt" in intent.lower():
            cmd_args = ["--adapt"]
        # 过滤掉意图关键词
        filter_words = ["价值驱动元进化", "元进化决策", "价值自适应", "驱动决策", "value driven meta", "meta evolution decision", "value adaptive", "value driven decision", "分析", "analyze", "决策", "decision", "驾驶舱", "cockpit", "自适应", "adapt"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--analyze"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True, encoding='utf-8', errors='replace')
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环元进化价值执行验证与持续学习引擎 (Round 566)
    elif "价值执行" in intent or "执行验证" in intent or "持续学习" in intent or "价值学习" in intent or "value execution" in intent.lower() or "execution verification" in intent.lower() or "continuous learning" in intent.lower() or "value learning" in intent.lower():
        print(f"[智能全场景进化环元进化价值执行验证与持续学习引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_value_execution_verification_continuous_learning_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--execute"]
        # 检测功能关键词
        if "执行" in intent or "execute" in intent.lower():
            cmd_args = ["--execute"]
        elif "驾驶舱" in intent or "cockpit" in intent.lower():
            cmd_args = ["--cockpit-data"]
        elif "任务" in intent or "task" in intent.lower():
            cmd_args = ["--tasks"]
        elif "验证" in intent or "verify" in intent.lower():
            cmd_args = ["--verify"]
        # 过滤掉意图关键词
        filter_words = ["价值执行", "执行验证", "持续学习", "价值学习", "value execution", "execution verification", "continuous learning", "value learning", "执行", "execute", "驾驶舱", "cockpit", "任务", "task", "验证", "verify"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--execute"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True, encoding='utf-8', errors='replace')
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环元进化全链路自主运行自动化引擎 (Round 567)
    elif "元进化全链路" in intent or "元进化自主运行" in intent or "元进化无人值守" in intent or "全链路自动化进化" in intent or "meta evolution full auto" in intent.lower() or "meta auto loop" in intent.lower() or "evolution full automation" in intent.lower():
        print(f"[智能全场景进化环元进化全链路自主运行自动化引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_evolution_full_auto_loop_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 检测功能关键词
        if "运行" in intent or "run" in intent.lower() or "执行" in intent.lower():
            cmd_args = ["--run"]
        elif "驾驶舱" in intent or "cockpit" in intent.lower():
            cmd_args = ["--cockpit-data"]
        elif "状态" in intent or "status" in intent.lower():
            cmd_args = ["--status"]
        elif "检查" in intent or "check" in intent.lower():
            cmd_args = ["--check"]
        # 过滤掉意图关键词
        filter_words = ["元进化全链路", "元进化自主运行", "元进化无人值守", "全链路自动化进化", "meta evolution full auto", "meta auto loop", "evolution full automation", "运行", "run", "执行", "驾驶舱", "cockpit", "状态", "status", "检查", "check"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True, encoding='utf-8', errors='replace')
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环价值干预自动执行引擎 (Round 471)
    elif "价值干预自动执行" in intent or "干预自动执行" in intent or "自动干预" in intent or "干预执行" in intent or "价值干预执行" in intent or "auto intervention" in intent.lower() or "execute intervention" in intent.lower():
        print(f"[智能全场景进化环价值干预自动执行引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_value_intervention_auto_execution_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["价值干预自动执行", "干预自动执行", "自动干预", "干预执行", "价值干预执行", "auto intervention", "execute intervention"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环自适应价值优化引擎 (Round 472)
    elif "自适应价值优化" in intent or "价值优化" in intent or "价值自适应" in intent or "自适应优化" in intent or "价值参数调整" in intent or "adaptive value optimization" in intent.lower() or "value optimization" in intent.lower() or "adaptive optimization" in intent.lower():
        print(f"[智能全场景进化环自适应价值优化引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_adaptive_value_optimization_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["自适应价值优化", "价值优化", "价值自适应", "自适应优化", "价值参数调整", "adaptive value optimization", "value optimization", "adaptive optimization"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环元进化驱动的自适应价值深度优化引擎 (Round 473)
    elif "元进化价值优化" in intent or "元进化驱动优化" in intent or "元价值优化" in intent or "meta value optimization" in intent.lower() or "meta driven" in intent.lower():
        print(f"[智能全场景进化环元进化驱动的自适应价值深度优化引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_driven_adaptive_value_deep_optimization_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["元进化价值优化", "元进化驱动优化", "元价值优化", "meta value optimization", "meta driven"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环认知-价值-元进化深度融合引擎 (Round 474)
    elif "认知价值融合" in intent or "认知驱动优化" in intent or "认知元进化" in intent or "cognition value fusion" in intent.lower() or "cognition driven" in intent.lower() or "cognitive meta" in intent.lower():
        print(f"[智能全场景进化环认知-价值-元进化深度融合引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_cognition_value_meta_fusion_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["认知价值融合", "认知驱动优化", "认知元进化", "cognition value fusion", "cognition driven", "cognitive meta"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环全维度价值-风险平衡自适应优化引擎 (Round 541)
    # 在 round 540 决策执行质量闭环、round 539 战略执行闭环、round 538 自我进化意识基础上，构建全维度价值-风险平衡优化能力
    elif "价值风险平衡" in intent or "风险评估" in intent or "多维度优化" in intent or "risk balance" in intent.lower() or "value risk" in intent.lower() or "风险平衡" in intent or "价值平衡" in intent or "多维度价值" in intent or "价值-风险" in intent or "risk assessment" in intent.lower():
        print(f"[智能全场景进化环全维度价值-风险平衡自适应优化引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_value_risk_balance_optimizer_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["价值风险平衡", "风险评估", "多维度优化", "risk balance", "value risk", "风险平衡", "价值平衡", "多维度价值", "价值-风险", "risk assessment"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--analyze"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环跨引擎协作元优化与智能编排引擎 (Round 543)
    # 在 round 541 价值风险平衡优化、round 538 自我进化意识基础上，构建跨引擎协作元优化能力
    elif "跨引擎优化" in intent or "引擎编排优化" in intent or "协作优化" in intent or "编排建议" in intent or "引擎调度" in intent or "cross engine" in intent.lower() or "orchestration" in intent.lower() or "engine scheduling" in intent.lower() or "cross-engine" in intent.lower() or "meta optimization" in intent.lower():
        print(f"[智能全场景进化环跨引擎协作元优化与智能编排引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_cross_engine_orchestration_meta_optimizer.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["跨引擎优化", "引擎编排优化", "协作优化", "编排建议", "引擎调度", "cross engine", "orchestration", "engine scheduling", "cross-engine", "meta optimization"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--analyze"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环创新投资组合优化引擎 (Round 544)
    # 在 round 506 ROI 评估、round 541 价值风险平衡、round 543 跨引擎协作优化成果基础上，构建创新投资组合优化能力
    elif "创新投资组合" in intent or "投资组合优化" in intent or "组合管理" in intent or "创新优化" in intent or "portfolio" in intent.lower() or "innovation portfolio" in intent.lower() or "投资组合" in intent or "组合分配" in intent:
        print(f"[智能全场景进化环创新投资组合优化引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_innovation_portfolio_optimizer_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["创新投资组合", "投资组合优化", "组合管理", "创新优化", "portfolio", "innovation portfolio", "投资组合", "组合分配"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--analyze"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环元进化创新投资组合优化与战略决策增强引擎 (Round 602)
    # 在 round 600-601 完成的创新涌现与创新价值自动实现引擎基础上，构建让系统能够从600+轮进化历史中分析创新投资回报、智能分配创新资源、形成创新战略决策能力
    elif "创新投资组合优化" in intent or "创新战略决策" in intent or "战略决策增强" in intent or "创新投资优化" in intent or "innovation portfolio optimizer" in intent.lower() or "strategic decision" in intent.lower() or "创新资源配置" in intent:
        print(f"[智能全场景进化环元进化创新投资组合优化与战略决策增强引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_innovation_portfolio_optimizer_strategic_decision_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["创新投资组合优化", "创新战略决策", "战略决策增强", "创新投资优化", "innovation portfolio optimizer", "strategic decision", "创新资源配置", "投资组合", "战略决策"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环创新生态系统深度治理与价值最大化引擎 (Round 610)
    # 在 round 608-609 完成的创新投资组合优化引擎和价值预测预防优化引擎 V2 基础上，构建完整的创新生态系统治理能力
    # 实现创新资源全局优化配置、跨领域创新协同促进、创新风险预警与防控、创新价值链端到端管理
    elif "创新生态系统" in intent or "生态系统治理" in intent or "创新治理" in intent or "生态系统管理" in intent or "innovation ecosystem" in intent.lower() or "ecosystem governance" in intent.lower() or "创新资源优化" in intent or "跨领域创新" in intent or "创新价值链" in intent or "价值链管理" in intent:
        print(f"[智能全场景进化环创新生态系统深度治理与价值最大化引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_innovation_ecosystem_governance_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["创新生态系统", "生态系统治理", "创新治理", "生态系统管理", "innovation ecosystem", "ecosystem governance", "创新资源优化", "跨领域创新", "创新价值链", "价值链管理", "资源优化", "跨领域"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环跨维度价值平衡全局决策与自适应优化引擎 (Round 611)
    # 在 round 608-610 完成的创新投资组合优化引擎、价值预测预防优化引擎 V2、创新生态系统治理引擎基础上
    # 实现跨维度价值全局评估、价值平衡智能决策、自适应价值优化
    elif "全局价值决策" in intent or "跨维度全局价值" in intent or "价值中枢" in intent or "自适应价值优化" in intent or "跨维度价值平衡" in intent or "全局价值优化" in intent:
        print(f"[智能全场景进化环跨维度价值平衡全局决策与自适应优化引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_cross_dimension_value_balance_global_decision_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["全局价值决策", "跨维度全局价值", "价值中枢", "自适应价值优化", "跨维度价值平衡", "全局价值优化"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环元进化执行闭环全自动化深度增强引擎 (Round 612)
    # 在 round 611 完成的跨维度价值平衡全局决策引擎基础上，构建真正的元进化执行闭环全自动化能力。
    # 让系统能够自主识别进化机会、自动生成进化策略、智能执行进化任务、自动验证进化结果、持续优化进化方法
    elif "元进化执行闭环" in intent or "全自动化进化" in intent or "执行闭环自动化" in intent or "meta execution closed loop" in intent.lower() or "evolution automation" in intent.lower() or "自主进化闭环" in intent or "进化自主运行" in intent or "自动进化" in intent:
        print(f"[智能全场景进化环元进化执行闭环全自动化深度增强引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_execution_closed_loop_automation_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["元进化执行闭环", "全自动化进化", "执行闭环自动化", "meta execution", "evolution automation", "自主进化闭环", "进化自主运行", "自动进化"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环元进化自主决策元认知引擎 (Round 613)
    # 在 round 612 完成的元进化执行闭环全自动化引擎基础上，构建让系统能够反思自身决策过程、
    # 评估决策质量、优化决策策略的元认知能力，形成「学会如何决策」的递归优化能力
    elif "元进化自主决策" in intent or "决策元认知" in intent or "决策反思" in intent or "决策质量" in intent or "决策优化" in intent or "meta decision" in intent.lower() or "decision meta" in intent.lower() or "学会决策" in intent or "决策元知识" in intent:
        print(f"[智能全场景进化环元进化自主决策元认知引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_decision_meta_cognition_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["元进化自主决策", "决策元认知", "决策反思", "决策质量", "决策优化", "meta decision", "decision meta", "学会决策", "决策元知识"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环元进化能力缺口主动发现与自愈引擎 (Round 615)
    # 在 round 614 完成的元进化价值自循环与进化飞轮增强引擎基础上，构建让系统能够主动发现能力缺口
    # 并自动修复的完整自愈闭环。实现从「被动修复问题」到「主动预防并自愈」的范式升级
    elif "能力缺口" in intent or "自愈" in intent or "缺口发现" in intent or "主动修复" in intent or "capability gap" in intent.lower() or "self healing" in intent.lower() or "gap discovery" in intent.lower() or "自愈引擎" in intent or "能力自愈" in intent or "缺口自愈" in intent:
        print(f"[智能全场景进化环元进化能力缺口主动发现与自愈引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_capability_gap_discovery_self_healing_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["能力缺口", "自愈", "缺口发现", "主动修复", "capability gap", "self healing", "gap discovery", "自愈引擎", "能力自愈", "缺口自愈"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环元进化智能体集群协同优化引擎 (Round 616)
    # 在 round 615 完成的元进化能力缺口主动发现与自愈引擎基础上，构建让系统能够自动协调
    # 多个元进化引擎的工作，实现更高效的协同进化。实现从「单引擎独立工作」到「多引擎智能协同」的范式升级
    elif "集群协同" in intent or "多引擎协同" in intent or "引擎集群" in intent or "cluster collaboration" in intent.lower() or "multi engine" in intent.lower() or "engine cluster" in intent.lower() or "元进化协同" in intent or "智能体集群" in intent or "agent cluster" in intent.lower() or "协同优化" in intent:
        print(f"[智能全场景进化环元进化智能体集群协同优化引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_agent_cluster_collaboration_optimizer.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["集群协同", "多引擎协同", "引擎集群", "cluster collaboration", "multi engine", "engine cluster", "元进化协同", "智能体集群", "agent cluster", "协同优化"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环元进化价值感知与自我激励深度增强引擎 (Round 617)
    # 在 round 614 完成的元进化价值自循环与进化飞轮增强引擎基础上，构建让系统能够
    # 主动感知自身价值实现状态的深度增强能力。实现「价值感知→差距识别→自我激励→路径优化→实现反馈」的完整闭环
    elif "价值感知" in intent or "自我激励" in intent or "价值差距" in intent or "value awareness" in intent.lower() or "self motivation" in intent.lower() or "value gap" in intent.lower() or "价值激励" in intent or "自我价值感知" in intent or "价值状态感知" in intent:
        print(f"[智能全场景进化环元进化价值感知与自我激励深度增强引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_value_awareness_self_motivation_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["价值感知", "自我激励", "价值差距", "value awareness", "self motivation", "value gap", "价值激励", "自我价值感知", "价值状态感知"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环元进化系统深度健康诊断与跨引擎智能修复闭环增强引擎 (Round 618)
    # 在 round 497-498、451、615 完成的健康诊断与自愈引擎基础上，利用600+轮进化历史的模式识别能力，
    # 构建深度诊断元进化系统健康状态并智能修复的增强能力。实现「深度诊断→智能修复→持续优化」的增强闭环
    elif "健康诊断" in intent or "深度健康" in intent or "系统诊断" in intent or "health diagnosis" in intent.lower() or "health repair" in intent.lower() or "自愈" in intent and "元进化" in intent or "智能修复" in intent or "跨引擎修复" in intent or "深度诊断" in intent or "预防性健康" in intent or "健康预警" in intent or "meta health" in intent.lower():
        print(f"[智能全场景进化环元进化系统深度健康诊断与跨引擎智能修复闭环增强引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_system_deep_health_diagnosis_repair_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["健康诊断", "深度健康", "系统诊断", "health diagnosis", "health repair", "自愈", "智能修复", "跨引擎修复", "深度诊断", "预防性健康", "健康预警", "meta health"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 在 round 618 完成的元进化系统深度健康诊断与跨引擎智能修复闭环增强引擎基础上，
    # 构建让系统能够主动预测进化趋势、预判风险机会、主动规划预防性演化策略的增强能力。
    # 实现「预测→预判→规划→执行→验证」的完整主动演化闭环
    elif "智能预测" in intent or "主动演化" in intent or "演化预测" in intent or "趋势预测" in intent or "进化预测" in intent or "prediction" in intent.lower() and "evolution" in intent.lower() or "proactive evolution" in intent.lower() or "风险预判" in intent or "机会预判" in intent or "预防性演化" in intent or "演化趋势" in intent or "元进化预测" in intent:
        print(f"[智能全场景进化环元进化智能预测与主动演化增强引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_intelligent_prediction_proactive_evolution_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["智能预测", "主动演化", "演化预测", "趋势预测", "进化预测", "prediction", "proactive evolution", "风险预判", "机会预判", "预防性演化", "演化趋势", "元进化预测"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环元进化执行效能实时优化引擎 (Round 620)
    # 让系统能够实时监控进化执行过程中的效率指标，自动识别性能瓶颈，
    # 动态生成优化策略并执行验证，形成「监控→分析→优化→验证」的持续效能提升闭环
    elif "效能优化" in intent or "执行效能" in intent or "效率优化" in intent or "效能监控" in intent or "瓶颈分析" in intent or "efficiency optimization" in intent.lower() or "execution efficiency" in intent.lower() or "bottleneck analysis" in intent.lower() or "performance bottleneck" in intent.lower() or "优化策略" in intent or "效能趋势" in intent or "元进化效能" in intent:
        print(f"[智能全场景进化环元进化执行效能实时优化引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_execution_efficiency_realtime_optimizer.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["效能优化", "执行效能", "效率优化", "效能监控", "瓶颈分析", "efficiency optimization", "execution efficiency", "bottleneck analysis", "performance bottleneck", "优化策略", "效能趋势", "元进化效能"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环进化效能自动化归因与智能建议引擎 (Round 545)
    # 基于540+轮进化历史，自动分析每轮进化的成效，识别成功/失败的根本原因，并智能生成可执行的改进建议
    elif "归因分析" in intent or "根因分析" in intent or "改进建议" in intent or "效果归因" in intent or "attribution" in intent.lower() or "root cause" in intent.lower() or "improvement advice" in intent.lower() or "进化归因" in intent or "成效分析" in intent:
        print(f"[智能全场景进化环进化效能自动化归因与智能建议引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_effectiveness_attribution_advice_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--analyze"]
        # 过滤掉意图关键词
        filter_words = ["归因分析", "根因分析", "改进建议", "效果归因", "attribution", "root cause", "improvement advice", "进化归因", "成效分析"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--analyze"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环进化效能智能对话分析与趋势预测引擎 (Round 546)
    # 基于 round 545 归因引擎，进一步构建对话式效能分析与趋势预测能力
    elif "效能对话" in intent or "进化效能问答" in intent or "效能趋势" in intent or "效能预测" in intent or "智能效能顾问" in intent or "efficiency dialog" in intent.lower() or "efficiency trend" in intent.lower() or "efficiency prediction" in intent.lower() or "efficiency advisor" in intent.lower() or "问我效能" in intent or "效能报告" in intent or "对话效能" in intent:
        print(f"[智能全场景进化环进化效能智能对话分析与趋势预测引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_efficiency_dialog_analysis_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 过滤意图关键词
        filter_words = ["效能对话", "进化效能问答", "效能趋势", "效能预测", "智能效能顾问", "efficiency dialog", "efficiency trend", "efficiency prediction", "efficiency advisor", "问我效能", "效能报告", "对话效能"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]

        # 检测功能关键词
        if "--report" in cmd_args or "报告" in intent:
            cmd_args = ["--report"]
        elif "--predict" in cmd_args:
            cmd_args = ["--predict"]
        elif "--recent" in cmd_args:
            cmd_args = ["--recent"]
        elif "--cockpit-data" in cmd_args:
            cmd_args = ["--cockpit-data"]
        elif "--version" in cmd_args:
            cmd_args = ["--version"]
        elif not filtered_args:
            # 无额外参数时默认生成报告
            cmd_args = ["--report"]
        else:
            # 将过滤后的参数作为问题
            if filtered_args:
                cmd_args = ["--ask", ' '.join(filtered_args)]
            else:
                cmd_args = ["--report"]
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环系统性健康持续监测与预警增强引擎 (Round 547)
    # 基于 round 546 对话式效能分析引擎，构建系统性健康持续监测与预警增强能力
    elif "系统性健康" in intent or "健康监测" in intent or "持续监测" in intent or "systematic health" in intent.lower() or "health monitoring" in intent.lower() or "continuous monitoring" in intent.lower() or "健康预警" in intent or "health warning" in intent.lower() or "健康趋势" in intent or "health trend" in intent.lower() or "进化健康" in intent or "evolution health" in intent.lower():
        print(f"[智能全场景进化环系统性健康持续监测与预警增强引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_systematic_health_monitoring_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 过滤意图关键词
        filter_words = ["系统性健康", "健康监测", "持续监测", "systematic health", "health monitoring", "continuous monitoring", "健康预警", "health warning", "健康趋势", "health trend", "进化健康", "evolution health"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]

        # 检测功能关键词
        if "--status" in cmd_args or "状态" in intent:
            cmd_args = ["--status"]
        elif "--predict" in cmd_args or "预测" in intent:
            cmd_args = ["--predict"]
            if "--rounds-ahead" in cmd_args:
                # 提取预测轮次
                import re
                match = re.search(r'--rounds-ahead\s+(\d+)', ' '.join(cmd_args))
                if match:
                    cmd_args = ["--predict", "--rounds-ahead", match.group(1)]
        elif "--warnings" in cmd_args or "预警" in intent:
            cmd_args = ["--warnings"]
        elif "--monitor" in cmd_args:
            cmd_args = ["--monitor"]
        elif "--cockpit-data" in cmd_args or "驾驶舱" in intent or "cockpit" in intent.lower():
            cmd_args = ["--cockpit-data"]
        elif "--version" in cmd_args:
            cmd_args = ["--version"]
        elif not filtered_args:
            # 无额外参数时默认执行持续监测
            cmd_args = ["--monitor"]
        else:
            cmd_args = filtered_args if filtered_args else ["--monitor"]

        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环健康监测-效能对话深度集成引擎 (Round 548)
    # 将 round 547 的系统性健康持续监测与预警增强引擎与 round 546 的进化效能智能对话分析引擎深度集成
    elif "健康对话" in intent or "健康集成" in intent or "监测对话" in intent or "health dialog" in intent.lower() or "health integration" in intent.lower() or "monitoring dialog" in intent.lower() or "健康问答" in intent or "health qa" in intent.lower() or "health question" in intent.lower() or "问我健康" in intent:
        print(f"[智能全场景进化环健康监测-效能对话深度集成引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_health_monitoring_dialog_integration_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []

        # 检测功能关键词
        if "报告" in intent:
            cmd_args = ["--report"]
        elif "问" in intent:
            # 提取问题
            import re
            match = re.search(r'问[道](.+)', intent)
            if match:
                question = match.group(1).strip()
                cmd_args = ["--ask", question]
            else:
                cmd_args = ["--ask", "健康状态如何"]
        elif "预警" in intent:
            cmd_args = ["--warnings"]
        elif "通知" in intent:
            cmd_args = ["--notify"]
        elif "状态" in intent:
            cmd_args = ["--status"]
        elif "驾驶舱" in intent or "cockpit" in intent.lower():
            cmd_args = ["--cockpit-data"]
        elif "--version" in cmd_args:
            cmd_args = ["--version"]
        else:
            # 无额外参数时默认生成报告
            cmd_args = ["--report"]

        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环自我进化效能深度分析与自适应优化引擎 (Round 475/487)
    # Round 487 增强：支持策略参数自动调整、模式提取、迭代优化等自适应学习能力
    elif "效能分析" in intent or "自我优化" in intent or "进化效能" in intent or "效能瓶颈" in intent or "effectiveness" in intent.lower() or "self optimization" in intent.lower() or "evolution effectiveness" in intent.lower() or "自适应学习" in intent or "策略调整" in intent or "模式提取" in intent or "迭代优化" in intent or "recursive optimization" in intent.lower() or "strategy adjustment" in intent.lower() or "pattern extraction" in intent.lower():
        print(f"[智能全场景进化环自我进化效能深度分析与自适应优化引擎 v1.1.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_self_evolution_effectiveness_analysis_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 检测新功能关键词
        if "提取模式" in intent or "extract pattern" in intent.lower():
            cmd_args = ["--extract-patterns"]
        elif "自动调整" in intent or "auto adjust" in intent.lower() or "策略调整" in intent:
            cmd_args = ["--auto-adjust"]
        elif "应用策略" in intent or "apply strategy" in intent.lower():
            cmd_args = ["--apply-strategy"]
        elif "迭代优化" in intent or "iterative" in intent.lower():
            # 提取迭代次数
            import re
            match = re.search(r'(\d+)', intent)
            iterations = int(match.group(1)) if match else 3
            cmd_args = ["--iterative", str(iterations)]
        elif "完整闭环" in intent or "full loop" in intent.lower() or "自适应学习" in intent:
            cmd_args = ["--full-loop"]
        # 过滤掉意图关键词
        filter_words = ["效能分析", "自我优化", "进化效能", "效能瓶颈", "effectiveness", "self optimization", "evolution effectiveness", "自适应学习", "策略调整", "模式提取", "迭代优化", "recursive optimization", "strategy adjustment", "pattern extraction", "完整闭环", "full loop", "提取模式", "自动调整", "应用策略"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环跨引擎协同学习与知识共享深度增强引擎 (Round 488)
    elif "跨引擎协同学习" in intent or "协同学习" in intent or "知识共享" in intent or "跨引擎学习" in intent or "模式复用" in intent or "cross engine collaborative" in intent.lower() or "collaborative learning" in intent.lower() or "knowledge sharing" in intent.lower() or "pattern reuse" in intent.lower() or "跨引擎知识" in intent:
        print(f"[智能全场景进化环跨引擎协同学习与知识共享深度增强引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_cross_engine_collaborative_learning_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 检测功能关键词
        if "收集经验" in intent or "collect" in intent.lower():
            cmd_args = ["--collect"]
        elif "识别模式" in intent or "identify pattern" in intent.lower() or "可复用模式" in intent:
            cmd_args = ["--identify-patterns"]
        elif "共享知识" in intent or "share" in intent.lower() or "知识分享" in intent:
            cmd_args = ["--share"]
        elif "效果" in intent or "effectiveness" in intent.lower() or "学习效果" in intent:
            cmd_args = ["--effectiveness"]
        elif "驾驶舱数据" in intent or "cockpit data" in intent.lower():
            cmd_args = ["--cockpit-data"]
        # 过滤掉意图关键词
        filter_words = ["跨引擎协同学习", "协同学习", "知识共享", "跨引擎学习", "模式复用", "cross engine collaborative", "collaborative learning", "knowledge sharing", "pattern reuse", "跨引擎知识", "收集经验", "识别模式", "共享知识", "学习效果", "驾驶舱数据"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环跨引擎深度知识蒸馏与智能传承增强引擎 (Round 489)
    elif "知识蒸馏" in intent or "知识传承" in intent or "提炼知识" in intent or "knowledge distillation" in intent.lower() or "knowledge inheritance" in intent.lower() or "知识传承" in intent or "知识提炼" in intent or "传承知识" in intent:
        print(f"[智能全场景进化环跨引擎深度知识蒸馏与智能传承增强引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_knowledge_distillation_inheritance_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 检测功能关键词
        if "蒸馏" in intent or "distill" in intent.lower():
            cmd_args = ["--distill"]
        elif "传承" in intent or "inherit" in intent.lower():
            cmd_args = ["--inherit"]
        elif "质量" in intent or "quality" in intent.lower() or "评估" in intent:
            cmd_args = ["--assess-quality"]
        elif "驾驶舱数据" in intent or "cockpit data" in intent.lower():
            cmd_args = ["--cockpit-data"]
        elif "搜索" in intent or "检索" in intent or "search" in intent.lower():
            # 提取搜索关键词
            search_keywords = [w for w in sys.argv[1:] if not w.startswith("-") and w not in ["知识蒸馏", "知识传承", "提炼知识", "传承知识"]]
            cmd_args = ["--search", search_keywords[0]] if search_keywords else ["--search", "进化"]
        # 过滤掉意图关键词
        filter_words = ["知识蒸馏", "知识传承", "提炼知识", "knowledge distillation", "knowledge inheritance", "传承知识", "知识提炼", "搜索", "检索"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环知识主动涌现发现与智能传承递归增强引擎 (Round 521)
    # 在 round 489 跨引擎深度知识蒸馏与智能传承增强引擎基础上，进一步增强知识的主动涌现发现与创新传承能力
    elif "知识涌现" in intent or "涌现发现" in intent or "emergence" in intent.lower() or "创新传承" in intent or "传承增强" in intent or "智能传承" in intent or "涌现洞察" in intent or "跨领域关联" in intent or "领域演进" in intent:
        print(f"[智能全场景进化环知识主动涌现发现与智能传承递归增强引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_knowledge_emergence_inheritance_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 检测功能关键词
        if "涌现发现" in intent or "发现" in intent or "discover" in intent.lower():
            cmd_args = ["--discover"]
        elif "传承链" in intent or "传承" in intent or "inherit" in intent.lower():
            # 提取目标轮次
            target_keywords = [w for w in sys.argv[1:] if w.startswith("r") and w[1:].isdigit()]
            if target_keywords:
                cmd_args = ["--inherit", int(target_keywords[0][1:])]
            else:
                cmd_args = ["--inherit"]
        elif "递归增强" in intent or "recursive" in intent.lower():
            cmd_args = ["--recursive"]
        elif "驾驶舱" in intent or "cockpit" in intent.lower():
            cmd_args = ["--cockpit-data"]
        # 过滤掉意图关键词
        filter_words = ["知识涌现", "涌现发现", "emergence", "创新传承", "传承增强", "智能传承", "涌现洞察", "跨领域关联", "领域演进", "发现", "discover", "传承链", "inherit", "递归增强", "recursive", "驾驶舱", "cockpit"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环知识推理-涌现发现深度集成引擎 (Round 522)
    # 在 round 521 知识涌现发现引擎和 round 447 知识推理引擎基础上，将两者深度集成
    # 实现「知识推理→涌现发现→知识传承→持续进化」的完整自主闭环
    elif "知识推理涌现" in intent or "推理驱动发现" in intent or "涌现推理集成" in intent or "reasoning emergence" in intent.lower() or "reasoning driven" in intent.lower():
        print(f"[智能全场景进化环知识推理-涌现发现深度集成引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_knowledge_reasoning_emergence_integration_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 检测功能关键词
        if "执行闭环" in intent or "run" in intent.lower() or "闭环" in intent:
            cmd_args = ["--run"]
        elif "驾驶舱" in intent or "cockpit" in intent.lower():
            cmd_args = ["--cockpit-data"]
        # 过滤掉意图关键词
        filter_words = ["知识推理涌现", "推理驱动发现", "涌现推理集成", "reasoning emergence", "reasoning driven", "执行闭环", "run", "闭环", "驾驶舱", "cockpit"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环进化效能深度分析-优化执行闭环增强引擎 (Round 524)
    # 在已有的效能分析引擎基础上，增强从效能分析→智能优化→自动执行→效果验证的完整闭环能力
    elif "效能深度分析" in intent or "分析优化闭环" in intent or "分析优化执行" in intent or "deep analysis" in intent.lower() or "analysis optimization" in intent.lower() or "analysis optimizer" in intent.lower() or "效能分析优化" in intent or "进化效能" in intent and "优化" in intent:
        print(f"[智能全场景进化环进化效能深度分析-优化执行闭环增强引擎 v1.0.0] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_effectiveness_deep_analysis_optimizer_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 检测功能关键词
        if "收集数据" in intent or "collect" in intent.lower():
            cmd_args = ["--collect"]
        elif "深度分析" in intent or "analyze" in intent.lower() or "分析" in intent:
            cmd_args = ["--analyze"]
        elif "生成建议" in intent or "proposal" in intent.lower() or "优化建议" in intent:
            cmd_args = ["--generate-proposals"]
        elif "执行优化" in intent or "execute" in intent.lower():
            cmd_args = ["--execute"]
        elif "自动执行" in intent or "auto execute" in intent.lower():
            cmd_args = ["--auto-execute"]
        elif "验证" in intent or "verify" in intent.lower():
            cmd_args = ["--verify"]
        elif "完整闭环" in intent or "closed loop" in intent.lower() or "full loop" in intent.lower():
            cmd_args = ["--closed-loop"]
        elif "驾驶舱" in intent or "cockpit" in intent.lower():
            cmd_args = ["--cockpit-data"]
        # 过滤掉意图关键词
        filter_words = ["效能深度分析", "分析优化闭环", "分析优化执行", "deep analysis", "analysis optimization", "analysis optimizer", "效能分析优化", "进化效能", "收集数据", "collect", "深度分析", "analyze", "生成建议", "proposal", "优化建议", "执行优化", "execute", "自动执行", "auto execute", "验证", "verify", "完整闭环", "closed loop", "full loop", "驾驶舱", "cockpit"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环效能实时数据推送与驾驶舱智能预警深度集成引擎 (Round 482)
    elif "实时推送" in intent or "智能预警" in intent or "自动刷新" in intent or "效能推送" in intent or "预警阈值" in intent or "realtime push" in intent.lower() or "smart warning" in intent.lower() or "auto refresh" in intent.lower() or "效能预警" in intent:
        print(f"[智能全场景进化环效能实时数据推送与驾驶舱智能预警深度集成引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_realtime_performance_push_cockpit_integration_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 过滤掉意图关键词
        filter_words = ["实时推送", "智能预警", "自动刷新", "效能推送", "预警阈值", "realtime push", "smart warning", "auto refresh", "效能预警"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环主动诊断与优化建议引擎 (Round 483/484)
    # Round 484 增强：支持自动修复功能
    elif "主动诊断" in intent or "诊断引擎" in intent or "健康诊断" in intent or "优化建议" in intent or "智能诊断" in intent or "proactive diagnosis" in intent.lower() or "diagnosis engine" in intent.lower() or "health diagnosis" in intent.lower() or "auto diagnosis" in intent.lower() or "自动修复" in intent or "auto fix" in intent.lower() or "诊断修复" in intent or "自动修复" in intent:
        print(f"[智能全场景进化环主动诊断与优化建议引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_proactive_diagnosis_optimizer_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 检测是否需要执行自动修复
        if "自动修复" in intent or "auto fix" in intent.lower() or "诊断修复" in intent:
            # 检查是否模拟模式
            if "模拟" in intent or "dry" in intent.lower():
                cmd_args = ["--auto-fix", "--dry-run"]
            else:
                cmd_args = ["--auto-fix"]
        elif "验证修复" in intent or "verify fix" in intent.lower():
            cmd_args = ["--verify-fix"]
        # 过滤掉意图关键词
        filter_words = ["主动诊断", "诊断引擎", "健康诊断", "优化建议", "智能诊断", "proactive diagnosis", "diagnosis engine", "health diagnosis", "auto diagnosis", "自动修复", "auto fix", "诊断修复", "验证修复", "verify fix", "模拟"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环预防性维护增强引擎 (Round 485)
    # 在主动诊断与自动修复引擎基础上，增强预防性维护能力
    elif "预防性维护" in intent or "预防维护" in intent or "主动预防" in intent or "preventive maintenance" in intent.lower() or "prevention" in intent.lower() or "预防" in intent:
        print(f"[智能全场景进化环预防性维护增强引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_preventive_maintenance_enhancement_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 检测是否需要执行检查
        if "检查" in intent or "check" in intent.lower():
            cmd_args = ["--check"]
        elif "趋势" in intent or "trend" in intent.lower():
            cmd_args = ["--trend"]
        elif "驾驶舱" in intent or "cockpit" in intent.lower():
            cmd_args = ["--cockpit-data"]
        # 检测模拟模式
        if "模拟" in intent or "dry" in intent.lower():
            if "--check" in cmd_args:
                cmd_args.append("--dry-run")
        # 过滤掉意图关键词
        filter_words = ["预防性维护", "预防维护", "主动预防", "preventive maintenance", "prevention", "预防", "检查", "check", "趋势", "trend", "驾驶舱", "cockpit", "模拟"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能全场景进化环预防-诊断-修复完整闭环引擎 (Round 486)
    # 将预防性维护引擎与自动诊断/修复引擎深度集成，形成「预测→诊断→修复→验证」完整闭环
    elif "预防诊断修复" in intent or "预防-诊断" in intent or "预防诊断" in intent or "完整闭环" in intent or "预防→诊断→修复" in intent or "prevention diagnosis repair" in intent.lower() or "prevention loop" in intent.lower() or "closed loop" in intent.lower() or "闭环" in intent:
        print(f"[智能全场景进化环预防-诊断-修复完整闭环引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_prevention_diagnosis_repair_closed_loop_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--status"]
        # 检测是否需要运行完整闭环
        if "运行" in intent or "执行" in intent or "run" in intent.lower():
            cmd_args = ["--run"]
        # 检测模拟模式
        if "模拟" in intent or "dry" in intent.lower():
            if "--run" in cmd_args:
                cmd_args.append("--dry-run")
        # 检测驾驶舱数据
        if "驾驶舱" in intent or "cockpit" in intent.lower():
            cmd_args = ["--cockpit-data"]
        # 过滤掉意图关键词
        filter_words = ["预防诊断修复", "预防-诊断", "预防诊断", "完整闭环", "预防→诊断→修复", "prevention diagnosis repair", "prevention loop", "closed loop", "闭环", "运行", "执行", "run", "模拟", "驾驶舱", "cockpit"]
        filtered_args = [arg for arg in cmd_args if not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["--status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)

    # 智能创意生成与评估引擎
    elif "创意生成" in intent or "智能创意" in intent or "创新想法" in intent or "新组合" in intent or "创意建议" in intent or "creative generation" in intent.lower() or "creative" in intent.lower() or "创意" in intent:
        print(f"[智能创意生成与评估引擎] 正在分析创意机会...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "creative_generation_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["status"]
        # 过滤掉意图关键词
        filter_words = ["创意生成", "智能创意", "创新想法", "新组合", "创意建议", "creative generation", "creative", "创意"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words and not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能创新实现增强引擎 (Round 285)
    elif "创新实现" in intent or "增强创新" in intent or "实现创新" in intent or "创新增强" in intent or "innovation enhancement" in intent.lower() or "enhance innovation" in intent.lower() or "实现创新能力" in intent:
        print(f"[智能创新实现增强引擎] 正在增强创新能力...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "innovation_enhancement_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["status"]
        # 过滤掉意图关键词
        filter_words = ["创新实现", "增强创新", "实现创新", "创新增强", "innovation enhancement", "enhance innovation", "实现创新能力"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words and not any(w in arg for w in filter_words)]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能创意工作流自动生成与执行引擎 (Round 263)
    elif "创意工作流" in intent or "自动生成工作流" in intent or "生成工作流" in intent or "creative workflow" in intent.lower() or "工作流生成" in intent:
        print(f"[智能创意工作流自动生成与执行引擎] 正在生成工作流...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "creative_workflow_generator.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 过滤掉意图关键词
        filter_words = ["创意工作流", "自动生成工作流", "生成工作流", "creative workflow", "工作流生成"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words and not any(w in arg for w in filter_words)]
        # 默认执行或预览
        if "--execute" in filtered_args or "-e" in filtered_args:
            filtered_args = [a for a in filtered_args if a not in ["--execute", "-e"]]
            if filtered_args:
                result = subprocess.run([sys.executable, script_path, " ".join(filtered_args), "--execute"], cwd=PROJECT, capture_output=True, text=True)
            else:
                result = subprocess.run([sys.executable, script_path, "--execute"], cwd=PROJECT, capture_output=True, text=True)
        else:
            if filtered_args:
                result = subprocess.run([sys.executable, script_path, " ".join(filtered_args)], cwd=PROJECT, capture_output=True, text=True)
            else:
                # 交互模式
                result = subprocess.run([sys.executable, script_path, "--interactive"], cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能主动价值发现与即时服务引擎 (Round 264) - 主动分析用户情境，识别用户可能需要但尚未提出的高价值服务
    elif "主动发现" in intent or "价值发现" in intent or "即时服务" in intent or "主动价值" in intent or "proactive value" in intent.lower() or "value discovery" in intent.lower() or "主动服务" in intent or "discover opportunity" in intent.lower():
        print(f"[智能主动价值发现与即时服务引擎] 正在分析情境并发现价值机会...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "proactive_value_discovery_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["--discover"]
        # 判断动作
        action = "status"
        if "discover" in intent.lower() or "发现" in intent:
            action = "discover"
        elif "analyze" in intent.lower() or "分析" in intent:
            action = "analyze"
        elif "effectiveness" in intent.lower() or "效果" in intent:
            action = "effectiveness"
        # 过滤掉意图关键词
        filter_words = ["主动发现", "价值发现", "即时服务", "主动价值", "proactive value", "value discovery", "主动服务", "discover opportunity", "分析", "发现", "效果"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words and not any(w in arg for w in filter_words)]
        # 添加动作参数
        if action not in filtered_args:
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能长期记忆与主动规划引擎
    elif "长期记忆" in intent or "目标跟踪" in intent or "主动规划" in intent or "我的目标" in intent or "待办" in intent or "long term memory" in intent.lower() or "目标" in intent or "待办" in intent:
        print(f"[智能长期记忆与主动规划引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "long_term_memory_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["status"]
        # 过滤掉意图关键词
        filter_words = ["长期记忆", "目标跟踪", "主动规划", "我的目标", "待办", "long term memory", "目标", "记忆"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words and not any(w in arg for w in filter_words)]
        if not filtered_args:
            # 默认显示状态
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能数据洞察与可视化引擎
    elif "数据洞察" in intent or "data insight" in intent.lower() or "洞察报告" in intent or "可视化报告" in intent or "数据统计" in intent:
        print(f"[智能数据洞察与可视化引擎] 正在分析数据并生成洞察报告...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "data_insight_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["status"]
        # 过滤掉意图关键词
        filter_words = ["数据洞察", "数据统计", "洞察报告", "可视化报告", "data insight"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words and not any(w in arg for w in filter_words)]
        if not filtered_args:
            # 默认显示状态
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能会议助手引擎
    elif "会议" in intent or "meeting" in intent.lower() or "会议纪要" in intent or "会议提醒" in intent:
        print(f"[智能会议助手引擎] 正在处理会议相关请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "meeting_assistant_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["status"]
        # 过滤掉意图关键词
        filter_words = ["会议", "meeting", "会议纪要", "会议提醒", "会议助手"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words and not any(w in arg for w in filter_words)]
        if not filtered_args:
            # 默认显示状态
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能任务规划与执行编排引擎
    elif "任务规划" in intent or "执行编排" in intent or "任务编排" in intent or "task planning" in intent.lower() or "规划任务" in intent:
        print(f"[智能任务规划与执行编排引擎] 正在处理任务规划请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "task_planning_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["status"]
        # 过滤掉意图关键词
        filter_words = ["任务规划", "执行编排", "任务编排", "task planning", "规划任务"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words and not any(w in arg for w in filter_words)]
        if not filtered_args:
            # 默认显示状态
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能自动化脚本生成引擎
    elif "生成脚本" in intent or "脚本生成" in intent or "创建脚本" in intent or "自动生成脚本" in intent or "script generation" in intent.lower() or "生成代码" in intent or "帮我写脚本" in intent:
        print(f"[智能自动化脚本生成引擎] 正在处理脚本生成请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "script_generation_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["status"]
        # 过滤掉意图关键词
        filter_words = ["生成脚本", "脚本生成", "创建脚本", "自动生成脚本", "script generation", "生成代码", "帮我写脚本"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words and not any(w in arg for w in filter_words)]
        if not filtered_args:
            # 默认显示状态
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能统一推荐引擎 - 执行指定推荐
    elif "执行推荐" in intent or "execute recommend" in intent.lower():
        print(f"[智能统一推荐引擎] 正在执行推荐...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "unified_recommender.py")
        # 尝试从参数中获取推荐ID
        rec_id = None
        for arg in sys.argv[1:]:
            if arg.startswith("rec_") or arg.startswith("scene_") or arg.startswith("workflow_") or arg.startswith("action_"):
                rec_id = arg
                break
        cmd_args = ["execute"]
        if rec_id:
            cmd_args.extend(["--rec-id", rec_id])
        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能统一推荐引擎
    elif "统一推荐" in intent or "综合推荐" in intent or "智能推荐" in intent or "unified recommend" in intent.lower() or "all recommend" in intent.lower() or "推荐" in intent and "场景" not in intent and "工作流" not in intent and "执行" not in intent:
        print(f"[智能统一推荐引擎] 正在整合多引擎推荐能力...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "unified_recommender.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["recommend"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["统一推荐", "综合推荐", "智能推荐", "unified recommend", "all recommend", "推荐"]]
        if not filtered_args:
            filtered_args = ["recommend"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能任务理解与自动规划引擎
    elif "任务规划" in intent or "规划任务" in intent or "自动规划" in intent or "分解任务" in intent or "task plan" in intent.lower() or "智能任务" in intent or "帮我做" in intent or "帮我执行" in intent or "描述任务" in intent:
        print(f"[智能任务理解与自动规划引擎] 正在解析任务...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "task_planner.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["actions"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["任务规划", "规划任务", "自动规划", "分解任务", "task plan", "智能任务", "帮我做", "帮我执行", "描述任务"]]
        if not filtered_args:
            # 尝试从整个命令行提取任务描述
            task_desc = " ".join(sys.argv[1:])
            for kw in ["任务规划", "规划任务", "自动规划", "分解任务", "task plan", "智能任务", "帮我做", "帮我执行", "描述任务"]:
                task_desc = task_desc.replace(kw, "").strip()
            if task_desc:
                filtered_args = ["plan", "--input", task_desc]
            else:
                filtered_args = ["actions"]
        # 检查是否需要执行
        if "--execute" in intent or "执行" in intent or "执行计划" in intent:
            if "plan" not in filtered_args:
                filtered_args = ["execute"] + filtered_args
            else:
                # 在 plan 后面加 --execute
                idx = filtered_args.index("plan") if "plan" in filtered_args else -1
                if idx >= 0 and idx + 1 < len(filtered_args) and not filtered_args[idx + 1].startswith("--"):
                    filtered_args.insert(idx + 2, "--execute")
                else:
                    filtered_args.append("--execute")
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能学习与适应引擎
    elif "学习" in intent or "适应" in intent or "个性化" in intent or "learning" in intent.lower() or "adaptive" in intent.lower() or "personalize" in intent.lower() or "习惯" in intent or "分析习惯" in intent:
        print(f"[智能学习与适应引擎] 正在处理学习与适应请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "adaptive_learning_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["status"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["学习", "适应", "个性化", "learning", "adaptive", "personalize", "习惯", "分析习惯"]]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能主动通知引擎
    elif "通知" in intent or "提醒" in intent or "主动建议" in intent or "notification" in intent.lower() or "reminder" in intent.lower() or "智能提醒" in intent or "主动通知" in intent:
        print(f"[智能主动通知引擎] 正在处理通知请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "proactive_notification_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["status"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["通知", "提醒", "主动建议", "notification", "reminder", "智能提醒", "主动通知"]]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能记忆引擎
    elif "记忆" in intent or "记住" in intent or "存储" in intent or "memory" in intent.lower() or "记住" in intent or "存储信息" in intent or "记住偏好" in intent:
        print(f"[智能记忆引擎] 正在处理记忆请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "memory_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["stats"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["记忆", "记住", "存储", "memory", "存储信息", "记住偏好"]]
        if not filtered_args:
            filtered_args = ["stats"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能问题诊断与自愈引擎
    elif "诊断" in intent or "自愈" in intent or "问题检测" in intent or "diagnose" in intent.lower() or "heal" in intent.lower() or "self-heal" in intent.lower() or "健康检测" in intent:
        print(f"[智能问题诊断与自愈引擎] 正在处理诊断请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "self_healing_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["diagnose", "--check-all"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["诊断", "自愈", "问题检测", "健康检测", "diagnose", "heal", "self-heal"]]
        if not filtered_args:
            filtered_args = ["diagnose", "--check-all"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能错误模式学习与主动防御引擎
    elif "错误模式" in intent or "主动防御" in intent or "防御" in intent or "error_pattern" in intent.lower() or "defense" in intent.lower() or "错误学习" in intent or "模式学习" in intent:
        print(f"[智能错误模式学习与主动防御引擎] 正在分析错误模式并制定防御策略...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "error_pattern_learning_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["status"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["错误模式", "主动防御", "防御", "error_pattern", "defense", "错误学习", "模式学习"]]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能操作安全卫士引擎
    elif "安全" in intent or "安全卫士" in intent or "操作安全" in intent or "危险操作" in intent or "safety" in intent.lower() or "guardian" in intent.lower():
        print(f"[智能操作安全卫士引擎] 正在分析操作安全性...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "safety_guardian.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["analyze", " ".join(sys.argv[1:])]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["安全", "安全卫士", "操作安全", "危险操作", "safety", "guardian"]]
        if not filtered_args:
            filtered_args = ["analyze", " ".join(sys.argv[1:])]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 主动预测与预防引擎 + 自动闭环
    elif "预测与预防" in intent or "主动预防" in intent or "预防" in intent or "predictive" in intent.lower() or "prevention" in intent.lower() or "预警" in intent or "发送预警" in intent or "预警通知" in intent or "自动触发" in intent or "自动闭环" in intent or "自动修复" in intent or "auto" in intent.lower():
        # 判断是否是自动触发/闭环
        is_auto = "自动触发" in intent or "自动闭环" in intent or "自动修复" in intent or "auto" in intent.lower()

        if is_auto:
            print(f"[自动闭环引擎] 正在执行预测→决策→执行→通知的完整自动化服务...", file=sys.stderr)
        else:
            print(f"[主动预测与预防引擎] 正在分析系统状态并预测潜在问题...", file=sys.stderr)

        script_path = os.path.join(SCRIPTS, "predictive_prevention_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["预测与预防", "主动预防", "预防", "predictive", "prevention", "预警", "发送预警", "预警通知", "自动触发", "自动闭环", "自动修复", "auto"]]

        # 根据意图类型选择命令
        if is_auto:
            # 自动触发使用 auto 命令
            if not filtered_args:
                filtered_args = ["auto"]
            else:
                filtered_args = ["auto"] + filtered_args
        elif "发送预警" in intent or "预警通知" in intent:
            filtered_args = ["notify"] + filtered_args
        elif not filtered_args:
            filtered_args = ["report"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能系统主动运维引擎（round 160/161）- 增强自动执行能力
    elif "主动运维" in intent or "系统运维" in intent or "运维引擎" in intent or "资源优化" in intent or "自动清理" in intent or "内存优化" in intent or "proactive operations" in intent.lower() or "system operations" in intent.lower() or "资源监控" in intent or "运维" in intent or "自动优化" in intent or "一键优化" in intent or "执行优化" in intent or "auto optimize" in intent.lower():
        print(f"[智能系统主动运维引擎] 正在处理请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "proactive_operations_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["主动运维", "系统运维", "运维引擎", "资源优化", "自动清理", "内存优化", "proactive operations", "system operations", "资源监控", "运维", "自动优化", "一键优化", "执行优化", "auto optimize"]]
        if not filtered_args:
            # 如果没有额外参数，显示状态
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能系统健康保障闭环引擎（round 162）- 集成主动运维、自愈、预测预防
    elif "健康保障" in intent or "服务闭环" in intent or "系统保障" in intent or "保障状态" in intent or "health assurance" in intent.lower() or "health loop" in intent.lower() or "assurance" in intent.lower() or "保障" in intent:
        print(f"[智能系统健康保障闭环引擎] 正在处理请求...", file=sys.stderr)

        # 检查是否是守护进程相关请求
        if "守护进程" in intent or "daemon" in intent.lower() or "后台" in intent or "持续" in intent or "自动运行" in intent:
            # 启动健康保障守护进程
            script_path = os.path.join(SCRIPTS, "daemon_manager.py")
            cmd = ["start", "health_assurance"]
            if "停止" in intent or "关闭" in intent:
                cmd = ["stop", "health_assurance"]
            elif "状态" in intent or "查看" in intent or "status" in intent.lower():
                cmd = ["status", "health_assurance"]
            elif "列表" in intent or "list" in intent.lower():
                cmd = ["list"]
            elif "启用" in intent or "enable" in intent.lower():
                cmd = ["enable", "health_assurance"]
            elif "禁用" in intent or "disable" in intent.lower():
                cmd = ["disable", "health_assurance"]
            elif "单次" in intent or "一次" in intent or "run-once" in intent.lower():
                # 单次执行
                script_path = os.path.join(SCRIPTS, "health_assurance_daemon.py")
                cmd = ["--run-once"]
                result = subprocess.run([sys.executable, script_path] + cmd, cwd=PROJECT, capture_output=True, text=True)
                if result.stdout:
                    print(result.stdout)
                if result.returncode != 0 and result.stderr:
                    print(result.stderr, file=sys.stderr)
                sys.exit(0 if result.returncode == 0 else result.returncode)

            result = subprocess.run([sys.executable, script_path] + cmd, cwd=PROJECT, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            if result.returncode != 0 and result.stderr:
                print(result.stderr, file=sys.stderr)
            sys.exit(0 if result.returncode == 0 else result.returncode)

        # 正常健康保障闭环引擎调用
        script_path = os.path.join(SCRIPTS, "health_assurance_loop.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["健康保障", "服务闭环", "系统保障", "保障状态", "health assurance", "health loop", "assurance", "保障"]]
        if not filtered_args:
            # 如果没有额外参数，显示状态
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 跨模块状态共享总线
    elif "状态总线" in intent or "模块共享" in intent or "共享状态" in intent or "module_bus" in intent.lower() or "state bus" in intent.lower():
        print(f"[跨模块状态共享总线] 正在处理状态共享...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "module_bus.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["状态总线", "模块共享", "共享状态", "module_bus", "state bus"]]
        if not filtered_args:
            # 如果没有额外参数，显示状态
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能主动决策与行动引擎（round 146）- 放在决策编排中心之前以优先匹配
    elif "主动决策" in intent or "主动行动" in intent or "主动思考" in intent or "proactive action" in intent.lower() or "主动扫描" in intent or "主动识别" in intent or "主动推荐" in intent:
        print(f"[智能主动决策与行动引擎] 正在处理请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "proactive_decision_action_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["scan"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["主动决策", "主动行动", "主动思考", "proactive action", "主动扫描", "主动识别", "主动推荐"]]
        if not filtered_args:
            # 根据意图确定默认命令
            if "状态" in intent or "status" in intent.lower():
                filtered_args = ["status"]
            elif "分析" in intent or "analyze" in intent.lower():
                filtered_args = ["analyze"]
            elif "扫描" in intent or "scan" in intent.lower():
                filtered_args = ["scan"]
            elif "启用" in intent or "enable" in intent.lower():
                filtered_args = ["enable"]
            elif "禁用" in intent or "disable" in intent.lower():
                filtered_args = ["disable"]
            else:
                filtered_args = ["scan"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能实时操作指导引擎（round 169）
    elif "实时指导" in intent or "操作指导" in intent or "智能辅助" in intent or "realtime guidance" in intent.lower() or "操作观察" in intent or "实时监控操作" in intent:
        print(f"[智能实时操作指导引擎] 正在处理请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "realtime_guidance_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["analyze"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["实时指导", "操作指导", "智能辅助", "realtime guidance", "操作观察", "实时监控操作"]]
        if not filtered_args:
            # 根据意图确定默认命令
            if "状态" in intent or "status" in intent.lower():
                filtered_args = ["status"]
            elif "分析" in intent or "analyze" in intent.lower():
                filtered_args = ["analyze"]
            elif "开始监控" in intent or "启动监控" in intent or "start" in intent.lower():
                filtered_args = ["start"]
            elif "停止监控" in intent or "stop" in intent.lower():
                filtered_args = ["stop"]
            elif "建议" in intent or "suggestion" in intent.lower():
                filtered_args = ["suggestions"]
            elif "上下文" in intent or "context" in intent.lower():
                filtered_args = ["context"]
            elif "清除" in intent or "clear" in intent.lower():
                filtered_args = ["clear"]
            else:
                filtered_args = ["analyze"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能跨设备协同控制引擎（round 170）
    elif "跨设备" in intent or "设备协同" in intent or "设备控制" in intent or "cross device" in intent.lower() or "设备发现" in intent or "扫描设备" in intent or "设备列表" in intent or "发送到手机" in intent or "发送文件到" in intent or "远程控制" in intent or "远程执行" in intent or "通知同步" in intent:
        print(f"[智能跨设备协同控制引擎] 正在处理请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "cross_device_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["status"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["跨设备", "设备协同", "设备控制", "cross device", "设备发现", "扫描设备", "设备列表", "发送到手机", "发送文件到", "远程控制", "远程执行", "通知同步"]]
        if not filtered_args:
            # 根据意图确定默认命令
            if "状态" in intent or "status" in intent.lower():
                filtered_args = ["status"]
            elif "列表" in intent or "list" in intent.lower():
                filtered_args = ["list"]
            elif "扫描" in intent or "发现" in intent or "scan" in intent.lower() or "discover" in intent.lower():
                filtered_args = ["scan"]
            elif "发送" in intent or "send" in intent.lower() or "传输" in intent:
                filtered_args = ["help"]  # 需要额外参数
            elif "远程" in intent or "remote" in intent.lower():
                filtered_args = ["help"]  # 需要额外参数
            elif "同步" in intent or "sync" in intent.lower():
                filtered_args = ["sync"]
            else:
                filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能跨会话知识传承引擎（round 171）
    elif "知识传承" in intent or "传承知识" in intent or "跨会话" in intent or "会话接续" in intent or "知识摘要" in intent or "knowledge inheritance" in intent.lower() or "knowledge summary" in intent.lower() or "session summary" in intent.lower() or "知识概览" in intent:
        print(f"[智能跨会话知识传承引擎] 正在处理请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "knowledge_inheritance_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["summary"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["知识传承", "传承知识", "跨会话", "会话接续", "知识摘要", "knowledge inheritance", "knowledge summary", "session summary", "知识概览"]]
        if not filtered_args:
            # 根据意图确定默认命令
            if "状态" in intent or "status" in intent.lower() or "概览" in intent or "summary" in intent.lower():
                filtered_args = ["summary"]
            elif "列表" in intent or "list" in intent.lower():
                filtered_args = ["list"]
            elif "会话" in intent or "session" in intent.lower():
                filtered_args = ["sessions"]
            elif "决策" in intent or "decision" in intent.lower():
                filtered_args = ["decisions"]
            elif "进化" in intent or "evolution" in intent.lower():
                filtered_args = ["evolution"]
            elif "获取" in intent or "get" in intent.lower():
                filtered_args = ["help"]  # 需要会话ID参数
            else:
                filtered_args = ["summary"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能决策编排中心 + 基于预测的主动服务
    elif "决策" in intent or "编排" in intent or "协同" in intent or "最佳方案" in intent or "智能调度" in intent or "multi-engine" in intent.lower() or "decision" in intent.lower() or "orchestrate" in intent.lower() or "协调" in intent or "预测服务" in intent or "主动服务" in intent or "proactive" in intent.lower() or "predictive-service" in intent.lower():
        # 判断是否是主动预测服务
        is_proactive = "预测服务" in intent or "主动服务" in intent or "proactive" in intent.lower() or "predictive-service" in intent.lower()

        if is_proactive:
            print(f"[基于预测的主动服务] 正在分析系统状态并生成主动服务...", file=sys.stderr)
        else:
            print(f"[智能决策编排中心] 正在分析并调度引擎...", file=sys.stderr)

        script_path = os.path.join(SCRIPTS, "decision_orchestrator.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["决策", "编排", "协同", "最佳方案", "智能调度", "multi-engine", "decision", "orchestrate", "协调", "预测服务", "主动服务", "proactive", "predictive-service"]]

        if is_proactive:
            # 主动预测服务使用 predictive-service 命令
            if not filtered_args:
                filtered_args = ["proactive"]
            else:
                filtered_args = ["proactive"] + filtered_args
        else:
            if not filtered_args:
                # 如果没有额外参数，显示状态
                filtered_args = ["status"]

        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能服务闭环引擎 - 整合预测→决策→执行→反馈的完整自动化服务
    elif "智能服务闭环" in intent or "服务闭环" in intent or "智能闭环" in intent or "service loop" in intent.lower() or "智能主动闭环" in intent or "跨引擎闭环" in intent:
        print(f"[智能服务闭环引擎] 正在运行预测→决策→执行→反馈闭环...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "intelligent_service_loop.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断是否自动执行
        auto_execute = "自动" in intent or "auto" in intent.lower()
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["智能服务闭环", "服务闭环", "智能闭环", "service loop", "智能主动闭环", "跨引擎闭环"]]
        if not filtered_args:
            filtered_args = ["run"]
            if auto_execute:
                filtered_args.append("--auto")
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 主动服务触发引擎 - 条件触发的自动服务
    elif "触发器" in intent or "自动服务" in intent or "条件触发" in intent or "proactive trigger" in intent.lower() or "服务触发" in intent or "trigger" in intent.lower():
        print(f"[主动服务触发引擎] 正在处理触发请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "proactive_service_trigger.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "启动" in intent or "start" in intent.lower() or "开启" in intent:
            action = "start"
        elif "停止" in intent or "stop" in intent.lower() or "关闭" in intent:
            action = "stop"
        elif "触发" in intent or "手动触发" in intent:
            action = "trigger"
        elif "列表" in intent or "list" in intent.lower():
            action = "list"
        # 过滤掉意图关键词
        filter_words = ["触发器", "自动服务", "条件触发", "proactive trigger", "服务触发", "trigger", "启动", "start", "开启", "停止", "stop", "关闭", "手动触发", "触发", "列表", "list"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        if action not in ["status", "list"]:
            filtered_args.insert(0, action)
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能主动服务编排引擎（round 166）- 持续监控用户行为，主动发现并推荐服务
    elif "主动服务编排" in intent or "服务编排" in intent or "proactive orchestrator" in intent.lower() or "service orchestration" in intent.lower() or "编排引擎" in intent:
        print(f"[智能主动服务编排引擎] 正在分析并提供服务...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "proactive_service_orchestrator.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = None
        if "推荐" in intent or "recommend" in intent.lower() or "发现" in intent:
            action = "recommendations"
        elif "执行" in intent or "execute" in intent.lower():
            action = "execute"
        elif "状态" in intent or "status" in intent.lower():
            action = "status"
        elif "历史" in intent or "history" in intent.lower():
            action = "history"
        elif "启用" in intent or "enable" in intent.lower():
            action = "enable"
        elif "禁用" in intent or "disable" in intent.lower():
            action = "disable"
        # 过滤掉意图关键词
        filter_words = ["主动服务编排", "服务编排", "proactive orchestrator", "service orchestration", "编排引擎", "推荐", "recommend", "发现", "执行", "execute", "状态", "status", "历史", "history", "启用", "enable", "禁用", "disable"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        if action and action not in filtered_args:
            filtered_args.insert(0, action)
        if not filtered_args:
            # 默认查看推荐
            filtered_args = ["recommendations"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能主动服务增强引擎（round 193）- 在用户发出指令之前预测需求并预准备
    elif "主动增强" in intent or "服务增强" in intent or "预见服务" in intent or "主动预测" in intent or "proactive enhance" in intent.lower() or "service enhancer" in intent.lower() or "predictive service" in intent.lower():
        print(f"[智能主动服务增强引擎] 正在预测用户需求并准备服务...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "proactive_service_enhancer.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = None
        if "状态" in intent or "status" in intent.lower() or "查看状态" in intent:
            action = "status"
        elif "预测" in intent or "predict" in intent.lower():
            action = "predict"
        elif "推荐" in intent or "recommend" in intent.lower():
            action = "recommend"
        elif "预加载" in intent or "preload" in intent.lower():
            action = "preload"
        elif "启用" in intent or "enable" in intent.lower():
            action = "enable"
        elif "禁用" in intent or "disable" in intent.lower():
            action = "disable"
        # 过滤掉意图关键词
        filter_words = ["主动增强", "服务增强", "预见服务", "主动预测", "proactive enhance", "service enhancer", "predictive service", "预测", "predict", "推荐", "recommend", "预加载", "preload", "状态", "status", "启用", "enable", "禁用", "disable"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        if action and action not in filtered_args:
            filtered_args.insert(0, action)
        if not filtered_args:
            # 默认查看状态
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能系统自检与健康报告引擎（round 194）- 自动进行全面健康检查、生成详细状态报告、提供健康建议
    elif "系统自检" in intent or "健康报告" in intent or "健康诊断" in intent or "自检" in intent or "系统诊断" in intent or "system diagnose" in intent.lower() or "health report" in intent.lower() or "self check" in intent.lower() or "self diagnosis" in intent.lower() or "system self" in intent.lower():
        print(f"[智能系统自检与健康报告引擎] 正在进行全面健康检查...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "system_self_diagnosis_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = None
        if "完整" in intent or "full" in intent.lower() or "全面" in intent:
            action = "--full"
        elif "快速" in intent or "quick" in intent.lower() or "状态" in intent:
            action = "--quick"
        elif "报告" in intent or "report" in intent.lower():
            action = "--report"
        # 过滤掉意图关键词
        filter_words = ["系统自检", "健康报告", "健康诊断", "自检", "系统诊断", "system diagnose", "health report", "self check", "self diagnosis", "system self", "完整", "full", "全面", "快速", "quick", "状态", "报告", "report"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        if action and action not in filtered_args:
            filtered_args.insert(0, action)
        if not filtered_args:
            # 默认运行完整检查
            filtered_args = ["--full"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景跨模块深度诊断与自愈统一引擎（round 319）- 构建统一的系统健康诊断与自愈中枢
    elif "统一诊断" in intent or "跨模块诊断" in intent or "深度诊断" in intent or "诊疗" in intent or "unified diagnosis" in intent.lower() or "cross module diagnosis" in intent.lower() or "deep diagnosis" in intent.lower() or "诊疗" in intent.lower() or "统一健康" in intent or "跨模块健康" in intent or "健康仪表盘" in intent:
        print(f"[跨模块深度诊断与自愈统一引擎] 正在执行统一诊断...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "unified_diagnosis_healing_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = None
        if "快速" in intent or "quick" in intent.lower():
            action = "--level quick"
        elif "深度" in intent or "deep" in intent.lower():
            action = "--level deep"
        elif "仪表盘" in intent or "dashboard" in intent.lower() or "状态" in intent:
            action = "--dashboard"
        elif "历史" in intent or "history" in intent.lower():
            action = "--history"
        # 判断是否自动修复
        auto_heal = False
        if "自动修复" in intent or "auto heal" in intent.lower() or "自愈" in intent:
            auto_heal = True
            action = (action or "") + " --auto-heal"
        # 过滤掉意图关键词
        filter_words = ["统一诊断", "跨模块诊断", "深度诊断", "诊疗", "unified diagnosis", "cross module diagnosis", "deep diagnosis", "健康仪表盘", "dashboard", "快速", "quick", "深度", "deep", "历史", "history", "自动修复", "auto heal", "自愈", "状态"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        if action:
            action_parts = action.split()
            for part in action_parts:
                if part and part not in filtered_args:
                    filtered_args.insert(0, part)
        if not filtered_args:
            # 默认运行标准诊断
            filtered_args = ["--level", "standard"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环自主意识觉醒与执行闭环引擎（round 321）- 让系统具备真正的自主意识
    elif "自主意识" in intent or "自主执行" in intent or "意识觉醒" in intent or "执行闭环" in intent or "autonomous consciousness" in intent.lower() or "consciousness execution" in intent.lower() or "想做事" in intent or "想做" in intent or "我要做" in intent or "自主驱动" in intent or "auto drive" in intent.lower():
        print(f"[智能全场景进化环自主意识觉醒与执行闭环引擎] 正在分析系统自主意识状态并驱动执行...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_autonomous_consciousness_execution_engine.py")
        # 判断动作
        action = None
        if "状态" in intent or "status" in intent.lower():
            action = "--status"
        elif "扫描" in intent or "scan" in intent.lower() or "分析" in intent:
            action = "--consciousness-scan"
        elif "意图" in intent or "intent" in intent.lower() or "生成" in intent:
            action = "--generate-intent"
        elif "执行" in intent or "execute" in intent.lower() or "驱动" in intent:
            action = "--auto-execute"
        elif "验证" in intent or "verify" in intent.lower() or "验证结果" in intent:
            action = "--verify-result"
        elif "仪表盘" in intent or "dashboard" in intent.lower():
            action = "--dashboard"
        # 默认使用摘要
        if not action:
            action = "--summary"
        result = subprocess.run([sys.executable, script_path, action], cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环自主意识与决策深度集成引擎（round 322）
    # 将自主意识引擎(round 321)与进化决策引擎深度集成，形成完整的「意识→决策→执行→验证→意识更新」闭环
    elif "深度集成" in intent or "意识决策" in intent or "consciousness decision" in intent.lower() or "意识驱动" in intent or "完整闭环" in intent or "full loop" in intent.lower() or "融合引擎" in intent or "fusion" in intent.lower():
        print(f"[智能全场景进化环自主意识与决策深度集成引擎] 正在执行意识-决策融合闭环...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_consciousness_decision_fusion.py")
        # 判断动作
        action = None
        if "状态" in intent or "status" in intent.lower():
            action = "--status"
        elif "仪表盘" in intent or "dashboard" in intent.lower():
            action = "--dashboard"
        elif "完整闭环" in intent or "full loop" in intent.lower() or "执行闭环" in intent:
            action = "--full-loop"
        elif "意识驱动决策" in intent or "consciousness decision" in intent.lower():
            action = "--consciousness-driven-decision"
        elif "决策执行" in intent or "decision execution" in intent.lower():
            action = "--decision-to-execution"
        elif "执行反馈" in intent or "反馈意识" in intent.lower() or "execution consciousness" in intent.lower():
            action = "--execution-to-consciousness"
        # 默认使用摘要
        if not action:
            action = "--summary"
        result = subprocess.run([sys.executable, script_path, action], cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能场景自适应执行引擎（round 176）- 基于实时上下文自动执行/切换场景计划
    elif "场景自适应" in intent or "自适应场景" in intent or "自动场景" in intent or "scene adaptive" in intent.lower() or "auto scene" in intent.lower() or "场景自动" in intent or "自适应执行" in intent or "auto-switch" in intent.lower():
        print(f"[智能场景自适应执行引擎] 正在分析上下文并执行场景...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "scene_adaptive_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = None
        if "状态" in intent or "status" in intent.lower() or "查看状态" in intent:
            action = "status"
        elif "启动" in intent or "start" in intent.lower() or "开启" in intent:
            action = "start"
        elif "停止" in intent or "stop" in intent.lower() or "关闭" in intent:
            action = "stop"
        elif "执行" in intent or "execute" in intent.lower() or "运行" in intent:
            action = "execute"
        elif "启用" in intent or "enable" in intent.lower():
            action = "enable"
        elif "禁用" in intent or "disable" in intent.lower():
            action = "disable"
        elif "自动开" in intent or "auto-on" in intent.lower() or "自动启用" in intent:
            action = "auto-on"
        elif "自动关" in intent or "auto-off" in intent.lower() or "自动禁用" in intent:
            action = "auto-off"
        elif "上下文" in intent or "context" in intent.lower():
            action = "context"
        elif "历史" in intent or "history" in intent.lower():
            action = "history"
        elif "日志" in intent or "log" in intent.lower():
            action = "log"
        elif "间隔" in intent or "interval" in intent.lower():
            action = "interval"
        # 过滤掉意图关键词
        filter_words = ["场景自适应", "自适应场景", "自动场景", "scene adaptive", "auto scene", "场景自动", "自适应执行", "auto-switch", "状态", "status", "启动", "start", "开启", "停止", "stop", "关闭", "执行", "execute", "运行", "启用", "enable", "禁用", "disable", "自动开", "auto-on", "自动启用", "自动关", "auto-off", "自动禁用", "上下文", "context", "历史", "history", "日志", "log", "间隔", "interval"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        if action and action not in filtered_args:
            filtered_args.insert(0, action)
        if not filtered_args:
            # 默认查看状态
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能自动化执行闭环引擎（round 157）- 自动发现并执行重复任务
    elif "自动化执行" in intent or "自动执行" in intent or "执行闭环" in intent or "automation execution" in intent.lower() or "auto execute" in intent.lower() or "自动化闭环" in intent or "auto-task" in intent.lower() or "自动化任务" in intent:
        print(f"[智能自动化执行闭环引擎] 正在分析并执行自动化任务...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "automation_execution_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = None
        if "分析" in intent or "analyze" in intent.lower():
            action = "analyze"
        elif "执行" in intent or "execute" in intent.lower() or "run" in intent.lower():
            action = "execute"
        elif "启用" in intent or "enable" in intent.lower() or "开启" in intent:
            action = "enable"
        elif "禁用" in intent or "disable" in intent.lower() or "关闭" in intent:
            action = "disable"
        elif "统计" in intent or "stats" in intent.lower():
            action = "stats"
        elif "报告" in intent or "report" in intent.lower():
            action = "report"
        # 过滤掉意图关键词
        filter_words = ["自动化执行", "自动执行", "执行闭环", "automation execution", "auto execute", "自动化闭环", "auto-task", "自动化任务", "分析", "analyze", "执行", "execute", "run", "启用", "enable", "开启", "禁用", "disable", "关闭", "统计", "stats", "报告", "report"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        if action and action not in filtered_args:
            filtered_args.insert(0, action)
        if not filtered_args:
            # 默认分析自动化机会
            filtered_args = ["analyze"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全自动化服务引擎（round 158）- 基于时间/事件/行为的自动触发执行
    elif "全自动化" in intent or "自动服务" in intent or "full auto" in intent.lower() or "fullauto" in intent.lower() or "auto service" in intent.lower() or "自动化守护" in intent or "auto guardian" in intent.lower() or "守护进程" in intent or "daemon" in intent.lower():
        print(f"[智能全自动化服务引擎] 正在处理自动化服务...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "full_auto_service_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = None
        if "状态" in intent or "status" in intent.lower():
            action = "status"
        elif "启动" in intent or "start" in intent.lower() or "开始" in intent:
            action = "start"
        elif "停止" in intent or "stop" in intent.lower() or "关闭" in intent:
            action = "stop"
        elif "检查" in intent or "check" in intent.lower():
            action = "check"
        elif "列表" in intent or "list" in intent.lower() or "任务列表" in intent:
            action = "list-tasks"
        elif "添加" in intent or "add" in intent.lower():
            action = "add-default-tasks"
        elif "启用" in intent or "enable" in intent.lower():
            action = "enable"
        elif "禁用" in intent or "disable" in intent.lower():
            action = "disable"
        # 过滤掉意图关键词
        filter_words = ["全自动化", "自动服务", "full auto", "fullauto", "auto service", "自动化守护", "auto guardian", "守护进程", "daemon", "状态", "status", "启动", "start", "开始", "停止", "stop", "关闭", "检查", "check", "列表", "list", "任务列表", "添加", "add", "启用", "enable", "禁用", "disable"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        if action and action not in filtered_args:
            filtered_args.insert(0, action)
        if not filtered_args:
            # 默认显示状态
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能情境感知引擎
    elif "情境感知" in intent or "环境感知" in intent or "当前状态" in intent or "主动推荐" in intent or "context awareness" in intent.lower() or "sense environment" in intent.lower() or "perceive" in intent.lower():
        print(f"[智能情境感知引擎] 正在感知当前环境...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "context_awareness_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["情境感知", "环境感知", "当前状态", "主动推荐", "context awareness", "sense environment", "perceive"]]
        if not filtered_args:
            # 如果没有额外参数，显示状态
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能系统健康监控与自适应优化引擎
    elif "系统监控" in intent or "健康监控" in intent or "系统健康" in intent or "性能监控" in intent or "系统状态" in intent or "system health" in intent.lower() or "health monitor" in intent.lower() or "monitor" in intent.lower() or "系统优化" in intent or "auto optimize" in intent.lower():
        print(f"[智能系统健康监控引擎] 正在监控和分析系统状态...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "system_health_monitor.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["系统监控", "健康监控", "系统健康", "性能监控", "系统状态", "system health", "health monitor", "monitor", "系统优化", "auto optimize"]]
        if not filtered_args:
            # 如果没有额外参数，显示健康报告
            filtered_args = ["report"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能UI结构理解引擎（round 167）- 解析界面元素层级、识别可交互组件、精确点击坐标计算
    elif "UI结构" in intent or "界面元素" in intent or "元素识别" in intent or "ui structure" in intent.lower() or "ui element" in intent.lower() or "element识别" in intent or "界面解析" in intent or "点击元素" in intent or "find element" in intent.lower() or "element" in intent.lower():
        print(f"[智能UI结构理解引擎] 正在分析UI结构...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "ui_structure_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = None
        if "分析" in intent or "analyze" in intent.lower() or "结构" in intent:
            action = "analyze"
        elif "查找" in intent or "find" in intent.lower() or "搜索" in intent or "找" in intent:
            action = "find"
        elif "点击" in intent or "click" in intent.lower():
            action = "click"
        elif "摘要" in intent or "summary" in intent.lower() or "概览" in intent:
            action = "summary"
        elif "交互" in intent or "interactive" in intent.lower() or "探索" in intent:
            action = "interactive"
        # 过滤掉意图关键词
        filter_words = ["UI结构", "界面元素", "元素识别", "ui structure", "ui element", "element识别", "界面解析", "点击元素", "find element", "element", "分析", "analyze", "结构", "查找", "find", "搜索", "找", "点击", "click", "摘要", "summary", "概览", "交互", "interactive", "探索"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        if action and action not in filtered_args:
            filtered_args.insert(0, action)
        if not filtered_args:
            # 默认分析当前UI
            filtered_args = ["analyze"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能操作演示与回放引擎（round 168）- 记录操作序列、转换为run_plan、回放操作、生成演示脚本
    elif "录制操作" in intent or "回放操作" in intent or "操作演示" in intent or "做个教程" in intent or "record operation" in intent.lower() or "playback" in intent.lower() or "operation demo" in intent.lower() or "tutorial" in intent.lower() or "录制" in intent or "回放" in intent:
        print(f"[智能操作演示与回放引擎] 正在处理操作录制请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "operation_recorder.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = None
        if "开始" in intent or "start" in intent.lower() or "录制" in intent and "开始" not in intent:
            action = "start"
        elif "停止" in intent or "stop" in intent.lower():
            action = "stop"
        elif "状态" in intent or "status" in intent.lower():
            action = "status"
        elif "转换" in intent or "convert" in intent.lower() or "run_plan" in intent.lower():
            action = "convert"
        elif "演示" in intent or "demo" in intent.lower() or "教程" in intent:
            action = "demo"
        elif "回放" in intent or "play" in intent.lower() or "playback" in intent.lower():
            action = "play"
        elif "加载" in intent or "load" in intent.lower():
            action = "load"
        # 过滤掉意图关键词
        filter_words = ["录制操作", "回放操作", "操作演示", "做个教程", "record operation", "playback", "operation demo", "tutorial", "录制", "回放", "开始", "start", "停止", "stop", "状态", "status", "转换", "convert", "演示", "demo", "教程", "加载", "load"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        if action and action not in filtered_args:
            filtered_args.insert(0, action)
        if not filtered_args:
            # 默认显示状态
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能代码理解与重构引擎
    elif "代码分析" in intent or "代码理解" in intent or "代码重构" in intent or intent == "code" or intent == "analyze" or "code analysis" in intent.lower() or "code understanding" in intent.lower() or "code refactor" in intent.lower() or "analyze code" in intent.lower():
        print(f"[智能代码理解与重构引擎] 正在分析代码...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "code_understanding_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["代码分析", "代码理解", "代码重构", "code analysis", "code understanding", "code refactor", "analyze code"]]
        if not filtered_args:
            filtered_args = ["--help"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 进化策略引擎
    elif "进化策略" in intent or "策略分析" in intent or "evolution strategy" in intent.lower():
        print(f"[进化策略引擎] 正在分析进化方向...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_strategy_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["analyze"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["进化策略", "策略分析"]]
        if not filtered_args:
            filtered_args = ["analyze"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 进化解释引擎
    elif "进化解释" in intent or "可解释性" in intent or "解释进化" in intent or "evolution explain" in intent.lower() or "explain evolution" in intent.lower():
        print(f"[进化解释引擎] 正在解释进化决策...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_explainer.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["report"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["进化解释", "可解释性", "解释进化"]]
        if not filtered_args:
            filtered_args = ["report"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能引擎编排优化器
    elif "引擎编排" in intent or "引擎优化" in intent or "编排优化" in intent or "engine orchestration" in intent.lower() or "orchestrate" in intent.lower() or "engine optimize" in intent.lower() or "优化引擎" in intent or "引擎协作优化" in intent or "collaboration optimize" in intent.lower():
        print(f"[智能引擎编排优化器] 正在分析引擎协作并生成优化建议...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "engine_orchestration_optimizer.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["引擎编排", "引擎优化", "编排优化", "engine orchestration", "orchestrate", "engine optimize", "优化引擎", "引擎协作优化", "collaboration optimize"]]
        if not filtered_args:
            filtered_args = ["--analyze"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能跨引擎智能体自主协作引擎（round 200）
    elif "智能协作" in intent or "引擎协作" in intent or "多引擎协同" in intent or "智能体协作" in intent or "multi-agent" in intent.lower() or "agent collaboration" in intent.lower() or "跨引擎协作" in intent or "引擎社会" in intent or "任务分配" in intent or "联动执行" in intent or "执行协作任务" in intent or "引擎联动" in intent or "collaboration execute" in intent.lower():
        print(f"[智能跨引擎智能体自主协作引擎] 正在处理请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "multi_agent_collaboration_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["智能协作", "引擎协作", "多引擎协同", "智能体协作", "multi-agent", "agent collaboration", "跨引擎协作", "引擎社会", "任务分配", "联动执行", "执行协作任务", "引擎联动", "collaboration execute"]]
        if not filtered_args:
            # 根据意图确定默认命令
            if "状态" in intent or "status" in intent.lower():
                filtered_args = ["status"]
            elif "统计" in intent or "stats" in intent.lower():
                filtered_args = ["stats"]
            elif "引擎" in intent or "agents" in intent.lower():
                filtered_args = ["agents"]
            elif "日志" in intent or "logs" in intent.lower():
                filtered_args = ["logs"]
            elif "测试" in intent or "test" in intent.lower():
                filtered_args = ["test_execution"]
            elif "执行" in intent or "execute" in intent.lower():
                filtered_args = ["example"]
            else:
                filtered_args = ["example"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能进化协同增强引擎（round 214）
    elif "进化协同" in intent or "协同增强" in intent or "引擎神经网络" in intent or "分布式进化" in intent or "collaboration enhance" in intent.lower() or "evolution collaboration" in intent.lower():
        print(f"[智能进化协同增强引擎] 正在处理请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_collaboration_enhancer.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["进化协同", "协同增强", "引擎神经网络", "分布式进化", "collaboration enhance", "evolution collaboration"]]
        if not filtered_args:
            # 根据意图确定默认命令
            if "状态" in intent or "status" in intent.lower():
                filtered_args = ["status"]
            elif "分析" in intent or "analyze" in intent.lower():
                filtered_args = ["analyze"]
            elif "推荐" in intent or "recommend" in intent.lower():
                filtered_args = ["recommend", "--task-type", "general"]
            elif "关系" in intent or "relationships" in intent.lower():
                filtered_args = ["relationships"]
            elif "创建" in intent or "create" in intent.lower():
                filtered_args = ["create", "--task-id", "test_task", "--engines", "evolution_command_tower,evolution_strategy_optimizer", "--task-type", "test"]
            elif "事件" in intent or "event" in intent.lower():
                filtered_args = ["trigger", "--event-type", "test_event", "--source", "test", "--event-data", "{}"]
            else:
                filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 进化日志分析与可视化
    elif "进化日志" in intent or "日志分析" in intent or "进化分析" in intent or "evolution log" in intent.lower() or "evolution analysis" in intent.lower():
        print(f"[进化日志分析] 正在分析进化日志...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_log_analyzer.py")
        result = subprocess.run([sys.executable, script_path], cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        # 显示分析结果的JSON摘要
        json_path = os.path.join(PROJECT, "runtime/state/evolution_analysis.json")
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                analysis = json.load(f)
            print("\n=== 进化日志分析摘要 ===")
            print(f"总轮次: {analysis['summary']['total_rounds']}")
            print(f"总行动数: {analysis['summary']['total_actions']}")
            print(f"首次轮次: {analysis['summary']['first_round']}")
            print(f"最后轮次: {analysis['summary']['last_round']}")
            print(f"有目标的轮次: {analysis['summary']['rounds_with_goals']}")
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 进化环自我评估
    elif "进化评估" in intent or "自我评估" in intent or "进化健康" in intent or "evolution self" in intent.lower() or "evaluation" in intent.lower():
        print(f"[进化环自我评估] 正在评估进化环状态...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_self_evaluator.py")
        result = subprocess.run([sys.executable, script_path, "evaluate"], cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        # 显示评估结果的摘要
        json_path = os.path.join(PROJECT, "runtime/state/evolution_self_evaluation.json")
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                evaluation = json.load(f)
            print("\n=== 进化环自我评估摘要 ===")
            print(f"健康分数: {evaluation.get('health_score', 0)}")
            print(f"总体评级: {evaluation.get('overall_grade', 'N/A')}")
            print(f"本周完成轮次: {evaluation.get('efficiency_metrics', {}).get('rounds_completed_this_week', 0)}")
            print(f"进化速度: {evaluation.get('efficiency_metrics', {}).get('evolution_velocity', 'N/A')}")
            print(f"完成率: {evaluation.get('success_metrics', {}).get('completion_rate', 0):.1f}%")
            print(f"稳定性分数: {evaluation.get('stability_metrics', {}).get('stability_score', 0)}")
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 进化闭环自动化引擎
    elif "进化闭环" in intent or "闭环自动化" in intent or "evolution loop" in intent.lower() or "evolution automation" in intent.lower() or ("进化" in intent and "自动" in intent):
        print(f"[进化闭环自动化引擎] 正在联动三个进化模块（增强版：智能预测+优先级排序）...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_loop_automation.py")
        result = subprocess.run([sys.executable, script_path], cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        # 显示自动化计划的摘要
        json_path = os.path.join(PROJECT, "runtime/state/evolution_automation_status.json")
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                automation = json.load(f)
            print("\n=== 进化闭环自动化摘要 ===")
            print(f"运行时间: {automation.get('last_run', 'N/A')}")
            print(f"状态: {automation.get('status', 'N/A')}")
            if automation.get("plan"):
                plan = automation["plan"]
                print(f"策略输入: {list(plan.get('strategy_input', {}).keys())}")
                print(f"分析输入: {list(plan.get('analysis_input', {}).keys())}")
                print(f"评估输入: {list(plan.get('evaluation_input', {}).keys())}")
                # 显示预测结果
                prediction = plan.get("prediction", {})
                if prediction.get("predicted_direction") != "unknown":
                    print(f"\n=== 智能预测 ===")
                    print(f"预测进化方向: {prediction.get('predicted_direction', 'N/A')}")
                    print(f"置信度: {prediction.get('confidence', 0.0):.1%}")
                    for reason in prediction.get("reasoning", [])[:2]:
                        print(f"  - {reason}")
                # 显示优先级排序后的任务
                priority_ranked = plan.get("priority_ranked", [])
                if priority_ranked:
                    print(f"\n=== 优先级排序任务 ===")
                    for i, task in enumerate(priority_ranked[:3], 1):
                        print(f"  {i}. {task.get('description', task.get('action', 'N/A'))} (优先级: {task.get('priority', 5)})")
                print(f"\n推荐行动数: {len(plan.get('recommendations', []))}")
                for i, rec in enumerate(plan.get('recommendations', [])[:3], 1):
                    print(f"  {i}. {rec}")
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 进化学习引擎
    elif "进化学习" in intent or "学习进化" in intent or "evolution learning" in intent.lower() or ("进化" in intent and "智能" in intent) or ("学习" in intent and "策略" in intent):
        print(f"[进化学习引擎] 正在从历史数据中学习...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_learning_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["learn"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["进化学习", "学习进化"]]
        if not filtered_args:
            filtered_args = ["learn"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        # 显示学习结果的摘要
        json_path = os.path.join(PROJECT, "runtime/state/evolution_learning_recommendations.json")
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                recommendations = json.load(f)
            print("\n=== 进化学习引擎推荐摘要 ===")
            print(f"推荐数: {len(recommendations.get('recommendations', []))}")
            for i, rec in enumerate(recommendations.get('recommendations', [])[:3], 1):
                print(f"  {i}. [{rec.get('priority', 'N/A')}] {rec.get('title', 'N/A')}: {rec.get('description', 'N/A')[:50]}...")
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 进化环定时触发器
    elif "进化定时" in intent or "定时进化" in intent or "进化调度" in intent or "evolution scheduler" in intent.lower() or "schedule evolution" in intent.lower():
        script_path = os.path.join(SCRIPTS, "evolution_scheduler.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []

        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["进化定时", "定时进化", "进化调度"]]

        # 确定子命令
        if "状态" in intent or "status" in intent.lower():
            subprocess.run([sys.executable, script_path, "status"], cwd=PROJECT, capture_output=True, text=True)
        elif "启动" in intent or "start" in intent.lower() or "开启" in intent:
            if "守护" in intent or "daemon" in intent.lower():
                subprocess.run([sys.executable, script_path, "start", "--daemon"], cwd=PROJECT, capture_output=True, text=True)
            else:
                subprocess.run([sys.executable, script_path, "start"], cwd=PROJECT, capture_output=True, text=True)
        elif "停止" in intent or "stop" in intent.lower() or "关闭" in intent:
            subprocess.run([sys.executable, script_path, "stop"], cwd=PROJECT, capture_output=True, text=True)
        elif "立即运行" in intent or "run" in intent.lower():
            subprocess.run([sys.executable, script_path, "run"], cwd=PROJECT, capture_output=True, text=True)
        elif "启用" in intent or "enable" in intent.lower():
            subprocess.run([sys.executable, script_path, "enable"], cwd=PROJECT, capture_output=True, text=True)
        elif "禁用" in intent or "disable" in intent.lower():
            subprocess.run([sys.executable, script_path, "disable"], cwd=PROJECT, capture_output=True, text=True)
        else:
            # 默认显示状态
            subprocess.run([sys.executable, script_path, "status"], cwd=PROJECT, capture_output=True, text=True)

        # 显示调度器配置摘要
        config_path = os.path.join(PROJECT, "runtime/state/evolution_scheduler_config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print("\n=== 进化环定时触发器配置 ===")
            print(f"启用状态: {'已启用' if config.get('enabled') else '已禁用'}")
            print(f"运行间隔: {config.get('interval_hours')} 小时 {config.get('interval_minutes')} 分钟")
            print(f"上次运行: {config.get('last_run', 'N/A')}")
            print(f"下次运行: {config.get('next_run', 'N/A')}")
            print(f"总运行次数: {config.get('total_runs', 0)}")
        sys.exit(0)
    # 智能进化协调器
    elif "进化协调" in intent or "协调进化" in intent or "evolution coordinator" in intent.lower() or "统一进化" in intent:
        print(f"[智能进化协调器] 正在协调各进化模块...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_coordinator.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["status"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["进化协调", "协调进化", "统一进化"]]
        if not filtered_args:
            filtered_args = ["status"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.returncode == 0:
            json_path = os.path.join(PROJECT, "runtime", "state", "evolution_coordinator_status.json")
            if os.path.exists(json_path):
                import json as json_module
                with open(json_path, 'r', encoding='utf-8') as f:
                    status = json_module.load(f)
                print("\n=== 智能进化协调器状态 ===")
                print(f"协调器状态: {status.get('status', 'N/A')}")
                print(f"健康分数: {status.get('health', {}).get('score', 0):.1f}%")
                print(f"健康状态: {status.get('health', {}).get('status', 'N/A')}")
                print(f"模块数量: {status.get('health', {}).get('modules_ready', 0)}/{status.get('health', {}).get('modules_total', 0)}")
                print(f"可用模块: {', '.join(status.get('modules', []))}")
        sys.exit(0)
    # 进化环可视化监控面板
    elif "进化监控" in intent or "进化面板" in intent or "evolution dashboard" in intent.lower() or "进化状态" in intent:
        print(f"[进化环监控面板] 正在生成监控数据...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_dashboard.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["进化监控", "进化面板", "进化状态"]]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.returncode == 0:
            json_path = os.path.join(PROJECT, "runtime", "state", "evolution_dashboard.json")
            if os.path.exists(json_path):
                import json as json_module
                with open(json_path, 'r', encoding='utf-8') as f:
                    dashboard = json_module.load(f)
                print("\n=== 进化环监控面板 ===")
                mission = dashboard.get("current_mission", {})
                print(f"当前轮次: Round {mission.get('round', 0)}")
                print(f"当前阶段: {mission.get('phase', 'N/A')}")
                health = dashboard.get("modules_health", {})
                print(f"模块健康度: {health.get('healthy_count', 0)}/{health.get('total_count', 0)} ({health.get('health_score', 0)}%)")
                stats = dashboard.get('statistics', {})
                print(f"进化统计: {stats.get('completed_rounds', 0)}/{stats.get('total_rounds', 0)} 轮 ({stats.get('success_rate', 0)}% 成功率)")
                print(f"详细报告已保存至: {json_path}")
        else:
            print(f"执行出错: {result.stderr}", file=sys.stderr)
        sys.exit(0)
    # 进化 CLI 统一入口
    elif "进化cli" in intent or "统一入口" in intent or "进化命令" in intent or "evolution cli" in intent.lower() or ("进化" in intent and "命令行" in intent):
        print(f"[进化环 CLI] 正在执行...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_cli.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["进化cli", "统一入口", "进化命令", "命令行"]]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"执行出错: {result.stderr}", file=sys.stderr)
        sys.exit(result.returncode)
    # 进化环 REST API 服务
    elif "进化api" in intent or "api服务" in intent or "evolution api" in intent.lower() or ("进化" in intent and "接口" in intent):
        print(f"[进化环 API 服务] 正在执行...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_api_server.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["进化api", "api服务", "接口"]]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"执行出错: {result.stderr}", file=sys.stderr)
        sys.exit(result.returncode)
    # 进化决策增强器
    elif "进化决策增强" in intent or "增强进化决策" in intent or "evolution decision" in intent.lower() or ("进化" in intent and "决策" in intent):
        print(f"[进化决策增强器] 正在将智能预测应用到进化决策...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_decision_enhancer.py")
        result = subprocess.run([sys.executable, script_path], cwd=PROJECT, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"执行出错: {result.stderr}", file=sys.stderr)

        # 读取并显示增强报告
        report_path = os.path.join(PROJECT, "runtime/state/evolution_decision_enhancement_report.json")
        if os.path.exists(report_path):
            with open(report_path, 'r', encoding='utf-8') as f:
                report = json.load(f)
            print("\n=== 进化决策增强报告 ===")
            print(f"预测方向: {report.get('enhancement_summary', {}).get('prediction_used', 'N/A')}")
            print(f"置信度: {report.get('enhancement_summary', {}).get('confidence', 0):.1%}")
            print("\n建议:")
            for rec in report.get("recommendations", []):
                print(f"  - {rec}")

        sys.exit(0)
    # 智能系统综合诊断引擎 - 跨模块问题追踪和综合诊断
    elif "系统诊断" in intent or "综合诊断" in intent or "诊断报告" in intent or "diagnostic" in intent.lower() or "diagnose" in intent.lower() or "system diagnose" in intent.lower():
        print(f"[智能系统综合诊断引擎] 正在运行综合诊断...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "system_diagnostic_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "diagnose"
        if "快速" in intent or "quick" in intent.lower() or "状态" in intent:
            action = "quick"
        elif "历史" in intent or "history" in intent.lower():
            action = "history"
        # 过滤掉意图关键词
        filter_words = ["系统诊断", "综合诊断", "诊断报告", "diagnostic", "diagnose", "system diagnose", "快速", "quick", "状态", "历史"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        if action not in ["diagnose", "history"]:
            filtered_args.insert(0, f"--{action}")
        if not filtered_args:
            filtered_args = ["--diagnose"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    elif "进化元学习" in intent or "元学习进化" in intent or "evolution meta" in intent.lower() or ("进化" in intent and "元学习" in intent):
        print(f"[进化元学习引擎] 正在分析进化历史...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_meta_learning_engine.py")
        result = subprocess.run([sys.executable, script_path, "--analyze"], cwd=PROJECT, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"执行出错: {result.stderr}", file=sys.stderr)

        # 读取并显示分析结果
        result_path = os.path.join(PROJECT, "runtime/state/evolution_meta_learning_result.json")
        if os.path.exists(result_path):
            with open(result_path, 'r', encoding='utf-8') as f:
                result_data = json.load(f)
            print("\n=== 进化元学习分析结果 ===")
            patterns = result_data.get("patterns", {})
            print(f"总进化轮次: {patterns.get('total_evolution_rounds', 'N/A')}")
            print(f"完成轮次: {patterns.get('completed_rounds', 'N/A')}")
            if patterns.get('success_rate'):
                print(f"成功率: {patterns.get('success_rate', 0):.1%}")

            recommendations = result_data.get("recommendations", {}).get("next_evolution_suggestions", [])
            if recommendations:
                print("\n进化建议:")
                for rec in recommendations[:5]:  # 只显示前5条
                    print(f"  - {rec}")
        sys.exit(0)
    elif "进化预测" in intent or "高级预测" in intent or "预测增强" in intent or "多维度预测" in intent or ("进化" in intent and ("预测" in intent or "高级" in intent)):
        print(f"[进化高级预测引擎] 正在分析并生成预测...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "advanced_evolution_predictor.py")
        result = subprocess.run([sys.executable, script_path, "--predict"], cwd=PROJECT, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"执行出错: {result.stderr}", file=sys.stderr)

        # 读取并显示预测结果
        result_path = os.path.join(PROJECT, "runtime/state/advanced_evolution_prediction_result.json")
        if os.path.exists(result_path):
            with open(result_path, 'r', encoding='utf-8') as f:
                result_data = json.load(f)
            print("\n=== 进化高级预测结果 ===")

            summary = result_data.get("summary", {})
            print(f"综合置信度: {summary.get('overall_confidence', 0):.1%}")

            recommended = summary.get("recommended_primary_direction")
            if recommended:
                print(f"推荐方向: {recommended.get('direction', 'N/A')}")
                print(f"描述: {recommended.get('description', 'N/A')}")

            timeline = result_data.get("predictions", {}).get("timeline", {})
            if timeline.get("next_evolution_estimate"):
                print(f"预计下次进化: {timeline['next_evolution_estimate']}")
            print(f"趋势分析: {timeline.get('trend_analysis', 'N/A')}")

            # 显示详细推荐
            directions = result_data.get("predictions", {}).get("next_direction", {}).get("recommended_directions", [])
            if directions:
                print("\n详细推荐:")
                for i, d in enumerate(directions[:3], 1):
                    print(f"  {i}. {d.get('direction', 'N/A')}")
                    print(f"     置信度: {d.get('confidence', 0):.1%}")
                    print(f"     {d.get('description', '')}")
        sys.exit(0)
    elif "自适应优先级" in intent or "优先级调整" in intent or "智能优先级" in intent or ("优先级" in intent and "调整" in intent) or ("自适应" in intent and "优先" in intent):
        print(f"[自适应优先级引擎] 正在分析系统状态并调整任务优先级...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "adaptive_priority_engine.py")
        result = subprocess.run([sys.executable, script_path, "--analyze"], cwd=PROJECT, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"执行出错: {result.stderr}", file=sys.stderr)

        # 读取并显示优先级状态
        result_path = os.path.join(PROJECT, "runtime/state/adaptive_priority_result.json")
        if os.path.exists(result_path):
            with open(result_path, 'r', encoding='utf-8') as f:
                result_data = json.load(f)
            print("\n=== 自适应优先级状态 ===")
            system = result_data.get("system", {})
            print(f"系统负载等级: {system.get('load_level', 'N/A')}")

            metrics = system.get("metrics", {})
            if metrics:
                print(f"CPU: {metrics.get('average_cpu', 0):.1f}%")
                print(f"内存: {metrics.get('average_memory', 0):.1f}%")

            user = result_data.get("user", {})
            print(f"\n用户需求等级: {user.get('demand_level', 'N/A')}/10")

            tasks = result_data.get("tasks", {}).get("tasks", [])
            if tasks:
                print("\n任务优先级:")
                for task in tasks[:5]:
                    print(f"  - {task.get('task_name')}: {task.get('current_priority')}/10 ({task.get('adjustment_reason', '')})")

            recommendations = result_data.get("recommendations", [])
            if recommendations:
                print("\n建议:")
                for rec in recommendations:
                    print(f"  - {rec}")
        sys.exit(0)
    # 增强智能知识推理引擎 - 因果推理、类比推理、知识关联发现和主动洞察
    elif "知识推理" in intent or "因果分析" in intent or "推理" in intent or "主动洞察" in intent or "发现关联" in intent or "knowledge reasoning" in intent.lower() or "reasoning" in intent.lower() or "insight" in intent.lower() or "causal" in intent.lower() or "analogy" in intent.lower():
        print(f"[增强智能知识推理引擎] 正在分析知识关联...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "enhanced_knowledge_reasoning_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "reason"
        if "因果" in intent or "cause" in intent.lower():
            action = "causal"
        elif "类似" in intent or "相似" in intent or "analogy" in intent.lower():
            action = "analogy"
        elif "关联" in intent or "association" in intent.lower():
            action = "association"
        elif "洞察" in intent or "主动" in intent or "insight" in intent.lower():
            action = "insight"
        elif "状态" in intent or "status" in intent.lower():
            action = "status"
        # 过滤掉意图关键词
        filter_words = ["知识推理", "因果分析", "推理", "主动洞察", "发现关联", "knowledge reasoning", "reasoning", "insight", "causal", "analogy", "状态"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加命令
        if action not in filtered_args:
            filtered_args.insert(0, action)
        if not filtered_args:
            filtered_args = ["reason"]
        # 提取查询内容
        query = intent
        for word in filter_words:
            query = query.replace(word, "").strip()
        if query:
            filtered_args.extend(["--query", query])
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 知识推理与决策增强引擎 - 知识驱动决策、决策分析、决策模式分析
    elif "知识驱动决策" in intent or "决策增强" in intent or "决策分析" in intent or "决策模式" in intent or "knowledge decision" in intent.lower() or "decision enhancer" in intent.lower() or "决策建议" in intent or "智能决策建议" in intent:
        print(f"[知识推理与决策增强引擎] 正在分析并生成决策建议...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "knowledge_driven_decision_enhancer.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "决策" in intent and ("建议" in intent or "分析" in intent or "evaluate" in intent.lower()):
            action = "decide"
        elif "模式" in intent or "pattern" in intent.lower():
            action = "patterns"
        elif "查询" in intent or "query" in intent.lower() or "搜索" in intent:
            action = "query"
        elif "推理" in intent or "reasoning" in intent.lower():
            action = "reason"
        elif "洞察" in intent or "insight" in intent.lower():
            action = "insight"
        # 过滤掉意图关键词
        filter_words = ["知识驱动决策", "决策增强", "决策分析", "决策模式", "knowledge decision", "decision enhancer", "决策建议", "智能决策建议", "查询", "推理", "洞察", "模式"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加命令
        if action not in filtered_args:
            filtered_args.insert(0, action)
        if not filtered_args:
            filtered_args = ["status"]
        # 提取上下文内容
        query = intent
        for word in filter_words:
            query = query.replace(word, "").strip()
        if query:
            filtered_args.extend(["--context", query])
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 增强多模态场景理解与智能场景联动引擎 - 界面结构解析、场景联动推荐、跨场景上下文传递
    elif "场景理解" in intent or "场景联动" in intent or "智能场景推荐" in intent or "multimodal" in intent.lower() or "scene understanding" in intent.lower() or "scene linkage" in intent.lower() or "scene_recommend" in intent.lower():
        print(f"[增强多模态场景理解引擎] 正在分析场景...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "multimodal_scene_understanding.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "analyze"
        if "推荐" in intent or "recommend" in intent.lower():
            action = "recommend"
        elif "联动" in intent or "link" in intent.lower():
            action = "link"
        elif "上下文" in intent or "context" in intent.lower():
            action = "context"
        elif "理解" in intent or "understand" in intent.lower():
            action = "understand"
        # 过滤掉意图关键词
        filter_words = ["场景理解", "场景联动", "智能场景推荐", "multimodal", "scene understanding", "scene linkage", "scene_recommend", "推荐", "联动", "上下文", "理解"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加命令
        if action not in filtered_args:
            filtered_args.insert(0, action)
        if not filtered_args:
            filtered_args = ["analyze"]
        # 如果是截图路径，直接作为参数
        if len(cmd_args) == 1 and os.path.exists(cmd_args[0]):
            filtered_args = ["analyze", cmd_args[0]]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能任务偏好记忆引擎
    elif "任务偏好" in intent or "我的偏好" in intent or "设置偏好" in intent or "查看偏好" in intent or "preference" in intent.lower() or "task preference" in intent.lower():
        print(f"[智能任务偏好记忆引擎] 正在处理任务偏好请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "task_preference_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["list"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["任务偏好", "我的偏好", "设置偏好", "查看偏好", "preference", "task preference"]]
        if not filtered_args:
            filtered_args = ["list"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能自动化模式发现与场景生成引擎（含引擎协同功能 round 143）
    elif "模式发现" in intent or "自动创建场景" in intent or "发现自动化" in intent or "场景推荐" in intent or "pattern discovery" in intent.lower() or "automation pattern" in intent.lower() or "引擎协同" in intent or "偏好学习" in intent or "深度集成" in intent or "engine collab" in intent.lower() or "learn preferences" in intent.lower():
        print(f"[智能自动化模式发现与场景生成引擎（含引擎协同）] 正在处理请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "automation_pattern_discovery.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else ["discover"]
        # 过滤掉意图关键词
        filtered_args = [arg for arg in cmd_args if arg not in ["模式发现", "自动创建场景", "发现自动化", "场景推荐", "pattern discovery", "automation pattern", "引擎协同", "偏好学习", "深度集成", "engine collab", "learn preferences"]]
        if not filtered_args:
            # 根据意图确定默认命令
            if "协同" in intent or "engine collab" in intent.lower():
                filtered_args = ["collaboration"]
            elif "学习" in intent or "learn" in intent.lower():
                filtered_args = ["learn"]
            elif "应用" in intent or "apply" in intent.lower():
                filtered_args = ["apply"]
            elif "追踪" in intent or "track" in intent.lower():
                filtered_args = ["track"]
            else:
                filtered_args = ["discover"]
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 专注模式
    elif "专注模式" in intent or ("专注" in intent and "模式" in intent):
        if "开始" in intent or "启动" in intent or "开启" in intent:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "focus_reminder.py"), "focus", "mode", "start"], cwd=PROJECT)
        elif "停止" in intent or "结束" in intent or "关闭" in intent:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "focus_reminder.py"), "focus", "mode", "stop"], cwd=PROJECT)
        else:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "focus_reminder.py"), "status"], cwd=PROJECT)
    elif intent in ("当前时间", "时间", "time"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "time_tool.py")], cwd=PROJECT)
    elif intent in ("主机名", "计算机名", "COMPUTERNAME"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "env_tool.py"), "COMPUTERNAME"], cwd=PROJECT)
    elif intent in ("用户名", "USERNAME"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "env_tool.py"), "USERNAME"], cwd=PROJECT)
    elif intent in ("列目录", "list_dir", "ls"):
        p = sys.argv[2] if len(sys.argv) > 2 else "."
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "file_tool.py"), "list", p], cwd=PROJECT)
    elif intent in ("读文件", "file_read"):
        p = sys.argv[2] if len(sys.argv) > 2 else ""
        if p:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "file_tool.py"), "read", p], cwd=PROJECT)
    elif intent in ("写文件", "file_write"):
        p = sys.argv[2] if len(sys.argv) > 2 else ""
        content = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else ""
        if p:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "file_tool.py"), "write", p, content], cwd=PROJECT)
    elif intent == "run" or intent == "执行":
        if len(sys.argv) < 3:
            print("用法: do.py run <脚本名> [参数...]，如 do.py run screenshot_tool 路径", file=sys.stderr)
            sys.exit(1)
        name = sys.argv[2]
        if not name.endswith(".py"):
            name += ".py"
        path = os.path.join(SCRIPTS, name)
        if not os.path.isfile(path):
            print("脚本不存在:", path, file=sys.stderr)
            sys.exit(1)
        subprocess.run([sys.executable, path] + sys.argv[3:], cwd=PROJECT)
    # 智能引擎能力激活与自适应推荐引擎
    elif ("引擎能力激活" in intent or "能力激活" in intent or "引擎推荐" in intent or "激活引擎" in intent or "engine activator" in intent.lower() or "engine capability" in intent.lower() or "引擎仪表盘" in intent or "能力发现" in intent):
        print(f"[Smart Engine Capability Activator] Scanning and recommending engines...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "engine_capability_activator.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "dashboard"
        if "扫描" in intent or "scan" in intent.lower():
            action = "scan"
        elif "推荐" in intent or "recommend" in intent.lower():
            action = "recommend"
        elif "测试" in intent or "test" in intent.lower():
            action = "test"
        elif "状态" in intent or "status" in intent.lower():
            action = "status"
        # 过滤掉意图关键词
        filter_words = ["引擎能力激活", "能力激活", "引擎推荐", "激活引擎", "engine activator", "engine capability", "引擎仪表盘", "能力发现", "推荐", "扫描", "测试", "状态"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加命令
        if action not in filtered_args:
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能零点击服务引擎
    elif "零点击" in intent or "一键服务" in intent or "自动任务链" in intent or "一句话办事" in intent or "零click" in intent.lower() or "zero_click" in intent.lower() or "zero click" in intent.lower() or ("完成" in intent and "整件事" in intent) or ("帮我" in intent and len(intent.split()) < 10) or ("自动" in intent and "执行" in intent and "完整" in intent):
        print(f"[智能零点击服务引擎] 正在分析目标并生成任务链...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "zero_click_service_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "plan"
        if "执行" in intent or "execute" in intent.lower() or "运行" in intent:
            action = "execute"
        elif "状态" in intent or "status" in intent.lower():
            action = "status"
        elif "仪表盘" in intent or "dashboard" in intent.lower():
            action = "dashboard"
        elif "历史" in intent or "history" in intent.lower():
            action = "history"
        # 过滤掉意图关键词
        filter_words = ["零点击", "一键服务", "自动任务链", "一句话办事", "零click", "完成", "整件事", "帮我", "自动", "执行", "状态", "仪表盘", "历史", "运行"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加命令
        if action not in filtered_args:
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能统一元进化引擎
    elif "元进化" in intent or "统一进化" in intent or "meta evolution" in intent.lower() or ("进化" in intent and "协调" in intent) or ("进化" in intent and "引擎" in intent and "状态" in intent) or ("进化" in intent and "机会" in intent) or "进化追踪" in intent or "进化评估" in intent:
        print(f"[智能统一元进化引擎] 正在处理元进化任务...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "meta_evolution_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "full"
        if "状态" in intent or "status" in intent.lower():
            action = "status"
        elif "分析" in intent or "analyze" in intent.lower():
            action = "analyze"
        elif "机会" in intent or "opportunity" in intent.lower():
            action = "opportunities"
        elif "修复" in intent or "repair" in intent.lower() or "自动修复" in intent:
            action = "repair"
        elif "追踪" in intent or "track" in intent.lower() or "进化评估" in intent:
            action = "track"
        # 过滤掉意图关键词
        filter_words = ["元进化", "统一进化", "meta evolution", "进化协调", "引擎状态", "进化机会", "进化追踪", "进化评估"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加命令
        if action not in filtered_args:
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能多维融合智能分析引擎
    elif "多维融合" in intent or "融合分析" in intent or "统一态势" in intent or "融合洞察" in intent or "cross dimension" in intent.lower() or "multi dimension" in intent.lower() or ("态势感知" in intent) or ("跨引擎" in intent and "协同" in intent):
        print(f"[智能多维融合智能分析引擎] 正在处理融合分析任务...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "multi_dimension_fusion_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "summary"
        if "状态" in intent or "status" in intent.lower():
            action = "status"
        elif "洞察" in intent or "insights" in intent.lower():
            action = "insights"
        elif "态势" in intent or "situational" in intent.lower():
            action = "situational"
        elif "协同" in intent or "collaboration" in intent.lower() or "跨引擎" in intent:
            action = "collaboration"
        elif "建议" in intent or "recommendations" in intent.lower() or "推荐" in intent:
            action = "recommendations"
        # 过滤掉意图关键词
        filter_words = ["多维融合", "融合分析", "统一态势", "融合洞察", "态势感知", "cross dimension", "multi dimension", "跨引擎协同"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加命令
        if action not in filtered_args:
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能统一服务中枢引擎 (Round 202)
    elif "统一服务" in intent or "服务中枢" in intent or "统一入口" in intent or "服务聚合" in intent or "unified service" in intent.lower() or "service hub" in intent.lower() or "服务统计" in intent or "服务历史" in intent:
        print(f"[智能统一服务中枢引擎] 正在处理服务请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "unified_service_hub.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "查询" in intent or "query" in intent.lower() or "服务" in intent and "推荐" in intent:
            action = "query"
        elif "统计" in intent or "stats" in intent.lower():
            action = "stats"
        elif "历史" in intent or "history" in intent.lower():
            action = "history"
        elif "状态" in intent or "status" in intent.lower():
            action = "status"
        # 过滤掉意图关键词
        filter_words = ["统一服务", "服务中枢", "统一入口", "服务聚合", "unified service", "service hub", "服务统计", "服务历史", "查询", "统计", "状态"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加命令
        if action not in filtered_args:
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景服务融合引擎 (Round 249)
    elif "全场景服务" in intent or "服务融合" in intent or "模糊需求" in intent or "一站式服务" in intent or "full scenario" in intent.lower() or "service fusion" in intent.lower() or "融合服务" in intent or "智能服务入口" in intent or "理解我的需求" in intent:
        print(f"[智能全场景服务融合引擎] 正在处理服务请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "full_scenario_service_fusion_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "分析" in intent or "analyze" in intent.lower():
            action = "analyze"
        elif "能力" in intent or "capabilities" in intent.lower() or "能做什么" in intent:
            action = "capabilities"
        elif "查询" in intent or "query" in intent.lower() or "服务" in intent:
            action = "query"
        # 过滤掉意图关键词
        filter_words = ["全场景服务", "服务融合", "模糊需求", "一站式服务", "full scenario", "service fusion", "融合服务", "智能服务入口", "理解我的需求", "分析", "能力", "能做什么", "查询"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加命令
        if action not in filtered_args:
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能拟人操作协调引擎 (Round 250) - 像人一样理解任务、选择工具、协同执行
    elif "拟人操作" in intent or "操作协调" in intent or "humanoid" in intent.lower() or "像人一样" in intent or "综合协调" in intent or "引擎协调" in intent:
        print(f"[智能拟人操作协调引擎] 正在处理任务...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "humanoid_operation_coordinator.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "理解" in intent or "understand" in intent.lower():
            action = "understand"
        elif "执行" in intent or "execute" in intent.lower():
            action = "execute"
        elif "建议" in intent or "suggest" in intent.lower() or "推荐" in intent:
            action = "suggest"
        elif "分析" in intent or "analyze" in intent.lower():
            action = "analyze"
        # 过滤掉意图关键词
        filter_words = ["拟人操作", "操作协调", "humanoid", "像人一样", "综合协调", "引擎协调", "理解", "执行", "建议", "推荐", "分析"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加动作
        if action not in filtered_args:
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能引擎深度集成协同引擎 (Round 251) - 将拟人操作协调引擎与全场景服务融合引擎深度集成
    elif "引擎集成" in intent or "深度集成" in intent or "integrate" in intent.lower() or "服务推荐增强" in intent or "上下文保持" in intent or "deep integration" in intent.lower():
        print(f"[智能引擎深度集成协同引擎] 正在处理深度集成请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "engine_deep_integration.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "分析" in intent or "analyze" in intent.lower():
            action = "analyze"
        elif "执行" in intent or "execute" in intent.lower():
            action = "execute"
        elif "上下文" in intent or "context" in intent.lower():
            action = "context"
        elif "清除" in intent or "clear" in intent.lower():
            action = "clear"
        # 过滤掉意图关键词
        filter_words = ["引擎集成", "深度集成", "integrate", "服务推荐增强", "上下文保持", "deep integration", "分析", "执行", "上下文", "清除"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加动作
        if action not in filtered_args:
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能进化环深度集成引擎 (Round 252) - 将深度集成引擎与进化环进一步集成
    elif "进化环深度集成" in intent or "进化深度集成" in intent or "evolution deep" in intent.lower() or "进化智能决策" in intent or "evolution integration" in intent.lower():
        print(f"[智能进化环深度集成引擎] 正在处理进化环深度集成请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_deep_integration.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "分析" in intent or "analyze" in intent.lower():
            action = "analyze"
        elif "洞察" in intent or "insights" in intent.lower():
            action = "insights"
        elif "建议" in intent or "suggest" in intent.lower() or "下一轮" in intent:
            action = "suggest"
        # 过滤掉意图关键词
        filter_words = ["进化环深度集成", "进化深度集成", "evolution deep", "进化智能决策", "evolution integration", "分析", "洞察", "建议", "下一轮"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加动作
        if action not in filtered_args:
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能进化闭环自适应增强引擎 (Round 253) - 让进化环根据实时执行反馈自动调整进化策略
    elif "自适应进化" in intent or "动态进化" in intent or "闭环增强" in intent or "adaptive loop" in intent.lower() or "自适应增强" in intent or "进化自适应" in intent or "进化闭环自适应" in intent:
        print(f"[智能进化闭环自适应增强引擎] 正在处理自适应进化请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_adaptive_loop_enhancer.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "收集" in intent or "collect" in intent.lower() or "反馈" in intent:
            action = "collect"
        elif "适应" in intent or "adapt" in intent.lower() or "调整" in intent:
            action = "adapt"
        elif "选择" in intent or "select" in intent.lower() or "决策" in intent:
            action = "select"
        elif "验证" in intent or "verify" in intent.lower() or "学习" in intent:
            action = "verify"
        elif "建议" in intent or "recommend" in intent.lower() or "推荐" in intent:
            action = "recommend"
        # 过滤掉意图关键词
        filter_words = ["自适应进化", "动态进化", "闭环增强", "adaptive loop", "自适应增强", "进化自适应", "进化闭环自适应", "收集", "反馈", "适应", "调整", "选择", "决策", "验证", "学习", "建议", "推荐"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加动作
        if action not in filtered_args:
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能进化架构自省与自我重构引擎 (Round 254) - 让系统主动分析自身架构问题、识别优化机会、自动进行结构优化
    elif "架构自省" in intent or "自我重构" in intent or "架构优化" in intent or "进化架构" in intent or "architecture" in intent.lower() or "self-reflect" in intent.lower() or "架构分析" in intent or "自省" in intent:
        print(f"[智能进化架构自省与自我重构引擎] 正在处理架构自省请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_architecture_self_refactor.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "分析" in intent or "analyze" in intent.lower() or "架构" in intent:
            action = "analyze"
        elif "问题" in intent or "issue" in intent.lower():
            action = "issues"
        elif "建议" in intent or "suggestion" in intent.lower() or "优化" in intent:
            action = "suggestions"
        elif "自省" in intent or "reflect" in intent.lower() or "完整" in intent:
            action = "reflect"
        elif "重构" in intent or "refactor" in intent.lower() or "重整" in intent:
            action = "refactor"
        # 过滤掉意图关键词
        filter_words = ["架构自省", "自我重构", "架构优化", "进化架构", "architecture", "self-reflect", "架构分析", "自省", "分析", "问题", "建议", "优化", "重构", "重整", "完整"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加动作
        if action not in filtered_args:
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化效率自动优化引擎 (Round 274) - 让进化环执行更快、资源占用更低
    elif "进化效率优化" in intent or "效率优化" in intent or "优化进化环" in intent or "evolution efficiency" in intent.lower() or "进化更快" in intent or "进化性能" in intent or "efficiency optimizer" in intent.lower():
        print(f"[智能全场景进化效率自动优化引擎] 正在处理进化效率优化请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_efficiency_optimizer.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "分析" in intent or "analyze" in intent.lower():
            action = "analyze_time"
        elif "资源" in intent or "resource" in intent.lower():
            action = "analyze_resources"
        elif "瓶颈" in intent or "bottleneck" in intent.lower():
            action = "bottlenecks"
        elif "建议" in intent or "suggest" in intent.lower():
            action = "suggestions"
        elif "优化" in intent or "optimize" in intent.lower():
            action = "optimize"
        # 过滤掉意图关键词
        filter_words = ["进化效率优化", "效率优化", "优化进化环", "evolution efficiency", "进化更快", "进化性能", "efficiency optimizer", "分析", "analyze", "资源", "resource", "瓶颈", "bottleneck", "建议", "suggest", "优化", "optimize"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加动作
        if action not in filtered_args:
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能进化全自主闭环引擎 (Round 255) - 让进化环能够真正自主运行、主动触发、形成完整闭环
    elif "全自主进化" in intent or "自主闭环" in intent or "进化自主运行" in intent or "autonomous loop" in intent.lower() or "自动进化" in intent or "自主进化" in intent or "进化全自主" in intent or "full autonomous" in intent.lower():
        print(f"[智能进化全自主闭环引擎] 正在处理全自主进化请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_full_autonomous_loop.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "检测" in intent or "detect" in intent.lower() or "需求" in intent:
            action = "detect"
        elif "触发" in intent or "trigger" in intent.lower() or "启动" in intent:
            action = "trigger"
        elif "验证" in intent or "verify" in intent.lower() or "效果" in intent:
            action = "verify"
        elif "启动" in intent or "start" in intent.lower() or "运行" in intent:
            action = "start"
        elif "停止" in intent or "stop" in intent.lower():
            action = "stop"
        elif "等级" in intent or "level" in intent.lower() or "模式" in intent:
            action = "level"
        elif "周期" in intent or "cycle" in intent.lower():
            action = "cycle"
        # 过滤掉意图关键词
        filter_words = ["全自主进化", "自主闭环", "进化自主运行", "autonomous loop", "自动进化", "自主进化", "进化全自主", "full autonomous", "检测", "需求", "触发", "验证", "效果", "启动", "运行", "停止", "等级", "模式", "周期"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加动作
        if action not in filtered_args:
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能自主意识觉醒引擎 (Round 256) - 让系统能够主动感知自身状态、主动发现问题、主动规划改进，形成真正的自主意识闭环
    elif "自主意识" in intent or "自我感知" in intent or "系统意识" in intent or "主动发现问题" in intent or "意识状态" in intent or "意识评估" in intent or "意识成长" in intent or "自主目标" in intent or "self awareness" in intent.lower() or "self-awareness" in intent.lower() or "consciousness" in intent.lower():
        print(f"[智能自主意识觉醒引擎] 正在处理自主意识请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_self_awareness_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "感知" in intent or "perceive" in intent.lower():
            action = "perceive"
        elif "报告" in intent or "report" in intent.lower():
            action = "report"
        elif "目标" in intent or "goal" in intent.lower():
            action = "goals"
        elif "设置目标" in intent or "set_goal" in intent.lower():
            action = "set_goal"
        elif "洞察" in intent or "insights" in intent.lower():
            action = "insights"
        elif "级别" in intent or "level" in intent.lower():
            action = "level"
        elif "状态" in intent or "status" in intent.lower():
            action = "status"
        # 过滤掉意图关键词
        filter_words = ["自主意识", "自我感知", "系统意识", "主动发现问题", "意识状态", "意识评估", "意识成长", "自主目标", "self awareness", "self-awareness", "consciousness", "感知", "报告", "目标", "设置目标", "洞察", "级别", "状态"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加命令
        if action not in filtered_args:
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景情境感知与主动服务编排引擎 (Round 257) - 综合时间、行为、系统状态、历史交互，主动识别服务机会并编排多引擎协同
    elif "全场景情境" in intent or "情境编排" in intent or "服务机会" in intent or "主动服务编排" in intent or "context aware" in intent.lower() or "service orchestrator" in intent.lower() or "编排服务" in intent:
        print(f"[智能全场景情境感知与主动服务编排引擎] 正在分析情境并编排服务...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "context_aware_service_orchestrator.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "perceive"
        if "机会" in intent or "opportunities" in intent.lower():
            action = "opportunities"
        elif "编排" in intent or "orchestrate" in intent.lower() or "执行" in intent:
            action = "orchestrate"
        elif "状态" in intent or "status" in intent.lower():
            action = "status"
        elif "记录" in intent or "record" in intent.lower():
            action = "record"
        # 过滤掉意图关键词
        filter_words = ["全场景情境", "情境编排", "服务机会", "主动服务编排", "context aware", "service orchestrator", "编排服务", "机会", "编排", "执行", "状态", "记录"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加命令
        if action not in filtered_args:
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能多维融合智能分析引擎 (Round 204)
    elif "多维分析" in intent or "态势感知" in intent or "智能分析" in intent or "统一分析" in intent or "跨引擎分析" in intent or "multi-dim" in intent.lower() or "situation" in intent.lower() or "智能洞察" in intent:
        print(f"[智能多维融合智能分析引擎] 正在运行多维度分析...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "multi_dim_analysis_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "full"
        if "态势" in intent or "situation" in intent.lower():
            action = "situation"
        elif "协同" in intent or "synergy" in intent.lower() or "跨引擎" in intent:
            action = "synergy"
        elif "预测" in intent or "predict" in intent.lower() or "洞察" in intent:
            action = "predict"
        elif "analyze" in intent.lower():
            action = "analyze"

        # 过滤掉意图关键词
        filter_words = ["多维分析", "态势感知", "智能分析", "统一分析", "跨引擎分析", "multi-dim", "situation", "智能洞察", "预测", "协同", "analyze"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        cmd_args = filtered_args

        # 添加动作参数
        if action not in cmd_args:
            cmd_args.insert(0, action)

        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景智能服务融合引擎 (Round 206)
    elif "服务融合" in intent or "智能服务" in intent or "需求预测" in intent or "完整服务" in intent or "服务闭环" in intent or "service fusion" in intent.lower() or "预测需求" in intent:
        print(f"[智能全场景智能服务融合引擎] 正在处理智能服务请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "intelligent_service_fusion_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "预测" in intent or "predict" in intent.lower():
            action = "predict"
        elif "服务" in intent or "serve" in intent.lower() or "帮我" in intent or "完成" in intent:
            action = "serve"
        elif "分析" in intent or "analyze" in intent.lower() or "模式" in intent:
            action = "analyze"
        # 过滤掉意图关键词
        filter_words = ["服务融合", "智能服务", "需求预测", "完整服务", "服务闭环", "service fusion", "预测需求", "预测", "分析", "模式"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加命令
        if action not in filtered_args:
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能进化效果自动评估引擎 (Round 207)
    elif "进化效果" in intent or "效果评估" in intent or "效率评估" in intent or "进化评估" in intent or "evolution effect" in intent.lower() or "效果分析" in intent or "进化趋势" in intent or "evolution trend" in intent.lower() or "价值评估" in intent:
        print(f"[智能进化效果自动评估引擎] 正在评估进化效果...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_effectiveness_evaluator.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "evaluate"
        if "趋势" in intent or "trend" in intent.lower():
            action = "trends"
        elif "报告" in intent or "report" in intent.lower():
            action = "report"
        elif any(arg.isdigit() for arg in cmd_args):
            action = "value"
        # 过滤掉意图关键词
        filter_words = ["进化效果", "效果评估", "效率评估", "进化评估", "evolution effect", "效果分析", "进化趋势", "evolution trend", "价值评估", "趋势", "报告"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加命令
        if action not in filtered_args and not any(arg.isdigit() for arg in filtered_args):
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能进化执行闭环增强引擎 (Round 222)
    elif "进化追踪" in intent or "执行追踪" in intent or "evolution track" in intent.lower() or "执行闭环" in intent or "进化执行" in intent or "执行报告" in intent or "evolution execution" in intent.lower():
        print(f"[智能进化执行闭环增强引擎] 正在追踪进化执行...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_execution_tracker.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "track"
        if "报告" in intent or "report" in intent.lower():
            action = "report"
        elif "趋势" in intent or "trend" in intent.lower():
            action = "trends"
        elif "状态" in intent or "status" in intent.lower():
            action = "status"
        # 过滤掉意图关键词
        filter_words = ["进化追踪", "执行追踪", "evolution track", "执行闭环", "进化执行", "执行报告", "evolution execution", "报告", "趋势", "状态"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加命令
        if action not in filtered_args:
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能进化闭环自治引擎 (Round 223)
    elif "进化自治" in intent or "自动进化" in intent or "启动进化环" in intent or "停止进化环" in intent or "evolution autonomy" in intent.lower() or "auto evolution" in intent.lower():
        print(f"[智能进化闭环自治引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_autonomy_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "启动" in intent or "start" in intent.lower() or "运行" in intent:
            action = "start"
        elif "停止" in intent or "stop" in intent.lower():
            action = "stop"
        elif "状态" in intent or "status" in intent.lower():
            action = "status"
        elif "健康" in intent or "health" in intent.lower():
            action = "health"
        elif "统计" in intent or "stats" in intent.lower() or "统计" in intent:
            action = "stats"
        elif "立即触发" in intent or "trigger" in intent.lower():
            action = "trigger"
        elif "添加条件" in intent or "add-condition" in intent.lower():
            action = "add-condition"
        # 过滤掉意图关键词
        filter_words = ["进化自治", "自动进化", "启动进化环", "停止进化环", "evolution autonomy", "auto evolution", "启动", "停止", "运行", "状态", "健康", "统计", "立即触发", "trigger", "添加条件"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加命令
        if action not in filtered_args:
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能进化闭环学习增强引擎 (Round 224)
    elif "进化学习" in intent or "闭环学习" in intent or "智能优化" in intent or "进化策略优化" in intent or "evolution loop learning" in intent.lower() or "learning enhancer" in intent.lower() or "学习增强" in intent:
        print(f"[智能进化闭环学习增强引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_loop_learning_enhancer.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "分析" in intent or "analyze" in intent.lower():
            action = "analyze"
        elif "模式" in intent or "patterns" in intent.lower():
            action = "patterns"
        elif "优化" in intent or "optimize" in intent.lower():
            action = "optimize"
        elif "预测" in intent or "predict" in intent.lower():
            action = "predict"
        elif "洞察" in intent or "insights" in intent.lower():
            action = "insights"
        elif "状态" in intent or "status" in intent.lower():
            action = "status"
        # 过滤掉意图关键词
        filter_words = ["进化学习", "闭环学习", "智能优化", "进化策略优化", "evolution loop learning", "learning enhancer", "学习增强", "分析", "模式", "优化", "预测", "洞察", "状态", "analyze", "patterns", "optimize", "predict", "insights", "status"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加命令
        if action not in filtered_args:
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能进化闭环执行增强引擎 (Round 225)
    elif "进化执行" in intent or "闭环执行" in intent or "执行进化" in intent or "自动化进化" in intent or "evolution execution" in intent.lower() or "execution enhancer" in intent.lower() or "执行增强" in intent:
        print(f"[智能进化闭环执行增强引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_loop_execution_enhancer.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "分析" in intent or "analyze" in intent.lower():
            action = "analyze"
        elif "预测" in intent or "predict" in intent.lower():
            action = "predict"
        elif "计划" in intent or "plan" in intent.lower():
            action = "plan"
        elif "执行" in intent or "execute" in intent.lower() or "运行" in intent:
            action = "execute"
        elif "验证" in intent or "validate" in intent.lower() or "校验" in intent:
            action = "validate"
        elif "报告" in intent or "report" in intent.lower():
            action = "report"
        elif "状态" in intent or "status" in intent.lower():
            action = "status"
        # 过滤掉意图关键词
        filter_words = ["进化执行", "闭环执行", "执行进化", "自动化进化", "evolution execution", "execution enhancer", "执行增强", "分析", "预测", "计划", "执行", "验证", "报告", "状态", "analyze", "predict", "plan", "execute", "validate", "report", "status"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加命令
        if action not in filtered_args:
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能进化创意生成引擎 (Round 226)
    elif "进化创意" in intent or "发现进化方向" in intent or "还有什么可以进化" in intent or "进化建议" in intent or "evolution idea" in intent.lower() or "idea generator" in intent.lower() or "进化方向" in intent:
        print(f"[智能进化创意生成引擎] 正在生成进化创意...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_idea_generator.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "generate"
        if "报告" in intent or "report" in intent.lower():
            action = "report"
        elif "top" in intent.lower() or "建议" in intent:
            action = "top"
        elif "生成" in intent:
            action = "generate"
        # 过滤掉意图关键词
        filter_words = ["进化创意", "发现进化方向", "还有什么可以进化", "进化建议", "evolution idea", "idea generator", "进化方向", "生成", "报告", "top", "建议"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加命令
        if action not in filtered_args:
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能进化创意评估与执行引擎 (Round 227) - 集成创意生成到执行
    elif "进化评估" in intent or "创意执行" in intent or "执行创意" in intent or "evolution evaluate" in intent.lower() or "idea execute" in intent.lower() or "进化闭环" in intent or "idea evaluation" in intent.lower() or "创意评估" in intent:
        print(f"[智能进化创意评估与执行引擎] 正在评估和执行进化创意...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_idea_execution_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "evaluate"
        if "执行" in intent or "execute" in intent.lower() or "运行" in intent:
            action = "execute"
        elif "报告" in intent or "report" in intent.lower():
            action = "report"
        elif "状态" in intent or "status" in intent.lower():
            action = "status"
        elif "学习" in intent or "learn" in intent.lower():
            action = "learn"
        # 过滤掉意图关键词
        filter_words = ["进化评估", "创意执行", "执行创意", "evolution evaluate", "idea execute", "进化闭环", "idea evaluation", "创意评估", "执行", "报告", "状态", "学习", "execute", "report", "status", "learn", "运行"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加命令
        if action not in filtered_args:
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能进化闭环完整集成引擎 (Round 228) - 整合创意生成、创意评估执行、进化学习、进化执行
    elif "闭环集成" in intent or "完整闭环" in intent or "发现评估执行学习" in intent or "evolution loop complete" in intent.lower() or "complete loop" in intent.lower() or "闭环完整" in intent or "集成进化" in intent:
        print(f"[智能进化闭环完整集成引擎] 正在运行完整进化闭环...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution闭环_complete_integrator.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "run"
        action_mode = "full"
        if "status" in intent or "状态" in intent:
            action = "status"
        elif "history" in intent or "历史" in intent:
            action = "history"
        elif "analyze" in intent or "分析" in intent:
            action = "analyze"
        elif "discovery" in intent or "发现" in intent:
            action_mode = "discovery"
        elif "evaluation" in intent or "评估" in intent:
            action_mode = "evaluation"
        elif "execution" in intent or "执行" in intent:
            action_mode = "execution"
        elif "learning" in intent or "学习" in intent:
            action_mode = "learning"
        # 过滤掉意图关键词
        filter_words = ["闭环集成", "完整闭环", "发现评估执行学习", "evolution loop complete", "complete loop", "闭环完整", "集成进化", "status", "history", "analyze", "discovery", "evaluation", "execution", "learning", "状态", "历史", "分析", "发现", "评估", "执行", "学习"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加命令
        if action == "run" and action_mode not in filtered_args:
            filtered_args.insert(0, action_mode)
        elif action not in filtered_args:
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path, action] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能进化闭环条件自动触发引擎 (Round 229) - 让进化环能够基于条件自动触发
    elif "条件触发" in intent or "触发条件" in intent or "触发引擎" in intent or "conditional trigger" in intent.lower() or "evolution trigger" in intent.lower() or "设置进化触发" in intent or "查看触发条件" in intent or "触发引擎状态" in intent or "触发引擎统计" in intent:
        print(f"[智能进化闭环条件自动触发引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_conditional_trigger.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "启动" in intent or "start" in intent.lower() or "开始" in intent or "运行" in intent:
            action = "start"
        elif "停止" in intent or "stop" in intent.lower():
            action = "stop"
        elif "统计" in intent or "stats" in intent.lower():
            action = "stats"
        elif "列表" in intent or "list" in intent.lower() or "查看" in intent:
            action = "list"
        elif "添加" in intent or "add" in intent.lower() or "新增" in intent:
            action = "add"
        elif "移除" in intent or "remove" in intent.lower() or "删除" in intent:
            action = "remove"
        elif "启用" in intent or "enable" in intent.lower():
            action = "enable"
        elif "禁用" in intent or "disable" in intent.lower():
            action = "disable"
        elif "立即触发" in intent or "trigger now" in intent.lower() or "手动触发" in intent:
            action = "trigger"
        # 过滤掉意图关键词
        filter_words = ["条件触发", "触发条件", "触发引擎", "conditional trigger", "evolution trigger", "设置进化触发", "查看触发条件", "触发引擎状态", "触发引擎统计", "启动", "start", "开始", "运行", "停止", "stop", "统计", "stats", "列表", "list", "查看", "添加", "add", "新增", "移除", "remove", "删除", "启用", "enable", "禁用", "disable", "立即触发", "trigger now", "手动触发"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        if action not in filtered_args and action not in ["status", "list"]:
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path, action] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全系统健康预警与自适应干预引擎 (Round 230)
    elif "健康预警" in intent or "系统预警" in intent or "健康干预" in intent or "自适应干预" in intent or "health alert" in intent.lower() or "健康趋势" in intent or "预测问题" in intent or "系统预测" in intent:
        print(f"[智能全系统健康预警与自适应干预引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "system_health_alert_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "check"
        if "状态" in intent or "status" in intent.lower():
            action = "status"
        elif "趋势" in intent or "trends" in intent.lower():
            action = "trends"
        elif "预测" in intent or "predict" in intent.lower():
            action = "predict"
        elif "干预" in intent or "intervene" in intent.lower():
            action = "intervene"
        elif "预警" in intent and "查看" in intent or "alerts" in intent.lower():
            action = "alerts"
        elif "干预记录" in intent or "interventions" in intent.lower():
            action = "interventions"
        elif "启动监控" in intent or "start monitor" in intent.lower():
            action = "start"
        elif "停止监控" in intent or "stop monitor" in intent.lower():
            action = "stop"

        # 过滤掉意图关键词
        filter_words = ["健康预警", "系统预警", "健康干预", "自适应干预", "health alert", "健康趋势", "预测问题", "系统预测", "状态", "趋势", "预测", "干预", "预警", "干预记录", "启动监控", "停止监控"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        if action not in filtered_args and action not in ["status", "check"]:
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path, action] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能健康预警与进化自动触发集成引擎 (Round 231) - 将健康预警与进化触发深度集成
    elif "预警进化" in intent or "健康驱动进化" in intent or "预警触发进化" in intent or "健康预警进化" in intent or "health evolution" in intent.lower() or "预警集成" in intent or "health evolution integration" in intent.lower():
        print(f"[智能健康预警与进化自动触发集成引擎] 正在处理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "health_evolution_integration.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "检查" in intent or "check" in intent.lower():
            action = "check"
        elif "触发" in intent or "trigger" in intent.lower():
            action = "trigger"
        elif "历史" in intent or "history" in intent.lower():
            action = "history"
        elif "统计" in intent or "stats" in intent.lower():
            action = "stats"
        elif "配置" in intent or "config" in intent.lower():
            action = "config"
        elif "启动监控" in intent or "start monitor" in intent.lower() or "开始监控" in intent:
            action = "start"
        elif "停止监控" in intent or "stop monitor" in intent.lower() or "停止监控" in intent:
            action = "stop"
        elif "验证" in intent or "verify" in intent.lower():
            action = "verify"
        elif "启用" in intent or "enable" in intent.lower():
            action = "enable"
        elif "禁用" in intent or "disable" in intent.lower():
            action = "enable"
        # 过滤掉意图关键词
        filter_words = ["预警进化", "健康驱动进化", "预警触发进化", "健康预警进化", "health evolution", "预警集成", "检查", "check", "触发", "trigger", "历史", "history", "统计", "stats", "配置", "config", "启动监控", "开始监控", "停止监控", "验证", "verify", "启用", "enable", "禁用", "disable"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        if action not in filtered_args and action not in ["status", "check"]:
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path, action] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景自进化健康保障闭环引擎 (Round 271-272 深度集成版)
    elif "进化健康" in intent or "自进化保障" in intent or "evolution health" in intent.lower() or "进化保障" in intent or "健康闭环" in intent or "自进化健康" in intent or "自动修复" in intent or "闭环自愈" in intent:
        print(f"[智能全场景自进化健康保障闭环引擎 v2.0] 正在检查进化健康状态...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_health_assurance_loop.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作 (v2.0 新增: auto_repair, verify, closed_loop)
        action = "summary"
        if "检查" in intent or "check" in intent.lower() or "状态" in intent:
            action = "check"
        elif "诊断" in intent or "diagnose" in intent.lower():
            action = "diagnose"
        elif "自动修复" in intent or "auto_repair" in intent.lower():
            action = "auto_repair"
        elif "验证" in intent or "verify" in intent.lower():
            action = "verify"
        elif "闭环" in intent or "closed_loop" in intent.lower() or "完整闭环" in intent:
            action = "closed_loop"
        elif "修复" in intent or "heal" in intent.lower() or "自愈" in intent:
            action = "heal"
        elif "评估" in intent or "evaluate" in intent.lower():
            action = "evaluate"
        elif "摘要" in intent or "summary" in intent.lower():
            action = "summary"
        # 过滤掉意图关键词 (v2.0 新增关键词)
        filter_words = ["进化健康", "自进化保障", "evolution health", "进化保障", "健康闭环", "自进化健康", "自动修复", "闭环自愈", "检查", "check", "状态", "诊断", "diagnose", "修复", "heal", "自愈", "评估", "evaluate", "摘要", "summary", "自动修复", "auto_repair", "验证", "verify", "闭环", "closed_loop", "完整闭环"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        if action not in filtered_args:
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path, action] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景系统健康防御深度协同引擎 (Round 326) - 需要在错误模式防御之前
    elif ("健康防御" in intent or "系统防御" in intent or "防御协同" in intent or
          "health defense" in intent.lower() or "防御闭环" in intent or
          "统一防御" in intent or "防御体系" in intent or "health_defense" in intent.lower()) and "错误模式" not in intent:
        print(f"[智能全场景系统健康防御深度协同引擎 v1.0] 正在执行健康防御协同...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "health_defense_deep_integration.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "状态" in intent or "status" in intent.lower():
            action = "status"
        elif "仪表盘" in intent or "dashboard" in intent.lower():
            action = "dashboard"
        elif "检查" in intent or "check" in intent.lower():
            action = "check"
        elif "完整周期" in intent or "full_cycle" in intent.lower() or "全链路" in intent or "防御周期" in intent:
            action = "full-cycle"
        elif "修复" in intent or "repair" in intent.lower():
            action = "repair"
        # 过滤掉意图关键词
        filter_words = ["健康防御", "系统防御", "防御协同", "health defense", "防御闭环", "统一防御", "健康闭环", "防御体系", "health_defense", "状态", "status", "仪表盘", "dashboard", "检查", "check", "完整周期", "full_cycle", "全链路", "防御周期", "修复", "repair"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        if action not in filtered_args:
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景跨维度健康态势感知与预测防御引擎 (Round 327)
    elif (("健康" in intent and "态势" in intent) or "跨维度健康" in intent or
          "health situation awareness" in intent.lower() or "预测防御" in intent or
          "前瞻防御" in intent or "风险预测" in intent or
          "preemptive defense" in intent.lower() or
          "health_situation" in intent.lower() or ("跨时间" in intent and "健康" in intent)):
        print(f"[智能全场景跨维度健康态势感知与预测防御引擎 v1.0] 正在执行态势感知与预测...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "health_situation_awareness_prediction_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "full"
        if "状态" in intent or "status" in intent.lower():
            action = "status"
        elif "态势" in intent or "situation" in intent.lower():
            action = "situation"
        elif "趋势" in intent or "trend" in intent.lower():
            action = "trends"
        elif "预测" in intent or "predict" in intent.lower() or "风险" in intent:
            action = "predict"
        elif "完整周期" in intent or "full" in intent.lower() or "报告" in intent:
            action = "full"
        # 过滤掉意图关键词
        filter_words = ["健康态势", "跨维度健康", "health situation awareness", "预测防御", "前瞻防御", "风险预测", "preemptive defense", "health_situation", "跨时间健康", "状态", "status", "趋势", "trend", "预测", "predict", "风险", "完整周期", "full", "报告", "态势"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加 -- 前缀
        if action not in filtered_args:
            filtered_args.insert(0, "--" + action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景系统健康免疫增强与自愈进化引擎 (Round 328)
    elif (("健康免疫" in intent or "免疫增强" in intent or "自愈进化" in intent or
          "health immunity" in intent.lower() or "immunity enhancement" in intent.lower() or
          "self healing evolution" in intent.lower() or "免疫系统" in intent or
          "immune system" in intent.lower() or "immunity_evolution" in intent.lower() or
          "自愈学习" in intent or "免疫记忆" in intent or "主动免疫" in intent)):
        print(f"[智能全场景系统健康免疫增强与自愈进化引擎 v1.0] 正在执行免疫增强与自愈进化...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "health_immunity_evolution_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "状态" in intent or "status" in intent.lower():
            action = "status"
        elif "增强" in intent or "enhance" in intent.lower() or "提升" in intent:
            action = "enhance"
        elif "学习" in intent or "learn" in intent.lower():
            action = "learn"
        elif "完整周期" in intent or "full" in intent.lower() or "周期" in intent:
            action = "full-cycle"
        elif "仪表盘" in intent or "dashboard" in intent.lower():
            action = "dashboard"
        # 过滤掉意图关键词
        filter_words = ["健康免疫", "免疫增强", "自愈进化", "health immunity", "immunity enhancement",
                       "self healing evolution", "免疫系统", "immune system", "immunity_evolution",
                       "自愈学习", "免疫记忆", "主动免疫", "状态", "status", "增强", "enhance",
                       "提升", "学习", "learn", "完整周期", "full-cycle", "周期", "仪表盘", "dashboard"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加 -- 前缀
        if action not in filtered_args:
            filtered_args.insert(0, "--" + action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化环全局态势感知与自适应决策增强引擎 (Round 329)
    elif ("全局态势" in intent or "态势感知" in intent or "全局感知" in intent or
          "global situation" in intent.lower() or "situation awareness" in intent.lower() or
          "adaptive decision" in intent.lower() or "自适应决策" in intent or
          "决策增强" in intent or "decision enhancement" in intent.lower() or
          "决策质量" in intent or "优化建议" in intent or "智能建议" in intent or
          "动态优化" in intent or "adaptive optimization" in intent.lower() or
          "态势分析" in intent or "situation analyze" in intent.lower() or
          "决策增强" in intent or "全局态势感知" in intent):
        print(f"[智能全场景进化环全局态势感知与自适应决策增强引擎 v1.0] 正在执行全局态势感知与自适应决策增强...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_global_situation_awareness.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "状态" in intent or "status" in intent.lower():
            action = "status"
        elif "感知" in intent or "perceive" in intent.lower():
            action = "perceive"
        elif "分析" in intent or "analyze" in intent.lower():
            action = "analyze"
        elif "增强" in intent or "enhance" in intent.lower() or "决策增强" in intent:
            action = "enhance"
        elif "完整周期" in intent or "full-cycle" in intent.lower() or "完整" in intent:
            action = "full-cycle"
        elif "优化建议" in intent or "suggestions" in intent.lower():
            action = "full-cycle"
        # 过滤掉意图关键词
        filter_words = ["全局态势", "态势感知", "全局感知", "global situation", "situation awareness",
                       "adaptive decision", "自适应决策", "决策增强", "decision enhancement",
                       "决策质量", "优化建议", "智能建议", "动态优化", "adaptive optimization",
                       "态势分析", "situation analyze", "全局态势感知", "状态", "status",
                       "感知", "perceive", "分析", "analyze", "增强", "enhance", "完整周期", "full-cycle", "完整"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加 -- 前缀
        if action not in filtered_args:
            filtered_args.insert(0, "--" + action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景知识图谱深度推理与主动洞察生成引擎 (Round 330)
    elif ("知识推理" in intent or "图谱推理" in intent or "知识图谱" in intent or
          "kg reasoning" in intent.lower() or "kg推理" in intent or
          "主动洞察" in intent or "洞察生成" in intent or "insight" in intent.lower() or
          "洞察发现" in intent or "创新发现" in intent or "discovery" in intent.lower() or
          "创新方向" in intent or "跨领域" in intent or "cross domain" in intent.lower() or
          "价值发现" in intent or "hidden opportunity" in intent.lower() or
          "深度推理" in intent or "deep reasoning" in intent.lower()):
        print(f"[智能全场景知识图谱深度推理与主动洞察生成引擎 v1.0] 正在执行知识图谱深度推理与洞察生成...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_kg_deep_reasoning_insight_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "generate"
        if "洞察" in intent or "insight" in intent.lower():
            action = "generate"
        elif "推理" in intent or "reasoning" in intent.lower() or "分析" in intent:
            action = "reasoning"
        elif "仪表盘" in intent or "dashboard" in intent.lower() or "状态" in intent:
            action = "dashboard"
        elif "验证" in intent or "validate" in intent.lower():
            action = "validate"
        elif "实现" in intent or "implement" in intent.lower():
            action = "implement"
        elif "完整" in intent or "full" in intent.lower() or "循环" in intent:
            action = "full-cycle"
        # 过滤掉意图关键词
        filter_words = ["知识推理", "图谱推理", "知识图谱", "kg reasoning", "kg推理",
                       "主动洞察", "洞察生成", "insight", "洞察发现", "创新发现", "discovery",
                       "创新方向", "跨领域", "cross domain", "价值发现", "hidden opportunity",
                       "深度推理", "deep reasoning", "推理", "reasoning", "分析",
                       "洞察", "仪表盘", "dashboard", "状态", "验证", "validate",
                       "实现", "implement", "完整", "full", "循环", "generate", "reasoning", "dashboard"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加 -- 前缀
        if action not in filtered_args and not any(arg.startswith("--") for arg in filtered_args):
            filtered_args.insert(0, "--" + action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景洞察驱动进化自动执行引擎 (Round 331)
    elif ("洞察执行" in intent or "洞察驱动" in intent or "insight driven" in intent.lower() or
          "洞察落地" in intent or "执行洞察" in intent or "execute insight" in intent.lower() or
          "洞察任务" in intent or "insight task" in intent.lower() or
          "洞察转化" in intent or "自动执行洞察" in intent or "insight auto" in intent.lower() or
          "洞察→执行" in intent or "洞察到执行" in intent or "insight to execution" in intent.lower()):
        print(f"[智能全场景洞察驱动进化自动执行引擎 v1.0] 正在执行洞察驱动的进化自动执行...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_insight_driven_execution_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "执行" in intent or "execute" in intent.lower() or "运行" in intent or "run" in intent.lower():
            action = "run-cycle"
        elif "仪表盘" in intent or "dashboard" in intent.lower() or "状态" in intent:
            action = "dashboard"
        elif "分析" in intent or "analyze" in intent.lower():
            action = "analyze"
        # 过滤掉意图关键词
        filter_words = ["洞察执行", "洞察驱动", "insight driven", "洞察落地", "执行洞察",
                       "execute insight", "洞察任务", "insight task", "洞察转化",
                       "自动执行洞察", "insight auto", "洞察→执行", "洞察到执行",
                       "insight to execution", "执行", "execute", "运行", "run",
                       "仪表盘", "dashboard", "状态", "分析", "analyze"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加 -- 前缀
        if action not in filtered_args and not any(arg.startswith("--") for arg in filtered_args):
            filtered_args.insert(0, "--" + action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景跨轮次进化知识深度融合与自适应推理引擎 (Round 332)
    elif ("跨轮融合" in intent or "跨轮次" in intent or "跨轮" in intent or
          "cross round" in intent.lower() or "cross-round" in intent.lower() or
          "知识融合" in intent or "fusion" in intent.lower() or
          "自适应推理" in intent or "adaptive inference" in intent.lower() or
          "进化推理" in intent or "evolution inference" in intent.lower() or
          "跨轮学习" in intent or "cross-round learning" in intent.lower() or
          "跨轮知识" in intent or "知识推理" in intent):
        print(f"[智能全场景跨轮次进化知识深度融合与自适应推理引擎 v1.0] 正在执行跨轮次知识融合与自适应推理...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_cross_round_knowledge_fusion_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "融合" in intent or "fuse" in intent.lower() or "知识" in intent:
            action = "fuse"
        elif "推理" in intent or "inference" in intent.lower() or "infer" in intent.lower() or "推理" in intent:
            action = "infer"
        elif "决策" in intent or "decision" in intent.lower() or "增强决策" in intent:
            action = "enhance-decision"
        elif "仪表盘" in intent or "dashboard" in intent.lower() or "状态" in intent:
            action = "dashboard"
        elif "分析" in intent or "analyze" in intent.lower():
            action = "analyze"
        # 过滤掉意图关键词
        filter_words = ["跨轮融合", "跨轮次", "跨轮", "cross round", "cross-round",
                       "知识融合", "fusion", "自适应推理", "adaptive inference",
                       "进化推理", "evolution inference", "跨轮学习", "cross-round learning",
                       "跨轮知识", "知识推理", "推理", "infer", "决策", "decision",
                       "增强决策", "融合", "fuse", "分析", "analyze",
                       "仪表盘", "dashboard", "状态"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加 -- 前缀
        if action not in filtered_args and not any(arg.startswith("--") for arg in filtered_args):
            filtered_args.insert(0, "--" + action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能进化决策可解释性深度增强引擎 (Round 333)
    elif ("决策可解释" in intent or "可解释性" in intent or "解释决策" in intent or
          "decision explain" in intent.lower() or "explainability" in intent.lower() or
          "决策解释" in intent or "解释进化" in intent or "evolution explain" in intent.lower() or
          "决策依据" in intent or "知其然" in intent or "reasoning chain" in intent.lower() or
          "决策证据" in intent or "evidence" in intent.lower() or
          "进化可解释" in intent):
        print(f"[智能进化决策可解释性深度增强引擎 v1.0] 正在分析进化决策依据...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_decision_explainability_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "记录" in intent or "record" in intent.lower():
            action = "record"
        elif "解释" in intent or "explain" in intent.lower():
            action = "explain"
        elif "历史" in intent or "history" in intent.lower():
            action = "history"
        elif "质量" in intent or "quality" in intent.lower():
            action = "quality"
        elif "最近" in intent or "recent" in intent.lower():
            action = "recent"
        elif "自动" in intent or "auto" in intent.lower():
            action = "auto_explain"
        # 过滤掉意图关键词
        filter_words = ["决策可解释", "可解释性", "解释决策", "decision explain", "explainability",
                       "决策解释", "解释进化", "evolution explain", "决策依据", "知其然",
                       "reasoning chain", "决策证据", "evidence", "进化可解释",
                       "记录", "record", "解释", "explain", "历史", "history", "质量", "quality",
                       "最近", "recent", "自动", "auto"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加 -- 前缀
        if action not in filtered_args and not any(arg.startswith("--") for arg in filtered_args):
            filtered_args.insert(0, "--" + action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化决策质量实时评估与自适应优化引擎 (Round 335) - 需要放在前面以避免被 round 334 拦截
    elif ("决策质量评估" in intent or "质量评估" in intent or "质量优化" in intent or
          "quality evaluation" in intent.lower() or "decision quality" in intent.lower() or
          "自适应优化" in intent or "优化建议" in intent or
          "决策偏差" in intent or "质量趋势" in intent):
        print(f"[智能进化决策质量实时评估与自适应优化引擎 v1.0] 正在处理决策质量评估...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_decision_quality_evaluator.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "评估" in intent or "evaluate" in intent.lower() or "评估决策" in intent:
            action = "--evaluate"
        elif "分析" in intent or "analyze" in intent.lower() or "偏差" in intent:
            action = "--analyze"
        elif "建议" in intent or "suggest" in intent.lower() or "优化建议" in intent:
            action = "--suggest"
        elif "趋势" in intent or "trend" in intent.lower() or "质量趋势" in intent:
            action = "--trend"
        # 过滤掉意图关键词
        filter_words = ["决策质量评估", "质量评估", "质量优化", "quality evaluation", "decision quality",
                       "自适应优化", "优化建议", "决策偏差", "质量趋势",
                       "评估", "evaluate", "分析", "analyze", "建议", "suggest", "趋势", "trend",
                       "状态", "status"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加动作前缀
        if action not in filtered_args and not any(arg.startswith("--") for arg in filtered_args):
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能全场景进化决策-知识-解释深度集成引擎 (Round 334)
    elif ("决策知识集成" in intent or "解释增强" in intent or
          "知识驱动决策" in intent or "decision knowledge" in intent.lower() or
          "知识解释集成" in intent or "深度集成决策" in intent):
        print(f"[智能进化决策-知识-解释深度集成引擎 v1.0] 正在处理知识驱动的决策...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_decision_knowledge_integration.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "决策" in intent and ("做" in intent or "生成" in intent or "执行" in intent):
            action = "decision"
        elif "关联" in intent or "link" in intent.lower() or "追踪" in intent:
            action = "link"
        elif "解释" in intent or "explain" in intent.lower():
            action = "explain"
        elif "反馈" in intent or "学习" in intent or "feedback" in intent.lower() or "learn" in intent.lower():
            action = "feedback"
        elif "自适应" in intent or "adaptive" in intent.lower():
            action = "adaptive-level"
        # 过滤掉意图关键词
        filter_words = ["决策知识集成", "决策优化", "解释增强", "知识驱动决策", "decision knowledge",
                       "决策学习", "知识解释集成", "深度集成决策", "状态", "status", "决策", "做", "生成",
                       "执行", "关联", "link", "追踪", "解释", "explain", "反馈", "学习", "feedback",
                       "learn", "自适应", "adaptive"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        # 添加 -- 前缀
        if action not in filtered_args and not any(arg.startswith("--") for arg in filtered_args):
            filtered_args.insert(0, "--" + action)
        result = subprocess.run([sys.executable, script_path] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能进化方向自动发现与优先级排序引擎 (Round 239)
    elif "进化发现" in intent or "方向发现" in intent or "优先级排序" in intent or "evolution discovery" in intent.lower() or "方向排序" in intent or "进化机会" in intent or "发现进化" in intent or "自动发现进化" in intent:
        print(f"[智能进化方向自动发现引擎] 正在分析进化机会...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_direction_discovery.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "report"
        if "分析" in intent or "analyze" in intent.lower():
            action = "analyze"
        elif "排序" in intent or "rank" in intent.lower():
            action = "rank"
        elif "计划" in intent or "plan" in intent.lower():
            action = "plan"
        elif "报告" in intent or "report" in intent.lower():
            action = "report"
        # 过滤掉意图关键词
        filter_words = ["进化发现", "方向发现", "优先级排序", "evolution discovery", "方向排序", "进化机会", "发现进化", "自动发现进化", "分析", "analyze", "排序", "rank", "计划", "plan", "报告", "report"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        if action not in filtered_args:
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path, action] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能跨代进化知识传承引擎 (Round 240)
    elif "进化知识传承" in intent or "知识传承" in intent or "跨代知识" in intent or "knowledge inheritance" in intent.lower() or "进化知识" in intent or "传承进化" in intent:
        print(f"[智能跨代进化知识传承引擎] 正在处理知识传承...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_knowledge_inheritance_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "提取" in intent or "extract" in intent.lower():
            action = "extract"
        elif "图谱" in intent or "graph" in intent.lower():
            action = "graph"
        elif "查询" in intent or "query" in intent.lower() or "搜索" in intent:
            action = "query"
            # 从参数中提取查询词
            for arg in cmd_args:
                if not any(kw in arg for kw in ["进化知识传承", "知识传承", "跨代知识", "knowledge inheritance", "进化知识", "传承进化", "提取", "extract", "图谱", "graph", "查询", "query", "搜索", "推荐", "recommend", "缺口", "gaps", "状态", "status"]):
                    action_arg = arg
                    break
        elif "推荐" in intent or "recommend" in intent.lower():
            action = "recommend"
        elif "缺口" in intent or "gaps" in intent.lower():
            action = "gaps"
        # 过滤掉意图关键词
        filter_words = ["进化知识传承", "知识传承", "跨代知识", "knowledge inheritance", "进化知识", "传承进化", "提取", "extract", "图谱", "graph", "查询", "query", "搜索", "推荐", "recommend", "缺口", "gaps", "状态", "status"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        if action not in filtered_args:
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path, action] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能进化知识驱动自适应执行引擎 (Round 241)
    elif "知识驱动执行" in intent or "知识执行" in intent or "自适应执行" in intent or "知识自适应" in intent or "knowledge driven" in intent.lower() or "knowledge execution" in intent.lower() or "knowledge adaptive" in intent.lower() or "智能执行" in intent or "执行优化" in intent:
        print(f"[智能进化知识驱动自适应执行引擎] 正在处理知识驱动执行...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "evolution_knowledge_driven_executor.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "status"
        if "检索" in intent or "知识" in intent or "knowledge" in intent.lower():
            action = "knowledge"
        elif "适配" in intent or "adapt" in intent.lower() or "策略" in intent:
            action = "adapt"
        elif "统计" in intent or "stats" in intent.lower():
            action = "stats"
        elif "模式" in intent or "patterns" in intent.lower() or "分析" in intent:
            action = "patterns"
        # 过滤掉意图关键词
        filter_words = ["知识驱动执行", "知识执行", "自适应执行", "知识自适应", "knowledge driven", "knowledge execution", "knowledge adaptive", "智能执行", "执行优化", "检索", "适配", "adapt", "策略", "统计", "stats", "模式", "patterns", "分析"]
        filtered_args = [arg for arg in cmd_args if arg not in filter_words]
        if action not in filtered_args:
            filtered_args.insert(0, action)
        result = subprocess.run([sys.executable, script_path, action] + filtered_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    # 智能系统自检与健康报告引擎 (Round 203) - 放在 system_health_monitor 之前
    elif "健康检查" in intent or "健康报告" in intent or "系统自检" in intent or "health check" in intent.lower() or "health report" in intent.lower() or "系统诊断" in intent:
        print(f"[智能系统自检与健康报告引擎] 正在运行健康检查...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "system_health_report_engine.py")
        # 解析命令参数
        cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
        # 判断动作
        action = "--check"
        if "详细" in intent or "report" in intent.lower() or "完整" in intent:
            action = "--report"
        elif "摘要" in intent or "summary" in intent.lower():
            action = "--summary"
        elif "--output" in " ".join(cmd_args):
            # 保持原样
            pass
        else:
            # 过滤掉意图关键词
            filter_words = ["系统健康", "健康检查", "健康报告", "系统自检", "system health", "health check", "health report", "系统状态", "系统诊断", "详细", "摘要", "完整", "report", "summary"]
            filtered_args = [arg for arg in cmd_args if arg not in filter_words]
            cmd_args = filtered_args

            # 添加动作参数
            if action not in cmd_args:
                cmd_args.insert(0, action)

        result = subprocess.run([sys.executable, script_path] + cmd_args, cwd=PROJECT, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(0 if result.returncode == 0 else result.returncode)
    else:
        # 未知意图时，先检查是否包含情感关键词
        import json
        import glob

        # 检查是否包含情感关键词，如果是则触发情感交互
        emotion_keywords = ["累", "好累", "疲惫", "困", "好困", "无聊", "开心", "难过", "焦虑", "烦", "伤心", "郁闷", "迷茫"]
        user_input_full = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
        has_emotion = any(kw in user_input_full for kw in emotion_keywords)

        if has_emotion:
            print(f"[情感交互] 检测到您可能有些情绪，尝试理解您的感受...", file=sys.stderr)
            script_path = os.path.join(SCRIPTS, "emotional_interaction.py")
            result = subprocess.run([sys.executable, script_path, user_input_full], cwd=PROJECT, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            if result.returncode != 0 and result.stderr:
                print(result.stderr, file=sys.stderr)
            sys.exit(0 if result.returncode == 0 else result.returncode)

        # 获取用户偏好
        user_prefs = _get_user_preferences()

        # 获取智能推荐
        recommendations = _get_smart_scenario_recommendations(intent, user_prefs)

        # 获取基于前台窗口的推荐
        foreground_recommendations = _get_foreground_based_recommendations()

        # 合并推荐结果
        all_recommendations = []
        seen_plans = set()

        # 先添加智能推荐
        for rec in recommendations:
            if rec['plan'] not in seen_plans:
                all_recommendations.append(rec)
                seen_plans.add(rec['plan'])

        # 再添加前台窗口推荐（带标记）
        for rec in foreground_recommendations:
            if rec['plan'] not in seen_plans:
                rec_copy = rec.copy()
                rec_copy['score'] = rec_copy.get('score', 0) + 3  # 前台窗口推荐加分
                rec_copy['source'] = 'foreground'
                all_recommendations.append(rec_copy)
                seen_plans.add(rec['plan'])

        # 按分数排序
        all_recommendations.sort(key=lambda x: x.get('score', 0), reverse=True)

        if all_recommendations:
            print("未找到直接匹配的命令，根据您的当前使用场景和偏好，为您推荐以下计划:", file=sys.stderr)
            # 显示前台窗口信息
            if foreground_recommendations:
                fg_title = foreground_recommendations[0].get('matched_on', '')
                if fg_title:
                    print(f"  [检测到您正在使用: {fg_title}]", file=sys.stderr)
            for rec in all_recommendations[:5]:
                source_tag = " [当前场景]" if rec.get('source') == 'foreground' else ""
                print(f"  - {rec['intent']}{source_tag}: 使用 run_plan assets/plans/{rec['plan']}", file=sys.stderr)
            print("可用: python scripts/run_plan.py assets/plans/<计划名>.json", file=sys.stderr)
            sys.exit(0)  # 不是错误，只是推荐
        else:
            # 如果没有智能推荐，则使用原有逻辑
            plans_dir = os.path.join(PROJECT, "assets", "plans")
            matched_plans = []
            if os.path.isdir(plans_dir):
                for plan_file in glob.glob(os.path.join(plans_dir, "*.json")):
                    try:
                        with open(plan_file, encoding="utf-8") as f:
                            plan_data = json.load(f)
                            triggers = plan_data.get("triggers", [])
                            for trigger in triggers:
                                if trigger in intent or intent in trigger:
                                    matched_plans.append((os.path.basename(plan_file), plan_data.get("intent", ""), trigger))
                                    break
                    except Exception:
                        pass
            if matched_plans:
                print("未找到直接匹配的命令，但发现以下相关计划:", file=sys.stderr)
                for plan_name, plan_intent, trigger in matched_plans:
                    print(f"  - {plan_intent}: 使用 run_plan assets/plans/{plan_name}", file=sys.stderr)
                print("可用: python scripts/run_plan.py assets/plans/<计划名>.json", file=sys.stderr)
                sys.exit(0)  # 不是错误，只是推荐
            print("未知意图:", intent, file=sys.stderr)
            sys.exit(1)


# 入口点
if __name__ == '__main__':
    main()
