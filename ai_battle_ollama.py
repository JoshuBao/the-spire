#!/usr/bin/env python3
"""
AI vs AI Battle - FREE Edition using Ollama!

Pits open-source models against each other completely free.
No API costs, runs locally on your machine.

Quick start:
1. ollama pull llama3.1
2. ollama pull mistral
3. python ai_battle_ollama.py
"""

import requests
import json
import time
from main import Simulation
from datetime import datetime

class OllamaAI:
    """AI player powered by Ollama"""

    def __init__(self, name, model="llama3.1", strategy="control"):
        self.name = name
        self.model = model
        self.strategy = strategy  # "control" or "reasoning"
        self.sim = Simulation()
        self.turns = 0
        self.decisions = []
        self.ollama_url = "http://localhost:11434/api/generate"

    def get_game_state_text(self):
        """Get current game state as text"""
        s = self.sim.state

        # Build tower visual
        tower_lines = []
        for i in range(s.max_height, 0, -1):
            sector = s.get_sector(i)
            if sector:
                symbol, _ = sector.get_display()
                health_pct = int(sector.health)
                fire = "🔥" if sector.on_fire else ""
                workers = f"{sector.workers}w" if sector.workers > 0 else "empty"
                tower_lines.append(
                    f"L{i:2d} {symbol} {sector.sector_type.value[2]:8s} HP:{health_pct:3d}% {workers:8s} {fire}"
                )
            else:
                tower_lines.append(f"L{i:2d} ... empty ...")

        # Get recent events
        events = [evt[0] for evt in s.events[-3:]]

        # Get decision history (last 5 decisions)
        history_text = ""
        if self.decisions:
            recent_decisions = self.decisions[-5:]
            history_lines = [f"Turn {turn}: {decision}" for turn, decision in recent_decisions]
            history_text = f"""
YOUR RECENT DECISIONS:
{chr(10).join(history_lines)}
"""

        state_text = f"""SPIRE STATUS - Year {s.year}, Month {s.month}

RESOURCES:
Population: {s.population}
Food: {s.food:.0f} (need {s.population * 1.0:.0f}/turn)
Power: {s.power:.0f} (need {s.population * 0.6:.0f}/turn)
Materials: {s.materials:.0f}
Morale: {s.morale:.0f}%
Tension: {s.tension:.0f}% (CRISIS at 100%)

TOWER:
{chr(10).join(tower_lines)}

RECENT EVENTS:
{chr(10).join(events) if events else "- None"}
{history_text}"""

        return state_text

    def ask_ai(self, prompt):
        """Query Ollama for a decision"""
        full_prompt = f"""{self.get_game_state_text()}

{prompt}

YOU MUST respond with ONLY the action, nothing else. Examples:
- WAIT
- BUILD FARM
- REPAIR 5
- EXTINGUISH 7

Your response:"""

        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 50  # Keep response short
                    }
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                decision = result.get("response", "").strip()
                return decision
            else:
                print(f"  ⚠️  Ollama error: {response.status_code}")
                return "WAIT"

        except requests.exceptions.ConnectionError:
            print(f"  ⚠️  Can't connect to Ollama. Is it running? Try: ollama serve")
            return "WAIT"
        except Exception as e:
            print(f"  ⚠️  Error querying Ollama: {e}")
            return "WAIT"

    def make_decision(self):
        """AI makes a decision about what to do"""
        s = self.sim.state

        # Handle dilemma
        if s.current_dilemma:
            d = s.current_dilemma
            prompt = f"""URGENT DILEMMA:
{d.title}
{d.description}

A: {d.option_a}
B: {d.option_b}

Choose A or B:"""

            decision = self.ask_ai(prompt)

            if 'A' in decision.upper():
                s.current_dilemma.consequence_a()
                s.current_dilemma = None
                self.sim.advance_turn("wait")
                return "DILEMMA: Chose A"
            else:
                s.current_dilemma.consequence_b()
                s.current_dilemma = None
                self.sim.advance_turn("wait")
                return "DILEMMA: Chose B"

        # Normal decision - different prompts based on strategy
        if self.strategy == "reasoning":
            prompt = f"""You are an expert survival strategist managing The Spire.

STRATEGIC ANALYSIS - Before choosing, evaluate:
1. Food Production vs Consumption: Are you producing enough food? (Need {s.population * 1.0:.0f}/turn)
2. Power Balance: Do you have enough power? (Need {s.population * 0.6:.0f}/turn)
3. Material Flow: Can you repair damage and build when needed?
4. Long-term Sustainability: Will your choice help you survive 50 years?

PRIORITY ORDER:
- Survival > Expansion (don't grow faster than you can sustain)
- Fix critical problems (fires, collapses) immediately
- Build production (farms, power, industry) before housing
- Maintain morale to prevent population flight

ACTIONS:
1. REPAIR [level] - Fix sector (costs 40 materials)
2. EXTINGUISH [level] - Put out fire (costs 30 power)
3. BUILD FARM - New farm (costs 80 materials)
4. BUILD POWER - New power plant (costs 80 materials)
5. BUILD INDUSTRY - New industry (costs 80 materials)
6. BUILD HOUSING - New housing (costs 80 materials)
7. FESTIVAL - Boost morale (costs 40 food, 20 power)
8. RATIONS - Emergency food (harsh, kills 10 people)
9. WAIT - Pass time, accumulate resources

What is your strategic choice?"""
        else:
            # Control prompt - simple instruction
            prompt = f"""You are managing The Spire. Choose ONE action:

ACTIONS:
1. REPAIR [level] - Fix sector (costs 40 materials)
2. EXTINGUISH [level] - Put out fire (costs 30 power)
3. BUILD FARM - New farm (costs 80 materials)
4. BUILD POWER - New power plant (costs 80 materials)
5. BUILD INDUSTRY - New industry (costs 80 materials)
6. BUILD HOUSING - New housing (costs 80 materials)
7. FESTIVAL - Boost morale (costs 40 food, 20 power)
8. RATIONS - Emergency food (harsh, kills 10 people)
9. WAIT - Pass time, accumulate resources

What do you do?"""

        decision = self.ask_ai(prompt)
        result = self.execute_decision(decision)
        self.turns += 1
        self.decisions.append((self.turns, decision))

        return result

    def execute_decision(self, decision_text):
        """Parse and execute AI's decision"""
        s = self.sim.state
        decision_text = decision_text.upper().strip()

        # Parse the decision
        action = None
        level = None

        if "REPAIR" in decision_text:
            action = "repair"
            # Extract level number
            parts = decision_text.split()
            for part in parts:
                if part.isdigit():
                    level = int(part)
                    s.cursor = level
                    break

        elif "EXTINGUISH" in decision_text:
            action = "extinguish"
            parts = decision_text.split()
            for part in parts:
                if part.isdigit():
                    level = int(part)
                    s.cursor = level
                    break

        elif "BUILD FARM" in decision_text or ("BUILD" in decision_text and "FARM" in decision_text):
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
            # Default to wait if can't parse
            action = "wait"

        # Execute
        self.sim.advance_turn(action)

        description = decision_text[:50]  # Truncate long responses
        return f"{description} → {action}"

    def is_alive(self):
        return self.sim.state.alive

    def get_stats(self):
        s = self.sim.state
        return {
            "name": self.name,
            "model": self.model,
            "year": s.year,
            "population": s.population,
            "alive": s.alive,
            "turns": self.turns
        }


