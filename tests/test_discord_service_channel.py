from __future__ import annotations

try:
    from src.digest_bot.discord.self_guide import ServerBlueprint
except Exception:
    from digest_bot.discord.self_guide import ServerBlueprint


def test_service_channel_in_blueprint():
    bp = ServerBlueprint.default()
    admin_cat = next((c for c in bp.categories if c.name == "⚙️ ADMIN"), None)
    assert admin_cat is not None
    names = [ch.name for ch in admin_cat.channels]
    assert "🔧-service" in names
    # New admin reports channel should exist
    assert "📥-reports" in names
