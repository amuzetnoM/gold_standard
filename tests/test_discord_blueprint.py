import os
from pathlib import Path

import pytest


def test_discord_requirement_present():
    req_file = Path(__file__).resolve().parents[1] / "src" / "digest_bot" / "requirements.txt"
    txt = req_file.read_text()
    assert "discord.py" in txt, "discord.py should be in digest bot requirements"


def test_blueprint_files_exist():
    root = Path(__file__).resolve().parents[1] / "src" / "digest_bot" / "discord"
    assert (root / "BLUEPRINT_ARCHITECTURE.md").exists()
    assert (root / "README_BLUEPRINT.md").exists()
    assert (root / "bot_base.py").exists()
    assert (root / "cogs").is_dir()


@pytest.mark.skipif(not os.getenv("DISCORD_BOT_TOKEN"), reason="No bot token set for live import test")
def test_bot_import_and_init_live():
    # This is a live test and is skipped unless DISCORD_BOT_TOKEN is present in env
    from src.digest_bot.discord.bot_base import GoldStandardBot
    bot = GoldStandardBot(token=os.getenv("DISCORD_BOT_TOKEN"))
    assert bot.token
