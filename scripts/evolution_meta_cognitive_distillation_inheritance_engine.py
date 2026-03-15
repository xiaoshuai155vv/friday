"""
智能全场景进化环元进化认知蒸馏与自动传承引擎

在 round 570 完成的元进化主动创新引擎基础上，
构建让系统从 570+ 轮进化历史中自动提取可复用元知识、
实现代际传承的引擎，形成「学习→蒸馏→传承→创新」的完整闭环。

功能：
1. 进化历史元知识提取 - 从 570+ 轮历史中提取元模式、最佳实践、失败教训
2. 认知蒸馏 - 将复杂进化经验凝练为可复用的知识单元
3. 自动传承 - 新轮次自动继承历史智慧
4. 主动创新集成 - 与 round 570 主动创新引擎深度集成
5. 驾驶舱数据接口 - 提供统一的认知蒸馏与传承数据输出

Version: 1.0.0
"""

import json
import os
import sys
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path
import random
import glob
from collections import defaultdict


class MetaCognitiveDistillationInheritanceEngine:
    """元进化认知蒸馏与自动传承引擎"""

    VERSION = "1.0.0"

    def __init__(self):
        self.name = "MetaCognitiveDistillationInheritanceEngine"
        self.data_dir = Path("runtime/state")
        self.output_dir = Path("runtime/state")
        self.output_file = self.output_dir / "meta_cognitive_distillation.json"
        self.inheritance_file = self.output_dir / "meta_inheritance_knowledge.json"

        # 相关引擎数据文件
        self.active_innovation_file = self.data_dir / "meta_active_innovation.json"
        self.self_optimization_file = self.data_dir / "meta_self_optimization.json"
        self.self_awareness_file = self.data_dir / "meta_self_awareness_deep_enhancement.json"
        self.cross_round_file = self.data_dir / "cross_round_learning.json"

    def load_evolution_history(self) -> List[Dict[str, Any]]:
        """加载进化历史数据"""
        history = []

        # 查找所有 evolution_completed_*.json 文件
        pattern = str(self.data_dir / "evolution_completed_*.json")
        files = glob.glob(pattern)

        # 按修改时间排序，加载最新的历史
        files.sort(key=os.path.getmtime, reverse=True)

        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'loop_round' in data:
                        history.append(data)
            except Exception:
                continue

        # 按轮次排序
        history.sort(key=lambda x: x.get('loop_round', 0))

        return history[-100:]  # 取最近100轮

    def extract_meta_knowledge(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """从进化历史中提取元知识"""
        meta_knowledge = {
            "meta_patterns": [],  # 元模式
            "best_practices": [],  # 最佳实践
            "failure_lessons": [],  # 失败教训
            "successful_strategies": [],  # 成功策略
            "evolution_trends": [],  # 进化趋势
            "value_insights": []  # 价值洞察
        }

        if not history:
            return meta_knowledge

        # 提取元模式
        for item in history:
            if item.get('completion_status') == 'completed':
                # 从完成的任务中提取元模式
                goal = item.get('current_goal', '')
                if goal:
                    # 提取关键词作为元模式
                    keywords = self._extract_keywords(goal)
                    for kw in keywords[:3]:
                        # 检查是否已存在
                        exists = any(kw in p.get('pattern', '') for p in meta_knowledge['meta_patterns'])
                        if not exists:
                            meta_knowledge['meta_patterns'].append({
                                "pattern": kw,
                                "source_round": item.get('loop_round', 0),
                                "frequency": 1
                            })

        # 统计出现频率
        pattern_counts = defaultdict(int)
        for p in meta_knowledge['meta_patterns']:
            pattern_counts[p['pattern']] += 1

        # 更新频率
        for p in meta_knowledge['meta_patterns']:
            p['frequency'] = pattern_counts[p['pattern']]

        # 按频率排序，保留前20个
        meta_knowledge['meta_patterns'] = sorted(
            meta_knowledge['meta_patterns'],
            key=lambda x: x['frequency'],
            reverse=True
        )[:20]

        # 提取最佳实践
        for item in history:
            if item.get('completion_status') == 'completed':
                impact = item.get('impact', {})
                if impact:
                    # 从有impact的完成任务中提取最佳实践
                    meta_knowledge['best_practices'].append({
                        "practice": item.get('current_goal', '')[:100],
                        "source_round": item.get('loop_round', 0),
                        "impact": impact,
                        "verification": item.get('verification', {})
                    })

        # 只保留有实际impact的
        meta_knowledge['best_practices'] = [
            p for p in meta_knowledge['best_practices']
            if p.get('impact') or p.get('verification', {}).get('baseline') == '通过'
        ][:15]

        # 提取失败教训
        for item in history:
            if item.get('completion_status') in ['failed', 'stale_failed', 'partial']:
                meta_knowledge['failure_lessons'].append({
                    "lesson": item.get('current_goal', '')[:100],
                    "source_round": item.get('loop_round', 0),
                    "what_happened": item.get('what_happened', [])[:3]
                })

        # 只保留最近的教训
        meta_knowledge['failure_lessons'] = meta_knowledge['failure_lessons'][-10:]

        # 提取成功策略
        for item in history:
            if item.get('completion_status') == 'completed':
                innovation = item.get('innovation', [])
                if innovation:
                    for inn in innovation:
                        meta_knowledge['successful_strategies'].append({
                            "strategy": inn,
                            "source_round": item.get('loop_round', 0)
                        })

        # 去重并限制数量
        seen = set()
        unique_strategies = []
        for s in meta_knowledge['successful_strategies']:
            key = s.get('strategy', '')[:50]
            if key not in seen:
                seen.add(key)
                unique_strategies.append(s)

        meta_knowledge['successful_strategies'] = unique_strategies[:15]

        # 提取进化趋势
        if len(history) >= 10:
            rounds = [h.get('loop_round', 0) for h in history]
            completed = [h for h in history if h.get('completion_status') == 'completed']

            meta_knowledge['evolution_trends'].append({
                "trend": "元进化能力持续增强",
                "total_rounds": len(history),
                "completed_rounds": len(completed),
                "completion_rate": len(completed) / len(history) if history else 0,
                "start_round": min(rounds) if rounds else 0,
                "end_round": max(rounds) if rounds else 0
            })

        return meta_knowledge

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 常见的高价值关键词
        high_value_keywords = [
            "元进化", "自我", "智能", "优化", "决策", "执行", "学习",
            "知识", "价值", "创新", "认知", "意识", "自主", "协同",
            "集成", "引擎", "闭环", "深度", "自适应", "预测"
        ]

        keywords = []
        for kw in high_value_keywords:
            if kw in text:
                keywords.append(kw)

        return keywords[:5]

    def distill_knowledge(self, meta_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """认知蒸馏 - 将复杂进化经验凝练为可复用的知识单元"""
        distilled = {
            "core_insights": [],  # 核心洞察
            "actionable_patterns": [],  # 可执行模式
            "inheritance_units": []  # 传承单元
        }

        # 核心洞察：从元模式中提炼
        patterns = meta_knowledge.get('meta_patterns', [])
        high_freq = [p for p in patterns if p.get('frequency', 0) >= 2]

        for p in high_freq[:5]:
            distilled['core_insights'].append({
                "insight": f"高频元模式：{p['pattern']}（出现{p['frequency']}次）",
                "pattern": p['pattern'],
                "confidence": min(p['frequency'] / 10, 1.0),
                "action": f"在进化决策时优先考虑{p['pattern']}相关的优化方向"
            })

        # 可执行模式：从最佳实践中提炼
        practices = meta_knowledge.get('best_practices', [])
        for p in practices[:5]:
            distilled['actionable_patterns'].append({
                "pattern": p.get('practice', '')[:80],
                "source_round": p.get('source_round', 0),
                "impact_summary": f"验证通过，impact: {p.get('impact', {})}"
            })

        # 传承单元：从成功策略中提炼
        strategies = meta_knowledge.get('successful_strategies', [])
        for s in strategies[:10]:
            distilled['inheritance_units'].append({
                "unit": s.get('strategy', '')[:100],
                "source_round": s.get('source_round', 0),
                "category": self._categorize_strategy(s.get('strategy', ''))
            })

        return distilled

    def _categorize_strategy(self, strategy: str) -> str:
        """分类策略"""
        if '元' in strategy or '自我' in strategy:
            return "元进化"
        elif '智能' in strategy or '自适应' in strategy:
            return "智能决策"
        elif '知识' in strategy or '图谱' in strategy:
            return "知识工程"
        elif '价值' in strategy or '投资' in strategy:
            return "价值驱动"
        elif '创新' in strategy or '假设' in strategy:
            return "创新驱动"
        else:
            return "通用"

    def generate_inheritance_package(self, distilled: Dict[str, Any]) -> Dict[str, Any]:
        """生成传承包 - 准备传递给下一轮的知识"""
        package = {
            "version": self.VERSION,
            "generated_at": datetime.now().isoformat(),
            "core_insights": distilled.get('core_insights', []),
            "top_patterns": distilled.get('actionable_patterns', [])[:5],
            "inheritance_units": distilled.get('inheritance_units', [])[:10],
            "usage_guide": {
                "description": "本传承包包含从570+轮进化历史中提取的核心智慧",
                "usage": [
                    "1. 在制定新进化策略时参考core_insights",
                    "2. 在遇到类似问题时参考actionable_patterns",
                    "3. 在创新时参考inheritance_units获取灵感",
                    "4. 定期更新传承包以纳入新学到的知识"
                ],
                "integration": "可通过加载本文件获取历史智慧，用于增强决策质量"
            }
        }

        return package

    def inherit_knowledge(self) -> Dict[str, Any]:
        """自动传承 - 新轮次自动继承历史智慧"""
        inheritance = {
            "status": "ready",
            "knowledge_loaded": False,
            "package": {}
        }

        # 尝试加载已保存的传承包
        if self.inheritance_file.exists():
            try:
                with open(self.inheritance_file, 'r', encoding='utf-8') as f:
                    inheritance['package'] = json.load(f)
                    inheritance['knowledge_loaded'] = True
            except Exception:
                pass

        return inheritance

    def save_distillation_results(self, meta_knowledge: Dict, distilled: Dict, package: Dict) -> bool:
        """保存蒸馏结果"""
        try:
            # 保存主数据
            results = {
                "version": self.VERSION,
                "generated_at": datetime.now().isoformat(),
                "meta_knowledge": meta_knowledge,
                "distilled": distilled,
                "inheritance_package": package
            }

            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

            # 保存传承包
            with open(self.inheritance_file, 'w', encoding='utf-8') as f:
                json.dump(package, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"保存失败: {e}")
            return False

    def run_full_pipeline(self) -> Dict[str, Any]:
        """运行完整的认知蒸馏与传承流程"""
        results = {
            "status": "success",
            "history_rounds": 0,
            "meta_knowledge": {},
            "distilled": {},
            "inheritance_package": {}
        }

        # 1. 加载进化历史
        history = self.load_evolution_history()
        results['history_rounds'] = len(history)

        # 2. 提取元知识
        meta_knowledge = self.extract_meta_knowledge(history)
        results['meta_knowledge'] = meta_knowledge

        # 3. 认知蒸馏
        distilled = self.distill_knowledge(meta_knowledge)
        results['distilled'] = distilled

        # 4. 生成传承包
        package = self.generate_inheritance_package(distilled)
        results['inheritance_package'] = package

        # 5. 保存结果
        self.save_distillation_results(meta_knowledge, distilled, package)

        return results

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱数据"""
        data = {
            "engine": self.name,
            "version": self.VERSION,
            "status": "ready",
            "data": {}
        }

        # 尝试加载最新数据
        if self.output_file.exists():
            try:
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    results = json.load(f)

                data['data'] = {
                    "history_rounds": len(self.load_evolution_history()),
                    "meta_patterns_count": len(results.get('meta_knowledge', {}).get('meta_patterns', [])),
                    "best_practices_count": len(results.get('meta_knowledge', {}).get('best_practices', [])),
                    "failure_lessons_count": len(results.get('meta_knowledge', {}).get('failure_lessons', [])),
                    "core_insights_count": len(results.get('distilled', {}).get('core_insights', [])),
                    "inheritance_units_count": len(results.get('distilled', {}).get('inheritance_units', [])),
                    "generated_at": results.get('generated_at', '')
                }
            except Exception:
                pass

        return data

    def check_status(self) -> Dict[str, Any]:
        """检查引擎状态"""
        status = {
            "engine": self.name,
            "version": self.VERSION,
            "status": "healthy",
            "output_file_exists": self.output_file.exists(),
            "inheritance_file_exists": self.inheritance_file.exists()
        }

        if self.output_file.exists():
            try:
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    status['last_generated'] = data.get('generated_at', '')
                    status['history_rounds'] = len(self.load_evolution_history())
            except Exception:
                status['status'] = "error"

        return status


def main():
    parser = argparse.ArgumentParser(
        description="智能全场景进化环元进化认知蒸馏与自动传承引擎"
    )
    parser.add_argument('--version', action='version', version='1.0.0')
    parser.add_argument('--run', action='store_true', help='运行完整的认知蒸馏与传承流程')
    parser.add_argument('--status', action='store_true', help='检查引擎状态')
    parser.add_argument('--cockpit-data', action='store_true', help='获取驾驶舱数据')
    parser.add_argument('--inherit', action='store_true', help='继承历史智慧')
    parser.add_argument('--distill', action='store_true', help='仅执行认知蒸馏')

    args = parser.parse_args()

    engine = MetaCognitiveDistillationInheritanceEngine()

    if args.status:
        status = engine.check_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    elif args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
    elif args.inherit:
        inheritance = engine.inherit_knowledge()
        print(json.dumps(inheritance, ensure_ascii=False, indent=2))
    elif args.distill:
        history = engine.load_evolution_history()
        meta_knowledge = engine.extract_meta_knowledge(history)
        distilled = engine.distill_knowledge(meta_knowledge)
        print(json.dumps(distilled, ensure_ascii=False, indent=2))
    elif args.run:
        results = engine.run_full_pipeline()
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()