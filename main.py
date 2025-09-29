"""Main entry point launching the Streamlit GUI."""
from __future__ import annotations

import logging
import sys
from pathlib import Path

from plugin_manager import PluginManager


class MainEntryPoint:
    """Entry point invoked via `python main.py`."""

    def __init__(self) -> None:
        self._logger = logging.getLogger("stsm.main")
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
        self._logger.setLevel(logging.INFO)
        self._plugin_manager = PluginManager.get_instance()
        self._plugin_manager.register_module(__name__, __import__(__name__))
        self._plugin_manager.register_symbol("main.entry_point", self)

    def launch(self) -> None:
        self._logger.info("Launching Streamlit GUI")
        try:
            from streamlit.web import bootstrap
        except ImportError as exc:  # pragma: no cover - dependency error path
            raise RuntimeError("Streamlit is required to launch the GUI") from exc
        script_path = Path(__file__).with_name("gui.py").resolve()
        command_line = f"streamlit run {script_path}"
        bootstrap.run(str(script_path), command_line, sys.argv[1:])


if __name__ == "__main__":
    MainEntryPoint().launch()
