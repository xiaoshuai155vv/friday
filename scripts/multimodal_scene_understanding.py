#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
增强多模态场景理解与智能场景联动引擎

功能：
- 实现界面结构解析，识别屏幕布局和视觉元素
- 实现视觉元素识别（按钮、输入框、图片、列表等）
- 实现文本-图像关系理解（识别界面中的文字与图像的关系）
- 实现场景联动推荐（根据当前场景理解结果推荐相关场景计划）
- 实现跨场景上下文传递（完成一个场景后自动衔接下一相关场景）
- 集成到 do.py 支持「场景理解」「场景联动」「智能场景推荐」等关键词触发

使用方式：
- python multimodal_scene_understanding.py analyze <截图路径> - 分析界面结构
- python multimodal_scene_understanding.py recommend <场景类型> - 推荐相关场景计划
- python multimodal_scene_understanding.py link <当前场景> - 联动下一相关场景
- python multimodal_scene_understanding.py context - 获取跨场景上下文
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# 确保 scripts 目录在路径中
SCRIPT_DIR = Path(__file__).parent
RUNTIME_DIR = SCRIPT_DIR.parent / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"
ASSETS_DIR = SCRIPT_DIR.parent / "assets"
PLANS_DIR = ASSETS_DIR / "plans"


def ensure_dir(path):
    """确保目录存在"""
    path = Path(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    return path


def load_plans():
    """加载所有场景计划"""
    plans = []
    if PLANS_DIR.exists():
        for plan_file in PLANS_DIR.glob("*.json"):
            try:
                with open(plan_file, "r", encoding="utf-8") as f:
                    plan_data = json.load(f)
                    # 兼容数组格式的计划文件
                    if isinstance(plan_data, list):
                        plan_data = {"name": plan_file.stem, "steps": plan_data}
                    plan_data["_file"] = plan_file.name
                    plans.append(plan_data)
            except Exception as e:
                print(f"加载计划失败 {plan_file.name}: {e}", file=sys.stderr)
    return plans


def analyze_interface_structure(screenshot_path):
    """分析界面结构，识别布局和元素"""
    if not os.path.exists(screenshot_path):
        return {"error": f"截图文件不存在: {screenshot_path}"}

    # 使用 vision 分析界面结构
    vision_script = SCRIPT_DIR / "vision_proxy.py"
    if not vision_script.exists():
        return {"error": "vision_proxy.py 不存在"}

    # 构建分析提示
    analysis_prompt = """分析这张截图中的界面结构。请识别：
1. 界面类型（网页、桌面应用、系统界面等）
2. 主要布局区域（顶部菜单栏、侧边栏、主内容区、底部状态栏等）
3. 视觉元素（按钮、输入框、列表、图片、链接等）
4. 界面中的文字内容（标题、标签、按钮文字等）
5. 元素的相对位置关系

请用JSON格式返回分析结果：
{
    "interface_type": "...",
    "layout_regions": [{"name": "...", "position": "top/left/center/right/bottom", "description": "..."}],
    "visual_elements": [{"type": "button/input/link/image/list/...", "text": "...", "position": "..."}],
    "main_content": "界面主要内容和功能",
    "confidence": 0.0-1.0
}"""

    try:
        result = subprocess.run(
            [sys.executable, str(vision_script), screenshot_path, analysis_prompt],
            capture_output=True,
            timeout=60
        )

        stdout_text = ""
        if result.stdout:
            try:
                stdout_text = result.stdout.decode("utf-8", errors="ignore")
            except Exception:
                stdout_text = str(result.stdout)

        if result.returncode == 0 and stdout_text.strip():
            try:
                # 尝试解析 JSON 结果
                analysis_result = json.loads(stdout_text.strip())
                return analysis_result
            except json.JSONDecodeError:
                # 如果不是 JSON，返回原始文本
                return {"analysis": stdout_text.strip(), "raw": True}
        else:
            stderr_text = ""
            if result.stderr:
                try:
                    stderr_text = result.stderr.decode("utf-8", errors="ignore")
                except Exception:
                    stderr_text = str(result.stderr)
            return {"error": f"分析失败: {stderr_text}"}
    except Exception as e:
        return {"error": str(e)}


def understand_text_image_relationship(screenshot_path):
    """理解文本与图像的关系"""
    if not os.path.exists(screenshot_path):
        return {"error": f"截图文件不存在: {screenshot_path}"}

    vision_script = SCRIPT_DIR / "vision_proxy.py"

    relationship_prompt = """分析这张截图中的文字与图像的关系：
1. 哪些文字是按钮/链接的标签？与对应的点击区域是什么关系？
2. 哪些图像是图标？它们旁边通常有什么文字说明？
3. 哪些是装饰性图像/背景？
4. 文字和图像是如何组合传达信息的？

请用JSON格式返回：
{
    "text_image_pairs": [{"text": "...", "related_image": "...", "relationship": "label/icon/decorative/..."}],
    "clickable_elements": [{"text": "...", "coordinates": [x, y], "type": "button/link/icon/..."}],
    "information_flow": "文字和图像如何配合传达信息"
}"""

    try:
        result = subprocess.run(
            [sys.executable, str(vision_script), screenshot_path, relationship_prompt],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0 and result.stdout.strip():
            try:
                return json.loads(result.stdout.strip())
            except json.JSONDecodeError:
                return {"analysis": result.stdout.strip(), "raw": True}
        else:
            return {"error": f"分析失败: {result.stderr}"}
    except Exception as e:
        return {"error": str(e)}


def recommend_related_scenarios(current_scene, analysis_result=None):
    """根据当前场景推荐相关场景计划"""
    plans = load_plans()

    if not plans:
        return {"recommendations": [], "reason": "未找到可用的场景计划"}

    # 提取当前场景的关键特征
    current_features = extract_scene_features(current_scene, analysis_result)

    # 计算与各场景的相关性
    scored_plans = []
    for plan in plans:
        plan_features = extract_plan_features(plan)
        similarity = calculate_similarity(current_features, plan_features)
        scored_plans.append({
            "plan_name": plan.get("name", plan.get("_file", "未知")),
            "file": plan.get("_file", ""),
            "triggers": plan.get("triggers", []),
            "description": plan.get("description", ""),
            "relevance_score": similarity,
            "reason": generate_recommendation_reason(current_scene, plan)
        })

    # 按相关性排序
    scored_plans.sort(key=lambda x: x["relevance_score"], reverse=True)

    # 返回前5个推荐
    return {
        "current_scene": current_scene,
        "recommendations": scored_plans[:5],
        "analysis": analysis_result if analysis_result else "未提供详细分析"
    }


def extract_scene_features(scene, analysis_result):
    """提取场景特征"""
    features = {
        "keywords": [],
        "interface_type": "",
        "elements": []
    }

    if analysis_result and isinstance(analysis_result, dict):
        if "interface_type" in analysis_result:
            features["interface_type"] = analysis_result["interface_type"]
        if "visual_elements" in analysis_result:
            features["elements"] = [e.get("type", "") for e in analysis_result["visual_elements"]]
        if "main_content" in analysis_result:
            features["keywords"] = analysis_result["main_content"].split()[:10]

    # 从场景名称提取关键词
    features["keywords"].extend(scene.split())

    return features


def extract_plan_features(plan):
    """提取计划特征"""
    features = {
        "keywords": [],
        "triggers": plan.get("triggers", []),
        "description": plan.get("description", ""),
        "steps": len(plan.get("steps", []))
    }

    # 从触发词和描述中提取关键词
    if "triggers" in plan:
        for trigger in plan["triggers"]:
            features["keywords"].extend(trigger.split())
    if "description" in plan:
        features["keywords"].extend(plan["description"].split())

    return features


def calculate_similarity(features1, features2):
    """计算场景与计划的相似度"""
    score = 0.0

    # 关键词重叠
    keywords1 = set(features1.get("keywords", []))
    keywords2 = set(features2.get("keywords", []))
    if keywords1 and keywords2:
        overlap = len(keywords1 & keywords2)
        score += overlap * 0.2

    # 触发词匹配
    triggers = features2.get("triggers", [])
    for trigger in triggers:
        if any(kw in trigger.lower() for kw in features1.get("keywords", [])):
            score += 0.3

    # 界面类型匹配
    if features1.get("interface_type") and features2.get("description", "").lower():
        if features1["interface_type"].lower() in features2["description"].lower():
            score += 0.2

    return min(score, 1.0)


def generate_recommendation_reason(current_scene, plan):
    """生成推荐原因"""
    triggers = plan.get("triggers", [])
    if triggers:
        return f"与当前场景「{current_scene}」相关，可通过「{triggers[0]}」触发"
    return f"可作为当前场景的补充或后续步骤"


def link_next_scene(current_scene, context=None):
    """联动下一相关场景"""
    # 先获取推荐
    recommendations = recommend_related_scenarios(current_scene)

    if not recommendations.get("recommendations"):
        return {
            "current_scene": current_scene,
            "next_scene": None,
            "reason": "未找到相关联的场景"
        }

    # 选择最相关的场景
    best_recommendation = recommendations["recommendations"][0]

    # 保存跨场景上下文
    save_context(current_scene, best_recommendation["plan_name"], context)

    return {
        "current_scene": current_scene,
        "next_scene": best_recommendation["plan_name"],
        "next_file": best_recommendation["file"],
        "reason": best_recommendation["reason"],
        "all_recommendations": recommendations["recommendations"]
    }


def save_context(from_scene, to_scene, additional_context=None):
    """保存跨场景上下文"""
    ensure_dir(STATE_DIR)

    context_file = STATE_DIR / "scene_linkage_context.json"
    context_data = {
        "from_scene": from_scene,
        "to_scene": to_scene,
        "timestamp": datetime.now().isoformat(),
        "additional_context": additional_context or {}
    }

    try:
        if context_file.exists():
            with open(context_file, "r", encoding="utf-8") as f:
                contexts = json.load(f)
        else:
            contexts = []

        contexts.append(context_data)

        # 保留最近10条上下文
        contexts = contexts[-10:]

        with open(context_file, "w", encoding="utf-8") as f:
            json.dump(contexts, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存上下文失败: {e}", file=sys.stderr)


def get_context():
    """获取跨场景上下文"""
    context_file = STATE_DIR / "scene_linkage_context.json"

    if not context_file.exists():
        return {"contexts": [], "message": "无历史上下文"}

    try:
        with open(context_file, "r", encoding="utf-8") as f:
            contexts = json.load(f)
        return {"contexts": contexts}
    except Exception as e:
        return {"error": str(e)}


def analyze_and_recommend(screenshot_path):
    """分析截图并推荐相关场景"""
    # 分析界面结构
    analysis = analyze_interface_structure(screenshot_path)

    # 如果分析失败，返回错误
    if "error" in analysis:
        return analysis

    # 识别界面类型作为当前场景
    interface_type = analysis.get("interface_type", "未知界面")
    main_content = analysis.get("main_content", "")

    current_scene = f"{interface_type}: {main_content}" if main_content else interface_type

    # 推荐相关场景
    recommendations = recommend_related_scenarios(current_scene, analysis)

    return {
        "scene": current_scene,
        "analysis": analysis,
        "recommendations": recommendations.get("recommendations", []),
        "reason": f"基于界面类型「{interface_type}」和内容「{main_content}」推荐"
    }


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\n用法示例:")
        print("  python multimodal_scene_understanding.py analyze <截图路径>")
        print("  python multimodal_scene_understanding.py recommend <场景类型>")
        print("  python multimodal_scene_understanding.py link <当前场景>")
        print("  python multimodal_scene_understanding.py context")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "analyze":
        # 分析界面结构
        if len(sys.argv) < 3:
            print("用法: python multimodal_scene_understanding.py analyze <截图路径>")
            sys.exit(1)
        screenshot_path = sys.argv[2]
        result = analyze_and_recommend(screenshot_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "understand":
        # 理解文本图像关系
        if len(sys.argv) < 3:
            print("用法: python multimodal_scene_understanding.py understand <截图路径>")
            sys.exit(1)
        screenshot_path = sys.argv[2]
        result = understand_text_image_relationship(screenshot_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "recommend":
        # 推荐相关场景
        if len(sys.argv) < 3:
            print("用法: python multimodal_scene_understanding.py recommend <场景类型>")
            sys.exit(1)
        scene_type = " ".join(sys.argv[2:])
        result = recommend_related_scenarios(scene_type)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "link":
        # 联动下一场景
        if len(sys.argv) < 3:
            print("用法: python multimodal_scene_understanding.py link <当前场景>")
            sys.exit(1)
        current_scene = " ".join(sys.argv[2:])
        result = link_next_scene(current_scene)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "context":
        # 获取跨场景上下文
        result = get_context()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()