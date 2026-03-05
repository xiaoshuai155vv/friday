# Vision 输出解析约定

vision_proxy 返回自然语言。若需转为 run_plan 步骤（click/type/key），约定如下。

## 截图与屏幕尺寸（避免点击错位）

- **坐标体系**：screenshot_tool 与 mouse_tool 均使用 Windows **GetSystemMetrics** 得到的逻辑分辨率（与 DPI 一致）；截图像素尺寸 = 屏幕逻辑尺寸。
- **多模态注入**：vision_proxy 会**自动读取图片像素尺寸**并追加到提示中，要求模型在「此尺寸下」返回整数 x,y，避免 API 缩图导致坐标与屏幕不一致。
- **验证点击**：多模态返回 (x,y) 后，可用 `python scripts/click_verify.py x y 5` 将鼠标移到该点、等待 5 秒，目视核对是否点在预期位置；可选 `--screenshot path` 保存当前屏。屏幕尺寸：`python scripts/screen_size.py` 输出 `W H`。

## 期望 vision 回复格式（提示词中可要求）

- 坐标：`点击 (x, y)` 或 `click x y`，x、y 为**与截图/屏幕同尺寸的整数像素**。
- 输入：`输入 "内容"` 或 `type "内容"`。
- 按键：`按键 Enter` 或 `key 13`（VK 码十进制）。

## 解析方式

- 正则：`点击\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)`、`click\s+(\d+)\s+(\d+)`、`输入\s*["']([^"']*)["']`、`type\s*["']([^"']*)["']`。
- 解析出一步则追加到 plan 或直接调用 mouse_tool/keyboard_tool；多步则写入临时 plan.json 后 run_plan 执行。

## 后续

- 可实现在 scripts/parse_vision_steps.py：读 vision  stdout，输出 JSON 步骤数组或执行。
