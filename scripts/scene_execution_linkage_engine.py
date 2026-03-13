#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能场景执行联动引擎
让系统能够自动分析任务需求，识别需要执行的多个场景计划，
实现场景计划间的参数传递、状态共享，形成从场景理解→计划串联→自动执行的完整闭环
"""
import os
import json
import re
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import subprocess
import sys


# 数据存储路径
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runtime', 'state')
SCENE_CHAIN_LOG_FILE = os.path.join(DATA_DIR, 'scene_chain_execution_log.json')
SCENE_PARAM_STORE = os.path.join(DATA_DIR, 'scene_param_store.json')
PLANS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'plans')


@dataclass
class SceneChainStep:
    """场景链步骤"""
    step_id: int
    scene_name: str
    scene_path: str
    params: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[int] = field(default_factory=list)
    execute_mode: str = "sequential"  # sequential, parallel, conditional


@dataclass
class SceneChain:
    """场景链"""
    chain_id: str
    chain_name: str
    description: str
    steps: List[SceneChainStep]
    total_steps: int = 0
    created_at: str = ""
    status: str = "pending"  # pending, running, completed, failed


@dataclass
class ChainExecutionResult:
    """场景链执行结果"""
    chain_id: str
    status: str  # success, partial, failed
    step_results: List[Dict[str, Any]] = field(default_factory=list)
    shared_data: Dict[str, Any] = field(default_factory=dict)
    total_time: float = 0.0
    error_message: str = ""


class SceneExecutionLinkageEngine:
    """智能场景执行联动引擎"""

    def __init__(self):
        self.plans_dir = PLANS_DIR
        self.chain_log_file = SCENE_CHAIN_LOG_FILE
        self.param_store_file = SCENE_PARAM_STORE
        self._ensure_data_dir()
        self._load_param_store()

    def _ensure_data_dir(self):
        """确保数据目录存在"""
        os.makedirs(DATA_DIR, exist_ok=True)

    def _load_param_store(self):
        """加载参数存储"""
        if os.path.exists(self.param_store_file):
            try:
                with open(self.param_store_file, 'r', encoding='utf-8') as f:
                    self.param_store = json.load(f)
            except:
                self.param_store = {}
        else:
            self.param_store = {}

    def _save_param_store(self):
        """保存参数存储"""
        with open(self.param_store_file, 'w', encoding='utf-8') as f:
            json.dump(self.param_store, f, ensure_ascii=False, indent=2)

    def list_available_scenes(self) -> List[Dict[str, str]]:
        """列出所有可用的场景计划"""
        scenes = []
        if os.path.exists(self.plans_dir):
            for f in os.listdir(self.plans_dir):
                if f.endswith('.json'):
                    scene_path = os.path.join(self.plans_dir, f)
                    try:
                        with open(scene_path, 'r', encoding='utf-8') as fp:
                            scene_data = json.load(fp)
                            scenes.append({
                                'name': f.replace('.json', ''),
                                'path': scene_path,
                                'description': scene_data.get('description', ''),
                                'triggers': scene_data.get('triggers', [])
                            })
                    except:
                        pass
        return scenes

    def analyze_task_and_plan_chain(self, task_description: str) -> SceneChain:
        """分析任务并规划场景链"""
        # 可用场景
        available_scenes = self.list_available_scenes()

        # 基于任务描述智能分析需要的场景
        chain_steps = []
        step_id = 1

        # 关键词匹配场景
        task_lower = task_description.lower()

        # 工作相关场景
        if any(k in task_lower for k in ['绩效', '申报', 'oa', '办公', 'ihaier']):
            chain_steps.append(SceneChainStep(
                step_id=step_id,
                scene_name='ihaier_performance_declaration',
                scene_path=os.path.join(self.plans_dir, 'ihaier_performance_declaration.json'),
                params={},
                depends_on=[],
                execute_mode='sequential'
            ))
            step_id += 1

        # 消息相关场景
        if any(k in task_lower for k in ['发消息', '联系人', '消息', '周小帅']):
            chain_steps.append(SceneChainStep(
                step_id=step_id,
                scene_name='example_ihaier_send_message',
                scene_path=os.path.join(self.plans_dir, 'example_ihaier_send_message.json'),
                params={'contact': self._extract_contact(task_description)},
                depends_on=[step_id - 1] if chain_steps else [],
                execute_mode='sequential'
            ))
            step_id += 1

        # 音乐相关场景
        if any(k in task_lower for k in ['放歌', '音乐', '听歌', '播放']):
            chain_steps.append(SceneChainStep(
                step_id=step_id,
                scene_name='play_music',
                scene_path=os.path.join(self.plans_dir, 'play_music.json'),
                params={},
                depends_on=[],
                execute_mode='sequential'
            ))
            step_id += 1

        # 视频/电影相关
        if any(k in task_lower for k in ['电影', '视频', '看片']):
            chain_steps.append(SceneChainStep(
                step_id=step_id,
                scene_name='watch_movie',
                scene_path=os.path.join(self.plans_dir, 'watch_movie.json'),
                params={},
                depends_on=[],
                execute_mode='sequential'
            ))
            step_id += 1

        # 资讯/新闻相关
        if any(k in task_lower for k in ['新闻', '资讯', '浏览']):
            chain_steps.append(SceneChainStep(
                step_id=step_id,
                scene_name='read_news',
                scene_path=os.path.join(self.plans_dir, 'read_news.json'),
                params={},
                depends_on=[],
                execute_mode='sequential'
            ))
            step_id += 1

        # 批量文件操作
        if any(k in task_lower for k in ['批量', '文件', '整理']):
            chain_steps.append(SceneChainStep(
                step_id=step_id,
                scene_name='batch_file_operation',
                scene_path=os.path.join(self.plans_dir, 'batch_file_operation.json'),
                params={},
                depends_on=[],
                execute_mode='sequential'
            ))
            step_id += 1

        # 如果没有匹配到任何场景，创建一个通用场景
        if not chain_steps:
            # 尝试通用场景理解
            chain_steps.append(SceneChainStep(
                step_id=step_id,
                scene_name='example_screenshot_vision',
                scene_path=os.path.join(self.plans_dir, 'example_screenshot_vision.json'),
                params={'task': task_description},
                depends_on=[],
                execute_mode='sequential'
            ))

        # 创建场景链
        chain_id = f"chain_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        scene_chain = SceneChain(
            chain_id=chain_id,
            chain_name=f"场景链-{task_description[:20]}",
            description=f"自动分析任务'{task_description}'生成的场景链",
            steps=chain_steps,
            total_steps=len(chain_steps),
            created_at=datetime.now().isoformat(),
            status="pending"
        )

        return scene_chain

    def _extract_contact(self, text: str) -> str:
        """提取联系人"""
        # 简单提取：查找"给xxx发消息"中的xxx
        patterns = [
            r'给(.+?)发消息',
            r'发消息给(.+?)',
            r'联系(.+?)，?发',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return "周小帅"  # 默认联系人

    def execute_scene_chain(self, scene_chain: SceneChain, simulate: bool = False) -> ChainExecutionResult:
        """执行场景链"""
        start_time = datetime.now()
        step_results = []
        shared_data = {}

        # 更新状态
        scene_chain.status = "running"
        self._log_chain_execution(scene_chain, "started")

        try:
            for step in scene_chain.steps:
                # 检查依赖是否满足
                if step.depends_on:
                    deps_satisfied = all(
                        step_results[dep - 1].get('status') == 'success'
                        for dep in step.depends_on
                        if dep <= len(step_results)
                    )
                    if not deps_satisfied:
                        step_results.append({
                            'step_id': step.step_id,
                            'scene_name': step.scene_name,
                            'status': 'skipped',
                            'reason': 'dependency not satisfied'
                        })
                        continue

                # 准备参数（合并全局共享数据）
                exec_params = {**shared_data, **step.params}

                # 执行场景
                if simulate:
                    step_result = {
                        'step_id': step.step_id,
                        'scene_name': step.scene_name,
                        'status': 'simulated',
                        'params': exec_params,
                        'message': f"模拟执行场景: {step.scene_name}"
                    }
                else:
                    step_result = self._execute_single_scene(step.scene_path, exec_params)

                step_results.append(step_result)

                # 提取共享数据
                if step_result.get('status') == 'success':
                    # 从结果中提取可共享的数据
                    if 'output' in step_result:
                        shared_data.update(step_result.get('output', {}))

                # 记录参数供后续步骤使用
                if exec_params:
                    self.param_store[f"step_{step.step_id}"] = exec_params

            # 计算总时间
            total_time = (datetime.now() - start_time).total_seconds()

            # 判断整体状态
            all_success = all(r.get('status') == 'success' for r in step_results)
            any_success = any(r.get('status') == 'success' for r in step_results)

            if all_success:
                status = "success"
            elif any_success:
                status = "partial"
            else:
                status = "failed"

            result = ChainExecutionResult(
                chain_id=scene_chain.chain_id,
                status=status,
                step_results=step_results,
                shared_data=shared_data,
                total_time=total_time,
                error_message=""
            )

            scene_chain.status = "completed" if status == "success" else "failed"
            self._log_chain_execution(scene_chain, "completed", result)
            self._save_param_store()

            return result

        except Exception as e:
            total_time = (datetime.now() - start_time).total_seconds()
            scene_chain.status = "failed"

            result = ChainExecutionResult(
                chain_id=scene_chain.chain_id,
                status="failed",
                step_results=step_results,
                shared_data=shared_data,
                total_time=total_time,
                error_message=str(e)
            )

            self._log_chain_execution(scene_chain, "failed", result)
            self._save_param_store()

            return result

    def _execute_single_scene(self, scene_path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个场景"""
        try:
            # 调用 run_plan 执行场景
            cmd = [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run_plan.py'), scene_path]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode == 0:
                return {
                    'status': 'success',
                    'scene_path': scene_path,
                    'output': {'result': result.stdout},
                    'message': '执行成功'
                }
            else:
                return {
                    'status': 'failed',
                    'scene_path': scene_path,
                    'error': result.stderr,
                    'message': '执行失败'
                }

        except subprocess.TimeoutExpired:
            return {
                'status': 'failed',
                'scene_path': scene_path,
                'error': '执行超时',
                'message': '执行超时（5分钟）'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'scene_path': scene_path,
                'error': str(e),
                'message': f'执行异常: {str(e)}'
            }

    def _log_chain_execution(self, chain: SceneChain, event: str, result: Optional[ChainExecutionResult] = None):
        """记录场景链执行日志"""
        log_entry = {
            'chain_id': chain.chain_id,
            'chain_name': chain.chain_name,
            'event': event,
            'timestamp': datetime.now().isoformat(),
            'status': chain.status
        }

        if result:
            log_entry['result'] = asdict(result)

        # 读取现有日志
        logs = []
        if os.path.exists(self.chain_log_file):
            try:
                with open(self.chain_log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except:
                logs = []

        logs.append(log_entry)

        # 只保留最近100条
        logs = logs[-100:]

        with open(self.chain_log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

    def get_chain_status(self, chain_id: str) -> Optional[Dict[str, Any]]:
        """获取场景链状态"""
        if os.path.exists(self.chain_log_file):
            try:
                with open(self.chain_log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                    for log in reversed(logs):
                        if log.get('chain_id') == chain_id:
                            return log
            except:
                pass
        return None

    def list_recent_chains(self, limit: int = 10) -> List[Dict[str, Any]]:
        """列出最近执行的场景链"""
        if os.path.exists(self.chain_log_file):
            try:
                with open(self.chain_log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                    return logs[-limit:]
            except:
                pass
        return []

    def analyze_chain_opportunities(self) -> Dict[str, Any]:
        """分析场景链执行机会"""
        available = self.list_available_scenes()

        # 分析场景组合可能性
        opportunities = []

        # 办公+消息组合
        office_scenes = [s for s in available if any(k in str(s).lower() for k in ['ihaier', '绩效', '办公'])]
        message_scenes = [s for s in available if 'message' in s.get('name', '').lower()]

        if office_scenes and message_scenes:
            opportunities.append({
                'type': 'office_message',
                'description': '办公+消息联动',
                'scenes': [office_scenes[0]['name'], message_scenes[0]['name']],
                'score': 0.8
            })

        # 音乐+娱乐组合
        entertainment_scenes = [s for s in available if any(k in s.get('name', '').lower() for k in ['music', 'movie', 'video'])]
        if len(entertainment_scenes) >= 2:
            opportunities.append({
                'type': 'entertainment_chain',
                'description': '娱乐场景串联',
                'scenes': [s['name'] for s in entertainment_scenes[:2]],
                'score': 0.7
            })

        return {
            'available_scenes': len(available),
            'opportunities': opportunities,
            'recommendation': opportunities[0] if opportunities else None
        }


def main():
    """主函数 - 命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='智能场景执行联动引擎')
    parser.add_argument('command', choices=['list', 'analyze', 'execute', 'status', 'chains', 'opportunities'],
                        help='命令')
    parser.add_argument('--task', type=str, help='任务描述（用于 analyze 命令）')
    parser.add_argument('--chain-id', type=str, help='场景链ID（用于 status 命令）')
    parser.add_argument('--simulate', action='store_true', help='模拟执行')
    parser.add_argument('--plan', type=str, help='场景计划文件路径')

    args = parser.parse_args()

    engine = SceneExecutionLinkageEngine()

    if args.command == 'list':
        scenes = engine.list_available_scenes()
        print(json.dumps(scenes, ensure_ascii=False, indent=2))

    elif args.command == 'analyze':
        if not args.task:
            print("错误: --task 参数 required")
            sys.exit(1)
        chain = engine.analyze_task_and_plan_chain(args.task)
        print(json.dumps(asdict(chain), ensure_ascii=False, indent=2))

    elif args.command == 'execute':
        if not args.plan:
            print("错误: --plan 参数 required")
            sys.exit(1)

        # 读取场景链
        with open(args.plan, 'r', encoding='utf-8') as f:
            chain_data = json.load(f)

        # 转换为 SceneChain 对象
        steps = [SceneChainStep(**s) for s in chain_data.get('steps', [])]
        chain = SceneChain(
            chain_id=chain_data.get('chain_id'),
            chain_name=chain_data.get('chain_name'),
            description=chain_data.get('description', ''),
            steps=steps,
            total_steps=len(steps)
        )

        result = engine.execute_scene_chain(chain, simulate=args.simulate)
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))

    elif args.command == 'status':
        if not args.chain_id:
            print("错误: --chain-id 参数 required")
            sys.exit(1)
        status = engine.get_chain_status(args.chain_id)
        print(json.dumps(status, ensure_ascii=False, indent=2) if status else "{}")

    elif args.command == 'chains':
        chains = engine.list_recent_chains()
        print(json.dumps(chains, ensure_ascii=False, indent=2))

    elif args.command == 'opportunities':
        analysis = engine.analyze_chain_opportunities()
        print(json.dumps(analysis, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()