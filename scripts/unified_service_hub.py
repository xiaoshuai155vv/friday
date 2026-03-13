"""
智能统一服务中枢引擎 (Unified Service Hub Engine)

整合所有智能服务能力，提供统一的自然语言服务入口，让用户通过一个入口
即可获得推荐、解释、执行、协同等完整服务体验。

功能：
1. 统一服务入口 - 一个命令入口接入所有智能服务
2. 智能服务路由 - 根据用户意图自动选择合适的服务引擎
3. 服务链编排 - 支持多引擎协同完成复杂任务
4. 结果聚合展示 - 统一格式输出各引擎结果
5. 服务状态追踪 - 追踪服务执行状态和学习用户偏好
"""

import json
import os
import sys
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class UnifiedServiceHub:
    """智能统一服务中枢"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.scripts_dir = self.project_root / "scripts"
        self.state_dir = self.project_root / "runtime" / "state"

        # 服务引擎映射
        self.service_engines = {
            "recommendation": {
                "unified_recommender": "unified_recommender.py",
                "scenario_recommender": "scenario_recommender.py",
                "workflow_recommender": "workflow_smart_recommender.py",
                "engine_combination_recommender": "engine_combination_recommender.py",
            },
            "orchestration": {
                "dynamic_orchestrator": "dynamic_engine_orchestrator.py",
                "decision_orchestrator": "decision_orchestrator.py",
                "workflow_orchestrator": "workflow_orchestrator.py",
            },
            "execution": {
                "auto_execution": "auto_execution_engine.py",
                "conversation_execution": "conversation_execution_engine.py",
                "task_execution": "task_execution_strategy.py",
            },
            "explanation": {
                "decision_explainer": "decision_explainer_engine.py",
            },
            "collaboration": {
                "multi_agent": "multi_agent_collaboration_engine.py",
            }
        }

        # 已加载的引擎实例
        self.loaded_engines = {}

        # 服务历史
        self.service_history = []
        self.load_history()

    def load_history(self):
        """加载服务历史"""
        history_file = self.state_dir / "service_hub_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.service_history = data.get('history', [])
            except Exception as e:
                print(f"加载历史记录失败: {e}")

    def save_history(self):
        """保存服务历史"""
        history_file = self.state_dir / "service_hub_history.json"
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'history': self.service_history[-100:]  # 保留最近100条
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史记录失败: {e}")

    def add_history(self, request: str, service_type: str, result: Any, status: str):
        """添加服务历史记录"""
        self.service_history.append({
            'timestamp': datetime.now().isoformat(),
            'request': request,
            'service_type': service_type,
            'status': status,
            'result_summary': str(result)[:200] if result else ''
        })
        self.save_history()

    def parse_intent(self, user_input: str) -> Dict[str, Any]:
        """解析用户意图并路由到合适的服务引擎"""
        user_input_lower = user_input.lower()

        # 推荐类意图
        recommendation_keywords = ['推荐', 'recommend', '建议', 'suggest', '什么好', '哪个好']
        if any(kw in user_input_lower for kw in recommendation_keywords):
            return {
                'type': 'recommendation',
                'action': 'get_recommendations',
                'params': {'query': user_input}
            }

        # 编排类意图
        orchestration_keywords = ['编排', 'orchestrate', '协调', '安排', '计划', 'plan']
        if any(kw in user_input_lower for kw in orchestration_keywords):
            return {
                'type': 'orchestration',
                'action': 'plan_task',
                'params': {'query': user_input}
            }

        # 执行类意图
        execution_keywords = ['执行', 'execute', 'run', '做', '完成', '运行']
        if any(kw in user_input_lower for kw in execution_keywords):
            return {
                'type': 'execution',
                'action': 'execute_task',
                'params': {'query': user_input}
            }

        # 解释类意图
        explanation_keywords = ['解释', 'explain', '为什么', '原因', '说明', '讲讲']
        if any(kw in user_input_lower for kw in explanation_keywords):
            return {
                'type': 'explanation',
                'action': 'explain_decision',
                'params': {'query': user_input}
            }

        # 协同类意图
        collaboration_keywords = ['协作', 'collaborate', '协同', '合作', '联动']
        if any(kw in user_input_lower for kw in collaboration_keywords):
            return {
                'type': 'collaboration',
                'action': 'collaborate',
                'params': {'query': user_input}
            }

        # 复合意图 - 需要多引擎协同
        return {
            'type': 'complex',
            'action': 'orchestrate_service_chain',
            'params': {'query': user_input}
        }

    def call_engine(self, engine_path: str, args: List[str] = None) -> Dict[str, Any]:
        """调用引擎脚本"""
        try:
            cmd = [sys.executable, str(self.scripts_dir / engine_path)]
            if args:
                cmd.extend(args)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8',
                errors='replace'
            )

            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr if result.returncode != 0 else None
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': '执行超时'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_recommendations(self, query: str) -> Dict[str, Any]:
        """获取推荐"""
        result = self.call_engine(
            self.service_engines['recommendation']['unified_recommender'],
            ['--query', query]
        )
        return result

    def orchestrate(self, query: str) -> Dict[str, Any]:
        """编排任务"""
        result = self.call_engine(
            self.service_engines['orchestration']['dynamic_orchestrator'],
            ['--query', query]
        )
        return result

    def execute_task(self, query: str) -> Dict[str, Any]:
        """执行任务"""
        result = self.call_engine(
            self.service_engines['execution']['auto_execution'],
            ['--query', query]
        )
        return result

    def explain_decision(self, query: str) -> Dict[str, Any]:
        """解释决策"""
        result = self.call_engine(
            self.service_engines['explanation']['decision_explainer'],
            ['--explain', query]
        )
        return result

    def collaborate(self, query: str) -> Dict[str, Any]:
        """协作任务"""
        result = self.call_engine(
            self.service_engines['collaboration']['multi_agent'],
            ['--query', query]
        )
        return result

    def orchestrate_service_chain(self, query: str) -> Dict[str, Any]:
        """服务链编排 - 多引擎协同"""
        results = {}

        # 并行调用多个引擎获取综合结果
        try:
            # 1. 获取推荐
            results['recommendation'] = self.get_recommendations(query)

            # 2. 编排计划
            results['orchestration'] = self.orchestrate(query)

            # 3. 解释原因
            results['explanation'] = self.explain_decision(query)

            return {
                'success': True,
                'results': results,
                'summary': self._summarize_results(results)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _summarize_results(self, results: Dict[str, Any]) -> str:
        """汇总各引擎结果"""
        summary_parts = []

        if 'recommendation' in results and results['recommendation'].get('success'):
            summary_parts.append("推荐引擎已处理")

        if 'orchestration' in results and results['orchestration'].get('success'):
            summary_parts.append("编排引擎已处理")

        if 'explanation' in results and results['explanation'].get('success'):
            summary_parts.append("解释引擎已处理")

        return "; ".join(summary_parts) if summary_parts else "服务处理中"

    def process_request(self, user_input: str) -> Dict[str, Any]:
        """处理用户请求的统一入口"""
        # 1. 解析意图
        intent = self.parse_intent(user_input)

        # 2. 路由到对应服务
        service_type = intent['type']
        action = intent['action']
        params = intent['params']

        # 3. 执行服务
        if service_type == 'recommendation':
            result = self.get_recommendations(params['query'])
        elif service_type == 'orchestration':
            result = self.orchestrate(params['query'])
        elif service_type == 'execution':
            result = self.execute_task(params['query'])
        elif service_type == 'explanation':
            result = self.explain_decision(params['query'])
        elif service_type == 'collaboration':
            result = self.collaborate(params['query'])
        elif service_type == 'complex':
            result = self.orchestrate_service_chain(params['query'])
        else:
            result = {'success': False, 'error': f'未知服务类型: {service_type}'}

        # 4. 记录历史
        self.add_history(user_input, service_type, result, 'success' if result.get('success') else 'failed')

        # 5. 返回结果
        return {
            'intent': intent,
            'result': result,
            'service_type': service_type
        }

    def get_status(self) -> Dict[str, Any]:
        """获取服务中枢状态"""
        return {
            'service_engines': {
                category: list(engines.keys())
                for category, engines in self.service_engines.items()
            },
            'loaded_engines': list(self.loaded_engines.keys()),
            'history_count': len(self.service_history),
            'recent_services': [
                {
                    'timestamp': h['timestamp'],
                    'request': h['request'][:50],
                    'type': h['service_type'],
                    'status': h['status']
                }
                for h in self.service_history[-5:]
            ]
        }

    def get_service_stats(self) -> Dict[str, Any]:
        """获取服务统计"""
        stats = {}
        for entry in self.service_history:
            service_type = entry['service_type']
            stats[service_type] = stats.get(service_type, 0) + 1

        return {
            'total_requests': len(self.service_history),
            'by_type': stats,
            'success_rate': sum(1 for e in self.service_history if e['status'] == 'success') / max(len(self.service_history), 1)
        }


def main():
    """命令行入口"""
    import argparse
    import io

    # 设置 stdout 编码为 UTF-8
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except:
        pass

    parser = argparse.ArgumentParser(description='智能统一服务中枢引擎')
    parser.add_argument('command', nargs='?', default='status',
                        help='命令: status, query, stats, recommend, orchestrate, execute, explain, collaborate')
    parser.add_argument('--query', '-q', type=str, help='查询内容')
    parser.add_argument('--explain', '-e', type=str, help='需要解释的内容')

    args = parser.parse_args()

    hub = UnifiedServiceHub()

    if args.command == 'status':
        # 显示状态
        status = hub.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.command == 'stats':
        # 显示统计
        stats = hub.get_service_stats()
        print(json.dumps(stats, ensure_ascii=False, indent=2))

    elif args.command in ['query', 'recommend', 'orchestrate', 'execute', 'explain', 'collaborate']:
        # 处理查询
        query = args.query or args.explain or ''
        if not query:
            print("错误: 请提供 --query 或 --explain 参数")
            sys.exit(1)

        result = hub.process_request(query)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'history':
        # 显示历史
        for entry in hub.service_history[-10:]:
            print(f"[{entry['timestamp']}] {entry['service_type']}: {entry['request'][:50]}")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()