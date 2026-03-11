# 假设的用户需求（自主假设、待实现/进行中）

以下为主动假设的用户需求，自闭环中逐项实现或迭代，未满足不向用户汇报、持续进化直到满足。

| 需求简述 | 能力链 | 状态 |
|----------|--------|------|
| 帮我打开摄像头，看到了什么 | camera_qt → 截图 → vision 描述 | 已具备脚本；需联调 |
| 帮我来个自拍 | do.py 自拍 → selfie.py（打开摄像头→等3s→截屏） | 已实现；对话中说自拍即执行 do.py 自拍 |
| 用 ihaier 给周小帅发个消息 | 打开/聚焦 ihaier → 截图 → vision 找联系人与输入框 → click + type | 待规划计划 |
| 绩效达成申报 | 搜索绩效管理 → 进入应用 → 目标签订/实际申报 → 选周期 → 达成申报 → 填写表单 → 保存草稿 | 已实现 plan `ihaier_performance_declaration.json`；`--period 月度|季度|年度` |
| 帮我访问某网站完成某操作 | launch_browser → **激活并最大化浏览器窗口** → 截图 → vision 决策 → click/type（见 assets/plans/example_visit_website.json） | 计划模板已有；打开后须先 maximize 再做截图/vision |
| 点点点（基础点击、输入） | run_plan：screenshot / vision / click / type / key | 已实现 run_plan |

能力基础：多模态(vision_proxy) + 鼠标(mouse_tool) + 键盘(keyboard_tool) + 屏幕(screenshot_tool) + 计划执行(run_plan)。

**待探索**：vision 输出自然语言 → 解析为「click x y」「type "..."」等步骤并追加到 plan 或执行（可 LLM 解析或规则）。

**主动提出需求（第12轮）**：① vision 回复中若含坐标或「点击 (x,y)」「输入 某某」，用约定格式或脚本解析后追加 run_plan 步骤并执行；② serve 启动时自动执行一次 export_recent_logs，使 UI 打开即见最新日志。

**已扩展能力**：自拍流程中自动按回车消弹窗；打开记事本、打开文件管理器、按回车；run_plan 支持 `run` 步骤执行 scripts 下脚本。

**自主扩展（能力补齐）**：已补齐声音、剪贴板、定时、闹钟、日历、防休眠、设置、运行、任务管理器、计算器、文件/目录、时间、主机名、网络等；run_plan 支持 screenshot/vision/click/type/key/scroll/wait/run。详见 references/capabilities.md。

**目标「你即我的电脑」**：用户说干啥就用电脑干。当前能力已覆盖：输入（键盘/剪贴板）、输出（截图/文件/屏幕）、看（vision）、点（鼠标）、打开任意应用（run/launch/do）、执行计划（run_plan）。缺口主要在：大模型把自然语言映射到能力链的准确性、vision+点击在任意界面上的鲁棒性、以及具体场景（某网站/某软件）的 plan 与调参。无固定「还需几轮」，可继续多轮打磨文档与示例。
