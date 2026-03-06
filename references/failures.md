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
- 2026-03-02：打开摄像头时出现「需要用新应用打开此 microsoft.windows.camera 链接」弹窗阻断 → launch_camera 已改为：CAMERA_APP_PATH → shell:AppsFolder → **PyQt5 直接打开摄像头**（camera_qt.py，项目已集成 Qt，无系统相机时用此方式无白框）→ protocol。若本机无 Windows 相机且商店不可用，会优先走 Qt 摄像头；也可设 CAMERA_APP_PATH 指定第三方 exe。
- 2026-03-02：自校验用 vision 判别「是否有 CMD/是否圆形/是否无标题栏」时 vision_proxy 可能超时 → 下次：自校验轮可设较短 vision 超时或重试；或记录「待人工抽检」后继续下一轮假设。
- 2026-03-02：悬浮窗内嵌 WebView 白底、右侧/底部圆仍被裁切 → 原因：WebView2 默认 DefaultBackgroundColor 为白；透明模式内圆 92vmax/大 ring 仍超出 420 圆。下次：设环境变量 WEBVIEW2_DEFAULT_BACKGROUND_COLOR=00000000；透明模式再缩小 grid(78vmax)/ring/orb 使全部落在圆内。
- 2026-03-02：Windows 上悬浮窗白底始终不变 → 原因：pywebview 文档写明 transparent 在 Windows 不支持；WEBVIEW2_DEFAULT_BACKGROUND_COLOR 在当前环境下未生效。采用回退：悬浮窗用深色底 #0a0a0f（create_window background_color + 页面 transparent-mode 用同色），与 UI 风格一致，不再露白。
- 2026-03-04：ihaier 检查「是否有人找我」：run_plan 执行时 vision 结果打印触发 Windows 控制台 gbk UnicodeEncodeError；activate_process ihaier 未找到窗口时整链中断。下次：run_plan 内 stdout 使用 utf-8 或安全编码再打印 vision 输出；用户未打开 ihaier 时可先截当前屏再 vision 作保底。
- 2026-03-04：Claude Code 执行时 ihaier 窗口激活一直失败（activate "办公平台"、activate_process iHaier2.0、activate_pid 均 SetForegroundWindow 返回 0）。原因：1) iHaier2.0 多进程，原先只激活「第一个可见窗口」可能是子进程小窗而非主窗口「办公平台」；2) Windows 限制只有近期有用户输入的进程才能抢前台，Claude Code 在后台/不同会话跑脚本时无前台权限；3) iHaier 为 Electron（Chrome_WidgetWin_1），抢前台更易被系统拒绝。下次：window_tool 已改进——activate_process 时收集该进程名所有可见窗口并**优先激活标题含「办公平台」**的窗口；SetForegroundWindow 失败时尝试 **AttachThreadInput + BringWindowToTop** 再激活。若仍在 Claude Code/远程会话中失败，需在**用户本机交互式桌面**执行（如本机 CMD 或 `run_with_env` 在本机终端跑）。
- 2026-03-05：激活后的应用有时未最大化，截图时背景露出其他窗口，导致多模态识别出错。下次：**激活后先最大化再截图/多模态**。能力：`window_tool maximize "标题"` 或 `maximize_process 进程名`；计划中在 activate 后增加一步 `run window_tool args ["maximize", "办公平台"]`，再 wait → screenshot。
- 2026-03-05：悬浮窗（friday_floating_qt / launch_friday_floating）在无桌面/远程会话（如 Claude Code 所在环境）中启动失败。下次：**悬浮窗非必须**，主流程（run_plan、截图、vision 等）不依赖它；失败可忽略；若需展示状态，在本机有交互式桌面时再启动悬浮窗。
- 2026-03-05：剪贴板 `clipboard_tool set` 在远程/无交互桌面会话中报 **SetClipboardData failed**，导致「搜索框粘贴联系人名」步骤失败、页面未输入、后续回车/点击无效。下次：**计划中改用 `set_clipboard_ps`**（`scripts/set_clipboard_ps.py`，通过 PowerShell `Set-Clipboard` 写剪贴板），在该类环境中更易成功；`keyboard_tool type` 仅支持 ASCII，**不能用于输入中文**，仍以剪贴板 set + paste 为主。

## 与决策的关系

- 主动决策阶段：查阅本表与最近日志，再决定下一轮假设/规划。
- 主动规划阶段：若新任务与历史教训相关，在规划中显式加入「避免 XXX」的步骤。
- 多轮连续进化时：自校验（self_verify_capabilities.py）可隔轮或每 N 轮执行一次，不必每轮都跑，以节省时间。
