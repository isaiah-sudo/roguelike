# Crypt of the Necrolord ⚔️💀
*A Dark Fantasy Deckbuilding Roguelike built in Python & Pygame-CE*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Inspired by classics like *Slay the Spire*, **Crypt of the Necrolord** is a turn-based tactical roguelike where you descend through procedural catacombs, draft lethal spellcards, discover eldritch relics, and battle monstrous horrors culminating in the ancient Necrolord Malakor.

---

## 🚀 What's New in v1.2
- **Difficulty & Boss Tuning**:
  - Reverted aggressive floor scaling and extra monster Strength buffs in Act 1 for balanced progression.
  - Substantially nerfed boss damage and combat buffs (Necrolord Malakor, Void Behemoth, Ignis the Infernal, Archmage Valerius, The Corrupted Heart, Nemesis Avatar).
  - Restored Act Ascension Healing to **75% Max HP** and restored starting economy to **99 Gold**.
  - Reverted early enemy damage spikes (Cultist, Skeletal Sentinel, Plague Fiend, Void Reaver).
- **Character Survival Rebalance**:
  - Blood Knight: **84 Max HP**
  - Shadow Assassin: **75 Max HP**
  - Void Necromancer: **76 Max HP** (better offsets self-harm card costs)
  - Tempest Herald: **76 Max HP**
  - Radiant Templar: **88 Max HP**
- **Radiant Templar Mechanics**:
  - **1-Turn Thorns**: Retaliation Thorns persists through the enemy turn to strike back against incoming attacks, then clears at the start of your next turn.
  - **Non-Stacking Thorns**: Re-applying Thorns refreshes to the maximum value rather than accumulating indefinitely.
- **Character-Exclusive Card Pools**:
  - Card rewards and shops now offer archetype cards unique to your chosen champion, alongside universal neutral spells.
- **Inspect Tooltips**:
  - Hovering over relics and potions across the top bar, merchant shop, and combat rewards displays stylized tooltips with descriptions.

