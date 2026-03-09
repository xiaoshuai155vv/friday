---
name: friday-self-evolution
description: |
  依托用户电脑的自我进化技能，形成「主动假设→主动规划→任务追踪→完成校验→主动决策」闭环，满足用户所有需求；未满足不反馈、一直自进化。始终知道当前要干什么，不迷失。宗旨与约束见 SKILL 内「本技能宗旨与约束」。
  触发：星期五、贾维斯、电脑操作、自我进化、主动假设、任务追踪、闭环生态、技能进化、当前在干什么、私域知识、行为日志溯源。
---

# 星期五 · 自我进化技能

**核心信条：始终知道我们当前要干什么。** 在多轮循环中不迷失。

---

## 本技能当前可做到的（明确范围）

本技能**主动承接用户需求**，在**自主决策**下执行，并持续**进化**。具体包括：

| 维度 | 可做到的 |
|------|----------|
| **主动承接用户需求** | 响应用户场景请求（如自拍、截图、打开应用、网页/WebSearch 等）；按「已有支持的场景 → 保底场景（开浏览器+鼠标键盘截图多模态）→ 明确能力」的优先级选择执行方式；执行后记录场景与结果，形成可复用的场景经验。 |
| **自主决策** | 按进化环（假设 → 规划 → 执行 → 校验 → 反思 → 决策）自主推进；读取 `state/current_mission.json`、`capability_gaps`、`failures`、场景经验等，决定下一步目标与动作；不依赖用户逐步指令，可多轮闭环直至任务达成或能力补齐。 |
| **进化** | 在闭环中扩展能力（脚本、do、capabilities 文档）；按场景积累成功/失败经验（`scenario_log` / `query_scenario_experiences`）；从失败中写教训（`failures.md`）并在后续规划中规避；支持便携环境与跨机复制，经验与能力随项目迁移。 |

**能力边界（当前可做到）**：在 Windows 上具备鼠标、键盘、截图、多模态看图、剪贴板、窗口/进程、电源、音量/亮度、通知、网络、注册表、文件、计划执行（run_plan）等能力；可通过「打开浏览器 + 截图 + 多模态 + 点击/输入」完成网页与 WebSearch 类需求。详见下方「已有支持的场景」与 [references/capabilities.md](references/capabilities.md)。

---

## 本技能宗旨与约束（通用智能体必读）

以下为技能的设计宗旨，**每次由通用智能体驱动本技能时均应遵循**，确保沿同一道路贯彻执行。

| 维度 | 内容 |
|------|------|
| **作用** | 引导、帮助当前技能进行自我进化。 |
| **目标** | 当前技能依托用户电脑，满足用户**所有**需求。 |
| **方法** | 主动假设用户需求 → 列出所需能力清单 → 自动规划实施路线 → 任务跟踪完成闭环 → 主动校验与测试完成情况 → **直到满足所有假想需求**；若未满足，**不要向用户反馈**，一直自进化。 |
| **核心** | 形成闭环生态：**主动假设 → 主动规划 → 任务追踪跟进 → 完成情况校验审核 → 主动决策**。每个模块独立发展进化，基础上依托**电脑 + LLM** 完成拟人化的所有假设。 |
| **私域与用户补充** | 部分知识 LLM 可能不知道（如办公平台 ihaier 等），见 `references/private_domains.md` 按需加载；**支持用户补充需求假设**，纳入闭环并回环实现。 |
| **注意** | **吃一堑长一智**，从失败中吸取教训（见 `references/failures.md`）；善于**跟踪和使用文档**来自我管理；可参考 **skill-creator** 的整体设计思路与架构；适当**抽象通用能力**（如鼠标、键盘、屏幕相关）支持自己；可配置**备用多模态模型**，以便拟人理解和使用界面。 |
| **日志与溯源** | **记录所有行为**，便于溯源；`scripts/behavior_log.py` 写 `logs/`，详见 `references/logging.md`。 |
| **UI** | 类似贾维斯/星期五的**科幻主体**，不断自我完善；思考能力由当前 LLM 决定，不在 UI 上显示年龄或智商阶段。 |
| **防迷失** | **始终知道我们当前要干什么**；状态见 `state/current_mission.json`，每次行动前后读写，避免多轮循环中迷失。 |

