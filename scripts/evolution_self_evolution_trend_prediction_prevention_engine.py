#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环自我进化效能趋势预测与预防性策略动态调整引擎
version 1.0.0

让系统能够基于历史进化效能数据预测未来趋势，提前识别可能的效能下降风险，
并自动生成预防性的策略调整建议，形成「评估→预测→预防→优化」的完整闭环。

这是对 round 549 自我进化能力深度增强引擎 V2 的深度增强：
- 集成 V2 引擎的评估结果
- 实现基于历史数据的趋势预测
- 实现风险预警与预防性策略调整
- 实现从「预测→预防→执行」的完整闭环

功能：
1. 进化效能趋势预测（基于历史评估数据分析未来走势）
2. 风险预警（提前识别可能的效能下降或健康问题）
3. 预防性策略调整（自动生成预防性优化建议）
4. 动态策略优化（根据趋势预测结果自动调整进化策略）
5. 驾驶舱数据接口（可视化趋势与预测结果）

依赖：
- evolution_self_evolution_enhancement_v2.py (round 549)
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import statistics

# 路径配置
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

# 尝试导入依赖引擎
try:
    from evolution_self_evolution_enhancement_v2 import (
        SelfEvolutionEnhancementV2Engine
    )
    SELF_EVOLUTION_V2_AVAILABLE = True
except ImportError:
    SELF_EVOLUTION_V2_AVAILABLE = False
    print("[警告] 无法导入自我进化能力增强引擎 V2，将使用简化模式")


