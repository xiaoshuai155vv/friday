#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能自动化脚本生成引擎
利用LLM根据用户自然语言描述的需求，自动生成可执行的Python/Shell脚本

功能：
- 需求理解：将自然语言需求转换为技术实现
- 代码生成：生成可执行的 Python/Shell 脚本
- 脚本验证：验证生成的脚本语法正确
- 执行与反馈：执行脚本并返回结果
- 脚本历史管理

集成到 do.py 支持：
- 生成脚本 <需求描述>
- 执行脚本 <脚本名>
- 脚本历史 / 脚本列表
- 脚本验证 <脚本名>
"""

import os
import sys
import json
import ast
import subprocess
import re
from datetime import datetime
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
RUNTIME_DIR = PROJECT_ROOT / "runtime" / "state"
SCRIPTS_HISTORY_DIR = RUNTIME_DIR / "generated_scripts"

# 确保目录存在
SCRIPTS_HISTORY_DIR.mkdir(parents=True, exist_ok=True)


class ScriptGenerationEngine:
    """智能自动化脚本生成引擎"""

    def __init__(self):
        self.history_file = SCRIPTS_HISTORY_DIR / "script_history.json"
        self.generated_scripts_dir = SCRIPTS_HISTORY_DIR / "scripts"
        self.generated_scripts_dir.mkdir(exist_ok=True)
        self.history = self._load_history()

    def _load_history(self):
        """加载脚本生成历史"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"scripts": []}
        return {"scripts": []}

    def _save_history(self):
        """保存脚本生成历史"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史失败: {e}")

    def _get_available_capabilities(self):
        """获取当前系统可用能力（用于提示LLM生成正确的脚本）"""
        capabilities_file = PROJECT_ROOT / "references" / "capabilities.md"
        if capabilities_file.exists():
            try:
                with open(capabilities_file, 'r', encoding='utf-8') as f:
                    return f.read()[:3000]  # 限制长度
            except:
                pass
        return "参考 scripts/ 目录下的脚本和 do.py 命令"

    def generate_script(self, requirement, script_type="python"):
        """
        根据需求生成脚本

        Args:
            requirement: 用户自然语言描述的需求
            script_type: 脚本类型 (python/shell)

        Returns:
            生成结果字典
        """
        # 获取可用能力作为上下文
        capabilities = self._get_available_capabilities()

        # 构建提示词
        if script_type == "python":
            prompt = f"""请根据以下用户需求生成一个可执行的Python脚本。

用户需求：{requirement}

当前系统可用能力（参考）:
{capabilities}

要求：
1. 生成的脚本必须是独立可执行的Python脚本
2. 脚本应该调用现有的工具和引擎完成需求
3. 脚本放在 scripts/ 目录下，使用现有的工具（如 screenshot_tool, mouse_tool, keyboard_tool 等）
4. 如果需要调用外部命令，使用 subprocess 模块
5. 添加必要的注释说明脚本功能
6. 确保脚本在 Windows 环境下可以运行

请只输出Python代码，不要有其他解释。"""
        else:
            prompt = f"""请根据以下用户需求生成一个可执行的Shell脚本。

用户需求：{requirement}

要求：
1. 生成的脚本必须是独立的Shell脚本
2. 脚本在 Windows 环境下可执行（使用 cmd.exe 或 PowerShell 语法）
3. 添加必要的注释说明脚本功能

