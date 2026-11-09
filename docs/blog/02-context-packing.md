# 02 · Context Packing：优先级队列式塞消息

## 当时我怎么看这个问题

「从旧到新截断」是最常见的懒办法，但会切掉系统提示或用户第一条里的硬约束。另一种懒办法是「永远保留 system + 最近 k 轮」，中间工具结果全丢——Agent 会忘掉自己刚搜到的关键数字，然后开开心心再搜一遍，又贵又慢。

我还见过按时间均匀抽样的方案：语义上乱七八糟，模型看到的是「时间上均匀、信息上残缺」的拼盘。

## 试过什么

1. **FIFO 砍头**：伤 system / 初始约束。
2. **只留最近 k**：伤中期工具结果与记忆。
3. **按字数均匀抽样**：语义碎。
4. **Knapsack 求极限利用率**：理论漂亮，工程上难解释「为什么这条被丢」，也不利于单测稳定。

## 为什么否决

否决单一启发式。打包应是**带优先级的装箱**：system/pin > 当前 user > 记忆摘要 > 检索片段 > 最近对话 > 更旧对话。超预算时从优先级最低的开始丢，而不是从最旧的一刀切。可解释的 dropped 列表，比「多塞 3% token」更重要。

## 最终怎么解

`lab/src/context_lab/packer.py`：

- 输入：`PackItem(role, content, priority, kind)` 列表 + `ContextBudget`
- 算法：按 priority 降序尝试放入，放不下就记入 `dropped`
- 输出：`PackResult(messages, used_tokens, dropped)`；chosen 再按原始顺序排回，保证对话可读

这样测试都能断言：「system 永不被丢（除非 system 自身超过预算）」——后者应直接报错，而不是静默截断。

## 用到的具体 skill / 技巧清单

| Skill | 用法 |
|-------|------|
| **priority packing** | 数值越大越先占坑 |
| **kind 标签** | system/pin/memory/retrieval/history |
| **dropped 可观测** | 方便和 tracing 联动 |
| **确定性** | 同输入同输出，便于单测 |
| **与预算解耦** | packer 不关心 model 名 |
| **顺序恢复** | 选中后再按原序输出 |

## 代码解析（按文件路径）

### `lab/src/context_lab/packer.py`

核心循环可读性优先。`kind=="system"` 且自身超过 packable 时 `raise ValueError`——静默切 system 是最危险的行为之一。

### `lab/tests/test_packer.py`

覆盖：system 保留、used_tokens ≤ packable、memory kind 可生成。重构时先跑测试再谈「优化利用率」。

### `lab/src/context_lab/cli.py`

`pack` 子命令塞一套含记忆、检索、闲聊的例子，打印 dropped，便于博客对照。
