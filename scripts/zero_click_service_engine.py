#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能零点击服务引擎
让系统能够基于用户简短输入自动识别完整任务链并执行，实现从「单步指令」到「完整任务闭环」的范式升级

这是「超越用户」的能力：用户只需要说一个目标，系统自动完成整个任务链。
区别于 conversation_execution_engine（理解单句意图），本引擎专注于从简短目标描述到完整任务链的转换。

功能：
1. 意图深度理解 - 解析用户的简短目标描述，识别深层需求
2. 任务链自动规划 - 自动生成完整的执行步骤链
3. 智能执行编排 - 编排多个引擎协同执行任务链
4. 执行状态追踪 - 实时追踪任务执行进度
5. 结果汇总反馈 - 执行完成后提供完整的结果汇总

使用方法：
    python zero_click_service_engine.py execute "用户目标描述"
    python zero_click_service_engine.py plan "用户目标描述"
    python zero_click_service_engine.py status
    python zero_click_service_engine.py history
    python zero_click_service_engine.py dashboard
"""
import os
import sys
import json
import sqlite3
import subprocess
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from collections import defaultdict

# 路径配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, '..', 'runtime', 'state', 'zero_click_service.db')
RUNTIME_DIR = os.path.join(SCRIPT_DIR, '..', 'runtime')
CAPABILITIES_PATH = os.path.join(SCRIPT_DIR, '..', 'references', 'capabilities.md')


@dataclass
class TaskStep:
    """任务步骤"""
    step_id: int
    description: str
    engine: str
    action: str
    params: Dict[str, Any]
    status: str = "pending"  # pending, running, completed, failed
    result: Any = None
    error: str = ""


@dataclass
class TaskChain:
    """任务链"""
    chain_id: str
    user_goal: str
    steps: List[TaskStep]
    status: str = "pending"  # pending, running, completed, failed, partially_completed
    created_at: str = ""
    completed_at: str = ""
    result_summary: str = ""


class ZeroClickServiceEngine:
    """智能零点击服务引擎"""

    def __init__(self):
        self.db_path = DB_PATH
        self._init_database()
        self._load_engine_registry()

    def _init_database(self):
        """初始化数据库"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 任务链历史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_chain_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chain_id TEXT NOT NULL,
                user_goal TEXT NOT NULL,
                steps_json TEXT,
                status TEXT,
                created_at TEXT,
                completed_at TEXT,
                result_summary TEXT
            )
        ''')

        # 引擎注册表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS engine_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                engine_name TEXT NOT NULL,
                engine_type TEXT,
                capabilities TEXT,
                keywords TEXT,
                last_used TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def _load_engine_registry(self):
        """加载引擎注册表"""
        self.engine_registry = {}

        # 尝试从数据库加载
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT engine_name, engine_type, capabilities, keywords FROM engine_registry")
        for row in cursor.fetchall():
            self.engine_registry[row[0]] = {
                'type': row[1],
                'capabilities': row[2],
                'keywords': row[3]
            }
        conn.close()

        # 如果数据库为空，从 capabilities.md 加载
        if not self.engine_registry:
            self._scan_engines_from_capabilities()

    def _scan_engines_from_capabilities(self):
        """从 capabilities.md 扫描引擎"""
        if not os.path.exists(CAPABILITIES_PATH):
            return

        try:
            with open(CAPABILITIES_PATH, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取引擎名称和描述
            # 简单解析：查找 `引擎名` 或 ## 引擎名 格式
            import re

            # 查找引擎列表（通常在 capabilities.md 的表格中）
            patterns = [
                r'`([^`]+)`[^\n]*[-–]\s*([^\n]+)',  # `engine_name` - description
                r'##\s+(\w+)\s+[^\n]*\n[^\n]*\n([^\n]+)',  ## Engine Name
            ]

            for pattern in patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                for name, desc in matches:
                    name = name.strip()
                    if len(name) > 2 and len(name) < 50:
                        self.engine_registry[name] = {
                            'type': 'general',
                            'capabilities': desc.strip()[:200],
                            'keywords': name.lower()
                        }

            # 保存到数据库
            self._save_engine_registry()

        except Exception as e:
            print(f"扫描引擎时出错: {e}")

    def _save_engine_registry(self):
        """保存引擎注册表到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 清空并重新插入
        cursor.execute("DELETE FROM engine_registry")

        for name, info in self.engine_registry.items():
            cursor.execute(
                "INSERT INTO engine_registry (engine_name, engine_type, capabilities, keywords) VALUES (?, ?, ?, ?)",
                (name, info.get('type', 'general'), info.get('capabilities', ''), info.get('keywords', ''))
            )

        conn.commit()
        conn.close()

    def _call_llm(self, prompt: str) -> str:
        """调用 LLM 进行意图分析和任务规划"""
        # 尝试使用项目内置的 LLM 接口
        # 首先检查是否有环境变量或配置文件
        llm_endpoint = os.environ.get('FRIDAY_LLM_ENDPOINT', '')
        llm_key = os.environ.get('FRIDAY_LLM_KEY', '')

        if not llm_endpoint:
            # 尝试从配置文件读取
            config_path = os.path.join(SCRIPT_DIR, '..', 'references', 'llm_config.json')
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        llm_endpoint = config.get('endpoint', '')
                        llm_key = config.get('key', '')
                except:
                    pass

        # 如果没有配置 LLM，使用基于规则的 fallback 分析
        if not llm_endpoint:
            return self._rule_based_analysis(prompt)

        # 调用 LLM API（简化版）
        try:
            import requests

            headers = {
                'Content-Type': 'application/json'
            }
            if llm_key:
                headers['Authorization'] = f'Bearer {llm_key}'

            payload = {
                'model': 'claude-sonnet-4-6',
                'messages': [
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 2000,
                'temperature': 0.7
            }

            response = requests.post(
                llm_endpoint,
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return result.get('choices', [{}])[0].get('message', {}).get('content', '')
            else:
                return self._rule_based_analysis(prompt)

        except Exception as e:
            print(f"LLM 调用失败: {e}")
            return self._rule_based_analysis(prompt)

    def _rule_based_analysis(self, user_goal: str) -> str:
        """基于规则的分析（当 LLM 不可用时）"""
        goal_lower = user_goal.lower()

        # 定义常见任务模式
        patterns = {
            '整理文件': ['整理', '归类', '分类', '整理文件', '整理文档'],
            '发送消息': ['发送', '发消息', '发个消息', '通知'],
            '打开应用': ['打开', '启动', '运行', '开'],
            '查找信息': ['查找', '搜索', '找', '查'],
            '管理工作': ['工作', '任务', 'todo', '待办'],
            '会议相关': ['会议', '会议纪要', '开会'],
            '汇报总结': ['汇报', '总结', '报告'],
        }

        matched_patterns = []
        for pattern, keywords in patterns.items():
            for keyword in keywords:
                if keyword in goal_lower:
                    matched_patterns.append(pattern)
                    break

        if matched_patterns:
            return f"识别到任务类型: {', '.join(matched_patterns)}\n\n建议执行步骤将根据识别的模式自动生成。"
        else:
            return "无法明确识别任务类型，将尝试通用任务分析。"

    def analyze_and_plan(self, user_goal: str) -> TaskChain:
        """分析用户目标并规划任务链"""
        chain_id = f"chain_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 构建分析 prompt
        analysis_prompt = f"""用户目标: {user_goal}

请分析这个用户目标，并生成一个执行任务链。

要求：
1. 识别用户的深层需求
2. 生成具体执行步骤
3. 每步需要说明：步骤描述、使用的引擎/工具、具体参数

可用引擎示例（从以下选择或推断）:
- file_manager_engine: 文件管理
- clipboard_tool: 剪贴板
- keyboard_tool: 键盘输入
- mouse_tool: 鼠标操作
- screenshot_tool: 截图
- window_tool: 窗口操作
- process_tool: 进程管理
- notification_tool: 通知
- run_plan: 执行计划
- conversation_execution_engine: 对话执行

请以 JSON 格式输出，格式如下：
{{
    "chain_id": "{chain_id}",
    "goal_summary": "目标摘要",
    "steps": [
        {{
            "step_id": 1,
            "description": "步骤描述",
            "engine": "引擎名",
            "action": "动作",
            "params": {{"参数": "值"}}
        }}
    ]
}}
"""

        # 调用 LLM 分析
        llm_result = self._call_llm(analysis_prompt)

        # 解析结果
        steps = []

        try:
            # 尝试从 LLM 结果中提取 JSON
            import re
            json_match = re.search(r'\{[\s\S]*\}', llm_result)
            if json_match:
                result_json = json.loads(json_match.group())
                if 'steps' in result_json:
                    for step_data in result_json['steps']:
                        steps.append(TaskStep(
                            step_id=step_data.get('step_id', 0),
                            description=step_data.get('description', ''),
                            engine=step_data.get('engine', ''),
                            action=step_data.get('action', ''),
                            params=step_data.get('params', {})
                        ))
        except Exception as e:
            print(f"解析 LLM 结果时出错: {e}")

        # 如果没有解析出步骤，使用基于规则的分析
        if not steps:
            steps = self._generate_rule_based_steps(user_goal)

        # 创建任务链
        chain = TaskChain(
            chain_id=chain_id,
            user_goal=user_goal,
            steps=steps,
            status="pending",
            created_at=datetime.now().isoformat()
        )

        # 保存到数据库
        self._save_chain(chain)

        return chain

    def _generate_rule_based_steps(self, user_goal: str) -> List[TaskStep]:
        """基于规则生成任务步骤"""
        goal_lower = user_goal.lower()
        steps = []
        step_id = 1

        # 根据关键词识别任务类型
        if any(k in goal_lower for k in ['整理', '分类', '归类']):
            # 文件整理任务
            steps.append(TaskStep(
                step_id=step_id,
                description="扫描和分析需要整理的文件",
                engine="file_manager_engine",
                action="analyze",
                params={"path": "用户文档目录"}
            ))
            step_id += 1

            steps.append(TaskStep(
                step_id=step_id,
                description="根据文件类型分类",
                engine="file_manager_engine",
                action="organize",
                params={"by": "type"}
            ))
            step_id += 1

        if any(k in goal_lower for k in ['发送', '通知', '发消息']):
            # 发送消息任务
            steps.append(TaskStep(
                step_id=step_id,
                description="确定接收人和消息内容",
                engine="conversation_execution_engine",
                action="analyze_intent",
                params={"input": user_goal}
            ))

        if any(k in goal_lower for k in ['打开', '启动', '运行']):
            # 打开应用任务
            steps.append(TaskStep(
                step_id=step_id,
                description="识别要打开的应用",
                engine="conversation_execution_engine",
                action="extract_entity",
                params={"input": user_goal, "entity_type": "app"}
            ))
            step_id += 1

            steps.append(TaskStep(
                step_id=step_id,
                description="打开应用",
                engine="do",
                action="打开应用",
                params={}
            ))

        # 如果没有匹配到任何模式，添加通用步骤
        if not steps:
            steps.append(TaskStep(
                step_id=step_id,
                description="分析用户目标",
                engine="conversation_execution_engine",
                action="analyze_intent",
                params={"input": user_goal}
            ))
            step_id += 1

            steps.append(TaskStep(
                step_id=step_id,
                description="识别需要的引擎能力",
                engine="engine_capability_activator",
                action="recommend",
                params={"context": user_goal}
            ))

        return steps

    def _save_chain(self, chain: TaskChain):
        """保存任务链到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        steps_json = json.dumps([{
            'step_id': s.step_id,
            'description': s.description,
            'engine': s.engine,
            'action': s.action,
            'params': s.params,
            'status': s.status
        } for s in chain.steps])

        cursor.execute(
            """INSERT INTO task_chain_history
               (chain_id, user_goal, steps_json, status, created_at, completed_at, result_summary)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (chain.chain_id, chain.user_goal, steps_json, chain.status,
             chain.created_at, chain.completed_at, chain.result_summary)
        )

        conn.commit()
        conn.close()

    def execute_chain(self, chain_id: str, auto_execute: bool = True) -> Dict[str, Any]:
        """执行任务链"""
        # 从数据库加载任务链
        chain = self._load_chain(chain_id)
        if not chain:
            return {"error": f"找不到任务链: {chain_id}"}

        if not chain.steps:
            return {"error": "任务链没有步骤"}

        # 更新状态
        chain.status = "running"
        self._save_chain(chain)

        # 执行每个步骤
        results = []
        for step in chain.steps:
            step.status = "running"

            if auto_execute:
                result = self._execute_step(step)
                step.result = result.get('result')
                step.status = "completed" if result.get('success') else "failed"
                if not result.get('success'):
                    step.error = result.get('error', 'Unknown error')
            else:
                # 预览模式，只返回步骤信息
                step.status = "pending"

            results.append({
                'step_id': step.step_id,
                'description': step.description,
                'status': step.status,
                'result': str(step.result)[:200] if step.result else None
            })

        # 更新任务链状态
        failed_steps = [s for s in chain.steps if s.status == "failed"]
        if not failed_steps:
            chain.status = "completed"
        else:
            chain.status = "partially_completed"

        chain.completed_at = datetime.now().isoformat()
        chain.result_summary = f"完成 {len(chain.steps) - len(failed_steps)}/{len(chain.steps)} 步骤"
        self._save_chain(chain)

        return {
            "chain_id": chain_id,
            "status": chain.status,
            "results": results,
            "summary": chain.result_summary
        }

    def _execute_step(self, step: TaskStep) -> Dict[str, Any]:
        """执行单个步骤"""
        try:
            # 根据引擎和动作调用相应的功能
            if step.engine == "do":
                # 调用 do.py
                params_str = ' '.join([f'"{v}"' if isinstance(v, str) else str(v) for v in step.params.values()])
                cmd = f'python scripts/do.py {step.action} {params_str}'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
                return {
                    "success": result.returncode == 0,
                    "result": result.stdout,
                    "error": result.stderr if result.returncode != 0 else ""
                }

            elif step.engine == "run_plan":
                # 调用 run_plan
                plan_path = step.params.get('plan', '')
                cmd = f'python scripts/run_plan.py {plan_path}'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
                return {
                    "success": result.returncode == 0,
                    "result": result.stdout,
                    "error": result.stderr if result.returncode != 0 else ""
                }

            elif step.engine == "file_manager_engine":
                # 调用文件管理器
                cmd = f'python scripts/file_manager_engine.py {step.action}'
                for k, v in step.params.items():
                    cmd += f' --{k} "{v}"' if isinstance(v, str) else f' --{k} {v}'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
                return {
                    "success": result.returncode == 0,
                    "result": result.stdout,
                    "error": result.stderr if result.returncode != 0 else ""
                }

            else:
                # 通用执行方式
                engine_script = os.path.join(SCRIPT_DIR, f"{step.engine}.py")
                if os.path.exists(engine_script):
                    cmd = f'python {engine_script} {step.action}'
                    for k, v in step.params.items():
                        cmd += f' --{k} "{v}"' if isinstance(v, str) else f' --{k} {v}'
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
                    return {
                        "success": result.returncode == 0,
                        "result": result.stdout,
                        "error": result.stderr if result.returncode != 0 else ""
                    }
                else:
                    return {
                        "success": False,
                        "error": f"引擎不存在: {step.engine}"
                    }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "执行超时"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _load_chain(self, chain_id: str) -> Optional[TaskChain]:
        """从数据库加载任务链"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT chain_id, user_goal, steps_json, status, created_at, completed_at, result_summary FROM task_chain_history WHERE chain_id = ?",
            (chain_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        steps_data = json.loads(row[2])
        steps = []
        for s in steps_data:
            step = TaskStep(
                step_id=s['step_id'],
                description=s['description'],
                engine=s['engine'],
                action=s['action'],
                params=s['params'],
                status=s.get('status', 'pending')
            )
            steps.append(step)

        return TaskChain(
            chain_id=row[0],
            user_goal=row[1],
            steps=steps,
            status=row[3],
            created_at=row[4],
            completed_at=row[5],
            result_summary=row[6]
        )

    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取执行历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT chain_id, user_goal, status, created_at, result_summary FROM task_chain_history ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )

        results = []
        for row in cursor.fetchall():
            results.append({
                "chain_id": row[0],
                "user_goal": row[1],
                "status": row[2],
                "created_at": row[3],
                "result_summary": row[4]
            })

        conn.close()
        return results

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "engine": "ZeroClickServiceEngine",
            "version": "1.0.0",
            "status": "active",
            "engines_registered": len(self.engine_registry),
            "description": "智能零点击服务引擎 - 从简短目标描述自动生成并执行完整任务链"
        }

    def get_dashboard(self) -> Dict[str, Any]:
        """获取仪表盘数据"""
        # 获取统计数据
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM task_chain_history")
        total_chains = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM task_chain_history WHERE status = 'completed'")
        completed_chains = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM task_chain_history WHERE status = 'failed'")
        failed_chains = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM task_chain_history WHERE created_at > datetime('now', '-1 day')")
        today_chains = cursor.fetchone()[0]

        conn.close()

        return {
            "engine": "ZeroClickServiceEngine",
            "total_chains": total_chains,
            "completed_chains": completed_chains,
            "failed_chains": failed_chains,
            "today_chains": today_chains,
            "success_rate": round(completed_chains / total_chains * 100, 1) if total_chains > 0 else 0,
            "recent_chains": self.get_history(5)
        }


def main():
    """主入口"""
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1]
    engine = ZeroClickServiceEngine()

    if command == "status":
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif command == "dashboard":
        dashboard = engine.get_dashboard()
        print(json.dumps(dashboard, ensure_ascii=False, indent=2))

    elif command == "history":
        history = engine.get_history()
        print(json.dumps(history, ensure_ascii=False, indent=2))

    elif command == "plan":
        if len(sys.argv) < 3:
            print("用法: python zero_click_service_engine.py plan \"用户目标\"")
            return
        user_goal = sys.argv[2]
        chain = engine.analyze_and_plan(user_goal)
        print(json.dumps({
            "chain_id": chain.chain_id,
            "user_goal": chain.user_goal,
            "steps": [
                {
                    "step_id": s.step_id,
                    "description": s.description,
                    "engine": s.engine,
                    "action": s.action,
                    "params": s.params
                } for s in chain.steps
            ]
        }, ensure_ascii=False, indent=2))

    elif command == "execute":
        if len(sys.argv) < 3:
            print("用法: python zero_click_service_engine.py execute \"用户目标\"")
            return
        user_goal = sys.argv[2]
        # 先规划
        chain = engine.analyze_and_plan(user_goal)
        # 再执行
        result = engine.execute_chain(chain.chain_id, auto_execute=True)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "run":
        if len(sys.argv) < 3:
            print("用法: python zero_click_service_engine.py run <chain_id>")
            return
        chain_id = sys.argv[2]
        result = engine.execute_chain(chain_id, auto_execute=True)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()