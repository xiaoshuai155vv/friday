# 场景维度日志（用户请求与执行结果）

## 场景指导（plans/）

`plans/` 目录下的 JSON 为**场景指导**（含 triggers 的）或**可执行计划**（run_plan 的步骤数组），供通用智能体查阅并按 steps 执行。格式示例：`triggers`（用户话）、`steps`（执行步骤）、`fallback`（保底）。当用户话匹配 triggers 时，**必须**按该 JSON 执行，勿自行发挥。如 `plans/play_music.json` 指导「放个歌」流程；`plans/ihaier_performance_declaration.json` 为绩效达成申报的可执行计划。

## 目的

当用户说出**场景化请求**（如「帮我打开摄像头给我来个自拍」「截个图」）时，将**用户输入**与**执行结果（成功/失败）**按**场景**记录，便于：

- 按场景积累**成功/失败经验**；
- 规划或决策时查阅「这类场景上次怎么做、结果如何」；
- 与 `references/failures.md` 配合，吃一堑长一智。

技能拷贝到另一台电脑（如 Claude Code 的 skills 目录）后，用户在该处提出的场景问题也会被记录，从而在不同环境中形成同一场景维度的经验。

## 记录什么

| 字段 | 说明 |
|------|------|
| 用户输入/场景描述 | 用户原话或归纳，如「打开摄像头自拍」 |
| 执行的意图或命令 | 实际调用的能力，如 `do 自拍`、`run selfie` |
| 结果 | `success` 或 `fail` |
| 备注 | 可选，如失败原因、环境说明 |

## 谁负责写

**通用智能体**（如 Claude）：在响应用户场景请求并执行完对应能力后，应主动调用 `scenario_log.py` 写入一条记录。例如：

- 用户说：「帮我打开摄像头给我来个自拍」
- 智能体执行：`do 自拍` 或 `selfie.py`
- 执行结束后调用：  
  `python scripts/scenario_log.py "打开摄像头给我来个自拍" "do 自拍" success`  
  或若失败：  
  `python scripts/scenario_log.py "打开摄像头自拍" "do 自拍" fail "摄像头未就绪"`

## 存储位置

- **按日日志**：`logs/scenario_YYYY-MM-DD.log`（TAB 分隔：时间、场景、命令、结果、备注）
- **近期汇总**：`state/scenario_experiences.json`（最近 N 条，供快速查询与 UI）

## 如何查阅

- **最近 N 条**：`python scripts/query_scenario_experiences.py 20`
- **按关键词**：`python scripts/query_scenario_experiences.py --keyword 自拍`  
  用于规划时查看「自拍」相关场景的历史成功/失败。

## 与进化环的关系

- **假设/规划**：可先查 `query_scenario_experiences.py --keyword <场景>`，再结合 `failures.md` 决定如何实现或避免重复失败。
- **执行后**：用户场景请求执行完毕，必须调用 `scenario_log.py` 写入结果，这样下一轮或别机才有「按场景维度的经验」可用。
- **do 不支持时的固化**：当 `do.py` 返回「未知意图」且用保底能力（鼠标、键盘、多模态）成功完成时，**必须**将最短正确路径整理为 `plans/<场景名>.json`，并 scenario_log 备注「已固化 plan」，下次同类需求直接 `run_plan`。
