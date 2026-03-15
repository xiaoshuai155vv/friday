#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环创新生态系统深度治理与价值最大化引擎

在 round 608-609 完成的创新投资组合优化引擎和价值预测预防优化引擎 V2 基础上，
构建完整的创新生态系统治理能力。

让系统能够从全局视角优化创新资源分配、预测创新风险、最大化创新投资回报。
系统将实现：
1. 创新资源全局优化配置 - 基于价值预测和投资回报分析全局配置资源
2. 跨领域创新协同促进 - 发现跨领域创新机会并促进协同
3. 创新风险预警与防控 - 预测创新项目风险并提供防控策略
4. 创新价值链端到端管理 - 从创意到价值实现的完整链路管理
5. 与 round 608-609 引擎深度集成

Version: 1.0.0
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import subprocess

# 项目根目录
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"
REFERENCES_DIR = PROJECT_ROOT / "references"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"


class InnovationEcosystemGovernanceEngine:
    """创新生态系统深度治理与价值最大化引擎"""

    def __init__(self):
        self.name = "创新生态系统深度治理与价值最大化引擎"
        self.version = "1.0.0"
        self.state_dir = STATE_DIR
        self.logs_dir = LOGS_DIR
        # 数据文件
        self.ecosystem_data_file = self.state_dir / "innovation_ecosystem_data.json"
        self.resource_allocation_file = self.state_dir / "innovation_resource_allocation.json"
        self.risk预警_file = self.state_dir / "innovation_risk_warnings.json"
        self.value_chain_file = self.state_dir / "innovation_value_chain.json"
        self.cross_domain_synergy_file = self.state_dir / "cross_domain_innovation_synergy.json"

    def get_version(self):
        """获取引擎版本信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": "创新生态系统深度治理与价值最大化引擎"
        }

    def load_evolution_history(self):
        """加载进化历史数据"""
        history = []
        state_files = list(self.state_dir.glob("evolution_completed_*.json"))
        # 读取最近的 100 轮进化历史
        state_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        for f in state_files[:100]:
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    goal = data.get("current_goal", "")
                    if "创新" in goal or "价值" in goal or "投资" in goal or "生态" in goal:
                        history.append({
                            "round": data.get("loop_round", 0),
                            "goal": goal,
                            "completed": data.get("completed", False),
                            "status": data.get("status", "unknown")
                        })
            except Exception as e:
                print(f"Warning: Failed to load {f}: {e}")
        return history

    def load_round608_data(self):
        """加载 round 608 创新投资组合优化引擎的数据"""
        file = self.state_dir / "innovation_portfolio_analysis.json"
        if not file.exists():
            return {}
        try:
            with open(file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load round 608 data: {e}")
            return {}

    def load_round609_data(self):
        """加载 round 609 价值预测预防优化引擎 V2 的数据"""
        file = self.state_dir / "meta_evolution_value_prediction_v2_data.json"
        if not file.exists():
            # 尝试其他可能的数据文件名
            for name in ["value_prediction_data.json", "meta_value_prediction_data.json"]:
                file = self.state_dir / name
                if file.exists():
                    with open(file, 'r', encoding='utf-8') as f:
                        return json.load(f)
            return {}
        try:
            with open(file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load round 609 data: {e}")
            return {}

    def analyze_resource_allocation(self):
        """分析当前创新资源分配状况"""
        history = self.load_evolution_history()
        round608_data = self.load_round608_data()

        # 分析各创新领域的资源分配
        allocation = {
            "timestamp": datetime.now().isoformat(),
            "total_innovations": len(history),
            "domain_distribution": {},
            "resource_efficiency": {},
            "investment_roi": {}
        }

        # 统计各创新领域的分布
        domains = {}
        for item in history:
            goal = item.get("goal", "")
            # 简单分类
            if "投资" in goal or "组合" in goal:
                domain = "创新投资"
            elif "价值" in goal or "预测" in goal:
                domain = "价值管理"
            elif "知识" in goal or "图谱" in goal:
                domain = "知识管理"
            elif "多模态" in goal or "感知" in goal:
                domain = "多模态融合"
            elif "元进化" in goal or "自省" in goal:
                domain = "元进化"
            else:
                domain = "其他创新"

            domains[domain] = domains.get(domain, 0) + 1

        allocation["domain_distribution"] = domains

        # 计算各领域的投资效率
        for domain, count in domains.items():
            if count > 0:
                allocation["resource_efficiency"][domain] = {
                    "count": count,
                    "efficiency_score": min(1.0, count / 10),  # 简化计算
                    "resource_allocation": count * 10  # 假设每个创新需要10单位资源
                }

        # 从 round 608 获取投资回报数据
        if round608_data:
            allocation["investment_roi"] = round608_data.get("roi_analysis", {})

        return allocation

    def optimize_resource_allocation(self):
        """优化创新资源全局配置"""
        allocation = self.analyze_resource_allocation()

        # 生成优化建议
        optimization = {
            "timestamp": datetime.now().isoformat(),
            "current_state": allocation,
            "optimization_recommendations": [],
            "resource_rebalancing": []
        }

        # 分析各领域的资源配置效率
        resource_eff = allocation.get("resource_efficiency", {})
        for domain, data in resource_eff.items():
            efficiency = data.get("efficiency_score", 0)
            if efficiency < 0.5:
                optimization["optimization_recommendations"].append({
                    "domain": domain,
                    "issue": f"资源效率较低 ({efficiency:.2f})",
                    "recommendation": "建议增加资源投入或优化执行策略",
                    "priority": "high" if efficiency < 0.3 else "medium"
                })
            elif efficiency > 0.8:
                optimization["optimization_recommendations"].append({
                    "domain": domain,
                    "issue": f"资源效率较高 ({efficiency:.2f})",
                    "recommendation": "可考虑将部分资源分配到其他低效率领域",
                    "priority": "low"
                })

        # 生成资源再平衡建议
        total_resources = sum(d.get("resource_allocation", 0) for d in resource_eff.values())
        if total_resources > 0:
            for domain, data in resource_eff.items():
                current = data.get("resource_allocation", 0)
                target = total_resources * 0.2  # 假设理想分配是各领域20%
                if abs(current - target) > total_resources * 0.1:  # 差异超过10%
                    optimization["resource_rebalancing"].append({
                        "domain": domain,
                        "current_allocation": current,
                        "recommended_allocation": int(target),
                        "adjustment": int(target - current)
                    })

        return optimization

    def discover_cross_domain_synergy(self):
        """发现跨领域创新协同机会"""
        history = self.load_evolution_history()

        # 构建创新领域关系图
        synergy = {
            "timestamp": datetime.now().isoformat(),
            "domain_relationships": [],
            "synergy_opportunities": [],
            "collaboration_recommendations": []
        }

        # 分析领域间的关系
        domains = {}
        for item in history:
            goal = item.get("goal", "")
            # 提取关键词
            keywords = []
            if "价值" in goal or "预测" in goal:
                keywords.append("价值管理")
            if "投资" in goal or "组合" in goal:
                keywords.append("创新投资")
            if "知识" in goal or "图谱" in goal:
                keywords.append("知识管理")
            if "多模态" in goal or "感知" in goal:
                keywords.append("多模态融合")
            if "元进化" in goal or "自省" in goal:
                keywords.append("元进化")
            if "策略" in goal or "决策" in goal:
                keywords.append("策略决策")

            for kw in keywords:
                domains[kw] = domains.get(kw, 0) + 1

        # 发现协同机会
        domain_list = list(domains.keys())
        for i, d1 in enumerate(domain_list):
            for d2 in domain_list[i+1:]:
                synergy["domain_relationships"].append({
                    "domain_a": d1,
                    "domain_b": d2,
                    "combined_count": domains[d1] + domains[d2],
                    "synergy_potential": min(1.0, (domains[d1] + domains[d2]) / 20)
                })

        # 生成协同建议
        if len(domain_list) >= 2:
            synergy["synergy_opportunities"].append({
                "type": "跨领域协同",
                "description": f"发现 {len(domain_list)} 个创新领域，存在 {len(domain_list)*(len(domain_list)-1)//2} 个潜在协同组合",
                "recommendation": "建议优先发展高协同潜力的领域组合"
            })

        # 具体的协作建议
        if "创新投资" in domain_list and "价值管理" in domain_list:
            synergy["collaboration_recommendations"].append({
                "domains": ["创新投资", "价值管理"],
                "synergy_type": "投资-价值联动",
                "description": "创新投资应与价值管理紧密联动，确保投资决策基于价值预测"
            })

        if "元进化" in domain_list and "知识管理" in domain_list:
            synergy["collaboration_recommendations"].append({
                "domains": ["元进化", "知识管理"],
                "synergy_type": "自省-知识联动",
                "description": "元进化方法论自省应与知识图谱结合，形成更智能的进化策略"
            })

        return synergy

    def predict_innovation_risks(self):
        """预测创新项目风险并提供防控策略"""
        history = self.load_evolution_history()
        allocation = self.analyze_resource_allocation()
        round609_data = self.load_round609_data()

        risk_analysis = {
            "timestamp": datetime.now().isoformat(),
            "risk_factors": [],
            "risk_warnings": [],
            "prevention_strategies": []
        }

        # 分析风险因素
        # 1. 资源过度集中风险
        domain_dist = allocation.get("domain_distribution", {})
        if domain_dist:
            max_domain = max(domain_dist.items(), key=lambda x: x[1])
            total = sum(domain_dist.values())
            concentration = max_domain[1] / total if total > 0 else 0

            if concentration > 0.5:
                risk_analysis["risk_factors"].append({
                    "type": "资源过度集中",
                    "domain": max_domain[0],
                    "concentration": concentration,
                    "severity": "high" if concentration > 0.7 else "medium"
                })

        # 2. 创新领域覆盖不足风险
        if len(domain_dist) < 5:
            risk_analysis["risk_factors"].append({
                "type": "创新领域覆盖不足",
                "current_domains": len(domain_dist),
                "recommended_domains": 8,
                "severity": "medium"
            })

        # 3. 从 round 609 获取价值偏离预警
        if round609_data:
            anomalies = round609_data.get("anomalies", [])
            for anomaly in anomalies:
                risk_analysis["risk_warnings"].append({
                    "type": "价值偏离预警",
                    "description": anomaly.get("description", "检测到价值偏离"),
                    "severity": anomaly.get("severity", "medium"),
                    "suggested_action": "立即调整投资策略"
                })

        # 生成风险预警
        if len(history) > 0:
            # 检查最近进化是否有失败
            failed_count = sum(1 for h in history[:20] if not h.get("completed", True))
            if failed_count > 5:
                risk_analysis["risk_warnings"].append({
                    "type": "执行风险",
                    "description": f"近20轮有 {failed_count} 轮未完成",
                    "severity": "high",
                    "suggested_action": "优化执行策略，提高完成率"
                })

        # 生成预防策略
        if risk_analysis["risk_factors"] or risk_analysis["risk_warnings"]:
            risk_analysis["prevention_strategies"].append({
                "strategy": "分散投资",
                "description": "将创新资源分散到更多领域，降低单点风险",
                "priority": "high"
            })
            risk_analysis["prevention_strategies"].append({
                "strategy": "建立预警机制",
                "description": "建立实时监控和预警机制，及早发现风险",
                "priority": "high"
            })
            risk_analysis["prevention_strategies"].append({
                "strategy": "预留应急资源",
                "description": "预留10-20%的资源作为应急储备",
                "priority": "medium"
            })

        return risk_analysis

    def manage_innovation_value_chain(self):
        """管理创新价值链端到端"""
        history = self.load_evolution_history()
        round608_data = self.load_round608_data()
        round609_data = self.load_round609_data()

        value_chain = {
            "timestamp": datetime.now().isoformat(),
            "chain_stages": [],
            "stage_metrics": {},
            "optimization_opportunities": []
        }

        # 定义价值链各阶段
        stages = [
            {"name": "创意生成", "description": "从进化历史中产生创新想法"},
            {"name": "价值评估", "description": "评估创新想法的潜在价值"},
            {"name": "投资决策", "description": "决定是否投资该创新"},
            {"name": "执行实施", "description": "执行创新实现"},
            {"name": "价值验证", "description": "验证创新是否实现预期价值"},
            {"name": "知识沉淀", "description": "将经验教训沉淀到知识图谱"}
        ]

        value_chain["chain_stages"] = stages

        # 分析各阶段的执行情况
        for stage in stages:
            stage_name = stage["name"]
            # 简单匹配进化历史中的相关轮次
            matching_rounds = 0
            for item in history:
                goal = item.get("goal", "")
                if stage_name in goal:
                    matching_rounds += 1

            value_chain["stage_metrics"][stage_name] = {
                "executed_rounds": matching_rounds,
                "completion_rate": min(1.0, matching_rounds / max(1, len(history) * 0.15)),
                "health_status": "good" if matching_rounds > 5 else "needs_attention"
            }

        # 从 round 608 获取投资分析
        if round608_data:
            roi = round608_data.get("roi_analysis", {})
            if roi:
                value_chain["stage_metrics"]["投资决策"]["roi_analysis"] = roi

        # 从 round 609 获取价值预测
        if round609_data:
            predictions = round609_data.get("predictions", [])
            if predictions:
                value_chain["stage_metrics"]["价值评估"]["predictions"] = predictions[:5]

        # 发现优化机会
        for stage_name, metrics in value_chain["stage_metrics"].items():
            if metrics.get("health_status") == "needs_attention":
                value_chain["optimization_opportunities"].append({
                    "stage": stage_name,
                    "issue": "执行轮次不足",
                    "recommendation": f"加强 {stage_name} 阶段的投入"
                })

        # 识别价值链瓶颈
        stages_by_health = [(name, metrics.get("health_status", "unknown"))
                           for name, metrics in value_chain["stage_metrics"].items()]
        bottlenecks = [s for s, h in stages_by_health if h == "needs_attention"]

        if bottlenecks:
            value_chain["optimization_opportunities"].append({
                "type": "价值链瓶颈",
                "affected_stages": bottlenecks,
                "recommendation": "优先解决价值链瓶颈环节"
            })

        return value_chain

    def get_cockpit_data(self):
        """获取驾驶舱展示数据"""
        allocation = self.analyze_resource_allocation()
        optimization = self.optimize_resource_allocation()
        synergy = self.discover_cross_domain_synergy()
        risks = self.predict_innovation_risks()
        value_chain = self.manage_innovation_value_chain()

        return {
            "engine": self.get_version(),
            "timestamp": datetime.now().isoformat(),
            "resource_allocation": allocation,
            "optimization": optimization,
            "cross_domain_synergy": synergy,
            "risk_analysis": risks,
            "value_chain": value_chain,
            "summary": {
                "total_innovations": allocation.get("total_innovations", 0),
                "active_domains": len(allocation.get("domain_distribution", {})),
                "risk_level": "high" if any(r.get("severity") == "high" for r in risks.get("risk_warnings", [])) else "medium" if risks.get("risk_warnings") else "low",
                "ecosystem_health": "good" if len(risks.get("risk_warnings", [])) < 3 else "needs_attention"
            }
        }

    def run_full_analysis(self):
        """运行完整分析"""
        print("=" * 60)
        print("创新生态系统深度治理分析")
        print("=" * 60)

        # 1. 资源分配分析
        print("\n[1] 创新资源分配分析")
        allocation = self.analyze_resource_allocation()
        print(f"  - 总创新数: {allocation.get('total_innovations', 0)}")
        print(f"  - 领域分布: {allocation.get('domain_distribution', {})}")

        # 2. 资源优化建议
        print("\n[2] 资源优化建议")
        optimization = self.optimize_resource_allocation()
        for rec in optimization.get("optimization_recommendations", [])[:3]:
            print(f"  - {rec.get('domain')}: {rec.get('recommendation', '')}")

        # 3. 跨领域协同
        print("\n[3] 跨领域创新协同")
        synergy = self.discover_cross_domain_synergy()
        for rec in synergy.get("collaboration_recommendations", [])[:3]:
            print(f"  - {rec.get('synergy_type', '')}: {rec.get('description', '')}")

        # 4. 风险预警
        print("\n[4] 创新风险预警")
        risks = self.predict_innovation_risks()
        for warning in risks.get("risk_warnings", [])[:3]:
            print(f"  - [{warning.get('severity', 'medium').upper()}] {warning.get('description', '')}")

        # 5. 价值链管理
        print("\n[5] 创新价值链管理")
        value_chain = self.manage_innovation_value_chain()
        for stage, metrics in value_chain.get("stage_metrics", {}).items():
            health = metrics.get("health_status", "unknown")
            print(f"  - {stage}: {health}")

        # 6. 综合评分
        print("\n[6] 生态系统综合状态")
        summary = {
            "total_innovations": allocation.get("total_innovations", 0),
            "active_domains": len(allocation.get("domain_distribution", {})),
            "risk_level": "high" if any(r.get("severity") == "high" for r in risks.get("risk_warnings", [])) else "medium" if risks.get("risk_warnings") else "low",
            "ecosystem_health": "good" if len(risks.get("risk_warnings", [])) < 3 else "needs_attention"
        }
        print(f"  - 总创新数: {summary.get('total_innovations', 0)}")
        print(f"  - 活跃领域数: {summary.get('active_domains', 0)}")
        print(f"  - 风险等级: {summary.get('risk_level', 'unknown')}")
        print(f"  - 生态系统健康: {summary.get('ecosystem_health', 'unknown')}")

        print("\n" + "=" * 60)

        return {
            "allocation": allocation,
            "optimization": optimization,
            "synergy": synergy,
            "risks": risks,
            "value_chain": value_chain,
            "summary": summary
        }


def main():
    """主函数"""
    engine = InnovationEcosystemGovernanceEngine()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "--version":
            info = engine.get_version()
            print(f"{info['name']} v{info['version']}")
            print(f"描述: {info['description']}")

        elif command == "--status":
            data = engine.get_cockpit_data()
            summary = data.get("summary", {})
            print("创新生态系统状态:")
            print(f"  - 总创新数: {summary.get('total_innovations', 0)}")
            print(f"  - 活跃领域数: {summary.get('active_domains', 0)}")
            print(f"  - 风险等级: {summary.get('risk_level', 'unknown')}")
            print(f"  - 生态系统健康: {summary.get('ecosystem_health', 'unknown')}")

        elif command == "--resource":
            allocation = engine.analyze_resource_allocation()
            print(json.dumps(allocation, ensure_ascii=False, indent=2))

        elif command == "--optimize":
            optimization = engine.optimize_resource_allocation()
            print(json.dumps(optimization, ensure_ascii=False, indent=2))

        elif command == "--synergy":
            synergy = engine.discover_cross_domain_synergy()
            print(json.dumps(synergy, ensure_ascii=False, indent=2))

        elif command == "--risk":
            risks = engine.predict_innovation_risks()
            print(json.dumps(risks, ensure_ascii=False, indent=2))

        elif command == "--value-chain":
            value_chain = engine.manage_innovation_value_chain()
            print(json.dumps(value_chain, ensure_ascii=False, indent=2))

        elif command == "--cockpit-data":
            data = engine.get_cockpit_data()
            print(json.dumps(data, ensure_ascii=False, indent=2))

        elif command == "--run":
            result = engine.run_full_analysis()
            return result

        else:
            print(f"未知命令: {command}")
            print("可用命令:")
            print("  --version       显示版本信息")
            print("  --status        显示生态系统状态")
            print("  --resource      分析资源分配")
            print("  --optimize      生成优化建议")
            print("  --synergy       发现跨领域协同")
            print("  --risk          预测创新风险")
            print("  --value-chain   管理价值链")
            print("  --cockpit-data  获取驾驶舱数据")
            print("  --run           运行完整分析")

    else:
        # 默认运行完整分析
        engine.run_full_analysis()


if __name__ == "__main__":
    main()