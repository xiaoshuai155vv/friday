"""
智能全场景进化环评估-预测-预防能力与完全无人值守进化环深度集成引擎

将评估-预测-预防能力与完全无人值守进化环深度集成，实现基于评估结果的自动化触发执行。
让系统能够根据评估分数、预测结果自动判断是否触发进化、如何触发，形成真正的自主进化闭环。

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


class EvolutionEvaluationUnattendedIntegrationEngine:
    """评估-预测-预防能力与完全无人值守进化环深度集成引擎"""

    VERSION = "1.0.0"

    def __init__(self):
        self.name = "评估-无人值守集成引擎"
        self.description = "评估-预测-预防与完全无人值守进化环深度集成"
        self.engines = {}

        # 初始化子引擎
        if EvolutionEvaluationPredictionPreventionIntegrationEngine:
            self.engines['evaluation'] = EvolutionEvaluationPredictionPreventionIntegrationEngine()
            print(f"[{self.name}] 评估引擎已加载")

        if EvolutionAutonomousUnattendedEnhancementEngine:
            self.engines['unattended'] = EvolutionAutonomousUnattendedEnhancementEngine()
            print(f"[{self.name}] 无人值守引擎已加载")

        # 触发阈值配置
        self.config = {
            'auto_trigger_enabled': True,
            'evaluation_threshold_low': 30,      # 低于此分数自动触发进化
            'evaluation_threshold_high': 80,      # 高于此分数可考虑加速进化
            'prediction_risk_threshold': 70,     # 预测风险高于此值禁止自动进化
            'check_interval': 300,               # 检查间隔（秒）
            'max_auto_evolution_per_day': 10,    # 每日最大自动进化次数
        }

        # 状态记录
        self.state_file = "runtime/state/evaluation_unattended_state.json"
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
            'auto_evolution_count_today': 0,
            'last_auto_evolution_date': '',
            'last_evaluation_score': 0,
            'last_prediction_score': 0,
            'auto_trigger_history': [],
            'enabled': True
        }

    def _save_state(self):
        """保存状态"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def run_evaluation(self) -> Dict:
        """运行评估"""
        if 'evaluation' in self.engines:
            try:
                # 尝试不同的方法名
                if hasattr(self.engines['evaluation'], 'run_full_integration_cycle'):
                    raw_result = self.engines['evaluation'].run_full_integration_cycle()
                elif hasattr(self.engines['evaluation'], 'run_full_cycle'):
                    raw_result = self.engines['evaluation'].run_full_cycle()
                elif hasattr(self.engines['evaluation'], 'run'):
                    raw_result = self.engines['evaluation'].run()
                else:
                    return {'evaluation_score': 0, 'prediction_score': 0, 'prevention_status': 'unknown', 'fusion_score': 0, 'conclusion': '评估引擎无可用方法'}

                # 提取分数
                evaluation_score = 0
                prediction_score = 0
                fusion_score = 0
                risk_level = 'unknown'

                # 从嵌套结构中提取
                if isinstance(raw_result, dict):
                    fusion_data = raw_result.get('fusion', {})
                    if isinstance(fusion_data, dict):
                        evaluation_score = fusion_data.get('evaluation_score', 0)
                        prediction_score = fusion_data.get('prediction_score', 0)
                        fusion_score = fusion_data.get('integrated_score', 0)
                        risk_level = fusion_data.get('prediction_risk_level', 'unknown')

                    prediction_data = raw_result.get('prediction', {})
                    if isinstance(prediction_data, dict):
                        risk_data = prediction_data.get('risk_assessment', {})
                        if isinstance(risk_data, dict):
                            risk_level = risk_data.get('risk_level', risk_level)

                return {
                    'evaluation_score': evaluation_score,
                    'prediction_score': prediction_score,
                    'prevention_status': {'risk_level': risk_level},
                    'fusion_score': fusion_score,
                    'raw_result': raw_result,
                    'conclusion': '评估完成'
                }
            except Exception as e:
                print(f"[{self.name}] 评估失败: {e}")
                return {
                    'evaluation_score': 0,
                    'prediction_score': 0,
                    'prevention_status': {'risk_level': 'unknown'},
                    'fusion_score': 0,
                    'conclusion': f'评估失败: {str(e)}'
                }
        else:
            return {
                'evaluation_score': 0,
                'prediction_score': 0,
                'prevention_status': {'risk_level': 'no_engine'},
                'fusion_score': 0,
                'conclusion': '评估引擎未加载'
            }

    def should_auto_evolve(self, evaluation_result: Dict) -> Dict:
        """根据评估结果判断是否应该自动触发进化"""
        eval_score = evaluation_result.get('evaluation_score', 0)
        pred_score = evaluation_result.get('prediction_score', 0)

        # 处理 prevention_status 可能是字符串或字典的情况
        prevention_status = evaluation_result.get('prevention_status', {})
        if isinstance(prevention_status, dict):
            risk_level = prevention_status.get('risk_level', 'unknown')
        else:
            risk_level = str(prevention_status) if prevention_status else 'unknown'

        # 检查是否启用自动触发
        if not self.config['auto_trigger_enabled']:
            return {
                'should_evolve': False,
                'reason': '自动触发已禁用',
                'confidence': 100
            }

        # 检查每日进化次数限制
        today = datetime.now().strftime('%Y-%m-%d')
        if self.state['last_auto_evolution_date'] != today:
            self.state['auto_evolution_count_today'] = 0
            self.state['last_auto_evolution_date'] = today

        if self.state['auto_evolution_count_today'] >= self.config['max_auto_evolution_per_day']:
            return {
                'should_evolve': False,
                'reason': f"已达到每日最大进化次数({self.config['max_auto_evolution_per_day']})",
                'confidence': 100
            }

        # 风险评估
        if risk_level == 'high' or pred_score > self.config['prediction_risk_threshold']:
            return {
                'should_evolve': False,
                'reason': f"风险等级过高(risk={risk_level}, pred={pred_score})，禁止自动进化",
                'confidence': 95
            }

        # 评估分数判断
        if eval_score < self.config['evaluation_threshold_low']:
            # 分数过低，建议立即进化
            confidence = min(100, (self.config['evaluation_threshold_low'] - eval_score) * 3)
            return {
                'should_evolve': True,
                'reason': f"评估分数过低({eval_score})，需要进化",
                'confidence': confidence,
                'urgency': 'high'
            }
        elif eval_score > self.config['evaluation_threshold_high']:
            # 分数很高，可以加速进化
            confidence = min(100, (eval_score - self.config['evaluation_threshold_high']) * 2)
            return {
                'should_evolve': True,
                'reason': f"系统状态优秀({eval_score})，可加速进化",
                'confidence': confidence,
                'urgency': 'low'
            }
        else:
            # 分数适中，维持当前状态
            return {
                'should_evolve': False,
                'reason': f"评估分数适中({eval_score})，无需强制进化",
                'confidence': 80
            }

    def execute_auto_evolution(self, guidance: Dict = None) -> Dict:
        """执行自动进化"""
        today = datetime.now().strftime('%Y-%m-%d')

        # 检查是否可执行
        if self.state['last_auto_evolution_date'] != today:
            self.state['auto_evolution_count_today'] = 0

        if self.state['auto_evolution_count_today'] >= self.config['max_auto_evolution_per_day']:
            return {
                'success': False,
                'message': f"已达到每日最大进化次数({self.config['max_auto_evolution_per_day']})"
            }

        # 调用无人值守引擎
        if 'unattended' in self.engines:
            try:
                result = self.engines['unattended'].trigger_evolution(guidance)
                self.state['auto_evolution_count_today'] += 1
                self._save_state()

                # 记录历史
                self.state['auto_trigger_history'].append({
                    'timestamp': datetime.now().isoformat(),
                    'guidance': guidance,
                    'result': result
                })
                # 只保留最近20条记录
                self.state['auto_trigger_history'] = self.state['auto_trigger_history'][-20:]
                self._save_state()

                return {
                    'success': True,
                    'message': '自动进化执行成功',
                    'result': result
                }
            except Exception as e:
                return {
                    'success': False,
                    'message': f"自动进化执行失败: {str(e)}"
                }
        else:
            return {
                'success': False,
                'message': '无人值守引擎未加载'
            }

    def run_full_cycle(self) -> Dict:
        """运行完整的评估-决策-执行循环"""
        print(f"\n[{self.name}] 开始执行完整循环...")

        # 1. 运行评估
        print("[1/4] 运行评估...")
        evaluation_result = self.run_evaluation()
        self.state['last_evaluation_score'] = evaluation_result.get('evaluation_score', 0)
        self.state['last_prediction_score'] = evaluation_result.get('prediction_score', 0)
        self._save_state()

        # 2. 判断是否触发进化
        print("[2/4] 分析是否需要触发进化...")
        auto_decision = self.should_auto_evolve(evaluation_result)

        # 3. 如果需要进化，执行自动进化
        evolution_result = None
        if auto_decision['should_evolve']:
            print(f"[3/4] 触发自动进化 (原因: {auto_decision['reason']})...")
            evolution_result = self.execute_auto_evolution({
                'evaluation': evaluation_result,
                'auto_decision': auto_decision
            })
        else:
            print(f"[3/4] 不触发自动进化 (原因: {auto_decision['reason']})")
            evolution_result = {'success': True, 'message': '不需要自动进化'}

        # 4. 生成总结
        print("[4/4] 生成总结...")
        summary = {
            'timestamp': datetime.now().isoformat(),
            'evaluation_result': evaluation_result,
            'auto_decision': auto_decision,
            'evolution_result': evolution_result,
            'state': {
                'auto_evolution_count_today': self.state['auto_evolution_count_today'],
                'enabled': self.state['enabled']
            }
        }

        print(f"\n[{self.name}] 完整循环执行完成")
        print(f"  评估分数: {evaluation_result.get('evaluation_score', 0)}")
        print(f"  预测分数: {evaluation_result.get('prediction_score', 0)}")
        print(f"  是否触发: {auto_decision['should_evolve']}")
        print(f"  原因: {auto_decision['reason']}")

        return summary

    def get_status(self) -> Dict:
        """获取状态"""
        return {
            'engine': self.name,
            'version': self.VERSION,
            'enabled': self.state['enabled'],
            'auto_evolution_today': self.state['auto_evolution_count_today'],
            'max_per_day': self.config['max_auto_evolution_per_day'],
            'last_evaluation_score': self.state['last_evaluation_score'],
            'last_prediction_score': self.state['last_prediction_score'],
            'engines_loaded': list(self.engines.keys()),
            'config': self.config
        }

    def enable(self):
        """启用自动触发"""
        self.state['enabled'] = True
        self._save_state()
        print(f"[{self.name}] 自动触发已启用")

    def disable(self):
        """禁用自动触发"""
        self.state['enabled'] = False
        self._save_state()
        print(f"[{self.name}] 自动触发已禁用")

    def set_threshold(self, threshold_type: str, value: float):
        """设置阈值"""
        if threshold_type in self.config:
            self.config[threshold_type] = value
            print(f"[{self.name}] {threshold_type} 设置为 {value}")
        else:
            print(f"[{self.name}] 未知阈值类型: {threshold_type}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='评估-无人值守集成引擎')
    parser.add_argument('command', nargs='?', default='status',
                       choices=['status', 'full_cycle', 'evaluate', 'enable', 'disable', 'config'],
                       help='命令')
    parser.add_argument('--threshold', type=str, help='设置阈值 (格式: type=value)')
    parser.add_argument('--check-interval', type=int, help='检查间隔(秒)')

    args = parser.parse_args()

    engine = EvolutionEvaluationUnattendedIntegrationEngine()

    if args.command == 'status':
        result = engine.get_status()
        print("\n=== 评估-无人值守集成引擎状态 ===")
        print(f"引擎: {result['engine']}")
        print(f"版本: {result['version']}")
        print(f"自动触发: {'启用' if result['enabled'] else '禁用'}")
        print(f"今日自动进化次数: {result['auto_evolution_today']}/{result['max_per_day']}")
        print(f"最后评估分数: {result['last_evaluation_score']}")
        print(f"最后预测分数: {result['last_prediction_score']}")
        print(f"已加载引擎: {', '.join(result['engines_loaded']) if result['engines_loaded'] else '无'}")
        print("\n配置:")
        for k, v in result['config'].items():
            print(f"  {k}: {v}")

    elif args.command == 'full_cycle':
        result = engine.run_full_cycle()
        print("\n=== 完整循环结果 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'evaluate':
        result = engine.run_evaluation()
        print("\n=== 评估结果 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'enable':
        engine.enable()

    elif args.command == 'disable':
        engine.disable()

    elif args.command == 'config':
        if args.threshold:
            parts = args.threshold.split('=')
            if len(parts) == 2:
                engine.set_threshold(parts[0], float(parts[1]))
            else:
                print("格式错误，应为 type=value")
        else:
            print("当前配置:")
            for k, v in engine.config.items():
                print(f"  {k}: {v}")


if __name__ == "__main__":
    main()