# Development Plan

## Research Excerpts and Derived Tasks
The following excerpts are copied directly from the research documents to justify actionable tasks.

### BaseMod Responsibilities
BaseMod maintains registries for most modded content types:
- **Cards**: `BaseMod.addCard(AbstractCard card);` plus `UnlockTracker.markCardAsSeen` for compendium visibility.
- **Relics**: `BaseMod.addRelicToCustomPool(AbstractRelic relic, AbstractCard.CardColor color);` or add to base pools.
- **Potions**: `BaseMod.addPotion(Class<? extends AbstractPotion> potionClass, Color liquid, Color hybrid, Color spots, String potionID);`
- **Powers**: use `BaseMod.addPowerJSON` and register via JSON descriptors, or rely on `BaseMod.addPower` for dynamic addition.
- **Events**: `BaseMod.addEvent(String eventID, Class<? extends AbstractEvent> eventClass, String... actIDs);`
- **Monsters and Encounters**: `BaseMod.addMonster` and `BaseMod.addBoss`, plus map node overrides.
- **Keywords**: register from JSON via `BaseMod.addKeyword` or `BaseMod.loadCustomStrings`.

[todo] Design GUI registries mirroring BaseMod content types with validation for IDs, asset presence, and dependency ordering. Ensure guistructure.md references the workflow before implementation.

### ModTheSpire Loader Expectations
ModTheSpire (MTS) is the primary mod loader for Slay the Spire. It bootstraps JVM instrumentation, loads mod JARs, handles dependency resolution, and provides patching annotations (SpirePatch) that allow mods to inject code into the base game. STSMODDER must reproduce its configuration UI and automation to guarantee that players can assemble mod lists, manage load order, and launch the game seamlessly.

[todo] Implement a launch management module that encapsulates ModTheSpire configuration, including mod selection, dependency ordering, command-line argument generation, and profile persistence. Update guistructure.md accordingly before coding UI.

### StSLib Utility Coverage
StSLib ships with several gameplay mechanics (e.g., `Freeze`, `Banish`, `Infest`, `Sealed`, etc.). Each mechanic includes pre-defined keywords and helper classes. Mods can opt-in by referencing these keywords and hooking into StSLib's effect classes instead of reinventing them.

[todo] Extend registry and validation logic to surface StSLib mechanics as optional modules, automatically managing keyword inclusion and dependency declarations.

### ActLikeIt Custom Act Support
ActLikeIt is a Slay the Spire modding library focused on enabling custom acts, events, and dungeon progression tweaks. It augments BaseMod by providing map generation helpers, encounter management utilities, and hooks that bridge acts with vanilla systems. Tools targeting full modding parity must expose ActLikeIt features so creators can design entire acts without writing code manually.

[todo] Plan a visual act editor that outputs ActLikeIt-compliant map generation code, asset packaging, and encounter scheduling.

