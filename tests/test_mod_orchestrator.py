"""Integration tests for the ModOrchestrator."""
from __future__ import annotations

import json
import os
import urllib.request
import zipfile
from pathlib import Path

import jpype
import pytest

from logic import APPLICATION_LOGIC
from modorchestrator import MOD_ORCHESTRATOR, ModOrchestrator
from scripts.create_fake_desktop_jar import create_fake_desktop_jar

BASEMOD_URL = "https://github.com/daviscook477/BaseMod/releases/download/v5.5.0/BaseMod.jar"
MODTHESPIRE_URL = "https://github.com/kiooeht/ModTheSpire/releases/download/v3.6.3/ModTheSpire.zip"
CACHE_DIR = Path("tests/.cache")


@pytest.fixture(scope="session")
def dependency_bundle() -> dict[str, Path]:
    """Ensure BaseMod, ModTheSpire, and the desktop stub jar are available."""

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    basemod_path = CACHE_DIR / "BaseMod.jar"
    if not basemod_path.exists():
        with urllib.request.urlopen(BASEMOD_URL) as response:
            basemod_path.write_bytes(response.read())
    modthespire_zip = CACHE_DIR / "ModTheSpire.zip"
    modthespire_path = CACHE_DIR / "ModTheSpire.jar"
    if not modthespire_path.exists():
        with urllib.request.urlopen(MODTHESPIRE_URL) as response:
            modthespire_zip.write_bytes(response.read())
        with zipfile.ZipFile(modthespire_zip, "r") as archive:
            with archive.open("ModTheSpire.jar") as jar_stream:
                modthespire_path.write_bytes(jar_stream.read())
    desktop_path = CACHE_DIR / "desktop-1.0.jar"
    if not desktop_path.exists():
        create_fake_desktop_jar(desktop_path)
    return {
        "basemod": basemod_path,
        "modthespire": modthespire_path,
        "desktop": desktop_path,
    }


@pytest.fixture()
def restore_runtime_config() -> None:
    """Reset ApplicationLogic runtime configuration after each test."""

    original = APPLICATION_LOGIC.runtime_config.to_dict()
    yield
    APPLICATION_LOGIC.update_configuration(**original)


def _write_card_image(path: Path) -> None:
    """Persist a minimal transparent PNG used for card registration."""

    png_bytes = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0cIDATx\x9cc``\x00\x00\x00\x02\x00\x01"
        b"\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png_bytes)


class TestModOrchestrator:
    """Validate that the orchestrator produces runnable assets."""

    def test_builds_mod_and_exposes_classes(
        self,
        tmp_path: Path,
        dependency_bundle: dict[str, Path],
        restore_runtime_config: None,
    ) -> None:
        output_dir = tmp_path / "build"
        image_path = tmp_path / "art" / "strike.png"
        _write_card_image(image_path)

        APPLICATION_LOGIC.update_configuration(
            java_home="",
            modthespire_jar=str(dependency_bundle["modthespire"]),
            basemod_path=str(dependency_bundle["basemod"]),
            stslib_path="",
            actlikeit_path="",
            desktop_jar_path=str(dependency_bundle["desktop"]),
        )

        metadata = ModOrchestrator.ModMetadata(
            mod_id="buddytestmod",
            name="Buddy Test Mod",
            author="Best Bud",
            version="1.0.0",
            description="Integration test mod built by ModOrchestrator",
            package="com.buddy.mods",
            entry_class="BuddyMod",
        )
        card = ModOrchestrator.CardDefinition(
            card_id="BuddyStrike",
            name="Buddy Strike",
            description="Deal damage like a champ.",
            upgrade_description="Deal even more damage.",
            card_type="ATTACK",
            card_color="COLORLESS",
            rarity="COMMON",
            target="ENEMY",
            cost=1,
            base_damage=6,
            upgrade_damage=3,
            image_path=image_path,
        )
        keyword = ModOrchestrator.KeywordDefinition(
            proper_name="Buddy",
            names=["buddy"],
            description="Represents how much of a pal you are.",
        )
        project = ModOrchestrator.ModProject(
            metadata=metadata,
            cards=[card],
            keywords=[keyword],
        )

        jar_path = MOD_ORCHESTRATOR.build_mod(project, output_dir)
        assert jar_path.exists()

        with zipfile.ZipFile(jar_path, "r") as archive:
            with archive.open("META-INF/mod.json") as mod_json_handle:
                mod_json = json.load(mod_json_handle)
            assert f"com/buddy/mods/cards/{card.class_name()}.class" in archive.namelist()
        assert mod_json["modid"] == metadata.mod_id
        assert mod_json["name"] == metadata.name

        classpath = os.pathsep.join(
            [
                str(jar_path),
                str(dependency_bundle["basemod"]),
                str(dependency_bundle["modthespire"]),
                str(dependency_bundle["desktop"]),
            ]
        )
        if jpype.isJVMStarted():
            jpype.shutdownJVM()
        jpype.startJVM(classpath=classpath)
        try:
            entry_class = jpype.JClass(f"{metadata.package}.{metadata.entry_class}")
            assert entry_class is not None
        finally:
            jpype.shutdownJVM()
