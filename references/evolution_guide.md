# 自我进化实施指南

## 始终知道当前要干什么

- 每轮开始：`python scripts/state_tracker.py read` 查看当前使命与阶段。
- 每轮结束：用 `state_tracker.py set` 更新状态，用 `behavior_log.py` 写一条日志。

## 闭环执行顺序

1. **主动假设**：读 `references/capability_gaps.md` 与 `references/failures.md`，列出/补充需求假设（含用户补充、私域见 references/private_domains.md），写一条 `assume` 日志。
2. **主动规划**：产出能力清单与任务分解，写 `plan` 日志。
3. **任务追踪**：执行任务并更新状态与 `track` 日志。
4. **完成校验**：测试是否满足假设，写 `verify` 日志；失败则记入 `references/failures.md`。
5. **主动决策**：查阅 failures 与日志，决定下一轮假设/规划或结束，写 `decide` 日志。

## 未满足时不反馈

若校验未通过，不向用户汇报失败，而是根据「主动决策」更新假设或规划，继续下一轮闭环，直到满足。

## 多轮持续（必须遵守）

- **不得在一轮结束后停止**：单轮完成不足以达成目标，自主假设、自主规划、自主决策需形成常态。
- **每轮 decide 之后**：必须更新 state（当前使命、阶段、下一轮假设/目标），并立即进入下一轮的「假设」或「规划」，不在对话或执行中「结束并总结」。
- **轮次可记录**：在 mission 或 state 中可含「第 N 轮」，便于 UI 与日志溯源；行为日志持续写入，export_recent_logs 供 UI 展示整体进度。

## Git 与版本

- 每次功能修改：`git add` → `git commit -m "feat: 描述 (vX.Y.Z)"` → 更新 `VERSION` 文件。
- 推送到 master：需先添加远程仓库 `git remote add origin <url>`，再 `git push -u origin master`。

## 多模态备用

需要看图理解时，使用本技能内 `scripts/vision_proxy.py`，配置 `vision_config.json`（可参考 `assets/vision_config.example.json`）填写 API。

## 私域与用户补充

- 私域：见 `references/private_knowledge.md`、`references/private_domains.md`，按需用 `scripts/load_private_knowledge.py get domains` 等加载。
- 用户补充需求：纳入「主动假设」清单，并在闭环中回环实现。
