---
name: friday-self-evolution
description: |
  依托用户电脑的自我进化技能，形成「主动假设→主动规划→任务追踪→完成校验→主动决策」闭环，满足用户所有需求。始终知道当前要干什么，不迷失。
  触发：星期五、贾维斯、自我进化、主动假设、任务追踪、闭环生态、技能进化、当前在干什么、私域知识、行为日志溯源、智商阶段。
---

# 星期五 · 自我进化技能

**核心信条：始终知道我们当前要干什么。** 在多轮循环中不迷失。

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

## 通用基础能力（自包含）

- **独立自闭环**：本技能不依赖其他技能。鼠标、键盘、屏幕、截图、多模态均由本技能内脚本完成。
- **脚本**：`scripts/screen_size_tool.py`（主屏宽高）、`scripts/mouse_tool.py`（click/scroll）、`scripts/keyboard_tool.py`（key/keys/type）、`scripts/screenshot_tool.py`（全屏 BMP）、`scripts/vision_proxy.py`（看图问答）。均为 Windows 下自包含（ctypes/标准库）。

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

## 脚本

- `scripts/state_tracker.py` — 读写 `state/current_mission.json`，维护「当前要干什么」。
- `scripts/behavior_log.py` — 写行为日志到 `logs/`。
- `scripts/load_private_knowledge.py` — 按需加载私域（`get domains` / `get user_assumptions`）。
- `scripts/screen_size_tool.py`、`scripts/mouse_tool.py`、`scripts/keyboard_tool.py`、`scripts/screenshot_tool.py` — 自包含的屏幕/鼠标/键盘/截图（Windows）。
- `scripts/vision_proxy.py` — 自包含多模态看图问答，配置见 `vision_config.json`。

## 资源与配置

- **多模态**：复制 `assets/vision_config.example.json` 为 `scripts/vision_config.json` 或项目根下 `vision_config.json`，填写 api_key、base_url、model_name。
- **UI**：`assets/friday-ui.html` 为 BS 科幻主题骨架，展示当前使命、阶段与智商等级；本地用浏览器打开即可，状态来自 `state/current_mission.json`。

## 设计参考

- 整体思路与架构参考 **skill-creator**：SKILL.md 精简、引用 references、脚本可独立运行、渐进式披露。
- 本技能**独立自闭环**，不依赖其他技能；长期任务中可继续抽象通用能力并沉淀在本技能内。
