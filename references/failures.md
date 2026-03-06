# 吃一堑长一智：失败与教训

## 目的

从失败中吸取教训，在「主动决策」与「主动规划」时查阅，避免重复错误。

## 维护方式

- 每次校验不通过或执行失败时，在本文档或等价结构中**追加一条**教训。
- 建议格式：日期、简短描述、原因分析、下次如何避免（或策略变更）。

## 示例条目

```markdown
- 2025-03-02：某自动化步骤因窗口未前置失败 → 原因：未等待窗口激活。下次：先激活目标窗口再发送按键。
```

- 2026-03-02：screenshot_tool 写 BMP 时 buf 切片非 bytes → 原因：ctypes 数组切片类型。下次：用 memoryview(buf).tobytes() 写入。
- 2026-03-02：run_plan 中 vision 步骤报错 → 原因：未配置 vision_config.json 或环境变量。下次：规划时注明「需配置多模态 API」；无 key 时 run_plan 可跳过 vision 或记入 failures，不阻断整链。
- 2026-03-02：打开摄像头时出现「需要用新应用打开此 microsoft.windows.camera 链接」弹窗阻断 → 改用 **camera_qt.py**（PyQt5 直接打开摄像头，无白框）。
- 2026-03-02：自校验用 vision 判别「是否有 CMD/是否圆形/是否无标题栏」时 vision_proxy 可能超时 → 下次：自校验轮可设较短 vision 超时或重试；或记录「待人工抽检」后继续下一轮假设。
- 2026-03-02：悬浮窗内嵌 WebView 白底、右侧/底部圆仍被裁切 → 原因：WebView2 默认 DefaultBackgroundColor 为白；透明模式内圆 92vmax/大 ring 仍超出 420 圆。下次：设环境变量 WEBVIEW2_DEFAULT_BACKGROUND_COLOR=00000000；透明模式再缩小 grid(78vmax)/ring/orb 使全部落在圆内。
- 2026-03-02：Windows 上悬浮窗白底始终不变 → 原因：pywebview 文档写明 transparent 在 Windows 不支持；WEBVIEW2_DEFAULT_BACKGROUND_COLOR 在当前环境下未生效。采用回退：悬浮窗用深色底 #0a0a0f（create_window background_color + 页面 transparent-mode 用同色），与 UI 风格一致，不再露白。
- 2026-03-04：ihaier 检查「是否有人找我」：run_plan 执行时 vision 结果打印触发 Windows 控制台 gbk UnicodeEncodeError；activate_process ihaier 未找到窗口时整链中断。下次：run_plan 内 stdout 使用 utf-8 或安全编码再打印 vision 输出；用户未打开 ihaier 时可先截当前屏再 vision 作保底。
- 2026-03-04：Claude Code 执行时 ihaier 窗口激活一直失败（activate "办公平台"、activate_process iHaier2.0、activate_pid 均 SetForegroundWindow 返回 0）。原因：1) iHaier2.0 多进程，原先只激活「第一个可见窗口」可能是子进程小窗而非主窗口「办公平台」；2) Windows 限制只有近期有用户输入的进程才能抢前台，Claude Code 在后台/不同会话跑脚本时无前台权限；3) iHaier 为 Electron（Chrome_WidgetWin_1），抢前台更易被系统拒绝。下次：window_tool 已改进——activate_process 时收集该进程名所有可见窗口并**优先激活标题含「办公平台」**的窗口；SetForegroundWindow 失败时尝试 **AttachThreadInput + BringWindowToTop** 再激活。若仍在 Claude Code/远程会话中失败，需在**用户本机交互式桌面**执行（如本机 CMD 或 `run_with_env` 在本机终端跑）。
- 2026-03-05：激活后的应用有时未最大化，截图时背景露出其他窗口，导致多模态识别出错。下次：**激活后先最大化再截图/多模态**。能力：`window_tool maximize "标题"` 或 `maximize_process 进程名`；计划中在 activate 后增加一步 `run window_tool args ["maximize", "办公平台"]`，再 wait → screenshot。
- 2026-03-05：悬浮窗（friday_floating_qt / launch_friday_floating）在无桌面/远程会话（如 Claude Code 所在环境）中启动失败。下次：**悬浮窗非必须**，主流程（run_plan、截图、vision 等）不依赖它；失败可忽略；若需展示状态，在本机有交互式桌面时再启动悬浮窗。
- 2026-03-05：剪贴板 `clipboard_tool set` 在远程/无交互桌面会话中报 **SetClipboardData failed**，导致「搜索框粘贴联系人名」步骤失败。下次：**计划中可用 `keyboard_tool type "中文"`**（已支持 Unicode）；或备用 `set_clipboard_ps` + paste。剪贴板仍用于发消息等场景（`clipboard_tool` 保留）。
- 2026-03-05：vision 返回的点击 x 坐标比实际少约 210（1920×1080）。原因：多模态可能返回的是**界面内某块区域（如搜索列表区）的相对坐标**，而 ihaier 左侧导航栏约占 210px，导致全屏坐标 = 返回坐标 + 210。截图/鼠标/click_verify 均用 GetSystemMetrics，坐标系统一致，非分辨率或点击工具错误。下次：**vision_proxy** 已加强提示「返回坐标必须以整张图片左上角为原点」；**run_plan** 的 click 步骤支持 `vision_coords_offset: {"x": 210, "y": 0}` 做固定偏移；ihaier 计划已加该偏移。若换分辨率或布局，可调 offset 或复测。
- 2026-03-05：`process_tool.py list` 在 GBK 控制台下报 **'gbk' codec can't encode character**（进程名含 Unicode 时）。下次：**process_tool** 已用 `_safe_print` 兜底，无法用 reconfigure 时改为写 stdout.buffer UTF-8 字节，避免崩溃。**激活 ihaier** 请用 `window_tool activate "办公平台"` 或 `activate_process iHaier2.0`，不要用 `activate "ihaier"`（无匹配窗口）；已在 capabilities 与 SKILL 必守约定中写明。
- 2026-03-06：ihaier 搜索框输入联系人后，`keyboard_tool key 13` 按回车无效（与手动按键盘效果不同）。原因：1) keybd_event 对部分应用（如 Electron/ihaier）响应异常；2) 搜狗等输入法可能拦截 VK_RETURN。下次：**keyboard_tool** 已改为用 **SendInput** 发送按键；对 Enter(VK 13) 特别用**扫描码 0x1C** 发送，减少被 IME 拦截。**不要**在搜索框场景按 Esc（会取消搜索框）。
- 2026-03-06：`selfie` 执行时弹窗「no Qt platform plugin could be initialized」。原因：便携 Python 或子进程环境下 Qt 找不到 platform 插件（platforms/qwindows.dll）。下次：**camera_qt.py** 启动时若未设置 `QT_QPA_PLATFORM_PLUGIN_PATH`，则根据 PyQt5 安装路径自动设为 `PyQt5/Qt5/plugins/platforms`。
- 2026-03-06：selfie 报「未检测到可用摄像头」：run_with_env 用项目便携 Python 时 camera_qt 可能检测不到摄像头。下次：**run_with_env** 传 `FRIDAY_INVOKER_PYTHON`（调用者 python）；**selfie** 与 **do.py** 用该解释器运行 camera_qt；若仍失败，直接用 `python scripts/selfie.py`（不用 run_with_env）。

## 与决策的关系

- 主动决策阶段：查阅本表与最近日志，再决定下一轮假设/规划。
- 主动规划阶段：若新任务与历史教训相关，在规划中显式加入「避免 XXX」的步骤。
- 多轮连续进化时：自校验（self_verify_capabilities.py）可隔轮或每 N 轮执行一次，不必每轮都跑，以节省时间。
