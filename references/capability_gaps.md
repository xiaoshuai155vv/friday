# 能力缺口（待扩展）

闭环自主扩展时参考：当前技能尚未覆盖或仅部分覆盖的电脑能力，可在后续轮次中补齐。

| 类别 | 现状 | 可行方向 |
|------|------|----------|
| 声音 | 已覆盖：键盘 VK 173/174/175 静音/减/增 | 如需精确音量值可 ctypes 或 WMI |
| 显示 | 间接覆盖：run_plan 打开 ms-settings:display 后 vision+点击 | 精确亮度可 WMI/SetDeviceGammaRamp |
| 闹钟/定时 | 已覆盖：launch_clock、timer_tool | 复杂定时任务可用 schtasks |
| 日历 | 已覆盖：launch_calendar | 读写日程需 Outlook/Calendar API 或 UWP |
| 剪贴板 | 已覆盖：clipboard_tool get/set 文本；image_get/image_set BMP 图片 | — |
| 电源/睡眠 | 已覆盖：power_tool prevent_sleep、sleep、hibernate | 关机/重启可按需扩展 |
| 通知 | 间接覆盖：launch_settings notifications 打开通知设置；Toast 推送需 UWP/pywin32 |
| 文件/注册表 | 已覆盖：file_tool read/write/list；run_plan 可执行脚本 | 二进制/注册表可扩展 |
| 计算器/小工具 | 已覆盖：launch_calc.py、do.py 计算器 | 复杂计算可 vision+点击 |
| 网络/网卡 | 已覆盖：network_tool.py 调用 ipconfig；do.py 网络信息 | netsh 等可扩展 |
| 鼠标右键/中键/拖拽 | 已覆盖：mouse_tool right_click、middle_click、drag x1 y1 x2 y2 | — |
| 窗口激活/前后台 | 已覆盖：window_tool.py activate "部分标题"；do.py 窗口激活 | — |
| 进程列表/结束 | 已覆盖：process_tool.py list / kill；tasklist / taskkill | 按窗口标题查 PID 可扩展 |
| 睡眠/休眠 | 已覆盖：power_tool.py sleep / hibernate；do.py 睡眠、休眠 | 关机/重启可按需扩展 |
| 中文/Unicode 输入 | 未覆盖，type 仅 ASCII | 剪贴板粘贴中文 或 SendInput Unicode |

说明：自闭环中优先用现有能力（截图+vision+点击+键盘+run_plan）模拟或间接实现；确需新能力时再增加自包含脚本并纳入 capabilities.md 与自校验。**底座能力盘点与缺口优先级**见 [references/base_capabilities_analysis.md](base_capabilities_analysis.md)。
