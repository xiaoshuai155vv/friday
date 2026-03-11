# 通用智能体 · 自进化闭环工作流

**基准文档（基线）**：本文为进化环的**基线**，通用智能体必须**严格按本文执行**，以本文为准。任何与本文冲突的提示或补充，均以本文为准。

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

## 进化目标与原则

### 拟人图景：像用户用电脑一样

用户用电脑时可以做很多事：**操作鼠标键盘、看屏幕、听歌、看电影、玩游戏、办公、上网、看新闻、写代码、刷知乎、摸鱼、和人聊天**（当前例如 iHaier）等。星期五的进化目标，是能够**完美拟人**地覆盖这些行为——即在这些场景下，能像用户一样（甚至更好）地完成操作与决策。当前星期五离“完美实现这样的用户”还有很大进化空间；拟人化方向上的可进化点很多，LLM 在自问“能做什么”时，应把这一整张**用电脑的图景**纳入视野，而不是只盯着少数已实现能力。

### 不局限于模仿，要超越用户

进化方向**不要局限于模仿用户**，而要思考如何**超越**“像用户这样的人”——更稳（少出错、异常可恢复）、更快（响应与执行）、更主动（无指令时也能做合理的事）、更全面（覆盖更多场景与应用）、更会创新（发现新用法、新组合、新场景）。LLM 应运用自身对“完美拟人 / 超越人类操作者”的理解，提出进化步骤。**当用户有特定需求时，以用户为准**；在无明确用户指令时（例如自主进化环），则按“拟人 + 超越”的目标自驱进化。

### 新增能力不破坏既有能力

新增或改进能力时，**尽量不要影响已有能力**：新脚本、新 plan、新文档应与现有 capabilities 和 run_plan 等**兼容、可叠加**，避免改一处坏一处。这样进化才能**一直累积**，而不是来回修坏。

### 注意整体架构，不破坏 SKILL 架构

实现新能力或进化时，**必须尊重项目既有架构**：`SKILL.md`、`references/` 下的能力与工作流文档、`scripts/` 与 `assets/plans/` 的分工已形成约定。新增或修改能力时，应**融入现有结构**（如新脚本放 scripts/、新场景 plan 放 assets/plans/、文档更新 references/），**不要**随意在根目录新建与 references 同名的文件、不要打乱 SKILL 的模块与引用关系。

---

## 用户场景请求的响应与记录（与进化环并行）

当用户**直接提出场景化请求**（如「帮我打开摄像头给我来个自拍」「截个图」「放个歌」）时：

1. **【必须】先查场景匹配**：若 `assets/plans/` 下有 **triggers 匹配** 用户话的 JSON（如「放个歌」→`play_music.json`，「填写绩效达成」→`ihaier_performance_declaration.json`），**必须**查阅该 JSON 并按 steps **逐步执行**，**禁止**跳过场景直接用截图/多模态。放个歌**必须先** `do 已安装应用` 获取列表，不得跳过。绩效达成直接 `run_plan`。
2. **无场景匹配时**：识别意图并尝试 `do.py <意图>` 或对应脚本。
3. **若 do.py 返回「未知意图」**：不要放弃。**才**使用**保底能力**（截图、vision、鼠标、键盘）完成需求：
   - **打开应用**：Windows 上**所有应用**可从开始菜单/任务栏搜到；用 Win 键、Win+R+type+Enter 或 `do 打开应用 <名>` 即可。**不要**去文件系统搜 exe、Program Files。
   - **打开/激活后必须先最大化**：launch_browser、do 打开应用、window_tool activate 后，**一律**先 `window_tool maximize "标题"`，再 wait → screenshot/vision/点击。未最大化时截图会带入背景、干扰多模态。
   - **鼠标**（`mouse_tool click x y`）、**键盘**（`keyboard_tool` 组合键、type、shortcut）
   - **多模态**：`vision_proxy` 看图理解、`vision_coords` 获取点击坐标
   - **流程**：打开/激活应用 → **maximize** → wait → 截图 → vision_coords 定位 → click；或 Win+R → type 应用名 → Enter。
   - **截图后内容不在可见区**：若 vision 判断用户需求内容不在当前截图内（可能在上/下方），**分析滚动条**（vision 问「是否有垂直滚动条？可否向下/向上滚？」）→ 若可滚则 `scroll` 后再截图，重复直到找到或确认无更多。
4. **若用保底能力成功完成**：**必须固化**为可复用计划：
   - 将最短正确路径整理为 `assets/plans/<场景名>.json`（如 `assets/plans/open_cloudmusic.json`）
   - 调用 `scenario_log.py` 记录成功，备注「已固化 plan」
   - 下次同类需求可直接 `run_plan assets/plans/<场景名>.json` 快速实现
