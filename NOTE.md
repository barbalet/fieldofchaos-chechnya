# NOTE.md - fieldofchaos-chechnya

## Current Reset Status

The earlier first-run PDFs and PNGs are superseded draft experiments. The active workflow is text first:

1. Research corpus.
2. Source validation.
3. 120-page reference text and 50 image statements.
4. 48-page rulebook text.
5. Editorial pass to reduce templating and sharpen page-specific prose.
6. New PNG rendering last.
7. PDF layout and visual verification after the text is stable.

## Current Active Text Counts

- `research-corpus.md`: 466,757 words.
- `book2-reference-draft.txt`: 55,172 words across 120 marked pages.
- `book1-rulebook-draft.txt`: 21,159 words across 48 marked pages.
- `reference-page-plan.md`: 120 reference pages, page 1 cover included.
- `image-statements.md`: 50 text-only image statements for the reference book.

## Key Corrections

- 2026-07-01 Book 1 rebuild: downloaded `https://warlordgames.com/downloads/pdf/bolt_action_reference.pdf` to `tmp/pdfs/bolt_action_reference.pdf`, rendered/studied its compact reference layout, then rebuilt `foc-chechnya-gold.pdf` as a 48-page US Letter, table-first rulebook. Bolt Action was used only as a layout reference; no Bolt Action mechanics were imported.
- Book 1 current source of truth is `tools/build_rulebook_pdf.py` and the generated `foc-chechnya-gold.pdf`. It now has a page-2 interleaved index, 40 non-weapon/non-First-Aid setting skills, recreated Gold combat/healing/movement/wound tables, Chechnya weapon-to-Gold-name mapping, enemy-only Soldier/Hunter/Animal and specialist packages, ten scenario cards, and quick-reference pages.
- 2026-07-01 Book 1 text correction: the first rebuilt rulebook pass overcorrected into table-reference format. `tools/build_rulebook_pdf.py` now injects page-specific prose blocks into every content page so the PDF reads as a rulebook with tables, not just a table packet.
- 2026-07-02 Book 1 fun/skill-matrix pass: added play-hook text boxes throughout the rulebook, renamed the skills play page to `Skill Matrix In Play`, replaced the old example-check table with a cross-stat skill matrix, and replaced the quick-reference skill list with a problem-first `Skill Matrix Quick Reference`.
- 2026-07-02 10 pt minimum pass: rebuilt both `foc-chechnya-gold.pdf` and `foc-chechnya-gold-reference.pdf` so ReportLab font calls audit at 10.0 pt minimum with no sub-10 pt text. Rulebook remains 48 pages; reference remains 120 pages. Rulebook page 40 and reference pages 46-51 explicitly cover organized crime, caches, bribes, oil theft, arms leakage, corrupt channels, and war-economy pressure.
- 2026-07-02 column image-fill pass: rebuilt both PDFs so in-column figures use cover-cropped frames instead of thumbnail-style fitting. Rulebook remains 48 pages; reference now renders to 122 pages because the 50 reference images have larger 230 pt figure frames. Extracted PDF font audit still reports 10.0 pt minimum and no sub-10 pt text in either book.
- 2026-07-02 Book 2 subsection-spacing pass: rebuilt `foc-chechnya-gold-reference.pdf` with a regular-line-break-sized gap after framed subsection bands and internal all-caps subsection labels. The reference now renders to 125 pages; extracted PDF font audit still reports 10.0 pt minimum and no sub-10 pt text.
- 2026-07-02 first-commit cleanup: removed generated `tmp/` caches, Python bytecode caches, Finder metadata, `rules-scratch.*`, the obsolete scratch PDF builder, and 27 unused/rejected PNG variants. Current `png/` contains 66 active image files referenced by `tools/build_rulebook_pdf.py`, `tools/build_reference_pdf.py`, or the project notes, with no missing or unused PNGs in that active allow-list.
- Visual proof renders were generated during layout passes and removed during first-commit cleanup. Regenerate proof PNGs with `pdftoppm` from the committed PDFs when needed. Current `pdfinfo` checks verify Book 1 at 48 US Letter pages and Book 2 at 125 US Letter pages.
- Al Khattab lost most of his right hand in an explosive accident in Afghanistan. Any image with two full hands is wrong.
- The supported rabbit reference is not a bin Laden story. The fetched Ahmed Khadr page says that before Tajikistan in 1994, Ibn al-Khattab gave Abdulkareem Khadr a rabbit, and the rabbit was named Khattab.
- No source found supports Osama bin Laden giving Khattab a rabbit, Khattab giving bin Laden a rabbit, or bin Laden naming a rabbit Al Khattab.
- The fetched Ibn al-Khattab page supports a bin Laden connection: Khattab met bin Laden and Zawahiri in the Afghan period; the page also reports claims that bin Laden sent veterans, money, and arms to Khattab while other accounts describe separate groups and strategic differences.
- Al Khattab likeness correction: use the RFE/RL image URL supplied by the user as the main visual direction. The controlling requirement is an African-influenced Afro-Arab/Saudi face with a very broad flat nose, low bridge, broad base, rounded tip, wide nostrils, full lips, shaped mustache line, thick beard, and no visible full right hand. Current PDF candidate: `png/ref-21-al-khattab-source-likeness-v6.png`.
- Reference PDF layout correction: `tools/build_reference_pdf.py` now uses larger measured two-column text, paragraph-aware column composition, running section headers, alternating image floats, framed image areas, caption bars, styled subsection bands, and overflow detection. The rebuilt PDF replaces the tiny fixed-width text layout.
- Index correction: Book 1 and Book 2 now use a true page-2 index structure: each section is followed immediately by its own subsections and page numbers. Do not split the index into one list of sections followed by one list of subsections.
- Section-start correction: sections no longer consume title-only opener pages. Each section starts on a new content page with the section title at the top, a compact summary line, and live text/images beginning on the same page. Column two on section-start pages must respect the lowered section content top.
- Rulebook layout correction: Book 1 now uses the same interleaved index, compact section-start, and subsection-band model and builds to exactly 48 pages with `tools/build_rulebook_pdf.py`.

## Book Counts To Preserve

- Book 1: 48 pages total, including page 1 cover.
- Book 2: approximately 120 pages total, including page 1 cover; current rendered PDF is 125 pages after the subsection-spacing layout correction.
- Book 2 target image count: 50 new images, generated only after text is stable.

## Gold Rules Constraints

- Preserve Gold weapon type names: Sniper Rifle, Rifle, Carbine, Automatic, SubMG, Shotgun, Grenade.
- Normal game: 10-20 miniatures per side, 28mm, no heavy vehicles, no RPGs, no artillery, no airstrikes, no machine guns.
- Edge machine guns for reference only: RPK/RPK-74 and PK/PKM.
- Player sides should usually be local Chechen factions: Ichkerian/local fighters versus pro-Moscow Chechen opposition, police, militia, criminalized guard group, or limited foreign-volunteer attachment.
- Russian regulars are covered in detail historically but normally remain off-table pressure.

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
- AK-74: https://en.wikipedia.org/wiki/AK-74

## Existing Images

Existing PNGs are provisional and should not be used as final art direction. New image statements must be generated from the final text. The bad Al Khattab full-hand image is specifically rejected.
