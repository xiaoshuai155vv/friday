# 进化环与 Claude Code 对接实施方案

## 一、目标

用户可在**悬浮球**上开启「自主进化环」，由星期五**主动向 Claude Code（通过 CCR 项目）提交需求**，由 Claude Code 在本项目内执行进化环（假设→决策→执行→校验→反思），实现自我完善。

## 二、当前项目（星期五）已具备能力

| 维度 | 能力 |
|------|------|
| **进化环流程** | `references/agent_evolution_workflow.md` 定义完整：假设→自主决策→自主执行→自主校验审核→自主优化反思；state（current_mission.json）、behavior_log、export_recent_logs、self_verify_capabilities 等已就绪。 |
| **脚本与能力** | 鼠标、键盘、截图、vision、run_plan、do、窗口/进程、剪贴板、文件等；capabilities.md、SKILL.md 已文档化。 |
| **状态与日志** | runtime/state/current_mission.json、runtime/logs/behavior_*.log、recent_logs.json；state_tracker、behavior_log.py、export_recent_logs.py。 |
| **UI** | Qt 悬浮球（friday_floating_qt.py）、OneCall 多模态、过程/结果弹框；可扩展菜单与入口。 |
| **缺项** | **主动调用 Claude Code 的能力**：当前进化环需由「人或其他智能体在 Cursor/Claude Code 中」读 workflow 并执行；缺少「星期五主动给 Claude Code 派活」的通道。 |

## 三、CCR 项目（D:\ai\数字化资产\ccr）可提供的接口

- **Claude Code UI + API**：基于 claudecodeui，集成 CCR（Claude Code Router），可用本地模型与 Claude Code 交互。
- **与 Claude Code 交互方式**：  
  - **WebSocket**：前端发 `{ type: 'claude-command', command: "用户消息", options: { cwd, sessionId, ... } }`，服务端调用 `queryClaudeSDK(command, options, ws, ccrReady)` 流式返回。  
  - **HTTP API**：`POST /api/agent`（需 `x-api-key`），body：`{ projectPath, message, provider: 'claude', stream: false }`，在指定项目目录下执行一条「消息」任务，非流式时返回 `{ messages, tokens }`。
- **结论**：星期五通过 **HTTP 调用 CCR 的 POST /api/agent**，传入本项目根目录为 `projectPath`、进化任务为 `message`，即可让 Claude Code 在本项目内跑一轮进化环。

## 四、方案选型

- **直接调用 CCR API**：在星期五内用脚本（如 Python `requests`）请求 `http://localhost:3001/api/agent`（或用户配置的 CCR 地址），无需再起一层独立「中间服务」；实现简单、易维护。
- **悬浮球侧**：在**新线程/工作线程**中发起 HTTP 请求并轮询或等待结果，避免阻塞 UI；必要时可封装为「进化环客户端」脚本供球内调用。
- **不采用**：再包一层与 CCR 同级的「中间层服务」；当前需求下直接调 API 即可。

## 五、实施步骤

### 步骤 1：配置与约定

- **配置文件**：`runtime/config/evolution_loop.json`（或与现有 state 同目录），内容示例：
  - `ccr_base_url`: CCR 服务地址，默认 `http://localhost:3001`
  - `ccr_api_key`: 调用 `/api/agent` 所需的 API Key（在 CCR 的 API Keys 管理中创建）
  - `friday_project_path`: 星期五项目根目录（即 `projectPath` 传给 CCR）
  - `evolution_prompt`: 可选，默认一段「请按 agent_evolution_workflow 执行一轮进化环…」的提示
  - `auto_interval_seconds`: 自动模式下的间隔秒数，0 表示不自动轮询
- **API Key**：CCR 端需已配置 API Key 并启用（在 CCR 的 API Keys 管理中创建）；星期五仅存储并随请求携带，不实现 Key 发放逻辑。将 Key 填入 `evolution_loop.json` 的 `ccr_api_key` 即可。

