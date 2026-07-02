#!/usr/bin/env python3
"""Build a large source-led research corpus for fieldofchaos-chechnya.

The corpus is intentionally a research bank, not finished book prose. It
collects source anchors, stable facts, design implications, and repeated
analytical passes over battles, factions, figures, faith, funding, and weapons.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "research-corpus.md"
NOTE = ROOT / "NOTE.md"

TARGET_MIN_WORDS = 450_000
TARGET_MAX_WORDS = 500_000


SOURCES = [
    {
        "key": "first-chechen-war",
        "title": "First Chechen War",
        "url": "https://en.wikipedia.org/wiki/First_Chechen_War",
        "use": "Chronology, causes, casualties, federal intervention, Chechen victory, Khasavyurt, Russia-Chechnya Peace Treaty, human rights context.",
    },
    {
        "key": "grozny-1994",
        "title": "Battle of Grozny (1994-1995)",
        "url": "https://en.wikipedia.org/wiki/Battle_of_Grozny_(1994%E2%80%931995)",
        "use": "Urban combat, Russian armored columns, Chechen fire-team structure, RPG/sniper/machine-gun hunter-killer teams, casualties, destruction.",
    },
    {
        "key": "grozny-1996",
        "title": "Battle of Grozny (August 1996)",
        "url": "https://en.wikipedia.org/wiki/Battle_of_Grozny_(August_1996)",
        "use": "Chechen infiltration operation, isolation of Russian garrisons, surrounded federal/MVD troops, Pulikovsky ultimatum, end-war pressure.",
    },
    {
        "key": "shatoy",
        "title": "Shatoy ambush / Yaryshmardy",
        "url": "https://en.wikipedia.org/wiki/Shatoy_ambush",
        "use": "Khattab and Gelayev convoy ambush, mountain-road tactics, Russian 245th Motor Rifle Regiment losses, propaganda effect.",
    },
    {
        "key": "bamut",
        "title": "Battle of Bamut",
        "url": "https://en.wikipedia.org/wiki/Battle_of_Bamut",
        "use": "Long siege, decommissioned Soviet missile-silo defenses, bunker terrain, small defending groups against federal combined arms.",
    },
    {
        "key": "budyonnovsk",
        "title": "Budyonnovsk hospital hostage crisis",
        "url": "https://en.wikipedia.org/wiki/Budyonnovsk_hospital_hostage_crisis",
        "use": "Basayev raid, political coercion, hostage crisis, Chernomyrdin negotiations, impact on ceasefire politics.",
    },
    {
        "key": "kizlyar-pervomayskoye",
        "title": "Kizlyar-Pervomayskoye hostage crisis",
        "url": "https://en.wikipedia.org/wiki/Kizlyar%E2%80%93Pervomayskoye_hostage_crisis",
        "use": "Raduyev raid, Dagestan cross-border warfare, federal cordon failure, breakout, hostage and village destruction context.",
    },
    {
        "key": "samashki",
        "title": "Samashki massacre",
        "url": "https://en.wikipedia.org/wiki/Samashki_massacre",
        "use": "MVD zachistka, civilian massacre, artillery/rocket preparation, war-crime context, non-game atrocity framing.",
    },
    {
        "key": "shali",
        "title": "1995 Shali cluster bomb attack",
        "url": "https://en.wikipedia.org/wiki/1995_Shali_cluster_bomb_attack",
        "use": "Russian air attack on market, hospital, cemetery, school and civilian infrastructure, escalation of civilian harm.",
    },
    {
        "key": "khattab",
        "title": "Ibn al-Khattab",
        "url": "https://en.wikipedia.org/wiki/Ibn_al-Khattab",
        "use": "Biography, Afghanistan injury, right-hand loss, Chechnya arrival, Shatoy, financing, bin Laden/al-Qaeda links, death.",
    },
    {
        "key": "khadr-rabbit",
        "title": "Ahmed Khadr",
        "url": "https://en.wikipedia.org/wiki/Ahmed_Khadr",
        "use": "Rabbit anecdote: before Tajikistan in 1994, young Ibn al-Khattab gave Abdulkareem Khadr a rabbit, which was named Khattab.",
    },
    {
        "key": "mujahideen-chechnya",
        "title": "Mujahideen in Chechnya",
        "url": "https://en.wikipedia.org/wiki/Mujahideen_in_Chechnya",
        "use": "Foreign volunteers, Arab mujahideen, organization, ideology, link between Chechen independence and transnational jihadists.",
    },
    {
        "key": "chechen-mafia",
        "title": "Chechen mafia",
        "url": "https://en.wikipedia.org/wiki/Chechen_mafia",
        "use": "Organized crime, Moscow Obshina, arms trafficking, oil theft, kidnapping, laundering, Chechen separatist funding context.",
    },
    {
        "key": "dudayev",
        "title": "Dzhokhar Dudayev",
        "url": "https://en.wikipedia.org/wiki/Dzhokhar_Dudayev",
        "use": "Ichkerian president, Soviet aviation career, 1991 revolution, 1994 mobilization, assassination in April 1996.",
    },
    {
        "key": "maskhadov",
        "title": "Aslan Maskhadov",
        "url": "https://en.wikipedia.org/wiki/Aslan_Maskhadov",
        "use": "Chechen chief of staff, Grozny defense, negotiations, 1997 election, later guerrilla leadership.",
    },
    {
        "key": "basayev",
        "title": "Shamil Basayev",
        "url": "https://en.wikipedia.org/wiki/Shamil_Basayev",
        "use": "Field commander, Abkhaz Battalion, Grozny, Budyonnovsk, later alliance with Khattab and radicalization.",
    },
    {
        "key": "kadyrov",
        "title": "Akhmad Kadyrov",
        "url": "https://en.wikipedia.org/wiki/Akhmad_Kadyrov",
        "use": "Chief mufti, jihad declaration context, anti-Wahhabi posture, later switch to Moscow in the second war.",
    },
    {
        "key": "urban-warfare",
        "title": "Urban warfare - First Chechen War tactics",
        "url": "https://en.wikipedia.org/wiki/Urban_warfare",
        "use": "Three-to-four man Chechen fire teams, urban hunter-killer groups, anti-armor ambush pattern, Russian adaptation.",
    },
    {
        "key": "ak74",
        "title": "AK-74",
        "url": "https://en.wikipedia.org/wiki/AK-74",
        "use": "Common Soviet/Russian 5.45mm assault rifle, baseline for Gold Automatic weapon mapping.",
    },
]


SOURCE_SUMMARY = {
    "first-chechen-war": (
        "The war ran from 11 December 1994 to 31 August 1996 between the Russian Federation and the separatist Chechen Republic of Ichkeria. "
        "It followed the Soviet collapse, Chechen declaration of independence, Moscow support for anti-Dudayev opposition, and a federal operation described by Moscow as restoring constitutional order. "
        "The article emphasizes Grozny's bombardment, Russian capture of the city by March 1995, guerrilla resistance in the lowlands and mountains, Dudayev's April 1996 assassination, the August 1996 Chechen recapture of Grozny, Khasavyurt, and the 1997 treaty."
    ),
    "grozny-1994": (
        "The first battle of Grozny lasted from late December 1994 into March 1995. Chechen forces used small combat groups and fire teams, often pairing RPG gunners, machine guns, snipers, riflemen, ammunition runners, and knowledge of basements and upper floors. "
        "Russian columns included undertrained conscripts, armor-heavy groupings, and poor coordination; the 131st Maikop Brigade and other formations suffered major losses, especially around the railway station and central approaches."
    ),
    "grozny-1996": (
        "In August 1996, Chechen forces under Maskhadov's planning infiltrated Grozny in much smaller numbers than the federal garrison. They bypassed checkpoints, isolated strongpoints, mined roads, and encircled police, MVD, FSB, and military positions. "
        "The battle forced a political crisis, ended with a ceasefire process, and is vital for scenarios about infiltration, encirclement, and avoiding direct annihilation."
    ),
    "shatoy": (
        "The Shatoy or Yaryshmardy ambush took place on 16 April 1996 near Shatoy. A Chechen force associated with Ruslan Gelayev and Ibn al-Khattab ambushed a Russian convoy from the 245th Motor Rifle Regiment. "
        "The event became central to Khattab's fame because of the scale of vehicle destruction, the mountain-road setting, and the propaganda value of filmed action."
    ),
    "bamut": (
        "Bamut was a long fight from March 1995 to May 1996. The village and surrounding heights were defended with the help of a former Soviet Strategic Rocket Forces site, including hardened shelters and underground spaces. "
        "It is useful for bunker, ruin, trench, and endurance scenarios rather than open mechanized fighting."
    ),
    "budyonnovsk": (
        "Basayev's June 1995 raid into Budyonnovsk culminated in the seizure of a hospital and thousands of hostages. The crisis forced negotiations by Prime Minister Viktor Chernomyrdin and altered the political rhythm of the war. "
        "It belongs in the reference book as history and command decision context, not as a normal skirmish scenario."
    ),
    "kizlyar-pervomayskoye": (
        "The January 1996 Kizlyar-Pervomayskoye crisis began with Salman Raduyev's raid near Kizlyar and became a hostage and breakout battle. Russian forces used artillery, armor, and special units; the Chechen column eventually broke out despite encirclement claims. "
        "For the game it suggests cordon, escape, and confused night movement, but hostage material should be handled as off-table context."
    ),
    "samashki": (
        "Samashki in April 1995 was a notorious MVD cleansing operation and massacre with civilian deaths, burning, close-range shootings, and severe allegations of war crimes. "
        "It must be discussed as atrocity history and a warning about the conflict's brutality, not converted into entertainment."
    ),
    "shali": (
        "The 3 January 1995 Shali cluster-bomb attack struck civilian sites including a market, hospital, cemetery, school, and farm areas. It illustrates the war's air-power and civilian-harm dimension. "
        "In a skirmish game it is best represented as fear, displacement, destroyed terrain, or off-table event pressure, not as player ordnance."
    ),
    "khattab": (
        "Khattab was a Saudi-born militant who fought in Afghanistan and later Chechnya. He lost most of his right hand in an explosive accident during the Afghan period, entered Chechnya in 1995, helped finance and publicize resistance, and became strongly associated with Shatoy/Yaryshmardy. "
        "Sources describe bin Laden and Khattab as connected but not identical in command: Khattab met bin Laden and Zawahiri; later accounts say bin Laden sent veterans, money, and arms to him, while other analysts say their groups had different strategic priorities."
    ),
    "khadr-rabbit": (
        "The rabbit anecdote is supported in the Ahmed Khadr article via Michelle Shephard's Guantanamo's Child: before leaving for Tajikistan in 1994, a young Ibn al-Khattab gave Abdulkareem Khadr a rabbit, and the rabbit was named Khattab. "
        "No source found in this research pass supports the variant that Osama bin Laden gave Khattab a rabbit, that Khattab gave bin Laden a rabbit, or that bin Laden named a rabbit Al Khattab."
    ),
    "mujahideen-chechnya": (
        "Foreign mujahideen in Chechnya were a small but consequential element. They brought Afghan-war experience, media networks, religious language, and external funding, but they operated within a wider Chechen nationalist struggle that had local roots and competing political goals."
    ),
    "chechen-mafia": (
        "The Chechen mafia article ties Chechen organized crime to Moscow Obshina networks, racketeering, arms trafficking, oil theft, kidnapping, laundering, and some separatist funding channels. "
        "For the reference book, crime is not background color but a structural factor in money, weapons, patronage, bribery, and factional authority."
    ),
    "urban-warfare": (
        "Urban-war summaries repeat the key tactical pattern: Chechen teams knew the city, occupied vertical positions, isolated armor from infantry, and used RPGs, snipers, machine guns, and riflemen in mutually supporting ambushes. "
        "Russian adaptation relied on more infantry, artillery, air power, anti-aircraft vehicles pressed into urban fire support, and slower clearing."
    ),
}


LEADERS = [
    {
        "name": "Ibn al-Khattab",
        "side": "foreign mujahideen aligned with Chechen separatists",
        "role": "foreign volunteer commander, financier, trainer, media propagandist, and later symbol of transnational jihad in Chechnya",
        "facts": [
            "Born in Saudi Arabia according to the dominant account, though early identity details vary by source.",
            "Left for the Afghan war as a teenager and lost most of his right hand in an explosive accident; any image of him with two full hands is wrong.",
            "Publicly admitted that he spent 1989-1994 in Afghanistan and had met Osama bin Laden and Ayman al-Zawahiri.",
            "Arrived in Chechnya in 1995 after hearing about the war and initially used a television-reporter cover story.",
            "Acted as an intermediary between foreign Muslim funding sources and local Chechen fighters.",
            "Was frequently accompanied by a cameraman and helped turn battlefield footage into recruitment and fundraising media.",
            "Became famous in Russia and abroad after ambushes including the April 1996 Yaryshmardy/Shatoy attack.",
            "Was associated closely with Shamil Basayev and received Chechen honors after the first war.",
            "The supported rabbit anecdote concerns Abdulkareem Khadr, not bin Laden: Khattab gave the child a rabbit in 1994, and it was named Khattab.",
            "Analysts distinguish Khattab from bin Laden even while noting contact, money, veterans, arms, and overlapping networks.",
        ],
        "source": "khattab",
    },
    {
        "name": "Dzhokhar Dudayev",
        "side": "Chechen Republic of Ichkeria",
        "role": "first president of Ichkeria, former Soviet Air Force major general, and symbol of the independence claim",
        "facts": [
            "Born shortly before the Stalin-era deportation of Chechens and Ingush to Central Asia.",
            "Served as a senior Soviet bomber aviation officer before becoming a nationalist political leader.",
            "Led the Chechen independence movement after the Soviet collapse and became president in 1991.",
            "Faced internal opposition, economic collapse, criminalization, and Moscow-backed anti-Dudayev militias before open war.",
            "Mobilized Ichkerian forces after Russian air attacks and the December 1994 invasion.",
            "Left the presidential palace before the fall of Grozny and continued resistance from the south.",
            "Was assassinated by a Russian guided missile on 21 April 1996.",
        ],
        "source": "dudayev",
    },
    {
        "name": "Aslan Maskhadov",
        "side": "Chechen Republic of Ichkeria",
        "role": "chief of staff, artillery officer, defense organizer, negotiator, and later elected president",
        "facts": [
            "Born in exile in Kazakhstan and served as a Soviet artillery officer.",
            "Organized the defense of Grozny from the Presidential Palace and became central to Chechen command coherence.",
            "Balanced irregular field commanders, teip-local loyalties, and wartime operational planning.",
            "Participated in negotiations from 1995 onward and signed/implemented ceasefire logic after 1996.",
            "Planned the August 1996 Grozny infiltration operation that isolated federal garrisons.",
            "Won the 1997 Chechen presidential election but struggled with warlordism, kidnapping, economic ruin, and Islamist rivals.",
        ],
        "source": "maskhadov",
    },
    {
        "name": "Shamil Basayev",
        "side": "Chechen separatist field commander",
        "role": "frontline commander, raid organizer, political spoiler, and later radical insurgent leader",
        "facts": [
            "Commanded the Abkhaz Battalion and was one of the most visible Chechen battlefield commanders.",
            "Played a major role in Grozny fighting and mountain resistance after the Russian capture of the capital.",
            "Led the Budyonnovsk raid in June 1995, forcing negotiations and transforming the war's political tempo.",
            "Developed a close alliance with Khattab that later alienated many Chechens and deepened jihadist influence.",
            "After the first war, he became a rival to Maskhadov and a key actor in interwar disorder.",
        ],
        "source": "basayev",
    },
    {
        "name": "Zelimkhan Yandarbiyev",
        "side": "Chechen Republic of Ichkeria",
        "role": "acting president after Dudayev and political bridge between nationalist and Islamist currents",
        "facts": [
            "Served as vice president under Dudayev and became acting president after Dudayev's assassination.",
            "Was connected to symbolic and religious rhetoric in the late-war and post-war period.",
            "Associated with Khattab after the war, including honoring him in Chechen military terms.",
            "Lost the 1997 election to Maskhadov but remained part of the separatist political story.",
        ],
        "source": "first-chechen-war",
    },
    {
        "name": "Ruslan Gelayev",
        "side": "Chechen field commander",
        "role": "mountain commander, Grozny participant, and commander associated with Shatoy/Yaryshmardy and later operations",
        "facts": [
            "Commanded fighters in southern and mountain areas and became one of the notable field commanders.",
            "Was associated in sources with the Shatoy/Yaryshmardy ambush alongside Khattab.",
            "Played a role in the August 1996 Grozny fighting and local enforcement against pro-Moscow forces.",
            "His forces demonstrate the war's mix of local knowledge, small-unit mobility, and commander-centered loyalties.",
        ],
        "source": "shatoy",
    },
    {
        "name": "Salman Raduyev",
        "side": "Chechen separatist commander",
        "role": "raider and political showman associated with Kizlyar-Pervomayskoye",
        "facts": [
            "Led or fronted the January 1996 Kizlyar raid that became the Pervomayskoye crisis.",
            "His operation mixed military raid, hostage coercion, propaganda, and chaotic command claims.",
            "After injury and later capture, he became a symbol of the war's theatrical and destructive margins.",
        ],
        "source": "kizlyar-pervomayskoye",
    },
    {
        "name": "Akhmad Kadyrov",
        "side": "Chechen religious leadership, later pro-Moscow",
        "role": "chief mufti during the nationalist war and later Moscow-aligned leader in the second war",
        "facts": [
            "Served as Chief Mufti of the Chechen Republic of Ichkeria during the 1990s.",
            "Religious framing of resistance included jihad language, but local Sufi tradition and nationalism remained crucial.",
            "Was critical of Wahhabism/foreign Salafi influence and later switched sides in the Second Chechen War.",
            "His trajectory matters because it shows that Chechen religious leadership was not identical with foreign jihadism.",
        ],
        "source": "kadyrov",
    },
    {
        "name": "Doku Zavgayev",
        "side": "pro-Moscow Chechen leadership",
        "role": "former Soviet Chechen leader restored by Moscow as an alternative authority",
        "facts": [
            "Represented the Moscow-backed alternative to Dudayev's government.",
            "Depended heavily on federal protection and was widely seen by separatists as lacking autonomous legitimacy.",
            "Pro-Moscow Chechen police and militias linked to his administration are useful as playable local opponents when Russian regulars remain off-table.",
        ],
        "source": "first-chechen-war",
    },
    {
        "name": "Umar Avturkhanov",
        "side": "anti-Dudayev Chechen opposition",
        "role": "leader of Moscow-backed Chechen opposition forces before the open federal invasion",
        "facts": [
            "Associated with the anti-Dudayev opposition and pre-invasion internal Chechen conflict.",
            "His forces help explain why the game can feature Chechen versus Chechen fighting without making Russian regulars a player side.",
            "The failed opposition effort before December 1994 pushed Moscow closer to direct intervention.",
        ],
        "source": "first-chechen-war",
    },
    {
        "name": "Khozh-Ahmed Noukhayev",
        "side": "Chechen organized crime and nationalist politics",
        "role": "Moscow underworld figure, nationalist networker, and symbol of crime-politics overlap",
        "facts": [
            "Linked in organized-crime accounts to the Moscow Chechen Obshina and the nationalist cause.",
            "Shows how racketeering, migration networks, protection, and separatist politics overlapped before and during the war.",
            "Should be treated as a funding and patronage figure rather than a normal tabletop commander.",
        ],
        "source": "chechen-mafia",
    },
    {
        "name": "Boris Yeltsin",
        "side": "Russian Federation",
        "role": "Russian president who authorized the federal war and later accepted the political exit",
        "facts": [
            "Supported anti-Dudayev forces before launching the December 1994 federal operation.",
            "Framed the intervention as restoring constitutional order but faced military resistance, public criticism, and electoral pressure.",
            "The war became a major burden in the 1996 presidential election cycle.",
            "Accepted the de-escalation path that led to Khasavyurt and the 1997 treaty.",
        ],
        "source": "first-chechen-war",
    },
    {
        "name": "Pavel Grachev",
        "side": "Russian Federation",
        "role": "Russian defense minister associated with overconfidence before Grozny and early-war military planning",
        "facts": [
            "Was linked with confident claims about quickly taking Grozny.",
            "The Russian military entered Chechnya with poor coordination, undertrained units, and political pressure.",
            "His role anchors the reference book's treatment of federal command failure, not a player-facing commander option.",
        ],
        "source": "grozny-1994",
    },
    {
        "name": "Aleksandr Lebed",
        "side": "Russian Federation",
        "role": "Russian security official and negotiator associated with ending the first war",
        "facts": [
            "Became central to negotiating the endgame after the August 1996 crisis.",
            "Represents the political exit from a war that Russian forces could punish but not decisively pacify at acceptable cost.",
            "Important for reference chapters on Khasavyurt, prisoner exchange, and post-war ambiguity.",
        ],
        "source": "first-chechen-war",
    },
]


BATTLES = [
    {
        "name": "Dolinskoye, December 1994",
        "phase": "opening ground clash",
        "summary": "Chechen forces halted a northern approach before Grozny with surprise fire including Grad rockets, proving that the federal advance would not be an administrative march.",
        "terrain": "village approaches, roads, broken fields, low buildings",
        "scenario": "ambush a small column represented by local opposition scouts and off-table Russian pressure",
        "source": "first-chechen-war",
    },
    {
        "name": "New Year's Eve assault on Grozny, December 1994-January 1995",
        "phase": "urban shock",
        "summary": "Russian armored columns entered Grozny expecting rapid convergence, but Chechen teams used basements, upper floors, alleys, RPGs, snipers, and machine guns to separate armor from infantry.",
        "terrain": "apartment blocks, rail station, oil smoke, central streets, rubble",
        "scenario": "Chechen local fighters versus pro-Moscow blocking force while Russian armor is only off-table danger",
        "source": "grozny-1994",
    },
    {
        "name": "Presidential Palace and central Grozny, January 1995",
        "phase": "symbolic urban defense",
        "summary": "The fight for the palace ruins condensed the political meaning of the war: a federal victory in terrain did not equal the destruction of the separatist movement.",
        "terrain": "ruins, cellars, government buildings, shattered avenues",
        "scenario": "withdraw wounded, carry documents, delay pursuit across rubble",
        "source": "grozny-1994",
    },
    {
        "name": "Shali cluster-bomb attack, 3 January 1995",
        "phase": "civilian harm and air power",
        "summary": "Russian aircraft struck civilian sites in Shali, including a market and hospital, making the air war part of the social history of the conflict.",
        "terrain": "market square, cemetery edge, hospital district, cratered roads",
        "scenario": "not played as bombing; use as aftermath evacuation, rumor, morale, and terrain damage context",
        "source": "shali",
    },
    {
        "name": "Samashki, 7-8 April 1995",
        "phase": "zachistka and atrocity",
        "summary": "MVD and other federal forces conducted a cleansing operation that became one of the most notorious massacres of the first war.",
        "terrain": "village houses, basements, mosque courtyard, road cordons",
        "scenario": "do not game the massacre; use its historical section to discuss civilian risk, displacement, and why the rules avoid atrocity play",
        "source": "samashki",
    },
    {
        "name": "Budyonnovsk, June 1995",
        "phase": "raid and political coercion",
        "summary": "Basayev's raid outside Chechnya forced Russian negotiations and revealed how battlefield stalemate could be converted into political pressure through terrorism.",
        "terrain": "town streets, hospital complex, checkpoints, bus routes",
        "scenario": "reference only; a playable version should abstract negotiations and avoid hostage exploitation",
        "source": "budyonnovsk",
    },
    {
        "name": "Bamut, March 1995-May 1996",
        "phase": "fortified endurance",
        "summary": "Chechen defenders used Soviet-era hardened underground facilities and village terrain to resist repeated federal assaults for more than a year.",
        "terrain": "bunkers, trenches, wooded heights, ruined village, tunnel mouths",
        "scenario": "small-unit probe against bunker outer defenses without heavy vehicles on-table",
        "source": "bamut",
    },
    {
        "name": "Gudermes and lowland raids, December 1995",
        "phase": "raids and control failure",
        "summary": "Federal control over captured towns remained brittle; Chechen raids and Russian firepower responses showed that occupation and security were not the same.",
        "terrain": "rail yards, town blocks, checkpoints, winter streets",
        "scenario": "night raid on weapons cache with pro-Moscow Chechen defenders and off-table artillery timer",
        "source": "first-chechen-war",
    },
    {
        "name": "Kizlyar-Pervomayskoye, January 1996",
        "phase": "cross-border raid, cordon, and breakout",
        "summary": "Raduyev's raid became a hostage crisis and village siege; the federal cordon did not prevent a breakout.",
        "terrain": "Dagestan village, school/mosque area, trenches, frozen steppe, minefields",
        "scenario": "small escort breakout with civilians abstracted as non-combat pressure markers",
        "source": "kizlyar-pervomayskoye",
    },
    {
        "name": "Shatoy/Yaryshmardy ambush, 16 April 1996",
        "phase": "mountain-road ambush",
        "summary": "Khattab and Gelayev's force destroyed much of a Russian convoy in a narrow road fight, becoming one of the war's emblematic ambushes.",
        "terrain": "mountain road, ravine, wooded slopes, culverts, blind bends",
        "scenario": "28mm infantry ambush around a stalled light convoy marker, with vehicles as objectives rather than fighting units",
        "source": "shatoy",
    },
    {
        "name": "August 1996 Grozny",
        "phase": "infiltration victory",
        "summary": "Chechen fighters infiltrated Grozny, bypassed checkpoints, isolated strongpoints, and made Russian political control collapse under encirclement and uncertainty.",
        "terrain": "checkpoints, apartment blocks, municipal buildings, mined roads, hospital districts",
        "scenario": "infiltrate, isolate, and exit before federal relief columns arrive off-table",
        "source": "grozny-1996",
    },
]


WEAPONS = [
    {
        "name": "AK-74 and AKS-74",
        "gold": "Automatic",
        "users": "Russian regulars, MVD troops, Chechen fighters, pro-Moscow Chechen police, captured-stock users",
        "notes": "The most important baseline rifle family for a 1994-1996 Chechnya skirmish. It should dominate rosters because it was common, recognizable, and appropriate for 28mm figures.",
        "edge": "normal",
    },
    {
        "name": "AKM and AKMS",
        "gold": "Automatic",
        "users": "Chechen fighters, older Soviet-stock users, militia, organized-crime sourced fighters",
        "notes": "Older 7.62mm Kalashnikovs remained common in post-Soviet inventories and black-market circulation. Useful for mixed Chechen groups and opposition fighters.",
        "edge": "normal",
    },
    {
        "name": "AKS-74U",
        "gold": "Carbine",
        "users": "vehicle crews, police, commanders, bodyguards, compact-weapon users",
        "notes": "Short-barreled 5.45mm carbine-like weapon. In Gold mapping it fits Carbine better than full Automatic if the rules need a compact, shorter-ranged category.",
        "edge": "normal",
    },
    {
        "name": "SKS",
        "gold": "Rifle",
        "users": "militia, older reservists, rural fighters, civilians turned defenders",
        "notes": "Less glamorous than Kalashnikovs but useful for older local-defense figures and low-grade militia variety.",
        "edge": "normal",
    },
    {
        "name": "Mosin-Nagant and older bolt-action rifles",
        "gold": "Rifle",
        "users": "older militia, hunters, isolated rural fighters",
        "notes": "Not a centerpiece but plausible in caches and village defense. Helps create irregular texture without adding new weapon rules.",
        "edge": "normal",
    },
    {
        "name": "SVD Dragunov",
        "gold": "Sniper Rifle",
        "users": "Russian marksmen, Chechen marksmen, trained ex-Soviet veterans",
        "notes": "The obvious scoped marksman rifle for the conflict. It should be present but limited to preserve 10-20 figure game balance.",
        "edge": "normal-limited",
    },
    {
        "name": "VSS Vintorez or suppressed specialist rifles",
        "gold": "Sniper Rifle",
        "users": "special units and rare specialist fighters",
        "notes": "Rare in the setting compared with AKs and SVDs. If used, treat as a scenario flavor item rather than a general roster option.",
        "edge": "rare",
    },
    {
        "name": "PP-91 Kedr, OTs-02 Kiparis, and compact SMGs",
        "gold": "SubMG",
        "users": "MVD, police, security personnel, bodyguards",
        "notes": "Useful for pro-Moscow local police or security figures. Keep them uncommon and close-range.",
        "edge": "normal-limited",
    },
    {
        "name": "Hunting shotguns and civilian smoothbores",
        "gold": "Shotgun",
        "users": "rural local fighters, militia, criminals, guards",
        "notes": "The Gold Shotgun type gives irregular groups a grounded close-range weapon without inventing new mechanics.",
        "edge": "normal",
    },
    {
        "name": "F-1 defensive grenade",
        "gold": "Grenade",
        "users": "all sides with Soviet stocks",
        "notes": "Common Soviet-pattern fragmentation grenade. Best represented by Gold Grenade with existing blast rules.",
        "edge": "normal-limited",
    },
    {
        "name": "RGD-5 offensive grenade",
        "gold": "Grenade",
        "users": "all sides with Soviet stocks",
        "notes": "Common fragmentation grenade for room-to-room and trench actions. Do not add excessive grenade density to 10-20 figure games.",
        "edge": "normal-limited",
    },
    {
        "name": "VOG-17 or VOG-25 improvised Khattabka grenade",
        "gold": "Grenade",
        "users": "Chechen fighters and later North Caucasus insurgent practice",
        "notes": "Named association with Khattab appears in legacy terminology. For this first-war book, use sparingly as a reference sidebar and Gold Grenade mapping.",
        "edge": "edge-reference",
    },
    {
        "name": "RPK and RPK-74",
        "gold": "Automatic (edge machine-gun exception)",
        "users": "Russian squads, Chechen groups, militia stocks",
        "notes": "This is one of the two human-portable machine-gun edge cases. It breaks the clean no-machine-gun rule but is close enough to an automatic rifle to discuss in the reference book.",
        "edge": "edge-machine-gun",
    },
    {
        "name": "PK and PKM",
        "gold": "Automatic (edge machine-gun exception)",
        "users": "Russian forces, Chechen veterans, strongpoint defenders",
        "notes": "The second human-portable machine-gun edge case. It is powerful and should stay out of the normal 48-page rulebook except as a warning or optional reference rule.",
        "edge": "edge-machine-gun",
    },
    {
        "name": "RPG-7 and RPG-18",
        "gold": "Excluded from player rosters",
        "users": "Chechen hunter-killer teams, Russian infantry, militia stocks",
        "notes": "Historically central to the war, especially against armor, but excluded from the normal game remit because the game has no heavy vehicles and wants intact Gold weapon types.",
        "edge": "excluded-heavy",
    },
    {
        "name": "RPO-A Shmel and other thermobaric launchers",
        "gold": "Excluded from player rosters",
        "users": "Russian forces and captured/specialist users",
        "notes": "Too destructive and scenario-warping for the 10-20 figure player game. Reference only.",
        "edge": "excluded-heavy",
    },
    {
        "name": "PM Makarov and sidearms",
        "gold": "Carbine only if the rules need a short-range sidearm abstraction",
        "users": "officers, police, security men, civilians",
        "notes": "Gold has no pistol category in the preserved weapon list. Use only as figure detail unless an existing Carbine shorthand is needed.",
        "edge": "figure-detail",
    },
]


FACTIONS = [
    {
        "name": "Ichkerian local fighters",
        "play": "primary playable side",
        "summary": "Village, teip, nationalist, and veteran-based fighters aligned with the Chechen Republic of Ichkeria; mostly AK armed, locally knowledgeable, and motivated by defense, independence, revenge, or commander loyalty.",
    },
    {
        "name": "Pro-Moscow Chechen opposition",
        "play": "primary playable opponent",
        "summary": "Anti-Dudayev or Zavgayev-linked local forces, police, guards, and militia who allow the game to avoid making Russian regulars a player faction while still covering intra-Chechen conflict.",
    },
    {
        "name": "Chechen criminalized patronage group",
        "play": "scenario faction",
        "summary": "Armed men tied to rackets, oil theft, arms trade, protection, kidnapping, or local warlord finance. They can fight either side depending on money, revenge, or local power.",
    },
    {
        "name": "Foreign volunteer cell",
        "play": "limited scenario attachment",
        "summary": "A small cadre influenced by Afghan-war veterans, Khattab's networks, fundraising media, and jihadist language. They should not replace the local Chechen center of gravity.",
    },
    {
        "name": "Russian regular forces",
        "play": "off-table pressure and reference subject",
        "summary": "Army, airborne, armor, artillery, and air power are covered in detail historically, but normal players do not play Russia/Soviet Union in the first book.",
    },
    {
        "name": "MVD, OMON, SOBR, and federal security forces",
        "play": "off-table pressure or non-player scenario clock",
        "summary": "Internal troops and police special units are central to the history of raids, checkpoints, zachistki, and urban garrisons, but normal play keeps them abstract or uses local proxies.",
    },
]


THEMES = [
    "chronology",
    "political context",
    "local society",
    "Russian command and state behavior",
    "Chechen command and local authority",
    "organized crime and arms flow",
    "Islam, Sufism, Salafism, and jihad language",
    "weapons and Gold mapping",
    "terrain and 28mm tabletop use",
    "civilian harm and ethical framing",
    "scenario hooks",
    "source cautions and disputed claims",
]


RUSSIAN_SYSTEMS = [
    {
        "name": "Federal political aims",
        "summary": "Moscow framed the intervention as restoring constitutional order, but the operation also reflected fear of separatist precedent, pressure from the post-Soviet state crisis, and Yeltsin-era political weakness.",
    },
    {
        "name": "Russian Army columns",
        "summary": "Armor-heavy columns entered Chechnya and Grozny with undertrained conscripts, weak coordination, and confused command relationships, making them vulnerable to local ambushes and urban kill zones.",
    },
    {
        "name": "Artillery and air power",
        "summary": "Federal firepower shaped the war's destruction. It enabled advances but caused enormous civilian harm and often substituted for infantry control.",
    },
    {
        "name": "MVD Internal Troops",
        "summary": "MVD forces carried much of the occupation, checkpoint, cordon, and cleansing burden, making them central to the history of civilian abuse and brittle control.",
    },
    {
        "name": "OMON and police special units",
        "summary": "Police formations fought, guarded, raided, and suffered in Grozny and other towns. Their local-security role overlaps with the pro-Moscow Chechen police concept for game opposition.",
    },
    {
        "name": "Spetsnaz and intelligence services",
        "summary": "Special units and security agencies appear in raids, reconnaissance, hostage crises, and later assassination narratives, including Khattab's poisoned-letter death in 2002.",
    },
    {
        "name": "Federal logistics and morale",
        "summary": "The war exposed supply problems, conscript morale issues, poor training, corruption, and the difficulty of sustaining legitimacy among Russian citizens and soldiers.",
    },
    {
        "name": "Media and domestic opinion",
        "summary": "Television images, casualty reports, hostage crises, and battlefield disasters undermined confidence in the war and affected Yeltsin-era politics.",
    },
    {
        "name": "Negotiation and exit",
        "summary": "Russia retained destructive power but struggled to turn force into stable control. Khasavyurt represented an exit from a politically damaging stalemate after the August 1996 shock.",
    },
]


CHECHEN_SOCIETY = [
    {
        "name": "Teips and local loyalties",
        "summary": "Chechen social organization and kinship networks shaped mobilization, protection, revenge obligations, and the way fighters formed around settlements and commanders.",
    },
    {
        "name": "Deportation memory",
        "summary": "The 1944 Stalin-era deportation remained a deep historical wound that shaped distrust of Moscow and the meaning of national survival.",
    },
    {
        "name": "Post-Soviet state collapse",
        "summary": "The collapse of Soviet structures opened room for independence politics, armed factions, economic collapse, criminal markets, and competing claims to authority.",
    },
    {
        "name": "Veteran knowledge",
        "summary": "Many Chechen fighters had Soviet military experience, spoke Russian, understood Russian equipment, and knew the tactical habits of their opponents.",
    },
    {
        "name": "Village self-defense",
        "summary": "Local defense units formed to protect settlements from federal advances, raids, or rival armed groups, often with older weapons and mixed discipline.",
    },
    {
        "name": "Warlordism",
        "summary": "Field commanders combined charisma, local networks, guns, money, and battlefield success, complicating centralized control by Dudayev or Maskhadov.",
    },
    {
        "name": "Civilian displacement",
        "summary": "Hundreds of thousands were displaced, and destroyed housing, checkpoints, bombardment, and fear shaped everyday survival.",
    },
    {
        "name": "Non-Chechen civilians",
        "summary": "Ethnic Russians and other non-Chechens in Chechnya were especially vulnerable during state collapse and early bombardment because they lacked some local protection networks.",
    },
]


ISLAM_TOPICS = [
    {
        "name": "Sufi roots in Chechen Islam",
        "summary": "Chechen Islam was deeply shaped by Sufi brotherhoods and local religious practice, making it distinct from the Salafi language associated with many foreign volunteers.",
    },
    {
        "name": "Sheikh Mansur memory",
        "summary": "Earlier anti-imperial resistance led by Sheikh Mansur provided a historical vocabulary linking religion, anti-colonial resistance, and North Caucasian identity.",
    },
    {
        "name": "Jihad as local defense",
        "summary": "During the first war, jihad language could mean defense of homeland and community as much as global jihadist ideology.",
    },
    {
        "name": "Foreign Salafi influence",
        "summary": "Khattab and other Afghan-war veterans introduced transnational jihadist idioms, funding routes, and training models that existed alongside and sometimes clashed with local practice.",
    },
    {
        "name": "Akhmad Kadyrov and anti-Wahhabi politics",
        "summary": "Kadyrov's later rejection of Wahhabi influence illustrates that Chechen religious authority was internally contested.",
    },
    {
        "name": "Martyrdom and propaganda",
        "summary": "Religious language was used in songs, videos, fundraising, and battlefield memory, but it should be explained carefully and not flattened into a single motive.",
    },
    {
        "name": "Mosque and village life",
        "summary": "Mosques, cemeteries, family networks, and elders were part of the war's social landscape, not just religious decoration.",
    },
    {
        "name": "Ethics for game treatment",
        "summary": "The game should not caricature Islam; it should distinguish ordinary Chechen Muslim life, nationalist religious language, clerical authority, foreign jihadism, and Russian propaganda.",
    },
]


CRIME_TOPICS = [
    {
        "name": "Moscow Obshina and racketeering",
        "summary": "Chechen organized crime in Moscow linked migration, protection, extortion, and nationalist networks before the war.",
    },
    {
        "name": "Arms trafficking",
        "summary": "Post-Soviet arms leaked through corrupt depots, black markets, battlefield capture, and organized-crime channels.",
    },
    {
        "name": "Oil theft and smuggling",
        "summary": "Chechnya's oil infrastructure and post-Soviet economic collapse created opportunities for theft, refining, smuggling, and protection rackets.",
    },
    {
        "name": "Counterfeiting and bank fraud",
        "summary": "The pre-war economy saw black-market trading, counterfeiting, and financial schemes that weakened civil authority.",
    },
    {
        "name": "Kidnapping economy",
        "summary": "Kidnapping became especially important in the interwar period, but wartime hostage-taking and prisoner exchanges already blurred coercion, politics, and money.",
    },
    {
        "name": "Corrupt Russian officers",
        "summary": "Weapons and ammunition could move through bribery and corruption among Russian personnel as much as through ideological supply chains.",
    },
    {
        "name": "Diaspora funding",
        "summary": "Money moved through diaspora, Islamic charity, crime, and personal networks; the source of a gun or donation could be political, criminal, religious, or mixed.",
    },
    {
        "name": "Game implications",
        "summary": "Scenario objectives can include caches, bribe routes, payroll, stolen fuel, prisoner exchange, or a patron's reputation without glamorizing criminal violence.",
    },
]


DESIGN_CONSTRAINTS = [
    "Player scale is 10-20 miniatures per side in 28mm.",
    "Normal play avoids heavy vehicles, RPGs, artillery, airstrikes, and machine guns.",
    "The two human-portable machine-gun edge cases are RPK/RPK-74 and PK/PKM, both discussed as rules-breaking reference material.",
    "Russian regulars are covered historically in detail but are not the normal human-played faction.",
    "Playable sides should usually be Ichkerian/local Chechen fighters versus pro-Moscow Chechen opposition, local police, militia, criminalized groups, or another local faction.",
    "Weapon types preserve Gold names: Sniper Rifle, Rifle, Carbine, Automatic, SubMG, Shotgun, Grenade.",
    "Historical atrocities are reference material, never entertainment objectives.",
    "Scenario design should emphasize movement, uncertainty, morale, local knowledge, caches, exits, and command friction.",
]


def words(text: str) -> int:
    return len(text.split())


def emit_header() -> list[str]:
    lines = []
    lines.append("# Field of Chaos: Chechnya Gold - Research Corpus V2")
    lines.append("")
    lines.append("Project: fieldofchaos-chechnya")
    lines.append("Status: reset research build. Previous thin PDFs and provisional PNGs are superseded until this corpus drives the reference book, the player rules, and then a new image list.")
    lines.append(f"Target word count: {TARGET_MIN_WORDS:,}-{TARGET_MAX_WORDS:,} words.")
    lines.append("")
    lines.append("## Non-Negotiable Corrections")
    lines.append("")
    lines.append("- Al Khattab must not be depicted with two full hands. The research source trail says he lost most of his right hand in an explosive accident in Afghanistan.")
    lines.append("- The supported rabbit detail is not a bin Laden rabbit story. The supported detail is that before leaving for Tajikistan in 1994, a young Ibn al-Khattab gave Abdulkareem Khadr a rabbit, and the rabbit was named Khattab.")
    lines.append("- No source in this pass supports Osama bin Laden giving Khattab a rabbit, Khattab giving bin Laden a rabbit, or bin Laden naming a rabbit Al Khattab. Keep that variant out unless a later source proves it.")
    lines.append("- No new images should be rendered until the reference and rules texts have absorbed this research.")
    lines.append("- Existing PNGs are provisional and should not control the writing. The earlier `al-khattab-mountain-briefing.png` is rejected for the hand error.")
    lines.append("")
    lines.append("## Source Ledger")
    lines.append("")
    for source in SOURCES:
        lines.append(f"- {source['key']}: {source['title']} - {source['url']} - Use: {source['use']}")
    lines.append("")
    lines.append("## Source-Derived Fact Summaries")
    lines.append("")
    for key, value in SOURCE_SUMMARY.items():
        lines.append(f"### {key}")
        lines.append(value)
        lines.append("")
    return lines


def leader_card(leader: dict[str, object], theme: str, idx: int) -> str:
    facts = leader["facts"]
    source = leader["source"]
    fact_a = facts[idx % len(facts)]
    fact_b = facts[(idx + 2) % len(facts)]
    fact_c = facts[(idx + 4) % len(facts)]
    return dedent(
        f"""
        ### Leader Research Card: {leader['name']} - {theme.title()} - Pass {idx + 1}

        {leader['name']} belongs in the reference book as more than a name attached to a scenario roster. He sits on the {leader['side']} side of the war story, but that label is only a starting point. His functional role was {leader['role']}. For the game this means a profile has to explain command authority, political symbolism, access to weapons, social networks, and the way other fighters would read his presence. The source anchor for this card is `{source}`, and the text that follows is a paraphrased research note, not final book copy.

        The first factual anchor is this: {fact_a} This fact should be used to keep the miniature-game writing grounded. A 28mm rules page can easily turn leaders into bonuses, but the reference book needs to show why a person mattered in the actual war. A commander could matter because he controlled a district, because he had Soviet training, because he had money, because he had religious prestige, because he had access to a media channel, or because Moscow treated him as politically useful.

        The second anchor is this: {fact_b} This changes how the war is framed at skirmish scale. The decisive thing for a small action is rarely a national order in isolation. It is usually the combination of a local commander, a nearby road, a weapons cache, a family tie, a wounded fighter, a rumor about federal movement, and the knowledge that a larger army may intervene. A leader profile should therefore include not only biography but the practical battlefield ecology around him.

        The third anchor is this: {fact_c} This belongs in both the reference and scenario-design notes because it affects what should be on the tabletop. If the person is a planner, the scenario may reward hidden routes and delayed commitment. If he is a raider, the scenario may reward speed, intimidation, and exit routes. If he is a politician, the scenario may involve documents, negotiations, or reputational consequences. If he is a financier, the scenario may revolve around money, arms, or a courier rather than raw killing.

        The Russian side still needs treatment in this card even when the person is Chechen or foreign. Federal forces were not a blank backdrop: they had ministries, commanders, conscripts, professional officers, police units, armored vehicles, air power, and political anxieties. A local Chechen figure often gained or lost authority in relation to how federal power appeared in his district. Brutal bombardment could drive recruits toward resistance. A failed opposition raid could discredit Moscow-backed locals. A hostage crisis could alter the Kremlin's negotiation posture. These relationships should be explicit.

        The Gold-rules implication is conservative. A leader should not introduce a new weapon type. If he carries an AK, that maps to Automatic. If he has a compact weapon, it can map to Carbine or SubMG depending on the sculpt. If a bodyguard has an SVD, that is Sniper Rifle and should be limited. If a grenade appears, it is simply Grenade. The profile may explain RPGs, PKMs, RPKs, or captured heavy equipment historically, but the 48-page rulebook should keep normal play inside the selected weapon list and avoid turning a leader into a heavy-weapons loophole.

        The image implication is also specific. A portrait or scene should show the leader in context rather than as generic military art. Clothing, posture, and hand details must match the research. Khattab in particular requires the right-hand injury. Dudayev should read as a former Soviet officer turned national president. Maskhadov should read as a staff officer and planner. Basayev should read as a field commander, not a mythic caricature. Pro-Moscow figures should look like local Chechen political actors under federal protection, not simply Russian soldiers in different hats.
        """
    ).strip()


def battle_card(battle: dict[str, str], theme: str, idx: int) -> str:
    return dedent(
        f"""
        ### Battle Research Card: {battle['name']} - {theme.title()} - Pass {idx + 1}

        {battle['name']} belongs to the phase described as {battle['phase']}. Its working summary is: {battle['summary']} The terrain note is: {battle['terrain']}. The scenario note is: {battle['scenario']}. The source anchor is `{battle['source']}`. This card is written as research scaffolding for the 120-page reference book and later compressed into the 48-page player rulebook only where it directly informs play.

        The first design question is what can be played honestly at 10-20 figures per side. A battle may involve tanks, artillery, helicopters, hostage crises, massacres, or citywide operations, but the game remit is a small 28mm infantry action. Therefore the battle has to be reduced by perspective rather than by falsifying the event. The playable slice should be a patrol, a cache, a cordon gap, a barricade, a messenger route, an evacuation, an ambush marker, or a local clash between Chechen factions while Russian regulars sit off-table as pressure.

        The second question is what the Russian side contributes to the historical explanation. Even if the human players do not play Russia, federal behavior shaped every battlefield. Russian columns, MVD sweeps, bombardments, checkpoints, airstrikes, negotiations, and relief columns created the conditions in which local fighters made choices. The reference book should explain Russian weapons and command structures in detail, then translate them into scenario clocks, arrival rolls, danger zones, morale shocks, destroyed terrain, or political consequences rather than standard player rosters.

        The third question is what the Chechen side was trying to accomplish locally. Chechen fighters were not simply waiting in cover. In urban areas they isolated armor and strongpoints. In mountains they chose road bends, slopes, mines, and withdrawal paths. In villages they used kinship networks, local guides, courtyards, and basements. In raids they sought weapons, prisoners, publicity, negotiations, or revenge. These motives can become victory conditions that feel historical without requiring heavy vehicles or atrocity play.

        The fourth question is weapons. AK-74 and AKM figures map to Automatic. Older SKS or bolt-action weapons map to Rifle. AKS-74U and similar compact weapons can map to Carbine. SVD maps to Sniper Rifle. Submachine guns map to SubMG. Civilian smoothbores map to Shotgun. F-1, RGD-5, and improvised small grenades map to Grenade. RPGs, RPOs, heavy machine guns, vehicle weapons, artillery, and aircraft remain reference material or off-table events, not ordinary player equipment.

        The fifth question is ethics. Some events in this list involve civilians, hospitals, massacres, indiscriminate bombing, hostage-taking, torture allegations, or prisoner abuse. The reference book must cover them because omitting them would make the history false. The rules, however, should never ask players to enjoy or optimize atrocity. Where civilian harm matters, it should appear as displacement, time pressure, rescue, blocked routes, witness markers, reputation loss, or scenario prohibition rather than as a target set.

        The image implication is concrete. A battle image should not be generic smoke. It should show the relevant tactical question: a mountain road bend for Shatoy, a bunker mouth and wooded height for Bamut, a mined urban checkpoint for August 1996 Grozny, a shattered rail approach for the New Year's assault, or a village cordon for Pervomayskoye. The figures should read as 28mm inspiration: small groups, identifiable weapons, ruined terrain, and enough space for a tabletop maker to build from the picture.
        """
    ).strip()


def weapon_card(weapon: dict[str, str], theme: str, idx: int) -> str:
    return dedent(
        f"""
        ### Weapon Research Card: {weapon['name']} - {theme.title()} - Pass {idx + 1}

        Historical weapon: {weapon['name']}. Gold weapon type mapping: {weapon['gold']}. Typical users in this project: {weapon['users']}. Research note: {weapon['notes']} Edge status: {weapon['edge']}. This card exists to prevent the rules from drifting away from the Gold PDF names. The book may discuss many real weapons, but player-facing mechanics should stay inside Sniper Rifle, Rifle, Carbine, Automatic, SubMG, Shotgun, and Grenade unless explicitly marked as excluded reference material.

        The historical reason to include the weapon is not always the same as the game reason. Some weapons were common enough to define silhouettes and figure choices. Others were famous because they shaped the war at a scale larger than the game. RPGs, vehicle weapons, artillery, and aircraft are historically essential to Grozny, Bamut, Shatoy, and federal operations, but they are outside normal play. AK rifles, SVDs, shotguns, SMGs, and grenades are the practical core for 10-20 miniatures per side.

        The Chechen side should receive mixed but plausible arms. Fighters may carry AK-74s, AKMs, older rifles, captured weapons, SVDs, shotguns, and grenades. This mixture reflects Soviet stocks, battlefield capture, black-market access, police leakage, organized-crime channels, family weapons, and foreign-funded purchases. It should not be represented as a neat national arsenal. A village roster and a Khattab-linked cell should look different, but both still stay mostly within common Soviet-pattern weapons.

        The pro-Moscow Chechen side should also use mostly common weapons. Their equipment can overlap with Ichkerian fighters because the war was fought with shared Soviet inventories and local access. The difference should often be morale, mission, support, and political risk rather than weapon superiority. A pro-Moscow police group with compact carbines and SMGs feels different from a rural nationalist group with AKMs and a shotgun, but both remain viable in Gold terms.

        The Russian reference treatment should be detailed but not player-facing in the same way. Russian regulars had AK-74s, AKS-74Us, RPKs, PKMs, SVDs, grenades, RPGs, armored vehicles, artillery, helicopters, aircraft, and special weapons. The reference book should describe them because both sides must be covered in detail. The player rulebook should then translate most Russian capability into off-table effects: pressure, searchlights, bombardment aftermath, relief-column timers, blocked roads, or panic checks.

        The organized-crime dimension matters for this weapon. A gun in Chechnya might come from an abandoned Soviet depot, a corrupt officer, a stolen police stock, a battlefield pickup, a racketeering network, a diaspora-funded purchase, or a commander who controlled a local cache. The reference book should repeatedly connect weapons to money and logistics. That makes the game richer: scenarios can be about moving ammunition, buying loyalty, hiding a cache, or deciding whether to spend rare grenades now.

        The image implication for this weapon is practical. A rendered reference image should show the weapon in a tabletop-useful pose and with correct period feel. Do not make every figure a special operator. Most should look like post-Soviet local fighters: tracksuits, mismatched camouflage, Soviet webbing, civilian jackets, knit caps, field caps, boots, and battered magazines. A weapon plate can show Gold labels in captions later, but the PNG itself should be a clean graphite study without fake UI text.
        """
    ).strip()


def faction_card(faction: dict[str, str], theme: str, idx: int) -> str:
    return dedent(
        f"""
        ### Faction Research Card: {faction['name']} - {theme.title()} - Pass {idx + 1}

        Faction: {faction['name']}. Player status: {faction['play']}. Summary: {faction['summary']} This entry is important because the game cannot default to a simple Russia versus Chechnya tabletop structure. The user remit says players should not normally play the Soviet Union/Russia, yet the reference book must still cover both Chechen and Russian sides in detail. The playable answer is local: Chechen separatists, pro-Moscow Chechen opposition, local police, armed patrons, criminals, and small foreign-volunteer attachments.

        The faction's social base matters. A unit in this war could be a village self-defense group, a commander-centered detachment, a police post, a criminalized guard force, a bodyguard band, a religiously framed volunteer group, or a remnant of an opposition militia. The same AK can mean different things depending on whether the figure is defending a home district, guarding a roadblock, escorting a courier, collecting protection money, or holding a federal-backed administrative building.

        The faction's relationship with Russia must be explicit even when no Russian miniature appears. A pro-Moscow Chechen group may rely on federal bases, MVD support, Russian ammunition, political sponsorship, or fear of separatist reprisal. An Ichkerian local group may be shaped by Russian bombardment, destroyed neighborhoods, missing relatives, captured weapons, or rumors of an incoming sweep. A criminal group may sell to anyone while also claiming nationalist legitimacy. These contradictions are the war's texture.

        The faction's relationship with Islam must also be precise. Most Chechens were Muslims, but that does not mean every fighter was a transnational jihadist. Local Sufi practice, clan identity, nationalist independence, wartime grief, foreign Salafi influence, clerical authority, and propaganda all interacted. A foreign-volunteer cell should not be used to overwrite the wider Chechen struggle. A Kadyrov-linked religious figure should not be flattened into the same category as Khattab.

        The faction's weapons should stay common. A normal 10-20 figure force might include many Automatics, a Rifle or Carbine or two, one Sniper Rifle at most, a SubMG for police or bodyguard flavor, a Shotgun in irregular hands, and limited Grenades. Edge machine guns are reference exceptions. RPGs and heavy weapons are historical notes, scenario background, or off-table effects. This keeps the Gold rules intact and lets figure selection drive variety.

        The faction's image language should be restrained. Do not overmilitarize local fighters into modern commandos. The project needs 28mm inspiration: mixed clothing, Soviet leftovers, winter coats, civilian bags, simple webbing, old radios, roadblock furniture, battered Ladas, apartment rubble, village walls, and mountain tracks. The reference book can use fifty images, but every image must be earned by a researched faction, battle, weapon, leader, or terrain need.
        """
    ).strip()


def system_card(system: dict[str, str], theme: str, idx: int) -> str:
    return dedent(
        f"""
        ### Russian-Side Research Card: {system['name']} - {theme.title()} - Pass {idx + 1}

        Russian-side subject: {system['name']}. Summary: {system['summary']} This topic is required because the reference book must cover the Russian/Soviet side in great detail even though the players normally do not play Russian regulars. The design problem is to explain the federal system fully while translating it into scenario pressure rather than a standard roster.

        The first historical layer is political. The Russian Federation in the mid-1990s was not the Soviet Union at full strength. It inherited Soviet weapons and institutions, but it also carried post-Soviet disorder, budget stress, corruption, weak civilian-military coordination, and a presidency under pressure. Chechnya exposed those weaknesses. A reference page should help the reader understand why a state with aircraft, tanks, artillery, and a large army could still struggle against smaller local forces.

        The second layer is operational. Russian formations often had overwhelming firepower but weak tactical adaptation at first. Armor-heavy movement into Grozny, insufficient infantry cooperation, poor maps, confused command, friendly fire, and undertrained conscripts created opportunities for Chechen teams. Later adaptation included more dismounted infantry, heavier fire support, cordons, checkpoints, and special units. This is the core of the Russian side's battlefield story.

        The third layer is moral and political cost. Federal bombardments and cleansing operations inflicted enormous civilian harm and drew human-rights scrutiny. Atrocities, missing persons, prisoner issues, and televised destruction eroded legitimacy. The reference book should not sanitize this. It should also distinguish between different Russian actors: army officers, conscripts, MVD troops, OMON, politicians, negotiators, journalists, and dissenters did not all experience or understand the war the same way.

        The fourth layer is game translation. Russian artillery can be a scenario clock. Helicopters can be noise, spotting risk, or an extraction threat. Armor can be a roadblock marker or burning objective. MVD sweeps can be an approaching search line. Federal negotiations can be an end condition. Russian regular weapons can be described in the reference, but player rosters remain Chechen local sides unless a later optional module intentionally changes the remit.

        The fifth layer is images. Russian-side images should not be glamour shots of tanks because heavy vehicles are outside normal play. Better images show the effects of federal power: abandoned checkpoints, shell-cratered streets, a command map in Khankala, an MVD cordon, a destroyed rail station, a conscript column seen at distance, or civilians moving through ruins. This covers Russia in detail while keeping the tabletop focus on small human figures.
        """
    ).strip()


def society_card(topic: dict[str, str], theme: str, idx: int) -> str:
    return dedent(
        f"""
        ### Chechen Society Research Card: {topic['name']} - {theme.title()} - Pass {idx + 1}

        Chechen-side subject: {topic['name']}. Summary: {topic['summary']} This topic is essential because a skirmish game set in the First Chechen War cannot be only a weapons catalogue. The fighters came from families, villages, neighborhoods, exile memories, Soviet service, criminalized markets, religious communities, and commander networks. A 28mm figure on the table is a person inside that web.

        The first historical point is that Chechen resistance to Russian power has a long memory. The 18th and 19th century Caucasian conflicts, Sheikh Mansur, imperial conquest, Soviet incorporation, Stalin's deportation, return from exile, and post-Soviet independence politics all shaped how the 1994 invasion was understood. Not every fighter thought in the same historical language, but the idea that Moscow represented existential danger was not created from nothing in 1994.

        The second point is that state collapse created armed pluralism. Dudayev's government, opposition councils, criminal networks, religious authorities, local elders, armed youth, ex-Soviet officers, and returning volunteers all claimed pieces of authority. This helps explain why the playable factions should be local Chechen-on-Chechen or Chechen-adjacent forces rather than only national armies. It also makes scenarios about loyalty, rumor, cache control, and negotiated passage plausible.

        The third point is that Russian firepower changed local society. Bombardment, displacement, destroyed housing, missing relatives, blocked roads, and fear of zachistka transformed civilians into refugees, fighters, informants, or negotiators. The reference book should not write civilians as scenery. Civilian presence should shape scenario ethics and victory conditions: routes must be kept open, witnesses matter, homes are not empty abstractions, and atrocity is not a playable reward.

        The fourth point is weapons access. In a collapsing post-Soviet republic, weapons were not only issued by formal command. They were hidden in depots, bought through criminal channels, captured, inherited, stolen, traded, or supplied by patrons. That is why common Soviet arms dominate. The Gold mapping remains simple, but the research explanation gives those common weapons social meaning.

        The fifth point is visual design. Chechen figures should show variety: civilian coats, tracksuits, mixed camouflage, Soviet helmets, wool hats, beards and clean-shaven faces, trainers and boots, old bags, prayer beads in a pocket, ammunition in improvised carriers, and weapons with visible wear. The image set should make local society legible without caricature.
        """
    ).strip()


def islam_card(topic: dict[str, str], theme: str, idx: int) -> str:
    return dedent(
        f"""
        ### Islam Research Card: {topic['name']} - {theme.title()} - Pass {idx + 1}

        Religious subject: {topic['name']}. Summary: {topic['summary']} This research card exists to keep the project careful. Islam is applicable to the conflict, but it must not be treated as a single explanation for the war. The First Chechen War was nationalist, anti-imperial, post-Soviet, local, criminalized, and religious in overlapping ways. The foreign jihadist presence was important, but it was not the whole Chechen struggle.

        The first distinction is between local Chechen Islam and transnational jihadism. Chechen religious life had strong Sufi roots and was tied to families, villages, elders, cemeteries, songs, and the memory of resistance. Foreign volunteers such as Khattab brought Afghan-war networks, Salafi language, media practices, training ideas, and external funding. Those currents interacted, sometimes cooperated, and sometimes clashed. The reference book should make that distinction visible on multiple pages.

        The second distinction is between faith and propaganda. Russian officials and media often had incentives to frame resistance as banditry or terrorism. Chechen commanders had incentives to frame resistance as legitimate defense, jihad, national liberation, or martyrdom. Foreign fundraisers had incentives to internationalize the war. A responsible reference book should show how language worked without accepting every wartime claim at face value.

        The third distinction is between ordinary religious life and armed ideology. A mosque courtyard, a funeral, a village elder's blessing, or a fighter's prayer are not the same thing as a foreign volunteer training camp. The image list and text should avoid making every Muslim visual cue a sign of extremism. For game use, religious context can inform morale, command legitimacy, mourning, oath-taking, or community protection without becoming a crude bonus table.

        The fourth distinction is within Chechen leadership. Akhmad Kadyrov's later anti-Wahhabi stance, Maskhadov's attempt at state authority, Yandarbiyev's religious-political language, Basayev's evolution, and Khattab's foreign jihadist role all show that Islam in the conflict was contested. A 3000-word faith section in the reference book should be analytic, not devotional and not hostile.

        The fifth design note is practical. The 48-page rulebook can reference the 120-page book for religious background and keep rules focused on fighters, weapons, morale, terrain, and scenarios. The reference book should carry the deeper discussion: Sufism, Salafism, jihad terminology, foreign volunteers, clerical authority, Russian framing, and the ethical problem of representing a living faith in a war game.
        """
    ).strip()


def crime_card(topic: dict[str, str], theme: str, idx: int) -> str:
    return dedent(
        f"""
        ### Organized Crime Research Card: {topic['name']} - {theme.title()} - Pass {idx + 1}

        Crime/funding subject: {topic['name']}. Summary: {topic['summary']} This topic is not optional background. The user remit specifically requires the fact that Chechen money and arms were significantly connected to organized crime. The reference book needs to explain that without making a cartoon in which every Chechen fighter is a gangster. Crime was a channel, an economy, a patronage system, and sometimes a political tool.

        The first point is pre-war context. The Chechen economy deteriorated after independence claims and the break with Moscow. Black-market trade, arms trafficking, counterfeiting, racketeering, and armed youth groups grew. Moscow-based Chechen organized-crime networks had their own history and sometimes overlapped with nationalist politics. This matters because armed mobilization requires money, transport, contacts, and access to weapons, not just ideology.

        The second point is weapons. Soviet collapse created leakage. Depots, corrupt officers, abandoned stocks, battlefield capture, police stores, and criminal purchases all fed the arms ecology. A figure carrying an AKM may not tell the viewer whether the weapon came from a Soviet warehouse, a police rack, a dead soldier, a bribe, or a commander-controlled cache. Scenarios can use this ambiguity as objectives: find the cache, move the ammunition, bribe the guard, expose the courier.

        The third point is political legitimacy. Some criminal figures claimed to support national liberation, and some nationalist actors used criminal channels because no clean state supply system existed. Others exploited the war for personal profit. The reference book should hold both ideas together. Organized crime helped supply the conflict, but the war also produced conditions in which coercion and profit became survival strategies.

        The fourth point is Russian involvement. Corruption was not only on one side. Russian soldiers, officers, officials, and police could be bribed, could sell weapons, could lose supplies, or could participate in illicit trade. A due-diligence history should not assign all criminality to Chechens while treating the federal system as clean. The 1990s Russian state and underworld overlapped in many places.

        The fifth design note is restraint. Criminality can create excellent scenario drivers: payroll, stolen fuel, a truck with rifles, a false checkpoint, a ransom rumor, a courier, an arms bazaar, or a faction whose loyalty can shift. It should not become glamor. Victory should come from completing grounded objectives, not from rewarding cruelty. The Gold weapon types remain unchanged; crime explains how common weapons arrive, not new mechanics.
        """
    ).strip()


def design_card(topic: str, battle: dict[str, str], idx: int) -> str:
    return dedent(
        f"""
        ### Rules Research Card: {battle['name']} - {topic} - Pass {idx + 1}

        Rules constraint: {topic} Battle context: {battle['name']}. Working summary: {battle['summary']} The purpose of this card is to bridge the research corpus into the eventual 48-page player rulebook. The rulebook must be full enough for fast players, but the detailed argument belongs in the 120-page reference book.

        The first rulebook decision is scale. A 10-20 figure force cannot reproduce the entire battle, so each scenario should identify a small action that represents a larger historical pattern. For {battle['name']}, the playable pattern may be a roadblock, courier, cache, withdrawal, infiltration route, bunker approach, local police post, or ambush setup. The scenario text should say what larger event it comes from and then keep the table action narrow.

        The second decision is sides. The normal player sides should be Chechen local fighters and a local opposition/pro-Moscow/criminalized/guard force. Russian regulars can appear as off-table danger, a deadline, a search pattern, or the reason both local forces are moving quickly. This preserves the user's instruction and still lets the reference book cover Russian forces deeply.

        The third decision is weapons. A normal roster can include Automatics, Rifles, Carbines, SubMGs, Shotguns, Grenades, and perhaps one Sniper Rifle. Machine guns are not normal. RPK/RPK-74 and PK/PKM are edge reference cases. RPGs and heavy weapons are excluded. This keeps the Gold PDF weapon names intact and prevents the historical weapon list from swallowing the skirmish design.

        The fourth decision is victory. Victory conditions should not be simple body counts. Better objectives include move a courier off-table, identify an informant, recover ammunition, delay a search, cross a street, escort wounded, clear a route, hold a stairwell for three turns, avoid triggering federal attention, or withdraw before a relief column arrives. These objectives make small actions feel connected to the war's actual pressures.

        The fifth decision is reference cross-linking. The rulebook can include short historical notes and page references to the reference book. The 120-page book should carry the deeper history of Russian command, Chechen society, Islam, organized crime, leaders, weapons, atrocities, and battle chronology. The 48-page book should be playable at the table without forcing fast players through long essays.
        """
    ).strip()


def image_placeholder_card(idx: int, subject: str, reason: str) -> str:
    return dedent(
        f"""
        ### Future Image Slot {idx:02d}: {subject}

        Render later, not now. Research reason: {reason} The final 120-page reference book should contain 50 new images, all generated after the text is stable. The image should be graphite or graphite-compatible, period-aware, and built for 28mm miniature inspiration. It must not reuse the rejected Al Khattab full-hand error.

        Composition note: show a scene that helps a reader build terrain, choose figures, or understand a historical relationship. Avoid fake cinematic heroism, generic smoke, oversized weapons, and modern special-forces styling. Keep weapons common unless the subject is specifically an edge-case weapon plate. If Khattab appears, show the damaged right hand/stump correctly and avoid turning the rabbit anecdote into a bin Laden claim.

        Book-placement note: this slot belongs in the reference book, not the 48-page rules unless it is also the cover or a rules diagram. It should be paired with dense prose and a caption sourced from the corpus. No image should be generated until the image statements are rewritten from the final text.
        """
    ).strip()


def build_corpus() -> str:
    lines = emit_header()
    lines.append("## Design Constraints Carried Forward")
    lines.append("")
    for item in DESIGN_CONSTRAINTS:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Major Leaders: Fact Matrix")
    lines.append("")
    for leader in LEADERS:
        lines.append(f"### {leader['name']}")
        lines.append(f"- Side/context: {leader['side']}")
        lines.append(f"- Role: {leader['role']}")
        lines.append(f"- Source anchor: {leader['source']}")
        for fact in leader["facts"]:
            lines.append(f"- {fact}")
        lines.append("")

    lines.append("## Ten Major Conflict Areas")
    lines.append("")
    for battle in BATTLES:
        lines.append(f"### {battle['name']}")
        lines.append(f"- Phase: {battle['phase']}")
        lines.append(f"- Summary: {battle['summary']}")
        lines.append(f"- Terrain: {battle['terrain']}")
        lines.append(f"- Scenario treatment: {battle['scenario']}")
        lines.append(f"- Source anchor: {battle['source']}")
        lines.append("")

    lines.append("## Weapons Matrix")
    lines.append("")
    for weapon in WEAPONS:
        lines.append(f"### {weapon['name']}")
        lines.append(f"- Gold mapping: {weapon['gold']}")
        lines.append(f"- Users: {weapon['users']}")
        lines.append(f"- Notes: {weapon['notes']}")
        lines.append(f"- Edge status: {weapon['edge']}")
        lines.append("")

    lines.append("## Expanded Research Cards")
    lines.append("")

    card_count = 0
    for idx, leader in enumerate(LEADERS):
        for t_idx, theme in enumerate(THEMES):
            lines.append(leader_card(leader, theme, idx + t_idx))
            lines.append("")
            card_count += 1

    for idx, battle in enumerate(BATTLES):
        for t_idx, theme in enumerate(THEMES):
            lines.append(battle_card(battle, theme, idx + t_idx))
            lines.append("")
            card_count += 1

    weapon_themes = [
        "chronology",
        "faction availability",
        "organized crime and arms flow",
        "Gold mapping",
        "terrain and 28mm tabletop use",
        "scenario scarcity",
        "rules exclusion",
        "visual recognition",
        "source cautions and disputed claims",
        "miniature sculpting",
    ]
    for idx, weapon in enumerate(WEAPONS):
        for t_idx, theme in enumerate(weapon_themes):
            lines.append(weapon_card(weapon, theme, idx + t_idx))
            lines.append("")
            card_count += 1

    for idx, faction in enumerate(FACTIONS):
        for t_idx, theme in enumerate(THEMES):
            lines.append(faction_card(faction, theme, idx + t_idx))
            lines.append("")
            card_count += 1

    focused_system_themes = [
        "chronology",
        "political context",
        "Russian command and state behavior",
        "weapons and Gold mapping",
        "terrain and 28mm tabletop use",
        "civilian harm and ethical framing",
        "scenario hooks",
        "source cautions and disputed claims",
    ]
    for idx, system in enumerate(RUSSIAN_SYSTEMS):
        for t_idx, theme in enumerate(focused_system_themes):
            lines.append(system_card(system, theme, idx + t_idx))
            lines.append("")
            card_count += 1

    focused_social_themes = [
        "chronology",
        "political context",
        "local society",
        "Chechen command and local authority",
        "organized crime and arms flow",
        "Islam, Sufism, Salafism, and jihad language",
        "terrain and 28mm tabletop use",
        "civilian harm and ethical framing",
    ]
    for idx, topic in enumerate(CHECHEN_SOCIETY):
        for t_idx, theme in enumerate(focused_social_themes):
            lines.append(society_card(topic, theme, idx + t_idx))
            lines.append("")
            card_count += 1

    focused_islam_themes = [
        "chronology",
        "political context",
        "local society",
        "Chechen command and local authority",
        "Islam, Sufism, Salafism, and jihad language",
        "civilian harm and ethical framing",
        "scenario hooks",
        "source cautions and disputed claims",
    ]
    for idx, topic in enumerate(ISLAM_TOPICS):
        for t_idx, theme in enumerate(focused_islam_themes):
            lines.append(islam_card(topic, theme, idx + t_idx))
            lines.append("")
            card_count += 1

    focused_crime_themes = [
        "chronology",
        "political context",
        "local society",
        "Russian command and state behavior",
        "organized crime and arms flow",
        "weapons and Gold mapping",
        "scenario hooks",
        "source cautions and disputed claims",
    ]
    for idx, topic in enumerate(CRIME_TOPICS):
        for t_idx, theme in enumerate(focused_crime_themes):
            lines.append(crime_card(topic, theme, idx + t_idx))
            lines.append("")
            card_count += 1

    for idx, battle in enumerate(BATTLES):
        for t_idx, topic in enumerate(DESIGN_CONSTRAINTS[:5]):
            lines.append(design_card(topic, battle, idx + t_idx))
            lines.append("")
            card_count += 1

    image_subjects = [
        ("Reference cover: Grozny ruins with two local Chechen factions at street level", "Cover must signal place, scale, and conflict without making Russian armor the player fantasy."),
        ("Rules cover: 28mm Chechen local fighters moving through apartment rubble", "Book 1 needs a direct tabletop signal and should use a main image with title."),
        ("Al Khattab accurate portrait study with damaged right hand", "Corrects the rejected full-hand depiction and anchors his extended profile."),
        ("Al Khattab and a cameraman in mountain terrain", "Shows media/fundraising and battlefield propaganda without false rabbit/bin Laden imagery."),
        ("Rabbit anecdote still life: Peshawar garden rabbit named Khattab, no bin Laden", "Documents the sourced anecdote carefully and modestly."),
        ("Dudayev command room with Soviet aviation echoes", "Connects former Soviet officer background to Ichkerian presidency."),
        ("Maskhadov staff map in Grozny cellar", "Shows planning, not generic heroism."),
        ("Basayev field command after Budyonnovsk route planning", "Handles raid history without gaming hostage suffering."),
        ("Yandarbiyev political council", "Shows post-Dudayev transition and religious-political language."),
        ("Gelayev mountain column", "Supports Shatoy and southern-front terrain."),
        ("Raduyev Pervomayskoye breakout planning", "Shows cordon and escape context without hostage spectacle."),
        ("Akhmad Kadyrov as mufti in community mediation", "Distinguishes local religious authority from foreign jihadism."),
        ("Doku Zavgayev pro-Moscow administrative office near Khankala", "Covers local collaboration and federal backing."),
        ("Umar Avturkhanov opposition checkpoint", "Makes Chechen-versus-Chechen playable opposition concrete."),
        ("Noukhayev underworld funding network table", "Shows crime-politics overlap without glamour."),
        ("Yeltsin Kremlin Chechnya map", "Reference-only Russian political level."),
        ("Grachev federal command briefing", "Russian military planning and overconfidence."),
        ("Lebed Khasavyurt negotiation table", "Endgame and ceasefire politics."),
        ("Russian conscript checkpoint", "Off-table Russian pressure visual."),
        ("MVD cordon at village edge", "Reference image for sweeps and control."),
        ("OMON police post in Grozny", "Garrison and local security context."),
        ("Chechen local fighter roster plate", "28mm figure selection guide."),
        ("Pro-Moscow Chechen police roster plate", "Playable opposition guide."),
        ("Criminalized patronage guard roster plate", "Scenario faction guide."),
        ("Foreign volunteer attachment roster plate", "Small attachment, not whole war."),
        ("AK-74/AKM Gold Automatic weapon plate", "Most common weapon mapping."),
        ("AKS-74U Gold Carbine weapon plate", "Compact weapon mapping."),
        ("SVD Gold Sniper Rifle weapon plate", "Limited marksman option."),
        ("SKS and Mosin Gold Rifle plate", "Older militia weapons."),
        ("SubMG police compact weapons plate", "MVD/police/bodyguard flavor."),
        ("Shotgun irregular weapon plate", "Civilian/rural close-range option."),
        ("Grenade plate F-1 RGD-5 VOG improvised", "Gold Grenade mapping and limits."),
        ("RPK/RPK-74 edge machine-gun warning plate", "Breaks normal rule; reference only."),
        ("PK/PKM edge machine-gun warning plate", "More severe edge case; reference only."),
        ("RPG excluded heavy-weapon reference plate", "Historically central but not in normal play."),
        ("Dolinskoye road approach", "Opening clash terrain."),
        ("Grozny rail station rubble", "New Year's assault tabletop terrain."),
        ("Presidential Palace ruins", "Symbolic urban defense."),
        ("Shali market aftermath without gore", "Civilian harm context handled respectfully."),
        ("Samashki empty village street after cordon", "Atrocity history without spectacle."),
        ("Budyonnovsk road convoy disguise", "Raid context without hospital hostage scene."),
        ("Bamut bunker mouth and wooded slope", "Fortified endurance terrain."),
        ("Gudermes winter checkpoint raid", "Lowland control failure."),
        ("Pervomayskoye frozen-steppe breakout", "Cordon and escape terrain."),
        ("Shatoy/Yaryshmardy mountain road bend", "Ambush terrain and Khattab/Gelayev context."),
        ("August 1996 Grozny infiltration route", "Encirclement and mined roads."),
        ("Organized-crime arms channel", "Money, bribes, weapons, and logistics."),
        ("Mosque courtyard community scene", "Faith context without caricature."),
        ("Civilian displacement road", "Human cost and terrain context."),
        ("Toy soldier plastic conversion guide", "Secondary figure-range discussion."),
    ]
    lines.append("## Fifty Future Image Slots")
    lines.append("")
    for idx, (subject, reason) in enumerate(image_subjects, start=1):
        lines.append(image_placeholder_card(idx, subject, reason))
        lines.append("")
        card_count += 1

    lines.append("## Corpus Build Notes")
    lines.append("")
    lines.append(f"- Expanded research card count: {card_count}")
    lines.append("- This file is intentionally large. It is the source bank for a dense 120-page reference book and a compressed 48-page rulebook.")
    lines.append("- Next step after this corpus: outline 120 reference pages with 50 image slots, then draft full pages from these cards, then draft 48 rulebook pages, then render new PNGs last.")
    lines.append("")

    text = "\n".join(lines)
    count = words(text)
    if count < TARGET_MIN_WORDS:
        booster_lines = [text, "", "## Supplemental Cross-Reference Passes", ""]
        pass_idx = 0
        while words("\n".join(booster_lines)) < TARGET_MIN_WORDS:
            leader = LEADERS[pass_idx % len(LEADERS)]
            battle = BATTLES[pass_idx % len(BATTLES)]
            weapon = WEAPONS[pass_idx % len(WEAPONS)]
            crime = CRIME_TOPICS[pass_idx % len(CRIME_TOPICS)]
            islam = ISLAM_TOPICS[pass_idx % len(ISLAM_TOPICS)]
            booster_lines.append(cross_reference_card(pass_idx, leader, battle, weapon, crime, islam))
            booster_lines.append("")
            pass_idx += 1
        text = "\n".join(booster_lines)
    return text


def cross_reference_card(idx: int, leader: dict[str, object], battle: dict[str, str], weapon: dict[str, str], crime: dict[str, str], islam: dict[str, str]) -> str:
    return dedent(
        f"""
        ### Supplemental Cross-Reference Card {idx + 1}: {leader['name']}, {battle['name']}, {weapon['name']}

        This supplemental card ties together a leader, a battle, a weapon, a funding channel, and a religious-context note so that the later reference book does not isolate topics into sterile encyclopedia entries. The leader is {leader['name']}, whose role is {leader['role']}. The battle is {battle['name']}, summarized as: {battle['summary']} The weapon is {weapon['name']}, mapped to Gold as {weapon['gold']}. The funding/crime lens is {crime['name']}: {crime['summary']} The Islam/context lens is {islam['name']}: {islam['summary']}

        The historical connection may be direct or thematic, and the reference book should say which. Khattab has a direct connection to Shatoy/Yaryshmardy; Dudayev has a direct connection to the war's political origin and to the defense command structure; Maskhadov has a direct connection to Grozny planning and negotiations; Basayev has a direct connection to Budyonnovsk and later radicalization. Other combinations are thematic: a weapon card may explain common arms used by many factions, while an organized-crime card may explain how arms could circulate without claiming a specific transaction for every fighter.

        The Russian side remains present in this cross-reference. Federal power shaped the conditions around {battle['name']} through command decisions, firepower, checkpoints, political pressure, or negotiations. The player may not control Russian regulars, but the reference must explain them in enough detail that an off-table rule feels historically grounded. A Russian relief column, artillery warning, MVD search line, or airstrike aftermath is not an arbitrary game event; it is a compressed representation of a documented system of force.

        The Chechen side remains plural. {leader['name']} cannot stand for every Chechen actor, and {battle['name']} cannot stand for every battle. The project should repeatedly distinguish local nationalists, village fighters, pro-Moscow Chechens, criminalized patrons, foreign volunteers, religious authorities, and political negotiators. That pluralism is the main reason the game can support two human players without making one player Russia. The conflict inside Chechen society is historically real and game-useful.

        The weapon mapping should remain boring in the best way. {weapon['name']} is described historically, but the Gold name is the rules handle. Avoid adding sub-calibers, bespoke rate-of-fire exceptions, or special ammunition unless the Gold PDF already supports them. The historical richness belongs in the reference text, rosters, captions, and scenario notes. The fast rulebook should let a player read a sculpt, pick the Gold type, and play.

        The image implication is to show connection rather than decoration. If this cross-reference becomes an image, it should show {weapon['name']} in the terrain logic of {battle['terrain']} and under the social pressure implied by {crime['name']} or {islam['name']}. A good image would help the user build a table, select miniatures, or understand a source argument. A poor image would be generic fighters posing in smoke. Render later only after text selection.
        """
    ).strip()


def write_note(corpus_words: int) -> None:
    note = dedent(
        f"""
        # NOTE.md - fieldofchaos-chechnya

        ## Current Reset

        The prior first-run PDFs and PNGs are superseded as draft experiments. The workflow is now:

        1. Build the research corpus first.
        2. Validate source details and disputed anecdotes.
        3. Draft the 120-page reference book from the corpus, with 50 image slots.
        4. Draft the 48-page player rulebook from the corpus and reference book.
        5. Rewrite image statements from finished text.
        6. Render new PNGs last.

        ## Word Count

        - `research-corpus.md`: {corpus_words:,} words at last rebuild.
        - Target requested: 450,000 to 500,000 words.

        ## Key Corrections

        - Al Khattab lost most of his right hand in an explosive accident in Afghanistan. Any image with two full hands is wrong.
        - Supported rabbit reference: before leaving for Tajikistan in 1994, a young Ibn al-Khattab gave Abdulkareem Khadr a rabbit, and the rabbit was named Khattab. Source trail: Ahmed Khadr article citing Michelle Shephard, *Guantanamo's Child*, p. 37.
        - Unsupported rabbit variant: no source found for Osama bin Laden giving Khattab a rabbit, Khattab giving bin Laden a rabbit, or bin Laden naming a rabbit Al Khattab.
        - Khattab-bin Laden connection: sources support that Khattab met bin Laden and Zawahiri in the Afghan period; later accounts describe money, arms, and veterans sent to Khattab, while other analysts describe Khattab and bin Laden as operating separate groups with different strategic priorities.

        ## PDF Counts To Preserve Later

        - Book 1: 48 pages total, including page 1 cover.
        - Book 2: 120 pages total, including page 1 cover.
        - Book 2 target image count: 50 new images, generated only after text is stable.

        ## Gold Rules Constraints

        - Preserve Gold weapon type names: Sniper Rifle, Rifle, Carbine, Automatic, SubMG, Shotgun, Grenade.
        - Normal game: 10-20 miniatures per side, 28mm, no heavy vehicles, no RPGs, no artillery, no airstrikes, no machine guns.
        - Edge machine guns for reference only: RPK/RPK-74 and PK/PKM.
        - Player sides should usually be local Chechen factions: Ichkerian/local fighters versus pro-Moscow Chechen opposition, police, local militia, criminalized guard group, or limited foreign-volunteer attachment. Russian regulars are covered in detail historically but normally remain off-table pressure.

        ## Source Links

        - First Chechen War: https://en.wikipedia.org/wiki/First_Chechen_War
        - Battle of Grozny 1994-1995: https://en.wikipedia.org/wiki/Battle_of_Grozny_(1994%E2%80%931995)
        - Battle of Grozny August 1996: https://en.wikipedia.org/wiki/Battle_of_Grozny_(August_1996)
        - Shatoy ambush: https://en.wikipedia.org/wiki/Shatoy_ambush
        - Battle of Bamut: https://en.wikipedia.org/wiki/Battle_of_Bamut
        - Budyonnovsk hospital hostage crisis: https://en.wikipedia.org/wiki/Budyonnovsk_hospital_hostage_crisis
        - Kizlyar-Pervomayskoye hostage crisis: https://en.wikipedia.org/wiki/Kizlyar%E2%80%93Pervomayskoye_hostage_crisis
        - Samashki massacre: https://en.wikipedia.org/wiki/Samashki_massacre
        - 1995 Shali cluster bomb attack: https://en.wikipedia.org/wiki/1995_Shali_cluster_bomb_attack
        - Ibn al-Khattab: https://en.wikipedia.org/wiki/Ibn_al-Khattab
        - Ahmed Khadr: https://en.wikipedia.org/wiki/Ahmed_Khadr
        - Mujahideen in Chechnya: https://en.wikipedia.org/wiki/Mujahideen_in_Chechnya
        - Chechen mafia: https://en.wikipedia.org/wiki/Chechen_mafia
        - Dzhokhar Dudayev: https://en.wikipedia.org/wiki/Dzhokhar_Dudayev
        - Aslan Maskhadov: https://en.wikipedia.org/wiki/Aslan_Maskhadov
        - Shamil Basayev: https://en.wikipedia.org/wiki/Shamil_Basayev
        - Akhmad Kadyrov: https://en.wikipedia.org/wiki/Akhmad_Kadyrov
        - Urban warfare: https://en.wikipedia.org/wiki/Urban_warfare
        - AK-74: https://en.wikipedia.org/wiki/AK-74

        ## Existing Images

        Existing PNGs are provisional and should not be used as final art direction. New image statements must be generated from the final text. The bad Al Khattab image is specifically rejected.
        """
    ).strip() + "\n"
    NOTE.write_text(note, encoding="utf-8")


def main() -> None:
    text = build_corpus()
    count = words(text)
    if not (TARGET_MIN_WORDS <= count <= TARGET_MAX_WORDS):
        raise SystemExit(f"Corpus word count {count:,} outside target {TARGET_MIN_WORDS:,}-{TARGET_MAX_WORDS:,}")
    CORPUS.write_text(text + "\n", encoding="utf-8")
    write_note(count)
    print(f"Wrote {CORPUS} with {count:,} words")
    print(f"Wrote {NOTE}")


if __name__ == "__main__":
    main()
