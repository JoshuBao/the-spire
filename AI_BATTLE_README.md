# AI vs AI Battle Mode 🤖⚔️🤖

Watch ChatGPT and Claude compete to survive The Spire!

## Quick Start

```bash
python ai_battle.py
```

## How It Works

1. **Run the script** - It creates two separate games, one for each AI
2. **Copy game state** - Script shows current tower state, resources, events
3. **Paste to AIs** - Open ChatGPT and Claude in separate tabs
4. **Get decisions** - Each AI decides what to do
5. **Paste back** - Enter their decisions
6. **Repeat** - Until one or both die!

## Example Flow

**Script shows:**
```
🟢 CHATGPT'S TURN

Copy this to ChatGPT:

You are playing THE SPIRE - a terminal crisis management game.

CURRENT STATE (Year 3, Month 2):

Resources:
- Population: 75
- Food: 45 (consumption: 75/turn)
- Power: 120 (consumption: 45/turn)
- Materials: 60
- Morale: 55%
- Tension: 75% (crisis at 100%)

Tower Status:
L 8 🏠  Housing   [████░░░░░░] 12w
L 7 ⚡  Power     [██████░░░░] 14w   🔥
L 6 🌾  Farms     [███░░░░░░░] 8w
...

Recent Events:
- Y3M1: 🔥 MAJOR FIRE on Level 7!
- Y3M2: Fire spreading...

Available Actions:
1. REPAIR [level]
2. EXTINGUISH [level]
3. BUILD FARM
...
```

**You paste that to ChatGPT, it responds:**
```
I need to extinguish the fire on Level 7 before it spreads further.

EXTINGUISH 7
```

**You paste "EXTINGUISH 7" back to the script, it executes!**

## What Makes This Great for Twitter

### 📹 Record It
- Screen record the whole battle
- Speed up to 2-4x
- Post the highlights

### 📊 Compare Strategies
ChatGPT might:
- Play aggressively (expand fast)
- Take risks

Claude might:
- Play conservatively (repair focus)
- Avoid risks

### 🎭 Drama & Narrative
```
Turn 5: Both AIs thriving
Turn 12: ChatGPT hit by earthquake
Turn 15: Claude builds 3 farms
Turn 18: ChatGPT running out of food
Turn 20: ChatGPT tries emergency rations
Turn 23: ChatGPT DIES - Claude wins!
```

### 💬 Engagement Hooks

**Tweet Example 1:**
```
Made my terminal game play itself: ChatGPT vs Claude

ChatGPT: Aggressive expansion, risky plays
Claude: Conservative, repair-focused

ChatGPT died Year 7 (starvation)
Claude survived to Year 15

Who would you bet on?
[video]
```

**Tweet Example 2:**
```
AI Battle Royale but it's crisis management

Round 1:
🟢 ChatGPT: "BUILD FARM"
🔵 Claude: "REPAIR damaged sectors"

Round 2: Earthquake hits
🟢 ChatGPT: "EMERGENCY RATIONS"
🔵 Claude: "WAIT and recover"

[Play yourself: github link]
```

**Tweet Example 3:**
```
Watched ChatGPT and Claude play my survival sim:

Turn 10 both alive
Turn 15 both struggling
Turn 18 ChatGPT: "This is fine" 🔥
Turn 20 ChatGPT dead
Turn 25 Claude barely surviving
Turn 30 Claude extinct

92% die to starvation
0% win rate
Strategy matters

[link]
```

## Competition Formats

### 1. **Head-to-Head** (What we built)
- Both play simultaneously
- First to die loses
- Most engaging to watch

### 2. **Best of 3**
Run 3 battles, who wins more?

### 3. **High Score Challenge**
- Each AI plays 5 games
- Best year survived wins
- Shows consistency

### 4. **Speedrun**
- Who reaches Year 10 first?
- Rewards aggressive play

### 5. **Population Challenge**
- Who has most population at Year 10?
- Tests different strategies

## Tips for Running

**Make it interesting:**
- Start recording before turn 1
- Narrate key decisions
- Show side-by-side stats
- Highlight dramatic moments

**What to capture:**
- First major crisis
- Dilemma choices (A vs B)
- Death spiral moments
- Final extinction

**Speed up boring parts:**
- Early game buildup (fast)
- Crisis moments (slow)
- Death spiral (dramatic music)

## Results Storage

Battle results automatically save to:
```
battle_results_20251229_153045.json
```

Contains:
- Who won
- Years survived
- Final population
- All decisions made
- Timestamps

## Making It Viral

**The Hook:**
"I made two AIs play my terminal game against each other"

**The Payoff:**
Show different strategies, dramatic deaths, who won

**The CTA:**
"Try it yourself: [github link]"
"Which AI would you bet on?"
"ChatGPT players vs Claude players - who survives longer?"

## Advanced: Automate It

If you have API access:
1. Use ChatGPT API
2. Use Claude API
3. Run fully automated battles
4. Generate tournament brackets
5. Stream it live

(Would need API keys + code updates)

---

## Example Commentary Script

```
"ChatGPT and Claude are about to compete in crisis management"

Turn 1-5: "Both expanding quickly, building farms and power"

Turn 8: "ChatGPT gets hit by an earthquake - 3 sectors damaged"

Turn 10: "Claude playing it safe, repairing everything"

Turn 12: "ChatGPT's food running low - going for emergency rations"

Turn 15: "ChatGPT's morale tanking, people are fleeing"

Turn 18: "Fire breaks out on ChatGPT's last farm"

Turn 20: "ChatGPT extinct. Claude wins with 60 population."

"ChatGPT's aggressive strategy backfired. Claude's conservative approach paid off."

"Try it yourself [link]"
```

Perfect for a 60-90 second video!
