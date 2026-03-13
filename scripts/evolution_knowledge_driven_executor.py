#!/usr/bin/env python3
"""
智能进化知识驱动自适应执行引擎（Evolution Knowledge Driven Adaptive Executor）
version 1.0.0

让系统能够将 round 240 传承的进化知识真正应用到执行中，基于历史成功/失败模式
自动调整执行策略，实现从"存储知识"到"应用知识"的闭环，形成真正的学以致用能力。

功能：
1. 进化知识智能检索（基于当前目标检索相关历史知识）
2. 执行策略自动适配（根据历史成功模式调整执行参数）
3. 失败模式规避（基于历史失败教训自动规避风险）
4. 执行效果实时反馈（将执行结果反馈给知识图谱更新）
5. 与 do.py 深度集成

依赖：
- evolution_knowledge_inheritance_engine.py (round 240)
- evolution_adaptive_optimizer.py (round 237)
- evolution_iteration_coordination.py (round 238)
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class EvolutionKnowledgeDrivenExecutor:
    """智能进化知识驱动自适应执行引擎"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.runtime_dir = self.project_root / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.references_dir = self.project_root / "references"

        # 加载知识传承引擎
        try:
            from evolution_knowledge_inheritance_engine import EvolutionKnowledgeInheritance
            self.knowledge_engine = EvolutionKnowledgeInheritance()
        except ImportError:
            print("警告：无法加载知识传承引擎，将使用基础模式")
            self.knowledge_engine = None

        # 执行策略缓存
        self.strategy_cache_file = self.runtime_dir / "knowledge_driven_strategy_cache.json"
        self.strategy_cache = self._load_strategy_cache()

        # 执行历史
        self.execution_history_file = self.runtime_dir / "knowledge_driven_execution_history.json"
        self.execution_history = self._load_execution_history()

    def _load_strategy_cache(self) -> Dict:
        """加载策略缓存"""
        if self.strategy_cache_file.exists():
            try:
                with open(self.strategy_cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "version": "1.0.0",
            "strategies": {},
            "last_updated": datetime.now().isoformat()
        }

    def _save_strategy_cache(self):
        """保存策略缓存"""
        self.strategy_cache["last_updated"] = datetime.now().isoformat()
        with open(self.strategy_cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.strategy_cache, f, ensure_ascii=False, indent=2)

    def _load_execution_history(self) -> List[Dict]:
        """加载执行历史"""
        if self.execution_history_file.exists():
            try:
                with open(self.execution_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return []

    def _save_execution_history(self):
        """保存执行历史"""
        # 只保留最近100条
        history = self.execution_history[-100:]
        with open(self.execution_history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def get_relevant_knowledge(self, current_goal: str) -> Dict[str, Any]:
        """
        基于当前目标检索相关知识
        参数：
            current_goal: 当前进化目标
        返回：相关知识字典
        """
        knowledge_result = {
            "related_rounds": [],
            "success_patterns": [],
            "failure_patterns": [],
            "best_practices": [],
            "recommended_actions": [],
            "risks_to_avoid": []
        }

        if not self.knowledge_engine:
            return knowledge_result

        # 1. 获取推荐的相关历史进化
        try:
            recommendations = self.knowledge_engine.recommend_knowledge(current_goal)
            knowledge_result["related_rounds"] = recommendations
        except Exception as e:
            print(f"获取推荐知识失败: {e}")

        # 2. 加载 failures.md 获取失败模式
        try:
            failures_file = self.references_dir / "failures.md"
            if failures_file.exists():
                with open(failures_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 提取失败模式
                    lines = content.split('\n')
                    for line in lines:
                        if line.startswith('- 20') and '：' in line:
                            knowledge_result["failure_patterns"].append(line.strip())
        except Exception as e:
            print(f"加载失败模式失败: {e}")

        # 3. 获取最佳实践
        try:
            status = self.knowledge_engine.get_knowledge_status()
            # 查询相关最佳实践
            query_keywords = self._extract_keywords(current_goal)
            for keyword in query_keywords[:3]:
                results = self.knowledge_engine.query_knowledge(keyword, max_results=3)
                for r in results:
                    if r.get('type') == 'best_practice':
                        knowledge_result["best_practices"].append(r.get('data'))
        except Exception as e:
            print(f"获取最佳实践失败: {e}")

        # 4. 生成推荐动作
        knowledge_result["recommended_actions"] = self._generate_recommended_actions(
            knowledge_result["related_rounds"],
            knowledge_result["best_practices"]
        )

        # 5. 识别需要规避的风险
        knowledge_result["risks_to_avoid"] = self._identify_risks(
            knowledge_result["failure_patterns"]
        )

        return knowledge_result

    def _extract_keywords(self, goal: str) -> List[str]:
        """从目标中提取关键词"""
        keywords = []

        # 常见关键词
        common_keywords = [
            '引擎', 'engine', '智能', '自动', '协同', '学习', '预测',
            '优化', '决策', '执行', '集成', '发现', '评估', '监控'
        ]

        goal_lower = goal.lower()
        for kw in common_keywords:
            if kw.lower() in goal_lower:
                keywords.append(kw)

        # 从目标中提取更多词
        import re
        words = re.findall(r'[\u4e00-\u9fa5a-zA-Z]+', goal)
        for word in words:
            if len(word) >= 2 and word not in keywords:
                keywords.append(word)

        return keywords[:5]

    def _generate_recommended_actions(self, related_rounds: List[Dict],
                                     best_practices: List[Dict]) -> List[str]:
        """基于知识生成推荐动作"""
        actions = []

        # 从相关历史中提取成功要素
        for round_data in related_rounds[:5]:
            if isinstance(round_data, dict):
                goal = round_data.get('goal', '')
                overlap = round_data.get('overlap', 0)
                if overlap > 0:
                    actions.append(f"参考 round {round_data.get('round', '?')}: {goal[:50]}")

        # 从最佳实践中提取动作
        for practice in best_practices[:3]:
            if isinstance(practice, dict):
                key_actions = practice.get('key_actions', [])
                for action in key_actions[:2]:
                    if action and action not in actions:
                        actions.append(action)

        return actions[:5]

    def _identify_risks(self, failure_patterns: List[str]) -> List[str]:
        """从失败模式中识别需要规避的风险"""
        risks = []

        for pattern in failure_patterns[-10:]:  # 取最近的10条
            if '：' in pattern:
                try:
                    # 提取原因部分
                    reason = pattern.split('：')[1].split('→')[0].strip()
                    if reason and len(reason) < 100:
                        risks.append(reason)
                except:
                    pass

        return risks[:5]

    def adapt_execution_strategy(self, current_goal: str,
                                 base_strategy: Dict) -> Dict[str, Any]:
        """
        基于知识自动适配执行策略
        参数：
            current_goal: 当前进化目标
            base_strategy: 基础执行策略
        返回：适配后的执行策略
        """
        # 1. 获取相关知识
        knowledge = self.get_relevant_knowledge(current_goal)

        # 2. 构建适配策略
        adapted = {
            "original_strategy": base_strategy,
            "adaptations": [],
            "knowledge_applied": knowledge,
            "risk_mitigations": [],
            "estimated_improvement": 0.0
        }

        # 3. 应用知识进行策略调整

        # 3.1 基于成功模式增强
        if knowledge["related_rounds"]:
            adapted["adaptations"].append({
                "type": "enhancement",
                "description": "基于相关历史进化成功模式增强执行策略",
                "applied_from_rounds": [r.get('round', 0) for r in knowledge["related_rounds"][:3]]
            })
            adapted["estimated_improvement"] += 0.15

        # 3.2 基于最佳实践优化
        if knowledge["best_practices"]:
            adapted["adaptations"].append({
                "type": "optimization",
                "description": "应用历史最佳实践优化执行步骤",
                "practices_count": len(knowledge["best_practices"])
            })
            adapted["estimated_improvement"] += 0.10

        # 3.3 规避失败模式
        if knowledge["risks_to_avoid"]:
            adapted["adaptations"].append({
                "type": "risk_mitigation",
                "description": "添加失败模式规避措施",
                "risks_avoided": len(knowledge["risks_to_avoid"])
            })
            adapted["risk_mitigations"] = knowledge["risks_to_avoid"]
            adapted["estimated_improvement"] += 0.10

        # 4. 生成优化后的策略
        optimized_strategy = self._apply_adaptations(
            base_strategy,
            knowledge,
            adapted["adaptations"]
        )

        adapted["optimized_strategy"] = optimized_strategy

        # 5. 缓存策略
        strategy_key = self._generate_strategy_key(current_goal)
        self.strategy_cache["strategies"][strategy_key] = adapted
        self._save_strategy_cache()

        return adapted

    def _apply_adaptations(self, base_strategy: Dict, knowledge: Dict,
                          adaptations: List[Dict]) -> Dict:
        """应用适配生成优化策略"""
        optimized = base_strategy.copy()

        # 添加前置知识准备步骤
        if knowledge.get("related_rounds"):
            if "preparation_steps" not in optimized:
                optimized["preparation_steps"] = []

            # 添加知识检索步骤
            optimized["preparation_steps"].append({
                "step": "knowledge_retrieval",
                "description": "检索相关历史进化知识",
                "related_rounds": [r.get('round', 0) for r in knowledge.get("related_rounds", [])[:3]]
            })

        # 添加风险规避步骤
        if knowledge.get("risks_to_avoid"):
            if "risk_mitigations" not in optimized:
                optimized["risk_mitigations"] = []
            optimized["risk_mitigations"] = knowledge.get("risks_to_avoid", [])[:3]

        # 调整超时设置（基于历史经验）
        if adaptations:
            # 如果有复杂适配，增加超时时间
            optimized["estimated_timeout"] = base_strategy.get("timeout", 300) * 1.2

        return optimized

    def _generate_strategy_key(self, goal: str) -> str:
        """生成策略缓存键"""
        import hashlib
        return hashlib.md5(goal.encode('utf-8')).hexdigest()[:16]

    def execute_with_knowledge_guidance(self, current_goal: str,
                                        execution_func,
                                        *args, **kwargs) -> Tuple[Any, Dict]:
        """
        在知识指导下执行任务
        参数：
            current_goal: 当前目标
            execution_func: 执行函数
            *args, **kwargs: 传递给执行函数的参数
        返回：(执行结果, 执行报告)
        """
        start_time = datetime.now()

        # 1. 获取相关知识
        knowledge = self.get_relevant_knowledge(current_goal)

        # 2. 记录执行开始
        execution_record = {
            "goal": current_goal,
            "start_time": start_time.isoformat(),
            "knowledge_applied": bool(knowledge.get("related_rounds")),
            "related_rounds": [r.get('round', 0) for r in knowledge.get("related_rounds", [])[:3]],
            "risks_aware": len(knowledge.get("risks_to_avoid", []))
        }

        # 3. 尝试执行
        result = None
        error = None

        try:
            result = execution_func(*args, **kwargs)
            execution_record["status"] = "success"
            execution_record["result"] = str(result)[:200] if result else None
        except Exception as e:
            execution_record["status"] = "failed"
            error = str(e)
            execution_record["error"] = error

            # 4. 如果失败，分析原因并记录
            self._analyze_failure_and_update_knowledge(current_goal, error, knowledge)

        # 5. 记录执行结束
        end_time = datetime.now()
        execution_record["end_time"] = end_time.isoformat()
        execution_record["duration_seconds"] = (end_time - start_time).total_seconds()

        # 6. 如果成功，更新知识库
        if execution_record.get("status") == "success":
            self._update_knowledge_with_success(current_goal, knowledge, execution_record)

        # 7. 保存执行历史
        self.execution_history.append(execution_record)
        self._save_execution_history()

        # 8. 生成执行报告
        report = {
            "goal": current_goal,
            "status": execution_record.get("status", "unknown"),
            "duration": execution_record.get("duration_seconds", 0),
            "knowledge_applied": execution_record.get("knowledge_applied", False),
            "related_rounds_used": execution_record.get("related_rounds", []),
            "risks_aware": execution_record.get("risks_aware", 0),
            "error": error
        }

        return result, report

    def _analyze_failure_and_update_knowledge(self, goal: str, error: str,
                                               knowledge: Dict):
        """分析失败并更新知识库"""
        # 可以在这里添加失败分析逻辑
        # 例如：将失败模式记录到 failures.md
        pass

    def _update_knowledge_with_success(self, goal: str, knowledge: Dict,
                                       execution_record: Dict):
        """将成功执行的经验更新到知识库"""
        if not self.knowledge_engine:
            return

        try:
            # 更新知识库
            evolution_data = {
                "current_goal": goal,
                "loop_round": 241,
                "是否完成": "已完成",
                "做了什么": f"基于知识驱动执行，成功应用 {len(knowledge.get('related_rounds', []))} 个相关历史进化经验"
            }
            self.knowledge_engine.update_knowledge_from_current_round(evolution_data)
        except Exception as e:
            print(f"更新知识库失败: {e}")

    def get_execution_statistics(self) -> Dict[str, Any]:
        """获取执行统计信息"""
        total = len(self.execution_history)
        if total == 0:
            return {
                "total_executions": 0,
                "success_rate": 0.0,
                "avg_duration": 0.0,
                "knowledge_applied_count": 0,
                "knowledge_application_rate": 0.0,
                "cached_strategies": len(self.strategy_cache.get("strategies", {}))
            }

        success_count = sum(1 for r in self.execution_history if r.get("status") == "success")
        durations = [r.get("duration_seconds", 0) for r in self.execution_history]
        knowledge_applied = sum(1 for r in self.execution_history if r.get("knowledge_applied"))

        return {
            "total_executions": total,
            "success_count": success_count,
            "success_rate": success_count / total * 100,
            "avg_duration": sum(durations) / total,
            "knowledge_applied_count": knowledge_applied,
            "knowledge_application_rate": knowledge_applied / total * 100,
            "cached_strategies": len(self.strategy_cache.get("strategies", {}))
        }

    def analyze_execution_patterns(self) -> Dict[str, Any]:
        """分析执行模式，发现优化机会"""
        patterns = {
            "high_success_patterns": [],
            "failure_patterns": [],
            "optimization_suggestions": []
        }

        # 分析成功模式
        success_records = [r for r in self.execution_history if r.get("status") == "success"]
        if success_records:
            # 成功的共同点
            goals = [r.get("goal", "") for r in success_records]
            patterns["high_success_patterns"] = {
                "count": len(success_records),
                "common_keywords": self._extract_common_keywords(goals)
            }

        # 分析失败模式
        failure_records = [r for r in self.execution_history if r.get("status") == "failed"]
        if failure_records:
            patterns["failure_patterns"] = {
                "count": len(failure_records),
                "errors": list(set([r.get("error", "")[:100] for r in failure_records]))
            }

        # 生成优化建议
        stats = self.get_execution_statistics()
        if stats["knowledge_application_rate"] < 50:
            patterns["optimization_suggestions"].append(
                "建议：在更多进化任务中应用知识驱动执行"
            )
        if stats["success_rate"] < 80:
            patterns["optimization_suggestions"].append(
                "建议：分析失败模式，优化执行策略"
            )

        return patterns


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description='智能进化知识驱动自适应执行引擎')
    parser.add_argument('command', nargs='?', default='status',
                       choices=['status', 'knowledge', 'adapt', 'execute', 'stats', 'patterns'],
                       help='要执行的命令')
    parser.add_argument('--goal', '-g', type=str, default='',
                       help='当前进化目标')
    parser.add_argument('--strategy', '-s', type=str, default='{}',
                       help='基础策略 (JSON 字符串)')

    args = parser.parse_args()

    executor = EvolutionKnowledgeDrivenExecutor()

    if args.command == 'status':
        status = {
            "version": "1.0.0",
            "knowledge_engine_loaded": executor.knowledge_engine is not None,
            "cached_strategies": len(executor.strategy_cache.get("strategies", {})),
            "execution_history_size": len(executor.execution_history)
        }
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.command == 'knowledge':
        if not args.goal:
            print("错误：knowledge 命令需要 --goal 参数")
            return
        knowledge = executor.get_relevant_knowledge(args.goal)
        print(json.dumps(knowledge, ensure_ascii=False, indent=2))

    elif args.command == 'adapt':
        if not args.goal:
            print("错误：adapt 命令需要 --goal 参数")
            return
        try:
            base_strategy = json.loads(args.strategy)
        except:
            base_strategy = {"timeout": 300, "retry": 3}

        adapted = executor.adapt_execution_strategy(args.goal, base_strategy)
        print(json.dumps(adapted, ensure_ascii=False, indent=2))

    elif args.command == 'stats':
        stats = executor.get_execution_statistics()
        print(json.dumps(stats, ensure_ascii=False, indent=2))

    elif args.command == 'patterns':
        patterns = executor.analyze_execution_patterns()
        print(json.dumps(patterns, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()