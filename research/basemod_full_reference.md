# BaseMod Comprehensive Reference and Tutorial

## Overview
BaseMod is the de-facto modding API for Slay the Spire. It augments the ModTheSpire loader with an extensible subscription model that exposes lifecycle hooks, registries for custom content, shared utilities, and debugging aids like the in-game developer console. Understanding BaseMod is essential for building non-trivial mods or tooling (like STSMODDER) because almost every custom game element flows through its registration and hook mechanisms.

## Installation and Bootstrapping
1. **Prerequisites**: Install Java (JDK 8+), obtain the Slay the Spire modding base via Steam, and download ModTheSpire.
2. **Add BaseMod**: Drop the BaseMod JAR into the `mods/` directory used by ModTheSpire.
3. **Declare Dependency**: In your mod's `ModTheSpire.json`, add `"modDependencies": ["basemod"]` to enforce load ordering.
4. **Initialize**: Implement a class annotated with `@SpireInitializer` or extend `basemod.BaseMod` and call `BaseMod.subscribe()` to register your mod with the event bus.

### Example Mod Skeleton
```java
@SpireInitializer
public class ExampleMod implements EditCardsSubscriber, PostInitializeSubscriber {
    public static void initialize() {
        new ExampleMod();
    }

    public ExampleMod() {
        BaseMod.subscribe(this);
    }

    @Override
    public void receivePostInitialize() {
        // UI setup or localization
    }

    @Override
    public void receiveEditCards() {
        // register cards here
    }
}
```

## Core Concepts and Systems

### Subscriber Interfaces and Lifecycle Hooks
BaseMod exposes numerous interfaces representing hook points in Slay the Spire's runtime. The most common include:
- `EditCardsSubscriber`, `EditRelicsSubscriber`, `EditStringsSubscriber`, `EditKeywordsSubscriber`: run during the editing stage before the game fully initializes content.
- `PostInitializeSubscriber`: run after all mods have registered, ideal for UI, badges, and mod settings.
- `OnStartBattleSubscriber`, `OnCardUseSubscriber`, `PostDrawSubscriber`, etc.: respond to gameplay events.
- `AddAudioSubscriber`, `AddColorSubscriber`, `PostPowerApplySubscriber`, and many others for specialized needs.

Subscribers can be combined by implementing multiple interfaces in the same class. BaseMod automatically invokes the matching methods at the correct time.

### Content Registries
BaseMod maintains registries for most modded content types:
- **Cards**: `BaseMod.addCard(AbstractCard card);` plus `UnlockTracker.markCardAsSeen` for compendium visibility.
- **Relics**: `BaseMod.addRelicToCustomPool(AbstractRelic relic, AbstractCard.CardColor color);` or add to base pools.
- **Potions**: `BaseMod.addPotion(Class<? extends AbstractPotion> potionClass, Color liquid, Color hybrid, Color spots, String potionID);`
- **Powers**: use `BaseMod.addPowerJSON` and register via JSON descriptors, or rely on `BaseMod.addPower` for dynamic addition.
- **Events**: `BaseMod.addEvent(String eventID, Class<? extends AbstractEvent> eventClass, String... actIDs);`
- **Monsters and Encounters**: `BaseMod.addMonster` and `BaseMod.addBoss`, plus map node overrides.
- **Keywords**: register from JSON via `BaseMod.addKeyword` or `BaseMod.loadCustomStrings`.

Each registry enforces unique IDs and may require color associations or additional metadata. STSMODDER must validate ID formats (`modID:ThingName`) and guarantee dependencies (e.g., custom colors before cards).

### Custom Colors and Rarity Pools
BaseMod allows mods to introduce new card colors (for characters) using `BaseMod.addColor`. This call expects card back textures, energy orb sprites, and attack/skill/power backgrounds in multiple sizes (e.g., `512x512` and `1024x1024`). Cards tied to the new color automatically appear under that pool, while relics can be assigned via `BaseMod.addRelicToCustomPool`.

### Localization and Custom Strings
Localization strings are loaded via JSON using methods like `BaseMod.loadCustomStrings` and `BaseMod.loadCustomStringsFile`. Each string type (CardStrings, RelicStrings, EventStrings, MonsterStrings, UIStrings, etc.) has expected JSON schema. During `receiveEditStrings`, mods call these methods pointing to language-specific resource paths. STSMODDER must provide editors that generate valid JSON with fallback languages.