## 📦 Downloads (v1.2)
- **[Download Windows Setup Installer (`CryptOfTheNecrolord_Setup_v1.2.0.exe`)](https://github.com/isaiah-sudo/rougelike/releases/download/v1.2/CryptOfTheNecrolord_Setup_v1.2.0.exe)** *(Recommended: Installs or cleanly updates existing game with desktop & start menu shortcuts)*
- **[Download Portable Windows 64-bit Zip (`CryptOfTheNecrolord_v1.2.0_win64.zip`)](https://github.com/isaiah-sudo/rougelike/releases/download/v1.2/CryptOfTheNecrolord_v1.2.0_win64.zip)** *(Extract & play directly without installation)*

---

## 🌟 Key Features

1. **Multiple Playable Champions**:
   - **The Blood Knight (Vanguard of Ruin)**: 84 Max HP. Starter Relic: *Burning Blood* (Heal 6 HP after combat). Specializes in Strength scaling (*Limit Break*, *Whirlwind*), self-harm berserk combos (*Rupture*, *Hemokinesis*), and impenetrable fortress defense (*Barricade*, *Entrench*, *Body Slam*).
   - **The Shadow Assassin (Nightshade Weaver)**: 75 Max HP. Starter Relic: *Ring of the Serpent* (+2 cards drawn on Turn 1). Specializes in dual-dagger Shiv storms (*Accuracy*, *Blade Dance*, *Storm of Steel*), lethal Poison compounding (*Deadly Poison*, *Catalyst*, *Envenom*), and damage negation (*Wraith Form*, *Neutralize*).
   - **The Void Necromancer (Scion of the Abyss)**: 76 Max HP. Starter Relic: *Soul Phylactery* (Deal 4 damage whenever any card is Exhausted). Specializes in dark soul sacrifice (*Offering*, *Soul Drain*), chain corpse detonations (*Corpse Explosion*), and free-casting demonic powers (*Corruption*, *Dark Embrace*, *Abyssal Echo*).
   - **The Tempest Herald (Conduit of the Storm)**: 76 Max HP. Starter Relic: *Storm Core* (Zap lowest-health enemy for 5 damage at end of turn). Specializes in lightning manipulation and vulnerable execution.
   - **The Radiant Templar (Champion of the Dawn)**: 88 Max HP. Starter Relic: *Sun Crest* (Gain 2 Thorns for 1 turn upon playing a Skill). Specializes in holy retribution and judgment.

2. **Diverse Enemy Types & Dynamic Fighting Styles**:
   - **Undead**: *Crypt Cultist* (Ritual scaler that escalates attack damage each round), *Skeletal Sentinel* (High block turtle with bone cleavers), *Tormented Wight* (Elite banshee that drains life and inflicts mass debuffs).
   - **Beast / Vermin**: *Plague Fiend* (Rapid double-bite poisoner), *Dread Spider* (Web spinner that entangles you with Weak + Vulnerable, spits venom).
   - **Demon / Abyssal**: *Void Reaver* (Elite berserker that enrages and builds Strength), *Cinder Demon* (Pyromancer surrounded by flame spikes that punish every attack).
   - **Arcane / Occult**: *Mad Alchemist* (Chaotic potion brewer that chugs stoneskin elixirs and hurls corrosive acids), *Corrupted Hierophant* (Dark preacher that casts unholy benedictions and heavy smites).
   - **Boss Encounters**: *Necrolord Malakor* (Multi-phase Lich King charging Apocalypse Blasts) and *The Void Behemoth* (Titanic cosmic entity with multi-tentacle flurries and Devour attacks).

3. **Paced & Staged Turn Action System (Slay the Spire Style)**:
   - **Deliberate Attack Pacing**: Enemy turns are no longer instant! Each monster lunges forward one-by-one, announces its move via an on-screen action banner, deals its damage/effects, displays floating combat popups, and holds for ~0.85s so you can clearly see and process what every enemy did.
   - **Combat Action Banner**: An ornate obsidian & gold banner centered across the top of the battlefield broadcasts live play-by-play combat announcements (`"⚡ Cinder Demon: Flame Burst (10 DMG)"`, `"🛡️ Skeletal Sentinel gains 10 Block!"`, `"⚔️ ENEMY TURN ⚔️"`, `"TURN 2 - YOUR TURN"`).
   - **Ornate Energy Orb & Controls**: Slay the Spire-style clockwork brass & fiery crimson energy orb with bright font, plus an arched End Turn button that illuminates when enabled and dims to "ENEMY TURN..." during enemy phases.
   - **Atmospheric Dungeon Aesthetics**: Gothic stone walls, flickering animated wall torches with flame sparks, flagstone floors with perspective lines, and elevated card hover states.

4. **Procedural Branching Dungeon Map**:
   - Multiple paths through the Crypt: Normal Monsters, deadly Elites, Shrines/Events (`?`), Campfires (`R`), Underworld Merchants (`$`), and the Final Boss (`B`).
   - Every floor provides meaningful tactical choices between high risk/reward routes.

5. **Complex Archetype Synergies & Deck Drafting (50+ Cards)**:
   - **0-Cost Buffs, Cantrips & Enablers**:
     - *Flex*: Gain 2 (4) Strength for 0 Energy, temporary until end of turn. Massive burst attack synergy.
     - *Clash*: 0-cost Attack that deals 14 (18) damage, playable only when all other cards in hand are Attacks!
     - *Adrenaline*: 0 cost, Gain 1 (2) Energy, Draw 2 cards, Exhausts.
     - *Seeing Red*: 0 cost, Gain 2 (3) Energy. Instant burst enabler.
     - *Dark Offering*: 0 cost, Lose 3 HP to gain 2 Energy and Draw 3 (5) cards.
     - *Warcry* & *Shadowstep*: 0 cost, gain Block and draw cards without burning Energy.
     - *Gouge*: 0 cost attack that applies Vulnerable.
     - *Shivs*: 0 cost generated attacks that trigger combo counters.
   - **Blood & Self-Harm Berserker**:
     - *Feed*: Deal 10 (14) damage. If Fatal, permanently increases your Max HP!
     - *Fiend Fire*: Exhausts ALL cards in hand, hitting the enemy for 7 (10) damage for each card exhausted!
     - *Spot Weakness*: If the enemy intends to attack, gain 3 (4) Strength!
     - *Armaments*: Gain Block and upgrade cards in your hand for the remainder of combat!
     - *True Grit*: Gain Block and exhaust a card from hand to thin your deck.
     - *Rupture*: Whenever you lose HP from a card effect, gain permanent Strength!
     - *Hemokinesis*: Sacrifice 2 HP to deal 15 (20) crushing damage (immediately triggers Rupture).
     - *Combustion*: Lose 1 HP at turn end to blast ALL enemies with hellfire every turn.
     - *Blood for Blood*: High-damage 4-cost attack that discounts by 1 each time you take damage (down to 0 cost!).
     - *Soul Reaper*: Multi-target attack that heals unblocked damage dealt.
   - **Shiv Tempo, Multi-Cast & Finishers**:
     - *Accuracy*: Shivs deal +4 (+6) additional damage.
     - *Blade Dance* & *Cloak and Dagger*: Generate waves of lethal Shivs into your hand.
     - *Storm of Steel*: Discard your entire hand to flood it with upgraded Shivs.
     - *Finisher*: Deals massive damage for EACH Attack played this turn!
     - *Double Tap* & *Burst*: Causes your next Attacks or Skills to cast TWICE in a row!
   - **Exponential Poison & Decay**:
     - *Crippling Cloud*: Applies Poison and Weak to all enemies.
     - *Bouncing Flask*: Cascades toxic vials across random foes multiple times.
     - *Corpse Explosion*: Applies Poison, and upon target's death, it explodes dealing its Max HP to all remaining enemies!
     - *Catalyst*: Multiplies enemy Poison stacks 2x (3x upgraded)!
     - *Noxious Fumes*: Passively inflicts Poison on all foes every turn.
   - **Fortress Block & Shield Slam**:
     - *Barricade*: Your Block does not reset at turn start—build defense into the hundreds!
     - *Entrench*: Doubles your current Block value!
     - *Body Slam*: Deals damage equal to your current Block (0 cost when upgraded!).
     - *Flame Barrier*: Grants heavy Block and retaliates when attacked.
   - **Necromantic Exhaust Engines**:
     - *Corruption*: All Skills cost 0 Energy and Exhaust when played!
     - *Feel No Pain*: Gain Block every time ANY card is Exhausted.
     - *Dark Embrace*: Draw a card every time ANY card is Exhausted.
     - *Second Wind* & *Sever Soul*: Purge non-attacks from hand for massive shields and damage.
     - *Exhumation*: Retrieve exhausted cards back into your hand.

4. **Metaprogression & Facilities**:
   - **Rest Sites (Campfires)**: Rest to mend wounds (+30% Max HP) or Smith at the anvil to upgrade cards to their enhanced `+` versions.
   - **Underworld Merchant**: Buy new cards, legendary relics, and combat potions, or pay gold to purge unwanted cards from your deck.
   - **Mystery Encounters**: Atmospheric text-based gothic events with branching decisions.
   - **Relics & Potions**: Passive modifiers (*Vajra*, *Anchor*, *Kunai*, *Lantern*, *Meat on the Bone*, *Dark Grimoire*) and instant-use consumable flasks.
   - **Save Game & Title Screen**: Multi-slot expedition save system. Auto-saves on map progress and combat victory; manual **Save & Quit** button directly in the dungeon top bar; Title Screen with **Continue**, **New Expedition**, and full **Saved Expeditions** browser.

5. **Self-Contained Procedural Sound & Visual Effects**:
   - Built-in real-time audio synthesis (no missing sound files or broken audio dependencies).
   - Particle explosion system, damage popup floats, screen shake, and smooth card rendering.

---

## 🚀 Quick Start

### Prerequisites
Make sure Python 3.10+ is installed:
```bash
python --version
```

### Run the Game
Simply execute:
```bash
python main.py
```
Or double-click `play.bat` or `run.bat`.

### 📦 Standalone Executable & Windows Installer

The project includes pre-configured tools to build a standalone Windows `.exe` and an Inno Setup installer with custom gothic icons:

1. **Run the Standalone Executable**:
   - Location: `dist/CryptOfTheNecrolord/CryptOfTheNecrolord.exe`
   - Fully standalone with bundled Python runtime, assets, and custom icon. No Python installation required!

2. **Run the Windows Setup Installer**:
   - Location: `installer_output/CryptOfTheNecrolord_Setup_v1.0.0.exe`
   - Installs the game into Program Files / User Apps, configures Desktop & Start Menu shortcuts with the game icon, and registers a standard Windows uninstaller.

3. **Re-building EXE & Installer**:
   - Simply double-click `build.bat` or run:
   ```bash
   build.bat
   ```
   This will automatically generate the multi-resolution `.ico` / `.png` icons, compile the standalone executable via PyInstaller, and generate the Windows setup wizard via Inno Setup.

### Run Automated Tests
```bash
python -m unittest tests/test_gameplay.py
```

---

## 🎮 Controls

| Action | Control |
| :--- | :--- |
| **Play Card** | **Left Click** card and drag targeting arrow to enemy (or click for self/all) |
| **Cancel Targeting** | **Right Click** or **Escape** |
| **End Turn** | Click **END TURN** button or press **Space** / **E** |
| **Use Potion** | Click any potion in the potion belt (top right) during combat |
| **Inspect Deck** | Press **D** or click the **Deck** button on the Map |
| **Save & Quit** | Click **Save & Quit** in the top bar or press **Escape** on the Map |
| **Navigate Map** | **Left Click** on any glowing / available connected node |
| **Title Navigation** | **Enter** (Embark/Continue), **N** (New Run), **L** (Saved Games), **Esc** (Depart) |

---

## 📂 Project Structure

```
rougelike/
├── assets/                     # Game icons (multi-res .ico and .png)
├── build.bat                   # 1-Click build script for EXE & Installer
├── installer.iss               # Inno Setup Windows installer definition
├── main.py                     # Entry point & run state coordinator
├── settings.py                 # Display dimensions, color themes, fonts
├── engine/
│   ├── card_renderer.py        # Card visual frames, typography, emblem art
│   ├── sound.py                # Procedural audio waveform synthesizer
│   ├── particles.py            # Combat particles & floating damage numbers
│   ├── visual_fx.py            # Screen shake & Bezier curve targeting arrows
│   └── ui.py                   # Reusable buttons, health bars, top HUD
├── models/
│   ├── card.py                 # Card base class, catalog, and upgrades
│   ├── relic.py                # Passive relics and combat lifecycle hooks
│   ├── potion.py               # Usable combat potions
│   ├── status.py               # Status effects manager (Vulnerable, Poison, etc.)
│   ├── entity.py               # Combatant base class
│   ├── player.py               # Hero entity, master deck, draw/discard piles
│   └── enemy.py                # Enemy AI, intents, normal, elite & boss roster
├── scripts/
│   └── generate_icon.py        # Programmatic high-res icon generator
├── systems/
│   ├── combat.py               # Battle state, turn management, damage math
│   ├── map_generator.py        # Slay-the-Spire procedural node graph
│   ├── save_manager.py         # Multi-slot game serialization and recovery
│   ├── events.py               # Gothic mystery encounters & choices
│   ├── shop.py                 # Merchant shop & card removal service
│   └── reward.py               # Post-battle card draft & loot tables
├── views/
│   ├── title_view.py           # Atmospheric main menu & Continue screen
│   ├── load_game_view.py       # Expedition slot browser with stats & purge
│   ├── char_select_view.py     # Hero class selection screen
│   ├── combat_view.py          # Battlefield rendering & card interaction
│   ├── map_view.py             # Branching map navigation screen
│   ├── reward_view.py          # 3-Card drafting & victory loot screen
│   ├── rest_view.py            # Campfire rest & smithing screen
│   ├── shop_view.py            # Merchant shop screen
│   ├── event_view.py           # Narrative story screen
│   ├── deck_view.py            # Modal full deck viewer
│   └── game_over_view.py       # Victory / Defeat end screen
└── tests/
    └── test_gameplay.py        # Automated test suite
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