上述宗旨与 `references/requirements.md` 中的项目约束一并适用；闭环执行细节见 `references/agent_evolution_workflow.md`。

---

## 通用智能体：驱动本技能请先读此文档

若你作为**通用智能体**驱动本技能的自进化闭环，请**优先阅读**：

**`references/agent_evolution_workflow.md`**

该文档说明进化环（假设 → 自主决策 → 自主执行 → 自主校验审核 → 自主优化反思 → 回到假设）及每一阶段的输入、输出与执行清单。按其中步骤执行即可形成无限进化循环。读完该文档后再按需查阅本 SKILL 其余能力与脚本说明。

**必守约定**：① **看图理解必须用本技能 vision**：运行环境（如 Claude Code）可能**无法直接读取或展示截图/图片**，不要尝试直接读截图文件；一律用 `python scripts/vision_proxy.py <图片路径> "<问题>"`（通用看图）或 `python scripts/vision_coords.py <图片路径> "<问题>"`（**获取点击坐标**，内部多轮取中位数）或 run_plan 中的 vision 步骤。② **键盘组合键**：`keyboard_tool` 使用**虚拟键码**（如 `keys 17 75` 表示 Ctrl+K），见 capabilities 或 `keyboard_tool shortcut ctrl+k`。③ **激活窗口后先最大化**再截图/多模态，见 private_domains 与各 ihaier 计划。④ **ihaier 窗口**：主窗口标题是「**办公平台**」，激活请用 `window_tool activate "办公平台"` 或 `activate_process iHaier2.0`，**不要用** `activate "ihaier"`（会找不到窗口）。

---

## 使用此技能时需自动运行（必读）

**使用本技能时，需自动运行**以下命令以展示 **FRIDAY 的执行阶段与过程**（当前使命、阶段、轮次等）：

```text
python scripts/friday_floating_qt.py
```

其中 **`python` 为项目内预先打包的解释器**：若项目根存在 `python/python.exe`，请使用 `python\python.exe scripts\friday_floating_qt.py` 或 `python scripts/run_with_env.py friday_floating_qt`；无便携环境时使用系统 `python`。运行后会出现**圆形置顶悬浮窗**，实时显示当前阶段、使命、轮次；双击可查看过程/日志。

**使用本技能前需先启动服务（可选）**：若需本地 HTTP 服务与自动拉起悬浮窗，可在技能目录下执行 `python scripts/serve.py`（python 同上，优先用项目内打包的）。服务启动后会自动打开上述悬浮窗。**推荐安装 PyQt5**（项目内 `python` 已装或系统 `pip install PyQt5`）以使用**原生 GUI 版**（无 WebView、真透明、网格球+环+光球）；未装 PyQt5 时自动回退到 WebView 版（需 `pywebview`）。

**使用本技能时**：自闭环需**多轮持续**，不得在一轮结束后向用户「总结并结束」。每轮 decide 后更新 state、写入日志，并立即进入下一轮假设/规划。

**通用智能体驱动闭环**：按上文「通用智能体：驱动本技能请先读此文档」指向的 **references/agent_evolution_workflow.md** 执行进化环即可。

**场景记录**：当用户提出**场景化请求**（如「帮我打开摄像头给我来个自拍」）时，在响应该请求并执行完对应能力后，**必须**调用 `scripts/scenario_log.py` 记录场景与结果（成功/失败），从而按**场景维度**积累经验；规划时可使用 `scripts/query_scenario_experiences.py --keyword <场景>` 查阅历史。详见 `references/scenario_logging.md`。

## 依赖与安装

以下为需要**额外安装**的依赖（`pip install`），与对应能力。技能目录下提供 `requirements.txt`，可 `pip install -r requirements.txt` 安装推荐依赖。

| 依赖 | 用途 | 是否必须 |
|------|------|----------|
| **PyQt5** | 悬浮窗**原生 GUI 版**：圆形、透明、托盘右键退出、网格球动画；不依赖 WebView | **推荐**（不装则用下一条） |
| **pywebview** | 悬浮窗**回退版**：无 PyQt5 时用浏览器内核内嵌 Friday UI；Windows 下透明可能不生效 | 可选（仅当未装 PyQt5 且需悬浮窗时） |
| 多模态 API | `vision_proxy.py` 看图问答：需在 `scripts/vision_config.json` 或环境变量中配置 API（见 `assets/vision_config.example.json`），无额外 pip 包要求 | 按需配置 |

