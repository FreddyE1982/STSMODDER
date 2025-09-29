# GUI Structure Blueprint

[complete] Build a launch configuration sidebar capturing Java home, ModTheSpire jar location, BaseMod/STSLib/ActLikeIt toggles, and validation status badges so users can confirm readiness before exporting mods.

[complete] Provide a central orchestration dashboard with tabs for "JPype Bridge", "Library Status", "Plugin Registry", and "Test Suites" to reflect the runtime lifecycle of the orchestrator and expose quick actions for starting or shutting down the JVM, running integration tests, and inspecting plugin contributions.

[complete] Introduce a top-level "Status" tab ahead of the existing runtime workflow tabs so environment validation, JVM state metrics, and the latest test results move out of the sidebar into a dedicated workspace, with guielements.md kept in sync for the consolidated layout.

[todo] Implement a Streamlit-based log viewer panel that streams structured log records (JPype, plugin system, GUI interactions) with filtering controls for severity, module, and timeframe.

[complete] Create a contextual helper modal describing BaseMod requirements and StSLib dependency interplay, ensuring compliance with the AGENTS instructions about GUI-first documentation and offering a "Do not show again" persistence toggle.

[todo] Reserve a dedicated area for ModTheSpire launch shortcuts, including jar selection, mod enablement toggles, and validation warnings for missing dependencies, enabling seamless alignment with the development plan's ModTheSpire integration objectives.

[todo] Define a top-level "Workflows" tab containing sub-tabs for every authoring workflow (characters, enemies, cards, relics, potions, acts, composite mods, and future additions), ensuring no workflow panels appear outside this hierarchy and documenting the binding expectations for each sub-tab.
