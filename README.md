# Super TradingAgents CN — A股智能投研助手

[![GitHub](https://img.shields.io/badge/GitHub-hutuboy/super--tradingagents--cn--skill-blue)](https://github.com/hutuboy/super-tradingagents-cn-skill)
[![PyPI](https://img.shields.io/badge/PyPI-super--tradingagents--cn--skill-green)](https://pypi.org/project/super-tradingagents-cn-skill)

A股多Agent投研分析框架，集成 **7 分析师 → 多空辩论 → 综合研判 → 交易方案 → 风控辩论 → 最终决策** 的完整决策链路。全部数据源免费直连，无需 API Key。

## 安装

```bash
pip install super-tradingagents-cn-skill
```

依赖会自动安装 [tradingagents-astock](https://github.com/simonlin1212/TradingAgents-astock)（A股数据源与核心框架）。

## CLI 快速使用

```bash
# 快速分析一只股票（轻量模式，无需 LLM Key）
stcs analyze 002714

# 深入分析
stcs analyze 600519 --deep

# 将 SKILL 安装到当前项目（支持 TRAE/Cursor/Claude/Cline/Windsurf）
stcs skill install --platform all

# 列出支持的平台
stcs skill list

# 启动 Web UI
stcs web
```

## Python API

```python
from super_tradingagents_cn_skill import quick_analyze

result = quick_analyze("002714", deep=True)
print(result["signal"])      # HOLD
print(result["position"])    # 40-60%
print(result["avg_score"])   # 69.9
print(result["report"])      # Markdown 格式完整报告
```

## 多平台适配

本 SKILL 已适配以下主流 AI 编程助手/IDE，选择适合你的平台：

| 平台 | 文件 | 放置位置 | 说明 |
|------|------|----------|------|
| **TRAE / Claude** | `SKILL.md` | `.trae/skills/super-tradingagents-cn-skill/SKILL.md` | 原始 SKILL 格式，含 frontmatter |
| **Cursor** | `.cursorrules` | 项目根目录 `/.cursorrules` | Cursor IDE Project Rules |
| **Claude Code** | `CLAUDE.md` | 项目根目录 `/CLAUDE.md` | Claude Code 项目级指令 |
| **Cline** | `.clinerules` | 项目根目录 `/.clinerules` | VS Code Cline 扩展规则 |
| **Windsurf** | `.windsurfrules` | 项目根目录 `/.windsurfrules` | Windsurf IDE 规则 |
| **通用** | `README.md` | 项目根目录 `/README.md` | 通用说明文档 |

> 将对应文件复制到你的 A股分析项目根目录即可生效。

## 项目概述

基于 [TradingAgents-Astock](https://github.com/simonlin1212/TradingAgents-astock) 深度特化的 A 股多 Agent 投研框架。

**双模式运行：**
- **完整模式**（有 LLM Key）：7 分析师由 LLM 驱动，生成深度研报
- **轻量模式**（无 LLM Key）：用规则引擎 + 数据驱动模拟多空辩论与决策

**双 LLM 设计**（完整模式）：
- `deep_think_llm`：Research Manager + Portfolio Manager（全局综合决策）
- `quick_think_llm`：7 个 Analyst + Researcher + Trader + Risk Debater（快速推理）

---

## LOOP ENGINEERING 架构

采用 **LOOP ENGINEERING（循环工程）** 思想，将一次性线性 pipeline 重构为三层持续运行的交互式闭环系统。

### 三层循环模型

```
┌─────────────────────────────────────────────────────────────┐
│                    外层循环：用户对话循环                        │
│  感知用户输入 → 解析意图 → 路由到对应中层循环 → 等待反馈         │
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
IDLE → INTENT → DATA → ANALYST_LOOP → DEBATE_LOOP → RISK_LOOP → DECISION → REPORT → MEMORY
```

用户在任意节点可发出：继续 / 深入分析 / 跳过 / 重跑 / 对比另一只 / 追问 / 换个模型 / 终止 / 回到上一步

---

## 快速触发（一句话启动）

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

从 `tradingagents.dataflows.a_stock` 导入：

| 工具函数 | 参数 | 功能 | 数据源 |
|----------|------|------|--------|
| `get_stock_data(ticker, start_date, end_date)` | 代码, 起始日, 结束日 | K线/OHLCV/实时行情 | mootdx / 腾讯 |
| `get_indicators(symbol, indicator, curr_date, look_back_days)` | 代码, 指标名, 日期, 回看天数 | MACD/RSI/布林/均线等 | stockstats |
| `get_fundamentals(ticker)` | 代码 | 财务快照/PE/PB/ROE | mootdx / 腾讯 |
| `get_balance_sheet(ticker)` | 代码 | 资产负债表 | 新浪财经 |
| `get_income_statement(ticker)` | 代码 | 利润表 | 新浪财经 |
| `get_cashflow(ticker)` | 代码 | 现金流量表 | 新浪财经 |
| `get_news(ticker, start_date, end_date)` | 代码, 起始日, 结束日 | 个股/板块新闻 | 东方财富 / 财联社 |
| `get_global_news(limit=10)` | 条数 | 全球宏观财经快讯 | 财联社 |
| `get_insider_transactions(ticker)` | 代码 | insider 交易/大宗交易 | 东方财富 |
| `get_profit_forecast(ticker)` | 代码 | EPS一致预期 | 同花顺 |
| `get_hot_stocks()` | 无 | 热门股票/涨幅榜 | 东方财富 |
| `get_northbound_flow(curr_date)` | 日期 | 北向资金流向 | 东方财富 |
| `get_concept_blocks(ticker)` | 代码 | 概念板块分类 | 百度股市通 |
| `get_fund_flow(ticker, curr_date)` | 代码, 日期 | 个股/板块资金流向 | 东方财富 |
| `get_dragon_tiger_board(ticker, trade_date)` | 代码, 日期 | 龙虎榜数据 | 东方财富 |
| `get_lockup_expiry(ticker, trade_date)` | 代码, 日期 | 限售解禁日历 | 东方财富 |
| `get_industry_comparison(ticker, trade_date)` | 代码, 日期 | 行业对比数据 | 东方财富 |

**东财防封提示**：批量分析时设置环境变量 `EM_MIN_INTERVAL=1.5` 降低请求频率。

### 补充数据源（mx-skills-suite）

当配置了 `MX_APIKEY` 环境变量时，可调用东方财富妙想 API 作为补充。

---

## 决策链路架构

```
┌──────────────────────────────────────────────┐
│  7 Analyst 研报生成（可 selective 启用）          │
│  Market → Social → News → Fundamentals        │
│  → Policy → Hot Money → Lockup                │
├──────────────────────────────────────────────┤
│  Bull vs Bear 投研辩论（max_debate_rounds 轮）  │
├──────────────────────────────────────────────┤
│  Research Manager 综合研判                      │
│  → 输出 Investment Plan                       │
├──────────────────────────────────────────────┤
│  Trader 交易方案（A股约束：T+1/涨跌停/手数）     │
├──────────────────────────────────────────────┤
│  Aggressive ←→ Conservative ←→ Neutral        │
│  三方风险辩论（max_risk_discuss_rounds 轮）     │
├──────────────────────────────────────────────┤
│  Portfolio Manager 最终决策                     │
│  → 输出 Signal: Buy / Hold / Sell + 仓位建议   │
└──────────────────────────────────────────────┘
```

---

## 无 LLM Key 轻量模式

当 `.env` 中未配置任何 LLM API Key 时，自动切换为轻量模式：

1. **数据采集**：TradingAgents 免费工具 + mx-skills-suite
2. **分析师报告**：基于规则引擎生成结构化数据报告（非 LLM 驱动）
3. **多空辩论**：用评分矩阵模拟 Bull vs Bear 观点交锋
4. **综合研判**：基于加权评分模型输出时序判断（短/中/长期）
5. **交易方案**：基于 A 股约束生成分批建仓/止损/止盈策略
6. **最终决策**：六维评分矩阵 → Signal + 仓位 + 信心度

---

## 六维评分矩阵

| 维度 | 得分 | 权重 | 核心考量 |
|------|------|------|----------|
| **基本面** | 0-100 | 30% | 周期拐点、PE/PB、PEG、盈利预期离散度 |
| **技术面** | 0-100 | 25% | 均线排列、MACD、RSI、K线形态、量价 |
| **资金面** | 0-100 | 20% | 主力流向、超大单占比、北向资金、龙虎榜 |
| **消息面** | 0-100 | 10% | 高管增持、回购、公告、新闻事件 |
| **政策面** | 0-100 | 8% | 监管政策、产业政策、消费刺激 |
| **风险面** | 0-100 | 7% | ATR波动率、解禁压力、预测分歧、获利盘 |

### 信号判断

| 综合评分 | 信号 | 建议仓位 |
|----------|------|----------|
| >= 75 | **BUY** | 60-80% |
| 65-74 | **HOLD** | 40-60% |
| 55-64 | **HOLD** | 20-40% |
| 40-54 | **SELL** | 0-20% |
| < 40 | **SELL** | 清仓 |

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

## 安装依赖

```bash
pip install tradingagents-astock
```

或从源码安装：

```bash
git clone https://github.com/simonlin1212/TradingAgents-astock.git
cd TradingAgents-astock
pip install -e . --no-build-isolation
```

---

## 文件清单

| 文件 | 用途 | 目标平台 |
|------|------|----------|
| `SKILL.md` | TRAE/Claude SKILL 格式 | TRAE Work CN / Claude |
| `.cursorrules` | Cursor Project Rules | Cursor IDE |
| `CLAUDE.md` | Claude Code 项目指令 | Claude Code CLI |
| `.clinerules` | Cline 扩展规则 | VS Code + Cline |
| `.windsurfrules` | Windsurf 项目规则 | Windsurf IDE |
| `README.md` | 通用说明文档 | 所有平台 |

---

## 免责声明

**本项目仅供学习研究与技术演示，不构成任何投资建议。**

- 所有分析结果、评分、信号和交易方案均基于公开数据通过规则引擎或 LLM 生成，不保证准确性和完整性
- A 股市场具有高度波动性，历史数据不代表未来表现
- 投资决策请咨询持牌专业机构，作者不对因使用本项目而产生的任何投资损失承担责任
- 本项目中的数据工具仅调用公开 API，不获取、不存储任何非公开或内幕信息
- 使用本项目即表示您已理解并接受上述风险声明

---

## 致谢

本 SKILL 基于以下开源项目进行适配与改造：

- **[TradingAgents-Astock](https://github.com/simonlin1212/TradingAgents-astock)** — A 股深度特化的多 Agent 投研框架，由 simonlin1212 开发并维护。本 SKILL 的核心数据源工具、7 分析师角色定义和决策链路架构均源自该项目。
- **[TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents)** — 原版 TradingAgents 多 Agent LLM 金融交易框架，为本项目提供了基础架构和开源精神。

感谢原作者的出色工作和 Apache 2.0 开源许可。

原始论文：*TradingAgents: Multi-Agents LLM Financial Trading Framework*

---

## 许可证

**Apache License 2.0**

本项目是 [TradingAgents-Astock](https://github.com/simonlin1212/TradingAgents-astock) 的衍生 SKILL，继承 Apache 2.0 许可证。详见 [LICENSE](LICENSE) 文件。

```
Copyright 2026 hutuboy

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
