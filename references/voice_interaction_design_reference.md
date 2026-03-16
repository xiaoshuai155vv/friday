# 语音交互设计参考：ai_vision_chat → 星期五悬浮球

> 悬浮球是当前与 CC、LLM 交互的**唯一入口**。参考 `D:\ai\ai-lab\ai_vision_chat` 的 Flutter 语音交互设计，将语音能力集成到星期五悬浮球，实现拟人化语音交互。  
> 讯飞（科大讯飞）API 已在本机配置可用。

---

## 一、ai_vision_chat 语音交互架构（Flutter）

### 1. 核心组件

| 组件 | 文件 | 职责 |
|------|------|------|
| **VoiceWakeupManager** | `voice_wakeup_manager.dart` | 唤醒词（贾维斯、jarvis、小贾等）、退下词（拜拜、再见、退下等）、2 分钟无交互自动休眠 |
| **ContinuousListeningService** | `continuous_listening_service.dart` | 持续监听麦克风、调用真实时语音识别、语音结束回调 |
| **TrueRealtimeSpeechService** | `true_realtime_speech_service.dart` | 讯飞 WebSocket 实时语音识别、流式传输、partial/final 结果 |
| **XunfeiTTSService** | `xunfei_tts_service.dart` | 讯飞 TTS WebSocket、PCM→WAV、按需连接 |
| **FloatingChatOverlay** | `floating_chat_overlay.dart` | 唤醒后显示悬浮对话、消息列表、展开/收起 |
| **AppProvider** | `app_provider.dart` | 统一状态、服务初始化、TTS 完成后恢复监听 |

### 2. 交互流程

```
启动应用
  → 初始化 ContinuousListeningService、VoiceWakeupManager、TrueRealtimeSpeechService
  → 启动持续监听（麦克风 → 讯飞 WebSocket 实时识别）
  → 用户说「贾维斯」→ VoiceWakeupManager 检测唤醒词 → 唤醒
  → 显示 FloatingChatOverlay（悬浮对话）
  → 用户说命令 → onWakeupCommand 回调 → 执行（LLM/工具/RPA）
  → TTS 播放回复 → onSpeechComplete → 恢复监听
  → 用户说「拜拜」→ 退下、隐藏悬浮窗
  → 2 分钟无交互 → 自动休眠
```

### 3. 讯飞配置（xunfei_config.dart）

```dart
// 讯飞开放平台 https://console.xfyun.cn/
static const String appId = '...';
static const String apiKey = '...';
static const String apiSecret = '...';

// TTS 发音人
static const String voice = 'xiaoyan';  // 小燕
static const int speed = 50;
static const int volume = 50;
static const int pitch = 50;
```

### 4. 唤醒词与退下词

**唤醒词**：贾维斯、jarvis、嘉维斯、小贾、小助手、hey jarvis、你好贾维斯 等  
**退下词**：拜拜、再见、你可以退下了、退下、隐藏、睡觉、bye、goodbye 等

---

## 二、星期五当前状态

| 能力 | 现状 |
|------|------|
| **悬浮球** | PyQt5、圆形置顶、右键菜单（过程·结果、OneCall、提交进化环、自动进化环） |
| **TTS** | `tts_engine.py`：pyttsx3 / Windows SAPI / gTTS，**未用讯飞** |
| **语音识别** | `voice_interaction_engine.py` 存在，具体实现待查 |
| **语音唤醒** | 无 |
| **持续监听** | 无 |
| **悬浮对话** | OneCall 为多模态（截图+提问），非语音对话 |

---

## 三、集成方案：悬浮球 + 讯飞语音

### 方案 A：在悬浮球内嵌语音（Python + 讯飞 WebSocket）

1. **新增 `xunfei_tts_service.py`**  
   - 参考 ai_vision_chat 的 `xunfei_tts_service.dart`  
   - 使用 `websocket-client` 连接讯飞 TTS WebSocket  
   - 输出 PCM→WAV，用 `pygame` 或 `playsound` 播放  

2. **新增 `xunfei_asr_service.py`**  
   - 参考 `true_realtime_speech_service.dart`  
   - 麦克风 → 讯飞语音听写 WebSocket（`iat-api.xfyun.cn`）  
   - 支持 partial / final 结果回调  

3. **新增 `voice_wakeup_manager.py`**  
   - 唤醒词：星期五、贾维斯、小五、hey friday 等  
   - 退下词：拜拜、再见、退下 等  
   - 2 分钟无交互自动休眠  

