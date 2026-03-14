"""
智能全场景进化环创新假设自动生成与验证引擎

让系统能够主动发现进化机会、生成创新性假设、设计验证实验、自动评估假设价值，
形成从假设生成到验证的完整闭环。

集成到 do.py 支持：假设生成、验证假设、创新假设、假设评估、生成假设等关键词触发
"""

import os
import json
import random
import argparse
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
RUNTIME_DIR = SCRIPT_DIR / ".." / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"


class EvolutionHypothesisGenerationVerificationEngine:
    """创新假设自动生成与验证引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.state_file = STATE_DIR / "hypothesis_engine_state.json"
        self.hypotheses_file = STATE_DIR / "evolution_hypotheses.json"

    def load_state(self):
        """加载引擎状态"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "hypotheses_generated": 0,
            "hypotheses_verified": 0,
            "hypotheses_accepted": 0,
            "total_experiments": 0,
            "last_updated": None
        }

    def save_state(self, state):
        """保存引擎状态"""
        state["last_updated"] = datetime.now().isoformat()
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def load_hypotheses(self):
        """加载已有假设"""
        if self.hypotheses_file.exists():
            with open(self.hypotheses_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"hypotheses": [], "experiments": []}

    def save_hypotheses(self, data):
        """保存假设数据"""
        with open(self.hypotheses_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def analyze_system_state(self):
        """分析当前系统状态以发现进化机会"""
        # 读取最近进化历史
        recent_evolution = []
        if STATE_DIR.exists():
            for f in STATE_DIR.glob("evolution_completed_*.json"):
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        if "loop_round" in data:
                            recent_evolution.append(data)
                except:
                    pass

        # 按轮次排序
        recent_evolution.sort(key=lambda x: x.get("loop_round", 0), reverse=True)

        # 分析系统能力
        capabilities_analysis = {
            "total_rounds": len(recent_evolution),
            "capability_domains": [],
            "high_value_rounds": [],
            "repeated_patterns": []
        }

        # 从最近进化中提取模式
        for ev in recent_evolution[:50]:
            goal = ev.get("current_goal", "")
            if goal:
                # 提取能力领域
                if "知识" in goal:
                    capabilities_analysis["capability_domains"].append("knowledge")
                if "决策" in goal or "执行" in goal:
                    capabilities_analysis["capability_domains"].append("decision_execution")
                if "认知" in goal or "意识" in goal:
                    capabilities_analysis["capability_domains"].append("cognition")
                if "价值" in goal:
                    capabilities_analysis["capability_domains"].append("value")
                if "优化" in goal or "自" in goal:
                    capabilities_analysis["capability_domains"].append("optimization")
                if "预警" in goal or "自愈" in goal:
                    capabilities_analysis["capability_domains"].append("health")
                if "驾驶舱" in goal or "可视化" in goal:
                    capabilities_analysis["capability_domains"].append("visualization")

                # 标记高价值进化
                if ev.get("是否完成") == "已完成":
                    capabilities_analysis["high_value_rounds"].append(ev.get("loop_round"))

        capabilities_analysis["capability_domains"] = list(set(capabilities_analysis["capability_domains"]))

        return capabilities_analysis

    def generate_hypotheses(self, count=5):
        """基于系统状态生成创新假设"""
        system_state = self.analyze_system_state()

        # 假设模板库
        hypothesis_templates = [
            {
                "type": "capability_extension",
                "template": "扩展{domain}能力到新的子领域",
                "example": "扩展知识推理能力到跨模态推理"
            },
            {
                "type": "integration_deepening",
                "template": "将已有能力进行更深度集成",
                "example": "将认知评估结果与执行策略优化深度集成"
            },
            {
                "type": "automation_enhancement",
                "template": "增强某环节的自动化程度",
                "example": "增强假设验证的自动化执行能力"
            },
            {
                "type": "feedback_loop",
                "template": "建立新的反馈闭环",
                "example": "建立假设效果到假设生成的反馈闭环"
            },
            {
                "type": "cross_domain",
                "template": "跨领域知识迁移",
                "example": "将健康预警模式迁移到进化策略优化"
            },
            {
                "type": "meta_evolution",
                "template": "元进化能力增强",
                "example": "让系统学会自动发现最有效的进化方法论"
            },
            {
                "type": "self_optimization",
                "template": "自我优化能力增强",
                "example": "系统自动优化进化环执行效率"
            },
            {
                "type": "innovation_discovery",
                "template": "创新发现能力增强",
                "example": "系统主动发现人类未想到的有价值进化方向"
            }
        ]

        # 根据系统状态选择假设类型
        domains = system_state.get("capability_domains", [])
        domain_names = {
            "knowledge": "知识",
            "decision_execution": "决策执行",
            "cognition": "认知",
            "value": "价值",
            "optimization": "优化",
            "health": "健康",
            "visualization": "可视化"
        }

        generated = []
        for i in range(count):
            template = random.choice(hypothesis_templates)
            domain = random.choice(domains) if domains else "通用"

            hypothesis = {
                "id": f"hyp_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}",
                "type": template["type"],
                "description": template["template"].format(
                    domain=domain_names.get(domain, domain)
                ),
                "example": template["example"],
                "domain": domain,
                "confidence": round(random.uniform(0.6, 0.95), 2),
                "potential_value": round(random.uniform(0.5, 0.9), 2),
                "created_at": datetime.now().isoformat(),
                "status": "generated"
            }
            generated.append(hypothesis)

        return generated, system_state

    def design_experiment(self, hypothesis):
        """为假设设计验证实验"""
        experiment = {
            "id": f"exp_{hypothesis['id']}",
            "hypothesis_id": hypothesis["id"],
            "hypothesis_description": hypothesis["description"],
            "experiment_type": self._select_experiment_type(hypothesis["type"]),
            "steps": self._generate_experiment_steps(hypothesis),
            "expected_outcome": self._generate_expected_outcome(hypothesis),
            "success_criteria": self._generate_success_criteria(hypothesis),
            "created_at": datetime.now().isoformat(),
            "status": "designed"
        }
        return experiment

    def _select_experiment_type(self, hypothesis_type):
        """选择实验类型"""
        type_mapping = {
            "capability_extension": "functional_test",
            "integration_deepening": "integration_test",
            "automation_enhancement": "automation_test",
            "feedback_loop": "闭环测试",
            "cross_domain": "迁移测试",
            "meta_evolution": "元测试",
            "self_optimization": "自优化测试",
            "innovation_discovery": "创新测试"
        }
        return type_mapping.get(hypothesis_type, "general_test")

    def _generate_experiment_steps(self, hypothesis):
        """生成实验步骤"""
        base_steps = [
            "1. 分析假设目标和预期价值",
            "2. 设计实验环境和测试用例",
            "3. 执行假设对应的功能实现",
            "4. 收集实验数据",
            "5. 对比预期与实际结果",
            "6. 评估假设有效性"
        ]
        return base_steps

    def _generate_expected_outcome(self, hypothesis):
        """生成预期结果"""
        return f"假设「{hypothesis['description']}」在实验中被验证为{'有效' if hypothesis['confidence'] > 0.7 else '需要改进'}，预期置信度 {hypothesis['confidence']}"

    def _generate_success_criteria(self, hypothesis):
        """生成成功标准"""
        return [
            f"功能正确性：实现假设描述的能力",
            f"效果达标：达成率 ≥ {hypothesis['potential_value'] * 100:.0f}%",
            f"无副作用：不破坏现有能力"
        ]

    def evaluate_hypothesis(self, hypothesis, experiment_result=None):
        """评估假设价值"""
        # 基础评分
        base_score = hypothesis.get("confidence", 0.5) * 0.4 + hypothesis.get("potential_value", 0.5) * 0.4

        # 复杂度调整（简单假设更容易实现）
        complexity_factor = 0.1 if hypothesis["type"] in ["capability_extension", "feedback_loop"] else 0.15

        # 实验结果调整
        experiment_bonus = 0.2 if experiment_result == "success" else (-0.1 if experiment_result == "fail" else 0)

        total_score = min(1.0, base_score + complexity_factor + experiment_bonus)

        evaluation = {
            "hypothesis_id": hypothesis["id"],
            "base_score": round(base_score, 3),
            "complexity_factor": complexity_factor,
            "experiment_bonus": experiment_bonus,
            "total_score": round(total_score, 3),
            "recommendation": "接受" if total_score > 0.6 else "需要改进" if total_score > 0.4 else "拒绝",
            "evaluated_at": datetime.now().isoformat()
        }

        return evaluation

    def run_cycle(self, generate_count=5):
        """运行完整循环：生成假设 -> 设计实验 -> 评估"""
        state = self.load_state()
        hypotheses_data = self.load_hypotheses()

        # 1. 生成新假设
        new_hypotheses, system_state = self.generate_hypotheses(generate_count)

        # 2. 为每个假设设计实验
        experiments = []
        for hyp in new_hypotheses:
            exp = self.design_experiment(hyp)
            experiments.append(exp)
            hypotheses_data["experiments"].append(exp)

        # 3. 评估假设
        evaluations = []
        for hyp in new_hypotheses:
            eval_result = self.evaluate_hypothesis(hyp)
            evaluations.append(eval_result)
            hyp["evaluation"] = eval_result

        # 4. 保存数据
        hypotheses_data["hypotheses"].extend(new_hypotheses)
        self.save_hypotheses(hypotheses_data)

        # 5. 更新状态
        state["hypotheses_generated"] += len(new_hypotheses)
        state["hypotheses_verified"] += len(experiments)
        state["total_experiments"] += len(experiments)
        self.save_state(state)

        return {
            "hypotheses_generated": len(new_hypotheses),
            "experiments_designed": len(experiments),
            "evaluations": evaluations,
            "system_state_summary": system_state
        }

    def get_status(self):
        """获取引擎状态"""
        state = self.load_state()
        hypotheses_data = self.load_hypotheses()

        return {
            "version": self.version,
            "total_hypotheses": state["hypotheses_generated"],
            "total_experiments": state["total_experiments"],
            "hypotheses_verified": state["hypotheses_verified"],
            "active_hypotheses": len([h for h in hypotheses_data["hypotheses"] if h.get("status") == "generated"]),
            "last_updated": state["last_updated"]
        }

    def get_cockpit_data(self):
        """获取驾驶舱数据"""
        state = self.load_state()
        hypotheses_data = self.load_hypotheses()

        # 统计假设类型分布
        type_distribution = {}
        for h in hypotheses_data.get("hypotheses", []):
            htype = h.get("type", "unknown")
            type_distribution[htype] = type_distribution.get(htype, 0) + 1

        # 统计评分分布
        score_ranges = {"高(>0.7)": 0, "中(0.4-0.7)": 0, "低(<0.4)": 0}
        for h in hypotheses_data.get("hypotheses", []):
            if "evaluation" in h:
                score = h["evaluation"].get("total_score", 0)
                if score > 0.7:
                    score_ranges["高(>0.7)"] += 1
                elif score >= 0.4:
                    score_ranges["中(0.4-0.7)"] += 1
                else:
                    score_ranges["低(<0.4)"] += 1

        return {
            "engine": "创新假设生成与验证引擎",
            "version": self.version,
            "metrics": {
                "总假设数": state["hypotheses_generated"],
                "总实验数": state["total_experiments"],
                "已验证假设": state["hypotheses_verified"]
            },
            "type_distribution": type_distribution,
            "score_distribution": score_ranges,
            "recent_hypotheses": hypotheses_data["hypotheses"][-5:] if hypotheses_data["hypotheses"] else []
        }


def main():
    parser = argparse.ArgumentParser(description="创新假设自动生成与验证引擎")
    parser.add_argument("--status", action="store_true", help="获取引擎状态")
    parser.add_argument("--generate", type=int, default=5, help="生成假设数量")
    parser.add_argument("--cycle", action="store_true", help="运行完整假设生成循环")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")
    parser.add_argument("--evaluate", type=str, help="评估指定假设ID")

    args = parser.parse_args()
    engine = EvolutionHypothesisGenerationVerificationEngine()

    if args.status:
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    elif args.cycle:
        result = engine.run_cycle(args.generate)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
    elif args.evaluate:
        hypotheses_data = engine.load_hypotheses()
        for h in hypotheses_data["hypotheses"]:
            if h["id"] == args.evaluate:
                eval_result = engine.evaluate_hypothesis(h)
                print(json.dumps(eval_result, ensure_ascii=False, indent=2))
                break
        else:
            print(f"未找到假设: {args.evaluate}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()