# Bullet Cards — Doomsday Western Edition
> A two-player local duel blending strategy, psychology, and probability.

Step into a dusty saloon where the stakes are life and death. Outwit your opponent, bribe the greedy owl dealer, and pray the chamber is empty.

---

## 🎵 Audio System (v4.1)

### Immersive Audio
- **Background Music**: Original accordion + piano composition, inspired by Chopin's nocturnes but fully original and royalty-free.
- **Ambient Sounds**: Rain, wind, creaking doors, and distant murmur of other gamblers in the saloon.
- **Sound Effects**: Card flips, card throws, gold coin clinks, gunshots, empty chamber clicks, cylinder spins, button clicks.
- **Controls**: Press `M` to mute/unmute at any time.

### Audio Copyright Notice
> All music and sound effects in this game are **originally composed and generated** for this project using AI audio synthesis. They are **not** taken from any copyrighted source. The background music is an original composition inspired by (but not copying) the romantic-era piano style — no actual Chopin recordings or sheet music are used. All audio assets are free to use with this game.

---

## 🧮 The Math Behind the Game (v5.0)

This game is more than a card game — it's a **math problem about asymmetry**, wrapped in a western saloon.

### Key Findings (from 350,000 simulated games)

| Scenario | P1 (Snake) Win Rate | P2 (Lizard) Win Rate |
|---|---|---|
| Random vs Random | 19.9% | 80.1% |
| P1 Optimal vs P2+Intel | 21.5% | 78.5% |
| **No Bribes (Fair)** | **48.8%** | **51.2%** |
| P1 All-In Bribe | 0.0% | 100.0% |

### The Core Truths

1. **Gold is worthless** — it never enters any win/loss determination. It's pure narrative deception.
2. **Bribes only help P2** — P2 holds the final rule-flip, so intel = guaranteed win. P1's intel is worth 0.
3. **The seat decides everything** — not luck, not skill. P2 wins 80%+ with bribes, 51% without.
4. **Average game length: 2.02 rounds** — 97.9% of games end before round 6.

### Best-of-Three Swap System

To make the game fair, v5.0 introduces a **best-of-three with side swap**:
- First to 2 wins takes the match
- Sides swap after every round (P1 becomes P2, P2 becomes P1)
- Each player experiences both the advantaged and disadvantaged seat
- This turns the game's biggest flaw into its biggest feature

### In-Game Mathematical Truth Reveal

After the final match ends, press **[A]** to reveal the mathematical truth:
- 4 pages of simulation data, formulas, and optimal strategies
- Win rate comparison charts
- The gold-useless theorem proof
- Optimal strategy for both seats
- The final verdict on what this game really is

### Full Analysis

