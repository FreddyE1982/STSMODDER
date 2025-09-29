# Futures Roadmap

## Modular Content Authoring
Implement plugin-driven content authoring wizards that align BaseMod hook coverage with GUI workflows, enabling future extensions to introduce new card behaviors without modifying core logic. Each plugin should define metadata (name, version, capabilities) and expose registration callbacks consumable by the global plugin manager.

## Automated Asset Validation
Design a validation microservice that cross-checks asset dimensions, keyword consistency, and localization coverage against BaseMod requirements before export. Integrate the service through the planned REST API and provide GUI dashboards for results inspection.

## Cross-Library Compatibility Testing
Extend the JPype test orchestrator with scenario scripting so testers can define ActLikeIt dungeon progressions, BaseMod hook invocations, and StSLib mechanic toggles in YAML. The orchestrator will compile these scripts into Java method calls via JPype, capturing metrics for later analytics.

## Plugin Marketplace
Create a plugin packaging format (signed zip) allowing community distribution. The plugin manager should verify signatures, resolve dependencies, and sandbox plugin execution while still exposing the complete repository API through controlled facades.

## Status Telemetry Integrations
Extend the Status tab through plugin-provided panels that can subscribe to lifecycle events from `plugin_manager.PluginManager.dispatch_event`. Each plugin should be able to register custom render callbacks contributing Streamlit components to a shared grid, enabling surfaced health checks for BaseMod asset validation, ModTheSpire launch readiness, and StSLib mechanic coverage without touching the core GUI implementation.

## Workflow Hub Architecture
Document and implement a Workflows parent tab that dynamically enumerates workflow sub-tabs supplied by core modules and plugins. Provide plugin APIs so extensions can inject new workflow tabs, register dependency metadata, and expose Streamlit renderers while inheriting shared validation and persistence services.

## Orchestrator Extension Points
Encapsulate ModOrchestrator hooks so plugins can register new content generators (relics, potions, events) by contributing dataclass serializers and Java templates, ensuring the core builder automatically incorporates plugin-defined assets, localization bundles, and build-time validations without manual wiring.
