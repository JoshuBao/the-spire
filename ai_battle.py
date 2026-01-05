#!/usr/bin/env python3
"""
AI vs AI Battle - ChatGPT vs Claude compete to survive The Spire!

How to use:
1. Run this script
2. Copy the game state for each AI
3. Paste it to ChatGPT and Claude separately
4. Paste their decisions back here
5. Watch them compete!
"""

import json
from main import Simulation
from datetime import datetime

class AIPlayer:
    def __init__(self, name):
        self.name = name
        self.sim = Simulation()
        self.turns = 0
        self.decisions = []

    def get_game_state_prompt(self):
        """Generate a prompt to send to the AI"""
        s = self.sim.state

        # Build tower visual
        tower_visual = []
        for i in range(s.max_height, 0, -1):
            sector = s.get_sector(i)
            if sector:
                symbol, color = sector.get_display()
                health_bar = "█" * int(sector.health / 10)
                fire = "🔥" if sector.on_fire else ""
                workers = f"{sector.workers}w" if sector.workers > 0 else "empty"
                tower_visual.append(f"L{i:2d} {symbol} {sector.sector_type.value[2]:8s} [{health_bar:10s}] {workers:8s} {fire}")
            else:
                tower_visual.append(f"L{i:2d} ... empty ...")

        # Get recent events
        recent_events = [f"- {evt[0]}" for evt in s.events[-5:]]

        # Build prompt
        prompt = f"""You are playing THE SPIRE - a terminal crisis management game.

CURRENT STATE (Year {s.year}, Month {s.month}):

Resources:
- Population: {s.population}
- Food: {s.food:.0f} (consumption: {s.population * 1.0:.0f}/turn)
- Power: {s.power:.0f} (consumption: {s.population * 0.6:.0f}/turn)
- Materials: {s.materials:.0f}
- Morale: {s.morale:.0f}%
- Tension: {s.tension:.0f}% (crisis at 100%)

Tower Status:
{chr(10).join(tower_visual)}

Recent Events:
{chr(10).join(recent_events)}

"""

        # Add dilemma if exists
        if s.current_dilemma:
            d = s.current_dilemma
            prompt += f"""
⚠️  URGENT DILEMMA:
{d.title}: {d.description}
A: {d.option_a}
B: {d.option_b}

RESPOND WITH: "A" or "B"
"""
        else:
            prompt += """
Available Actions:
1. REPAIR [level] - Fix selected level (40 materials)
2. EXTINGUISH [level] - Put out fire (30 power)
3. BUILD FARM - New farm sector (80 materials)
4. BUILD POWER - New power plant (80 materials)
5. BUILD INDUSTRY - New industry (80 materials)
6. BUILD HOUSING - New housing (80 materials)
7. FESTIVAL - Boost morale (40 food, 20 power)
8. RATIONS - Kill 10 for food (harsh)
9. WAIT - Pass time, accumulate resources

RESPOND WITH: Action name and level if needed
Examples: "REPAIR 5", "BUILD FARM", "WAIT"
"""

        return prompt

    def process_ai_decision(self, decision_text):
        """Process the AI's text decision into a game action"""
        s = self.sim.state
        decision_text = decision_text.strip().upper()

        # Handle dilemma
        if s.current_dilemma:
            if 'A' in decision_text:
                s.current_dilemma.consequence_a()
                s.current_dilemma = None
                self.sim.advance_turn("wait")
                self.decisions.append((self.turns, "DILEMMA: Choose A"))
                return "Chose option A"
            elif 'B' in decision_text:
                s.current_dilemma.consequence_b()
                s.current_dilemma = None
                self.sim.advance_turn("wait")
                self.decisions.append((self.turns, "DILEMMA: Choose B"))
                return "Chose option B"
            else:
                return "ERROR: Dilemma requires A or B"

        # Parse action
        action = None
        level = None

        if "REPAIR" in decision_text:
            action = "repair"
            # Try to extract level number
            parts = decision_text.split()
            for part in parts:
                if part.isdigit():
                    level = int(part)
                    break
            if level:
                s.cursor = level

        elif "EXTINGUISH" in decision_text:
            action = "extinguish"
            parts = decision_text.split()
            for part in parts:
                if part.isdigit():
                    level = int(part)
                    break
            if level:
                s.cursor = level

        elif "BUILD FARM" in decision_text or "FARM" in decision_text:
            action = "build_farm"

        elif "BUILD POWER" in decision_text or ("BUILD" in decision_text and "POWER" in decision_text):
            action = "build_power"

        elif "BUILD INDUSTRY" in decision_text or ("BUILD" in decision_text and "INDUSTRY" in decision_text):
            action = "build_industry"

        elif "BUILD HOUSING" in decision_text or ("BUILD" in decision_text and "HOUSING" in decision_text):
            action = "build_housing"

        elif "FESTIVAL" in decision_text:
            action = "boost_morale"

        elif "RATIONS" in decision_text or "EMERGENCY" in decision_text:
            action = "emergency_rations"

        elif "WAIT" in decision_text:
            action = "wait"

        else:
            return f"ERROR: Could not parse action from '{decision_text}'"

        # Execute action
        self.sim.advance_turn(action)
        self.turns += 1
        self.decisions.append((self.turns, decision_text))

        return f"Executed: {action}" + (f" on level {level}" if level else "")

    def is_alive(self):
        return self.sim.state.alive

    def get_final_stats(self):
        s = self.sim.state
        return {
            "name": self.name,
            "survived_years": s.year,
            "final_population": s.population,
            "turns_played": self.turns,
            "death_message": s.victory_message if not s.alive else "Still alive!",
            "alive": s.alive
        }