See [MATHEMATICAL_ANALYSIS.md](MATHEMATICAL_ANALYSIS.md) for the complete deep dive:
- Mathematical modeling (state space, Bellman equations)
- Game theory analysis (Stackelberg game, committer vs adjudicator)
- Psychology analysis (player's cognitive arc, intuition traps)
- Probability analysis (death countdown, game length distribution)
- Optimal strategy tables
- All simulation data and methodology

### Reproduce the Simulations

```bash
python simulate.py
```

Outputs `simulation_results.json` with all 7 experiments (50,000 games each).

---

## 🎮 Quick Start

### Requirements
- Python 3.8+
- pygame 2.0+ (or pygame-ce)

### Step 1: Download game assets
The `assets/` folder (character images, cards, backgrounds) is not included in the repository. Run this script to download all 21 images automatically:

```bash
python download_assets.py
```

Wait for it to finish — you should see `All assets ready!` when done.

### Step 2: Install & Run
```bash
pip install pygame
python game_v2.py
```

Or use the launcher (auto-installs pygame if missing):
```bash
python run_game.py
```

### Testing (headless logic verification)
```bash
python test_v2.py
```

> **Windows users**: You can also just double-click `start.bat` to launch the game directly.

---

## 🎭 Characters

| Player | Animal | Personality |
|--------|--------|-------------|
| **Player 1** | 🐍 Venomous Snake | Cunning, sly, always with a cigar |
| **Player 2** | 🦎 Scarred Lizard | Fierce, scarred, dangerous in a duel |

Each character has **5 mood portraits** that change based on the game state:
- `normal` — calm and collected
- `scared` — terrified, sweating, about to shoot
- `dead` — X-eyes, tongue out, bullet wound
- `survivor` — relieved, shaking, lucky to be alive
- `victory` — triumphant, laughing, showered in gold

---

## 📜 Complete Rules

### Initial State
- Two players, **50 gold each**
- Hand: **1, 2, 3, 4, 5, 6** (one of each)
- Dealer (a greedy owl) sits in the center

### Turn-Based System
**Player 1 always acts first.** During each player's turn:
- Their own hand is **face-up**
- The opponent's hand is **face-down** (hidden)
- Their private dealer hint is visible
- A large banner announces whose turn it is

*Look away when it's not your turn!*

### Round Flow
```
┌─────────────────────────────────────────────────────────────┐
│ ① SELECT — turn-based                                       │
│   · Click a card to select → click "Confirm Play"           │
│   · Played card is permanently removed                       │
│   · Card value = bullets loaded into your own revolver       │
├─────────────────────────────────────────────────────────────┤
│ ② BRIBE (round 2 onwards) — turn-based, SECRET             │
│   · Each player secretly enters bribe amount (0 = skip)     │
│   · Choose strategy: TRICK (lie to opponent) / HONEST      │
│   · Bribe gold goes to the dealer (DESTROYED)               │
│   · Opponent never knows if/how much you bribed             │
├─────────────────────────────────────────────────────────────┤
│ ③ BETTING — call / raise & flip                             │
│   · P1 calls HIGH or LOW + places bet (integer, ≤ gold)     │
│   · P2 chooses: CALL (accept rule) or RAISE (flip rule +   │
│     bet more gold)                                          │
│   · If P2 raises, P1 can CALL or RAISE again (max 3 raises)│
│   · Final rule = last raiser's choice; all bet gold DESTROYED│
│   · Bet amounts are PUBLIC; total gold is PRIVATE           │
├─────────────────────────────────────────────────────────────┤
│ ④ REVEAL — both cards shown                                 │
│   · Final HIGH/LOW mode announced                            │
│   · Higher card wins HIGH mode; lower card wins LOW mode     │
├─────────────────────────────────────────────────────────────┤
│ ⑤ SHOOT — loser points gun at themselves                    │
│   · Bullets in chamber = your own card value                 │
│   · Hit chance = card value / 6                              │
│   · Hit → death → game over                                  │
│   · Miss → survive → next round                              │
│   · Tie → no penalty, cards consumed                         │
└─────────────────────────────────────────────────────────────┘
```

### Game Over Conditions
1. Any player dies from a gunshot
2. Any player runs out of cards

---

## 🦉 Dealer Bribe & Intel System (Core)

The most strategic layer — a multi-level mind game where the dealer is your weapon.

### How It Works
- **Bribe amount** → highest bidder becomes the **Benefactor**
- Benefactor always receives **true intel** about the opponent's card
- The opponent receives intel determined by the benefactor's strategy:
  - **TRICK** → Dealer **lies** to the opponent about your card
  - **HONEST** → Dealer tells the **truth** to the opponent (reverse psychology)
- If no one bribes, both get vague, useless intel
- Bribe amounts are **completely secret** — opponent only sees your public bets

### Intel Quality
| Card Range | True Hint | False Hint (TRICK) |
|-----------|-----------|-------------------|
| 1-2 (small) | "Opponent's card is light... real light." | "Opponent's card is huge! He's loaded for bear." |
| 3-4 (medium) | "Opponent's card is middling. Nothing fancy." | "Opponent's card is tiny. Practically empty." |
| 5-6 (large) | "Opponent's card is heavy... real heavy." | "Opponent's card is tiny. Nothing to fear." |

### 🧠 Classic Mind Games

#### Scenario 1: Small Card, Big Bribe, TRICK
```
You play: 1 (small, only 1/6 death chance)
You bribe: 30 gold, strategy TRICK
Dealer tells opponent: "His card is huge! He's loaded for bear."
Opponent thinks: "He's got a big card, so if I RAISE to LOW I'll win!"
Opponent raises to LOW...
Result: LOW mode → your 1 beats his big card → opponent shoots!
```

#### Scenario 2: Big Card, HONEST Reverse Psychology
```
You play: 6 (huge, 6/6 = certain death if you lose)
You bribe: 25 gold, strategy HONEST
Dealer tells opponent the TRUTH: "His card is heavy... real heavy."
Opponent thinks: "He's definitely lying to make me play small! I'll reverse!"
Opponent raises to HIGH (expecting you to have a small card)...
Result: HIGH mode → your 6 beats his card → opponent shoots!
You perfectly avoid the 6/6 death risk.
```

#### Scenario 3: Infinite Regression
```
You: "I'll bribe TRICK so he thinks I have a big card"
Opponent: "He's bribing TRICK, so I should do the opposite"
You: "He knows I'll bribe TRICK, so I'll bribe HONEST instead"
Opponent: "He predicted I'd predict, so he flipped to HONEST..."
→ Russian nesting doll mind games!
```

#### Scenario 4: Bankroll Destruction
```
Early game: you keep raising bets, forcing opponent to match
Opponent burns through gold early
Late game: opponent has 2 gold left, you have 30
You open with 15 gold — opponent can't even CALL!
You dictate the rule every round, and they can't stop you.
```

### 💡 Strategy Tips
- **6 is a death sentence** if you lose — use bribes to make opponents think you're weak
- **1 is almost safe** (1/6) — use it to bluff and lure opponents into big bets
- **Track opponent's remaining cards** — after a few rounds you can deduce what's left
- **Gold is a weapon** — all gold is destroyed, so making opponents spend is as good as stealing
- **No folding** — once you're in, you're in. Think before you raise.

---

## 🎨 Visual Style

Doomsday Western aesthetic:
- 🏜️ Desert town / saloon interior backgrounds
- 🦉 Greedy owl dealer with top hat and gold pouch
- 🔫 Russian roulette cylinder (bullet chambers)
- 🃏 Vintage parchment cards with **bullet** suit symbols
- 💰 Dark gold + brown leather + blood red palette
- ✨ Muzzle flash particles + screen flash / blood overlay
- 🎭 Dynamic character mood portraits

### Card Design
Each card (1-6) features:
- Aged yellow parchment texture
- Dark brown leather border with metal rivets
- Large italic red numerals in corners
- Brass bullet icons arranged by value (1=1 bullet, 2=2 bullets, etc.)
- Card back: burgundy leather with crossed bullets emblem

---

## 🗂️ File Structure
```
bullet_cards/
├── game_v2.py            # ⭐ Main program (run this!)
├── test_v2.py            # Headless logic + rendering tests
├── run_game.py           # Auto-installer + launcher
├── download_assets.py    # Asset download script
├── README.md             # This file
└── assets/               # Game assets (21 images)
    ├── card_1.png ~ card_6.png   # Bullet-suit playing cards
    ├── card_back.png              # Card back design
    ├── snake_normal.png           # Snake character moods
    ├── snake_scared.png
    ├── snake_dead.png
    ├── snake_survivor.png
    ├── snake_victory.png
    ├── lizard_normal.png          # Lizard character moods
    ├── lizard_scared.png
    ├── lizard_dead.png
    ├── lizard_survivor.png
    ├── lizard_victory.png
    ├── dealer_owl.png             # Owl dealer character
    ├── roulette_cylinder.png      # Revolver cylinder decoration
    ├── background_menu.png        # Main menu background
    └── background_saloon.png      # Game background
```

---

## 🔧 Controls

| Action | Input |
|--------|-------|
| Select card / option | Left Mouse Click |
| Confirm / buttons | Left Mouse Click |
| Next round (round end) | `SPACE` |
| Quit game | `ESC` or window close |

---

## ❓ FAQ

**Q: Why is it called "Bullet Cards"?**
A: Each card you play loads that many bullets into your own revolver — the higher the card, the more chambers are loaded, and the deadlier the shot if you lose.

**Q: Where does all the gold go?**
A: Every gold coin — both bets and bribes — is destroyed every round. It feeds the crows, never returns. The goal isn't to win money, it's to make the opponent run out or get shot.

**Q: How does the betting work?**
A: Player 1 calls HIGH or LOW and places a bet. Player 2 can CALL (accept the rule and pay the same) or RAISE (bet more gold and FLIP the rule — HIGH becomes LOW, LOW becomes HIGH). Up to 3 raises total.

**Q: Can I fold?**
A: No folding. You can CALL or RAISE, but once the betting starts you're committed. Think before you raise!

**Q: What does the dealer hint tell me?**
A: It's intel about your opponent's card — "his card is heavy" or "barely a bullet in there." If you bribed the most, your hint is always true. If the opponent bribed more, their strategy (TRICK/HONEST) decides whether your hint is true or false.

**Q: Can the opponent see how much I bribed?**
A: Never. Bribes are completely secret. The opponent only sees your public bets, not your bribe amount or your total gold.

**Q: Why turn-based instead of simultaneous?**
A: To prevent players from seeing each other's hands. During your turn, only your cards are visible — the opponent's hand is face-down. Look away when it's not your turn!

---

## 🚀 Extension Ideas
- [ ] Online multiplayer (Socket / WebSocket)
- [ ] AI opponent with game theory strategy
- [ ] Sound effects (gunshots, coins, western whistle)
- [ ] Card deal / shoot animations
- [ ] 3-4 player mode
- [ ] Tournament / multi-round scoring

---

## 📢 声明 / Attribution

**本项目为非盈利个人创作项目。**

| 项目 | 说明 |
|------|------|
| **游戏设计 / 规则 / 玩法 / 核心理念** | 原创，由项目作者独立设计 |
| **程序代码** | 由 AI 辅助生成，作者进行整合、调试与修改 |
| **美术资源（角色、背景、卡牌、界面等）** | 由豆包 AI 生成 |
| **项目性质** | 非盈利、纯兴趣分享，不用于任何商业用途 |

如需转载或使用本项目内容，请注明来源。

---

**May the odds be ever in your favor, stranger. 🤠🔫**
