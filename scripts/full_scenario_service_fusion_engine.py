"""
智能全场景服务融合引擎 (Full-Scenario Service Fusion Engine)

增强版的统一服务中枢，让系统能够从一个入口理解用户的模糊需求，
自动选择和组合多个引擎协同工作，提供一站式智能服务体验。

功能：
1. 深度意图理解 - 不仅识别表面关键词，还能理解深层需求和隐含意图
2. 多引擎智能组合 - 根据任务需求自动选择最合适的引擎组合
3. 上下文感知 - 理解当前系统状态、用户历史行为
4. 主动服务 - 预测用户可能需要的服务并主动推荐
5. 服务链自动编排 - 复杂任务自动拆分为多引擎协同执行

Version: 1.0.0
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import re

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class FullScenarioServiceFusionEngine:
    """智能全场景服务融合引擎"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.scripts_dir = self.project_root / "scripts"
        self.state_dir = self.project_root / "runtime" / "state"

        # 深度意图理解映射表 - 支持模糊输入
        self.intent_patterns = {
            # 文件操作类
            'file_organize': {
                'keywords': ['整理', 'organize', '归类', '分类', '排序'],
                'engines': ['file_manager_engine', 'file_watcher'],
                'description': '文件整理归类'
            },
            'file_search': {
                'keywords': ['找', 'search', '查找', '搜索', '在哪里'],
                'engines': ['file_tool', 'file_manager_engine'],
                'description': '文件搜索查找'
            },
            # 系统操作类
            'system_optimize': {
                'keywords': ['优化', 'optimize', '清理', 'clean', '加速'],
                'engines': ['proactive_operations_engine', 'self_healing_engine'],
                'description': '系统优化清理'
            },
            'system_monitor': {
                'keywords': ['监控', 'monitor', '状态', 'status', '健康'],
                'engines': ['system_health_report_engine', 'unified_system_monitor'],
                'description': '系统状态监控'
            },
            # 任务执行类
            'task_automation': {
                'keywords': ['自动', 'auto', '帮我做', '帮我完成', '执行'],
                'engines': ['workflow_engine', 'workflow_orchestrator', 'auto_execution_engine'],
                'description': '任务自动化执行'
            },
            'task_planning': {
                'keywords': ['计划', 'plan', '安排', 'schedule', '定时'],
                'engines': ['task_scheduler', 'cross_engine_task_planner'],
                'description': '任务规划安排'
            },
            # 信息获取类
            'info_query': {
                'keywords': ['什么是', '什么是', '怎么样', '如何', 'how to', 'what is'],
                'engines': ['knowledge_graph', 'enhanced_knowledge_reasoning_engine'],
                'description': '信息查询解答'
            },
            'system_info': {
                'keywords': ['信息', 'info', '查看', 'show', '显示'],
                'engines': ['system_health_check', 'network_tool', 'env_tool'],
                'description': '系统信息查询'
            },
            # 通信类
            'message_send': {
                'keywords': ['发消息', 'message', '告诉', '通知', 'send'],
                'engines': ['clipboard_tool', 'keyboard_tool', 'window_tool'],
                'description': '发送消息'
            },
            # 媒体类
            'media_play': {
                'keywords': ['播放', 'play', '音乐', 'music', '视频', 'video'],
                'engines': ['launch_browser', 'window_tool'],
                'description': '媒体播放'
            },
            # 学习类
            'learning': {
                'keywords': ['学习', 'learn', '记住', '记住我', '习惯'],
                'engines': ['adaptive_learning_engine', 'user_behavior_learner', 'long_term_memory_engine'],
                'description': '学习用户偏好'
            },
            # 创意类
            'creative': {
                'keywords': ['创意', 'creative', '建议', 'suggest', '想法', 'idea'],
                'engines': ['creative_generation_engine', 'proactive_insight_engine'],
                'description': '创意建议生成'
            }
        }

        # 复合任务模式 - 多引擎协同
        self.complex_patterns = [
            {
                'name': '完整工作流',
                'keywords': ['帮我', '帮我做', '帮我完成', '帮我处理'],
                'engines': ['workflow_engine', 'auto_execution_engine', 'multi_agent_collaboration_engine'],
                'action': 'full_automation'
            },
            {
                'name': '智能分析',
                'keywords': ['分析', 'analyze', '报告', 'report'],
                'engines': ['multi_dim_analysis_engine', 'data_insight_engine', 'system_health_report_engine'],
                'action': 'intelligent_analysis'
            },
            {
                'name': '预测规划',
                'keywords': ['预测', 'predict', '未来', '趋势', 'trends'],
                'engines': ['behavior_sequence_prediction_engine', 'proactive_insight_engine', 'evolution_prediction_planner'],
                'action': 'prediction_planning'
            }
        ]

        # 服务历史
        self.service_history = []
        self.load_history()

        # 用户上下文
        self.user_context = {}
        self.load_user_context()

    def load_history(self):
        """加载服务历史"""
        history_file = self.state_dir / "service_fusion_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.service_history = data.get('history', [])
            except Exception as e:
                print(f"加载历史记录失败: {e}")

    def save_history(self):
        """保存服务历史"""
        history_file = self.state_dir / "service_fusion_history.json"
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'history': self.service_history[-100:]
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史记录失败: {e}")

    def load_user_context(self):
        """加载用户上下文"""
        context_file = self.state_dir / "user_context.json"
        if context_file.exists():
            try:
                with open(context_file, 'r', encoding='utf-8') as f:
                    self.user_context = json.load(f)
            except Exception as e:
                print(f"加载用户上下文失败: {e}")

    def analyze_intent_deeply(self, user_input: str) -> Dict[str, Any]:
        """深度意图分析 - 理解模糊输入背后的真正需求"""

        # 1. 提取关键实体
        entities = self._extract_entities(user_input)

        # 2. 识别意图类型
        intent_type = self._classify_intent(user_input)

        # 3. 判断是否需要多引擎协同
        needs_collaboration = self._needs_collaboration(user_input)

        # 4. 推断隐含意图
        hidden_intents = self._infer_hidden_intents(user_input, entities)

        return {
            'user_input': user_input,
            'entities': entities,
            'primary_intent': intent_type,
            'hidden_intents': hidden_intents,
            'needs_collaboration': needs_collaboration,
            'confidence': self._calculate_confidence(user_input, intent_type)
        }

    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """提取关键实体"""
        entities = {
            'time': [],      # 时间相关
            'app': [],       # 应用名称
            'file': [],      # 文件/路径
            'action': [],    # 动作
            'target': []     # 目标对象
        }

        # 时间模式
        time_patterns = [
            r'\d+点', r'\d+分钟', r'\d+小时',
            r'今天|明天|后天|昨天',
            r'早上|中午|下午|晚上',
            r'现在|稍后|等一下'
        ]
        for pattern in time_patterns:
            matches = re.findall(pattern, text)
            entities['time'].extend(matches)

        # 应用模式
        app_patterns = [
            r'打开\s*(\S+)',
            r'关闭\s*(\S+)',
            r'(\S+)\s*应用'
        ]
        for pattern in app_patterns:
            matches = re.findall(pattern, text)
            entities['app'].extend(matches)

        # 动作模式
        action_patterns = [
            r'(帮我|给我|帮我做|帮我完成|执行)',
            r'(打开|关闭|启动|运行|执行)',
            r'(发送|发送|通知|告诉)'
        ]
        for pattern in action_patterns:
            matches = re.findall(pattern, text)
            if matches:
                entities['action'].append(matches[0] if isinstance(matches[0], str) else matches[0][0])

        return entities

    def _classify_intent(self, user_input: str) -> str:
        """分类意图"""
        input_lower = user_input.lower()

        # 匹配具体模式
        for intent_name, pattern_info in self.intent_patterns.items():
            for keyword in pattern_info['keywords']:
                if keyword in input_lower:
                    return intent_name

        # 匹配复合模式
        for pattern in self.complex_patterns:
            for keyword in pattern['keywords']:
                if keyword in input_lower:
                    return 'complex_task'

        # 默认归类为信息查询
        return 'info_query'

    def _needs_collaboration(self, user_input: str) -> bool:
        """判断是否需要多引擎协同"""
        collaboration_keywords = [
            '然后', 'and', '还有', '并且', '同时',
            '帮我', '帮我做', '完成', '处理',
            '分析', '报告', '看看'
        ]
        return any(kw in user_input.lower() for kw in collaboration_keywords)

    def _infer_hidden_intents(self, user_input: str, entities: Dict[str, List[str]]) -> List[str]:
        """推断隐含意图"""
        hidden = []
        input_lower = user_input.lower()

        # 如果提到"看看"，可能是想了解状态
        if '看看' in input_lower or '查看' in input_lower:
            hidden.append('status_check')

        # 如果提到"优化"，可能需要先分析
        if '优化' in input_lower or '加速' in input_lower:
            hidden.append('analysis_first')

        # 如果是复杂任务，需要规划
        if self._needs_collaboration(user_input):
            hidden.append('needs_planning')

        return hidden

    def _calculate_confidence(self, user_input: str, intent_type: str) -> float:
        """计算意图识别置信度"""
        if intent_type in self.intent_patterns:
            pattern = self.intent_patterns[intent_type]
            for keyword in pattern['keywords']:
                if keyword in user_input.lower():
                    return 0.9

        # 尝试模糊匹配
        for name, info in self.intent_patterns.items():
            for keyword in info['keywords']:
                if keyword[0] in user_input.lower():
                    return 0.6

        return 0.5

    def select_engine_combination(self, intent_analysis: Dict[str, Any]) -> List[str]:
        """根据意图分析选择引擎组合"""

        primary_intent = intent_analysis['primary_intent']
        needs_collab = intent_analysis['needs_collaboration']
        hidden_intents = intent_analysis.get('hidden_intents', [])

        # 获取主意图对应的引擎
        selected_engines = []

        if primary_intent in self.intent_patterns:
            selected_engines.extend(self.intent_patterns[primary_intent]['engines'])

        # 如果需要协作，添加协作引擎
        if needs_collab:
            selected_engines.append('multi_agent_collaboration_engine')

        # 处理隐含意图
        for hidden in hidden_intents:
            if hidden == 'analysis_first':
                selected_engines.append('multi_dim_analysis_engine')
            elif hidden == 'needs_planning':
                selected_engines.append('cross_engine_task_planner')

        # 去重但保持顺序
        seen = set()
        unique_engines = []
        for eng in selected_engines:
            if eng not in seen:
                seen.add(eng)
                unique_engines.append(eng)

        return unique_engines

    def call_engine(self, engine_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """调用引擎脚本"""

        # 引擎名称到脚本的映射
        engine_scripts = {
            'file_manager_engine': 'file_manager_engine.py',
            'file_tool': 'file_tool.py',
            'file_watcher': 'file_watcher.py',
            'proactive_operations_engine': 'proactive_operations_engine.py',
            'self_healing_engine': 'self_healing_engine.py',
            'system_health_report_engine': 'system_health_report_engine.py',
            'unified_system_monitor': 'unified_system_monitor.py',
            'workflow_engine': 'workflow_engine.py',
            'workflow_orchestrator': 'workflow_orchestrator.py',
            'auto_execution_engine': 'auto_execution_engine.py',
            'task_scheduler': 'task_scheduler.py',
            'cross_engine_task_planner': 'cross_engine_task_planner.py',
            'knowledge_graph': 'knowledge_graph.py',
            'enhanced_knowledge_reasoning_engine': 'enhanced_knowledge_reasoning_engine.py',
            'system_health_check': 'system_health_check.py',
            'network_tool': 'network_tool.py',
            'env_tool': 'env_tool.py',
            'clipboard_tool': 'clipboard_tool.py',
            'keyboard_tool': 'keyboard_tool.py',
            'window_tool': 'window_tool.py',
            'launch_browser': 'launch_browser.py',
            'adaptive_learning_engine': 'adaptive_learning_engine.py',
            'user_behavior_learner': 'user_behavior_learner.py',
            'long_term_memory_engine': 'long_term_memory_engine.py',
            'creative_generation_engine': 'creative_generation_engine.py',
            'proactive_insight_engine': 'proactive_insight_engine.py',
            'multi_dim_analysis_engine': 'multi_dim_analysis_engine.py',
            'data_insight_engine': 'data_insight_engine.py',
            'behavior_sequence_prediction_engine': 'behavior_sequence_prediction_engine.py',
            'evolution_prediction_planner': 'evolution_prediction_planner.py',
            'multi_agent_collaboration_engine': 'multi_agent_collaboration_engine.py',
            'unified_recommender': 'unified_recommender.py'
        }

        script_name = engine_scripts.get(engine_name)
        if not script_name:
            return {'success': False, 'error': f'未知引擎: {engine_name}'}

        script_path = self.scripts_dir / script_name

        # 如果是 Python 脚本，直接调用
        if script_path.exists():
            try:
                cmd = [sys.executable, str(script_path)]
                if params:
                    for k, v in params.items():
                        cmd.extend([f'--{k}', str(v)])

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
                    'engine': engine_name,
                    'output': result.stdout[:500] if result.stdout else '',
                    'error': result.stderr[:200] if result.stderr else None
                }
            except subprocess.TimeoutExpired:
                return {'success': False, 'error': '执行超时', 'engine': engine_name}
            except Exception as e:
                return {'success': False, 'error': str(e), 'engine': engine_name}
        else:
            return {'success': False, 'error': f'脚本不存在: {script_name}', 'engine': engine_name}

    def orchestrate_service_chain(self, user_input: str) -> Dict[str, Any]:
        """编排服务链 - 智能协同多个引擎"""

        # 1. 深度意图分析
        intent_analysis = self.analyze_intent_deeply(user_input)

        # 2. 选择引擎组合
        engine_combination = self.select_engine_combination(intent_analysis)

        # 3. 执行引擎链
        results = []
        for engine in engine_combination:
            result = self.call_engine(engine, {'query': user_input})
            results.append({
                'engine': engine,
                'result': result
            })

        # 4. 聚合结果
        return {
            'success': True,
            'user_input': user_input,
            'intent_analysis': intent_analysis,
            'engine_combination': engine_combination,
            'results': results,
            'summary': self._generate_summary(results, intent_analysis)
        }

    def _generate_summary(self, results: List[Dict], intent_analysis: Dict) -> str:
        """生成结果摘要"""
        success_count = sum(1 for r in results if r['result'].get('success', False))
        total_count = len(results)

        summary_parts = [
            f"意图识别: {intent_analysis['primary_intent']}",
            f"置信度: {intent_analysis['confidence']:.0%}",
            f"引擎组合: {', '.join(intent_analysis.get('engine_combination', []))}",
            f"执行结果: {success_count}/{total_count} 成功"
        ]

        return " | ".join(summary_parts)

    def process_request(self, user_input: str) -> Dict[str, Any]:
        """处理用户请求的统一入口"""

        # 1. 深度意图分析
        intent_analysis = self.analyze_intent_deeply(user_input)

        # 2. 选择引擎组合
        engine_combination = self.select_engine_combination(intent_analysis)

        # 3. 如果需要多引擎协同，执行服务链
        if intent_analysis['needs_collaboration'] or len(engine_combination) > 1:
            result = self.orchestrate_service_chain(user_input)
        else:
            # 单引擎执行
            result = self.call_engine(engine_combination[0] if engine_combination else 'unified_recommender',
                                      {'query': user_input})

        # 4. 记录历史
        self.add_history(user_input, intent_analysis['primary_intent'], result,
                        'success' if result.get('success') else 'failed')

        return {
            'user_input': user_input,
            'intent_analysis': intent_analysis,
            'engine_combination': engine_combination,
            'result': result
        }

    def add_history(self, request: str, intent_type: str, result: Any, status: str):
        """添加服务历史记录"""
        self.service_history.append({
            'timestamp': datetime.now().isoformat(),
            'request': request,
            'intent_type': intent_type,
            'status': status,
            'result_summary': str(result)[:200] if result else ''
        })
        self.save_history()

    def get_status(self) -> Dict[str, Any]:
        """获取服务引擎状态"""
        return {
            'supported_intents': list(self.intent_patterns.keys()),
            'complex_patterns': len(self.complex_patterns),
            'history_count': len(self.service_history),
            'user_context': self.user_context
        }

    def get_capabilities(self) -> Dict[str, Any]:
        """获取引擎能力描述"""
        capabilities = {}
        for intent_name, info in self.intent_patterns.items():
            capabilities[intent_name] = {
                'description': info['description'],
                'keywords': info['keywords'],
                'engines': info['engines']
            }
        return capabilities


def main():
    """命令行入口"""
    import argparse
    import io

    # 设置 stdout 编码为 UTF-8
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except:
        pass

    parser = argparse.ArgumentParser(description='智能全场景服务融合引擎')
    parser.add_argument('command', nargs='?', default='status',
                        help='命令: status, query, capabilities, analyze')
    parser.add_argument('--query', '-q', type=str, help='查询内容')
    parser.add_argument('--input', '-i', type=str, help='用户输入（模糊需求）')

    args = parser.parse_args()

    engine = FullScenarioServiceFusionEngine()

    if args.command == 'status':
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.command == 'capabilities':
        caps = engine.get_capabilities()
        print(json.dumps(caps, ensure_ascii=False, indent=2))

    elif args.command == 'analyze':
        query = args.query or args.input or ''
        if not query:
            print("错误: 请提供 --query 或 --input 参数")
            sys.exit(1)

        analysis = engine.analyze_intent_deeply(query)
        print(json.dumps(analysis, ensure_ascii=False, indent=2))

    elif args.command == 'query':
        query = args.query or args.input or ''
        if not query:
            print("错误: 请提供 --query 或 --input 参数")
            sys.exit(1)

        result = engine.process_request(query)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == '__main__':
    main()