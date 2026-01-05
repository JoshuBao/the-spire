#!/usr/bin/env python3
"""
THE SPIRE - Vertical City Crisis Management
============================================

You manage a desperate city built vertically around an ancient tower.
Each level is a sector with its own purpose, dangers, and stories.

This is not a peaceful building sim. This is crisis management.
Fires spread. Sectors collapse. People panic. You make impossible choices.

The question isn't "will something go wrong?" - it's "what will you sacrifice when it does?"

Controls:
↑/↓ or W/S - Navigate levels
1-5 - Actions (see help panel)
SPACE - Wait/advance time
Q - Quit
"""

import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from enum import Enum

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Header, Footer
from textual.reactive import reactive
from textual import events
from rich.text import Text
from rich.panel import Panel
from rich.table import Table


class SectorType(Enum):
    RESIDENTIAL = ("🏠", "cyan", "Housing")
    FARMS = ("🌾", "green", "Farms")
    POWER = ("⚡", "yellow", "Power")
    INDUSTRIAL = ("⚙️", "magenta", "Industry")
    EMPTY = ("░░", "dim white", "Empty")


class DisasterType(Enum):
    FIRE = ("🔥", "red")
    COLLAPSE = ("💥", "red")
    DISEASE = ("🦠", "magenta")
    RIOTS = ("✊", "yellow")


@dataclass
class Sector:
    level: int
    sector_type: SectorType
    health: float = 100.0
    workers: int = 0
    disaster: Optional[DisasterType] = None
    disaster_intensity: int = 0
    on_fire: bool = False
    fire_turns: int = 0
    unstable: bool = False
    quarantined: bool = False

    def get_display(self) -> Tuple[str, str]:
        """Return (symbol, color) for rendering"""
        if self.disaster:
            return self.disaster.value

        # Show damage state
        if self.health < 30:
            return ("💀", "red")
        elif self.health < 60:
            return ("⚠️", "yellow")

        return self.sector_type.value[0:2]

    def is_functional(self) -> bool:
        return self.health > 20 and not self.on_fire


@dataclass
class Citizen:
    name: str
    role: str
    location: int
    alive: bool = True


@dataclass
class Dilemma:
    title: str
    description: str
    option_a: str
    option_b: str
    consequence_a: callable
    consequence_b: callable


@dataclass
class GameState:
    year: int = 1
    month: int = 1

    # Resources
    food: float = 150.0
    power: float = 100.0
    materials: float = 80.0

    # Population
    population: int = 85
    morale: float = 65.0

    # Tower
    sectors: List[Sector] = field(default_factory=list)
    max_height: int = 12

    # Characters
    citizens: List[Citizen] = field(default_factory=list)

    # Events
    events: List[Tuple[str, str]] = field(default_factory=list)
    current_dilemma: Optional[Dilemma] = None

    # Pacing
    tension: float = 0.0
    turns_since_crisis: int = 0

    # State
    alive: bool = True
    victory_message: str = ""
    cursor: int = 5
    building_mode: bool = False  # True when choosing building type

    def __post_init__(self):
        if not self.sectors:
            self._initialize_tower()
        if not self.citizens:
            self._initialize_citizens()

    def _initialize_tower(self):
        """Create starting sectors"""
        configs = [
            (1, SectorType.POWER),
            (2, SectorType.INDUSTRIAL),
            (3, SectorType.RESIDENTIAL),
            (4, SectorType.FARMS),
            (5, SectorType.RESIDENTIAL),
            (6, SectorType.FARMS),
            (7, SectorType.POWER),
            (8, SectorType.RESIDENTIAL),
        ]

        for level, stype in configs:
            sector = Sector(level=level, sector_type=stype, workers=random.randint(8, 15))
            self.sectors.append(sector)

    def _initialize_citizens(self):
        """Create named characters"""
        names = ["Chen", "Maria", "Akeno", "Viktor", "Zara", "Kim", "Raj"]
        roles = ["Engineer", "Farmer", "Doctor", "Builder", "Guard", "Scientist"]

        for name in names[:5]:
            role = random.choice(roles)
            location = random.choice([s.level for s in self.sectors])
            self.citizens.append(Citizen(name, role, location))

    def get_sector(self, level: int) -> Optional[Sector]:
        for s in self.sectors:
            if s.level == level:
                return s
        return None


