#!/usr/bin/env python3
"""
智能工作流自动生成引擎
让系统能够根据用户自然语言描述的任务需求，自动分析并生成可执行的 run_plan JSON

功能：
1. 理解用户的自然语言任务描述
2. 自动分析任务所需的步骤
3. 生成可执行的 run_plan JSON
4. 提供验证和优化功能

使用方式：
- 直接运行：python scripts/workflow_auto_generator.py "帮我打开浏览器访问百度"
- 模块导入：from workflow_auto_generator import WorkflowAutoGenerator
- CLI：python scripts/workflow_auto_generator.py --task "任务描述" [--output plan.json]
"""

import json
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

try:
    from do import get_model
except ImportError:
    # 如果导入失败，尝试使用环境变量或默认值
    get_model = None


class WorkflowAutoGenerator:
    """智能工作流自动生成引擎"""

    # 支持的步骤类型
    STEP_TYPES = [
        "screenshot", "vision", "vision_coords", "click", "type", "key",
        "paste", "scroll", "wait", "run", "activate", "maximize"
    ]

    # 常用应用的激活命令映射
    APP_ACTIVATION = {
        "浏览器": {"type": "run", "command": "launch_browser.py"},
        "chrome": {"type": "activate_process", "process": "chrome"},
        "edge": {"type": "activate_process", "process": "msedge"},
        "记事本": {"type": "run", "command": "launch_notepad.py"},
        "文件管理器": {"type": "run", "command": "launch_explorer.py"},
        "计算器": {"type": "run", "command": "launch_calc.py"},
        "任务管理器": {"type": "run", "command": "launch_taskmgr.py"},
    }

    def __init__(self):
        self.model = None
        self._init_model()

    def _init_model(self):
        """初始化模型"""
        try:
            if get_model:
                self.model = get_model()
        except Exception as e:
            print(f"警告：无法初始化模型，将使用规则引擎: {e}")

    def generate_workflow(self, task_description: str, context: dict = None) -> dict:
        """
        根据自然语言任务描述生成工作流

        Args:
            task_description: 用户任务描述
            context: 额外上下文信息（如当前窗口、系统状态等）

        Returns:
            可执行的 plan JSON 结构
        """
        # 尝试使用 LLM 生成
        if self.model:
            return self._generate_with_llm(task_description, context)

        # 回退到规则引擎
        return self._generate_with_rules(task_description, context)

    def _generate_with_llm(self, task_description: str, context: dict = None) -> dict:
        """使用 LLM 生成工作流"""
        prompt = self._build_prompt(task_description, context)

        try:
            response = self.model(prompt, return_reasoning=False)

            # 尝试解析 JSON 响应
            plan = self._parse_llm_response(response)

            if plan and self._validate_plan(plan):
                return plan

        except Exception as e:
            print(f"LLM 生成失败，回退到规则引擎: {e}")

        # 回退到规则引擎
        return self._generate_with_rules(task_description, context)

    def _build_prompt(self, task_description: str, context: dict = None) -> str:
        """构建 LLM 提示词"""
        context_str = ""
        if context:
            context_str = f"\n额外上下文信息：{json.dumps(context, ensure_ascii=False)}"

        prompt = f"""你是一个智能工作流生成器。请根据用户描述的任务，生成可执行的 run_plan JSON。

任务描述：{task_description}{context_str}

可用的步骤类型：
- screenshot: 截图
- vision: 视觉理解（看图回答问题）
- vision_coords: 获取点击坐标
- click: 鼠标点击 (x, y)
- type: 键盘输入（仅 ASCII）
- key: 发送特殊键（如 13=回车）
- paste: 粘贴剪贴板内容
- scroll: 滚动（正数向上滚，负数向下滚）
- wait: 等待指定秒数
- run: 运行脚本
- activate: 激活窗口（按标题）
- maximize: 最大化窗口

重要约束：
1. 打开或激活任何应用后，必须先最大化窗口，再进行后续操作
2. 截图后如果需要与界面交互，必须先用 vision 理解界面
3. 中文输入使用 paste（先写剪贴板再粘贴）
4. 生成的 plan 必须符合 run_plan.py 的格式要求

请直接输出 JSON 格式的 plan，不要包含其他内容。格式：
{{
  "name": "任务名称",
  "description": "任务描述",
  "steps": [
    {{"do": "步骤类型", "args": ["参数"]}}
  ]
}}

请确保 steps 中的每个步骤都是可执行的。"""

        return prompt

    def _parse_llm_response(self, response: str) -> dict:
        """解析 LLM 响应"""
        try:
            # 尝试提取 JSON
            response = response.strip()

            # 处理可能的 markdown 代码块
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                response = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                response = response[start:end].strip()

            return json.loads(response)

        except (json.JSONDecodeError, ValueError) as e:
            print(f"JSON 解析失败: {e}")
            return None

    def _generate_with_rules(self, task_description: str, context: dict = None) -> dict:
        """使用规则引擎生成工作流"""
        task_lower = task_description.lower()

        # 初始化 plan
        plan = {
            "name": task_description[:50],
            "description": task_description,
            "steps": []
        }

        # 检测任务类型并生成对应步骤

        # 1. 打开浏览器访问网站
        if "打开浏览器" in task_description or "访问" in task_description:
            # 提取 URL
            url = self._extract_url(task_description)
            plan["steps"].append({"do": "run", "args": ["launch_browser.py", url or ""]})
            plan["steps"].append({"do": "wait", "args": ["2"]})
            plan["steps"].append({"do": "maximize", "args": []})
            plan["steps"].append({"do": "wait", "args": ["1"]})
            plan["steps"].append({"do": "screenshot", "args": []})

            # 如果有具体任务，如搜索
            if "搜索" in task_description:
                keyword = task_description.split("搜索")[-1].strip()
                plan["steps"].append({"do": "vision", "args": ["找到搜索框位置"]})
                plan["steps"].append({"do": "click", "args": []})  # 坐标由上一步确定
                plan["steps"].append({"do": "paste", "args": [keyword]})
                plan["steps"].append({"do": "key", "args": ["13"]})  # 回车

            return plan

        # 2. 打开应用程序
        if "打开" in task_description and any(app in task_description for app in ["记事本", "文件管理器", "计算器", "音乐", "视频"]):
            app_name = self._extract_app_name(task_description)

            if app_name in self.APP_ACTIVATION:
                app_info = self.APP_ACTIVATION[app_name]
                if app_info["type"] == "run":
                    plan["steps"].append({"do": "run", "args": [app_info["command"]]})
                elif app_info["type"] == "activate_process":
                    plan["steps"].append({"do": "activate_process", "args": [app_info["process"]]})

            plan["steps"].append({"do": "wait", "args": ["2"]})
            plan["steps"].append({"do": "maximize", "args": []})
            plan["steps"].append({"do": "wait", "args": ["1"]})
            plan["steps"].append({"do": "screenshot", "args": []})

            return plan

        # 3. 截图任务
        if "截图" in task_description:
            plan["steps"].append({"do": "screenshot", "args": []})
            return plan

        # 4. 点击任务
        if "点击" in task_description:
            plan["steps"].append({"do": "screenshot", "args": []})
            plan["steps"].append({"do": "vision_coords", "args": [f"找到{task_description}中描述的位置"]})
            plan["steps"].append({"do": "click", "args": []})  # 坐标由上一步确定
            return plan

        # 5. 默认：尝试理解任务
        plan["steps"].append({"do": "screenshot", "args": []})
        plan["steps"].append({"do": "vision", "args": [f"理解当前界面，告诉我如何完成：{task_description}"]})

        return plan

    def _extract_url(self, task_description: str) -> str:
        """从任务描述中提取 URL"""
        keywords = ["http://", "https://", "www."]
        for keyword in keywords:
            if keyword in task_description:
                start = task_description.find(keyword)
                # 提取到空格或句子结束
                end = len(task_description)
                for sep in [" ", "，", "。", "？", "！"]:
                    pos = task_description.find(sep, start)
                    if pos > 0:
                        end = min(end, pos)
                return task_description[start:end]

        # 常见网站映射
        website_map = {
            "百度": "https://www.baidu.com",
            "谷歌": "https://www.google.com",
            "淘宝": "https://www.taobao.com",
            "京东": "https://www.jd.com",
            "bilibili": "https://www.bilibili.com",
            "B站": "https://www.bilibili.com",
        }

        for name, url in website_map.items():
            if name in task_description:
                return url

        return "https://www.baidu.com"  # 默认

    def _extract_app_name(self, task_description: str) -> str:
        """从任务描述中提取应用名称"""
        for app_name in self.APP_ACTIVATION.keys():
            if app_name in task_description:
                return app_name
        return None

    def _validate_plan(self, plan: dict) -> bool:
        """验证生成的 plan 是否有效"""
        if not isinstance(plan, dict):
            return False

        if "steps" not in plan:
            return False

        if not isinstance(plan["steps"], list):
            return False

        for step in plan["steps"]:
            if "do" not in step:
                return False

            if step["do"] not in self.STEP_TYPES:
                # 允许自定义步骤类型
                pass

        return True

    def optimize_plan(self, plan: dict, execution_history: list = None) -> dict:
        """
        优化生成的工作流

        Args:
            plan: 原始工作流
            execution_history: 执行历史（用于学习优化）

        Returns:
            优化后的工作流
        """
        if not plan or "steps" not in plan:
            return plan

        optimized = plan.copy()
        steps = optimized["steps"]

        # 1. 移除冗余的 wait
        optimized_steps = []
        for i, step in enumerate(steps):
            if step.get("do") == "wait":
                # 如果前后都是 wait，合并
                if optimized_steps and optimized_steps[-1].get("do") == "wait":
                    prev_wait = int(optimized_steps[-1].get("args", ["0"])[0])
                    curr_wait = int(step.get("args", ["0"])[0])
                    optimized_steps[-1]["args"] = [str(prev_wait + curr_wait)]
                    continue
            optimized_steps.append(step)

        optimized["steps"] = optimized_steps

        # 2. 确保激活后有 maximize
        for i, step in enumerate(optimized_steps):
            if step.get("do") in ["activate", "activate_process", "run"]:
                # 检查下一步是否是 maximize
                if i + 1 < len(optimized_steps):
                    next_step = optimized_steps[i + 1]
                    if next_step.get("do") != "maximize" and next_step.get("do") != "wait":
                        # 插入 maximize
                        optimized_steps.insert(i + 1, {"do": "maximize", "args": []})
                        # 添加 wait
                        optimized_steps.insert(i + 2, {"do": "wait", "args": ["1"]})

        return optimized

    def save_plan(self, plan: dict, output_path: str) -> bool:
        """保存工作流到文件"""
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(plan, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存失败: {e}")
            return False

    def load_plan(self, plan_path: str) -> dict:
        """从文件加载工作流"""
        try:
            with open(plan_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"加载失败: {e}")
            return None


def main():
    """CLI 入口"""
    parser = argparse.ArgumentParser(description="智能工作流自动生成引擎")
    parser.add_argument("task", nargs="?", help="任务描述")
    parser.add_argument("--task", "-t", help="任务描述（长格式）")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--validate", "-v", action="store_true", help="验证生成的 plan")

    args = parser.parse_args()

    task_description = args.task or args.task_s
    if not task_description:
        print("请输入任务描述")
        parser.print_help()
        return

    # 创建生成器
    generator = WorkflowAutoGenerator()

    # 生成工作流
    print(f"正在分析任务：{task_description}")
    plan = generator.generate_workflow(task_description)

    if plan:
        # 优化 plan
        plan = generator.optimize_plan(plan)

        print("\n生成的工作流：")
        print(json.dumps(plan, ensure_ascii=False, indent=2))

        # 验证
        if args.validate or True:  # 默认验证
            if generator._validate_plan(plan):
                print("\n[OK] Plan 验证通过")
            else:
                print("\n[FAIL] Plan 验证失败")

        # 保存
        if args.output:
            if generator.save_plan(plan, args.output):
                print(f"\n[OK] 已保存到：{args.output}")
        else:
            # 默认保存到 runtime/state/auto_generated_plan.json
            default_path = PROJECT_ROOT / "runtime" / "state" / "auto_generated_plan.json"
            if generator.save_plan(plan, str(default_path)):
                print(f"\n[OK] 已保存到：{default_path}")
    else:
        print("生成失败")


if __name__ == "__main__":
    main()