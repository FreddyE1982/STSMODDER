"""Tests for the JPype test orchestrator."""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from jpypetestorchestrator import ORCHESTRATOR
from logic import APPLICATION_LOGIC, ApplicationLogic
from scripts import FakeDesktopJarFactory


class TestJPypeOrchestrator:
    """Validate suite discovery and execution behavior."""

    def test_baseline_suite_is_registered(self) -> None:
        suites = ORCHESTRATOR.get_suites()
        assert "baseline_smoke" in suites

    def test_execute_suite_requires_classpath(self) -> None:
        APPLICATION_LOGIC.update_configuration(
            modthespire_jar="",
            basemod_path="",
            stslib_path="",
            actlikeit_path="",
        )
        with pytest.raises(ApplicationLogic.ConfigurationError):
            ORCHESTRATOR.execute_suite("baseline_smoke")

    def test_execute_suite_runs_with_real_jvm(self, tmp_path: Path) -> None:
        original = APPLICATION_LOGIC.runtime_config.to_dict()
        try:
            library_dir = tmp_path / "libs"
            library_dir.mkdir()
            jar_paths = {}
            factory = FakeDesktopJarFactory()
            for filename in [
                "ModTheSpire.jar",
                "BaseMod.jar",
                "StSLib.jar",
                "ActLikeIt.jar",
            ]:
                jar_path = library_dir / filename
                factory.create(jar_path)
                jar_paths[filename] = str(jar_path)
            desktop_jar = library_dir / "desktop-1.0.jar"
            factory.create(desktop_jar)
            APPLICATION_LOGIC.update_configuration(
                modthespire_jar=jar_paths["ModTheSpire.jar"],
                basemod_path=jar_paths["BaseMod.jar"],
                stslib_path=jar_paths["StSLib.jar"],
                actlikeit_path=jar_paths["ActLikeIt.jar"],
            )
            results = ORCHESTRATOR.execute_suite("baseline_smoke")
            assert results["suite"] == "baseline_smoke"
            statuses = {case["status"] for case in results["results"]}
            assert statuses == {"passed"}
            controller = APPLICATION_LOGIC.bridge_controller
            assert controller.get_state() == ApplicationLogic.BridgeState.RUNNING
            # call into JVM to confirm JPype bridge is usable
            value = controller.execute_static("java.lang.String", "valueOf", True)
            assert value == "true"
        finally:
            APPLICATION_LOGIC.bridge_controller.shutdown_jvm()
            APPLICATION_LOGIC.update_configuration(**original)
            if tmp_path.exists():
                shutil.rmtree(tmp_path, ignore_errors=True)
