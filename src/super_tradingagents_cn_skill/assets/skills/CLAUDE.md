# CLAUDE.md — Super TradingAgents CN

## 这是什么

这是 A股多Agent投研分析框架的项目级指令文件。当你在这个项目中工作时，如果用户要求进行 A股个股分析、投研报告生成或交易诊断，请严格遵循以下规范执行。

## 核心能力

- **7 分析师角色**：市场/舆情/新闻/基本面/政策/游资/解禁
- **多空辩论**：Bull vs Bear 评分矩阵交锋
- **决策链路**：7 Analyst → 辩论 → 综合研判 → 交易方案 → 风控辩论 → 最终决策
- **双模式**：完整模式（LLM驱动）/ 轻量模式（规则引擎+数据驱动）

## 默认执行模式

**轻量模式**（无 LLM API Key 依赖）：

1. 用 `tradingagents.dataflows.a_stock` 工具采集数据（全部免费，无需Key）
2. 基于规则引擎生成结构化数据报告
3. 评分矩阵模拟多空辩论
4. 六维加权评分 → 时序判断（短/中/长期）
5. A股约束交易方案（T+1，涨跌停±20%，最小手数100股）
6. 最终决策：Signal + 仓位 + 信心度

## 三层循环交互

采用 LOOP ENGINEERING 架构：

- **外层**：用户对话循环（感知输入 → 解析意图 → 路由）
- **中层**：分析师轮询循环（7位分析师逐轮展示，用户可介入）
- **内层**：工具调用循环（ReAct 模式，失败自动重试/切换数据源）

## 7 分析师角色与工具

| 角色 | 数据工具 |
|------|----------|
| 市场分析师 | get_stock_data(ticker, start, end), get_indicators(symbol, indicator, date, days) |
| 舆情分析师 | get_news(ticker, start, end) |
| 新闻分析师 | get_news, get_global_news(limit), get_insider_transactions(ticker) |
| 基本面分析师 | get_fundamentals(ticker), get_balance_sheet, get_income_statement, get_cashflow |
| 政策分析师 | get_news, get_global_news |
| 游资追踪师 | get_stock_data, get_dragon_tiger_board(ticker, date), get_fund_flow(ticker, date) |
| 解禁监控师 | get_lockup_expiry(ticker, date), get_insider_transactions, get_news |

## 完整工具清单

从 `tradingagents.dataflows.a_stock` 导入：

```python
get_stock_data(ticker, start_date, end_date)      # K线，mootdx/腾讯
get_indicators(symbol, indicator, curr_date, look_back_days)  # 技术指标
get_fundamentals(ticker)                           # PE/PB/ROE
get_balance_sheet(ticker)                          # 资产负债表
get_income_statement(ticker)                       # 利润表
get_cashflow(ticker)                               # 现金流量表
get_news(ticker, start_date, end_date)             # 个股新闻
get_global_news(limit=10)                          # 宏观快讯
get_insider_transactions(ticker)                   # insider交易
get_profit_forecast(ticker)                        # EPS一致预期
get_hot_stocks()                                   # 热门股票
get_northbound_flow(curr_date)                     # 北向资金
get_concept_blocks(ticker)                         # 概念板块
get_fund_flow(ticker, curr_date)                   # 资金流向
get_dragon_tiger_board(ticker, trade_date)         # 龙虎榜
get_lockup_expiry(ticker, trade_date)              # 解禁日历
get_industry_comparison(ticker, trade_date)        # 行业对比
```

**东财防封**：设置 `EM_MIN_INTERVAL=1.5` 环境变量。

## 六维评分矩阵

| 维度 | 权重 | 核心考量 |
|------|------|----------|
| 基本面 | 30% | 周期拐点、PE/PB、PEG、盈利预期离散度 |
| 技术面 | 25% | 均线排列、MACD、RSI、K线形态、量价关系 |
| 资金面 | 20% | 主力流向、超大单占比、北向资金、龙虎榜 |
| 消息面 | 10% | 高管增持、回购、公告、新闻事件 |
| 政策面 | 8% | 监管政策、产业政策、消费刺激 |
| 风险面 | 7% | ATR波动率、解禁压力、预测分歧、获利盘 |

## 信号与仓位

| 综合评分 | 信号 | 仓位 |
|----------|------|------|
| >= 75 | BUY | 60-80% |
| 65-74 | HOLD | 40-60% |
| 55-64 | HOLD | 20-40% |
| 40-54 | SELL | 0-20% |
| < 40 | SELL | 清仓 |

## 交易方案要素

- 止损位：今日低点 - ATR（或-10%最大回撤）
- 止盈位1：SMA50 或近期技术压力位
- 止盈位2：年初高点50%回撤位
- 移动止盈：盈利15%后回撤8%止盈
- 单股仓位上限 ≤ 总资产50%
- 行业仓位上限 ≤ 总资产60%

## 用户介入指令

在任意节点用户可发出：继续/深入分析/跳过/重跑/对比另一只/追问/换个模型/终止/回到上一步

## 输出语言

所有输出使用中文。分析师报告用表格，多空辩论用评分矩阵，最终决策用四要素（信号+仓位+信心度+评分）。

## 免责声明

本项目仅供学习研究与技术演示，不构成任何投资建议。
