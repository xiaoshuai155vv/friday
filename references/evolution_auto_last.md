# 当前核心目录与文件树（简要）
scripts/ references/ assets/ runtime/ 等（一行即可）

# 本轮影响文件
scripts/realtime_guidance_engine.py, scripts/do.py

## 2026-03-13 round 169
- **current_goal**：智能实时操作指导引擎 - 让系统实时观察用户操作、识别动作、预测意图并提供智能辅助
- **做了什么**：
  1. 创建 realtime_guidance_engine.py 模块，实现智能实时操作指导引擎功能
  2. 实现窗口信息获取功能（GetForegroundWindow API）
  3. 实现操作类型识别（file_browse、web_browse、chat、document_edit 等）
  4. 实现意图预测功能（基于历史操作序列）
  5. 实现智能建议生成（根据操作类型和上下文）
  6. 实现操作历史记录和上下文管理
  7. 支持守护进程模式持续监控
  8. 在 do.py 中添加「实时指导」「操作指导」「智能辅助」等关键词触发支持
  9. 基线验证通过（5/6，剪贴板远程限制为已知问题）
  10. 本轮针对性验证通过：realtime_guidance_engine.py 的 status/suggestions/context 命令均可正常工作
- **是否完成**：已完成
- **下一轮建议**：可增强与 vision 的集成实现更精确的界面元素识别；可添加实时通知功能；可实现操作预测后的自动执行