"""Tests for the JPype test orchestrator."""
from __future__ import annotations

import pytest

from jpypetestorchestrator import ORCHESTRATOR
from logic import APPLICATION_LOGIC, ApplicationLogic


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
