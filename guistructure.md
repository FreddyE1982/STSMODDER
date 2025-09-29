# GUI Structure Blueprint

[complete] Build a launch configuration sidebar capturing Java home, ModTheSpire jar location, BaseMod/STSLib/ActLikeIt toggles, and validation status badges so users can confirm readiness before exporting mods.

[complete] Provide a central orchestration dashboard with tabs for "JPype Bridge", "Library Status", "Plugin Registry", and "Test Suites" to reflect the runtime lifecycle of the orchestrator and expose quick actions for starting or shutting down the JVM, running integration tests, and inspecting plugin contributions.

[complete] Introduce a top-level "Status" tab ahead of the existing runtime workflow tabs so environment validation, JVM state metrics, and the latest test results move out of the sidebar into a dedicated workspace, with guielements.md kept in sync for the consolidated layout.

[todo] Implement a Streamlit-based log viewer panel that streams structured log records (JPype, plugin system, GUI interactions) with filtering controls for severity, module, and timeframe.

[complete] Create a contextual helper modal describing BaseMod requirements and StSLib dependency interplay, ensuring compliance with the AGENTS instructions about GUI-first documentation and offering a "Do not show again" persistence toggle.

[todo] Reserve a dedicated area for ModTheSpire launch shortcuts, including jar selection, mod enablement toggles, and validation warnings for missing dependencies, enabling seamless alignment with the development plan's ModTheSpire integration objectives.

[todo] Define a top-level "Workflows" tab containing sub-tabs for every authoring workflow (characters, enemies, cards, relics, potions, acts, composite mods, and future additions), ensuring no workflow panels appear outside this hierarchy and documenting the binding expectations for each sub-tab.

[todo] Draft the "Workflows › Character" sub-tab layout with discrete sections for BaseMod registration metadata (character title/class strings, enum binding, custom color picker, select button path, portrait path) and surface plugin-published validators alongside the form.
> # Requirements
> 1. (prereq) Register a new custom color with BaseMod for the player - take a look here to see how (https://github.com/daviscook477/BaseMod/wiki/Custom-Colors)
> 2. Define a custom player class that has a public static CharSelectInfo getLoadout() method
> 3. Register the custom player with BaseMod
>
> # API
> Note that `addCharacter` should only be called in the `receiveEditCharacters` callback of `EditCharactersSubscriber`.
>
> `addCharacter(Class characterClass, String titleString, String classString, String color, String selectText, String selectButton, String portrait, String characterID)`
> * `character` - An instance of your character
> * `color` - The name of the custom color for this character, e.g. `MY_CUSTOM_COLOR.toString()` where `MY_CUSTOM_COLOR` is the enum value for this character's color
> * `selectButtonPath` - The path to the select button texture (starting at the root of your jar)
> * `portraitPath` - The path to your character select portrait texture (starting at the root of your jar) (size: 1920px x 1200px)
> * `characterID` - Should be `MY_PLAYER_CLASS` where `MY_PLAYER_CLASS` is the enum value for this character's class

[todo] Plan an assets & animation column within the Character workflow featuring uploaders/previews for shoulders, corpse art, and spine atlas/json plus energy/dialog offsets, wired to plugin-driven validation states.
> public class MyCharacter extends CustomPlayer {
> public static final int ENERGY_PER_TURN = 3; // how much energy you get every turn
> public static final String MY_CHARACTER_SHOULDER_2 = "img/char/shoulder2.png"; // campfire pose
> public static final String MY_CHARACTER_SHOULDER_1 = "img/char/shoulder1.png"; // another campfire pose
> public static final String MY_CHARACTER_CORPSE = "img/char/corpse.png"; // dead corpse
> public static final String MY_CHARACTER_SKELETON_ATLAS = "img/char/skeleton.atlas"; // spine animation atlas
> public static final String MY_CHARACTER_SKELETON_JSON = "img/char/skeleton.json"; // spine animation json
>
> public MyCharacter (String name) {
> super(name, MyPlayerClassEnum.MY_PLAYER_CLASS);
>
> this.dialogX = (this.drawX + 0.0F * Settings.scale); // set location for text bubbles
> this.dialogY = (this.drawY + 220.0F * Settings.scale); // you can just copy these values
>
> initializeClass(null, MY_CHARACTER_SHOULDER_2, // required call to load textures and setup energy/loadout
> MY_CHARACTER_SHOULDER_1,
> MY_CHARACTER_CORPSE,
> getLoadout(), 20.0F, -10.0F, 220.0F, 290.0F, new EnergyManager(ENERGY_PER_TURN));
>
> loadAnimation(MY_CHARACTER_SKELETON_ATLAS, MY_CHARACTER_SKELETON_JSON, 1.0F); // if you're using modified versions of base game animations or made animations in spine make sure to include this bit and the following lines

[todo] Introduce a loadout configuration region in the Character sub-tab combining selectors for starting deck/relic references, stat inputs, and CharSelectInfo preview copy while explicitly pointing users back to the Cards/Relics workflows for new content creation.
> public static ArrayList<String> getStartingDeck() { // starting deck 'nuff said
> ArrayList<String> retVal = new ArrayList<>();
> retVal.add("MyCard0");
> retVal.add("MyCard0");
> retVal.add("MyCard0");
> retVal.add("MyCard0");
> retVal.add("MyCard1");
> retVal.add("MyCard1");
> retVal.add("MyCard1");
> retVal.add("MyCard1");
> retVal.add("MyCard2");
> return retVal;
> }
>
> public static ArrayList<String> getStartingRelics() { // starting relics - also simple
> ArrayList<String> retVal = new ArrayList<>();
> retVal.add("MyRelic");
> UnlockTracker.markRelicAsSeen("MyRelic");
> return retVal;
> }
>
> public static final int STARTING_HP = 75;
> public static final int MAX_HP = 75;
> public static final int STARTING_GOLD = 99;
> public static final int HAND_SIZE = 5;
>
> public static CharSelectInfo getLoadout() { // the rest of the character loadout so includes your character select screen info plus hp and starting gold
> return new CharSelectInfo("My Character", "My character is a person from the outer worlds. He makes magic stuff happen.",
> STARTING_HP, MAX_HP, ORB_SLOTS, STARTING_GOLD, HAND_SIZE,
> this, getStartingRelics(), getStartingDeck(), false);
> }