class SelfEvolutionTrendPredictionPreventionEngine:
    """自我进化效能趋势预测与预防性策略动态调整引擎"""

    VERSION = "1.0.0"

    def __init__(self):
        """初始化引擎"""
        # 初始化依赖引擎
        self.self_evolution_v2_engine = None

        if SELF_EVOLUTION_V2_AVAILABLE:
            try:
                self.self_evolution_v2_engine = SelfEvolutionEnhancementV2Engine()
            except Exception as e:
                print(f"[警告] 自我进化能力增强引擎 V2 初始化失败: {e}")

        # 状态文件路径
        self.state_dir = PROJECT_ROOT / "runtime" / "state"
        self.trend_state_path = self.state_dir / "self_evolution_trend_prediction_state.json"

        # 趋势历史
        self.trend_history = self._load_trend_history()

    def _load_trend_history(self) -> List[Dict]:
        """加载趋势历史"""
        if self.trend_state_path.exists():
            try:
                with open(self.trend_state_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('trend_history', [])
            except Exception as e:
                print(f"[警告] 加载趋势历史失败: {e}")
        return []

    def _save_trend_history(self):
        """保存趋势历史"""
        try:
            self.state_dir.mkdir(parents=True, exist_ok=True)
            with open(self.trend_state_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'trend_history': self.trend_history[-30:],  # 保留最近30条
                    'last_update': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[警告] 保存趋势历史失败: {e}")

    def _calculate_trend(self, values: List[float]) -> Dict:
        """计算趋势

        Args:
            values: 数值序列

        Returns:
            趋势分析结果
        """
        if not values or len(values) < 2:
            return {
                'direction': 'unknown',
                'slope': 0.0,
                'volatility': 0.0,
                'confidence': 'low'
            }

        n = len(values)
        x_mean = (n - 1) / 2
        y_mean = statistics.mean(values)

        # 计算斜率（线性回归）
        numerator = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            slope = 0.0
        else:
            slope = numerator / denominator

        # 计算波动性
        if len(values) >= 2:
            volatility = statistics.stdev(values) if len(values) > 1 else 0.0
        else:
            volatility = 0.0

        # 判断趋势方向
        if abs(slope) < 0.5:
            direction = 'stable'
        elif slope > 0:
            direction = 'improving'
        else:
            direction = 'declining'

        # 置信度
        confidence = 'high' if len(values) >= 5 else ('medium' if len(values) >= 3 else 'low')

        return {
            'direction': direction,
            'slope': round(slope, 2),
            'volatility': round(volatility, 2),
            'confidence': confidence,
            'values': values,
            'count': len(values)
        }

    def predict_evolution_trend(self) -> Dict:
        """预测进化效能趋势

        基于历史评估数据预测未来趋势。

        Returns:
            趋势预测结果
        """
        # 获取当前评估数据
        if self.self_evolution_v2_engine:
            try:
                current_evaluation = self.self_evolution_v2_engine.evaluate_evolution_state()
            except Exception as e:
                print(f"[警告] 获取当前评估失败: {e}")
                current_evaluation = {
                    'evolution_capability_index': 75,
                    'health_score': 75,
                    'efficiency_score': 75,
                    'timestamp': datetime.now().isoformat()
                }
        else:
            current_evaluation = {
                'evolution_capability_index': 75,
                'health_score': 75,
                'efficiency_score': 75,
                'timestamp': datetime.now().isoformat()
            }

        # 构建趋势数据
        health_scores = [h.get('health_score', 75) for h in self.trend_history if 'health_score' in h]
        efficiency_scores = [h.get('efficiency_score', 75) for h in self.trend_history if 'efficiency_score' in h]
        capability_indices = [h.get('capability_index', 75) for h in self.trend_history if 'capability_index' in h]

        # 添加当前值
        health_scores.append(current_evaluation.get('health_score', 75))
        efficiency_scores.append(current_evaluation.get('efficiency_score', 75))
        capability_indices.append(current_evaluation.get('evolution_capability_index', 75))

        # 计算趋势
        health_trend = self._calculate_trend(health_scores)
        efficiency_trend = self._calculate_trend(efficiency_scores)
        capability_trend = self._calculate_trend(capability_indices)

        # 综合预测
        overall_trend_direction = capability_trend['direction']

        # 预测未来状态（基于当前趋势）
        predicted_index = current_evaluation.get('evolution_capability_index', 75)
        if capability_trend['direction'] == 'declining' and capability_trend['confidence'] != 'low':
            predicted_index = max(50, predicted_index + capability_trend['slope'] * 3)  # 预测3期后
        elif capability_trend['direction'] == 'improving' and capability_trend['confidence'] != 'low':
            predicted_index = min(100, predicted_index + capability_trend['slope'] * 3)

        # 构建预测结果
        prediction_result = {
            'timestamp': datetime.now().isoformat(),
            'current_state': {
                'capability_index': current_evaluation.get('evolution_capability_index', 75),
                'health_score': current_evaluation.get('health_score', 75),
                'efficiency_score': current_evaluation.get('efficiency_score', 75)
            },
            'trends': {
                'health': health_trend,
                'efficiency': efficiency_trend,
                'capability': capability_trend
            },
            'prediction': {
                'predicted_index': round(predicted_index, 2),
                'prediction_horizon': '3_rounds',
                'confidence': capability_trend['confidence']
            },
            'overall_trend': overall_trend_direction,
            'round': current_evaluation.get('current_round', 550)
        }

        # 保存趋势数据
        self.trend_history.append({
            'timestamp': prediction_result['timestamp'],
            'health_score': current_evaluation.get('health_score', 75),
            'efficiency_score': current_evaluation.get('efficiency_score', 75),
            'capability_index': current_evaluation.get('evolution_capability_index', 75),
            'overall_trend': overall_trend_direction
        })
        self._save_trend_history()

        return prediction_result

    def identify_risks(self) -> List[Dict]:
        """识别风险

        基于趋势分析识别潜在风险。

        Returns:
            风险列表
        """
        prediction = self.predict_evolution_trend()
        risks = []

        # 检查下降趋势
        if prediction['trends']['capability']['direction'] == 'declining':
            risks.append({
                'id': 'capability_declining',
                'type': 'trend',
                'severity': 'high' if prediction['trends']['capability']['confidence'] == 'high' else 'medium',
                'description': f"综合进化能力呈下降趋势（斜率: {prediction['trends']['capability']['slope']}）",
                'confidence': prediction['trends']['capability']['confidence'],
                'suggested_action': '启动预防性优化策略'
            })

        # 检查健康评分下降
        if prediction['trends']['health']['direction'] == 'declining':
            risks.append({
                'id': 'health_declining',
                'type': 'health',
                'severity': 'medium',
                'description': f"健康评分呈下降趋势（斜率: {prediction['trends']['health']['slope']}）",
                'confidence': prediction['trends']['health']['confidence'],
                'suggested_action': '加强健康监测和自愈策略'
            })

        # 检查效能评分下降
        if prediction['trends']['efficiency']['direction'] == 'declining':
            risks.append({
                'id': 'efficiency_declining',
                'type': 'efficiency',
                'severity': 'medium',
                'description': f"效能评分呈下降趋势（斜率: {prediction['trends']['efficiency']['slope']}）",
                'confidence': prediction['trends']['efficiency']['confidence'],
                'suggested_action': '优化执行策略和资源分配'
            })

        # 检查预测值低于阈值
        if prediction['prediction']['predicted_index'] < 60:
            risks.append({
                'id': 'low_predicted_index',
                'type': 'prediction',
                'severity': 'high',
                'description': f"预测显示未来能力指数可能降至 {prediction['prediction']['predicted_index']}",
                'confidence': prediction['prediction']['confidence'],
                'suggested_action': '立即触发预防性优化'
            })

        # 检查高波动性
        if prediction['trends']['capability']['volatility'] > 15:
            risks.append({
                'id': 'high_volatility',
                'type': 'stability',
                'severity': 'medium',
                'description': f"能力指数波动性较高（{prediction['trends']['capability']['volatility']}）",
                'confidence': 'high',
                'suggested_action': '加强稳定性优化'
            })

        # 按严重性排序
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        risks.sort(key=lambda x: (severity_order.get(x['severity'], 2), -len(risks)))

        return risks

    def generate_preventive_strategies(self) -> Dict:
        """生成预防性策略

        基于风险识别结果生成预防性调整策略。

        Returns:
            预防性策略
        """
        risks = self.identify_risks()

        if not risks:
            return {
                'status': 'optimal',
                'message': '当前无明显风险，无需预防性策略',
                'strategies': []
            }

        strategies = []
        for risk in risks[:5]:  # 最多5条策略
            strategy = {
                'risk_id': risk['id'],
                'risk_type': risk['type'],
                'severity': risk['severity'],
                'description': risk['description'],
                'action': self._generate_strategy_action(risk),
                'priority': 1 if risk['severity'] == 'high' else (2 if risk['severity'] == 'medium' else 3),
                'expected_impact': self._estimate_impact(risk)
            }
            strategies.append(strategy)

        # 按优先级排序
        strategies.sort(key=lambda x: x['priority'])

        return {
            'status': 'risk_detected',
            'message': f'发现 {len(risks)} 个潜在风险，已生成 {len(strategies)} 条预防性策略',
            'risk_count': len(risks),
            'strategies': strategies,
            'top_priority_action': strategies[0]['action'] if strategies else None
        }

    def _generate_strategy_action(self, risk: Dict) -> str:
        """生成策略动作"""
        risk_type = risk.get('type', '')

        action_map = {
            'trend': '调整进化策略参数，增加稳定性保障',
            'health': '加强健康监测频率，启用自愈机制',
            'efficiency': '优化执行流程，分配更多资源',
            'prediction': '立即触发预防性优化流程',
            'stability': '增加执行验证环节，提高容错能力'
        }

        return action_map.get(risk_type, '执行通用优化策略')

    def _estimate_impact(self, risk: Dict) -> str:
        """估计影响"""
        severity = risk.get('severity', 'low')
        severity_impact = {
            'high': '预计提升能力指数 10-15%',
            'medium': '预计提升能力指数 5-10%',
            'low': '预计提升能力指数 2-5%'
        }
        return severity_impact.get(severity, '预计小幅提升')

    def apply_preventive_strategies(self) -> Dict:
        """应用预防性策略

        自动应用预防性策略（记录策略，供决策引擎使用）。

        Returns:
            应用结果
        """
        strategies = self.generate_preventive_strategies()

        if strategies['status'] == 'optimal':
            return {
                'status': 'no_action_needed',
                'message': strategies['message'],
                'applied_strategies': []
            }

        # 保存策略到状态文件
        strategy_file = self.state_dir / "preventive_strategies.json"
        try:
            self.state_dir.mkdir(parents=True, exist_ok=True)
            with open(strategy_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'strategies': strategies['strategies'],
                    'status': strategies['status']
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[警告] 保存预防性策略失败: {e}")

        return {
            'status': 'strategies_generated',
            'message': f'已生成 {len(strategies["strategies"])} 条预防性策略',
            'applied_strategies': strategies['strategies'],
            'strategy_file': str(strategy_file)
        }

    def get_cockpit_data(self) -> Dict:
        """获取驾驶舱展示数据

        Returns:
            驾驶舱数据
        """
        prediction = self.predict_evolution_trend()
        risks = self.identify_risks()
        strategies = self.generate_preventive_strategies()

        return {
            'prediction': prediction,
            'risks': risks,
            'strategies': strategies,
            'trend_summary': {
                'current_index': prediction['current_state']['capability_index'],
                'predicted_index': prediction['prediction']['predicted_index'],
                'overall_trend': prediction['overall_trend'],
                'risk_count': len(risks),
                'strategy_count': len(strategies.get('strategies', []))
            },
            'last_update': prediction['timestamp']
        }

    def run_full_cycle(self) -> Dict:
        """运行完整预测-预防周期

        Returns:
            完整结果
        """
        # 1. 预测趋势
        prediction = self.predict_evolution_trend()

        # 2. 识别风险
        risks = self.identify_risks()

        # 3. 生成策略
        strategies = self.generate_preventive_strategies()

        # 4. 应用策略
        application = self.apply_preventive_strategies()

        # 构建完整报告
        report = {
            'status': 'completed',
            'timestamp': datetime.now().isoformat(),
            'prediction': prediction,
            'risks': risks,
            'strategies': strategies,
            'application': application,
            'recommendation': self._generate_recommendation(prediction, risks, strategies)
        }

        return report

    def _generate_recommendation(self, prediction: Dict, risks: List[Dict], strategies: Dict) -> str:
        """生成推荐建议"""
        if not risks:
            return "当前进化状态稳定，趋势良好，建议继续保持当前策略。"

        if strategies['status'] == 'optimal':
            return "当前无明显风险，建议继续监控趋势变化。"

        high_severity_count = sum(1 for r in risks if r['severity'] == 'high')

        if high_severity_count > 0:
            return f"检测到 {high_severity_count} 个高风险，建议立即执行预防性策略以避免效能下降。"
        else:
            return f"检测到 {len(risks)} 个中等风险，建议关注并适时执行预防性策略。"

    def get_status_summary(self) -> str:
        """获取状态摘要

        Returns:
            状态摘要
        """
        prediction = self.predict_evolution_trend()
        risks = self.identify_risks()
        strategies = self.generate_preventive_strategies()

        summary = f"""
## 自我进化效能趋势预测与预防性策略报告

### 当前状态
- **综合能力指数**: {prediction['current_state']['capability_index']:.1f}
- **健康评分**: {prediction['current_state']['health_score']:.1f}
- **效能评分**: {prediction['current_state']['efficiency_score']:.1f}

### 趋势分析
- **整体趋势**: {prediction['overall_trend']}
- **预测能力指数（3轮后）**: {prediction['prediction']['predicted_index']:.1f}
- **预测置信度**: {prediction['prediction']['confidence']}

### 风险评估
- **风险数量**: {len(risks)}
"""

        if risks:
            summary += "#### 识别的风险\n"
            for i, risk in enumerate(risks[:3], 1):
                summary += f"{i}. [{risk['severity']}] {risk['description']}\n"

        if strategies.get('strategies'):
            summary += f"\n### 预防性策略 ({len(strategies['strategies'])}条)\n"
            for i, strategy in enumerate(strategies['strategies'][:3], 1):
                summary += f"{i}. {strategy['action']}\n"

        return summary


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description='智能全场景进化环自我进化效能趋势预测与预防性策略动态调整引擎'
    )
    parser.add_argument('--status', action='store_true', help='显示状态摘要')
    parser.add_argument('--predict', action='store_true', help='预测趋势')
    parser.add_argument('--risks', action='store_true', help='识别风险')
    parser.add_argument('--strategies', action='store_true', help='生成预防性策略')
    parser.add_argument('--apply', action='store_true', help='应用预防性策略')
    parser.add_argument('--cockpit-data', action='store_true', help='获取驾驶舱数据')
    parser.add_argument('--full-cycle', action='store_true', help='运行完整周期')

    args = parser.parse_args()

    # 初始化引擎
    engine = SelfEvolutionTrendPredictionPreventionEngine()

    # 执行命令
    if args.status:
        print(engine.get_status_summary())
    elif args.predict:
        result = engine.predict_evolution_trend()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.risks:
        risks = engine.identify_risks()
        print(json.dumps(risks, ensure_ascii=False, indent=2))
    elif args.strategies:
        strategies = engine.generate_preventive_strategies()
        print(json.dumps(strategies, ensure_ascii=False, indent=2))
    elif args.apply:
        result = engine.apply_preventive_strategies()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
    elif args.full_cycle:
        result = engine.run_full_cycle()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 默认显示状态
        print(engine.get_status_summary())


if __name__ == '__main__':
    main()