def run_battle():
    """Run an interactive AI battle"""
    print("="*70)
    print("🤖 AI vs AI BATTLE - ChatGPT vs Claude")
    print("="*70)
    print("\nHow to play:")
    print("1. Copy the game state for each AI")
    print("2. Paste it to ChatGPT and Claude (separate conversations)")
    print("3. Copy their decisions back here")
    print("4. Watch them compete!\n")

    input("Press Enter to start...")

    chatgpt = AIPlayer("ChatGPT")
    claude = AIPlayer("Claude")

    turn = 0
    max_turns = 100  # Safety limit

    while (chatgpt.is_alive() or claude.is_alive()) and turn < max_turns:
        turn += 1
        print("\n" + "="*70)
        print(f"TURN {turn}")
        print("="*70)

        # ChatGPT's turn
        if chatgpt.is_alive():
            print("\n" + "-"*70)
            print("🟢 CHATGPT'S TURN")
            print("-"*70)
            print("\nCopy this to ChatGPT:\n")
            print(chatgpt.get_game_state_prompt())
            print("-"*70)

            decision = input("\n📝 Paste ChatGPT's decision: ").strip()
            if decision.lower() == 'quit':
                break

            result = chatgpt.process_ai_decision(decision)
            print(f"✅ {result}")

            if not chatgpt.is_alive():
                print(f"\n💀 ChatGPT DIED: {chatgpt.sim.state.victory_message}")

        # Claude's turn
        if claude.is_alive():
            print("\n" + "-"*70)
            print("🔵 CLAUDE'S TURN")
            print("-"*70)
            print("\nCopy this to Claude:\n")
            print(claude.get_game_state_prompt())
            print("-"*70)

            decision = input("\n📝 Paste Claude's decision: ").strip()
            if decision.lower() == 'quit':
                break

            result = claude.process_ai_decision(decision)
            print(f"✅ {result}")

            if not claude.is_alive():
                print(f"\n💀 Claude DIED: {claude.sim.state.victory_message}")

        # Quick status
        print(f"\n📊 Status:")
        if chatgpt.is_alive():
            print(f"   ChatGPT: Year {chatgpt.sim.state.year}, Pop {chatgpt.sim.state.population}")
        else:
            print(f"   ChatGPT: DEAD")

        if claude.is_alive():
            print(f"   Claude: Year {claude.sim.state.year}, Pop {claude.sim.state.population}")
        else:
            print(f"   Claude: DEAD")

    # Final results
    print("\n" + "="*70)
    print("🏆 BATTLE RESULTS")
    print("="*70)

    chatgpt_stats = chatgpt.get_final_stats()
    claude_stats = claude.get_final_stats()

    print(f"\n🟢 ChatGPT:")
    print(f"   Survived: {chatgpt_stats['survived_years']} years")
    print(f"   Population: {chatgpt_stats['final_population']}")
    print(f"   Turns: {chatgpt_stats['turns_played']}")
    print(f"   Status: {chatgpt_stats['death_message']}")

    print(f"\n🔵 Claude:")
    print(f"   Survived: {claude_stats['survived_years']} years")
    print(f"   Population: {claude_stats['final_population']}")
    print(f"   Turns: {claude_stats['turns_played']}")
    print(f"   Status: {claude_stats['death_message']}")

    # Determine winner
    print("\n" + "="*70)

    if chatgpt_stats['alive'] and not claude_stats['alive']:
        print("🏆 WINNER: ChatGPT (survived longer)")
    elif claude_stats['alive'] and not chatgpt_stats['alive']:
        print("🏆 WINNER: Claude (survived longer)")
    elif chatgpt_stats['survived_years'] > claude_stats['survived_years']:
        print("🏆 WINNER: ChatGPT (survived more years)")
    elif claude_stats['survived_years'] > chatgpt_stats['survived_years']:
        print("🏆 WINNER: Claude (survived more years)")
    elif chatgpt_stats['final_population'] > claude_stats['final_population']:
        print("🏆 WINNER: ChatGPT (saved more people)")
    elif claude_stats['final_population'] > chatgpt_stats['final_population']:
        print("🏆 WINNER: Claude (saved more people)")
    else:
        print("🤝 TIE!")

    print("="*70)

    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "chatgpt": chatgpt_stats,
        "claude": claude_stats
    }

    filename = f"battle_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Results saved to: {filename}")


if __name__ == "__main__":
    try:
        run_battle()
    except KeyboardInterrupt:
        print("\n\n⏸️  Battle interrupted!")
