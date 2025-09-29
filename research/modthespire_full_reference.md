# ModTheSpire Comprehensive Reference and Tutorial

## Overview
ModTheSpire (MTS) is the primary mod loader for Slay the Spire. It bootstraps JVM instrumentation, loads mod JARs, handles dependency resolution, and provides patching annotations (SpirePatch) that allow mods to inject code into the base game. STSMODDER must reproduce its configuration UI and automation to guarantee that players can assemble mod lists, manage load order, and launch the game seamlessly.

## Installation Workflow
1. **Download MTS**: Obtain the latest release and place `ModTheSpire.jar` in the Slay the Spire directory.
2. **mods Folder**: Create a `mods/` folder next to the JAR. Drop BaseMod, StSLib, ActLikeIt, and custom mod JARs inside.
3. **Launch**: Run `java -jar ModTheSpire.jar` (or use bundled scripts). The launcher UI allows selecting mods, toggling debug, and specifying Java args.
4. **Command Line**: `java -jar ModTheSpire.jar --mods BaseMod.jar,MyMod.jar --enable Beta` etc. STSMODDER should wrap both UI and command-line flows.

## Anatomy of an MTS Mod
Every mod is a fat JAR containing:
- Compiled classes targeting Java 8 (or compatible).
- `ModTheSpire.json` manifest describing name, author, version, dependencies, and optional description/credits.
- Resource files (images, JSON, localization) under `resources/` or `src/main/resources` when using Gradle.

### ModTheSpire.json Keys
```json
{
  "modid": "examplemod",
  "name": "Example Mod",
  "author_list": ["You"],
  "description": "Adds cards and relics.",
  "version": "1.0.0",
  "mts_version": "3.30.0",
  "sts_version": "12-22-2020",
  "dependencies": ["basemod"],
  "optional_dependencies": ["stslib"],
  "modDependencies": ["basemod"],
  "update_json": "https://.../update.json"
}
```
- `modid` must be lowercase and unique.
- `mts_version`/`sts_version` ensure compatibility.
- `dependencies` vs `modDependencies`: loader-level vs BaseMod registries.

## Patching System
MTS leverages `javassist` to patch base game classes. The patching pipeline involves scanning for annotations at runtime and applying transformations in load order.

### Patch Annotations
- `@SpirePatch(clz = X.class, method = "methodName")`: Basic patch targeting specific methods.
- `@SpireInsertPatch(locator = ...)`: Insert custom code at calculated line positions.
- `@SpirePrefixPatch`, `@SpirePostfixPatch`, `@SpireInsertPatch`: run before, after, or within the target method.
- `@SpireInstrumentPatch`: Use `ExprEditor` to rewrite bytecode expressions.
- `@SpireEnum`, `@SpireField`: Inject new enum values or fields.

### Example Prefix Patch
```java
@SpirePatch(clz = AbstractPlayer.class, method = "useCard")
public class ExampleUseCardPatch {
    @SpirePrefixPatch
    public static void beforeUse(AbstractPlayer __instance, AbstractCard card, AbstractMonster monster, int energyOnUse) {
        // Custom logic before the card resolves
    }
}
```

### Locator Example
```java
@SpireInsertPatch(locator = Locator.class)
public static void insert(AbstractPlayer __instance) {
    // Runs at the located line
}

private static class Locator extends SpireInsertLocator {
    @Override
    public int[] Locate(CtBehavior ctMethodToPatch) throws Exception {
        Matcher matcher = new Matcher.MethodCallMatcher(AbstractDungeon.class, "onModifyPower");
        return LineFinder.findInOrder(ctMethodToPatch, matcher);
    }
}
```

STSMODDER must surface patch creation via visual editors and templates, generating these classes automatically.

## Loader Lifecycle
1. **Manifest Parsing**: Reads `ModTheSpire.json` for each JAR.
2. **Dependency Resolution**: Orders mods, ensuring required dependencies load earlier.
3. **ClassLoader Setup**: Each mod obtains a `URLClassLoader` with parent-first rules.
4. **Annotation Scan**: All `@Spire*` annotations are processed.
5. **Mod Initialization**: `@SpireInitializer` methods or `BaseMod.subscribe` flows run.
6. **Game Launch**: Once patches apply, the vanilla game is started inside the instrumented JVM.

## CLI Arguments
- `--mods <list>`: Comma-separated JAR names.
- `--modfolder <path>`: Alternative mods directory.
- `--config <file>`: Load a saved configuration.
- `--beta`, `--daily`: Launch in beta or daily mode.
- `--help`: Print usage.
- `--enableMods`/`--disableMods`: Quick toggles for saved configs.
- `--skip-launcher`: Immediately launch using saved configuration.

STSMODDER should serialize launch profiles matching these arguments and allow headless automation.

## Mod Configuration Files
MTS stores configuration in `preferences/ModTheSpire`. Each mod may also use `SpireConfig` (provided by BaseMod) or custom config files. Provide import/export tooling so users can share setups.

## Debugging and Logs
- Standard output and error logs go to `ModTheSpire.log`.
- The loader exposes toggles for enabling debug logging and instrumentation dumps.
- When patches fail, MTS prints stack traces referencing CtBehavior names; tools should parse and present them in a friendly UI.

## Update JSON
MTS supports remote update manifests where `update_json` points to metadata describing latest versions and download URLs. STSMODDER should monitor these endpoints to alert users about outdated mods.

## Tutorial: Building a Mod for MTS
1. **Project Setup**: Use Gradle with `sourceCompatibility = 1.8`. Depend on MTS and BaseMod via local libs.
2. **Create Manifest**: Fill out `ModTheSpire.json` with dependencies and metadata.
3. **Implement Patches**: Annotate patch classes as needed.
4. **Compile & Package**: Use `gradle jar` to produce a mod JAR including resources.
5. **Deploy**: Copy to `mods/`. Launch ModTheSpire and select the mod.
6. **Test**: Use BaseMod console and MTS logs to verify patch behavior.

## Integration Requirements for STSMODDER
- Provide a launch dashboard replicating MTS features (mod selection, order management, Java args, runtime flags).
- Manage `ModTheSpire.json` creation and validation inside the GUI, ensuring dependencies and versions align.
- Offer patch authoring tools with automated locator suggestions and preview of transformed bytecode when possible.
- Integrate update checking and log parsing for real-time feedback.
- Ensure plugin architecture can hook into loader events, exposing mod metadata, patch graph, and launch states.

## Troubleshooting Tips
- `javassist.NotFoundException`: Usually missing classpath entries; ensure required game or library classes exist.
- ClassCast or NoClassDefFound errors: Check load order and dependencies.
- Update loops: Validate `update_json` format and HTTP availability.

## Further Reading
- Official ModTheSpire GitHub README and wiki.
- Example patching tutorials by community members (insertion, instrumentation, adding UI).
- Source code of the loader (open source) for advanced customization.

