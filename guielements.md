# GUI Elements Registry

[complete] Sidebar Form Fields
- **Java Home Input**: Text input bound to `logic.runtime_config.java_home`. Validates path existence and ensures the JVM library can be resolved.
- **ModTheSpire Jar Selector**: File uploader bound to `logic.runtime_config.modthespire_jar`. Triggers validation of jar metadata via the JPype orchestrator.
- **Library Toggles**: Checkbox group reflecting BaseMod, STSLib, and ActLikeIt activation states, bound to `logic.runtime_config.enabled_libraries`.

[complete] Main Dashboard Components
- **JPype Bridge Status Card**: Displays current JVM state (stopped, starting, running, shutting down) and exposes actions to start/stop through `logic.JPypeBridgeController`.
- **Plugin Registry Table**: Interactive table listing registered plugins, exposed symbols, and health indicators as provided by `plugin_manager.PluginManager`.
- **Test Suite Runner Panel**: Buttons to trigger baseline smoke tests and mod-specific regression suites managed by `jpypetestorchestrator.JPypeTestOrchestrator`.

[complete] Status Tab Panels
- **Runtime Overview Metric**: `st.metric` reflecting the active JVM state sourced from `logic.JPypeBridgeController.get_state()` so authors see engine readiness at a glance.
- **Environment Validation Feed**: Streamlit success/warning callouts generated from `logic.ApplicationLogic.validate_environment()` summarizing dependency availability across BaseMod, ModTheSpire, StSLib, and ActLikeIt paths.
- **Recent Test Snapshot**: JSON viewer mirroring `st.session_state["last_test_results"]` so the dashboard mirrors the last executed suite outcome without reopening the Tests tab.

[complete] Modal Dialogs
- **Dependency Guidance Modal**: Streamlit modal presenting BaseMod/ModTheSpire prerequisites with "Do not show again" preference stored in a persistent configuration file.

[complete] Notification System
- **Toast Notifications**: Streamlit `st.toast` wrappers delivering success/error/warning feedback from orchestrator and plugin operations.

[todo] Workflows Tab Layout
- **Workflows Parent Tab**: Streamlit tabset labeled "Workflows" that nests all workflow-specific sub-tabs and binds each to its respective orchestrator controllers (character builder, enemy authoring, relic designer, etc.), guaranteeing no workflow UI exists outside the parent tab.
