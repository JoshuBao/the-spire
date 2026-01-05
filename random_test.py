#!/usr/bin/env python3
"""
Random Play Test - How often can you win with random decisions?
Tests game balance by playing completely randomly
"""

import random
from main import Simulation

def play_random_game(max_turns=200, verbose=False):
    """Play one game with completely random actions"""
    sim = Simulation()
    turns = 0

    while sim.state.alive and turns < max_turns:
        s = sim.state

        # Handle dilemmas randomly
        if s.current_dilemma:
            if random.choice([True, False]):
                s.current_dilemma.consequence_a()
            else:
                s.current_dilemma.consequence_b()
            s.current_dilemma = None
            sim.advance_turn("wait")
            turns += 1
            continue

        # Choose random action
        available_actions = ["wait"]

        # Can repair if we have materials
        if s.materials >= 40:
            available_actions.append("repair")

        # Can extinguish if we have power
        if s.power >= 30:
            available_actions.append("extinguish")

        # Can build if not at max and have materials
        if len(s.sectors) < s.max_height and s.materials >= 80:
            available_actions.extend(["build_farm", "build_power", "build_industry", "build_housing"])

        # Can boost morale if we have resources
        if s.food >= 40 and s.power >= 20:
            available_actions.append("boost_morale")

        # Can do emergency rations
        if s.population > 30:
            available_actions.append("emergency_rations")

        # Pick random action
        action = random.choice(available_actions)

        # If repair/extinguish, pick random level
        if action in ["repair", "extinguish"]:
            if s.sectors:
                s.cursor = random.choice([sec.level for sec in s.sectors])

        sim.advance_turn(action)
        turns += 1

        if verbose and turns % 20 == 0:
            print(f"  Turn {turns}: Pop={s.population}, Year={s.year}, Food={s.food:.0f}, Sectors={len(s.sectors)}")

    # Return results
    result = {
        "won": s.alive and s.year >= 50,
        "survived_years": s.year,
        "final_population": s.population,
        "turns": turns,
        "death_reason": s.victory_message if not s.alive else "Still alive"
    }

    return result


def run_trials(num_trials=100):
    """Run multiple random games and analyze results"""
    print("="*70)
    print("RANDOM PLAY TEST - Testing Game Balance")
    print("="*70)
    print(f"\nRunning {num_trials} games with completely random actions...\n")

    results = []
    wins = 0

    for i in range(num_trials):
        if (i + 1) % 10 == 0:
            print(f"Progress: {i + 1}/{num_trials} games completed...")

        result = play_random_game(max_turns=200, verbose=False)
        results.append(result)

        if result["won"]:
            wins += 1

    # Analyze results
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)

    win_rate = (wins / num_trials) * 100
    print(f"\n🏆 Win Rate: {wins}/{num_trials} ({win_rate:.1f}%)")

    # Survival statistics
    years_survived = [r["survived_years"] for r in results]
    avg_years = sum(years_survived) / len(years_survived)
    max_years = max(years_survived)
    min_years = min(years_survived)

    print(f"\n📊 Survival Statistics:")
    print(f"  Average years survived: {avg_years:.1f}")
    print(f"  Best run: {max_years} years")
    print(f"  Worst run: {min_years} years")

    # Population statistics
    final_pops = [r["final_population"] for r in results]
    avg_pop = sum(final_pops) / len(final_pops)

    print(f"\n👥 Population:")
    print(f"  Average final population: {avg_pop:.1f}")

    # Death reasons
    death_reasons = {}
    for r in results:
        if not r["won"]:
            reason = r["death_reason"]
            # Categorize
            if "EXTINCTION" in reason:
                category = "Starvation/Population Loss"
            elif "COLLAPSE" in reason:
                category = "All Sectors Destroyed"
            else:
                category = "Other"

            death_reasons[category] = death_reasons.get(category, 0) + 1

    if death_reasons:
        print(f"\n💀 Common Death Causes:")
        for reason, count in sorted(death_reasons.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / (num_trials - wins)) * 100
            print(f"  {reason}: {count} ({percentage:.1f}%)")

    # Survival distribution
    print(f"\n📈 Survival Distribution:")
    buckets = {
        "Year 1-5": 0,
        "Year 6-10": 0,
        "Year 11-20": 0,
        "Year 21-30": 0,
        "Year 31-49": 0,
        "Year 50+ (Win)": 0
    }

    for years in years_survived:
        if years <= 5:
            buckets["Year 1-5"] += 1
        elif years <= 10:
            buckets["Year 6-10"] += 1
        elif years <= 20:
            buckets["Year 11-20"] += 1
        elif years <= 30:
            buckets["Year 21-30"] += 1
        elif years < 50:
            buckets["Year 31-49"] += 1
        else:
            buckets["Year 50+ (Win)"] += 1

    for bucket, count in buckets.items():
        percentage = (count / num_trials) * 100
        bar = "█" * int(percentage / 2)
        print(f"  {bucket:15s}: {bar} {count} ({percentage:.1f}%)")

    # Analysis
    print("\n" + "="*70)
    print("ANALYSIS")
    print("="*70)

    if win_rate > 20:
        print("\n⚠️  Game might be TOO EASY")
        print(f"   Random play wins {win_rate:.1f}% of the time")
        print("   Consider increasing difficulty")
    elif win_rate > 5:
        print("\n✅ Game balance is GOOD")
        print(f"   Random play wins {win_rate:.1f}% of the time")
        print("   Skilled play should do much better")
    elif win_rate > 0:
        print("\n✅ Game is CHALLENGING")
        print(f"   Random play rarely wins ({win_rate:.1f}%)")
        print("   Strategy is important")
    else:
        print("\n⚠️  Game might be TOO HARD")
        print("   Even random play should occasionally win by luck")
        print("   Consider slight difficulty adjustment")

    if avg_years < 10:
        print(f"\n⚠️  Games end very quickly (avg {avg_years:.1f} years)")
        print("   Players might not have time to develop strategies")
    elif avg_years > 30:
        print(f"\n⚠️  Games last a long time (avg {avg_years:.1f} years)")
        print("   Might feel grindy")
    else:
        print(f"\n✅ Good game length (avg {avg_years:.1f} years)")

    print("\n" + "="*70)
    print("Random play test complete!")
    print("="*70)

    return results


if __name__ == "__main__":
    import sys

    # Default to 100 trials, but allow override
    num_trials = int(sys.argv[1]) if len(sys.argv) > 1 else 100

    results = run_trials(num_trials)

    print("\n💡 TIP: Run with more trials for better statistics:")
    print("   python random_test.py 500")
