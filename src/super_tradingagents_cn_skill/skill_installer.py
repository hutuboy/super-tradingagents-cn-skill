"""SKILL 文件安装器 — 将 SKILL 安装到不同平台"""
import shutil
from pathlib import Path
from typing import List

# 包内 SKILL 文件路径
PKG_DIR = Path(__file__).parent
SKILLS_DIR = PKG_DIR / "assets" / "skills"

PLATFORM_MAP = {
    "trae": {
        "file": "SKILL.md",
        "location": ".trae/skills/super-tradingagents-cn-skill/SKILL.md",
    },
    "cursor": {
        "file": ".cursorrules",
        "location": ".cursorrules",
    },
    "claude": {
        "file": "CLAUDE.md",
        "location": "CLAUDE.md",
    },
    "cline": {
        "file": ".clinerules",
        "location": ".clinerules",
    },
    "windsurf": {
        "file": ".windsurfrules",
        "location": ".windsurfrules",
    },
}


def list_platforms() -> List[dict]:
    """列出支持的所有平台"""
    return [
        {"name": name, "file": info["file"], "location": info["location"]}
        for name, info in PLATFORM_MAP.items()
    ]


def install_skill(platform: str, target_dir: str = ".") -> List[str]:
    """安装 SKILL 文件到目标目录

    Args:
        platform: trae/cursor/claude/cline/windsurf/all
        target_dir: 安装目标目录

    Returns:
        已安装的文件路径列表
    """
    target = Path(target_dir).resolve()
    installed = []

    platforms = list(PLATFORM_MAP.keys()) if platform == "all" else [platform]

    for p in platforms:
        if p not in PLATFORM_MAP:
            continue

        info = PLATFORM_MAP[p]
        src = SKILLS_DIR / info["file"]
        dst = target / info["location"]

        if not src.exists():
            continue

        # 确保父目录存在
        dst.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(src, dst)
        installed.append(str(dst))

    return installed
