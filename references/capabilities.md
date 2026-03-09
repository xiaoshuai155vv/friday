# 能力清单（供运行环境模型选用）

本技能**不做意图识别**。意图由 Claude Code / Cursor 等运行环境中的模型识别；识别后可从下表选用对应能力并执行。

**do.py 不支持时**：当 `do.py <意图>` 返回「未知意图」，**不要放弃**。使用保底能力完成：① 鼠标（mouse_tool click）、键盘（keyboard_tool、Win+R+type+Enter）；② 多模态：截图 → vision_proxy/vision_coords 定位 → click。若成功，将最短路径固化为 `plans/<场景>.json`，下次直接 `run_plan`。**打开应用**：Windows 上所有应用可从开始菜单/任务栏搜到，用 Win 键、Win+R 或 `do 打开应用 <名>` 即可；**不要**去文件系统搜 exe 路径。

## 能力与调用

| 意图/场景 | 命令（在技能项目根或 scripts 所在目录执行） |
|-----------|---------------------------------------------|
| 自拍 | `python scripts/selfie.py` |
| 打开摄像头 | `python scripts/camera_qt.py` 或 `do.py 打开摄像头` |
| 截图 | `python scripts/screenshot_tool.py` 或带路径 |
| 屏幕尺寸 | `python scripts/screen_size.py` 输出主屏逻辑宽高 W H（与截图/鼠标坐标一致） |
| 验证点击坐标 | `python scripts/click_verify.py <x> <y> [秒数] [--screenshot path]` 移动鼠标到 (x,y) 并等待，用于核对多模态返回的坐标是否正确 |
| 打开浏览器/某 URL | `python scripts/launch_browser.py [url]` |
| 屏幕宽高 | `python scripts/screen_size_tool.py` |
| 鼠标点击 (x,y) | `mouse_tool.py click x y`；右键 `right_click x y`、中键 `middle_click x y`；拖拽 `drag x1 y1 x2 y2` |
| 当前光标位置 | `python scripts/mouse_tool.py pos`（输出 x y） |
| 鼠标滚轮 | `python scripts/mouse_tool.py scroll delta` |
| 常用组合键 | `keyboard_tool.py keys <vk1> <vk2>`（VK 十进制）；或 `keyboard_tool.py shortcut ctrl+k` / `shortcut ctrl+c` / `shortcut ctrl+v` 等（无需记 VK）。Ctrl=17, K=75, 故 Ctrl+K 也可写 `keys 17 75`。 |
| 键盘输入 | `python scripts/keyboard_tool.py type "内容"` 或 `key <vk>`（type 仅 ASCII） |
| 中文/Unicode 输入 | `do.py 输入中文 内容`（先写剪贴板再 Ctrl+V 粘贴）；计划中可用 step paste 粘贴剪贴板内容 |
| 看图提问 | `python scripts/vision_proxy.py <图路径> "问题"` |
| **获取点击坐标**（多轮取中位数） | `python scripts/vision_coords.py <图路径> "问题"` 或 run_plan 中 `{"do": "vision_coords", ...}`；默认归一化(0-1)转像素，加 `"pixel": true` 用像素直出；设 `FRIDAY_VISION_VERBOSE=1` 打印提示词与模型输出 |
| 执行计划（截图/vision/点击/输入等） | `python scripts/run_plan.py plans/xxx.json`；步骤类型：screenshot / vision / vision_coords / click / type / key / paste / scroll / wait / run；默认打印多模态输入输出（`--no-verbose` 可关闭）、自动启动 Qt 悬浮球显示进度（`--no-floating` 可跳过） |
| vision 输出解析为步骤 JSON | `python scripts/parse_vision_steps.py [文件或 stdin]` |
| 打开记事本 | `python scripts/launch_notepad.py [文件路径]` 或 `do.py 打开记事本` |
| 打开文件管理器 | `python scripts/launch_explorer.py [目录]` 或 `do.py 打开文件管理器` |
| 打开闹钟/日历 | `do.py 打开闹钟`、`do.py 打开日历` |
| 放个歌/播放音乐 | **查阅** `scenarios/play_music.json` 按步骤执行。**勿用浏览器** |
| 填写绩效达成/绩效申报 | **查阅** `scenarios/performance_declaration.json`：**直接** `run_plan plans/ihaier_performance_declaration.json`，勿手动截图+vision 逐步操作 |
| 打开音乐播放器 | 同上，或先 `do 已安装应用` 查列表，识别后 `do 打开应用 <名>`；保底 `do 打开WMP` |
| 已安装应用列表 | `do.py 已安装应用` 或 `installed_apps_tool.py`；`--json` 输出 JSON（含 name/version/publisher），默认每行一个应用名 |
| 剪贴板读/写 | `do.py 剪贴板读`、`do.py 剪贴板写 内容`；图片：`clipboard_tool.py image_get <路径>`、`image_set <路径>`；`do.py 剪贴板图片保存 [路径]`、`剪贴板图片写入 <路径>` |
| 防休眠、音量 | `do.py 防休眠 [秒]`、`do.py 音量静音`、`do.py 音量减`、`do.py 音量增`；精确音量：`volume_tool.py get`、`set <0-100>`；`do.py 音量值`、`do.py 设置音量 50` |
| 执行任意脚本 | `do.py run <脚本名> [参数...]`，如 `do.py run screenshot_tool`、`do.py run timer_tool 5 run launch_notepad` |
| 按回车（可用来确认弹窗） | `python scripts/keyboard_tool.py key 13` 或 `do.py 按回车` |
| 音量静音/减/增 | `python scripts/keyboard_tool.py key 173`（静音）/`174`（减）/`175`（增） |
| 剪贴板读/写/图片 | `clipboard_tool.py get`、`set "内容"`；`image_get <路径>` 将剪贴板图存为 BMP、`image_set <路径>` 从 BMP 写入剪贴板 |
| 定时 N 秒后执行 | `python scripts/timer_tool.py <秒数>` 仅等待；`timer_tool.py <秒> run launch_notepad` 等执行脚本 |
| 当前系统时间 | `python scripts/time_tool.py`（UTC）、`time_tool.py --local` 本地；`do.py 当前时间` |
| 主机名/用户名/路径展开 | `env_tool.py COMPUTERNAME|USERNAME|all`；`env_tool.py EXPAND %USERPROFILE%\\Desktop`；`do.py 主机名`、`do.py 用户名` |
| 进程列表/结束 | `python scripts/process_tool.py list`、`process_tool.py kill <进程名或PID>` |
| 复制/粘贴(组合键) | `do.py 复制`（Ctrl+C）、`do.py 粘贴`（Ctrl+V） |
| 打开闹钟与时钟 | `python scripts/launch_clock.py` |
| 打开日历（闹钟与时钟） | `python scripts/launch_calendar.py` |
| 防止休眠/关屏（N 秒内） | `python scripts/power_tool.py prevent_sleep [秒数]`，0 表示持续到进程结束 |
| 睡眠/休眠 | `power_tool.py sleep`、`power_tool.py hibernate`；`do.py 睡眠`、`do.py 休眠` |
| 关机/重启 | `power_tool.py shutdown [秒]`、`power_tool.py reboot [秒]`；`do.py 关机 [秒]`、`do.py 重启 [秒]`（默认立即） |
| 窗口激活（按标题/按进程名） | `window_tool.py activate "标题"`；`window_tool.py activate_process <进程名>`；`window_tool.py activate_pid <PID>`；按标题查 PID：`window_tool.py pid "标题"`。**ihaier 主窗口标题是「办公平台」**，请用 `activate "办公平台"` 或 `activate_process iHaier2.0`，不要用 `activate "ihaier"`。 |
| 窗口最大化（激活后先最大化再截图，有助于截取目标界面、避免背景干扰多模态） | `window_tool.py maximize "标题"`（如 `maximize "办公平台"`）；`window_tool.py maximize_process <进程名>`；计划中在 activate 后加一步 run window_tool args ["maximize", "办公平台"] 再 wait → screenshot |
| 显示/亮度 | `launch_settings.py display` 或 run_plan+vision；软件亮度：`brightness_tool.py get`、`set <0-100>`；`do.py 亮度`、`do.py 设置亮度 80` |
| 通知/Toast | `notification_tool.py show "正文"`；`do.py 通知 内容`（Win10+）；通知设置：`launch_settings.py notifications` |
| 打开运行对话框（Win+R） | `do.py 打开运行` 或 `keyboard_tool.py keys 91 82` |
| 任务管理器 | `do.py 任务管理器` 或 `python scripts/launch_taskmgr.py` |
| 计算器 | `do.py 计算器` 或 `python scripts/launch_calc.py` |
| 网络信息 | `do.py 网络信息`、`do.py 网络信息 all`；`network_tool.py [ipconfig|brief|wlan|interfaces]`；`do.py WLAN`、`do.py 网络接口` |
| 注册表读/写 | `reg_tool.py get HKCU "Software\\..." [值名]`、`reg_tool.py set HKCU "Software\\..." 值名 sz "内容"` 或 `dword 1`；根键 HKCU/HKLM/HKCR/HKU/HKCC |
| 文本文件读/写/列目录 | `file_tool.py read/write <路径> [内容]`、`file_tool.py list <目录>`；`do.py 列目录 [路径]` |
| Vision 坐标校准（维护偏移数据集） | `python scripts/vision_calibrate.py calibrate`：屏幕 5 点红点→截图→多模态识坐标→算偏移写入 state/vision_calibration.json；run_plan/click_from_vision_or_key 会自动加该偏移再点击。换分辨率后需重跑。详见 vision_parse_convention.md。 |
| 自主校验能力链（截图/鼠标/键盘/启动/vision/剪贴板） | `python scripts/self_verify_capabilities.py`，结果见 `state/self_verify_result.json` |
| 闭环跑者（无人时持续推进轮次与日志） | `python scripts/loop_runner.py` 一轮；`loop_runner.py --daemon [--interval 300]` 常驻 |
| 计划模板（plans/） | `minimal_self_verify.json`、`example_visit_website.json`、`example_ihaier_send_message.json`、`example_ihaier_check_messages.json`、`example_ihaier_who_contacted_me.json`、`example_ihaier_my_latest_message.json`、`ihaier_performance_declaration.json`（绩效达成申报）、`example_screenshot_vision.json`，供 run_plan 引用 |

## 说明

- 模型只需在识别到用户意图后，从表中选对应命令执行即可。
- 更多脚本见 SKILL.md「脚本」节；需求与能力链见 assumed_demands.md。
- **保底方案（鼠标+键盘+截图+多模态）** 在 Windows 上的界面引导（任务栏亮线切换应用、托盘向上箭头展开、托盘图标右键菜单等）见 **SKILL.md「保底方案：Windows 界面引导」**，规划 run_plan 或 vision 提问时可参考。
- **ihaier**：**能力**（读取消息列表、消息详情、视频会议、云文档、会议室预约、工作台、审批、日历、任务、搜索、发消息等）与 **场景**（谁找我、发消息给某人等）的区分及执行方式见 **references/ihaier_capabilities.md**。
