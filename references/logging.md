# 行为日志与溯源

## 原则

记录所有行为，便于溯源、复盘与审计。

## Behavior log 写入结构（通用智能体直接按此写入，无需读 behavior_*.log 文件）

**统一通过脚本写入**（推荐，自动带时间戳与格式）：

- **脚本**：`scripts/behavior_log.py`
- **路径**：脚本自动写入 `runtime/logs/behavior_YYYY-MM-DD.log`（按当天日期，无需智能体拼路径）。
- **命令行格式**：
  ```text
  python scripts/behavior_log.py <action_type> "<description>" [--mission "<mission>"] [--task-id "<id>"] [--result "<pass|fail|...>"]
  ```
- **action_type**：必填，且只能为以下之一：`assume` | `plan` | `track` | `verify` | `decide` | `other`。
- **description**：必填，简短描述（建议一句话，过长会令日志膨胀）。
- **--mission**：可选，当前使命/轮次描述。
- **--task-id**：可选。
- **--result**：可选；`verify` 阶段建议填 `pass` 或 `fail`。

**各阶段直接调用的命令示例**（将 `...` 替换为实际内容即可）：

| 阶段 | 命令 |
|------|------|
| 假设 | `python scripts/behavior_log.py assume "<简短描述>" --mission "<当前使命>"` |
| 决策/规划 | `python scripts/behavior_log.py plan "<目标与下一步>" --mission "<当前使命>"` |
| 执行 | `python scripts/behavior_log.py track "<做了什么>" --mission "<当前使命>"` |
| 校验 | `python scripts/behavior_log.py verify "<校验结论>" --mission "<当前使命>" --result "pass"或"fail"` |
| 反思 | `python scripts/behavior_log.py decide "<决策与下一轮意图>" --mission "<当前使命>"` |

**文件内一行结构**（仅当无法调脚本、需直接写文件时参考；否则一律用脚本）：

- 一行一条，TAB 分隔：`{ISO8601_UTC}\t{action_type}\t{description}\tmission={mission}\ttask_id={task_id}\tresult={result}\n`
- 时间用 UTC ISO8601，如 `2026-03-11T08:00:00.123456+00:00`；空字段仍保留 `mission=` 等 key，值为空即可。

**说明**：`behavior_*.log` 会随轮次增多而变大，仅追加不覆盖；通用智能体**只需按上表调用脚本**，无需打开或解析已有日志文件。

## 实现（与上等价，保留原说明）

- **脚本**：`scripts/behavior_log.py`
- **目录**：`runtime/logs/`，按日分文件 `behavior_YYYY-MM-DD.log`。
- **每条记录建议字段**：时间（ISO8601）、动作类型（assume/plan/track/verify/decide/other）、简要描述、mission、task_id、result。格式为 TAB 分隔，便于 export_recent_logs 与弹框解析。

## 用途

- 回溯「某次决策为什么这样做」。
- 吃一堑长一智时结合 `references/failures.md` 对照日志分析。
- 多轮或多智能体接续时，通过日志理解已发生动作。

## 与闭环的关系

- 每个闭环模块在执行关键步骤时写一条日志。
- 决策模块在「记录教训」时，可引用日志中的某条或某段。

## evolution_loop.log（仅客户端写入，智能体不写）

- **路径**：`runtime/logs/evolution_loop.log`
- **谁写**：仅 `scripts/evolution_loop_client.py` 在每次请求 CCR 时追加（POST、成功/失败等一行）。
- **会越来越大**：仅追加不轮转；通用智能体**不写入**此文件。若需按大小/时间轮转或归档，可由运维或后续脚本处理。

## 场景维度日志（用户请求与结果）

除上述**行为日志**（assume/plan/track/verify/decide）外，还有**场景日志**：记录用户说出的场景（如「打开摄像头自拍」）及执行结果（成功/失败），便于按场景积累经验。脚本：`scripts/scenario_log.py`（写入）、`scripts/query_scenario_experiences.py`（查询）。详见 `references/scenario_logging.md`。
