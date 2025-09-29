"""Orchestrates generation of ModTheSpire-ready Slay the Spire mods."""
from __future__ import annotations

import json
import logging
import os
import re
import shutil
import subprocess
import textwrap
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from logic import APPLICATION_LOGIC, ApplicationLogic
from plugin_manager import PluginManager


class ModOrchestrator:
    """High-level builder that materializes GUI-authored mods on disk."""

    class SpecificationError(Exception):
        """Raised when a provided project specification is invalid."""

    class BuildError(Exception):
        """Raised when the compilation pipeline fails."""

    @dataclass
    class AssetMapping:
        """Mapping of source asset to a resources-relative destination."""

        source: Path
        relative_path: str

    @dataclass
    class KeywordDefinition:
        """Keyword specification mirrored from the GUI state."""

        proper_name: str
        names: List[str]
        description: str

    @dataclass
    class CardDefinition:
        """Card description encapsulating gameplay and presentation fields."""

        card_id: str
        name: str
        description: str
        upgrade_description: str
        card_type: str
        card_color: str
        rarity: str
        target: str
        cost: int
        base_damage: int = 0
        base_block: int = 0
        base_magic: int = 0
        upgrade_damage: int = 0
        upgrade_block: int = 0
        upgrade_magic: int = 0
        image_path: Optional[Path] = None

        def class_name(self) -> str:
            segments = re.split(r"[^0-9A-Za-z]+", self.card_id)
            sanitized = "".join(segment[:1].upper() + segment[1:] for segment in segments if segment)
            if not sanitized:
                raise ModOrchestrator.SpecificationError("Card ID must contain alphanumeric characters")
            return f"{sanitized}Card"

        def resource_image_path(self, mod_id: str) -> str:
            file_name = f"{self.card_id}.png"
            return f"{mod_id}Resources/images/cards/{file_name}"

    @dataclass
    class ModMetadata:
        """Primary metadata for the mod."""

        mod_id: str
        name: str
        author: str
        version: str
        description: str
        package: str
        entry_class: str
        homepage: Optional[str] = None
        update_json: Optional[str] = None
        dependencies: List[str] = field(default_factory=list)
        mts_version: str = "3.6.3"
        sts_version: str = "12-18-2022"

    @dataclass
    class ModProject:
        """Aggregate project definition produced by the GUI."""

        metadata: "ModOrchestrator.ModMetadata"
        cards: List["ModOrchestrator.CardDefinition"] = field(default_factory=list)
        keywords: List["ModOrchestrator.KeywordDefinition"] = field(default_factory=list)
        assets: List["ModOrchestrator.AssetMapping"] = field(default_factory=list)
        additional_dependencies: List[Path] = field(default_factory=list)

    def __init__(self, logic: ApplicationLogic, plugin_manager: PluginManager) -> None:
        self._logic = logic
        self._plugin_manager = plugin_manager
        self._logger = logging.getLogger("stsm.mod_orchestrator")
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
        self._logger.setLevel(logging.INFO)
        self._plugin_manager.register_module(__name__, __import__(__name__))
        self._plugin_manager.register_symbol("modorchestrator.orchestrator", self)

    def build_mod(self, project: "ModOrchestrator.ModProject", destination: Path, clean: bool = True) -> Path:
        """Create the on-disk project structure and compile it into a mod jar."""

        self._validate_project(project)
        destination = destination.expanduser().resolve()
        destination.mkdir(parents=True, exist_ok=True)
        project_root = destination / project.metadata.mod_id
        if clean and project_root.exists():
            shutil.rmtree(project_root)
        java_root = project_root / "src" / "main" / "java"
        resource_root = project_root / "src" / "main" / "resources"
        java_root.mkdir(parents=True, exist_ok=True)
        resource_root.mkdir(parents=True, exist_ok=True)

        self._plugin_manager.dispatch_event(
            "mod.build.start",
            {"project": project, "destination": str(project_root)},
        )

        self._write_mod_metadata(resource_root, project)
        self._write_localization(resource_root, project)
        self._copy_assets(resource_root, project)
        self._write_entry_class(java_root, project)
        self._write_card_classes(java_root, project)

        jar_path = self._compile_project(project_root, project)

        self._plugin_manager.dispatch_event(
            "mod.build.completed",
            {"project": project, "jar_path": str(jar_path)},
        )
        self._logger.info("Built mod jar at %s", jar_path)
        return jar_path

    def _validate_project(self, project: "ModOrchestrator.ModProject") -> None:
        metadata = project.metadata
        if not re.fullmatch(r"[a-z][a-z0-9_.-]*", metadata.mod_id):
            raise ModOrchestrator.SpecificationError(
                "mod_id must start with a lowercase letter and contain only lowercase letters, numbers, '_', '-' or '.'"
            )
        if not re.fullmatch(r"[A-Za-z_][0-9A-Za-z_.]*", metadata.package):
            raise ModOrchestrator.SpecificationError("package name must be a valid Java package identifier")
        if not re.fullmatch(r"[A-Za-z_][0-9A-Za-z_]*", metadata.entry_class):
            raise ModOrchestrator.SpecificationError("entry class must be a valid Java identifier")
        seen_ids = set()
        for card in project.cards:
            if card.card_id in seen_ids:
                raise ModOrchestrator.SpecificationError(f"Duplicate card id '{card.card_id}' detected")
            seen_ids.add(card.card_id)
        for asset in project.assets:
            if not asset.source.exists():
                raise ModOrchestrator.SpecificationError(f"Asset '{asset.source}' does not exist")

    def _write_mod_metadata(self, resource_root: Path, project: "ModOrchestrator.ModProject") -> None:
        meta_dir = resource_root / "META-INF"
        meta_dir.mkdir(parents=True, exist_ok=True)
        metadata = project.metadata
        mod_json = {
            "modid": metadata.mod_id,
            "name": metadata.name,
            "author_list": [metadata.author],
            "description": metadata.description,
            "version": metadata.version,
            "sts_version": metadata.sts_version,
            "mts_version": metadata.mts_version,
            "dependencies": metadata.dependencies,
        }
        if metadata.update_json:
            mod_json["update_json"] = metadata.update_json
        if metadata.homepage:
            mod_json["homepage"] = metadata.homepage
        mod_json_path = meta_dir / "mod.json"
        with mod_json_path.open("w", encoding="utf-8") as handle:
            json.dump(mod_json, handle, indent=2)

    def _write_localization(self, resource_root: Path, project: "ModOrchestrator.ModProject") -> None:
        base_dir = resource_root / f"{project.metadata.mod_id}Resources" / "localization" / "eng"
        base_dir.mkdir(parents=True, exist_ok=True)
        cards_payload: Dict[str, Dict[str, str]] = {}
        for card in project.cards:
            cards_payload[card.card_id] = {
                "NAME": card.name,
                "DESCRIPTION": card.description,
                "UPGRADE_DESCRIPTION": card.upgrade_description,
            }
        cards_path = base_dir / "cards.json"
        with cards_path.open("w", encoding="utf-8") as handle:
            json.dump({"cards": cards_payload}, handle, indent=2)

        if project.keywords:
            keyword_payload = []
            for keyword in project.keywords:
                keyword_payload.append(
                    {
                        "PROPER_NAME": keyword.proper_name,
                        "NAMES": keyword.names,
                        "DESCRIPTION": keyword.description,
                    }
                )
            keywords_path = base_dir / "keywords.json"
            with keywords_path.open("w", encoding="utf-8") as handle:
                json.dump({"keywords": keyword_payload}, handle, indent=2)

    def _copy_assets(self, resource_root: Path, project: "ModOrchestrator.ModProject") -> None:
        for asset in project.assets:
            destination = resource_root / asset.relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(asset.source, destination)
        for card in project.cards:
            if card.image_path is None:
                continue
            destination = resource_root / card.resource_image_path(project.metadata.mod_id)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(card.image_path, destination)

    def _write_entry_class(self, java_root: Path, project: "ModOrchestrator.ModProject") -> None:
        metadata = project.metadata
        package_dir = java_root / Path(metadata.package.replace(".", "/"))
        package_dir.mkdir(parents=True, exist_ok=True)
        cards_package = f"{metadata.package}.cards"
        card_registrations = []
        for card in project.cards:
            card_registrations.append(
                f"        BaseMod.addCard(new {cards_package}.{card.class_name()}());"
            )
        keyword_registrations = []
        for keyword in project.keywords:
            names_literal = ", ".join(f"\"{name}\"" for name in keyword.names)
            keyword_registrations.append(
                textwrap.dedent(
                    f"""
                    BaseMod.addKeyword("{keyword.proper_name}", new String[]{{{names_literal}}}, "{keyword.description}");
                    """
                ).strip()
            )
        entry_source = textwrap.dedent(
            f"""
            package {metadata.package};

            import basemod.BaseMod;
            import basemod.interfaces.EditCardsSubscriber;
            import basemod.interfaces.EditStringsSubscriber;
            import basemod.interfaces.PostInitializeSubscriber;
            import com.evacipated.cardcrawl.modthespire.lib.SpireInitializer;
            import com.megacrit.cardcrawl.localization.CardStrings;

            @SpireInitializer
            public class {metadata.entry_class} implements EditCardsSubscriber, EditStringsSubscriber, PostInitializeSubscriber {{
                public {metadata.entry_class}() {{
                    BaseMod.subscribe(this);
                }}

                public static void initialize() {{
                    new {metadata.entry_class}();
                }}

                @Override
                public void receiveEditCards() {{
            {os.linesep.join(card_registrations) if card_registrations else "        // No cards registered."}
                }}

                @Override
                public void receiveEditStrings() {{
                    BaseMod.loadCustomStringsFile(
                        CardStrings.class,
                        "{project.metadata.mod_id}Resources/localization/eng/cards.json"
                    );
                }}

                @Override
                public void receivePostInitialize() {{
            {os.linesep.join(f"        {line}" for line in keyword_registrations) if keyword_registrations else "        // No keywords registered."}
                }}
            }}
            """
        ).strip() + "\n"
        entry_path = package_dir / f"{metadata.entry_class}.java"
        with entry_path.open("w", encoding="utf-8") as handle:
            handle.write(entry_source)

    def _write_card_classes(self, java_root: Path, project: "ModOrchestrator.ModProject") -> None:
        if not project.cards:
            return
        metadata = project.metadata
        cards_package_dir = java_root / Path(f"{metadata.package}.cards".replace(".", "/"))
        cards_package_dir.mkdir(parents=True, exist_ok=True)
        for card in project.cards:
            source = self._render_card_source(project, card)
            file_path = cards_package_dir / f"{card.class_name()}.java"
            with file_path.open("w", encoding="utf-8") as handle:
                handle.write(source)

    def _render_card_source(
        self,
        project: "ModOrchestrator.ModProject",
        card: "ModOrchestrator.CardDefinition",
    ) -> str:
        metadata = project.metadata
        package_name = f"{metadata.package}.cards"
        image_path = card.resource_image_path(metadata.mod_id)
        use_statements: List[str] = []
        if card.base_damage > 0:
            use_statements.append(
                "addToBot(new DamageAction(m, new DamageInfo(p, this.damage, DamageInfo.DamageType.NORMAL), AbstractGameAction.AttackEffect.SLASH_HORIZONTAL));"
            )
        if card.base_block > 0:
            use_statements.append("addToBot(new GainBlockAction(p, p, this.block));")
        if not use_statements:
            use_statements.append("// No primary effect defined in GUI specification.")
        use_body = textwrap.indent(os.linesep.join(use_statements), " " * 12)

        upgrade_statements: List[str] = []
        if card.upgrade_damage:
            upgrade_statements.append(f"upgradeDamage({card.upgrade_damage});")
        if card.upgrade_block:
            upgrade_statements.append(f"upgradeBlock({card.upgrade_block});")
        if card.upgrade_magic:
            upgrade_statements.append(f"upgradeMagicNumber({card.upgrade_magic});")
        if not upgrade_statements:
            upgrade_statements.append("// No upgrade deltas configured.")
        upgrade_body = textwrap.indent(os.linesep.join(upgrade_statements), " " * 12)

        source = textwrap.dedent(
            f"""
            package {package_name};

            import basemod.abstracts.CustomCard;
            import com.megacrit.cardcrawl.actions.AbstractGameAction;
            import com.megacrit.cardcrawl.actions.common.DamageAction;
            import com.megacrit.cardcrawl.actions.common.GainBlockAction;
            import com.megacrit.cardcrawl.cards.AbstractCard;
            import com.megacrit.cardcrawl.cards.DamageInfo;
            import com.megacrit.cardcrawl.characters.AbstractPlayer;
            import com.megacrit.cardcrawl.monsters.AbstractMonster;

            public class {card.class_name()} extends CustomCard {{
                public static final String ID = "{metadata.mod_id}:{card.card_id}";
                private static final int COST = {card.cost};
                private static final int DAMAGE = {card.base_damage};
                private static final int BLOCK = {card.base_block};
                private static final int MAGIC = {card.base_magic};

                public {card.class_name()}() {{
                    super(
                        ID,
                        "{card.name}",
                        "{image_path}",
                        COST,
                        "{card.description}",
                        CardType.{card.card_type.upper()},
                        CardColor.{card.card_color.upper()},
                        CardRarity.{card.rarity.upper()},
                        CardTarget.{card.target.upper()}
                    );
                    baseDamage = DAMAGE;
                    baseBlock = BLOCK;
                    baseMagicNumber = MAGIC;
                    magicNumber = baseMagicNumber;
                }}

                @Override
                public void use(AbstractPlayer p, AbstractMonster m) {{
{use_body}
                }}

                @Override
                public void upgrade() {{
                    if (!upgraded) {{
                        upgradeName();
{upgrade_body}
                    }}
                }}

                @Override
                public AbstractCard makeCopy() {{
                    return new {card.class_name()}();
                }}
            }}
            """
        ).strip() + "\n"
        return source

    def _compile_project(self, project_root: Path, project: "ModOrchestrator.ModProject") -> Path:
        java_root = project_root / "src" / "main" / "java"
        resource_root = project_root / "src" / "main" / "resources"
        classes_dir = project_root / "build" / "classes"
        classes_dir.mkdir(parents=True, exist_ok=True)
        java_files = sorted(str(path) for path in java_root.rglob("*.java"))
        if not java_files:
            raise ModOrchestrator.BuildError("No Java source files generated; cannot compile mod")
        javac = self._locate_javac()
        classpath = self._compose_classpath(project)
        command = [javac, "-encoding", "UTF-8", "-d", str(classes_dir)]
        if self._supports_release_flag(javac):
            command.extend(["--release", "8"])
        if classpath:
            command.extend(["-cp", classpath])
        command.extend(java_files)
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
        if completed.returncode != 0:
            raise ModOrchestrator.BuildError(
                f"javac failed with exit code {completed.returncode}: {completed.stderr.strip()}"
            )

        jar_path = project_root / "build" / f"{project.metadata.mod_id}.jar"
        manifest_content = "Manifest-Version: 1.0\nCreated-By: STSMODDER ModOrchestrator\n"
        manifest_path = classes_dir / "META-INF" / "MANIFEST.MF"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(manifest_content, encoding="utf-8")
        with zipfile.ZipFile(jar_path, "w") as handle:
            for file_path in classes_dir.rglob("*"):
                if file_path.is_file():
                    handle.write(file_path, file_path.relative_to(classes_dir))
            for resource_path in resource_root.rglob("*"):
                if resource_path.is_file():
                    handle.write(resource_path, resource_path.relative_to(resource_root))
        return jar_path

    def _compose_classpath(self, project: "ModOrchestrator.ModProject") -> str:
        components: List[str] = []
        config = self._logic.runtime_config
        for dependency in [
            config.modthespire_jar,
            config.basemod_path,
            config.stslib_path,
            config.actlikeit_path,
            config.desktop_jar_path,
        ]:
            if dependency:
                resolved = Path(dependency).expanduser().resolve()
                if not resolved.exists():
                    raise ModOrchestrator.BuildError(
                        f"Dependency '{resolved}' declared in runtime configuration does not exist"
                    )
                components.append(str(resolved))
        for extra in project.additional_dependencies:
            resolved = extra.expanduser().resolve()
            if not resolved.exists():
                raise ModOrchestrator.BuildError(f"Additional dependency '{resolved}' does not exist")
            components.append(str(resolved))
        return os.pathsep.join(dict.fromkeys(components))

    def _locate_javac(self) -> str:
        java_home = self._logic.runtime_config.java_home
        if java_home:
            javac_path = Path(java_home).expanduser().resolve() / "bin" / "javac"
            if javac_path.exists():
                return str(javac_path)
        from shutil import which

        discovered = which("javac")
        if not discovered:
            raise ModOrchestrator.BuildError(
                "Unable to locate javac. Configure java_home or ensure javac is on PATH"
            )
        return discovered

    def _supports_release_flag(self, javac_path: str) -> bool:
        try:
            completed = subprocess.run(
                [javac_path, "--help"],
                check=False,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError as exc:
            raise ModOrchestrator.BuildError("javac binary not executable") from exc
        return "--release" in completed.stdout


_PLUGIN_MANAGER = PluginManager.get_instance()
MOD_ORCHESTRATOR = ModOrchestrator(APPLICATION_LOGIC, _PLUGIN_MANAGER)

__all__ = [
    "ModOrchestrator",
    "MOD_ORCHESTRATOR",
]