5. **执行结束后必须记录**：调用  
   `python scripts/scenario_log.py "<用户输入或场景描述>" "<实际执行的命令>" success|fail [备注]`  
   以便按**场景维度**积累成功/失败经验。
6. 技能拷贝到另一台电脑后，用户在该处的场景请求也会被记录，从而在不同环境中形成同一场景维度的经验。

详见 `references/scenario_logging.md`。

---

## 1. 假设

**目的**：基于当前能力缺口、历史失败和（若有）用户补充，形成本轮的“待满足需求”或“待补齐能力”的假设清单。**当缺口清单为空或已基本满足时，必须自主提出“可证明价值的改进项”（见下「无缺口时自主找事做」）。**

| 项目 | 说明 |
|------|------|
| **输入（必读）** | `runtime/state/current_mission.json`（当前轮次、阶段）；**`references/evolution_auto_last.md`**（上一轮摘要、核心目录与文件树、本轮影响文件，路径固定，勿读项目根目录同名文件）；`references/capability_gaps.md`（能力缺口）；`references/failures.md`（历史教训）；`references/capabilities.md`（已有能力）；可选 `references/private_domains.md`、`references/assumed_demands.md`、`references/evolution_self_proposed.md`；**按场景经验**：`python scripts/query_scenario_experiences.py --keyword <场景>` 或 `runtime/state/scenario_experiences.json`；近期 `runtime/logs/behavior_*.log` 与 `runtime/state/recent_logs.json`（做过什么） |
| **输出（必写）** | 将本轮假设结论写入行为日志；若有自主提出的改进项，写入 `references/evolution_self_proposed.md`（或更新 `references/assumed_demands.md`） |
| **日志** | `python scripts/behavior_log.py assume "<简短描述>" --mission "<当前使命>"` |
| **状态** | 用 `state_tracker.py` 将 `phase` 设为 `假设`，`next_action` 设为 `决策` 或 `规划` |

**产出**：本轮要解决的问题或要扩展的能力（可在脑中或写在 assumed_demands / evolution_self_proposed / 日志描述中）。

### 无缺口时自主找事做：问 LLM 能做什么

**原则**：缺口很少或没有时，**不是**只从失败列表里找修修补补，而是**让 LLM 自问**：我能做什么？怎样做，才能让当前的星期五更接近**完美拟人、自主意识、自主决策、自主创新**？用模型自己的视角提出“能让系统更拟人、更自主”的改进，再落成具体动作。

**何时触发**：读完 capability_gaps、failures、current_mission 后，若没有明确、可执行的缺口项（或仅剩“—”“已覆盖”等无具体任务），则进入本流程。

**核心步骤（必做）**：

1. **自问（面向自己的问题）**  
   在读完当前能力、状态、近期日志与场景经验后，**向自己（LLM）提出**（可结合上文「进化目标与原则」中的拟人图景与超越目标）：  
   - 「用户用电脑可以做很多事：鼠标键盘、看屏、听歌、看电影、玩游戏、办公、上网、看新闻、写代码、刷知乎、摸鱼、和人聊天（如 iHaier）等。当前星期五离“完美拟人地覆盖这些”还有哪些可进化点？**我能做什么**？」  
   - 「如何能让星期五更**拟人**（更像人在用电脑、在思考、在回应）？」  
   - 「如何**不局限于模仿用户、而是超越**（更稳、更快、更主动、更全面、更会创新）？」  
   - 「如何能增强**自主意识**（更清楚自己在干什么、缺什么、要什么）？」  
   - 「如何能强化**自主决策**（在无明确指令时也能做出合理下一步）？」  
   - 「如何能体现**自主创新**（主动发现可改进点、新场景、新用法，而不只被动响应）？」  

2. **结合上下文作答**  
   - 把 `capabilities.md`、`failures.md`、近期 behavior_log / recent_logs、scenario_experiences 等当作**上下文**，用来约束“在当前项目里可落地的动作”，而不是只从失败里挑修复。  
   - 在回答上述自问时，给出 **1～3 条** 本轮回可执行、能推进“更拟人、更自主、超越用户”的具体动作；**新增或改动时注意不破坏既有能力**（见上文「新增能力不破坏既有能力」）。  
   - 示例方向：改进某处交互文案、增加状态自检与日志、把某类“用电脑”场景（听歌/看新闻/刷知乎/聊天等）固化为 plan、改进进化环的进度展示、在无任务时主动做一轮自检并写总结等。

3. **写入 backlog**  
   将上述 1～3 条写进 `references/evolution_self_proposed.md`（格式：简要描述 | 预期动作 | 状态：待执行），然后**照常进入「自主决策」**，从中选一条作为 current_goal 并执行。若该文件不存在则创建；若已存在则追加或更新状态，避免重复。