### 步骤 2：进化环客户端脚本

- **脚本**：`scripts/evolution_loop_client.py`
  - 读 `runtime/config/evolution_loop.json`（若不存在则使用默认 base_url + 无 key，并提示配置）。
  - 请求 `POST {ccr_base_url}/api/agent`，body：`projectPath=friday_project_path`，`message=evolution_prompt`（或命令行传入的一条 message），`stream=false`，headers：`x-api-key: ccr_api_key`。
  - 解析 JSON 响应，将「本轮结果」简要写回 state 或日志（可选）；返回码非 2xx 或超时则写失败日志并返回非 0。
  - 可支持参数：`--once`（只跑一轮）、`--message "自定义任务"`（覆盖默认 evolution_prompt）。
- **用途**：既可被悬浮球「开启自主进化环」时在后台线程中调用，也可在命令行单独执行测试。

### 步骤 3：悬浮球入口与后台触发

- **入口**：在悬浮球右键菜单（或 OneCall 相关入口）增加「开启自主进化环」。
  - 行为：若当前未开启，则「开启」：写入/更新 state 或 config 中的「自动进化已开启」标记，并**启动一次** evolution_loop_client（在新线程或 QThread 中），避免阻塞 UI；若已开启，则可改为「停止自主进化环」并清除标记。
- **自动轮询（可选）**：若配置了 `auto_interval_seconds > 0`，在「开启」后启动定时器，每隔 N 秒在后台线程中调用一次 evolution_loop_client，直到用户「停止」或关闭应用。
- **状态展示**：可在悬浮球或 OneCall 上显示简要状态，例如「已向 Claude Code 提交进化任务」「进化环运行中」「本轮完成」或「已停止」；实现方式可为更新 phase 文案或弹 Toast。

### 步骤 4：默认进化提示词

- 在 config 或脚本内写死一段默认 `evolution_prompt`，例如：
  - 「请读取本项目 references/agent_evolution_workflow.md，按其中「通用智能体执行清单」执行**一轮**进化环：1）读 current_mission.json 2）假设：读 capability_gaps、failures，写 assume 日志 3）自主决策：定 current_goal 与 next_action，写 plan 日志 4）自主执行：执行脚本/改文档，写 track 日志 5）自主校验：运行 self_verify_capabilities.py（基线）+ 按本轮执行内容做针对性校验，写 verify 日志（见 workflow「自主校验审核」两层） 6）自主反思：更新 failures 等，写 decide 日志，loop_round+1，phase 设回假设。请在本项目目录下执行并写入 state 与 behavior_log。」
- 用户可在 config 中覆盖 `evolution_prompt` 以自定义任务说明。

### 步骤 5：文档与自检

- 在 `references/capabilities.md` 或 SKILL.md 中增加一条：**自主进化环（Claude Code）**：通过配置 CCR 地址与 API Key，可从悬浮球「开启自主进化环」，向 Claude Code 提交进化任务；详见 `references/evolution_loop_claude_code_integration.md`。
- 自检：在 CCR 已启动、API Key 已配置的前提下，命令行执行 `python scripts/evolution_loop_client.py --once` 能成功收到 2xx 并看到返回内容（或日志中有记录）。

## 六、依赖与前置条件

- **CCR 服务**：需已启动（如 `npm run ccr` + 前端/服务器，或 complete-package 的一键启动），且 `/api/agent` 可访问（默认端口 3001）。
- **API Key**：在 CCR 的 API Keys 管理中创建 Key，并将该 Key 填入星期五的 `evolution_loop.json` 的 `ccr_api_key`。
- **Python**：星期五脚本运行环境需具备 `requests`（或标准库 `urllib.request`）以便发 HTTP；若用 `urllib` 则无额外 pip 依赖。

## 七、任务完成与进度

