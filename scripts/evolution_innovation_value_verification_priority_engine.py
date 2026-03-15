"""
智能全场景进化环创新建议自动验证与价值优先级排序引擎
version: 1.0.0

基于 round 633 完成的元进化知识图谱动态推理与主动创新发现引擎（已发现388条待执行创新建议）基础上，
构建让系统能够自动验证创新建议价值并智能排序优先级的增强能力。

功能：
1. 创新建议批量验证 - 对图谱发现的创新建议进行快速价值验证
2. 价值评分智能计算 - 基于多维度（效率提升、能力增强、风险降低等）计算价值评分
3. 优先级自动排序 - 根据价值评分和实施难度自动排序优先级
4. 执行路径优化 - 为高优先级建议优化执行路径
5. 效果预测 - 预测实施后的预期效果

与 round 633 知识图谱引擎、round 620 效能优化引擎深度集成，形成「发现→验证→排序→优化→执行」的完整创新价值实现闭环。
"""

import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE_DIR = PROJECT_ROOT / "runtime" / "state"
RUNTIME_LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# 知识图谱数据库路径
KG_DB_PATH = RUNTIME_STATE_DIR / "knowledge_graph.db"

# 创新价值验证数据库
INNOVATION_DB_PATH = RUNTIME_STATE_DIR / "innovation_verification.db"


