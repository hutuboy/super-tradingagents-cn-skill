---
name: "super-tradingagents-cn-skill"
description: "A股多Agent投研分析Skill，集成7分析师、多空辩论、风控评估与交易决策，适配TRAE Work CN对话式交互。支持有/无LLM Key两种模式运行，数据源覆盖mootdx/东财/腾讯/新浪/同花顺。当用户需要进行A股个股深度分析、投研报告生成或交互式诊断时调用。"
---

# Super TradingAgents CN — A股智能投研助手

## 项目概述

基于 TradingAgents-Astock 深度特化的 A 股多 Agent 投研框架，采用 **7 分析师 → 多空辩论 → Research Manager → Trader → 三方风险辩论 → Portfolio Manager** 的完整决策链路。全部数据源免费直连（mootdx/东财/腾讯/新浪/同花顺），无需 API Key。

**双模式运行：**
- **完整模式**（有 LLM Key）：7 分析师由 LLM 驱动，生成深度研报
- **轻量模式**（无 LLM Key）：用规则引擎 + 数据驱动模拟多空辩论与决策，输出结构化投研报告

**双 LLM 设计**（完整模式）：
- `deep_think_llm`：Research Manager + Portfolio Manager（全局综合决策）
- `quick_think_llm`：7 个 Analyst + Researcher + Trader + Risk Debater（快速推理）

---

## LOOP ENGINEERING 架构（TRAE Work CN 适配版）

本 Skill 采用 **LOOP ENGINEERING（循环工程）** 思想改造原有一次性线性 pipeline，将其重构为三层持续运行的交互式闭环系统，适配 TRAE Work CN 对话式人机协作。

### 核心思想

> 别再只盯着单次 prompt 运行完整 pipeline，而要设计一套能持续运行、允许用户在每个节点介入的闭环系统。

### 三层循环模型

```
┌─────────────────────────────────────────────────────────────┐
│                    外层循环：用户对话循环                        │
│  感知用户输入 → 解析意图 → 路由到对应中层循环 → 等待反馈         │
│  （支持打断、追问、切换目标、多股同时跟踪）                       │
├─────────────────────────────────────────────────────────────┤
│                    中层循环：分析师轮询循环                      │
│  Market → Social → News → Fundamentals → Policy →            │
│  Hot Money → Lockup                                          │
│  （每轮执行完给用户展示结果，用户选择：深入/跳过/重跑/终止）      │
├─────────────────────────────────────────────────────────────┤
│                    内层循环：工具调用循环                        │
│  Thought → Action（调工具）→ Observation → 下一轮 Thought      │
│  （ReAct 模式，工具失败自动重试/切换数据源）                     │
└─────────────────────────────────────────────────────────────┘
```

### 交互状态机

```
                    ┌─────────────┐
         ┌─────────│    IDLE     │←────────┐
         │         └──────┬──────┘         │
         │                │ 用户输入        │
         │                ▼                │
         │         ┌─────────────┐         │
         │         │   INTENT    │         │
         │         │ 意图解析     │         │
         │         └──────┬──────┘         │
         │                │                │
         │                ▼                │
         │         ┌─────────────┐         │
         │         │    DATA     │         │
         │         │ 数据收集     │         │
         │         └──────┬──────┘         │
         │                │                │
         │     ┌──────────┼──────────┐     │
         │     │          │          │     │
         │     ▼          ▼          ▼     │
         │  ┌──────┐  ┌──────┐  ┌──────┐  │
         │  │专项  │  │完整  │  │对比  │  │
         │  │分析  │  │pipeline│ │分析  │  │
         │  └──┬───┘  └──┬───┘  └──┬───┘  │
         │     │         │         │      │
         │     └─────────┼─────────┘      │
         │               ▼                │
         │      ┌─────────────────┐       │
         │      │   ANALYST_LOOP  │       │
         │      │  分析师轮询(7轮) │       │
         │      │  每轮用户可介入  │       │
         │      └────────┬────────┘       │
         │               │                │
         │               ▼                │
         │      ┌─────────────────┐       │
         │      │   DEBATE_LOOP   │       │
         │      │  多空辩论循环    │       │
         │      │  用户可调轮数    │       │
         │      └────────┬────────┘       │
         │               │                │
         │               ▼                │
         │      ┌─────────────────┐       │
         │      │   RISK_LOOP     │       │
         │      │  风控辩论循环    │       │
         │      │  三方风险辩论    │       │
         │      └────────┬────────┘       │
         │               │                │
         │               ▼                │
         │      ┌─────────────────┐       │
         │      │    DECISION     │       │
         │      │  Portfolio决策   │       │
         │      │  Buy/Hold/Sell   │       │
         │      └────────┬────────┘       │
         │               │                │
         │               ▼                │
         │      ┌─────────────────┐       │
         │      │     REPORT      │       │
         │      │  报告输出/导出   │       │
         │      └────────┬────────┘       │
         │               │                │
         │               ▼                │
         │      ┌─────────────────┐       │
         │      │     MEMORY      │       │
         │      │  交易记忆/反思   │       │
         │      └─────────────────┘       │
         │                                │
         └────────────────────────────────┘
```

