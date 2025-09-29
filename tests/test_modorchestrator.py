"""Tests for the mod project orchestrator."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from modorchestrator import MOD_ORCHESTRATOR, ModOrchestrator
from plugin_manager import PluginManager


class CaptureListener:
    """Collect dispatched events for assertions."""

    def __init__(self) -> None:
        self.events = []

    def handle_event(self, event_name: str, payload):  # noqa: D401 - plugin interface
        self.events.append((event_name, payload))


class TestModOrchestrator:
    """Validate mod generation end-to-end."""

    def test_generate_mod_project(self, tmp_path: Path) -> None:
        plugin_manager = PluginManager.get_instance()
        listener = CaptureListener()
        plugin_manager.register_event_listener("mod_generation.post", listener)

        card_definition = ModOrchestrator.CardDefinition(
            card_id="buddy:SparkStrike",
            class_name="SparkStrike",
            name="Spark Strike",
            description="Deal !D! damage and gain !B! Block.",
            upgrade_description="Deal !D! damage and gain !B! Block.",
            card_type="ATTACK",
            rarity="COMMON",
            target="ENEMY",
            color="RED",
            cost=1,
            base_damage=6,
            base_block=4,
            base_magic=1,
            upgrade_damage=3,
            upgrade_block=2,
            upgrade_magic=1,
        )
        keyword_definition = ModOrchestrator.KeywordDefinition(
            name="spark",
            proper_name="Spark",
            description="Sparks your creativity, granting Strength.",
            aliases=["sparks"],
        )
        definition = ModOrchestrator.ModDefinition(
            mod_id="buddy",
            package="com.buddy.mod",
            entry_class_name="BuddyMod",
            display_name="Buddy Mod",
            author="Best Bud",
            version="1.0.0",
            description="A friendly mod built entirely by automation.",
            cards=[card_definition],
            keywords=[keyword_definition],
        )

        output_dir = tmp_path / "BuddyMod"
        result = MOD_ORCHESTRATOR.generate_mod(definition, destination=output_dir, overwrite=True)

        assert result.exists()
        entrypoint = result / "src" / "main" / "java" / "com" / "buddy" / "mod" / "BuddyMod.java"
        assert entrypoint.exists()
        entrypoint_text = entrypoint.read_text(encoding="utf-8")
        assert "BaseMod.addCard(new SparkStrike());" in entrypoint_text
        assert "BaseMod.addKeyword(" in entrypoint_text

        card_java = result / "src" / "main" / "java" / "com" / "buddy" / "mod" / "cards" / "SparkStrike.java"
        assert card_java.exists()
        card_text = card_java.read_text(encoding="utf-8")
        assert "extends CustomCard" in card_text
        assert "BaseMod" not in card_text  # sanity check on namespace

        cards_json = result / "src" / "main" / "resources" / "buddy" / "localization" / "eng" / "cards.json"
        assert cards_json.exists()
        cards_payload = json.loads(cards_json.read_text(encoding="utf-8"))
        assert "buddy:SparkStrike" in cards_payload
        assert cards_payload["buddy:SparkStrike"]["NAME"] == "Spark Strike"

        keywords_json = result / "src" / "main" / "resources" / "buddy" / "keywords.json"
        localization_keywords = result / "src" / "main" / "resources" / "buddy" / "localization" / "eng" / "keywords.json"
        for file_path in (keywords_json, localization_keywords):
            assert file_path.exists()
            payload = json.loads(file_path.read_text(encoding="utf-8"))
            assert payload[0]["PROPER_NAME"] == "Spark"
            assert "sparks" in payload[0]["NAMES"]

        for folder in ("cards", "relics", "powers", "orbs", "ui"):
            marker = result / "src" / "main" / "resources" / "buddy" / "images" / folder / ".gitkeep"
            assert marker.exists()

        pom = result / "pom.xml"
        assert pom.exists()
        pom_text = pom.read_text(encoding="utf-8")
        assert "desktop-1.0.jar" in pom_text

        readme = result / "README.md"
        assert readme.exists()
        assert "Run `mvn package`" in readme.read_text(encoding="utf-8")

        assert listener.events
        assert listener.events[-1][0] == "mod_generation.post"
        assert listener.events[-1][1]["destination"] == str(result)

    def test_generate_mod_requires_namespace_alignment(self, tmp_path: Path) -> None:
        card_definition = ModOrchestrator.CardDefinition(
            card_id="other:Spark",
            class_name="Spark",
            name="Spark",
            description="",
            upgrade_description="",
            card_type="ATTACK",
            rarity="COMMON",
            target="ENEMY",
            color="RED",
            cost=1,
        )
        definition = ModOrchestrator.ModDefinition(
            mod_id="buddy",
            package="com.buddy.mod",
            entry_class_name="BuddyMod",
            display_name="Buddy Mod",
            author="Best Bud",
            version="1.0.0",
            description="",
            cards=[card_definition],
        )
        with pytest.raises(ModOrchestrator.GenerationError):
            MOD_ORCHESTRATOR.generate_mod(definition, destination=tmp_path / "bad", overwrite=True)
