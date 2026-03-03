---
name: friday-self-evolution
description: |
  依托用户电脑的自我进化技能，形成「主动假设→主动规划→任务追踪→完成校验→主动决策」闭环，满足用户所有需求；未满足不反馈、一直自进化。始终知道当前要干什么，不迷失。宗旨与约束见 SKILL 内「本技能宗旨与约束」。
  触发：星期五、贾维斯、自我进化、主动假设、任务追踪、闭环生态、技能进化、当前在干什么、私域知识、行为日志溯源、智商阶段。
---

# 星期五 · 自我进化技能

**核心信条：始终知道我们当前要干什么。** 在多轮循环中不迷失。

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
| **UI** | 类似贾维斯/星期五的**科幻主体**，不断自我完善；可体现当前**智商/阶段**（不同阶段年龄对应不同难度，见 `references/ui_iq.md`）。 |
| **防迷失** | **始终知道我们当前要干什么**；状态见 `state/current_mission.json`，每次行动前后读写，避免多轮循环中迷失。 |

上述宗旨与 `references/requirements.md` 中的项目约束一并适用；闭环执行细节见 `references/agent_evolution_workflow.md`。

---

## 通用智能体：驱动本技能请先读此文档

若你作为**通用智能体**驱动本技能的自进化闭环，请**优先阅读**：

**`references/agent_evolution_workflow.md`**

该文档说明进化环（假设 → 自主决策 → 自主执行 → 自主校验审核 → 自主优化反思 → 回到假设）及每一阶段的输入、输出与执行清单。按其中步骤执行即可形成无限进化循环。读完该文档后再按需查阅本 SKILL 其余能力与脚本说明。

---

**使用本技能前需先启动服务**：在技能目录下执行 `python scripts/serve.py`。服务启动后会自动打开**圆形置顶悬浮窗**（无 CMD 窗口）：无标题栏、无图标与最小化/最大化/关闭按钮，圆形窗口。**推荐安装 PyQt5**（`pip install PyQt5`）以使用**原生 GUI 版**悬浮窗（无 WebView、真透明/深色底、网格球+环+光球动画，状态从 `state/current_mission.json` 读取）；未装 PyQt5 时自动回退到 WebView 版（需 `pywebview`）。

**使用本技能时**：自闭环需**多轮持续**，不得在一轮结束后向用户「总结并结束」。每轮 decide 后更新 state、写入日志，并立即进入下一轮假设/规划。

**通用智能体驱动闭环**：按上文「通用智能体：驱动本技能请先读此文档」指向的 **references/agent_evolution_workflow.md** 执行进化环即可。

## 依赖与安装

以下为需要**额外安装**的依赖（`pip install`），与对应能力。技能目录下提供 `requirements.txt`，可 `pip install -r requirements.txt` 安装推荐依赖。

| 依赖 | 用途 | 是否必须 |
|------|------|----------|
| **PyQt5** | 悬浮窗**原生 GUI 版**：圆形、透明、托盘右键退出、网格球动画；不依赖 WebView | **推荐**（不装则用下一条） |
| **pywebview** | 悬浮窗**回退版**：无 PyQt5 时用浏览器内核内嵌 Friday UI；Windows 下透明可能不生效 | 可选（仅当未装 PyQt5 且需悬浮窗时） |
| 多模态 API | `vision_proxy.py` 看图问答：需在 `scripts/vision_config.json` 或环境变量中配置 API（见 `assets/vision_config.example.json`），无额外 pip 包要求 | 按需配置 |

- **悬浮窗**：优先使用 PyQt5 版（`scripts/friday_floating_qt.py`），无 PyQt5 时自动回退到 pywebview 版（`scripts/friday_floating.py`）。入口统一为 `scripts/launch_friday_floating.py` 或由 `serve.py` 自动拉起。
- **一键安装推荐**：`pip install -r requirements.txt`（当前主要为 PyQt5）。

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
- **自包含**：本技能内 `scripts/vision_proxy.py` 读 `vision_config.json`（或环境变量），调用 OpenAI 兼容多模态 API（如 qwen3-vl）；配置示例见 `assets/vision_config.example.json`。
- 与本技能内「截图 + 鼠标 + 键盘」脚本配合，实现自动化与自我验证。

## 行为日志与溯源

- **原则**：记录所有行为，便于溯源。
- **实现**：`scripts/behavior_log.py` 写入 `logs/` 目录，每条含时间、动作类型、简要描述、关联任务/使命。
- **用途**：复盘、吃一堑长一智、审计。详见 [references/logging.md](references/logging.md)。

