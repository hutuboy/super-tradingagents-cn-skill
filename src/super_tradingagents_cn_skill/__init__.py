"""
Super TradingAgents CN Skill
A股多Agent投研分析SKILL — 适配多平台的交互式投研助手

Usage:
    from super_tradingagents_cn_skill import quick_analyze
    result = quick_analyze("002714")
"""

__version__ = "0.1.0"
__author__ = "hutuboy"

from .quick_analyze import quick_analyze
from .skill_installer import install_skill, list_platforms

__all__ = ["quick_analyze", "install_skill", "list_platforms"]
