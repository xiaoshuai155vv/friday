#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能UI结构理解引擎

功能：
- 实现界面元素层级解析，识别父子元素关系
- 实现可交互组件识别（按钮、输入框、下拉菜单、复选框等）
- 实现精确点击坐标计算，结合UIA和vision
- 提供元素路径定位功能（类似CSS选择器）
- 集成到 do.py 支持「UI结构」「界面元素」「元素识别」等关键词触发

使用方式：
- python ui_structure_engine.py analyze - 分析当前屏幕UI结构
- python ui_structure_engine.py find <元素描述> - 查找指定元素
- python ui_structure_engine.py click <元素描述> - 查找并点击元素
- python ui_structure_engine.py interactive - 启动交互式UI探索模式

依赖：
- Windows UI Automation (UIA) - Windows内置
- vision_proxy.py - 多模态分析
"""

import os
import sys
import json
import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# 尝试导入 Windows UI Automation
try:
    import ctypes
    from ctypes import wintypes
    import comtypes
    from comtypes.client import GetObject
    UIA_AVAILABLE = True
except ImportError:
    UIA_AVAILABLE = False

# 路径配置
SCRIPT_DIR = Path(__file__).parent
RUNTIME_DIR = SCRIPT_DIR.parent / "runtime"
STATE_DIR = RUNTIME_DIR / "state"


def ensure_dir(path):
    """确保目录存在"""
    path = Path(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    return path


class UIAutomationBridge:
    """Windows UI Automation 桥接器"""

    def __init__(self):
        self.uia = None
        if UIA_AVAILABLE:
            try:
                self.uia = GetObject("uia:")
            except Exception:
                pass

    def is_available(self):
        """检查 UIA 是否可用"""
        return self.uia is not None

    def get_root_element(self):
        """获取桌面根元素"""
        if not self.uia:
            return None
        try:
            return self.uia.GetRootElement()
        except Exception:
            return None

    def get_foreground_window(self):
        """获取当前前景窗口"""
        if not self.uia:
            return None
        try:
            return self.uia.GetFocusedElement()
        except Exception:
            return None


class UIStructureEngine:
    """智能UI结构理解引擎"""

    # 可交互元素类型映射
    INTERACTIVE_TYPES = {
        'button': ['Button', 'RadioButton', 'CheckBox', 'SplitButton', 'ToggleButton'],
        'input': ['Edit', 'ComboBox', 'TextBox', 'Document'],
        'menu': ['Menu', 'MenuBar', 'MenuItem', 'ContextMenu'],
        'list': ['List', 'ListItem', 'Tree', 'TreeItem', 'Grid'],
        'link': ['Hyperlink', 'Link'],
        'tab': ['Tab', 'TabItem'],
        'slider': ['Slider', 'Thumb'],
        'pane': ['Pane', 'Group', 'Window', 'Dialog']
    }

    def __init__(self):
        """初始化UI结构引擎"""
        self.uia_bridge = UIAutomationBridge()
        self.current_elements = []
        self.screenshot_path = None

    def capture_screen(self, path: str = None) -> str:
        """截取当前屏幕"""
        if path is None:
            ensure_dir(STATE_DIR / "temp")
            path = STATE_DIR / "temp" / f"ui_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

        screenshot_script = SCRIPT_DIR / "screenshot_tool.py"
        if not screenshot_script.exists():
            return None

        try:
            result = subprocess.run(
                [sys.executable, str(screenshot_script), str(path)],
                capture_output=True,
                timeout=10
            )
            if result.returncode == 0:
                return str(path)
        except Exception:
            pass
        return None

    def analyze_current_ui(self) -> Dict:
        """
        分析当前屏幕的UI结构

        Returns:
            Dict: 包含窗口信息、元素列表、布局区域等
        """
        # 1. 截取屏幕
        screenshot_path = self.capture_screen()
        if screenshot_path:
            self.screenshot_path = screenshot_path
        else:
            self.screenshot_path = None

        result = {
            "timestamp": datetime.now().isoformat(),
            "screenshot": screenshot_path,
            "window": None,
            "elements": [],
            "interactive_elements": [],
            "layout_regions": [],
            "analysis_method": "hybrid_uia_vision"
        }

        # 2. 获取前台窗口信息
        if self.uia_bridge.is_available():
            try:
                root = self.uia_bridge.get_root_element()
                focused = self.uia_bridge.get_foreground_window()

                if focused:
                    window_info = self._extract_element_info(focused)
                    result["window"] = window_info

                    # 获取窗口子元素
                    elements = self._get_child_elements(focused)
                    result["elements"] = elements[:50]  # 限制数量

                    # 筛选可交互元素
                    for elem in elements:
                        if elem.get("control_type") in [t for types in self.INTERACTIVE_TYPES.values() for t in types]:
                            result["interactive_elements"].append(elem)
            except Exception as e:
                result["error"] = str(e)

        # 3. 如果有截图，用 vision 补充分析
        if screenshot_path and self.screenshot_path:
            vision_result = self._vision_analyze(screenshot_path)
            if vision_result:
                result["vision_analysis"] = vision_result
                # 合并布局区域
                if "layout_regions" in vision_result:
                    result["layout_regions"] = vision_result["layout_regions"]

        # 4. 如果无法获取 UIA，至少返回截图分析
        if not result["elements"] and screenshot_path:
            vision_result = self._vision_analyze(screenshot_path)
            if vision_result:
                result["vision_analysis"] = vision_result
                result["elements"] = vision_result.get("visual_elements", [])
                result["interactive_elements"] = [
                    e for e in result["elements"]
                    if e.get("type") in ["button", "input", "link", "menu", "checkbox"]
                ]
                result["layout_regions"] = vision_result.get("layout_regions", [])

        return result

    def _extract_element_info(self, element) -> Dict:
        """提取元素信息"""
        info = {}
        try:
            info["name"] = element.CurrentName or ""
            info["control_type"] = element.CurrentControlTypeName or ""
            info["automation_id"] = element.CurrentAutomationId or ""
            info["class_name"] = element.CurrentClassName or ""

            # 获取边界矩形
            try:
                bounds = element.CurrentBoundingRectangle
                info["bounds"] = {
                    "left": bounds.left,
                    "top": bounds.top,
                    "right": bounds.right,
                    "bottom": bounds.bottom,
                    "width": bounds.right - bounds.left,
                    "height": bounds.bottom - bounds.top
                }
                info["center"] = {
                    "x": (bounds.left + bounds.right) // 2,
                    "y": (bounds.top + bounds.bottom) // 2
                }
            except Exception:
                pass
        except Exception:
            pass
        return info

    def _get_child_elements(self, element, depth: int = 0, max_depth: int = 3) -> List[Dict]:
        """递归获取子元素"""
        elements = []
        if depth > max_depth:
            return elements

        try:
            # 尝试使用 TreeWalker
            from comtypes.client import CoCreateInstance
            from comtypes import GUID

            # 获取子元素
            try:
                walker = self.uia_bridge.uia.ControlViewWalker
                child = walker.GetFirstChildElement(element)
                while child:
                    elem_info = self._extract_element_info(child)
                    elem_info["depth"] = depth
                    if elem_info.get("name") or elem_info.get("control_type"):
                        elements.append(elem_info)

                    # 递归获取子元素
                    if depth < max_depth:
                        children = self._get_child_elements(child, depth + 1, max_depth)
                        elements.extend(children)

                    child = walker.GetNextSiblingElement(child)
            except Exception:
                pass
        except Exception:
            pass

        return elements

    def _vision_analyze(self, image_path: str) -> Optional[Dict]:
        """使用 vision 分析截图"""
        vision_script = SCRIPT_DIR / "vision_proxy.py"
        if not vision_script.exists():
            return None

        prompt = """分析这张UI截图，识别界面元素。