- **悬浮窗**：**`scripts/launch_friday_floating.py` 默认直接启动 Qt 版**（`friday_floating_qt.py`），即圆形原生 GUI 悬浮球；仅当无 PyQt5 时才回退到 pywebview 版（`scripts/friday_floating.py`）。由 `serve.py` 自动拉起时同样优先 Qt 版。
- **一键安装推荐**：`pip install -r requirements.txt`（当前主要为 PyQt5）。

## 命令行编码（避免中文乱码）

在 Windows 下从 CMD/PowerShell 运行本技能脚本时，控制台默认多为 GBK，脚本输出 UTF-8 中文会出现乱码（如 run_plan、vision 结果、日志打印等）。**建议提前设置编码**后再执行：

| 方式 | 说明 |
|------|------|
| **方式一（推荐）** | 执行前设置环境变量：CMD 下 `set PYTHONIOENCODING=utf-8`，PowerShell 下 `$env:PYTHONIOENCODING="utf-8"`，再运行 `python scripts/run_plan.py ...` 等。 |
| **方式二** | 将控制台代码页改为 UTF-8：CMD 中先执行 `chcp 65001`，再运行脚本。 |
| **方式三** | 由自动化/通用智能体调用时，启动子进程时传入 `env={**os.environ, "PYTHONIOENCODING": "utf-8"}`（或等效），确保 stdout/stderr 为 UTF-8。 |

**推荐**：通过 `python scripts/run_with_env.py <脚本名> [参数...]` 运行脚本时，已自动为子进程设置 `PYTHONIOENCODING=utf-8`，无需再手动设置。若直接使用 `python scripts/run_plan.py ...` 等，则需按上表提前设置编码，run_plan、vision 输出、scenario_log 等打印的中文方可正常显示。

**为什么你本机执行不乱码、agent 执行时乱码？** 乱码取决于**运行命令时所在终端（进程）的代码页**：你在本机 PowerShell 里直接跑 `vision_proxy.py` 时，该终端可能是 UTF-8（或你已执行过 `chcp 65001`），所以中文正常显示；当由 Cursor/Claude Code 等在「另一个终端」里执行 run_plan 时，该终端往往是新建进程、默认 GBK 代码页，同一段 UTF-8 输出就会被当成 GBK 显示成乱码。**执行时已做的编码保障**：① run_plan 调用所有子进程（vision_proxy、window_tool 等）时都会传入 **`PYTHONIOENCODING=utf-8`**，子进程 stdout 以 UTF-8 输出；② vision_proxy 启动时会**强制将 stdout/stderr 设为 UTF-8**（`reconfigure`），这样无论由谁在何种环境下执行，vision 的输出字节都是 UTF-8，run_plan 捕获后写入 **`state/vision_last_output.txt`** 的内容应为正确中文。若控制台仍乱码，可直接打开该文件查看；若该文件曾乱码，更新后应已修复。

## 便携运行环境（复制到别机直接使用）

可将 **Python 解释器 + 已安装依赖** 放入项目目录，整份项目复制到另一台 Windows 后**无需**在该机安装 Python 或执行 pip，直接使用。

| 情况 | 通用智能体应如何运行脚本 |
|------|---------------------------|
| 项目根存在 `python/python.exe` | **直接使用**：`python\python.exe scripts\do.py 截图` 或 `python scripts/run_with_env.py do 截图`。**勿使用** `python python/python.exe scripts/...`（会误将 exe 当脚本执行报错）；应使用 `python\python.exe scripts\xxx.py` 或 `run_with_env.py`。**不要**依赖目标机系统 Python 或 pip。 |
| 不存在 `python/` | 使用目标机 `python`，按需 `pip install -r requirements.txt`。 |

**推荐**：运行本技能脚本时统一用  
`python scripts/run_with_env.py <脚本名> [参数...]`  
（例如 `python scripts/run_with_env.py do 截图`）。  
`run_with_env.py` 会自动选用项目内 `python/python.exe`（若存在），否则使用当前解释器。  

