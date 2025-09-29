"""Centralized plugin management for STSMODDER."""
from __future__ import annotations

import importlib.util
import inspect
import logging
import sys
import threading
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, Iterable, List, Optional


class PluginManager:
    """Singleton manager that orchestrates plugin loading and symbol exposure."""

    _instance: Optional["PluginManager"] = None
    _instance_lock = threading.RLock()

    def __init__(self) -> None:
        self._logger = logging.getLogger("stsm.plugin_manager")
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
        self._logger.setLevel(logging.INFO)
        self._module_registry: Dict[str, Dict[str, Any]] = {}
        self._symbol_index: Dict[str, Any] = {}
        self._loaded_plugins: Dict[str, ModuleType] = {}
        self._event_listeners: Dict[str, List[Any]] = {}
        self._logger.debug("PluginManager initialized")

    @classmethod
    def get_instance(cls) -> "PluginManager":
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def register_module(self, module_name: str, module_obj: ModuleType) -> None:
        """Register a module so that all public symbols are exposed to plugins."""
        if not module_name:
            raise ValueError("module_name cannot be empty")
        public_members: Dict[str, Any] = {}
        for attr_name in dir(module_obj):
            if attr_name.startswith("_"):
                continue
            try:
                value = getattr(module_obj, attr_name)
            except AttributeError:
                continue
            public_members[attr_name] = value
            qualified_name = f"{module_name}.{attr_name}"
            self._symbol_index[qualified_name] = value
        self._module_registry[module_name] = public_members
        self._logger.debug("Registered module %s with %d public members", module_name, len(public_members))

    def register_symbol(self, qualified_name: str, value: Any) -> None:
        """Expose a runtime symbol that may not belong to a static module."""
        if not qualified_name:
            raise ValueError("qualified_name cannot be empty")
        self._symbol_index[qualified_name] = value
        module_name = qualified_name.split(".", 1)[0]
        module_members = self._module_registry.setdefault(module_name, {})
        module_members[qualified_name] = value
        self._logger.debug("Registered dynamic symbol %s", qualified_name)

    def get_symbol(self, qualified_name: str) -> Any:
        """Retrieve a previously exposed symbol."""
        if qualified_name not in self._symbol_index:
            raise KeyError(f"Symbol '{qualified_name}' not registered")
        return self._symbol_index[qualified_name]

    def load_plugin(self, plugin_path: Path) -> ModuleType:
        """Load an external plugin module and register its symbols."""
        if not plugin_path.exists():
            raise FileNotFoundError(f"Plugin path '{plugin_path}' does not exist")
        plugin_name = plugin_path.stem
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Unable to load plugin from '{plugin_path}'")
        module = importlib.util.module_from_spec(spec)
        sys.modules[plugin_name] = module
        spec.loader.exec_module(module)
        self._loaded_plugins[plugin_name] = module
        self.register_module(plugin_name, module)
        self._logger.info("Loaded plugin %s", plugin_name)
        return module

    def register_event_listener(self, event_name: str, listener: Any) -> None:
        """Register an object that exposes a handler for the specified event."""
        if not hasattr(listener, "handle_event") or not callable(getattr(listener, "handle_event")):
            raise ValueError("Listener must define a callable 'handle_event' method")
        listeners = self._event_listeners.setdefault(event_name, [])
        listeners.append(listener)
        self._logger.debug("Registered listener %s for event %s", listener, event_name)

    def dispatch_event(self, event_name: str, payload: Dict[str, Any]) -> None:
        """Dispatch an event to all registered listeners."""
        listeners = self._event_listeners.get(event_name, [])
        for listener in list(listeners):
            try:
                listener.handle_event(event_name, payload)
            except Exception as exc:  # pylint: disable=broad-except
                self._logger.error("Listener %s raised %s during event %s", listener, exc, event_name)

    def export_registry(self) -> Dict[str, Dict[str, str]]:
        """Return a serializable snapshot of registered modules and symbols."""
        snapshot: Dict[str, Dict[str, str]] = {}
        for module_name, members in self._module_registry.items():
            snapshot[module_name] = {
                key: self._describe_symbol(value) for key, value in members.items()
            }
        return snapshot

    def get_loaded_plugins(self) -> Iterable[str]:
        """Return the names of loaded plugin modules."""
        return tuple(self._loaded_plugins.keys())

    def _describe_symbol(self, value: Any) -> str:
        """Return a descriptive string for a symbol."""
        if inspect.isclass(value):
            return f"class {value.__module__}.{value.__name__}"
        if inspect.ismethod(value) or inspect.isfunction(value):
            return f"callable {value.__module__}.{value.__name__}"
        return f"instance of {type(value).__module__}.{type(value).__name__}"


_plugin_manager_instance = PluginManager.get_instance()
_plugin_manager_instance.register_module(__name__, sys.modules[__name__])
