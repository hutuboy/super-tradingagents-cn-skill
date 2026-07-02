"""CLI 入口 — stcs 命令"""
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import __version__
from .quick_analyze import quick_analyze
from .skill_installer import install_skill, list_platforms

console = Console()
app = typer.Typer(
    name="stcs",
    help="Super TradingAgents CN Skill — A股多Agent投研助手",
    no_args_is_help=True,
)


@app.command()
def analyze(
    ticker: str = typer.Argument(..., help="A股6位代码，如 002714、600519"),
    date: str = typer.Option("", "--date", "-d", help="分析日期，默认今天（YYYY-MM-DD）"),
    deep: bool = typer.Option(False, "--deep", help="启用深入分析模式（更多指标/更长周期）"),
    output: str = typer.Option("", "--output", "-o", help="报告输出路径，默认打印到终端"),
):
    """快速分析一只股票（轻量模式，无需 LLM API Key）"""
    console.print(Panel.fit(
        f"[bold cyan]Super TradingAgents CN Skill[/bold cyan] v{__version__}\n"
        f"分析标的: [bold yellow]{ticker}[/bold yellow]",
        title="投研分析",
        border_style="cyan",
    ))

    try:
        result = quick_analyze(ticker, date=date or None, deep=deep)
    except Exception as e:
        console.print(f"[bold red]分析失败: {e}[/bold red]")
        raise typer.Exit(1)

    # 输出报告
    if output:
        Path(output).write_text(result["report"], encoding="utf-8")
        console.print(f"[green]报告已保存: {output}[/green]")
    else:
        console.print(result["report"])

    # 打印决策摘要
    table = Table(title="最终决策", border_style="green")
    table.add_column("项目", style="cyan")
    table.add_column("内容", style="yellow")
    table.add_row("信号", result["signal"])
    table.add_row("仓位", result["position"])
    table.add_row("信心度", result["confidence"])
    table.add_row("综合评分", str(result["avg_score"]))
    table.add_row("多空比", result["bull_bear_ratio"])
    console.print(table)


@app.command()
def skill(
    action: str = typer.Argument(..., help="动作: install / list"),
    platform: str = typer.Option("all", "--platform", "-p", help="目标平台: trae/cursor/claude/cline/windsurf/all"),
    target_dir: str = typer.Option(".", "--dir", help="安装目标目录，默认当前目录"),
):
    """管理 SKILL 文件（安装到项目）"""
    if action == "list":
        platforms = list_platforms()
        table = Table(title="支持的 SKILL 平台", border_style="blue")
        table.add_column("平台", style="cyan")
        table.add_column("文件", style="green")
        table.add_column("放置位置", style="yellow")
        for p in platforms:
            table.add_row(p["name"], p["file"], p["location"])
        console.print(table)

    elif action == "install":
        installed = install_skill(platform, target_dir)
        for item in installed:
            console.print(f"[green]已安装: {item}[/green]")
        console.print(f"[bold green]SKILL 安装完成！[/bold green]")
    else:
        console.print(f"[red]未知动作: {action}，支持 install / list[/red]")
        raise typer.Exit(1)


@app.command()
def web():
    """启动 Web UI（调用 tradingagents-astock 的 Streamlit 界面）"""
    console.print("[cyan]正在启动 Web UI...[/cyan]")
    try:
        import subprocess
        subprocess.run([sys.executable, "-m", "streamlit", "run", "web/app.py"])
    except Exception as e:
        console.print(f"[red]启动失败: {e}[/red]")
        raise typer.Exit(1)


def main():
    app()