如何在本机打出便携环境（一次性）：见 **references/portable_env.md**（Windows 嵌入式包解压到 `python/`，pip 安装依赖后，整份项目拷到别机即可）。

## 作用与目标

- **作用**：引导当前技能进行自我进化。
- **目标**：依托用户电脑 + LLM，满足用户所有需求；未满足时不向用户反馈，持续自进化直到满足。
- **方法**：主动假设用户需求 → 列出能力清单 → 自动规划实施路线 → 任务跟踪完成闭环 → 主动校验与测试 → 不满足则继续进化。

## 闭环生态（五模块）

每个模块独立发展进化，形成闭环：

| 模块         | 职责 |
|--------------|------|
| **主动假设** | 假设用户需求（含用户补充的假设），维护私域知识（见 references/private_domains.md）按需加载。 |
| **主动规划** | 根据假设生成能力清单与实施路线。 |
| **任务追踪** | 跟踪任务状态，使用文档/状态文件自我管理，形成闭环。 |
| **完成校验** | 审核完成情况，测试是否满足假想需求。 |
| **主动决策** | 根据校验结果决定下一轮假设/规划或继续执行，吃一堑长一智。 |

## 当前要干什么（防迷失）

- **状态位置**：`state/current_mission.json`（由 `scripts/state_tracker.py` 维护）。
- **每次行动前**：读取当前使命与当前任务，再执行。
- **每次行动后**：更新状态与 `references/state.md` 或日志，便于下一轮或其它智能体接续。
- **长任务**：在文档中显式写「当前阶段」「本轮目标」「下一步」，避免在多轮中丢失上下文。

详见 [references/state.md](references/state.md)。

## 私域知识与用户补充

- **私域**：LLM 可能不知道的知识，按需加载；不限于单一平台，见 `references/private_domains.md`（如办公平台 ihaier 等）。
- **用户补充假设**：用户可补充需求假设，需纳入闭环（假设→规划→追踪→校验→决策）并回环实现。
- **按需加载**：大段私域放在 `references/private_domains.md`、`references/private_knowledge.md`，在 SKILL 中仅说明「何时读」；必要时用 `scripts/load_private_knowledge.py get domains` 等。

详见 [references/private_knowledge.md](references/private_knowledge.md)。

## 多模态与视觉理解

- 当文本/代码无法拟人理解界面时，使用**多模态模型**看图决策（截图→模型→点击/键盘）。
- **自包含**：本技能内 `scripts/vision_proxy.py` 读 `vision_config.json`（或环境变量），调用 OpenAI 兼容多模态 API（如 qwen3-vl、glm-4-5v）；配置示例见 `assets/vision_config.example.json`。支持多 provider（qwen/glm 等），`vision_config.json` 中 `provider` 指定当前使用哪个。
- 与本技能内「截图 + 鼠标 + 键盘」脚本配合，实现自动化与自我验证。
- **通用智能体/驱动本技能的智能体**：**不要直接读取截图文件**（大图、二进制或无法解析）；运行环境通常不具备「看图」能力。若需理解截图内容，**必须使用本技能的 vision 脚本**：`vision_proxy.py`（通用看图）或 `vision_coords.py`（**获取点击坐标**，多轮取中位数）；或 run_plan 中的 vision 步骤（`coords: true` 时自动用 vision_coords）。失败或无法读图时，一律走 vision 多模态识别，勿反复尝试直接读图。

### 多模态能力设定（坐标稳定性）

- **vision_proxy**：通用看图问答，单次调用，输出自然语言。
- **vision_coords**：**获取点击坐标**专用，内部调用 vision_proxy 多轮（默认 3 次）、解析 (x,y) 取中位数，输出 `x y`。计划中 vision 步骤加 `"coords": true` 时，run_plan 自动用 vision_coords；非坐标类（如「输出消息内容」）用 vision_proxy。通用智能体规划时：**需要坐标返回的 vision 步骤加 `"coords": true`**。
- **校准偏移**：vision 返回的坐标常有系统性偏差，需通过 `vision_calibrate.py calibrate` 得到 offset 并写入 `state/vision_calibration.json`；run_plan / click_from_vision_or_key 会自动加上该偏移再点击。换分辨率后需重跑校准。
- **provider 选择**：可用 `vision_calibrate.py benchmark` 对比各 provider 的偏差稳定性（std 越小越稳）；benchmark 结果通常推荐 glm。

