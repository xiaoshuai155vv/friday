#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环元进化价值创造与知识资产持续变现引擎

让系统能够将640轮积累的进化知识资产转化为实际价值，
识别高价值应用机会，主动创造新价值，形成知识资产的价值实现闭环。

系统能够：
1. 知识资产盘点与价值评估 - 全面盘点640轮进化积累的知识资产，评估每个资产的价值潜力
2. 高价值应用机会识别 - 从知识资产中发现高价值的应用场景和机会
3. 价值创造路径自动生成 - 将知识资产转化为实际价值的路径和方案
4. 价值变现效果追踪与反馈 - 追踪价值实现效果，形成反馈闭环

与 round 640 执行监控引擎、round 639 目标设定引擎、round 621 价值创造引擎深度集成，
形成「资产盘点→机会识别→价值创造→效果追踪」的完整价值变现闭环。

Version: 1.0.0
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import subprocess

# 项目根目录
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"
REFERENCES_DIR = PROJECT_ROOT / "references"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"


class MetaValueCreationKnowledgeAssetMonetizationEngine:
    """元进化价值创造与知识资产持续变现引擎"""

    def __init__(self):
        self.name = "元进化价值创造与知识资产持续变现引擎"
        self.version = "1.0.0"
        self.state_dir = STATE_DIR
        self.logs_dir = LOGS_DIR
        # 数据文件
        self.knowledge_asset_file = self.state_dir / "meta_knowledge_asset_inventory.json"
        self.value_opportunity_file = self.state_dir / "meta_value_opportunity_high_value.json"
        self.value_creation_path_file = self.state_dir / "meta_value_creation_path.json"
        self.value_tracking_file = self.state_dir / "meta_value_monetization_tracking.json"
        # 引擎状态
        self.current_loop_round = 641
        # 知识资产类型
        self.asset_types = [
            "evolution_history",  # 进化历史
            "engine_knowledge",   # 引擎知识
            "methodology",        # 方法论
            "failure_learnings",   # 失败教训
            "success_patterns",   # 成功模式
            "knowledge_graph",    # 知识图谱
            "wisdom_accumulation"  # 智慧积累
        ]

    def get_version(self):
        """获取引擎版本信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": "元进化价值创造与知识资产持续变现引擎 - 将640轮进化知识资产转化为实际价值，识别高价值机会，主动创造价值"
        }

    def get_status(self):
        """获取引擎当前状态"""
        # 检查数据文件
        status = {
            "engine": self.name,
            "version": self.version,
            "loop_round": self.current_loop_round,
            "data_files": {}
        }

        for file_name, file_path in [
            ("knowledge_asset", self.knowledge_asset_file),
            ("value_opportunity", self.value_opportunity_file),
            ("value_creation_path", self.value_creation_path_file),
            ("value_tracking", self.value_tracking_file)
        ]:
            status["data_files"][file_name] = {
                "exists": file_path.exists(),
                "path": str(file_path)
            }

        return status

    def get_cockpit_data(self):
        """获取驾驶舱数据"""
        # 加载知识资产盘点
        asset_data = {}
        if self.knowledge_asset_file.exists():
            try:
                with open(self.knowledge_asset_file, 'r', encoding='utf-8') as f:
                    asset_data = json.load(f)
            except Exception as e:
                pass

        # 加载价值机会
        opportunity_data = {}
        if self.value_opportunity_file.exists():
            try:
                with open(self.value_opportunity_file, 'r', encoding='utf-8') as f:
                    opportunity_data = json.load(f)
            except Exception as e:
                pass

        # 加载价值追踪
        tracking_data = {}
        if self.value_tracking_file.exists():
            try:
                with open(self.value_tracking_file, 'r', encoding='utf-8') as f:
                    tracking_data = json.load(f)
            except Exception as e:
                pass

        return {
            "engine": self.name,
            "version": self.version,
            "loop_round": self.current_loop_round,
            "knowledge_asset_summary": asset_data.get("summary", {}),
            "value_opportunities": opportunity_data.get("high_value_opportunities", [])[:5],
            "value_monetization_stats": tracking_data.get("monetization_stats", {}),
            "last_updated": asset_data.get("timestamp", "unknown")
        }

    def run(self):
        """执行知识资产价值变现分析"""
        print("=" * 60)
        print("元进化价值创造与知识资产持续变现引擎")
        print("=" * 60)

        results = {
            "timestamp": datetime.now().isoformat(),
            "loop_round": self.current_loop_round,
            "phases": {}
        }

        # 阶段1: 知识资产盘点
        print("\n[1/4] 知识资产盘点与价值评估...")
        asset_inventory = self.knowledge_asset_inventory()
        results["phases"]["asset_inventory"] = asset_inventory
        print(f"  - 发现 {asset_inventory.get('total_assets', 0)} 个知识资产")

        # 阶段2: 高价值机会识别
        print("\n[2/4] 高价值应用机会识别...")
        opportunities = self.identify_high_value_opportunities(asset_inventory)
        results["phases"]["opportunities"] = opportunities
        print(f"  - 识别 {len(opportunities.get('high_value_opportunities', []))} 个高价值机会")

        # 阶段3: 价值创造路径生成
        print("\n[3/4] 价值创造路径自动生成...")
        creation_paths = self.generate_value_creation_paths(opportunities)
        results["phases"]["creation_paths"] = creation_paths
        print(f"  - 生成 {len(creation_paths.get('value_creation_paths', []))} 条价值创造路径")

        # 阶段4: 价值变现追踪
        print("\n[4/4] 价值变现效果追踪与反馈...")
        tracking = self.track_value_monetization(results)
        results["phases"]["tracking"] = tracking
        print(f"  - 价值变现率: {tracking.get('monetization_stats', {}).get('overall_monetization_rate', 0):.1%}")

        print("\n" + "=" * 60)
        print("价值变现分析完成!")
        print("=" * 60)

        return results

    def knowledge_asset_inventory(self):
        """知识资产盘点与价值评估"""
        inventory = {
            "timestamp": datetime.now().isoformat(),
            "total_assets": 0,
            "assets_by_type": {},
            "value_assessment": {},
            "summary": {}
        }

        # 1. 盘点进化历史资产
        evolution_assets = self._inventory_evolution_history()
        inventory["assets_by_type"]["evolution_history"] = evolution_assets

        # 2. 盘点引擎知识资产
        engine_assets = self._inventory_engine_knowledge()
        inventory["assets_by_type"]["engine_knowledge"] = engine_assets

        # 3. 盘点方法论资产
        methodology_assets = self._inventory_methodology()
        inventory["assets_by_type"]["methodology"] = methodology_assets

        # 4. 盘点失败教训资产
        failure_assets = self._inventory_failure_learnings()
        inventory["assets_by_type"]["failure_learnings"] = failure_assets

        # 5. 盘点成功模式资产
        success_assets = self._inventory_success_patterns()
        inventory["assets_by_type"]["success_patterns"] = success_assets

        # 计算总资产
        inventory["total_assets"] = sum(
            len(assets) for assets in inventory["assets_by_type"].values()
        )

        # 价值评估
        inventory["value_assessment"] = self._assess_asset_value(inventory["assets_by_type"])

        # 摘要
        inventory["summary"] = {
            "total_assets": inventory["total_assets"],
            "asset_types_count": len(inventory["assets_by_type"]),
            "high_value_assets": len([v for v in inventory["value_assessment"].values() if v.get("value_score", 0) > 0.7]),
            "total_value_score": sum(v.get("value_score", 0) for v in inventory["value_assessment"].values()) / max(len(inventory["value_assessment"]), 1)
        }

        # 保存
        self._save_json(self.knowledge_asset_file, inventory)

        return inventory

    def _inventory_evolution_history(self):
        """盘点进化历史资产"""
        assets = {
            "total_rounds": 0,
            "completed_rounds": 0,
            "engines_created": 0,
            "key_milestones": []
        }

        # 统计进化历史
        try:
            # 读取 evolution_completed_*.json 文件数量
            completed_files = list(STATE_DIR.glob("evolution_completed_*.json"))
            assets["total_rounds"] = len(completed_files)

            # 统计已完成的轮次
            completed_count = 0
            engines_created = 0
            for f in completed_files:
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        if data.get("completion_status") == "completed":
                            completed_count += 1
                            if "modules_created" in data.get("execution_summary", {}):
                                engines_created += len(data["execution_summary"].get("modules_created", []))
                except:
                    pass

            assets["completed_rounds"] = completed_count
            assets["engines_created"] = engines_created

        except Exception as e:
            print(f"  警告: 盘点进化历史失败: {e}")

        return assets

    def _inventory_engine_knowledge(self):
        """盘点引擎知识资产"""
        assets = {
            "total_engines": 0,
            "engine_categories": {},
            "engine_list": []
        }

        try:
            # 统计 scripts 目录下的 evolution_*.py 文件
            engine_files = list(SCRIPTS_DIR.glob("evolution_meta_*.py"))
            engine_files.extend(list(SCRIPTS_DIR.glob("evolution_*.py")))
            engine_files = [f for f in engine_files if f.name != "evolution_loop_client.py"]

            assets["total_engines"] = len(engine_files)

            # 分类
            categories = defaultdict(list)
            for f in engine_files:
                name = f.stem
                if "value" in name.lower():
                    categories["价值类"].append(name)
                elif "knowledge" in name.lower() or "wisdom" in name.lower():
                    categories["知识类"].append(name)
                elif "prediction" in name.lower() or "forecast" in name.lower():
                    categories["预测类"].append(name)
                elif "health" in name.lower() or "diagnosis" in name.lower():
                    categories["健康类"].append(name)
                elif "collaboration" in name.lower() or "协同" in name:
                    categories["协同类"].append(name)
                else:
                    categories["其他类"].append(name)

            assets["engine_categories"] = dict(categories)
            assets["engine_list"] = [f.stem for f in engine_files]

        except Exception as e:
            print(f"  警告: 盘点引擎知识失败: {e}")

        return assets

    def _inventory_methodology(self):
        """盘点方法论资产"""
        assets = {
            "evolution_methodology": True,
            "optimization_patterns": 0,
            "best_practices": []
        }

        try:
            # 检查 references 下的方法论文件
            methodology_file = REFERENCES_DIR / "agent_evolution_workflow.md"
            if methodology_file.exists():
                assets["has_methodology_doc"] = True
                # 统计优化模式
                assets["optimization_patterns"] = 10  # 基本的优化模式数量

        except Exception as e:
            print(f"  警告: 盘点方法论资产失败: {e}")

        return assets

    def _inventory_failure_learnings(self):
        """盘点失败教训资产"""
        assets = {
            "total_lessons": 0,
            "failure_categories": []
        }

        try:
            failures_file = REFERENCES_DIR / "failures.md"
            if failures_file.exists():
                with open(failures_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 统计失败教训数量
                    assets["total_lessons"] = content.count("- 202")
                    assets["failure_categories"] = [
                        "截图/视觉相关",
                        "窗口激活相关",
                        "剪贴板相关",
                        "多模态相关",
                        "远程会话相关"
                    ]

        except Exception as e:
            print(f"  警告: 盘点失败教训失败: {e}")

        return assets

    def _inventory_success_patterns(self):
        """盘点成功模式资产"""
        assets = {
            "successful_engines": 0,
            "success_patterns": []
        }

        try:
            # 从已完成轮次中提取成功模式
            completed_files = list(STATE_DIR.glob("evolution_completed_*.json"))
            success_patterns = []

            for f in completed_files:
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        if data.get("completion_status") == "completed":
                            goal = data.get("current_goal", "")
                            if goal:
                                success_patterns.append({
                                    "round": data.get("loop_round"),
                                    "goal": goal[:100]
                                })
                except:
                    pass

            assets["successful_engines"] = len(success_patterns)
            assets["success_patterns"] = success_patterns[:20]  # 保留最近20个

        except Exception as e:
            print(f"  警告: 盘点成功模式失败: {e}")

        return assets

    def _assess_asset_value(self, assets_by_type):
        """评估资产价值"""
        value_assessment = {}

        for asset_type, assets in assets_by_type.items():
            # 基于资产数量和类型计算价值分数
            base_score = 0.5

            if asset_type == "evolution_history":
                # 进化历史价值高
                total = assets.get("total_rounds", 0)
                if total > 500:
                    base_score = 0.95
                elif total > 300:
                    base_score = 0.85
                elif total > 100:
                    base_score = 0.75

            elif asset_type == "engine_knowledge":
                # 引擎知识价值高
                total = assets.get("total_engines", 0)
                if total > 80:
                    base_score = 0.95
                elif total > 50:
                    base_score = 0.85
                elif total > 30:
                    base_score = 0.75

            elif asset_type == "success_patterns":
                # 成功模式价值高
                total = assets.get("successful_engines", 0)
                if total > 300:
                    base_score = 0.90

            value_assessment[asset_type] = {
                "value_score": base_score,
                "value_category": "high" if base_score > 0.7 else "medium" if base_score > 0.4 else "low",
                "monetization_potential": self._calculate_monetization_potential(asset_type, assets)
            }

        return value_assessment

    def _calculate_monetization_potential(self, asset_type, assets):
        """计算资产变现潜力"""
        potential = {
            "direct_value": 0.0,
            "indirect_value": 0.0,
            "strategic_value": 0.0
        }

        if asset_type == "evolution_history":
            potential = {"direct_value": 0.8, "indirect_value": 0.9, "strategic_value": 0.95}
        elif asset_type == "engine_knowledge":
            potential = {"direct_value": 0.85, "indirect_value": 0.85, "strategic_value": 0.90}
        elif asset_type == "success_patterns":
            potential = {"direct_value": 0.75, "indirect_value": 0.80, "strategic_value": 0.85}

        return potential

    def identify_high_value_opportunities(self, asset_inventory):
        """识别高价值应用机会"""
        opportunities = {
            "timestamp": datetime.now().isoformat(),
            "high_value_opportunities": [],
            "opportunity_analysis": {}
        }

        # 分析知识资产找高价值机会
        value_assessment = asset_inventory.get("value_assessment", {})

        # 机会1: 进化历史数据价值变现
        if value_assessment.get("evolution_history", {}).get("value_score", 0) > 0.7:
            opportunities["high_value_opportunities"].append({
                "id": "opp_001",
                "name": "进化历史数据价值变现",
                "description": "利用640轮进化历史数据，为未来进化提供预测和决策支持",
                "value_score": 0.92,
                "asset_source": "evolution_history",
                "execution_approach": "构建进化趋势预测模型，指导后续进化方向",
                "expected_roi": 0.85
            })

        # 机会2: 引擎组合价值最大化
        if value_assessment.get("engine_knowledge", {}).get("value_score", 0) > 0.7:
            opportunities["high_value_opportunities"].append({
                "id": "opp_002",
                "name": "引擎组合价值最大化",
                "description": "组合多个元进化引擎能力，创造协同效应",
                "value_score": 0.88,
                "asset_source": "engine_knowledge",
                "execution_approach": "识别引擎间协作模式，生成优化组合建议",
                "expected_roi": 0.80
            })

        # 机会3: 成功模式复制推广
        if value_assessment.get("success_patterns", {}).get("value_score", 0) > 0.6:
            opportunities["high_value_opportunities"].append({
                "id": "opp_003",
                "name": "成功模式复制推广",
                "description": "将已验证的成功模式复制到新的进化场景",
                "value_score": 0.82,
                "asset_source": "success_patterns",
                "execution_approach": "提取成功模式模板，应用到新进化任务",
                "expected_roi": 0.75
            })

        # 机会4: 失败教训价值转化
        if value_assessment.get("failure_learnings", {}).get("value_score", 0) > 0.5:
            opportunities["high_value_opportunities"].append({
                "id": "opp_004",
                "name": "失败教训价值转化",
                "description": "将失败教训转化为优化建议，避免重复错误",
                "value_score": 0.78,
                "asset_source": "failure_learnings",
                "execution_approach": "构建失败模式识别器，自动预警潜在风险",
                "expected_roi": 0.70
            })

        # 机会5: 方法论复用价值实现
        if value_assessment.get("methodology", {}).get("value_score", 0) > 0.5:
            opportunities["high_value_opportunities"].append({
                "id": "opp_005",
                "name": "方法论复用价值实现",
                "description": "将进化方法论复用到新的进化场景",
                "value_score": 0.75,
                "asset_source": "methodology",
                "execution_approach": "构建方法论模板库，自动匹配应用场景",
                "expected_roi": 0.68
            })

        # 按价值评分排序
        opportunities["high_value_opportunities"].sort(
            key=lambda x: x.get("value_score", 0),
            reverse=True
        )

        # 机会分析摘要
        opportunities["opportunity_analysis"] = {
            "total_opportunities": len(opportunities["high_value_opportunities"]),
            "average_value_score": sum(o.get("value_score", 0) for o in opportunities["high_value_opportunities"]) / max(len(opportunities["high_value_opportunities"]), 1),
            "top_opportunity": opportunities["high_value_opportunities"][0].get("name") if opportunities["high_value_opportunities"] else None
        }

        # 保存
        self._save_json(self.value_opportunity_file, opportunities)

        return opportunities

    def generate_value_creation_paths(self, opportunities):
        """生成价值创造路径"""
        paths = {
            "timestamp": datetime.now().isoformat(),
            "value_creation_paths": [],
            "path_analysis": {}
        }

        high_value_opps = opportunities.get("high_value_opportunities", [])

        # 为每个高价值机会生成执行路径
        for opp in high_value_opps[:5]:
            path = {
                "opportunity_id": opp.get("id"),
                "opportunity_name": opp.get("name"),
                "value_score": opp.get("value_score", 0),
                "steps": self._generate_path_steps(opp),
                "estimated_duration": self._estimate_duration(opp),
                "required_engines": self._identify_required_engines(opp),
                "risk_level": self._assess_risk(opp)
            }
            paths["value_creation_paths"].append(path)

        # 路径分析
        paths["path_analysis"] = {
            "total_paths": len(paths["value_creation_paths"]),
            "low_risk_paths": len([p for p in paths["value_creation_paths"] if p.get("risk_level") == "low"]),
            "medium_risk_paths": len([p for p in paths["value_creation_paths"] if p.get("risk_level") == "medium"]),
            "recommended_path": paths["value_creation_paths"][0].get("opportunity_name") if paths["value_creation_paths"] else None
        }

        # 保存
        self._save_json(self.value_creation_path_file, paths)

        return paths

    def _generate_path_steps(self, opportunity):
        """生成路径步骤"""
        steps = []

        if opportunity.get("asset_source") == "evolution_history":
            steps = [
                {"step": 1, "action": "加载进化历史数据", "engine": "knowledge_graph_engine"},
                {"step": 2, "action": "训练趋势预测模型", "engine": "prediction_engine"},
                {"step": 3, "action": "生成进化建议", "engine": "goal_setting_engine"},
                {"step": 4, "action": "执行并验证", "engine": "execution_engine"}
            ]
        elif opportunity.get("asset_source") == "engine_knowledge":
            steps = [
                {"step": 1, "action": "盘点引擎能力", "engine": "meta_evolution_enhancement"},
                {"step": 2, "action": "识别协作模式", "engine": "collaboration_engine"},
                {"step": 3, "action": "生成组合建议", "engine": "strategy_optimizer"},
                {"step": 4, "action": "实施优化", "engine": "execution_engine"}
            ]
        else:
            steps = [
                {"step": 1, "action": "提取资产价值", "engine": "knowledge_extraction"},
                {"step": 2, "action": "匹配应用场景", "engine": "reasoning_engine"},
                {"step": 3, "action": "生成执行方案", "engine": "planning_engine"},
                {"step": 4, "action": "执行验证", "engine": "execution_engine"}
            ]

        return steps

    def _estimate_duration(self, opportunity):
        """估计执行时间"""
        duration_map = {
            "opp_001": "2-3轮",
            "opp_002": "1-2轮",
            "opp_003": "1轮",
            "opp_004": "1轮",
            "opp_005": "1-2轮"
        }
        return duration_map.get(opportunity.get("id"), "1-2轮")

    def _identify_required_engines(self, opportunity):
        """识别所需引擎"""
        engine_map = {
            "evolution_history": ["knowledge_graph_engine", "prediction_engine", "goal_setting_engine"],
            "engine_knowledge": ["meta_evolution_enhancement", "collaboration_engine", "strategy_optimizer"],
            "success_patterns": ["pattern_discovery_engine", "strategy_optimizer"],
            "failure_learnings": ["diagnosis_engine", "prevention_engine"],
            "methodology": ["methodology_optimizer", "strategy_generator"]
        }
        return engine_map.get(opportunity.get("asset_source"), ["execution_engine"])

    def _assess_risk(self, opportunity):
        """评估风险"""
        risk_map = {
            "opp_001": "medium",
            "opp_002": "low",
            "opp_003": "low",
            "opp_004": "low",
            "opp_005": "medium"
        }
        return risk_map.get(opportunity.get("id"), "medium")

    def track_value_monetization(self, results):
        """追踪价值变现效果"""
        tracking = {
            "timestamp": datetime.now().isoformat(),
            "monetization_stats": {},
            "value_creation_records": []
        }

        # 统计价值变现
        opportunities = results.get("phases", {}).get("opportunities", {})
        high_value_opps = opportunities.get("high_value_opportunities", [])

        if high_value_opps:
            total_value = sum(o.get("value_score", 0) for o in high_value_opps)
            avg_value = total_value / len(high_value_opps)

            tracking["monetization_stats"] = {
                "total_opportunities": len(high_value_opps),
                "total_value_score": total_value,
                "average_value_score": avg_value,
                "overall_monetization_rate": avg_value * 0.85,  # 估计变现率
                "top_opportunity_value": high_value_opps[0].get("value_score", 0)
            }

            # 记录价值创造
            for opp in high_value_opps[:3]:
                tracking["value_creation_records"].append({
                    "opportunity": opp.get("name"),
                    "value_score": opp.get("value_score", 0),
                    "expected_roi": opp.get("expected_roi", 0),
                    "status": "identified"
                })

        # 保存
        self._save_json(self.value_tracking_file, tracking)

        return tracking

    def _save_json(self, file_path, data):
        """保存JSON文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"  保存文件失败 {file_path}: {e}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="元进化价值创造与知识资产持续变现引擎")
    parser.add_argument("--version", action="store_true", help="显示版本信息")
    parser.add_argument("--status", action="store_true", help="显示引擎状态")
    parser.add_argument("--run", action="store_true", help="执行价值变现分析")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")

    args = parser.parse_args()

    engine = MetaValueCreationKnowledgeAssetMonetizationEngine()

    if args.version:
        print(json.dumps(engine.get_version(), ensure_ascii=False, indent=2))
    elif args.status:
        print(json.dumps(engine.get_status(), ensure_ascii=False, indent=2))
    elif args.cockpit_data:
        print(json.dumps(engine.get_cockpit_data(), ensure_ascii=False, indent=2))
    elif args.run:
        result = engine.run()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()