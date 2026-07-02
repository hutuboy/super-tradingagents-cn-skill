"""快速分析 — 轻量模式（无LLM Key，规则引擎驱动）"""
import json
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd


def quick_analyze(ticker: str, date: Optional[str] = None, deep: bool = False) -> dict:
    """
    快速分析一只股票（轻量模式）

    Args:
        ticker: A股6位代码
        date: 分析日期，默认今天
        deep: 是否启用深入分析

    Returns:
        dict 包含 report、signal、position、confidence、avg_score、scores
    """
    from tradingagents.dataflows.a_stock import (
        get_stock_data, get_indicators, get_fundamentals,
        get_fund_flow, get_news, get_lockup_expiry,
        get_dragon_tiger_board, get_insider_transactions,
        get_profit_forecast, get_northbound_flow,
        get_industry_comparison, get_concept_blocks,
    )

    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    start = (datetime.strptime(date, "%Y-%m-%d") - timedelta(days=60)).strftime("%Y-%m-%d")
    start_deep = (datetime.strptime(date, "%Y-%m-%d") - timedelta(days=120)).strftime("%Y-%m-%d")

    # ===== 1. 数据采集 =====
    data = {"ticker": ticker, "date": date}

    # K线
    try:
        kline = get_stock_data(ticker, start, date)
        data["kline"] = kline[:1500] if isinstance(kline, str) else "NO_DATA"
    except Exception as e:
        data["kline"] = f"ERROR: {e}"

    # 技术指标
    try:
        macd = get_indicators(ticker, "macd", date, 60)
        data["macd"] = macd[:1000] if isinstance(macd, str) else "NO_DATA"
    except Exception:
        data["macd"] = "NO_DATA"

    try:
        rsi = get_indicators(ticker, "rsi", date, 60)
        data["rsi"] = rsi[:800] if isinstance(rsi, str) else "NO_DATA"
    except Exception:
        data["rsi"] = "NO_DATA"

    # 基本面
    try:
        fund = get_fundamentals(ticker)
        data["fundamentals"] = fund[:2000] if isinstance(fund, str) else "NO_DATA"
    except Exception as e:
        data["fundamentals"] = f"ERROR: {e}"

    # 资金流向
    try:
        ff = get_fund_flow(ticker, date)
        data["fund_flow"] = ff[:1500] if isinstance(ff, str) else "NO_DATA"
    except Exception:
        data["fund_flow"] = "NO_DATA"

    # 新闻
    try:
        news = get_news(ticker, start, date)
        data["news"] = news[:1500] if isinstance(news, str) else "NO_DATA"
    except Exception:
        data["news"] = "NO_DATA"

    # 解禁
    try:
        lock = get_lockup_expiry(ticker, date)
        data["lockup"] = lock[:1000] if isinstance(lock, str) else "NO_DATA"
    except Exception:
        data["lockup"] = "NO_DATA"

    # 龙虎榜
    try:
        dtb = get_dragon_tiger_board(ticker, date)
        data["dragon_tiger"] = dtb[:1000] if isinstance(dtb, str) else "NO_DATA"
    except Exception:
        data["dragon_tiger"] = "NO_DATA"

    # 盈利预测
    try:
        pf = get_profit_forecast(ticker)
        data["profit_forecast"] = pf[:1500] if isinstance(pf, str) else "NO_DATA"
    except Exception:
        data["profit_forecast"] = "NO_DATA"

    # 北向资金
    try:
        nf = get_northbound_flow(date)
        data["northbound"] = nf[:1000] if isinstance(nf, str) else "NO_DATA"
    except Exception:
        data["northbound"] = "NO_DATA"

    # 深入分析
    if deep:
        try:
            sma50 = get_indicators(ticker, "close_50_sma", date, 120)
            data["sma50"] = sma50[:1000] if isinstance(sma50, str) else "NO_DATA"
        except Exception:
            data["sma50"] = "NO_DATA"

        try:
            atr = get_indicators(ticker, "atr", date, 60)
            data["atr"] = atr[:800] if isinstance(atr, str) else "NO_DATA"
        except Exception:
            data["atr"] = "NO_DATA"

    # ===== 2. 规则引擎评分 =====
    scores = _rule_engine_scoring(data, deep)
    avg_score = round(
        scores["fundamental"] * 0.30 +
        scores["technical"] * 0.25 +
        scores["capital"] * 0.20 +
        scores["news"] * 0.10 +
        scores["policy"] * 0.08 +
        scores["risk"] * 0.07,
        1,
    )

    # ===== 3. 多空辩论 =====
    bull_score, bear_score = _debate(data, scores)

    # ===== 4. 信号判断 =====
    if avg_score >= 75:
        signal, position, confidence = "BUY", "60-80%", "高"
    elif avg_score >= 65:
        signal, position, confidence = "HOLD", "40-60%", "中高"
    elif avg_score >= 55:
        signal, position, confidence = "HOLD", "20-40%", "中高"
    elif avg_score >= 40:
        signal, position, confidence = "SELL", "0-20%", "中"
    else:
        signal, position, confidence = "SELL", "清仓", "低"

    # ===== 5. 生成报告 =====
    report = _generate_report(data, scores, avg_score, signal, position, confidence, bull_score, bear_score)

    return {
        "ticker": ticker,
        "date": date,
        "signal": signal,
        "position": position,
        "confidence": confidence,
        "avg_score": avg_score,
        "scores": scores,
        "bull_score": bull_score,
        "bear_score": bear_score,
        "data": data,
        "report": report,
        "bull_bear_ratio": f"{bull_score}:{bear_score}",
    }


