#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能自适应场景选择引擎
让系统能够基于实时上下文（用户行为、系统状态、时间、情绪、历史）深度理解当前情境，
主动选择最合适的场景计划并执行，实现真正的「懂用户」式主动服务
"""
import os
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import subprocess
import sys


# 数据存储路径
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runtime', 'state')
CONTEXT_DATA_FILE = os.path.join(DATA_DIR, 'adaptive_context_data.json')
SCENE_SELECTION_LOG_FILE = os.path.join(DATA_DIR, 'scene_selection_log.json')
USER_HISTORY_FILE = os.path.join(DATA_DIR, 'user_behavior_history.json')


@dataclass
class ContextSnapshot:
    """上下文快照"""
    timestamp: str
    time_period: str  # 早晨/上午/中午/下午/傍晚/晚上/深夜
    weekday: str  # 工作日/周末
    system_state: Dict[str, Any] = field(default_factory=dict)
    recent_behaviors: List[str] = field(default_factory=list)
    active_window: str = ""
    emotion_hint: str = ""
    location: str = ""  # 办公室/家里/外出


@dataclass
class SceneCandidate:
    """场景候选"""
    scene_name: str
    scene_path: str
    match_score: float  # 0-1
    match_reasons: List[str] = field(default_factory=list)
    auto_execute: bool = False


@dataclass
class SelectionDecision:
    """选择决策"""
    selected_scene: Optional[str] = None
    confidence: float = 0.0
    candidates: List[SceneCandidate] = field(default_factory=list)
    reasoning: str = ""
    should_recommend: bool = False
    recommendation_text: str = ""


class ContextCollector:
    """上下文收集器"""

    def __init__(self):
        self.data_file = CONTEXT_DATA_FILE
        self._ensure_data_dir()
        self._load_context()

    def _ensure_data_dir(self):
        """确保数据目录存在"""
        os.makedirs(DATA_DIR, exist_ok=True)

    def _load_context(self):
        """加载上下文数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.context_data = json.load(f)
            except:
                self.context_data = {}
        else:
            self.context_data = {}

    def collect_current_context(self) -> ContextSnapshot:
        """收集当前上下文"""
        now = datetime.now()
        hour = now.hour

        # 时间段判断
        if 5 <= hour < 9:
            time_period = "早晨"
        elif 9 <= hour < 12:
            time_period = "上午"
        elif 12 <= hour < 14:
            time_period = "中午"
        elif 14 <= hour < 18:
            time_period = "下午"
        elif 18 <= hour < 20:
            time_period = "傍晚"
        elif 20 <= hour < 23:
            time_period = "晚上"
        else:
            time_period = "深夜"

        # 工作日判断
        weekday = "周末" if now.weekday() >= 5 else "工作日"

        # 收集系统状态
        system_state = self._collect_system_state()

        # 收集最近行为
        recent_behaviors = self._collect_recent_behaviors()

        # 获取活跃窗口
        active_window = self._get_active_window()

        # 推断情绪
        emotion_hint = self._infer_emotion(time_period, system_state, recent_behaviors)

        return ContextSnapshot(
            timestamp=now.isoformat(),
            time_period=time_period,
            weekday=weekday,
            system_state=system_state,
            recent_behaviors=recent_behaviors,
            active_window=active_window,
            emotion_hint=emotion_hint,
            location=system_state.get("location", "")
        )

    def _collect_system_state(self) -> Dict[str, Any]:
        """收集系统状态"""
        state = {"cpu": 0, "memory": 0, "battery": 100, "location": ""}

        # 尝试获取系统信息
        try:
            # CPU使用率
            result = subprocess.run(
                ["wmic", "cpu", "get", "loadpercentage"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    state["cpu"] = int(lines[1].strip()) if lines[1].strip().isdigit() else 0
        except:
            pass

        # 内存使用
        try:
            result = subprocess.run(
                ["wmic", "OS", "get", "FreePhysicalMemory,TotalVisibleMemorySize", "/format:list"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                free = 0
                total = 0
                for line in result.stdout.split('\n'):
                    if 'FreePhysicalMemory' in line:
                        free = int(line.split('=')[1].strip()) if '=' in line else 0
                    if 'TotalVisibleMemorySize' in line:
                        total = int(line.split('=')[1].strip()) if '=' in line else 0
                if total > 0:
                    state["memory"] = int((1 - free / total) * 100)
        except:
            pass

        # 电池状态
        try:
            result = subprocess.run(
                ["wmic", "Battery", "get", "EstimatedChargeRemaining", "/format:list"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and "EstimatedChargeRemaining" in result.stdout:
                battery = result.stdout.split('=')[1].strip()
                state["battery"] = int(battery) if battery.isdigit() else 100
        except:
            pass

        return state

    def _collect_recent_behaviors(self) -> List[str]:
        """收集最近行为"""
        behaviors = []
        history_file = USER_HISTORY_FILE

        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    # 获取最近的行为
                    recent = history.get("recent_behaviors", [])[-10:]
                    behaviors = [b.get("action", "") for b in recent if b.get("action")]
            except:
                pass

        return behaviors

    def _get_active_window(self) -> str:
        """获取活跃窗口标题"""
        try:
            # 使用 PowerShell 获取顶层窗口标题
            script = '''
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll", CharSet = CharSet.Auto)]
    public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);
}
"@
$hwnd = [Win32]::GetForegroundWindow()
$sb = New-Object System.Text.StringBuilder(256)
[Win32]::GetWindowText($hwnd, $sb, 256) | Out-Null
$sb.ToString()
'''
            result = subprocess.run(
                ["powershell", "-Command", script],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except:
            pass

        return ""

    def _infer_emotion(self, time_period: str, system_state: Dict, behaviors: List[str]) -> str:
        """推断情绪状态"""
        # 基于时间和行为模式推断情绪
        if time_period in ["深夜", "早晨"]:
            return "清醒" if behaviors else "安静"
        elif time_period == "中午":
            return "活跃"
        elif time_period == "下午":
            return "专注" if system_state.get("cpu", 0) > 50 else "放松"
        elif time_period == "晚上":
            return "放松"
        return "平静"

    def save_context(self, context: ContextSnapshot):
        """保存上下文"""
        self.context_data["last_context"] = asdict(context)
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.context_data, f, ensure_ascii=False, indent=2)
        except:
            pass


class SceneMatcher:
    """场景匹配器"""

    # 场景与上下文模式的映射
    SCENE_PATTERNS = {
        "工作模式": {
            "keywords": ["工作", "办公", "写代码", "写文档", "处理文件"],
            "time_periods": ["上午", "下午", "中午"],
            "weekdays": ["工作日"],
            "system_states": ["正常", "忙碌"],
            "emotions": ["专注", "清醒"],
        },
        "学习模式": {
            "keywords": ["学习", "阅读", "看文档", "教程", "课程"],
            "time_periods": ["早晨", "上午", "下午", "晚上"],
            "weekdays": ["工作日", "周末"],
            "system_states": ["正常"],
            "emotions": ["专注", "平静"],
        },
        "休息模式": {
            "keywords": ["休息", "放松", "娱乐", "看视频", "听音乐"],
            "time_periods": ["晚上", "中午"],
            "weekdays": ["工作日", "周末"],
            "system_states": ["放松"],
            "emotions": ["放松", "平静"],
        },
        "专注模式": {
            "keywords": ["专注", "集中", "不打扰", "番茄钟"],
            "time_periods": ["上午", "下午"],
            "weekdays": ["工作日"],
            "system_states": ["专注"],
            "emotions": ["专注", "清醒"],
        },
        "早晨准备": {
            "keywords": ["早上", "早晨", "开机", "准备"],
            "time_periods": ["早晨"],
            "weekdays": ["工作日", "周末"],
            "system_states": ["正常"],
            "emotions": ["清醒", "安静"],
        },
        "晚间总结": {
            "keywords": ["晚上", "总结", "回顾", "收尾"],
            "time_periods": ["晚上", "深夜"],
            "weekdays": ["工作日"],
            "system_states": ["正常", "放松"],
            "emotions": ["放松", "平静"],
        },
    }

    def __init__(self):
        self.plans_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..', 'assets', 'plans'
        )

    def load_available_scenes(self) -> List[Dict[str, str]]:
        """加载可用场景"""
        scenes = []

        if not os.path.exists(self.plans_dir):
            return scenes

        for filename in os.listdir(self.plans_dir):
            if filename.endswith('.json'):
                scene_path = os.path.join(self.plans_dir, filename)
                try:
                    with open(scene_path, 'r', encoding='utf-8') as f:
                        scene_data = json.load(f)
                        # 处理 triggers 可能是单个字符串或列表
                        triggers = scene_data.get("triggers", [])
                        if isinstance(triggers, str):
                            triggers = [triggers]
                        # 也检查 trigger 字段
                        trigger = scene_data.get("trigger", "")
                        if trigger and trigger not in triggers:
                            triggers.append(trigger)

                        scenes.append({
                            "name": scene_data.get("name", filename[:-5]),
                            "path": scene_path,
                            "description": scene_data.get("description", ""),
                            "triggers": triggers,
                            "steps": scene_data.get("steps", [])
                        })
                except:
                    pass

        return scenes

    def calculate_match_score(self, scene: Dict[str, Any], context: ContextSnapshot) -> tuple:
        """计算场景与上下文的匹配分数"""
        score = 0.0
        reasons = []

        # 场景名称关键词
        scene_name = scene.get("name", "").lower()
        scene_description = scene.get("description", "").lower()
        scene_triggers = [t.lower() for t in scene.get("triggers", [])]

        # 合并所有关键词
        all_keywords = scene_triggers + scene_name.split() + scene_description.split()

        # 基于场景名称和触发词的基本匹配
        if any(kw in ["工作", "办公", "写代码", "写文档", "代码"] for kw in all_keywords):
            if context.time_period in ["上午", "下午"] and context.weekday == "工作日":
                score += 0.5
                reasons.append("工作场景匹配工作日工作时间")
        elif any(kw in ["休息", "放松", "娱乐", "看视频", "听音乐", "音乐", "电影", "播放"] for kw in all_keywords):
            if context.time_period in ["晚上", "中午", "傍晚"]:
                score += 0.5
                reasons.append("娱乐场景匹配休息时间")
        elif any(kw in ["学习", "阅读", "文档", "教程"] for kw in all_keywords):
            score += 0.3
            reasons.append("学习场景")

        # 活跃窗口匹配
        if context.active_window:
            active = context.active_window.lower()
            if any(kw in active for kw in ["code", "vs", "notepad", "word", "excel", "ppt", "文档", "编辑"]):
                if any(kw in all_keywords for kw in ["工作", "办公", "写代码", "代码", "文档"]):
                    score += 0.4
                    reasons.append(f"活跃窗口与工作场景匹配")
            elif any(kw in active for kw in ["music", "video", "player", "potplayer", "网易云", "音乐", "视频"]):
                if any(kw in all_keywords for kw in ["音乐", "视频", "娱乐", "播放"]):
                    score += 0.4
                    reasons.append(f"活跃窗口与娱乐场景匹配")

        # 关键词匹配
        keywords = scene.get("triggers", [])
        if keywords:
            # 检查最近行为是否包含关键词
            for behavior in context.recent_behaviors:
                for kw in keywords:
                    if kw.lower() in behavior.lower():
                        score += 0.2
                        reasons.append(f"行为匹配关键词: {kw}")

        # 时间段匹配
        time_patterns = self._get_scene_time_pattern(scene.get("name", ""))
        if time_patterns:
            for pattern in time_patterns:
                if pattern in context.time_period:
                    score += 0.3
                    reasons.append(f"时间匹配: {context.time_period}")
                    break

        # 工作日/周末匹配
        if "工作" in scene.get("name", "") and context.weekday == "工作日":
            score += 0.2
            reasons.append(f"工作日匹配")
        elif "周末" in scene.get("name", "").lower() or "休息" in scene.get("name", ""):
            if context.weekday == "周末" or context.time_period in ["晚上", "深夜"]:
                score += 0.2
                reasons.append(f"休息时间匹配")

        # 系统状态匹配
        if context.system_state.get("cpu", 0) > 70:
            if "忙碌" in scene.get("name", "").lower() or "工作" in scene.get("name", "").lower():
                score += 0.2
                reasons.append(f"系统忙碌状态匹配")

        # 情绪匹配
        if context.emotion_hint == "专注" and "专注" in scene.get("name", ""):
            score += 0.2
            reasons.append(f"情绪匹配: 专注")

        # 归一化分数
        score = min(score, 1.0)

        return score, reasons

    def _get_scene_time_pattern(self, scene_name: str) -> List[str]:
        """获取场景的典型时间段"""
        name = scene_name.lower()

        if any(kw in name for kw in ["早晨", "早上", "开机", "启动"]):
            return ["早晨"]
        elif any(kw in name for kw in ["上午", "工作", "办公"]):
            return ["上午", "下午"]
        elif any(kw in name for kw in ["午", "午餐", "休息"]):
            return ["中午"]
        elif any(kw in name for kw in ["晚", "总结", "收尾"]):
            return ["晚上", "深夜"]
        elif any(kw in name for kw in ["学习", "阅读"]):
            return ["早晨", "上午", "下午", "晚上"]

        return []


class AdaptiveSceneSelector:
    """自适应场景选择器"""

    def __init__(self):
        self.context_collector = ContextCollector()
        self.scene_matcher = SceneMatcher()
        self.selection_log_file = SCENE_SELECTION_LOG_FILE

    def analyze_and_select(self, user_input: str = "", force_recommend: bool = False) -> SelectionDecision:
        """分析上下文并选择最佳场景"""
        # 收集当前上下文
        context = self.context_collector.collect_current_context()
        self.context_collector.save_context(context)

        # 加载可用场景
        scenes = self.scene_matcher.load_available_scenes()

        if not scenes:
            return SelectionDecision(
                reasoning="未找到可用的场景计划",
                should_recommend=False
            )

        # 计算每个场景的匹配分数
        candidates = []
        for scene in scenes:
            score, reasons = self.scene_matcher.calculate_match_score(scene, context)
            if score > 0 or force_recommend:
                candidates.append(SceneCandidate(
                    scene_name=scene.get("name", ""),
                    scene_path=scene.get("path", ""),
                    match_score=score,
                    match_reasons=reasons
                ))

        # 按分数排序
        candidates.sort(key=lambda x: x.match_score, reverse=True)

        # 如果没有高匹配度的场景，给予基础分数让用户能看到推荐
        # 这样即使没有精确匹配也能提供场景选择
        if candidates and all(c.match_score < 0.1 for c in candidates):
            # 基于时间段的默认推荐 - 给予所有场景一个基础分数
            base_score = 0.3
            for candidate in candidates:
                candidate.match_score = base_score
                # 添加推荐原因
                if context.time_period in ["深夜", "晚上"]:
                    candidate.match_reasons.append(f"当前是{context.time_period}，推荐场景")
                elif context.time_period in ["上午", "下午"] and context.weekday == "工作日":
                    candidate.match_reasons.append(f"工作时间段，{context.weekday}可使用")
                else:
                    candidate.match_reasons.append(f"可用场景推荐")
            candidates.sort(key=lambda x: x.match_score, reverse=True)

        # 决策
        if not candidates or candidates[0].match_score < 0.1:
            return SelectionDecision(
                reasoning="当前上下文没有高匹配度的场景",
                candidates=candidates,
                should_recommend=False
            )

        top_candidate = candidates[0]

        # 决定是否自动执行
        should_execute = (
            force_recommend or
            top_candidate.match_score > 0.6 or
            (user_input and any(kw in user_input for kw in ["执行", "运行", "start"]))
        )

        # 构建推荐文本
        recommendation = ""
        if top_candidate.match_score > 0.5:
            recommendation = f"根据当前情境（{context.time_period} {context.weekday}），推荐场景「{top_candidate.scene_name}」"
            if top_candidate.match_reasons:
                recommendation += f"\n匹配原因: {'; '.join(top_candidate.match_reasons[:3])}"
            if should_execute:
                recommendation += "\n将自动执行该场景..."

        return SelectionDecision(
            selected_scene=top_candidate.scene_name if should_execute else None,
            confidence=top_candidate.match_score,
            candidates=candidates[:5],
            reasoning=f"选择场景「{top_candidate.scene_name}」，匹配度 {top_candidate.match_score:.1%}",
            should_recommend=top_candidate.match_score > 0.3,
            recommendation_text=recommendation
        )

    def log_selection(self, decision: SelectionDecision, context: ContextSnapshot):
        """记录选择决策"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "context": asdict(context),
            "decision": {
                "selected_scene": decision.selected_scene,
                "confidence": decision.confidence,
                "reasoning": decision.reasoning,
                "should_recommend": decision.should_recommend
            }
        }

        try:
            if os.path.exists(self.selection_log_file):
                with open(self.selection_log_file, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            else:
                log_data = {"selections": []}

            log_data["selections"].append(log_entry)

            # 只保留最近100条
            log_data["selections"] = log_data["selections"][-100:]

            with open(self.selection_log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
        except:
            pass


def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser(description="智能自适应场景选择引擎")
    parser.add_argument("action", nargs="?", default="analyze",
                        choices=["analyze", "select", "recommend", "context", "test"],
                        help="要执行的操作")
    parser.add_argument("--input", "-i", type=str, default="",
                        help="用户输入（可选）")
    parser.add_argument("--force", "-f", action="store_true",
                        help="强制推荐")
    parser.add_argument("--execute", "-e", action="store_true",
                        help="自动执行推荐的场景")

    args = parser.parse_args()

    selector = AdaptiveSceneSelector()

    if args.action == "analyze" or args.action == "select" or args.action == "recommend":
        decision = selector.analyze_and_select(
            user_input=args.input,
            force_recommend=args.force
        )

        # 输出推荐
        if decision.should_recommend and decision.recommendation_text:
            print(decision.recommendation_text)

        # 列出候选场景
        if decision.candidates:
            print("\n可用场景候选:")
            for i, candidate in enumerate(decision.candidates[:5], 1):
                print(f"  {i}. {candidate.scene_name} - 匹配度: {candidate.match_score:.1%}")
                if candidate.match_reasons:
                    print(f"     原因: {'; '.join(candidate.match_reasons[:2])}")

        # 自动执行
        if args.execute and decision.selected_scene:
            print(f"\n正在执行场景: {decision.selected_scene}")
            # 调用 run_plan 执行场景
            for candidate in decision.candidates:
                if candidate.scene_name == decision.selected_scene:
                    cmd = [sys.executable, "-c",
                           f"import subprocess; subprocess.run(['python', 'scripts/do.py', 'run_plan', '{candidate.scene_path}'])"]
                    subprocess.run(cmd, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    break

        print(f"\n决策: {decision.reasoning}")
        print(f"置信度: {decision.confidence:.1%}")

    elif args.action == "context":
        # 只收集和显示上下文
        context = selector.context_collector.collect_current_context()
        print("当前上下文:")
        print(f"  时间段: {context.time_period}")
        print(f"  日期类型: {context.weekday}")
        print(f"  系统状态: CPU {context.system_state.get('cpu', 0)}% | 内存 {context.system_state.get('memory', 0)}%")
        print(f"  活跃窗口: {context.active_window}")
        print(f"  情绪推断: {context.emotion_hint}")
        print(f"  最近行为: {', '.join(context.recent_behaviors[-5:]) if context.recent_behaviors else '无'}")

    elif args.action == "test":
        # 测试模式：模拟各种上下文
        print("=== 智能自适应场景选择引擎测试 ===\n")

        test_contexts = [
            ContextSnapshot(
                timestamp=datetime.now().isoformat(),
                time_period="上午",
                weekday="工作日",
                system_state={"cpu": 20, "memory": 40},
                recent_behaviors=["写代码", "处理文档"],
                active_window="VS Code",
                emotion_hint="专注"
            ),
            ContextSnapshot(
                timestamp=datetime.now().isoformat(),
                time_period="晚上",
                weekday="周末",
                system_state={"cpu": 10, "memory": 30},
                recent_behaviors=["看视频", "听音乐"],
                active_window="PotPlayer",
                emotion_hint="放松"
            ),
        ]

        for ctx in test_contexts:
            print(f"测试上下文: {ctx.time_period} {ctx.weekday}")
            print(f"  活跃窗口: {ctx.active_window}")
            print(f"  情绪: {ctx.emotion_hint}")
            print(f"  最近行为: {ctx.recent_behaviors}")

            decision = selector.analyze_and_select(force_recommend=True)
            if decision.candidates:
                print(f"  推荐场景: {decision.candidates[0].scene_name} ({decision.candidates[0].match_score:.1%})")
            print()


if __name__ == "__main__":
    main()