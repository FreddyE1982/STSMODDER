# STSMODDER

STSMODDER delivers a Streamlit-driven experience for managing Slay the Spire modding workflows with full parity across BaseMod, ModTheSpire, STSLib, and ActLikeIt. The platform embeds a global plugin framework so every class, method, and configuration value remains accessible to extensions, while the JPype orchestration stack bridges Python and the Java libraries required for comprehensive testing.

## Features

- **Global Plugin System** – `plugin_manager.PluginManager` exposes every registered module, symbol, and runtime object, enabling advanced extensions without patching core files.
- **Centralized Application Logic** – `logic.ApplicationLogic` persists runtime configuration, validates Java dependencies, and manages the JPype lifecycle with strict error handling.
- **JPype Test Harness** – `jpypetestorchestrator.JPypeTestOrchestrator` discovers baseline and plugin-provided integration suites, guaranteeing JVM readiness before executing tests.
- **Streamlit GUI** – `gui.StreamlitGUI` provides configuration forms, live JVM controls, plugin registry introspection, and one-click execution of JPype-powered test suites.
- **Command-Line Launcher** – `main.MainEntryPoint` bootstraps the Streamlit interface when invoked via `python main.py`, eliminating manual `streamlit run` commands.

## Prerequisites

- Python 3.10+
- Java 8 (with access to the `libjvm` shared library)
- BaseMod, ModTheSpire, STSLib, and ActLikeIt jar files
- `desktop-1.0.jar` from your Slay the Spire installation

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Running the GUI

Launch the Streamlit interface directly:

```bash
python main.py
```

Configure Java paths, library jars, and run the **baseline_smoke** suite to validate the environment before executing mod-specific workflows. The dependency modal summarizes the BaseMod and ModTheSpire requirements and can be dismissed permanently when desired.

## Automated Tests

Execute the integration tests to verify the plugin registry, configuration persistence, and JPype orchestration guards:

```bash
pytest
```

## Repository Structure

- `plugin_manager.py` – Singleton plugin registry exposing modules, dynamic symbols, and event hooks.
- `logic.py` – Configuration persistence, validation routines, and JPype lifecycle management.
- `jpypetestorchestrator.py` – Test suite registration and execution through the JPype bridge.
- `gui.py` – Streamlit UI orchestration, environment forms, JVM control panel, and test runner.
- `main.py` – Command-line entry launching the Streamlit app.
- `tests/` – Pytest suite targeting plugin manager, logic, and orchestrator behavior.
- `research/` – Curated references from BaseMod, ModTheSpire, STSLib, ActLikeIt, and JPype documentation.
- `developmentplan.md`, `guistructure.md`, `guielements.md`, `restapi.md`, `futures.md` – Planning and documentation artifacts maintained alongside code changes.

## Extending via Plugins

Create a Python module, expose classes or callables, and register it with `PluginManager.load_plugin`. Any symbol marked with a `build_suite` method and `__jpype_suite__ = True` will automatically contribute additional JPype test suites to the GUI and automation pipelines.
