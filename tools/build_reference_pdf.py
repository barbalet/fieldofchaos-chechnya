#!/usr/bin/env python3
"""Build the Book 2 reference PDF as a sectioned reference book."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageOps
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book2-reference-draft.txt"
OUT = ROOT / "foc-chechnya-gold-reference.pdf"
PNG = ROOT / "png"
PDF_ASSETS = ROOT / "tmp" / "pdf-assets-reference"

PAGE_W, PAGE_H = letter
TARGET_PAGES = 120
MIN_FONT = 10.0

MARGIN_X = 44
TOP_BAND_H = 30
BODY_TOP = PAGE_H - 48
SECTION_BODY_TOP = PAGE_H - 135
BOTTOM_Y = 54
FOOTER_Y = 26
GUTTER = 18
COL_W = (PAGE_W - 2 * MARGIN_X - GUTTER) / 2

BODY_FONT = "Times-Roman"
BODY_SIZE = 12.12
BODY_LEADING = 15.27
SUBSECTION_AFTER_GAP = 15.0
INLINE_LABEL_AFTER_GAP = BODY_LEADING
CAPTION_FONT = "Helvetica-Oblique"
SMALL_FONT = "Helvetica"
SMALL_BOLD = "Helvetica-Bold"
TITLE_FONT = "Helvetica-Bold"

SECTION_FILL = colors.HexColor("#EDE9DE")
RULE = colors.HexColor("#A39A8D")
TEXT = colors.black
MUTED = colors.HexColor("#5E574F")
PALE = colors.HexColor("#F6F3EC")


IMAGE_SOURCE_PAGES = [
    1, 3, 4, 5, 6, 8, 10, 11, 13, 14,
    15, 16, 18, 19, 21, 22, 23, 24, 25, 26,
    27, 28, 29, 30, 31, 32, 33, 35, 36, 38,
    40, 42, 44, 47, 49, 50, 51, 52, 53, 54,
    55, 57, 58, 59, 60, 62, 65, 96, 97, 99,
]

IMAGE_FILES = [
    "ref-01-cover-grozny-ruins.png",
    "ref-02-chechnya-before-1991.png",
    "ref-03-deportation-return.png",
    "ref-04-dudayev-command-room.png",
    "ref-05-opposition-council.png",
    "ref-06-prewar-arms-ecology.png",
    "ref-07-federal-decision-room.png",
    "ref-08-dolinskoye-road.png",
    "ref-09-grozny-rail-station.png",
    "ref-10-presidential-palace-ruins.png",
    "ref-11-chechen-urban-fire-team.png",
    "ref-12-russian-conscript-column.png",
    "ref-13-shali-aftermath.png",
    "ref-14-samashki-empty-street.png",
    "ref-15-budyonnovsk-route-planning.png",
    "ref-16-ceasefire-negotiation-room.png",
    "ref-17-bamut-bunker-mouth.png",
    "ref-18-bamut-hardened-shelters.png",
    "ref-19-southern-mountain-logistics.png",
    "ref-20-foreign-volunteers-arrival.png",
    "ref-21-al-khattab-source-likeness-v6.png",
    "ref-22-al-khattab-injury-context-v3.png",
    "ref-23-rabbit-anecdote-khadr.png",
    "ref-24-al-khattab-arrival-v3.png",
    "ref-25-al-khattab-cameraman-v3.png",
    "ref-26-foreign-funding-network.png",
    "ref-27-khattab-chechen-field-command-v3.png",
    "ref-28-shatoy-yaryshmardy-road.png",
    "ref-29-mosque-courtyard-faith-context.png",
    "ref-30-jihad-local-defense-funeral.png",
    "ref-31-kadyrov-mufti-mediation.png",
    "ref-32-organized-crime-arms-channel.png",
    "ref-33-oil-theft-weapons-leakage.png",
    "ref-34-teip-village-loyalty.png",
    "ref-35-dudayev-profile.png",
    "ref-36-maskhadov-staff-map.png",
    "ref-37-basayev-field-command.png",
    "ref-38-yandarbiyev-political-council.png",
    "ref-39-gelayev-mountain-column.png",
    "ref-40-raduyev-pervomayskoye-planning.png",
    "ref-41-kadyrov-community-scene.png",
    "ref-42-noukhayev-underworld-politics.png",
    "ref-43-yeltsin-kremlin-map.png",
    "ref-44-grachev-command-briefing.png",
    "ref-45-lebed-khasavyurt-negotiation.png",
    "ref-46-mvd-cordon-village-edge.png",
    "ref-47-federal-firepower-aftermath.png",
    "ref-48-gudermes-checkpoint-aftermath.png",
    "ref-49-pervomayskoye-frozen-breakout.png",
    "ref-50-august-1996-grozny-infiltration.png",
]

IMAGE_CAPTIONS = [
    "Ruined Grozny street, civilians, and local armed men.",
    "Chechnya before 1991: mountains, village roads, cemetery, and memory.",
    "The 1944 deportation and return from exile.",
    "Dudayev-era command room and Ichkerian state papers.",
    "Moscow-backed Chechen opposition before open invasion.",
    "Prewar arms ecology: Soviet weapons, leakage, and black-market exchange.",
    "Federal decision room with Chechnya maps.",
    "Dolinskoye road approach in December 1994.",
    "Grozny railway station after the New Year's assault.",
    "Presidential Palace ruins and destroyed state authority.",
    "Chechen urban fire team moving through interior routes.",
    "Russian conscript column stalled outside Grozny.",
    "Shali aftermath: cratered market and hospital district without gore.",
    "Samashki village street after a federal cordon.",
    "Budyonnovsk route planning without hostage spectacle.",
    "Ceasefire negotiation room with maps and intermediaries.",
    "Bamut bunker mouth and wooded slope.",
    "Bamut hardened shelters and village defenses.",
    "Southern mountain logistics through ravines and hidden paths.",
    "Foreign volunteers arriving among local Chechen fighters.",
    "Al Khattab portrait revised for broad, flat-nosed Afro-Arab likeness.",
    "Al Khattab injury context with covered right stump.",
    "Rabbit anecdote: Abdulkareem Khadr's rabbit named Khattab.",
    "Al Khattab entering Chechnya under journalist-cover context.",
    "Al Khattab with camera and battlefield media equipment.",
    "Foreign funding network represented without named portrait spectacle.",
    "Khattab and Basayev in field-command context.",
    "Shatoy/Yaryshmardy mountain road bend after ambush.",
    "Chechen mosque courtyard and local faith context.",
    "Jihad as local defense: funeral, elders, and village edge.",
    "Akhmad Kadyrov as mufti in community mediation.",
    "Organized-crime arms channel: bribes, weapons, money, and transport.",
    "Oil theft and weapons leakage at a rough depot.",
    "Teip and village loyalty in a courtyard meeting.",
    "Dudayev profile in a damaged presidential office.",
    "Maskhadov staff map in a Grozny cellar.",
    "Basayev field command after a long road movement.",
    "Yandarbiyev political council after Dudayev's death.",
    "Gelayev mountain column moving through snow and rock.",
    "Raduyev Pervomayskoye planning without hostage spectacle.",
    "Akhmad Kadyrov in first-war religious-political context.",
    "Noukhayev underworld-politics table with ledgers and pipeline sketches.",
    "Yeltsin-era Kremlin Chechnya map table.",
    "Grachev federal command briefing.",
    "Lebed Khasavyurt negotiation table.",
    "MVD cordon at a village edge.",
    "Federal firepower aftermath without active bombardment.",
    "Gudermes winter checkpoint raid aftermath.",
    "Pervomayskoye frozen-steppe breakout landscape.",
    "August 1996 Grozny infiltration route.",
]

IMAGE_BY_SOURCE_PAGE = {
    page: (PNG / filename, caption)
    for page, filename, caption in zip(IMAGE_SOURCE_PAGES, IMAGE_FILES, IMAGE_CAPTIONS)
}


@dataclass(frozen=True)
class Section:
    key: str
    title: str
    short: str
    source_first: int
    source_last: int
    summary: str


SECTIONS = [
    Section("origins", "Origins And Road To War", "Origins", 2, 10, "Historical roots, Soviet memory, the Ichkerian claim, organized crime, arms ecology, and Moscow's decision for war."),
    Section("opening", "Opening Operations", "Opening", 11, 24, "Dolinskoye, Grozny, Shali, Samashki, Budyonnovsk, early negotiations, and Bamut."),
    Section("khattab", "Foreign Volunteers And Al Khattab", "Al Khattab", 25, 34, "Foreign volunteers, Khattab's biography, injury, media, money, Basayev, bin Laden links, and myth control."),
    Section("faith", "Faith And Religious Politics", "Faith", 35, 41, "Local Islam, Sufi practice, jihad as defense, Salafi influence, Kadyrov, and Russian framing."),
    Section("crime", "War Economy And Society", "War Economy", 42, 48, "Organized crime, money, oil, kidnapping, leakage, teips, local loyalties, and warlord authority."),
    Section("leaders", "Leaders And Command", "Leaders", 49, 60, "Chechen, pro-Moscow Chechen, foreign, and Russian political-military figures."),
    Section("federal", "Federal Forces", "Federal Forces", 61, 68, "Russian army formations, Interior Ministry forces, intelligence, logistics, firepower, refugees, and human-rights sources."),
    Section("weapons", "Weapons And Material Culture", "Weapons", 69, 82, "Small arms, excluded heavy weapons, edge machine guns, vehicles, figure style, and material culture."),
    Section("terrain", "Terrain And Local Armed Groups", "Terrain", 83, 91, "Urban, village, mountain, checkpoint, local-faction, and ethics context."),
    Section("cases", "Historical Case Studies", "Case Studies", 92, 101, "Scenario-derived historical cases from Dolinskoye to August 1996 Grozny."),
    Section("appendices", "Appendices And Source Notes", "Appendices", 102, 120, "Khasavyurt, interwar consequences, source cautions, timelines, tables, image index, and revision notes."),
]


SECTION_BY_SOURCE = {
    page: section
    for section in SECTIONS
    for page in range(section.source_first, section.source_last + 1)
}

SUBHEAD_LABELS = {
    "Historical frame",
    "Chechen-side history",
    "Russian-side history",
    "Material and social history",
    "Ethical frame",
    "Cross-reference",
    "Physical setting",
}


def clean(text: str) -> str:
    return (
        text.replace("\u2013", "-")
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


def parse_source_pages() -> list[dict]:
    pages: list[dict] = []
    for idx, raw in enumerate(BOOK.read_text(encoding="utf-8").split("\f"), start=1):
        text = clean(raw.strip())
        if not text:
            continue
        lines = text.splitlines()
        title = re.sub(r"^Page\s+\d+:\s*", "", lines[0].strip())
        body = "\n".join(lines[1:]).strip()
        body = re.sub(r"\nIllustration slot \d+:[^\n]+", "", body)
        pages.append({"source_page": idx, "title": title, "body": body})
    if len(pages) != TARGET_PAGES:
        raise SystemExit(f"Expected {TARGET_PAGES} source pages, got {len(pages)}")
    return pages


def split_paragraphs(text: str) -> list[str]:
    return [" ".join(p.split()) for p in re.split(r"\n\s*\n", text) if p.strip()]


def split_label(para: str) -> tuple[str | None, str]:
    match = re.match(r"^([A-Za-z][A-Za-z -]{2,42})\. (.+)", para)
    if not match:
        return None, para
    label = match.group(1).strip()
    if label in SUBHEAD_LABELS:
        return label, match.group(2).strip()
    return None, para


def fit_text(c: canvas.Canvas, text: str, font: str, size: float, x: float, y: float, max_w: float) -> None:
    c.setFont(font, size)
    if pdfmetrics.stringWidth(text, font, size) <= max_w:
        c.drawString(x, y, text)
        return
    cut = text
    while cut and pdfmetrics.stringWidth(cut.rstrip() + "...", font, size) > max_w:
        cut = cut[:-1]
    c.drawString(x, y, cut.rstrip() + "...")


class SectionedReference:
    def __init__(
        self,
        draw: bool,
        subsection_pages: dict[int, int] | None = None,
        section_pages: dict[str, int] | None = None,
        total_pages: int | None = None,
    ):
        self.draw = draw
        self.c = canvas.Canvas(str(OUT), pagesize=letter) if draw else None
        self.page_no = 0
        self.total_pages = total_pages or TARGET_PAGES
        self.section_pages: dict[str, int] = section_pages or {}
        self.subsection_pages: dict[int, int] = subsection_pages or {}
        self.col = 0
        self.y = BODY_TOP
        self.column_top = BODY_TOP
        self.current_section: Section | None = None
        self.output_subsection_pages: dict[int, int] = {}

    def save(self) -> None:
        if self.c:
            self.c.save()

    def show_page(self) -> None:
        if self.c:
            self.draw_footer()
            self.c.showPage()

    def draw_footer(self) -> None:
        assert self.c is not None
        self.c.setStrokeColor(colors.HexColor("#D8D3C8"))
        self.c.setLineWidth(0.45)
        self.c.line(MARGIN_X, FOOTER_Y + 14, PAGE_W - MARGIN_X, FOOTER_Y + 14)
        self.c.setFont(SMALL_FONT, MIN_FONT)
        self.c.setFillColor(MUTED)
        self.c.drawString(MARGIN_X, FOOTER_Y, "Field of Chaos: Chechnya Historical Reference")
        self.c.drawRightString(PAGE_W - MARGIN_X, FOOTER_Y, f"{self.page_no} / {self.total_pages}")
        self.c.setFillColor(TEXT)

    def new_running_page(self, section: Section) -> None:
        if self.page_no:
            self.show_page()
        self.page_no += 1
        self.current_section = section
        self.col = 0
        self.y = BODY_TOP
        self.column_top = BODY_TOP
        if not self.draw:
            return
        c = self.c
        assert c is not None
        c.setFillColor(colors.white)
        c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        c.setFillColor(SECTION_FILL)
        c.rect(0, PAGE_H - TOP_BAND_H, PAGE_W, TOP_BAND_H, fill=1, stroke=0)
        c.setFont(SMALL_BOLD, MIN_FONT)
        c.setFillColor(MUTED)
        c.drawString(MARGIN_X, PAGE_H - 19, section.title.upper())
        c.drawRightString(PAGE_W - MARGIN_X, PAGE_H - 19, "BOOK 2")

    def start_section_page(self, section: Section) -> None:
        if self.page_no:
            self.show_page()
        self.page_no += 1
        self.section_pages[section.key] = self.page_no
        self.current_section = section
        self.col = 0
        self.y = SECTION_BODY_TOP
        self.column_top = SECTION_BODY_TOP
        if not self.draw:
            return
        c = self.c
        assert c is not None
        c.setFillColor(colors.white)
        c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        c.setFillColor(SECTION_FILL)
        c.rect(0, PAGE_H - TOP_BAND_H, PAGE_W, TOP_BAND_H, fill=1, stroke=0)
        c.setFont(SMALL_BOLD, MIN_FONT)
        c.setFillColor(MUTED)
        c.drawString(MARGIN_X, PAGE_H - 19, section.title.upper())
        c.drawRightString(PAGE_W - MARGIN_X, PAGE_H - 19, "BOOK 2")
        c.setFillColor(TEXT)
        c.setFont(TITLE_FONT, 18)
        fit_text(c, section.title, TITLE_FONT, 18, MARGIN_X, PAGE_H - 61, PAGE_W - 2 * MARGIN_X)
        c.setStrokeColor(RULE)
        c.setLineWidth(0.8)
        c.line(MARGIN_X, PAGE_H - 74, PAGE_W - MARGIN_X, PAGE_H - 74)
        c.setFont("Times-Italic", MIN_FONT)
        c.setFillColor(colors.HexColor("#3E3933"))
        yy = PAGE_H - 91
        for line in simpleSplit(section.summary, "Times-Italic", MIN_FONT, PAGE_W - 2 * MARGIN_X):
            c.drawString(MARGIN_X, yy, line)
            yy -= 12.2
            if yy < PAGE_H - 113:
                break
        c.setStrokeColor(colors.HexColor("#D8D1C5"))
        c.setLineWidth(0.45)
        c.line(MARGIN_X, PAGE_H - 122, PAGE_W - MARGIN_X, PAGE_H - 122)
        c.setFillColor(TEXT)

    def draw_cover(self) -> None:
        self.page_no += 1
        if not self.draw:
            return
        c = self.c
        assert c is not None
        c.setTitle("Field of Chaos: Chechnya Historical Reference")
        c.setFillColor(colors.HexColor("#ECE8DE"))
        c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        cover_path, _ = IMAGE_BY_SOURCE_PAGE[1]
        draw_image(c, cover_path, 34, 214, PAGE_W - 68, 505)
        c.setStrokeColor(colors.HexColor("#4F4840"))
        c.setLineWidth(1.2)
        c.rect(34, 214, PAGE_W - 68, 505, fill=0, stroke=1)
        c.setFillColor(colors.HexColor("#FAF8F2"))
        c.setStrokeColor(colors.HexColor("#4F4840"))
        c.setLineWidth(1.0)
        c.rect(46, 70, PAGE_W - 92, 124, fill=1, stroke=1)
        c.setFillColor(TEXT)
        c.setFont(TITLE_FONT, 28)
        c.drawCentredString(PAGE_W / 2, 155, "Field of Chaos: Chechnya")
        c.setFont(SMALL_BOLD, 13)
        c.setFillColor(colors.HexColor("#4D463E"))
        c.drawCentredString(PAGE_W / 2, 128, "Historical Reference")
        c.setFont(SMALL_FONT, MIN_FONT)
        c.drawCentredString(PAGE_W / 2, 105, "First Chechen War, 1994-1996")
        c.setFont(SMALL_BOLD, MIN_FONT)
        c.drawCentredString(PAGE_W / 2, 86, "BOOK 2")

    def draw_index(self) -> None:
        if self.page_no:
            self.show_page()
        self.page_no += 1
        if not self.draw:
            return
        c = self.c
        assert c is not None
        c.setFillColor(colors.white)
        c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        c.setFillColor(SECTION_FILL)
        c.rect(0, PAGE_H - TOP_BAND_H, PAGE_W, TOP_BAND_H, fill=1, stroke=0)
        c.setFillColor(TEXT)
        c.setFont(TITLE_FONT, 20)
        c.drawString(MARGIN_X, PAGE_H - 62, "Index")
        c.setStrokeColor(RULE)
        c.line(MARGIN_X, PAGE_H - 75, PAGE_W - MARGIN_X, PAGE_H - 75)

        c.setFont(SMALL_FONT, MIN_FONT)
        c.setFillColor(MUTED)
        c.drawRightString(PAGE_W - MARGIN_X, PAGE_H - 62, "Book 2: Historical Reference")

        cols = 3
        gap = 20
        col_w = (PAGE_W - 2 * MARGIN_X - gap * (cols - 1)) / cols
        start_y = PAGE_H - 98
        bottom = 58
        col = 0
        y = start_y

        def advance(line_h: float) -> None:
            nonlocal col, y
            if y - line_h >= bottom:
                return
            col += 1
            y = start_y

        def entry(title: str, page: int, font: str, size: float, indent: float, line_h: float, color) -> None:
            nonlocal y
            advance(line_h)
            x = MARGIN_X + col * (col_w + gap) + indent
            w = col_w - indent
            page_text = str(page) if page else ""
            c.setFont(font, size)
            c.setFillColor(color)
            if page_text:
                c.drawRightString(x + w, y, page_text)
            title_w = w - pdfmetrics.stringWidth(page_text, font, size) - 9
            fit_text(c, title, font, size, x, y, title_w)
            y -= line_h

        for section in SECTIONS:
            advance(27)
            page = self.section_pages.get(section.key, 0)
            entry(section.title, page, SMALL_BOLD, MIN_FONT, 0, 12.2, colors.HexColor("#302B26"))
            for item in SOURCE_PAGES:
                source_page = item["source_page"]
                if not (section.source_first <= source_page <= section.source_last):
                    continue
                page = self.subsection_pages.get(source_page, 0)
                entry(item["title"], page, SMALL_FONT, MIN_FONT, 10, 11.7, colors.HexColor("#3E3933"))
            y -= 3.0

    def ensure_space(self, height: float) -> None:
        if self.y - height >= BOTTOM_Y:
            return
        if self.col == 0:
            self.col = 1
            self.y = self.column_top
            return
        assert self.current_section is not None
        self.new_running_page(self.current_section)

    def col_x(self) -> float:
        return MARGIN_X + self.col * (COL_W + GUTTER)

    def draw_subsection_heading(self, title: str, source_page: int) -> None:
        h = 27
        self.ensure_space(h + SUBSECTION_AFTER_GAP + 1)
        self.output_subsection_pages[source_page] = self.page_no
        if self.draw:
            assert self.c is not None
            x = self.col_x()
            c = self.c
            c.setFillColor(PALE)
            c.rect(x, self.y - h + 3, COL_W, h, fill=1, stroke=0)
            c.setStrokeColor(colors.HexColor("#D0C8BB"))
            c.setLineWidth(0.45)
            c.line(x, self.y + 3, x + COL_W, self.y + 3)
            c.line(x, self.y - h + 3, x + COL_W, self.y - h + 3)
            c.setFont(SMALL_BOLD, MIN_FONT)
            c.setFillColor(colors.HexColor("#3E3933"))
            fit_text(c, title, SMALL_BOLD, MIN_FONT, x + 6, self.y - 11, COL_W - 38)
            c.setFont(SMALL_FONT, MIN_FONT)
            c.setFillColor(MUTED)
            c.drawRightString(x + COL_W - 5, self.y - 11, f"S{source_page:03d}")
            c.setFillColor(TEXT)
        self.y -= h + SUBSECTION_AFTER_GAP

    def draw_figure(self, path: Path, caption: str) -> None:
        image_h = 230
        cap_lines = simpleSplit(caption, CAPTION_FONT, MIN_FONT, COL_W - 10)
        cap_h = min(2, len(cap_lines)) * 12.0 + 8
        total_h = image_h + cap_h + 13
        self.ensure_space(total_h)
        if self.draw:
            assert self.c is not None
            x = self.col_x()
            c = self.c
            image_y = self.y - image_h
            c.setFillColor(PALE)
            c.setStrokeColor(colors.HexColor("#C9C1B5"))
            c.rect(x, image_y, COL_W, image_h, fill=1, stroke=1)
            draw_image_cover(c, path, x + 5, image_y + 5, COL_W - 10, image_h - 10)
            box_y = image_y - cap_h
            c.setFillColor(colors.HexColor("#EEEAE1"))
            c.rect(x, box_y, COL_W, cap_h, fill=1, stroke=0)
            c.setFont("Helvetica-Oblique", MIN_FONT)
            c.setFillColor(colors.HexColor("#464038"))
            yy = box_y + cap_h - 10.5
            for line in cap_lines[:2]:
                c.drawCentredString(x + COL_W / 2, yy, line)
                yy -= 12.0
        self.y -= total_h

    def draw_paragraph(self, para: str, lead: bool = False) -> None:
        label, body = split_label(para)
        if label:
            self.ensure_space(INLINE_LABEL_AFTER_GAP + BODY_LEADING)
            if self.draw:
                assert self.c is not None
                self.c.setFont(SMALL_BOLD, MIN_FONT)
                self.c.setFillColor(MUTED)
                self.c.drawString(self.col_x(), self.y, label.upper())
                self.c.setFillColor(TEXT)
            self.y -= INLINE_LABEL_AFTER_GAP
        font = "Times-Italic" if lead else BODY_FONT
        size = BODY_SIZE + 0.15 if lead else BODY_SIZE
        leading = BODY_LEADING + 0.1 if lead else BODY_LEADING
        for line in simpleSplit(body, font, size, COL_W):
            self.ensure_space(leading)
            if self.draw:
                assert self.c is not None
                self.c.setFont(font, size)
                self.c.setFillColor(TEXT)
                self.c.drawString(self.col_x(), self.y, line)
            self.y -= leading
        self.y -= 3.6


def build_book(
    draw: bool,
    known_subsections: dict[int, int] | None = None,
    known_sections: dict[str, int] | None = None,
    total_pages: int | None = None,
) -> SectionedReference:
    book = SectionedReference(
        draw=draw,
        subsection_pages=known_subsections,
        section_pages=known_sections,
        total_pages=total_pages,
    )
    book.draw_cover()
    book.draw_index()

    pages_by_source = {p["source_page"]: p for p in SOURCE_PAGES}
    for section in SECTIONS:
        book.start_section_page(section)
        for source_page in range(section.source_first, section.source_last + 1):
            item = pages_by_source[source_page]
            book.ensure_space(245 if source_page in IMAGE_BY_SOURCE_PAGE else 108)
            book.draw_subsection_heading(item["title"], source_page)
            if source_page in IMAGE_BY_SOURCE_PAGE:
                path, caption = IMAGE_BY_SOURCE_PAGE[source_page]
                book.draw_figure(path, caption)
            paragraphs = split_paragraphs(item["body"])
            for idx, para in enumerate(paragraphs):
                book.draw_paragraph(para, lead=(idx == 0))

    if book.page_no:
        book.show_page()
    return book


def main() -> None:
    missing = [str(path) for path, _ in IMAGE_BY_SOURCE_PAGE.values() if not path.exists()]
    if missing:
        raise SystemExit("Missing images:\n" + "\n".join(missing))

    dry = build_book(draw=False)
    total = dry.page_no
    final = build_book(
        draw=True,
        known_subsections=dry.output_subsection_pages,
        known_sections=dry.section_pages,
        total_pages=total,
    )
    final.save()

    print(f"Wrote {OUT}")
    print(f"Pages: {total}")
    print(f"Target was {TARGET_PAGES}; sectioned flow uses {total} pages")
    print(f"Sections: {len(SECTIONS)}; subsection index entries: {len(dry.output_subsection_pages)}")
    print(f"Active images: {len(IMAGE_FILES)}")


SOURCE_PAGES = parse_source_pages()


if __name__ == "__main__":
    main()