class Simulation:
    def __init__(self):
        self.state = GameState()
        self._add_event("⚡ The Spire awakens. Your people huddle in its shadow.", "cyan")
        self._add_event("⚠️  The Tower is unstable. Disasters will come. Be ready.", "yellow")

    def advance_turn(self, action: str = "wait"):
        """Main simulation tick"""
        s = self.state

        # Advance time
        s.month += 1
        if s.month > 12:
            s.month = 1
            s.year += 1

        s.turns_since_crisis += 1

        # Process action
        if action != "wait":
            self._process_action(action)

        # === PRODUCTION PHASE ===
        power_gen = 0
        food_gen = 0
        materials_gen = 0

        for sector in s.sectors:
            if not sector.is_functional():
                continue

            efficiency = sector.health / 100.0

            if sector.sector_type == SectorType.POWER:
                power_gen += sector.workers * 3 * efficiency
            elif sector.sector_type == SectorType.FARMS:
                food_gen += sector.workers * 2.5 * efficiency
            elif sector.sector_type == SectorType.INDUSTRIAL:
                materials_gen += sector.workers * 2 * efficiency

        s.power += power_gen
        s.food += food_gen
        s.materials += materials_gen

        # === CONSUMPTION PHASE ===
        power_cost = s.population * 0.6
        food_cost = s.population * 1.0

        s.power -= power_cost
        s.food -= food_cost

        # === CRISIS PHASE ===
        if s.food < 0:
            deaths = min(int(s.population * 0.12), 15)
            s.population -= deaths
            s.morale -= 25
            self._add_event(f"💀 STARVATION: {deaths} die from hunger", "red")
            s.food = 0

        if s.power < 0:
            s.morale -= 15
            functional = [sec for sec in s.sectors if sec.is_functional()]
            if functional:
                victim = random.choice(functional)
                victim.health -= 25
                self._add_event(f"⚡ BLACKOUT damages Level {victim.level}", "red")
            s.power = 0

        # === DISASTER PROPAGATION ===
        self._propagate_disasters()

        # === SECTOR DECAY ===
        for sector in s.sectors:
            if sector.health > 0:
                decay = 1.5
                if sector.level > 8:
                    decay *= 2
                sector.health -= decay

            if sector.health <= 0 and sector.workers > 0:
                casualties = sector.workers
                s.population -= casualties
                sector.workers = 0
                self._add_event(f"💥 Level {sector.level} COLLAPSES: {casualties} lost", "red")

                if random.random() < 0.3:
                    below = s.get_sector(sector.level - 1)
                    if below:
                        below.health -= 40
                        self._add_event(f"⚠️  Collapse damages Level {below.level}!", "yellow")

        # === MORALE & POPULATION ===
        if s.morale < 30:
            fled = random.randint(3, 8)
            s.population -= fled
            self._add_event(f"🚪 {fled} citizens flee the Spire", "yellow")

        if s.morale < 60:
            s.morale += 1.5

        if s.food > 50 and s.morale > 50 and s.month % 3 == 0:
            growth = random.randint(2, 5)
            s.population += growth

        # === TENSION & PACING ===
        s.tension += 2.5

        if s.tension > 100 or (s.turns_since_crisis > 8 and random.random() < 0.4):
            self._trigger_crisis()
            s.tension = 0
            s.turns_since_crisis = 0

        if random.random() < 0.15:
            self._trigger_minor_event()

        if s.current_dilemma is None and random.random() < 0.12:
            self._create_dilemma()

        # === WIN/LOSE ===
        if s.population <= 0:
            s.population = 0  # Prevent negative population
            s.alive = False
            s.victory_message = f"💀 EXTINCTION - The Spire stands empty. Year {s.year}"

        functional_sectors = sum(1 for sec in s.sectors if sec.is_functional())
        if functional_sectors == 0:
            s.alive = False
            s.victory_message = f"💥 TOTAL COLLAPSE - All sectors destroyed. Year {s.year}"

        if s.year >= 50:
            s.alive = False
            s.victory_message = f"🏆 LEGENDARY - {s.year} years, {s.population} survivors!"

    def _propagate_disasters(self):
        """Disasters spread spatially"""
        s = self.state

        for sector in list(s.sectors):
            if sector.on_fire:
                sector.fire_turns += 1
                sector.health -= 8

                if sector.fire_turns > 2 and random.random() < 0.4:
                    adjacent_levels = [sector.level - 1, sector.level + 1]
                    for adj_level in adjacent_levels:
                        adj_sector = s.get_sector(adj_level)
                        if adj_sector and not adj_sector.on_fire and random.random() < 0.5:
                            adj_sector.on_fire = True
                            adj_sector.fire_turns = 0
                            self._add_event(f"🔥 Fire spreads to Level {adj_level}!", "red")

                if sector.fire_turns > 5 and random.random() < 0.3:
                    sector.on_fire = False
                    self._add_event(f"🔥 Fire on Level {sector.level} burns out", "yellow")

    def _trigger_crisis(self):
        """Major disaster event"""
        crisis_types = [
            self._crisis_earthquake,
            self._crisis_fire,
            self._crisis_disease,
            self._crisis_structural_failure,
            self._crisis_riot,
        ]
        crisis = random.choice(crisis_types)
        crisis()

    def _crisis_earthquake(self):
        s = self.state
        affected = random.randint(2, 5)
        sectors_hit = random.sample(s.sectors, min(affected, len(s.sectors)))

        casualties = 0
        for sector in sectors_hit:
            damage = random.randint(20, 45)
            sector.health -= damage
            casualties += random.randint(2, 6)

        s.population -= casualties
        s.morale -= 20
        self._add_event(f"🌍 EARTHQUAKE! {affected} levels damaged, {casualties} dead", "red")

    def _crisis_fire(self):
        s = self.state
        origin = random.choice(s.sectors)
        origin.on_fire = True
        origin.fire_turns = 0
        self._add_event(f"🔥 MAJOR FIRE on Level {origin.level}! Spreading fast!", "red")

    def _crisis_disease(self):
        s = self.state
        deaths = int(s.population * random.uniform(0.15, 0.3))
        s.population -= deaths
        s.morale -= 30
        self._add_event(f"🦠 PLAGUE OUTBREAK: {deaths} dead in days", "red")

    def _crisis_structural_failure(self):
        s = self.state
        levels_lost = random.randint(1, 3)
        targets = random.sample(s.sectors, min(levels_lost, len(s.sectors)))

        total_casualties = 0
        for sector in targets:
            total_casualties += sector.workers
            sector.health = 0
            sector.workers = 0

        s.population -= total_casualties
        self._add_event(f"💥 STRUCTURAL FAILURE: {levels_lost} levels collapse, {total_casualties} lost", "red")

    def _crisis_riot(self):
        s = self.state
        target = random.choice(s.sectors)
        target.health -= 30
        s.morale -= 25
        deaths = random.randint(5, 15)
        s.population -= deaths
        self._add_event(f"✊ RIOTS on Level {target.level}: {deaths} casualties", "red")

    def _trigger_minor_event(self):
        s = self.state
        events = [
            ("🎁 Supply cache discovered", lambda: setattr(s, 'materials', s.materials + random.randint(30, 60)), "green"),
            ("👥 Refugee group arrives", lambda: setattr(s, 'population', s.population + random.randint(5, 12)), "cyan"),
            ("⚡ Power surge", lambda: setattr(s, 'power', s.power + random.randint(40, 80)), "yellow"),
            ("🌾 Abundant harvest", lambda: setattr(s, 'food', s.food + random.randint(50, 100)), "green"),
        ]

        event_text, effect, color = random.choice(events)
        effect()
        self._add_event(event_text, color)

    def _create_dilemma(self):
        s = self.state
        damaged = [sec for sec in s.sectors if 20 < sec.health < 60]
        if not damaged:
            return

        target = random.choice(damaged)

        def save_sector():
            target.health += 40
            s.materials -= 50
            self._add_event(f"✅ Level {target.level} reinforced", "green")

        def abandon_sector():
            refugees = target.workers
            s.population -= int(refugees * 0.3)
            target.workers = 0
            target.health = 0
            s.morale -= 15
            self._add_event(f"🚪 Level {target.level} evacuated, some lost", "yellow")

        s.current_dilemma = Dilemma(
            title=f"Level {target.level} Critical",
            description=f"{target.sector_type.value[2]} sector failing! {target.workers} workers trapped.",
            option_a=f"Reinforce (-50 materials)",
            option_b=f"Evacuate (lose workers)",
            consequence_a=save_sector,
            consequence_b=abandon_sector
        )

    def _process_action(self, action: str):
        s = self.state

        if action == "repair":
            sector = s.get_sector(s.cursor)
            if sector and s.materials >= 40:
                s.materials -= 40
                sector.health += 50
                sector.health = min(100, sector.health)
                self._add_event(f"🔧 Level {s.cursor} repaired", "green")
            else:
                self._add_event("❌ Need 40 materials", "red")

        elif action == "extinguish":
            sector = s.get_sector(s.cursor)
            if sector and sector.on_fire and s.power >= 30:
                s.power -= 30
                sector.on_fire = False
                self._add_event(f"🚒 Fire on Level {s.cursor} extinguished", "green")
            else:
                self._add_event("❌ Need 30 power or no fire", "red")

        elif action.startswith("build"):
            next_level = len(s.sectors) + 1
            if next_level > s.max_height:
                self._add_event("❌ At maximum height", "red")
                return
            if s.materials < 80:
                self._add_event("❌ Need 80 materials to build", "red")
                return

            # Determine building type
            sector_type = SectorType.RESIDENTIAL  # default
            type_name = "Housing"

            if action == "build_farm":
                sector_type = SectorType.FARMS
                type_name = "Farm"
            elif action == "build_power":
                sector_type = SectorType.POWER
                type_name = "Power"
            elif action == "build_industry":
                sector_type = SectorType.INDUSTRIAL
                type_name = "Industry"
            elif action == "build_housing":
                sector_type = SectorType.RESIDENTIAL
                type_name = "Housing"

            s.materials -= 80
            new_sector = Sector(level=next_level, sector_type=sector_type, workers=random.randint(5, 10))
            s.sectors.append(new_sector)
            s.sectors.sort(key=lambda x: x.level)
            self._add_event(f"🏗️  {type_name} built on Level {next_level}", "cyan")

        elif action == "boost_morale":
            if s.food >= 40 and s.power >= 20:
                s.food -= 40
                s.power -= 20
                s.morale += 30
                self._add_event("🎉 Festival held - morale boosted!", "green")
            else:
                self._add_event("❌ Need 40 food + 20 power", "red")

        elif action == "emergency_rations":
            if s.population > 30:
                s.population -= 10
                s.food += 60
                s.morale -= 20
                self._add_event("⚔️  Culled 10 citizens for emergency rations", "red")

    def _add_event(self, message: str, color: str = "white"):
        self.state.events.append((f"Y{self.state.year}M{self.state.month}: {message}", color))
        if len(self.state.events) > 50:
            self.state.events.pop(0)


