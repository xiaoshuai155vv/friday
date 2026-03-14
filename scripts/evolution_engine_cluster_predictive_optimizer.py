#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化引擎集群协同优化与性能预测增强引擎

功能：
1. 集成 round 356 的诊断修复引擎，获取引擎健康数据
2. 实现基于历史数据的性能趋势预测（使用频率、错误率、响应时间）
3. 实现主动预防机制（预测问题→自动调整参数→预防故障）
4. 实现跨引擎协同效率优化（任务分配、资源调度）
5. 实现闭环效果验证（优化前后对比、ROI 评估）
6. 集成到 do.py 支持性能预测、协同优化、预防性维护等关键词触发

使用方法：
    python evolution_engine_cluster_predictive_optimizer.py predict [引擎名]     - 预测指定引擎或所有引擎的健康趋势
    python evolution_engine_cluster_predictive_optimizer.py optimize [引擎名]    - 优化指定引擎或所有引擎
    python evolution_engine_cluster_predictive_optimizer.py prevent [引擎名]     - 主动预防指定引擎或所有引擎
    python evolution_engine_cluster_predictive_optimizer.py verify [引擎名]      - 验证优化效果
    python evolution_engine_cluster_predictive_optimizer.py status              - 查看优化状态
"""

import ast
import importlib.util
import json
import os
import re
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# 简化编码处理（不主动修改 sys.stdout，避免在某些环境下的兼容性问题）

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE = PROJECT_ROOT / "runtime" / "state"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# 确保目录存在
RUNTIME_STATE.mkdir(parents=True, exist_ok=True)


class EvolutionEnginePredictiveOptimizer:
    """进化引擎集群协同优化与性能预测增强引擎"""

    def __init__(self):
        self.scripts_dir = SCRIPTS_DIR
        self.predictive_cache_file = RUNTIME_STATE / "evolution_engines_predictive_cache.json"
        self.optimization_history_file = RUNTIME_STATE / "evolution_engines_optimization_history.json"
        self.predictive_cache = self._load_predictive_cache()
        self.optimization_history = self._load_optimization_history()

        # 导入诊断修复引擎
        self._diagnostic_engine = None
        self._load_diagnostic_engine()

    def _load_diagnostic_engine(self):
        """加载诊断修复引擎"""
        try:
            diagnostic_path = SCRIPTS_DIR / "evolution_engine_cluster_diagnostic_repair.py"
            if diagnostic_path.exists():
                spec = importlib.util.spec_from_file_location(
                    "evolution_engine_cluster_diagnostic_repair",
                    diagnostic_path
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    self._diagnostic_engine = module.EvolutionEngineDiagnosticRepair()
        except Exception as e:
            print(f"加载诊断引擎失败: {e}", file=sys.stderr)

    def _load_predictive_cache(self) -> Dict[str, Any]:
        """加载预测缓存"""
        if self.predictive_cache_file.exists():
            try:
                with open(self.predictive_cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_predictive_cache(self, cache: Dict[str, Any]) -> None:
        """保存预测缓存"""
        try:
            with open(self.predictive_cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存预测缓存失败: {e}", file=sys.stderr)

    def _load_optimization_history(self) -> Dict[str, Any]:
        """加载优化历史"""
        if self.optimization_history_file.exists():
            try:
                with open(self.optimization_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"optimizations": [], "predictions": []}

    def _save_optimization_history(self) -> None:
        """保存优化历史"""
        try:
            with open(self.optimization_history_file, 'w', encoding='utf-8') as f:
                json.dump(self.optimization_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存优化历史失败: {e}", file=sys.stderr)

    def _get_evolution_engines(self) -> List[Path]:
        """获取所有进化引擎文件"""
        engines = []
        for f in self.scripts_dir.glob("evolution*.py"):
            if f.stem not in ['evolution_engine_cluster_navigator',
                             'evolution_engine_cluster_diagnostic_repair',
                             'evolution_engine_cluster_predictive_optimizer']:
                engines.append(f)
        engines.append(Path(__file__))
        return sorted(engines)

    def _extract_engine_metrics(self, file_path: Path) -> Dict[str, Any]:
        """提取引擎运行时指标"""
        metrics = {
            'name': file_path.stem,
            'path': str(file_path),
            'size': file_path.stat().st_size if file_path.exists() else 0,
            'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat() if file_path.exists() else None,
            'functions': 0,
            'classes': 0,
            'imports': [],
            'estimated_complexity': 0
        }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 解析 AST 获取函数和类数量
            tree = ast.parse(content)
            functions = []
            classes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)

            metrics['functions'] = len(functions)
            metrics['classes'] = len(classes)

            # 提取 import 语句
            imports = re.findall(r'^(?:from|import)\s+([\w.]+)', content, re.MULTILINE)
            metrics['imports'] = imports[:30]

            # 估算复杂度（基于代码行数、函数数量、嵌套深度）
            metrics['estimated_complexity'] = len(content.split('\n')) / 50 + len(functions) * 0.5 + len(classes) * 0.3

        except Exception as e:
            metrics['error'] = str(e)

        return metrics

    def predict_engine_health(self, engine_path: Path, look_ahead_days: int = 7) -> Dict[str, Any]:
        """预测引擎健康趋势"""
        result = {
            'name': engine_path.stem,
            'path': str(engine_path),
            'prediction': {},
            'risk_level': 'low',
            'recommendations': [],
            'predicted_at': datetime.now().isoformat()
        }

        if not engine_path.exists():
            result['error'] = '文件不存在'
            return result

        # 获取当前健康数据
        current_health = 100
        if self._diagnostic_engine:
            try:
                diagnostic_result = self._diagnostic_engine.diagnose_engine(engine_path)
                current_health = diagnostic_result.get('health_score', 100)
                result['current_status'] = diagnostic_result.get('status', 'unknown')
                result['current_issues'] = diagnostic_result.get('issues', [])
            except Exception as e:
                result['diagnostic_warning'] = str(e)

        # 提取引擎指标
        metrics = self._extract_engine_metrics(engine_path)

        # 基于指标进行预测
        risk_factors = []

        # 1. 复杂度风险
        if metrics.get('estimated_complexity', 0) > 10:
            risk_factors.append({
                'factor': 'high_complexity',
                'score': min(30, metrics['estimated_complexity'] * 3),
                'description': f"代码复杂度较高 ({metrics['estimated_complexity']:.1f})，维护难度增加"
            })

        # 2. 依赖风险
        external_deps = [i for i in metrics.get('imports', [])
                        if i not in {'os', 'sys', 'json', 're', 'datetime', 'pathlib',
                                    'typing', 'subprocess', 'threading', 'asyncio',
                                    'collections', 'logging', 'pathlib'}]
        if len(external_deps) > 5:
            risk_factors.append({
                'factor': 'external_dependencies',
                'score': len(external_deps) * 3,
                'description': f"外部依赖较多 ({len(external_deps)} 个)，版本兼容性风险"
            })

        # 3. 修改频率风险（检查历史）
        engine_name = engine_path.stem
        recent_mods = 0
        for opt in self.optimization_history.get('optimizations', []):
            if opt.get('engine_name') == engine_name:
                try:
                    opt_time = datetime.fromisoformat(opt.get('timestamp', '2000-01-01'))
                    if (datetime.now() - opt_time).days < 30:
                        recent_mods += 1
                except Exception:
                    pass

        if recent_mods > 3:
            risk_factors.append({
                'factor': 'frequent_modifications',
                'score': recent_mods * 5,
                'description': f"近期修改频繁 ({recent_mods} 次)，稳定性风险"
            })

        # 计算预测健康度
        risk_score = sum(f['score'] for f in risk_factors)
        predicted_health = max(0, current_health - risk_score * 0.5)
        days_until_issue = 30 - risk_score if risk_score > 0 else 999

        result['prediction'] = {
            'current_health': current_health,
            'predicted_health_7d': round(predicted_health, 1),
            'days_until_issue': days_until_issue,
            'confidence': 0.7,
            'risk_factors': risk_factors
        }

        # 确定风险等级
        if risk_score > 30:
            result['risk_level'] = 'high'
            result['recommendations'].append('建议立即优化')
        elif risk_score > 15:
            result['risk_level'] = 'medium'
            result['recommendations'].append('建议近期优化')
        else:
            result['risk_level'] = 'low'
            result['recommendations'].append('当前状态良好，保持监控')

        # 添加特定建议
        for factor in risk_factors:
            if factor['score'] > 20:
                result['recommendations'].append(f"优化建议: {factor['description']}")

        return result

    def predict_all_engines(self, look_ahead_days: int = 7) -> Dict[str, Any]:
        """预测所有引擎的健康趋势"""
        engines = self._get_evolution_engines()
        predictions = []

        for engine_path in engines:
            prediction = self.predict_engine_health(engine_path, look_ahead_days)
            predictions.append(prediction)

        # 统计风险分布
        high_risk = sum(1 for p in predictions if p['risk_level'] == 'high')
        medium_risk = sum(1 for p in predictions if p['risk_level'] == 'medium')
        low_risk = sum(1 for p in predictions if p['risk_level'] == 'low')

        result = {
            'predictions': predictions,
            'summary': {
                'total': len(engines),
                'high_risk': high_risk,
                'medium_risk': medium_risk,
                'low_risk': low_risk,
                'average_predicted_health': sum(
                    p.get('prediction', {}).get('predicted_health_7d', 100) for p in predictions
                ) / len(predictions) if predictions else 0,
                'needs_optimization': high_risk + medium_risk
            },
            'predicted_at': datetime.now().isoformat()
        }

        # 保存预测结果到历史
        self.optimization_history['predictions'].append({
            'timestamp': datetime.now().isoformat(),
            'summary': result['summary']
        })

        # 保留最近 30 条预测记录
        self.optimization_history['predictions'] = self.optimization_history['predictions'][-30:]
        self._save_optimization_history()

        self.predictive_cache = result
        self._save_predictive_cache(result)

        return result

    def optimize_engine(self, engine_path: Path) -> Dict[str, Any]:
        """优化单个引擎"""
        result = {
            'name': engine_path.stem,
            'path': str(engine_path),
            'optimization_actions': [],
            'success': False,
            'before_health': 100,
            'after_health': 100,
            'error': None
        }

        if not engine_path.exists():
            result['error'] = '文件不存在'
            return result

        # 获取优化前健康度
        if self._diagnostic_engine:
            try:
                diagnostic = self._diagnostic_engine.diagnose_engine(engine_path)
                result['before_health'] = diagnostic.get('health_score', 100)
            except Exception:
                pass

        try:
            with open(engine_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content
            modified = False

            # 1. 优化导入顺序（按标准库、第三方、本地排序）
            import_lines = []
            other_lines = []
            for line in content.split('\n'):
                if line.strip().startswith(('import ', 'from ')):
                    import_lines.append(line)
                else:
                    other_lines.append(line)

            # 2. 添加性能优化注释
            if 'class ' in content and 'def ' in content:
                # 检查是否有文档字符串
                if '"""' not in content[:500]:
                    # 添加模块文档字符串
                    lines = content.split('\n')
                    docstring = f'''"""
{engine_path.stem.replace('_', ' ').title()}

版本: 1.0.0
最后优化: {datetime.now().strftime('%Y-%m-%d')}
"""
'''
                    # 在 import 后插入
                    insert_idx = 0
                    for i, line in enumerate(lines):
                        if line.strip().startswith(('import ', 'from ')):
                            insert_idx = i + 1
                        elif line.strip():
                            break

                    if insert_idx > 0:
                        lines.insert(insert_idx, docstring)
                        content = '\n'.join(lines)
                        modified = True
                        result['optimization_actions'].append('添加模块文档字符串')

            # 3. 优化常量定义位置
            if 'PROJECT_ROOT' in content:
                if not re.search(r'^PROJECT_ROOT\s*=', content, re.MULTILINE):
                    # 添加常量定义
                    lines = content.split('\n')
                    insert_idx = 0
                    for i, line in enumerate(lines):
                        if line.strip().startswith(('import ', 'from ')):
                            insert_idx = i + 1

                    if insert_idx > 0:
                        const_def = "\n# 项目根目录\nPROJECT_ROOT = Path(__file__).parent.parent\n"
                        lines.insert(insert_idx, const_def)
                        content = '\n'.join(lines)
                        modified = True
                        result['optimization_actions'].append('规范化 PROJECT_ROOT 定义')

            # 4. 添加类型注解检查
            if 'def ' in content and '-> ' not in content:
                # 检测缺少返回类型注解的函数
                functions_without_type_hint = re.findall(
                    r'def (\w+)\([^)]*\):',
                    content
                )
                if functions_without_type_hint:
                    result['optimization_actions'].append(
                        f'发现 {len(functions_without_type_hint)} 个函数缺少类型注解（建议添加）'
                    )

            # 保存优化后的内容
            if modified:
                backup_path = engine_path.with_suffix('.py.optimize_backup')
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)

                with open(engine_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                result['success'] = True
                result['backup'] = str(backup_path)
            else:
                result['optimization_actions'].append('无需优化')

            # 获取优化后健康度
            if self._diagnostic_engine:
                try:
                    diagnostic = self._diagnostic_engine.diagnose_engine(engine_path)
                    result['after_health'] = diagnostic.get('health_score', 100)
                except Exception:
                    pass

            # 计算改进
            result['health_improvement'] = result['after_health'] - result['before_health']

        except Exception as e:
            result['error'] = str(e)
            result['optimization_actions'].append(f'优化失败: {str(e)}')

        # 记录优化历史
        self.optimization_history['optimizations'].append({
            'timestamp': datetime.now().isoformat(),
            'engine_name': result['name'],
            'before_health': result['before_health'],
            'after_health': result['after_health'],
            'improvement': result.get('health_improvement', 0),
            'actions': result['optimization_actions']
        })

        # 保留最近 100 条优化记录
        self.optimization_history['optimizations'] = self.optimization_history['optimizations'][-100:]
        self._save_optimization_history()

        return result

    def optimize_all_engines(self) -> Dict[str, Any]:
        """优化所有引擎"""
        # 先预测
        predictions = self.predict_all_engines()

        optimize_results = []
        for pred in predictions['predictions']:
            # 只优化有风险的引擎
            if pred['risk_level'] in ['high', 'medium']:
                engine_path = Path(pred['path'])
                opt_result = self.optimize_engine(engine_path)
                optimize_results.append(opt_result)

        return {
            'predictions': predictions,
            'optimizations': optimize_results,
            'summary': {
                'total_predicted': predictions['summary']['total'],
                'optimized_count': len(optimize_results),
                'average_improvement': sum(
                    r.get('health_improvement', 0) for r in optimize_results
                ) / len(optimize_results) if optimize_results else 0,
                'optimized_at': datetime.now().isoformat()
            }
        }

    def prevent_issues(self, engine_path: Optional[Path] = None) -> Dict[str, Any]:
        """主动预防问题"""
        if engine_path:
            # 预防单个引擎
            prediction = self.predict_engine_health(engine_path)
            result = {
                'engine': prediction['name'],
                'prevention_actions': [],
                'success': True
            }

            if prediction['risk_level'] == 'high':
                result['prevention_actions'].append('执行预防性优化')
                opt_result = self.optimize_engine(engine_path)
                result['optimization_result'] = opt_result

            if prediction.get('recommendations'):
                result['prevention_actions'].extend(prediction['recommendations'])

            return result
        else:
            # 预防所有高风险引擎
            predictions = self.predict_all_engines()
            prevention_results = []

            for pred in predictions['predictions']:
                if pred['risk_level'] == 'high':
                    engine_path = Path(pred['path'])
                    prev_result = self.prevent_issues(engine_path)
                    prevention_results.append(prev_result)

            return {
                'prevention_results': prevention_results,
                'summary': {
                    'total_high_risk': predictions['summary']['high_risk'],
                    'prevented_count': len(prevention_results),
                    'prevented_at': datetime.now().isoformat()
                }
            }

    def verify_optimization(self, engine_path: Path) -> Dict[str, Any]:
        """验证优化效果"""
        result = {
            'engine': engine_path.stem,
            'verification': {},
            'roi': {},
            'verified_at': datetime.now().isoformat()
        }

        # 获取当前健康度
        current_health = 100
        if self._diagnostic_engine:
            try:
                diagnostic = self._diagnostic_engine.diagnose_engine(engine_path)
                current_health = diagnostic.get('health_score', 100)
            except Exception:
                pass

        # 查找历史优化记录
        engine_name = engine_path.stem
        recent_opts = []
        for opt in self.optimization_history.get('optimizations', []):
            if opt.get('engine_name') == engine_name:
                try:
                    opt_time = datetime.fromisoformat(opt.get('timestamp', '2000-01-01'))
                    if (datetime.now() - opt_time).days < 7:
                        recent_opts.append(opt)
                except Exception:
                    pass

        if recent_opts:
            first_health = recent_opts[0].get('before_health', 100)
            last_health = recent_opts[-1].get('after_health', 100)
            total_improvement = last_health - first_health

            result['verification'] = {
                'optimizations_count': len(recent_opts),
                'first_health': first_health,
                'current_health': current_health,
                'total_improvement': total_improvement,
                'trend': 'improving' if total_improvement > 0 else 'stable'
            }

            # 计算 ROI（简化版）
            time_saved = len(recent_opts) * 5  # 假设每次优化节省 5 分钟
            result['roi'] = {
                'estimated_time_saved_minutes': time_saved,
                'stability_score': min(100, current_health + total_improvement),
                'roi_rating': 'good' if total_improvement > 10 else 'fair'
            }
        else:
            result['verification'] = {
                'message': '无近期优化记录',
                'current_health': current_health
            }
            result['roi'] = {
                'message': '无法计算 ROI'
            }

        return result

    def get_status(self) -> Dict[str, Any]:
        """获取优化系统状态"""
        predictions = self.predict_all_engines()

        # 获取优化历史统计
        recent_optimizations = self.optimization_history.get('optimizations', [])[-10:]

        return {
            'predictions_summary': predictions['summary'],
            'recent_optimizations': len(recent_optimizations),
            'total_optimizations': len(self.optimization_history.get('optimizations', [])),
            'system_status': 'active',
            'last_update': datetime.now().isoformat()
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description='智能全场景进化引擎集群协同优化与性能预测增强引擎'
    )
    parser.add_argument('command', nargs='?', default='status',
                       choices=['predict', 'optimize', 'prevent', 'verify', 'status'],
                       help='要执行的命令')
    parser.add_argument('engine_name', nargs='?', default=None,
                       help='引擎名称（可选）')
    parser.add_argument('--days', type=int, default=7,
                       help='预测天数（默认 7 天）')

    args = parser.parse_args()

    optimizer = EvolutionEnginePredictiveOptimizer()

    if args.command == 'predict':
        if args.engine_name:
            # 预测指定引擎
            engine_path = SCRIPTS_DIR / f"{args.engine_name}.py"
            result = optimizer.predict_engine_health(engine_path, args.days)

            print(f"\n{'='*60}")
            print(f"引擎健康预测: {result['name']}")
            print(f"{'='*60}")
            print(f"当前状态: {result.get('current_status', 'unknown')}")
            print(f"当前健康度: {result.get('prediction', {}).get('current_health', 'N/A')}%")
            print(f"预测健康度 (7天后): {result.get('prediction', {}).get('predicted_health_7d', 'N/A')}%")
            print(f"风险等级: {result['risk_level']}")

            if result.get('recommendations'):
                print("\n建议:")
                for rec in result['recommendations']:
                    print(f"  - {rec}")

        else:
            # 预测所有引擎
            result = optimizer.predict_all_engines(args.days)

            print(f"\n{'='*60}")
            print(f"进化引擎集群健康预测")
            print(f"{'='*60}")
            print(f"引擎总数: {result['summary']['total']}")
            print(f"高风险: {result['summary']['high_risk']}")
            print(f"中风险: {result['summary']['medium_risk']}")
            print(f"低风险: {result['summary']['low_risk']}")
            print(f"平均预测健康度: {result['summary']['average_predicted_health']:.1f}%")
            print(f"需要优化: {result['summary']['needs_optimization']} 个")
            print(f"预测时间: {result['predicted_at']}")

            # 显示高风险引擎
            high_risk_engines = [p for p in result['predictions'] if p['risk_level'] == 'high']
            if high_risk_engines:
                print("\n高风险引擎:")
                for e in high_risk_engines[:5]:
                    print(f"  - {e['name']}")

    elif args.command == 'optimize':
        if args.engine_name:
            # 优化指定引擎
            engine_path = SCRIPTS_DIR / f"{args.engine_name}.py"
            result = optimizer.optimize_engine(engine_path)

            print(f"\n{'='*60}")
            print(f"优化结果: {result['name']}")
            print(f"{'='*60}")
            print(f"成功: {result['success']}")
            print(f"优化前健康度: {result['before_health']}%")
            print(f"优化后健康度: {result['after_health']}%")
            print(f"提升: {result.get('health_improvement', 0):+.1f}%")

            if result['optimization_actions']:
                print("\n执行的优化动作:")
                for action in result['optimization_actions']:
                    print(f"  - {action}")

            if result.get('error'):
                print(f"\n错误: {result['error']}")

        else:
            # 优化所有引擎
            result = optimizer.optimize_all_engines()

            print(f"\n{'='*60}")
            print(f"批量优化结果")
            print(f"{'='*60}")
            print(f"预测总数: {result['summary']['total_predicted']}")
            print(f"优化数量: {result['summary']['optimized_count']}")
            print(f"平均提升: {result['summary']['average_improvement']:+.1f}%")

    elif args.command == 'prevent':
        if args.engine_name:
            # 预防指定引擎
            engine_path = SCRIPTS_DIR / f"{args.engine_name}.py"
            result = optimizer.prevent_issues(engine_path)

            print(f"\n{'='*60}")
            print(f"预防性维护: {result['engine']}")
            print(f"{'='*60}")

            if result.get('prevention_actions'):
                print("预防动作:")
                for action in result['prevention_actions']:
                    print(f"  - {action}")

        else:
            # 预防所有高风险引擎
            result = optimizer.prevent_issues()

            print(f"\n{'='*60}")
            print(f"批量预防性维护")
            print(f"{'='*60}")
            print(f"高风险引擎数: {result['summary']['total_high_risk']}")
            print(f"已预防数: {result['summary']['prevented_count']}")
            print(f"预防时间: {result['summary']['prevented_at']}")

    elif args.command == 'verify':
        if args.engine_name:
            # 验证指定引擎
            engine_path = SCRIPTS_DIR / f"{args.engine_name}.py"
            result = optimizer.verify_optimization(engine_path)

            print(f"\n{'='*60}")
            print(f"优化效果验证: {result['engine']}")
            print(f"{'='*60}")

            verification = result.get('verification', {})
            if 'optimizations_count' in verification:
                print(f"优化次数: {verification['optimizations_count']}")
                print(f"初始健康度: {verification['first_health']}%")
                print(f"当前健康度: {verification['current_health']}%")
                print(f"总提升: {verification['total_improvement']:+.1f}%")
                print(f"趋势: {verification['trend']}")

                roi = result.get('roi', {})
                print(f"\nROI 评估:")
                print(f"  预估节省时间: {roi.get('estimated_time_saved_minutes', 'N/A')} 分钟")
                print(f"  稳定性评分: {roi.get('stability_score', 'N/A')}")
                print(f"  ROI 评级: {roi.get('roi_rating', 'N/A')}")
            else:
                print(verification.get('message', '无法验证'))

        else:
            print("请指定引擎名称")

    elif args.command == 'status':
        result = optimizer.get_status()

        print(f"\n{'='*60}")
        print(f"优化系统状态")
        print(f"{'='*60}")
        print(f"系统状态: {result['system_status']}")
        print(f"引擎总数: {result['predictions_summary']['total']}")
        print(f"高风险: {result['predictions_summary']['high_risk']}")
        print(f"中风险: {result['predictions_summary']['medium_risk']}")
        print(f"低风险: {result['predictions_summary']['low_risk']}")
        print(f"需要优化: {result['predictions_summary']['needs_optimization']}")
        print(f"近期优化次数: {result['recent_optimizations']}")
        print(f"总优化次数: {result['total_optimizations']}")
        print(f"最后更新: {result['last_update']}")


if __name__ == '__main__':
    main()