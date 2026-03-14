#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化引擎集群统一导航与智能入口引擎

功能：
1. 自动扫描 scripts/ 下所有 evolution*.py 文件
2. 提取命令和功能描述，构建进化引擎能力知识库
3. 提供统一的自然语言入口，支持模糊匹配和智能推荐
4. 实现进化引擎状态查询和健康度监控
5. 集成到 do.py 支持进化导航、引擎导航等关键词触发

使用方法：
    python evolution_engine_cluster_navigator.py list                    - 列出所有进化引擎
    python evolution_engine_cluster_navigator.py search <关键词>        - 搜索进化引擎
    python evolution_engine_cluster_navigator.py info <引擎名>          - 查看引擎详情
    python evolution_engine_cluster_navigator.py status                  - 查看引擎集群状态
    python evolution_engine_cluster_navigator.py run <引擎名> [命令]   - 运行指定引擎
"""

import ast
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE = PROJECT_ROOT / "runtime" / "state"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# 确保目录存在
RUNTIME_STATE.mkdir(parents=True, exist_ok=True)


class EvolutionEngineClusterNavigator:
    """进化引擎集群导航器"""

    def __init__(self):
        self.scripts_dir = SCRIPTS_DIR
        self.cache_file = RUNTIME_STATE / "evolution_engines_cache.json"
        self.engines_cache = self._load_cache()

    def _load_cache(self) -> Dict[str, Any]:
        """加载缓存的引擎信息"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_cache(self, cache: Dict[str, Any]) -> None:
        """保存引擎信息缓存"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存缓存失败: {e}", file=sys.stderr)

    def _extract_docstring(self, file_path: Path) -> str:
        """提取文件的 docstring"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 尝试解析 AST 获取 docstring
                try:
                    tree = ast.parse(content)
                    if tree.body and isinstance(tree.body[0], ast.Module):
                        docstring = ast.get_docstring(tree.body[0])
                        if docstring:
                            return docstring.strip()
                except Exception:
                    pass
                # 备用：正则提取
                match = re.search(r'"""(.+?)"""', content, re.DOTALL)
                if match:
                    return match.group(1).strip().split('\n')[0]
        except Exception as e:
            print(f"读取文件失败 {file_path}: {e}", file=sys.stderr)
        return ""

    def _extract_commands(self, file_path: Path) -> List[str]:
        """提取脚本支持的命令列表"""
        commands = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 查找 if __name__ == "__main__" 块
            if 'if __name__' in content:
                # 提取 main 代码块
                match = re.search(r'if __name__ == ["\']__main__["\']:(.+?)(?=\n(?:class|def|if|$))',
                                  content, re.DOTALL)
                if match:
                    main_block = match.group(1)
                    # 查找 sys.argv 或 argparse
                    if 'sys.argv' in main_block or 'argparse' in main_block:
                        # 简单提取命令用法注释
                        usage_matches = re.findall(r'["\'](\w+)["\']', main_block)
                        commands.extend(usage_matches)
        except Exception as e:
            print(f"提取命令失败 {file_path}: {e}", file=sys.stderr)
        return list(set(commands))

    def _extract_keywords(self, file_path: Path) -> List[str]:
        """提取可能的触发关键词"""
        keywords = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()

            # 常见功能关键词
            common_keywords = [
                'auto', 'autonomous', 'self', 'evolution', 'smart', 'intelligent',
                'adaptive', 'optimize', 'learn', 'analyze', 'monitor', 'health',
                'meta', 'cross', 'deep', 'integration', 'engine', 'loop'
            ]

            for kw in common_keywords:
                if kw in content:
                    keywords.append(kw)
        except Exception:
            pass
        return list(set(keywords))

    def _generate_description(self, file_path: Path, docstring: str) -> str:
        """基于文件名和 docstring 生成描述"""
        name = file_path.stem.replace('evolution_', '').replace('_', ' ').title()

        if docstring:
            # 取第一行作为描述
            desc_lines = [l.strip() for l in docstring.split('\n') if l.strip()]
            if desc_lines:
                return desc_lines[0][:100]

        return f"进化引擎: {name}"

    def scan_engines(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """扫描所有进化引擎并提取信息"""
        if not force_refresh and self.engines_cache:
            cached_time = self.engines_cache.get('_cached_at', '')
            if cached_time:
                # 缓存有效期 1 小时
                try:
                    cached_dt = datetime.fromisoformat(cached_time)
                    if (datetime.now() - cached_dt).total_seconds() < 3600:
                        return self.engines_cache.get('engines', [])
                except Exception:
                    pass

        engines = []
        pattern = "evolution*.py"

        for file_path in sorted(self.scripts_dir.glob(pattern)):
            # 跳过非引擎文件
            if file_path.name in ['evolution_loop_daemon.py', 'evolution_scheduler.py',
                                   'evolution_loop_client.py', 'evolution_api_server.py',
                                   'evolution_cli.py', 'evolution_dashboard.py']:
                continue

            try:
                docstring = self._extract_docstring(file_path)
                commands = self._extract_commands(file_path)
                keywords = self._extract_keywords(file_path)
                description = self._generate_description(file_path, docstring)

                engine_info = {
                    'name': file_path.stem,
                    'file': file_path.name,
                    'description': description,
                    'docstring': docstring[:500] if docstring else '',
                    'commands': commands,
                    'keywords': keywords,
                    'path': str(file_path.relative_to(PROJECT_ROOT))
                }
                engines.append(engine_info)
            except Exception as e:
                print(f"扫描引擎失败 {file_path}: {e}", file=sys.stderr)

        # 更新缓存
        self.engines_cache = {
            '_cached_at': datetime.now().isoformat(),
            'engines': engines
        }
        self._save_cache(self.engines_cache)

        return engines

    def search_engines(self, query: str) -> List[Dict[str, Any]]:
        """搜索进化引擎"""
        engines = self.scan_engines()
        query_lower = query.lower()
        results = []

        for engine in engines:
            score = 0
            # 名称匹配
            if query_lower in engine['name'].lower():
                score += 10
            # 描述匹配
            if query_lower in engine['description'].lower():
                score += 5
            # 关键词匹配
            for kw in engine.get('keywords', []):
                if query_lower in kw.lower():
                    score += 3
            # 命令匹配
            for cmd in engine.get('commands', []):
                if query_lower in cmd.lower():
                    score += 2

            if score > 0:
                results.append((score, engine))

        # 按得分排序
        results.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in results]

    def get_engine_info(self, engine_name: str) -> Optional[Dict[str, Any]]:
        """获取指定引擎的详细信息"""
        engines = self.scan_engines()
        engine_name_lower = engine_name.lower()

        for engine in engines:
            if engine_name_lower in engine['name'].lower():
                return engine

        return None

    def run_engine(self, engine_name: str, command: str = "status") -> Dict[str, Any]:
        """运行指定的进化引擎"""
        engine_info = self.get_engine_info(engine_name)
        if not engine_info:
            return {"error": f"未找到引擎: {engine_name}"}

        script_path = PROJECT_ROOT / engine_info['path']
        if not script_path.exists():
            return {"error": f"引擎文件不存在: {script_path}"}

        try:
            result = subprocess.run(
                [sys.executable, str(script_path), command],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(PROJECT_ROOT)
            )

            output = result.stdout.strip()
            if output.startswith('{'):
                try:
                    return json.loads(output)
                except Exception:
                    pass
            return {
                "engine": engine_name,
                "command": command,
                "output": output,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"error": f"引擎执行超时: {engine_name}"}
        except Exception as e:
            return {"error": f"执行失败: {str(e)}"}

    def get_cluster_status(self) -> Dict[str, Any]:
        """获取进化引擎集群整体状态"""
        engines = self.scan_engines()

        # 分类统计
        categories = {
            'health': [],
            'decision': [],
            'execution': [],
            'knowledge': [],
            'meta': [],
            'other': []
        }

        for engine in engines:
            name = engine['name'].lower()
            if 'health' in name or 'heal' in name:
                categories['health'].append(engine['name'])
            elif 'decision' in name or 'intent' in name:
                categories['decision'].append(engine['name'])
            elif 'execution' in name or 'run' in name or 'loop' in name:
                categories['execution'].append(engine['name'])
            elif 'knowledge' in name or 'kg' in name or 'reasoning' in name:
                categories['knowledge'].append(engine['name'])
            elif 'meta' in name:
                categories['meta'].append(engine['name'])
            else:
                categories['other'].append(engine['name'])

        return {
            "total_engines": len(engines),
            "categories": categories,
            "cached_at": self.engines_cache.get('_cached_at', ''),
            "engines": [e['name'] for e in engines]
        }

    def format_list(self, engines: List[Dict[str, Any]]) -> str:
        """格式化引擎列表输出"""
        if not engines:
            return "未找到匹配的进化引擎"

        lines = ["=" * 60]
        lines.append("🧬 进化引擎集群导航")
        lines.append("=" * 60)
        lines.append(f"共找到 {len(engines)} 个进化引擎:\n")

        for i, engine in enumerate(engines, 1):
            lines.append(f"{i}. {engine['name']}")
            lines.append(f"   描述: {engine['description']}")
            if engine.get('commands'):
                lines.append(f"   命令: {', '.join(engine['commands'])}")
            lines.append("")

        return "\n".join(lines)

    def format_search(self, query: str, engines: List[Dict[str, Any]]) -> str:
        """格式化搜索结果输出"""
        if not engines:
            return f"未找到与 '{query}' 匹配的进化引擎"

        lines = ["=" * 60]
        lines.append(f"🔍 搜索结果: '{query}'")
        lines.append("=" * 60)
        lines.append(f"找到 {len(engines)} 个匹配结果:\n")

        for i, engine in enumerate(engines, 1):
            lines.append(f"{i}. {engine['name']}")
            lines.append(f"   描述: {engine['description']}")
            if engine.get('commands'):
                lines.append(f"   命令: {', '.join(engine['commands'])}")
            lines.append("")

        return "\n".join(lines)

    def format_info(self, engine: Dict[str, Any]) -> str:
        """格式化引擎详情输出"""
        lines = ["=" * 60]
        lines.append(f"📋 引擎详情: {engine['name']}")
        lines.append("=" * 60)
        lines.append(f"文件: {engine['file']}")
        lines.append(f"路径: {engine['path']}")
        lines.append(f"描述: {engine['description']}")
        if engine.get('commands'):
            lines.append(f"支持命令: {', '.join(engine['commands'])}")
        if engine.get('keywords'):
            lines.append(f"关键词: {', '.join(engine['keywords'])}")
        if engine.get('docstring'):
            lines.append(f"\n完整说明:\n{engine['docstring']}")

        return "\n".join(lines)


