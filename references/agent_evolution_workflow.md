# 通用智能体 · 自进化闭环工作流

**面向对象**：任何驱动本项目的智能体（不限定具体平台或模型）。只要按本工作流读取输入、执行动作、写入输出，即可形成**无限进化循环**。

**核心环**：假设 → 自主决策 → 自主执行 → 自主校验审核 → 自主优化反思 → 回到「假设」。

---

## 进化环示意

```
     ┌──────────────────────────────────────────────────────────┐
     │                                                          │
     ▼                                                          │
  假设 ──► 自主决策 ──► 自主执行 ──► 自主校验审核 ──► 自主优化反思 ──┘
  (读缺口与失败)  (定目标与计划)  (跑脚本/改文档)  (自校验与审核)  (写教训、定下一轮)
```

**重要**：每轮「自主优化反思」结束后，**必须**进入下一轮的「假设」，不要在本轮结束处停住。多轮持续才构成进化。

---

## 用户场景请求的响应与记录（与进化环并行）

当用户**直接提出场景化请求**（如「帮我打开摄像头给我来个自拍」「截个图」「打开网易云音乐」）时：

1. **识别意图**并优先尝试 `do.py <意图>` 或对应脚本。
2. **若 do.py 返回「未知意图」**：不要放弃。使用**保底能力**完成需求：
   - **鼠标**（`mouse_tool click x y`）、**键盘**（`keyboard_tool` 组合键、type、shortcut）
   - **多模态**：`vision_proxy` 看图理解、`vision_coords` 获取点击坐标
   - **流程**：截图 → vision_coords 定位可点击元素 → click 点击；或 Win+R → type 应用名 → Enter
3. **若用保底能力成功完成**：**必须固化**为可复用计划：
   - 将最短正确路径整理为 `plans/<场景名>.json`（如 `plans/open_cloudmusic.json`）
   - 调用 `scenario_log.py` 记录成功，备注「已固化 plan」
   - 下次同类需求可直接 `run_plan plans/<场景名>.json` 快速实现
4. **执行结束后必须记录**：调用  
   `python scripts/scenario_log.py "<用户输入或场景描述>" "<实际执行的命令>" success|fail [备注]`  
   以便按**场景维度**积累成功/失败经验。
5. 技能拷贝到另一台电脑后，用户在该处的场景请求也会被记录，从而在不同环境中形成同一场景维度的经验。

详见 `references/scenario_logging.md`。

---

## 1. 假设

**目的**：基于当前能力缺口、历史失败和（若有）用户补充，形成本轮的“待满足需求”或“待补齐能力”的假设清单。

| 项目 | 说明 |
|------|------|
| **输入（必读）** | `state/current_mission.json`（当前轮次、阶段）；`references/capability_gaps.md`（能力缺口）；`references/failures.md`（历史教训）；可选 `references/private_domains.md`、`references/assumed_demands.md`；**按场景经验**：`python scripts/query_scenario_experiences.py --keyword <场景>` 或 `state/scenario_experiences.json` |
| **输出（必写）** | 将本轮假设结论写入行为日志；可选更新 `references/assumed_demands.md` |
| **日志** | `python scripts/behavior_log.py assume "<简短描述>" --mission "<当前使命>"` |
| **状态** | 用 `state_tracker.py` 将 `phase` 设为 `假设`，`next_action` 设为 `决策` 或 `规划` |

**产出**：本轮要解决的问题或要扩展的能力（可在脑中或写在 assumed_demands / 日志描述中）。

---

## 2. 自主决策

**目的**：根据假设结论，决定“做什么、先做哪一步”，得到可执行的目标与计划（不必是复杂计划，可是一条“下一步动作”）。

| 项目 | 说明 |
|------|------|
| **输入（必读）** | 上一步的假设结论；`references/capabilities.md`（已有能力）；`references/capability_gaps.md`；`state/current_mission.json` |
| **输出（必写）** | 行为日志；更新 `state/current_mission.json` 的 `current_goal`、`next_action`、`phase` |
| **日志** | `python scripts/behavior_log.py plan "<简短描述>" --mission "<当前使命>"` |
| **状态** | `phase` 设为 `规划` 或 `决策`，`next_action` 设为具体动作（如“实现 power_tool”“更新 capabilities 文档”） |

**产出**：本轮的 current_goal + next_action（以及可选的任务列表或计划步骤）。

