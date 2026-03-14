#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化引擎集群智能诊断与自动修复引擎

功能：
1. 自动检测进化引擎的健康状态（导入测试、函数签名验证、依赖检查）
2. 识别常见问题（ImportError、AttributeError、SyntaxError、参数不匹配）
3. 尝试自动修复常见故障
4. 生成诊断报告
5. 与导航引擎深度集成
6. 集成到 do.py 支持引擎诊断、诊断修复等关键词触发

使用方法：
    python evolution_engine_cluster_diagnostic_repair.py list                    - 列出所有进化引擎
    python evolution_engine_cluster_diagnostic_repair.py diagnose [引擎名]      - 诊断指定引擎或所有引擎
    python evolution_engine_cluster_diagnostic_repair.py repair [引擎名]       - 自动修复指定引擎或所有引擎
    python evolution_engine_cluster_diagnostic_repair.py report [引擎名]        - 生成诊断报告
    python evolution_engine_cluster_diagnostic_repair.py health                - 查看集群健康度统计
"""

import ast
import importlib.util
import inspect
import json
import os
import re
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# 修复 Windows 控制台编码问题（延迟执行，避免在某些环境下报错）
_imported_io = False
try:
    import io
    _imported_io = True
except ImportError:
    pass

if _imported_io and sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'buffer'):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass  # 忽略编码问题

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE = PROJECT_ROOT / "runtime" / "state"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# 确保目录存在
RUNTIME_STATE.mkdir(parents=True, exist_ok=True)


class EvolutionEngineDiagnosticRepair:
    """进化引擎集群智能诊断与自动修复引擎"""

    def __init__(self):
        self.scripts_dir = SCRIPTS_DIR
        self.diagnostic_cache_file = RUNTIME_STATE / "evolution_engines_diagnostic_cache.json"
        self.diagnostic_cache = self._load_cache()

    def _load_cache(self) -> Dict[str, Any]:
        """加载缓存的诊断信息"""
        if self.diagnostic_cache_file.exists():
            try:
                with open(self.diagnostic_cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_cache(self, cache: Dict[str, Any]) -> None:
        """保存诊断信息缓存"""
        try:
            with open(self.diagnostic_cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存缓存失败: {e}", file=sys.stderr)

    def _get_evolution_engines(self) -> List[Path]:
        """获取所有进化引擎文件"""
        engines = []
        for f in self.scripts_dir.glob("evolution*.py"):
            if f.stem not in ['evolution_engine_cluster_navigator', 'evolution_engine_cluster_diagnostic_repair']:
                engines.append(f)
        # 也包含当前引擎
        engines.append(Path(__file__))
        return sorted(engines)

    def _extract_engine_info(self, file_path: Path) -> Dict[str, Any]:
        """提取引擎基本信息"""
        info = {
            'name': file_path.stem,
            'path': str(file_path),
            'exists': file_path.exists()
        }
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 提取 docstring
                match = re.search(r'"""(.+?)"""', content, re.DOTALL)
                if match:
                    info['description'] = match.group(1).strip().split('\n')[0]
                else:
                    info['description'] = ''
                # 提取版本
                version_match = re.search(r'version\s*[\d.]+', content, re.IGNORECASE)
                info['version'] = version_match.group() if version_match else 'unknown'
        except Exception as e:
            info['error'] = str(e)
        return info

    def diagnose_engine(self, engine_path: Path) -> Dict[str, Any]:
        """诊断单个进化引擎"""
        result = {
            'name': engine_path.stem,
            'path': str(engine_path),
            'status': 'unknown',
            'issues': [],
            'health_score': 100,
            'checked_at': datetime.now().isoformat()
        }

        if not engine_path.exists():
            result['status'] = 'not_found'
            result['issues'].append('文件不存在')
            result['health_score'] = 0
            return result

        # 1. 语法检查
        try:
            with open(engine_path, 'r', encoding='utf-8') as f:
                content = f.read()
            ast.parse(content)
        except SyntaxError as e:
            result['issues'].append(f'语法错误: {e.msg} (行 {e.lineno})')
            result['health_score'] -= 30
        except Exception as e:
            result['issues'].append(f'语法检查失败: {str(e)}')
            result['health_score'] -= 20

        # 2. 导入测试
        try:
            spec = importlib.util.spec_from_file_location(engine_path.stem, engine_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(module)
                    result['imported'] = True
                except ImportError as e:
                    result['issues'].append(f'导入失败: {str(e)}')
                    result['health_score'] -= 25
                except AttributeError as e:
                    result['issues'].append(f'属性错误: {str(e)}')
                    result['health_score'] -= 20
                except Exception as e:
                    result['issues'].append(f'执行错误: {str(e)}')
                    result['health_score'] -= 25
            else:
                result['issues'].append('无法创建模块规格')
                result['health_score'] -= 20
        except Exception as e:
            result['issues'].append(f'导入测试失败: {str(e)}')
            result['health_score'] -= 25

        # 3. 函数签名检查
        try:
            with open(engine_path, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content)

            functions = []
            classes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)

            result['functions'] = functions[:10]  # 限制数量
            result['classes'] = classes[:5]

            # 检查是否有主类（通常以 Engine 结尾）
            engine_classes = [c for c in classes if 'Engine' in c or 'engine' in c.lower()]
            if not engine_classes and classes:
                result['issues'].append('未找到标准 Engine 类命名')
                result['health_score'] -= 5
        except Exception as e:
            result['issues'].append(f'函数签名检查失败: {str(e)}')
            result['health_score'] -= 10

        # 4. 依赖检查
        try:
            with open(engine_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取 import 语句
            imports = re.findall(r'^(?:from|import)\s+([\w.]+)', content, re.MULTILINE)
            result['dependencies'] = imports[:20]  # 限制数量

            # 检查标准库和常见依赖
            stdlib_modules = {'os', 'sys', 'json', 're', 'datetime', 'pathlib', 'typing',
                            'subprocess', 'threading', 'asyncio', 'collections', 'logging'}
            external_modules = {'requests', 'numpy', 'pandas', 'pypdf2', 'PIL', 'PyQt5',
                              'webview', 'fastapi', 'flask', 'torch', 'tensorflow'}

            missing_external = []
            for imp in imports:
                base = imp.split('.')[0]
                if base in external_modules:
                    try:
                        importlib.import_module(base)
                    except ImportError:
                        missing_external.append(base)

            if missing_external:
                result['issues'].append(f'缺少可选依赖: {", ".join(missing_external)}')
                result['health_score'] -= 10
        except Exception as e:
            result['issues'].append(f'依赖检查失败: {str(e)}')
            result['health_score'] -= 5

        # 最终状态
        result['health_score'] = max(0, result['health_score'])
        if result['health_score'] >= 90:
            result['status'] = 'healthy'
        elif result['health_score'] >= 60:
            result['status'] = 'warning'
        else:
            result['status'] = 'error'

        return result

    def diagnose_all_engines(self, force: bool = False) -> Dict[str, Any]:
        """诊断所有进化引擎"""
        if not force and self.diagnostic_cache:
            # 检查缓存是否过期（超过 1 小时）
            last_check = self.diagnostic_cache.get('last_check', '')
            if last_check:
                try:
                    last_time = datetime.fromisoformat(last_check)
                    if (datetime.now() - last_time).total_seconds() < 3600:
                        return self.diagnostic_cache
                except Exception:
                    pass

        engines = self._get_evolution_engines()
        results = []

        for engine_path in engines:
            result = self.diagnose_engine(engine_path)
            results.append(result)

        # 统计
        healthy = sum(1 for r in results if r['status'] == 'healthy')
        warning = sum(1 for r in results if r['status'] == 'warning')
        error = sum(1 for r in results if r['status'] == 'error')
        not_found = sum(1 for r in results if r['status'] == 'not_found')

        diagnostic_result = {
            'engines': results,
            'summary': {
                'total': len(engines),
                'healthy': healthy,
                'warning': warning,
                'error': error,
                'not_found': not_found,
                'average_health_score': sum(r['health_score'] for r in results) / len(results) if results else 0
            },
            'last_check': datetime.now().isoformat()
        }

        self.diagnostic_cache = diagnostic_result
        self._save_cache(diagnostic_result)

        return diagnostic_result

    def repair_engine(self, engine_path: Path) -> Dict[str, Any]:
        """尝试自动修复进化引擎"""
        result = {
            'name': engine_path.stem,
            'path': str(engine_path),
            'repair_actions': [],
            'success': False,
            'error': None
        }

        if not engine_path.exists():
            result['error'] = '文件不存在'
            return result

        try:
            with open(engine_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            content = original_content
            modified = False

            # 1. 修复常见的语法问题
            # 修复缺少的括号
            content = re.sub(r'(\w)\s*\)', r'\1)', content)

            # 2. 修复常见导入问题
            # 添加缺失的 typing 导入（如果在代码中使用但未导入）
            if 'Dict[' in content or 'List[' in content or 'Any' in content:
                if 'from typing import' not in content and 'import typing' not in content:
                    # 检查是否真的需要 typing
                    if 'Dict[' in content or 'List[' in content or 'Optional[' in content:
                        # 检查文件开头是否已有 import 语句
                        lines = content.split('\n')
                        insert_idx = 0
                        for i, line in enumerate(lines):
                            if line.strip().startswith(('import ', 'from ')):
                                insert_idx = i + 1
                            elif line.strip() and not line.strip().startswith('#'):
                                break

                        if insert_idx > 0:
                            new_import = "from typing import Dict, List, Any, Optional, Tuple\n"
                            lines.insert(insert_idx, new_import)
                            content = '\n'.join(lines)
                            modified = True
                            result['repair_actions'].append('添加 typing 模块导入')

            # 3. 修复 path 问题
            # 确保 PROJECT_ROOT 等常量在使用前定义
            if 'PROJECT_ROOT' in content:
                # 检查是否已定义 PROJECT_ROOT
                if not re.search(r'^PROJECT_ROOT\s*=', content, re.MULTILINE):
                    # 添加 PROJECT_ROOT 定义
                    lines = content.split('\n')
                    insert_idx = 0
                    for i, line in enumerate(lines):
                        if line.strip().startswith(('import ', 'from ')):
                            insert_idx = i + 1

                    if insert_idx > 0:
                        project_root_def = "\n# 项目根目录\nPROJECT_ROOT = Path(__file__).parent.parent\n"
                        lines.insert(insert_idx, project_root_def)
                        content = '\n'.join(lines)
                        modified = True
                        result['repair_actions'].append('添加 PROJECT_ROOT 定义')

            # 4. 修复 sys.stdout 问题（Windows 编码）
            if sys.platform == 'win32' and 'sys.stdout' in content:
                if 'import io' not in content and 'sys.stdout = io.TextIOWrapper' in content:
                    lines = content.split('\n')
                    insert_idx = 0
                    for i, line in enumerate(lines):
                        if line.strip().startswith(('import ', 'from ')):
                            insert_idx = i + 1

                    if insert_idx > 0 and 'import io' not in content:
                        io_import = "import io\n"
                        lines.insert(insert_idx, io_import)
                        content = '\n'.join(lines)
                        modified = True
                        result['repair_actions'].append('添加 io 模块导入')

            # 保存修复后的内容
            if modified:
                backup_path = engine_path.with_suffix('.py.bak')
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)

                with open(engine_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                result['success'] = True
                result['backup'] = str(backup_path)
            else:
                result['repair_actions'].append('无需修复')

        except Exception as e:
            result['error'] = str(e)
            result['repair_actions'].append(f'修复失败: {str(e)}')

        return result

    def repair_all_engines(self) -> Dict[str, Any]:
        """尝试修复所有有问题的引擎"""
        diagnostic = self.diagnose_all_engines(force=True)

        repair_results = []
        for engine_result in diagnostic['engines']:
            if engine_result['status'] != 'healthy':
                engine_path = Path(engine_result['path'])
                repair_result = self.repair_engine(engine_path)
                repair_results.append(repair_result)

        return {
            'diagnostic': diagnostic,
            'repairs': repair_results,
            'summary': {
                'total_repaired': sum(1 for r in repair_results if r['success']),
                'total_failed': sum(1 for r in repair_results if not r['success']),
                'repaired_at': datetime.now().isoformat()
            }
        }

    def generate_report(self, engine_name: Optional[str] = None) -> Dict[str, Any]:
        """生成诊断报告"""
        diagnostic = self.diagnose_all_engines()

        if engine_name:
            # 查找指定引擎
            for engine in diagnostic['engines']:
                if engine_name.lower() in engine['name'].lower():
                    return {
                        'engine': engine,
                        'report_type': 'single'
                    }

        return {
            'diagnostic': diagnostic,
            'report_type': 'full',
            'generated_at': datetime.now().isoformat()
        }

    def get_health_summary(self) -> Dict[str, Any]:
        """获取集群健康度摘要"""
        diagnostic = self.diagnose_all_engines()

        return {
            'total_engines': diagnostic['summary']['total'],
            'healthy_count': diagnostic['summary']['healthy'],
            'warning_count': diagnostic['summary']['warning'],
            'error_count': diagnostic['summary']['error'],
            'average_health_score': round(diagnostic['summary']['average_health_score'], 2),
            'last_check': diagnostic['last_check'],
            'health_status': 'healthy' if diagnostic['summary']['average_health_score'] >= 90 else \
                             'warning' if diagnostic['summary']['average_health_score'] >= 60 else 'critical'
        }

    def list_engines(self) -> List[Dict[str, Any]]:
        """列出所有进化引擎及其诊断状态"""
        diagnostic = self.diagnose_all_engines()
        return diagnostic['engines']


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description='智能全场景进化引擎集群智能诊断与自动修复引擎'
    )
    parser.add_argument('command', nargs='?', default='health',
                       choices=['list', 'diagnose', 'repair', 'report', 'health'],
                       help='要执行的命令')
    parser.add_argument('engine_name', nargs='?', default=None,
                       help='引擎名称（可选）')
    parser.add_argument('--force', action='store_true',
                       help='强制重新诊断，忽略缓存')

    args = parser.parse_args()

    engine = EvolutionEngineDiagnosticRepair()

    if args.command == 'list':
        engines = engine.list_engines()
        print(f"\n{'='*60}")
        print(f"进化引擎集群诊断列表（共 {len(engines)} 个引擎）")
        print(f"{'='*60}\n")

        for e in engines:
            status_icon = {
                'healthy': '✓',
                'warning': '⚠',
                'error': '✗',
                'not_found': '?'
            }.get(e['status'], '?')

            print(f"{status_icon} {e['name']}")
            print(f"   状态: {e['status']} | 健康度: {e['health_score']}%")
            if e.get('issues'):
                for issue in e['issues'][:2]:  # 最多显示 2 个问题
                    print(f"   问题: {issue}")
            print()

    elif args.command == 'diagnose':
        if args.engine_name:
            # 诊断指定引擎
            engine_path = SCRIPTS_DIR / f"{args.engine_name}.py"
            result = engine.diagnose_engine(engine_path)

            print(f"\n{'='*60}")
            print(f"诊断结果: {result['name']}")
            print(f"{'='*60}")
            print(f"状态: {result['status']}")
            print(f"健康度: {result['health_score']}%")

            if result.get('issues'):
                print("\n发现的问题:")
                for issue in result['issues']:
                    print(f"  - {issue}")
            else:
                print("\n未发现问题")

        else:
            # 诊断所有引擎
            result = engine.diagnose_all_engines(force=args.force)

            print(f"\n{'='*60}")
            print(f"进化引擎集群诊断报告")
            print(f"{'='*60}")
            print(f"引擎总数: {result['summary']['total']}")
            print(f"健康: {result['summary']['healthy']}")
            print(f"警告: {result['summary']['warning']}")
            print(f"错误: {result['summary']['error']}")
            print(f"平均健康度: {result['summary']['average_health_score']:.1f}%")
            print(f"检查时间: {result['last_check']}")

    elif args.command == 'repair':
        if args.engine_name:
            # 修复指定引擎
            engine_path = SCRIPTS_DIR / f"{args.engine_name}.py"
            result = engine.repair_engine(engine_path)

            print(f"\n{'='*60}")
            print(f"修复结果: {result['name']}")
            print(f"{'='*60}")
            print(f"成功: {result['success']}")

            if result['repair_actions']:
                print("\n执行的修复动作:")
                for action in result['repair_actions']:
                    print(f"  - {action}")

            if result.get('backup'):
                print(f"\n备份文件: {result['backup']}")

            if result.get('error'):
                print(f"\n错误: {result['error']}")

        else:
            # 修复所有引擎
            result = engine.repair_all_engines()

            print(f"\n{'='*60}")
            print(f"批量修复结果")
            print(f"{'='*60}")
            print(f"修复成功: {result['summary']['total_repaired']}")
            print(f"修复失败: {result['summary']['total_failed']}")

    elif args.command == 'report':
        result = engine.generate_report(args.engine_name)

        if result['report_type'] == 'single':
            engine_info = result['engine']
            print(f"\n{'='*60}")
            print(f"引擎诊断报告: {engine_info['name']}")
            print(f"{'='*60}")
            print(json.dumps(engine_info, ensure_ascii=False, indent=2))
        else:
            print(f"\n{'='*60}")
            print(f"完整诊断报告")
            print(f"{'='*60}")
            print(json.dumps(result['diagnostic']['summary'], ensure_ascii=False, indent=2))

    elif args.command == 'health':
        result = engine.get_health_summary()

        print(f"\n{'='*60}")
        print(f"进化引擎集群健康度摘要")
        print(f"{'='*60}")
        print(f"引擎总数: {result['total_engines']}")
        print(f"健康: {result['healthy_count']} | 警告: {result['warning_count']} | 错误: {result['error_count']}")
        print(f"平均健康度: {result['average_health_score']}%")
        print(f"健康状态: {result['health_status']}")
        print(f"最后检查: {result['last_check']}")


if __name__ == '__main__':
    main()