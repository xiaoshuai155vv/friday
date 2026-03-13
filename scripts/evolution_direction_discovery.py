#!/usr/bin/env python3
"""
智能进化方向自动发现与优先级排序引擎（Evolution Direction Discovery Engine）
version 1.0.0

让系统能够主动发现进化机会（基于系统状态、能力缺口、进化历史），自动评估价值并排序优先级，
生成可执行进化计划，实现真正的自主进化方向发现。

功能：
1. 多维度进化机会分析（系统状态、能力缺口、进化历史、用户场景模拟）
2. 自动价值评估与优先级排序
3. 进化计划生成
4. 与进化决策引擎深度集成

依赖：
- evolution_adaptive_optimizer.py (round 237)
- evolution_iteration_coordination.py (round 238)
- cross_engine_learning_engine.py (round 212)
- evolution_prediction_planner.py (round 217)
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class EvolutionDirectionDiscovery:
    """智能进化方向自动发现与优先级排序引擎"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.runtime_dir = self.project_root / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.references_dir = self.project_root / "references"

        # 读取各类输入数据
        self.capability_gaps = self._load_capability_gaps()
        self.failures = self._load_failures()
        self.capabilities = self._load_capabilities()
        self.evolution_history = self._load_evolution_history()
        self.current_state = self._load_current_state()

    def _load_capability_gaps(self) -> List[Dict]:
        """加载能力缺口"""
        gaps_file = self.references_dir / "capability_gaps.md"
        gaps = []
        if gaps_file.exists():
            content = gaps_file.read_text(encoding='utf-8')
            # 解析 markdown 表格
            lines = content.split('\n')
            for line in lines:
                if '|' in line and '---' not in line and '类别' not in line:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 3 and parts[2] and parts[2] != '—':
                        gaps.append({
                            "category": parts[1],
                            "direction": parts[2]
                        })
        return gaps

    def _load_failures(self) -> List[Dict]:
        """加载历史失败教训"""
        failures_file = self.references_dir / "failures.md"
        failures = []
        if failures_file.exists():
            content = failures_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            for line in lines:
                if '20' in line and '：' in line:
                    # 提取日期和描述
                    try:
                        date_part = line.split('：')[0].strip().replace('- ', '')
                        desc_part = '：'.join(line.split('：')[1:]).strip()
                        if desc_part:
                            failures.append({
                                "date": date_part,
                                "description": desc_part
                            })
                    except:
                        pass
        return failures

    def _load_capabilities(self) -> Dict:
        """加载已有能力"""
        caps_file = self.references_dir / "capabilities.md"
        capabilities = {}
        if caps_file.exists():
            try:
                content = caps_file.read_text(encoding='utf-8')
                # 尝试加载 JSON 格式的能力列表
                # 这里简化处理，实际可以解析 markdown 表格
                return {"loaded": True, "count": len(content.split('\n'))}
            except:
                pass
        return capabilities

    def _load_evolution_history(self) -> List[Dict]:
        """加载进化历史"""
        history = []
        state_dir = self.state_dir
        if state_dir.exists():
            # 读取最近的进化完成记录
            for f in state_dir.glob("evolution_completed_*.json"):
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        history.append(data)
                except:
                    pass
        # 按轮次排序
        history.sort(key=lambda x: x.get('loop_round', 0), reverse=True)
        return history[:30]  # 只取最近30轮

    def _load_current_state(self) -> Dict:
        """加载当前系统状态"""
        mission_file = self.state_dir / "current_mission.json"
        if mission_file.exists():
            with open(mission_file, 'r', encoding='utf-8') as fp:
                return json.load(fp)
        return {}

    def analyze_opportunities(self) -> List[Dict[str, Any]]:
        """
        分析多维度进化机会
        返回：进化机会列表，每个包含机会描述、来源、潜在价值
        """
        opportunities = []

        # 1. 基于能力缺口分析
        for gap in self.capability_gaps:
            if gap.get('direction') and gap['direction'] != '—':
                opportunities.append({
                    "id": f"gap_{len(opportunities) + 1}",
                    "opportunity": f"补齐{gap['category']}能力缺口：{gap['direction']}",
                    "source": "capability_gaps",
                    "category": gap.get('category', 'unknown'),
                    "potential_value": 7.0,
                    "feasibility": 8.0,
                    "urgency": 6.0
                })

        # 2. 基于历史失败教训分析
        for failure in self.failures[-10:]:  # 最近10条失败
            desc = failure.get('description', '')
            if '下次' in desc:
                # 提取"下次如何避免"
                improvement = desc.split('下次：')[1].strip() if '下次：' in desc else ''
                opportunities.append({
                    "id": f"failure_{len(opportunities) + 1}",
                    "opportunity": f"基于失败教训改进：{improvement}",
                    "source": "failures",
                    "category": "system_improvement",
                    "potential_value": 8.0,
                    "feasibility": 9.0,
                    "urgency": 7.0
                })

        # 3. 基于进化历史趋势分析
        if len(self.evolution_history) >= 5:
            # 分析最近的进化模式
            recent_rounds = [h.get('current_goal', '') for h in self.evolution_history[:5]]

            # 检测重复领域
            domains = {}
            for goal in recent_rounds:
                for domain in ['engine', '引擎', '协同', '学习', '预测', '优化', '自动', '智能']:
                    if domain in goal:
                        domains[domain] = domains.get(domain, 0) + 1

            # 找出较少涉及的领域
            all_domains = ['engine', '引擎', '协同', '学习', '预测', '优化', '自动', '智能', '发现', '评估', '诊断']
            for domain in all_domains:
                if domains.get(domain, 0) == 0:
                    opportunities.append({
                        "id": f"trend_{len(opportunities) + 1}",
                        "opportunity": f"探索新进化方向：{domain}相关能力增强",
                        "source": "evolution_history",
                        "category": domain,
                        "potential_value": 7.5,
                        "feasibility": 8.0,
                        "urgency": 5.0
                    })

        # 4. 基于当前系统状态分析
        current_phase = self.current_state.get('phase', 'unknown')
        current_goal = self.current_state.get('current_goal', '')

        if current_goal and 'TBD' not in current_goal:
            opportunities.append({
                "id": "current_enhancement",
                "opportunity": f"深化当前进化方向：{current_goal}",
                "source": "current_state",
                "category": "continuation",
                "potential_value": 9.0,
                "feasibility": 9.0,
                "urgency": 8.0
            })

        # 5. 基于 LLM 特有优势的前沿探索
        frontier_opportunities = [
            {
                "id": "frontier_1",
                "opportunity": "跨引擎深度协同优化：让多个引擎能够共享学习成果，形成更紧密的协同闭环",
                "source": "frontier_exploration",
                "category": "collaboration",
                "potential_value": 8.5,
                "feasibility": 7.0,
                "urgency": 6.0
            },
            {
                "id": "frontier_2",
                "opportunity": "进化环自我诊断与自愈：让进化环能够自动检测自身问题并尝试修复",
                "source": "frontier_exploration",
                "category": "self_healing",
                "potential_value": 9.0,
                "feasibility": 6.5,
                "urgency": 7.0
            },
            {
                "id": "frontier_3",
                "opportunity": "用户行为驱动的自适应进化：根据用户实际使用模式动态调整进化方向",
                "source": "frontier_exploration",
                "category": "adaptation",
                "potential_value": 8.0,
                "feasibility": 7.5,
                "urgency": 6.5
            }
        ]
        opportunities.extend(frontier_opportunities)

        return opportunities

    def evaluate_opportunity(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """
        评估单个进化机会的价值
        返回：包含价值评分的详细信息
        """
        # 计算综合评分
        potential = opportunity.get('potential_value', 5.0)
        feasibility = opportunity.get('feasibility', 5.0)
        urgency = opportunity.get('urgency', 5.0)

        # 加权综合评分
        overall_score = (potential * 0.4 + feasibility * 0.35 + urgency * 0.25)

        opportunity['overall_score'] = round(overall_score, 2)
        opportunity['evaluated_at'] = datetime.now().isoformat()

        return opportunity

    def rank_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        对进化机会进行优先级排序
        返回：按优先级排序的机会列表
        """
        # 先评估每个机会
        evaluated = [self.evaluate_opportunity(op) for op in opportunities]

        # 按综合评分排序
        ranked = sorted(evaluated, key=lambda x: x.get('overall_score', 0), reverse=True)

        # 添加排名
        for i, op in enumerate(ranked):
            op['rank'] = i + 1

        return ranked

    def generate_evolution_plan(self, top_n: int = 3) -> Dict[str, Any]:
        """
        生成进化计划
        top_n: 选取前 N 个最高优先级的机会
        """
        opportunities = self.analyze_opportunities()
        ranked = self.rank_opportunities(opportunities)

        # 选取前 N 个
        selected = ranked[:top_n]

        # 生成计划
        plan = {
            "plan_id": f"evo_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "round": self.current_state.get('loop_round', 239),
            "opportunities": selected,
            "recommended_focus": selected[0] if selected else None,
            "execution_recommendations": []
        }

        # 为每个选中的机会生成执行建议
        for i, opp in enumerate(selected):
            recommendation = {
                "priority": i + 1,
                "direction": opp.get('opportunity', ''),
                "category": opp.get('category', ''),
                "score": opp.get('overall_score', 0),
                "rationale": f"综合评分{opp.get('overall_score', 0)}，潜力{opp.get('potential_value')}，可行性{opp.get('feasibility')}，紧急度{opp.get('urgency')}",
                "suggested_actions": self._generate_actions(opp)
            }
            plan["execution_recommendations"].append(recommendation)

        return plan

    def _generate_actions(self, opportunity: Dict) -> List[str]:
        """为机会生成具体的行动建议"""
        category = opportunity.get('category', '')
        source = opportunity.get('source', '')

        actions = []

        if category == 'continuation':
            actions = [
                "深入分析当前进化方向的实现细节",
                "识别可进一步优化的点",
                "增强与其他引擎的集成"
            ]
        elif category == 'collaboration':
            actions = [
                "创建跨引擎协同接口",
                "实现引擎间状态共享机制",
                "添加闭环触发链"
            ]
        elif category == 'self_healing':
            actions = [
                "实现进化环自诊断功能",
                "添加问题自动检测与修复",
                "建立自愈反馈机制"
            ]
        elif category == 'adaptation':
            actions = [
                "收集用户行为数据",
                "分析使用模式",
                "实现自适应进化策略"
            ]
        else:
            actions = [
                "分析该方向的可行性",
                "设计实现方案",
                "逐步实现并测试"
            ]

        return actions

    def get_discovery_report(self) -> Dict[str, Any]:
        """
        获取完整的发现报告
        """
        opportunities = self.analyze_opportunities()
        ranked = self.rank_opportunities(opportunities)
        plan = self.generate_evolution_plan(3)

        return {
            "report_id": f"discovery_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_opportunities": len(opportunities),
                "sources_analyzed": ["capability_gaps", "failures", "evolution_history", "current_state", "frontier_exploration"],
                "top_priority": ranked[0].get('opportunity', 'N/A') if ranked else 'N/A',
                "top_score": ranked[0].get('overall_score', 0) if ranked else 0
            },
            "ranked_opportunities": ranked,
            "evolution_plan": plan,
            "recommendations": {
                "primary": ranked[0].get('opportunity', 'N/A') if ranked else '继续深化现有能力',
                "rationale": "基于多维度分析得出的最高优先级进化方向"
            }
        }


def main():
    """主函数，支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description='智能进化方向自动发现与优先级排序引擎')
    parser.add_argument('command', choices=['analyze', 'rank', 'plan', 'report'],
                        help='要执行的命令')
    parser.add_argument('--top', type=int, default=3, help='计划中选取的top机会数')

    args = parser.parse_args()

    engine = EvolutionDirectionDiscovery()

    if args.command == 'analyze':
        opportunities = engine.analyze_opportunities()
        print(json.dumps({
            "status": "success",
            "count": len(opportunities),
            "opportunities": opportunities
        }, ensure_ascii=False, indent=2))

    elif args.command == 'rank':
        opportunities = engine.analyze_opportunities()
        ranked = engine.rank_opportunities(opportunities)
        print(json.dumps({
            "status": "success",
            "count": len(ranked),
            "ranked_opportunities": ranked
        }, ensure_ascii=False, indent=2))

    elif args.command == 'plan':
        plan = engine.generate_evolution_plan(args.top)
        print(json.dumps({
            "status": "success",
            "plan": plan
        }, ensure_ascii=False, indent=2))

    elif args.command == 'report':
        report = engine.get_discovery_report()
        print(json.dumps({
            "status": "success",
            "report": report
        }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()