class StatsPanel(Static):
    """Display game stats"""

    def __init__(self, sim: Simulation, **kwargs):
        super().__init__(**kwargs)
        self.sim = sim

    def render(self) -> Text:
        s = self.sim.state

        # Color coding
        food_color = "green" if s.food > 80 else "yellow" if s.food > 30 else "red"
        power_color = "green" if s.power > 60 else "yellow" if s.power > 20 else "red"
        morale_color = "green" if s.morale > 60 else "yellow" if s.morale > 30 else "red"
        tension_color = "green" if s.tension < 40 else "yellow" if s.tension < 70 else "red"

        text = Text()
        text.append(f"Year {s.year}, Month {s.month}\n", style="bold cyan")
        text.append("\n")
        text.append(f"Population: ", style="white")
        text.append(f"{s.population}\n", style=morale_color)
        text.append(f"Food: ", style="white")
        text.append(f"{s.food:.0f}\n", style=food_color)
        text.append(f"Power: ", style="white")
        text.append(f"{s.power:.0f}\n", style=power_color)
        text.append(f"Materials: ", style="white")
        text.append(f"{s.materials:.0f}\n", style="white")
        text.append(f"Morale: ", style="white")
        text.append(f"{s.morale:.0f}%\n", style=morale_color)
        text.append(f"Tension: ", style="white")
        text.append(f"{s.tension:.0f}%", style=tension_color)

        return text