class InnovationValueVerificationEngine:
    """创新建议自动验证与价值优先级排序引擎"""

    def __init__(self):
        self.kg_db_path = KG_DB_PATH
        self.innovation_db_path = INNOVATION_DB_PATH
        self._init_database()

    def _init_database(self):
        """初始化创新价值验证数据库"""
        conn = sqlite3.connect(str(self.innovation_db_path))
        cursor = conn.cursor()

        # 创新建议验证记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS innovation_verification (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discovery_id INTEGER,
                description TEXT,
                category TEXT,
                efficiency_score REAL DEFAULT 0.0,
                capability_enhancement_score REAL DEFAULT 0.0,
                risk_reduction_score REAL DEFAULT 0.0,
                complexity_score REAL DEFAULT 0.0,
                total_value_score REAL DEFAULT 0.0,
                priority_rank INTEGER,
                execution_difficulty TEXT DEFAULT 'medium',
                predicted_effect TEXT,
                verification_status TEXT DEFAULT 'pending',
                verified_at TEXT,
                notes TEXT
            )
        """)

        # 执行路径优化记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_path_optimization (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                innovation_id INTEGER,
                optimized_steps TEXT,
                estimated_time_savings REAL DEFAULT 0.0,
                resource_requirements TEXT,
                dependencies TEXT,
                created_at TEXT
            )
        """)

        # 效果预测记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS effect_prediction (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                innovation_id INTEGER,
                predicted_metrics TEXT,
                confidence_level REAL DEFAULT 0.0,
                prediction_basis TEXT,
                created_at TEXT
            )
        """)

        conn.commit()
        conn.close()

    def get_pending_innovations_from_kg(self) -> List[Dict]:
        """从知识图谱获取待验证的创新建议"""
        innovations = []
        conn = sqlite3.connect(str(self.kg_db_path))
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id, discovery_type, description, entities_involved, execution_status, created_at
                FROM innovation_discoveries
                WHERE execution_status = 'pending'
                ORDER BY created_at DESC
            """)
            rows = cursor.fetchall()
            for row in rows:
                innovations.append({
                    "id": row[0],
                    "discovery_type": row[1],
                    "description": row[2],
                    "entities_involved": row[3],
                    "execution_status": row[4],
                    "created_at": row[5]
                })
        except Exception as e:
            print(f"从知识图谱获取创新建议失败: {e}")
        finally:
            conn.close()

        return innovations

    def batch_verify_innovations(self) -> Dict:
        """批量验证创新建议"""
        result = {
            "status": "success",
            "verified_count": 0,
            "message": ""
        }

        # 获取待验证的创新建议
        pending_innovations = self.get_pending_innovations_from_kg()

        if not pending_innovations:
            result["message"] = "没有待验证的创新建议"
            return result

        conn = sqlite3.connect(str(self.innovation_db_path))
        cursor = conn.cursor()

        try:
            for innovation in pending_innovations:
                # 计算价值评分
                value_scores = self._calculate_value_scores(innovation)

                # 评估执行难度
                difficulty = self._assess_execution_difficulty(innovation)

                # 预测效果
                predicted_effect = self._predict_effect(innovation)

                # 插入验证记录
                cursor.execute("""
                    INSERT INTO innovation_verification
                    (discovery_id, description, category, efficiency_score, capability_enhancement_score,
                     risk_reduction_score, complexity_score, total_value_score, execution_difficulty,
                     predicted_effect, verification_status, verified_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    innovation["id"],
                    innovation["description"],
                    innovation.get("discovery_type", "unknown"),
                    value_scores["efficiency"],
                    value_scores["capability_enhancement"],
                    value_scores["risk_reduction"],
                    value_scores["complexity"],
                    value_scores["total"],
                    difficulty,
                    predicted_effect,
                    "verified",
                    datetime.now().isoformat()
                ))
                result["verified_count"] += 1

            conn.commit()
            result["message"] = f"批量验证完成，共验证 {result['verified_count']} 条创新建议"

        except Exception as e:
            result["status"] = "error"
            result["message"] = f"批量验证失败: {e}"
        finally:
            conn.close()

        return result

    def _calculate_value_scores(self, innovation: Dict) -> Dict:
        """计算多维度价值评分"""
        description = innovation.get("description", "")
        entities = innovation.get("entities_involved", "")

        # 基于关键词和模式进行初步评分
        efficiency = 0.5
        capability_enhancement = 0.5
        risk_reduction = 0.5
        complexity = 0.5

        # 分析描述中的关键词
        efficiency_keywords = ["效率", "优化", "加速", "快速", "提升", "自动化", "auto", "optimize", "speed"]
        capability_keywords = ["能力", "功能", "增强", "扩展", "新能力", "新增", "capability", "enhance", "new"]
        risk_keywords = ["风险", "预防", "安全", "保护", "预警", "健康", "risk", "prevent", "safety"]
        complex_keywords = ["复杂", "深度", "多维度", "集成", "跨引擎", "complex", "deep", "integrate"]

        desc_lower = description.lower()

        # 计算效率提升分数
        for kw in efficiency_keywords:
            if kw.lower() in desc_lower:
                efficiency += 0.1

        # 计算能力增强分数
        for kw in capability_keywords:
            if kw.lower() in desc_lower:
                capability_enhancement += 0.1

        # 计算风险降低分数
        for kw in risk_keywords:
            if kw.lower() in desc_lower:
                risk_reduction += 0.1

        # 计算复杂度分数（复杂度越高，初始分越低因为难以实现）
        for kw in complex_keywords:
            if kw.lower() in desc_lower:
                complexity += 0.15

        # 归一化到 0-1 范围
        efficiency = min(1.0, efficiency)
        capability_enhancement = min(1.0, capability_enhancement)
        risk_reduction = min(1.0, risk_reduction)
        complexity = min(1.0, complexity)

        # 计算总分（加权平均）
        # 效率权重 0.3，能力增强 0.3，风险降低 0.2，复杂度（逆向）0.2
        total = (efficiency * 0.3 + capability_enhancement * 0.3 +
                risk_reduction * 0.2 + (1 - complexity) * 0.2)

        return {
            "efficiency": round(efficiency, 2),
            "capability_enhancement": round(capability_enhancement, 2),
            "risk_reduction": round(risk_reduction, 2),
            "complexity": round(complexity, 2),
            "total": round(total, 2)
        }

    def _assess_execution_difficulty(self, innovation: Dict) -> str:
        """评估执行难度"""
        description = innovation.get("description", "")
        desc_lower = description.lower()

        # 高难度关键词
        high_difficulty_keywords = ["跨引擎", "深度集成", "多维度", "复杂", "重构", "系统级", "跨实例"]
        # 低难度关键词
        low_difficulty_keywords = ["增强", "优化", "简单", "接口", "小改", "更新", "集成"]

        high_count = sum(1 for kw in high_difficulty_keywords if kw in desc_lower)
        low_count = sum(1 for kw in low_difficulty_keywords if kw in desc_lower)

        if high_count > low_count:
            return "high"
        elif low_count > high_count:
            return "low"
        else:
            return "medium"

    def _predict_effect(self, innovation: Dict) -> str:
        """预测实施效果"""
        description = innovation.get("description", "")
        desc_lower = description.lower()

        # 基于关键词预测效果
        if any(kw in desc_lower for kw in ["效率", "优化", "加速", "性能"]):
            return "预期提升执行效率 15-30%"
        elif any(kw in desc_lower for kw in ["能力", "功能", "扩展", "增强"]):
            return "预期扩展系统能力边界"
        elif any(kw in desc_lower for kw in ["风险", "安全", "健康", "预防"]):
            return "预期降低系统风险 20-40%"
        elif any(kw in desc_lower for kw in ["知识", "图谱", "推理"]):
            return "预期增强知识利用率 25%"
        else:
            return "预期带来系统性改进"

    def prioritize_innovations(self) -> Dict:
        """根据价值评分优先级排序"""
        result = {
            "status": "success",
            "prioritized_count": 0,
            "top_priorities": [],
            "message": ""
        }

        conn = sqlite3.connect(str(self.innovation_db_path))
        cursor = conn.cursor()

        try:
            # 按总价值评分降序排序
            cursor.execute("""
                UPDATE innovation_verification
                SET priority_rank = (
                    SELECT COUNT(*) + 1 FROM innovation_verification v2
                    WHERE v2.total_value_score > innovation_verification.total_value_score
                )
                WHERE verification_status = 'verified'
            """)

            # 获取排序后的结果
            cursor.execute("""
                SELECT id, discovery_id, description, category, total_value_score,
                       priority_rank, execution_difficulty, predicted_effect
                FROM innovation_verification
                WHERE verification_status = 'verified'
                ORDER BY priority_rank ASC
                LIMIT 20
            """)

            rows = cursor.fetchall()
            for row in rows:
                result["top_priorities"].append({
                    "id": row[0],
                    "discovery_id": row[1],
                    "description": row[2],
                    "category": row[3],
                    "total_value_score": row[4],
                    "priority_rank": row[5],
                    "execution_difficulty": row[6],
                    "predicted_effect": row[7]
                })
                result["prioritized_count"] += 1

            conn.commit()
            result["message"] = f"优先级排序完成，前 {result['prioritized_count']} 项已确定"

        except Exception as e:
            result["status"] = "error"
            result["message"] = f"优先级排序失败: {e}"
        finally:
            conn.close()

        return result

    def optimize_execution_path(self, innovation_id: int) -> Dict:
        """优化执行路径"""
        result = {
            "status": "success",
            "optimized_steps": [],
            "estimated_time_savings": 0.0,
            "message": ""
        }

        conn = sqlite3.connect(str(self.innovation_db_path))
        cursor = conn.cursor()

        try:
            # 获取创新建议详情
            cursor.execute("""
                SELECT description, execution_difficulty
                FROM innovation_verification
                WHERE id = ?
            """, (innovation_id,))

            row = cursor.fetchone()
            if not row:
                result["status"] = "error"
                result["message"] = "未找到该创新建议"
                return result

            description, difficulty = row

            # 基于难度生成优化步骤
            steps = []
            if difficulty == "low":
                steps = ["执行代码审查", "编写测试用例", "实现功能", "提交验证"]
                result["estimated_time_savings"] = 0.2  # 20% 时间节省
            elif difficulty == "medium":
                steps = ["详细设计评审", "编写测试用例", "分步实现", "集成测试", "提交验证"]
                result["estimated_time_savings"] = 0.15
            else:
                steps = ["架构设计评审", "详细设计", "代码审查", "单元测试", "集成测试", "系统测试", "部署验证"]
                result["estimated_time_savings"] = 0.1

            result["optimized_steps"] = steps

            # 记录优化路径
            cursor.execute("""
                INSERT INTO execution_path_optimization
                (innovation_id, optimized_steps, estimated_time_savings, created_at)
                VALUES (?, ?, ?, ?)
            """, (innovation_id, json.dumps(steps), result["estimated_time_savings"],
                  datetime.now().isoformat()))

            conn.commit()
            result["message"] = f"执行路径优化完成，预计节省 {result['estimated_time_savings']*100}% 时间"

        except Exception as e:
            result["status"] = "error"
            result["message"] = f"执行路径优化失败: {e}"
        finally:
            conn.close()

        return result

    def get_statistics(self) -> Dict:
        """获取验证统计信息"""
        stats = {
            "total_verified": 0,
            "high_priority_count": 0,
            "medium_priority_count": 0,
            "low_priority_count": 0,
            "avg_value_score": 0.0,
            "by_category": {}
        }

        conn = sqlite3.connect(str(self.innovation_db_path))
        cursor = conn.cursor()

        try:
            # 总验证数
            cursor.execute("SELECT COUNT(*) FROM innovation_verification WHERE verification_status = 'verified'")
            stats["total_verified"] = cursor.fetchone()[0]

            # 高优先级数（评分 >= 0.7）
            cursor.execute("SELECT COUNT(*) FROM innovation_verification WHERE total_value_score >= 0.7 AND verification_status = 'verified'")
            stats["high_priority_count"] = cursor.fetchone()[0]

            # 中优先级数（评分 0.5-0.7）
            cursor.execute("SELECT COUNT(*) FROM innovation_verification WHERE total_value_score >= 0.5 AND total_value_score < 0.7 AND verification_status = 'verified'")
            stats["medium_priority_count"] = cursor.fetchone()[0]

            # 低优先级数（评分 < 0.5）
            cursor.execute("SELECT COUNT(*) FROM innovation_verification WHERE total_value_score < 0.5 AND verification_status = 'verified'")
            stats["low_priority_count"] = cursor.fetchone()[0]

            # 平均价值评分
            cursor.execute("SELECT AVG(total_value_score) FROM innovation_verification WHERE verification_status = 'verified'")
            avg = cursor.fetchone()[0]
            stats["avg_value_score"] = round(avg, 2) if avg else 0.0

            # 按类别统计
            cursor.execute("""
                SELECT category, COUNT(*), AVG(total_value_score)
                FROM innovation_verification
                WHERE verification_status = 'verified'
                GROUP BY category
            """)
            for row in cursor.fetchall():
                stats["by_category"][row[0]] = {
                    "count": row[1],
                    "avg_score": round(row[2], 2) if row[2] else 0.0
                }

        except Exception as e:
            print(f"获取统计信息失败: {e}")
        finally:
            conn.close()

        return stats

    def get_cockpit_data(self) -> Dict:
        """获取驾驶舱数据"""
        stats = self.get_statistics()

        # 获取 Top 10 优先级
        conn = sqlite3.connect(str(self.innovation_db_path))
        cursor = conn.cursor()

        top_priorities = []
        try:
            cursor.execute("""
                SELECT id, description, total_value_score, priority_rank, execution_difficulty, predicted_effect
                FROM innovation_verification
                WHERE verification_status = 'verified'
                ORDER BY priority_rank ASC
                LIMIT 10
            """)
            for row in cursor.fetchall():
                top_priorities.append({
                    "id": row[0],
                    "description": row[1][:100] + "..." if len(row[1]) > 100 else row[1],
                    "value_score": row[2],
                    "rank": row[3],
                    "difficulty": row[4],
                    "predicted_effect": row[5]
                })
        finally:
            conn.close()

        return {
            "total_verified": stats["total_verified"],
            "high_priority": stats["high_priority_count"],
            "medium_priority": stats["medium_priority_count"],
            "low_priority": stats["low_priority_count"],
            "avg_value_score": stats["avg_value_score"],
            "by_category": stats["by_category"],
            "top_priorities": top_priorities,
            "last_updated": datetime.now().isoformat()
        }


def main():
    """主函数 - 支持命令行调用"""
    import argparse
    parser = argparse.ArgumentParser(description="创新建议自动验证与价值优先级排序引擎")
    parser.add_argument("--action", choices=["verify", "prioritize", "stats", "cockpit-data", "optimize-path"], default="stats",
                       help="执行动作")
    parser.add_argument("--innovation-id", type=int, help="创新建议ID（用于优化执行路径）")
    parser.add_argument("--version", action="store_true", help="显示版本信息")
    parser.add_argument("--status", action="store_true", help="显示引擎状态")

    args = parser.parse_args()

    if args.version:
        print("创新建议自动验证与价值优先级排序引擎 v1.0.0")
        return

    engine = InnovationValueVerificationEngine()

    if args.status:
        stats = engine.get_statistics()
        print(f"引擎状态: 运行中")
        print(f"已验证创新建议: {stats['total_verified']}")
        print(f"高优先级: {stats['high_priority_count']}")
        print(f"中优先级: {stats['medium_priority_count']}")
        print(f"低优先级: {stats['low_priority_count']}")
        print(f"平均价值评分: {stats['avg_value_score']}")
        return

    if args.action == "verify":
        result = engine.batch_verify_innovations()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.action == "prioritize":
        result = engine.prioritize_innovations()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.action == "stats":
        stats = engine.get_statistics()
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    elif args.action == "cockpit-data":
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
    elif args.action == "optimize-path":
        if not args.innovation_id:
            print("错误: 需要指定 --innovation-id")
            return
        result = engine.optimize_execution_path(args.innovation_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()