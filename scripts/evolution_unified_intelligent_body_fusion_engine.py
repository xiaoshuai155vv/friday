"""
智能全场景统一进化智能体深度融合引擎

将评估(r390)、预测(r389/337)、预防(r361)、决策(r371/372)、执行(r372/380/382)、学习(r338/352)等多维度智能融合能力深度集成，构建统一的进化智能体核心。

实现从「多引擎协同」到「统一智能体」的关键跃迁，形成真正的进化智慧大脑。

版本: 1.0.0
创建时间: 2026-03-14
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# 添加 scripts 目录到 Python 路径
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

# 导入相关引擎
try:
    from evolution_evaluation_prediction_prevention_integration_engine import EvolutionEvaluationPredictionPreventionIntegrationEngine
except ImportError:
    EvolutionEvaluationPredictionPreventionIntegrationEngine = None

try:
    from evolution_autonomous_unattended_enhancement_engine import EvolutionAutonomousUnattendedEnhancementEngine
except ImportError:
    EvolutionAutonomousUnattendedEnhancementEngine = None

try:
    from evolution_decision_execution_closed_loop import EvolutionDecisionExecutionClosedLoop
except ImportError:
    EvolutionDecisionExecutionClosedLoop = None

try:
    from evolution_self_evaluation_strategy_iteration_engine import EvolutionSelfEvaluationStrategyIterationEngine
except ImportError:
    EvolutionSelfEvaluationStrategyIterationEngine = None


class EvolutionUnifiedIntelligentBodyFusionEngine:
    """统一进化智能体深度融合引擎"""

    VERSION = "1.0.0"

    def __init__(self):
        self.name = "统一进化智能体融合引擎"
        self.description = "多维度智能深度融合，构建统一进化智能体核心"
        self.engines = {}

        # 初始化子引擎
        if EvolutionEvaluationPredictionPreventionIntegrationEngine:
            self.engines['evaluation'] = EvolutionEvaluationPredictionPreventionIntegrationEngine()
            print(f"[{self.name}] 评估引擎已加载")

        if EvolutionAutonomousUnattendedEnhancementEngine:
            self.engines['unattended'] = EvolutionAutonomousUnattendedEnhancementEngine()
            print(f"[{self.name}] 无人值守引擎已加载")

        if EvolutionDecisionExecutionClosedLoop:
            self.engines['decision_execution'] = EvolutionDecisionExecutionClosedLoop()
            print(f"[{self.name}] 决策-执行引擎已加载")

        if EvolutionSelfEvaluationStrategyIterationEngine:
            self.engines['self_evaluation'] = EvolutionSelfEvaluationStrategyIterationEngine()
            print(f"[{self.name}] 自我评估引擎已加载")

        # 融合配置
        self.config = {
            'fusion_enabled': True,
            'decision_weight': 0.25,           # 决策权重
            'evaluation_weight': 0.25,         # 评估权重
            'prediction_weight': 0.20,         # 预测权重
            'execution_weight': 0.15,          # 执行权重
            'learning_weight': 0.15,           # 学习权重
            'auto_trigger_enabled': True,      # 自动触发
            'check_interval': 300,             # 检查间隔（秒）
        }

        # 状态记录
        self.state_file = "runtime/state/unified_intelligent_body_state.json"
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        """加载状态"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[{self.name}] 加载状态失败: {e}")
        return {
            'fusion_cycle_count': 0,
            'last_fusion_timestamp': '',
            'last_fusion_score': 0,
            'components_status': {},
            'fusion_history': [],
            'enabled': True
        }

    def _save_state(self):
        """保存状态"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def check_components_health(self) -> Dict:
        """检查各组件健康状态"""
        health_status = {}

        for name, engine in self.engines.items():
            try:
                if hasattr(engine, 'get_status'):
                    status = engine.get_status()
                    health_status[name] = {
                        'healthy': True,
                        'status': status
                    }
                elif hasattr(engine, 'health_check'):
                    result = engine.health_check()
                    health_status[name] = {
                        'healthy': result.get('healthy', True),
                        'status': result
                    }
                else:
                    health_status[name] = {
                        'healthy': True,
                        'status': 'unknown'
                    }
            except Exception as e:
                health_status[name] = {
                    'healthy': False,
                    'error': str(e)
                }

        return health_status

    def run_evaluation(self) -> Dict:
        """运行评估"""
        if 'evaluation' in self.engines:
            try:
                if hasattr(self.engines['evaluation'], 'run_full_integration_cycle'):
                    raw_result = self.engines['evaluation'].run_full_integration_cycle()
                elif hasattr(self.engines['evaluation'], 'run_full_cycle'):
                    raw_result = self.engines['evaluation'].run_full_cycle()
                elif hasattr(self.engines['evaluation'], 'run'):
                    raw_result = self.engines['evaluation'].run()
                else:
                    return {'evaluation_score': 0, 'conclusion': '评估引擎无可用方法'}

                # 提取分数
                evaluation_score = 0
                if isinstance(raw_result, dict):
                    fusion_data = raw_result.get('fusion', {})
                    if isinstance(fusion_data, dict):
                        evaluation_score = fusion_data.get('integrated_score', 0)

                return {
                    'evaluation_score': evaluation_score,
                    'raw_result': raw_result,
                    'conclusion': '评估完成'
                }
            except Exception as e:
                return {'evaluation_score': 0, 'conclusion': f'评估失败: {str(e)}'}
        else:
            return {'evaluation_score': 0, 'conclusion': '评估引擎未加载'}

    def run_decision(self, context: Dict = None) -> Dict:
        """运行决策"""
        if 'decision_execution' in self.engines:
            try:
                engine = self.engines['decision_execution']
                if hasattr(engine, 'run_full_cycle'):
                    result = engine.run_full_cycle(context)
                elif hasattr(engine, 'run'):
                    result = engine.run(context)
                else:
                    return {'decision': None, 'conclusion': '决策引擎无可用方法'}

                return {
                    'decision': result,
                    'conclusion': '决策完成'
                }
            except Exception as e:
                return {'decision': None, 'conclusion': f'决策失败: {str(e)}'}
        else:
            return {'decision': None, 'conclusion': '决策引擎未加载'}

    def run_execution(self, guidance: Dict = None) -> Dict:
        """运行执行"""
        if 'unattended' in self.engines:
            try:
                result = self.engines['unattended'].trigger_evolution(guidance)
                return {
                    'execution_result': result,
                    'conclusion': '执行完成'
                }
            except Exception as e:
                return {'execution_result': None, 'conclusion': f'执行失败: {str(e)}'}
        else:
            return {'execution_result': None, 'conclusion': '执行引擎未加载'}

    def run_learning(self) -> Dict:
        """运行学习"""
        if 'self_evaluation' in self.engines:
            try:
                engine = self.engines['self_evaluation']
                if hasattr(engine, 'run_full_cycle'):
                    result = engine.run_full_cycle()
                elif hasattr(engine, 'analyze'):
                    result = engine.analyze()
                else:
                    return {'learning_result': None, 'conclusion': '学习引擎无可用方法'}

                return {
                    'learning_result': result,
                    'conclusion': '学习完成'
                }
            except Exception as e:
                return {'learning_result': None, 'conclusion': f'学习失败: {str(e)}'}
        else:
            return {'learning_result': None, 'conclusion': '学习引擎未加载'}

    def calculate_fusion_score(self, components: Dict) -> float:
        """计算融合分数"""
        scores = {
            'evaluation': components.get('evaluation', {}).get('evaluation_score', 0),
            'decision': components.get('decision', {}).get('decision', {}).get('score', 50),
            'execution': 50 if components.get('execution', {}).get('execution_result', {}).get('success', False) else 0,
            'learning': components.get('learning', {}).get('learning_result', {}).get('optimization_score', 50),
        }

        # 加权计算
        fusion_score = (
            scores['evaluation'] * self.config['evaluation_weight'] +
            scores['decision'] * self.config['decision_weight'] +
            scores['execution'] * self.config['execution_weight'] +
            scores['learning'] * self.config['learning_weight']
        )

        return fusion_score

    def run_full_fusion_cycle(self) -> Dict:
        """运行完整的融合循环"""
        print(f"\n[{self.name}] 开始执行统一智能体融合循环...")

        components = {}

        # 1. 评估
        print("[1/5] 运行评估...")
        components['evaluation'] = self.run_evaluation()

        # 2. 决策
        print("[2/5] 运行决策...")
        components['decision'] = self.run_decision({
            'evaluation': components['evaluation']
        })

        # 3. 执行（如果决策需要执行）
        decision_result = components['decision'].get('decision', {})
        if decision_result and decision_result.get('should_execute', False):
            print("[3/5] 执行决策...")
            components['execution'] = self.run_execution({
                'decision': decision_result,
                'evaluation': components['evaluation']
            })
        else:
            print("[3/5] 跳过执行（决策无需执行）")
            components['execution'] = {'execution_result': {'success': True, 'message': '无需执行'}, 'conclusion': '跳过执行'}

        # 4. 学习
        print("[4/5] 运行学习...")
        components['learning'] = self.run_learning()

        # 5. 计算融合分数
        print("[5/5] 计算融合分数...")
        fusion_score = self.calculate_fusion_score(components)

        # 更新状态
        self.state['fusion_cycle_count'] += 1
        self.state['last_fusion_timestamp'] = datetime.now().isoformat()
        self.state['last_fusion_score'] = fusion_score
        self.state['components_status'] = {
            'evaluation': components['evaluation'].get('conclusion', 'unknown'),
            'decision': components['decision'].get('conclusion', 'unknown'),
            'execution': components['execution'].get('conclusion', 'unknown'),
            'learning': components['learning'].get('conclusion', 'unknown'),
        }
        self._save_state()

        # 记录历史
        self.state['fusion_history'].append({
            'timestamp': datetime.now().isoformat(),
            'fusion_score': fusion_score,
            'components': self.state['components_status'].copy()
        })
        self.state['fusion_history'] = self.state['fusion_history'][-20:]
        self._save_state()

        summary = {
            'timestamp': datetime.now().isoformat(),
            'fusion_cycle': self.state['fusion_cycle_count'],
            'fusion_score': fusion_score,
            'components': components,
            'conclusion': '融合循环完成'
        }

        print(f"\n[{self.name}] 融合循环执行完成")
        print(f"  融合分数: {fusion_score}")
        print(f"  评估状态: {components['evaluation'].get('conclusion', 'unknown')}")
        print(f"  决策状态: {components['decision'].get('conclusion', 'unknown')}")
        print(f"  执行状态: {components['execution'].get('conclusion', 'unknown')}")
        print(f"  学习状态: {components['learning'].get('conclusion', 'unknown')}")

        return summary

    def get_status(self) -> Dict:
        """获取状态"""
        health = self.check_components_health()

        return {
            'engine': self.name,
            'version': self.VERSION,
            'enabled': self.state['enabled'],
            'fusion_cycle_count': self.state['fusion_cycle_count'],
            'last_fusion_timestamp': self.state['last_fusion_timestamp'],
            'last_fusion_score': self.state['last_fusion_score'],
            'components_health': health,
            'components_status': self.state['components_status'],
            'engines_loaded': list(self.engines.keys()),
            'config': self.config
        }

    def get_fusion_history(self) -> List[Dict]:
        """获取融合历史"""
        return self.state.get('fusion_history', [])

    def enable(self):
        """启用融合引擎"""
        self.state['enabled'] = True
        self._save_state()
        print(f"[{self.name}] 融合引擎已启用")

    def disable(self):
        """禁用融合引擎"""
        self.state['enabled'] = False
        self._save_state()
        print(f"[{self.name}] 融合引擎已禁用")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='统一进化智能体融合引擎')
    parser.add_argument('command', nargs='?', default='status',
                       choices=['status', 'full_cycle', 'evaluate', 'decision', 'execution', 'learning', 'health', 'history', 'enable', 'disable'],
                       help='命令')

    args = parser.parse_args()

    engine = EvolutionUnifiedIntelligentBodyFusionEngine()

    if args.command == 'status':
        result = engine.get_status()
        print("\n=== 统一进化智能体融合引擎状态 ===")
        print(f"引擎: {result['engine']}")
        print(f"版本: {result['version']}")
        print(f"融合引擎: {'启用' if result['enabled'] else '禁用'}")
        print(f"融合循环次数: {result['fusion_cycle_count']}")
        print(f"最后融合时间: {result['last_fusion_timestamp'] or '无'}")
        print(f"最后融合分数: {result['last_fusion_score']}")
        print(f"已加载引擎: {', '.join(result['engines_loaded']) if result['engines_loaded'] else '无'}")
        print("\n组件状态:")
        for k, v in result['components_status'].items():
            print(f"  {k}: {v}")

    elif args.command == 'full_cycle':
        result = engine.run_full_fusion_cycle()
        print("\n=== 完整融合循环结果 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'evaluate':
        result = engine.run_evaluation()
        print("\n=== 评估结果 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'decision':
        result = engine.run_decision()
        print("\n=== 决策结果 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'execution':
        result = engine.run_execution()
        print("\n=== 执行结果 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'learning':
        result = engine.run_learning()
        print("\n=== 学习结果 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'health':
        result = engine.check_components_health()
        print("\n=== 组件健康状态 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'history':
        result = engine.get_fusion_history()
        print("\n=== 融合历史 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'enable':
        engine.enable()

    elif args.command == 'disable':
        engine.disable()


if __name__ == "__main__":
    main()