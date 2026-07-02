#!/usr/bin/env python3
"""Build text-first book drafts from the research corpus data."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
REBUILD = ROOT / "tools" / "rebuild_research_corpus.py"
REFERENCE_PLAN = ROOT / "reference-page-plan.md"
BOOK2 = ROOT / "book2-reference-draft.txt"
BOOK1 = ROOT / "book1-rulebook-draft.txt"
IMAGES = ROOT / "image-statements.md"


spec = importlib.util.spec_from_file_location("research_data", REBUILD)
research_data = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(research_data)


BOOK2_PAGES = [
    ("Cover: Field of Chaos Chechnya Gold Reference", "reference-cover"),
    ("How To Use This Reference Book", "method"),
    ("Chechnya Before 1991: Empire, Soviet Rule, And Memory", "society"),
    ("The 1944 Deportation And Return", "society"),
    ("Dudayev's Revolution And The Ichkerian Claim", "leader:Dzhokhar Dudayev"),
    ("Moscow, Opposition Councils, And The Road To War", "russian"),
    ("Organized Crime Before Open War", "crime"),
    ("Arms Ecology Before December 1994", "weapon:AK-74 and AKS-74"),
    ("The Russian State And Army In The Post-Soviet Crisis", "russian"),
    ("The Federal Decision For War", "russian"),
    ("Dolinskoye And The Opening Shock", "battle:Dolinskoye, December 1994"),
    ("New Year's Eve In Grozny: Operational Overview", "battle:New Year's Eve assault on Grozny, December 1994-January 1995"),
    ("Grozny Railway Station And Column Disaster", "battle:New Year's Eve assault on Grozny, December 1994-January 1995"),
    ("Presidential Palace And Symbolic Defense", "battle:Presidential Palace and central Grozny, January 1995"),
    ("Chechen Urban Fire Teams", "faction:Ichkerian local fighters"),
    ("Russian Urban Failure And Adaptation", "russian"),
    ("Grozny Civilian Destruction", "ethics"),
    ("Shali: Air Power And Civilian Harm", "battle:Shali cluster-bomb attack, 3 January 1995"),
    ("Samashki: Atrocity History And Non-Game Boundaries", "battle:Samashki, 7-8 April 1995"),
    ("Spring And Summer 1995 Lowland War", "battle:Gudermes and lowland raids, December 1995"),
    ("Budyonnovsk: Raid, Terror, And Negotiation", "battle:Budyonnovsk, June 1995"),
    ("Ceasefire Attempts And Negotiation Pressure", "russian"),
    ("Bamut: Fortified Endurance", "battle:Bamut, March 1995-May 1996"),
    ("Bamut Terrain And Bunker Logic", "battle:Bamut, March 1995-May 1996"),
    ("Mountain Warfare In The Southern Districts", "battle:Shatoy/Yaryshmardy ambush, 16 April 1996"),
    ("Foreign Volunteers In The First War", "faction:Foreign volunteer cell"),
    ("Al Khattab I: Origins And Afghan War", "leader:Ibn al-Khattab"),
    ("Al Khattab II: Injury, Hand Detail, And Myth Control", "leader:Ibn al-Khattab"),
    ("Al Khattab III: Tajikistan And The Rabbit Source", "leader:Ibn al-Khattab"),
    ("Al Khattab IV: Arrival In Chechnya", "leader:Ibn al-Khattab"),
    ("Al Khattab V: Media, Money, And Training", "leader:Ibn al-Khattab"),
    ("Al Khattab VI: Bin Laden Connection", "leader:Ibn al-Khattab"),
    ("Al Khattab VII: Basayev, Shatoy, And Reputation", "leader:Ibn al-Khattab"),
    ("Al Khattab VIII: Legacy And Limits", "leader:Ibn al-Khattab"),
    ("Shatoy/Yaryshmardy: Ambush Anatomy", "battle:Shatoy/Yaryshmardy ambush, 16 April 1996"),
    ("Islam In Chechnya: Overview", "islam"),
    ("Sufi Brotherhoods And Local Practice", "islam"),
    ("Jihad As Local Defense", "islam"),
    ("Foreign Salafi Influence", "islam"),
    ("Akhmad Kadyrov And Anti-Wahhabi Politics", "leader:Akhmad Kadyrov"),
    ("Faith, Propaganda, And Russian Framing", "islam"),
    ("Organized Crime: War Economy Overview", "crime"),
    ("Moscow Obshina And Noukhayev", "leader:Khozh-Ahmed Noukhayev"),
    ("Oil Theft, Arms, And Corruption", "crime"),
    ("Kidnapping, Hostages, And Coercive Money", "crime"),
    ("Russian Corruption And Weapons Leakage", "crime"),
    ("Teips, Villages, And Local Loyalties", "society"),
    ("Warlordism And Commander-Centered Authority", "society"),
    ("Dudayev Profile", "leader:Dzhokhar Dudayev"),
    ("Maskhadov Profile", "leader:Aslan Maskhadov"),
    ("Basayev Profile", "leader:Shamil Basayev"),
    ("Yandarbiyev Profile", "leader:Zelimkhan Yandarbiyev"),
    ("Gelayev Profile", "leader:Ruslan Gelayev"),
    ("Raduyev Profile", "leader:Salman Raduyev"),
    ("Akhmad Kadyrov Profile", "leader:Akhmad Kadyrov"),
    ("Zavgayev And Avturkhanov", "leader:Doku Zavgayev"),
    ("Noukhayev And Crime-Politics Overlap", "leader:Khozh-Ahmed Noukhayev"),
    ("Yeltsin And The Federal Presidency", "leader:Boris Yeltsin"),
    ("Grachev, Kulikov, And Federal Command Failure", "leader:Pavel Grachev"),
    ("Lebed And The Khasavyurt Exit", "leader:Aleksandr Lebed"),
    ("Russian Army Formations And Conscripts", "russian"),
    ("MVD, OMON, SOBR, And Police War", "russian"),
    ("Spetsnaz, FSB, And Intelligence Operations", "russian"),
    ("Russian Logistics, Morale, And Media", "russian"),
    ("Federal Firepower: Artillery And Air Power", "russian"),
    ("Refugees, Civilians, And Destroyed Homes", "ethics"),
    ("Human Rights Sources And How To Use Them", "ethics"),
    ("Weapon Reference Overview And Gold Mapping", "weapon:AK-74 and AKS-74"),
    ("AK-74, AKS-74, AKM, And AKMS", "weapon:AK-74 and AKS-74"),
    ("AKS-74U And Compact Weapons", "weapon:AKS-74U"),
    ("SKS, Mosin, And Older Rifles", "weapon:SKS"),
    ("SVD And Sniper Rifle Mapping", "weapon:SVD Dragunov"),
    ("SMGs For Police And Security", "weapon:PP-91 Kedr, OTs-02 Kiparis, and compact SMGs"),
    ("Shotguns And Civilian Smoothbores", "weapon:Hunting shotguns and civilian smoothbores"),
    ("Grenades: F-1, RGD-5, And VOG Improvisation", "weapon:F-1 defensive grenade"),
    ("RPK/RPK-74 Edge Case", "weapon:RPK and RPK-74"),
    ("PK/PKM Edge Case", "weapon:PK and PKM"),
    ("RPGs: Historically Central, Rules-Excluded", "weapon:RPG-7 and RPG-18"),
    ("RPO, Launchers, And Other Excluded Weapons", "weapon:RPO-A Shmel and other thermobaric launchers"),
    ("Vehicles And Heavy Weapons As Off-Table Pressure", "russian"),
    ("28mm Figure Style And Miniature Range Notes", "figures"),
    ("Grozny Terrain For 28mm Tables", "terrain"),
    ("Village Terrain: Walls, Yards, Mosques, And Roads", "terrain"),
    ("Mountain Terrain: Roads, Ravines, And Wooded Slopes", "terrain"),
    ("Checkpoints, Caches, Couriers, And Patrol Routes", "terrain"),
    ("Playable Sides: Why The Players Are Local", "faction:Pro-Moscow Chechen opposition"),
    ("Roster Archetypes", "faction:Ichkerian local fighters"),
    ("Scenario Ethics And Historical Boundaries", "ethics"),
    ("Scenario Reference 1: Dolinskoye Road", "battle:Dolinskoye, December 1994"),
    ("Scenario Reference 2: Grozny Rail Station", "battle:New Year's Eve assault on Grozny, December 1994-January 1995"),
    ("Scenario Reference 3: Palace Withdrawal", "battle:Presidential Palace and central Grozny, January 1995"),
    ("Scenario Reference 4: Shali Aftermath", "battle:Shali cluster-bomb attack, 3 January 1995"),
    ("Scenario Reference 5: Village Cordon After Samashki", "battle:Samashki, 7-8 April 1995"),
    ("Scenario Reference 6: Bamut Bunker Probe", "battle:Bamut, March 1995-May 1996"),
    ("Scenario Reference 7: Budyonnovsk Route Pressure", "battle:Budyonnovsk, June 1995"),
    ("Scenario Reference 8: Gudermes Cache Raid", "battle:Gudermes and lowland raids, December 1995"),
    ("Scenario Reference 9: Pervomayskoye Breakout", "battle:Kizlyar-Pervomayskoye, January 1996"),
    ("Scenario Reference 10: Shatoy Road Bend", "battle:Shatoy/Yaryshmardy ambush, 16 April 1996"),
    ("Scenario Reference 11: August 1996 Grozny", "battle:August 1996 Grozny"),
    ("Khasavyurt And The Treaty Track", "russian"),
    ("Interwar Consequences Without Rewriting The First War", "ethics"),
    ("First War Versus Second War: Avoiding Anachronism", "method"),
    ("Field Research Questions Still Open", "method"),
    ("Miniature Sourcing And Plastic Conversion Notes", "figures"),
    ("Glossary Of Chechen War Terms", "method"),
    ("Detailed Timeline", "method"),
    ("Order Of Battle As Abstraction", "russian"),
    ("Bibliography And Source Cautions", "method"),
    ("Gold Rules Crosswalk", "weapon:AK-74 and AKS-74"),
    ("Map Notes For Non-Cartographic Layout", "terrain"),
    ("Civilian Harm Best Practices For Scenarios", "ethics"),
    ("Appendix: Paraphrased Source Nuggets", "method"),
    ("Weapon Quick Table", "weapon:AK-74 and AKS-74"),
    ("Leader Quick Table", "method"),
    ("Battle Quick Table", "method"),
    ("Image Index And Render Instructions", "figures"),
    ("Rulebook Cross-References", "method"),
    ("Designer Audit Checklist", "method"),
    ("Final Source And Revision Log", "method"),
    ("Back Matter And Final Historical Warning", "ethics"),
]


IMAGE_SUBJECTS = [
    "Reference cover: ruined Grozny street with local armed men and civilians moving through rubble",
    "Chechnya before 1991: mountain village, Soviet road, cemetery, and long memory landscape",
    "The 1944 deportation and return: empty village houses, rail shadows, and returning families",
    "Dudayev-era command room with former Soviet aviation cues and Ichkerian papers",
    "Moscow-backed Chechen opposition council before the open invasion",
    "Prewar arms ecology: common Soviet small arms, civilian coats, police leakage, and black-market table",
    "Federal decision room in Moscow with Chechnya maps and anxious officials",
    "Dolinskoye road approach in December 1994 with winter fields and burned road markers",
    "Grozny rail station rubble after the New Year's assault",
    "Presidential Palace ruins as a symbol of destroyed state authority",
    "Chechen urban fire team moving through basements and upper floors",
    "Russian conscript column stalled on Grozny outskirts, seen at distance without glamour",
    "Shali aftermath without gore: market, hospital district, cratered street, and civilians searching",
    "Samashki empty village street after a federal cordon, smoke and abandoned household objects",
    "Budyonnovsk route planning without hostage spectacle: buses, maps, and grim commanders",
    "Ceasefire negotiation room with weary intermediaries and maps",
    "Bamut bunker mouth and wooded slope",
    "Bamut hardened shelters and village defenses in rain",
    "Southern mountain road logistics: pack loads, narrow ravine, and hidden withdrawal paths",
    "Foreign volunteers arriving among local Chechen fighters, modest and historically grounded",
    "Al Khattab source-photo likeness portrait: papakha, blue-gray camouflage parka, sock-covered right stump",
    "Al Khattab Afghan-war injury context: source-photo face traits, right stump covered in sock-like cloth, no heroic exaggeration",
    "Rabbit anecdote still life: Abdulkareem Khadr's rabbit named Khattab, no bin Laden present",
    "Al Khattab entering Chechnya under journalist-cover travel context, source-photo likeness and sock-covered stump",
    "Al Khattab with cameraman and battlefield media equipment, source-photo likeness and sock-covered stump",
    "Bin Laden connection as an abstract network table: documents, money routes, and separate silhouettes",
    "Khattab and Basayev field command, grounded and non-mythic, Khattab in black beret or papakha and sock-covered stump",
    "Shatoy/Yaryshmardy mountain road bend after an ambush, no gore",
    "Chechen mosque courtyard and local faith context",
    "Jihad as local defense: funeral, elders, and fighters at village edge",
    "Akhmad Kadyrov as mufti mediating community politics",
    "Organized-crime arms channel: money, bribes, weapons, and transport",
    "Oil theft and weapons leakage at a rough depot",
    "Teip and village loyalty: courtyard meeting with elders and armed young men",
    "Dudayev profile in a damaged presidential office",
    "Maskhadov staff map in a Grozny cellar",
    "Basayev field command after a long road movement",
    "Yandarbiyev political council after Dudayev's death",
    "Gelayev mountain column moving through snow and rock",
    "Raduyev Pervomayskoye breakout planning without hostage spectacle",
    "Akhmad Kadyrov community scene in the first-war religious-political context",
    "Noukhayev underworld-politics table with ledgers, protection money, and pipeline sketches",
    "Yeltsin-era Kremlin Chechnya map table",
    "Grachev federal command briefing with overconfident staff atmosphere",
    "Lebed Khasavyurt negotiation table",
    "MVD cordon at village edge",
    "Federal firepower aftermath: destroyed apartment block and shell crater, no active bombardment",
    "Gudermes winter checkpoint raid aftermath with local police post and broken barriers",
    "Pervomayskoye frozen-steppe breakout landscape",
    "August 1996 Grozny infiltration route through mined streets and isolated strongpoints",
]

IMAGE_PAGES = [
    1, 3, 4, 5, 6, 8, 10, 11, 13, 14,
    15, 16, 18, 19, 21, 22, 23, 24, 25, 26,
    27, 28, 29, 30, 31, 32, 33, 35, 36, 38,
    40, 42, 44, 47, 49, 50, 51, 52, 53, 54,
    55, 57, 58, 59, 60, 62, 65, 96, 97, 99,
]


HISTORICAL_WEAPON_NOTES = {
    "AK-74 and AKS-74": "The 5.45 mm AK-74 family was a standard Soviet and Russian service rifle family and appears throughout federal, police, militia, and captured-stock contexts.",
    "AKM and AKMS": "The older 7.62 mm Kalashnikov family remained widespread in post-Soviet arsenals, black markets, village stocks, and captured inventories.",
    "AKS-74U": "The compact AKS-74U was associated with vehicle crews, police, officers, guards, and urban close-quarters use.",
    "SKS": "Older semi-automatic carbines such as the SKS help explain the mixed character of local armament in a collapsing post-Soviet weapons environment.",
    "Mosin-Nagant and older bolt-action rifles": "Older bolt-action rifles were not central to the war's image, but they could persist in rural stocks, hunting contexts, and low-grade militia hands.",
    "SVD Dragunov": "The SVD Dragunov was the most recognizable Soviet designated-marksman rifle in the conflict and appears in both federal and Chechen hands.",
    "VSS Vintorez or suppressed specialist rifles": "Suppressed specialist rifles belonged more to security-service and specialist contexts than to ordinary local fighting groups.",
    "PP-91 Kedr, OTs-02 Kiparis, and compact SMGs": "Compact submachine guns and police weapons help explain the equipment of security personnel, bodyguards, and internal troops.",
    "Hunting shotguns and civilian smoothbores": "Civilian smoothbores connect the war to rural self-defense, hunting culture, guard work, and improvised local security.",
    "F-1 defensive grenade": "The F-1 fragmentation grenade was a common Soviet-pattern grenade and part of the wider inherited stock of small munitions.",
    "RGD-5 offensive grenade": "The RGD-5 was another common Soviet-pattern grenade, often associated with close urban and trench fighting.",
    "VOG-17 or VOG-25 improvised Khattabka grenade": "Improvised grenade use and the later term Khattabka show how battlefield improvisation, launcher ammunition, and Khattab's name entered militant vocabulary.",
    "RPK and RPK-74": "The RPK family occupied the light automatic-rifle space between ordinary rifles and belt-fed machine guns in Soviet and post-Soviet squad arsenals.",
    "PK and PKM": "The PK/PKM belt-fed machine gun was a major infantry support weapon in strongpoint, ambush, and defensive contexts.",
    "RPG-7 and RPG-18": "RPG weapons were central to Chechen anti-armor tactics and to the destruction of Russian vehicles in Grozny and mountain-road ambushes.",
    "RPO-A Shmel and other thermobaric launchers": "Thermobaric launchers and specialized assault weapons belong to the history of federal firepower, urban destruction, and extreme close assault.",
    "PM Makarov and sidearms": "Sidearms were common officer, police, and security weapons but rarely define the tactical history as strongly as rifles, grenades, machine guns, and launchers.",
}


HISTORICAL_FACTION_NOTES = {
    "Ichkerian local fighters": "Village, teip, nationalist, and veteran-based fighters aligned with the Chechen Republic of Ichkeria formed the local core of resistance.",
    "Pro-Moscow Chechen opposition": "Anti-Dudayev and Moscow-backed Chechen opposition forces were central to the pre-invasion crisis and to later local collaboration structures.",
    "Chechen criminalized patronage group": "Armed patronage groups tied to rackets, oil, weapons, protection, and local commanders blurred the boundary between politics and organized crime.",
    "Foreign volunteer cell": "Foreign volunteers were a small but consequential current whose Afghan-war experience, media networks, and external funding influenced parts of the war.",
    "Russian regular forces": "Russian regular forces brought armor, artillery, aviation, conscripts, professional officers, and institutional post-Soviet disorder into the conflict.",
    "MVD, OMON, SOBR, and federal security forces": "Internal troops and police special units shaped checkpoints, cordons, raids, garrison life, village sweeps, and urban security operations.",
}


BOOK1_PAGES = [
    ("Cover: Field of Chaos Chechnya Gold Rules", "cover"),
    ("What This Rulebook Is", "rules"),
    ("What It Refuses To Be", "ethics"),
    ("Components, Scale, And Table Size", "rules"),
    ("Gold Core: Stats And Skills", "gold"),
    ("Gold Core: Ranged Fire", "gold"),
    ("Gold Core: Wounds, Cover, And Movement", "gold"),
    ("Gold Core: Shotgun And Grenade", "gold"),
    ("Weapons Of Chechnya: Mapping To Gold", "weapons"),
    ("Automatic Weapons: AK-74, AKM, AKS-74", "weapons"),
    ("Rifle, Carbine, Sniper Rifle", "weapons"),
    ("SubMG, Shotgun, Grenade", "weapons"),
    ("Excluded Weapons And Edge Machine Guns", "weapons"),
    ("Player Sides: Local, Not Russian Regulars", "factions"),
    ("Ichkerian Local Fighter Force", "factions"),
    ("Pro-Moscow Chechen Opposition Force", "factions"),
    ("Criminalized Patronage And Guard Forces", "factions"),
    ("Foreign Volunteer Attachment", "factions"),
    ("Roster Building: 10-20 Figures", "rules"),
    ("Morale, Reputation, And Off-Table Russia", "rules"),
    ("Terrain: Grozny Blocks", "terrain"),
    ("Terrain: Villages And Cordon Lines", "terrain"),
    ("Terrain: Mountains And Roads", "terrain"),
    ("Scenario Structure And Ethics", "scenario"),
    ("Scenario 1: Dolinskoye Road", "scenario"),
    ("Scenario 2: Grozny Rail Station", "scenario"),
    ("Scenario 3: Palace Withdrawal", "scenario"),
    ("Scenario 4: Shali Aftermath", "scenario"),
    ("Scenario 5: Village Cordon", "scenario"),
    ("Scenario 6: Bamut Bunker Probe", "scenario"),
    ("Scenario 7: Gudermes Cache Raid", "scenario"),
    ("Scenario 8: Pervomayskoye Breakout", "scenario"),
    ("Scenario 9: Shatoy Road Bend", "scenario"),
    ("Scenario 10: August Grozny Infiltration", "scenario"),
    ("Campaign Links", "campaign"),
    ("Caches, Bribes, Prisoners, And Couriers", "campaign"),
    ("Islam, Community, And Morale In Fast Play", "campaign"),
    ("Organized Crime In Fast Play", "campaign"),
    ("Reference Book Cross-Links", "rules"),
    ("Optional Edge: RPK/RPK-74", "edge"),
    ("Optional Edge: PK/PKM Warning", "edge"),
    ("Optional Edge: Off-Table Federal Pressure", "edge"),
    ("Ten Scenario Quick Reference", "quick"),
    ("Weapon Quick Reference", "quick"),
    ("Roster Quick Reference", "quick"),
    ("Terrain Quick Reference", "quick"),
    ("Sources And Historical Boundaries", "ethics"),
    ("Back Cover: Use The Reference Book", "cover"),
]


def words(text: str) -> int:
    return len(text.split())


def find_by_name(collection: list[dict], name: str) -> dict | None:
    for item in collection:
        if item.get("name") == name:
            return item
    return None


def lookup(kind: str) -> dict | None:
    if ":" not in kind:
        return None
    label, name = kind.split(":", 1)
    collections = {
        "leader": research_data.LEADERS,
        "battle": research_data.BATTLES,
        "weapon": research_data.WEAPONS,
        "faction": research_data.FACTIONS,
    }
    return find_by_name(collections.get(label, []), name)


def image_for_page(page_number: int) -> tuple[int, str] | None:
    if page_number in IMAGE_PAGES:
        slot = IMAGE_PAGES.index(page_number) + 1
        return slot, IMAGE_SUBJECTS[slot - 1]
    return None


def history_title(title: str) -> str:
    replacements = {
        "Weapon Reference Overview And Gold Mapping": "Small Arms Reference Overview",
        "Gold Rules Crosswalk": "Historical Small-Arms Crosswalk",
        "Weapon Quick Table": "Small-Arms Quick Table",
        "Leader Quick Table": "Leader Quick Table",
        "Battle Quick Table": "Battle Quick Table",
        "Image Index And Render Instructions": "Illustration Index",
        "Rulebook Cross-References": "Further Reading Pathways",
        "RPGs: Historically Central, Rules-Excluded": "RPGs: Historically Central, Outside The Small-Arms Focus",
        "Vehicles And Heavy Weapons As Off-Table Pressure": "Vehicles And Heavy Weapons In Federal Operations",
        "Order Of Battle As Abstraction": "Order Of Battle And Organizational Limits",
        "Map Notes For Non-Cartographic Layout": "Map Notes And Terrain Interpretation",
        "Samashki: Atrocity History And Non-Game Boundaries": "Samashki: Atrocity History And Source Boundaries",
        "Cover: Field of Chaos Chechnya Gold Reference": "Cover: Field of Chaos Chechnya Historical Reference",
        "Scenario Ethics And Historical Boundaries": "Ethics Of Reading Atrocity History",
        "Scenario Reference": "Historical Case Study",
        "Civilian Harm Best Practices For Scenarios": "Civilian Harm And Historical Method",
        "SVD And Sniper Rifle Mapping": "SVD Dragunov And Marksman Rifles",
        "Grozny Terrain For 28mm Tables": "Grozny Urban Terrain",
        "Miniature Sourcing And Plastic Conversion Notes": "Material Culture And Uniform Notes",
        "28mm Figure Style And Miniature Range Notes": "Clothing, Equipment, And Appearance Notes",
        "Playable Sides: Why The Players Are Local": "Local Factions And Intra-Chechen Conflict",
        "Roster Archetypes": "Armed Group Archetypes",
    }
    clean = title
    for old, new in replacements.items():
        clean = clean.replace(old, new)
    return clean


def reference_page(page_number: int, title: str, kind: str) -> str:
    title = history_title(title)
    item = lookup(kind)
    image = image_for_page(page_number)
    image_text = ""
    if image:
        slot, subject = image
        image_text = (
            f"\n\nIllustration slot {slot:02d}: {subject}. This illustration is selected for historical orientation, material culture, terrain, or biographical context."
        )

    if item and kind.startswith("leader:"):
        facts = " ".join(item["facts"])
        facts = facts.replace(
            "Should be treated as a funding and patronage figure rather than a normal tabletop commander.",
            "He is best understood as a funding and patronage figure rather than a conventional battlefield commander.",
        )
        facts = facts.replace(
            "His role anchors the reference book's treatment of federal command failure, not a player-facing commander option.",
            "His role anchors the reference book's treatment of federal command failure and early-war overconfidence.",
        )
        base = f"{item['name']} is treated here as {item['role']} in the context of {item['side']}. {facts}"
    elif item and kind.startswith("battle:"):
        base = (
            f"{item['name']} is handled as a historical {item['phase']} case. "
            f"{item['summary']} Physical setting: {item['terrain']}."
        )
    elif item and kind.startswith("weapon:"):
        note = HISTORICAL_WEAPON_NOTES.get(item["name"], "This weapon belongs to the conflict's material history and is best understood through supply, capture, training, and user context.")
        base = (
            f"{item['name']} appears here as a historical small-arms subject. Typical users: {item['users']}. "
            f"{note}"
        )
    elif item and kind.startswith("faction:"):
        note = HISTORICAL_FACTION_NOTES.get(item["name"], item["summary"])
        base = f"{item['name']} appears here as a historical armed-group subject. {note}"
    elif kind == "crime":
        base = "This page draws from the organized-crime research cards: Moscow Obshina, racketeering, arms trafficking, oil theft, kidnapping, laundering, corrupt officers, and diaspora channels all belong in the war economy."
    elif kind == "islam":
        base = "This page draws from the Islam research cards: Chechen Sufi practice, village faith, jihad as local defense, foreign Salafi influence, clerical authority, propaganda, and ethical representation remain separate subjects rather than one collapsed explanation."
    elif kind == "russian":
        base = "This page draws from Russian-side research: federal political aims, Army columns, MVD and OMON, firepower, conscript morale, media pressure, logistics, and negotiation all shaped the conflict."
    elif kind == "society":
        base = "This page draws from Chechen society research: deportation memory, teips, local loyalties, state collapse, village self-defense, warlordism, displacement, and non-Chechen civilian vulnerability shaped what a small fighter group meant."
    elif kind == "ethics":
        base = "This page deals with civilian harm, atrocity history, hostage events, human rights sources, and the principle that suffering belongs in historical context rather than entertainment spectacle."
    elif kind == "terrain":
        base = "This page describes physical settings: apartment blocks, basements, village walls, mosque courtyards, bunker mouths, mountain roads, ravines, checkpoints, caches, and damaged civilian infrastructure."
    elif kind == "figures":
        base = "This page describes appearance, clothing, and material culture: mixed civilian clothes, Soviet gear, AK-pattern weapons, local police styling, foreign-volunteer cues, and the visual record of armed groups."
    else:
        base = "This page is a source-method and cross-reference page. It connects the historical corpus to the reference book without inventing unsourced material."

    body = dedent(
        f"""
        Page {page_number}: {title}

        {base}

        Historical frame. The First Chechen War was a post-Soviet war with older roots in imperial conquest, Soviet nationalities policy, the 1944 deportation, return from exile, and the collapse of the Soviet state. The open war began in December 1994 after Moscow's attempts to control or replace Dudayev's government through opposition channels failed. It ended after the August 1996 collapse of federal control in Grozny and the Khasavyurt process. Between those dates the conflict passed through armored disaster, urban ruin, mountain resistance, raids beyond Chechnya, hostage crises, village sweeps, bunker warfare, road ambushes, assassination, negotiation, and a devastated civilian landscape.

        Chechen-side history. The Chechen side was never a single block. Ichkerian government forces, village fighters, ex-Soviet officers, field commanders, religious authorities, criminalized patrons, foreign volunteers, pro-Moscow Chechens, and displaced civilians all appear in the source base. Their motives included independence, family survival, revenge, local defense, command loyalty, religious language, profit, political rivalry, and fear of federal power. The strands remain distinct enough that one does not erase the others.

        Russian-side history. Federal policy and military practice shaped every phase of the war. The federal side included presidential politics, the Ministry of Defense, Army units, airborne troops, armor, artillery, aviation, MVD Internal Troops, OMON, SOBR, FSB, conscripts, professional officers, negotiators, journalists, and corrupt logistics channels. Russian firepower could destroy neighborhoods and villages, but the state struggled to convert violence into durable legitimacy or stable control.

        Material and social history. Weapons, clothing, roads, buildings, money, documents, vehicles, hospitals, mosques, cemeteries, basements, markets, and checkpoints all matter because they show how the war was lived. Common Soviet-pattern arms circulated through depots, captured stocks, police leakage, battlefield pickup, bribery, black markets, organized crime, diaspora money, and foreign support. The same rifle could appear in the hands of a separatist, a pro-Moscow policeman, a criminal guard, a federal soldier, or a village defender; context gives it meaning.

        Ethical frame. Civilian suffering and atrocity evidence belong in sober historical context, not spectacle. Samashki, Shali, Grozny, Budyonnovsk, Pervomayskoye, and other cases require careful prose, clear sourcing, and restrained language. Illustrations emphasize people, places, material culture, and historical relationships while avoiding gore, hostage spectacle, fake hero worship, and anachronistic modern styling. Khattab appears with the correct damaged right hand where visible, and the rabbit anecdote remains separate from bin Laden because the supported source trail makes it a Khadr-family anecdote.{image_text}
        """
    ).strip()
    return body


def rule_page(page_number: int, title: str, kind: str) -> str:
    gold_table = ""
    if kind in {"gold", "weapons", "quick"}:
        gold_table = (
            "\n\nGold weapon facts to preserve: Sniper Rifle 24/36/48 inches, Very Slow, one shot, no fire under 12 inches, called head shot allowed. "
            "Rifle 18/27/36 inches, Slow, one shot or two with Firearm Advanced. Carbine 12/18/24 inches, Standard, one shot or two with Firearm Advanced. "
            "Automatic 8/12/16 inches, Standard, two shots, jams on 1 on 2d6, no head shot. SubMG 6/9/12 inches, Fast, three shots, jams on 1 on 1d6, no head shot. "
            "Shotgun uses the 15 inch cone and Firearm Use Basic. Grenade range is 12 inches, 2d6 reliability, dud on 4 or less, and uses open or building blast bands."
        )
    scenario_note = ""
    if kind == "scenario":
        scenario_note = (
            "\n\nScenario format: forces, terrain, setup, objectives, off-table federal pressure, historical note, and refusal line. "
            "The refusal line states what the scenario does not play: no heavy vehicles, no player artillery, no playable massacre, no hostage exploitation, and no Russian regular roster unless an optional referee module later exists."
        )
    body = dedent(
        f"""
        Page {page_number}: {title}

        This page belongs to the 48-page fast rulebook. It must be playable at the table without forcing the reader through the full 120-page reference book, but it should never pretend that the short rules are the whole history. The default game is 10-20 miniatures per side in 28mm, with two human players controlling local forces. Russian regulars, artillery, aircraft, armor, and heavy weapons are historically explained in Book 2 and appear here as off-table pressure.

        The playable factions are narrow by design. One side is usually an Ichkerian/local Chechen fighter group. The other is usually pro-Moscow Chechen opposition, local police, a militia, a criminalized guard force, or a rival local faction. A small foreign-volunteer attachment may appear where the scenario calls for it, but it should not replace the Chechen center of gravity. This keeps the game inside the user's remit while still acknowledging the Russian side in every scenario.

        Weapons use the Gold names, not new Chechnya-only categories. Most figures carry Automatics or Rifles. Carbines and SubMGs mark compact police, courier, bodyguard, or close-building figures. One Sniper Rifle at most is enough for most scenarios. Shotguns give rural and criminalized groups texture. Grenades are powerful and should be limited by scenario supply. RPK/RPK-74 and PK/PKM are edge cases discussed cautiously; RPGs and heavy weapons are excluded from normal play.{gold_table}

        Terrain should do more work than special rules. Grozny needs rubble, basements, upper floors, blocked avenues, stairwells, shell holes, burned vehicles as scenery, and broken sight lines. Villages need walls, courtyards, garden plots, mosque or cemetery edges, road cordons, and civilian movement routes. Mountain tables need road bends, ravines, boulder cover, wooded slopes, culverts, and hidden exit tracks. Every table should create movement decisions, not just shooting lanes.

        Victory conditions should avoid body-count thinking. Better objectives are moving a courier, recovering a cache, crossing a road, carrying a wounded fighter, delaying a sweep, identifying an informant, withdrawing before federal arrival, holding a stairwell long enough to extract documents, or opening a route for civilians. The player should feel the pressure of the war's larger systems without being asked to optimize atrocity or control heavy federal firepower.{scenario_note}

        Cross-reference. When a player wants more history, send them to Book 2. The reference book explains the leaders, battles, weapons, organized crime, Islam, Russian command, Chechen society, atrocities, and source cautions in depth. The rulebook stays compact, firm, and playable.
        """
    ).strip()
    return body


def build_reference_plan() -> str:
    lines = ["# Reference Page Plan", "", "Book 2 target: 120 pages total, page 1 cover included, 50 image slots included.", ""]
    for i, (title, kind) in enumerate(BOOK2_PAGES, start=1):
        title = history_title(title)
        image = image_for_page(i)
        img = f" Image {image[0]:02d}: {image[1]}." if image else ""
        lines.append(f"{i}. {title} - `{kind}`.{img}")
    return "\n".join(lines) + "\n"


def build_book2() -> str:
    pages = []
    for i, (title, kind) in enumerate(BOOK2_PAGES, start=1):
        pages.append(reference_page(i, title, kind))
    text = "\n\n\f\n\n".join(pages)
    return text + "\n"


def build_book1() -> str:
    pages = []
    for i, (title, kind) in enumerate(BOOK1_PAGES, start=1):
        pages.append(rule_page(i, title, kind))
    return "\n\n\f\n\n".join(pages) + "\n"


def build_image_statements() -> str:
    lines = [
        "# Image Statements - Render Last",
        "",
        "These are text-only statements for 50 new PNGs in the 120-page history reference book. All images must be no larger than 2048 by 2048; the project graphite pipeline uses 1024 by 1024. All earlier PNGs are superseded.",
        "",
    ]
    for idx, subject in enumerate(IMAGE_SUBJECTS, start=1):
        page = IMAGE_PAGES[idx - 1]
        lines.append(f"## Image {idx:02d} - Page {page}: {subject}")
        lines.append("")
        lines.append(
            "Graphite-rendered historical reference art. Period: First Chechen War, 1994-1996. Dense black-and-white hand-drawn graphite line art, heavy pencil cross-hatching, paper grain, tonal graphite shading, and rich scene-specific micro-detail. Keep the scene grounded and historically restrained. Do not include captions, readable text, UI, logos, watermarks, cartoon simplification, gore, or hostage spectacle. If Al Khattab appears, use the RFE/RL user-supplied reference direction and source-photo likeness traits: African-influenced Afro-Arab/Saudi facial structure, rounder full face, heavy brows, large dark eyes, very broad flat nose with low bridge, broad base, rounded tip, and wide nostrils, full lips, compact mouth, shaped mustache line, thick black beard, and dark hair around the sides where visible. Do not westernize his face; avoid narrow bridge, pointed nose, sharp European nose, thin lips, or western proportions. His right hand must be outside the crop or a short stump covered in a sock-like cloth mitten or sleeve, not a bare stump and not a full hand. The rabbit image must show the sourced Abdulkareem Khadr anecdote only and must not involve Osama bin Laden."
        )
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    assert len(BOOK2_PAGES) == 120, len(BOOK2_PAGES)
    assert len(BOOK1_PAGES) == 48, len(BOOK1_PAGES)
    assert len(IMAGE_SUBJECTS) == 50, len(IMAGE_SUBJECTS)
    assert len(IMAGE_PAGES) == 50, len(IMAGE_PAGES)

    plan = build_reference_plan()
    book2 = build_book2()
    book1 = build_book1()
    images = build_image_statements()

    REFERENCE_PLAN.write_text(plan, encoding="utf-8")
    BOOK2.write_text(book2, encoding="utf-8")
    BOOK1.write_text(book1, encoding="utf-8")
    IMAGES.write_text(images, encoding="utf-8")

    print(f"Wrote {REFERENCE_PLAN} ({words(plan):,} words)")
    print(f"Wrote {BOOK2} ({words(book2):,} words)")
    print(f"Wrote {BOOK1} ({words(book1):,} words)")
    print(f"Wrote {IMAGES} ({words(images):,} words)")


if __name__ == "__main__":
    main()
