"""
智能服务闭环引擎 (Intelligent Service Loop Engine)
整合预测预防引擎、决策编排中心、执行引擎，实现预测→决策→执行→反馈→学习的完整自动化服务闭环

功能：
1. 智能主动服务：一键触发预测→决策→执行闭环
2. 跨引擎协调：整合多个引擎协同工作
3. 反馈学习：根据执行结果自动学习和优化
4. 统一入口：提供简洁的 CLI 接口

集成模块：
- predictive_prevention_engine: 预测与预防
- decision_orchestrator: 决策编排
- unified_recommender: 统一推荐与执行
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# 添加 scripts 目录到路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))


class IntelligentServiceLoop:
    """智能服务闭环引擎"""

    def __init__(self):
        self.state_file = SCRIPT_DIR.parent / "runtime" / "state" / "service_loop_state.json"
        self.history_file = SCRIPT_DIR.parent / "runtime" / "state" / "service_loop_history.json"
        self._ensure_state_dir()
        self.predictive_engine = None
        self.decision_orchestrator = None
        self.unified_recommender = None

    def _ensure_state_dir(self):
        """确保状态目录存在"""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

    def _load_state(self) -> Dict[str, Any]:
        """加载状态"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "enabled": True,
            "auto_execute": False,
            "last_run": None,
            "total_runs": 0,
            "feedback_count": 0
        }

    def _save_state(self, state: Dict[str, Any]):
        """保存状态"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def _load_history(self) -> List[Dict[str, Any]]:
        """加载历史记录"""
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_history(self, history: List[Dict[str, Any]]):
        """保存历史记录"""
        # 只保留最近 50 条
        history = history[-50:]
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def _load_engines(self):
        """加载集成引擎"""
        if self.predictive_engine is None:
            try:
                from predictive_prevention_engine import PredictivePreventionEngine
                self.predictive_engine = PredictivePreventionEngine()
            except ImportError as e:
                print(f"警告: 无法加载预测预防引擎: {e}")

        if self.decision_orchestrator is None:
            try:
                from decision_orchestrator import DecisionOrchestrator
                self.decision_orchestrator = DecisionOrchestrator()
            except ImportError as e:
                print(f"警告: 无法加载决策编排中心: {e}")

        if self.unified_recommender is None:
            try:
                from unified_recommender import UnifiedRecommenderEngine as UnifiedRecommender
                self.unified_recommender = UnifiedRecommender()
            except ImportError as e:
                print(f"警告: 无法加载统一推荐引擎: {e}")

    def run_service_loop(self, auto_execute: bool = False, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        运行智能服务闭环

        Args:
            auto_execute: 是否自动执行推荐
            context: 额外上下文信息

        Returns:
            包含预测、决策、执行结果的字典
        """
        start_time = datetime.now()
        result = {
            "status": "init",
            "start_time": start_time.isoformat(),
            "prediction": None,
            "decision": None,
            "execution": None,
            "feedback": None,
            "errors": []
        }

        # 加载引擎
        self._load_engines()
        state = self._load_state()

        # 步骤 1: 预测
        try:
            if self.predictive_engine:
                prediction_result = self.predictive_engine.scan_and_predict()
                result["prediction"] = {
                    "status": "success",
                    "data": prediction_result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                result["errors"].append("预测引擎未加载")
        except Exception as e:
            result["prediction"] = {"status": "error", "message": str(e)}
            result["errors"].append(f"预测步骤失败: {e}")

        # 步骤 2: 决策编排
        try:
            if self.decision_orchestrator and result.get("prediction", {}).get("status") == "success":
                # 使用预测结果进行决策
                decision_result = self.decision_orchestrator.proactive_service_from_prediction()
                result["decision"] = {
                    "status": "success",
                    "data": decision_result,
                    "timestamp": datetime.now().isoformat()
                }
            elif self.decision_orchestrator:
                # 如果没有预测结果，使用一般上下文
                user_input = "智能主动服务"
                decision_result = self.decision_orchestrator.orchestrate(user_input)
                result["decision"] = {
                    "status": "success",
                    "data": decision_result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                result["errors"].append("决策引擎未加载")
        except Exception as e:
            result["decision"] = {"status": "error", "message": str(e)}
            result["errors"].append(f"决策步骤失败: {e}")

        # 步骤 3: 执行
        if auto_execute:
            try:
                if self.unified_recommender:
                    # 尝试自动执行推荐
                    exec_result = self.unified_recommender.execute_auto(auto_confirm=True)
                    result["execution"] = {
                        "status": "success",
                        "data": exec_result,
                        "timestamp": datetime.now().isoformat()
                    }
                elif self.decision_orchestrator and result.get("decision", {}).get("status") == "success":
                    # 使用决策编排中心执行
                    exec_result = self.decision_orchestrator.execute_auto_remediation()
                    result["execution"] = {
                        "status": "success",
                        "data": exec_result,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    result["execution"] = {"status": "skipped", "message": "无可执行项"}
            except Exception as e:
                result["execution"] = {"status": "error", "message": str(e)}
                result["errors"].append(f"执行步骤失败: {e}")
        else:
            result["execution"] = {"status": "pending", "message": "等待用户确认执行"}

        # 步骤 4: 记录历史
        end_time = datetime.now()
        result["end_time"] = end_time.isoformat()
        result["duration_seconds"] = (end_time - start_time).total_seconds()
        result["status"] = "completed" if not result["errors"] else "partial"

        # 更新状态
        state["last_run"] = end_time.isoformat()
        state["total_runs"] = state.get("total_runs", 0) + 1
        self._save_state(state)

        # 保存到历史
        history = self._load_history()
        history.append({
            "timestamp": end_time.isoformat(),
            "auto_execute": auto_execute,
            "status": result["status"],
            "prediction_status": result.get("prediction", {}).get("status"),
            "decision_status": result.get("decision", {}).get("status"),
            "execution_status": result.get("execution", {}).get("status"),
            "duration_seconds": result["duration_seconds"]
        })
        self._save_history(history)

        return result

    def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        state = self._load_state()
        history = self._load_history()

        # 计算成功率
        total = len(history)
        success = sum(1 for h in history if h.get("status") == "completed")
        success_rate = (success / total * 100) if total > 0 else 0

        return {
            "enabled": state.get("enabled", True),
            "last_run": state.get("last_run"),
            "total_runs": state.get("total_runs", 0),
            "feedback_count": state.get("feedback_count", 0),
            "history_count": total,
            "success_rate": round(success_rate, 1),
            "recent_runs": history[-5:] if history else []
        }

    def submit_feedback(self, run_timestamp: str, feedback: str, rating: int = None) -> Dict[str, Any]:
        """
        提交执行反馈

        Args:
            run_timestamp: 运行时间戳
            feedback: 反馈内容
            rating: 评分 (1-5)

        Returns:
            操作结果
        """
        history = self._load_history()

        # 找到对应运行记录
        for item in history:
            if item.get("timestamp") == run_timestamp:
                item["feedback"] = feedback
                if rating is not None:
                    item["rating"] = max(1, min(5, rating))
                break

        self._save_history(history)

        # 更新反馈计数
        state = self._load_state()
        state["feedback_count"] = state.get("feedback_count", 0) + 1
        self._save_state(state)

        return {"status": "success", "message": "反馈已记录"}

    def get_recommendations(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """获取智能推荐（整合所有引擎的推荐）"""
        self._load_engines()
        recommendations = []

        # 从预测引擎获取推荐
        if self.predictive_engine:
            try:
                prediction = self.predictive_engine.scan_and_predict()
                if prediction.get("risk_level") in ["high", "critical"]:
                    recommendations.append({
                        "type": "predictive",
                        "priority": "high",
                        "description": f"风险预警: {prediction.get('risk_level')}",
                        "data": prediction
                    })
                # 添加预防建议
                for suggestion in prediction.get("prevention_suggestions", [])[:3]:
                    recommendations.append({
                        "type": "prevention",
                        "priority": "medium",
                        "description": suggestion.get("title", "预防建议"),
                        "data": suggestion
                    })
            except Exception as e:
                pass

        # 从决策引擎获取推荐
        if self.decision_orchestrator:
            try:
                suggestions = self.decision_orchestrator.suggest_engines("智能服务")
                for suggestion in suggestions[:3]:
                    recommendations.append({
                        "type": "decision",
                        "priority": "medium",
                        "description": suggestion.get("description", "决策建议"),
                        "data": suggestion
                    })
            except Exception as e:
                pass

        # 从推荐引擎获取推荐
        if self.unified_recommender:
            try:
                unified_recs = self.unified_recommender.get_all_recommendations(context or {}, limit=5)
                for rec in unified_recs:
                    recommendations.append({
                        "type": "unified",
                        "priority": rec.confidence,
                        "description": rec.title,
                        "data": {"recommendation_id": rec.id, **rec.__dict__}
                    })
            except Exception as e:
                pass

        return {
            "status": "success",
            "recommendations": recommendations,
            "count": len(recommendations)
        }

    def auto_learning(self) -> Dict[str, Any]:
        """自动学习：基于历史数据优化服务"""
        history = self._load_history()

        if len(history) < 3:
            return {"status": "skipped", "message": "历史数据不足，需要至少 3 次运行记录"}

        # 分析历史数据
        analysis = {
            "total_runs": len(history),
            "success_count": sum(1 for h in history if h.get("status") == "completed"),
            "avg_duration": sum(h.get("duration_seconds", 0) for h in history) / len(history),
            "rating_avg": sum(h.get("rating", 0) for h in history if h.get("rating")) / max(1, sum(1 for h in history if h.get("rating"))) if any(h.get("rating") for h in history) else None,
            "feedback_issues": [h.get("feedback") for h in history if h.get("feedback")]
        }

        # 生成优化建议
        suggestions = []

        if analysis["avg_duration"] > 30:
            suggestions.append("执行时间较长，建议优化决策流程")

        if analysis.get("rating_avg") and analysis["rating_avg"] < 3:
            suggestions.append("用户评分较低，建议改进预测准确性")

        if analysis["feedback_issues"]:
            # 提取常见问题
            issue_keywords = {}
            for issue in analysis["feedback_issues"]:
                words = issue.split()
                for word in words:
                    if len(word) > 3:
                        issue_keywords[word] = issue_keywords.get(word, 0) + 1

            common_issues = sorted(issue_keywords.items(), key=lambda x: x[1], reverse=True)[:3]
            if common_issues:
                suggestions.append(f"常见问题: {', '.join([k for k, v in common_issues])}")

        return {
            "status": "success",
            "analysis": analysis,
            "suggestions": suggestions
        }


def main():
    """CLI 入口"""
    import argparse

    parser = argparse.ArgumentParser(description="智能服务闭环引擎")
    parser.add_argument("action", nargs="?", choices=["run", "status", "recommend", "feedback", "learn"],
                        default="status", help="执行动作")
    parser.add_argument("--auto", "-a", action="store_true", help="自动执行推荐")
    parser.add_argument("--timestamp", "-t", help="运行时间戳（用于反馈）")
    parser.add_argument("--feedback", "-f", help="反馈内容")
    parser.add_argument("--rating", "-r", type=int, choices=[1, 2, 3, 4, 5], help="评分 1-5")

    args = parser.parse_args()

    engine = IntelligentServiceLoop()

    if args.action == "run":
        result = engine.run_service_loop(auto_execute=args.auto)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == "status":
        status = engine.get_service_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.action == "recommend":
        recs = engine.get_recommendations()
        print(json.dumps(recs, ensure_ascii=False, indent=2))

    elif args.action == "feedback":
        if not args.timestamp or not args.feedback:
            print("错误: 需要提供 --timestamp 和 --feedback")
            sys.exit(1)
        result = engine.submit_feedback(args.timestamp, args.feedback, args.rating)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == "learn":
        result = engine.auto_learning()
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()