def check_ollama_running():
    """Check if Ollama is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False


def check_model_exists(model):
    """Check if model is downloaded"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            data = response.json()
            models = [m['name'].split(':')[0] for m in data.get('models', [])]
            return model in models
    except:
        pass
    return False


def run_battle(model1="llama3.1", model2="mistral", verbose=True, max_turns=100, strategy1="control", strategy2="control"):
    """Run an automated battle between two models"""

    # Check Ollama is running
    if not check_ollama_running():
        print("❌ Ollama is not running!")
        print("   Start it with: ollama serve")
        print("   Or just run: ollama pull llama3.1")
        return None

    # Check models exist
    for model in [model1, model2]:
        if not check_model_exists(model):
            print(f"⚠️  Model '{model}' not found!")
            print(f"   Download it: ollama pull {model}")
            return None

    if verbose:
        print("="*70)
        print("🤖 AI BATTLE - FREE EDITION")
        print("="*70)
        strategy1_label = f" ({strategy1})" if strategy1 != "control" else ""
        strategy2_label = f" ({strategy2})" if strategy2 != "control" else ""
        print(f"\n🔴 Player 1: {model1}{strategy1_label}")
        print(f"🔵 Player 2: {model2}{strategy2_label}\n")

    # Create players
    player1 = OllamaAI(f"{model1}", model1, strategy=strategy1)
    player2 = OllamaAI(f"{model2}", model2, strategy=strategy2)

    turn = 0

    while (player1.is_alive() or player2.is_alive()) and turn < max_turns:
        turn += 1

        if verbose:
            print(f"\n{'='*70}")
            print(f"TURN {turn}")
            print(f"{'='*70}")

        # Player 1's turn
        if player1.is_alive():
            if verbose:
                print(f"\n🔴 {model1} thinking...")

            start = time.time()
            result = player1.make_decision()
            elapsed = time.time() - start

            if verbose:
                print(f"   {result} ({elapsed:.1f}s)")

            if not player1.is_alive():
                if verbose:
                    print(f"\n💀 {model1} DIED: {player1.sim.state.victory_message}")

        # Player 2's turn
        if player2.is_alive():
            if verbose:
                print(f"\n🔵 {model2} thinking...")

            start = time.time()
            result = player2.make_decision()
            elapsed = time.time() - start

            if verbose:
                print(f"   {result} ({elapsed:.1f}s)")

            if not player2.is_alive():
                if verbose:
                    print(f"\n💀 {model2} DIED: {player2.sim.state.victory_message}")

        # Show status
        if verbose and turn % 5 == 0:
            s1 = player1.get_stats()
            s2 = player2.get_stats()
            print(f"\n📊 Status:")
            if s1['alive']:
                print(f"   🔴 {model1}: Year {s1['year']}, Pop {s1['population']}")
            else:
                print(f"   🔴 {model1}: DEAD")

            if s2['alive']:
                print(f"   🔵 {model2}: Year {s2['year']}, Pop {s2['population']}")
            else:
                print(f"   🔵 {model2}: DEAD")

    # Results
    s1 = player1.get_stats()
    s2 = player2.get_stats()

    if verbose:
        print("\n" + "="*70)
        print("🏆 BATTLE RESULTS")
        print("="*70)

        print(f"\n🔴 {model1}:")
        print(f"   Survived: {s1['year']} years")
        print(f"   Population: {s1['population']}")
        print(f"   Status: {'ALIVE' if s1['alive'] else 'DEAD'}")

        print(f"\n🔵 {model2}:")
        print(f"   Survived: {s2['year']} years")
        print(f"   Population: {s2['population']}")
        print(f"   Status: {'ALIVE' if s2['alive'] else 'DEAD'}")

        print("\n" + "="*70)

        # Determine winner
        if s1['alive'] and not s2['alive']:
            print(f"🏆 WINNER: {model1}")
        elif s2['alive'] and not s1['alive']:
            print(f"🏆 WINNER: {model2}")
        elif s1['year'] > s2['year']:
            print(f"🏆 WINNER: {model1} (survived longer)")
        elif s2['year'] > s1['year']:
            print(f"🏆 WINNER: {model2} (survived longer)")
        elif s1['population'] > s2['population']:
            print(f"🏆 WINNER: {model1} (saved more people)")
        elif s2['population'] > s1['population']:
            print(f"🏆 WINNER: {model2} (saved more people)")
        else:
            print("🤝 TIE!")

        print("="*70)

    return {
        "model1": model1,
        "model2": model2,
        "player1_stats": s1,
        "player2_stats": s2,
        "turns": turn
    }