请用JSON格式返回：
{
    "interface_type": "界面类型（网页/桌面应用/系统界面）",
    "layout_regions": [
        {"name": "区域名称", "position": "位置", "bounds": {"x": 0, "y": 0, "w": 100, "h": 50}}
    ],
    "visual_elements": [
        {
            "type": "button/input/link/image/checkbox/radio/menu/list/label/other",
            "text": "显示文字",
            "bounds": {"x": 0, "y": 0, "w": 100, "h": 30},
            "clickable": true/false
        }
    ],
    "confidence": 0.0-1.0
}"""

        try:
            result = subprocess.run(
                [sys.executable, str(vision_script), image_path, prompt],
                capture_output=True,
                timeout=60
            )
            if result.stdout:
                output = result.stdout.decode("utf-8", errors="ignore")
                # 尝试提取 JSON
                json_match = re.search(r'\{[\s\S]*\}', output)
                if json_match:
                    return json.loads(json_match.group())
        except Exception:
            pass
        return None

    def find_element(self, description: str) -> List[Dict]:
        """
        根据描述查找UI元素

        Args:
            description: 元素描述，如"确定按钮"、"搜索输入框"等

        Returns:
            List[Dict]: 匹配的元素列表
        """
        # 先分析当前UI
        ui_analysis = self.analyze_current_ui()
        self.current_elements = ui_analysis.get("elements", []) + ui_analysis.get("interactive_elements", [])

        # 使用 vision 智能匹配
        if self.screenshot_path:
            vision_prompt = f"""在当前UI截图找到符合描述「{description}」的元素。

