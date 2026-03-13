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
