# ActLikeIt Comprehensive Reference and Tutorial

## Overview
ActLikeIt is a Slay the Spire modding library focused on enabling custom acts, events, and dungeon progression tweaks. It augments BaseMod by providing map generation helpers, encounter management utilities, and hooks that bridge acts with vanilla systems. Tools targeting full modding parity must expose ActLikeIt features so creators can design entire acts without writing code manually.

## Installation
1. Download the latest ActLikeIt release JAR and place it inside the `mods/` directory.
2. Declare the dependency in `ModTheSpire.json` via `"modDependencies": ["actlikeit"]` (in addition to BaseMod/StSLib when needed).
3. Load order: BaseMod first, then StSLib (if used), ActLikeIt, followed by custom mods.

## Core Capabilities

### Custom Act Framework
- Provides `CustomDungeon` base class allowing mods to define floors, bosses, events, and map structure.
- Supports adding entire acts or injecting extra floors between vanilla acts.
- Handles dynamic floor counts, map node types, and custom icons.

### Map Generation APIs
- `ActLikeIt.dungeons.CustomDungeon` exposes methods to populate nodes using `MapRoomNode` templates.
- Utility functions for generating hallway, treasure, rest, shop, event, and elite nodes.
- Integration with BaseMod's event/monster registries to ensure new encounters appear.

### Dungeon Registration
- Mods call `DownfallMod.registerAct(CustomDungeon.class, ActInfo info)` (or equivalent API) to introduce acts.
- Provide metadata such as act ID, name, color, background textures, and boss icons.
- Supports toggling acts on/off and customizing transitions.

### Encounter Scheduling
- Helpers to define weighted encounter lists, elite pools, boss rotations, and event selection weights.
- Works with BaseMod `addMonster`/`addEvent` to ensure compatibility.

### UI and Visual Assets
- ActLikeIt expects background layers (e.g., sky, ground) in specific resolutions matching vanilla acts.
- Provides classes to manage cutscenes, map icons, and scene transitions.
- Tools should enforce asset requirements and preview the generated map.

### Additional Hooks
- Act-specific settings stored using `SpireConfig` wrappers similar to BaseMod.
- Patches for run history, compendium entries, and integration with the main menu act selection.
- Interfaces for intercepting act transitions and customizing player starting states for new acts.

## Tutorial: Building a Custom Act
1. **Define Resources**: Prepare background images (`BG`, `FG`, etc.), boss icons, map nodes, and event art.
2. **Create Dungeon Class**: Extend `CustomDungeon` and override methods such as `initialize` (build map), `generateMonsters`, `generateEvents`, and `getActID`.
3. **Register Acts**: In your mod's initialization (e.g., `receivePostInitialize`), call the ActLikeIt registration method with metadata and event handlers.
4. **Populate Encounters**: Use BaseMod to register custom monsters and events, then reference them in ActLikeIt encounter pools with weights.
5. **Customize Map**: Use helper methods to place special nodes (shops, rest sites) and define branching patterns.
6. **Integrate Story Elements**: Provide act cutscenes, event dialogues, and boss transitions using ActLikeIt-provided classes.
7. **Test**: Launch the game with ActLikeIt enabled, start a run targeting the custom act, and verify map generation, event triggers, and rewards.

## Integration Points for STSMODDER
- GUI must allow defining acts via visual map editors, automatically translating to ActLikeIt map generation code.
- Provide asset uploaders with validation for background/boss textures and map icons.
- Offer encounter pool designers with weight sliders tied to BaseMod monster/event registries.
- Manage dependency injection so generated mods automatically include ActLikeIt references and proper load order.
- Plugin architecture should expose ActLikeIt registries and runtime data (current act, node definitions) for scripted customization.

## Best Practices
- Keep act IDs unique and consistent with resource folder names.
- Provide fallback translations for act names and event text.
- Balance encounters by mixing new and existing monsters to maintain difficulty curves.
- Use ActLikeIt's helper methods instead of replicating vanilla map generation logic to remain compatible with updates.

## Troubleshooting
- Map generation errors often stem from missing nodes; ensure each column has at least one path to the next.
- Asset loading failures arise from incorrect paths or dimensions; validate file structure.
- Encounter pools referencing unregistered monsters or events cause runtime exceptions; cross-check BaseMod registries first.

## Additional Resources
- ActLikeIt GitHub documentation and sample custom act mods.
- Community tutorials on map layout design and act balancing.
- Downfall mod source code showcasing advanced usage of ActLikeIt features.

