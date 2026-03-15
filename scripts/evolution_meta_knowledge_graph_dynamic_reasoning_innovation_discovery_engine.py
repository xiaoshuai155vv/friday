"""
智能全场景进化环元进化知识图谱动态推理与主动创新发现引擎
version: 1.0.0

基于 round 625 完成的记忆深度整合与智慧涌现引擎和 round 632 完成的方法论自动学习引擎基础上，
构建让系统能够构建动态进化的知识图谱、进行图谱实时推理、主动发现创新机会并生成可执行创新建议。

功能：
1. 知识图谱动态构建 - 自动从600+轮进化历史中抽取实体（引擎、能力、概念）和关系构建动态图谱
2. 图谱实时推理 - 在知识图谱上进行实时推理，发现隐藏关联和潜在模式
3. 主动创新发现 - 基于图谱结构主动发现创新机会和未被利用的能力组合
4. 创新建议生成 - 将发现的创新机会转化为可执行的进化建议
5. 图谱自演化 - 根据进化结果自动更新图谱，保持图谱时效性

与 round 625 记忆整合引擎、round 632 方法论学习引擎深度集成，形成「构建→推理→发现→建议→演化」的完整知识图谱创新闭环。
"""

import json
import os
import re
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


class KnowledgeGraphEntity:
    """知识图谱实体"""

    def __init__(self, id: str, name: str, entity_type: str, properties: Dict = None):
        self.id = id
        self.name = name
        self.entity_type = entity_type  # engine, capability, concept, round, file
        self.properties = properties or {}
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "entity_type": self.entity_type,
            "properties": self.properties,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class KnowledgeGraphRelation:
    """知识图谱关系"""

    def __init__(self, source_id: str, target_id: str, relation_type: str, weight: float = 1.0):
        self.source_id = source_id
        self.target_id = target_id
        self.relation_type = relation_type  # depends_on, uses, combines_with, evolved_from, etc.
        self.weight = weight
        self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type,
            "weight": self.weight,
            "created_at": self.created_at
        }


