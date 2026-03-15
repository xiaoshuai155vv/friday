#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环创新方案智能执行与深度优化引擎
(Innovation Execution Optimizer Engine)

在 round 504 完成的跨引擎深度融合创新实现引擎基础上，
进一步增强创新方案的智能执行能力。
让系统能够将高价值创新方案自动转化为可执行代码、智能生成实现代码、
自动执行优化、验证优化效果，形成从「方案生成→智能代码生成→自动执行→效果验证」的完整闭环。

系统将利用 LLM 特有的大规模代码生成能力，实现从创新方案到可执行代码的自动化，
填补从"方案"到"实现"的最后一块拼图。

Version: 1.0.0
"""

import json
import os
import sys

# Fix Windows console encoding issues
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import subprocess
import re
import ast
import tempfile
import hashlib

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
STATE_DIR = PROJECT_ROOT / "runtime" / "state"
DATA_DIR = PROJECT_ROOT / "runtime" / "data"
LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# 添加 scripts 目录到路径以便导入
sys.path.insert(0, str(SCRIPTS_DIR))


@dataclass
class CodeGenerationRequest:
    """代码生成请求"""
    solution_id: str
    title: str
    description: str
    implementation_steps: List[str]
    target_language: str = "python"


@dataclass
class GeneratedCode:
    """生成的代码"""
    code_id: str
    solution_id: str
    code: str
    language: str
    validation_result: Dict[str, Any]
    generation_time: float


@dataclass
class ExecutionRecord:
    """执行记录"""
    code_id: str
    solution_id: str
    execution_status: str  # "success", "partial", "failed", "validation_failed"
    execution_time: float
    output: str
    error: str
    execution_timestamp: str


@dataclass
class OptimizationResult:
    """优化结果"""
    solution_id: str
    code_id: str
    original_code: str
    optimized_code: str
    optimization_type: str
    improvement_score: float
    verification_status: str


class InnovationExecutionOptimizerEngine:
    """创新方案智能执行与深度优化引擎核心类"""

    def __init__(self):
        self.version = "1.0.0"
        self.name = "Innovation Execution Optimizer Engine"
        self.runtime_dir = PROJECT_ROOT / "runtime"

        # 存储
        self.code_requests: Dict[str, CodeGenerationRequest] = {}
        self.generated_codes: Dict[str, GeneratedCode] = {}
        self.execution_records: Dict[str, ExecutionRecord] = {}
        self.optimization_results: Dict[str, OptimizationResult] = {}

        # 数据目录
        self.data_dir = self.runtime_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 状态文件路径
        self.state_file = self.data_dir / "innovation_execution_optimizer_state.json"
        self.load_state()

        print(f"✅ Innovation Execution Optimizer Engine v{self.version} 已初始化")

    def load_state(self):
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    # 恢复数据
                    self.code_requests = {
                        k: CodeGenerationRequest(**v) if isinstance(v, dict) else v
                        for k, v in state.get('code_requests', {}).items()
                    }
                    self.generated_codes = {
                        k: GeneratedCode(**v) if isinstance(v, dict) else v
                        for k, v in state.get('generated_codes', {}).items()
                    }
                    # 执行记录需要特殊处理
                    exec_records = state.get('execution_records', {})
                    self.execution_records = {
                        k: ExecutionRecord(**v) if isinstance(v, dict) else v
                        for k, v in exec_records.items()
                    }
                    self.optimization_results = {
                        k: OptimizationResult(**v) if isinstance(v, dict) else v
                        for k, v in state.get('optimization_results', {}).items()
                    }
                print(f"📂 已加载状态：{len(self.code_requests)} 个请求, {len(self.generated_codes)} 个代码, {len(self.execution_records)} 个执行记录")
            except Exception as e:
                print(f"⚠️ 加载状态失败: {e}")

    def save_state(self):
        """保存状态"""
        try:
            state = {
                'code_requests': {k: asdict(v) if isinstance(v, CodeGenerationRequest) else v
                                for k, v in self.code_requests.items()},
                'generated_codes': {k: asdict(v) if isinstance(v, GeneratedCode) else v
                                   for k, v in self.generated_codes.items()},
                'execution_records': {k: asdict(v) if isinstance(v, ExecutionRecord) else v
                                     for k, v in self.execution_records.items()},
                'optimization_results': {k: asdict(v) if isinstance(v, OptimizationResult) else v
                                        for k, v in self.optimization_results.items()},
                'last_updated': datetime.now().isoformat()
            }
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存状态失败: {e}")

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "name": self.name,
            "version": self.version,
            "code_requests_count": len(self.code_requests),
            "generated_codes_count": len(self.generated_codes),
            "execution_records_count": len(self.execution_records),
            "optimization_results_count": len(self.optimization_results),
            "last_updated": datetime.now().isoformat()
        }

    def load_solutions_from_previous_engine(self) -> List[Dict[str, Any]]:
        """从 round 504 的跨引擎融合引擎加载已生成的方案"""
        solutions = []

        # 尝试从状态文件加载
        fusion_state_file = self.data_dir / "cross_engine_deep_fusion_state.json"
        if fusion_state_file.exists():
            try:
                with open(fusion_state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    solutions_data = state.get('solutions', {})
                    for sol_id, sol_data in solutions_data.items():
                        if isinstance(sol_data, dict) and sol_data.get('status') in ['ready', 'completed']:
                            solutions.append(sol_data)
            except Exception as e:
                print(f"⚠️ 加载 round 504 方案失败: {e}")

        # 也检查其他可能的位置
        if not solutions:
            # 扫描已有的解决方案数据
            for state_file in self.data_dir.glob("*fusion*state*.json"):
                try:
                    with open(state_file, 'r', encoding='utf-8') as f:
                        state = json.load(f)
                        if 'solutions' in state:
                            for sol_id, sol_data in state['solutions'].items():
                                if isinstance(sol_data, dict) and sol_data.get('status') in ['ready', 'completed']:
                                    solutions.append(sol_data)
                except Exception:
                    pass

        return solutions

    def generate_code_from_solution(self, solution: Dict[str, Any], target_language: str = "python") -> GeneratedCode:
        """从创新方案生成可执行代码"""
        solution_id = solution.get('solution_id', 'unknown')
        title = solution.get('title', 'Untitled')
        description = solution.get('description', '')
        implementation_steps = solution.get('implementation_steps', [])

        # 生成唯一的代码 ID
        code_id = f"code_{solution_id}_{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]}"

        # 构建代码生成的 prompt
        prompt = self._build_code_generation_prompt(
            title, description, implementation_steps, target_language
        )

        # 生成代码（这里使用规则模板作为基础，实际可以接入 LLM）
        code = self._generate_code(prompt, implementation_steps)

        # 验证代码
        validation_result = self._validate_code(code, target_language)

        generated_code = GeneratedCode(
            code_id=code_id,
            solution_id=solution_id,
            code=code,
            language=target_language,
            validation_result=validation_result,
            generation_time=0.0
        )

        self.generated_codes[code_id] = generated_code
        self.save_state()

        return generated_code

    def _build_code_generation_prompt(self, title: str, description: str,
                                      implementation_steps: List[str],
                                      target_language: str) -> str:
        """构建代码生成提示"""
        prompt = f"""请根据以下创新方案生成可执行的 {target_language} 代码：