4. **悬浮球集成**  
   - 启动时可选开启「语音监听」  
   - 检测到唤醒词 → 显示语音对话浮层（类似 FloatingChatOverlay）  
   - 用户说话 → ASR → 文本 → 调用 `do.py` 或 CCR/LLM  
   - 回复 → TTS 播放 → 播放完成 → 恢复监听  

### 方案 B：Flutter 悬浮窗与星期五桥接

- 在 Windows 上运行 ai_vision_chat 的 Flutter 版本（若支持）  
- Flutter 负责：语音唤醒、ASR、TTS、悬浮 UI  
- 通过 HTTP/WebSocket 与星期五的 `do.py`、CCR 通信  
- 用户语音 → Flutter 识别 → 发请求给星期五 → 星期五执行 → 返回结果 → Flutter TTS 播放  

### 方案 C：混合（推荐起步）

- **悬浮球**：保持现有 PyQt5 悬浮球，作为主入口  
- **语音**：新增 Python 讯飞 ASR/TTS 服务，由悬浮球调用  
- **唤醒**：见下「电脑端触发与唤醒」  
- **对话**：语音文本 → `do.py` 或 evolution_loop_client → 结果 → TTS 播放  

---

## 三.1 电脑端触发与唤醒（重要）

**与手机端差异**：电脑端用户通常离麦克风较远、环境噪音多（键盘、视频、周围人声），持续语音唤醒易误触发、耗资源、有隐私顾虑。**应以快捷键/点击为主，语音唤醒为可选增强**。

### 主触发方式（电脑端优先）

| 方式 | 说明 | 实现 |
|------|------|------|
| **快捷键唤醒** | 用户按快捷键后开始听，说完自动结束 | 新增全局热键（如 `Ctrl+Shift+V`），按下→开启 ASR→松开或静音结束→识别→执行 |
| **点击悬浮球唤醒** | 点击悬浮球或右键菜单「开始语音」 | 点击后弹出语音浮层，开始录音，说完或点击结束 |
| **「按住说话」** | 按住某键（如空格）时录音，松开结束 | 类似微信语音，可控、无持续监听 |

### 可选：语音唤醒（用户主动开启时）

- **不默认开启**：用户需在菜单中勾选「开启语音唤醒」  
- **持续监听**：仅在开启后后台监听，检测唤醒词（星期五、贾维斯）  
- **退下词**：拜拜、退下 等  
- **自动休眠**：2 分钟无交互自动关闭语音监听  
- **麦克风选择**：电脑可能有内置麦、外接麦、耳机麦，需支持在设置中选择  

### 与现有快捷键的关系

悬浮球已有：
- `Ctrl+Shift+S`：全屏截图  
- `Ctrl+Shift+Q`：框选区域  

建议新增：
- `Ctrl+Shift+V`：**开始语音输入**（按下即录，说完自动识别；或按下弹出浮层，再说话）  
- 或 `Ctrl+Space`：若与系统冲突可改用 `Ctrl+Alt+V`  

### 电脑端推荐流程

```
用户按 Ctrl+Shift+V（或点击悬浮球「语音」）
  → 弹出语音输入浮层，开始 ASR 录音
  → 用户说话（3～10 秒内）
  → 静音检测结束 或 用户点击「结束」
  → 讯飞返回文本 → 调用 do.py / CCR
  → TTS 播放回复
  → 浮层可继续下一轮或关闭

（可选）用户开启「语音唤醒」
  → 后台持续监听
  → 检测到「星期五」→ 自动弹出语音浮层，开始录音
  → 同上流程
```

---

## 四、讯飞 API 使用要点（Python）

### 1. 语音听写（ASR）

- 接口：`wss://iat-api.xfyun.cn/v2/iat`  
- 鉴权：URL 中带 `authorization`、`date`、`host`（HMAC-SHA256 签名）  
- 音频：16k 采样、16bit、单声道 PCM，按帧发送  

### 2. 语音合成（TTS）

- 接口：`wss://tts-api.xfyun.cn/v2/tts`  
- 请求：JSON，含 `common.app_id`、`business`（aue、vcn、speed 等）、`data.text`（base64）  
- 响应：`data.audio` 为 base64 PCM，需加 WAV 头后播放  

### 3. 配置存放