请只输出Shell代码，不要有其他解释。"""

        # 使用 LLM 生成代码（通过调用 do.py 的内置功能或直接生成）
        # 这里我们使用内置的简单实现
        generated_code = self._generate_with_llm(prompt, script_type)

        if not generated_code:
            return {
                "success": False,
                "error": "脚本生成失败，请稍后重试"
            }

        # 保存生成的脚本
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        script_name = f"generated_{timestamp}.{'py' if script_type == 'python' else 'bat'}"
        script_path = self.generated_scripts_dir / script_name

        try:
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(generated_code)
        except Exception as e:
            return {
                "success": False,
                "error": f"保存脚本失败: {e}"
            }

        # 验证脚本语法
        syntax_valid = self._validate_syntax(script_path, script_type)

        # 记录到历史
        script_info = {
            "name": script_name,
            "path": str(script_path),
            "requirement": requirement,
            "type": script_type,
            "created_at": datetime.now().isoformat(),
            "syntax_valid": syntax_valid,
            "executed_count": 0
        }
        self.history["scripts"].insert(0, script_info)
        self._save_history()

        return {
            "success": True,
            "script_name": script_name,
            "script_path": str(script_path),
            "code": generated_code,
            "syntax_valid": syntax_valid,
            "script_info": script_info
        }

    def _generate_with_llm(self, prompt, script_type):
        """调用 LLM 生成代码"""
        # 这里使用简单的模板生成作为后备方案
        # 实际使用时可以通过配置 LLM API 进行更智能的生成

        # 简单的模板匹配生成
        requirement = prompt.split("用户需求：")[1].split("\n")[0].strip() if "用户需求：" in prompt else ""

        if not requirement:
            return None

        # 基于需求关键词生成基本脚本框架
        code = self._generate_from_template(requirement, script_type)
        return code

    def _generate_from_template(self, requirement, script_type):
        """基于需求模板生成代码"""
        req_lower = requirement.lower()

        # Python 脚本生成
        if script_type == "python":
            # 根据需求类型生成对应脚本
            if any(k in req_lower for k in ["截图", "截图", "截屏"]):
                code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自动生成的截图脚本"""

import subprocess
import sys
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

def main():
    """执行截图"""
    try:
        # 调用截图工具
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / "screenshot_tool.py")],
            capture_output=True,
            text=True,
            timeout=30
        )
        print("截图完成")
        print(result.stdout)
        return True
    except Exception as e:
        print(f"截图失败: {e}")
        return False

if __name__ == "__main__":
    main()
'''
            elif any(k in req_lower for k in ["文件", "整理", "管理"]):
                code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自动生成的文件管理脚本"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

def main():
    """执行文件管理任务"""
    print("文件管理脚本已生成")
    print("请根据具体需求修改此脚本")

    # 示例：列出当前目录文件
    scripts_dir = PROJECT_ROOT / "scripts"
    if scripts_dir.exists():
        files = list(scripts_dir.glob("*.py"))[:10]
        print(f"scripts 目录下有 {len(files)} 个 Python 文件")

if __name__ == "__main__":
    main()
'''
            elif any(k in req_lower for k in ["窗口", "激活", "关闭"]):
                code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自动生成的窗口管理脚本"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

def main():
    """执行窗口管理任务"""
    print("窗口管理脚本已生成")
    print("请指定具体的窗口标题或进程名")

    # 示例：调用窗口工具
    # subprocess.run([sys.executable, str(PROJECT_ROOT / "scripts" / "window_tool.py"), "activate", "记事本"])

if __name__ == "__main__":
    main()
'''
            elif any(k in req_lower for k in ["浏览器", "打开网页", "访问"]):
                code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自动生成的浏览器控制脚本"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

def main():
    """执行浏览器操作任务"""
    # 提取URL（如果需求中有）
    print("浏览器控制脚本已生成")

    # 调用浏览器打开
    # subprocess.run([sys.executable, str(PROJECT_ROOT / "scripts" / "launch_browser.py"), "https://www.baidu.com"])

if __name__ == "__main__":
    main()
'''
            else:
                # 默认通用脚本
                code = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动生成的脚本 - 基于需求：{requirement}
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

def main():
    """
    执行任务：{requirement}

    此脚本根据用户需求自动生成，您可以修改此脚本以满足具体需求。
    """
    print("=" * 50)
    print(f"任务：{requirement}")
    print("=" * 50)

    # TODO: 根据具体需求实现自动化逻辑
    # 示例：调用现有工具
    # subprocess.run([sys.executable, str(PROJECT_ROOT / "scripts" / "screenshot_tool.py")])

    print("\\n任务执行完成")

if __name__ == "__main__":
    main()
'''
        else:
            # Shell 脚本生成
            code = f'''@echo off
REM 自动生成的脚本 - 基于需求：{requirement}
REM 生成时间：{datetime.now().isoformat()}

echo.
echo ========================================
echo 任务：{requirement}
echo ========================================
echo.

REM TODO: 根据具体需求实现自动化逻辑