### Keywords System
Keywords are defined in JSON arrays with id, proper name, and synonyms. BaseMod enforces lowercase IDs. Example snippet:
```json
[
  {
    "PROPER_NAME": "Spark",
    "NAMES": ["spark", "sparks"],
    "DESCRIPTION": "Applies a stacking lightning effect."
  }
]
```
Use `BaseMod.addKeyword(modID, keywordID, names, description);`. Tools should ensure keywords referenced by cards are registered and provide alias linting.

### Developer Console and Commands
BaseMod ships with an in-game developer console. Mods can define console commands via `DevConsole.registerCommand`. Commands extend `ConsoleCommand` and enable debugging features (e.g., spawn cards, set stats). STSMODDER's launch workflow must expose toggles for enabling the console and listing available commands.

### Save Data and Config
BaseMod provides `SpireConfig` for storing persistent mod configuration. Config files live under `ModID/Config`. Example usage:
```java
SpireConfig config = new SpireConfig("ExampleMod", "config", defaults);
boolean enabled = config.getBool("enableFeature");
config.setBool("enableFeature", true);
config.save();
```
A GUI should automatically surface these settings with validation and persistence.

## Advanced Hook Coverage
- **Combat Events**: `OnCardUseSubscriber`, `PostBattleSubscriber`, `OnPlayerLoseBlockSubscriber`, etc.
- **Rendering Hooks**: `PostRenderSubscriber`, `RenderSubscriber` to draw overlays.
- **Dungeon Generation**: `PostCreateStartingDeckSubscriber`, `PostCreateStartingRelicsSubscriber` for custom character loadouts.
- **Rewards and Screens**: Hooks like `PostCreateShopRelic` allow customizing shops, while `PreStartGameSubscriber` influences run initialization.

A comprehensive tool must cross-reference these hooks when users configure behaviors, ensuring visual editors map to the correct subscriber implementations.

## Tutorial Workflow (End-to-End)
1. **Create Mod Skeleton**: Use ModTheSpire's template with `@SpireInitializer`.
2. **Define Mod ID**: Provide a lowercase ID and register using `BaseMod.subscribe`.
3. **Load Localization**: Implement `receiveEditStrings` to load JSON strings per language.
4. **Register Keywords**: Parse keywords JSON and call `BaseMod.addKeyword`.
5. **Add Custom Color (Optional)**: Provide textures and call `BaseMod.addColor`.
6. **Create Content**: Cards, relics, events, potions, powers, characters, etc., via the relevant subscribers.
7. **Implement Hooks**: Add gameplay logic by overriding card methods or subscribing to events.
8. **Testing**: Launch via ModTheSpire with BaseMod and dependencies enabled. Use the dev console and debug commands.
9. **Packaging**: Ensure `ModTheSpire.json` includes dependencies and versioning.

## Best Practices
- Maintain unique IDs using `modID:` prefix to avoid collisions.
- Keep JSON resources under `src/main/resources` using the language directories `eng`, `zhs`, etc.
- Use `UnlockTracker` APIs to manage logbook visibility.
- Provide fallback localization for default language to prevent runtime errors.
- Validate asset resolutions: card faces (250×190), portraits `_p` (500×380), energy orbs (96×96 for UI), etc.
- Ensure hooking logic respects thread safety and avoids heavy operations in render hooks.

## Integration Points for STSMODDER
- **Registry Management**: Provide GUI editors that output JSON and class skeletons while ensuring BaseMod API calls are generated.
- **Hook Visualizers**: Map GUI events to BaseMod interfaces, allowing plugin scripts to inject custom logic.
- **Dependency Validation**: Confirm BaseMod is present in the launch configuration and warn if version mismatches occur.
- **Plugin Exposure**: Wrap BaseMod objects (cards, relics, actions) in an API layer accessible from the global plugin architecture so advanced users can script behaviors without editing core code.

## Troubleshooting
- Missing textures cause runtime `NullPointerException`; double-check resource paths.
- Forgotten `BaseMod.subscribe(this)` means none of your hooks fire.
- Keyword JSON errors manifest as localization failures; validate JSON with strict schema.
- Outdated BaseMod versions may lack newer hooks—check release notes and update dependencies accordingly.

## Additional Learning Resources
- Official GitHub wiki articles (Custom Cards, Characters, Strings, Keywords, Powers, Events).
- Community tutorials on card design patterns, custom actions, and balancing.
- Example mods in the BaseMod repository demonstrating complex integrations (e.g., The Guard, ReplayTheSpire).

