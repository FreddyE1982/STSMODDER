# Futures Roadmap

## Modular Content Authoring
Implement plugin-driven content authoring wizards that align BaseMod hook coverage with GUI workflows, enabling future extensions to introduce new card behaviors without modifying core logic. Each plugin should define metadata (name, version, capabilities) and expose registration callbacks consumable by the global plugin manager.

## Automated Asset Validation
Design a validation microservice that cross-checks asset dimensions, keyword consistency, and localization coverage against BaseMod requirements before export. Integrate the service through the planned REST API and provide GUI dashboards for results inspection.

## Cross-Library Compatibility Testing
Extend the JPype test orchestrator with scenario scripting so testers can define ActLikeIt dungeon progressions, BaseMod hook invocations, and StSLib mechanic toggles in YAML. The orchestrator will compile these scripts into Java method calls via JPype, capturing metrics for later analytics.

## Plugin Marketplace
Create a plugin packaging format (signed zip) allowing community distribution. The plugin manager should verify signatures, resolve dependencies, and sandbox plugin execution while still exposing the complete repository API through controlled facades.
