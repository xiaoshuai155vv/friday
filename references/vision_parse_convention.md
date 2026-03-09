# Vision 输出解析约定

vision_proxy 返回自然语言。若需转为 run_plan 步骤（click/type/key），约定如下。

## 提示词风格（多模态看图）

- **简短上下文 + 明确任务**：先交代「图中是电脑桌面，打开的 ihaier 应用，[具体区域]」，再写要输出的内容（如「输出 xxx 的中间坐标，仅一行 x y」）。提示词不宜过长，以免干扰模型思考。
- **坐标类**：可直接写「输出 [某区域/某列表项] 的中间坐标，仅一行 x y」或「返回第一条可点击结果的中间坐标，仅一行 x y。无法识别则返回：否」。
- **读内容类**：写「输出右侧最下面一条消息的发送方、内容和时间」等，不堆砌「请读取」「完整内容」「包括」等冗余词。

## 截图与屏幕尺寸（避免点击错位）

- **坐标体系**：screenshot_tool 与 mouse_tool 均使用 Windows **GetSystemMetrics** 得到的逻辑分辨率（与 DPI 一致）；截图像素尺寸 = 屏幕逻辑尺寸。
- **绝对坐标约束**：vision_proxy 会**自动注入**图片尺寸与坐标约束，要求模型返回以整张图最左上角 (0,0) 为原点的**绝对像素坐标**，不能缩放、不能只算某块区域、不能使用界面内相对坐标。场景/计划 JSON 中无需再写。
- **截图文件名带时间戳**：run_plan 执行 screenshot 步骤时，会自动在文件名中加上 `_YYYYMMDD_HHMMSS`，便于区分多轮截图、大模型与人工排查；后续同一步骤中的 vision 若引用该截图路径，会自动使用带时间戳的实际路径。
- **验证点击**：多模态返回 (x,y) 后，可用 `python scripts/click_verify.py x y 5` 将鼠标移到该点、等待 5 秒，目视核对；可选 `--screenshot path` 保存当前屏。屏幕尺寸：`python scripts/screen_size.py` 输出 `W H`。
- **不写死坐标**：计划中可用 `{"do": "click", "from_vision_coords": true}`，则从上一步 vision 的输出中解析「x y」两个整数并点击；上一步 vision 的提问需明确要求「仅输出 x y 两数、空格分隔」。
- **坐标类用 vision_coords**：当步骤需要返回点击坐标时，用 `{"do": "vision_coords", ...}`，run_plan 会调用 vision_coords.py（内部多轮取中位数）；非坐标类（如读消息内容）用 `{"do": "vision", ...}`。
- **归一化坐标**：若模型像素坐标不准（如 x 偏小），可加 `"normalized": true` 让模型输出 0-1 归一化坐标，脚本自动乘以图片尺寸转为像素。适用于 GLM/Qwen3 等内部可能缩放图片的模型。

## Vision 坐标校准（维护偏移数据集）

多模态返回的坐标常存在系统性偏移（如整屏少 x、DPI/分辨率差异）。可通过**屏幕校准**得到当前环境下的偏移量并持久化。**默认不启用校准**，仅用多模态原始坐标；需启用时设环境变量 `FRIDAY_USE_VISION_CALIBRATION=1`，run_plan / click_from_vision_or_key 会加上校准偏移再点击。

**流程（scripts/vision_calibrate.py）**：

1. **calibrate（一键全流程）**：在屏幕 5 个已知位置（左上、中、右上、左下、右下）用**红点标记**（tkinter 小窗口）→ 全屏**截图** → 调 **vision** 识别「每个红点中心的像素坐标」→ 解析多组 x y → 与真实坐标逐对求差，**取平均**得到 offset_x、offset_y → 写入 **state/vision_calibration.json**（含 screen_w、screen_h、samples、updated_at）。分辨率变更后需重新校准。
2. **draw**：仅画红点并截图（不调 vision），便于人工核对或单独再跑 vision。
3. **get-offset**：输出当前校准的 offset_x offset_y（无校准则输出 0 0）。

**使用**：

- 首次或换分辨率/换机后执行一次：`python scripts/vision_calibrate.py calibrate`（需已配置 vision_config.json 与 tkinter）。
- 之后所有 `click from_vision_coords` 与 `click_from_vision_or_key` 会先读 state/vision_calibration.json，若分辨率与当前屏一致则自动对解析出的 (x,y) 加上 offset_x、offset_y 再点击；计划内的 vision_coords_offset 仍会先加，校准则在其基础上再加。

## 期望 vision 回复格式（提示词中可要求）

- 坐标：`点击 (x, y)` 或 `click x y`，x、y 为**与截图/屏幕同尺寸的整数像素**。
- 输入：`输入 "内容"` 或 `type "内容"`。
- 按键：`按键 Enter` 或 `key 13`（VK 码十进制）。

## 解析方式

- 正则：`点击\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)`、`click\s+(\d+)\s+(\d+)`、`输入\s*["']([^"']*)["']`、`type\s*["']([^"']*)["']`。
- 解析出一步则追加到 plan 或直接调用 mouse_tool/keyboard_tool；多步则写入临时 plan.json 后 run_plan 执行。

## 后续

- 可实现在 scripts/parse_vision_steps.py：读 vision  stdout，输出 JSON 步骤数组或执行。
