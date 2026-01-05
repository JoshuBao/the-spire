# The Spire - Crisis Management Simulator

**A terminal-based disaster management game where you fight to keep a vertical city alive.**

This isn't a peaceful building sim. This is **crisis management**. Fires spread through your tower. Sectors collapse. People panic. You make impossible choices about who lives and who dies.

## What Makes This Stream-Worthy

**Visible Spatial Disasters:**
- Watch fires spread from level to level in real-time
- See sectors collapse and take neighboring levels with them
- Track health bars depleting as disasters cascade

**Hard Dilemmas:**
- "Level 4 is collapsing. Reinforce it or evacuate?"
- Both options hurt. Choose wisely.

**Tension/Release Pacing:**
- Tension meter builds over time
- Crisis events release tension (but cause chaos)
- Creates rhythm: calm → building dread → catastrophe → recovery → repeat

**Cascading Failures:**
- One fire on Level 7 → spreads to 6 and 8 → power plant burns → blackout → farms fail → starvation
- Collapse damages levels below it
- Scarcity creates new emergencies

**Emergent Stories:**
- "I had it under control until the earthquake hit my last farm during a fire"
- "Saved the residential sector but my power grid collapsed - everyone froze"

## Installation

```bash
cd the-spire
pip install -r requirements.txt
python main.py
```

Or: `./run.sh`

**Requirements:**
- Python 3.7+
- `rich` - For text formatting
- `textual` - For the TUI framework

## Testing & Demo

**Quick Test:**
```bash
python test_game.py        # Unit tests - verify core systems work
```

**Watch AI Play (Visual Demo):**
```bash
python demo.py             # Watch Claude play for 20 turns with commentary
```

**Full Automated Playthrough:**
```bash
python autoplay.py         # AI plays 50 turns + scenario tests
```

See [TEST_RESULTS.md](TEST_RESULTS.md) for detailed test validation.

## The Interface

The game uses a **professional TUI** (Terminal User Interface) built with Textual. The screen is divided into panels:

- **Stats Panel** (top-left) - Resources, population, morale, tension
- **Tower Panel** (center) - Visual representation of all levels with health bars
- **Legend Panel** (top-right) - Symbol reference guide
- **Event Log** (middle-right) - Recent events and disasters
- **Controls Panel** (bottom-right) - Keyboard shortcuts
- **Dilemma Panel** (bottom-left) - Urgent decisions when they appear

The tower display shows:
```
→ L8 🏠 Housin ██████████ 12w    🔥
  L7 ⚡ Power  ████       8w
  L6 ⚠️  Farms  ███        10w
```
- `→` = Your cursor position
- Icon = Sector type (or status if damaged/critical)
- Name = Sector purpose
- Health bar = Structural integrity
- Workers = Population working in that sector
- 🔥 = Fire indicator (if on fire)

## How to Play

**Your Goal:** Keep the population alive as long as possible (50 years = victory)

**Controls:**
- `↑/↓` or `W/S` - Move cursor between levels
- `1` - Repair selected level (costs 40 materials)
- `2` - Extinguish fire on selected level (costs 30 power)
- `3` - Build new level (costs 80 materials)
- `4` - Boost morale with festival (costs 40 food + 20 power)
- `5` - Emergency rations - cull population for food (harsh but sometimes necessary)
- `SPACE` - Pass time without action
- `Q` - Quit
- `A/B` - Answer dilemmas when they appear

## The Tower

Your city is built vertically in sectors:

- **🏠 Residential** - Houses citizens (population capacity)
- **🌾 Farms** - Produces food (workers × 2.5 per turn)
- **⚡ Power** - Generates power (workers × 3 per turn)
- **⚙️  Industrial** - Produces materials (workers × 2 per turn)

Each sector has:
- **Health**: Decays over time, falls faster when damaged
- **Workers**: Produce resources, die when sector collapses
- **Status**: Can catch fire, become unstable, or be quarantined

## Why It's Compelling

**Spatial Strategy:**
- Put farms high up? Harder to maintain but more production
- Cluster sectors? Fire spreads faster
- Spread them out? Harder to defend all of them

