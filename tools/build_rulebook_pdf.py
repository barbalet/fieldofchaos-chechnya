#!/usr/bin/env python3
"""Build Book 1 as a compact table-first Gold rulebook."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageOps
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "foc-chechnya-gold.pdf"
PNG = ROOT / "png"
PDF_ASSETS = ROOT / "tmp" / "pdf-assets-rulebook"

PAGE_W, PAGE_H = letter
TARGET_PAGES = 48
MIN_FONT = 10.0
MARGIN_X = 42
TOP_Y = PAGE_H - 42
BOTTOM_Y = 46
FOOTER_Y = 25
GUTTER = 18
COL_W = (PAGE_W - 2 * MARGIN_X - GUTTER) / 2

BODY = "Helvetica"
BOLD = "Helvetica-Bold"
ITALIC = "Helvetica-Oblique"
TITLE = "Helvetica-Bold"

PAPER = colors.HexColor("#F7F2E6")
INK = colors.HexColor("#25211E")
MUTED = colors.HexColor("#5E5A4F")
GREEN = colors.HexColor("#607252")
GREEN_DARK = colors.HexColor("#48563E")
GRID = colors.HexColor("#6D6A60")
ROW_ALT = colors.HexColor("#E2E0D6")
ROW_LIGHT = colors.HexColor("#F8F6EE")
PALE = colors.HexColor("#ECE7D9")
RED = colors.HexColor("#7A3D34")


@dataclass(frozen=True)
class Block:
    kind: str
    data: dict[str, Any]


@dataclass(frozen=True)
class Page:
    section: str
    title: str
    strap: str
    left: list[Block]
    right: list[Block]


def table(
    title: str,
    headers: list[str],
    rows: list[list[str]],
    widths: list[float] | None = None,
    size: float = MIN_FONT,
) -> Block:
    return Block("table", {"title": title, "headers": headers, "rows": rows, "widths": widths, "size": size})


def bullets(title: str, items: list[str], size: float = MIN_FONT) -> Block:
    return Block("bullets", {"title": title, "items": items, "size": size})


def note(title: str, text: str, size: float = MIN_FONT) -> Block:
    return Block("note", {"title": title, "text": text, "size": size})


def prose(text: str, size: float = MIN_FONT) -> Block:
    return Block("prose", {"text": text, "size": size})


def image_block(filename: str, caption: str, height: float = 102) -> Block:
    return Block("image", {"filename": filename, "caption": caption, "height": height})


GOLD_STATS = [
    ["RE", "Regular Intelligence", "Book learning, formal knowledge, ordinary problem solving."],
    ["IR", "Irregular Intelligence", "Streetwise, improvised, criminal, or unorthodox problem solving."],
    ["AP", "Appearance", "Presentation, first impression, authority, and social face."],
    ["PH", "Physical Health", "Body, stamina, durability, climbing, carrying, and movement strain."],
    ["ME", "Mental Health", "Steadiness, self-control, fear, shock, and stress resistance."],
]

SKILLS_RE = [
    ["Cartography", "Read maps, apartment plans, ravine sketches, and marked routes."],
    ["Soviet Weapons ID", "Recognize common Soviet-pattern weapons, magazines, mines, and crates."],
    ["Radio Procedure", "Use call signs, brevity, intercept discipline, and message priority."],
    ["Triage Estimate", "Choose who needs evacuation first; does not replace First Aid."],
    ["Engineering Survey", "Assess walls, stairwells, culverts, barricades, and firing slits."],
    ["Document Search", "Find rosters, ledgers, safe papers, IDs, and route notes under time pressure."],
    ["Command Estimate", "Read enemy intent from timing, route choice, and deployment."],
    ["Language Bridge", "Translate Russian/Chechen/Arabic fragments when the scenario allows."],
    ["Logistics Count", "Track ammunition, fuel, food, medical packets, and usable vehicles."],
    ["Formal Negotiation", "Use official language, ceasefire procedure, and intermediary etiquette."],
]

SKILLS_IR = [
    ["Cache Reading", "Find likely weapons, food, and fuel hides from terrain and habit."],
    ["Black-Market Appraisal", "Judge the value, risk, and origin of arms or money."],
    ["Bribe Protocol", "Know who can be paid, who cannot, and what payment will expose."],
    ["Back-Alley Route", "Move through courtyards, cellars, service alleys, and broken interiors."],
    ["Informant Handling", "Assess a nervous guide, courier, broker, or captured messenger."],
    ["Ambush Sense", "Spot signs of roadblock, flank, kill zone, or staged panic."],
    ["Forged Papers", "Use false passes, names, license plates, and cover stories."],
    ["Vehicle Scrounge", "Find fuel, batteries, tires, keys, and usable civilian transport."],
    ["Prisoner Whisper", "Get useful information without turning the game into interrogation spectacle."],
    ["Contraband Concealment", "Hide weapons, documents, money, and radios during a search."],
]

SKILLS_AP = [
    ["Clan Introduction", "Open a conversation through kinship, village ties, or elder authority."],
    ["Refugee Reassurance", "Move frightened civilians without panic or coercion."],
    ["Checkpoint Demeanor", "Look calm, local, useful, harmless, or official at the right moment."],
    ["Religious Courtesy", "Behave correctly around mosque, burial, fasting, and clergy scenes."],
    ["Underworld Reputation", "Be known enough to pass a broker, guard, or criminal checkpoint."],
    ["Command Presence", "Keep a small group moving when authority is uncertain."],
]

SKILLS_PH = [
    ["Rubble Climb", "Cross debris, broken walls, shell holes, and collapsed interiors."],
    ["Mountain Traverse", "Move across ravines, scree, snow line, and wooded slopes."],
    ["Load Carry", "Carry ammunition, water, food, money, radios, or a wounded figure."],
    ["Silent Crawl", "Move low and slowly through rubble, brush, or dark interiors."],
    ["Breach Entry", "Force a door, window, wall gap, or stairwell without freezing."],
    ["Casualty Drag", "Move a wounded model without full carry speed."],
    ["Cold Camp", "Endure winter, wet clothes, hunger, and sleeping rough."],
    ["Sprint Across Fire", "Cross a lane, courtyard, or road when hesitation is worse."],
]

SKILLS_ME = [
    ["Hold Under Shelling", "Keep acting when off-table pressure lands nearby."],
    ["Resist Coercion", "Stay composed under threat, shouted orders, or intimidation."],
    ["Night Discipline", "Avoid noise, flash, silhouette, and panic in darkness."],
    ["Wounded Calm", "Continue a task while injured or while carrying a casualty."],
    ["Atrocity Shock", "Avoid paralysis after discovering civilian harm."],
    ["Ceasefire Patience", "Wait through negotiation, delay, and unclear orders."],
]

ALL_SKILLS = SKILLS_RE + SKILLS_IR + SKILLS_AP + SKILLS_PH + SKILLS_ME

SCENARIOS = [
    ["1", "Dolinskoye Road", "Roadblock approach, early-war confusion, off-table federal armor pressure.", "Cross, delay, or recover a courier before the pressure clock expires."],
    ["2", "Grozny Rail Station", "Interior routes, smoke, stairwells, trapped movement.", "Exit documents or wounded figures through two connected buildings."],
    ["3", "Palace Withdrawal", "Rubble lanes, short sight lines, political-symbol terrain.", "Withdraw before encirclement while denying a cache marker."],
    ["4", "Shali Aftermath", "Market, hospital edge, civilian movement, no spectacle.", "Open a civilian route while avoiding body-count victory."],
    ["5", "Village Cordon", "Walls, gardens, mosque or cemetery edge, search pressure.", "Move a hidden person or packet through the cordon."],
    ["6", "Bamut Bunker Probe", "Wooded slopes, bunker mouths, hidden exits.", "Scout, mark, and leave; not a bunker-clearing fantasy."],
    ["7", "Gudermes Cache Raid", "Winter streets, checkpoints, informants, fast exit.", "Recover one cache and exit before alarm escalation."],
    ["8", "Pervomayskoye Breakout", "Frozen fields, village edges, pressure clock.", "Move a group across exposed ground under pursuit."],
    ["9", "Shatoy Road Bend", "Ravine road, culverts, high ground, convoy aftermath.", "Observe, mark, or extract; heavy weapons stay off-table."],
    ["10", "August Grozny Infiltration", "Night routes, basements, roadblocks, local guides.", "Open an approach lane without turning it into regular-army command."],
]


def build_pages() -> list[Page]:
    pages: list[Page] = [
        Page(
            "Getting Started",
            "What This Rulebook Is",
            "A table book for two local-force players, not a history essay.",
            [
                bullets("Scope", [
                    "Default game: two human players, 10-20 miniatures per side, 28mm figures.",
                    "Playable forces are local Chechen factions, pro-Moscow Chechen opposition, police, militia, guards, or small foreign-volunteer attachments.",
                    "Russian regulars, artillery, armor, aircraft, RPGs, and heavy weapons remain off-table unless a scenario says otherwise.",
                    "The rulebook is the primary game source. Book 2 is history, context, and source support.",
                ]),
                table("Table Kit", ["Item", "Use"], [
                    ["d6 and 2d6", "Gold checks, jams, grenade reliability, hit locations."],
                    ["Tape measure", "Ranges and movement in inches."],
                    ["Tokens", "Wounds, jam, reload, cache, courier, pressure clock."],
                    ["Templates", "Shotgun cone and grenade bands."],
                ], [0.33, 0.67]),
            ],
            [
                table("Fast Turn Outline", ["Step", "Do This"], [
                    ["1", "Check scenario pressure and any timed events."],
                    ["2", "Activate one figure or group as the scenario permits."],
                    ["3", "Move, shoot, melee, throw, heal, search, or interact."],
                    ["4", "Resolve wounds, jams, duds, caches, and morale triggers."],
                    ["5", "End turn when all eligible figures have acted."],
                ], [0.16, 0.84]),
                image_block("complete-28mm-skirmish-roster.png", "The game is sized for 28mm skirmish groups, not platoon combat.", 118),
            ],
        ),
        Page(
            "Getting Started",
            "Refusal Lines",
            "The game is tense and historical without asking players to optimize atrocity.",
            [
                table("Do Not Put On Table", ["Excluded", "Reason"], [
                    ["No player artillery", "Handled only as pressure, crater, or event."],
                    ["No heavy vehicles", "Scenery or pressure only."],
                    ["No RPGs", "Outside the requested play envelope."],
                    ["No regular Russian player roster", "Federal side is covered historically, but not controlled by a player."],
                    ["No hostage spectacle", "Historical context can exist without exploitation."],
                ], [0.38, 0.62]),
                note("Victory Language", "Use courier, cache, escape, delay, identify, withdraw, recover, screen, rescue, or open-route objectives. Avoid victory by civilian harm or body count."),
            ],
            [
                table("Ethical Scenario Test", ["Question", "Keep If"], [
                    ["Can both players make decisions?", "Yes, each side has agency."],
                    ["Does terrain create choices?", "Yes, not just a shooting gallery."],
                    ["Are civilians scenery?", "No, they are protected objectives or pressure markers."],
                    ["Is Russia ignored?", "No, federal pressure exists, but player control is local."],
                ], [0.45, 0.55]),
                bullets("Book 2 Use", [
                    "Use the reference book for leaders, battles, sources, Islam, organized crime, and Russian command.",
                    "Do not import Book 2 history as extra game exceptions unless a scenario says so.",
                    "When a dispute appears, the Gold tables in this rulebook control play.",
                ]),
            ],
        ),
        Page(
            "Getting Started",
            "Components And Scale",
            "US Letter reference pages, dense enough for play, open enough to read.",
            [
                table("Scale", ["Element", "Default"], [
                    ["Figure", "One 28mm miniature is one person."],
                    ["Side", "10-20 figures."],
                    ["Table", "3 x 3 ft. for small games; 4 x 4 ft. for 16-20 per side."],
                    ["Buildings", "Interior routes matter more than footprints."],
                    ["Turn", "Short action interval; keep pressure clocks scenario-specific."],
                ], [0.35, 0.65]),
                image_block("grozny-apartment-block-skirmish.png", "Urban boards need vertical routes, blocked streets, and broken sight lines.", 112),
            ],
            [
                table("Markers", ["Marker", "Meaning"], [
                    ["Cache", "Weapons, money, food, documents, or medical supplies."],
                    ["Courier", "Person or packet that must move."],
                    ["Pressure", "Off-table federal arrival, cordon, sweep, shelling, or alarm."],
                    ["Civilian route", "Path that should be opened, protected, or avoided."],
                    ["Wounded", "Figure has location damage; track normally."],
                ], [0.35, 0.65]),
                note("Measurement", "All distances are inches. Keep Gold weapon ranges intact. Do not convert to Bolt Action ranges; only the visual reference format is borrowed."),
            ],
        ),
        Page(
            "Skills",
            "Gold Stats And Character Build",
            "Skills hang from the five Gold statistics.",
            [
                table("Gold Statistics", ["Short", "Statistic", "Game Meaning"], GOLD_STATS, [0.14, 0.34, 0.52], 6.9),
                table("Generation", ["Step", "Instruction"], [
                    ["1", "Roll three d6."],
                    ["2", "Choose two dice and invert them: 1 becomes 6, 2 becomes 5, and so on."],
                    ["3", "You now have five values: three original and two inverted."],
                    ["4", "Choose one value to receive +2; the others receive +1."],
                    ["5", "Assign the five results to RE, IR, AP, PH, and ME."],
                ], [0.16, 0.84], 6.8),
            ],
            [
                table("Limits", ["Rule", "Gold Value"], [
                    ["Stat range", "0-10."],
                    ["Initial total", "Maximum 30 across all five stats."],
                    ["Detailed play total", "May rise to 40."],
                    ["Skill slots", "One skill per statistic point in that area."],
                    ["Prerequisites", "Count against skill accounting."],
                    ["Skill value", "0-100 percent."],
                ], [0.42, 0.58]),
                note("Chechnya Rule", "The forty setting skills below are in addition to Gold firearm and medical skills. They do not change weapon ranges, healing dice, grenade duds, shotgun cones, or wound locations."),
            ],
        ),
        Page(
            "Skills",
            "Gold Skill Chains",
            "Keep the original weapon and medical chains visible.",
            [
                table("Weapon And Medical Skills", ["Area", "Gold Chain", "Effect"], [
                    ["Firearms", "Firearm Use Basic (PH) -> Advanced (ME)", "Basic adds one range die; Advanced adds two."],
                    ["Shotgun", "Covered by Firearm Use Basic", "No separate Shotgun skill in Gold play."],
                    ["Grenade", "No skill requirement", "No skill changes throw, dud, blast, or damage."],
                    ["Close combat", "Close Combat (PH)", "Used for melee checks."],
                    ["Improvised", "Improvised Weapon Use Basic (IR)", "For improvised weapons."],
                    ["Clandestine", "Clandestine Weapon Use Basic (IR)", "For hidden or covert weapons."],
                    ["Manufacture", "Carpentry (PH) -> Manufacture Clandestine Weapon (IR)", "For making or supporting hidden weapons."],
                    ["Explosives", "Chemistry Basic (RE) -> Explosive Engineering (IR)", "Exists, but no Gold grenade effect."],
                    ["Medical", "First Aid (RE) -> Paramedic (RE)", "Improves healing dice."],
                ], [0.22, 0.42, 0.36], 6.45),
            ],
            [
                table("Skill Dice Pattern", ["Use", "Dice"], [
                    ["No skill", "Base dice only."],
                    ["Basic firearm", "Range dice +1 die."],
                    ["Advanced firearm", "Range dice +2 dice."],
                    ["First Aid", "Roll 2d6, use highest."],
                    ["Paramedic", "Roll 3d6, use highest."],
                    ["New setting skill", "Referee calls a stat check or gives a task bonus; never changes Gold weapon math."],
                ], [0.42, 0.58]),
                bullets("Design Principle", [
                    "Gold mechanics remain intact.",
                    "New skills create scenario permissions and task resolution.",
                    "Chechen player forces get skills and objectives, not enemy-only special foe traits.",
                ]),
            ],
        ),
        Page(
            "Skills",
            "Forty Setting Skills: RE And IR",
            "Twenty knowledge and improvisation skills for Chechnya play.",
            [
                table("Regular Intelligence Skills", ["Skill", "Use"], SKILLS_RE, [0.36, 0.64], 6.3),
            ],
            [
                table("Irregular Intelligence Skills", ["Skill", "Use"], SKILLS_IR, [0.36, 0.64], 6.3),
            ],
        ),
        Page(
            "Skills",
            "Forty Setting Skills: AP, PH, ME",
            "The remaining twenty skills cover social presence, bodies, and nerve.",
            [
                table("Appearance Skills", ["Skill", "Use"], SKILLS_AP, [0.38, 0.62], 6.5),
                table("Physical Health Skills", ["Skill", "Use"], SKILLS_PH, [0.38, 0.62], 6.2),
            ],
            [
                table("Mental Health Skills", ["Skill", "Use"], SKILLS_ME, [0.38, 0.62], 6.5),
                table("Skill Count", ["Stat", "New Skills"], [
                    ["RE", "10"],
                    ["IR", "10"],
                    ["AP", "6"],
                    ["PH", "8"],
                    ["ME", "6"],
                    ["Total", "40"],
                ], [0.45, 0.55]),
            ],
        ),
        Page(
            "Skills",
            "Skill Matrix In Play",
            "Skills make local war problems playable without rewriting Gold combat.",
            [
                table("Skill Matrix", ["Problem", "Skill Paths"], [
                    ["Plan a route", "RE Cartography; IR Back-Alley Route; AP Clan Introduction; PH Mountain Traverse; ME Night Discipline."],
                    ["Find a cache", "RE Engineering Survey; IR Cache Reading; AP Underworld Reputation; PH Rubble Climb; ME Hold Under Shelling."],
                    ["Cross a checkpoint", "RE Formal Negotiation; IR Forged Papers; AP Checkpoint Demeanor; PH Silent Crawl; ME Resist Coercion."],
                    ["Move a casualty", "RE Triage Estimate; IR Informant Handling; AP Refugee Reassurance; PH Casualty Drag; ME Wounded Calm."],
                    ["Open a civilian route", "RE Logistics Count; IR Back-Alley Route; AP Religious Courtesy; PH Load Carry; ME Ceasefire Patience."],
                    ["Break contact", "RE Command Estimate; IR Ambush Sense; AP Command Presence; PH Sprint Across Fire; ME Night Discipline."],
                ], [0.28, 0.72], 10),
                note("Referee Use", "A skill can allow an action, reduce time, prevent a pressure-clock increase, or add a task die. It cannot make a grenade safer or make an Automatic into a Rifle."),
            ],
            [
                table("Matrix Procedure", ["Step", "Question"], [
                    ["1", "Name the problem in plain language."],
                    ["2", "Choose the column that best describes how the figure solves it."],
                    ["3", "Use the skill to allow the attempt, reduce time, or hold the clock."],
                    ["4", "If no skill fits, use the raw statistic or make the player take the longer route."],
                ], [0.18, 0.82], 6.7),
                table("Roster Limits", ["Type", "Limit"], [
                    ["Ordinary fighter", "0-2 setting skills."],
                    ["Experienced local", "2-4 setting skills."],
                    ["Specialist", "One focus: radio, guide, medic, engineer, broker, scout."],
                    ["Leader", "Command Presence or Formal Negotiation recommended."],
                    ["Foreign volunteer", "May have religious, mountain, media, or training role, but not free enemy traits."],
                ], [0.42, 0.58]),
                image_block("common-weapons-tabletop.png", "Gold types stay mechanical.", 110),
            ],
        ),
        Page(
            "Gold Core",
            "Ranged Weapons",
            "This is the Gold weapon table that controls fire.",
            [
                table("Weapon Ranges", ["Weapon", "Close", "Std", "Long"], [
                    ["Sniper Rifle", "24 in.", "36 in.", "48 in."],
                    ["Rifle", "18 in.", "27 in.", "36 in."],
                    ["Carbine", "12 in.", "18 in.", "24 in."],
                    ["Automatic", "8 in.", "12 in.", "16 in."],
                    ["SubMG", "6 in.", "9 in.", "12 in."],
                ], [0.34, 0.22, 0.22, 0.22]),
                table("Range Dice", ["Range", "Dice", "Hit", "Head"], [
                    ["Close", "1d6 / +1 Basic / +2 Advanced", "4-6", "6"],
                    ["Standard", "2d6 / +1 Basic / +2 Advanced", "10-12", "12"],
                    ["Long", "3d6 / +1 Basic / +2 Advanced", "16-18", "18"],
                ], [0.22, 0.44, 0.17, 0.17], 6.5),
            ],
            [
                table("Fire Modifiers", ["Modifier", "Value"], [
                    ["Light cover", "-1 die"],
                    ["Heavy cover", "-2 dice"],
                    ["Target standard movement", "-1 die"],
                    ["Target fast movement", "-2 dice"],
                    ["Target has Evade", "-1 die"],
                    ["Grenade debris", "Treat as Light cover through blast area."],
                ], [0.58, 0.42]),
                table("Weapon Fire", ["Weapon", "#", "Move", "Special"], [
                    ["Sniper Rifle", "1", "Very Slow", "No fire under 12 in.; called head shot allowed."],
                    ["Rifle", "1 or 2", "Slow", "Two shots with Advanced Firearm Use."],
                    ["Carbine", "1 or 2", "Standard", "Two shots with Advanced Firearm Use."],
                    ["Automatic", "2", "Standard", "Jam on 1 on 2d6; no head shot."],
                    ["SubMG", "3", "Fast", "Jam on 1 on 1d6; no head shot."],
                ], [0.25, 0.15, 0.2, 0.4], 6.1),
            ],
        ),
        Page(
            "Gold Core",
            "Fire Procedure And Jams",
            "Use the exact Gold procedure; do not invent Chechnya fire categories.",
            [
                table("Shooting Sequence", ["Step", "Action"], [
                    ["1", "Choose shooter and target."],
                    ["2", "Check weapon range band."],
                    ["3", "Build dice pool from range and skill."],
                    ["4", "Apply cover and movement modifiers."],
                    ["5", "Roll to hit; then roll hit location and wounds."],
                    ["6", "Apply jams, reloads, and scenario pressure."],
                ], [0.14, 0.86]),
                table("Maintenance", ["Event", "Gold Rule"], [
                    ["Standard clip", "10 rounds."],
                    ["Change clip", "1 turn."],
                    ["Clear jam", "1 turn."],
                    ["Called head shot", "Call two moves prior, miss two moves, then fire."],
                    ["Missed called head shot", "Misses altogether."],
                ], [0.42, 0.58]),
            ],
            [
                table("Weapon Mapping Discipline", ["Do", "Do Not"], [
                    ["Use AK-74 as Automatic.", "Create AK-only fire rules."],
                    ["Use Mosin/SKS as Rifle.", "Change Gold range bands."],
                    ["Use AKS-74U as Carbine/SubMG by scenario.", "Let compact weapons become assault rifles."],
                    ["Use RPK/PKM only as edge cases.", "Normalize machine guns."],
                ], [0.5, 0.5], 6.8),
                note("Why This Matters", "The war's weapon variety is historical color. The game stays fast because every common weapon maps back to a short Gold type name."),
            ],
        ),
        Page(
            "Gold Core",
            "Shotgun And Grenade",
            "Gold imports these procedures; keep the bands intact.",
            [
                table("Shotgun Cone", ["Band", "Cone Length", "Cone Width", "Damage"], [
                    ["Near", "0-5 in.", "1 in.", "2d6 wounds"],
                    ["Middle", ">5-10 in.", "2 in.", "d6 wounds"],
                    ["Far", ">10-15 in.", "3 in.", "d3 wounds"],
                ], [0.21, 0.27, 0.24, 0.28]),
                bullets("Shotgun Rules", [
                    "Total cone length is 15 in.",
                    "Apply damage only to models in the nearest occupied cone band.",
                    "All models in the affected band can be hit, including allies.",
                    "Covered by Firearm Use Basic; no separate Shotgun skill.",
                ], 7.8),
                image_block("shotgun-cone-template-28mm.png", "Use the cone as a table aid, not as a new weapon category.", 92),
            ],
            [
                table("Grenade Rules", ["Rule", "Gold Value"], [
                    ["Maximum range", "12 in."],
                    ["Inner radius", "1 in.; d6 wounds."],
                    ["Middle radius", "3 in.; d3 wounds."],
                    ["Outer radius", "4 in.; d2 wounds."],
                    ["Building at least two walls", "Doubled bands: 3 in., 6 in., 9 in."],
                    ["Reliability", "Roll 2d6; dud on 4 or less."],
                    ["Debris", "Light cover through blast area."],
                    ["Skill", "No skill modifies throw, dud, radius, or damage."],
                ], [0.39, 0.61], 6.5),
                image_block("grenade-blast-template-28mm.png", "Grenade templates should make risk obvious before the throw.", 92),
            ],
        ),
        Page(
            "Gold Core",
            "Movement, Wounds, Melee",
            "Movement and wound tables are table-facing rules.",
            [
                table("Movement Rates", ["Pace", "Distance", "Skill Effect", "1 Grenade"], [
                    ["Very Slow", "2 in.", "+1 in. with Evade", "1 in."],
                    ["Slow", "3 in.", "+1 in. with Marching", "1 in."],
                    ["Standard", "5 in.", "+1 in. with Marching", "2 in."],
                    ["Fast", "8 in.", "+2 in. with Running", "4 in."],
                ], [0.25, 0.2, 0.35, 0.2], 6.7),
                table("Hit Locations", ["3d6", "Location"], [
                    ["3-8", "Leg; odd left, even right."],
                    ["9-13", "Chest."],
                    ["14-15", "Abdomen."],
                    ["16-17", "Arm; odd left, even right."],
                    ["18", "Head."],
                ], [0.28, 0.72]),
            ],
            [
                table("Wounds By Location", ["Location", "Wounds"], [
                    ["Head", "1W"],
                    ["Chest", "4W"],
                    ["Abdomen", "2W"],
                    ["Left Arm", "1W"],
                    ["Right Arm", "1W"],
                    ["Left Leg", "2W"],
                    ["Right Leg", "2W"],
                    ["Total", "13W"],
                ], [0.65, 0.35]),
                table("Melee Checks", ["Check", "Requirement", "Dice"], [
                    ["Blow", "3-6", "1d6 / +1 skill / +2 skill"],
                    ["Weapon", "4-6", "1d6 / +1 skill / +2 skill"],
                ], [0.25, 0.25, 0.5], 6.5),
                note("Injury Effects", "One leg at 0W halves movement. Both legs at 0W means no movement. One arm at 0W means no firearm. Head, chest, or abdomen at 0W means unconscious."),
            ],
        ),
        Page(
            "Gold Core",
            "Healing And Casualty Work",
            "First Aid stays important, but new skills support the situation around it.",
            [
                table("Gold Healing", ["Condition", "Roll"], [
                    ["No medical skill", "1d6 per turn; recover 1 wound on 6."],
                    ["Bandage/equipment", "Recover 1 wound on 5-6."],
                    ["First Aid", "Roll 2d6 and use highest die."],
                    ["Paramedic", "Roll 3d6 and use highest die."],
                    ["Pharmaceutical Chemistry", "No Gold healing effect."],
                ], [0.45, 0.55]),
                table("Casualty Tasks", ["Task", "Useful Skill"], [
                    ["Reach casualty", "Sprint Across Fire, Rubble Climb, Night Discipline."],
                    ["Choose priority", "Triage Estimate."],
                    ["Move casualty", "Casualty Drag or Load Carry."],
                    ["Keep group calm", "Wounded Calm or Command Presence."],
                ], [0.38, 0.62]),
            ],
            [
                bullets("Restrictions", [
                    "No skill turns a dead figure into a wounded figure.",
                    "No social skill prevents normal wound allocation.",
                    "A casualty objective can win the scenario even when the tactical situation is worse.",
                    "Do not require graphic description for treatment.",
                ]),
                image_block("civilian-displacement-road.png", "Casualty and civilian routes should be practical table objectives.", 118),
            ],
        ),
        Page(
            "Weapons",
            "Chechnya Weapons To Gold Names",
            "Common weapons stay common by mapping to short Gold weapon names.",
            [
                table("Common Mapping", ["Historical Weapon", "Gold Type", "Table Use"], [
                    ["AK-74, AKM, AKS, AKMS", "Automatic", "Most fighters and guards."],
                    ["AKS-74U", "Carbine or SubMG", "Compact police, courier, vehicle, or bodyguard weapon."],
                    ["SKS", "Rifle", "Older rifle, militia, rural or rear-area figure."],
                    ["Mosin-Nagant", "Rifle", "Older rifle, marksman color without Sniper Rifle rules."],
                    ["SVD Dragunov", "Sniper Rifle", "Rare scenario-limited precision weapon."],
                    ["Makarov/TT pistol", "Carbine by scenario or sidearm note", "Normally avoid sidearm micromanagement."],
                    ["Hunting shotgun", "Shotgun", "Rural, criminalized, or household weapon."],
                    ["F1/RGD-5 grenade", "Grenade", "Scenario-limited supply."],
                ], [0.34, 0.23, 0.43], 6.25),
            ],
            [
                image_block("common-weapons-tabletop.png", "Most figures should be Automatics or Rifles. Variety is visual first.", 130),
                table("Normal Limits", ["Item", "Limit"], [
                    ["Sniper Rifle", "Usually zero or one per side."],
                    ["Shotgun", "One or two in rural/criminalized games."],
                    ["Grenades", "Allocated by scenario, never unlimited."],
                    ["Machine guns", "Edge rules only."],
                    ["RPGs/heavy weapons", "Excluded from normal play."],
                ], [0.42, 0.58]),
            ],
        ),
        Page(
            "Weapons",
            "Excluded And Edge Weapons",
            "The weapon boundary is a rules tool, not a denial of history.",
            [
                table("Excluded From Normal Play", ["Weapon", "Handling"], [
                    ["RPG-7 and launchers", "Historical in Book 2; no normal player use."],
                    ["Mortars", "Off-table event or crater history only."],
                    ["Artillery and aircraft", "Pressure clock, sound, crater, refugee route, never player fire."],
                    ["Armored vehicles", "Scenery, timed threat, or blocked road."],
                    ["Heavy machine guns", "Do not appear as portable player weapons."],
                ], [0.38, 0.62]),
                note("Why", "The requested play scale is 10-20 figures per side. Heavy systems pull the game away from movement, routes, skills, and local decisions."),
            ],
            [
                table("Edge Machine Guns", ["Weapon", "Gold Handling", "Warning"], [
                    ["RPK/RPK-74", "Hard edge case; use only by special scenario.", "Breaks the small-arms focus."],
                    ["PK/PKM", "Harder edge case; usually fixed position or off-table.", "At the edge of the game."],
                ], [0.25, 0.4, 0.35], 6.5),
                bullets("If Used", [
                    "Declare it before rosters are built.",
                    "Limit ammunition and fields of fire.",
                    "Make it an objective or hazard, not a casual squad upgrade.",
                    "Never use it to smuggle in heavy-vehicle play.",
                ]),
            ],
        ),
        Page(
            "Forces",
            "Roster Building",
            "Build small forces with visible jobs.",
            [
                table("Roster Size", ["Game Size", "Figures Per Side", "Use"], [
                    ["Patrol", "10-12", "Fast, scenario tight, low weapon variety."],
                    ["Standard", "13-16", "Default game."],
                    ["Large", "17-20", "More civilians, couriers, and pressure clocks."],
                ], [0.25, 0.3, 0.45]),
                table("Figure Jobs", ["Job", "Typical Skills"], [
                    ["Leader", "Command Presence, Formal Negotiation, Hold Under Shelling."],
                    ["Guide", "Back-Alley Route, Mountain Traverse, Cartography."],
                    ["Broker", "Bribe Protocol, Underworld Reputation, Black-Market Appraisal."],
                    ["Medic", "First Aid plus Triage Estimate or Refugee Reassurance."],
                    ["Scout", "Ambush Sense, Silent Crawl, Night Discipline."],
                    ["Carrier", "Load Carry, Casualty Drag, Cold Camp."],
                ], [0.28, 0.72], 6.4),
            ],
            [
                image_block("complete-28mm-skirmish-roster.png", "A force should read clearly at arm's length: leader, guide, carrier, shooter, medic.", 130),
                table("Skill Budget", ["Figure", "Suggestion"], [
                    ["Green/local", "0-1 setting skill."],
                    ["Experienced", "2 setting skills."],
                    ["Specialist", "3 setting skills and one job."],
                    ["Leader", "2-4 skills, mostly AP/ME/RE."],
                    ["Foreign attachment", "2-4 skills, scenario permission required."],
                ], [0.42, 0.58]),
            ],
        ),
        Page(
            "Forces",
            "Playable Ichkerian Or Local Force",
            "Chechen player-side capability comes from skills, terrain, and objectives.",
            [
                table("Archetypes", ["Figure", "Typical Weapon", "Useful Skills"], [
                    ["Local fighter", "Automatic/Rifle", "Back-Alley Route, Rubble Climb."],
                    ["Ex-Soviet officer", "Automatic", "Command Estimate, Radio Procedure."],
                    ["Village guide", "Rifle/Carbine", "Mountain Traverse, Clan Introduction."],
                    ["Courier", "Carbine/SubMG", "Night Discipline, Sprint Across Fire."],
                    ["Cache keeper", "Automatic/Shotgun", "Cache Reading, Contraband Concealment."],
                    ["Medic", "Carbine", "First Aid, Triage Estimate."],
                    ["Elder/contact", "None/Carbine", "Formal Negotiation, Religious Courtesy."],
                ], [0.3, 0.28, 0.42], 6.2),
            ],
            [
                bullets("No Additive Foe Traits", [
                    "Do not give Chechen player forces Gold Soldier armor save.",
                    "Do not give Hunter +1 movement as a free faction rule.",
                    "Do not give Animal rules to local fighters.",
                    "Chechen advantages are chosen skills, terrain knowledge, hidden routes, and scenario objectives.",
                ]),
                image_block("ref-11-chechen-urban-fire-team.png", "Local force rules should reward movement through terrain, not super-soldier labels.", 120),
            ],
        ),
        Page(
            "Forces",
            "Playable Pro-Moscow Or Local Opposition",
            "The second player remains local, even when federal pressure shapes the table.",
            [
                table("Archetypes", ["Figure", "Typical Weapon", "Useful Skills"], [
                    ["Opposition guard", "Automatic", "Checkpoint Demeanor, Command Presence."],
                    ["Police contact", "Carbine/SubMG", "Forged Papers, Formal Negotiation."],
                    ["Militia fighter", "Rifle/Automatic", "Soviet Weapons ID, Rubble Climb."],
                    ["Criminal guard", "Automatic/Shotgun", "Underworld Reputation, Bribe Protocol."],
                    ["Informer handler", "Carbine", "Informant Handling, Back-Alley Route."],
                    ["Cordon runner", "Automatic", "Sprint Across Fire, Night Discipline."],
                ], [0.3, 0.28, 0.42], 6.2),
            ],
            [
                image_block("pro-moscow-chechen-opposition-lineup.png", "The opposition side can be local, political, criminalized, or police-linked.", 118),
                bullets("Federal Link", [
                    "A scenario may give this player federal pressure markers.",
                    "The player does not directly aim artillery, armor, or aircraft.",
                    "Federal arrival can be a timer, table edge threat, blocked road, or cordon shift.",
                    "Use Book 2 for historical explanation; use Book 1 for table effects.",
                ]),
            ],
        ),
        Page(
            "Forces",
            "Foreign Volunteer Attachment",
            "Foreign fighters are scenario attachments, not a replacement for Chechen forces.",
            [
                table("Attachment Rules", ["Rule", "Limit"], [
                    ["Availability", "Only scenarios that name it."],
                    ["Size", "1-4 figures inside a local force."],
                    ["Weapons", "Gold types only; mostly Automatic/Rifle."],
                    ["Skills", "Mountain Traverse, Night Discipline, Religious Courtesy, Radio Procedure, Command Estimate."],
                    ["No free traits", "No Soldier armor save, Hunter move, or Animal rules."],
                ], [0.35, 0.65]),
                note("Khattab Note", "Al Khattab belongs mainly in Book 2. In Book 1 he matters through scenario framing, foreign volunteer limits, and mountain/road-bend case studies."),
            ],
            [
                image_block("ref-20-foreign-volunteers-arrival.png", "Foreign volunteers should appear as a small attachment with a specific job.", 125),
                table("Jobs", ["Job", "Skills"], [
                    ["Trainer", "Soviet Weapons ID, Command Estimate."],
                    ["Guide", "Mountain Traverse, Night Discipline."],
                    ["Camera/media", "Document Search, Command Presence."],
                    ["Religious contact", "Religious Courtesy, Formal Negotiation."],
                ], [0.32, 0.68]),
            ],
        ),
        Page(
            "Enemy Side",
            "Federal Pressure",
            "Russia is covered in detail, but player control stays local.",
            [
                table("Off-Table Pressure", ["Pressure", "Table Effect"], [
                    ["Cordon tightens", "Close one route or add a checkpoint marker."],
                    ["Armor nearby", "Block or threaten a road; no player vehicle."],
                    ["Artillery heard", "Pressure clock advances; crater/debris may appear."],
                    ["Air threat", "Forces movement through cover; no player strike."],
                    ["MVD sweep", "Search markers advance building by building."],
                    ["Negotiation pause", "Freeze firing in a zone; move civilians or couriers."],
                ], [0.34, 0.66], 6.5),
            ],
            [
                image_block("russian-federal-command-map.png", "Federal detail belongs in pressure, timing, routes, and command friction.", 125),
                bullets("Use Federal Detail For", [
                    "Pressure clocks.",
                    "Enemy-only specialists.",
                    "Scenario hazards.",
                    "Historical notes.",
                    "Cordon routes and roadblocks.",
                    "Never a normal Russian regular player army.",
                ]),
            ],
        ),
        Page(
            "Enemy Side",
            "Special Foes: Soldiers, Hunters, Animals",
            "Gold special foes are enemy-side tools here.",
            [
                table("Gold Special Foes", ["Foe", "Gold Rule", "Chechnya Use"], [
                    ["Soldier", "Every shot wound has armor save on 5-6 on d6, including head shots.", "Enemy-only professional federal/special unit."],
                    ["Hunter", "+1 movement.", "Enemy-only tracker, recon, mountain pursuit, or MVD guide."],
                    ["Animal", "Gold animal head shot only succeeds on 5-6; gas rule exists in Gold.", "Enemy-only dog team if used. Default historical mode omits gas."],
                ], [0.18, 0.42, 0.4], 6.0),
                note("Hard Boundary", "Do not give these additive traits to Chechen player rosters. Chechen figures use stats, skills, terrain, and scenario permissions."),
            ],
            [
                table("Specialized Enemy Elements", ["Element", "Additive Package"], [
                    ["Spetsnaz/recon cell", "Soldier + Hunter; limited figures; objective-driven."],
                    ["OMON/SOBR assault cell", "Soldier; strong entry pressure; no player heavy weapons."],
                    ["MVD cordon team", "Soldier on selected figures; search and checkpoint rules."],
                    ["Dog handler", "Animal marker plus handler; enemy-side only."],
                    ["Sniper pair", "Sniper Rifle, Soldier on shooter only, pressure timer."],
                ], [0.36, 0.64], 6.3),
            ],
        ),
        Page(
            "Enemy Side",
            "Specialist Use Limits",
            "Special foes create pressure, not a second full game system.",
            [
                table("Deployment Limits", ["Specialist", "Limit"], [
                    ["Spetsnaz/recon", "1-4 enemy figures, never the whole opposing player roster."],
                    ["Hunter", "Use for pursuit scenes, mountain routes, or cordon collapse."],
                    ["Soldier", "Use sparingly; armor saves slow play."],
                    ["Animal", "Use only when a dog team affects route choice."],
                    ["Sniper pair", "Use as timer, lane denial, or extraction problem."],
                ], [0.34, 0.66]),
                table("No Chechen Mirror", ["Do Not", "Use Instead"], [
                    ["Chechen Hunter trait", "Mountain Traverse, Back-Alley Route, Night Discipline."],
                    ["Chechen Soldier save", "Cover, hidden route, and casualty objectives."],
                    ["Chechen Animal rule", "Guide, courier, or civilian route."],
                ], [0.44, 0.56], 6.6),
            ],
            [
                image_block("ref-12-russian-conscript-column.png", "Federal forces are historically central even when not player-controlled.", 118),
                bullets("Pressure Not Control", [
                    "Enemy specialists should narrow choices, open deadlines, or force movement.",
                    "Do not let them become a full Russian skirmish platoon.",
                    "If the table starts feeling like a regular army battle, cut the specialist count.",
                ]),
            ],
        ),
        Page(
            "Terrain",
            "Terrain Table",
            "Terrain does heavy rules work in this setting.",
            [
                table("Terrain Effects", ["Terrain", "Movement", "Cover", "Notes"], [
                    ["Open road", "Normal", "None", "Dangerous because sight lines are long."],
                    ["Rubble", "No Fast unless Rubble Climb", "Light/Heavy", "Can hide caches and casualties."],
                    ["Interior rooms", "Normal/Slow", "Light", "Doors, stairs, holes, and corners matter."],
                    ["Basement route", "Slow", "Heavy from outside", "May bypass street pressure."],
                    ["Wall/garden", "Climb or detour", "Light/Heavy", "Good village terrain."],
                    ["Ravine", "Slow/Fast only with skill", "Heavy", "Mountain Traverse matters."],
                    ["Culvert", "Slow", "Heavy", "Route or ambush sign."],
                    ["Checkpoint", "Stop/interact", "Light/Heavy", "Social skills may matter more than shooting."],
                ], [0.26, 0.24, 0.2, 0.3], 6.0),
            ],
            [
                image_block("ruined-market-terrain.png", "Terrain should create route choices before it creates fire lanes.", 125),
                table("Terrain Skill Hooks", ["Terrain", "Skills"], [
                    ["Urban", "Back-Alley Route, Rubble Climb, Engineering Survey."],
                    ["Village", "Clan Introduction, Religious Courtesy, Checkpoint Demeanor."],
                    ["Mountain", "Mountain Traverse, Cold Camp, Ambush Sense."],
                    ["Cordon", "Forged Papers, Bribe Protocol, Refugee Reassurance."],
                ], [0.35, 0.65]),
            ],
        ),
        Page(
            "Terrain",
            "Grozny Blocks",
            "Grozny tables need vertical and interior play.",
            [
                table("Urban Features", ["Feature", "Rule Use"], [
                    ["Stairwell", "Choke point; hold, rush, or bypass."],
                    ["Basement", "Hidden route, cache, civilian shelter, or medical point."],
                    ["Hole in wall", "Back-Alley Route or Engineering Survey can find/use."],
                    ["Shell crater", "Light cover; may block Fast movement."],
                    ["Burned vehicle", "Hard cover and road choke."],
                    ["Collapsed room", "Rubble Climb or detour."],
                ], [0.36, 0.64]),
                note("Line Of Sight", "Avoid straight streets that turn every game into a firing range. Use offset buildings, stairwells, courtyards, smoke, vehicles, and rubble piles."),
            ],
            [
                image_block("grozny-apartment-block-skirmish.png", "The best urban boards show routes through buildings, not only roads between them.", 130),
                table("Urban Objectives", ["Objective", "Good For"], [
                    ["Extract documents", "Document Search, escort, pressure clock."],
                    ["Open civilian route", "Refugee Reassurance, hold stairwell."],
                    ["Recover cache", "Cache Reading, Contraband Concealment."],
                    ["Break contact", "Night Discipline, Back-Alley Route."],
                ], [0.4, 0.6], 6.7),
            ],
        ),
        Page(
            "Terrain",
            "Village And Mountain Tables",
            "Small boards still need social and route pressure.",
            [
                table("Village Features", ["Feature", "Rule Use"], [
                    ["Garden wall", "Cover and movement puzzle."],
                    ["Mosque edge", "Religious Courtesy; no spectacle."],
                    ["Cemetery", "Movement boundary and respect zone."],
                    ["Courtyard", "Short-range danger; civilian route."],
                    ["Road cordon", "Checkpoint Demeanor or Bribe Protocol."],
                    ["Shed/barn", "Cache, animal, vehicle scrounge."],
                ], [0.36, 0.64]),
                image_block("village-road-checkpoint.png", "Cordon games should be about routes, searches, and pressure.", 100),
            ],
            [
                table("Mountain Features", ["Feature", "Rule Use"], [
                    ["Ravine road", "Ambush Sense, Mountain Traverse."],
                    ["Culvert", "Hidden movement or warning sign."],
                    ["Wooded slope", "Light cover; movement tax."],
                    ["Rock shelf", "Hard cover; limited exit."],
                    ["Snow/wet cold", "Cold Camp or pressure penalty."],
                    ["Blind bend", "Observation and timing objective."],
                ], [0.36, 0.64]),
                image_block("yaryshmardy-mountain-road-observation.png", "Road-bend scenarios should not require playable heavy weapons.", 100),
            ],
        ),
        Page(
            "Scenarios",
            "Scenario Format",
            "Each scenario uses the same quick-reference structure.",
            [
                table("Scenario Card", ["Line", "Content"], [
                    ["Forces", "Who plays which local force; enemy-only pressure if any."],
                    ["Table", "Terrain features that matter."],
                    ["Setup", "Entry edges, hidden markers, civilians, caches."],
                    ["Objectives", "Doable tasks with no body-count victory."],
                    ["Pressure", "Federal/off-table event timer if used."],
                    ["Refusal line", "What the scenario will not play."],
                    ["History note", "One short context line; Book 2 has detail."],
                ], [0.28, 0.72]),
                table("Pressure Clock", ["Turn/Trigger", "Effect"], [
                    ["Start", "Place pressure marker."],
                    ["Each turn", "Advance if alarm, gunfire, failed social check, or scenario event."],
                    ["Mid clock", "Close route, add enemy search, or shift checkpoint."],
                    ["End clock", "Federal arrival, cordon lock, or forced withdrawal."],
                ], [0.32, 0.68], 6.7),
            ],
            [
                bullets("Ten Scenarios", [f"{s[0]}. {s[1]} - {s[3]}" for s in SCENARIOS], 7.2),
            ],
        ),
    ]

    for number, title, setting, objective in SCENARIOS:
        pages.append(
            Page(
                "Scenarios",
                f"Scenario {number}: {title}",
                setting,
                [
                    table("Scenario Card", ["Line", "Play Detail"], [
                        ["Forces", scenario_forces(number)],
                        ["Table", scenario_table(number)],
                        ["Setup", scenario_setup(number)],
                        ["Objective", objective],
                        ["Refusal", scenario_refusal(number)],
                    ], [0.26, 0.74], 6.15),
                    table("Useful Skills", ["Role", "Skills"], scenario_skills(number), [0.32, 0.68], 6.25),
                ],
                [
                    image_block(scenario_image(number), scenario_caption(number), 120),
                    table("Pressure", ["Trigger", "Effect"], scenario_pressure(number), [0.38, 0.62], 6.4),
                    note("History Note", scenario_history(number), 7.7),
                ],
            )
        )

    pages.extend(
        [
            Page(
                "Campaign",
                "Linked Play",
                "Campaign rules should record consequences without turning into accounting sludge.",
                [
                    table("Between Games", ["Result", "Next Game Effect"], [
                        ["Courier escaped", "One free route clue."],
                        ["Cache recovered", "One extra grenade or one re-roll on ammunition search."],
                        ["Civilian route opened", "Pressure clock starts one step lower."],
                        ["Casualty evacuated", "One wounded figure may return with reduced PH or ME."],
                        ["Checkpoint exposed", "Opponent places one suspicion marker."],
                    ], [0.4, 0.6]),
                    note("No Experience Ladder", "Gold does not use the 2024 use-based advancement table. Campaign growth should be narrative, limited, and agreed before play."),
                ],
                [
                    table("Campaign Track", ["Track", "0", "1", "2", "3"], [
                        ["Pressure", "Quiet", "Watchful", "Search", "Lockdown"],
                        ["Supplies", "Short", "Enough", "Cache", "Overstock"],
                        ["Trust", "Hostile", "Cold", "Useful", "Committed"],
                        ["Exposure", "Hidden", "Rumored", "Named", "Hunted"],
                    ], [0.25, 0.18, 0.18, 0.18, 0.21], 6.4),
                    bullets("Use Tracks For", [
                        "Scenario setup changes.",
                        "Route availability.",
                        "Social skill difficulty.",
                        "Off-table pressure intensity.",
                    ]),
                ],
            ),
            Page(
                "Campaign",
                "Organized Crime, Caches, Bribes",
                "Money and arms networks matter, but they should produce choices.",
                [
                    table("War Economy Actions", ["Action", "Skill", "Game Effect"], [
                        ["Buy passage", "Bribe Protocol", "Delay or bypass a checkpoint."],
                        ["Value a crate", "Black-Market Appraisal", "Know whether cache is worth risk."],
                        ["Hide weapons", "Contraband Concealment", "Reduce search pressure."],
                        ["Find supplier", "Underworld Reputation", "Open one cache lead."],
                        ["Move cash", "Courier plus Back-Alley Route", "Objective marker, not bonus points."],
                    ], [0.31, 0.31, 0.38], 6.1),
                ],
                [
                    image_block("organized-crime-arms-channel.png", "Arms, money, bribes, routes, risk.", 120),
                    bullets("Ethics", [
                        "Do not glamorize kidnapping or trafficking.",
                        "Use criminal networks as pressure and logistics, not reward fantasy.",
                        "If a scenario includes coercive money, keep it abstract and objective-based.",
                    ], 7.9),
                ],
            ),
            Page(
                "Campaign",
                "Faith, Community, Morale",
                "Faith is social context and motivation, not a magic power list.",
                [
                    table("Faith Context", ["Scene", "Useful Skill"], [
                        ["Mosque courtyard", "Religious Courtesy, Formal Negotiation."],
                        ["Funeral or burial edge", "Religious Courtesy, Atrocity Shock."],
                        ["Ramadan/fasting pressure", "Cold Camp, Wounded Calm."],
                        ["Cleric mediation", "Formal Negotiation, Clan Introduction."],
                        ["Foreign volunteer friction", "Religious Courtesy, Command Presence."],
                    ], [0.38, 0.62]),
                    note("Rules Boundary", "Do not make faith a supernatural buff. Use it for morale context, negotiation, restraint, trust, and conflict between local authority and imported ideology."),
                ],
                [
                    image_block("mosque-courtyard-faith-context.png", "Faith scenes should be handled with restraint and practical table purpose.", 118),
                    table("Morale Hooks", ["Event", "Check"], [
                        ["Civilian harm discovered", "Atrocity Shock."],
                        ["Leader wounded", "Command Presence or Hold Under Shelling."],
                        ["Ceasefire ordered", "Ceasefire Patience."],
                        ["Foreign/local disagreement", "Religious Courtesy or Formal Negotiation."],
                    ], [0.45, 0.55], 6.7),
                ],
            ),
            Page(
                "Optional Edges",
                "RPK And PKM Edge Rules",
                "Two human-portable machine guns are hard edge cases.",
                [
                    table("Edge Weapon Warning", ["Weapon", "Permission", "Cost"], [
                        ["RPK/RPK-74", "Scenario only.", "Fixed lane, limited ammo, pressure increase."],
                        ["PK/PKM", "Rare scenario hazard.", "Usually fixed, crewed, or off-table."],
                    ], [0.28, 0.36, 0.36]),
                    bullets("Use Only When", [
                        "The scenario is built around the gun.",
                        "Both players know it bends the small-arms scale.",
                        "Terrain gives bypass routes.",
                        "A non-shooting objective can still win.",
                    ]),
                ],
                [
                    table("Suggested Handling", ["Element", "Rule"], [
                        ["Arc", "Declare before game; no free 360-degree dominance."],
                        ["Ammo", "Use cache/ammo markers; running dry matters."],
                        ["Move", "Very Slow or fixed by scenario."],
                        ["Pressure", "Every burst can advance pressure clock."],
                        ["Capture", "Objective marker; do not make it a permanent roster buy."],
                    ], [0.38, 0.62]),
                    note("Default", "Leave both out. The normal weapon ecology is Automatic, Rifle, Carbine, SubMG, Shotgun, Grenade, and rare Sniper Rifle."),
            ],
            ),
            Page(
                "Quick Reference",
                "Turn And Action Summary",
                "Open this page during play.",
                [
                    table("Common Actions", ["Action", "Effect"], [
                        ["Move", "Use movement table; terrain may reduce or require skill."],
                        ["Shoot", "Use Gold range dice, cover, movement modifiers."],
                        ["Melee", "Use Blow or Weapon check."],
                        ["Throw grenade", "Half movement; dud on 4 or less on 2d6."],
                        ["Heal", "Use Gold healing table."],
                        ["Search/interact", "Use relevant setting skill and scenario clock."],
                        ["Carry/drag", "Use Load Carry or Casualty Drag when needed."],
                    ], [0.32, 0.68], 6.6),
                ],
                [
                    table("Fast Checks", ["Question", "Go To"], [
                        ["Weapon range?", "Page 11."],
                        ["Shotgun/grenade?", "Page 13."],
                        ["Wound location?", "Page 14."],
                        ["Healing?", "Page 15."],
                        ["Skills?", "Pages 6-10."],
                        ["Special foes?", "Pages 22-24."],
                        ["Scenario cards?", "Pages 28-38."],
                    ], [0.48, 0.52]),
                    note("Principle", "When in doubt, pick the closest Gold table and keep play moving."),
                ],
            ),
            Page(
                "Quick Reference",
                "Skill Matrix Quick Reference",
                "The new skills arranged by table problem.",
                [
                    table("Problem Matrix", ["Problem", "Skills To Check First"], [
                        ["Routes", "Cartography, Back-Alley Route, Mountain Traverse, Night Discipline, Silent Crawl."],
                        ["Caches", "Cache Reading, Engineering Survey, Contraband Concealment, Black-Market Appraisal."],
                        ["Checkpoints", "Checkpoint Demeanor, Forged Papers, Bribe Protocol, Formal Negotiation, Resist Coercion."],
                        ["Civilians", "Refugee Reassurance, Religious Courtesy, Clan Introduction, Ceasefire Patience."],
                        ["Casualties", "Triage Estimate, First Aid, Casualty Drag, Load Carry, Wounded Calm."],
                        ["Command", "Command Estimate, Command Presence, Radio Procedure, Hold Under Shelling."],
                        ["Ambush", "Ambush Sense, Soviet Weapons ID, Sprint Across Fire, Night Discipline."],
                        ["War economy", "Underworld Reputation, Vehicle Scrounge, Logistics Count, Informant Handling."],
                    ], [0.28, 0.72], 5.85),
                ],
                [
                    table("Gold Skills Not Replaced", ["Area", "Still Use"], [
                        ["Firearms", "Firearm Use Basic and Advanced."],
                        ["Medical", "First Aid and Paramedic."],
                        ["Melee", "Close Combat."],
                        ["Improvised/Clandestine", "Gold weapon-use chains."],
                        ["Explosives", "Exists, but no grenade modifier."],
                    ], [0.35, 0.65]),
                    bullets("Buying Skills", [
                        "One skill per point in its statistic.",
                        "Prerequisites count against slots.",
                        "Setting skills are 0-100 percent.",
                        "Use them for tasks, route access, social tests, and pressure clocks.",
                    ], 7.9),
                ],
            ),
            Page(
                "Quick Reference",
                "Weapons Quick Tables",
                "Gold weapon data plus Chechnya mapping.",
                [
                    table("Gold Weapons", ["Type", "Range", "Shots", "Notes"], [
                        ["Sniper Rifle", "24/36/48", "1", "No fire under 12 in.; head shot allowed."],
                        ["Rifle", "18/27/36", "1-2", "Two shots with Advanced."],
                        ["Carbine", "12/18/24", "1-2", "Two shots with Advanced."],
                        ["Automatic", "8/12/16", "2", "Jam 1 on 2d6; no head shot."],
                        ["SubMG", "6/9/12", "3", "Jam 1 on 1d6; no head shot."],
                        ["Shotgun", "15 in. cone", "1", "Nearest occupied band only."],
                        ["Grenade", "12 in.", "1 throw", "Dud on 4 or less on 2d6."],
                    ], [0.24, 0.24, 0.16, 0.36], 6.1),
                ],
                [
                    table("Chechnya Mapping", ["Weapon", "Gold Type"], [
                        ["AK-74/AKM/AKS/AKMS", "Automatic"],
                        ["AKS-74U", "Carbine or SubMG"],
                        ["SKS/Mosin", "Rifle"],
                        ["SVD", "Sniper Rifle"],
                        ["Hunting shotgun", "Shotgun"],
                        ["F1/RGD-5", "Grenade"],
                        ["RPK/PKM", "Edge case only"],
                        ["RPG/mortar/heavy weapons", "Excluded"],
                    ], [0.55, 0.45]),
                    note("Reminder", "Do not add new weapon names to the Gold table during play."),
                ],
            ),
            Page(
                "Quick Reference",
                "Terrain And Objective Quick Tables",
                "Use these tables when building a scenario.",
                [
                    table("Terrain Mix", ["Board", "Must Include"], [
                        ["Grozny", "Interior routes, rubble, blocked streets, vertical movement."],
                        ["Village", "Walls, gardens, mosque/cemetery edge, cordon route."],
                        ["Mountain", "Road bend, ravine, culvert, wooded/rock cover."],
                        ["Checkpoint", "Stop point, bypass route, social test, pressure clock."],
                    ], [0.3, 0.7]),
                    table("Objective Verbs", ["Verb", "Good For"], [
                        ["Recover", "Cache, papers, wounded figure."],
                        ["Escort", "Courier, civilian, mediator."],
                        ["Open", "Route, stairwell, gate, checkpoint."],
                        ["Delay", "Sweep, cordon, pursuit."],
                        ["Withdraw", "Before pressure clock ends."],
                    ], [0.28, 0.72]),
                ],
                [
                    table("Pressure Triggers", ["Trigger", "Effect"], [
                        ["Gunfire in quiet area", "Advance pressure."],
                        ["Failed checkpoint test", "Advance pressure or close route."],
                        ["Civilian panic", "Add route problem."],
                        ["Cache found", "Opponent may shift one marker."],
                        ["Clock maxed", "Federal arrival or escape phase."],
                    ], [0.42, 0.58]),
                    image_block("mountain-village-patrol.png", "Good boards make movement as important as shooting.", 96),
                ],
            ),
            Page(
                "Quick Reference",
                "Sources And Boundaries",
                "The rulebook is compact; the reference book carries the history.",
                [
                    table("Primary Rules Sources", ["Source", "Use"], [
                        ["Field of Chaos Gold", "Stats, skills, weapons, wounds, healing, special foes."],
                        ["Book 1", "Chechnya game rules, skill matrix, tables, scenarios."],
                        ["Book 2", "History, leaders, battles, faith, organized crime, weapons context."],
                        ["Bolt Action reference", "Studied for compact table-first layout, not copied for mechanics."],
                    ], [0.36, 0.64]),
                    bullets("Historical Boundaries", [
                        "First Chechen War, 1994-1996.",
                        "Player forces are local, not Russian regulars.",
                        "Organized crime is represented as arms/money logistics.",
                        "Faith is represented as community, mediation, morale, and political context.",
                    ], 7.8),
                ],
                [
                    table("No Import", ["Do Not Import", "Reason"], [
                        ["Bolt Action mechanics", "Different game."],
                        ["Book 2 rules", "Reference book is historical."],
                        ["Modern equipment", "Avoid anachronism."],
                        ["Heavy systems", "Outside requested skirmish focus."],
                        ["Chechen special foe traits", "Only enemy/opposing side gets Gold additive foes."],
                    ], [0.42, 0.58], 6.6),
                ],
            ),
            Page(
                "Quick Reference",
                "Back Cover: Table Reminders",
                "Keep this book open on the table.",
                [
                    table("At A Glance", ["Rule", "Value"], [
                        ["Figures", "10-20 per side, 28mm."],
                        ["Normal weapons", "Automatic, Rifle, Carbine, SubMG, Shotgun, Grenade."],
                        ["Rare weapon", "Sniper Rifle."],
                        ["Edge weapons", "RPK/RPK-74 and PK/PKM only by scenario."],
                        ["Excluded", "RPGs, heavy vehicles, artillery, aircraft, mortars."],
                        ["Chechen capability", "Stats, skills, terrain, route, objective."],
                        ["Enemy-only traits", "Soldier, Hunter, Animal, specialist packages."],
                    ], [0.42, 0.58], 6.5),
                ],
                [
                    image_block("chechen-28mm-miniature-lineup.png", "The game should look and play like a 28mm local-force skirmish.", 135),
                    note("Final Rule", "When rules collide, keep the Gold table intact, keep Russia as pressure or enemy-side specialist, and keep the player decision local."),
                ],
            ),
        ]
    )
    return pages


def scenario_forces(number: str) -> str:
    data = {
        "1": "Local fighters versus pro-Moscow road guards; federal armor is off-table pressure.",
        "2": "Ichkerian/local cell versus opposition guards or police-linked fighters.",
        "3": "Local withdrawal group versus pro-Moscow blocking force.",
        "4": "Local protection group versus criminalized/guard faction under pressure.",
        "5": "Village defenders/guides versus cordon force.",
        "6": "Scout group versus local opposition probes; federal pressure timer.",
        "7": "Cache recovery cell versus guard or police-linked raiders.",
        "8": "Breakout group versus pursuit/cutoff force.",
        "9": "Observation/extraction group versus patrol or pursuit force.",
        "10": "Infiltration cell versus checkpoint and local opposition screens.",
    }
    return data[number]


def scenario_table(number: str) -> str:
    data = {
        "1": "Road, ditch, ruined vehicle, low walls, one bypass path.",
        "2": "Rail/station edge, interiors, stairwell, rubble, smoke lanes.",
        "3": "Palace/rubble zone, basement route, two exit lanes.",
        "4": "Market/hospital edge, civilian route, blocked street.",
        "5": "Village road, courtyard, mosque/cemetery edge, search markers.",
        "6": "Wooded slope, bunker mouth, ravine, hidden exit.",
        "7": "Winter street, cache building, checkpoint, side alley.",
        "8": "Village edge, frozen open ground, ditch, escape edge.",
        "9": "Mountain road bend, culvert, ravine, high observation point.",
        "10": "Night city blocks, basements, checkpoint, guide route.",
    }
    return data[number]


def scenario_setup(number: str) -> str:
    data = {
        "1": "Place courier/cache near road center; pressure starts at 1.",
        "2": "Place documents and one wounded marker inside station/interior zone.",
        "3": "One side starts surrounded on two edges with one hidden exit.",
        "4": "Place three civilian route markers; no firing through route if avoidable.",
        "5": "Hide one person/packet marker among village features.",
        "6": "Place three bunker/exit markers; only one is real objective.",
        "7": "Hide cache in one of three buildings; alarm starts low.",
        "8": "Breakout group begins near village edge; pursuit enters later.",
        "9": "Observation team starts hidden; extraction edge known only after trigger.",
        "10": "Guide chooses one secret route before play; checkpoints start alert.",
    }
    return data[number]


def scenario_refusal(number: str) -> str:
    data = {
        "1": "No player tank fight, RPG duel, or artillery control.",
        "2": "No heavy weapons and no body-count victory.",
        "3": "No palace-as-fortress fantasy; withdrawal is success.",
        "4": "No massacre play; protect routes and witnesses.",
        "5": "No civilian exploitation; searches stay abstract.",
        "6": "No bunker-clearing spectacle with grenades everywhere.",
        "7": "No loot reward fantasy; cache creates risk.",
        "8": "No hostage spectacle; breakout is movement problem.",
        "9": "No playable convoy massacre; heavy weapons off-table.",
        "10": "No Russian regular roster; checkpoints and pressure only.",
    }
    return data[number]


def scenario_skills(number: str) -> list[list[str]]:
    data = {
        "1": [["Guide", "Cartography, Ambush Sense"], ["Courier", "Sprint Across Fire, Back-Alley Route"], ["Guard", "Checkpoint Demeanor, Soviet Weapons ID"]],
        "2": [["Scout", "Rubble Climb, Document Search"], ["Medic", "First Aid, Casualty Drag"], ["Leader", "Hold Under Shelling"]],
        "3": [["Leader", "Command Presence, Command Estimate"], ["Carrier", "Load Carry, Night Discipline"], ["Engineer", "Engineering Survey"]],
        "4": [["Protector", "Refugee Reassurance, Religious Courtesy"], ["Witness", "Document Search"], ["Guard", "Wounded Calm"]],
        "5": [["Guide", "Clan Introduction, Back-Alley Route"], ["Cordon", "Checkpoint Demeanor"], ["Broker", "Bribe Protocol"]],
        "6": [["Scout", "Mountain Traverse, Silent Crawl"], ["Engineer", "Engineering Survey"], ["Leader", "Ceasefire Patience"]],
        "7": [["Broker", "Cache Reading, Black-Market Appraisal"], ["Guard", "Contraband Concealment"], ["Runner", "Vehicle Scrounge"]],
        "8": [["Breakout", "Cold Camp, Sprint Across Fire"], ["Medic", "Triage Estimate"], ["Leader", "Wounded Calm"]],
        "9": [["Observer", "Ambush Sense, Cartography"], ["Guide", "Mountain Traverse"], ["Exit", "Night Discipline"]],
        "10": [["Guide", "Back-Alley Route, Night Discipline"], ["Checkpoint", "Forged Papers"], ["Leader", "Command Presence"]],
    }
    return data[number]


def scenario_pressure(number: str) -> list[list[str]]:
    data = {
        "1": [["Gunfire", "Advance armor-pressure clock."], ["Clock 3", "Road crossing becomes threatened."], ["Clock 4", "Forced withdrawal phase."]],
        "2": [["Alarm", "Add search marker."], ["Wounded moved", "Opponent shifts one guard."], ["Clock 4", "Exit routes narrow."]],
        "3": [["Each turn", "One blocking marker shifts inward."], ["Cache denied", "Pressure pauses once."], ["Clock 4", "Only hidden exit remains."]],
        "4": [["Civilian panic", "Route marker stops."], ["Open route", "Pressure decreases once."], ["Clock 4", "Scenario becomes evacuation only."]],
        "5": [["Failed social check", "Search marker advances."], ["Gunfire", "Cordon closes one lane."], ["Clock 4", "Packet/person must exit immediately."]],
        "6": [["Wrong marker", "Pressure increases."], ["Real marker found", "Exit revealed."], ["Clock 4", "Probe must leave."]],
        "7": [["Cache found", "Alarm rises."], ["Bribe success", "Hold clock one turn."], ["Clock 4", "Checkpoint locks."]],
        "8": [["Open-ground firing", "Pursuit advances."], ["Casualty carried", "Pressure pauses if route opened."], ["Clock 4", "Escape edge shrinks."]],
        "9": [["Observation shot", "Pursuit enters."], ["Culvert used", "Pressure delayed."], ["Clock 4", "Extraction only."]],
        "10": [["Noise", "Checkpoint rotates."], ["Guide lost", "Route becomes uncertain."], ["Clock 4", "Federal arrival ends infiltration."]],
    }
    return data[number]


def scenario_history(number: str) -> str:
    data = {
        "1": "Early-war roads around Dolinskoye show confusion, escalation, and federal pressure without needing playable armor.",
        "2": "The Grozny rail and station fighting was urban, fragmented, and lethal to movement.",
        "3": "Palace fighting is treated as withdrawal and document/cache pressure, not heroic last stand myth.",
        "4": "Shali is handled as aftermath, civilian route, and restraint.",
        "5": "Village cordons combine local knowledge, fear, search pressure, and social risk.",
        "6": "Bamut is a probe-and-withdraw terrain problem, not a tunnel-clearing arcade.",
        "7": "Gudermes-style cache raids suit winter movement, police-linked forces, and informant pressure.",
        "8": "Pervomayskoye belongs here as breakout pressure and frozen movement, not hostage spectacle.",
        "9": "Shatoy/Yaryshmardy road cases are represented through observation, route, and extraction.",
        "10": "August 1996 Grozny infiltration stresses night routes, basements, checkpoints, and local coordination.",
    }
    return data[number]


def scenario_image(number: str) -> str:
    data = {
        "1": "ref-08-dolinskoye-road.png",
        "2": "ref-09-grozny-rail-station.png",
        "3": "ref-10-presidential-palace-ruins.png",
        "4": "ref-13-shali-aftermath.png",
        "5": "ref-14-samashki-empty-street.png",
        "6": "ref-17-bamut-bunker-mouth.png",
        "7": "ref-48-gudermes-checkpoint-aftermath.png",
        "8": "ref-49-pervomayskoye-frozen-breakout.png",
        "9": "ref-28-shatoy-yaryshmardy-road.png",
        "10": "ref-50-august-1996-grozny-infiltration.png",
    }
    return data[number]


def scenario_caption(number: str) -> str:
    return {
        "1": "Dolinskoye road pressure.",
        "2": "Grozny rail station urban movement.",
        "3": "Palace rubble as withdrawal terrain.",
        "4": "Shali aftermath without spectacle.",
        "5": "Village cordon street.",
        "6": "Bamut bunker approach.",
        "7": "Gudermes checkpoint aftermath.",
        "8": "Pervomayskoye frozen breakout.",
        "9": "Shatoy/Yaryshmardy road bend.",
        "10": "August 1996 Grozny infiltration.",
    }[number]


RULE_PROSE = {
    "What This Rulebook Is": "Use this book as the table authority for a short First Chechen War skirmish game. It keeps the Gold rules intact, narrows the player forces to local actors, and turns the larger federal war into pressure, routes, specialists, and deadlines rather than a playable Russian army.",
    "Refusal Lines": "The subject is violent history, so the game needs firm boundaries. The refusal lines are not decorative ethics notes; they tell the scenario writer what the table is allowed to reward. Good play should come from movement, recovery, delay, concealment, evacuation, and difficult withdrawal.",
    "Components And Scale": "The scale is deliberately small. A 28mm figure represents one person, and a table should feel crowded with routes before it feels crowded with weapons. If a board cannot support cover, entry points, hiding places, and withdrawal choices, add terrain before adding rules.",
    "Gold Stats And Character Build": "Gold characters are built from five statistics. The Chechnya layer does not replace those statistics; it gives them setting jobs. Regular Intelligence handles formal knowledge, Irregular Intelligence handles improvised survival, Appearance handles social presentation, Physical Health handles the body, and Mental Health handles nerve.",
    "Gold Skill Chains": "Weapon and medical skills remain the hard mechanical core. The new setting skills are not extra firepower and do not change range bands, grenade duds, shotgun cones, or wound locations. Their job is to decide who can read the room, find a route, steady civilians, or understand a cache.",
    "Forty Setting Skills: RE And IR": "Regular Intelligence and Irregular Intelligence are the two thinking styles most visible in this war. RE covers maps, weapons recognition, radio language, documents, and command estimates. IR covers caches, markets, bribes, false papers, informants, and improvised routes through a shattered city.",
    "Forty Setting Skills: AP, PH, ME": "The social, physical, and mental skills keep the game from becoming only a shooting exercise. Appearance covers how a figure is read by others. Physical Health covers movement under load and broken terrain. Mental Health covers fear, shelling, injury, waiting, and shock.",
    "Skill Matrix In Play": "A skill is permission and leverage, not automatic success. The matrix is the fun part: name the problem, choose how the figure attacks it, and let the skill open the risky option. A guide, broker, medic, scout, and leader should all feel different before anyone fires.",
    "Ranged Weapons": "Fire is resolved by Gold type names. Historical labels such as AK-74, AKM, SVD, SKS, and shotgun are mapped onto those names before play starts. During play, use the Gold range band, dice pool, hit number, and head-shot rule printed here.",
    "Fire Procedure And Jams": "Run shooting in a fixed order so arguments stay short. Pick the target, find the range, build the dice pool, apply cover and movement, then roll. Jams and called head shots are part of the weapon's character; do not smooth them away for convenience.",
    "Shotgun And Grenade": "Shotguns and grenades are dangerous because they affect space, not because they need extra subsystems. The cone and blast bands should be visible on the table before a player commits. Allies can be caught, duds matter, and no skill makes a grenade safer.",
    "Movement, Wounds, Melee": "Gold wounds are location based, so a hit should change what a figure can do. Movement penalties, lost arms, unconsciousness, and casualty recovery create decisions beyond firing back. Melee is short and brutal; it should resolve a local crisis, not replace the weapon rules.",
    "Healing And Casualty Work": "First Aid is still the only direct medical improvement chain in the Gold rules. The Chechnya skills around casualties help a figure reach, assess, move, and calm the wounded. They do not create new healing dice or erase the consequences of location wounds.",
    "Chechnya Weapons To Gold Names": "Most weapons in the game should feel common. The common Soviet-pattern small arms map cleanly to Gold Automatics, Rifles, Carbines, SubMGs, Shotguns, Grenades, and rare Sniper Rifles. If a weapon name does not change decisions on the table, keep it as visual color.",
    "Excluded And Edge Weapons": "The war contained far more than this game allows. The exclusion list protects the requested scale. RPGs, mortars, armored vehicles, aircraft, and artillery are historical realities for Book 2, but in Book 1 they become blocked roads, pressure clocks, craters, or off-table fear.",
    "Roster Building": "Build rosters by jobs, not shopping lists. A good force has someone who leads, someone who knows routes, someone who can handle civilians or brokers, someone who can carry, someone who can treat wounds, and enough ordinary fighters to make choices dangerous.",
    "Playable Ichkerian Or Local Force": "The Ichkerian or local force should not become a superhero faction. Its advantages come from terrain knowledge, chosen skills, caches, guides, hidden routes, and scenario objectives. Keep the figures human, uneven, and local, with Automatics and Rifles forming the usual weapon base.",
    "Playable Pro-Moscow Or Local Opposition": "The opposing player can be local without being simple. Pro-Moscow Chechen opposition, police-linked forces, guards, militia, and criminalized groups can all be played as local actors under federal pressure. They may benefit from cordons and timing, but they do not become a Russian regular army.",
    "Foreign Volunteer Attachment": "Foreign volunteers are small attachments with a defined role. They can bring mountain experience, religious authority, media attention, training, or outside networks, but they should not displace Chechen politics. Use them when the scenario needs that tension, not as a default upgrade.",
    "Federal Pressure": "Russia matters on every board even when no player controls Russian regulars. Federal power appears as a tightening cordon, blocked road, distant shelling, search team, negotiation pause, radio intercept, or arrival clock. This keeps the larger war present without breaking the local-force premise.",
    "Special Foes: Soldiers, Hunters, Animals": "Gold special foes are additive enemy tools, not faction traits for the Chechen player. Use Soldier, Hunter, and Animal sparingly to represent professional pressure, pursuit, or dog teams. The default historical mode does not use the weird gas element unless the table explicitly imports it.",
    "Specialist Use Limits": "Specialists should create urgency, not replace the scenario. A Spetsnaz pair, sniper, dog handler, or MVD cordon element is enough to change movement choices. If the board starts feeling like a full regular-army fight, reduce the specialist count and restore the route problem.",
    "Terrain Table": "Terrain is the main rules engine for Chechnya. A good terrain piece changes movement, sight, cover, social risk, and objective timing at once. Use terrain to make players choose between speed, concealment, civilian safety, and fire positions.",
    "Grozny Blocks": "Grozny should not be a flat street grid. The city game depends on interiors, basements, stairwells, courtyards, collapsed rooms, blocked avenues, and holes between buildings. A player who understands routes should have options that a purely firepower-minded player misses.",
    "Village And Mountain Tables": "Village and mountain boards should feel different from Grozny. Villages create cordons, courtyards, religious spaces, gardens, and social tests. Mountains create route reading, cold, ravines, culverts, hidden exits, and observation problems. Both should reward movement before casualty counting.",
    "Scenario Format": "Each scenario is a compact rules object. Forces, table, setup, objective, pressure, refusal line, and history note should all be visible before play begins. If a scenario cannot be explained in this format, it is probably too large for this rulebook.",
    "Scenario 1: Dolinskoye Road": "Play this as an approach and crossing problem. The federal armor threat is off-table, but it shapes every movement choice. The road is tempting because it is fast and dangerous because it is exposed. Winning should mean crossing, delaying, or recovering, not destroying tanks.",
    "Scenario 2: Grozny Rail Station": "This scenario should feel cramped, loud, and confused. Use interiors, smoke lanes, stairwells, and wounded markers to make movement hard. The rail station is not a shooting gallery; it is a place where documents, exits, casualties, and routes compete for attention.",
    "Scenario 3: Palace Withdrawal": "Treat the palace as a symbolic ruin rather than a fortress fantasy. The interesting decision is when and how to leave, what to deny, and who can still move. The pressure clock should make staying feel costly even when the terrain looks defensible.",
    "Scenario 4: Shali Aftermath": "This is an aftermath scenario, not a spectacle. Civilian route markers and witness or medical objectives should dominate the board. Armed figures still matter, but they are there to open movement, prevent panic, and buy time rather than harvest casualties.",
    "Scenario 5: Village Cordon": "The village cordon is a social and movement game before it is a firefight. Walls, courtyards, elders, religious boundaries, search markers, and false papers all matter. A player who shoots too early should face a faster pressure clock and fewer exit options.",
    "Scenario 6: Bamut Bunker Probe": "Bamut works best as reconnaissance and withdrawal. The players are trying to identify, mark, scout, or escape a strong position, not clear it room by room. Hidden exits and false markers give the terrain uncertainty without importing heavy weapons.",
    "Scenario 7: Gudermes Cache Raid": "This scenario puts the war economy on the table. The cache is valuable because it creates risk, alarm, bargaining, and pursuit. Treat money and arms as logistics and pressure, not as a loot reward that makes the next game absurd.",
    "Scenario 8: Pervomayskoye Breakout": "The breakout should be about cold, exposure, wounded movement, and a shrinking route. Keep hostage history in the reference book and keep the table focused on escape, pursuit, casualty carrying, and pressure timing.",
    "Scenario 9: Shatoy Road Bend": "The road-bend scenario uses observation, timing, and extraction instead of playable heavy weapons. High ground, culverts, and blind corners create the danger. The player goal is to mark, identify, withdraw, or cross before pursuit closes in.",
    "Scenario 10: August Grozny Infiltration": "This is a night-route scenario. Basements, guides, checkpoints, noise, and local coordination matter more than raw firepower. A small mistake should rotate a checkpoint or close a route, pushing the players to improvise rather than stand and trade shots.",
    "Linked Play": "Linked play should remember consequences without becoming a campaign spreadsheet. Carry forward route knowledge, trust, exposure, supplies, pressure, and wounded figures. Avoid a broad experience ladder; the war should become more complicated, not simply more powerful.",
    "Organized Crime, Caches, Bribes": "Organized crime belongs in the rules because money and arms networks shaped what forces could do. Represent it through caches, bribes, brokers, false papers, paid passage, stolen stores, and pressure. Keep the tone logistical and dangerous rather than glamorous.",
    "Faith, Community, Morale": "Faith affects authority, trust, burial, restraint, mediation, foreign-local tension, fasting, and morale. It is not a supernatural bonus list. Use Religious Courtesy and related skills to decide whether a figure understands the setting well enough to avoid making a crisis worse.",
    "RPK And PKM Edge Rules": "These weapons sit at the edge of the requested design. They are human-portable, but they distort a 10-20 figure skirmish if used casually. Put them in only when the scenario is about the gun, its lane, its ammunition, and how to bypass it.",
    "Turn And Action Summary": "This page is for play speed. Use it when a player asks what a figure can do now, then turn to the detailed page only if the action needs a table. The summary is not a replacement for the Gold procedures.",
    "Skill Matrix Quick Reference": "This is the grab-and-go skill page. Start with the table problem rather than the character sheet, then pick the first matching skill. It keeps the force colorful: the best answer might be a calm face, a back route, a stretcher carry, or a forged pass.",
    "Weapons Quick Tables": "Use this page during roster checks and play disputes. If the historical weapon name is distracting the table, map it back to its Gold type and move on. The quick table exists to keep the game from expanding into weapon-by-weapon simulation.",
    "Terrain And Objective Quick Tables": "Use these quick tables when building a board. Choose the terrain identity first, then pick objective verbs that fit the terrain. A Grozny board, village board, and mountain board should ask different movement questions.",
    "Sources And Boundaries": "This rulebook is intentionally compact. It cites its rule source, keeps the historical reference work in Book 2, and names what it refuses to import. That boundary is what lets the table stay playable while still respecting the conflict's complexity.",
    "Back Cover: Table Reminders": "When a dispute reaches the back cover, simplify. Keep the Gold table intact, keep heavy systems off-table, keep Russian regular power as pressure or specialist opposition, and bring the question back to what the local figures can do right now.",
}


def prose_for_page(page: Page) -> str:
    return RULE_PROSE.get(
        page.title,
        "Use this page as rules text first and reference data second. Read the prose to understand intent, then use the tables to settle the exact numbers at the table.",
    )


PLAY_HOOKS = {
    "What This Rulebook Is": "Play hook: start with a job, a route, and a clock. If the board has only targets, add a courier, cache, casualty, or exit.",
    "Refusal Lines": "Play hook: reward the player who solves the problem without making the table uglier. Withdrawal can be the sharpest move in the game.",
    "Components And Scale": "Play hook: before turn one, point out three tempting paths. The safest path, fastest path, and loudest path should not be the same.",
    "Gold Stats And Character Build": "Play hook: give every named figure one thing they are good at and one situation that scares the player who controls them.",
    "Gold Skill Chains": "Play hook: make the non-shooters matter. A fighter with no special weapon can still win the turn with a pass, a stretcher, or a map.",
    "Forty Setting Skills: RE And IR": "Play hook: RE is the clean plan on paper. IR is the plan after the stairwell collapses, the guide vanishes, and the clock moves.",
    "Forty Setting Skills: AP, PH, ME": "Play hook: AP opens doors, PH crosses terrible ground, and ME keeps the player from wasting the one quiet turn they needed.",
    "Skill Matrix In Play": "Play hook: let players argue their column. If the argument tells a good table story, choose a fair difficulty and roll.",
    "Ranged Weapons": "Play hook: make cover matter before range math. A player who wins the fire lane should still have to move to win the scenario.",
    "Fire Procedure And Jams": "Play hook: a jam is not dead air. It is the moment the courier runs, the medic moves, or the other side risks the open lane.",
    "Shotgun And Grenade": "Play hook: put the template down before the throw. If the player winces at the friendly figures nearby, the rule is doing its job.",
    "Movement, Wounds, Melee": "Play hook: a wounded figure is not removed from the story. They become a route problem, a morale problem, and sometimes the whole objective.",
    "Healing And Casualty Work": "Play hook: the best medical scene on the table is a race to reach cover, not a longer arithmetic problem.",
    "Chechnya Weapons To Gold Names": "Play hook: paint the weapons historically, but play the Gold names. The table should look rich and still resolve fast.",
    "Excluded And Edge Weapons": "Play hook: when someone asks for the big weapon, ask what interesting choice it creates. If the answer is only damage, leave it off-table.",
    "Roster Building": "Play hook: build a group that can fail in interesting ways. Too many shooters and not enough jobs makes a flat scenario.",
    "Playable Ichkerian Or Local Force": "Play hook: give this force routes, contacts, and pressure. Do not give it magic toughness or free enemy traits.",
    "Playable Pro-Moscow Or Local Opposition": "Play hook: make the opposition local enough to know the ground and connected enough that the clock feels dangerous.",
    "Foreign Volunteer Attachment": "Play hook: a foreign attachment should complicate the plan as much as it strengthens it.",
    "Federal Pressure": "Play hook: the pressure clock is the third player. It does not need miniatures to make everyone lean over the table.",
    "Special Foes: Soldiers, Hunters, Animals": "Play hook: use special foes like spice, not soup. One professional pressure point is memorable; ten are just another army.",
    "Specialist Use Limits": "Play hook: if the specialist forces only one obvious response, soften it. If it creates three bad choices, keep it.",
    "Terrain Table": "Play hook: every terrain piece should answer two questions: can I hide there, and will it cost me time?",
    "Grozny Blocks": "Play hook: let buildings breathe. A hole in a wall, a stairwell, and a basement exit are worth more than another straight street.",
    "Village And Mountain Tables": "Play hook: villages test faces and families; mountains test lungs and patience. Make the board ask which war this is.",
    "Scenario Format": "Play hook: each scenario needs one clear promise: cross the road, find the cache, carry the wounded, open the route, or get out.",
    "Linked Play": "Play hook: carry forward consequences players can feel in setup, not just numbers on a roster sheet.",
    "Organized Crime, Caches, Bribes": "Play hook: money should unlock a door and create a witness. A clean bargain is less interesting than a useful one.",
    "Faith, Community, Morale": "Play hook: the right courtesy can be as decisive as the right alley. Use it to open restraint, trust, or delay.",
    "RPK And PKM Edge Rules": "Play hook: if the gun appears, the scenario becomes about line, sound, weight, ammunition, and bypass.",
    "Turn And Action Summary": "Play hook: when stuck, make a move that changes the board. Standing still and debating is rarely the brave option.",
    "Skill Matrix Quick Reference": "Play hook: pick a problem row first. The character sheet should answer the table, not the other way around.",
    "Weapons Quick Tables": "Play hook: if a weapon dispute takes longer than the shot, map it to Gold and keep the turn moving.",
    "Terrain And Objective Quick Tables": "Play hook: choose terrain and objective together. A cache in a flat field is dull; a cache behind a checkpoint breathes.",
    "Sources And Boundaries": "Play hook: boundaries make the game sharper. The things left out give the things on the table room to matter.",
    "Back Cover: Table Reminders": "Play hook: the last page answer is almost always the best one: local decision, Gold table, pressure clock, move on.",
}


def play_hook_for_page(page: Page) -> str:
    if page.title.startswith("Scenario "):
        return "Play hook: give both sides a reason to move before the shooting feels comfortable. The clock should make the best route feel late."
    return PLAY_HOOKS.get(page.title, "")


def add_page_prose(pages: list[Page]) -> list[Page]:
    with_prose: list[Page] = []
    for page in pages:
        hook = play_hook_for_page(page)
        right = page.right + ([note("Play Hook", hook, 7.3)] if hook else [])
        with_prose.append(
            Page(
                page.section,
                page.title,
                page.strap,
                [prose(prose_for_page(page))] + page.left,
                right,
            )
        )
    return with_prose


PAGES = add_page_prose(build_pages())


def clean(text: str) -> str:
    return (
        str(text)
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u00a0", " ")
    )


def prepared_image(path: Path) -> Path:
    PDF_ASSETS.mkdir(parents=True, exist_ok=True)
    out = PDF_ASSETS / f"{path.stem}.jpg"
    if out.exists() and out.stat().st_mtime >= path.stat().st_mtime:
        return out
    with Image.open(path) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        im.thumbnail((1200, 1200))
        im.save(out, "JPEG", quality=86, optimize=True, progressive=True)
    return out


def prepared_cover_image(path: Path, target_w: float, target_h: float) -> Path:
    PDF_ASSETS.mkdir(parents=True, exist_ok=True)
    key = f"{int(round(target_w))}x{int(round(target_h))}"
    out = PDF_ASSETS / f"{path.stem}-cover-{key}.jpg"
    if out.exists() and out.stat().st_mtime >= path.stat().st_mtime:
        return out
    aspect = max(target_w / max(target_h, 1), 0.1)
    px_w = 1400
    px_h = max(1, int(round(px_w / aspect)))
    if px_h > 1400:
        px_h = 1400
        px_w = max(1, int(round(px_h * aspect)))
    with Image.open(path) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        im = ImageOps.fit(im, (px_w, px_h), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        im.save(out, "JPEG", quality=88, optimize=True, progressive=True)
    return out


def draw_image(c: canvas.Canvas, path: Path, x: float, y: float, w: float, h: float) -> None:
    img_path = prepared_image(path)
    img = ImageReader(str(img_path))
    iw, ih = img.getSize()
    scale = min(w / iw, h / ih)
    dw, dh = iw * scale, ih * scale
    c.drawImage(img, x + (w - dw) / 2, y + (h - dh) / 2, dw, dh, preserveAspectRatio=True, mask="auto")


def draw_image_cover(c: canvas.Canvas, path: Path, x: float, y: float, w: float, h: float) -> None:
    img_path = prepared_cover_image(path, w, h)
    c.drawImage(ImageReader(str(img_path)), x, y, w, h, preserveAspectRatio=False, mask="auto")


def text_width(text: str, font: str, size: float) -> float:
    return pdfmetrics.stringWidth(clean(text), font, size)


def fit_text(c: canvas.Canvas, text: str, font: str, size: float, x: float, y: float, max_w: float) -> None:
    text = clean(text)
    c.setFont(font, size)
    if text_width(text, font, size) <= max_w:
        c.drawString(x, y, text)
        return
    cut = text
    while cut and text_width(cut.rstrip() + "...", font, size) > max_w:
        cut = cut[:-1]
    c.drawString(x, y, cut.rstrip() + "...")


def wrap(text: str, font: str, size: float, width: float) -> list[str]:
    return simpleSplit(clean(text), font, size, width)


class RulebookBuilder:
    def __init__(self) -> None:
        self.c = canvas.Canvas(str(OUT), pagesize=letter)
        self.page_no = 0

    def new_page(self, section: str | None = None) -> None:
        if self.page_no:
            self.footer()
            self.c.showPage()
        self.page_no += 1
        self.c.setFillColor(PAPER)
        self.c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        if section:
            self.c.setFillColor(GREEN_DARK)
            self.c.setFont(BOLD, MIN_FONT)
            self.c.drawString(MARGIN_X, TOP_Y + 14, section.upper())
            self.c.drawRightString(PAGE_W - MARGIN_X, TOP_Y + 14, "BOOK 1")
            self.c.setStrokeColor(GREEN)
            self.c.setLineWidth(0.55)
            self.c.line(MARGIN_X, TOP_Y + 7, PAGE_W - MARGIN_X, TOP_Y + 7)

    def footer(self) -> None:
        self.c.setStrokeColor(colors.HexColor("#B8B09E"))
        self.c.setLineWidth(0.4)
        self.c.line(MARGIN_X, FOOTER_Y + 13, PAGE_W - MARGIN_X, FOOTER_Y + 13)
        self.c.setFont(BODY, MIN_FONT)
        self.c.setFillColor(MUTED)
        self.c.drawString(MARGIN_X, FOOTER_Y, "Field of Chaos: Chechnya Gold")
        self.c.drawRightString(PAGE_W - MARGIN_X, FOOTER_Y, f"{self.page_no} / {TARGET_PAGES}")

    def draw_cover(self) -> None:
        self.new_page()
        self.c.setTitle("Field of Chaos: Chechnya Gold Rulebook")
        cover = PNG / "chechnya-cover-grozny.png"
        if cover.exists():
            draw_image(self.c, cover, 34, 208, PAGE_W - 68, 510)
            self.c.setStrokeColor(GRID)
            self.c.setLineWidth(1.1)
            self.c.rect(34, 208, PAGE_W - 68, 510, fill=0, stroke=1)
        self.c.setFillColor(colors.HexColor("#FBF8EE"))
        self.c.setStrokeColor(GRID)
        self.c.rect(46, 66, PAGE_W - 92, 122, fill=1, stroke=1)
        self.c.setFillColor(INK)
        self.c.setFont(TITLE, 27)
        self.c.drawCentredString(PAGE_W / 2, 151, "Field of Chaos: Chechnya")
        self.c.setFont(BOLD, 13)
        self.c.setFillColor(GREEN_DARK)
        self.c.drawCentredString(PAGE_W / 2, 124, "Gold Rulebook")
        self.c.setFont(BODY, MIN_FONT)
        self.c.setFillColor(MUTED)
        self.c.drawCentredString(PAGE_W / 2, 102, "Book 1: 48-page fast-player rules")
        self.c.setFont(BOLD, MIN_FONT)
        self.c.drawCentredString(PAGE_W / 2, 84, "28mm skirmish - 10 to 20 miniatures per side")

    def draw_index(self) -> None:
        self.new_page("Index")
        self.c.setFont(TITLE, 24)
        self.c.setFillColor(INK)
        self.c.drawString(MARGIN_X, PAGE_H - 76, "Index")
        self.c.setStrokeColor(GREEN)
        self.c.setLineWidth(0.8)
        self.c.line(MARGIN_X, PAGE_H - 88, PAGE_W - MARGIN_X, PAGE_H - 88)

        by_section: dict[str, list[tuple[int, str]]] = {}
        for offset, page in enumerate(PAGES, start=3):
            by_section.setdefault(page.section, []).append((offset, page.title))
        entries = list(by_section.items())
        col_w = COL_W
        x_positions = [MARGIN_X, MARGIN_X + COL_W + GUTTER]
        y_positions = [PAGE_H - 114, PAGE_H - 114]
        col = 0
        for section, items in entries:
            needed = 17 + 12.2 * len(items) + 8
            if y_positions[col] - needed < BOTTOM_Y:
                col = 1
            x = x_positions[col]
            y = y_positions[col]
            self.c.setFont(BOLD, MIN_FONT)
            self.c.setFillColor(GREEN_DARK)
            first_page = items[0][0]
            self.c.drawString(x, y, section)
            self.c.drawRightString(x + col_w, y, str(first_page))
            y -= 13.0
            self.c.setFont(BODY, MIN_FONT)
            self.c.setFillColor(INK)
            for page_no, title in items:
                fit_text(self.c, title, BODY, MIN_FONT, x + 10, y, col_w - 28)
                self.c.drawRightString(x + col_w, y, str(page_no))
                y -= 12.2
            y_positions[col] = y - 5

    def title_area(self, page: Page) -> tuple[float, float]:
        y = PAGE_H - 72
        self.c.setFont(TITLE, 21)
        self.c.setFillColor(INK)
        fit_text(self.c, page.title, TITLE, 21, MARGIN_X, y, PAGE_W - 2 * MARGIN_X)
        self.c.setStrokeColor(GREEN)
        self.c.setLineWidth(0.6)
        self.c.line(MARGIN_X, y - 12, PAGE_W - MARGIN_X, y - 12)
        self.c.setFont(ITALIC, MIN_FONT)
        self.c.setFillColor(MUTED)
        for line in wrap(page.strap, ITALIC, MIN_FONT, PAGE_W - 2 * MARGIN_X):
            self.c.drawString(MARGIN_X, y - 28, line)
            break
        return MARGIN_X, y - 56

    def draw_pages(self) -> None:
        for page in PAGES:
            self.new_page(page.section)
            _, top = self.title_area(page)
            self.draw_column(MARGIN_X, top, COL_W, page.left)
            self.draw_column(MARGIN_X + COL_W + GUTTER, top, COL_W, page.right)

    def draw_column(self, x: float, y: float, w: float, blocks: list[Block]) -> None:
        for block in blocks:
            if block.kind == "table":
                y = self.draw_table(x, y, w, **block.data)
            elif block.kind == "prose":
                y = self.draw_prose(x, y, w, **block.data)
            elif block.kind == "bullets":
                y = self.draw_bullets(x, y, w, **block.data)
            elif block.kind == "note":
                y = self.draw_note(x, y, w, **block.data)
            elif block.kind == "image":
                y = self.draw_image_block(x, y, w, **block.data)
            else:
                raise ValueError(block.kind)
            if y < BOTTOM_Y - 6:
                raise RuntimeError(f"Page {self.page_no} overflow after {block.kind}: {y}")

    def draw_prose(self, x: float, y: float, w: float, text: str, size: float = MIN_FONT) -> float:
        size = max(size, MIN_FONT)
        self.c.setFillColor(INK)
        self.c.setFont(BODY, size)
        line_h = size + 2.1
        paragraphs = [p.strip() for p in clean(text).split("\n\n") if p.strip()]
        for paragraph in paragraphs:
            lines = wrap(paragraph, BODY, size, w)
            for line in lines:
                self.c.drawString(x, y - size, line)
                y -= line_h
            y -= 3.2
        return y - 7

    def draw_table(
        self,
        x: float,
        y: float,
        w: float,
        title: str,
        headers: list[str],
        rows: list[list[str]],
        widths: list[float] | None = None,
        size: float = MIN_FONT,
    ) -> float:
        size = max(size, MIN_FONT)
        widths = widths or [1 / len(headers)] * len(headers)
        col_ws = [w * frac for frac in widths]
        title_h = 19
        header_h = 18
        pad = 4
        line_h = size + 1.35

        row_heights: list[float] = []
        wrapped_rows: list[list[list[str]]] = []
        for row in rows:
            wrapped_cells: list[list[str]] = []
            max_lines = 1
            for idx, cell in enumerate(row):
                lines = wrap(cell, BODY, size, col_ws[idx] - 2 * pad)
                max_lines = max(max_lines, len(lines))
                wrapped_cells.append(lines)
            wrapped_rows.append(wrapped_cells)
            row_heights.append(max(14, max_lines * line_h + 6))

        total_h = title_h + header_h + sum(row_heights)
        self.c.setFillColor(GREEN)
        self.c.rect(x, y - title_h, w, title_h, fill=1, stroke=0)
        self.c.setFillColor(colors.white)
        self.c.setFont(BOLD, MIN_FONT)
        fit_text(self.c, title.upper(), BOLD, MIN_FONT, x + 6, y - 13.0, w - 12)
        y -= title_h

        self.c.setFillColor(colors.HexColor("#A9AC9A"))
        self.c.rect(x, y - header_h, w, header_h, fill=1, stroke=0)
        xx = x
        self.c.setFont(BOLD, MIN_FONT)
        self.c.setFillColor(colors.white)
        for idx, head in enumerate(headers):
            fit_text(self.c, head.upper(), BOLD, MIN_FONT, xx + pad, y - 12.5, col_ws[idx] - 2 * pad)
            xx += col_ws[idx]
        y -= header_h

        for r_idx, wrapped_cells in enumerate(wrapped_rows):
            h = row_heights[r_idx]
            self.c.setFillColor(ROW_LIGHT if r_idx % 2 == 0 else ROW_ALT)
            self.c.rect(x, y - h, w, h, fill=1, stroke=0)
            xx = x
            for c_idx, lines in enumerate(wrapped_cells):
                self.c.setFillColor(INK)
                self.c.setFont(BODY, size)
                yy = y - 6 - size
                for line in lines:
                    self.c.drawString(xx + pad, yy, line)
                    yy -= line_h
                xx += col_ws[c_idx]
            y -= h

        self.c.setStrokeColor(GRID)
        self.c.setLineWidth(0.45)
        self.c.rect(x, y, w, total_h, fill=0, stroke=1)
        xx = x
        for cw in col_ws[:-1]:
            xx += cw
            self.c.line(xx, y, xx, y + total_h - title_h)
        return y - 10

    def draw_bullets(self, x: float, y: float, w: float, title: str, items: list[str], size: float = MIN_FONT) -> float:
        size = max(size, MIN_FONT)
        self.c.setFillColor(GREEN_DARK)
        self.c.setFont(BOLD, MIN_FONT)
        self.c.drawString(x, y, title.upper())
        y -= 11
        self.c.setStrokeColor(GREEN)
        self.c.setLineWidth(0.45)
        self.c.line(x, y + 4, x + w, y + 4)
        self.c.setFont(BODY, size)
        self.c.setFillColor(INK)
        line_h = size + 2.4
        for item in items:
            lines = wrap(item, BODY, size, w - 12)
            self.c.drawString(x, y - size, "-")
            yy = y - size
            for line in lines:
                self.c.drawString(x + 10, yy, line)
                yy -= line_h
            y = yy - 1
        return y - 7

    def draw_note(self, x: float, y: float, w: float, title: str, text: str, size: float = MIN_FONT) -> float:
        size = max(size, MIN_FONT)
        lines = wrap(text, BODY, size, w - 12)
        h = 22 + len(lines) * (size + 2.2)
        self.c.setFillColor(PALE)
        self.c.setStrokeColor(GRID)
        self.c.rect(x, y - h, w, h, fill=1, stroke=1)
        self.c.setFont(BOLD, MIN_FONT)
        self.c.setFillColor(RED)
        self.c.drawString(x + 6, y - 12, title.upper())
        self.c.setFont(BODY, size)
        self.c.setFillColor(INK)
        yy = y - 25
        for line in lines:
            self.c.drawString(x + 6, yy, line)
            yy -= size + 2.2
        return y - h - 10

    def draw_image_block(self, x: float, y: float, w: float, filename: str, caption: str, height: float = 102) -> float:
        path = PNG / filename
        height = max(height, 135)
        cap_lines = simpleSplit(caption, ITALIC, MIN_FONT, w - 12)
        line_count = max(1, min(2, len(cap_lines)))
        cap_h = line_count * 12.0 + 8
        if path.exists():
            self.c.setFillColor(colors.HexColor("#EEE8D8"))
            self.c.setStrokeColor(GRID)
            self.c.rect(x, y - height, w, height, fill=1, stroke=1)
            draw_image_cover(self.c, path, x + 4, y - height + 4, w - 8, height - 8)
        else:
            self.c.setFillColor(PALE)
            self.c.setStrokeColor(GRID)
            self.c.rect(x, y - height, w, height, fill=1, stroke=1)
            self.c.setFont(BODY, MIN_FONT)
            self.c.setFillColor(MUTED)
            self.c.drawCentredString(x + w / 2, y - height / 2, filename)
        self.c.setFillColor(PALE)
        self.c.rect(x, y - height - cap_h, w, cap_h, fill=1, stroke=0)
        self.c.setFont(ITALIC, MIN_FONT)
        self.c.setFillColor(MUTED)
        caption_y = y - height - 13
        for line in cap_lines[:line_count]:
            self.c.drawString(x + 6, caption_y, line)
            caption_y -= 12.0
        return y - height - cap_h - 10

    def save(self) -> None:
        self.footer()
        self.c.save()


def main() -> None:
    if len(PAGES) != TARGET_PAGES - 2:
        raise SystemExit(f"Expected {TARGET_PAGES - 2} content pages, got {len(PAGES)}")
    builder = RulebookBuilder()
    builder.draw_cover()
    builder.draw_index()
    builder.draw_pages()
    if builder.page_no != TARGET_PAGES:
        raise SystemExit(f"Expected {TARGET_PAGES} pages, got {builder.page_no}")
    builder.save()
    print(f"Wrote {OUT}")
    print(f"Pages: {builder.page_no}")
    print(f"Setting skills: {len(ALL_SKILLS)}")


if __name__ == "__main__":
    main()
