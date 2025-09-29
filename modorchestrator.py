"""Generate full Slay the Spire mod projects from GUI-authored definitions."""
from __future__ import annotations

import json
import logging
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List

from plugin_manager import PluginManager


class ModOrchestrator:
    """Translate GUI data into a fully realized mod project structure."""

    _CARD_TYPE_MAP: Dict[str, str] = {
        "ATTACK": "AbstractCard.CardType.ATTACK",
        "SKILL": "AbstractCard.CardType.SKILL",
        "POWER": "AbstractCard.CardType.POWER",
        "STATUS": "AbstractCard.CardType.STATUS",
        "CURSE": "AbstractCard.CardType.CURSE",
    }
    _CARD_RARITY_MAP: Dict[str, str] = {
        "BASIC": "AbstractCard.CardRarity.BASIC",
        "COMMON": "AbstractCard.CardRarity.COMMON",
        "UNCOMMON": "AbstractCard.CardRarity.UNCOMMON",
        "RARE": "AbstractCard.CardRarity.RARE",
        "SPECIAL": "AbstractCard.CardRarity.SPECIAL",
        "CURSE": "AbstractCard.CardRarity.CURSE",
    }
    _CARD_TARGET_MAP: Dict[str, str] = {
        "ENEMY": "AbstractCard.CardTarget.ENEMY",
        "ALL_ENEMY": "AbstractCard.CardTarget.ALL_ENEMY",
        "SELF": "AbstractCard.CardTarget.SELF",
        "SELF_AND_ENEMY": "AbstractCard.CardTarget.SELF_AND_ENEMY",
        "NONE": "AbstractCard.CardTarget.NONE",
        "ALL": "AbstractCard.CardTarget.ALL",
    }
    _CARD_COLOR_MAP: Dict[str, str] = {
        "RED": "AbstractCard.CardColor.RED",
        "GREEN": "AbstractCard.CardColor.GREEN",
        "BLUE": "AbstractCard.CardColor.BLUE",
        "PURPLE": "AbstractCard.CardColor.PURPLE",
        "COLORLESS": "AbstractCard.CardColor.COLORLESS",
        "CURSE": "AbstractCard.CardColor.CURSE",
    }

    class GenerationError(Exception):
        """Raised when generation fails due to invalid configuration."""

    @dataclass(frozen=True)
    class KeywordDefinition:
        """Describe a keyword entry for keywords.json."""

        name: str
        description: str
        proper_name: str
        aliases: Iterable[str] = field(default_factory=list)
        positive: bool = True
        prefix: bool = False

        def to_resource(self) -> Dict[str, object]:
            names = {self.name.lower(), *(alias.lower() for alias in self.aliases)}
            payload: Dict[str, object] = {
                "PROPER_NAME": self.proper_name,
                "NAMES": sorted(names),
                "DESCRIPTION": self.description,
            }
            if not self.positive:
                payload["IS_POSITIVE"] = False
            if self.prefix:
                payload["IS_PREFIX"] = True
            return payload

    @dataclass(frozen=True)
    class CardDefinition:
        """Describe a card and the code required to render it."""

        card_id: str
        class_name: str
        name: str
        description: str
        upgrade_description: str
        card_type: str
        rarity: str
        target: str
        color: str
        cost: int
        base_damage: int = 0
        base_block: int = 0
        base_magic: int = 0
        upgrade_damage: int = 0
        upgrade_block: int = 0
        upgrade_magic: int = 0
        upgrade_cost: int = 0

        def to_localization(self) -> Dict[str, Dict[str, str]]:
            return {
                self.card_id: {
                    "NAME": self.name,
                    "DESCRIPTION": self.description,
                    "UPGRADE_DESCRIPTION": self.upgrade_description,
                }
            }

        def generate_java(self, package: str, mod_id: str) -> str:
            type_literal = ModOrchestrator._card_literal(ModOrchestrator._CARD_TYPE_MAP, self.card_type)
            rarity_literal = ModOrchestrator._card_literal(ModOrchestrator._CARD_RARITY_MAP, self.rarity)
            target_literal = ModOrchestrator._card_literal(ModOrchestrator._CARD_TARGET_MAP, self.target)
            color_literal = ModOrchestrator._card_literal(ModOrchestrator._CARD_COLOR_MAP, self.color)
            java_lines = [
                f"package {package};",
                "",
                "import basemod.abstracts.CustomCard;",
                "import com.megacrit.cardcrawl.actions.AbstractGameAction;",
                "import com.megacrit.cardcrawl.actions.common.DamageAction;",
                "import com.megacrit.cardcrawl.actions.common.GainBlockAction;",
                "import com.megacrit.cardcrawl.actions.common.ApplyPowerAction;",
                "import com.megacrit.cardcrawl.cards.AbstractCard;",
                "import com.megacrit.cardcrawl.cards.DamageInfo;",
                "import com.megacrit.cardcrawl.characters.AbstractPlayer;",
                "import com.megacrit.cardcrawl.core.CardCrawlGame;",
                "import com.megacrit.cardcrawl.localization.CardStrings;",
                "import com.megacrit.cardcrawl.monsters.AbstractMonster;",
                "import com.megacrit.cardcrawl.powers.StrengthPower;",
                "",
                f"public class {self.class_name} extends CustomCard {{",
                f"    public static final String ID = \"{self.card_id}\";",
                "    private static final CardStrings STRINGS = CardCrawlGame.languagePack.getCardStrings(ID);",
                "",
                f"    public {self.class_name}() {{",
                f"        super(ID, STRINGS.NAME, makeImagePath(\"{self.class_name}.png\"), {self.cost}, STRINGS.DESCRIPTION,",
                f"            {type_literal}, {color_literal}, {rarity_literal}, {target_literal});",
                f"        this.baseDamage = {self.base_damage};",
                f"        this.baseBlock = {self.base_block};",
                f"        this.baseMagicNumber = {self.base_magic};",
                "        this.magicNumber = this.baseMagicNumber;",
                "    }",
                "",
                "    @Override",
                "    public void use(AbstractPlayer player, AbstractMonster monster) {",
                "        if (this.baseDamage > 0 && monster != null) {",
                "            addToBot(new DamageAction(monster, new DamageInfo(player, this.damage, this.damageTypeForTurn),",
                "                AbstractGameAction.AttackEffect.SLASH_DIAGONAL));",
                "        }",
                "        if (this.baseBlock > 0) {",
                "            addToBot(new GainBlockAction(player, player, this.block));",
                "        }",
                "        if (this.baseMagicNumber > 0) {",
                "            addToBot(new ApplyPowerAction(player, player, new StrengthPower(player, this.magicNumber)));",
                "        }",
                "    }",
                "",
                "    @Override",
                "    public void upgrade() {",
                "        if (!this.upgraded) {",
                "            upgradeName();",
                f"            if ({self.upgrade_cost} > 0) {{",
                f"                upgradeBaseCost(Math.max(0, {self.cost} - {self.upgrade_cost}));",
                "            }",
                f"            if ({self.upgrade_damage} > 0) {{",
                f"                upgradeDamage({self.upgrade_damage});",
                "            }",
                f"            if ({self.upgrade_block} > 0) {{",
                f"                upgradeBlock({self.upgrade_block});",
                "            }",
                f"            if ({self.upgrade_magic} > 0) {{",
                f"                upgradeMagicNumber({self.upgrade_magic});",
                "            }",
                "        }",
                "    }",
                "",
                "    @Override",
                "    public AbstractCard makeCopy() {",
                f"        return new {self.class_name}();",
                "    }",
                "",
                "    private static String makeImagePath(String filename) {",
                f"        return \"{mod_id}/images/cards/\" + filename;",
                "    }",
                "}",
            ]
            return "\n".join(java_lines) + "\n"

    @dataclass(frozen=True)
    class ModDefinition:
        """Aggregate the inputs required to generate a mod."""

        mod_id: str
        package: str
        entry_class_name: str
        display_name: str
        author: str
        version: str
        description: str
        cards: Iterable["ModOrchestrator.CardDefinition"] = field(default_factory=list)
        keywords: Iterable["ModOrchestrator.KeywordDefinition"] = field(default_factory=list)
        localization_language: str = "eng"

    def __init__(self, plugin_manager: PluginManager, base_output: Path | None = None) -> None:
        self._plugin_manager = plugin_manager
        self._logger = logging.getLogger("stsm.mod_orchestrator")
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s"))
            self._logger.addHandler(handler)
        self._logger.setLevel(logging.INFO)
        self._base_output = Path(base_output or "generated_mods").resolve()
        self._base_output.mkdir(parents=True, exist_ok=True)
        self._plugin_manager.register_module(__name__, __import__(__name__))
        self._plugin_manager.register_symbol("modorchestrator.orchestrator", self)

    def generate_mod(self, definition: "ModDefinition", destination: Path | None = None, overwrite: bool = False) -> Path:
        """Generate a mod project for the provided definition."""

        self._validate_definition(definition)
        output_dir = Path(destination or (self._base_output / definition.mod_id)).resolve()
        if output_dir.exists():
            if not overwrite:
                raise ModOrchestrator.GenerationError(f"Destination {output_dir} already exists")
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        self._logger.info("Generating mod %s at %s", definition.mod_id, output_dir)
        self._plugin_manager.dispatch_event(
            "mod_generation.pre",
            {"definition": definition, "destination": str(output_dir)},
        )
        try:
            self._create_structure(output_dir, definition)
        except Exception as exc:  # pylint: disable=broad-except
            if output_dir.exists():
                shutil.rmtree(output_dir, ignore_errors=True)
            raise
        self._plugin_manager.dispatch_event(
            "mod_generation.post",
            {"definition": definition, "destination": str(output_dir)},
        )
        return output_dir

    def _create_structure(self, base_dir: Path, definition: "ModDefinition") -> None:
        java_dir = base_dir / "src" / "main" / "java"
        resource_dir = base_dir / "src" / "main" / "resources"
        java_dir.mkdir(parents=True, exist_ok=True)
        resource_dir.mkdir(parents=True, exist_ok=True)
        package_path = Path(*definition.package.split("."))
        mod_java_dir = java_dir / package_path
        mod_java_dir.mkdir(parents=True, exist_ok=True)
        self._write_entrypoint(mod_java_dir, definition)
        self._write_cards(mod_java_dir, definition)
        self._write_metadata(resource_dir, definition)
        self._write_keywords(resource_dir, definition)
        self._write_localization(resource_dir, definition)
        self._write_assets(resource_dir, definition)
        self._write_build_files(base_dir, definition)
        self._write_readme(base_dir, definition)
        self._write_gitignore(base_dir)

    def _write_entrypoint(self, java_dir: Path, definition: "ModDefinition") -> None:
        cards_initialization = "".join(
            f"        BaseMod.addCard(new {card.class_name}());\n" for card in definition.cards
        ) or "        // No cards registered yet.\n"
        keyword_lines: List[str] = []
        for keyword in definition.keywords:
            resource = keyword.to_resource()
            aliases = ", ".join(f'"{alias}"' for alias in resource["NAMES"])
            keyword_lines.append(
                "        BaseMod.addKeyword("
                f'"{definition.mod_id}", '
                f'"{resource["PROPER_NAME"]}", '
                f"new String[]{{{aliases}}}, "
                f'"{resource["DESCRIPTION"]}");\n'
            )
        keyword_registration = "".join(keyword_lines) or "        // No keywords registered yet.\n"
        class_name = definition.entry_class_name
        package_statement = f"package {definition.package};\n\n"
        imports = "\n".join(
            [
                "import basemod.BaseMod;",
                "import basemod.interfaces.EditCardsSubscriber;",
                "import basemod.interfaces.EditKeywordsSubscriber;",
                "import basemod.interfaces.EditStringsSubscriber;",
                "import com.evacipated.cardcrawl.modthespire.lib.SpireInitializer;",
                "import com.megacrit.cardcrawl.localization.CardStrings;",
                "import com.megacrit.cardcrawl.localization.KeywordStrings;",
                f"import {definition.package}.cards.*;",
            ]
        ) + "\n\n"
        class_body = f"@SpireInitializer\npublic class {class_name} implements " \
            "EditCardsSubscriber, EditKeywordsSubscriber, EditStringsSubscriber {{\n" \
            f"    public static final String MOD_ID = \"{definition.mod_id}\";\n\n" \
            f"    public static void initialize() {{\n        new {class_name}();\n    }}\n\n" \
            f"    public {class_name}() {{\n        BaseMod.subscribe(this);\n    }}\n\n" \
            "    @Override\n    public void receiveEditCards() {\n" + cards_initialization + "    }\n\n" \
            "    @Override\n    public void receiveEditStrings() {\n" \
            f"        String cardPath = \"{definition.mod_id}/localization/{definition.localization_language}/cards.json\";\n" \
            f"        String keywordPath = \"{definition.mod_id}/localization/{definition.localization_language}/keywords.json\";\n" \
            "        BaseMod.loadCustomStringsFile(CardStrings.class, cardPath);\n" \
            "        BaseMod.loadCustomStringsFile(KeywordStrings.class, keywordPath);\n" \
            "    }\n\n" \
            "    @Override\n    public void receiveEditKeywords() {\n" + keyword_registration + "    }\n}\n"
        java_dir.mkdir(parents=True, exist_ok=True)
        target_file = java_dir / f"{class_name}.java"
        target_file.write_text(package_statement + imports + class_body, encoding="utf-8")

    def _write_cards(self, java_dir: Path, definition: "ModDefinition") -> None:
        cards_dir = java_dir / "cards"
        cards_dir.mkdir(parents=True, exist_ok=True)
        for card in definition.cards:
            card_file = cards_dir / f"{card.class_name}.java"
            card_file.write_text(card.generate_java(f"{definition.package}.cards", definition.mod_id), encoding="utf-8")

    def _write_metadata(self, resource_dir: Path, definition: "ModDefinition") -> None:
        meta_dir = resource_dir / "META-INF"
        meta_dir.mkdir(parents=True, exist_ok=True)
        metadata = {
            "modid": definition.mod_id,
            "name": definition.display_name,
            "author_list": [definition.author],
            "description": definition.description,
            "version": definition.version,
            "sts_version": "12-22-2020",
            "mts_version": "3.1.0",
            "dependencies": ["basemod"],
        }
        (meta_dir / "mod.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    def _write_keywords(self, resource_dir: Path, definition: "ModDefinition") -> None:
        keywords_dir = resource_dir / definition.mod_id
        keywords_dir.mkdir(parents=True, exist_ok=True)
        keyword_payload = [keyword.to_resource() for keyword in definition.keywords]
        (keywords_dir / "keywords.json").write_text(json.dumps(keyword_payload, indent=2), encoding="utf-8")
        localization_dir = keywords_dir / "localization" / definition.localization_language
        localization_dir.mkdir(parents=True, exist_ok=True)
        (localization_dir / "keywords.json").write_text(json.dumps(keyword_payload, indent=2), encoding="utf-8")

    def _write_localization(self, resource_dir: Path, definition: "ModDefinition") -> None:
        localization_dir = resource_dir / definition.mod_id / "localization" / definition.localization_language
        localization_dir.mkdir(parents=True, exist_ok=True)
        card_strings: Dict[str, Dict[str, str]] = {}
        for card in definition.cards:
            card_strings.update(card.to_localization())
        (localization_dir / "cards.json").write_text(json.dumps(card_strings, indent=2), encoding="utf-8")

    def _write_build_files(self, base_dir: Path, definition: "ModDefinition") -> None:
        pom_content = f"""<project xmlns=\"http://maven.apache.org/POM/4.0.0\"
    xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"
    xsi:schemaLocation=\"http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd\">\n"""
        pom_content += f"  <modelVersion>4.0.0</modelVersion>\n  <groupId>{definition.package}</groupId>\n"
        pom_content += f"  <artifactId>{definition.mod_id}</artifactId>\n  <version>{definition.version}</version>\n"
        pom_content += "  <properties>\n    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>\n    <maven.compiler.source>1.8</maven.compiler.source>\n    <maven.compiler.target>1.8</maven.compiler.target>\n  </properties>\n"
        pom_content += "  <dependencies>\n    <dependency>\n      <groupId>com.megacrit.cardcrawl</groupId>\n      <artifactId>desktop</artifactId>\n      <version>1.0</version>\n      <scope>system</scope>\n      <systemPath>${project.basedir}/lib/desktop-1.0.jar</systemPath>\n    </dependency>\n    <dependency>\n      <groupId>basemod</groupId>\n      <artifactId>basemod</artifactId>\n      <version>dev</version>\n      <scope>system</scope>\n      <systemPath>${project.basedir}/lib/BaseMod.jar</systemPath>\n    </dependency>\n    <dependency>\n      <groupId>modthespire</groupId>\n      <artifactId>modthespire</artifactId>\n      <version>dev</version>\n      <scope>system</scope>\n      <systemPath>${project.basedir}/lib/ModTheSpire.jar</systemPath>\n    </dependency>\n  </dependencies>\n"
        pom_content += "  <build>\n    <plugins>\n      <plugin>\n        <groupId>org.apache.maven.plugins</groupId>\n        <artifactId>maven-compiler-plugin</artifactId>\n        <version>3.8.1</version>\n        <configuration>\n          <source>1.8</source>\n          <target>1.8</target>\n        </configuration>\n      </plugin>\n      <plugin>\n        <groupId>org.apache.maven.plugins</groupId>\n        <artifactId>maven-jar-plugin</artifactId>\n        <version>3.2.2</version>\n        <configuration>\n          <archive>\n            <manifestEntries>\n              <ModID>{definition.mod_id}</ModID>\n            </manifestEntries>\n          </archive>\n        </configuration>\n      </plugin>\n    </plugins>\n  </build>\n</project>\n"
        (base_dir / "pom.xml").write_text(pom_content, encoding="utf-8")
        lib_dir = base_dir / "lib"
        lib_dir.mkdir(exist_ok=True)
        (lib_dir / ".gitkeep").write_text("", encoding="utf-8")

    def _write_readme(self, base_dir: Path, definition: "ModDefinition") -> None:
        readme = f"# {definition.display_name}\n\n"
        readme += f"Generated by STSMODDER for mod ID `{definition.mod_id}`.\n\n"
        readme += "## Building\n\n"
        readme += "1. Place `desktop-1.0.jar`, `BaseMod.jar`, and `ModTheSpire.jar` into the `lib/` directory.\n"
        readme += "2. Run `mvn package`.\n"
        readme += "3. Copy the resulting jar from `target/` into your ModTheSpire `mods` directory.\n"
        (base_dir / "README.md").write_text(readme, encoding="utf-8")

    def _write_gitignore(self, base_dir: Path) -> None:
        gitignore = "# Generated by STSMODDER\n" "target/\n" "lib/*.jar\n" "*.iml\n" ".idea/\n"
        (base_dir / ".gitignore").write_text(gitignore, encoding="utf-8")

    def _write_assets(self, resource_dir: Path, definition: "ModDefinition") -> None:
        assets_root = resource_dir / definition.mod_id / "images"
        for subdir in ("cards", "relics", "powers", "orbs", "ui"):
            asset_dir = assets_root / subdir
            asset_dir.mkdir(parents=True, exist_ok=True)
            (asset_dir / ".gitkeep").write_text("", encoding="utf-8")

    def _validate_definition(self, definition: "ModDefinition") -> None:
        if not re.fullmatch(r"[a-z0-9_.-]+", definition.mod_id):
            raise ModOrchestrator.GenerationError("mod_id must use lowercase letters, digits, '_', or '-' only")
        namespace = definition.mod_id
        if not definition.package or not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*", definition.package):
            raise ModOrchestrator.GenerationError("package must be a valid Java package identifier")
        if not definition.entry_class_name or not re.fullmatch(r"[A-Z][A-Za-z0-9_]*", definition.entry_class_name):
            raise ModOrchestrator.GenerationError("Entry class must be a valid PascalCase Java class name")
        for card in definition.cards:
            if not card.card_id.startswith(f"{namespace}:"):
                raise ModOrchestrator.GenerationError(
                    f"Card ID {card.card_id} must share the mod namespace '{namespace}'"
                )
            if not re.fullmatch(r"[A-Z][A-Za-z0-9_]*", card.class_name):
                raise ModOrchestrator.GenerationError(f"Card class {card.class_name} must be PascalCase")
            ModOrchestrator._card_literal(ModOrchestrator._CARD_TYPE_MAP, card.card_type)
            ModOrchestrator._card_literal(ModOrchestrator._CARD_RARITY_MAP, card.rarity)
            ModOrchestrator._card_literal(ModOrchestrator._CARD_TARGET_MAP, card.target)
            ModOrchestrator._card_literal(ModOrchestrator._CARD_COLOR_MAP, card.color)
        for keyword in definition.keywords:
            if not keyword.name:
                raise ModOrchestrator.GenerationError("Keywords must define a base name")

    @staticmethod
    def _card_literal(mapping: Dict[str, str], key: str) -> str:
        key_upper = key.upper()
        if key_upper not in mapping:
            raise ModOrchestrator.GenerationError(f"Unsupported card attribute '{key}'")
        return mapping[key_upper]


MOD_ORCHESTRATOR = ModOrchestrator(PluginManager.get_instance())
