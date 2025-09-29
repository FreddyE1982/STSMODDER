"""JPype-based integration test orchestration."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List

from logic import APPLICATION_LOGIC, ApplicationLogic
from plugin_manager import PluginManager


class JPypeTestOrchestrator:
    """Coordinates discovery and execution of integration tests via JPype."""

    @dataclass
    class TestCase:
        name: str
        executor: Callable[[ApplicationLogic.JPypeBridgeController], Any]
        description: str = ""

        def run(self, controller: ApplicationLogic.JPypeBridgeController) -> Dict[str, Any]:
            result: Dict[str, Any] = {"name": self.name, "description": self.description}
            try:
                output = self.executor(controller)
                result["status"] = "passed"
                result["output"] = output
            except Exception as exc:  # pylint: disable=broad-except
                result["status"] = "failed"
                result["error"] = str(exc)
            return result

    @dataclass
    class TestSuite:
        name: str
        cases: List["JPypeTestOrchestrator.TestCase"] = field(default_factory=list)
        description: str = ""

        def add_case(self, case: "JPypeTestOrchestrator.TestCase") -> None:
            self.cases.append(case)

        def execute(self, controller: ApplicationLogic.JPypeBridgeController) -> Dict[str, Any]:
            results: List[Dict[str, Any]] = []
            for case in self.cases:
                results.append(case.run(controller))
            return {"suite": self.name, "results": results, "description": self.description}

    def __init__(self, app_logic: ApplicationLogic, plugin_manager: PluginManager) -> None:
        self._logic = app_logic
        self._plugin_manager = plugin_manager
        self._logger = logging.getLogger("stsm.jpype_test_orchestrator")
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
        self._logger.setLevel(logging.INFO)
        self._suites: Dict[str, JPypeTestOrchestrator.TestSuite] = {}
        self._register_builtin_suites()
        self._discover_plugin_suites()
        self._plugin_manager.register_module(__name__, __import__(__name__))
        self._plugin_manager.register_symbol("jpypetestorchestrator.orchestrator", self)

    def _register_builtin_suites(self) -> None:
        smoke_suite = JPypeTestOrchestrator.TestSuite(
            name="baseline_smoke",
            description="Validates JPype readiness and configuration completeness.",
        )
        smoke_suite.add_case(
            JPypeTestOrchestrator.TestCase(
                name="validate_environment",
                description="Ensures required configuration paths are present before launching the JVM.",
                executor=self._validate_environment,
            )
        )
        smoke_suite.add_case(
            JPypeTestOrchestrator.TestCase(
                name="verify_classpath",
                description="Confirms the computed JPype classpath resolves to existing artifacts.",
                executor=self._verify_classpath,
            )
        )
        self._suites[smoke_suite.name] = smoke_suite

    def _discover_plugin_suites(self) -> None:
        registry = self._plugin_manager.export_registry()
        for module_name, members in registry.items():
            for symbol_name in members:
                try:
                    symbol = self._plugin_manager.get_symbol(f"{module_name}.{symbol_name}")
                except KeyError:
                    continue
                if hasattr(symbol, "__jpype_suite__") and callable(getattr(symbol, "build_suite", None)):
                    suite = symbol.build_suite(self._logic, self._plugin_manager)
                    if isinstance(suite, JPypeTestOrchestrator.TestSuite):
                        self._suites[suite.name] = suite

    def get_suites(self) -> List[str]:
        return sorted(self._suites.keys())

    def execute_suite(self, name: str) -> Dict[str, Any]:
        if name not in self._suites:
            raise KeyError(f"Test suite '{name}' is not registered")
        controller = self._logic.bridge_controller
        if controller.get_state() != ApplicationLogic.BridgeState.RUNNING:
            controller.start_jvm()
        suite = self._suites[name]
        self._logger.info("Executing test suite %s", name)
        results = suite.execute(controller)
        self._plugin_manager.dispatch_event(
            "tests.completed",
            {"suite": name, "results": results},
        )
        return results

    def _validate_environment(self, controller: ApplicationLogic.JPypeBridgeController) -> Dict[str, bool]:
        _ = controller
        return self._logic.validate_environment()

    def _verify_classpath(self, controller: ApplicationLogic.JPypeBridgeController) -> Dict[str, Any]:
        _ = controller
        missing: List[str] = []
        config = self._logic.runtime_config
        for attr in ["modthespire_jar", "basemod_path", "stslib_path", "actlikeit_path"]:
            path_value = getattr(config, attr)
            if not path_value:
                missing.append(attr)
            elif not Path(path_value).expanduser().exists():
                missing.append(attr)
        return {"missing": missing, "classpath_ready": not missing}


ORCHESTRATOR = JPypeTestOrchestrator(APPLICATION_LOGIC, PluginManager.get_instance())
