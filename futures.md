# Futures Roadmap

## Global Plugin Architecture Expansion
- **Purpose**: Provide a single extensibility surface that exposes BaseMod, ModTheSpire, StSLib, and ActLikeIt APIs to external plugins. This enables third parties to script new workflows, add validators, or extend the GUI without modifying core code.
- **Usage Notes**:
  - Define a plugin registry that discovers plugins from a designated directory and injects them with handles to subsystems (registry manager, launch manager, act editor, etc.).
  - Expose typed interfaces for all major systems: content registries, localization manager, asset pipeline, launch orchestration, validation framework.
  - Provide lifecycle callbacks (`onLoad`, `onBeforeExport`, `onAfterLaunch`, etc.) so plugins can react to user actions.
  - Ensure permission controls and sandboxing to prevent malicious plugins from corrupting projects.
  - Document plugin API in dedicated developer guide once core systems solidify.

## Repository Cloning Automation
- **Purpose**: Automate cloning of upstream reference repositories (BaseMod, ModTheSpire, StSLib, ActLikeIt) into `research/repos` for offline inspection and keeping parity with upstream changes.
- **Usage Notes**: Implement a research sync script that fetches or updates repositories, logs commit hashes, and caches documentation snapshots for traceability.

## Research Data Normalization
- **Purpose**: Convert research markdown files into structured data (JSON/YAML) consumable by the application for inline help and validation rules.
- **Usage Notes**: Build a parser that extracts requirements (e.g., asset sizes, hook names) and populates configuration tables used by validators and tooltips.