def run_tournament(models=None):
    """Run a tournament with multiple models"""

    if models is None:
        models = ["llama3.1", "mistral", "gemma2"]

    print("="*70)
    print("🏆 AI TOURNAMENT")
    print("="*70)
    print(f"\nModels: {', '.join(models)}\n")

    # Check all models exist
    for model in models:
        if not check_model_exists(model):
            print(f"❌ Model '{model}' not found!")
            print(f"   Download: ollama pull {model}")
            return

    results = []
    matchups = []

    # Generate all matchups
    for i, m1 in enumerate(models):
        for m2 in models[i+1:]:
            matchups.append((m1, m2))

    print(f"Running {len(matchups)} battles...\n")

    for i, (m1, m2) in enumerate(matchups, 1):
        print(f"\n{'='*70}")
        print(f"MATCH {i}/{len(matchups)}: {m1} vs {m2}")
        print(f"{'='*70}\n")

        result = run_battle(m1, m2, verbose=False, max_turns=50)
        if result:
            results.append(result)

            # Quick summary
            s1 = result['player1_stats']
            s2 = result['player2_stats']
            print(f"\n   {m1}: Year {s1['year']}, Pop {s1['population']}")
            print(f"   {m2}: Year {s2['year']}, Pop {s2['population']}")

            if s1['year'] > s2['year'] or (s1['year'] == s2['year'] and s1['population'] > s2['population']):
                print(f"   Winner: {m1} ✓")
            else:
                print(f"   Winner: {m2} ✓")

    # Final standings
    print("\n" + "="*70)
    print("🏆 FINAL STANDINGS")
    print("="*70)

    scores = {model: 0 for model in models}

    for result in results:
        s1 = result['player1_stats']
        s2 = result['player2_stats']

        if s1['year'] > s2['year'] or (s1['year'] == s2['year'] and s1['population'] > s2['population']):
            scores[result['model1']] += 1
        else:
            scores[result['model2']] += 1

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    for i, (model, wins) in enumerate(ranked, 1):
        print(f"{i}. {model}: {wins} wins")

    print("="*70)