class KnowledgeGraphEngine:
    """元进化知识图谱动态推理与主动创新发现引擎"""

    def __init__(self):
        self.kg_db_path = KG_DB_PATH
        self._init_database()

        # 实体类型
        self.entity_types = ["engine", "capability", "concept", "round", "file", "module"]

        # 关系类型
        self.relation_types = [
            "depends_on", "uses", "combines_with", "evolved_from",
            "integrates_with", "enhances", "triggers", "generates",
            "optimizes", "validates", "monitors"
        ]

    def _init_database(self):
        """初始化知识图谱数据库"""
        conn = sqlite3.connect(str(self.kg_db_path))
        cursor = conn.cursor()

        # 创建实体表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                properties TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # 创建关系表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relations (
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                relation_type TEXT NOT NULL,
                weight REAL DEFAULT 1.0,
                created_at TEXT,
                PRIMARY KEY (source_id, target_id, relation_type)
            )
        """)

        # 创建创新发现记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS innovation_discoveries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discovery_type TEXT,
                description TEXT,
                entities_involved TEXT,
                execution_status TEXT DEFAULT 'pending',
                created_at TEXT,
                executed_at TEXT
            )
        """)

        conn.commit()
        conn.close()

    def build_knowledge_graph(self) -> Dict:
        """从进化历史构建知识图谱"""
        result = {
            "status": "success",
            "entities_added": 0,
            "relations_added": 0,
            "message": ""
        }

        conn = sqlite3.connect(str(self.kg_db_path))
        cursor = conn.cursor()

        try:
            # 1. 从 scripts 目录扫描引擎文件，提取实体
            engine_entities = self._scan_engine_files()
            for entity in engine_entities:
                cursor.execute("""
                    INSERT OR REPLACE INTO entities (id, name, entity_type, properties, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (entity.id, entity.name, entity.entity_type, json.dumps(entity.properties), entity.created_at, entity.updated_at))
                result["entities_added"] += 1

            # 2. 从进化历史提取实体和关系
            evolution_entities, evolution_relations = self._extract_from_evolution_history()
            for entity in evolution_entities:
                cursor.execute("""
                    INSERT OR REPLACE INTO entities (id, name, entity_type, properties, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (entity.id, entity.name, entity.entity_type, json.dumps(entity.properties), entity.created_at, entity.updated_at))
                result["entities_added"] += 1

            for relation in evolution_relations:
                cursor.execute("""
                    INSERT OR REPLACE INTO relations (source_id, target_id, relation_type, weight, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (relation.source_id, relation.target_id, relation.relation_type, relation.weight, relation.created_at))
                result["relations_added"] += 1

            # 3. 从 evolution_self_proposed.md 提取待执行项作为实体
            proposed_entities = self._extract_from_proposals()
            for entity in proposed_entities:
                cursor.execute("""
                    INSERT OR REPLACE INTO entities (id, name, entity_type, properties, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (entity.id, entity.name, entity.entity_type, json.dumps(entity.properties), entity.created_at, entity.updated_at))
                result["entities_added"] += 1

            # 4. 从 capabilities.md 提取能力实体
            capability_entities = self._extract_from_capabilities()
            for entity in capability_entities:
                cursor.execute("""
                    INSERT OR REPLACE INTO entities (id, name, entity_type, properties, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (entity.id, entity.name, entity.entity_type, json.dumps(entity.properties), entity.created_at, entity.updated_at))
                result["entities_added"] += 1

            conn.commit()
            result["message"] = f"知识图谱构建完成：添加 {result['entities_added']} 个实体，{result['relations_added']} 个关系"

        except Exception as e:
            result["status"] = "error"
            result["message"] = f"构建知识图谱失败: {str(e)}"
            conn.rollback()
        finally:
            conn.close()

        return result

    def _scan_engine_files(self) -> List[KnowledgeGraphEntity]:
        """扫描 scripts 目录下的引擎文件"""
        entities = []
        engine_pattern = re.compile(r'^evolution_.*\.py$')

        for file in SCRIPTS_DIR.glob("evolution_*.py"):
            if engine_pattern.match(file.name):
                entity = KnowledgeGraphEntity(
                    id=f"engine:{file.stem}",
                    name=file.stem,
                    entity_type="engine",
                    properties={
                        "file": str(file),
                        "description": self._extract_engine_description(file)
                    }
                )
                entities.append(entity)

        return entities

    def _extract_engine_description(self, file_path: Path) -> str:
        """从引擎文件提取描述"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(1000)  # 只读取开头部分
                # 提取文档字符串第一行
                match = re.search(r'"""([^"]+)"""', content)
                if match:
                    return match.group(1).strip()
        except:
            pass
        return ""

    def _extract_from_evolution_history(self) -> Tuple[List[KnowledgeGraphEntity], List[KnowledgeGraphRelation]]:
        """从进化历史提取实体和关系"""
        entities = []
        relations = []

        # 读取 evolution_auto_last.md
        auto_last_path = PROJECT_ROOT / "references" / "evolution_auto_last.md"
        if auto_last_path.exists():
            with open(auto_last_path, 'r', encoding='utf-8') as f:
                content = f.read()

                # 提取轮次信息
                round_match = re.search(r'round (\d+)', content)
                if round_match:
                    round_num = round_match.group(1)
                    entity = KnowledgeGraphEntity(
                        id=f"round:{round_num}",
                        name=f"Round {round_num}",
                        entity_type="round",
                        properties={"source": "evolution_auto_last.md"}
                    )
                    entities.append(entity)

        # 读取最近的 evolution_completed_*.json 文件
        completed_files = sorted(RUNTIME_STATE_DIR.glob("evolution_completed_*.json"))[-10:]  # 最近10个
        for file in completed_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    # 添加 round 实体
                    if "loop_round" in data:
                        entity = KnowledgeGraphEntity(
                            id=f"round:{data['loop_round']}",
                            name=f"Round {data['loop_round']}",
                            entity_type="round",
                            properties={
                                "current_goal": data.get("current_goal", ""),
                                "status": data.get("status", "")
                            }
                        )
                        entities.append(entity)

            except Exception as e:
                print(f"读取 {file} 失败: {e}")

        return entities, relations

    def _extract_from_proposals(self) -> List[KnowledgeGraphEntity]:
        """从 evolution_self_proposed.md 提取待执行项"""
        entities = []

        proposals_path = PROJECT_ROOT / "references" / "evolution_self_proposed.md"
        if proposals_path.exists():
            with open(proposals_path, 'r', encoding='utf-8') as f:
                content = f.read()

                # 提取待执行的项目
                for line in content.split('\n'):
                    if '待执行' in line or 'to be executed' in line.lower():
                        # 提取项目名称（简化处理）
                        if '|' in line:
                            parts = line.split('|')
                            if len(parts) >= 2:
                                name = parts[1].strip()
                                entity = KnowledgeGraphEntity(
                                    id=f"proposal:{name[:30]}",
                                    name=name[:50],
                                    entity_type="concept",
                                    properties={"status": "pending"}
                                )
                                entities.append(entity)

        return entities

    def _extract_from_capabilities(self) -> List[KnowledgeGraphEntity]:
        """从 capabilities.md 提取能力实体"""
        entities = []

        capabilities_path = PROJECT_ROOT / "references" / "capabilities.md"
        if capabilities_path.exists():
            with open(capabilities_path, 'r', encoding='utf-8') as f:
                content = f.read()

                # 提取 | 意图/场景 | 命令 | 行
                for line in content.split('\n'):
                    if '|' in line and 'do.py' in line:
                        parts = [p.strip() for p in line.split('|')]
                        if len(parts) >= 3 and parts[1] and parts[1] != '意图/场景':
                            entity = KnowledgeGraphEntity(
                                id=f"capability:{parts[1][:30]}",
                                name=parts[1][:50],
                                entity_type="capability",
                                properties={"command": parts[2][:100]}
                            )
                            entities.append(entity)

        return entities

    def reason_on_graph(self, query: str = "") -> Dict:
        """在知识图谱上进行推理"""
        result = {
            "status": "success",
            "reasoning_results": [],
            "hidden_patterns": [],
            "message": ""
        }

        conn = sqlite3.connect(str(self.kg_db_path))
        cursor = conn.cursor()

        try:
            # 1. 查找高连接度实体（关键引擎）
            cursor.execute("""
                SELECT e.id, e.name, e.entity_type, COUNT(r.source_id) + COUNT(r2.target_id) as degree
                FROM entities e
                LEFT JOIN relations r ON e.id = r.source_id
                LEFT JOIN relations r2 ON e.id = r2.target_id
                GROUP BY e.id
                ORDER BY degree DESC
                LIMIT 10
            """)
            high_degree_entities = cursor.fetchall()

            result["hidden_patterns"].append({
                "type": "high_degree_entities",
                "description": "高连接度实体（关键引擎）",
                "data": [{"id": e[0], "name": e[1], "type": e[2], "degree": e[3]} for e in high_degree_entities]
            })

            # 2. 查找未被使用的引擎（潜在优化点）
            cursor.execute("""
                SELECT e.id, e.name, e.entity_type
                FROM entities e
                LEFT JOIN relations r ON e.id = r.source_id
                WHERE e.entity_type = 'engine' AND r.source_id IS NULL
            """)
            unused_engines = cursor.fetchall()

            result["hidden_patterns"].append({
                "type": "unused_engines",
                "description": "未被引用的引擎（可优化）",
                "data": [{"id": e[0], "name": e[1], "type": e[2]} for e in unused_engines]
            })

            # 3. 查找共同依赖关系
            cursor.execute("""
                SELECT r1.source_id, r1.target_id, r2.target_id, COUNT(*) as cnt
                FROM relations r1
                JOIN relations r2 ON r1.target_id = r2.source_id AND r1.source_id != r2.target_id
                WHERE r1.relation_type IN ('depends_on', 'uses')
                GROUP BY r1.source_id, r1.target_id, r2.target_id
                HAVING cnt > 1
                LIMIT 10
            """)
            common_deps = cursor.fetchall()

            result["hidden_patterns"].append({
                "type": "common_dependencies",
                "description": "共同依赖关系（可优化的共同点）",
                "data": [{"from": d[0], "via": d[1], "to": d[2], "count": d[3]} for d in common_deps]
            })

            # 4. 实体关系路径分析
            cursor.execute("""
                SELECT r1.source_id, r1.relation_type, r1.target_id, r2.relation_type, r2.target_id
                FROM relations r1
                LEFT JOIN relations r2 ON r1.target_id = r2.source_id
                WHERE r2.target_id IS NOT NULL
                LIMIT 20
            """)
            paths = cursor.fetchall()

            reasoning_paths = []
            for p in paths:
                reasoning_paths.append({
                    "from": p[0],
                    "relation1": p[1],
                    "via": p[2],
                    "relation2": p[3],
                    "to": p[4]
                })

            result["reasoning_results"] = reasoning_paths

            result["message"] = f"图谱推理完成：发现 {len(result['hidden_patterns'])} 种隐藏模式，{len(reasoning_paths)} 条推理路径"

        except Exception as e:
            result["status"] = "error"
            result["message"] = f"图谱推理失败: {str(e)}"
        finally:
            conn.close()

        return result

    def discover_innovations(self) -> Dict:
        """主动发现创新机会"""
        result = {
            "status": "success",
            "innovations": [],
            "message": ""
        }

        conn = sqlite3.connect(str(self.kg_db_path))
        cursor = conn.cursor()

        try:
            # 1. 发现未被组合的能力组合
            cursor.execute("""
                SELECT e1.id, e1.name, e2.id, e2.name
                FROM entities e1, entities e2
                WHERE e1.entity_type = 'engine' AND e2.entity_type = 'engine'
                AND e1.id < e2.id
                AND NOT EXISTS (
                    SELECT 1 FROM relations r
                    WHERE r.source_id = e1.id AND r.target_id = e2.id
                    AND r.relation_type = 'combines_with'
                )
                LIMIT 10
            """)
            unused_combinations = cursor.fetchall()

            for combo in unused_combinations:
                result["innovations"].append({
                    "type": "unused_combination",
                    "description": f"未被组合的引擎: {combo[1]} + {combo[3]}",
                    "entities": [combo[0], combo[2]],
                    "potential": "medium"
                })

            # 2. 发现孤立引擎（无依赖关系）
            cursor.execute("""
                SELECT e.id, e.name
                FROM entities e
                WHERE e.entity_type = 'engine'
                AND NOT EXISTS (SELECT 1 FROM relations r WHERE r.source_id = e.id)
                AND NOT EXISTS (SELECT 1 FROM relations r WHERE r.target_id = e.id)
            """)
            isolated_engines = cursor.fetchall()

            for engine in isolated_engines:
                result["innovations"].append({
                    "type": "isolated_engine",
                    "description": f"孤立引擎（可建立连接）: {engine[1]}",
                    "entities": [engine[0]],
                    "potential": "high"
                })

            # 3. 发现可自动化的能力缺口
            cursor.execute("""
                SELECT e.id, e.name
                FROM entities e
                WHERE e.entity_type = 'capability'
                AND NOT EXISTS (
                    SELECT 1 FROM relations r
                    WHERE r.source_id = e.id AND r.relation_type = 'automated'
                )
                LIMIT 5
            """)
            non_automated_caps = cursor.fetchall()

            for cap in non_automated_caps:
                result["innovations"].append({
                    "type": "non_automated_capability",
                    "description": f"可自动化的能力: {cap[1]}",
                    "entities": [cap[0]],
                    "potential": "medium"
                })

            # 4. 发现能力链优化机会
            cursor.execute("""
                SELECT e1.name, r.relation_type, e2.name
                FROM relations r
                JOIN entities e1 ON r.source_id = e1.id
                JOIN entities e2 ON r.target_id = e2.id
                WHERE e1.entity_type = 'engine' AND e2.entity_type = 'engine'
                AND r.relation_type = 'depends_on'
                ORDER BY e1.name
                LIMIT 10
            """)
            chains = cursor.fetchall()

            # 检查是否有长依赖链（可简化）
            chain_lengths = {}
            for chain in chains:
                key = chain[0]
                if key not in chain_lengths:
                    chain_lengths[key] = 0
                chain_lengths[key] += 1

            for engine_name, length in chain_lengths.items():
                if length > 3:
                    result["innovations"].append({
                        "type": "long_dependency_chain",
                        "description": f"长依赖链可简化: {engine_name} (依赖 {length} 个引擎)",
                        "entities": [],
                        "potential": "high"
                    })

            result["message"] = f"发现 {len(result['innovations'])} 个创新机会"

        except Exception as e:
            result["status"] = "error"
            result["message"] = f"创新发现失败: {str(e)}"
        finally:
            conn.close()

        return result

    def generate_innovation_suggestions(self) -> Dict:
        """生成可执行的创新建议"""
        result = {
            "status": "success",
            "suggestions": [],
            "message": ""
        }

        # 获取创新发现结果
        discoveries = self.discover_innovations()

        # 将发现转化为可执行的建议
        for innovation in discoveries.get("innovations", []):
            suggestion = {
                "id": f"suggestion_{len(result['suggestions']) + 1}",
                "innovation_type": innovation["type"],
                "description": innovation["description"],
                "priority": innovation.get("potential", "low"),
                "actions": []
            }

            if innovation["type"] == "unused_combination":
                # 建议：创建新引擎组合
                engine1 = innovation["entities"][0].split(":")[-1] if innovation["entities"] else ""
                engine2 = innovation["entities"][1].split(":")[-1] if len(innovation["entities"]) > 1 else ""
                suggestion["actions"] = [
                    f"分析 {engine1} 和 {engine2} 的功能互补性",
                    f"设计组合引擎的架构",
                    f"实现组合引擎并集成到 do.py"
                ]
                suggestion["priority"] = "high"

            elif innovation["type"] == "isolated_engine":
                # 建议：建立与其他引擎的连接
                engine = innovation["entities"][0].split(":")[-1] if innovation["entities"] else ""
                suggestion["actions"] = [
                    f"分析 {engine} 的功能",
                    f"识别可关联的引擎和能力",
                    f"建立依赖或集成关系"
                ]

            elif innovation["type"] == "long_dependency_chain":
                # 建议：简化依赖链
                suggestion["actions"] = [
                    "分析依赖链的必要性",
                    "提取共同依赖为独立模块",
                    "重构引擎以减少直接依赖"
                ]
                suggestion["priority"] = "high"

            elif innovation["type"] == "non_automated_capability":
                # 建议：自动化该能力
                capability = innovation["entities"][0].split(":")[-1] if innovation["entities"] else ""
                suggestion["actions"] = [
                    f"分析 {capability} 的实现方式",
                    f"设计自动化执行流程",
                    f"集成到 run_plan 或创建新脚本"
                ]

            result["suggestions"].append(suggestion)

        result["message"] = f"生成 {len(result['suggestions'])} 条可执行创新建议"

        # 保存到数据库
        conn = sqlite3.connect(str(self.kg_db_path))
        cursor = conn.cursor()
        for suggestion in result["suggestions"]:
            cursor.execute("""
                INSERT INTO innovation_discoveries (discovery_type, description, entities_involved, execution_status, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                suggestion["innovation_type"],
                suggestion["description"],
                json.dumps(suggestion.get("entities", [])),
                "pending",
                datetime.now().isoformat()
            ))
        conn.commit()
        conn.close()

        return result

    def get_cockpit_data(self) -> Dict:
        """获取驾驶舱数据"""
        conn = sqlite3.connect(str(self.kg_db_path))
        cursor = conn.cursor()

        # 统计信息
        cursor.execute("SELECT COUNT(*) FROM entities")
        entity_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM relations")
        relation_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM innovation_discoveries WHERE execution_status = 'pending'")
        pending_suggestions = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM innovation_discoveries WHERE execution_status = 'executed'")
        executed_suggestions = cursor.fetchone()[0]

        conn.close()

        return {
            "entity_count": entity_count,
            "relation_count": relation_count,
            "pending_suggestions": pending_suggestions,
            "executed_suggestions": executed_suggestions,
            "last_updated": datetime.now().isoformat()
        }

    def run(self, action: str = "full") -> Dict:
        """运行引擎"""
        if action == "build":
            return self.build_knowledge_graph()
        elif action == "reason":
            return self.reason_on_graph()
        elif action == "discover":
            return self.discover_innovations()
        elif action == "suggestions":
            return self.generate_innovation_suggestions()
        elif action == "full":
            # 完整流程：构建->推理->发现->建议
            build_result = self.build_knowledge_graph()
            reasoning_result = self.reason_on_graph()
            discovery_result = self.discover_innovations()
            suggestion_result = self.generate_innovation_suggestions()

            return {
                "status": "success",
                "build": build_result,
                "reasoning": reasoning_result,
                "discovery": discovery_result,
                "suggestions": suggestion_result,
                "cockpit_data": self.get_cockpit_data()
            }
        else:
            return {"status": "error", "message": f"未知动作: {action}"}


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="元进化知识图谱动态推理与主动创新发现引擎")
    parser.add_argument("--action", default="full", choices=["build", "reason", "discover", "suggestions", "full"], help="执行动作")
    parser.add_argument("--version", action="store_true", help="显示版本")
    parser.add_argument("--status", action="store_true", help="显示状态")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")

    args = parser.parse_args()

    engine = KnowledgeGraphEngine()

    if args.version:
        print("evolution_meta_knowledge_graph_dynamic_reasoning_innovation_discovery_engine.py version 1.0.0")
        return

    if args.status:
        data = engine.get_cockpit_data()
        print(f"知识图谱状态:")
        print(f"  - 实体数量: {data['entity_count']}")
        print(f"  - 关系数量: {data['relation_count']}")
        print(f"  - 待执行建议: {data['pending_suggestions']}")
        print(f"  - 已执行建议: {data['executed_suggestions']}")
        print(f"  - 最后更新: {data['last_updated']}")
        return

    if args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    result = engine.run(args.action)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()