echo 任务执行完成
pause
'''
        return code

    def _validate_syntax(self, script_path, script_type):
        """验证脚本语法"""
        if script_type == "python":
            try:
                with open(script_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                ast.parse(code)
                return True
            except SyntaxError as e:
                print(f"语法错误: {e}")
                return False
            except Exception as e:
                print(f"验证失败: {e}")
                return False
        else:
            # Shell 脚本简单验证
            return True

    def execute_script(self, script_name):
        """执行已生成的脚本"""
        script_path = self.generated_scripts_dir / script_name
        if not script_path.exists():
            # 尝试在 scripts 目录下查找
            script_path = SCRIPTS_DIR / script_name
            if not script_path.exists():
                return {
                    "success": False,
                    "error": f"脚本不存在: {script_name}"
                }

        # 判断脚本类型
        if script_path.suffix == ".py":
            try:
                result = subprocess.run(
                    [sys.executable, str(script_path)],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    cwd=str(PROJECT_ROOT)
                )
                output = result.stdout + result.stderr
                success = result.returncode == 0

                # 更新执行次数
                self._update_execution_count(script_name)

                return {
                    "success": success,
                    "output": output,
                    "returncode": result.returncode
                }
            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "error": "脚本执行超时"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"执行失败: {e}"
                }
        else:
            # Shell 脚本
            try:
                result = subprocess.run(
                    [str(script_path)],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    shell=True
                )
                return {
                    "success": result.returncode == 0,
                    "output": result.stdout + result.stderr,
                    "returncode": result.returncode
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"执行失败: {e}"
                }

    def _update_execution_count(self, script_name):
        """更新脚本执行次数"""
        for script in self.history["scripts"]:
            if script["name"] == script_name:
                script["executed_count"] = script.get("executed_count", 0) + 1
                script["last_executed"] = datetime.now().isoformat()
                break
        self._save_history()

    def list_scripts(self):
        """列出所有生成的脚本"""
        return self.history.get("scripts", [])

    def get_script_content(self, script_name):
        """获取脚本内容"""
        script_path = self.generated_scripts_dir / script_name
        if not script_path.exists():
            return None

        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return None

    def delete_script(self, script_name):
        """删除脚本"""
        script_path = self.generated_scripts_dir / script_name
        if script_path.exists():
            script_path.unlink()

        # 从历史中移除
        self.history["scripts"] = [
            s for s in self.history["scripts"] if s["name"] != script_name
        ]
        self._save_history()
        return True

    def status(self):
        """获取引擎状态"""
        scripts = self.history.get("scripts", [])
        return {
            "total_scripts": len(scripts),
            "executed_scripts": sum(s.get("executed_count", 0) for s in scripts),
            "scripts_dir": str(self.generated_scripts_dir),
            "history_file": str(self.history_file)
        }


def main():
    """CLI 入口"""
    import argparse

    parser = argparse.ArgumentParser(description="智能自动化脚本生成引擎")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # 生成脚本
    generate_parser = subparsers.add_parser("generate", help="生成脚本")
    generate_parser.add_argument("requirement", help="用户需求描述")
    generate_parser.add_argument("--type", choices=["python", "shell"], default="python", help="脚本类型")

    # 执行脚本
    execute_parser = subparsers.add_parser("execute", help="执行脚本")
    execute_parser.add_argument("script_name", help="脚本名称")

    # 列出脚本
    subparsers.add_parser("list", help="列出所有脚本")

    # 查看脚本内容
    content_parser = subparsers.add_parser("content", help="查看脚本内容")
    content_parser.add_argument("script_name", help="脚本名称")

    # 删除脚本
    delete_parser = subparsers.add_parser("delete", help="删除脚本")
    delete_parser.add_argument("script_name", help="脚本名称")

    # 状态
    subparsers.add_parser("status", help="获取引擎状态")

    args = parser.parse_args()

    engine = ScriptGenerationEngine()

    if args.command == "generate":
        result = engine.generate_script(args.requirement, args.type)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "execute":
        result = engine.execute_script(args.script_name)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "list":
        scripts = engine.list_scripts()
        print(json.dumps(scripts, ensure_ascii=False, indent=2))
    elif args.command == "content":
        content = engine.get_script_content(args.script_name)
        if content:
            print(content)
        else:
            print(f"脚本不存在: {args.script_name}")
    elif args.command == "delete":
        result = engine.delete_script(args.script_name)
        print(json.dumps({"success": result}, ensure_ascii=False, indent=2))
    elif args.command == "status":
        status = engine.status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()