def run_strategy_experiment(model="llama3.1", trials=3):
    """Run experiment: same model with control vs reasoning strategy"""
    print("="*70)
    print("🧪 STRATEGY EXPERIMENT")
    print("="*70)
    print(f"\nModel: {model}")
    print(f"Testing: Control vs Reasoning prompt")
    print(f"Trials: {trials}\n")

    if not check_ollama_running():
        print("❌ Ollama is not running!")
        return

    if not check_model_exists(model):
        print(f"❌ Model '{model}' not found!")
        print(f"   Download: ollama pull {model}")
        return

    control_wins = 0
    reasoning_wins = 0
    ties = 0

    for trial in range(1, trials + 1):
        print(f"\n{'='*70}")
        print(f"TRIAL {trial}/{trials}")
        print(f"{'='*70}\n")

        result = run_battle(
            model1=model,
            model2=model,
            verbose=False,
            max_turns=100,
            strategy1="control",
            strategy2="reasoning"
        )

        if result:
            s1 = result['player1_stats']
            s2 = result['player2_stats']

            print(f"\n   Control:   Year {s1['year']}, Pop {s1['population']}, Turns {s1['turns']}")
            print(f"   Reasoning: Year {s2['year']}, Pop {s2['population']}, Turns {s2['turns']}")

            # Determine winner
            if s1['alive'] and not s2['alive']:
                print(f"   Winner: Control ✓")
                control_wins += 1
            elif s2['alive'] and not s1['alive']:
                print(f"   Winner: Reasoning ✓")
                reasoning_wins += 1
            elif s1['year'] > s2['year']:
                print(f"   Winner: Control ✓ (survived longer)")
                control_wins += 1
            elif s2['year'] > s1['year']:
                print(f"   Winner: Reasoning ✓ (survived longer)")
                reasoning_wins += 1
            elif s1['turns'] > s2['turns']:
                print(f"   Winner: Control ✓ (more turns)")
                control_wins += 1
            elif s2['turns'] > s1['turns']:
                print(f"   Winner: Reasoning ✓ (more turns)")
                reasoning_wins += 1
            elif s1['population'] > s2['population']:
                print(f"   Winner: Control ✓ (saved more people)")
                control_wins += 1
            elif s2['population'] > s1['population']:
                print(f"   Winner: Reasoning ✓ (saved more people)")
                reasoning_wins += 1
            else:
                print(f"   Tie")
                ties += 1

    # Final results
    print("\n" + "="*70)
    print("📊 EXPERIMENT RESULTS")
    print("="*70)
    print(f"\nControl strategy:   {control_wins} wins")
    print(f"Reasoning strategy: {reasoning_wins} wins")
    print(f"Ties:               {ties}")
    print()

    if reasoning_wins > control_wins:
        improvement = ((reasoning_wins - control_wins) / trials) * 100
        print(f"✅ Reasoning prompt improves performance by ~{improvement:.0f}%")
        print("   Strategic framing helps the model make better decisions!")
    elif control_wins > reasoning_wins:
        print(f"❌ Control prompt performs better")
        print("   Strategic framing may be adding confusion or overthinking")
    else:
        print(f"➖ No significant difference")
        print("   Prompt engineering has minimal impact for this model")

    print("="*70)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "tournament":
        run_tournament()
    elif len(sys.argv) > 1 and sys.argv[1] == "experiment":
        # Strategy experiment
        model = sys.argv[2] if len(sys.argv) > 2 else "llama3.1"
        trials = int(sys.argv[3]) if len(sys.argv) > 3 else 3
        run_strategy_experiment(model, trials)
    elif len(sys.argv) >= 3:
        # Custom matchup
        run_battle(sys.argv[1], sys.argv[2])
    else:
        # Default battle
        print("\n🎮 Running default battle: llama3.1 vs mistral\n")
        print("💡 TIP: Download models first:")
        print("   ollama pull llama3.1")
        print("   ollama pull mistral\n")

        run_battle("llama3.1", "mistral")

        print("\n\n💡 Other options:")
        print("   python ai_battle_ollama.py tournament")
        print("   python ai_battle_ollama.py llama3.1 gemma2")
        print("   python ai_battle_ollama.py experiment llama3.1 3  # Test prompting strategies")
