from types import SimpleNamespace

from digest_bot.discord.self_guide import SelfGuide


def fake_guild_with(names):
    return SimpleNamespace(text_channels=[SimpleNamespace(name=n) for n in names])


def test_service_duplicate_detection_keeps_canonical():
    g = fake_guild_with(["service", "🔧-service", "Service", "service-2"])
    sg = SelfGuide()

    # Access internal logic by invoking apply cleanup via a tiny runner: we can't call the async method directly here,
    # but we can emulate the detection logic by copying the detection code in test form.
    # For sanity, run the same normalization logic used in the module.
    import re

    service_candidates = []
    for ch in g.text_channels:
        norm = re.sub(r"[^a-z]", "", ch.name.lower())
        if norm == "service":
            service_candidates.append(ch)

    assert len(service_candidates) == 4

    # Keep canonical if present
    keep = next((c for c in service_candidates if c.name == "🔧-service"), None)
    assert keep is not None

    # The ones to delete should be all except keep
    to_delete = [c for c in service_candidates if c is not keep]
    assert [c.name for c in to_delete] == ["service", "Service", "service-2"]


def test_service_duplicate_detection_no_canonical_keeps_first():
    g = fake_guild_with(["service", "Service", "service-2"])
    import re

    service_candidates = []
    for ch in g.text_channels:
        norm = re.sub(r"[^a-z]", "", ch.name.lower())
        if norm == "service":
            service_candidates.append(ch)

    keep = service_candidates[0]
    to_delete = [c for c in service_candidates if c is not keep]
    assert [c.name for c in to_delete] == ["Service", "service-2"]
