# STSMODDER

STSMODDER delivers a Streamlit-driven experience for managing Slay the Spire modding workflows with full parity across BaseMod, ModTheSpire, STSLib, and ActLikeIt. The platform embeds a global plugin framework so every class, method, and configuration value remains accessible to extensions, while the JPype orchestration stack bridges Python and the Java libraries required for comprehensive testing.

## Features

- **Global Plugin System** – `plugin_manager.PluginManager` exposes every registered module, symbol, and runtime object, enabling advanced extensions without patching core files.
- **Centralized Application Logic** – `logic.ApplicationLogic` persists runtime configuration, validates Java dependencies, and manages the JPype lifecycle with strict error handling.
- **JPype Test Harness** – `jpypetestorchestrator.JPypeTestOrchestrator` discovers baseline and plugin-provided integration suites, guaranteeing JVM readiness before executing tests.
- **Streamlit GUI** – `gui.StreamlitGUI` provides configuration forms, live JVM controls, plugin registry introspection, and one-click execution of JPype-powered test suites.
- **Command-Line Launcher** – `main.MainEntryPoint` bootstraps the Streamlit interface when invoked via `python main.py`, eliminating manual `streamlit run` commands.
- **Mod Export Orchestrator** – `modorchestrator.ModOrchestrator` materializes GUI-authored content into Java sources, localization payloads, assets, and a compiled jar ready for ModTheSpire while dispatching lifecycle events for plugin extensions.

## Prerequisites

- Python 3.10+
- Java 8 (with access to the `libjvm` shared library)
- BaseMod, ModTheSpire, StSLib, and ActLikeIt jar files
- `desktop-1.0.jar` from your Slay the Spire installation (or a script-generated equivalent for testing)

Create the desktop jar when needed instead of checking binaries into version control:

```bash
python -m scripts.create_fake_desktop_jar tests/.cache/desktop-1.0.jar
```

Point `logic.ApplicationLogic` at the generated jar so both the GUI and JPype tests can start the JVM successfully.

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

Always run the suite against an installed copy of JPype with the JVM classpath pointing to ModTheSpire, BaseMod, StSLib, ActLikeIt, and the configured desktop jar.

## Repository Structure

- `plugin_manager.py` – Singleton plugin registry exposing modules, dynamic symbols, and event hooks.
- `logic.py` – Configuration persistence, validation routines, and JPype lifecycle management.
- `jpypetestorchestrator.py` – Test suite registration and execution through the JPype bridge.
- `modorchestrator.py` – Export pipeline producing fully structured Slay the Spire mods directly from GUI specifications.
- `gui.py` – Streamlit UI orchestration, environment forms, JVM control panel, and test runner.
- `main.py` – Command-line entry launching the Streamlit app.
- `tests/` – Pytest suite targeting plugin manager, logic, and orchestrator behavior.
- `research/` – Curated references from BaseMod, ModTheSpire, STSLib, ActLikeIt, and JPype documentation.
- `developmentplan.md`, `guistructure.md`, `guielements.md`, `restapi.md`, `futures.md` – Planning and documentation artifacts maintained alongside code changes.

## Extending via Plugins

Create a Python module, expose classes or callables, and register it with `PluginManager.load_plugin`. Any symbol marked with a `build_suite` method and `__jpype_suite__ = True` will automatically contribute additional JPype test suites to the GUI and automation pipelines.

## Mod Export Pipeline

`modorchestrator.ModOrchestrator` is the canonical export pathway. Given a GUI-authored project it will:

1. Create `<output>/<mod_id>/src/main/java` and `<output>/<mod_id>/src/main/resources` scaffolding.
2. Generate the ModTheSpire entry point, card classes, and keyword registrations from the captured GUI state.
3. Write localization JSON and copy all referenced assets under `<mod_id>Resources`.
4. Compile the Java sources with `javac`, targeting Java 8 when the compiler supports `--release 8`.
5. Package compiled classes and resources into `build/<mod_id>.jar`, ready for ModTheSpire.

Plugins can subscribe to the `mod.build.start` and `mod.build.completed` events to extend validation, emit additional assets, or trigger downstream automation.
