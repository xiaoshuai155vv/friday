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
    # 智能全场景超级预测与主动价值创造引擎（Round 287）
    elif "超级预测" in intent or "主动价值创造" in intent or "机会发现" in intent or "价值预测" in intent or "super prediction" in intent.lower() or "opportunity discovery" in intent.lower() or "create value" in intent.lower() or "价值创造" in intent or "趋势分析" in intent or "trends analysis" in intent.lower():
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
    # 跨模态深度融合引擎
    elif "跨模态" in intent or "多模态融合" in intent or "cross modal" in intent.lower() or "fusion" in intent.lower() or "看图说话" in intent or "视觉语音" in intent or "语音执行" in intent:
        print(f"[跨模态深度融合引擎] 正在处理多模态融合请求...", file=sys.stderr)
        script_path = os.path.join(SCRIPTS, "cross_modal_fusion_engine.py")
        # 参数处理
        cmd_args = []
        for arg in sys.argv[1:]:
            if arg in ["跨模态", "多模态融合", "cross modal", "fusion", "看图说话", "视觉语音", "语音执行"]:
                continue
            cmd_args.append(arg)
        if not cmd_args:
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