## 吃一堑长一智

- 从失败中抽取教训，写入 `references/failures.md` 或等价文档。
- 在「主动决策」阶段查阅失败记录，避免重复错误；在规划时考虑历史教训。

详见 [references/failures.md](references/failures.md)。

## 能力与调用方式（供模型选用）

**意图识别由运行环境（Claude Code / Cursor）的模型负责。** 本技能只提供能力与调用方式，模型识别到用户意图后可直接执行对应命令。

| 用户可能表达的意图 | 可调用的能力（在技能目录下执行） |
|--------------------|----------------------------------|
| 自拍、帮我来个自拍 | `python scripts/selfie.py` 或 `python scripts/do.py 自拍` |
| 打开摄像头、看看摄像头 | `python scripts/launch_camera.py` 或 `python scripts/do.py 打开摄像头` |
| 截图、截屏 | `python scripts/screenshot_tool.py [路径]` 或 `python scripts/do.py 截图` |
| 打开浏览器、打开某网址 | `python scripts/launch_browser.py [url]` 或 `python scripts/do.py 打开浏览器 [url]` |
| 打开记事本、打开文件管理器 | `python scripts/launch_notepad.py`、`python scripts/launch_explorer.py [目录]` 或 `do.py 打开记事本/打开文件管理器` |
| 按回车、按键 | `python scripts/keyboard_tool.py key 13` 或 `do.py 按回车` |
| 点击 (x,y)、输入文字 | `scripts/mouse_tool.py click x y`、`scripts/keyboard_tool.py type "..."`、`scripts/run_plan.py plans/xxx.json` |
| 看图并问问题 | `python scripts/vision_proxy.py <图片路径> "<问题>"` |
| 按计划执行一系列操作 | `python scripts/run_plan.py plans/xxx.json` |

更多脚本与用法见下方「脚本」节；详细需求与能力链见 [references/assumed_demands.md](references/assumed_demands.md)。

## 通用基础能力（自包含）

- **独立自闭环**：本技能不依赖其他技能。鼠标、键盘、屏幕、截图、多模态均由本技能内脚本完成。
- **脚本**：`scripts/screen_size_tool.py`（主屏宽高）、`scripts/mouse_tool.py`（click/right_click/middle_click/scroll/drag）、`scripts/keyboard_tool.py`（key/keys/type）、`scripts/screenshot_tool.py`（全屏 BMP）、`scripts/vision_proxy.py`（看图问答）。均为 Windows 下自包含（ctypes/标准库）。

## UI：科幻主体与智商阶段

- **形态**：采用 **BS（浏览器端）**，理由见 [references/ui_iq.md](references/ui_iq.md)（开发与迭代成本低、易自进化）。
- **风格**：类似贾维斯/星期五的科幻主体，持续自我完善；智商阶段对应不同操作难度。
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
| [references/ui_iq.md](references/ui_iq.md) | 需要 UI 或智商阶段设计时。 |
| [references/failures.md](references/failures.md) | 决策或规划时吸取历史教训。 |
| [references/evolution_guide.md](references/evolution_guide.md) | 自我进化实施顺序、Git 与版本、多模态与私域。 |
| [references/assumed_demands.md](references/assumed_demands.md) | 假设的用户需求（打开摄像头、ihaier 发消息、访问网站等）与能力链、状态。 |
| [references/capabilities.md](references/capabilities.md) | 能力与调用方式一览，供模型在识别意图后选用（本技能不做意图识别）。 |
| [references/agent_evolution_workflow.md](references/agent_evolution_workflow.md) | **通用智能体进化环**：假设→决策→执行→校验→反思的输入/输出与执行清单，供任何智能体驱动无限进化。 |
| [references/base_capabilities_analysis.md](references/base_capabilities_analysis.md) | **底座能力盘点与缺口**：按输入/输出/看/执行/窗口/进程等维度盘点已有能力与待补齐项。 |

## 脚本

