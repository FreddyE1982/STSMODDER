"""Utility for generating a reusable fake `desktop-1.0.jar` for automated testing."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
import textwrap
import zipfile
from pathlib import Path
from typing import Dict, Optional

STUB_SOURCES: Dict[str, str] = {
    "com/megacrit/cardcrawl/cards/AbstractCard.java": textwrap.dedent(
        """
        package com.megacrit.cardcrawl.cards;

        import com.megacrit.cardcrawl.actions.AbstractGameAction;
        import com.megacrit.cardcrawl.characters.AbstractPlayer;
        import com.megacrit.cardcrawl.monsters.AbstractMonster;

        public abstract class AbstractCard {
            public enum CardType { ATTACK, SKILL, POWER, STATUS, CURSE }
            public enum CardColor { RED, GREEN, BLUE, PURPLE, COLORLESS, CURSE }
            public enum CardRarity { BASIC, COMMON, UNCOMMON, RARE, SPECIAL, CURSE }
            public enum CardTarget { ENEMY, SELF, ALL_ENEMY, ALL, SELF_AND_ENEMY, NONE }

            protected boolean upgraded = false;
            public int baseDamage;
            public int baseBlock;
            public int baseMagicNumber;
            public int magicNumber;
            public int block;
            public int damage;

            protected AbstractCard(
                String id,
                String name,
                String img,
                int cost,
                String rawDescription,
                CardType type,
                CardColor color,
                CardRarity rarity,
                CardTarget target
            ) {
            }

            public void addToBot(AbstractGameAction action) {
            }

            public void upgradeName() {
                this.upgraded = true;
            }

            protected void upgradeDamage(int amount) {
                this.baseDamage += amount;
                this.damage = this.baseDamage;
            }

            protected void upgradeBlock(int amount) {
                this.baseBlock += amount;
                this.block = this.baseBlock;
            }

            protected void upgradeMagicNumber(int amount) {
                this.baseMagicNumber += amount;
                this.magicNumber = this.baseMagicNumber;
            }

            public abstract void use(AbstractPlayer p, AbstractMonster m);

            public abstract void upgrade();

            public abstract AbstractCard makeCopy();
        }
        """
    ),
    "com/megacrit/cardcrawl/cards/DamageInfo.java": textwrap.dedent(
        """
        package com.megacrit.cardcrawl.cards;

        public class DamageInfo {
            public enum DamageType { NORMAL, THORNS }

            public DamageInfo(Object owner, int base, DamageType type) {
            }
        }
        """
    ),
    "com/megacrit/cardcrawl/actions/AbstractGameAction.java": textwrap.dedent(
        """
        package com.megacrit.cardcrawl.actions;

        public abstract class AbstractGameAction {
            public enum AttackEffect { SLASH_HORIZONTAL, SLASH_DIAGONAL, NONE }
            public abstract void update();
        }
        """
    ),
    "com/megacrit/cardcrawl/actions/common/DamageAction.java": textwrap.dedent(
        """
        package com.megacrit.cardcrawl.actions.common;

        import com.megacrit.cardcrawl.actions.AbstractGameAction;
        import com.megacrit.cardcrawl.cards.DamageInfo;
        import com.megacrit.cardcrawl.characters.AbstractPlayer;
        import com.megacrit.cardcrawl.monsters.AbstractMonster;

        public class DamageAction extends AbstractGameAction {
            public DamageAction(AbstractMonster target, DamageInfo info, AttackEffect effect) {
            }

            @Override
            public void update() {
            }
        }
        """
    ),
    "com/megacrit/cardcrawl/actions/common/GainBlockAction.java": textwrap.dedent(
        """
        package com.megacrit.cardcrawl.actions.common;

        import com.megacrit.cardcrawl.actions.AbstractGameAction;
        import com.megacrit.cardcrawl.characters.AbstractCreature;

        public class GainBlockAction extends AbstractGameAction {
            public GainBlockAction(AbstractCreature target, AbstractCreature source, int amount) {
            }

            @Override
            public void update() {
            }
        }
        """
    ),
    "com/megacrit/cardcrawl/characters/AbstractCreature.java": textwrap.dedent(
        """
        package com.megacrit.cardcrawl.characters;

        public class AbstractCreature {
        }
        """
    ),
    "com/megacrit/cardcrawl/characters/AbstractPlayer.java": textwrap.dedent(
        """
        package com.megacrit.cardcrawl.characters;

        public class AbstractPlayer extends AbstractCreature {
        }
        """
    ),
    "com/megacrit/cardcrawl/monsters/AbstractMonster.java": textwrap.dedent(
        """
        package com.megacrit.cardcrawl.monsters;

        import com.megacrit.cardcrawl.characters.AbstractCreature;

        public class AbstractMonster extends AbstractCreature {
        }
        """
    ),
    "com/megacrit/cardcrawl/localization/CardStrings.java": textwrap.dedent(
        """
        package com.megacrit.cardcrawl.localization;

        public class CardStrings {
            public String NAME;
            public String DESCRIPTION;
            public String UPGRADE_DESCRIPTION;
        }
        """
    ),
    "com/megacrit/cardcrawl/localization/KeywordStrings.java": textwrap.dedent(
        """
        package com.megacrit.cardcrawl.localization;

        public class KeywordStrings {
            public String PROPER_NAME;
            public String[] NAMES;
            public String DESCRIPTION;
        }
        """
    ),
}


def _locate_javac(java_home: Optional[str] = None) -> str:
    if java_home:
        candidate = Path(java_home).expanduser().resolve() / "bin" / "javac"
        if candidate.exists():
            return str(candidate)
    discovered = shutil.which("javac")
    if not discovered:
        raise RuntimeError("javac executable not found; install a JDK or set JAVA_HOME")
    return discovered


def _supports_release_flag(javac_path: str) -> bool:
    probe = subprocess.run(
        [javac_path, "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    return "--release" in probe.stdout


def create_fake_desktop_jar(output_path: Path, java_home: Optional[str] = None) -> Path:
    output_path = Path(output_path).expanduser().resolve()
    with tempfile.TemporaryDirectory() as tmp_dir:
        src_root = Path(tmp_dir) / "src"
        classes_root = Path(tmp_dir) / "classes"
        for relative_path, source in STUB_SOURCES.items():
            file_path = src_root / relative_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(source, encoding="utf-8")
        javac = _locate_javac(java_home)
        compile_command = [javac, "-encoding", "UTF-8", "-d", str(classes_root)]
        if _supports_release_flag(javac):
            compile_command.extend(["--release", "8"])
        compile_command.extend(str(path) for path in src_root.rglob("*.java"))
        subprocess.run(compile_command, check=True)
        manifest_path = classes_root / "META-INF" / "MANIFEST.MF"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text("Manifest-Version: 1.0\nCreated-By: STSMODDER Test Harness\n", encoding="utf-8")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output_path, "w") as handle:
            for file in classes_root.rglob("*"):
                if file.is_file():
                    handle.write(file, file.relative_to(classes_root))
    return output_path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a fake desktop-1.0.jar for tests")
    parser.add_argument("output", type=Path, help="Destination jar path")
    parser.add_argument("--java-home", type=str, default=None, help="Optional JAVA_HOME override")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    create_fake_desktop_jar(args.output, args.java_home)


__all__ = ["create_fake_desktop_jar", "main"]


if __name__ == "__main__":
    main()