class TowerPanel(Static):
    """Display the tower"""

    def __init__(self, sim: Simulation, **kwargs):
        super().__init__(**kwargs)
        self.sim = sim

    def render(self) -> Text:
        s = self.sim.state
        text = Text()

        text.append("THE TOWER\n\n", style="bold white")

        for i in range(s.max_height, 0, -1):
            sector = s.get_sector(i)

            if sector:
                symbol, color = sector.get_display()
                health_bar = "█" * int(sector.health / 10)
                cursor_marker = "→" if i == s.cursor else " "

                # Show worker status or condition
                if sector.workers > 0:
                    workers_display = f"{sector.workers} workers"
                elif sector.health > 0:
                    workers_display = "abandoned"  # Has structure, no workers
                else:
                    workers_display = "DESTROYED"  # Completely gone

                fire_indicator = "🔥" if sector.on_fire else "  "

                # Show sector type name (full name, not truncated)
                sector_name = sector.sector_type.value[2]

                text.append(f"{cursor_marker} ", style="cyan")
                text.append(f"L{i:2d} ", style="white")
                text.append(f"{symbol}  ", style=color)  # Two spaces after emoji
                text.append(f"{sector_name:8s} ", style="dim white")
                text.append(f"{health_bar:10s} ", style="dim")
                text.append(f"{workers_display:11s} ", style="white")
                text.append(f"{fire_indicator}\n")
            else:
                cursor_marker = "→" if i == s.cursor else " "
                text.append(f"{cursor_marker} L{i:2d} ", style="dim white")
                text.append("... empty ...\n", style="dim")

        text.append("\n")
        text.append("   ╚═════╝ Base\n", style="bold cyan")

        return text


