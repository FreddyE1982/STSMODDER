# StSLib Comprehensive Reference and Tutorial

## Overview
StSLib is a community-maintained library that extends BaseMod with shared mechanics, keywords, UI helpers, and utility classes. Many content mods expect StSLib to be present, and it provides reusable abstractions like custom actions, powers, damage types, and patches to base classes that enable advanced behavior. STSMODDER must understand these facilities to offer full-featured mod creation and compatibility.

## Installation
1. Download the latest StSLib release and place the JAR into the `mods/` folder with ModTheSpire.
2. Ensure BaseMod is loaded before StSLib; StSLib declares dependencies but order should still be validated.
3. Add `"modDependencies": ["stslib"]` to mods that rely on its features.

## Feature Categories

### Keywords and Mechanics
StSLib ships with several gameplay mechanics (e.g., `Freeze`, `Banish`, `Infest`, `Sealed`, etc.). Each mechanic includes pre-defined keywords and helper classes. Mods can opt-in by referencing these keywords and hooking into StSLib's effect classes instead of reinventing them.

### Extended Card Framework
- **AbstractEasyCard**: Simplifies card creation by bundling common constructor logic, damage, block, magic number handling, and automatic localization lookups.
- **AbstractEasyRelic**: Provides base functionality for relic triggers with built-in localization fields and texture loading.
- **AbstractEasyPower**: Handles power textures, localization, and stacking automatically.
- **Move-based Enemies**: Utilities for enemy intents, extra actions, and animation support.

### Utility Classes
- **Wiz**: Static helper for retrieving players/monsters, applying powers, dealing damage, etc., reducing boilerplate.
- **TextureLoader**: Simplifies loading textures with fallback and caching.
- **ConfigHelper**: Streamlines `SpireConfig` usage.
- **FastSet** and collections optimized for frequent operations.

### Patching Enhancements
StSLib introduces patches that add new hooks (e.g., `OnCreateMidCombatCard`) and improvements like dynamic badge support. Tools must recognize these to avoid duplicate patch generation.

### UI Components
- Custom orb layers, energy panels, and rendering helpers.
- Tooltip frameworks for multi-line and multi-keyword tooltips.
- Particle systems (e.g., sparkles, icicles) accessible via simple calls.

### Action Utilities
StSLib wraps numerous standard actions with helper methods (e.g., `Wiz.atb(new ApplyPowerAction(...))`) and introduces specialized actions for chaining events, handling freeze/burn counters, and more.

## Tutorial: Using StSLib in a Mod
1. **Setup Dependencies**: Add StSLib jar to your build path and declare dependency in `ModTheSpire.json`.
2. **Extend Helper Classes**: Instead of using raw `CustomCard`, extend `AbstractEasyCard` to leverage auto-generated values.
3. **Localization**: Place JSON under `resources/stslib-localization` or integrate with BaseMod's localization pipeline.
4. **Use Wiz Helpers**: Replace manual `AbstractDungeon.actionManager.addToBottom` with `Wiz.atb` or `Wiz.att`.
5. **Opt into Mechanics**: For example, apply the `Freeze` power by importing `stslib.powers.FreezePower` and referencing `StSLib.FreezeStrings` for consistent descriptions.
6. **Register Custom Tooltips**: Use `TooltipInfo` and `TooltipHelper` from StSLib to display rich descriptions.
7. **Testing**: Ensure StSLib is loaded before your mod to access all features. Use console commands to spawn cards/powers for quick checks.

## Integration Points for STSMODDER
- Provide toggles to include StSLib mechanics when designing cards or relics, automatically linking required keywords and assets.
- Offer templates that extend `AbstractEasyCard` or `AbstractEasyPower` when generating source code.
- Validate that any referenced StSLib mechanic triggers the correct dependency declaration.
- Surface documentation for StSLib-specific hooks (e.g., freeze interactions, multi-attack utilities) inside the GUI.
- Ensure plugin architecture can call StSLib helpers without tight coupling by abstracting them through interface adapters.

## Best Practices
- Keep StSLib version in sync with mods; breaking changes may alter helper class signatures.
- Avoid duplicating features already provided; reuse StSLib utilities to maintain compatibility.
- Monitor changelog for new keywords to update localization editors.
- When packaging, include StSLib in mod lists for players or warn them if missing.

## Troubleshooting
- Missing StSLib dependency leads to runtime `NoClassDefFoundError`; enforce dependency checks before launch.
- Keyword mismatches: Ensure custom keywords do not conflict with StSLib-provided ones (use `modID` namespacing).
- Texture issues: Utilize `TextureLoader` to avoid file path errors.

## Additional Resources
- StSLib GitHub README and wiki for mechanic definitions and API docs.
- Community guides demonstrating freeze and banish combos.
- Example mods like "Replay the Spire" leveraging StSLib extensively.