## 行为日志与溯源

- **原则**：记录所有行为，便于溯源。
- **实现**：`scripts/behavior_log.py` 写入 `logs/` 目录，每条含时间、动作类型、简要描述、关联任务/使命。
- **用途**：复盘、吃一堑长一智、审计。详见 [references/logging.md](references/logging.md)。

## 吃一堑长一智

- 从失败中抽取教训，写入 `references/failures.md` 或等价文档。
- 在「主动决策」阶段查阅失败记录，避免重复错误；在规划时考虑历史教训。

详见 [references/failures.md](references/failures.md)。

## 已有支持的场景（摘要）

以下场景已支持，**用到某场景时**再至 **references/capabilities.md** 取具体能力与命令。

| 场景类别 | 摘要（示例） |
|----------|--------------|
| 拍照/看 | 自拍、打开摄像头、截图、看图提问 |
| 打开/启动 | 打开浏览器、记事本、文件管理器、闹钟、日历、设置、任务管理器、计算器、运行(Win+R) |
| 输入/剪贴板 | 按键、组合键、键盘输入、中文输入、复制/粘贴、剪贴板读写、剪贴板图片 |
| 窗口/进程 | 窗口激活、按标题查 PID、结束窗口、进程列表与结束 |
| 系统 | 时间、主机名/用户名、防休眠、睡眠/休眠、关机/重启、音量、亮度、通知、WLAN/网络接口、注册表、文件读写/列目录 |
| 自动化 | 按计划执行（run_plan）、执行任意脚本、自主校验能力链 |
| **保底场景** | **打开浏览器 + 鼠标 + 键盘 + 截图 + 多模态** 的通用流程：先打开浏览器（或指定 URL/搜索页），再截图 → 多模态看图 → 根据画面点击/输入/按键（或 run_plan 多步）。适用于**网页操作、WebSearch、未单独列出的在线任务**等，无专门场景时即用此流程。详见下方「保底方案：Windows 界面引导」。 |

**具体命令与参数**：见 [references/capabilities.md](references/capabilities.md)。下方表格为意图→能力速查，细节仍以 capabilities.md 为准。

### 保底方案：Windows 界面引导（鼠标+键盘+截图+多模态时参考）

在 **Win 电脑**上走保底「截图 → 多模态看图 → 点击/输入」时，可让多模态模型结合以下界面常识做决策，减少漏点、误点：

| 区域 | 说明与可操作方式 |
|------|------------------|
| **任务栏** | 屏幕底部任务栏中，**正在运行的应用**在图标下方有一条**亮线/高亮**；点击该图标即可**切换并前置**对应窗口。截图后若 vision 识别到任务栏，可据此点击图标切换应用，无需仅依赖「按标题激活窗口」。 |
| **系统托盘（右下角）** | 托盘区显示时间、网络、音量等；**点击向上箭头（^）**可展开，显示**所有托盘程序**（如 ihaier、OneDrive、输入法、后台服务等）。需要打开或操作托盘程序时：先截图 → vision 识别托盘区与向上箭头 → 点击箭头展开 → 再截图 → 识别目标图标并点击。 |
| **托盘图标右键** | 托盘里的程序图标**右键点击**一般会弹出**菜单**（如「打开主界面」「退出」「设置」等）。若需对某托盘程序做操作，可：先展开托盘 → 对目标图标**右键**（`mouse_tool right_click x y`）→ 再截图 → vision 识别菜单项 → 点击对应项。 |

以上引导供规划 run_plan 或「截图→vision→点击」步骤时参考；vision 提问中可明确要求模型「若画面含任务栏/托盘，请指出可点击的图标与大致坐标」。

## 满足用户需求的优先级（通用智能体必遵）

响应用户请求时，按以下顺序选择方式：