class LegendPanel(Static):
    """Display legend and game info"""

    def render(self) -> Text:
        text = Text()
        text.append("HOW IT WORKS\n\n", style="bold white")

        text.append("Sectors Produce:\n", style="bold yellow")
        text.append("🏠 Housing: ", style="cyan")
        text.append("Capacity\n", style="dim white")
        text.append("🌾 Farms: ", style="green")
        text.append("Food (2.5/worker)\n", style="dim white")
        text.append("⚡ Power: ", style="yellow")
        text.append("Energy (3/worker)\n", style="dim white")
        text.append("⚙️  Industry: ", style="magenta")
        text.append("Materials (2/worker)\n", style="dim white")
        text.append("  → For repairs & building\n\n", style="dim white")

        text.append("Workers = Citizens in sectors\n", style="dim white")
        text.append("  → Produce resources\n", style="dim white")
        text.append("Population = Total citizens\n", style="dim white")
        text.append("  → Consume food & power\n\n", style="dim white")

        text.append("Status Icons:\n", style="bold yellow")
        text.append("⚠️  Damaged (< 60% HP)\n", style="yellow")
        text.append("💀 Critical (< 30% HP)\n", style="red")
        text.append("  → Will collapse soon!\n", style="dim red")
        text.append("🔥 Fire (spreading!)\n\n", style="red")

        text.append("Worker Status:\n", style="bold yellow")
        text.append("X workers = Active\n", style="dim white")
        text.append("abandoned = No workers\n", style="dim white")
        text.append("DESTROYED = Collapsed\n", style="dim red")

        return text


