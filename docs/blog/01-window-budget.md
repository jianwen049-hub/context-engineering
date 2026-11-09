# 01 · 窗口预算：先算账再塞字

## 当时我怎么看这个问题

刚开始做多轮 Agent 时，我把「模型上下文上限」当成唯一约束：8192 就往 8192 塞。很快发现真实预算远更窄——要给**输出预留**、给**工具 JSON schema**留位、给**检索片段**留位，还要给模型一点「思考余量」。一次性塞满输入时，输出被截断，工具参数残缺，排障极痛：日志里只看到半截 JSON，还以为是模型「偶发抽风」。

另一次换模型（上下文从 8k 到 32k），有人把 packable 直接调满，结果账单与延迟一起飞——因为「能塞」不等于「该塞」。

## 试过什么

1. **硬编码 max_prompt_tokens=常量**：换模型 / 换输出长度需求就炸。
2. **只按字符数砍**：中英混排误差大，工具 schema 的括号与引号也被低估。
3. **超了再靠 API 报错回滚**：用户已感知失败，且重试把成本再乘一次。
4. **把 output 也算进同一截断池**：模型刚生成到关键结论被砍，体验比输入截断更差。

## 为什么否决

否决「窗口上限 = 可输入上限」。必须有显式 **Budget**：`model_limit - output_reserve - tool_reserve - safety_margin = packable`。打包前先算账。也否决「靠供应商报错当预算系统」——那是生产事故，不是控制流。

## 最终怎么解

`lab/src/context_lab/budget.py` 定义 `ContextBudget`：

- `model_limit`
- `output_reserve`
- `tool_reserve`
- `safety_margin`
- 属性 `packable_tokens`

`tokens.py` 提供启发式 `estimate_tokens` / `measure_message`，保证离线可测。Packer **只消费** `packable_tokens`，绝不直接读裸 `model_limit`。这样改 reserve 时，行为变化集中在一处。

## 用到的具体 skill / 技巧清单

| Skill | 用法 |
|-------|------|
| **输出预留** | output_reserve |
| **工具 schema 预留** | tool_reserve |
| **safety margin** | 防估算偏差与隐藏 framing |
| **启发式 token** | `tokens.py` |
| **按角色 framing** | 每条消息加固定开销 |
| **单测锁不变量** | packable < model_limit |

## 代码解析（按文件路径）

### `lab/src/context_lab/budget.py`

`ContextBudget.packable_tokens` 一处算清。单元测试锁定：提高 reserve 会缩小可打包额度。

### `lab/src/context_lab/tokens.py`

`estimate_tokens` + `measure_message`。为 packer 提供统一尺子——成本仓、压缩逻辑若复用同一尺子，跨仓数字才可比。

### `lab/scripts/smoke_check.py`

先断言 budget 不变量，再跑 packer；避免「测试只测快乐路径」。
