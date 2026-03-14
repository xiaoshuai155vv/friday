#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能跨场景协同推理引擎 (Cross-Scene Reasoning Engine)
版本: 1.0.0

让系统能够理解跨多个场景的复杂任务，自动识别场景间的关联与依赖，
协同多个引擎协同推理和执行，形成从单场景到跨场景理解的范式升级。

功能：
1. 多场景关联分析 - 识别任务涉及的多个场景及其关系
2. 跨场景依赖推理 - 分析场景间的数据流和执行顺序
3. 协同推理执行 - 多引擎协同完成跨场景任务
4. 跨场景状态传递 - 保持上下文一致性
"""

import json
import os
import sys
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE_DIR = PROJECT_ROOT / "runtime" / "state"
SCENES_DIR = PROJECT_ROOT / "assets" / "plans"


class CrossSceneReasoningEngine:
    """智能跨场景协同推理引擎"""

    def __init__(self):
        self.name = "跨场景协同推理引擎"
        self.version = "1.0.0"
        self.execution_history = []
        self.context_store = {}  # 跨场景上下文存储

        # 场景类型定义
        self.scene_types = {
            "ihaier": {"keywords": ["办公平台", "iHaier", "企业微信", "消息", "联系人"], "type": "enterprise_app"},
            "browser": {"keywords": ["浏览器", "Chrome", "Edge", "打开网页", "访问"], "type": "web"},
            "music": {"keywords": ["音乐", "播放", "歌曲", "网易云", "QQ音乐"], "type": "media"},
            "file": {"keywords": ["文件", "文件夹", "打开文件", "保存"], "type": "system"},
            "email": {"keywords": ["邮件", "发邮件", "收件箱", "Outlook"], "type": "communication"},
            "document": {"keywords": ["文档", "Word", "Excel", "PPT", "编辑"], "type": "office"},
            "chat": {"keywords": ["微信", "QQ", "聊天", "发消息"], "type": "communication"},
            "system": {"keywords": ["设置", "控制面板", "系统"], "type": "system"},
        }

        # 场景依赖关系图
        self.dependency_graph = {
            "ihaier": {"requires": [], "provides": ["contact_info", "message_content", "approval_data"]},
            "browser": {"requires": [], "provides": ["web_content", "search_result"]},
            "music": {"requires": [], "provides": ["music_control"]},
            "file": {"requires": [], "provides": ["file_path", "file_content"]},
            "email": {"requires": ["file", "browser"], "provides": ["email_content", "attachment"]},
            "document": {"requires": ["file"], "provides": ["document_content"]},
            "chat": {"requires": [], "provides": ["message_content"]},
            "system": {"requires": [], "provides": ["system_settings"]},
        }

    def analyze_scenes(self, user_request: str) -> Dict[str, Any]:
        """分析用户请求涉及哪些场景"""
        scenes_detected = []
        request_lower = user_request.lower()

        for scene_name, scene_info in self.scene_types.items():
            for keyword in scene_info["keywords"]:
                if keyword.lower() in request_lower:
                    scenes_detected.append({
                        "name": scene_name,
                        "type": scene_info["type"],
                        "confidence": request_lower.count(keyword.lower()) + 1,
                        "keyword_matched": keyword
                    })
                    break

        # 推断隐含场景
        if "发" in user_request and ("消息" in user_request or "邮件" in user_request):
            if not any(s["name"] == "chat" for s in scenes_detected):
                scenes_detected.append({
                    "name": "implicit_chat",
                    "type": "communication",
                    "confidence": 0.5,
                    "keyword_matched": "隐含推断"
                })

        return {
            "scenes": scenes_detected,
            "scene_count": len(scenes_detected),
            "is_cross_scene": len(scenes_detected) > 1
        }

    def analyze_dependencies(self, scenes: List[Dict]) -> Dict[str, Any]:
        """分析场景间的依赖关系"""
        scene_names = [s["name"] for s in scenes]
        dependencies = []
        execution_order = []

        # 拓扑排序确定执行顺序
        remaining = set(scene_names)
        while remaining:
            # 找到没有未处理依赖的场景
            ready = []
            for scene in remaining:
                deps = self.dependency_graph.get(scene, {}).get("requires", [])
                if all(d not in remaining for d in deps):
                    ready.append(scene)

            if not ready:
                # 循环依赖，选择一个继续
                ready = [list(remaining)[0]]

            execution_order.extend(ready)
            remaining -= set(ready)

        # 分析数据流
        data_flows = []
        for i, scene in enumerate(execution_order):
            provides = self.dependency_graph.get(scene, {}).get("provides", [])
            for j, other_scene in enumerate(execution_order[i+1:], i+1):
                requires = self.dependency_graph.get(other_scene, {}).get("requires", [])
                if scene in requires:
                    data_flows.append({
                        "from_scene": scene,
                        "to_scene": other_scene,
                        "data_type": provides[0] if provides else "unknown"
                    })

        return {
            "execution_order": execution_order,
            "data_flows": data_flows,
            "total_dependencies": len(data_flows)
        }

    def reason_task_flow(self, user_request: str) -> Dict[str, Any]:
        """推理任务流程 - 主要入口"""
        # 1. 场景分析
        scene_analysis = self.analyze_scenes(user_request)

        if not scene_analysis["scenes"]:
            return {
                "success": False,
                "reason": "未识别到具体场景",
                "request": user_request
            }

        # 2. 依赖分析
        dependency_analysis = self.analyze_dependencies(scene_analysis["scenes"])

        # 3. 生成执行计划
        execution_plan = self._generate_execution_plan(
            user_request,
            scene_analysis,
            dependency_analysis
        )

        return {
            "success": True,
            "request": user_request,
            "scenes": scene_analysis["scenes"],
            "is_cross_scene": scene_analysis["is_cross_scene"],
            "execution_order": dependency_analysis["execution_order"],
            "data_flows": dependency_analysis["data_flows"],
            "execution_plan": execution_plan,
            "timestamp": datetime.now().isoformat()
        }

    def _generate_execution_plan(
        self,
        user_request: str,
        scene_analysis: Dict,
        dependency_analysis: Dict
    ) -> List[Dict[str, Any]]:
        """生成执行计划"""
        plan = []
        execution_order = dependency_analysis["execution_order"]

        for i, scene in enumerate(execution_order):
            step = {
                "step_number": i + 1,
                "scene": scene,
                "action": self._get_default_action(scene, user_request),
                "estimated_duration": self._estimate_duration(scene),
                "required_context": dependency_analysis["data_flows"][i-1]["data_type"] if i > 0 and i-1 < len(dependency_analysis["data_flows"]) else None
            }
            plan.append(step)

        return plan

    def _get_default_action(self, scene: str, user_request: str) -> str:
        """获取场景的默认动作"""
        action_map = {
            "ihaier": "打开企业应用并操作",
            "browser": "打开浏览器访问",
            "music": "播放音乐",
            "file": "操作文件",
            "email": "发送邮件",
            "document": "编辑文档",
            "chat": "发送消息",
            "system": "打开系统设置",
            "implicit_chat": "发送消息"
        }
        return action_map.get(scene, f"操作{scene}")

    def _estimate_duration(self, scene: str) -> int:
        """估算场景执行时长（秒）"""
        duration_map = {
            "ihaier": 15,
            "browser": 10,
            "music": 5,
            "file": 5,
            "email": 10,
            "document": 15,
            "chat": 8,
            "system": 10,
            "implicit_chat": 8
        }
        return duration_map.get(scene, 10)

    def execute_cross_scene_task(
        self,
        user_request: str,
        execute: bool = False
    ) -> Dict[str, Any]:
        """执行跨场景任务"""
        # 1. 推理任务流程
        task_flow = self.reason_task_flow(user_request)

        if not task_flow["success"]:
            return task_flow

        # 2. 记录到执行历史
        execution_record = {
            "request": user_request,
            "timestamp": datetime.now().isoformat(),
            "scenes": task_flow["scenes"],
            "execution_order": task_flow["execution_order"],
            "executed": execute
        }
        self.execution_history.append(execution_record)

        # 3. 如果需要执行
        if execute:
            return self._execute_plan(task_flow["execution_plan"], user_request)

        return task_flow

    def _execute_plan(self, plan: List[Dict], user_request: str) -> Dict[str, Any]:
        """执行计划（返回建议，实际执行由调用者完成）"""
        suggestions = []
        for step in plan:
            suggestions.append({
                "step": step["step_number"],
                "action": f"执行场景: {step['scene']}",
                "details": step["action"],
                "estimated_time": step["estimated_duration"]
            })

        return {
            "success": True,
            "message": "已生成执行计划，建议按以下步骤执行：",
            "execution_suggestions": suggestions,
            "user_request": user_request,
            "note": "此为计划建议，实际执行需要通过 do.py 或 run_plan 调用各引擎"
        }

    def get_scene_relationships(self, scene_name: str) -> Dict[str, Any]:
        """获取特定场景的关系信息"""
        if scene_name not in self.dependency_graph:
            return {"error": f"场景 {scene_name} 不存在"}

        info = self.dependency_graph[scene_name]
        return {
            "scene": scene_name,
            "requires": info.get("requires", []),
            "provides": info.get("provides", []),
            "related_scenes": [
                s for s, v in self.dependency_graph.items()
                if scene_name in v.get("requires", []) or scene_name in v.get("provides", [])
            ]
        }

    def get_execution_history(self, limit: int = 10) -> List[Dict]:
        """获取执行历史"""
        return self.execution_history[-limit:]

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "name": self.name,
            "version": self.version,
            "scenes_supported": list(self.scene_types.keys()),
            "total_executions": len(self.execution_history),
            "context_count": len(self.context_store),
            "capabilities": [
                "多场景关联分析",
                "跨场景依赖推理",
                "协同推理执行",
                "跨场景状态传递",
                "执行计划生成"
            ]
        }

    def analyze_request_complexity(self, user_request: str) -> Dict[str, Any]:
        """分析请求复杂度"""
        scenes = self.analyze_scenes(user_request)
        length = len(user_request)

        complexity_score = 0
        factors = []

        # 场景数量
        scene_count = len(scenes["scenes"])
        complexity_score += scene_count * 2
        factors.append(f"场景数量: {scene_count}")

        # 请求长度
        if length > 50:
            complexity_score += 2
            factors.append("请求较长，可能包含多个子任务")

        # 关键词检测
        complex_keywords = ["然后", "再", "接着", "同时", "并且", "或者", "或者"]
        for kw in complex_keywords:
            if kw in user_request:
                complexity_score += 1
                factors.append(f"包含复合词: {kw}")

        # 判断复杂度等级
        if complexity_score >= 5:
            complexity = "high"
        elif complexity_score >= 2:
            complexity = "medium"
        else:
            complexity = "low"

        return {
            "complexity": complexity,
            "score": complexity_score,
            "factors": factors,
            "scenes_detected": scene_count,
            "recommendation": "建议使用跨场景协同推理" if complexity != "low" else "单场景处理即可"
        }


def main():
    """主函数 - 支持命令行调用"""
    engine = CrossSceneReasoningEngine()

    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "用法: python cross_scene_reasoning_engine.py <命令> [参数]",
            "commands": [
                "analyze <用户请求> - 分析请求涉及的场景",
                "reason <用户请求> - 推理任务流程",
                "execute <用户请求> - 生成执行计划",
                "status - 获取引擎状态",
                "history - 获取执行历史",
                "complexity <用户请求> - 分析请求复杂度",
                "relationships <场景名> - 获取场景关系"
            ]
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    command = sys.argv[1]

    try:
        if command == "analyze" and len(sys.argv) > 2:
            user_request = " ".join(sys.argv[2:])
            result = engine.analyze_scenes(user_request)
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif command == "reason" and len(sys.argv) > 2:
            user_request = " ".join(sys.argv[2:])
            result = engine.reason_task_flow(user_request)
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif command == "execute" and len(sys.argv) > 2:
            user_request = " ".join(sys.argv[2:])
            result = engine.execute_cross_scene_task(user_request, execute=False)
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif command == "status":
            print(json.dumps(engine.get_status(), ensure_ascii=False, indent=2))

        elif command == "history":
            print(json.dumps(engine.get_execution_history(), ensure_ascii=False, indent=2))

        elif command == "complexity" and len(sys.argv) > 2:
            user_request = " ".join(sys.argv[2:])
            result = engine.analyze_request_complexity(user_request)
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif command == "relationships" and len(sys.argv) > 2:
            scene_name = sys.argv[2]
            result = engine.get_scene_relationships(scene_name)
            print(json.dumps(result, ensure_ascii=False, indent=2))

        else:
            print(json.dumps({"error": f"未知命令: {command}"}, ensure_ascii=False, indent=2))
            sys.exit(1)

    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()