请返回JSON格式：
{{
    "matched_elements": [
        {{
            "description": "元素描述",
            "bounds": {{"x": 0, "y": 0, "w": 100, "h": 30}},
            "clickable": true,
            "confidence": 0.0-1.0
        }}
    ]
}}"""

            vision_result = self._vision_analyze_with_prompt(self.screenshot_path, vision_prompt)
            if vision_result and "matched_elements" in vision_result:
                return vision_result["matched_elements"]

        # 回退：基于名称和控制类型匹配
        matched = []
        desc_lower = description.lower()

        # 常见按钮关键词
        button_keywords = ["按钮", "确定", "取消", "提交", "保存", "关闭", "删除", "编辑", "添加", "确认", "button", "ok", "cancel", "submit", "save", "close"]
        input_keywords = ["输入", "框", "文本", "搜索", "输入框", "编辑", "input", "edit", "search", "text"]
        link_keywords = ["链接", "超链接", "link"]
        menu_keywords = ["菜单", "menu", "导航"]

        for elem in self.current_elements:
            name = elem.get("name", "").lower()
            control_type = elem.get("control_type", "").lower()

            # 关键词匹配
            if any(kw in desc_lower for kw in button_keywords) and any(kw in name or kw in control_type for kw in button_keywords):
                matched.append(elem)
            elif any(kw in desc_lower for kw in input_keywords) and any(kw in name or kw in control_type for kw in input_keywords):
                matched.append(elem)
            elif any(kw in desc_lower for kw in link_keywords) and any(kw in name or kw in control_type for kw in link_keywords):
                matched.append(elem)
            elif any(kw in desc_lower for kw in menu_keywords) and any(kw in name or kw in control_type for kw in menu_keywords):
                matched.append(elem)
            elif description in name or name in description:
                matched.append(elem)

        return matched[:10]  # 限制返回数量

    def _vision_analyze_with_prompt(self, image_path: str, prompt: str) -> Optional[Dict]:
        """使用自定义 prompt 分析截图"""
        vision_script = SCRIPT_DIR / "vision_proxy.py"
        if not vision_script.exists():
            return None

        try:
            result = subprocess.run(
                [sys.executable, str(vision_script), image_path, prompt],
                capture_output=True,
                timeout=60
            )
            if result.stdout:
                output = result.stdout.decode("utf-8", errors="ignore")
                json_match = re.search(r'\{[\s\S]*\}', output)
                if json_match:
                    return json.loads(json_match.group())
        except Exception:
            pass
        return None

    def get_element_path(self, element: Dict) -> str:
        """生成元素路径（类似CSS选择器）"""
        path_parts = []

        if element.get("automation_id"):
            path_parts.append(f'#{element["automation_id"]}')

        if element.get("name"):
            name = re.sub(r'[^\w\u4e00-\u9fa5]', '', element["name"])
            if name:
                path_parts.append(f'text="{name}"')

        if element.get("control_type"):
            path_parts.append(element["control_type"])

        return ' > '.join(path_parts) if path_parts else 'unknown'

    def click_element(self, description: str) -> Dict:
        """
        查找并点击元素

        Args:
            description: 元素描述

        Returns:
            Dict: 点击结果
        """
        elements = self.find_element(description)

        if not elements:
            return {
                "success": False,
                "message": f"未找到符合描述「{description}」的元素",
                "elements_found": 0
            }

        # 选择置信度最高的元素
        best = max(elements, key=lambda e: e.get("confidence", 0.5))

        # 获取点击坐标
        if "bounds" in best:
            bounds = best["bounds"]
            if isinstance(bounds, dict):
                x = bounds.get("x", 0) + bounds.get("w", 0) // 2
                y = bounds.get("y", 0) + bounds.get("h", 0) // 2
            else:
                x, y = bounds.get("center", {}).get("x", 0), bounds.get("center", {}).get("y", 0)
        elif "center" in best:
            x, y = best["center"]["x"], best["center"]["y"]
        else:
            return {
                "success": False,
                "message": "无法确定元素位置",
                "element": best
            }

        # 执行点击
        mouse_script = SCRIPT_DIR / "mouse_tool.py"
        if mouse_script.exists():
            try:
                result = subprocess.run(
                    [sys.executable, str(mouse_script), "click", str(x), str(y)],
                    capture_output=True,
                    timeout=10
                )
                return {
                    "success": result.returncode == 0,
                    "clicked_at": {"x": x, "y": y},
                    "element": best,
                    "method": "uia_vision_hybrid"
                }
            except Exception as e:
                return {
                    "success": False,
                    "message": str(e),
                    "element": best
                }

        return {
            "success": False,
            "message": "mouse_tool.py 不存在",
            "element": best
        }

    def get_interactive_summary(self) -> Dict:
        """获取可交互元素的摘要"""
        ui = self.analyze_current_ui()

        window_info = ui.get("window") or {}
        summary = {
            "timestamp": ui["timestamp"],
            "window_title": window_info.get("name", "Unknown") if window_info else "Unknown",
            "element_count": len(ui.get("elements", [])),
            "interactive_count": len(ui.get("interactive_elements", [])),
            "by_type": {}
        }

        # 统计各类型元素数量
        for elem in ui.get("interactive_elements", []):
            ctype = elem.get("control_type", "other")
            summary["by_type"][ctype] = summary["by_type"].get(ctype, 0) + 1

        return summary


def analyze_command(args: List[str]) -> Dict:
    """analyze 命令处理"""
    engine = UIStructureEngine()
    result = engine.analyze_current_ui()

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def find_command(args: List[str]) -> Dict:
    """find 命令处理"""
    if not args:
        return {"error": "请提供元素描述"}

    description = " ".join(args)
    engine = UIStructureEngine()
    elements = engine.find_element(description)

    print(f"找到 {len(elements)} 个匹配元素:")
    for i, elem in enumerate(elements, 1):
        bounds = elem.get("bounds", {})
        if isinstance(bounds, dict):
            pos = f"({bounds.get('x', 0)}, {bounds.get('y', 0)})"
        else:
            pos = f"center={bounds.get('center', {})}"
        print(f"  {i}. {elem.get('name', elem.get('control_type', 'Unknown'))} at {pos}")

    return {"elements": elements, "count": len(elements)}


def click_command(args: List[str]) -> Dict:
    """click 命令处理"""
    if not args:
        return {"error": "请提供元素描述"}

    description = " ".join(args)
    engine = UIStructureEngine()
    result = engine.click_element(description)

    if result.get("success"):
        print(f"成功点击元素: {result.get('element', {}).get('name', 'Unknown')}")
        print(f"点击坐标: {result.get('clicked_at')}")
    else:
        print(f"点击失败: {result.get('message', '未知错误')}")
        if result.get("elements_found", 0) == 0:
            print(f"未找到匹配元素")

    return result


def summary_command(args: List[str]) -> Dict:
    """summary 命令处理"""
    engine = UIStructureEngine()
    result = engine.get_interactive_summary()

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def interactive_mode(args: List[str]) -> Dict:
    """交互式UI探索模式"""
    print("=" * 50)
    print("智能UI结构理解引擎 - 交互式探索模式")
    print("=" * 50)
    print("命令:")
    print("  analyze - 分析当前屏幕UI结构")
    print("  summary - 显示可交互元素摘要")
    print("  find <描述> - 查找元素")
    print("  click <描述> - 查找并点击元素")
    print("  quit - 退出")
    print("=" * 50)

    engine = UIStructureEngine()

    while True:
        try:
            cmd = input("\n> ").strip()
            if not cmd:
                continue

            if cmd == "quit":
                break

            parts = cmd.split(None, 1)
            action = parts[0]
            args = parts[1].split() if len(parts) > 1 else []

            if action == "analyze":
                analyze_command(args)
            elif action == "summary":
                summary_command(args)
            elif action == "find":
                find_command(args)
            elif action == "click":
                click_command(args)
            else:
                print(f"未知命令: {action}")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"错误: {e}")

    return {"mode": "interactive", "exited": True}


def main():
    """主入口"""
    if len(sys.argv) < 2:
        # 默认进入交互模式
        interactive_mode([])
        return

    command = sys.argv[1].lower()
    args = sys.argv[2:]

    if command == "analyze":
        analyze_command(args)
    elif command == "find":
        find_command(args)
    elif command == "click":
        click_command(args)
    elif command == "summary":
        summary_command(args)
    elif command == "interactive":
        interactive_mode(args)
    elif command in ["help", "-h", "--help"]:
        print(__doc__)
    else:
        print(f"未知命令: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()