| 优先级 | 条件 | 做法 |
|--------|------|------|
| **1** | 用户需求**匹配已有支持的场景**（见上表，含保底场景） | **优先使用该场景**对应能力；场景会记录历史操作，可查 `query_scenario_experiences.py --keyword <场景>` 参考以往成功/失败。 |
| **2** | 用户需求**不匹配**已有场景 | **走保底场景**：**打开浏览器**（如需网页/搜索则先 `do 打开浏览器 [url]`）→ **鼠标 + 键盘 + 截图 + 多模态**：截图 → 多模态看图理解 → 根据画面点击/输入/按键（或 run_plan 多步），直至完成任务。网页、WebSearch 等均可按此通用流程处理。 |
| **3** | 存在**非常明确**的单项能力支持（用户诉求直接对应某脚本/do 意图） | **直接使用该能力**，不必强行走截图+多模态。 |

简要记：**先对已支持场景（含保底） → 再对保底「开浏览器+看屏+点键」 → 有明确能力则直接用**。

## 能力与调用方式（供模型选用）

**意图识别由运行环境（Claude Code / Cursor）的模型负责。** 本技能只提供能力与调用方式，模型识别到用户意图后可直接执行对应命令。

| 用户可能表达的意图 | 可调用的能力（在技能目录下执行） |
|--------------------|----------------------------------|
| 自拍、帮我来个自拍 | `python scripts/selfie.py` 或 `python scripts/do.py 自拍` |
| 打开摄像头、看看摄像头 | `python scripts/camera_qt.py` 或 `python scripts/do.py 打开摄像头` |
| 截图、截屏 | `python scripts/screenshot_tool.py [路径]` 或 `python scripts/do.py 截图` |
| 打开浏览器、打开某网址 | `python scripts/launch_browser.py [url]` 或 `python scripts/do.py 打开浏览器 [url]` |
| 打开记事本、打开文件管理器 | `python scripts/launch_notepad.py`、`python scripts/launch_explorer.py [目录]` 或 `do.py 打开记事本/打开文件管理器` |
| 按回车、按键 | `python scripts/keyboard_tool.py key 13` 或 `do.py 按回车` |
| 点击 (x,y)、输入文字、中文输入 | `mouse_tool.py click x y`、`keyboard_tool.py type "..."`；`do.py 输入中文 内容`（剪贴板+粘贴）；`run_plan.py` |
| 看图并问问题 | `python scripts/vision_proxy.py <图片路径> "<问题>"` |
| **获取点击坐标**（多轮取中位数） | `python scripts/vision_coords.py <图片路径> "<问题>"` 或 run_plan 中 vision 加 `"coords": true` |
| 按计划执行一系列操作 | `python scripts/run_plan.py plans/xxx.json` |

更多脚本与用法见下方「脚本」节；详细需求与能力链见 [references/assumed_demands.md](references/assumed_demands.md)。

## 通用基础能力（自包含）

- **独立自闭环**：本技能不依赖其他技能。鼠标、键盘、屏幕、截图、多模态均由本技能内脚本完成。
- **脚本**：`scripts/screen_size_tool.py`（主屏宽高）、`scripts/mouse_tool.py`（click/right_click/middle_click/scroll/drag）、`scripts/keyboard_tool.py`（key/keys/type）、`scripts/screenshot_tool.py`（全屏 BMP）、`scripts/vision_proxy.py`（看图问答）、`scripts/vision_coords.py`（**获取点击坐标**，多轮取中位数）。均为 Windows 下自包含（ctypes/标准库）。

## UI：科幻主体

- **形态**：采用 **BS（浏览器端）**，理由见 [references/ui_iq.md](references/ui_iq.md)（开发与迭代成本低、易自进化）。
- **风格**：类似贾维斯/星期五的科幻主体，持续自我完善；不在 FRIDAY 后显示年龄或智商阶段（思考能力由当前 LLM 决定）。
- **实现**：见 [references/ui_iq.md](references/ui_iq.md)；前端骨架在 `assets/friday-ui.html`。

## 技能内资源索引（按需加载）

