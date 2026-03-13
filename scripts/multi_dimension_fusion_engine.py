#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能多维融合智能分析引擎 (Multi-Dimension Fusion Intelligence Engine)

该引擎集成了系统自检、主动服务、预测预防、健康保障等多个引擎的洞察，
实现统一的智能态势感知与跨引擎协同增强。

功能：
1. 多引擎洞察聚合 - 整合系统自检、主动服务、预测预防等引擎的分析结果
2. 统一态势感知 - 提供综合的系统状态视图
3. 跨引擎协同增强 - 识别引擎间协同机会，优化联动效果
4. 智能建议融合 - 将多引擎建议整合为统一的行动指南

集成引擎：
- system_self_diagnosis_engine: 系统自检与健康报告
- proactive_service_enhancer: 主动服务增强
- predictive_prevention_engine: 预测与预防
- health_assurance_loop: 健康保障闭环
- proactive_operations_engine: 主动运维
- unified_recommender: 统一推荐
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# 路径配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
RUNTIME_STATE_DIR = os.path.join(PROJECT_ROOT, "runtime", "state")
RUNTIME_LOGS_DIR = os.path.join(PROJECT_ROOT, "runtime", "logs")


class MultiDimensionFusionEngine:
    """智能多维融合分析引擎"""

    def __init__(self):
        self.name = "MultiDimensionFusionEngine"
        self.version = "1.0.0"
        self.integrated_engines = [
            "system_self_diagnosis_engine",
            "proactive_service_enhancer",
            "predictive_prevention_engine",
            "health_assurance_loop",
            "proactive_operations_engine",
            "unified_recommender"
        ]
        self.last_update = None

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "name": self.name,
            "version": self.version,
            "status": "active",
            "integrated_engines": self.integrated_engines,
            "last_update": self.last_update
        }

    def collect_insights(self) -> Dict[str, Any]:
        """收集各引擎洞察"""
        insights = {
            "timestamp": datetime.now().isoformat(),
            "engines": {}
        }

        # 1. 收集系统自检洞察
        insights["engines"]["system_diagnosis"] = self._collect_system_diagnosis()

        # 2. 收集主动服务洞察
        insights["engines"]["proactive_service"] = self._collect_proactive_service()

        # 3. 收集预测预防洞察
        insights["engines"]["prediction_prevention"] = self._collect_prediction_prevention()

        # 4. 收集健康保障洞察
        insights["engines"]["health_assurance"] = self._collect_health_assurance()

        # 5. 收集主动运维洞察
        insights["engines"]["operations"] = self._collect_operations()

        # 6. 收集推荐洞察
        insights["engines"]["recommendations"] = self._collect_recommendations()

        return insights

    def _collect_system_diagnosis(self) -> Dict[str, Any]:
        """收集系统自检洞察"""
        result = {
            "status": "unknown",
            "health_score": 0,
            "issues": [],
            "recommendations": []
        }

        try:
            # 尝试导入并执行系统自检引擎
            sys.path.insert(0, SCRIPT_DIR)
            from system_self_diagnosis_engine import SystemSelfDiagnosisEngine
            diagnosis = SystemSelfDiagnosisEngine()
            report = diagnosis.get_detailed_report()
            result = {
                "status": "available",
                "health_score": report.get("health_score", 0),
                "issues": report.get("issues", [])[:5] if report.get("issues") else [],
                "recommendations": report.get("recommendations", [])[:3] if report.get("recommendations") else []
            }
        except Exception as e:
            result["status"] = "unavailable"
            result["error"] = str(e)

        return result

    def _collect_proactive_service(self) -> Dict[str, Any]:
        """收集主动服务洞察"""
        result = {
            "status": "unknown",
            "predicted_needs": [],
            "active_services": []
        }

        try:
            sys.path.insert(0, SCRIPT_DIR)
            from proactive_service_enhancer import ProactiveServiceEnhancer
            enhancer = ProactiveServiceEnhancer()
            prediction = enhancer.run_prediction()
            result = {
                "status": "available",
                "predicted_needs": prediction.get("predicted_services", [])[:3] if prediction.get("predicted_services") else [],
                "active_services": prediction.get("active_services", []) if prediction.get("active_services") else []
            }
        except Exception as e:
            result["status"] = "unavailable"
            result["error"] = str(e)

        return result

    def _collect_prediction_prevention(self) -> Dict[str, Any]:
        """收集预测预防洞察"""
        result = {
            "status": "unknown",
            "risk_level": "unknown",
            "predictions": [],
            "alerts": []
        }

        try:
            sys.path.insert(0, SCRIPT_DIR)
            from predictive_prevention_engine import PredictivePreventionEngine
            predictor = PredictivePreventionEngine()
            scan_result = predictor.scan_and_predict()
            result = {
                "status": "available",
                "risk_level": scan_result.get("risk_level", "unknown"),
                "predictions": scan_result.get("predictions", [])[:3] if scan_result.get("predictions") else [],
                "alerts": scan_result.get("issues", [])[:3] if scan_result.get("issues") else []
            }
        except Exception as e:
            result["status"] = "unavailable"
            result["error"] = str(e)

        return result

    def _collect_health_assurance(self) -> Dict[str, Any]:
        """收集健康保障洞察"""
        result = {
            "status": "unknown",
            "health_status": "unknown",
            "assurance_score": 0
        }

        try:
            sys.path.insert(0, SCRIPT_DIR)
            from health_assurance_loop import HealthAssuranceLoop
            health = HealthAssuranceLoop()
            status = health.get_status()
            result = {
                "status": "available",
                "health_status": status.get("health_status", "unknown"),
                "assurance_score": status.get("assurance_score", 0)
            }
        except Exception as e:
            result["status"] = "unavailable"
            result["error"] = str(e)

        return result

    def _collect_operations(self) -> Dict[str, Any]:
        """收集主动运维洞察"""
        result = {
            "status": "unknown",
            "resource_status": {},
            "optimizations": []
        }

        try:
            sys.path.insert(0, SCRIPT_DIR)
            from proactive_operations_engine import ProactiveOperationsEngine
            operations = ProactiveOperationsEngine()
            status = operations.get_status()
            suggestions = operations.get_suggestions()
            result = {
                "status": "available",
                "resource_status": status.get("resources", {}),
                "optimizations": suggestions.get("optimizations", [])[:3]
            }
        except Exception as e:
            result["status"] = "unavailable"
            result["error"] = str(e)

        return result

    def _collect_recommendations(self) -> Dict[str, Any]:
        """收集推荐洞察"""
        result = {
            "status": "unknown",
            "recommendations": []
        }

        try:
            sys.path.insert(0, SCRIPT_DIR)
            from unified_recommender import UnifiedRecommenderEngine
            recommender = UnifiedRecommenderEngine()
            recs = recommender.recommend()
            result = {
                "status": "available",
                "recommendations": recs.get("recommendations", [])[:3] if recs.get("recommendations") else []
            }
        except Exception as e:
            result["status"] = "unavailable"
            result["error"] = str(e)

        return result

    def analyze_situational_awareness(self) -> Dict[str, Any]:
        """分析统一态势感知"""
        insights = self.collect_insights()

        # 综合评分计算
        health_scores = []
        if insights["engines"].get("system_diagnosis", {}).get("status") == "available":
            health_scores.append(insights["engines"]["system_diagnosis"].get("health_score", 0))
        if insights["engines"].get("health_assurance", {}).get("status") == "available":
            health_scores.append(insights["engines"]["health_assurance"].get("assurance_score", 0))

        overall_health = sum(health_scores) / len(health_scores) if health_scores else 0

        # 风险评估
        risk_level = "low"
        pred_status = insights["engines"].get("prediction_prevention", {}).get("status")
        if pred_status == "available":
            risk = insights["engines"]["prediction_prevention"].get("risk_level", "low")
            if risk == "critical":
                risk_level = "critical"
            elif risk == "high":
                risk_level = "high"
            elif risk == "medium":
                risk_level = "medium"

        # 主动服务评估
        proactive_count = len(insights["engines"].get("proactive_service", {}).get("predicted_needs", []))

        return {
            "timestamp": datetime.now().isoformat(),
            "overall_health_score": round(overall_health, 1),
            "risk_level": risk_level,
            "active_predictions": proactive_count,
            "engines_status": {
                name: data.get("status", "unknown")
                for name, data in insights["engines"].items()
            }
        }

    def analyze_cross_engine_collaboration(self) -> Dict[str, Any]:
        """分析跨引擎协同"""
        insights = self.collect_insights()

        # 识别协同机会
        collaboration_opportunities = []

        # 机会1: 预测 + 主动服务
        if (insights["engines"].get("prediction_prevention", {}).get("status") == "available" and
            insights["engines"].get("proactive_service", {}).get("status") == "available"):
            predictions = insights["engines"]["prediction_prevention"].get("predictions", [])
            if predictions:
                collaboration_opportunities.append({
                    "type": "prediction_to_service",
                    "description": "将预测结果转化为主动服务",
                    "engines": ["predictive_prevention_engine", "proactive_service_enhancer"],
                    "priority": "high"
                })

        # 机会2: 自检 + 运维
        if (insights["engines"].get("system_diagnosis", {}).get("status") == "available" and
            insights["engines"].get("operations", {}).get("status") == "available"):
            issues = insights["engines"]["system_diagnosis"].get("issues", [])
            if issues:
                collaboration_opportunities.append({
                    "type": "diagnosis_to_operations",
                    "description": "根据诊断问题自动触发运维优化",
                    "engines": ["system_self_diagnosis_engine", "proactive_operations_engine"],
                    "priority": "high"
                })

        # 机会3: 健康保障 + 推荐
        if (insights["engines"].get("health_assurance", {}).get("status") == "available" and
            insights["engines"].get("recommendations", {}).get("status") == "available"):
            collaboration_opportunities.append({
                "type": "health_to_recommendations",
                "description": "基于健康状态提供个性化推荐",
                "engines": ["health_assurance_loop", "unified_recommender"],
                "priority": "medium"
            })

        return {
            "opportunities": collaboration_opportunities,
            "total_count": len(collaboration_opportunities)
        }

    def generate_fused_recommendations(self) -> List[Dict[str, Any]]:
        """生成融合建议"""
        insights = self.collect_insights()
        recommendations = []

        # 从系统自检获取建议
        diag_recs = insights["engines"].get("system_diagnosis", {}).get("recommendations", [])
        for rec in diag_recs:
            recommendations.append({
                "source": "system_diagnosis",
                "content": rec,
                "priority": "high"
            })

        # 从运维获取优化建议
        ops_opts = insights["engines"].get("operations", {}).get("optimizations", [])
        for opt in ops_opts:
            recommendations.append({
                "source": "operations",
                "content": opt,
                "priority": "medium"
            })

        # 从预测获取预防建议
        pred_alerts = insights["engines"].get("prediction_prevention", {}).get("alerts", [])
        for alert in pred_alerts:
            recommendations.append({
                "source": "prediction_prevention",
                "content": alert,
                "priority": "high"
            })

        return recommendations

    def get_fusion_summary(self) -> Dict[str, Any]:
        """获取融合分析摘要"""
        situational = self.analyze_situational_awareness()
        collaboration = self.analyze_cross_engine_collaboration()
        recommendations = self.generate_fused_recommendations()

        self.last_update = datetime.now().isoformat()

        return {
            "name": self.name,
            "version": self.version,
            "situational_awareness": situational,
            "cross_engine_collaboration": collaboration,
            "fused_recommendations": recommendations[:5],
            "last_update": self.last_update
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="智能多维融合智能分析引擎")
    parser.add_argument("command", nargs="?", default="status",
                       help="命令: status, insights, situational, collaboration, recommendations, summary")
    parser.add_argument("--output", "-o", help="输出文件路径")

    args = parser.parse_args()

    engine = MultiDimensionFusionEngine()

    if args.command == "status":
        result = engine.get_status()
    elif args.command == "insights":
        result = engine.collect_insights()
    elif args.command == "situational":
        result = engine.analyze_situational_awareness()
    elif args.command == "collaboration":
        result = engine.analyze_cross_engine_collaboration()
    elif args.command == "recommendations":
        result = {"recommendations": engine.generate_fused_recommendations()}
    elif args.command == "summary" or args.command == "status":
        result = engine.get_fusion_summary()
    else:
        result = {"error": f"未知命令: {args.command}"}

    # 输出结果
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到: {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()