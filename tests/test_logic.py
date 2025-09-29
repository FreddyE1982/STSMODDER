"""Tests for application logic configuration handling."""
from __future__ import annotations

from copy import deepcopy

from logic import APPLICATION_LOGIC, ApplicationLogic


class TestApplicationLogic:
    """Ensure configuration lifecycle behaves predictably."""

    def test_configuration_roundtrip(self) -> None:
        logic_instance = ApplicationLogic()
        original = deepcopy(logic_instance.runtime_config.to_dict())
        updated = {
            "java_home": "/tmp/java_home",
            "modthespire_jar": "/tmp/ModTheSpire.jar",
            "basemod_path": "/tmp/BaseMod.jar",
            "stslib_path": "/tmp/StSLib.jar",
            "actlikeit_path": "/tmp/ActLikeIt.jar",
        }
        logic_instance.update_configuration(**updated)
        reloaded = ApplicationLogic()
        assert reloaded.runtime_config.java_home == updated["java_home"]
        assert reloaded.runtime_config.modthespire_jar == updated["modthespire_jar"]
        logic_instance.update_configuration(**original)
        APPLICATION_LOGIC.update_configuration(**original)