### 每个节点的用户介入操作

在循环的任意节点，用户都可发出以下指令：

| 指令 | 效果 |
|------|------|
| **"继续"** / 直接回车 | 进入下一阶段 |
| **"深入分析一下"** | 当前步骤增加更多数据/工具/轮数 |
| **"跳过"** | 直接进入下一阶段 |
| **"重跑"** | 用不同模型/参数重新执行当前步骤 |
| **"对比另一只"** | 引入第二只股票并行分析 |
| **"为什么"** / **"详细说说"** | 对当前结果追问，进入子循环 |
| **"换个模型"** | 切换 LLM 供应商重新分析 |
| **"终止"** | 结束分析，输出当前已有结果 |
| **"回到上一步"** | 回退到上一状态重新分析 |

### 上下文保持机制

- **ConversationContext**：整个对话中的分析结果、用户选择、中间结论全部保存在会话上下文中
- **用户可随时追问**："刚才那个 MACD 什么意思"、"重新看一下基本面"、"对比一下昨天的结论"
- **跨会话记忆**：TradingMemoryLog 自动持久化，支持"回顾一下上周分析的宁德时代"

---

## TRAE Work CN 交互方式

### 第一层：快速触发（一句话启动）

| 用户说 | AI 执行 |
|--------|---------|
| "分析一下 600519" | 识别代码 → 收集数据 → 进入分析师轮询循环 |
| "看看宁德时代怎么样" | 名称→代码映射 → 启动完整 pipeline |
| "帮我诊断贵州茅台" | 同义词识别 → 运行 7 分析师循环 |
| "对比一下比亚迪和宁德时代" | 双股并行 → 综合对比报告 |
| "这个股的龙虎榜数据" | 直接进入游资追踪模块（专项分析） |
| "有什么解禁风险" | 直接进入解禁监控模块（专项分析） |
| "回顾一下昨天的分析" | 查询 TradingMemoryLog → 反思对比 |
| "启动 Web UI" | 启动 Streamlit → 给出访问地址 |

### 第二层：循环介入（分析师轮询阶段）

当 AI 完成每个分析师的报告后，会主动询问用户：

```
[市场分析师报告完成]
├─ 技术面：MACD 死叉，KDJ 超卖，布林下轨...
├─ 量价：今日放量下跌，主力资金净流出 13 亿...
└─ 关键信号：短期趋势偏弱

请选择下一步：
[1] 深入分析 → 增加更多技术指标/更长周期 K 线
[2] 继续 → 进入舆情分析师
[3] 跳过 → 直接进入多空辩论
[4] 重跑 → 换用 DeepSeek 重新分析技术面
[5] 对比 → 同时看一下比亚迪的技术面
[6] 追问 → "MACD 死叉意味着什么？"
```

### 第三层：子循环追问（深度交互）

用户在任意阶段可发起追问，AI 进入子循环深度解答：

```
用户："刚才说 PEG 0.78 是什么意思？"
AI："PEG = PE / 利润增长率。宁德时代当前 PE 22.5x，
     分析师一致预期未来 3 年利润 CAGR 约 24%，
     所以 PEG = 22.5 / 24 ≈ 0.94。一般来说 PEG < 1
     表示估值相对成长性偏低..."
     
用户："那和比亚迪比呢？"
AI：[进入对比子循环，调用 get_fundamentals('002594')...]
```

### 执行流程（循环式）

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph

# 初始化引擎（自动读取 .env 配置）
config = {
    "llm_provider": "minimax",
    "deep_think_llm": "MiniMax-M2.7",
    "quick_think_llm": "MiniMax-M2.7-highspeed",
    "output_language": "Chinese",
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
}

ta = TradingAgentsGraph(debug=True, config=config)

# 外层循环：用户输入
ticker = "300750"  # 从用户对话中解析
date = "2026-07-01"

# 中层循环：分析师轮询（每步可介入）
for analyst in ["market", "social", "news", "fundamentals", 
                "policy", "hot_money", "lockup"]:
    report = ta.run_analyst(analyst, ticker, date)
    # 展示报告 → 等待用户选择（深入/跳过/重跑/终止）
    # 用户选择后决定下一步