def _rule_engine_scoring(data: dict, deep: bool) -> dict:
    """基于规则引擎的六维评分"""
    scores = {
        "fundamental": 50,
        "technical": 50,
        "capital": 50,
        "news": 50,
        "policy": 50,
        "risk": 50,
    }

    # 基本面：从 fundamentals 文本中提取PE/PB信息
    fund = data.get("fundamentals", "")
    if "PE" in fund or "pe" in fund.lower():
        scores["fundamental"] = 65
    if deep and "EPS" in fund:
        scores["fundamental"] = min(85, scores["fundamental"] + 10)

    # 技术面：MACD + RSI
    macd = data.get("macd", "")
    if "macd" in macd.lower() and ("金叉" in macd or "positive" in macd.lower()):
        scores["technical"] = 70
    elif "macd" in macd.lower() and ("死叉" in macd or "negative" in macd.lower()):
        scores["technical"] = 35

    rsi = data.get("rsi", "")
    if "rsi" in rsi.lower():
        try:
            rsi_val = float(rsi.split()[-1]) if rsi.split() else 50
            if rsi_val > 70:
                scores["technical"] -= 10
            elif rsi_val < 30:
                scores["technical"] += 10
        except (ValueError, IndexError):
            pass

    # 资金面
    ff = data.get("fund_flow", "")
    if "净流入" in ff or "inflow" in ff.lower():
        scores["capital"] = 75
    elif "净流出" in ff or "outflow" in ff.lower():
        scores["capital"] = 40

    # 消息面
    news = data.get("news", "")
    if "增持" in news or "回购" in news or "利好" in news:
        scores["news"] = 80
    elif "减持" in news or "利空" in news:
        scores["news"] = 35

    # 政策面（从新闻中推断）
    if "政策" in news or "监管" in news:
        scores["policy"] = 65

    # 风险面
    lock = data.get("lockup", "")
    if "解禁" in lock and "无" not in lock:
        scores["risk"] = 40
    else:
        scores["risk"] = 55

    # 确保在0-100范围内
    for k in scores:
        scores[k] = max(0, min(100, scores[k]))

    return scores


def _debate(data: dict, scores: dict) -> tuple:
    """模拟多空辩论"""
    bull = 0
    bear = 0

    # Bull 论据
    if scores["capital"] > 60:
        bull += 2
    if scores["news"] > 60:
        bull += 2
    if scores["fundamental"] > 60:
        bull += 2
    if scores["technical"] > 60:
        bull += 1
    if scores["policy"] > 55:
        bull += 1

    # Bear 论据
    if scores["technical"] < 45:
        bear += 2
    if scores["risk"] < 45:
        bear += 2
    if scores["fundamental"] < 45:
        bear += 1
    if scores["capital"] < 45:
        bear += 1

    return max(1, bull), max(1, bear)


def _generate_report(data, scores, avg_score, signal, position, confidence, bull, bear) -> str:
    """生成 Markdown 报告"""
    ticker = data["ticker"]
    date = data["date"]

    report = f"""# {ticker} 快速投研报告

**日期**: {date} | **模式**: 轻量模式（规则引擎）

---

## 信号摘要

| 项目 | 内容 |
|------|------|
| **信号** | **{signal}** |
| **建议仓位** | {position} |
| **信心度** | {confidence} |
| **综合评分** | **{avg_score}/100** |
| **多空比分** | Bull {bull} : Bear {bear} |

---

## 六维评分

| 维度 | 得分 | 权重 | 加权分 |
|------|------|------|--------|
| 基本面 | {scores['fundamental']} | 30% | {round(scores['fundamental']*0.30,1)} |
| 技术面 | {scores['technical']} | 25% | {round(scores['technical']*0.25,1)} |
| 资金面 | {scores['capital']} | 20% | {round(scores['capital']*0.20,1)} |
| 消息面 | {scores['news']} | 10% | {round(scores['news']*0.10,1)} |
| 政策面 | {scores['policy']} | 8% | {round(scores['policy']*0.08,1)} |
| 风险面 | {scores['risk']} | 7% | {round(scores['risk']*0.07,1)} |

---

## 数据摘要

### K线/行情
{data.get('kline', 'N/A')[:500]}

### 技术指标
- MACD: {data.get('macd', 'N/A')[:200]}
- RSI: {data.get('rsi', 'N/A')[:200]}

### 基本面
{data.get('fundamentals', 'N/A')[:500]}

### 资金流向
{data.get('fund_flow', 'N/A')[:300]}

### 新闻要点
{data.get('news', 'N/A')[:500]}

### 解禁情况
{data.get('lockup', 'N/A')[:300]}

---

## 免责声明

本项目仅供学习研究与技术演示，不构成任何投资建议。
"""
    return report
