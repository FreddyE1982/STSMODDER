# Development Plan

[complete] Integrate Java 8 and ModTheSpire v3.1.0+ prerequisites into the JPype testing and runtime orchestration, ensuring the tooling enforces these requirements before attempting to interact with BaseMod, STSLib, ModTheSpire, or ActLikeIt.
> # BaseMod #
> BaseMod provides a number of hooks and a console.
> 
> ![Developer Console](github_resources/console.png)
> 
> ## Requirements ##
> #### General Use ####
> * **Java 8 (do not use Java 9 - ModTheSpire does not work on Java 9)**
> * ModTheSpire v3.1.0+ (https://github.com/kiooeht/ModTheSpire/releases)
> 
> #### Development ####
> * Java 8
> * Maven
> * ModTheSpire (https://github.com/kiooeht/ModTheSpire)
> 
> ## Building ##
> 1. (If you haven't already) `mvn install` ModTheSpire Altenatively, modify pom.xml to point to a local copy of the JAR.
> 2. Copy `desktop-1.0.jar` from your Slay the Spire folder into `../lib` relative to the repo.
> 3. Run `mvn package`

[todo] Model ModTheSpire launch integration so the GUI can eventually orchestrate one-click launching and jar validation, leveraging ModTheSpire's expectation of `desktop-1.0.jar` and ensuring plugin access to all runtime controls.
> # ModTheSpire
> ModTheSpire is a mod loader for Slay the Spire that allows players to play with community-made mods.
> 
> ## Requirements
> * Java 8 (64-bit)
> * desktop-1.0.jar (from Slay the Spire install directory)
> 
> ## Usage
> 1. Place ModTheSpire.jar into the Slay the Spire install directory.
> 2. Run ModTheSpire.jar to load and manage mods.

[todo] Reflect StSLib shared mechanics availability inside both the plugin exposure layer and the JPype bridge so cross-mod keyword expectations can be validated during testing.
> # StSLib
> Shared library for Slay the Spire mods.  Adds new mechanics, powers, relics, events, and UI elements.
> 
> ## Dependencies
> * BaseMod
> * Java 8

[todo] Capture ActLikeIt runtime behaviors and provide plugin hooks so behavior emulation remains possible when orchestrating tests that require dungeon or act switching logic.
> # ActLikeIt
> ActLikeIt is an extension to the Slay the Spire modding API that allows modders to add new Acts to the game.

[todo] Enhance the Status tab to provide remediation guidance for dependency readiness, leveraging plugin_manager hooks so plugins can append detectors covering BaseMod installation and ModTheSpire runtime expectations.
> ## Installation ##
> 1. Copy `target/BaseMod.jar` to your ModTheSpire mods directory. Maven will automatically do this after packaging if your mods directory is located at `../_ModTheSpire/mods` relative to the repo.
>
> ### Running Mods ###
> 1. Run ModTheSpire.
>     * For Windows, run `MTS.cmd`.
>     * For Linux, run `MTS.sh`.
>     * Or run `ModTheSpire.jar` with Java 8.
> 2. Select the mod(s) you want to use.
> 3. Press 'Play'.

[complete] Ensure the application embeds JPype lifecycle management to start and stop the JVM exactly once per session and expose the resulting bridge to plugin consumers for test orchestration, referencing JPype's recommended initialization pattern.
> JPype is an effort to allow python programs full access to Java class libraries.  This is achieved not through re-implementing Python, as Jython/JPython does, but rather through interfacing at the native level in both Virtual Machines.  Eventually, it should be possible to replace Java with Python in many, though not all, situations. (If you are curious about the project, and want to join the JPype project, please join the project on github).
> 
> JPype is currently in development.  The latest release of JPype is 1.4.1.  Please check the github issues for the latest status on new features and bugs.
> 
> Quick start
> -----------
> * Install Java and make sure the JVM library (jvm.dll, libjvm.dylib, libjvm.so) is in your path.
> * Install JPype using ``pip``.
> * Start JVM with ``jpype.startJVM()``.
> * Access Java classes.
> * Shutdown JVM with ``jpype.shutdownJVM()``.

[complete] Build the GUI orchestration on Streamlit with modular panels for configuration, runtime status, and validation dashboards, ensuring every GUI element is catalogued in guistructure.md, guielements.md, and mirrored via future REST endpoints.

[complete] Document and implement a global plugin system that exposes every runtime symbol—classes, functions, instances, configuration values—so plugin authors can extend the tool without monkey patching.

[todo] After delivering the initial orchestration stack, expand research on BaseMod hooks, StSLib additions, and ActLikeIt act definitions to append workflow-specific tasks here.

[todo] Architect the unified "Workflows" parent tab with sub-tabs for every authoring flow, aligning GUI, REST, and plugin hooks so workflow logic lives exclusively within this hierarchy and is fully discoverable via the plugin manager registry.
