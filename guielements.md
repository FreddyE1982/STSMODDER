# GUI Elements Registry

[complete] Sidebar Form Fields
- **Java Home Input**: Text input bound to `logic.runtime_config.java_home`. Validates path existence and ensures the JVM library can be resolved.
- **ModTheSpire Jar Selector**: File uploader bound to `logic.runtime_config.modthespire_jar`. Triggers validation of jar metadata via the JPype orchestrator.
- **Library Toggles**: Checkbox group reflecting BaseMod, STSLib, and ActLikeIt activation states, bound to `logic.runtime_config.enabled_libraries`.

[complete] Main Dashboard Components
- **JPype Bridge Status Card**: Displays current JVM state (stopped, starting, running, shutting down) and exposes actions to start/stop through `logic.JPypeBridgeController`.
- **Plugin Registry Table**: Interactive table listing registered plugins, exposed symbols, and health indicators as provided by `plugin_manager.PluginManager`.
- **Test Suite Runner Panel**: Buttons to trigger baseline smoke tests and mod-specific regression suites managed by `jpypetestorchestrator.JPypeTestOrchestrator`.

[complete] Modal Dialogs
- **Dependency Guidance Modal**: Streamlit modal presenting BaseMod/ModTheSpire prerequisites with "Do not show again" preference stored in a persistent configuration file.

[complete] Notification System
- **Toast Notifications**: Streamlit `st.toast` wrappers delivering success/error/warning feedback from orchestrator and plugin operations.