def main():
    """主函数"""
    navigator = EvolutionEngineClusterNavigator()

    if len(sys.argv) < 2:
        # 默认列出所有引擎
        engines = navigator.scan_engines()
        print(navigator.format_list(engines))
        return

    command = sys.argv[1]

    if command == "list":
        # 列出所有引擎
        force = "--refresh" in sys.argv
        engines = navigator.scan_engines(force_refresh=force)
        print(navigator.format_list(engines))

    elif command == "search":
        # 搜索引擎
        if len(sys.argv) < 3:
            print("用法: python evolution_engine_cluster_navigator.py search <关键词>")
            sys.exit(1)
        query = sys.argv[2]
        engines = navigator.search_engines(query)
        print(navigator.format_search(query, engines))

    elif command == "info":
        # 查看引擎详情
        if len(sys.argv) < 3:
            print("用法: python evolution_engine_cluster_navigator.py info <引擎名>")
            sys.exit(1)
        engine_name = sys.argv[2]
        engine = navigator.get_engine_info(engine_name)
        if engine:
            print(navigator.format_info(engine))
        else:
            print(f"未找到引擎: {engine_name}")

    elif command == "status":
        # 查看集群状态
        status = navigator.get_cluster_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif command == "run":
        # 运行引擎
        if len(sys.argv) < 3:
            print("用法: python evolution_engine_cluster_navigator.py run <引擎名> [命令]")
            sys.exit(1)
        engine_name = sys.argv[2]
        cmd = sys.argv[3] if len(sys.argv) > 3 else "status"
        result = navigator.run_engine(engine_name, cmd)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()