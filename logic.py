"""Core application logic orchestrating configuration and JPype bridge management."""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from plugin_manager import PluginManager


class ApplicationLogic:
    """Coordinates configuration state and JPype bridge lifecycle."""

    class ConfigurationError(Exception):
        """Raised when configuration data is invalid."""

    class JPypeUnavailableError(Exception):
        """Raised when JPype is not available in the runtime environment."""

    class BridgeState(str, Enum):
        """State enumeration for the JPype bridge."""

        STOPPED = "stopped"
        STARTING = "starting"
        RUNNING = "running"
        SHUTTING_DOWN = "shutting_down"

    @dataclass
    class RuntimeConfig:
        """Runtime configuration persisted to disk."""

        java_home: str = ""
        modthespire_jar: str = ""
        basemod_path: str = ""
        stslib_path: str = ""
        actlikeit_path: str = ""
        enabled_libraries: List[str] = field(default_factory=lambda: ["BaseMod", "StSLib", "ActLikeIt"])
        suppress_dependency_modal: bool = False

        def to_dict(self) -> Dict[str, Any]:
            return {
                "java_home": self.java_home,
                "modthespire_jar": self.modthespire_jar,
                "basemod_path": self.basemod_path,
                "stslib_path": self.stslib_path,
                "actlikeit_path": self.actlikeit_path,
                "enabled_libraries": list(self.enabled_libraries),
                "suppress_dependency_modal": self.suppress_dependency_modal,
            }

        @classmethod
        def from_dict(cls, raw: Dict[str, Any]) -> "ApplicationLogic.RuntimeConfig":
            config = cls()
            config.java_home = raw.get("java_home", "")
            config.modthespire_jar = raw.get("modthespire_jar", "")
            config.basemod_path = raw.get("basemod_path", "")
            config.stslib_path = raw.get("stslib_path", "")
            config.actlikeit_path = raw.get("actlikeit_path", "")
            config.enabled_libraries = list(raw.get("enabled_libraries", config.enabled_libraries))
            config.suppress_dependency_modal = bool(raw.get("suppress_dependency_modal", False))
            return config

    class JPypeBridgeController:
        """Encapsulates JPype lifecycle control."""

        def __init__(self, logic: "ApplicationLogic") -> None:
            self._logic = logic
            self._logger = logging.getLogger("stsm.jpype_bridge")
            if not self._logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
                handler.setFormatter(formatter)
                self._logger.addHandler(handler)
            self._logger.setLevel(logging.INFO)
            self._state = ApplicationLogic.BridgeState.STOPPED
            self._jvm = None

        def start_jvm(self) -> None:
            if self._state == ApplicationLogic.BridgeState.RUNNING:
                return
            self._state = ApplicationLogic.BridgeState.STARTING
            try:
                import jpype
                import jpype.imports  # noqa: F401  # pylint: disable=unused-import
            except ImportError as exc:
                self._state = ApplicationLogic.BridgeState.STOPPED
                raise ApplicationLogic.JPypeUnavailableError("JPype is not installed") from exc
            classpath = self._compose_classpath()
            jvm_path = self._resolve_jvm_path()
            if jpype.isJVMStarted():
                self._state = ApplicationLogic.BridgeState.RUNNING
                return
            self._logger.info("Starting JVM with classpath: %s", classpath)
            if jvm_path:
                jpype.startJVM(jvm_path, "-ea", classpath=classpath)
            else:
                jpype.startJVM("-ea", classpath=classpath)
            self._state = ApplicationLogic.BridgeState.RUNNING
            self._jvm = jpype

        def shutdown_jvm(self) -> None:
            if self._state == ApplicationLogic.BridgeState.STOPPED:
                return
            self._state = ApplicationLogic.BridgeState.SHUTTING_DOWN
            try:
                import jpype
            except ImportError as exc:
                self._state = ApplicationLogic.BridgeState.STOPPED
                raise ApplicationLogic.JPypeUnavailableError("JPype is not installed") from exc
            if jpype.isJVMStarted():
                self._logger.info("Shutting down JVM")
                jpype.shutdownJVM()
            self._state = ApplicationLogic.BridgeState.STOPPED
            self._jvm = None

        def get_state(self) -> "ApplicationLogic.BridgeState":
            return self._state

        def execute_static(self, class_name: str, method_name: str, *args: Any) -> Any:
            if self._state != ApplicationLogic.BridgeState.RUNNING:
                raise ApplicationLogic.ConfigurationError("JVM is not running")
            if self._jvm is None:
                raise ApplicationLogic.ConfigurationError("JVM handle not available")
            java_class = self._jvm.JClass(class_name)
            method = getattr(java_class, method_name)
            return method(*args)

        def _compose_classpath(self) -> str:
            components: List[str] = []
            config = self._logic.runtime_config
            for path_value in [
                config.modthespire_jar,
                config.basemod_path,
                config.stslib_path,
                config.actlikeit_path,
            ]:
                if path_value:
                    resolved = Path(path_value).expanduser().resolve()
                    self._logic._validate_path(resolved)  # noqa: SLF001
                    components.append(str(resolved))
            path_separator = os.pathsep
            if not components:
                raise ApplicationLogic.ConfigurationError(
                    "Classpath is empty; configure ModTheSpire and library jar locations"
                )
            return path_separator.join(components)

        def _resolve_jvm_path(self) -> Optional[str]:
            java_home = self._logic.runtime_config.java_home
            if not java_home:
                return None
            candidate = Path(java_home).expanduser().resolve() / "lib" / "server"
            for suffix in ("libjvm.so", "libjvm.dylib", "jvm.dll"):
                lib_path = candidate / suffix
                if lib_path.exists():
                    return str(lib_path)
            raise ApplicationLogic.ConfigurationError(
                "Unable to locate JVM shared library in configured java_home"
            )

    def __init__(self) -> None:
        self._logger = logging.getLogger("stsm.application_logic")
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
        self._logger.setLevel(logging.INFO)
        self._plugin_manager = PluginManager.get_instance()
        self._config_dir = Path("config")
        self._config_path = self._config_dir / "runtime_config.json"
        self._runtime_config = ApplicationLogic.RuntimeConfig()
        self._bridge_controller = ApplicationLogic.JPypeBridgeController(self)
        self._ensure_config_dir()
        self._load_configuration()
        self._plugin_manager.register_module(__name__, __import__(__name__))
        self._plugin_manager.register_symbol("logic.application", self)

    @property
    def runtime_config(self) -> "ApplicationLogic.RuntimeConfig":
        return self._runtime_config

    @property
    def bridge_controller(self) -> "ApplicationLogic.JPypeBridgeController":
        return self._bridge_controller

    def update_configuration(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            if not hasattr(self._runtime_config, key):
                raise ApplicationLogic.ConfigurationError(f"Unknown configuration key '{key}'")
            setattr(self._runtime_config, key, value)
        self._save_configuration()

    def validate_environment(self) -> Dict[str, bool]:
        results: Dict[str, bool] = {}
        config = self._runtime_config
        results["java_home"] = bool(config.java_home and Path(config.java_home).expanduser().exists())
        results["modthespire_jar"] = self._optional_path_exists(config.modthespire_jar)
        results["basemod_path"] = self._optional_path_exists(config.basemod_path)
        results["stslib_path"] = self._optional_path_exists(config.stslib_path)
        results["actlikeit_path"] = self._optional_path_exists(config.actlikeit_path)
        return results

    def _optional_path_exists(self, path_value: str) -> bool:
        if not path_value:
            return False
        return Path(path_value).expanduser().exists()

    def _ensure_config_dir(self) -> None:
        self._config_dir.mkdir(parents=True, exist_ok=True)

    def _load_configuration(self) -> None:
        if self._config_path.exists():
            with self._config_path.open("r", encoding="utf-8") as handle:
                raw = json.load(handle)
            self._runtime_config = ApplicationLogic.RuntimeConfig.from_dict(raw)
        else:
            self._save_configuration()

    def _save_configuration(self) -> None:
        serialized = self._runtime_config.to_dict()
        with self._config_path.open("w", encoding="utf-8") as handle:
            json.dump(serialized, handle, indent=2)

    def _validate_path(self, path_value: Path) -> None:
        if not path_value.exists():
            raise ApplicationLogic.ConfigurationError(f"Configured path '{path_value}' does not exist")


APPLICATION_LOGIC = ApplicationLogic()