| 资源 | 何时读 |
|------|--------|
| [references/loop.md](references/loop.md) | 需要细化闭环流程、各模块输入输出时。 |
| [references/state.md](references/state.md) | 需要读写当前使命/任务、防迷失时。 |
| [references/private_knowledge.md](references/private_knowledge.md) | 需要私域知识或用户补充假设时。 |
| [references/private_domains.md](references/private_domains.md) | 需要按域加载私域（如办公平台等）时。 |
| [references/requirements.md](references/requirements.md) | 项目约束与要求，自我进化中必须遵守。 |
| [references/logging.md](references/logging.md) | 需要规范行为日志与溯源时。 |
| [references/ui_iq.md](references/ui_iq.md) | 需要 UI 设计（CS/BS、科幻主体、悬浮球）时。 |
| [references/failures.md](references/failures.md) | 决策或规划时吸取历史教训。 |
| [references/evolution_guide.md](references/evolution_guide.md) | 自我进化实施顺序、Git 与版本、多模态与私域。 |
| [references/assumed_demands.md](references/assumed_demands.md) | 假设的用户需求（打开摄像头、ihaier 发消息、访问网站等）与能力链、状态。 |
| [references/capabilities.md](references/capabilities.md) | 能力与调用方式一览，供模型在识别意图后选用（本技能不做意图识别）。 |
| [references/agent_evolution_workflow.md](references/agent_evolution_workflow.md) | **通用智能体进化环**：假设→决策→执行→校验→反思的输入/输出与执行清单，供任何智能体驱动无限进化。 |
| [references/base_capabilities_analysis.md](references/base_capabilities_analysis.md) | **底座能力盘点与缺口**：按输入/输出/看/执行/窗口/进程等维度盘点已有能力与待补齐项。 |
| [references/portable_env.md](references/portable_env.md) | **便携运行环境**：如何将 Python+依赖打入项目、复制到别机直接使用。 |
| [references/scenario_logging.md](references/scenario_logging.md) | **场景维度日志**：用户场景请求与执行结果的记录与查询，按场景积累成功/失败经验。 |

## 脚本

