"""Tests for the plugin manager."""
from __future__ import annotations

from plugin_manager import PluginManager


class TestPluginManager:
    """Verify plugin registry behavior."""

    def test_registry_contains_core_modules(self) -> None:
        manager = PluginManager.get_instance()
        snapshot = manager.export_registry()
        assert "plugin_manager" in snapshot
        assert "PluginManager" in snapshot["plugin_manager"]

    def test_dynamic_symbol_registration(self) -> None:
        manager = PluginManager.get_instance()
        manager.register_symbol("tests.custom_symbol", {"value": 42})
        retrieved = manager.get_symbol("tests.custom_symbol")
        assert retrieved == {"value": 42}