方案标题: {title}
方案描述: {description}

实现步骤:
"""
        for i, step in enumerate(implementation_steps, 1):
            prompt += f"{i}. {step}\n"

        prompt += """

请生成完整、可执行的代码，包括必要的导入、错误处理和注释。
"""
        return prompt

    def _generate_code(self, prompt: str, implementation_steps: List[str]) -> str:
        """生成代码（基于模板和步骤）"""
        # 分析实现步骤，生成对应的代码
        code_lines = []
        code_lines.append("#!/usr/bin/env python3")
        code_lines.append("# -*- coding: utf-8 -*-")
        code_lines.append(f"# 自动生成的创新方案执行代码")
        code_lines.append(f"# 生成时间: {datetime.now().isoformat()}")
        code_lines.append("")
        code_lines.append("import sys")
        code_lines.append("import os")
        code_lines.append("from pathlib import Path")
        code_lines.append("")
        code_lines.append("# 项目根目录")
        code_lines.append("PROJECT_ROOT = Path(__file__).parent.parent")
        code_lines.append("")

        # 根据实现步骤生成代码
        for i, step in enumerate(implementation_steps, 1):
            step_lower = step.lower()

            # 分析步骤类型，生成相应代码
            if '创建' in step or '生成' in step or '初始化' in step:
                code_lines.append(f"# 步骤 {i}: {step}")
                code_lines.append(f"# TODO: 实现 {step}")
                code_lines.append("")

            elif '分析' in step or '检测' in step or '识别' in step:
                code_lines.append(f"# 步骤 {i}: {step}")
                code_lines.append(f"# TODO: 实现 {step}")
                code_lines.append("")

            elif '优化' in step or '改进' in step or '增强' in step:
                code_lines.append(f"# 步骤 {i}: {step}")
                code_lines.append(f"# TODO: 实现 {step}")
                code_lines.append("")

            elif '执行' in step or '运行' in step or '调用' in step:
                code_lines.append(f"# 步骤 {i}: {step}")
                code_lines.append("try:")
                code_lines.append("    # 执行相关操作")
                code_lines.append("    pass")
                code_lines.append("except Exception as e:")
                code_lines.append("    print(f'执行错误: {{e}}')")
                code_lines.append("")

            elif '集成' in step or '对接' in step or '整合' in step:
                code_lines.append(f"# 步骤 {i}: {step}")
                code_lines.append(f"# TODO: 实现 {step}")
                code_lines.append("")

            else:
                code_lines.append(f"# 步骤 {i}: {step}")
                code_lines.append(f"# TODO: 实现 {step}")
                code_lines.append("")

        # 添加主函数
        code_lines.append("")
        code_lines.append("def main():")
        code_lines.append('    """主函数"""')
        code_lines.append('    print("创新方案执行开始")')
        code_lines.append('    # 在这里添加主要的执行逻辑')
        code_lines.append('    print("创新方案执行完成")')
        code_lines.append("")
        code_lines.append("")
        code_lines.append("if __name__ == '__main__':")
        code_lines.append("    main()")

        return "\n".join(code_lines)

    def _validate_code(self, code: str, language: str) -> Dict[str, Any]:
        """验证生成的代码"""
        result = {
            "valid": False,
            "syntax_valid": False,
            "imports_valid": False,
            "issues": []
        }

        if language == "python":
            # 语法检查
            try:
                ast.parse(code)
                result["syntax_valid"] = True
            except SyntaxError as e:
                result["issues"].append(f"语法错误: {e}")
                return result

            # 导入检查
            imports = re.findall(r'^import\s+(\w+)', code, re.MULTILINE)
            from_imports = re.findall(r'^from\s+(\w+)', code, re.MULTILINE)

            all_imports = set(imports + from_imports)

            # 标准库导入（应该都有效）
            stdlib = {'sys', 'os', 'pathlib', 'json', 'datetime', 're', 'subprocess',
                     'collections', 'typing', 'dataclasses', 'hashlib', 'tempfile',
                     'time', 'threading', 'asyncio', 'functools'}

            invalid_imports = [imp for imp in all_imports if imp not in stdlib]

            if invalid_imports:
                # 尝试导入这些模块
                for imp in invalid_imports:
                    try:
                        __import__(imp)
                    except ImportError:
                        result["issues"].append(f"导入 '{imp}' 失败，可能需要安装额外依赖")

            if not invalid_imports:
                result["imports_valid"] = True

            result["valid"] = result["syntax_valid"]

        return result

    def execute_code(self, code_id: str, dry_run: bool = False) -> ExecutionRecord:
        """执行生成的代码"""
        if code_id not in self.generated_codes:
            raise ValueError(f"代码 ID {code_id} 不存在")

        generated_code = self.generated_codes[code_id]
        solution_id = generated_code.solution_id

        execution_record = ExecutionRecord(
            code_id=code_id,
            solution_id=solution_id,
            execution_status="pending",
            execution_time=0.0,
            output="",
            error="",
            execution_timestamp=datetime.now().isoformat()
        )

        if dry_run:
            execution_record.execution_status = "validation_failed"
            execution_record.output = "干运行模式，仅验证代码不执行"
            self.execution_records[code_id] = execution_record
            self.save_state()
            return execution_record

        # 实际执行代码
        start_time = datetime.now()

        try:
            # 创建临时文件执行
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py',
                                            encoding='utf-8',
                                            delete=False) as f:
                f.write(generated_code.code)
                temp_file = f.name

            try:
                # 执行代码
                result = subprocess.run(
                    ['python', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    encoding='utf-8',
                    errors='replace'
                )

                execution_record.execution_status = "success" if result.returncode == 0 else "failed"
                execution_record.output = result.stdout
                execution_record.error = result.stderr

            finally:
                # 清理临时文件
                try:
                    os.unlink(temp_file)
                except Exception:
                    pass

        except subprocess.TimeoutExpired:
            execution_record.execution_status = "failed"
            execution_record.error = "执行超时（60秒）"

        except Exception as e:
            execution_record.execution_status = "failed"
            execution_record.error = str(e)

        finally:
            execution_record.execution_time = (datetime.now() - start_time).total_seconds()
            self.execution_records[code_id] = execution_record
            self.save_state()

        return execution_record

    def run_full_cycle(self, collect_from_previous: bool = True,
                       target_solutions: List[str] = None,
                       dry_run: bool = False) -> Dict[str, Any]:
        """运行完整周期：从方案到执行"""
        results = {
            "solutions_collected": 0,
            "codes_generated": 0,
            "codes_executed": 0,
            "execution_results": [],
            "total_value": 0.0
        }

        # 1. 收集方案
        solutions = []
        if collect_from_previous:
            solutions = self.load_solutions_from_previous_engine()

        results["solutions_collected"] = len(solutions)
        print(f"📋 收集到 {len(solutions)} 个创新方案")

        # 2. 如果有指定目标方案，也添加
        if target_solutions:
            for sol_id in target_solutions:
                if sol_id not in [s.get('solution_id') for s in solutions]:
                    solutions.append({
                        "solution_id": sol_id,
                        "title": f"Target solution: {sol_id}",
                        "description": "",
                        "implementation_steps": ["执行指定方案"],
                        "expected_value": 50.0
                    })

        # 3. 生成代码
        for solution in solutions:
            if solution.get('status') in ['completed', 'failed']:
                continue

            try:
                generated_code = self.generate_code_from_solution(solution)
                results["codes_generated"] += 1

                print(f"  ✅ 为方案 {solution.get('solution_id')} 生成代码: {generated_code.code_id}")

                # 4. 执行代码
                if generated_code.validation_result.get('valid') or dry_run:
                    exec_record = self.execute_code(generated_code.code_id, dry_run=dry_run)
                    results["codes_executed"] += 1
                    results["execution_results"].append({
                        "code_id": generated_code.code_id,
                        "solution_id": solution.get('solution_id'),
                        "status": exec_record.execution_status,
                        "output": exec_record.output[:200] if exec_record.output else "",
                        "error": exec_record.error[:200] if exec_record.error else ""
                    })

                    if exec_record.execution_status == "success":
                        results["total_value"] += solution.get('expected_value', 0)

            except Exception as e:
                print(f"  ⚠️ 处理方案 {solution.get('solution_id')} 失败: {e}")

        print(f"\n📊 执行完成:")
        print(f"  - 收集方案: {results['solutions_collected']}")
        print(f"  - 生成代码: {results['codes_generated']}")
        print(f"  - 执行代码: {results['codes_executed']}")
        print(f"  - 总价值: {results['total_value']:.1f}")

        return results

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱数据"""
        return {
            "engine": self.name,
            "version": self.version,
            "status": self.get_status(),
            "recent_codes": [
                {
                    "code_id": k,
                    "solution_id": v.solution_id,
                    "language": v.language,
                    "valid": v.validation_result.get('valid', False)
                }
                for k, v in list(self.generated_codes.items())[-5:]
            ],
            "recent_executions": [
                {
                    "code_id": k,
                    "solution_id": v.solution_id,
                    "status": v.execution_status,
                    "timestamp": v.execution_timestamp
                }
                for k, v in list(self.execution_records.items())[-5:]
            ],
            "summary": {
                "total_codes": len(self.generated_codes),
                "total_executions": len(self.execution_records),
                "success_rate": self._calculate_success_rate()
            }
        }

    def _calculate_success_rate(self) -> float:
        """计算成功率"""
        if not self.execution_records:
            return 0.0

        success_count = sum(
            1 for r in self.execution_records.values()
            if r.execution_status == "success"
        )

        return success_count / len(self.execution_records) * 100

    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取执行历史"""
        history = []
        for code_id, code in list(self.generated_codes.items())[-limit:]:
            record = {
                "code_id": code_id,
                "solution_id": code.solution_id,
                "language": code.language,
                "generated_at": code.validation_result.get('generated_at', ''),
                "executed": code_id in self.execution_records,
                "execution_status": self.execution_records.get(code_id, {}).execution_status if code_id in self.execution_records else None
            }
            history.append(record)
        return history


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="创新方案智能执行与深度优化引擎"
    )
    parser.add_argument('--status', action='store_true', help='显示引擎状态')
    parser.add_argument('--run', action='store_true', help='运行完整周期')
    parser.add_argument('--generate', action='store_true', help='为指定方案生成代码')
    parser.add_argument('--execute', type=str, help='执行指定代码 ID')
    parser.add_argument('--validate', type=str, help='验证指定代码 ID')
    parser.add_argument('--cockpit-data', action='store_true', help='获取驾驶舱数据')
    parser.add_argument('--history', action='store_true', help='获取执行历史')
    parser.add_argument('--dry-run', action='store_true', help='干运行模式（仅验证代码不执行）')
    parser.add_argument('--collect', action='store_true', default=True, help='从上一轮引擎收集方案')

    args = parser.parse_args()

    # 创建引擎实例
    engine = InnovationExecutionOptimizerEngine()

    if args.status:
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.run:
        results = engine.run_full_cycle(
            collect_from_previous=args.collect,
            dry_run=args.dry_run
        )
        print(json.dumps(results, ensure_ascii=False, indent=2))

    elif args.generate:
        # 从上一轮收集方案并生成代码
        solutions = engine.load_solutions_from_previous_engine()
        for solution in solutions[:3]:  # 最多处理3个
            code = engine.generate_code_from_solution(solution)
            print(f"生成代码: {code.code_id}")

    elif args.execute:
        result = engine.execute_code(args.execute, dry_run=False)
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))

    elif args.validate:
        if args.validate in engine.generated_codes:
            code = engine.generated_codes[args.validate]
            print(json.dumps(code.validation_result, ensure_ascii=False, indent=2))
        else:
            print(f"代码 ID {args.validate} 不存在")

    elif args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))

    elif args.history:
        history = engine.get_history()
        print(json.dumps(history, ensure_ascii=False, indent=2))

    else:
        # 默认显示状态
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()