- `scripts/scenario_log.py` — **场景日志**：记录用户场景与执行结果。用法 `scenario_log.py "<用户输入/场景>" "<执行的命令>" success|fail [备注]`。响应用户场景请求后由通用智能体调用。
- `scripts/query_scenario_experiences.py` — 查询场景经验：`query_scenario_experiences.py [N]` 最近 N 条；`--keyword 自拍` 按关键词筛选。规划时可查阅。
- `scripts/run_with_env.py` — **统一解释器入口**：优先使用项目内 `python/python.exe`（若存在），否则当前解释器；用法 `python scripts/run_with_env.py <脚本名> [参数...]`，便于便携部署后直接使用。
- `scripts/state_tracker.py` — 读写 `state/current_mission.json`，维护「当前要干什么」。
- `scripts/loop_runner.py` — **闭环跑者**：执行一轮 assume→plan→track→verify→decide 并更新状态与日志。`python scripts/loop_runner.py` 跑一轮退出；`python scripts/loop_runner.py --daemon [--interval 300]` 每 N 秒跑一轮、持续运行（可挂后台或计划任务），这样轮次与日志会持续前进。
- `scripts/behavior_log.py` — 写行为日志到 `logs/`。
- `scripts/load_private_knowledge.py` — 按需加载私域（`get domains` / `get user_assumptions`）。
- `scripts/screen_size_tool.py`、`scripts/mouse_tool.py`（含 right_click/middle_click/drag）、`scripts/keyboard_tool.py`、`scripts/screenshot_tool.py`、`scripts/clipboard_tool.py`、`scripts/timer_tool.py`、`scripts/file_tool.py`、`scripts/time_tool.py`、`scripts/process_tool.py`（进程 list/kill）— 屏幕/鼠标/键盘/截图/剪贴板/定时/文件/时间/进程（Windows）。
- `scripts/launch_clock.py`、`scripts/launch_calendar.py`、`scripts/launch_settings.py`、`scripts/launch_taskmgr.py`、`scripts/launch_calc.py`、`scripts/env_tool.py`（含 EXPAND 路径）、`scripts/network_tool.py`（ipconfig/wlan/interfaces）— 打开闹钟、日历、设置、任务管理器、计算器；环境/网络；`do.py WLAN`、`do.py 网络接口`。
- `scripts/window_tool.py` — 窗口激活 `activate "标题"`；按标题查 PID `pid "标题"`；`do.py 窗口激活/窗口PID/结束窗口`。
- `scripts/power_tool.py` — 防止休眠/关屏（prevent_sleep [秒数]）；睡眠/休眠（sleep、hibernate）；关机/重启（shutdown [秒]、reboot [秒]）；`do.py 睡眠/休眠/关机/重启`。
- `scripts/clipboard_tool.py` — get/set 文本；image_get/image_set 剪贴板图片（BMP/CF_DIB）；`do.py 剪贴板图片保存|剪贴板图片写入 [路径]`。
- `scripts/reg_tool.py` — 注册表 get/set（HKCU/HKLM 等，sz/dword）；`do.py run reg_tool get HKCU "..."`。
- `scripts/volume_tool.py` — 主音量 get/set 0–100（winmm）；`do.py 音量值`、`do.py 设置音量 50`。
- `scripts/brightness_tool.py` — 屏幕亮度 get/set 0–100（伽马）；`do.py 亮度`、`do.py 设置亮度 80`。
- `scripts/notification_tool.py` — Toast 通知 show（Win10+）；`do.py 通知 内容`。
- `scripts/vision_proxy.py` — 自包含多模态看图问答（单次），配置见 `vision_config.json`。
- `scripts/vision_coords.py` — **获取点击坐标**：对同一图多轮调用 vision_proxy、解析 (x,y) 取中位数，输出 `x y`；run_plan 中 `coords: true` 时自动使用。
- `scripts/serve.py` — 本地 HTTP 服务（默认 8765）；启动后约 1.5s 自动打开置顶悬浮窗。使用本技能前需先运行此服务。
- `scripts/friday_floating_main.py` — 悬浮窗统一入口：优先启动 Qt 版，无 PyQt5 时回退 WebView 版。
- `scripts/friday_floating_qt.py` — 悬浮窗**原生 GUI 版**（需 `pip install PyQt5`）：圆形、透明、托盘图标右键退出、网格球+环+光球。
- `scripts/friday_floating.py` — 悬浮窗 **WebView 版**（需 `pip install pywebview`）：内嵌 Friday UI；无 PyQt5 时由 main 自动选用。
- `scripts/launch_friday_floating.py` — 无 CMD 窗口启动悬浮窗；**默认启动 Qt 版**（friday_floating_qt.py），无 PyQt5 时再回退 WebView。
- `scripts/run_plan.py` — 执行自动化计划（screenshot/vision/click/right_click/middle_click/drag/type/key/paste/scroll/wait/run）；步骤 `paste` 为 Ctrl+V 粘贴（可配合剪贴板输入中文）；计划见 `plans/*.json`。
- `scripts/camera_qt.py` — 用 PyQt5 直接打开摄像头窗口；配合截图+vision 可「看到了什么」。
- `scripts/launch_browser.py` — 用默认浏览器打开 URL；配合截图+vision+run_plan 可访问网站并操作。
- `scripts/launch_notepad.py`、`scripts/launch_explorer.py` — 打开记事本、文件管理器（可带路径）。
- `scripts/selfie.py` — 自拍：直接启动 camera_qt → 等约 4s 画面就绪 → 截屏保存 screenshots/selfie_*.bmp。用 `run_with_env` 或系统 `python` 执行时，camera_qt 会使用调用者 Python（避免便携环境检测不到摄像头）。
- `scripts/parse_vision_steps.py` — 从 vision 自然语言输出解析 click/type/key 步骤，输出 JSON。
- `scripts/do.py` — 便捷入口：自拍/截图/剪贴板/输入中文/窗口激活/窗口PID/结束窗口/睡眠/休眠/关机/重启/音量值/设置音量/亮度/设置亮度/通知/WLAN/网络接口等；意图由模型识别后选用。

## 资源与配置

- **多模态**：复制 `assets/vision_config.example.json` 为 `scripts/vision_config.json` 或项目根下 `vision_config.json`，填写 api_key、base_url、model_name。
- **UI**：`assets/friday-ui.html` 为 BS 科幻主题骨架，由 `serve.py` 提供。悬浮窗优先用 PyQt5 原生绘制（见上方「依赖与安装」）；回退 WebView 时内嵌该页面。

## 设计参考

- 整体思路与架构参考 **skill-creator**：SKILL.md 精简、引用 references、脚本可独立运行、渐进式披露。
- 本技能**独立自闭环**，不依赖其他技能；长期任务中可继续抽象通用能力并沉淀在本技能内。