**Multiple Simultaneous Crises:**
- Fire on Level 6
- Level 3 collapsing
- Food shortage
- Riot on Level 8
- **Which do you handle first?**

**Risk/Reward:**
- Build higher = more production BUT higher sectors decay faster
- Wait to stockpile = safe BUT tension builds toward guaranteed disaster
- Invest in morale = expensive BUT prevents riots

**Pacing Creates Drama:**
- Early game: Peaceful expansion, stockpiling resources
- Mid game: First crisis hits, you scramble to respond
- Late game: Multiple systems failing, impossible choices

## Disaster Types

**Major Crises** (triggered by tension meter):
- 🌍 **Earthquake** - Damages 2-5 random sectors
- 🔥 **Major Fire** - Starts fire that spreads between levels
- 🦠 **Plague** - Kills 15-30% of population instantly
- 💥 **Structural Failure** - 1-3 sectors collapse completely
- ✊ **Riots** - Damages sector, kills citizens, tanks morale

**Cascading Effects:**
- Fires spread to adjacent levels every few turns
- Collapses can damage the level below
- Scarcity (food/power) creates new problems
- Low morale triggers emigration and riots

**Minor Events** (random):
- 🎁 Supply cache found (+materials)
- 👥 Refugees arrive (+population)
- ⚡ Power surge (+power)
- 🌾 Abundant harvest (+food)

## Strategy Tips

**Early Game:**
- Build up materials and food stockpiles
- Repair sectors before they collapse
- Don't expand too fast - higher levels = more decay

**Mid Game:**
- Watch the tension meter - crisis is coming
- Keep power and food positive
- Have materials ready for emergency repairs

**Late Game:**
- Prioritize fires - they spread and cascade
- Let damaged sectors collapse rather than waste materials
- Sometimes you have to sacrifice sectors to save the city

**Critical:**
- Sectors below 20 health will collapse and kill all workers
- Fires deal 8 damage/turn and spread
- Population = 0 or all sectors destroyed = game over
- Morale < 30 causes mass emigration

## The Tension System

**How it works:**
- Tension builds 2.5% per turn
- At 100%, a major crisis triggers
- Crisis resets tension to 0
- Creates predictable rhythm of calm → dread → catastrophe

**What this means:**
- You know disaster is coming
- You just don't know WHICH disaster
- Build stockpiles during calm periods
- Brace for impact when tension hits 70%+

## Sample Playthrough

```
Year 1: Built to 8 levels. Everything stable.
Year 2: Earthquake damaged 4 sectors. Scrambled to repair.
Year 3: Fire outbreak on Level 5 during repairs.
Year 4: Fire spread to 4, 6. Extinguished 5 and 6. Level 4 collapsed.
Year 5: Food shortage from lost farm. Used emergency rations.
Year 6: Morale crisis from culling. Riots on Level 7.
Year 7: Structural failure destroyed Level 2 power plant.
Year 8: Blackout cascaded into farm failure. Starvation.
Year 9: EXTINCTION - 37 survivors fled the Spire.
```

**The story:** Early earthquake weakened defenses. Fire exploited that weakness. Desperate choices (emergency rations) created new problems (riots). Lost key infrastructure (power plant). Cascaded into total failure.

## Why Streamers Will Love This

**Clip-worthy moments:**
- "Chat, I think I can sa— OH NO THE FIRE SPREAD TO THE FARMS"
- Dilemma popups forcing impossible choices live on stream
- Watching carefully managed stability spiral into chaos in 3 turns
- The moment you realize your one mistake 10 turns ago just killed you

**Strategic depth:**
- Multiple viable approaches (tall vs wide, aggressive vs conservative)
- Every run plays out differently based on which disasters hit when
- Skill expression in resource management and priority calls

**Narrative emergence:**
- Every disaster creates a story
- Chat gets invested in "saving Level 5" or "the last farm"
- Natural highlights for VOD editing

Try to beat Year 50. Good luck. You'll need it.