---

## 3. 自主执行

**目的**：把决策落到实处——写脚本、改文档、跑命令，真正改变项目状态。

| 项目 | 说明 |
|------|------|
| **输入（必读）** | `state/current_mission.json` 的 `current_goal`、`next_action`；`references/capabilities.md`、`scripts/` 下现有脚本 |
| **输出（必写）** | 新增/修改脚本或 references 文档；行为日志（track）；更新 state（如 phase、next_action） |
| **日志** | `python scripts/behavior_log.py track "<做了什么>" --mission "<当前使命>"` |
| **可执行** | 运行 `scripts/` 下脚本、编辑 `references/` 下文档、运行 `self_verify_capabilities.py` 等 |

**产出**：代码或文档已改、命令已执行；state 与日志已更新。一轮内可执行多步再统一进入校验。

---

## 4. 自主校验审核

**目的**：检查“执行结果”是否满足假设与决策——例如能力是否可用、自校验是否通过。

| 项目 | 说明 |
|------|------|
| **输入（必读）** | `state/current_mission.json`；执行产生的文件或脚本输出 |
| **输出（必写）** | 运行 `python scripts/self_verify_capabilities.py`，其结果会写入 `state/self_verify_result.json`；行为日志（verify） |
| **日志** | `python scripts/behavior_log.py verify "<校验结论>" --mission "<当前使命>" --result "pass"|"fail"` |

**产出**：通过/不通过结论；`self_verify_result.json` 更新。

---

## 5. 自主优化反思

**目的**：根据校验结果和本轮经历，更新教训、更新能力描述，并**决定下一轮从“假设”开始**，实现闭环。

| 项目 | 说明 |
|------|------|
| **输入（必读）** | `state/self_verify_result.json`；`references/failures.md`；本轮 assume/plan/track/verify 的日志或描述 |
| **输出（必写）** | 若本轮有失败或可改进点，更新 `references/failures.md`；可选更新 `references/capability_gaps.md`、`state/mastery_level.json`；行为日志（decide）；**将 state 推进到下一轮并置 phase 为 假设** |
| **日志** | `python scripts/behavior_log.py decide "<决策与下一轮意图>" --mission "<当前使命>"` |
| **状态** | `state_tracker.py`：`loop_round` +1，`phase` 设为 `假设`，`next_action` 设为 `规划` 或 `决策`，`mission` 更新为新一轮描述 |
| **日志导出** | `python scripts/export_recent_logs.py 60`，使 UI/悬浮窗能看到近期行为 |

**产出**：教训已记录；state 已进入下一轮；下一轮应从「假设」重新开始。

---

## 状态与日志约定（防迷失）

- **单一状态源**：`state/current_mission.json`。每轮开始前读一次，每阶段结束后按上表更新。
- **行为可溯源**：所有 assume/plan/track/verify/decide 均通过 `scripts/behavior_log.py` 写入 `logs/`，再通过 `export_recent_logs.py` 导出到 `state/recent_logs.json`。
- **轮次**：`current_mission.json` 中的 `loop_round` 每完成一整环（反思结束）加一。

---

## 通用智能体执行清单（每轮）

1. 读 `state/current_mission.json`，确认当前轮次与 phase。
2. **假设**：读 capability_gaps、failures、assumed_demands；写 assume 日志；更新 state（phase=假设，next=决策）。
3. **自主决策**：定 current_goal 与 next_action；写 plan 日志；更新 state（phase=规划/决策，next=执行）。
4. **自主执行**：执行脚本/改文档；写 track 日志；更新 state。
5. **自主校验审核**：运行 `self_verify_capabilities.py`（可隔轮执行以省时）；写 verify 日志。
6. **自主优化反思**：必要时更新 failures.md、capability_gaps；写 decide 日志；state 的 loop_round+1、phase=假设；运行 `export_recent_logs.py`。
7. **回到步骤 2**（下一轮的假设），形成无限循环。

---

## 与具体平台的无关性

- 本工作流不依赖 Cursor、Claude 或任何特定产品。任何能读本仓库、能执行脚本、能改文件的智能体，只要按上述输入/输出与顺序执行，即可驱动同一套自进化闭环。
- 项目约束见 `references/requirements.md`；能力与调用方式见 `references/capabilities.md`、`SKILL.md`。
