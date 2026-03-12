#!/usr/bin/env python3
"""
智能错误诊断与根因分析引擎
提供跨模块错误聚合、根因识别、智能修复建议功能
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ErrorDiagnosisEngine:
    """智能错误诊断引擎"""

    def __init__(self, log_dir: str = "runtime/state"):
        """
        初始化错误诊断引擎

        Args:
            log_dir: 日志文件存储目录
        """
        self.log_dir = log_dir
        self.error_history_file = os.path.join(log_dir, "error_history.json")
        self.diagnosis_results_file = os.path.join(log_dir, "diagnosis_results.json")

        # 确保目录存在
        os.makedirs(log_dir, exist_ok=True)

        # 加载历史错误数据
        self.error_history = self._load_error_history()

    def _load_error_history(self) -> List[Dict]:
        """加载历史错误记录"""
        try:
            if os.path.exists(self.error_history_file):
                with open(self.error_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return []
        except Exception as e:
            logger.error(f"加载错误历史失败: {e}")
            return []

    def _save_error_history(self):
        """保存错误历史记录"""
        try:
            with open(self.error_history_file, 'w', encoding='utf-8') as f:
                json.dump(self.error_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存错误历史失败: {e}")

    def record_error(self, module: str, error_type: str, error_message: str,
                     timestamp: Optional[str] = None, context: Optional[Dict] = None):
        """
        记录错误信息

        Args:
            module: 出错的模块名称
            error_type: 错误类型
            error_message: 错误信息
            timestamp: 时间戳，默认为当前时间
            context: 错误上下文信息
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        error_record = {
            "timestamp": timestamp,
            "module": module,
            "error_type": error_type,
            "error_message": error_message,
            "context": context or {}
        }

        self.error_history.append(error_record)
        self._save_error_history()

        logger.info(f"记录错误: {module} - {error_type}")

    def analyze_errors(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """
        分析错误模式和根因

        Args:
            time_window_hours: 分析的时间窗口（小时）

        Returns:
            错误分析结果
        """
        # 过滤指定时间窗口内的错误
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        recent_errors = [
            error for error in self.error_history
            if datetime.fromisoformat(error["timestamp"]) >= cutoff_time
        ]

        if not recent_errors:
            return {
                "summary": "无近期错误记录",
                "error_patterns": [],
                "root_causes": [],
                "recommendations": []
            }

        # 统计错误频率
        error_counter = Counter()
        module_counter = Counter()
        error_types = defaultdict(list)

        for error in recent_errors:
            error_counter[(error["module"], error["error_type"])] += 1
            module_counter[error["module"]] += 1
            error_types[error["error_type"]].append(error)

        # 识别高频错误模式
        frequent_patterns = []
        for (module, error_type), count in error_counter.most_common(10):
            frequent_patterns.append({
                "module": module,
                "error_type": error_type,
                "frequency": count
            })

        # 识别根因
        root_causes = self._identify_root_causes(recent_errors)

        # 生成建议
        recommendations = self._generate_recommendations(recent_errors)

        return {
            "summary": f"分析时间窗口: {time_window_hours}小时, 总错误数: {len(recent_errors)}",
            "error_patterns": frequent_patterns,
            "root_causes": root_causes,
            "recommendations": recommendations,
            "module_distribution": dict(module_counter)
        }

    def _identify_root_causes(self, errors: List[Dict]) -> List[Dict]:
        """
        识别错误的根本原因

        Args:
            errors: 错误记录列表

        Returns:
            根因列表
        """
        root_causes = []

        # 基于错误类型识别根因
        for error in errors:
            error_type = error["error_type"]
            module = error["module"]

            # 常见错误类型映射
            if "timeout" in error_type.lower():
                root_causes.append({
                    "cause": "超时问题",
                    "description": f"模块 {module} 执行过程中出现超时",
                    "related_errors": [error],
                    "potential_cause": "资源不足、网络延迟、系统繁忙"
                })
            elif "activation" in error_type.lower() or "window" in error_type.lower():
                root_causes.append({
                    "cause": "窗口激活问题",
                    "description": f"模块 {module} 无法激活目标窗口",
                    "related_errors": [error],
                    "potential_cause": "窗口不存在、权限不足、系统限制"
                })
            elif "clipboard" in error_type.lower():
                root_causes.append({
                    "cause": "剪贴板访问问题",
                    "description": f"模块 {module} 无法访问剪贴板",
                    "related_errors": [error],
                    "potential_cause": "远程会话限制、权限不足、剪贴板忙"
                })
            elif "vision" in error_type.lower():
                root_causes.append({
                    "cause": "视觉识别问题",
                    "description": f"模块 {module} 的视觉识别失败",
                    "related_errors": [error],
                    "potential_cause": "图像质量差、坐标偏移、模型问题"
                })
            elif "permission" in error_type.lower() or "access" in error_type.lower():
                root_causes.append({
                    "cause": "权限不足",
                    "description": f"模块 {module} 缺少必要权限",
                    "related_errors": [error],
                    "potential_cause": "用户权限不足、系统限制、安全策略"
                })

        # 如果没有明确的根因，根据模块特征判断
        if not root_causes:
            module_specific_causes = {
                "vision_coords": "视觉坐标识别问题",
                "window_tool": "窗口操作问题",
                "clipboard_tool": "剪贴板访问问题",
                "run_plan": "任务执行问题",
                "task_recovery": "任务恢复问题"
            }

            for module, cause in module_specific_causes.items():
                if any(module in error["module"] for error in errors):
                    root_causes.append({
                        "cause": cause,
                        "description": f"模块 {module} 存在相关问题",
                        "related_errors": [e for e in errors if module in e["module"]],
                        "potential_cause": "模块配置或环境问题"
                    })

        return root_causes

    def _generate_recommendations(self, errors: List[Dict]) -> List[Dict]:
        """
        生成修复建议

        Args:
            errors: 错误记录列表

        Returns:
            建议列表
        """
        recommendations = []

        # 基于错误类型生成建议
        for error in errors:
            error_type = error["error_type"]
            module = error["module"]

            if "timeout" in error_type.lower():
                recommendations.append({
                    "priority": "high",
                    "action": "增加超时时间或重试机制",
                    "module": module,
                    "details": f"建议为 {module} 增加超时容忍机制"
                })
            elif "activation" in error_type.lower() or "window" in error_type.lower():
                recommendations.append({
                    "priority": "high",
                    "action": "添加窗口激活重试逻辑",
                    "module": module,
                    "details": f"建议在 {module} 中添加窗口激活失败时的重试机制"
                })
            elif "clipboard" in error_type.lower():
                recommendations.append({
                    "priority": "medium",
                    "action": "使用备用剪贴板方案",
                    "module": module,
                    "details": f"建议为 {module} 添加剪贴板访问失败时的备用方案"
                })
            elif "vision" in error_type.lower():
                recommendations.append({
                    "priority": "medium",
                    "action": "校准视觉坐标偏移",
                    "module": module,
                    "details": f"建议校准 {module} 中的视觉坐标偏移"
                })
            elif "permission" in error_type.lower() or "access" in error_type.lower():
                recommendations.append({
                    "priority": "high",
                    "action": "检查用户权限",
                    "module": module,
                    "details": f"建议检查 {module} 执行所需的权限配置"
                })

        # 如果没有特定建议，生成通用建议
        if not recommendations:
            recommendations.append({
                "priority": "medium",
                "action": "检查系统健康状况",
                "module": "通用",
                "details": "建议进行全面的系统健康检查"
            })

        return recommendations

    def get_diagnosis_report(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """
        获取诊断报告

        Args:
            time_window_hours: 分析时间窗口

        Returns:
            诊断报告
        """
        analysis = self.analyze_errors(time_window_hours)

        # 保存诊断结果
        diagnosis_result = {
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis
        }

        try:
            with open(self.diagnosis_results_file, 'w', encoding='utf-8') as f:
                json.dump(diagnosis_result, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存诊断结果失败: {e}")

        return diagnosis_result

    def clear_history(self):
        """清空错误历史"""
        self.error_history = []
        self._save_error_history()
        logger.info("错误历史已清空")


def main():
    """主函数 - 支持命令行参数"""
    import argparse

    parser = argparse.ArgumentParser(description="智能错误诊断与根因分析引擎")
    parser.add_argument("--analyze", action="store_true", help="分析错误模式")
    parser.add_argument("--report", action="store_true", help="生成诊断报告")
    parser.add_argument("--history", action="store_true", help="查看错误历史")
    parser.add_argument("--clear", action="store_true", help="清空错误历史")
    parser.add_argument("--hours", type=int, default=24, help="分析时间窗口（小时）")
    parser.add_argument("--record", nargs=3, metavar=("MODULE", "TYPE", "MESSAGE"), help="记录错误: 模块 类型 消息")

    args = parser.parse_args()

    engine = ErrorDiagnosisEngine()

    if args.record:
        # 记录错误
        module, error_type, message = args.record
        engine.record_error(module, error_type, message)
        print(f"错误已记录: {module} - {error_type}")
    elif args.clear:
        # 清空历史
        engine.clear_history()
        print("错误历史已清空")
    elif args.history:
        # 查看历史
        errors = engine.error_history
        if not errors:
            print("无错误历史记录")
        else:
            print(f"错误历史记录 ({len(errors)}条):")
            for error in errors[-10:]:  # 显示最近10条
                print(f"  [{error['timestamp']}] {error['module']} - {error['error_type']}: {error['error_message']}")
    elif args.report:
        # 生成诊断报告
        report = engine.get_diagnosis_report(args.hours)
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif args.analyze:
        # 分析错误
        analysis = engine.analyze_errors(args.hours)
        print(json.dumps(analysis, ensure_ascii=False, indent=2))
    else:
        # 默认：测试并输出报告
        # 测试记录错误（仅在无历史时）
        if not engine.error_history:
            engine.record_error("vision_coords", "timeout", "视觉识别超时", context={"target": "button"})
            engine.record_error("window_tool", "activation_failed", "窗口激活失败", context={"window_title": "办公平台"})
            engine.record_error("clipboard_tool", "access_denied", "剪贴板访问被拒绝")

        # 生成诊断报告
        report = engine.get_diagnosis_report(args.hours)
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()