- `scripts/state_tracker.py` — 读写 `state/current_mission.json`，维护「当前要干什么」。
- `scripts/loop_runner.py` — **闭环跑者**：执行一轮 assume→plan→track→verify→decide 并更新状态与日志。`python scripts/loop_runner.py` 跑一轮退出；`python scripts/loop_runner.py --daemon [--interval 300]` 每 N 秒跑一轮、持续运行（可挂后台或计划任务），这样轮次与日志会持续前进。
- `scripts/behavior_log.py` — 写行为日志到 `logs/`。
- `scripts/load_private_knowledge.py` — 按需加载私域（`get domains` / `get user_assumptions`）。
- `scripts/screen_size_tool.py`、`scripts/mouse_tool.py`（含 right_click/middle_click/drag）、`scripts/keyboard_tool.py`、`scripts/screenshot_tool.py`、`scripts/clipboard_tool.py`、`scripts/timer_tool.py`、`scripts/file_tool.py`、`scripts/time_tool.py`、`scripts/process_tool.py`（进程 list/kill）— 屏幕/鼠标/键盘/截图/剪贴板/定时/文件/时间/进程（Windows）。
- `scripts/launch_clock.py`、`scripts/launch_calendar.py`、`scripts/launch_settings.py`、`scripts/launch_taskmgr.py`、`scripts/launch_calc.py`、`scripts/env_tool.py`（含 EXPAND 路径）、`scripts/network_tool.py` — 打开闹钟、日历、设置、任务管理器、计算器；环境/网络只读。
- `scripts/window_tool.py` — 窗口激活：`activate "标题或部分标题"`（EnumWindows+SetForegroundWindow）；`do.py 窗口激活 记事本`。
- `scripts/power_tool.py` — 防止休眠/关屏（prevent_sleep [秒数]）；睡眠/休眠（sleep、hibernate）；Windows ctypes。
- `scripts/clipboard_tool.py` — get/set 文本；image_get/image_set 剪贴板图片（BMP/CF_DIB）；`do.py 剪贴板图片保存|剪贴板图片写入 [路径]`。
- `scripts/vision_proxy.py` — 自包含多模态看图问答，配置见 `vision_config.json`。
- `scripts/serve.py` — 本地 HTTP 服务（默认 8765）；启动后约 1.5s 自动打开置顶悬浮窗。使用本技能前需先运行此服务。
- `scripts/friday_floating_main.py` — 悬浮窗统一入口：优先启动 Qt 版，无 PyQt5 时回退 WebView 版。
- `scripts/friday_floating_qt.py` — 悬浮窗**原生 GUI 版**（需 `pip install PyQt5`）：圆形、透明、托盘图标右键退出、网格球+环+光球。
- `scripts/friday_floating.py` — 悬浮窗 **WebView 版**（需 `pip install pywebview`）：内嵌 Friday UI；无 PyQt5 时由 main 自动选用。
- `scripts/launch_friday_floating.py` — 无 CMD 窗口启动悬浮窗（CREATE_NO_WINDOW）。
- `scripts/run_plan.py` — 执行自动化计划（screenshot/vision/click/right_click/middle_click/drag/type/key/scroll/wait/run），实现点点点与多模态决策；计划见 `plans/*.json`。步骤 `run`：`{"do":"run","script":"launch_camera"}` 执行 scripts/ 下对应 .py；`drag` 需 `x1,y1,x2,y2`。
- `scripts/launch_camera.py` — 打开系统摄像头应用；配合截图+vision 可「看到了什么」。
- `scripts/launch_browser.py` — 用默认浏览器打开 URL；配合截图+vision+run_plan 可访问网站并操作。
- `scripts/launch_notepad.py`、`scripts/launch_explorer.py` — 打开记事本、文件管理器（可带路径）。
- `scripts/selfie.py` — 自拍：打开摄像头 → 等 3s → 截屏保存 screenshots/selfie_*.bmp。
- `scripts/parse_vision_steps.py` — 从 vision 自然语言输出解析 click/type/key 步骤，输出 JSON。
- `scripts/do.py` — 便捷入口：自拍/摄像头/截图/浏览器/剪贴板读写/剪贴板图片保存写入/窗口激活/睡眠/休眠/防休眠/进程/复制粘贴等；意图由模型识别后选用。

## 资源与配置

- **多模态**：复制 `assets/vision_config.example.json` 为 `scripts/vision_config.json` 或项目根下 `vision_config.json`，填写 api_key、base_url、model_name。
- **UI**：`assets/friday-ui.html` 为 BS 科幻主题骨架，由 `serve.py` 提供。悬浮窗优先用 PyQt5 原生绘制（见上方「依赖与安装」）；回退 WebView 时内嵌该页面。

## 设计参考

- 整体思路与架构参考 **skill-creator**：SKILL.md 精简、引用 references、脚本可独立运行、渐进式披露。
- 本技能**独立自闭环**，不依赖其他技能；长期任务中可继续抽象通用能力并沉淀在本技能内。
