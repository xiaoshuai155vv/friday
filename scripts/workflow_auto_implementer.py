#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能工作流自动实现引擎 (Workflow Auto-Implementer)

功能：将引擎能力组合发现的工作流建议自动转化为可执行的 run_plan JSON，
并可选自动执行，形成「发现建议→自动实现→执行验证」的完整闭环。

核心能力：
1. 建议解析 - 解析工作流建议，提取关键信息
2. 计划生成 - 将建议转化为可执行的 run_plan JSON
3. 自动保存 - 保存到 assets/plans/ 目录
4. 自动执行 - 可选一键自动执行
5. 执行验证 - 执行后验证效果并反馈

区别于 workflow_auto_generator：
- workflow_auto_generator：根据用户自然语言描述生成计划
- 本引擎：将引擎能力发现的建议自动转化为计划
"""

import json
import os
import sys
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any

# 路径处理
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)


class WorkflowAutoImplementer:
    """智能工作流自动实现引擎"""

    def __init__(self):
        self.name = "Workflow Auto-Implementer"
        self.version = "1.0.0"
        self.state_file = os.path.join(PROJECT_ROOT, "runtime", "state", "workflow_auto_implementer_state.json")
        self.findings_file = os.path.join(PROJECT_ROOT, "runtime", "state", "engine_combination_recommendations.json")
        self.plans_dir = os.path.join(PROJECT_ROOT, "assets", "plans")

        # 引擎能力到动作的映射
        self.engine_action_map = {
            "health_assurance_loop": "run health_assurance_check",
            "security_monitor_engine": "run security_check",
            "proactive_operations_engine": "run proactive_operations",
            "predictive_prevention_engine": "run predictive_check",
            "self_healing_engine": "run self_healing",
            "system_dashboard_engine": "run dashboard",
            "engine_performance_monitor": "run engine_performance",
            "daemon_linkage_engine": "run daemon_linkage",
            "unified_recommender": "run recommend",
            "context_awareness_engine": "run context",
            "behavior_sequence_prediction_engine": "run predict",
            "proactive_notification_engine": "run notify",
        }

        # 组合模板
        self.combination_templates = {
            "综合系统监控闭环": {
                "description": "将健康保障与安全监控深度集成，形成综合监控→预警→自动响应的闭环",
                "steps": [
                    {"action": "run", "command": "health_assurance_loop status", "description": "检查系统健康状态"},
                    {"action": "run", "command": "security_monitor_engine check", "description": "检查安全状态"},
                    {"action": "run", "command": "system_dashboard_engine show", "description": "显示综合监控仪表盘"}
                ]
            },
            "主动预判服务链": {
                "description": "从预测到主动行动的完整服务链",
                "steps": [
                    {"action": "run", "command": "predictive_prevention_engine predict", "description": "预测潜在问题"},
                    {"action": "run", "command": "proactive_decision_action_engine decide", "description": "生成行动计划"},
                    {"action": "run", "command": "proactive_notification_engine notify", "description": "发送通知"}
                ]
            },
            "智能场景自适应": {
                "description": "基于上下文感知和行为预测，智能推荐最合适的场景计划",
                "steps": [
                    {"action": "run", "command": "context_awareness_engine status", "description": "感知当前上下文"},
                    {"action": "run", "command": "behavior_sequence_prediction_engine predict", "description": "预测用户行为"},
                    {"action": "run", "command": "unified_recommender recommend", "description": "智能推荐"}
                ]
            },
            "智能运维自愈": {
                "description": "从主动运维到自动修复的智能闭环",
                "steps": [
                    {"action": "run", "command": "proactive_operations_engine check", "description": "检查运维状态"},
                    {"action": "run", "command": "self_healing_engine diagnose", "description": "诊断问题"},
                    {"action": "run", "command": "proactive_operations_engine optimize", "description": "执行优化"}
                ]
            }
        }

        self.generated_plans = []
        self._load_state()

    def _load_state(self):
        """加载状态"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    self.generated_plans = state.get('generated_plans', [])
            except Exception:
                pass

    def _save_state(self):
        """保存状态"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump({
                'generated_plans': self.generated_plans,
                'last_updated': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)

    def load_recommendations(self) -> List[Dict]:
        """加载工作流建议"""
        recommendations = []

        # 优先从 findings 文件加载
        findings_file = os.path.join(PROJECT_ROOT, "runtime", "state", "engine_capability_findings.json")
        if os.path.exists(findings_file):
            try:
                with open(findings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    recommendations = data.get('suggestions', [])
                    if recommendations:
                        print(f"   从 findings 加载 {len(recommendations)} 条建议")
                        return recommendations
            except Exception as e:
                print(f"加载 findings 失败: {e}")

        # 回退到 recommendations 文件
        if os.path.exists(self.findings_file):
            try:
                with open(self.findings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    recommendations = data.get('suggestions', [])
            except Exception as e:
                print(f"加载建议失败: {e}")
        return recommendations

    def parse_recommendation(self, recommendation: Dict) -> Dict:
        """解析工作流建议，提取关键信息"""
        title = recommendation.get('title', '')
        description = recommendation.get('description', '')
        action = recommendation.get('action', '')
        priority = recommendation.get('priority', '中')

        # 提取组合名称
        combination_name = ""
        if '建议实现：' in title:
            combination_name = title.replace('建议实现：', '')

        # 查找匹配的模板
        template = None
        for name, tpl in self.combination_templates.items():
            if name in combination_name or name in description:
                template = tpl
                break

        return {
            "name": combination_name,
            "description": description,
            "action": action,
            "priority": priority,
            "template": template
        }

    def generate_plan_json(self, parsed: Dict) -> Dict:
        """将解析后的建议转化为 run_plan JSON"""
        name = parsed.get('name', 'unnamed_workflow')
        description = parsed.get('description', '')
        template = parsed.get('template')

        # 生成 plan 结构
        if template:
            plan = {
                "name": name,
                "description": description,
                "trigger": f"auto:{name.replace(' ', '_').lower()}",
                "steps": template.get('steps', [])
            }
        else:
            # 默认计划：只包含描述，无实际步骤
            plan = {
                "name": name,
                "description": description,
                "trigger": f"auto:{name.replace(' ', '_').lower()}",
                "steps": [
                    {"action": "log", "message": f"工作流「{name}」需要进一步实现", "description": "记录待实现的工作流"}
                ]
            }

        return plan

    def save_plan(self, plan: Dict) -> str:
        """保存计划到 assets/plans/ 目录"""
        os.makedirs(self.plans_dir, exist_ok=True)

        # 生成文件名
        safe_name = plan['name'].replace(' ', '_').replace('：', '').replace(':', '')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"auto_{safe_name}_{timestamp}.json"
        filepath = os.path.join(self.plans_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)

        return filepath

    def execute_plan(self, plan_path: str) -> Dict:
        """执行生成的 plan"""
        print(f"\n=== 执行计划: {plan_path} ===")

        try:
            # 使用 do.py 执行 plan
            cmd = [sys.executable, os.path.join(SCRIPT_DIR, "do.py"), "run_plan", plan_path]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "执行超时",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "returncode": -1
            }

    def run_auto_implement(self, auto_execute: bool = False) -> Dict:
        """运行自动实现流程"""
        print("\n" + "="*60)
        print("智能工作流自动实现引擎")
        print("="*60 + "\n")

        # 1. 加载工作流建议
        print("1. 加载工作流建议...")
        recommendations = self.load_recommendations()

        if not recommendations:
            print("未找到工作流建议，请先运行 engine_capability_discovery.py")
            return {
                "success": False,
                "message": "未找到工作流建议",
                "plans_generated": 0
            }

        print(f"   找到 {len(recommendations)} 条工作流建议")

        # 2. 解析并生成计划
        print("\n2. 解析建议并生成计划...")
        plans_generated = []

        for rec in recommendations:
            parsed = self.parse_recommendation(rec)
            plan = self.generate_plan_json(parsed)
            plan_path = self.save_plan(plan)
            plans_generated.append({
                "name": plan['name'],
                "path": plan_path,
                "description": plan['description']
            })
            print(f"   [OK] 生成: {plan['name']} -> {plan_path}")

        self.generated_plans = plans_generated
        self._save_state()

        # 3. 可选：自动执行
        results = []
        if auto_execute and plans_generated:
            print("\n3. 自动执行计划...")
            for plan_info in plans_generated:
                result = self.execute_plan(plan_info['path'])
                results.append({
                    "plan": plan_info['name'],
                    "path": plan_info['path'],
                    "result": result
                })
                status = "成功" if result.get('success') else "失败"
                print(f"   [{status}] {plan_info['name']}")

        # 4. 返回结果
        result = {
            "success": True,
            "message": f"成功生成 {len(plans_generated)} 个工作流计划",
            "recommendations_loaded": len(recommendations),
            "plans_generated": len(plans_generated),
            "plans": plans_generated,
            "auto_executed": auto_execute,
            "execution_results": results if results else None,
            "timestamp": datetime.now().isoformat()
        }

        print("\n" + "="*60)
        print("自动实现完成")
        print("="*60)
        print(f"建议加载: {result['recommendations_loaded']}")
        print(f"计划生成: {result['plans_generated']}")
        if auto_execute:
            print(f"自动执行: {'是' if result['auto_executed'] else '否'}")
            if results:
                success_count = sum(1 for r in results if r['result'].get('success'))
                print(f"执行成功: {success_count}/{len(results)}")

        return result

    def get_status(self) -> Dict:
        """获取引擎状态"""
        return {
            "name": self.name,
            "version": self.version,
            "plans_generated": len(self.generated_plans),
            "last_updated": os.path.getmtime(self.state_file) if os.path.exists(self.state_file) else None
        }

    def get_generated_plans(self) -> List[Dict]:
        """获取已生成的计划"""
        return self.generated_plans


def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser(description='智能工作流自动实现引擎')
    parser.add_argument('command', nargs='?', default='run',
                        choices=['run', 'status', 'list', 'execute'],
                        help='要执行的命令')
    parser.add_argument('--execute', '-e', action='store_true',
                        help='自动执行生成的计划')
    parser.add_argument('--output', '-o', help='输出文件路径 (JSON)')

    args = parser.parse_args()

    implementer = WorkflowAutoImplementer()

    if args.command == 'run':
        result = implementer.run_auto_implement(auto_execute=args.execute)

        if args.output:
            os.makedirs(os.path.dirname(args.output), exist_ok=True)
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n结果已保存到: {args.output}")

    elif args.command == 'status':
        status = implementer.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.command == 'list':
        plans = implementer.get_generated_plans()
        print(json.dumps(plans, ensure_ascii=False, indent=2))

    elif args.command == 'execute':
        # 执行所有已生成的计划
        plans = implementer.get_generated_plans()
        if not plans:
            print("没有已生成的计划，请先运行 'run' 命令")
            return

        print(f"将执行 {len(plans)} 个计划...")
        for plan_info in plans:
            result = implementer.execute_plan(plan_info['path'])
            status = "成功" if result.get('success') else "失败"
            print(f"  [{status}] {plan_info['name']}")


if __name__ == '__main__':
    main()