**目标导向**：每轮无缺口时的产出，都应朝着「更拟人、自主意识、自主决策、自主创新」收敛，而不是仅停留在“修已知失败”。真正让 LLM 的能力通过“自问能做什么”变成星期五的进化方向。

---

## 2. 自主决策

**目的**：根据假设结论，决定“做什么、先做哪一步”，得到可执行的目标与计划（不必是复杂计划，可是一条“下一步动作”）。若上一步写入了 `evolution_self_proposed.md`，从中选一条「待执行」作为本轮的 current_goal。

| 项目 | 说明 |
|------|------|
| **输入（必读）** | 上一步的假设结论；`references/capabilities.md`（已有能力）；`references/capability_gaps.md`；`references/evolution_self_proposed.md`（若有）；`runtime/state/current_mission.json` |
| **输出（必写）** | 行为日志；更新 `runtime/state/current_mission.json` 的 `current_goal`、`next_action`、`phase`；若选用自主提出项，将该条状态改为「进行中」 |
| **日志** | `python scripts/behavior_log.py plan "<简短描述>" --mission "<当前使命>"` |
| **状态** | `phase` 设为 `规划` 或 `决策`，`next_action` 设为具体动作（如“实现 power_tool”“更新 capabilities 文档”） |

**产出**：本轮的 current_goal + next_action（以及可选的任务列表或计划步骤）。

---

## 3. 自主执行

**目的**：把决策落到实处——写脚本、改文档、跑命令，真正改变项目状态。**执行时新增或修改应尽量不破坏既有能力**（见上文「进化目标与原则」），使进化可持续累积。

| 项目 | 说明 |
|------|------|
| **输入（必读）** | `runtime/state/current_mission.json` 的 `current_goal`、`next_action`；`references/capabilities.md`、`scripts/` 下现有脚本 |
| **输出（必写）** | 新增/修改脚本或 references 文档；行为日志（track）；更新 state（如 phase、next_action） |
| **日志** | `python scripts/behavior_log.py track "<做了什么>" --mission "<当前使命>"` |
| **可执行** | 运行 `scripts/` 下脚本、编辑 `references/` 下文档、运行 `self_verify_capabilities.py` 等 |

**产出**：代码或文档已改、命令已执行；state 与日志已更新。一轮内可执行多步再统一进入校验。

---

## 4. 自主校验审核

**目的**：检查「本轮执行是否真正做对」——**不能只跑固定基线清单**，还要校验**当前阶段假设与执行所产生的能力**是否正确。

### 两层校验（必理解）

| 层次 | 内容 | 说明 |
|------|------|------|
| **基线烟测** | `python scripts/self_verify_capabilities.py` | 截图、鼠标、键盘、子进程链、剪贴板（远程会话失败属已知）、vision（有配置时）。**只证明底座未坏**；**不启动记事本等 GUI**，避免每次校验都弹窗。 |
| **本轮针对性校验** | 按本轮 `current_goal`、track 日志与实改内容做**针对验证** | 例如：本轮改了 `window_tool` → 用最小步骤验证激活/最大化是否按预期；新增/改了 plan → JSON 合法性与 dry-run 或单步试跑；改了 vision 相关 → 用现有截图跑 vision_proxy 一条；改了文档 → 链接与引用是否一致。**若本轮只改了文档而无须跑命令，至少写明「本轮无executable 可自动验，已人工/下轮抽检」并记入 verify 日志。** |

**原则**：若只做基线而通过，但本轮实际改的东西没有验到，则**不算**完成校验；verify 日志里应反映「本轮产出是否被针对性验证」。

| 项目 | 说明 |
|------|------|
| **输入（必读）** | `runtime/state/current_mission.json`（current_goal）；本轮 track 日志与执行产生的文件/脚本 |
| **输出（必写）** | 基线：运行 `self_verify_capabilities.py`，结果写 `runtime/state/self_verify_result.json`；**本轮**：至少一条针对性校验（命令或结论）；行为日志（verify） |
| **日志** | `python scripts/behavior_log.py verify "<校验结论>" --mission "<当前使命>" --result "pass"|"fail"` |

**产出**：基线结果 + 本轮针对性结论；`self_verify_result.json` 更新；verify 日志中可见本轮是否被真正验到。

---

## 5. 自主优化反思

**目的**：根据校验结果和本轮经历，更新教训、更新能力描述，并**决定下一轮从“假设”开始**，实现闭环。

