# 底座能力盘点与缺口分析

本文档对「电脑 + LLM 拟人化」底座做结构化盘点，便于后续补齐。

---

## 一、已有底座（按类别）

| 类别 | 能力 | 脚本/入口 |
|------|------|-----------|
| **输入·键盘** | 单键、组合键、输入字符串(ASCII) | keyboard_tool key/keys/type；do 按回车、音量静音/减/增 |
| **输入·鼠标** | 左键点击、滚轮、当前坐标 | mouse_tool click/scroll/pos |
| **输入·剪贴板** | 文本读/写；图片(BMP)读/写 | clipboard_tool get/set/image_get/image_set；do 剪贴板读/写/剪贴板图片保存/写入 |
| **输出·屏幕** | 全屏截图(BMP)、屏幕宽高 | screenshot_tool、screen_size_tool |
| **输出·文件** | 文本读/写、列目录 | file_tool read/write/list；do 读文件/写文件/列目录 |
| **看** | 看图问答(多模态) | vision_proxy；run_plan 中 vision 步骤 |
| **执行·计划** | 截图→vision→点击→输入→按键→等待→运行脚本 | run_plan + plans/*.json |
| **执行·统一入口** | 自拍/摄像头/截图/浏览器/记事本/资源管理器/闹钟/日历/设置/任务管理器/计算器/运行/网络/时间/主机名/剪贴板/防休眠/音量/run 脚本等 | do.py |
| **系统·时间** | 当前时间(UTC/本地) | time_tool；do 当前时间 |
| **系统·环境** | 主机名、用户名 | env_tool；do 主机名/用户名 |
| **系统·网络** | ipconfig 信息 | network_tool；do 网络信息 |
| **系统·电源** | 防休眠/关屏 N 秒；睡眠/休眠 | power_tool prevent_sleep、sleep、hibernate；do 防休眠/睡眠/休眠 |
| **系统·音量** | 静音/减/增(模拟键) | keyboard_tool key 173/174/175 |
| **启动·应用** | 记事本、浏览器、摄像头、资源管理器、闹钟、日历、设置、任务管理器、计算器、运行(Win+R) | 各 launch_*.py 与 do |
| **窗口·激活** | 按标题（部分匹配）提到前台 | window_tool activate；do 窗口激活 |
| **闭环·状态** | 当前使命/阶段/轮次 | state_tracker、current_mission.json |
| **闭环·日志** | 行为记录、近期导出 | behavior_log、export_recent_logs |
| **闭环·校验** | 能力链自检 | self_verify_capabilities |
| **私域** | 按需加载(如 ihaier) | load_private_knowledge、private_domains.md |

---

## 二、底座缺口（建议补齐顺序）

| 缺口 | 说明 | 可行实现 |
|------|------|----------|
| **鼠标·右键/中键** | 已覆盖：mouse_tool right_click、middle_click | — |
| **鼠标·拖拽** | 已覆盖：mouse_tool drag x1 y1 x2 y2 | — |
| **键盘·中文/Unicode** | type 主要 ASCII，中文会变成空格 | SendInput Unicode 或 IME 模拟；或依赖剪贴板粘贴中文 |
| **窗口·前后台** | 已覆盖：window_tool activate "部分标题"；do 窗口激活 | — |
| **进程·列表/结束** | 已覆盖：process_tool list / kill（tasklist/taskkill） | 按窗口标题查 PID 可扩展 |
| **剪贴板·图片** | 已覆盖：clipboard_tool image_get/image_set（BMP/CF_DIB） | — |
| **电源·睡眠/休眠** | 已覆盖：power_tool sleep、hibernate；do 睡眠、休眠 | 关机/重启可按需扩展 |
| **组合键·常用** | Win+E、Ctrl+C/V、Alt+F4 等未在 do/capabilities 显式列出 | capabilities 补充「组合键用 keyboard_tool keys」；do 可加 do 复制/粘贴 等 |
| **路径·解析** | 无 %USERPROFILE%、%TEMP% 等展开 | env_tool 或 file_tool 支持 expand 路径 |

---

## 三、优先级建议

- **高**（拟人操作常用）：**鼠标右键**、**常用组合键文档化或 do 化**、**窗口激活(可选)**。
- **中**：鼠标拖拽、进程 taskkill、剪贴板图片。
- **低**：精确亮度、Toast 推送、关机/休眠 API、Unicode 输入（可先用剪贴板粘贴中文）。

---

## 四、与 capability_gaps 的关系

- `references/capability_gaps.md` 按「设备/功能」维度（声音、显示、文件等）记录现状与可行方向。
- 本文档按「底座能力」维度（输入/输出/看/执行/窗口/进程等）做缺口分析，两者互补；新增能力后同步更新 capability_gaps 与 capabilities.md。
