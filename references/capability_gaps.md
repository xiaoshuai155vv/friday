# 能力缺口（待扩展）

闭环自主扩展时参考：当前技能尚未覆盖或仅部分覆盖的电脑能力，可在后续轮次中补齐。

| 类别 | 现状 | 可行方向 |
|------|------|----------|
| 声音 | 已覆盖：键盘静音/减/增；volume_tool get/set；do 音量值/设置音量 | — |
| 显示 | 已覆盖：launch_settings+vision；brightness_tool get/set；do 亮度/设置亮度 | — |
| 闹钟/定时 | 已覆盖：launch_clock、timer_tool | 复杂定时任务可用 schtasks |
| 日历 | 已覆盖：launch_calendar | 读写日程需 Outlook/Calendar API 或 UWP |
| 剪贴板 | 已覆盖：clipboard_tool get/set 文本；image_get/image_set BMP 图片 | — |
| 电源/睡眠 | 已覆盖：power_tool prevent_sleep、sleep、hibernate、shutdown、reboot；do 睡眠/休眠/关机/重启 | — |
| 通知 | 已覆盖：notification_tool show；do 通知（Win10+ Toast） | — |
| 文件/注册表 | 已覆盖：file_tool read/write/list；reg_tool get/set（HKCU/HKLM，sz/dword） | 二进制可扩展 |
| 计算器/小工具 | 已覆盖：launch_calc.py、do.py 计算器 | 复杂计算可 vision+点击 |
| 网络/网卡 | 已覆盖：network_tool ipconfig、wlan、interfaces；do 网络信息/WLAN/网络接口 | — |
| 鼠标右键/中键/拖拽 | 已覆盖：mouse_tool right_click、middle_click、drag x1 y1 x2 y2 | — |
| 窗口激活/前后台 | 已覆盖：window_tool activate、pid；do 窗口激活/窗口PID/结束窗口 | — |
| 进程列表/结束 | 已覆盖：process_tool list/kill；window_tool pid 按标题查 PID | — |
| 已安装应用列表 | 已覆盖：installed_apps_tool.py；do 已安装应用；从注册表 Uninstall 读取 | — |
| 睡眠/休眠/关机/重启 | 已覆盖：power_tool sleep/hibernate/shutdown/reboot；do 睡眠/休眠/关机/重启 | — |
| 中文/Unicode 输入 | 已覆盖：`do.py 输入中文 内容`（剪贴板+粘贴）；run_plan 步骤 `paste` | — |

说明：自闭环中优先用现有能力（截图+vision+点击+键盘+run_plan）模拟或间接实现；确需新能力时再增加自包含脚本并纳入 capabilities.md 与自校验。**底座能力盘点与缺口优先级**见 [references/base_capabilities_analysis.md](base_capabilities_analysis.md)。
