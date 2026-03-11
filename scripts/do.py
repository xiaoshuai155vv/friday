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
        print("用法: do.py 自拍|打开摄像头|截图|已安装应用|打开网易云音乐|...|剪贴板读|防休眠|...|run <脚本名> [参数...]", file=sys.stderr)
        sys.exit(1)

    # 检查是否请求自主决策/系统建议
    intent_with_args = " ".join(sys.argv[1:]).lower()
    autonomous_keywords = ["自主决策", "系统建议", "主动建议", "ai建议", "智能建议", "给我建议"]
    for keyword in autonomous_keywords:
        if keyword in intent_with_args:
            print(f"[自主决策] 检测到请求: {keyword}", file=sys.stderr)
            ret = _run_autonomous_decision()
            sys.exit(ret)

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
                    trend_data = json.load(f)
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
        msg = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "FRIDAY"
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "notification_tool.py"), "show", msg], cwd=PROJECT)
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
        # 未知意图时，使用智能推荐系统 + 前台窗口感知
        import json
        import glob

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

if __name__ == "__main__":
    main()