- **任务何时算完成**：当前使用 `stream=false` 调用 CCR，即星期五发出一条 HTTP 请求后**等待 CCR 整轮执行完毕**再返回。因此「任务完成」= 该 HTTP 请求返回时（成功或失败）。CCR 不会通过文件或推送主动通知星期五；完成信号就是客户端收到的响应。
- **悬浮球如何知道完成**：后台线程里 `evolution_loop_client` 返回后，会通过 `finished_signal` 回调到 UI，悬浮球在 `_on_evolution_finished` 中刷新 state、托盘提示「本轮完成」或「进化环失败」；同时写入 `runtime/state/evolution_last_status.json`（status: ok/timeout/error），供**过程·结果**弹框与防重复提交使用。
- **过程·结果里的进化环状态**：打开「过程 · 结果」弹框时，首行会显示**最近进化环请求**：成功（本轮已完成）、超时（CC 可能仍在执行，请勿急于再提交）、或失败。便于判断上一轮是否在客户端侧已完成，避免误以为没完成又开新会话。
- **超时说明**：「进化环 Fail: timeout」表示**客户端**（或 Worker 子进程）等待 CCR 响应超时（默认 300s，可配 `evolution_loop.json` 的 `request_timeout_seconds`）。**CC 端可能仍在执行**，只是我们这边先断开了。超时后：手动再提交会弹出提示「上一轮请求已超时，CC 可能仍在执行；若现在提交会开启新会话」；自动进化环会在 15 分钟内跳过本轮再检查，减少多会话堆积。
- **是否有流式进度**：当前无。若将来改用 `stream=true`，可解析 SSE 流并在悬浮球上展示「执行中」的阶段性进度（需额外实现 SSE 解析与 UI 更新）。

## 八、自主假设与用户参与

- **进化环的「假设」从哪来**：按 `agent_evolution_workflow.md`，每轮**假设**阶段会**自主**读取 `references/capability_gaps.md`、`references/failures.md` 以及 `current_mission.json` 等，形成本轮「待满足需求 / 待补齐能力」。即：**是否优化、优化什么方向，由能力缺口与历史失败驱动**，不需要用户每轮都下指令。
- **用户如何参与**：点击「提交一轮进化环」时会弹出**可选输入框**，用户可填写「本轮补充需求或优先级」（如「优先改进 vision 校准」「本轮重点补截图相关能力」）。留空则完全按 workflow 自主假设。填写内容会以「【用户本轮的补充或优先级】」追加到发给 CCR 的 message 中，供 Claude Code 在本轮决策时参考。
- **自动进化环**：悬浮球菜单提供「开启自动进化环」/「关闭自动进化环」。开启后，会按 `evolution_loop.json` 中的 `auto_interval_seconds`（默认 300）**定时**触发一轮进化环（仅当当前没有任务在跑时）。**自动提交时客户端会带 `--auto-evolution`**：在发给 CC 的 message 末尾自动拼接「上一轮」上下文——`current_mission.json` 的轮次/阶段、最近 behavior 中的 track/decide 摘要、`evolution_self_proposed.md` 里已标「已完成」的项，并明确要求**不要做与上一轮已完成的同一件事**，减少重复劳动。

## 九、风险与注意

- **API Key 安全**：仅存于本机 `runtime/config/`，不要提交到版本库；可加入 .gitignore。
- **超时**：单轮进化可能较长，客户端默认 300s（`evolution_loop.json` 的 `request_timeout_seconds`），可改为 600/900。超时后 CC 可能仍在跑，过程·结果会显示「最近进化环请求: 超时」，且 15 分钟内再提交会提示、自动进化会跳过。
- **并发**：同一时间只提交一轮任务；若上一轮超时，自动进化环 15 分钟内不重复提交，避免 CC 侧多会话堆积。

---

**实施顺序**：先完成步骤 1 配置约定与步骤 2 客户端脚本，再在悬浮球上接步骤 3；最后更新文档与自检（步骤 4、5）。
