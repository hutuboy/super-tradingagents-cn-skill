"""基础导入测试"""


def test_import():
    import super_tradingagents_cn_skill
    assert super_tradingagents_cn_skill.__version__ == "0.1.0"


def test_quick_analyze_import():
    from super_tradingagents_cn_skill import quick_analyze
    assert callable(quick_analyze)


def test_skill_installer_import():
    from super_tradingagents_cn_skill import install_skill, list_platforms
    assert callable(install_skill)
    assert callable(list_platforms)


def test_list_platforms():
    from super_tradingagents_cn_skill import list_platforms
    platforms = list_platforms()
    names = [p["name"] for p in platforms]
    assert "trae" in names
    assert "cursor" in names
    assert "claude" in names
    assert "cline" in names
    assert "windsurf" in names
