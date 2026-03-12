# Friday · 通用智能体外层环

**让你的 Claude Code 不停歇，自进化。**

依托用户电脑的自我进化技能，形成「主动假设 → 主动规划 → 任务追踪 → 完成校验 → 主动决策」闭环，满足用户所有需求；未满足不反馈、一直自进化。**始终知道我们当前要干什么。** 在多轮循环中不迷失。

---

## 项目简介

Friday 是一个**自进化技能**，运行在通用智能体（如 Claude Code、CCR）之下，具备：

| 维度 | 能力 |
|------|------|
| **电脑操作** | 鼠标、键盘、截图、多模态看图、剪贴板、窗口/进程、电源、音量/亮度、通知、网络、文件等 |
| **自主决策** | 按进化环（假设 → 规划 → 执行 → 校验 → 反思 → 决策）自主推进，不依赖逐步指令 |
| **进化** | 在闭环中扩展能力，按场景积累经验，从失败中写教训，支持便携环境与跨机复制 |
| **进化环定时触发** | 悬浮球或独立守护进程，定时向 CCR 提交进化任务，让 Claude Code 不停歇 |

---

## 目录结构

```
friday/
├── README.md           # 本文件
├── SKILL.md            # 技能说明（通用智能体必读）
├── VERSION
├── scripts/            # 可执行脚本
│   ├── do.py           # 意图分发入口
│   ├── run_with_env.py # 统一入口（自动选便携/系统 Python）
│   ├── launch_friday_floating.py  # 悬浮球
│   ├── evolution_loop_client.py   # 进化环客户端（提交到 CCR）
│   ├── evolution_loop_daemon.py   # 进化环定时守护（无 GUI）
│   ├── vision_proxy.py # 看图理解
│   ├── vision_coords.py# 获取点击坐标
│   └── ...
├── references/         # 文档
│   ├── agent_evolution_workflow.md  # 进化环工作流（基线）
│   ├── capabilities.md
│   └── ...
├── assets/
│   ├── plans/          # 场景 JSON（run_plan）
│   └── vision_config.example.json  # 多模态配置模板
└── runtime/            # 运行时生成（.gitignore，不提交）
    ├── config/         # evolution_loop.json 等
    ├── logs/
    └── state/
```

---

## 快速开始

### 1. 克隆与依赖

```bash
git clone https://github.com/xiaoshuai155vv/friday.git
cd friday
pip install -r requirements.txt   # 主要需 PyQt5
```

### 2. 配置（按需）

- **多模态看图**：复制 `assets/vision_config.example.json` 为 `scripts/vision_config.json`，填入 API key（**勿提交 vision_config.json**）
- **进化环**：首次运行会在 `runtime/config/evolution_loop.json` 生成配置，填入 `ccr_base_url`、`ccr_api_key`、`friday_project_path`

### 3. 启动悬浮球

```bash
python scripts/launch_friday_floating.py
```

出现圆形置顶悬浮窗，实时显示当前阶段、使命、轮次；双击可查看过程/日志；右键可「提交一轮进化环」「开启自动进化环」等。

### 4. 意图执行

```bash
python scripts/do.py 截图
python scripts/do.py 提交进化环
python scripts/do.py 进化环守护    # 后台定时触发
```

---

## 进化环使用

### 通用智能体驱动

若你作为**通用智能体**驱动本技能，请**优先阅读**：

**`references/agent_evolution_workflow.md`**

按其中「通用智能体执行清单」执行进化环即可形成无限进化循环。

### 定时触发（无 GUI）

| 命令 | 说明 |
|------|------|
| `python scripts/evolution_loop_client.py --once --auto-evolution` | 提交一轮，阻塞至完成 |
| `python scripts/evolution_loop_daemon.py` | 按配置间隔循环触发 |
| `python scripts/evolution_loop_daemon.py --once` | 单次提交后退出（适合 cron） |

配置：`runtime/config/evolution_loop.json`（`ccr_base_url`、`ccr_api_key`、`auto_interval_seconds`）

---

## 环境要求

- **Windows**（当前主要支持）
- **Python 3.8+**
- **PyQt5**（悬浮球）
- 多模态 API（vision 按需配置）

---

## 注意事项

- **vision_config.json** 含 API 密钥，已加入 `.gitignore`，请勿提交
- **runtime/** 为运行时目录，不纳入版本库
- 命令行中文乱码时，可设置 `PYTHONIOENCODING=utf-8` 或使用 `python scripts/run_with_env.py <脚本> [参数]`

---

## 许可证

Apache-2.0