class EventLog(Static):
    """Display event log"""

    def __init__(self, sim: Simulation, **kwargs):
        super().__init__(**kwargs)
        self.sim = sim

    def render(self) -> Text:
        s = self.sim.state
        text = Text()

        text.append("RECENT EVENTS\n\n", style="bold white")

        for event_text, color in s.events[-10:]:
            text.append(f"{event_text}\n", style=color)

        return text


class ControlsPanel(Static):
    """Display controls"""

    def __init__(self, sim: Simulation, **kwargs):
        super().__init__(**kwargs)
        self.sim = sim

    def render(self) -> Text:
        s = self.sim.state
        text = Text()
        text.append("CONTROLS\n\n", style="bold white")

        # Show selected level
        text.append("→ = ", style="cyan")
        text.append(f"Selected Level {s.cursor}\n\n", style="bold yellow")

        text.append("Target selected level:\n", style="dim yellow")
        text.append("↑↓/WS  ", style="cyan")
        text.append("Navigate levels\n", style="white")
        text.append("1      ", style="cyan")
        text.append("Repair selected\n", style="white")
        text.append("2      ", style="cyan")
        text.append("Extinguish selected\n\n", style="white")

        text.append("Global actions:\n", style="dim yellow")
        text.append("3      ", style="cyan")
        text.append("Build new level\n", style="white")
        text.append("4      ", style="cyan")
        text.append("Festival (morale)\n", style="white")
        text.append("5      ", style="cyan")
        text.append("Emergency rations\n", style="white")
        text.append("SPACE  ", style="cyan")
        text.append("Wait/pass time\n", style="white")
        text.append("Q      ", style="cyan")
        text.append("Quit\n", style="white")

        return text


class DilemmaPanel(Static):
    """Display dilemma or building choice"""

    def __init__(self, sim: Simulation, **kwargs):
        super().__init__(**kwargs)
        self.sim = sim

    def render(self) -> Text:
        s = self.sim.state

        # Show game over screen
        if hasattr(self.sim, 'app') and self.sim.app.game_over:
            text = Text()
            text.append("💀 GAME OVER 💀\n\n", style="bold red")
            text.append(f"{self.sim.app.game_over_message}\n\n", style="yellow")
            text.append("Press R to restart\n", style="green")
            text.append("Press Q to quit\n", style="dim white")
            return text

        # Show building choice menu
        if s.building_mode:
            text = Text()
            text.append("🏗️  BUILD NEW LEVEL\n\n", style="bold cyan")
            text.append("Choose sector type:\n\n", style="white")
            text.append("F - ", style="bold green")
            text.append("🌾 Farm ", style="green")
            text.append("(food production)\n", style="dim white")
            text.append("P - ", style="bold yellow")
            text.append("⚡ Power ", style="yellow")
            text.append("(energy generation)\n", style="dim white")
            text.append("I - ", style="bold magenta")
            text.append("⚙️  Industry ", style="magenta")
            text.append("(materials)\n", style="dim white")
            text.append("H - ", style="bold cyan")
            text.append("🏠 Housing ", style="cyan")
            text.append("(population cap)\n\n", style="dim white")
            text.append("ESC - Cancel\n", style="dim white")
            return text

        # Show dilemma if one exists
        if s.current_dilemma:
            d = s.current_dilemma
            text = Text()
            text.append("⚠️  URGENT DECISION ⚠️\n\n", style="bold red")
            text.append(f"{d.title}\n\n", style="bold yellow")
            text.append(f"{d.description}\n\n", style="white")
            text.append("A: ", style="bold cyan")
            text.append(f"{d.option_a}\n", style="cyan")
            text.append("B: ", style="bold yellow")
            text.append(f"{d.option_b}\n", style="yellow")
            return text

        # Show what this panel is for when empty
        text = Text()
        text.append("DECISIONS\n\n", style="bold red")
        text.append("Urgent choices appear here\n", style="dim white")
        text.append("when crises occur.\n\n", style="dim white")
        text.append("Press A or B to decide.\n", style="dim white")

        return text


