# 当前使命与任务状态（防迷失）

## 目的

在多轮对话与长期任务中，**始终知道我们当前要干什么**，避免迷失。

## 状态文件

- **路径**：`state/current_mission.json`
- **维护**：`scripts/state_tracker.py` 读写。

## 建议字段

```json
{
  "mission": "当前使命的一句话描述",
  "phase": "假设|规划|追踪|校验|决策",
  "current_goal": "本阶段要达成的目标",
  "next_action": "下一步具体动作",
  "task_id": "可选，当前任务 ID",
  "updated_at": "ISO8601 时间"
}
```

## 使用纪律

1. **行动前**：读取状态，确认 mission 与 phase 再执行。
2. **行动后**：更新 `current_goal` / `next_action` / `phase` 并写回。
3. **长任务**：在会话或文档中显式写出「当前阶段」「本轮目标」「下一步」。

## 常用命令示例

- 推进轮次：`python scripts/state_tracker.py set --mission "RoundN 描述" --phase "assume" --next "plan" --round N`
- 仅更新阶段：`state_tracker.py set --phase "规划" --next "执行"`

## 与闭环的关系

- `phase` 与闭环五模块对应，便于知道处在「假设」还是「校验」等。
- 任务追踪模块可扩展状态（如 task_list、blockers），仍以 current_mission 为单一真相源。