- 建议：`runtime/config/xunfei_config.json` 或环境变量  
- 字段：`app_id`、`api_key`、`api_secret`  
- 勿提交到 git，可提供 `xunfei_config.example.json`  

---

## 五、拟人化设计对照

| 维度 | ai_vision_chat（手机端） | 星期五（电脑端） |
|------|--------------------------|------------------|
| **主唤醒** | 说「贾维斯」唤醒 | **快捷键（Ctrl+Shift+V）或点击悬浮球**，语音唤醒为可选 |
| **退下** | 说「拜拜」退下 | 说「拜拜」退下（仅语音唤醒开启时）；或点击关闭浮层 |
| **自动休眠** | 2 分钟无交互 | 可配置；语音监听不默认开启 |
| **对话展示** | FloatingChatOverlay 消息列表 | 悬浮球内或独立浮层 |
| **TTS 回复** | 讯飞 TTS 播放 | 讯飞 TTS（替换/补充 pyttsx3） |
| **持续监听** | 后台一直听 | **按需开启**：用户勾选「语音唤醒」后才持续监听 |
| **麦克风** | 设备单一 | **支持选择**：内置/外接/耳机麦 |

---

## 六、实施步骤建议（电脑端优先）

1. **配置讯飞**  
   - 复制 `config/xunfei_config.example.json` 到 `runtime/config/xunfei_config.json`  
   - 填入 app_id、api_key、api_secret  

2. **实现 xunfei_tts_service.py**  
   - WebSocket 连接讯飞 TTS  
   - 供悬浮球和 do.py 调用  

3. **实现 xunfei_asr_service.py**  
   - 麦克风采集 + 讯飞实时听写  
   - 支持 partial/final 回调  
   - **支持麦克风设备选择**（Windows 枚举音频输入设备）  

4. **悬浮球集成（电脑端主流程）**  
   - **快捷键**：新增 `Ctrl+Shift+V` 全局热键，按下→弹出语音浮层→开始 ASR  
   - **右键菜单**：新增「开始语音」项，点击即弹出浮层并开始录音  
   - 语音浮层：显示实时识别、结束按钮，说完或点击结束→调用 do.py / CCR  
   - TTS 播放回复  

5. **可选：voice_wakeup_manager.py**  
   - 唤醒词/退下词检测  
   - 仅当用户勾选「开启语音唤醒」时启用持续监听  
   - 与悬浮球状态联动  

6. **do.py 集成**  
   - `do 语音`、`do 开始语音` 等意图  

---

## 七、实施状态（v1.0，2026-03）

已完成：
- `runtime/config/xunfei_config.example.json` 示例配置
- `scripts/xunfei_config_loader.py` 配置加载
- `scripts/xunfei_tts_service.py` 讯飞 TTS（WebSocket + PCM→WAV）
- `scripts/xunfei_asr_service.py` 讯飞 ASR（录音 + IAT WebSocket）
- `scripts/voice_capture.py` 命令行语音捕获
- 悬浮球：Ctrl+Shift+V 快捷键、右键「开始语音」、FridayVoiceDialog 浮层
- do.py：`语音`、`开始语音` 意图
- tts_engine.speak_text：配置讯飞时优先使用讯飞 TTS

依赖：`pip install websocket-client sounddevice numpy`

---

## 八、参考文件路径

| 项目 | 路径 |
|------|------|
| ai_vision_chat 语音唤醒 | `D:\ai\ai-lab\ai_vision_chat\lib\services\voice_wakeup_manager.dart` |
| ai_vision_chat 持续监听 | `D:\ai\ai-lab\ai_vision_chat\lib\services\continuous_listening_service.dart` |
| ai_vision_chat 讯飞实时识别 | `D:\ai\ai-lab\ai_vision_chat\lib\services\true_realtime_speech_service.dart` |
| ai_vision_chat 讯飞 TTS | `D:\ai\ai-lab\ai_vision_chat\lib\services\xunfei_tts_service.dart` |
| ai_vision_chat 悬浮对话 | `D:\ai\ai-lab\ai_vision_chat\lib\widgets\floating_chat_overlay.dart` |
| ai_vision_chat 讯飞配置 | `D:\ai\ai-lab\ai_vision_chat\lib\config\xunfei_config.dart` |
| 星期五悬浮球 | `d:\ai\ai-lab\星期五\scripts\friday_floating_qt.py` |
| 星期五 TTS | `d:\ai\ai-lab\星期五\scripts\tts_engine.py` |