class SpireApp(App):
    """The Spire TUI application"""

    CSS = """
    Screen {
        layout: grid;
        grid-size: 3 3;
        grid-gutter: 1;
    }

    #stats {
        column-span: 1;
        row-span: 1;
        border: solid cyan;
    }

    #tower {
        column-span: 1;
        row-span: 3;
        border: solid white;
    }

    #legend {
        column-span: 1;
        row-span: 1;
        border: solid yellow;
    }

    #events {
        column-span: 1;
        row-span: 1;
        border: solid green;
    }

    #controls {
        column-span: 1;
        row-span: 1;
        border: solid magenta;
    }

    #dilemma {
        column-span: 1;
        row-span: 1;
        border: solid red;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("w", "move_up", "Up"),
        ("s", "move_down", "Down"),
        ("up", "move_up", "Up"),
        ("down", "move_down", "Down"),
        ("1", "do_repair", "Repair"),
        ("2", "do_extinguish", "Extinguish"),
        ("3", "do_build", "Build"),
        ("4", "do_morale", "Festival"),
        ("5", "do_rations", "Rations"),
        ("space", "do_wait", "Wait"),
        ("a", "choice_a", "Choice A"),
        ("b", "choice_b", "Choice B"),
        ("f", "build_farm", "Build Farm"),
        ("p", "build_power", "Build Power"),
        ("i", "build_industry", "Build Industry"),
        ("h", "build_housing", "Build Housing"),
        ("escape", "cancel_build", "Cancel"),
        ("r", "restart", "Restart"),
    ]

    def __init__(self):
        super().__init__()
        self.sim = Simulation()
        self.sim.app = self  # Link back so panels can access game state
        self.game_over = False
        self.game_over_message = ""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield StatsPanel(self.sim, id="stats")
        yield TowerPanel(self.sim, id="tower")
        yield LegendPanel(id="legend")
        yield EventLog(self.sim, id="events")
        yield ControlsPanel(self.sim, id="controls")
        yield DilemmaPanel(self.sim, id="dilemma")
        yield Footer()

    def action_move_up(self) -> None:
        if self.game_over:
            return
        self.sim.state.cursor = min(self.sim.state.cursor + 1, self.sim.state.max_height)
        self.refresh_all()

    def action_move_down(self) -> None:
        if self.game_over:
            return
        self.sim.state.cursor = max(self.sim.state.cursor - 1, 1)
        self.refresh_all()

    def action_restart(self) -> None:
        """Restart the game"""
        self.sim = Simulation()
        self.sim.app = self
        self.game_over = False
        self.game_over_message = ""
        self.refresh_all()

    def action_do_repair(self) -> None:
        if self.game_over or self.sim.state.current_dilemma:
            return
        self.sim.advance_turn("repair")
        self.check_game_over()
        self.refresh_all()

    def action_do_extinguish(self) -> None:
        if self.game_over or self.sim.state.current_dilemma:
            return
        self.sim.advance_turn("extinguish")
        self.check_game_over()
        self.refresh_all()

    def action_do_build(self) -> None:
        """Enter building mode to choose sector type"""
        if self.game_over or self.sim.state.current_dilemma:
            return
        # Check if we can build
        if len(self.sim.state.sectors) >= self.sim.state.max_height:
            self.sim._add_event("❌ At maximum height", "red")
            self.refresh_all()
            return
        if self.sim.state.materials < 80:
            self.sim._add_event("❌ Need 80 materials to build", "red")
            self.refresh_all()
            return

        # Enter building mode
        self.sim.state.building_mode = True
        self.refresh_all()

    def action_build_farm(self) -> None:
        """Build a farm sector"""
        if not self.sim.state.building_mode:
            return
        self.sim.state.building_mode = False
        self.sim.advance_turn("build_farm")
        self.check_game_over()
        self.refresh_all()

    def action_build_power(self) -> None:
        """Build a power plant"""
        if not self.sim.state.building_mode:
            return
        self.sim.state.building_mode = False
        self.sim.advance_turn("build_power")
        self.check_game_over()
        self.refresh_all()

    def action_build_industry(self) -> None:
        """Build an industry sector"""
        if not self.sim.state.building_mode:
            return
        self.sim.state.building_mode = False
        self.sim.advance_turn("build_industry")
        self.check_game_over()
        self.refresh_all()

    def action_build_housing(self) -> None:
        """Build a housing sector"""
        if not self.sim.state.building_mode:
            return
        self.sim.state.building_mode = False
        self.sim.advance_turn("build_housing")
        self.check_game_over()
        self.refresh_all()

    def action_cancel_build(self) -> None:
        """Cancel building mode"""
        if self.sim.state.building_mode:
            self.sim.state.building_mode = False
            self.refresh_all()

    def action_do_morale(self) -> None:
        if self.game_over or self.sim.state.current_dilemma:
            return
        self.sim.advance_turn("boost_morale")
        self.check_game_over()
        self.refresh_all()

    def action_do_rations(self) -> None:
        if self.game_over or self.sim.state.current_dilemma:
            return
        self.sim.advance_turn("emergency_rations")
        self.check_game_over()
        self.refresh_all()

    def action_do_wait(self) -> None:
        if self.game_over or self.sim.state.current_dilemma:
            return
        self.sim.advance_turn("wait")
        self.check_game_over()
        self.refresh_all()

    def action_choice_a(self) -> None:
        if self.game_over or not self.sim.state.current_dilemma:
            return
        if self.sim.state.current_dilemma:
            self.sim.state.current_dilemma.consequence_a()
            self.sim.state.current_dilemma = None
            self.sim.advance_turn("wait")
            self.check_game_over()
            self.refresh_all()

    def action_choice_b(self) -> None:
        if self.game_over or not self.sim.state.current_dilemma:
            return
        if self.sim.state.current_dilemma:
            self.sim.state.current_dilemma.consequence_b()
            self.sim.state.current_dilemma = None
            self.sim.advance_turn("wait")
            self.check_game_over()
            self.refresh_all()

    def refresh_all(self) -> None:
        """Refresh all panels"""
        self.query_one("#stats").refresh()
        self.query_one("#tower").refresh()
        self.query_one("#events").refresh()
        self.query_one("#dilemma").refresh()
        self.query_one("#controls").refresh()

    def check_game_over(self) -> None:
        """Check if game is over"""
        if not self.sim.state.alive and not self.game_over:
            self.game_over = True
            self.game_over_message = self.sim.state.victory_message
            # Show game over in the dilemma panel
            self.refresh_all()


def main():
    app = SpireApp()
    result = app.run()
    if result:
        print(f"\n{result}\n")


if __name__ == "__main__":
    main()