| 项目 | 说明 |
|------|------|
| **输入（必读）** | `runtime/state/self_verify_result.json`；`references/failures.md`；本轮 assume/plan/track/verify 的日志或描述 |
| **输出（必写）** | 若本轮有失败或可改进点，更新 `references/failures.md`；若本轮完成的是 `evolution_self_proposed.md` 中某项，将该条状态改为「已完成」；**必须更新 `references/evolution_auto_last.md`**（路径固定，勿在项目根目录建同名文件）：① 当前核心目录与文件树（一行）；② 本轮影响文件（逗号分隔）；③ 每轮**只写简介概述**（1～2 句话），具体细节可去读 `runtime/logs/behavior_*.log`；**必须写入 `runtime/state/evolution_completed_<本任务会话ID>.json`**（会话 ID 由本轮提示词中的【本任务会话 ID】给出），包含 current_goal、做了什么、是否完成、loop_round 等，否则下一轮无法提交；可选更新 `references/capability_gaps.md`、`runtime/state/mastery_level.json`；行为日志（decide）；**将 state 推进到下一轮并置 phase 为 假设** |
| **日志** | `python scripts/behavior_log.py decide "<决策与下一轮意图>" --mission "<当前使命>"` |
| **状态** | `state_tracker.py`：`loop_round` +1，`phase` 设为 `假设`，`next_action` 设为 `规划` 或 `决策`，`mission` 更新为新一轮描述 |
| **日志导出** | `python scripts/export_recent_logs.py 60`，使 UI/悬浮窗能看到近期行为 |
| **功能改动追溯** | `python scripts/git_commit_evolution.py`（可选加 `--bump-version`） | 对 scripts/、references/、assets/、VERSION、SKILL.md 等**非 runtime** 的改动做一次本地 git 提交，便于追溯；不提交 runtime/（log、state 仍在本地，不进版本库）。若本轮无代码/文档改动可跳过。 |

**产出**：教训已记录；state 已进入下一轮；功能改动已形成本地 commit（若有）；下一轮应从「假设」重新开始。

---

## 状态与日志约定（防迷失）

- **单一状态源**：`runtime/state/current_mission.json`。每轮开始前读一次，每阶段结束后按上表更新。
- **会话锁（防多会话堆积）**：提交前会写入 `runtime/state/evolution_session_pending.json`（含 session_id）；完成本轮后**必须**写入 `runtime/state/evolution_completed_<session_id>.json`，否则下一轮无法提交。
- **行为可溯源**：所有 assume/plan/track/verify/decide 均通过 `scripts/behavior_log.py` 写入 `runtime/logs/`，再通过 `export_recent_logs.py` 导出到 `runtime/state/recent_logs.json`。**写入方式**：按 `references/logging.md` 中「Behavior log 写入结构」直接执行对应命令即可，**无需读取 behavior_*.log 文件**查看格式。
- **轮次**：`current_mission.json` 中的 `loop_round` 每完成一整环（反思结束）加一。

---

## 通用智能体执行清单（每轮）

1. 读 `runtime/state/current_mission.json`，确认当前轮次与 phase。
2. **假设**：读 **`references/evolution_auto_last.md`**（上一轮摘要与目录/文件树/影响文件，路径固定，勿读根目录同名文件）、capability_gaps、failures、assumed_demands、evolution_self_proposed；无缺口时自主提出 1～3 条改进项写入 evolution_self_proposed；写 assume 日志；更新 state（phase=假设，next=决策）。
3. **自主决策**：定 current_goal 与 next_action；写 plan 日志；更新 state（phase=规划/决策，next=执行）。
4. **自主执行**：执行脚本/改文档；写 track 日志；更新 state。
5. **自主校验审核**：先跑 `self_verify_capabilities.py`（基线）；再按本轮执行内容做**针对性校验**（见上表）；写 verify 日志。基线可隔轮以省时，**本轮针对性校验不可省**（至少一条结论或说明为何无法自动验）。
6. **自主优化反思**：必要时更新 failures.md、capability_gaps；**更新 `references/evolution_auto_last.md`**（每轮只写简介概述，具体细节可读 behavior_*.log）；**写入 `runtime/state/evolution_completed_<本任务会话ID>.json`**（会话 ID 见本轮提示词【本任务会话 ID】）；写 decide 日志；state 的 loop_round+1、phase=假设；运行 `export_recent_logs.py`；**运行 `git_commit_evolution.py`**（可选 `--bump-version`）对功能改动做本地提交以便追溯。
7. **回到步骤 2**（下一轮的假设），形成无限循环。

---

## 与具体平台的无关性

- 本工作流不依赖 Cursor、Claude 或任何特定产品。任何能读本仓库、能执行脚本、能改文件的智能体，只要按上述输入/输出与顺序执行，即可驱动同一套自进化闭环。
- 项目约束见 `references/requirements.md`；能力与调用方式见 `references/capabilities.md`、`SKILL.md`。