# 中层循环：多空辩论
debate = ta.run_debate(ticker, date)
# 展示辩论结果 → 用户可调轮数

# 中层循环：风控评估
risk = ta.run_risk_assessment(ticker, date)
# 展示风控结果 → 用户可调整参数

# 最终决策
decision = ta.final_decision(ticker, date)
# decision 包含: Signal(Buy/Hold/Sell)、仓位建议、完整报告
```

### 无 LLM Key 轻量模式

当 `.env` 中未配置任何 LLM API Key 时，自动切换为轻量模式：

```
1. 数据采集：TradingAgents 免费工具 + mx-skills-suite（东方财富API）
2. 分析师报告：基于规则引擎生成结构化数据报告（非 LLM 驱动）
3. 多空辩论：用评分矩阵模拟 Bull vs Bear 观点交锋
4. 综合研判：基于加权评分模型输出时序判断（短/中/长期）
5. 交易方案：基于 A 股约束生成分批建仓/止损/止盈策略
6. 最终决策：六维评分矩阵 → Signal + 仓位 + 信心度
```

轻量模式同样支持 LOOP ENGINEERING 的三层循环交互，仅分析师报告的生成方式不同（数据驱动 vs LLM 驱动）。

### 专项分析（快速通道）

用户也可直接指定只跑 pipeline 中的某一段：

| 用户指令 | 执行模块 | 数据工具 |
|----------|----------|----------|
| "看一下技术面" | Market Analyst | `get_stock_data` + `get_indicators` |
| "基本面怎么样" | Fundamentals Analyst | `get_fundamentals` + 三表 |
| "资金流向如何" | Hot Money Tracker | `get_fund_flow` + `get_dragon_tiger_board` |
| "有什么新闻" | News + Social Analyst | `get_news` + `get_global_news` |
| "政策面有影响吗" | Policy Analyst | `get_news` + `get_global_news` |
| "解禁压力大吗" | Lockup Watcher | `get_lockup_expiry` + `get_insider_transactions` |

### 高级配置（对话中动态调整）

| 用户说 | AI 动作 |
|--------|---------|
| "用 DeepSeek 来分析" | 切换 `llm_provider` 为 deepseek，重跑当前步骤 |
| "多辩论两轮" | 增加 `max_debate_rounds`，重跑辩论阶段 |
| "用英文输出" | 切换 `output_language` 为 English，重跑报告阶段 |
| "不需要舆情和游资" | 跳过 Social Analyst 和 Hot Money Tracker |
| "启用断点续跑" | 设置 `checkpoint_enabled=True`，支持中断恢复 |
| "对比一下 002594" | 并行启动第二只股票的 pipeline，输出对比表格 |

---

## 7 个分析师角色

| 角色 | 职责 | 核心数据工具 |
|------|------|-------------|
| **市场分析师** | K线形态、技术指标、量价分析 | `get_stock_data`, `get_indicators` |
| **舆情分析师** | 社交媒体情绪、散户讨论热度 | `get_news` |
| **新闻分析师** | 行业新闻、公告、宏观事件 | `get_news`, `get_global_news`, `get_insider_transactions` |
| **基本面分析师** | 财报三表、盈利能力、估值 | `get_fundamentals`, `get_balance_sheet`, `get_cashflow`, `get_income_statement` |
| **政策分析师** | 监管政策、产业政策、窗口指导 | `get_news`, `get_global_news` |
| **游资追踪师** | 龙虎榜、大单流向、主力资金动态 | `get_stock_data`, `get_dragon_tiger_board`, `get_fund_flow` |
| **解禁监控师** | 限售股解禁、大股东减持、股权质押 | `get_lockup_expiry`, `get_insider_transactions`, `get_news` |

---

## 数据源工具清单（全部免费，无需 Key）

从 `tradingagents.dataflows.a_stock` 导入（无 LLM 轻量模式）或 `tradingagents.agents.utils.agent_utils` 导入（完整 LLM 模式）：

### 核心数据工具

| 工具函数 | 参数 | 功能 | 数据源 |
|----------|------|------|--------|
| `get_stock_data(ticker, start_date, end_date)` | 代码, 起始日, 结束日 | K线/OHLCV/实时行情 | mootdx / 腾讯 |
| `get_indicators(ticker)` | 代码 | 技术指标（MACD/RSI/KDJ/布林等） | stockstats |
| `get_fundamentals(ticker)` | 代码 | 财务快照/PE/PB/ROE | mootdx / 腾讯 |
| `get_balance_sheet(ticker)` | 代码 | 资产负债表 | 新浪财经 |
| `get_income_statement(ticker)` | 代码 | 利润表 | 新浪财经 |
| `get_cashflow(ticker)` | 代码 | 现金流量表 | 新浪财经 |
| `get_news(ticker, start_date, end_date)` | 代码, 起始日, 结束日 | 个股/板块新闻 | 东方财富 / 财联社 |
| `get_global_news(limit=10)` | 条数 | 全球宏观财经快讯 | 财联社 |
| `get_insider_transactions(ticker)` | 代码 | insider 交易/大宗交易 | 东方财富 |
| `get_profit_forecast(ticker)` | 代码 | EPS一致预期 | 同花顺 |
| `get_hot_stocks()` | 无 | 热门股票/涨幅榜 | 东方财富 |
| `get_northbound_flow()` | 无 | 北向资金流向 | 东方财富 |
| `get_concept_blocks(ticker)` | 代码 | 概念板块分类 | 百度股市通 |
| `get_fund_flow(ticker, curr_date)` | 代码, 日期 | 个股/板块资金流向 | 东方财富 |
| `get_dragon_tiger_board(ticker)` | 代码 | 龙虎榜数据 | 东方财富 |
| `get_lockup_expiry(ticker, trade_date)` | 代码, 日期 | 限售解禁日历 | 东方财富 |
| `get_industry_comparison(ticker)` | 代码 | 行业对比数据 | 东方财富 |

### 补充数据源（mx-skills-suite）

当配置了 `MX_APIKEY` 环境变量时，可调用东方财富妙想 API 作为补充：

| 数据源 | 内容 | 配置方式 |
|--------|------|---------|
| 东方财富妙想API | 行情快照、主力资金、估值、财务指标 | `MX_APIKEY` 环境变量 |
| 东方财富妙想搜索 | 新闻、公告、研报、政策 | `MX_APIKEY` 环境变量 |

**东财防封提示**：批量分析时设置环境变量 `EM_MIN_INTERVAL=1.5` 降低请求频率。

---

## 决策链路架构

```
┌──────────────────────────────────────────────┐
│  7 Analyst 研报生成（可 selective 启用）          │
│  Market → Social → News → Fundamentals        │
│  → Policy → Hot Money → Lockup                │
│  （每个 Analyst 带工具循环，Quality Gate 质检）   │
├──────────────────────────────────────────────┤
│  Bull vs Bear 投研辩论（max_debate_rounds 轮）  │
├──────────────────────────────────────────────┤
│  Research Manager 综合研判（deep_think_llm）    │
│  → 输出 Investment Plan                       │
├──────────────────────────────────────────────┤
│  Trader 交易方案（A股约束：T+1/涨跌停/手数）     │
├──────────────────────────────────────────────┤
│  Aggressive ←→ Conservative ←→ Neutral        │
│  三方风险辩论（max_risk_discuss_rounds 轮）     │
├──────────────────────────────────────────────┤
│  Portfolio Manager 最终决策（deep_think_llm）   │
│  → 输出 Signal: Buy / Hold / Sell + 仓位建议   │
└──────────────────────────────────────────────┘
```

---

## 交易记忆与反思

- **TradingMemoryLog**：自动记录每次分析的最终决策、理由和时间戳
- **Reflector**：以沪深 300（CSI 300）为基准，对历史决策进行回顾性反思
- 记忆文件默认保存在 `~/.tradingagents/memory/trading_memory.md`

---

## 常见问题速查

| 问题 | 解决方案 |
|------|----------|
| 报 `OPENAI_API_KEY` 错误但用的是 DeepSeek/通义/智谱 | 每个供应商用各自的环境变量名：`DEEPSEEK_API_KEY` / `DASHSCOPE_API_KEY` / `ZHIPU_API_KEY` |
| 部分分析师报告空白 | 所选模型 tool-call 能力弱，换用 `deepseek-chat` / `qwen` / `GLM-4` / `Claude` |
| 无 LLM Key 能否运行 | **可以！** 自动切换轻量模式，用规则引擎模拟多空辩论与决策 |
| 东方财富 API 返回空值 | 检查 `MX_APIKEY` 是否配置；东方财富妙想 API 端点可能需要根据最新文档调整 |
| PDF 导出报 `UnicodeEncodeError` | `pip uninstall -y fpdf && pip install "fpdf2>=2.8.0"` |
| Docker 里 PDF 中文乱码 | Dockerfile 已内置 `fonts-noto-cjk`，重新 build 镜像 |
| 东财批量请求被封 IP | 设置 `EM_MIN_INTERVAL=1.5` 环境变量降速 |
| Web UI 启动后打不开 | 确认服务已启动：`python -m streamlit run web/app.py`，访问 `http://localhost:8501` |

---

## 免责声明

本项目仅供学习研究与技术演示，不构成任何投资建议。投资决策请咨询持牌专业机构。
