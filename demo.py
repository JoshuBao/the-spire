#!/usr/bin/env python3
"""
Visual demo - Watch Claude play The Spire in slow motion
Shows exactly what's happening each turn
"""

import time
from main import Simulation

def print_tower_visual(sim):
    """Print a visual representation of the tower"""
    s = sim.state

    print("\n" + "="*60)
    print("THE TOWER:")
    print("="*60)

    for i in range(s.max_height, 0, -1):
        sector = s.get_sector(i)

        if sector:
            symbol, color = sector.get_display()
            health_bar = "█" * int(sector.health / 10)
            health_empty = "░" * (10 - int(sector.health / 10))

            cursor = "→" if i == s.cursor else " "
            fire = "🔥" if sector.on_fire else "  "
            sector_name = sector.sector_type.value[2]

            print(f"{cursor} L{i:2d} {symbol} {sector_name:8s} [{health_bar}{health_empty}] {sector.workers:2d}w {fire}")
        else:
            cursor = "→" if i == s.cursor else " "
            print(f"{cursor} L{i:2d} ... empty ...")

    print("     ╚═════╝ Base")


def demo_playthrough(turns=20, delay=1.0):
    """Play the game with visual output and delays"""
    sim = Simulation()

    print("\n" + "="*60)
    print("🎮 CLAUDE PLAYS THE SPIRE - VISUAL DEMO")
    print("="*60)
    print("\nWatch as I manage the tower, handle crises, and make")
    print("strategic decisions in real-time...")
    print("\nPress Ctrl+C to stop early\n")

    time.sleep(2)

    for turn in range(turns):
        s = sim.state

        # Clear and show status
        print("\n" + "█"*60)
        print(f"YEAR {s.year}, MONTH {s.month} - TURN {turn + 1}")
        print("█"*60)

        # Show resources
        print(f"\n📊 Status: Pop={s.population} | Food={s.food:.0f} | Power={s.power:.0f} | Materials={s.materials:.0f} | Morale={s.morale:.0f}% | Tension={s.tension:.0f}%")

        # Show tower
        print_tower_visual(sim)

        # Check for alerts
        fires = [sec for sec in s.sectors if sec.on_fire]
        critical = [sec for sec in s.sectors if 0 < sec.health < 30]

        if fires or critical or s.current_dilemma:
            print("\n⚠️  ALERTS:")
            if fires:
                print(f"   🔥 FIRE on levels: {[sec.level for sec in fires]}")
            if critical:
                print(f"   💀 CRITICAL sectors: {[sec.level for sec in critical]}")
            if s.current_dilemma:
                print(f"   ❓ {s.current_dilemma.title}: {s.current_dilemma.description}")

        # Decide action
        action = "wait"
        reason = "Stockpiling"

        # Handle dilemma
        if s.current_dilemma:
            if s.materials >= 50:
                s.current_dilemma.consequence_a()
                action = "SAVE SECTOR"
                reason = "Have materials to reinforce"
            else:
                s.current_dilemma.consequence_b()
                action = "EVACUATE"
                reason = "Can't afford to save it"
            s.current_dilemma = None

        # Emergency: fires
        elif fires and s.power >= 30:
            s.cursor = fires[0].level
            action = "EXTINGUISH"
            reason = f"Fire spreading on Level {fires[0].level}"
            sim.advance_turn("extinguish")

        # Emergency: critical sectors
        elif critical and s.materials >= 40:
            s.cursor = critical[0].level
            action = "REPAIR"
            reason = f"Level {critical[0].level} about to collapse"
            sim.advance_turn("repair")

        # Build if we have resources
        elif s.materials >= 120 and len(s.sectors) < s.max_height:
            action = "BUILD"
            reason = "Expanding upward"
            sim.advance_turn("build")

        # Boost morale if low
        elif s.morale < 40 and s.food >= 40 and s.power >= 20:
            action = "FESTIVAL"
            reason = "Preventing morale crisis"
            sim.advance_turn("boost_morale")

        # Default: wait
        else:
            action = "WAIT"
            reason = "Accumulating resources"
            sim.advance_turn("wait")

        print(f"\n🎮 Action: {action}")
        print(f"   Reason: {reason}")

        # Show recent events
        if s.events and len(s.events) > 0:
            print(f"\n📰 Latest Event:")
            event_text, color = s.events[-1]
            print(f"   {event_text}")

        # Check if game over
        if not s.alive:
            print(f"\n💀 GAME OVER: {s.victory_message}")
            break

        # Delay for readability
        time.sleep(delay)

    # Final summary
    print("\n" + "="*60)
    print("📊 DEMO COMPLETE")
    print("="*60)
    print(f"\nSurvived: Year {sim.state.year}, Month {sim.state.month}")
    print(f"Population: {sim.state.population}")
    print(f"Levels: {len(sim.state.sectors)}/{sim.state.max_height}")
    print(f"Morale: {sim.state.morale:.0f}%")
    print("\n✅ All game mechanics working correctly!")
    print("\nReady to play? Run: ./run.sh\n")


if __name__ == "__main__":
    try:
        # Run a 20-turn demo with 1 second between turns
        demo_playthrough(turns=20, delay=1.0)
    except KeyboardInterrupt:
        print("\n\n⏸️  Demo interrupted. Game is ready to play!")
        print("\nRun: ./run.sh\n")
