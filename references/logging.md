# 行为日志与溯源

## 原则

记录所有行为，便于溯源、复盘与审计。

## 实现

- **脚本**：`scripts/behavior_log.py`
- **目录**：`runtime/logs/`，按日或按任务分文件均可。
- **每条记录建议字段**：时间（ISO8601）、动作类型（如 assume/plan/track/verify/decide）、简要描述、关联 mission/task_id、可选 result。格式为 TAB 分隔：`时间\t类型\t描述\tmission=...\ttask_id=...\tresult=...`，便于 export_recent_logs 与弹框解析。

## 用途

- 回溯「某次决策为什么这样做」。
- 吃一堑长一智时结合 `references/failures.md` 对照日志分析。
- 多轮或多智能体接续时，通过日志理解已发生动作。

## 与闭环的关系

- 每个闭环模块在执行关键步骤时写一条日志。
- 决策模块在「记录教训」时，可引用日志中的某条或某段。

## 场景维度日志（用户请求与结果）

除上述**行为日志**（assume/plan/track/verify/decide）外，还有**场景日志**：记录用户说出的场景（如「打开摄像头自拍」）及执行结果（成功/失败），便于按场景积累经验。脚本：`scripts/scenario_log.py`（写入）、`scripts/query_scenario_experiences.py`（查询）。详见 `references/scenario_logging.md`。
