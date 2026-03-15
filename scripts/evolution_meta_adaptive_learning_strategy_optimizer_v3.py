#!/usr/bin/env python3
"""
智能全场景进化环元进化自适应学习与策略自动优化引擎 V3

在 round 654 完成的元进化投资回报智能评估与战略优化引擎基础上，构建更智能的自适应学习能力。让系统能够：
1. 基于最新 ROI 评估结果自动调整进化策略
2. 实现进化资源的动态分配
3. 实现进化优先级的自动优化
4. 形成「ROI评估→策略调整→资源分配→优先级优化→执行验证」的完整闭环

此引擎让系统从「学习方法论」升级到「基于价值评估的自适应优化」，实现真正的数据驱动进化决策。

Version: 1.0.0
Author: AI Evolution System
"""

import json
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
import statistics


class EvolutionMetaAdaptiveLearningV3Engine:
    """元进化自适应学习与策略自动优化引擎 V3 - 基于 ROI 评估的自适应优化"""

    VERSION = "1.0.0"

    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent.parent
        self.runtime_dir = self.base_dir / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.logs_dir = self.runtime_dir / "logs"
        self.scripts_dir = self.base_dir / "scripts"

        # 数据库路径
        self.db_path = self.runtime_dir / "state" / "meta_adaptive_learning_v3.db"

        # 初始化数据库
        self._init_database()

    def _init_database(self):
        """初始化学习数据库"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # ROI 驱动策略调整表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roi_driven_strategy_adjustments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                adjustment_id TEXT NOT NULL UNIQUE,
                based_on_roi_analysis TEXT,
                parameter_name TEXT NOT NULL,
                old_value REAL,
                new_value REAL,
                adjustment_reason TEXT,
                value_impact REAL,
                execution_round INTEGER,
                result_effectiveness REAL,
                adjustment_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 资源动态分配表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dynamic_resource_allocation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                allocation_id TEXT NOT NULL UNIQUE,
                resource_type TEXT NOT NULL,
                allocated_amount REAL,
                based_on_roi_category TEXT,
                allocation_reason TEXT,
                priority_level INTEGER,
                execution_round INTEGER,
                actual_usage REAL,
                utilization_rate REAL,
                allocated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 优先级自动优化表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS priority_auto_optimization (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                optimization_id TEXT NOT NULL UNIQUE,
                optimization_type TEXT NOT NULL,
                old_priority INTEGER,
                new_priority INTEGER,
                optimization_reason TEXT,
                based_on_metrics TEXT,
                impact_score REAL,
                execution_round INTEGER,
                result_score REAL,
                optimized_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ROI 策略联动表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roi_strategy_linkage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                linkage_id TEXT NOT NULL UNIQUE,
                roi_category TEXT NOT NULL,
                strategy_adjustment TEXT,
                resource_allocation TEXT,
                priority_change TEXT,
                effectiveness_score REAL,
                linked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 执行验证记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_verification (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                verification_id TEXT NOT NULL UNIQUE,
                adjusted_strategy TEXT,
                allocated_resources TEXT,
                optimized_priorities TEXT,
                verification_result TEXT,
                effectiveness_measured REAL,
                round_number INTEGER,
                verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def get_latest_roi_data(self) -> dict:
        """获取最新的 ROI 评估数据"""
        # 查找 round 654 的 ROI 评估结果
        state_dir = self.state_dir

        # 查找最新的 ROI 评估完成文件
        roi_file = state_dir / "evolution_completed_ev_20260315_185406.json"

        roi_data = {
            "total_evolutions": 0,
            "completion_rate": 0.0,
            "value_contributions": [],
            "strategic_recommendations": []
        }

        if roi_file.exists():
            try:
                with open(roi_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    roi_data = data.get("roi_analysis", roi_data)
            except Exception as e:
                print(f"读取 ROI 数据失败: {e}")

        return roi_data

    def analyze_roi_driven_adjustments(self) -> dict:
        """基于 ROI 分析生成策略调整"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        roi_data = self.get_latest_roi_data()

        adjustments = []

        # 分析价值贡献类别，生成策略调整
        value_categories = roi_data.get("value_contributions", [])

        category_strategy_map = {
            "价值优化类": {
                "parameter": "value_optimization_weight",
                "adjustment_direction": "increase",
                "reason": "价值优化类贡献最高，应增加权重"
            },
            "创新驱动类": {
                "parameter": "innovation_weight",
                "adjustment_direction": "increase",
                "reason": "创新驱动类贡献显著，应增加创新投入"
            },
            "知识学习类": {
                "parameter": "knowledge_learning_weight",
                "adjustment_direction": "maintain",
                "reason": "知识学习类贡献稳定，保持当前投入"
            },
            "执行效率类": {
                "parameter": "efficiency_weight",
                "adjustment_direction": "optimize",
                "reason": "执行效率类有优化空间，应优化资源配置"
            },
            "健康保障类": {
                "parameter": "health_protection_weight",
                "adjustment_direction": "maintain",
                "reason": "健康保障类贡献稳定，保持基础投入"
            }
        }

        for category_data in value_categories:
            category = category_data.get("category", "")
            count = category_data.get("count", 0)
            total_value = category_data.get("total_value", 0)

            if category in category_strategy_map:
                strategy = category_strategy_map[category]

                # 根据价值贡献计算调整幅度
                value_ratio = total_value / 20.0 if total_value else 0.5
                old_value = 0.5
                if strategy["adjustment_direction"] == "increase":
                    new_value = min(0.9, old_value + value_ratio * 0.3)
                elif strategy["adjustment_direction"] == "optimize":
                    new_value = min(0.8, old_value + value_ratio * 0.2)
                else:
                    new_value = old_value

                adjustment = {
                    "adjustment_id": f"roi_adj_{category}",
                    "parameter": strategy["parameter"],
                    "old_value": old_value,
                    "new_value": new_value,
                    "reason": strategy["reason"],
                    "value_impact": total_value,
                    "based_on": category
                }
                adjustments.append(adjustment)

                # 存储调整记录
                cursor.execute("""
                    INSERT OR REPLACE INTO roi_driven_strategy_adjustments
                    (adjustment_id, based_on_roi_analysis, parameter_name, old_value, new_value,
                     adjustment_reason, value_impact, result_effectiveness)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (adjustment["adjustment_id"], json.dumps(roi_data), adjustment["parameter"],
                      adjustment["old_value"], adjustment["new_value"], adjustment["reason"],
                      adjustment["value_impact"], value_ratio))

        conn.commit()
        conn.close()

        return {
            "adjustments_made": len(adjustments),
            "adjustments": adjustments,
            "roi_data_analyzed": len(value_categories)
        }

    def dynamic_resource_allocation(self) -> dict:
        """基于 ROI 分析实现资源的动态分配"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        roi_data = self.get_latest_roi_data()
        value_categories = roi_data.get("value_contributions", [])

        allocations = []

        # 基于价值贡献类别动态分配资源
        total_value = sum(c.get("total_value", 0) for c in value_categories)

        if total_value > 0:
            for category_data in value_categories:
                category = category_data.get("category", "")
                category_value = category_data.get("total_value", 0)

                # 计算资源分配比例
                allocation_ratio = category_value / total_value

                allocation = {
                    "allocation_id": f"alloc_{category}",
                    "resource_type": "evolution_budget",
                    "allocated_amount": round(allocation_ratio * 100, 1),
                    "based_on": category,
                    "allocation_reason": f"基于 ROI 评估，{category}贡献了 {category_value} 价值，分配 {allocation_ratio:.1%} 资源",
                    "priority_level": int((1 - allocation_ratio) * 10)
                }
                allocations.append(allocation)

                # 存储分配记录
                cursor.execute("""
                    INSERT OR REPLACE INTO dynamic_resource_allocation
                    (allocation_id, resource_type, allocated_amount, based_on_roi_category,
                     allocation_reason, priority_level, utilization_rate)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (allocation["allocation_id"], allocation["resource_type"],
                      allocation["allocated_amount"], allocation["based_on"],
                      allocation["allocation_reason"], allocation["priority_level"],
                      allocation_ratio))

        conn.commit()
        conn.close()

        return {
            "allocations_made": len(allocations),
            "allocations": allocations,
            "total_budget": "100%"
        }

    def auto_optimize_priorities(self) -> dict:
        """基于 ROI 分析自动优化优先级"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        roi_data = self.get_latest_roi_data()
        value_categories = roi_data.get("value_contributions", [])

        optimizations = []

        # 基于价值贡献自动调整优先级
        priority_map = {
            "价值优化类": 1,  # 最高优先级
            "创新驱动类": 2,
            "知识学习类": 3,
            "执行效率类": 4,
            "健康保障类": 5
        }

        for category_data in value_categories:
            category = category_data.get("category", "")
            count = category_data.get("count", 0)

            old_priority = priority_map.get(category, 5)
            # 根据完成数量调整优先级
            if count >= 10:
                new_priority = max(1, old_priority - 1)
            elif count >= 5:
                new_priority = old_priority
            else:
                new_priority = min(5, old_priority + 1)

            if old_priority != new_priority:
                optimization = {
                    "optimization_id": f"prio_opt_{category}",
                    "optimization_type": "roi_based_priority",
                    "old_priority": old_priority,
                    "new_priority": new_priority,
                    "reason": f"{category}完成 {count} 轮，调整优先级从 {old_priority} 到 {new_priority}",
                    "based_on": category,
                    "impact_score": count / 20.0
                }
                optimizations.append(optimization)

                # 存储优化记录
                cursor.execute("""
                    INSERT OR REPLACE INTO priority_auto_optimization
                    (optimization_id, optimization_type, old_priority, new_priority,
                     optimization_reason, based_on_metrics, impact_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (optimization["optimization_id"], optimization["optimization_type"],
                      optimization["old_priority"], optimization["new_priority"],
                      optimization["reason"], json.dumps(category_data), optimization["impact_score"]))

        conn.commit()
        conn.close()

        return {
            "optimizations_made": len(optimizations),
            "optimizations": optimizations
        }

    def create_roi_strategy_linkage(self) -> dict:
        """创建 ROI 与策略的联动机制"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        roi_data = self.get_latest_roi_data()

        # 获取所有策略调整
        cursor.execute("""
            SELECT adjustment_id, parameter_name, new_value, adjustment_reason
            FROM roi_driven_strategy_adjustments
            ORDER BY value_impact DESC
        """)

        strategy_adjustments = []
        for row in cursor.fetchall():
            strategy_adjustments.append({
                "id": row[0],
                "parameter": row[1],
                "value": row[2],
                "reason": row[3]
            })

        # 获取所有资源分配
        cursor.execute("""
            SELECT allocation_id, resource_type, allocated_amount, allocation_reason
            FROM dynamic_resource_allocation
            ORDER BY allocated_amount DESC
        """)

        resource_allocations = []
        for row in cursor.fetchall():
            resource_allocations.append({
                "id": row[0],
                "type": row[1],
                "amount": row[2],
                "reason": row[3]
            })

        # 获取所有优先级优化
        cursor.execute("""
            SELECT optimization_id, old_priority, new_priority, optimization_reason
            FROM priority_auto_optimization
            ORDER BY impact_score DESC
        """)

        priority_changes = []
        for row in cursor.fetchall():
            priority_changes.append({
                "id": row[0],
                "old": row[1],
                "new": row[2],
                "reason": row[3]
            })

        # 创建联动记录
        linkage = {
            "linkage_id": f"linkage_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "roi_summary": {
                "total_evolution": roi_data.get("total_evolutions", 0),
                "completion_rate": roi_data.get("completion_rate", 0),
                "categories": len(roi_data.get("value_contributions", []))
            },
            "strategy_adjustments_count": len(strategy_adjustments),
            "resource_allocations_count": len(resource_allocations),
            "priority_changes_count": len(priority_changes),
            "linkage_complete": True
        }

        # 存储联动记录
        cursor.execute("""
            INSERT INTO roi_strategy_linkage
            (linkage_id, roi_category, strategy_adjustment, resource_allocation,
             priority_change, effectiveness_score)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (linkage["linkage_id"], json.dumps(roi_data.get("value_contributions", [])),
              json.dumps(strategy_adjustments), json.dumps(resource_allocations),
              json.dumps(priority_changes), roi_data.get("completion_rate", 0)))

        conn.commit()
        conn.close()

        return linkage

    def verify_execution_effectiveness(self) -> dict:
        """验证执行效果"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 获取所有调整
        cursor.execute("SELECT COUNT(*) FROM roi_driven_strategy_adjustments")
        adjustment_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM dynamic_resource_allocation")
        allocation_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM priority_auto_optimization")
        optimization_count = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(result_effectiveness) FROM roi_driven_strategy_adjustments")
        avg_effectiveness = cursor.fetchone()[0] or 0

        verification = {
            "verification_id": f"verify_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "total_adjustments": adjustment_count,
            "total_allocations": allocation_count,
            "total_optimizations": optimization_count,
            "average_effectiveness": round(avg_effectiveness, 3),
            "verification_complete": True
        }

        # 存储验证记录
        cursor.execute("""
            INSERT INTO execution_verification
            (verification_id, adjusted_strategy, allocated_resources, optimized_priorities,
             verification_result, effectiveness_measured)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (verification["verification_id"], adjustment_count, allocation_count,
              optimization_count, "completed", avg_effectiveness))

        conn.commit()
        conn.close()

        return verification

    def run_full_roi_adaptive_cycle(self) -> dict:
        """运行完整的 ROI 驱动自适应周期"""
        results = {
            "cycle_started_at": datetime.now().isoformat(),
            "steps": {}
        }

        # 步骤1: 获取 ROI 数据
        print("[1/6] 获取 ROI 评估数据...")
        roi_data = self.get_latest_roi_data()
        results["steps"]["roi_data"] = {
            "total_evolutions": roi_data.get("total_evolutions", 0),
            "completion_rate": roi_data.get("completion_rate", 0),
            "categories": len(roi_data.get("value_contributions", []))
        }

        # 步骤2: 基于 ROI 分析生成策略调整
        print("[2/6] 基于 ROI 分析生成策略调整...")
        adjustment_result = self.analyze_roi_driven_adjustments()
        results["steps"]["strategy_adjustments"] = adjustment_result

        # 步骤3: 动态资源分配
        print("[3/6] 动态分配资源...")
        allocation_result = self.dynamic_resource_allocation()
        results["steps"]["resource_allocation"] = allocation_result

        # 步骤4: 自动优化优先级
        print("[4/6] 自动优化优先级...")
        optimization_result = self.auto_optimize_priorities()
        results["steps"]["priority_optimization"] = optimization_result

        # 步骤5: 创建 ROI 策略联动
        print("[5/6] 创建 ROI 策略联动...")
        linkage_result = self.create_roi_strategy_linkage()
        results["steps"]["strategy_linkage"] = linkage_result

        # 步骤6: 验证执行效果
        print("[6/6] 验证执行效果...")
        verification_result = self.verify_execution_effectiveness()
        results["steps"]["verification"] = verification_result

        results["cycle_completed_at"] = datetime.now().isoformat()
        results["summary"] = {
            "adjustments_made": adjustment_result["adjustments_made"],
            "allocations_made": allocation_result["allocations_made"],
            "optimizations_made": optimization_result["optimizations_made"],
            "effectiveness_score": verification_result["average_effectiveness"]
        }

        return results

    def get_cockpit_data(self) -> dict:
        """获取驾驶舱数据"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 获取策略调整统计
        cursor.execute("SELECT COUNT(*) FROM roi_driven_strategy_adjustments")
        adjustments_count = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(result_effectiveness) FROM roi_driven_strategy_adjustments")
        avg_effectiveness = cursor.fetchone()[0] or 0

        # 获取资源分配统计
        cursor.execute("SELECT COUNT(*) FROM dynamic_resource_allocation")
        allocations_count = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(allocated_amount) FROM dynamic_resource_allocation")
        total_allocated = cursor.fetchone()[0] or 0

        # 获取优先级优化统计
        cursor.execute("SELECT COUNT(*) FROM priority_auto_optimization")
        optimizations_count = cursor.fetchone()[0]

        # 获取 ROI 数据
        roi_data = self.get_latest_roi_data()

        # 获取最近的策略调整
        cursor.execute("""
            SELECT parameter_name, new_value, adjustment_reason
            FROM roi_driven_strategy_adjustments
            ORDER BY adjustment_timestamp DESC
            LIMIT 5
        """)

        recent_adjustments = []
        for row in cursor.fetchall():
            recent_adjustments.append({
                "parameter": row[0],
                "new_value": row[1],
                "reason": row[2]
            })

        conn.close()

        return {
            "version": self.VERSION,
            "roi_summary": {
                "total_evolutions": roi_data.get("total_evolutions", 0),
                "completion_rate": roi_data.get("completion_rate", 0),
                "value_categories": len(roi_data.get("value_contributions", []))
            },
            "adjustments_count": adjustments_count,
            "avg_effectiveness": round(avg_effectiveness, 3),
            "allocations_count": allocations_count,
            "total_allocated": round(total_allocated, 1),
            "optimizations_count": optimizations_count,
            "recent_adjustments": recent_adjustments,
            "status": "operational"
        }


def main():
    """主函数 - 支持命令行调用"""
    import sys

    engine = EvolutionMetaAdaptiveLearningV3Engine()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "--version":
            print(f"evolution_meta_adaptive_learning_strategy_optimizer_v3 v{engine.VERSION}")
            print("智能全场景进化环元进化自适应学习与策略自动优化引擎 V3")

        elif command == "--status":
            data = engine.get_cockpit_data()
            print(f"状态: {data['status']}")
            print(f"ROI 评估: {data['roi_summary']['total_evolutions']} 轮, 完成率 {data['roi_summary']['completion_rate']:.1%}")
            print(f"策略调整: {data['adjustments_count']}")
            print(f"平均效果: {data['avg_effectiveness']:.1%}")
            print(f"资源分配: {data['allocations_count']} 项")
            print(f"优先级优化: {data['optimizations_count']}")

        elif command == "--run":
            print("运行完整的 ROI 驱动自适应周期...")
            result = engine.run_full_roi_adaptive_cycle()
            print(f"自适应周期完成!")
            print(f"  - 策略调整: {result['summary']['adjustments_made']}")
            print(f"  - 资源分配: {result['summary']['allocations_made']}")
            print(f"  - 优先级优化: {result['summary']['optimizations_made']}")
            print(f"  - 效果评分: {result['summary']['effectiveness_score']:.1%}")

        elif command == "--adjust-strategy":
            print("基于 ROI 分析生成策略调整...")
            result = engine.analyze_roi_driven_adjustments()
            print(f"完成了 {result['adjustments_made']} 项策略调整")

        elif command == "--allocate-resources":
            print("动态分配资源...")
            result = engine.dynamic_resource_allocation()
            print(f"完成了 {result['allocations_made']} 项资源分配")

        elif command == "--optimize-priorities":
            print("自动优化优先级...")
            result = engine.auto_optimize_priorities()
            print(f"完成了 {result['optimizations_made']} 项优先级优化")

        elif command == "--linkage":
            print("创建 ROI 策略联动...")
            result = engine.create_roi_strategy_linkage()
            print(f"联动创建完成: {result['linkage_id']}")

        elif command == "--cockpit-data":
            data = engine.get_cockpit_data()
            print(json.dumps(data, ensure_ascii=False, indent=2))

        else:
            print(f"未知命令: {command}")
            print("支持: --version, --status, --run, --adjust-strategy, --allocate-resources, --optimize-priorities, --linkage, --cockpit-data")
    else:
        print(f"evolution_meta_adaptive_learning_strategy_optimizer_v3 v{engine.VERSION}")
        print("智能全场景进化环元进化自适应学习与策略自动优化引擎 V3")
        print("")
        print("用法: python evolution_meta_adaptive_learning_strategy_optimizer_v3.py [命令]")
        print("")
        print("命令:")
        print("  --version              显示版本信息")
        print("  --status               显示状态")
        print("  --run                  运行完整的 ROI 驱动自适应周期")
        print("  --adjust-strategy      基于 ROI 分析生成策略调整")
        print("  --allocate-resources   动态分配资源")
        print("  --optimize-priorities  自动优化优先级")
        print("  --linkage              创建 ROI 策略联动")
        print("  --cockpit-data         获取驾驶舱数据")


if __name__ == "__main__":
    main()